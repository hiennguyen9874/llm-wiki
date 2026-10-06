---
type: Concept
title: SAM Audio GGUF
description: GGUF packaging of Meta SAM Audio Small, Base, and Large for audio.cpp with text, visual, and temporal prompting, C++/Python parity, RTX 5090 performance, quantization, and bounded-memory long-form figures.
tags: [audio-separation, target-extraction, audio-cpp, gguf]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: sam-audio-gguf-card
    resource: ../raw/SAM-Audio-GGUF.md
    kind: documentation
    title: SAM Audio GGUF
---

SAM Audio GGUF is a GGUF packaging of the Meta SAM Audio separation checkpoints (Small, Base, Large) for native inference with audio.cpp, separating a sound described by text, a masked image or video, or positive and negative time spans from an input recording, distributed as self-contained F32, BF16, and Q8_0 weight files with documented CLI usage, controlled C++/Python parity figures, RTX 5090 performance and VRAM figures, and an experimental bounded-memory mode for long recordings (**Reported**).[^sam-audio-gguf-card]

## Package identity and variants

- Card title is "SAM Audio GGUF"; frontmatter declares `license: other` with `license_name: sam-license`, `base_model: facebook/sam-audio-large`, `library_name: audio.cpp`, `pipeline_tag: audio-to-audio`, and tags `audio.cpp`, `gguf`, and `audio-separation` (**Reported**).[^sam-audio-gguf-card]
- These packages use the original Meta checkpoints, not the separate `-tv` variants; the official SAM Audio implementation is pinned to `bb4c699` (**Reported**).[^sam-audio-gguf-card]

| Variant | GGUF | Pinned checkpoint |
| --- | --- | --- |
| Small | `sam-audio-small-f32.gguf` | `facebook/sam-audio-small` at `20b65f5` |
| Base | `sam-audio-base-f32.gguf` | `facebook/sam-audio-base` at `81f6400` |
| Large | `sam-audio-large-f32.gguf` | `facebook/sam-audio-large` at `5f2cd3a` |

Table values are source-reported filenames and pinned Hugging Face revisions as listed in the card's upstream table (**Reported**).[^sam-audio-gguf-card]

- Each GGUF contains SAM weights, the T5 text encoder, tokenizer, configuration, and the audio.cpp model spec; no separate text encoder is needed (**Reported**).[^sam-audio-gguf-card]
- F32 packages retain the original weights, checked byte-for-byte against the source tensors; BF16 and Q8_0 packages for each variant were converted directly from the source safetensors; biases, normalization vectors, and scale/shift tables remain F32; Q8_0 denotes mixed quantized storage, not that every tensor is quantized (**Reported**).[^sam-audio-gguf-card]
- Runtime target is [audio.cpp](https://github.com/0xShug0/audio.cpp); code is reported tested on CUDA, Vulkan, and Metal (**Reported**).[^sam-audio-gguf-card]

## Usage

- Text-conditioned separation: `audiocpp_cli --task s2s --family sam_audio --model /path/to/SAM-Audio-GGUF/sam-audio-small-f32.gguf --backend cuda --audio input.wav --text "man speaking" --seed -1 --out-dir outputs/separation --log` (**Reported**).[^sam-audio-gguf-card]
- Outputs are `target.wav` and `residual.wav`, mono 48 kHz (**Reported**).[^sam-audio-gguf-card]
- Optional temporal prompts use `--request-option 'anchors=[["+",0.5,2.0],["-",3.0,4.0]]'`; a masked static image uses `--request-option reference_image_path=masked.png` and a masked video uses `--request-option reference_video_path=masked.mp4` (**Reported**).[^sam-audio-gguf-card]
- Video decoding requires FFmpeg/libav runtime libraries; use one visual option at a time and keep the video and input audio time origins aligned; automatic span prediction and candidate ranking are not included (**Reported**).[^sam-audio-gguf-card]
- Full request options are documented in the linked audio.cpp SAM Audio model usage guide (**Reported**).[^sam-audio-gguf-card]
- Watermark caveat: all parity, performance, and VRAM results below were measured with watermarking enabled to match the official Python implementation, which adds a watermark to its output; the final audio.cpp version will return audio without the added watermark, so these results do not describe the final implementation (**Reported**).[^sam-audio-gguf-card]

## Controlled parity with Python

- Protocol: tested separately from performance on CUDA with F32 weights and TF32 disabled in both implementations (`NVIDIA_TF32_OVERRIDE=0`); Python used seed 42 while C++ replayed its exact diffusion noise and watermark bits; both used the same 14.975-second office recording, `man speaking` prompt, and 16 midpoint steps; C++ computed its own encoder features, diffusion, and decoded audio (**Reported**).[^sam-audio-gguf-card]
- Each row compares the final C++ waveforms directly against official Python, including bounded-memory mode; higher cosine similarity is better, with 1 as exact directional agreement, not a claim of byte-identical waveforms (**Reported**).[^sam-audio-gguf-card]

| Variant | C++ mode | Target cosine | Residual cosine |
| --- | --- | ---: | ---: |
| Small F32 | Normal | 0.99999945 | 0.99999864 |
| Small F32 | Bounded memory | 0.99999968 | 0.99999896 |
| Base F32 | Normal | 0.99999956 | 0.99999558 |
| Base F32 | Bounded memory | 0.99999950 | 0.99999753 |
| Large F32 | Normal | 0.99999980 | 0.99999888 |
| Large F32 | Bounded memory | 0.99999984 | 0.99999936 |

Table values are source-reported cosine similarities as listed in the card's parity table; all rows exceeded 0.9999 for both outputs (**Reported**).[^sam-audio-gguf-card]

- Repeating each controlled C++ run within the same session produced byte-identical outputs (**Reported**).[^sam-audio-gguf-card]

## Ordinary CUDA performance with Python

- Conditions: NVIDIA RTX 5090 (32 GB) with a 14.975-second recording from the official office example and the text prompt `man speaking`; both implementations use the original weights, 16 midpoint steps, one candidate, and no visual or span prompts; optional ranking and span-prediction models are not loaded in Python (**Reported**).[^sam-audio-gguf-card]
- Ordinary inference means no fixed or replayed random noise, no TF32 override, and no forced precision/autocast changes; C++ uses `--seed -1` while Python does not set a seed; Python uses PyTorch 2.11.0+cu128 and C++ uses a debug build with 8 threads (**Reported**).[^sam-audio-gguf-card]
- Warm inference time is the median of the last three of five sequential requests in one session, excluding model loading and file I/O; RTF is inference time divided by input duration (lower is faster); peak VRAM is process memory sampled with `nvidia-smi` every 50 ms across loading and all five requests, using the same method for Python and C++ (**Reported**).[^sam-audio-gguf-card]

| Variant | C++ warm time | C++ RTF | C++ peak VRAM | Python warm time | Python RTF | Python peak VRAM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Small F32 | 684 ms | 0.0456 | 8,500 MiB | 746 ms | 0.0498 | 10,972 MiB |
| Base F32 | 918 ms | 0.0613 | 11,010 MiB | 1,105 ms | 0.0738 | 13,414 MiB |
| Large F32 | 1,542 ms | 0.1030 | 17,826 MiB | 2,103 ms | 0.1405 | 20,568 MiB |

Table values are source-reported measurements as listed in the card's performance table (**Reported**).[^sam-audio-gguf-card]

- These are text-conditioned, single-recording measurements, not a benchmark of visual prompting, automatic span prediction, or candidate ranking; outputs from these independent-randomness performance runs are not used for parity comparisons (**Reported**).[^sam-audio-gguf-card]

## BF16 and Q8_0 compared with C++ F32

- This is a separate C++-only comparison on the same RTX 5090 and 14.975-second input; ordinary performance uses the five-request methodology above with `--seed -1` and no TF32 or precision overrides; F32 was remeasured for this comparison and no Python model was run (**Reported**).[^sam-audio-gguf-card]

| Variant | Storage | Warm time | RTF | Peak VRAM |
| --- | --- | ---: | ---: | ---: |
| Small | F32 | 700 ms | 0.04673 | 8,500 MiB |
| Small | BF16 | 674 ms | 0.04501 | 7,366 MiB |
| Small | Q8_0 | 673 ms | 0.04493 | 6,834 MiB |
| Base | F32 | 960 ms | 0.06408 | 11,010 MiB |
| Base | BF16 | 785 ms | 0.05241 | 8,644 MiB |
| Base | Q8_0 | 794 ms | 0.05302 | 7,524 MiB |
| Large | F32 | 1,566 ms | 0.10457 | 17,826 MiB |
| Large | BF16 | 1,146 ms | 0.07652 | 12,092 MiB |
| Large | Q8_0 | 1,051 ms | 0.07018 | 9,378 MiB |

Table values are source-reported C++-only measurements (**Reported**).[^sam-audio-gguf-card]

- Output drift was measured in separate controlled C++ runs using seed 42 and `NVIDIA_TF32_OVERRIDE=0` for every dtype; each output is compared against that variant's C++ F32 waveform, not Python; these runs supply no performance or VRAM figures (**Reported**).[^sam-audio-gguf-card]

| Variant | Storage | Target cosine vs F32 | Residual cosine vs F32 |
| --- | --- | ---: | ---: |
| Small | BF16 | 0.999940 | 0.999763 |
| Small | Q8_0 | 0.999476 | 0.999095 |
| Base | BF16 | 0.999918 | 0.999788 |
| Base | Q8_0 | 0.999623 | 0.999069 |
| Large | BF16 | 0.999743 | 0.999712 |
| Large | Q8_0 | 0.999590 | 0.999273 |

Table values are source-reported drift figures (**Reported**).[^sam-audio-gguf-card]

- BF16 reduced peak VRAM by 13–32% and Q8_0 by 20–47% in this workload; drift is expected; these short text-conditioned checks do not establish equal quality for every recording or validate reduced-precision visual prompting and bounded-memory long-form execution; F32 remains available as the reference (**Reported**).[^sam-audio-gguf-card]

## Bounded-memory mode

- Enable the experimental session option with `--session-option sam_audio.memory_bounded=true`; it defaults to `false` and its name is provisional (**Reported**).[^sam-audio-gguf-card]
- The existing Small GGUF predates this option, so add `--model-spec-override model_specs/sam_audio.json` from a checkout that includes bounded-memory support; the Base and Large GGUFs include the option in their embedded specs (**Reported**).[^sam-audio-gguf-card]
- The mode retains full-recording diffusion and attention; codec convolutions use tiles with receptive-field context and watermark LSTM state carries between tiles; it does not separate independent audio chunks and crossfade them; intermediate sequences reside in host RAM, which still grows with input length; transfers and overlap computation can make it slower on short inputs and small numerical differences are possible; the configured model context limit remains 400 seconds (**Reported**).[^sam-audio-gguf-card]
- Test setup: CUDA tests on a 180-second input made by repeating the same example to 180 seconds, with the same prompt and inference settings as above; each C++ result is the first inference in a fresh session, including graph setup but excluding model loading and file I/O; peak VRAM includes loading and inference; these are not warm medians (**Reported**).[^sam-audio-gguf-card]

| Variant | C++ bounded time | C++ RTF | C++ peak VRAM | Official Python, same input |
| --- | ---: | ---: | ---: | --- |
| Small F32 | 8.768 s | 0.0487 | 6,550 MiB | CUDA out of memory |
| Base F32 | 11.109 s | 0.0617 | 9,212 MiB | CUDA out of memory |
| Large F32 | 17.038 s | 0.0947 | 16,244 MiB | CUDA out of memory |

Table values are source-reported long-form figures (**Reported**).[^sam-audio-gguf-card]

- All three C++ runs produced the complete target and residual recordings; Python ran out of memory in its audio encoder on the same 32 GB GPU using its default precision and allocator settings; this demonstrates completion and memory usage for this workload, not 180-second parity against Python, since Python did not produce a full-length reference; other hardware or Python memory-saving configurations may behave differently (**Reported**).[^sam-audio-gguf-card]

## License

- SAM Audio weights are distributed under the SAM License, dated November 19, 2025; the included T5 encoder is from Google T5 Base and retains its Apache-2.0 license (`LICENSE-T5`); conversion does not replace the upstream license terms (**Reported**).[^sam-audio-gguf-card]

## Relationships

- Related sibling packaging: [AuK Base and Flash GGUF](auk-base-and-flash-gguf.md) is also an audio.cpp GGUF packaging that covers speech separation and target speaker extraction among its 16 validated tasks, while this concept covers a dedicated text/visual/span-prompted separation model with bounded-memory long-form execution (**Synthesis**).[^sam-audio-gguf-card]
- Related sibling packaging: [Audio Flamingo 3 and Next GGUF](audio-flamingo-3-and-next-gguf.md) is also a self-contained audio.cpp GGUF packaging with CLI/server usage and RTX 5090 C++/Python reporting, while this concept covers audio separation (target plus residual outputs) rather than transcription and audio understanding (**Synthesis**).[^sam-audio-gguf-card]
- Related sibling packaging: [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md) is also a GGUF conversion for a llama.cpp-family CPU/edge runtime with quantization tradeoffs, while this concept targets CUDA/Vulkan/Metal separation with F32 reference weights and BF16/Q8_0 storage options (**Synthesis**).[^sam-audio-gguf-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no GGUFs loaded, and no parity, performance, VRAM, or drift figures reproduced (**Synthesis**).[^sam-audio-gguf-card]
- Referenced local artifacts (GGUF files, `LICENSE`, `LICENSE-T5`, `model_specs/sam_audio.json`, `outputs/separation` results) were not present in `raw/` and were not inspected; linked external pages (audio.cpp repository, audio.cpp SAM Audio usage guide, upstream Meta checkpoints at the pinned revisions, official office example) were not fetched (**Synthesis**).[^sam-audio-gguf-card]
- All identity, usage, parity, performance, VRAM, quantization, bounded-memory, and license characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the instance staleness convention; the watermark-enabled measurement caveat and the text-conditioned single-recording scope are consequential limits (**Synthesis**).[^sam-audio-gguf-card]

[^sam-audio-gguf-card]: [SAM Audio GGUF](../raw/SAM-Audio-GGUF.md) — locators: frontmatter (`license`, `license_name`, `base_model`, `library_name`, `pipeline_tag`, `tags`); section `Upstream` (original-checkpoints-not-`-tv` paragraph, 3-row variant/GGUF/pinned-checkpoint table with revisions `20b65f5…`, `81f6400…`, `5f2cd3a…`, official-implementation pin `bb4c699`, self-contained GGUF contents paragraph, F32 byte-for-byte / BF16/Q8_0 direct-conversion / F32-bias-norm-scale paragraph, Q8_0-mixed-storage note); section `Usage` (`audiocpp_cli --task s2s --family sam_audio` fence with `--model --backend --audio --text --seed --out-dir --log`, `target.wav`/`residual.wav` mono-48-kHz paragraph, `anchors` / `reference_image_path` / `reference_video_path` paragraphs, FFmpeg-libav / one-visual-option / time-origin-alignment / no-span-prediction-or-ranking paragraph, usage-guide link, CUDA/Vulkan/Metal paragraph, `WARNING` watermark paragraph); section `Controlled Parity With Python` (CUDA F32 TF32-disabled / seed-42 / replayed-noise-and-watermark / 14.975-s office recording / `man speaking` / 16-midpoint-steps / own-encoder-features paragraph, cosine-definition paragraph, 6-row parity table, >0.9999 and byte-identical-rerun paragraph); section `Ordinary CUDA Performance With Python` (RTX 5090 32-GB / office-example / `man speaking` paragraph, original-weights / 16-steps / one-candidate / no-visual-or-span / ranking-not-loaded paragraph, ordinary-inference / `--seed -1` / Python-no-seed / PyTorch 2.11.0+cu128 / debug-build-8-threads paragraph, warm-median-3-of-5 / RTF-definition / 50-ms-`nvidia-smi` paragraph, 3-row C++/Python table, single-recording-scope and independent-randomness-not-for-parity notes); section `BF16 and Q8 Compared With C++ F32` (C++-only / same-GPU-and-input / 5-request-methodology / F32-remeasured / no-Python paragraph, 9-row warm-time/RTF/VRAM table, seed-42 TF32-disabled vs-C++-F32-not-Python paragraph, 6-row drift table, 13–32% / 20–47% VRAM / drift-expected / no-every-recording-or-visual-or-bounded-memory-validation / F32-reference paragraph); section `Bounded-Memory Mode` (`sam_audio.memory_bounded=true` / default-`false` / provisional-name paragraph, Small-GGUF `--model-spec-override model_specs/sam_audio.json` vs Base/Large-embedded-spec paragraph, full-diffusion-and-attention / tiled-codec-convolutions / watermark-LSTM-carry / no-chunk-crossfade / host-RAM-growth / slower-on-short-inputs / 400-s-limit paragraph, 180-s-repeated-input / first-inference-fresh-session / VRAM-includes-loading / not-warm-medians paragraph, 3-row bounded table with Python-OOM column, completion-not-parity / default-precision-and-allocator / hardware-config paragraph); section `License` (SAM License 2025-11-19, Google-T5-Base Apache-2.0 `LICENSE-T5`, conversion-does-not-replace-terms paragraph). Referenced GGUF binaries, `LICENSE`, `LICENSE-T5`, and `model_specs/` paths have no locator available in `raw/` (files absent).
