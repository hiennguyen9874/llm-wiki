---
type: Concept
title: Qwen3-TTS-Tokenizer-12Hz
description: Discrete neural speech tokenizer with 12.5 Hz 16-codebook encoding and causal ConvNet decoding for ultra-low-latency streaming TTS.
tags: [tts, tokenizer, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T17:00:00Z }
stale_after: 2027-10-06
sources:
  - id: qwen3-tts-tokenizer-card
    resource: ../raw/Qwen3-TTS-Tokenizer-12Hz.md
    kind: documentation
    title: Qwen3-TTS-Tokenizer-12Hz model card
---

Qwen3-TTS-Tokenizer-12Hz is Qwen's discrete neural speech codec for the Qwen3-TTS series, encoding input speech into discrete codes at 12.5 Hz across 16 codebooks and decoding codes back to waveforms through a lightweight causal ConvNet, claimed to deliver extreme bitrate reduction with ultra-low-latency streaming and immediate first-packet emission (**Reported**).[^qwen3-tts-tokenizer-card]

## Model identity and release

- Model identifier is `Qwen/Qwen3-TTS-Tokenizer-12Hz`, presented as the tokenizer of the Qwen3-TTS series per the Qwen3-TTS Technical Report (**Reported**).[^qwen3-tts-tokenizer-card]
- Linked resources are the Qwen3-TTS Technical Report (`https://huggingface.co/papers/2601.15621`), GitHub repository `QwenLM/Qwen3-TTS`, and the `Qwen/Qwen3-TTS` Hugging Face Space demo (**Reported**).[^qwen3-tts-tokenizer-card]
- Card frontmatter declares `license: apache-2.0`, `pipeline_tag: audio-to-audio`, and tags `audio, tts, speech, codec` (**Observed** by static inspection).[^qwen3-tts-tokenizer-card]
- Series context in this card: Qwen3-TTS covers 10 major languages (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian) plus multiple dialectal voice profiles; the card's `Released Tokenizers` table lists this tokenizer as its single entry, encoding input speech into codes and decoding them back into speech (**Reported**).[^qwen3-tts-tokenizer-card]
- Citation is the Qwen3-TTS Technical Report BibTeX (`arXiv:2601.15621`, year 2026) (**Reported**).[^qwen3-tts-tokenizer-card]

## Design

- Frame rate is 12.5 Hz with a 16-layer multi-codebook design over a lightweight causal ConvNet (**Reported**).[^qwen3-tts-tokenizer-card]
- Speech representation claims efficient acoustic compression with high-dimensional semantic modeling, fully preserving paralinguistic information and acoustic environmental features (**Reported**).[^qwen3-tts-tokenizer-card]
- Streaming claim is immediate first-packet emission from this low-rate discrete representation (**Reported**).[^qwen3-tts-tokenizer-card]
- The 97 ms end-to-end synthesis latency and first-audio-packet-after-a-single-character statements in this card describe the Qwen3-TTS system's Dual-Track hybrid streaming generation architecture, not a tokenizer-only measurement with protocol or hardware in this card (**Synthesis**).[^qwen3-tts-tokenizer-card]

## Encode and decode usage

- Install with `pip install -U qwen-tts` (**Reported**).[^qwen3-tts-tokenizer-card]
- Load with `Qwen3TTSTokenizer.from_pretrained("Qwen/Qwen3-TTS-Tokenizer-12Hz", device_map="cuda:0")` (**Reported**).[^qwen3-tts-tokenizer-card]
- Encode with `tokenizer.encode(...)` accepting an audio URL or local path; the documented example encodes the hosted `tokenizer_demo_1.wav` (**Reported**).[^qwen3-tts-tokenizer-card]
- Decode with `tokenizer.decode(enc)` returning `(wavs, sr)`, saved with `soundfile.write`, e.g. `sf.write("decode_output.wav", wavs[0], sr)` (**Reported**).[^qwen3-tts-tokenizer-card]

## Evaluation pointer

- This card carries no benchmark numbers itself; it defers detailed results on speech-generation consistency, speaker similarity, and tokenizer benchmarks (ASR tasks, PESQ, STOI, UTMOS) to the technical report and GitHub repository (**Reported**).[^qwen3-tts-tokenizer-card]

## Relationships

- Shared tokenizer for [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md): that checkpoint describes itself as built on the 12Hz tokenizer with preset timbres and a 97 ms streaming claim, while this concept covers the underlying 12.5 Hz 16-codebook encode/decode interface (**Synthesis**).[^qwen3-tts-tokenizer-card]
- Shared tokenizer for [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md): that checkpoint adds the five-model family table, instruction control, and tokenizer reconstruction rows, while this concept is the dedicated tokenizer authority (**Synthesis**).[^qwen3-tts-tokenizer-card]

## Coverage and limits

- Source inspected statically only; no `qwen-tts` package installed, no tokenizer weights downloaded, no audio encoded or decoded, and no bitrate, latency, reconstruction-quality, or language-coverage claim reproduced (**Synthesis**).[^qwen3-tts-tokenizer-card]
- Linked but unfetched and absent from `raw/`: Qwen3-TTS GitHub repository, technical-report paper `arXiv:2601.15621`, Hugging Face Space demo, `qwen-tts` PyPI package, the `Qwen/Qwen3-TTS-Tokenizer-12Hz` weights, and the hosted `tokenizer_demo_1.wav` and architecture images (`qwen3_tts_introduction.png`, `overview.png`); image contents were not visually inspected and claims above come from surrounding prose only (**Synthesis**).[^qwen3-tts-tokenizer-card]
- Tokenizer reconstruction figures (PESQ, STOI, UTMOS, SIM) are summarized in the sibling [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) concept from its card's benchmark table, not from this card (**Synthesis**).[^qwen3-tts-tokenizer-card]
- All capability, latency, and usage claims are source assertions without independent verification in this wiki; model-release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^qwen3-tts-tokenizer-card]

[^qwen3-tts-tokenizer-card]: [Qwen3-TTS-Tokenizer-12Hz model card](../raw/Qwen3-TTS-Tokenizer-12Hz.md) — locators: frontmatter (`license`, `pipeline_tag`, `tags`); title plus lead paragraph (12.5 Hz, 16-layer multi-codebook, lightweight causal ConvNet, extreme bitrate reduction, ultra-low-latency streaming, first-packet emission); `Paper`/`GitHub Repository`/`Demo` link lines; `Quickstart/Environment Setup` (`pip install -U qwen-tts` fence); `Tokenizer Encode and Decode` fence (`Qwen3TTSTokenizer.from_pretrained` with `Qwen/Qwen3-TTS-Tokenizer-12Hz` and `device_map`, `tokenizer.encode` with hosted wav URL, `tokenizer.decode`, `sf.write`); `Overview/Introduction` section (10-language list, dialectal profiles, speech-representation bullet with paralinguistic/environmental preservation, Dual-Track streaming bullet with single-character first packet and 97 ms); `Model Architecture` image lines; `Released Tokenizers` single-row table; `Evaluation` section (consistency, speaker similarity, ASR/PESQ/STOI/UTMOS deferral to report and GitHub); `Citation` BibTeX (`arXiv:2601.15621`, 2026).
