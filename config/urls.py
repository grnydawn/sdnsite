from django.contrib import admin
from django.urls import include, path

from apps.content.views import home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("browse/", include("apps.content.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("markdownx/", include("markdownx.urls")),
]
