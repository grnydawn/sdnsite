"""Local development settings."""

import os

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# PostgreSQL required for JSONB/GIN/tsvector features
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "scidata_portal"),
        "USER": os.environ.get("POSTGRES_USER", "scidata"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Redis cache for local dev — full production parity (D-06)
# Uses db/1 to avoid collision with Celery broker on db/0
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
    }
}

# Console email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# WhiteNoise autorefresh in dev — rechecks filesystem on each request (D-01)
WHITENOISE_AUTOREFRESH = True
