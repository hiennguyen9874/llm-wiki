---
type: Synthesis
title: SGLang vs vLLM Self-Hosted Comparison (Mayhem 2026)
description: Self-hosted SGLang versus vLLM selection signals from a June 2026 X comparison with Q2 2026 benchmark snapshots, workstation GPU scaling, and deployment trade-offs.
tags: [sglang, vllm, comparison, self-hosted, radix-attention, paged-attention, benchmark]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: mayhem-selfhosted
    resource: ../raw/2069090022117019928/index.md
    title: "SGLang vs vLLM: A Technical Comparison for Self-Hosted Deployments"
---

For single-GPU and multi-GPU workstation or server self-hosting, the source reduces the SGLang versus vLLM choice to workload shape and hardware constraints rather than raw speed: SGLang is favored for shared-prefix chat, coding-assistant, and RAG traffic plus low-overhead structured output, while vLLM is favored for widest model, quantization, hardware, and Kubernetes-maturity coverage[^mayhem-selfhosted].

## Source scope

The following is source-attributed framing from a 2026-06-22 X thread by @Mayhem4Markets, not an independent rerun[^mayhem-selfhosted]:

- Scope: self-hosted single-GPU and multi-GPU workstation and server environments.
- Shared ground: both serve OpenAI-compatible APIs, support continuous batching, and run on multiple GPU types.
- Claimed differentiators: GPU-memory management, shared-context handling, and codebase structure.
- Benchmark numbers below are second-hand Q2 2026 snapshots cited without linked methodology or harness details; treat them as directional and configuration-specific.

## Cache architecture contrast

The source frames KV-cache management as the core architectural difference[^mayhem-selfhosted]:

- vLLM PagedAttention, attributed to a 2023 SOSP paper from UC Berkeley, divides KV cache into fixed-size pages allocated, freed, and remapped independently, avoiding contiguous reservation for worst-case length. The cited example is a 32-request batch where 30 finish in 10 tokens and 2 finish in 500 tokens no longer paying padded allocations, framed as near-zero waste versus naive static allocation.
- SGLang RadixAttention, attributed to a 2024 LMSYS paper, organizes KV cache as a radix tree. New requests reuse the longest matching prefix and compute only the diverging suffix; the cited example is three requests sharing "What is the capital of" but diverging to France, Germany, and weather, with the shared prefix stored once.
- The inspected PagedAttention-versus-RadixAttention diagram carries the same framing with no additional numbers beyond the prose: unique-prompt gap near zero, shared-prefix SGLang up to 6.4x and 30%+ on benchmarks, and vLLM APC as opt-in manual versus SGLang default automatic[^mayhem-selfhosted].
- vLLM Automatic Prefix Caching is described as opt-in via `--enable-prefix-caching`, using block-level hash matching that needs exact token-sequence matches and often manual tuning. RadixAttention is described as on by default with automatic partial-prefix detection.
- Workload rule stated: with unique prompts and no shared context the throughput gap narrows to near zero; with shared prefixes SGLang delivers about 30% higher throughput on standard benchmarks and up to 6.4x on prefix-heavy RAG and multi-turn runs, with migrated multi-turn chatbots routinely gaining 30% or more on identical hardware[^mayhem-selfhosted].
- Scale note: on a single GPU the GPU itself bottlenecks before scheduler or cache manager, compressing the difference. The gap matters most for multi-GPU setups, high concurrency, and over roughly 60% prefix overlap, where the source claims 3-5x effective prefill-latency improvement for SGLang[^mayhem-selfhosted].

## Q2 2026 benchmark snapshots

All rows are source-cited without reproducible harness detail[^mayhem-selfhosted]:

| Snapshot | Configuration | Reported result |
| --- | --- | --- |
| IoT Digital Twin Q2 | Llama-3.3-70B at 4-bit on 8x H200 SXM, 141GB HBM3e per GPU, high concurrency | vLLM about 5,300 tok/s, SGLang about 5,450 tok/s, trading narrow leads by concurrency and batch size |
| Turion Q2 2026 | H100 80GB, smaller models, 50 concurrent requests | SGLang leads on models up to 30B; on 70B+ the gap narrows to single-digit percent; at 100+ requests vLLM tail time-to-first-token lags while SGLang p95 stays tighter |
| SemiAnalysis InferenceXv2, early 2026 | SGLang on GB300 NVL72 with DeepSeek R1 | 25x gain versus H200 baseline, attributed to piecewise CUDA graphs default since v0.5.10 plus HiSparse sparse-attention integration for DeepSeek models |
| Workstation curve | Qwen3-Coder-30B AWQ at 8K context on vLLM | RTX 5090 about 4,570 tok/s; RTX PRO 6000 Blackwell about 8,425 tok/s; PRO 6000 fits 70B at FP8 on one card, RTX 5090 cannot |

The workstation chart image carries a longer GPU table than the prose excerpt and footers the data to CloudRift published benchmarks 2026, while the prose attributes the same numbers to VRLA Tech 2026; preserve both attributions and do not resolve the mismatch from this source alone[^mayhem-selfhosted]:

| GPU | VRAM | Bandwidth | Tok/s on 30B vLLM | Note in image |
| --- | --- | --- | --- | --- |
| RTX 4090 | 24GB GDDR6X | ~1.0 TB/s | ~2,259 | Baseline; cannot fit 70B |
| RTX 5090 | 32GB GDDR7 | 1.79 TB/s | ~4,570 | ~2x 4090; cannot fit 70B single card |
| RTX PRO 6000 Blackwell | 96GB ECC GDDR7 | 1.8 TB/s | ~8,425 | 1.8x 5090; fits 70B at FP8 single card |
| H100 PCIe | 80GB HBM3 | 2.0 TB/s | Comparable to RTX PRO 6000 | PRO 6000 wins on cost per token at single-GPU scale |
| H200 | 141GB HBM3e | 4.8 TB/s | Higher at large models | Fits 70B at FP16; required for 100B+ inference |
| B200 | 180GB HBM3e | ~8 TB/s | Up to 4.9x RTX PRO 6000 | Long-context efficiency leader; datacenter only |

The image caveat states figures are approximate and vary by model, quantization, batch size, and serving configuration, with B200 advantage growing with context length in the 8K+8K setup[^mayhem-selfhosted].

## Hardware and parallelism

Source-attributed portability snapshot, not a current compatibility matrix[^mayhem-selfhosted]:

- vLLM: NVIDIA, AMD, Intel Gaudi, AWS Trainium, Google TPUs, Apple Silicon, IBM Spyre, Huawei Ascend, and x86/ARM/PowerPC CPUs.
- SGLang: NVIDIA and AMD GPUs plus Intel Xeon CPUs, Google TPUs, and Ascend NPUs; no Apple Silicon or AWS Trainium in this account. For AMD-GPU or Mac users the source calls vLLM the safer choice.
- Both support tensor, pipeline, data, expert, and context parallelism. vLLM tensor parallelism is described as more battle-tested from longer production use across more hardware.

## Models, quantization, and structured output

- Model breadth: vLLM is credited with 200+ Hugging Face architectures spanning decoder-only LLMs such as Llama, Qwen, and Gemma, MoE models such as MiniMax, Mixtral, DeepSeek, and Qwen-MoE, hybrid attention and state-space models such as Mamba and Qwen3.5+, multimodal models such as LLaVA, Qwen-VL, and Pixtral, plus embedding models such as E5-Mistral, GTE, and ColBERT and reward models[^mayhem-selfhosted]. SGLang is framed as wide but narrower, compensating with day-0 support for major releases, notably DeepSeek-V4 on launch day in April 2026 with purpose-built kernels for hybrid sparse attention and FP4 expert weights.
- Quantization breadth is framed as largely overlapping by mid-2026 rather than decisive. vLLM lists FP8, MXFP8/MXFP4, NVFP4, INT8, INT4, GPTQ/AWQ, GGUF, compressed-tensors, ModelOpt, TorchAO, AutoAWQ, BitsAndBytes, GPTQModel, Intel Neural Compressor, LLM Compressor, and AMD Quark; SGLang lists fp8, mxfp4, blockwise_int8, w8a8_int8, w8a8_fp8, awq, gptq, compressed-tensors, gguf, modelopt_fp8, modelopt_fp4, torchao, bitsandbytes, awq_marlin, gptq_marlin, plus AMD paths including quark_int4fp8_moe, quark_mxfp4, and petit_nvfp4[^mayhem-selfhosted]. Both handle FP4, with SGLang NVFP4 via modelopt_fp4 on Blackwell plus nvfp4_online and AMD FP4 paths; for 7B-13B at 4-bit on 24-48GB GPUs the source treats AWQ or GPTQ on either engine as equivalent.
- The durable difference claimed is structured-output overhead: SGLang overlaps grammar-mask computation with GPU execution for near-zero JSON-mode or function-calling penalty even at high batch sizes, with compressed finite-state-machine plus overlapped mask generation in v0.4 framed as up to 10x faster JSON decoding; vLLM xgrammar and guidance integrations are described as CPU-side mask application with a noticeable bottleneck above about 8 concurrent requests[^mayhem-selfhosted].
- Memory framing: PagedAttention removes padded-sequence and early-finisher waste so more concurrent users fit; RadixAttention lowers effective per-request footprint when prompts share context such as system prompts and history in chatbot, RAG, and agentic traffic[^mayhem-selfhosted].

## Install, deploy, and API integration

Source-attributed operational notes, partly version-sensitive[^mayhem-selfhosted]:

- Install: both via pip with pre-built wheels, requiring CUDA and PyTorch plus first-use custom-kernel compilation. vLLM is given as `uv pip install vllm`, SGLang as `pip install sglang`; either is framed as 10-15 minutes for someone comfortable with Python virtual environments, with vLLM having fewer unsupported-GPU edge cases.
- Deploy: vLLM has more mature Docker images, Helm charts, Kubernetes docs, and production guides; SGLang supports Docker and Kubernetes with less comprehensive guides. Behind a reverse proxy on one machine with Docker Compose the source treats them as equal.
- API: both serve OpenAI-compatible chat and completions endpoints, so tools named as Factory Droid, OpenCode, Hermes Agent, LangChain, LlamaIndex, Open WebUI, and SillyTavern work without modification. vLLM additionally supports Anthropic Messages API and gRPC endpoints.
- SGLang DSL: a Python frontend language for structured-generation logic with chained calls, control flow, multimodal inputs, parallelism, and tool interaction; the source notes this is the namesake Structured Generation Language and has no vLLM equivalent, which it frames as a serving engine rather than a generation-programming framework[^mayhem-selfhosted].

## Speculative decoding, disaggregation, LoRA, and RL

- Speculative decoding: vLLM with n-gram, suffix, EAGLE, and DFlash; SGLang with DFlash and Spec V2 introduced June 2026 as the next generation[^mayhem-selfhosted].
- Both support disaggregated prefill and decode for separate prefill/decode GPU specialization at large scale; irrelevant on single-GPU where both phases share one device.
- Both support multi-LoRA batching for serving multiple adapters of one base model without full duplicate weights.
- SGLang-only role claimed: rollout backend for reinforcement-learning training in AReaL, Miles, verl, and Tunix, favored for fast rollouts and DeepSeek-specific optimizations including use for DeepSeek-V4 itself; optimizations are framed as flowing both ways between training and serving[^mayhem-selfhosted].

## Community and decision rule

- Community snapshot: vLLM over 17,000 stars and 2,000 contributors, originating at UC Berkeley Sky Computing Lab and used as default backend by AWS, Google Cloud, and Azure with an academic-plus-company maintainer board; SGLang over 15,000 stars under LMSYS with adoption listed as xAI Grok 3, AMD, NVIDIA, Intel, LinkedIn, Cursor, and Oracle Cloud plus over 400,000 GPUs in production, an a16z open-source grant in 2025, and PyTorch-ecosystem membership in March 2025[^mayhem-selfhosted]. For troubleshooting the source favors vLLM's larger base of answers and guides while calling SGLang's Slack and weekly meetings active.
- Choose SGLang for multi-turn, chatbot, coding-assistant, or RAG workloads with large shared prefixes, heavy JSON-mode or function-calling use, or close tracking of new DeepSeek releases[^mayhem-selfhosted].
- Choose vLLM for broadest model coverage including obscure architectures, widest hardware including AMD, Apple Silicon, and Trainium, most quantization options, largest troubleshooting base, or planned scale beyond one machine on Docker and Kubernetes[^mayhem-selfhosted].
- For mixed general-purpose or single-user traffic the source expects little noticeable performance difference and points the decision at hardware compatibility, model availability, and DSL versus ecosystem preference; both are free, open-source, and actively maintained[^mayhem-selfhosted].

## Relationships

- Compares with [SGLang and vLLM Comparison](sglang-vs-vllm.md) — workload-oriented engine comparison; this concept adds the Mayhem self-hosted benchmark snapshots and workstation selection rule.
- Uses [PagedAttention for LLM Serving](paged-attention.md) and [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — cache designs behind the paging-versus-tree contrast.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — opt-in APC context for the exact-match and tuning note.
- Uses [SGLang Structured Outputs](sglang-structured-outputs.md) and [vLLM Structured Outputs](vllm-structured-outputs.md) — backend context for the overlapped-mask versus CPU-side claim.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md), [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md), and [DFlash Block Diffusion Speculative Decoding](dflash-block-diffusion.md) — maturity context for the EAGLE/DFlash versus Spec V2 note.
- Uses [SGLang for RL Systems](sglang-for-rl.md) — RL rollout-backend context for the AReaL/Miles/verl/Tunix claim.
- Uses [vLLM vs SGLang 2026 Spheron Benchmark](vllm-vs-sglang-2026-spheron-benchmark.md) and [vLLM vs SGLang DeepInfra Decision Framework](vllm-vs-sglang-deepinfra-framework.md) — versioned TTFT/throughput evidence and validity rules to read alongside these second-hand Q2 snapshots.

## Coverage limits

- Single X-thread evidence citing IoT Digital Twin, Turion, SemiAnalysis, and VRLA Tech/CloudRift without linked methodology; versions are given only for SGLang piecewise graphs (default since v0.5.10), structured outputs (v0.4), and Spec V2 (June 2026).
- Workstation table prose attributes numbers to VRLA Tech while the chart footer says CloudRift published benchmarks 2026; both attributions are preserved unresolved.
- Hardware, model-count, quantization-format, install-command, tool-integration, and community-size claims are source-attributed snapshots, not current upstream verification.
- Cover image inspected as decorative title art with no extra numbers; the PagedAttention-versus-RadixAttention diagram and the workstation GPU table were inspected and carry only the numbers compiled above; the remaining seven section images were not inspected beyond placement because the prose carries the claims.

[^mayhem-selfhosted]: @Mayhem4Markets, SGLang vs vLLM: A Technical Comparison for Self-Hosted Deployments — `../raw/2069090022117019928/index.md` (x.com, 2026-06-22), covering PagedAttention versus RadixAttention behavior and APC configuration, IoT Digital Twin/Turion/SemiAnalysis/VRLA-Tech Q2 2026 snapshots, workstation GPU scaling table also footered to CloudRift, hardware/model/quantization/API/install/spec-decoding/RL/community comparison, and self-hosted decision rules; plus inspected `assets/HLbTCb1aAAAAzT9.jpg` diagram and `assets/HLbR18JXoAAaans.png` GPU table and decorative `assets/HLbiErwaUAAJiK7.jpg` cover.
