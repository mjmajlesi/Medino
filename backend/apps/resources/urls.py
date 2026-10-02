from django.urls import path

from .views import (
    ModerateUploadView,
    MyUploadsView,
    PendingUploadsView,
    ResourceFileView,
    SiteStatsView,
    UploadView,
)


urlpatterns = [
    path("stats/", SiteStatsView.as_view(), name="site-stats"),
    path("resources/<int:pk>/file/", ResourceFileView.as_view(), name="resource-file"),
    path("uploads/", UploadView.as_view(), name="resource-upload"),
    path("uploads/mine/", MyUploadsView.as_view(), name="my-uploads"),
    path("admin/pending/", PendingUploadsView.as_view(), name="pending-uploads"),
    path("admin/approve/<int:pk>/", ModerateUploadView.as_view(), name="moderate-upload"),
]
