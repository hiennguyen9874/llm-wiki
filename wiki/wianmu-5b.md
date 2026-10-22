---
type: Concept
title: Wianmu-5B
description: A community audio extension of WeMM-Embedding-4B that trains only a ~71M-parameter connector between a frozen Qwen2.5-Omni-3B audio tower and the frozen 2,560-dimensional WeMM space, leaving text, image, and video embeddings unchanged.
tags: [embedding, retrieval, multimodal, omni-modal, audio, qwen, wemm, mmeb]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:59:50Z }
stale_after: 2027-01-20
sources:
  - id: wianmu-5b-page
    resource: ../raw/eduardo-terres2-Wianmu-5B.md
    kind: model-card
    title: eduardo-terres2/Wianmu-5B Hugging Face model page (HTML capture)
  - id: sentio-card
    resource: ../raw/Dragos-Datcu-Sentio.md
    kind: model-card
    title: Dragos-Datcu/Sentio Hugging Face model page (HTML capture)
---

# Wianmu-5B

Wianmu-5B ("WeMM + Tianmu") gives [WeMM-Embedding](wemm-embedding.md) 4B an audio input without retraining it. The WeMM-4B embedder and the audio encoder of Qwen2.5-Omni-3B stay frozen; only a small connector, four modality adapters, a gate, a projection, and 64 loss-only prototypes are trained (~71M parameters, under 2% of the ~5.2B total). Because WeMM is untouched, text, image, and video embeddings equal plain WeMM-4B's, and audio lands in the same 2,560-dimensional space, so an audio clip can be compared directly with a caption, label name, image, or video.[^wianmu-5b-page] It is the larger sibling of [Wianmu-3B](wianmu-3b.md) (WeMM-2B, 2,048-d) and applies the recipe of [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md); [Sentio](sentio.md) later applied it to WeMM-9B. Claims below are **Reported** (author text on the model page) unless labeled otherwise; the page itself contains no score table.

## Model facts

| Field | Value |
|---|---|
| Hub repo | `eduardo-terres2/Wianmu-5B`; created 2026-10-16, last modified 2026-10-16; 0 likes, 38 downloads last month and all-time at capture; not gated; no inference provider |
| Base models (card metadata) | `tencent/WeMM-Embedding-4B` and `Qwen/Qwen2.5-Omni-3B` (audio tower only); the Hub tag list records only the Qwen2.5-Omni-3B base-model link |
| Pipeline tag / tags | `feature-extraction`; audio, multimodal-embedding, audio-retrieval, audio-classification |
| Output | 2,560-d, L2-normalized |
| Audio input | Whisper-style mel features, 128 bins, up to 30 s; frame-mean pooled to one vector |
| Parameters | trained ≈71M (almost all the connector); frozen audio tower 638M; frozen WeMM-4B 4.54B excluding its unused language-model head; ≈5.2B total |
| License | Apache-2.0 (Hub metadata) |
| Languages | not listed; most training targets are English |

Locators: header metadata (`cardData`, `createdAt`, `lastModified`, `downloads`), How it works, Known limitations.[^wianmu-5b-page]

## Architecture

waveform → mel features → frozen Qwen2.5-Omni audio tower, mean pooled over frames → 3-layer MLP connector (LayerNorm + GELU) → modality adapter fusion → RMSNorm projection → L2 normalize → 2,560-d embedding.[^wianmu-5b-page]

- **Adapter fusion:** four residual bottleneck adapters (text, audio, video, label), each Linear 2,560→320 (no bias), GELU, Linear 320→2,560 (no bias), 1,638,400 parameters each. A gate (Linear 2,560→640, no bias, with LayerNorm(640), GELU, Linear 640→4 with bias; 1,642,244 parameters) reads the audio vector and mixes the four outputs with softmax weights. The stated rationale: captions need meaning, audio–audio needs acoustic detail, video needs timing, labels need category; a gate-entropy bonus prevents collapse onto one adapter.[^wianmu-5b-page]
- **Shared prototypes:** 64 learnable vectors; audio and target embeddings get soft assignments over them and are pushed to agree. Used only in the loss, ignored at inference.[^wianmu-5b-page]
- **Parameter arithmetic (Synthesis):** adapters plus gate total 8,195,844 ≈ 8.2M, so the connector, projection, and prototypes hold the remaining ≈63M of the ≈71M trained, consistent with the card's "almost all of it is the connector"; 0.638B + 4.54B + 0.071B ≈ 5.25B, matching "about 5.2B".[^wianmu-5b-page]
- **Scaling versus the 3B sibling (Synthesis):** the adapter bottleneck widens from 256 to 320 and the gate hidden size from 512 to 640 in proportion to the 2,048→2,560 embedding width, giving ~1.64M parameters per adapter instead of ~1.05M.[^wianmu-5b-page]

## Training

- **Loss:** symmetric InfoNCE between audio and target embeddings (temperature 0.07) does most of the work, plus the Tianmu prototype loss (prototype-assignment contrastive term, symmetric KL between audio and target assignments, usage-balance term) and the gate entropy bonus, both small-weight. Exact loss weights are not on the page.[^wianmu-5b-page]
- **False-negative control:** label datasets are batched so each label appears at most once, so two "dog bark" clips are not treated as negatives.[^wianmu-5b-page]
- **Data:** about 1.4M pairs from twelve public audio datasets. Label-target classification sets: NSynth, TAU Urban, SpeechCommands, FSD50K, RAVDESS, TUT SED; caption pairs: AudioCaps, Clotho, WavCaps; Flickr8k Audio and SpeechCOCO (spoken caption ↔ image); AVE (clip ↔ source video). Each epoch is split equally across datasets, to stop SpeechCOCO from taking a large share under natural sampling.[^wianmu-5b-page]
- **Optimization:** batch size 64, learning rate 1e-5, 500 warm-up steps, single GPU.[^wianmu-5b-page]
- **Differences from Wianmu-3B (Synthesis):** the 3B page lists ~650k pairs from ten datasets (no WavCaps, no SpeechCOCO) with half equal / half variety-weighted sampling; the 5B page lists ~1.4M pairs from twelve datasets with fully equal sampling.[^wianmu-5b-page]

## Evaluation

The page states evaluation used the Tencent WeMM harness (`mmeb_v3_eval`, a vlm2vec variant with modifications) on the audio tasks of MMEB-V3 (classification, retrieval, grounding) but reports no numbers.[^wianmu-5b-page] Scores come from the [Sentio](sentio.md) card's tables of the MMEB-V3 leaderboard snapshot of 16 Oct 2026 (190 tasks), where the model is named "Wianmu-5B-v0". They are **Reported by a different author**, not reproduced:[^sentio-card]

| Overall | Overall-V3 | Text | Audio | Agent | Image | Video | Visdoc |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 60.45 | 47.50 | 48.13 | 42.93 | 48.00 | 79.73 | 71.56 | 81.99 |

Audio hit@1: NSynth 60.90, ESC-50 86.60, UrbanSound8K 66.63, SpeechCommands 89.90, CREMA-D 48.93, Clotho 16.56, SoundDescs 20.50, TUTSound 46.89, AVE 18.66, SpeechCOCO 13.00; A-CLS 70.59, A-RET 19.88, Audio-Overall 42.93.[^sentio-card]

**Interpretation (Synthesis):** on the same snapshot Wianmu-5B's Audio (42.93) beats [Wianmu-3B](wianmu-3b.md) (41.16) and [Sentio](sentio.md) (36.81), mainly via audio–text retrieval (A-RET 19.88 vs 16.42 and 15.58) and SpeechCOCO (13.00 vs 1.50 and 2.80, consistent with the 5B model's added SpeechCOCO training data), while it is weaker on NSynth and TUTSound. Its Overall (60.45) is above WeMM-9B (59.33) and Wianmu-3B (58.16) but below Sentio (61.69), so a 4B tower plus audio connector reaches near-9B scores on this snapshot. Do not merge these Overall values with WeMM's own 59.5 (V3-All), Ovis's 58.46, or the local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md), which does not contain this model.

## Limitations

- Audio is pooled to one vector, so there is no fine intra-clip timing; grounding tasks suffer most. Clips over 30 s are truncated.[^wianmu-5b-page]
- Frozen WeMM: whatever WeMM cannot distinguish in text, Wianmu cannot either. Label names collide across datasets (for example "happy" is a SpeechCommands word and a RAVDESS emotion sharing one target vector). Most training targets are English.[^wianmu-5b-page]
- Licensing: the page lists Apache-2.0 only; the Sentio card says the Qwen2.5-Omni audio tower keeps the Qwen Research License. This is an unresolved discrepancy about the redistributed component, not interpreted here (Unverified).[^wianmu-5b-page][^sentio-card]
- Coverage limits: the capture is an HTML page; the file tree, weights, loading code, usage example, and the evaluation harness were not supplied, so how to load the model and whether the weights are self-contained are not established. The architecture diagram (`resources/wianmu_architecture.png`) is a remote image, not inspected; the text pipeline and adapter table cover the same content. Site navigation, scripts, the downloads sparkline, and configuration blobs were excluded as non-substantive.

## Relationships

- **Builds on:** [WeMM-Embedding](wemm-embedding.md) (4B variant, 2,560-d space; Wianmu documents only the full 2,560-d output).
- **Reuses recipe from:** [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) (frozen embedder + frozen Qwen2.5-Omni audio tower + trained connector with prototype loss); the same audio-tower family underlies [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md) and [e5-omni](e5-omni.md), which instead train a full omni backbone.
- **Sibling of:** [Wianmu-3B](wianmu-3b.md), the same method on WeMM-2B.
- **Extended by / compared in:** [Sentio](sentio.md), which applies the method to WeMM-9B with an audio-tower LoRA, credits Wianmu-5B, and tabulates it as a baseline.
- **Compared in:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).

[^wianmu-5b-page]: [eduardo-terres2/Wianmu-5B model page](../raw/eduardo-terres2-Wianmu-5B.md), HTML capture; rendered sections How it works (pipeline, adapter table, prototypes, parameter budget), Training, Evaluation, Known limitations, Credits; embedded `cardData`/header props for base models, license, dates, downloads. Author-reported; the capture date is not recorded (Hub `lastModified` 2026-10-16).
[^sentio-card]: [Dragos-Datcu/Sentio model page](../raw/Dragos-Datcu-Sentio.md), HTML capture; Evaluation sections (MMEB-V3 190-task table, audio task table) and Limitations. Scores for "Wianmu-5B-v0" are relayed by a third party from the 16 Oct 2026 leaderboard snapshot; no independent reproduction.
