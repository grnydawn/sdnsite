"""Infrastructure verification tests for INFRA-01, INFRA-02, INFRA-03."""

import pytest
from unittest.mock import patch
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class TestWhiteNoise:
    """INFRA-01: WhiteNoise configured for static file serving."""

    def test_whitenoise_in_middleware(self):
        assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE

    def test_whitenoise_storage_backend(self):
        backend = settings.STORAGES["staticfiles"]["BACKEND"]
        assert backend == "whitenoise.storage.CompressedManifestStaticFilesStorage"

    def test_whitenoise_autorefresh(self):
        assert settings.WHITENOISE_AUTOREFRESH is True


class TestRedisConfig:
    """INFRA-02: Redis configured for broker and cache."""

    def test_redis_cache_backend(self):
        backend = settings.CACHES["default"]["BACKEND"]
        assert backend == "django.core.cache.backends.redis.RedisCache"

    def test_redis_cache_location_uses_db1(self):
        location = settings.CACHES["default"]["LOCATION"]
        assert "/1" in location, f"Cache should use Redis db/1, got: {location}"

    def test_celery_broker_url_is_redis(self):
        assert "redis://" in settings.CELERY_BROKER_URL

    def test_redis_ping(self):
        """Verify Redis server is reachable (skip if not running)."""
        import redis as redis_lib

        try:
            client = redis_lib.Redis.from_url(settings.CELERY_BROKER_URL)
            result = client.ping()
            assert result is True
        except redis_lib.exceptions.ConnectionError:
            pytest.skip("Redis server not running")


class TestCeleryGuard:
    """INFRA-03: Production safety guard in celery.py."""

    def test_guard_raises_when_debug_false_no_explicit_dsm(self):
        from config.celery import _guard_production_settings

        with patch.object(settings, "DEBUG", False):
            import config.celery as celery_mod
            original = celery_mod._explicit_dsm
            try:
                celery_mod._explicit_dsm = None
                with pytest.raises(ImproperlyConfigured, match="DJANGO_SETTINGS_MODULE must be explicitly set"):
                    _guard_production_settings(sender=None)
            finally:
                celery_mod._explicit_dsm = original

    def test_guard_ok_when_debug_true(self):
        from config.celery import _guard_production_settings

        with patch.object(settings, "DEBUG", True):
            import config.celery as celery_mod
            original = celery_mod._explicit_dsm
            try:
                celery_mod._explicit_dsm = None
                # Should not raise
                _guard_production_settings(sender=None)
            finally:
                celery_mod._explicit_dsm = original

    def test_guard_ok_when_explicit_dsm_set(self):
        from config.celery import _guard_production_settings

        with patch.object(settings, "DEBUG", False):
            import config.celery as celery_mod
            original = celery_mod._explicit_dsm
            try:
                celery_mod._explicit_dsm = "config.settings.production"
                # Should not raise even with DEBUG=False
                _guard_production_settings(sender=None)
            finally:
                celery_mod._explicit_dsm = original

    def test_celery_module_has_explicit_dsm_variable(self):
        import config.celery as celery_mod
        assert hasattr(celery_mod, "_explicit_dsm")

    def test_celery_module_does_not_use_setdefault(self):
        import inspect
        import config.celery as celery_mod
        source = inspect.getsource(celery_mod)
        assert "setdefault" not in source, "celery.py must not use os.environ.setdefault"
