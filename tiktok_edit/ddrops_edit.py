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
Scene order follows the reference video.
"""
import avco_edit as eng

# all 3840x2160 HEVC, rotated to portrait (2160x3840 = 9:16, no crop)
eng.CLIPS = {
    "A": "VID20261107102613.mp4",  # box on the sofa: front, back panel, side panel
    "B": "VID20261107102831.mp4",  # bottle in hand on the sofa
    "C": "VID20261107103027.mp4",  # kitchen: milk bottle, dropper, drop into milk
    "D": "VID20261107103216.mp4",  # kitchen: bottle front label
}

eng.MARKER_BLUE = (110, 50, 175, 190)  # Ddrops purple highlighter behind the name

eng.SCENES = [
    dict(  # HOOK 1/2 - the drop falling into the milk
        src="C", t_in=27.6, t_out=29.6, speed=1.25,
        lines=[
            ("Anak susah makan &", 0.05, "text"),
            ("jarang kena matahari? 😩", 0.05, "text"),
        ],
    ),
    dict(  # HOOK 2/2 - bottle front next to the milk bottle
        src="C", t_in=48.6, t_out=50.4, speed=1.2,
        lines=[
            ("Vitamin D3 setitis ni", 0.03, "text"),
            ("WAJIB ada! 🛒✨", 0.03, "text"),
        ],
    ),
    dict(  # product name over the front label (white flash after the hook)
        src="D", t_in=5.0, t_out=9.0, speed=1.2, flash=True, text_top=0.10,
        lines=[
            ("Kids Ddrops", 0.1, "name"),
            ("Liquid Vitamin D3", 0.9, "sub"),
        ],
    ),
    dict(  # box front
        src="A", t_in=2.0, t_out=7.0, speed=1.3,
        lines=[
            ("Mummy dah masukkan Vitamin D3", 0.08, "text"),
            ("dalam rutin harian anak belum? 👀", 0.08, "text"),
        ],
    ),
    dict(  # box close-up: "Helps support bone development"
        src="A", t_in=18.5, t_out=23.5, speed=1.2,
        lines=[
            ("Bantu sokong tumbesaran &", 0.08, "text"),
            ("perkembangan si kecil", 0.08, "text"),
            ("dengan 1 titis je 💜", 0.9, "text"),
        ],
    ),
    dict(  # bottle front: 600 IU
        src="B", t_in=0.5, t_out=5.0, speed=1.2,
        lines=[
            ("Yang ni 600IU sesuai", 0.08, "text"),
            ("untuk anak 1 tahun ke atas 👶", 0.08, "text"),
        ],
    ),
    dict(  # bottle front in the kitchen
        src="D", t_in=14.5, t_out=21.5, speed=1.8,
        lines=[
            ("Boleh tambah dalam rutin", 0.05, "text"),
            ("harian kalau anak:", 0.05, "text"),
            ("✅ Kurang selera makan", 0.75, "check"),
            ("✅ Jarang kena cahaya matahari", 1.4, "check"),
            ("✅ Kurang dapat Vitamin D", 2.05, "check"),
            ("daripada makanan harian", 2.05, "check"),
        ],
    ),
    dict(  # opening the dropper over the milk
        src="C", t_in=21.6, t_out=25.6, speed=1.2,
        lines=[
            ("Cukup 1 titis sehari je 💧", 0.08, "text"),
            ("senang & tak leceh!", 0.9, "text"),
        ],
        sfx=[(0.9, "ding", 0.45)],
    ),
    dict(  # closing and shaking the milk bottle
        src="C", t_in=37.5, t_out=45.5, speed=2.0,
        lines=[
            ("Cara guna:", 0.05, "text"),
            ("✅ Titis dalam susu / minuman", 0.6, "check"),
            ("✅ Letak atas makanan", 1.25, "check"),
            ("✅ Titis atas jari yang bersih", 1.9, "check"),
        ],
    ),
    dict(  # back panel
        src="A", t_in=33.0, t_out=44.0, speed=2.5,
        lines=[
            ("Vitamin D3 bagus untuk:", 0.05, "text"),
            ("✅ Sokong tulang yang kuat", 0.6, "check"),
            ("✅ Sokong fungsi otot", 1.25, "check"),
            ("✅ Sokong sistem imun", 1.9, "check"),
        ],
    ),
    dict(  # side panel: directions, no preservatives, USDA organic, non-GMO
        src="A", t_in=59.5, t_out=67.5, speed=2.0,
        lines=[
            ("✅ Tanpa pengawet & gula", 0.1, "check"),
            ("✅ Tanpa perisa & pewarna tiruan", 0.75, "check"),
            ("✅ USDA Organic & Non-GMO", 1.4, "check"),
        ],
    ),
    dict(  # box front: "100 drops"
        src="A", t_in=7.0, t_out=11.5, speed=1.2,
        lines=[
            ("1 kotak = 100 titis 💧", 0.08, "text"),
            ("tahan lebih 3 bulan!", 0.08, "text"),
            ("Memang berbaloi ✨", 1.0, "text"),
        ],
    ),
    dict(  # CTA 1/2 - bottle front on the sofa
        src="B", t_in=36.5, t_out=42.5, speed=1.5,
        lines=[
            ("Jangan tunggu si kecil", 0.08, "text"),
            ("kurang Vitamin D 😭", 0.08, "text"),
        ],
        sfx=[(0.0, "whoosh", 0.5)],
    ),
    dict(  # CTA 2/2, text only
        src="C", t_in=52.0, t_out=56.0, speed=1.1,
        lines=[
            ("Tekan beg kuning &", 0.08, "cta"),
            ("checkout sekarang! 🛒💛", 0.08, "cta"),
        ],
    ),
]

if __name__ == "__main__":
    eng.main()
