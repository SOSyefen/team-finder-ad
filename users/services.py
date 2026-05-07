"""Вспомогательные функции приложения users."""


def normalize_phone(value: str) -> str:
    """Приводит номер вида 8XXXXXXXXXX к формату +7XXXXXXXXXX."""
    if value and value.startswith("8") and len(value) == 11:
        return "+7" + value[1:]
    return value
