---
type: Concept
title: e5-omni
description: A Qwen2.5-Omni-based 3B/7B omni-modal embedding family that uses explicit temperature, negative-selection, and covariance alignment during contrastive training.
tags: [embedding, retrieval, multimodal, omni-modal, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:30:00Z }
sources:
  - id: e5-omni-report
    resource: ../raw/2601.03666_e5-omni/acl.tex
    title: e5-omni technical-report LaTeX source
  - id: e5-omni-3b-card
    resource: ../raw/e5-omni-3B.md
    title: Haon-Chen/e5-omni-3B model card
  - id: e5-omni-3b-hub-page
    resource: ../raw/Haon-Chen-e5-omni-3B.md
    title: Haon-Chen/e5-omni-3B Hugging Face page capture (HTML)
  - id: e5-omni-7b-card
    resource: ../raw/e5-omni-7B.md
    title: Haon-Chen/e5-omni-7B model card
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
---

# e5-omni

e5-omni is an omni-modal embedding family with 3B and 7B variants, built by LoRA fine-tuning a Qwen2.5-Omni VLM as a contrastive bi-encoder for text, image, audio, and video inputs. Its training recipe leaves the backbone architecture unchanged while adding modality-aware temperature calibration, a debiased hard-negative curriculum, and batch whitening with covariance alignment. The technical report releases a 7B checkpoint, while the supplied 3B model card documents a separately available MIT-licensed checkpoint; none of the supplied source artifacts states its embedding dimensionality. A captured Hub page shows that the 3B checkpoint holds 4.703B BF16 parameters, about 1.6× its “3B” name. [^e5-omni-report] [^e5-omni-3b-card] [^e5-omni-7b-card] [^e5-omni-3b-hub-page]

## Method

- **Modality-aware temperature calibration:** Each input receives a temperature calculated as the mean of learned per-modality values for its active modalities; pairwise logits divide similarity by the average of the two input temperatures. This calibrates contrastive-logit sharpness across modality compositions. [^e5-omni-report]
- **Controllable negative curriculum:** The loss retains the top `(1 - rho)` fraction of in-batch and mined negatives by similarity, increasing `rho` after warmup to focus progressively on harder negatives. A masked Debiased Contrastive Learning objective subtracts a scaled positive term from the negative aggregate to reduce potential false-negative bias. [^e5-omni-report]
- **Batch whitening and covariance alignment:** One whitening transform, estimated from the concatenated query and positive-target batch, is applied to both sets. A CORAL-style Frobenius penalty then aligns their covariance matrices. [^e5-omni-report]

The reported 7B configuration uses 512-token query and target limits, one training epoch, LoRA adaptation, two dataset-provided hard negatives per query, and an eight-H100 training setup. Its learned temperatures are 0.0130 (text), 0.0127 (image), 0.0219 (audio), and 0.0223 (video); the reported curriculum uses `rho` from 0.1 to 0.5 after 4,000 steps, DCL coefficient 0.1, and CORAL weight 0.05. [^e5-omni-report]

## Training coverage

The training mixture combines BGE-M3 text pairs; MMEB-V1 and PixMo text-image pairs; MSR-VTT and MMEB-V2 text-video pairs; AudioCaps text-audio pairs; and MMEB-V2 visual-document pairs. The report does not give mixture weights, sample counts, language distribution, filtering or deduplication methods, or contamination analysis. [^e5-omni-report]

## Deployment

The supplied `Haon-Chen/e5-omni-3B` model card identifies this 3B checkpoint as a Sentence Transformers model derived from `Qwen/Qwen2.5-Omni-3B`. Its documented API uses `encode_query` for queries and `encode_document` for candidates, then compares their normalized representations with the wrapper's similarity function. Candidates can be text or media paths/URLs, or dictionaries combining `text`, `image`, `audio`, and `video`; its examples cover text-to-video, text-to-audio, text-to-image/visual-document, and multilingual text retrieval. [^e5-omni-3b-card]

The 7B card identifies `Haon-Chen/e5-omni-7B` as an MIT-licensed Sentence Transformers model derived from `Qwen/Qwen2.5-Omni-7B`. Its quickstart installs Sentence Transformers with image, audio, and video extras plus `transformers>=5.6.0`; it loads the model in bfloat16 and recommends, but does not require, FlashAttention 2. For smaller GPUs it shows reducing video processor pixels and sampling frames at 1 fps. Its lower-level Transformers example uses the Qwen2.5-Omni processor, applies its chat template with an end-of-text token, and L2-normalizes the final-token hidden state. These are provider examples rather than compatibility or performance guarantees. [^e5-omni-7b-card]

## 3B checkpoint metadata

Metadata from a Hugging Face page capture of `Haon-Chen/e5-omni-3B` (Reported by the Hub, not independently checked): [^e5-omni-3b-hub-page]

| Field | Value |
|---|---|
| Parameters / tensor type | 4,703,464,448, all BF16; sharded safetensors, 9,407,206,896 bytes total (page header displays “5B params”) |
| Architecture class | `Qwen2_5OmniThinkerForConditionalGeneration` (`qwen2_5_omni_thinker`), so only the Thinker, not the full Qwen2.5-Omni model with speech output |
| Base model / license | `Qwen/Qwen2.5-Omni-3B` (tagged finetune); MIT |
| Library / pipeline tag | `sentence-transformers`; `visual-document-retrieval` |
| Repo dates | Created 2026-01-06; last modified 2026-04-24 |
| Popularity at capture | 467 downloads last month, 3,418 all time, 9 likes, 36 finetuned derivatives listed |

- The 4.703B count equals the [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md) count, consistent with both adapting the same Qwen2.5-Omni-3B Thinker (Synthesis). By the same inference the output width would be 2,048, but no e5-omni source states it (Unverified); the Transformers example only takes the L2-normalized final-token hidden state. [^e5-omni-3b-hub-page]
- The Transformers example prepends the Qwen2.5-Omni chat template, appends `<|endoftext|>`, uses left padding, passes `use_audio_in_video=True`, and prefixes text queries with `Query: `; the Sentence Transformers path uses `encode_query` instead. Both paths yield similar example scores (e.g. video 0.5881/0.5454 vs 0.5898/0.5430; text 0.7248/0.6511 vs 0.7266/0.6523), differing slightly from bfloat16 precision effects (Synthesis). These are single-pair illustrations, not benchmarks. [^e5-omni-3b-hub-page]
- The page's benchmark figures (MMEB-V2, AudioCaps) are images that were not inspected; the numbers in the table below come from the report. [^e5-omni-3b-hub-page]

## Reported evaluation

Results below are author-reported, not independently reproduced. MMEB-V2 comprises 78 image, video, and visual-document tasks; its reported group metrics mix Hit@1 for image/video with NDCG@5 for visual documents. AudioCaps uses text-to-audio Recall@1. [^e5-omni-report]

| Model | MMEB-V2 Image | Video | VisDoc | All | AudioCaps Recall@1 |
|---|---:|---:|---:|---:|---:|
| e5-omni 3B | 67.6 | 40.6 | 73.2 | 63.1 | 34.3 |
| e5-omni 7B | 71.2 | 43.5 | 76.1 | 66.4 | 37.7 |

For the 7B variant, removing temperature calibration, the curriculum, DCL, or whitening plus CORAL reduced both reported MMEB-V2 and AudioCaps results. The report also applies the full recipe to Qwen2.5-VL 3B (61.5 to 62.9 MMEB-V2), Qwen2-VL 2B (59.2 to 60.5), and LLaVA-OV 7B (63.7 to 65.4). [^e5-omni-report]

The local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) separately lists e5-omni-7B at reported rank 10 (Overall 46.53, Overall-V3 31.56, Text 24.65, Audio 43.04, Agent 36.67) and e5-omni-3B at rank 11 (44.03, 30.29, 24.38, 30.76, and 36.85 respectively). The snapshot has no metric definitions or evaluation provenance, so these values support only within-snapshot comparison. [^mmeb-v3-ranking]

## Limits

- The recipe targets retrieval similarity geometry and optimization dynamics, not higher-level reasoning or compositional understanding; the authors expect potentially smaller gains on tasks requiring multi-step inference. [^e5-omni-report]
- Whitening and covariance alignment depend on mini-batch statistics, which the report says can be noisy for small or modality-imbalanced batches despite group-wise computation and jitter. [^e5-omni-report]
- The reported evaluation covers MMEB-V2 and AudioCaps; broader audio/video domains, long-horizon retrieval, and real-world multimodal corpora remain unevaluated in the supplied report. [^e5-omni-report]

## Relationships

- **Sibling on the same base:** [AuroLA-Omni-3B](aurola-omni-3b.md), another Qwen2.5-Omni-3B Thinker embedding checkpoint with a similar Sentence Transformers interface.
- **Evaluated in:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md), which contains reported 3B and 7B entries. [^mmeb-v3-ranking]

[^e5-omni-report]: [e5-omni technical-report LaTeX source](../raw/2601.03666_e5-omni/acl.tex). This ingest covered its included sections, bibliography, and figure captions; PDFs in `figures/` were not visually rendered because the captions carried the claims compiled here. Model architecture, training, and evaluation results are author-reported.
[^e5-omni-3b-card]: [Haon-Chen/e5-omni-3B model card](../raw/e5-omni-3B.md). The local card was fully read; its externally hosted media, paper, package documentation, and repository artifacts were not independently inspected. License, availability, API, implementation, and example-retrieval claims are provider-reported.
[^e5-omni-3b-hub-page]: [Haon-Chen/e5-omni-3B Hugging Face page capture](../raw/Haon-Chen-e5-omni-3B.md). The 192 KB HTML capture (page text, embedded model metadata JSON) was inspected statically: the card prose duplicates the local 3B card, while the metadata block (safetensors counts, tags, dates, download counts, config class) is new. Asset images, the chat-template JSON, site chrome, and scripts were excluded as decorative or non-informative. Capture date is not recorded in the file (file timestamp 2026-10-22); popularity figures are time-sensitive.
[^e5-omni-7b-card]: [Haon-Chen/e5-omni-7B model card](../raw/e5-omni-7B.md). The local card was fully read; its externally hosted benchmark images, paper, package documentation, and example media were not independently inspected. License, availability, API, implementation, and example-retrieval claims are provider-reported.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv), as compiled in the [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md). This local artifact is unauthenticated and omits metric definitions and evaluation protocol.
