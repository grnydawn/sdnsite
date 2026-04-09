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
        if user.is_authenticated:
            return self.filter(
                status="published",
                visibility__in=["public", "registered"],
            )
        return self.filter(status="published", visibility="public")
