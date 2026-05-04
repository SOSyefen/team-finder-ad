"""Константы приложения users."""
from enum import StrEnum

# Длины полей модели User.
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256

# Пагинация.
USERS_PAGE_SIZE = 12

# Параметры генерации аватара.
AVATAR_SIZE = 256
AVATAR_FONT_RATIO = 0.55
AVATAR_TEXT_FILL = "white"
AVATAR_FALLBACK_LETTER = "?"
AVATAR_ANCHOR = (0, 0)
AVATAR_FONT_NAME = "arial.ttf"


class AvatarPalette(StrEnum):
    """Палитра цветов фона для авто-генерируемых аватаров."""

    BLUE = "#5B8DEF"
    PURPLE = "#7C5CFF"
    GREEN = "#3DBE8B"
    ORANGE = "#E0935A"
    PINK = "#D8627E"
    TEAL = "#4FA3A3"
    GREY_BLUE = "#7E8AA1"
    LILAC = "#B07AB0"
    OLIVE = "#5C8C57"
    TERRACOTTA = "#C97B4A"


# Готовый список цветов для random.choice.
AVATAR_PALETTE = [color.value for color in AvatarPalette]

# Регулярки для валидаторов.
PHONE_REGEX = r"(\+7|8)\d{10}"
GITHUB_URL_REGEX = r"^https?://(www\.)?github\.com/.+"
