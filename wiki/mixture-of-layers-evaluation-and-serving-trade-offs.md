---
type: Concept
title: Mixture of Layers evaluation and serving trade-offs
description: The Mixture of Layers report finds iso-active perplexity gains in selected data regimes and long-context prefill gains, but an iso-total dense-quality gap, scale-specific training overhead, and slower measured decode.
tags: [mixture-of-layers, evaluation, sparse-models, inference, long-context]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:18:06Z }
sources:
  - id: mol-2026
    resource: ../raw/2605.09516_MixtureofLayerswithHybridAttention/submission.tex
    title: "Mixture of Layers with Hybrid Attention: Parallel Thin Blocks for Sparse Transformer Compute"
---

# Mixture of Layers evaluation and serving trade-offs

The MoL preprint reports a quality advantage over its iso-active dense baselines in selected high-token regimes, but not over an iso-total dense model. At 1.3B scale it trades a 0.49-perplexity iso-active lead and hardware-dependent long-context prefill gains for a 3.01-perplexity iso-total deficit, 1.91–2.29$\times$ longer measured training time, and slower decode in the measured implementation.[^mol-2026]

## Reported quality by comparison basis

The source's comparisons distinguish total from active parameters rather than treating either as the sole fairness criterion:

| Setting | MoL result | Relevant dense comparison | What the result supports |
|---|---:|---:|---|
| WikiText-103, 85M total | K=5, top-3: $30.95\pm0.11$ PPL | dense softmax: 30.26 | MoL trails the iso-total dense baseline by 0.69 PPL. |
| WikiText-103, 198M total / 77M active | Hybrid 1+3of15: $29.99\pm0.08$ | dense softmax, 198M: 26.89 | Sparse block routing trails the iso-total dense model by 3.10 PPL. |
| Cosmopedia v2, about 104M | K=5, top-3: 6.49 | dense softmax: 6.65; dense DeltaNet: 6.64 | In this 15B-token single-epoch run, MoL leads both dense controls by 0.15–0.16 PPL. |
| FineWeb-Edu, 20B tokens | Hybrid 1+3of15, 2.08B total / 0.61B active: 18.04 | dense softmax 0.71B: 18.53; dense softmax 1.31B: 15.03 | MoL leads the closer iso-active model by 0.49 PPL but trails the smaller iso-total model by 3.01. |

The paper's dense DeltaNet Cosmopedia control ends at 6.64 versus dense softmax's 6.65, and its FFN-only MoE ablation ends at 6.89. Within that recipe, these controls support attributing the MoL lead to joint block-level routing rather than the DeltaNet substitution alone or FFN-only routing. They do not establish the mechanism across datasets or scales.[^mol-2026]

The 1.3B results use one seed per condition. The authors identify active per-layer capacity, greater within-MoL sparsity, and low tokens per total parameter as possible explanations for the iso-total gap, but their single trio of runs cannot separate them.[^mol-2026]

## Transfer and training cost

On the reported eight-task lm-eval-harness suite, the 1.3B MoL model wins four tasks against the 0.7B dense baseline and wins WinoGrande (54.38 versus 51.62) against the 1.3B dense model; it trails the 1.3B dense model on the listed broad-knowledge tasks and all models are near chance on MMLU. These task-level outcomes are author-run, low-scale, and not a general transfer ranking.[^mol-2026]

At the same 20B-token budget on four H200 NVL GPUs, the reported 2.08B-total MoL run takes 102.0 hours, versus 53.3 for dense 1.3B and 44.5 for dense 0.7B. The paper attributes this training cost to mandatory gradient checkpointing under its memory budget and replay cost for the routed DeltaNet kernel; it reports an 80M Cosmopedia setup without checkpointing was 1.45$\times$ faster than dense. Thus the source does not support treating the training penalty as intrinsic to all MoL implementations.[^mol-2026]

## Inference evidence

The source measures batch-one single-GPU prefill with FlashAttention-2 for softmax and FLA Triton kernels for DeltaNet:

- On RTX 3090, Hybrid MoL crosses the dense 1.3B model at roughly 5–6K tokens and is reported 1.25–1.76$\times$ faster at 8–32K.
- On A100, H100 SXM, and H200, the observed crossover lies between 64K and 128K. At 128K, MoL ranges from near parity on H100 (0.98$\times$) to 1.20$\times$ on A100; at 256K it is 1.42–1.54$\times$ faster on H100 and H200. Dense softmax OOMs at 256K on the 80GB A100 while the MoL configuration completes prefill.
- On the RTX 3090 decode test with KV cache, MoL latency stays near 60–65 ms/token but is slower than dense at every measured context, owing to an approximately 2,160-operation Python dispatch floor. The authors do not extrapolate beyond the measured 24K context.[^mol-2026]

The figure attachment shows the three FineWeb-Edu validation curves in the same final ordering reported in the table: dense 1.3B first, MoL second, and dense 0.7B third. It does not supply uncertainty for the one-seed scale run.[^mol-2026]

## Relationships

- **Evaluates:** [Mixture of Layers block routing](mixture-of-layers-block-routing.md) across quality, training, prefill, and decode measurements.
- **Compares with:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) on the distinction between active compute, total parameters, dispatch cost, and retained weights.[^mol-2026]
- **Uses:** [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md) as relevant prior hybrid-attention evidence, but under a different architecture and experimental setup.[^mol-2026]
- **Qualifies:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md): MoL reduces the fraction of layers with full softmax KV state but does not make all decode state fixed-size, and its implementation can still lose on decode latency.[^mol-2026]

## Evidence limits

All measurements are author-reported from one preprint, with no independent replication in this repository. The TeX source was read in full and the attached loss plot was visually inspected; its plotted ordering agrees with the text and table. The 1.3B quality results are single seed, prefill is single-GPU batch one with specified kernels, decode was measured only on RTX 3090 through 24K, and the paper explicitly declines a simple hardware scaling law.

[^mol-2026]: Ivan Ternovtsii and Yurii Bilak, “Mixture of Layers with Hybrid Attention: Parallel Thin Blocks for Sparse Transformer Compute,” May 2026 preprint, [source](../raw/2605.09516_MixtureofLayerswithHybridAttention/submission.tex), Sections 4–5 and appendices.