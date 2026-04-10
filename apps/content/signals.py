import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import ContentItem
from .models.revision_log import RevisionLog


@receiver(pre_save, sender=ContentItem)
def capture_pre_save_snapshot(sender, instance, **kwargs):
    """Capture a snapshot of the existing field values before save."""
    if not instance.pk:
        return
    try:
        old = ContentItem.objects.get(pk=instance.pk)
    except ContentItem.DoesNotExist:
        return

    snapshot = {}
    for field in old._meta.fields:
        if field.name == "search_vector":
            continue
        # Use attname for FK fields (e.g. content_type_id instead of content_type)
        snapshot[field.attname] = getattr(old, field.attname)

    # Convert to JSON-safe values (handles datetimes, UUIDs, etc.)
    snapshot = json.loads(json.dumps(snapshot, cls=DjangoJSONEncoder))

    instance._pre_save_snapshot = snapshot
    instance._pre_save_version = old.content_version


@receiver(post_save, sender=ContentItem)
def create_revision_and_increment_version(sender, instance, created, **kwargs):
    """Atomically increment content_version and create a RevisionLog entry."""
    if created:
        return

    snapshot = getattr(instance, "_pre_save_snapshot", None)
    old_version = getattr(instance, "_pre_save_version", None)

    if snapshot is None or old_version is None:
        return

    # Atomic increment using F() expression -- no race condition
    ContentItem.objects.filter(pk=instance.pk).update(
        content_version=F("content_version") + 1
    )
    instance.refresh_from_db(fields=["content_version"])

    RevisionLog.objects.create(
        content_item=instance,
        version_number=instance.content_version,
        snapshot=snapshot,
        changed_by=None,
    )

    # Clean up transient attrs
    del instance._pre_save_snapshot
    del instance._pre_save_version
