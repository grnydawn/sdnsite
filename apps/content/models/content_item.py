from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.content.managers import ContentItemManager


class ContentItem(models.Model):
    """Polymorphic base table for all content.

    Type-specific data lives in extra_data (JSONB). The content_type FK
    determines which template renders the detail view.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEWED = "reviewed", "Reviewed"
        PUBLISHED = "published", "Published"
        DEPRECATED = "deprecated", "Deprecated"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        REGISTERED = "registered", "Registered users"
        ADMIN = "admin", "Admin only"

    content_type = models.ForeignKey(
        "content.ContentTypeDef",
        on_delete=models.PROTECT,
        related_name="items",
    )
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    title = models.CharField(max_length=300)
    summary = models.TextField(blank=True)
    body_md = models.TextField(blank=True, help_text="Markdown body")
    extra_data = models.JSONField(default=dict, blank=True)
    schema_version = models.SmallIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )

    reproducibility = models.JSONField(default=dict, blank=True)

    # Authorship / review (W3C PROV: Agent)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_items",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_items",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    content_version = models.PositiveIntegerField(default=1)

    search_vector = SearchVectorField(null=True, blank=True)

    objects = ContentItemManager()

    class Meta:
        db_table = "content_item"
        indexes = [
            models.Index(fields=["status", "visibility"], name="idx_ci_status_vis"),
            GinIndex(fields=["extra_data"], name="idx_ci_extra"),
            GinIndex(fields=["reproducibility"], name="idx_ci_repro"),
            GinIndex(fields=["search_vector"], name="idx_ci_fts"),
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title
