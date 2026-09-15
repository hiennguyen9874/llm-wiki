---
type: Concept
title: Kimi K3 Local Deployment
description: Run Moonshot AI 2.8T (104B active) Kimi K3 locally via Unsloth Dynamic GGUFs with hardware, sampling, reasoning, llama.cpp, and benchmark guidance.
tags: [kimi, moonshot-ai, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning, vision]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: kimi-k3
    resource: ../raw/unsloth/models/kimi-k3.md
    title: 'Kimi K3 - How to Run Locally'
  - id: kimi-k3-dspark
    resource: ../raw/Kimi-K3-DSpark.md
    title: Kimi K3 DSpark speculator
---

Kimi K3 is Moonshot AI's 2.8T-parameter (104B active) open-weight model for coding, agentic, long-context, and chat work; Unsloth publishes Dynamic 1-bit to 8-bit GGUFs and day-zero llama.cpp plus Unsloth Desktop run paths for 610GB+ local setups[^kimi-k3].

## Model identity

- Vendor Moonshot AI; 2.8T total / 104B active[^kimi-k3].
- Presented in this source as the strongest open model to date, rivaling Claude 4.8 Opus and GPT-5.6[^kimi-k3].
- Native vision; maximum context window `1,048,576`[^kimi-k3].
- Base precision uses MXFP4 for MoE weights and BF16 for everything else; full-precision inference requires about 1.56 TB of storage[^kimi-k3].
- Hugging Face artifact: `unsloth/Kimi-K3-GGUF`[^kimi-k3].

## Reasoning and sampling settings

- Thinking-only model with `preserve_thinking` always enabled and max thinking on by default; instant mode is not supported[^kimi-k3].
- Thinking effort is configured with the `reasoning_effort` request field; supported values are `"low"`, `"high"`, and `"max"`; Unsloth Desktop exposes a low/high/max toggle[^kimi-k3].
- Default recommendation: `temperature = 1.0`, `top_p = 0.95`[^kimi-k3].
- Agentic recommendation: `temperature = 1.0`, `top_p = 1.0`[^kimi-k3].
- Training default keeps thinking traces rather than deleting them[^kimi-k3].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory; keep total available memory comfortably above the quantized file size[^kimi-k3]:

| Dynamic 1-bit S | Dynamic 1-bit M | Dynamic 2-bit XXS | Dynamic 2-bit XL | Q8 lossless |
| --- | --- | --- | --- | --- |
| 610 GB | 665 GB | 726 GB | 880 GB | 1.6 TB |

- Source says Kimi K3 can run on an NVIDIA DGX Station, or a Mac Studio connected to a 128GB RAM device[^kimi-k3].
- Tutorial default is `UD-IQ1_S` (594 GB) for best balance of accessibility and accuracy; it requires at least 610 GB RAM[^kimi-k3].
- Rule of thumb: RAM + VRAM should approximately equal the quant size; smaller hosts still work but fall back to much slower disk offloading[^kimi-k3].
- Source-reported throughput when the model fits: about 20 tokens/s generation on B200s and over 120 tokens/s throughput[^kimi-k3].

## Unsloth dynamic quantization

Source summaries are approximate top-1 agreement versus the lossless baseline: Dynamic 1-bit reaches about 78.9% while about 62% smaller; Dynamic 2-bit `UD-Q2_K_XL` reaches about 90% while about 45% smaller[^kimi-k3].

Full reported GGUF table[^kimi-k3]:

| Quant | GB | Mean KLD | PPL(q) | Top-1 agree % | RMS dp % |
| --- | --- | --- | --- | --- | --- |
| UD-IQ1_S | 594.0 | 0.5645 | 2.5789 | 78.875 +/- 0.107 | 36.495 |
| UD-IQ1_M | 648.9 | 0.4789 | 2.3639 | 81.219 +/- 0.103 | 33.629 |
| UD-IQ2_XXS | 711.1 | 0.3784 | 2.1266 | 84.127 +/- 0.096 | 29.826 |
| UD-Q2_K_XL | 861.3 | 0.1779 | 1.7359 | 90.390 +/- 0.077 | 19.862 |
| UD-Q4_K_XL | 1,510 | — | 1.4579 | — | — |
| UD-Q8_K_XL | 1,560 | — | 1.4581 | — | — |

- `UD-Q8_K_XL` is described as lossless versus the MXFP4 full safetensors version because `Q8_K_XL` follows the native MXFP4-plus-BF16 layout exactly; `UD-Q4_K_XL` is near full precision with remaining tensors except norms at `Q8_0`, and is about 50 GB smaller than Q8[^kimi-k3].
- Source says work is still investigating whether Kimi K3 can be pushed under 512 GiB without damaging the model; dynamic 1-bit is parenthetically given as 553.2 GiB[^kimi-k3].
- Imatrix generation and quantization used the 1.56 TB lossless `UD-Q8_K_XL` throughout calibration; its perplexity is 1.4581[^kimi-k3].
- Community-quant contrast is source-reported only: one 618.9 GB `IQ1_M` is larger than Unsloth's 594 GB 1-bit quant but its perplexity jumps to 54.56, about 21x worse; one 725 GB `IQ2_XXS` at 96 PPL compares against Unsloth's 711 GB at 2.12 PPL, about 45x worse[^kimi-k3].
- Durable lesson stated by the source is that dynamic quantization plus proper calibration matters more than nominal bit width[^kimi-k3].

## GGUF implementation notes

- Built on llama.cpp PR `26185` plus Unsloth fork PR `48`, which adds vision support and bug fixes[^kimi-k3].
- Vision tower / mmproj is similar to the Kimi-K2.5 tower, but with RMSNorm, no biases, a non-square fused QKV where qkv width differs from `n_embd`, and a post-norm projector[^kimi-k3].
- llama.cpp needed `n_tokens * 160` budget instead of `n_tokens * 40` at large batch sizes[^kimi-k3].
- Kimi chat template was converted to Jinja format[^kimi-k3].

## Local run paths

- Unsloth Desktop automatically offloads to RAM and detects multi-GPU setups; it runs on macOS, Windows, and Linux with GGUF and safetensors search/download/run, self-healing tool calling plus web search, Python/Bash code execution, automatic inference-parameter tuning, llama.cpp-backed CPU plus GPU inference, and faster training paths[^kimi-k3].
- Install and launch: download the Unsloth Desktop app, or on macOS/Linux/WSL run `curl -fsSL https://unsloth.ai/install.sh | sh` and on Windows PowerShell run `irm https://unsloth.ai/install.ps1 | iex`; then run `unsloth studio` and open `http://127.0.0.1:8888`; `unsloth studio --secure` launches over HTTPS through a Cloudflare tunnel[^kimi-k3].
- In Unsloth Studio, create a password on first launch, search the Model hub for Kimi K3, download the chosen quant, and run with auto-set inference parameters while retaining manual control over low/high/max thinking, context length, and chat template[^kimi-k3].
- llama.cpp requires the specific Unsloth fork branch for vision support[^kimi-k3]:

```bash
git clone https://github.com/unslothai/llama.cpp
cd llama.cpp
git fetch origin pull/48/head:kimi-k3-fullsize-vision
git checkout kimi-k3-fullsize-vision
cd ..
cmake llama.cpp -B llama.cpp/build \
    -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build llama.cpp/build --config Release -j --clean-first --target llama-cli llama-mtmd-cli llama-server llama-gguf-split
cp llama.cpp/build/bin/llama-* llama.cpp
```

- Use `-DGGML_CUDA=OFF` for no-GPU or CPU-only inference; on Apple Mac / Metal devices set `-DGGML_CUDA=OFF` and continue since Metal support is on by default[^kimi-k3].
- Direct llama.cpp run, after `export LLAMA_CACHE="unsloth/Kimi-K3-GGUF"`[^kimi-k3]:

```bash
./llama.cpp/llama-cli \
    -hf unsloth/Kimi-K3-GGUF:UD-IQ1_S \
    --temp 1.0 \
    --top-p 0.95
```

- Source warns this download path can be very slow and recommends manual download after `pip install huggingface_hub`[^kimi-k3]:

```bash
hf download unsloth/Kimi-K3-GGUF \
    --local-dir unsloth/Kimi-K3-GGUF \
    --include "*mmproj-BF16*" \
    --include "*UD-IQ1_S*"
```

- Use `"*UD-Q8_K_XL*"` instead for full precision; see the source's Hugging Face Hub XET debugging page if downloads stall[^kimi-k3].
- Then run conversation mode with vision projector[^kimi-k3]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/Kimi-K3-GGUF/UD-IQ1_S/Kimi-K3-UD-IQ1_S-00001-of-00014.gguf \
    --mmproj unsloth/Kimi-K3-GGUF/mmproj-BF16.gguf \
    --temp 1.0 \
    --top-p 0.95
```

## Source-reported benchmarks

Kimi K3 `(max)` scores with source-selected competitors; HLE-Full, MMMU-Pro, and MathVision cells carry two numbers as written in the source[^kimi-k3]:

| Benchmark | Kimi K3 (max) | Claude Fable 5 (max) | GPT-5.6 Sol (max) | Claude Opus 4.8 (max) | GPT-5.5 (xhigh) | GLM-5.2 (max) |
| --- | --- | --- | --- | --- | --- | --- |
| GPQA Diamond | 93.5 | 92.6 | 94.1 | 91.0 | 93.5 | 91.2 |
| HLE-Full | 43.5 / 56.0 | 53.3 / 63.0 | 44.5 / 58.0 | 49.8 / 57.9 | 41.4 / 52.2 | — |
| DeepSWE | 67.5 | 70.0 | 73.0 | 59.0 | 67.0 | 46.2 |
| Terminal-Bench 2.1 | 88.3 | 88.0 | 88.8 | 84.6 | 83.4 | 82.7 |
| BrowseComp | 91.2 | 88.0 | 90.4 | 84.3 | 84.4 | — |
| GDPval-AA v2 (Elo) | 1686 | 1747 | 1736 | 1593 | 1491 | 1510 |
| OSWorld 2.0 | 58.3 | 66.1 | 62.6 | 55.7 | 49.5 | — |
| MMMU-Pro | 81.6 / 83.4 | 81.2 / 86.5 | 83.0 / 84.6 | 78.9 / 82.7 | 81.2 / 83.2 | — |
| MathVision | 94.3 / 97.8 | 94.8 / 98.6 | 95.8 / 97.8 | 86.7 / 97.1 | 92.2 / 96.8 | — |

- Source highlights BrowseComp 91.2 as a Kimi K3 lead and describes DeepSWE behavior as very efficient; supporting DeepSWE efficiency and benchmark plots were not independently inspected[^kimi-k3].

## Relationships

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — Kimi K3 UD-IQ1_S through UD-Q8_K_XL instances of Unsloth per-layer dynamic post-training quantization.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — top-1 agreement, mean KLD, RMS dp, and PPL figures used here are the same fidelity signals used to judge quantized models.
- Related to [Kimi K3 DSpark Speculator](kimi-k3-dspark.md) — server-side SGLang speculative-decoding path for the same base model with block-size-7 drafting and 1M-token serving[^kimi-k3-dspark].
- Related to [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md) — canonical tech-report source for the 2.8T/104B hybrid KDA-MLA design, Stable LatentMoE, MoonViT-V2, and 2.5x scaling claim.
- Related to [Kimi K3 Post-Training and Agentic RL](kimi-k3-posttraining-agentic-rl.md) — canonical source for SFT, nine domain-effort RL experts, MOPD, MXFP4 QAT, and XTML template.
- Related to [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md) — canonical source for MoonEP, KDA parallelism, RL infra, AgentENV, and hybrid-cache serving.
- Related to [Kimi K3 Evaluation and Case Studies](kimi-k3-evaluation.md) — canonical eval source superseding the overlapping benchmark table here.

## Coverage limits

- Remote GIF demonstrations, top-1/KLD plots, benchmark images, Hugging Face files, and linked llama.cpp PRs were not independently inspected; benchmark, hardware, and quant-fidelity numbers are source-reported Unsloth claims, not independently verified.
- The source's recommendation link names shard `Kimi-K3-UD-IQ1_S-00001-of-00015.gguf` while its run example names `Kimi-K3-UD-IQ1_S-00001-of-00014.gguf`; follow the actual downloaded shard layout.
- No local attachments were referenced by the source.

[^kimi-k3]: Kimi K3 - How to Run Locally — `../raw/unsloth/models/kimi-k3.md`, 2.8T/104B identity and strongest-open-model claim, native vision and 1M context, MXFP4 layout and 1.56TB full-precision size, 594GB 1-bit and 861.3GB 2-bit size/accuracy claims, 610GB–1.6TB hardware table, UD size/KLD/PPL/top-1 table and community-quant contrast, Q8-lossless analysis, llama.cpp fork and vision-tower notes, thinking-only reasoning and sampling tables, Unsloth Desktop and llama.cpp install/download/run commands, B200 throughput note, and coding/agentic/vision benchmark table.
[^kimi-k3-dspark]: Kimi K3 DSpark speculator — `../raw/Kimi-K3-DSpark.md`.
