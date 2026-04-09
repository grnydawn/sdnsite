import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model

from apps.content.models import (
    ContentTypeDef,
    ContentItem,
    ContentRelation,
    ContentSourceLink,
    SourceReference,
)
from apps.taxonomy.models import Tag, ContentTag

User = get_user_model()


@pytest.mark.django_db
class TestSeedCommand:
    """Tests for the seed_content_types management command."""

    def _run_seed(self):
        call_command("seed_content_types", verbosity=0)

    def test_content_types_have_extra_schema(self):
        """SEED-01: All 5 content types have non-null extra_schema with $schema key."""
        self._run_seed()
        assert ContentTypeDef.objects.count() == 5
        for ct in ContentTypeDef.objects.all():
            assert ct.extra_schema is not None, f"{ct.slug} has null extra_schema"
            assert "$schema" in ct.extra_schema, f"{ct.slug} missing $schema key"
            assert "properties" in ct.extra_schema, f"{ct.slug} missing properties key"

    def test_tags_all_categories(self):
        """SEED-02: Tags exist across all 5 taxonomy categories."""
        self._run_seed()
        for category in ["domain", "format", "language", "skill", "topic"]:
            assert Tag.objects.filter(category=category).exists(), (
                f"No tags in category '{category}'"
            )
        assert Tag.objects.count() >= 40

    def test_seed_items(self):
        """SEED-03: 5 published/public content items with expected slugs."""
        self._run_seed()
        qs = ContentItem.objects.filter(status="published", visibility="public")
        assert qs.count() == 5
        expected_slugs = {
            "netcdf-4", "xarray", "ncar-rda",
            "netcdf-to-zarr-workflow", "chunked-io-concept",
        }
        actual_slugs = set(qs.values_list("slug", flat=True))
        assert actual_slugs == expected_slugs

    def test_seed_items_have_extra_data(self):
        """SEED-03: Every content item has non-empty extra_data dict."""
        self._run_seed()
        for item in ContentItem.objects.all():
            assert bool(item.extra_data), f"{item.slug} has empty extra_data"

    def test_seed_items_have_body_md(self):
        """SEED-03/D-06: Every content item has markdown body with headings and code."""
        self._run_seed()
        for item in ContentItem.objects.all():
            assert "##" in item.body_md, f"{item.slug} missing ## heading"
            assert "```" in item.body_md, f"{item.slug} missing code block"

    def test_superuser_created(self):
        """SEED-04: Superuser is created when none exists."""
        self._run_seed()
        assert User.objects.filter(is_superuser=True).count() == 1
        admin = User.objects.get(is_superuser=True)
        assert admin.username == "admin"

    def test_superuser_not_duplicated(self):
        """SEED-04: Existing superuser is not duplicated."""
        User.objects.create_superuser("existing", "e@localhost", "pass")
        self._run_seed()
        assert User.objects.filter(is_superuser=True).count() == 1

    def test_relations_created(self):
        """D-09: At least 6 content relations are created."""
        self._run_seed()
        assert ContentRelation.objects.count() >= 6

    def test_sources_created(self):
        """D-10: At least 3 source references and 4 source links created."""
        self._run_seed()
        assert SourceReference.objects.count() >= 3
        assert ContentSourceLink.objects.count() >= 4

    def test_tag_assignments(self):
        """D-11: At least 10 tag assignments, 2+ per item."""
        self._run_seed()
        assert ContentTag.objects.count() >= 10
        for slug in ["netcdf-4", "xarray", "ncar-rda",
                      "netcdf-to-zarr-workflow", "chunked-io-concept"]:
            count = ContentTag.objects.filter(content_item__slug=slug).count()
            assert count >= 2, f"{slug} has only {count} tags, expected >= 2"

    def test_idempotent(self):
        """D-02: Running seed twice produces same counts."""
        self._run_seed()
        ct_count = ContentTypeDef.objects.count()
        item_count = ContentItem.objects.count()
        tag_count = Tag.objects.count()

        self._run_seed()
        assert ContentTypeDef.objects.count() == ct_count
        assert ContentItem.objects.count() == item_count
        assert Tag.objects.count() == tag_count
