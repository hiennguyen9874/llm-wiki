---
type: Concept
title: SGLang EPD Disaggregation
description: Separate encoder, prefill, and decode stages for VLM inference with independent encoder scaling and three-tier deployment.
tags: [sglang, multimodal, disaggregated-inference, vision-encoder, prefill-decode]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-epd-disagg
    resource: ../raw/sglang/advanced_features/epd_disaggregation.mdx
    title: EPD Disaggregation
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

## Relationships

- Uses [vLLM Disaggregated Encoder](vllm-disaggregated-encoder.md) — vLLM analog separating vision encoding from prefill/decode with EC-connector transfer; SGLang EPD covers the same E→PD shape plus the full E→P→D tier via `--encoder-only` / `--language-only`.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — vLLM analog for the P→D leg with connector-mediated KV transfer; SGLang EPD composes its encoder split with `--disaggregation-mode prefill|decode` plus a `--pd-disaggregation` router.
- Uses [SGLang Data-Parallel Multimodal Encoder](sglang-dp-multimodal-encoder.md) — alternative intra-server encoder optimization via `--mm-enable-dp-encoder`; EPD instead places encoders on independent servers for horizontal scaling.

[^sgl-epd-disagg]: EPD Disaggregation — `../raw/sglang/advanced_features/epd_disaggregation.mdx`, covering Encoder/Prefill/Decode resource profiles, colocated and PD-only coupling limits, independent encoder scaling and load-balancing rationale, `--encoder-only` / `--language-only` / `--encoder-urls` / `--encoder-transfer-backend` with `zmq_to_scheduler`, `zmq_to_tokenizer`, and `mooncake` options, and Qwen3-VL-8B EP and EPD launch plus `--pd-disaggregation` router commands.
