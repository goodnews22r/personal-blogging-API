from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Table, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base

def gen_id():
    return str(uuid.uuid4())[:8]

post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", String, ForeignKey("posts.id")),
    Column("tag_id", String, ForeignKey("tags.id")),
)

class Author(Base):
    __tablename__ = "authors"
    id         = Column(String, primary_key=True, default=lambda: "usr_" + gen_id())
    name       = Column(String, nullable=False)
    email      = Column(String, unique=True, nullable=False, index=True)
    password   = Column(String, nullable=False)
    bio        = Column(Text, default="")
    avatar_url = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    posts      = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id            = Column(String, primary_key=True, default=lambda: "post_" + gen_id())
    title         = Column(String(200), nullable=False)
    slug          = Column(String, unique=True, index=True, nullable=False)
    content       = Column(Text, nullable=False)
    status        = Column(String, default="draft")   # draft | published | scheduled | archived
    feature_image = Column(String, default="")
    reading_time  = Column(Integer, default=1)
    views         = Column(Integer, default=0)
    author_id     = Column(String, ForeignKey("authors.id"))
    author        = relationship("Author", back_populates="posts")
    tags          = relationship("Tag", secondary=post_tags, back_populates="posts")
    comments      = relationship("Comment", back_populates="post", cascade="all, delete")
    analytics     = relationship("PostAnalytics", back_populates="post", cascade="all, delete")
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())
    published_at  = Column(DateTime(timezone=True), nullable=True)

class Tag(Base):
    __tablename__ = "tags"
    id    = Column(String, primary_key=True, default=lambda: "tag_" + gen_id())
    slug  = Column(String, unique=True, index=True, nullable=False)
    label = Column(String, nullable=False)
    posts = relationship("Post", secondary=post_tags, back_populates="tags")

class Comment(Base):
    __tablename__ = "comments"
    id         = Column(String, primary_key=True, default=lambda: "cmt_" + gen_id())
    post_id    = Column(String, ForeignKey("posts.id"))
    post       = relationship("Post", back_populates="comments")
    author     = Column(String, nullable=False)
    email      = Column(String, default="")
    body       = Column(Text, nullable=False)
    status     = Column(String, default="pending")  # pending | approved | spam | deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Media(Base):
    __tablename__ = "media"
    id         = Column(String, primary_key=True, default=lambda: "med_" + gen_id())
    url        = Column(String, nullable=False)
    alt        = Column(String, default="")
    caption    = Column(String, default="")
    width      = Column(Integer, default=0)
    height     = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    author_id  = Column(String, ForeignKey("authors.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PostAnalytics(Base):
    __tablename__ = "post_analytics"
    id               = Column(String, primary_key=True, default=lambda: "anl_" + gen_id())
    post_id          = Column(String, ForeignKey("posts.id"))
    post             = relationship("Post", back_populates="analytics")
    date             = Column(DateTime(timezone=True), server_default=func.now())
    views            = Column(Integer, default=0)
    reads            = Column(Integer, default=0)
    avg_time_seconds = Column(Float, default=0)
    referrer         = Column(String, default="direct")
