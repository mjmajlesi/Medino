from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, student_no, password=None, **extra_fields):
        if not student_no or not student_no.strip():
            raise ValueError("A student number is required.")
        user = self.model(student_no=student_no.strip(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_no, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True.")
        return self.create_user(student_no, password, **extra_fields)


class User(AbstractUser):
    username = None
    student_no = models.CharField(max_length=20, unique=True)
    entry_year = models.PositiveIntegerField(null=True, blank=True)
    current_term = models.PositiveSmallIntegerField(null=True, blank=True)

    USERNAME_FIELD = "student_no"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.student_no
