#!/usr/bin/env python
"""Radar: Jev, Terra (read off their chart), openjev 4B zero-shot, openjev 35B-A3B zero-shot, openjev 35B-A3B frozen latent + MLP."""
import argparse, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SPOKES = [("MMLU", "mmlu"), ("GPQA\nDiamond", "gpqa"), ("ARC-Easy", "arc_easy"), ("ARC-Challenge", "arc_challenge"), ("WinoGrande", "winogrande"),
          ("HellaSwag", "hellaswag"), ("GSM8K\n4 choices", "gsm8k_mc4"), ("GSM8K\n10 choices", "gsm8k_mc10"), ("Chess\n4 legal moves", "chess")]
JEV = [86, 50, 97, 92, 68, 86, 78, 67, 38]
TERRA = [84, 42, 97, 92, 52, 88, 86, 83, 45]


def load(paths):
    r = {}
    for p in paths:
        d = json.load(open(p)); d = d.get("results", d)
        for m, v in d.items():
            r.setdefault(m, {}).update(v)
    return r


ap = argparse.ArgumentParser(); ap.add_argument("--out", default="assets/radar_openjev_35b.png"); args = ap.parse_args()
ev4 = load(["results/qwen4b_all.json", "results/qwen4b_extra_mc.json"])["ckpt/qwen3.5-4b-nli"]
ev35 = load(["results/qwen35b_all.json"])["/mnt/qwen_nli_ckpt/qwen3.5-35b-a3b-nli"]
mlp35 = load(["results/latent_mlp_35b.json"])
z4 = [100 * ev4[k]["rerank_acc"] for _, k in SPOKES]; z35 = [100 * ev35[k]["rerank_acc"] for _, k in SPOKES]; p35 = [100 * mlp35[k]["mlp_per_task"] for _, k in SPOKES]
n = len(SPOKES); ang = np.linspace(0, 2 * np.pi, n, endpoint=False); close = lambda v: np.r_[v, v[:1]]
fig = plt.figure(figsize=(9.2, 10.6), facecolor="white"); ax = fig.add_subplot(111, polar=True); fig.subplots_adjust(top=0.85, bottom=0.18)
ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1); ax.set_facecolor("#f4f5f7")
ax.set_ylim(0, 100); ax.set_yticks([20, 40, 60, 80, 100]); ax.set_yticklabels([f"{t}%" for t in [20, 40, 60, 80, 100]], color="#9aa0a6", fontsize=8)
ax.set_xticks(ang); ax.set_xticklabels([s for s, _ in SPOKES], fontsize=10.5, color="#222"); ax.grid(color="#d0d4d9", linewidth=0.8); ax.spines["polar"].set_color("#c8ccd1")
for name, v, col, ls, lw in [("Jev", JEV, "#c4753a", "-", 2), ("Terra · letter only", TERRA, "#4c7fa8", "-", 2),
                             ("openjev 4B · zero-shot", z4, "#a0a0a0", "--", 1.6), ("openjev 35B-A3B · zero-shot", z35, "#444444", "-", 2),
                             ("openjev 35B-A3B · frozen latent + MLP", p35, "#2e8b57", "-", 2.4)]:
    v = np.array(v, float); ax.plot(close(ang), close(v), color=col, linewidth=lw, linestyle=ls, marker="o", markersize=4, label=name); ax.fill(close(ang), close(v), color=col, alpha=0.05)
fig.suptitle("openjev 35B vs. Jev vs. Terra", fontsize=17, fontweight="bold", y=0.955)
fig.text(0.5, 0.915, "multiple-choice accuracy, common 0-100% scale · Jev/Terra read off their published chart", ha="center", fontsize=9.5, color="#666")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, frameon=False, fontsize=9.5)
fig.text(0.5, 0.03, "openjev: Qwen3.5 fine-tuned as an NLI cross-encoder. Zero-shot = argmax P(entailment) over the options, no task-specific training.\n"
         "latent + MLP = backbone frozen, 2048→512→1 head on the last-token latent, a few thousand labelled questions per task (not zero-shot).\n"
         "Chess is our synthetic 4-move legality set; GSM8K k-choice uses gold + numeric distractors. Polygon area is not an aggregate score.", ha="center", fontsize=8, color="#777")
fig.savefig(args.out, dpi=170); print("wrote", args.out)
for (s, _), a, b, c in zip(SPOKES, z4, z35, p35):
    print(f"{s.replace(chr(10), ' '):22s} 4B zs {a:5.1f}  35B zs {b:5.1f}  35B mlp {c:5.1f}")
