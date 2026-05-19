# IMP-14: Migrate from MySQL to PostgreSQL

## Problem

The project uses MySQL (mysqlclient) which requires installing `libmysqlclient` — a system-level C library that is a frequent source of setup issues, particularly on macOS where it must be installed via Homebrew or from Oracle's download page. PostgreSQL's Python driver (`psycopg2-binary`) is a self-contained wheel with no system dependencies, eliminating this friction entirely.

Beyond setup, PostgreSQL is Django's best-supported database backend. Several Django features work better or only with PostgreSQL (e.g., `ArrayField`, `JSONField` with full indexing, full-text search, `ExclusionConstraint`). PythonAnywhere also supports PostgreSQL databases as an alternative to MySQL.

## Current State

- **Development**: MySQL 8.0, `django.db.backends.mysql`, database `mmg_1`
- **Production**: MySQL on PythonAnywhere, `mholloway$movie_club`
- **Driver**: `mysqlclient==2.2.3` (requires `libmysqlclient`)
- **MySQL-specific config**: `charset: utf8mb4` (both settings files), `SET sql_mode='STRICT_TRANS_TABLES'` (production only)
- **Raw SQL**: None — all queries use the Django ORM, so no MySQL-specific SQL to rewrite

## Why PostgreSQL

| Aspect | MySQL (current) | PostgreSQL |
|--------|----------------|------------|
| Python driver install | Requires `libmysqlclient` system library | `psycopg2-binary` — no system deps |
| Django support | Good | Best-supported; exclusive features available |
| PythonAnywhere | Supported | Supported (on paid plans) |
| Docker dev setup | Works fine | Works fine, slightly simpler image |
| Data types | Standard | Richer (array, jsonb, range, etc.) |

## Migration Steps

### Phase 1: Update Settings & Dependencies

1. Replace `mysqlclient` with `psycopg2-binary` in `requirements.txt`:
   ```
   # Remove: mysqlclient==2.2.3
   # Add:
   psycopg2-binary>=2.9
   ```

2. Update `mmg/settings/development.py` database config:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': env('DB_NAME'),
           'USER': env('DB_USER'),
           'PASSWORD': env('DB_PASSWORD'),
           'HOST': env('DB_HOST', default='127.0.0.1'),
           'PORT': env('DB_PORT', default='5432'),
       }
   }
   ```

3. Update `mmg/settings/production.py` database config:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.getenv('DATABASE_NAME'),
           'USER': os.getenv('DATABASE_USER'),
           'PASSWORD': os.getenv('DATABASE_PASSWORD'),
           'HOST': os.getenv('DATABASE_HOST'),
           'PORT': os.getenv('DATABASE_PORT', '5432'),
       }
   }
   ```

4. Remove MySQL-specific `OPTIONS` (`charset`, `init_command`) — PostgreSQL uses UTF-8 by default and has strict mode built in.

### Phase 2: Update Development Environment

5. Update `.env` / `.env.docker` templates with PostgreSQL defaults:
   ```env
   DB_NAME=mmg_1
   DB_USER=mmg_user_a
   DB_PASSWORD=mmg_password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   ```

6. Update `scripts/server_setup.sh` — replace `sudo mysql` commands with:
   ```bash
   sudo -u postgres psql <<EOF
   CREATE DATABASE mmg_1;
   CREATE USER mmg_user_a WITH PASSWORD 'mmg_password';
   GRANT ALL PRIVILEGES ON DATABASE mmg_1 TO mmg_user_a;
   ALTER DATABASE mmg_1 OWNER TO mmg_user_a;
   EOF
   ```

7. Update `docs/SERVER_SETUP.md` — replace MySQL setup instructions with PostgreSQL equivalents.

8. If IMP-13 (Docker dev) is done, update `docker-compose.yml`:
   ```yaml
   db:
     image: postgres:16
     environment:
       POSTGRES_DB: mmg_1
       POSTGRES_USER: mmg_user_a
       POSTGRES_PASSWORD: mmg_password
     volumes:
       - postgres_data:/var/lib/postgresql/data
   ```
   And update `Dockerfile.dev` — remove `default-libmysqlclient-dev` and `build-essential` (no longer needed).

### Phase 3: Migrate Data (Production)

9. On PythonAnywhere, create a new PostgreSQL database.

10. Export data from MySQL and import to PostgreSQL. Recommended approach using Django:
    ```bash
    # On current MySQL-backed setup:
    python3 manage.py dumpdata --natural-foreign --natural-primary -o dump.json --settings=mmg.settings.production

    # Switch settings to PostgreSQL, then:
    python3 manage.py migrate --settings=mmg.settings.production
    python3 manage.py loaddata dump.json --settings=mmg.settings.production
    ```

11. Update PythonAnywhere environment variables to point to the new PostgreSQL database.

12. Reload the web app and verify.

### Phase 4: Cleanup

13. Remove `mysqlclient` from `requirements.txt`.
14. Remove any remaining MySQL references from documentation.
15. Drop the old MySQL database on PythonAnywhere after confirming PostgreSQL is stable.

## Ordering Dependencies

- **Should be done after IMP-10 (Django upgrade)**: Newer Django versions have better PostgreSQL support and updated migration tooling.
- **Coordinate with IMP-13 (Docker dev)**: If Docker is set up first, update the compose file as part of this migration. If not, this migration simplifies the future Docker setup since `psycopg2-binary` has no system deps.
- **Should be done after IMP-04 (test suite)**: Having tests in place before a database migration provides confidence that nothing breaks.

## Risks

- **Data migration**: `dumpdata`/`loaddata` handles most cases, but large text fields or binary data should be spot-checked after import. The dataset for this app is small enough that manual verification is feasible.
- **PythonAnywhere PostgreSQL**: Available on paid plans. Verify the current plan includes PostgreSQL access before starting.
- **Auto-increment behavior**: MySQL uses `AUTO_INCREMENT`, PostgreSQL uses sequences. Django's ORM handles this transparently, but if any fixtures or seed data hardcode IDs, they should be tested.

## Effort: Medium (4-6 hours)

Most time is in the production data migration and verification. The code changes themselves are minimal since no raw SQL is used.
