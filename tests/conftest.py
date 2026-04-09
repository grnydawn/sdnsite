import pytest

from tests.factories import ContentItemFactory, ContentTypeDefFactory, UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def staff_user():
    return UserFactory(is_staff=True)


@pytest.fixture
def content_type_def():
    return ContentTypeDefFactory()


@pytest.fixture
def content_item(content_type_def, user):
    return ContentItemFactory(content_type=content_type_def, created_by=user)
