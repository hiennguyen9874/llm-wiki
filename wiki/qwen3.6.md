---
type: Concept
title: Qwen3.6 Local Deployment
description: Run Alibaba Qwen3.6-27B and 35B-A3B hybrid-thinking multimodal models locally via Unsloth GGUF/MLX/NVFP4 with hardware, sampling, reasoning, MTP, and benchmark guidance.
tags: [qwen, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning, vision, mtp, nvfp4]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T16:00:00Z }
sources:
  - id: qwen36
    resource: ../raw/unsloth/models/qwen3.6.md
    title: 'Qwen3.6 - How to Run Locally'
---

Qwen3.6 is Alibaba's multimodal hybrid-thinking family with `Qwen3.6-27B` dense and `35B-A3B` MoE variants for agentic coding, vision, and chat; Unsloth publishes Dynamic 2.0 GGUFs, MLX quants, MTP GGUFs, and Blackwell NVFP4 quants with llama.cpp, Unsloth Desktop, vLLM, and SGLang run paths[^qwen36].

## Model identity

- Family `Qwen3.6-27B` and `35B-A3B`; multimodal hybrid-thinking with thinking and instruct non-thinking modes[^qwen36].
- Reported scope: top performance for size, 256K context across 201 languages, strength in agentic coding, vision, and chat[^qwen36].
- Overview positions 27B on 18GB RAM setups and 35B-A3B on 22GB setups; use the per-quant tables below as authoritative[^qwen36].
- Unsloth GGUFs use Dynamic 2.0 calibration on real-world use-case datasets with important layers upcasted[^qwen36].
- Developer-role support for Codex, OpenCode, and other agentic coding tools; improved nested-object tool-call parsing carried over from Qwen3.5 work[^qwen36].
- Hugging Face artifacts named in source include `unsloth/Qwen3.6-27B-GGUF`, `unsloth/Qwen3.6-35B-A3B-GGUF`, `unsloth/Qwen3.6-27B-MTP-GGUF`, `unsloth/Qwen3.6-35B-A3B-MTP-GGUF`, plus MLX and NVFP4 repos below[^qwen36].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory[^qwen36]:

| Qwen3.6 | 3-bit | 4-bit | 6-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- |
| **27B** | 15 GB | 18 GB | 24 GB | 30 GB | 55 GB |
| **35B-A3B** | 17 GB | 23 GB | 30 GB | 38 GB | 70 GB |

MTP variants need about 1 GB additional headroom[^qwen36]:

| Qwen3.6 MTP | 3-bit | 4-bit | 6-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- |
| **27B** | 16 GB | 19 GB | 25 GB | 31 GB | 56 GB |
| **35B-A3B** | 18 GB | 24 GB | 31 GB | 39 GB | 71 GB |

- Rule of thumb: total available memory should exceed the quantized file size; smaller hosts can use SSD/HDD offload at slower speed[^qwen36].
- Recommended inference starting point is Dynamic 4-bit `UD-Q4_K_XL`; for size/accuracy balance the source recommends at least Dynamic 2-bit `UD-Q2_K_XL`[^qwen36].
- Full F16 precision is stated as around 72 GB in the llama.cpp section; treat the 55/70 GB BF16 rows above as the source hardware table and 72 GB as an approximate F16 note[^qwen36].

## Recommended settings

- Maximum context window `262,144`, extendable to 1M via YaRN[^qwen36].
- Adequate output length `32,768` tokens for most queries[^qwen36].
- `presence_penalty = 0.0 to 2.0`; default off, higher values may reduce repetition at a slight performance cost[^qwen36].
- If output is gibberish, context length may be set too low, or try `--cache-type-k bf16 --cache-type-v bf16`[^qwen36].
- Do not use CUDA 13.2 because it may produce gibberish; use below 13.2 or CUDA 13.3[^qwen36].

Thinking mode[^qwen36]:

| General tasks | Precise coding tasks such as WebDev |
| --- | --- |
| temperature = 1.0 | temperature = 0.6 |
| top_p = 0.95 | top_p = 0.95 |
| top_k = 20 | top_k = 20 |
| min_p = 0.0 | min_p = 0.0 |
| presence_penalty = 0.0 | presence_penalty = 0.0 |
| repeat_penalty = disabled or 1.0 | repeat_penalty = disabled or 1.0 |

Instruct non-thinking mode for general tasks[^qwen36]:

| Setting | Value |
| --- | --- |
| temperature | 0.7 |
| top_p | 0.8 |
| top_k | 20 |
| min_p | 0.0 |
| presence_penalty | 1.5 |
| repeat_penalty | disabled or 1.0 |

## Thinking controls

- Disable thinking with `--chat-template-kwargs '{"enable_thinking":false}'`; on Windows PowerShell use `--chat-template-kwargs "{\"enable_thinking\":false}"`; `true`/`false` are interchangeable[^qwen36].
- Preserve Thinking keeps the prior thinking trace in continued conversations at higher token cost with possible accuracy gain; Unsloth Studio exposes Think and Preserved Thinking toggles[^qwen36]:

```bash
--chat-template-kwargs '{"preserve_thinking":true}'
```

- llama.cpp enable/disable matrix uses `enable_thinking true/false` on Linux, macOS, and WSL and escaped quoting on Windows/PowerShell[^qwen36].
- Preserve-thinking server example[^qwen36]:

```bash
./llama.cpp/llama-server \
    --model unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-BF16.gguf \
    --alias "unsloth/Qwen3.6-35B-A3B-GGUF" \
    --temp 0.6 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.00 \
    --port 8001 \
    --chat-template-kwargs '{"preserve_thinking":true}'
```

## Quantization packaging

- GGUF: Dynamic 2.0 family; only `Q6_K` was updated for more dynamic layers in this cycle and a new `UD-IQ4_NL_XL` quant was introduced[^qwen36].
- MLX for macOS: 27B in 3-bit, 4-bit, MXFP4, NVFP4, 6-bit, and 8-bit; 35B-A3B in 3-bit, 4-bit, and 8-bit[^qwen36]:

```bash
curl -fsSL https://raw.githubusercontent.com/unslothai/unsloth/refs/heads/main/scripts/install_qwen3_6_mlx.sh | sh
source ~/.unsloth/unsloth_qwen3_6_mlx/bin/activate
python -m mlx_vlm.chat --model unsloth/Qwen3.6-27B-UD-MLX-4bit
```

- Reported 27B MLX fidelity, lower is better; 8-bit is closest to full precision while 4-bit is much smaller at modest KLD cost[^qwen36]:

| Model | Mean KLD | Median KLD | PPL | P90 KLD | P99.9 KLD | Size |
| --- | --- | --- | --- | --- | --- | --- |
| 8-bit | 0.0028 | 0.0003 | 4.812 | 0.0019 | 0.192 | 34.7 GB |
| 6-bit | 0.0037 | 0.0007 | 4.809 | 0.0032 | 0.343 | 30.5 GB |
| 4-bit | 0.0227 | 0.0053 | 4.821 | 0.0293 | 2.339 | 26.2 GB |
| NVFP4 | 0.0325 | 0.0087 | 4.843 | 0.0466 | 3.693 | 26.2 GB |
| MXFP4 | 0.0479 | 0.0153 | 4.902 | 0.0769 | 4.035 | 25.6 GB |
| 3-bit | 0.0734 | 0.0223 | 4.976 | 0.1261 | 5.529 | 24.1 GB |

- NVFP4, July 10 2026: dynamic W4A4 quants using Blackwell FP4 tensor cores, FP8 KV-cache calibration for 2x longer context, MTP tensors built in, and chat-template plus coding/tool-call/chat and UltraChat calibration[^qwen36].
- NVFP4 requires Blackwell GPUs such as RTX 50-series, DGX Spark, B200/B300; older GPUs should use GGUFs[^qwen36].
- Reported NVFP4 positioning: 27B 2.5x faster on 24GB VRAM; 35B-A3B 1.56x faster and 35B-A3B Fast full-W4A4 1.79x faster on 32GB VRAM; 35B Fast is fastest while non-Fast is slightly larger and more accurate; decode reported as 1.03x faster for 27B and 1.17x/1.22x for 35B variants[^qwen36].
- Do not pin Marlin for W4A4 because it can cause about 2.5x degradation; leave vLLM backend auto-selection to choose CUTLASS, FlashInfer-TRTLLM, or Cute-DSL, except DGX Spark where `--moe-backend flashinfer_b12x` is required[^qwen36].

## Local run paths

- Unsloth Desktop is the easiest path on macOS, Windows, and Linux for GGUF and safetensor search, download, and run with self-healing tool calling, web search, Python/Bash execution, auto-tuned inference parameters, llama.cpp CPU+GPU inference, and faster training[^qwen36].
- Install with `curl -fsSL https://unsloth.ai/install.sh | sh` on macOS/Linux/WSL or `irm https://unsloth.ai/install.ps1 | iex` on Windows PowerShell; launch with `unsloth studio -H 0.0.0.0 -p 8888` and open `http://127.0.0.1:8888`; `--secure` uses a Cloudflare tunnel[^qwen36].
- In Studio Chat search for Qwen3.6 or Qwen3.6 MTP, download the chosen quant, and run with auto-set parameters while retaining manual control of context, template, and MTP settings[^qwen36].
- llama.cpp build from `https://github.com/ggml-org/llama.cpp`; use `-DGGML_CUDA=OFF` for CPU-only and Apple Mac/Metal where Metal is default; build `llama-cli llama-mtmd-cli llama-server llama-gguf-split`[^qwen36]:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

- Standard 27B thinking example for general tasks; use `temperature=0.6` for precise coding[^qwen36]:

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.00
```

- Standard 27B non-thinking server example[^qwen36]:

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-GGUF"
./llama.cpp/llama-server \
    -hf unsloth/Qwen3.6-27B-GGUF:UD-Q4_K_XL \
    --temp 0.7 \
    --top-p 0.8 \
    --top-k 20 \
    --presence-penalty 1.5 \
    --min-p 0.00 \
    --chat-template-kwargs '{"enable_thinking":false}'
```

- Standard 35B-A3B thinking and non-thinking forms use the same sampling values with `unsloth/Qwen3.6-35B-A3B-GGUF` as the `-hf` target[^qwen36].
- Manual download after `pip install huggingface_hub`; see the source Hugging Face Hub XET debugging page if stuck[^qwen36]:

```bash
hf download unsloth/Qwen3.6-35B-A3B-GGUF \
    --local-dir unsloth/Qwen3.6-35B-A3B-GGUF \
    --include "*mmproj-F16*" \
    --include "*UD-Q4_K_XL*"
```

- Local-file conversation mode with vision projector[^qwen36]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Qwen3.6-35B-A3B-GGUF/mmproj-F16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --min-p 0.00 \
    --top-k 20
```

- MTP adds `--spec-type draft-mtp --spec-draft-n-max 2`; start at `2`, then try `1` through `6` because the optimum is hardware-dependent[^qwen36]:

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-MTP-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/Qwen3.6-27B-MTP-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 20 \
    --min-p 0.00 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

- vLLM NVFP4 install and serve; change the checkpoint name for other NVFP4 variants[^qwen36]:

```bash
uv venv unsloth-nvfp4-env --python 3.13
source unsloth-nvfp4-env/bin/activate
uv pip install "vllm>=0.25.0" "flashinfer-python>=0.6.13" "nvidia-cutlass-dsl>=4.5.2" \
    --torch-backend=auto
```

```bash
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast
```

```bash
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast \
    --speculative-config '{"method": "mtp", "num_speculative_tokens": 2}'
```

- DGX Spark NVFP4 must verify b12x GEMM/MoE availability, then serve with `CUTE_DSL_ARCH=sm_121a` and `flashinfer_b12x`, or inference is much slower[^qwen36]:

```bash
export CUTE_DSL_ARCH=sm_121a
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast --moe-backend flashinfer_b12x
```

- SGLang NVFP4 example[^qwen36]:

```bash
python -m sglang.launch_server --model-path unsloth/Qwen3.6-27B-NVFP4 --speculative-algorithm NEXTN \
     --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

- OpenAI Codex and Claude Code: point the coding agent at the local `llama-server` URL and set the model name to the exact `--alias` value reported by `GET /v1/models`, for example `unsloth/Qwen3.6-35B-A3B-GGUF`, while keeping Qwen3.6 sampling settings[^qwen36].
- Qwen3.5 fine-tuning guide is referenced for training Qwen3.6; no Qwen3.6-specific training commands are given in this source[^qwen36].

## Source-reported benchmarks

All figures are source-reported Unsloth claims[^qwen36]:

- GGUF KLD: nearly all Unsloth GGUFs are on the SOTA Pareto frontier and top in 21 of 22 tested sizes; KLD measures match to BF16 output distribution[^qwen36].
- MTP: about 1.4-2.2x faster generation with no accuracy change; RTX 6000 generation at 160 tok/s for 27B MTP and 240 tok/s for 35B-A3B; local UD-Q2_K_XL generation at 140 tok/s for 27B and 220 tok/s for 35B-A3B[^qwen36].
- MTP shape: dense models gain about 1.4-2x versus MoE at about 1.15-1.25x; average at draft 2 is 1.4x dense and 1.15-1.2x MoE; acceptance falls from about 83% to 50% with 4 draft tokens, so more than 2 drafts is not recommended[^qwen36].
- NVFP4 accuracy is comparable to NVIDIA NVFP4, FP8, and BF16 with comparable output lengths, so speed is not offset by longer thinking[^qwen36]:

| 27B provider | MMLU-Pro | GPQA | AIME 2025 |
| --- | --- | --- | --- |
| Unsloth | 86.25 | 86.34 | 93.12 |
| NVIDIA | 85.96 | 86.87 | 93.12 |
| FP8 | 86.11 | 86.87 | 93.75 |
| BF16 | 85.96 | 88.13 | 93.33 |

| 35B-A3B provider | MMLU-Pro | GPQA | AIME 2025 |
| --- | --- | --- | --- |
| Unsloth | 85.85 | 86.74 | 92.29 |
| Unsloth Fast | 85.58 | 87.75 | 91.67 |
| NVIDIA | 85.60 | 87.12 | 91.88 |
| FP8 | 85.75 | 86.74 | 93.12 |
| BF16 | 85.75 | 86.36 | 92.50 |

- Official Qwen 27B and 35B-A3B score images are included in the source but were not independently inspected here[^qwen36].
- Practical tradeoff stated in source: Dynamic GGUFs for memory/quality balance, MTP for faster generation, NVFP4 on Blackwell for maximum throughput, Unsloth Studio defaults for easiest path[^qwen36].

## Relationships

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — Qwen3.6 `UD-Q4_K_XL`, `UD-Q2_K_XL`, and `UD-IQ4_NL_XL` instances of Unsloth per-layer dynamic post-training quantization.
- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — Blackwell W4A4 path, backend auto-selection, and DGX Spark serving context for the Qwen3.6 NVFP4 checkpoints named here.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — llama.cpp `--spec-type draft-mtp` and `--spec-draft-n-max 2` starting point with 1-through-6 sweep shared with Gemma 4 and Qwen3.5 MTP runs.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — mean/median/P90/P99.9 KLD, PPL, and output-length checks used here to judge MLX, GGUF, and NVFP4 fidelity.

## Coverage limits

- Remote benchmark plots, throughput images, GIF demonstrations, Hugging Face files, and linked Unsloth, llama.cpp, MLX, vLLM, SGLang, troubleshooting, and fine-tuning pages were not independently inspected; benchmark, tok/s, and hardware claims are source-reported Unsloth claims, not independently verified.
- No local attachments were referenced by the source.

[^qwen36]: Qwen3.6 - How to Run Locally — `../raw/unsloth/models/qwen3.6.md`, Qwen3.6-27B/35B-A3B identity with 256K context and 201-language claim, standard and MTP hardware tables, thinking/instruct sampling and preserve-thinking controls, Dynamic 2.0 and developer-role/tool-call notes, MLX quant list and 27B KLD/PPL table, NVFP4 speed/VRAM/accuracy/backend tables and vLLM/SGLang/DGX Spark commands, Unsloth Studio and llama.cpp standard/MTP install/download/run/server commands with mmproj projector, Codex/Claude Code alias note, and GGUF/MTP/NVFP4 benchmark tradeoff.
