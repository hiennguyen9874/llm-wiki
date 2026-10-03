---
type: Concept
title: Bespoke Nimble Open Typed-Decision Recipe
description: Open recipe for a Jev-like single-token typed-decision model on Qwen3.5-9B with contrastive data curation, LoRA recipe, and fitted-temperature calibration.
tags: [jev, decision-models, calibration, fine-tuning, open-weights]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T12:00:00Z }
sources:
  - id: bespoke-nimble-2026-09
    resource: ../raw/nimble.md
    kind: documentation
    title: Bespoke Nimble
---

# Bespoke Nimble Open Typed-Decision Recipe

Synthesis: Bespoke Nimble is an open Jev-inspired recipe that fine-tunes Qwen3.5-9B with LoRA to return flat enum/boolean decisions by scoring one answer token per field, trained on 2,676 contrastive pairs and reporting 90.12% on a narrow 324-example holdout versus 93.21% for Jev 1.13.0 and 66.36% for its base model[^bespoke-nimble-2026-09].

## Identity and position

- Creator and artifact are **reported** as Bespoke Labs, model `bespokelabs/Bespoke-Nimble-9B` with a separate `Bespoke-Nimble-9B-v2` repository, built in one day with rough edges expected[^bespoke-nimble-2026-09].
- Base model is Qwen3.5-9B; capability comes from that base plus curated data for a few specific domains, with better new-domain behavior than the base model **reported** but own-task testing required[^bespoke-nimble-2026-09].
- Explicit non-distillation claim is **reported**: the repository did not distill from Jev; its point is to show data curation, training, and serving and encourage more research[^bespoke-nimble-2026-09].
- Inspiration is **reported** as TypeSafe's Jev System One approach and Bespoke-MiniCheck serving, following a Niels Rogge post on Jev decoding[^bespoke-nimble-2026-09].

## Serving and schema interface

- Input is context text plus a flat schema with no nested fields; each field is an enum with fixed string choices or a boolean[^bespoke-nimble-2026-09].
- Mechanism is **reported** as one decision step with no written reasoning: each allowed answer has a one-token code, the scorer reads model logits for those codes, applies softmax with temperature, and builds typed output in Python with no generated JSON to parse[^bespoke-nimble-2026-09].
- Task mapping covers route-a-request, check-a-condition, apply-a-policy, and rate-an-outcome shapes; for ordered rating scales applications can compute an expected level from the probabilities[^bespoke-nimble-2026-09].
- Scorers: `ParallelScorer` on Mac processes shared context once then scores fields in parallel, while the CUDA scorer scores each field separately with the full prompt; both return typed output plus per-candidate logits and probabilities[^bespoke-nimble-2026-09].
- Field isolation is **reported**: each field is scored separately so one field cannot see another field's answer; application code must check cross-field consistency[^bespoke-nimble-2026-09].
- Limits are **reported**: latest checkpoint allows 1–255 choices per enum field and 8,192 input tokens including schema plus field-naming prompt text, rejecting longer prompts; training used a 2,048-token prompt limit so shorter prompts are better tested[^bespoke-nimble-2026-09].

## Contrastive data curation

- Method is **reported** as contrastive data curation: write two nearly identical examples differing in one focus fact within at most eight words of one sentence, such that the correct label flips while question and policy stay fixed[^bespoke-nimble-2026-09].
- Worked refund example is **reported**: sole-authorization-signer change from Mira to Noah flips authorized from `true` to `false` given an only-Mira-may-authorize rule and two jointly needed evidence sentences[^bespoke-nimble-2026-09].
- Four-step pipeline is **reported**: check decision rules for answer coverage; build the pair with two jointly needed evidence sentences; check both examples with separate model calls plus answer-leak and sentence-ablation checks; make labels by code from checked rules and facts, keeping a pair only when all checks pass and labels differ[^bespoke-nimble-2026-09].
- Ablation rule is **reported**: with either evidence sentence removed the focus fact must become unknown even with all other text present; removal examples are checks only and are not added as training data because missing evidence does not mean false or low score[^bespoke-nimble-2026-09].
- Pair/split discipline is **reported**: both examples of a pair and all examples of one source family stay in the same train or eval split; all model requests, responses, and check results are saved for offline replay[^bespoke-nimble-2026-09].

## Dataset

- Files are **reported** as `data/train.jsonl` with 2,676 original-release training examples and `data/eval.jsonl` with 324 frozen final-evaluation examples, published 2026-09-20 after being omitted by mistake; offline checksum, count, and no-overlap check is `nimble.training.verify_dataset`[^bespoke-nimble-2026-09].
- Subject coverage is **reported** as 10 training categories with six in the holdout: Commerce 242/58, Education 230/70, Home 300/0, Media 256/44, Public services 194/106, Science 300/0, Software 300/0, Supply chain 270/30, Travel 284/16, Workplace 300/0[^bespoke-nimble-2026-09].
- Task-type split is **reported** as Choice 856/146, Noul (Boolean) 888/114, Score 932/64 across train/holdout[^bespoke-nimble-2026-09].
- Label trust limit is **reported**: all labels are synthetic, model-checked, with no person review; separate calls to the same model can repeat the same mistake[^bespoke-nimble-2026-09].

## Finetuning recipe

- Trainer applies LoRA to Qwen3.5-9B optimizing cross-entropy over allowed candidate logits; saved Jev probabilities exist for possible future soft-target distillation but current training uses hard reference labels not derived from Jev[^bespoke-nimble-2026-09].
- Final **reported** settings: LoRA rank 16, learning rate 5e-5, effective batch size 8, seed 17, one epoch, preserving the three-epoch linear schedule used during selection and stopping after the selected epoch; BF16 with 2,048-token prompt limit; tuning on L40S with final fit and eval on H100[^bespoke-nimble-2026-09].
- Adapter checks are **reported** on the CUDA unmerged path only: reloaded adapter gave identical logits and adapter-off matched base-model results; no separate quality test of the merged Mac/Linux weights was run[^bespoke-nimble-2026-09].

## Held-out evaluation

- Headline on the same 324 examples is **reported** as Bespoke-Nimble-9B 292/324 (90.12%) versus Jev 1.13.0 302/324 (93.21%), Qwen3.8-27B 275/324 (84.88%), Qwen3.5-9B 215/324 (66.36%), Qwen3.5-4B 199/324 (61.42%), Qwen3.5-0.8B 147/324 (45.37%), Gemma 3 270M IT 93/324 (28.70%)[^bespoke-nimble-2026-09].
- Margins are **reported** as Nimble +17 labels (+5.25 points) over the untuned 27B and Jev +10 labels (+3.09 points) over Nimble; for rating tasks a match means the most probable level equals the reference level[^bespoke-nimble-2026-09].
- Narrowness caveat is **reported**: 324 examples form 162 closely related pairs from only six source families[^bespoke-nimble-2026-09].
- Precision note is **reported**: untuned models scored candidates in FP32 while Nimble used the checked BF16 output-layer setup; one rerun moved an untuned-9B 50/50 tie from 214 to 215[^bespoke-nimble-2026-09].
- External human-labeled coverage is pointed to the public-benchmarks guide over thirteen public subsets starting with VitaminC, added 2026-09-18; that guide was not inspected here[^bespoke-nimble-2026-09].

## Probability temperature

- Temperature divides logits before softmax; above 1 flattens probabilities without changing answer order or picks, but changes probabilities and any expected level, so retest thresholds[^bespoke-nimble-2026-09].
- Original-release fit is **reported** as T=2.179 for revision `93ec5d6ff1a9cd31d6cc0e0c58d312465d36de7c`, selected by lowest log loss on one 300-example set and kept after log loss fell and Brier did not rise on a second 300-example set from different sources, disjoint from train and the 324 holdout[^bespoke-nimble-2026-09].
- Pre-fit miscalibration is **reported**: at T=1 the picked-answer mean probability was 0.89 but only 73% correct on the second set[^bespoke-nimble-2026-09].
- Second-set (300) **reported** results at T=1 versus 2.179: ECE 0.128→0.066, log loss 0.692→0.555, Brier 0.348→0.295; holdout (324): ECE 0.052→0.054, log loss 0.318→0.259, Brier 0.154→0.144; both temperatures picked correctly on 220/300 and 292/324[^bespoke-nimble-2026-09].
- Metric definitions are **reported**: ten probability bins for ECE, correct=1 versus others=0 summed squared gaps averaged for Brier; 24/300 second-set items have probabilistic references used for log loss/Brier but excluded from ECE[^bespoke-nimble-2026-09].
- Rating regression is **reported**: on the 64 holdout rating questions picked-answer probabilities became underconfident with ECE 0.105→0.177[^bespoke-nimble-2026-09].
- Versioning is **reported**: latest checkpoint uses T=1.0 without a separate fit; v2 auto-uses 2.179078721266035 as a transferred release default needing `temperature=1.0` plus `allow_uncalibrated=True` for raw probabilities; full revision hash is required and short hashes do not match[^bespoke-nimble-2026-09].
- Merge gap is **reported**: temperature was fitted on unmerged CUDA weights while hosted API and Mac/Linux quickstarts use merged weights whose logits can differ slightly, without rechecking temperature on merged weights[^bespoke-nimble-2026-09].

## Observed latency

- Table times are **reported** milliseconds per example from saved per-request timings, one question each, with local scorers running once per example and OpenRouter models generating text at medium reasoning[^bespoke-nimble-2026-09].
- **Reported** medians include Gemma 3 270M IT 21.8, Qwen3.5-0.8B 48.6, Qwen3.5-4B 58.0, Qwen3.5-9B 58.1, Qwen3.8-27B 145.3 on H100 contrastive holdout; Nimble 106.0 on 120 H100 examples and 444.0 on 324 M5 Pro 64GB examples; Jev 1.13.0 246.7 via TypeSafe API; DeepSeek-V4.1-Flash 2896.4 and Qwen3.8 2.4T A95B 2792.3 on 100 general-eval examples[^bespoke-nimble-2026-09].
- Saved per-record times for multi-field parallel savings are **reported** as not from a controlled serving test, with one field per saved record[^bespoke-nimble-2026-09].

## What it cannot do

- Text-only input; the base vision part is not usable for judging images[^bespoke-nimble-2026-09].
- No free text, explanations, nested JSON, or extracted spans — only supplied answers[^bespoke-nimble-2026-09].
- Probabilities sum to 1 over supplied answers and do not guarantee correctness; a 0.9 does not mean 90% right on new data, add a no-match answer when none may fit, and test thresholds on own data[^bespoke-nimble-2026-09].

## Local use and versioning

- Requirements are **reported** as Python 3.12, Apple Silicon with native macOS Python plus Metal for Mac or BF16-capable NVIDIA GPU for Linux; unquantized 9B weights take about 18 GB plus runtime overhead, with CPU merge needing extra RAM and disk for base plus merged weights[^bespoke-nimble-2026-09].
- Preparation downloads the checkpoint or LoRA adapter, validates any `schema_config.json` contract, merges adapters against the pinned base once, and records revision plus model path in `.cache/nimble-model.json`; no TypeSafe or generation API key is needed for local inference[^bespoke-nimble-2026-09].
- MLX versus CUDA loading is **reported** as `ParallelScorer` versus `CudaCandidateScorer` from the same config file; bare `ParallelScorer()` loads a Qwen3.5-4B baseline rather than Nimble, MLX cannot load LoRA folders directly or quantized weights, and CUDA also supports unmerged-adapter eval[^bespoke-nimble-2026-09].
- Updates are **reported** as 2026-09-18 public benchmark suite, 2026-09-19 hosted-API 8,192-token per-question limit, 2026-09-20 dataset publication, 2026-09-22 temperature fit, and 2026-09-24 latest checkpoint with 8,192-token context, up to 255 choices, default T=1.0, original release under `original-2676` tag[^bespoke-nimble-2026-09].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) Choice/Noul/Score semantics via flat enum/boolean fields and one-token codes.
- Uses [Classifier Calibration](classifier-calibration.md) temperature scaling with a fitted 2.179 original versus uncalibrated T=1.0 latest.
- Informs [Classifier Selection](classifier-selection.md) open-recipe versus narrow-eval tradeoff.
- Contrasts with [Jev Decision Model](jev-decision-model.md) proprietary Jev on the same 324-example holdout.

## Coverage limits

- Single-file static inspection of `../raw/nimble.md`; linked `docs/`, `data/*.jsonl`, `assets/`, `requirements/`, `tests/`, and `examples/` contents, public-benchmark results, videos, and Hub revisions were not inspected.
- All benchmark, calibration, and latency figures are **reported** source values, not reproduced here; no model was executed.
- Dataset checksums, merged-weight quality, and merged-weight temperature behavior are unreproduced.
- Update and availability notes are time-sensitive; verify Hub revision and docs before building.

[^bespoke-nimble-2026-09]: Bespoke Labs, "Bespoke Nimble," canonical local entry `../raw/nimble.md`, repo `https://github.com/bespokelabsai/nimble`, model `https://huggingface.co/bespokelabs/Bespoke-Nimble-9B`. Locators in text: Updates (2026-09-18–24); Capabilities (schema, scorer, limits); Quickstart (download, MLX, CUDA, typed decision); Methodology (serving, contrastive curation, dataset tables, finetuning, 324-example eval, temperature, latency); Documentation and development (guides, folder layout).
