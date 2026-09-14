---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts
- [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — Isolating vLLM-compile failures with tlparse logs and per-subsystem disable flags for Dynamo, dynamic shapes, Inductor, cache, and CUDAGraphs.
- [vLLM Attention Backends](vllm-attention-backends.md) — Selection, configuration, composite routing, and MLA/sparse variants for vLLM attention backends.
- [vLLM Batch Invariance](vllm-batch-invariance.md) — Deterministic batch-size-independent inference via VLLM_BATCH_INVARIANT with hardware, backend, and model coverage.
- [vLLM Context Extension via RoPE Scaling](vllm-context-extension.md) — Extending model context length with rope_parameters overrides via --hf-overrides and --max-model-len for offline and online inference.
- [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — Prefill and decode context-parallel strategies for long-context serving, including DCP KV-cache sharding and sizing guidance.
- [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — Configurable CUDA Graphs modes, runtime dispatcher, nested wrappers, and attention-backend compatibility for vLLM v1.
- [vLLM Custom Arguments](vllm-custom-arguments.md) — Passing out-of-spec SamplingParams and REST arguments via SamplingParams.extra_args and vllm_xargs for offline and online inference.
- [vLLM Custom Logits Processors](vllm-custom-logits-processors.md) — Authoring, loading, and invoking out-of-tree logits processors, including Adapter wrapping and FQCN, entry-point, and class-object loading.
- [vLLM CustomOp Dispatch and Registration](vllm-custom-op.md) — Platform-dispatched forward methods, compilation-config enablement, and in-tree versus out-of-tree registration for vLLM custom ops.
- [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — Replicated-weight data-parallel serving with internal, hybrid, and external load-balancing modes and MoE DP+EP coordination.
- [vLLM Disaggregated Encoder](vllm-disaggregated-encoder.md) — Separate vision-encoder and prefill/decode instances with EC-connector embedding transfer for independent scaling, lower TTFT, and shared encoder-cache reuse.
- [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — Separate prefill and decode vLLM instances with connector-mediated KV transfer to tune TTFT and ITL independently and control tail ITL without improving throughput.
- [vLLM Dual Batch Overlap (DBO)](vllm-dbo-dual-batch-overlap.md) — Overlapping MoE sparse all-to-all with compute by splitting batches into paired microbatches on ping-ponging CPU threads.
- [vLLM EC CPU Connector](vllm-ec-cpu-connector.md) — Local CPU-tier encoder-cache offload with optional NIXL peer-to-peer transfer for disaggregated vision encoding.
- [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — Budget-based CUDA Graphs capture and replay for vision encoders, with greedy packing, dual-path graphs, video support, and model opt-in protocol.
- [vLLM Endpoint Plugins](vllm-endpoint-plugins.md) — Out-of-tree HTTP routes for the vLLM OpenAI-compatible server via two-phase EndpointPlugin loading and EngineClient access.
- [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — LLMEngine, workers, model runner, model objects, and VllmConfig design rationale.
- [vLLM Entrypoints](vllm-entrypoints.md) — Offline LLM class versus online vllm serve server for model inference.
- [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — Expert-parallel MoE serving with EP=TP×DP sharding, all-to-all backends, EPLB rebalancing, and prefill/decode disaggregation.
- [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — Selecting vLLM modular MoE All2All backends and experts kernels by activation format, quantization, and compatibility families.
- [vLLM Fused MoE Modular Kernel](vllm-fused-moe-modular-kernel.md) — Architecture, components, initialization, and extension workflow for vLLM's modular fused MoE kernel.
- [vLLM HiSparse Local KV Offload](vllm-hisparse.md) — Local host-tier KV offload for sparse attention with coordinator-owned host blocks, spill-before-free residency, and fused GPU hot lookup.
- [vLLM Hugging Face Integration](vllm-huggingface-integration.md) — Resolving model IDs to config, tokenizer, and weights via Hugging Face Hub or local path, with config-class and architecture-registry mapping.
- [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — Unified page-size grouping, per-group allocation, and intersected prefix caching for hybrid-attention models.
- [vLLM IndexCache for DeepSeek Sparse Attention](vllm-index-cache.md) — Reusing DeepSeek DSA top-k indices across layers via use_index_cache, index_topk_freq, and index_topk_pattern.
- [vLLM Interleaved Thinking](vllm-interleaved-thinking.md) — Reasoning between tool calls for chained tool use with intermediate decisions.
- [vLLM IO Processor Plugins](vllm-io-processor-plugins.md) — Pre- and post-processing plugins for pooling models that map custom inputs to model prompts and model outputs to custom outputs.
- [vLLM IR Functional Intermediate Representation](vllm-ir.md) — Functional IR dialect separating op semantics from kernel implementations with late priority-based dispatch and compile lowering.
- [vLLM KV Offloading Connector](vllm-kv-offloading.md) — Extending vLLM prefix cache with CPU and tiered offload via OffloadingConnector, covering specs, secondary tiers, P2P protocol, tuning, and per-request selective offload.
- [vLLM Logits Processors](vllm-logits-processors.md) — Stateful batch-granular logits transforms, BatchUpdate lifecycle, argmax-invariant sampling shortcut, and built-in versus custom extension model.
- [vLLM LoRA Adapters](vllm-lora-adapters.md) — Per-request LoRA serving offline and online, including static serving, dynamic loading, MoE format mixing, lineage, multimodal defaults, and tuning.
- [vLLM LoRA Resolver Plugins](vllm-lora-resolver-plugins.md) — On-demand LoRA adapter discovery and loading at request time via LoRAResolver plugins for filesystem, Hugging Face Hub, and custom backends.
- [vLLM Metrics and Observability](vllm-metrics.md) — V1 metrics collection, Prometheus and logging publishers, interval definitions, and deprecation and future-work policy for vLLM observability.
- [vLLM Model Runner V2](vllm-model-runner-v2.md) — Cleaner, async-first, GPU-native reimplementation of the vLLM model runner with decoupled persistent batches, staged writes, Triton sampling, and explicit CUDA-graph management.
- [vLLM Mooncake Connector](vllm-mooncake-connector.md) — RDMA-based disaggregated prefill/decode KV transfer via Mooncake with producer/consumer roles, bootstrap and RDMA-registration tuning, and proxy fan-out.
- [vLLM Mooncake Store Connector](vllm-mooncake-store-connector.md) — Shared distributed KV-cache pool via Mooncake store for CPU/disk offloading and cross-instance prefix reuse, with single-node, disaggregated, and standalone-store deployments.
- [vLLM MoRI-IO Connector](vllm-moriio-connector.md) — ROCm MoRI-IO disaggregated prefill/decode KV transfer with WRITE/READ modes, RDMA/xGMI transports, control-plane ports, and vllm-router proxy routing.
- [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — Placeholder-to-input correspondence via HF-processor replay, dummy text, prompt updates, output caching, and GPU-fused normalization.
- [vLLM Multimodal Inputs](vllm-multimodal-inputs.md) — Passing image, video, audio, embedding, and cached UUID inputs to multimodal models offline and via OpenAI-compatible serving.
- [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md) — Feature compatibility matrix, handshake requirements, KV layout, and quantized-cache rules for NixlConnector disaggregated prefill/decode.
- [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) — Installing, configuring, deploying, and observing NixlConnector for vLLM disaggregated prefill/decode, including bidirectional multi-turn transfer.
- [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) — Heartbeat-renewed short leases letting prefill reclaim KV blocks quickly on decode failure while keeping them alive under decode overload.
- [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — Push-based disaggregated prefill/decode where prefill WRITEs KV directly into decode's pre-allocated blocks via a dedicated writer thread and PUSH_REG registrations.
- [vLLM Optimization Levels](vllm-optimization-levels.md) — Preset -O0 through -O3 flags trading startup time for performance via compilation, CUDA-graph, fusion, and autotune defaults.
- [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — Historical vLLM multi-head query attention CUDA kernel over paged KV cache, covering query/key/value data paths, softmax reduction, and output writeback.
- [vLLM Per-Request Metrics](vllm-per-request-metrics.md) — Per-request timing metrics returned in API responses via --enable-per-request-metrics for billing, SLA monitoring, and latency analysis.
- [vLLM Plugin System](vllm-plugin-system.md) — Discovery, loading, and plugin groups for extending vLLM out-of-tree via Python entry points and VLLM_PLUGINS filtering.
- [vLLM Prefix Caching](vllm-prefix-caching.md) — Enabling, workloads, limits, and hash-based full-block reuse in vLLM v1 with LRU eviction, touch-on-hit allocation, cache-salt isolation, and Mamba fine-grained option.
- [vLLM Prompt Embedding Inputs](vllm-prompt-embeds.md) — Passing precomputed prompt/token embeddings directly to vLLM offline and via OpenAI-compatible Completions and Chat APIs.
- [vLLM Python Multiprocessing Method Selection](vllm-python-multiprocessing.md) — Best-effort fork/spawn selection, library-use constraints, and worker configuration for vLLM multiprocessing.
- [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — Separate reasoning and content fields for thinking models via reasoning parsers, thinking toggles, budgets, and response controls.
- [vLLM Sleep Mode](vllm-sleep-mode.md) — Releasing GPU memory via levelled sleep/wake with partial weights and KV-cache restore for RLHF and colocation.
- [vLLM Structured Outputs](vllm-structured-outputs.md) — Constrained generation via choice, regex, JSON schema, grammar, and structural tags for online and offline inference.
- [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — Single-replica tensor/pipeline strategy selection, multi-node Ray and multiprocessing runtimes, and InfiniBand/GPUDirect networking for vLLM scaling.
- [vLLM Text Watermarking](vllm-watermarking.md) — Statistical generation-time watermarking with Gumbel-max and dual-key variants, Philox PRF, context deduplication, speculative-decoding rules, and separate token-ID detection.
- [vLLM Tool Calling](vllm-tool-calling.md) — Named, auto, required, and none tool-choice modes with model-specific parsers and schema-constrained decoding for vLLM.
- [vLLM torch.compile for Multimodal Encoders](vllm-torch-compile-multimodal.md) — Compiling multimodal encoders with support_torch_compile gating, encoder compile ranges, and vision troubleshooting.
- [vLLM torch.compile Fusion Passes](vllm-fusion-passes.md) — Custom Inductor fusion passes controlled by PassConfig that fuse collectives, norms, attention, RoPE, and quantization by token regime and platform.
- [vLLM torch.compile Integration](vllm-torch-compile.md) — Default V1 torch.compile pipeline covering cache, dynamic shapes, Dynamo capture, Inductor compilation, and piecewise CUDA graphs.
- [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — API server, engine core, GPU worker, and DP coordinator processes and counts.
