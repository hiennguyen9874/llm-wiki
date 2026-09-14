---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts
- [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — Isolating vLLM-compile failures with tlparse logs and per-subsystem disable flags for Dynamo, dynamic shapes, Inductor, cache, and CUDAGraphs.
- [vLLM Attention Backends](vllm-attention-backends.md) — Selection, configuration, composite routing, and MLA/sparse variants for vLLM attention backends.
- [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — Configurable CUDA Graphs modes, runtime dispatcher, nested wrappers, and attention-backend compatibility for vLLM v1.
- [vLLM CustomOp Dispatch and Registration](vllm-custom-op.md) — Platform-dispatched forward methods, compilation-config enablement, and in-tree versus out-of-tree registration for vLLM custom ops.
- [vLLM Dual Batch Overlap (DBO)](vllm-dbo-dual-batch-overlap.md) — Overlapping MoE sparse all-to-all with compute by splitting batches into paired microbatches on ping-ponging CPU threads.
- [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — Budget-based CUDA Graphs capture and replay for vision encoders, with greedy packing, dual-path graphs, video support, and model opt-in protocol.
- [vLLM Endpoint Plugins](vllm-endpoint-plugins.md) — Out-of-tree HTTP routes for the vLLM OpenAI-compatible server via two-phase EndpointPlugin loading and EngineClient access.
- [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — LLMEngine, workers, model runner, model objects, and VllmConfig design rationale.
- [vLLM Entrypoints](vllm-entrypoints.md) — Offline LLM class versus online vllm serve server for model inference.
- [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — Selecting vLLM modular MoE All2All backends and experts kernels by activation format, quantization, and compatibility families.
- [vLLM Fused MoE Modular Kernel](vllm-fused-moe-modular-kernel.md) — Architecture, components, initialization, and extension workflow for vLLM's modular fused MoE kernel.
- [vLLM HiSparse Local KV Offload](vllm-hisparse.md) — Local host-tier KV offload for sparse attention with coordinator-owned host blocks, spill-before-free residency, and fused GPU hot lookup.
- [vLLM Hugging Face Integration](vllm-huggingface-integration.md) — Resolving model IDs to config, tokenizer, and weights via Hugging Face Hub or local path, with config-class and architecture-registry mapping.
- [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — Unified page-size grouping, per-group allocation, and intersected prefix caching for hybrid-attention models.
- [vLLM IO Processor Plugins](vllm-io-processor-plugins.md) — Pre- and post-processing plugins for pooling models that map custom inputs to model prompts and model outputs to custom outputs.
- [vLLM IR Functional Intermediate Representation](vllm-ir.md) — Functional IR dialect separating op semantics from kernel implementations with late priority-based dispatch and compile lowering.
- [vLLM Logits Processors](vllm-logits-processors.md) — Stateful batch-granular logits transforms, BatchUpdate lifecycle, argmax-invariant sampling shortcut, and built-in versus custom extension model.
- [vLLM LoRA Resolver Plugins](vllm-lora-resolver-plugins.md) — On-demand LoRA adapter discovery and loading at request time via LoRAResolver plugins for filesystem, Hugging Face Hub, and custom backends.
- [vLLM Metrics and Observability](vllm-metrics.md) — V1 metrics collection, Prometheus and logging publishers, interval definitions, and deprecation and future-work policy for vLLM observability.
- [vLLM Model Runner V2](vllm-model-runner-v2.md) — Cleaner, async-first, GPU-native reimplementation of the vLLM model runner with decoupled persistent batches, staged writes, Triton sampling, and explicit CUDA-graph management.
- [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — Placeholder-to-input correspondence via HF-processor replay, dummy text, prompt updates, output caching, and GPU-fused normalization.
- [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) — Heartbeat-renewed short leases letting prefill reclaim KV blocks quickly on decode failure while keeping them alive under decode overload.
- [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — Push-based disaggregated prefill/decode where prefill WRITEs KV directly into decode's pre-allocated blocks via a dedicated writer thread and PUSH_REG registrations.
- [vLLM Optimization Levels](vllm-optimization-levels.md) — Preset -O0 through -O3 flags trading startup time for performance via compilation, CUDA-graph, fusion, and autotune defaults.
- [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — Historical vLLM multi-head query attention CUDA kernel over paged KV cache, covering query/key/value data paths, softmax reduction, and output writeback.
- [vLLM Plugin System](vllm-plugin-system.md) — Discovery, loading, and plugin groups for extending vLLM out-of-tree via Python entry points and VLLM_PLUGINS filtering.
- [vLLM Prefix Caching](vllm-prefix-caching.md) — Hash-based full-block prefix reuse in vLLM v1 with LRU eviction, touch-on-hit allocation, and cache-salt isolation.
- [vLLM Python Multiprocessing Method Selection](vllm-python-multiprocessing.md) — Best-effort fork/spawn selection, library-use constraints, and worker configuration for vLLM multiprocessing.
- [vLLM torch.compile for Multimodal Encoders](vllm-torch-compile-multimodal.md) — Compiling multimodal encoders with support_torch_compile gating, encoder compile ranges, and vision troubleshooting.
- [vLLM torch.compile Fusion Passes](vllm-fusion-passes.md) — Custom Inductor fusion passes controlled by PassConfig that fuse collectives, norms, attention, RoPE, and quantization by token regime and platform.
- [vLLM torch.compile Integration](vllm-torch-compile.md) — Default V1 torch.compile pipeline covering cache, dynamic shapes, Dynamo capture, Inductor compilation, and piecewise CUDA graphs.
- [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — API server, engine core, GPU worker, and DP coordinator processes and counts.
