need to install :
sudo apt install osmium-tool
sudo apt-get install redis-server


need to run:
celery -A app.celery_app:celery_app worker --loglevel=info

# OSM Import Pipeline & Celery Setup

## 1. Install Requirements

```bash
pip install celery[redis] psycopg2-binary
sudo apt-get install redis-server osmctools osmium-tool
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname       # For FastAPI async API
DATABASE_URL_SYNCH=postgresql://user:pass@host:5432/dbname         # For Celery/runner
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_BACKEND_URL=redis://localhost:6379/1
OSM_IMPORT_DIR=/var/tmp/osm_imports/
sudo service redis-server start
celery -A app.celery_app:celery_app worker --loglevel=info
POST /admin/osm-import/run – starts import, returns job/task ID.

GET /admin/osm-import/job-status?task_id=... – check import job status.

GET /admin/osm-import/status – check latest import log.

celery -A app.celery_app:celery_app beat --loglevel=info
#### 7. Troubleshooting
Ensure all dependencies are installed (celery, psycopg2-binary, redis-server, osmctools, osmium-tool).

Redis and Postgres must be running.

If import fails, clean up leftover OSM temp tables/functions (pipeline handles this).

For permissions or connection errors, check .env and service status.


## 2. Database changes.
alembic revision --autogenerate -m "user role enum"
 alembic upgrade head