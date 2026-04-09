from django.contrib import admin

from .models import DataSourceSync


@admin.register(DataSourceSync)
class DataSourceSyncAdmin(admin.ModelAdmin):
    list_display = [
        "content_item",
        "external_source_type",
        "sync_strategy",
        "sync_status",
        "last_sync_at",
        "created_at",
    ]
    list_filter = ["sync_strategy", "sync_status", "external_source_type"]
    search_fields = ["content_item__title", "external_source_type", "sync_url"]
    autocomplete_fields = ["content_item"]
    readonly_fields = ["created_at"]
    fieldsets = [
        (None, {"fields": ["content_item", "external_source_type", "sync_url"]}),
        ("Sync Configuration", {"fields": ["sync_strategy", "sync_status", "last_sync_at"]}),
        ("Raw Metadata", {"fields": ["raw_metadata_json"], "classes": ["collapse"]}),
        ("Meta", {"fields": ["created_at"]}),
    ]
