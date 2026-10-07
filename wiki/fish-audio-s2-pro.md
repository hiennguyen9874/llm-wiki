---
type: Concept
title: Fish Audio S2 Pro
description: Dual-autoregressive multilingual TTS model with free-form inline prosody and emotion control across 80+ languages and ~100 ms time-to-first-audio streaming on H200.
tags: [tts, multilingual, expressive, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:10:00Z }
stale_after: 2027-10-06
sources:
  - id: fish-s2pro-card
    resource: ../raw/s2-pro.md
    kind: documentation
    title: Fish Audio S2 Pro model card
---

Fish Audio S2 Pro is a leading multilingual text-to-speech model combining reinforcement-learning alignment with a Dual-Autoregressive transformer (4B slow AR plus 400M fast AR) over a 10-codebook RVQ codec, trained on 10M+ hours across 80+ languages, offering free-form `[tag]` inline control of prosody and emotion plus an SGLang-based streaming engine that reports 0.195 RTF and ~100 ms time-to-first-audio on a single H200, under a research/non-commercial license (**Reported**).[^fish-s2pro-card]

## Model identity and release

- Title is `Fish Audio S2 Pro`; frontmatter declares `pipeline_tag: text-to-speech`, tags `text-to-speech`, `instruction-following`, `multilingual`, an 80+-entry language list, license `other` named `fish-audio-research-license`, and `inference: false` (**Reported**).[^fish-s2pro-card]
- Release scope per the intro is model weights, fine-tuning code, and an SGLang-based streaming inference engine; upstream pointers are the technical report (`huggingface.co/papers/2603.08823`), GitHub (`fishaudio/fish-speech`), Playground (`fish.audio`), and blog/tech-report page (`fish.audio/blog/fish-audio-open-sources-s2/`) (**Reported**).[^fish-s2pro-card]
- Header image alt text advertises fine-grained control, multi-speaker multi-turn generation, low-latency streaming, and long-context inference; the image file itself (`overview.png`) was not present in `raw/` and was inspected only via its alt text (**Synthesis**).[^fish-s2pro-card]
- Technical-report citation is Liao et al., `Fish Audio S2 Technical Report`, 2026, `arXiv:2603.08823 [cs.SD]`, with the card's BibTeX as the canonical reference (**Reported**).[^fish-s2pro-card]

## Architecture

- Backbone is a decoder-only transformer with an RVQ-based audio codec (10 codebooks, ~21 Hz frame rate) in a Dual-Autoregressive (Dual-AR) layout: Slow AR (4B parameters) runs along the time axis and predicts the primary semantic codebook, while Fast AR (400M parameters) generates the remaining 9 residual codebooks at each step for fine acoustic detail (**Reported**).[^fish-s2pro-card]
- Training combines 10M+ hours of audio across 80+ languages with reinforcement-learning alignment; the asymmetric Slow/Fast sizing is stated to keep inference efficient while preserving fidelity (**Reported**).[^fish-s2pro-card]
- The card states the Dual-AR structure is isomorphic to standard autoregressive LLMs and therefore inherits LLM-native SGLang serving optimizations: continuous batching, paged KV cache, CUDA graph replay, and RadixAttention-based prefix caching (**Reported**).[^fish-s2pro-card]

## Fine-grained inline control

- Control embeds natural-language instructions directly in the text with `[tag]` syntax at the word level; unlike fixed tag sets, S2 Pro accepts free-form descriptions such as `[whisper in small voice]`, `[professional broadcast tone]`, or `[pitch up]` for open-ended expression control (**Reported**).[^fish-s2pro-card]
- Card states 15,000+ unique tags are supported; commonly listed tags are `[pause]` `[emphasis]` `[laughing]` `[inhale]` `[chuckle]` `[tsk]` `[singing]` `[excited]` `[laughing tone]` `[interrupting]` `[chuckling]` `[excited tone]` `[volume up]` `[echo]` `[angry]` `[low volume]` `[sigh]` `[low voice]` `[whisper]` `[screaming]` `[shouting]` `[loud]` `[surprised]` `[short pause]` `[exhale]` `[delight]` `[panting]` `[audience laughter]` `[with strong accent]` `[volume down]` `[clearing throat]` `[sad]` `[moaning]` `[shocked]` (**Reported**).[^fish-s2pro-card]

## Supported languages

- 80+ languages total. Tier 1 is Japanese (ja), English (en), Chinese (zh); Tier 2 is Korean (ko), Spanish (es), Portuguese (pt), Arabic (ar), Russian (ru), French (fr), German (de) (**Reported**).[^fish-s2pro-card]
- Remaining supported codes are listed as sv, it, tr, no, nl, cy, eu, ca, da, gl, ta, hu, fi, pl, et, hi, la, ur, th, vi, jw, bn, yo, xsl, cs, sw, nn, he, ms, uk, id, kk, bg, lv, my, tl, sk, ne, fa, af, el, bo, hr, ro, sn, mi, yi, am, be, km, is, az, sd, br, sq, ps, mn, ht, ml, sr, sa, te, ka, bs, pa, lt, kn, si, hy, mr, as, gu, fo, "and more" — so the tail is open-ended rather than exhaustive (**Reported**).[^fish-s2pro-card]

## Production streaming performance

- All figures are for a single NVIDIA H200 GPU: Real-Time Factor (RTF) 0.195, time-to-first-audio ~100 ms, and throughput of 3,000+ acoustic tokens/s while holding RTF below 0.5 (**Reported**).[^fish-s2pro-card]
- No measurement protocol, batch size, text length, voice, language, precision, or variance is stated alongside these figures, so they are not directly comparable to per-request latency/RTF tables measured under different harnesses (**Synthesis**).[^fish-s2pro-card]

## License and access

- Weights are under the Fish Audio Research License (`LICENSE.md` in the source repository): research and non-commercial use free of charge; commercial use requires a separate license via `business@fish.audio` (**Reported**).[^fish-s2pro-card]
- Model-page gating states agreement not to generate content violating DMCA or local laws, with required fields for Country, specific date, and a non-commercial-use-only checkbox (**Reported**).[^fish-s2pro-card]

## Relationships

- Included by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as an expressive streaming candidate with a commercial-license gate. `vi` is in Other languages, not Tier 1/2; H200~100ms TTFA is not matched Vietnamese quality/latency evidence against consumer-GPU alternatives (**Synthesis**).[^fish-s2pro-card]
- DualAR lineage: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) describes its DualAR design as inspired by Fish Audio S2 Pro (slow AR semantic token per frame, fast AR codec codebooks conditioned on slow hidden state), while this concept covers the upstream S2 Pro architecture, control, language, and streaming claims; no shared checkpoint is asserted (**Synthesis**).[^fish-s2pro-card]
- Independent benchmark baseline: [Higgs TTS 3](higgs-tts-3-4b.md) reports Fish Audio S2 Pro scores as a baseline on multilingual voice-clone WER/CER suites and the Emergent-TTS judge win-rate table, while this concept carries S2 Pro's own card claims; prefer the Higgs page for head-to-head numbers (**Synthesis**).[^fish-s2pro-card]
- Edge/server packaging: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) already catalogs a `Fish-Audio-S2-Pro-GGUF` entry (`fish_audio`, BF16 + Q8, Fish Audio Research License), while this concept covers the upstream weights, card, and serving claims; prefer the GGUF entry for audio.cpp deployment questions (**Synthesis**).[^fish-s2pro-card]

## Coverage and limits

- Source inspected statically only; no weights downloaded, no fine-tuning or inference code executed, and no RTF, latency, throughput, tag-effect, language-quality, or cloning claims reproduced (**Synthesis**).[^fish-s2pro-card]
- Header image (`overview.png`), `LICENSE.md`, the arXiv/Hugging Face technical report, the `fish-speech` GitHub repository, the fish.audio playground, and the blog/tech-report page were linked but not fetched and were not present in `raw/`; checkpoint, tokenizer, codec, and audio contents were not inspected (**Synthesis**).[^fish-s2pro-card]
- All architecture, training-scale, control-effect, language-coverage, performance, and licensing claims are source assertions without independent verification in this wiki; release and performance figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^fish-s2pro-card]

[^fish-s2pro-card]: [Fish Audio S2 Pro model card](../raw/s2-pro.md) — locators: frontmatter (`license`, `license_name`, `pipeline_tag`, `tags`, `language`, `inference`, `extra_gated_prompt`, `extra_gated_fields`); H1 plus intro paragraph (10M+ hours, 80+ languages, RL alignment, Dual-AR, weights/fine-tuning-code/SGLang-engine release); `Architecture` section (decoder-only transformer, 10-codebook RVQ at ~21 Hz, Slow AR 4B semantic codebook, Fast AR 400M 9 residual codebooks, SGLang optimizations incl. continuous batching / paged KV cache / CUDA graph replay / RadixAttention prefix caching); `Fine-Grained Inline Control` section (free-form `[tag]` syntax, word-level examples, 15,000+ tags, common-tag list); `Supported Languages` section (Tier 1, Tier 2, other-codes list); `Production Streaming Performance` section (H200 RTF 0.195, ~100 ms TTFA, 3,000+ tokens/s at RTF < 0.5); `Links` section (GitHub, Playground, blog/tech report); `Technical Report` BibTeX (Liao et al. 2026, arXiv:2603.08823); `License` section (research/non-commercial grant, business@fish.audio); header `<img>` alt text (fine-grained control, multi-speaker multi-turn, low-latency streaming, long-context inference).
