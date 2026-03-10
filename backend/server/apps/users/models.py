import textwrap
from typing import Any, ClassVar, Final, final, override

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserModelManager(_UserManager):

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "UserModel":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "UserModel":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

    def _create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "UserModel":
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


@final
class UserModel(AbstractUser):

    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
    )

    patronymic_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    is_stantion_admin = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD: ClassVar[str] = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects: UserModelManager = UserModelManager()