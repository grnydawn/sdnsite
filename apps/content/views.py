from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import ContentItem, ContentTypeDef


def home_view(request):
    """Landing page with recent published content."""
    recent_items = ContentItem.objects.visible_to(request.user).select_related(
        "content_type"
    )[:10]
    content_types = ContentTypeDef.objects.filter(is_active=True)
    return render(
        request,
        "home.html",
        {"recent_items": recent_items, "content_types": content_types},
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
