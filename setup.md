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



# Raspberry Pi Deployment Checklist (Meshnet, PostGIS, OSM)

## 1. Update and Prepare the System

```sh
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install python3 python3-pip python3-venv git
```

## 2. Install Database and Dependencies

```sh
sudo apt-get install postgresql postgis
sudo apt-get install redis-server
sudo apt-get install osmctools osmium-tool
sudo service redis-server start
sudo service postgresql start
```

## 3. Clone Your Project

```sh
git clone <your-repo-url>
cd showme-backend
```

## 4. Set Up Python Environment

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install poetry
poetry install --no-dev
```

## 5. Configure Environment Variables

- Copy `.env.production` to `.env` (or create `.env`).
- Fill in all secrets, DB credentials, and set `DEBUG=false`.

## 6. Initialize Database

- Edit `init_db.sh` with your DB password if needed.
- Run the script to create the database, user, and enable PostGIS:

```sh
chmod +x init_db.sh
./init_db.sh
```

## 7. Run Database Migrations

```sh
alembic upgrade head
```

## 8. Install and Configure NordVPN Meshnet

```sh
sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
nordvpn login
nordvpn set meshnet on
```
- Enable Meshnet on your mobile device via the NordVPN app.
- Note your Pi’s Meshnet IP (e.g., `10.x.x.x`).

## 9. Start Services

- **Redis:**  
  ```sh
  sudo service redis-server start
  ```
- **Celery Worker:**  
  ```sh
  celery -A app.celery_app:celery_app worker --loglevel=info
  ```
- **(Optional) Celery Beat:**  
  ```sh
  celery -A app.celery_app:celery_app beat --loglevel=info
  ```
- **FastAPI App:**  
  ```sh
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```