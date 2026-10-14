# Medino deployment

This guide describes the repository's Docker Compose deployment on a VPS. Run Compose commands from the repository root. For backend endpoints and permissions see [API reference](api.md); for seed, backup and test procedures see [operations](operations.md). The root README is an overview, while `backend/README.md` covers backend setup and settings.

## Topology

```text
Internet browser --HTTPS--> host Nginx --HTTP on 127.0.0.1:8080--> frontend Nginx
                                    / and /admin: React SPA
                                    /static/: collected Django static files
                                    /api/, /django-admin/: backend Gunicorn/Django --> PostgreSQL
                                    /media/: 404 (never direct public media access)
```

The Compose frontend image builds React with `VITE_USE_MOCK=false` and `VITE_API_URL=/api`, so browser API calls use the same origin. The frontend runtime is non-root Nginx on port 8080 with SPA fallback, `/healthz`, `/api/` and `/django-admin/` proxies, and a 55 MiB body limit. Its upstream is `backend:8000`. Host Nginx terminates HTTPS and forwards only to the loopback-bound Compose frontend port. Do not publish backend port 8000 or PostgreSQL port 5432 to the Internet. `/admin` is the React dashboard; `/django-admin/` is Django Admin. There is currently no React User Management route, although its backend API exists.

| Compose service | Responsibility | Networks | Persistent mount |
| --- | --- | --- | --- |
| `postgres` (`postgres:18`) | PostgreSQL; `pg_isready` health check | Internal `data` only | `postgres_data` at `/var/lib/postgresql` |
| `backend-init` | Runs `migrate --noinput` and `collectstatic --noinput`, then exits successfully | Internal `data` only | `static_data` at `/app/staticfiles` |
| `backend` | Non-root Gunicorn/Django on container port 8000; `/api/health/` health check | `data` and `edge` | `media_data` at `/app/media` |
| `frontend` | Non-root Nginx, React SPA, API/Django Admin proxy; `/healthz` health check | `edge` only | `static_data` read-only at `/srv/django-static` |

The `data` network is Compose-internal; the `edge` network connects frontend to backend. Only the frontend publishes a host port, by default `127.0.0.1:8080`. Named volumes persist across normal container recreation and `docker compose down`. The `media_data` volume holds uploaded files; the frontend does not mount it. Django streams stored files through `/api/resources/{id}/file/` with approval/owner/staff checks. Frontend Nginx deliberately returns 404 for `/media/`.

## Environment preparation

Copy the safe template to a Git-ignored deployment file and replace placeholders:

```bash
cp .env.docker.example .env.docker
chmod 600 .env.docker
python3 -c 'from secrets import token_urlsafe; print(token_urlsafe(48))'
```

Use the generated value for a unique `SECRET_KEY`; generate a different strong `POSTGRES_PASSWORD`. Do not put either value in Git, shell history, logs, or shared documentation. `backend/.env.example` is a separate template for a host-run backend; Compose consumes root `.env.docker` and forces `POSTGRES_HOST=postgres`, `POSTGRES_PORT=5432` for Django containers. `postgres` is a Docker DNS name, not a host machine name. The application and tests have no SQLite fallback.

For production, set `DEBUG=False`, `ALLOWED_HOSTS` to the public hostname(s) (and any explicitly needed internal host), and `CSRF_TRUSTED_ORIGINS` to the public HTTPS origin(s) used for Django Admin. `CORS_ALLOWED_ORIGINS` may stay empty for the same-origin Compose frontend; set exact origins only for separately hosted clients. Keep `APP_BIND_HOST=127.0.0.1` and select `APP_PORT` if 8080 is occupied. `MAX_UPLOAD_SIZE` defaults to 52,428,800 bytes (50 MiB); keep the host proxy request limit at least as high as the container Nginx 55 MiB body limit if files near that size must work.

After host TLS and forwarding are verified, set `SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https`, `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, and `CSRF_COOKIE_SECURE=True`. The backend accepts only that exact proxy-header setting. `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, and `SECURE_HSTS_PRELOAD` are optional and default to off; enable HSTS only after HTTPS works reliably for the intended domain scope. The trusted host proxy must overwrite any client-supplied `X-Forwarded-Proto` header.

## Start and verify the Compose stack

```bash
docker compose --env-file .env.docker config --quiet
docker compose --env-file .env.docker build
docker compose --env-file .env.docker up -d --wait
docker compose --env-file .env.docker ps
docker compose --env-file .env.docker logs --tail=100 backend-init
```

`backend-init` waits for healthy PostgreSQL and runs migrations and static collection. `backend` waits for it to exit successfully, and `frontend` waits for a healthy backend. For local loopback verification:

```bash
curl -f http://127.0.0.1:8080/healthz
curl -f http://127.0.0.1:8080/api/health/
curl -f http://127.0.0.1:8080/api/sections/
```

The backend health check probes `/api/health/` inside its container; the frontend health check probes `/healthz`. These checks show process and routing health, not full business-flow correctness. `docker compose --env-file .env.docker down` stops containers but retains named volumes. **Do not use `down -v` on a database or upload volume you intend to keep.**

After the stack is healthy, management commands can run in the existing backend container:

```bash
docker compose --env-file .env.docker exec backend python manage.py check
docker compose --env-file .env.docker exec backend python manage.py showmigrations
docker compose --env-file .env.docker exec backend python manage.py createsuperuser
docker compose --env-file .env.docker exec backend python manage.py seed_academics
```

`createsuperuser` asks for `student_no`. The seed is non-destructive by default; use [operations](operations.md#academic-seed-and-prune) for dry-run and prune rules. For a one-off process instead of `exec`, `docker compose --env-file .env.docker run --rm backend python manage.py test` uses the service configuration and dependencies. PostgreSQL test execution requires the configured database user to be able to create a test database.

## VPS DNS and host Nginx

Create a DNS `A` record for `example.com` pointing to `SERVER_IP` and, if using `www`, a `CNAME` from `www` to `example.com`. DNS-only mode can simplify initial origin verification. Replace these placeholders with your own domain and IP; this repository does not store a production address. Ensure the VPS firewall allows public HTTP/HTTPS to host Nginx while the Compose application remains bound to loopback.

Install and configure host Nginx as the public reverse proxy. A bootstrap HTTP server block can forward to the current Compose port; use a matching domain in `ALLOWED_HOSTS`:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    client_max_body_size 55m;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Check host Nginx syntax and reload it after installation. Obtain a Let's Encrypt certificate with Certbot's Nginx integration, for example `certbot --nginx -d example.com -d www.example.com`, and check renewal with `certbot renew --dry-run`. Verify the resulting HTTPS server block still forwards the four headers above, retains the body limit, and redirects ordinary HTTP traffic to HTTPS. The host proxy must set `X-Forwarded-Proto` from its own `$scheme`; the Docker frontend Nginx maps only `http` or `https` values and forwards that scheme to Django. Thus an HTTPS browser request stays marked HTTPS across both proxy hops, allowing Django's configured `SECURE_PROXY_SSL_HEADER` to work. Do not trust an arbitrary client-provided forwarded scheme or expose the loopback application port publicly.

## Upgrade workflow

1. Back up PostgreSQL and `media_data` before a risky upgrade; see [backup and restore](operations.md#backup-and-restore). Plan maintenance for schema or destructive data changes.
2. Update the repository (`git pull` on the intended branch), then review changed images, migrations and environment-template fields. Build on the VPS with `docker compose --env-file .env.docker build` or load prebuilt images as described below.
3. Run `docker compose --env-file .env.docker up -d --wait`. The `backend-init` service performs `migrate` and `collectstatic` before the backend and frontend become healthy. Check `docker compose --env-file .env.docker logs --tail=100 backend-init`, then `docker compose --env-file .env.docker exec backend python manage.py showmigrations`.
4. Check `docker compose --env-file .env.docker ps`, `/healthz`, `/api/health/`, and the smoke tests below over the public HTTPS domain. Watch `docker compose --env-file .env.docker logs -f backend` and the host Nginx logs for failures.

If the VPS cannot pull/build required registry images, build in a compatible environment, identify the exact image names with `docker compose --env-file .env.docker images`, transfer them with `docker save` and `scp`, then `docker load` on the VPS before `up -d --wait`. Preserve the image names/tags expected by Compose; this is an alternative to a VPS-side build, not an automated release pipeline.

## Smoke tests

Over the public HTTPS hostname, check `/`, `/healthz`, `/api/health/`, `/api/sections/`, `/api/lessons/`, and `/django-admin/`. `/admin` should load the React dashboard; `/django-admin/` should load Django Admin. Then exercise login, a student upload, the staff pending queue, approval, direct staff upload, staff lesson create/edit/delete, and the **backend** user-management API. There is currently no React User Management page. Check a private file as owner/staff and verify an anonymous request is rejected. Confirm `/media/` does not expose uploads.

For routine logs and tests see [operations](operations.md#checks-logs-and-test-suite). Keep backups and secrets outside Git. The repository does not configure automated backups or monitoring.
