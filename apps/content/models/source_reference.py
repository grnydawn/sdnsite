from django.db import models


class SourceReference(models.Model):
    """Reusable citation entity aligned with DataCite 4.7.

    One source can be cited by many content items via ContentSourceLink.
    """

    class SourceType(models.TextChoices):
        OFFICIAL_SPEC = "official_spec", "Official Specification"
        OFFICIAL_DOCS = "official_docs", "Official Documentation"
        PAPER = "paper", "Paper"
        REPOSITORY = "repository", "Repository"
        POLICY = "policy", "Policy"
        TUTORIAL = "tutorial", "Tutorial"
        COMMUNITY_NOTE = "community_note", "Community Note"

    class IdentifierType(models.TextChoices):
        DOI = "DOI", "DOI"
        URL = "URL", "URL"
        RRID = "RRID", "RRID"
        ACCESSION = "Accession", "Accession"
        ISBN = "ISBN", "ISBN"
        ARXIV = "arXiv", "arXiv"
        OTHER = "other", "Other"

    title = models.TextField()
    url = models.URLField(max_length=2000, blank=True)
    source_type = models.CharField(
        max_length=40,
        choices=SourceType.choices,
        blank=True,
    )
    publisher = models.TextField(blank=True)
    publication_date = models.DateField(null=True, blank=True)
    access_date = models.DateField(null=True, blank=True)
    version_label = models.CharField(max_length=80, blank=True)
    license = models.TextField(blank=True)
    citation_text = models.TextField(blank=True)
    identifier_type = models.CharField(
        max_length=20,
        choices=IdentifierType.choices,
        blank=True,
    )
    identifier_value = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "source_reference"
        indexes = [
            models.Index(fields=["source_type"], name="idx_sr_type"),
            models.Index(
                fields=["identifier_type", "identifier_value"],
                name="idx_sr_doi",
            ),
        ]

    def __str__(self):
        return self.title


class ContentSourceLink(models.Model):
    """Junction table: many content items cite many sources with a role."""

    class LinkRole(models.TextChoices):
        PRIMARY_SPEC = "primary_spec", "Primary Specification"
        DOCUMENTATION = "documentation", "Documentation"
        PAPER = "paper", "Paper"
        TUTORIAL = "tutorial", "Tutorial"
        EXAMPLE = "example", "Example"
        RELATED = "related", "Related"

    content_item = models.ForeignKey(
        "content.ContentItem",
        on_delete=models.CASCADE,
        related_name="source_links",
    )
    source_ref = models.ForeignKey(
        SourceReference,
        on_delete=models.RESTRICT,
        related_name="content_links",
    )
    link_role = models.CharField(
        max_length=40,
        choices=LinkRole.choices,
        default=LinkRole.RELATED,
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "content_source_link"
        unique_together = [("content_item", "source_ref", "link_role")]
        indexes = [
            models.Index(fields=["content_item"], name="idx_csl_item"),
            models.Index(fields=["source_ref"], name="idx_csl_ref"),
        ]

    def __str__(self):
        return f"{self.content_item} → {self.source_ref} ({self.link_role})"
