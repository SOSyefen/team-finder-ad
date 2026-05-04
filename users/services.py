"""Вспомогательные функции приложения users."""
from django.core.paginator import Page, Paginator

from .constants import USERS_PAGE_SIZE


def normalize_phone(value: str) -> str:
    """Приводит номер вида 8XXXXXXXXXX к формату +7XXXXXXXXXX."""
    if value and value.startswith("8") and len(value) == 11:
        return "+7" + value[1:]
    return value


def paginate(queryset, request, page_size: int = USERS_PAGE_SIZE) -> Page:
    """Возвращает объект Page для переданного queryset и GET-параметра page."""
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get("page"))
