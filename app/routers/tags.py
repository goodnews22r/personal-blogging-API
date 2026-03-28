import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_author

router = APIRouter()

def slugify(text: str) -> str:
    return re.sub(r"[\s_-]+", "-", re.sub(r"[^\w\s-]", "", text.lower().strip()))

@router.get("")
def list_tags(db: Session = Depends(get_db)):
    tags = db.query(models.Tag).all()
    return {"tags": [
        {"id": t.id, "slug": t.slug, "label": t.label, "post_count": len(t.posts)}
        for t in tags
    ]}

@router.post("", status_code=201)
def create_tag(
    body: schemas.TagCreate,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    slug = body.slug or slugify(body.label)
    if db.query(models.Tag).filter(models.Tag.slug == slug).first():
        raise HTTPException(status_code=409, detail="Tag slug already exists")
    tag = models.Tag(slug=slug, label=body.label)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return {"id": tag.id, "slug": tag.slug, "label": tag.label}

@router.delete("/{tag_id}")
def delete_tag(
    tag_id: str,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted"}
