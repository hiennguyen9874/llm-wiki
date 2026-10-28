---
type: Concept
title: Audio8 TTS Preview 0.1B
description: Compact zero-shot voice-cloning TTS with a 170M generative model, separate 120M codec decoder, experimental multilingual coverage, ONNX INT8 CPU deployment, and a revenue-capped community license.
tags: [tts, multilingual, voice-cloning, edge]
status: stable
created: 2026-10-28
generated: { by: llm-wiki-agent/1, at: 2026-10-28T03:14:12Z }
stale_after: 2027-10-28
sources:
  - id: audio8-01-card
    resource: ../raw/Edge0-Audio8-TTS-Preview-0.1b.md
    kind: documentation
    title: Audio8 TTS Preview 0.1B model card
---

Audio8 TTS Preview 0.1B is a compact zero-shot voice-cloning and speech-generation checkpoint with an approximately 170M-parameter generative model and a separate approximately 120M-parameter codec decoder. Chinese and English are primary targets; six other languages are experimental. A separate ONNX INT8 CPU package and a revenue-capped custom license distinguish deployment and commercial-use decisions (**Reported**).[^audio8-01-card]

## Architecture and languages

The Audio8 Falcon H1 model has slow and fast autoregressive branches: the slow branch predicts semantic tokens and the fast branch predicts codec codebooks conditioned on the slow hidden state. Slow AR has 24 layers and fast AR four; both use width 512, eight attention heads and two KV heads. There are ten codebooks of 4,096 entries, 44.1 kHz audio with 2,048 samples per frame (about 21.5 frames/s), and up to 2,048 packed text/audio positions. The codec decoder is bundled as `codec.pth` (**Reported**).[^audio8-01-card]

Chinese and English are primary; German, Spanish, French, Italian, Japanese and Korean are experimental/multilingual evaluation languages, not equally supported production targets. Longer, noisy or incorrectly transcribed references can reduce stability and similarity (**Reported**).[^audio8-01-card]

## Inference and deployment

- The Transformers example recommends Python 3.11+ and CUDA, with PyTorch and torchaudio 2.5+, Transformers 4.57 to below 5, soundfile and safetensors. It loads `Audio8/Audio8-TTS-Preview-0.1b` with `trust_remote_code=True`; that runs custom code, which should be reviewed before use. CUDA uses bfloat16 in the example, CPU float32 (**Reported**; security implication **Synthesis**).[^audio8-01-card]
- For cloning, supply text, reference audio and its matching transcript to the processor, generate codes, decode audio and write at the configured codec sample rate. The example uses 512 maximum new tokens, temperature 0.7, top-p 0.9, top-k 50 and sampling. Omit both reference inputs for reference-free synthesis (**Reported**).[^audio8-01-card]
- The separate ONNX Runtime package uses per-token INT8 Slow/Fast AR graphs and an FP16 codec; it reports approximately 0.4 GiB loaded on tested Linux x86_64, with CPUExecutionProvider, no CUDA, PyTorch or Transformers runtime dependency after download, CLI, web/HTTP service, streaming PCM and voice registration. Normal synthesis loads the two AR sessions and decoder; registration releases them before loading an optional encoder (**Reported**). This memory number is configuration-specific and is not a latency or peak-memory measurement (**Synthesis**).[^audio8-01-card]

## Evaluation

The card reports Seed-TTS English WER 1.662 and similarity 56.7%, and Chinese CER 1.13 and similarity 68.2%. Its 0.6B comparison is 1.506 / 63.2% and 0.950 / 73.1%, respectively. CV3 error rates for the 0.1B are zh 3.619, en 3.307, ja 12.322, ko 7.653, de 5.292, es 8.548, fr 12.349 and it 14.480; lower WER/CER and higher similarity are better (**Reported**).[^audio8-01-card]

These comparisons mix reported and local evaluations and differing normalizers/evaluators; they are not a matched ranking. The CV3 comparison follows the 0.6B card rather than a strictly matched re-evaluation, and approximate model parameter counts exclude some separate components. The card does not specify a complete reproducible evaluation protocol (**Reported/Synthesis**).[^audio8-01-card]

## License and responsible use

The card describes Audio8 Community License v1.0: non-commercial use is free; commercial use is free for entities with annual revenue including affiliates below US$2 million, and at or above that threshold requires a separate written commercial license. The authoritative English license text was not inspected, so these are card-reported terms, not a complete license interpretation. Obtain consent before cloning and disclose synthetic audio as appropriate (**Reported**).[^audio8-01-card]

## Relationships

- Related model: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) is the larger Preview checkpoint; its page reports different language, license and CPU quantization details, so those should not be transferred to 0.1B (**Synthesis**).[^audio8-01-card]
- Catalogued in [TTS Model Survey](tts-model-survey.md), with the separate decoder and license noted.

## Coverage and limits

The local model-card capture was read in full and inspected statically. The relative header image is absent and decorative; linked teaser, demos, GitHub repository, ONNX package and guide, license, baseline sources, checkpoint, codec, tokenizer, processor and remote code were not inspected. No immutable revision, publication date or capture date is stated. No code, download, synthesis, listening, benchmark or license verification was performed. The card gives no TTFA, RTF, peak memory, training data or Vietnamese support; streaming PCM in the ONNX package alone does not establish a realtime latency target (**Observed/Synthesis**).[^audio8-01-card]

[^audio8-01-card]: [Audio8 TTS Preview 0.1B model card](../raw/Edge0-Audio8-TTS-Preview-0.1b.md), frontmatter; introduction; “Compact Scale”; “Supported Languages”; “Model Details”; “Deployment Options”; “Installation”; “Usage”; “Evaluation” (CV3 and Seed-TTS tables and comparison qualifications); “Limitations and Responsible Use”; “License”.
