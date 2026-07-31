---
type: Concept
title: BLOOM open multilingual language model
description: BLOOM is BigScience’s reported 176B-parameter causal language model, developed through an international open-science collaboration and released with weights, code, checkpoints, and documentation under a use-restricting RAIL license.
tags: [bloom, bigscience, causal-language-modeling, multilingual, open-weights]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:41:40Z }
sources:
  - id: bloom-summary
    resource: ../raw/BLOOM.md
    title: "BLOOM overview (Vietnamese summary)"
  - id: alibi-summary
    resource: ../raw/ALiBi.md
    title: "ALiBi overview (Vietnamese summary)"
---

# BLOOM open multilingual language model

BLOOM (BigScience Large Open-science Open-access Multilingual Language Model) is BigScience’s reported 176B-parameter decoder-only language model. The supplied overview characterizes its principal contribution as an unusually large, multilingual, collaboratively developed open-access release—not as a fundamentally new Transformer architecture—and reports releases of weights, code, intermediate checkpoints, and development documentation.[^bloom-summary]

## Reported architecture

The overview reports 70 Transformer layers, hidden width 14,336, 112 attention heads of dimension 128, a 2,048-token training context, and a 250,680-token byte-level BPE vocabulary. BLOOM is pre-trained with causal next-token prediction, so the base model should be understood as a text-completion model rather than an instruction-tuned chat system.[^bloom-summary]

Its reported architectural variations include [ALiBi attention with linear biases](alibi-attention-with-linear-biases.md), layer normalization after word embeddings (called StableEmbedding), and GELU feed-forward activations. ALiBi adds a head-specific distance penalty to attention scores; the source describes this as avoiding a learned positional-embedding table and potentially supporting longer-context extrapolation, not as proof of uniformly better long-context behavior.[^bloom-summary][^alibi-summary]

## Openness and scope limits

The source reports that BLOOM weights were released under Responsible AI License (RAIL) terms that restrict specified harmful uses. Consequently, public weight availability and substantial accompanying documentation do not make BLOOM unrestricted software under every definition of “open source.”[^bloom-summary]

The overview also describes multilingual and code-generation capabilities as dependent on language, prompt format, data representation, and model variant. It reports that multitask prompted fine-tuning produced BLOOMZ, a related model better suited to instruction following; this does not make the original BLOOM base model instruction tuned.[^bloom-summary]

## Relationships

- **Uses:** [ROOTS multilingual training corpus and governance](roots-multilingual-training-corpus-and-governance.md) as its reported pretraining data source.
- **Operationalized by:** [BLOOM distributed training and responsible release](bloom-distributed-training-and-responsible-release.md).
- **Compared with:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md); both are reported GPT-3-scale causal models, while the supplied overview distinguishes BLOOM through intentional multilingual design and conditional weight access.[^bloom-summary]

[^bloom-summary]: “BLOOM overview” (Vietnamese summary), [raw source](../raw/BLOOM.md), Sections 1–3, 6, and 8–10. This is secondary-source evidence linking to the BLOOM paper, model page, and related papers; those primary materials have not been independently ingested here.
