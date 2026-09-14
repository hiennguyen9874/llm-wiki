# Run Unsloth Dynamic NVFP4 Guide

Learn how Unsloth Dynamic NVFP4 enables fast, accurate 4-bit inference on NVIDIA Blackwell GPUs.

Unsloth Dynamic NVFP4 is a quantized model format that runs on NVIDIA Blackwell GPUs and is designed for faster, more accurate 4-bit inference. It combines NVIDIA’s native NVFP4 precision with [Unsloth Dynamic 2.0](/docs/basics/dynamic-3.0-ggufs.md) quantization to preserve model accuracy while reducing VRAM usage and increasing speed. This guide explains FP4 quantization, compares NVFP4 with other formats, and shows how to run models like [Qwen3.8](/docs/models/qwen3.8.md), [Gemma 4](/docs/models/gemma-4.md) and [Qwen3.6](/docs/models/qwen3.6.md) locally using vLLM or SGLang on RTX 5050-5090, B200, RTX PRO 6000 and more GPUs.

Dynamic NVFP4 works by selecting important layers to remain in FP8 (W8A8) or BF16 and the rest in W4A4 (not W4A16) instead of forcing every layer into FP4. This allows up to **2.5x faster inference** since W4A4 leverages Blackwell GPU's FP4 tensor cores. For all quants, we also provide FP8 KV cache calibration allowing for **2x longer context lengths**.

{% hint style="success" %}
**Aug 14:** [**Qwen3.8-27B**](/docs/models/qwen3.8.md) **is out now along with our NVFP4 quant.**

**All** [**Gemma 4**](#gemma-4) **models are now available as Unsloth Dynamic NVFP4 quants:** E2B, E4B, 12B Unified, 26B-A4B MoE, and 31B Dense.

Explore the [Unsloth Dynamic NVFP4 Collection](https://huggingface.co/collections/unsloth/nvfp4) for all our model uploads.
{% endhint %}

### Float4 vs other precisions

The trick for **faster GPUs is to lower the numerical precision of matrix multiplications**. The number of transistors needed for the matrix multiplication units is related to the **square of the mantissa**. The mantissa allows for numbers to have how many "fractional" decimals - so the more bits, the more accurate it can represent decimals. For example expressing 0.121332 is possible with more mantissa bits, whilst few mantissa bits will round it to 0.1.

{% columns %}
{% column width="50%" %}
FP32 has 23 mantissa bits, so 23^2+ 8 exponent bits = 537 space is needed. Bfloat16 has 7 mantissa bits, so 7^2 + 8 exponent = 57 space. This means bfloat16 needs around 9x less space than FP32! And when we go to float8 which has 3 mantissa bits so 3^2 + 4 exponent = 13 - this is 41x less space than FP32!

Finally float4 has 1 mantissa bit and 2 exponents so 3 space - a whopping 179x less space than FP32 - this essentially means a **GPU can do around 179x more FP4 matrix multiplication than FP32 multiplication FLOPs in the same space**!
{% endcolumn %}

{% column width="50%" %}
![](https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FJQlcQbDGgw5qbkltc7jr%2Funknown.png?alt=media\&token=75d1ec98-3fa5-4b5a-b51a-5577ac5a96ca)
{% endcolumn %}
{% endcolumns %}

### NVFP4 vs MXFP4

<div><figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FRDyKe2OmFRK0tDbrrnMb%2Fimage.png?alt=media&amp;token=affd39c0-11e9-458f-982f-181ebc327b82" alt=""><figcaption></figcaption></figure> <figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fj2COTZX8rNX5un1JeaNU%2Fimage.png?alt=media&amp;token=9b5749d8-9e0e-4f04-8022-90379e9d544c" alt=""><figcaption></figcaption></figure></div>

There is another FP4 format called MXFP4 - it's less accurate than NVFP4 due to 2 things:

1. NVFP4 uses a block size of 16 vs 32 for MXFP4 - this allows outliers to be isolated easier and scaling factors are provided for smaller subsets of weights which increases accuracy
2. A E4M3 (FP8) scale is used instead of a E8M0 (powers of 2 scaling) per block. Using a FP8 type block size looks to be much better especially for LLMs.

### Performance Analysis

Our new dynamic NVFP4 Qwen3.6 quants run \~**2.5× faster** than other NVFP4 quants, with **better performance** and comparable file sizes. Run Qwen3.6-27B NVFP4 **2.5x faster** on **24GB VRAM** and Qwen3.6-35B-A3B **1.7x faster** on **32GB VRAM**. We also added **FP8 KV cache calibration** for 2x longer context lengths! NVFP4 requires NVIDIA's Blackwell GPUs like RTX 50X, DGX Spark (see [#dgx-spark-with-nvfp4-quants](#dgx-spark-with-nvfp4-quants "mention")), B200, B300 GPUs. For older GPUs, our GGUFs work well!

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F8zM7cg0Xgo2pAlop1iPW%2F01_qwen36_combined_throughput.png?alt=media&amp;token=23131a96-4c41-42d7-aa16-5bfb21bb44a3" alt="" width="563"><figcaption></figcaption></figure>

All benchmarks use 1x B200 128 concurrency. Higher concurrency can boost 35B to 17,561 tokens / s. We also just released our new [Qwen3.8](/docs/models/qwen3.8.md) NVFP4 quants:

* [Qwen3.8-27B NVFP4](https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4) (new)

We're also releasing two 35B-A3B NVFP4 versions:

* [Qwen3.6-35B-A3B-NVFP4-Fast](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-NVFP4-Fast) which is a full W4A4 quant - 1.79x faster
* [Qwen3.6-35B-A3B-NVFP4](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-NVFP4) which is slightly bigger but more accurate and 1.56x faster

For accuracy benchmarks, we conducted MMLU-Pro, AIME 2025, GPQA for FP8, BF16, NVIDIA's NVFP4 and our NVFP4s - we show our faster quants do similarly on all:

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FFhOUUUlRBj3dafGnmvhK%2F03_qwen36_combined_accuracy(7).png?alt=media&amp;token=9178447f-d5ae-4489-9bdc-73b2b7b1631b" alt=""><figcaption></figcaption></figure>

| Qwen3.8-27B (new)                                                           |
| --------------------------------------------------------------------------- |
| [Qwen3.8-27B NVFP4](https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4) (new) |

<table><thead><tr><th width="372.5999755859375">Qwen3.6-35B-A3B</th><th>Qwen3.6-27B</th></tr></thead><tbody><tr><td><a href="https://huggingface.co/unsloth/Qwen3.6-35B-A3B-NVFP4">Qwen3.6-35B-A3B-NVFP4</a> (1.56x Faster)</td><td><a href="https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4">Qwen3.6-27B-NVFP4</a> (2.5x Faster)</td></tr><tr><td><a href="https://huggingface.co/unsloth/Qwen3.6-35B-A3B-NVFP4-Fast">Qwen3.6-35B-A3B-NVFP4-Fast</a> (1.79x Faster)</td><td></td></tr></tbody></table>

**MTP tensors are also built directly into the quants for additional speedups.** Accuracy gains come from improvements to Qwen3.6’s chat template and dataset calibration. We use our previous chat template updates to help improve coding and tool-calling consistency while reducing looping and other reported issues. Our calibration uses a mix of our dataset optimized for coding, tool-calling and chat alongside UltraChat.

For Decode speed (tokens per person), ours is 1.03x faster for 27B and 1.17x and 1.22x faster for 35B.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FR3X2O3iOBhjMS1ekX7zO%2F03_qwen36_combined_decode.png?alt=media&amp;token=a8b34056-7178-4e0d-851b-9467fa0ba2f6" alt="" width="563"><figcaption></figcaption></figure>

### Overview

Below are the hardware requirements for models which you can use including Gemma 4 and Qwen3.6. Also see the overall speed boost you will achieve:

#### Gemma 4:

| Gemma 4 variant                                                    | Required VRAM | Faster than BF16 |
| ------------------------------------------------------------------ | ------------: | ---------------: |
| [E2B](https://huggingface.co/unsloth/gemma-4-E2B-it-NVFP4)         |          7 GB |     1.12× faster |
| [E4B](https://huggingface.co/unsloth/gemma-4-E4B-it-NVFP4)         |          9 GB |     1.22× faster |
| [12B Unified](https://huggingface.co/unsloth/gemma-4-12b-it-NVFP4) |         11 GB |     1.26× faster |
| [26B A4B](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-NVFP4) |         26 GB |     1.41× faster |
| [31B](https://huggingface.co/unsloth/gemma-4-31B-it-NVFP4)         |         32 GB |     1.45× faster |

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FZw91MhTauyOZGP5HT7bl%2Fimage.png?alt=media&amp;token=ae0051a9-af39-4ef7-8ed2-9f8c1fff33fc" alt="" width="563"><figcaption></figcaption></figure>

#### Qwen3.6:

| Qwen3.6 variant                                                           | Required VRAM | Faster than other NVFP4 quants |
| ------------------------------------------------------------------------- | ------------: | -----------------------------: |
| [27B](https://huggingface.co/unsloth/Qwen3.6-27B-NVFP4)                   |         24 GB |                    2.5× faster |
| [35B A3B](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-NVFP4)           |         32 GB |                   1.56× faster |
| [35B A3B Fast](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-NVFP4-Fast) |         32 GB |                   1.79× faster |

### NVFP4 Benchmarks

NVFP4 runs 4-bit weights and matrix multiplications directly on Blackwell Tensor Cores. Our Qwen3.6 NVFP4 quants use W4A4 so they actually use the FP4 tensor cores, so they decode faster than NVIDIA's which use W4A16. We also dynamically quantize layers to retain accuracy, and we conducted MMLU-Pro, AIME 2025, GPQA for all quants including comparing to FP8 and BF16.

**Qwen3.6-27B NVFP4 Accuracy Benchmarks**

| Provider | MMLU-Pro |  GPQA | AIME 2025 |
| -------- | -------: | ----: | --------: |
| Unsloth  |    86.25 | 86.34 |     93.12 |
| NVIDIA   |    85.96 | 86.87 |     93.12 |
| FP8      |    86.11 | 86.87 |     93.75 |
| BF16     |    85.96 | 88.13 |     93.33 |

**Qwen3.6-35B-A3B NVFP4 Accuracy Benchmarks**

| Provider         | MMLU-Pro |  GPQA | AIME 2025 |
| ---------------- | -------: | ----: | --------: |
| Unsloth          |    85.85 | 86.74 |     92.29 |
| **Unsloth Fast** |    85.58 | 87.75 |     91.67 |
| NVIDIA           |    85.60 | 87.12 |     91.88 |
| FP8              |    85.75 | 86.74 |     93.12 |
| BF16             |    85.75 | 86.36 |     92.50 |

We also checked the output length of all benchmarks, and they are comparable, so the new NVFP4 quants do not think for longer which defeats the purpose of quantizing them! (Ie if it's 2x faster, but thinks 2x more, then that's useless)

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2FjG1C3y6GVWvnorRfmnIF%2Fqwen36_combined_output_length_reordered_estimated_no_footnote.png?alt=media&amp;token=2aa2d784-c082-476e-895a-4bea77385956" alt=""><figcaption></figcaption></figure>

## **Run NVFP4 Tutorials**

To run NVFP4 quants, see below for commands to run Qwen3.6-27B in [vLLM](/docs/basics/inference-and-deployment/vllm-guide.md) and [SGLang](/docs/basics/inference-and-deployment/sglang-guide.md) (you can change model name to `Qwen3.6-35-A3B-NVFP4`).&#x20;

### **vLLM Tutorial**

You can run all NVFP4 models in [vLLM](https://github.com/vllm-project/vllm). Do NOT select any MoE backend - leave vLLM to select it - for eg Marlin is 2.5x slower! See [#marlin-vs-flashinfer-vs-cutlass-vs-cute-dsl](#marlin-vs-flashinfer-vs-cutlass-vs-cute-dsl "mention")If you have a DGX Spark, see [#dgx-spark-serving](#dgx-spark-serving "mention") you must use `--moe-backend flashinfer_b12x` or you will get much slower inference.

To install vLLM in a separate venv:

{% code overflow="wrap" expandable="true" %}

```bash
uv venv unsloth-nvfp4-env --python 3.13
source unsloth-nvfp4-env/bin/activate
uv pip install "vllm>=0.25.0" "flashinfer-python>=0.6.13" "nvidia-cutlass-dsl>=4.5.2" \
    --torch-backend=auto
```

{% endcode %}

Then to serve the 35B Fast variant:

```shell
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast
```

Change `unsloth/Qwen3.6-35B-A3B-NVFP4-Fast` to the NVFP4 quant names!

To enable MTP / speculative decoding (faster decode but somewhat less throughput), use:

```bash
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast
    --speculative-config '{"method": "mtp", "num_speculative_tokens": 2}'
```

If you get Torchcodec issues, be sure to do the below then relaunch vllm.

{% code overflow="wrap" expandable="true" %}

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

{% endcode %}

### **DGX Spark Tutorial**

To ensure DGX Spark has the correct kernels (or you will get **2x SLOWER inference**), first check:

{% code overflow="wrap" expandable="true" %}

```bash
python -c "
import torch; from vllm.utils.flashinfer import has_flashinfer_b12x_gemm as g, has_flashinfer_b12x_moe as m
cap = torch.cuda.get_device_capability(); print('cap', cap, '| b12x gemm', g(), '| b12x moe', m()); assert cap[0] == 12 and g() and m(), 'b12x unavailable: serving would degrade to marlin W4A16'"
```

{% endcode %}

which should NOT error out - if it did, please update vllm or reinstall via:

{% code overflow="wrap" expandable="true" %}

```bash
uv venv unsloth-nvfp4-env --python 3.13
source unsloth-nvfp4-env/bin/activate
uv pip install "vllm>=0.25.0" "flashinfer-python>=0.6.13" "nvidia-cutlass-dsl>=4.5.2" \
    --torch-backend=auto
```

{% endcode %}

Then to serve in vLLM for DGX Spark:

{% code overflow="wrap" expandable="true" %}

```shellscript
export CUTE_DSL_ARCH=sm_121a
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast --moe-backend flashinfer_b12x
```

{% endcode %}

If you get Torchcodec issues, be sure to do the below then relaunch vllm.

{% code overflow="wrap" expandable="true" %}

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

{% endcode %}

### **SGLang Tutorial:**

You can run all NVFP4 models in [SGLang](https://github.com/sgl-project/sglang). Remember to switch out the model name for your desired model.

**Qwen3.6:**

```bash
python -m sglang.launch_server --model-path unsloth/Qwen3.6-27B-NVFP4 --speculative-algorithm NEXTN \
     --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

**Gemma 4:**

```bash
python -m sglang.launch_server --model-path unsloth/Gemma-4-31B-NVFP4 --speculative-algorithm NEXTN \
     --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

### Gemma 4 and others

Every Gemma 4 variant now has an Unsloth Dynamic NVFP4 checkpoint.

We show Gemma-4 having at most a 1.44x throughput boost on serving 128 concurrent people on 1x B200 vs BF16. Qwen3.5-122B-A10B is 1.38x faster and GLM-4.7-Flash is 1.27x faster.

<figure><img src="https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2F40mWjyryioZIww8kxH61%2F02_throughput_nvfp4_vs_bf16.png?alt=media&amp;token=330f88e8-00d4-4573-8f79-24bd9886f2f9" alt=""><figcaption></figcaption></figure>

### Marlin vs Flashinfer vs cutlass vs cute-DSL

We also found Marlin kernels to not support W4A4 well - enabling it will cause a 2.5x performance degradation - so use CUTLASS, Flashinfer-TRTLLM or Cute-DSL (auto enabled in vLLM)! Also if you have a DGX Spark, see [#dgx-spark-serving](#dgx-spark-serving "mention") you must use `--moe-backend flashinfer_b12x` or you will get 2.5x slower inference.

**So don't set any backend - vLLM auto selects the best.**

| Model           | scheme | backend             | decode tok/s | thr out tok/s |
| --------------- | ------ | ------------------- | ------------ | ------------- |
| nvidia 27B      | W4A16  | marlin (auto)       | 115.6        | 2,403         |
| unsloth 27B     | W4A4   | marlin              | 105.6        | 2,127         |
| unsloth 27B     | W4A4   | cutlass             | 113.5        | 6,681         |
| unsloth 27B     | W4A4   | flashinfer\_trtllm  | 112.6        | 6,158         |
| unsloth 27B     | W4A4   | **cute-DSL (auto)** | 125.9        | **6,863**     |
| nvidia 35B-A3B  | W4A4   | marlin (auto)       | 240.8        | 8,721         |
| unsloth 35B-A3B | W4A4   | marlin              | 215.8        | 8,619         |
| unsloth 35B-A3B | W4A4   | cutlass             | 158.3        | 11,017        |
| unsloth 35B-A3B | W4A4   | **cute-DSL (auto)** | 295.2        | **15,636**    |
