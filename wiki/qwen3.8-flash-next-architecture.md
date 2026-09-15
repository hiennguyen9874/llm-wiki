---
type: Concept
title: Qwen3.8-Flash-Next Architecture and Evaluation
description: Qwen3.8-Flash-Next 125B/6B-active plus 51B host n-gram design with 3:1 GDN/QSA hybrid, 4-branch gated residual, and 8-of-14 wins over the 397B-A17B flagship at 1/9 training FLOPs.
tags: [qwen3.8-flash-next, gdn, qsa, sparse-attention, gated-residual, ngram-embedding, moe, evaluation, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: 'On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability'
---

Qwen3.8-Flash-Next is a 125B-total / 6B-active sparse MoE plus 51B host-resident n-gram tables that matches the prior 397B-A17B flagship on 14 pre-training benchmarks while using ~1/3 activated parameters, ~1/3 training tokens, and ~1/9 training FLOPs[^qwen38-next-report].

## Model identity and design thesis

- 125B MoE parameters with 6B activated per token; additional 51B n-gram embedding tables held off-accelerator and prefetched from host memory[^qwen38-next-report].
- Base result: leads the 397B-A17B predecessor on 8 of 14 benchmarks and trails by at most 2.6 points on the other six[^qwen38-next-report].
- Every candidate change is judged on three axes: loss plus downstream benchmarks; training/prefill/decode cost; optimal hyperparameters and stability[^qwen38-next-report].
- Recurring finding: loss and downstream accuracy diverge — n-gram vocab growth lowers loss monotonically while accuracy saturates; data-dependent residual read/write gives marginal loss gain but clear benchmark gain; sparse 2-branch reads look free in pre-training but degrade after post-training; NoPE full attention looks equal in pre-training but causes more endless generation after post-training[^qwen38-next-report].

## GDN hybrid token mixing

- 3 Gated DeltaNet recurrent layers plus 1 full-attention layer per block of four; GDN compresses prefix into fixed-size state at linear cost while periodic full attention preserves exact token-level retrieval and long-context quality[^qwen38-next-report].
- GDN uses short causal depthwise convolutions on q/k/v, SiLU, L2Norm on q/k, data-dependent decay `alpha_t` and delta write `beta_t`, rank-one erase-and-write update, zero-centered RMSNorm, and bounded sigmoid output gate instead of SiLU[^qwen38-next-report].
- RoPE is retained in full-attention layers; NoPE variant is similar in pre-training but shows substantially higher endless-generation rate after post-training[^qwen38-next-report].
- 25B-A3B 400B+80B ablation: GDN hybrid beats full-attention Transformer on 8/9 benchmarks and beats SWA hybrid on 7/9, with best average 53.81 vs 51.15 SWA vs 49.87 full attention[^qwen38-next-report].
- Kernel: FlashQLA TileLang fused linear-attention gives 2–3x forward and ~2x backward speedup over FLA Triton baseline on NVIDIA GPUs[^qwen38-next-report].

## Qwen Sparse Attention

- At continued pre-training, full-attention layers become Qwen Sparse Attention: micro-block compression with ratio `r=4`, lightweight MQA indexer with 4 query heads plus 1 shared key head, partial RoPE on 64/128 indexer dims, block-causal ReLU-summed scores, token budget `K=2048` -> 512 complete blocks plus tail tokens[^qwen38-next-report].
- Key compression by average pooling precedes positional encoding so each block gets one block-level position without averaging different rotary phases[^qwen38-next-report].
- Training at 256K: Stage 1 dense distillation of summed teacher attention via max-pooled block distribution and KL loss, 1,000 steps at LR 1e-3 (~2B tokens, indexer only); Stage 2 sparse joint backbone plus indexer training, 8,000 steps at LR 2.5e-5 (~200B tokens) with KL only over selected top blocks[^qwen38-next-report].
- Loss tracks full attention within ~1e-4; fused QSA kernel computes sparse attention plus KL without materializing intermediates[^qwen38-next-report].
- General benchmarks: QSA matches or beats full attention on 7/8 suites and raises average 75.9 to 76.8[^qwen38-next-report].
- Long retrieval: RULER >512K 90.08 to 93.00; MRCR 512K 30.66 to 40.53 and 1M 20.71 to 26.44; comparable at shorter lengths[^qwen38-next-report].
- MTP with QSA-index reuse across 4-step speculative decoding leaves mean accepted length essentially unchanged (4.06 to 4.07)[^qwen38-next-report].
- Ablations at 35B-A3B: QSA matches full-attention RULER at 0.25 relative indexer latency while IndexShare stays below baseline at 0.5; few indexer heads suffice after joint training, so 4 heads chosen for speed/accuracy balance[^qwen38-next-report].
- Kernel-level at 1M: 7.6x prefill and 4.9x decode attention-module speedups; indexer complexity falls from `O(n^2)` to `O(n^2/r)`[^qwen38-next-report].

## Gated Residual

- Residual widened to `n_r=4` branches; read is elementwise gated and write is per-branch scalar; no `H_res` branch-mixing matrix[^qwen38-next-report].
- Starting point is simplified AltUp: per-block scalar read plus round-robin single-branch write, negligible compute, ~0.01 loss reduction on 25B-A3B/400B; data-dependent sigmoid read/write then adds benchmark value[^qwen38-next-report].
- Ablation findings: sigmoid gates beat tanh in loss and stability; making mix/combine data-dependent cuts loss only 0.002 but adds 1.98 accuracy points versus 1.58 from static widening alone; elementwise read helps while elementwise write adds almost nothing; predict from all branches with per-branch RMSNorm; `H_res` adds little once read/write are expressive[^qwen38-next-report].
- GR equations: per-branch RMSNorm with own gain, low-rank bottleneck `r=d/8` predicting `n_r x d` sigmoid gates, branch-averaged gated read; write is `2*sigmoid` scalar per branch added to every branch; no static term or special init needed; separate GR for attention and MLP sublayers; replaces block pre-norm[^qwen38-next-report].
- 25B-A3B/560B result: pre-norm loss 1.617 avg 50.91; mHC static 1.596/52.49; mHC dynamic 1.594/54.47; GR 1.590/54.66[^qwen38-next-report].
- Versus Attention Residual at 28 layers: full AttnRes 1.762 ties GR 1.762; block summaries cost 0.008 at S=2 and 0.011 at S=4; GatedNorm lowers every setting, more when the read is complex[^qwen38-next-report].
- Branch analysis with exact writer-to-reader decomposition: 21 of 780 paths gain `>=0.05` share; one branch is long-range (~10.9-layer typical skip) while other three stay local (3.4–3.9); e.g. layer-0 GDN to layer-15 attention 0.020 to 0.138, layer-10 GDN to layer-11 attention `Δ=0.117`, layer-0 MLP reaches both layer-2 locally and layer-15 distantly[^qwen38-next-report].
- Aggregate: adjacent-skip paths gain 0.96 share, long-range skip>12 gains 0.91, mid-range skip 2–12 loses 3.21; mean skip nearly unchanged (3.97 vs 3.91), so GR redistributes rather than increases cross-layer flow; softmax-attention sublayers are the main long-range readers[^qwen38-next-report].
- Inference: dropping `H_res` removes a full residual-state read per block; residual kept in FP8 with almost no quality loss because gated writes bound magnitudes; read/write each fused into one kernel with group RMSNorm folded into read; sparse top-2 branch reads looked free in pre-training but degraded after post-training and were rejected[^qwen38-next-report].

## N-gram embedding

- Single n-gram layer at Layer 2; same-parameter multi-layer splits (2+15, 2+25) give no consistent downstream benefit; placement is largely insensitive to full attention versus GDN[^qwen38-next-report].
- Shallow Layers 1–2 are strong but intermediate/deep remain competitive; Layer 2 chosen so host prefetch overlaps Layer-1 compute; sparse deterministic addressing gives negligible per-token FLOPs/latency with off-accelerator storage[^qwen38-next-report].
- Under fixed total budget (fewer MoE experts as n-gram grows): loss non-monotonic with minimum at 10x vocab (25% param ratio); uncheatable PPL flat; no clear downstream gain over MoE-only baseline, suggesting distinct scaling roles[^qwen38-next-report].
- With MoE fixed and vocab scaled 20V–200V: loss falls monotonically 1.585 to 1.526 while downstream saturates/fluctuates; Chinese C-Eval 66.91 to 74.94 and CMMLU 68.10 to 73.24 keep improving[^qwen38-next-report].
- Token normalization, non-uniform order allocation, and frequency partitioning showed no consistent gain in this recipe; ablation TPP is 300 tokens per active parameter[^qwen38-next-report].

## Base evaluation

- 14-benchmark base comparison: Flash-Next-Base beats Qwen3.8-27B-Base on all 14 and beats Qwen3.7-Plus-Base on 8/14 at ~1/9 training FLOPs[^qwen38-next-report].

| Suite | Flash-Next-Base | 27B-Base | 3.7-Plus-Base |
| --- | --- | --- | --- |
| MMLU / Redux / Pro | 90.36 / 90.68 / 73.23 | 87.51 / 87.26 / 68.60 | 90.43 / 91.47 / 70.90 |
| SuperGPQA / BBH | 51.36 / 90.87 | 44.86 / 89.56 | 48.42 / 89.41 |
| GPQA / GSM8K / MATH | 51.42 / 93.29 / 72.78 | 45.01 / 93.18 / 60.54 | 51.52 / 92.95 / 74.38 |
| EvalPlus / MultiPL-E / SWEBench-Pretrain | 78.76 / 79.09 / 50.99 | 76.05 / 74.50 / 41.66 | 78.06 / 81.68 / 49.24 |
| MGSM / MMMLU / INCLUDE | 89.33 / 84.86 / 78.40 | 86.37 / 79.74 / 74.37 | 85.42 / 84.53 / 78.90 |

## Relationships

- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — datacenter serving realization with GDN/QSA, IndexShare MTP, gated-residual kernels, and PLE host offload.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — same 125B-plus-51B identity via Unsloth GGUFs and llama.cpp rather than training architecture.
- Related to [Qwen3.8-Flash-Next Training and Stability](qwen3.8-flash-next-training.md) — optimizer, hyperparameter, and stability choices that make this architecture trainable at scale.
- Related to [Qwen3.8-Flash-Next HF Release and Serving](qwen3.8-flash-next-hf-release.md) — official HF checkpoint, Transformers code, thinking and YaRN serving, and post-trained evaluation for this architecture.
- Related to [Qwen3.8-2.4T-A95B Architecture and Evaluation](qwen3.8-2.4t-a95b-architecture.md) — prior Qwen3.8 69-GDN/23-GQA flagship family preceding this 3:1 GDN/QSA Flash-Next design.

## Coverage limits

- Figure JPGs under `raw/Qwen3.8-Flash-Next-tech_report/images/` were not visually inspected; architecture and speedup claims follow prose, equations, and tables.
- All benchmark, loss-delta, and kernel-speedup figures are report snapshots on stated model scales and contexts, not independently verified.
- No credentials, PII, or disclosure markings found.

[^qwen38-next-report]: On the Design of Qwen3.8-Next Architecture — `../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md`, Abstract plus Sec. 2.1–2.3 and Sec. 4–5 covering 125B/6B+51B identity with 1/3-params 1/3-tokens 1/9-FLOPs claim, 3:1 GDN/full-attention plus FlashQLA, QSA c4/K2048 two-stage CPT with RULER/MRCR/MTP evidence and 7.6x/4.9x kernel gains, 4-branch GR with ablations and path analysis plus FP8 inference, single-layer-2 n-gram with vocab-scaling divergence, and 14-benchmark Table 11.
