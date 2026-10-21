---
type: Concept
title: Voxtral Mini 4B Realtime Arabic
description: Mistral AI Arabic-dialect and MSA streaming ASR fine-tune of Voxtral Mini 4B Realtime 2602 (~4.4B params, BF16, Apache-2.0) reporting 8.82% average CER at 480 ms delay across seven Arabic benchmarks, with code-switching focus and vLLM/Transformers serving.
tags: [stt, asr, streaming, realtime, arabic, code-switching]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T18:00:00Z }
stale_after: 2027-04-21
sources:
  - id: voxtral-arabic-card
    resource: ../raw/Voxtral-Mini-4B-Realtime-Arabic.md
    kind: documentation
    title: Voxtral Mini 4B Realtime Arabic model card
---

Voxtral Mini 4B Realtime Arabic (`mistralai/Voxtral-Mini-4B-Realtime-Arabic`) is a streaming speech-to-text model for Modern Standard Arabic and Arabic dialects, fine-tuned from [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md), with ~4.4B parameters in BF16, a causal audio encoder plus language decoder over 16 kHz audio, a configurable transcription delay, and a vendor-reported 8.82% average CER at 480 ms across seven Arabic benchmarks, 0.91 points behind the offline Voxtral Transcribe Arabic (7.91%) (**Reported**).[^voxtral-arabic-card]

## Identity and release

- Fine-tuned from `mistralai/Voxtral-Mini-4B-Realtime-2602` (frontmatter `base_model`); `library_name: vllm`, `pipeline_tag: automatic-speech-recognition`, `inference: false`; weights Apache-2.0 with a third-party-rights usage disclaimer (**Observed** by static inspection).[^voxtral-arabic-card]
- Frontmatter lists 16 language codes: `ar` (MSA); Maghreb `ary`, `ayl`, `aeb`, `arq`, `mey`; Gulf `afb`, `ars`, `acx`, `ayn`; Nile Valley `arz`, `apd`; Levantine `acm`, `ajp`, `apc`; and Chadian `shu` (**Observed** by static inspection).[^voxtral-arabic-card]
- Positioned for challenging real-world audio and **code-switching** (speakers alternating languages within a conversation); the card also reports improvements on code-switching with languages outside the training focus, without numbers (**Reported**).[^voxtral-arabic-card]
- Co-developed with Morocco's Ministère de la Transition Numérique et de la Réforme Administrative (MTNRA) under a January 2026 Mistral–Morocco partnership, described as a sovereign AI asset (**Reported**).[^voxtral-arabic-card]
- Supplementary pointers: a WebGPU browser demo Space backed by a community ONNX checkpoint (`onnx-community/Voxtral-Mini-4B-Realtime-Arabic-ONNX`); neither was fetched (**Observed**).[^voxtral-arabic-card]

## Benchmarks and protocol

- Headline: 8.82% average CER at a configured 480 ms transcription delay over seven Arabic benchmarks; the card says it outperforms several open-source and proprietary offline models and is within 0.91 points of Voxtral Transcribe Arabic's 7.91% CER (**Reported**; the 0.91 gap equals 8.82 − 7.91).[^voxtral-arabic-card]
- Two new benchmarks, ISMA and Darija in the Wild, were co-developed with MTNRA alongside established Arabic benchmarks; lower CER is better (**Reported**).[^voxtral-arabic-card]
- Protocol: temperature 0.0; 480 ms delay; CER computed after `normalize_arabic_asr` (from `normalization.py`) co-developed with MTNRA, covering dialect-specific spelling, clitics, loanwords, and spoken numbers. Scores may differ under other normalization (**Reported**).[^voxtral-arabic-card]
- Gemini's safety filters block transcription of some FLEURS samples, a caveat on the proprietary-baseline comparison (**Reported**).[^voxtral-arabic-card]
- Per-benchmark scores, delay-sweep results, competitor names, and the ISMA/Darija composition live only in three images (`assets/avg_evals_by_delay.png`, `benchmark_scores.png`, `benchmark_composition.png`) that are not in `raw/`; no per-benchmark figure is recorded here (**Observed** limit).[^voxtral-arabic-card]
- Comparability: this is CER under MTNRA normalization at 480 ms, whereas [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md) reports average WER/CER on the Open Universal Arabic leaderboard (25.87 / 11.80). The two sets of numbers use different benchmark suites and normalization, so no ranking follows (**Synthesis**).[^voxtral-arabic-card]

## Usage

- **vLLM:** `pip install --upgrade vllm "mistral-common[audio]"`, then `vllm serve mistralai/Voxtral-Mini-4B-Realtime-Arabic`; stream audio over WebSocket to `/v1/realtime`, adapting the vLLM realtime example (**Reported**).[^voxtral-arabic-card]
- **Transformers:** native from `transformers >= 5.2.0` via `VoxtralRealtimeForConditionalGeneration` and `AutoProcessor`, plus `accelerate` and `mistral-common[audio]`. The example resamples a sample WAV (`assets/bank-take-2.wav`) to the feature extractor's rate, calls `generate(do_sample=False)`, and decodes with `skip_special_tokens=True`; this is file-based, not live streaming (**Reported**).[^voxtral-arabic-card]
- The card does not restate the base model's delay-setting (`transcription_delay_ms` in `tekken.json`, 80 ms steps), serving flags, context-length rule, or ≥16 GB GPU guidance. Those are documented for the base in [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md); applying them to this checkpoint is an unverified inference (**Synthesis**).[^voxtral-arabic-card]

## Limitations

- Targets Arabic transcription only; for other languages the card directs users to the original Voxtral Mini 4B Realtime (**Reported**).[^voxtral-arabic-card]
- No training data, recipe, parameter breakdown, latency/throughput, or VRAM figure is given beyond ~4.4B BF16 (**Observed** absence).[^voxtral-arabic-card]

## Relationships

- Fine-tuned from [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md); inherits its causal-encoder streaming design and delay knob, while the base covers 13 languages (including `ar`) and this model narrows to Arabic (**Reported** lineage; delay inheritance **Synthesis**).[^voxtral-arabic-card]
- Alternative to [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md): this model is natively streaming with a tunable delay and targets code-switching, while the Cohere model is offline with auto-chunked long-form and no stated streaming mode; their reported metrics are not comparable (**Synthesis**).[^voxtral-arabic-card]
- Compared in the [ASR/STT Model Survey](asr-stt-model-survey.md) catalog and its Arabic guidance (**Synthesis**).[^voxtral-arabic-card]

## Coverage and limits

- The whole single capture was inspected statically: frontmatter, intro, usage, benchmarks prose, emerging capabilities, limitations, and license. No model download, vLLM serve, transcription, or benchmark was run (**Synthesis**).[^voxtral-arabic-card]
- Not inspected or absent from `raw/`: the three benchmark images, `normalization.py`, `assets/bank-take-2.wav`, the demo Space, ONNX checkpoint, vLLM example, Transformers docs, weights, and any revision identifier (**Observed** limit).[^voxtral-arabic-card]
- All accuracy and capability claims are vendor assertions; `stale_after: 2027-04-21` follows the `stt` domain rule for model releases and benchmark numbers (**Synthesis**).[^voxtral-arabic-card]

[^voxtral-arabic-card]: [Voxtral Mini 4B Realtime Arabic model card](../raw/Voxtral-Mini-4B-Realtime-Arabic.md) — locators: frontmatter (`library_name`, 16-code `language` list, `pipeline_tag`, `inference`, `tags`, `base_model`, `metrics` cer/wer); top note (WebGPU Space and ONNX checkpoint); intro paragraphs (Arabic dialect/MSA scope, code-switching, ~4.4B BF16, 16 kHz causal encoder, 480 ms 8.82% CER, 0.91-point gap to 7.91%, MTNRA partnership); `Usage > vLLM`, `> Transformers` (>= 5.2.0 and example fence); `Benchmarks` (ISMA/Darija, three image references, temperature 0.0, 480 ms, MTNRA normalization and `normalize_arabic_asr` example, Gemini FLEURS note); `Emerging capabilities`; `Limitations`; `License` (Apache-2.0 and third-party-rights disclaimer).
