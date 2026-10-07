---
type: Concept
title: Higgs TTS 3
description: 4B-parameter multilingual expressive TTS model with zero-shot voice cloning, inline emotion/style/prosody/SFX control across 102 languages, and SGLang Omni plus vLLM Omni serving.
tags: [ml, tts, multilingual, voice-cloning, expressive]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:10:00Z }
stale_after: 2027-10-06
sources:
  - id: higgs-v3-card
    resource: ../raw/higgs-audio-v3-tts-4b.md
    kind: documentation
    title: Higgs TTS 3 model card
---

Higgs TTS 3 is a ~4B-parameter autoregressive multilingual text-to-speech model from Boson AI built for conversational voice chat, combining zero-shot voice cloning with inline control over emotion, style, prosody, pauses, and sound effects across 102 languages at single-digit WER/CER, served via SGLang Omni and vLLM Omni with streaming support, under a research/non-commercial license plus a creator-use grant (**Reported**).[^higgs-v3-card]

## Model identity and release

- Title is `Higgs TTS 3`; weights are `bosonai/higgs-tts-3-4b` on Hugging Face; frontmatter declares `library_name: transformers`, `pipeline_tag: text-to-speech`, a 100+ language list, license `other` named `boson-higgs-tts-3-research-and-non-commercial-license`, and tags including `text-to-speech`, `speech-generation`, `voice-agent`, `expressive-speech`, `controllable-tts`, and `multilingual-tts` (**Reported**).[^higgs-v3-card]
- Upstream links are the Boson blog post, Hugging Face model page, SGLang Omni cookbook, sglang-omni and vLLM-Omni repositories, Boson AI API docs, and `contact@boson.ai` for commercial licensing; the card's BibTeX cites `Boson AI, Higgs TTS 3: Conversational Speech for Voice AI, 2026, https://huggingface.co/bosonai/higgs-tts-3-4b` (**Reported**).[^higgs-v3-card]
- Intended use is expressive conversational speech for voice chat ("speaks, not just reads"); production, hosted APIs, embedding in a product or service, and reselling the model require a separate commercial license (**Reported**).[^higgs-v3-card]

## Architecture

- Backbone is a ~4B autoregressive decoder (36 layers, hidden size 2560, GQA 32 query / 8 KV heads) consuming interleaved text and audio tokens, with 8,192-token training sequence length (**Reported**).[^higgs-v3-card]
- Audio is encoded by the Higgs Tokenizer into 8 codebooks of 1,026 entries each at 25 fps (40 ms per frame), staggered via a delay pattern, mapped through a fused single-tensor multi-codebook embedding tied with the text embedding; outputs pass a fused multi-codebook head, are de-delayed, and decoded to 24 kHz waveform (**Reported**).[^higgs-v3-card]

## Supported languages

- 102 languages reach single-digit WER/CER, split into a polished tier (WER/CER under 5, 85 languages) and a usable-but-less-polished tier (WER/CER 5–10, 17 languages) (**Reported**).[^higgs-v3-card]
- Polished tier (<5) includes Afrikaans, Arabic, Armenian, Assamese, Asturian, Azerbaijani, Bashkir, Basque, Belarusian, Bengali, Bosnian, Bulgarian, Catalan, Cebuano, Central Kurdish, Chinese, Croatian, Czech, Danish, Dutch, Eastern Mari, English, Esperanto, Estonian, Finnish, French, Galician, Georgian, German, Greek, Gujarati, Haitian Creole, Hausa, Hebrew, Hindi, Hungarian, Indonesian, Italian, Japanese, Javanese, Kannada, Kazakh, Korean, Kinyarwanda, Kyrgyz, Latvian, Lingala, Lithuanian, Luo, Macedonian, Malay, Malayalam, Maltese, Maori, Marathi, Mongolian, Nepali, Norwegian, Occitan, Persian, Polish, Portuguese, Romanian, Russian, Sepedi, Serbian, Shona, Slovak, Slovene, Spanish, Swahili, Swedish, Tagalog, Tajik, Tamil, Telugu, Thai, Turkish, Ukrainian, Urdu, Uyghur, Uzbek, Vietnamese, Xhosa, and Zulu — so Vietnamese and English voice-clone requests fall in the production-quality tier (**Reported**).[^higgs-v3-card]
- Usable tier (5–10) includes Albanian, Chichewa/Nyanja, Eastern Punjabi, Ganda, Icelandic, Irish, Kabyle, Kabuverdianu, Kamba, Latin, Luxembourgish, Oromo, Pashto, Sindhi, Somali, Umbundu, and Welsh (**Reported**).[^higgs-v3-card]

## Expressive control tokens

- All tags use `<|category:value|>` syntax and can be inserted mid-utterance; delivery-shaping tokens (emotion, style, speed/pitch/expressive prosody) go at the start of `input`, while positional tokens (`<|prosody:pause|>`, `<|prosody:long_pause|>`, `<|sfx:…|>`) go inline where they fire; detailed placement, stacking, and worked examples are delegated to the linked `PROMPTING.md`, which was not present in `raw/` (**Reported**).[^higgs-v3-card]
- Emotion (21): `elation`, `amusement`, `enthusiasm`, `determination`, `pride`, `contentment`, `affection`, `relief`, `contemplation`, `confusion`, `surprise`, `awe`, `longing`, `arousal`, `anger`, `fear`, `disgust`, `bitterness`, `sadness`, `shame`, `helplessness` (**Reported**).[^higgs-v3-card]
- Style (3): `singing`, `shouting`, `whispering` (**Reported**).[^higgs-v3-card]
- Sound effects (9), each paired with its onomatopoeia immediately after the token (e.g. `<|sfx:laughter|>Haha`, `<|sfx:sigh|>Uh`, `<|sfx:sneeze|>Achoo`): `cough` (Ahem), `laughter` (Haha/Hehe), `crying` (Boohoo/Sob), `screaming` (Ahh/Aaah), `burping` (Burp), `humming` (Hmm/Mmm), `sigh` (Uh/Ahh), `sniff` (Sff), `sneeze` (Achoo); the written sound gives the acoustic cue realizing the effect (**Reported**).[^higgs-v3-card]
- Prosody (10): `speed_very_slow` (~0.65x), `speed_slow` (~0.85x), `speed_fast` (~1.2x), `speed_very_fast` (~1.4x), `pitch_low` (~-3 semitones), `pitch_high` (~+2.5 semitones), `pause` (~400–700 ms), `long_pause` (~700–1500 ms), `expressive_high` (more expressive), `expressive_low` (flatter) (**Reported**).[^higgs-v3-card]

## Evaluation

- Multilingual voice-clone WER/CER (down, x100, macro-averaged per benchmark suite; lower is better): Higgs TTS 3 is reported best on all four suites — SeedTTS 1.11, CV3 4.41, MiniMax-Multilingual 2.74, Higgs-Multilingual (internal 111-language set) 3.61 — ahead of Higgs TTS v2 (2.10 / 21.19 / 49.86 / 52.24), Fish Audio S2 Pro (1.31 / 4.60 / 5.15 / 8.68), Qwen3-TTS-1.7B (1.30 / 7.73 / 27.41 / 97.09), OmniVoice (1.21 / 4.92 / 2.98 / 3.63), and six further baselines (VibeVoice-7B, IndexTTS-2, MiMo-Audio-7B-Instruct, MOSS-TTS-v1.5, ChatterBox, FireRedTTS-2) scoring worse per row; the card states numbers are reproducible end-to-end with original metrics and normalization (**Reported**).[^higgs-v3-card]
- Emergent-TTS judge win-rate (up; vs a BASELINE row, same reference audio per prompt, verbatim text with no inline tags): Higgs TTS 3 leads overall at 53.65% and leads the Foreign Words (48.75%), Paralinguistics (68.57%), Questions (61.43%), and Syntactic Complexity (60.71%) columns, trails on Emotions (53.75% vs OmniVoice 61.07% best and MOSS-TTS-v1.5 60.54%) and Complex Pronunciation (25.10% vs Qwen3-TTS-1.7B 30.00% best); Fish Audio S2 Pro (43.80%), Qwen3-TTS-1.7B (38.84%), IndexTTS-2 (31.12%), MOSS-TTS-v1.5 (43.89%), and OmniVoice (40.82%) trail overall (**Reported**).[^higgs-v3-card]

## Serving and throughput

- SGLang Omni is the documented production stack (continuous batching for multi-codebook decoding, same inline tag controls): pull `lmsysorg/sglang-omni:dev`, install the `sglang-omni` checkout (`uv venv`, `uv pip install -e .`), download `bosonai/higgs-tts-3-4b`, and `sgl-omni serve --model-path bosonai/higgs-tts-3-4b --port 8000`; plain synthesis posts `{"input": "…"}` to `/v1/audio/speech` (**Reported**).[^higgs-v3-card]
- Zero-shot voice cloning posts `input` plus `references: [{audio_path, text}]` with `temperature 0.8`, `top_k 50`, `max_new_tokens 1024`; supplying the reference transcript materially improves cloning fidelity (**Reported**).[^higgs-v3-card]
- Streaming sets `"stream": true` for Server-Sent Events carrying base64 WAV chunks as the vocoder emits them (sub-second time-to-first-audio); each event carries `audio.data`, and the terminal event has `finish_reason: "stop"` plus usage metadata (**Reported**).[^higgs-v3-card]
- Throughput on Seed-TTS EN (full set, N=1088 per run; server `max_running_requests=16`, bf16, CUDA Graph on; 1x H100; mean of 3 runs per row; reproducible via the linked `benchmark_tts_seedtts.py`, not present in `raw/`): (**Reported**).[^higgs-v3-card]

| Concurrency | Throughput (req/s) | Mean latency | RTF (per-req) | audio_s/s |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1.62 | 617 ms | 0.147 | 6.89 |
| 2 | 2.70 | 742 ms | 0.180 | 11.37 |
| 4 | 5.45 | 733 ms | 0.177 | 22.84 |
| 8 | 8.91 | 898 ms | 0.217 | 37.38 |
| 16 | 14.74 | 1079 ms | 0.262 | 61.84 |

- Throughput columns mean: Concurrency is max in-flight client requests; Throughput is completed requests over wall-clock; Mean latency is send-to-full-response per request; RTF <1 is faster than real time; audio_s/s is audio seconds per wall-clock second (**Reported**).[^higgs-v3-card]
- [vLLM-Omni](vllm-omni.md) alternative exposes the same OpenAI-compatible `/v1/audio/speech` API with zero-shot cloning (`vllm-omni serve bosonai/higgs-tts-3-4b --host 0.0.0.0 --port 8095 --trust-remote-code --omni`); zero-ops alternative is the Boson AI API (**Reported**).[^higgs-v3-card]

## License and responsible use

- Weights are under the Boson Higgs TTS 3 Research and Non-Commercial License; prohibited uses include non-consensual voice cloning, impersonation, fraud, election deception, biometric surveillance, and any unlawful use (**Reported**).[^higgs-v3-card]
- Creator Use Grant lets digital creators make and monetize podcasts, videos, audiobooks, and social posts for free with one requirement: credit Boson AI's Higgs Audio in the audio (e.g. "This audio was created with Boson AI's Higgs Audio.") or prominently in the accompanying text (post body, video description, or show notes — not buried in credits); suggested string is "This audio was created with Boson AI's Higgs Audio — https://www.boson.ai/higgs-audio" (**Reported**).[^higgs-v3-card]
- The grant covers creating content, not hosting the model behind an API/service, redistributing, reselling, fine-tuning for resale, or embedding in a product or application — those need a commercial license; AI-generated audio must be disclosed where required (**Reported**).[^higgs-v3-card]

## Relationships

- Included by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as an expressive candidate with a commercial-license gate. Vietnamese under-5 tier is vendor-reported rather than a matched MOS result; H100617ms is full-response latency, not TTFA, and cannot rank first-audio speed against VieNeu/Fish (**Synthesis**).[^higgs-v3-card]
- STT sibling in the same upstream family: [Higgs Audio v3 STT](higgs-audio-v3-stt.md) covers the 2.68B Whisper-Large-v3-encoder plus Qwen3-1.7B-decoder transcription checkpoint with thinking mode and repetition-loop post-processing, while this concept covers the 4B TTS weights; no shared checkpoint is asserted (**Synthesis**).[^higgs-v3-card]
- Packaged for edge/server runtimes: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) already catalogs a `Higgs-Audio-v3-TTS-4B-GGUF` (`higgs_audio_tts`, BF16 + Q8) entry under the same Boson research/non-commercial license, while this concept covers the upstream `bosonai/higgs-tts-3-4b` weights, card, benchmarks, and serving paths; prefer the GGUF entry for audio.cpp deployment questions (**Synthesis**).[^higgs-v3-card]
- Compact multilingual cloning contrast: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B DualAR cloning model with 11 recommended languages and Seed-TTS/CV3 tables that use Higgs Audio v2 as a baseline, while this concept covers the 4B model that supersedes that baseline on those suites; no shared codebase is asserted (**Synthesis**).[^higgs-v3-card]
- Massively multilingual design contrast: [OmniVoice](omnivoice.md) covers a 600+-language diffusion-LM cloning/design model at 0.025 RTF that beats Higgs TTS 3 on the Emergent Emotions column, while this concept covers 102 languages with finer inline emotion/prosody/SFX tag control and H100 throughput figures; no shared codebase is asserted (**Synthesis**).[^higgs-v3-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no audio synthesized, and no WER/CER, win-rate, latency, throughput, RTF, streaming, or cloning-fidelity claims reproduced (**Synthesis**).[^higgs-v3-card]
- Architecture image (`assets/model_architecture.png`), `PROMPTING.md`, `LICENSE`, the Boson blog post, Higgs TTS cookbook, sglang-omni and vLLM-Omni repositories and recipes, the Seed-TTS benchmark script, the Boson AI API docs, and the Hugging Face checkpoint were linked but not fetched and were not present in `raw/`; checkpoint, tokenizer, and reference-audio contents were not inspected (**Synthesis**).[^higgs-v3-card]
- All architecture, language-tier, control-token effect, accuracy, win-rate, memory, compatibility, and usage claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^higgs-v3-card]

[^higgs-v3-card]: [Higgs TTS 3 model card](../raw/higgs-audio-v3-tts-4b.md) — locators: frontmatter (`license`, `language`, `library_name`, `pipeline_tag`, `tags`); header (Boson blog badge, voice-chat intro, 100+ languages / cloning / inline-control paragraph); license `TIP` callouts (research/non-commercial terms, Creator Use Grant); architecture figure plus Component Spec table (backbone 36L/hidden-2560/GQA-32-8, fused embedding/head, 8192 ctx, 8x1026 codebooks delay pattern, 24 kHz, 25 fps); `Supported Languages` tiers (85 under-5 list, 17 5-to-10 list); `Control Tokens` section (syntax note, `PROMPTING.md` pointer, 21-emotion / 3-style / 9-sfx / 10-prosody tables with effects and onomatopoeia); `Evaluation Benchmarks` section (multilingual voice-clone 4x11 table incl. Higgs-Multilingual; emergent win-rate 6x7 table plus same-reference/verbatim-text method note); `Usage` section (SGLang install/serve fences, cloning `references` fence with transcript note, SSE streaming fence, inline-token placement rules, throughput 5-row H100 table with metric definitions and benchmark-script link; vLLM-Omni serve fence and recipe link; Boson AI API link); `Citation` bibtex (2026); `Creator Use` section (covered works, attribution rule, suggested credit, commercial-license carve-outs); `License` section (LICENSE pointer, contact@boson.ai).
