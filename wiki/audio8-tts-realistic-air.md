---
type: Concept
title: Audio8 TTS Realistic Air
description: 0.6B DualAR multilingual voice-cloning TTS checkpoint with 23 supported languages, 44.1 kHz codec, reported multilingual evaluation, and SGLang Omni GPU serving without measured streaming latency.
tags: [tts, multilingual, voice-cloning, serving]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:37:12Z }
stale_after: 2027-05-02
sources:
  - id: audio8-realistic-card
    resource: ../raw/Audio8-TTS-Realistic-Air.md
    kind: documentation
    title: Audio8 TTS Realistic Air model card
---

Audio8 TTS Realistic Air is Edge0's 0.6B multilingual text-to-speech checkpoint, built on [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md), with zero-shot voice cloning, reference-free generation and a 44.1 kHz codec. Its card claims improved realism and 23 supported languages, including Vietnamese; perceived realism is not directly measured by its reported intelligibility and speaker-similarity metrics (**Reported**).[^audio8-realistic-card]

## Architecture and language coverage

The DualAR model predicts one semantic token per frame with a 24-layer slow transformer, followed by 10 codec codebooks with a 4-layer fast transformer. Both use width 896, 14 attention heads and 2 KV heads; each codebook has 4,096 entries. The main model has 601,159,424 parameters excluding the bundled codec; 2,048 samples per frame at 44.1 kHz is about 21.5 frames/s, with up to 2,048 packed text/audio positions (**Reported**).[^audio8-realistic-card]

The 11 Preview languages are Cantonese, Chinese, Dutch, English, French, German, Italian, Japanese, Korean, Polish and Spanish; Air adds Arabic, Finnish, Hindi, Indonesian, Malay, Norwegian, Portuguese, Russian, Swedish, Thai, Turkish and Vietnamese. Quality varies by language, and evaluation coverage is not the same as supported languages (**Reported**).[^audio8-realistic-card]

## Inference and serving

- Python 3.10+, CUDA GPU recommended; dependencies include PyTorch and torchaudio ≥2.5, Transformers ≥4.57 and <5, soundfile and safetensors. `AutoProcessor` and `AutoModel` require `trust_remote_code=True`; review the custom code before running. The example supplies target text and, for cloning, clean reference audio and its exact transcript, then calls `generate` and `decode_audio`; omit reference inputs for reference-free generation (**Reported**).[^audio8-realistic-card]
- The independent [SGLang-Omni](sglang-omni.md) model plugin advertises paged attention, dynamic batching and `/v1/audio/speech`, with the `audio8_tts_0_6b.yaml` configuration. The card reports an NVIDIA H20 BF16 test of the **non-streaming** API with and without reference audio, Torch compilation and CUDA graphs disabled; streaming, throughput and first-audio latency were not benchmarked. A separate Transformers smoke test used H20, PyTorch 2.8.0 and Transformers 4.57.3 (**Reported**, not reproduced).[^audio8-realistic-card]
- Reference and target inputs share finite context; noisy audio and mismatched transcripts can harm cloning. Split long passages, listen for mispronunciations, repetition, omissions and early stops, obtain permission for cloning, and disclose synthetic speech as appropriate (**Reported**).[^audio8-realistic-card]

## Evaluation

The card reports unweighted language macro averages: Seed-TTS English WER/Chinese CER 1.25% and SIM 0.704; CV3 nine core languages 4.86% and SIM 0.661; MiniMax 24 languages 5.89% and SIM 0.754. Seed-TTS excludes hard Chinese, CV3 excludes hard subsets and additional languages, and MiniMax includes four evaluated but unsupported languages. Preview and Air were evaluated separately; different normalizers and pipelines make cross-project tables reference comparisons, not matched rankings (**Reported**).[^audio8-realistic-card]

For Vietnamese the card reports CV3 WER 28.111% and SIM 0.6790 over 500 items, versus MiniMax CER 7.966% and SIM 0.7120 over 100 items. These use different sets and metrics and cannot be compared as a direct improvement (**Reported**; comparison caveat is **Synthesis**). Seed-TTS English WER is 1.464% versus Preview 1.506%, while Chinese CER is 1.029% versus 0.950%, and hard Chinese 12.797% versus 11.510%; the separately evaluated figures do not establish a universal improvement (**Reported**).[^audio8-realistic-card]

## Relationships

- Supersedes [Audio8 TTS Realistic 0.6B](audio8-tts-realistic-0.6b.md): the user confirmed the rename on 2026-11-02; its effective date is unknown. The Air card uses the new model ID.[^audio8-realistic-card]

- Builds on [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md), adding languages and claiming greater realism; Preview's ONNX INT4 packaging is not established for this checkpoint (**Reported/Synthesis**).[^audio8-realistic-card]
- Uses an independently installed [SGLang-Omni](sglang-omni.md) adapter for GPU serving (**Reported**).[^audio8-realistic-card]

## Coverage and limits

The single model-card capture was inspected statically; no dated revision, capture date or training details are supplied. The card claims Apache-2.0 for code and weights, but linked `LICENSE` and `NOTICE` are absent locally. The decorative hero and badge assets are excluded; the model weights, codec, tokenizer, processor, remote code, external repository and serving guide, paper, demos, Preview card on the web, benchmark sources and datasets were not inspected. No installation, code execution, inference, listening or benchmark was performed; memory, streaming latency and throughput remain unknown. The release's realism claim is not independently verified (**Synthesis**).[^audio8-realistic-card]

[^audio8-realistic-card]: [Audio8 TTS Realistic Air model card](../raw/Audio8-TTS-Realistic-Air.md), frontmatter and introduction; §§ Highlights, Supported Languages, Model Details, Installation, Usage, High-throughput serving: SGLang Omni, Evaluation (Benchmark summary, Seed-TTS detail, Multilingual detail), Limitations and Responsible Use, License and Acknowledgements.
