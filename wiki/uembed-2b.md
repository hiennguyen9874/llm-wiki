---
type: Concept
title: UEmbed-2B
description: A 2.21B-parameter Qwen3.5-based decoder-only multimodal embedding model producing dense and SPLADE-style sparse vectors, with reported MMEB-v2, BEIR, BrowseComp-Plus, and MMEB-v3 results.
tags: [embedding, retrieval, multimodal, dense-retrieval, sparse-retrieval, splade, qwen]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T19:00:00Z }
sources:
  - id: uembed-2b-card
    resource: ../raw/Alibaba-NLP-UEmbed-2B.md
    kind: web-capture
    title: Alibaba-NLP/UEmbed-2B Hugging Face model page (HTML capture)
  - id: uembed-tech-report
    resource: ../raw/2608.02583_UEmbed/main.tex
    scope: ../raw/2608.02583_UEmbed/
    kind: paper
    title: UEmbed technical-report LaTeX source
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    kind: dataset
    title: MMEB v3 ranking CSV
---

# UEmbed-2B

UEmbed-2B is the smallest member of the [UEmbed](uembed.md) family: a decoder-only multimodal embedding model on a Qwen3.5 backbone that returns a normalized dense vector and a SPLADE-style sparse lexical vector from one causal forward pass, for text, image, and video inputs. The Hugging Face page lists 2,213,241,664 BF16 parameters and a CC-BY-4.0 license. Its author-reported MMEB-v2 score is 66.5 dense / 65.5 sparse, below [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) (73.2) in the same table.[^uembed-2b-card][^uembed-tech-report]

## Model details

| Item | Value |
|---|---|
| Parameters | 2,213,241,664, all BF16; sharded safetensors, 4,426,605,902 bytes total (HF page metadata) — the page's family table rounds this to "2B"[^uembed-2b-card] |
| Backbone | Qwen3.5-2B; HF config architecture `Qwen3_5ForConditionalGeneration`, `model_type: qwen3_5`[^uembed-2b-card][^uembed-tech-report] |
| Modalities | Text, image, video, and mixed-modal inputs (no audio)[^uembed-2b-card] |
| Dense output | Normalized hidden state of the EOS token before the appended sparse special tokens (`pooling="last.normal"`); dimensionality not stated[^uembed-2b-card] |
| Sparse output | 16 appended special tokens, each with a subset-specific linear head; vocabulary compressed from 248,320 to 184,016 canonical entries; activation `log(1 + ReLU(logits))` (`pooling="splade.last"`)[^uembed-2b-card] |
| Objective | Dense InfoNCE + sparse InfoNCE + query/document FLOPS regularization[^uembed-2b-card] |
| Context limit | Not stated[^uembed-2b-card] |
| License | CC-BY-4.0[^uembed-2b-card] |
| Languages | Not stated on the card; the report acknowledges English/Chinese-heavy training data and limited sparse cross-lingual activation[^uembed-tech-report] |

## Usage

- Requires `transformers>=5.4.0` with Qwen3.5/Qwen3-VL support; the card says it loads natively, with no `trust_remote_code`, and also lists a vLLM backend for dense and sparse inference.[^uembed-2b-card]
- Download the whole repository: sparse inference needs both `sparse_info.json` and `sparse_weights.pt` in the local model directory.[^uembed-2b-card]
- Inference goes through the `Qwen35Embedder.process` wrapper in the project's GitHub repository, taking dictionaries with `text`, `image`, `video`, optional `instruction`, `fps`, and `max_frames`. The card example uses bfloat16 and optional FlashAttention-2.[^uembed-2b-card]
- Those code and example details are Reported; the code was not inspected or run for this concept. The linked GitHub repository and demo Space were not captured.[^uembed-2b-card]

## Training

The family trains on 3.94M public samples: E5 training data (text), MLDR from M3, and MMEB training sets, with Qwen3-VL-Embedding-8B as the hard-negative teacher for multimodal data. The report adds that 2B and 4B were trained on 16×A100 GPUs with per-device batch 16, for a global batch of 256.[^uembed-2b-card][^uembed-tech-report]

## Reported benchmarks (author-reported)

**MMEB-v2 (78 datasets)**, from the report's main table:[^uembed-tech-report]

| Output | Image (36) | Video (18) | VisDoc (24) | All |
|---|---:|---:|---:|---:|
| Dense | 67.8 | 50.0 | 77.0 | 66.5 |
| Sparse | 67.0 | 47.7 | 76.7 | 65.5 |
| Qwen3-VL-Embedding-2B (reference row) | 75.0 | 61.9 | 79.2 | 73.2 |

The report excludes Qwen3-VL-Embedding from bolded best-score selection because it is described as trained on large-scale proprietary data.[^uembed-tech-report] A seed-42 appendix ablation lists UEmbed-2B at 64.6 dense / 63.4 sparse; it is a separate run and should not be mixed with the main-table values.[^uembed-tech-report]

**BEIR (nine datasets, nDCG@10):** dense 53.6, sparse 52.3. Qwen3-VL-Embedding-2B reaches 53.8 in the dense table. Compare protocol-for-protocol, not with other benchmark suites.[^uembed-tech-report]

**Hybrid scoring** (linear interpolation of dense and sparse similarity, per-modality weights in the appendix): 53.9 text, 67.9 image, 50.0 video, 77.5 VisDoc. Over dense, that is +0.3 text, +0.1 image, 0.0 video, and +0.5 VisDoc; the paper describes the gain as modest.[^uembed-tech-report]

**BrowseComp-Plus (agentic search):**[^uembed-tech-report]

| Retriever | Accuracy % | Recall % | Avg. searches | Calibration error % |
|---|---:|---:|---:|---:|
| UEmbed-2B dense | 44.10 | 53.47 | 39.19 | 16.69 |
| UEmbed-2B sparse | 44.05 | 57.04 | 32.67 | 8.54 |
| Qwen3-VL-Embedding-2B | 26.87 | 38.20 | 34.99 | 12.13 |
| BM25 | 36.87 | 43.02 | 17.91 | — |

For 2B, sparse retrieval matches dense accuracy with higher recall, fewer search rounds, and lower calibration error. The 4B model shows a different pattern, so the result is not a general rule across the family.[^uembed-tech-report]

**MMEB v3 ranking snapshot** (local CSV, 26-08-12 entries, see [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md)):[^mmeb-v3-ranking]

| Output | Rank | Overall | Overall-V3 | Text | Audio | Agent |
|---|---:|---:|---:|---:|---:|---:|
| Dense | 8 | 47.82 | 34.71 | 40.46 | 0.00 | 36.34 |
| Sparse | 9 | 46.93 | 33.85 | 39.40 | 0.00 | 35.52 |

In this snapshot dense leads sparse on every listed column for 2B, whereas for [UEmbed-4B](uembed-4b.md) sparse is slightly ahead on Overall-V3 and Agent. The CSV does not define metrics or evaluation configuration, and zero Audio may mean not evaluated.[^mmeb-v3-ranking]

The card's headline claim that UEmbed reaches state-of-the-art on the MMEB-v3 text and agent tracks and ranks second only to the Qwen3-VL-Embedding series among open-source models on MMEB-v2 is a family-level, author-reported claim. It is not specific to the 2B checkpoint, and the 2B scores above do not support it.[^uembed-2b-card][^uembed-tech-report]

## Limits and caveats

- All scores are Reported (author-reported); none was reproduced here. The report's authors name an English/Chinese-heavy training mix, limited sparse cross-lingual activation, occasional anomalous vocabulary activations, and a larger sparse-vs-dense gap on video.[^uembed-tech-report]
- The source is an HTML capture of the model page (undated; the page showed 410 downloads last month). The embedded chat template, site scripts, navigation, and the capture's widget metadata were excluded as boilerplate.[^uembed-2b-card]
- The card names the training text source "E5 training data" while the report names it "Echo-embedding training data" (see [UEmbed-4B](uembed-4b.md)).[^uembed-2b-card][^uembed-tech-report]

## Relationships

- **Variant of:** [UEmbed](uembed.md); siblings are [UEmbed-4B](uembed-4b.md) and a 9B model that has no concept page here.
- **Compared with:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) in the report's MMEB-v2, BEIR, and BrowseComp-Plus tables.
- **Placed in:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) and the [multimodal embedding model comparison](multimodal-embedding-model-comparison.md).

[^uembed-2b-card]: [Alibaba-NLP/UEmbed-2B model page capture](../raw/Alibaba-NLP-UEmbed-2B.md). Locators: rendered card sections "Model Family", "Architecture", "Usage", "Input Format", "Training Data", "News"; embedded page metadata (`safetensors`, `cardData`, `config`). Claims are author-reported or page metadata (Observed from the capture, not from the weights).
[^uembed-tech-report]: [UEmbed technical-report LaTeX source](../raw/2608.02583_UEmbed/main.tex). Locators: `tables/mmeb.tex` (main MMEB-v2), `tables/beir.tex`, `tables/effective-analysis.tex`, `tables/agent-app.tex`, `tables/appendix-mode-mmeb.tex`, `appendix/A.tex` (training hardware), `main/5-analysis.tex` (hybrid scoring). Author-reported; no independent reproduction.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). Rows "UEmbed-2B (dense)" and "UEmbed-2B (sparse)"; the artifact does not document metric definitions or evaluation provenance.
