import json

import jsonschema
from django import forms
from django.contrib import admin

from apps.content.models import (
    ContentItem,
    ContentRelation,
    ContentSourceLink,
    ContentTypeDef,
    RevisionLog,
    SourceReference,
)
from apps.taxonomy.models import ContentTag


@admin.register(ContentTypeDef)
class ContentTypeDefAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


class ContentSourceLinkInline(admin.TabularInline):
    model = ContentSourceLink
    extra = 1
    autocomplete_fields = ["source_ref"]


class ContentRelationFromInline(admin.TabularInline):
    model = ContentRelation
    fk_name = "from_item"
    extra = 1
    autocomplete_fields = ["to_item"]
    verbose_name = "Outgoing relation"
    verbose_name_plural = "Outgoing relations"


class ContentTagInline(admin.TabularInline):
    model = ContentTag
    extra = 1
    autocomplete_fields = ["tag"]


class ContentItemAdminForm(forms.ModelForm):
    """Custom form for ContentItem admin: pretty-prints JSON and validates extra_data against schema."""

    class Meta:
        model = ContentItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            for field_name in ("extra_data", "reproducibility"):
                value = getattr(self.instance, field_name, None)
                if value:
                    self.initial[field_name] = json.dumps(value, indent=2)

    def clean(self):
        cleaned = super().clean()
        extra_data = cleaned.get("extra_data")
        content_type = cleaned.get("content_type")
        if content_type and content_type.extra_schema and extra_data:
            try:
                jsonschema.validate(instance=extra_data, schema=content_type.extra_schema)
            except jsonschema.ValidationError as e:
                raise forms.ValidationError(
                    {"extra_data": f"Does not match {content_type.name} schema: {e.message}"}
                )
        return cleaned


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    form = ContentItemAdminForm
    list_display = ["title", "content_type", "status", "visibility", "updated_at"]
    list_filter = ["content_type", "status", "visibility"]
    list_select_related = ["content_type"]
    search_fields = ["title", "slug", "summary"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["content_version", "created_at", "updated_at"]
    inlines = [ContentTagInline, ContentSourceLinkInline, ContentRelationFromInline]
    fieldsets = [
        (None, {"fields": ["content_type", "title", "slug", "summary", "body_md"]}),
        ("Type-specific data", {"fields": ["extra_data", "schema_version"], "classes": ["collapse"]}),
        ("Status", {"fields": ["status", "visibility"]}),
        ("Reproducibility", {"fields": ["reproducibility"], "classes": ["collapse"]}),
        ("Authorship", {"fields": ["created_by", "updated_by", "reviewed_by", "reviewed_at", "published_at"]}),
        ("Meta", {"fields": ["content_version", "created_at", "updated_at"]}),
    ]


@admin.register(SourceReference)
class SourceReferenceAdmin(admin.ModelAdmin):
    list_display = ["title", "source_type", "identifier_type", "identifier_value"]
    list_filter = ["source_type", "identifier_type"]
    search_fields = ["title", "identifier_value", "citation_text"]


@admin.register(ContentRelation)
class ContentRelationAdmin(admin.ModelAdmin):
    list_display = ["from_item", "rel_type", "to_item"]
    list_filter = ["rel_type"]
    autocomplete_fields = ["from_item", "to_item"]


@admin.register(RevisionLog)
class RevisionLogAdmin(admin.ModelAdmin):
    list_display = ["content_item", "version_number", "changed_by", "changed_at"]
    list_filter = ["changed_at"]
    readonly_fields = ["content_item", "version_number", "snapshot", "changed_by", "changed_at"]
