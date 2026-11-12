#!/usr/bin/env python3
"""Renderiza 'A Rotina do Clóvis' como vídeo MP4."""
import math, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
import matplotlib, os

W, H = 1280, 720
S = 2
FPS = 24
DUR = 74.0
OUT = sys.argv[1] if len(sys.argv) > 1 else 'clovis.mp4'

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
def font(sz, bold=False):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype(os.path.join(FONT_DIR, name), sz * S)

F_SUB      = font(24)
F_SUB_SPK  = font(15, bold=True)
F_CLOCK    = font(30, bold=True)
F_SIGN     = font(13, bold=True)
F_TITLE    = font(26, bold=True)
F_DAY      = font(15, bold=True)
F_CHECK    = font(30, bold=True)

def C(hexs):
    hexs = hexs.lstrip('#')
    return tuple(int(hexs[i:i+2], 16) for i in (0, 2, 4))

NIGHT_TOP, NIGHT_BOT = C('070b1c'), C('26334f')
DAWN_TOP,  DAWN_BOT  = C('26365f'), C('e8985e')
DAY_TOP,   DAY_BOT   = C('6db9dd'), C('ffe8c2')
DUSK_TOP,  DUSK_BOT  = C('2e2749'), C('e79a5e')
IN_TOP,    IN_BOT    = C('37344a'), C('4e4766')
SKIN, SKIN_D         = C('f6cba4'), C('e5ac82')
HAIR                 = C('33231b')
BEARD                = C('3a2a20')
SHIRT, SHIRT_D       = C('3a7bd5'), C('2d5fa8')
PANTS, PANTS_D       = C('3d5166'), C('314254')
SHOE                 = C('26262b')
GROUND               = C('3a4a5f')
ROAD                 = C('272e3d')
YELL                 = C('ffd166')
RED                  = C('ef476f')
WHITE                = (255, 255, 255)
BLACK                = (13, 16, 23)

def gradient(colors):
    top, bot = colors
    t = np.linspace(0, 1, H * S)[:, None, None]
    arr = (np.array(top) * (1 - t) + np.array(bot) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, W * S, axis=1))

def rr(d, box, r, **kw):
    d.rounded_rectangle([v * S for v in box], radius=r * S, **kw)

def ell(d, box, **kw):
    d.ellipse([v * S for v in box], **kw)

def line(d, pts, w, fill):
    d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S))
    for x, y in (pts[0], pts[-1]):
        r = w * S / 2
        ell(d, (x - r, y - r, x + r, y + r), fill=fill)

def txt(d, x, y, s, f, fill, anchor='la'):
    d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor)

# ---------- cenários ----------
STARS = [(np.random.rand() * W, np.random.rand() * H * 0.55, np.random.rand() * 6) for _ in range(60)]
WINSEED = np.random.RandomState(7)

def city(d, base_y, heights, lit):
    x = 30
    bw = 120
    for i, h in enumerate(heights):
        top = base_y - h
        rr(d, (x, top, x + bw, base_y), 4, fill=C('33415c'))
        for wy in range(int(top) + 14, int(base_y) - 12, 26):
            for wx in range(x + 16, x + bw - 14, 30):
                if lit and WINSEED.rand() < 0.35:
                    d.rectangle([wx * S, wy * S, (wx + 14) * S, (wy + 11) * S], fill=(255, 209, 102, 60))
                else:
                    d.rectangle([wx * S, wy * S, (wx + 14) * S, (wy + 11) * S], fill=C('26324a'))
        x += bw + 28

def road_and_ground(d, gy=None):
    gy = gy if gy is not None else H - 100
    d.rectangle([0, gy * S, W * S, H * S], fill=GROUND)
    d.rectangle([0, (gy + 44) * S, W * S, H * S], fill=ROAD)
    for x in range(-20, W + 40, 90):
        d.rectangle([x * S, (gy + 74) * S, (x + 40) * S, (gy + 78) * S], fill=C('f4f1de') + (40,))

def sky_scene(kind, t=0.0):
    im = gradient({'night': (NIGHT_TOP, NIGHT_BOT), 'dawn': (DAWN_TOP, DAWN_BOT),
                   'day': (DAY_TOP, DAY_BOT), 'dusk': (DUSK_TOP, DUSK_BOT),
                   'ind': (IN_TOP, IN_BOT)}[kind])
    d = ImageDraw.Draw(im, 'RGBA')
    if kind == 'night':
        for x, y, ph in STARS:
            a = int(90 + 90 * math.sin(t * 2 + ph))
            ell(d, (x - 1.2, y - 1.2, x + 1.2, y + 1.2), fill=(255, 255, 255, a))
        ell(d, (900, 60, 960, 120), fill=C('fdfbf4'))
        ell(d, (924, 78, 938, 92), fill=C('c9c4ae'))
        city(d, H - 100, [300, 210, 260, 180, 235], lit=True)
        road_and_ground(d)
    elif kind == 'dawn':
        ell(d, (980, 250, 1044, 314), fill=C('ffb84d'))
        city(d, H - 100, [290, 200, 250, 180, 225], lit=False)
        road_and_ground(d)
    elif kind == 'day':
        ell(d, (950, 55, 1014, 119), fill=C('ffe9a8'))
        city(d, H - 100, [260, 310, 210, 270, 235], lit=False)
        road_and_ground(d)
    elif kind == 'dusk':
        ell(d, (840, 360, 904, 424), fill=C('e8854f'))
        city(d, H - 100, [290, 200, 250, 175, 220], lit=True)
        road_and_ground(d)
        for lx in (280, 820):
            d.rectangle([lx * S, (H - 240) * S, (lx + 5) * S, (H - 100) * S], fill=C('4a5262'))
            ell(d, (lx - 8, H - 248, lx + 20, H - 232), fill=C('ffe9a8'))
    return im, d

# ---------- personagem ----------
def draw_char(d, x, y, t, pose='stand', eyes='open', mouth='flat', walking=False, phase=0.0,
              hand_face=False, hold_bar=False, backpack=False, badge=False, back=False):
    """x = centro dos pés, y = linha do chão."""
    if pose == 'lie':
        return
    bounce = -4 * abs(math.sin(phase)) if walking else 0
    hip_y = y - 62 + bounce
    if pose == 'sit':
        hip_y = y - 40 + bounce
    sh_y = hip_y - 52
    head_cy = sh_y - 26
    # sombra
    ell(d, (x - 30, y - 5, x + 30, y + 5), fill=(0, 0, 0, 70))
    # pernas
    for side in (-1, 1):
        if walking:
            fx = x + side * 10 * math.sin(phase + (0 if side < 0 else math.pi))
            fy = y - max(0, 8 * math.sin(phase + (0 if side < 0 else math.pi)))
        elif pose == 'sit':
            fx, fy = x + side * 12, y
        else:
            fx, fy = x + side * 9, y
        line(d, [(x + side * 8, hip_y), (fx, fy - 8)], 11, PANTS)
        rr(d, (fx - 12, fy - 10, fx + 10, fy), 4, fill=SHOE)
    # torso
    rr(d, (x - 25, sh_y - 6, x + 25, hip_y + 8), 12, fill=SHIRT)
    if backpack:
        rr(d, (x - 21, sh_y - 2, x + 21, hip_y + 4), 10, outline=SHIRT_D, width=3 * S)
        line(d, [(x - 14, sh_y - 2), (x - 14, hip_y - 6)], 4, SHIRT_D)
        line(d, [(x + 14, sh_y - 2), (x + 14, hip_y - 6)], 4, SHIRT_D)
    if badge:
        rr(d, (x + 8, sh_y + 6, x + 20, sh_y + 20), 2, fill=WHITE)
        d.rectangle([(x + 12) * S, (sh_y + 8) * S, (x + 16) * S, (sh_y + 11) * S], fill=C('3a7bd5'))
    # braços
    for side in (-1, 1):
        if walking:
            hx = x + side * (26 + 8 * math.sin(phase + (math.pi if side < 0 else 0)))
            hy = hip_y - 14
        elif pose == 'sit':
            hx, hy = x + side * 28, hip_y - 6
        else:
            hx, hy = x + side * 28, hip_y - 12
        if hand_face and side > 0:
            line(d, [(x + side * 22, sh_y + 4), (x + 30, sh_y + 22)], 9, SHIRT_D)
            line(d, [(x + 30, sh_y + 22), (x + 6, head_cy + 16)], 9, SHIRT_D)
            ell(d, (x + 2, head_cy + 12, x + 12, head_cy + 22), fill=SKIN)
            continue
        if hold_bar and side > 0:
            line(d, [(x + side * 22, sh_y + 4), (x + 16, head_cy + 2)], 9, SHIRT_D)
            ell(d, (x + 11, head_cy - 3, x + 21, head_cy + 7), fill=SKIN)
            continue
        line(d, [(x + side * 22, sh_y + 4), (hx, hy)], 9, SHIRT_D)
        ell(d, (hx - 6, hy - 6, hx + 6, hy + 6), fill=SKIN)
    # cabeça
    if back:
        ell(d, (x - 21, head_cy - 23, x + 21, head_cy + 21), fill=SKIN)
        ell(d, (x - 20, head_cy - 22, x + 20, head_cy + 20), fill=HAIR)
        rr(d, (x - 25, sh_y - 6, x + 25, hip_y + 8), 12, fill=SHIRT)
        return
    ell(d, (x - 21, head_cy - 23, x + 21, head_cy + 21), fill=SKIN)
    rr(d, (x - 22, head_cy - 26, x + 22, head_cy - 8), 12, fill=HAIR)
    ell(d, (x - 26, head_cy - 3, x - 19, head_cy + 8), fill=SKIN_D)
    ell(d, (x + 19, head_cy - 3, x + 26, head_cy + 8), fill=SKIN_D)
    # olhos / boca
    blink = eyes == 'open' and (t % 3.1) < 0.12
    for side in (-1, 1):
        if eyes == 'closed' or blink or (side > 0 and eyes == 'one'):
            d.rectangle([(x + side * 9 - 4) * S, (head_cy - 1) * S, (x + side * 9 + 4) * S, (head_cy + 1) * S], fill=C('26211d'))
        else:
            ell(d, (x + side * 9 - 3.5, head_cy - 3.5, x + side * 9 + 3.5, head_cy + 3.5), fill=C('26211d'))
        d.rectangle([(x + side * 9 - 4) * S, (head_cy - 8) * S, (x + side * 9 + 4) * S, (head_cy - 6) * S], fill=HAIR)
    rr(d, (x - 2, head_cy + 1, x + 2, head_cy + 7), 2, fill=SKIN_D)
    ell(d, (x - 16, head_cy + 8, x + 16, head_cy + 22), fill=BEARD)
    rr(d, (x - 20, head_cy + 2, x - 15, head_cy + 14), 4, fill=BEARD)
    rr(d, (x + 15, head_cy + 2, x + 20, head_cy + 14), 4, fill=BEARD)
    if mouth == 'sad':
        d.arc([(x - 7) * S, (head_cy + 8) * S, (x + 7) * S, (head_cy + 18) * S], 180, 360, fill=C('a4552f'), width=int(2.5 * S))
    elif mouth == 'flat':
        d.rectangle([(x - 6) * S, (head_cy + 12) * S, (x + 6) * S, (head_cy + 14) * S], fill=C('a4552f'))
    else:
        d.arc([(x - 7) * S, (head_cy + 4) * S, (x + 7) * S, (head_cy + 16) * S], 0, 180, fill=C('a4552f'), width=int(2.5 * S))

def draw_bed(d, x, y):
    rr(d, (x, y - 66, x + 320, y), 12, fill=C('8a68f2'))
    rr(d, (x, y - 112, x + 26, y), 8, fill=C('5b3fb8'))
    rr(d, (x + 20, y - 62, x + 314, y - 36), 8, fill=C('ded9f5'))
    rr(d, (x + 24, y - 66, x + 116, y - 40), 10, fill=C('ffffff'))
    rr(d, (x + 70, y - 40, x + 320, y), 10, fill=C('f0607f'))
    d.rectangle([(x + 70) * S, (y - 30) * S, (x + 320) * S, (y - 24) * S], fill=(255, 255, 255, 40))

def draw_clock(d, x, y, t, shake=False, calm=False):
    jx = 3 * math.sin(t * 18) if shake else 0
    rr(d, (x + jx, y, x + 130 + jx, y + 62), 8,
       fill=C('16161f'), outline=C('3c3c4e') if calm else RED, width=3 * S)
    txt(d, x + 65 + jx, y + 12, '5:00', F_CLOCK, C('8b93a8') if calm else C('ff5d5d'), anchor='ma')

def draw_bus(d, x, y, body_top, body_bot, metro=False):
    bw, bh = 250, 104
    rr(d, (x, y - bh, x + bw, y), 14, fill=body_top)
    for i in range(3 if not metro else 4):
        wx = x + 14 + i * 74
        rr(d, (wx, y - bh + 16, wx + 60, y - bh + 58), 5, fill=C('9cc9e8'))
    if metro:
        d.rectangle([x * S, (y - bh + 52) * S, (x + bw) * S, (y - bh + 60) * S], fill=YELL)
        ell(d, (x - 4, y - bh + 18, x + 10, y - bh + 32), fill=C('fff7cf'))
    rr(d, (x + bw - 30, y - 56, x + bw - 10, y - 6), 4, fill=C('b8d9ee'))
    for wx in (x + 26, x + bw - 56):
        ell(d, (wx, y - 16, wx + 30, y + 14), fill=C('171717'))
        ell(d, (wx + 9, y - 7, wx + 21, y + 5), fill=C('8a8a8a'))

def draw_coworker(d, x, y, t, skin, shirt):
    ell(d, (x - 24, y - 4, x + 24, y + 4), fill=(0, 0, 0, 50))
    rr(d, (x - 24, y - 92, x + 24, y - 34), 10, fill=shirt)
    sw = 5 * math.sin(t * 9)
    line(d, [(x - 20, y - 82), (x - 30 + sw, y - 46)], 8, shirt)
    line(d, [(x + 20, y - 82), (x + 30 - sw, y - 46)], 8, shirt)
    ell(d, (x - 16, y - 126, x + 16, y - 92), fill=skin)
    rr(d, (x - 17, y - 130, x + 17, y - 114), 8, fill=C('2e2018'))

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        test = (cur + ' ' + w_).strip()
        if f.getlength(test) / S <= maxw:
            cur = test
        else:
            lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

# ---------- legendas ----------
SUBS = [
    (0.6, 4.9, 'NARRADOR', 'Ei, Clóvis! Você está na hora de acordar... já são 5 horas!'),
    (5.5, 7.9, 'CLÓVIS', 'Só mais 5 minutos...'),
    (8.6, 13.9, 'NARRADOR', 'Clóvis! Se você dormir mais 5 minutos, você vai atrasar. Você tem DOIS ônibus e um metrô pra pegar!'),
    (17.6, 22.5, 'NARRADOR', 'E então Clóvis levanta. Arrastando os pés, como sempre.'),
    (23.6, 28.5, 'NARRADOR', 'Clóvis tenta tomar seu café... mas o relógio não perdoa.'),
    (29.6, 33.5, 'NARRADOR', 'E Clóvis NÃO escova os dentes. Mais uma vez.'),
    (34.6, 39.5, 'NARRADOR', 'Lá vem o primeiro ônibus.'),
    (41.6, 46.5, 'NARRADOR', 'Agora o segundo ônibus.'),
    (48.6, 53.5, 'NARRADOR', 'E por fim... o metrô.'),
    (55.6, 60.5, 'NARRADOR', 'Eis que Clóvis chega no trabalho... e ninguém dá um sorriso pra ele.'),
    (61.6, 65.5, 'NARRADOR', 'O dia acaba. E amanhã... a mesma rotina.'),
    (67.0, 73.0, 'NARRADOR', 'Clóvis faz isso todo dia.'),
]

def draw_subtitle(im, t):
    sub = next(((sp, tx) for a, b, sp, tx in SUBS if a <= t <= b), None)
    if not sub:
        return im
    sp, tx = sub
    d = ImageDraw.Draw(im, 'RGBA')
    lines = wrap(tx, F_SUB, 680)
    lh = 30
    box_h = len(lines) * lh + 44
    box_w = max(int(F_SUB.getlength(l) / S) for l in lines) + 60
    bx, by = (W - box_w) / 2, H - box_h - 18
    rr(d, (bx, by, bx + box_w, by + box_h), 10, fill=(10, 12, 20, 200))
    col = YELL if sp == 'NARRADOR' else C('7fe3d0')
    txt(d, W / 2, by + 8, sp, F_SUB_SPK, col, anchor='ma')
    for i, l in enumerate(lines):
        txt(d, W / 2, by + 28 + i * lh, l, F_SUB, WHITE, anchor='ma')
    return im

# ---------- cenas ----------
t_shake = 0.0  # unused

def scene_quarto(t, sitting=False, warning=False):
    im, d = sky_scene('night', t)
    draw_clock(d, 1000, 70, t, shake=(not sitting and not warning and t < 5.0), calm=sitting or warning)
    draw_bed(d, 110, H - 108)
    if sitting:
        draw_char(d, 250, H - 104, t, pose='sit', eyes='open' if warning else 'one', mouth='sad')
    else:
        # deitado: cabeça no travesseiro + coberta
        ell(d, (196, H - 186, 252, H - 140), fill=SKIN)
        rr(d, (194, H - 192, 254, H - 172), 9, fill=HAIR)
        d.rectangle([214 * S, (H - 168) * S, 226 * S, (H - 164) * S], fill=C('26211d'))
        d.rectangle([234 * S, (H - 168) * S, 246 * S, (H - 164) * S], fill=C('26211d'))
        for k, (zx, zy, dl) in enumerate([(300, H - 260, 0.0), (330, H - 290, 0.9), (285, H - 315, 1.7)]):
            ph = (t + dl) % 2.6
            a = int(220 * (1 - ph / 2.6))
            txt(d, zx, zy - ph * 22, 'Z', font(20, bold=True), (207, 216, 255, a))
    return im

def scene_rua(t, kind, char_x=None, walking=False, mouth='flat', bus_x=None, bus_color=None):
    im, d = sky_scene(kind, t)
    if kind == 'dawn':
        d.rectangle([150 * S, (H - 260) * S, 158 * S, (H - 100) * S], fill=C('7c8698'))
        rr(d, (108, H - 292, 204, H - 258), 5, fill=C('f5c95d'))
        txt(d, 156, H - 287, 'ÔNIBUS', F_SIGN, C('4a3b12'), anchor='ma')
    gy = H - 100
    if bus_x is not None and bus_x < 1350:
        c1, c2 = bus_color if bus_color else (C('f28268'), C('dd5f42'))
        draw_bus(d, bus_x, gy + 66, c1, c2)
    if char_x is not None:
        draw_char(d, char_x, gy + 62, t, pose='stand', eyes='open', mouth=mouth, walking=walking,
                  phase=t * 11)
    return im

def scene_kitchen(t):
    im, d = sky_scene('ind', t)
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('4a4258'))
    rr(d, (108, H - 190, 232, H - 96), 10, fill=C('cfe7fb'), outline=C('7d5f3e'), width=6 * S)
    rr(d, (430, H - 152, 700, H - 138), 4, fill=C('9c7a52'))
    for px in (448, 668):
        d.rectangle([px * S, (H - 138) * S, (px + 10) * S, (H - 74) * S], fill=C('66502f'))
    rr(d, (508, H - 178, 536, H - 152), 6, fill=C('f0607f'))
    for k in range(2):
        ph = (t + k * 0.8) % 2.2
        a = int(70 * (1 - ph / 2.2))
        ell(d, (518 + k * 8, H - 196 - ph * 26, 526 + k * 8, H - 182 - ph * 26), fill=(255, 255, 255, a))
    rr(d, (576, H - 172, 620, H - 152), 8, fill=C('e0aa63'))
    draw_char(d, 330, H - 96, t, pose='sit', eyes='open', mouth='flat')
    return im

def scene_bathroom(t, char_x=None):
    im, d = sky_scene('ind', t)
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('4a4258'))
    rr(d, (130, H - 330, 290, H - 218), 10, fill=C('cfe7fb'), outline=C('7d5f3e'), width=6 * S)
    rr(d, (900, H - 210, 1120, H - 150), 10, fill=C('ececec'))
    rr(d, (960, H - 236, 976, H - 208), 4, fill=C('c0c0c0'))
    d.rectangle([940 * S, (H - 262) * S, 996 * S, (H - 256) * S], fill=C('0dc9a0'))
    d.rectangle([928 * S, (H - 262) * S, 940 * S, (H - 259) * S], fill=WHITE)
    if char_x is not None:
        draw_char(d, char_x, H - 96, t, pose='stand', eyes='open', mouth='flat', walking=True, phase=t * 11)
    return im

def scene_office(t, char_x=None):
    im, d = sky_scene('ind', t)
    d.rectangle([0, (H - 100) * S, W * S, H * S], fill=C('6a6f7d'))
    for dx, skin, shirt in ((150, C('c9ada7'), C('457b9d')), (560, C('e8c39e'), C('6d597a')), (960, C('b5838d'), C('355070'))):
        rr(d, (dx - 100, H - 152, dx + 100, H - 138), 3, fill=C('9c7a52'))
        rr(d, (dx - 24, H - 192, dx + 24, H - 158), 4, fill=C('22283a'))
        draw_coworker(d, dx, H - 138, t, skin, shirt)
    if char_x is not None:
        draw_char(d, char_x, H - 96, t, pose='stand', eyes='open', mouth='sad', walking=True, phase=t * 11)
    return im

def scene_week(t):
    im = gradient((C('12151f'), C('1a2030')))
    d = ImageDraw.Draw(im, 'RGBA')
    txt(d, W / 2, 60, 'E Clóvis faz isso todo. Santo. Dia.', F_TITLE, YELL, anchor='ma')
    days = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    cw, gap = 210, 22
    total = 5 * cw + 4 * gap
    x0 = (W - total) / 2
    for i, day in enumerate(days):
        x = x0 + i * (cw + gap)
        y, ch = 150, 470
        active = t >= 1.0 + i * 0.7
        done = t >= 1.4 + i * 0.7
        rr(d, (x, y, x + cw, y + ch), 12, fill=C('202b44'),
           outline=YELL if active else C('35446a'), width=4 * S)
        rr(d, (x + 4, y + 4, x + cw - 4, y + ch - 4), 10, fill=C('26365f'))
        rr(d, (x + 24, y + ch - 70, x + 118, y + ch - 30), 5, fill=C('7f5af0'))
        gy = y + ch - 60
        ell(d, (x + cw - 62, gy - 30, x + cw - 34, gy - 2), fill=SKIN)
        rr(d, (x + cw - 64, gy - 2, x + cw - 32, gy + 44), 6, fill=SHIRT)
        rr(d, (x + cw - 52, y + 90, x + cw - 12, y + 118), 4, fill=C('16161f'), outline=RED, width=2 * S)
        txt(d, x + cw - 32, y + 96, '5:00', font(11, bold=True), C('ff5d5d'), anchor='ma')
        rr(d, (x, y, x + cw, y + 34), 10, fill=C('c73e5e'))
        txt(d, x + cw / 2, y + 5, day, F_DAY, WHITE, anchor='ma')
        if done:
            txt(d, x + cw - 30, y + ch - 46, '✔', F_CHECK, C('0dc9a0'), anchor='ma')
    return im

CROSS = 0.6
def scene_at(idx, t):
    if idx == 0:  return scene_quarto(t, sitting=False)
    if idx == 1:  return scene_quarto(t, sitting=True)
    if idx == 2:  return scene_quarto(t, sitting=True, warning=True)
    if idx == 3:
        cx = 200 + min(1, max(0, (t - 0.7) / 3.6)) * 700
        return scene_rua(t, 'dawn', char_x=cx, walking=(t < 4.3))
    if idx == 4:  return scene_kitchen(t)
    if idx == 5:  return scene_bathroom(t, char_x=180 + min(1, max(0, (t - 0.6) / 2.4)) * 380)
    if idx in (6, 7, 8):
        if t < 2.6:
            bx = -300 + (t / 2.6) * 480
        elif t < 5.0:
            bx = 180
        else:
            bx = 180 + ((t - 5.0) / 2.0) * 1300
        if idx == 6:
            return scene_rua(t, 'dawn', char_x=None if t >= 5.0 else 380 + min(1, max(0, (t - 2.6) / 1.6)) * 90,
                             walking=(2.6 <= t < 4.2), bus_x=bx,
                             bus_color=(C('f28268'), C('dd5f42')))
        if idx == 7:
            return scene_rua(t, 'day', char_x=None if t >= 5.0 else 400 + min(1, max(0, (t - 2.6) / 1.6)) * 90,
                             walking=(2.6 <= t < 4.2), bus_x=bx,
                             bus_color=(C('9fd4ee'), C('6fb3d6')))
        im, d = sky_scene('night', t)
        for lx in range(60, W, 180):
            d.rectangle([lx * S, 60 * S, (lx + 6) * S, 74 * S], fill=(255, 209, 102, 70))
        d.rectangle([0, (H - 130) * S, W * S, H * S], fill=C('3a3f4d'))
        d.rectangle([0, (H - 96) * S, W * S, (H - 60) * S], fill=C('272e3d'))
        draw_bus(d, bx, H - 40, C('2ba3cc'), C('1b7fa3'), metro=True)
        if t < 5.0:
            draw_char(d, 420 + min(1, max(0, (t - 2.6) / 1.6)) * 90, H - 62, t,
                      pose='stand', eyes='open', mouth='flat', walking=(2.6 <= t < 4.2), phase=t * 11)
        return im
    if idx == 9:  return scene_office(t, char_x=60 + min(1, max(0, (t - 0.6) / 2.4)) * 200)
    if idx == 10:
        cx = 120 + min(1, max(0, (t - 0.6) / 3.6)) * 780
        return scene_rua(t, 'dusk', char_x=cx, walking=True, mouth='sad')
    return scene_week(t)

SCENE_TIMES = [(0, 8), (8, 14), (14, 17), (17, 23), (23, 29), (29, 34), (34, 41),
               (41, 48), (48, 55), (55, 61), (61, 66), (66, 74)]

def render_frame(t):
    for i, (a, b) in enumerate(SCENE_TIMES):
        if a <= t < b:
            img = scene_at(i, t - a)
            if img.size != (W * S, H * S):
                img = img.resize((W * S, H * S), Image.LANCZOS)
            if b - t < CROSS and i + 1 < len(SCENE_TIMES):
                nxt = scene_at(i + 1, 0.0)
                if nxt.size != img.size:
                    nxt = nxt.resize(img.size, Image.LANCZOS)
                if nxt.mode != img.mode:
                    nxt = nxt.convert(img.mode)
                img = Image.blend(img, nxt, (t - (b - CROSS)) / CROSS)
            return img
    return scene_week(t - SCENE_TIMES[-1][0])

def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
           '-s', f'{W}x{H}', '-pix_fmt', 'rgb24', '-r', str(FPS), '-i', '-',
           '-an', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23',
           '-preset', 'medium', '-movflags', '+faststart', OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    total = int(DUR * FPS)
    for n in range(total):
        t = n / FPS
        img = draw_subtitle(render_frame(t), t)
        img = img.resize((W, H), Image.LANCZOS).convert('RGB')
        proc.stdin.write(img.tobytes())
        if n % 120 == 0:
            print(f'{n}/{total} frames ({t:.1f}s)', flush=True)
    proc.stdin.close()
    proc.wait()
    print('OK:', OUT)

if __name__ == '__main__':
    main()
