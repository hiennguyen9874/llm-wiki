---
type: Synthesis
title: Multimodal embedding model comparison
description: A scope-aware comparison of the wiki's 21 documented multimodal embedding checkpoints and the limited 89-entry MMEB v3 ranking snapshot.
tags: [embedding, multimodal, retrieval, comparison, synthesis]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T20:04:02+07:00 }
sources:
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
  - id: jina-v5-omni-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    title: jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers
---

# Multimodal embedding model comparison

The wiki documents 21 concrete multimodal-embedding checkpoints in 14 model lines. They are not one substitutable class: dense bi-encoders optimize low-cost ANN; late-interaction models optimize visual-document recall at much larger indexes; omni models add audio and/or video. A supplied [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) names 89 entries, but only 13 have nonzero v3 modality columns and its protocol is unspecified. Thus it can rank those reported values, not establish a universal leaderboard.[^mmeb-v3-ranking]

## Selection by workload

| Workload | Prefer | Why / qualification |
|---|---|---|
| Broad image, video, visual-document retrieval | [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) | Dense, instruction-aware model; author-reported MMEB-v2 All 77.9, highest in its supplied table. Its 2B sibling is the lower-cost alternative (73.4). |
| Text, image, audio, video in one index | [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [e5-omni](e5-omni.md), [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), or [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) | Tianmu/e5/Omni have reported audio results; Jina has the smallest published omni variants and removable unused towers. Tianmu's released package additionally requires two base models. |
| Visual-document (page image/PDF) retrieval where recall outweighs index cost | late-interaction models below | Token-vector MaxSim preserves page-region matches, unlike one-vector ANN. It increases storage and scoring cost. |
| High ViDoRe V3 score in the reported tables | [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md), [EVIE-Preview-4.5B](evie-preview-4-5b.md), [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) | They respectively report 64.95 final mean, 65.36 public (at 1,792 visual tokens), and 63.54. These are different captures/configurations, so this is not a strict three-way ranking. |
| Compact Vietnamese visual/text retrieval | [Vintern-Embedding-1B](vintern-embedding-1b.md) | Only documented model explicitly listing Vietnamese; it is multi-vector but omits output width and deployment limits. |
| Dense + lexical sparse retrieval from one model | [UEmbed](uembed.md) | 2B/4B/9B models emit dense and SPLADE-style sparse vectors in one causal pass. Training is English/Chinese-heavy and sparse cross-lingual activation is limited. |

## Text–image models at or below 2B

This subset treats “2B” as the checkpoint's published model class; Jina Nano/Small exact counts differ between their cards and the leaderboard (1.04B/1.74B versus 0.986B/1.626B). All five can be used for text↔image/visual-document retrieval, but they do not report one common image-only benchmark.

| Model | Retrieval representation | Evidence for text–image work | Reported result | Best fit / caveat |
|---|---|---|---|---|
| [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) | one dense cosine vector; 64–2,048D Matryoshka | text, images, screenshots, mixed input; 30+ language claim | MMEB-v2: 75.0 Image, 79.2 VisDoc, 73.2 All | **Default choice**: the strongest documented broad multimodal evidence in this size band. Supports instructions, quantization, and 32K context; training disclosure is incomplete. |
| [UEmbed 2B](uembed.md) | dense EOS vector and learned sparse lexical vector; optional hybrid | text, images, visual documents | MMEB-v2 All: 66.5 dense / 65.5 sparse; its report finds only a small 2B hybrid gain on text/VisDoc and essentially none on image/video | Choose when one serving pass must feed both ANN and inverted sparse search. Image-specific score and output width are not reported; training is English/Chinese-heavy. |
| [Jina Embeddings v5 Omni Nano](jina-embeddings-v5-omni-nano.md) | 768D dense, truncatable, task adapters | text and image in a text-aligned shared space; image tower can be loaded while unused towers are omitted | Author report: MIEB Image 47.87; MIEB document-retrieval slice 79.25 at a 0.31B text+image path | Choose for the smallest documented dense deployment and adapter selection. This MIEB evidence is not directly comparable with Qwen's MMEB-v2 values. [^jina-v5-omni-report] |
| [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) | 1,024D dense, truncatable to 32–768D; task adapters | text and image in the same text-aligned space; unused towers can be omitted | Author report: MIEB Image 58.00; MIEB document-retrieval slice 79.25 at a 0.92B text+image path | Choose over Nano when 32K rather than 8K text context, 1,024D output, and stronger reported image score justify the larger footprint. This MIEB evidence is not directly comparable with Qwen's MMEB-v2 values. [^jina-v5-omni-report] |
| [Vintern-Embedding-1B](vintern-embedding-1b.md) | multi-vector; scoring mechanism and width undisclosed | text-query against image or text document; explicitly lists Vietnamese, English, Chinese | ViDoRe average 82.85 in its card's table, but protocol/metric configuration is not documented | Choose for Vietnamese-first retrieval. It is not directly comparable to Qwen's MMEB-v2 score and has the least deployment detail. |

**Recommendation:** use Qwen 2B unless Vietnamese is primary (evaluate Vintern) or hybrid dense+sparse indexing is a hard requirement (evaluate UEmbed 2B). Choose Jina Omni Small over Nano when 32K context and adapters matter; choose Nano for the smaller footprint. The Jina report supplies MIEB evidence but not a common benchmark with Qwen, so validate both on the target corpus. [^jina-v5-omni-report]

## Architecture and modality matrix

| Model line (concrete variants) | Reported modalities | Retrieval form | Size / output |
|---|---|---|---|
| [Qwen3-VL Embedding](qwen3-vl-embedding-8b.md) (2B, 8B) | text, image, screenshot, video, mixed input | dense cosine bi-encoder | 2B: 64–2,048D; 8B: 64–4,096D Matryoshka |
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
| MMEB-v2, 78 tasks | Qwen3-VL Embedding 8B: 77.9 All | Qwen 2B: 73.4; UEmbed 9B dense: 71.8; e5-omni 7B: 66.4. Metrics mix image/video Hit@1 and visual-document nDCG@5. |
| MMEB v3 snapshot, Overall | Tianmu: 52.83 | UEmbed 9B hybrid: 51.54; UEmbed 4B dense: 50.10; e5-omni 7B: 46.53; Omni-Embed: 42.83. |
| MMEB v3 snapshot, Audio | e5-omni 7B: 43.04 among documented entries | Tianmu: 38.94; Omni-Embed: 36.52. Ovis (not documented as a concept) reports 47.82. |
| ViDoRe V3 reported tables | webAI 8B: 64.95 final mean | EVIE: 65.36 public at extrapolated visual budget; Nemotron 8B: 63.54; ColQwen3.5: 61.46 Mean (Task); Tomoro 8B: 0.6113 nDCG@5, therefore not directly metric-comparable. |
| MTEB Multilingual v2 (text-only slice) | Jina v5 Omni Small: 67.00 Mean (Task) | Omni Nano: 65.52. Both equal their paired text-model snapshot values, so independent omni evaluation is not established. |

## MMEB v3 snapshot coverage and limits

The raw CSV ranks 89 entries by reported `Overall`; 13 provide nonzero `Overall-V3`, Text, Audio, and Agent values. The remaining 76 entries include Qwen3-VL-Embedding (ranks 18 and 24), Jina v5 Omni Small/Nano (87/88), and many models not otherwise documented in this wiki. Their zero-filled v3 fields may mean missing evaluation rather than failure. The only defensible exhaustive comparison of all 89 is the [snapshot](mmeb-v3-ranking-snapshot.md) itself; it lacks metric definitions, task composition, capture date, inclusion rules, and evaluation configuration.[^mmeb-v3-ranking]

## Decision constraints

- **Do not compare dense-vector dimensions to token-vector dimensions as index footprint.** Late-interaction footprint also scales with retained tokens/page or frame.
- **Use a reranker after first-stage retrieval** when latency allows. Qwen's multimodal rerankers are cross-encoders, not embeddings, and are intentionally excluded from this comparison.
- **Language claims are uneven.** Qwen claims 30+ languages; EVIE explicitly lists seven query languages; Vintern explicitly lists Vietnamese, English, and Chinese. Many other cards merely say multilingual.
- Most scores are provider-reported; neither the raw snapshot nor the model cards provide a common independently reproduced evaluation.

## Relationships

- **Uses benchmark:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md).
- **Compares:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md), [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [UEmbed](uembed.md), and the model lines linked above.
- **Uses method:** [GELATO](gelato.md) for the Jina v5 Omni variants. [^jina-v5-omni-report]

[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This supplied, unauthenticated artifact supports only its reported values; it does not define benchmark semantics or explain zero-filled fields.
[^jina-v5-omni-report]: [jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers](../raw/2605.08384_jina-embeddings-v5-omni/main.tex). Author technical report; its architecture and benchmark claims were not independently reproduced.
