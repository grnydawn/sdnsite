from django.conf import settings
from django.db import models


class RevisionLog(models.Model):
    """Snapshot of a content item at a given version number."""

    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="revisions",
    )
    version_number = models.PositiveIntegerField()
    snapshot = models.JSONField()
    change_summary = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "revision_log"
        unique_together = [("content_item", "version_number")]
        indexes = [
            models.Index(fields=["content_item"], name="idx_rl_item"),
        ]
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.content_item} v{self.version_number}"
