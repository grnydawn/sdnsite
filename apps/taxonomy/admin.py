from django.contrib import admin

from .models import ContentTag, Tag


class ContentTagInline(admin.TabularInline):
    model = ContentTag
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "category", "parent"]
    list_filter = ["category"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
