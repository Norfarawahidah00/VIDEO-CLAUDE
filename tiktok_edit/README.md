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

## Penguin Punching Toys

```
python3 penguin_edit.py --src "/path/to/penguin clips" --out preview.mp4 --preview   # 540x960
python3 penguin_edit.py --src "/path/to/penguin clips" --out final.mp4               # 1080x1920
```

- `penguin_edit.py` – scene list and render; reuses the text engine from `avco_edit.py` and `sfx.py`
- Source clips are iPhone HLG HDR; they are tone-mapped to SDR BT.709 (no colour grade)
- No product speech or packaging in the footage, so text only describes what is shown
