# Medino — Medical Education Platform

![frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite%20%2B%20Tailwind-0ea5e9)
![backend](https://img.shields.io/badge/backend-Django%20REST%20%2B%20PostgreSQL-092e20)
![lang](https://img.shields.io/badge/lang-fa%20RTL-blue)
![license](https://img.shields.io/badge/license-MIT-green)

> 🇮🇷 **نسخه فارسی:** [README.fa.md](README.fa.md)

Medino is a Persian (RTL) education platform for medical students: lecture notes, video
tutorials, past exams and summaries — from basic sciences to internship — plus general courses.

> `Education • For • Better Tomorrow`

## ✨ Features

- 🏠 Home with hero slider, quick search, live stats and 6 section cards
- 🔍 Search (lesson/professor) + 5 filters (section, resource type, professor, term, sort) with shareable URLs
- 📚 Lesson pages with 4 tabs: notes / videos / past exams / summaries
- ⬆️ Student uploads + **admin approval queue** + direct admin publishing
- 👤 Student-number auth (JWT with auto refresh), profile with personal uploads
- 🛠️ Admin lesson management (create / edit / delete)
- 🌙 Soft dark mode with persisted preference

## 🗂️ Repository map

```
Medino/
├── frontend/          # React + Vite + TS + Tailwind v4 (see below)
├── backend/           # Django REST + SimpleJWT ([backend guide](backend/README.md))
├── docs/              # Docs, incl. API contract audit + lessons seed export
├── plan.md            # Project plan + API contract (source of truth)
├── task.md            # Task breakdown + progress log
└── LICENSE            # MIT
```

## 🚀 Quick start (Docker — recommended)

Requirements: Docker Engine and Docker Compose with support for health-based `depends_on`.
From the repository root:

```bash
cp .env.docker.example .env.docker
chmod 600 .env.docker
# Edit .env.docker: replace SECRET_KEY and POSTGRES_PASSWORD with distinct random values.
docker compose --env-file .env.docker config --quiet
docker compose --env-file .env.docker build
docker compose --env-file .env.docker up -d --wait
docker compose --env-file .env.docker ps
```

Generate secrets with `python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(48))'`.
Do not reuse a development database password or commit `.env.docker`.
The example secret is deliberately rejected when `DEBUG=False`.

The complete container stack runs the React application, Django API and Admin, and PostgreSQL 18.
The browser uses one origin for the SPA and `/api/`.

```text
Browser -> Nginx :8080 -> React SPA
                      -> /api/          -> Gunicorn/Django :8000 -> PostgreSQL :5432
                      -> /django-admin/ -> Gunicorn/Django
                      -> /static/       -> collected Django static volume
```

React owns `/admin` and `/admin/pending`. Django Admin lives at `/django-admin/` to avoid a
route collision. Nginx never mounts or serves uploaded media;
`/api/resources/{id}/file/` remains the approval-aware file endpoint.

With the default `APP_BIND_HOST=127.0.0.1` and `APP_PORT=8080`, open `http://localhost:8080/`.
The API is under `http://localhost:8080/api/`, Django Admin under
`http://localhost:8080/django-admin/`, and the edge health probe under
`http://localhost:8080/healthz`. Only Nginx publishes a host port.

After startup, check `curl -f http://localhost:8080/healthz`,
`curl -f http://localhost:8080/api/health/`, and `curl -f http://localhost:8080/api/sections/`.
Open `/admin` for the React staff page and `/django-admin/` for Django's login. A user needs
`is_staff` for the React staff area and a Django staff account for Django Admin.

The one-shot `backend-init` service waits for healthy PostgreSQL, applies existing migrations,
and runs `collectstatic --noinput`. Academic content and a superuser are deliberately not
created automatically:

```bash
docker compose --env-file .env.docker run --rm backend python manage.py seed_academics
docker compose --env-file .env.docker run --rm backend python manage.py createsuperuser
```

The seed command is idempotent. The account command uses the custom `student_no` identity.
The authoritative 75-lesson catalog lives in [`docs/lessons-seed.json`](docs/lessons-seed.json).

## 💻 Local development (without Docker)

### Frontend — `http://localhost:5173`

```bash
cd frontend
npm install
cp .env.example .env    # then set real values
npm run dev             # build: npm run build | preview: npm run preview
```

| Variable | Mock mode | Real API |
|---|---|---|
| `VITE_USE_MOCK` | `true` | `false` |
| `VITE_API_URL` | — | `http://127.0.0.1:8000/api` |

With `VITE_USE_MOCK=true` the frontend runs fully offline on built-in mock data.

### Backend — `http://127.0.0.1:8000`

Full guide: [`backend/README.md`](backend/README.md). In short: venv → `pip install -r requirements.txt` →
own `backend/.env` → `migrate` → `seed_academics` → `runserver`. Keep `CORS_ALLOWED_ORIGINS`
in sync with the frontend origin (exact scheme + port).

> ⚠️ **Upload-limit coupling:** the frontend enforces 50 MiB and `MAX_UPLOAD_SIZE` is the
> authoritative backend limit — keep both sides on the same value.

## 👥 Roles

| Role | Access |
|---|---|
| Guest | Home, lessons, lesson detail, search/filters |
| Student (login) | Resource uploads, profile with personal uploads |
| Admin (`is_staff`) | `/admin` dashboard, approval queue, direct publishing, lesson management |

## 📡 API contract

The full contract is [`plan.md`](plan.md) §7; the compatibility audit is in [`docs/`](docs/).
Key points: JWT Bearer auth with refresh, `is_staff` in auth responses, `ordering=-created_at|-views`
on lesson search, `direct=true` staff uploads, approval-aware file delivery.

## Day-to-day commands (Docker)

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

`docker compose --env-file .env.docker down -v` **deletes the PostgreSQL database, uploads, and
collected static volume**. Use it only for an intentionally disposable stack. To inspect
PostgreSQL without exposing a host port, use
`docker compose --env-file .env.docker exec postgres psql -U medino -d medino`; substitute the
configured user/database names if changed.

## Services and data

| Service | Role | Network |
| --- | --- | --- |
| `postgres` | PostgreSQL 18, `pg_isready` healthcheck | Internal `data` only |
| `backend-init` | One-time migrations and static collection | Internal `data` only |
| `backend` | Non-root Gunicorn/Django, API healthcheck | `data` and `edge` |
| `frontend` | Non-root Nginx, SPA and reverse proxy, `/healthz` | `edge` only |

Volumes persist across normal `down`/`up` cycles. See the configuration, TLS/proxy and backup
notes below before exposing the stack publicly.

## Configuration and security

`.env.docker.example` lists the required variables: `SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `ALLOWED_HOSTS`, `MAX_UPLOAD_SIZE`, and the optional origin, port, and HTTPS
settings. Compose forces `POSTGRES_HOST=postgres` and `POSTGRES_PORT=5432` inside Django
containers. The frontend production build sets `VITE_USE_MOCK=false` and `VITE_API_URL=/api`;
requests remain on the browser's origin, so CORS may be empty. `CSRF_TRUSTED_ORIGINS` accepts exact
origin URLs when needed for Django Admin behind another origin. Keep `ALLOWED_HOSTS` explicit and
include the application's public host.

Nginx permits request bodies up to 55 MiB so a 50 MiB file plus multipart overhead can reach
Django. Django's `MAX_UPLOAD_SIZE` remains the authoritative file limit. Nginx does not expose
`/media/`; approved files are public through the Django file endpoint, while pending/rejected
files require the owner or staff JWT.

The supplied stack serves HTTP on loopback for local use or behind a trusted host-level TLS
gateway. For public HTTPS, the host Nginx must overwrite `X-Forwarded-Proto` with its own
`$scheme` before forwarding to the loopback-only Docker port. For example, inside a host Nginx
TLS server block (with certificates configured separately):

```nginx
server {
    listen 443 ssl;
    server_name example.com; # Replace with the deployed hostname.

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Do not pass a browser-supplied forwarded-protocol header through the host proxy or expose the
Docker port publicly; the stack binds it to `127.0.0.1` by default. Set the public
`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`, enable secure cookies and redirects, and configure
HSTS, backups, and monitoring for production.

## Backups

Back up both PostgreSQL and the `media_data` volume; a database dump alone does not contain
uploaded files. A basic database backup and restore through the PostgreSQL service:

```bash
docker compose --env-file .env.docker exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$HOME/medino.dump"
docker compose --env-file .env.docker exec -T postgres sh -c 'pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$HOME/medino.dump"
```

Perform restores during maintenance after stopping application writes. Store dumps and media
backups securely outside Git, test restoration periodically, and plan retention separately.
The stack does not implement automated backups.

## 🤝 Contributing

- The plan ([`plan.md`](plan.md)) is the source of truth; scope changes go there first.
- The frontend works fully offline with `VITE_USE_MOCK=true` — no backend needed.
- Backend-only development and API details: [backend/README.md](backend/README.md).

## 📄 License

MIT — see [`LICENSE`](LICENSE).
