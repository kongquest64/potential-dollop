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
sys.path.insert(0, HERE)
from scenes import SCENES  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "output")
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
        cues = []
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


def make_bg(glow=(1500, 160), strength=0.16, chapter=False):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = BG
    # vertical vignette
    v = 1 - 0.35 * ((yy / H - 0.45) ** 2)
    base *= v[..., None]
    gx, gy = glow
    d = np.sqrt((xx - gx) ** 2 + (yy - gy) ** 2)
    g = np.exp(-(d / (900 if not chapter else 1100)) ** 2) * strength
    base += g[..., None] * np.array(RED, np.float32)
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


def cue(cues, s, frac=0.0):
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
    els.append(El(0.0, lambda d, p: txt(d, (x, 300), "PART", F("Inter-Bold", 36), MUTED, p)))
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

        def item(d, p, it=it, x=x, y=y, i=i):
            e = ease(p)
            if e <= 0:
                return
            if v.get("numbered"):
                cx = x + 34
                d.ellipse((cx - 34, y - 34, cx + 34, y + 34), fill=blend(RED, e))
                d.text((cx, y), str(i + 1), font=F("InterDisplay-Bold", 40), fill=blend(FG, e, RED), anchor="mm")
            else:
                d.rectangle((x + 10, y - 9, x + 28, y + 9), fill=blend(RED, e))
            txt(d, (x + 100 + (1 - e) * 30, y), it["text"], f, FG, p, "lm", 0)
        els.append(El(t0, item, 0.5))
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
    els.append(El(0.0, lambda d, p: txt(d, (W / 2, 210), "“Lateral thinking with withered technology”", F("InterDisplay-BoldItalic", 64), FG, p, "mm")))
    els.append(El(0.3, lambda d, p: txt(d, (W / 2, 290), "— Gunpei Yokoi's design philosophy", F("Inter-Medium", 40), MUTED, p, "mm")))
    for i, pr in enumerate(v["pairs"]):
        y = 470 + i * 170

        def row(d, p, pr=pr, y=y):
            txt(d, (W / 2 - 60, y), pr["term"], F("InterDisplay-Black", 96), RED, p, "rm", 0)
            txt(d, (W / 2 + 0, y), pr["meaning"], F("Inter-Medium", 48), FG, p, "lm", 0)
        els.append(El(cue(cues, pr["s"]), row, 0.6))
    els.append(El(cue(cues, v["s_footer"]), lambda d, p: footer(d, p, v["footer"])))
    return els


BUILDERS = dict(hero=v_hero, graveyard=v_graveyard, title=v_title, chapter=v_chapter,
                statement=v_statement, timeline=v_timeline, list=v_list, versus=v_versus,
                bars=v_bars, quote=v_quote, define=v_define)

SERIES = "WHY HASN'T NINTENDO DIED?"


def part_labels():
    labels, cur = {}, "INTRO"
    for sc in SCENES:
        v = sc["visual"]
        if v["type"] == "chapter":
            cur = f"PART {v['num']} · {v['title'].upper()}"
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
    bgs = {"normal": make_bg(), "chapter": make_bg((1650, 540), 0.26, True), "title": make_bg((W / 2, 420), 0.2, True)}
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
        if only and sc["id"] != only:
            continue
        v = sc["visual"]
        els = BUILDERS[v["type"]](v, seg["cues"], seg["dur"])
        bgk = "chapter" if v["type"] == "chapter" else ("title" if v["type"] == "title" else "normal")
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
                if v["type"] not in ("chapter", "title"):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="render one still per scene instead of video")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    tts_all()
    timeline, voice = build_timeline()
    total = len(voice) / SR
    print(f"Total runtime: {total / 60:.1f} min")
    if args.stills:
        sd = os.path.join(OUT, "stills"); os.makedirs(sd, exist_ok=True)
        render(timeline, total, None, stills_dir=sd)
        return
    # audio mix
    vpk = np.max(np.abs(voice)) + 1e-9
    voice = voice / vpk * 0.89
    music = music_bed(len(voice)) * 0.055
    # duck music under speech
    env = np.abs(voice)
    win = int(0.3 * SR)
    sm = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.45 * np.clip(sm / 0.05, 0, 1)
    mix = voice + music * duck
    wav = os.path.join(CACHE, "mix.wav")
    write_wav(wav, mix)
    captions = []
    # rebuild caption list from timeline
    for seg in timeline:
        sents = split_sentences(seg["scene"]["text"])
        for s, (a, b) in zip(sents, seg["cues"]):
            captions.append((seg["start"] + a, seg["start"] + b, s))
    srt = os.path.join(OUT, "why_hasnt_nintendo_died.srt")
    write_srt(srt, captions)
    silent = os.path.join(CACHE, "video_silent.mp4")
    render(timeline, total, silent)
    final = os.path.join(OUT, "why_hasnt_nintendo_died.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-i", srt,
                    "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=7", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    print("Wrote", final)


if __name__ == "__main__":
    main()
