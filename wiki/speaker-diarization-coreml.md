---
type: Concept
title: Speaker Diarization Core ML
description: Core ML conversion set of pyannote speaker-diarization-community-1 for on-device Apple diarization via FluidAudio, with segmentation, embedding, and PLDA artifacts, provenance caveats, and legacy models.
tags: [vad, diarization, coreml, on-device, apple]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T15:00:00Z }
stale_after: 2027-10-06
sources:
  - id: speaker-diar-coreml-card
    resource: ../raw/speaker-diarization-coreml.md
    kind: documentation
    title: Speaker Diarization Core ML
---

Speaker Diarization Core ML is FluidInference's Core ML conversion of `pyannote/speaker-diarization-community-1` for on-device speaker diarization on Apple platforms via FluidAudio, distributing compiled segmentation, feature-extraction, embedding, and PLDA artifacts plus serialized parameters under a scoped CC-BY-4.0 grant, with SHA-256-pinned but not fully attested-reproducible provenance and separate legacy diarizer artifacts outside the Community-1 scope (**Reported**).[^speaker-diar-coreml-card]

## Identity and upstream

- Card title is `Speaker Diarization Core ML`; frontmatter declares `base_model: pyannote/speaker-diarization-community-1`, `pipeline_tag: voice-activity-detection`, `license: other` with `license_name: scoped-cc-by-4.0` and a NOTICE.md license-scope link, and tags `speech`, `audio`, `voice`, `speaker-diarization`, `speaker-change-detection`, `coreml`, `speaker-segmentation` (**Reported**).[^speaker-diar-coreml-card]
- Conversions are used by [FluidAudio](https://github.com/FluidInference/FluidAudio) for on-device diarization on Apple platforms; these are Core ML conversions, not fine-tuned models (**Reported**).[^speaker-diar-coreml-card]
- The supported Community-1 artifact set is distributed under CC-BY-4.0 with attribution and precise license scope in `NOTICE.md`, and source, conversion, environment, and file-integrity records in `PROVENANCE.md` plus `provenance.json` (**Reported**).[^speaker-diar-coreml-card]

## Supported Community-1 artifacts

| Artifact | Source |
| --- | --- |
| `Segmentation.mlmodelc` | `pyannote/speaker-diarization-community-1/segmentation/pytorch_model.bin` |
| `FBank.mlmodelc` | Deterministic feature-extraction graph configured from the embedding checkpoint |
| `Embedding.mlmodelc` | `pyannote/speaker-diarization-community-1/embedding/pytorch_model.bin` |
| `PLDA.mlmodelc`, `PldaRho.mlmodelc` | `plda/plda.npz` and `plda/xvec_transform.npz` |
| `plda-parameters.json`, `xvector-transform.json` | Serialized tensors from the same two PLDA files |

Table values are the card's supported-artifact mapping (**Reported**).[^speaker-diar-coreml-card]

- The snapshot includes uncompiled packages for `Segmentation`, `FBank`, `Embedding`, and `PldaRho` under `mlpackages/`; no uncompiled `PLDA` package was published (**Reported**).[^speaker-diar-coreml-card]

## Provenance status

- Artifacts are pinned by SHA-256 in `provenance.json`; historical source lineage was reconstructed from the public Community-1 repository, artifact metadata, and the published conversion source (**Reported**).[^speaker-diar-coreml-card]
- The exact local upstream checkout and Mobius commit used for the original 2025 conversion were not recorded, so the existing binaries are not described as a fully attested reproducible build (**Reported**).[^speaker-diar-coreml-card]
- Immutable upstream reference used for reconstruction is `pyannote/speaker-diarization-community-1@3533c8cf8e369892e6b79ff1bf80f7b0286a54ee`; public historical conversion reference is `FluidInference/mobius@33fd6eab634966ae7db4d73da3376a90379642fb/models/speaker-diarization/pyannote-community-1/coreml` (**Reported**).[^speaker-diar-coreml-card]
- The current conversion pipeline requires a full upstream commit SHA, records input and output hashes, embeds source metadata in each model, and captures the build environment, at `FluidInference/mobius@ffbc3c8cae2d0ac83912a005a25a2874ced98a3a/models/speaker-diarization/pyannote-community-1/coreml` (**Reported**).[^speaker-diar-coreml-card]

## Legacy compatibility artifacts

- The repository also retains `pyannote_segmentation.mlmodelc`, `wespeaker.mlmodelc`, `wespeaker_v2.mlmodelc`, and `wespeaker_int8.mlmodelc` for FluidAudio's legacy online diarizer (**Reported**).[^speaker-diar-coreml-card]
- They predate the Community-1 export, record a different toolchain, and are not included in the Community-1 provenance or license-scope confirmation in `NOTICE.md` (**Reported**).[^speaker-diar-coreml-card]

## Technical specifications

- Input: 16 kHz mono audio; output: speaker segments with timestamps and speaker identifiers (**Reported**).[^speaker-diar-coreml-card]
- Framework: Core ML converted from PyTorch; deployment target: iOS 17 / macOS 14 or later (**Reported**).[^speaker-diar-coreml-card]
- Community-1 conversion metadata: PyTorch 2.8.0, coremltools 9.0b1, TorchScript source dialect; compiled MIL metadata: coremlc 3500.32.1, MIL 3500.14.1 (**Reported**).[^speaker-diar-coreml-card]

## Usage

- See the FluidAudio diarization documentation at `github.com/FluidInference/FluidAudio/tree/main/Documentation/Diarization` (**Reported**).[^speaker-diar-coreml-card]

## Research lineage

- Speaker segmentation cites Plaquet and Bredin (INTERSPEECH 2023) on powerset multi-class cross-entropy loss for neural speaker diarization; speaker embedding cites Wang et al. (ICASSP 2023) on the Wespeaker toolkit; speaker clustering cites Landini et al. (Computer Speech & Language 2022) on Bayesian HMM clustering of x-vector sequences (VBx) (**Reported**).[^speaker-diar-coreml-card]

## Relationships

- Alternative to [Nemotron 3 Diarization](nemotron-3-diarization.md): NVIDIA open-weight streaming/offline GPU diarizer for up to eight speakers with DER/RTFx benchmarks, while this concept covers the Apple on-device Core ML conversion of the pyannote Community-1 pipeline with no DER figures in the card (**Synthesis**).[^speaker-diar-coreml-card]
- Alternative to [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md) and [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md): NeMo offline/streaming up-to-four-speaker diarizers, while this concept covers a pyannote-lineage Core ML packaging for iOS 17 / macOS 14 or later (**Synthesis**).[^speaker-diar-coreml-card]
- Alternative to [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md): joint long-form transcription plus diarization plus timestamps model, while this concept covers diarization-only segmentation/embedding/PLDA artifacts that return speaker segments without transcribed words (**Synthesis**).[^speaker-diar-coreml-card]
- Related edge packaging: [Nemotron 3 Diarization GGUF](nemotron-3-diarization-gguf.md) is also an edge-format conversion (GGUF for audio.cpp with BF16/Q8_0 weights and quantization caveats), while this concept covers Core ML `.mlmodelc` plus `mlpackages/` artifacts for Apple deployment (**Synthesis**).[^speaker-diar-coreml-card]

## Coverage and limits

- Source inspected statically only; no model files executed, no audio processed, and no diarization accuracy or latency figures reproduced (**Synthesis**).[^speaker-diar-coreml-card]
- Referenced local artifacts (`NOTICE.md`, `PROVENANCE.md`, `provenance.json`, compiled `.mlmodelc` files, `mlpackages/`, PLDA `.npz` files, and JSON parameter files) were not present in `raw/` and were not inspected; linked external pages (FluidAudio repository and diarization docs, upstream Hugging Face revision, Mobius conversion references) were not fetched (**Synthesis**).[^speaker-diar-coreml-card]
- All identity, artifact-mapping, provenance, compatibility, deployment-target, toolchain-version, and licensing characterizations are source assertions without independent verification in this wiki; model-release and toolchain figures carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^speaker-diar-coreml-card]

[^speaker-diar-coreml-card]: [Speaker Diarization Core ML](../raw/speaker-diarization-coreml.md) — locators: frontmatter (`license`, `license_name`, `license_link`, `tags`, `base_model`, `pipeline_tag`); intro (FluidAudio on-device use, CC-BY-4.0 scope with `NOTICE.md` link, `PROVENANCE.md` plus `provenance.json` records, conversions-not-finetuned note); section `Supported Community-1 artifacts` (5-row artifact-to-source table, `mlpackages/` uncompiled-package paragraph with no-`PLDA` note); section `Provenance status` (SHA-256 paragraph, not-fully-attested paragraph with unrecorded checkout/commit, `3533c8cf` upstream link, `33fd6eab` historical and `ffbc3c8` current Mobius links with full-SHA plus hash-recording plus metadata-embedding plus environment-capture requirements); section `Legacy compatibility artifacts` (4-file list, predates-Community-1 plus different-toolchain plus excluded-from-`NOTICE.md` paragraph); section `Technical specifications` (16 kHz mono, segments-with-timestamps-and-IDs, Core-ML-from-PyTorch, iOS 17 / macOS 14, PyTorch 2.8.0 / coremltools 9.0b1 / TorchScript, coremlc 3500.32.1 / MIL 3500.14.1 bullets); section `Usage` (FluidAudio `Documentation/Diarization` link); section `Citations` (Plaquet23, Wang2023, Landini2022 bibtex blocks). Referenced binaries, `NOTICE.md`, `PROVENANCE.md`, `provenance.json`, and `mlpackages/` have no locator available in `raw/` (files absent).
