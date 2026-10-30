# AVCO Morning Dew – TikTok edit

Script that cuts the raw D'AURA AVCO clips into a <60 s TikTok video
(1080x1920, 30 fps) with reference-style text, animated product name and
synthesised SFX (no music, original audio removed, original colours).

```
pip install numpy pillow
python3 avco_edit.py --src "/path/to/AVCO 1" --out preview.mp4 --preview   # 540x960
python3 avco_edit.py --src "/path/to/AVCO 1" --out final.mp4               # 1080x1920
```

- `avco_edit.py` – scene list (EDL), text/animation and render
- `sfx.py` – pop, bubble, tick, sparkle, ding, whoosh, pen, shimmer, kaching (numpy synth)
- `fonts/` – Fredoka SemiBold, Pacifico (SIL Open Font License, Google Fonts)
- Emoji: system Noto Color Emoji (`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`)

Body text is copied from the reference video; only the hook and CTA are new.

## Nursing Cover (AFFILIATE 1)

```
python3 nursing_edit.py --src "/path/to/AFFILIATE 1" --out preview.mp4 --preview   # 540x960
python3 nursing_edit.py --src "/path/to/AFFILIATE 1" --out final.mp4               # 1080x1920
```

Same pipeline as `avco_edit.py`. No speech in the raw clips, so the text comes
from the visuals, the client's product points and the reference wording.
Product name in Pacifico on a plum-pink marker (colour of the cover).
