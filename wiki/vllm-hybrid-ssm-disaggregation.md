---
type: Concept
title: vLLM Hybrid SSM Disaggregated Serving
description: NIXL dual-descriptor, physical-logical bridging, and 3-descriptor conv transfer for hybrid Mamba-attention prefill/decode disaggregation.
tags: [vllm, disaggregated-prefill, hybrid-models, mamba, nixl, kv-cache]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T00:00:00Z }
sources:
  - id: hybrid-ssm-disagg
    resource: ../raw/2026-04-21-hybrid-ssm-disagg/index.md
    title: Disaggregated Serving for Hybrid SSM Models in vLLM
---

vLLM extends NIXL prefill/decode disaggregation to hybrid SSM-attention models (for example NVIDIA Nemotron-H) with dual FA/Mamba descriptor views over shared HMA tensors, FA-only physical/logical block expansion, and DS-layout 3-descriptor conv transfer, available additively in `vllm>=v0.20.0` without changing dense-transformer behavior[^hybrid-ssm-disagg].

## Background: NIXL KV transfer for dense models

For standard transformers the workflow is register KV regions for RDMA, create per-block `(address, length, device_id)` descriptors, handshake once per P-D pair (agent handles, block counts, lengths), then decode maps `block_id -> descriptor_id`, issues RDMA READ, and polls[^hybrid-ssm-disagg].

For `M` regions and `N` blocks the list is `M x N` with index `region_id * N + block_id`[^hybrid-ssm-disagg].

## Why hybrid models break the uniform scheme

- Full-attention layers use uniform per-token KV: `[num_blocks, 2, block_size, num_kv_heads, head_dim]` with shared block size and page size[^hybrid-ssm-disagg].
- Mamba layers store fixed-size history summaries with no token dimension: conv state `(conv_dim, state_len)` for example `(3072, 3)` bf16 plus temporal SSM state `(num_heads, head_dim, state_size)` for example `(32, 64, 128)` fp32; effective SSM `block_size` is 1 and one block is one complete snapshot[^hybrid-ssm-disagg].
- [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) pools memory so layers at the same position in each type-group share one physical tensor, bumps FA `block_size` above the Mamba state size, and pads Mamba rows so both views share equal byte page sizes[^hybrid-ssm-disagg].
- One uniform descriptor list cannot index both views because FA length (`fa_block_len` at `base + b * page_size`) differs from Mamba `conv_size` / `ssm_size` at the same base; separate K/V and x/B/C/SSM descriptors are also needed for heterogeneous TP head indexing[^hybrid-ssm-disagg].

## Dual descriptor views

Register two concatenated descriptor lists under one NIXL handle over the same physical memory: FA descriptors first (`M regions x N_phys`, K and V indexed separately), then Mamba descriptors[^hybrid-ssm-disagg]:

```python
if is_fa_group:
    desc_id = region_id * N_phys + block_id
else:  # mamba group
    desc_id = mamba_region_id * N_log + block_id + num_descs
```

where `num_descs = M * N_phys` is the FA section size[^hybrid-ssm-disagg].

Homogeneous-TP Mamba uses 2 sub-regions (Conv, SSM); heterogeneous-TP uses 4 (x, B, C, SSM) for the conv decomposition below[^hybrid-ssm-disagg].

## Physical versus logical blocks

Attention kernels such as FlashInfer may require a smaller physical block (for example 16 tokens) than the logical/HMA block size. Standard models use `physical_blocks = logical_blocks * ratio` with `ratio = logical_block_size / kernel_block_size`; for hybrid models this expansion applies only to FA layers while SSM layers always use `N_logical`[^hybrid-ssm-disagg].

The FA section is therefore `M x N_phys` (`N_phys = N_logical * ratio`) and the Mamba section is `M x N_logical`, tracked per-engine in `_physical_blocks_per_logical` and resolved in `_get_block_descs_ids` because P and D may have different ratios under different TP sizes[^hybrid-ssm-disagg].

## 3-descriptor conv transfer and DS layout

Homogeneous TP (`P_TP == D_TP`) reads matching conv plus SSM blocks directly. Heterogeneous TP (for example `P_TP=1, D_TP=4`) must shard: SSM temporal state shards trivially on the leading `heads` axis, but conv `[x | B | C]` shards as `intermediate_size / TP`, `groups_ss / TP`, `groups_ss / TP` and is interleaved under the standard SD `(state_len, dim)` layout, preventing zero-copy RDMA slicing[^hybrid-ssm-disagg].

Setting `VLLM_SSM_CONV_STATE_LAYOUT=DS` selects `(dim, state_len)`, making x, B, and C each contiguous so every D rank performs three contiguous RDMA reads in one NIXL READ; `remote_conv_offsets` computes each rank's slice for the P page and TP ratio[^hybrid-ssm-disagg].

Zero-overhead properties claimed[^hybrid-ssm-disagg]:

- No GPU staging buffer and no sender/receiver reshuffle or post-transfer permute kernel; state lands directly usable.
- Each D rank transfers only its `1/TP` conv share rather than the full P conv state.
- Mamba descriptors are sized to real `conv_bytes + ssm_bytes`, skipping HMA padding bytes.

Transfer-volume evidence on Nemotron Super 120B at TP=4 with FA `block_size=4224` compares analytical Naive (full padded pages) against Optimal (actual conv plus SSM) plus measured NIXL bytes versus input length: the measured line matches Optimal, padding is negligible for fp8 in that configuration, and bf16 saves about 50 MB per request; transfer grows with ISL through FA block count even though Mamba state itself is fixed-size per request. Both figures in `raw/` were visually inspected and support this reading[^hybrid-ssm-disagg].

## Worked example: Nemotron-3-Nano-30B-A3B-FP8 at TP=2

- 52 layers alternating Mamba/FA; HMA forms 5 groups (4 Mamba, 1 FA) pooled into 6 shared KV tensors[^hybrid-ssm-disagg].
- FA layout `[num_blocks, 2, block_size=400, 4, 128]` with HMA-inflated block size; SSM `conv [num_blocks, 3, 3072]` plus `ssm [num_blocks, 48, 64, 128]`, padded to equal page bytes with possible further FA physical/logical subdivision by the kernel[^hybrid-ssm-disagg].
- Registration: 6 NIXL regions; FA descriptors `6 x N_phys` with K/V split; Mamba descriptors appended as `6 x N_logical` with 4 sub-regions for 3-descriptor transfer[^hybrid-ssm-disagg].
- Transfer: P completes prefill, scheduler emits `[[fa_block_ids], [mamba_ids_g0], ...]`, D maps with FA versus Mamba stride plus `num_descs` offset, issues one `make_prepped_xfer` READ, polls, then notifies P to free blocks[^hybrid-ssm-disagg].

## Performance claim

On 8x H200 over NVLink with Nemotron-3-Super-120B-A12B-FP8 (LatentMoE hybrid Mamba2 plus attention), ShareGPT sweep from concurrency 8 to 256, prefix-caching disabled, high warmup to scramble allocation (verified by constant descriptor counts), 1xTP8 colocated versus 1P-TP4 plus 1D-TP4 disaggregated on the same GPU count, disaggregated Pareto-dominates colocated at higher batch sizes with substantially higher output tok/s per GPU by isolating decode from prefill interference[^hybrid-ssm-disagg].

Treat this as vendor-reported single-workload evidence, not a general throughput guarantee; the general P/D split is documented not to improve raw throughput in [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md)[^hybrid-ssm-disagg].

## Operation

Requires `VLLM_SSM_CONV_STATE_LAYOUT=DS` for heterogeneous TP only; otherwise colocated kernel behavior shows no noticeable regression claimed and DS may become default later[^hybrid-ssm-disagg]:

```bash
# Prefill instance
VLLM_SSM_CONV_STATE_LAYOUT=DS vllm serve nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8 \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.85 \
    --trust-remote-code \
    --max-model-len 8192 \
    --block-size 128 \
    --no-disable-hybrid-kv-cache-manager \
    --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_both"}'
```

Additive scope: inactive for models without SSM layers; builds on HMA NIXL interface PR #35758 via #36687 (dual views plus homogeneous TP), #37416 (DS conv layout), #37635 (heterogeneous 3-descriptor transfer), and #37310 (N-1 prefill)[^hybrid-ssm-disagg].

See [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) for pull-mode deployment, roles, and metrics, and [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md) for P/D handshake and layout rules.

## Limitations

- Mamba1 unsupported for 3-descriptor transfer because `(intermediate_size // tp, state_size)` cannot reconstruct `intermediate_size` for conv decomposition; Mamba2 only. GDN (Qwen3.5+) is roadmap issue #33702[^hybrid-ssm-disagg].
- SSM transfer plus speculative decoding is not extensively validated[^hybrid-ssm-disagg].
- Different P/D block sizes with HMA (`block_size_ratio > 1`) are unsupported[^hybrid-ssm-disagg].

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — general P/D split and connector catalog; this concept covers only the hybrid-SSM NIXL extension.
- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — HMA grouping, FA block-size inflation, and Mamba padding that this transfer must skip and bridge.
- Uses [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) — pull READ, proxy, lease, and `vllm:nixl_*` observability reused here; this concept covers only hybrid descriptor and conv-transfer additions.
- Uses [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md) — handshake, layout, and hetero-TP/hetero-block-size rules; this source claims Mamba2 hetero-TP transfer in `v0.20.0`, newer than that matrix's work-in-progress cell, so treat the matrix as point-in-time until re-verified.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — performance comparison above disables prefix caching; Mamba fine-grained cache interaction is outside this source's verified scope.

## Coverage limits

- PR contents (#35758, #36687, #37416, #37635, #37310), roadmap #33702, HMA internals beyond the stated pooling/padding behavior, and kernel internals were not inspected beyond this post[^hybrid-ssm-disagg].
- Quantitative savings and Pareto claims follow the post text plus inspected `transfer-volume-vs-isl.png` and `disagg-vs-colocated.png`; no independent rerun was performed[^hybrid-ssm-disagg].

[^hybrid-ssm-disagg]: Nicolò Lucchesi, Zhanqiu Hu (Red Hat), vLLM team, Disaggregated Serving for Hybrid SSM Models in vLLM — `../raw/2026-04-21-hybrid-ssm-disagg/index.md` (2026-04-21), covering dense NIXL workflow, FA versus SSM state mismatch, HMA shared-tensor views and padding, dual descriptor mapping, physical/logical ratio handling, DS-layout 3-descriptor heterogeneous transfer with zero-buffer/skip-padding properties, Nemotron-H/Nano/Super examples, 8xH200 disaggregated versus colocated Pareto result, `v0.20.0` operation command, and Mamba1/GDN/spec-decode/mixed-block-size limits.
