from django.db import transaction
from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.views import APIView

from apps.academics.models import Lesson

from .models import Resource
from .serializers import ModerationActionSerializer, ResourceSerializer, ResourceUploadSerializer


class SiteStatsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        counts = dict(
            Resource.objects.filter(status=Resource.Status.APPROVED)
            .values("type")
            .annotate(total=Count("id"))
            .values_list("type", "total")
        )
        return Response(
            {
                "lessons": Lesson.objects.count(),
                "notes": counts.get(Resource.Type.NOTE, 0),
                "videos": counts.get(Resource.Type.VIDEO, 0),
                "samples": counts.get(Resource.Type.SAMPLE, 0),
                "summaries": counts.get(Resource.Type.SUMMARY, 0),
            }
        )


class ResourceFileView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, pk):
        resource = get_object_or_404(Resource.objects.exclude(file=""), pk=pk)
        if resource.status != Resource.Status.APPROVED:
            # Authenticate only private files, so a stale token cannot block public files.
            try:
                authenticated = JWTAuthentication().authenticate(request)
            except (AuthenticationFailed, InvalidToken) as exc:
                raise Http404 from exc
            user = authenticated[0] if authenticated else None
            if not user or not (user.is_staff or resource.uploaded_by_id == user.pk):
                raise Http404
        return FileResponse(resource.file.open("rb"))


class UploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResourceUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        review = {"reviewed_by": user, "reviewed_at": timezone.now()} if user.is_staff else {}
        resource = serializer.save(
            uploaded_by=user,
            status=Resource.Status.APPROVED if user.is_staff else Resource.Status.PENDING,
            **review,
        )
        return Response({"id": str(resource.pk), "status": resource.status}, status=201)


class MyUploadsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resources = (
            Resource.objects.filter(uploaded_by=request.user)
            .select_related("uploaded_by")
            .order_by("-created_at", "-pk")
        )
        return Response(ResourceSerializer(resources, many=True, context={"request": request}).data)


class PendingUploadsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        resources = (
            Resource.objects.filter(status=Resource.Status.PENDING)
            .select_related("uploaded_by")
            .order_by("-created_at", "-pk")
        )
        return Response(ResourceSerializer(resources, many=True, context={"request": request}).data)


class ModerateUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        serializer = ModerationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]
        status = Resource.Status.APPROVED if action == "approve" else Resource.Status.REJECTED
        reviewed_at = timezone.now()
        with transaction.atomic():
            resource = get_object_or_404(Resource.objects.select_for_update(), pk=pk)
            if resource.status != Resource.Status.PENDING:
                raise ValidationError({"status": "Only pending resources may be reviewed."})
            # The conditional update also guards the transition on databases without row locks.
            updated = Resource.objects.filter(pk=pk, status=Resource.Status.PENDING).update(
                status=status,
                reviewed_by=request.user,
                reviewed_at=reviewed_at,
                updated_at=reviewed_at,
            )
            if not updated:
                raise ValidationError({"status": "Only pending resources may be reviewed."})
        return Response({"id": str(pk), "status": status})
