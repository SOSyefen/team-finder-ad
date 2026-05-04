"""Константы приложения projects."""

# Значения статусов проекта.
STATUS_OPEN = "open"
STATUS_CLOSED = "closed"

STATUS_CHOICES = (
    (STATUS_OPEN, "Открыт"),
    (STATUS_CLOSED, "Закрыт"),
)

# max_length для status — считаем «на лету» по самому длинному ключу.
STATUS_MAX_LENGTH = max(len(value) for value, _ in STATUS_CHOICES)

# Длины полей модели Project.
NAME_MAX_LENGTH = 200

# Пагинация.
PROJECTS_PAGE_SIZE = 12
