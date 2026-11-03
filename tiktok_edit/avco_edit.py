#!/usr/bin/env python3
"""TikTok edit for D'AURA AVCO Aromatic Virgin Coconut Oil (Morning Dew).

Renders straight from the original 4K phone clips:
  python3 avco_edit.py --src "<folder with raw clips>" --out preview.mp4 --preview
  python3 avco_edit.py --src "<folder with raw clips>" --out final.mp4

- 1080x1920 @ 30 fps (preview: 540x960), original colours, original audio removed
- text in the reference style (white, centred, ~18-25% from top, thin dark outline)
- synthesised SFX only, no music
"""
import argparse

from engine import render

MARKER_BLUE = (60, 150, 255, 150)  # translucent blue highlighter behind the label

# Source clips (all 3840x2160 HEVC; A/D are portrait, B/C landscape after autorotate)
CLIPS = {
    "A": "VID20260908154605.mp4",  # front + back label, pump
    "B": "VID20260908154728.mp4",  # oil swatch on back of hand (landscape)
    "C": "VID20260908154758.mp4",  # oil rubbed in, glossy hand (landscape)
    "D": "VID20260908155004.mp4",  # front label, different angles
}

# ---------------------------------------------------------------------------
# Edit decision list. Times are seconds in the source clip; text times are
# seconds from the start of the scene. cx = horizontal crop centre (0..1) for
# landscape clips. Every scene is < 5 s.
# Body text is copied word-for-word from the reference video (two typos fixed:
# "baban" -> "bahan", "ristko" -> "risiko"; "-" bullets shown as ✅).
# Only the hook and the CTA are new.
# ---------------------------------------------------------------------------
SCENES = [
    dict(  # HOOK 1/2 - product front
        src="A", t_in=0.0, t_out=2.0, speed=1.2,
        lines=[
            ("Nak bersalin mudah,", 0.05, "text"),
            ("tak koyak, tak jahit? 🤰", 0.05, "text"),
        ],
    ),
    dict(  # HOOK 2/2 - oil texture
        src="B", t_in=2.8, t_out=4.6, speed=1.2, cx=0.56,
        lines=[
            ("Minyak kelapa dara ni", 0.03, "text"),
            ("WAJIB ada! 🛒✨", 0.03, "text"),
        ],
    ),
    dict(  # product label over the front of the bottle
        src="D", t_in=7.6, t_out=12.4, speed=1.2, flash=True, text_top=0.115,
        lines=[
            ("D'Aura Aromatic", 0.1, "name"),
            ("Virgin Coconut Oil", 0.7, "name"),
            ("Morning Dew", 1.5, "sub"),
        ],
    ),
    dict(
        src="A", t_in=10.0, t_out=15.5, speed=1.4,
        lines=[
            ("Ibu preggy dah buat urutan", 0.08, "text"),
            ("perineum belum ?", 0.08, "text"),
            ("34 week dah boleh", 1.3, "text"),
            ("start dah !", 1.3, "text"),
        ],
    ),
    dict(  # back label
        src="A", t_in=17.5, t_out=26.5, speed=2.0,
        lines=[
            ("Kegunaan minyak kelapa dara", 0.05, "text"),
            ("✅ bantu menganjalkan laluan bersalin", 0.7, "check"),
            ("✅ boleh guna untuk urutan badan", 1.35, "check"),
            ("✅ menyihatkan rambut", 2.0, "check"),
            ("(rambut kering & bercabang)", 2.0, "check"),
        ],
    ),
    dict(  # glossy hand, zoomed in on the oiled skin
        src="C", t_in=0.0, t_out=6.0, speed=1.5, cx=0.45, cy=0.55, zoom=1.3,
        lines=[
            ("100% bahan semulajadi (selamat", 0.1, "text"),
            ("untuk ibu & bayi tanpa bahan kimia)", 0.1, "text"),
        ],
    ),
    dict(  # pump
        src="A", t_in=48.5, t_out=53.5, speed=2.0,
        lines=[
            ("bau aroma bunga", 0.08, "text"),
            ("yang lembut", 0.08, "text"),
        ],
    ),
    dict(
        src="D", t_in=17.0, t_out=21.6, speed=1.2,
        lines=[
            ("Ikhtiar untuk kurangkan", 0.08, "text"),
            ("risiko koyakan & jahitan", 0.08, "text"),
            ("semasa bersalin !", 0.08, "text"),
            ("Dengan buat urutan perineum", 1.2, "text"),
        ],
        sfx=[(0.1, "ding", 0.45)],
    ),
    dict(  # CTA 1/2
        src="D", t_in=0.8, t_out=4.0, speed=1.2,
        lines=[
            ("Jangan tunggu dah sarat", 0.08, "text"),
            ("baru nak start 😭", 0.08, "text"),
        ],
        sfx=[(0.0, "whoosh", 0.5)],
    ),
    dict(  # CTA 2/2, text only
        src="D", t_in=26.0, t_out=30.4, speed=1.1,
        lines=[
            ("Tekan beg kuning &", 0.08, "cta"),
            ("checkout sekarang! 🛒💛", 0.08, "cta"),
        ],
    ),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder with the original clips")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", action="store_true", help="540x960 quick render")
    args = ap.parse_args()
    render(SCENES, CLIPS, args.src, args.out, args.preview, marker=MARKER_BLUE)


if __name__ == "__main__":
    main()
