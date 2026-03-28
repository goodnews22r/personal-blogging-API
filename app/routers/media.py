import os, uuid, shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_author

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
CDN_BASE   = os.getenv("CDN_BASE", "http://localhost:8000/uploads")
ALLOWED    = {"image/jpeg", "image/png", "image/webp", "image/gif"}

@router.post("/upload", status_code=201, response_model=schemas.MediaOut)
async def upload_media(
    file: UploadFile = File(...),
    alt: str = Form(""),
    caption: str = Form(""),
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=422, detail="Unsupported file type")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    size = os.path.getsize(path)
    url  = f"{CDN_BASE}/{filename}"

    media = models.Media(
        url=url, alt=alt, caption=caption,
        size_bytes=size, author_id=author.id,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media

@router.get("")
def list_media(
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    items = db.query(models.Media).filter(models.Media.author_id == author.id).all()
    return {"media": [schemas.MediaOut.from_orm(m) for m in items]}
