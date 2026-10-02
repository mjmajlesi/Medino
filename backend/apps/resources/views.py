from django.db.models import Count
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.academics.models import Lesson

from .models import Resource


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
        resource = get_object_or_404(
            Resource.objects.filter(status=Resource.Status.APPROVED)
            .exclude(file=""),
            pk=pk,
        )
        return FileResponse(resource.file.open("rb"))
