---
type: Concept
title: Resemblyzer
description: Python voice-encoder library that turns speech into a 256-value speaker embedding for voice similarity, verification, diarization, and feature analysis, with README-reported demos and speed claims but no measured accuracy, protocol, or license in the capture.
tags: [vad, diarization, speaker-embedding, speaker-verification, tts, voice-cloning]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T05:00:07Z }
stale_after: 2027-04-13
sources:
  - id: resemblyzer-readme
    resource: ../raw/resemblyzer.md
    kind: documentation
    title: Resemblyzer README capture
---

Resemblyzer is an open-source Python package that runs a PyTorch voice encoder over one utterance of speech and returns a 256-value embedding summarizing the speaker's voice (**Reported**).[^resemblyzer-readme] The embedding is a building block. The README names voice similarity, speaker verification, speaker diarization, and feature analysis as uses, and points to a separate project for voice cloning rather than synthesizing speech itself. Its speed, noise, and language claims come with no protocol, dataset, or license in the capture, so they stay unverified. In this wiki, the package supplies the Target Sim measure inside [KVoiceWalk](kvoicewalk.md).

## Model and interface

- **Input and output.** The example reads a file path with `preprocess_wav` and calls `VoiceEncoder().embed_utterance(wav)` to get the embedding (lines 44–58).[^resemblyzer-readme] The README does not state the expected sample rate, preprocessing steps, or minimum utterance length (**Observed** from the static example; not executed).
- **Embedding.** One 256-value vector per utterance (line 1).[^resemblyzer-readme] The README does not say whether vectors are normalized or which similarity function its demos use. It tells readers to view the demos "to understand how similarity is computed" (line 60).
- **Model.** A deep-learning voice encoder written in PyTorch (line 39), implemented from the Generalized End-To-End loss paper, where it is called the speaker encoder (line 63).[^resemblyzer-readme] Architecture, size, training data, and weights license are not in the capture.
- **Runtime.** Runs on CPU or GPU (line 41).[^resemblyzer-readme] The bundled pretrained model is described as interchangeable with models from the Real-Time-Voice-Cloning project and fine-tunable on new data (line 63).
- **Installation.** `pip install resemblyzer`, with Python 3.5+ stated as required (line 3).[^resemblyzer-readme] That floor is old and was not tested here (**Unverified**).

## Applications named in the README

| Use | README description | Evidence and limit | Locator |
| --- | --- | --- | --- |
| Voice similarity | Compare voices and report how similar they sound | No formula or scale in the capture | line 31 |
| Speaker verification | Build a profile from 5–30 s of speech; reject scores below a threshold | No threshold or error rate given | line 32 |
| Speaker diarization | Match profiles against a continuous embedding of a multispeaker segment (demo 02) | No DER, latency, streaming mode, or overlap handling | lines 6, 33 |
| Fake speech detection | Compare unknown utterances with reference audio (demo 05) | 12 utterances with one error; the README calls it "modest" | lines 11, 13 |
| Feature analysis | Embeddings as features for accent, tone, prosody, or gender analysis | Possible use; no evaluation in the README | lines 35, 37 |
| Voice cloning | Pointed to a separate project | Resemblyzer does not synthesize speech | line 36 |
| Virtual voices | Sample new embeddings from a prior distribution | No prior or method given | line 38 |
| Loss function | Backpropagate through the encoder as a perceptual loss | No example or result | line 39 |

All rows are **Reported**.[^resemblyzer-readme]

## Performance and robustness claims

- **Speed.** "Around 1000x real-time on a GTX 1080, with a minimum of 10ms for I/O operations" (line 41). **Reported**; batch size, utterance length, precision, and timing method are not stated.
- **Noise.** "It is robust to noise" (line 41), with no noise condition, SNR, or comparison (**Reported**; not evaluated).
- **Language.** Best on English and "somewhat decently" elsewhere (line 41). **Reported**; the capture has no Vietnamese or other non-English evidence.
- **Demo 03 (line 18).** 100 utterances from 10 speakers, projected in 2D. The README says a trivial clustering would give a 0% verification error on that example. **Reported** on a 100-utterance demonstration, not a benchmark.
- **Demo 04 (line 19).** 251 embeddings from distinct speakers. The README says the model "learned on its own to identify the sex of the speaker." **Reported**; the figure is in the upstream repository.
- **Demo 05 (line 11).** 12 utterances (6 real, 6 fake) with one error. **Reported**; too small to estimate an error rate.
- **Demo 01 (line 23).** Cross-similarity of 10 utterances against 10 others from the same speakers. The capture holds no values.

## Uses in this wiki

- **KVoiceWalk.** [KVoiceWalk](kvoicewalk.md) uses Resemblyzer for Target Sim, the walk's objective, which is combined with self-similarity and feature similarity in [KVoiceWalk Scoring Function](kvoicewalk-scoring-function.md). The claims about that tool come from its own README; this page does not repeat them (**Synthesis** for this link). Its Target Sim values are specific to that tool and should not be compared with speaker-similarity figures from other evaluation protocols, such as those in [CosyVoice2-0.5B](cosyvoice2-0.5b.md) (**Synthesis**).
- **Diarization context.** Diarization concepts in this wiki publish DER and latency, for example [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md). The Resemblyzer README publishes neither, so its diarization demo cannot be compared with them (**Synthesis**). [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) covers another speaker-embedding stack, which cites its own source.
- **Turn-taking.** The README addresses speaker identity over a segment, not speech boundaries, endpointing, or streaming. Boundary decisions would come from a VAD such as [Silero VAD](silero-vad.md) (**Synthesis**).
- **Trust.** A voice profile identifies a person. The README does not address consent, storage, or retention of profiles, which matter before speaker profiles are used in production (**Synthesis**).

## Coverage and limits

- **Inspected statically:** the whole README capture, lines 1–63.[^resemblyzer-readme]
- **Not executed:** nothing was installed, imported, or run. The code example and every figure stay **Reported** or **Observed**.
- **Not captured:** the demo scripts `demo01` through `demo05` (linked from lines 6, 11, 18, 19, and 23), the `plots/` images, the bundled demo audio (line 3), the PyPI package and its metadata, the source code, the pretrained weights, the license file, the GE2E paper (arXiv 1710.10467), the Real-Time-Voice-Cloning repository, and the upstream revision (not recorded in the capture).
- **License:** the capture states none, so licensing is not established.
- **Contradictions:** none found within the capture.
- **Staleness:** the speed figure, the Python floor, and the demo claims are time-sensitive, so `stale_after` is set to 2027-04-13.

[^resemblyzer-readme]: [Resemblyzer README capture](../raw/resemblyzer.md) — locators: line 1 embedding definition; line 3 install command, Python 3.5+ floor, and demo-audio note; lines 5–23 demo links, figures, and claims (demo 01 line 23, demo 02 line 6, demo 03 line 18, demo 04 line 19, demo 05 line 11); lines 29–39 application list; line 41 speed, noise, and language claims; lines 44–58 code example; line 60 demo pointer; lines 62–63 origin, pretrained-model, and paper notes.
