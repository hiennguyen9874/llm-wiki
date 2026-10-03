---
type: Concept
title: 'SemIf Open Decisions: Direct-Logit Jev-Interface Baseline'
description: No-training open baseline that reads typed option logits from frozen models with shared-state reuse, audited speed/quality fixtures, and per-workload temperature calibration.
tags: [jev, decision-models, open-weights, calibration]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:45:00Z }
sources:
  - id: semif-2026-09-22
    resource: ../raw/SemIf-OpenJev.md
    kind: code
    title: SemIf (formerly OpenJev)
---

# SemIf Open Decisions: Direct-Logit Jev-Interface Baseline

Synthesis: SemIf (formerly OpenJev) is an independent no-training baseline that reproduces the Jev **interface pattern** on frozen open models — runtime criteria plus typed options in, probabilities out — by reading declared option logits in one forward pass with no answer sampling, shared-state prefill reuse, and committed fixtures, revisions, prompts, and failures[^semif-2026-09-22]. **Synthesis**: prefer it when a self-hosted decision baseline must avoid training and stay auditable, accepting frozen-model accuracy limits and single-file capture limits below.

## Mechanism

- **Runtime-defined:** criteria and option descriptions arrive with the request; one forward pass reads declared option logits into probabilities — **reported** no answer sentence, JSON repair, or decoding loop[^semif-2026-09-22].
- **Shared-state aware:** one long state is prefetched once, then branched across many criteria; rows carry typed option scores, timing, exact model revision, and prompt hash (`prompt_sha256`)[^semif-2026-09-22].
- **Input contract:** **observed** `{id, state, question, options: [{id, description}]}` example; `state` may be text or a nonempty JSON object/array; direct modes preserve structured JSON while reranker mode renders state as document text; probabilities are conditional on the supplied options, so calibrate and validate on the deployment workload[^semif-2026-09-22].
- **Backends:** **reported** CUDA Torch (`Qwen/Qwen3.5-4B` at pinned revision `851bf6e8`), Apple Silicon MLX (`--backend mlx`, serial prefix reuse, parallel shared-state) and PyTorch/MPS (`--device mps`), CPU-only llama.cpp GGUF (`--backend llamacpp --gguf`, pinned reference tokenizer so `prompt_sha256` matches Torch row for row, scores conditional on quantized weights), slow full-precision Torch reference (`--device cpu --dtype float32`), Qwen3.8-27B EXL3 bridge, and WebGPU/GGUF browser demo with MiniCPM5-2B and Qwen3.5-4B plus an Unsloppify conventional-interface switch; one loaded backend owns one stateful scoring context[^semif-2026-09-22].
- **Modes:** `semif-score --mode direct` (fresh scoring) versus `--mode shared` (prefill repeated state once, evaluate criteria in parallel) on the owned `examples/decisions.jsonl` shape[^semif-2026-09-22].

## Speed (**reported**, RTX 3090, same frozen Qwen3.5-4B / state / 21 binary criteria unless noted)

- Direct typed logits median-of-3 **1.023 s** for 21 probability pairs with **0** output tokens versus compact autoregressive JSON-array median-of-3 **5.332 s** and 111 tokens (**5.21×**); generative median first-token 0.489 s, all three arrays valid and identical, direct-argmax agreement 18/21 — framed as a systems comparison, not semantic equivalence[^semif-2026-09-22].
- Owned 37-state × 21-criterion (777 decisions) fixture: fresh direct 2.33 decisions/s (333.1 s), serial prefix reuse 10.75 (72.3 s), parallel suffixes **20.03** (38.8 s), native reranker 1.86 (417.3 s); fast reuse paths are experimental — **reported** BF16 execution changed 5–6 of 777 argmaxes versus fresh scoring, and llama.cpp direct versus prefix-cached paths differ slightly, so compare decisions/probabilities with tolerance, not raw-logit bit equality[^semif-2026-09-22].

## Quality (**reported**, native BF16 unless noted)

- Browser ladder (authored / perturbation balanced accuracy, TypeSafe-subset agreement): Qwen3-0.6B Q8_0 0.440 / 0.528 / 0.407; MiniCPM5-2B Q4_K_M 0.686 / 0.693 / 0.637; **Qwen3.5-4B** Q4_K_M **0.813** / **0.766** / 0.845 versus published Jev 0.883 on the same 102-row subset[^semif-2026-09-22].
- General baseline (frozen 4B BF16 direct logits vs 4B reranker): authored 144 rows 0.813 vs 0.625; WANLI 256 rows **0.637** vs 0.522; TypeSafe selected 102 rows across 20 cases **0.845** vs 0.560 (published Jev 0.883); Every judgment grid 36 rows **0.806** vs 0.694; Every action firewall 10 actions 0.700 vs 0.700; Every code retrieval 6 queries 1.000 vs 1.000; Every company knowledge 7 queries 0.929 vs 0.929 — direct logits the better general-decision baseline, reranker still strong at retrieval ranking[^semif-2026-09-22].
- EXL3 bridge (Qwen3.8-27B, 5 bpw): same 144 authored rows with matching prompt hashes, options, readout, and metric, **0.958** vs 4B 0.813; framed as a system-level quality comparison (family, size, quantization, runtime all differ), not a controlled size/quantization ablation; not yet run on other quality workloads; 84.43% choice agreement with the pinned 4B model across the 777-decision shared-state fixture[^semif-2026-09-22].
- Jev comparison boundary: the Jev figure is read from TypeSafe public records on the 102 alignable rows, not a live endpoint run and not the vendor 711-row aggregate; the project reproduces the interface pattern, explicitly not Jev's undisclosed model or training[^semif-2026-09-22].

## Calibration (**reported** per-workload temperature scaling, fitted on labeled decisions)

- Authored: raw ECE 0.068 → calibrated out-of-fold **0.038**, T=1.23; WANLI: 0.208 → **0.069**, T=2.50; Every judgments: 0.050 → 0.047, T=1.71; scaling does not change the selected option, the clear gain is WANLI while authored/Every intervals overlap[^semif-2026-09-22].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) runtime-criteria plus typed-options shape without the hosted endpoint.
- Requires [Classifier Calibration](classifier-calibration.md) per-workload temperatures before depending on confidence.
- Informs [Classifier Selection](classifier-selection.md) no-training clone option versus distilled students.
- Contrasts with [Jev Decision Model](jev-decision-model.md) closed Jev on the aligned 102-row subset.

## Coverage limits

- Single-file capture (`How it works`, `Speed`, `Quality`, `Calibration`, `Input`, `Quick start`, `Documentation`, `Evaluation sources` sections); referenced `docs/`, `examples/`, `benchmarks/`, `results/raw/`, `results/phase1-summary.json`, `exl3-bridge/`, `demo/`, `webgpu-demo/`, and `assets/` artifacts were not included and not inspected — verify commands, fixtures, and reruns against the live repo before depending on them[^semif-2026-09-22].
- All speed, accuracy, agreement, and ECE figures are **reported** project measurements with committed runners/fixtures; no execution, reproduction, or live Jev call was performed here[^semif-2026-09-22].
- Model weights and third-party records are not included; project code is MIT, upstream models retain their licenses[^semif-2026-09-22].

[^semif-2026-09-22]: SemIf project, "SemIf (formerly OpenJev)," independent project formerly called OpenJev with no TypeSafe affiliation or endorsement, canonical local entry `../raw/SemIf-OpenJev.md`, repo `TheoLeeCJ/SemIf` via PR/star-history links, latest changes 2026-09-22 (Apple Silicon MPS, Qwen3.8-27B EXL3 bridge, per-workload calibration) and 2026-09-18 (browser ladder, Unsloppify site), project code MIT with upstream model licenses retained. Locators in file: "How it works" interface diagram and bullets; "Quick start" backends and `semif-score` commands; "Speed" decision-vs-compact-array and 777-reuse tables; "Quality" browser-ladder, general-baseline, and EXL3-bridge tables plus Jev-alignment caveat; "Calibration" ECE/temperature table; "Input" JSON contract; "Documentation" and "Evaluation sources" link lists.
