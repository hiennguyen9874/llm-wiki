---
type: Concept
title: SGLang Attention Backends
description: Selection, MHA/MLA support matrices, hybrid prefill-decode, and extension workflow for SGLang attention backends.
tags: [sglang, attention, backends, cuda, mla]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:53:07Z }
sources:
  - id: sgl-attn
    resource: ../raw/sglang/advanced_features/attention_backend.mdx
    title: Attention Backend
---

SGLang selects an attention kernel per model and hardware from MHA and MLA backend families, defaulting automatically when `--attention-backend` is omitted and allowing experimental split prefill/decode selection[^sgl-attn].

Backend choice affects native paged KV-cache page sizes, FP8/FP4 KV cache, speculative-decoding top-k, sliding window, multimodal, and chunked prefix-cache support[^sgl-attn].

## Selection

If `--attention-backend` is unspecified, SGLang makes a best-effort automatic choice for performance based on hardware and model architecture; not all backends work on all platforms or architectures[^sgl-attn].

Multimodal attention is selected separately with `--mm-attention-backend`; the MHA "MultiModal" column below indicates whether that backend family has a corresponding multimodal implementation[^sgl-attn].

CUDA automatic-selection logic[^sgl-attn]:

- MHA models such as Llama and Qwen:
  - Hopper such as H100/H200/H20: `fa3` if CUDA 12.3+ and model config supported.
  - Blackwell such as B200: `trtllm_mha`, unless speculative decoding uses `topk > 1`.
  - Other architectures such as Ampere/Ada: `flashinfer` if available, else `triton`.
- MLA models such as DeepSeek V3/R1:
  - Hopper: `fa3` with CUDA 12.3+.
  - Blackwell: `trtllm_mla`.
  - Other architectures: `triton`.

Representative explicit selection[^sgl-attn]:

```bash
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend flashinfer
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend fa3
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend triton
python3 -m sglang.launch_server --tp 8 --model deepseek-ai/DeepSeek-R1 --attention-backend flashmla --trust-remote-code
python3 -m sglang.launch_server --tp 8 --model deepseek-ai/DeepSeek-R1 --attention-backend trtllm_mla --trust-remote-code
python3 -m sglang.launch_server --tp 8 --model deepseek-ai/DeepSeek-R1 --attention-backend cutlass_mla --trust-remote-code
python3 -m sglang.launch_server --model Qwen/Qwen2.5-14B-Instruct-1M --attention-backend dual_chunk_flash_attn
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend torch_native
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend flex_attention
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend ascend
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend intel_xpu
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend wave
```

FP8 KV-cache example with MLA[^sgl-attn]:

```bash
python3 -m sglang.launch_server --tp 8 --model deepseek-ai/DeepSeek-R1 \
  --attention-backend trtllm_mla --kv-cache-dtype fp8_e4m3 --trust-remote-code
```

## MHA support matrix

"Page Size > 1 (native)" means true in-kernel paging; backends without native support can emulate `page_size > 1` at the wrapper layer by expanding page tables to per-token indices[^sgl-attn].

| Backend | Page Size > 1 native | FP8 KV | FP4 KV | Spec topk=1 | Spec topk>1 | Sliding Window | MultiModal |
|---|---|---|---|---|---|---|---|
| FlashInfer | yes | yes | no | yes | yes | yes | no |
| FA3 | yes | yes | no | yes | yes | yes | yes |
| FA4 | 128 only | no | yes | no | no | no | yes |
| Triton | no | no | yes | yes | yes | yes | yes |
| Torch Native SDPA | no | yes | yes | no | no | no | yes |
| FlexAttention | no | no | yes | no | no | no | no |
| TRTLLM MHA | 16, 32 or 64 | yes | yes | yes | no | yes | no |
| Dual Chunk FlashAttention | yes | no | no | no | no | no | no |
| AITER ROCm | yes | yes | no | yes | yes | no | yes |
| Wave ROCm | yes | no | no | no | no | no | no |
| Ascend NPU | yes | no | no | no | no | no | yes |
| Intel XPU | yes | no | no | no | no | yes | no |
| Intel AMX CPU | no | no | no | no | no | no | no |

Notes[^sgl-attn]:

- FlashAttention 4 is prefill-only for now.
- For KV FP4 with FA4, a different `--decode-attention-backend` is required; except `trtllm_mha` being incompatible with FA4, other decode backends behave as in the table.
- NSA is designed specifically for DeepSeek V3.2 DSA.

## MLA support matrix

| Backend | Native page sizes | FP8 KV | FP4 KV | Chunked prefix cache | Spec topk=1 | Spec topk>1 |
|---|---|---|---|---|---|---|
| FlashInfer MLA | 1 | no | yes | yes | yes | no |
| FlashMLA | 64 | yes | yes | yes | yes | no |
| Cutlass MLA | 128 | yes | yes | yes | yes | no |
| TRTLLM MLA Blackwell | 32 or 64 | yes | yes | yes | yes | no |
| FA3 | n/a | no | no | yes | yes | limited, page_size=1 only |
| Triton | n/a | no | no | no | yes | limited, page_size=1 only |
| FA4 | 1 | no | yes | no | no | no |
| Ascend MLA NPU | 128 | no | no | no | no | no |

Fixed native page-size constraints[^sgl-attn]:

- FlashInfer MLA: `page_size = 1`.
- FlashMLA: `page_size = 64`.
- Cutlass MLA: `page_size = 128`.
- TRTLLM MLA: `page_size` in `{32, 64}`.
- TRTLLM MHA: `16/32/64`.
- Ascend: `128`.

## Page size and prefix cache

Page size groups tokens into KV-cache blocks; prefix caching only matches complete pages and cannot pad partial pages[^sgl-attn].

For example, with `page_size = 64`, a 32-token prompt fills no complete page and cannot match, while a 65-token prompt caches and matches only the first 64 tokens and discards the remaining token; use `page_size = 1` for maximum token-level prefix reuse[^sgl-attn].

## Speculative decoding top-k

`topk` is the number of draft tokens sampled per step from the draft model: `topk = 1` follows classic EAGLE, while `topk > 1` explores multiple branches and needs backend support in both draft and verification paths[^sgl-attn].

## Hybrid prefill-decode attention

Hybrid attention is experimental and mixes backends per phase when one excels at prefill and another at decode; implementation lives in `python/sglang/srt/layers/attention/hybrid_attn_backend.py`[^sgl-attn].

```bash
python3 -m sglang.launch_server \
  --model-path nvidia/DeepSeek-R1-FP4 \
  --tp 8 \
  --attention-backend trtllm_mla \
  --moe-runner-backend flashinfer_trtllm \
  --quantization modelopt_fp4 \
  --prefill-attention-backend fa4
```

Behavior[^sgl-attn]:

- Setting only one of `--prefill-attention-backend` or `--decode-attention-backend` makes the unspecified phase inherit `--attention-backend`.
- Setting both to different values automatically enables the hybrid wrapper for per-phase dispatch.
- FA4 hybrid example above uses FA4 for prefill and TRTLLM MLA for decode.

Speculative decoding with hybrid attention uses `--speculative-attention-mode`[^sgl-attn]:

- `decode`, recommended: draft decoding and target verification use the decode backend.
- `prefill`, default: draft decoding and target verification use the prefill backend.

Constraints[^sgl-attn]:

- Any `trtllm_mha` backend supports only `--speculative-eagle-topk 1`.
- Paged MHA backends with `--page-size > 1` and `--speculative-eagle-topk > 1` support only `flashinfer`.
- CUDA Graph always captures the decode backend; it captures the prefill backend only when `--speculative-attention-mode prefill`.

## Adding a new backend

Learn from `python/sglang/srt/layers/attention/triton_backend.py` and `flashattention_backend.py`[^sgl-attn].

Without CUDA graph, implement[^sgl-attn]:

- `forward_extend`: prefill, prefill with KV cache, and target verification; called once per layer.
- `forward_decode`: normal decode and draft decode; called once per layer.
- `init_forward_metadata`: shared per-forward setup and planning such as split-KV; called once per forward.

With CUDA graph, add capture/replay support[^sgl-attn]:

- `init_cuda_graph_state`: called once per lifetime; create shared buffers.
- `init_forward_metadata_capture_cuda_graph`: called before graph capture; like `init_forward_metadata` but writes to predefined buffers.
- `init_forward_metadata_replay_cuda_graph`: called before graph replay; on the critical path and must be fast.

## Coverage limits

- Linked DeepSeek MLA throughput-optimization docs and the original DeepSeek MLA paper were not inspected; MHA versus MLA architectural detail beyond backend selection is not compiled here[^sgl-attn].
- NSA/DeepSeek V3.2 DSA kernel detail and multimodal backend implementations are out of scope[^sgl-attn].

## Relationships

- Uses [SGLang Advanced CUDA Graphs](sglang-advanced-cuda-graphs.md) — full prefill capture currently needs FA4/FlashInfer-style extend metadata; BCG avoids compiler-tracing constraints when evolving backends.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — companion matrix for vLLM backend selection, useful for comparing SGLang FA3/FlashInfer/Triton coverage and MLA prefill/decode handling.

[^sgl-attn]: Attention Backend — `../raw/sglang/advanced_features/attention_backend.mdx`.
