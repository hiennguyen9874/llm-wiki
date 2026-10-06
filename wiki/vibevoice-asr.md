---
type: Concept
title: VibeVoice-ASR
description: Unified long-form ASR model transcribing up to 60 minutes in a single pass with speaker, timestamp, and hotword-guided output across 50+ languages.
tags: [stt, long-form, speaker-attribution, hotwords, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T09:25:39Z }
stale_after: 2027-10-06
sources:
  - id: vibevoice-asr-card
    resource: ../raw/VibeVoice-ASR.md
    kind: documentation
    title: VibeVoice-ASR model card
---

VibeVoice-ASR is Microsoft Research's unified long-form speech-to-text model that transcribes up to 60 minutes of continuous audio in a single pass, producing structured Who (speaker), When (timestamps), and What (content) output with user-supplied customized hotwords across 50+ languages (**Reported**).[^vibevoice-asr-card]

## Model identity and release

- Card title is `VibeVoice-ASR`; creator is Microsoft Research via the contact address; code is `github.com/microsoft/VibeVoice` and live demo is `aka.ms/vibevoice-asr` (**Reported**).[^vibevoice-asr-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, `license: mit`, a 50+ entry `language` list, and tags `ASR`, `Transcriptoin` [sic], `Diarization`, and `Speech-to-Text` (**Observed** by static inspection).[^vibevoice-asr-card]
- Technical report is `arXiv:2601.18184` linked as `VibeVoice-ASR Technical Report`; finetuning and vLLM entry points are linked as `finetuning-asr/README.md` and `docs/vibevoice-vllm-asr.md`; installation and usage are deferred to the GitHub repository rather than specified in the card (**Reported**).[^vibevoice-asr-card]

## Capabilities

- 60-minute single-pass processing: accepts up to 60 minutes of continuous audio within 64K token length, contrasted with conventional chunked ASR that slices audio into short chunks and loses global context, to keep consistent speaker tracking and semantic coherence across the hour (**Reported**).[^vibevoice-asr-card]
- Customized hotwords: users can provide names, technical terms, or background info to guide recognition and improve accuracy on domain-specific content (**Reported**).[^vibevoice-asr-card]
- Rich transcription (Who, When, What): jointly performs ASR, diarization, and timestamping, producing structured output indicating who said what and when (**Reported**).[^vibevoice-asr-card]
- Multilingual and code-switching support: supports over 50 languages with no explicit language setting and natively handles code-switching within and across utterances; a language-distribution figure is referenced for the coverage mix (**Reported**).[^vibevoice-asr-card]

## Evaluation

- An `Evaluation` section embeds `figures/DER.jpg`, `figures/cpWER.jpg`, and `figures/tcpWER.jpg`, but the figure files are absent from `raw/` and no metric value, test set, baseline, or protocol is stated in text, so no DER, cpWER, or tcpWER figure is compiled here (**Synthesis**).[^vibevoice-asr-card]
- The architecture figure `figures/VibeVoice_ASR_archi.png` and the language-distribution figure `figures/language_distribution_horizontal.png` are likewise referenced but absent from `raw/` and were not inspected (**Synthesis**).[^vibevoice-asr-card]

## Relationships

- Streaming sibling: [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) covers the 1.5B unified streaming ASR model for continuous speaker-attributed transcription with hotwords across 10 languages, while this concept covers the offline long-form model for up to 60-minute single-pass Who/When/What output across 50+ languages; no shared checkpoint or streaming mechanism is asserted (**Synthesis**).[^vibevoice-asr-card]
- Streaming sibling: [VibeVoice-ASR-Streaming-7B](vibevoice-asr-streaming-7b.md) covers the larger 7B-scale unified streaming ASR model with the same 10-language streaming scope, while this concept covers the 60-minute 50+ language offline card; no size or performance comparison is inferred here (**Synthesis**).[^vibevoice-asr-card]
- Brand sibling with distinct task: [VibeVoice-1.5B](vibevoice-1.5b.md) covers a long-form multi-speaker TTS model with 7.5 Hz continuous tokenizers and diffusion-head synthesis, while this concept covers long-form ASR with joint diarization and timestamping; no shared checkpoint or codebase is asserted (**Synthesis**).[^vibevoice-asr-card]
- Speaker-attribution comparison: [Nemotron 3 Diarization](nemotron-3-diarization.md) covers a dedicated streaming/offline diarization model for up to eight speakers with DER/RTFx benchmarks, while this concept covers a unified ASR model that jointly performs diarization without a separate diarization stage described; no shared method is asserted (**Synthesis**).[^vibevoice-asr-card]
- Streaming ASR comparison: [Audio8 ASR Infinite](audio8-asr-infinite.md) covers a native streaming bilingual Chinese-English ASR model with selectable clock, transcription delay, rolling KV cache, and semantic VAD, while this concept covers an offline 60-minute single-pass model with hotwords and code-switching but no published clock, delay, or cache design; no shared architecture is asserted (**Synthesis**).[^vibevoice-asr-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no checkpoint downloaded, no audio transcribed, and no 60-minute, speaker-tracking, hotword, multilingual, or code-switching claim reproduced (**Synthesis**).[^vibevoice-asr-card]
- Linked but unfetched and not in `raw/`: GitHub repository `microsoft/VibeVoice`, live playground `aka.ms/vibevoice-asr`, technical report `arXiv:2601.18184`, finetuning README, vLLM doc, all five `figures/` images, and any checkpoint weights (**Synthesis**).[^vibevoice-asr-card]
- All capability, language-scope, and release claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^vibevoice-asr-card]

[^vibevoice-asr-card]: [VibeVoice-ASR model card](../raw/VibeVoice-ASR.md) — locators: frontmatter (`language`, `license`, `pipeline_tag`, `library_name`, `tags`); H1/H2 title plus intro paragraph (60-minute long-form single pass, Who/Speaker plus When/Timestamps plus What/Content, customized hotwords, 50+ languages; code `microsoft/VibeVoice`, demo `aka.ms/vibevoice-asr`, report `arXiv:2601.18184`, finetuning `finetuning-asr/README.md`, vLLM `docs/vibevoice-vllm-asr.md` links; `VibeVoice_ASR_archi.png` reference); `Key Features` section (60-minute 64K-token bullet, customized-hotwords bullet with names/technical terms/background info, rich-transcription Who/When/What bullet, multilingual code-switching bullet with no-explicit-language-setting and language-distribution pointer); `Evaluation` section (`DER.jpg`, `cpWER.jpg`, `tcpWER.jpg` references); `Installation and Usage` section (GitHub README pointer); `Language Distribution` section (`language_distribution_horizontal.png` reference); `License` section (MIT); `Contact` section (Microsoft Research, `VibeVoice@microsoft.com`).
