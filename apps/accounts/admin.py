from django.contrib import admin

from .models import AdminAuditLog, SavedItem, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "affiliation", "orcid"]
    search_fields = ["user__username", "affiliation", "orcid"]


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ["actor", "action", "target_type", "target_id", "created_at"]
    list_filter = ["action", "target_type"]
    readonly_fields = ["actor", "action", "target_type", "target_id", "detail", "created_at"]


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ["user", "content_item", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "content_item__title"]
    autocomplete_fields = ["user", "content_item"]
    readonly_fields = ["created_at"]
