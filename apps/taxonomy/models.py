from django.db import models


class Tag(models.Model):
    """Hierarchical tag with category for faceted navigation."""

    class Category(models.TextChoices):
        DOMAIN = "domain", "Domain"
        FORMAT = "format", "Format"
        LANGUAGE = "language", "Language"
        SKILL = "skill", "Skill Level"
        TOPIC = "topic", "Topic"
        OTHER = "other", "Other"

    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        db_index=True,
    )
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    class Meta:
        db_table = "tag"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.category}/{self.name}"


class ContentTag(models.Model):
    """Junction table linking content items to tags."""

    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="content_tags",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="content_tags",
    )

    class Meta:
        db_table = "content_tag"
        unique_together = [("content_item", "tag")]
        indexes = [
            models.Index(fields=["tag"], name="idx_ct_tag"),
            models.Index(fields=["content_item"], name="idx_ct_item"),
        ]

    def __str__(self):
        return f"{self.content_item} — {self.tag}"
