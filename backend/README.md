# Running the Medino backend locally

`backend/.env` is local and ignored by Git. Each developer must create their own copy before starting Django. The settings module reads this file automatically; an already defined environment variable takes precedence.

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python - <<'PY'
from pathlib import Path
from secrets import token_urlsafe

template = Path('.env.example').read_text(encoding='utf-8')
target = Path('.env')
if target.exists():
    raise SystemExit('backend/.env already exists; keeping the existing secret')
target.write_text(
    template.replace('replace-with-a-long-random-value', token_urlsafe(48)),
    encoding='utf-8',
)
target.chmod(0o600)
PY
python manage.py check
python manage.py migrate
python manage.py runserver
```

Do not commit or share `.env`. For local development, its `ALLOWED_HOSTS` value contains the backend hostnames without a scheme or port. Its `CORS_ALLOWED_ORIGINS` value must contain the exact frontend origins, including scheme and port. For example, a frontend opened at `http://127.0.0.1:5173` needs that origin added to `CORS_ALLOWED_ORIGINS`.

On a separate frontend machine, set `frontend/.env` to `VITE_USE_MOCK=false` and `VITE_API_URL=http://<reachable-backend-host>:8000/api`; also add the backend host to `ALLOWED_HOSTS` and the frontend origin to `CORS_ALLOWED_ORIGINS` on the backend machine.
