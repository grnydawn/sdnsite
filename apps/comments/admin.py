from django.contrib import admin

from .models import ContentComment


@admin.action(description="Mark selected comments as visible")
def approve_comments(modeladmin, request, queryset):
    queryset.update(status=ContentComment.Status.VISIBLE)


@admin.action(description="Flag selected comments for review")
def flag_comments(modeladmin, request, queryset):
    queryset.update(status=ContentComment.Status.FLAGGED)


@admin.action(description="Hide selected comments")
def hide_comments(modeladmin, request, queryset):
    queryset.update(status=ContentComment.Status.HIDDEN)


@admin.register(ContentComment)
class ContentCommentAdmin(admin.ModelAdmin):
    list_display = ["content_item", "user", "comment_type", "status", "created_at"]
    list_filter = ["status", "comment_type"]
    search_fields = ["body", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["content_item", "user"]
    actions = [approve_comments, flag_comments, hide_comments]
    fieldsets = [
        (None, {"fields": ["content_item", "parent", "user", "body"]}),
        ("Classification", {"fields": ["comment_type", "status", "section_anchor"]}),
        ("Meta", {"fields": ["created_at", "updated_at"]}),
    ]
