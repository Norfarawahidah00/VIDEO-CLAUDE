#!/usr/bin/env python3
"""TikTok edit for Kids Ddrops Booster Liquid Vitamin D3 600 IU.

Uses the render engine in avco_edit.py with its own clip list and scene list.
  python3 ddrops_edit.py --src "<folder with raw clips>" --out preview.mp4 --preview
  python3 ddrops_edit.py --src "<folder with raw clips>" --out final.mp4

The raw clips have no product speech (only background noise), so all text is
taken from the packaging:
  front : "Helps support bone development and immune function", "For ages 1 year+",
          "100 drops", "Vitamin D3 600 IU per drop", "Organic"
  back  : "helps to support your little one's healthy growth and development in just
          one drop", "helps support the development of strong bones, muscles and
          immune functions", "Free from preservatives, artificial flavors, sugars ..."
  side  : "Take 1 drop daily ... May be put on food, added to a drink or licked from a
          clean surface such as a washed finger", "No preservatives, artificial
          flavors or colors", USDA Organic, Non-GMO Project Verified
Scene order, shots and body text follow the reference video.
"""
import avco_edit as eng

# all 3840x2160 HEVC, rotated to portrait (2160x3840 = 9:16, no crop)
eng.CLIPS = {
    "A": "VID20261107102613.mp4",  # box on the sofa: front, back panel, side panel
    "B": "VID20261107102831.mp4",  # bottle in hand on the sofa
    "C": "VID20261107103027.mp4",  # kitchen: drop into the milk (hook only)
}

eng.MARKER_BLUE = (110, 50, 175, 190)  # Ddrops purple highlighter behind the name
eng.TEXT_SIZE = 50   # body text (smaller than the AVCO edit)
eng.NAME_SIZE = 135  # bigger product name
eng.SUB_RATIO = 0.38  # smaller line under the product name
eng.FONT_SUB = eng.FONT_TEXT  # Fredoka for the line under the name (name stays Pacifico)

# Body text is copied word-for-word from the reference video (only line breaks
# differ so every line fits; "✨" bullets shown as ✅). Hook and the
# "Tekan beg kuning" line follow the brief. Dropped: "1 titis = 15 biji telur"
# (not on the packaging, can't be proven for TikTok ads review).
# Shots follow the reference: only the sofa footage (A, B) plus the
# drop-into-milk shot from C, reused where the reference shows the cup.
eng.SCENES = [
    dict(  # HOOK 1/2 - dropper moving over the milk
        src="C", t_in=26.2, t_out=28.0, speed=1.2,
        lines=[
            ("Anak susah makan &", 0.05, "text"),
            ("jarang kena matahari? 😩", 0.05, "text"),
        ],
    ),
    dict(  # HOOK 2/2 - the drop falling into the milk
        src="C", t_in=28.0, t_out=29.8, speed=1.2,
        lines=[
            ("Vitamin D3 setitis ni", 0.03, "text"),
            ("WAJIB ada! 🛒✨", 0.03, "text"),
        ],
    ),
    dict(  # ref 0-2.4s: drop into the cup
        src="C", t_in=26.6, t_out=29.8, speed=1.2,
        lines=[
            ("1 titik, besar manfaatnya 🤍", 0.05, "text"),
            ("Mummy dah masukkan Vitamin D3", 0.6, "text"),
            ("dalam rutin harian anak belum? 👀", 0.6, "text"),
        ],
    ),
    dict(  # ref 2.5-4s: title card over the product (white flash)
        src="B", t_in=0.5, t_out=4.5, speed=1.2, flash=True, text_top=0.10,
        lines=[
            ("Kids Ddrops", 0.1, "name"),
            ("Vitamin D3", 0.9, "sub"),
        ],
    ),
    dict(  # ref 4-7s: box in hand, turning to the back
        src="A", t_in=23.0, t_out=28.5, speed=1.2,
        lines=[
            ("Vitamin D ni bagus untuk", 0.08, "text"),
            ("perkembangan anak terutama", 0.08, "text"),
            ("untuk baby yang Fully Direct feed", 0.08, "text"),
        ],
    ),
    dict(  # ref 7-9.5s: box front close-up (600 IU)
        src="A", t_in=11.0, t_out=16.0, speed=1.2,
        lines=[
            ("Pilih ikut umur anak", 0.08, "text"),
            ("Yang ni 600IU sesuai anak", 0.7, "text"),
            ("umur 1-18 tahun", 0.7, "text"),
        ],
    ),
    dict(  # ref 9.5-15s: holding the bottle
        src="B", t_in=0.5, t_out=9.5, speed=2.0,
        lines=[
            ("Boleh tambah dalam rutin harian kalau", 0.05, "text"),
            ("anak ada situasi macam ni :", 0.05, "text"),
            ("✅ Kurang selera makan", 0.6, "check"),
            ("✅ Kurang terdedah kepada", 1.15, "check"),
            ("cahaya matahari", 1.15, "check"),
            ("✅ Kurang dapat sumber Vitamin D", 1.7, "check"),
            ("daripada makanan harian", 1.7, "check"),
            ("✅ Kerap sakit", 2.25, "check"),
        ],
    ),
    dict(  # ref 15-17.5s: holding the bottle
        src="B", t_in=36.0, t_out=39.6, speed=1.2,
        lines=[
            ("cukup 1 titis sehari je", 0.08, "text"),
            ("banyak manfaat", 0.08, "text"),
        ],
        sfx=[(0.6, "ding", 0.45)],
    ),
    dict(  # ref 17.5-20s: drop into the milk
        src="C", t_in=25.4, t_out=29.8, speed=1.2,
        lines=[
            ("Cara guna :", 0.05, "text"),
            ("✅ Titiskan dalam susu", 0.6, "check"),
            ("✅ Direct dalam mulut anak", 1.2, "check"),
            ("✅ Guna sudu", 1.8, "check"),
        ],
    ),
    dict(  # ref 20-24s: box back panel
        src="A", t_in=32.0, t_out=42.5, speed=2.5,
        lines=[
            ("Vitamin D bagus", 0.05, "text"),
            ("✅ Menyokong perkembangan", 0.6, "check"),
            ("tulang dan gigi", 0.6, "check"),
            ("✅ Meningkatkan penyerapan kalsium", 1.25, "check"),
            ("✅ Menyokong fungsi sistem imun", 1.9, "check"),
        ],
    ),
    dict(  # ref 24-27s: product shot (box front, "100 drops")
        src="A", t_in=2.0, t_out=6.6, speed=1.2,
        lines=[
            ("satu botol tahan sampai 3 bulan!", 0.08, "text"),
            ("Jadi memang berbaloi untuk", 0.08, "text"),
            ("dijadikan rutin harian anak ✨", 0.08, "text"),
        ],
    ),
    dict(  # CTA, text only
        src="B", t_in=39.4, t_out=42.6, speed=1.1,
        lines=[
            ("Order Now Mummy ! 🛒💛", 0.08, "cta"),
            ("Tekan beg kuning & checkout sekarang!", 0.08, "cta"),
        ],
    ),
]

if __name__ == "__main__":
    eng.main()
