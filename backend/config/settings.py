"""Django settings for the Medino API."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def load_local_env():
    """Load the local development .env without overriding deployed environment values."""
    env_file = BASE_DIR / ".env"
    if not env_file.is_file():
        return
    allowed = {
        "SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "CORS_ALLOWED_ORIGINS", "MAX_UPLOAD_SIZE",
        "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT",
        "SECURE_SSL_REDIRECT", "SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE",
        "SECURE_HSTS_SECONDS", "SECURE_HSTS_INCLUDE_SUBDOMAINS", "SECURE_HSTS_PRELOAD",
        "SECURE_PROXY_SSL_HEADER",
    }
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in allowed:
            os.environ.setdefault(name, value.strip().strip('"').strip("'"))


load_local_env()


def env_list(name):
    return [value.strip() for value in os.environ.get(name, "").split(",") if value.strip()]


def env_bool(name, default=False):
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} must be set in the environment or backend/.env.")
    return value


def env_nonnegative_int(name, default):
    value = os.environ.get(name, str(default)).strip()
    try:
        number = int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be a non-negative integer.") from exc
    if number < 0:
        raise ImproperlyConfigured(f"{name} must be a non-negative integer.")
    return number


SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY must be set in the environment or in backend/.env. "
        "See backend/README.md for local setup."
    )

DEBUG = env_bool("DEBUG")
if not DEBUG and SECRET_KEY == "replace-with-a-long-random-value":
    raise ImproperlyConfigured("Replace the example SECRET_KEY before deployment.")
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE")
SECURE_HSTS_SECONDS = env_nonnegative_int("SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD")
proxy_ssl_header = os.environ.get("SECURE_PROXY_SSL_HEADER", "").strip()
if proxy_ssl_header:
    if proxy_ssl_header != "HTTP_X_FORWARDED_PROTO,https":
        raise ImproperlyConfigured(
            "SECURE_PROXY_SSL_HEADER must be HTTP_X_FORWARDED_PROTO,https when enabled."
        )
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.accounts.apps.AccountsConfig",
    "apps.academics.apps.AcademicsConfig",
    "apps.resources.apps.ResourcesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": required_env("POSTGRES_DB"),
        "USER": required_env("POSTGRES_USER"),
        "PASSWORD": required_env("POSTGRES_PASSWORD"),
        "HOST": required_env("POSTGRES_HOST"),
        "PORT": required_env("POSTGRES_PORT"),
    }
}
try:
    postgres_port = int(DATABASES["default"]["PORT"])
except ValueError as exc:
    raise ImproperlyConfigured("POSTGRES_PORT must be an integer from 1 to 65535.") from exc
if not 1 <= postgres_port <= 65535:
    raise ImproperlyConfigured("POSTGRES_PORT must be an integer from 1 to 65535.")

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
try:
    MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))
except ValueError as exc:
    raise ImproperlyConfigured("MAX_UPLOAD_SIZE must be a positive byte count.") from exc
if MAX_UPLOAD_SIZE <= 0:
    raise ImproperlyConfigured("MAX_UPLOAD_SIZE must be a positive byte count.")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
