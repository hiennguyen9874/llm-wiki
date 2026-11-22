---
type: Concept
title: Inkling 2 Mini looped MoE architecture report
description: A social-media diagram reports that Inkling 2 Mini repeats its middle 12 layers three times, combining sparse MoE, block attention residuals, and gated cross-pass messages.
tags: [looped-models, mixture-of-experts, recurrent-depth, language-models]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:24:19Z }
stale_after: 2027-05-22
sources:
  - id: scaling01-inkling-mini
    resource: ../raw/2123909722646483219/index.md
    scope: ../raw/2123909722646483219/
    kind: web
    title: "Post by @scaling01 on X"
  - id: tml-inkling-mini
    resource: ../raw/inkling-2-mini/index.md
    scope: ../raw/inkling-2-mini/
    kind: web
    title: "Introducing Inkling 2 Mini"
---

# Inkling 2 Mini looped MoE architecture report

A social-media post and its attached architecture diagram describe Inkling 2 Mini as a looped sparse mixture-of-experts (MoE) model: a 12-layer middle core is applied three times between single-pass six-layer prelude and coda stacks. The diagram also reports block attention residuals and gated messages from the preceding pass. These details are **Reported**, not independently verified; the captured diagram attributes its facts to a model card, configuration and Transformers implementation, none of which was inspected here.[^scaling01-inkling-mini]

The model developer independently **reports** the same middle-loop layout, 24 stored layers and 48 layer applications; it also reports 26.4B total, 3.4B active and 5.4B loop-counted weight activations per token. This is developer reporting, not an inspection of the weights or implementation.[^tml-inkling-mini]

## Reported architecture

- The diagram shows 24 stored layers: layers 0–5 run once, layers 6–17 run three times with shared weights, and layers 18–23 run once. This yields 48 layer visits, not 48 independently parameterized layers.[^scaling01-inkling-mini]
- Four attention-residual blocks each span six layers. The pictured depth sources include token embeddings and earlier block sums. For passes after the first, messages based on the previous pass's block 2 and 3 sums are read by four learned queries per layer for Q, K, V and MoE; the diagram labels a rank-64 tanh gate and gives `(1 − f) · x + g · m`. The prelude and coda are shown without message gates.[^scaling01-inkling-mini]
- The diagram labels 128 experts, with eight routed and no shared experts per token. It reports 26.4B total stored parameters, 3.4B active parameters per token and 5.4B when counting three passes. These are reported parameter accounting figures, not measured FLOPs, wall-clock speed, or a quality comparison.[^scaling01-inkling-mini]
- Other depicted configuration includes 2,304 embedding dimensions, 24 query and eight KV heads, a 200k vocabulary and 1M-token native context. It shows gated grouped-query and sliding-window attention in a 5:1 ratio, short convolutions and an MoE feed-forward path. A 23-layer vision transformer and three-layer DSpark draft are explicitly omitted from the drawing.[^scaling01-inkling-mini]

## Interpretation and limits

The post author describes this as a larger, better-trained looping model than their own small experiment and calls Inkling's approach better; no measured comparison is supplied. Their statement that the design resembles what they had expected for GPT-6 is a prediction about another model, **not evidence** of GPT-6's actual architecture.[^scaling01-inkling-mini] See the separately sourced [GPT-6 Astra architecture report](openai-astra-looped-architecture-report.md).

The entry-point post and its sole local image attachment were inspected; the diagram is a secondary visualization, not the underlying model card, `config.json`, or implementation (its footer refers to Transformers pull request 51050). The underlying model card, configuration and implementation are unavailable in that package; the separately captured developer release supplies training, evaluation and architecture reporting, but has not independently verified the diagram’s finer implementation details.[^tml-inkling-mini] The diagram's creator, source revision and license are not established. The draft status reflects these provenance and coverage limits.[^scaling01-inkling-mini]

The separate [loop-position discussion](loop-position-and-workspace-hypothesis.md) preserves an apparent conflict between a later post’s description of a last-half loop and its own attached figure’s middle-loop design.

See [Inkling pruning, quantization and training](inkling-2-mini-pruning-quantization-and-training.md) for the release training and deployment recipe, and [variable-loop evaluation](inkling-variable-loop-reasoning-and-monitorability.md) for controlled pass-count results.

## Relationships

- Compared with: [SMELT](smelt-compute-matched-moe-looped-transformers.md) also studies a looped middle section with sparse MoE; the settings and evidence differ, so this is not a measured model comparison.[^scaling01-inkling-mini]
- Related to: [Controlled looped-model architecture ablations](controlled-looped-model-architecture-ablations.md) studies a prelude–recurrent-core–coda envelope; its results do not establish the effects of Inkling's specific design.[^scaling01-inkling-mini]

[^scaling01-inkling-mini]: @scaling01, X post, 2026-11-20, archived `raw/2123909722646483219/index.md`, post text and attached `assets/HXmkPlxXcAAJBt_.jpg` (central architecture, cross-pass message, MoE and resource-savings panels, and footer). The diagram's cited model card, config and implementation were not inspected.

[^tml-inkling-mini]: Thinking Machines Lab, *Introducing Inkling 2 Mini*, archived `raw/inkling-2-mini/index.md`, opening and §§“Architecture and training”, “Looping design”; publication date, capture date and license not stated.
