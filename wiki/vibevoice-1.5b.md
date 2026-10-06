---
type: Concept
title: VibeVoice-1.5B
description: Open-source long-form multi-speaker TTS model with 7.5 Hz continuous tokenizers, Qwen2.5-1.5B backbone and diffusion head, synthesizing up to 90 minutes with up to 4 speakers.
tags: [tts, multi-speaker, long-form]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: vibevoice-1-5b-card
    resource: ../raw/VibeVoice-1.5B.md
    kind: documentation
    title: VibeVoice-1.5B model card
---

VibeVoice-1.5B is Microsoft Research's open-source text-to-speech model for expressive long-form multi-speaker conversational audio such as podcasts, combining a Qwen2.5-1.5B backbone with 7.5 Hz continuous acoustic and semantic tokenizers and a diffusion head to synthesize up to 90 minutes with up to 4 distinct speakers (**Reported**).[^vibevoice-1-5b-card]

## Model identity and release

- Name is VibeVoice-1.5B; framework is VibeVoice; creator is Microsoft Research; frontmatter declares `pipeline_tag: text-to-speech`, `library_name: transformers`, languages `en, zh`, license `mit`, and tag `Podcast` (**Observed** by static inspection of frontmatter, **Reported** for authorship and framework positioning).[^vibevoice-1-5b-card]
- Linked entry points are the technical report `arXiv:2508.19205`, project page `microsoft.github.io/VibeVoice`, and code repository `github.com/microsoft/VibeVoice`; installation is deferred to the GitHub README rather than specified in the card (**Reported**).[^vibevoice-1-5b-card]
- Variant table lists `VibeVoice-0.5B-Streaming` (Hugging Face `microsoft/VibeVoice-Realtime-0.5B`), `VibeVoice-1.5B` with 64K context and ~90 min generation ("You are here"), and `VibeVoice-Large` with 32K context and ~45 min generation marked Disabled (**Reported**).[^vibevoice-1-5b-card]

## Architecture and training

- Design goal is long-form multi-speaker dialogue synthesis, addressing scalability, speaker consistency, and natural turn-taking limits of traditional TTS (**Reported**).[^vibevoice-1-5b-card]
- Core mechanism is continuous speech tokenizers (Acoustic plus Semantic) at an ultra-low 7.5 Hz frame rate to preserve fidelity while improving long-sequence efficiency, plus a next-token diffusion framework in which the LLM models textual context and dialogue flow and a diffusion head generates acoustic detail (**Reported**).[^vibevoice-1-5b-card]
- Backbone LLM is `Qwen/Qwen2.5-1.5B`; text-tokenizer choice is not explicitly specified beyond the Qwen2.5 default (**Reported**).[^vibevoice-1-5b-card]
- Acoustic tokenizer is a σ-VAE variant from `LatentLM` (`arXiv:2412.08635`) with a mirror-symmetric encoder-decoder of 7 stages of modified Transformer blocks, 3200× downsampling from 24 kHz input, and ~340M parameters each for encoder and decoder (**Reported**).[^vibevoice-1-5b-card]
- Semantic tokenizer encoder mirrors the acoustic tokenizer architecture without VAE components and is trained with an ASR proxy task (**Reported**).[^vibevoice-1-5b-card]
- Diffusion head is a lightweight 4-layer ~123M-parameter module conditioned on LLM hidden states, predicting acoustic VAE features with a DDPM process and using Classifier-Free Guidance (CFG) and DPM-Solver variants at inference (**Reported**).[^vibevoice-1-5b-card]
- Training uses a curriculum up to 65,536 tokens: tokenizers are pre-trained separately then frozen, and only LLM plus diffusion-head parameters are trained with input-length curriculum 4K → 16K → 32K → 64K (**Reported**).[^vibevoice-1-5b-card]

## Capabilities and constraints

- Synthesizes up to 90 minutes with up to 4 distinct speakers, positioned as surpassing typical 1–2 speaker limits of prior models (**Reported**).[^vibevoice-1-5b-card]
- Supported languages are English and Chinese only; other-language transcripts may produce unexpected, unintelligible, or offensive output (**Reported**).[^vibevoice-1-5b-card]
- Speech-only scope: no coherent background ambience, Foley, music, background noise, or sound effects; overlapping speech segments are not explicitly modeled or generated (**Reported**).[^vibevoice-1-5b-card]
- Inherits biases, errors, and omissions of the Qwen2.5-1.5B base model; outputs may still be unexpected, biased, or inaccurate despite optimization (**Reported**).[^vibevoice-1-5b-card]

## Intended use and prohibitions

- Direct intended use is research exploration of highly realistic audio dialogue generation as detailed in the tech report; commercial or real-world use without further testing and development is not recommended (**Reported**).[^vibevoice-1-5b-card]
- Out-of-scope uses listed are violating applicable laws including trade-compliance laws, uses prohibited by the MIT License, generating any text transcript, non-consensual voice impersonation (satire, advertising, ransom, social engineering, authentication bypass), disinformation or impersonation presented as genuine recordings, real-time or low-latency voice conversion for live telephone or video-conference deepfakes, unsupported languages, and non-speech ambience/Foley/music generation (**Reported**).[^vibevoice-1-5b-card]
- Misuse risks called out are convincing fake audio for impersonation, fraud, or disinformation; users must verify transcript reliability and content accuracy, deploy lawfully, and disclose AI generation when sharing content (**Reported**).[^vibevoice-1-5b-card]
- Stated mitigations are an audible AI disclaimer embedded in every synthesized file, an imperceptible provenance watermark, hashed inference-request logging for abuse-pattern detection with quarterly aggregate statistics, and repository updates when undesired behavior is reported or found; users remain responsible for lawful and ethical dataset sourcing including rights and anonymization plus data-privacy care (**Reported**).[^vibevoice-1-5b-card]

## Relationships

- Long-form multi-speaker comparison: [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md) covers a 0.5B multilingual zero-shot TTS model with base and RL checkpoints and pronunciation inpainting, while this concept covers a 1.5B long-form conversational TTS model with 7.5 Hz continuous tokenizers and a diffusion head for up to 90-minute 4-speaker output; no shared codebase is asserted (**Synthesis**).[^vibevoice-1-5b-card]
- Streaming TTS comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B streaming zero-shot TTS model with saved-speaker reuse and vLLM/TRT-LLM serving mentions, while this concept covers a non-streaming long-form research model with frozen tokenizers and curriculum-trained LLM plus diffusion head; no shared vendor or codebase is asserted (**Synthesis**).[^vibevoice-1-5b-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice design/direction and H100 TTFA/RTF figures, while this concept covers a research-only long-form podcast model with explicit prohibitions on real-time voice conversion and commercial use; no shared vendor or codebase is asserted (**Synthesis**).[^vibevoice-1-5b-card]
- Voice-cloning comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a compact multilingual zero-shot voice-cloning TTS model with DualAR architecture and ONNX/SGLang paths, while this concept covers a larger long-form multi-speaker model focused on speaker consistency and turn-taking over up to 90 minutes; no shared codebase is asserted (**Synthesis**).[^vibevoice-1-5b-card]
- Packaged variant: [VibeVoice-7B GGUF](vibevoice-7b-gguf.md) covers a Q8_0 GGUF distribution of the larger 7B checkpoint for the audio.cpp runtime with CLI/server/WebUI usage and RTX 5090 sanity-check figures, while this concept covers the 1.5B research checkpoint with 7.5 Hz tokenizers and diffusion-head architecture; no shared weight file is asserted (**Synthesis**).[^vibevoice-1-5b-card]
- Brand sibling with distinct task: [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) covers a unified streaming ASR model for speaker-attributed transcription with hotwords across 10 languages, while this concept covers long-form multi-speaker TTS synthesis; no shared checkpoint is asserted (**Synthesis**).[^vibevoice-1-5b-card]
- Streaming family sibling: [VibeVoice-Realtime-0.5B](vibevoice-realtime-0.5b.md) covers the 0.5B single-speaker realtime streaming variant with acoustic-only 7.5 Hz tokens and ~300 ms first audio, while this concept covers the 1.5B long-form multi-speaker model with acoustic plus semantic tokenizers and up to 90-minute 4-speaker output; no shared checkpoint is asserted (**Synthesis**).[^vibevoice-1-5b-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no checkpoint downloaded, no audio synthesized, and no 90-minute, 4-speaker, 7.5 Hz efficiency, 3200× downsampling, or watermark/disclaimer claims reproduced (**Synthesis**).[^vibevoice-1-5b-card]
- Overview figure `figures/Fig1.png` is referenced but absent from `raw/` and was not inspected; technical report, project page, GitHub README/code, Hugging Face streaming weights, Qwen2.5-1.5B weights, and LatentLM paper were linked but not fetched and are not in `raw/` (**Synthesis**).[^vibevoice-1-5b-card]
- Sibling file `raw/VibeVoice-Realtime-0.5B.md` is now compiled as [VibeVoice-Realtime-0.5B](vibevoice-realtime-0.5b.md); `raw/VibeVoice-ASR.md` is compiled as [VibeVoice-ASR](vibevoice-asr.md); `raw/VibeVoice-ASR-Streaming-7B.md` is compiled as [VibeVoice-ASR-Streaming-7B](vibevoice-asr-streaming-7b.md) and `raw/VibeVoice-ASR-Streaming-7B-GGUF.md` as [VibeVoice-ASR-Streaming-7B GGUF](vibevoice-asr-streaming-7b-gguf.md); `raw/VibeVoice-7B-GGUF.md` is compiled as [VibeVoice-7B GGUF](vibevoice-7b-gguf.md) and `raw/VibeVoice-ASR-Streaming-1.5B.md` as [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) (**Synthesis**).[^vibevoice-1-5b-card]
- All architecture, training, capability, language-scope, and mitigation claims are source assertions without independent verification in this wiki; release and capability figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^vibevoice-1-5b-card]

[^vibevoice-1-5b-card]: [VibeVoice-1.5B model card](../raw/VibeVoice-1.5B.md) — locators: frontmatter (`language`, `license`, `pipeline_tag`, `library_name`, `tags`); intro paragraphs (long-form multi-speaker podcast goal, scalability/consistency/turn-taking challenges, 7.5 Hz Acoustic/Semantic tokenizers, next-token diffusion with LLM plus diffusion head, 90-minute 4-speaker claim, technical-report/project-page/code links, `Fig1.png` reference); `Training Details` section (Qwen2.5-1.5B LLM, σ-VAE LatentLM acoustic tokenizer with 7-stage Transformer blocks / 3200× downsampling from 24 kHz / ~340M encoder/decoder, semantic-tokenizer mirror without VAE plus ASR proxy task, 4-layer ~123M diffusion head with DDPM/CFG/DPM-Solver conditioning, 65,536-token curriculum, frozen-tokenizer two-stage training with 4K→16K→32K→64K curriculum); `Models` table (0.5B-Streaming HF link, 1.5B 64K/~90 min "You are here", Large 32K/~45 min Disabled); `Installation and Usage` section (GitHub README pointer); `Responsible Usage` section (research-only intended use, out-of-scope list including legal/MIT, transcript, impersonation, disinformation, live conversion, unsupported-language, ambience/Foley/music bullets); `Risks and limitations` section (unexpected/biased/inaccurate outputs, Qwen2.5 inheritance, deepfake warning, English/Chinese-only, non-speech, overlapping-speech bullets); `Recommendations` section (non-commercial research-only warning, audible disclaimer, imperceptible watermark, hashed-logging plus quarterly statistics, dataset rights/anonymization/privacy bullets).
