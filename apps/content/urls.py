from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.ContentBrowseView.as_view(), name="browse"),
    path("<slug:slug>/", views.ContentDetailView.as_view(), name="detail"),
]
