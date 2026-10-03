#!/usr/bin/env python
"""Video of a minecraft.py episode: frames recorded by mc_record.js (named <unix_ms>.jpg) + the model's predicate checks per step.

    python mc_video.py --json results/minecraft_mc_chain_ep.json --frames /mnt/mc/frames_ep --out results/minecraft_chain.mp4
"""
import argparse
import json
import os

import imageio
import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from minecraft import MILESTONES, nm, skill_text

W, H = 1600, 900
BG, PANEL, INK, MUTE, LINE = (11, 21, 25), (18, 34, 41), (228, 239, 236), (138, 166, 171), (36, 64, 74)
GOLD, GREEN, RED = (242, 177, 52), (63, 191, 127), (229, 83, 61)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--planner", default="chain")
    ap.add_argument("--episode", type=int, default=0)
    ap.add_argument("--out", default="results/minecraft_chain.mp4")
    ap.add_argument("--speed", type=float, default=2.0, help="playback speed-up over real time")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()
    data = json.load(open(args.json))
    ep = data["episodes"][args.planner][args.episode]
    steps = ep["steps"]
    fd = matplotlib.get_data_path() + "/fonts/ttf/"
    F = lambda sz, b=False: ImageFont.truetype(fd + ("DejaVuSansMono-Bold.ttf" if b else "DejaVuSansMono.ttf"), sz)
    f_s, f_m, f_l = F(15), F(18), F(26, True)
    t0, t1 = steps[0]["ts"], steps[-1]["ts_end"] + 3
    files = sorted(f for f in os.listdir(args.frames) if f.endswith(".jpg"))
    times = np.array([int(f[:-4]) / 1000 for f in files])
    keep = (times >= t0 - 1) & (times <= t1)
    files, times = [f for f, k in zip(files, keep) if k], times[keep]
    # resample to constant output rate: output frame j shows real time t0 + j * speed / fps
    out_t = np.arange(times[0], times[-1], args.speed / args.fps)
    idx = np.clip(np.searchsorted(times, out_t), 0, len(files) - 1)
    w = imageio.get_writer(args.out, fps=args.fps, codec="libx264", quality=7, macro_block_size=None)
    cache = (None, None)
    for t, fi in zip(out_t, idx):
        k = max(0, int(np.searchsorted([s["ts"] for s in steps], t, side="right")) - 1)
        st = steps[k]
        phase = "thinking" if t < st["ts_act"] else ("acting" if t < st["ts_end"] else "done")
        inv = st["state"]["inventory"] if t < st["ts_end"] else st["state_after"]["inventory"]
        if cache[0] != fi:
            cache = (fi, Image.open(os.path.join(args.frames, files[fi])).convert("RGB").resize((960, 540)))
        img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
        d.text((30, 16), "Minecraft · craft an iron pickaxe · Qwen3.5-4B NLI cross-encoder · zero-shot", fill=INK, font=f_l)
        d.text((30, 52), f"the model only answers entailment questions about the state; the scaffold walks the tech tree · shown at x{args.speed:g}", fill=MUTE, font=f_s)
        img.paste(cache[1], (30, 84))
        # milestones
        have_now = {m for m in MILESTONES if inv.get(m, 0) > 0}
        reached = set()
        for s in steps[:k + 1]:
            reached |= {m for m in MILESTONES if s["state"]["inventory"].get(m, 0) > 0} | {m for m, v in s["state"]["near"].items() if v}
        reached |= have_now
        x, y = 30, 650
        d.text((x, y), "milestones", fill=MUTE, font=f_s)
        for j, m in enumerate(MILESTONES):
            cx, cy = x + (j % 6) * 162, y + 28 + (j // 6) * 30
            d.rectangle([cx, cy + 3, cx + 12, cy + 15], fill=GREEN if m in reached else PANEL, outline=LINE)
            d.text((cx + 20, cy), nm(m, 2 if m == 'planks' else 1).replace(' block', '').replace(' chunk', ''), fill=INK if m in reached else MUTE, font=f_s)
        d.text((x, y + 100), "inventory: " + (", ".join(f"{n} {nm(i, n)}" for i, n in inv.items() if i in MILESTONES) or "empty"), fill=INK, font=f_s)
        mins = (t - t0) / 60
        d.text((x, y + 130), f"step {k + 1}/{len(steps)}   game time {int(mins):02d}:{int(mins * 60) % 60:02d}   predicates judged this step: {sum('hyp' in j for j in st['trace'])}", fill=MUTE, font=f_s)
        # reasoning panel
        PX, PY = 1030, 84
        d.rectangle([PX - 10, PY, W - 20, H - 30], fill=PANEL)
        d.text((PX, PY + 10), "backward chaining (model = judge)", fill=GOLD, font=f_m)
        d.text((W - 190, PY + 13), "P(yes)/P(no)", fill=MUTE, font=f_s)
        yy, depth = PY + 44, 0
        for j in st["trace"]:
            if yy > H - 170:
                break
            if "node" in j:
                d.text((PX + 12 * depth, yy), ("└ " if depth else "") + (f"need: {nm(j['node'])}" if j['node'] in MILESTONES else j['node'].replace('_', ' ')[:48]), fill=INK, font=f_m)
                depth += 1; yy += 26
            else:
                col = GREEN if j["judged"] else RED
                txt = j["hyp"].replace("The answer to whether a ", "Is a ").replace(" is placed nearby is yes.", " placed nearby? Yes.")
                txt = txt if len(txt) < 46 - depth else txt[:44 - depth] + "…"
                d.text((PX + 12 * depth, yy), ("✓ " if j["judged"] else "✗ ") + txt, fill=col, font=f_s)
                if "p_ent_neg" in j:
                    d.text((W - 130, yy), f"{j['p_ent']:.2f}/{j['p_ent_neg']:.2f}", fill=MUTE, font=f_s)
                if j.get("truth") is not None and j["truth"] != j["judged"]:
                    d.text((W - 40, yy), "!", fill=GOLD, font=f_m)
                yy += 21
        d.line([(PX, H - 150), (W - 40, H - 150)], fill=LINE)
        d.text((PX, H - 138), "action", fill=MUTE, font=f_s)
        d.text((PX, H - 114), skill_text(tuple(st["skill"]))[:44].upper(), fill=GOLD, font=f_m)
        res = "deciding…" if phase == "thinking" else ("executing…" if phase == "acting" else ("ok: " if st["ok"] else "FAILED: ") + st["msg"])
        d.text((PX, H - 84), res[:52], fill=INK if phase != "done" else (GREEN if st["ok"] else RED), font=f_s)
        w.append_data(np.asarray(img))
    for _ in range(args.fps * 2):
        w.append_data(np.asarray(img))
    w.close()
    print("wrote", args.out, len(out_t), "frames,", f"{(times[-1] - times[0]) / 60:.1f} min of game time")


if __name__ == "__main__":
    main()
