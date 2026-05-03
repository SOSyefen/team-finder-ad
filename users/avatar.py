import io
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

PALETTE = [
    "#5B8DEF", "#7C5CFF", "#3DBE8B", "#E0935A",
    "#D8627E", "#4FA3A3", "#7E8AA1", "#B07AB0",
    "#5C8C57", "#C97B4A",
]


def generate_avatar(letter: str, size: int = 256) -> ContentFile:
    bg_color = random.choice(PALETTE)
    img = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    text = (letter or "?")[0].upper()
    try:
        font = ImageFont.truetype("arial.ttf", size=int(size * 0.55))
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]
    draw.text((x, y), text, fill="white", font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.getvalue())
