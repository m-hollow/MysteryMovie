# IMP-13: Dockerized Development Environment

## Problem

Setting up the development environment requires manually installing Python 3, MySQL server, libmysqlclient, creating a database and user, configuring `.env`, running migrations, and seeding data. Devs have reported this as a source of friction — differences in local MySQL versions, missing system libraries (especially `libmysqlclient` on macOS), and misconfigured `.env` files cause setup failures.

## Goal

A single `docker compose up` command that gives developers a fully working environment mirroring the PythonAnywhere production stack (Python 3, MySQL, WSGI), with no global installs required beyond Docker itself.

## Proposed Setup

### `docker-compose.yml`

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: mmg_1
      MYSQL_USER: mmg_user_a
      MYSQL_PASSWORD: mmg_password
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 3s
      retries: 10

  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: >
      bash -c "
        python3 manage.py migrate --settings=mmg.settings.development &&
        python3 manage.py shell --settings=mmg.settings.development -c \"
          from movies.utility_functions import create_ranks, add_trophies;
          from movies.models import RoundRank;
          (RoundRank.objects.exists() or (create_ranks(), add_trophies()))
        \" &&
        python3 manage.py runserver 0.0.0.0:8000 --settings=mmg.settings.development
      "
    volumes:
      - .:/app
      - media_data:/app/media
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env

volumes:
  mysql_data:
  media_data:
```

### `Dockerfile.dev`

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
```

### `.env` changes

The development `.env` needs `DB_HOST=db` (the Docker service name) instead of `127.0.0.1`. Provide a `.env.docker` template:

```env
SECRET_KEY=change-me-in-production
DEBUG=True
DB_NAME=mmg_1
DB_USER=mmg_user_a
DB_PASSWORD=mmg_password
DB_HOST=db
```

This requires a small change to `mmg/settings/development.py` to read `DB_HOST` from the environment (currently hardcoded to `127.0.0.1`):

```python
# Current:
'HOST': '127.0.0.1',

# Changed to:
'HOST': env('DB_HOST', default='127.0.0.1'),
```

This is backwards-compatible — devs not using Docker still get `127.0.0.1` by default.

### `.dockerignore`

```
.git
.idea
.venv
venv
media/
staticfiles/
*.pyc
__pycache__
.env
.env-prod
```

## Steps

1. Add `DB_HOST` env var support to `mmg/settings/development.py` (with `127.0.0.1` default)
2. Create `Dockerfile.dev`
3. Create `docker-compose.yml`
4. Create `.env.docker` template and `.dockerignore`
5. Update `docs/SERVER_SETUP.md` with Docker quickstart section
6. Test: `cp .env.docker .env && docker compose up` should yield a working app at `localhost:8000`

## What This Mirrors From Production

| Aspect | PythonAnywhere (prod) | Docker (dev) |
|--------|----------------------|--------------|
| Python | Python 3 | Python 3.11 (closest available) |
| Database | MySQL 8.0 (`mholloway$movie_club`) | MySQL 8.0 (`mmg_1`) |
| Web server | PythonAnywhere WSGI | Django `runserver` (fine for dev) |
| Static files | Served by PythonAnywhere | Served by Django with `DEBUG=True` |
| Media files | PythonAnywhere filesystem | Docker volume mount |

## What This Does NOT Do

- No production Dockerfile — PythonAnywhere doesn't support Docker, so production deployment remains as-is (git pull + reload via PA dashboard/API)
- No container orchestration or Kubernetes — this is purely a dev convenience tool
- `createsuperuser` still requires manual interaction: `docker compose exec web python3 manage.py createsuperuser --settings=mmg.settings.development`

## Effort: Low-Medium (3-5 hours)

Most time will be spent testing the MySQL healthcheck timing and verifying the seed data idempotency.
