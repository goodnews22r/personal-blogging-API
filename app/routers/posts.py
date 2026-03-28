import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app import models, schemas
from app.auth import get_current_author

router = APIRouter()

BLOG_BASE = "https://blog.io"

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)

def calc_reading_time(content: str) -> int:
    words = len(content.split())
    return max(1, round(words / 200))

def resolve_tags(db, tag_slugs):
    tags = []
    for slug in tag_slugs:
        tag = db.query(models.Tag).filter(models.Tag.slug == slug).first()
        if tag:
            tags.append(tag)
    return tags

def post_to_out(post: models.Post) -> dict:
    d = schemas.PostOut.from_orm(post).dict()
    d["url"] = f"{BLOG_BASE}/{post.slug}"
    return d


@router.get("", response_model=schemas.PostList)
def list_posts(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = Query("published_at"),
    db: Session = Depends(get_db),
):
    q = db.query(models.Post)
    if status:
        q = q.filter(models.Post.status == status)
    if tag:
        q = q.join(models.Post.tags).filter(models.Tag.slug == tag)

    sort_col = {
        "published_at": models.Post.published_at,
        "updated_at": models.Post.updated_at,
        "views": models.Post.views,
    }.get(sort, models.Post.published_at)

    total = q.count()
    posts = q.order_by(sort_col.desc().nullslast()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "posts": [post_to_out(p) for p in posts],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("", status_code=201)
def create_post(
    body: schemas.PostCreate,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    slug = body.slug or slugify(body.title)
    if db.query(models.Post).filter(models.Post.slug == slug).first():
        slug = slug + "-" + author.id[-4:]

    post = models.Post(
        title=body.title,
        slug=slug,
        content=body.content,
        status=body.status,
        feature_image=body.feature_image or "",
        reading_time=calc_reading_time(body.content),
        published_at=body.published_at,
        author_id=author.id,
        tags=resolve_tags(db, body.tags or []),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post_to_out(post)


@router.get("/{id_or_slug}")
def get_post(id_or_slug: str, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(
        or_(models.Post.id == id_or_slug, models.Post.slug == id_or_slug)
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.views += 1
    db.commit()
    return post_to_out(post)


@router.put("/{post_id}")
def update_post(
    post_id: str,
    body: schemas.PostUpdate,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != author.id:
        raise HTTPException(status_code=403, detail="Not your post")

    if body.title is not None:
        post.title = body.title
    if body.content is not None:
        post.content = body.content
        post.reading_time = calc_reading_time(body.content)
    if body.slug is not None:
        post.slug = body.slug
    if body.status is not None:
        post.status = body.status
    if body.feature_image is not None:
        post.feature_image = body.feature_image
    if body.published_at is not None:
        post.published_at = body.published_at
    if body.tags is not None:
        post.tags = resolve_tags(db, body.tags)

    db.commit()
    db.refresh(post)
    return post_to_out(post)


@router.delete("/{post_id}")
def delete_post(
    post_id: str,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != author.id:
        raise HTTPException(status_code=403, detail="Not your post")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}


@router.get("/{post_id}/comments")
def list_comments(
    post_id: str,
    status: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    q = db.query(models.Comment).filter(models.Comment.post_id == post_id)
    if status:
        q = q.filter(models.Comment.status == status)
    comments = q.offset((page - 1) * 20).limit(20).all()
    return {"comments": [schemas.CommentOut.from_orm(c) for c in comments]}


@router.post("/{post_id}/comments", status_code=201)
def add_comment(post_id: str, body: schemas.CommentCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = models.Comment(post_id=post_id, **body.dict())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return schemas.CommentOut.from_orm(comment)
