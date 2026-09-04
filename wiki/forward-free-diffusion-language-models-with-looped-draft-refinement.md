---
type: Concept
title: Forward-free diffusion language models with looped draft refinement
description: FReDA treats model-generated token drafts as the recurrent state of a shared refinement model, avoiding a prescribed diffusion corruption path and BPTT across refinement passes.
tags: [best-of-n, diffusion-language-models, iterative-refinement, looped-transformers, parameter-sharing]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:36:32Z }
sources:
  - id: sun2026freda
    resource: ../raw/arXiv-2606.08357v2/arxiv.tex
    title: "Forward-Free Diffusion Language Models with BPTT-Free Looped Refinement"
---

# Forward-free diffusion language models with looped draft refinement

FReDA formulates discrete diffusion language modeling as recursive refinement of drafts sampled from the model rather than denoising states from a prescribed forward-corruption process. It reuses a shared Transformer over explicit, block-level token drafts; earlier sampled refinement passes are stop-gradient and only the final pass receives gradients, avoiding BPTT *across* passes. In the source's 4B continued-pretraining evaluation, self-refinement and Best-of-$N$ variants outperform its listed sub-8B diffusion baselines on reasoning and code metrics, but this is a source-controlled comparison with different base models, training data, and token budgets.[^sun2026freda]

## Formulation and training

- Given a model-induced draft marginal, FReDA trains a refinement kernel to map a draft toward the clean target. Its tractable conditional negative-log-likelihood surrogate pairs clean targets with drafts sampled under the same context; it does not specify a token-level forward-noise schedule.[^sun2026freda]
- The paper proves that its joint surrogate upper-bounds the marginal KL objective. Its monotonic-improvement result is an idealized statement: it assumes optimization over a refinement family containing the identity kernel, not that finite FReDA training will improve every pass.[^sun2026freda]
- Training samples a refinement depth up to $K=3$. Earlier passes construct drafts with stopped gradients, while the last pass is trained; ordinary backpropagation remains within that final Transformer pass. This saves cross-pass BPTT but deeper sampled drafts still require the corresponding forward computations.[^sun2026freda]
- The 4B model continues Qwen3-4B-Base pretraining for 10B tokens with block size 4 and blockwise semi-causal attention. The corpus is intentionally weighted toward math, code, and formal logic (78% by the source's accounting), so reported reasoning and coding outcomes are not a broad pretraining comparison.[^sun2026freda]

## Refinement parameterizations

- **Self-refinement** predicts a token-factorized revision of its current draft. Its confidence-weighted soft draft embedding mixes the selected token embedding with a blank-token embedding, allowing low-confidence positions to remain more revisable across iterations.[^sun2026freda]
- **Best-of-$N$** generates parallel refinements and uses a lightweight, shared-backbone scorer to rank them. The scorer is trained against a clean positive and model-generated candidate negatives while the proposer is stopped; at inference, the reported rank combines proposal log likelihood and a weighted scorer value.[^sun2026freda]
- The authors interpret the optimal scorer as a target-versus-proposal marginal density-ratio correction. This is a population-optimum interpretation, not evidence that the learned finite scorer is calibrated as such in deployment.[^sun2026freda]

## Reported results and compute trade-offs

- Against the source's listed diffusion models, FReDA-4B Best-of-$N$ reports 84.15 GSM8K, 53.00 MATH-500, 63.41 HumanEval, and 59.76 HumanEval+; its self-refinement variant reports 83.55, 51.98, 60.98, and 58.54. The source also reports a 5.06-point average advantage over a BlockDiff-4B baseline trained with the same stated initial model and data.[^sun2026freda]
- The paper reports overall accuracy increasing from 25.9% with one refinement to 56.3% with five, with gains tapering after three. This demonstrates a reported quality--compute trade-off for this fixed architecture and evaluation; it does not establish stable arbitrary-depth extrapolation.[^sun2026freda]
- At matched source-defined quality, it reports 1.5--1.8$\times$ average generation speedup over compared diffusion baselines and 1.5--2.5 tokens per forward pass. These are decoding comparisons, not independently reproduced end-to-end serving measurements.[^sun2026freda]
- In ablations, Best-of-$N$ width 4 exceeds width 2 by 0.65 overall points at two iterations and 0.52 at four; scorer weight 0.1 yields the best listed overall score. The gains are modest and were measured on the source's aggregate math/coding setup.[^sun2026freda]

## Trust boundary and limitations

The empirical claims are from one paper's continued-pretraining and benchmark protocol. Baseline models differ in parameters, architecture, training corpus, and reported training budgets; e.g., the paper contrasts its 10B tokens with cited diffusion baselines trained on 50B or 600B tokens. The results support the reported outcomes, not an isolated causal estimate of removing the forward process.[^sun2026freda]

The paper's four vector figures were not independently rendered during ingestion; quantitative claims above come from the source text and included tables. No live credentials were found; public author contact details in the raw manuscript were not retained.

## Relationships

- **Related to**: [Recurrent-depth systematic generalization and extrapolation](recurrent-depth-systematic-generalization-and-extrapolation.md) — both reuse parameters across depth, but FReDA recurrently refines explicit token drafts and detaches prior passes, whereas the related study iterates a latent state on controlled synthetic tasks.
- **Related to**: [Depth-recurrent transformers for compositional generalization](depth-recurrent-transformers-for-compositional-generalization.md) — both investigate inference-time depth with shared weights, but FReDA's intermediate state is directly supervised text rather than an internal representation.
- **Related to**: [Ouro looped language models](ouro-looped-language-models.md) — both treat repeated use of a shared stack as variable compute, but FReDA revises drafts and may branch candidates rather than using Ouro's learned exit distribution.

[^sun2026freda]: Sun, Qiang, Zheng, and Dai, *Forward-Free Diffusion Language Models with BPTT-Free Looped Refinement*, source manuscript, abstract, §§2--5, appendices, and Tables 1--3 (arXiv:2606.08357v2, 2026).