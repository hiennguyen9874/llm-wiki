---
type: Concept
title: WeMM-Embedding
description: A 2B, 4B, and 9B Qwen3.5-based universal multimodal embedding family with dedicated-token pooling, Matryoshka outputs, and reported MMEB-v2/v3 leadership.
tags: [embedding, retrieval, multimodal, multilingual, matryoshka, qwen]
status: stable
created: 2026-09-03
generated: { by: llm-wiki-agent/1, at: 2026-09-03T00:00:00Z }
sources:
  - id: wemm-readme
    resource: ../raw/WeMM-Embedding/README.md
    title: WeMM-Embedding repository README
  - id: wemm-2b-card
    resource: ../raw/WeMM-Embedding/WeMM-Embedding-2B.md
    title: WeMM-Embedding-2B model card
  - id: wemm-4b-card
    resource: ../raw/WeMM-Embedding/WeMM-Embedding-4B.md
    title: WeMM-Embedding-4B model card
  - id: wemm-9b-card
    resource: ../raw/WeMM-Embedding/WeMM-Embedding-9B.md
    title: WeMM-Embedding-9B model card
  - id: wemm-report
    resource: ../raw/WeMM-Embedding/2608.24053-WeMM-Embedding/main.tex
    title: "WeMM-Embedding: WeChat Multi-Modal Embedding Technical Report"
---

# WeMM-Embedding

WeMM-Embedding is a universal multimodal embedding family from WeChat Vision, Tencent, built on natively multimodal Qwen3.5 backbones. It encodes text, images, videos, visual documents, and interleaved multimodal inputs into one L2-normalized dense space; audio input is not supported. The 2B variant already exceeds the report's prior 8B open-source baselines on MMEB-v2, and the 9B variant reports 80.6 overall, claimed as first on the official MMEB-v2 leaderboard as of August 24, 2026.[^wemm-report][^wemm-readme]

## Variants

| Variant | Base model | Full dimension | Matryoshka dimensions |
|---|---|---:|---|
| WeMM-Embedding-2B | Qwen/Qwen3.5-2B | 2,048 | 64, 128, 256, 512, 1024, 2048 |
| WeMM-Embedding-4B | Qwen/Qwen3.5-4B | 2,560 | 64, 128, 256, 512, 1024, 2560 |
| WeMM-Embedding-9B | Qwen/Qwen3.5-9B | 4,096 | 64, 128, 256, 512, 1024, 2048, 4096 |

Base-model, dimension, and Matryoshka-set claims are from the repository Model Zoo and the three model cards.[^wemm-readme][^wemm-2b-card][^wemm-4b-card][^wemm-9b-card] Cards list languages as Chinese and English, pipeline tag `feature-extraction`, and Apache-2.0 licensing for Tencent-released code and weights with third-party components retaining their own licenses.[^wemm-2b-card][^wemm-4b-card][^wemm-9b-card]

## Architecture

- **Pooling:** a dedicated `<embedding>` token is appended to the ordered multimodal token sequence; its final-layer hidden state is L2-normalized as the output representation. It attends to all preceding text and visual tokens under causal attention.[^wemm-report]
- **Multi-position embeddings:** the same causal formulation allows several `<embedding>` tokens at different positions. The report's example places one after video tokens and another after an ASR transcript to obtain video-only and joint video-text vectors in one forward pass.[^wemm-report]
- **Matryoshka outputs:** dimension `d` keeps the first `d` hidden-state entries and re-normalizes, so all supported widths come from one forward pass. Cards and README use `embedding[..., :d]` plus `normalize`, or Sentence Transformers `truncate_dim` with normalization.[^wemm-report][^wemm-readme][^wemm-2b-card]
- **Inputs:** text, image, video, visual document, and interleaved combinations; image or video entries precede text in the documented prompt ordering. Chat-message inputs with several images or videos are accepted.[^wemm-2b-card][^wemm-4b-card][^wemm-9b-card]

## Training data

Training examples use a unified pair format `(I, q, c, N, y)`: optional instruction, source, paired target, optional explicit hard negatives, and optional graded relevance score. Both source and target may be text, image, video, or interleaved combinations; negatives share the target-side modality structure.[^wemm-report]

- **Large-scale collection:** several hundred million pairs from public datasets, web-scale weakly supervised sources, task-oriented synthetic data, and in-house collections. Families are weakly supervised image/video-text pairs, caption pairs, retrieval pairs, classification pairs reformulated as source-label pairs, multimodal question-answer pairs, and manually graded discrete-relevance pairs.[^wemm-report]
- **Curated set:** about one-tenth the large-scale size, built by Semantic-ID-guided resampling, MLLM quality filtering and text correction, and hard-negative enrichment. Semantic IDs come from encoding each pair's longer side with an intermediate WeMM checkpoint and mapping it through a three-level residual k-means quantizer; dense codes are downsampled and rare codes retained at higher rates.[^wemm-report]
- **Hard negatives:** LLM-generated plausible-but-wrong candidates for text targets; embedding-retrieved similar candidates from task pools for image and video targets; a smaller mined subset receives reranker-assigned relevance scores.[^wemm-report]

Rendered dataset-overview and performance-overview PDF figures under `figs/` were not visually inspected; the above follows the report text and captions. Icon assets carry no material claims.[^wemm-report]

## Training strategy

Two stages progress from broad alignment to fine-grained relevance learning.[^wemm-report]

- **Stage 1, large-scale alignment:** each batch comes from one data source with task-consistent candidate spaces; batches from different tasks interleave. Standard pairs use InfoNCE with in-batch negatives plus available explicit hard negatives and duplicate-aware masking that drops candidates tied to near-duplicate sources or near-duplicate positives above similarity threshold `tau_dup`. Manually graded batches use a score-gap-weighted CoSENT-style objective weighting pairwise comparisons by `max(|y_i - y_j|, epsilon)`. Both objectives are trained in Matryoshka form across all supported dimensions.[^wemm-report]
- **Stage 2, curated fine-tuning and distillation:** contrastive and graded objectives remain; reranker-scored batches replace contrastive loss with a query-local gap-weighted ranking loss over reranker orderings. Embedding distillation adds bidirectional KL between teacher and student source-to-target and target-to-source softmax distributions. For 2B and 4B the frozen 9B WeMM model is teacher; the 9B final model merges multiple specialized Stage-2 variants with TIES merging because no larger teacher exists. A larger visual-input budget from higher resolution and denser frame sampling is included in the final 2B configuration.[^wemm-report]
- **Ablation evidence:** a small-scale 2B Stage-1 study reports full 71.9 MMEB-v2 AVG, falling to 71.1 without task instructions, 68.5 without task-consistent batching, and 71.4 without duplicate masking. A cumulative 2B Stage-2 study reports 75.7 from Stage 1, then 76.6 with curated data, 76.7 with reranker supervision, 77.6 with teacher distillation, and 77.9 final with expanded visual budget. The report presents reranker gains as reliable only on a limited task subset.[^wemm-report]

## Reported benchmarks

All scores below are author-reported; no independent reproduction was available.

| Benchmark | WeMM-2B | WeMM-4B | WeMM-9B | Context |
|---|---:|---:|---:|---|
| MMEB-v2 AVG, 78 datasets | 77.9 | 79.2 | 80.6 | Image/Video Hit@1; VisDoc NDCG@5 |
| MMEB-v2 Image / Video / VisDoc | 79.6 / 70.8 / 80.7 | 80.8 / 72.1 / 82.0 | 81.9 / 74.3 / 83.3 | Same protocol |
| MMEB-v3 V3-All, 190 tasks | 56.0 | 58.2 | 59.5 | Unsupported tasks scored zero; audio 0.0 for all WeMM |
| MMEB-v3 Text / Agent / MCMR | 45.3 / 45.1 / 42.5 | 47.9 / 49.0 / 41.9 | 48.8 / 51.0 / 49.3 | Text NDCG@5; agent/MCMR Hit@1 |
| 12-task cross-modal AVG | 79.8 | 80.8 | 81.7 | MSCOCO, Flickr30k, DOCCI, TextCaps, VATEX, MSR-VTT, YouCook2, ViDoRe V2 |

MMEB-v2 and MMEB-v3 tables are shared across the README and all three cards and detailed by task split in the report.[^wemm-readme][^wemm-2b-card][^wemm-report] On MMEB-v2 the report places 2B above Qwen3-VL-Embedding-2B by 4.7 and DME-Small by 3.1, slightly above Qwen3-VL-Embedding-8B, with 4B above all compared 8B-9B baselines and 9B first among listed open and proprietary entries.[^wemm-report] On MMEB-v3 the report places 2B above all compared baselines including Qwen3-VL-Embedding-2B/8B, Tianmu-Emb-Uni, E5-Omni, Omni-Embed-Nemotron, GME, VLM2Vec variants, WAVE, and LCO-Embedding-Omni.[^wemm-report]

Cross-modal retrieval averages MSCOCO, Flickr30k, DOCCI, and TextCaps in both directions plus VATEX, MSR-VTT, YouCook2, and ViDoRe V2. Reported 9B AVG is 81.7 against Gemini Embedding 2 at 79.5, Amazon Nova MME at 70.2, Voyage Multimodal 3.5 at 71.8, and author-evaluated Qwen3-VL-Embedding-8B at 76.7.[^wemm-report]

In-house evidence covers 26 WeChat tasks in classification, search, cross-domain matching, article relevance, and video relevance. Reported 2B AVG is 72.0 versus 60.9 for Qwen3-VL-Embedding-2B, higher in all five groups. The report also claims deployment gains across 14 online A/B tests in WeChat Channels, Official Accounts, Moments, e-commerce recommendation, and WeChat search, including candidate retrieval, ranking features, sequence modeling, and Semantic-ID indexing.[^wemm-report]

## Efficiency findings

On MMEB-v2, 2B at 256 dimensions retains a reported 98.7% of full-dimensional image and video performance; at 512 dimensions retention is 99.2% image and 98.8% video. Visual-document tasks are more dimension-sensitive, attributed to dense textual content. By task type, classification degrades least, question answering moderately, and retrieval most at 64-128 dimensions; all three exceed 97% retention at 256 dimensions.[^wemm-report][^wemm-readme][^wemm-2b-card]

## Deployment

- Recommended inference stack is `transformers==5.2.0`, `qwen-vl-utils[decord]==0.0.14`, `sentence-transformers>=5.7.0`, and `accelerate>=1.1.0`.[^wemm-2b-card][^wemm-4b-card][^wemm-9b-card]
- Transformers path calls `model.embedding(**inputs)` after `process_vision_info` with `image_patch_size=16`; Sentence Transformers path uses `encode_query` and `encode_document` with optional `truncate_dim`.[^wemm-2b-card]
- Serving is documented for vLLM `0.27.0` in pooling mode with the bundled embedding chat template and SGLang `0.5.9` with `--is-embedding` and precise-embedding interpolation; wrapper scripts are `scripts/serve_vllm.sh` and `scripts/serve_sglang.sh`.[^wemm-readme][^wemm-2b-card]
- MMEB-v3 evaluation code in `mmeb_v3_eval/` adapts the VLM2Vec pipeline with multi-node `torchrun`, a `wemm_embedding` backbone, aligned dataset instructions, and 64-frame video sampling.[^wemm-readme]

## Limits

- No audio input support; MMEB-v3 audio tasks are therefore zero in the reported V3-All averages.[^wemm-readme][^wemm-report]
- Proprietary and in-house training portions, exact pair counts, and production A/B details are not disclosed enough for a full audit; reranker supervision is described as beneficial only on a limited subset.[^wemm-report]
- Leaderboard-first and cross-modal comparison claims are dated to report capture and August 24, 2026 leaderboard status, not continuously verified.[^wemm-report]

## Relationships

- **Shares Qwen3.5 backbone generation with:** [UEmbed](uembed.md), [UEmbed-4B](uembed-4b.md), [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md), [EVIE-Preview-4.5B](evie-preview-4-5b.md), [webAI-ColVec1.1-4b](webai-colvec1-1-4b.md), and [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md).
- **Report compares against:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md), [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), and [e5-omni](e5-omni.md).
- **Uses benchmark context from:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md).

[^wemm-readme]: [WeMM-Embedding repository README](../raw/WeMM-Embedding/README.md). Model Zoo, Matryoshka guidance, serving versions, MMEB tables, and evaluation-code claims are author-reported.
[^wemm-2b-card]: [WeMM-Embedding-2B model card](../raw/WeMM-Embedding/WeMM-Embedding-2B.md). Base model, 2,048 dimensions, language, install, inference, serving, and benchmark claims are author-reported.
[^wemm-4b-card]: [WeMM-Embedding-4B model card](../raw/WeMM-Embedding/WeMM-Embedding-4B.md). Base model, 2,560 dimensions, install, inference, serving, and benchmark claims are author-reported.
[^wemm-9b-card]: [WeMM-Embedding-9B model card](../raw/WeMM-Embedding/WeMM-Embedding-9B.md). Base model, 4,096 dimensions, install, inference, serving, and benchmark claims are author-reported.
[^wemm-report]: [WeMM-Embedding technical report](../raw/WeMM-Embedding/2608.24053-WeMM-Embedding/main.tex). Architecture, unified data format, two-stage training, distillation, ablation, MRL, cross-modal, in-house, and deployment claims are author-reported; proprietary data prevent full auditability. PDF figures were coverage-limited to captions and citing text.
