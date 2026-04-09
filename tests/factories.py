import factory
from django.contrib.auth.models import User

from apps.content.models import ContentItem, ContentTypeDef


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class ContentTypeDefFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentTypeDef

    slug = factory.Sequence(lambda n: f"type-{n}")
    name = factory.Sequence(lambda n: f"Type {n}")
    description = "Test content type"
    template_name = "content/detail_base.html"
    sort_order = factory.Sequence(lambda n: n)


class ContentItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentItem

    content_type = factory.SubFactory(ContentTypeDefFactory)
    slug = factory.Sequence(lambda n: f"item-{n}")
    title = factory.Sequence(lambda n: f"Test Item {n}")
    summary = "A test content item"
    body_md = "# Test\n\nThis is test content."
    status = "published"
    visibility = "public"
