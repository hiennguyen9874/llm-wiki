---
type: Concept
title: Kimi K3 DSpark Speculator
description: Long-context DSpark draft model for Kimi K3 with 1M-token serving, block-size-7 drafting, and reported acceptance lengths.
tags: [kimi, dspark, speculative-decoding, sglang, long-context, specforge]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T13:02:19Z }
sources:
  - id: kimi-k3-dspark
    resource: ../raw/Kimi-K3-DSpark.md
    title: Kimi K3 DSpark speculator
---

RadixArk's DSpark speculator accelerates [Kimi K3](kimi-k3.md) with block-size-7 semi-autoregressive drafting, a Markov logit-bias head, and a per-position confidence head, served in SGLang with a 1M-token context and reported acceptance lengths of roughly 3–5.5 on short-context suites and 4.26 on 1M-token RULER V2[^kimi-k3-dspark].

## Model identity and architecture

- Target is `moonshotai/Kimi-K3`; draft checkpoint is `RadixArk/Kimi-K3-DSpark`[^kimi-k3-dspark].
- Extends the DFlash parallel-draft backbone with a Markov logit-bias head and a per-position confidence head[^kimi-k3-dspark].
- Draft shape: 5 full-attention Qwen3-style GQA layers, hidden size 7168, 64 query heads / 16 KV heads, `block_size=7`[^kimi-k3-dspark].
- Verification width is 1 current token plus 7 draft tokens[^kimi-k3-dspark].
- Auxiliary target layers used for distillation: `[7, 23, 51, 67, 83]`[^kimi-k3-dspark].
- Format is single-file BF16 Safetensors with 2,249,289,601 parameters; embedding and unembedding weights are not included[^kimi-k3-dspark].
- Trained context is 65,536 tokens; serving context extends to 1,048,576 tokens via YaRN-16 enabled by default in the draft config (`original_max_position_embeddings=65536`, `max_position_embeddings=1048576`), so no separate draft config override is required[^kimi-k3-dspark].

## Acceptance-length evaluation

`acc_len` is SGLang's histogram-native request acceptance length, averaged within each question and then equally across questions[^kimi-k3-dspark].

| Dataset | Questions | acc_len |
| --- | ---: | ---: |
| SWE-Rebench | 50 | 4.6594 |
| GSM8K | 1,319 | 5.4176 |
| MATH500 | 500 | 4.1329 |
| HumanEval | 164 | 5.5121 |
| MBPP | 257 | 5.1980 |
| MT-Bench | 80 | 3.9342 |
| AIME26 | 30 | 2.9893 |
| RULER V2 1M (MK/MV/QA) | 150 (50 per partition) | 4.2553 |

All figures above are source-reported[^kimi-k3-dspark].

RULER V2 uses the 1M input configuration with actual prompts spanning 1,000,432–1,047,925 tokens; per-partition `acc_len` is 4.4658 for MK, 4.3081 for MV, and 3.9919 for QA[^kimi-k3-dspark].

AIME26 split by output length[^kimi-k3-dspark]:

| Output-token bucket | Questions | Actual output range | acc_len |
| --- | ---: | ---: | ---: |
| 0–1K | 13 | 192–885 | 3.1310 |
| 1–2K | 5 | 1,359–1,828 | 2.5773 |
| 2–4K | 6 | 2,210–3,732 | 2.5632 |
| 4–8K | 4 | 5,187–7,750 | 2.7174 |
| 8–16K | 0 | — | — |
| 16–32K | 0 | — | — |
| 32K+ | 2 | 54,545–224,703 | 4.9194 |

## Serving with SGLang

Reference launch from the source, with the SGLang Cookbook Kimi K3 recipes as the deployment reference[^kimi-k3-dspark]:

```bash
sglang serve \
  --trust-remote-code \
  --model-path moonshotai/Kimi-K3 \
  --tp-size 8 \
  --dcp-size 8 \
  --mem-fraction-static 0.85 \
  --max-mamba-cache-size 160 \
  --max-running-requests 32 \
  --cuda-graph-max-bs-decode 32 \
  --reasoning-parser kimi_k3 \
  --tool-call-parser kimi_k3 \
  --host 0.0.0.0 \
  --port 30000 \
  --speculative-algorithm DSPARK \
  --speculative-draft-model-path RadixArk/Kimi-K3-DSpark \
  --speculative-dspark-block-size 7 \
  --speculative-draft-attention-backend trtllm_mha \
  --enable-linear-replayssm-spec \
  --context-length 1048576 \
  --chunked-prefill-size 16384
```

Notable choices are `--speculative-algorithm DSPARK` with `--speculative-dspark-block-size 7`, `trtllm_mha` draft attention backend, `--enable-linear-replayssm-spec`, TP8 plus DCP8 parallelism, and `--context-length 1048576` with `--chunked-prefill-size 16384`[^kimi-k3-dspark].

## Training details

- Framework is SpecForge online distillation with hidden states captured from a frozen Kimi K3 target served by a live SGLang engine; draft trained from random initialization[^kimi-k3-dspark].
- Loss is `0.1 CE + 0.9 L1 distillation + 1.0 confidence BCE`, decay gamma 4.0, with 512 sampled anchors per sequence and `block_size=7`[^kimi-k3-dspark].
- Topology is 4 nodes × 4 GB300 (16 ranks): 2 × TP8 target replicas, DP2 sampler, FSDP16 `SHARD_GRAD_OP` on the draft, TP-batch scatter[^kimi-k3-dspark].
- Batch is 8 per replica × 32 accumulation steps × 2 replicas for a global batch of 512[^kimi-k3-dspark].

## Relationships

- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — this checkpoint is a long-context DSpark instance using confidence-driven variable-length verification and ragged verify.
- Uses [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — DSpark extends the DFlash parallel-draft backbone with the Markov logit-bias and confidence heads.
- Related to [Kimi K3 Local Deployment](kimi-k3.md) — same Kimi K3 base model served here with server-side speculative decoding rather than local GGUF inference.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — base EAGLE/MTP speculation surface this DSpark path is an alternative to.

## Coverage limits

- No local attachments were referenced by the source; Hugging Face checkpoints (`moonshotai/Kimi-K3`, `RadixArk/Kimi-K3-DSpark`), the SGLang Cookbook recipes, SpecForge, and the live SGLang target engine were not inspected beyond the source description[^kimi-k3-dspark].
- Acceptance lengths are source-reported SGLang histogram-native figures with the stated averaging; throughput, latency, speedup, and harness details beyond `acc_len` are not given in the source and are not compiled here[^kimi-k3-dspark].
- Launch flags, TP8/DCP8 topology, memory fraction, batch caps, and chunked-prefill size are workload-specific values from the reference command, not universal defaults[^kimi-k3-dspark].

[^kimi-k3-dspark]: Kimi K3 DSpark speculator — `../raw/Kimi-K3-DSpark.md`.
