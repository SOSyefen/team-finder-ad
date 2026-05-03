import re
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from .avatar import generate_avatar
from .managers import UserManager


def normalize_phone(value: str) -> str:
    if value and value.startswith("8") and len(value) == 11:
        return "+7" + value[1:]
    return value


def validate_phone(value: str) -> None:
    if not re.fullmatch(r"(\+7|8)\d{10}", value or ""):
        raise ValidationError(
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )


def validate_github_url(value: str) -> None:
    if not value:
        return
    pattern = r"^https?://(www\.)?github\.com/.+"
    if not re.match(pattern, value):
        raise ValidationError("Ссылка должна вести на github.com")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField(
        "Телефон",
        max_length=12,
        unique=True,
        validators=[validate_phone],
        blank=True,
        null=True,
    )
    github_url = models.URLField(
        "GitHub", blank=True, default="", validators=[validate_github_url]
    )
    about = models.TextField("О себе", max_length=256, blank=True, default="")
    is_active = models.BooleanField("Активный", default=True)
    is_staff = models.BooleanField("Администратор", default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)
        if not self.avatar:
            filename = f"{uuid.uuid4().hex}.png"
            content = generate_avatar(self.name or self.email)
            self.avatar.save(filename, content, save=False)
        super().save(*args, **kwargs)
