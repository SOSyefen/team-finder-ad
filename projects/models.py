from django.conf import settings
from django.db import models
from django.urls import reverse

from users.validators import validate_github_url

from .constants import (
    NAME_MAX_LENGTH,
    STATUS_CHOICES,
    STATUS_MAX_LENGTH,
    STATUS_OPEN,
)


class Project(models.Model):
    name = models.CharField("Название", max_length=NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    github_url = models.URLField(
        "GitHub", blank=True, default="", validators=[validate_github_url]
    )
    status = models.CharField(
        "Статус",
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        """Канонический URL для отображения проекта на сайте.

        Используется в админке (ссылка «посмотреть на сайте»).
        """
        return reverse("projects:detail", args=[self.pk])
