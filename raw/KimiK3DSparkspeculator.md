---
library_name: transformers
pipeline_tag: text-generation
tags:
- speculative-decoding
- dspark
- dflash
- specforge
- sglang
- long-context
inference: false
---

# Kimi K3 DSpark speculator

## Overview

A long-context DSpark speculator for
[Kimi K3](https://huggingface.co/moonshotai/Kimi-K3). It supports context lengths of up to 1 million tokens.

A DSpark speculator for the Kimi K3 target, enabling faster inference through speculative decoding. 
DSpark extends the DFlash parallel-draft backbone with a Markov logit-bias head and a per-position confidence head. This checkpoint was trained with [SpecForge](https://github.com/sgl-project/SpecForge/) using hidden states from a live SGLang target engine.


## Model Specifications

- **Base model:** `moonshotai/Kimi-K3`
- **Format:** Safetensors (single-file BF16, 2,249,289,601 parameters)
- **Draft:** 5 full-attention Qwen3-style GQA layers, hidden size 7168,
  64 query heads / 16 KV heads, and `block_size=7`
- **Verification width:** 1 current token + 7 draft tokens
- **Auxiliary target layers:** `[7, 23, 51, 67, 83]`
- **Trained context:** 65,536 tokens
- **Target weights:** embedding and unembedding weights are not included

## Evaluation Results

`acc_len` is SGLang's histogram-native request acceptance length, averaged
within each question and then equally across questions. 

| Dataset | Questions | acc_len |
|---|---:|---:|
| SWE-Rebench | 50 | **4.6594** |
| GSM8K | 1,319 | **5.4176** |
| MATH500 | 500 | **4.1329** |
| HumanEval | 164 | **5.5121** |
| MBPP | 257 | **5.1980** |
| MT-Bench | 80 | **3.9342** |
| AIME26 | 30 | **2.9893** |
| RULER V2 1M (MK/MV/QA) | 150 (50 per partition) | **4.2553** |

RULER V2 uses the 1M input configuration. Actual prompts span
1,000,432–1,047,925 tokens; partition acc_len is 4.4658 for MK, 4.3081 for
MV, and 3.9919 for QA.

### AIME26 acc_len by output length

| Output-token bucket | Questions | Actual output range | acc_len |
|---|---:|---:|---:|
| 0–1K | 13 | 192–885 | **3.1310** |
| 1–2K | 5 | 1,359–1,828 | **2.5773** |
| 2–4K | 6 | 2,210–3,732 | **2.5632** |
| 4–8K | 4 | 5,187–7,750 | **2.7174** |
| 8–16K | 0 | — | — |
| 16–32K | 0 | — | — |
| 32K+ | 2 | 54,545–224,703 | **4.9194** |


## Serving with SGLang

[SGLang Cookbook](https://lmsysorg.mintlify.app/cookbook/autoregressive/Moonshotai/Kimi-K3#hw=b300&pdMode=unified&strategy=low-latency&spec=dspark&hicache=off) provides Kimi K3 deployment recipes.  
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

YaRN-16 is enabled in the published draft config by default with
`original_max_position_embeddings=65536` and
`max_position_embeddings=1048576`; no separate draft config override is
required.

## Training Details

- **Framework:** SpecForge online distillation, with hidden states captured from a frozen Kimi K3 target served by a live SGLang engine. Draft trained from random initialization.
- **Loss:** `0.1 CE + 0.9 L1 distillation + 1.0 confidence BCE`, decay gamma 4.0, with 512 sampled anchors per sequence and `block_size=7`.
- **Topology:** 4 nodes × 4 GB300 (16 ranks) — 2 × TP8 target replicas, DP2 sampler, FSDP16 `SHARD_GRAD_OP` on the draft, TP-batch scatter. Batch 8 per replica × 32 accumulation steps × 2 replicas = global batch 512.

