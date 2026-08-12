---
type: Concept
title: DFlash evaluation and serving trade-offs
description: DFlash reports large low-concurrency decoding gains over autoregressive and EAGLE-3 baselines, while gains shrink with concurrency and depend on target, task, backend, block size, and target-specific draft training.
tags: [speculative-decoding, evaluation, serving, throughput, diffusion]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T07:35:39Z }
sources:
  - id: dflash-2026
    resource: ../raw/arXiv-2602.06036v2/main.tex
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
---

# DFlash evaluation and serving trade-offs

DFlash’s author-run evaluation reports substantially longer accepted prefixes and higher decoding speedups than EAGLE-3 across tested Qwen3 and LLaMA-3.1 tasks. The strongest reported result is 6.09× over autoregressive decoding, but production-style SGLang and vLLM measurements show the expected systems boundary: acceleration generally falls as concurrency rises and depends on model, task, hardware, backend, and scheduling.[^dflash-2026]

## Main comparison

On Qwen3-4B and 8B with thinking disabled, a block-size-16 DFlash drafter was compared with EAGLE-3 trees of 16 and 60 using the Transformers backend and up to 2,048 generated tokens. Across seven math, code, and chat tasks:[^dflash-2026]

| Setting | DFlash average speedup | DFlash average acceptance $\tau$ | EAGLE-3 (16) average speedup |
|---|---:|---:|---:|
| Qwen3-4B, temperature 0 | 4.91× | 6.54 | 1.81× |
| Qwen3-8B, temperature 0 | 4.86× | 6.49 | 1.76× |
| Qwen3-4B, temperature 1 | 4.24× | 5.69 | 1.72× |
| Qwen3-8B, temperature 1 | 4.03× | 5.48 | 1.68× |

The peak 6.09× result occurs on Qwen3-4B MATH-500; Qwen3-8B reaches 6.08× on the same task. MT-Bench is consistently weaker at 2.47–2.85×, showing task dependence. Thinking-mode Qwen3 results range from 3.64× to 4.64× across GPQA, MATH-500, and AIME25.[^dflash-2026]

## Serving evidence

Single-B200 SGLang tests with FA4 and Spec-v2 overlap report gains at concurrency 1–32, but most shrink as batching fills the device. For Qwen3-8B, Math500 falls from 5.1× at concurrency 1 to 2.8× at 32; HumanEval falls from 4.2× to 2.4×. Qwen3-Coder-30B-A3B is flatter but lower, reporting 2.3–3.3× across three code tasks and tested concurrency levels.[^dflash-2026]

A separate vLLM Qwen3.5-9B evaluation follows the same pattern: Math500 drops from 4.0× at concurrency 1 to 1.9× at 32, HumanEval from 4.6× to 2.1×, and MT-Bench from 3.0× to 1.3×. These results support DFlash as a decode optimization rather than a constant multiplicative gain.[^dflash-2026]

## Generalization and adaptation

- DFlash outperformed official EAGLE-3 checkpoints for LLaMA-3.1-8B across GSM8K, HumanEval, and Alpaca at concurrency 1–32 under SGLang Spec-v1, though gains were lower than for Qwen3 and reached 1.4–2.8×.
- Additional single-B200, concurrency-8 results cover Qwen3.5, Qwen3-Coder-Next, and GPT-OSS targets; reported DFlash gains span 1.2–3.9× and exceed native MTP where compared.
- A Qwen3.5-27B drafter trained at 4K loses acceptance beyond that length. Fine-tuning on 1.6K LongAlign-10K samples improves reported 16K acceptance from 3.61–3.57 to 6.05–6.00 on HotpotQA and Qasper, and from 2.67 to 3.81 on GovReport; only GovReport is reported at 32K.[^dflash-2026]

## Relationships

- **Measures:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md).
- **Evidences:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md), especially the decline in gains as concurrency increases.
- **Compared with:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) on selected Qwen3.5 targets and EAGLE-3 in the paper’s main baselines.

## Evidence limits

All results are produced by the DFlash authors. The main EAGLE-3 comparisons use released third-party or official checkpoints rather than retraining every baseline under one pipeline, and other diffusion speculative methods are omitted because implementations were unavailable. Hardware and software vary across sections: H200/Transformers for many experiments, B200/SGLang with different speculative schedulers and attention backends for serving, and B200/vLLM for an appendix result. The paper reports decoding throughput and acceptance, not draft-training cost amortization, memory capacity under multi-tenant serving, prefill acceleration, energy, or independent reproduction. “Lossless” refers to target verification, not bitwise identity or unchanged system-level sampling behavior under every implementation.[^dflash-2026]

[^dflash-2026]: Chen, Liang, and Liu, “DFlash: Block Diffusion for Flash Speculative Decoding,” arXiv:2602.06036v2, [source](../raw/arXiv-2602.06036v2/main.tex), Sections 3 and 5, Tables 1–8, and Appendix C–F. The five PDF figures were visually inspected; they agree with the TeX captions and tabulated trends.
