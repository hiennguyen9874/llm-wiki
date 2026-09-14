---
type: Concept
title: SGLang EPD Disaggregation
description: Separate encoder, prefill, and decode stages for VLM inference with independent encoder scaling and three-tier deployment.
tags: [sglang, multimodal, disaggregated-inference, vision-encoder, prefill-decode]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:29:13Z }
sources:
  - id: sgl-epd-disagg
    resource: ../raw/sglang/advanced_features/epd_disaggregation.mdx
    title: EPD Disaggregation
  - id: epd-blog-20260112
    resource: ../raw/2026-01-12-epd/index.md
    title: "EPD Disaggregation: Elastic Encoder Scaling for Vision-Language Models in SGLang"
---

SGLang EPD disaggregation separates Vision-Language Model inference into independent Encoder, Prefill, and Decode tiers, allowing encoder servers to scale horizontally apart from language prefill/decode and to compose with existing PD disaggregation[^sgl-epd-disagg].

## Stage decomposition

VLM request execution decomposes into three stages with different resource profiles[^sgl-epd-disagg]:

- **Encoder:** vision preprocessing plus ViT-based image encoding; highly compute-intensive but only required during request initialization.
- **Prefill:** processes the full multimodal input sequence to initialize the language-model KV cache.
- **Decode:** autoregressive token generation dominated by memory bandwidth and KV-cache access.

## Motivation

Existing deployments colocate all three stages in a unified engine, or at best apply Prefill–Decode (PD) disaggregation[^sgl-epd-disagg]:

- Vision encoding stays tightly coupled to language prefill.
- Resource utilization is inefficient and scalability for image-heavy workloads is limited.
- Scheduling under load is suboptimal.

EPD addresses this by separating vision encoding from language processing, enabling independent horizontal scaling of encoder servers and improved load balancing for multimodal requests[^sgl-epd-disagg].

## Why ViT favors horizontal encoder scaling

Vision encoders have far fewer parameters than the language component, so tensor parallelism adds per-layer communication overhead that can dominate execution and make encoding slower at higher TP[^epd-blog-20260112]. A Qwen2.5-VL-72B measurement on H20 with 4 images per request reports[^epd-blog-20260112]:

| tp | vit mean time |
| --- | --- |
| 2 | 492.13ms |
| 4 | 465.80ms |
| 8 | 523.80ms |

EPD sidesteps this by scaling encoders horizontally with data-parallel image sharding instead of raising encoder TP[^epd-blog-20260112]. This synthesis links the same small-encoder TP-overhead rationale behind the intra-server DP-encoder alternative described in [SGLang Data-Parallel Multimodal Encoder](sglang-dp-multimodal-encoder.md)[^epd-blog-20260112].

## Request flow

The blog request path is: client sends a multimodal request to prefill; prefill shards images across encoders; encoders run ViT and return embeddings plus image-grid metadata; prefill fuses embeddings with text into `mm_inputs` with pre-computed tensors; the LLM runs prefill and either decodes locally or ships KV to decode when PD disaggregation is enabled[^epd-blog-20260112]. The inspected `epd_workflow.png` sequence diagram shows the same path, including image shards to Encoder 0/1, embedding transfer back to prefill, local fuse plus prefill and KV build, then either KV transfer to Decode with Decode streaming tokens or prefill streaming tokens directly when PD is off[^epd-blog-20260112].

## Enablement

Launch an encoder-only or language-only server[^sgl-epd-disagg]:

- `--encoder-only` — encoder-only model instance.
- `--language-only` — language-only model instance.
- `--encoder-urls` — required on language-only servers; lists encoder service endpoints.
- `--encoder-transfer-backend` — encoder transfer backend; one of `zmq_to_scheduler`, `zmq_to_tokenizer`, and `mooncake`, with `zmq_to_scheduler` as default.

## Deployment shapes

### EP disaggregation

Two encoder servers plus one combined language-only server, illustrated with `Qwen/Qwen3-VL-8B-Instruct`[^sgl-epd-disagg]:

```bash
# encoder 0
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-VL-8B-Instruct \
  --encoder-only \
  --encoder-transfer-backend zmq_to_scheduler \
  --port 30000
# encoder 1
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-VL-8B-Instruct \
  --encoder-only \
  --encoder-transfer-backend zmq_to_scheduler \
  --port 30001
# language-only server
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-VL-8B-Instruct \
  --language-only \
  --encoder-urls http://127.0.0.1:30000 http://127.0.0.1:30001 \
  --encoder-transfer-backend zmq_to_scheduler \
  --port 30002
```

### EPD disaggregation

Two encoder servers plus split prefill and decode servers fronted by a PD-aware router, forming a fully decoupled three-tier architecture[^sgl-epd-disagg]:

```bash
# prefill 0
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-VL-8B-Instruct \
  --disaggregation-mode prefill \
  --language-only \
  --encoder-urls http://127.0.0.1:30000 http://127.0.0.1:30001 \
  --encoder-transfer-backend zmq_to_scheduler \
  --port 30002
# decode 0
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-VL-8B-Instruct \
  --disaggregation-mode decode \
  --port 30003
# router
python -m sglang_router.launch_router \
  --pd-disaggregation \
  --prefill http://$PREFILL_HOST:30002 \
  --decode http://$DECODE_HOST:30003 \
  --port 8000
```

Encoder launch flags are the same as the EP shape; the prefill server adds `--disaggregation-mode prefill` alongside `--language-only` and `--encoder-urls`, the decode server uses `--disaggregation-mode decode`, and the router uses `--pd-disaggregation` with `--prefill` and `--decode` endpoints[^sgl-epd-disagg].

## Image distribution

Unlike tensor parallelism, EPD uses data parallelism across independent encoder instances and distributes images among them[^epd-blog-20260112]. The documented example shards 7 images across 3 encoders after shuffling as 3/2/2 images, enabling intra-request parallelism because different images in one request encode independently[^epd-blog-20260112].

## Transfer backend behavior

The three encoder transfer backends are `zmq_to_scheduler` (default), `zmq_to_tokenizer`, and `mooncake`[^epd-blog-20260112]:

- **zmq_to_scheduler:** direct ZMQ socket path from encoder to scheduler via the RDMA transfer engine without blocking[^epd-blog-20260112].
- **zmq_to_tokenizer:** embeddings go to the tokenizer manager and are processed during tokenization[^epd-blog-20260112].
- **mooncake:** RDMA-based multi-node transfer registering embeddings in shared memory for high-bandwidth, low-latency movement[^epd-blog-20260112].

Do not confuse `--encoder-transfer-backend` for this E→P embedding leg with `--disaggregation-transfer-backend` for the P→D KV leg; the blog deployment uses `nixl` for the latter while keeping ZMQ-family or Mooncake semantics for the former[^epd-blog-20260112].

## Vision embedding cache

Encoders support prefix multimodal caching to skip redundant ViT work for repeated images, reducing both compute and embedding-transfer overhead[^epd-blog-20260112]. Cache size is configurable with a 4GB default via `SGLANG_VLM_CACHE_SIZE_MB`; the blog encoder example enables it with `--enable-prefix-mm-cache` while setting `SGLANG_VLM_CACHE_SIZE_MB=0` on the language-only prefill[^epd-blog-20260112].

## When EPD helps

EPD targets vision-heavy multi-image workloads where visual encoding is the bottleneck[^epd-blog-20260112]. In image-heavy cases it reports roughly 6–8× lower TTFT under load than colocation at 1 QPS; in image-light cases with few images the extra embedding-transfer latency can outweigh encoding savings and raise TTFT versus colocation[^epd-blog-20260112]. Dedicated encoder GPUs may idle in image-light serving, so EPD is most resource-efficient when visual processing dominates[^epd-blog-20260112].

## Benchmark evidence

Experimental setup is 8× H20 96GB GPUs with Qwen3-VL-235B-A22B-Instruct-FP8 on a random multimodal dataset (128/256 text tokens, 1–8 random images averaging about 4, 1080p resolution, 0.2–1.0 QPS)[^epd-blog-20260112]. Deployments compared are Colocate (1 PD instance, TP=4, 4× H20), 1E1P (1 TP=1 encoder plus 1 TP=4 PD instance, 5× H20), and 2E1P (2 TP=1 encoders plus 1 TP=4 PD instance, 6× H20)[^epd-blog-20260112].

Reported findings versus colocate[^epd-blog-20260112]:

- TTFT stays much lower under load, about 6–8× lower at 1 QPS.
- TPOT stays far below colocate, about 8–10× lower.
- Request throughput roughly doubles at higher QPS, about 2× at 0.8–1.0 QPS.
- The gain exceeds the extra GPU cost: 2E1P uses 50% more GPUs (6× versus 4× H20) for a disproportionately larger latency and throughput improvement.
- The higher 2E1P TPOT relative to 1E1P is attributed to its larger decode batch size.

The inspected TTFT, TPOT, and throughput charts are consistent in shape with these ratios; exact plotted points were not transcribed because the TTFT and TPOT axes are logarithmic and the source text already states the headline ratios[^epd-blog-20260112].

## Blog deployment notes

The blog Qwen2.5-VL-7B-Instruct example launches `--encoder-only` encoders with `--enable-prefix-mm-cache`, a `--language-only` prefill with `--disaggregation-mode prefill`, `--disaggregation-transfer-backend nixl`, `--tp 1`, `--mem-fraction-static 0.5`, `--disable-radix-cache`, `--chunked-prefill-size 8192`, and an explicit multi-URL `--encoder-urls` list, plus a `--disaggregation-mode decode` decoder and a mini-LB router with `--pd-disaggregation --mini-lb --prefill --decode`[^epd-blog-20260112]. The prefill example disables the language-side VLM cache while encoders keep prefix-MM caching enabled[^epd-blog-20260112].

## Relationships

- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — the P→D leg EPD composes with; when PD is enabled the existing prefill-to-decode transfer logic is reused, otherwise the language-only prefill decodes locally[^epd-blog-20260112].
- Uses [vLLM Disaggregated Encoder](vllm-disaggregated-encoder.md) — vLLM analog separating vision encoding from prefill/decode with EC-connector transfer; SGLang EPD covers the same E→PD shape plus the full E→P→D tier via `--encoder-only` / `--language-only`.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — vLLM analog for the P→D leg with connector-mediated KV transfer; SGLang EPD composes its encoder split with `--disaggregation-mode prefill|decode` plus a `--pd-disaggregation` router.
- Uses [SGLang Data-Parallel Multimodal Encoder](sglang-dp-multimodal-encoder.md) — alternative intra-server encoder optimization via `--mm-enable-dp-encoder`; EPD instead places encoders on independent servers for horizontal scaling.

## Coverage limits

- `epd_workflow.png`, `epd_architecture.svg`, and the TTFT, TPOT, and throughput charts under `../raw/2026-01-12-epd/assets/` were inspected; chart numbers above reuse the source-text ratios rather than transcribing log-scale plot points.
- The roadmap link to Encoder Disaggregation (2025 Q4) issue 15118 was not fetched.
- Individual contributor handles in the acknowledgments were omitted as non-durable provenance; organizational attribution is in the source file itself.

[^epd-blog-20260112]: EPD Disaggregation: Elastic Encoder Scaling for Vision-Language Models in SGLang — `../raw/2026-01-12-epd/index.md`, covering ViT TP scaling table and horizontal-scaling rationale, five-step E→P→D request flow, 7-image data-parallel shuffle distribution, `zmq_to_scheduler` / `zmq_to_tokenizer` / `mooncake` embedding-transfer semantics, prefix-MM vision-embedding cache with `SGLANG_VLM_CACHE_SIZE_MB` default 4GB, image-heavy versus image-light guidance, 8× H20 Qwen3-VL-235B-A22B-FP8 benchmark setup with Colocate / 1E1P / 2E1P GPU counts and TTFT / TPOT / throughput findings plus decode-batch TPOT caveat, and Qwen2.5-VL-7B `--encoder-only` / `--language-only` plus NIXL PD-leg, `--disable-radix-cache`, chunked-prefill, and mini-LB launch commands.
[^sgl-epd-disagg]: EPD Disaggregation — `../raw/sglang/advanced_features/epd_disaggregation.mdx`, covering Encoder/Prefill/Decode resource profiles, colocated and PD-only coupling limits, independent encoder scaling and load-balancing rationale, `--encoder-only` / `--language-only` / `--encoder-urls` / `--encoder-transfer-backend` with `zmq_to_scheduler`, `zmq_to_tokenizer`, and `mooncake` options, and Qwen3-VL-8B EP and EPD launch plus `--pd-disaggregation` router commands.
