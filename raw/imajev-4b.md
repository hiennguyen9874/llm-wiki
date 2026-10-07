---
license: apache-2.0
base_model: Qwen/Qwen3.5-4B
library_name: peft
pipeline_tag: image-text-to-text
language:
- en
tags:
- typed-decisions
- jev
- decision-model
- vision-language
- calibrated-probabilities
- lora
- mlx
---

<p align="center">
  <img src="assets/logo-light.png" class="block dark:hidden" width="300" alt="imajev">
  <img src="assets/logo-dark.png" class="hidden dark:block" width="300" alt="imajev">
</p>

<h3 align="center">Decisions for real-world cases.</h3>

<p align="center">Small open models that read the photos, records and text a business already has and answer in the options you set,
with a probability on each and an explicit <i>can't tell</i>. Your system acts when it is sure and hands the rest to a person.</p>

<p align="center">
  <a href="https://huggingface.co/spaces/mohit67890/imajev"><img alt="Try the live demo" src="https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-md.svg"></a>
  <a href="https://github.com/mohit67890/imajev"><img alt="GitHub" src="https://img.shields.io/badge/GitHub-mohit67890%2Fimajev-111111?style=flat-square&logo=github"></a>
  <a href="https://mohit67890.github.io/imajev/"><img alt="Website" src="https://img.shields.io/badge/website-checked%20examples-555555?style=flat-square"></a>
  <a href="https://huggingface.co/datasets/mohit67890/imajev-bench"><img alt="ImajevBench" src="https://img.shields.io/badge/benchmark-ImajevBench-555555?style=flat-square"></a>
  <img alt="Apache-2.0" src="https://img.shields.io/badge/licence-Apache--2.0-111111?style=flat-square">
</p>

<p align="center"><b>imajev-4b</b> is the recommended default of the family · other sizes: <a href="https://huggingface.co/mohit67890/imajev-2b">imajev-2b</a> · <a href="https://huggingface.co/mohit67890/imajev-9b">imajev-9b</a><br>
<a href="https://huggingface.co/spaces/mohit67890/imajev"><b>Live demo</b></a> · <a href="https://mohit67890.github.io/imajev/">Website</a> ·
<a href="https://github.com/mohit67890/imajev">Code and results</a> · <a href="https://mohit67890.github.io/imajev/report/">Technical report</a></p>

<p align="center"><a href="https://benchmarkheaven.com/jev-models"><img src="assets/ranks-light.png" class="block dark:hidden" width="820" alt="#1 of 91 on JevBench v1.4.2.2 (scored 27 Sep 2026); #1 of 49 on Image JevBench v0.1.3 (released 28 Sep 2026); #3 of 56 on DecisionBench (eng, v1), 28 Sep 2026."><img src="assets/ranks-dark.png" class="hidden dark:block" width="820" alt="#1 of 91 on JevBench v1.4.2.2; #3 of 56 on DecisionBench"></a></p>


<p align="center"><b>Independent results</b> (screenshots of the official leaderboards, 28 Sep 2026)</p>
<p align="center"><a href="https://benchmarkheaven.com/jev-models"><img src="assets/proof-jevbench-score.png" width="760" alt="JevBench v1.4.2.2 Composite Score: 1 Imajev-4B 67.4, 2 Plumb-4B 65.8, 3 decider-4b v2 64.1, 4 Jev 1.13.0 63.3"></a></p>
<p align="center"><a href="https://benchmarkheaven.com/image-jev-bench"><img src="assets/proof-image-jevbench.png" width="760" alt="Image JevBench v0.1.3 composite: 1 Imajev-4B 76.39, 2 Jev-Omni 73.10, 3 NeoHorse Jev 4B 71.94"></a></p>
<p align="center"><a href="https://huggingface.co/spaces/Hanno-Labs/decision-bench-leaderboard"><img src="assets/proof-decisionbench.png" width="760" alt="DecisionBench (eng, v1): 1 bosun-v3.1-1.7b 87.29, 2 bosun-v3.1-0.6b 83.20, 3 imajev-4b 79.65, ahead of glm-5.3-flash, jev-1.13, deepseek-v4.1-flash, gpt-5.6-luna"></a></p>
<p align="center"><sub>JevBench v1.4.2.2, scored 27 Sep 2026 (<a href="https://benchmarkheaven.com/jev-models">board</a>). Image JevBench v0.1.3, released 28 Sep 2026: #1 of 49, 76.39, ahead of Jev-Omni (<a href="https://benchmarkheaven.com/image-jev-bench">board</a>). DecisionBench (eng, v1): #3 of 56 models, 79.65, ahead of GLM-5.3 Flash (320B), Jev 1.13, DeepSeek V4.1 Flash (552B) and GPT-5.6 Luna; the two above are the benchmark team's own models (<a href="https://huggingface.co/spaces/Hanno-Labs/decision-bench-leaderboard">leaderboard</a>).</sub></p>

<p align="center"><img src="assets/request-listing.png" class="block dark:hidden" alt="imajev-4b checks a listing against its photo: listing.color says red, the photo shows beige shoes; the model names listing.color at 0.999 and the app holds the listing"><img src="assets/request-listing-dark.png" class="hidden dark:block" alt="imajev-4b checks a listing against its photo: listing.color says red, the photo shows beige shoes; the model names listing.color at 0.999 and the app holds the listing"></p>

imajev-4b is the recommended default: 83.9% on ImajevBench against the 9B's 82.1% at under half the size, and the only size trained in the phase-3 hard-data stage.

## What sets it apart

<p><img src="assets/highlights.png" class="block dark:hidden" alt="Five highlights: a photo read against your record; two photos, one decision; a trained can't tell; open, small and local; Jev's contract, now with images"><img src="assets/highlights-dark.png" class="hidden dark:block" alt="Five highlights: a photo read against your record; two photos, one decision; a trained can't tell; open, small and local; Jev's contract, now with images"></p>

- **A photo read against your record.** Checks a photo against your own fields and names the one that is wrong. Trained on 72k
  photo-vs-record and two-photo decisions.
- **Two photos, one decision.** A reference and a target in the same request: shipped against returned, a known-good part against
  the one on the line.
- **A trained *can't tell*.** Every answer carries a probability for `unknown`, so the app can stop instead of guessing.
- **Open, small and local.** Apache-2.0, MLX on a Mac or PyTorch on one GPU; photos and customer data never leave your network.
- **Jev's contract, now with images.** TypeSafe's Jev request and response (`POST /v1/systemone`), plus `images`,
  `unknown_probability` and `abstained`. Jev itself is text-only and hosted; its state limit (32k tokens) is larger than imajev's (32 KB).

## One request, every answer typed

The exact script we ran against imajev-4b and its output (rounded, `usage` shortened); 1.15 s on a Mac Studio (four option orders averaged, calibration file applied). Swap the adapter for
this size and the request is unchanged.

```python
import json, requests

URL = "http://127.0.0.1:8765/v1/systemone"

listing = {
    "title": "Men's suede boat shoes",
    "color": "red",
    "product_type": "shoe",
}

questions = {
    "contradicted_field": {
        "type": "choice",
        "instructions":
            "Which field of `listing` does this photo contradict?",
        "criteria": {
            "listing.color": None,
            "listing.product_type": None,
            "none of these": "the photo agrees with every field",
        },
    },
    "color_matches": {
        "type": "noul",
        "instructions":
            "The product in the photo matches `listing.color`.",
    },
    "type_matches": {
        "type": "noul",
        "instructions": "The photo shows the kind of product "
                        "given in `listing.product_type`.",
    },
}

request = {"state": {"listing": listing}, "questions": questions}
with open("listing.jpg", "rb") as photo:
    r = requests.post(URL, files={"image": photo},
                      data={"request": json.dumps(request)})
print(json.dumps(r.json(), indent=2))
```

<details><summary>Result</summary>

```json
{
  "model": "imajev-4b",
  "answers": {
    "contradicted_field": {
      "type": "choice",
      "choice": "listing.color",
      "probabilities": {
        "listing.color": 0.95,
        "listing.product_type": 0.006,
        "none of these": 0.043
      },
      "confidence": 0.919,
      "unknown_probability": 0.007,
      "abstained": false
    },
    "color_matches": {
      "type": "noul",
      "noul": 0.082,
      "unknown_probability": 0.022,
      "abstained": false
    },
    "type_matches": {
      "type": "noul",
      "noul": 0.989,
      "unknown_probability": 0.004,
      "abstained": false
    }
  },
  "usage": {
    "total_ms": 1152.9,
    "input_tokens": 224
  }
}
```
</details>

<p><img src="assets/request-ticket.png" class="block dark:hidden" alt="A support ticket answered in one text-only request: department, urgency and frustration"><img src="assets/request-ticket-dark.png" class="hidden dark:block" alt="A support ticket answered in one text-only request: department, urgency and frustration"></p>

## Automate what is clear, route the rest

<p><img src="assets/automation.png" class="block dark:hidden" alt="At a 90% threshold imajev-4b decides 58% of ImajevBench questions automatically, 97.5% of them correctly"><img src="assets/automation-dark.png" class="hidden dark:block" alt="At a 90% threshold imajev-4b decides 58% of ImajevBench questions automatically, 97.5% of them correctly"></p>

imajev-4b on the 279 ImajevBench test questions (photos, records and text; 21 whose honest answer is *can't tell*), raw
probabilities, scored with the benchmark's own rule:

| Act automatically when at least… | Decisions automated | Automatic decisions right |
|---|---:|---:|
| 80% sure | 63% | 94.9% |
| 90% sure | 58% | 97.5% |
| 99% sure | 40% | 100% |

The rest go to a person. The benchmark is built to be hard; measure on a few hundred of your own cases before choosing a threshold.
Other sizes at 90%: 2B 38% automated at 95.3% right, 4B 58% at 97.5%, 9B 70% at 91.8%.

**Checked demos.** Every clickable combination in the five playground apps (business checks, text only, wardrobe, stylist, tracing pad) was run on imajev-4b (four option orders) and compared with the right answer: 130 of 145 pass without the calibration file, 118 with it. Only passing combinations are shown as demos; the misses are listed in `reports/scenarios/`.

## How it was made

About a million training decisions across the family, in four stages, for about $676 of rented GPU time for the whole project.
The 4B was trained on stages 1 and 2 in one run (867k decisions: the 504k human-labelled set, 296k labelled by our 9B and 66k photo-vs-record and two-photo decisions), then on about 23k hard questions kept only when open-weight teachers agreed, then a soft-target continuation on 39,515 rows carrying Qwen3.6-35B-A3B's full probability distributions (with the strict slice of the Eikos decisions set (`caiovicentino1/eikos-decisions`, CC-BY-4.0; attribution and per-source licences in `docs/eikos-decisions-usage.md`) and 5k replayed image decisions). The shipped adapter is the weight-space average of two adapters: the hard-question adapter and that continuation. Every teacher is open-weight; no Jev outputs, paid-API outputs or JevBench items were used.

## This adapter

This repository holds the **4B adapter**: the recommended default tier — the best accuracy per millisecond in the family. It is a
LoRA (rank 64, alpha 128) on the language layers of Qwen3.5-4B (revision `851bf6e8`) plus a 256-code decision readout (255 option
codes and `unknown`), in PEFT format at the root and in MLX format under `mlx/`. It is the last checkpoint of the phase-3 run: the
previous release (a rank-16 weight-space average) expanded to rank 64 and trained for two rounds on the decisions that release got
wrong. Code, server and evaluation harness: https://github.com/mohit67890/imajev.
Other tiers: https://huggingface.co/mohit67890/imajev-2b (latency), https://huggingface.co/mohit67890/imajev-9b (quality); both are
still the previous-generation adapters.

## Technical specification

| | |
|---|---|
| Base model | Qwen/Qwen3.5-4B, revision `851bf6e8` (Apache-2.0) |
| LoRA | rank 64, alpha 128 (scale 2, as before), dropout 0, no bias, on every language-model projection: `q,k,v,o`, `gate,up,down` and the DeltaNet `in_proj_qkv`, `in_proj_z`, `out_proj`; vision encoder frozen, no LoRA |
| Decision readout | one bias-free linear layer, 256 × 2560, float32 (255 option codes + `unknown`) |
| Trainable parameters | 121,896,960 LoRA + 655,360 readout = 122,552,320 |
| Files | `adapter_model.safetensors` 487.6 MB (F32); readout 2.6 MB |
| Precision | base weights bfloat16; LoRA and readout float32 (MLX copies under `mlx/` converted from the same files) |
| Request limits | 0–2 images (resized to at most 400,000 pixels), state up to 32 KB, 1–8 questions, 2–255 options per `choice`, 2–10 levels per `score`, at most 4,096 tokens (longer requests are refused, not truncated); English only |
| Calibration | one temperature, 1.305, fitted on 150 template-generated JevBench-style items (none from JevBench); `calibration-rot4.json` is the same fit for the 4-rotation serving mode |

**Training path.** One trainer for every stage (PyTorch + PEFT): cross-entropy on the readout logits (soft targets where a
record carries a distribution), AdamW with weight decay 0, linear warm-up then cosine decay to 10% of the peak rate, gradient
clipping 1.0, seed 0, 4 GPUs. The soft-target stage adds a rationale loss (weight 0.3, at most 192 tokens) and permutes the
options of every question.

| Stage | Started from | Epochs | Peak LR | Steps (kept / total) | Hardware | Time |
|---|---|---|---|---|---|---|
| First run (stages 1 and 2 combined) | Qwen3.5-4B | 0.5 | 1.5e-4 | 1,900 / 2,595 | 4×H200 | 1.9 h (2 h 06 min wall) |
| Stage 3, round 1 | first run | 2 | 3e-5 | 250 / 303 | 4×H200 | 12 min |
| Stage 3, round 2 | round 1 | 2 | 2e-5 | 266 / 266 | 4×H100 | 22 min (27 min wall) |
| Stage 4, soft-target continuation | round 2 | 2 | 2e-5 | 260 / 747 | 4×H100 | 1.4 h (out of memory at step 625, resumed at the same budget) |
| Weight-space average (= the previous release) | ½ round 2 + ½ stage 4, element-wise (LoRA and readout) | – | – | – | – | – |
| Stage 5 (phase 3), round 1 | previous release, LoRA rank 16 → 64 (identical output at step 0), readout 255 → 256 codes | 2 | 2e-5 | 2,640 / 2,640 | 8×H100 | 3 h 13 min |
| Stage 5, round 2 | round 1 | 1 | 1e-5 | 291 / 291 | 8×H100 | 23 min |

**Data this size saw.**

- **First run:** 866,854 decisions: 504,000 stage-1 decisions with their original labels (36 licence-admitted sources); 296,482
  stage-2 decisions labelled by the 9B, with `unknown` targets capped at 15%; 66,372 photo-vs-record and two-photo decisions.
  17.15% of its training targets are `unknown`; no base-model blend.
- **Stage 3, round 1:** 14,112 training records: kept teacher questions (9,368 of 13,386 kept on two-answerer agreement) plus the
  training share of 8,532 human reasoning items from 10 licensed sets.
- **Stage 3, round 2:** 7,812 training records: 3,598 new (4,852 of 8,097 kept on three-answerer agreement) + 4,214 replayed from round 1.
- **Stage 4:** 39,515 records: the stage-3 teacher questions relabelled with Qwen3.6-35B-A3B's probability distributions (thinking
  mode), 9,880 new hard, judge and programmatic questions, the strict slice of the Eikos decisions set (10,570 rows, open-weight
  teachers only) and 5,000 replayed image decisions.

- **Stage 5 (phase 3), round 1:** 125,424 rows: 58,000 hard text and 32,427 hard image decisions the previous release got wrong, mined from a
  210,565-candidate pool (our generators, public datasets, earlier pools, trap variants), labelled by Qwen3.6-35B-A3B (thinking) with
  distribution targets and kept only after an independent review (Kimi-K2.5 plus a 220-item blind human-style review; families over 5%
  estimated label error dropped), including 20,270 constructed chart, document, inventory, safety, geometry and screenshot decisions with
  answers by construction; 19,998 earlier text and 14,999 earlier photo decisions replayed. 22% of targets are `unknown`.
- **Stage 5, round 2:** 26,494 rows: the 13,247 labelled items the round-1 model still failed plus 13,247 replayed.

**Compute.** $499.07 of rented GPU time on RunPod through stage 3, about $177 for stage 4 (all three sizes) and, for stage 5 (4B only),
$177 of training (8×H100, 6 h 20 min incl. the pilot and the full evaluation) plus about $414 of mining, teacher labelling and review
(RunPod and Azure, open-weight teachers): about $1,270 for the whole project, every run included.

Full specification: https://github.com/mohit67890/imajev/blob/main/docs/technical-specification.md

## Results (2026-09-26; every number reproducible from the repo's `reports/`)

| Benchmark | imajev-4b (this version) | Previous version (same pod, same protocol) | Notes |
|---|---|---|---|
| JevBench public hard (111) | **72.1%** with 4 option rotations + calibration (ECE 0.082); single pass 71.2% raw (ECE 0.113), 71.2% calibrated (ECE 0.082) | 70.3% served; 69.4% raw | unchanged within noise (111 items, ±3.7 pts); same protocol, our runs: JevK5 v0.2.0 73.9% / 0.073, Eikos-4B 73.9% / 0.054, Hopper 67.6% / 0.050, Qwen3.5-4B base (generation) 48.6%; a frozen Qwen3.6-35B-A3B with thinking 97.3% at seconds per decision |
| JevBench public original / easy | 98.6% / 100% | 98.6% / 100% | |
| JevBench public, served from a Mac (MLX, 4 rotations + calibration) | 71.2% hard (ECE 0.073), 98.6% original, 100% easy | 70.3% | parity check of the `mlx/` weights |
| ImajevBench v2.0-lite test (279 items: text, photo, photo+state) | **83.9%** (234/279); tracks text 25/37 · visual 109/120 · joint 100/122 | 82.4% (230/279); 26/37 · 107/120 · 97/122 | Qwen3.5-4B base 70.6%; imajev-9b 82.1%; frontier APIs by structured generation 91–99.6% (a different interface) |
| MLX (Mac) vs PyTorch on ImajevBench public test | 83.9% vs 83.9% (234/279 both), 98.6% argmax agreement (275/279); ECE 0.059 vs 0.070 | 82.1% vs 82.4% | parity check of the `mlx/` weights against the pod run |
| ImajevBench private-1 hidden split (202; aggregates only) | 85.6% (173/202); text 20/30 · visual 83/84 · joint 70/88; ECE 0.029 | 84.2% | run on a Mac (MLX weights), the previous version on the pod |
| Fresh held-out hard set (4,297 decisions from every generator family and the unflagged pool, never mined or trained on) | **87.2%** | 68.4% | same generators as the training data: an in-distribution number |
| Human-verified slice (785 decisions, blind-reviewed labels) | **76.2%** | 48.2% | |
| Constructed image sets, held-out (charts 300 / documents 300 / inventory 250 / safety 250 / geometry 250 / screenshots 250) | 95.7 / 90.3 / 67.6 / 92.4 / 88.4 / 95.6% | 84.0 / 76.0 / 54.8 / 72.0 / 66.4 / 72.8% | answers by construction; inventory (shelf counts) stays the weakest |
| DecisionBench 1.0 (Hanno-Labs), full suite (23,900 rows), the benchmark's own harness, 4 rotations + calibration, 64k-token serving limit | **79.7%** primary, every row scored (coverage 100%); ECE 0.069; reasoning family 80.6%, ordinal scoring 46.2% | 77.5% primary (79.3% scored; 537 rows unsupported); ECE 0.024; reasoning 68.0%, ordinal 40.3% | the previous version had the lowest ECE of 55 on the board (2026-09-25); this version's record (revision `c9e5f132`) is in the official registry (PR #68, merged 28 Sep 2026): #3 of 60 records, behind only the benchmark team's own Bosun v3.1 1.7B (84.9) and 0.6B (81.2); it trades calibration (ECE 0.024 → 0.069) for accuracy on this suite |
| fastino/fast-decisions dev (1,700 rows, 17 domains; their board scores a held-out test split) | 60.4% domain macro (59.4% pooled heads) | 59.0% (58.4%) | not comparable to their board |
| Irrelevance panel (2,823) | 80.0% | 80.2% | |
| Hard-question test (435): correct on Unknown-gold rows / false abstention | **11/14** · 0.48% | 14/14 · 0.24% | this version answers 3 of the 14 unknown-gold items (at 0.83, 0.60 and 0.51 confidence); the previous release's 14/14 ship gate was **overridden** for this release, see Limits |
| State probe / pairs probe | 76.5% / 96.7% | 71.5% / 98.3% | |
| S1-Bench, typed conversion (212 of the 220 English items; our derivative, not an S1-Bench score) | 99.1% (ECE 0.019, abstention 0) | 98.6% (0.006) | saturated: a no-regression check on simple questions |
| Atlan Decision Bench bench-v4 (atlanai/decision-bench; 1,071 rows, 35 tasks, 36 public sources; their harness through its Jev-compatible adapter, text only) | 86.6% (928/1,071, Wilson 84.5–88.6; 88.6% on the 1,041 rows a text-only model can answer); ECE 0.021, Brier 0.189 | not run | Jev 1.13 92.4%, Claude Haiku 4.5 90.6%, Tev1-4B 85.4%, Laya 52.8% on their board; one Civil Comments row of the corpus is in our training data (disclosed); run on a Mac, latency not comparable |
| LocalLLaMA/typed-decisions test (400 cases × 5 = 2,000 decisions; gold is teacher agreement) | 69.2% (choice 67.8 / yes-no 77.0 / score 64.2); calibrated Brier 0.423, ECE 0.025 | 67.0% | Intern-Decision-4B reports 80.6%, Jev 73.4%, JevK5 64.5% on the same records (their runs, 2026-09-26); the score questions are our weakest type |
| MMLU-1000, text-only / with an unrelated photo; two-image / held-out photo sources | 74.5% / 72.9%; 41.8% / 56.7% | | measured on earlier versions, not re-run |

Every number in this table was produced in one evaluation on 2026-09-26 (pod ctr4dy9bzom5ji, 8×H100) with the previous release
re-measured under the identical protocol; the full table for all eight phase-3 checkpoints, with item counts and gate results, is
`reports/phase3/train-results/benchmarks.md` in the repo. The paired cluster test of this version against the previous one on
ImajevBench (89 evidence clusters) is pending; the previous release beat its untuned base by +11.8 points [+5.8, +18.0], p = 0.0006.
JevBench is text-only; imajev's image capability shows only on ImajevBench and in use. The official JevBench board adds
308 sealed items and a four-axis score run by its maintainer: there this adapter (revision `c9e5f132`, served with `--rotations 1 --calibration calibration.json`) is **#1 of 91 on JevBench v1.4.2.2** (scored 27 Sep 2026; JevBench Score 67.37: Intelligence 52.2, Calibration 80.4, Speed 90.6, Cost 59.7; Jev 1.13.0 63.29). Source: https://benchmarkheaven.com/jev-models.

## Calibration

`calibration.json` (schema 1.0) applies one temperature (1.305) to every question type × option-count bucket, fitted by negative
log-likelihood on 150 template-generated JevBench-style items (none from JevBench). `calibration-rot4.json` is the same fit for the
4-rotation serving mode. A per-type fit on the flagged half of our held-out set was tried and rejected: it lowers hard-tier ECE but
raises the pooled ECE over all public JevBench items (0.059 single / 0.039 rot4 against a 0.03 guard). Temperature scaling never
changes an answer, only its probability. `unknown` offsets are 0.

Checked through the evaluation server (ECE, uncalibrated → with `calibration.json`); the off-distribution rows were measured on the
previous version with its own temperature and have not been re-run for this version:

| Panel | ECE |
|---|---|
| JevBench public hard, single pass (111) | 0.113 raw → 0.082 |
| JevBench public hard, 4 rotations (111) | 0.079 raw → 0.082 |
| Pooled over all 231 public JevBench items, single pass | 0.064 raw → 0.046 |
| MMLU-1000, text-only (previous version) | 0.150 → 0.035 |
| typed-decisions test (2,000; previous version) | 0.149 → 0.047 |
| SST-5 (2,210; previous version) | 0.220 → 0.020 |
| Photo-only verification (ABO + VizWiz, 823; previous version) | 0.038 → 0.062 |

On photo-only verification the previous version's raw probabilities were already calibrated and the temperature over-softened them; if
your traffic is mostly photo-against-record checks, serve without `--calibration` or fit your own temperature on a held-out sample.

## Serving
```sh
git clone https://github.com/mohit67890/imajev && cd imajev
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e ".[serve,mlx]"            # Apple silicon;  elsewhere: pip install -e ".[serve,torch]"
python scripts/download_model.py --model 4b
hf download mohit67890/imajev-4b --local-dir adapters/imajev-4b
# Mac (MLX)
PYTHONPATH=src:scripts python scripts/playground/server.py --model-bundle artifacts/model-qwen4b.json \
  --adapter adapters/imajev-4b/mlx --rotations 4 --calibration adapters/imajev-4b/calibration-rot4.json --model-name imajev-4b --port 8765
# Linux / CUDA (PyTorch + PEFT)
PYTHONPATH=src:scripts python scripts/playground/server.py --backend torch --model-bundle artifacts/model-qwen4b.json \
  --adapter adapters/imajev-4b --rotations 4 --calibration adapters/imajev-4b/calibration-rot4.json --model-name imajev-4b --port 8765
```
Then `POST /v1/systemone` with a Jev-shaped request. One forward pass per question: p50 96 ms raw on one H100 for a JevBench hard
item, serially; 350 ms with the `--rotations 4` (four option orders averaged, +0.9 hard) and `calibration.json` used for the numbers
above (shared pod, under load).

## Training data and provenance
Synthetic documents and typed questions written by Qwen3.6-27B, answered independently by Qwen3.6-27B (thinking), gpt-oss-20b and,
in the last part of the hard-question stage, Qwen3.6-35B-A3B (thinking); a question is kept only when every answerer agrees with the intended answer. In the
soft-target stage the same questions were relabelled with Qwen3.6-35B-A3B's probability distributions (thinking mode), joined by 9,880 new hard, judge and
programmatic questions, the strict slice of the Eikos decisions set (10,570 rows, open-weight teachers only) and 5,000 replayed image decisions; the
shipped adapter is the weight-space average of the hard-question adapter and that continuation's best checkpoint. Plus
licensed image datasets and human-written states from earlier training stages (see the repo's datasheets). No JevBench items (8-gram lint),
no outputs from Jev or any paid API. All teachers are open-weight, Apache-2.0.

## Limits

Single-pass: no reasoning at inference, so multi-step arithmetic and answer-quality judging trail reasoning models (a frozen
Qwen3.6-35B-A3B *with thinking* scores 97% on JevBench hard at seconds per decision); the phase-3 stage moved our own hard held-out
sets by 19 to 28 points but left JevBench hard unchanged within noise. Over-confident without `calibration.json`. On the previous
release's 14-item unknown-gold check this version abstains on 11 (the previous release on all 14) while its false-abstention rate on
answerable items stays at 0.5%: it is slightly less conservative on borderline "cannot tell" cases, and that ship gate was overridden
for this release. Two-image comparisons are the weakest visual task (41.8% on real pairs, measured on an earlier imajev-4b); shelf
inventory counts are the weakest constructed image family (67.6%). English only. The 2B and 9B tiers are still the previous generation.
