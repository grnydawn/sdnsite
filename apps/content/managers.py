from django.db import models


class ContentItemManager(models.Manager):
    """Custom manager with queryset-level access control."""

    def visible_to(self, user):
        """Return items visible to the given user.

        - Staff: everything
        - Authenticated: published + public/registered
        - Anonymous: published + public only
        """
        if user.is_staff:
            return self.all()

        # Import here to avoid circular import (ContentItem imports this manager)
        from apps.content.models.content_item import ContentItem

        if user.is_authenticated:
            return self.filter(
                status=ContentItem.Status.PUBLISHED,
                visibility__in=[ContentItem.Visibility.PUBLIC, ContentItem.Visibility.REGISTERED],
            )
        return self.filter(
            status=ContentItem.Status.PUBLISHED,
            visibility=ContentItem.Visibility.PUBLIC,
        )
