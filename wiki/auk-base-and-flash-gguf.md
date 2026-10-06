---
type: Concept
title: AuK Base and Flash GGUF
description: GGUF packaging of Tencent AuK Base and AuK-Flash for audio.cpp with component layout, CLI usage, 16-task C++/Python parity figures, and quantized-component smoke-test scope.
tags: [ml, tts, voice-cloning, speech-editing, audio-cpp, gguf]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:04:37Z }
stale_after: 2027-10-06
sources:
  - id: auk-gguf-card
    resource: ../raw/AuK-Base-and-Flash-GGUF.md
    kind: documentation
    title: AuK GGUF for audio.cpp
---

AuK Base and Flash GGUF is a GGUF packaging of the Tencent AuK base model plus an optional AuK-Flash distilled variant for use with audio.cpp, with a three-component runtime layout (generator, Qwen conditioner, VAE), explicit variant-selection flags, and a 16-task C++/Python waveform-parity report that applies only to the original combined GGUF, not the component files in this package (**Reported**).[^auk-gguf-card]

## Package identity and components

- Card title is "AuK GGUF for audio.cpp"; frontmatter declares `license: mit`, `base_model: tencent/AuK`, `pipeline_tag: text-to-speech`, and audio/speech/TTS tags including zero-shot TTS, voice cloning, speech editing, enhancement, separation, instruction-guided, and diffusion (**Reported**).[^auk-gguf-card]
- The pinned base model is [Tencent AuK](https://huggingface.co/tencent/AuK); the package also includes optional files converted from [AuK-Flash](https://huggingface.co/tencent/AuK-Flash), which is a separate distilled variant and not the pinned base model (**Reported**).[^auk-gguf-card]
- Runtime target is [audio.cpp](https://github.com/0xShug0/audio.cpp): pass the downloaded directory to `audiocpp_cli --model` and keep the `config/` and `tokenizer/` directories alongside the GGUF files (**Reported**).[^auk-gguf-card]
- Default Base components are `auk-base-f32.gguf`, `qwen2.5-omni-3b-bf16.gguf`, and `auk-vae-f32.gguf`; the Qwen conditioner component is Qwen2.5-Omni-3B; the Flash default generator is `auk-flash-f32.gguf` (**Reported**).[^auk-gguf-card]
- Keep the F32 VAE in either Base or Flash configurations (**Reported**).[^auk-gguf-card]

## Usage

- Instruction TTS with explicitly selected Base components uses `--task tts --family auk --backend cuda` with `--session-option auk.variant=base`, `auk.model_gguf`, `auk.qwen_gguf`, `auk.vae_gguf`, plus `--text`, `--request-option "instruct=..."`, `duration_sec`, `--seed`, `--log`, and `--out` (**Reported**).[^auk-gguf-card]
- To use AuK-Flash, select `auk.variant=flash` and an `auk-flash-*.gguf` generator; to use the Qwen Q8_0 component, select `auk.qwen_gguf=qwen2.5-omni-3b-q8_0.gguf` (**Reported**).[^auk-gguf-card]
- For editing, use `--task gen --audio input.wav --text "<editing instruction>"`; request options and example instructions are documented in the audio.cpp AuK guide and the AuK cookbook, linked from the card (**Reported**).[^auk-gguf-card]
- Output-quality expectation: the card states it validates parity with upstream Python for the tested configuration, not whether AuK's output meets every quality expectation; if a result disappoints, it advises listening to the corresponding linked Python reference WAV first, since a similar Python result points to upstream model behavior rather than necessarily an audio.cpp conversion issue (**Reported**).[^auk-gguf-card]
- The card explicitly states the quantized component combinations have not received the same 16-task parity validation (**Reported**).[^auk-gguf-card]

## Sixteen-task C++/Python validation

- Protocol: the 16-task comparison forced FP32 inference and disabled TF32 in both implementations; input audio and reference voices came from the upstream AuK demo assets; durations not shown matched the source recording (**Reported**).[^auk-gguf-card]
- Outcome: all 16 C++ requests completed and produced 24 kHz WAVs with the same frame counts as the Python outputs; cosine values compare C++ WAVs against the Python baseline; the no-TF32 C++ run matched at waveform cosine 0.999989991 or higher across all tasks, and the files were not byte-identical (**Reported**).[^auk-gguf-card]
- The card cautions that waveform cosine alone does not establish whether an edit followed its instruction (**Reported**).[^auk-gguf-card]
- These historical results use the original combined GGUF and are not a 16-task parity claim for the component GGUFs in this package (**Reported**).[^auk-gguf-card]

| Task | Tested instruction / setting | C++ vs Python WAV cosine |
| --- | --- | ---: |
| Zero-shot TTS | Reference voice; target sentence; 6 s | 0.999999992 |
| Instruct TTS | Calm woman speaking clear English; 3 s | 0.999999898 |
| Speech content editing | Replace "but accepting what we cannot have" with "and living well with dreams unmet"; 7 s | 0.999999982 |
| Lyric editing | Replace "rear view" with "like you" in isolated vocals | 1.000000000 |
| Pitch editing | Raise pitch by 2 semitones | 0.999989991 |
| Speed editing | Speed 1.5x; 6.86 s | 0.999999993 |
| Volume editing | Increase volume by 10 dB | 0.999999997 |
| Emotion editing | Change emotion to happy | 0.999999993 |
| Timbre editing | Change to a deep, calm male voice | 0.999999991 |
| De-accent | Change Sichuan-accented speech to standard Mandarin | 0.999999795 |
| Nonverbal editing | Add a cough before "We tested"; 10.44 s | 0.999991188 |
| Whisper conversion | Speak the source in a quiet whisper | 0.999998371 |
| Speech enhancement | Preserve speakers; remove noise and reverberation | 0.999999994 |
| Speech separation | Keep the second speaker to start talking | 0.999999985 |
| Music separation | Keep the singing voice; remove other audio | 0.999999998 |
| Target speaker extraction | Keep the speaker saying "get what" | 0.999999997 |

Table values are source-reported measurements as listed in the card's 16-task table (**Reported**).[^auk-gguf-card]

## Component dtype smoke-test scope

- All component smoke tests used CUDA and the F32 VAE; a pass means the listed task loaded the selected GGUFs and generated a WAV, and does not establish Python parity or task quality (**Reported**).[^auk-gguf-card]

| Generator | Qwen conditioner | Tested task(s) |
| --- | --- | --- |
| Base F32 | BF16 | Zero-shot TTS; instruct TTS |
| Base F16 or Q8_0 | BF16 | Instruct TTS, one run per dtype |
| Base F32 or Q8_0 | Q8_0 | Zero-shot TTS, one run per combination |
| AuK-Flash F32 | BF16 | Zero-shot TTS; instruct TTS |
| AuK-Flash F16 or Q8_0 | BF16 | Instruct TTS, one run per dtype |
| AuK-Flash F32 | Q8_0 | Zero-shot TTS, one run |
| AuK-Flash F16 | Q8_0 | Instruct TTS, one run |

- The Base F16 + Qwen Q8_0 and AuK-Flash Q8_0 + Qwen Q8_0 combinations were not tested (**Reported**).[^auk-gguf-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no GGUFs loaded, and no WAV comparisons reproduced (**Synthesis**).[^auk-gguf-card]
- Referenced local artifacts (`config/`, `tokenizer/`, `examples/python/*.wav`, `examples/cpp/*.wav`, and the GGUF files) were not present in `raw/` and were not inspected; linked external guides, cookbook, upstream model pages, and demo assets were not fetched (**Synthesis**).[^auk-gguf-card]
- All parity figures, smoke-test outcomes, and quality disclaimers are source assertions without independent verification in this wiki (**Synthesis**).[^auk-gguf-card]

## Relationships

- Packages the upstream model described in [AuK](auk.md), which covers the official 1.5B base weights, the 16-task instruction interface, and SGLang-Omni serving, alongside the distilled variant in [AuK-Flash](auk-flash.md) (**Synthesis**).[^auk-gguf-card]

[^auk-gguf-card]: [AuK GGUF for audio.cpp](../raw/AuK-Base-and-Flash-GGUF.md) — locators: frontmatter (`license`, `base_model`, `pipeline_tag`, `tags`); intro paragraphs (audio.cpp target, base vs Flash variant, output-quality disclaimer); usage paragraphs and instruction-TTS code fence (`--task`, `--family auk`, `--model`, `--backend`, `auk.variant`, `auk.model_gguf`, `auk.qwen_gguf`, `auk.vae_gguf`, `instruct`, `duration_sec`); editing paragraph (`--task gen --audio`); section `Sixteen-task validation` (protocol paragraph, 16-row task table, cosine floor 0.999989991, combined-GGUF scope note); section `Dtypes and validation scope` (CUDA/F32-VAE note, 7-row smoke-test table, untested-combinations note). Referenced `config/`, `tokenizer/`, and `examples/` WAV paths have no locator available in `raw/` (files absent).
