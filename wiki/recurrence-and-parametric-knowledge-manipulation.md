---
type: Concept
title: Recurrence and parametric knowledge manipulation
description: One controlled study finds looped transformers retain similar synthetic factual-storage capacity while improving synthetic rule composition and multi-hop QA sample efficiency.
tags: [latent-reasoning, parametric-memory, parameter-sharing, reasoning, synthetic-tasks]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:21:45Z }
sources:
  - id: zhu2025ouro
    resource: ../raw/arXiv-2510.25741v5/paper.tex
    title: "Scaling Latent Reasoning via Looped Language Models"
---

# Recurrence and parametric knowledge manipulation

In synthetic tasks, the Ouro study reports that reapplying a transformer's shared blocks does not raise its measured factual-storage capacity at fixed parameter count, but improves performance and sample efficiency on tasks that compose stored facts. This supports a source-specific knowledge-*manipulation* interpretation of recurrence, not a general measurement of an LLM's factual memory or reasoning.[^zhu2025ouro]

## Controlled evidence

- On synthetic biographies, GPT-2-style looped and non-looped models from 1M to 40M parameters both reached roughly two bits of measured knowledge per parameter. The metric estimates encoded name-and-attribute information from cross-entropy, rather than testing open-world factual retrieval.[^zhu2025ouro]
- On the synthetic Mano modular-arithmetic tree task, looped configurations outperformed their iso-parameter non-looped counterparts at the tested maximum expression lengths. The source also reports some looped configurations matched or exceeded its iso-FLOP, deeper non-looped baseline.[^zhu2025ouro]
- In a synthetic three-hop natural-language relation QA task, six-layer models looped two or four times reportedly learned faster and with fewer distinct training QA pairs than the one-loop model. An appendix notes one iso-FLOP comparison that was not significantly better and calls for further validation, so the sample-efficiency conclusion remains tentative.[^zhu2025ouro]
- The source's MMLU depth ablation showed larger relative improvements from loop 1 to loop 4 in selected logic and mathematics categories than in global-facts and moral-scenarios categories. This is correlational benchmark evidence consistent with, but not independently validating, the synthetic interpretation.[^zhu2025ouro]

## Theoretical construction

The paper gives an existence construction: with a thresholding normalization, a one-layer single-head recurrent transformer of hidden dimension $2n$ can decide reachability in a combined contextual and parameter-encoded graph in $O(\log D)$ loops, where $D$ is graph diameter. It achieves this by repeated-squaring-style parallel expansion of an adjacency representation.[^zhu2025ouro]

This construction assumes an adjacency-matrix input, specially assigned parameters, thresholding normalization, and parameterized access to a fixed hidden graph. It is not a learned-model result or evidence that practical LoopLMs carry out the same algorithm.[^zhu2025ouro]

## Trust boundary and limitations

The evidence separates capacity from manipulation only under selected synthetic data generators, architectures, metrics, and training budgets. The approximately two-bits-per-parameter result does not bound factual capacity in natural-language foundation models; likewise, synthetic multi-hop accuracy does not establish an improvement in arbitrary retrieval or reasoning workloads.[^zhu2025ouro]

## Relationships

- Extends: [Virtual logical depth scaling](virtual-logical-depth-scaling.md) — both report fixed-parameter recurrence improving reasoning-oriented tasks without a corresponding increase in their chosen storage proxy.
- Relates to: [Circuit organization and systematic generalization](circuit-organization-and-systematic-generalization.md) — that work proposes recurrence or parameter sharing as a possible remedy for a cross-layer knowledge-access limitation; this source evaluates recurrence directly on different synthetic tasks.
- Supports the interpretation in: [Ouro looped language models](ouro-looped-language-models.md).

[^zhu2025ouro]: Zhu et al., *Scaling Latent Reasoning via Looped Language Models*, source manuscript, §§5–6 and appendices (arXiv:2510.25741v5, 2025).