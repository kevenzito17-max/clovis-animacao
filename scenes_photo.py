#!/usr/bin/env python3
"""Cenas com a arte do usuário: foto como cenário completo + zoom lento (Ken Burns)."""
import os
from PIL import Image, ImageFilter, ImageEnhance
import render_video as r
import scenes_v2

W, H, S = r.W, r.H, r.S
PHOTO_DIR = os.environ.get('FOTOS_DIR', 'assets/fotos')
PHOTO_FILES = {
    1: '01_quarto_sentado.jpg',
    2: '02_cafe.jpg',
    3: '03_banheiro.jpg',
    4: '04_correndo_ponto.jpg',
    5: '05_onibus1.jpg',
    6: '06_onibus2.jpg',
    7: '07_metro.jpg',
    8: '08_trabalho.jpg',
}
_photos = {}

def load_photos():
    if not _photos:
        for k, f in PHOTO_FILES.items():
            p = os.path.join(PHOTO_DIR, f)
            if os.path.exists(p):
                _photos[k] = Image.open(p).convert('RGB')
    return _photos

def photo_scene(idx, t, dur):
    photos = load_photos()
    img = photos[idx]
    bg = img.resize((int(H * 2.2), int(H * 2.2 * img.height / img.width)), Image.LANCZOS)
    bw = bg.width
    bg = bg.crop(((bw - int(H * 16 / 9)) // 2, 0, (bw - int(H * 16 / 9)) // 2 + int(H * 16 / 9), H * 2))
    bg = bg.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(16))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)
    z = 1.0 + 0.07 * min(1.0, t / max(dur, 0.1))
    fh = int(H * z)
    fw = int(fh * img.width / img.height)
    fg = img.resize((fw, fh), Image.LANCZOS)
    cw, ch = min(fw, W), min(fh, H)
    left, top = (fw - cw) // 2, (fh - ch) // 2
    canvas = bg.copy()
    canvas.paste(fg.crop((left, top, left + cw, top + ch)), ((W - cw) // 2, (H - ch) // 2))
    return canvas

# cenas com foto: 1..8 | desenhadas: 0 quarto, 9 volta, 10 tv, 11 semana
PHOTO_SCENES = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}

def scene_at_photo(idx, t):
    times = r.SCENE_TIMES
    a, b = times[idx]
    dur = b - a
    if idx in PHOTO_SCENES:
        return photo_scene(PHOTO_SCENES[idx], t, dur)
    if idx == 0:
        return scenes_v2.quarto_v2(t, sitting=False)
    if idx == 9:
        cx = 120 + min(1, max(0, (t - 0.6) / 3.6)) * 780
        return scenes_v2.dusk_v2(t, char_x=cx, backpack=True)
    if idx == 10:
        return scenes_v2.tv_scene(t)
    return r.scene_week(t)
