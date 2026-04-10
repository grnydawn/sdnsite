import pytest
from django.test import Client

from tests.factories import ContentItemFactory, ContentTypeDefFactory, UserFactory


@pytest.mark.django_db
class TestHomeView:
    """Smoke tests for home_view (TMPL-01, TMPL-02)."""

    def test_home_renders(self, client):
        """Home page returns 200 with base layout."""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_has_hero(self, client):
        """Home page has hero section with title and search placeholder (D-09)."""
        response = client.get("/")
        content = response.content.decode()
        assert "Scientific Data Portal" in content
        assert "Search coming soon" in content

    def test_home_has_content_type_grid(self, client):
        """Home page has content type cards grid (D-10)."""
        ct = ContentTypeDefFactory(name="Data Formats", slug="data_format")
        response = client.get("/")
        content = response.content.decode()
        assert "content-type-grid" in content
        assert "Data Formats" in content

    def test_home_shows_recent_items(self, client):
        """Home page shows recently updated items (D-11)."""
        item = ContentItemFactory(title="NetCDF Guide", status="published", visibility="public")
        response = client.get("/")
        content = response.content.decode()
        assert "NetCDF Guide" in content

    def test_home_no_items(self, client):
        """Home page handles empty state."""
        response = client.get("/")
        content = response.content.decode()
        assert "No content published yet." in content


@pytest.mark.django_db
class TestBrowseView:
    """Smoke tests for ContentBrowseView (TMPL-03)."""

    def test_browse_renders(self, client):
        """Browse page returns 200."""
        response = client.get("/browse/")
        assert response.status_code == 200

    def test_browse_has_card_grid(self, client):
        """Browse page uses card-grid layout (D-12)."""
        ContentItemFactory(title="Test Item", status="published", visibility="public")
        response = client.get("/browse/")
        content = response.content.decode()
        assert "card-grid" in content

    def test_browse_shows_item(self, client):
        """Browse page displays content items."""
        ContentItemFactory(title="NetCDF Format", status="published", visibility="public")
        response = client.get("/browse/")
        content = response.content.decode()
        assert "NetCDF Format" in content

    def test_browse_has_badge(self, client):
        """Browse cards have content type badge (D-13)."""
        ContentItemFactory(title="Test", status="published", visibility="public")
        response = client.get("/browse/")
        content = response.content.decode()
        assert "badge" in content

    def test_browse_type_filter(self, client):
        """Browse page filters by type parameter."""
        ct = ContentTypeDefFactory(slug="data_format", name="Data Format")
        ContentItemFactory(title="HDF5", content_type=ct, status="published", visibility="public")
        response = client.get("/browse/?type=data_format")
        assert response.status_code == 200
        content = response.content.decode()
        assert "HDF5" in content

    def test_browse_empty_state(self, client):
        """Browse page shows empty state when no items."""
        response = client.get("/browse/")
        content = response.content.decode()
        assert "No content found." in content


@pytest.mark.django_db
class TestDetailView:
    """Smoke tests for ContentDetailView (QUAL-04)."""

    def test_detail_renders(self, client):
        """Detail page returns 200 for published/public item."""
        item = ContentItemFactory(status="published", visibility="public")
        response = client.get(f"/browse/{item.slug}/")
        assert response.status_code == 200

    def test_detail_uses_fallback_template(self, client):
        """Detail page uses detail_base.html when no per-type template exists."""
        item = ContentItemFactory(status="published", visibility="public")
        response = client.get(f"/browse/{item.slug}/")
        templates_used = [t.name for t in response.templates]
        assert "content/detail_base.html" in templates_used

    def test_detail_shows_title(self, client):
        """Detail page renders the item title."""
        item = ContentItemFactory(title="NetCDF Format Guide", status="published", visibility="public")
        response = client.get(f"/browse/{item.slug}/")
        assert b"NetCDF Format Guide" in response.content

    def test_detail_shows_body(self, client):
        """Detail page renders the markdown body."""
        item = ContentItemFactory(
            body_md="## Overview\n\nThis is a test body.",
            status="published",
            visibility="public",
        )
        response = client.get(f"/browse/{item.slug}/")
        content = response.content.decode()
        assert "Overview" in content

    def test_detail_404_for_draft(self, client):
        """Detail page returns 404 for non-published items."""
        item = ContentItemFactory(status="draft", visibility="public")
        response = client.get(f"/browse/{item.slug}/")
        assert response.status_code == 404

    def test_detail_404_for_nonexistent(self, client):
        """Detail page returns 404 for non-existent slug."""
        response = client.get("/browse/nonexistent-slug-xyz/")
        assert response.status_code == 404
