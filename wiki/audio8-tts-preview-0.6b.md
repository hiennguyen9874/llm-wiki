---
type: Concept
title: Audio8 TTS Preview 0.6B
description: 0.6B-parameter multilingual zero-shot voice-cloning TTS model with DualAR architecture, 44.1 kHz neural codec, 11 recommended languages, best-in-comparison English WER on Seed-TTS, and ONNX INT4 CPU plus SGLang Omni serving options.
tags: [ml, tts, multilingual, voice-cloning]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
sources:
  - id: audio8-tts-preview-card
    resource: ../raw/Audio8-TTS-Preview-0.6b.md
    kind: documentation
    title: Audio8 TTS Preview 0.6B model card
---

Audio8 TTS Preview 0.6B is a compact 0.6B-parameter multilingual text-to-speech model with zero-shot voice cloning, using a DualAR architecture (slow semantic AR plus fast codec-codebook AR) with a bundled 44.1 kHz neural audio codec, 11 recommended languages, Seed-TTS best-in-comparison English WER of 1.506 with competitive Chinese CER, plus ONNX INT4 CPU and SGLang Omni GPU serving paths, released as a Preview checkpoint with limited multilingual and dialect coverage (**Reported**).[^audio8-tts-preview-card]

## Model identity and architecture

- Title is `Audio8 TTS Preview 0.6B`; model ID is `Audio8/Audio8-TTS-Preview-0.6b`; upstream repository is `https://github.com/Audio8-AI/Audio8_TTS`; live demo is `https://audio8-ai.github.io/Audio8_TTS/`; frontmatter declares `license: apache-2.0`, `library_name: transformers`, `pipeline_tag: text-to-speech`, languages `yue, zh, nl, en, fr, de, it, ja, ko, pl, es`, and tags including `audio`, `text-to-speech`, `tts`, `voice-cloning`, `zero-shot`, and `multilingual` (**Reported**).[^audio8-tts-preview-card]
- Architecture is DualAR inspired by Fish Audio S2 Pro: the slow AR transformer predicts one semantic token per audio frame, and the fast AR transformer predicts the frame's codec codebooks conditioned on the slow hidden state and preceding codebooks (**Reported**).[^audio8-tts-preview-card]
- Main model is 601,159,424 parameters excluding the codec; Slow AR is 24 layers, width 896, 14 attention heads, 2 KV heads; Fast AR is 4 layers, width 896, 14 attention heads, 2 KV heads; acoustic tokens use 10 codebooks with 4,096 entries per codebook; codec runs at 44.1 kHz with 2,048 samples per model frame (~21.5 frames/s); context holds up to 2,048 packed text/audio positions (**Reported**).[^audio8-tts-preview-card]
- The bundled codec handles both reference-audio encoding and waveform decoding, so no additional codec checkpoint is required (**Reported**).[^audio8-tts-preview-card]

## Supported languages

Cantonese, Chinese, Dutch, English, French, German, Italian, Japanese, Korean, Polish, and Spanish — 11 recommended languages; broader multilingual coverage and Chinese dialect support are planned for future releases, and the release is explicitly a Preview with intentionally limited language coverage (**Reported**).[^audio8-tts-preview-card]

## Inference usage

- Requires Python 3.10 or newer with a CUDA-capable GPU recommended, plus `torch>=2.5.0`, `torchaudio>=2.5.0`, `transformers>=4.57.0,<5`, `soundfile>=0.12`, and `safetensors>=0.4`; the model uses custom Transformers code and must be loaded with `trust_remote_code=True` (**Reported**).[^audio8-tts-preview-card]
- Zero-shot voice cloning passes `text`, `reference_audio`, and `reference_text` through `AutoProcessor`, moves inputs to device (`bfloat16` on CUDA, `float32` otherwise), calls `model.generate` with `max_new_tokens=1024`, `temperature=0.8`, `top_p=0.95`, `top_k=50`, `do_sample=True`, `return_dict_in_generate=True`, then decodes with `model.decode_audio(output.codes)` and writes the waveform at `model.config.codec_sample_rate` (**Reported**).[^audio8-tts-preview-card]
- The reference transcript must match the spoken content in the reference audio (**Reported**).[^audio8-tts-preview-card]
- Generation without a cloned voice omits `reference_audio` and `reference_text`; command-line inference, batching, and supervised fine-tuning are documented in the upstream Audio8 TTS repository rather than the card (**Reported**).[^audio8-tts-preview-card]

## Deployment options

- ONNX INT4 release (`Audio8/Audio8-TTS-Preview-0.6B-ONNX-INT4`) targets low-resource CPU inference with ONNX Runtime: Slow and Fast AR weights use weight-only INT4 while activations, KV caches, and the neural codec use FP16; it runs on `CPUExecutionProvider` with no CUDA required, loads at about 1 GiB in the tested Apple M2 configuration, needs no PyTorch or Transformers dependency after model download, and ships a CLI, web and HTTP service, streaming PCM, and voice registration; normal synthesis loads only Slow AR, Fast AR, and codec decoder sessions, and voice registration releases those sessions before loading the optional codec encoder to control peak memory (**Reported**).[^audio8-tts-preview-card]
- SGLang Omni adapter (`sglang_omni` in the upstream repository) targets high-throughput production GPU serving: installed as an independent model plugin without overwriting SGLang Omni core files, supporting SGLang paged attention and dynamic batching, DualAR execution with Slow AR serving plus a fixed KV cache for the Fast AR codebook decoder, reference-audio encoding and waveform decoding for voice cloning, and an OpenAI-compatible `/v1/audio/speech` service; the released adapter is validated against a pinned SGLang Omni revision and supports both reference-free generation and zero-shot voice cloning (**Reported**).[^audio8-tts-preview-card]

## Evaluation

Seed-TTS results; lower WER/CER is better, higher SIM is better, SIM shown as percentages; Audio8 is the smallest model in the comparison at 0.6B (**Reported**):[^audio8-tts-preview-card]

| Model | Parameters | EN WER / SIM | ZH CER / SIM | Hard ZH CER / SIM |
| --- | ---: | ---: | ---: | ---: |
| Audio8 TTS Preview | 0.6B | 1.506 / 63.2 | 0.950 / 73.1 | 11.510 / 68.7 |
| Fish S2 Pro | 4.6B | 1.607 / 64.6 | 1.038 / 73.8 | 10.149 / 70.1 |
| Higgs Audio v2 | 4.7B | 1.524 / 66.4 | 0.806 / 72.1 | 10.622 / 69.3 |
| CosyVoice3-1.5B | 1.5B | 2.22 / 72.0 | 1.12 / 78.1 | 5.83 / 75.8 |
| MOSS-TTS | 8.5B | 1.85 / 73.4 | 1.20 / 78.8 | - |
| VoxCPM2 | 2.3B | 1.84 / 75.3 | 0.97 / 79.5 | 8.13 / 75.3 |

CV3 multilingual error rates; lower is better (**Reported**):[^audio8-tts-preview-card]

| Model | Parameters | zh | en | hard-zh | hard-en | ja | ko | de | es | fr | it | ru |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Audio8 TTS Preview | 0.6B | 3.205 | 3.128 | 10.535 | 5.997 | 7.205 | 4.223 | 3.447 | 3.641 | 8.790 | 4.790 | - |
| Fish S2 Pro | 4.6B | 3.600 | 3.493 | 10.588 | 7.349 | 5.139 | 4.111 | 3.605 | 2.972 | 8.600 | 4.229 | 4.702 |
| Higgs Audio v2 | 4.7B | 3.378 | 3.404 | 10.424 | 5.754 | 4.742 | 4.260 | 3.300 | 2.929 | 9.425 | 3.555 | 5.423 |
| CosyVoice3-1.5B | 1.5B | 3.91 | 4.99 | 9.77 | 10.55 | 7.57 | 5.69 | 6.43 | 4.47 | 11.8 | 10.5 | 6.64 |
| VoxCPM2 | 2.3B | 3.65 | 5.00 | 8.55 | 8.48 | 5.96 | 5.69 | 4.77 | 3.80 | 9.85 | 4.25 | 5.21 |

- Card's headline reading: best English WER with competitive Chinese CER on Seed-TTS, and competitive results across the CV3 multilingual evaluation (**Reported**).[^audio8-tts-preview-card]
- Methodology notes: parameter counts are computed directly from released weight tensors (MOSS-TTS 8,489,841,664; VoxCPM2 main model 2,290,004,544 excluding the separate AudioVAE); Fish S2 Pro was reevaluated because its official evaluation uses its own normalizer; Higgs Audio v2 was evaluated locally because concrete values were unavailable; all other baseline values were collected from official reports via the VoxCPM repository; different normalizers and evaluators make cross-project values reference comparisons rather than strictly matched rankings; evaluation coverage does not expand the Preview checkpoint's supported-language claim beyond the 11 listed languages (**Reported**).[^audio8-tts-preview-card]

## Limitations and responsible use

- Preview checkpoint with limited multilingual and dialect coverage; very long, noisy, or incorrectly transcribed reference clips can reduce stability and speaker similarity (**Reported**).[^audio8-tts-preview-card]
- Generated speech can be misused for impersonation or misinformation; obtain consent before cloning a voice and clearly disclose synthetic audio where appropriate; evaluate accuracy, safety, and legal compliance before deployment (**Reported**).[^audio8-tts-preview-card]

## License and acknowledgements

- Code and model weights are released under Apache License 2.0 with attribution details in the upstream `NOTICE`; thanks go to the Fish Audio team for publishing the DualAR architecture used in Fish Audio S2 Pro (**Reported**).[^audio8-tts-preview-card]

## Relationships

- Audio8 ASR family: [Audio8-ASR-0.1B](audio8-asr-0.1b.md) and [Audio8 ASR Infinite](audio8-asr-infinite.md) cover Audio8-named speech-recognition models (multilingual short-form transcription and streaming bilingual ASR respectively), while this concept covers the Audio8-named speech-synthesis Preview model; no shared codebase or vendor claim is asserted beyond the naming and audio-model overlap (**Synthesis**).[^audio8-tts-preview-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio synthesized, and no WER/CER, SIM, memory-footprint, or serving-throughput figures reproduced (**Synthesis**).[^audio8-tts-preview-card]
- Header image (`20260729-124515.jpeg`), upstream GitHub repository, live demo, ONNX INT4 release, CPU ONNX Runtime guide, SGLang Omni adapter and deployment guide, VoxCPM baseline collection, Fish S2 Pro source, and upstream `LICENSE`/`NOTICE` were linked but not fetched and were not present in `raw/`; checkpoint, codec, tokenizer, processor, and remote-code files were listed but not present in `raw/` and were not inspected (**Synthesis**).[^audio8-tts-preview-card]
- All architecture, language-coverage, accuracy, similarity, memory, compatibility, and usage claims are source assertions without independent verification in this wiki (**Synthesis**).[^audio8-tts-preview-card]

[^audio8-tts-preview-card]: [Audio8 TTS Preview 0.6B model card](../raw/Audio8-TTS-Preview-0.6b.md) — locators: frontmatter (`license`, `language`, `library_name`, `pipeline_tag`, `tags`); header badges (GitHub `Audio8-AI/Audio8_TTS`, demo, ONNX INT4, Apache 2.0); intro paragraph (0.6B, multilingual, zero-shot cloning, checkpoint/codec/tokenizer/processor/remote code); `Preview status` callout (11 recommended languages, planned broader/dialect coverage); `Supported Languages` section (11-language list); `Model Details` section (DualAR slow/fast description, 7-row configuration table, bundled-codec paragraph); `Installation` section (`torch`, `torchaudio`, `transformers`, `soundfile`, `safetensors` requirements, Python 3.10+/CUDA); `Usage` section (`trust_remote_code=True` paragraph, zero-shot Python fence with `max_new_tokens`/`temperature`/`top_p`/`top_k`/`do_sample` plus transcript-match note, reference-free paragraph, CLI/batch/SFT pointer); `Deployment Options` section (ONNX INT4 advantage table, ~1 GiB M2/session-management paragraph, CPU guide link; SGLang Omni capability table, plugin/pinned-revision paragraph, deployment-guide link); `Evaluation` section (intro 0.6B/first-tier paragraph, Seed-TTS 6-row table, CV3 5-row table, parameter-count paragraph, reevaluation/normalizer paragraph, language-claim scoping sentence); `Limitations and Responsible Use` section (4 bullets); `License and Acknowledgements` section (Apache 2.0, NOTICE, Fish Audio thanks).
