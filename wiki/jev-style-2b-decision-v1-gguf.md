---
type: Concept
title: Jev-Style-2B Decision v1 GGUF Letter-Readout Decisions
description: GGUF builds of Jev-Style 2B v1 for letter-readout typed decisions with folded-temperature calibration and llama.cpp serving.
tags: [jev-style, decision-models, gguf, on-device, calibration]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:59:00Z }
sources:
  - id: jev-style-2b-v1-gguf-2026
    resource: ../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md
    scope: ../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/
    kind: model-card
    title: Jev-Style-Qwen3.5-2B-Decision-GGUF
---

# Jev-Style-2B Decision v1 GGUF Letter-Readout Decisions

Synthesis: Jev-Style 2B v1 is an independent Apache-2.0 typed-decision fine-tune of Qwen3.5-2B-Base that returns Choice/Bool/Score decisions from a single option-letter token with the calibration temperature folded into the weights, distributed as 1.3–3.9 GB GGUFs for LM Studio and llama.cpp use[^jev-style-2b-v1-gguf-2026].

## Identity and lineage

- Package `chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-GGUF`; GGUF builds of `Jev-Style-Qwen3.5-2B-Decision` v1 on base `Qwen/Qwen3.5-2B-Base`[^jev-style-2b-v1-gguf-2026].
- Header lineage **reported**: this repository preserves v1; v2 lives at `chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-v2-GGUF`; v3 (`Jev-Style-0.8B-Decision-v3-GGUF`) at 0.8B **reports** 79.2% on 2,000 typed decisions (v1 53.4%, v2 73.5%), 25,600-token inputs, 51 languages, and 77 options without the 26-letter cap[^jev-style-2b-v1-gguf-2026].
- **Synthesis**: unlike JEV-9B/27B distillations of Jev labels, this source explicitly states it is an independent from-scratch reproduction of the publicly described idea with no affiliation to TypeSafe AI and no Jev model inside; "Jev-style" only describes the decision-with-calibrated-probabilities pattern[^jev-style-2b-v1-gguf-2026].
- License Apache-2.0, same as the Qwen base; training rows include AG News distributed for research/non-commercial use[^jev-style-2b-v1-gguf-2026].

## Readout, prompt, and calibration

- Letter readout **observed** in client code and **reported** in README: the prompt ends with `Answer:` and the next token is the option letter (` A`, ` B`, …); probabilities are the letter log-probs renormalised over the declared letters[^jev-style-2b-v1-gguf-2026].
- Prompt template (must be used verbatim; plain chat produces meaningless continuation): `You are a decision function…`, then `[State]`, `[Question]`, `[Options]` as `A. …`, `B. …`, then `Answer:`; **observed** builder emits exactly this shape in `jev_style_client.py::build_prompt`[^jev-style-2b-v1-gguf-2026].
- Choice/Bool/Score mapping: Choice picks one of N declared options; Bool uses `yes`/`no`; Score lists ordered levels and takes the expectation as the continuous score[^jev-style-2b-v1-gguf-2026].
- Option cap: up to 26 options by letter, but only 20 when probabilities are read through a server `top_logprobs` cap; client enforces `MAX_OPTIONS = 20` and assigns off-list letters a floor of `min(top) − 5.0` (**observed** in `decide`) before softmax[^jev-style-2b-v1-gguf-2026].
- Pass-through chat template ships with the repo so `/v1/chat/completions` passes the prompt verbatim; LM Studio does not return candidate log-probs on `/v1/completions`, so the client uses the chat endpoint on both LM Studio and llama-server (**observed** in `_top_logprobs` docstring)[^jev-style-2b-v1-gguf-2026].
- Zero-cost calibration: a temperature fitted on 4,366 held-out examples is folded into the final RMSNorm weight, so every logit is already calibrated with nothing to apply at inference time[^jev-style-2b-v1-gguf-2026].
- Calibration outcome **reported** on 1,500 held-out examples across 5 tasks: ECE 0.017 vs 0.065 for zero-shot base, NLL 0.418 vs 0.786, Brier 0.242 vs 0.446; the README notes 0.017 is statistically indistinguishable from perfect calibration under sampling noise (expected 0.017, 95th percentile 0.025)[^jev-style-2b-v1-gguf-2026].

## GGUF files and reported parity

- Files **reported** with same-decision-as-bf16 and 500-held-out accuracy (table in README "Files" section)[^jev-style-2b-v1-gguf-2026]:

  | File | Size | Same decision as bf16 | Accuracy (500 held-out) |
  |---|---|---|---|
  | `Q4_K_M` | 1.3 GB | 94.4% | 82.4% |
  | `Q8_0` | 2.1 GB | 99.4% | 81.6% |
  | `BF16` | 3.9 GB | 99.8% | 81.6% |

- **Synthesis**: treat "same decision" as format agreement on the same 500 rows, not accuracy; Q4_K_M is the size pick (1.3 GB) at unchanged-or-higher accuracy in this table, while Q8_0 is the fidelity pick at 99.4% agreement[^jev-style-2b-v1-gguf-2026].

## Reported accuracy, transfer, and speed

- 5 decision tasks / 1,500 held-out rows never trained on, probabilities exactly as released weights produce them with no post-processing: accuracy 82.3% vs 65.9% zero-shot base at unchanged latency (77 ms vs 76 ms per decision, M1 Max MLX bf16)[^jev-style-2b-v1-gguf-2026].
- Per-task gains **reported**: MNLI 52.3% → 86.7%, SST-5 32.0% → 61.7%, BoolQ 73.0% → 82.7%, SST-2 87.3% → 92.7%, AG News 84.7% → 87.7%[^jev-style-2b-v1-gguf-2026].
- Transfer **reported**: on unseen types (emotion, RTE) at unchanged 64.5% accuracy, ECE halves 0.155 → 0.075 — better but not perfect calibration off-distribution[^jev-style-2b-v1-gguf-2026].
- End-to-end serving check **reported**: verified through LM Studio server on 500 held-out examples at 81.6% accuracy, ECE 0.028, ~110 ms per decision over HTTP on M1 Max[^jev-style-2b-v1-gguf-2026].
- Training recipe **reported**: LoRA rank 16 on all linear layers with log-score loss, on a custom chunk-parallel differentiable Gated DeltaNet forward matching the per-token path to 1e-6 (outputs, state, all gradients) and 6.5× faster per step — measured on the 0.8B sibling model, not this 2B run[^jev-style-2b-v1-gguf-2026].

## Runtime and serving

- LM Studio: download a file, load it, start the local server (Developer tab), then run the client against `http://localhost:1234`[^jev-style-2b-v1-gguf-2026].
- llama.cpp: `llama-server -hf chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-GGUF:Q8_0 --port 8080`, then the same client against `http://localhost:8080`[^jev-style-2b-v1-gguf-2026].
- Client surface **observed** (standard library only): `decide(url, state, question, options)`, `decide_bool(url, state, proposition)`, `decide_score(url, state, question, levels)`; one token requested with `top_logprobs: 20`, `temperature: 0`, then renormalisation — no temperature post-processing because it is baked into the weights[^jev-style-2b-v1-gguf-2026].

## Scope, training data, and limits

- A decision function, not a chat model: start a new chat per decision and paste the full prompt ending in `Answer:`; in the chat window the model replies with the option letter[^jev-style-2b-v1-gguf-2026].
- Trained on five English families (sentiment, NLI, topic, yes/no QA, 5-level rating) from SST-2, MNLI (GLUE), AG News, BoolQ, SST-5: 22k examples converted to typed decisions, 80% LoRA training / 20% held out for the temperature[^jev-style-2b-v1-gguf-2026].
- Companion entry points **reported** but not inspected here: `jevstyle.com`, MLX bf16 repo for Apple Silicon, v2 GGUF repo, and v3 0.8B repo[^jev-style-2b-v1-gguf-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) Choice/Bool/Score semantics via a simpler single-letter readout (vs the v3 verdict-slot mechanism).
- Uses [Classifier Calibration](classifier-calibration.md) folded-temperature mechanism for confidence.
- Informs [Classifier Selection](classifier-selection.md) on-device buy-vs-clone choice and [Jev Decision Model](jev-decision-model.md) independent-alternative positioning.
- Precedes [Jev-Style-0.8B Decision v3 GGUF](jev-style-0.8b-decision-v3-gguf.md), which **reports** higher typed accuracy at 0.8B with longer contexts and no 26-letter cap.

## Coverage limits

- Inspected by static reading: `README.md` and `jev_style_client.py` (prompt builder, `top_logprobs` path, renormalisation, `MAX_OPTIONS`, CLI); no code execution, weight loading, or benchmark reproduction was performed.
- Excluded with reason: `*.gguf` weight binaries as unreadable binary (sizes/parity/accuracy via README table only); `calibration.png` reliability diagram as decorative once the ECE/NLL/Brier table was captured.
- External and unverified here: `jevstyle.com` site, MLX bf16 repo, v2 and v3 repos, and main training-data card; all accuracy/latency/calibration figures above are **reported**, not reproduced.
- Contact email in README was redacted from this synthesis per privacy policy.

[^jev-style-2b-v1-gguf-2026]: chaoliangUNSW, "Jev-Style-Qwen3.5-2B-Decision-GGUF," model package, canonical local entry `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md`, package scope `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/`. Locators in text: header v3/v2 lineage callout and frontmatter `base_model`/`license`; "Results" held-out table and bullets; "What `Jev-style` means" Choice/Bool/Score list; "Quick start" LM Studio/llama.cpp commands and `jev_style_client.py` usage; "Prompt format" template; "Scope" decision-function limits; "Training data and licence" 22k/80-20/AG News note; "Files" GGUF table; `jev_style_client.py::build_prompt/_top_logprobs/decide/decide_bool/decide_score/MAX_OPTIONS`.
