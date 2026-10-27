---
type: Attention Mechanism
title: Sparse Reference Sliding Window Attention
description: Sparse Reference Sliding Window Attention bounds each query's active visual references through page gating and learned top-k block routing alongside a local window.
tags: [ml, attention, sliding-window-attention, kv-cache, document-parsing]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:01:00Z }
sources:
  - id: report
    resource: ../raw/Unlimited-OCR-2.pdf
    kind: paper
    title: Unlimited OCR Works 2
  - id: model-card
    resource: ../raw/Unlimited-OCR-2.md
    kind: model-card
    title: Unlimited OCR 2 model card
---

# Sparse Reference Sliding Window Attention

Sparse Reference Sliding Window Attention (SR-SWA) augments a bounded local attention window with a fixed budget of selected visual blocks. Unlike [Reference Sliding Window Attention](reference-sliding-window-attention.md), which retains access to the whole visual prefix, it gates candidate blocks by page and selects relevant ones using a learned router. **Reported:** this reduces active visual attention as document length grows; it does not by itself bound all resident visual KV caches.[^report]

## Mechanism

**Reported:** Page Gate chooses blocks intersecting the query's designated page; blocks can straddle page boundaries. Positions combine alternating 0–1 page coordinates with monotonic intra-page coordinates. Token Sieve summarizes candidate keys, scores them against the query, applies α-entmax and retains the top-k blocks. The local window and chosen blocks form the retained attention set; selected blocks receive mean-centered log routing probabilities as attention-logit biases, allowing the language-model loss to train the router without an auxiliary KL distillation loss.[^report]

The model card gives 512 reference tokens as an example, not a universal capacity specification.[^model-card] The report does not specify enough routing implementation and benchmark configuration to establish independently that every component's cost is constant as candidate pages or image resolution vary.[^report]

## Separate cache-management requirement

**Reported:** all-at-once prefill still stores visual KV for every page. Unlimited-horizon decoding instead divides pages into fixed-size overlapping chunks, reuses the shared boundary page's visual KV and a text KV tail, releases inactive visual caches and processes chunks sequentially. Only the first chunk carries the instruction. Thus bounded resident GPU cache depends on chunk scheduling and fixed configuration, not merely sparse attention; total work and output necessarily grow with document size. The paper acknowledges loss of global document information.[^report]

## Relationships

- **Extends:** [Reference Sliding Window Attention](reference-sliding-window-attention.md) by sparsifying the reference side.[^report]
- **Used by:** [Unlimited OCR 2](unlimited-ocr-2.md), with chunked decoding for resident-cache control.[^report]

[^report]: Baidu ERNIE Team, [Unlimited OCR Works 2](../raw/Unlimited-OCR-2.pdf), §§3.2–3.4, equations 2–7, Algorithm 1, Figure 4 and §6.
[^model-card]: Baidu, [Unlimited OCR 2 model card](../raw/Unlimited-OCR-2.md), § What's New in 2.
