---
type: Concept
title: Ling-3.0-tiny Inference and Serving
description: SGLang, vLLM, and Ollama/MLX serving for Ling-3.0-tiny with NEXTN speculation, ling3 parsers, 256K YaRN context, and DGX Spark plus Apple Silicon edge deployment.
tags: [ling, sglang, vllm, ollama, inference, speculative-decoding, mtp, reasoning-parser, tool-calling, edge]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: ling-card
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny.md
    title: Ling-3.0-tiny model card
---

SGLang and vLLM serve Ling-3.0-tiny with NEXTN/MTP speculation, `ling3` reasoning and tool parsers, and 256K YaRN context, while an Ollama/MLX path plus FP8 edge figures target DGX Spark and Apple Silicon local deployment[^ling-card].

## SGLang serving

- Hardware/recipe matrix (BF16/FP8 × Low-Latency / High-Throughput / HiCache + Mooncake) with live command generator lives in the SGLang cookbook for `InclusionAI/Ling-3.0-tiny`[^ling-card].
- Prebuilt runtime image: `lmsysorg/sglang:dev-Ling-3.0-tiny`[^ling-card].
- Recommended low-latency recipe: built-in MTP/NEXTN with 256K YaRN context on 1× 141GB-class GPU (H20-3e) or a 1-GPU Blackwell node; launch uses `--model-path inclusionAI/Ling-3.0-tiny --tp 1 --context-length 262144 --speculative-algorithm NEXTN --mem-fraction-static 0.8` with `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` and `--json-model-override-args '{"rope_scaling":{"rope_type":"yarn","factor":2.0,"rope_theta":6000000,"partial_rotary_factor":0.5,"original_max_position_embeddings":131072}}'` on port 30000[^ling-card].
- Client defaults: thinking enabled by both chat template and `ling3` reasoning parser; disable per request with `"chat_template_kwargs": {"enable_thinking": false}`; recommended sampling `temperature=1.0, top_p=0.95, top_k=20`; `--reasoning-parser ling3` / `--tool-call-parser ling3`, HiCache + Mooncake L3 setup, and GSM8K / `bench_serving` reproduction live in the cookbook[^ling-card].
- Model identity and benchmark context are in [Ling-3.0-tiny Architecture and Evaluation](ling-3.0-tiny-architecture.md).

## vLLM serving

- Install path is a dedicated branch: create venv, clone `https://github.com/inclusionAI/vllm-ling-v3.git` at branch `ling_3_0`, then editable install with `VLLM_USE_PRECOMPILED=1`[^ling-card].
- Example single-GPU server uses `--trust-remote-code --served-model-name auto --tensor-parallel-size 1 --gpu-memory-utilization 0.85 --enable-prefix-caching --mamba-cache-mode align --enable-auto-tool-choice --tool-call-parser ling3 --reasoning-parser ling3`[^ling-card].
- Client recommendation: `enable_thinking=true` with `temperature=1.0, top_p=0.95, top_k=20` for better performance[^ling-card].

## Ollama and edge deployment

- Verified on an M4 Pro Mac with 48 GB unified memory; support comes from `ollama/ollama#17643` on branch `bailing-moe-v3` and is limited to running via MLX on Apple Silicon, not yet in the official Ollama release[^ling-card].
- Build from source with `cmake -B build .` plus `cmake --build build --parallel 8` after fetching the PR branch, then use the local `./ollama` executable[^ling-card].
- Import BF16 weights with `FROM /absolute/path/to/bf16_weights` in a Modelfile and `./ollama create ling-tiny-bf16 --experimental -f /tmp/Modelfile.ling`[^ling-card].
- Serve with default 8,192 context via `OLLAMA_CONTEXT_LENGTH=8192 ./ollama serve` on `http://127.0.0.1:11434`; call with `"raw": true, "think": true, "stream": false`, role-tagged prompt (`<role>SYSTEM</role>detailed thinking on`, `<role>HUMAN</role>`, `<role>ASSISTANT</role>` plus `<think>`), and options `temperature=1.0, top_p=0.95, top_k=20, num_predict=2048`[^ling-card].

## Local performance posture

- Validated on NVIDIA DGX Spark, Apple Silicon MacBook, and Mac mini for reasoning and agentic workloads without datacenter-class GPUs[^ling-card].
- FP8 figures: around 100–105 tokens/s on DGX Spark and 86–90 tokens/s on an M4 Pro MacBook, with approximately 8.34 GiB peak memory usage at 8K context length[^ling-card].
- Artificial Analysis testing reports over 160 tokens/s output with approximately 18 seconds end-to-end latency for a 500-token response including reasoning time[^ling-card].

## Relationships

- Related to [Ling-3.0-tiny Architecture and Evaluation](ling-3.0-tiny-architecture.md) — architecture, MoE, MTP training, and benchmark evidence for this same checkpoint.
- Related to [Ling-3.0-flash Inference and Serving](ling-3.0-flash-inference.md) — 4-GPU TP4/TP8 SGLang plus vLLM MTP-3 counterpart for the larger 124B/5.1B Ling-3.0-flash checkpoint.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — NEXTN/MTP speculation context for the SGLang low-latency recipe.
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native MTP method context for the vLLM branch install.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — `ling3` reasoning separation behind the thinking-enabled default and disable flag.
- Uses [SGLang Tool Parser](sglang-tool-parser.md) — `ling3` tool-call parsing behind the SGLang and vLLM tool-parser flags.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) — tuning context for the cookbook's HiCache + Mooncake recipe variant.
- Uses [SGLang HiCache System Design](sglang-hicache-design.md) — hierarchy context for the cookbook's HiCache + Mooncake L3 setup.

## Coverage limits

- Cookbook cells, GSM8K / `bench_serving` reproductions, and HiCache + Mooncake L3 setup details were not independently executed; commands are vendor-reported recipes[^ling-card].
- Throughput, latency, and memory figures are vendor-reported snapshots on stated hardware, not independently verified or universal defaults[^ling-card].
- No live credentials were ingested; the card's `<your-hf-token>` placeholder is recorded here only as a redacted reference.

[^ling-card]: Ling-3.0-tiny model card — `../raw/Ling-3.0-tiny/Ling-3.0-tiny.md`, SGLang cookbook plus `dev-Ling-3.0-tiny` image, TP1 256K YaRN NEXTN low-latency recipe with rope-scaling override, `ling3` reasoning/tool parsers with thinking toggle and `temperature=1.0, top_p=0.95, top_k=20` defaults, vLLM `ling_3_0` branch install with single-GPU prefix-caching server flags, Ollama PR-17643 MLX-only Apple Silicon build/import/serve/call flow with 8,192 context, and DGX Spark plus M4 Pro FP8 throughput with 8.34 GiB at 8K.
