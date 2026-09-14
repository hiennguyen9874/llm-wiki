---
type: Concept
title: vLLM Attention Backends
description: Selection, configuration, composite routing, and MLA/sparse variants for vLLM attention backends.
tags: [vllm, attention, backends, cuda, mla]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:33:58Z }
sources:
  - id: attn-backends
    resource: ../raw/vllm/design/attention_backends.md
    title: Attention Backend Feature Support
---

vLLM selects an attention kernel implementation through an attention-backend registry whose priority and feature tables are auto-generated from `AttentionBackend.validate_configuration()` checks[^attn-backends].

Users can pin a backend explicitly or leave selection automatic, with separate handling for standard MHA/MQA/GQA, MLA prefill/decode, MiniMax M3 sparse layers, and multimodal-prefix composites[^attn-backends].

## Setting the backend

Command line has two mutually exclusive forms[^attn-backends]:

```bash
vllm serve <model> --attention-backend FLASH_ATTN
vllm serve <model> --attention-config.backend FLASH_ATTN
vllm serve <model> -ac.backend FLASH_ATTN
vllm serve <model> --attention-config '{"backend": "FLASH_ATTN"}'
```

Python API uses `AttentionConfig` with `LLM`[^attn-backends]:

```python
from vllm import LLM
from vllm.config import AttentionConfig
from vllm.v1.attention.backends.registry import AttentionBackendEnum

llm = LLM(model="Qwen/Qwen3-0.6B", attention_config=AttentionConfig(backend=AttentionBackendEnum.FLASH_ATTN))
llm = LLM(model="Qwen/Qwen3-0.6B", attention_backend="FLASH_ATTN")
```

## Selection behavior

Manual selection validates the requested backend against model dtype, head size, compute capability, and related configuration; an incompatible choice raises an error with the specific reason, for example `FLASHMLA is not valid ... Reason: ['compute capability not supported']`[^attn-backends].

Automatic selection, the default when no backend is specified, iterates backends in priority order where `1` is highest and picks the first compatible backend; if none is compatible it errors with per-backend incompatibility reasons[^attn-backends].

CUDA has separate priority lists for standard attention and DeepSeek-style MLA; ROCm and CPU use their own selection logic documented elsewhere[^attn-backends].

## Composite multimodal-prefix backends

### TRITON_FLASH_ATTN on Hopper

Preferred for compatible multimodal-prefix configurations: Triton handles batches whose current queries need bidirectional image attention while FlashAttention handles causal text prefills and decode, sharing one KV cache[^attn-backends].

The causal child must resolve to FA4. This happens automatically for FA4-only shapes such as head size 512 and models whose version policy promotes all layers to FA4, including Gemma 4; a standalone head-size-256 configuration selecting FA3 falls back to Triton for the whole layer[^attn-backends].

No override is needed, for example `vllm serve google/gemma-4-31B-it`[^attn-backends].

### TRITON_FLASHINFER on Blackwell

Preferred for compatible multimodal-prefix configurations, including Gemma 4 with BF16 or FP8 KV cache: Triton handles batches whose current queries require bidirectional image attention and FlashInfer handles causal text prefills and decode; historical image tokens alone do not select Triton[^attn-backends].

It instantiates `create_composite_attention_backend` from `vllm/v1/attention/backends/composite.py` with Triton, FlashInfer, and `MMPrefixAttentionRouting`; the factory owns child implementations, metadata dispatch, cache requirements, and workspace sharing, while the routing policy selects the child and defines graph-capture safety[^attn-backends].

Reported capabilities and limits[^attn-backends]:

- Head dimensions 256/512, FP16/BF16 and FP8 KV cache, 64-token kernel pages, head-major cache layout.
- TRTLLM handles causal attention at both head dimensions, but its head-dim-512 kernels do not support 128-token pages.
- For Gemma 4, full CUDA graphs cover single-token batches; multi-token batches use the non-full-graph path.
- Image masks extending beyond the sliding window cannot use full attention graphs.
- Context parallelism, R-SWA, attention sinks, and adaptive verification are not supported.

It can also be selected explicitly with `--attention-backend TRITON_FLASHINFER`[^attn-backends].

## Standard attention notes

The source defines a legend for the generated feature tables: model dtypes, KV-cache dtypes, block sizes where `%N` means multiples of `N`, head sizes, sink support for StreamingLLM, non-causal bidirectional support for decoder models, sparse support for MLA only, multimodal-prefix full-attention support, decode-context-parallelism support, attention pattern types, and required CUDA compute capability, with `✅` supported and `❌` unsupported[^attn-backends].

FlashInfer paths[^attn-backends]:

- Native is the regular FlashInfer path.
- XQA is the SM90 decode path exposed through FlashInfer's TRTLLM decode API.
- `trtllm-gen` is used on SM100 and supports sinks.
- Disable XQA/`trtllm-gen` with `--attention-config.use_trtllm_attention=0`.

FlashAttention version is set with `--attention-config.flash_attn_version=2`, `3`, or `4`; default is FA4 on SM100+ Blackwell, FA3 on SM90 Hopper, FA2 otherwise[^attn-backends].

On Blackwell with head size 256, the FlashAttention backend uses a dedicated FA4 kernel requiring KV-cache block size 128, advertised automatically unless `--block-size` is pinned; it does not support logit soft capping, attention sinks, multimodal-prefix/R-SWA masking, decode context parallelism, or windowed encoder attention, and those configurations transparently fall back to FA2, while a pinned incompatible `--block-size` makes FlashAttention ineligible and errors if explicitly requested[^attn-backends].

## b12x backend

Optional causal decoder-attention backend for NVIDIA SM120/SM121 GPUs[^attn-backends]:

```bash
uv pip install "vllm[b12x]"
vllm serve <model> --attention-backend b12x
```

## MiniMax M3 sparse attention

Block-sparse GQA backend used by MiniMax M3 sparse lightning-indexer layers[^attn-backends].

A lightning indexer scores KV blocks, selects top-k blocks plus fixed init/local blocks, attends only to those blocks, and keeps index keys in a separate side cache. It is wired in directly by the model and is not part of the automatic priority lists[^attn-backends].

## MLA backends

MLA uses separate prefill and decode backends[^attn-backends].

Prefill is selected explicitly with `-ac.mla_prefill_backend=<BACKEND>` or automatically at runtime. Automatic selection tries FlashAttention first; on Blackwell SM100 the fallback order is TRT-LLM Ragged, FlashInfer, then TokenSpeed MLA, except `(qk_nope_head_dim=192, qk_rope_head_dim=64, v_head_dim=256)` tries TRT-LLM Ragged before FlashAttention; on other GPUs only FlashAttention is considered[^attn-backends].

Decode is selected with the standard `-ac.backend=<BACKEND>` argument, for example `FLASHMLA` or `TRITON_MLA`[^attn-backends].

DeepSeek V4 sparse MLA has its own decode backends selected via `--attention-backend=<BACKEND>`, for example `FLASHMLA_SPARSE_DSV4` or `FLASHINFER_MLA_SPARSE_DSV4`; they share the V4 sparse-index pipeline of compressor plus sliding-window attention plus indexer with 256-token blocks and head 512, defaulting to `FLASHINFER_MLA_SPARSE_DSV4` on SM12x and `FLASHMLA_SPARSE_DSV4` on other supported CUDA architectures[^attn-backends].

Sparse MLA preference noted in the source: FP8 KV cache always prefers `FLASHINFER_MLA_SPARSE`; with BF16 KV cache, `FLASHINFER_MLA_SPARSE` is preferred at low query-head counts of 16 or fewer while `FLASHMLA_SPARSE` is preferred otherwise[^attn-backends].

## Coverage limits

- Priority tables for standard and MLA attention and feature tables for standard, MiniMax, MLA prefill, MLA decode, and DeepSeek V4 decode are auto-generated MkDocs snippets (`gen:priority-standard`, `gen:priority-mla`, `gen:table-standard`, `gen:table-minimax`, `gen:table-mla-prefill`, `gen:table-mla-decode`, `gen:table-mla-v4-decode`) absent from `raw/` and were not inspected[^attn-backends].
- ROCm and CPU selection logic is delegated to platform-specific documentation and is not compiled here[^attn-backends].

## Relationships

- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — historical paged-attention kernel predates the current backend registry but illustrates the attention computation these backends now provide.
- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — backends consume paged KV cache with backend-specific dtype, block-size, page-size, and layout constraints.

[^attn-backends]: Attention Backend Feature Support — `../raw/vllm/design/attention_backends.md`.
