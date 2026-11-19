#!/usr/bin/env python3
"""Render the newsday-20261119 front page: one 1024x1024 PNG summing up
Thursday 19 November 2026. Flat editorial style: warm paper, black ink,
one red accent, a gold figure. Drawn with Pillow only; no network.

Run from the repository root:  python3 tools/draw.py
Writes entry.png next to this script's parent directory.

Geometry is budgeted top to bottom (1024 total): masthead 210, hero 300,
middle row 290, bottom row 150, ticker 50, with 12px gaps. Every text block
is wrapped and measured before drawing so nothing can spill its box.
"""

import hashlib
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
PAPER = (246, 242, 231)
INK = (24, 24, 24)
RED = (190, 38, 28)
GOLD = (168, 124, 22)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def text_w(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, f, fill=INK, leading=1.22):
    """Draw lines top-aligned at (x, y); returns the y just below the block."""
    lh = int(f.size * leading)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def fit_lines(draw, text, size, max_w, max_lines, bold=True):
    """Largest bold-sans size at or below `size` wrapping into max_lines."""
    while size > 10:
        f = SANS_B(size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 2
    return wrap(draw, text, SANS_B(10), max_w), SANS_B(10)


def shrink_to_fit(draw, text, size, max_w):
    """Largest bold-sans size at or below `size` fitting one line in max_w."""
    while size > 10:
        f = SANS_B(size)
        if text_w(draw, text, f) <= max_w:
            return f
        size -= 1
    return SANS_B(10)


def star_points(cx, cy, r_out, r_in, rot=-90.0):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36.0)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def flag_us(draw, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        if i % 2 == 0:
            draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                           fill=(178, 34, 52))
    cw, ch = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(30, 50, 110))
    for r in range(4):
        for c in range(5):
            px = x + 6 + c * (cw - 10) / 4.0
            py = y + 5 + r * (ch - 9) / 3.0
            draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5],
                         fill=(255, 255, 255))


def flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.24, y + h * 0.28
    draw.polygon(star_points(cx, cy, h * 0.22, h * 0.09), fill=(255, 222, 0))
    for dx, dy in ((0.52, 0.12), (0.66, 0.28), (0.66, 0.52), (0.52, 0.66)):
        sx, sy = x + w * dx, y + h * dy
        draw.polygon(star_points(sx, sy, h * 0.08, h * 0.033),
                     fill=(255, 222, 0))


def flag_ru(draw, x, y, w, h):
    third = h / 3.0
    draw.rectangle([x, y, x + w, y + third], fill=(245, 245, 245))
    draw.rectangle([x, y + third, x + w, y + 2 * third], fill=(0, 60, 160))
    draw.rectangle([x, y + 2 * third, x + w, y + h], fill=(210, 30, 30))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def skyline(draw, x0, y_base, x1, heights):
    n = len(heights)
    step = (x1 - x0) / n
    for i, hh in enumerate(heights):
        bx0 = x0 + i * step + 2
        bx1 = x0 + (i + 1) * step - 2
        draw.rectangle([bx0, y_base - hh, bx1, y_base], fill=INK)
        if hh > 70:
            mid = (bx0 + bx1) / 2
            draw.rectangle([mid - 4, y_base - hh - 16, mid + 4, y_base - hh],
                           fill=INK)


def icon_capitol(draw, x, y, s):
    draw.pieslice([x, y, x + s, y + s], 180, 360, fill=INK)
    draw.rectangle([x + s * 0.08, y + s * 0.48, x + s * 0.92, y + s * 0.58],
                   fill=INK)
    for i in range(4):
        cx = x + s * (0.16 + i * 0.23)
        draw.rectangle([cx, y + s * 0.58, cx + s * 0.07, y + s * 0.92],
                       fill=INK)
    draw.rectangle([x, y + s * 0.92, x + s, y + s], fill=INK)
    draw.line([x + s / 2, y - s * 0.2, x + s / 2, y], fill=INK, width=2)
    draw.polygon([(x + s / 2, y - s * 0.2), (x + s * 0.76, y - s * 0.12),
                  (x + s / 2, y - s * 0.04)], fill=RED)


def icon_bars(draw, x, y, s):
    bw = s * 0.22
    for i, v in enumerate((0.35, 0.6, 0.9)):
        bx = x + i * s * 0.32
        draw.rectangle([bx, y + s * (1 - v), bx + bw, y + s], fill=INK)
    draw.line([x + s * 0.05, y + s * 0.28, x + s * 0.95, y + s * 0.02],
              fill=RED, width=3)


def icon_scales(draw, x, y, s):
    cx = x + s / 2
    draw.line([cx, y + s * 0.06, cx, y + s * 0.88], fill=INK, width=3)
    draw.line([x + s * 0.08, y + s * 0.24, x + s * 0.92, y + s * 0.24],
              fill=INK, width=3)
    for sx in (x + s * 0.08, x + s * 0.92):
        draw.line([sx, y + s * 0.24, sx - s * 0.13, y + s * 0.5], fill=INK,
                  width=2)
        draw.line([sx, y + s * 0.24, sx + s * 0.13, y + s * 0.5], fill=INK,
                  width=2)
        draw.pieslice([sx - s * 0.14, y + s * 0.46, sx + s * 0.14,
                       y + s * 0.74], 0, 180, fill=INK)
    draw.ellipse([cx - 4, y + s * 0.02, cx + 4, y + s * 0.1], fill=RED)
    draw.rectangle([x + s * 0.22, y + s * 0.88, x + s * 0.78, y + s * 0.98],
                   fill=INK)


def icon_bridge(draw, x, y, s):
    for tx in (x + s * 0.16, x + s * 0.76):
        draw.rectangle([tx, y + s * 0.06, tx + s * 0.08, y + s * 0.6],
                       fill=INK)
    draw.rectangle([x + s * 0.04, y + s * 0.58, x + s * 0.96, y + s * 0.66],
                   fill=INK)
    draw.arc([x + s * 0.12, y, x + s * 0.88, y + s * 0.72], 15, 165,
             fill=RED, width=3)
    for wy in (0.74, 0.86):
        for k in range(3):
            wx = x + k * s * 0.32
            draw.arc([wx, y + s * wy, wx + s * 0.26, y + s * (wy + 0.12)],
                     180, 360, fill=INK, width=2)


def icon_tank(draw, x, y, s):
    draw.rectangle([x + s * 0.08, y + s * 0.42, x + s * 0.9, y + s * 0.66],
                   fill=INK)
    draw.rectangle([x + s * 0.34, y + s * 0.2, x + s * 0.64, y + s * 0.44],
                   fill=INK)
    draw.line([x + s * 0.6, y + s * 0.3, x + s * 0.98, y + s * 0.3],
              fill=INK, width=4)
    for i in range(4):
        cx = x + s * (0.2 + i * 0.2)
        draw.ellipse([cx - s * 0.06, y + s * 0.66, cx + s * 0.06,
                      y + s * 0.78], fill=INK)
    draw.rectangle([x + s * 0.06, y + s * 0.76, x + s * 0.94, y + s * 0.84],
                   fill=INK)


def story_box(draw, x, y, w, h, kick, head, body, head_size=28,
              icon=None, gold=None, body_size=18):
    """One bordered story box. Icon sits on the kicker row, clear of text."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=3)
    px = x + 16
    inner = w - 32
    py = y + 13
    if icon is not None:
        icon(draw, x + w - 50, y + 8, 36)
    draw.text((px, py), kick, font=SANS_B(19), fill=RED)
    py += 26
    head_lines, head_f = fit_lines(draw, head, head_size, inner, 2)
    py = draw_lines(draw, head_lines, px, py + 2, head_f, leading=1.12)
    if gold:
        py = draw_lines(draw, [gold], px, py + 4, SANS_B(32), fill=GOLD,
                        leading=1.1)
    body_lines = wrap(draw, body, SANS(body_size), inner)
    end = draw_lines(draw, body_lines, px, py + 6, SANS(body_size),
                     leading=1.25)
    assert end <= y + h - 8, f"{kick} box overflows by {end - (y + h - 8)}px"
    return y + h


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28
    cw = W - 2 * mx

    # ---- Masthead: 16..210 ---------------------------------------------
    y = 16
    wd = "THURSDAY"
    d.text(((W - text_w(d, wd, SANS_B(26))) // 2, y), wd, font=SANS_B(26),
           fill=RED)
    y += 36
    date = "19 NOVEMBER 2026"
    df = SERIF_B(78)
    assert text_w(d, date, df) <= cw, "date too wide"
    d.text(((W - text_w(d, date, df)) // 2, y), date, font=df, fill=INK)
    y += 92
    d.rectangle([mx, y, W - mx, y + 5], fill=INK)
    y += 14
    stand = ("Three leaders meet in Shenzhen, a record IPO debuts, and a "
             "court rules: the day in six stories.")
    y = draw_lines(d, wrap(d, stand, SERIF(21), cw), mx, y, SERIF(21),
                   leading=1.25)
    assert y <= 210, f"masthead ends at {y}"
    y = 210

    # ---- Hero: 210..510 -------------------------------------------------
    hy, hh = 210, 300
    d.rectangle([mx, hy, W - mx, hy + hh], outline=INK, width=3)
    hx, hw = mx + 18, 612
    py = hy + 16
    d.text((hx, py), "SHENZHEN  ·  APEC", font=SANS_B(23), fill=RED)
    py += 30
    head_lines, head_f = fit_lines(d, "TRUMP, XI, PUTIN MEET IN SHENZHEN",
                                   46, hw, 2)
    py = draw_lines(d, head_lines, hx, py + 2, head_f, leading=1.1)
    bullets = [
        "First-ever three-way summit; Xi meets Trump first.",
        "Nuclear arms on the table; Ukraine off the agenda.",
        "Rare-earth exports to the US still ~75% below normal.",
    ]
    py += 10
    for b in bullets:
        lines = wrap(d, b, SANS(19), hw - 24)
        assert len(lines) <= 1, f"hero bullet wraps: {b}"
        d.rectangle([hx, py + 6, hx + 10, py + 16], fill=RED)
        py = draw_lines(d, lines, hx + 24, py, SANS(19), leading=1.25)
        py += 8
    assert py <= hy + hh - 12, f"hero text ends at {py}"
    # Right illustration: three flags over a skyline.
    ix0, ix1 = mx + 654, W - mx - 18
    iy_top = hy + 18
    pole_h = 112
    flag_w, flag_h = 72, 46
    xs = [ix0 + 6, ix0 + 102, ix0 + 198]
    for fx, fn in zip(xs, (flag_us, flag_cn, flag_ru)):
        d.line([fx + flag_w // 2, iy_top, fx + flag_w // 2,
                iy_top + pole_h], fill=INK, width=3)
        d.ellipse([fx + flag_w // 2 - 4, iy_top - 5, fx + flag_w // 2 + 4,
                   iy_top + 3], fill=RED)
        fn(d, fx, iy_top + 4, flag_w, flag_h)
    for i in range(9):
        bx = ix0 + 18 + i * 30
        by = iy_top + 72 + (6 if i % 2 else 0)
        d.polygon([(bx, by), (bx + 20, by), (bx + 10, by + 15)],
                  fill=RED if i % 3 == 0 else INK)
    skyline(d, ix0, hy + hh - 16, ix1,
            [48, 82, 60, 110, 70, 90, 54, 78])
    d.rectangle([ix0, hy + hh - 16, ix1, hy + hh - 12], fill=RED)

    # ---- Middle row: 522..806 -------------------------------------------
    my, mh = 522, 284
    gap = 12
    bw = (cw - 2 * gap) // 3
    story_box(d, mx, my, bw, mh, "WASHINGTON",
              "JEFFRIES NOMINATED FOR SPEAKER",
              "House Democrats pick Hakeem Jeffries 251-11, in line to be "
              "the first Black Speaker. The full House votes on 3 January.",
              icon=icon_capitol)
    story_box(d, mx + bw + gap, my, bw, mh, "MARKETS",
              "ANTHROPIC DEBUTS AT $83 A SHARE",
              "The largest IPO ever, topping SpaceX. Shares start trading "
              "today on Nasdaq as ANT; value near $1.5tn.",
              icon=icon_bars, gold="$81.3bn")
    story_box(d, mx + 2 * (bw + gap), my, bw, mh, "THE HAGUE",
              "ICJ TO RULE ON ROHINGYA GENOCIDE",
              "Judgment due at 10 a.m. on whether Myanmar committed "
              "genocide. The court has never found a state guilty of it.",
              icon=icon_scales)

    # ---- Bottom row: 818..974 -------------------------------------------
    by, bh = 818, 156
    bw2 = (cw - gap) // 2
    story_box(d, mx, by, bw2, bh, "UKRAINE",
              "CRIMEA BRIDGE HIT AGAIN",
              "Overnight strike, the third in a week, halts traffic across "
              "the crossing; damage being assessed.",
              head_size=26, body_size=17, icon=icon_bridge)
    story_box(d, mx + bw2 + gap, by, bw2, bh, "GAZA",
              "ISRAELI TROOPS ENTER CENTRAL GAZA",
              "Rare ground operation in a ceasefire area; dozens of "
              "families flee their tents.",
              head_size=26, body_size=17, icon=icon_tank)

    # ---- Ticker: 974..1024 ----------------------------------------------
    ty = 974
    d.rectangle([0, ty, W, H], fill=INK)
    t1 = ("GTA VI ROLLS OUT WORLDWIDE  ·  INDIA-JAPAN 2+2 IN TOKYO  ·  "
          "EU PROPOSES €45BN UKRAINE LOAN")
    t2 = ("EISENKOT TO FORM ISRAELI GOVERNMENT  ·  CYCLONE AKVAN NEARS "
          "ODISHA  ·  PEW: ISLAM LARGEST BY 2035")
    f1 = shrink_to_fit(d, t1, 19, W - 16)
    f2 = shrink_to_fit(d, t2, 19, W - 16)
    d.text(((W - text_w(d, t1, f1)) // 2, ty + 5), t1, font=f1,
           fill=(245, 241, 230))
    d.text(((W - text_w(d, t2, f2)) // 2, ty + 27), t2, font=f2,
           fill=(245, 241, 230))

    out = os.path.join(ROOT, "entry.png")
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print(f"wrote {out}  {len(data)} bytes  "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    assert len(data) <= 1048576, "entry.png exceeds 1 MiB"
    assert img.size == (1024, 1024)


if __name__ == "__main__":
    sys.exit(main())
