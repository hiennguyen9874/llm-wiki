---
type: Concept
title: VibeVoice-7B GGUF
description: Q8_0 GGUF packaging of VibeVoice-7B for audio.cpp with CLI/server/WebUI usage, English/Chinese long-form multi-speaker scope, and RTX 5090 sanity-check figures.
tags: [tts, gguf, audio-cpp, multi-speaker, long-form]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: vibevoice-7b-gguf-card
    resource: ../raw/VibeVoice-7B-GGUF.md
    kind: documentation
    title: VibeVoice 7B GGUF for audio.cpp
---

VibeVoice-7B GGUF is a Q8_0 GGUF conversion of `vibevoice/VibeVoice-7B` targeting the audio.cpp runtime, distributed as a single GGUF package for CLI/server and WebUI use, intended for English and Chinese long-form multi-speaker speech synthesis, with a reported RTX 5090 server-mode sanity check of about 0.18 RTF, 52 s output, and 13.3 GB peak VRAM (**Reported**).[^vibevoice-7b-gguf-card]

## Package identity

- Card title is `VibeVoice 7B GGUF for audio.cpp`; upstream model is [vibevoice/VibeVoice-7B](https://huggingface.co/vibevoice/VibeVoice-7B) and runtime target is [audio.cpp](https://github.com/0xShug0/audio.cpp) (**Reported**).[^vibevoice-7b-gguf-card]
- Frontmatter declares `base_model: vibevoice/VibeVoice-7B`, `library_name: audio.cpp`, `license: mit`, and tags `audio.cpp`, `gguf`, `text-to-speech`, `multi-speaker`, and `long-form` (**Observed** by static inspection).[^vibevoice-7b-gguf-card]
- VibeVoice is described as a long-form, multi-speaker speech generation model intended for English and Chinese speech synthesis (**Reported**).[^vibevoice-7b-gguf-card]

## Files

- `vibevoice-7b-q8_0.gguf`: Q8_0 GGUF package for VibeVoice 7B (**Reported**).[^vibevoice-7b-gguf-card]
- `LICENSE`: MIT license from the upstream VibeVoice project (**Reported**).[^vibevoice-7b-gguf-card]

## Usage

- Use the GGUF directly with the audio.cpp CLI/server, or download/select it from the native WebUI once the package is published (**Reported**).[^vibevoice-7b-gguf-card]

## Performance sanity check

- Observed quick-check on RTX 5090 for the Q8_0 GGUF in audio.cpp server mode: RTF about `0.18`, output length about `52s`, peak VRAM about `13.3 GB` (**Reported**).[^vibevoice-7b-gguf-card]
- The card qualifies these numbers as implementation- and hardware-dependent and as only a quick audio.cpp sanity check, not a benchmark (**Reported**).[^vibevoice-7b-gguf-card]

## Relationships

- Packaged variant of [VibeVoice-1.5B](vibevoice-1.5b.md): that concept covers the 1.5B long-form multi-speaker research model with 7.5 Hz continuous tokenizers, Qwen2.5-1.5B backbone, diffusion head, and up to 90-minute 4-speaker synthesis, while this concept covers a Q8_0 GGUF distribution of the larger 7B checkpoint for the audio.cpp runtime with CLI/server/WebUI usage and RTX 5090 sanity-check figures; no shared weight file is asserted (**Synthesis**).[^vibevoice-7b-gguf-card]

## Coverage and limits

- Source inspected statically only; no GGUF downloaded, no audio.cpp CLI/server executed, and no RTF, output-length, or VRAM figure reproduced (**Synthesis**).[^vibevoice-7b-gguf-card]
- Linked but unfetched and not in `raw/`: the upstream `vibevoice/VibeVoice-7B` checkpoint, the `vibevoice-7b-q8_0.gguf` weight file, the audio.cpp repository/CLI/server/WebUI, and the `LICENSE` file (**Synthesis**).[^vibevoice-7b-gguf-card]
- All packaging, usage, language-scope, and performance claims are source assertions without independent verification in this wiki; release and performance figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^vibevoice-7b-gguf-card]

[^vibevoice-7b-gguf-card]: [VibeVoice 7B GGUF for audio.cpp](../raw/VibeVoice-7B-GGUF.md) — locators: frontmatter (`license`, `base_model`, `library_name`, `tags`); H1 title plus intro paragraphs (GGUF conversion of `vibevoice/VibeVoice-7B` for audio.cpp, upstream-model and audio.cpp links); section `Files` (`vibevoice-7b-q8_0.gguf` Q8_0 bullet, `LICENSE` MIT bullet); section `Usage` (audio.cpp CLI/server direct-use sentence, native WebUI sentence; long-form multi-speaker English/Chinese synthesis sentence); section `Local audio.cpp check` (RTX 5090 Q8_0 server-mode RTF ~`0.18` / ~`52s` output / ~`13.3 GB` peak VRAM bullets, implementation- and hardware-dependent sanity-check-not-benchmark qualifier).
