from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    AdminUserSerializer, LoginSerializer, RegisterSerializer, StaffAccessSerializer,
    StudentUserSerializer,
)


def auth_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "user": StudentUserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(auth_response(serializer.validated_data["user"]))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(StudentUserSerializer(request.user).data)


class AdminUsersPagination(PageNumberPagination):
    page_size = 20


class AdminUsersView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    pagination_class = AdminUsersPagination

    def get_queryset(self):
        role = self.request.query_params.get("role", "all")
        if role not in {"all", "student", "staff", "superuser"}:
            raise ValidationError({"role": ["Invalid role."]})

        users = User.objects.all()
        if role == "student":
            users = users.filter(is_staff=False)
        elif role == "staff":
            users = users.filter(is_staff=True, is_superuser=False)
        elif role == "superuser":
            users = users.filter(is_superuser=True)

        search = self.request.query_params.get("search", "").strip()
        if search:
            users = users.filter(
                Q(student_no__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return users.order_by("pk")


class AdminUserAccessView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        serializer = StaffAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = get_object_or_404(User.objects.select_for_update(), pk=pk)
            if user.is_superuser:
                raise PermissionDenied("Superuser access cannot be modified from this endpoint.")
            new_staff = serializer.validated_data["is_staff"]
            if user.pk == request.user.pk and not new_staff:
                raise PermissionDenied("You cannot revoke your own admin access.")
            if user.is_staff != new_staff:
                user.is_staff = new_staff
                user.save(update_fields=["is_staff"])
            return Response(AdminUserSerializer(user).data)
