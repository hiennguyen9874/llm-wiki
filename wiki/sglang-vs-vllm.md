---
type: Synthesis
title: SGLang and vLLM Comparison
description: Workload-oriented comparison of SGLang and vLLM across serving architecture, caching, routing, disaggregation, extensibility, LoRA, structured output, quantization, observability, and RL integration.
tags: [sglang, vllm, comparison, inference-serving]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: sgl-overview
    resource: sglang-advanced-features-overview.md
    title: SGLang Advanced Features Overview
  - id: vllm-architecture
    resource: vllm-v1-process-architecture.md
    title: vLLM V1 Process Architecture
  - id: sgl-cache
    resource: sglang-unified-radix-cache.md
    title: SGLang Unified Radix Cache
  - id: vllm-cache
    resource: vllm-prefix-caching.md
    title: vLLM Prefix Caching
  - id: sgl-gateway
    resource: sglang-model-gateway.md
    title: SGLang Model Gateway
  - id: vllm-plugins
    resource: vllm-plugin-system.md
    title: vLLM Plugin System
  - id: sgl-pd
    resource: sglang-pd-disaggregation.md
    title: SGLang PD Disaggregation
  - id: vllm-pd
    resource: vllm-disaggregated-prefill.md
    title: vLLM Disaggregated Prefill
  - id: sgl-lora
    resource: sglang-lora-serving.md
    title: SGLang LoRA Serving
  - id: vllm-lora
    resource: vllm-lora-adapters.md
    title: vLLM LoRA Adapters
  - id: sgl-structured
    resource: sglang-structured-outputs.md
    title: SGLang Structured Outputs
  - id: vllm-structured
    resource: vllm-structured-outputs.md
    title: vLLM Structured Outputs
  - id: sgl-rl
    resource: sglang-for-rl.md
    title: SGLang for RL Systems
  - id: vllm-sleep
    resource: vllm-sleep-mode.md
    title: vLLM Sleep Mode
  - id: sgl-observability
    resource: sglang-observability.md
    title: SGLang Observability
  - id: vllm-observability
    resource: vllm-metrics.md
    title: vLLM Metrics and Observability
  - id: atomic-sgl-vllm
    resource: ../raw/sglang-vs-vllm/index.md
    title: "SGLang vs vLLM: Which Inference Engine Should You Use? (2026)"
  - id: jarvis-h100-3way
    resource: ../raw/vllm-sglang-trtllm-comparison/index.md
    title: "SGLang vs vLLM: H100 Benchmarks, with TensorRT-LLM"
  - id: privocto-vllm-sglang
    resource: ../raw/vllm-sglang/index.md
    title: "vLLM vs SGLang: Enterprise LLM Inference Comparison"
  - id: spheron-2026
    resource: ../raw/vllm-vs-sglang-2026/index.md
    title: "vLLM vs SGLang 2026: RadixAttention vs PagedAttention Benchmarks"
  - id: deepinfra-vllm-sglang
    resource: ../raw/vllm-vs-sglang/index.md
    title: "vLLM vs SGLang: Performance, Features & Deployment Compared"
  - id: mayhem-selfhosted
    resource: ../raw/2069090022117019928/index.md
    title: "SGLang vs vLLM: A Technical Comparison for Self-Hosted Deployments"
---

SGLang and vLLM substantially overlap as high-performance inference runtimes, but their documented strengths point in different directions. SGLang is especially cohesive for cache-aware multi-turn and agentic serving, a dedicated routing tier, prefill/decode topologies, and RL rollout control. vLLM presents a particularly explicit engine/process architecture and a broad out-of-tree Python plugin model. For ordinary OpenAI-compatible serving either can fit; the deciding factors should be the exact model, hardware, quantization, attention backend, and measured workload rather than a universal performance claim.[^sgl-overview][^vllm-architecture]

## Capability comparison

| Area | SGLang | vLLM |
| --- | --- | --- |
| Serving shape | Engine plus a Rust Model Gateway that can own worker lifecycle, cache-aware routing, PD routing, conversations, Responses API loops, MCP, retries, health, and circuit breaking.[^sgl-gateway] | Offline `LLM` and online `vllm serve`; V1 explicitly separates API server, engine core, GPU workers, and an optional DP coordinator.[^vllm-architecture] |
| Prefix and hybrid caching | Token-keyed radix topology with component-specific FULL, sliding-window, and Mamba reuse; HiCache extends identity across GPU, host, and external tiers, with session-aware eviction.[^sgl-cache] | Hash-based reuse of complete KV blocks with LRU eviction, reproducible or faster hash options, per-request cache salts, and hybrid/Mamba extensions.[^vllm-cache] |
| Extensibility | Gateway-side WASM middleware plus numerous selectable engine backends and hooks; the documented stack emphasizes integrated serving controls.[^sgl-gateway][^sgl-overview] | Standard Python entry-point plugins for models, platforms, IO processors, stat loggers, and HTTP endpoints, plus out-of-tree worker/backend integration.[^vllm-plugins] |
| Prefill/decode disaggregation | Mooncake, NIXL, and Ascend transfer paths integrated with a PD-aware router; separate stage tuning and multi-node examples are documented.[^sgl-pd] | Experimental connector abstraction with NIXL, Mooncake, LMCache, MoRI-IO, offload, and custom connector paths; explicitly targets independent TTFT/ITL tuning and tail-ITL control, not throughput improvement.[^vllm-pd] |
| LoRA | Multi-LoRA batching, dynamic load/unload, GPU pinning, LRU/FIFO policies, backend selection, and optional overlap loading.[^sgl-lora] | Static, dynamic, and resolver-based on-demand loading; in-place reload, model lineage, mixed MoE adapter formats, and multimodal defaults.[^vllm-lora] |
| Structured output | JSON Schema, regex, EBNF, and structural tags through XGrammar, Outlines, or llguidance, online and offline.[^sgl-structured] | Choice, JSON Schema, regex, EBNF, and structural tags through XGrammar or Guidance, online and offline.[^vllm-structured] |
| RL and colocation | Fine-grained memory release/resume, disk/tensor/distributed weight refit, pause/continue generation, deterministic mode, and gateway routing are documented as one RL toolbox.[^sgl-rl] | Sleep levels can offload or discard weights and KV cache with partial wake-up for RLHF and colocation; broader customization can be assembled through engine and plugin APIs.[^vllm-sleep][^vllm-plugins] |
| Observability | Opt-in Prometheus metrics and request logging, plus request dump/replay and five-minute pre-crash dump/replay; gateway adds routing metrics and tracing.[^sgl-observability][^sgl-gateway] | Detailed V1 request/server metric model, Prometheus and periodic logging publishers, KV-residency sampling, and explicit interval semantics across frontend and engine core.[^vllm-observability] |

Both also document automatic and manually selected attention backends, speculative decoding, quantization, tensor/data/pipeline/expert parallelism, multimodal serving, tool calling, reasoning parsing, and OpenAI-compatible APIs. Feature presence alone therefore rarely decides the choice.[^sgl-overview]

## Reported benchmarks (vendor-cited, unverified)

An Atomic Chat comparison cites two head-to-head throughput snapshots. Both are reported without linked methodology or reproducible harness details, so treat them as directional vendor-cited evidence, not verified results.[^atomic-sgl-vllm]

Unique-prompt workload — Llama 3.3 70B Instruct in FP8 on H100, 50 concurrent requests with unique prompts:[^atomic-sgl-vllm]

| Metric | SGLang | vLLM |
| --- | --- | --- |
| Throughput | ~1,920 tok/s | ~1,850 tok/s |
| Difference | +3.8% | — |
| Time per output token | ~20 ms | ~20 ms |

Prefix-heavy workload with high prefix reuse, such as repeated system prompts and conversation context:[^atomic-sgl-vllm]

| Metric | SGLang | vLLM |
| --- | --- | --- |
| Throughput | ~16,200 tok/s | ~12,500 tok/s |
| Throughput difference | +29% | — |
| Time to first token, 1 request | ~42 ms | ~45 ms |
| Time to first token, 100 requests | ~710 ms | ~740 ms |

The source attributes the larger prefix-heavy gap to KV-cache reuse: shared prefixes skip more prefill work under SGLang's RadixAttention. The stated takeaway is that unique-prompt performance is similar, within a few percent, while repeated-context workloads favor SGLang in these snapshots.[^atomic-sgl-vllm]

## Independent H100 three-way benchmark (JarvisLabs 2026)

A third-party H100 benchmark adds TensorRT-LLM as an engine-first path and sweeps concurrency from 60 to 600 plus saturation across Qwen2.5-7B-Instruct, Qwen3-30B-A3B, and Qwen3-32B on ShareGPT chat and RULER 16K long-context workloads; full detail is compiled in [vLLM vs SGLang vs TensorRT-LLM H100 Benchmark](vllm-sglang-trtllm-h100-benchmark.md).[^jarvis-h100-3way]

In those tested configurations vLLM was the strongest general default for combined first-token latency and output throughput, SGLang won decode latency on the 7B and 30B-A3B 16K runs at the cost of higher first-token latency, and TensorRT-LLM showed stable decode kernels on chat but sharply higher first-token latency under load with the published engine builds.[^jarvis-h100-3way] Exact framework versions are not recorded, several ShareGPT TensorRT-LLM builds used `max_batch_size` values below the tested concurrency sweep, and all runs used `vllm bench serve`, so treat the ranking as configuration-specific and validate on deployed versions.[^jarvis-h100-3way]

## Enterprise vendor snapshot (PrivOcto 2026)

A PrivOcto enterprise comparison adds a third vendor-cited snapshot set. It names only one model/hardware pair (Qwen3-Coder-30B on H200 for a single TTFT comparison); the remaining TTFT, throughput, memory, and structured-output numbers are reported without model, precision, harness, or version details, so treat all of them as directional and configuration-specific, not verified results.[^privocto-vllm-sglang]

Reported time-to-first-token snapshots:[^privocto-vllm-sglang]

| Condition | SGLang | vLLM |
| --- | --- | --- |
| H100, batch size 1 | 340 ms | 123 ms |
| Low concurrency, c=1 | 583 ms | 2,141 ms |
| Concurrency c=1 to c=10 | 583 ms rising to 2,525 ms | ~2,171 ms, described as consistent |
| H200, Qwen3-Coder-30B | 2,333 ms (12.6% faster) | 2,669 ms |

Reported throughput snapshots:[^privocto-vllm-sglang]

| Condition | SGLang | vLLM |
| --- | --- | --- |
| Throughput at c=1 | 220 tok/s | 61 tok/s |
| Throughput at c=100 | 4,587 tok/s | 4,432 tok/s |
| Overall throughput on A100 | 1,532 tok/s | 661 tok/s |
| Batch size 64 on H100 | 460 tok/s | not reported |

Additional vendor-cited claims in the same source:[^privocto-vllm-sglang]

- Memory footprint: ~40GB per GPU for SGLang versus ~75GB for vLLM with tensor parallelism (47% lower), and 7GB versus 21GB on A10; no model or configuration is given.
- Batch scaling shape: vLLM near-linear to c=50 (~40x) before plateauing at c=100+, while SGLang starts strong with slower scaling at higher concurrency.
- Multi-turn chat: 4.7x-5x SGLang speedup attributed to RadixAttention prefix caching, with ~10% prefix-caching boost and 50%+ production cache-hit rates claimed.
- Structured JSON: 4,200 tok/s at 99.8% validity for SGLang with xGrammar versus 820 tok/s at 85% for vLLM with Guidance; the backends differ, so this is a backend-path comparison, not a clean engine comparison.
- Architecture framing matches the compiled cache contrast: PagedAttention in fixed 16-256-token pages with block-table mapping and under-4% waste versus 60-80% in traditional systems, against RadixAttention radix-tree prefix sharing; the cover diagram was inspected and carries the same throughput-versus-flexibility framing with no additional numbers.
- Rough cost framing: self-hosted vLLM at USD 0.50-1.00 per million tokens versus USD 20-60 for API services, and 9-10x reduction for SGLang quantized-SLM versus FP16 deployments; no hardware or utilization basis is given.
- Install, Docker, `vllm serve`, and tensor/pipeline-parallel launch examples were excluded as version-sensitive operations rather than durable selection evidence.

## Spheron 2026 Llama and MoE benchmark

A Spheron comparison on Llama 3.3 70B Instruct FP8 (H100 single-GPU, vLLM v0.18.0 without MRV2 versus SGLang v0.5.9) plus one DeepSeek V4 Flash FP8 point on 8x H100 adds versioned TTFT/throughput evidence; full tables are compiled in [vLLM vs SGLang 2026 Spheron Benchmark](vllm-vs-sglang-2026-spheron-benchmark.md).[^spheron-2026]

Unique-prompt throughput is effectively tied within 5% (for example 1,850 versus 1,920 tok/s at c=50), matching the Atomic near-parity snapshot.[^spheron-2026] With 80% shared 512-token prefix, SGLang TTFT p50 drops from 310 ms to 195 ms at c=50 (37% lower) and from 620 ms to 370 ms at c=100; p95 drops from 580 ms to 340 ms at c=50.[^spheron-2026] Overlap scaling at c=50 runs roughly 7% TTFT reduction at 20% overlap, 15% at 40%, 24% at 60%, 37% at 80%, and 44% at 95%, supporting the source 60%-overlap rule for benchmarking SGLang first.[^spheron-2026] Enabling vLLM APC on the simple shared-system-prompt case narrows the c=10 gap to roughly 15-18%.[^spheron-2026]

The MoE point (DeepSeek V4 Flash, TP8 plus expert parallelism) is within 7% on unique prompts (580 versus 620 tok/s; 890 versus 855 ms TTFT p50) while the 80%-prefix TTFT gap persists (730 versus 520 ms), so workload shape matters more than dense versus MoE in this snapshot.[^spheron-2026] Warm-grammar structured output favors SGLang on repeated schemas (for example nested JSON +18% vLLM versus +4% SGLang warm; deeply nested +42% versus +6%), while speculative decoding favors vLLM (mature Eagle3/EAGLE2 versus experimental SGLang at v0.5.9) and Blackwell B200/GB200 favors vLLM via FlashAttention 4 in v0.17.0+.[^spheron-2026] Cost arithmetic uses `(hourly_rate / 3600) / (tokens_per_sec / 1_000_000)` on dated 24 Jun 2026 Spheron rates; prefix-heavy H100 on-demand is framed as $0.61 vLLM no-APC versus $0.54 vLLM APC-on versus $0.44 SGLang per 1M tokens.[^spheron-2026]

## DeepInfra workload-first framework

A DeepInfra comparison adds benchmark-validity rules and self-host economics rather than new head-to-head runs; full method is compiled in [vLLM vs SGLang DeepInfra Decision Framework](vllm-vs-sglang-deepinfra-framework.md).[^deepinfra-vllm-sglang]

Its version-mismatch critique targets the widely repeated 29% SGLang lead (16,215 versus 12,553 tok/s on Llama 3.1 8B bf16, H100): the paired releases SGLang v0.2.3 and vLLM 0.11.0 are roughly two years apart, so the number cannot rank either engine today. Its unit-conflation warning separates RunPod single-stream decode rates (35.0 versus 32.8 tok/s, 2x H100, 70B distill, 7k context) from aggregate saturated throughput — one predicts per-reader text speed, the other node capacity before queueing.[^deepinfra-vllm-sglang] The stated usability rule is version-matched, flag-matched, and run on your request distribution.[^deepinfra-vllm-sglang]

Workload triage uses four signals: prefix-reuse ratio (below ~20% stops discriminating; cached runs gain ~20% once hits land), batch shape (saturated offline packing versus bursty interactive TTFT), structured-output share with per-schema compiler cost, and dense versus MoE topology.[^deepinfra-vllm-sglang] The same-day prefix probe streams a real 8k+ preamble twice and reads cold-versus-warm TTFT delta at production concurrency, controlling for replica placement, cache aging, and HBM eviction pressure.[^deepinfra-vllm-sglang] Self-host break-even is framed at 8x H100 (~$11,700/month) versus $0.355 per 1M-in/250k-out unit, requiring roughly 12,000 input tok/s sustained; bursty 10-20% utilization, cached-input pricing, and engineer-months favor managed endpoints until saturation, regulatory placement, or modification needs flip the choice.[^deepinfra-vllm-sglang]

## Self-hosted Mayhem snapshots (June 2026)

A Mayhem4Markets X-thread comparison aimed at workstation and server self-hosting adds second-hand Q2 2026 snapshots and a workstation GPU curve; full tables are compiled in [SGLang vs vLLM Self-Hosted Comparison (Mayhem 2026)](sglang-vs-vllm-self-hosted-mayhem.md).[^mayhem-selfhosted]

At high concurrency on Llama-3.3-70B 4-bit with 8x H200, the cited IoT Digital Twin run is about 5,300 tok/s vLLM versus 5,450 tok/s SGLang with narrow lead swaps by concurrency; on H100 80GB the cited Turion run has SGLang ahead up to 30B at 50 requests with single-digit gaps at 70B+, and tighter SGLang p95 TTFT at 100+ requests.[^mayhem-selfhosted] The cited SemiAnalysis InferenceXv2 point is SGLang on GB300 NVL72 with DeepSeek R1 at 25x versus H200 baseline, attributed to piecewise CUDA graphs default since v0.5.10 plus HiSparse sparse attention.[^mayhem-selfhosted] The workstation curve on Qwen3-Coder-30B AWQ 8K context via vLLM is about 4,570 tok/s on RTX 5090 versus 8,425 tok/s on RTX PRO 6000 Blackwell, with 70B FP8 fitting on the PRO 6000 single card but not the 5090; the chart image extends the same table to RTX 4090, H100 PCIe, H200, and B200 rows and footers the data to CloudRift while the prose says VRLA Tech, preserved unresolved.[^mayhem-selfhosted]

The source repeats the familiar cache rule — near-zero gap on unique prompts, about 30% standard and up to 6.4x prefix-heavy SGLang advantage, 3-5x effective prefill-latency gain above roughly 60% overlap — and frames single-GPU differences as compressed because the GPU bottlenecks first.[^mayhem-selfhosted] Its durable deltas beyond existing pages are the self-hosted decision framing, the Anthropic Messages plus gRPC versus SGLang-DSL API contrast, the SGLang RL-rollout-backend role in AReaL/Miles/verl/Tunix, and the explicit workstation fit notes.[^mayhem-selfhosted]

## Contradictions

- PrivOcto internal TTFT ranking flips at nominally identical low concurrency (vLLM faster at batch size 1 on H100, SGLang faster at c=1) with no reconciling configuration; neither reading can be used alone.[^privocto-vllm-sglang]
- PrivOcto's large SGLang throughput and memory leads and its TTFT-instability claim for SGLang sit against the Atomic near-parity unique-prompt snapshot (+3.8% SGLang), the Spheron versioned unique-prompt tie (within 5% on Llama 3.3 70B FP8/H100), and the JarvisLabs configuration-specific vLLM default on Qwen/H100; the sources use different models, hardware, concurrency, and harnesses, so no universal ranking follows.[^privocto-vllm-sglang][^atomic-sgl-vllm][^spheron-2026][^jarvis-h100-3way]
- PrivOcto's xGrammar-versus-Guidance JSON gap (4,200 versus 820 tok/s) does not transfer to an engine-level structured-output ranking because both engines document multiple backends; select by parser and backend requirements instead.[^privocto-vllm-sglang][^sgl-structured][^vllm-structured]

## Cache-behavior contrast

SGLang matches each request with a longest-prefix lookup against a radix tree whose nodes map token-sequence prefixes to GPU KV-cache blocks; only the new suffix needs prefill, and the scheduler groups requests with shared prefixes to raise reuse above arrival-order scheduling.[^atomic-sgl-vllm] Practical limits stated in the source:[^atomic-sgl-vllm]

- The main gain is reduced prefill cost and time-to-first-token; decode behavior after generation starts is generally unchanged.
- Cached blocks and active sequences share the GPU memory pool configured by `--mem-fraction-static`; pressure evicts older entries under LRU policy.
- Gains scale with prefix reuse; low-overlap traffic sees limited benefit while still paying cache-management overhead.
- The cache is process-local, so a server restart clears it.

vLLM manages KV cache in fixed-size pages rather than per-request contiguous buffers, reducing fragmentation and fitting more active sequences; continuous batching admits waiting requests as sequences finish instead of waiting on a fixed batch.[^atomic-sgl-vllm] vLLM also has automatic prefix caching that reuses identical KV blocks across requests. The source contrasts granularity and scheduling: vLLM reuse operates at page granularity, while SGLang uses radix-tree matching plus shared-prefix-aware scheduling, which can matter most for long repeated prompts in agent systems.[^atomic-sgl-vllm]

For triage, the source proposes estimating prefix reuse as repeated prefix tokens divided by total prompt tokens, where the repeated portion is usually system prompts, tool definitions, and carried-forward conversation history.[^atomic-sgl-vllm]

## Practical selection notes

The following operational claims come from the vendor comparison and are folded here as source-attributed guidance, not independently verified findings:[^atomic-sgl-vllm]

- Model artifacts: standard Hugging Face `safetensors` checkpoints usually load in either engine; both cover FP16, BF16, FP8, AWQ, and GPTQ in the source's account, while GGUF is primarily a llama.cpp-runtime format rather than a preferred SGLang or vLLM input.
- Platform: both are primarily Linux server runtimes; Windows deployment is described through WSL2 or Docker.
- Provenance reported by the source: SGLang originated at UC Berkeley's Sky Computing Lab, is hosted by LMSYS, joined the PyTorch ecosystem in 2025, and is cited as serving Grok-scale deployments; vLLM originated at UC Berkeley as the source of PagedAttention and continuous batching, with broad model-release and integration coverage.
- Recent features named by the source without independent verification: SGLang CPU-based scheduling, prefill-decode disaggregation, speculative decoding including V2, structured output through xgrammar, plus vLLM Model Runner V2 and EAGLE 3.1 speculative decoding.
- Interchangeability: client code often needs only a different server URL, but launch options, parallelism settings, hardware configuration, and supported quantization formats do not transfer directly.
- Prefer SGLang when requests share long prefixes, structured output is needed at high throughput via the xgrammar path, AMD GPUs are targeted, or the model ships SGLang-specific kernels; expect less advantage with little prefix reuse.
- Prefer vLLM when prompts are mostly unique, broad model/hardware compatibility matters, distributed multi-GPU or multi-node serving including Ray-based workflows is required, or existing tooling already standardizes on vLLM.

## Decision guidance

The following is synthesis from the documented capabilities, not a benchmark result:

- Prefer **SGLang** when the application is dominated by repeated-prefix or multi-turn agent traffic, needs an integrated cache-aware gateway, uses hierarchical cache tiers, requires tightly integrated PD/EPD serving, or needs frequent rollout weight updates and pause/resume control.[^sgl-cache][^sgl-gateway][^sgl-pd][^sgl-rl]
- Prefer **vLLM** when the application benefits most from a clearly separated general-purpose engine architecture, offline/online API symmetry, or out-of-tree Python plugins for models, platforms, processing, metrics, and endpoints.[^vllm-architecture][^vllm-plugins]
- Treat **LoRA and structured output as workload-specific ties**: each has meaningful differentiators, so select by adapter lifecycle, parser/backend requirements, and model support rather than the headline feature.[^sgl-lora][^vllm-lora][^sgl-structured][^vllm-structured]
- For **latency or throughput**, benchmark both on the same model artifact, precision, attention backend, context-length distribution, concurrency, prefix-reuse rate, and output length. Head-to-head numbers compiled here are the vendor-cited Atomic and PrivOcto snapshots plus the configuration-specific JarvisLabs H100 sweep detailed in [vLLM vs SGLang vs TensorRT-LLM H100 Benchmark](vllm-sglang-trtllm-h100-benchmark.md), the versioned Spheron Llama/MoE snapshots detailed in [vLLM vs SGLang 2026 Spheron Benchmark](vllm-vs-sglang-2026-spheron-benchmark.md), and the DeepInfra validity and workload-triage rules detailed in [vLLM vs SGLang DeepInfra Decision Framework](vllm-vs-sglang-deepinfra-framework.md), not a universal ranking.[^atomic-sgl-vllm][^privocto-vllm-sglang][^jarvis-h100-3way][^spheron-2026][^deepinfra-vllm-sglang]

## Evaluation checklist

1. Confirm the exact model and quantized checkpoint load in each runtime.
2. Verify the target GPU/accelerator supports the intended attention, MoE, and KV-cache kernels.
3. Benchmark TTFT, inter-token latency, throughput, and memory at realistic prompt/output lengths and concurrency.
4. Repeat with the real prefix-sharing and multi-turn pattern; caching can change the result materially. Estimate prefix hit rate as repeated prefix tokens divided by total prompt tokens.[^atomic-sgl-vllm]
5. Include startup time, failure recovery, metrics, routing, and adapter churn if they matter operationally.
6. Pin versions and record all non-default flags; both projects' backend and compatibility matrices evolve quickly.

## Relationships

- Compares [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) with [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) as the broad entry points to each serving stack.
- Uses [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) and [vLLM Prefix Caching](vllm-prefix-caching.md) for the central cache-design contrast.
- Uses [vLLM vs SGLang vs TensorRT-LLM H100 Benchmark](vllm-sglang-trtllm-h100-benchmark.md) for concurrency-swept Qwen TTFT/decode/throughput evidence with TensorRT-LLM as a third path.
- Uses [vLLM vs SGLang 2026 Spheron Benchmark](vllm-vs-sglang-2026-spheron-benchmark.md) for versioned Llama 3.3 70B and DeepSeek V4 Flash unique versus prefix-heavy TTFT/throughput, structured-output, speculative-decoding, and cost evidence.
- Uses [vLLM vs SGLang DeepInfra Decision Framework](vllm-vs-sglang-deepinfra-framework.md) for benchmark-validity checks, four workload signals, TTFT prefix probe, and self-host versus managed-endpoint economics.
- Uses [SGLang Model Gateway](sglang-model-gateway.md) and [vLLM Plugin System](vllm-plugin-system.md) for integrated routing versus out-of-tree extensibility.

## Coverage limits

- This comparison is based on the repository's compiled documentation snapshots, not current upstream source inspection.
- The only head-to-head performance numbers in this page are vendor-cited snapshots without linked methodology (Atomic, PrivOcto) plus the configuration-specific JarvisLabs H100 sweep and the versioned Spheron Llama/MoE snapshots; they support no universal speed, efficiency, stability, ecosystem-size, or model-coverage ranking. The DeepInfra source adds validity rules and workload triage, not new runs.[^atomic-sgl-vllm][^privocto-vllm-sglang][^jarvis-h100-3way][^spheron-2026][^deepinfra-vllm-sglang]
- The Atomic Chat source's quantization, hardware, provenance, and feature-recency claims are compiled as source-attributed guidance, not independently verified findings; its four illustrative website/UI screenshots were not inspected beyond captions because they carry no additional performance claims.[^atomic-sgl-vllm]
- The JarvisLabs three-way results are configuration-specific Qwen/H100/BF16 evidence without recorded framework versions; see [vLLM vs SGLang vs TensorRT-LLM H100 Benchmark](vllm-sglang-trtllm-h100-benchmark.md) for scope and per-workload takeaways.[^jarvis-h100-3way]
- The source's Atomic Chat local-inference product pitch was excluded as non-durable vendor promotion.
- The PrivOcto source's install, Docker, `vllm serve`, launch-flag, cost-per-token, hardware-support, and model-support claims were treated as version-sensitive operations or unverified vendor framing; only the workload-selection signal (high-concurrency predictable serving versus prefix-heavy agent and structured-output work) is carried above, with limits intact.[^privocto-vllm-sglang]
- Feature maturity can vary by model, hardware, backend, and release even when both projects document a similarly named capability.

[^sgl-overview]: [SGLang Advanced Features Overview](sglang-advanced-features-overview.md).
[^vllm-architecture]: [vLLM V1 Process Architecture](vllm-v1-process-architecture.md).
[^sgl-cache]: [SGLang Unified Radix Cache](sglang-unified-radix-cache.md).
[^vllm-cache]: [vLLM Prefix Caching](vllm-prefix-caching.md).
[^sgl-gateway]: [SGLang Model Gateway](sglang-model-gateway.md).
[^vllm-plugins]: [vLLM Plugin System](vllm-plugin-system.md).
[^sgl-pd]: [SGLang PD Disaggregation](sglang-pd-disaggregation.md).
[^vllm-pd]: [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md).
[^sgl-lora]: [SGLang LoRA Serving](sglang-lora-serving.md).
[^vllm-lora]: [vLLM LoRA Adapters](vllm-lora-adapters.md).
[^sgl-structured]: [SGLang Structured Outputs](sglang-structured-outputs.md).
[^vllm-structured]: [vLLM Structured Outputs](vllm-structured-outputs.md).
[^sgl-rl]: [SGLang for RL Systems](sglang-for-rl.md).
[^vllm-sleep]: [vLLM Sleep Mode](vllm-sleep-mode.md).
[^sgl-observability]: [SGLang Observability](sglang-observability.md).
[^vllm-observability]: [vLLM Metrics and Observability](vllm-metrics.md).
[^atomic-sgl-vllm]: SGLang vs vLLM: Which Inference Engine Should You Use? (2026) — `../raw/sglang-vs-vllm/index.md`, covering RadixAttention versus PagedAttention behavior, safetensors and quantization guidance, Linux deployment, cache-aware scheduling limits, vendor-cited unique-prompt and prefix-heavy benchmarks, prefix-hit-rate triage, selection guidance, and interchangeability limits.
[^jarvis-h100-3way]: Jaydev Tonde, SGLang vs vLLM: H100 Benchmarks, with TensorRT-LLM — `../raw/vllm-sglang-trtllm-comparison/index.md` (jarvislabs.ai, 2026-05-18), covering H100 setup, Qwen server/client commands, ShareGPT and RULER 16K sweeps, TTFT/TPOT/ITL/throughput tables, and configuration-sensitive TensorRT-LLM TTFT interpretation.
[^privocto-vllm-sglang]: vLLM vs SGLang: Enterprise LLM Inference Comparison — `../raw/vllm-sglang/index.md` (privocto.com, 2026-03-15), covering PagedAttention versus RadixAttention framing, H100/H200/A100 TTFT and throughput snapshots without linked methodology, TP and A10 memory claims, multi-turn and xGrammar-versus-Guidance JSON claims, cost framing, and install and deployment examples.
[^spheron-2026]: Mitrasish Mukherjee, vLLM vs SGLang 2026: RadixAttention vs PagedAttention Benchmarks — `../raw/vllm-vs-sglang-2026/index.md` (spheron.network, 2026-06-23), covering versioned Llama 3.3 70B FP8 unique and 80%-prefix TTFT/throughput tables, overlap-to-hit-rate scaling, DeepSeek V4 Flash MoE point, xgrammar warm/cold overhead, Eagle3/MTP status, Blackwell readiness, H100/H200 cost arithmetic on 24 Jun 2026 rates, and router and flag-migration notes.
[^deepinfra-vllm-sglang]: DeepInfra, vLLM vs SGLang: Performance, Features & Deployment Compared — `../raw/vllm-vs-sglang/index.md` (deepinfra.com), covering version-mismatched and unit-conflated benchmark critiques, PagedAttention versus RadixAttention origins with V1 and zero-overhead scheduler notes, 2026-07-14 release and star snapshots, four workload signals, streaming TTFT prefix-reuse probe with confounders, 8-GPU self-host versus per-token break-even arithmetic, self-host-win conditions, and engine selection guidance.
[^mayhem-selfhosted]: @Mayhem4Markets, SGLang vs vLLM: A Technical Comparison for Self-Hosted Deployments — `../raw/2069090022117019928/index.md` (x.com, 2026-06-22), covering PagedAttention versus RadixAttention behavior and APC configuration, IoT Digital Twin/Turion/SemiAnalysis Q2 2026 snapshots, workstation GPU scaling table also footered to CloudRift, hardware/model/quantization/API/install/spec-decoding/RL/community comparison, and self-hosted decision rules.
