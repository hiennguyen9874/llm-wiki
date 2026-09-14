---
type: Concept
title: SGLang LoRA Serving
description: Multi-LoRA serving for SGLang covering dynamic loading, GPU pinning, Triton and ChunkedSGMV backends, and overlap loading.
tags: [sglang, lora, serving]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:15:00Z }
sources:
  - id: sgl-lora
    resource: ../raw/sglang/advanced_features/lora.mdx
    title: LoRA Serving
---

SGLang serves LoRA adapters against a base model with multiple adapters active for different sequences in one batch, using S-LoRA and Punica techniques[^sgl-lora].

## Server arguments

Relevant multi-LoRA flags[^sgl-lora]:

- `enable_lora`: enable LoRA support; automatically true when `--lora-paths` is provided.
- `enable_lora_overlap_loading`: load adapter weights asynchronously to overlap H2D transfers with GPU compute; enable when adapter loading bottlenecks throughput, for example frequent loading of large adapters.
- `lora_paths`: adapters to load, each as `<PATH>`, `<NAME>=<PATH>`, or JSON `{"lora_name":str,"lora_path":str,"pinned":bool}`.
- `max_loras_per_batch`: maximum adapters per batch; affects reserved GPU memory, so lower it when memory is scarce. Default `8`.
- `max_loaded_loras`: maximum adapters held in CPU memory; must be `>= max-loras-per-batch`.
- `lora_eviction_policy`: `lru` least-recently-used by default for better cache efficiency, or `fifo` first-in-first-out.
- `lora_backend`: GEMM backend, `triton` or `csgmv` chunked SGMV; Cutlass/CUDA kernels planned.
- `max_lora_rank`: maximum supported rank; inferred from `--lora-paths` when unset, but declare it explicitly when dynamically loading larger-rank adapters later.
- `lora_target_modules`: union of modules LoRA applies to, for example `q_proj`, `k_proj`, `gate_proj`; inferred from `--lora-paths` when unset, but declare it explicitly when dynamically loading adapters with different modules later. `all` enables every supported module at minor performance cost; for performance-sensitive use, list only planned modules.
- `--max-lora-chunk-size`: chunk size for the `csgmv` backend only; larger values may help, tune per hardware and workload. Default `16`.
- `tp_size`: tensor-parallel degree; LoRA works with tensor parallelism using the S-LoRA sharding strategy.

Clients send a list of prompt strings plus a per-sequence adapter name list[^sgl-lora].

## Request routing

Two serving APIs[^sgl-lora]:

- OpenAI-compatible (`/v1/chat/completions`, `/v1/completions`): select an adapter with `model:adapter-name`, for example `qwen/qwen2.5-0.5b-instruct:adapter_a`.
- Native (`/generate`): pass `lora_path` per sequence, using `None` for the base model.

Reserve one `max-loras-per-batch` slot for the base model when mixing adapted and unadapted requests; for example `--max-loras-per-batch 2` serves one adapter plus base-model traffic, with `"lora_path": ["lora0", None]`[^sgl-lora]. Multiple adapters use `"lora_path": ["lora0", "lora1"]`[^sgl-lora].

## Dynamic loading

`/load_lora_adapter` and `/unload_lora_adapter` load and unload adapters without listing them all in `--lora-paths`[^sgl-lora]. Requests carry `lora_name` plus `lora_path`, and unload carries `lora_name`.

When using dynamic loading, declare both `--max-lora-rank` and `--lora-target-modules` at startup[^sgl-lora]. Without explicit values SGLang infers them from `--lora-paths`, in which case later adapters must share the same rank and target modules or be strictly smaller[^sgl-lora].

## GPU pinning

A `pinned` adapter permanently occupies one GPU pool slot sized by `--max-loras-per-batch` and is never evicted until explicitly unloaded[^sgl-lora]. Pinning avoids repeated transfers and reinitialization for hot adapters but reduces slots for on-demand adapters; pinning all slots would starve unpinned requests, so SGLang caps pinned adapters at `max-loras-per-batch - 1`[^sgl-lora].

Pin at startup with JSON adapter specs or during dynamic loading with `"pinned": true`[^sgl-lora].

## Backend choice

- `triton`: basic Triton backend.
- `csgmv`: default chunked SGMV backend optimized for high concurrency, reported at 20–80% latency improvement over Triton in source benchmarks[^sgl-lora].

## Overlap loading

`--enable-lora-overlap-loading` overlaps adapter weight movement with prefill and decode compute, reported at about 35% median TTFT reduction under adversarial conditions in the cited PR benchmarks[^sgl-lora].

Two caveats[^sgl-lora]:

1. Pinned CPU memory: asynchronous H2D copies need pinned CPU memory, so `max_loaded_loras` is limited to at most `2x max_loras_per_batch` when overlap loading is on.
2. Reduced multi-adapter prefill batching: asynchronous readiness means only requests whose adapters are already loaded can batch together, so per-adapter prefills may run separately. This can raise TTFT when load time is small relative to prefill compute, which is why the option is off by default and intended for load-bottlenecked workloads such as high adapter churn, heavy weights, or PCIe limits.

Worst-case illustration from the source: four adapters with 2 ms load and 20 ms prefill take about `2*4+20=28 ms` synchronously, versus about `2+4*20=82 ms` when overlap serializes prefills[^sgl-lora].

## Future work

The source points to the LoRA roadmap issue for embedding-layer support, unified paging, and a Cutlass backend as still under development[^sgl-lora].

## Relationships

- Uses [vLLM LoRA Adapters](vllm-lora-adapters.md) — companion per-request adapter serving for comparing SGLang pinned slots, dynamic load APIs, rank/module pre-declaration, and backend selection against vLLM static, runtime-update, and resolver-based loading.

## Coverage limits

- The linked OpenAI API LoRA examples under `basic_usage/openai_api_completions` were not present in `raw/` and were not inspected; OpenAI-syntax detail here covers only the `model:adapter-name` form stated in this source[^sgl-lora].
- Latency claims above are source-reported benchmarks without independent verification; no hardware, concurrency, or adapter-size matrix was in the source[^sgl-lora].
- External S-LoRA/Punica papers, overlap-loading PR benchmarks, and the future-work roadmap issue were cited but not inspected beyond this doc[^sgl-lora].

[^sgl-lora]: LoRA Serving — `../raw/sglang/advanced_features/lora.mdx`.
