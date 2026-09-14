---
type: Concept
title: GLM-5.3 Local Deployment
description: Run Z.ai 744B (40B active) GLM-5.3 locally via Unsloth Dynamic GGUFs with hardware, sampling, reasoning, llama.cpp, and benchmark guidance.
tags: [glm, z-ai, unsloth, gguf, llama-cpp, local-inference, quantization, reasoning]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: glm53
    resource: ../raw/unsloth/models/glm-5.3.md
    title: 'GLM-5.3 - How to Run Locally'
---

GLM-5.3 is Z.ai's 744B-parameter (40B active) open model, presented as the strongest open model as of Aug 2026 with SOTA on Terminal Bench 3.0 and Agents' Last Exam; Unsloth publishes Dynamic 1- to 8-bit GGUFs and day-zero llama.cpp plus Unsloth Desktop run paths for 223GB+ local setups[^glm53].

## Model identity

- Vendor Z.ai; 744B total / 40B active[^glm53].
- Same base model and architecture/size as GLM-5.2; source attributes every gain to post-training[^glm53].
- Presented as strongest open model to date as of Aug 2026, achieving SOTA on Terminal Bench 3.0 and Agents' Last Exam[^glm53].
- Maximum context window `1,048,576`[^glm53].
- Related smaller model [GLM-5.3-Flash Local Deployment](glm-5.3-flash.md) is a distinct 320B (18B active) model with its own deployment page.

## Reasoning and sampling settings

- Three thinking modes: Low, High, and Max; use Max Thinking for complicated coding tasks; Unsloth Desktop exposes a Low/High/Max toggle[^glm53].
- Thinking cannot be disabled; maximum reasoning is default; `reasoning_effort` can be `low`, `high`, or `max`[^glm53].
- Default recommendation for most tasks: `temperature = 1.0`, `top_p = 0.95`[^glm53].
- Long agentic tasks: `temperature = 1.0`, `top_p = 1.0`[^glm53].
- `clear_thinking` is false by default and source recommends true, especially for multi-turn chat to remove prior-turn reasoning[^glm53].
- llama.cpp / server examples pass reasoning effort via `--chat-template-kwargs '{"reasoning_effort":"low"}'` and multi-turn via `--chat-template-kwargs '{"reasoning_effort":"max","clear_thinking":true}'`[^glm53].

## Chat-template fix

- Source reports GLM uses `.{id}.` notation unsupported by many engines; Unsloth edited it to `[id]` Python-list-indexing syntax[^glm53].
- Evidence pointer is the linked Unsloth `GLM-5.3` commit `05cd131`; commit contents were not independently inspected[^glm53].

## Hardware requirements

Total memory including RAM + VRAM, or unified memory; keep total available memory comfortably above the quantized file size[^glm53]:

| 1-bit | 2-bit | 3-bit | 4-bit | 6-bit | 8-bit |
| --- | --- | --- | --- | --- | --- |
| 223GB | 245GB | 290-360GB | 372-475GB | 570GB | 810GB |

- 2-bit dynamic quant `UD-IQ2_M` uses 239GB disk and works on 256GB RAM devices such as 2x NVIDIA DGX Spark or Mac Studio[^glm53].
- 1-bit quant fits 223GB RAM; 8-bit requires 810GB RAM[^glm53].
- Tutorial default is `UD-IQ2_M` for best balance of accessibility and accuracy[^glm53].

## Unsloth dynamic quantization

Source summaries are approximate top-1 accuracy versus BF16: Dynamic 1-bit reaches ~76% while ~85% smaller; Dynamic 2-bit reaches ~81% while ~83% smaller[^glm53].

Full reported GGUF table[^glm53]:

| Quant | GB | Top-1 % | Mean KLD | 99.9% KLD | PPL |
| --- | --- | --- | --- | --- | --- |
| UD-IQ1_S | 216.7 | 72.56 | 0.687991 | 9.104 | 4.6130 |
| UD-IQ1_M | 228.5 | 75.64 | 0.565455 | 8.595 | 4.1410 |
| UD-IQ2_M | 238.6 | 78.53 | 0.453992 | 7.717 | 3.7433 |
| UD-Q2_K_XL | 253.9 | 80.93 | 0.374219 | 7.076 | 3.5048 |
| UD-IQ3_XXS | 281.7 | 84.15 | 0.272796 | 6.252 | 3.2482 |
| UD-Q3_K_XL | 343.0 | 88.86 | 0.141406 | 4.127 | 2.9107 |
| UD-IQ4_XS | 365.3 | 90.59 | 0.101496 | 3.177 | 2.8460 |
| UD-Q4_K_XL | 467.3 | 94.29 | 0.036922 | 1.309 | 2.7006 |
| UD-Q5_K_XL | 562.5 | 95.82 | 0.019728 | 0.786 | 2.6842 |
| UD-Q6_K_XL | 684.4 | 96.59 | 0.013257 | 0.534 | 2.6771 |

- Source's KLD analysis says `Q4_K_XL` and `Q5_K_XL` are very close to baseline, so aim for those when memory allows[^glm53].

## Local run paths

- Hugging Face artifact: `unsloth/GLM-5.3-GGUF`[^glm53].
- Unsloth Desktop: install app or `curl -fsSL https://unsloth.ai/install.sh | sh` on macOS/Linux/WSL and `irm https://unsloth.ai/install.ps1 | iex` on PowerShell; search Model hub / Chat for GLM-5.3, download chosen quant, run with auto-set inference parameters; serve via `unsloth run --model unsloth/GLM-5.3-GGUF:UD-IQ2_M` with `llama-server` runtime flags[^glm53].
- llama.cpp: build from `https://github.com/ggml-org/llama.cpp` with `-DGGML_CUDA=ON` for CUDA or `OFF` for CPU-only / Apple Metal default; build targets `llama-cli llama-mtmd-cli llama-server llama-gguf-split`[^glm53].
- Direct llama.cpp run: `export LLAMA_CACHE="unsloth/GLM-5.3-GGUF"` then `./llama.cpp/llama-cli -hf unsloth/GLM-5.3-GGUF:UD-IQ2_M --temp 1.0 --top-p 0.95 --min-p 0.01`; source warns this download path can be very slow[^glm53].
- Faster manual download after `pip install huggingface_hub`: `hf download unsloth/GLM-5.3-GGUF --local-dir unsloth/GLM-5.3-GGUF --include "*UD-IQ2_M*"` or `"*UD-IQ1_S*"` for 1-bit; then run `llama-cli --model` on shard `UD-IQ2_M/GLM-5.3-UD-IQ2_M-00001-of-00006.gguf` or `UD-IQ1_S/GLM-5.3-UD-IQ1_S-00001-of-00006.gguf` with `--temp 1.0 --top-p 0.95 --min-p 0.01`[^glm53].
- Long context via KV-cache quantization: supported dtypes `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`; default `f16`; source says `q4_1` uses ~5 bits per weight for ~3.2x longer context; example adds `--cache-type-k q4_1 --cache-type-v q4_1 --jinja --chat-template-kwargs '{"reasoning_effort":"max"}'`[^glm53].
- Source reports a 1-bit `UD-IQ1_S` Snake-game generation demo worked well; demonstration media was not independently inspected[^glm53].

## Source-reported benchmarks

Selected GLM-5.3 scores; comparison columns in source cover GLM-5.2, Kimi K3, DeepSeek-V4 Pro-0813, Qwen3.8-Max, Opus 4.8, Fable 5 with fallback, and GPT-5.6 Sol[^glm53]:

- Coding: Terminal Bench 2.1 88.2; Terminal Bench 3.0 28.3; DeepSWE v1.1 66.9; NL2Repo 58.0; ProgramBench Almost Solved 19.0; FrontierSWE 78.1; SWE-Marathon v1.1 42.5; PostTrainBench 39.8[^glm53].
- Cyber: CyberGym 84.5; ExploitGym 2h/6h 105/130; ExploitBench 54.4[^glm53].
- Agentic: Toolathlon Verified 73.0; AutomationBench v1.0.6 48.2; Agents' Last Exam ALE-CLI 28.5; HLE w/ Tools 62.5; GDPval-AA v2 1769[^glm53].

## Relationships

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — GLM-5.3 UD-IQ1_S through UD-Q6_K_XL instances of Unsloth per-layer dynamic post-training quantization.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — top-1 accuracy, mean KLD, KLD 99.9%, and PPL figures used here are the same fidelity signals used to judge quantized models.

## Coverage limits

- Remote images, benchmark plots, GIF demonstrations, Hugging Face files, and linked llama.cpp commits were not independently inspected; benchmark, hardware, and quant-fidelity numbers are source-reported Unsloth claims, not independently verified.
- No local attachments were referenced by the source.

[^glm53]: GLM-5.3 - How to Run Locally — `../raw/unsloth/models/glm-5.3.md`, 744B/40B identity and strongest-open-model claim, same-base-as-GLM-5.2 post-training claim, 1M context, Low/High/Max reasoning and sampling tables, 223GB-810GB hardware table, UD size/accuracy/KLD/PPL table, chat-template `.{id}.` to `[id]` fix, Unsloth Desktop and llama.cpp install/download/run commands, KV-cache quantization guidance, and coding/cyber/agentic benchmark table.
