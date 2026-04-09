from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Extended profile for auth.User — data minimization by design."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
    )
    affiliation = models.TextField(blank=True)
    orcid = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return f"Profile: {self.user.username}"


class SavedItem(models.Model):
    """Bookmark: user saves a content item for later."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_items",
    )
    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_item"
        unique_together = [("user", "content_item")]

    def __str__(self):
        return f"{self.user} saved {self.content_item}"


class AdminAuditLog(models.Model):
    """Audit trail for admin actions (NIST Privacy Framework compliance)."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=60)
    target_type = models.CharField(max_length=60, blank=True)
    target_id = models.BigIntegerField(null=True, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_audit_log"
        indexes = [
            models.Index(fields=["actor"], name="idx_aal_actor"),
            models.Index(
                fields=["target_type", "target_id"],
                name="idx_aal_target",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor}: {self.action} on {self.target_type}#{self.target_id}"
