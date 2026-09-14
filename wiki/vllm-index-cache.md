---
type: Concept
title: vLLM IndexCache for DeepSeek Sparse Attention
description: Reusing DeepSeek DSA top-k indices across layers via use_index_cache, index_topk_freq, and index_topk_pattern.
tags: [vllm, deepseek, sparse-attention, optimization]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: index-cache
    resource: ../raw/vllm/features/index_cache.md
    title: IndexCache
---

IndexCache reduces redundant top-k token-selection computation in DeepSeek-V3.2 DeepSeek Sparse Attention (DSA) models by caching indices from Full layers and reusing them in Shared layers[^index-cache].

Enable it with `--hf-overrides '{"use_index_cache": true, ...}'`; it requires a DeepSeek-V3.2 or compatible DSA model[^index-cache].

## Configuration

| Parameter | Type | Default | Description |
|---|---|---|---|
| `use_index_cache` | bool | false | Enable IndexCache; must be true to use this feature[^index-cache]. |
| `index_topk_freq` | int | 1 | Frequency in layers at which top-k is computed; 1 means every layer (effectively disabled), 4 means 1/4 of layers[^index-cache]. |
| `index_topk_pattern` | str | null | Per-layer F/S pattern overriding `index_topk_freq`; each character maps to one DSA layer with F = Full (compute) and S = Shared (reuse)[^index-cache]. |

Using frequency[^index-cache]:

```bash
vllm serve deepseek-ai/DeepSeek-V3.2 \
    --hf-overrides '{"use_index_cache": true, "index_topk_freq": 4}' ...
```

Using an explicit 61-layer pattern[^index-cache]:

```bash
vllm serve deepseek-ai/DeepSeek-V3.2 \
    --hf-overrides '{"use_index_cache": true, "index_topk_pattern": "FFSFSSSFSSFFFSSSFFFSFSSSSSSFFSFFSFFSSFFFFFFSFFFFFSFFSSSSSSFSF"}'
```

## How it works

Layers marked `F` (Full) compute and store top-k indices; subsequent layers marked `S` (Shared) receive the cached indices from the previous layer instead of recomputing, with the cached indices passed through the layer stack[^index-cache].

This saves computation because DSA otherwise computes per-layer top-k selection, which is expensive in deep models with many layers[^index-cache].

## Coverage limits

- The cited IndexCache paper (`https://arxiv.org/abs/2603.12201`) was not inspected; performance and accuracy trade-offs are not compiled here[^index-cache].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — IndexCache reuses DSA sparse top-k indices within the attention computation those backends provide.

[^index-cache]: IndexCache — `../raw/vllm/features/index_cache.md`.
