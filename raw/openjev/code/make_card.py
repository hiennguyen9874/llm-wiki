#!/usr/bin/env python
"""Build README_hf.md (model card for AlexWortega/openjev) from results/*.json. Architecture + loss + results only."""
import glob, json, collections

def load(paths):
    r = collections.defaultdict(dict)
    for p in paths:
        for f in glob.glob(p):
            d = json.load(open(f)); d = d.get("results", d)
            for m, v in d.items():
                if isinstance(v, dict): r[m].update(v)
    return r

NAMES = {"ckpt/qwen3.5-0.8b-nli": "openjev-0.8B", "ckpt/qwen3.5-2b-nli": "openjev-2B", "ckpt/qwen3.5-4b-nli": "openjev-4B",
         "ckpt/qwen3.5-2b-nli-headonly": "Qwen3.5-2B head-only", "dleemiller/ModernCE-large-nli": "ModernCE-large-nli (reference)"}
ORDER = list(NAMES)
MC = ["gpqa", "mmlu", "arc_easy", "arc_challenge", "winogrande", "chess", "hellaswag", "gsm8k_mc4", "gsm8k_mc10"]
LAB = {"gpqa": "GPQA-diamond", "mmlu": "MMLU", "arc_easy": "ARC-Easy", "arc_challenge": "ARC-Challenge", "winogrande": "WinoGrande",
       "chess": "Chess (4 moves, 1 legal)", "hellaswag": "HellaSwag", "gsm8k_mc4": "GSM8K 4-choice", "gsm8k_mc10": "GSM8K 10-choice"}
f3 = lambda x: f"{x:.3f}"

ev = load(["results/qwen0.8b_mnli_gpqa.json", "results/qwen0.8b_gsm8k.json", "results/qwen2b_full.json", "results/qwen4b_all.json",
           "results/qwen2b_headonly_all.json", "results/mc_all.json", "results/qwen4b_extra_mc.json"])
mlp = {}
for m, f in [("ckpt/qwen3.5-0.8b-nli", "results/latent_mlp_0.8b.json"), ("ckpt/qwen3.5-2b-nli", "results/latent_mlp_2b.json"),
             ("ckpt/qwen3.5-4b-nli", "results/latent_mlp_4b_eps0.1.json"), ("raw2b", "results/latent_mlp_2b_base.json"), ("raw4b", "results/latent_mlp_4b_base.json")]:
    mlp[m] = json.load(open(f))["results"]
try:
    mlp["ckpt/qwen3.5-4b-nli"].update(json.load(open("results/latent_mlp_4b_extra.json"))["results"])
except FileNotFoundError:
    pass
fs = load(["results/fewshot.json", "results/fewshot_headonly.json", "results/fewshot_4b.json"])
doom = json.load(open("results/doom_4b.json"))["results"]

out = []
w = out.append
w('''---
license: mit
base_model: Qwen/Qwen3.5-4B
pipeline_tag: text-classification
library_name: transformers
tags:
- nli
- cross-encoder
- qwen3.5
- reranker
- text-classification
language:
- en
---

# openjev — Qwen3.5 trained as jev model

Zero-shot Doom, played by the cross-encoder from the text state (hypotheses "the nearest enemy is left of / right of /
exactly on the crosshair" → turn left / turn right / attack; 11 kills on average, oracle 18.8, ~57 ms per decision):

<video controls src="https://huggingface.co/AlexWortega/openjev/resolve/main/videos/doom_zs_position.mp4" width="720"></video>

From pixels (the frame goes in as image tokens through the Qwen3.5 vision tower, hypotheses about the monster's
x-position; 5.2 kills, still zero-shot):

<video controls src="https://huggingface.co/AlexWortega/openjev/resolve/main/videos/doom_vision_zeroshot_pixels.mp4" width="720"></video>

Zero-shot multiple-choice accuracy against Jev and Terra (their numbers read off their published chart; Chess and
GSM8K-k-choice are our constructions):

![radar](assets/radar_openjev.png)

A Qwen3.5 decoder turned into a 3-way NLI cross-encoder in the spirit of
[dleemiller's "NLI cross encoders: ways to use them"](https://huggingface.co/blog/dleemiller/nli-xenc-ways-to-use).
**Every number in the main tables is zero-shot**: the cross-encoder is applied as-is (argmax entailment over the
options, or entailment vs a reference answer) with no task-specific training. `dleemiller/ModernCE-large-nli`
(ModernBERT-large, 395M) is the reference throughout.

Checkpoint in this repo: `qwen3.5-4b-nli/` (Qwen3.5-4B backbone, 3 labels). Code: `modeling_openjev.py`, `code/`.

## Architecture

**Cross-encoder.** `Qwen3_5ForSequenceClassification`: the Qwen3.5 text backbone (Gated DeltaNet + gated attention,
decoder-only) followed by a linear `score` head over the hidden state of the *last non-pad token*. The pair is fed as a
single string (template stored in `config.nli_template`):

```
Premise: {premise}
Hypothesis: {hypothesis}
```

Three labels in dleemiller's order: `0 = contradiction, 1 = entailment, 2 = neutral`. Right padding; `pad_token_id`
lives on `config.get_text_config()`. The vision tower that ships with Qwen3.5 checkpoints is kept in the weights but is
not used for text. Loss for the NLI head: cross-entropy over the 3 classes (full fine-tune of the text backbone for
0.8B/2B/4B).

`modeling_openjev.py` also ships `LatentMLPHead` (a probe on the frozen latent, soft-BCE loss) — it is *not* zero-shot
and its numbers are confined to the appendix at the end.

## Usage

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

repo, sub = "AlexWortega/openjev", "qwen3.5-4b-nli"
tok = AutoTokenizer.from_pretrained(repo, subfolder=sub)
model = AutoModelForSequenceClassification.from_pretrained(repo, subfolder=sub, dtype=torch.bfloat16).cuda().eval()
tok.padding_side = "right"
model.config.get_text_config().pad_token_id = tok.pad_token_id

pairs = [("A man is playing a guitar on stage.", "Someone is making music."),
         ("A man is playing a guitar on stage.", "The room is silent.")]
texts = [model.config.nli_template.format(premise=p, hypothesis=h) for p, h in pairs]
enc = tok(texts, padding=True, return_tensors="pt").to("cuda")
probs = model(**enc).logits.float().softmax(-1)          # [contradiction, entailment, neutral]
```

`sentence_transformers.CrossEncoder` also loads it (`CrossEncoder(repo, subfolder=sub)` on recent versions) but note the
tokenizer has no pair separator: build the `Premise/Hypothesis` string yourself as above.

With the helper module:

```python
from modeling_openjev import OpenJevCrossEncoder, LatentMLPHead
ce = OpenJevCrossEncoder("AlexWortega/openjev", subfolder="qwen3.5-4b-nli")
ce.predict(pairs)                                   # probs
ce.rerank("Which gas do plants absorb?", ["CO2", "O2", "N2", "He"])   # zero-shot option index
ce.grade("What is 2+2?", reference="4", candidate="4")                   # entailment / contradiction / neutral
```

## Results (zero-shot)

Protocols follow the blog: **rerank without reference** (#3): premise = question, hypothesis = `The correct answer is: {option}`
(WinoGrande: the sentence with the blank filled; HellaSwag: the ending), pick argmax P(entailment).
**Grading with reference** (#6): premise = question + `Reference answer: {gold}`, hypothesis = `Answer: {option}`;
predict entailment iff the option is the gold one. Chess is our synthetic set (random position, 4 SAN moves, one legal);
GSM8K k-choice = gold final answer + numeric distractors; GSM8K best-of-4 uses candidates sampled from Qwen3.5-4B.

### NLI sanity

| model | MNLI-m | MNLI-mm |
|---|---|---|''')
for m in ORDER:
    mn = ev[m].get("mnli")
    if mn: w(f"| {NAMES[m]} | {f3(mn['validation_matched']['acc'])} | {f3(mn['validation_mismatched']['acc'])} |")

w("\n### Multiple choice, rerank without reference (zero-shot entailment)\n")
w("| model | " + " | ".join(LAB[t] for t in MC) + " |\n|---|" + "---|" * len(MC))
rb = {t: next((ev[m][t]["random_baseline"] for m in ORDER if t in ev[m] and "random_baseline" in ev[m][t]), 0.25) for t in MC}
w("| random | " + " | ".join(f3(rb[t]) for t in MC) + " |")
for m in ORDER:
    w(f"| {NAMES[m]} | " + " | ".join(f3(ev[m][t]["rerank_acc"]) if t in ev[m] else "-" for t in MC) + " |")

w("\n### Multiple choice, grading with reference (accuracy / F1)\n")
w("| model | " + " | ".join(LAB[t] for t in MC) + " |\n|---|" + "---|" * len(MC))
for m in ORDER:
    w(f"| {NAMES[m]} | " + " | ".join(f"{f3(ev[m][t]['grade_acc'])} / {f3(ev[m][t]['grade_f1'])}" if t in ev[m] else "-" for t in MC) + " |")

w("\n### GSM8K, 200 test questions, candidates from Qwen3.5-4B (greedy + 4 samples)\n")
w("| model | greedy | pass@1 | maj@4 | NLI rerank@4 | oracle@4 | grading acc / F1 |\n|---|---|---|---|---|---|---|")
for m in ORDER:
    g = ev[m].get("gsm8k")
    if g: w(f"| {NAMES[m]} | {f3(g['greedy_acc'])} | {f3(g['sample_pass1'])} | {f3(g['maj@4'])} | {f3(g['nli_rerank@4'])} | {f3(g['oracle@4'])} | {f3(g['grade_acc'])} / {f3(g['grade_f1'])} |")

w("\n### Few-shot (5 solved examples in the premise, hypothesis `Answer: {option}`; MMLU on a 2k subsample)\n")
w("| model | MMLU-2k 0-shot | MMLU-2k 5-shot | GPQA 0-shot | GPQA 5-shot | MMLU grading 0/5-shot | GPQA grading 0/5-shot |\n|---|---|---|---|---|---|---|")
for m in ORDER:
    r = fs.get(m)
    if r and "mmlu_fewshot" in r:
        g0 = ev[m]["gpqa"]
        w(f"| {NAMES[m]} | {f3(r['mmlu']['rerank_acc'])} | {f3(r['mmlu_fewshot']['rerank_acc'])} | {f3(g0['rerank_acc'])} | {f3(r['gpqa_fewshot']['rerank_acc'])} | {f3(r['mmlu']['grade_acc'])} / {f3(r['mmlu_fewshot']['grade_acc'])} | {f3(g0['grade_acc'])} / {f3(r['gpqa_fewshot']['grade_acc'])} |")
w("\nDemos do not help the entailment head (it is not an in-context learner); only the 4B gains a few points on MMLU.")

w("\n### Radar vs Jev and Terra\n\n![radar](assets/radar_openjev.png)\n")
w("All three series are zero-shot. Jev / Terra values are read off their published chart (approximate). Chess and GSM8K k-choice are our own constructions and may differ from theirs. Polygon area is not an aggregate score.")

w("\n## Real-time demos (zero-shot)\n")
w("The cross-encoder as a game policy with no training at all: the game state is the premise, the actions are the hypotheses, the action with the highest P(entailment) is taken every frame.\n")
w("**Flappy Bird** (`code/flappy.py`, game at 15 fps, one 4B forward per option per frame, ~55–65 ms per decision with `flash-linear-attention` kernels; 6 episodes, 900 frames max = 28 pipes). Premise = the state as a sentence (height, velocity, next gap, offset from the gap centre). Only the hypothesis wording changes; each hypothesis is a statement about the state bound to an action:\n")
w("| hypotheses (→ action) | pipes mean | pipes max |\n|---|---|---|")
for n, m_, mx in [("`The correct action is: flap` / `… do nothing`", "0.0", 0),
                  ("`The bird should flap now.` / `The bird should not flap now.`", "0.0", 0),
                  ("same, with a rule of thumb added to the premise", "17.7", 28),
                  ("`The bird is below the centre of the gap.` → flap / `… above …` → do nothing", "27.5", 28),
                  ("`… below the centre of the gap or falling fast.` / `… above …`", "0.3", 2),
                  ("`The offset relative to the gap centre is negative.` → flap / `… positive.` → do nothing", "**28.0**", 28),
                  ("(oracle heuristic)", "24.5", 28), ("(random)", "0.0", 0)]:
    w(f"| {n} | {m_} | {mx} |")
w("\nAsking the model to *name the action* fails; asking it to *verify a statement about the state* and binding that statement to an action gives a perfect game (28/28, above the heuristic oracle). Videos: `videos/flappy_nli.mp4`.")
w("\n**Doom, ViZDoom \"Defend the Center\"** (`code/doom.py`, turn left / turn right / attack, one decision per 4 tics = 114 ms budget, 5 episodes):\n")
w("| input | hypotheses (→ action) | kills mean | kills max | decision latency |\n|---|---|---|---|---|")
w(f"| - | (random) | {doom['random']['mean_kills']:.1f} | {doom['random']['max_kills']} | - |")
w(f"| labels buffer | (oracle heuristic) | {doom['oracle']['mean_kills']:.1f} | {doom['oracle']['max_kills']} | - |")
w(f"| text: enemies from the labels buffer (name, offset from crosshair, distance) | `The correct action is: turn left / turn right / attack` | {doom['nli']['mean_kills']:.1f} | {doom['nli']['max_kills']} | {doom['nli']['lat_ms']:.0f} ms |")
zs = {k: json.load(open(f"results/{k}.json"))["results"]["nli"] for k in ["doom_zs_position", "doom_zs_position_none"]}
w(f"| text, same state | `The nearest enemy is to the left of the crosshair.` → turn left / `… to the right of …` → turn right / `… exactly on the crosshair.` → attack | **{zs['doom_zs_position']['mean_kills']:.1f}** | {zs['doom_zs_position']['max_kills']} | {zs['doom_zs_position']['lat_ms']:.0f} ms |")
w(f"| text, same state | same + `There is no enemy in view.` → turn left | {zs['doom_zs_position_none']['mean_kills']:.1f} | {zs['doom_zs_position_none']['max_kills']} | {zs['doom_zs_position_none']['lat_ms']:.0f} ms |")
px = json.load(open("results/doom_vision_zeroshot_pixels.json"))["results"]
for k, lab in [("nli_pixels", "**pixels**: the 320×240 frame as image tokens through the Qwen3.5 vision tower; hypotheses about the monster's x-position (left / a little left / centre / a little right / right / none) → turn left / attack / turn right"),
               ("nli_pixels_sym", "pixels, 3 coarse position hypotheses"), ("nli_pixels_pct", "pixels, positions as % of screen width")]:
    d = px[k]; w(f"| {lab} | zero-shot NLI | {d['mean_kills']:.1f} | {d['max_kills']} | {d['lat_ms']:.0f} ms |")
w("\nThe pixel variant is the only one that needs no game-state parser at all: the frame goes in as image tokens (the vision tower was never fine-tuned; the NLI head only ever saw text), the hypotheses describe where the monster is, and each hypothesis is bound to an action. 5.2 kills vs 1.0 random and 18.8 for the oracle, ~100 ms per decision. With the text state and state-statement hypotheses the zero-shot head reaches 11.0 kills (oracle 18.8). Videos: `videos/doom_zs_position.mp4` (text state, position hypotheses), `videos/doom_nli.mp4` (text state, action hypotheses), `videos/doom_vision_zeroshot_pixels.mp4` (pixels).")
w("\n## Files\n\n* `qwen3.5-4b-nli/` — the 4B cross-encoder (transformers format, `id2label` in dleemiller order).\n* `modeling_openjev.py` — `OpenJevCrossEncoder`, `LatentMLPHead`, `soft_bce`.\n* `code/` — training (`train.py`), evaluation (`eval.py`, `latent_mlp.py`, `summarize.py`, `radar.py`), demos (`flappy.py`, `flappy_video.py`, `doom.py`, `sweep_flappy.sh`).\n* `results/` — raw JSON for every table above. `assets/`, `videos/`.\n\nReference model: [dleemiller/ModernCE-large-nli](https://huggingface.co/dleemiller/ModernCE-large-nli). License: MIT (model weights inherit the Qwen3.5 license).")
w("\n---\n\n## Appendix — not zero-shot: linear/MLP probes on the frozen latent\n")
w("For reference only. A small head `Linear(d, 512) → GELU → Dropout(0.1) → Linear(512, 1)` on the pooled last-token latent of the *frozen* cross-encoder, one scalar per (question, option), trained with a soft BCE loss (`BCEWithLogits(logit, y·(1−ε) + (1−y)·ε)`, ε = 0.1, positives re-weighted by (1−p)/p) on a few thousand labelled questions per task; argmax within each question at inference. `raw` = the same Qwen3.5 backbone without the NLI fine-tune.\n")
w("| backbone | " + " | ".join(LAB[t] for t in MC) + " |\n|---|" + "---|" * len(MC))
rows = [("openjev-0.8B zero-shot", ev["ckpt/qwen3.5-0.8b-nli"], "rerank_acc"), ("openjev-0.8B + MLP", mlp["ckpt/qwen3.5-0.8b-nli"], "mlp_per_task"),
        ("openjev-2B zero-shot", ev["ckpt/qwen3.5-2b-nli"], "rerank_acc"), ("openjev-2B + MLP", mlp["ckpt/qwen3.5-2b-nli"], "mlp_per_task"),
        ("raw Qwen3.5-2B + MLP", mlp["raw2b"], "mlp_per_task"),
        ("openjev-4B zero-shot", ev["ckpt/qwen3.5-4b-nli"], "rerank_acc"), ("openjev-4B + MLP", mlp["ckpt/qwen3.5-4b-nli"], "mlp_per_task"),
        ("raw Qwen3.5-4B + MLP", mlp["raw4b"], "mlp_per_task")]
for name, d, key in rows:
    w(f"| {name} | " + " | ".join(f3(d[t][key]) if t in d and key in d[t] else "-" for t in MC) + " |")
w("\nSoft-target ε (0 / 0.1 / 0.2) and appending the 3 NLI logits to the latent change nothing beyond noise; a joint head over all tasks is 1–4 pts behind per-task heads.")
w("\nData scaling of the 4B head (fraction of a larger labelled pool): MMLU 0.581 → 0.582 → 0.593 (0.1 / 0.3 / 1.0), WinoGrande 0.692 → 0.721 → 0.722, Chess 0.790 → 0.816 → 0.882. More data helps only where the pool matches the test distribution.")

w("\nWith such a probe the game policies reach oracle level (Flappy 28/28 pipes, Doom 16.0 kills mean vs oracle 18.8); raw JSON in `results/` (`latent_mlp_*.json`, `flappy_4b*.json`, `doom_4b.json`).")
open("README_hf.md", "w").write("\n".join(out) + "\n")
print("wrote README_hf.md", len("\n".join(out)) // 1024, "KB")
