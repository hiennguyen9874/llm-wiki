---
type: Concept
title: Imajev-4B Vision Decision Model
description: Apache-2.0 Qwen3.5-4B LoRA vision decision model with Jev-compatible Choice/Noul plus images, trained unknown, and reported JevBench/Image-JevBench leads.
tags: [jev, decision-models, multimodal, calibration]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T00:00:00Z }
stale_after: 2027-09-28
sources:
  - id: imajev-4b-2026-09-28
    resource: ../raw/imajev-4b.md
    kind: model-card
    title: mohit67890/imajev-4b
---

# Imajev-4B Vision Decision Model

Synthesis: `mohit67890/imajev-4b` is the recommended default of the Imajev family — an Apache-2.0 LoRA adapter on Qwen3.5-4B that adds photo-vs-record and two-photo typed decisions to Jev's Choice/Noul contract with a trained `unknown` and per-answer `unknown_probability`/`abstained`, with **reported** #1 of 91 on JevBench v1.4.2.2 and #1 of 49 on Image JevBench v0.1.3 plus #3 of 56 on DecisionBench (eng, v1)[^imajev-4b-2026-09-28].

## Identity and provenance

- Author `mohit67890`; family tiers `imajev-2b` (latency), `imajev-4b` (recommended default), `imajev-9b` (quality); 2B and 9B are still previous-generation adapters while 4B is the phase-3 adapter described here[^imajev-4b-2026-09-28].
- Base `Qwen/Qwen3.5-4B` revision `851bf6e8` (Apache-2.0); frontmatter declares `base_model`, `pipeline_tag: image-text-to-text`, PEFT library, English only; license Apache-2.0[^imajev-4b-2026-09-28].
- Canonical entry is the local model card `../raw/imajev-4b.md`; upstream code, server, and evaluation harness at `github.com/mohit67890/imajev`, live demo HF Space, website checked examples, technical report, and `imajev-bench` dataset; HF model `mohit67890/imajev-4b` with sibling `imajev-2b`/`imajev-9b` links[^imajev-4b-2026-09-28].
- Training provenance is **reported** as all open-weight teachers with no Jev outputs, no paid-API outputs, and no JevBench items (8-gram lint); strict Eikos slice attribution and per-source licences in repo `docs/eikos-decisions-usage.md`[^imajev-4b-2026-09-28].

## Architecture and adapter — observed

- LoRA rank 64, alpha 128 (scale 2), dropout 0, no bias, on every language-model projection (`q,k,v,o`, `gate,up,down`, DeltaNet `in_proj_qkv`, `in_proj_z`, `out_proj`); vision encoder frozen with no LoRA[^imajev-4b-2026-09-28].
- Decision readout is one bias-free linear layer 256×2560 float32 (255 option codes plus `unknown`); trainable total 122,552,320 (121,896,960 LoRA plus 655,360 readout); files `adapter_model.safetensors` 487.6 MB F32 plus 2.6 MB readout; base bfloat16 with LoRA/readout float32 and MLX copies under `mlx/` converted from the same files[^imajev-4b-2026-09-28].
- Shipped adapter is a weight-space average of two adapters (hard-question adapter plus soft-target continuation), last checkpoint of the phase-3 run; the previous release (rank-16 average) was expanded to rank 64 and trained two rounds on decisions that release got wrong[^imajev-4b-2026-09-28].

## Interface and serving

- Contract is TypeSafe Jev `POST /v1/systemone` plus `images`, `unknown_probability`, and `abstained`; Jev itself is text-only hosted with a 32k-token state limit versus imajev's 32 KB state limit[^imajev-4b-2026-09-28].
- Worked example (rounded, Mac Studio 1.15 s with four option orders averaged plus calibration): listing `color: red` photo of beige shoes returns `contradicted_field` Choice `listing.color` 0.95, `color_matches` Noul 0.082, `type_matches` Noul 0.989, each with `unknown_probability` and `abstained: false`[^imajev-4b-2026-09-28].
- Request limits are 0–2 images (resized to at most 400,000 px), state up to 32 KB, 1–8 questions, 2–255 options per `choice`, 2–10 levels per `score`, at most 4,096 tokens with longer requests refused not truncated; English only[^imajev-4b-2026-09-28].
- Serving is Mac MLX (`artifacts/model-qwen4b.json` plus `adapters/imajev-4b/mlx`) or Linux/CUDA PyTorch plus PEFT, via `scripts/playground/server.py` with `--rotations 4 --calibration` and `--model-name imajev-4b --port 8765`; one forward pass per question with **reported** p50 96 ms raw on one H100 for a JevBench hard item, 350 ms with 4 rotations plus calibration under shared-pod load[^imajev-4b-2026-09-28].

## Vision capability

- Photo read against own record: names which field is wrong, trained on 72k photo-vs-record and two-photo decisions; two-photo mode takes reference plus target (shipped versus returned, known-good versus line part)[^imajev-4b-2026-09-28].
- Trained can't-tell: every answer carries an `unknown` probability so the app stops instead of guessing; open/small/local (MLX Mac or one-GPU PyTorch, photos and customer data stay on network)[^imajev-4b-2026-09-28].
- Checked demos are **reported**: every clickable combination in five playground apps run on imajev-4b (four option orders) versus the right answer, 130 of 145 pass raw and 118 with calibration; only passing combinations are shown, misses listed in repo `reports/scenarios/`[^imajev-4b-2026-09-28].

## Training — reported

- About a million training decisions across the family; project compute about $1,270 all runs included ($499.07 rented RunPod through stage 3, ~$177 stage 4 all three sizes, stage-5 4B-only $177 training on 8×H100 6h20m plus ~$414 mining/labelling/review)[^imajev-4b-2026-09-28].
- First run (stages 1+2 combined): 866,854 decisions (504k stage-1 with original labels from 36 licence-admitted sources, 296,482 stage-2 labelled by the 9B with `unknown` capped at 15%, 66,372 photo-vs-record/two-photo); 17.15% `unknown` targets; 0.5 epochs, peak LR 1.5e-4, 1,900/2,595 steps on 4×H200 in ~1.9 h[^imajev-4b-2026-09-28].
- Stage 3 round 1: 14,112 records (9,368 of 13,386 teacher questions kept on two-answerer agreement plus training share of 8,532 human reasoning items from 10 licensed sets), 2 epochs LR 3e-5; round 2: 7,812 records (3,598 new from 4,852 of 8,097 kept on three-answerer agreement plus 4,214 replayed), 2 epochs LR 2e-5[^imajev-4b-2026-09-28].
- Stage 4 soft-target continuation: 39,515 records (stage-3 questions relabelled with Qwen3.6-35B-A3B thinking-mode distributions, 9,880 new hard/judge/programmatic, 10,570 strict Eikos rows open-weight teachers only, 5,000 replayed image decisions); cross-entropy on readout logits with soft targets plus rationale loss 0.3 (≤192 tokens), option permutation, AdamW decay 0, warmup plus cosine to 10%, clip 1.0, seed 0, 4 GPUs; 2 epochs LR 2e-5, 260/747 steps on 4×H100 in 1.4 h after OOM resume[^imajev-4b-2026-09-28].
- Stage 5 (phase 3) round 1: 125,424 rows (58k hard text plus 32,427 hard image the previous release got wrong, mined from 210,565 candidates, labelled by Qwen3.6-35B-A3B thinking with distribution targets, kept after Kimi-K2.5 plus 220-item blind review with >5% error families dropped, including 20,270 constructed chart/document/inventory/safety/geometry/screenshot decisions with answers by construction; 19,998 text plus 14,999 photo replayed; 22% `unknown`); 2 epochs LR 2e-5, 2,640/2,640 steps on 8×H100 in 3h13m; round 2: 26,494 rows (13,247 still-failed plus 13,247 replayed), 1 epoch LR 1e-5, 291/291 steps in 23 min[^imajev-4b-2026-09-28].

## Reported benchmarks (2026-09-26 single evaluation, previous release re-measured identically)

All figures below are vendor **reported** from one 2026-09-26 pod run (8×H100) with full tables in repo `reports/phase3/train-results/benchmarks.md`; JevBench is text-only so image capability shows only on ImajevBench and in use[^imajev-4b-2026-09-28].

- Official leaderboards (screenshots 28 Sep 2026): JevBench v1.4.2.2 #1 of 91, Score 67.37 (Intelligence 52.2, Calibration 80.4, Speed 90.6, Cost 59.7) versus Jev 1.13.0 63.29, served `--rotations 1 --calibration calibration.json` revision `c9e5f132`; Image JevBench v0.1.3 #1 of 49 at 76.39 versus Jev-Omni 73.10 and NeoHorse Jev 4B 71.94; DecisionBench (eng, v1) #3 of 56 (record #3 of 60, behind Bosun v3.1 1.7B 84.9/87.29 and 0.6B 81.2/83.20) at 79.65–79.7 ahead of GLM-5.3 Flash, Jev 1.13, DeepSeek V4.1 Flash, GPT-5.6 Luna[^imajev-4b-2026-09-28].
- JevBench public hard (111): 72.1% with 4 rotations plus calibration (ECE 0.082) versus previous 70.3% served; single-pass 71.2% raw (ECE 0.113) and calibrated (ECE 0.082); same-protocol JevK5 v0.2.0 73.9%/0.073, Eikos-4B 73.9%/0.054, Hopper 67.6%/0.050, Qwen3.5-4B base generation 48.6%, frozen Qwen3.6-35B-A3B thinking 97.3% at seconds per decision; original/easy 98.6%/100%; Mac MLX 4-rotation parity 71.2% hard (ECE 0.073)[^imajev-4b-2026-09-28].
- ImajevBench v2.0-lite test (279: text, photo, photo+state): 83.9% (234/279; text 25/37, visual 109/120, joint 100/122) versus previous 82.4% and base 70.6%, 9B 82.1%, frontier structured-generation APIs 91–99.6% (different interface); MLX versus PyTorch parity 83.9%/83.9% with 98.6% argmax agreement (ECE 0.059 vs 0.070); private-1 hidden split (202) 85.6% (ECE 0.029) versus previous 84.2%[^imajev-4b-2026-09-28].
- Hard held-outs: fresh 4,297-decision set (same generators, never mined/trained) 87.2% versus previous 68.4% (in-distribution number); human-verified slice (785 blind-reviewed) 76.2% versus 48.2%; constructed held-out charts 95.7 / documents 90.3 / inventory 67.6 / safety 92.4 / geometry 88.4 / screenshots 95.6% (inventory weakest), all well above the previous release[^imajev-4b-2026-09-28].
- Other suites: DecisionBench full 23,900 rows 79.7% primary at 100% coverage (ECE 0.069; reasoning 80.6%, ordinal 46.2%) versus previous 77.5% at 79.3% scored with 537 unsupported (ECE 0.024) — accuracy-for-calibration trade; Atlan bench-v4 (1,071 rows) 86.6% (88.6% answerable) versus Jev 1.13 92.4% and Haiku 4.5 90.6% with one Civil Comments training row disclosed; LocalLLaMA typed-decisions (2,000) 69.2% (choice 67.8 / yes-no 77.0 / score 64.2, weakest type) with calibrated Brier 0.423 ECE 0.025; fastino/fast-decisions dev 60.4% macro; irrelevance panel 80.0%; state/pairs probes 76.5%/96.7%; S1-Bench typed derivative 99.1% (saturated no-regression check); MMLU-1000 text-only 74.5% versus with unrelated photo 72.9% (earlier versions, not re-run)[^imajev-4b-2026-09-28].
- Unknown-gold regression: 11/14 with 0.48% false abstention versus previous 14/14 with 0.24%; this version answers 3 borderline can't-tell items (confidences 0.83/0.60/0.51) and the prior 14/14 ship gate was overridden for this release[^imajev-4b-2026-09-28].

## Calibration — reported

- One temperature 1.305 for every question-type × option-count bucket, fitted by NLL on 150 template-generated JevBench-style items (none from JevBench); `calibration-rot4.json` is the same fit for 4-rotation mode; per-type fit on flagged held-out half tried and rejected (lowers hard-tier ECE but raises pooled ECE over all 231 public JevBench items); scaling changes probabilities only, `unknown` offsets 0[^imajev-4b-2026-09-28].
- Measured ECE through the eval server: JevBench hard single-pass 0.113→0.082, 4-rotation 0.079→0.082, pooled 231 items 0.064→0.046; off-distribution rows measured on the previous version with its own temperature and not re-run (MMLU-1000 0.150→0.035, typed-decisions 0.149→0.047, SST-5 0.220→0.020, photo-only ABO+VizWiz 823 rows 0.038→0.062 over-softened) — serve photo-against-record traffic without `--calibration` or fit a held-out temperature[^imajev-4b-2026-09-28].

## Automation rule — reported

- On 279 ImajevBench test questions (21 honest can't-tell), raw probabilities with the benchmark's rule: ≥80% automates 63% at 94.9% right; ≥90% automates 58% at 97.5% right; ≥99% automates 40% at 100%; rest to a person; other sizes at 90%: 2B 38% at 95.3%, 9B 70% at 91.8%; benchmark is built hard, so measure a few hundred own cases before choosing a threshold[^imajev-4b-2026-09-28].

## Limits

- Single-pass no-reasoning inference trails reasoning models on multi-step arithmetic and answer-quality judging; phase-3 moved own hard held-outs 19–28 points but left JevBench hard within noise (±3.7 on 111 items)[^imajev-4b-2026-09-28].
- Over-confident without `calibration.json`; slightly less conservative on borderline can't-tell (see unknown-gold regression above)[^imajev-4b-2026-09-28].
- Weakest visual tasks are two-image comparisons (41.8% on real pairs, earlier 4B) and shelf-inventory counts (67.6% constructed); English only; 2B/9B tiers remain previous generation[^imajev-4b-2026-09-28].
- Paired cluster test versus previous release on ImajevBench (89 clusters) pending; previous release beat its base +11.8 [+5.8,+18.0], p=0.0006; official JevBench board adds 308 sealed items plus four-axis scoring[^imajev-4b-2026-09-28].

## Relationships

- Implements the typed-decision contract in [Jev API Patterns](jev-api-patterns.md) with Jev shapes plus `images`, `unknown_probability`, and `abstained`, and 0–2-image / 32 KB-state / 4,096-token limits.
- Uses [Classifier Calibration](classifier-calibration.md) single temperature 1.305 with stated ECE deltas and photo-traffic no-calibration guidance.
- Informs [Classifier Selection](classifier-selection.md) as an Apache-2.0 local photo-plus-text option and [Jev Decision Model](jev-decision-model.md) as a JevBench/Image-JevBench comparison point against Jev-Omni and NeoHorse-Jev-4B.
- Contrasts with [NeoHorse-Jev-4B Structured Decision Model](neohorse-jev-4b-decision-model.md): both are ~4B self-hosted vision decision models, but Imajev trains photo-vs-record/two-photo decisions with a trained `unknown` while NeoHorse covers single-image single-question with uncalibrated local-statistic confidence.

## Coverage limits

- Static inspection of `../raw/imajev-4b.md` only; no server execution, weight load, or benchmark reproduction, so accuracies, ECE figures, latencies, and cost totals are **reported** while frontmatter, adapter/config numbers, interface shapes, and file pointers are **observed**.
- Leaderboard images (`assets/ranks-*.png`, `proof-*.png`), highlight/request/automation illustrations, and demo photos/videos were covered via alt text and prose tables without pixel-level inspection; linked HF Spaces, GitHub repo, website, technical report, `imajev-bench` dataset, and benchmark boards were not inspected beyond the URLs named in the card.
- Consequential limits persist in prose: single-point 2026-09-26 evaluation with small-sample JevBench hard (111) and unknown-gold (14) panels; in-distribution 4,297 hard-held-out figure; unreproduced off-distribution calibration rows; pending paired cluster test; and time-sensitive `stale_after` 2027-09-28 for release, API, and leaderboard figures.

[^imajev-4b-2026-09-28]: mohit67890, "imajev-4b," model card, canonical local entry `../raw/imajev-4b.md`, upstream `https://huggingface.co/mohit67890/imajev-4b` with code `https://github.com/mohit67890/imajev`, demo `https://huggingface.co/spaces/mohit67890/imajev`, report `https://mohit67890.github.io/imajev/report/`, benchmark `https://huggingface.co/datasets/mohit67890/imajev-bench`. Locators in text: frontmatter (license, base_model, PEFT, image-text-to-text); header tier/demo/board links and leaderboard alt text plus sub-caption; "imajev-4b is the recommended default" line; "What sets it apart" five highlights; "One request, every answer typed" script plus result JSON; "Automate what is clear" threshold table and demo pass counts; "How it was made" stages and teachers; "This adapter" LoRA/readout/files plus tier links; "Technical specification" table, "Training path" table, "Data this size saw" bullets, "Compute" line; "Results (2026-09-26)" table plus evaluation paragraph; "Calibration" temperature paragraph plus ECE table; "Serving" install/serve commands plus latency line; "Training data and provenance" paragraph; "Limits" paragraph.
