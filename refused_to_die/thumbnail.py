#!/usr/bin/env python3
"""Thumbnail: red hybrid-console silhouette in front of faded generations
(hanafuda card, NES-style pad, Game Boy-style handheld, Wii-style remote,
cracked GamePad). Generic shapes only — no logos or character art.

Usage: python3 thumbnail.py [output.png]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2  # supersample
W, H = 1280 * S, 720 * S
BG = (12, 15, 26)
RED = (232, 36, 48)
FD = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(FD + name + ".otf", int(size * S))


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32) + BG
    d = np.sqrt((xx - W * 0.72) ** 2 + (yy - H * 0.45) ** 2)
    img += (np.exp(-(d / (W * 0.33)) ** 2) * 0.42)[..., None] * np.array(RED, np.float32)
    img *= (1 - 0.45 * (xx / W - 0.5) ** 2 - 0.5 * (yy / H - 0.5) ** 2)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def paste(base, lyr, alpha, angle=0, blur=0):
    if angle:
        lyr = lyr.rotate(angle, resample=Image.BICUBIC, center=(W * 0.72, H * 0.5))
    if blur:
        lyr = lyr.filter(ImageFilter.GaussianBlur(blur * S))
    a = lyr.getchannel("A").point(lambda v: int(v * alpha))
    lyr.putalpha(a)
    base.alpha_composite(lyr)


def u(v):
    return int(v * S)


def card(cx, cy, sc=1.0):
    l = layer(); d = ImageDraw.Draw(l)
    w, h = u(170 * sc), u(270 * sc)
    x0, y0 = u(cx) - w // 2, u(cy) - h // 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=u(10), fill=(236, 226, 204, 255), outline=(150, 30, 36, 255), width=u(6))
    r = u(46 * sc)
    d.ellipse((x0 + w // 2 - r, y0 + u(40 * sc), x0 + w // 2 + r, y0 + u(40 * sc) + 2 * r), fill=RED + (255,))
    d.polygon([(x0, y0 + h * 0.78), (x0 + w * 0.3, y0 + h * 0.58), (x0 + w * 0.55, y0 + h * 0.72), (x0 + w * 0.8, y0 + h * 0.55),
               (x0 + w, y0 + h * 0.7), (x0 + w, y0 + h), (x0, y0 + h)], fill=(30, 32, 40, 255))
    return l


def pad(cx, cy):
    l = layer(); d = ImageDraw.Draw(l)
    w, h = u(330), u(140)
    x0, y0 = u(cx) - w // 2, u(cy) - h // 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=u(10), fill=(200, 200, 205, 255))
    d.rounded_rectangle((x0 + u(10), y0 + u(10), x0 + w - u(10), y0 + h - u(10)), radius=u(6), fill=(40, 40, 46, 255))
    cxp, cyp = x0 + u(70), y0 + h // 2
    d.rectangle((cxp - u(30), cyp - u(10), cxp + u(30), cyp + u(10)), fill=(20, 20, 24, 255))
    d.rectangle((cxp - u(10), cyp - u(30), cxp + u(10), cyp + u(30)), fill=(20, 20, 24, 255))
    for bx in (x0 + w - u(110), x0 + w - u(60)):
        d.ellipse((bx - u(17), cyp - u(17), bx + u(17), cyp + u(17)), fill=(200, 40, 40, 255))
    return l


def handheld(cx, cy):
    l = layer(); d = ImageDraw.Draw(l)
    w, h = u(190), u(310)
    x0, y0 = u(cx) - w // 2, u(cy) - h // 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=u(14), fill=(190, 190, 182, 255))
    d.rectangle((x0 + u(25), y0 + u(25), x0 + w - u(25), y0 + u(150)), fill=(70, 72, 80, 255))
    d.rectangle((x0 + u(45), y0 + u(40), x0 + w - u(45), y0 + u(135)), fill=(120, 140, 90, 255))
    cxp, cyp = x0 + u(50), y0 + u(215)
    d.rectangle((cxp - u(22), cyp - u(7), cxp + u(22), cyp + u(7)), fill=(30, 30, 34, 255))
    d.rectangle((cxp - u(7), cyp - u(22), cxp + u(7), cyp + u(22)), fill=(30, 30, 34, 255))
    for bx, by in ((x0 + w - u(40), y0 + u(200)), (x0 + w - u(75), y0 + u(225))):
        d.ellipse((bx - u(14), by - u(14), bx + u(14), by + u(14)), fill=(140, 30, 70, 255))
    return l


def remote(cx, cy):
    l = layer(); d = ImageDraw.Draw(l)
    w, h = u(70), u(330)
    x0, y0 = u(cx) - w // 2, u(cy) - h // 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=u(26), fill=(235, 236, 240, 255))
    cxp = x0 + w // 2
    d.rectangle((cxp - u(18), y0 + u(50), cxp + u(18), y0 + u(62)), fill=(150, 150, 160, 255))
    d.rectangle((cxp - u(6), y0 + u(38), cxp + u(6), y0 + u(74)), fill=(150, 150, 160, 255))
    d.ellipse((cxp - u(15), y0 + u(100), cxp + u(15), y0 + u(130)), fill=(150, 150, 160, 255))
    return l


def gamepad(cx, cy):
    l = layer(); d = ImageDraw.Draw(l)
    w, h = u(470), u(230)
    x0, y0 = u(cx) - w // 2, u(cy) - h // 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=u(70), fill=(200, 202, 210, 255))
    d.rectangle((x0 + u(115), y0 + u(35), x0 + w - u(115), y0 + h - u(35)), fill=(30, 32, 40, 255))
    for sx in (x0 + u(60), x0 + w - u(60)):
        d.ellipse((sx - u(22), y0 + u(45), sx + u(22), y0 + u(89)), fill=(60, 62, 70, 255))
    # crack across the screen
    pts = [(x0 + u(150), y0 + u(40)), (x0 + u(205), y0 + u(100)), (x0 + u(185), y0 + u(125)),
           (x0 + u(260), y0 + u(170)), (x0 + u(245), y0 + u(195))]
    d.line(pts, fill=(235, 235, 240, 255), width=u(4), joint="curve")
    d.line([(x0 + u(205), y0 + u(100)), (x0 + u(250), y0 + u(85)), (x0 + u(300), y0 + u(95))], fill=(235, 235, 240, 255), width=u(3))
    return l


def switch(cx, cy, sc=1.0):
    l = layer(); d = ImageDraw.Draw(l)
    bw, bh, jw = u(420 * sc), u(240 * sc), u(78 * sc)
    x0, y0 = u(cx) - bw // 2, u(cy) - bh // 2
    d.rounded_rectangle((x0 - jw - u(4), y0, x0 + bw + jw + u(4), y0 + bh), radius=u(40 * sc), fill=RED + (255,))
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=u(10 * sc), fill=(150, 18, 28, 255))
    d.rounded_rectangle((x0 + u(18 * sc), y0 + u(16 * sc), x0 + bw - u(18 * sc), y0 + bh - u(16 * sc)), radius=u(6), fill=(18, 10, 14, 255))
    for sx, sy in ((x0 - jw // 2 - u(2), y0 + u(70 * sc)), (x0 + bw + jw // 2 + u(2), y0 + u(140 * sc))):
        r = u(19 * sc)
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(110, 12, 20, 255))
    # sheen
    d.line((x0 + u(40 * sc), y0 + u(30 * sc), x0 + u(110 * sc), y0 + u(30 * sc)), fill=(255, 255, 255, 60), width=u(3))
    return l


def main(out):
    img = bg().convert("RGBA")
    # faded generations, oldest furthest back
    paste(img, card(1150, 170, 0.9), 0.22, angle=-10, blur=2)
    paste(img, pad(780, 140), 0.20, angle=8, blur=2)
    paste(img, handheld(1150, 520), 0.24, angle=12, blur=1.5)
    paste(img, remote(700, 470), 0.22, angle=-22, blur=1.5)
    paste(img, gamepad(980, 600), 0.30, angle=-6, blur=1)
    # glow + hero console
    glow = switch(905, 370, 1.05).filter(ImageFilter.GaussianBlur(u(30)))
    paste(img, glow, 0.8)
    paste(img, switch(905, 370, 1.05), 1.0, angle=-4)
    d = ImageDraw.Draw(img)
    f1 = font("InterDisplay-Black", 150)
    f2 = font("InterDisplay-Black", 92)
    x = u(64)
    d.text((x + u(4), u(150) + u(5)), "137", font=f1, fill=(0, 0, 0, 160))
    d.text((x, u(150)), "137", font=f1, fill=(255, 255, 255, 255))
    d.text((x, u(310)), "YEARS.", font=f2, fill=(255, 255, 255, 255))
    d.text((x, u(420)), "STILL", font=f2, fill=RED + (255,))
    d.text((x, u(520)), "WINNING.", font=f2, fill=RED + (255,))
    d.rectangle((x, u(640), x + u(120), u(652)), fill=(255, 255, 255, 255))
    img = img.convert("RGB").resize((1280, 720), Image.LANCZOS)
    img.save(out)
    print("Wrote", out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "output", "refused_to_die", "thumbnail.png"))
