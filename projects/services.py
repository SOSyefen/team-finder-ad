"""Вспомогательные функции приложения projects."""
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet

from .constants import PROJECTS_PAGE_SIZE
from .models import Project


def with_owner_and_participants(queryset: QuerySet) -> QuerySet:
    """Подтягивает связанные данные одним запросом, чтобы избежать N+1.

    Карточка проекта в шаблоне читает автора (owner) и количество
    участников, поэтому select_related/prefetch_related обязательны.
    """
    return queryset.select_related("owner").prefetch_related("participants")


def project_queryset() -> QuerySet:
    """Базовый queryset для всех страниц со списком проектов."""
    return with_owner_and_participants(Project.objects.all())


def paginate(queryset, request, page_size: int = PROJECTS_PAGE_SIZE) -> Page:
    """Возвращает объект Page для переданного queryset и GET-параметра page."""
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get("page"))
