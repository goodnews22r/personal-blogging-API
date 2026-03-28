from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
import os, uuid, shutil
from typing import Optional

from app.database import get_db
from app import models, schemas
from app.auth import get_current_author

# ── Comments ──────────────────────────────────────────
router = APIRouter()

@router.patch("/{comment_id}")
def moderate_comment(
    comment_id: str,
    body: schemas.CommentModerate,
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.post.author_id != author.id:
        raise HTTPException(status_code=403, detail="Not your post")
    if body.status not in ("approved", "spam", "deleted"):
        raise HTTPException(status_code=422, detail="Invalid status")
    comment.status = body.status
    db.commit()
    return schemas.CommentOut.from_orm(comment)
