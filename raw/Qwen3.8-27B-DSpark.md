---
license: other
library_name: transformers
pipeline_tag: text-generation
base_model: RadixArk/Qwen3.8-27B-NVFP4
tags:
- speculative-decoding
- dspark
- specforge
- sglang
- qwen3.8
inference: false
---

# Qwen3.8-27B-DSpark

A DSpark speculative-decoding draft model for Qwen3.8-27B target models, trained with [SpecForge](https://github.com/sgl-project/SpecForge) and served with [SGLang](https://github.com/sgl-project/sglang).

The checkpoint has been evaluated with both [RadixArk/Qwen3.8-27B-NVFP4](https://huggingface.co/RadixArk/Qwen3.8-27B-NVFP4) and [Qwen/Qwen3.8-27B-FP8](https://huggingface.co/Qwen/Qwen3.8-27B-FP8) targets. The acceptance-length evaluation below uses the NVFP4 target. The throughput evaluation uses the FP8 target.

## Checkpoint

- Draft parameters: 1,857,358,337 (1.86B)
- Draft weight dtype: BF16
- Hidden size: 5,120
- Transformer layers: five full-attention layers
- Attention: GQA with 32 query heads and eight key/value heads
- Target auxiliary feature layers: 5, 19, 33, 47, 61
- Markov head: VanillaMarkov, rank 256
- Training target width: 16 future positions
- Serving gamma: seven draft proposals
- Target verification width: eight tokens, including the target bonus token
- Maximum position embeddings: 262,144

The serving configuration uses `block_size=7`. The separate `training_block_size=16` records the supervision width used during training.

## Acceptance length

Results cover 64,675 completed requests across 17 workloads.

| Category | Workload | Prompts | DSpark v1 | DSpark v2 |
|---|---|---:|---:|---:|
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
|---|---:|---:|---:|
| Request-count weighted, 64,675 prompts | 2.721143 | **3.428567** | **+26.00%** |
| Workload macro, 17 workloads | 3.098368 | **3.917881** | **+26.45%** |

Acceptance-length protocol:

- Runtime: SGLang v0.5.17
- Hardware and topology: four NVIDIA GB300 GPUs, DP4 × TP1
- Sampling: thinking enabled, temperature 1.0, top-p 0.95, top-k 20, seed 980406
- Generation limit: 8,192 tokens; client concurrency: 128

## Throughput

Throughput is total output tokens divided by end-to-end timed wall duration. Each speculative-decoding cell is `output tok/s (speedup over autoregressive)`.

### Concurrency 1

| Workload | Autoregressive | EAGLE | DSpark v1 | DSpark v2 |
|---|---:|---:|---:|---:|
| GSM8K | 94.2 | 179.9 (1.91×) | 238.6 (2.53×) | **297.3 (3.16×)** |
| MATH-500 | 95.0 | 174.0 (1.83×) | 214.4 (2.26×) | **280.0 (2.95×)** |
| HumanEval | 95.8 | 165.5 (1.73×) | 205.5 (2.14×) | **254.8 (2.66×)** |
| MBPP | 93.8 | 166.7 (1.78×) | 208.6 (2.22×) | **261.6 (2.79×)** |
| MT-Bench | 95.8 | 157.4 (1.64×) | 171.3 (1.79×) | **215.8 (2.25×)** |

### Concurrency 8

| Workload | Autoregressive | EAGLE | DSpark v1 | DSpark v2 |
|---|---:|---:|---:|---:|
| GSM8K | 602.7 | 1,001.1 (1.66×) | 1,183.8 (1.96×) | **1,494.0 (2.48×)** |
| MATH-500 | 635.2 | 1,071.6 (1.69×) | 1,208.2 (1.90×) | **1,575.1 (2.48×)** |
| HumanEval | 667.9 | 1,031.3 (1.54×) | 1,159.2 (1.74×) | **1,435.1 (2.15×)** |
| MBPP | 635.4 | 988.3 (1.56×) | 1,123.7 (1.77×) | **1,393.7 (2.19×)** |
| MT-Bench | 647.9 | 963.2 (1.49×) | 958.4 (1.48×) | **1,195.5 (1.85×)** |

### Concurrency 32

| Workload | Autoregressive | EAGLE | DSpark v1 | DSpark v2 |
|---|---:|---:|---:|---:|
| GSM8K | 1,298.5 | 1,969.5 (1.52×) | 1,934.2 (1.49×) | **2,268.5 (1.75×)** |
| MATH-500 | 1,764.2 | 2,353.4 (1.33×) | 2,014.2 (1.14×) | **2,545.2 (1.44×)** |
| HumanEval | 1,862.2 | 2,296.9 (1.23×) | 1,918.5 (1.03×) | **2,472.3 (1.33×)** |
| MBPP | 1,738.4 | 2,286.3 (1.32×) | 1,926.3 (1.11×) | **2,413.1 (1.39×)** |
| MT-Bench | 1,814.2 | **2,133.4 (1.18×)** | 1,593.3 (0.88×) | 1,973.0 (1.09×) |

Throughput protocol:

- EAGLE uses the target-integrated MTP head loaded as `Qwen3_5ForCausalLMMTP`, without an external draft checkpoint
- Hardware and topology: one NVIDIA H200 per workload, TP1 × DP1
- 128 prompts per cell, dataset shuffle seed 42, concurrency 1/8/32, `max_tokens=2048`, reasoning effort `xhigh`, temperature 1.0, top-p 0.95, top-k 20
- EAGLE serving: three speculative steps, top-k 1, four draft tokens, Mamba full-memory ratio 8.26, `extra_buffer` radix-cache strategy, float32 Mamba state
- DSpark serving: gamma 7, target verify width 8, one speculative step, block size 7, Mamba full-memory ratio 11.93, `extra_buffer` radix-cache strategy, float32 Mamba state
- Autoregressive and EAGLE serving used `mem-fraction-static=0.85`. DSpark used 0.80 with expandable CUDA allocation segments. Every mode retained its complete prefill and speculative-verification CUDA graph set and used `max-running-requests=48`.


## Serving with SGLang

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
|---|---:|---|
| `model.safetensors` | 3,714,723,322 | `2aff025f45823b40ebe726b9dfa40302f3512bd9a11c3a7347de32a567acd9a7` |
| `config.json` | 2,448 | `dd65fb1b01c2adea69512ff2990a79d58eb7fe2c7ea97375aa66f657a29a5bfd` |
