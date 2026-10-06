---
type: Concept
title: OmniVoice GGUF
description: GGUF packaging of OmniVoice for omnivoice.cpp with base-plus-tokenizer file pairs, four quantization variants, backend selection, and a non-uniform tokenizer quantization policy.
tags: [tts, gguf, voice-cloning, zero-shot, edge-deployment, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: omnivoice-gguf-card
    resource: ../raw/OmniVoice-GGUF.md
    kind: documentation
    title: OmniVoice GGUF model card
---

OmniVoice GGUF is a GGUF conversion of the OmniVoice zero-shot TTS weights for [omnivoice.cpp](https://github.com/ServeurpersoCom/omnivoice.cpp), a C++17/GGML port of OmniVoice, distributed as a paired base-LM file plus a tokenizer/codec file across four quantization variants with a recommended Q8_0 default, multi-backend GPU/CPU execution, and CC-BY-NC non-commercial terms inherited from the upstream weights (**Reported**).[^omnivoice-gguf-card]

## Package identity and runtime

- Card title is `OmniVoice GGUF`; the weights target `omnivoice.cpp`, described as a C++17/GGML port of OmniVoice (`k2-fsa/OmniVoice`); the system is characterized as multilingual zero-shot TTS covering 646 languages at 24 kHz mono, running on CPU, CUDA, ROCm, Metal, and Vulkan (**Reported**).[^omnivoice-gguf-card]
- Frontmatter declares `license: cc-by-nc-4.0`, `library_name: gguf`, `pipeline_tag: text-to-speech`, tags `tts`, `text-to-speech`, `voice-cloning`, `voice-design`, `ggml`, `gguf`, `omnivoice`, `cpp`, an 11-code frontmatter `language` list (en, fr, de, es, it, pt, zh, ja, ko, ar, ru), and `base_model: k2-fsa/OmniVoice` (**Observed** by static inspection).[^omnivoice-gguf-card]
- The 646-language figure here is more precise than the upstream card's "600+" framing; both describe the same upstream model line at different precision, so no contradiction is recorded (**Synthesis**).[^omnivoice-gguf-card]

## Files and variants

- The two GGUFs load together: `omnivoice-base-{variant}.gguf` carries the Qwen3 0.6B backbone (text to tokens) and `omnivoice-tokenizer-{variant}.gguf` carries the HuBERT plus DAC plus RVQ codec (tokens to and from 24 kHz audio) (**Reported**).[^omnivoice-gguf-card]

| Variant | Base size | Tokenizer size | Card-marked use case |
| --- | ---: | ---: | --- |
| F32 | 2.46 GB | 734 MB | reference, debug, conversion |
| BF16 | 1.23 GB | 373 MB | source faithful, max precision |
| Q8_0 | 656 MB | 289 MB | recommended default |
| Q4_K_M | 407 MB | 252 MB | lowest VRAM |

Table values are card-reported file sizes and use-case labels (**Reported**).[^omnivoice-gguf-card]

## Usage

- Build the runtime, fetch the recommended pair, then run the example scripts: `git clone --recurse-submodules https://github.com/ServeurpersoCom/omnivoice.cpp.git`, `./buildcuda.sh`, `huggingface-cli download Serveurperso/OmniVoice-GGUF omnivoice-base-Q8_0.gguf omnivoice-tokenizer-Q8_0.gguf --local-dir models`, then `./tts.sh` (voice design to `tts.wav`) and `./clone.sh` (voice cloning to `clone.wav`) from `examples/` (**Reported**).[^omnivoice-gguf-card]

## Backends

- Set `GGML_BACKEND` to force a device; otherwise the runtime picks the best available backend (**Reported**).[^omnivoice-gguf-card]

| Value | Target |
| --- | --- |
| `CUDA0` | NVIDIA GPU, fastest path on Ada / Blackwell |
| `Vulkan0` | Cross-vendor GPU (AMD / Intel / NVIDIA) |
| `Metal` | Apple Silicon GPU |
| `CPU` | CPU fallback, x86 variant auto selected |

(**Reported**).[^omnivoice-gguf-card]

## Quantization policy

- Tokenizer GGUFs are not uniform quants; three categories get dedicated treatment across all variants: RVQ codebooks, `fc`, `fc2`, `project_in` / `project_out` stay F32; Snake activation alpha stays F32; convolution kernels with non-alignable rows (K=7,3,1) use F16 in the Q* variants (**Reported**).[^omnivoice-gguf-card]
- The card states the same fallback as llama.cpp `tensor_type_fallback`: F16 has no block size and matches the runtime target dtype on every backend (**Reported**).[^omnivoice-gguf-card]
- The base LM (Qwen3 0.6B, hidden size 1024) has all dimensions divisible by 256, so the fallback never triggers there and the LM follows standard llama.cpp K-quant across variants (**Reported**).[^omnivoice-gguf-card]

## Licensing

- Upstream weights (OmniVoice by Xiaomi / k2-fsa): CC-BY-NC 4.0; upstream code: Apache 2.0; audio codec (Higgs Audio v2, `bosonai/higgs-audio-v2-tokenizer`): Apache 2.0; GGUF tooling (`omnivoice.cpp`): MIT (**Reported**).[^omnivoice-gguf-card]
- The upstream code is Apache 2.0 but the pre-trained weights are CC-BY-NC because of training-data constraints; these GGUF files are conversions of those weights and carry the same non-commercial terms (**Reported**).[^omnivoice-gguf-card]

## Relationships

- Depends on [OmniVoice](omnivoice.md): that concept covers the upstream massively multilingual zero-shot TTS model (600+ languages, diffusion-LM architecture, cloning plus attribute voice design, 0.025 RTF), while this concept covers only its third-party GGUF conversion and `omnivoice.cpp` runtime packaging; no independent acoustic claim is asserted here (**Synthesis**).[^omnivoice-gguf-card]
- Uses Higgs Audio v2 codec lineage: the card attributes the audio codec to Higgs Audio v2 (`bosonai/higgs-audio-v2-tokenizer`) under Apache 2.0, which places this tokenizer/codec file in the same codec family as [Higgs TTS 3](higgs-tts-3-4b.md); the exact code-sharing extent is unstated in this source (**Synthesis**).[^omnivoice-gguf-card]
- Distinct runtime from the [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) `OmniVoice-GGUF` catalog row (`omnivoice` family, BF16 + F16 + Q8, CC-BY-NC): that row targets the audio.cpp runtime, while this concept targets the separate `omnivoice.cpp` runtime; no shared weight file is asserted (**Synthesis**).[^omnivoice-gguf-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no build script executed, no GGUF downloaded or loaded, and no size, backend-selection, quantization-fallback, or audio-quality claim reproduced (**Synthesis**).[^omnivoice-gguf-card]
- Linked but unfetched and not in `raw/`: the `omnivoice.cpp` repository and submodules, `buildcuda.sh`, the `Serveurperso/OmniVoice-GGUF` weight files, the `examples/tts.sh` and `clone.sh` scripts, the upstream `k2-fsa/OmniVoice` checkpoint, and the Higgs Audio v2 tokenizer repository (**Synthesis**).[^omnivoice-gguf-card]
- All architecture, file-size, backend, quantization, and license claims are source assertions without independent verification in this wiki; release, precision, and backend figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^omnivoice-gguf-card]

[^omnivoice-gguf-card]: [OmniVoice GGUF model card](../raw/OmniVoice-GGUF.md) — locators: frontmatter (`license`, `license_link`, `library_name: gguf`, `pipeline_tag: text-to-speech`, `tags`, 11-code `language` list, `base_model: k2-fsa/OmniVoice`); intro paragraph (omnivoice.cpp C++17/GGML port, multilingual zero-shot TTS, 646 languages, 24 kHz mono, CPU/CUDA/ROCm/Metal/Vulkan); `## Files` section (paired base plus tokenizer file pattern, Qwen3 0.6B text-to-tokens and HuBERT+DAC+RVQ tokens-audio roles, four-row variant table with sizes and use cases); `## Quick start` fence (clone `--recurse-submodules`, `./buildcuda.sh`, `huggingface-cli download` of both Q8_0 files, `examples/` `tts.sh`/`clone.sh` to `tts.wav`/`clone.wav`); `## Backends` section (`GGML_BACKEND` plus four-row CUDA0/Vulkan0/Metal/CPU table); `## Quantization policy` section (three-row F32/F16 tokenizer table, llama.cpp `tensor_type_fallback` paragraph, Qwen3-0.6B hidden-1024 divisible-by-256 paragraph); `## License` section (four-bullet weights/code/codec/tooling list plus non-commercial conversion paragraph).
