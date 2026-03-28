from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

from app.database import get_db
from app import models
from app.auth import get_current_author

router = APIRouter()

@router.get("/posts/{post_id}")
def post_analytics(
    post_id: str,
    period: str = Query("30d"),
    author: models.Author = Depends(get_current_author),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != author.id:
        raise HTTPException(status_code=403, detail="Not your post")

    days_map = {"7d": 7, "30d": 30, "90d": 90}
    since = None
    if period in days_map:
        since = datetime.utcnow() - timedelta(days=days_map[period])

    q = db.query(models.PostAnalytics).filter(models.PostAnalytics.post_id == post_id)
    if since:
        q = q.filter(models.PostAnalytics.date >= since)
    rows = q.all()

    total_views = sum(r.views for r in rows) or post.views
    total_reads = sum(r.reads for r in rows)
    avg_time    = (sum(r.avg_time_seconds for r in rows) / len(rows)) if rows else 0
    read_rate   = round(total_reads / total_views, 2) if total_views else 0

    referrer_counts = defaultdict(int)
    for r in rows:
        referrer_counts[r.referrer] += r.views
    referrers = [{"source": k, "count": v} for k, v in sorted(referrer_counts.items(), key=lambda x: -x[1])]

    return {
        "views": total_views,
        "reads": total_reads,
        "read_rate": read_rate,
        "avg_time_seconds": round(avg_time, 1),
        "referrers": referrers or [{"source": "direct", "count": total_views}],
    }
