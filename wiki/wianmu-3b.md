---
type: Concept
title: Wianmu-3B
description: A community audio extension of WeMM-Embedding-2B that trains only a ~64M-parameter connector between a frozen Qwen2.5-Omni-3B audio tower and the frozen 2,048-dimensional WeMM space, leaving text, image, and video embeddings unchanged.
tags: [embedding, retrieval, multimodal, omni-modal, audio, qwen, wemm, mmeb]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:59:55Z }
stale_after: 2027-01-20
sources:
  - id: wianmu-3b-page
    resource: ../raw/eduardo-terres2-Wianmu-3B.md
    kind: model-card
    title: eduardo-terres2/Wianmu-3B Hugging Face model page (HTML capture)
  - id: sentio-card
    resource: ../raw/Dragos-Datcu-Sentio.md
    kind: model-card
    title: Dragos-Datcu/Sentio Hugging Face model page (HTML capture)
---

# Wianmu-3B

Wianmu-3B ("WeMM + Tianmu") gives [WeMM-Embedding](wemm-embedding.md) 2B an audio input without retraining it. Both the WeMM-2B embedder and the audio encoder of Qwen2.5-Omni-3B stay frozen; only a small connector, four modality adapters, a gate, a projection, and 64 loss-only prototypes are trained (~64M parameters, under 2% of the ~2.9B total). Because WeMM is untouched, text, image, and video embeddings equal plain WeMM-2B's, and audio lands in the same 2,048-dimensional space, so an audio clip can be compared directly with a caption, label name, image, or video.[^wianmu-3b-page] It applies the recipe of [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) to WeMM; [Sentio](sentio.md) later applied it to WeMM-9B. Claims below are **Reported** (author text on the model page) unless labeled otherwise; the page itself contains no score table.

## Model facts

| Field | Value |
|---|---|
| Hub repo | `eduardo-terres2/Wianmu-3B`; created 2026-10-13, last modified 2026-10-16; 2 likes, 41 downloads last month at capture; not gated; no inference provider |
| Base models (card metadata) | `tencent/WeMM-Embedding-2B` and `Qwen/Qwen2.5-Omni-3B` (audio tower only) |
| Pipeline tag / tags | `feature-extraction`; audio, multimodal-embedding, audio-retrieval, audio-classification |
| Output | 2,048-d, L2-normalized |
| Audio input | Whisper-style mel features, 128 bins, up to 30 s; frame-mean pooled to one vector |
| Parameters | trained ≈64M (mostly the connector); frozen audio tower 638M; frozen WeMM 2.21B excluding its unused language-model head; ≈2.9B total |
| License | Apache-2.0 (Hub metadata) |
| Languages | not listed; most training targets are English |

Locators: header metadata (`cardData`, `createdAt`, `lastModified`, downloads), How it works, Known limitations.[^wianmu-3b-page]

## Architecture

waveform → mel features → frozen Qwen2.5-Omni audio tower, mean pooled over frames → 3-layer MLP connector (LayerNorm + GELU) → modality adapter fusion → RMSNorm projection → L2 normalize → 2,048-d embedding.[^wianmu-3b-page]

- **Adapter fusion:** four residual bottleneck adapters (text, audio, video, label), each Linear 2,048→256 (no bias), GELU, Linear 256→2,048 (no bias), 1,048,576 parameters each. A gate (Linear 2,048→512 with LayerNorm, GELU, Linear 512→4 with bias; 1,051,652 parameters) reads the audio vector and mixes the four outputs with softmax weights. The stated rationale: captions need meaning, audio–audio needs acoustic detail, video needs timing, labels need category; a gate-entropy bonus prevents collapse onto one adapter.[^wianmu-3b-page]
- **Shared prototypes:** 64 learnable vectors; audio and target embeddings get soft assignments over them and are pushed to agree. Used only in the loss, ignored at inference.[^wianmu-3b-page]
- **Parameter arithmetic (Synthesis):** adapters plus gate total ≈5.25M, so the connector holds nearly all of the ≈64M trained parameters, matching the card's statement; 0.64B + 2.21B + 0.06B ≈ 2.9B.[^wianmu-3b-page]

## Training

- **Loss:** symmetric InfoNCE between audio and target embeddings (temperature 0.07) does most of the work, plus a prototype loss (prototype-assignment contrastive term, symmetric KL between audio and target assignments, usage-balance term) and the gate entropy bonus, both small-weight. Exact loss weights are not on the page.[^wianmu-3b-page]
- **False-negative control:** label datasets are batched so each label appears at most once, so two "dog bark" clips are not treated as negatives.[^wianmu-3b-page]
- **Data:** about 650k pairs from ten public audio datasets. Label-target classification sets: NSynth, TAU Urban, SpeechCommands, FSD50K, RAVDESS, TUT SED; caption pairs: AudioCaps, Clotho; Flickr8k Audio (spoken caption ↔ image); AVE (clip ↔ source video). Each epoch is half equal-per-dataset sampling and half weighted toward datasets with the most varied targets, to stop NSynth dominating.[^wianmu-3b-page]
- **Optimization:** batch size 64, learning rate 1e-5, 500 warm-up steps, single GPU.[^wianmu-3b-page]

## Evaluation

The page states evaluation used the Tencent WeMM harness (`mmeb_v3_eval`, a vlm2vec variant with modifications) on the audio tasks of MMEB-V3 (classification, retrieval, grounding) but reports no numbers.[^wianmu-3b-page] Scores come from the [Sentio](sentio.md) card's table of the MMEB-V3 leaderboard snapshot of 16 Oct 2026 (190 tasks), where the model is named "Wianmu-3B-v0". They are **Reported by a different author**, not reproduced:[^sentio-card]

| Overall | Overall-V3 | Text | Audio | Agent | Image | Video | Visdoc |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 58.16 | 44.37 | 45.30 | 41.16 | 44.11 | 78.67 | 70.79 | 80.80 |

Audio hit@1: NSynth 74.10, ESC-50 79.20, UrbanSound8K 64.05, SpeechCommands 89.80, CREMA-D 47.08, Clotho 13.61, SoundDescs 9.50, TUTSound 52.96, AVE 16.42, SpeechCOCO 1.50; A-CLS 70.85, A-RET 16.42, Audio-Overall 41.16.[^sentio-card]

**Interpretation (Synthesis):** on the same snapshot, Wianmu-3B's Audio score (41.16) beats [Sentio](sentio.md)'s (36.81) but trails [Wianmu-5B](wianmu-5b.md)'s (42.93); its Overall (58.16) is below WeMM-9B (59.33) and Sentio (61.69), which differ mainly through their larger non-audio towers. Do not merge these Overall values with WeMM's own 59.5 (V3-All), Ovis's 58.46, or the local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md), which does not contain this model.

## Limitations

- Audio is pooled to one vector, so there is no fine intra-clip timing; grounding tasks suffer most. Clips over 30 s are truncated.[^wianmu-3b-page]
- Frozen WeMM: whatever WeMM cannot distinguish in text, Wianmu cannot either. Label names collide across datasets (for example "happy" is a SpeechCommands word and a RAVDESS emotion sharing one target vector). Most training targets are English. The model is undertrained on SpeechCOCO.[^wianmu-3b-page]
- Licensing: the page lists Apache-2.0 only; the Sentio card says the Qwen2.5-Omni audio tower keeps the Qwen Research License. This is an unresolved discrepancy about the redistributed component, not interpreted here (Unverified).[^wianmu-3b-page][^sentio-card]
- Coverage limits: the capture is an HTML page; the file tree, weights, loading code, usage example, and the evaluation harness were not supplied, so how to load the model and whether the weights are self-contained are not established. Site navigation, scripts, the downloads sparkline, and configuration blobs were excluded as non-substantive.

## Relationships

- **Builds on:** [WeMM-Embedding](wemm-embedding.md) (2B variant, 2,048-d Matryoshka-capable space; Wianmu documents only the full 2,048-d output).
- **Reuses recipe from:** [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) (frozen embedder + frozen Qwen2.5-Omni audio tower + trained connector with prototype loss); the same audio-tower family underlies [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md) and [e5-omni](e5-omni.md), which instead train a full omni backbone.
- **Sibling of:** [Wianmu-5B](wianmu-5b.md), the same method on WeMM-4B (2,560-d, ≈71M trained, ~1.4M pairs from twelve datasets).
- **Extended by:** [Sentio](sentio.md), which applies the method to WeMM-9B with an audio-tower LoRA; its card credits Wianmu-5B and tabulates Wianmu-3B as a baseline.
- **Compared in:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).

[^wianmu-3b-page]: [eduardo-terres2/Wianmu-3B model page](../raw/eduardo-terres2-Wianmu-3B.md), HTML capture; rendered sections How it works (pipeline, adapter table, prototypes, parameter budget), Training, Evaluation, Known limitations, Credits; embedded `cardData`/header props for base models, license, dates, downloads. Author-reported; the capture date is not recorded (Hub `lastModified` 2026-10-16).
[^sentio-card]: [Dragos-Datcu/Sentio model page](../raw/Dragos-Datcu-Sentio.md), HTML capture; Evaluation sections (MMEB-V3 190-task table, audio task table) and Limitations. Scores for "Wianmu-3B-v0" are relayed by a third party from the 16 Oct 2026 leaderboard snapshot; no independent reproduction.
