---
type: Synthesis
title: Multimodal embedding model comparison
description: A scope-aware comparison of the wiki's 36 documented multimodal embedding checkpoints, including a filter by documented language coverage (>2 languages), and the limited 89-entry MMEB v3 ranking snapshot.
tags: [embedding, multimodal, retrieval, comparison, synthesis]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-10-23T00:00:00Z }
sources:
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
  - id: jina-v5-omni-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    title: "jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers"
  - id: ovis-omni-card
    resource: ../raw/ATH-MaaS-Ovis-Omni-Embedding-3B.md
    kind: model-card
    title: ATH-MaaS/Ovis-Omni-Embedding-3B model page
  - id: ovis-vl-card
    resource: ../raw/ATH-MaaS-Ovis-VL-Embedding-2B.md
    kind: model-card
    title: ATH-MaaS/Ovis-VL-Embedding-2B model page
  - id: auro-la-omni-3b-page
    resource: ../raw/Jazzcharles-AuroLA-Omni-3B.md
    kind: model-card
    title: Jazzcharles/AuroLA-Omni-3B Hugging Face page capture
  - id: sentio-card
    resource: ../raw/Dragos-Datcu-Sentio.md
    kind: model-card
    title: Dragos-Datcu/Sentio model page
  - id: wianmu-3b-page
    resource: ../raw/eduardo-terres2-Wianmu-3B.md
    kind: model-card
    title: eduardo-terres2/Wianmu-3B model page
  - id: wianmu-5b-page
    resource: ../raw/eduardo-terres2-Wianmu-5B.md
    kind: model-card
    title: eduardo-terres2/Wianmu-5B model page
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
  - id: geevec-page
    resource: ../raw/geevec-ai-geevec-embeddings-mm-1.0.md
    kind: model-card
    title: geevec-ai/geevec-embeddings-mm-1.0 model page
  - id: dna-vl-steer-2b-page
    resource: ../raw/dnotitia-DNA-VL-STEER-2B.md
    kind: model-card
    title: dnotitia/DNA-VL-STEER-2B model page
  - id: pplx-late-06b-page
    resource: ../raw/perplexity-ai-pplx-embed-v2-late-0.6b.md
    kind: web
    title: perplexity-ai/pplx-embed-v2-late-0.6b Hugging Face page capture
  - id: pplx-late-9b-page
    resource: ../raw/perplexity-ai-pplx-embed-v2-late-9b.md
    kind: web
    title: perplexity-ai/pplx-embed-v2-late-9b Hugging Face page capture
  - id: qwen3-vl-embedding-2b-card
    resource: ../raw/Qwen3-VL-Embedding-2B.md
    kind: model-card
    title: Qwen3-VL-Embedding-2B model card
  - id: qwen3-vl-embedding-8b-card
    resource: ../raw/Qwen3-VL-Embedding-8B.md
    kind: model-card
    title: Qwen3-VL-Embedding-8B model card
  - id: jina-v4-card
    resource: ../raw/jina-embeddings-v4.md
    kind: model-card
    title: Jina Embeddings v4 model card
  - id: evie-card
    resource: ../raw/EVIE-Preview-4.5B.md
    kind: model-card
    title: EVIE-Preview-4.5B model card
  - id: colqwen35v3-card
    resource: ../raw/ColQwen3.5-4.5B-v3.md
    kind: model-card
    title: ColQwen3.5-4.5B-v3 model card
  - id: vintern-embedding-1b-card
    resource: ../raw/Vintern-Embedding-1B.md
    kind: model-card
    title: Vintern-Embedding-1B model card
  - id: webai-colvec1-1-4b-card
    resource: ../raw/webAI-ColVec1.1-4b.md
    kind: model-card
    title: webAI-ColVec1.1-4b model card
  - id: webai-colvec1-1-8b-card
    resource: ../raw/webAI-ColVec1.1-8b.md
    kind: model-card
    title: webAI-ColVec1.1-8b model card
  - id: nemotron-colembed-vl-8b-v2-card
    resource: ../raw/nemotron-colembed-vl-8b-v2.md
    kind: model-card
    title: Nemotron ColEmbed VL 8B v2 model card
  - id: llama-nemotron-colembed-vl-3b-v2-card
    resource: ../raw/llama-nemotron-colembed-vl-3b-v2.md
    kind: model-card
    title: Llama-Nemotron-ColEmbed-VL-3B-v2 model card
  - id: tomoro-colqwen3-4b-card
    resource: ../raw/tomoro-colqwen3-embed-4b.md
    kind: model-card
    title: TomoroAI/tomoro-colqwen3-embed-4b model card
  - id: tomoro-colqwen3-8b-card
    resource: ../raw/tomoro-colqwen3-embed-8b.md
    kind: model-card
    title: TomoroAI/tomoro-colqwen3-embed-8b model card
  - id: jina-v5-omni-nano-card
    resource: ../raw/jina-embeddings-v5-omni-nano.md
    kind: model-card
    title: jina-embeddings-v5-omni-nano model card
  - id: jina-v5-omni-small-card
    resource: ../raw/jina-embeddings-v5-omni-small.md
    kind: model-card
    title: jina-embeddings-v5-omni-small model card
  - id: e5-omni-report
    resource: ../raw/2601.03666_e5-omni/acl.tex
    title: e5-omni technical-report LaTeX source
  - id: tianmu-emb-uni-8b-card
    resource: ../raw/Tianmu-Emb-Uni-8B.md
    kind: model-card
    title: Tianmu-Emb-Uni-8B model card
  - id: omni-embed-nemotron-3b-card
    resource: ../raw/omni-embed-nemotron-3b.md
    kind: model-card
    title: Omni-Embed-Nemotron-3B model card
  - id: uembed-tech-report
    resource: ../raw/2608.02583_UEmbed/main.tex
    title: UEmbed technical-report LaTeX source
---

# Multimodal embedding model comparison

The wiki documents 36 concrete multimodal-embedding checkpoints in 23 model lines (the latest additions are [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md), [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md), [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md), [Wianmu-5B](wianmu-5b.md), [Wianmu-3B](wianmu-3b.md), [DNA-VL-STEER-2B](dna-vl-steer-2b.md), [AuroLA-Omni-3B](aurola-omni-3b.md), [Sentio](sentio.md), [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md), [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), [WeMM-Embedding](wemm-embedding.md), [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md), and [EmbeddingGemma 2](embeddinggemma-2.md)). They are not one substitutable class: dense bi-encoders optimize low-cost ANN; late-interaction models optimize visual-document recall at much larger indexes; omni models add audio and/or video. A supplied [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) names 89 entries, but only 13 have nonzero v3 modality columns and its protocol is unspecified. Thus it can rank those reported values, not establish a universal leaderboard.[^mmeb-v3-ranking]

## Selection by workload

| Workload | Prefer | Why / qualification |
|---|---|---|
| Broad image, video, visual-document retrieval | [WeMM-Embedding](wemm-embedding.md) 9B/4B/2B, or [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) | WeMM reports MMEB-v2 All 80.6 / 79.2 / 77.9, above Qwen 8B's 77.9 (Qwen's own table; its 2B sibling is 73.4). Both are author-reported on the same 78-task benchmark but not independently reproduced; WeMM lists only Chinese and English and has no audio input, while Qwen claims 30+ languages.[^wemm-readme] |
| Image / visual-document retrieval at 9B scale with one 4,096D vector | [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md) or [WeMM-Embedding](wemm-embedding.md) 9B | On the 44 MMEB-v2 retrieval datasets GeeVec reports the top Image (81.82) and VisDoc (83.63) scores in its table but 59.66 Video vs WeMM-9B's 64.03 (AVG 78.78 vs 79.38). Card-only, no paper or training details; loading needs a custom `modeling` module.[^geevec-page] |
| Text, image, audio, video in one index | [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [e5-omni](e5-omni.md), [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), or [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) | Ovis (3B, 2,048D) self-reports the highest MMEB-v3 overall (58.46) of any documented omni model, though not reproduced and not on the snapshot's scale;[^ovis-omni-card] Tianmu/e5/Omni have reported audio results; Jina has the smallest published omni variants and removable unused towers. Tianmu's released package additionally requires two base models. |
| Highest reported MMEB-V3 overall with audio added to a WeMM-9B index | [Sentio](sentio.md) | 10.20B composite (WeMM-9B + Qwen2.5-Omni audio tower); 61.69 overall on the card's 190-task snapshot vs 59.33 for WeMM-9B, but its Audio score (36.81) trails [Wianmu-5B](wianmu-5b.md) (42.93). Author-reported; trained adapter weights are not distributed in the repo, and the audio tower carries the Qwen Research License.[^sentio-card] |
| Compact multilingual text-query → page-image/text retrieval with one dense vector | [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | 1.55B, 2,048D; vendor-run ViDoRe V3 image NDCG@10 58.02 vs 52.89 (Qwen3-VL-2B) and 58.29 (Qwen3-VL-8B); image retrieval evaluated in 18 languages. Text queries only; no video or audio.[^nemotron-3-5-embed-1b-card] |
| On-device single index over text, code, image, video, audio | [EmbeddingGemma 2](embeddinggemma-2.md) | 740M, 768D Matryoshka, removable encoders (270M text-only to 740M full). Smallest omni option, but reported MMEB v2 overall is only 59.01 and the card gives aggregates without protocol.[^embeddinggemma-2-card] |
| Multilingual image/video retrieval incl. low-resource languages (e.g. Korean) on a Qwen3-VL-2B stack | [DNA-VL-STEER-2B](dna-vl-steer-2b.md) | Drop-in calibrated variant of Qwen3-VL-Embedding-2B: XM3600 mean image→text R@1 59.8 → 70.3 (LRL-5 32.8 → 51.8) over 36 languages. Reports regressions on abstract text retrieval (−7.9 R@1), video action classification (−4 to −9), and fine-grained visual tasks; use the frozen base for English/text-only work. Author-reported; no MMEB score.[^dna-vl-steer-2b-page] |
| Visual-document (page image/PDF) retrieval where recall outweighs index cost | late-interaction models below | Token-vector MaxSim preserves page-region matches, unlike one-vector ANN. It increases storage and scoring cost. |
| High ViDoRe V3 score in the reported tables | [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md), [EVIE-Preview-4.5B](evie-preview-4-5b.md), [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) | They respectively report 64.95 final mean, 65.36 public (at 1,792 visual tokens), and 63.54. These are different captures/configurations, so this is not a strict three-way ranking. |
| Compact Vietnamese visual/text retrieval | [Vintern-Embedding-1B](vintern-embedding-1b.md) | Only documented model explicitly listing Vietnamese; it is multi-vector but omits output width and deployment limits. |
| Dense + lexical sparse retrieval from one model | [UEmbed](uembed.md) | 2B/4B/9B models emit dense and SPLADE-style sparse vectors in one causal pass. Training is English/Chinese-heavy and sparse cross-lingual activation is limited. |

## Text–image models at or below 2B

This subset treats “2B” as the checkpoint's published model class; Jina Nano/Small exact counts differ between their cards and the leaderboard (1.04B/1.74B versus 0.986B/1.626B). All nine can be used for text↔image/visual-document retrieval, but they do not report one common image-only benchmark. WeMM-2B, Nemotron-3.5-Embed-1B, and EmbeddingGemma 2 were added in October 2026.

| Model | Retrieval representation | Evidence for text–image work | Reported result | Best fit / caveat |
|---|---|---|---|---|
| [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) | one dense cosine vector; 64–2,048D Matryoshka | text, images, screenshots, mixed input; 30+ language claim | MMEB-v2: 75.0 Image, 79.2 VisDoc, 73.2 All | **Default choice**: the strongest documented broad multimodal evidence in this size band. Supports instructions, quantization, and 32K context; training disclosure is incomplete. |
| [WeMM-Embedding-2B](wemm-embedding.md) | one dense vector (dedicated `<embedding>` token); 64–2,048D Matryoshka | text, image, video, visual document, interleaved input; Chinese and English listed | MMEB-v2: 79.6 Image, 80.7 VisDoc, 77.9 All; 4.7 above Qwen3-VL-Embedding-2B in the report's table | Strongest reported MMEB-v2 score at this size. Same benchmark as Qwen, so directly comparable but author-reported; no audio; language coverage narrower than Qwen's. [^wemm-readme] |
| [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | one mean-pooled 2,048D vector, end-truncatable | text queries; image, text, or image+text documents; 18 image-retrieval languages | Vendor-run NDCG@10: ViDoRe V3 image 58.02, text 57.80, image+text 58.82; MIRACL-VISION image 68.93 | Choose for multilingual document-page retrieval at ~1.5B with 32K context. Beats Qwen3-VL-2B in every column of its table; not on MMEB, so not comparable with WeMM/Qwen MMEB scores. [^nemotron-3-5-embed-1b-card] |
| [EmbeddingGemma 2](embeddinggemma-2.md) | one mean-pooled 768D vector; MRL to 512/256/128 | text, code, image, video, audio; 8,192-token shared budget | MMEB v2: 57.28 Image, 67.84 VisDoc, 50.67 Video; MIEB lite 64.64 | Choose for the smallest footprint or audio coverage; expect lower image/video quality than Qwen-2B (MMEB-v2 All 73.2–73.4) and WeMM-2B. Do not use float16. [^embeddinggemma-2-card] |
| [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md) | one dense last-token vector; native 2,048D, no reduced widths documented | text, image, visual document, video, interleaved; no audio; language coverage unstated | MMEB-v2: 80.62 Image, 80.47 VisDoc, 67.12 Video, 77.46 All | Near WeMM-2B (77.9) and well above Qwen 2B (73.2–73.4) on the same benchmark, but about 0.4 below WeMM-2B; the card's baselines are unnamed and all values are author-reported. Choose to evaluate alongside WeMM-2B for image/document-heavy work; Video is its weakest group. [^ovis-vl-card] |
| [UEmbed 2B](uembed-2b.md) | dense EOS vector and learned sparse lexical vector; optional hybrid | text, images, visual documents | MMEB-v2 All: 66.5 dense / 65.5 sparse; its report finds only a small 2B hybrid gain on text/VisDoc and essentially none on image/video | Choose when one serving pass must feed both ANN and inverted sparse search. Image-specific score and output width are not reported; training is English/Chinese-heavy. |
| [Jina Embeddings v5 Omni Nano](jina-embeddings-v5-omni-nano.md) | 768D dense, truncatable, task adapters | text and image in a text-aligned shared space; image tower can be loaded while unused towers are omitted | Author report: MIEB Image 47.87; MIEB document-retrieval slice 79.25 at a 0.31B text+image path | Choose for the smallest documented dense deployment and adapter selection. This MIEB evidence is not directly comparable with Qwen's MMEB-v2 values. [^jina-v5-omni-report] |
| [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) | 1,024D dense, truncatable to 32–768D; task adapters | text and image in the same text-aligned space; unused towers can be omitted | Author report: MIEB Image 58.00; MIEB document-retrieval slice 79.25 at a 0.92B text+image path | Choose over Nano when 32K rather than 8K text context, 1,024D output, and stronger reported image score justify the larger footprint. This MIEB evidence is not directly comparable with Qwen's MMEB-v2 values. [^jina-v5-omni-report] |
| [Vintern-Embedding-1B](vintern-embedding-1b.md) | multi-vector; scoring mechanism and width undisclosed | text-query against image or text document; explicitly lists Vietnamese, English, Chinese | ViDoRe average 82.85 in its card's table, but protocol/metric configuration is not documented | Choose for Vietnamese-first retrieval. It is not directly comparable to Qwen's MMEB-v2 score and has the least deployment detail. |

**Recommendation (updated 2026-10-22):** for MMEB-style image/video/visual-document work, [WeMM-Embedding-2B](wemm-embedding.md) has the highest reported score in this band (77.9 vs Qwen 2B's 73.2–73.4), with [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md) a close second (77.46; its Image score of 80.62 exceeds WeMM-2B's 79.6, while VisDoc 80.47 is slightly below 80.7; author-reported, so treat as a tie), but Qwen 2B stays the safer choice when 30+ language coverage matters. For multilingual document-page retrieval with text queries, evaluate [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md). Choose [EmbeddingGemma 2](embeddinggemma-2.md) only when size or audio/video in one tiny index outweighs quality. Otherwise use Qwen 2B unless Vietnamese is primary (evaluate Vintern) or hybrid dense+sparse indexing is a hard requirement (evaluate UEmbed 2B). Choose Jina Omni Small over Nano when 32K context and adapters matter; choose Nano for the smaller footprint. The Jina report supplies MIEB evidence but not a common benchmark with Qwen, so validate both on the target corpus. [^jina-v5-omni-report]

## Multilingual filter: image + text with more than two languages

Filtered on 2026-10-23 for models that embed images and text and document more than two languages. Tiers reflect how strong the language evidence is, not model quality. Scores are Reported (author/vendor); cross-benchmark comparisons are Synthesis. Being absent here means "not documented in the wiki", not "monolingual".

### Tier A — explicit language list or count

| Model | Documented languages | Form / size | Reported result |
|---|---|---|---|
| [EmbeddingGemma 2](embeddinggemma-2.md) | 100+ understood; 140+ in training text; no per-language parity claimed[^embeddinggemma-2-card] | dense, 740M, 768D; also video/audio | MMEB-v2 overall 59.01 |
| [DNA-VL-STEER-2B](dna-vl-steer-2b.md) | 36 calibrated XM3600 languages (incl. vi, ko, th, sw)[^dna-vl-steer-2b-page] | dense, 2.13B, 64–2,048D | XM3600 i→t R@1 59.8 → 70.3; LRL-5 32.8 → 51.8; regressions on text-only and fine-grained tasks |
| [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | text retrieval evaluated in 34 languages (incl. Vietnamese); image retrieval in 18[^nemotron-3-5-embed-1b-card] | dense, 1.55B, 2,048D; text queries only | ViDoRe V3 image 58.02; MIRACL-VISION 68.93 (NDCG@10, vendor-run) |
| [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) / [8B](qwen3-vl-embedding-8b.md) | 30+, not enumerated[^qwen3-vl-embedding-2b-card][^qwen3-vl-embedding-8b-card] | dense, up to 2,048D / 4,096D Matryoshka | MMEB-v2 All 73.2–73.4 / 77.9 |
| [Jina Embeddings v4](jina-embeddings-v4.md) | 30+, not enumerated[^jina-v4-card] | dense 2,048D or 128D-token late interaction | no scores on the card |
| [EVIE-Preview-4.5B](evie-preview-4-5b.md) | queries in EN, FR, DE, IT, ES, PT, ZH[^evie-card] | 128D-token MaxSim, 4.54B | ViDoRe V3 public 65.36 at 1,792 visual tokens |
| [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md) | EN, FR, DE, ES, ZH[^colqwen35v3-card] | 320D-token MaxSim, 4.5B | ViDoRe V3 61.46 Mean (Task) |
| [Vintern-Embedding-1B](vintern-embedding-1b.md) | VI, EN, ZH[^vintern-embedding-1b-card] | multi-vector, ~0.9B; width undisclosed | ViDoRe average 82.85 (protocol undocumented) |

### Tier B — labelled multilingual without a language list

| Model | Language evidence | Reported result |
|---|---|---|
| [webAI-ColVec1.1-4b](webai-colvec1-1-4b.md) / [8b](webai-colvec1-1-8b.md) | ViDoRe V3 tasks averaged over six unnamed language subsets[^webai-colvec1-1-4b-card][^webai-colvec1-1-8b-card] | V3 final mean 63.90 / 64.95; 640D tokens |
| [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md) / [9b](pplx-embed-v2-late-9b.md) | Hub tag `multilingual` only[^pplx-late-06b-page][^pplx-late-9b-page] | ViDoRe V3 public (Image) 62.3 / 65.2; 128D tokens; MIT |
| [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) | multilingual synthetic training data; EN/FR finance tasks[^nemotron-colembed-vl-8b-v2-card] | ViDoRe V3 63.54; 4,096D tokens |
| [Llama-Nemotron-ColEmbed-VL-3B-v2](llama-nemotron-colembed-vl-3b-v2.md) | labelled multilingual[^llama-nemotron-colembed-vl-3b-v2-card] | ViDoRe V3 0.5970 nDCG@10 |
| [Tomoro ColQwen3 4B](tomoro-colqwen3-embed-4b.md) / [8B](tomoro-colqwen3-embed-8b.md) | separate multilingual ViDoRe V3 split, languages unlisted[^tomoro-colqwen3-4b-card][^tomoro-colqwen3-8b-card] | V3 multilingual nDCG@5 0.5708 / 0.5866 |
| [Jina v5 Omni Nano](jina-embeddings-v5-omni-nano.md) / [Small](jina-embeddings-v5-omni-small.md) | text space aligned with multilingual Jina v5 Text; language coverage for image/video/audio not established[^jina-v5-omni-nano-card][^jina-v5-omni-small-card] | MIEB Image 47.87 / 58.00 |
| [e5-omni](e5-omni.md) | training mixes in BGE-M3 text pairs; language distribution not reported[^e5-omni-report] | MMEB-v2 66.4 (7B) |

### Excluded (≤2 languages documented or none stated)

- Chinese + English only: [WeMM-Embedding](wemm-embedding.md)[^wemm-readme] and [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md).[^tianmu-emb-uni-8b-card]
- English only: [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md).[^omni-embed-nemotron-3b-card]
- English/Chinese-heavy training: [UEmbed](uembed.md).[^uembed-tech-report]
- Mostly English targets: [Sentio](sentio.md), [Wianmu-3B](wianmu-3b.md), [Wianmu-5B](wianmu-5b.md).[^sentio-card][^wianmu-3b-page][^wianmu-5b-page]
- Language coverage not stated: [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md), [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md), [AuroLA-Omni-3B](aurola-omni-3b.md).[^ovis-vl-card][^ovis-omni-card][^geevec-page][^auro-la-omni-3b-page]

### Selection within the filter (Synthesis)

- **Low-resource languages:** DNA-VL-STEER-2B is the only model with per-language evidence (36 languages); keep base Qwen3-VL-2B for text-only work.
- **Broad image/video/visual-document:** Qwen3-VL-Embedding-8B has the highest MMEB-v2 score (77.9) among models claiming 30+ languages. WeMM scores higher but fails the language filter.
- **Compact multilingual page retrieval, one vector:** Nemotron-3.5-Embed-1B (explicit 18-language image evaluation).
- **Highest visual-document recall:** pplx-late-9b, EVIE, webAI-8b, and Nemotron-ColEmbed-8B cluster at ~63.5–65.4 on ViDoRe V3 but under unequal protocols/token budgets; no strict ranking.
- **Vietnamese-first:** Vintern-Embedding-1B lists Vietnamese explicitly; Nemotron-3.5-Embed-1B and DNA-VL-STEER-2B include Vietnamese in their evaluated sets.
- **Widest coverage on device:** EmbeddingGemma 2 (100+), with clearly lower image quality than Qwen3-VL.

## Architecture and modality matrix

| Model line (concrete variants) | Reported modalities | Retrieval form | Size / output |
|---|---|---|---|
| [Qwen3-VL Embedding](qwen3-vl-embedding-8b.md) (2B, 8B) | text, image, screenshot, video, mixed input | dense cosine bi-encoder | 2B: 64–2,048D; 8B: 64–4,096D Matryoshka |
| [WeMM-Embedding](wemm-embedding.md) (2B, 4B, 9B) | text, image, video, visual document, interleaved; no audio | dense, dedicated-token pooling | 2,048D / 2,560D / 4,096D Matryoshka |
| [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md) | text queries; text, image, image+text documents | dense mean-pooled bi-encoder | 1.55B; 2,048D |
| [EmbeddingGemma 2](embeddinggemma-2.md) | text, code, image, video, audio | dense mean-pooled | 740M; 768D Matryoshka |
| [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md) | text, image, video (sampled frames), visual document; no audio listed | dense last-token bi-encoder (Qwen3.5-9B) | 9.41B; 4,096D; 8,192-token pipeline[^geevec-page] |
| [Sentio](sentio.md) | audio, text, image, video, visual document | dense; frozen WeMM-9B + audio connector/LoRA | 10.20B composite (152M trained); 4,096D |
| [Wianmu-5B](wianmu-5b.md) | audio added to WeMM-4B's text, image, video | dense; frozen WeMM-4B + frozen Qwen2.5-Omni audio tower + trained connector | ≈5.2B composite (≈71M trained); 2,560D[^wianmu-5b-page] |
| [Wianmu-3B](wianmu-3b.md) | audio added to WeMM-2B's text, image, video | dense; frozen WeMM-2B + frozen Qwen2.5-Omni audio tower + trained connector | ≈2.9B composite (≈64M trained); 2,048D[^wianmu-3b-page] |
| [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md) | text, image, visual document, video, audio, interleaved | dense last-token bi-encoder; no projection heads | 3B; 2,048D, post-hoc 1,024–128D |
| [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md) | text, image, visual document, video, interleaved; no audio | dense last-token bi-encoder; no projection heads | 2B class (Qwen3.5-2B); 2,048D |
| [DNA-VL-STEER-2B](dna-vl-steer-2b.md) | text, image, screenshot, video, interleaved (36 calibrated languages) | dense last-token bi-encoder; Qwen3-VL-Embedding-2B with early layers adjusted | 2.13B BF16; 2,048D Matryoshka 64–2,048 |
| [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md) | text, image, video, visual document, audio, agent | dense | 8B-scale assembled system; 3,584D |
| [e5-omni](e5-omni.md) (3B, 7B) | text, image, audio, video | dense contrastive bi-encoder | 3B checkpoint 4.703B BF16 (Hub metadata); dimensionality not disclosed |
| [AuroLA-Omni-3B](aurola-omni-3b.md) | text, image, audio, video | dense last-token bi-encoder (Qwen2.5-Omni Thinker) | 4.702B BF16 (Hub metadata); dimensionality not disclosed |
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
| [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md) | text, document image | 128D-token MaxSim | 0.59B stored / 340M active[^pplx-late-06b-page] |
| [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md) | text, document image | 128D-token MaxSim | 8.39B stored / 7.4B active; F32 33.57 GB[^pplx-late-9b-page] |

## Comparable reported results

Scores only compare *within the named benchmark, version, metric, and supplied table*.

| Evaluation | Reported leading documented model | Other material comparisons |
|---|---|---|
| MMEB-v2, 78 tasks | WeMM 9B: 80.6 All (author report; its leaderboard-first claim is dated 2026-08-24) | WeMM 4B: 79.2; WeMM 2B: 77.9; Qwen3-VL Embedding 8B: 77.9; Ovis-VL-Embedding-2B: 77.46 (card; baselines unnamed); Qwen 2B: 73.4; UEmbed 9B dense: 71.8; e5-omni 7B: 66.4; EmbeddingGemma 2: 59.01 (its own card, protocol unstated). Metrics mix image/video Hit@1 and visual-document nDCG@5. [^wemm-readme][^embeddinggemma-2-card][^ovis-vl-card] |
| MMEB-v3 V3-All, 190 tasks (WeMM card; not in the snapshot) | WeMM 9B: 59.5 | WeMM 4B: 58.2; WeMM 2B: 56.0; Tianmu: 53.27 in its own card. Unsupported tasks score zero, so WeMM's audio is 0.0. Do not merge with the snapshot's Overall column. [^wemm-readme] |
| ViDoRe V3 + MIRACL-VISION, NDCG@10 (Nemotron card; vendor-run) | Nemotron-3.5-Embed-1B: image 58.02 / 68.93 | Qwen3-VL-2B: 52.89 / 58.42; Qwen3-VL-8B: 58.29 / 68.33; the card's 8B teacher: 60.39 / 72.64. Different protocol from the late-interaction ViDoRe V3 row below. [^nemotron-3-5-embed-1b-card] |
| MMEB-v2, 44 retrieval datasets only (GeeVec card; Image/Video Hit@1, VisDoc NDCG@5) | Sentio: 79.57 AVG | WeMM-9B: 79.38; Ovis-VL-Embedding-9B: 78.94; [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md): 78.78 (best Image 81.82 and VisDoc 83.63, Video 59.66); WeMM-4B: 78.19; Qwen3-VL-Embedding-8B: 77.28. A retrieval-only subset: do not merge with the 78-task All scores above. Author-reported. [^geevec-page] |
| MMEB-V3, 190 tasks (Sentio card, leaderboard snapshot of 16 Oct 2026) | Sentio: 61.69 Overall (Overall-V3 48.46) | [Wianmu-5B](wianmu-5b.md)-v0: 60.45; WeMM-9B: 59.33; [Wianmu-3B](wianmu-3b.md)-v0: 58.16. Audio: Wianmu-5B 42.93 > Wianmu-3B 41.16 > Sentio 36.81. Different Overall value from WeMM's own 59.5 (V3-All) and scale from Ovis's 58.46; do not merge. [^sentio-card] |
| MMEB-v3, 190 datasets (Ovis card; not the snapshot) | Ovis-Omni-Embedding-3B: 58.46 | Its card's best compared baseline: 53.27 (unnamed); Tianmu: 53.27 in its own card. Audio 50.08, Agent 45.52, Text 47.15. Author-reported; the snapshot lists a differing v0.1 entry (52.55), so do not merge. [^ovis-omni-card] |
| MMEB-V3 (AuroLA-Omni-3B card; version and task count unstated) | AuroLA-Omni-3B: 46.7 Average (Image 65.1, Video 48.9, VisDoc 69.2, Text 32.4, Audio 46.8, Agentic 36.5) | No baselines on the card; the Average is not the mean of its six groups (49.8). Not in the snapshot; do not merge with Ovis's 58.46, Sentio's 61.69, or the snapshot's Overall. Author-reported. [^auro-la-omni-3b-page] |
| MMEB v3 snapshot, Overall | Tianmu: 52.83 | UEmbed 9B hybrid: 51.54; UEmbed 4B dense: 50.10; e5-omni 7B: 46.53; Omni-Embed: 42.83. |
| MMEB v3 snapshot, Audio | e5-omni 7B: 43.04 among documented entries | Tianmu: 38.94; Omni-Embed: 36.52. Ovis-Omni-Embedding-v0.1-3B reports 47.82 (see [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md)). |
| ViDoRe V3 reported tables | webAI 8B: 64.95 final mean | EVIE: 65.36 public at extrapolated visual budget; Nemotron 8B: 63.54; ColQwen3.5: 61.46 Mean (Task); Tomoro 8B: 0.6113 nDCG@5, therefore not directly metric-comparable; pplx-embed-v2-late-0.6b: 62.3 (Image) / 61.2 (Markdown) nDCG@10 on the public set, with unstated token budget;[^pplx-late-06b-page] pplx-embed-v2-late-9b: 65.2 / 64.7 on the same public set (token budget also unstated); it should be compared with the other entries only after confirming the unsupplied protocol matches.[^pplx-late-9b-page] |
| MTEB Multilingual v2 (text-only slice) | Jina v5 Omni Small: 67.00 Mean (Task) | Omni Nano: 65.52. Both equal their paired text-model snapshot values, so independent omni evaluation is not established. |

## MMEB v3 snapshot coverage and limits

The raw CSV ranks 89 entries by reported `Overall`; it does not include WeMM, Nemotron-3.5-Embed-1B, or EmbeddingGemma 2. 13 provide nonzero `Overall-V3`, Text, Audio, and Agent values. The remaining 76 entries include Qwen3-VL-Embedding (ranks 18 and 24), Jina v5 Omni Small/Nano (87/88), and many models not otherwise documented in this wiki. Their zero-filled v3 fields may mean missing evaluation rather than failure. The only defensible exhaustive comparison of all 89 is the [snapshot](mmeb-v3-ranking-snapshot.md) itself; it lacks metric definitions, task composition, capture date, inclusion rules, and evaluation configuration.[^mmeb-v3-ranking]

## Decision constraints

- **Do not compare dense-vector dimensions to token-vector dimensions as index footprint.** Late-interaction footprint also scales with retained tokens/page or frame.
- **Use a reranker after first-stage retrieval** when latency allows. Qwen's multimodal rerankers are cross-encoders, not embeddings, and are intentionally excluded from this comparison.
- **Language claims are uneven** (see the [multilingual filter](#multilingual-filter-image--text-with-more-than-two-languages)). Qwen claims 30+ languages; WeMM lists Chinese and English; Nemotron-3.5-Embed-1B evaluated image retrieval in 18 languages; EVIE explicitly lists seven query languages; Vintern explicitly lists Vietnamese, English, and Chinese. Many other cards merely say multilingual.
- Most scores are provider-reported; neither the raw snapshot nor the model cards provide a common independently reproduced evaluation.

## Relationships

- **Uses benchmark:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md).
- **Compares:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md), [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [UEmbed](uembed.md), and the model lines linked above.
- **Uses method:** [GELATO](gelato.md) for the Jina v5 Omni variants. [^jina-v5-omni-report]
- **Added 2026-10-22:** [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md), [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md), [GeeVec-Embeddings-mm-1.0](geevec-embeddings-mm-1-0.md), [Wianmu-5B](wianmu-5b.md), [Wianmu-3B](wianmu-3b.md), [DNA-VL-STEER-2B](dna-vl-steer-2b.md), [AuroLA-Omni-3B](aurola-omni-3b.md), [Sentio](sentio.md), [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md), [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), [WeMM-Embedding](wemm-embedding.md), [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md), [EmbeddingGemma 2](embeddinggemma-2.md). Their scores are author-reported (Reported) and cross-table comparisons above are Synthesis.

[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This supplied, unauthenticated artifact supports only its reported values; it does not define benchmark semantics or explain zero-filled fields.
[^jina-v5-omni-report]: [jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers](../raw/2605.08384_jina-embeddings-v5-omni/main.tex). Author technical report; its architecture and benchmark claims were not independently reproduced.
[^ovis-omni-card]: [Ovis-Omni-Embedding-3B model page](../raw/ATH-MaaS-Ovis-Omni-Embedding-3B.md), Performance (MMEB-v3) table. Author-reported; baseline names are in an image not in `raw/`.
[^ovis-vl-card]: [Ovis-VL-Embedding-2B model page](../raw/ATH-MaaS-Ovis-VL-Embedding-2B.md), Performance (MMEB-v2) table. Author-reported; baseline names are in an image not in `raw/`.
[^auro-la-omni-3b-page]: [Jazzcharles/AuroLA-Omni-3B page capture](../raw/Jazzcharles-AuroLA-Omni-3B.md), MMEB-V3 Results table. Author-reported; no protocol or baselines.
[^sentio-card]: [Dragos-Datcu/Sentio model page](../raw/Dragos-Datcu-Sentio.md), Evaluation tables (MMEB-V3, MMEB-V2, audio). Author-reported.
[^geevec-page]: [geevec-ai/geevec-embeddings-mm-1.0 model page](../raw/geevec-ai-geevec-embeddings-mm-1.0.md), Introduction and Evaluation → MMEB-v2 Retrieval table. Author-reported; the 44-dataset retrieval subset differs from the 78-task All score.
[^wianmu-3b-page]: [eduardo-terres2/Wianmu-3B model page](../raw/eduardo-terres2-Wianmu-3B.md), How it works (pipeline, parameter budget, output width). Author-reported; scores for this model come only via the Sentio card.
[^wianmu-5b-page]: [eduardo-terres2/Wianmu-5B model page](../raw/eduardo-terres2-Wianmu-5B.md), How it works (pipeline, parameter budget, output width). Author-reported; scores for this model come only via the Sentio card.
[^wemm-readme]: [WeMM-Embedding repository README](../raw/WeMM-Embedding/README.md), Model Zoo and MMEB-v2/MMEB-v3 tables (spot-checked against the 2B card's MMEB-v2 table). Author-reported; the technical report and other cards are covered in [WeMM-Embedding](wemm-embedding.md).
[^nemotron-3-5-embed-1b-card]: [Nemotron-3.5-Embed-1B-BF16 model card](../raw/Nemotron-3.5-Embed-1B-BF16.md), Evaluation Dataset table (ViDoRe V3, MIRACL-VISION). Vendor-run; not independently reproduced.
[^dna-vl-steer-2b-page]: [dnotitia/DNA-VL-STEER-2B model page](../raw/dnotitia-DNA-VL-STEER-2B.md), Performance (XM3600, video transfer) and Honest limitations. Author-reported; not independently reproduced.
[^embeddinggemma-2-card]: [EmbeddingGemma 2 model card](../raw/embeddinggemma-2.md), Benchmark Results and Matryoshka truncation tables. Vendor-reported aggregates; no protocol given.
[^pplx-late-06b-page]: [perplexity-ai/pplx-embed-v2-late-0.6b Hugging Face page capture](../raw/perplexity-ai-pplx-embed-v2-late-0.6b.md), Models table and Hub metadata. Vendor-reported; protocol in the unsupplied technical report.

[^pplx-late-9b-page]: [perplexity-ai/pplx-embed-v2-late-9b Hugging Face page capture](../raw/perplexity-ai-pplx-embed-v2-late-9b.md), Models table and Hub metadata. Vendor-reported; protocol in the unsupplied technical report.
[^qwen3-vl-embedding-2b-card]: [Qwen3-VL-Embedding-2B model card](../raw/Qwen3-VL-Embedding-2B.md), Highlights ("Supported Languages: 30+") and MMEB-V2 table. Author-reported.
[^qwen3-vl-embedding-8b-card]: [Qwen3-VL-Embedding-8B model card](../raw/Qwen3-VL-Embedding-8B.md), Highlights and MMEB-V2 table. Author-reported.
[^jina-v4-card]: [Jina Embeddings v4 model card](../raw/jina-embeddings-v4.md), feature list ("Multilingual support (30+ languages)"). Author-reported.
[^evie-card]: [EVIE-Preview-4.5B model card](../raw/EVIE-Preview-4.5B.md), language-support statement and ViDoRe V3 results. Author-reported.
[^colqwen35v3-card]: [ColQwen3.5-4.5B-v3 model card](../raw/ColQwen3.5-4.5B-v3.md), `language` front matter and ViDoRe V3 leaderboard capture. Author-reported.
[^vintern-embedding-1b-card]: [Vintern-Embedding-1B model card](../raw/Vintern-Embedding-1B.md), `language` front matter and ViDoRe table. Author-reported.
[^webai-colvec1-1-4b-card]: [webAI-ColVec1.1-4b model card](../raw/webAI-ColVec1.1-4b.md), ViDoRe V3 table and language claims. Author-reported.
[^webai-colvec1-1-8b-card]: [webAI-ColVec1.1-8b model card](../raw/webAI-ColVec1.1-8b.md), ViDoRe V3 table and language claims. Author-reported.
[^nemotron-colembed-vl-8b-v2-card]: [Nemotron ColEmbed VL 8B v2 model card](../raw/nemotron-colembed-vl-8b-v2.md), training-data description and ViDoRe V3 table. Vendor-reported.
[^llama-nemotron-colembed-vl-3b-v2-card]: [Llama-Nemotron-ColEmbed-VL-3B-v2 model card](../raw/llama-nemotron-colembed-vl-3b-v2.md), description and ViDoRe V1–V3 table. Vendor-reported.
[^tomoro-colqwen3-4b-card]: [TomoroAI/tomoro-colqwen3-embed-4b model card](../raw/tomoro-colqwen3-embed-4b.md), ViDoRe V3 multilingual table. Author-reported.
[^tomoro-colqwen3-8b-card]: [TomoroAI/tomoro-colqwen3-embed-8b model card](../raw/tomoro-colqwen3-embed-8b.md), ViDoRe V3 multilingual table. Author-reported.
[^jina-v5-omni-nano-card]: [jina-embeddings-v5-omni-nano model card](../raw/jina-embeddings-v5-omni-nano.md), model description ("multilingual"; no language list). Author-reported.
[^jina-v5-omni-small-card]: [jina-embeddings-v5-omni-small model card](../raw/jina-embeddings-v5-omni-small.md), model description ("multilingual"; no language list). Author-reported.
[^e5-omni-report]: [e5-omni technical report](../raw/2601.03666_e5-omni/acl.tex), training-data and MMEB-V2 results sections. Author-reported.
[^tianmu-emb-uni-8b-card]: [Tianmu-Emb-Uni-8B model card](../raw/Tianmu-Emb-Uni-8B.md), `language` front matter (zh, en).
[^omni-embed-nemotron-3b-card]: [Omni-Embed-Nemotron-3B model card](../raw/omni-embed-nemotron-3b.md), `language` front matter (en only).
[^uembed-tech-report]: [UEmbed technical report](../raw/2608.02583_UEmbed/main.tex), limitations (English/Chinese-heavy training data).
