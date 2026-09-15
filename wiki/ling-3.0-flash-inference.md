---
type: Concept
title: Ling-3.0-flash Inference and Serving
description: Production SGLang and vLLM serving for Ling-3.0-flash with NEXTN/MTP speculation, ling3 parsers, 256K context, and HiCache plus Mooncake caching.
tags: [ling, sglang, vllm, inference, speculative-decoding, mtp, hicache, mooncake, reasoning-parser, tool-calling]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: ling-card
    resource: ../raw/Ling-3.0-flash/Ling-3.0-flash.md
    title: Ling-3.0-flash model card
---

SGLang and vLLM serve Ling-3.0-flash with MTP/NEXTN speculation, `ling3` reasoning and tool parsers, 256K YaRN context, and HiCache plus Mooncake L3 reuse for long-horizon agent workloads[^ling-card].

## SGLang serving

- Hardware/recipe matrix (BF16/FP8 × Low-Latency / High-Throughput / HiCache + Mooncake) with live command generator lives in the SGLang cookbook for `InclusionAI/Ling-3.0-flash`[^ling-card].
- Prebuilt runtime image: `lmsysorg/sglang:dev-Ling-3.0-flash`[^ling-card].
- Recommended low-latency recipe: built-in MTP/NEXTN with 256K YaRN context on 4× 141GB-class GPUs (H20-3e) or 4-GPU Blackwell nodes; launch uses `--model-path inclusionAI/Ling-3.0-flash --tp 4 --context-length 262144 --speculative-algorithm NEXTN --mem-fraction-static 0.8` with `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1` on port 30000[^ling-card].
- On 80GB H100/H800 cards use `--tp 8` with the same flags; other hardware variants are in the cookbook cell[^ling-card].
- Client defaults: thinking enabled by both chat template and `ling3` reasoning parser; disable per request with `"chat_template_kwargs": {"enable_thinking": false}`; recommended sampling `temperature=0.6, top_p=0.95, top_k=20`; `--reasoning-parser ling3` / `--tool-call-parser ling3`, HiCache + Mooncake L3 setup, and GSM8K / `bench_serving` reproduction live in the cookbook[^ling-card].
- Model identity and benchmark context are in [Ling-3.0-flash Architecture and Evaluation](ling-3.0-flash-architecture.md).

## vLLM serving

- Install path is a dedicated branch: create venv, clone `https://github.com/inclusionAI/vllm-ling-v3.git` at branch `ling_3_0`, then editable install with `VLLM_USE_PRECOMPILED=1`[^ling-card].
- Example 4-GPU server enables native MTP for lower latency (`--speculative-config '{"method":"mtp","num_speculative_tokens":3}'`), plus `--trust-remote-code --tensor-parallel-size 4 --gpu-memory-utilization 0.85 --enable-prefix-caching --mamba-cache-mode align --enable-auto-tool-choice --tool-call-parser ling3 --reasoning-parser ling3`[^ling-card].
- Client recommendation: `temperature=0.6, top_p=0.95, top_k=20` with `enable_thinking` true for better performance[^ling-card].

## Caching and long-context posture

- HiCache + Mooncake hierarchical cache with physical dual-pools and cluster-shared L3 removes redundant recomputation in long-horizon interactions; vendor claim is 60% to over 80% TTFT reduction in long-input scenarios[^ling-card].
- Context posture: 8K → 32K → 256K training schedule, 256K serving context in both recipes, with 1M-token RoPE support noted in the architecture diagram[^ling-card].
- See [Ling-3.0-flash Architecture and Evaluation](ling-3.0-flash-architecture.md) for the training schedule and 1M-token diagram annotation.

## Relationships

- Uses [SGLang HiCache System Design](sglang-hicache-design.md) — three-tier cache hierarchy behind the HiCache plus Mooncake L3 setup.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) — memory-layout, prefetch, PD-disaggregation, and Mooncake deployment tuning for the long-input TTFT claim.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — NEXTN/MTP speculation context for the SGLang low-latency recipe.
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native MTP method context for the vLLM 3-token speculative config.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — `ling3` reasoning separation behind the thinking-enabled default and disable flag.
- Uses [SGLang Tool Parser](sglang-tool-parser.md) — `ling3` tool-call parsing behind the SGLang and vLLM tool-parser flags.
- Related to [Ling-3.0-flash Architecture and Evaluation](ling-3.0-flash-architecture.md) — architecture, MoE, MTP training, and benchmark evidence for this same checkpoint.

## Coverage limits

- Cookbook cells, GSM8K / `bench_serving` reproductions, HiCache + Mooncake L3 setup details, and image contents were not independently executed or inspected; commands are vendor-reported recipes[^ling-card].
- Throughput, latency, and TTFT-reduction figures are vendor-reported snapshots on stated hardware, not independently verified or universal defaults[^ling-card].
- No live credentials were ingested; the card's `<your-hf-token>` placeholder is recorded here only as a redacted reference.

[^ling-card]: Ling-3.0-flash model card — `../raw/Ling-3.0-flash/Ling-3.0-flash.md`, SGLang cookbook plus `dev-Ling-3.0-flash` image, TP4 256K NEXTN low-latency recipe with TP8 80GB variant, `ling3` reasoning/tool parsers with thinking toggle and sampling defaults, vLLM `ling_3_0` branch install with 4-GPU MTP-3 prefix-caching server flags, and HiCache+Mooncake TTFT plus 8K→32K→256K context posture.
