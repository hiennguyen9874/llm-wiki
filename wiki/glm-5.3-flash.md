---
type: Concept
title: GLM-5.3-Flash Local Deployment
description: Run Z.ai 320B (18B active) multimodal GLM-5.3-Flash locally via Unsloth GGUFs with hardware, sampling, reasoning, MTP, and benchmark guidance.
tags: [glm, z-ai, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: glm53-flash
    resource: ../raw/unsloth/models/glm-5.3-flash.md
    title: 'GLM-5.3-Flash: How to Run Locally'
---

GLM-5.3-Flash, also known as `ox-alpha`, is Z.ai's 320B-parameter (18B active) multimodal open model, presented as smaller than GLM-5.3, outperforming GLM-5.2, and competitive with Claude Opus 4.8 on coding and agentic benchmarks; Unsloth publishes dynamic 1- to 8-bit GGUFs and day-zero llama.cpp plus Unsloth Desktop run paths for 100GB+ local setups[^glm53-flash].

## Model identity

- Alias `ox-alpha`; vendor Z.ai; 320B total / 18B active; multimodal open model[^glm53-flash].
- Positioned as smaller version of GLM-5.3 and successor improving over GLM-5.2; source claims rivalry with Claude Opus 4.8 on coding and agentic benchmarks[^glm53-flash].
- Trained on 30T tokens on a newly trained base model; hybrid sparse and linear attention architecture is claimed to lower long-context serving costs without sacrificing accuracy[^glm53-flash].
- Maximum context window `1,048,576`[^glm53-flash].

## Reasoning and sampling settings

- Three thinking modes: Low, High, and Max; Max is default; `reasoning_effort` can be `low`, `high`, or `max`; Unsloth Desktop exposes Low/High/Max toggle[^glm53-flash].
- Default recommendation for most tasks: `temperature = 1.0`, `top_p = 0.95`[^glm53-flash].
- DeepSWE recommendation: `temperature = 0.95`, `top_p = 1.0`[^glm53-flash].
- llama.cpp example passes reasoning effort via `--chat-template-kwargs '{"reasoning_effort":"max"}'`[^glm53-flash].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory[^glm53-flash]:

| 1-bit | 2-bit | 3-bit | 4-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- |
| 100 GB | 115 GB | 128-150 GB | 162-210 GB | 350 GB | 650 GB |

- 1-bit fits ~100GB RAM; 3-bit fits 128GB devices such as Mac or NVIDIA DGX Spark; demos use 3-bit `UD-IQ3_XXS` for 128GB[^glm53-flash].
- Source also states 1-bit model runs on 102GB RAM/VRAM and BF16 is 642GB in one summary versus 641.64GB / 650GB elsewhere; treat exact BF16 footprint as approximately 642-650GB[^glm53-flash].

## Unsloth dynamic quantization

Source-reported retention is top-1% accuracy versus BF16[^glm53-flash]:

- 1-bit `UD-IQ1_S` 93.09GB: 70.89% top-1%, 85% smaller than BF16[^glm53-flash].
- 2-bit `UD-Q2_K_XL` 108.72GB: 78.34% top-1%, 83% smaller[^glm53-flash].
- 3-bit `UD-IQ3_XXS` 120.37GB: 81.63% top-1%, 81% smaller[^glm53-flash].
- 4-bit `UD-Q4_K_XL` 199.71GB: 92.22% top-1%, 69% smaller[^glm53-flash].

Full reported GGUF table:

| Quant | Size GB | Top-1 acc | Mean KLD | KLD 99.9% |
| --- | --- | --- | --- | --- |
| UD-IQ1_S | 93.09 | 70.89% | 0.669714 | 9.1658 |
| UD-IQ1_M | 97.58 | 73.06% | 0.572413 | 8.5069 |
| UD-IQ2_XXS | 101.84 | 76.30% | 0.450148 | 7.5764 |
| UD-Q2_K_XL | 108.72 | 78.34% | 0.380134 | 6.8412 |
| UD-IQ3_XXS | 120.37 | 81.63% | 0.283772 | 5.9611 |
| UD-Q3_K_XL | 147.54 | 86.25% | 0.159697 | 4.0281 |
| UD-IQ4_XS | 156.82 | 88.18% | 0.116652 | 3.1014 |
| UD-Q4_K_XL | 199.71 | 92.22% | 0.049294 | 1.4894 |
| UD-Q5_K_XL | 240.31 | 94.35% | 0.027052 | 0.8696 |
| UD-Q6_K_XL | 291.83 | 95.23% | 0.019007 | 0.6267 |

## Faster inference and MTP support

- Sep 4 update adds faster decoding plus bonus MTP support via Unsloth day-zero llama.cpp PR, claimed up to 3.3x faster inference at long context; works out of the box in Unsloth Desktop with no extra MTP files, or via the linked llama.cpp guide[^glm53-flash].
- Reported B200 result for `UD-IQ1_S` without MTP: `pp512` ~1122 tok/s; `tg32` 63.1 tok/s; `tg32 @4096` 59.5 tok/s; `tg32 @16384` 58.0 tok/s; `tg32 @65536` 49.0 tok/s, up from baselines especially at long context[^glm53-flash].
- Reported MTP gain: at 4096 prompt, MTP off 58.6 tok/s versus n=2 at 86.5 tok/s, n=3 at 80.2 tok/s, n=5 at 63.7 tok/s; at 16K, MTP off 55.0 tok/s versus n=3 at 77.2 tok/s; source advises stopping around n=2 because more draft tokens can slow inference; shorter contexts still gain up to ~1.6x[^glm53-flash].

## Local run paths

- Hugging Face artifact: `unsloth/GLM-5.3-Flash-GGUF`[^glm53-flash].
- Unsloth Desktop: install app or `curl -fsSL https://unsloth.ai/install.sh | sh` on macOS/Linux/WSL and `irm https://unsloth.ai/install.ps1 | iex` on PowerShell; search Model hub / Chat for GLM-5.3-Flash, download chosen quant, run with auto-set inference parameters; serve via `unsloth run --model unsloth/GLM-5.3-Flash-GGUF:UD-IQ3_XXS` with `llama-server` runtime flags[^glm53-flash].
- llama.cpp: build from `https://github.com/unslothai/llama.cpp` branch `glm5next/upstream` with CUDA on or off and Metal default on Apple; build targets `llama-cli llama-mtmd-cli llama-server llama-gguf-split`; download with `hf download unsloth/GLM-5.3-Flash-GGUF --include "*UD-IQ3_XXS*"`; run `llama-cli` with model shard path, `--temp 1.0 --top-p 0.95`, and `reasoning_effort max` chat-template kwarg[^glm53-flash].

## Source-reported benchmarks

Selected GLM-5.3-Flash scores; comparison columns cover GLM-5.2, DeepSeek-V4-Vision-Exp, Opus 4.8, GPT-5.6 Terra, and Gemini 3.7 Flash in source[^glm53-flash]:

- Coding: Terminal Bench 2.1 84.3; DeepSWE v1.1 63.4; NL2Repo 56.3[^glm53-flash].
- Agentic: Toolathlon Verified 78.4; AutomationBench v1.0.6 48.8; Agents' Last Exam 26.3; HLE w/ Tools 55.3; GDPval-AA v2 1773[^glm53-flash].
- Vision: OfficeQA Pro 62.4; CharXiv Reasoning w/ Tools 89.4; Chartography w/ Tools 78.0; BabyVision 53.4; MVbench 77.8; MMVU 80.5[^glm53-flash].

## Relationships

- Related to [GLM-5.3-Flash Architecture and Evaluation](glm-5.3-flash-architecture.md) — official 320B (18B active) hybrid linear-sparse plus mHC checkpoint, 1M context, IndexPool, base and full benchmark methodology, and Chinese-chip EPD serving context for these local run paths.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — GLM-5.3-Flash UD-IQ1_S through UD-Q6_K_XL instances of Unsloth per-layer dynamic post-training quantization.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — top-1 accuracy, mean KLD, and KLD 99.9% figures used here are the same fidelity signals used to judge quantized models.
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — MTP speedup context for the reported n=2/n=3 draft-token inference gains, although the local run uses llama.cpp/Unsloth rather than vLLM.

## Coverage limits

- Remote images, benchmark plots, GIF demonstrations, Hugging Face files, and linked llama.cpp PRs were not independently inspected; benchmark and throughput numbers are source-reported Unsloth claims, not independently verified.
- No local attachments were referenced by the source.

[^glm53-flash]: GLM-5.3-Flash: How to Run Locally — `../raw/unsloth/models/glm-5.3-flash.md`, model identity and 30T-token hybrid-attention claim, 1M context, Low/High/Max reasoning and sampling tables, 100GB-650GB hardware table, UD quant size/accuracy/KLD table, Sep 4 faster-decoding and MTP tok/s tables, Unsloth Desktop and llama.cpp run commands, and coding/agentic/vision benchmark table.
