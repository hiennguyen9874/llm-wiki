---
type: Concept
title: Sentio
description: A 10.20B composite omni-modal embedding model that adds a LoRA-tuned Qwen2.5-Omni audio tower and connector to WeMM-Embedding-9B, with a self-reported 61.69 overall on MMEB-V3.
tags: [embedding, retrieval, multimodal, omni-modal, audio, video, qwen, mmeb]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:59:55Z }
stale_after: 2027-01-20
sources:
  - id: sentio-card
    resource: ../raw/Dragos-Datcu-Sentio.md
    kind: model-card
    title: Dragos-Datcu/Sentio Hugging Face model page (HTML capture)
---

# Sentio

Sentio is a community-released composite embedding model that gives [WeMM-Embedding](wemm-embedding.md) 9B an audio path. It freezes WeMM-9B and the audio tower of Qwen2.5-Omni-3B, trains a connector, adapter fusion, and an audio-tower LoRA between them, and also applies a small video-moment-retrieval LoRA to the 9B tower. Audio lands in WeMM's 4,096-dimensional space, so existing WeMM indexes need no re-indexing. Total 10.20B parameters, 152M (1.5%) trained.[^sentio-card] All scores below are **Reported** (self-reported on the model card; no independent reproduction). The page does not name a technical report.

## Model facts

| Field | Value |
|---|---|
| Author / repo | Dragos-Datcu / `Sentio` (Hugging Face); 0 likes and 12 downloads last month at capture |
| Base models | [WeMM-Embedding](wemm-embedding.md) 9B (Tencent, Apache-2.0); Qwen2.5-Omni-3B audio tower only (638M, Alibaba, Qwen Research License) |
| Output | 4,096-d, L2-normalized; inner-product ranking (`audio @ text.T`) |
| Modalities | audio, text, image, video, visual document (non-audio via WeMM-9B + vdr LoRA) |
| Audio input | 128-bin Whisper-style mel features, 30 s head crop, masked-mean pooled over frames (one vector per clip) |
| License | Own code, card, and trained parameters Apache-2.0; the Qwen2.5-Omni audio tower keeps its own Qwen Research License terms |
| Languages | not listed; most training targets are English |

Source: model card header, How it works, Usage, License.[^sentio-card]

## Architecture

Audio path: waveform → mel features → Qwen2.5-Omni audio tower with LoRA (r=16) → 2,048-d pooled vector → 3-layer MLP connector (2,048→4,096→8,192→4,096, LayerNorm + GELU) → modality adapter fusion → RMSNorm projection → L2 normalize.[^sentio-card]

- **Adapter fusion:** four residual bottleneck adapters (text, audio, video, label; each 4,096→512→4,096, ≈4.19M parameters) are mixed by a softmax gate over the audio vector (4,096→1,024→4), with an entropy bonus during training to prevent gate collapse. The rationale: captions need meaning, audio–audio needs acoustic detail, video needs timing, labels need category.[^sentio-card]
- **Shared prototypes:** 64 learnable vectors used only in the training loss; ignored at inference.[^sentio-card]
- **Non-audio path:** identical to WeMM-9B with the stage-1 "vdr" LoRA (r=16, α=32, 43.3M) applied.[^sentio-card]
- **Parameter budget:** WeMM-9B tower 9,408M frozen; audio tower 638M frozen; trained 43.3M (vdr LoRA) + 11.8M (audio LoRA) + 75.5M (connector) + 21.0M (adapters and gate) + 0.27M (norm and prototypes). The card says counts were measured from weight files.[^sentio-card]

## Training

- **Stage 1 (tower):** 600 InfoNCE steps at temperature 0.045; 8/11 of each batch DiDeMo moment–query pairs and 1/11 each of MSR-VTT, MSCOCO text-to-image, and ColPali page–query replay so image, video, and document scores do not regress.[^sentio-card]
- **Stage 2 (audio, tower frozen):** symmetric in-batch InfoNCE (temperature 0.07) plus prototype contrastive (0.03), symmetric KL on prototype assignments (0.01), prototype balance (0.005), and gate-entropy bonus (0.01). Label datasets use batches with each label at most once to avoid false negatives. Data: 449k audio–target pairs over 37k targets from seven public datasets (NSynth, SpeechCommands, FSD50K, RAVDESS, Clotho, Flickr8k Audio, AVE), sampled naturally so NSynth dominates. Batch size 16, learning rates 1e-5 (head) and 1e-4 (audio LoRA), 500 warm-up steps, 498,000 steps on one H200; checkpoint chosen by lowest held-out InfoNCE (~step 408,000).[^sentio-card]

## Reported results

Evaluation used the Tencent WeMM harness on all 190 MMEB-V3 tasks, with audio modifications from Wianmu for the 11 audio tasks, and the leaderboard's own scoring code. The two TUTSound tasks (audio + text queries) are scored by summing the two unit embeddings equally and re-normalizing. Leaderboard snapshot date: 16 Oct 2026.[^sentio-card]

| MMEB-V3 (190 tasks) | Overall | Overall-V3 | Text | Audio | Agent | Image | Video | Visdoc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Sentio | 61.69 | 48.46 | 48.98 | 36.81 | 50.57 | 80.90 | 75.04 | 83.28 |
| Wianmu-5B-v0 | 60.45 | 47.50 | 48.13 | 42.93 | 48.00 | 79.73 | 71.56 | 81.99 |
| WeMM-Embedding-9B | 59.33 | 44.54 | 48.76 | — | 50.10 | 80.99 | 74.31 | 83.34 |
| Wianmu-3B-v0 | 58.16 | 44.37 | 45.30 | 41.16 | 44.11 | 78.67 | 70.79 | 80.80 |

MMEB-V2 (78 tasks): Sentio 80.68 overall versus WeMM-9B 80.58; Video-MRET 61.53 vs 58.46 (the stage-1 target); Image 81.77 vs 81.87; Visdoc 83.28 vs 83.34 — i.e. a video-moment gain with essentially neutral other groups.[^sentio-card]

Audio hit@1 (Sentio / Wianmu-3B / Wianmu-5B): NSynth 76.10 / 74.10 / 60.90; ESC-50 56.15 / 79.20 / 86.60; UrbanSound8K 55.92 / 64.05 / 66.63; SpeechCommands 89.50 / 89.80 / 89.90; CREMA-D 33.74 / 47.08 / 48.93; Clotho 8.48 / 13.61 / 16.56; SoundDescs 6.10 / 9.50 / 20.50; TUTSound 61.76 / 52.96 / 46.89; AVE 9.20 / 16.42 / 18.66; SpeechCOCO 2.80 / 1.50 / 13.00. A-CLS / A-RET / Audio-Overall: Sentio 62.28 / 15.58 / 36.81 versus 70.85 / 16.42 / 41.16 (3B) and 70.59 / 19.88 / 42.93 (5B).[^sentio-card]

**Interpretation (Synthesis):** Sentio's top Overall rests on the 9B tower (text, agent, video, visual documents), not audio — its Audio score is the lowest of the three audio-capable models listed, while WeMM-9B scores no audio (0 in aggregate, shown "—"). The card concedes this and says the next releases target audio. Its Overall leadership is on the card's leaderboard snapshot only; it is not in the local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md).

## Limitations

- Audio is pooled to one vector: no fine timing, weak on grounding and moment-level audio tasks; clips over 30 s are truncated.[^sentio-card]
- Audio training is dominated by NSynth, so it is strong on instruments and sound events, weaker than the Wianmu models on environmental scenes, emotion, and audio captions.[^sentio-card]
- Frozen tower: whatever WeMM-9B cannot distinguish, Sentio cannot either; label names collide across datasets ("happy" in SpeechCommands vs RAVDESS share one target vector). Mostly English targets.[^sentio-card]
- **Not self-contained:** the repo holds only the card, `config.json`, and `modeling_sentio.py`; the vdr LoRA adapter (43M) and `trainable.pt` (109M: audio head and audio-tower LoRA) are stated as not distributed there, and the base checkpoints come from their own repositories. As captured, the model therefore cannot be reproduced from the repository alone. Usage requires `Sentio.from_pretrained` with four local paths (WeMM-9B, adapter, Qwen2.5-Omni-3B, trainable weights).[^sentio-card]
- Licensing is mixed: the Qwen Research License applies to the audio-tower component, which matters for commercial use (not interpreted here).[^sentio-card]
- Coverage limit: the capture is an HTML page; the linked Tianmu-Emb-Uni, WeMM, and evaluation-harness pages were not supplied. Wianmu results are as quoted on this card. Page navigation, scripts, and embedded site configuration were excluded as non-substantive.

## Relationships

- **Builds on:** [WeMM-Embedding](wemm-embedding.md) (9B tower and 4,096-d space); the card cites WeMM-9B as the strongest open model for text, images, video, and visual documents, which is consistent with the [WeMM report](wemm-embedding.md) but not re-verified here.
- **Reuses recipe from:** [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) (frozen embedding model + frozen Qwen2.5-Omni audio tower + trained connector, prototype loss); the same Qwen2.5-Omni audio tower family underlies [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md) and [e5-omni](e5-omni.md), which train the whole backbone instead.
- **Compares against / credits:** Wianmu-5B-v0 (see [Wianmu-5B](wianmu-5b.md)) and Wianmu-3B-v0 (see [Wianmu-3B](wianmu-3b.md)).
- **Compared against by:** [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md), whose card tabulates Sentio as the AVG and Video leader (79.57 / 65.45) on a 44-dataset MMEB-v2 retrieval subset (Reported by GeeVec).
- **Compared in:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).

[^sentio-card]: [Dragos-Datcu/Sentio model page](../raw/Dragos-Datcu-Sentio.md), HTML capture; model card sections How it works, Training, Evaluation (MMEB-V3, MMEB-V2, audio tasks tables), Known limitations, Usage, License, Credits. Author-reported; no independent reproduction; capture date not recorded (leaderboard snapshot cited as 16 Oct 2026).
