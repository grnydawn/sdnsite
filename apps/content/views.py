from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from apps.taxonomy.models import Tag

from .models import ContentItem, ContentTypeDef


def home_view(request):
    """Landing page with content type cards and recent published content."""
    content_types = ContentTypeDef.objects.filter(is_active=True).annotate(
        item_count=Count(
            "items",
            filter=Q(items__status="published", items__visibility="public"),
        )
    )
    recent_items = ContentItem.objects.visible_to(request.user).select_related(
        "content_type"
    )[:10]

    # Tag categories for sidebar (D-03)
    tag_categories = {}
    for tag in Tag.objects.filter(parent=None).order_by("category", "name"):
        tag_categories.setdefault(tag.category, []).append(tag)

    return render(
        request,
        "home.html",
        {
            "content_types": content_types,
            "recent_items": recent_items,
            "tag_categories": tag_categories,
        },
    )


class ContentBrowseView(ListView):
    model = ContentItem
    template_name = "content/browse.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        qs = ContentItem.objects.visible_to(self.request.user).select_related(
            "content_type"
        )
        content_type_slug = self.request.GET.get("type")
        if content_type_slug:
            qs = qs.filter(content_type__slug=content_type_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_types"] = ContentTypeDef.objects.filter(is_active=True)
        context["current_type"] = self.request.GET.get("type", "")
        return context


class ContentDetailView(DetailView):
    model = ContentItem
    context_object_name = "item"

    def get_queryset(self):
        return ContentItem.objects.visible_to(self.request.user)

    def get_template_names(self):
        return [
            f"content/{self.object.content_type.slug}_detail.html",
            "content/detail_base.html",
        ]
