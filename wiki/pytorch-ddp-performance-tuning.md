---
type: Concept
title: PyTorch DDP performance tuning
description: PyTorch 1.5 DDP measurements show that bucket sizing, backend bandwidth, overlap, and synchronization frequency can materially alter scale-out throughput, with no universal configuration.
tags: [pytorch, distributed-training, data-parallelism, performance-tuning, allreduce]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T14:43:10Z }
sources:
  - id: pytorch-ddp-2020
    resource: ../raw/arXiv-2006.15704v1/main.tex
    title: "PyTorch Distributed: Experiences on Accelerating Data Parallel Training"
---

# PyTorch DDP performance tuning

In PyTorch 1.5 DDP, scaling efficiency depends on fitting gradient-bucket scheduling to model, backend, and network properties. The paper’s ResNet50 and BERT experiments find NCCL substantially faster than Gloo in its test configurations; overlap, an intermediate bucket size, and—in suitable training regimes—less frequent synchronization reduce amortized communication cost.[^pytorch-ddp-2020]

## Tune bucket size empirically

Small buckets start `AllReduce` early but incur more collective-launch overhead; large buckets improve coalescing but wait longer for gradients and leave less backward computation to hide communication. The implementation’s default was 25 MB, but the paper explicitly rejects a universal optimum. On 16 GPUs, it reports ResNet50’s best NCCL range around 10–25 MB and BERT’s best NCCL result at 50 MB; under Gloo, 5 MB was best for both workloads in those measurements.[^pytorch-ddp-2020]

The source attributes the backend difference to its observed collective curves: Gloo’s total `AllReduce` time flattened beyond roughly 512 KB in the tested setup, so larger buckets added readiness delay without comparable collective benefit. These are workload-, hardware-, and software-version-specific observations, not backend-wide thresholds.[^pytorch-ddp-2020]

## Overlap and backend effects

On 32 GPUs across four machines, overlapping asynchronous bucket reduction with backward computation improved the paper’s ResNet50/BERT iteration speed by 38.0%/35.2% with NCCL and 26.8%/21.5% with Gloo, relative to its non-overlapping configurations. The reported gain is largest when communication and computation take comparable time; when one dominates, less of it can be hidden.[^pytorch-ddp-2020]

At up to 256 GPUs in a shared entitlement, the paper reports that ResNet50 with NCCL had a twofold per-iteration latency increase over local training, equivalent to 128× throughput scaling under its fixed per-GPU workload. Gloo slowed about 3× for ResNet50 and 6× for BERT at that scale. The authors flag variable machine and network placement in the shared environment and suspect congestion or slow links for several anomalous points, so these figures are not controlled hardware limits.[^pytorch-ddp-2020]

## Reduce synchronization only with convergence checks

For ResNet50 at 256 GPUs, synchronizing every eighth iteration reduced reported average iteration latency by 38% with NCCL and 57% with Gloo. In an MNIST experiment with batch size 8 and learning rate 0.02, the paper found only negligible convergence degradation; with batch size 256 and learning rate 0.06, it reports worse final loss. Accumulating more unsynchronized gradients changes the effective update regime, so learning rate, batch construction, and quality must be evaluated together rather than assuming a speedup is free.[^pytorch-ddp-2020]

The paper also evaluates a round-robin composite of multiple process groups to work around a single backend group’s concurrency limits. Its BERT/NCCL measurement reports a 33% speedup from three versus one process group on 16 GPUs, whereas small ResNet50/NCCL differences were negligible. This is historical evidence for a backend-saturation diagnosis, not a recommendation to use that PyTorch-1.5 feature in current deployments.[^pytorch-ddp-2020]

## Practical diagnosis

- Prefer the backend and topology that provide the available collective bandwidth; the paper recommends NCCL when it is available in its GPU settings.[^pytorch-ddp-2020]
- Benchmark intermediate bucket caps on the actual model and scale-out topology rather than extrapolating a reported optimum.[^pytorch-ddp-2020]
- Inspect backward time and communication overlap first: the paper finds gradient synchronization dominates more as the evaluated model grows.[^pytorch-ddp-2020]
- Treat cross-machine links and stragglers as first-class constraints. Keeping a DDP group within one machine can be preferable when inter-machine bandwidth is much lower.[^pytorch-ddp-2020]

## Relationships

- **Evaluates:** [PyTorch DDP gradient synchronization](pytorch-ddp-gradient-synchronization.md) under the paper’s ResNet50 and BERT configurations.
- **Related to:** [OPT distributed training operations and transparency](opt-distributed-training-operations-and-transparency.md); both concern scale-out training, but OPT reports a later sharded-and-tensor-parallel run rather than these replicated-DDP benchmarks.

[^pytorch-ddp-2020]: Li et al., “PyTorch Distributed: Experiences on Accelerating Data Parallel Training,” arXiv:2006.15704v1 (2020), [source](../raw/arXiv-2006.15704v1/main.tex), Sections 4–6 and Figures 3–7.
