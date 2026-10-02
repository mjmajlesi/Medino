"""Validation shared by resource upload endpoints."""

from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django.conf import settings
from rest_framework import serializers

from .models import Resource


DOCUMENT_TYPES = {Resource.Type.NOTE, Resource.Type.SAMPLE, Resource.Type.SUMMARY}
ALLOWED_FILES = {
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".mp4": {"video/mp4"},
    ".webm": {"video/webm"},
}


def validate_resource_file(upload, resource_type):
    max_size = settings.MAX_UPLOAD_SIZE
    if upload.size > max_size:
        raise serializers.ValidationError(
            f"File exceeds the {max_size} byte upload limit."
        )

    extension = Path(upload.name).suffix.lower()
    allowed_extensions = (
        {".pdf", ".docx"} if resource_type in DOCUMENT_TYPES else {".mp4", ".webm"}
    )
    if extension not in allowed_extensions:
        raise serializers.ValidationError("File extension is not allowed for this resource type.")

    content_type = getattr(upload, "content_type", "")
    if content_type not in ALLOWED_FILES[extension] | {"application/octet-stream"}:
        raise serializers.ValidationError("File content type does not match its extension.")

    position = upload.tell()
    try:
        header = upload.read(12)
        if extension == ".pdf":
            valid = header.startswith(b"%PDF-")
        elif extension == ".docx":
            try:
                upload.seek(0)
                with ZipFile(upload) as archive:
                    valid = (
                        "[Content_Types].xml" in archive.namelist()
                        and "word/document.xml" in archive.namelist()
                    )
            except BadZipFile:
                valid = False
        elif extension == ".mp4":
            valid = header[4:8] == b"ftyp"
        else:
            valid = header.startswith(b"\x1a\x45\xdf\xa3")
    finally:
        upload.seek(position)

    if not valid:
        raise serializers.ValidationError("File content does not match its extension.")
