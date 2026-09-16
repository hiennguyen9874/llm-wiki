---
type: Concept
title: CONQUER context-aware query-enhanced person search
description: CONQUER combines training-time cross-modal representation refinement with MLLM-assisted query expansion and re-ranking for text-based person search, but its released code materially diverges from the manuscript.
tags: [cross-modal-retrieval, clip, person-reidentification, optimal-transport, query-expansion, multimodal-llm]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:38:23Z }
sources:
  - id: arxiv-2601.18625
    resource: ../raw/papers/arXiv-2601.18625v1/main.tex
    title: "CONQUER: Context-Aware Representation with Query Enhancement for Text-Based Person Search"
  - id: conquer-code
    resource: ../raw/codes/CONQUER/README.md
    title: CONQUER official source code
---

# CONQUER context-aware query-enhanced person search

CONQUER is a two-stage text-based person-search framework: Context-Aware Representation Enhancement (CARE) trains CLIP-based global and local representations, while Interactive Query Enhancement (IQE) uses a multimodal language model at inference to verify candidate anchor images, describe their attributes, rewrite the query, and re-rank the gallery. The central idea is to couple a stronger retrieval model with inference-time pseudo-relevance feedback, but the released code does not faithfully implement several algorithms and hyperparameters stated in the manuscript; results should therefore be treated as author-reported until the exact evaluation path is clarified or reproduced.[^arxiv-2601.18625][^conquer-code]

## Manuscript method

### Context-Aware Representation Enhancement

CARE uses CLIP ViT-B/16 image and text encoders to produce global features and local visual/text tokens. The manuscript describes three components:[^arxiv-2601.18625]

- **Multi-granularity encoding:** global cosine similarities and selected local tokens provide two views of image-text correspondence.
- **Complementary pair mining:** training pairs are partitioned into clean, uncertain, and refinable sets; off-diagonal pairs from the refinable set are used as negatives.
- **Context-guided optimal matching:** a learned local-token cost matrix feeds entropy-regularized optimal transport, solved with Sinkhorn iterations. A KL-divergence term is intended to align the transport plan with local token similarity while preserving global semantic context.

The stated training objective is an alignment loss plus weighted complementary-negative and OT losses. The reported configuration uses batch size 64, Adam, 60 epochs, learning rate $10^{-4}$ with cosine decay, and loss weights 0.5 and 0.1.[^arxiv-2601.18625]

### Interactive Query Enhancement

Given a query, IQE retrieves top-$K$ candidates and asks Qwen2.5-VL-7B to verify candidate anchors. The manuscript then proposes generated diagnostic questions, confidence-filtered attribute answers, cross-anchor confidence-weighted voting, MLLM query reconstruction, and fusion of original-query and enhanced-query similarities, optionally with an anchor bonus. Early stopping and a fallback trigger are intended to avoid unnecessary MLLM calls, while a safeguard is said to restore the original ranking if validation alignment drops substantially.[^arxiv-2601.18625]

**Synthesis:** IQE is automated pseudo-relevance feedback rather than interaction with a human user. Its main risk is confirmation bias: if the first-stage retrieval selects the wrong person, attributes inferred from that candidate can move the rewritten query farther from the intended target. Anchor verification, multi-anchor agreement, and fallback logic are intended to limit this risk, but the manuscript does not report a direct error analysis of anchor quality or hallucinated attributes.

## Reported evidence

The main comparison table reports:[^arxiv-2601.18625]

| Dataset | Rank-1 | Rank-5 | mAP |
|---|---:|---:|---:|
| CUHK-PEDES | 77.13 | 90.06 | 68.75 |
| ICFG-PEDES | 67.70 | 81.88 | 40.36 |
| RSTPReid | 68.40 | 84.95 | 51.73 |

Across six source-to-target cross-domain evaluations, CONQUER reports the highest Rank-1 among IRRA, SEN, and CONQUER, including 58.60 for CUHK-PEDES to RSTPReid and 43.27 for RSTPReid to CUHK-PEDES. It does not lead every Rank-5 or mAP comparison.[^arxiv-2601.18625]

The RSTPReid ablation table reports Rank-1/mAP of 66.50/51.47 for Base+IQE, 66.15/51.54 for Base+CARE, and 68.40/51.73 for Base+CARE+IQE. Because no Base-only row is included, the table supports complementarity of the combined system relative to either listed partial system, but cannot establish the manuscript’s claim that each module individually improves the baseline.[^arxiv-2601.18625]

These results are author-reported and were not reproduced during ingestion. The paper claims robustness to incomplete queries, but the supplied manuscript contains no incomplete-query protocol, table, or ablation. It also does not report IQE latency, MLLM call count, anchor precision, query-rewrite failure rate, or repeated-run variance.[^arxiv-2601.18625]

## Manuscript-code discrepancies

The local code mirror identifies itself as the official implementation and links arXiv:2601.18625, but inspection reveals material differences that prevent a straightforward manuscript-to-code mapping:[^conquer-code]

- The training model is still named `RDE` and closely follows dual global/token-selection embeddings with TAL-style losses. Pair cleanliness is estimated with two Gaussian mixtures; disagreements are randomly assigned rather than retained as a distinct uncertain set.
- The implemented OT rematching operates over normalized global embeddings from pairs labeled noisy, not the visual-token/text-token matrices described in the manuscript. Its loss is a symmetric KL between Sinkhorn assignments and similarity distributions. The training script weights context and rematching losses at 0.5 each, rather than the paper’s 0.5/0.1 negative/OT weights.
- IQE uses a fixed list of 15 pedestrian-attribute questions rather than generated diagnostic questions. It verifies candidates with a yes/no prompt and aggregates generated attribute sentences, but does not implement the stated answer-confidence thresholds, confidence-weighted cross-anchor voting, or validation-alignment safeguard.
- The supplied IQE shell script invokes a filename absent from the code mirror, selects `RDE` as the base model, and contains environment-specific paths. The available `IQE.py` is also not directly executable as released: it imports `build_clip_model`, which `model/__init__.py` does not export. Its remote-image branch calls `requests` without importing it.
- The pinned requirements omit runtime imports needed by the released paths, including vLLM, Transformers, Qwen VL utilities, OpenAI, and POT (`ot`); the shell script mentions only some IQE dependencies. The README names Qwen2.5-VL-7B, while the implementation loads a configurable local model through vLLM; the paper’s claimed LoRA fine-tuning procedure is not documented in the repository files inspected.

These discrepancies do not prove that the reported experiments are invalid; they mean the archived manuscript and code are insufficient to identify one unambiguous reproducible configuration.

## Source inconsistencies and limitations

- The active main table and ablation report RSTPReid Rank-5 as 84.95, while `RSTP.tex` in the same source bundle reports 82.95.
- The CARE prose defines KL alignment between the transport plan and local similarity, while the architecture caption and figure describe global similarity guiding OT; the precise global-to-local supervision path is underspecified.
- The paper says IQE uses top-$K=5$, fusion weight 0.6, and thresholds 0.90/0.85/0.85/0.5, whereas the available script defaults to five rounds, fusion weight 0.8, and anchor threshold 0.5.
- The source names only Zequn Xie as author but includes a corresponding-author email for another person and an equal-contribution footnote without identifying additional authors. Authorship metadata should be checked against the arXiv record before bibliographic reuse.
- IQE adds a 7B multimodal model and repeated visual question answering to inference. The manuscript acknowledges latency as future work but gives no cost or throughput measurements.

## Relationships

- **Evaluated against:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) is a principal in-domain and cross-domain baseline.
- **Evaluated against:** [RDE for noisy-correspondence person retrieval](rde-noisy-correspondence-person-retrieval.md) is a strong comparison point; the released CONQUER training code also retains substantial RDE structure and naming.
- **Evaluated against:** [TBPS-CLIP empirical person-search baseline](tbps-clip-empirical-person-search-baseline.md) provides another CLIP-based comparison across the same three benchmarks.

[^arxiv-2601.18625]: Zequn Xie, “CONQUER: Context-Aware Representation with Query Enhancement for Text-Based Person Search,” arXiv:2601.18625v1 / ICASSP 2026 manuscript, [`main.tex`](../raw/papers/arXiv-2601.18625v1/main.tex). Included sections, result tables, bibliography, and the CARE/IQE figures in the same source bundle were inspected.
[^conquer-code]: “CONQUER: Context-Aware Representation with Query Enhancement for Text-Based Person Search,” official code mirror, [`README.md`](../raw/codes/CONQUER/README.md). The source tree and key training/IQE paths, requirements, and launch scripts were inspected; all tracked Python files passed syntax compilation, but dependency installation, runtime execution, datasets, and pretrained weights were not validated.
