---
type: Concept
title: OPT open pre-trained language models
description: OPT is a 125M-to-175B-parameter family of GPT-3-scale causal language models released to support direct research on large-model behavior and reproducibility.
tags: [opt, causal-language-modeling, pre-training, open-weights, reproducibility]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:15:02+07:00 }
sources:
  - id: opt-summary
    resource: ../raw/OPT.md
    title: "OPT: Open Pre-trained Transformer Language Models (summary)"
---

# OPT open pre-trained language models

OPT (Open Pre-trained Transformers) is Meta AI’s reported family of autoregressive language models ranging from 125M to 175B parameters. It was designed to reproduce GPT-3-scale capability while making model weights, experimental code, and training experience available for direct research, rather than introducing a new Transformer architecture.[^opt-summary]

## Architecture and family

OPT uses a decoder-only next-token-prediction Transformer with a GPT-2 byte-level BPE tokenizer and a 2,048-token context. The reported family has nine sizes: 125M, 350M, 1.3B, 2.7B, 6.7B, 13B, 30B, 66B, and 175B parameters. OPT-175B has 96 layers, 96 attention heads, and width 12,288, placing it near GPT-3 175B in scale.[^opt-summary]

The supplied summary reports ReLU activations, 0.1 dropout except on embeddings, AdamW with $(\beta_1,\beta_2)=(0.9,0.95)$, 0.1 weight decay, gradient clipping at 1.0, and linear warmup followed by learning-rate decay. As a base language model, original OPT was not instruction tuned or RLHF trained; the source therefore distinguishes text continuation from reliable instruction following.[^opt-summary]

## Data and scale context

The reported final pretraining corpus contains about 180B mostly English tokens. It combines BookCorpus, Stories, CC-News, selected The Pile components, and Pushshift Reddit conversations; the source says MinHashLSH removes near-duplicates at a 0.95 Jaccard threshold, while also warning that The Pile contains substantial duplication.[^opt-summary]

At roughly one training token per parameter for OPT-175B, the model is comparatively data-limited under the later Chinchilla summary’s approximate 20-token-per-parameter heuristic. That is a historical scaling comparison, not evidence that OPT was trained incorrectly for every objective or deployment constraint.[^opt-summary]

## Relationships

- **Compared with:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md); OPT-175B was intended as a near-GPT-3-scale and near-GPT-3-quality research release.[^opt-summary]
- **Characterized by:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md) as comparatively undertrained under its approximate token-per-parameter heuristic.
- **Operationalized by:** [OPT distributed training operations and transparency](opt-distributed-training-operations-and-transparency.md).
- **Limited by:** [OPT safety evaluation and controlled release](opt-safety-evaluation-and-controlled-release.md).

[^opt-summary]: “OPT: Open Pre-trained Transformer Language Models” (Vietnamese summary), [raw source](../raw/OPT.md), Sections 1–4 and 9–10. This is secondary-source evidence that links to arXiv:2205.01068; the primary paper, model card, code, and training log have not been independently ingested here.
