---
title: "vLLM vs SGLang 2026: RadixAttention vs PagedAttention Benchmarks"
author: "Mitrasish Mukherjee"
site: "Spheron"
published: 2026-06-23T00:00:00.000Z
source: "https://www.spheron.network/blog/vllm-vs-sglang-2026/"
domain: "spheron.network"
language: "en"
description: "vLLM vs SGLang 2026: RadixAttention prefix reuse vs PagedAttention KV paging, H100/H200 throughput benchmarks, structured output, and cost per million tokens."
word_count: 3056
---

Whether vLLM or SGLang is the right inference engine for your workload comes down to one number: prefix overlap ratio. If more than 60% of your requests share a common prefix (a system prompt, a RAG document, a tool definition block), SGLang's RadixAttention delivers measurably lower latency. If your prompts are mostly unique, both engines land within 5% of each other on throughput and the decision comes down to model support breadth and operational simplicity. Run a SGLang vs vLLM benchmark on a prefix-heavy workload and that overlap number tells the whole story: at 80% shared prefix and 50 concurrent requests, TTFT p50 drops from 310 ms on vLLM to 195 ms on SGLang, a 37% reduction that holds across the concurrency levels tested below.

This post is a direct two-engine comparison. For the three-way benchmark that also includes TensorRT-LLM (compilation overhead, peak throughput, cold start times), see the [vLLM vs TensorRT-LLM vs SGLang benchmark guide](https://www.spheron.network/blog/vllm-vs-tensorrt-llm-vs-sglang-benchmarks/).

## TL;DR Decision Table

| Use Case | Winner | Reason |
| --- | --- | --- |
| Prefix-heavy RAG | SGLang | RadixAttention reuses document context KV cache; 20-40% lower TTFT |
| Multi-turn agent | SGLang | Conversation history prefix is cached and reused each turn |
| Structured JSON output | SGLang (slight) | Both default to xgrammar; SGLang's grammar-cache reuse drops per-request overhead closer to zero on repeated schemas |
| Unique-prompt throughput | Tie | Within 5% at all concurrency levels on H100 |
| Broadest model support | vLLM | Wider architecture coverage, faster community integration of new models |
| MoE / DeepSeek V4 | Tie | Both support expert parallelism; performance within 10% |
| Blackwell / B200 native | vLLM | FlashAttention 4 backend on SM100/SM103 in vLLM v0.17.0+; SGLang catching up |
| Speculative decoding | vLLM | Eagle3 and EAGLE2 well-integrated with MRV2; SGLang support is experimental |
| Simplest deployment | vLLM | Single pip install, no compile step, well-documented HF model loading |

Three decision rules:

- If prefix overlap is above 60%, benchmark SGLang first. RadixAttention is on by default and the cache hit rate is visible immediately at `/metrics`.
- If you're running Blackwell (B200, GB200) or need Eagle3 speculative decoding, start with vLLM.
- If you're unsure, deploy vLLM. It's the safe default with the most complete documentation and community.

## Architecture: What Actually Drives the Difference

### PagedAttention (vLLM)

PagedAttention treats the KV cache like OS virtual memory. Rather than pre-allocating a contiguous VRAM block sized to `max_model_len` per request (which wastes 60-80% of allocated memory on typical workloads), it divides the cache into fixed-size blocks (16 tokens by default) and allocates them on demand as tokens are generated. When a request finishes, its blocks are freed immediately and returned to the pool.

The practical benefit: more concurrent requests fit in the same VRAM. A 70B model at FP8 on H100 SXM5 80GB leaves roughly 8-10GB for KV cache after weights load. With static allocation, that headroom might handle 8-12 concurrent requests at 4K context. With PagedAttention, the same headroom handles 40-60 concurrent requests because blocks are shared across the pool and released as soon as requests complete.

vLLM also has Automatic Prefix Caching (APC), enabled via `--enable-prefix-caching`. APC caches the KV blocks for the system prompt prefix and reuses them across requests that share that exact prefix. It's effective for the simple case of a fixed system prompt but doesn't handle branching conversation histories or variable-length prefixes as efficiently as RadixAttention.

### RadixAttention (SGLang)

RadixAttention extends the block-based KV cache idea by organizing blocks in a radix tree indexed by token sequence. Each node in the tree represents a token prefix; child nodes extend the parent's sequence. When a new request arrives, SGLang walks the tree to find the longest matching cached prefix and begins computation at that branch point.

The result: workloads with prefix overlap avoid recomputing KV activations for the shared prefix entirely. A 512-token system prompt shared across 1,000 concurrent requests gets computed once. A 10-turn conversation reuses the KV state from turns 1-9 when computing turn 10.

Cache hit rate under RadixAttention scales with overlap ratio. At 80% prefix overlap across requests (c=1 single-request baseline; see the benchmark section for c=50 numbers):

| Prefix length | Cache hit rate | TTFT reduction (c=1) |
| --- | --- | --- |
| 256 tokens | ~75% | ~18% |
| 512 tokens | ~82% | ~26% |
| 1,024 tokens | ~88% | ~35% |
| 2,048 tokens | ~92% | ~42% |

For unique prompts with no overlap, RadixAttention adds no overhead and performance matches vLLM's PagedAttention within noise.

### Architecture Comparison Table

| Feature | vLLM (PagedAttention) | SGLang (RadixAttention) |
| --- | --- | --- |
| KV cache allocation | Fixed-size blocks, on-demand | Radix tree, shared across requests |
| Prefix reuse | APC (opt-in, flat prefix only) | RadixAttention (on by default, arbitrary prefix boundaries) |
| Memory fragmentation | Minimal (block-level) | Minimal (block-level) |
| Multi-turn efficiency | Recomputes history on each turn without APC | Accumulates cached KV across turns |
| Default activation | PagedAttention always on | RadixAttention always on |
| Monitoring | `/metrics` Prometheus endpoint | `/metrics` with `sglang_cache_hit_rate` |

## Benchmark Setup

### Hardware

All benchmarks below ran on a [Spheron H100 SXM5 80GB instance](https://www.spheron.network/gpu-rental/h100/) at on-demand rates. Bare metal, no hypervisor. Host driver 590.48.01, CUDA 13.0 containers for both engines. NVLink present but not used (single-GPU runs). For other GPU options see the full [GPU rental catalog](https://www.spheron.network/gpu-rental/).

### Software

- **vLLM**: v0.18.0 (`vllm/vllm-openai:v0.18.0`). Benchmarks ran without VLLM\_USE\_V2\_MODEL\_RUNNER since v0.18.0 predates MRV2 general availability. For MRV2-enabled numbers, see the [vLLM Model Runner V2 deployment guide](https://www.spheron.network/blog/vllm-model-runner-v2-mrv2-deployment-guide/).
- **SGLang**: v0.5.9 (`lmsysorg/sglang:v0.5.9-cu130-runtime`). RadixAttention on by default.
- **Model**: Llama 3.3 70B Instruct at FP8 precision. Weights: ~70GB, leaving ~8GB for KV cache on a single H100 80GB.
- **Benchmark client**: async aiohttp, 200 prompts per run, 60-second warmup before each measurement window, 3-minute measurement window per concurrency level.
- **Concurrency levels**: 1, 10, 50, 100 concurrent requests.

Two separate benchmark sets:

1. **Unique-prompt workloads**: each request uses a completely distinct prompt (no shared prefix). Tests raw scheduling and memory management efficiency.
2. **Prefix-heavy workloads**: 80% of requests share a 512-token system prompt prefix. Tests RadixAttention effectiveness.

## Throughput Benchmarks: Unique-Prompt Workloads

No prefix overlap. Both engines are on equal footing here.

| Concurrency | vLLM tok/s | SGLang tok/s | Delta |
| --- | --- | --- | --- |
| 1 | 312 | 318 | +2% SGLang |
| 10 | 890 | 902 | +1% SGLang |
| 50 | 1,850 | 1,920 | +4% SGLang |
| 100 | 2,010 | 2,050 | +2% SGLang |

At unique-prompt workloads, the engines are effectively identical. The ~2-4% SGLang edge falls within run-to-run variance. Neither engine has a meaningful throughput advantage when prefix overlap is zero.

These numbers align with the three-way comparison post: vLLM at 1,850 tok/s and SGLang at 1,920 tok/s at 50 concurrent requests, same test setup.

## Throughput Benchmarks: Prefix-Heavy Workloads (80% Shared Prefix)

80% of requests share a 512-token system prompt. This is where the engines diverge.

### TTFT Comparison (p50 and p95)

| Concurrency | vLLM TTFT p50 | SGLang TTFT p50 | vLLM TTFT p95 | SGLang TTFT p95 |
| --- | --- | --- | --- | --- |
| 1 | 118 ms | 89 ms | 145 ms | 108 ms |
| 10 | 142 ms | 98 ms | 220 ms | 135 ms |
| 50 | 310 ms | 195 ms | 580 ms | 340 ms |
| 100 | 620 ms | 370 ms | 1,240 ms | 680 ms |

At c=50, SGLang delivers a 37% lower TTFT p50 and 41% lower p95. This is RadixAttention in action: the 512-token shared prefix is computed once and cached; subsequent requests skip that prefill work entirely.

At c=10 with vLLM's APC (`--enable-prefix-caching`) enabled, the gap narrows to roughly 15-18%. For the simple shared-system-prompt case, APC closes most of the gap. For variable-length prefixes and branching conversations, the radix-tree organization remains more effective.

### Cache Hit Rate vs TTFT Reduction (at c=50)

| Prefix overlap ratio | SGLang cache hit rate | TTFT reduction vs vLLM no-APC |
| --- | --- | --- |
| 20% | ~28% | ~7% |
| 40% | ~54% | ~15% |
| 60% | ~71% | ~24% |
| 80% | ~84% | ~37% |
| 95% | ~93% | ~44% |

The TTFT reduction grows nonlinearly with overlap ratio because higher overlap means more requests land fully in cache. Below 40% overlap the advantage is marginal. Above 60%, it's consistently meaningful.

## DeepSeek V4 and MoE Model Benchmarks

For MoE models, the relevant variable is expert parallelism alongside tensor parallelism. Both engines support this but with different flag sets.

**Test configuration**: DeepSeek V4 Flash (~284B total, ~13B active) at FP8 on 8x H100 SXM5 (from a multi-GPU Spheron instance). Tensor parallelism TP=8 with expert parallelism enabled: `--tensor-parallel-size 8` shards attention and MLP layers across GPUs while `--enable-expert-parallel` routes MoE expert layers separately.

**vLLM flags**:

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --quantization fp8 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.90
```

**SGLang flags**:

```
python -m sglang.launch_server \
  --model-path deepseek-ai/DeepSeek-V4-Flash \
  --quantization fp8 \
  --tp 8 \
  --ep-size 8 \
  --mem-fraction-static 0.90
```

| Metric | vLLM | SGLang |
| --- | --- | --- |
| Throughput (50 req, unique prompt) | 580 tok/s | 620 tok/s |
| TTFT p50 (10 req, unique prompt) | 890 ms | 855 ms |
| TTFT p50 (10 req, 80% shared prefix) | 730 ms | 520 ms |

MoE performance on unique prompts is within 7% of each other. The shared-prefix advantage for SGLang holds at the same ratio as on dense models, meaning workload characteristics matter more than the model architecture when choosing between the two engines.

For teams running large MoE models, the [MoE inference optimization guide](https://www.spheron.network/blog/moe-inference-optimization-gpu-cloud/) covers expert parallelism tuning in more depth.

## Structured Output: xgrammar vs Guided Decoding

Constrained decoding overhead is a second axis where the engines differ, particularly for agent workloads.

### SGLang xgrammar

SGLang uses xgrammar as its default constrained decoding backend. xgrammar compiles the JSON schema to a grammar automaton once (20-50ms compilation time), caches the compiled grammar, and reduces per-token overhead to near-zero on subsequent requests with the same schema. For agent APIs where the same tool schema is called thousands of times per hour, grammar caching eliminates most of the overhead.

Enable with:

```
python -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --enable-cache-report
# xgrammar is the default backend; no extra flag needed
```

Monitor cache hit rate with the `sglang_grammar_cache_hit_rate` Prometheus metric.

### vLLM Guided Decoding

vLLM also defaults to xgrammar for guided decoding as of 2026. Outlines and lm-format-enforcer remain selectable backends, but xgrammar is the default. The slight SGLang advantage comes from grammar-cache behavior: SGLang reuses compiled grammar automata more aggressively, so per-request overhead on repeated schemas drops faster after warmup. For structured output workloads, see the [structured output and function calling guide](https://www.spheron.network/blog/structured-output-function-calling-inference-guide/) for detailed benchmarks across schema types.

### Latency Overhead by Schema Complexity (c=8, Llama 3.1 8B, H100 SXM5)

| Schema complexity | vLLM overhead | SGLang overhead (warm) | SGLang overhead (cold) |
| --- | --- | --- | --- |
| Flat JSON (3 fields) | +6% | +2% | +8% |
| Nested JSON (2 levels) | +18% | +4% | +15% |
| Deeply nested (4 levels) | +42% | +6% | +24% |
| Function calling | +22% | +5% | +18% |

After grammar cache warmup, SGLang's per-request overhead on repeated schemas drops close to zero. vLLM's xgrammar implementation also benefits from the grammar cache, but the overhead reduction is less pronounced on repeated schema calls.

## Speculative Decoding and MTP Support

### vLLM Eagle3 and EAGLE2

vLLM has mature support for speculative decoding via Eagle3 and EAGLE2. With MRV2 async scheduling (`VLLM_USE_V2_MODEL_RUNNER=1`), Eagle3 delivers 30-45% decode speedup on Llama 3.3 70B at low batch sizes (1-4 concurrent requests) and 15-20% at moderate concurrency (10-20 requests). Flags:

```
vllm serve meta-llama/Llama-3.3-70B-Instruct \
  --speculative-model meta-llama/Llama-3.3-70B-Instruct-Eagle3 \
  --num-speculative-tokens 5 \
  --speculative-draft-tensor-parallel-size 1
```

For the full Eagle3 setup guide, see [Eagle3 speculative decoding on GPU cloud](https://www.spheron.network/blog/eagle-3-speculative-decoding-gpu-cloud/).

### SGLang Speculative Decoding

SGLang has speculative decoding support but integration is less mature than vLLM's at v0.5.9. For latency-sensitive workloads that rely heavily on speculative decoding, vLLM is the safer choice in mid-2026.

### Multi-Token Prediction (MTP)

Both engines support MTP draft heads for models that ship them (DeepSeek V4, GLM-5.2). MTP provides 1.5-2x decode throughput on supported models by predicting multiple tokens per forward pass using the model's own lightweight draft heads rather than a separate draft model. DeepSeek V4 ships with MTP heads; check the model's documentation for the verified number of draft heads available in each variant before assuming a specific prediction depth per step. For setup details, see the [multi-token prediction deployment guide](https://www.spheron.network/blog/multi-token-prediction-mtp-gpu-cloud-deployment-guide/).

For coding-agent workloads that need to push latency further than Eagle3 or MTP alone, [TokenSpeed](https://www.spheron.network/blog/deploy-tokenspeed-gpu-cloud/) plugs into vLLM as a drop-in backend with a custom MLA kernel built specifically for agentic traces, and it is worth a look before you settle on a speculative decoding config.

## Hardware Readiness: Blackwell, FP8, NVFP4, Multi-GPU

| Feature | vLLM | SGLang |
| --- | --- | --- |
| B200 / GB200 native (SM100/SM103) | Yes (v0.17.0+, FlashAttention 4) | Partial (catching up) |
| FP8 inference | Yes (`--quantization fp8`) | Yes (`--quantization fp8`) |
| NVFP4 quantization | Yes (Blackwell only) | In progress |
| Tensor parallelism (TP) | Yes (`--tensor-parallel-size N`) | Yes (`--tp N`) |
| Expert parallelism (EP) | Yes (`--enable-expert-parallel`) | Yes (`--ep-size N`) |
| NVLink multi-GPU | Yes | Yes |
| Multi-node TP | Yes (Ray or vLLM distributed) | Yes (NCCL) |

Blackwell users should run vLLM today. The FlashAttention 4 backend landed in v0.17.0 and auto-enables on SM100/SM103 hardware, delivering a meaningful throughput gain over FA3 on B200 and B300 GPUs. The benchmark here ran v0.18.0, which already includes FA4. B200 SXM6 is currently available on Spheron starting from $7.37/hr on-demand and $5.34/hr spot. Spot instances can be reclaimed without notice, so plan for checkpointing and automatic restart logic in production workloads if running spot. For Blackwell deployments, [B200 GPU rental on Spheron](https://www.spheron.network/gpu-rental/b200/) lists current availability.

> Pricing fluctuates based on GPU availability. The prices above are based on **24 Jun 2026** and may have changed. Check [current GPU pricing](https://www.spheron.network/pricing/) for live rates.

For non-Blackwell hardware (H100, H200, A100), both engines are on equal hardware footing.

## Cost Per Million Tokens on Spheron

Formula: `(hourly_rate / 3600) / (tokens_per_sec / 1_000_000) = cost_per_million_tokens`

### Unique-Prompt Workloads (c=50)

| GPU | Engine | Tok/s | $/hr | Cost per 1M tokens |
| --- | --- | --- | --- | --- |
| H100 SXM5 | vLLM | 1,850 | $4.06 | $0.61 |
| H100 SXM5 | SGLang | 1,920 | $4.06 | $0.59 |
| H100 SXM5 | vLLM | 1,850 | $2.91 (spot) | $0.44 |
| H100 SXM5 | SGLang | 1,920 | $2.91 (spot) | $0.42 |
| H200 SXM5 | vLLM | 2,380 | $5.92 | $0.69 |
| H200 SXM5 | SGLang | 2,460 | $5.92 | $0.67 |

### Prefix-Heavy Workloads (80% shared prefix, c=50, effective throughput including cache savings)

| GPU | Engine | Effective tok/s | On-demand $/hr | Cost per 1M tokens |
| --- | --- | --- | --- | --- |
| H100 SXM5 | vLLM (APC off) | 1,850 | $4.06 | $0.61 |
| H100 SXM5 | vLLM (APC on) | 2,100 | $4.06 | $0.54 |
| H100 SXM5 | SGLang | 2,550 | $4.06 | $0.44 |
| H200 SXM5 | SGLang | 3,200 | $5.92 | $0.51 |

H200 SXM5 spot pricing ($3.31/hr) puts SGLang's cost for prefix-heavy workloads at around $0.29/1M tokens, well below managed inference API pricing for open-source models. For a full cross-GPU cost-per-token analysis, see the [GPU cost per token benchmark](https://www.spheron.network/blog/gpu-cost-per-token-benchmark-llm-inference-2026/).

> Pricing fluctuates based on GPU availability. The prices above are based on **24 Jun 2026** and may have changed. Check [current GPU pricing](https://www.spheron.network/pricing/) for live rates.

## When to Run Both Behind an Inference Router

High-traffic APIs often serve mixed workloads: some users run chatbots with shared system prompts (ideal for SGLang), others run batch classification jobs with unique prompts (roughly equivalent on both). Running a single engine optimizes for one use case at the expense of the other.

One approach: deploy both engines and route at the request level using LiteLLM or a custom gateway that reads a header or workload tag. Requests flagged as `prefix-heavy` go to the SGLang fleet; `unique-prompt` requests go to vLLM. Both expose the same OpenAI-compatible API, so the routing layer is a simple proxy change.

A simpler version: run SGLang for your customer-facing chat API and vLLM for your internal batch inference pipeline. Both pull from the same model weights on shared NFS or S3.

Neither approach helps once a single node runs out of VRAM for the KV cache under load. For deployments that need to scale prefill and decode independently across multiple nodes, [NVIDIA Dynamo's disaggregated inference architecture](https://www.spheron.network/blog/nvidia-dynamo-disaggregated-inference-guide/) sits above either engine and splits those two phases onto separate worker pools entirely.

## Migration Notes

### vLLM to SGLang

Both engines expose an OpenAI-compatible API at `/v1/chat/completions` and `/v1/completions`. Your client code does not change. The only changes are at the container level:

| vLLM flag | SGLang equivalent |
| --- | --- |
| `--model` | `--model-path` |
| `--quantization fp8` | `--quantization fp8` |
| `--gpu-memory-utilization 0.92` | `--mem-fraction-static 0.92` |
| `--max-model-len 8192` | `--context-length 8192` |
| `--max-num-seqs 256` | (no direct equivalent; SGLang uses dynamic scheduling) |
| `--tensor-parallel-size N` | `--tp N` |
| `--enable-prefix-caching` | (RadixAttention is on by default) |

Both load HuggingFace model format from Hub or local directory. No checkpoint conversion required.

### SGLang to vLLM

Reverse the flag mapping above. If you were relying on RadixAttention's high cache hit rates for prefix-heavy workloads, add `--enable-prefix-caching` to the vLLM command. Expect TTFT to increase 15-40% on prefix-heavy workloads depending on prefix length and overlap ratio.

## Summary

vLLM and SGLang are close enough in raw throughput that the decision rarely comes down to peak tokens per second on unique prompts. It comes down to workload characteristics and what you need to optimize.

SGLang wins when prefix overlap is above 60%, when you're running multi-turn agents or RAG pipelines, and when structured output schemas are repeated at high volume. vLLM wins when you need the broadest model support, Blackwell-native performance, or mature Eagle3 speculative decoding. For everything else, either engine gets you to production.

For deployment guides, see the [SGLang production deployment guide](https://www.spheron.network/blog/sglang-production-deployment-guide/) and the [vLLM production deployment guide](https://www.spheron.network/blog/vllm-production-deployment-2026/).

---

> Both vLLM and SGLang run side by side on Spheron GPU cloud at the same on-demand price. Spin up either engine in under 2 minutes on bare-metal H100 or H200 without hypervisor overhead. See the quick-guides at [docs.spheron.ai](https://docs.spheron.ai/quick-guides/llms/) to get started.
> 
> [H200 on Spheron](https://www.spheron.network/gpu-rental/h200/) | **[Get started →](https://app.spheron.ai/)**

## Quick Setup Guide

1. ### Choose your engine based on workload prefix overlap
	Measure prefix overlap in your workload before choosing an engine. If your system prompt or document context is identical across 60%+ of requests, use SGLang - RadixAttention will deliver a meaningful TTFT reduction. If prompts are unique (creative generation, search queries, one-shot summarization), vLLM's PagedAttention works equally well and offers broader model support.
2. ### Provision a Spheron GPU instance
	Log in to app.spheron.ai, select your GPU tier (H100 SXM5 for 70B at FP8, H200 for 70B FP16 or 405B at FP8, B200 for largest MoE models), choose a region, and SSH into the instance. Run nvidia-smi to confirm GPU count and VRAM. See the Spheron quick-guide catalog at https://docs.spheron.ai/quick-guides/llms/ for per-model Docker commands.
3. ### Deploy vLLM on H100 at FP8
	docker run --gpus all --ipc=host -p 8000:8000 -e HUGGING\_FACE\_HUB\_TOKEN=your\_token vllm/vllm-openai:v0.18.0 --model meta-llama/Llama-3.3-70B-Instruct --quantization fp8 --gpu-memory-utilization 0.92 --max-model-len 8192 --max-num-seqs 256 --host 0.0.0.0 --port 8000. For prefix-heavy workloads add --enable-prefix-caching.
4. ### Deploy SGLang on H100 at FP8
	docker run --gpus all --ipc=host -p 8000:8000 -e HUGGING\_FACE\_HUB\_TOKEN=your\_token lmsysorg/sglang:v0.5.9-cu130-runtime python -m sglang.launch\_server --model-path meta-llama/Llama-3.3-70B-Instruct --quantization fp8 --context-length 8192 --mem-fraction-static 0.92 --host 0.0.0.0 --port 8000. RadixAttention is on by default. Monitor cache hit rate via /metrics endpoint.
5. ### Benchmark throughput to confirm engine choice for your workload
	Run vLLM's benchmark\_serving.py against both deployments at your target concurrency. Use prompts from your actual workload, not synthetic ones - the prefix overlap ratio in real prompts is what determines whether RadixAttention helps. Compare TTFT p50 and p95, output tokens/sec, and cost per million tokens using the formula: (hourly\_rate / 3600) / (tokens\_per\_sec / 1\_000\_000).
