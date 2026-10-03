#!/usr/bin/env python
"""Render a replay (with per-frame option probabilities) from flappy.py --record-only into an mp4.

    python flappy_video.py --json results/flappy_4b_probs.json --policy mlp --out results/flappy_mlp.mp4
Game runs at 15 fps; the video plays it at 30 fps (x2), one video frame per game frame.
"""
import argparse
import json

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

GAP, PIPE_HW, BIRD_X = 0.28, 0.04, 0.2
W, H = 1280, 720
GW, GH, GX, GY = 400, 600, 40, 80
PX, PY, PW, PH = 500, 120, 720, 300
BG, PANEL, INK, MUTE = (11, 21, 25), (18, 34, 41), (228, 239, 236), (138, 166, 171)
SKY, PIPE, PIPE_D, BIRD, WARN, OK, LINE = (15, 39, 48), (63, 191, 127), (42, 143, 94), (242, 177, 52), (229, 83, 61), (63, 191, 127), (36, 64, 74)
NAMES = {"mlp": "latent + MLP (soft BCE)", "nli": "zero-shot NLI entailment", "oracle": "oracle"}
LABELS = {"mlp": ("P(flap)", "P(do nothing)"), "nli": ("P(entail | flap)", "P(entail | do nothing)"), "oracle": ("flap", "")}


def font(size, bold=False):
    import matplotlib
    d = matplotlib.get_data_path() + "/fonts/ttf/"
    try:
        return ImageFont.truetype(d + ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"), size)
    except OSError:
        return ImageFont.load_default()


F_S, F_M, F_L, F_XL = font(16), font(20), font(26, True), font(40, True)


def draw_frame(rep, i, policy, window=150):
    f = rep[i]
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # header
    d.text((40, 24), f"Flappy Qwen  ·  Qwen3.5-4B NLI cross-encoder  ·  {NAMES[policy]}", fill=INK, font=F_L)
    d.text((40, 56), "game 15 fps, shown at x2  ·  one 4B forward pass per option per frame", fill=MUTE, font=F_S)
    # game panel
    d.rectangle([GX, GY, GX + GW, GY + GH], fill=SKY)
    for px, lo in f["pipes"]:
        x = GX + px * GW
        hw = PIPE_HW * GW
        top = GY + (1 - (lo + GAP)) * GH
        bot = GY + (1 - lo) * GH
        d.rectangle([x - hw, GY, x + hw, top], fill=PIPE)
        d.rectangle([x - hw, bot, x + hw, GY + GH], fill=PIPE)
        d.rectangle([x - hw - 4, top - 14, x + hw + 4, top], fill=PIPE_D)
        d.rectangle([x - hw - 4, bot, x + hw + 4, bot + 14], fill=PIPE_D)
    d.rectangle([GX, GY + GH - 8, GX + GW, GY + GH], fill=LINE)
    bx, by, r = GX + BIRD_X * GW, GY + (1 - f["y"]) * GH, 13
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=BIRD)
    d.polygon([(bx + r, by), (bx + r + 10, by - 4), (bx + r + 10, by + 4)], fill=BIRD)
    d.ellipse([bx + 3, by - 6, bx + 8, by - 1], fill=(17, 32, 26))
    if f["a"]:
        d.line([(bx - 5, by + 3), (bx - 18, by - 12)], fill=INK, width=3)
        d.text((bx - 30, by + 18), "FLAP", fill=BIRD, font=F_S)
    if f["skipped"]:
        d.text((GX + GW - 150, GY + 12), "MODEL BUSY", fill=WARN, font=F_M)
    d.text((GX, GY + GH + 14), f"frame {f['t']:4d}   score {f['score']:3d}   " + (f"decision {f['lat_ms']:.0f} ms" if f["lat_ms"] else ""), fill=MUTE, font=F_S)
    if i >= len(rep) - 1:
        d.rectangle([GX, GY + GH / 2 - 40, GX + GW, GY + GH / 2 + 40], fill=(0, 0, 0))
        d.text((GX + 60, GY + GH / 2 - 22), f"GAME OVER  {f['score']}", fill=BIRD, font=F_XL)
    # probability panel
    d.rectangle([PX, PY, PX + PW, PY + PH], fill=PANEL)
    l1, l2 = LABELS[policy]
    d.text((PX, PY - 30), f"option scores over the last {window} frames", fill=MUTE, font=F_S)
    for yy, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]:
        y = PY + PH - yy * PH
        d.line([(PX, y), (PX + PW, y)], fill=LINE, width=1)
        d.text((PX - 30, y - 8), lab, fill=MUTE, font=F_S)
    start = max(0, i - window + 1)
    xs = lambda k: PX + (k - start) / window * PW
    for k in range(start, i + 1):
        g = rep[k]
        if g["skipped"]:
            d.rectangle([xs(k), PY, xs(k) + PW / window, PY + PH], fill=(60, 30, 30))
        elif g["a"]:
            d.line([(xs(k), PY + PH - 6), (xs(k), PY + PH)], fill=BIRD, width=2)
    for idx, col in [(0, BIRD), (1, OK)]:
        pts = [(xs(k), PY + PH - rep[k]["probs"][idx] * PH) for k in range(start, i + 1) if rep[k].get("probs")]
        if len(pts) > 1:
            d.line(pts, fill=col, width=3)
    if f.get("probs"):
        p0, p1 = f["probs"]
        d.text((PX, PY + PH + 16), f"{l1} = {p0:.3f}", fill=BIRD, font=F_M)
        d.text((PX + 300, PY + PH + 16), f"{l2} = {p1:.3f}", fill=OK, font=F_M)
        d.text((PX, PY + PH + 46), "chosen: " + ("FLAP" if f["a"] else "do nothing") + "  (argmax over the two options)", fill=INK, font=F_M)
    # what the model reads
    y0 = PY + PH + 90
    prev = rep[max(0, i - 1)]
    vy = f["y"] - prev["y"]
    nxt = next((p for p in f["pipes"] if p[0] + PIPE_HW >= BIRD_X - 0.03), f["pipes"][0])
    lo, hi = nxt[1], nxt[1] + GAP
    c = (lo + hi) / 2
    pos = "inside the gap" if lo < f["y"] < hi else ("above the gap" if f["y"] >= hi else "below the gap")
    txt = (f"Premise: bird at height {f['y']:.2f}, {'rising' if vy > 0 else 'falling'} ({vy:+.3f}/frame); next pipe {nxt[0]-BIRD_X:.2f} ahead, "
           f"gap {lo:.2f}-{hi:.2f} (centre {c:.2f}); bird is {pos}, {f['y']-c:+.2f} vs centre.")
    for j, line in enumerate(wrap(txt, 78)):
        d.text((PX, y0 + j * 22), line, fill=MUTE, font=F_S)
    d.text((PX, y0 + 70), "Hypothesis: The correct action is: flap  |  do nothing", fill=INK, font=F_S)
    return np.asarray(img)


def wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + [cur]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--policy", default="mlp")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--max-frames", type=int, default=900)
    args = ap.parse_args()
    rep = json.load(open(args.json))["results"][args.policy]["replay"][: args.max_frames]
    w = imageio.get_writer(args.out, fps=args.fps, codec="libx264", quality=8, macro_block_size=None)
    for i in range(len(rep)):
        w.append_data(draw_frame(rep, i, args.policy))
    for _ in range(args.fps):  # hold the last frame 1 s
        w.append_data(draw_frame(rep, len(rep) - 1, args.policy))
    w.close()
    print("wrote", args.out, len(rep), "frames")


if __name__ == "__main__":
    main()
