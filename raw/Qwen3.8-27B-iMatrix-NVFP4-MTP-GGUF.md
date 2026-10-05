---
license: apache-2.0
base_model: Qwen/Qwen3.8-27B
base_model_relation: quantized
pipeline_tag: image-text-to-text
tags:
  - gguf
  - qwen
  - qwen3.8
  - nvfp4
  - imatrix
  - mtp
  - llama.cpp
  - multimodal
  - 256k-context
---

# Qwen3.8-27B iMatrix NVFP4 MTP GGUF

I built this quant because the ready-made FP4 file answered the wrong question. It was fast, but on my short WikiText-2 control it scored 6.4949 PPL. Plain Q4_0 scored 6.3798. The first higher-quality hybrid went too far the other way: good perplexity, 34.19 tok/s, and no comfortable room for 256K plus vision.

This is the build that survived both gates.

It is a 17.1 GB, 5.01 BPW mixed-precision GGUF of [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B). It keeps large, tolerant matrices in native NVFP4 and spends more bits on selected attention, Gated DeltaNet, and late FFN tensors. The trained MTP layer remains embedded in the same GGUF.

This is not a fine-tune. I built the private calibration workload from 5,472 messages across 296 real sessions in my Hermes agent setup. The 153,600 processed tokens covered coding, infrastructure work, tool calls, and mixed Polish-English conversation. I used `llama-imatrix` to rank tensor sensitivity; the corpus and raw importance matrix are not distributed or embedded in the model.

The complete experiment, including the builds that lost, is here: [Qwen3.8 27B at 256K: 50 TPS on a 24 GB GPU](https://piszczek.pl/blog/qwen38-27b-256k-50-tps-24gb-gpu).

## Files

| File | Bytes | Purpose |
|---|---:|---|
| `Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf` | 17,125,207,136 | Target model and one embedded MTP layer |
| `mmproj-Qwen3.8-27B-F16.gguf` | 927,607,488 | Optional vision projector, unchanged from the upstream conversion |
| `recipe/tensor-types.txt` | small | Tensor overrides used for the final hybrid |
| `SHA256SUMS` | small | Release checksums |

The checksum was generated after public metadata replaced the private build metadata.

## Quant recipe

The base file is mostly NVFP4. These parts are protected:

- all Q, K, V, and output matrices in the 16 full-attention layers: Q5_K;
- selected high-importance DeltaNet QKV, gate, and output matrices: Q5_K;
- late FFN down projections in layers 54, 57-63: Q6_K;
- matching late FFN gate and up projections: Q5_K;
- token embeddings: Q6_K;
- output head: Q8_0;
- embedded MTP weights: NVFP4.

The exact regular expressions are in [`recipe/tensor-types.txt`](recipe/tensor-types.txt). I used the importance matrix to choose where precision was worth its VRAM and kernel cost. NVFP4 block quantization itself does not consume the matrix.

The resulting short-control PPL was 6.1197. Q4_1 scored 6.1127 on the same sample. That 0.11% gap is smaller than the error of this short check, so I treat them as tied rather than claim a quality win.

## Measured results

Hardware:

- GPU0: [NVIDIA RTX PRO 4000 Blackwell SFF Edition](https://www.nvidia.com/en-eu/products/workstations/professional-desktop-gpus/rtx-pro-4000-sff/), 24 GB GDDR7 ECC, 192-bit memory interface, 432 GB/s rated memory bandwidth, 70 W maximum board power, 24,467 MiB reported capacity, sm120a;
- GPU1, optional and used only for vision in this profile: NVIDIA RTX 2000 Ada, 15,996 MiB, sm89;
- Debian 13, CUDA 12.9.86, GCC 14.2;
- main model, MTP, recurrent state, CUDA graphs, and target KV on GPU0;
- optional F16 vision projector on GPU1.

All throughput rows below were measured on GPU0. The 70 W figure is NVIDIA's board-power limit, not a power reading captured during these runs. I did not measure energy at the wall, so this release makes no tokens-per-joule claim.

| Test | Result |
|---|---:|
| Production series, 10 runs | 50.441 tok/s mean, 49.420-51.397 |
| Clean llama.cpp b10454 | 45.422 tok/s |
| Measured custom runtime on RTX PRO 4000 Blackwell SFF | 55.402 tok/s, +21.97% |
| Target-only greedy | 21.189 tok/s |
| Embedded MTP | 59.456 tok/s, 2.81x target-only |
| Real context fill | 261,500 input tokens + 256 generated |
| Full-cache prefill | 226.750 tok/s |
| Full-cache decode | 12.606 tok/s |
| GPU0 after full fill | 23,952 / 24,467 MiB |
| GPU1 projector, optional vision path | 982 MiB |

These are separate measurements. The 55.402 tok/s runtime A/B is not the same run as the 50.441 tok/s production series. I am keeping the rows separate because multiplying unrelated best cases produces a nice number and a useless benchmark.

The 256K result is an occupied-cache measurement. The server ingested 261,500 tokens, generated another 256, did not truncate, and did not OOM. Merely allocating a 262,144-token slot is much easier.

## The llama.cpp branch behind 55.402 tok/s

I locally merged six pinned pull-request heads into the runtime used for the custom-build measurement. I did not write these patches, and none had been merged into upstream llama.cpp when I prepared this release on 18 August 2026.

| Pull request | Author | What it changed in this setup |
|---|---|---|
| [#26001](https://github.com/ggml-org/llama.cpp/pull/26001) | BLSharda | Chunked CUDA kernel for Gated DeltaNet prefill |
| [#26048](https://github.com/ggml-org/llama.cpp/pull/26048) | kmorennv | Fused NVFP4 scale handling in the MMQ epilogue |
| [#26705](https://github.com/ggml-org/llama.cpp/pull/26705) | praneshgo | Branchless Q4_K/Q5_K CUDA path used during speculative verification |
| [#27173](https://github.com/ggml-org/llama.cpp/pull/27173) | PatrickWalther | Chained MTP verification and token rollback fix |
| [#24891](https://github.com/ggml-org/llama.cpp/pull/24891) | hakuhan | Correct recurrent-checkpoint invalidation after tool requests |
| [#25635](https://github.com/ggml-org/llama.cpp/pull/25635) | ynankani | XOR-swizzled Flash Attention K/V tiles |

The first three patches moved the controlled run from 45.422 to 45.866 tok/s. Adding #27173 reached 55.402 tok/s. Patch #25635 separately moved 32K prefill from 759.38 to 815.64 tok/s and hot decode from 37.26 to 38.23 tok/s. Patch #24891 is a correctness fix for long agent sessions, not a speed claim.

The exact heads are pinned in [`recipe/llama.cpp-patches.md`](recipe/llama.cpp-patches.md). Treat that file as a benchmark manifest. Check current upstream before building; an open PR can move or become obsolete.

## Run it on current llama.cpp

Use a recent llama.cpp with Qwen3.8, NVFP4, Gated DeltaNet, multimodal, and MTP support. The model was checked against clean upstream build 10454, commit `4df29be4f`. Newer compatible builds should work, but record the commit when comparing performance.

For text-only use, download the main GGUF. Add the projector only if you need image input:

```bash
hf download cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF \
  Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf \
  mmproj-Qwen3.8-27B-F16.gguf \
  --local-dir ./qwen38
```

A conservative text and vision profile:

```bash
CUDA_VISIBLE_DEVICES=0,1 \
MTMD_BACKEND_DEVICE=CUDA1 \
llama-server \
  --model ./qwen38/Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf \
  --mmproj ./qwen38/mmproj-Qwen3.8-27B-F16.gguf \
  --device CUDA0 \
  --n-gpu-layers 999 \
  --ctx-size 262144 \
  --parallel 1 \
  --ctx-checkpoints 4 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --temp 0.6 \
  --spec-type draft-mtp \
  --spec-draft-n-max 1 \
  --spec-draft-backend-sampling \
  --reasoning-preserve \
  --jinja
```

`n_max=1` is the safer starting point when output equivalence matters. It leaves performance on the table.

## The measured max-throughput profile

This is the configuration behind the production measurements:

```bash
export CUDA_VISIBLE_DEVICES=0,1
export MTMD_BACKEND_DEVICE=CUDA1
export LLAMA_SPEC_CHAIN=1
export GGML_CUDA_GRAPH_OPT=1

llama-server \
  --model ./qwen38/Qwen3.8-27B-iMatrix-NVFP4-MTP.gguf \
  --alias Qwen3.8-27B-iMatrix-NVFP4-256K-MTP \
  --device CUDA0 \
  --n-gpu-layers 999 \
  --fit off \
  --ctx-size 262144 \
  --parallel 1 \
  --ctx-checkpoints 4 \
  --flash-attn on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --batch-size 512 \
  --ubatch-size 256 \
  --threads 8 \
  --threads-batch 8 \
  --temp 0.6 \
  --spec-type draft-mtp \
  --spec-default \
  --spec-draft-n-max 8 \
  --spec-draft-n-min 0 \
  --spec-draft-p-min 0 \
  --spec-draft-type-k f16 \
  --spec-draft-type-v f16 \
  --spec-draft-threads 8 \
  --spec-draft-threads-batch 8 \
  --spec-draft-backend-sampling \
  --mmproj ./qwen38/mmproj-Qwen3.8-27B-F16.gguf \
  --image-min-tokens 1024 \
  --reasoning-preserve \
  --jinja \
  --metrics
```

`--fit off` is intentional. Automatic fitting can silently reduce context or change placement to keep its own safety margin, which makes a capacity result hard to interpret. Do not copy this choice blindly. Confirm the allocation on your card.

The full profile uses a second GPU for the projector. For text-only use, omit `--mmproj` and `MTMD_BACKEND_DEVICE`. Putting the F16 projector on the same 24 GB card as the full 256K allocation is likely to cross the measured memory limit.

Those runtime patches do not change the model file or its clean-upstream compatibility.

## Why MTP stops at eight

On this model and GPU, `n_max=8` hit a favorable verification shape. Nine candidates were no faster and cost about 150 MiB more. Ten crossed another CUDA allocation boundary. At 20, throughput fell to 30.60 tok/s.

The MTP head also preferred the lower-precision match. Requantizing only its eight weight tensors to iMatrix Q5_K added 50.625 MiB and reduced the ten-run mean from 50.441 to 48.733 tok/s. A Q5_K/Q6_K version added 69.219 MiB and fell to 37.024 tok/s. More accurate standalone draft weights agreed less often with this quantized target.

## Known limitation: batch invariance

Target-only greedy decoding and MTP `n_max=8` do not produce the same continuation on this quantized target. Both paths were deterministic inside their own configurations, but the max-throughput mode is not bitwise distribution-preserving relative to target-only decode. This matches the open llama.cpp [batch-invariance issue #25618](https://github.com/ggml-org/llama.cpp/issues/25618).

Use `n_max=1` if that property matters more than throughput. Do not report the `n_max=8` result as lossless speculative decoding.

Performance also depends heavily on workload and cache position. Agentic code with repeated schemas and prefixes can accept drafts well. A fresh request at the far end of 256K is a different machine, despite using the same weights.

## Provenance and license

- Base model: [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B).
- Conversion starting point and unchanged F16 projector: [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF).
- Runtime: [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).
- Quant and benchmarks: [Michał Piszczek](https://piszczek.pl/michal-piszczek).

The base model and this quantized derivative use the Apache License 2.0. Keep the original attribution and license when redistributing the weights.
