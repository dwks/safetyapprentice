#!/usr/bin/env python3
"""Regenerate the raster favicons from the shield mark. One-off, not part of
the build — the outputs in static/ are committed.

    .venv/bin/pip install Pillow
    .venv/bin/python tools/make_icons.py

Keep the geometry in sync with static/favicon.svg, which is the SVG original
and the one modern browsers actually use.
"""
from PIL import Image, ImageDraw

TILE_FROM, TILE_TO = (0xB8, 0x5C, 0x38), (0xC2, 0x79, 0x3D)   # terracotta gradient
SHIELD = (0xFF, 0xFF, 0xFF, 255)                              # white
SHIELD_DARK = (0xEB, 0xDD, 0xCC, 255)                         # right half


def draw(size: int) -> Image.Image:
    S = size * 8                                  # supersample, downscale at the end
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    grad = Image.new('RGB', (S, S))
    gd = ImageDraw.Draw(grad)
    for i in range(2 * S):                        # 135deg sweep
        t = i / (2 * S - 1)
        gd.line([(i, 0), (0, i)],
                fill=tuple(round(TILE_FROM[c] + (TILE_TO[c] - TILE_FROM[c]) * t)
                           for c in range(3)))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=S // 4, fill=255)
    img.paste(grad, (0, 0), mask)

    u = S / 32                                    # shield on the same 32-unit grid as the SVG
    pts = [(16, 6.2), (24.2, 9.2), (24.2, 16.1)]
    for x0, y0, cx, cy, x1, y1 in [(24.2, 16.1, 24.2, 23.5, 16, 26.3),
                                   (16, 26.3, 7.8, 23.5, 7.8, 16.1)]:
        for i in range(41):
            t = i / 40
            pts.append(((1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1,
                        (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1))
    pts.append((7.8, 9.2))
    d.polygon([(x * u, y * u) for x, y in pts], fill=SHIELD)

    # right half in a slightly darker flat tone: apex -> right edge -> point
    half = [(16, 6.2), (24.2, 9.2), (24.2, 16.1)]
    for i in range(41):
        t2 = i / 40
        half.append(((1-t2)**2 * 24.2 + 2*(1-t2)*t2 * 24.2 + t2**2 * 16,
                     (1-t2)**2 * 16.1 + 2*(1-t2)*t2 * 23.5 + t2**2 * 26.3))
    d.polygon([(x * u, y * u) for x, y in half], fill=SHIELD_DARK)

    return img.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    draw(32).save('static/favicon.png')
    draw(180).save('static/apple-touch-icon.png')
    draw(64).save('static/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    print('wrote static/favicon.png, static/apple-touch-icon.png, static/favicon.ico')
