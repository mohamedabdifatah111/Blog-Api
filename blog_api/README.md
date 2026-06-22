# Blog API — Django + DRF

A robust, scalable REST API for a fully-featured blogging platform.
Built with **Django 4.2**, **Django REST Framework**, **SimpleJWT** and **drf-spectacular**.

---

## Architecture Overview

```
blog_api/
├── config/                  # Project-level configuration
│   ├── settings.py          # All settings (apps, DRF, JWT, Spectacular, DB)
│   ├── urls.py              # Root URL conf + Swagger/Redoc docs
│   └── wsgi.py
│
├── core/                    # Shared cross-app utilities
│   ├── pagination.py        # StandardResultsPagination (wrapped envelope)
│   └── permissions.py       # IsAuthorOrReadOnly, IsAdminOrReadOnly
│
├── apps/
│   ├── accounts/            # Custom User model + JWT auth
│   │   ├── models.py        # User (email-based, no username)
│   │   ├── serializers.py   # Register, Profile, ChangePassword, CustomToken
│   │   ├── views.py         # Register, Login, Logout, Profile, ChangePassword
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── blog/                # Posts, Categories, Tags
│   │   ├── models.py        # Category, Tag, Post
│   │   ├── serializers.py   # Full + Minimal + List variants
│   │   ├── views.py         # CategoryViewSet, TagViewSet, PostViewSet
│   │   ├── filters.py       # PostFilter (django-filter)
│   │   ├── urls.py          # DefaultRouter wiring
│   │   └── admin.py
│   │
│   └── comments/            # Nested comment threads
│       ├── models.py        # Comment (self-referencing FK)
│       ├── serializers.py   # CommentSerializer + ReplySerializer
│       ├── views.py         # CommentViewSet (scoped to post slug)
│       ├── urls.py
│       └── admin.py
│
├── requirements.txt
└── manage.py
```

---

## Quick Start

### 1 — Clone & install dependencies

```bash
git clone <repo-url> blog_api
cd blog_api

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2 — Environment variables

Copy and adjust for your environment:

```bash
export SECRET_KEY="your-very-secret-key"
export DEBUG="True"
export ALLOWED_HOSTS="localhost 127.0.0.1"

# Optional — PostgreSQL (defaults to SQLite)
export DB_ENGINE="django.db.backends.postgresql"
export DB_NAME="blog_db"
export DB_USER="postgres"
export DB_PASSWORD="secret"
export DB_HOST="localhost"
export DB_PORT="5432"
```

### 3 — Database migrations & superuser

```bash
python manage.py migrate
python manage.py createsuperuser   # prompts for email + password
```

### 4 — Run development server

```bash
python manage.py runserver
```

---

## API Endpoints

### Authentication — `/api/v1/auth/`

| Method | Endpoint                        | Auth?  | Description                          |
|--------|---------------------------------|--------|--------------------------------------|
| POST   | `/register/`                    | No     | Create a new account                 |
| POST   | `/token/`                       | No     | Obtain access + refresh JWT tokens   |
| POST   | `/token/refresh/`               | No     | Refresh access token                 |
| POST   | `/token/verify/`                | No     | Verify a token is valid              |
| POST   | `/logout/`                      | Yes    | Blacklist refresh token (logout)     |
| GET    | `/profile/`                     | Yes    | Retrieve own profile                 |
| PUT    | `/profile/`                     | Yes    | Update own profile                   |
| PATCH  | `/profile/`                     | Yes    | Partial update own profile           |
| PUT    | `/profile/change-password/`     | Yes    | Change own password                  |

### Blog — `/api/v1/blog/`

#### Categories (admin write, public read)

| Method | Endpoint                    | Description              |
|--------|-----------------------------|--------------------------|
| GET    | `/categories/`              | List all categories      |
| POST   | `/categories/`              | Create category (admin)  |
| GET    | `/categories/<slug>/`       | Retrieve category        |
| PUT    | `/categories/<slug>/`       | Update category (admin)  |
| PATCH  | `/categories/<slug>/`       | Partial update (admin)   |
| DELETE | `/categories/<slug>/`       | Delete category (admin)  |

#### Tags (admin write, public read)

| Method | Endpoint              | Description          |
|--------|-----------------------|----------------------|
| GET    | `/tags/`              | List all tags        |
| POST   | `/tags/`              | Create tag (admin)   |
| GET    | `/tags/<slug>/`       | Retrieve tag         |
| PUT    | `/tags/<slug>/`       | Update tag (admin)   |
| DELETE | `/tags/<slug>/`       | Delete tag (admin)   |

#### Posts

| Method | Endpoint                          | Auth?   | Description                       |
|--------|-----------------------------------|---------|-----------------------------------|
| GET    | `/posts/`                         | No      | List published posts              |
| POST   | `/posts/`                         | Yes     | Create a new post (throttled)     |
| GET    | `/posts/<slug>/`                  | No      | Retrieve a post                   |
| PUT    | `/posts/<slug>/`                  | Author  | Full update                       |
| PATCH  | `/posts/<slug>/`                  | Author  | Partial update                    |
| DELETE | `/posts/<slug>/`                  | Author  | Delete                            |
| POST   | `/posts/<slug>/publish/`          | Author  | Publish a draft post              |
| POST   | `/posts/<slug>/unpublish/`        | Author  | Revert published post to draft    |

#### Post Query Parameters

| Param           | Example                       | Description                        |
|-----------------|-------------------------------|------------------------------------|
| `search`        | `?search=django`              | Full-text search (title, content)  |
| `status`        | `?status=published`           | Filter by status                   |
| `category`      | `?category=3`                 | Filter by category id              |
| `category_slug` | `?category_slug=technology`   | Filter by category slug            |
| `tags`          | `?tags=5`                     | Filter by tag id                   |
| `author`        | `?author=1`                   | Filter by author id                |
| `created_after` | `?created_after=2024-01-01`   | Date range filter                  |
| `created_before`| `?created_before=2024-12-31`  | Date range filter                  |
| `ordering`      | `?ordering=-created_at`       | Sort: `created_at`, `updated_at`   |
| `page`          | `?page=2`                     | Pagination page number             |
| `page_size`     | `?page_size=20`               | Items per page (max 100)           |

### Comments — `/api/v1/comments/`

All comment endpoints are scoped under a post:

| Method | Endpoint                                          | Auth?   | Description                     |
|--------|---------------------------------------------------|---------|---------------------------------|
| GET    | `/blog/posts/<slug>/comments/`                    | No      | List top-level comments + replies |
| POST   | `/blog/posts/<slug>/comments/`                    | Yes     | Add a comment                   |
| GET    | `/blog/posts/<slug>/comments/<id>/`               | No      | Retrieve a comment              |
| PUT    | `/blog/posts/<slug>/comments/<id>/`               | Author  | Update comment                  |
| PATCH  | `/blog/posts/<slug>/comments/<id>/`               | Author  | Partial update                  |
| DELETE | `/blog/posts/<slug>/comments/<id>/`               | Author  | Soft-delete (sets body=[deleted])|

To post a reply, include `"parent": <parent_comment_id>` in the request body.

---

## Pagination Response Envelope

All list endpoints return:

```json
{
  "pagination": {
    "count": 42,
    "total_pages": 5,
    "current_page": 1,
    "next": "http://localhost:8000/api/v1/blog/posts/?page=2",
    "previous": null
  },
  "results": [ ... ]
}
```

---

## Throttling

| Scope        | Limit       | Applied to                  |
|--------------|-------------|------------------------------|
| `anon`       | 60/hour     | All unauthenticated requests |
| `user`       | 300/hour    | All authenticated requests   |
| `post_create`| 20/hour     | POST /posts/ only            |

---

## API Documentation

| URL                    | Description               |
|------------------------|---------------------------|
| `/api/schema/`         | Raw OpenAPI 3.0 schema    |
| `/api/docs/swagger/`   | Swagger UI                |
| `/api/docs/redoc/`     | Redoc                     |

---

## JWT Authentication Usage

**1. Obtain tokens:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response:
```json
{
  "access":  "<access_token>",
  "refresh": "<refresh_token>"
}
```

**2. Use access token:**
```bash
curl http://localhost:8000/api/v1/blog/posts/ \
  -H "Authorization: Bearer <access_token>"
```

**3. Refresh expired access token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -d '{"refresh": "<refresh_token>"}'
```

---

## Design Decisions

| Concern                  | Decision                                                              |
|--------------------------|-----------------------------------------------------------------------|
| Auth identifier          | Email (no username field) — cleaner UX, avoids username conflicts     |
| Slug generation          | Auto-generated from title with collision suffix (-1, -2 …)           |
| Post visibility          | Public sees published; logged-in users also see own drafts            |
| Category/Tag write access| Admin/staff only — prevents tag pollution                            |
| Comment nesting          | 1-level deep in the API; DB supports deeper but serializer caps at 2  |
| Comment deletion         | Soft-delete — preserves thread structure, marks as [deleted]         |
| Pagination               | Custom envelope with metadata (`pagination` + `results`)             |
| Serializer variants      | List vs Detail serializers — avoids over-fetching on list endpoints  |
