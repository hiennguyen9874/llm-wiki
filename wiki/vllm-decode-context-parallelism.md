---
type: Concept
title: vLLM Decode Context Parallelism
description: Sequence-sharded decode KV-cache parallelism with MLA/GQA sizing rules, communication pattern, and Kimi K2.6 long-context throughput evidence.
tags: [vllm, context-parallel, decode, kv-cache, long-context, mla, gqa]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: dcp-blog
    resource: ../raw/2026-08-07-decode-context-parallelism/index.md
    title: Efficient Decode Context Parallelism with vLLM for Long Context Workloads
---

vLLM Decode Context Parallelism (DCP) shards the decode KV cache along the sequence (token-position) dimension so each GPU stores and attends over only 1/N of every request's cache, freeing memory for larger batches on long-context agentic workloads[^dcp-blog].

## Why tensor parallelism alone duplicates KV cache

Under tensor parallelism the KV cache is partitioned by attention head, and one head is the smallest unit that can be handed to a GPU[^dcp-blog].

- Grouped-query attention (GQA) stores `num_key_value_heads` KV heads. TP splits cleanly only up to that count; once `tensor_parallel_size` exceeds it, ranks hold `tp // num_key_value_heads` identical copies[^dcp-blog].
- Multi-head latent attention (MLA) compresses keys/values into a single low-rank latent vector shared across all query heads — effectively one KV head — so under pure TP the full latent cache is replicated on every rank[^dcp-blog].

In both cases the duplicated cache leaves little room for additional requests, capping concurrency and driving down throughput on 64K–1M-token agent traces[^dcp-blog].

## What DCP does

DCP assigns each GPU a chunk of token positions from the same sequence (e.g. a 200K-token request split 0–50K / 50K–100K / 100K–150K / 150K–200K across four GPUs), so per-GPU KV footprint keeps shrinking as GPUs are added[^dcp-blog]. The freed memory admits more concurrent requests at larger batch sizes, which preserves interactive responsiveness on systems with high-bandwidth GPU-to-GPU interconnects[^dcp-blog].

## Decode communication pattern

Standard DCP follows AllGather Q, compute, then AllGather plus ReduceScatter[^dcp-blog]:

- **AllGather Q:** every GPU gathers the full decode query (a single token, so cheap) to score against any key. For MLA, `VLLM_DCP_Q_REPLICATE=1` (from vLLM PR `#45964`) can replicate the small query projection within each DCP group at load time to skip this all-gather[^dcp-blog].
- **Compute:** each GPU runs attention between the gathered query and its local KV slice — the `k_up` up-projection step for MLA, or tensor broadcast of shared KV heads across query heads for GQA[^dcp-blog].
- **AllGather + ReduceScatter (`cp_lse_ag_out_rs`):** partial outputs and log-sum-exp (LSE) values are shared, merged with the online-softmax reweighting trick, summed, and each GPU keeps only its own head-slice[^dcp-blog].

## Usage

DCP is enabled with `decode_context_parallel_size` alongside the tensor-parallel setting[^dcp-blog]:

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="deepseek-ai/DeepSeek-V2-Lite",
    tensor_parallel_size=2,
    decode_context_parallel_size=2,
)
outputs = llm.generate(["The future of AI is"], SamplingParams(temperature=0.8, top_p=0.95))
```

```bash
vllm serve deepseek-ai/DeepSeek-V2-Lite \
    --tensor-parallel-size 2 \
    --decode-context-parallel-size 2
```

### MLA backend

Applies to DeepSeek-V2/V3/R1 and Kimi K2.6 models using MLA[^dcp-blog]. Because the effective KV-head count is 1, the sequence can be split up to the full TP degree, subject to[^dcp-blog]:

- `tensor_parallel_size >= decode_context_parallel_size`
- `tensor_parallel_size % decode_context_parallel_size == 0`

```bash
vllm serve deepseek-ai/DeepSeek-R1 \
    --tensor-parallel-size 8 \
    --decode-context-parallel-size 8
```

### GQA backend

Applies to Qwen3-235B and other GQA models such as the Llama family[^dcp-blog]. DCP fills the would-be-duplicate TP copies with different sequence chunks, with the sequence-split degree capped by the duplication factor[^dcp-blog]:

- `(tensor_parallel_size // num_key_value_heads) >= decode_context_parallel_size`
- `(tensor_parallel_size // num_key_value_heads) % decode_context_parallel_size == 0`

For Qwen3-235B with `num_key_value_heads = 4` and `tp=8`, `8 // 4 = 2`, so DCP can be at most 2[^dcp-blog].

## Long-context throughput evidence

Setup: single 8×B200 node serving Kimi K2.6 in NVFP4 with vLLM, sweeping request concurrency 16–512; baseline TP8+EP8 (KV replicated) versus DCP TP8+EP8+DCP8 (KV sharded 8x), holding model, hardware, and workload fixed[^dcp-blog].

The workload is a public agentic multi-turn Mooncake trace (long inputs, short ~400-token outputs): median input ~67K tokens, bimodal with ~53% at 64K+ (tail to ~1M), ~47% under 64K, ~18% under 8K, ~8% over 128K, and ~3–4% over 256K[^dcp-blog].

| Concurrency | Baseline KV | DCP KV | Baseline tok/s/GPU | DCP tok/s/GPU |
|---|---|---|---|---|
| c16 | 53% | 7% | 1,720 | 2,230 |
| c32 | 86% | 12% | 1,780 | 2,880 |
| c64 | 100% (exhausted) | 19% | 1,863 | 3,750 |
| c128 | cannot admit | 34% | — | 4,650 |
| c256 | cannot admit | 54% | — | 5,480 |
| c512 | cannot admit | 82% | — | 6,091 |

The baseline hits 100% KV usage at c64 and plateaus near 1,863 tok/s/GPU, while DCP reaches 6,091 tok/s/GPU at c512 at 82% KV usage — roughly a 3.3x throughput-per-GPU gain at the top end of the sweep[^dcp-blog]. The stated core value is sustaining far higher concurrency on long-context runs where replicated-KV TP runs out of memory first[^dcp-blog].

Grouped by full (input+output) sequence length into five bands (<32K, 32–64K, 64–128K, 128–200K, 200K+), DCP holds a high, stable throughput–interactivity Pareto frontier with short- and long-bucket curves nearly overlapping, including the 200K+ range where the baseline cannot scale[^dcp-blog].

## Roadmap

Planned directions are finer-grained TP/DCP parallelism sizes, better single- and multi-node DCP all-to-all communication kernels with more compute overlap, MTP and speculative-decoding support, hardened prefill/decode disaggregation support, wider backend coverage, hybrid-model support, Dynamic Chunked Pipeline Parallelism integration, and a longer-term Prefill Context Parallelism (PCP) roadmap[^dcp-blog]. Community work extends DCP to GLM-5.2 and Kimi K3, with Kimi K3 DCP benchmarking still in progress at the time of writing[^dcp-blog].

Attribution notes: initial DCP work was upstreamed by Moonshot AI (vLLM PR `#23734`) with follow-up hardening by Lucas Wilkinson; the benchmarks were measured on NVIDIA B200 GPUs and are reproducible with vLLM releases supporting `--decode-context-parallel-size`[^dcp-blog]. The source also points to the [vLLM Decode Context Parallel docs](https://docs.vllm.ai/en/latest/serving/context_parallel_deployment/#decode-context-parallel) and NVIDIA's Helix Parallelism in TensorRT-LLM as the same industry direction[^dcp-blog].

## Coverage limits

- Attached figures (`figure-2.png`–`figure-5.png`, `kv-parallelism-overview.svg`) were inspected; per-point interactivity values behind the Pareto curves were not transcribed beyond the reported trend[^dcp-blog].
- Linked GitHub dataset/README, PRs `#23734`/`#45964`, deployment docs, and the Helix Parallelism blog were not inspected beyond this source's summary[^dcp-blog].
- Throughput numbers are single-setup evidence (8×B200, Kimi K2.6 NVFP4, this trace) and should not be reused as general speedup claims[^dcp-blog].
- Kimi K3 DCP benchmarks and PCP support were pending at publication time[^dcp-blog].

## Relationships

- Uses [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — general prefill/decode sharding and DCP sizing guidance that this mechanism, constraint, and benchmark evidence extends.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — DCP and DCP+MTP support varies by MLA/GQA backend implementation.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — DCP shards the paged KV cache consumed during decode attention.

[^dcp-blog]: Efficient Decode Context Parallelism with vLLM for Long Context Workloads — `../raw/2026-08-07-decode-context-parallelism/index.md`.
