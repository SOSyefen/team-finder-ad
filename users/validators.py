"""Валидаторы полей модели User."""
import re

from django.core.exceptions import ValidationError

from .constants import GITHUB_URL_REGEX, PHONE_REGEX


def validate_phone(value: str) -> None:
    """Проверяет, что телефон соответствует формату 8XXXXXXXXXX или +7XXXXXXXXXX."""
    if not re.fullmatch(PHONE_REGEX, value or ""):
        raise ValidationError(
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )


def validate_github_url(value: str) -> None:
    """Проверяет, что ссылка ведёт на github.com."""
    if not value:
        return
    if not re.match(GITHUB_URL_REGEX, value):
        raise ValidationError("Ссылка должна вести на github.com")
