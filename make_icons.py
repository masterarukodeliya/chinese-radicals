#!/usr/bin/env python3
# Иконки приложения: иероглиф 字 на красном градиенте (Pillow + Noto Sans SC).
from PIL import Image, ImageDraw, ImageFont

FONT = "/tmp/cjk.ttf"
GLYPH = "字"
TOP = (0xEC, 0x5C, 0x46)
BOT = (0xCE, 0x39, 0x28)
INK = (255, 255, 255)
SS = 4  # сглаживание через супердискретизацию

def render(size):
    S = size * SS
    img = Image.new("RGB", (S, S))
    # вертикальный градиент
    px = img.load()
    for y in range(S):
        v = y / (S - 1)
        c = (int(TOP[0]+(BOT[0]-TOP[0])*v),
             int(TOP[1]+(BOT[1]-TOP[1])*v),
             int(TOP[2]+(BOT[2]-TOP[2])*v))
        for x in range(S):
            px[x, y] = c
    draw = ImageDraw.Draw(img)
    # подобрать кегль, чтобы глиф занимал ~68% высоты
    target = S * 0.68
    fs = int(target)
    font = ImageFont.truetype(FONT, fs)
    try: font.set_variation_by_axes([700])  # жирное начертание, если есть ось
    except Exception: pass
    bb = draw.textbbox((0, 0), GLYPH, font=font)
    gh = bb[3] - bb[1]
    fs = int(fs * target / gh)
    font = ImageFont.truetype(FONT, fs)
    try: font.set_variation_by_axes([700])
    except Exception: pass
    bb = draw.textbbox((0, 0), GLYPH, font=font)
    cx = S/2 - (bb[0] + bb[2]) / 2
    cy = S/2 - (bb[1] + bb[3]) / 2
    draw.text((cx, cy), GLYPH, font=font, fill=INK)
    return img.resize((size, size), Image.LANCZOS)

for name, size in [("icon-512.png",512), ("icon-192.png",192), ("apple-touch-icon.png",180), ("favicon-32.png",32)]:
    render(size).save(name)
    print("ок:", name, size)
