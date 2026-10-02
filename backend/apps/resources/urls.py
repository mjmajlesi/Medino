from django.urls import path

from .views import ResourceFileView, SiteStatsView


urlpatterns = [
    path("stats/", SiteStatsView.as_view(), name="site-stats"),
    path("resources/<int:pk>/file/", ResourceFileView.as_view(), name="resource-file"),
]
