---
type: Concept
title: PyTorch DDP gradient synchronization
description: PyTorch 1.5 DistributedDataParallel maintains replica consistency by synchronizing gradient buckets during backward hooks, trading bucket coalescing against early communication overlap.
tags: [pytorch, distributed-training, data-parallelism, allreduce, gradient-synchronization]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T14:43:10Z }
sources:
  - id: pytorch-ddp-2020
    resource: ../raw/arXiv-2006.15704v1/main.tex
    title: "PyTorch Distributed: Experiences on Accelerating Data Parallel Training"
---

# PyTorch DDP gradient synchronization

PyTorch 1.5 `DistributedDataParallel` (DDP) maintains replicas by starting from identical parameters and averaging gradients across processes before independent optimizer steps. It packs gradients into ordered buckets and launches asynchronous `AllReduce` as each bucket becomes ready during backpropagation, so communication can overlap computation.[^pytorch-ddp-2020]

## Correctness and interface

DDP wraps a local `nn.Module` and intercepts its forward and autograd execution rather than requiring an explicit synchronization call between `backward()` and `step()`. At construction, rank 0 broadcasts model state; each process then uses the synchronized gradients after every backward pass. This is gradient synchronization, not parameter averaging after local optimizer updates: the paper argues the latter is not generally mathematically equivalent to processing the combined data, especially with optimizer state such as momentum.[^pytorch-ddp-2020]

The described design is a synchronous, intra-iteration data-parallel system. `AllReduce` requires all participants to issue matching operations in the same order, which makes ready-gradient order a correctness constraint as well as a scheduling concern.[^pytorch-ddp-2020]

## Bucketed reduction

DDP maps same-device parameter gradients into buckets, copies ready gradients into their bucket, `AllReduce`s and averages each bucket, then copies results back to `.grad`. A post-hook on every parameter’s gradient accumulator decrements that bucket’s pending-gradient count; the last ready gradient triggers its asynchronous reduction. Coalescing small gradients improves collective throughput, but a larger bucket delays its first reduction and can reduce computation–communication overlap.[^pytorch-ddp-2020]

To keep collective ordering consistent despite dynamically constructed autograd graphs, the PyTorch 1.5 implementation assigns buckets in reverse `model.parameters()` order and only launches ready buckets in that fixed order. This is an engineering approximation: it assumes parameter registration roughly follows forward execution, so reversing it approximates backward readiness; it is not a guaranteed optimal schedule.[^pytorch-ddp-2020]

## Dynamic graphs and accumulation

An iteration can omit parameters. With unused-parameter detection enabled, DDP traverses the autograd graph from forward outputs, marks locally absent parameters ready so buckets do not stall, and uses an additional `AllReduce` bitmap to identify globally unused parameters before preserving their absence. The extra collective is paid only when the application requests unused-parameter detection.[^pytorch-ddp-2020]

The `no_sync` context disables DDP synchronization hooks for intermediate microbatches and synchronizes their accumulated gradients on the next backward pass outside the context. This can reproduce a larger-batch gradient when the accumulation and optimizer boundary are configured accordingly; using skipped synchronization across optimizer updates instead changes the training dynamics and requires empirical convergence validation.[^pytorch-ddp-2020]

## Historical scope

This describes the paper’s PyTorch v1.5.0 implementation, not a guarantee about current DDP internals or APIs. The paper also describes NCCL, Gloo, and MPI through a common `ProcessGroup` interface, including a then-available round-robin composite process group; backend capabilities and recommended configurations may have changed.[^pytorch-ddp-2020]

## Relationships

- **Underlies:** [OPT distributed training operations and transparency](opt-distributed-training-operations-and-transparency.md), whose reported run combines sharded data parallelism with tensor parallelism.
- **Contrasts with:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md); DDP replicates full dense model state and reduces gradients, whereas expert parallelism dispatches selected tokens to sharded experts.
- **Evaluated by:** [PyTorch DDP performance tuning](pytorch-ddp-performance-tuning.md), which records the paper’s configuration-dependent bucket, backend, scaling, and `no_sync` results.

[^pytorch-ddp-2020]: Li et al., “PyTorch Distributed: Experiences on Accelerating Data Parallel Training,” arXiv:2006.15704v1 (2020), [source](../raw/arXiv-2006.15704v1/main.tex), Sections 2–4.
