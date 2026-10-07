---
license: apache-2.0
license_link: https://ai.google.dev/gemma/docs/gemma_4_license
base_model: autotrust/GEV-26B-Decide
base_model_relation: quantized
language:
  - en
library_name: transformers
pipeline_tag: text-classification
tags:
  - system-one
  - system-two
  - adaptive-thinking
  - typed-decisions
  - decision-model
  - calibrated-probabilities
  - jev
  - noul
  - choice
  - score
  - lora
  - gemma4
  - mixture-of-experts
  - multimodal
  - vllm
  - nvfp4
  - modelopt
  - fp4
model-index:
  - name: autotrust/GEV-26B-Decide-NVFP4
    results:
      - task:
          type: text-classification
          name: Jev Decision Index 0.2.1 with adaptive thinking (own scoring; Knowledge & Reasoning adaptive, other areas System 1)
        dataset:
          type: decision-index
          name: Decision Index suite 0.2 (edition 0.2.1)
        metrics:
          - type: decision_index
            name: Decision Index (balanced skill), bf16 GEV-26B-Decide
            value: 62.48
---

# autotrust/GEV-26B-Decide-NVFP4

### [autotrust/GEV-26B-Decide](https://huggingface.co/autotrust/GEV-26B-Decide) with NVFP4 routed experts: the same model in 17 GB of GPU memory instead of 50 GB

## NVFP4 version

This repository is **autotrust/GEV-26B-Decide with its 3,840 routed expert MLPs (30 layers × 128 experts) quantized
to NVFP4**. Everything else is the bf16 model unchanged: attention, the dense MLP of every layer, the routers, the
vision tower, the lm_head, the System 1 adapter, the decision head and the temperatures. The rest of this card is the
card of GEV-26B-Decide; its benchmark tables are the bf16 results, and the NVFP4 comparison is below.

| | GEV-26B-Decide (bf16) | **GEV-26B-Decide-NVFP4** |
|---|---:|---:|
| download (weights) | 49.5 GB | **18 GB** |
| GPU memory for the weights (vLLM) | 51.1 GiB | **17.1 GiB** (−66 %) |
| GPQA Diamond, System 1 (198 questions) | 43.9 % | 44.9 % |
| HLE text multiple choice, System 1 (513 questions) | 8.4 % | 9.7 % |

GPQA Diamond and HLE are the Decision Index items; the bf16 row is the model's `transformers` engine, the NVFP4 row is
vLLM with this checkpoint. The differences are within run-to-run noise (198 questions: about ±7 points).

**What is quantized and how.** NVFP4 is NVIDIA's 4-bit floating-point format: FP4 E2M1 values in groups of 16 with an
FP8 E4M3 scale per group and an FP32 scale per tensor. Per expert, gate, up and down projections are quantized (gate
and up share one tensor scale, as vLLM fuses them); activations of the experts use static scales calibrated on 3,072
System 1 prompts from GEV's own calibration splits. The checkpoint uses the ModelOpt NVFP4 layout and the same
exclusion list as `nvidia/Gemma-4-26B-A4B-NVFP4` (`quant_method: modelopt`), so vLLM loads it without any flag.

**Why only the experts.** The routed experts hold most of the weights (about 22 GB of FP4-able bf16 in 24 B parameters),
and the System 1 adapter does not touch them, so `adapter_vllm/` is the same as for the bf16 model and System 1 needs no
retraining. Attention, the dense MLP and the router carry the LoRA or are small; quantizing them saves little memory.

### Deploy the NVFP4 version (vLLM)

```bash
hf download autotrust/GEV-26B-Decide-NVFP4 --local-dir GEV-26B-Decide-NVFP4
MODEL_DIR=GEV-26B-Decide-NVFP4 bash GEV-26B-Decide-NVFP4/serve.sh     # vLLM on :8000
```

`serve.sh` and the API are exactly those of GEV-26B-Decide (see [Quick start](#quick-start-vllm)); vLLM reads the
quantization from `config.json` / `hf_quant_config.json` and logs `modelopt_fp4` and the selected NVFP4 MoE kernel.

| GPU | how NVFP4 runs |
|---|---|
| B200 / B300 / GB200 (SM100) | native W4A4: FlashInfer TRT-LLM NVFP4 MoE kernels (tested, B200) |
| RTX PRO 6000, RTX 5090, DGX Spark (SM12x) | native W4A4: CUTLASS / FlashInfer CUTLASS FP4 MoE kernels (not tested here) |
| H100 / H200 / A100 (SM80–90) | Marlin W4A16: weights in FP4, activations bf16 (not tested here) |

* **Memory.** The weights take 17.1 GiB, so the whole model fits on a 24 GB GPU with room left for a short context, and
  on a 32 GB RTX 5090 or a 48 GB card with long contexts and many concurrent requests. Set `--gpu-memory-utilization`
  and `MAX_MODEL_LEN` to fit the card, e.g. `MAX_MODEL_LEN=32768`.
* **Same patch as the bf16 model.** The one-engine setup needs `patches/vllm-gemma4-lm-head-lora.patch` (LoRA on
  Gemma-4's tied `lm_head`); tested with a vLLM development build from September 2026.
* **System 1 prompt.** Gemma-4 reads System 1 prompts after `<bos>`; `serve_decide.py` adds it. If you call
  `/v1/completions` yourself, start the prompt with `<bos>` and pass `top_k: 0` and `top_p: 1.0`.
* **transformers.** The `transformers` + `peft` path below loads bf16 weights; use the bf16 repository
  [autotrust/GEV-26B-Decide](https://huggingface.co/autotrust/GEV-26B-Decide) for it.


## Decision Index

| | Decision Index 0.2.1 (balanced skill) | balanced raw | breadth skill |
|---|---:|---:|---:|
| **autotrust/GEV-26B-Decide, adaptive thinking** | **62.48** | 70.66 | 62.00 |
| TypeSafe Jev 1.13 (board) | 57.91 | — | — |

| area (skill) | Knowledge & Reasoning | Language | Retrieval & Classification | Tools & Automation | Arts & Taste |
|---|---:|---:|---:|---:|---:|
| GEV-26B-Decide, adaptive thinking | **0.602** | 0.636 | 0.679 | 0.697 | 0.415 |

How the score was computed (our scoring with the kit's `score --edition 0.2.1`, not a board entry):

* **Knowledge & Reasoning:** all ten benchmarks with adaptive thinking (per-benchmark table under [Adaptive thinking](#adaptive-thinking)).
* **Other four areas:** System 1 only (thinking off), from the complete System 1 run of these weights (all 150,759
  requests, 0 errors), results in
  [`autotrust/jev-decision-index-results`](https://huggingface.co/datasets/autotrust/jev-decision-index-results)
  (`runs/jev-gemma4-26b-a4b`, the weights' previous name). Thinking was tried on five of their benchmarks and is not used
  there: it adds little to classification, retrieval and tool selection (see
  [Outside Knowledge & Reasoning](#outside-knowledge--reasoning)).
* The board requires a median latency of at most 1,000 ms per request, measured on an RTX PRO 6000. System 1 answers in
  about 45 ms on a B200; adaptive thinking is far slower on the Knowledge & Reasoning benchmarks (see
  [Latency](#latency)).

Details: `reports/decision_index_adaptive.json`, `reports/adaptive_latency_summary.json`.

## New (3 October 2026): computer use and robot arm, 60–85 ms per step

The fastest vision model of the family. Every step below is **one System 1 decision** (thinking off): a screenshot or a
camera image in, a probability for every action out, in a single forward pass on one B200.

**Computer use: screenshot → which element to click.** A real browser (headless Chromium). Every clickable element gets a
numbered box; System 1 picks the next click (or "the task is complete"), the browser clicks it, and the loop repeats.

<video src="https://huggingface.co/autotrust/GEV-26B-Decide/resolve/main/videos/computer_use_shop.mp4" controls autoplay loop muted playsinline width="100%"></video>

**95% of 60 random multi-step tasks completed** (shop, settings, mail; 3–7 clicks each) in **about 85 ms per click**:
the same success rate as JEV-27B-VL, 3× faster. The colour swatches carry no text, so that click is decided from the
screenshot alone.

**Robot arm: pick and place from a camera image.** At every step System 1 looks at the top camera image and answers two
questions: is the target left or right of the gripper, and above or below it? The arm moves accordingly and halves its
step whenever an answer flips. It grasps the cube, carries it and drops it in the tray (MuJoCo simulation).

<video src="https://huggingface.co/autotrust/GEV-26B-Decide/resolve/main/videos/robot_arm_pick_place.mp4" controls autoplay loop muted playsinline width="100%"></video>

61 ms per decision, so a whole pick and place takes 4–8 seconds of model time. It completed 40% of 20 random scenes:
close to the target its left/right answers are less precise than JEV-27B-VL's, so more grasps miss. Once grasped, 8 of 9
cubes ended in the tray.

Same scenes and tasks for every model in the family:

| | **GEV-26B-Decide** | [JEV-27B-VL](https://huggingface.co/autotrust/JEV-27B-VL) | [JEV-9B](https://huggingface.co/autotrust/JEV-9B) |
|---|---:|---:|---:|
| computer use: numbered boxes + element text (60 tasks) | 95% | 95% | 95% |
| time per click | **≈ 85 ms** | ≈ 260 ms | ≈ 200 ms |
| robot arm: pick and place (20 scenes) | 40% | **75%** | 50% |
| time per robot-arm decision | **61 ms** | 239 ms | 163 ms |

* For computer use, give it the element text (as an accessibility tree would). With the numbered boxes alone it
  completes 15% and often declares the task complete too early.
* Use System 1 for simple visual questions inside a control loop. Asked to pick one of 8 motor commands directly, it
  completed 0 of 10 scenes.

Demo code: [JEV-9B `vl/demos/`](https://huggingface.co/autotrust/JEV-9B/tree/main/vl/demos) (set `JEV_URL` to this
server). Per-episode results: [`reports/demos/`](reports/demos).

## Overview

**GEV-26B-Decide answers typed questions with a calibrated probability for every option; with thinking switched on, it
thinks only when it needs to.** System 1 decides in one forward pass (about 45 ms). When its leading option is uncertain, System 2 (the same
backbone in Gemma-4 thinking mode) reasons over the question, and the reasoning is folded into the final probabilities.
One set of weights, one vLLM engine, for text and images.

| | what it does | output |
|---|---|---|
| **System 1** | typed decisions: yes/no · pick one of 2–256 options · rate 0–5, over text and images; prompts up to 256K tokens | a calibrated probability for every option, in one forward pass |
| **Adaptive thinking** (opt-in: `thinking: "auto"`) | System 1 first; below 0.8 confidence, System 2 thinks and its answer is folded in | calibrated probabilities |
| **System 2** | the unmodified `google/gemma-4-26B-A4B-it`, optionally thinking step by step, text and images | text / reasoning |

GEV-26B-Decide was previously published as `autotrust/JEV-Gemma4-26B-A4B`; the weights are the same.

> **Two models, two organisations.** **TypeSafe Jev 1.13** is the hosted, closed model made by TypeSafe AI.
> **autotrust/GEV-26B-Decide** is an independent open-weights model built by AutoTrust AI; it is not affiliated with,
> endorsed by, or a product of TypeSafe AI.

## Watch it think

Each puzzle has one correct answer. System 1 answers in one pass; with `thinking: "auto"`, System 2 thinks when System 1
is below 0.8 confidence, and its answer is folded into the probabilities. The videos show puzzles that System 1 got wrong;
the tables below count all puzzles.

**Minesweeper.** Which hidden cell is certainly safe? System 1 is at chance (21.0 % against 25 %); with thinking, 86.0 %.
These thoughts usually reach the 8,192-token budget, and the answer read at that point is still right most of the time.

<video src="https://huggingface.co/autotrust/GEV-26B-Decide/resolve/main/videos/think_minesweeper.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Connect Four.** Which column wins now, or stops the opponent from winning next move? 54.0 % → 99.5 %.

<video src="https://huggingface.co/autotrust/GEV-26B-Decide/resolve/main/videos/think_connect4.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Wordle.** Which word still fits all the colour feedback? 52.0 % → 100 %.

<video src="https://huggingface.co/autotrust/GEV-26B-Decide/resolve/main/videos/think_wordle.mp4" controls autoplay loop muted playsinline width="100%"></video>

**Sudoku.** Which digit belongs in the highlighted cell? 76.0 % → 99.5 %.

<video src="https://huggingface.co/autotrust/GEV-26B-Decide/resolve/main/videos/think_sudoku.mp4" controls autoplay loop muted playsinline width="100%"></video>

One-move puzzles, 200 generated puzzles per game (threshold 0.8, budget 8,192 thinking tokens; text input, chess with the
board image as well):

| game | question (options) | chance | System 1 | **adaptive** | puzzles that thought |
|---|---|---:|---:|---:|---:|
| Minesweeper | which hidden cell is certainly safe (1 safe cell, 3 mines) | 25.0 | 21.0 | **86.0** | 100 % |
| Wordle | which word fits all the feedback (8 words) | 12.5 | 52.0 | **100.0** | 98 % |
| Connect Four | which column wins now or blocks (legal columns) | 14.5 | 54.0 | **99.5** | 95 % |
| Sudoku | which digit goes in the cell (1–9) | 11.1 | 76.0 | **99.5** | 92 % |
| 24 game | which expression equals 24 (6 expressions) | 16.7 | 89.0 | **100.0** | 74 % |
| Maze | first step towards the exit (2–4 directions) | 48.4 | 48.5 | **68.0** | 82 % |
| Chess (Lichess puzzles) | which move mates in one (16 moves, board image + FEN) | 6.3 | 46.5 | **78.0** | — |

Whole games and perception, where thinking helps little or not at all:

| check | System 1 | adaptive |
|---|---|---|
| Snake, one game (image + positions) | 3 food in 18 steps | 11 food in 90 steps (about 21 s per step) |
| Connect Four, 6 full games against a heuristic opponent | 1 win, 5 losses | 1 win, 4 losses, 1 draw |
| 2048, one game | 1,476 points | 1,016 points |
| Flappy Bird, one game | 0 pipes (23 frames) | 0 pipes (38 frames, about 35 s per frame) |
| Quick, Draw!, 320 real sketches, 16 answers (30 / 60 / 100 % of the strokes) | 46.9 / 73.1 / 94.4 % | 40.3 / 72.8 / 95.0 % |

Thinking pays off when the answer can be checked step by step against explicit rules: logic puzzles, tactics,
constraints, arithmetic. It does not help perception (sketches), reflexes (Flappy Bird) or long-horizon play (2048, full
Connect Four games), and every thought costs seconds. Details: `reports/thinking_games.json`.

## Adaptive thinking

1. **Fast distribution.** System 1 returns p1 in one pass.
2. **Think only when uncertain.** If the leading option of p1 is below the threshold (default 0.8), System 2 reasons in
   Gemma-4's thinking mode over the same state, question and options. The reasoning length is yours to set, as with the
   base model: `think_budget` caps the thinking tokens (default: no cap beyond the context window; the evaluations below
   used 8,192).
3. **Fold the reasoning in.** When the thinking channel closes, the answer-letter distribution p2 is read in one step,
   and the result is p = ½ p1 + ½ p2. On its own, p2 is close to one-hot and over-confident; the equal mix keeps the
   reasoning's accuracy and System 1's calibration.

The threshold and the mix were chosen on 1,754 questions from six public sets that are not part of the Decision Index
(test or validation splits, 300 random questions each; AQuA-RAT has 254):

| set | System 1 | **adaptive** | thinking on | always think |
|---|---:|---:|---:|---:|
| AQuA-RAT (math word problems) | 68.1 | **89.0** | 53.9 % | 90.2 |
| LogiQA (logical reasoning) | 55.3 | **80.3** | 63.7 % | 82.0 |
| StrategyQA (multi-hop yes/no) | 68.0 | **78.7** | 71.0 % | 79.0 |
| MedMCQA (medical) | 66.7 | **71.7** | 52.3 % | 73.7 |
| OpenBookQA (science) | 94.3 | **96.3** | 14.7 % | 95.7 |
| CommonsenseQA | 86.7 | **85.0** | 32.0 % | 83.3 |
| **all 1,754** | 73.3 | **83.4** | 47.8 % | 83.8 |

Accuracy in %. Calibration is unchanged: ECE 0.035 for System 1 and 0.035 for adaptive. The adaptive mode reaches 96 % of
the always-think gain while thinking on 48 % of the questions. Thinking length: median 2,282 tokens, 90th percentile 7,573;
91.6 % of the thoughts finish within the 8,192-token budget.

### Decision Index, Knowledge & Reasoning

All ten benchmarks of the area (33,856 scored requests) ran through the server (`POST /v1/decide`, `thinking: "auto"`,
threshold 0.8, budget 8,192 thinking tokens) and were scored with the Decision Index kit:

| benchmark | chance | System 1 | **adaptive** | DI skill, System 1 → adaptive | questions that thought |
|---|---:|---:|---:|---:|---:|
| GPQA Diamond | 25.0 | 42.9 | **78.6** | 0.238 → **0.714** | 87 % |
| CRUXEval | 37.0 | 67.5 | **90.7** | 0.485 → **0.853** | 42 % |
| CLadder | 50.0 | 71.0 | **86.6** | 0.420 → **0.732** | 51 % |
| GSM8K | 25.0 | 97.6 | **99.1** | 0.969 → 0.989 | 5 % |
| SATA-Bench (case exact) | 1.3 | 34.2 | 35.5 | 0.334 → 0.346 | 21 % |
| MuSR | 37.1 | 67.3 | 67.6 | 0.480 → 0.484 | 51 % |
| ChessBench | 8.2 | 23.7 | 23.6 | 0.169 → 0.168 | 88 % |
| HLE | 16.4 | 8.4 | 17.8 | 0.000 → 0.016 | 88 % |
| MMLU-Pro | 11.1 | 65.0 | **84.6** | 0.607 → **0.827** | 78 % |
| BBH | 31.0 | 75.0 | **92.0** | 0.638 → **0.884** | 60 % |

Accuracy in %; "chance" is the kit's random baseline, and the Decision Index skill rescales accuracy so that chance is
0 (below chance counts as 0). The Knowledge & Reasoning area skill rises from 0.429 to **0.602**.

* **Real gains** on science, code, causal and multi-step reasoning: GPQA Diamond, CRUXEval, CLadder, MMLU-Pro and BBH.
* **HLE only returns to chance.** System 1 is below chance (8.4 % against 16.4 %), and the questions where it is confident
  enough not to think are almost all wrong (1.6 %). Thinking brings HLE to 17.8 %, the level of guessing, so its skill
  stays near 0.
* **Chess does not benefit.** Two thirds of the ChessBench thoughts hit the 8,192-token budget; the answer read from a
  truncated thought is no better than System 1 (17.0 % against 17.7 % on those questions), while finished thoughts gain
  a little (19.8 % → 22.7 %). Answers read from truncated thoughts are also over-confident, so the equal mix does not
  damp them.

### Outside Knowledge & Reasoning

Adaptive thinking with the same settings on five benchmarks of the other areas (run stopped after these):

| benchmark | metric | System 1 | adaptive | requests that thought |
|---|---|---:|---:|---:|
| BFCL | case exact accuracy | 94.4 | 96.0 | 7 % |
| API-Bank | accuracy | 84.3 | 86.0 | 18 % |
| CLINC150+OOS (5,456 of 5,500) | macro-F1 | 93.3 | 94.4 | 10 % |
| ToolRet | nDCG@10 | 66.8 | 66.9 | 84 % |
| BANKING77 | macro-F1 | 88.0 | 85.0 | 19 % |

Small gains on tool calls and intents, none on retrieval, and a loss on BANKING77, whose training split System 1 was
trained on: the untrained System 2 often overrules a correct System 1 with an over-confident wrong answer. Use thinking
for reasoning questions; keep it off for classification, retrieval and tool routing.

### Latency

Thinking costs time. Over the area's ten benchmarks, 66 % of the requests thought at least once. Thinking length:
median 8,192 tokens (the budget) on GPQA, HLE and ChessBench, about 5,400 on MMLU-Pro, 3,300 on BBH and 900 on GSM8K.
Estimated single-request latency on one idle B200 (System 1 ≈ 45 ms, thinking ≈ 250 tokens per second): about 0.05 s
without thinking and up to about 33 s with an 8,192-token thought; median 13.4 s over the area (90th percentile 33 s).
With speculative decoding (below) thinking runs at about 438 tokens per second: median 7.7 s, 90th percentile 19 s.
Lower `threshold` or `think_budget` to trade accuracy for speed; `thinking: "off"` keeps every decision in one pass.

MMLU-Pro and BBH (except six questions) ran with speculative decoding, which does not change the output distribution.
Six BBH questions with 18 options hit a vLLM error in the speculative-decoding read-out path and were answered by the same
server without speculative decoding; the current `serve_decide.py` reads answers through a path that works with
speculative decoding.

## Images

The checkpoint contains Gemma-4's vision encoder (no audio encoder), so System 1 and System 2 both accept images. The
decision head was trained on text; decisions over images are zero-shot.

| check | result |
|---|---|
| synthetic images: colour (8 options), shape (4), printed number (8), "is there a red object?" (yes/no) | 100 % on each (30 images each) |
| [VL-RewardBench](https://huggingface.co/datasets/MMInstruction/VL-RewardBench), 1,247 pairs, both presentation orders averaged | **78.4 %** overall (general 55.8, hallucination 84.9, reasoning 76.0; macro 72.2) |

For reference, [autotrust/JEV-27B-VL](https://huggingface.co/autotrust/JEV-27B-VL) scores 78.3 % on VL-RewardBench with
the same protocol.

## Context length

The backbone's native context is **262,144 tokens (256K)**. We tested decisions that hinge on a single sentence placed at
a random depth in long real text (concatenated PubMedQA abstracts): a yes/no question and a 16-option question, 10 of
each per length, on one B200 with vLLM, one request at a time.

| prompt length | yes/no correct | 16-option correct | mean probability on the right answer | median latency |
|---|---:|---:|---:|---:|
| 4K | 10/10 | 10/10 | 0.999 | 0.15 s |
| 32K | 10/10 | 10/10 | 0.999 | 1.6 s |
| 64K | 10/10 | 10/10 | 0.999 | 5.0 s |
| 128K | 10/10 | 10/10 | 1.000 | 17.8 s |

Lengths above 128K have not been tested yet.

## Many options

`choice` takes 2–256 options. Up to 16 are read in one pass with the trained labels A–P. More options are read in groups
of at most 16 (in parallel), then a final of 16; every option is read and none is pruned (`strategy: "tournament"`, the
default). Zero-shot intent classification, all options offered at once, 400 test utterances per row:

| test | options | accuracy |
|---|---:|---:|
| MASSIVE (en) | 59 | 91.2 % |
| BANKING77 | 77 | 81.5 % |
| CLINC150 | 150 | 95.5 % |
| CLINC150 utterances among CLINC150 + BANKING77 + MASSIVE intents | 255 | 89.0 % |
| BANKING77 utterances among the same 255 intents | 255 | 75.2 % |

The 255-option sets merge three catalogues with overlapping intents, so part of the drop comes from near-duplicate labels.
A single pass with labels beyond P (`strategy: "single"`) is about 3× faster but less accurate here (CLINC150: 88.5 %
against 95.2 %), so it is not the default. The BANKING77 and CLINC150 training splits are part of the training data (see
below).

## Quick start (vLLM)

```bash
hf download autotrust/GEV-26B-Decide-NVFP4 --local-dir GEV-26B-Decide-NVFP4
MODEL_DIR=GEV-26B-Decide-NVFP4 bash GEV-26B-Decide-NVFP4/serve.sh   # vLLM on :8000; one GPU with 24 GB or more
```

`serve.sh` runs `serve_decide.py`: the standard vLLM OpenAI server (same flags as `vllm serve`) with a `POST /v1/decide`
route. It loads the backbone once: plain requests are System 2, and requests for the LoRA module `jev-decision`
(`adapter_vllm/`: backbone LoRA + the decision head as an `lm_head` LoRA) are System 1. It needs a vLLM build with
Gemma-4 support plus `patches/vllm-gemma4-lm-head-lora.patch` (LoRA on Gemma-4's tied `lm_head`, vocabulary 262,144);
tested with a vLLM development build from September 2026.

### System 1 and adaptive thinking: `POST /v1/decide`

```bash
curl localhost:8000/v1/decide -H 'Content-Type: application/json' -d '{
  "kind": "choice",
  "state": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball.",
  "question": "How much does the ball cost?",
  "options": ["$0.10", "$0.05", "$1.00", "$0.55"],
  "thinking": "auto"}'
```

| field | value |
|---|---|
| `kind` | `noul`: yes/no, probabilities for `["false", "true"]` · `score`: 0–5 · `choice`: your `options` |
| `state` | what the decision is about: a string, a JSON object, or a list mixing text and images `["Photo: ", {"image": "https://… or data:…"}]` |
| `question` | one question about the state |
| `options` | `choice` only: 2–256 strings |
| `thinking` | `"off"` (default: System 1 only), `"auto"` (adaptive), `"on"` (always think); `noul` and `choice`. Switch on `"auto"` for reasoning questions; keep `"off"` for classification, retrieval and tool routing |
| `threshold` | System 1 confidence below which `"auto"` thinks (default 0.8) |
| `think_budget` | maximum thinking tokens; default: no cap beyond the context window |
| `chat_template_kwargs` | passed to the base model's chat template, as in its chat API (Gemma-4 has thinking on/off only, so there is no `reasoning_effort` setting) |
| `strategy` | more than 16 options: `"tournament"` (default), `"single"`, `"permute"` |
| `return_reasoning` / `debug` | include System 2's reasoning / the System 1 and System 2 distributions |

The response has `options`, `probabilities`, `choice`, `choice_index`, `usage` and, when thinking was requested,
`thinking: {"used": true, "think_tokens": …, "think_seconds": …, "finished_within_budget": …}`. `GET /v1/decide/info`
lists the defaults.

```python
import requests

def decide(kind, state, question, options=None, thinking="auto"):
    body = {"kind": kind, "state": state, "question": question, "thinking": thinking, **({"options": options} if options else {})}
    r = requests.post("http://localhost:8000/v1/decide", json=body).json()
    return dict(zip(r["options"], r["probabilities"])), r.get("thinking", {}).get("used")

decide("noul", "John was born on 29 February 1996.", "Was John's 7th birthday celebrated on a 29 February?")
```

### System 2

```python
requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "autotrust/GEV-26B-Decide",
    "messages": [{"role": "user", "content": "In one sentence, what is safety stock?"}],
    "max_tokens": 200, "chat_template_kwargs": {"enable_thinking": False}})
```

### Speed (one B200, vLLM)

* System 1: median 45 ms for a single request; 257 decisions per second with 64 concurrent clients. vLLM matches the
  `transformers` engine below to a mean largest probability difference of 0.015 (300 held-out decisions).
* Adaptive thinking adds nothing when it does not think, and about 1 second per 250 thinking tokens when it does
  (see [Latency](#latency)).

**Faster thinking with speculative decoding.** `MTP=1 bash GEV-26B-Decide/serve.sh` adds Google's 0.9 GB draft model for
this backbone (`--speculative-config '{"model": "google/gemma-4-26B-A4B-it-assistant", "num_speculative_tokens": 4}'`).
On one B200 it speeds up System 2 about 1.8–1.9×: 247 → 438 tokens per second for a single request, 7,072 → 13,505 tokens
per second at 128 concurrent requests (mean acceptance length 3.5–3.7 of 4). System 1 decisions are unchanged, but System 1
throughput at high concurrency drops (257 → 140 decisions per second with 64 clients); use it when you mostly think.
`serve_decide.py` reads answers with the token restriction that works under speculative decoding, which needs
`--max-logprobs 256` (set in `serve.sh`).

If you call `/v1/completions` for System 1 yourself, pass `top_k: 0` and `top_p: 1.0`: the model's generation config sets
`top_k=64` and `top_p=0.95`, which vLLM applies as request defaults and which would truncate the returned probabilities.

## Usage (transformers + peft, System 1)

This path needs the bf16 weights: `snapshot_download("autotrust/GEV-26B-Decide")` (the bf16 repository).

```python
import json, torch
from huggingface_hub import snapshot_download
from peft import PeftModel
from safetensors.torch import load_file
from transformers import AutoTokenizer, Gemma4ForConditionalGeneration

d = snapshot_download("autotrust/GEV-26B-Decide")
tok = AutoTokenizer.from_pretrained(d)
base = Gemma4ForConditionalGeneration.from_pretrained(d, dtype=torch.bfloat16, device_map="cuda")
# System 2: `base` is gemma-4-26B-A4B-it unchanged; use base.generate(...) (text or images).

# System 1: adapter merged in memory + head
m = PeftModel.from_pretrained(base, f"{d}/adapter").merge_and_unload().eval()
backbone = m.model
jc, T = json.load(open(f"{d}/judge_config.json")), json.load(open(f"{d}/calibration.json"))["per_kind"]
head = load_file(f"{d}/head.safetensors"); W, b = head["proj.weight"].cuda(), head["proj.bias"].cuda()

@torch.no_grad()
def decide(kind, state, question, options):
    lines = options if kind != "choice" else [f"{'ABCDEFGHIJKLMNOP'[i]}) {o}" for i, o in enumerate(options)]
    text = f"[kind] {kind}\n[state] {state}\n[question] {question}\n[options]\n" + "\n".join(lines) + "\n[decision]:"
    ids = torch.tensor([[tok.bos_token_id] + tok.encode(text, add_special_tokens=False)], device="cuda")
    h = backbone(input_ids=ids, use_cache=False).last_hidden_state[0, -1].float()
    z = 30.0 * torch.tanh((W @ h + b) / 30.0)
    s, _ = jc["slots"]["ranges"][kind]
    return dict(zip(options, torch.softmax(z[s:s + len(options)] / T[kind], 0).tolist()))

print(decide("noul", "Customer says the parcel arrived damaged and wants their money back.",
             "Is the customer asking for a refund?", ["false", "true"]))
```

This path reads up to 16 options per pass; for more, use the server (or read groups of 16 and a final, as above).

## Engine and read-out

* **Template** `bare-v1`, prefixed with `<bos>`: `[kind] … [state] … [question] … [options] A) … [decision]:`
* **Read-out**: the final-norm hidden state of the last token goes through a linear fp32 head (hidden 2,816 → 24 slots),
  soft-capped at 30 like Gemma's own logits; inactive slots are masked, the logits are divided by the per-kind
  temperature and softmaxed. Nothing is generated.

## Temperatures

| table | noul | choice | score |
|---|---|---|---|
| `calibration.json` (default; used in the Decision Index run) | 1.003 | 1.017 | 0.999 |
| `calibration_gold.json` (calibrated against ground-truth answers) | 1.214 | 1.098 | 1.000 |

Use `calibration_gold.json` when you gate automatic actions on confidence.

## Training data (disclosure)

System 1 was trained on teacher distributions and ground-truth decision data. The ground-truth data includes the public
**training splits** of some datasets whose **test** splits the Decision Index uses (among them BANKING77 and CLINC150);
no test split of any benchmark was used, and suite items were excluded before training. The list has been provided to
the Decision Index maintainers. MMMU / MMMU-Pro are not valid evaluations for this model. The adaptive-thinking settings
were chosen on data outside the Decision Index suite.

## Limitations

* Where the teacher is wrong, System 1 often is too, and it can be confidently wrong: on HLE the questions it answers
  without thinking are 1.6 % correct. Thinking does not help classification or retrieval and can hurt tasks System 1
  was trained on (BANKING77 macro-F1 88.0 → 85.0). Adaptive thinking helps most on science, code, math and logic, does not help on
  chess or expert-level HLE questions, and can slightly lower accuracy on commonsense questions (CommonsenseQA 86.7 → 85.0).
* Thinking is slow on hard inputs: on expert-level and chess questions it often uses the full 8,192-token budget, and
  the adaptive mode does not meet the Decision Index latency limit on the Knowledge & Reasoning benchmarks.
* The Decision Index score above uses adaptive thinking on the Knowledge & Reasoning area and System 1 on the other four
  areas; it is our own scoring, not a board result.
* Weaker than JEV-27B on long structured inputs (e.g. the Decision Index's Home appliance simulator and POP909).
* HLE: below chance with System 1, like every open entry on the board.
* Decisions over images are zero-shot; contexts above 128K tokens are untested.
* The one-engine vLLM setup needs the bundled vLLM patch; `noul` and `score` accept only their canonical options.
* NVFP4: compared with the bf16 model on GPQA Diamond and HLE only (the full Decision Index was run with the bf16 model).
  Adaptive thinking (System 2) runs on the NVFP4 experts too and was not re-evaluated.
* English-centric; not for high-stakes decisions without confidence gating.

## Files

```
model-*.safetensors · config.json · hf_quant_config.json · processor_config.json · tokenizer* · chat_template.jinja · generation_config.json
                          google/gemma-4-26B-A4B-it; routed experts NVFP4 (ModelOpt layout), everything else bf16 unchanged
nvfp4_activation_amax.json  calibrated activation ranges of the experts (per layer)
adapter/                  System 1 LoRA (peft), for the transformers path
head.safetensors          24-slot decision head (fp32): proj.weight [24, 2816], proj.bias [24]
judge_config.json         slot layout, verbalizer ids, softcap, read-out
calibration.json          per-kind temperatures (default)
calibration_gold.json     per-kind temperatures calibrated against ground-truth answers
adapter_vllm/             System 1 for vLLM: backbone LoRA + the head as an lm_head LoRA, plus decision_head.json
serve_decide.py · serve.sh
                          vLLM server with POST /v1/decide (System 1, adaptive thinking) next to the OpenAI endpoints
patches/                  vLLM patch: LoRA on Gemma-4's tied lm_head
reports/                  adaptive thinking: validation summary, Decision Index recomputation, latency summary, other-area sample, games
reports/demos/            computer use and robot arm: per-episode results
videos/                   adaptive-thinking videos (Minesweeper, Connect Four, Wordle, Sudoku); computer use and robot arm
```

## License

Apache-2.0 for the adapter, head and calibration files; base model under the Gemma 4 terms
(<https://ai.google.dev/gemma/docs/gemma_4_license>). Not affiliated with TypeSafe AI.
