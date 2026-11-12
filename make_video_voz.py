#!/usr/bin/env python3
"""Gera o vídeo do Clóvis COM NARRAÇÃO: TTS -> timeline dinâmica -> render -> mux."""
import subprocess, wave, os, sys, asyncio
import numpy as np
import imageio_ffmpeg
import edge_tts
import render_video as r
import scenes_v2

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 24000
TMP = '/tmp/tts'
VOZ_NARRADOR = 'pt-BR-AntonioNeural'
VOZ_CLOVIS   = 'pt-BR-AntonioNeural'
CLV_RATE  = '+12%'
CLV_PITCH = '+30Hz'
NAR_RATE  = '-4%'

LINES = [
    dict(sid=0,  sp='NARRADOR', text='Ei, Cláudio! Você está na hora de acordar... já são 5 horas!'),
    dict(sid=0,  sp='CLÁUDIO',  text='Só mais 5 minutos...'),
    dict(sid=1,  sp='NARRADOR', text='Cláudio! Se você dormir mais 5 minutos, você vai atrasar. Você tem DOIS ônibus e um metrô pra pegar!'),
    dict(sid=3,  sp='NARRADOR', text='E então Cláudio levanta. Arrastando os pés, como sempre.'),
    dict(sid=4,  sp='NARRADOR', text='Cláudio tenta tomar seu café... mas o relógio não perdoa.'),
    dict(sid=5,  sp='NARRADOR', text='E Cláudio NÃO escova os dentes. Mais uma vez.'),
    dict(sid=6,  sp='NARRADOR', text='Lá vem o primeiro ônibus.'),
    dict(sid=7,  sp='NARRADOR', text='Dentro do primeiro ônibus, a placa diz: foco, força e fé. Cláudio só pensa em dormir.'),
    dict(sid=8,  sp='NARRADOR', text='Agora o segundo ônibus.'),
    dict(sid=9,  sp='NARRADOR', text='No segundo, nem sentar ele consegue. Em pé, segurando a barra, rumo ao metrô.'),
    dict(sid=10, sp='NARRADOR', text='E por fim... o metrô.'),
    dict(sid=11, sp='NARRADOR', text='Eis que Cláudio chega no trabalho... e ninguém dá um sorriso pra ele.'),
    dict(sid=12, sp='NARRADOR', text='O dia acaba. E amanhã... a mesma rotina.'),
    dict(sid=13, sp='NARRADOR', text='Em casa, a TV pergunta: fim da escala 6x1? Cláudio só sonha em ter mais tempo com a família.'),
    dict(sid=14, sp='NARRADOR', text='Cláudio faz isso todo dia.'),
]

MIN_DUR = {0: 6.0, 1: 5.0, 2: 2.5, 3: 5.0, 4: 5.0, 5: 5.0, 6: 7.2, 7: 6.0, 8: 7.2, 9: 6.0,
           10: 7.2, 11: 6.5, 12: 5.0, 13: 7.0, 14: 8.0}
TAIL = {0: 0.6, 1: 0.9, 3: 0.7, 4: 0.7, 5: 0.7, 6: 2.2, 7: 1.2, 8: 2.2, 9: 1.2, 10: 2.2,
        11: 1.2, 12: 0.7, 13: 1.2, 14: 1.5}

async def _tts(text, out, voice, rate, pitch):
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await com.save(out)

async def synth_all_async():
    os.makedirs(TMP, exist_ok=True)
    for i, ln in enumerate(LINES):
        mp3 = f'{TMP}/l{i}.mp3'
        wav = f'{TMP}/l{i}.wav'
        if not os.path.exists(wav):
            if ln['sp'] == 'CLÓVIS':
                await _tts(ln['text'], mp3, VOZ_CLOVIS, CLV_RATE, CLV_PITCH)
            else:
                await _tts(ln['text'], mp3, VOZ_NARRADOR, NAR_RATE, '+0Hz')
            subprocess.run([FF, '-y', '-i', mp3, '-ar', str(SR), '-ac', '1',
                            '-f', 's16le', wav], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raw = open(wav, 'rb').read()
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        dur = len(samples) / SR
        ln['dur'] = dur
        ln['samples'] = samples
        print(f"  fala {i:2d} ({ln['sp']:8s}) {dur:4.1f}s: {ln['text'][:50]}")

def synth_all():
    asyncio.run(synth_all_async())

def build_schedule():
    scene_dur = {}
    for i in range(15):
        scene_dur[i] = MIN_DUR[i]
    for ln in LINES:
        sid = ln['sid']
        off = 1.0 if sid == 14 else 0.6
        if sid == 0 and ln['sp'] == 'CLÓVIS':
            off = 0.6 + LINES[0]['dur'] + 0.7
        need = off + ln['dur'] + TAIL.get(sid, 0.7)
        scene_dur[sid] = max(scene_dur[sid], need)
    starts = {}
    t = 0.0
    for i in range(15):
        starts[i] = t
        t += scene_dur[i]
    total = t
    subs = []
    audio = np.zeros(int(total * SR) + SR)
    for ln in LINES:
        sid = ln['sid']
        off = 1.0 if sid == 14 else 0.6
        if sid == 0 and ln['sp'] == 'CLÓVIS':
            off = 0.6 + LINES[0]['dur'] + 0.7
        st = starts[sid] + off
        subs.append((st, st + ln['dur'] + 0.4, ln['sp'], ln['text']))
        i0 = int(st * SR)
        audio[i0:i0 + len(ln['samples'])] += ln['samples'] * 0.95
    scene_times = [(starts[i], starts[i] + scene_dur[i]) for i in range(15)]
    return scene_times, subs, audio, total

def main():
    print('1/4 Sintetizando falas (Edge TTS pt-BR)...')
    synth_all()
    print('2/4 Montando timeline...')
    scene_times, subs, audio, total = build_schedule()
    for i, (a, b) in enumerate(scene_times):
        print(f'  cena {i:2d}: {a:5.1f}s -> {b:5.1f}s')
    r.SCENE_TIMES = scene_times
    r.SUBS = subs
    r.DUR = total
    r.scene_at = scenes_v2.scene_at_v3
    r.OUT = '/tmp/clovis_mudo.mp4'
    print('3/4 Renderizando vídeo...')
    r.main()
    wav_path = '/tmp/clovis_narracao.wav'
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(wav_path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    out = sys.argv[1] if len(sys.argv) > 1 else 'clovis-com-voz.mp4'
    print('4/4 Misturando áudio + vídeo...')
    subprocess.run([FF, '-y', '-i', r.OUT, '-i', wav_path,
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                    '-shortest', out], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('OK:', out)

if __name__ == '__main__':
    main()
