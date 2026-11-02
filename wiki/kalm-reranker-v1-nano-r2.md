---
type: Concept
title: KaLM-Reranker-V1-Nano-R2
description: A 0.27B-activated-parameter multilingual T5Gemma2 reranker that compresses document states before pointwise query-conditioned scoring.
tags: [reranking, multilingual, compression, retrieval]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:41:22Z }
sources:
  - id: nano-card
    resource: ../raw/KaLM-Embedding-KaLM-Reranker-V1-Nano-R2.md
    kind: model-card
    title: KaLM-Reranker-V1-Nano-R2 model card
---

# KaLM-Reranker-V1-Nano-R2

**Reported:** KaLM-Reranker-V1-Nano-R2 is a multilingual, instruction-aware text reranker with 0.27B activated parameters and an Apache-2.0 license. Its fast-but-not-late-interaction (FBNL) architecture compresses encoded document states before query-conditioned, pointwise yes/no scoring. The card reports a 128K model sequence length and 1×–128× Matryoshka embedding pooling (MEP), but the supplied inference defaults are much shorter. [^nano-card]

## Architecture and training

**Reported:** Nano is initialized from `google/t5gemma-2-270m-270m`, with 18 encoder and 18 decoder layers, 100M non-embedding and 168M embedding parameters, and 640-dimensional document token states. These states are not a standalone dense embedding output. Mask-aware mean pooling over consecutive encoder states reduces the document representation before decoder interaction with the query and instruction. The decoder scores yes versus no for each pair, not a listwise ranking or a ColBERT MaxSim operation. [^nano-card]

R2 extends the family's validated compression range from 32× to 128×. Its reported three-stage recipe is supervised fine-tuning, soft-label distillation yielding `r64-a32` and `r96-a48` checkpoints, and model soup. The card lists KaLM reranker training data, KaLM embedding fine-tuning data, and BGE-M3 data, but not a complete training recipe. [^nano-card]

## Inference and constraints

- **Reported:** Sentence Transformers `CrossEncoder` accepts `(query, document)` pairs and an optional task-instruction prompt; its default output is `P(yes)`, while identity activation returns the yes-minus-no logit margin. [^nano-card]
- Defaults truncate raw queries at 512 tokens and encoder documents at 1,024 tokens, including the document prefix; the latter is not a combined query–document limit. `chunk_size=4` pools four states, `None` disables pooling. Do not interpret the 128K family figure as the default document limit. [^nano-card]
- The card specifies `sentence-transformers>=5.6,<6`, `transformers>=5.3,<6`, and PyTorch inference. Custom code requires `trust_remote_code=True`: use only trusted, pinned revisions. The release says training, ONNX, and OpenVINO are not included. [^nano-card]
- An experimental single-GPU vLLM adapter is reported validated with Python 3.12, vLLM 0.19.1, Transformers 5.6.2 and CUDA BF16; it supports chunk sizes 1, 2, 4, 8, 16, and 32 and runs the semantic forward through Transformers. Its supported sizes are narrower than the model family's reported 128× range. [^nano-card]

## Reported evaluation

The author's BEIR and MIRACL reranking scores are average nDCG@10, not independent verification. At `r=4`, Nano R2 scores 58.54 versus V1's 57.41 on BEIR, and 71.11 versus 62.08 on MIRACL. At 2× versus 128× compression, Nano R2 scores 58.75 versus 55.11 on BEIR and 71.63 versus 66.01 on MIRACL. The card reports that all three R2 sizes retain at least 92% of their 2× average at 128× on both benchmarks. MIRACL is described as 18-language evaluation, not a complete language-support list. [^nano-card]

Candidate generation, benchmark versions, splits and uncertainty are not fully specified in the local text; do not compare these values directly to other pipelines. The card reports a Small-model cascade cost/quality example, but its settings are in a missing figure and cannot be reproduced from the text alone. [^nano-card]

## Evidence and coverage limits

**Observed:** the local model card was inspected statically; no code was run. Nine linked `assets/*.jpg` figures and `vllm_support/README.md` are absent at their referenced local paths. The paper, datasets, model weights, custom code, adapter, and other external links were not inspected; decorative badges were excluded. Figure-only comparisons, ablations and cascade configurations therefore remain unavailable. The card has no capture date or immutable revision. Model behavior, licensing and performance remain publisher-reported and unverified; the missing evidence makes this page draft. [^nano-card]

## Relationships

- **Compared with:** [KaLM-Reranker-V1-Nano](kalm-reranker-v1-nano.md), the original V1 checkpoint used in the card's comparison. [^nano-card]
- **Sibling of:** [KaLM-Reranker-V1-Small-R2](kalm-reranker-v1-small-r2.md) and [KaLM-Reranker-V1-Large-R2](kalm-reranker-v1-large-r2.md), which use the same reported architecture and training approach at 1B and 4B activated parameters. [^nano-card]
- **Compared with:** [Reranker model comparison](reranker-model-comparison.md), a use-case guide that keeps benchmark protocols separate.

[^nano-card]: [KaLM-Reranker-V1-Nano-R2 model card](../raw/KaLM-Embedding-KaLM-Reranker-V1-Nano-R2.md), frontmatter; “What is KaLM-Reranker-V1-R2?”, “R2 Training Checkpoints,” “KaLM-Reranker-V1-R2 vs. the original,” “Model family,” “Prompt Template,” “Evaluation,” “Using Sentence Transformers,” “Using transformers,” and “Using vLLM.” Linked figures, paper, and implementation not inspected.
