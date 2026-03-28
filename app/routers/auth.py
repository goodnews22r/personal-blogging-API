from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_token, TOKEN_EXPIRE_HOURS

router = APIRouter()

@router.post("/token", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.email == body.email).first()
    if not author or not verify_password(body.password, author.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "token": create_token(author.id),
        "expires_in": TOKEN_EXPIRE_HOURS * 3600,
        "token_type": "Bearer",
    }

@router.post("/register", status_code=201)
def register(body: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.Author).filter(models.Author.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    author = models.Author(
        name=body.name,
        email=body.email,
        password=hash_password(body.password),
    )
    db.add(author)
    db.commit()
    db.refresh(author)
    return {"id": author.id, "name": author.name, "email": author.email}
