# Medino Backend

Medino is a Django REST API using PostgreSQL. SQLite is no longer a runtime or test database. Existing Django migrations are retained.

## Requirements

- Python 3.12 or newer supported by the pinned Django release
- PostgreSQL 16 or newer; Docker Compose is optional for the local database
- A locally generated `SECRET_KEY` and a PostgreSQL user that can create a test database

## Setup

From `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

Edit `.env` before starting anything. Generate a unique secret, for example with `python -c 'from secrets import token_urlsafe; print(token_urlsafe(48))'`, and replace the example `SECRET_KEY`. Replace `POSTGRES_PASSWORD` with a unique local password. The backend reads `.env` without overriding variables already present in the process environment. Never commit or share `.env`.

For the included PostgreSQL 16 development database, run these commands from `backend/` after editing `.env`:

```bash
docker compose up -d --wait
docker compose ps
docker compose exec postgres pg_isready -U medino -d medino
```

If you changed `POSTGRES_USER` or `POSTGRES_DB`, pass those values to `pg_isready`. The database listens only on `127.0.0.1` at `POSTGRES_PORT` and stores data in a named Docker volume. To stop it without deleting the data:

```bash
docker compose down
```

To initialize and run the API:

```bash
python manage.py migrate
python manage.py seed_academics
python manage.py createsuperuser
python manage.py runserver
```

`createsuperuser` asks for the custom user model's `student_no`. The academic seed can be rerun: it updates its known sections and lessons without duplicating them. For a fresh database it creates 6 sections, 12 professors, and 12 lessons. A former local `db.sqlite3` may still exist as an ignored legacy file; it is never read by current settings. Check and back it up before discarding it if it contains data you need. Existing user accounts and sessions are not created by the academic seed.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Required unique Django secret; no production default. |
| `DEBUG` | Explicit `1`, `true`, `yes`, or `on` enables debug; other values disable it. |
| `ALLOWED_HOSTS` | Comma-separated API hostnames without scheme or port; no wildcard default. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated exact client origins, each with scheme and port when applicable; no allow-all default. |
| `POSTGRES_DB` | Required PostgreSQL database name. |
| `POSTGRES_USER` | Required PostgreSQL user. |
| `POSTGRES_PASSWORD` | Required PostgreSQL password. |
| `POSTGRES_HOST` | Required PostgreSQL hostname or address. |
| `POSTGRES_PORT` | Required TCP port, integer from 1 to 65535. |
| `MAX_UPLOAD_SIZE` | Positive upload limit in bytes; default 52,428,800 (50 MiB). |
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS when enabled; default false. |
| `SESSION_COOKIE_SECURE` | Send session cookies only over HTTPS when enabled; default false. |
| `CSRF_COOKIE_SECURE` | Send CSRF cookies only over HTTPS when enabled; default false. |
| `SECURE_HSTS_SECONDS` | HSTS lifetime in seconds; default 0. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Extend HSTS to subdomains; default false. |
| `SECURE_HSTS_PRELOAD` | Opt in to HSTS preload; default false. |
| `SECURE_PROXY_SSL_HEADER` | Optional exact value `HTTP_X_FORWARDED_PROTO,https` for a trusted proxy that strips client-supplied versions of this header. |

Comma-separated lists trim whitespace and ignore empty entries. Empty required database values fail during startup. Production should use `DEBUG=False`, a unique `SECRET_KEY`, explicit public `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`, HTTPS, secure cookies, and a carefully selected HSTS policy. Turn on `SECURE_SSL_REDIRECT` only after HTTPS termination and proxy forwarding are correct. HSTS preload and subdomain scope require deliberate domain-wide planning. Run `python manage.py check --deploy` with the actual deployment environment; local HTTP defaults intentionally produce security warnings.

## Database and tests

The application and test suite use `django.db.backends.postgresql` with Psycopg 3. There is no SQLite fallback. `python manage.py test` creates a PostgreSQL test database, so the configured user needs `CREATEDB` permission. Use these checks from `backend/`:

```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check
python manage.py migrate
python manage.py showmigrations
python manage.py test
```

## API

All paths below are relative to the API host.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/health/` | Public | Health response. |
| POST | `/api/auth/register/` | Public | Register a student and issue JWTs. |
| POST | `/api/auth/login/` | Public | Log in with `student_no` and password. |
| POST | `/api/auth/token/refresh/` | Refresh token | Issue a new access token. |
| GET | `/api/auth/me/` | Access token | Return the current user, including `is_staff`. |
| GET | `/api/sections/` | Public | List academic sections. |
| GET | `/api/lessons/` | Public | List, filter, search, and sort lessons. |
| GET | `/api/lessons/{id}/` | Public | Lesson and approved resources; does not increment views. |
| GET | `/api/stats/` | Public | Count lessons and approved resources by type. |
| POST | `/api/uploads/` | Access token | Upload a resource. |
| GET | `/api/uploads/mine/` | Access token | List the current user's uploads. |
| GET | `/api/admin/pending/` | Staff access token | List pending uploads. |
| POST | `/api/admin/approve/{id}/` | Staff access token | Send `action=approve` or `action=reject`. |
| GET | `/api/resources/{id}/file/` | Public if approved; otherwise owner or staff access token | Stream a stored file. |

The lesson list accepts `section`, `search`, `professor`, `term`, `type`, `ordering=-created_at`, and `ordering=-views`. Lesson views are stored values. Auth responses include `is_staff`; student registration cannot grant staff status. IDs in API responses are strings and dates use ISO 8601.

## Authentication and upload workflow

The custom user identity is `student_no`. Passwords are hashed by Django. Login and registration issue JWT access and refresh tokens. Protected endpoints expect `Authorization: Bearer <access-token>`.

Student uploads become `pending`. Staff uploads become `approved` only when the staff user explicitly supplies `direct=true`; otherwise they are pending. Staff can approve or reject a pending resource once. The server sets uploader and review fields. Approved resources appear publicly, while pending and rejected resources remain visible only to their owner and staff. Private stored files require a valid token. The default file limit is 50 MiB. Uploaded files are stored under `MEDIA_ROOT` and excluded from Git.

## Production notes

Use a managed PostgreSQL service or a properly operated PostgreSQL instance with backups and limited credentials. Put Django behind a trusted HTTPS reverse proxy, set the production environment variables above, run `python manage.py collectstatic --noinput`, serve `STATIC_ROOT` through the proxy, and run `check --deploy`. Django's development media serving is not a production file delivery strategy. Preserve the current approval-aware file endpoint or implement an equally access-controlled production media path; never expose `MEDIA_ROOT` directly if it contains private uploads. Configure request body limits at the proxy as well as `MAX_UPLOAD_SIZE` in Django. Standard error logs go to the console; do not log passwords, JWTs, or uploaded contents.
