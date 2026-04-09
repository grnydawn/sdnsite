import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError

from apps.content.models import ContentItem, ContentRelation

from .factories import ContentItemFactory, ContentTypeDefFactory, UserFactory


@pytest.mark.django_db
class TestContentTypeDef:
    def test_create(self, content_type_def):
        assert content_type_def.pk is not None
        assert content_type_def.is_active is True

    def test_slug_unique(self, content_type_def):
        with pytest.raises(IntegrityError):
            ContentTypeDefFactory(slug=content_type_def.slug)

    def test_str(self, content_type_def):
        assert str(content_type_def) == content_type_def.name


@pytest.mark.django_db
class TestContentItem:
    def test_create(self, content_item):
        assert content_item.pk is not None
        assert content_item.content_version == 1

    def test_slug_unique(self, content_item):
        with pytest.raises(IntegrityError):
            ContentItemFactory(slug=content_item.slug)

    def test_default_status(self):
        ct = ContentTypeDefFactory()
        item = ContentItem.objects.create(
            content_type=ct,
            slug="test-default",
            title="Test Default",
        )
        assert item.status == "draft"
        assert item.visibility == "public"

    def test_version_increments_on_save(self, content_item):
        assert content_item.content_version == 1
        content_item.title = "Updated Title"
        content_item.save()
        content_item.refresh_from_db()
        assert content_item.content_version == 2


@pytest.mark.django_db
class TestContentItemManager:
    def _make_items(self):
        ct = ContentTypeDefFactory()
        pub_public = ContentItemFactory(
            content_type=ct, status="published", visibility="public"
        )
        pub_registered = ContentItemFactory(
            content_type=ct, status="published", visibility="registered"
        )
        pub_admin = ContentItemFactory(
            content_type=ct, status="published", visibility="admin"
        )
        draft = ContentItemFactory(
            content_type=ct, status="draft", visibility="public"
        )
        return pub_public, pub_registered, pub_admin, draft

    def test_anonymous_sees_only_public_published(self):
        pub_public, pub_registered, pub_admin, draft = self._make_items()
        anon = AnonymousUser()
        qs = ContentItem.objects.visible_to(anon)
        assert pub_public in qs
        assert pub_registered not in qs
        assert pub_admin not in qs
        assert draft not in qs

    def test_authenticated_sees_public_and_registered(self):
        pub_public, pub_registered, pub_admin, draft = self._make_items()
        user = UserFactory()
        qs = ContentItem.objects.visible_to(user)
        assert pub_public in qs
        assert pub_registered in qs
        assert pub_admin not in qs
        assert draft not in qs

    def test_staff_sees_everything(self):
        pub_public, pub_registered, pub_admin, draft = self._make_items()
        staff = UserFactory(is_staff=True)
        qs = ContentItem.objects.visible_to(staff)
        assert pub_public in qs
        assert pub_registered in qs
        assert pub_admin in qs
        assert draft in qs


@pytest.mark.django_db
class TestContentRelation:
    def test_no_self_relation(self):
        item = ContentItemFactory()
        with pytest.raises(IntegrityError):
            ContentRelation.objects.create(
                from_item=item,
                to_item=item,
                rel_type="related_to",
            )

    def test_create_relation(self):
        item_a = ContentItemFactory()
        item_b = ContentItemFactory()
        rel = ContentRelation.objects.create(
            from_item=item_a,
            to_item=item_b,
            rel_type="reads",
        )
        assert rel.pk is not None
        assert item_a.relations_from.count() == 1
        assert item_b.relations_to.count() == 1
