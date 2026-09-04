---
type: Synthesis
title: Looped transformers versus untied depth scaling
description: Looped transformers trade unique layer capacity for repeated computation, whereas ordinary depth adds both compute and distinct parameters; which is preferable depends on whether parameters, FLOPs, memory, or latency is constrained.
tags: [parameter-sharing, recurrent-depth, scaling, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T04:14:31Z }
sources:
  - id: zhu2025ouro
    resource: ../raw/arXiv-2510.25741v5/paper.tex
    title: "Scaling Latent Reasoning via Looped Language Models"
  - id: kohli2026loop
    resource: ../raw/arXiv-2604.07822v2/colm2026_conference.tex
    title: "Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers"
  - id: lee2026sparse
    resource: ../raw/arXiv-2605.09165v2/main.tex
    title: "Sparse Layers are Critical to Scaling Looped Language Models"
  - id: wang2026smelt
    resource: ../raw/arXiv-2609.01343v1/paper.tex
    title: "SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers"
---

# Looped transformers versus untied depth scaling

A looped transformer executes a physical stack repeatedly with tied weights; ordinary depth appends blocks with independent weights. For a stack of $K$ blocks and $R$ visits, both can expose $KR$ logical block applications, but looping stores roughly $K$ blocks while an untied model stores $KR$. The exchange is therefore **fewer unique parameters for comparable serial computation**, not free depth. Dense untied depth is the safer default when quality at equal effective depth is primary; looping is attractive when parameter or optimizer-state memory is scarce, inference depth should vary, or the task benefits from iterative reuse.[^zhu2025ouro]

## Comparison by constraint

| Comparison regime | Looped transformer | Add untied blocks/layers |
|---|---|---|
| Same stored parameters | Buys more logical depth by spending more FLOPs and latency; selected studies report gains on reasoning/composition without increasing their storage proxies.[^zhu2025ouro] | Cannot add substantial depth without increasing parameters; retains more distinct transformations per application. |
| Same logical depth / active FLOPs | Uses fewer unique parameters but dense tied models generally trail matched-depth untied baselines in the controlled studies available here.[^zhu2025ouro][^lee2026sparse] | Usually stronger dense baseline because every depth position can specialize independently. |
| Same parameter, FLOP, and KV-cache budgets | Requires architectural rebalancing rather than merely repeating a stack. SMELT narrows width, adds sparse experts, and loops only the middle span; it reports gains within its own source-controlled grid.[^wang2026smelt] | Simpler baseline and systems path; no recurrent-state or pass-conditioning design is required. |
| Variable inference compute | Can run more or fewer visits, potentially per sequence or token, but needs training for multiple depths and a stopping policy. Excess recurrence can overwrite correct predictions.[^kohli2026loop] | A fixed-depth stack normally has fixed compute unless paired with layer skipping, early exit, or another routing mechanism. |
| Parameter/optimizer memory | Lower because weights and optimizer states are shared across visits. | Grows with every unique block. |
| Activation memory and latency | Still pays for serial block applications; training may need activations across visits. Savings depend on checkpointing and implementation. | Also serial with depth, but standard kernels, pipeline plans, and serving stacks are usually more direct. |
| KV cache | Weight tying does not automatically remove per-logical-depth cache state; cache policy can erase expected memory savings or reduce quality. | Cache grows predictably with the number and shape of unique attention layers. |

## Capability trade-off

- **Expressivity and specialization:** untied depth gives each layer independent parameters, so stages can specialize. Tying forces repeated use of one transition and is a capacity bottleneck; this is consistent with the reported dense looped deficit at matched effective depth.[^zhu2025ouro][^lee2026sparse]
- **Iterative algorithm bias:** looping encourages repeated state refinement. Controlled synthetic studies associate this with improved fact composition, multi-hop sample efficiency, systematic generalization, and some inference-depth extrapolation, but these results do not establish broad frontier-LLM superiority.[^zhu2025ouro][^kohli2026loop]
- **Knowledge storage:** source-specific random-sequence and synthetic-biography proxies remain approximately tied to unique parameter count, suggesting loops improve manipulation more readily than storage. These proxies are not general measurements of factual knowledge.[^zhu2025ouro]
- **Sparse experts can soften the bottleneck:** a controlled isoFLOP study found Looped-MoE above its dense untied baseline while dense looping remained below it; unlooped MoE still had the best test loss. This supports MoE as one remedy, not looping as universally superior.[^lee2026sparse]
- **Stability is less automatic:** repeated residual dynamics can diverge, converge prematurely, or overthink. Loop count, normalization, residual scaling, initialization, depth supervision, and input injection become first-class architecture choices.[^zhu2025ouro][^kohli2026loop]

## Practical decision rule

1. Use **untied added depth** when the budget permits more parameters and the objective is the strongest, lowest-risk quality at a fixed logical depth.
2. Use **looping** when unique-parameter or optimizer memory is the binding constraint, adaptive depth is valuable, or there is evidence that iterative refinement matches the task.
3. Do not compare only by parameter count: report stored parameters, active FLOPs, logical depth, training tokens, activation memory, KV cache, throughput, and latency.
4. For a serious looped design, benchmark against both an iso-parameter shallower model and an iso-compute untied deeper model. If using MoE or width changes, also match stored parameters and cache as closely as possible.

## Relationships

- Synthesizes: [Loss scaling for looped language models](loss-scaling-for-looped-language-models.md) and [Virtual logical depth scaling](virtual-logical-depth-scaling.md).
- Supported by: [Recurrence and parametric knowledge manipulation](recurrence-and-parametric-knowledge-manipulation.md) and [Recurrent-depth systematic generalization and extrapolation](recurrent-depth-systematic-generalization-and-extrapolation.md).
- Qualified by: [Sparse MoE for looped language-model scaling](sparse-moe-for-looped-language-model-scaling.md) and [SMELT compute-matched MoE looped transformers](smelt-compute-matched-moe-looped-transformers.md).

[^zhu2025ouro]: Zhu et al., *Scaling Latent Reasoning via Looped Language Models*, source manuscript, §§3–6 and appendices (arXiv:2510.25741v5, 2025).
[^kohli2026loop]: Kohli, Parthasarathy, Sun, and Yao, *Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers*, source manuscript, §§2–5 and appendices (arXiv:2604.07822v2, 2026).
[^lee2026sparse]: Lee et al., *Sparse Layers are Critical to Scaling Looped Language Models*, source manuscript, §§2–5, appendix, and Tables 1–4 (arXiv:2605.09165v2, 2026).
[^wang2026smelt]: Wang et al., *SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers*, source manuscript, §§1–7, appendices, figures, and tables (arXiv:2609.01343v1, 2026).
