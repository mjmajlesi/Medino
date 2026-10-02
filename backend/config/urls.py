from django.contrib import admin
from django.urls import include, path

from .views import health


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="api-health"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.academics.urls")),
]
