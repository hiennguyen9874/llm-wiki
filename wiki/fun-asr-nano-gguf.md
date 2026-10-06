---
type: Concept
title: Fun-ASR-Nano GGUF
description: GGUF packaging of Fun-ASR-Nano (SenseVoice SAN-M encoder plus Qwen3-0.6B decoder) for the zero-Python FunASR llama.cpp CPU/edge runtime, with encoder/LLM/VAD files, quantization CER tiers, CLI usage, and deployment pointers.
tags: [ml, asr, speech-recognition, gguf, llama-cpp, cpu, edge, chinese]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: fun-asr-nano-gguf-card
    resource: ../raw/Fun-ASR-Nano-GGUF.md
    kind: documentation
    title: Fun-ASR-Nano GGUF model card
---

Fun-ASR-Nano GGUF is a GGUF build of Fun-ASR-Nano (SenseVoice SAN-M encoder plus adaptor plus Qwen3-0.6B LLM decoder) for the zero-Python, CPU/edge FunASR llama.cpp runtime, distributed as a separate encoder file plus a choice of three quantized LLM decoder files and run through the single self-contained `llama-funasr-cli` binary (**Reported**).[^fun-asr-nano-gguf-card]

## Architecture and runtime

- Card title is `Fun-ASR-Nano · GGUF (FunASR llama.cpp runtime)`; the described system pairs a SenseVoice SAN-M encoder plus adaptor with a Qwen3-0.6B LLM decoder, presented as the accuracy-leader (LLM decoder) option in a single C++ binary (**Reported**).[^fun-asr-nano-gguf-card]
- Frontmatter declares `license: apache-2.0`, `language: [zh, en]`, `library_name: gguf`, `pipeline_tag: automatic-speech-recognition`, and tags including `automatic-speech-recognition`, `asr`, `fun-asr`, `funasr`, `qwen3`, `llama.cpp`, `ggml`, `cpu`, `chinese`, and `arxiv:2407.04051` (**Observed** by static inspection).[^fun-asr-nano-gguf-card]
- Runtime target is the FunASR llama.cpp runtime — a whisper.cpp-style, single self-contained binary for CPU/edge with no Python and no build — at `runtime/llama.cpp` in the FunASR repositories (FunAudioLLM and ModelScope mirrors) (**Reported**).[^fun-asr-nano-gguf-card]
- Source checkpoint is [FunAudioLLM/Fun-ASR-Nano-2512](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512); the GGUF card links back to it as its source model (**Reported**).[^fun-asr-nano-gguf-card]
- Prebuilt binaries for Linux, macOS, and Windows are published under GitHub Releases tag `runtime-llamacpp-v*`; deployment guide and qualified benchmarks are at `funasr.com/deploy/llama-cpp` (**Reported**).[^fun-asr-nano-gguf-card]

## Files

- `funasr-encoder-f16.gguf` (470 MB): audio encoder plus adaptor in f16; pair any LLM tier with this file (**Reported**).[^fun-asr-nano-gguf-card]
- `qwen3-0.6b-q4km.gguf` (484 MB): LLM decoder, smallest option (Q4_K_M) (**Reported**).[^fun-asr-nano-gguf-card]
- `qwen3-0.6b-q5km.gguf` (551 MB): LLM decoder, best-accuracy option (Q5_K_M); listed in the quantization tier table but absent from the card's `Files` table (**Reported**, with the table-scope gap **Observed** by static inspection).[^fun-asr-nano-gguf-card]
- `qwen3-0.6b-q8_0.gguf` (805 MB): LLM decoder, card-marked recommended option (Q8_0) (**Reported**).[^fun-asr-nano-gguf-card]
- `fsmn-vad.gguf` (size unstated): VAD model passed via `--vad` in both CLI examples but absent from the card's `Files` table (**Reported**, with the gap **Observed** by static inspection).[^fun-asr-nano-gguf-card]

## LLM quantization tiers

- All three LLM tiers fall within 0.1% CER on the 184-file micro-CER comparison; recommended picks are Q4_K_M (smallest) or Q5_K_M (best accuracy) (**Reported**).[^fun-asr-nano-gguf-card]

| LLM file | size | CER (lower is better) | speed | card note |
| --- | ---: | ---: | ---: | --- |
| `qwen3-0.6b-q4km.gguf` | 484 MB | 8.35% | 6.1x | smallest |
| `qwen3-0.6b-q5km.gguf` | 551 MB | 8.25% | 5.7x | best accuracy |
| `qwen3-0.6b-q8_0.gguf` | 805 MB | 8.30% | 6.0x | (Files table marks recommended) |

Table values are source-reported measurements as listed in the card's quantization table (**Reported**).[^fun-asr-nano-gguf-card]

## Usage

- Fetch then run (no Python, no build): `bash download-funasr-model.sh nano ./gguf`, then `llama-funasr-cli --enc ./gguf/funasr-encoder-f16.gguf -m ./gguf/qwen3-0.6b-q8_0.gguf --vad ./gguf/fsmn-vad.gguf -a audio.wav` (**Reported**).[^fun-asr-nano-gguf-card]
- Minimal form needs both the encoder and the LLM GGUF: `llama-funasr-cli --enc funasr-encoder-f16.gguf -m qwen3-0.6b-q8_0.gguf -a audio.wav --vad fsmn-vad.gguf` (**Reported**).[^fun-asr-nano-gguf-card]
- CPU claim: 8.30% CER on the 184-clip Mandarin benchmark (versus whisper.cpp 22-31%) (**Reported**).[^fun-asr-nano-gguf-card]

## Relationships

- Depends on [Fun-ASR-Nano-2512](fun-asr-nano-2512.md): this GGUF package is converted from that 800M-parameter Chinese/English/Japanese checkpoint, which documents the Python FunASR inference path, dialect/accent coverage, and family benchmark tables (**Synthesis**).[^fun-asr-nano-gguf-card]

## Coverage and limits

- Source inspected statically only; no binaries downloaded, no GGUFs loaded, no CLI executed, and no CER or speed figures reproduced (**Synthesis**).[^fun-asr-nano-gguf-card]
- Linked but unfetched and not in `raw/`: FunASR `runtime/llama.cpp` code, prebuilt binaries (Releases tag `runtime-llamacpp-v*`), `download-funasr-model.sh`, the `funasr.com/deploy/llama-cpp` guide and qualified benchmarks, the `funasr-encoder-f16.gguf` / LLM / `fsmn-vad.gguf` weight files, `audio.wav`, the Hugging Face source-model repository, and arXiv 2407.04051 (**Synthesis**).[^fun-asr-nano-gguf-card]
- All architecture, file-size, CER, speed, and CPU/edge deployment claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `ml` domain rule (**Synthesis**).[^fun-asr-nano-gguf-card]

[^fun-asr-nano-gguf-card]: [Fun-ASR-Nano GGUF model card](../raw/Fun-ASR-Nano-GGUF.md) — locators: frontmatter (`license`, `language`, `library_name`, `tags`, `pipeline_tag`, `arxiv:2407.04051` tag); title heading (SenseVoice SAN-M encoder + adaptor + Qwen3-0.6B LLM decoder, accuracy-leader, single C++ binary); section `LLM quantization` (three-tier table: file names, sizes 484/551/805 MB, CER 8.35/8.25/8.30%, speeds 6.1/5.7/6.0x, within-0.1%-CER micro-CER note, `funasr-encoder-f16.gguf` 470 MB pairing note, q4_K_M/q5_K_M recommendation); section `Get it running` (llama.cpp runtime description, prebuilt-binaries Releases `runtime-llamacpp-v*` link, `funasr.com/deploy/llama-cpp` guide link, `bash download-funasr-model.sh nano ./gguf` plus `llama-funasr-cli --enc ... -m ... --vad ... -a audio.wav` fence); section `Files` (3-row table: encoder 470 MB, q8_0 805 MB recommended, q4km 484 MB; q5km and `fsmn-vad.gguf` absent); section `Usage` (encoder-plus-LLM fence, 8.30% CER 184-clip Mandarin vs whisper.cpp 22-31% sentence); section `Links` (FunASR `runtime/llama.cpp` build links, `FunAudioLLM/Fun-ASR-Nano-2512` source-model link).
