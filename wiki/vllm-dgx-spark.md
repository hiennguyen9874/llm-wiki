---
type: Concept
title: vLLM on DGX Spark
description: Local vLLM serving on NVIDIA DGX Spark GB10 with unified-memory tuning, NVFP4 MoE model fit, and Nemotron-3-Super evaluation.
tags: [vllm, dgx-spark, gb10, nvfp4, local-inference, deployment]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T04:01:49Z }
sources:
  - id: vllm-dgx-spark
    resource: ../raw/2026-06-01-vllm-dgx-spark/index.md
    title: "vLLM on the DGX Spark: Architecture, Configuration, and Local Evaluation"
---

vLLM is a practical local inference endpoint for NVIDIA DGX Spark: the standard OpenAI-compatible server image plus a Spark-tested model recipe serves large NVFP4 MoE models locally with streaming, continuous batching, paged KV cache, and Prometheus telemetry[^vllm-dgx-spark].

## GB10 architecture and memory model

DGX Spark is a desk-side GB10 Grace Blackwell SoC with one 128 GB unified LPDDR5X CPU+GPU pool, consumer Blackwell `sm_121` silicon, and ConnectX networking for multi-Spark scale-out[^vllm-dgx-spark].

- **Unified pool expands locally servable size.** CPU, GPU, OS, container runtime, weights, and KV cache share the same 128 GB, so more system memory is usable for inference than a fixed dedicated-VRAM pool would allow; the source cites up to 200B-parameter NVFP4 models on one Spark depending on architecture and runtime config[^vllm-dgx-spark].
- **Serving flags must leave headroom.** `--gpu-memory-utilization`, `--max-model-len`, `--max-num-seqs`, and paged KV cache balance model size, context, and concurrency against the OS, page cache, runtime, and KV growth sharing that pool[^vllm-dgx-spark].
- **Use `sm_121`-validated builds.** Image tags, runtime settings, and kernel paths should be validated for `sm_121`; adapting a larger-GPU config is an engineering checklist for kernel and memory behavior, not a Spark performance expectation[^vllm-dgx-spark].
- **Multi-Spark is ConnectX-linked.** Larger deployments can use low-latency, high-bandwidth ConnectX links for distributed inference across Sparks[^vllm-dgx-spark].

Spark is best viewed as a single-user or small-batch local target for large NVFP4 models; dense models and high-concurrency serving can run but fit the bandwidth and unified-memory profile less well[^vllm-dgx-spark].

## Model fit

Model choice is the largest Spark performance lever. The source's Figure 3 is directional selection guidance, not a benchmark table[^vllm-dgx-spark]:

- Compact MoE / low-active-parameter FP4 — single-Spark feasible (examples listed: `openai/gpt-oss-20b`, `Qwen/Qwen3-30B-A3B-Instruct-2507`, `moonshotai/Kimi-Linear-48B-A3B-Instruct`).
- Mid-size dense FP8/FP4 — memory feasible (examples listed: `Qwen/Qwen3-32B`, `Qwen/Qwen3-32B-FP8`, `google/gemma-3-27b-it`).
- Large MoE FP4/NVFP4 around 100–130B total — highlighted single-Spark high-capacity class (examples: `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4`, `openai/gpt-oss-120b`).
- Frontier-scale MoE or very large dense — multi-node / data-center oriented (examples: `deepseek-ai/DeepSeek-V3.2`, `Qwen/Qwen3-235B-A22B-Instruct-2507`, `moonshotai/Kimi-K2-Thinking`).

The concrete worked example is `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4`, a 120B-total / 12B-active NVFP4 MoE; 100–130B MoE NVFP4 models with roughly 10–15B active parameters are called out as the strong-fit class because NVFP4 eases memory pressure and prefill/model-fit while decode still depends on active parameter count and kernel path[^vllm-dgx-spark].

## vLLM capabilities on Spark

- **Continuous batching plus paged KV cache.** Requests are admitted and evicted per decode step rather than in arrival-time lockstep, and paged KV blocks avoid excessive fragmentation; on a 120B NVFP4 MoE the source reports KV utilization typically below 5% in single-user tests and below 30% under small-batch demo traffic[^vllm-dgx-spark].
- **OpenAI-compatible streaming.** Local apps use the same client code against `http://localhost:8000/v1`; `stream=true` renders tokens as they arrive, which matters for perceived latency on chat, coding, and agentic flows even when absolute decode throughput trails data-center GPUs[^vllm-dgx-spark].
- **Prometheus telemetry.** A side view can poll `/metrics` from the same machine; the most useful Spark signals are `vllm:kv_cache_usage_perc`, prompt/generation token counters, and TTFT / inter-token-latency histograms. In a healthy agentic run, first-turn prefill is slow as the system prompt is read, later prefix-cached turns avoid prefill spikes, generation settles near the expected decode rate, and the app should compact conversation before KV usage nears the context limit[^vllm-dgx-spark].
- **Official image, Spark recipe.** The Nemotron-3-Super recipe uses the official `vllm/vllm-openai` server image; at run time it was the CUDA 13 nightly track `vllm/vllm-openai:cu130-nightly`. Treat that tag as a compatibility track, not a reproducible pin — validate a specific release, commit nightly, or digest and keep it in the runbook[^vllm-dgx-spark].

## Runtime configuration

Pre-stage weights once into a host-mounted Hugging Face cache and mount it into the long-running container ("download once, mount everywhere"); model-specific download/launch examples belong in vLLM Recipes[^vllm-dgx-spark].

Example serving flags for `vllm serve nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4`[^vllm-dgx-spark]:

- `--gpu-memory-utilization` — fraction of GPU-visible (here unified) memory vLLM may claim; start from the recipe (0.85 in the demo) and tune for OS, page cache, runtime, KV growth, and concurrency.
- `--max-model-len 131072` — accepted prompt plus completion length; 131K accommodates system prompts, tool schemas, files, and history, but is not a worst-case per-request KV reservation since scheduling follows active context.
- `--max-num-seqs 4` — admitted in-flight sequences; kept low because above about four concurrent decode streams the per-token bandwidth tax can outweigh batching gains and TTFT spikes.
- **Automatic prefix caching** — default-on in vLLM V1, so no `--enable-prefix-caching` flag is needed; useful for long shared system prompts but apps must stay correct on zero hits.
- **Parser flags follow the model recipe** — reasoning parser only for models emitting supported reasoning blocks, tool parsers only when clients need tool calls; Nemotron-3 uses built-in `--reasoning-parser nemotron_v3` (older recipes reference an external `super_v3` plugin), with `--enable-auto-tool-choice` plus `--tool-call-parser qwen3_coder` in the demo.

Evaluate with validation rather than copying into a runbook[^vllm-dgx-spark]:

- `--kv-cache-dtype fp8` — lowers KV memory pressure but can hurt predictability and cost noticeable Spark performance for some workloads.
- `--speculative-config` — for Nemotron-3-Super the relevant path is model MTP support.
- `--tensor-parallel-size 2` — meaningful only with two Sparks linked through ConnectX-7 ports.

Defaults guidance: leave quantized linear/MoE backend selection on `auto` unless the tested recipe pins one (prefer `--linear-backend` / `--moe-backend` CLI flags; older env vars are deprecated; recent FlashInfer CUTLASS paths outperform older Spark guidance); leave `--quantization` unset for pre-quantized NVFP4 checkpoints; treat version-specific env overrides such as a FlashInfer allreduce backend as workarounds, unneeded for single-Spark without tensor parallelism[^vllm-dgx-spark].

## Cold start and throughput slider

- **JIT pre-warm.** First request after boot triggers Inductor plus FlashInfer codegen (~25 s in the reported setup); fire a startup ping on the same client path (`max_tokens=3`, same model and `chat_template_kwargs`), after which the same short path returns in under 0.5 s. Weight load is separate (10–15 min default safetensors path); evaluate `fastsafetensors` or `InstantTensor` when startup matters, against the exact model, image, and storage stack[^vllm-dgx-spark].
- **Measured versus tuned.** The reported numbers use CUDA graphs enabled, `--kv-cache-dtype` unset, and speculative decoding disabled as recipe choices, not universal Spark defaults. Throughput runs may try FP8 KV cache, async scheduling, MTP speculative decoding, and explicit backend selection, validated per model, prompt shape, batch pattern, and release. The source frames this as a predictability-to-throughput slider and optimizes the demo path for stable local serving and clear telemetry[^vllm-dgx-spark].

## Reference deployment and workload

Full Docker invocation from the source (replace the nightly tag with a validated pin for production)[^vllm-dgx-spark]:

```bash
docker run -d --name vllm --ipc=host --restart unless-stopped \
  --gpus all -p 8000:8000 \
  -e HF_TOKEN="$HF_TOKEN" \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:cu130-nightly \
  nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4 \
    --served-model-name nemotron-3-super \
    --trust-remote-code \
    --max-model-len 131072 \
    --gpu-memory-utilization 0.85 \
    --max-num-seqs 4 \
    --reasoning-parser nemotron_v3 \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder
```

Verify readiness with `curl -sS http://localhost:8000/v1/models | jq -r '.data[0].id'` returning `nemotron-3-super`[^vllm-dgx-spark].

The `vllm-spark-game` workload exercises the path end to end beyond `curl`: a live 20-Questions game against `/v1` (OpenAI SDK, streamed chat) plus a `spark-stats` view polling `/metrics` and NVML GPU stats from the same Spark; both are Textual TUI clients against one local endpoint, with layout and run commands in the project README[^vllm-dgx-spark].

## Single-Spark evaluation

Five-scenario application-oriented eval against the local endpoint hosting Nemotron-3-Super-120B-A12B-NVFP4, median of three runs after one warm-up, token counts from `stream_options.include_usage`; presented as methodology illustration, not a leaderboard submission[^vllm-dgx-spark]:

| Scenario | Prompt tok | Gen tok | TTFT | Total latency | Prefill tok/s | Decode tok/s |
| --- | --- | --- | --- | --- | --- | --- |
| typical judge call (real 20Q, noisy 2-token gen) | 58 | 2 | 0.42 s | ~0.53 s | 140 | ~23 |
| medium prompt, short gen | 1,834 | 32 | 1.12 s | ~2.47 s | 1,636 | 23.7 |
| long prompt, short gen | 7,234 | 32 | 3.85 s | ~5.26 s | 1,877 | 22.7 |
| medium prompt, long gen | 1,834 | 108 | 1.12 s | ~5.74 s | 1,639 | 23.4 |
| long prompt, long gen | 7,234 | 124 | 3.84 s | ~9.26 s | 1,884 | 22.9 |

Interpretation: prefill scales near-linearly and is compute-bound (140 to ~1,900 tok/s as prompts amortize overhead; TTFT roughly triples on a 4x prompt growth); decode stays in a narrow 22.7–23.7 tok/s band that is recipe-specific (image, context, CUDA graphs, backend, scheduling) rather than a universal Spark/vLLM ceiling; the 2-token judge call is latency- rather than decode-rate-sensitive; typical game turns (~1,000-token prompts, 5–15 output tokens) are TTFT-dominated with ~0.2–0.7 s decode, and KV utilization rarely tops 2% during play[^vllm-dgx-spark].

Report image tag, context length, CUDA-graph status, backend path, and scheduling settings alongside any reproduction[^vllm-dgx-spark].

## Relationships

- Uses [vLLM Memory Conservation](vllm-memory-conservation.md) — unified-pool reading of `--gpu-memory-utilization`, `--max-model-len`, and `--max-num-seqs` caps.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — pre-quantized NVFP4 checkpoint handling with `--quantization` left unset.
- Uses [vLLM b12x Quantized Linear and MoE Backends](vllm-b12x-quantization-backends.md) — `auto` FP4 backend selection including FlashInfer CUTLASS paths on `sm_121`.
- Uses [vLLM Metrics and Observability](vllm-metrics.md) — Prometheus `/metrics` KV-cache, token-counter, and TTFT/ITL signals.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — default-on V1 prefix reuse behind the agentic-turn behavior.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — graphs-on default for the measured recipe.
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — Nemotron-3-Super MTP as the speculative path to evaluate.
- Uses [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — FP8 KV cache as a validate-before-use memory option.
- Uses [vLLM Tool Calling](vllm-tool-calling.md) and [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — tool-call and reasoning parser flags in the serving command.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — two-Spark `--tensor-parallel-size 2` over ConnectX-7.
- Uses [vLLM Startup Optimization](vllm-startup-optimization.md) — JIT pre-warm ping and fast weight-loading paths.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — Spark as the accelerator-backed local-serving point versus CPU-first consumer inference.
- Related to [Distributed Inference Deployment Blueprints](distributed-inference-blueprints.md) — single-Spark small-batch versus multi-Spark edge inference shape.

## Coverage limits

- SVG figures were inspected via titles, descriptions, and markup; office and demo-crowd JPG photos were not visually inspected beyond captions[^vllm-dgx-spark].
- Linked vLLM Recipes, CLI/Docker/OpenAI-server/metrics docs, NVIDIA Spark guides, Docker Hub tags, Hugging Face model pages, and the `vllm-spark-game` repository were not inspected beyond the source's description[^vllm-dgx-spark].
- Benchmark numbers are recipe-specific single-Spark results for the stated image track, context, graphs, backend, and scheduling settings; treat decode and prefill rates as deployment snapshots, not general Spark or vLLM ceilings[^vllm-dgx-spark].

[^vllm-dgx-spark]: Inferact, vLLM on the DGX Spark: Architecture, Configuration, and Local Evaluation — `../raw/2026-06-01-vllm-dgx-spark/index.md` (vLLM blog, published 2026-06-01), covering GB10 unified memory and `sm_121`, NVFP4 MoE model fit, continuous batching and paged KV cache, OpenAI-compatible streaming, Prometheus signals, official image track, pre-staging, `vllm serve` flags and defaults, JIT pre-warm and fast weight loading, demo-versus-throughput tuning, Docker invocation, vllm-spark-game workload, and five-scenario Nemotron-3-Super single-Spark evaluation.
