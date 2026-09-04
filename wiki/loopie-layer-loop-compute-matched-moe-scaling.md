---
type: Concept
title: Loopie layer-loop compute-matched MoE scaling
description: Loopie applies each shared MoE transformer layer twice before advancing depth and selects larger recurrent models by measured optimizer-step time, reporting gains over matched Qwen3-like baselines.
tags: [mixture-of-experts, parameter-sharing, recurrent-depth, scaling, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:45:19Z }
sources:
  - id: gao2026loopie
    resource: ../raw/arXiv-2607.16051v2/neurips_2023.tex
    title: "Loop the Loopies!"
---

# Loopie layer-loop compute-matched MoE scaling

Loopie is a decoder-only MoE model family that applies every stored Transformer layer twice consecutively (**layer-loop**) instead of looping the entire stack. Its authors select recurrent configurations by matched measured optimizer-step wall time, converting reduced stored-depth activation memory into a larger microbatch; they report better downstream scores than their Qwen3-like vanilla MoE references after sufficient pretraining, but this is implementation- and hardware-dependent evidence rather than analytical FLOP equivalence.[^gao2026loopie]

## Architecture and matching recipe

- In conventional **model-loop** recurrence, the whole stack is repeated (for three layers and two passes: 1, 2, 3, 1, 2, 3). Layer-loop instead uses each layer twice locally (1, 1, 2, 2, 3, 3). The source argues that adjacent reuse improves parameter locality and pipeline execution; the latter are design arguments, not independently measured systems results.[^gao2026loopie]
- The two reported models are Loopie-20B-A2B and Loopie-6B-A0.6B, respectively with 20B/2B and 6B/0.6B total/active parameters. Both have two layer-loop applications, 128 top-8 MoE experts, grouped-query attention, and Qwen3 tokenization. The larger model has 27 stored layers of width 2,304; the smaller has 18 of width 1,536.[^gao2026loopie]
- Starting from a Qwen3-like 30B-A3B reference (48 layers, width 2,048), the recipe halves stored depth and sets two recurrences, then sweeps feasible width/depth candidates that permit twice the per-device microbatch. It chose the 27-layer, width-2,304 model because its measured optimizer-step time most closely matched the reference while holding hardware allocation, tokens per step, sequence length, data, optimizer, and checkpointing policy fixed.[^gao2026loopie]
- The selected model's leading-order block-work proxy is 1.424 times the reference, so the comparison explicitly does **not** claim equal theoretical FLOPs. It attributes matched time to lower activation memory at stored depth and a microbatch/gradient-accumulation change from $(b,g)$ to $(2b,g/2)$, which holds global batch size fixed.[^gao2026loopie]

## Reported scaling evidence

- Against the 30B-A3B reference trained for 800B tokens, Loopie-20B-A2B initially trailed but overtook it after about 600B tokens and remained ahead on the source's mean of eight downstream benchmarks. A layer-loop versus model-loop curve for Loopie-6B-A0.6B similarly reports layer-loop overtaking after about 1.2T tokens.[^gao2026loopie]
- In four reported matched-wall-time rungs, recurrent models with 0.11B, 0.18B, 0.41B, and 0.68B active parameters outscored respective 0.15B, 0.25B, 0.51B, and 1.00B vanilla references on the same eight-benchmark mean. The study uses 150B--500B tokens per rung, including deliberately overtrained small-model regimes.[^gao2026loopie]
- A loop-count sweep motivated two passes: the source reports diminishing marginal benefit for more layer-loop passes when compared with multiplying stored layers. It cautions that its two-pass stored-layer comparison was not precisely compute-matched, so this does not establish that two-pass looping dominates ordinary depth scaling.[^gao2026loopie]

## Trust boundary and limitations

The source reports its own Megatron-LM timing grid searches, training runs, and downstream means, without an external replication or end-to-end inference-cost comparison. Its fixed-time results therefore support the stated hardware/software configuration, checkpointing behavior, data, and benchmarks—not a portable exchange rate between recurrence, parameters, and FLOPs.[^gao2026loopie]

The headline 20B comparison uses an 800B-token pretraining run. Post-training changes model capabilities and should not be conflated with the pretraining architecture comparison.[^gao2026loopie]

## Contradictions

The source initially calls Stage 1 a 3T-token run, but later specifies a 570B-token corpus trained for four epochs (about 2.28T tokens). Adding its 1.26T-token Stage-2 pool gives about 3.54T, consistent with the 3.5T total in its post-training results table; the manuscript does not reconcile the initial 3T statement.[^gao2026loopie]

## Relationships

- Related to: [Sparse MoE for looped language-model scaling](sparse-moe-for-looped-language-model-scaling.md) — both investigate sparse experts as a way to make tied recurrent depth competitive, but Loopie uses hardware-matched wall time at larger reported scales rather than an isoFLOP study.
- Contrasts with: [Ouro looped language models](ouro-looped-language-models.md) — Loopie repeats each layer locally at fixed two-pass depth, whereas Ouro repeats its whole stack and learns an adaptive exit distribution.
- Uses: [Supervised pre-training at language-model scale](supervised-pre-training-at-language-model-scale.md) — Loopie's reported post-training pipeline applies SPT before math and code reinforcement learning.
- Contrasts with: [SMELT compute-matched MoE looped transformers](smelt-compute-matched-moe-looped-transformers.md) — SMELT repeats a middle block and closely matches FLOPs, parameters, and KV cache, while Loopie repeats each layer locally and matches measured optimizer-step time.

[^gao2026loopie]: Gao et al., *Loop the Loopies!*, source manuscript, abstract, §§1--5, appendix, and figures/tables (arXiv:2607.16051v2, 2026).