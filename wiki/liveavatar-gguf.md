---
type: Concept
title: LiveAvatar GGUF
description: Native GGUF packaging of Wan2.2-S2V-14B with the LiveAvatar LoRA for audio.cpp, with three-file layout, CLI usage, low-VRAM weight-streaming controls, and RTX 5090 memory and latency figures.
tags: [avatar, gguf, audio-cpp, video-generation, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T09:07:47Z }
sources:
  - id: liveavatar-gguf-card
    resource: ../raw/LiveAvatar-GGUF.md
    kind: documentation
    title: LiveAvatar GGUF for audio.cpp
---

LiveAvatar GGUF is a native GGUF packaging of [Wan-AI/Wan2.2-S2V-14B](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B) with the official [Quark-Vision/Live-Avatar](https://huggingface.co/Quark-Vision/Live-Avatar) LoRA merged for [audio.cpp](https://github.com/0xShug0/audio.cpp), generating audio-driven avatar video from a reference image, speech audio, and a text description (**Reported**).[^liveavatar-gguf-card] It is filed here as end-to-end pipeline knowledge: a speech-audio-conditioned GGUF/edge-packaging case with streaming, latency, and memory tradeoffs directly comparable to voice-agent deployment decisions, even though its output modality is video rather than speech (**Synthesis**).[^liveavatar-gguf-card]

## Package identity and components

- Card title is "LiveAvatar GGUF for audio.cpp"; frontmatter declares `license: apache-2.0`, `base_model: Wan-AI/Wan2.2-S2V-14B`, `library_name: audio.cpp`, `pipeline_tag: image-to-video`, and tags for audio.cpp, GGUF, audio-to-video, LiveAvatar, and Wan2.2 (**Reported**).[^liveavatar-gguf-card]
- All three files are required: `Wan2.2-S2V-Support-Q4_K_S-F16.gguf` (UMT5 text encoder, Wav2Vec2 audio encoder, tokenizer, and embedded audio.cpp model specification), `Wan2.2-S2V-VAE-F16.gguf` (Wan video VAE in F16 with the embedded specification), and `Wan2.2-S2V-14B-NVFP4-LORA.gguf` (LiveAvatar Wan2.2 S2V denoiser with the official LiveAvatar adapter) (**Reported**).[^liveavatar-gguf-card]
- LiveAvatar and its Wan2.2 base model are released under Apache License 2.0 with the upstream license included as `LICENSE`; the GGUF conversion is a packaging format for audio.cpp and is not an official upstream release (**Reported**).[^liveavatar-gguf-card]

## Usage and defaults

- The default LiveAvatar configuration uses four Euler steps, scheduler shift 3, guidance scale 0, seed 420, 48 frames per clip, SageAttention, and 16 FPS (**Reported**).[^liveavatar-gguf-card]
- Generation uses `audiocpp_cli --task gen --family liveavatar --model /path/to/LiveAvatar-GGUF --backend cuda` with `--audio`, `--text`, `--request-option generation_mode=liveavatar`, `reference_image_path`, `height`, `width`, `--out-dir`, `--threads 8`, and `--log` (**Reported**).[^liveavatar-gguf-card]
- For lower VRAM use, add `--session-option liveavatar.denoiser_weight_streaming=true` with `--request-option denoiser_layerwise=true` and `denoiser_layerwise_batch=16`; resolution, duration, and memory-control options are documented in the linked audio.cpp LiveAvatar guide, which was not fetched (**Reported**).[^liveavatar-gguf-card]

## Low-VRAM mode and 720p evidence

- Low-VRAM mode keeps the denoiser transformer blocks in pinned host memory and stages one layer group at a time, making 720p generation possible near a 16 GiB VRAM limit at the cost of additional host-to-device transfers (**Reported**).[^liveavatar-gguf-card]
- The validated 1280x720 run generated 93 frames at 16 FPS (5.81 seconds of video) in 276 seconds wall time (4 minutes 36 seconds) and peaked at 15,993 MiB VRAM on an RTX 5090 (**Reported**).[^liveavatar-gguf-card]
- Low-VRAM control set (**Reported**):[^liveavatar-gguf-card]

| Control | Value |
| --- | --- |
| `liveavatar.denoiser_weight_streaming` | `true` |
| `denoiser_layerwise` | `true` |
| `denoiser_layerwise_batch` | `16` |
| `target_cache_blocks` | `1` |
| `vae_cache_f16` | `true` |
| `vae_encoder_chunk_size` | `4` |
| `vae_decoder_tile_size` | `320` |

- Weight streaming is slower than the normal resident-weight path: in a matched 240p comparison, model time increased from 13.33 to 21.73 seconds (about 1.63x slower), with the exact slowdown depending on resolution, hardware, and host memory bandwidth (**Reported**).[^liveavatar-gguf-card]
- The full-duration 720p example uses the official LiveAvatar Cyclops Baker image (`examples/cyclops/reference.jpg`, 720x400) and speech audio (`examples/cyclops/reference.wav`), showing 1280x720 generation from a lower-resolution image condition while retaining the complete 11.6-second WAV in the generated video (**Reported**).[^liveavatar-gguf-card]

| Full-duration 720p measurement | Result |
| --- | --- |
| Reference image | 720x400 |
| Reference audio | 11.60 s, 24 kHz mono |
| Output | 1280x720, 16 FPS, 11.60 s |
| Generated frames | 189 before audio-length muxing |
| LiveAvatar clips | 4 |
| Peak VRAM | 16,126 MiB (15.75 GiB) |
| Session time | 543.03 s (9 min 3 s) |
| Full CLI wall time | 557.33 s (9 min 17 s) |

Table values are source-reported measurements collected with the CUDA debug build on an NVIDIA GeForce RTX 5090 using the low-VRAM controls above (**Reported**).[^liveavatar-gguf-card]

## Cache trade-off and iteration guidance

- The 480p comparison uses the same Cyclops Baker inputs, prompt, seed, four clips, and complete 11.6-second audio; only `target_cache_blocks` changes (**Reported**).[^liveavatar-gguf-card]
- A longer cache retains more temporal context from preceding video blocks and can improve continuity across clip boundaries, but it does not directly increase per-frame resolution or detail (**Reported**).[^liveavatar-gguf-card]

| Target cache | Peak VRAM | Peak host RAM | Session time | Practical trade-off |
| --- | --- | --- | --- | --- |
| 2 blocks | 15,311 MiB | 43.33 GiB | 317.92 s | Lower memory and faster; recommended for iteration. |
| 3 blocks | 19,357 MiB | 56.94 GiB | 512.69 s | More temporal history, but nearly exhausts a 64 GB host and uses swap. |

Table values are source-reported; the 2-vs-3-block videos were linked but not inspected (**Reported**).[^liveavatar-gguf-card]

- The card recommends 480p as the starting point for prompt, identity, motion, and cache-window experiments: iterate at 480p, select the strongest result, and upscale that video afterward instead of paying the 720p generation cost for every attempt (**Reported**).[^liveavatar-gguf-card]

## Quality comparison controls

- Protocol: each clip uses the same reference image, audio, prompt, seed 420, four Euler steps, guidance 0, scheduler shift 3, 416x240 resolution, 16 FPS, and 84 requested frames (81 output frames, 5.06 seconds); the reference cell uses SageAttention, `memory_saver=true`, full target cache, F32 VAE cache, no VAE tiling, and non-layerwise denoising, and each other cell changes only the parameter shown (**Reported**).[^liveavatar-gguf-card]
- Inputs are `examples/dwarven_blacksmith.wav` and `examples/dwarven_blacksmith.jpg`; the prompt describes a stout cheerful dwarf with a braided beard and metal rings in a fiery forge, in the style of Blizzard Entertainment cinematics (**Reported**).[^liveavatar-gguf-card]
- Measurements used the CUDA debug build on an RTX 5090; wall time includes model loading and output generation, and peak VRAM is total device memory used during the run (**Reported**).[^liveavatar-gguf-card]

| Case | Controlled option | Peak VRAM (MiB) | Wall time (s) |
| --- | --- | --- | ---: |
| Reference | Reference controls | 25,586 | 24.44 |
| FlashAttention | `sage_attention=false` | 25,990 | 24.90 |
| F16 VAE cache | `vae_cache_f16=true` | 22,896 | 25.16 |
| VAE decoder tiling | `vae_decoder_tile_size=320` | 25,566 | 24.51 |
| Target cache: 1 block | `target_cache_blocks=1` | 19,935 | 23.28 |
| Target cache: 4 blocks | `target_cache_blocks=4` | 22,761 | 24.40 |
| Layerwise denoising | `denoiser_layerwise=true`, `denoiser_layerwise_batch=16` | 25,333 | 26.62 |

Table values are source-reported measurements as listed in the card's quality table; the per-cell comparison videos were linked but not inspected (**Reported**).[^liveavatar-gguf-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no GGUFs loaded, and no videos regenerated or compared (**Synthesis**).[^liveavatar-gguf-card]
- Referenced local artifacts (`examples/cyclops/`, `examples/dwarven_blacksmith.*`, `examples/quality/`, output MP4s, and `LICENSE`) were not present in `raw/` and were not inspected; linked external pages (upstream model repos, audio.cpp repository and LiveAvatar guide, and the `audio-cpp/LiveAvatar-GGUF` media URLs) were not fetched (**Synthesis**).[^liveavatar-gguf-card]
- All latency, VRAM, host-RAM, and parity-adjacent figures are source assertions from a CUDA-debug RTX 5090 setup without independent verification in this wiki; the card states no source date or package version, so freshness is unknown and RTX 5090 figures should be treated as hardware- and build-specific (**Synthesis**).[^liveavatar-gguf-card]

[^liveavatar-gguf-card]: [LiveAvatar GGUF for audio.cpp](../raw/LiveAvatar-GGUF.md) — locators: frontmatter (`license`, `base_model`, `library_name`, `pipeline_tag`, `tags`); intro paragraphs (Wan2.2-S2V-14B base, LiveAvatar LoRA, audio.cpp target, image plus audio plus text inputs); `Files` table (three GGUF filenames and component descriptions; all-three-required note); `Low-VRAM mode` (pinned-memory staging paragraph, 93-frame/276 s/15,993 MiB paragraph, 7-row controls table, 1.63x slowdown paragraph); `Full-duration 720p example` (Cyclops inputs paragraph, 8-row measurement table, controls-and-build paragraph); `480p cache trade-off` (same-inputs paragraph, context-vs-resolution paragraph, 2-row cache table, 480p-iteration recommendation); `Quality comparison` (protocol paragraph, inputs plus prompt paragraph, measurement paragraph, 7-row VRAM/wall-time table); `Run` (two code fences, defaults paragraph, docs link); `License` (Apache-2.0 paragraph, `LICENSE` note, not-official-upstream note). Referenced `examples/` and `LICENSE` paths have no locator available in `raw/` (files absent).
