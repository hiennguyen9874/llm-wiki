---
type: Concept
title: KaLM-Reranker-V1-Large-R2
description: A 4B-activated-parameter T5Gemma2 multilingual pointwise reranker that compresses document token states before query-conditioned scoring.
tags: [reranking, multilingual, compression, retrieval]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:41:22Z }
sources:
  - id: kalm-card
    resource: ../raw/KaLM-Embedding-KaLM-Reranker-V1-Large-R2.md
    kind: model-card
    title: KaLM-Reranker-V1-Large-R2 model card
---

# KaLM-Reranker-V1-Large-R2

KaLM-Reranker-V1-Large-R2 is a multilingual text reranker using a T5Gemma2 encoder–decoder and “fast but not late interaction” (FBNL): document states are compressed before the decoder scores each query–document pair. **Reported:** the Large checkpoint has 4B activated parameters, supports instruction-aware scoring and 1×–128× Matryoshka embedding pooling (MEP), and is Apache-2.0 licensed. Its 128K model sequence-length figure is distinct from the much shorter defaults in the provided inference interface. [^kalm-card]

## Architecture and family

**Reported:** Large starts from `google/t5gemma-2-4b-4b`; its 34 encoder plus 34 decoder layers have 3,209M non-embedding and 675M embedding parameters, with 2,560-dimensional document token states. These are document representations, not a standalone dense embedding output. MEP averages consecutive encoder states with masking before decoder interaction; a larger chunk size reduces the number of document states. Query, task instruction, and document are formatted separately, and the decoder chooses between yes and no. This is pointwise scoring rather than listwise ranking or ColBERT-style MaxSim. [^kalm-card]

The R2 family also includes Nano (0.27B activated, 18+18 layers, 640-dimensional document states) and Small (1B activated, 26+26 layers, 1,152 dimensions); the card reports 128K sequence length and 1×–128× MEP for all three. R2 retains the V1 architecture while extending validated compression from 32× to 128×. The reported training sequence is supervised fine-tuning, two soft-label distillation checkpoints, and their model soup; the card lists reranker and embedding finetuning datasets plus BGE-M3 data, but does not provide a complete reproducible training protocol. [^kalm-card]

## Usage and constraints

- **Reported interface:** Sentence Transformers `CrossEncoder` expects `(query, document)` pairs and supports a task-instruction prompt. The default output is `P(yes)`; identity activation returns the yes-minus-no logit margin. [^kalm-card]
- The illustrated defaults truncate raw queries to 512 tokens and documents to 1,024; the latter includes the document prefix, not a combined query–document limit. `chunk_size=4` is the example default; `None` disables pooling. Thus the 128K family figure does not mean the example processes 128K-token documents without configuration changes. [^kalm-card]
- The card specifies `sentence-transformers>=5.6,<6`, `transformers>=5.3,<6`, PyTorch and custom remote code (`trust_remote_code=True`); load only trusted revisions. The release describes PyTorch inference only, not training, ONNX, or OpenVINO. The examples were inspected but not executed. [^kalm-card]
- An experimental single-GPU vLLM adapter is reported tested with Python 3.12, vLLM 0.19.1, Transformers 5.6.2 and CUDA BF16. It supports chunk sizes 1–32, not the full 128× MEP range, and still runs the T5Gemma2 semantic forward through Transformers. Its external plugin and guide were not inspected. [^kalm-card]

## Reported evaluation

The following are **author-reported** average nDCG@10 scores, on the card's BEIR and MIRACL reranking evaluations, at `r=4`. The source does not fully specify candidate generation, dataset versions, split composition, or uncertainty in the text available here; do not compare numbers with unrelated benchmark pipelines. MIRACL is described as covering 18 languages, not an exhaustive statement of supported languages. [^kalm-card]

| Size | BEIR V1 → R2 | MIRACL V1 → R2 |
|---|---:|---:|
| Nano | 57.41 → 58.54 | 62.08 → 71.11 |
| Small | 60.01 → 61.07 | 66.89 → 74.06 |
| Large | 62.87 → 63.53 | 70.07 → 74.92 |

For Large R2, reported BEIR falls from 63.69 at 2× to 61.23 at 128×, and MIRACL from 75.12 to 71.97. For all three sizes the card reports at least 92% retention relative to 2× on both benchmarks at 128×. It also reports a Small-model BEIR cascade example of 61.11 nDCG@10 at estimated relative serving cost 2.75× versus 61.17 at 8.65× for its baseline; the specific cascade settings are in an unavailable figure, so the result is not a reproducible deployment recipe. [^kalm-card]

## Evidence and coverage limits

**Observed:** the supplied local model card was inspected statically. Its nine linked `assets/*.jpg` figures and `vllm_support/README.md` are absent at the referenced local paths; paper, datasets, model weights, custom code, adapter, and other external links were not inspected. The card's figure-only comparisons, ablations, and cascade configuration therefore cannot be checked. Decorative badge images were excluded. The card does not provide a capture date or immutable revision. Reported scores, license, operational claims, and model behavior remain unverified; no model or example was run. These material gaps make the concept draft. [^kalm-card]

## Relationships

- **Sibling of:** [KaLM-Reranker-V1-Nano-R2](kalm-reranker-v1-nano-r2.md) and [KaLM-Reranker-V1-Small-R2](kalm-reranker-v1-small-r2.md), the 0.27B and 1B activated-parameter members of the same R2 family. [^kalm-card]
- **Newer version of:** [KaLM-Reranker-V1-Large](kalm-reranker-v1-large.md); R2 extends the reported compression range from 32× to 128×. [^kalm-card]
- **Compared with:** [Reranker model comparison](reranker-model-comparison.md) places this compression-oriented option alongside other rerankers without merging their benchmark protocols.
- **Contrasts with:** [jina-reranker-v3.5](jina-reranker-v3-5.md) performs listwise ranking; KaLM scores query–document pairs individually. [^kalm-card]

[^kalm-card]: [KaLM-Reranker-V1-Large-R2 model card](../raw/KaLM-Embedding-KaLM-Reranker-V1-Large-R2.md), frontmatter; “What is KaLM-Reranker-V1-R2?”, “R2 Training Checkpoints,” “KaLM-Reranker-V1-R2 vs. the original,” “Model family,” “Prompt Template,” “Evaluation,” “Using Sentence Transformers,” “Using transformers,” and “Using vLLM.” Publisher-reported; linked paper, figures, and implementation not inspected.
