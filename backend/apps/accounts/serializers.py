from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import User


class StudentUserSerializer(serializers.ModelSerializer):
    entry_year = serializers.SerializerMethodField()
    current_term = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "student_no", "entry_year", "current_term", "is_staff")

    def get_entry_year(self, user):
        return str(user.entry_year) if user.entry_year is not None else ""

    def get_current_term(self, user):
        return str(user.current_term) if user.current_term is not None else ""


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "student_no",
            "entry_year",
            "current_term",
            "password",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "student_no": {"required": True, "allow_blank": False},
            "entry_year": {"required": True, "allow_null": False, "min_value": 1},
            "current_term": {"required": True, "allow_null": False, "min_value": 1},
        }

    def validate(self, attrs):
        user = User(
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
            student_no=attrs["student_no"],
        )
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data,
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )


class LoginSerializer(serializers.Serializer):
    student_no = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            student_no=attrs["student_no"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid student number or password."}
            )
        attrs["user"] = user
        return attrs
