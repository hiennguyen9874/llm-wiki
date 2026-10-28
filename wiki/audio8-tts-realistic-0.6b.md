---
type: Concept
title: Audio8 TTS Realistic 0.6B
description: Multilingual 0.6B DualAR text-to-speech model with 23 supported languages, zero-shot voice cloning, a 44.1 kHz codec, and reported non-streaming SGLang Omni validation.
tags: [tts, multilingual, voice-cloning]
status: stable
created: 2026-10-28
generated: { by: llm-wiki-agent/1, at: 2026-10-28T03:16:03Z }
stale_after: 2027-10-28
sources:
  - id: audio8-realistic-card
    resource: ../raw/Edge0-Audio8-TTS-Realistic-0.6b.md
    kind: documentation
    title: Audio8 TTS Realistic 0.6B model card
---

Audio8 TTS Realistic 0.6B is a multilingual text-to-speech checkpoint derived from Preview 0.6B, with reference-free synthesis or zero-shot cloning and 23 supported languages including Vietnamese. Its card reports improved realism, but the printed error and speaker-similarity metrics do not measure perceived realism directly (**Reported**).[^audio8-realistic-card]

## Architecture and coverage

- The `Edge0/Audio8-TTS-Realistic-0.6b` main DualAR model has 601,159,424 parameters excluding its separately bundled codec. The slow autoregressive transformer predicts a semantic token per audio frame; the fast transformer predicts 10 codec codebooks conditioned on the slow hidden state and preceding codebooks. Slow/fast depths are 24/4 layers, both width 896 with 14 attention heads and 2 KV heads. Each codebook has 4,096 entries; the 44.1 kHz codec uses 2,048 samples per frame (~21.5 frames/s); the packed text/audio context is 2,048 positions (**Reported**).[^audio8-realistic-card]
- The card lists Preview's 11 languages—Cantonese, Chinese, Dutch, English, French, German, Italian, Japanese, Korean, Polish and Spanish—and 12 additions: Arabic, Finnish, Hindi, Indonesian, Malay, Norwegian, Portuguese, Russian, Swedish, Thai, Turkish and Vietnamese. Quality is not uniform; evaluation coverage is not the same as supported-language coverage (**Reported**).[^audio8-realistic-card]
- The card declares Apache-2.0 for code and weights; actual license and NOTICE texts were not inspected (**Reported**).[^audio8-realistic-card]

## Inference and serving

Python 3.10+ and CUDA are recommended; dependencies include PyTorch and torchaudio >=2.5, Transformers >=4.57 and <5, soundfile >=0.12, and safetensors >=0.4. The example loads `AutoProcessor` and `AutoModel` with `trust_remote_code=True`, uses BF16 on CUDA or FP32 on CPU, generates codes and calls `decode_audio` before saving at the codec sample rate. Cloning requires clean reference audio and an exact transcript; omit both reference fields for reference-free generation. The remote code is not included in this capture and must be reviewed before execution (**Reported**).[^audio8-realistic-card]

The SGLang Omni plugin uses paged attention and dynamic batching, slow AR serving with a fixed fast-AR KV cache, and an OpenAI-compatible `/v1/audio/speech` endpoint. Its `audio8_tts_0_6b.yaml` configuration targets this checkpoint. The card reports H20 BF16 tests with and without reference audio through the **non-streaming** API, with Torch compilation and CUDA graphs disabled; it explicitly does not benchmark throughput or streaming. It provides no first-audio latency, VRAM or CPU performance figure, so realtime or edge suitability remains unestablished (**Reported**).[^audio8-realistic-card]

## Evaluation

Reported macro averages, not independently reproduced; lower error is better and higher speaker similarity (SIM, 0–1) is better. Releases were evaluated separately. Seed-TTS combines English WER and Chinese CER; CV3 and MiniMax use the per-language WER/CER choices of their suites (**Reported**).[^audio8-realistic-card]

| Benchmark | Coverage | Preview error % | Realistic error % | Preview SIM | Realistic SIM |
| --- | --- | ---: | ---: | ---: | ---: |
| Seed-TTS | English and Chinese, excluding hard Chinese | 1.23 | 1.25 | 0.682 | 0.704 |
| CV3 | 8 shared languages | 4.80 | 4.56 | — | 0.663 |
| CV3 | 9 core languages including Russian | — | 4.86 | — | 0.661 |
| MiniMax | 24 evaluated languages | — | 5.89 | — | 0.754 |

The CV3 regular-language rows have 500 items each; Vietnamese WER is 28.111% and Thai WER 48.574%. MiniMax uses 100 items per language: Vietnamese CER is 7.966% and Cantonese CER 31.349%. Different datasets and metrics prevent direct comparison of those numbers. Four MiniMax languages are evaluated outside the supported list. Cross-project comparisons in the card use different pipelines and normalization and are not matched rankings; parameter-count conventions also differ (**Reported**).[^audio8-realistic-card]

Seed-TTS detail shows English WER 1.464% versus Preview 1.506%, Chinese CER 1.029% versus 0.950%, and hard-Chinese CER 12.797% versus 11.510%. Thus the claimed realism improvement does not imply uniform error-rate improvement (**Synthesis**).[^audio8-realistic-card]

## Limitations and relationships

Noisy references or transcript mismatch can hurt stability and similarity; reference audio, transcript and target text share the finite context budget. Pronunciation errors, omissions, repetitions and early stopping can occur. The card recommends listening to outputs, obtaining consent to clone, and appropriate synthetic-audio disclosure (**Reported**).[^audio8-realistic-card]

- Builds on [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md); the Realistic card reports the same inference interface and expanded language coverage, not retirement of Preview (**Reported**).[^audio8-realistic-card]
- Uses the DualAR architecture inspired by [Fish Audio S2 Pro](fish-audio-s2-pro.md); this is an architectural inspiration, not evidence that the checkpoints are interchangeable (**Reported/Synthesis**).[^audio8-realistic-card]

## Coverage and limits

The single local model-card capture was inspected statically. No revision, publication date or capture date is stated. The model checkpoint, tokenizer, codec, custom code, SGLang plugin and configuration, linked repository and deployment guide, demos, paper, benchmark sources and datasets, `LICENSE` and `NOTICE` were not inspected; the local hero and badge images are decorative and were not inspected. No download, code execution, synthesis, listening, or benchmark reproduction was performed. All performance and license claims are source-reported, not independently verified. The example's remote code is executable and presents a supply-chain risk (**Synthesis**).[^audio8-realistic-card]

[^audio8-realistic-card]: [Audio8 TTS Realistic 0.6B model card](../raw/Edge0-Audio8-TTS-Realistic-0.6b.md) — frontmatter and introduction; “Supported Languages”; “Model Details”; “Installation”; “Usage”; “High-throughput serving: SGLang Omni”; “Evaluation”, including benchmark summary, Seed-TTS detail and multilingual detail; “Limitations and Responsible Use”; “License and Acknowledgements”.
