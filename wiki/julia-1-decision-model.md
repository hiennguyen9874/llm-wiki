---
type: Concept
title: Julia 1 Decision Model: 144M Multilingual Typed Decisions and Router Runtime
description: Supersonic Labs Julia 1 turns state plus question plus 2-20 options into choice, noul, or score decisions on a 144.3M mmBERT-small backbone, with reported typed, pilot, and MASSIVE results plus a resident CPU/CUDA and hierarchical routing runtime.
tags: [julia, decision-models, routing, multilingual]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:30:00Z }
sources:
  - id: julia-1-2026-09-24
    resource: ../raw/Julia-1/README.md
    scope: ../raw/Julia-1/
    kind: code
    revision: df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72
    title: Julia 1
---

# Julia 1 Decision Model: 144M Multilingual Typed Decisions and Router Runtime

Synthesis: Julia 1 is an Apache-2.0 144.3M open-weight decision model from Supersonic Labs that scores supplied options for a typed question about a state; it is useful for local classification and routing with explicit candidates, with measured strengths on short pilots and MASSIVE scenario classification and explicit limits on knowledge, reasoning, long option lists, and new domains[^julia-1-2026-09-24].

## Identity and lineage

- First model in the Julia family and first released test of the Supersonic training system; model artifacts are Apache-2.0, training pipeline is not included[^julia-1-2026-09-24].
- Starts from JHU CLSP mmBERT-small, a multilingual ModernBERT encoder; Julia retains that encoder foundation and tokenizer, then adds a decision head trained on decision-format examples[^julia-1-2026-09-24].
- Comparison table in source: mmBERT-small about 140M plus encoder/masked-LM interface versus Julia 1 144.3M including decision components plus `state` + `question` + 2–20 `options` to one selected option; upstream context up to 8,192 tokens versus Julia runtime up to 8,192 combined tokens with historical benchmarks at 1,024[^julia-1-2026-09-24].
- Not a chat or text-generation model and not interchangeable with `AutoModelForMaskedLM`; not a drop-in Transformers text-classification pipeline or generative model[^julia-1-2026-09-24].
- **Observed** in code: `julia/model.py::JuliaDecisionModel` wraps an encoder with a 2-layer Transformer head, per-type embedding, scorer LayerNorm plus linear/GELU/linear head, action head, and per-type temperature buffer; `julia_config.json` fixes `head_layers: 2`, `n_act: 2`, `dropout: 0.1`[^julia-1-2026-09-24].

## Typed interface

- Same named-question interface as Dumont: `predict(state=..., questions=...)` with caller-defined IDs returned unchanged; named labels are an API feature, not a Dumont-exclusive capability[^julia-1-2026-09-24].
- `choice`: mapping of 2–20 IDs to nonempty descriptions, answer is winning ID[^julia-1-2026-09-24].
- `score`: ordered list of 2–20 rubric descriptions, answer is expected zero-based rubric index[^julia-1-2026-09-24].
- `noul`: optional mapping of `false` and `true` to descriptions, omitted criteria use literal false/true; answer is probability of true[^julia-1-2026-09-24].
- Each named answer includes `type` and `probabilities` keyed by caller IDs, zero-based strings, or `false`/`true`; choice and score also include `max_probability`; full softmax probabilities without display rounding, not guaranteed certainty; questions independently scored in a batch[^julia-1-2026-09-24].
- Existing list API remains supported: `predict([{state, question, options, type}])` returns one result per request with `index` and display-formatted `probabilities`; `probabilities=False` returns indices only; `logits(rows)` retains raw scores; legacy `noul` supplies false first and true second; score options must be ordered[^julia-1-2026-09-24].
- Native 2–20 option limit still applies; runtime defaults to 8,192-token combined state/question/options limit; example uses 512-token question-and-options budget with 48-token per-option limit; strict encoding rejects overflow[^julia-1-2026-09-24].
- **Observed** validation in `julia/data.py::validate_row`: options must be 2–20 nonempty rendered descriptions; `noul` must be ordered `[false, true]`; unknown types rejected; teacher logits, when present, must be finite and match option count/order[^julia-1-2026-09-24].
- **Observed** serialization in `julia/data.py::sequence`: `"{type} question: {question}"` head plus per-option `[MASK]`-prefixed chunks, CLS/SEP framing, marker positions scored, qtype IDs choice 0 / score 1 / noul 2; strict mode rejects marker injection, enforces 48-token option and head/state budgets[^julia-1-2026-09-24].

## Resident runtime

- Python 3.11+ required; CPU works with standard PyTorch, no native router build needed; CUDA with `device="cuda"` when PyTorch sees a BF16-capable GPU; `JULIA_CPU_THREADS` sets CPU threads, default 4[^julia-1-2026-09-24].
- Entry `julia/inference.py::load_model` delegates to `julia/router/engine.py::FastEngine`; install with full-repository download including 550.5 MiB checkpoint, then `pip install -e ./Julia-1`; keep model loaded between requests[^julia-1-2026-09-24].
- **Observed** `FastEngine`: bounded LRU token and encoding caches, length-sorted bounded microbatches restored to request order, one NumPy arena with zero-copy CPU views versus two pinned bulk transfers on CUDA, device-side softmax/argmax, optional `torch.compile(dynamic=True)`, file-backed safetensors storage unless `memory_map=False`, marker-only final-layer path on CPU by default[^julia-1-2026-09-24].
- Presentation rule in `julia/probabilities.py::display_probabilities`: winner above 0.95 with every other below 0.045 collapses to 1.0/0.0; otherwise values below 0.01 floor to 0.0 and renormalize; logits and selection stay raw[^julia-1-2026-09-24].
- Native Bend path is optional and experimental: `transformer_backend='bend-dense'` runs all 88 encoder projections in Bend on CPU FP32; `bend` head-only path is not a complete transformer rewrite; reduction order differs from PyTorch so tied choices may select differently; calls share a mutex and workers must use spawned processes, not fork[^julia-1-2026-09-24].
- Larger *choice* sets: `julia/router/router.py::Router` batches groups and reranks survivors until one final group remains, up to 4,096 options; a group retains only its winner when raw softmax exceeds 95% with every other below 4.5%, else retains configured survivor count; final probabilities are conditional on `result.candidates`, never a fabricated global distribution; this can discard the correct candidate and adds model calls[^julia-1-2026-09-24].

## Reported evaluation

- Measured 2026-09-24 with H200 BF16 inference and strict encoding for the checkpoint in the repository; weights SHA-256 `df853bf7...` in `metrics/accuracy-20260924.json` and `provenance.json`[^julia-1-2026-09-24].
- Typed decisions 1,463/2,000 at 73.15% versus supplied 72.70% Jev reference, plus 0.45 pp; breakdown Choice 71.33% 428/600, Noul 80.67% 484/600, Score 68.88% 551/800[^julia-1-2026-09-24].
- Classification pilots: AG News 4 labels 94/100 versus 91/100 reference; DAIR Emotion 6 labels 86/100 versus 48/100 reference; Banking77 72-label pilot 64/100 versus 87/100 reference through a ranking/top-16 shortlist, not a native 72-option call[^julia-1-2026-09-24].
- MASSIVE scenario classification, 18 scenario labels across 52 locales at 2,974 examples per locale, macro accuracy 110,573/154,648 at 71.50%; Portuguese pt-PT 2,565/2,974 at 86.25%; English en-US 2,580/2,974 at 86.75%; measures scenario only, not intent or slot filling[^julia-1-2026-09-24].
- Protocol: `typed-decisions` supplies 400 test cases; classification pilots follow the pinned Jev benchmark protocol using BTZSC; Jev numbers are supplied comparison references, not a new Jev run; pilots cover 100 examples per dataset; abstentions count as incorrect[^julia-1-2026-09-24].
- September 26 CPU FP32 reproduction with torch 2.14.0, transformers 5.0.0, marker-only head disabled gives 426/600 choice, 542/800 score, 483/600 noul; replacing only Boolean descriptions with literal false/true gives 391/600 noul on the same CPU run; historical CUDA BF16 totals remain separate and smaller CPU/GPU differences have not been isolated to a single cause[^julia-1-2026-09-24].
- Reproduction harness `scripts/reproduce_typed.py` verifies published weight hash, downloads pinned test Parquet at revision `c76749ec...` with SHA-256 `4f294f21...`, writes predictions and CPU results for all 400 cases / 2,000 questions; accuracy uses highest-probability option for all three types without rounding expected score index and without fitting a threshold on test data[^julia-1-2026-09-24].
- 8,192-token CPU smoke in `metrics/context-8k-smoke.json` passed with finite logits; 8k task accuracy is not established[^julia-1-2026-09-24].
- `inference-policy.json` records single-model, `max_length` 8,192, `head_length` 512, strict encoding true, `calibration: null`, `replacement_qualified: false`, step 500; context basis is native mmBERT positional limit with long-context task accuracy not established[^julia-1-2026-09-24].

## Limits

- Tradeoff is knowledge and multi-step reasoning: compares supplied answers but cannot be counted on to supply missing facts, solve algebraic equations, or carry long calculation chains; ambiguous wording, unfamiliar domains, and long label lists can cause mistakes[^julia-1-2026-09-24].
- Benchmark results do not establish accuracy for a new domain, every language, or high-stakes use; Banking pilot trails its supplied reference; 100-example pilots are encouraging signals, not guarantees; evaluate exact questions and options before consequential use[^julia-1-2026-09-24].
- FP32 weights occupy 550.5 MiB plus tokenizer and activations; CPU needs no GPU; download actual weights, not Git LFS pointers; keep checkpoint files unchanged while an engine is loaded[^julia-1-2026-09-24].
- Grouped routing can lose the correct answer during narrowing and final probabilities cover final candidates only; each native call still accepts 2–20 options[^julia-1-2026-09-24].
- Root `config.json` is the Hugging Face download-statistics query file, not a Transformers AutoModel manifest; native runtime continues to read `julia_config.json`; Hub counts requests server-side with no Julia telemetry[^julia-1-2026-09-24].
- Separate Julia-1-ONNX repository holds full ONNX export and JavaScript WebGPU adapter with Rust N-API/WebAssembly tokenizer; not inspected here[^julia-1-2026-09-24].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) for choice, noul, and score invocation semantics with a local named-question variant.
- Contrasts with [Jev Decision Model](jev-decision-model.md) as a small open-weight local alternative to a proprietary cloud decision model.
- Uses [Text Classification Lineage](text-classification-lineage.md) encoder plus shared-scorer retrofit pattern.
- Uses [Classifier Calibration](classifier-calibration.md) only as a negative point: no fitted calibration is reported.
- Informs [Classifier Selection](classifier-selection.md) for small local routing and classification testing.

## Contradictions

- None established. `provenance.json` step-500 validation and `metrics/validation.json` step-900 checkpoint record different training checkpoints and task mixes; treat them as separate snapshots, not interchangeable accuracy claims[^julia-1-2026-09-24].

## Coverage limits

- Static inspection only; no model execution, weight loading, or benchmark reproduction was performed here.
- `model.safetensors` weights were absent from `raw/`; weight identity is by reported SHA-256 only.
- `tokenizer/tokenizer.json` in `raw/` is a Git LFS pointer, so token IDs were not inspected.
- Native `router/native/*.bend` and `bridge.c` plus ONNX/WebGPU export were not executed or audited for numeric equivalence.
- `metrics/accuracy-20260924.json`, `metrics/typed-cpu-20260926.json`, `metrics/context-8k-smoke.json`, `metrics/validation.json`, and `provenance.json` were read as structured data without re-running their protocols.
- Image and logo assets under `assets/` were excluded as decorative.

[^julia-1-2026-09-24]: Supersonic Labs, "Julia 1," model package, canonical local entry `../raw/Julia-1/README.md`, package scope `../raw/Julia-1/`, weights SHA-256 `df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72`. Locators: "Evaluation" table and "Protocol" paragraph; "Where Julia is accurate" and "Why a decision model for routing" sections; "From mmBERT-small to Julia 1" table; "Start here" install and named-question plus legacy APIs; "Reproduce typed-decision accuracy" command and dataset revision; "Limits and deployment notes"; `julia/router/README.md` faster path, Bend operations, and larger choice sets; `julia/*.py` and `julia/router/*.py` interfaces; `metrics/accuracy-20260924.json`, `metrics/typed-cpu-20260926.json`, `metrics/context-8k-smoke.json`, `metrics/validation.json`; `provenance.json`, `inference-policy.json`, `julia_config.json`, `encoder/config.json`.
