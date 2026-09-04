---
type: Concept
title: Controlled looped-model architecture ablations
description: A living-study comparison attributes Huginn-style loop-model gains mainly to a prelude–recurrent-core–coda envelope and persistent contextual input access; its MoE transfer reports better routing balance and task-dependent gains over Ouro.
tags: [mixture-of-experts, recurrent-depth, transformers, weight-sharing]
status: draft
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:50:32Z }
sources:
  - id: huang2026looped
    resource: ../raw/TowardsLoopedModelsDoneRight.md
    title: "Towards Looped Models Done Right"
---

# Controlled looped-model architecture ablations

A July 2026 living article separates three coupled choices in Ouro- and Huginn-style looped transformers—where recurrence sits, whether a fixed input representation is rewritten at every step, and recurrent-state design. In its matched dense runs, it attributes the broad Huginn-style advantage chiefly to a prelude–recurrent-core–coda sandwich and persistent contextual input access; random initialization and a shared high/low state schedule have mixed results. Its source-reported MoE transfer finds Huginn-style models ahead of Ouro on most reported benchmarks and with more balanced routing, but the article is preliminary and its benchmark tables are image attachments not available in this repository.[^huang2026looped]

## Architecture frame and dense ablations

- The article represents a tied iterative model as a one-pass prelude $P$, repeated core $R$, and one-pass coda $C$, with a recurrent state initializer and an optional per-step write of a fixed prelude representation. Ouro is the full-stack case ($P$, write, and $C$ are identities); the Huginn-style case retains untied prelude/coda layers and repeatedly writes the contextualized prelude state.[^huang2026looped]
- At 730M stored parameters and 112 logical layers, its Ouro control is a 28-block stack run four times ($R_{28}^{4}$). Its sandwich control is an 8-layer prelude, 12-layer core run eight times, and 8-layer coda ($P_8R_{12}^{8}C_8$). The source holds logical depth and training budgets fixed across 42B–336B tokens.[^huang2026looped]
- At the 336B-token endpoint, the sandwich variant reportedly improves MATH500 by 12.00 points and DROP by 2.61 points over the full-stack control; its gains on MATH500 and BBH-CoT persist at the four reported budgets. The article reports mixed or negative changes on knowledge-heavy and strict code/specification tasks, so this does not establish a universal topology advantage.[^huang2026looped]
- Rewriting a fixed contextualized prelude state before each middle-core pass improves reported context- and specification-dependent tasks (including MMLU, BBH-CoT, DROP, HumanEval+, and MBPP+) but lowers MATH500 by 3.60 and GSM8K by 2.51 points in that architecture. The source treats this as a behavioral trade-off rather than a demonstrated mechanism.[^huang2026looped]
- With the sandwich and input write fixed, random state initialization and a shared-module high/low recurrent-state schedule provide no consistent aggregate gain. The latter keeps recurrent-body applications, parameters, and training budget fixed, but differs from architectures that use separately parameterized high- and low-level modules.[^huang2026looped]

## MoE transfer and routing evidence

- The source replaces each physical layer's dense FFN with top-2 routing over 25 experts. Both looped variants have 28 routed physical layers, 8.0B resident parameters, and 793.9M active parameters per physical pass; the 112-layer feedforward reference has 32.0B resident parameters at matched logical depth and active compute.[^huang2026looped]
- After 500B training tokens, the Huginn-style MoE reportedly exceeds Ouro on eight of ten benchmarks, with its largest reported gains on GSM8K (+4.70) and MATH500 (+3.60). Against the feedforward MoE, it reportedly wins on DROP and GSM8K, matches MATH500, and trails on seven tasks; these are source-run benchmarks, not a general model ranking.[^huang2026looped]
- At 500B tokens, the reported normalized load-balancing loss is 1.571 for Huginn-style MoE, versus 1.899 for Ouro and 1.652 for the feedforward reference (lower means more even expert use). Forcing later iterations to retain the identities of iteration-one experts reduces accuracy on all six tasks tested, providing intervention evidence that iteration-specific expert selection matters in this setup.[^huang2026looped]

## Trust boundary and coverage

This is explicitly a continuously updated living blog (“Part I”), with code marked for later release; no peer review, implementation, or independent replication is available in the source artifact. The source's image links and plotted/table values are remote Notion attachments rather than local files, so this compilation relies on the article's prose and captions and does not independently inspect the full tables or figures.[^huang2026looped]

The evidence is stronger for the article's controlled comparisons than for its proposed explanations of state refinement, gradient propagation, or routing behavior. Its dense and MoE configurations, data, and evaluation harness also bound portability to other recurrent layouts, training recipes, sparsity schemes, and systems performance.[^huang2026looped]

## Relationships

- Contrasts with: [Ouro looped language models](ouro-looped-language-models.md) — this source controls changes from full-stack Ouro recurrence to a Huginn-style envelope, whereas Ouro's source evaluates an adaptive full-stack model without this architecture ablation.[^huang2026looped]
- Related to: [Sparse MoE for looped language-model scaling](sparse-moe-for-looped-language-model-scaling.md) — both find loop-specific expert selection relevant, but this source includes an expert-identity intervention while the other source reports correlational pass-to-pass routing overlap.[^huang2026looped]
- Related to: [SMELT compute-matched MoE looped transformers](smelt-compute-matched-moe-looped-transformers.md) — both assess partial recurrence with MoE, but SMELT loops a middle span twice under a scaling grid while this study compares full-stack and sandwich designs at fixed 112 logical layers.[^huang2026looped]

[^huang2026looped]: Huang et al., *Towards Looped Models Done Right*, living article, §§1–4 and conclusion (dated July 31, 2026; compiled from `raw/TowardsLoopedModelsDoneRight.md`).
