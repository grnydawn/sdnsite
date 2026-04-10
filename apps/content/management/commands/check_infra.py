"""Management command to verify infrastructure connectivity."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import OperationalError, connections


class Command(BaseCommand):
    help = "Verify infrastructure connectivity: PostgreSQL, Redis, WhiteNoise, Celery"

    def handle(self, *args, **options):
        self.stdout.write("\nInfrastructure Check")
        self.stdout.write("=" * 20)

        results = {
            "pass": 0,
            "fail": 0,
            "warn": 0,
        }

        # PostgreSQL
        if self._check_postgres():
            results["pass"] += 1
        else:
            results["fail"] += 1

        # Redis
        if self._check_redis():
            results["pass"] += 1
        else:
            results["fail"] += 1

        # WhiteNoise
        if self._check_whitenoise():
            results["pass"] += 1
        else:
            results["fail"] += 1

        # Celery
        celery_result = self._check_celery()
        if celery_result == "pass":
            results["pass"] += 1
        elif celery_result == "warn":
            results["warn"] += 1
        else:
            results["fail"] += 1

        self.stdout.write(
            f"\nResult: {results['pass']} passed, "
            f"{results['fail']} failed, "
            f"{results['warn']} warning(s)"
        )

        if results["fail"] > 0:
            raise SystemExit(1)

    def _check_postgres(self):
        try:
            conn = connections["default"]
            conn.ensure_connection()
            self.stdout.write(self.style.SUCCESS("  [PASS] PostgreSQL"))
            return True
        except OperationalError as e:
            self.stderr.write(self.style.ERROR(f"  [FAIL] PostgreSQL: {e}"))
            return False

    def _check_redis(self):
        import redis as redis_lib

        try:
            url = settings.CELERY_BROKER_URL
            client = redis_lib.Redis.from_url(url)
            client.ping()
            self.stdout.write(self.style.SUCCESS("  [PASS] Redis"))
            return True
        except redis_lib.exceptions.ConnectionError as e:
            self.stderr.write(self.style.ERROR(f"  [FAIL] Redis: {e}"))
            return False

    def _check_whitenoise(self):
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists() and any(static_root.iterdir()):
            self.stdout.write(
                self.style.SUCCESS("  [PASS] WhiteNoise static root populated")
            )
            return True
        else:
            self.stderr.write(
                self.style.ERROR(
                    f"  [FAIL] WhiteNoise: STATIC_ROOT {static_root} "
                    "empty or missing. Run: python manage.py collectstatic"
                )
            )
            return False

    def _check_celery(self):
        try:
            from config.celery import app as celery_app

            response = celery_app.control.ping(timeout=3)
            if response:
                self.stdout.write(self.style.SUCCESS("  [PASS] Celery worker"))
                return "pass"
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "  [WARN] Celery: no workers responded (worker not running?)"
                    )
                )
                return "warn"
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  [FAIL] Celery: {e}"))
            return "fail"
