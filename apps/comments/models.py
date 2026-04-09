from django.conf import settings
from django.db import models


class ContentComment(models.Model):
    """Threaded comment on a content item with type and moderation status."""

    class CommentType(models.TextChoices):
        GENERAL = "general", "General note"
        CORRECTION = "correction", "Correction"
        TIP = "tip", "Tip"
        QUESTION = "question", "Question"

    class Status(models.TextChoices):
        VISIBLE = "visible", "Visible"
        FLAGGED = "flagged", "Flagged"
        HIDDEN = "hidden", "Hidden"

    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    body = models.TextField()
    comment_type = models.CharField(
        max_length=20,
        choices=CommentType.choices,
        default=CommentType.GENERAL,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.VISIBLE,
    )
    section_anchor = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content_comment"
        indexes = [
            models.Index(
                fields=["content_item", "status"],
                name="idx_cc_item",
            ),
            models.Index(fields=["user"], name="idx_cc_user"),
            models.Index(fields=["parent"], name="idx_cc_parent"),
            models.Index(fields=["comment_type"], name="idx_cc_type"),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.content_item}"
