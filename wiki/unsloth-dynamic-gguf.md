---
type: Concept
title: Unsloth Dynamic GGUF Quantization
description: Post-training GGUF quantization family with per-layer dynamic schemes, chat-oriented imatrix calibration, and versioned v2.0/v3.0 quality-size tradeoffs.
tags: [unsloth, quantization, gguf, ptq, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:44:15Z }
sources:
  - id: dynamic-ggufs
    resource: ../raw/unsloth/basics/dynamic-3.0-ggufs.md
    title: Unsloth Dynamic 3.0 GGUFs
  - id: aider-polyglot
    resource: ../raw/unsloth/basics/dynamic-3.0-ggufs/unsloth-dynamic-ggufs-on-aider-polyglot.md
    title: Unsloth Dynamic GGUFs on Aider Polyglot
---

Unsloth Dynamic GGUFs are post-training quantization artifacts that preserve chat, agentic-coding, and multilingual quality at a given disk size through per-layer quant selection, a curated imatrix calibration set, and model-specific schemes, with v3.0 improving small-quant fidelity over v2.0[^dynamic-ggufs].

## Method

- Pure post-training quantization: no training on the imatrix calibration set and no QAT or QAD; the imatrix file is published for community testing and reuse[^dynamic-ggufs].
- Per-layer dynamic selection: v2.0 onward adjusts the quantization type across layers rather than only selected layers, with different layer combinations per model[^dynamic-ggufs].
- Model-specific schemes: layers quantized for one model differ materially from another model, for example Gemma 3 versus Llama 4[^dynamic-ggufs].
- Calibration data is hand-curated and chat-oriented: v2.0 reports more than 1.5M tokens depending on model, while v3.0 reports a higher-quality diverse imatrix refined for agentic coding, chat, and multilingual performance[^dynamic-ggufs].
- v1-era Dynamic 1.58-bit worked effectively mainly for MoE architectures; v2.0 extends Dynamic quantization to MoE and non-MoE models[^dynamic-ggufs].
- Compatibility includes llama.cpp-compatible runtimes and Unsloth Desktop/Studio paths; the source names llama.cpp and Unsloth Desktop for v3.0 and llama.cpp plus Unsloth Studio for v2.0[^dynamic-ggufs].

## Versions and reported deltas

- Dynamic v3.0 is presented as a major improvement over v2.0, preserving more quality at the same size with stronger Divergence-300 @32 and KL Divergence results[^dynamic-ggufs].
- For Qwen3.8-27B, v3.0 is reported as more than 10% better top-1% accuracy at the same size than every other provider, and up to 10% extra top-1% accuracy at the same disk size on smaller quants[^dynamic-ggufs].
- Reported v3.0 size points include UD-Q2_K_XL around 9.83GB at about 8% higher top-1% than the next best, and UD-IQ1_S around 6.2GB without MTP retaining around 72% top-1% accuracy while about 89% smaller[^dynamic-ggufs].
- Older larger quants may still use v2.0: the source says bigger sizes showed less KLD improvement under the new method, so Unsloth retained the older UD-2 approach there pending further work[^dynamic-ggufs].
- v2.0 evidence cited includes Aider Polyglot, 5-shot MMLU, and KL Divergence wins, including a DeepSeek V3.1 3-bit GGUF Aider Polyglot result of 75.6% and Gemma 3 27B Q4_K_XL at 71.47% versus Google QAT at 70.64% while about 2GB smaller[^dynamic-ggufs].

## Aider Polyglot DeepSeek-V3.1 evidence

- Aider Polyglot is used as a real-world agentic-coding check of writing code, following instructions, and applying changes without human intervention[^aider-polyglot].
- DeepSeek-V3.1 tests cover both reasoning/thinking and non-reasoning modes; Aider Pass-2 is the reported convention from a median over about 3 runs by community contributor David Sluys[^aider-polyglot].
- Reported size win: 1-bit Unsloth Dynamic GGUF shrinks DeepSeek-V3.1 from 671GB to 192GB, about 75% smaller[^aider-polyglot].
- Thinking/reasoning Pass-2 highlights: full DeepSeek V3.1 76.1%, Unsloth 3-bit 75.6% ahead of Claude-4-Opus-May 72%, Unsloth 2-bit 66.7% ahead of Claude-3.7-Sonnet 64.9%, and Unsloth 1-bit 57.8% ahead of DeepSeek R1 56.9%[^aider-polyglot].
- Non-thinking Pass-2 highlights: full DeepSeek V3.1 71.6%, Unsloth 5-bit 70.7% matching Claude-4-Opus-May 70.7%, Unsloth 4-bit 69.7%, 3-bit 68.4%, 2-bit 65.8%, and 1-bit 55.7% ahead of DeepSeek-V3-0324 55.1%, GPT-4.1-April 52.4%, and GPT-4.5 44.9%[^aider-polyglot].
- Against same-size community dynamic imatrix GGUFs, Unsloth Dynamic is reported as consistently better, especially below 2-bit and above 4-bit; 3- and 4-bit perform similarly well[^aider-polyglot].
- Failure-mode contrast: other non-Unsloth 1- and 2-bit DeepSeek-V3.1 quants and standard 1-bit without selective-layer quantization either failed to load or produced gibberish and looping outputs, while Unsloth Dynamic retained usable accuracy[^aider-polyglot].

## Selective-layer ablation and template fix

- The durable method claim is to keep important/sensitive layers at higher precision while leaving unimportant layers at 1–6 bits; origin is Nov 2024 4-bit Dynamic selective-layer work, later applied to DeepSeek-R1/V3.1 including 8-bit-class treatment for sensitive tensors[^aider-polyglot].
- Ablation example: leaving `attn_k_b` at 4-bit in a semi-dynamic variant versus 8-bit in the Unsloth scheme adds only about 100MB, under 0.1%, but accuracy rises dramatically, so `attn_k_b` and similar DeepSeek-V3.1 tensors should stay at higher precision[^aider-polyglot].
- Fair-comparison procedure for community quants: match file size and bit type, and fall back to Unsloth's fixed chat template when a community quant errors, for example on a `split method must have between 1 and 1 positional arguments` failure[^aider-polyglot].
- llama.cpp minja fix: minja does not accept a positional argument in `.split`, so `content.split("</think>", 1)[1]` was replaced with splitting on `"</think>"` without the limit and rejoining the tail; the fixed template is published with the DeepSeek-V3.1 GGUF[^aider-polyglot].

## Packaging and runtime guidance

- MTP handling in v3.0: smaller quants under `UD-Q2_K_XL` at 8.37GB and below omit the MTP module to save around 500MB; a separate `Q4_0` MTP module is available when needed[^dynamic-ggufs].
- Extra small-quant formats for efficiency, especially Apple Silicon and ARM, include Q4_NL, Q5.1, Q5.0, Q4.1, and Q4.0 in the v2.0 line[^dynamic-ggufs].
- 1-bit operational limits: quants below UD-Q2_K_XL show a sharp Divergence-300 @32 fall from around 25% to under 8–10%, so they are unsuitable for agentic or tool-calling use and retain mainly short general-knowledge behavior[^dynamic-ggufs].
- Reported 1-bit mitigations are `presence_penalty = 1.5` or higher for looping, enabling thinking at least on low reasoning to avoid empty non-reasoning outputs, avoiding tool calling, and preferring UD-Q2_K_XL for real inference workloads[^dynamic-ggufs].
- Llama 4 running pattern in the source is Hugging Face `snapshot_download` of the chosen `*IQ2_XXS*` GGUF followed by `llama-cli` with large context, GPU layers, CPU offload for `.ffn_.*_exps`, sampling settings, and a Llama 4 header prompt; Unsloth also documents related fixes for RoPE scaling, QK-norm epsilon, and shared QK-norm that affected third-party accuracy[^dynamic-ggufs].
- DeepSeek-V3.1 running pattern is a CUDA `llama.cpp` build followed by `llama-cli -hf unsloth/DeepSeek-V3.1-GGUF:Q2_K_XL --jinja` with `--n-gpu-layers 99`, `--temp 0.6`, `--top-p 0.95`, `--min-p 0.01`, `--ctx-size 8192`, `--seed 3407`, and `-ot ".ffn_.*_exps.=CPU"`[^aider-polyglot].

## Relationships

- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — KLD, Divergence-300 @32, MMLU-replication, and calibration-leakage controls used to judge these quants.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — GGUF is one serving-side quantization path alongside AWQ, GPTQ, ModelOpt, Quark, and related toolchains.
- Uses [SGLang Quantization](sglang-quantization.md) — SGLang-side offline and online quantization context for deploying quantized checkpoints.

## Coverage limits

- Benchmark plots, GIF demonstrations, and Pass-1 comparison charts were not independently inspected; numeric deltas above are source-reported claims, not independently verified.
- Aider Discord benchmark snippets, Hugging Face template files, and external model, PR, and provider links were not inspected; related model-specific pages under `raw/unsloth/models/` remain separate sources.

[^dynamic-ggufs]: Unsloth Dynamic 3.0 GGUFs — `../raw/unsloth/basics/dynamic-3.0-ggufs.md`, Dynamic v3.0 method and size claims, MTP and 1-bit guidance, Dynamic v2.0 changes, Gemma QAT and Llama 4 sections, and Llama 4 Scout run example.
[^aider-polyglot]: Unsloth Dynamic GGUFs on Aider Polyglot — `../raw/unsloth/basics/dynamic-3.0-ggufs/unsloth-dynamic-ggufs-on-aider-polyglot.md`, DeepSeek-V3.1 thinking and non-thinking Pass-2 tables, same-size community-quant comparison, semi-dynamic `attn_k_b` ablation, minja chat-template fix, and DeepSeek-V3.1 `llama-cli` run example.
