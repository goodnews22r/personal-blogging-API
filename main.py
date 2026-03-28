from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import posts, comments, tags, media, author, analytics, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Personal Blogging Platform API",
    version="2.1.0",
    description="Publish, manage, and distribute your writing — programmatically.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/v2/auth",      tags=["Auth"])
app.include_router(posts.router,     prefix="/v2/posts",     tags=["Posts"])
app.include_router(comments.router,  prefix="/v2/comments",  tags=["Comments"])
app.include_router(tags.router,      prefix="/v2/tags",      tags=["Tags"])
app.include_router(media.router,     prefix="/v2/media",     tags=["Media"])
app.include_router(author.router,    prefix="/v2/author",    tags=["Author"])
app.include_router(analytics.router, prefix="/v2/analytics", tags=["Analytics"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "api": "Personal Blogging Platform", "version": "2.1.0"}
