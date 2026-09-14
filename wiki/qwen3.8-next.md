---
type: Concept
title: Qwen3.8-Flash-Next Local Deployment
description: Run Qwen 125B MoE multimodal Qwen3.8-Flash-Next locally via Unsloth GGUFs with hardware, sampling, reasoning, MTP, and benchmark guidance.
tags: [qwen, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning, mtp, moe]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T17:00:00Z }
sources:
  - id: qwen38-next
    resource: ../raw/unsloth/models/qwen3.8-next.md
    title: 'Qwen3.8-Flash-Next: How to Run Locally'
---

Qwen3.8-Flash-Next is Qwen's 125B-parameter MoE multimodal model on the Qwen4 architecture with 262K context and hybrid thinking; Unsloth publishes 1-bit to 8-bit GGUFs plus shared MTP modules for local llama.cpp and Unsloth Desktop runs starting at 75 GB total memory[^qwen38-next].

## Model identity

- Name `Qwen3.8-Flash-Next`; open-weight 125B-parameter MoE multimodal model from Qwen on Qwen4 architecture[^qwen38-next].
- Reported scope: 262K context window, advanced reasoning, and source claim of outperforming Claude-4.6-Opus (Max)[^qwen38-next].
- Source positions it as runnable locally with 75 GB RAM/unified memory and no GPU VRAM required[^qwen38-next].
- Hugging Face artifact: `unsloth/Qwen3.8-Flash-Next-GGUF`; ModelScope mirror: `unsloth/Qwen3.8-Flash-Next-GGUF`[^qwen38-next].
- Unique inference note: CPU system RAM versus GPU VRAM is said to matter relatively little because RAM/unified-memory performance is closer to VRAM than is typical; presented as well suited to Macs, NVIDIA DGX Spark systems, and other large-memory devices[^qwen38-next].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory[^qwen38-next]:

| 1-bit | 2-bit | 3-bit | 4-bit | 5-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- | --- |
| 75 GB | 79 GB | 90 GB | 96-114 GB | 163 GB | 200 GB | 355 GB |

- Smallest 1-bit quant works on 75 GB RAM, so source recommends a 96 GB RAM/unified-memory device as the practical starting point[^qwen38-next].
- 1-bit GGUF is 75 GB and keeps Ngram/PLE layers at 4-bit; stated as 79% smaller than 355 GB BF16 while retaining 80% top-1% accuracy[^qwen38-next].
- 1-bit footprint is larger than usual because new Ngram layers or per-layer embeddings act like a lookup table; lighter quantization there is said to preserve accuracy[^qwen38-next].
- PLE/Ngram layers can be offloaded to SSD with mmap to reduce CPU and GPU VRAM use[^qwen38-next].
- MTP needs about 1-2 GB extra headroom[^qwen38-next].

MTP hardware table, same total-memory units[^qwen38-next]:

| 1-bit | 2-bit | 3-bit | 4-bit | 5-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- | --- |
| 76 GB | 80 GB | 91 GB | 97-115 GB | 164 GB | 200 GB | 355 GB |

- Source notes 3-bit MTP works on 91 GB RAM, so a 96 GB device is again the practical recommendation[^qwen38-next].

## Recommended settings

Hybrid-thinking defaults with Extra High thinking enabled by default[^qwen38-next]:

| Parameter | Thinking Mode | Instruct non-thinking Mode |
| --- | --- | --- |
| `temperature` | 1.0 | 0.7 |
| `top_p` | 0.95 | 0.80 |
| `top_k` | 20 | 20 |
| `min_p` | 0.0 | 0.0 |
| `presence_penalty` | 0.0 | 1.5 |
| `repetition_penalty` | 1.0 | 1.0 |

- Maximum context length `262,144`[^qwen38-next].

## Thinking controls

- Preserve Thinking keeps the prior thinking trace in continued conversations at higher token cost with possible accuracy gain; Unsloth Desktop exposes Think and Preserved Thinking toggles[^qwen38-next].
- `reasoning_effort` levels: `xhigh` default for complex thorough analysis, `medium` for accuracy/speed balance, `low` for efficient reasoning, and none[^qwen38-next].
- Change effort in `unsloth run` or `llama-server`[^qwen38-next]:

```bash
--chat-template-kwargs '{"reasoning_effort":"medium"}'
```

- Windows PowerShell form[^qwen38-next]:

```bash
--chat-template-kwargs "{\"reasoning_effort\":\"medium\"}"
```

## Quantization packaging

- New architecture uses PLE/Ngrams with random access patterns; source keeps them at minimum 4-bit because heavier quantization would damage the model[^qwen38-next].
- Source claims 80% top-1% accuracy recovery with 79% less disk usage[^qwen38-next].

Reported GGUF size and fidelity table[^qwen38-next]:

| Quant | GB | Top-1 % | Mean KLD | 99.9% KLD |
| --- | --- | --- | --- | --- |
| UD-IQ1_S | 72.5 | 77.325 | 0.396070 | 7.2126 |
| UD-IQ1_M | 74.5 | 79.691 | 0.314739 | 6.1965 |
| UD-Q2_K_XL | 78.9 | 82.715 | 0.224607 | 4.9121 |
| UD-IQ3_XXS | 82.0 | 85.414 | 0.165120 | 4.0375 |
| UD-Q3_K_XL | 90.0 | 88.315 | 0.106504 | 3.0538 |
| UD-IQ4_XS | 93.7 | 89.554 | 0.083630 | 2.3677 |
| UD-Q4_K_XL | 111.3 | 92.255 | 0.046893 | 1.5468 |
| UD-Q5_K_XL | 158.3 | 93.680 | 0.030415 | 1.0036 |
| UD-Q6_K_XL | 169.2 | 94.089 | 0.027091 | 0.8416 |
| Q8_0 | 188.2 | 94.122 | 0.026574 | 0.8118 |

## Local run paths

- Unsloth Desktop is the easiest path on macOS, Windows, and Linux with automatic RAM offload and multi-GPU detection, GGUF/MLX/safetensor search and download, self-healing tool calling, web search, Python/Bash execution, auto-tuned inference parameters, and training support[^qwen38-next].
- Install on macOS/Linux/WSL with `curl -fsSL https://unsloth.ai/install.sh | sh`, or on Windows PowerShell with `irm https://unsloth.ai/install.ps1 | iex`; in Chat or Model hub search for Qwen3.8-Flash, download the chosen quant, and run with auto-set parameters while retaining manual control of context, template, and MTP settings[^qwen38-next].
- MTP is automatically enabled in Unsloth Desktop but can be disabled; inference parameters should auto-set but remain manually editable[^qwen38-next].
- Serve via Unsloth API with `llama-server` runtime flags for context, GPU layers, threading, sampling, networking, and tools; example uses Dynamic 4-bit[^qwen38-next]:

```bash
unsloth run --model unsloth/Qwen3.8-Flash-Next-GGUF:UD-Q4_K_XL
```

- Standard llama.cpp build from `https://github.com/ggml-org/llama.cpp`; use `-DGGML_CUDA=OFF` for CPU-only and Apple Mac/Metal where Metal is default; build `llama-cli llama-mtmd-cli llama-server llama-gguf-split`[^qwen38-next]:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

- Download after `pip install -U "huggingface_hub[cli]"`; source notes `*IQ2_XXS*` for 2-bit[^qwen38-next]:

```bash
hf download unsloth/Qwen3.8-Flash-Next-GGUF \
    --local-dir unsloth/Qwen3.8-Flash-Next-GGUF \
    --include "*UD-Q4_K_XL*"
```

- Source run example[^qwen38-next]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.8-Flash-Next-GGUF/UD-IQ1_S/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.0
```

## MTP faster inference

- MTP predicts multiple upcoming tokens at once for parallel verification; reported 1.3-1.7x faster inference with no accuracy degradation, reaching 170 tokens/s on 1x RTX 6000 PRO GPU versus 100-token baseline; especially effective on GPUs[^qwen38-next].
- Gains are smaller on lower-memory-bandwidth devices such as older Macs[^qwen38-next].
- Shared MTP modules exclude `embed_tokens` and share it with the main model to save disk, RAM, and VRAM by about 1-2 GB[^qwen38-next]:

| MTP Type | General MTP | Shared MTP | Savings |
| --- | --- | --- | --- |
| BF16 | 7.77 GB | 5.23 GB | 2.54 GB |
| Q8_0 | 4.14 GB | 2.79 GB | 1.35 GB |
| Q4_K_M | 2.79 GB | 1.91 GB | 880 MB |

- Run MTP by installing or updating Unsloth Desktop and re-downloading the model or MTP file; advanced sidebar exposes MTP/Ngram speculative decoding and draft-token count[^qwen38-next].
- Custom llama.cpp branch for MTP[^qwen38-next]:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone --branch qwen4exp/mtp https://github.com/danielhanchen/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

- Download shared MTP module[^qwen38-next]:

```bash
hf download unsloth/Qwen3.8-Flash-Next-GGUF \
    --local-dir unsloth/Qwen3.8-Flash-Next-GGUF \
    --include "*mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf*"
```

- Serve with shared MTP draft model[^qwen38-next]:

```bash
llama.cpp/llama-server \
    -hf unsloth/Qwen3.8-Flash-Next-GGUF:UD-Q4_K_XL \
    -md unsloth/Qwen3.8-Flash-Next-GGUF/MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf \
    --spec-type draft-mtp --spec-draft-n-max 5
```

## Source-reported benchmarks

All figures are source-reported Unsloth claims[^qwen38-next]:

- Model-level claim: outperforms Claude-4.6-Opus (Max) while running locally on 75 GB setups[^qwen38-next].
- Quantization claim: 1-bit 79% smaller than BF16 at 80% top-1% accuracy recovery[^qwen38-next].
- MTP claim: 1.3-1.7x faster, 170 tok/s on RTX 6000 PRO versus 100 tok/s baseline[^qwen38-next].
- Benchmark and throughput images plus Dynamic V3.0 article link are included in the source but were not independently inspected here[^qwen38-next].

## Relationships

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — Qwen3.8-Flash-Next `UD-IQ1_S` through `Q8_0` instances of Unsloth per-layer dynamic post-training quantization with 4-bit-minimum PLE/Ngram retention.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — top-1 accuracy, mean KLD, and 99.9% KLD figures used here are the same fidelity signals used to judge quantized models.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — llama.cpp `--spec-type draft-mtp` path with shared-MTP packaging and 1-2 GB extra-memory planning shared with Gemma 4 and Qwen3.6 MTP runs.
- Related to [Qwen3.6 Local Deployment](qwen3.6.md) — prior Qwen hybrid-thinking local family with the same thinking/instruct sampling split and MTP tuning pattern, now followed by the Qwen4-architecture Qwen3.8-Flash-Next.

## Coverage limits

- Remote images, KLD/accuracy plots, throughput charts, GIF demonstrations, Hugging Face and ModelScope files, and linked Unsloth Desktop, llama.cpp, MTP, and Dynamic 3.0 pages were not independently inspected; benchmark, tok/s, and hardware claims are source-reported Unsloth claims, not independently verified.
- The source llama-cli path pairs a `UD-IQ1_S` folder with a `UD-Q4_K_XL` shard filename; preserved as written without assuming the intended shard layout.
- No local attachments were referenced by the source.

[^qwen38-next]: Qwen3.8-Flash-Next: How to Run Locally — `../raw/unsloth/models/qwen3.8-next.md`, 125B MoE Qwen4-architecture identity with 262K context and Claude-4.6-Opus claim, 75-355 GB standard and 76-355 GB MTP hardware tables, thinking/instruct sampling and preserve-thinking plus reasoning-effort controls, Ngram/PLE 4-bit-minimum note with 10-row size/accuracy/KLD table, Unsloth Desktop and llama.cpp install/download/run/serve commands, shared-versus-general MTP size table with 1.3-1.7x and 170 tok/s claims and custom llama.cpp MTP branch commands, and benchmark tradeoff notes.
