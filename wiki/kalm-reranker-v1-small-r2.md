---
type: Concept
title: KaLM-Reranker-V1-Small-R2
description: A 1B-activated-parameter multilingual T5Gemma2 reranker that compresses document states before pointwise query-conditioned scoring.
tags: [reranking, multilingual, compression, retrieval]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:42:13Z }
sources:
  - id: small-card
    resource: ../raw/KaLM-Embedding-KaLM-Reranker-V1-Small-R2.md
    kind: model-card
    title: KaLM-Reranker-V1-Small-R2 model card
---

# KaLM-Reranker-V1-Small-R2

**Reported:** KaLM-Reranker-V1-Small-R2 is an Apache-2.0, multilingual, instruction-aware text reranker with 1B activated parameters. Its fast-but-not-late-interaction (FBNL) architecture compresses document encoder states before pointwise query-conditioned yes/no scoring. The card reports 128K sequence length and 1×–128× Matryoshka embedding pooling (MEP); the illustrated inference defaults are much shorter. [^small-card]

## Architecture and training

**Reported:** Small is initialized from `google/t5gemma-2-1b-1b`, with 26 encoder and 26 decoder layers, 698M non-embedding and 302M embedding parameters, and 1,152-dimensional document token states. Mask-aware mean pooling groups consecutive encoder states before the decoder interacts with the query and task instruction; these states are not a standalone dense embedding output. Scoring is per query–document pair, not listwise or ColBERT MaxSim. [^small-card]

R2 extends validated compression from V1's 32× to 128×. The reported recipe comprises supervised fine-tuning, two soft-label distillation checkpoints (`r64-a32` and `r96-a48`), and model soup. The card lists KaLM reranker training data, KaLM embedding fine-tuning data and BGE-M3 data, but does not supply a complete training protocol. [^small-card]

## Inference and constraints

- **Reported:** Sentence Transformers `CrossEncoder` accepts `(query, document)` pairs and optional task instructions. It returns `P(yes)` by default; identity activation returns the yes-minus-no logit margin. [^small-card]
- Default truncation is 512 raw query tokens and 1,024 encoder document tokens including the document prefix, not a combined limit. `chunk_size=4` pools four states; `None` disables compression. The reported 128K model figure is not the default document limit. [^small-card]
- The card requires `sentence-transformers>=5.6,<6`, `transformers>=5.3,<6`, PyTorch and custom remote code (`trust_remote_code=True`); use trusted, pinned revisions. Training, ONNX and OpenVINO are not included in this release. [^small-card]
- An experimental single-GPU vLLM adapter is reported validated on Python 3.12, vLLM 0.19.1, Transformers 5.6.2 and CUDA BF16. It supports chunk sizes 1, 2, 4, 8, 16 and 32, narrower than the reported 128× range, and uses Transformers for the semantic forward. [^small-card]

## Reported evaluation

The following are **author-reported** average nDCG@10 scores under the card's BEIR and MIRACL reranking protocols. Benchmark versions, candidate generation, split composition and uncertainty are not fully specified in the available text; scores should not be compared directly across unrelated pipelines. MIRACL is described as an 18-language evaluation, not an exhaustive supported-language list. [^small-card]

| Compression | BEIR V1 → R2 | MIRACL V1 → R2 |
|---|---:|---:|
| 2× | 60.32 → 61.17 | 67.28 → 74.34 |
| 4× | 60.01 → 61.07 | 66.89 → 74.06 |
| 32× | 55.98 → 59.54 | 59.07 → 71.81 |
| 128× | not reported → 58.20 | not reported → 70.16 |

The card reports a Small cascade at 61.11 BEIR nDCG@10 and 2.75× estimated relative serving cost versus 61.17 and 8.65× for its baseline. The settings are in a missing figure, so this is not a reproducible deployment recipe or measured latency. [^small-card]

## Evidence and coverage limits

**Observed:** the local card and its embedded examples were inspected statically; no code was executed. Nine linked `assets/*.jpg` figures and `vllm_support/README.md` are absent at their referenced local paths. The paper, datasets, checkpoint, custom code, adapter and other external links were not inspected; decorative badges were excluded. Figure-only comparisons, ablations and cascade settings remain unavailable. The card provides no capture date or immutable revision. Performance, license and model behavior are publisher-reported and unverified; these material gaps make the concept draft. [^small-card]

## Relationships

- **Newer version of:** [KaLM-Reranker-V1-Small](kalm-reranker-v1-small.md); this does not by itself establish deprecation. [^small-card]
- **Sibling of:** [KaLM-Reranker-V1-Nano-R2](kalm-reranker-v1-nano-r2.md) and [KaLM-Reranker-V1-Large-R2](kalm-reranker-v1-large-r2.md), the smaller and larger members of the same family. [^small-card]
- **Compared with:** [Reranker model comparison](reranker-model-comparison.md), which separates different evaluation protocols.

[^small-card]: [KaLM-Reranker-V1-Small-R2 model card](../raw/KaLM-Embedding-KaLM-Reranker-V1-Small-R2.md), frontmatter; “What is KaLM-Reranker-V1-R2?”, “R2 Training Checkpoints,” “KaLM-Reranker-V1-R2 vs. the original,” “Model family,” “Prompt Template,” “Evaluation,” “Using Sentence Transformers,” “Using transformers,” and “Using vLLM.” Linked figures, paper and implementation not inspected.
