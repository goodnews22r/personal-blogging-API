from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    expires_in: int
    token_type: str = "Bearer"

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


# ── Tag ───────────────────────────────────────────────
class TagCreate(BaseModel):
    label: str
    slug: Optional[str] = None

class TagOut(BaseModel):
    id: str
    slug: str
    label: str
    post_count: int = 0
    class Config: from_attributes = True


# ── Post ──────────────────────────────────────────────
class PostCreate(BaseModel):
    title: str
    content: str
    slug: Optional[str] = None
    status: Optional[str] = "draft"
    tags: Optional[List[str]] = []
    feature_image: Optional[str] = ""
    published_at: Optional[datetime] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    feature_image: Optional[str] = None
    published_at: Optional[datetime] = None

class AuthorMini(BaseModel):
    id: str
    name: str
    class Config: from_attributes = True

class PostOut(BaseModel):
    id: str
    title: str
    slug: str
    status: str
    feature_image: str
    reading_time: int
    views: int
    author: Optional[AuthorMini]
    tags: List[TagOut] = []
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    url: Optional[str] = None
    class Config: from_attributes = True

class PostList(BaseModel):
    posts: List[PostOut]
    meta: dict


# ── Comment ───────────────────────────────────────────
class CommentCreate(BaseModel):
    author: str
    email: Optional[str] = ""
    body: str

class CommentModerate(BaseModel):
    status: str  # approved | spam | deleted

class CommentOut(BaseModel):
    id: str
    author: str
    body: str
    status: str
    created_at: datetime
    class Config: from_attributes = True


# ── Media ─────────────────────────────────────────────
class MediaOut(BaseModel):
    id: str
    url: str
    alt: str
    caption: str
    width: int
    height: int
    size_bytes: int
    class Config: from_attributes = True


# ── Author ────────────────────────────────────────────
class AuthorOut(BaseModel):
    id: str
    name: str
    email: str
    bio: str
    avatar_url: str
    total_posts: int = 0
    total_views: int = 0
    class Config: from_attributes = True

class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


# ── Analytics ─────────────────────────────────────────
class ReferrerOut(BaseModel):
    source: str
    count: int

class AnalyticsOut(BaseModel):
    views: int
    reads: int
    read_rate: float
    avg_time_seconds: float
    referrers: List[ReferrerOut]
