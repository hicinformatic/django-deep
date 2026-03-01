"""URL configuration for django-deep tests."""

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
]

admin.site.site_header = "Django Deep - Administration"
admin.site.site_title = "Django Deep Admin"
admin.site.index_title = "Welcome to Django Deep"
