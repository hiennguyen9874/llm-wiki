---
type: Concept
title: VibeVoice-ASR-Streaming-1.5B
description: Unified streaming ASR model for speaker-attributed transcription with customized hotwords across 10 languages.
tags: [stt, streaming, speaker-attribution, hotwords, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T16:30:00Z }
stale_after: 2027-10-06
sources:
  - id: vibevoice-asr-streaming-1-5b-card
    resource: ../raw/VibeVoice-ASR-Streaming-1.5B.md
    kind: documentation
    title: VibeVoice-ASR-Streaming-1.5B model card
---

VibeVoice-ASR-Streaming-1.5B is Microsoft Research's unified streaming ASR model that continuously transcribes who said what as speech arrives, with user-supplied customized hotwords and support for 10 languages (**Reported**).[^vibevoice-asr-streaming-1-5b-card]

## Model identity and release

- Card title is `VibeVoice-ASR-Streaming-1.5B`; creator is Microsoft Research via the contact address; code is `github.com/microsoft/VibeVoice` and live demo is `aka.ms/vibeasr` (**Reported**).[^vibevoice-asr-streaming-1-5b-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, `license: mit`, 10 frontmatter languages, and tags `ASR`, `Transcription`, `Speech-to-Text`, and `Streaming` (**Observed** by static inspection).[^vibevoice-asr-streaming-1-5b-card]
- Technical report is `arXiv:2609.02812` linked as `VibeVoice-ASR-Streaming Technical Report`; installation and usage are deferred to the GitHub repository rather than specified in the card (**Reported**).[^vibevoice-asr-streaming-1-5b-card]

## Capabilities

- Streaming speaker-attributed transcription: continuously transcribes who said what as speech arrives (**Reported**).[^vibevoice-asr-streaming-1-5b-card]
- Customized hotwords: users can provide names and technical terms to improve recognition of domain-specific content (**Reported**).[^vibevoice-asr-streaming-1-5b-card]
- Multilingual support across 10 languages: Chinese, English, French, German, Italian, Japanese, Korean, Portuguese, Russian, and Spanish (**Reported**).[^vibevoice-asr-streaming-1-5b-card]

## Evaluation

- An `Evaluation` section embeds `figures/VibeVoice_ASR_Streaming_results.png`, but the figure file is absent from `raw/` and no metric, test set, baseline, or protocol is stated in text, so no accuracy or latency figure is compiled here (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- The architecture figure `figures/VibeVoice_ASR_Streaming_architecture.png` is likewise referenced but absent from `raw/` and was not inspected (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]

## Relationships

- Brand sibling with distinct task: [VibeVoice-1.5B](vibevoice-1.5b.md) covers a long-form multi-speaker TTS model with 7.5 Hz continuous tokenizers and diffusion-head synthesis, while this concept covers a streaming ASR model for speaker-attributed transcription with hotwords; no shared checkpoint or codebase is asserted (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- Streaming ASR comparison: [Audio8 ASR Infinite](audio8-asr-infinite.md) covers a native streaming bilingual Chinese-English ASR model with selectable 80/120/160 ms clock, transcription delay, rolling KV cache, and semantic VAD, while this concept covers a 10-language streaming model with speaker attribution and hotwords but no published clock, delay, or cache design; no shared architecture is asserted (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- Speaker-attribution comparison: [Nemotron 3 Diarization](nemotron-3-diarization.md) covers a dedicated streaming/offline diarization model for up to eight speakers with DER/RTFx benchmarks, while this concept covers a unified streaming ASR model that jointly transcribes who said what without a separate diarization stage described; no shared method is asserted (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- Packaged 7B deployment: [VibeVoice-ASR-Streaming-7B GGUF](vibevoice-asr-streaming-7b-gguf.md) covers the audio.cpp GGUF distribution of the larger 7B checkpoint (BF16/Q8_0/Q4_K, CLI/server plus 16 kHz live endpoint), while this concept covers the 1.5B model card with no deployment packaging; no shared weight file is asserted (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no checkpoint downloaded, no audio transcribed, and no speaker-attribution, hotword, multilingual, or latency claim reproduced (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- Linked but unfetched and not in `raw/`: GitHub repository `microsoft/VibeVoice`, live playground `aka.ms/vibeasr`, technical report `arXiv:2609.02812`, both `figures/` images, and any checkpoint weights (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- Sibling `raw/VibeVoice-ASR-Streaming-7B.md` matches this source except for its H2 checkpoint title in this snapshot, so no 7B parameter or performance claim is inferred from this 1.5B card; the 7B card is now compiled separately as [VibeVoice-ASR-Streaming-7B](vibevoice-asr-streaming-7b.md), and `raw/VibeVoice-ASR-Streaming-7B-GGUF.md` (audio.cpp packaging) is compiled as [VibeVoice-ASR-Streaming-7B GGUF](vibevoice-asr-streaming-7b-gguf.md), while `raw/VibeVoice-ASR.md` (offline 60-minute 50+ language Who/When/What model) is now compiled as [VibeVoice-ASR](vibevoice-asr.md) and `raw/VibeVoice-Realtime-0.5B.md` was inventoried but not ingested in this operation and remains uncompiled (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]
- All capability, language-scope, and release claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^vibevoice-asr-streaming-1-5b-card]

[^vibevoice-asr-streaming-1-5b-card]: [VibeVoice-ASR-Streaming-1.5B model card](../raw/VibeVoice-ASR-Streaming-1.5B.md) — locators: frontmatter (`language`, `license`, `pipeline_tag`, `library_name`, `tags`); H1/H2 title plus intro paragraph (unified streaming ASR, Who/Speaker plus What/Content, hotwords, 10 languages; code `microsoft/VibeVoice` and demo `aka.ms/vibeasr` links; `VibeVoice_ASR_Streaming_architecture.png` reference); `Key Features` section (streaming speaker-attributed transcription bullet, customized-hotwords bullet with names/technical terms, multilingual bullet listing Chinese/English/French/German/Italian/Japanese/Korean/Portuguese/Russian/Spanish); `Technical Report` section (`arXiv:2609.02812` link); `Evaluation` section (`VibeVoice_ASR_Streaming_results.png` reference); `Installation and Usage` section (GitHub repository pointer); `License` section (MIT); `Contact` section (Microsoft Research, `VibeVoice@microsoft.com`).
