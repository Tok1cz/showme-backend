# ShowMe Backend

REST API backend for the ShowMe tourist guide application. Built with **FastAPI**, **PostgreSQL/PostGIS**, **Celery**, and **OpenAI**, it serves geospatial points-of-interest (POIs) imported from OpenStreetMap and enriches them with AI-generated text, images, and audio.

---

## Tech Stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| Framework  | FastAPI + Uvicorn                           |
| Database   | PostgreSQL + PostGIS (async via asyncpg)    |
| ORM        | SQLAlchemy + GeoAlchemy2                    |
| Migrations | Alembic                                     |
| Task Queue | Celery + Redis                              |
| AI         | OpenAI API (text, image & audio generation) |
| Auth       | FastAPI-Users (JWT + Google OAuth)          |
| Geospatial | Osmium (OSM data import pipeline)           |

## Project Structure

```
app/
├── main.py                  # FastAPI app entry point
├── celery_app.py            # Celery worker configuration
├── api/routes/
│   ├── poi/                 # POI endpoints (nearest, images, texts, audio)
│   ├── admin/               # Admin endpoints (OSM import, content CUD, prompt templates)
│   ├── auth/                # Authentication routes
│   ├── health.py            # Health check
│   └── refdata.py           # Reference data
├── core/
│   ├── settings.py          # Pydantic settings (env config)
│   └── secrets.py           # Secret management
├── db/
│   ├── models/              # SQLAlchemy models (POI, users, generation jobs, etc.)
│   ├── queries/             # Database query helpers
│   └── enums/               # Database enums
├── services/
│   ├── osm_import/          # OSM data import pipeline
│   ├── text_generation/     # AI text generation
│   ├── image_generation/    # AI image generation
│   ├── audio_generation/    # AI audio generation
│   └── media_storage.py     # Media file storage
├── tasks/                   # Celery async tasks
├── schemas/                 # Pydantic request/response schemas
└── exceptions/              # Custom exception types
```

## Prerequisites

- Python 3.10+
- PostgreSQL with PostGIS extension
- Redis
- System packages: `osmium-tool`, `osmctools`

## Setup

### 1. Clone & create virtual environment

```bash
git clone <repo-url> && cd showme-backend
python3 -m venv venv
source venv/bin/activate
pip install poetry && poetry install
```

### 2. Configure environment

Copy `.env.example` to `.env` and populate:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/showme
DATABASE_URL_SYNCH=postgresql://user:pass@localhost:5432/showme
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_BACKEND_URL=redis://localhost:6379/1
OPEN_API_KEY=sk-...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
JWT_SECRET=...
```

### 3. Initialize database

```bash
chmod +x scripts/init_db.sh && ./scripts/init_db.sh
alembic upgrade head
```

### 4. Start services

```bash
# Redis
sudo service redis-server start

# Celery worker
celery -A app.celery_app:celery_app worker --loglevel=info

# (Optional) Celery beat scheduler
celery -A app.celery_app:celery_app beat --loglevel=info

# API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Overview

| Method | Endpoint                   | Description                   |
| ------ | -------------------------- | ----------------------------- |
| `GET`  | `/pois/nearest`            | Nearest POIs by lat/lon       |
| `POST` | `/pois/images`             | Batch-fetch POI image URLs    |
| `GET`  | `/pois/{id}/info-texts`    | AI-generated POI descriptions |
| `GET`  | `/pois/{id}/audio`         | AI-generated POI audio        |
| `POST` | `/admin/osm-import/run`    | Trigger OSM data import       |
| `GET`  | `/admin/osm-import/status` | Import job status             |
| `GET`  | `/docs`                    | Interactive Swagger UI        |

Authentication is handled via **API key** (`X-API-Key` header) and **JWT / Google OAuth** for user-facing flows.

## Development

```bash
# Run tests
pytest

# Lint & format
black app/ && isort app/

# Generate a new migration
alembic revision --autogenerate -m "description"
```

## License

Private — all rights reserved.
