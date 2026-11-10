#!/usr/bin/env python3
"""TikTok edit for Hana Femme Intimate Cleanser (Nicotinamide Lactic Acid Care Mousse).

Renders straight from the original 4K phone clips:
  python3 hanafemme_edit.py --src "<folder with raw clips>" --out preview.mp4 --preview
  python3 hanafemme_edit.py --src "<folder with raw clips>" --out final.mp4

- 1080x1920 @ 30 fps (preview: 540x960), original colours, original audio removed
- text in the reference style (white, centred, ~18-25% from top, thin dark outline)
- synthesised SFX only, no music
"""
import argparse
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfx  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
FONT_TEXT = os.path.join(HERE, "fonts", "Fredoka-SemiBold.ttf")
FONT_NAME = os.path.join(HERE, "fonts", "Pacifico-Regular.ttf")
FONT_SUB = os.path.join(HERE, "fonts", "Quicksand-Bold.ttf")
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

MARKER = (205, 22, 48, 175)  # translucent cherry-red highlighter (brand colour) behind the name
OUTLINE = (25, 20, 35)

# Source clips (all 3840x2160 HEVC, portrait after autorotate, 59-60 fps).
# Their audio is background chatter, not a voice-over, so it is dropped.
CLIPS = {
    "A": "VID20261107104301.mp4",  # 125 s: box front/back, unboxing, bottle, pump + foam on palm
    "B": "VID20261107104608.mp4",  # 51 s: bottle in one hand, front -> back label -> front
    "C": "VID20261107104802.mp4",  # 30 s: box + bottle front labels side by side
}

# ---------------------------------------------------------------------------
# Edit decision list. Times are seconds in the source clip; text times are
# seconds from the start of the scene. Every scene is < 10 s. `track` = where the
# product sits in the source frame at points u (0..1) of the scene: (u, centre x,
# top y, bottom y) as fractions; the crop follows it so the product stays centred
# and below the text.
# Body wording follows the reference video. Lines whose claim is not printed on
# the packaging were swapped for claims that are:
#   box:    "gentle formula cleanses and cares for intimate areas ... providing
#            comfort and a lasting feeling of freshness", "2-3 pumps"
#   bottle: "Daily Intimate Cleansing Mousse", "Helps maintain pH balance",
#           "Infused with Vitamin E, Chamomile, Probiotics, Niacinamide, and
#            Cranberry Extract"
# Hook, ingredient line, texture line and CTA are new.
# ---------------------------------------------------------------------------
SCENES = [
    dict(  # HOOK 1/2 - foam coming out of the pump (pain point)
        src="A", t_in=105.0, t_out=107.4, speed=1.5,
        track=[(0, 0.55, 0.25, 0.42), (0.33, 0.47, 0.27, 0.4), (0.66, 0.55, 0.2, 0.4), (1, 0.55, 0.2, 0.38)],
        lines=[
            ("Dah mandi pun Cik Bunga", 0.03, "text"),
            ("MASIH rasa tak fresh? 😩", 0.03, "text"),
        ],
    ),
    dict(  # HOOK 2/2 - foam on the palm (product)
        src="A", t_in=108.3, t_out=110.4, speed=1.4,
        track=[(0, 0.4, 0.27, 0.48), (0.33, 0.45, 0.3, 0.52), (0.66, 0.5, 0.3, 0.5), (1, 0.55, 0.32, 0.54)],
        lines=[
            ("Intimate mousse ni", 0.03, "text"),
            ("WAJIB ada! 🛒✨", 0.03, "text"),
        ],
    ),
    dict(  # product name over the box + bottle front labels, flash after the hook
        src="C", t_in=8.6, t_out=12.6, speed=1.2, flash=True,
        track=[(0, 0.5, 0.17, 0.95)], max_zoom=1.0, text_top=0.035,
        lines=[
            ("Hana Femme", 0.1, "name"),
            ("Intimate Cleanser", 1.0, "sub"),
        ],
    ),
    dict(  # bottle front, one hand (reference line 1)
        src="B", t_in=1.0, t_out=4.6, speed=1.3,
        track=[(0, 0.32, 0.13, 0.69), (0.33, 0.36, 0.13, 0.67), (0.66, 0.45, 0.16, 0.66), (1, 0.55, 0.12, 0.65)],
        lines=[
            ("Nak Cik Bunga rasa lebih", 0.05, "text"),
            ("bersih & selesa?", 0.05, "text"),
            ("Jangan skip step ni 🫧", 0.9, "text"),
        ],
    ),
    dict(  # bottle pulled out of the box (reference line 2)
        src="A", t_in=40.3, t_out=44.3, speed=1.2,
        track=[(0, 0.4, 0.3, 1.0), (0.33, 0.38, 0.0, 0.95), (0.66, 0.4, 0.0, 0.5), (1, 0.37, 0.03, 0.65)],
        lines=[
            ("Intimate pun perlukan", 0.05, "text"),
            ("self-care juga tau.", 0.05, "text"),
            ("Baru rasa lebih bersih, fresh", 1.3, "text"),
            ("& selesa sepanjang hari 🤍🫧", 1.3, "text"),
        ],
    ),
    dict(  # bottle front label close-up (ingredients printed on it)
        src="A", t_in=115.2, t_out=120.0, speed=1.4,
        track=[(0, 0.7, 0.08, 0.9), (0.33, 0.45, 0.0, 0.95), (0.66, 0.4, 0.0, 0.95), (1, 0.42, 0.05, 0.85)], max_zoom=1.1,
        lines=[
            ("Diperkaya Vitamin E, Chamomile,", 0.05, "text"),
            ("Probiotik, Niacinamide &", 0.05, "text"),
            ("ekstrak Cranberry 🍒", 0.05, "text"),
        ],
    ),
    dict(  # back label (reference checklist, claims matched to packaging)
        src="B", t_in=23.0, t_out=35.0, speed=2.0,
        track=[(0, 0.3, 0.17, 0.75), (0.33, 0.4, 0.17, 0.75), (0.66, 0.33, 0.18, 0.75), (1, 0.33, 0.18, 0.72)],
        lines=[
            ("✅ Formula lembut untuk kawasan intim", 0.1, "check"),
            ("✅ Rasa segar & selesa lebih lama 🤍", 0.75, "check"),
            ("✅ Wangi, lembut & menyegarkan", 1.4, "check"),
            ("✅ Membantu kekalkan keseimbangan pH", 2.05, "check"),
        ],
    ),
    dict(  # foam texture on the palm
        src="A", t_in=110.6, t_out=114.6, speed=1.5,
        track=[(0, 0.45, 0.32, 0.55), (0.33, 0.42, 0.35, 0.58), (0.66, 0.42, 0.38, 0.6), (1, 0.42, 0.4, 0.6)],
        lines=[
            ("Tekstur mousse lembut,", 0.05, "text"),
            ("2-3 pam je dah cukup ✨", 0.05, "text"),
        ],
    ),
    dict(  # bottle turning back to the front (reference CTA line)
        src="B", t_in=44.6, t_out=49.6, speed=1.5,
        track=[(0, 0.35, 0.22, 0.78), (0.33, 0.38, 0.18, 0.75), (0.66, 0.36, 0.17, 0.75), (1, 0.37, 0.17, 0.73)],
        lines=[
            ("Nak tambah dalam", 0.05, "text"),
            ("self-care routine? 🫶", 0.05, "text"),
        ],
        sfx=[(0.05, "ding", 0.4)],
    ),
    dict(  # CTA 1/2 - box front
        src="A", t_in=20.6, t_out=25.1, speed=1.5,
        track=[(0, 0.5, 0.15, 0.88), (0.33, 0.55, 0.12, 0.87), (0.66, 0.55, 0.12, 0.87), (1, 0.6, 0.12, 0.87)], max_zoom=1.15,
        lines=[
            ("Jangan tunggu Cik Bunga", 0.05, "text"),
            ("rasa tak selesa dulu 😭", 0.05, "text"),
        ],
        sfx=[(0.0, "whoosh", 0.5)],
    ),
    dict(  # CTA 2/2, text only
        src="C", t_in=21.5, t_out=26.0, speed=1.2,
        track=[(0, 0.5, 0.2, 0.95)], max_zoom=1.05,
        lines=[
            ("Tekan beg kuning &", 0.08, "cta"),
            ("checkout sekarang! 🛒💛", 0.08, "cta"),
        ],
    ),
]

# layout (fractions of the 1080x1920 frame; scaled for preview)
TEXT_TOP = 0.08           # block starts ~8% from top, above the product
TEXT_SIZE = 40            # Fredoka px at 1080 wide (max; one size for all lines)
NAME_SIZE = 96            # Pacifico px at 1080 wide (max; one size for all rows)
MAX_TEXT_W = 0.88         # longest line must fit within 88% of the width
LINE_GAP = 1.06           # tight line spacing
POP_DUR = 0.28
BASE_MARGIN = 1.08        # decode slightly larger so push-ins stay sharp
PUSH = 0.03               # slow push-in across a scene
PUNCH = 0.035             # small punch-in at each cut
PUNCH_DUR = 0.22
PRODUCT_Y = 0.55          # product centre height in the frame (pushed lower if text needs room)
MAX_ZOOM = 1.6            # most a scene is cropped in to centre the product (4K source stays > 1080p)

EMOJI_RE = re.compile(
    "([\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿]"
    "[️\U0001F3FB-\U0001F3FF]*(?:‍[\U0001F000-\U0001FAFF☀-➿][️]?)*)"
)


# ---------------------------------------------------------------------------
# text rendering
# ---------------------------------------------------------------------------
class TextKit:
    def __init__(self, scale, text_size, name_size):
        self.scale = scale
        self.size = text_size
        self.font = ImageFont.truetype(FONT_TEXT, self.size)
        self.name_size = name_size
        self.name_font = ImageFont.truetype(FONT_NAME, self.name_size)
        self.sub_font = ImageFont.truetype(FONT_SUB, round(name_size * 0.7))
        self.emoji_font = ImageFont.truetype(FONT_EMOJI, 109)
        self.stroke = max(1, round(3 * scale))
        self._emoji_cache = {}

    def emoji(self, ch, h):
        key = (ch, h)
        if key not in self._emoji_cache:
            im = Image.new("RGBA", (300, 160), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((10, 10), ch, font=self.emoji_font, embedded_color=True)
            im = im.crop(im.getbbox())
            w = round(im.width * h / im.height)
            self._emoji_cache[key] = im.resize((w, h), Image.LANCZOS)
        return self._emoji_cache[key]

    def _shadowed(self, im):
        """Thin dark outline is drawn with the glyphs; add a soft drop shadow."""
        a = im.split()[3]
        sh = Image.new("RGBA", im.size, OUTLINE + (0,))
        sh.putalpha(a.point(lambda v: int(v * 0.55)))
        sh = sh.filter(ImageFilter.GaussianBlur(max(1, 3 * self.scale)))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        off = max(1, round(3 * self.scale))
        out.alpha_composite(sh, (0, off))
        out.alpha_composite(im)
        return out

    def line(self, text):
        """Render a Fredoka line with inline colour emoji -> RGBA image."""
        f = self.font
        asc, desc = f.getmetrics()
        pad = round(14 * self.scale)
        h = asc + desc + 2 * pad
        eh = round(self.size * 1.0)
        parts = [p for p in EMOJI_RE.split(text) if p]
        widths = []
        for p in parts:
            if EMOJI_RE.fullmatch(p):
                widths.append(self.emoji(p, eh).width + round(4 * self.scale))
            else:
                widths.append(round(f.getlength(p)))
        w = sum(widths) + 2 * pad
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x = pad
        for p, pw in zip(parts, widths):
            if EMOJI_RE.fullmatch(p):
                e = self.emoji(p, eh)
                y = pad + round(asc * 0.62) - e.height // 2
                im.alpha_composite(e, (x + round(2 * self.scale), y))
            else:
                d.text((x, pad), p, font=f, fill=(255, 255, 255, 255),
                       stroke_width=self.stroke, stroke_fill=OUTLINE + (235,))
            x += pw
        return self._shadowed(im)

    def sub(self, text):
        """Variant name under the label: Quicksand Bold, letter-spaced."""
        f = self.sub_font
        track = round(f.size * 0.08)
        pad = round(18 * self.scale)
        widths = [f.getlength(c) for c in text]
        w = round(sum(widths) + track * (len(text) - 1)) + 2 * pad
        asc, desc = f.getmetrics()
        im = Image.new("RGBA", (w, asc + desc + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x = pad
        for c, cw in zip(text, widths):
            d.text((x, pad), c, font=f, fill=(255, 255, 255, 255),
                   stroke_width=self.stroke, stroke_fill=OUTLINE + (235,))
            x += cw + track
        return self._shadowed(im)

    def name(self, text):
        """Pacifico product name. Returns (text_layer, marker_layer) same size."""
        f = self.name_font
        pad = round(30 * self.scale)
        bbox = f.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        w, h = tw + 2 * pad + round(40 * self.scale), th + 2 * pad
        txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text(((w - tw) // 2 - bbox[0], pad - bbox[1]), text, font=f,
                                 fill=(255, 255, 255, 255), stroke_width=self.stroke,
                                 stroke_fill=OUTLINE + (230,))
        txt = self._shadowed(txt)
        # marker: slightly tilted, rounded, hand-drawn-ish band behind the lower 70% of the word
        mk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        md = ImageDraw.Draw(mk)
        x0, x1 = round(10 * self.scale), w - round(10 * self.scale)
        y0, y1 = pad + th * 0.18, pad + th * 1.02
        r = (y1 - y0) * 0.35
        md.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=MARKER)
        mk = mk.rotate(-1.5, resample=Image.BICUBIC)
        return txt, mk


def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    return 1 - (1 - x) ** 3


def paste_scaled(frame, im, cx, cy, s, alpha):
    if s <= 0.01 or alpha <= 0:
        return
    if abs(s - 1) > 1e-3:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BICUBIC)
    if alpha < 1:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    frame.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def star(size, color=(255, 255, 255)):
    """4-point sparkle star."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    k = s * 0.09
    d.polygon([(c, 0), (c + k, c - k), (s, c), (c + k, c + k), (c, s), (c - k, c + k), (0, c), (c - k, c - k)],
              fill=color + (255,))
    im = im.resize((size, size), Image.LANCZOS)
    glow = im.filter(ImageFilter.GaussianBlur(size / 8))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


class Overlay:
    """Pre-renders a scene's text and draws it animated onto frames."""

    def __init__(self, kit, scene, W, H):
        self.kit, self.W, self.H = kit, W, H
        self.items = []
        self.sparkle_big = star(round(46 * kit.scale), (255, 244, 200))
        self.sparkle_small = star(round(28 * kit.scale))
        y = scene.get("text_top", TEXT_TOP) * H
        names = [i for i, l in enumerate(scene["lines"]) if l[2] == "name"]
        for i, (text, t0, kind) in enumerate(scene["lines"]):
            if kind == "name":
                txt, mk = kit.name(text)
                self.items.append(dict(kind=kind, t0=t0, txt=txt, mk=mk, cy=y + txt.height / 2,
                                       first=i == names[0], last=i == names[-1]))
                y += txt.height * 0.72
            elif kind == "sub":
                im = kit.sub(text)
                y += im.height * 0.08
                self.items.append(dict(kind=kind, t0=t0, im=im, cy=y + im.height / 2))
                y += im.height
            else:
                im = kit.line(text)
                self.items.append(dict(kind=kind, t0=t0, im=im, cy=y + im.height / 2))
                y += kit.size * LINE_GAP
        self.bottom = y + (kit.size * 0.45 if self.items and self.items[-1]["kind"] not in ("name", "sub") else 0)

    def draw(self, frame, t):
        cx = self.W / 2
        for it in self.items:
            dt = t - it["t0"]
            if dt < 0:
                continue
            if it["kind"] == "name":
                self._draw_name(frame, it, dt)
                continue
            p = min(dt / POP_DUR, 1)
            s = 0.55 + 0.45 * ease_out_back(p)
            a = min(dt / 0.1, 1)
            paste_scaled(frame, it["im"], cx, it["cy"], s, a)
            if it["kind"] == "sub" and dt > 0.2:
                self._sparkles(frame, cx - it["im"].width / 2, it["cy"] - it["im"].height / 2,
                               it["im"].width, it["im"].height, dt - 0.2,
                               [(0.0, 0.2, 0.6, self.sparkle_big), (1.0, 0.75, 1.4, self.sparkle_small),
                                (0.96, 0.1, 0.2, self.sparkle_small)])

    def _draw_name(self, frame, it, dt):
        txt, mk = it["txt"], it["mk"]
        w, h = txt.size
        x0 = round(self.W / 2 - w / 2)
        y0 = round(it["cy"] - h / 2)
        # marker wipes in first (0-0.35s), then the handwriting writes left->right (0.15-1.0s)
        pm = ease_out(min(dt / 0.35, 1))
        pt = min(max((dt - 0.15) / 0.85, 0), 1)
        self._wipe(frame, mk, x0, y0, pm)
        self._wipe(frame, txt, x0, y0, pt)
        # sparkles on the first label row once written
        if dt > 0.9 and it["first"]:
            self._sparkles(frame, x0, y0, w, h, dt - 0.9,
                           [(0.03, 0.15, 1.0, self.sparkle_big), (0.97, 0.2, 0.6, self.sparkle_small)])

    def _sparkles(self, frame, x0, y0, w, h, k, pts):
        for fx, fy, ph, im in pts:
            tw = 0.55 + 0.45 * math.sin(k * 7 + ph * 3)
            s = ease_out_back(min(k / 0.3, 1)) * tw
            paste_scaled(frame, im, x0 + fx * w, y0 + fy * h, s, min(k / 0.15, 1))

    @staticmethod
    def _wipe(frame, im, x0, y0, p):
        if p <= 0:
            return
        w, h = im.size
        if p >= 1:
            frame.alpha_composite(im, (x0, y0))
            return
        edge = max(4, w // 20)
        xs = np.arange(w)
        front = p * (w + edge)
        ramp = np.clip((front - xs) / edge, 0, 1)
        mask = (np.array(im.split()[3], dtype=np.float32) * ramp[None, :]).astype(np.uint8)
        im2 = im.copy()
        im2.putalpha(Image.fromarray(mask))
        frame.alpha_composite(im2, (x0, y0))


# ---------------------------------------------------------------------------
# video
# ---------------------------------------------------------------------------
def place(z, x, yt, yb, clear):
    """Crop window (left, top, size as fractions of the source) at zoom z that puts the
    product (centre x, top yt, bottom yb) horizontally centred and vertically around
    PRODUCT_Y, but never with its top above `clear` (the bottom of the text block)."""
    w = 1 / z
    left = min(max(x - w / 2, 0), 1 - w)
    want = max(PRODUCT_Y, clear + 0.03 + (yb - yt) * z / 2)  # product centre in the frame
    top = min(max((yt + yb) / 2 - want * w, 0), 1 - w)
    return left, top, w


def framing(sc, clear):
    """Pick the crop zoom for a scene and return (zoom, u -> product box).

    `track` lists (u, x, top, bottom): the product's centre and vertical extent in the
    source frame at point u (0..1) of the scene. The zoom (1..max_zoom) is chosen to best
    centre the product while keeping it below the text and inside the frame."""
    track = sc.get("track", [(0, 0.5, 0.3, 0.9)])
    zmax = sc.get("max_zoom", MAX_ZOOM)

    def cost(z):
        c = 0.15 * (z - 1)
        for _, x, yt, yb in track:
            left, top, w = place(z, x, yt, yb, clear)
            c += (abs((x - left) / w - 0.5) + 3 * max(0, clear + 0.01 - (yt - top) / w)
                  + 2 * max(0, (yb - top) / w - 0.98)) / len(track)
        return c
    zs = [1 + k * 0.02 for k in range(int((zmax - 1) / 0.02) + 1)]
    zoom = min(zs, key=cost)

    def pos(u):
        if u <= track[0][0]:
            return track[0][1:]
        for a, b in zip(track, track[1:]):
            if u <= b[0]:
                k = (u - a[0]) / max(b[0] - a[0], 1e-6)
                k = k * k * (3 - 2 * k)  # smoothstep so the crop eases between points
                return tuple(p + (q - p) * k for p, q in zip(a[1:], b[1:]))
        return track[-1][1:]
    return zoom, pos


def scene_frames(path, sc, BW, BH):
    """Yield RGB frames (BW x BH, whole 9:16 source frame) for a scene, decoded from the original clip."""
    dur_out = (sc["t_out"] - sc["t_in"]) / sc["speed"]
    n = round(dur_out * FPS)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:stream_side_data=rotation", "-of", "default=nw=1", path],
        capture_output=True, text=True).stdout
    vals = dict(l.split("=", 1) for l in probe.split() if "=" in l)
    w, h = int(vals["width"]), int(vals["height"])
    if abs(int(float(vals.get("rotation", 0)))) == 90:
        w, h = h, w
    # largest centred 9:16 window (the raw clips are already 9:16, so usually none)
    cw, ch = (h * 9 / 16, h) if w / h > 9 / 16 else (w, w * 16 / 9)
    cw, ch = round(cw / 2) * 2, round(ch / 2) * 2
    crop = f"crop={cw}:{ch}," if (cw, ch) != (w, h) else ""
    vf = (f"setpts=(PTS-STARTPTS)/{sc['speed']},fps={FPS},{crop}"
          f"scale={BW}:{BH}:flags=lanczos,format=rgb24")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{sc['t_in']}", "-t", f"{sc['t_out'] - sc['t_in']}",
           "-i", path, "-an", "-vf", vf, "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fsz = BW * BH * 3
    last = None
    for _ in range(n):
        buf = proc.stdout.read(fsz)
        if len(buf) == fsz:
            last = Image.frombuffer("RGB", (BW, BH), buf, "raw", "RGB", 0, 1)
        yield last
    proc.kill()  # stop decoding; we have all frames we need
    proc.stdout.close()
    proc.wait()


def build_sfx_events(scenes_meta):
    ev = []
    alt = 0
    for start, sc, ov in scenes_meta:
        if sc.get("flash") and not any(l[2] == "name" for l in sc["lines"]):
            ev.append((start, "whoosh", 0.55, 0.0))  # name scenes get their own whoosh
        for t, name, g in sc.get("sfx", []):
            ev.append((start + t, name, g, 0.0))
        seen_t = set()
        for it in ov.items:
            t = start + it["t0"]
            if it["kind"] == "name":
                if it["first"]:
                    ev.append((t, "whoosh", 0.45, -0.2))
                ev.append((t + 0.15, "pen", 0.55, 0.1))
                continue
            if it["kind"] == "sub":
                ev += [(t, "bubble", 0.5, 0.0), (t + 0.1, "shimmer", 0.55, 0.0)]
                continue
            key = round(t, 2)
            if key in seen_t:  # two-row sentence: one sound
                continue
            seen_t.add(key)
            if it["kind"] == "check":
                ev.append((t + 0.02, "tick", 0.55, 0.0))
            elif it["kind"] == "cta":
                ev.append((t + 0.02, "kaching", 0.75, 0.0))
            else:
                ev.append((t, "pop" if alt % 2 == 0 else "bubble", 0.6, 0.0))
                alt += 1
        texts = " ".join(l[0] for l in sc["lines"])
        if "✨" in texts:
            first = next(l for l in sc["lines"] if "✨" in l[0])
            ev.append((start + first[1] + 0.12, "sparkle", 0.45, 0.25))
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder with the original clips")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", action="store_true", help="540x960 quick render")
    args = ap.parse_args()

    W, H = (540, 960) if args.preview else (1080, 1920)
    scale = W / 1080
    BW, BH = round(W * BASE_MARGIN / 2) * 2, round(H * BASE_MARGIN / 2) * 2
    # one font size for every text line (and one for every label row): the largest
    # size at which the longest line still fits
    probe = TextKit(scale, round(TEXT_SIZE * scale), round(NAME_SIZE * scale))
    texts = [l[0] for sc in SCENES for l in sc["lines"] if l[2] not in ("name", "sub")]
    names = [l[0] for sc in SCENES for l in sc["lines"] if l[2] == "name"]
    tw = max(probe.line(t).width for t in texts)
    nw = max(probe.name(t)[0].width for t in names)
    tsize = int(probe.size * min(1, MAX_TEXT_W * W / tw))
    nsize = int(probe.name_size * min(1, 0.95 * W / nw))
    print(f"text size {tsize}px, label size {nsize}px", flush=True)
    kit = TextKit(scale, tsize, nsize)

    meta, start = [], 0.0
    for sc in SCENES:
        dur = (sc["t_out"] - sc["t_in"]) / sc["speed"]
        assert dur < 10, f"scene too long: {dur:.2f}s"
        meta.append((start, sc, Overlay(kit, sc, W, H)))
        start += round(dur * FPS) / FPS
    total = start
    assert total < 60
    print(f"{len(SCENES)} scenes, total {total:.2f}s", flush=True)

    tmp = tempfile.mkdtemp(prefix="hanafemme_")
    wav = os.path.join(tmp, "sfx.wav")
    sfx.mix_timeline(build_sfx_events(meta), total, wav)

    enc = (["-c:v", "libx264", "-preset", "medium", "-crf", "23"] if args.preview else
           ["-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high", "-tune", "film"])
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav,
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           *enc, "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", args.out]
    out = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for i, (s0, sc, ov) in enumerate(meta):
        dur = (sc["t_out"] - sc["t_in"]) / sc["speed"]
        path = os.path.join(args.src, CLIPS[sc["src"]])
        zoom, pos = framing(sc, ov.bottom / H)
        # decode big enough that the cropped window is still >= output resolution
        DW, DH = round(BW * zoom / 2) * 2, round(BH * zoom / 2) * 2
        print(f"scene {i + 1}: crop zoom {zoom:.2f}", flush=True)
        for fi, base in enumerate(scene_frames(path, sc, DW, DH)):
            t = fi / FPS
            z = 1 + PUSH * (t / dur) + PUNCH * (1 - ease_out(min(t / PUNCH_DUR, 1)))
            cw, ch = DW / (zoom * z), DH / (zoom * z)  # zoom 1, z 1 = whole source frame
            left, top, _ = place(zoom, *pos(t / dur), ov.bottom / H)
            # push/punch-in zooms around the centre of the product-framed window
            x0 = (left + 0.5 / zoom) * DW - cw / 2
            y0 = (top + 0.5 / zoom) * DH - ch / 2
            box = (x0, y0, x0 + cw, y0 + ch)
            frame = base.resize((W, H), Image.BICUBIC, box=box).convert("RGBA")
            ov.draw(frame, t)
            if sc.get("flash") and t < 0.25:
                a = int(220 * (1 - t / 0.25) ** 1.5)
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
            out.stdin.write(frame.convert("RGB").tobytes())
        print(f"scene {i + 1}/{len(meta)} done", flush=True)
    out.stdin.close()
    out.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
