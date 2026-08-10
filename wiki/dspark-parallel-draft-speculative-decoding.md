---
type: Concept
title: DSpark parallel-draft speculative decoding
description: DSpark extends the DFlash parallel-draft backbone with a Markov logit-bias head and a per-position confidence head, trained by SpecForge online distillation from a live target's hidden states.
tags: [speculative-decoding, draft-model, dspark, dflash, distillation]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T13:58:35Z }
sources:
  - id: kimi-k3-dspark-card
    resource: ../raw/KimiK3DSparkspeculator.md
    title: "Kimi K3 DSpark speculator (Hugging Face model card)"
---

# DSpark parallel-draft speculative decoding

DSpark is a speculative-decoding draft architecture that extends the DFlash parallel-draft backbone with a Markov logit-bias head and a per-position confidence head. The published Kimi K3 DSpark speculator implements it as a 2.25B-parameter draft — five full-attention Qwen3-style GQA layers, hidden size 7168, 64 query heads and 16 KV heads — trained from random initialization by SpecForge online distillation against a frozen Kimi K3 target, with block size 7, meaning each round verifies one current token plus seven draft tokens.[^kimi-k3-dspark-card]

## Draft architecture

- **DFlash backbone:** DSpark builds on DFlash's parallel-draft backbone, which proposes draft tokens in parallel rather than purely sequentially. The card does not define DFlash's internal structure beyond this role.
- **Markov logit-bias head:** biases draft logits during proposal, adding Markov-conditioned bias on top of the backbone's output.
- **Per-position confidence head:** predicts acceptance confidence at each draft position, supplying a per-position signal the architecture can use for draft behavior such as adaptive stopping.
- **Topology:** 5 full-attention Qwen3-style GQA layers, hidden size 7168, 64 query heads / 16 KV heads; `block_size=7`; verification width of 1 current token + 7 draft tokens.
- **Auxiliary target layers:** `[7, 23, 51, 67, 83]` — the draft reads hidden states from these Kimi K3 layers as auxiliary features.
- **Checkpoint:** 2,249,289,601 parameters in a single-file BF16 safetensors; target embedding and unembedding weights are not included, so the draft carries its own vocabulary projections.
- **Scale note:** at about 2.25B parameters against a roughly 2.8T-parameter Kimi K3 target, this draft is far larger than the small drafts typical of textbook speculative decoding, which changes the draft-cost side of the speedup trade-off.[^kimi-k3-dspark-card]

## Training

SpecForge online distillation captures hidden states from a frozen Kimi K3 target served by a live SGLang engine; the draft is trained from random initialization rather than fine-tuned from target layers.

- **Loss:** `0.1 CE + 0.9 L1 distillation + 1.0 confidence BCE`, with decay gamma 4.0, 512 sampled anchors per sequence, and `block_size=7`.
- **Topology:** 4 nodes × 4 GB300 (16 ranks) — 2 × TP8 target replicas, DP2 sampler, FSDP16 `SHARD_GRAD_OP` on the draft, and TP-batch scatter.
- **Global batch:** 8 per replica × 32 accumulation steps × 2 replicas = global batch 512.[^kimi-k3-dspark-card]

## Long-context extension

The draft is trained at a 65,536-token context. The published draft config enables YaRN-16 by default with `original_max_position_embeddings=65536` and `max_position_embeddings=1048576`, so 1M-token serving works without a separate draft config override.[^kimi-k3-dspark-card]

## Relationships

- **Extends:** the DFlash parallel-draft backbone with the Markov logit-bias and per-position confidence heads.
- **Drafts for:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md); proposals still require target verification as in [Speculative decoding exact sampling](speculative-decoding-exact-sampling.md).
- **Differs from:** the Kimi K3 report's own EAGLE-3-style draft, which fine-tunes the target's pre-trained multi-token-prediction layer over AttnRes features; DSpark is a separate externally trained parallel-draft checkpoint for the same target.[^kimi-k3-dspark-card]
- **Evaluated by:** [DSpark speculator evaluation and deployment](dspark-speculator-evaluation-and-deployment.md).

## Evidence limits

The model card names the DFlash backbone and the two added heads but does not specify their internal structure, how the Markov condition is applied, or how the confidence head is consumed at runtime. Parameter counts, layer choices, and loss weights are checkpoint-specific and may not generalize to other targets or draft sizes.[^kimi-k3-dspark-card]

[^kimi-k3-dspark-card]: RadixArk, “Kimi K3 DSpark speculator,” Hugging Face model card, [source](../raw/KimiK3DSparkspeculator.md), Overview, Model Specifications, and Training Details.
