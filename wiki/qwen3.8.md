---
type: Concept
title: Qwen3.8 Local Deployment
description: Run Qwen 27B dense and 2.4T-A95B MoE Qwen3.8 models locally via Unsloth GGUF/NVFP4 with hardware, sampling, reasoning, llama.cpp, and benchmark guidance.
tags: [qwen, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning, vision, mtp, nvfp4]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T16:00:00Z }
sources:
  - id: qwen38
    resource: ../raw/unsloth/models/qwen3.8.md
    title: 'Qwen3.8 - How to Run Locally'
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
  - id: qwen38-dspark
    resource: ../raw/Qwen3.8-27B-DSpark.md
    title: Qwen3.8-27B-DSpark
  - id: dflash2
    resource: ../raw/DFlash2.md
    title: 'DFlash 2: Keep Drafting Parallel'
---

Qwen3.8 is Qwen's family with `Qwen3.8-27B` dense vision-reasoning, `Qwen3.8-2.4T-A95B` MoE (2.4T total, 95B active), and `Qwen3.8-Max`; Unsloth publishes Dynamic V3.0 GGUFs, narrow 1-bit GGUFs, and Blackwell NVFP4 quants for local llama.cpp, Unsloth Desktop, and vLLM runs[^qwen38].

## Model identity

- Family `Qwen3.8-27B`, `Qwen3.8-2.4T-A95B`, and `Qwen3.8-Max`[^qwen38].
- 27B scope: vision and reasoning, 256K context, agentic coding/vision/chat strength, runnable on 17GB RAM/VRAM setups[^qwen38].
- 2.4T-A95B scope: 2.4T-parameter MoE with 95B active; source claims rivalry with GPT-5.6 Sol[^qwen38].
- 2.4T is thinking-only, while Qwen3.8-Max is hybrid thinking[^qwen38].
- Aug 19 update: Qwen3.8-27B GGUFs use [Unsloth Dynamic V3.0](unsloth-dynamic-gguf.md) for 10% more accuracy at the same size, stated as largely outperforming others[^qwen38].
- Unsloth quant features: Developer Role support for agentic tools like Codex, MTP enabled for fast inference, and improved nested-object tool-call parsing[^qwen38].
- Hugging Face artifacts: `unsloth/Qwen3.8-27B-GGUF`, `unsloth/Qwen3.8-27B-NVFP4`, `unsloth/Qwen3.8-2.4T-A95B-GGUF`; ModelScope mirrors for the 27B GGUF and NVFP4[^qwen38].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory[^qwen38].

Qwen3.8-27B:

| 1-bit | 2-bit | 3-bit | 4-bit | 6-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- | --- |
| 7-8 GB | 9-11 GB | 12-14 GB | 16-19 GB | 23-26 GB | 31 GB | 56 GB |

- 4-bit works on 16-19GB VRAM such as RTX 5080/4090 or a 24GB RAM Mac[^qwen38].
- MTP needs about 1-2GB extra headroom[^qwen38].

Qwen3.8-2.4T-A95B[^qwen38]:

| Dynamic 1-bit XXXS | Dynamic 1-bit Standard | Dynamic 2-bit | Q8_0 | BF16 lossless |
| --- | --- | --- | --- | --- |
| 397GB | 508GB | 657GB | 2.6TB | 4.9TB |

- Full-precision 2.4T needs 4.9TB storage; 1-bit Dynamic XXXS is 397GB (91% smaller) and larger IQ1_S is 508GB[^qwen38].
- Recommended large-model path uses the 397GB `IQ1_XXXS` quant, named `Q1_0`, and needs at least 450GB RAM[^qwen38].
- Rule of thumb: RAM+VRAM should approximately equal the quant size; otherwise disk offloading still works but is much slower[^qwen38].

## Recommended settings

Qwen3.8-27B hybrid-thinking defaults with Extra High enabled by default[^qwen38]:

| Parameter | Thinking Mode | Instruct non-thinking Mode |
| --- | --- | --- |
| `temperature` | 1.0 | 0.7 |
| `top_p` | 0.95 | 0.80 |
| `top_k` | 20 | 20 |
| `min_p` | 0.0 | 0.0 |
| `presence_penalty` | 0.0 | 1.5 |
| `repetition_penalty` | 1.0 | 1.0 |

- Maximum context `262,144`, extendable to 1M via YaRN[^qwen38].

Qwen3.8-2.4T defaults[^qwen38]:

| Setting | Value |
| --- | --- |
| `temperature` | 1.0 |
| `top_p` | 0.95 |
| `top_k` | 20 |
| `min_p` | 0.0 |
| `presence_penalty` | 0.0 |
| `repetition_penalty` | 1.0 |

- Context length up to `1,010,000`[^qwen38].
- If the model fits, source reports about 20 tokens/s generation on B200s and greater than 120 tokens/s throughput[^qwen38].

## Thinking controls

- Preserve Thinking keeps the prior thinking trace in continued conversations at higher token cost with possible accuracy gain; Unsloth exposes Think and Preserved Thinking toggles[^qwen38].
- `reasoning_effort` levels: `xhigh` default for complex thorough analysis, `medium` for accuracy/speed balance, `low` for efficient reasoning, and none; toggles are automatically enabled in Unsloth[^qwen38].
- Change effort in `unsloth run` or `llama-server`[^qwen38]:

```bash
--chat-template-kwargs '{"reasoning_effort":"medium"}'
```

- Windows PowerShell form[^qwen38]:

```bash
--chat-template-kwargs "{\"reasoning_effort\":\"medium\"}"
```

- Example Unsloth serve with reasoning effort[^qwen38]:

```bash
unsloth run --model unsloth/qwen3.8-27B-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.0 \
    --reasoning-effort medium
```

## New 1-bit data types for 2.4T

- Unsloth extended `IQ1_S` at 1.5625 bits per weight down to 1.1875 bpw by reducing codebook entries; reported as working well for large models and fine for PTQ without QAT/QAD[^qwen38].
- HF naming uses `TQ2_0`, `TQ1_0`, and `Q1_0` for the new types because of naming issues; otherwise files would not appear in the HF repo[^qwen38].

| Dtype | Naming | BPW | Entries | Index bits | Block |
| --- | --- | --- | --- | --- | --- |
| IQ1_S | IQ1_S | 1.5625 | 2048 | 11 | 50 B |
| UD-IQ1_XS | TQ2_0 | 1.4375 | 1024 | 10 | 46 B |
| UD-IQ1_XXS | TQ1_0 | 1.3125 | 512 | 9 | 42 B |
| UD-IQ1_XXXS | Q1_0 | 1.1875 | 256 | 8 | 38 B |

Reported figures for other large models, not yet final Qwen3.8-2.4T benchmarks[^qwen38]:

| Dtype | GiB | PPL | KLD | top-p |
| --- | --- | --- | --- | --- |
| IQ1_S | 553.204 | 2.578876 | 0.564553 | 78.882 |
| UD-IQ1_XS | 513.583 | 2.931261 | 0.690161 | 75.726 |
| UD-IQ1_XXS | 473.961 | 3.540383 | 0.876007 | 71.284 |
| UD-IQ1_XXXS | 434.340 | 4.488796 | 1.109944 | 66.257 |

## Local run paths

- Unsloth Desktop is the easiest path on macOS, Windows, and Linux with automatic RAM offload and multi-GPU detection, GGUF/MLX/safetensor search and download, self-healing tool calling, web search, Python/Bash execution, auto-tuned inference parameters, and training support[^qwen38].
- Install on macOS/Linux/WSL with `curl -fsSL https://unsloth.ai/install.sh | sh`, or on Windows PowerShell with `irm https://unsloth.ai/install.ps1 | iex`; in Chat or Model hub search for Qwen3.8, download the chosen quant, and run with auto-set parameters while retaining manual control of context, template, and thinking settings[^qwen38].
- Serve via Unsloth API with `llama-server` runtime flags for context, GPU layers, threading, sampling, networking, and tools; see API and `unsloth start` docs linked in source[^qwen38].

llama.cpp for narrow 1-bit `IQ1_XXXS` needs the Unsloth branch; use `-DGGML_CUDA=OFF` for CPU-only and Apple Mac/Metal where Metal is default[^qwen38]:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone --branch iq1-narrow https://github.com/unslothai/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

Standard `IQ1_S` and other quants use normal llama.cpp[^qwen38]:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

Download after `pip install -U "huggingface_hub[cli]"`; see source Hugging Face Hub XET debugging page if stuck[^qwen38]:

```bash
hf download unsloth/Qwen3.8-27B-GGUF \
    --local-dir unsloth/Qwen3.8-27B-GGUF \
    --include "*UD-Q4_K_XL*" # Use "*UD-Q3_K_XL*" for 3-bit
```

```bash
hf download unsloth/Qwen3.8-2.4T-A95B-GGUF \
    --local-dir unsloth/Qwen3.8-2.4T-A95B-GGUF \
    --include "*Q1_0*" # Use "*IQ2_XXS*" for 2-bit
```

Run examples with source sampling settings[^qwen38]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.8-27B-GGUF/Qwen3.8-27B-UD-Q4_K_XL.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.0
```

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.8-2.4T-A95B-GGUF/UD-Q1_0/Qwen3.8-2.4T-A95B-UD-Q1_0-00001-of-00010.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.0
```

General `UD-IQ1_S` download and run[^qwen38]:

```bash
hf download unsloth/Qwen3.8-2.4T-A95B-GGUF \
    --local-dir unsloth/Qwen3.8-2.4T-A95B-GGFF \
    --include "*IQ1_S*" # Use "*IQ2_XXS*" for 2-bit
```

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.8-2.4T-A95B-GGUF/UD-IQ1_S/Qwen3.8-2.4T-A95B-UD-IQ1_S-00001-of-00012.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.0
```

## NVFP4 faster inference

- Dynamic NVFP4 Qwen3.8-27B runs about 1.5x faster than BF16 with better performance and comparable file size; source reports 1.5x faster 27B on 24GB VRAM plus FP8 KV-cache calibration for 2x longer context[^qwen38].
- Requires Blackwell GPUs such as RTX 50-series, DGX Spark, B200/B300; older GPUs should use GGUFs[^qwen38].

Reported B200 throughput, total and per-user tok/s[^qwen38]:

| batch | BF16 total tok/s | NVFP4 total tok/s | speedup | BF16 per-user | NVFP4 per-user |
| --- | --- | --- | --- | --- | --- |
| 1 | 89.8 | 133.7 | 1.49x | 89.8 | 133.7 |
| 8 | 649.4 | 938.8 | 1.45x | 81.2 | 117.3 |
| 32 | 1983.0 | 2787.0 | 1.41x | 62.0 | 87.1 |
| 64 | 3048.5 | 4407.2 | 1.45x | 47.6 | 68.9 |

- All benchmarks use 1x B200 at 128 concurrency; higher concurrency is claimed to boost 35B to 17,561 tokens/s, preserved as written even though this page covers 27B/2.4T[^qwen38].
- NVFP4 accuracy recovery is 92-97% top-1 agreement versus BF16[^qwen38]:

| corpus | KLD mean | top-1 agreement |
| --- | --- | --- |
| zh | 0.01628 | 93.55% |
| code | 0.02600 | 96.68% |
| refgen | 0.03993 | 94.46% |
| chat | 0.05818 | 92.15% |
| ja / ko / ru / es | 0.0124-0.0155 | 94-95% |

- For Qwen3.6, source compares FP8, BF16, NVIDIA NVFP4, and Unsloth NVFP4 on MMLU-Pro, AIME 2025, and GPQA and presents Unsloth as similar; Qwen3.6 figures are not Qwen3.8 evidence[^qwen38].
- vLLM install and 27B serve[^qwen38]:

```bash
uv venv unsloth-nvfp4-env --python 3.13
source unsloth-nvfp4-env/bin/activate
uv pip install "vllm>=0.25.0" "flashinfer-python>=0.6.13" "nvidia-cutlass-dsl>=4.5.2" \
    --torch-backend=auto
```

```bash
vllm serve unsloth/Qwen3.8-27B-NVFP4
```

```bash
vllm serve unsloth/Qwen3.8-27B-NVFP4 \
    --speculative-config '{"method": "mtp", "num_speculative_tokens": 2}'
```

- Torchcodec failure workaround is installing `ffmpeg` then relaunching vLLM[^qwen38]:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

- SGLang path requires version v0.5.19 because the lm_head is quantized to FP8; source elsewhere says SGLang is not supported, so treat v0.5.19 as the newer exception rather than general SGLang support[^qwen38]:

```bash
uv pip install sglang sglang-kernel \
  --extra-index-url https://sgl-project.github.io/whl/cu130/ \
  --extra-index-url https://download.pytorch.org/whl/cu130 \
  --index-strategy unsafe-best-match
```

```bash
sglang serve unsloth/Qwen3.8-27B-NVFP4
```

```bash
sglang serve unsloth/Qwen3.8-27B-NVFP4 --speculative-algorithm EAGLE \
    --speculative-num-steps 3 --speculative-eagle-topk 1  --speculative-num-draft-tokens 4
```

## Source-reported benchmarks

All figures are source-reported Unsloth claims[^qwen38].

Qwen3.8-27B text table versus Qwen3.6-27B, Qwen3.7-Plus, Muse Glimmer-30B, and Opus4.6 Max[^qwen38]:

| Benchmark | Qwen3.8-27B | Qwen3.6-27B | Qwen3.7-Plus | Muse Glimmer-30B | Opus4.6 Max |
| --- | --- | --- | --- | --- | --- |
| Terminal Bench 2.1 Terminus | 73.0 | 63.4 | 64.0 | 51.7 | 78.2 |
| SWE-bench Pro | 61.7 | 53.5 | 57.6 | 51.2 | 53.4 |
| NL2Repo-Bench | 42.3 | 36.2 | 41.1 | -- | 47.6 |
| DeepSWE 1.1 | 42.2 | 13.3 | 14.2 | -- | -- |
| QwenSWEBench | 79.0 | 49.3 | 59.2 | -- | 63.8 |
| CoWorkBench | 70.7 | 61.0 | 65.1 | -- | 68.2 |
| JobBench | 33.4 | 21.8 | 27.6 | -- | -- |
| Agents Last Exam Pass@1 / Score | 20.4 / 42.9 | 10.6 / 27.3 | 13.2 / 33.6 | -- | -- |
| IFBench | 79.5 | 69.1 | 79.1 | 77.0 | 62.5 |
| GPQA Diamond | 89.2 | 87.8 | 90.3 | 83.5 | 91.3 |
| HLE | 30.8 | 24.0 | 34.7 | 22.0 | 40.0 |
| LiveCodeBench v6 | 90.3 | 83.9 | 89.6 | -- | 88.8 |

- Qwen3.8-2.4T-A95B benchmark image is included in the source but was not independently inspected here[^qwen38].
- GGUF quantization detail points to the Dynamic V3.0 analysis and the top-1%/KLD plots in the source[^qwen38].

## Relationships

- Related to [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — day-zero `incoai/Qwen3.8-27B-DFlash2` drafter reports 4.80 mean acceptance (block 8, default sampling) versus 4.28 MTP and 3.62 community DSpark, with 2.7–3.4× autoregressive throughput at batch size 1 in SGLang[^dflash2].

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — Qwen3.8-27B Dynamic V3.0 GGUFs and 2.4T narrow 1-bit `TQ`/`Q1_0` types as instances of Unsloth per-layer dynamic PTQ without QAT/QAD.
- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — Blackwell W4A4 path, FP8 KV-cache calibration, and vLLM/SGLang serving context for the Qwen3.8-27B NVFP4 checkpoint named here.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — MTP-enabled local inference with 1-2GB extra-memory planning and vLLM MTP speculative serving shared with Qwen3.6 and Gemma 4 runs.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — PPL, KLD, and top-1/top-p agreement figures used here are the same fidelity signals used to judge quantized models.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — prior Qwen hybrid-thinking local family with the same thinking/instruct sampling split, preserve-thinking pattern, and NVFP4/MTP serving shape.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — sibling Qwen3.8 local family on Qwen4 MoE architecture with shared thinking controls and Dynamic GGUF packaging.
- Related to [Muse Glimmer Local Deployment](muse-glimmer.md) — appears as a comparison point in the Qwen3.8-27B benchmark table.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — datacenter-scale Day-0 SGLang/Miles serving for the same 2.4T-A95B identity with GDN three-state caching, chunked PP prefill, PD staging buffer, fused kernels, and colocated LoRA RL[^qwen38-day0].
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — server-side SGLang speculative-decoding path for the 27B dense base with block-size-7 drafting and v1/v2 acceptance plus throughput comparisons[^qwen38-dspark].

## Contradictions

- SGLang support: one passage says NVFP4 quants run in vLLM only for now and SGLang is not supported, while the later SGLang section gives a v0.5.19 serve path; preserved without choosing one because the source contains both statements[^qwen38].

## Coverage limits

- Remote images, accuracy/KLD plots, throughput charts, GIF demonstrations, Hugging Face and ModelScope files, and linked Unsloth Desktop, llama.cpp, MTP, Dynamic 3.0, NVFP4, API, troubleshooting, and fine-tuning pages were not independently inspected; benchmark, tok/s, and hardware claims are source-reported Unsloth claims, not independently verified.
- The `*IQ2_XXS*` 2-bit note is preserved for the 2.4T download even though the surrounding include pattern uses `*Q1_0*`; the `UD-IQ1_S` download example writes `GGFF` in the local-dir value and is preserved as written.
- The 17,561 tokens/s higher-concurrency row names 35B in a 27B/2.4T page and is preserved as written without reassignment.
- No local attachments were referenced by the source.

[^qwen38]: Qwen3.8 - How to Run Locally — `../raw/unsloth/models/qwen3.8.md`, Qwen3.8-27B/2.4T-A95B/Max identity with 256K and 1.01M context claims, 27B 7-56GB and 2.4T 397GB-4.9TB hardware tables, thinking/instruct sampling and preserve-thinking plus reasoning-effort controls, narrow 1-bit BPW/codebook table with large-model PPL/KLD figures, Unsloth Desktop and llama.cpp iq1-narrow/standard install/download/run commands, NVFP4 throughput/accuracy tables with vLLM and SGLang v0.5.19 commands, and 27B text benchmark table plus 2.4T image note.
[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering datacenter-scale 2.4T-A95B serving with three-state caching, chunked PP prefill, PD staging buffer, fused kernels, and colocated LoRA RL.
[^qwen38-dspark]: Qwen3.8-27B-DSpark — `../raw/Qwen3.8-27B-DSpark.md`.
[^dflash2]: DFlash 2: Keep Drafting Parallel — `../raw/DFlash2.md`.
