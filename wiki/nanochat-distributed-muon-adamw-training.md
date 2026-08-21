---
type: Concept
title: nanochat distributed Muon–AdamW training
description: nanochat trains hidden-layer matrices with a fused Muon variant and other parameters with fused AdamW, integrating gradient synchronization and ZeRO-2-style optimizer-state sharding without PyTorch DDP.
tags: [nanochat, muon, adamw, distributed-training, zero-2, scaling-laws]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:55:51Z }
sources:
  - id: nanochat-optim
    resource: ../raw/nanochat/nanochat/optim.py
    title: nanochat combined Muon–AdamW optimizer
  - id: nanochat-gpt
    resource: ../raw/nanochat/nanochat/gpt.py
    title: nanochat GPT implementation
  - id: nanochat-base-train
    resource: ../raw/nanochat/scripts/base_train.py
    title: nanochat base-model training script
---

# nanochat distributed Muon–AdamW training

nanochat puts hidden-layer matrices into a fused Muon path and embeddings, value embeddings, the LM head, and learned scalars into fused AdamW groups. The optimizer itself synchronizes gradients and shards large optimizer states across ranks, so multi-GPU training initializes `torch.distributed` but does not wrap the model in PyTorch DDP.[^nanochat-optim][^nanochat-gpt]

## Hybrid parameter treatment

The model groups all Transformer-block parameters by matrix shape for Muon. It assigns AdamW separately to the token embedding, value embeddings, LM head, residual/input-blend scalars, and smear/backout parameters, with group-specific learning rates, betas, epsilon, and decay. AdamW learning rates scale as $1/\sqrt{d_{model}/768}$.[^nanochat-gpt]

The Muon kernel applies Nesterov momentum, row equilibration, five Polar Express polynomial iterations, Frobenius renormalization, and a factored per-row or per-column second moment before a cautious parameter update. These are nanochat-specific extensions; they should not be treated as the universal Muon algorithm.[^nanochat-optim]

## Distributed update path

For large AdamW tensors, each rank receives a gradient slice through `reduce_scatter`, updates only its parameter slice and sharded first/second moments, then reconstructs the parameter with `all_gather`. Parameters below 1,024 elements use all-reduce and replicated state.[^nanochat-optim]

Muon parameters of equal shape are stacked, padded across ranks when necessary, reduced-scattered by parameter chunk, updated by their owning rank, and all-gathered. Communication follows three phases: launch all reductions asynchronously; wait group by group, compute updates, and launch gathers; then finish gathers and copy stacked Muon weights back. On one rank these paths reduce to local full-tensor updates.[^nanochat-optim]

This is ZeRO-2-style state and gradient sharding, not model-parameter sharding: every rank receives the complete updated model after each step.[^nanochat-optim]

## Depth-derived training schedule

The base trainer uses depth as the primary scale control. It computes a target token horizon from a configurable token-to-scaling-parameter ratio, estimates an optimal global batch from a depth-12 reference with $B \propto D^{0.383}$, and adjusts learning rates and weight decay from those derived quantities.[^nanochat-base-train]

These extrapolations mix measured project defaults with explicit assumptions. In particular, the script says its square-root batch learning-rate rule and AdamW-derived weight-decay theory are not carefully established for Muon. They are experiment policy, not validated universal scaling laws.[^nanochat-base-train]

The loop uses gradient accumulation to reach the global token batch, explicit BF16/FP32 or scaled FP16 computation, linear warmup/plateau/warmdown, scheduled Muon momentum, cosine Muon weight-decay decay, resumable data/checkpoint state, validation bits per byte, CORE evaluation, sampling, and MFU logging.[^nanochat-base-train]

## Relationships

- **Implements:** a concrete extension of [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md).
- **Trains:** [nanochat modern GPT reference implementation](nanochat-modern-gpt-reference-implementation.md).
- **Contrasts with:** [PyTorch DDP gradient synchronization](pytorch-ddp-gradient-synchronization.md), because synchronization is optimizer-integrated rather than driven by DDP backward hooks.
- **Uses as heuristic context:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md), while retaining a configurable project-measured token ratio.

[^nanochat-optim]: nanochat contributors, [combined Muon–AdamW optimizer](../raw/nanochat/nanochat/optim.py), fused kernels, parameter ownership, communication phases, and state sharding.
[^nanochat-gpt]: nanochat contributors, [GPT implementation](../raw/nanochat/nanochat/gpt.py), parameter groups and optimizer hyperparameters.
[^nanochat-base-train]: nanochat contributors, [base-model training script](../raw/nanochat/scripts/base_train.py), depth sizing, scaling assumptions, schedules, distributed loop, evaluation, and checkpointing.
