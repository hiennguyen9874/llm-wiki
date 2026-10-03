# openjev qwen3.5-4b-nli-v5 — NVFP4

NVFP4 (W4A4, FP8 block scales, group 16) version of [`qwen3.5-4b-nli-v5`](../qwen3.5-4b-nli-v5), made with
[NVIDIA Model-Optimizer](https://github.com/NVIDIA/Model-Optimizer) 0.47 and exported with `export_hf_checkpoint`
(`quant_method: modelopt`). The 3-way `score` head, embeddings, vision tower and the GDN `in_proj_a/b` / `conv1d`
stay in bf16. Size 3.95 GB vs 9.1 GB for bf16. Same template and label order as the bf16 model:
`"Premise: {premise}\nHypothesis: {hypothesis}"` -> `[contradiction, entailment, neutral]`.

## How it was made
1. PTQ: `mtq.quantize` with `NVFP4_DEFAULT_CFG` (+ `score` excluded), max calibration on 512 rows of the v5 training mix.
2. QAD (quantization-aware distillation, the Model-Optimizer `llm_qat` recipe adapted to a seq-cls head): the NVFP4
   student is trained on 30k v5-mix rows with KL(teacher || student) over the 3 logits, teacher = the bf16 v5 model;
   lr 1e-5 cosine, bs 16, 1 epoch, scales frozen. ~40 min on one RTX PRO 6000.
3. Export to packed NVFP4.

## Accuracy
Served with SGLang on real FP4 kernels (RTX PRO 6000 Blackwell), same server flags for all rows:

| task | bf16 | fp8 (on the fly) | **NVFP4 (this)** |
|---|---|---|---|
| MNLI m+mm | 0.898 | 0.898 | 0.894 |
| ANLI r1 / r2 / r3 | 0.782 / 0.665 / 0.626 | 0.776 / 0.664 / 0.629 | 0.771 / 0.675 / 0.618 |
| WANLI | 0.766 | 0.768 | 0.761 |
| SciTail | 0.952 | 0.952 | 0.948 |
| ConTRoL | 0.735 | 0.735 | 0.722 |

Plain PTQ without QAD loses up to 4 points on the hard sets (ANLI r3 0.585, ConTRoL 0.698); QAD recovers most of it.

## Speed
SGLang 0.5.18, one RTX PRO 6000 Blackwell, `--chunked-prefill-size 16384 --max-prefill-tokens 65536 --disable-radix-cache`,
saturated throughput on random token ids (tok/s):

| input length | bf16 | fp8 | **NVFP4** |
|---|---|---|---|
| 64 | 36.1k | 48.9k | **64.3k** |
| 256 | 37.7k | 51.3k | **68.8k** |
| 1024 | 37.5k | 51.4k | **69.0k** |
| 4096 | 36.0k | 48.5k | **63.9k** |
| 16384 | 30.7k | 39.2k | **48.7k** |

p50 latency of a single request at 4k / 16k tokens: bf16 119 / 547 ms, fp8 86 / 434 ms, NVFP4 67 / 351 ms.
Raw numbers: `bench/`.

## Serving
Needs a Blackwell GPU (sm100 / sm120). With SGLang and the openjev external model package (`code/sglang_openjev`):

```bash
SGLANG_EXTERNAL_MODEL_PACKAGE=sglang_openjev python -m sglang.launch_server --model-path qwen3.5-4b-nli-v5-nvfp4 \
  --is-embedding --json-model-override-args '{"architectures": ["Qwen3_5ForConditionalGeneration"]}' \
  --attention-backend triton
```

SGLang picks up `modelopt_fp4` from `hf_quant_config.json`. flashinfer JIT-compiles the FP4 activation-quantize kernel on
first start, so `CUDA_HOME` must point to a CUDA toolkit whose nvcc matches its headers (13.0 worked).
