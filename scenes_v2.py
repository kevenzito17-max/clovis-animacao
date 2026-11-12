#!/usr/bin/env python3
"""Cenas v2 — mais detalhadas e realistas. Usa os helpers do render_video."""
import math
import numpy as np
from PIL import Image, ImageDraw
import render_video as r
from render_video import (W, H, S, C, rr, ell, line, txt, font, gradient,
                          draw_char, draw_bus, F_SIGN, F_CLOCK, F_DAY, F_CHECK,
                          F_TITLE, YELL, RED, WHITE, SKIN, SKIN_D, HAIR, SHIRT)

SPRITE_PATH = 'assets/clovis_sprite.png'
_sprite = None
def load_sprite():
    global _sprite
    if _sprite is None:
        try:
            _sprite = Image.open(SPRITE_PATH).convert('RGBA')
        except Exception:
            _sprite = False
    return _sprite

def add_char(im, d, x, y, t, **kw):
    """Desenha o Clóvis: usa o sprite enviado pelo usuário se existir."""
    sp = load_sprite()
    walking = kw.get('walking', False)
    phase = kw.get('phase', t * 11)
    if sp:
        h = int(170 * S)
        w = int(sp.width * h / sp.height)
        spr = sp.resize((w, h), Image.LANCZOS)
        bob = -5 * abs(math.sin(phase)) if walking else 0
        px, py = int((x - w / (2 * S)) * S), int((y - h / S) * S + bob * S)
        im.paste(spr, (px, py), spr)
        ell(d, (x - 28, y - 4, x + 28, y + 4), fill=(0, 0, 0, 70))
        return
    draw_char(d, x, y, t, **kw)

# ---------- helpers novos ----------
def cloud(d, x, y, s, alpha=90):
    for dx, dy, ds in ((0, 0, 1.0), (s * .9, s * .15, .75), (-s * .9, s * .2, .7), (s * .3, -s * .35, .8)):
        ell(d, (x + dx - s * ds, y + dy - s * ds * .55, x + dx + s * ds, y + dy + s * ds * .55),
            fill=(255, 255, 255, alpha))

def city2(d, base_y, lit=False, dusk_glow=False):
    heights = [300, 215, 265, 180, 240, 195]
    x = 20
    bw = 118
    for i, h in enumerate(heights):
        top = base_y - h
        shade = C('3b4a68') if i % 2 == 0 else C('33415c')
        rr(d, (x, top, x + bw, base_y), 4, fill=shade)
        rr(d, (x + 8, top - 14, x + 20, top), 2, fill=shade)
        if i % 3 == 1:
            d.rectangle([(x + bw - 30) * S, (top - 20) * S, (x + bw - 12) * S, top * S], fill=shade)
        wy = 0
        for row in range(int(top) + 16, int(base_y) - 14, 26):
            wx = 0
            for col in range(x + 14, x + bw - 16, 28):
                on = lit and ((i * 7 + row * 3 + col) % 11) < 4
                col_ = (255, 209, 102, 150) if on else (C('ffd166') if dusk_glow and (i + col) % 5 == 0 else C('26324a'))
                d.rectangle([(col + wx * 0) * S, row * S, (col + 15) * S, (row + 11) * S], fill=col_)
                wx += 1
            wy += 1
        x += bw + 26

def road2(d, crosswalk=False):
    gy = H - 100
    d.rectangle([0, gy * S, W * S, H * S], fill=C('3a4a5f'))
    d.rectangle([0, (gy + 40) * S, W * S, H * S], fill=C('272e3d'))
    for x in range(-20, W + 40, 90):
        d.rectangle([x * S, (gy + 72) * S, (x + 42) * S, (gy + 76) * S], fill=(244, 241, 222, 60))
    if crosswalk:
        for k in range(6):
            x0 = 470 + k * 62
            d.rectangle([x0 * S, (gy + 44) * S, (x0 + 30) * S, (gy + 96) * S], fill=(244, 241, 222, 130))
    return gy

def window_night(d, x, y, w, h, t):
    rr(d, (x - 8, y - 8, x + w + 8, y + h + 8), 8, fill=C('5b5470'))
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=C('0b1226'))
    ell(d, (x + w * .68, y + h * .22, x + w * .68 + 26, y + h * .22 + 26), fill=C('fdfbf4'))
    for k in range(14):
        sx = x + 12 + (k * 53) % (w - 24)
        sy = y + 10 + (k * 37) % (h - 40)
        a = int(100 + 100 * math.sin(t * 2 + k))
        ell(d, (sx, sy, sx + 2.4, sy + 2.4), fill=(255, 255, 255, a))
    d.rectangle([(x + w / 2 - 3) * S, y * S, (x + w / 2 + 3) * S, (y + h) * S], fill=C('5b5470'))
    d.rectangle([x * S, (y + h / 2 - 3) * S, (x + w) * S, (y + h / 2 + 3) * S], fill=C('5b5470'))
    rr(d, (x - 20, y - 6, x - 6, y + h + 10), 4, fill=C('7a6fa0'))
    rr(d, (x + w + 6, y - 6, x + w + 20, y + h + 10), 4, fill=C('7a6fa0'))

def lamp_glow(d, x, y, rad=70, col=(255, 220, 150)):
    for k in range(3):
        a = 26 - k * 8
        ell(d, (x - rad * (1 + k * .35), y - rad * (1 + k * .35), x + rad * (1 + k * .35), y + rad * (1 + k * .35)),
            fill=col + (a,))

# ---------- cenas ----------
def quarto_v2(t, sitting=False, warning=False):
    im = gradient((C('453d63'), C('6b5f8a')))
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('5a4a42'))
    d.rectangle([0, (H - 100) * S, W * S, (H - 88) * S], fill=C('6e5a50'))
    ell(d, (300, H - 40, 760, H + 10), fill=(90, 60, 80, 120))
    window_night(d, 60, 60, 200, 150, t)
    rr(d, (1010, 90, 1170, 420), 10, fill=C('5f5478'))
    d.rectangle([(1090 - 3) * S, 100 * S, (1090 + 3) * S, 410 * S], fill=C('4a4160'))
    ell(d, (1078, 240, 1092, 254), fill=C('c9bfa0'))
    ell(d, (1088, 240, 1102, 254), fill=C('c9bfa0'))
    rr(d, (880, 330, 990, H - 100), 8, fill=C('7a5c3e'))
    rr(d, (895, 300, 975, 336), 8, fill=C('8a6c4a'))
    lamp_glow(d, 935, 310, 60)
    rr(d, (905, 268, 965, 302), 10, fill=C('ffe9a8'))
    r.draw_bed(d, 380, H - 106)
    r.draw_clock(d, 1000, 70, t, shake=(not sitting and not warning and t < 5.0),
                 calm=sitting or warning)
    if sitting:
        add_char(im, d, 520, H - 102, t, pose='sit', eyes='open' if warning else 'one', mouth='sad')
    else:
        ell(d, (466, H - 192, 522, H - 146), fill=SKIN)
        rr(d, (464, H - 198, 524, H - 178), 9, fill=HAIR)
        d.rectangle([484 * S, (H - 174) * S, 496 * S, (H - 170) * S], fill=C('26211d'))
        d.rectangle([504 * S, (H - 174) * S, 516 * S, (H - 170) * S], fill=C('26211d'))
        for zx, zy, dl in ((570, H - 266, 0.0), (600, H - 296, 0.9), (555, H - 321, 1.7)):
            ph = (t + dl) % 2.6
            a = int(220 * (1 - ph / 2.6))
            txt(d, zx, zy - ph * 22, 'Z', font(20, bold=True), (207, 216, 255, a))
    return im

def kitchen_v2(t):
    im = gradient((C('5a5470'), C('7a7290')))
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('8a7a6a'))
    d.rectangle([0, (H - 100) * S, W * S, (H - 88) * S], fill=C('9a8a7a'))
    rr(d, (60, 70, 260, 220), 8, fill=C('5b5470'))
    d.rectangle([60 * S, 70 * S, 260 * S, 220 * S], fill=C('ffdf9e'))
    d.rectangle([(160 - 3) * S, 70 * S, (160 + 3) * S, 220 * S], fill=C('5b5470'))
    d.rectangle([60 * S, 145 * S, 260 * S, 151 * S], fill=C('5b5470'))
    rr(d, (1080, 110, 1200, H - 100), 12, fill=C('c8cdd4'))
    d.rectangle([(1140 - 3) * S, 130 * S, (1140 + 3) * S, 300 * S], fill=C('9aa0a8'))
    rr(d, (1090, 150, 1190, 240), 4, fill=(255, 255, 255, 40))
    rr(d, (300, H - 260, 900, H - 100), 6, fill=C('8a6c4e'))
    d.rectangle([300 * S, (H - 268) * S, 900 * S, (H - 252) * S], fill=C('a89070'))
    for k in range(4):
        cx0 = 330 + k * 148
        rr(d, (cx0, H - 240, cx0 + 128, H - 110), 6, fill=C('7a5f42'))
        rr(d, (cx0 + 50, H - 185, cx0 + 78, H - 175), 3, fill=C('c9bfa0'))
    lamp_glow(d, 600, 96, 80)
    d.rectangle([560 * S, 60 * S, 640 * S, 100 * S], fill=C('3a3f4d'))
    ell(d, (570, 96, 630, 116), fill=C('ffe9a8'))
    rr(d, (430, H - 152, 700, H - 138), 4, fill=C('9c7a52'))
    for px in (448, 668):
        d.rectangle([px * S, (H - 138) * S, (px + 10) * S, (H - 74) * S], fill=C('66502f'))
    rr(d, (508, H - 178, 536, H - 152), 6, fill=C('f0607f'))
    for k in range(2):
        ph = (t + k * 0.8) % 2.2
        a = int(70 * (1 - ph / 2.2))
        ell(d, (518 + k * 8, H - 196 - ph * 26, 526 + k * 8, H - 182 - ph * 26), fill=(255, 255, 255, a))
    rr(d, (576, H - 172, 620, H - 152), 8, fill=C('e0aa63'))
    add_char(im, d, 330, H - 96, t, pose='sit', eyes='open', mouth='flat')
    return im

def bathroom_v2(t, char_x=None):
    im = gradient((C('7e97a8'), C('9db4c2')))
    d = ImageDraw.Draw(im, 'RGBA')
    for gy in range(0, H - 100, 52):
        for gx in range(0, W, 52):
            d.rectangle([gx * S, gy * S, (gx + 50) * S, (gy + 50) * S],
                        fill=C('a8c0ce') if (gx // 52 + gy // 52) % 2 == 0 else C('98b2c2'))
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('7a8a94'))
    rr(d, (130, 90, 300, 210), 10, fill=C('cfe7fb'), outline=C('7d5f3e'), width=6 * S)
    d.rectangle([160 * S, 110 * S, 210 * S, 190 * S], fill=(255, 255, 255, 60))
    rr(d, (880, 200, 920, 208), 3, fill=C('6a6a72'))
    rr(d, (860, 208, 940, 218), 4, fill=C('5fa8d3'))
    rr(d, (900, H - 210, 1120, H - 150), 10, fill=C('ececec'))
    ell(d, (960, H - 196, 1060, H - 166), fill=C('b8c4cc'))
    rr(d, (960, H - 236, 976, H - 208), 4, fill=C('c0c0c0'))
    rr(d, (940, H - 268, 996, H - 256), 4, fill=C('0dc9a0'))
    d.rectangle([928 * S, (H - 268) * S, 940 * S, (H - 265) * S], fill=WHITE)
    rr(d, (760, H - 130, 940, H - 96), 8, fill=C('5fa8d3'))
    if char_x is not None:
        add_char(im, d, char_x, H - 96, t, pose='stand', eyes='open', mouth='flat', walking=True, phase=t * 11)
    return im

def bus_street_v2(t, kind, char_x=None, walking=False, mouth='flat', bus_x=None, bus_color=None, backpack=False):
    if kind == 'dawn':
        im = gradient((C('26365f'), C('e8985e')))
        cloud(d := ImageDraw.Draw(im, 'RGBA'), 300, 120, 34, 70)
        cloud(d, 700, 80, 26, 60)
        ell(d, (1000, 300, 1064, 364), fill=C('ffb84d'))
        lamp_glow(d, 1032, 332, 40, col=(255, 190, 110))
    else:
        im = gradient((C('6db9dd'), C('aadcf7')))
        d = ImageDraw.Draw(im, 'RGBA')
        cloud(d, 280, 100, 36, 160)
        cloud(d, 760, 70, 28, 140)
        ell(d, (980, 60, 1044, 124), fill=C('ffe9a8'))
    city2(d, H - 100, lit=(kind == 'dawn'))
    gy = road2(d, crosswalk=True)
    d.rectangle([150 * S, (H - 260) * S, 158 * S, (H - 100) * S], fill=C('7c8698'))
    rr(d, (104, H - 296, 208, H - 258), 5, fill=C('f5c95d'))
    txt(d, 156, H - 291, 'ÔNIBUS', F_SIGN, C('4a3b12'), anchor='ma')
    rr(d, (240, H - 150, 360, H - 104), 6, fill=C('8a6c4e'))
    d.rectangle([240 * S, (H - 156) * S, 360 * S, (H - 148) * S], fill=C('9a7c5e'))
    d.rectangle([250 * S, (H - 144) * S, 350 * S, (H - 138) * S], fill=C('8a6c4e'))
    rr(d, (420, H - 130, 470, H - 100), 6, fill=C('4a6b52'))
    ell(d, (428, H - 138, 462, H - 122), fill=C('4a6b52'))
    if bus_x is not None and bus_x < 1350:
        c1, c2 = bus_color if bus_color else (C('f28268'), C('dd5f42'))
        draw_bus(d, bus_x, gy + 66, c1, c2)
    if char_x is not None:
        add_char(im, d, char_x, gy + 62, t, pose='stand', eyes='open', mouth=mouth,
                 walking=walking, phase=t * 11, backpack=backpack)
    return im

def metro_v2(t, char_x=None, bus_x=None):
    im = gradient((C('20242e'), C('303644')))
    d = ImageDraw.Draw(im, 'RGBA')
    for gy in range(0, H - 140, 46):
        for gx in range(0, W, 46):
            d.rectangle([gx * S, gy * S, (gx + 44) * S, (gy + 44) * S],
                        fill=C('3c4454') if (gx // 46 + gy // 46) % 2 == 0 else C('343c4c'))
    d.rectangle([0, (H - 150) * S, W * S, (H - 138) * S], fill=YELL)
    d.rectangle([0, (H - 138) * S, W * S, H * S], fill=C('3a3f4d'))
    d.rectangle([0, (H - 96) * S, W * S, (H - 60) * S], fill=C('272e3d'))
    for px in (240, 640, 1040):
        rr(d, (px - 14, 60, px + 14, H - 140), 6, fill=C('4a5262'))
    for lx in range(120, W, 260):
        d.rectangle([lx * S, 40 * S, (lx + 90) * S, 52 * S], fill=C('fff7cf'))
        lamp_glow(d, lx + 45, 52, 46, col=(255, 247, 207))
    rr(d, (60, 90, 220, 130), 6, fill=C('1b7fa3'))
    txt(d, 140, 98, 'LINHA 7', font(14, bold=True), WHITE, anchor='ma')
    if bus_x is not None and bus_x < 1350:
        draw_bus(d, bus_x, H - 40, C('2ba3cc'), C('1b7fa3'), metro=True)
    if char_x is not None:
        add_char(im, d, char_x, H - 62, t, pose='stand', eyes='open', mouth='flat',
                 walking=char_x is not None and 2.6 <= t < 4.2, phase=t * 11)
    return im

def office_v2(t, char_x=None):
    im = gradient((C('6a7590'), C('8a94aa')))
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('787e8c'))
    for lx in range(140, W, 300):
        d.rectangle([lx * S, 36 * S, (lx + 120) * S, 48 * S], fill=C('fdfdf2'))
        lamp_glow(d, lx + 60, 48, 60, col=(253, 253, 242))
    rr(d, (70, 90, 330, 230), 6, fill=C('e8ecef'), outline=C('9aa4ae'), width=4 * S)
    for k in range(3):
        d.line([(100 + k * 60) * S, 130 * S, (150 + k * 60) * S, 120 * S], fill=C('3a7bd5'), width=3 * S)
    d.rectangle([90 * S, 160 * S, 140 * S, 165 * S], fill=C('ef476f'))
    d.rectangle([90 * S, 175 * S, 170 * S, 180 * S], fill=C('3a7bd5'))
    rr(d, (1020, 80, 1200, 260), 8, fill=C('9cc9e8'), outline=C('6a7590'), width=5 * S)
    d.rectangle([1106 * S, 80 * S, 1114 * S, 260 * S], fill=C('6a7590'))
    for dx, skin, shirt in ((190, C('c9ada7'), C('457b9d')), (590, C('e8c39e'), C('6d597a')), (980, C('b5838d'), C('355070'))):
        rr(d, (dx - 110, H - 152, dx + 110, H - 138), 3, fill=C('9c7a52'))
        for px in (dx - 90, dx + 80):
            d.rectangle([px * S, (H - 138) * S, (px + 10) * S, (H - 74) * S], fill=C('66502f'))
        rr(d, (dx - 26, H - 196, dx + 26, H - 158), 4, fill=C('22283a'))
        rr(d, (dx - 20, H - 190, dx + 20, H - 164), 3, fill=C('7fd4ff'))
        ell(d, (dx + 40, H - 160, dx + 72, H - 140), fill=(0, 0, 0, 40))
        r.draw_coworker(d, dx, H - 138, t, skin, shirt)
    rr(d, (1160, H - 190, 1220, H - 100), 8, fill=C('b5651d'))
    ell(d, (1140, H - 240, 1240, H - 180), fill=C('3f7d44'))
    if char_x is not None:
        add_char(im, d, char_x, H - 96, t, pose='stand', eyes='open', mouth='sad',
                 walking=t < 2.6, phase=t * 11)
    return im

def dusk_v2(t, char_x=None, backpack=False):
    im = gradient((C('2e2749'), C('e79a5e')))
    d = ImageDraw.Draw(im, 'RGBA')
    cloud(d, 320, 140, 40, 90)
    cloud(d, 800, 100, 30, 80)
    ell(d, (860, 400, 924, 464), fill=C('e8854f'))
    lamp_glow(d, 892, 432, 55, col=(232, 133, 79))
    city2(d, H - 100, lit=True, dusk_glow=True)
    gy = road2(d, crosswalk=True)
    for lx in (280, 820):
        d.rectangle([lx * S, (H - 250) * S, (lx + 6) * S, (H - 100) * S], fill=C('4a5262'))
        d.rectangle([(lx - 18) * S, (H - 258) * S, (lx + 16) * S, (H - 248) * S], fill=C('4a5262'))
        ell(d, (lx - 12, H - 250, lx + 14, H - 240), fill=C('ffe9a8'))
        lamp_glow(d, lx + 1, H - 244, 52, col=(255, 233, 168))
    if char_x is not None:
        add_char(im, d, char_x, gy + 62, t, pose='stand', eyes='open', mouth='sad',
                 walking=True, phase=t * 11, backpack=backpack)
    return im

def scene_at_v2(idx, t):
    if idx in (0, 1, 2):
        return quarto_v2(t, sitting=(idx >= 1), warning=(idx == 2))
    if idx == 3:
        cx = 200 + min(1, max(0, (t - 0.7) / 3.6)) * 700
        return bus_street_v2(t, 'dawn', char_x=cx, walking=(t < 4.3))
    if idx == 4:  return kitchen_v2(t)
    if idx == 5:  return bathroom_v2(t, char_x=180 + min(1, max(0, (t - 0.6) / 2.4)) * 380)
    if idx in (6, 7, 8):
        if t < 2.6:   bx = -300 + (t / 2.6) * 480
        elif t < 5.0: bx = 180
        else:         bx = 180 + ((t - 5.0) / 2.0) * 1300
        if idx == 6:
            return bus_street_v2(t, 'dawn', char_x=None if t >= 5.0 else 380 + min(1, max(0, (t - 2.6) / 1.6)) * 90,
                                 walking=(2.6 <= t < 4.2), bus_x=bx, bus_color=(C('f28268'), C('dd5f42')))
        if idx == 7:
            return bus_street_v2(t, 'day', char_x=None if t >= 5.0 else 400 + min(1, max(0, (t - 2.6) / 1.6)) * 90,
                                 walking=(2.6 <= t < 4.2), bus_x=bx, bus_color=(C('9fd4ee'), C('6fb3d6')))
        return metro_v2(t, char_x=None if t >= 5.0 else 420 + min(1, max(0, (t - 2.6) / 1.6)) * 90, bus_x=bx)
    if idx == 9:  return office_v2(t, char_x=60 + min(1, max(0, (t - 0.6) / 2.4)) * 200)
    if idx == 10:
        cx = 120 + min(1, max(0, (t - 0.6) / 3.6)) * 780
        return dusk_v2(t, char_x=cx)
    return r.scene_week(t)

# ---------- cenas v3 (ficha do Cláudio) ----------
def bus_interior(t, variant=0):
    im = gradient((C('c9c4b8'), C('a8a294')))
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, (H - 130) * S, W * S, H * S], fill=C('6a655a'))
    d.rectangle([0, (H - 130) * S, W * S, (H - 118) * S], fill=C('7a7468'))
    wy0, wy1 = 90, 240
    d.rectangle([0, wy0 * S, W * S, wy1 * S], fill=C('3c4454'))
    shift = int(t * 130) % 260
    for k in range(-1, 6):
        bx0 = k * 260 - shift
        rr(d, (bx0 + 14, wy0 + 14, bx0 + 246, wy1 - 14), 8, fill=C('9cc9e8'))
        rr(d, (bx0 + 30, wy0 + 40, bx0 + 120, wy1 - 40), 6, fill=C('c8e4f6'))
        base = H - 130
        hh = [180, 130, 210, 150]
        for j, h in enumerate(hh):
            rr(d, (bx0 + 30 + j * 55, base - h, bx0 + 75 + j * 55, base), 2, fill=C('33415c'))
    for wx0 in range(0, W + 130, 130):
        d.rectangle([wx0 * S, wy0 * S, (wx0 + 8) * S, wy1 * S], fill=C('5a5f6a'))
    rr(d, (W / 2 - 170, 20, W / 2 + 170, 62), 6, fill=C('f5c95d'))
    txt(d, W / 2, 27, 'FOCO, FORÇA E FÉ', font(17, bold=True), C('4a3b12'), anchor='ma')
    for sx0 in range(40, W, 240):
        rr(d, (sx0, H - 260, sx0 + 150, H - 140), 10, fill=C('4a6b8a'))
        rr(d, (sx0 + 12, H - 248, sx0 + 138, H - 190), 8, fill=C('5a7b9a'))
    ell(d, (445, H - 96, 505, H - 84), fill=(0, 0, 0, 60))
    if variant == 0:
        draw_char(d, 475, H - 150, t, pose='sit', eyes='closed', mouth='flat', hand_face=True, backpack=True)
    else:
        d.rectangle([487 * S, 70 * S, 497 * S, (H - 140) * S], fill=C('8a8f99'))
        ell(d, (481, 62, 503, 80), fill=C('c9c4b8'))
        draw_char(d, 475, H - 140, t, pose='stand', eyes='open', mouth='sad', hold_bar=True, backpack=True)
    return im

def tv_scene(t):
    im = gradient((C('3a3450'), C('54496e')))
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, (H - 110) * S, W * S, H * S], fill=C('5a4a42'))
    window_night(d, 80, 60, 190, 140, t)
    flicker = 0.85 + 0.15 * math.sin(t * 9)
    rr(d, (760, 120, 1140, 340), 10, fill=C('14141c'), outline=C('2a2a36'), width=6 * S)
    d.rectangle([776 * S, 136 * S, 1124 * S, 324 * S], fill=C('0e2a4a'))
    for k in range(3):
        a = int(26 * flicker)
        ell(d, (760 - k * 40, 120 - k * 40, 1140 + k * 40, 340 + k * 40), fill=(120, 180, 255, a))
    txt(d, 950, 190, 'FIM DA ESCALA', font(24, bold=True), C('ff6b6b'), anchor='ma')
    txt(d, 950, 228, '6x1 ?', font(30, bold=True), WHITE, anchor='ma')
    rr(d, (830, 340, 1070, 360), 4, fill=C('3a3450'))
    rr(d, (300, H - 210, 700, H - 130), 14, fill=C('6a5a8a'))
    rr(d, (300, H - 240, 700, H - 200), 12, fill=C('7a6a9a'))
    rr(d, (285, H - 260, 320, H - 130), 8, fill=C('5a4a7a'))
    rr(d, (680, H - 260, 715, H - 130), 8, fill=C('5a4a7a'))
    draw_char(d, 500, H - 150, t, pose='sit', back=True)
    ell(d, (500, H - 152, 620, H - 140), fill=(0, 0, 0, 50))
    return im

def office_v3(t, char_x=None):
    im = office_v2(t, char_x=None)
    d = ImageDraw.Draw(im, 'RGBA')
    if char_x is None or t >= 2.8:
        rr(d, (660, H - 148, 900, H - 134), 3, fill=C('9c7a52'))
        for px in (680, 880):
            d.rectangle([px * S, (H - 134) * S, (px + 10) * S, (H - 74) * S], fill=C('66502f'))
        rr(d, (726, H - 186, 774, H - 148), 4, fill=C('22283a'))
        rr(d, (732, H - 180, 768, H - 154), 3, fill=C('7fd4ff'))
        ell(d, (778, H - 100, 838, H - 88), fill=(0, 0, 0, 40))
        draw_char(d, 780, H - 148, t, pose='sit', eyes='open', mouth='flat', badge=True)
    return im

SCENES_V3_COUNT = 15

def scene_at_v3(idx, t):
    if idx in (0, 1, 2):
        return quarto_v2(t, sitting=(idx >= 1), warning=(idx == 2))
    if idx == 3:
        cx = 200 + min(1, max(0, (t - 0.7) / 3.6)) * 700
        return bus_street_v2(t, 'dawn', char_x=cx, walking=(t < 4.3), backpack=True)
    if idx == 4:  return kitchen_v2(t)
    if idx == 5:  return bathroom_v2(t, char_x=180 + min(1, max(0, (t - 0.6) / 2.4)) * 380)
    if idx == 6:
        bx = -300 + (min(t, 2.6) / 2.6) * 480 if t < 2.6 else (180 if t < 5.0 else 180 + ((t - 5.0) / 2.0) * 1300)
        return bus_street_v2(t, 'dawn', char_x=None if t >= 5.0 else 380 + min(1, max(0, (t - 2.6) / 1.6)) * 90,
                             walking=(2.6 <= t < 4.2), bus_x=bx, bus_color=(C('f28268'), C('dd5f42')))
    if idx == 7:  return bus_interior(t, variant=0)
    if idx == 8:
        bx = -300 + (min(t, 2.6) / 2.6) * 480 if t < 2.6 else (180 if t < 5.0 else 180 + ((t - 5.0) / 2.0) * 1300)
        return bus_street_v2(t, 'day', char_x=None if t >= 5.0 else 400 + min(1, max(0, (t - 2.6) / 1.6)) * 90,
                             walking=(2.6 <= t < 4.2), bus_x=bx, bus_color=(C('9fd4ee'), C('6fb3d6')))
    if idx == 9:  return bus_interior(t, variant=1)
    if idx == 10:
        if t < 2.6:   bx = -300 + (t / 2.6) * 480
        elif t < 5.0: bx = 180
        else:         bx = 180 + ((t - 5.0) / 2.0) * 1300
        return metro_v2(t, char_x=None if t >= 5.0 else 420 + min(1, max(0, (t - 2.6) / 1.6)) * 90, bus_x=bx)
    if idx == 11:
        cx = 60 + min(1, max(0, (t - 0.6) / 2.2)) * 640
        return office_v3(t, char_x=cx if t < 2.8 else None)
    if idx == 12:
        cx = 120 + min(1, max(0, (t - 0.6) / 3.6)) * 780
        return dusk_v2(t, char_x=cx, backpack=True)
    if idx == 13: return tv_scene(t)
    return r.scene_week(t)
