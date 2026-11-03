#!/usr/bin/env python3
"""TikTok edit for D'Aura Stevia Natural Sweetener (10 ml, 250 drops).

Renders straight from the original iPhone clips (HLG HDR, tone-mapped to SDR
without any grading):
  python3 stevia_edit.py --src "<folder with raw clips>" --out preview.mp4 --preview
  python3 stevia_edit.py --src "<folder with raw clips>" --out final.mp4

- 1080x1920 @ 30 fps (preview: 540x960), original audio removed, no music
- text in the reference style (white, centred, ~18.5% from top, thin dark outline)
- synthesised SFX only

The raw clips have no speech (only room noise), so every line comes from the
packaging. Claims used, as printed on the bottle:
  front : "Stevia Natural Sweetener", "0 Calorie", "100% Pure", "10ml", "250 Drops"
  side  : Khasiatnya - "Pengganti gula tanpa kalori",
          "150 - 250 kali ganda lebih manis daripada gula"
  back  : Penggunaan - "Masukkan 3 - 4 titis pemanis ke dalam satu cawan (250 ml)
          minuman, sejuk atau panas"; "*Goncang sebelum minum";
          table - Calories 0, Fat 0, Protein 0, Carbohydrate 0, Calsium 0, Glucose 0
Left out on purpose (TikTok ads review): the label line about diabetes/obesity.
"""
import argparse

from engine import render

MARKER_GREEN = (118, 184, 52, 170)  # translucent brand green behind the product name

CLIPS = {
    "A": "IMG_0779.MOV",  # 13.7 s, drawer background: tilts, front label
    "B": "IMG_0780.MOV",  # 29.1 s, window background: front, side (khasiat), back
    "C": "IMG_0781.MOV",  # 33.6 s, sky/balcony background: front, side, back
}

# Times are seconds in the source clip; text times are seconds from the start
# of the scene. Every scene is < 5 s. Line kinds: text, check (✅ list row),
# name (Pacifico + marker), cta (kaching).
SCENES = [
    dict(  # HOOK 1/2 - close, tilted bottle against the sky
        src="C", t_in=8.6, t_out=10.4, speed=1.2,
        lines=[
            ("Nak kurangkan gula,", 0.03, "text"),
            ("tapi tak boleh tak manis? 😩", 0.03, "text"),
        ],
    ),
    dict(  # HOOK 2/2
        src="B", t_in=3.6, t_out=5.4, speed=1.2,
        lines=[
            ("Stevia titis ni", 0.03, "text"),
            ("WAJIB ada! 🛒✨", 0.03, "text"),
        ],
    ),
    dict(  # product name over the front label, white flash after the hook
        src="A", t_in=8.5, t_out=12.5, speed=1.2, flash=True,
        lines=[
            ("D'Aura Stevia", 0.1, "name"),
            ("Natural Sweetener", 0.7, "name"),
        ],
        sfx=[(1.55, "shimmer", 0.6)],
    ),
    dict(  # front badges
        src="C", t_in=11.0, t_out=13.8, speed=1.2,
        lines=[
            ("Tengok label dia 👀", 0.05, "text"),
            ("0 Calorie & 100% Pure ✨", 0.75, "text"),
        ],
        sfx=[(0.75, "ding", 0.4)],
    ),
    dict(  # side label: Khasiatnya
        src="B", t_in=7.0, t_out=11.0, speed=1.2,
        lines=[
            ("Khasiatnya:", 0.05, "text"),
            ("✅ Pengganti gula tanpa kalori", 0.7, "check"),
            ("✅ 150-250x lebih manis", 1.5, "check"),
            ("daripada gula", 1.5, "check"),
        ],
    ),
    dict(  # back label: Penggunaan
        src="B", t_in=13.0, t_out=19.0, speed=1.6,
        lines=[
            ("Cara guna senang je 💧", 0.05, "text"),
            ("✅ 3-4 titis untuk 1 cawan (250ml)", 0.75, "check"),
            ("✅ Minuman sejuk atau panas", 1.55, "check"),
            ("✅ Goncang sebelum minum", 2.35, "check"),
        ],
    ),
    dict(  # back label: nutrition table
        src="C", t_in=21.5, t_out=26.0, speed=1.5,
        lines=[
            ("Kalori, lemak, karbohidrat", 0.08, "text"),
            ("& glukos semua 0 😍", 0.08, "text"),
        ],
    ),
    dict(  # size
        src="A", t_in=1.3, t_out=5.0, speed=1.5,
        lines=[
            ("Botol 10ml kecil comel", 0.08, "text"),
            ("tapi dapat 250 titis 💧", 0.08, "text"),
        ],
    ),
    dict(  # CTA 1/2
        src="C", t_in=27.5, t_out=31.0, speed=1.2,
        lines=[
            ("Jangan tunggu ketagih gula", 0.08, "text"),
            ("makin teruk 😭", 0.08, "text"),
        ],
        sfx=[(0.0, "whoosh", 0.5)],
    ),
    dict(  # CTA 2/2, text only
        src="B", t_in=0.0, t_out=2.9, speed=1.2,
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
    render(SCENES, CLIPS, args.src, args.out, args.preview, marker=MARKER_GREEN, tonemap=True)


if __name__ == "__main__":
    main()
