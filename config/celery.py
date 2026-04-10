"""Celery application configuration."""

import os

from celery import Celery

# Capture whether DJANGO_SETTINGS_MODULE was explicitly set by the operator
# before this module defaults it. Used by the production safety guard below.
_explicit_dsm = os.environ.get("DJANGO_SETTINGS_MODULE")

if not _explicit_dsm:
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"

app = Celery("scidata_portal")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_finalize.connect
def _guard_production_settings(sender, **kwargs):
    """Raise ImproperlyConfigured if worker starts with DEBUG=False but no explicit settings."""
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    if not settings.DEBUG and not _explicit_dsm:
        raise ImproperlyConfigured(
            "DJANGO_SETTINGS_MODULE must be explicitly set when DEBUG=False. "
            "Refusing to start Celery worker with fallback local settings. "
            "Set DJANGO_SETTINGS_MODULE=config.settings.production before starting the worker."
        )
