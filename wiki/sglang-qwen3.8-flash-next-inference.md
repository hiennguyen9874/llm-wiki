---
type: Concept
title: SGLang Qwen3.8-Flash-Next Inference
description: Day-0 SGLang serving for Qwen3.8-Flash-Next 125B MoE with GDN plus QSA sparse attention, gated residual, PLE host offload, IndexShare MTP, and fused kernels.
tags: [sglang, qwen3.8-flash-next, qwen4, gdn, qsa, sparse-attention, moe, nvfp4, speculative-decoding, quantization]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: qwen38-flash-next-day0
    resource: ../raw/2026-08-26-qwen-flash-next/index.md
    title: 'Qwen3.8-Flash-Next: Day-0 Support in SGLang'
---

SGLang provides day-0 support for Qwen3.8-Flash-Next in collaboration with Qwen, NVIDIA, and AMD, covering a 125B-parameter multimodal MoE plus 51B N-gram embedding with GDN plus QSA hybrid attention, 4-branch gated residual, host-offloaded per-layer embeddings, Radix-Cache-compatible sparse KV management, and IndexShare MTP speculative decoding[^qwen38-flash-next-day0].

## Model identity

- `Qwen3.8-Flash-Next`: multimodal MoE model and early preview of the Qwen4 architecture; plays the same role for Qwen4 that Qwen3-Next played for Qwen3.5[^qwen38-flash-next-day0].
- Continues the Gated DeltaNet plus Gated Attention hybrid design used from Qwen3.5 through Qwen3.8[^qwen38-flash-next-day0].
- Hybrid architecture: 125B-parameter main model plus additional 51B N-gram Embedding, with 6B parameters activated per token; 48 layers total with 36 GDN linear-attention layers and 12 QSA sparse-attention layers; MoE layers use 512 experts with top-10 routing[^qwen38-flash-next-day0].
- Day-0 NVFP4 checkpoint: [RadixArk/Qwen3.8-Flash-Next-NVFP4](https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4)[^qwen38-flash-next-day0].
- Architecture upgrades over prior hybrids: GDN plus QSA hybrid attention, Gated Residual widening, and N-gram Embedding local-pattern memory[^qwen38-flash-next-day0].
- Launch commands and per-workload configuration guidance live in the [SGLang Cookbook](https://docs.sglang.io/cookbook/autoregressive/Qwen/Qwen3.8-Flash-Next)[^qwen38-flash-next-day0].

## GDN plus QSA hybrid architecture

- Out of every 4 layers, 3 GDN layers compress history into fixed-size state while the remaining layer performs precise retrieval over the full context[^qwen38-flash-next-day0].
- QSA addresses the growth of both computation and KV-cache memory-access cost with context length by attending only to important context[^qwen38-flash-next-day0].
- QSA aggregates the sequence into micro-blocks, estimates importance at block level, then selects the most relevant regions, reducing indexing overhead and attention cost together[^qwen38-flash-next-day0].
- Gated Residual combines Hyper-Connection multi-branch residuals with GatedNorm-style element-wise dynamic gating: the single residual stream is expanded into 4 parallel branches, with dynamic per-content control of how much to read from each branch and write back[^qwen38-flash-next-day0].
- N-gram Embedding performs lookups from local context of current token plus several preceding tokens, adding representations for common phrases and local patterns with almost no per-token compute; the model uses only a single N-gram layer near the start of the network[^qwen38-flash-next-day0].

## Qwen Sparse Attention: retrieve coarsely, attend precisely

Qwen3.8-Flash-Next uses compressed QSA with compression ratio 4 (`c4`): a lightweight indexer decides where to look while sparse GQA reads selected entries from the original attention K/V cache[^qwen38-flash-next-day0].

- Indexer projects four 128-dimensional query heads and one shared key head[^qwen38-flash-next-day0].
- Every four raw index keys are averaged in FP32, normalized, and rotated with the first token's MRoPE position to form one compressed key[^qwen38-flash-next-day0].
- A query scores visible compressed blocks with:

$$
s_{t,b} = \frac{1}{\sqrt{128}}
\sum_{h=1}^{4}
\mathrm{ReLU}
\left(\left\langle q^I_{t,h}, \bar{k}^I_b \right\rangle\right).
$$

- QSA keeps the best 512 blocks, expands them back to 2048 logical token positions, and appends the zero-to-three tokens in the current incomplete block; final sparse attention therefore sees at most 2051 positions[^qwen38-flash-next-day0].
- Compressed keys are only an index: final softmax and value aggregation use the original, uncompressed K/V[^qwen38-flash-next-day0].
- This trades a small amount of cache capacity for much lower long-context compute and memory traffic: the indexer scans roughly `L/4` small keys, then sparse attention reads about 2K full K/V entries instead of all `L`[^qwen38-flash-next-day0].
- Model-level KV saving comes from the hybrid layout — only 12 of 48 layers store growing attention K/V while the other 36 GDN layers use fixed-size state — not from discarding K/V inside a QSA layer[^qwen38-flash-next-day0].

SGLang implementation[^qwen38-flash-next-day0]:

- Attaches the indexer only to full-attention layers and reuses their MRoPE implementation; original K/V stays in the normal paged pool[^qwen38-flash-next-day0].
- Adds one BF16 compressed index key per four tokens; raw keys for the unfinished block live in a four-slot per-request ring, avoiding retention of raw index keys for the full context and reducing QSA index-cache overhead by 80%[^qwen38-flash-next-day0].
- Page-aligned `full_slot / 4` addressing lets the compressed cache follow Radix Cache ownership without a separate lifecycle[^qwen38-flash-next-day0].
- Prefill uses a custom GPU kernel for index scores, fast top-k selection, and Triton expansion plus sparse GQA; decode uses a paged scorer, compacts selected original K/V, and dispatches to TRTLLM-Gen on Blackwell or packed FlashAttention otherwise[^qwen38-flash-next-day0].
- The indexer can overlap the main Q/K/V projection on a second CUDA stream, and metadata paths are CUDA-graph compatible[^qwen38-flash-next-day0].

## IndexShare MTP: reusing QSA selection across draft steps

A QSA layer runs an indexer that picks which tokens to attend, then sparse attention over exactly those tokens; the second stage has a fixed token budget while the first scores its query against all `ceil(L/4)` compressed blocks, so beyond a few thousand tokens the indexer sets the layer cost[^qwen38-flash-next-day0].

- Speculative decoding multiplies that cost: with `--speculative-num-steps N`, one MTP iteration spends `N` indexer invocations (`N-1` draft-decode forwards plus one draft-extend) to advance the draft by at most `N` positions[^qwen38-flash-next-day0].
- Fix: draft-decode steps stop running the indexer altogether[^qwen38-flash-next-day0].
- Every MTP iteration opens with a draft-extend over tokens the target just accepted, and that pass runs the indexer anyway; each request's last accepted row is captured there and reused by the whole draft loop, with `N+1` extra columns filled at lookup with positions drafted since capture, so the draft still sees its own in-flight tokens[^qwen38-flash-next-day0].
- The selection is a list of logical token indices and a request only ever grows, so it can never go out of range; because the query has moved by at most `N` positions out of `L`, the reused ranking is essentially the one the indexer would have recomputed, leaving accept length unchanged[^qwen38-flash-next-day0].
- Draft indexer work per MTP iteration drops from `N` invocations to one; small metadata kernels that exist only to feed it, including the compressed decode view and pending-ring and group-ring layouts, are removed from the draft-decode step[^qwen38-flash-next-day0].
- Reported rate: at TP4 on B200, the NVFP4 checkpoint decodes at 540 tok/s for batch size 1 with MTP at accept length 3.3 including the bonus token[^qwen38-flash-next-day0].

## HyperConnection kernel optimizations

HyperConnection maintains four parallel residual streams while Attention and MoE operate on a single hidden state; each block uses Mix to read from the four streams and Combine to write back[^qwen38-flash-next-day0].

- `M` is tokens processed by one call: small during decode and speculative verification but can reach thousands during prefill; SGLang dispatches to different kernels by `M`[^qwen38-flash-next-day0].

### Mix

Mix uses a low-rank projection to generate element-wise gates and reduce four residual streams into one hidden state[^qwen38-flash-next-day0].

- For `M <= 16`, uses the low-latency split-K CuTe GEMM from [FlashInfer PR #4266](https://github.com/flashinfer-ai/flashinfer/pull/4266): Split-K partitions the K dimension so multiple CTAs process the same output region in parallel, compensating for limited M-dimension parallelism[^qwen38-flash-next-day0].
- SiLU, Sigmoid, gating, and final reduction are fused into the two GEMM epilogues, avoiding intermediate global-memory writes; up-projection weights are reordered offline so four gate values per output reduce locally inside a tile[^qwen38-flash-next-day0].
- For larger `M`, uses cuBLAS[^qwen38-flash-next-day0].
- On B300 at `M=4`, fused path reduces Mix latency from 12.36 to 6.03 µs, a 2.05x kernel-level speedup; end-to-end speculative-decode benchmark against the previous Triton path improves throughput by 7.6%[^qwen38-flash-next-day0].

### Combine

Combine computes four injection coefficients and applies a residual update to the four streams[^qwen38-flash-next-day0].

- For large `M`, one fused kernel processes each token row in a single pass[^qwen38-flash-next-day0].
- At small `M`, one-CTA-per-row exposes too few CTAs, so the `M <= 32` path splits each row along the hidden dimension; the two-kernel implementation preserves reference FP32 accumulation order and bitwise-identical outputs[^qwen38-flash-next-day0].
- At `M=4`, split path reduces Combine latency from 4.17 to 2.13 µs, a 1.96x kernel-level speedup; separate end-to-end benchmark against the original one-CTA-per-row kernel improves throughput by 5.49%[^qwen38-flash-next-day0].
- For large `M`, the fused kernel is up to 2.54x faster than the cuBLAS baseline and reaches 6144 GB/s effective bandwidth[^qwen38-flash-next-day0].
- Shape-aware dispatch covers both low-latency decode and large-scale prefill[^qwen38-flash-next-day0].

## Per-layer embeddings

### Architecture

This model places PLE, a hash-addressed learned N-gram embedding memory, at the second decoder block (configured layer ID 2, zero-based index 1); its 51.2B embedding parameters, about 95.4 GiB in BF16, are fixed model weights rather than KV cache or mutable attention memory[^qwen38-flash-next-day0].

- For token `x_t`, eight 2-gram hash heads use `(x_{t-1}, x_t)` and eight 3-gram hash heads use `(x_{t-2}, x_{t-1}, x_t)`, producing 16 embedding row IDs; each row contributes 160 values concatenated into `E_t` with shape `[2560]`[^qwen38-flash-next-day0].

$$
E_t \in \mathbb{R}^{2560}
\longrightarrow
K_t \in \mathbb{R}^{4 \times 2560},
\qquad
V_t \in \mathbb{R}^{2560}
$$

$$
R_t \in \mathbb{R}^{4 \times 2560}
\longrightarrow
Q_t \in \mathbb{R}^{4 \times 2560}
$$

$$
g_t = \mathrm{Gate}(\mathrm{Norm}(Q_t), \mathrm{Norm}(K_t))
\in \mathbb{R}^{4 \times 1},
\qquad
U_t = g_t \odot V_t
$$

$$
\Delta_t = U_t + \mathrm{SiLU}(\mathrm{DWConv}(\mathrm{RMSNorm}(U_t)))
$$

$$
\widetilde{R}_t = R_t + \Delta_t,
\qquad
\widetilde{R}_t \xrightarrow{\mathrm{HC\ Mix}} h_t \in \mathbb{R}^{2560}
$$

- The fourth line forms the PLE delta by adding the gated value to its short-conv output; the fifth injects that delta into the HC state[^qwen38-flash-next-day0].
- PLE keeps two request-local states: the two recent token IDs used for hashing and a short-conv history of shape `[10240, 9]`[^qwen38-flash-next-day0].
- Target model retains PLE during prefill, decode, and target verification; only the one-layer MTP draft model disables it[^qwen38-flash-next-day0].

### Sparse pinned-host offload

Because each token touches only 16 rows, SGLang keeps each rank's vocabulary-parallel table shard in pinned host memory and gathers selected rows into a small BF16 GPU buffer with a Triton UVA kernel; a dedicated CUDA stream overlaps the gather with the first decoder block[^qwen38-flash-next-day0].

- Existing TP reduction and DP gather/scatter paths are preserved: offload changes storage location, not table ownership or PLE math[^qwen38-flash-next-day0].
- This CUDA path is enabled by default when the effective model dtype is BF16 and remains separate from KV-cache or generic layer offload[^qwen38-flash-next-day0].
- On H200 with TP4 and MTP-213 (2 draft steps, top-k 1, 3 draft tokens per target verification), offload reduced target-model weights from 83.91 to 60.45 GiB per GPU (-23.46 GiB) and increased allocated KV capacity from 1.84M to 3.28M tokens (+78.54%) at the same memory fraction[^qwen38-flash-next-day0].
- With 1, 2, and 4 concurrent requests, matched throughput was effectively unchanged (-0.07% geometric mean); four fixed prompts with 128 generated tokens each matched exactly in output IDs, and the recorded chosen-token logprob trace for the first case also matched exactly[^qwen38-flash-next-day0].

## Relationships

- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — IndexShare MTP reusing the draft-extend QSA top-k across draft-decode steps to cut draft indexer work from N to one invocation per MTP iteration.
- Uses [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — GDN plus QSA KV management with page-aligned compressed-index ownership following Radix Cache without a separate lifecycle.
- Uses [SGLang Quantization](sglang-quantization.md) — day-0 `RadixArk/Qwen3.8-Flash-Next-NVFP4` checkpoint context for the 512-expert top-10 MoE.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — prior Qwen3.8-2.4T-A95B day-0 stack with 69-GDN/23-GQA plus ReplaySSM, here replaced by 36-GDN/12-QSA plus QSA IndexShare, gated residual, and PLE offload for the Qwen4-preview Flash-Next identity.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — same 125B MoE plus 51B N-gram identity served here at datacenter scale rather than via local GGUF runs.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) — QSA indexer plus TRTLLM-Gen/FlashAttention sparse-GQA execution with second-stream overlap and CUDA-graph-compatible metadata.
- Related to [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) — authoritative tech-report design, ablations, and base evaluation for this serving stack.
- Related to [Qwen3.8-Flash-Next Training and Stability](qwen3.8-flash-next-training.md) — Muon, scaling, and stability recipe behind the served checkpoint.
- Related to [Qwen3.8-Flash-Next HF Release and Serving](qwen3.8-flash-next-hf-release.md) — official HF model card, Qwen4Exp config and code, thinking controls, YaRN extension, and post-trained benchmarks behind this serving stack.

## Coverage limits

- Three local SVG diagrams were inspected as SVG text: architecture block layout with 3x GDN plus 1x QSA/MoE repetition, PLE, and QSA-indexer internals; QSA index-plus-attention dataflow with c4 compression, top-512/2051-token expansion, and prefill/decode paths; and PLE model-plus-offload lanes with pinned-host shard, Triton UVA gather, and H200 memory/throughput metrics[^qwen38-flash-next-day0].
- Cookbook launch commands, FlashInfer/SGLang PR diffs, Hugging Face NVFP4 checkpoint contents, and prior Qwen3-Next/Qwen3.5 references were cited as identifiers without independent inspection[^qwen38-flash-next-day0].
- Throughput, latency, speedup, bandwidth, memory-saving, KV-capacity, and exact-match figures are day-0 source-reported snapshots on the stated B200/B300/H200 setups, not independently verified or universal defaults[^qwen38-flash-next-day0].

[^qwen38-flash-next-day0]: Qwen3.8-Flash-Next: Day-0 Support in SGLang — `../raw/2026-08-26-qwen-flash-next/index.md`, covering 125B-plus-51B 48-layer 36-GDN/12-QSA plus 512-expert top-10 identity with NVFP4 checkpoint, c4 QSA scoring with top-512/2051-token selection and paged Radix-compatible index cache, IndexShare MTP QSA reuse with 540 tok/s TP4 B200 batch-1 rate, 4-branch Mix/Combine HyperConnection kernels with 2.05x/1.96x speedups, single-layer PLE with 16-row gather and pinned-host offload saving 23.46 GiB/GPU and gaining 78.54% KV capacity at unchanged throughput with exact output match, and cookbook plus collaboration context.
