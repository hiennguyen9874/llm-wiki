---
type: Concept
title: Last-round KV caching for looped CED
description: Last-round KV caching retains terminal recurrent states instead of per-round histories, with small-model quality tests and workload-specific production-scale serving measurements.
tags: [looped-models, kv-cache, recurrent-transformers]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:18:48Z }
sources:
  - id: leng2026ced
    resource: ../raw/arXiv-2611.13378v1/main.tex
    scope: ../raw/arXiv-2611.13378v1/
    kind: paper
    revision: arXiv-2611.13378v1
    title: "Looping Deeper Without Growing the KV Cache: Recurrent Depth for Causal Encoder-Decoders"
  - id: leng2026kv
    resource: ../raw/arXiv-2611.13378v1/main.tex
    scope: ../raw/arXiv-2611.13378v1/
    kind: paper
    revision: arXiv-2611.13378v1
    title: Fixed-point quality evidence
  - id: leng2026serve
    resource: ../raw/arXiv-2611.13378v1/main.tex
    scope: ../raw/arXiv-2611.13378v1/
    kind: paper
    revision: arXiv-2611.13378v1
    title: Serving evidence
---

# Last-round KV caching for looped CED

Last-round KV caching stores each past token's final recurrent-round keys and values for reuse by every round of future tokens, rather than keeping a separate history per round. **Reported:** in [Looped CED](looped-causal-encoder-decoder-global-kv.md), stochastic-depth training made this substitution nearly lossless on the tested small models, while production-architecture serving benchmarks showed workload-dependent cache-capacity benefits. Lossless quality at production scale was assumed, not demonstrated.[^leng2026ced]

## Mechanism and quality evidence

During parallel training, each round attends to same-round historical KV. At inference, the model retains the last-round global KV and each looped layer's last-round sliding-window KV for completed tokens; the current token retains its own current-round state. This changes the inference context, so equivalence is an empirical condition, not an identity. Training samples a per-sequence Poisson depth with mean eight, clipped to at least one, and backpropagates through the final four rounds; evaluation uses eight rounds.[^leng2026ced]

**Reported:** in exact FP32 token-by-token validation across 2,829 samples, stochastic-depth models from 90M to 340M showed under 0.001 BPB change from per-round to last-round KV. At 150M/6B tokens the encoder model changes from 0.8465 to 0.8463 BPB; a fixed-eight-round training ablation instead worsens from 0.8484 to 0.8801. The authors observe late-round convergence for the stochastic model and a period-four cycle for the fixed-depth ablation, but this does not prove a general contraction theorem or guarantee losslessness at other scales.[^leng2026kv]

## Reported serving measurements

The authors implement a tied-layer SGLang schedule for a 40-layer, 552B-parameter DeepSeek-V4.1-Flash CED architecture, looping encoder layers 2–19; tests use a single four-GB200 tray or eight-H200 node. The model uses original or dummy weights not trained for recurrence, so these are cost benchmarks rather than quality evaluations. Per-round KV is **emulated by reducing the KV pool**, with the same compute, rather than implemented as an independently validated per-round engine.[^leng2026serve]

- At eight rounds, the specified GB200 configuration reports global KV of 1.6 KB/token for last-round CED, 8.5 KB/token for per-round CED, and 60.0 KB/token for a per-layer, per-round baseline: respectively 5.2× and 36.8× reductions in this component, not total model memory.[^leng2026serve]
- On 8K-input/1K-output requests, measured peak throughput is 185.1 versus 50.9 output tokens/s/GPU for last-round CED versus the per-layer/per-round baseline (3.6×); per-round CED achieves 142.5. At 128K context, last-round fits 38 requests and the baseline cannot fit one at eight rounds; pool and workload settings are specific to the experiment.[^leng2026serve]
- On the Mooncake toolagent trace at concurrency 512, median time to first token is 11.6 versus 345.1 seconds against per-round CED, attributed to fewer prefix-cache evictions. Output throughput differs by at most 13% in the cited comparison. Results are not an unconditional 29.7× speedup.[^leng2026serve]
- Recurrence still costs compute: at eight rounds measured GB200 prefill slope and decode step time are 5.12× and 3.95× unlooped CED respectively; the encoder loop is especially costly for prompt-heavy requests. The decoder-loop prefill implementation itself has overhead above its theoretical cost.[^leng2026serve]

## Limits and relationships

The package does not establish end-to-end quality for a frontier-scale loop-trained MoE, disaggregated serving, or universal fixed-point behavior. Figure PDFs were not visually inspected; claims use manuscript text and tables. Numerical provenance scripts and `data/numbers.json` are absent; no experiments were run independently.[^leng2026serve]

- Used by: [Looped causal encoder-decoder and global KV refinement](looped-causal-encoder-decoder-global-kv.md), which supplies the shared-KV architecture.
- Related: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) describes a different recursion-wise and first-recursion KV-sharing design.

[^leng2026ced]: Leng et al., arXiv:2611.13378v1, `sections/03_method.tex`, “Per-round training vs. last-round inference” and “Fixed-point convergence under stochastic depth”; `data/numbers.tex` configuration keys.
[^leng2026kv]: Same source, `sections/05_results.tex`, Table “Per-round versus last-round KV caching” and fixed-point discussion; `sections/appendix.tex` fixed-point analysis; `data/numbers.tex` keys `kvshare/x40/1024/ced-enc*` and `fp/x40/1024/ced-enc-fixed/fw/period`.
[^leng2026serve]: Same source, `sections/06_cost.tex`, Table “Workload / Metric” and serving discussion; `sections/appendix.tex`, production serving setup; `sections/appendix_serving.tex`, Table “Unit prefill and decode cost multipliers” and setup of serving figure; `sections/08_limitations.tex`.
