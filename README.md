# Medino

Medino is a Persian medical education application with lesson browsing, resource uploads, moderation, and student accounts. The repository contains a React/Vite frontend and a Django REST backend; the [API contract](plan.md) and [backend guide](backend/README.md) cover development details.

The complete container stack runs the React application, Django API and Admin, and PostgreSQL 18. The browser uses one origin for the SPA and `/api/`.

```text
Browser -> Nginx :8080 -> React SPA
                      -> /api/          -> Gunicorn/Django :8000 -> PostgreSQL :5432
                      -> /django-admin/ -> Gunicorn/Django
                      -> /static/       -> collected Django static volume
```

React owns `/admin` and `/admin/pending`. Django Admin lives at `/django-admin/` to avoid a route collision. Nginx never mounts or serves uploaded media; `/api/resources/{id}/file/` remains the approval-aware file endpoint.

## Quick start

Requirements: Docker Engine and Docker Compose with support for health-based `depends_on`. From the repository root:

```bash
cp .env.docker.example .env.docker
chmod 600 .env.docker
# Edit .env.docker: replace SECRET_KEY and POSTGRES_PASSWORD with distinct random values.
docker compose --env-file .env.docker config --quiet
docker compose --env-file .env.docker build
docker compose --env-file .env.docker up -d --wait
docker compose --env-file .env.docker ps
```

Generate secrets with `python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(48))'`. Do not reuse a development database password or commit `.env.docker`. The example secret is deliberately rejected when `DEBUG=False`.

With the default `APP_BIND_HOST=127.0.0.1` and `APP_PORT=8080`, open `http://localhost:8080/`. The API is under `http://localhost:8080/api/`, Django Admin under `http://localhost:8080/django-admin/`, and the edge health probe under `http://localhost:8080/healthz`. Only Nginx publishes a host port. The backend and PostgreSQL have no host ports.

After startup, check `curl -f http://localhost:8080/healthz`, `curl -f http://localhost:8080/api/health/`, and `curl -f http://localhost:8080/api/sections/`. Open `/admin` for the React staff page and `/django-admin/` for Django's login. A user needs `is_staff` for the React staff area and a Django staff account for Django Admin.

The one-shot `backend-init` service waits for healthy PostgreSQL, applies existing migrations, and runs `collectstatic --noinput`. The backend starts only after that service completes successfully. Academic content and a superuser are deliberately not created automatically:

```bash
docker compose --env-file .env.docker run --rm backend python manage.py seed_academics
docker compose --env-file .env.docker run --rm backend python manage.py createsuperuser
```

The seed command is idempotent. The account command uses the custom `student_no` identity.

## Day-to-day commands

Run all commands from the repository root:

```bash
docker compose --env-file .env.docker build
docker compose --env-file .env.docker up -d --wait
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs -f backend
docker compose --env-file .env.docker logs -f frontend
docker compose --env-file .env.docker logs -f postgres
docker compose --env-file .env.docker run --rm backend python manage.py migrate --noinput
docker compose --env-file .env.docker run --rm backend python manage.py test
docker compose --env-file .env.docker down
```

`docker compose --env-file .env.docker down -v` **deletes the PostgreSQL database, uploads, and collected static volume**. Use it only for an intentionally disposable stack. To inspect PostgreSQL without exposing a host port, use `docker compose --env-file .env.docker exec postgres psql -U medino -d medino`; substitute the configured user/database names if changed.

## Services and data

| Service | Role | Network |
| --- | --- | --- |
| `postgres` | PostgreSQL 18, `pg_isready` healthcheck | Internal `data` only |
| `backend-init` | One-time migrations and static collection | Internal `data` only |
| `backend` | Non-root Gunicorn/Django, API healthcheck | `data` and `edge` |
| `frontend` | Non-root Nginx, SPA and reverse proxy, `/healthz` | `edge` only |

`postgres_data` is mounted at `/var/lib/postgresql`, the [official PostgreSQL 18 volume location](https://github.com/docker-library/docs/blob/master/postgres/README.md). `media_data` is mounted only into the backend at `/app/media`. `static_data` is writable by `backend-init` at `/app/staticfiles` and read-only in Nginx at `/srv/django-static`. Volumes persist across normal `down`/`up` cycles. PostgreSQL 16 data volumes are **not** directly reusable by PostgreSQL 18; plan a controlled dump/restore or major-version upgrade before replacing an existing volume. The old backend-only Compose file was removed so there is one stack definition.

## Configuration and security

`.env.docker.example` lists the required variables: `SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ALLOWED_HOSTS`, `MAX_UPLOAD_SIZE`, and the optional origin, port, and HTTPS settings. Compose forces `POSTGRES_HOST=postgres` and `POSTGRES_PORT=5432` inside Django containers. The frontend production build sets `VITE_USE_MOCK=false` and `VITE_API_URL=/api`; requests remain on the browser's origin, so CORS may be empty. `CSRF_TRUSTED_ORIGINS` accepts exact origin URLs when needed for Django Admin behind another origin. Keep `ALLOWED_HOSTS` explicit and include the application's public host.

Nginx permits request bodies up to 55 MiB so a 50 MiB file plus multipart overhead can reach Django. Django's `MAX_UPLOAD_SIZE` remains the authoritative file limit. Nginx does not expose `/media/`; approved files are public through the Django file endpoint, while pending/rejected files require the owner or staff JWT. External URLs are controlled by their external host and cannot be made private by this stack.

The supplied stack serves HTTP on loopback for local use or for a trusted host-level TLS gateway. For a real public deployment, configure HTTPS termination, secure cookies, redirects, HSTS, a trusted forwarded-protocol chain, public hosts, CSRF origins, backups, and monitoring. Nginx currently sends its own `$scheme` to Django, which is correct for direct HTTP use; if TLS terminates **before** this container, the deployment must configure that trusted proxy chain so Django receives the verified HTTPS scheme. Do not trust client-supplied `X-Forwarded-Proto` on a publicly exposed HTTP port. Keep the Compose port bound to loopback until TLS is ready.

## Backups

Back up both PostgreSQL and the `media_data` volume; a database dump alone does not contain uploaded files. A basic database backup and restore through the PostgreSQL service:

```bash
docker compose --env-file .env.docker exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$HOME/medino.dump"
docker compose --env-file .env.docker exec -T postgres sh -c 'pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$HOME/medino.dump"
```

Perform restores during maintenance after stopping application writes. Store dumps and media backups securely outside Git, test restoration periodically, and plan retention separately. The stack does not implement automated backups.

Backend-only development and API details are documented in [backend/README.md](backend/README.md).
