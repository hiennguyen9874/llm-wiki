#!/usr/bin/env python
"""Radar: openjev NLI-4B zero-shot rerank vs Jev and Terra on the same spokes (all zero-shot).
Jev / Terra values are read off the reference chart (letter-only Terra), so they are approximate.
    python radar.py --out assets/radar_openjev.png
"""
import argparse, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SPOKES = [("MMLU", "mmlu"), ("GPQA\nDiamond", "gpqa"), ("ARC-Easy", "arc_easy"), ("ARC-Challenge", "arc_challenge"),
          ("WinoGrande", "winogrande"), ("HellaSwag", "hellaswag"), ("GSM8K\n4 choices", "gsm8k_mc4"),
          ("GSM8K\n10 choices", "gsm8k_mc10"), ("Chess\n4 legal moves", "chess")]
# approximate, read off the "Jev vs. Terra" chart
JEV = [86, 50, 97, 92, 68, 86, 78, 67, 38]
TERRA = [84, 42, 97, 92, 52, 88, 86, 83, 45]


def load(paths):
    r = {}
    for p in paths:
        try:
            d = json.load(open(p))
        except FileNotFoundError:
            continue
        d = d.get("results", d)
        for m, v in d.items():
            r.setdefault(m, {}).update(v)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/radar_openjev.png")
    args = ap.parse_args()
    ev = load(["results/qwen4b_all.json", "results/qwen4b_extra_mc.json"])["ckpt/qwen3.5-4b-nli"]
    zero = [100 * ev[k]["rerank_acc"] if k in ev else np.nan for _, k in SPOKES]

    n = len(SPOKES)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    close = lambda v: np.r_[v, v[:1]]
    fig = plt.figure(figsize=(9.2, 10.4), facecolor="white")
    ax = fig.add_subplot(111, polar=True)
    fig.subplots_adjust(top=0.86, bottom=0.17)
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    ax.set_facecolor("#f4f5f7")
    ax.set_ylim(0, 100); ax.set_yticks([20, 40, 60, 80, 100]); ax.set_yticklabels([f"{t}%" for t in [20, 40, 60, 80, 100]], color="#9aa0a6", fontsize=8)
    ax.set_xticks(ang); ax.set_xticklabels([s for s, _ in SPOKES], fontsize=10.5, color="#222")
    ax.grid(color="#d0d4d9", linewidth=0.8); ax.spines["polar"].set_color("#c8ccd1")
    series = [("Jev", JEV, "#c4753a", "-"), ("Terra · letter only", TERRA, "#4c7fa8", "-"),
              ("openjev · NLI-4B zero-shot rerank", zero, "#4a4a4a", "-")]
    for name, v, col, ls in series:
        v = np.array(v, dtype=float)
        ax.plot(close(ang), close(v), color=col, linewidth=2, linestyle=ls, marker="o", markersize=4, label=name)
        ax.fill(close(ang), close(np.nan_to_num(v)), color=col, alpha=0.06)
    ax.set_title("openjev vs. Jev vs. Terra", fontsize=17, fontweight="bold", pad=42)
    fig.text(0.5, 0.905, "multiple-choice accuracy, common 0-100% scale · Jev/Terra read off their published chart",
             ha="center", fontsize=9.5, color="#666")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=3, frameon=False, fontsize=9.5)
    fig.text(0.5, 0.035, "openjev: Qwen3.5-4B fine-tuned as an NLI cross-encoder, zero-shot = argmax P(entailment) over the options, no task-specific training.\n"
             "Chess is our synthetic 4-move legality set; GSM8K k-choice uses gold + numeric distractors. Polygon area is not an aggregate score.",
             ha="center", fontsize=8, color="#777")
    fig.savefig(args.out, dpi=170)
    print("wrote", args.out)
    for (s, k), z in zip(SPOKES, zero):
        print(f"{s.replace(chr(10), ' '):22s} zero-shot {z:5.1f}")


if __name__ == "__main__":
    main()
