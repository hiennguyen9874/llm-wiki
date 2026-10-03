---
type: Concept
title: Jev-Style-0.8B Decision v3 GGUF On-Device Decisions
description: GGUF builds of Jev-Style-0.8B Decision v3 for on-device verdict-readout decisions with long-context budgets, quantized parity, and llama.cpp serving.
tags: [jev-style, decision-models, gguf, on-device, calibration]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T00:00:00Z }
sources:
  - id: jev-style-v3-gguf-2026
    resource: ../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md
    scope: ../raw/Jev-Style-0.8B-Decision-v3-GGUF/
    kind: model-card
    title: Jev-Style-0.8B-Decision-v3-GGUF
---

# Jev-Style-0.8B Decision v3 GGUF On-Device Decisions

Synthesis: Jev-Style v3 0.8B is an independent Apache-2.0 typed-decision fine-tune of Qwen3.5-0.8B with a verdict readout and fitted temperatures, distributed as llama.cpp GGUFs down to 0.53 GB with 240/240 format parity and a slot-logit scorer for long-context on-device use[^jev-style-v3-gguf-2026].

## Identity and lineage

- Package `chaoliangUNSW/Jev-Style-0.8B-Decision-v3-GGUF`; GGUF builds of `chaoliangUNSW/Jev-Style-0.8B-Decision-v3`; third generation after 2B v1 and 2B v2 on Qwen3.5-2B-Base, with no v1/v2 weights reused in v3[^jev-style-v3-gguf-2026].
- Base `Qwen/Qwen3.5-0.8B` revision `2fc06364715b967f1860aea9cf38778875588b17`; text-only `Qwen3_5ForCausalLM` with 24 layers (18 Gated DeltaNet + 6 full attention), hidden 1024, tied embeddings, 752,393,024 parameters; vision tower and multi-token-prediction head removed[^jev-style-v3-gguf-2026].
- **Synthesis**: unlike JEV-9B/27B distillations of Jev labels, this source explicitly states no Jev weights, code or outputs are included and "Jev-Style" only describes the model kind; question types follow the Laya typed-decision convention so both can be evaluated on the same inputs, with no Laya code or weights included[^jev-style-v3-gguf-2026].
- Companion entry points **reported** in README but not inspected here: main model card for training data/protocols, `jevstyle.com`, GitHub `jev-style` systemone-compatible API with Playground, six agent skills, guard hook and MCP tools, plus `jev-style` pip package and Hugging Face collection/demo Space[^jev-style-v3-gguf-2026].

## Readout, budgets, and calibration

- Template `macjev-render-v1`: `State`, typed `Question`, `Options`, then `Judge each option` with one ` ->` verdict slot per option; segments are encoded separately and concatenated; user text is tokenized with special tokens disabled[^jev-style-v3-gguf-2026].
- Verdict readout `macjev-readout-v1`: per-option score is `logit(" yes") - logit(" no")` at its ` ->` slot, computed from final normed hidden state and tied embedding rows in float32; probabilities are `softmax(scores / T)` with `T` clamped to `[0.3, 5.0]`[^jev-style-v3-gguf-2026].
- Temperature selection: no `category` (default) uses global `T=0.88...`; `category=...` selects the fitted group for family × question-type × option-bucket, else global; explicit `temperature=...` overrides with `1.0` uncalibrated[^jev-style-v3-gguf-2026].
- Calibration `macjev-temperatures-v1`: 20 groups keyed `family|qtype|option_bucket`, families map category prefixes (`typed_official*`→typed, `general_*`→general, `intent*`→intent, `nli*`→nli, `theme_*`→theme, `mac_*`→mac, `long_*`→long, else global), buckets `2`, `3-5`, `6-10`, `11-20`, `21+`; fitted on 15,655 calibration-pool rows (never test rows) with NLL 0.3775→0.3667 and ECE 0.0329→0.0114, shrinkage `k=100`[^jev-style-v3-gguf-2026].
- Budgets: whole input ≤25,600 tokens, question+options+readout head ≤2,048 tokens, runtime context 32,768 tokens; over-budget raises `InputBudgetError`, nothing truncated; long option lists exceeding the head budget are scored in contiguous token-balanced chunks (fewest chunks) with one softmax over all options, added 2026-09-26 and **reported** bit-identical on a 476-request in-budget set[^jev-style-v3-gguf-2026].

## GGUF files and parity

- Files **observed** via manifest sizes: `F16` 1.52 GB, `Q8_0` 0.81 GB, `Q4_K_M` 0.53 GB; README **reports** all three match PyTorch FP32 top-1 on 240/240 parity rows plus 6/6 long prompts at ~16K/25.6K tokens; those rows test format agreement, not accuracy[^jev-style-v3-gguf-2026].
- G5 parity detail in release config: 240 mixed training-pool rows (22 categories, en 215 / zh 25) vs Torch FP32; GGUF F16 top-1 1.0 dNLL ~2.4e-05 pass, Q8_0 1.0 dNLL ~-3.1e-05 pass, Q4_K_M 1.0 dNLL 0.0062 report-only; gates require ≥0.99 16-bit / ≥0.98 8-bit and |dNLL|≤0.02 with no NaN[^jev-style-v3-gguf-2026].
- Runtime parity **reported** 2026-09-24/25: each runtime in a clean subprocess with `--verify` on 24 fixed rows plus 2 synthetic long states (16,381 and 25,582 tokens); rendered token IDs identical on 244/244 rows; vs same-backend reference max prob diff 0.0; vs Torch FP32 max prob diff ~0.00022 F16, ~0.0027 Q8_0, ~0.032 Q4_K_M with 0 top-1 changes[^jev-style-v3-gguf-2026].
- `decide_many` correctness **reported**: `exact` (default) shares state in whole 1,024-token blocks and is bit-identical to per-question `decide` on 201 pairs per quant plus an independent 128-pair recheck; `batched` reads the whole state once with max prob diff ~0.00044 F16/Q8_0 and ~0.00168 Q4_K_M and 1 answer change on F16/Q8_0, so it is opt-in only[^jev-style-v3-gguf-2026].
- Quantization context: Q4_K_M is ~2.4× smaller than 2B v2 Q4_K_M (1.27 GB); v1/v2 agreement figures (91–99% on 500 held-out decisions) use different fixtures and references, so the source states no agreement gap is claimed[^jev-style-v3-gguf-2026].

## Runtime and serving

- Chat or text generation does not give decisions; decisions require the bundled `jev-score` scorer reading logits only at slot positions[^jev-style-v3-gguf-2026].
- `jev-score` (`jev_score.cpp`) is a JSON-lines libllama process: with a shared prefix it decodes the state once and scores several questions on copies; `decide_many` sends all questions about one state in one request[^jev-style-v3-gguf-2026].
- Build **observed** as static procedure: `sh build_jev_score.sh llama.cpp` against llama.cpp commit `441df11f65ea0b6d0c72965aaf70c8241070ddcb` or later, Metal on macOS and `LLAMA_CMAKE_FLAGS="-DGGML_CUDA=ON"` on Linux/CUDA; Python needs `tokenizers` and `numpy` per `requirements.txt`[^jev-style-v3-gguf-2026].
- Python surface **observed** in script docstrings: `JevStyleDecisionGGUF(".", quant="F16"|"Q8_0"|"Q4_K_M").decide(state, question, options, category)` and `decide_many` with `many_mode="exact"|"batched"` and `split_options` toggle; CLI mirrors the same `--quant`, `--state`, `--question`, `--options`, `--category` plus `--no-split-options`[^jev-style-v3-gguf-2026].

## Reported generalization and speed

- Beyond-training-data points **reported** in README with paired CIs excluding zero for Banking77 and MASSIVE: Banking77 68.2% vs best official Laya 49.2%, MASSIVE 37 held-out languages 65.5% vs 36.1%, tweet_topic zero-shot 75.5% vs 63.2%, JevBench v1.4.1 64.1% vs 58.4% (Laya score inside v3 CI, so point-estimate lead only); also ahead of Laya multilingual in 51/51 languages and +2.6 over Laya typed on the same split[^jev-style-v3-gguf-2026].
- Typed in-domain **reported**: 79.2% on 2,000 typed decisions, +2.6 over Laya typed (paired 95% CI +1.0 to +4.2) and +5.7 over 2B v2; in-domain measures agreement with teacher labels, not held-out generalization[^jev-style-v3-gguf-2026].
- Long-context **reported**: up to 25,600 tokens per call (25× Laya 1,024 default and 25× 2B v2 prompt); 98.3% on 1,280 real 24K-token items with flat accuracy 1K→24K, described as preregistered claim passed[^jev-style-v3-gguf-2026].
- Latency **reported** on Apple M1 Max 64 GB warm p50 idle 2026-09-23 with untrained same-architecture export: up to 4.6× faster than the authors' round-1 MacLaya-4K engine (not an official Laya checkpoint) when 10 questions share one 4K state (1,381 ms vs 6,364 ms batched), and 2.3–2.6 s for 8K-token states; exact-mode speedups 1.04–4.29× and batched 3.79–8.47× depend on shared-token fraction[^jev-style-v3-gguf-2026].

## License and trust limits

- License Apache-2.0; built on Qwen3.5-0.8B Apache-2.0; some training data has restrictive or unclear terms and some rows are OpenAI/Anthropic model outputs — full training-data and licence detail lives on the uninspected main card[^jev-style-v3-gguf-2026].
- Integrity: `manifest.json` hashes every repo file except itself; runtime `--verify` skips docs (`README.md`, `figures/`, `assets/`) and checks every other file; GGUF `general.name` metadata edit left tensor data byte-identical with recorded checks[^jev-style-v3-gguf-2026].
- Not affiliated with TypeSafe AI/Jev, Laya authors, or Qwen team[^jev-style-v3-gguf-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) semantics for choice/score/noul with a different verdict-slot mechanism and option-chunk extension.
- Uses [Classifier Calibration](classifier-calibration.md) group-temperature mechanism for confidence.
- Informs [Classifier Selection](classifier-selection.md) on-device buy-vs-clone choice and [Jev Decision Model](jev-decision-model.md) independent-alternative positioning.

## Coverage limits

- Inspected by static reading: `README.md`, `manifest.json`, `readout_config.json`, `release_config.json`, `requirements.txt`, `NOTICE`, `build_jev_score.sh`, script headers/docstrings, `tokenizer_config.json`, and `figures/*.data.json`; no code execution, weight loading, or benchmark reproduction was performed.
- Excluded with reason: `*.gguf` weight binaries as unreadable binary (sizes/hashes/parity via manifest and configs); `tokenizer/tokenizer.json` as large vendored artifact (hash recorded); `figures/*.png`/`*.svg` as decorative once `*.data.json` was inspected.
- External and unverified here: main model card training data/protocols/licences, Hugging Face collection/demo Space, `jevstyle.com`, GitHub `jev-style` API/skills/hooks/MCP, and pip `jev-style` serving; accuracy/latency figures above are **reported**, not reproduced.
- Contact email in README was redacted from this synthesis per privacy policy.

[^jev-style-v3-gguf-2026]: chaoliangUNSW, “Jev-Style-0.8B-Decision-v3-GGUF,” model package, canonical local entry `../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md`, package scope `../raw/Jev-Style-0.8B-Decision-v3-GGUF/`. Locators in text: header lineage and local-run callout; beyond-training-data table and footnotes; long-document paragraph; “Files” parity table; “Quick start” CLI/Python; `jev-score` mechanics, `decide_many` modes, context budgets and “Long option lists”; “Results and speed” collapse with quantization/latency charts and sub-footnote; “Licence”; `readout_config.json` slot/temperature/family/budget keys; `release_config.json` lineage, architecture, calibration, `g5_parity`, `runtime_parity`, `gguf_metadata_edit`, runtime and `split_options`; `manifest.json` file hashes; `figures/quantization.data.json` and `figures/latency.data.json`; `jev_style_decision_gguf.py` header/docstrings and `jev_score.cpp` header; `build_jev_score.sh`; `NOTICE` derivation and non-affiliation.
