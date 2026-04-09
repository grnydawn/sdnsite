from django.db import models


class ContentRelation(models.Model):
    """Typed knowledge graph edge between two content items.

    Aligned with FAIR qualified references.
    """

    class RelationType(models.TextChoices):
        RELATED_TO = "related_to", "Related to"
        SUPPORTED_BY = "supported_by", "Supported by"
        READS = "reads", "Reads"
        WRITES = "writes", "Writes"
        USES = "uses", "Uses"
        INPUT_FORMAT = "input_format", "Input format"
        OUTPUT_FORMAT = "output_format", "Output format"
        SOURCE_REPOSITORY = "source_repository", "Source repository"
        CONVERTS_TO = "converts_to", "Converts to"
        SUPERSEDES = "supersedes", "Supersedes"
        REQUIRES = "requires", "Requires"
        EXAMPLE_OF = "example_of", "Example of"

    from_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="relations_from",
    )
    to_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="relations_to",
    )
    rel_type = models.CharField(
        max_length=40,
        choices=RelationType.choices,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_relation"
        unique_together = [("from_item", "to_item", "rel_type")]
        indexes = [
            models.Index(fields=["from_item"], name="idx_cr_from"),
            models.Index(fields=["to_item"], name="idx_cr_to"),
            models.Index(fields=["rel_type"], name="idx_cr_type"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_item=models.F("to_item")),
                name="no_self_relation",
            ),
        ]

    def __str__(self):
        return f"{self.from_item} —[{self.rel_type}]→ {self.to_item}"
