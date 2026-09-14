---
type: Concept
title: Unsloth MTP Local Inference
description: Run Gemma 4 and Qwen3.6/3.5 MTP models locally via Unsloth Studio or llama.cpp with draft-token tuning, hardware, and sampling guidance.
tags: [unsloth, mtp, speculative-decoding, llama-cpp, gguf, local-inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T17:00:00Z }
sources:
  - id: mtp-guide
    resource: ../raw/unsloth/models/mtp.md
    title: 'How to Run MTP Models: Multi-Token Prediction Guide'
---

MTP predicts multiple future tokens that the main model verifies in parallel, reducing generation forward passes while keeping only verified tokens; Unsloth packages Gemma 4 and Qwen3.6/3.5 MTP GGUFs for local `llama.cpp` or Unsloth Studio runs with reported GGUF speedups around 1.4x-2.2x at the cost of about 2 GB extra memory headroom[^mtp-guide].

## Mechanism and performance tradeoff

- MTP, or Multi-Token Prediction, generates multiple upcoming tokens per step instead of one token per step, with parallel verification preserving quality[^mtp-guide].
- Reported GGUF speedup is about 1.4x to 2.2x faster generation; dense models such as Gemma-4-31B benefit most at over 1.4x, while gains are smaller on lower-memory-bandwidth devices such as older Macs[^mtp-guide].
- MTP uses more memory than standard inference, so plan for about 2 GB additional RAM/VRAM headroom[^mtp-guide].
- Supported local runtimes in the source are Unsloth Studio UI and llama.cpp[^mtp-guide].

## Draft-token tuning

- Start with `--spec-draft-n-max 2`, but do not assume `2` is optimal because performance is hardware-dependent; try values `1` through `6` and keep whichever is fastest[^mtp-guide].
- Unsloth Studio automatically sets MTP/speculative-decoding settings for the detected hardware, while still allowing manual changes[^mtp-guide].

## Gemma 4 MTP packaging

- Google DeepMind trained MTP separately from the original Gemma 4 models, including QAT variants, and released specific MTP variants under the `assistant` name[^mtp-guide].
- Unsloth reports uploading `mtp-`-prefixed GGUFs to each Gemma 4 repo with 8-bit and 16-bit BF16/F16 precision options; for QAT it applied the same smart 4-bit recovery process used for Gemma 4 QAT quants, so the MTP quants are also smart 4-bit derived[^mtp-guide].
- Gemma 4 MTP is automatically enabled in Unsloth Studio; download only the regular original Gemma 4 GGUF because updated Gemma 4 GGUF packages include the extra MTP file in a separate folder, with no separate assistant GGUF needed[^mtp-guide].
- Only Qwen3.6 still requires a separate MTP GGUF in this packaging scheme[^mtp-guide].
- Gemma 4 MTP checkpoints are linked in the source through the `unsloth/gemma-4` Hugging Face collection[^mtp-guide].
- Reported Gemma 4 QAT with MTP runs 1.5x-2.2x faster[^mtp-guide].

Total memory including RAM + VRAM, or unified memory[^mtp-guide]:

| Gemma 4 variant | 4-bit | 8-bit | BF16 / FP16 |
| --- | --- | --- | --- |
| **E2B** | 5 GB | 6–9 GB | 11 GB |
| **E4B** | 6.5–7 GB | 10–13 GB | 17 GB |
| **12B Unified** | 8–9 GB | 14–15 GB | 26 GB |
| **26B A4B** | 17–18 GB | 29–31 GB | 53 GB |
| **31B** | 18–21 GB | 35–39 GB | 63 GB |

## Qwen MTP packaging

- Qwen directly trained MTP inside Qwen3.6 and Qwen3.5 models, rather than as a separately trained assistant as with Gemma 4[^mtp-guide].
- Named Qwen3.6 MTP GGUFs are `unsloth/Qwen3.6-27B-MTP-GGUF` and `unsloth/Qwen3.6-35B-A3B-MTP-GGUF`[^mtp-guide].
- Reported throughput on an RTX 6000 GPU is 160 tokens/s for Qwen3.6 27B MTP and 240 tokens/s for Qwen3.6 35B-A3B[^mtp-guide].
- The source also lists uploaded MTP GGUFs for the Qwen3.5 family: 0.8B, 2B, 4B, 9B, 27B, 35B-A3B, 122B-A10B, and 397B-A17B[^mtp-guide].
- Llama.cpp MTP performance is described as continually improving, so newer builds may be faster[^mtp-guide].

Total memory including RAM + VRAM, or unified memory[^mtp-guide]:

| Qwen3.6 | 3-bit | 4-bit | 6-bit | 8-bit | BF16 |
| --- | --- | --- | --- | --- | --- |
| **27B** | 16 GB | 19 GB | 25 GB | 31 GB | 56 GB |
| **35B-A3B** | 18 GB | 24 GB | 31 GB | 39 GB | 71 GB |

## Unsloth Studio path

- Install on macOS, Linux, or WSL with `curl -fsSL https://unsloth.ai/install.sh | sh`, or on Windows PowerShell with `irm https://unsloth.ai/install.ps1 | iex`[^mtp-guide].
- Launch with `unsloth studio -H 127.0.0.1 -p 8888`, then open `http://127.0.0.1:8888` in a browser[^mtp-guide].
- On first launch create a password, then use the Chat tab to search for Qwen3.6 MTP or Gemma 4, download the desired model and quant[^mtp-guide].
- For Gemma 4 download only the regular original GGUF; for Qwen3.6 download the separate MTP GGUF[^mtp-guide].
- Inference, MTP, speculative-decoding settings, context length, chat template, and related options are auto-set but remain manually editable in the right sidebar[^mtp-guide].

## llama.cpp path

- Install the latest `llama.cpp` build referenced in the source; for no GPU or CPU-only inference change `-DGGML_CUDA=ON` to `-DGGML_CUDA=OFF`, while Apple Mac/Metal devices use `-DGGML_CUDA=OFF` with Metal enabled by default[^mtp-guide].
- Reference build sequence installs build dependencies, clones `https://github.com/ggml-org/llama.cpp`, configures with `-DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON`, builds `llama-cli llama-mtmd-cli llama-server llama-gguf-split`, and copies `llama-*` binaries[^mtp-guide].
- Remote-model runs use `export LLAMA_CACHE="folder"` to pin the download location and support up to 256K context length; `Q4_K_XL`-style suffixes select the quant[^mtp-guide].

Gemma 4 remote examples use the 12B repo as a placeholder and require changing the model name for other sizes[^mtp-guide]:

```bash
export LLAMA_CACHE="unsloth/gemma-4-12b-it-GGUF"
./llama.cpp/llama-cli \
    -hf unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

Non-thinking Gemma 4 adds[^mtp-guide]:

```bash
--chat-template-kwargs '{"enable_thinking":false}'
```

Qwen3.6 27B thinking-mode example for general tasks[^mtp-guide]:

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

For precise coding tasks change to `temperature=0.6`[^mtp-guide]. Qwen non-thinking server example for general tasks[^mtp-guide]:

```bash
export LLAMA_CACHE="unsloth/Qwen3.6-27B-MTP-GGUF"
./llama.cpp/llama-server \
    -hf unsloth/Qwen3.6-27B-MTP-GGUF:UD-Q4_K_XL \
    --temp 0.7 \
    --top-p 0.8 \
    --top-k 20 \
    --presence-penalty 1.5 \
    --min-p 0.00 \
    --spec-type draft-mtp --spec-draft-n-max 2 \
    --chat-template-kwargs '{"enable_thinking":false}'
```

Minimal Gemma-4-31B server form from the source uses the 8-bit quant[^mtp-guide]:

```bash
llama-server \
    -hf unsloth/gemma-4-31B-it-GGUF \
    --spec-type draft-mtp \
    --spec-draft-n-max 4
```

Manual quant download uses `pip install huggingface_hub hf_transfer`, prefers at least dynamic 2-bit `UD-Q2_K_XL` for size/accuracy balance, and links a Hugging Face Hub/XET debugging page when downloads stall[^mtp-guide]:

```bash
hf download unsloth/gemma-4-12B-it-qat-GGUF \
    --local-dir unsloth/gemma-4-12B-it-qat-GGUF \
    --include "*mmproj-F16*" \
    --include "mtp-*" \
    --include "*UD-Q4_K_XL*"
```

```bash
hf download unsloth/Qwen3.6-27B-MTP-GGUF \
    --local-dir unsloth/Qwen3.6-27B-MTP-GGUF \
    --include "*mmproj-F16*" \
    --include "*UD-Q4_K_XL*"
```

Local-file Gemma 4 run[^mtp-guide]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/gemma-4-12B-it-qat-GGUF/gemma-4-12B-it-qat-UD-Q4_K_XL.gguf \
    --mmproj unsloth/gemma-4-12B-it-qat-GGUF/mmproj-F16.gguf \
    --model-draft unsloth/gemma-4-12B-it-qat-GGUF/mtp-gemma-4-12B-it.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

Local-file Qwen3.6 run[^mtp-guide]:

```bash
./llama.cpp/llama-cli \
    --model unsloth/Qwen3.6-27B-MTP-GGUF/Qwen3.6-27B-UD-Q4_K_XL.gguf \
    --mmproj unsloth/Qwen3.6-27B-MTP-GGUF/mmproj-F16.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --min-p 0.00 \
    --top-k 20 \
    --spec-type draft-mtp --spec-draft-n-max 2
```

Gemma-4 `llama-server` deployment example[^mtp-guide]:

```bash
./llama.cpp/llama-server \
    --model unsloth/gemma-4-12B-it-qat-GGUF/gemma-4-12B-it-qat-UD-Q4_K_XL.gguf \
    --mmproj unsloth/gemma-4-12B-it-qat-GGUF/mmproj-F16.gguf \
    --model-draft unsloth/gemma-4-12B-it-qat-GGUF/mtp-gemma-4-12B-it.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --alias "unsloth/gemma-4-12b-it-qat-GGUF" \
    --port 8001 \
    --chat-template-kwargs '{"enable_thinking":true}'
```

## Relationships

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — `UD-Q4_K_XL` and `UD-Q2_K_XL` quants named here are instances of Unsloth per-layer dynamic GGUF quantization.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — vLLM native `method: mtp` path versus the llama.cpp `--spec-type draft-mtp` path used here; both cover Gemma 4 assistant checkpoints.
- Related to [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md) — Qwen4-architecture shared-MTP packaging with `--spec-draft-n-max 5` example and 1.3-1.7x speedup claim, extending the Gemma 4 and Qwen3.6 MTP pattern.
- Related to [GLM-5.3-Flash Local Deployment](glm-5.3-flash.md) — another Unsloth local run reporting MTP draft-token tuning and tok/s gains, here with the general `--spec-draft-n-max 2` starting point and 1-through-6 sweep.

## Coverage limits

- Remote benchmark images, throughput plots, GIF demonstrations, Hugging Face collections/files, and linked Gemma 4, Qwen3.6/3.5, Studio, GGUF, troubleshooting, and llama.cpp PR pages were not independently inspected; speedup and tok/s figures are source-reported claims, not independently verified.
- The source introduction names Qwen3.8 but links the Qwen3.6 model doc while the body covers Qwen3.6/3.5; Qwen3.8-Flash-Next MTP detail is compiled separately in [Qwen3.8-Flash-Next Local Deployment](qwen3.8-next.md).
- No local attachments were referenced by the source.

[^mtp-guide]: How to Run MTP Models: Multi-Token Prediction Guide — `../raw/unsloth/models/mtp.md`, MTP verify-in-parallel mechanism, 1.4x-2.2x GGUF and 1.5x-2.2x Gemma 4 QAT speedup claims, 2 GB extra-memory note, `--spec-draft-n-max 2` starting point with 1-through-6 sweep, Gemma 4 separate-assistant training and bundled `mtp-` packaging with hardware table, Qwen built-in MTP packaging with 160/240 tok/s RTX 6000 claims and hardware table plus Qwen3.5 family list, Unsloth Studio install/launch/download/run steps, and llama.cpp build plus thinking/non-thinking, manual-download, local-file, and server commands.
