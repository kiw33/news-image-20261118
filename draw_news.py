#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news front page (1024x1024 PNG).

Flat vector-style newspaper page: one headline banner, six illustrated
story panels and an "also today" ticker. Pure Pillow, no network, no
external assets, so the output is byte-deterministic.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (16, 35, 63)
PAPER = (244, 241, 234)
GOLD = (232, 163, 61)
WHITE = (255, 255, 255)
INK = (20, 20, 20)
GREY = (90, 90, 90)

STORIES = [
    dict(kicker="THE GULF", color=(192, 57, 43),
         head="US strikes Iran island; Iran hits Kuwait & Bahrain",
         sub="US jets hit Qeshm; Iran drones hit US bases",
         tag="QESHM \u2022 BAHRAIN \u2022 KUWAIT", icon="burst"),
    dict(kicker="UKRAINE", color=(46, 111, 183),
         head="Ukraine hits Crimea bridge \u2014 span collapses",
         sub="Second day of strikes; span falls into strait",
         tag="KERCH STRAIT, CRIMEA", icon="bridge"),
    dict(kicker="APEC \u00b7 SHENZHEN", color=(176, 120, 31),
         head="Xi, Putin open APEC; Trump summit next",
         sub="Leaders denounce protectionism and sanctions",
         tag="SHENZHEN, CHINA", icon="flags"),
    dict(kicker="USA \u00b7 SENATE", color=(31, 95, 168),
         head="Peltola wins Alaska; Democrats take 56\u201344",
         sub="Biggest Senate majority since 2009",
         tag="ALASKA \u2022 MIDTERMS 2026", icon="ballot"),
    dict(kicker="HEALTH", color=(169, 50, 38),
         head="Ebola surges; US measles-free era ends",
         sub="11,000+ cases in Congo; 5,412 US cases",
         tag="2ND-LARGEST EBOLA OUTBREAK", icon="virus"),
    dict(kicker="SPACE", color=(74, 59, 140),
         head="Voyager 1 reaches one light-day from Earth",
         sub="16 billion miles, farthest object ever",
         tag="NASA \u2022 16 BILLION MILES", icon="voyager"),
]

TICKER = [
    "Russian plane crash in Siberia, 19 dead \u2022 Cyclone Xavier, Cat 5, hits Cook Islands \u2022 Nvidia record earnings",
    "Kahana elected Knesset speaker \u2022 Quakes: PNG 6.0, Romania 5.3 \u2022 Word of the Year: \u201cHuman\u201d",
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def starburst(d, cx, cy, r1, r2, n, fill):
    pts = []
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def draw_icon(d, kind, x, y, s):
    """Flat pictogram inside a s x s box at (x, y)."""
    if kind == "burst":
        starburst(d, x + s * 0.5, y + s * 0.52, s * 0.48, s * 0.2, 10,
                  (245, 176, 65))
        starburst(d, x + s * 0.5, y + s * 0.52, s * 0.3, s * 0.13, 8,
                  (220, 80, 40))
        d.ellipse([x + s * 0.38, y + s * 0.4, x + s * 0.62, y + s * 0.64],
                  fill=(120, 20, 20))
    elif kind == "bridge":
        # Broken bridge: two deck ends, a fallen span, water below.
        d.rectangle([x + 4, y + s * 0.3, x + s * 0.4, y + s * 0.4],
                    fill=(70, 90, 120))
        d.rectangle([x + s * 0.6, y + s * 0.3, x + s - 4, y + s * 0.4],
                    fill=(70, 90, 120))
        d.polygon([(x + s * 0.42, y + s * 0.52), (x + s * 0.6, y + s * 0.46),
                   (x + s * 0.58, y + s * 0.56), (x + s * 0.4, y + s * 0.62)],
                  fill=(192, 57, 43))
        d.line([x + s * 0.2, y + s * 0.3, x + s * 0.2, y + s * 0.08],
               fill=(46, 111, 183), width=4)
        d.line([x + s * 0.8, y + s * 0.3, x + s * 0.8, y + s * 0.08],
               fill=(46, 111, 183), width=4)
        d.line([x + s * 0.2, y + s * 0.08, x + s * 0.4, y + s * 0.3],
               fill=(46, 111, 183), width=3)
        d.line([x + s * 0.8, y + s * 0.08, x + s * 0.6, y + s * 0.3],
               fill=(46, 111, 183), width=3)
        for yy in (0.78, 0.88):
            d.arc([x + 4, y + s * yy, x + s - 4, y + s * (yy + 0.12)],
                  0, 180, fill=(46, 111, 183), width=4)
    elif kind == "flags":
        # China, USA, Russia as three small simplified flags.
        d.rectangle([x + 2, y + 8, x + s * 0.32, y + s * 0.55],
                    fill=(222, 41, 16))
        starburst(d, x + s * 0.13, y + s * 0.22, 9, 4, 5, (255, 222, 0))
        d.rectangle([x + s * 0.36, y + 8, x + s * 0.66, y + s * 0.55],
                    fill=(255, 255, 255), outline=(180, 180, 180))
        for i in range(4):
            d.rectangle([x + s * 0.36, y + 8 + i * 11,
                         x + s * 0.66, y + 8 + i * 11 + 5],
                        fill=(178, 34, 52))
        d.rectangle([x + s * 0.36, y + 8, x + s * 0.5, y + s * 0.3],
                    fill=(60, 59, 110))
        d.rectangle([x + s * 0.7, y + 8, x + s - 2, y + s * 0.55],
                    fill=(255, 255, 255), outline=(180, 180, 180))
        d.rectangle([x + s * 0.7, y + 8, x + s - 2, y + s * 0.23],
                    fill=(255, 255, 255))
        d.rectangle([x + s * 0.7, y + s * 0.23, x + s - 2, y + s * 0.4],
                    fill=(0, 57, 166))
        d.rectangle([x + s * 0.7, y + s * 0.4, x + s - 2, y + s * 0.55],
                    fill=(213, 0, 50))
        d.line([x + s * 0.17, y + s * 0.55, x + s * 0.17, y + s * 0.92],
               fill=(120, 120, 120), width=3)
        d.line([x + s * 0.51, y + s * 0.55, x + s * 0.51, y + s * 0.92],
               fill=(120, 120, 120), width=3)
        d.line([x + s * 0.85, y + s * 0.55, x + s * 0.85, y + s * 0.92],
               fill=(120, 120, 120), width=3)
    elif kind == "ballot":
        d.rectangle([x + s * 0.18, y + s * 0.4, x + s * 0.82, y + s * 0.92],
                    fill=(31, 95, 168))
        d.rectangle([x + s * 0.3, y + s * 0.3, x + s * 0.7, y + s * 0.42],
                    fill=(20, 60, 110))
        d.line([x + s * 0.3, y + s * 0.62, x + s * 0.46, y + s * 0.78],
               fill=(255, 255, 255), width=7)
        d.line([x + s * 0.46, y + s * 0.78, x + s * 0.74, y + s * 0.48],
               fill=(255, 255, 255), width=7)
    elif kind == "virus":
        cx, cy = x + s * 0.5, y + s * 0.52
        for i in range(10):
            a = 2 * math.pi * i / 10
            d.line([cx + 30 * math.cos(a), cy + 30 * math.sin(a),
                    cx + 46 * math.cos(a), cy + 46 * math.sin(a)],
                   fill=(169, 50, 38), width=6)
            d.ellipse([cx + 46 * math.cos(a) - 6, cy + 46 * math.sin(a) - 6,
                       cx + 46 * math.cos(a) + 6, cy + 46 * math.sin(a) + 6],
                      fill=(169, 50, 38))
        d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(192, 57, 43))
        d.ellipse([cx - 16, cy - 20, cx - 2, cy - 6], fill=(255, 255, 255))
        d.ellipse([cx + 6, cy + 6, cx + 18, cy + 18], fill=(255, 255, 255))
    elif kind == "voyager":
        for sx, sy in [(0.12, 0.15), (0.85, 0.1), (0.7, 0.3), (0.2, 0.75),
                       (0.9, 0.7)]:
            d.ellipse([x + s * sx - 3, y + s * sy - 3,
                       x + s * sx + 3, y + s * sy + 3], fill=(255, 255, 255))
        d.line([x + s * 0.5, y + s * 0.12, x + s * 0.5, y + s * 0.34],
               fill=(232, 163, 61), width=4)
        d.ellipse([x + s * 0.42, y + s * 0.06, x + s * 0.58, y + s * 0.2],
                  fill=(232, 163, 61))
        d.polygon([(x + s * 0.3, y + s * 0.5), (x + s * 0.7, y + s * 0.5),
                   (x + s * 0.58, y + s * 0.72), (x + s * 0.42, y + s * 0.72)],
                  fill=(200, 200, 210))
        d.pieslice([x + s * 0.14, y + s * 0.55, x + s * 0.86, y + s * 0.95],
                   0, 180, fill=(232, 163, 61))


def build(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header ----
    d.rectangle([0, 0, W, 128], fill=NAVY)
    d.rectangle([0, 128, W, 134], fill=GOLD)
    d.text((24, 16), "THE WORLD IN ONE DAY",
           font=font(BOLD, 26), fill=GOLD)
    d.text((24, 50), "WEDNESDAY 18 NOVEMBER 2026",
           font=font(BOLD, 46), fill=WHITE)
    # small globe mark, top right
    gx, gy = 946, 32
    d.ellipse([gx, gy, gx + 56, gy + 56], outline=GOLD, width=4)
    d.ellipse([gx + 14, gy, gx + 42, gy + 56], outline=GOLD, width=3)
    d.line([gx, gy + 28, gx + 56, gy + 28], fill=GOLD, width=3)
    d.arc([gx + 5, gy + 11, gx + 51, gy + 45], 200, 340, fill=GOLD, width=3)

    # ---- six story panels, 2 x 3 ----
    px, py, pw, ph, gap = 16, 146, 490, 242, 12
    for i, st in enumerate(STORIES):
        x = px + (i % 2) * (pw + gap)
        y = py + (i // 2) * (ph + gap)
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=10, fill=WHITE)
        d.rounded_rectangle([x, y, x + pw, y + 8], radius=4,
                            fill=st["color"])
        d.rectangle([x, y + 4, x + pw, y + 8], fill=st["color"])
        # icon tile, top right
        ix, iy, isz = x + pw - 122, y + 22, 100
        d.rounded_rectangle([ix, iy, ix + isz, iy + isz], radius=8,
                            fill=(238, 238, 232))
        draw_icon(d, st["icon"], ix, iy, isz)
        # kicker + headline + sub
        tx = x + 18
        d.text((tx, y + 20), st["kicker"], font=font(BOLD, 20),
               fill=st["color"])
        head_lines = wrap(d, st["head"], font(BOLD, 28), 340)
        yy = y + 50
        for ln in head_lines[:3]:
            d.text((tx, yy), ln, font=font(BOLD, 28), fill=INK)
            yy += 34
        sub_lines = wrap(d, st["sub"], font(REG, 20), 452)
        yy = yy + 10
        for ln in sub_lines[:2]:
            d.text((tx, yy), ln, font=font(REG, 20), fill=GREY)
            yy += 25
        # fact chip along the panel's bottom edge
        chip_fnt = font(BOLD, 17)
        tw = d.textlength(st["tag"], font=chip_fnt)
        cy = max(y + ph - 42, yy + 8)
        d.rounded_rectangle([tx, cy, tx + tw + 20, cy + 28], radius=14,
                            outline=st["color"], width=2)
        d.text((tx + 10, cy + 4), st["tag"], font=chip_fnt, fill=st["color"])

    # ---- footer ticker ----
    d.rectangle([0, 902, W, H], fill=NAVY)
    d.text((24, 912), "ALSO TODAY", font=font(BOLD, 20), fill=GOLD)
    d.text((24, 938), TICKER[0], font=font(REG, 18), fill=WHITE)
    d.text((24, 964), TICKER[1], font=font(REG, 18), fill=WHITE)
    d.text((24, 994), "Sources: Reuters, AP, Just Security, Zark News, Horizon \u2014 18 Nov 2026",
           font=font(REG, 15), fill=(160, 170, 185))

    img.save(path, "PNG", optimize=True)


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
