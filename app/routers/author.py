from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.auth import get_current_author

# ── Author ────────────────────────────────────────────
router = APIRouter()

@router.get("/me")
def get_me(author: models.Author = Depends(get_current_author), db: Session = Depends(get_db)):
    total_views = db.query(func.sum(models.Post.views)).filter(
        models.Post.author_id == author.id
    ).scalar() or 0
    return {
        "id": author.id,
        "name": author.name,
        "email": author.email,
        "bio": author.bio,
        "avatar_url": author.avatar_url,
        "total_posts": len(author.posts),
        "total_views": total_views,
    }

@router.put("/me")
def update_me(
    body: schemas.AuthorUpdate,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    if body.name is not None: author.name = body.name
    if body.bio is not None: author.bio = body.bio
    if body.avatar_url is not None: author.avatar_url = body.avatar_url
    db.commit()
    db.refresh(author)
    return {"id": author.id, "name": author.name, "bio": author.bio}
