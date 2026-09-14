---
type: Concept
title: Qwen3.8-27B DSpark Speculator
description: DSpark draft model for Qwen3.8-27B targets with block-size-7 drafting, v1/v2 acceptance gains, and SGLang throughput results.
tags: [qwen3.8, dspark, speculative-decoding, sglang, specforge]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:00:00Z }
sources:
  - id: qwen38-dspark
    resource: ../raw/Qwen3.8-27B-DSpark.md
    title: Qwen3.8-27B-DSpark
---

RadixArk's DSpark speculator accelerates Qwen3.8-27B targets with block-size-7 semi-autoregressive drafting, a VanillaMarkov head, and seven draft proposals per step, trained with SpecForge and served in SGLang with v2 acceptance around 3.2–6.3 and up to 3.16x autoregressive throughput at concurrency 1[^qwen38-dspark].

## Model identity and architecture

- Draft checkpoint is `RadixArk/Qwen3.8-27B-DSpark`; evaluated targets are `RadixArk/Qwen3.8-27B-NVFP4` and `Qwen/Qwen3.8-27B-FP8`[^qwen38-dspark].
- Acceptance-length evaluation uses the NVFP4 target; throughput evaluation uses the FP8 target[^qwen38-dspark].
- Draft parameters: 1,857,358,337 (1.86B); weight dtype BF16[^qwen38-dspark].
- Hidden size 5,120 with five full-attention transformer layers[^qwen38-dspark].
- Attention is GQA with 32 query heads and eight key/value heads[^qwen38-dspark].
- Target auxiliary feature layers: 5, 19, 33, 47, 61[^qwen38-dspark].
- Markov head is VanillaMarkov with rank 256[^qwen38-dspark].
- Training target width is 16 future positions; serving gamma is seven draft proposals[^qwen38-dspark].
- Target verification width is eight tokens, including the target bonus token[^qwen38-dspark].
- Maximum position embeddings: 262,144[^qwen38-dspark].
- Serving configuration uses `block_size=7`; separate `training_block_size=16` records the supervision width used during training[^qwen38-dspark].

## Acceptance length

Results cover 64,675 completed requests across 17 workloads[^qwen38-dspark].

| Category | Workload | Prompts | DSpark v1 | DSpark v2 |
| --- | --- | ---: | ---: | ---: |
| Code | HumanEval | 164 | 3.0437 | **3.8468** |
| Code | MBPP | 257 | 3.2299 | **4.0603** |
| Code | LiveCodeBench | 1,055 | 2.5915 | **3.3462** |
| Code | BigCodeBench | 1,140 | 2.7752 | **3.4678** |
| Math | GSM8K | 1,319 | 3.6030 | **4.5162** |
| Math | MATH-500 | 500 | 3.2559 | **4.2267** |
| Math | AIME 2025 | 30 | 2.9798 | **3.9401** |
| Math | AMC23 | 40 | 3.2111 | **4.1572** |
| Math | GSM-Symbolic | 2,048 | 3.4554 | **4.2716** |
| Chat | MT-Bench | 80 | 2.6075 | **3.2860** |
| Chat | Alpaca | 52,002 | 2.5659 | **3.2337** |
| Chat | Arena-Hard-v2 | 750 | 2.5910 | **3.2536** |
| Chat | IFEval | 541 | 2.9457 | **3.6628** |
| Misc. | MMLU-Pro | 2,048 | 2.8345 | **3.5964** |
| Misc. | GPQA-Diamond | 198 | 2.7634 | **3.5109** |
| Misc. | LongBench-v2 | 503 | 3.2602 | **3.9268** |
| Misc. | RULER-8K | 2,000 | 4.9585 | **6.3009** |

| Aggregate | DSpark v1 | DSpark v2 | Change |
| --- | ---: | ---: | ---: |
| Request-count weighted, 64,675 prompts | 2.721143 | **3.428567** | **+26.00%** |
| Workload macro, 17 workloads | 3.098368 | **3.917881** | **+26.45%** |

Acceptance-length protocol[^qwen38-dspark]:

- Runtime: SGLang v0.5.17.
- Hardware and topology: four NVIDIA GB300 GPUs, DP4 x TP1.
- Sampling: thinking enabled, temperature 1.0, top-p 0.95, top-k 20, seed 980406.
- Generation limit: 8,192 tokens; client concurrency: 128.

## Throughput

Throughput is total output tokens divided by end-to-end timed wall duration; each speculative-decoding cell is `output tok/s (speedup over autoregressive)`[^qwen38-dspark].

### Concurrency 1

| Workload | Autoregressive | EAGLE | DSpark v1 | DSpark v2 |
| --- | ---: | ---: | ---: | ---: |
| GSM8K | 94.2 | 179.9 (1.91x) | 238.6 (2.53x) | **297.3 (3.16x)** |
| MATH-500 | 95.0 | 174.0 (1.83x) | 214.4 (2.26x) | **280.0 (2.95x)** |
| HumanEval | 95.8 | 165.5 (1.73x) | 205.5 (2.14x) | **254.8 (2.66x)** |
| MBPP | 93.8 | 166.7 (1.78x) | 208.6 (2.22x) | **261.6 (2.79x)** |
| MT-Bench | 95.8 | 157.4 (1.64x) | 171.3 (1.79x) | **215.8 (2.25x)** |

### Concurrency 8

| Workload | Autoregressive | EAGLE | DSpark v1 | DSpark v2 |
| --- | ---: | ---: | ---: | ---: |
| GSM8K | 602.7 | 1,001.1 (1.66x) | 1,183.8 (1.96x) | **1,494.0 (2.48x)** |
| MATH-500 | 635.2 | 1,071.6 (1.69x) | 1,208.2 (1.90x) | **1,575.1 (2.48x)** |
| HumanEval | 667.9 | 1,031.3 (1.54x) | 1,159.2 (1.74x) | **1,435.1 (2.15x)** |
| MBPP | 635.4 | 988.3 (1.56x) | 1,123.7 (1.77x) | **1,393.7 (2.19x)** |
| MT-Bench | 647.9 | 963.2 (1.49x) | 958.4 (1.48x) | **1,195.5 (1.85x)** |

### Concurrency 32

| Workload | Autoregressive | EAGLE | DSpark v1 | DSpark v2 |
| --- | ---: | ---: | ---: | ---: |
| GSM8K | 1,298.5 | 1,969.5 (1.52x) | 1,934.2 (1.49x) | **2,268.5 (1.75x)** |
| MATH-500 | 1,764.2 | 2,353.4 (1.33x) | 2,014.2 (1.14x) | **2,545.2 (1.44x)** |
| HumanEval | 1,862.2 | 2,296.9 (1.23x) | 1,918.5 (1.03x) | **2,472.3 (1.33x)** |
| MBPP | 1,738.4 | 2,286.3 (1.32x) | 1,926.3 (1.11x) | **2,413.1 (1.39x)** |
| MT-Bench | 1,814.2 | **2,133.4 (1.18x)** | 1,593.3 (0.88x) | 1,973.0 (1.09x) |

Throughput protocol[^qwen38-dspark]:

- EAGLE uses the target-integrated MTP head loaded as `Qwen3_5ForCausalLMMTP`, without an external draft checkpoint.
- Hardware and topology: one NVIDIA H200 per workload, TP1 x DP1.
- 128 prompts per cell, dataset shuffle seed 42, concurrency 1/8/32, `max_tokens=2048`, reasoning effort `xhigh`, temperature 1.0, top-p 0.95, top-k 20.
- EAGLE serving: three speculative steps, top-k 1, four draft tokens, Mamba full-memory ratio 8.26, `extra_buffer` radix-cache strategy, float32 Mamba state.
- DSpark serving: gamma 7, target verify width 8, one speculative step, block size 7, Mamba full-memory ratio 11.93, `extra_buffer` radix-cache strategy, float32 Mamba state.
- Autoregressive and EAGLE serving used `mem-fraction-static=0.85`; DSpark used 0.80 with expandable CUDA allocation segments. Every mode retained its complete prefill and speculative-verification CUDA graph set and used `max-running-requests=48`.

## Serving with SGLang

Reference launch from the source[^qwen38-dspark]:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
SGLANG_RAGGED_VERIFY_MODE=static \
sglang serve \
  --trust-remote-code \
  --model-path Qwen/Qwen3.8-27B-FP8 \
  --kv-cache-dtype fp8_e4m3 \
  --mem-fraction-static 0.80 \
  --attention-backend flashinfer \
  --chunked-prefill-size 32768 \
  --max-prefill-tokens 32768 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder \
  --mamba-full-memory-ratio 11.93 \
  --mamba-radix-cache-strategy extra_buffer \
  --mamba-ssm-dtype float32 \
  --max-running-requests 48 \
  --speculative-algorithm DSPARK \
  --speculative-draft-model-path RadixArk/Qwen3.8-27B-DSpark \
  --speculative-draft-model-quantization unquant \
  --speculative-draft-attention-backend flashinfer \
  --speculative-dspark-block-size 7 \
  --speculative-num-steps 1 \
  --speculative-eagle-topk 1 \
  --host 127.0.0.1 \
  --port 30000
```

## Artifact identity

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `model.safetensors` | 3,714,723,322 | `2aff025f45823b40ebe726b9dfa40302f3512bd9a11c3a7347de32a567acd9a7` |
| `config.json` | 2,448 | `dd65fb1b01c2adea69512ff2990a79d58eb7fe2c7ea97375aa66f657a29a5bfd` |

All artifact rows are source-reported[^qwen38-dspark].

## Relationships

- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — this checkpoint is a dense-27B DSpark instance using block-size-7 drafting with gamma-7 proposals and width-8 verification.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — base EAGLE/MTP speculation surface this DSpark path is an alternative to.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same Qwen3.8-27B base family served here with server-side speculative decoding rather than local GGUF/NVFP4 inference.
- Related to [Kimi K3 DSpark Speculator](kimi-k3-dspark.md) — sibling DSpark checkpoint with the same block-size-7 shape but a 1M-token YaRN serving context versus the 262K context here.

## Coverage limits

- No local attachments were referenced by the source; Hugging Face checkpoints (`RadixArk/Qwen3.8-27B-NVFP4`, `Qwen/Qwen3.8-27B-FP8`, `RadixArk/Qwen3.8-27B-DSpark`), SpecForge training, and the SGLang serving engines were not inspected beyond the source description[^qwen38-dspark].
- Acceptance lengths and throughput cells are source-reported figures under the stated SGLang, hardware, sampling, and concurrency protocols; MT-Bench concurrency-32 is the one cell where EAGLE beats DSpark v2 and is preserved as reported[^qwen38-dspark].
- Launch flags, Mamba memory ratios, radix-cache strategy, memory fractions, batch caps, and chunked-prefill sizes are workload-specific values from the reference commands, not universal defaults[^qwen38-dspark].

[^qwen38-dspark]: Qwen3.8-27B-DSpark — `../raw/Qwen3.8-27B-DSpark.md`.
