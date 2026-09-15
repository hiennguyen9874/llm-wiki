---
type: Concept
title: vLLM Context Parallel Deployment
description: Prefill and decode context-parallel strategies for long-context serving, including DCP KV-cache sharding and sizing guidance.
tags: [vllm, context-parallel, long-context, kv-cache, tensor-parallel]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: cp-deploy
    resource: ../raw/vllm/serving/context_parallel_deployment.md
    title: Context Parallel Deployment
---

vLLM implements context parallelism separately for prefill and decode because long-context prefill is bound by time-to-first-token while long-context decode is bound by KV-cache capacity and batch size[^cp-deploy].

## Prefill context parallel

For a long prefill with `T` new tokens on `N` GPUs, the request is split into `N` chunks and each GPU computes one chunk of query/key/value tensors[^cp-deploy].

Two strategies are described, both under active development[^cp-deploy]:

1. Partial query, full key/value: for moderately long requests where full key/value tensors fit in memory. Key/value tensors are gathered from all GPUs and each GPU computes attention output for its query chunk, amortizing prefill compute across query tokens to control TTFT.
2. Partial query, partial key/value: for very long requests where full key/value tensors do not fit. Each GPU holds only one query/key/value chunk and exchanges key/value chunks with techniques such as ring-attention.

## Decode context parallel

Each decode step computes a small number of query tokens against a large paged KV cache, so the core problem is how to shard the KV cache across GPUs[^cp-deploy].

For a model with `H` KV-heads and `T` context tokens, the cache holds `H * T` key/value tensors[^cp-deploy]:

1. If one GPU holds the cache with good enough performance, no parallelization is needed.
2. Otherwise shard along `H` with plain tensor parallelism via `-tp <num_gpus>`.
3. Because `H` is fixed by the model architecture, increasing `tp_size` beyond `H` duplicates the cache `tp_size / H` times. Add decode context parallel via `-dcp <size>` to further shard along `T` and reduce duplication.

DCP size does not change the number of GPUs launched; it only reduces KV-cache duplication[^cp-deploy]. It must lie in `[1, tp_size/H]`; larger values reduce duplication at the cost of more communication overhead[^cp-deploy].

Extending DCP beyond `tp_size / H` is theoretically possible but left unsupported for simplicity: decode has few query tokens, leaving no clear assignment for the remaining GPUs on non-attention layers. To further accelerate decode, increase `tp_size` first and then increase DCP size[^cp-deploy].

Because the KV cache grows during decoding, vLLM shards along `T` with an interleaving strategy so future tokens are naturally sharded. The source attributes this to Chao Hong from Moonshot and cites further detail in arXiv `2507.07120`[^cp-deploy].

## Sizing examples and guidance

| Model | KV-heads | Deployment | Duplication | DCP choice |
|---|---|---|---|---|
| DeepSeek-R1 with MLA | 1 | `-tp 8` single node | 8x | Add `-dcp 8` to reduce duplication[^cp-deploy] |
| Kimi-K2 | 1-class, larger than R1 | `-tp 16` | 16x | `-dcp 16` removes duplication with more communication, or `-dcp 8` leaves 2x duplication with smaller intra-node-only communication[^cp-deploy] |
| Qwen3-235B-A22B | 4 | `-tp 8` | 2x | Add `-dcp 2` to remove duplication[^cp-deploy] |

General rule: increase `-tp` until decode performance is satisfactory, then add `-dcp` to remove the resulting KV-cache duplication[^cp-deploy].

Decode context parallel is supported in vLLM for both MLA and GQA models, and some attention backends also combine it with MTP multi-token prediction for further decode acceleration[^cp-deploy].

## Discussion venue

Ongoing technical discussion happens in the `#sig-context-parallel` channel of vLLM Slack[^cp-deploy].

## Coverage limits

- Ring-attention (`2310.01889`), the Moonshot interleaved-sharding paper (`2507.07120`), and linked Slack/GitHub discussions were not inspected beyond the deployment note's summary[^cp-deploy].
- Prefill context-parallel strategies are marked as under active development in the source and should be re-verified before reuse as a stable procedure[^cp-deploy].

## Relationships

- Uses [vLLM Decode Context Parallelism](vllm-decode-context-parallelism.md) — sequence-dimension sharding mechanism, MLA/GQA sizing constraints, and Kimi K2.6 long-context throughput evidence extending this deployment guidance.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — decode context parallel shards the paged KV cache that paged attention consumes.
- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — both concern KV-cache organization and growth across prefill and decode.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — DCP and DCP+MTP support varies by attention backend and MLA/GQA implementation.

[^cp-deploy]: Context Parallel Deployment — `../raw/vllm/serving/context_parallel_deployment.md`.
