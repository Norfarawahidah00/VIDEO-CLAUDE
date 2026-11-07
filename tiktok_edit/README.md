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
- `fonts/` – Fredoka SemiBold, Pacifico, Mali Medium (✅ points in the Ddrops edit) (SIL Open Font License, Google Fonts)
- Emoji: system Noto Color Emoji (`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`)

Body text is copied from the reference video; only the hook and CTA are new.

## Kids Ddrops Vitamin D3

`ddrops_edit.py` reuses the engine in `avco_edit.py` with its own clip and scene
list. Raw clips have no product speech, so all text comes from the packaging.

```
python3 ddrops_edit.py --src "/path/to/VIT D DROPS" --out preview.mp4 --preview
python3 ddrops_edit.py --src "/path/to/VIT D DROPS" --out final.mp4
```
