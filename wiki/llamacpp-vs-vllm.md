---
type: Concept
title: llama.cpp vs vLLM Local Inference Choice
description: When to use llama.cpp for consumer CPU-first single-user inference versus vLLM for high-concurrency GPU serving, with GuideLLM benchmark context.
tags: [llamacpp, vllm, inference-serving, local-inference, comparison]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: llamacpp-vllm-guide
    resource: ../raw/llamacpp-vs-vllm-choosing-right-local-llm-inference-engine/index.md
    title: "llama.cpp vs. vLLM: Choosing the right local LLM inference engine"
---

llama.cpp is the CPU-first consumer-hardware path for single-user local inference via quantized GGUF models, while vLLM is the accelerator-backed serving path for multi-user throughput via continuous batching and PagedAttention; both expose an OpenAI-compatible API so switching is largely an endpoint change, and the choice turns on concurrency, hardware, latency SLAs, and offline versus serving needs[^llamacpp-vllm-guide].

## Why local inference

Local open-weight inference avoids recurring API bills and vendor rate limits and keeps data private by default, serving RAG pipelines, AI agents, and code assistants[^llamacpp-vllm-guide].

The source traces the gap to Llama 2 (2023) as one of the first commercially viable open-weight families in 7B, 13B, and 70B sizes: downloadable but hard to run because even the 7B model needed significant GPU memory in native precision[^llamacpp-vllm-guide].

## llama.cpp: consumer-hardware inference

llama.cpp began as a lightweight dependency-free C++ way to run Llama models and became a primary way to run LLMs on consumer hardware[^llamacpp-vllm-guide].

- **Quantization:** compresses 16- or 32-bit weights to 4-bit or 2-bit integers; the source's illustration is ~30 GB shrinking to ~4 GB to fit laptop RAM, with some quality loss but surprisingly good preserved performance for most uses[^llamacpp-vllm-guide].
- **GGUF packaging:** GPT-Generated Unified Format bundles weights plus tokenizer configuration, architecture details, and quantization parameters in one portable single file for fast loading and swapping; it is described as the de facto standard for local model distribution on Hugging Face[^llamacpp-vllm-guide].
- **CPU-first with optional GPU:** designed to run efficiently on CPUs, where most personal computers have no dedicated GPU, with GPU acceleration when available; this accessibility underlies tools such as Ollama and LM Studio[^llamacpp-vllm-guide].
- **Quantization note:** both engines benefit from quantization but apply it differently by backend, format, and target; the source says llama.cpp supports widely used quantized GGUF models plus activation quantization in some backends such as CUDA and Vulkan when paired with compatible int8-based weights[^llamacpp-vllm-guide].

## vLLM: high-throughput serving

vLLM targets production inference on accelerators including NVIDIA GPUs, Google TPUs, AMD GPUs, and Intel accelerators, centered on KV-cache management and GPU-utilization problems[^llamacpp-vllm-guide].

- **Continuous batching:** instead of processing each request alone or waiting on a fixed batch, vLLM interleaves token generation per token across the batch, so ~10 near-simultaneous arrivals interleave rather than making nine wait; the source contrasts this with BERT/YOLO-style fixed-input fixed-output batching and with static batching that leaves GPU slots idle[^llamacpp-vllm-guide].
- **PagedAttention:** the KV cache holds intermediate calculations reused for each subsequent token but grows quickly — a single long request can consume dozens of gigabytes — while accelerators commonly offer only 10, 40, or 80 GB VRAM for weights plus concurrent caches; PagedAttention manages KV memory like OS virtual memory with dynamic block allocate/free to raise GPU utilization[^llamacpp-vllm-guide].
- **Quantization coverage:** the source points to vLLM FP8, INT8, INT4, and other quantization workflows[^llamacpp-vllm-guide].

## Shared technique and scale-out limit

Both engines benefit from speculative decoding: a small fast draft model proposes candidate tokens and the large model verifies them in one parallel forward pass, yielding multiple tokens per verification step when the draft is correct, which is common for predictable tokens[^llamacpp-vllm-guide].

Single-node deployments eventually hit memory, throughput, and latency-under-load limits where adding another inference server is not enough; the source points to the llm-d project as the Kubernetes-scale answer that separates prefill (prompt processing) from decode (token generation) so each stage scales and optimizes independently[^llamacpp-vllm-guide].

## Benchmark context

Benchmarks used the GuideLLM open-source toolkit on Llama 3.1 8B at full 16-bit precision on a single NVIDIA H200 GPU across 1–64 concurrent users; full methodology is in the linked detailed comparison, which was not inspected[^llamacpp-vllm-guide].

Explicit scope warning from the source: this is a high-concurrency data-center-GPU serving scenario suited to vLLM's strengths, not a general ranking; llama.cpp is often used for local single-user CPU-first or consumer-hardware inference[^llamacpp-vllm-guide].

- **Throughput:** comparable single-request token rate, diverging with concurrency; at 64 simultaneous users vLLM generated roughly 44x more tokens per second than llama.cpp[^llamacpp-vllm-guide].
- **Time to first token (TTFT):** vLLM P99 TTFT stayed low and stable across concurrency levels while llama.cpp TTFT grew exponentially, exceeding three minutes at 64 concurrent users; the source attributes this to llama.cpp's sequential queuing model where later arrivals wait in line, while single-user response is immediate in both[^llamacpp-vllm-guide].

## Selection guidance

Both engines serve through an OpenAI-compatible API endpoint, so moving between llama.cpp, vLLM, or a hosted API is essentially a URL change with no code rewrite for RAG, agents, or other LLM clients[^llamacpp-vllm-guide].

Prefer llama.cpp (or Ollama / LM Studio) when prototyping on a laptop or workstation, running on consumer-grade or no GPU, swapping GGUF files to test models quickly, or needing offline inference such as factory floors and IoT[^llamacpp-vllm-guide].

Prefer vLLM when serving multiple concurrent users, running on data-center GPUs such as A100 or H100, meeting latency SLAs, or needing disaggregated serving with llm-d[^llamacpp-vllm-guide].

The typical journey described is: start on a paid API such as OpenAI or Anthropic for fast prototyping, move to llama.cpp locally as bills grow and for development, then switch to vLLM on GPU infrastructure for user-facing deployment[^llamacpp-vllm-guide].

Entry points named are `llama-cli` for experimentation and `llama-server` for serving on the llama.cpp side, vLLM Recipes for vLLM run guides, and the Red Hat AI optimized-model collection on Hugging Face for deployment-ready checkpoints[^llamacpp-vllm-guide].

## Relationships

- Compares with [SGLang and vLLM Comparison](sglang-vs-vllm.md) — server-GPU engine comparison counterpart; this concept adds the consumer-local versus serving split.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) and [vLLM Prefix Caching](vllm-prefix-caching.md) — implementation and cache-reuse context for the PagedAttention summary here.
- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — decode-prioritized batching context related to the continuous-batching summary here.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) and [Distributed Inference Deployment Blueprints](distributed-inference-blueprints.md) — prefill/decode separation and llm-d scale-out context.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) and [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — serving-side quantization and GGUF packaging context.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — when draft-model speculation pays off and how to tune it.

## Coverage limits

- Figure images under `assets/` (GGUF sizes, GGUF layout, batching grids, KV-cache growth, speculative-decoding workflow, throughput/TTFT charts, endpoint-switch snippet) were not visually inspected; quantitative claims above rest on prose and captions.
- The linked detailed benchmark methodology article, GuideLLM docs, FP8/INT8 DeepSeek accuracy article, quantization visual guide, PagedAttention paper, speculators article, llm-d site, Ollama/vLLM comparison, vLLM quantization docs, and vLLM Recipes / Red Hat AI model collection were not inspected beyond the source's description.
- Benchmark numbers are single-setup source-reported results (Llama 3.1 8B FP16, H200, concurrency 1–64); treat the 44x throughput and >3-minute TTFT gaps as production-serving snapshots under the source's stated scope warning, not universal engine rankings.

[^llamacpp-vllm-guide]: Cedric Clyburn, llama.cpp vs. vLLM: Choosing the right local LLM inference engine — `../raw/llamacpp-vs-vllm-choosing-right-local-llm-inference-engine/index.md` (Red Hat Developer, published 2026-06-15, updated 2026-07-13), covering local-inference motivation, Llama 2 origin, llama.cpp quantization/GGUF/CPU-first design, vLLM continuous batching/PagedAttention/speculative-decoding/llm-d scale-out, GuideLLM Llama 3.1 8B H200 concurrency 1–64 throughput and TTFT results with serving-scope caveat, OpenAI-compatible interchangeability, llama.cpp versus vLLM selection rules, API-to-local-to-serve journey, and llama-cli/llama-server plus vLLM Recipes entry points.
