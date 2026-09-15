---
type: Concept
title: DeepSeek-V3 FP8 Training and Deployment Systems
description: Fine-grained FP8 mixed precision, DualPipe overlap with custom all-to-all kernels, prefill/decode disaggregation with redundant experts, and hardware suggestions behind 2.788M-H800 training.
tags: [deepseek-v3, fp8, pipeline-parallelism, moe, inference, hardware]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v3-report
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: DeepSeek-V3 Technical Report
  - id: v3-fp8
    resource: ../raw/arXiv-2412.19437v2/content/fp8.tex
    title: DeepSeek-V3 FP8 training section
---

DeepSeek-V3 reaches economical 671B-MoE training through fine-grained FP8 mixed precision, DualPipe pipeline parallelism with near-zero MoE communication overhead, memory savings that avoid tensor parallelism, and separated prefill/decode deployment with redundant experts, totaling a reported 2.788M H800 GPU hours without irrecoverable loss spikes[^v3-report].

## Cluster and training layout

Training uses 2048 NVIDIA H800 GPUs with 8 GPUs per node over NVLink/NVSwitch inside nodes and InfiniBand across nodes[^v3-report].

The HAI-LLM framework uses 16-way pipeline parallelism, 64-way expert parallelism spanning 8 nodes, and ZeRO-1 data parallelism[^v3-report].

Cross-node MoE communication initially gives about a 1:1 computation-to-communication ratio, motivating DualPipe overlap rather than simply adding bandwidth[^v3-report].

## DualPipe

DualPipe overlaps computation and communication within paired forward and backward chunks, addressing heavy cross-node expert-parallel traffic while also reducing pipeline bubbles[^v3-report].

Each chunk is split into attention, all-to-all dispatch, MLP, and all-to-all combine, plus PP communication; backward attention and MLP are further divided into backward-for-input and backward-for-weights in the style of ZeroBubble, and GPU SM allocation between communication and computation is manually tuned[^v3-report].

Full scheduling uses bidirectional pipelining that feeds micro-batches from both ends simultaneously, so much communication is hidden; with a constant computation-to-communication ratio, fine-grained cross-node experts can scale with near-zero all-to-all overhead[^v3-report].

Reported bubble and memory trade-offs are: 1F1B bubbles `(PP-1)(F+B)` with `1x` parameters and `PP` activations; ZB1P bubbles `(PP-1)(F+B-2W)` with the same memory; DualPipe bubbles `(PP/2-1)(F&B+B-3W)` with `2x` parameters and `PP+1` activations, where the extra parameter copy is acceptable under large EP[^v3-report].

DualPipe only requires pipeline stages and micro-batches to be divisible by 2, unlike Chimera's stricter divisibility, and neither bubbles nor activation memory grow as micro-batches increase[^v3-report].

## Cross-node all-to-all kernels

Custom dispatch and combine kernels are co-designed with MoE gating and cluster topology to conserve communication SMs and exploit asymmetric bandwidth: about 160 GB/s NVLink versus 50 GB/s IB, or roughly 3.2x[^v3-report].

Each token goes to at most 4 nodes; it first travels by IB to same-index GPUs on target nodes, then forwards immediately by NVLink to GPUs hosting target experts without waiting for later tokens, overlapping IB and NVLink movement[^v3-report].

This allows an average of 3.2 experts per node without extra NVLink overhead: although V3 activates 8 routed experts, the same communication budget could support up to 13 experts across 4 nodes[^v3-report].

Implementation uses warp specialization over 20 SMs in 10 communication channels: dispatch splits IB sending, IB-to-NVLink forwarding, and NVLink receiving across dynamically sized warp groups, while combining splits NVLink sending, NVLink-to-IB forwarding plus accumulation, and IB receiving plus accumulation; custom PTX and autotuned chunk size curb L2-cache use and interference with compute SMs, and both kernels overlap the compute stream[^v3-report].

## Memory savings

All RMSNorm operations and MLA up-projections are recomputed in back-propagation rather than storing their activations, at minor overhead[^v3-report].

Exponential moving-average parameters for post-decay performance estimation live in CPU memory and update asynchronously after each step, avoiding extra GPU memory or time overhead[^v3-report].

DualPipe places the shallowest layers including embeddings and deepest layers including the output head on the same PP rank, physically sharing parameters and gradients between the MTP module and main model[^v3-report].

Together these measures make it possible to train DeepSeek-V3 without costly tensor parallelism[^v3-report].

## FP8 mixed-precision framework

Most compute-dense GEMMs run in FP8 with BF16 or FP32 outputs; the three Linear GEMMs for forward, activation-backward, and weight-backward all use FP8, theoretically doubling compute speed over BF16 and letting activations persist in FP8 for the backward pass[^v3-fp8].

Higher precision is retained for embeddings, output head, MoE gating, normalization, and attention; master weights and weight gradients stay in FP32 while AdamW first and second moments use BF16 without observed degradation[^v3-fp8].

### Fine-grained quantization

Activations use per-tile `1x128` grouping per token per 128 channels, while weights use per-block `128x128` grouping per 128 input by 128 output channels, adapting scale to smaller groups so outliers do not force whole-tensor overflow or underflow[^v3-fp8].

This aligns with microscaling ideas and anticipates Blackwell support for smaller-granularity microscaling formats[^v3-fp8].

### Accumulation precision

Hopper FP8 Tensor Cores retain only about 14 bits in accumulation, far below FP32; at inner dimension 4096 the paper reports nearly 2% maximum relative error in a random-matrix test, a default limitation in some FP8 frameworks[^v3-fp8].

DeepSeek-V3 promotes partial MMA results to FP32 registers on CUDA cores every `N_C=128` elements, equivalent to 4 WGMMAs, where full-precision accumulation and per-group dequantization occur with minimal extra cost; concurrent WGMMAs overlap promotion and MMA to preserve Tensor Core utilization[^v3-fp8].

### Format and online scaling

All tensors use E4M3 rather than hybrid E4M3-forward plus E5M2-backward, favoring mantissa precision; feasibility is attributed to tile- and block-wise sharing of exponent range[^v3-fp8].

Scales are computed online from each tile or block's maximum absolute value rather than using delayed history-based quantization[^v3-fp8].

### Low-precision storage and communication

Attention-following Linear inputs use a custom E5M6 format because they are reused by precision-sensitive attention backward; their scales are powers of two so `1x128` forward tiles can convert to `128x1` backward tiles without extra quantization error[^v3-fp8].

MoE SwiGLU inputs are cached in FP8 and their outputs recomputed backward; MoE up-projection dispatch is FP8-quantized with power-of-two scales, activation gradients before MoE down-projections are handled similarly, and forward/backward combines remain BF16 to protect critical precision[^v3-fp8].

Validation on roughly 16B-parameter models over about 1T tokens and roughly 230B-parameter models over about 0.9T tokens keeps relative loss error below 0.25% versus BF16, within training randomness[^v3-fp8].

Block-wise quantization of activation gradients diverges on a roughly 16B MoE after about 300B tokens because token-imbalanced, token-correlated outliers propagate chain-like through `Dgrad`; this is why forward and backward activation groupings differ[^v3-fp8].

## Inference deployment

Deployment runs on H800 clusters with NVLink inside nodes and full IB connectivity, separating prefill and decode to meet online SLOs while sustaining throughput[^v3-report].

### Prefill

The minimum prefill unit is 4 nodes and 32 GPUs: attention uses 4-way tensor parallelism with sequence parallelism plus 8-way data parallelism, MoE uses 32-way expert parallelism for large per-expert batches, and shallow dense MLPs use 1-way tensor parallelism to save communication[^v3-report].

Load balance uses periodically refreshed redundant experts, about every 10 minutes from online statistics: 32 redundant experts for prefill, so each GPU hosts its original 8 experts plus one redundant copy, rearranged within nodes without raising cross-node all-to-all traffic[^v3-report].

Two computationally similar micro-batches run together, overlapping one micro-batch's attention and MoE with the other's dispatch and combine[^v3-report].

An explored dynamic-redundancy variant hosts more experts per GPU, for example 16 hosted with 9 active per step, computing a globally optimal routing plan before each layer's all-to-all; the overhead is negligible against heavy prefill compute[^v3-report].

### Decode

The shared expert is treated as a routed expert during decoding, so each token effectively selects 9 experts with the shared expert always chosen as a heavy-load member[^v3-report].

The minimum decode unit is 40 nodes and 320 GPUs: attention uses TP4 with sequence parallelism plus DP80, MoE uses EP320 with one expert per GPU, and 64 GPUs cover redundant plus shared experts[^v3-report].

Dispatch and combine use direct point-to-point IB transfers plus IBGDA for low latency; redundant experts are refreshed periodically from online load but no rearrangement is needed because each GPU holds one expert[^v3-report].

Decode also explores two-micro-batch overlap, pairing one micro-batch's attention with another's dispatch-plus-MoE-plus-combine; because decode MoE batches are small, usually within 256 tokens, and memory-access bound with only one expert's parameters loaded, only a small SM share goes to MoE to protect attention speed[^v3-report].

End-to-end generation is reported at more than twice DeepSeek-V2 speed, with further headroom remaining[^v3-report].

## Hardware suggestions

Communication hardware should offload IB/NVLink forwarding, RDMA-buffer transport, all-to-all-combine reductions, and fine-grained multi-expert layout from SMs into a GPU or network co-processor in the style of NVIDIA SHARP, unifying scale-out IB and scale-up NVLink behind simple read, write, multicast, and reduce primitives[^v3-report].

Compute hardware should provide higher FP8 GEMM accumulation precision, at least 14-bit parallel addition with FP32 register accumulation and ideally movement toward full FP32; native tile- and block-wise quantization with group scaling inside Tensor Cores; fused FP8-cast plus TMA access, warp-level cast, or near-HBM casting to avoid repeated HBM traffic; and direct transposed shared-memory reads before MMA to simplify the `1x128` forward versus `128x1` backward workflow[^v3-report].

## Cost and stability

The paper reports 2664K H800 hours for pretraining, 119K for context extension, and 5K for post-training, totaling 2.788M H800 hours or about $5.576M at $2 per GPU hour[^v3-report].

Per trillion pretraining tokens costs about 180K H800 hours, or about 3.7 days on 2048 H800 GPUs, putting official pretraining under two months; these figures cover only official V3 training, excluding earlier architecture, algorithm, and data research plus ablations[^v3-report].

Training is reported as remarkably stable with no irrecoverable loss spikes or rollbacks; checkpoints are published at `github.com/deepseek-ai/DeepSeek-V3`[^v3-report].

Acknowledged deployment limits are a relatively large recommended deployment unit that can burden small teams and remaining inference-speed headroom despite the greater-than-2x gain over V2; future work points to more efficient architectures toward very long or infinite context, possibly beyond Transformers, more and better data plus extra training signals, deeper thinking through longer reasoning, and broader multi-dimensional evaluation to avoid overfitting fixed benchmarks[^v3-report].

## Relationships

- Related to [DeepSeek-V3 Architecture and Evaluation](deepseek-v3-architecture.md) — model, data, post-training, and benchmark counterpart to these training and serving systems.
- Related to [SGLang Expert Parallelism](sglang-expert-parallelism.md) — expert-parallel serving context using DeepEP dispatch and DeepGEMM compute for DeepSeek-V3-class MoE.
- Related to [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — EP sharding, all-to-all, and rebalancing context relevant to V3's 64-way EP and redundant-expert load balancing.
- Related to [SGLang Quantization](sglang-quantization.md) — already-FP8 DeepSeek-V3/R1 loading context relevant to V3's fine-grained FP8 training and storage choices.
- Related to [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — format and hardware-target context for FP8-trained MoE deployment.
- Related to [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — prefill/decode separation context for V3's disaggregated prefill and decode deployment units.

## Coverage limits

- PDF figures under `raw/arXiv-2412.19437v2/figures/` were not visually inspected; DualPipe, FP8-framework, overlap, and NIAH claims follow LaTeX prose, equations, tables, and captions.
- Cost arithmetic assumes the paper's $2 per H800-hour rental price and official-training scope; independent hardware, utilization, and price validation is out of scope.
- FP8 loss-error bounds are paper-reported comparisons on 16B- and 230B-scale baselines, not an independent reproduction at 671B scale.
