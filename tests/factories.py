import factory
from django.contrib.auth.models import User

from apps.comments.models import ContentComment
from apps.content.models import ContentItem, ContentRelation, ContentTypeDef, SourceReference
from apps.taxonomy.models import Tag


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


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    slug = factory.Sequence(lambda n: f"tag-{n}")
    name = factory.Sequence(lambda n: f"Tag {n}")
    category = "domain"


class SourceReferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SourceReference

    title = factory.Sequence(lambda n: f"Source {n}")
    url = factory.Sequence(lambda n: f"https://example.com/source/{n}")
    source_type = "official_docs"
    identifier_type = "URL"


class ContentCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentComment

    content_item = factory.SubFactory(ContentItemFactory)
    user = factory.SubFactory(UserFactory)
    body = "A test comment."
    comment_type = "general"
    status = "visible"


class ContentRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentRelation

    from_item = factory.SubFactory(ContentItemFactory)
    to_item = factory.SubFactory(ContentItemFactory)
    rel_type = "related_to"
