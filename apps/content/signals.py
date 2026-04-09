from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import ContentItem


@receiver(pre_save, sender=ContentItem)
def increment_content_version(sender, instance, **kwargs):
    """Auto-increment content_version on every save of an existing item."""
    if instance.pk:
        try:
            old = ContentItem.objects.get(pk=instance.pk)
            instance.content_version = old.content_version + 1
        except ContentItem.DoesNotExist:
            pass
