---
type: Concept
title: Audio Flamingo 3 and Next GGUF
description: Self-contained GGUF packaging of NVIDIA Audio Flamingo 3 and Audio Flamingo Next for audio.cpp with CLI/server usage, Python-parity correctness, RTX 5090 performance, and quantization tradeoffs.
tags: [ml, asr, audio-understanding, audio-cpp, gguf]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
sources:
  - id: audio-flamingo-gguf-card
    resource: ../raw/Audio-Flamingo-GGUF.md
    kind: documentation
    title: Audio Flamingo 3 and Next GGUF
---

Audio Flamingo 3 and Next GGUF is a self-contained GGUF packaging of NVIDIA Audio Flamingo 3 and Audio Flamingo Next for use with audio.cpp, bundling model tensors, tokenizer, configuration, and the audio.cpp model spec, with six weight files spanning BF16, Q8_0, and Q4_K and documented CLI/server usage, Python-parity correctness, and RTX 5090 performance figures (**Reported**).[^audio-flamingo-gguf-card]

## Package identity and capabilities

- Card title is "Audio Flamingo 3 and Next GGUF"; frontmatter declares `license: other` with `license_name: nvidia-oneway-noncommercial`, `base_model` entries `nvidia/audio-flamingo-3-hf` and `nvidia/audio-flamingo-next-hf`, `language: en`, and tags `audio.cpp`, `gguf`, `audio-text-to-text`, and `automatic-speech-recognition` (**Reported**).[^audio-flamingo-gguf-card]
- Runtime target is [audio.cpp](https://github.com/0xShug0/audio.cpp); both models support transcription, captioning, and questions about speech, music, and environmental sounds (**Reported**).[^audio-flamingo-gguf-card]
- File layout with upstream checkpoint, size, and maximum audio (**Reported**):[^audio-flamingo-gguf-card]

| File | Upstream checkpoint | Size | Maximum audio |
| --- | --- | ---: | ---: |
| `audio-flamingo-3-bf16.gguf` | Audio Flamingo 3 | 15.4 GiB | 10 minutes |
| `audio-flamingo-3-q8_0.gguf` | Audio Flamingo 3 | 8.7 GiB | 10 minutes |
| `audio-flamingo-3-q4_k.gguf` | Audio Flamingo 3 | 5.1 GiB | 10 minutes |
| `audio-flamingo-next-bf16.gguf` | Audio Flamingo Next | 15.4 GiB | 30 minutes |
| `audio-flamingo-next-q8_0.gguf` | Audio Flamingo Next | 8.7 GiB | 30 minutes |
| `audio-flamingo-next-q4_k.gguf` | Audio Flamingo Next | 5.1 GiB | 30 minutes |

## Usage

- CLI transcription uses `audiocpp_cli --task asr --family audio_flamingo --model /path/to/audio-flamingo-3-bf16.gguf --backend cuda --audio input.wav --request-option "instruct=Transcribe the input speech." --text-out response.txt --log`; select either GGUF with `--model` (**Reported**).[^audio-flamingo-gguf-card]
- For general audio understanding, use a question-style instruction such as `Describe the instruments and tempo.` (**Reported**).[^audio-flamingo-gguf-card]
- Requested timestamps or speaker descriptions are generated text, not structured alignment or diarization results (**Reported**).[^audio-flamingo-gguf-card]
- For server use, configure family `audio_flamingo`, task `asr`, and mode `offline`, then submit audio to `/v1/audio/transcriptions` with the instruction in `prompt` (**Reported**).[^audio-flamingo-gguf-card]

## Correctness reference

- Official Python BF16 output is the reference; correctness comparisons and performance measurements are separate tests (**Reported**).[^audio-flamingo-gguf-card]

| Model | Runtime / weights | Result compared with official Python |
| --- | --- | --- |
| Audio Flamingo 3 | Official Python BF16 | Reference |
| Audio Flamingo 3 | audio.cpp BF16 | Exact transcription and music answer |
| Audio Flamingo 3 | audio.cpp Q8_0 | Exact transcription; coherent but different music answer |
| Audio Flamingo 3 | audio.cpp Q4_K | Same transcription words with different wrapper and punctuation; coherent but different music answer |
| Audio Flamingo Next | Official Python BF16 | Reference |
| Audio Flamingo Next | audio.cpp BF16 | Exact short transcription; matching words and line boundaries on the three-minute test after timestamps were removed |
| Audio Flamingo Next | audio.cpp Q8_0 | Same short transcription words with one comma omitted |
| Audio Flamingo Next | audio.cpp Q4_K | Exact short transcription |

Table values are source-reported comparisons as listed in the card's correctness table (**Reported**).[^audio-flamingo-gguf-card]

- Audio Flamingo Next generates timestamps as text rather than structured alignment; its BF16 three-minute response used the same words and line boundaries as Python after timestamps were removed, but the generated timestamps drifted (**Reported**).[^audio-flamingo-gguf-card]

## CUDA performance and quantization

- Test conditions: RTX 5090 with the same decoded 10-second, 16-kHz mono speech input; Python uses the official Transformers BF16 model with SDPA; audio.cpp uses the CUDA backend and 8 CPU threads; wall time and RTF come from the second request in an already-loaded session; peak VRAM covers the complete process sampled every 100 ms (**Reported**).[^audio-flamingo-gguf-card]

| Model | Runtime / weights | Warm wall time | RTF | Peak VRAM |
| --- | --- | ---: | ---: | ---: |
| Audio Flamingo 3 | Official Python BF16 | 292.4 ms | 0.0292 | 16,766 MiB |
| Audio Flamingo 3 | audio.cpp BF16 | 283.3 ms | 0.0283 | 16,854 MiB |
| Audio Flamingo 3 | audio.cpp Q8_0 | 184.9 ms | 0.0185 | 9,956 MiB |
| Audio Flamingo 3 | audio.cpp Q4_K | 151.7 ms | 0.0152 | 6,280 MiB |
| Audio Flamingo Next | Official Python BF16 | 249.0 ms | 0.0249 | 16,784 MiB |
| Audio Flamingo Next | audio.cpp BF16 | 246.3 ms | 0.0246 | 16,890 MiB |
| Audio Flamingo Next | audio.cpp Q8_0 | 160.9 ms | 0.0161 | 9,992 MiB |
| Audio Flamingo Next | audio.cpp Q4_K | 129.9 ms | 0.0130 | 6,314 MiB |

Table values are source-reported measurements as listed in the card's performance table (**Reported**).[^audio-flamingo-gguf-card]

- Quantized outputs remained coherent on the transcription and music-understanding requests; Q4_K is the default package and offers the lowest tested VRAM, while Q8_0 is the higher-precision quantized alternative (**Reported**).[^audio-flamingo-gguf-card]
- Quantization can change wording, punctuation, or factual details in open-ended answers and should not be treated as exact parity with BF16 (**Reported**).[^audio-flamingo-gguf-card]

## Audio preprocessing and license

- For comparisons with Python, supply the same decoded 16-kHz mono WAV to both implementations (**Reported**).[^audio-flamingo-gguf-card]
- Python's optional TorchCodec loader and librosa fallback use different downmixing and resampling paths; audio.cpp averages channels and uses SOXR when resampling is needed (**Reported**).[^audio-flamingo-gguf-card]
- Both checkpoints use the NVIDIA OneWay Noncommercial License; the card states the upstream license is included in its directory and advises reviewing its terms before use or redistribution (**Reported**).[^audio-flamingo-gguf-card]
- The card points to the audio.cpp model documentation for request options, conversion, and additional usage details (**Reported**).[^audio-flamingo-gguf-card]

## Relationships

- Related sibling packaging: [AuK Base and Flash GGUF](auk-base-and-flash-gguf.md) is also a GGUF packaging for audio.cpp with CLI usage and C++/Python parity reporting, while this concept covers the Audio Flamingo 3/Next audio-understanding family (**Synthesis**).[^audio-flamingo-gguf-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no GGUFs loaded, and no correctness or performance figures reproduced (**Synthesis**).[^audio-flamingo-gguf-card]
- Referenced local artifacts (the six GGUF files and the stated included upstream license) were not present in `raw/` and were not inspected; linked external pages (audio.cpp repository, upstream Hugging Face checkpoints, audio.cpp model documentation) were not fetched (**Synthesis**).[^audio-flamingo-gguf-card]
- All correctness and performance figures, quantization characterizations, and preprocessing claims are source assertions without independent verification in this wiki (**Synthesis**).[^audio-flamingo-gguf-card]

[^audio-flamingo-gguf-card]: [Audio Flamingo 3 and Next GGUF](../raw/Audio-Flamingo-GGUF.md) — locators: frontmatter (`license`, `license_name`, `base_model`, `tags`, `language`); intro paragraphs (audio.cpp target, self-contained GGUF contents, supported tasks); file table (6 GGUF filenames, sizes, maximum audio); section `Usage` (CLI code fence with `--task asr --family audio_flamingo --model --backend --audio --request-option --text-out --log`, general-understanding question, timestamp/diarization disclaimer, server `offline` + `/v1/audio/transcriptions` paragraph); section `Correctness Reference` (BF16-reference note, 8-row comparison table, Next timestamp-drift paragraph); section `CUDA Performance and Quantization` (RTX 5090 / 10-s 16-kHz mono / SDPA / CUDA + 8 threads / second-request / 100-ms VRAM protocol, 8-row performance table, quantization coherence/default/VRAM paragraphs); section `Audio Preprocessing` (same-WAV note, TorchCodec/librosa vs average-channels/SOXR paragraph); license paragraph (NVIDIA OneWay Noncommercial, review-before-use note); closing model-documentation link.
