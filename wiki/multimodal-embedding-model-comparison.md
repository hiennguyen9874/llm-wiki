---
type: Synthesis
title: Multimodal embedding model comparison
description: A scope-aware comparison of the wiki's 26 documented multimodal embedding checkpoints and the limited 89-entry MMEB v3 ranking snapshot.
tags: [embedding, multimodal, retrieval, comparison, synthesis]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-10-22T04:00:00Z }
sources:
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
  - id: jina-v5-omni-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    title: "jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers"
  - id: wemm-readme
    resource: ../raw/WeMM-Embedding/README.md
    kind: model-card
    title: WeMM-Embedding repository README
  - id: nemotron-3-5-embed-1b-card
    resource: ../raw/Nemotron-3.5-Embed-1B-BF16.md
    kind: model-card
    title: Nemotron-3.5-Embed-1B-BF16 model card
  - id: embeddinggemma-2-card
    resource: ../raw/embeddinggemma-2.md
    kind: model-card
    title: EmbeddingGemma 2 model card
---

# Multimodal embedding model comparison

The wiki documents 26 concrete multimodal-embedding checkpoints in 17 model lines (the latest additions are [WeMM-Embedding](wemm-embedding.md), [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md), and [EmbeddingGemma 2](embeddinggemma-2.md)). They are not one substitutable class: dense bi-encoders optimize low-cost ANN; late-interaction models optimize visual-document recall at much larger indexes; omni models add audio and/or video. A supplied [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) names 89 entries, but only 13 have nonzero v3 modality columns and its protocol is unspecified. Thus it can rank those reported values, not establish a universal leaderboard.[^mmeb-v3-ranking]

## Selection by workload

| Workload | Prefer | Why / qualification |
|---|---|---|
| Broad image, video, visual-document retrieval | [WeMM-Embedding](wemm-embedding.md) 9B/4B/2B, or [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) | WeMM reports MMEB-v2 All 80.6 / 79.2 / 77.9, above Qwen 8B's 77.9 (Qwen's own table; its 2B sibling is 73.4). Both are author-reported on the same 78-task benchmark but not independently reproduced; WeMM lists only Chinese and English and has no audio input, while Qwen claims 30+ languages.[^wemm-readme] |
| Text, image, audio, video in one index | [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [e5-omni](e5-omni.md), [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), or [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) | Tianmu/e5/Omni have reported audio results; Jina has the smallest published omni variants and removable unused towers. Tianmu's released package additionally requires two base models. |
| Compact multilingual text-query → page-image/text retrieval with one dense vector | [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | 1.55B, 2,048D; vendor-run ViDoRe V3 image NDCG@10 58.02 vs 52.89 (Qwen3-VL-2B) and 58.29 (Qwen3-VL-8B); image retrieval evaluated in 18 languages. Text queries only; no video or audio.[^nemotron-3-5-embed-1b-card] |
| On-device single index over text, code, image, video, audio | [EmbeddingGemma 2](embeddinggemma-2.md) | 740M, 768D Matryoshka, removable encoders (270M text-only to 740M full). Smallest omni option, but reported MMEB v2 overall is only 59.01 and the card gives aggregates without protocol.[^embeddinggemma-2-card] |
| Visual-document (page image/PDF) retrieval where recall outweighs index cost | late-interaction models below | Token-vector MaxSim preserves page-region matches, unlike one-vector ANN. It increases storage and scoring cost. |
| High ViDoRe V3 score in the reported tables | [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md), [EVIE-Preview-4.5B](evie-preview-4-5b.md), [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) | They respectively report 64.95 final mean, 65.36 public (at 1,792 visual tokens), and 63.54. These are different captures/configurations, so this is not a strict three-way ranking. |
| Compact Vietnamese visual/text retrieval | [Vintern-Embedding-1B](vintern-embedding-1b.md) | Only documented model explicitly listing Vietnamese; it is multi-vector but omits output width and deployment limits. |
| Dense + lexical sparse retrieval from one model | [UEmbed](uembed.md) | 2B/4B/9B models emit dense and SPLADE-style sparse vectors in one causal pass. Training is English/Chinese-heavy and sparse cross-lingual activation is limited. |

## Text–image models at or below 2B

This subset treats “2B” as the checkpoint's published model class; Jina Nano/Small exact counts differ between their cards and the leaderboard (1.04B/1.74B versus 0.986B/1.626B). All eight can be used for text↔image/visual-document retrieval, but they do not report one common image-only benchmark. WeMM-2B, Nemotron-3.5-Embed-1B, and EmbeddingGemma 2 were added in October 2026.

| Model | Retrieval representation | Evidence for text–image work | Reported result | Best fit / caveat |
|---|---|---|---|---|
| [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) | one dense cosine vector; 64–2,048D Matryoshka | text, images, screenshots, mixed input; 30+ language claim | MMEB-v2: 75.0 Image, 79.2 VisDoc, 73.2 All | **Default choice**: the strongest documented broad multimodal evidence in this size band. Supports instructions, quantization, and 32K context; training disclosure is incomplete. |
| [WeMM-Embedding-2B](wemm-embedding.md) | one dense vector (dedicated `<embedding>` token); 64–2,048D Matryoshka | text, image, video, visual document, interleaved input; Chinese and English listed | MMEB-v2: 79.6 Image, 80.7 VisDoc, 77.9 All; 4.7 above Qwen3-VL-Embedding-2B in the report's table | Strongest reported MMEB-v2 score at this size. Same benchmark as Qwen, so directly comparable but author-reported; no audio; language coverage narrower than Qwen's. [^wemm-readme] |
| [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | one mean-pooled 2,048D vector, end-truncatable | text queries; image, text, or image+text documents; 18 image-retrieval languages | Vendor-run NDCG@10: ViDoRe V3 image 58.02, text 57.80, image+text 58.82; MIRACL-VISION image 68.93 | Choose for multilingual document-page retrieval at ~1.5B with 32K context. Beats Qwen3-VL-2B in every column of its table; not on MMEB, so not comparable with WeMM/Qwen MMEB scores. [^nemotron-3-5-embed-1b-card] |
| [EmbeddingGemma 2](embeddinggemma-2.md) | one mean-pooled 768D vector; MRL to 512/256/128 | text, code, image, video, audio; 8,192-token shared budget | MMEB v2: 57.28 Image, 67.84 VisDoc, 50.67 Video; MIEB lite 64.64 | Choose for the smallest footprint or audio coverage; expect lower image/video quality than Qwen-2B (MMEB-v2 All 73.2–73.4) and WeMM-2B. Do not use float16. [^embeddinggemma-2-card] |
| [UEmbed 2B](uembed.md) | dense EOS vector and learned sparse lexical vector; optional hybrid | text, images, visual documents | MMEB-v2 All: 66.5 dense / 65.5 sparse; its report finds only a small 2B hybrid gain on text/VisDoc and essentially none on image/video | Choose when one serving pass must feed both ANN and inverted sparse search. Image-specific score and output width are not reported; training is English/Chinese-heavy. |
| [Jina Embeddings v5 Omni Nano](jina-embeddings-v5-omni-nano.md) | 768D dense, truncatable, task adapters | text and image in a text-aligned shared space; image tower can be loaded while unused towers are omitted | Author report: MIEB Image 47.87; MIEB document-retrieval slice 79.25 at a 0.31B text+image path | Choose for the smallest documented dense deployment and adapter selection. This MIEB evidence is not directly comparable with Qwen's MMEB-v2 values. [^jina-v5-omni-report] |
| [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) | 1,024D dense, truncatable to 32–768D; task adapters | text and image in the same text-aligned space; unused towers can be omitted | Author report: MIEB Image 58.00; MIEB document-retrieval slice 79.25 at a 0.92B text+image path | Choose over Nano when 32K rather than 8K text context, 1,024D output, and stronger reported image score justify the larger footprint. This MIEB evidence is not directly comparable with Qwen's MMEB-v2 values. [^jina-v5-omni-report] |
| [Vintern-Embedding-1B](vintern-embedding-1b.md) | multi-vector; scoring mechanism and width undisclosed | text-query against image or text document; explicitly lists Vietnamese, English, Chinese | ViDoRe average 82.85 in its card's table, but protocol/metric configuration is not documented | Choose for Vietnamese-first retrieval. It is not directly comparable to Qwen's MMEB-v2 score and has the least deployment detail. |

**Recommendation (updated 2026-10-22):** for MMEB-style image/video/visual-document work, [WeMM-Embedding-2B](wemm-embedding.md) now has the highest reported score in this band (77.9 vs Qwen 2B's 73.2–73.4), but Qwen 2B stays the safer choice when 30+ language coverage matters. For multilingual document-page retrieval with text queries, evaluate [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md). Choose [EmbeddingGemma 2](embeddinggemma-2.md) only when size or audio/video in one tiny index outweighs quality. Otherwise use Qwen 2B unless Vietnamese is primary (evaluate Vintern) or hybrid dense+sparse indexing is a hard requirement (evaluate UEmbed 2B). Choose Jina Omni Small over Nano when 32K context and adapters matter; choose Nano for the smaller footprint. The Jina report supplies MIEB evidence but not a common benchmark with Qwen, so validate both on the target corpus. [^jina-v5-omni-report]

## Architecture and modality matrix

| Model line (concrete variants) | Reported modalities | Retrieval form | Size / output |
|---|---|---|---|
| [Qwen3-VL Embedding](qwen3-vl-embedding-8b.md) (2B, 8B) | text, image, screenshot, video, mixed input | dense cosine bi-encoder | 2B: 64–2,048D; 8B: 64–4,096D Matryoshka |
| [WeMM-Embedding](wemm-embedding.md) (2B, 4B, 9B) | text, image, video, visual document, interleaved; no audio | dense, dedicated-token pooling | 2,048D / 2,560D / 4,096D Matryoshka |
| [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | text queries; text, image, image+text documents | dense mean-pooled bi-encoder | 1.55B; 2,048D |
| [EmbeddingGemma 2](embeddinggemma-2.md) | text, code, image, video, audio | dense mean-pooled | 740M; 768D Matryoshka |
| [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) | text, image, video, visual document, audio, agent | dense | 8B-scale assembled system; 3,584D |
| [e5-omni](e5-omni.md) (3B, 7B) | text, image, audio, video | dense contrastive bi-encoder | dimensionality not disclosed |
| [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md) | text, image, audio, video, mixed input | dense contrastive bi-encoder | 4.703B actual reported; 2,048D |
| [Jina v5 Omni](jina-embeddings-v5-omni-small.md) (Nano, Small) | text, image, video, audio, fused input | dense, task adapters | 1.04B/768D; 1.74B/1,024D |
| [Jina Embeddings v4](jina-embeddings-v4.md) | text, image, visual document | dense or late interaction | Qwen2.5-VL-3B base; 2,048D dense / 128D token |
| [UEmbed](uembed.md) (2B, 4B, 9B) | text, image, video, visual document | dense, sparse, or hybrid | output width not disclosed |
| [Vintern-Embedding-1B](vintern-embedding-1b.md) | text, visual input | multi-vector | ~0.9B; output width not disclosed |
| [Tomoro ColQwen3](tomoro-colqwen3-embed-8b.md) (4B, 8B) | text, page image, short video | 320D-token MaxSim | 4B-/8B-class |
| [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md) | text, document image | 320D-token MaxSim | 4.5B |
| [EVIE-Preview-4.5B](evie-preview-4-5b.md) | text, document image | 128D-token MaxSim | 4.54B |
| [Llama-Nemotron-ColEmbed-VL-3B-v2](llama-nemotron-colembed-vl-3b-v2.md) | text, page image | 3,072D-token MaxSim | ~4.4B actual reported |
| [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) | text, page image | 4,096D-token MaxSim | ~8.8B actual reported |
| [webAI-ColVec1.1](webai-colvec1-1-8b.md) (4B, 8B) | text, document image/PDF page | 640D-token MaxSim | 4.54B / 8.40B |

## Comparable reported results

Scores only compare *within the named benchmark, version, metric, and supplied table*.

| Evaluation | Reported leading documented model | Other material comparisons |
|---|---|---|
| MMEB-v2, 78 tasks | WeMM 9B: 80.6 All (author report; its leaderboard-first claim is dated 2026-08-24) | WeMM 4B: 79.2; WeMM 2B: 77.9; Qwen3-VL Embedding 8B: 77.9; Qwen 2B: 73.4; UEmbed 9B dense: 71.8; e5-omni 7B: 66.4; EmbeddingGemma 2: 59.01 (its own card, protocol unstated). Metrics mix image/video Hit@1 and visual-document nDCG@5. [^wemm-readme][^embeddinggemma-2-card] |
| MMEB-v3 V3-All, 190 tasks (WeMM card; not in the snapshot) | WeMM 9B: 59.5 | WeMM 4B: 58.2; WeMM 2B: 56.0; Tianmu: 53.27 in its own card. Unsupported tasks score zero, so WeMM's audio is 0.0. Do not merge with the snapshot's Overall column. [^wemm-readme] |
| ViDoRe V3 + MIRACL-VISION, NDCG@10 (Nemotron card; vendor-run) | Nemotron-3.5-Embed-1B: image 58.02 / 68.93 | Qwen3-VL-2B: 52.89 / 58.42; Qwen3-VL-8B: 58.29 / 68.33; the card's 8B teacher: 60.39 / 72.64. Different protocol from the late-interaction ViDoRe V3 row below. [^nemotron-3-5-embed-1b-card] |
| MMEB v3 snapshot, Overall | Tianmu: 52.83 | UEmbed 9B hybrid: 51.54; UEmbed 4B dense: 50.10; e5-omni 7B: 46.53; Omni-Embed: 42.83. |
| MMEB v3 snapshot, Audio | e5-omni 7B: 43.04 among documented entries | Tianmu: 38.94; Omni-Embed: 36.52. Ovis (not documented as a concept) reports 47.82. |
| ViDoRe V3 reported tables | webAI 8B: 64.95 final mean | EVIE: 65.36 public at extrapolated visual budget; Nemotron 8B: 63.54; ColQwen3.5: 61.46 Mean (Task); Tomoro 8B: 0.6113 nDCG@5, therefore not directly metric-comparable. |
| MTEB Multilingual v2 (text-only slice) | Jina v5 Omni Small: 67.00 Mean (Task) | Omni Nano: 65.52. Both equal their paired text-model snapshot values, so independent omni evaluation is not established. |

## MMEB v3 snapshot coverage and limits

The raw CSV ranks 89 entries by reported `Overall`; it does not include WeMM, Nemotron-3.5-Embed-1B, or EmbeddingGemma 2. 13 provide nonzero `Overall-V3`, Text, Audio, and Agent values. The remaining 76 entries include Qwen3-VL-Embedding (ranks 18 and 24), Jina v5 Omni Small/Nano (87/88), and many models not otherwise documented in this wiki. Their zero-filled v3 fields may mean missing evaluation rather than failure. The only defensible exhaustive comparison of all 89 is the [snapshot](mmeb-v3-ranking-snapshot.md) itself; it lacks metric definitions, task composition, capture date, inclusion rules, and evaluation configuration.[^mmeb-v3-ranking]

## Decision constraints

- **Do not compare dense-vector dimensions to token-vector dimensions as index footprint.** Late-interaction footprint also scales with retained tokens/page or frame.
- **Use a reranker after first-stage retrieval** when latency allows. Qwen's multimodal rerankers are cross-encoders, not embeddings, and are intentionally excluded from this comparison.
- **Language claims are uneven.** Qwen claims 30+ languages; WeMM lists Chinese and English; Nemotron-3.5-Embed-1B evaluated image retrieval in 18 languages; EVIE explicitly lists seven query languages; Vintern explicitly lists Vietnamese, English, and Chinese. Many other cards merely say multilingual.
- Most scores are provider-reported; neither the raw snapshot nor the model cards provide a common independently reproduced evaluation.

## Relationships

- **Uses benchmark:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md).
- **Compares:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md), [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [UEmbed](uembed.md), and the model lines linked above.
- **Uses method:** [GELATO](gelato.md) for the Jina v5 Omni variants. [^jina-v5-omni-report]
- **Added 2026-10-22:** [WeMM-Embedding](wemm-embedding.md), [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md), [EmbeddingGemma 2](embeddinggemma-2.md). Their scores are author-reported (Reported) and cross-table comparisons above are Synthesis.

[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This supplied, unauthenticated artifact supports only its reported values; it does not define benchmark semantics or explain zero-filled fields.
[^jina-v5-omni-report]: [jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers](../raw/2605.08384_jina-embeddings-v5-omni/main.tex). Author technical report; its architecture and benchmark claims were not independently reproduced.
[^wemm-readme]: [WeMM-Embedding repository README](../raw/WeMM-Embedding/README.md), Model Zoo and MMEB-v2/MMEB-v3 tables (spot-checked against the 2B card's MMEB-v2 table). Author-reported; the technical report and other cards are covered in [WeMM-Embedding](wemm-embedding.md).
[^nemotron-3-5-embed-1b-card]: [Nemotron-3.5-Embed-1B-BF16 model card](../raw/Nemotron-3.5-Embed-1B-BF16.md), Evaluation Dataset table (ViDoRe V3, MIRACL-VISION). Vendor-run; not independently reproduced.
[^embeddinggemma-2-card]: [EmbeddingGemma 2 model card](../raw/embeddinggemma-2.md), Benchmark Results and Matryoshka truncation tables. Vendor-reported aggregates; no protocol given.
