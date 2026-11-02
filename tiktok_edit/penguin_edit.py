#!/usr/bin/env python3
"""TikTok edit for the inflatable Penguin Punching Toy.

Renders straight from the original iPhone clips (1080x1920 HEVC, HLG HDR):
  python3 penguin_edit.py --src "<folder with raw clips>" --out preview.mp4 --preview
  python3 penguin_edit.py --src "<folder with raw clips>" --out final.mp4

- 1080x1920 @ 30 fps (preview: 540x960), original audio removed, no music
- HLG HDR is converted to SDR BT.709 (mobius tone map, no grade) so colours
  look like the original clip on a phone
- text in the reference style; text engine and SFX are shared with avco_edit.py

There is no speech about the product in the clips and no box or label, so the
text only describes what the footage shows.
"""
import argparse
import os
import subprocess
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import avco_edit as base  # noqa: E402
import sfx  # noqa: E402
from avco_edit import FPS, Overlay, TextKit, ease_out  # noqa: E402

# brand colour: the penguin's magenta, translucent like a highlighter
base.MARKER_BLUE = (236, 64, 150, 165)
# text a little smaller and higher than the AVCO edit
base.TEXT_SIZE = 50   # Fredoka px at 1080 wide
base.TEXT_TOP = 0.15  # block starts 15% from top
NAME_TOP = 0.10       # product name block

CLIPS = {k: f"IMG_{k}.MOV" for k in
         ("1516", "1517", "1519", "1522", "1524", "1525", "1527", "1528", "1529", "1530")}

# ---------------------------------------------------------------------------
# Edit decision list. t_in/t_out are seconds in the source clip, text times
# are seconds from the start of the scene. Every scene is < 5 s.
# IMG_1515 (taking the toy out of the plastic) is left out on purpose.
# ---------------------------------------------------------------------------
SCENES = [
    dict(  # HOOK 1/2 - baby smacks the penguin, it swings away
        src="1530", t_in=0.4, t_out=2.2, speed=1.2,
        lines=[
            ("Anak cepat bosan", 0.0, "text"),
            ("dengan mainan? 😩", 0.0, "text"),
        ],
    ),
    dict(  # HOOK 2/2 - big smile, penguin pushed over
        src="1528", t_in=8.1, t_out=9.9, speed=1.2,
        lines=[
            ("Penguin punching ni", 0.0, "text"),
            ("WAJIB ada! 🛒✨", 0.0, "text"),
        ],
    ),
    dict(  # product name over the penguin's front
        src="1529", t_in=4.2, t_out=8.6, speed=1.2, flash=True, text_top=NAME_TOP,
        lines=[
            ("Penguin", 0.1, "name"),
            ("Punching Toys", 0.55, "name"),
        ],
    ),
    dict(  # finger push, penguin rocks back up
        src="1529", t_in=9.5, t_out=15.5, speed=1.5,
        lines=[
            ("Tolak je,", 0.1, "text"),
            ("dia bangun balik! 😆", 0.1, "text"),
        ],
    ),
    dict(  # turned around in the hand
        src="1525", t_in=0.0, t_out=8.0, speed=2.0,
        lines=[
            ("Kenapa best? 🤩", 0.05, "text"),
            ("✅ Ringan, baby senang tolak", 0.7, "check"),
            ("✅ Warna terang & comel", 1.4, "check"),
            ("✅ Tumbang, terus bangun balik", 2.1, "check"),
        ],
    ),
    dict(
        src="1517", t_in=2.0, t_out=7.5, speed=1.3,
        lines=[
            ("Baby yang dah boleh duduk", 0.1, "text"),
            ("pun boleh main 🥰", 0.1, "text"),
        ],
    ),
    dict(
        src="1527", t_in=4.0, t_out=10.0, speed=1.5,
        lines=[
            ("Tumbuk, tolak, peluk 🥊", 0.1, "text"),
            ("main sendiri pun seronok!", 0.9, "text"),
        ],
    ),
    dict(  # crawls after the penguin
        src="1524", t_in=44.0, t_out=52.0, speed=2.0,
        lines=[
            ("Sampai merangkak", 0.1, "text"),
            ("kejar penguin 😂", 0.1, "text"),
        ],
    ),
    dict(
        src="1528", t_in=0.0, t_out=4.5, speed=1.2,
        lines=[
            ("Tengok tu, happy je dia", 0.1, "text"),
            ("ada kawan baru 🐧💕", 0.1, "text"),
        ],
        sfx=[(0.15, "ding", 0.4)],
    ),
    dict(  # hand pump
        src="1516", t_in=0.0, t_out=9.0, speed=2.5,
        lines=[
            ("Pam guna pam tangan,", 0.1, "text"),
            ("senang je 💨", 0.1, "text"),
        ],
    ),
    dict(  # CTA 1/2
        src="1519", t_in=15.0, t_out=20.0, speed=1.2,
        lines=[
            ("Jangan tunggu anak", 0.08, "text"),
            ("makin bosan 😭", 0.08, "text"),
        ],
        sfx=[(0.0, "whoosh", 0.5)],
    ),
    dict(  # CTA 2/2, text only
        src="1522", t_in=12.0, t_out=16.8, speed=1.1,
        lines=[
            ("Tekan beg kuning &", 0.08, "cta"),
            ("checkout sekarang! 🛒💛", 0.08, "cta"),
        ],
    ),
]

# HLG (BT.2020) -> SDR BT.709. 203 nits = HLG reference white, so mid-tones and
# skin keep their brightness; mobius only rolls off the highlights.
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv")


def scene_frames(path, sc, BW, BH):
    """Yield RGB frames (BW x BH) for a scene, decoded from the original clip."""
    n = round((sc["t_out"] - sc["t_in"]) / sc["speed"] * FPS)
    vf = (f"setpts=(PTS-STARTPTS)/{sc['speed']},fps={FPS},{TONEMAP},"
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
    proc.kill()
    proc.stdout.close()
    proc.wait()


def build_sfx_events(meta):
    ev, alt = [], 0
    for start, sc, ov in meta:
        if sc.get("flash"):
            ev.append((start, "whoosh", 0.55, 0.0))
        for t, name, g in sc.get("sfx", []):
            ev.append((start + t, name, g, 0.0))
        seen = set()
        for it in ov.items:
            t = start + it["t0"]
            if it["kind"] == "name":
                ev.append((t + 0.15, "pen", 0.55, 0.1))
                if it["last"]:  # magic shimmer + sparkle once the name is written
                    ev += [(t + 0.8, "shimmer", 0.55, 0.0), (t + 0.95, "sparkle", 0.4, 0.25)]
                continue
            key = round(t, 2)
            if key in seen:  # two-row sentence: one sound
                continue
            seen.add(key)
            if it["kind"] == "check":
                ev.append((t + 0.02, "tick", 0.55, 0.0))
            elif it["kind"] == "cta":
                ev.append((t + 0.02, "kaching", 0.75, 0.0))
            else:
                ev.append((t, "pop" if alt % 2 == 0 else "bubble", 0.6, 0.0))
                alt += 1
        hit = next((l for l in sc["lines"] if "✨" in l[0]), None)
        if hit:
            ev.append((start + hit[1] + 0.12, "sparkle", 0.45, 0.25))
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder with the original clips")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", action="store_true", help="540x960 quick render")
    args = ap.parse_args()

    W, H = (540, 960) if args.preview else (1080, 1920)
    scale = W / 1080
    BW, BH = round(W * base.BASE_MARGIN / 2) * 2, round(H * base.BASE_MARGIN / 2) * 2
    probe = TextKit(scale, round(base.TEXT_SIZE * scale), round(base.NAME_SIZE * scale))
    texts = [l[0] for sc in SCENES for l in sc["lines"] if l[2] != "name"]
    names = [l[0] for sc in SCENES for l in sc["lines"] if l[2] == "name"]
    tw = max(probe.line(t).width for t in texts)
    nw = max(probe.name(t)[0].width for t in names)
    tsize = int(probe.size * min(1, base.MAX_TEXT_W * W / tw))
    nsize = int(probe.name_size * min(1.05, 0.9 * W / nw))
    print(f"text size {tsize}px, name size {nsize}px", flush=True)
    kit = TextKit(scale, tsize, nsize)

    meta, start = [], 0.0
    for sc in SCENES:
        dur = (sc["t_out"] - sc["t_in"]) / sc["speed"]
        assert dur < 5, f"scene too long: {dur:.2f}s"
        meta.append((start, sc, Overlay(kit, sc, W, H)))
        start += round(dur * FPS) / FPS
    total = start
    assert total < 60
    print(f"{len(SCENES)} scenes, total {total:.2f}s", flush=True)

    tmp = tempfile.mkdtemp(prefix="penguin_")
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
        for fi, frame0 in enumerate(scene_frames(path, sc, BW, BH)):
            t = fi / FPS
            # slow push-in + small punch-in at the cut; z == 1 is the full source frame
            z = 1 + base.PUSH * (t / dur) + base.PUNCH * (1 - ease_out(min(t / base.PUNCH_DUR, 1)))
            cw, ch = BW / z, BH / z
            box = ((BW - cw) / 2, (BH - ch) / 2, (BW + cw) / 2, (BH + ch) / 2)
            frame = frame0.resize((W, H), Image.BICUBIC, box=box).convert("RGBA")
            ov.draw(frame, t)
            if sc.get("flash") and t < 0.25:  # white flash right after the hook
                a = int(220 * (1 - t / 0.25) ** 1.5)
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
            out.stdin.write(frame.convert("RGB").tobytes())
        print(f"scene {i + 1}/{len(meta)} done", flush=True)
    out.stdin.close()
    out.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
