---
type: Concept
title: Muse Glimmer Local Deployment
description: Run Meta 30B dense vision Muse Glimmer locally via Unsloth Dynamic GGUFs with hardware, sampling, reasoning, llama.cpp, and benchmark guidance.
tags: [muse, meta, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning, vision]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T16:00:00Z }
sources:
  - id: muse-glimmer
    resource: ../raw/unsloth/models/muse-glimmer.md
    title: 'Muse Glimmer - How to Run Locally'
  - id: dflash2
    resource: ../raw/DFlash2.md
    title: 'DFlash 2: Keep Drafting Parallel'
---

Muse Glimmer is Meta's 30B-parameter dense vision open-weight model for local agentic and coding workflows, presented as the first open model from Meta Superintelligence Labs under Apache 2.0; Unsloth publishes Dynamic 2- to 8-bit GGUFs and day-zero llama.cpp plus Unsloth Desktop run paths for 12GB+ local setups[^muse-glimmer].

## Model identity

- Vendor Meta / Meta Superintelligence Labs; 30B total, dense architecture, vision-capable[^muse-glimmer].
- Presented as first open model from Meta Superintelligence Labs, released under Apache 2.0[^muse-glimmer].
- Positioned for local agentic and coding workflows, including multimodal workflows via vision support[^muse-glimmer].
- Full-precision BF16 weights use about 58 GB[^muse-glimmer].
- Unsloth reports collaboration with Meta and Hugging Face on the llama.cpp inference implementation with day-zero support[^muse-glimmer].
- Hugging Face artifacts: `unsloth/Muse-Glimmer-30B-GGUF` and Muse Glimmer 30B collection[^muse-glimmer].

## Capabilities

- Plans multi-step tasks, executes sequential tool calls, recovers from failures, adapts as conditions change, uses runtime memory, and resumes work across long-running sessions when state is persisted[^muse-glimmer].
- Persistence across sessions comes from the agent harness, not the model itself[^muse-glimmer].
- Vision support enables multimodal workflows[^muse-glimmer].
- Controllable reasoning efforts: `low`, `medium`, `high`, `xhigh`[^muse-glimmer].

## Reasoning and sampling settings

- Recommended defaults: `temperature = 1.0`, `top_p = 0.95`, `top_k = 64`[^muse-glimmer].
- Maximum context length: `131,072` default, up to `262,144`[^muse-glimmer].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory[^muse-glimmer]:

| 2-bit | 3-bit | 4-bit | 6-bit | 8-bit |
| --- | --- | --- | --- | --- |
| 12-14 GB | 14-15 GB | 17 GB | 20-22 GB | 34 GB |

Detailed table[^muse-glimmer]:

| Quantization | Recommended RAM/VRAM | Hardware examples |
| --- | --- | --- |
| 2-bit (`UD-Q2_K_XL`) | 12-14+ GB | RTX 4080 |
| 3-bit (`UD-Q3_K_XL`) | 14-15 GB+ | RTX 4090 |
| 4-bit (`UD-Q4_K_XL`, `NVFP4`) | 17 GB+ | Mac 32GB |
| 6-bit (`UD-Q6_K_XL`) | 20-22 GB+ | RTX 5090, Mac 48GB |
| 8-bit (`UD-Q8_K_XL`) | 34 GB+ | Mac 128GB, DGX Spark |
| BF16 full precision | 58 GB+ | Mac 128GB, DGX Spark |

- Source overview states 18GB RAM/VRAM setups including Mac and GPU/CPU systems; detailed table permits 12GB+ for 2-bit, so treat 18GB as a general entry point and the per-quant table as authoritative[^muse-glimmer].
- Rule of thumb: total available memory should exceed the downloaded quantized model size; smaller hosts can use partial RAM / disk offload but generation is slower; larger context windows need more compute[^muse-glimmer].
- Recommended starting point is Dynamic 4-bit `UD-Q4_K_XL`[^muse-glimmer].

## Local run paths

- Unsloth Desktop is an open-source desktop app for local AI on macOS, Windows, and Linux; features include GGUF and safetensor search/download/run, self-healing tool calling plus web search, Python/Bash code execution, automatic inference-parameter tuning, llama.cpp-backed CPU plus GPU inference, and faster training paths[^muse-glimmer].
- Install: download the Unsloth Desktop app, or on macOS/Linux/WSL run `curl -fsSL https://unsloth.ai/install.sh | sh` and on Windows PowerShell run `irm https://unsloth.ai/install.ps1 | iex`[^muse-glimmer].
- In Unsloth Desktop, search the Model hub for Muse Glimmer, download the chosen quant, and run with auto-set inference parameters while retaining manual control over context length, chat template, and other settings; supports GGUF and MLX files[^muse-glimmer].
- Serve via Unsloth API with `llama-server` runtime flags for context sizing, GPU layers, threading, sampling, networking, and tool configuration[^muse-glimmer]:

```bash
unsloth run --model unsloth/Muse-Glimmer-30B-GGUF:UD-Q4_K_XL
```

- llama.cpp: build from `https://github.com/ggml-org/llama.cpp`; use `-DGGML_CUDA=ON` for CUDA or `OFF` for no-GPU / CPU-only; on Apple Mac / Metal set `-DGGML_CUDA=OFF` since Metal is on by default; build targets `llama-cli llama-mtmd-cli llama-server llama-gguf-split`[^muse-glimmer]:

```bash
apt-get update
apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev -y
git clone https://github.com/ggml-org/llama.cpp
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

- Direct llama.cpp run, after `export LLAMA_CACHE="unsloth/Muse-Glimmer-30B-GGUF"`; no manual context-length setting is needed because llama.cpp uses the exact amount required[^muse-glimmer]:

```bash
./llama.cpp/llama-cli \
    -hf unsloth/Muse-Glimmer-30B-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64
```

- Manual download after `pip install huggingface_hub`; use `UD-Q2_K_XL` pattern for Dynamic 2-bit; see source's Hugging Face Hub XET debugging page if downloads stall[^muse-glimmer]:

```bash
hf download unsloth/Muse-Glimmer-30B-GGUF \
    --local-dir unsloth/Muse-Glimmer-30B-GGUF \
    --include "*mmproj-BF16*" \
    --include "*UD-Q4_K_XL*"
```

- Conversation mode with vision projector[^muse-glimmer]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/Muse-Glimmer-30B-GGUF/Muse-Glimmer-30B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Muse-Glimmer-30B-GGUF/mmproj-BF16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64
```

- llama-server deployment[^muse-glimmer]:

```bash
./llama.cpp/llama-server \
    --model unsloth/Muse-Glimmer-30B-GGUF/Muse-Glimmer-30B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Muse-Glimmer-30B-GGUF/mmproj-BF16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --alias "unsloth/Muse-Glimmer-30B-GGUF" \
    --port 8001
```

- Additional Unsloth Desktop uses: connect Claude Code, Codex, web search, MCP and other tools; fine-tune text, diffusion, embedding, and other models; generate and train images, video, and TTS locally[^muse-glimmer].

## Fine-tuning

- Source states Muse Glimmer 30B can be fine-tuned with Unsloth on a 24GB card[^muse-glimmer].
- Two Kaggle notebooks provide 30 hours free with 2x Tesla T4 GPUs: Muse Glimmer Vision and Muse Glimmer Conversational[^muse-glimmer].

## Source-reported benchmarks

Muse Glimmer 30B High Reasoning versus Gemma4-31B Thinking Mode and Qwen3.6-27B Thinking Mode; all numbers are source-reported Unsloth claims[^muse-glimmer]:

- General Agentic leads: MCP Atlas Public 75.5 vs 54.2 / 62.5; DeepSearch QA 74.6 vs 61.7 / 71.1; tau3-Banking 23.5 vs 15.1 / 16.7; WildClawBench 47.6 vs 37.6 / 43.2; Gaia2 43.3 vs 36.4 / 40.0[^muse-glimmer].
- General Agentic losses: GDPVal-AA v2 953 vs 811 / 1141 Qwen best; SkillsBench with skills 44.3 vs 32.4 / 46.6 Qwen best; OSWorld-Verified 65.9 vs 58.5 / 75.6 Qwen best[^muse-glimmer].
- Agentic Coding: SWE-Bench Pro 51.2 vs 36.9 / 50.2 Glimmer best; SWE-Bench Verified 76.0 vs 66.6 / 77.2 Qwen best; TerminalBench 2.1 with terminus2 51.7 vs 43.4 / 60.7 Qwen best; SciCode 43.6 vs 43.4 / 39.8 Glimmer best[^muse-glimmer].
- Multimodal: CharXiv Reasoning 78.8 vs 77.7 / 78.4 Glimmer best; ScreenSpot Pro 75.4 vs 75.9 / 76.1 Qwen best; OmniDocBench v1.5 75.8 vs 72.5 / 77.8 Qwen best; MMMU Pro 74 vs 73 / 75 Qwen best[^muse-glimmer].
- Safety: CI Memories violation lower is better 26.4 vs 12.1 Gemma best / 53.4, coverage 64.8 vs 53.0 / 66.9 Qwen best; Siren AgentDojo attack success lower is better 28.4 vs 25.6 Gemma best / 40.3, utility 94.2 vs 90.8 / 92.7 Glimmer best[^muse-glimmer].
- General Capabilities and Reasoning: IFBench 77.0 vs 76.0 / 70.8 Glimmer best; AIME 2026 94.7 vs 89.2 / 94.1 Glimmer best; GPQA Diamond AA 83.5 vs 85.7 Gemma best / 84.2; HLE Text AA 22.0 vs 23.6 Gemma best / 23.1; AA-LCR 80.0 vs 68.3 / 73.3 Glimmer best; Beam128K 65.1 vs 58.2 / 63.0 Glimmer best[^muse-glimmer].

## Relationships

- Related to [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — day-zero `incoai/Muse-Glimmer-30B-DFlash2` drafter reports 5.70 mean acceptance (block 16, default sampling) versus 4.44 official DFlash and 4.48 community DSpark, with 3.1–4.6× autoregressive throughput[^dflash2].

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — Muse Glimmer UD-Q2_K_XL through UD-Q8_K_XL instances of Unsloth per-layer dynamic post-training quantization.
- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — 4-bit hardware table lists `NVFP4` alongside `UD-Q4_K_XL` as a 17GB+ option.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — same Unsloth Desktop plus llama.cpp local-run pattern used for MTP-capable models, although this source does not claim MTP support for Muse Glimmer.

## Coverage limits

- Remote GIF demonstrations, benchmark plots, Hugging Face files, and linked Unsloth, llama.cpp, and Kaggle pages were not independently inspected; benchmark, hardware, and quant claims are source-reported Unsloth claims, not independently verified.
- No local attachments were referenced by the source.

[^muse-glimmer]: Muse Glimmer - How to Run Locally — `../raw/unsloth/models/muse-glimmer.md`, 30B dense vision identity and first-open-model Apache-2.0 claim, 58GB BF16 and 12GB-58GB hardware tables, temp 1.0 / top-p 0.95 / top-k 64 and 131K-262K context, low/medium/high/xhigh reasoning, harness-persisted agentic memory claim, Unsloth Desktop and llama.cpp install/download/run/server commands with mmproj vision projector, 24GB fine-tune and Kaggle notebook links, and Glimmer vs Gemma4-31B vs Qwen3.6-27B benchmark table.
[^dflash2]: DFlash 2: Keep Drafting Parallel — `../raw/DFlash2.md`.
