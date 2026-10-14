# Medino Backend

Medino is a Django REST API backed by PostgreSQL. The current API contract is in [API reference](../docs/api.md), the container and VPS setup is in [deployment](../docs/deployment.md), and database maintenance is in [operations](../docs/operations.md). The [75-lesson reference catalog](../docs/lessons-seed.json) mirrors the catalog embedded in `seed_academics.py`.

## Architecture and stack

```text
Browser --HTTPS--> host Nginx --127.0.0.1:8080--> Docker frontend Nginx
                                           |-- React SPA (/ and /admin)
                                           |-- /api/ and /django-admin/ --> Django/Gunicorn --> PostgreSQL
                                           `-- /static/ --> collected Django static files
```

The frontend Nginx container runs as a non-root user on port 8080. It serves the built React SPA, proxies `/api/` and `/django-admin/` to the backend, and serves `/static/` from the shared `static_data` volume. `/healthz` checks the frontend container. `/admin` is a React route; Django Admin is `/django-admin/`. Uploaded media in `media_data` is **not** served from Nginx: `/media/` returns 404. Stored files are streamed by `/api/resources/{id}/file/` after Django checks visibility.

The container images use Python 3.12, PostgreSQL 18, Node 22.23.3 for the frontend build, and Nginx 1.30.5 for the frontend runtime. `requirements.txt` pins Django 5.2.17, Django REST Framework 3.16.1, SimpleJWT 5.5.1, django-cors-headers 4.9.0, Psycopg 3.2.12, and Gunicorn 23.0.0. The three backend apps are `accounts` (student identity, JWT and staff access), `academics` (sections, professors and lessons), and `resources` (uploads, moderation, files and stats).

## Local backend setup

From `backend/`, connect to a PostgreSQL server reachable from the host:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

Replace the example secret and database password in `.env`; `python -c 'from secrets import token_urlsafe; print(token_urlsafe(48))'` can generate a unique `SECRET_KEY`. Settings load `backend/.env` without overriding process environment variables. `POSTGRES_HOST=postgres` resolves only inside Compose; the Compose database is not published on the host. Never commit `.env`. PostgreSQL is required for runtime and tests; there is no SQLite fallback. The configured test user needs permission to create a test database.

```bash
python manage.py migrate
python manage.py seed_academics
python manage.py createsuperuser
python manage.py runserver
```

`createsuperuser` uses `student_no` as the login identity. The seed creates or updates six sections, 26 professors and 75 lessons on a fresh database. It matches lessons by `(section_slug, title)` and never deletes stale rows by default. Review [operations](../docs/operations.md) before using `--prune`, `--dry-run`, or the development cleanup command.

## Authentication and roles

Registration and login issue JWT access and refresh tokens; protected API calls use `Authorization: Bearer <access-token>`. The project does not override SimpleJWT's default lifetimes: access 5 minutes, refresh 1 day. Login, registration and `/api/auth/me/` return `is_staff` and `is_superuser`. Registration sets both to false on the server, regardless of client-supplied privilege fields.

| Role | Practical access |
| --- | --- |
| Student (`is_staff=False`, `is_superuser=False`) | Public reads, authenticated uploads and own upload list. |
| Staff/Admin (`is_staff=True`) | Student capabilities plus moderation, explicit direct upload, lesson writes and the user-management API. |
| Superuser (`is_superuser=True`, normally `is_staff=True`) | Staff capabilities and full Django Admin privileges. |

The user-management API lets staff grant or revoke **only** `is_staff` for other non-superusers. It cannot change `is_superuser`, cannot change any superuser's staff state, and cannot revoke the caller's own staff access. The backend API exists, but the current React frontend has no User Management page or `/admin/users` route. See [API reference](../docs/api.md#user-management).

## API and data behavior

Public reads include `/api/health/`, `/api/sections/`, `/api/lessons/`, `/api/lessons/{id}/`, and `/api/stats/`. Staff writes include lesson create, replace and delete, moderation, and staff-access changes. The lesson list accepts `section`, `search`, `professor`, `term`, `type`, and `ordering=-created_at|-views`; a detail GET does not increment stored views. Lesson deletion returns 204 and cascades to its Resource rows. After the database transaction commits, Django storage deletes a file only if no Resource still references it; storage failures are logged and may leave an orphan for operator cleanup.

Resource types are `note`, `video`, `sample`, and `summary`; statuses are `pending`, `approved`, and `rejected`. Normal uploads start pending. Staff must explicitly send `direct=true` for an immediately approved upload. Approved resources are public; pending and rejected resources are visible through the applicable API to their owner and staff. Private stored-file requests without authorization return 404. External resource URLs point to third-party hosts, which Medino cannot access-control after disclosure. Uploads accept either a file or an HTTP(S) `external_url`, never both. The default backend limit is 52,428,800 bytes (50 MiB), and container Nginx permits request bodies up to 55 MiB. See [API reference](../docs/api.md#resources-and-moderation) for extensions and response shapes.

## Environment and checks

`backend/.env.example` is the local template; root `.env.docker.example` is the Compose deployment template. Set real values in ignored `.env` or `.env.docker` files. The Django settings read these variables:

| Variable | Current behavior |
| --- | --- |
| `SECRET_KEY` | Required; no usable production default. |
| `DEBUG` | True for `1`, `true`, `yes`, or `on`; otherwise false. Use false in production. |
| `ALLOWED_HOSTS` | Comma-separated hostnames without scheme/port; no wildcard default. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated browser origins; no allow-all default. Same-origin Compose traffic can leave it empty. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins for Django Admin CSRF behind a proxy. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Required PostgreSQL connection; port must be 1–65535. Compose supplies host `postgres`, port `5432`. |
| `MAX_UPLOAD_SIZE` | Positive byte limit; default 52,428,800. |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | Boolean HTTPS settings; default false. |
| `SECURE_HSTS_SECONDS` | Non-negative HSTS lifetime; default 0. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` | Boolean HSTS options; default false. |
| `SECURE_PROXY_SSL_HEADER` | Optional, exact value `HTTP_X_FORWARDED_PROTO,https`; use only behind a trusted proxy that controls this header. |

From `backend/`, check configuration and migrations with `python manage.py check`, `python manage.py makemigrations --check`, and `python manage.py showmigrations`. Run the full PostgreSQL suite with `python manage.py test`. In the deployed environment also run `python manage.py check --deploy`; configure HTTPS forwarding before enabling SSL redirects and HSTS. Deployment commands, health checks, backup and restore are in [deployment](../docs/deployment.md) and [operations](../docs/operations.md).
