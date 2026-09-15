---
type: Synthesis
title: vLLM vs SGLang 2026 Spheron Benchmark
description: Spheron H100/H200 comparison of vLLM and SGLang on Llama 3.3 70B and DeepSeek V4 Flash across unique versus prefix-heavy workloads with TTFT, structured-output, speculative-decoding, and cost evidence.
tags: [vllm, sglang, benchmark, h100, h200, radix-attention, paged-attention, ttft, cost]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: spheron-2026
    resource: ../raw/vllm-vs-sglang-2026/index.md
    title: "vLLM vs SGLang 2026: RadixAttention vs PagedAttention Benchmarks"
---

On the tested Spheron configurations, unique-prompt throughput is effectively tied within 5%, while prefix-heavy work with 80% shared 512-token context favors SGLang by roughly 37% lower TTFT p50 at 50 concurrent requests; the source reduces the choice to prefix-overlap ratio, Blackwell/speculative-decoding needs, and operational simplicity[^spheron-2026].

## Test scope

The following is source-attributed methodology, not an independent rerun[^spheron-2026]:

- Hardware: bare-metal H100 SXM5 80GB single-GPU for dense runs; 8x H100 SXM5 for DeepSeek V4 Flash MoE runs; H200 figures appear only in the cost section.
- Software: vLLM v0.18.0 without MRV2 model runner; SGLang v0.5.9 with RadixAttention on by default; CUDA 13.0 containers.
- Model: Llama 3.3 70B Instruct at FP8 for single-GPU runs; DeepSeek V4 Flash at FP8 on 8x H100 with TP8 plus expert parallelism for MoE runs.
- Client: async aiohttp, 200 prompts per run, 60-second warmup, 3-minute measurement window at concurrency 1, 10, 50, and 100.
- Workload split: unique-prompt runs use fully distinct prompts; prefix-heavy runs share a 512-token system prompt across 80% of requests.

## Unique-prompt throughput: tie

No shared prefix, so both engines test raw scheduling and memory management[^spheron-2026]:

| Concurrency | vLLM tok/s | SGLang tok/s | Delta |
| --- | --- | --- | --- |
| 1 | 312 | 318 | +2% SGLang |
| 10 | 890 | 902 | +1% SGLang |
| 50 | 1,850 | 1,920 | +4% SGLang |
| 100 | 2,010 | 2,050 | +2% SGLang |

The source treats the 2-4% SGLang edge as run-to-run variance with no meaningful advantage at zero overlap[^spheron-2026].

## Prefix-heavy TTFT: SGLang advantage

80% of requests share a 512-token system prompt[^spheron-2026]:

| Concurrency | vLLM TTFT p50 | SGLang TTFT p50 | vLLM TTFT p95 | SGLang TTFT p95 |
| --- | --- | --- | --- | --- |
| 1 | 118 ms | 89 ms | 145 ms | 108 ms |
| 10 | 142 ms | 98 ms | 220 ms | 135 ms |
| 50 | 310 ms | 195 ms | 580 ms | 340 ms |
| 100 | 620 ms | 370 ms | 1,240 ms | 680 ms |

At c=50 this is 37% lower p50 and 41% lower p95 for SGLang, attributed to computing the shared prefix once and skipping that prefill on hits[^spheron-2026]. With vLLM automatic prefix caching enabled at c=10 on the simple shared-system-prompt case, the source says the gap narrows to roughly 15-18%; radix-tree organization is still framed as more effective for variable-length prefixes and branching conversations[^spheron-2026].

Overlap scaling at c=50, measured against vLLM without APC[^spheron-2026]:

| Overlap ratio | SGLang hit rate | TTFT reduction vs vLLM no-APC |
| --- | --- | --- |
| 20% | ~28% | ~7% |
| 40% | ~54% | ~15% |
| 60% | ~71% | ~24% |
| 80% | ~84% | ~37% |
| 95% | ~93% | ~44% |

The source decision rule is to benchmark SGLang first above 60% overlap, where the gain is consistently meaningful, and to treat sub-40% overlap advantage as marginal[^spheron-2026]. Cache hit rate is observable at `/metrics` via `sglang_cache_hit_rate`[^spheron-2026].

Single-request prefix-length scaling at c=1, also source-attributed[^spheron-2026]:

| Prefix length | Hit rate | TTFT reduction |
| --- | --- | --- |
| 256 tokens | ~75% | ~18% |
| 512 tokens | ~82% | ~26% |
| 1,024 tokens | ~88% | ~35% |
| 2,048 tokens | ~92% | ~42% |

## MoE: DeepSeek V4 Flash within 7% on unique prompts

Test configuration is DeepSeek V4 Flash at FP8 on 8x H100 with TP8 plus expert parallelism; vLLM uses `--tensor-parallel-size 8 --enable-expert-parallel`, SGLang uses `--tp 8 --ep-size 8`[^spheron-2026]:

| Metric | vLLM | SGLang |
| --- | --- | --- |
| Throughput, 50 req unique prompt | 580 tok/s | 620 tok/s |
| TTFT p50, 10 req unique prompt | 890 ms | 855 ms |
| TTFT p50, 10 req 80% shared prefix | 730 ms | 520 ms |

The source takeaway is that unique-prompt MoE performance is within 7% while the shared-prefix SGLang advantage holds at a similar ratio as dense models, so workload shape matters more than dense versus MoE architecture[^spheron-2026].

## Structured output: warm-cache SGLang edge

Both engines default to xgrammar in the source's account; the SGLang edge comes from more aggressive compiled-grammar reuse on repeated schemas, monitored via `sglang_grammar_cache_hit_rate`[^spheron-2026]. Latency overhead at c=8 on Llama 3.1 8B H100[^spheron-2026]:

| Schema complexity | vLLM overhead | SGLang warm | SGLang cold |
| --- | --- | --- | --- |
| Flat JSON, 3 fields | +6% | +2% | +8% |
| Nested JSON, 2 levels | +18% | +4% | +15% |
| Deeply nested, 4 levels | +42% | +6% | +24% |
| Function calling | +22% | +5% | +18% |

After warmup, SGLang per-request overhead on repeated schemas drops close to zero in these snapshots; vLLM also benefits from grammar caching but less pronouncedly on repeated calls[^spheron-2026].

## Speculative decoding and MTP

vLLM Eagle3/EAGLE2 is framed as mature, with 30-45% decode speedup on Llama 3.3 70B at 1-4 concurrent requests and 15-20% at 10-20 requests when combined with MRV2 async scheduling; SGLang speculative decoding at v0.5.9 is framed as experimental, so the source recommends vLLM for latency-sensitive speculative-decoding workloads in mid-2026[^spheron-2026]. Both engines support MTP draft heads on models that ship them such as DeepSeek V4 and GLM-5.2, framed as 1.5-2x decode throughput by predicting multiple tokens per forward pass[^spheron-2026].

## Hardware readiness

Source-attributed snapshot, not a current compatibility matrix[^spheron-2026]:

| Feature | vLLM | SGLang |
| --- | --- | --- |
| B200/GB200 native SM100/SM103 | Yes, v0.17.0+ FlashAttention 4 | Partial, catching up |
| FP8 inference | Yes | Yes |
| NVFP4 | Yes, Blackwell only | In progress |
| Tensor parallelism | Yes | Yes |
| Expert parallelism | Yes | Yes |
| NVLink multi-GPU / multi-node | Yes | Yes |

The source recommendation is to run vLLM on Blackwell today because of the FA4 backend; H100/H200/A100 are framed as equal hardware footing[^spheron-2026].

## Cost per million tokens

Formula used throughout: `(hourly_rate / 3600) / (tokens_per_sec / 1_000_000)`[^spheron-2026]. Rates are Spheron on-demand/spot snapshots dated 24 Jun 2026 and fluctuate; check live pricing before reuse.

Unique-prompt at c=50[^spheron-2026]:

| GPU | Engine | Tok/s | $/hr | Cost per 1M |
| --- | --- | --- | --- | --- |
| H100 SXM5 | vLLM | 1,850 | $4.06 | $0.61 |
| H100 SXM5 | SGLang | 1,920 | $4.06 | $0.59 |
| H100 SXM5 spot | vLLM | 1,850 | $2.91 | $0.44 |
| H100 SXM5 spot | SGLang | 1,920 | $2.91 | $0.42 |
| H200 SXM5 | vLLM | 2,380 | $5.92 | $0.69 |
| H200 SXM5 | SGLang | 2,460 | $5.92 | $0.67 |

Prefix-heavy effective throughput at 80% shared prefix, c=50[^spheron-2026]:

| GPU | Engine | Effective tok/s | $/hr | Cost per 1M |
| --- | --- | --- | --- | --- |
| H100 SXM5 | vLLM APC off | 1,850 | $4.06 | $0.61 |
| H100 SXM5 | vLLM APC on | 2,100 | $4.06 | $0.54 |
| H100 SXM5 | SGLang | 2,550 | $4.06 | $0.44 |
| H200 SXM5 | SGLang | 3,200 | $5.92 | $0.51 |

H200 spot at $3.31/hr puts prefix-heavy SGLang near $0.29/1M in the source arithmetic[^spheron-2026].

## Routing and migration notes

The following is source-attributed operational guidance, not independently verified practice[^spheron-2026]:

- Mixed traffic: serve both engines behind LiteLLM or a header/tag gateway, routing `prefix-heavy` to SGLang and `unique-prompt` to vLLM; both expose OpenAI-compatible APIs so routing is a proxy change. Simpler split: SGLang for customer chat, vLLM for internal batch.
- Disaggregation above either engine: NVIDIA Dynamo splits prefill and decode onto separate pools when one node runs out of KV-cache VRAM.
- Flag mapping vLLM to SGLang: `--model` to `--model-path`; `--quantization fp8` unchanged; `--gpu-memory-utilization` to `--mem-fraction-static`; `--max-model-len` to `--context-length`; `--max-num-seqs` has no direct SGLang equivalent because scheduling is dynamic; `--tensor-parallel-size` to `--tp`; `--enable-prefix-caching` has no flag because RadixAttention is on by default. Both load Hugging Face format with no checkpoint conversion.
- Moving SGLang to vLLM on prefix-heavy work without APC is framed as 15-40% higher TTFT depending on prefix length and overlap.

## Relationships

- Compares with [SGLang and vLLM Comparison](sglang-vs-vllm.md) — workload-oriented engine comparison; this concept adds the Spheron Llama 3.3 70B and DeepSeek V4 Flash TTFT/throughput/cost evidence.
- Uses [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) and [vLLM Prefix Caching](vllm-prefix-caching.md) — cache designs behind the prefix-overlap TTFT gap and the APC-narrows-the-gap note.
- Uses [SGLang Structured Outputs](sglang-structured-outputs.md) and [vLLM Structured Outputs](vllm-structured-outputs.md) — backend context for the xgrammar warm versus cold overhead contrast.
- Uses [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) and [SGLang Speculative Decoding](sglang-speculative-decoding.md) — maturity context for the Eagle3 versus experimental-SGLang claim.
- Uses [vLLM vs SGLang vs TensorRT-LLM H100 Benchmark](vllm-sglang-trtllm-h100-benchmark.md) — independent Qwen/H100 sweep to read alongside these Llama/MoE snapshots.

## Coverage limits

- Single-vendor Spheron evidence on Llama 3.3 70B FP8 plus one DeepSeek V4 Flash MoE point; H200 throughput appears only via cost arithmetic, not full latency tables.
- vLLM v0.18.0 predates MRV2 general availability, so MRV2-enabled numbers are out of scope here.
- Pricing is a 24 Jun 2026 Spheron snapshot and fluctuates; B200 figures in the source are rental listings, not measured benchmark rows.
- Docker deploy commands and quick-start steps were excluded as version-sensitive operations; the token placeholder in the source is not a credential.
- Linked TensorRT-LLM, MRV2, Eagle3, MTP, TokenSpeed, Dynamo, and GPU-rental guides were not inspected beyond the claims cited above.

[^spheron-2026]: Mitrasish Mukherjee, vLLM vs SGLang 2026: RadixAttention vs PagedAttention Benchmarks — `../raw/vllm-vs-sglang-2026/index.md` (spheron.network, 2026-06-23), covering PagedAttention versus RadixAttention framing, H100 Llama 3.3 70B unique and 80%-prefix TTFT/throughput tables, overlap-to-hit-rate scaling, DeepSeek V4 Flash MoE point, xgrammar warm/cold overhead, Eagle3/MTP status, Blackwell readiness, H100/H200 cost arithmetic, router and flag-migration notes, and versioned deploy commands.
