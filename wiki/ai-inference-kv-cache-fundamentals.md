---
type: Concept
title: AI Inference, KV Cache, and Serving Optimizations
description: Autoregressive inference, KV-cache sizing, and runtime plus quantization optimizations that decide serving cost.
tags: [inference, kv-cache, quantization, vllm, serving]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T23:00:00Z }
sources:
  - id: clyburn-inference
    resource: ../raw/HowAIInferenceWorksClearlyExplained.md
    title: How AI Inference Works, Clearly Explained
  - id: kv-explainer
    resource: ../raw/KVCachinginLLMsClearlyExplained.md
    title: KV Caching in LLMs, Clearly Explained
---

Single explainer synthesis: training is one-time cost while inference recurs on every request, every output token costs a full forward pass, KV-cache growth sets concurrency limits, and runtime memory management plus pre-deploy quantization decides cost on fixed GPUs[^clyburn-inference].

## Inference is a stack

Serving needs three pieces together: model weights, inference server, and hardware accelerator[^clyburn-inference]:

- **Model weights:** billions of learned parameters, for example Kimi, GLM, or Qwen.
- **Inference server:** software such as vLLM that loads the model, manages requests, and applies batching, paging, and caching optimizations.
- **Hardware accelerator:** usually a GPU doing the numerical work.

Running a model directly on a GPU with PyTorch works for a notebook or single user; serving many users at production scale needs the server layer, analogized in the source to opening `.html` locally versus serving it with Apache httpd[^clyburn-inference].

## Autoregressive generation

LLMs emit one token at a time, with each new token conditioned on all prior tokens including tokens just generated[^clyburn-inference].

Example from the source: `The quick brown` predicts `fox`, then `The quick brown fox` predicts `jumps`, continuing until a special end-of-sequence token[^clyburn-inference].

Cost consequence: every response token needs a full model pass, so a 500-token answer means about 500 passes[^clyburn-inference].

A complementary first-principles account adds that the transformer produces one hidden state per input token and projects them to vocabulary logits, but only the last token's logits are sampled; that token is appended and the loop repeats, so only the most recent hidden state is directly needed while the rest are intermediate byproducts[^kv-explainer].

## Why the KV cache exists

Each pass turns tokens into embeddings flowing through transformer layers; every layer has a self-attention block where tokens attend to each other[^clyburn-inference].

Attention uses three vectors per token[^clyburn-inference]:

- **Q, query:** what the current token wants from context.
- **K, key:** the kind of information a token holds.
- **V, value:** its actual content.

Next-token prediction compares the current query against keys of all prior tokens and takes a weighted sum of values. The query is needed only for the current token, while keys and values for history do not change across steps, so recomputing them wastes work[^clyburn-inference].

In last-row terms, the final row of `QK^T` uses the query of the last token against all keys, and its output uses the same query against all keys and values; each attention layer therefore needs Q from the latest token plus K and V from everything[^kv-explainer].

The redundancy is concrete: generating token 50 needs K/V for tokens 1-50, generating token 51 needs K/V for tokens 1-51, while tokens 1-49 are unchanged with the same inputs and outputs; naively recomputing them is O(n) redundant work per step and O(n²) wasted compute over generation[^kv-explainer].

The KV cache therefore saves K and V in GPU memory at every layer and computes K/V only for the new token; savings multiply by layer count[^clyburn-inference]. Each step computes Q, K, and V only for the newest token, appends the new K/V to the cache, retrieves prior K/V from memory, and runs attention with the new Q against the full cached K/V[^kv-explainer]. Attention work still scales with sequence length, but the expensive K/V projections happen once per token rather than once per step[^kv-explainer].

## How big the KV cache gets

Per-token cache size follows[^clyburn-inference]:

```text
2 × num_layers × num_kv_heads × head_dim × dtype_bytes
```

The factor of 2 covers K and V.

Worked `gpt-oss-120b` example from the source: 36 layers, 8 KV heads, head dim 64, 2 bytes per value gives about 72 KB per token, but only half the layers retain full history, so the growing figure is about 36 KB per token[^clyburn-inference]:

| Context | Reported cache |
|---|---:|
| 2k, typical chat turn | ~75 MB |
| 8k, standard production tier | ~300 MB |
| 32k, long document or codebase | ~1.2 GB |
| 128k, gpt-oss max | ~4.8 GB |

Contrast with a dense 70B such as Llama 3.3 70B with 80 layers and 128 head dim: about 320 KB per token, roughly 9× more for the same conversation, so architecture choice directly affects serving cost[^clyburn-inference].

A second scale anchor is Qwen 2.5 72B with 80 layers, 32K context, and hidden dimension 8192: the KV cache for one request can consume several gigabytes of GPU memory, at hundreds of concurrent requests often exceeding the model weights themselves, and doubling context length doubles per-request cache and reduces concurrency[^kv-explainer].

## Where the GPU budget goes

The source presents `gpt-oss-120b` fitting on one 80 GB H100, leaving about 15–20 GB for KV cache after weights[^clyburn-inference]:

- **Naive max-reservation:** reserve per request for the maximum context it might reach. At 4.8 GB per request, only about 3 concurrent users fit.
- **Actual-use allocation:** allocate what each request uses. A typical 8k request at 300 MB allows about 50–60 users on the same card.

Same model and GPU, different memory management — hence the source's emphasis that managing KV memory is central to inference economics[^clyburn-inference].

## Prefill, decode, and time-to-first-token

Prompt processing runs one forward pass over the whole input, computing and caching K and V for every token; this prefill phase is the most compute-intensive part of the request[^kv-explainer].

Once the cache is warm, each later token needs only a single-token forward pass, so tokens stream quickly after a slow start[^kv-explainer].

That initial delay is time-to-first-token (TTFT); longer prompts mean longer prefills and longer waits, summarized as building the cache is expensive while reading from it is cheap[^kv-explainer].

The source lists chunked prefill, speculative decoding, and prompt caching as TTFT optimizations but treats them as a separate deep topic without method detail[^kv-explainer].

Practical claim from this explainer: KV caching makes LLM inference roughly 5x faster in practice, and every major serving stack including vLLM, TGI, and TensorRT-LLM builds on this idea[^kv-explainer].

## Production runtime optimizations

These change serving efficiency without changing the model[^clyburn-inference]:

- **PagedAttention:** split KV cache into small fixed-size blocks that can live anywhere in memory, with a table tracking each request's blocks. Nothing is reserved for unused context; the source compares the idea to OS virtual memory.
- **Continuous batching:** do not wait for a whole batch to finish together. Finished requests leave and new ones join as slots free, keeping the GPU fed.
- **Prefix caching:** when requests share a prefix — system prompt, retrieved document, or the same repo file in a coding agent — reuse cached K and V instead of recomputing.

## Shrinking the model before deployment

Quantization stores weights or activations in lower precision. Most models ship at BF16; FP8 or INT8 roughly halves memory and 4-bit is roughly one quarter[^clyburn-inference].

`gpt-oss-120b` case: 117B parameters in hypothetical BF16 would be about 234 GB and need three 80 GB GPUs; shipped MXFP4 quantization on MoE weights brings it under 80 GB on one card[^clyburn-inference].

Two wins are distinguished[^clyburn-inference]:

- **Quantized weights:** less data moved from HBM into SRAM every forward pass, a latency win.
- **Quantized activations:** tensor cores do lower-precision math at more operations per second, a throughput win.

Weight-only `W8A16` gets the first win; `W8A8` gets both[^clyburn-inference].

Practical guidance reported in the source: FP8 halves memory and buys up to about 1.6× throughput with minimal accuracy impact; calibrated methods such as GPTQ, AWQ, and SmoothQuant use a small representative dataset to identify and protect important weights, with quality loss typically under a point[^clyburn-inference].

The summary table also lists sparsification as a pre-deploy technique that skips the least-important weights, but the body gives no further method, evidence, or tuning detail[^clyburn-inference].

## Cost takeaway

Training happens once; inference happens per message and dominates the bill. The KV cache grows with context length and concurrent users, and the gap between naive and tuned deployment on the same H100 is presented as roughly 3 versus 50 concurrent users[^clyburn-inference].

| Technique | Where it applies | Reported benefit |
|---|---|---|
| PagedAttention | Runtime | More concurrent requests in same memory |
| Continuous batching | Runtime | GPU stays busy between requests |
| Prefix caching | Runtime | Skips recompute on shared context |
| Quantization | Model, pre-deploy | Fewer GPUs, faster loading, faster math |
| Sparsification | Model, pre-deploy | Skips least-important weights |

## Relationships

- Related to [PagedAttention for LLM Serving](paged-attention.md) — synthesis: block tables, on-demand growth, copy-on-write sharing, batching, preemption, and evaluation detail behind the PagedAttention summary above.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: paged block layout behind the PagedAttention memory-saving claim above.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — synthesis: vLLM's hash, allocation, eviction, and workload mechanics behind the shared-prefix reuse claim above.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — synthesis: format, hardware, and plugin selection behind deploying the BF16/FP8/INT4 trade-offs above.
- Uses [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — synthesis: offline FP8/INT4/INT8 recipes relevant to the Qwen + LLM Compressor course path mentioned below.
- Related to [Grouped-Query Attention](grouped-query-attention.md) — synthesis: fewer KV heads directly lowers the `num_kv_heads` term in the cache-size formula above; the KV-cache explainer independently cites GQA/MQA head-sharing as the memory fix with minimal quality loss[^kv-explainer].
- Related to [Distributed Inference Core Concepts and Scaling Dimensions](distributed-inference-core-concepts.md) — synthesis: prefill/decode split and parallelism dimensions extend this single-GPU cost picture to distributed serving; the prefill/TTFT mechanics above ground that split in cache construction versus cache reads[^kv-explainer].
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — synthesis: disaggregation, tiered/shared KV cache, and speculative-decoding choices beyond the three runtime techniques summarized here.
- Related to [llama.cpp vs vLLM Local Inference Choice](llamacpp-vs-vllm.md) — synthesis: single-user local inference versus high-concurrency GPU serving distinction behind the PyTorch versus inference-server point above.
- Related to [W8A8 INT8 Quantization Mechanics](w8a8-int8-quantization-mechanics.md) — synthesis: SmoothQuant plus GPTQ mechanics behind the W8A16 versus W8A8 latency/throughput distinction above.

## Coverage limits

- KV-cache explainer source was read in full as Markdown; no local attachments were referenced, and embedded behavior such as ChatGPT/Claude streaming delay was used only as motivation, not evidence[^kv-explainer].

- Source text and summary table of the inference explainer were read in full; embedded images and GIFs linked from X/pbs.twimg were not inspected, so visual-only evidence is not captured[^clyburn-inference].
- No local attachments were referenced by either raw file.
- All layer/head/dimension counts, MB/GB cache figures, H100 headroom, 3-versus-50 concurrency, 234 GB and MXFP4 fit, FP8 1.6× throughput, sub-point accuracy-loss, Qwen 2.5 72B several-GB, doubling-context, last-row attention, O(n)/O(n²), ~5x speedup, and vLLM/TGI/TensorRT-LLM claims are source-reported and not independently verified.
- Model examples such as `gpt-oss-120b` and Llama 3.3 70B, plus the free DeepLearning.AI plus Red Hat course path using LLM Compressor, vLLM, GuideLLM, and lm-eval on Qwen, are source-reported; course availability and tool behavior were not checked.
- No secrets, credentials, tokens, private keys, or PII were found in either source.

[^clyburn-inference]: Cedric Clyburn on X, “How AI Inference Works, Clearly Explained” — `../raw/HowAIInferenceWorksClearlyExplained.md`, covering inference stack, autoregressive generation, Q/K/V and KV-cache rationale, per-token size formula, gpt-oss-120b and dense-70B sizing, H100 budget example, PagedAttention, continuous batching, prefix caching, quantization including MXFP4/FP8/W8A16/W8A8/GPTQ/AWQ/SmoothQuant, sparsification table entry, cost takeaway, and course pointer.
[^kv-explainer]: “KV Caching in LLMs, Clearly Explained” — `../raw/KVCachinginLLMsClearlyExplained.md`, covering last-token logits sampling, last-row Q/K/V mechanics, O(n)-per-step and O(n²)-total recompute redundancy, cache-append plus cached-attention fix, prefill versus decode and TTFT, chunked-prefill/speculative-decoding/prompt-caching pointer, Qwen 2.5 72B memory scale, GQA/MQA memory rationale, ~5x speedup claim, and vLLM/TGI/TensorRT-LLM stack note.
