from django.db import models


class ContentTypeDef(models.Model):
    """Registry of content types (e.g. data_format, software_tool).

    Adding a new content type requires only a new row here and a template —
    no migrations needed.
    """

    slug = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    extra_schema = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON Schema for validating extra_data on ContentItem",
    )
    template_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Template path for detail view, e.g. content/data_format_detail.html",
    )
    icon_slug = models.SlugField(max_length=60, blank=True)
    sort_order = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_type_def"
        ordering = ["sort_order", "name"]
        verbose_name = "Content Type"
        verbose_name_plural = "Content Types"

    def __str__(self):
        return self.name
