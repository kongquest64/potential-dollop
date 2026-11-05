#!/usr/bin/env python3
"""Build the narrated explainer video.

Steps
  1. tts    – synthesize every narration sentence (edge-tts neural voice), cached
  2. audio  – stitch voice + generated ambient music bed, write captions (.srt)
  3. video  – render animated motion-graphics frames, pipe into ffmpeg

Usage: python3 build.py [--preview SCENE_ID] [--stills]
"""
import argparse
import asyncio
import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Project settings; overridden by load_project() from the project's scenes.py
SCENES = []
PROJECT = None
SLUG = "why_hasnt_nintendo_died"
SERIES = "WHY HASN'T NINTENDO DIED?"
MUSIC = "pad"
OUT = os.path.join(ROOT, "output")
CACHE = os.path.join(HERE, ".cache")
VOICE = "en-US-AndrewNeural"
RATE = "+2%"
SR = 48000
W, H, FPS = 1920, 1080, 30
SENT_GAP = 0.28   # silence between sentences
SCENE_GAP = 0.75  # silence after each scene
CHAPTER_EXTRA = 0.6

# ----------------------------------------------------------------- text utils
ABBREV = ["R.O.B.", "Bros.", "U.S."]


def split_sentences(text):
    if not text.strip():
        return []
    protected = text
    for i, a in enumerate(ABBREV):
        protected = protected.replace(a, f"@@{i}@@")
    parts = re.split(r"(?<=[.?!])\s+", protected.strip())
    out = []
    for p in parts:
        for i, a in enumerate(ABBREV):
            p = p.replace(f"@@{i}@@", a)
        out.append(p)
    return out


# ----------------------------------------------------------------- 1. TTS
async def _synth(text, path):
    import certifi
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"  # agent proxy CA
    import edge_tts
    for attempt in range(5):
        try:
            c = edge_tts.Communicate(text, VOICE, rate=RATE, proxy=os.environ.get("HTTPS_PROXY"))
            await c.save(path + ".tmp")
            os.replace(path + ".tmp", path)
            return
        except Exception as e:  # network hiccups
            print("  retry", attempt, e)
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError("TTS failed: " + text)


def tts_all():
    os.makedirs(CACHE, exist_ok=True)
    jobs = []
    for sc in SCENES:
        for i, s in enumerate(split_sentences(sc["text"])):
            jobs.append((s, sentence_path(sc["id"], i, s)))
    todo = [j for j in jobs if not os.path.exists(j[1])]
    print(f"TTS: {len(jobs)} sentences, {len(todo)} to synthesize")

    async def run():
        sem = asyncio.Semaphore(6)

        async def one(s, p):
            async with sem:
                await _synth(s, p)
        await asyncio.gather(*(one(s, p) for s, p in todo))
    if todo:
        asyncio.run(run())


def sentence_path(sc_id, i, s):
    import hashlib
    h = hashlib.sha1(f"{s}|{VOICE}|{RATE}".encode()).hexdigest()[:10]
    return os.path.join(CACHE, f"{sc_id}_{i:02d}_{h}.mp3")


def decode(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).copy()
    # trim leading/trailing near-silence so our own gaps control pacing
    thr = 0.01
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx):
        a = a[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]
    return a


# ----------------------------------------------------------------- 2. AUDIO
def build_timeline():
    """Returns per-scene timing and the voice track."""
    voice = []
    t = 0.6  # short lead-in
    voice.append(np.zeros(int(t * SR), np.float32))
    timeline = []
    captions = []
    for sc in SCENES:
        sents = split_sentences(sc["text"])
        start = t
        cues = Cues()
        cues.sents = sents
        if not sents:  # silent scene (title / chapter card)
            hold = sc.get("hold", 2.5)
            voice.append(np.zeros(int(hold * SR), np.float32))
            t += hold
            timeline.append(dict(scene=sc, start=start, dur=hold, cues=cues))
            continue
        for i, s in enumerate(sents):
            a = decode(sentence_path(sc["id"], i, s))
            cues.append((t - start, t - start + len(a) / SR))
            captions.append((t, t + len(a) / SR, s))
            voice.append(a)
            t += len(a) / SR
            gap = SENT_GAP if i < len(sents) - 1 else SCENE_GAP
            if i == len(sents) - 1 and sc["visual"]["type"] == "chapter":
                gap += CHAPTER_EXTRA
            voice.append(np.zeros(int(gap * SR), np.float32))
            t += gap
        timeline.append(dict(scene=sc, start=start, dur=t - start, cues=cues))
    voice.append(np.zeros(int(1.5 * SR), np.float32))
    v = np.concatenate(voice)
    return timeline, v


def music_bed(n):
    """Warm, slow ambient pad: Fmaj7 – C/E – Am7 – G, 8 s per chord."""
    tt = np.arange(n) / SR
    chords = [
        [41, 48, 52, 57, 64],   # F2 C3 E3 A3 E4
        [40, 48, 55, 60, 67],   # E2 C3 G3 C4 G4
        [45, 52, 55, 60, 67],   # A2 E3 G3 C4 G4
        [43, 50, 55, 59, 62],   # G2 D3 G3 B3 D4
    ]
    seg = 8.0
    out = np.zeros(n, np.float32)
    nseg = int(math.ceil(n / SR / seg)) + 1
    xf = 2.5  # crossfade seconds
    for k in range(nseg):
        s0 = int(max(0, (k * seg - xf) * SR))
        s1 = int(min(n, ((k + 1) * seg + xf) * SR))
        if s0 >= n:
            break
        ts = tt[s0:s1]
        local = ts - k * seg
        env = np.clip((local + xf) / xf, 0, 1) * np.clip((seg + xf - local) / xf, 0, 1)
        env = np.sin(env * math.pi / 2) ** 2
        sig = np.zeros_like(ts)
        for j, m in enumerate(chords[k % 4]):
            f = 440 * 2 ** ((m - 69) / 12)
            amp = 0.5 if j == 0 else 0.28
            for det in (-0.12, 0.12):
                ff = f * 2 ** (det / 12 / 8)
                sig += amp * np.sin(2 * math.pi * ff * ts + j) * (0.85 + 0.15 * np.sin(2 * math.pi * 0.07 * ts + j))
                sig += amp * 0.18 * np.sin(2 * math.pi * 2 * ff * ts)
        out[s0:s1] += (sig * env).astype(np.float32)
    # gentle sparkle: soft high bell every 4 s on chord tones
    out /= np.max(np.abs(out)) + 1e-9
    fade = np.minimum(1, np.minimum(tt / 4, (tt[-1] - tt) / 5))
    return out * fade


def write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def fmt_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path, captions):
    lines = []
    n = 1
    for (a, b, text) in captions:
        words = text.split()
        # split long sentences into ~12-word chunks, timed proportionally by characters
        chunks, cur = [], []
        for w_ in words:
            cur.append(w_)
            if len(cur) >= 12 or (len(cur) >= 6 and w_.endswith((",", ";", ":"))):
                chunks.append(" ".join(cur)); cur = []
        if cur:
            if chunks and len(cur) < 4:
                chunks[-1] += " " + " ".join(cur)  # avoid orphan words
            else:
                chunks.append(" ".join(cur))
        total = sum(len(c) for c in chunks)
        t = a
        for c in chunks:
            d = (b - a) * len(c) / total
            lines += [str(n), f"{fmt_srt(t)} --> {fmt_srt(t + d)}", c, ""]
            n += 1
            t += d
    with open(path, "w") as f:
        f.write("\n".join(lines))


# ----------------------------------------------------------------- 3. VIDEO
FD = "/usr/share/fonts/opentype/inter/"
_fonts = {}


def F(name, size):
    k = (name, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FD + name + ".otf", size)
    return _fonts[k]


BG = (13, 17, 28)
FG = (242, 243, 247)
MUTED = (140, 150, 172)
FAINT = (52, 60, 82)
RED = (232, 36, 48)
GOLD = (255, 196, 64)
SLATE = (84, 98, 130)


def blend(c, a, base=BG):
    return tuple(int(base[i] + (c[i] - base[i]) * a) for i in range(3))


def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def make_bg(glow=(1500, 160), strength=0.16, chapter=False, color=RED):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = BG
    # vertical vignette
    v = 1 - 0.35 * ((yy / H - 0.45) ** 2)
    base *= v[..., None]
    gx, gy = glow
    d = np.sqrt((xx - gx) ** 2 + (yy - gy) ** 2)
    g = np.exp(-(d / (900 if not chapter else 1100)) ** 2) * strength
    base += g[..., None] * np.array(color, np.float32)
    # second cool glow
    d2 = np.sqrt((xx - 200) ** 2 + (yy - 1000) ** 2)
    base += (np.exp(-(d2 / 800) ** 2) * 0.10)[..., None] * np.array([60, 90, 200], np.float32)
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d_ = ImageDraw.Draw(img)
    # subtle dot grid
    for y in range(30, H, 48):
        for x in range(30, W, 48):
            d_.point((x, y), fill=(34, 40, 58))
    return img


def text_w(font, s):
    return font.getlength(s)


def wrap(s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(font, t) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


class El:
    """An animated element: appears at `t0`, animates for `dur` seconds."""

    def __init__(self, t0, fn, dur=0.55):
        self.t0, self.fn, self.dur = t0, fn, dur

    def p(self, t):
        return max(0.0, min(1.0, (t - self.t0) / self.dur))


class Cues(list):
    """Sentence (start, end) times within a scene, plus the sentence texts."""
    sents = ()


def cue(cues, s, frac=0.0):
    """Time at which sentence `s` starts; `s` is an index or a substring of the sentence."""
    if s is None or not cues:
        return 1.0 + frac
    if isinstance(s, str):
        key = s.lower()
        for i, t in enumerate(cues.sents):
            if key in t.lower():
                s = i
                break
        else:
            raise ValueError(f"cue text not found: {s!r} in {cues.sents}")
    s = max(0, min(s, len(cues) - 1))
    a, b = cues[s]
    return a + (b - a) * frac


def txt(d, xy, s, font, color, a, anchor="la", dy=24):
    if a <= 0:
        return
    x, y = xy
    d.text((x, y + (1 - ease(a)) * dy), s, font=font, fill=blend(color, ease(a)), anchor=anchor)


# ---- visual builders: return list[El]
def v_hero(v, cues, dur):
    els = []
    els.append(El(0.0, lambda d, p: txt(d, (W / 2, 330), v["kicker"], F("Inter-SemiBold", 34), RED, p, "mm")))
    tb = cue(cues, v["s_big"])
    els.append(El(tb, lambda d, p: txt(d, (W / 2, 520), v["big"], F("InterDisplay-Black", 230), FG, p, "mm", 40), 0.7))

    def bar(d, p):
        e = ease(p)
        if e > 0:
            w_ = 220 * e
            d.rectangle((W / 2 - w_, 668, W / 2 + w_, 676), fill=RED)
    els.append(El(tb + 0.25, bar, 0.6))
    els.append(El(tb + 0.45, lambda d, p: txt(d, (W / 2, 740), v["sub"], F("Inter-Medium", 46), MUTED, p, "mm")))
    return els


def v_graveyard(v, cues, dur):
    els = []
    names = v["names"]
    a, b = cues[v["s_names"]]
    step = (b - a) / len(names)
    cols, cw, rh = 4, 380, 120
    x0 = W / 2 - cols * cw / 2 + cw / 2
    y0 = 330
    ts = cue(cues, v["s_strike"])
    fnt = F("InterDisplay-Bold", 64)
    for i, n in enumerate(names):
        cx = x0 + (i % cols) * cw
        cy = y0 + (i // cols) * rh

        def draw_name(d, p, n=n, cx=cx, cy=cy):
            txt(d, (cx, cy), n, fnt, FG, p, "mm")
        els.append(El(cue(cues, v["s_names"] + i), draw_name, 0.45))

        def strike(d, p, n=n, cx=cx, cy=cy):
            e = ease(p)
            if e <= 0:
                return
            # dim the name
            d.text((cx, cy), n, font=fnt, fill=blend(FAINT, 1, blend(FG, 1 - e * 0.75)), anchor="mm")
            wn = text_w(fnt, n) / 2 + 14
            d.line((cx - wn, cy, cx - wn + 2 * wn * e, cy), fill=RED, width=7)
        els.append(El(ts + i * 0.12, strike, 0.45))
    tv = cue(cues, v["s_survivor"])

    def surv(d, p):
        e = ease(p)
        if e <= 0:
            return
        f = F("InterDisplay-Black", 120)
        d.text((W / 2, 690 + (1 - e) * 40), v["survivor"], font=f, fill=blend(RED, e), anchor="mm")
        txt(d, (W / 2, 790), "still here", F("Inter-Medium", 40), MUTED, p, "mm")
    els.append(El(tv, surv, 0.7))
    return els


def v_title(v, cues, dur):
    els = []
    f = F("InterDisplay-Black", 118)
    lines = wrap(v["title"], f, W - 300)
    n = len(lines)

    def title(d, p):
        for i, ln in enumerate(lines):
            txt(d, (W / 2, 470 - (n - 1) * 66 + i * 132), ln, f, FG, p, "mm", 40)
    els.append(El(0.05, title, 0.8))

    def rule(d, p):
        e = ease(p)
        if e > 0:
            d.rectangle((W / 2 - 90 * e, 590, W / 2 + 90 * e, 598), fill=RED)
    els.append(El(0.4, rule, 0.6))
    els.append(El(cue(cues, v["s_sub"]), lambda d, p: txt(d, (W / 2, 670), v["sub"], F("Inter-Medium", 50), MUTED, p, "mm")))
    return els


def v_chapter(v, cues, dur):
    els = []
    x = 240
    els.append(El(0.0, lambda d, p: txt(d, (x, 300), v.get("label", "PART"), F("Inter-Bold", 36), MUTED, p)))
    els.append(El(0.08, lambda d, p: txt(d, (x - 8, 340), v["num"], F("InterDisplay-Black", 220), RED, p, "la", 50), 0.7))
    tf = F("InterDisplay-Bold", 88)
    lines = wrap(v["title"], tf, W - 2 * x)

    def title(d, p):
        for i, ln in enumerate(lines):
            txt(d, (x, 610 + i * 100), ln, tf, FG, p, "la", 30)
    els.append(El(0.3, title, 0.7))
    ys = 610 + len(lines) * 100 + 30
    els.append(El(0.6, lambda d, p: txt(d, (x, ys), v["sub"], F("Inter-Medium", 44), MUTED, p)))
    return els


def v_statement(v, cues, dur):
    els = []
    f = F("InterDisplay-Bold", 92 if "text2" not in v else 76)
    lines = wrap(v["text"], f, W - 360)
    lh = f.size * 1.18
    has2 = "text2" in v or "small" in v
    top = 540 - (len(lines) * lh) / 2 - (90 if has2 else 0)

    def main(d, p):
        for i, ln in enumerate(lines):
            txt(d, (W / 2, top + i * lh + lh / 2), ln, f, FG if "text2" not in v else MUTED, p, "mm", 30)
    els.append(El(cue(cues, v.get("s_text", 0)) if v.get("s_text", 0) else 0.05, main, 0.7))
    yb = top + len(lines) * lh + 50
    if "text2" in v:
        f2 = F("InterDisplay-Bold", 76)
        l2 = wrap(v["text2"], f2, W - 360)

        def second(d, p):
            for i, ln in enumerate(l2):
                txt(d, (W / 2, yb + 40 + i * f2.size * 1.18), ln, f2, FG, p, "mm", 30)
            e = ease(p)
            if e > 0:
                d.rectangle((W / 2 - 70 * e, yb - 14, W / 2 + 70 * e, yb - 8), fill=RED)
        els.append(El(cue(cues, v["s_text2"]), second, 0.7))
    if "small" in v:
        def small(d, p):
            e = ease(p)
            if e > 0:
                d.rectangle((W / 2 - 70 * e, yb - 14, W / 2 + 70 * e, yb - 8), fill=RED)
            txt(d, (W / 2, yb + 50), v["small"], F("Inter-Medium", 48), RED if False else MUTED, p, "mm")
        els.append(El(cue(cues, v["s_small"]), small, 0.6))
    return els


def heading(els, text, y=150):
    els.append(El(0.0, lambda d, p: txt(d, (200, y), text, F("InterDisplay-Bold", 68), FG, p)))

    def rule(d, p):
        e = ease(p)
        if e > 0:
            d.rectangle((200, y + 96, 200 + 120 * e, y + 104), fill=RED)
    els.append(El(0.2, rule, 0.5))


def stagger(items, cues, gap=0.4):
    seen = {}
    out = []
    for it in items:
        s = it.get("s", 0)
        k = seen.get(s, 0)
        seen[s] = k + 1
        out.append(cue(cues, s) + k * gap if s or k else 0.35 + k * gap)
    return out


def v_timeline(v, cues, dur):
    els = []
    heading(els, v["heading"])
    items = v["items"]
    ys = 330
    gap = min(140, 620 / max(1, len(items)))
    lx = 240
    t0s = stagger(items, cues, 0.5)
    last = ys + gap * (len(items) - 1)

    def line(d, p):
        e = ease(p)
        if e > 0:
            d.line((lx, ys, lx, ys + (last - ys) * e), fill=FAINT, width=4)
    els.append(El(0.2, line, max(0.6, (t0s[-1] if t0s else 1))))
    for i, (it, t0) in enumerate(zip(items, t0s)):
        y = ys + i * gap

        def item(d, p, it=it, y=y):
            e = ease(p)
            if e <= 0:
                return
            r = 14 * e
            d.ellipse((lx - r, y - r, lx + r, y + r), fill=RED if it["year"] else MUTED)
            if it["year"]:
                txt(d, (lx + 50, y), it["year"], F("InterDisplay-Bold", 52), RED, p, "lm", 0)
            txt(d, (lx + 280, y), it["text"], F("Inter-Medium", 46), FG, p, "lm", 0)
        els.append(El(t0, item, 0.55))
    return els


def v_list(v, cues, dur):
    els = []
    heading(els, v["heading"])
    items = v["items"]
    cols = v.get("columns", 1)
    t0s = stagger(items, cues, 0.4)
    y0 = 360
    if "pre" in v:
        pre = v["pre"]

        def pre_fn(d, p):
            txt(d, (200, 300), pre["text"], F("Inter-MediumItalic", 44), MUTED, p)
        els.append(El(cue(cues, pre["s"]) if pre["s"] else 0.4, pre_fn))
        y0 = 420
    rows = math.ceil(len(items) / cols)
    gap = min(130, (880 - y0) / max(1, rows))
    colw = (W - 400) / cols
    f = F("Inter-SemiBold", 52)
    for i, (it, t0) in enumerate(zip(items, t0s)):
        c, r = i % cols, i // cols
        x = 200 + c * colw
        y = y0 + r * gap + gap / 2

        fi = f
        while text_w(fi, it["text"]) > colw - 130 and fi.size > 34:
            fi = F("Inter-SemiBold", fi.size - 2)
        decay = v.get("decay")

        def item(d, p, it=it, x=x, y=y, i=i, fi=fi):
            if decay:  # appear, hold, then fade toward grey
                pa, pd = min(1.0, p / 0.18), max(0.0, min(1.0, (p - 0.45) / 0.4))
                e = ease(pa)
                if e <= 0:
                    return
                col = blend((78, 86, 110), pd, FG)
                d.rectangle((x + 10, y - 9, x + 28, y + 9), fill=blend(blend((78, 86, 110), pd, RED), e))
                d.text((x + 100 + (1 - e) * 30, y), it["text"], font=fi, fill=blend(col, e), anchor="lm")
                return
            e = ease(p)
            if e <= 0:
                return
            if v.get("numbered"):
                cx = x + 34
                d.ellipse((cx - 34, y - 34, cx + 34, y + 34), fill=blend(RED, e))
                d.text((cx, y), str(i + 1), font=F("InterDisplay-Bold", 40), fill=blend(FG, e, RED), anchor="mm")
            elif v.get("check"):
                d.line((x + 6, y, x + 18, y + 12, x + 38, y - 14), fill=blend(RED, e), width=7, joint="curve")
            else:
                d.rectangle((x + 10, y - 9, x + 28, y + 9), fill=blend(RED, e))
            txt(d, (x + 100 + (1 - e) * 30, y), it["text"], fi, FG, p, "lm", 0)
        els.append(El(t0, item, 3.2 if decay else 0.5))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def footer(d, p, s):
    e = ease(p)
    if e <= 0:
        return
    f = F("Inter-SemiBold", 42)
    w_ = text_w(f, s) + 80
    x0, y0 = W / 2 - w_ / 2, 930 + (1 - e) * 20
    d.rounded_rectangle((x0, y0, x0 + w_, y0 + 84), radius=42, outline=blend(RED, e), width=3, fill=blend((32, 20, 28), e))
    d.text((W / 2, y0 + 42), s, font=f, fill=blend(FG, e), anchor="mm")


def v_versus(v, cues, dur):
    els = []
    cw, ch = 760, 520
    gapx = 90
    y0 = 200
    for side, key in ((0, "left"), (1, "right")):
        c = v[key]
        x0 = W / 2 - cw - gapx / 2 if side == 0 else W / 2 + gapx / 2
        t0 = cue(cues, c["s"])

        def card(d, p, c=c, x0=x0, key=key):
            e = ease(p)
            if e <= 0:
                return
            yy = y0 + (1 - e) * 30
            d.rounded_rectangle((x0, yy, x0 + cw, yy + ch), radius=28, fill=blend((24, 30, 46), e), outline=blend(FAINT, e), width=2)
            d.text((x0 + 60, yy + 60), c["title"], font=F("InterDisplay-Bold", 64), fill=blend(FG, e), anchor="la")
            for i, ln in enumerate(c["lines"]):
                ly = yy + 200 + i * 78
                d.ellipse((x0 + 62, ly - 8, x0 + 78, ly + 8), fill=blend(MUTED, e))
                d.text((x0 + 104, ly), ln, font=F("Inter-Medium", 42), fill=blend(FG, e * 0.9), anchor="lm")
        els.append(El(t0, card, 0.6))
    tv = cue(cues, v["s_verdict"], 0.3)
    win = v.get("winner")

    def verdict(d, p):
        e = ease(p)
        if e <= 0:
            return
        if win:
            x0 = W / 2 - cw - gapx / 2 if win == "left" else W / 2 + gapx / 2
            d.rounded_rectangle((x0 - 4, y0 - 4, x0 + cw + 4, y0 + ch + 4), radius=32, outline=blend(RED, e), width=6)
        footer(d, p, v["verdict"])
    els.append(El(tv, verdict, 0.6))
    return els


def v_bars(v, cues, dur):
    els = []
    heading(els, v["title"], 120)
    items = v["items"]
    compact = v.get("compact")
    y0 = 300 if not compact else 270
    gap = 150 if not compact else 62
    bh = 84 if not compact else 44
    lx = 200
    labw = 520 if not compact else 420
    bx = lx + labw
    maxw = W - bx - 260
    t0s = stagger(items, cues, 0.35 if not compact else 0.18)
    lf = F("Inter-SemiBold", 46 if not compact else 34)
    vf = F("InterDisplay-Bold", 50 if not compact else 36)
    for i, (it, t0) in enumerate(zip(items, t0s)):
        y = y0 + i * gap

        def bar(d, p, it=it, y=y):
            e = ease(p)
            if e <= 0:
                return
            col = RED if it.get("hl") else SLATE
            txt(d, (lx, y + bh / 2), it["label"], lf, FG, min(1, p * 2), "lm", 0)
            w_ = maxw * it["value"] / v["max"] * e
            d.rounded_rectangle((bx, y, bx + max(w_, 8), y + bh), radius=8, fill=blend(col, min(1, p * 2)))
            val = it["value"] * e
            label = f"{val:.0f}M+" if it.get("plus") else f"{val:.1f}M"
            d.text((bx + w_ + 24, y + bh / 2), label, font=vf, fill=blend(FG, min(1, p * 2)), anchor="lm")
        els.append(El(t0, bar, 1.0))
    if "legend" in v:
        def legend(d, p):
            e = ease(p)
            if e <= 0:
                return
            x = lx
            for j, (lbl, col) in enumerate(zip(v["legend"], (SLATE, RED))):
                xx = x + j * 340
                d.rounded_rectangle((xx, 912, xx + 36, 948), radius=6, fill=blend(col, e))
                d.text((xx + 52, 930), lbl, font=F("Inter-Medium", 36), fill=blend(MUTED, e), anchor="lm")
        els.append(El(0.3, legend))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def v_quote(v, cues, dur):
    els = []
    f = F("InterDisplay-MediumItalic", 74 if len(v["text"]) < 90 else 62)
    lines = wrap(v["text"], f, W - 480)
    lh = f.size * 1.3
    top = 520 - len(lines) * lh / 2
    els.append(El(0.0, lambda d, p: txt(d, (170, top - 210), "“", F("InterDisplay-Black", 300), RED, p, "la", 30), 0.6))

    def body(d, p):
        for i, ln in enumerate(lines):
            txt(d, (240, top + i * lh), ln, f, FG, p, "la", 24)
    t0 = cue(cues, v["s_text"])
    els.append(El(t0, body, 0.8))
    yb = top + len(lines) * lh + 50

    def by(d, p):
        e = ease(p)
        if e > 0:
            d.rectangle((240, yb + 22, 240 + 60 * e, yb + 27), fill=RED)
        txt(d, (330, yb + 24), v["by"], F("Inter-Medium", 40), MUTED, p, "lm", 0)
    els.append(El(t0 + 0.6, by, 0.6))
    return els


def v_define(v, cues, dur):
    els = []
    els.append(El(0.0, lambda d, p: txt(d, (W / 2, 210), v.get("heading", "“Lateral thinking with withered technology”"), F("InterDisplay-BoldItalic", 64), FG, p, "mm")))
    els.append(El(0.3, lambda d, p: txt(d, (W / 2, 290), v.get("byline", "— Gunpei Yokoi's design philosophy"), F("Inter-Medium", 40), MUTED, p, "mm")))
    for i, pr in enumerate(v["pairs"]):
        y = 470 + i * 170

        def row(d, p, pr=pr, y=y):
            txt(d, (W / 2 - 60, y), pr["term"], F("InterDisplay-Black", 96), RED, p, "rm", 0)
            txt(d, (W / 2 + 0, y), pr["meaning"], F("Inter-Medium", 48), FG, p, "lm", 0)
        els.append(El(cue(cues, pr["s"]), row, 0.6))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


# ---------------------------------------------------------------- extra visual types
def fit_font(name, size, s, maxw, min_size=26):
    f = F(name, size)
    while text_w(f, s) > maxw and size > min_size:
        size -= 2
        f = F(name, size)
    return f


def draw_wrapped(d, cx, cy, s, font, color, maxw, lh=1.2):
    lines = wrap(s, font, maxw)
    h = len(lines) * font.size * lh
    for i, ln in enumerate(lines):
        d.text((cx, cy - h / 2 + (i + 0.5) * font.size * lh), ln, font=font, fill=color, anchor="mm")


def arrow(d, x0, y0, x1, y1, col, width=5, head=16):
    d.line((x0, y0, x1, y1), fill=col, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        a = ang + math.pi - s * 0.45
        d.line((x1, y1, x1 + head * math.cos(a), y1 + head * math.sin(a)), fill=col, width=width)


def v_exhibits(v, cues, dur):
    """Dark-museum placards."""
    els = []
    if v.get("heading"):
        els.append(El(cue(cues, v.get("s_heading", 0)) if v.get("s_heading") else 0.2,
                      lambda d, p: txt(d, (W / 2, 210), v["heading"], F("InterDisplay-MediumItalic", 62), FG, p, "mm")))
    items = v["items"]
    n = len(items)
    cw, gap = 470, 60
    x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
    for i, it in enumerate(items):
        x = x0 + i * (cw + gap)

        def card(d, p, it=it, x=x, i=i):
            e = ease(p)
            if e <= 0:
                return
            y = 380 + (1 - e) * 30
            # spotlight pool on the "floor"
            d.ellipse((x + 30, 860, x + cw - 30, 910), fill=blend((30, 34, 50), e))
            d.rounded_rectangle((x, y, x + cw, y + 400), radius=10, fill=blend((22, 26, 40), e), outline=blend((60, 66, 90), e), width=2)
            d.text((x + 40, y + 50), f"EXHIBIT {i + 1:02d}", font=F("Inter-Bold", 28), fill=blend(RED, e), anchor="lm")
            ft = fit_font("InterDisplay-Bold", 66, it["title"], cw - 80)
            d.text((x + 40, y + 140), it["title"], font=ft, fill=blend(FG, e), anchor="lm")
            fc = F("Inter-Medium", 36)
            for j, ln in enumerate(wrap(it["caption"], fc, cw - 80)):
                d.text((x + 40, y + 230 + j * 48), ln, font=fc, fill=blend(MUTED, e), anchor="lm")
            d.line((x + cw / 2, y + 400, x + cw / 2, 870), fill=blend((50, 56, 78), e), width=3)
        els.append(El(cue(cues, it["s"]), card, 0.8))
    return els


def v_cards(v, cues, dur):
    """Row of big-number data cards."""
    els = []
    if v.get("heading"):
        heading(els, v["heading"])
    items = v["items"]
    n = len(items)
    gap = 50
    cw = (W - 400 - (n - 1) * gap) / n
    y0 = 380 if v.get("heading") else 300
    ch = v.get("height", 420)
    t0s = stagger(items, cues, 0.4)
    fb = min((fit_font("InterDisplay-Black", 150 if n <= 3 else 96, it["big"], cw - 70, 40) for it in items), key=lambda f: f.size)
    for i, (it, t0) in enumerate(zip(items, t0s)):
        x = 200 + i * (cw + gap)

        def card(d, p, it=it, x=x):
            e = ease(p)
            if e <= 0:
                return
            y = y0 + (1 - e) * 30
            d.rounded_rectangle((x, y, x + cw, y + ch), radius=26, fill=blend((24, 30, 46), e),
                                outline=blend(RED if it.get("hl") else FAINT, e), width=3 if it.get("hl") else 2)
            d.text((x + cw / 2, y + ch * 0.36), it["big"], font=fb, fill=blend(RED if it.get("hl") else FG, e), anchor="mm")
            fl = F("Inter-SemiBold", 40 if n <= 3 else 34)
            draw_wrapped(d, x + cw / 2, y + ch * 0.66, it["label"], fl, blend(FG, e), cw - 70)
            if it.get("note"):
                draw_wrapped(d, x + cw / 2, y + ch * 0.86, it["note"], F("Inter-Medium", 28), blend(MUTED, e), cw - 70)
        els.append(El(t0, card, 0.6))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def v_flow(v, cues, dur):
    """Boxes joined by arrows; optional loop-back arrow or two-way arrows."""
    els = []
    if v.get("heading"):
        heading(els, v["heading"])
    nodes = v["nodes"]
    n = len(nodes)
    gapx = 110
    bw = min(400, (W - 360 - (n - 1) * gapx) / n)
    total = n * bw + (n - 1) * gapx
    x0 = W / 2 - total / 2
    cy = v.get("y", 560)
    bh = 200
    t0s = stagger(nodes, cues, 0.45)
    for i, (nd, t0) in enumerate(zip(nodes, t0s)):
        x = x0 + i * (bw + gapx)

        def box(d, p, nd=nd, x=x, i=i):
            e = ease(p)
            if e <= 0:
                return
            hl = nd.get("hl")
            d.rounded_rectangle((x, cy - bh / 2, x + bw, cy + bh / 2), radius=24,
                                fill=blend((24, 30, 46) if not hl else (60, 22, 30), e), outline=blend(RED if hl else FAINT, e), width=3)
            draw_wrapped(d, x + bw / 2, cy, nd["text"], fit_font("InterDisplay-Bold", 46, max(nd["text"].split(), key=len), bw - 50), blend(FG, e), bw - 50)
            if i > 0:
                ax0, ax1 = x - gapx + 14, x - 14
                col = blend(RED, e)
                if v.get("bidir"):
                    arrow(d, ax0 + (ax1 - ax0) * (1 - e), cy, ax1, cy, col)
                    arrow(d, ax1 - (ax1 - ax0) * (1 - e) * 0, cy, ax0, cy, col) if e > 0.5 else None
                else:
                    arrow(d, ax0, cy, ax0 + (ax1 - ax0) * e, cy, col)
        els.append(El(t0, box, 0.6))
    if v.get("loop"):
        def loop(d, p):
            e = ease(p)
            if e <= 0:
                return
            col = blend(RED, e)
            xl, xr = x0 + bw / 2, x0 + total - bw / 2
            yb = cy + bh / 2 + 70
            d.line((xr, cy + bh / 2 + 10, xr, yb), fill=col, width=5)
            d.line((xr, yb, xr - (xr - xl) * e, yb), fill=col, width=5)
            if e > 0.95:
                arrow(d, xl, yb, xl, cy + bh / 2 + 14, col)
        els.append(El((t0s[-1] if t0s else 0) + 0.5, loop, 0.9))
    if v.get("kicker"):
        els.append(El(0.1, lambda d, p: txt(d, (W / 2, cy - bh / 2 - 90), v["kicker"], F("Inter-SemiBold", 36), RED, p, "mm")))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def v_chain(v, cues, dur):
    """Rows of 'A → B' (patent-drawing style when v['blueprint'])."""
    els = []
    heading(els, v["heading"])
    rows = v["rows"]
    n = len(rows)
    y0 = 340
    gap = min(150, 580 / max(1, n))
    bw = 640
    xa, xb = 200, W - 200 - bw
    t0s = stagger(rows, cues, 0.5)
    bp = v.get("blueprint")
    if bp:
        def grid(d, p):
            e = ease(p) * 0.6
            for x in range(200, W - 199, 80):
                d.line((x, 300, x, 980), fill=blend((30, 40, 62), e))
            for y in range(300, 981, 80):
                d.line((200, y, W - 200, y), fill=blend((30, 40, 62), e))
        els.insert(0, El(0.0, grid, 0.8))
    for i, (r, t0) in enumerate(zip(rows, t0s)):
        y = y0 + i * gap + gap / 2 - 10

        def row(d, p, r=r, y=y):
            e = ease(p)
            if e <= 0:
                return
            h = min(gap - 26, 110)
            d.rounded_rectangle((xa, y - h / 2, xa + bw, y + h / 2), radius=14, outline=blend((110, 130, 170) if bp else FAINT, e),
                                width=2, fill=blend((18, 24, 40), e))
            fa = F("Inter-Medium", 40 if text_w(F("Inter-Medium", 40), r["a"]) <= bw - 60 else 36)
            for j, ln in enumerate(la := wrap(r["a"], fa, bw - 60)):
                d.text((xa + 30, y + (j - (len(la) - 1) / 2) * fa.size * 1.15), ln, font=fa, fill=blend((170, 182, 205), e), anchor="lm")
            e2 = ease(min(1, p * 1.6 - 0.3))
            if e2 > 0:
                arrow(d, xa + bw + 30, y, xa + bw + 30 + (xb - xa - bw - 60) * e2, y, blend(RED, e2), 6, 20)
                d.rounded_rectangle((xb, y - h / 2, xb + bw, y + h / 2), radius=14, fill=blend((40, 22, 32), e2), outline=blend(RED, e2), width=3)
                fb = F("InterDisplay-Bold", 46 if text_w(F("InterDisplay-Bold", 46), r["b"]) <= bw - 60 else 38)
                for j, ln in enumerate(lb := wrap(r["b"], fb, bw - 60)):
                    d.text((xb + 30, y + (j - (len(lb) - 1) / 2) * fb.size * 1.15), ln, font=fb, fill=blend(FG, e2), anchor="lm")
        els.append(El(t0, row, 0.9))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def v_rail(v, cues, dur):
    """The recurring red timeline. Can break after a node and reconnect later."""
    els = []
    if v.get("heading"):
        heading(els, v["heading"])
    nodes = v["nodes"]
    n = len(nodes)
    lx0, lx1, ly = 220, W - 220, v.get("y", 600)
    xs = [lx0 + (lx1 - lx0) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
    t0s = stagger(nodes, cues, 0.35)
    brk = v.get("break_after")
    t_reconnect = cue(cues, v["s_reconnect"]) if "s_reconnect" in v else None

    for i in range(1, n):
        def seg(d, p, i=i):
            e = ease(p)
            if e <= 0:
                return
            xa, xb = xs[i - 1] + 18, xs[i] - 18
            if brk is not None and i - 1 == brk:
                # broken segment: jagged stubs with a gap; red only once reconnected
                mid = (xa + xb) / 2
                col = blend((90, 98, 122), e)
                for sgn, start in ((1, xa), (-1, xb)):
                    end = mid - sgn * 34
                    d.line((start, ly, start + (end - start) * e, ly), fill=col, width=8)
                    if e > 0.9:
                        jx = end
                        d.line((jx, ly - 4, jx + sgn * 10, ly - 16, jx + sgn * 2, ly + 2, jx + sgn * 12, ly + 14),
                               fill=col, width=4)
                return
            d.line((xa, ly, xa + (xb - xa) * e, ly), fill=blend(RED, e), width=8)
        if brk is not None and i - 1 == brk:
            t_seg = t0s[i - 1] + 0.3
        else:
            t_seg = t0s[i] - 0.2 if i < n else 0
        els.append(El(max(0.0, t_seg), seg, 0.6))
    if t_reconnect is not None and brk is not None:
        def bridge(d, p):
            e = ease(p)
            if e <= 0:
                return
            xa, xb = xs[brk] + 18, xs[brk + 1] - 18
            mid = (xa + xb) / 2
            d.line((mid - 40 - (mid - 40 - xa) * 0, ly, mid - 40 + 80 * e, ly), fill=blend(RED, e), width=8)
            d.line((xa, ly, mid, ly), fill=blend(RED, e), width=8)
            d.line((mid, ly, mid + (xb - mid) * e, ly), fill=blend(RED, e), width=8)
        els.append(El(t_reconnect, bridge, 0.8))
    for i, (nd, t0) in enumerate(zip(nodes, t0s)):
        x = xs[i]
        up = i % 2 == 0

        def node(d, p, nd=nd, x=x, up=up):
            e = ease(p)
            if e <= 0:
                return
            dim = nd.get("dim")
            col = (110, 118, 140) if dim else RED
            r = 18 * e
            d.ellipse((x - r, ly - r, x + r, ly + r), fill=blend(col, e), outline=blend(FG, e), width=3)
            yy = ly - 70 if up else ly + 70
            d.text((x, yy), nd["year"], font=F("InterDisplay-Bold", 46), fill=blend(col, e), anchor="mm")
            yl = ly - 125 if up else ly + 125
            fl = fit_font("Inter-SemiBold", 36, nd["label"], 300, 24)
            d.text((x, yl), nd["label"], font=fl, fill=blend(FG if not dim else MUTED, e), anchor="mm")
            if nd.get("value"):
                yv = ly - 185 if up else ly + 190
                d.text((x, yv), nd["value"], font=F("InterDisplay-Black", 54), fill=blend(GOLD if nd.get("gold") else FG, e), anchor="mm")
        els.append(El(t0, node, 0.5))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def v_rings(v, cues, dur):
    els = []
    if v.get("heading"):
        heading(els, v["heading"])
    cx, cy = 640, 600
    radii = [150, 255, 360]
    rings = v["rings"]
    for i, rg in enumerate(rings):
        r = radii[i]
        ly = 400 + i * 190

        def ring(d, p, r=r, rg=rg, i=i, ly=ly):
            e = ease(p)
            if e <= 0:
                return
            col = blend(RED if i == 0 else (RED if rg.get("hl") else (150, 60, 70)), e)
            d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * e, fill=col, width=10)
            # leader line to label
            ang = math.radians(-40 + i * 40)
            px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
            if e > 0.4:
                ee = (e - 0.4) / 0.6
                d.line((px, py, px + (1180 - px) * ee, ly), fill=blend(FAINT, ee), width=3)
                d.text((1210, ly - 26), f"{i + 1:02d}  {rg['title']}", font=F("InterDisplay-Bold", 52), fill=blend(FG, ee), anchor="lm")
                d.text((1210 + 76, ly + 32), rg["sub"], font=F("Inter-Medium", 34), fill=blend(MUTED, ee), anchor="lm")
        els.append(El(cue(cues, rg["s"]), ring, 1.0))

    def center(d, p):
        e = ease(p)
        if e > 0:
            d.ellipse((cx - 70 * e, cy - 70 * e, cx + 70 * e, cy + 70 * e), fill=blend(RED, e))
            if e > 0.6:
                d.text((cx, cy), v.get("center", "N"), font=F("InterDisplay-Black", 64), fill=blend(FG, (e - 0.6) / 0.4, RED), anchor="mm")
    els.append(El(cue(cues, v.get("s_center", 0)) if v.get("s_center") else 0.3, center, 0.6))
    return els


# --- product silhouettes (generic shapes, no logos)
def draw_tablet(d, cx, cy, e, sep=0.0, scale=1.0, left=RED, right=(70, 120, 200), body=(44, 48, 62), base=BG):
    bw, bh = 600 * scale, 340 * scale
    jw = 110 * scale
    d.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), radius=22 * scale, fill=blend(body, e, base))
    d.rounded_rectangle((cx - bw / 2 + 28 * scale, cy - bh / 2 + 22 * scale, cx + bw / 2 - 28 * scale, cy + bh / 2 - 22 * scale),
                        radius=8 * scale, fill=blend((16, 20, 32), e, base), outline=blend((70, 76, 100), e, base), width=2)
    for side, col in ((-1, left), (1, right)):
        x_in = cx + side * (bw / 2 + sep)
        x_out = x_in + side * jw
        xa, xb = sorted((x_in, x_out))
        rad = jw * 0.55
        d.rounded_rectangle((xa, cy - bh / 2, xb, cy + bh / 2), radius=rad, fill=blend(col, e, base))
        sx = (xa + xb) / 2
        sy = cy - bh * 0.18 if side < 0 else cy + bh * 0.12
        d.ellipse((sx - 26 * scale, sy - 26 * scale, sx + 26 * scale, sy + 26 * scale), fill=blend((30, 32, 40), e, base))


def v_morph(v, cues, dur):
    """Wii U-style GamePad simplifies into a hybrid tablet with detachable controllers."""
    els = []
    tm = cue(cues, v["s_morph"])
    td = cue(cues, v["s_detach"]) if "s_detach" in v else None
    cx, cy = W / 2, 470

    def shape(d, p):
        t = p * dur
        m = ease((t - tm) / 1.6) if t >= tm else 0.0
        a = ease(t / 0.6)
        if a <= 0:
            return
        sep = 0.0
        if td is not None and t >= td:
            sep = 70 * ease((t - td) / 0.8)
        # GamePad (fades/shrinks as m -> 1)
        if m < 1:
            g = a * (1 - m)
            bw = 900 - (900 - 600) * m
            bh = 420 - (420 - 340) * m
            rad = 130 - 100 * m
            d.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), radius=rad, fill=blend((70, 78, 100), g))
            sw, shh = 470 + 60 * m, 270 + 30 * m
            d.rounded_rectangle((cx - sw / 2, cy - shh / 2, cx + sw / 2, cy + shh / 2), radius=8, fill=blend((16, 20, 32), g))
            for sx in (cx - 345, cx + 345):
                d.ellipse((sx - 34, cy - 110, sx + 34, cy - 42), fill=blend((40, 44, 56), g))
            if m == 0:
                d.text((cx, cy + bh / 2 + 70), v.get("before", "Wii U GamePad"), font=F("Inter-SemiBold", 40), fill=blend(MUTED, a), anchor="mm")
        if m > 0:
            draw_tablet(d, cx, cy, m * a, sep=sep + (1 - m) * 120)
            d.text((cx, cy + 250), v.get("after", "Nintendo Switch"), font=F("Inter-SemiBold", 40), fill=blend(MUTED, m), anchor="mm")
    els.append(El(0.0, shape, max(dur, 0.1)))
    labels = v.get("labels", [])
    t0s = stagger(labels, cues, 0.4)
    f = F("Inter-SemiBold", 38)
    widths = [text_w(f, lb["text"]) + 70 for lb in labels]
    gapp = 34
    xcur = W / 2 - (sum(widths) + gapp * (len(widths) - 1)) / 2
    for i, (lb, t0) in enumerate(zip(labels, t0s)):
        x = xcur + widths[i] / 2
        xcur += widths[i] + gapp

        def lab(d, p, lb=lb, x=x):
            e = ease(p)
            if e <= 0:
                return
            w_ = text_w(f, lb["text"]) + 70
            y = 900 + (1 - e) * 20
            d.rounded_rectangle((x - w_ / 2, y - 36, x + w_ / 2, y + 36), radius=36, outline=blend(RED, e), width=3, fill=blend((32, 20, 28), e))
            d.text((x, y), lb["text"], font=f, fill=blend(FG, e), anchor="mm")
        els.append(El(t0, lab, 0.5))
    return els


def v_journey(v, cues, dur):
    """A red line travels from the dock through the day and back."""
    els = []
    if v.get("heading"):
        heading(els, v["heading"])
    st = v["stations"]
    n = len(st)
    xs = [240 + (W - 480) * i / (n - 1) for i in range(n)]
    ly = 600
    times = [cue(cues, s["s"]) for s in st]

    def path_y(x):
        return ly + 60 * math.sin((x - 240) / (W - 480) * math.pi * 2)

    def draw(d, p):
        t = p * dur
        # how far along (in station units) the dot is
        pos = 0.0
        for i in range(1, n):
            if t >= times[i]:
                pos = i
            elif t >= times[i] - 0.9:
                pos = i - 1 + ease((t - (times[i] - 0.9)) / 0.9)
                break
            else:
                break
        xdot = xs[0] + (xs[-1] - xs[0]) * pos / (n - 1)
        a = ease(t / 0.6)
        # full faint path, then red travelled part
        pts = [(x, path_y(x)) for x in range(int(xs[0]), int(xs[-1]) + 1, 8)]
        d.line(pts, fill=blend(FAINT, a), width=6, joint="curve")
        red = [(x, y) for (x, y) in pts if x <= xdot]
        if len(red) > 1:
            d.line(red, fill=blend(RED, a), width=8, joint="curve")
        for i, (x, s) in enumerate(zip(xs, st)):
            reached = t >= times[i] - 0.05
            ea = ease((t - times[i]) / 0.5) if reached else 0
            y = path_y(x)
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=blend(RED if reached else FAINT, a), outline=blend(FG, a * (0.3 + 0.7 * ea)), width=2)
            up = i % 2 == 0
            if ea > 0:
                yy = y - 90 if up else y + 90
                d.text((x, yy + (1 - ea) * 15), s["label"], font=fit_font("InterDisplay-Bold", 46, s["label"], 340), fill=blend(FG, ea), anchor="mm")
                if s.get("sub"):
                    d.text((x, yy + (44 if not up else -50)), s["sub"], font=F("Inter-Medium", 30), fill=blend(MUTED, ea), anchor="mm")
        yd = path_y(xdot)
        d.ellipse((xdot - 26, yd - 26, xdot + 26, yd + 26), fill=blend(FG, a), outline=blend(RED, a), width=8)
    els.append(El(0.0, draw, max(dur, 0.1)))
    if "footer" in v:
        els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


def draw_card(d, cx, cy, e, scale=1.0):
    """Abstract hanafuda-style card: cream face, red sun, dark hills."""
    w_, h_ = 300 * scale, 470 * scale
    x0, y0 = cx - w_ / 2, cy - h_ / 2
    d.rounded_rectangle((x0 - 8, y0 - 8, x0 + w_ + 8, y0 + h_ + 8), radius=18 * scale, fill=blend((120, 30, 36), e))
    d.rounded_rectangle((x0, y0, x0 + w_, y0 + h_), radius=12 * scale, fill=blend((238, 228, 206), e))
    r = 80 * scale
    d.ellipse((cx - r, y0 + 70 * scale, cx + r, y0 + 70 * scale + 2 * r), fill=blend(RED, e))
    hills = [(x0, y0 + h_ * 0.78), (x0 + w_ * 0.25, y0 + h_ * 0.6), (x0 + w_ * 0.5, y0 + h_ * 0.72),
             (x0 + w_ * 0.78, y0 + h_ * 0.55), (x0 + w_, y0 + h_ * 0.7), (x0 + w_, y0 + h_), (x0, y0 + h_)]
    d.polygon(hills, fill=blend((30, 32, 40), e))
    d.line((x0 + w_ * 0.15, y0 + h_ * 0.5, x0 + w_ * 0.5, y0 + h_ * 0.42, x0 + w_ * 0.85, y0 + h_ * 0.47),
           fill=blend((30, 32, 40), e), width=int(6 * scale))


def v_cardmorph(v, cues, dur):
    els = []
    ts = cue(cues, v["s_shift"])

    def draw(d, p):
        t = p * dur
        a = ease(t / 0.8)
        m = ease((t - ts) / 1.4) if t >= ts else 0.0
        cxc = W / 2 - 400 * m
        draw_card(d, cxc, 500, a, 1.0)
        if a > 0:
            d.text((cxc, 820), v.get("left", "1889 · paper and ink"), font=F("Inter-SemiBold", 38), fill=blend(MUTED, a), anchor="mm")
        if m > 0:
            drop = (1 - ease((t - ts - 0.6) / 0.9)) * 240 if t >= ts + 0.6 else 240
            cx2 = W / 2 + 330
            # tablet with right controller attached; left controller slides down its rail
            draw_tablet(d, cx2, 500, m, sep=0, scale=0.7)
            if drop > 0:
                # cover the left controller and redraw it offset upward (sliding in)
                bw, bh, jw = 600 * 0.7, 340 * 0.7, 110 * 0.7
                xa, xb = cx2 - bw / 2 - jw, cx2 - bw / 2
                d.rounded_rectangle((xa - 2, 500 - bh / 2 - 2, xb, 500 + bh / 2 + 2), radius=jw * 0.55, fill=BG)
                d.rounded_rectangle((xa, 500 - bh / 2 - drop, xb, 500 + bh / 2 - drop), radius=jw * 0.55, fill=blend(RED, m))
            d.text((cx2, 820), v.get("right", "today · screens and controllers"), font=F("Inter-SemiBold", 38), fill=blend(MUTED, m), anchor="mm")
            arrow(d, W / 2 - 120, 500, W / 2 - 120 + 150 * m, 500, blend(RED, m), 6, 20)
    els.append(El(0.0, draw, max(dur, 0.1)))
    return els


BUILDERS = dict(hero=v_hero, graveyard=v_graveyard, title=v_title, chapter=v_chapter,
                statement=v_statement, timeline=v_timeline, list=v_list, versus=v_versus,
                bars=v_bars, quote=v_quote, define=v_define,
                exhibits=v_exhibits, cards=v_cards, flow=v_flow, chain=v_chain, rail=v_rail,
                rings=v_rings, morph=v_morph, journey=v_journey, cardmorph=v_cardmorph)



def load_project(path):
    """Load <path>/scenes.py; module attributes override the defaults above."""
    import importlib.util
    global SCENES, PROJECT, SLUG, SERIES, MUSIC, OUT, CACHE, VOICE, RATE, SENT_GAP, SCENE_GAP, CHAPTER_EXTRA
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location("project_scenes", os.path.join(path, "scenes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    PROJECT = mod
    SCENES = mod.SCENES
    SLUG = getattr(mod, "SLUG", SLUG)
    SERIES = getattr(mod, "SERIES", SERIES)
    MUSIC = getattr(mod, "MUSIC", MUSIC)
    VOICE = getattr(mod, "VOICE", VOICE)
    RATE = getattr(mod, "RATE", RATE)
    SENT_GAP = getattr(mod, "SENT_GAP", SENT_GAP)
    SCENE_GAP = getattr(mod, "SCENE_GAP", SCENE_GAP)
    CHAPTER_EXTRA = getattr(mod, "CHAPTER_EXTRA", CHAPTER_EXTRA)
    CACHE = os.path.join(path, ".cache")
    OUT = os.path.join(ROOT, "output", getattr(mod, "OUT_SUBDIR", "")).rstrip("/")


def part_labels():
    labels, cur = {}, "INTRO"
    for sc in SCENES:
        v = sc["visual"]
        if v["type"] == "chapter":
            cur = v.get("hud") or f"PART {v['num']} · {v['title'].upper()}"
        if sc.get("hud"):
            cur = sc["hud"]
        if sc["id"].startswith("p6"):
            cur = "THE WEAKNESSES"
        if sc["id"].startswith("c_"):
            cur = "THE ANSWER"
        labels[sc["id"]] = cur
    return labels


def hud(d, label):
    d.ellipse((80, 62, 96, 78), fill=RED)
    d.text((112, 70), SERIES, font=F("Inter-Bold", 26), fill=MUTED, anchor="lm")
    f = F("Inter-SemiBold", 26)
    d.text((W - 80, 70), label, font=f, fill=(110, 120, 145), anchor="rm")


def render(timeline, total, out_path, only=None, stills_dir=None):
    bgs = {"normal": make_bg(), "chapter": make_bg((1650, 540), 0.26, True), "title": make_bg((W / 2, 420), 0.2, True),
           "cool": make_bg((1500, 160), 0.30, color=(70, 110, 190)),
           "dark": make_bg((W / 2, 300), 0.07, True)}
    labels = part_labels()
    proc = None
    if stills_dir is None:
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
               "-tune", "animation", "-pix_fmt", "yuv420p", out_path]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frame_i = 0
    blank = bgs["normal"].tobytes()
    lead = timeline[0]["start"]
    if proc:
        for _ in range(int(round(lead * FPS))):
            proc.stdin.write(blank); frame_i += 1
    for ti, seg in enumerate(timeline):
        sc = seg["scene"]
        if only and sc["id"] not in only:
            continue
        v = sc["visual"]
        els = BUILDERS[v["type"]](v, seg["cues"], seg["dur"])
        bgk = sc.get("bg") or ("chapter" if v["type"] == "chapter" else ("title" if v["type"] == "title" else "normal"))
        bg = bgs[bgk]
        if proc:
            nframes = int(round((seg["start"] + seg["dur"]) * FPS)) - frame_i
        else:
            nframes = int(seg["dur"] * FPS)
        last_key, last_bytes = None, None
        for k in range(nframes):
            t = k / FPS
            # fade out last 0.3 s of the scene
            fo = max(0.0, min(1.0, (seg["dur"] - t) / 0.3))
            ps = tuple(round(e.p(t), 3) for e in els)
            key = (ps, round(fo, 2))
            if key != last_key:
                img = bg.copy()
                d = ImageDraw.Draw(img)
                if v["type"] not in ("chapter", "title") and not v.get("no_hud"):
                    hud(d, labels[sc["id"]])
                for e, p in zip(els, ps):
                    if p > 0:
                        e.fn(d, p)
                if fo < 1:
                    img = Image.blend(bg, img, fo)
                last_bytes = img.tobytes()
                last_key = key
            if stills_dir is not None and k == int(nframes * 0.97):
                Image.frombytes("RGB", (W, H), last_bytes).save(os.path.join(stills_dir, f"{ti:02d}_{sc['id']}.png"))
            if proc:
                proc.stdin.write(last_bytes)
            frame_i += 1
        print(f"  [{ti + 1}/{len(timeline)}] {sc['id']}  {seg['dur']:.1f}s", flush=True)
    if proc:
        tail = int(round(total * FPS)) - frame_i
        for _ in range(max(0, tail)):
            proc.stdin.write(blank)
        proc.stdin.close()
        proc.wait()


def music_arc(n, timeline):
    """Layered score that follows each scene's `mood` (inherited until changed).

    Layers: pad (sustained chords), mallet (marimba-like arpeggio), piano (sparse
    isolated notes), pulse (low mechanical tick), room (quiet room tone).
    """
    rng = np.random.default_rng(7)
    tt = np.arange(n) / SR
    pad = music_bed(n)
    beat = 60 / 100  # 100 bpm
    chords = [[65, 69, 72, 76], [64, 67, 72, 76], [64, 67, 69, 72], [62, 67, 71, 74]]  # upper voicings
    seg = 8.0

    def chord_at(t):
        return chords[int(t // seg) % 4]

    def note(f, length, kind):
        k = np.arange(int(length * SR)) / SR
        if kind == "mallet":
            y = np.sin(2 * np.pi * f * k) * np.exp(-k * 5) + 0.25 * np.sin(2 * np.pi * 3.93 * f * k) * np.exp(-k * 22)
        elif kind == "piano":
            y = (np.sin(2 * np.pi * f * k) + 0.4 * np.sin(4 * np.pi * f * k) * np.exp(-k * 2) + 0.15 * np.sin(6 * np.pi * f * k) * np.exp(-k * 3)) * np.exp(-k * 1.1)
        else:  # pulse thump + tick
            y = np.sin(2 * np.pi * 55 * k) * np.exp(-k * 10) + 0.12 * rng.standard_normal(len(k)) * np.exp(-k * 90)
        att = np.minimum(1, k / 0.004)
        return (y * att).astype(np.float32)

    def place(buf, start, y, g=1.0):
        i = int(start * SR)
        if i >= len(buf):
            return
        j = min(len(buf), i + len(y))
        buf[i:j] += y[: j - i] * g

    mallet = np.zeros(n, np.float32)
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    t = 0.0
    k = 0
    while t < n / SR:
        c = chord_at(t)
        m = c[pattern[k % 8]] + (12 if k % 16 >= 8 and k % 8 == 3 else 0)
        place(mallet, t, note(440 * 2 ** ((m - 69) / 12), 0.7, "mallet"), 0.8 + 0.2 * ((k % 4) == 0))
        t += beat / 2
        k += 1
    piano = np.zeros(n, np.float32)
    t = 0.5
    while t < n / SR:
        c = chord_at(t)
        m = c[rng.integers(0, 4)] - 12 * rng.integers(0, 2)
        place(piano, t, note(440 * 2 ** ((m - 69) / 12), 3.5, "piano"), 0.8)
        t += beat * 4 * rng.choice([1, 1, 1.5])
    pulse = np.zeros(n, np.float32)
    t = 0.0
    while t < n / SR:
        place(pulse, t, note(55, 0.4, "pulse"))
        t += beat
    room = np.cumsum(rng.standard_normal(n).astype(np.float32))
    w = int(0.05 * SR)
    room = room - np.convolve(room, np.ones(w) / w, mode="same")

    layers = dict(pad=pad, mallet=mallet, piano=piano, pulse=pulse, room=room)
    for kk in layers:
        layers[kk] = layers[kk] / (np.max(np.abs(layers[kk])) + 1e-9)
    weights = dict(pad=1.0, mallet=0.45, piano=0.55, pulse=0.6, room=0.05)
    MOODS = {
        "open":    dict(pad=0.35, mallet=0.0, piano=0.0, pulse=1.0, room=0.6),
        "playful": dict(pad=0.65, mallet=1.0, piano=0.0, pulse=0.35, room=0.0),
        "thin":    dict(pad=0.12, mallet=0.0, piano=1.0, pulse=0.0, room=1.0),
        "warm":    dict(pad=1.0, mallet=0.9, piano=0.2, pulse=0.55, room=0.0),
        "neutral": dict(pad=0.7, mallet=0.0, piano=0.3, pulse=0.15, room=0.3),
        "close":   dict(pad=1.0, mallet=0.25, piano=0.75, pulse=0.0, room=0.0),
        "silent":  dict(pad=0.0, mallet=0.0, piano=0.0, pulse=0.0, room=0.0),
    }
    cr = 100  # control rate
    nc = int(n / SR * cr) + 1
    gains = {kk: np.zeros(nc, np.float32) for kk in layers}
    cur = "open"
    marks = []
    for seg_ in timeline:
        cur = seg_["scene"].get("mood", cur)
        marks.append((seg_["start"], cur))
    marks.append((n / SR, cur))
    for (a, mood), (b2, _) in zip(marks, marks[1:]):
        ia, ib = int(a * cr), int(b2 * cr)
        if a == marks[0][0]:
            ia = 0
        for kk in layers:
            gains[kk][ia:ib] = MOODS[mood][kk]
    if marks:
        for kk in layers:
            gains[kk][int(marks[-1][0] * cr):] = MOODS[marks[-1][1]][kk]
    sm = int(2.5 * cr)
    out = np.zeros(n, np.float32)
    xc = np.arange(nc) / cr
    for kk, y in layers.items():
        g = np.convolve(np.pad(gains[kk], (sm, sm), mode="edge"), np.ones(sm) / sm, mode="same")[sm:-sm]
        out += y * np.interp(tt, xc, g).astype(np.float32) * weights[kk]
    out /= np.max(np.abs(out)) + 1e-9
    fade = np.minimum(1, (tt[-1] - tt) / 4)
    return out * fade


def sfx_track(n, timeline):
    """Original synthesized cues: 'boot' power-on chimes and a final wooden 'click'."""
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(3)
    for seg in timeline:
        for j, item in enumerate(seg["scene"].get("sfx", [])):
            s, kind = item[0], item[1]
            t0 = seg["start"] + (cue(seg["cues"], s) if s != "end" else seg["dur"] - 0.6)
            if kind == "boot":
                base = [392, 440, 523.25, 587.33][j % 4]
                k = np.arange(int(1.6 * SR)) / SR
                click = rng.standard_normal(int(0.012 * SR)) * 0.6
                y = np.zeros_like(k)
                y[: len(click)] += click
                for dt, f in ((0.05, base), (0.17, base * 1.5)):
                    kk = np.clip(k - dt, 0, None)
                    y += (k >= dt) * (np.sin(2 * np.pi * f * kk) + 0.3 * np.sin(4 * np.pi * f * kk)) * np.exp(-kk * 3.2) * 0.5
                g = 0.35
            elif kind == "click":
                k = np.arange(int(0.25 * SR)) / SR
                y = (np.sin(2 * np.pi * 1750 * k) * 0.6 + np.sin(2 * np.pi * 820 * k)) * np.exp(-k * 55)
                y[: int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.4
                g = 0.6
            else:
                continue
            i = int(t0 * SR)
            jj = min(n, i + len(y))
            out[i:jj] += (y[: jj - i] * g).astype(np.float32)
    return out


def write_description(path, timeline):
    lines = []
    for seg in timeline:
        ch = seg["scene"].get("chapter")
        if ch:
            t = 0 if not lines else int(seg["start"])
            lines.append(f"{t // 60:02d}:{t % 60:02d} {ch}")
    head = getattr(PROJECT, "DESCRIPTION", "").strip()
    tail = getattr(PROJECT, "DESCRIPTION_SOURCES", "").strip()
    with open(path, "w") as f:
        f.write(head + "\n\nChapters:\n" + "\n".join(lines) + ("\n\n" + tail if tail else "") + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=HERE, help="directory containing scenes.py")
    ap.add_argument("--stills", action="store_true", help="render one still per scene instead of video")
    ap.add_argument("--only", help="with --stills: comma-separated scene ids")
    args = ap.parse_args()
    load_project(args.project)
    os.makedirs(OUT, exist_ok=True)
    tts_all()
    timeline, voice = build_timeline()
    total = len(voice) / SR
    print(f"Total runtime: {total / 60:.1f} min ({len(SCENES)} scenes)")
    if args.stills:
        sd = os.path.join(OUT, "stills"); os.makedirs(sd, exist_ok=True)
        render(timeline, total, None, stills_dir=sd, only=set(args.only.split(",")) if args.only else None)
        return
    # audio mix
    vpk = np.max(np.abs(voice)) + 1e-9
    voice = voice / vpk * 0.89
    if MUSIC == "arc":
        music = music_arc(len(voice), timeline) * 0.07
    else:
        music = music_bed(len(voice)) * 0.055
    # duck music under speech
    env = np.abs(voice)
    win = int(0.3 * SR)
    sm = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.45 * np.clip(sm / 0.05, 0, 1)
    mix = voice + music * duck + sfx_track(len(voice), timeline)
    wav = os.path.join(CACHE, "mix.wav")
    write_wav(wav, mix)
    captions = []
    for seg in timeline:
        for s, (a, b) in zip(seg["cues"].sents, seg["cues"]):
            captions.append((seg["start"] + a, seg["start"] + b, s))
    srt = os.path.join(OUT, f"{SLUG}.srt")
    write_srt(srt, captions)
    if any(sc.get("chapter") for sc in SCENES):
        write_description(os.path.join(OUT, f"{SLUG}_youtube_description.txt"), timeline)
    silent = os.path.join(CACHE, "video_silent.mp4")
    render(timeline, total, silent)
    final = os.path.join(OUT, f"{SLUG}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-i", srt,
                    "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=7", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    print("Wrote", final)


if __name__ == "__main__":
    main()
