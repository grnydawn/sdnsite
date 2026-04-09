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
