---
type: Concept
title: Quyet-1.0-Large Calibrated Decision Model
description: Apache-2.0 31B Gemma-based typed-decision model with letter-readout, fitted-temperature calibration, and Jev-compatible Choice/Noul/Score APIs.
tags: [quyet, decision-models, calibration, open-weights]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T12:00:00Z }
stale_after: 2027-10-07
sources:
  - id: quyet-1-0-large-2026
    resource: ../raw/Quyet-1.0-Large.md
    kind: model-card
    title: Quyet-1.0-Large
---

# Quyet-1.0-Large Calibrated Decision Model

Synthesis: Quyet-1.0-Large is Chinh Nguyen's Apache-2.0 31.3B typed-decision fine-tune of Gemma-4-31B-it that answers `choice`, `noul`, and `score` questions from option-letter token probabilities with package-applied calibrated temperatures in TypeSafe `/v1/systemone` shapes; shortlist it when a self-hosted Jev-compatible 80 GB-class model with English plus Vietnamese tuning is acceptable, and verify accuracy and calibration on own data since this card reports no benchmarks or ECE figures[^quyet-1-0-large-2026].

## Identity and family

- Model `chinhnc/Quyet-1.0-Large` by Chinh Nguyen, part of the Quyet 1.0 family (Large, Medium, Small, Small-EN, Tiny), released under Apache-2.0[^quyet-1-0-large-2026].
- Base model is **reported** as `google/gemma-4-31B-it` with `base_model_relation: finetune` in the card frontmatter[^quyet-1-0-large-2026].
- Credits Gemma 4 by Google (Apache-2.0); redistribution must keep the NOTICE file starting with "Quyet by Chinh Nguyen"[^quyet-1-0-large-2026].
- Citation block is provided as `@misc{quyet2026, title = {Quyet 1.0: calibrated decision models}}` with the model Hub URL[^quyet-1-0-large-2026].
- Languages are **reported**: English plus Vietnamese tuning; other languages work with lower accuracy[^quyet-1-0-large-2026].
- Upstream is `https://huggingface.co/chinhnc/Quyet-1.0-Large`; canonical local entry is the single-file card below[^quyet-1-0-large-2026].

## Architecture and readout

- Architecture is **reported** as Gemma-4-31B-it with a merged LoRA fine-tune (rank 16) and a letter-readout decision prompt[^quyet-1-0-large-2026].
- Parameters are **reported** as 31.3B total (30.7B text); weights are **reported** as 62.5 GB in bf16[^quyet-1-0-large-2026].
- Mechanism is **reported**: the model answers by reading the next-token probabilities of the option letters (A, B, ...) after a fixed prompt; the `quyet` package builds that prompt and applies the calibrated temperatures[^quyet-1-0-large-2026].
- Prompt version 2 is **reported**: the trained prompt without the system message and the closing line, with structured states as compact JSON (about 68 fewer input tokens per decision); its temperatures were refit for it[^quyet-1-0-large-2026].
- The checkpoint also loads with transformers and serves with vLLM as a standard gemma-4-31B-it-architecture checkpoint, but the decision prompt and temperatures live in the package and in `quyet_config.json`, not in the bare weights[^quyet-1-0-large-2026].

## APIs and limits

- Question types are `choice` (pick one label), `score` (an ordered scale), and `noul` (true/false)[^quyet-1-0-large-2026].
- Answers follow the TypeSafe `/v1/systemone` shape: `choice` with `probabilities`, `score` with expected level plus `probabilities` plus `legend`, and `noul` as P(true)[^quyet-1-0-large-2026].
- At most 10 options per question[^quyet-1-0-large-2026].
- Input budget is **reported**: state up to 6,000 tokens inside an 8,000-token prompt[^quyet-1-0-large-2026].
- Truncation rule is **reported**: only the state is ever truncated — conversation lists keep their most recent turns, other states keep their beginning[^quyet-1-0-large-2026].
- Usage shape is **reported** via `quyet.load("chinhnc/Quyet-1.0-Large")` plus `m.predict(state, questions)` with per-question `type`, `instructions`, and `criteria` (choice label descriptions, score ordered levels), returning an `answers` map with per-question choice/confidence/probabilities, noul, and score entries[^quyet-1-0-large-2026].

## Calibration

- Calibration is **reported** as fitted temperatures applied by the `quyet` package, with prompt-version-2 temperatures refit and stored in the package plus `quyet_config.json`[^quyet-1-0-large-2026].
- Temperature never changing the winner is not stated in this card; do not assume it without a per-workload check[^quyet-1-0-large-2026].
- No accuracy, ECE, NLL, Brier, latency, or leaderboard figures appear in this card — treat all quality and speed expectations as unmeasured here[^quyet-1-0-large-2026].

## Serving and runtime

- Install and run are **reported**: `pip install quyet`, bf16 on one 80 GB GPU, or several GPUs with `device_map="auto"` via `pip install quyet[multi-gpu]`[^quyet-1-0-large-2026].
- vLLM and transformers paths are **reported** as compatible for the bare checkpoint, with the caveat above that prompt and temperature handling stays in the `quyet` package[^quyet-1-0-large-2026].
- Contact email in the card is redacted from this synthesis per privacy policy[^quyet-1-0-large-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) Choice/Noul/Score semantics via letter readout with a 10-option cap.
- Uses [Classifier Calibration](classifier-calibration.md) package-applied fitted-temperature mechanism.
- Informs [Classifier Selection](classifier-selection.md) self-hosted 31B-class choice with Vietnamese coverage and 80 GB serving needs.

## Coverage limits

- Inspected by static reading of `../raw/Quyet-1.0-Large.md` only; no code execution, weight download, API call, or benchmark reproduction was performed.
- Referenced but uninspected: `LICENSE`, `NOTICE`, `quyet_config.json`, the `quyet` package implementation, sibling Quyet 1.0 checkpoints (Medium, Small, Small-EN, Tiny), and the upstream Hub page; all architecture, language, context, and serving figures above are **reported** card values.
- No evaluation section exists in this source; do not rank Quyet against Jev, Kev, Laya, OpenJev, JEV, Clef, Von, Julia, NeoHorse, Imajev, or Jev-Style variants on accuracy, calibration, or speed without an independent protocol.
- No credentials, keys, tokens, or PII are recorded here; the card's contact address was withheld.

[^quyet-1-0-large-2026]: Chinh Nguyen, "Quyet-1.0-Large," model card, canonical local entry `../raw/Quyet-1.0-Large.md`, upstream `https://huggingface.co/chinhnc/Quyet-1.0-Large`. Locators in text: frontmatter `base_model`/`base_model_relation`/`tags`; title plus family sentence; spec table (Base model, Architecture, Parameters, Languages, Input, Weights, License); "How to use" install plus `quyet.load`/`m.predict` example and answers-shape paragraph; serving paragraph (bf16 one-80 GB-GPU, `device_map="auto"`, transformers/vLLM, prompt version 2 with 68-token saving and refit temperatures, 10-option cap, state-only truncation rule); "Credits", "Citation", and "License" sections.
