"""Авто-генерация аватарки для пользователей без загруженной картинки."""
import io
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_ANCHOR,
    AVATAR_FALLBACK_LETTER,
    AVATAR_FONT_NAME,
    AVATAR_FONT_RATIO,
    AVATAR_PALETTE,
    AVATAR_SIZE,
    AVATAR_TEXT_FILL,
)


def generate_avatar(letter: str, size: int = AVATAR_SIZE) -> ContentFile:
    """Возвращает PNG-аватарку: первая буква на однотонном цветном фоне."""
    bg_color = random.choice(AVATAR_PALETTE)
    img = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    text = (letter or AVATAR_FALLBACK_LETTER)[0].upper()
    try:
        font = ImageFont.truetype(
            AVATAR_FONT_NAME, size=int(size * AVATAR_FONT_RATIO)
        )
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox(AVATAR_ANCHOR, text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]
    draw.text((x, y), text, fill=AVATAR_TEXT_FILL, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.getvalue())
