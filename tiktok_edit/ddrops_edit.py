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
    "C": "VID20261107103027.mp4",  # kitchen: drop into the milk
}

eng.MARKER_BLUE = (110, 50, 175, 190)  # Ddrops purple highlighter behind the name
eng.TEXT_SIZE = 42   # body text, small
eng.NAME_SIZE = 135  # big product name (Pacifico)
eng.SUB_RATIO = 0.38  # small line under the product name
eng.FONT_SUB = eng.FONT_TEXT  # Fredoka for the line under the name
eng.FONT_POINT = eng.os.path.join(eng.HERE, "fonts", "Mali-Medium.ttf")  # cute, not bold, for ✅ points
eng.TEXT_TOP = 0.12
# mini zoom-in at every cut and every new line/point, anchored at the bottom of
# the text so the product grows downwards and never slides under the text
eng.PUNCH = 0.0
eng.STEP_ZOOM = 0.025
eng.STEP_MAX = 0.08
eng.ZOOM_AT_TEXT = True
eng.BASE_MARGIN = 1.12  # decode larger so the zoom stays sharp

# Body text is copied word-for-word from the reference video (only line breaks
# differ; "✨" bullets shown as ✅). Hook and the "Tekan beg kuning" line follow
# the brief. Dropped: "1 titis = 15 biji telur" (not on the packaging).
# Shots: sofa footage (box A, bottle B) matched to the text, plus the
# drop-into-milk shot from C (hook and "Cara guna").
# Every text block sits above the product: text_top is set per shot so the
# block ends before the top of the bottle/box.
eng.SCENES = [
    dict(  # HOOK 1/2 - bottle front on the sofa (cap starts ~25% down)
        src="B", t_in=39.0, t_out=40.8, speed=1.2,
        lines=[
            ("Anak susah makan &", 0.05, "text"),
            ("jarang kena matahari? 😩", 0.05, "text"),
        ],
    ),
    dict(  # HOOK 2/2 - the drop falling into the milk; one line between dropper and cup
        src="C", t_in=28.0, t_out=29.8, speed=1.2, text_top=0.275,
        lines=[
            ("Vitamin D3 setitis ni WAJIB ada! 🛒✨", 0.03, "text"),
        ],
    ),
    dict(  # box front: "Helps support bone development and immune function" (box top ~11%)
        src="A", t_in=6.0, t_out=9.8, speed=1.2, text_top=0.025,
        lines=[
            ("1 titik, besar manfaatnya 🤍", 0.05, "text"),
            ("Mummy dah masukkan Vitamin D3", 0.6, "text"),
            ("dalam rutin harian anak belum? 👀", 0.6, "text"),
        ],
    ),
    dict(  # title card over the bottle front (white flash)
        src="B", t_in=0.5, t_out=4.5, speed=1.2, flash=True, text_top=0.025,
        lines=[
            ("Kids Ddrops", 0.1, "name"),
            ("Vitamin D3", 0.9, "sub"),
        ],
    ),
    dict(  # box back panel: "healthy growth and development" (box top ~13.5%)
        src="A", t_in=32.5, t_out=35.5, speed=1.2, text_top=0.04,
        lines=[
            ("Vitamin D ni bagus untuk", 0.08, "text"),
            ("perkembangan anak terutama", 0.08, "text"),
            ("untuk baby yang Fully Direct feed", 0.08, "text"),
        ],
    ),
    dict(  # box front: 600 IU, for ages 1 year+ (box top ~10%)
        src="A", t_in=3.0, t_out=6.0, speed=1.1, text_top=0.035,
        lines=[
            ("Pilih ikut umur anak", 0.08, "text"),
            ("Yang ni 600IU sesuai anak umur 1-18 tahun", 0.7, "text"),
        ],
    ),
    dict(  # bottle front coming up into frame (cap 30-45% down)
        src="B", t_in=34.8, t_out=38.4, speed=1.2, text_top=0.045,
        lines=[
            ("Boleh tambah dalam rutin harian kalau", 0.05, "text"),
            ("anak ada situasi macam ni :", 0.05, "text"),
            ("✅ Kurang selera makan", 0.5, "check"),
            ("✅ Kurang terdedah kepada", 0.95, "check"),
            ("cahaya matahari", 0.95, "check"),
            ("✅ Kurang dapat sumber Vitamin D", 1.4, "check"),
            ("daripada makanan harian", 1.4, "check"),
            ("✅ Kerap sakit", 1.85, "check"),
        ],
    ),
    dict(  # box side panel: "Just one drop" / "Take 1 drop daily" (box top ~13%)
        src="A", t_in=65.5, t_out=68.6, speed=1.2, text_top=0.05,
        lines=[
            ("cukup 1 titis sehari je", 0.08, "text"),
            ("banyak manfaat", 0.08, "text"),
        ],
        sfx=[(0.6, "ding", 0.45)],
    ),
    dict(  # drop into the milk; text sits between the dropper tip and the cup
        src="C", t_in=25.4, t_out=29.8, speed=1.2, text_top=0.27,
        lines=[
            ("Cara guna :", 0.05, "text"),
            ("✅ Titiskan dalam susu", 0.6, "check"),
            ("✅ Direct dalam mulut anak", 1.2, "check"),
            ("✅ Guna sudu", 1.8, "check"),
        ],
    ),
    dict(  # box back panel: strong bones, immune functions (box top ~14%)
        src="A", t_in=35.5, t_out=39.9, speed=1.2, text_top=0.025,
        lines=[
            ("Vitamin D bagus", 0.05, "text"),
            ("✅ Menyokong perkembangan tulang dan gigi", 0.6, "check"),
            ("✅ Meningkatkan penyerapan kalsium", 1.25, "check"),
            ("✅ Menyokong fungsi sistem imun", 1.9, "check"),
        ],
    ),
    dict(  # bottle front
        src="B", t_in=5.0, t_out=9.5, speed=1.2, text_top=0.06,
        lines=[
            ("satu botol tahan sampai 3 bulan!", 0.08, "text"),
            ("Jadi memang berbaloi untuk", 0.08, "text"),
            ("dijadikan rutin harian anak ✨", 0.08, "text"),
        ],
    ),
    dict(  # CTA, text only - box front (box top ~11%)
        src="A", t_in=6.3, t_out=9.6, speed=1.1, text_top=0.03,
        lines=[
            ("Order Now Mummy ! 🛒💛", 0.08, "cta"),
            ("Tekan beg kuning & checkout sekarang!", 0.08, "cta"),
        ],
    ),
]

if __name__ == "__main__":
    eng.main()
