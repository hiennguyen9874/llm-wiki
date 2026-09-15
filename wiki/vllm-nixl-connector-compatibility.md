---
type: Concept
title: vLLM NIXL Connector Compatibility
description: Feature compatibility matrix, handshake requirements, KV layout, and quantized-cache rules for NixlConnector disaggregated prefill/decode.
tags: [vllm, nixl, disaggregated-prefill, kv-cache, compatibility]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T19:00:00Z }
sources:
  - id: nixl-compat
    resource: ../raw/vllm/features/nixl_connector_compatibility.md
    title: NixlConnector Compatibility Matrix
  - id: hybrid-ssm-disagg
    resource: ../raw/2026-04-21-hybrid-ssm-disagg/index.md
    title: Disaggregated Serving for Hybrid SSM Models in vLLM
---

NixlConnector disaggregated prefill/decode supports most dense, MLA, sparse-MLA, MoE, and hybrid-SSM combinations for basic transfer, with narrower support for speculative decoding, heterogeneous parallelism, cross-layer blocks, and heterogeneous block sizes, plus a handshake compatibility hash and KV-layout and quantization rules governing valid P/D pairs[^nixl-compat].

Legend: `✅` fully supported, `🟠` partial support, `❌` not supported, `❔` unknown / not yet validated, `🚧` work in progress[^nixl-compat].

## Universally supported features

The following work with all model architectures under NixlConnector PD disaggregated serving[^nixl-compat]:

- Chunked prefill
- APC (prefix caching)
- Data parallel
- CUDA graph
- Logprobs and prompt logprobs
- Prompt embeds
- Multiple NIXL backends (UCX, GDS, LIBFABRIC, etc.)

## Model architecture x capability

| Model type | Basic PD | Spec decode | Hetero TP | Cross-layer blocks | SWA | Host buffer | Hetero block size |
|---|---|---|---|---|---|---|---|
| Dense Transformers | ✅ | ✅¹ | ✅ | ✅² | ✅ | ✅ | 🟠³ |
| MLA (e.g. DeepSeek-V2/V3) | ✅ | ✅¹ | 🟠⁴ | ✅² | ✅ | ✅ | 🟠³ |
| Sparse MLA (e.g. DeepSeek-V3.2) | ✅ | ✅¹ | 🟠⁴ | ✅² | ✅ | ✅ | 🟠³ |
| Hybrid SSM / Mamba | ✅ | ❔ | 🚧⁵ | ❌ | ✅ | ✅ | ❌⁶ |
| MoE | ✅ | ✅¹ | ✅ | ✅² | ✅ | ✅ | 🟠³ |
| Multimodal | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ |
| Encoder-Decoder | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

Capability shorthand: Basic PD is basic prefill/decode disaggregation; Hetero TP is heterogeneous tensor parallelism with P TP != D TP; Host buffer is CPU host-buffer offload; Hetero block size is different block sizes on P and D[^nixl-compat].

- ¹ Speculative decoding requires compatible speculation configurations on P and D instances[^nixl-compat].
- ² Cross-layer contiguity uses a `BLHNC` layout, set via `VLLM_KV_CACHE_LAYOUT=BLHNC`[^nixl-compat].
- ³ Hetero block size is supported only when HMA is not required (non-hybrid models); block IDs are remapped automatically and only P block size < D block size is supported[^nixl-compat].
- ⁴ MLA KV cache is replicated across TP workers, so heterogeneous TP works without head-splitting; when P TP > D TP only a single read executes with redundant ranks skipped, and D TP > P TP also works[^nixl-compat].
- ⁵ Hybrid SSM (Mamba) models require homogeneous TP (`P TP == D TP`); heterogeneous TP is not yet supported for Mamba layers[^nixl-compat].
- ⁶ HMA, required by hybrid models, does not support different remote block sizes[^nixl-compat].

## P/D handshake compatibility

By default a compatibility hash is checked during handshake. P and D must agree on[^nixl-compat]:

- vLLM version and NIXL connector version
- Model architecture, dtype, number of KV heads, head size, and number of hidden layers
- Attention backend
- KV cache dtype (`cache_dtype`)
- EAGLE/MTP-style speculative method and draft-model configuration
- NIXL transfer mode: push (WRITE) and pull (READ) connectors use incompatible transfer protocols and must never be paired

Disabling the check with `--kv-transfer-config '{"kv_connector_extra_config": {"enforce_handshake_compat": false}}'` is at the operator's own risk[^nixl-compat].

The following may safely differ between P and D[^nixl-compat]:

- `tensor-parallel-size`, subject to the heterogeneous-TP restrictions above
- `block-size`, subject to the heterogeneous-block-size restrictions above
- Number of KV cache blocks, determined by available memory on each instance
- `num_speculative_tokens`; prefill and decode may use different draft depths
- Draft-model `attention_backend`; each instance auto-selects independently and the resulting KV block layout is validated at handshake time rather than via the compatibility hash

## KV cache layout

- NixlConnector defaults to `LBHNC` (head-major, formerly `HND`) for optimal transfer performance on non-MLA models[^nixl-compat].
- `LBNHC` (token-major, formerly `NHD`) is supported but does not allow heterogeneous-TP head splitting[^nixl-compat].
- Experimental `LBHNC` ↔ `LBNHC` permutation is enabled via `--kv-transfer-config '{"enable_permute_local_kv": true}'` and is not supported with HMA[^nixl-compat].

## Quantized KV cache

Quantized KV cache (e.g. FP8) requires P and D to use the same `cache_dtype`; mismatched cache dtypes fail the handshake compatibility check[^nixl-compat]:

- Static quantization with scales loaded from the checkpoint: ✅ supported; each instance loads scales independently from the model checkpoint[^nixl-compat].
- Dynamic quantization with scales computed at runtime: ❌ not supported; per-block scales are not transferred alongside KV data[^nixl-compat].
- Packed-layout scales stored inline with weights: ✅ supported; scales transfer together with the KV cache blocks[^nixl-compat].

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — general prefill/decode split and connector catalog; this concept covers only NixlConnector-specific compatibility, handshake, layout, and quantization rules.
- Uses [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — push WRITE versus pull READ is one incompatible P/D pairing choice; this concept covers the compatibility rule, not push threading or wire format.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — APC is listed here as universally supported under NixlConnector PD serving; this concept covers only the compatibility claim, not cache mechanics.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — attention backend must match across P/D for the handshake hash; this concept covers only the matching requirement, not backend selection.
- Uses [vLLM Hybrid SSM Disaggregated Serving](vllm-hybrid-ssm-disaggregation.md) — Mamba2 hetero-TP transfer mechanism claimed in `v0.20.0`, newer than the 🚧 cell above; treat the matrix cell as point-in-time until re-verified[^hybrid-ssm-disagg].

## Coverage limits

- Linked usage and background guides (`nixl_connector_usage.md`, `disagg_prefill.md`, chunked-prefill optimization, APC, data-parallel deployment, prompt embeds, and quantized-KV-cache docs) were not recompiled here; only the compatibility claims stated in this source are covered[^nixl-compat].
- The external NIXL connector roadmap issue and any tracking issues linked from 🟠/❌ entries were not inspected; roadmap status beyond this point-in-time matrix is outside verified scope[^nixl-compat].
- The source describes itself as current-state documentation subject to change; treat partial, unknown, and work-in-progress cells as point-in-time rather than guarantees[^nixl-compat].

[^nixl-compat]: NixlConnector Compatibility Matrix — `../raw/vllm/features/nixl_connector_compatibility.md`, covering universally supported features, model-architecture x capability matrix with footnotes 1–6, P/D must-match versus may-differ configuration notes with handshake-hash warning, `LBHNC` / `LBNHC` layout defaults and experimental permute flag, and quantized-KV-cache same-dtype plus static/dynamic/packed-scale rules.

[^hybrid-ssm-disagg]: Disaggregated Serving for Hybrid SSM Models in vLLM — `../raw/2026-04-21-hybrid-ssm-disagg/index.md` (2026-04-21), covering Mamba2 dual-descriptor and DS-layout hetero-TP transfer claimed in `v0.20.0`; matrix values above remain point-in-time.
