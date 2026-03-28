# Personal Blogging Platform API

A production-ready REST API built with FastAPI + PostgreSQL. Deploy to Railway in minutes.

---

## Project Structure

```
blog-api/
├── main.py                  # App entry point
├── requirements.txt
├── Dockerfile
├── railway.toml
├── .env.example
└── app/
    ├── database.py          # DB connection
    ├── models.py            # SQLAlchemy models
    ├── schemas.py           # Pydantic schemas
    ├── auth.py              # JWT utilities
    └── routers/
        ├── auth.py          # POST /auth/token, /auth/register
        ├── posts.py         # Full CRUD + comments
        ├── comments.py      # PATCH /comments/{id}
        ├── tags.py          # GET/POST /tags
        ├── media.py         # POST /media/upload
        ├── author.py        # GET/PUT /author/me
        └── analytics.py     # GET /analytics/posts/{id}
```

---

## Local Development

### 1. Clone and set up

```bash
git clone <your-repo>
cd blog-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — for local dev, SQLite works out of the box (no DATABASE_URL needed)
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

API is live at: http://localhost:8000
Interactive docs at: http://localhost:8000/docs
ReDoc at: http://localhost:8000/redoc

---

## Deploy to Railway

Railway is the recommended host — it supports persistent Python servers and provides a managed PostgreSQL add-on for free.

### Step 1 — Push your code to GitHub

```bash
git init
git add .
git commit -m "initial commit"
gh repo create blog-api --public --push   # or push manually
```

### Step 2 — Create a Railway project

1. Go to https://railway.app and sign up / log in
2. Click **New Project → Deploy from GitHub repo**
3. Select your `blog-api` repository
4. Railway auto-detects the Dockerfile and starts building

### Step 3 — Add PostgreSQL

1. In your Railway project, click **+ New → Database → PostgreSQL**
2. Railway creates a database and injects `DATABASE_URL` automatically into your service

### Step 4 — Set environment variables

In Railway → your service → **Variables**, add:

| Variable    | Value                          |
|-------------|-------------------------------|
| SECRET_KEY  | (generate a long random string) |
| CDN_BASE    | https://your-app.up.railway.app/uploads |

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5 — Deploy

Railway deploys automatically on every push. Watch the build logs in the Railway dashboard.

Your API will be live at:
```
https://<your-app-name>.up.railway.app
```

---

## API Quick Reference

All protected endpoints require:
```
Authorization: Bearer <token>
```

### Auth

```bash
# Register
curl -X POST https://your-app.up.railway.app/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Alex","email":"alex@example.com","password":"secret123"}'

# Login — get token
curl -X POST https://your-app.up.railway.app/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"secret123"}'
```

### Posts

```bash
# List published posts
curl https://your-app.up.railway.app/v2/posts?status=published

# Create a post
curl -X POST https://your-app.up.railway.app/v2/posts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello World","content":"My first post.","status":"published","tags":["tech"]}'

# Get single post
curl https://your-app.up.railway.app/v2/posts/hello-world

# Update post
curl -X PUT https://your-app.up.railway.app/v2/posts/post_abc123 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status":"published"}'

# Delete post
curl -X DELETE https://your-app.up.railway.app/v2/posts/post_abc123 \
  -H "Authorization: Bearer <token>"
```

### Tags

```bash
# List tags
curl https://your-app.up.railway.app/v2/tags

# Create tag
curl -X POST https://your-app.up.railway.app/v2/tags \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"label":"JavaScript"}'
```

### Media Upload

```bash
curl -X POST https://your-app.up.railway.app/v2/media/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/image.jpg" \
  -F "alt=Hero image" \
  -F "caption=My blog hero"
```

### Comments

```bash
# Add comment (public)
curl -X POST https://your-app.up.railway.app/v2/posts/post_abc123/comments \
  -H "Content-Type: application/json" \
  -d '{"author":"Jane","body":"Great post!"}'

# List comments (with filter)
curl https://your-app.up.railway.app/v2/posts/post_abc123/comments?status=approved

# Moderate comment
curl -X PATCH https://your-app.up.railway.app/v2/comments/cmt_xyz \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status":"approved"}'
```

### Author & Analytics

```bash
# Get your profile
curl https://your-app.up.railway.app/v2/author/me \
  -H "Authorization: Bearer <token>"

# Post analytics (last 30 days)
curl https://your-app.up.railway.app/v2/analytics/posts/post_abc123?period=30d \
  -H "Authorization: Bearer <token>"
```

---

## Python Client Example

```python
import requests

BASE = "https://your-app.up.railway.app/v2"

# Login
r = requests.post(f"{BASE}/auth/token", json={
    "email": "alex@example.com",
    "password": "secret123"
})
token = r.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Create post
post = requests.post(f"{BASE}/posts", headers=headers, json={
    "title": "My Post",
    "content": "# Hello\n\nThis is my post.",
    "status": "published",
    "tags": ["tech", "writing"]
}).json()

print(post["url"])  # https://yourblog.io/my-post
```

---

## JavaScript Fetch Example

```javascript
const BASE = "https://your-app.up.railway.app/v2";

async function createPost(token, data) {
  const res = await fetch(`${BASE}/posts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  return res.json();
}

async function uploadImage(token, file) {
  const form = new FormData();
  form.append("file", file);
  form.append("alt", "Blog image");
  const res = await fetch(`${BASE}/media/upload`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${token}` },
    body: form,
  });
  return res.json();
}
```

---

## Environment Variables Reference

| Variable      | Required | Description                              |
|---------------|----------|------------------------------------------|
| DATABASE_URL  | Yes (prod)| PostgreSQL connection string            |
| SECRET_KEY    | Yes      | JWT signing secret, min 32 chars         |
| UPLOAD_DIR    | No       | Local upload path, default `./uploads`   |
| CDN_BASE      | No       | Public base URL for uploaded files       |

---

## Status Codes

| Code | Meaning           |
|------|-------------------|
| 200  | Success           |
| 201  | Created           |
| 401  | Unauthorized      |
| 403  | Forbidden         |
| 404  | Not Found         |
| 409  | Conflict          |
| 422  | Validation Error  |

---

## Notes

- The SQLite fallback (`blog.db`) is used automatically when `DATABASE_URL` is not set — perfect for local dev.
- Tables are auto-created on startup via `Base.metadata.create_all`.
- Interactive API docs are always available at `/docs` (Swagger UI).
- For production file storage, replace the local upload handler with S3/Cloudflare R2.
