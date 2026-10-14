from django.urls import path

from .views import AdminUserAccessView, AdminUsersView


urlpatterns = [
    path("users/", AdminUsersView.as_view(), name="admin-users"),
    path("users/<int:pk>/access/", AdminUserAccessView.as_view(), name="admin-user-access"),
]
