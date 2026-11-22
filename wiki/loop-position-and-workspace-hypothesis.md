---
type: Concept
title: Loop position and the workspace hypothesis
description: A social-media post and attached Inkling figure report loop-position comparisons and speculate that recurrent middle layers serve as a reasoning workspace.
tags: [looped-models, reasoning, recurrent-depth, transformers]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:24:19Z }
sources:
  - id: scaling01-position
    resource: ../raw/2123943370145890767/index.md
    scope: ../raw/2123943370145890767/
    kind: web
    title: "Post by @scaling01 on X"
  - id: tml-inkling-position
    resource: ../raw/inkling-2-mini/index.md
    scope: ../raw/inkling-2-mini/
    kind: web
    title: "Introducing Inkling 2 Mini"
---

# Loop position and the workspace hypothesis

A social-media post and an attached Inkling 2 Mini figure discuss whether the position of repeated layers affects looped-transformer quality. The figure reports stronger results for a middle loop than a last-half loop in its experiment; the poster separately reports informal observations and hypothesizes that the loop should occupy a middle reasoning workspace. These are **Reported** claims, not independently verified or a demonstrated causal mechanism.[^scaling01-position]

## Position comparison

- The attached figure describes a 24-layer model split into four six-layer blocks: the two middle blocks are repeated three times, with the first and last blocks run once. It reports that looping middle layers 7–18 yielded larger accuracy gains than looping last layers 13–24 on 27 of 28 evaluations. Benchmark identities, accuracy values, and uncertainty are not supplied in the capture.[^scaling01-position]
- At training step 2,000, the figure estimates that a no-loop baseline would require 1.51–1.91× as much training compute to match the middle-loop loss, versus 1.24–1.36× for the last loop. Each interval spans estimates across the same three evaluations; both looped runs used three passes and equal training compute. These are estimated compute-equivalent loss gains, not measured wall-clock speedups; the estimation method and full training details are unavailable.[^scaling01-position]
- The poster says their own first-half and second-half looping performed poorly, middle looping worked well, and a position slightly above the middle may be better but remains unproven. The post does not provide model sizes, tasks, comparison budgets, results, or methods for these separate experiments.[^scaling01-position]

The developer’s release independently describes middle blocks as the deployed design and repeats the 27/28 result and compute estimates; it does not provide the full protocol or uncertainty for the position comparison.[^tml-inkling-position]

## Hypothesis and limits

The poster speculates that reasoning should happen in a recurrent workspace, leaving early sensory/input and late motor/output functions uncluttered, and connects this to Anthropic's J-space work. An attached J-lens diagram labels early sensory, middle workspace, and late motor regions and shows a Sonnet 4.5 layer-similarity heatmap. The image alone does not establish that these regions cause loop-position effects, that reasoning occurs entirely within the loop, or that the result transfers across architectures or tasks.[^scaling01-position]

## Contradictions

The post says Thinking Labs “looped the entire second half” of its model, whereas the attached Inkling 2 Mini figure describes the two middle blocks as the deployed looping design and the last half as an experimental comparison. The post may refer to that comparison rather than the final model, but its wording does not resolve the distinction; the developer’s release explicitly supports the middle-loop deployment, although the post’s intended meaning remains unclear.[^tml-inkling-position] The separate [Inkling architecture report](inkling-2-mini-looped-moe-architecture-report.md) also describes a middle loop.[^scaling01-position]

## Relationships

- Related to: [Inkling 2 Mini looped MoE architecture report](inkling-2-mini-looped-moe-architecture-report.md) describes the same reported middle-loop layout from a separate captured diagram.[^scaling01-position]
- Related to: [Controlled looped-model architecture ablations](controlled-looped-model-architecture-ablations.md) compares a prelude–recurrent-core–coda design with full-stack recurrence; its setting differs and does not test this proposed workspace mechanism.[^scaling01-position]

## Coverage and trust

The post and both local image attachments were inspected. The figure and J-lens diagram are screenshots; their complete original publications, protocols, underlying data, authorship, revisions, licenses, and linked citations were not supplied or independently inspected. The post's publication date and author are capture metadata; the screenshot's origin and date are not independently established. Draft status reflects those provenance and evidence limits.[^scaling01-position]

[^scaling01-position]: @scaling01, X post, 2026-11-21, archived `raw/2123943370145890767/index.md`, post text; `assets/HXm-UjEWsAAiF-k.png`, “Looping design” and Figure 4; `assets/HXnAJ7IX0AAn6i6.jpg`, Figure 27 and J-lens heatmap.

[^tml-inkling-position]: Thinking Machines Lab, *Introducing Inkling 2 Mini*, archived `raw/inkling-2-mini/index.md`, §“Looping design”, position-comparison text and compute-equivalent gain caption.
