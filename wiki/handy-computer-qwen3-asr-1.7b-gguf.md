---
type: Concept
title: handy-computer Qwen3-ASR-1.7B GGUF
description: GGUF conversions of Qwen3-ASR-1.7B for transcribe.cpp in BF16, F16, Q8_0, Q6_K, Q5_K_M, and Q4_K_M (1.32–4.09 GB) with offline 16 kHz mono WAV transcription, automatic language detection across 30 languages, and card-reported LibriSpeech test-clean WER of 1.62–1.81%.
tags: [stt, asr, gguf, transcribe-cpp, quantization, multilingual, qwen3-asr]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:35:20Z }
stale_after: 2027-10-13
sources:
  - id: handy-computer-qwen3-asr-1.7b-gguf-card
    resource: ../raw/handy-computer-Qwen3-ASR-1.7B-gguf.md
    kind: documentation
    title: handy-computer Qwen3-ASR-1.7B-gguf model card
  - id: qwen3-asr-readme
    resource: ../raw/Qwen3-ASR-0.6B.md
    kind: documentation
    title: Qwen3-ASR README and model card (family)
---

handy-computer publishes `handy-computer/Qwen3-ASR-1.7B-gguf`: six GGUF quantizations (BF16, F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M) of the 1.7B checkpoint from the [Qwen3-ASR family](qwen3-asr-family.md), packaged for the [transcribe.cpp](transcribe-cpp.md) runtime. The card describes offline transcription of 16 kHz mono WAV with automatic language detection over 30 languages, and no language hints, timestamps, translation, or streaming. It reports LibriSpeech test-clean WER from 1.62% (BF16, F16, Q8_0) to 1.81% (Q4_K_M) (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card]

## Files and quantization

| Quant | File | Size (card) | LibriSpeech test-clean WER (card) |
| --- | --- | ---: | ---: |
| BF16 | `Qwen3-ASR-1.7B-BF16.gguf` | 4.08 GB | 1.62% |
| F16 | `Qwen3-ASR-1.7B-F16.gguf` | 4.09 GB | 1.62% |
| Q8_0 | `Qwen3-ASR-1.7B-Q8_0.gguf` | 2.19 GB | 1.62% |
| Q6_K | `Qwen3-ASR-1.7B-Q6_K.gguf` | 1.69 GB | 1.65% |
| Q5_K_M | `Qwen3-ASR-1.7B-Q5_K_M.gguf` | 1.52 GB | 1.65% |
| Q4_K_M | `Qwen3-ASR-1.7B-Q4_K_M.gguf` | 1.32 GB | 1.81% |

Rows come from the card's `Downloads` table (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card]

- Files are hosted in the `handy-computer/Qwen3-ASR-1.7B-gguf` Hugging Face repository, per the download URLs (**Observed**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- The card calls BF16, F16, Q8_0, Q6_K, and Q5_K_M "within bootstrap CI of each other" and says Q4_K_M "regresses only ~0.2 WER points" (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card] The capture gives no CI values; the Q4_K_M gap is 0.19 points by table arithmetic (**Synthesis**).
- The card says the 1.7B has "more quantization headroom than the 0.6B". No 0.6B GGUF data is in this capture, so that comparison is unchecked (**Reported**; limit).
- The capture gives no per-file checksum, revision, or upload date (**Observed**).

## Runtime usage

```bash
git clone git@github.com:handy-computer/transcribe.cpp.git
cd transcribe.cpp
cmake -B build && cmake --build build
build/bin/transcribe-cli -m Qwen3-ASR-1.7B-Q8_0.gguf input.wav
```

- These are the card's commands; none were run for this wiki (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card] For other inputs, the card converts first with `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`. The 16 kHz mono WAV rule matches the runtime's rule in [transcribe.cpp](transcribe-cpp.md) (**Synthesis**).
- The card says explicit language hints "are not supported at this time" (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- Frontmatter flags: `lang_detect: true`, `timestamps: none`, `translate: false`, `streaming: false` (**Observed**).[^handy-computer-qwen3-asr-1.7b-gguf-card]

## Capability and metadata

- Upstream: `base_model: Qwen/Qwen3-ASR-1.7B` with `base_model_relation: quantized`; `library_name: transcribe.cpp`; `pipeline_tag: automatic-speech-recognition` (**Observed**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- License: Apache-2.0, inherited from the base model; the card points to the upstream model card for full terms (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- Languages: the frontmatter lists the same 30 languages as the family card (**Observed**; set match **Synthesis**). It declares no Chinese dialects or English accent variants, although the upstream family covers 22 Chinese dialects ([Qwen3-ASR family](qwen3-asr-family.md)).
- Streaming is off in this package's flags. The upstream family supports streaming on its vLLM backend (**Synthesis**, see [Qwen3-ASR family](qwen3-asr-family.md)).

## Quality figures

### English (LibriSpeech)

- Protocol per card: the full test-clean split (2,620 utterances), batch size 1, timestamps none, Whisper-style English normalizer, jiwer 3.x, scored on an Apple M4. The card says the figure "characterizes the English case only" (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- The upstream family card reports 1.63 for the same split under its own protocol (bf16, vLLM, greedy) (**Reported**).[^qwen3-asr-readme] The 1.62 versus 1.63 gap is not a measured change, because the protocols differ (**Synthesis**).

### Multilingual (FLEURS, Q8_0 only)

The frontmatter gives one WER or CER per language for Q8_0 only and states no FLEURS protocol (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card] CER is used for ja, ko, zh, th, and yue; WER for the rest. Grouped by value:

- **Under 5:** it 2.68, en 3.23, es 3.31, de 4.25, pt 4.37, fr 4.52, ko 4.60 (CER)
- **5–10:** ja 5.29 (CER), id 5.37, yue 6.13 (CER), vi 6.15, ru 6.25, th 6.89 (CER), zh 7.14 (CER), nl 7.43, hi 7.84, tr 9.46, ms 10.42
- **10–20:** pl 12.50, ar 14.91, mk 18.22, sv 19.68
- **20–30:** ro 20.46, da 21.23, cs 22.97, fil 24.29, fi 25.48, fa 28.29, el 29.22
- **Over 30:** hu 32.84

- English FLEURS 3.23 is close to the upstream family card's 3.35 for the 1.7B offline (**Reported**).[^qwen3-asr-readme] The protocols differ, so the gap is not a measured change (**Synthesis**).
- Vietnamese FLEURS 6.15 is close to the 5.55 offline 1.7B figure that [Qwen3-ASR family](qwen3-asr-family.md) takes from the technical report appendix (**Reported** there). The protocols are not shared, so neither figure is a matched comparison for [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) (**Synthesis**).

### Performance keys

- Frontmatter RTF keys: `rtf_m4_max` cpu 9.59 and metal 41.08; `rtf_ryzen_4750u` cpu 2.47 and vulkan 4.08 (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- The card defines no unit, input, or protocol for these keys. The values rise with the faster backend, so they read as an "x realtime" speed multiplier rather than a conventional real-time factor (time divided by audio duration) (**Synthesis**). The key says M4 Max while the WER note says Apple M4 (**Observed**). They are not comparable with CSTR's "0.2x realtime" timing without a unit check (**Synthesis**).

## Provenance

- Port source: upstream `Qwen/Qwen3-ASR-1.7B` at commit `7278e1e`, pinned 2026-04-19. Validation: the `qwen_asr` 0.0.6 reference, checked at transcribe.cpp commit `3f61df7` on 2026-04-20 (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card] The validation numbers sit on a linked model page that is not captured.
- The capture has no GGUF-repository revision, upload date, or per-figure commit. The card says "figures without a commit were published before provenance was recorded" but does not mark which figures those are (**Observed**).[^handy-computer-qwen3-asr-1.7b-gguf-card]
- The card reproduces the upstream model card at `7278e1e` and calls it authoritative (**Observed**).[^handy-computer-qwen3-asr-1.7b-gguf-card] Its benchmark lineage matches [Qwen3-ASR family](qwen3-asr-family.md).
- Organization identity: the card names `handy-computer`. The wiki's [transcribe.cpp](transcribe-cpp.md) concept treats it as the Handy runtime, and community threads name a Handy dictation app ([Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md)). This capture does not establish whether these are one project (**Synthesis**).

## Relationships

- Depends on [Qwen3-ASR family](qwen3-asr-family.md): the upstream checkpoint this package quantizes. Dialects, serving, and benchmarks beyond this card's tables stay on that concept (**Synthesis**).
- Uses [transcribe.cpp](transcribe-cpp.md): the runtime for build, bindings, and quantization. Its `transcribe-quantize` presets (F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M) match this ladder plus BF16 (**Synthesis**).
- Sibling packagings of the same 1.7B checkpoint: [CSTR Qwen3-ASR-1.7B GGUF](cstr-qwen3-asr-1.7b-gguf.md) for CrispASR and [ggml-org Qwen3-ASR-1.7B GGUF](ggml-org-qwen3-asr-1.7b-gguf.md) for llama.cpp. This card is the only one of the three with a per-quant WER table. The CSTR card attributes its fix for an encoder-at-Q4_K failure to keeping the audio encoder at Q8_0. This card does not say whether its encoder is quantized separately, so its Q4_K_M row is no evidence either way on that failure mode (**Synthesis**).

## Contradictions

- **Chinese FLEURS:** this card reports zh CER 7.14 for Q8_0 (**Reported**).[^handy-computer-qwen3-asr-1.7b-gguf-card] The upstream family table reports Fleurs-zh 2.41 for the 1.7B under a WER-labeled header (**Reported**).[^qwen3-asr-readme] The metric label and protocol differ, so neither value is chosen here.

## Coverage and limits

- Entry point: one model-card capture, `raw/handy-computer-Qwen3-ASR-1.7B-gguf.md`, inspected statically in full (**Observed**), including the embedded upstream card reproduction.
- Not captured or executed: the six GGUF files and checksums; the transcribe.cpp model page (`docs/models/qwen3-asr-1.7b.md`) with validation numbers and reproduction steps; `scripts/wer/run.py` and `scripts/wer/score.py`; the `qwen_asr` 0.0.6 reference; and transcribe.cpp commit `3f61df7`. Nothing was downloaded, built, converted, transcribed, or benchmarked.
- Open provenance: the bootstrap CI values, the 0.6B quantization comparison, and the set of figures that predate commit tracking are absent from the capture.
- Language coverage is the 30-language list only; this package declares no dialects and no language-hint input.
- Time-sensitive: `stale_after: 2027-10-13` per the `stt` domain rule.
- No sensitive values were found in the capture (**Observed**).
- Status is `draft` because the validation page, per-file revision, and figure-provenance questions are open.

[^handy-computer-qwen3-asr-1.7b-gguf-card]: [handy-computer Qwen3-ASR-1.7B-gguf model card](../raw/handy-computer-Qwen3-ASR-1.7B-gguf.md) — locators: frontmatter (`base_model`, `base_model_relation: quantized`, `library_name`, `pipeline_tag`, `language` list, `transcribe_cpp` block with `streaming`, `translate`, `lang_detect`, `timestamps`, `wer_librispeech_test_clean`, `wer_fleurs_*` and `cer_fleurs_*` keys, `rtf_*` keys); intro paragraph (upstream commit `7278e1e` pinned 2026-04-19; transcribe.cpp commit `3f61df7` validation 2026-04-20; offline, 30-language auto-detection, 16 kHz mono WAV, no language hints); `Downloads` table (six quant rows, sizes, LibriSpeech WER); paragraph after the table (protocol, Apple M4, English-only, bootstrap CI and ~0.2-point claim, commit-provenance sentence, `scripts/wer/` pointer); `Usage` fences; `License`; `Original Model Card` section (reproduction at commit `7278e1e`, "authoritative" note).
[^qwen3-asr-readme]: [Qwen3-ASR README and model card](../raw/Qwen3-ASR-0.6B.md) — locators: `ASR Benchmarks on Public Datasets (WER ↓)` table, English block row `Fleurs-en` (Qwen3-ASR-1.7B column 3.35) and Chinese block row `Fleurs-zh` (Qwen3-ASR-1.7B column 2.41); `Evaluation` section (bfloat16, vLLM, greedy, no language parameter).
