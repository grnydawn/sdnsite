from django.db import models


class DataSourceSync(models.Model):
    """Tracks external metadata sync status for a content item."""

    class SyncStrategy(models.TextChoices):
        MANUAL = "manual", "Manual"
        PERIODIC = "periodic", "Periodic"
        WEBHOOK = "webhook", "Webhook"

    class SyncStatus(models.TextChoices):
        OK = "ok", "OK"
        FAILED = "failed", "Failed"
        STALE = "stale", "Stale"
        SKIPPED = "skipped", "Skipped"

    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="sync_records",
    )
    external_source_type = models.CharField(max_length=40, blank=True)
    sync_strategy = models.CharField(
        max_length=20,
        choices=SyncStrategy.choices,
        default=SyncStrategy.MANUAL,
    )
    sync_url = models.URLField(max_length=2000, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        blank=True,
    )
    raw_metadata_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "data_source_sync"
        indexes = [
            models.Index(fields=["content_item"], name="idx_dss_item"),
            models.Index(fields=["sync_status"], name="idx_dss_status"),
        ]

    def __str__(self):
        return f"Sync: {self.content_item} ({self.sync_status})"
