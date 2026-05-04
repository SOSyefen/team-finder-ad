import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .avatar import generate_avatar
from .constants import (
    ABOUT_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
)
from .managers import UserManager
from .services import normalize_phone
from .validators import validate_github_url, validate_phone


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "Email", unique=True, max_length=EMAIL_MAX_LENGTH
    )
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        validators=[validate_phone],
        blank=True,
        null=True,
    )
    github_url = models.URLField(
        "GitHub", blank=True, default="", validators=[validate_github_url]
    )
    about = models.TextField(
        "О себе", max_length=ABOUT_MAX_LENGTH, blank=True, default=""
    )
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
        ordering = ["-date_joined"]

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
