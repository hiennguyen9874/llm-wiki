---
type: Concept
title: Audio8 TTS Preview 0.1B
description: Compact zero-shot voice-cloning TTS with a reported 170M-parameter generator, separate 120M codec decoder, Chinese-English focus, ONNX INT8 CPU deployment, and revenue-capped community license.
tags: [tts, voice-cloning, multilingual, edge-deployment]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:37:12Z }
stale_after: 2027-05-02
sources:
  - id: audio8-01b-card
    resource: ../raw/Audio8-TTS-Preview-0.1b.md
    kind: documentation
    title: Audio8 TTS Preview 0.1B model card
  - id: audio8-01b-duplicate
    resource: ../raw/Edge0-Audio8-TTS-Preview-0.1b.md
    kind: documentation
    title: Duplicate Audio8 TTS Preview 0.1B model card capture
---

Audio8 TTS Preview 0.1B is a compact autoregressive TTS checkpoint for speech generation and zero-shot voice cloning, with Chinese and English as primary languages and an ONNX CPU deployment option. Its model card reports approximately 170M generator parameters plus a separate 120M codec decoder; all capabilities and measurements below are **Reported**, not independently verified.[^audio8-01b-card]

## Architecture and languages

The Audio8 Falcon H1 uses a 24-layer slow AR branch to predict semantic tokens and a 4-layer fast AR branch to predict codec codebooks conditioned on the slow hidden state. Both have width 512, 8 attention heads and 2 KV heads. Audio uses 10 codebooks of 4,096 entries, 44.1 kHz sampling and 2,048 samples per frame (approximately 21.5 frames/s); context is up to 2,048 packed text/audio positions. The card says the codec is bundled in `codec.pth` and no extra codec checkpoint is needed.[^audio8-01b-card]

Chinese and English are primary; German, Spanish, French, Italian, Japanese and Korean are experimental multilingual evaluation languages, not equivalent supported-quality claims. Vietnamese is not listed. Long, noisy or inaccurately transcribed references may reduce stability and speaker similarity.[^audio8-01b-card]

## Inference and deployment

- The Transformers example recommends Python 3.11+ and a CUDA GPU; dependencies are `torch>=2.5.0`, `torchaudio>=2.5.0`, `transformers>=4.57.0,<5`, `soundfile>=0.12`, and `safetensors>=0.4`. `trust_remote_code=True` executes custom model code, which was not inspected; review and pin it before use.[^audio8-01b-card]
- Clone with text, reference audio and a matching reference transcript via `AutoProcessor`, then `model.generate` and `decode_audio`; the example samples with 512 maximum new tokens, temperature 0.7, top-p 0.9 and top-k 50. Omit both reference inputs for reference-free synthesis.[^audio8-01b-card]
- The separate ONNX INT8 release uses per-token INT8 Slow/Fast AR graphs and an FP16 codec, CPUExecutionProvider, and reportedly ~0.4 GiB loaded on tested Linux x86_64. It offers CLI, web/HTTP service, streaming PCM and voice registration without PyTorch or Transformers after download. Normal synthesis loads decoder sessions; registration releases them before loading an optional codec encoder. The card supplies no first-audio latency or throughput, so streaming PCM does not establish realtime performance.[^audio8-01b-card]

## Reported evaluation

| Suite | 0.1B result | 0.6B comparison |
| --- | --- | --- |
| Seed-TTS EN WER / SIM | 1.662 / 56.7 | 1.506 / 63.2 |
| Seed-TTS ZH CER / SIM | 1.13 / 68.2 | 0.950 / 73.1 |
| CV3 zh / en error rates | 3.619 / 3.307 | 3.205 / 3.128 |
| CV3 ja / ko / de / es / fr / it error rates | 12.322 / 7.653 / 5.292 / 8.548 / 12.349 / 14.480 | 7.205 / 4.223 / 3.447 / 3.641 / 8.790 / 4.790 |

Lower WER/CER or error rate is better; higher SIM is better, and SIM is expressed as a percentage. The CV3 baselines are reference values from the 0.6B table, not a matched re-evaluation; the card also warns of different normalizers and evaluators across projects. Fish S2 Pro was reevaluated and Higgs Audio v2 locally evaluated; other baseline values came via VoxCPM. Parameter comparisons are approximate and not a matched audit; the separate codec matters for footprint comparisons.[^audio8-01b-card]

## License and responsible use

The card summarizes Audio8 Community License v1.0 as free for non-commercial use and for commercial use by entities with annual revenue below US$2 million, including affiliates, parent and subsidiaries; entities at or above that threshold need a separate written commercial license. The authoritative English license text was not inspected, so check the actual terms before relying on this summary. Obtain speaker consent and disclose synthetic audio where appropriate.[^audio8-01b-card]

## Relationships

- Related checkpoint: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) shares the reported slow/fast AR and 44.1 kHz codec pattern, but has different scale, language claims, CPU packaging and license; do not transfer its Apache-2.0 label to 0.1B (**Synthesis**).[^audio8-01b-card]
- Listed in the [TTS Model Survey](tts-model-survey.md) alongside other TTS deployment options.

## Coverage and limits

The local model-card capture was read in full and inspected statically. A second local capture is byte-identical (**Observed**).[^audio8-01b-duplicate] Its decorative header image is absent locally; teaser video and sample audio were not reviewed. Model weights, codec, tokenizer, remote code, ONNX release and guide, training/inference repository, license text, and evaluation datasets and linked baseline reports were not inspected. No download, install, execution, synthesis, listening, license verification or benchmark was performed. The card has no immutable revision, release or capture date, training data, TTFA, throughput or detailed evaluation protocol; its Linux CPU memory figure is configuration-specific. Draft status records these material trust and coverage limits.[^audio8-01b-card]

[^audio8-01b-duplicate]: [Duplicate model-card capture](../raw/Edge0-Audio8-TTS-Preview-0.1b.md) — complete file, compared with the other capture.

[^audio8-01b-card]: [Audio8 TTS Preview 0.1B model card](../raw/Audio8-TTS-Preview-0.1b.md) — frontmatter and introduction; “Compact Scale”; “Supported Languages”; “Model Details”; “Deployment Options / CPU deployment: ONNX INT8”; “Installation”; “Usage / Voice cloning”; “Evaluation / CV3 error-rate comparison” and “Seed-TTS comparison”; “Limitations and Responsible Use”; “License”.
