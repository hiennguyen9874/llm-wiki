---
type: Synthesis
title: Qwen3-VL, harrier, Qwen3, F2LLM, and Jina embedding comparison
description: A scope-aware comparison of Qwen3-VL-Embedding-2B, harrier-oss-v1-0.6b, Qwen3-Embedding-4B and 0.6B, F2LLM-v2-4B, and Jina Embeddings v5 Text Small.
tags: [embedding, retrieval, multimodal, multilingual, comparison]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T21:26:42+07:00 }
sources:
  - id: qwen3-vl-card
    resource: ../raw/Qwen3-VL-Embedding-2B.md
    title: Qwen3-VL-Embedding-2B model card
  - id: harrier-card
    resource: ../raw/harrier-oss-v1-0.6b.md
    title: harrier-oss-v1 model card
  - id: qwen3-report
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source
  - id: f2llm-report
    resource: ../raw/2603.19223_F2LLM-v2/main.tex
    title: F2LLM-v2 technical-report LaTeX source
  - id: multilingual-v2-snapshot
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
  - id: jina-v5-card
    resource: ../raw/jina-embeddings-v5-text-small.md
    title: jina-embeddings-v5-text-small model card
  - id: jina-v5-report
    resource: ../raw/2602.15547_jina-embeddings-v5-text/paper.tex
    title: Jina Embeddings v5 Text technical report
---

# Qwen3-VL, harrier, Qwen3, F2LLM, and Jina embedding comparison

[Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) is the only model in this set for cross-modal retrieval. Among the five text models in the supplied Multilingual MTEB v2 snapshot, [Qwen3-Embedding-4B](qwen3-embedding-4b.md) leads, followed by [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md); Jina Text Small, F2LLM-v2-4B, and Qwen3-Embedding-0.6B follow. Their aggregate scores support only an internal comparison within that undocumented snapshot. Qwen3-VL’s MMEB/MMTEB results use different reported evaluations and must not be ranked against it.[^qwen3-vl-card][^multilingual-v2-snapshot]

| Model | Scope | Parameters | Representation / context | Reported result | Best fit |
|---|---|---:|---|---|---|
| [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) | Text, images, screenshots, video, mixed inputs | 2B | 64–2,048-d Matryoshka; 32K tokens | MMEB-V2 73.2; MMTEB Mean (Task) 63.87 | Multimodal or visual-document retrieval |
| [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) | Multilingual text | 0.6B | 1,024-d normalized last-token; 32,768 tokens | Multilingual MTEB v2: 69.01, rank 2/45 | Best snapshot score near 0.6B; 93 declared language codes |
| [Qwen3-Embedding-4B](qwen3-embedding-4b.md) | Multilingual text and code | 4B | 32–2,560-d EOS-pooled Matryoshka; 32K tokens | Multilingual MTEB v2: 69.45, rank 1/45 | Highest supplied aggregate text score |
| [F2LLM-v2-4B](f2llm-v2.md) | Multilingual text and code | 4.022B | 2,560-d EOS-pooled Matryoshka; truncatable to at least 8-d | Multilingual MTEB v2: 67.06, rank 3/45 | Reported coverage of 282 natural and 40+ programming languages |
| [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md) | Multilingual text | 677M | 32–1,024-d last-token Matryoshka; 32,768 tokens | Snapshot: 67.00, rank 5/45; card says 67.7 MMTEB | Under-1B text model with task-specific adapters; score discrepancy requires caution |
| [Qwen3-Embedding-0.6B](qwen3-embedding-0-6b.md) | Multilingual text and code | 0.6B | 32–1,024-d EOS-pooled Matryoshka; 32K tokens | Multilingual MTEB v2: 64.34, rank 9/45 | Qwen-family small model; Apache-2.0 |

## Selection guidance

- Choose **Qwen3-VL-Embedding-2B** when queries or corpus items include images, screenshots, or video. The five other models are documented as text embedders, so their text scores do not show that they can substitute for it.[^qwen3-vl-card]
- For the highest reported text aggregate, choose **Qwen3-Embedding-4B**. Its 69.45 snapshot score is only 0.44 above harrier’s but uses roughly 6.7× the parameters.[^multilingual-v2-snapshot]
- For a compact text model, **harrier-oss-v1-0.6b** is the strongest snapshot result: 4.67 points above same-size Qwen3-Embedding-0.6B and 2.01 above the 677M Jina model. It requires a one-sentence task instruction for queries; documents have none.[^multilingual-v2-snapshot][^harrier-card]
- Choose **F2LLM-v2-4B** when its reported language/code coverage is material despite its 2.39-point snapshot gap to Qwen3-Embedding-4B. This is an inference from report metadata and the snapshot, not a controlled deployment comparison.[^f2llm-report][^multilingual-v2-snapshot]
- Consider **Jina Embeddings v5 Text Small** when its task-specific LoRA adapters or documented long-context fine-tuning matter. Its published 67.7 MMTEB claim conflicts with the 67.0 value in both its technical report and the supplied snapshot, so use the score only with that unresolved qualification.[^jina-v5-card][^jina-v5-report][^multilingual-v2-snapshot]

## Limits

- The supplied Multilingual MTEB v2 CSV does not state publisher, capture date, configuration, metric definitions, task set, or inclusion criteria. Its ranks support only an internal comparison within that artifact.[^multilingual-v2-snapshot]
- Qwen3-VL's reported MMEB-V2 score is multimodal; its MMTEB result and the text-model snapshot may differ in evaluation setup. Its model card and technical report themselves disagree on MMEB-V2 overall (73.4 versus 73.2).[^qwen3-vl-card]
- All reported benchmark and coverage claims originate from model cards, technical reports, or the supplied snapshot; none is independently reproduced here.

## Relationships

- **Compares:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md), [Qwen3-Embedding-4B](qwen3-embedding-4b.md), [F2LLM-v2](f2llm-v2.md), [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md), and [Qwen3-Embedding-0.6B](qwen3-embedding-0-6b.md).
- **Uses:** [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md) for the directly comparable text-model ranking.

[^qwen3-vl-card]: [Qwen3-VL-Embedding-2B model card](../raw/Qwen3-VL-Embedding-2B.md). Author-reported modality, dimensions, and benchmark claims.
[^harrier-card]: [harrier-oss-v1 model card](../raw/harrier-oss-v1-0.6b.md). Author-reported model size, architecture, and language claims.
[^qwen3-report]: [Qwen3 Embedding technical report](../raw/2506.05176_Qwen3Embedding/main.tex). Author-reported architecture and benchmark claims.
[^f2llm-report]: [F2LLM-v2 technical report](../raw/2603.19223_F2LLM-v2/main.tex). Author-reported architecture, coverage, and benchmark claims.
[^jina-v5-card]: [jina-embeddings-v5-text-small model card](../raw/jina-embeddings-v5-text-small.md). Author-reported model size, capability, and benchmark claims.
[^jina-v5-report]: [Jina Embeddings v5 Text technical report](../raw/2602.15547_jina-embeddings-v5-text/paper.tex). Author-reported training and evaluation claims.
[^multilingual-v2-snapshot]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied snapshot; its evaluation protocol is undocumented.
