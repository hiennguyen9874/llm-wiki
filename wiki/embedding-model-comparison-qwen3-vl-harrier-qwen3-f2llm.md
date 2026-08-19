---
type: Synthesis
title: Qwen3-VL, harrier, Qwen3, and F2LLM 4B embedding comparison
description: A scope-aware comparison of Qwen3-VL-Embedding-2B, harrier-oss-v1-0.6b, Qwen3-Embedding-4B, and F2LLM-v2-4B for multimodal versus multilingual text embedding.
tags: [embedding, retrieval, multimodal, multilingual, comparison]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T00:00:00Z }
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
---

# Qwen3-VL, harrier, Qwen3, and F2LLM 4B embedding comparison

[Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) is the only model here for cross-modal retrieval; [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) is the strongest text-only option per parameter in the supplied Multilingual MTEB v2 snapshot; and [Qwen3-Embedding-4B](qwen3-embedding-4b.md) leads that snapshot, narrowly ahead of harrier. [F2LLM-v2-4B](f2llm-v2.md) is a text-only 4B family member that trails both on that aggregate but reports broader stated natural-language and code coverage. These are different reported evaluations, so the VL model's MMEB/MMTEB scores must not be ranked against the text-only snapshot.[^qwen3-vl-card][^multilingual-v2-snapshot][^f2llm-report]

| Model | Scope | Parameters | Representation / context | Reported comparable result | Best fit |
|---|---|---:|---|---|---|
| [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) | Text, images, screenshots, video, and mixed inputs | 2B | 64–2,048-d Matryoshka; 32K tokens | MMEB-V2 73.2; MMTEB Mean (Task) 63.87 | Multimodal or visual-document retrieval |
| [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) | Multilingual text | 0.6B | 1,024-d last-token pooled; 32,768 tokens | Multilingual MTEB v2: 69.01, rank 2/45 | Lowest-compute text option here; 93 declared language codes |
| [Qwen3-Embedding-4B](qwen3-embedding-4b.md) | Multilingual text | 4B | 2,560-d EOS-pooled Matryoshka; 32K tokens | Multilingual MTEB v2: 69.45, rank 1/45 | Best reported aggregate text score in this set |
| F2LLM-v2-4B | Multilingual text and code | 4.022B | 2,560-d EOS-pooled Matryoshka; truncatable to at least 8-d | Multilingual MTEB v2: 67.06, rank 3/45 | Text/code coverage priority; report claims 282 natural and 40+ programming languages |

## Selection guidance

- Choose **Qwen3-VL-Embedding-2B** when queries or corpus items include images, screenshots, or video. The other three documented models are text embedding models, so their reported text benchmark scores do not establish that they can substitute for it.[^qwen3-vl-card]
- For text-only multilingual retrieval, choose **Qwen3-Embedding-4B** when the reported 0.44-point Mean (Task) lead over harrier justifies roughly 6.7× as many parameters; choose **harrier-oss-v1-0.6b** when its much smaller size is the priority.[^multilingual-v2-snapshot]
- Choose **F2LLM-v2-4B** only when its reported language/code training coverage or its family training design matters more than the supplied snapshot's 2.39-point gap to Qwen3-Embedding-4B. This is an inference from reported metadata and the snapshot, not a controlled deployment comparison.[^f2llm-report][^multilingual-v2-snapshot]

## Limits

- The supplied Multilingual MTEB v2 CSV does not state publisher, capture date, configuration, metric definitions, task set, or inclusion criteria. Its ranks support only an internal comparison within that artifact.[^multilingual-v2-snapshot]
- Qwen3-VL's reported MMEB-V2 score is multimodal; its MMTEB result and the text-model snapshot may differ in evaluation setup. Its model card and technical report themselves disagree on MMEB-V2 overall (73.4 versus 73.2).[^qwen3-vl-card]
- All reported benchmark and coverage claims originate from model cards, technical reports, or the supplied snapshot; none is independently reproduced here.

## Relationships

- **Compares:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md), [Qwen3-Embedding-4B](qwen3-embedding-4b.md), and [F2LLM-v2](f2llm-v2.md).
- **Uses:** [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md) for the directly comparable text-model ranking.

[^qwen3-vl-card]: [Qwen3-VL-Embedding-2B model card](../raw/Qwen3-VL-Embedding-2B.md). Author-reported modality, dimensions, and benchmark claims.
[^harrier-card]: [harrier-oss-v1 model card](../raw/harrier-oss-v1-0.6b.md). Author-reported model size, architecture, and language claims.
[^qwen3-report]: [Qwen3 Embedding technical report](../raw/2506.05176_Qwen3Embedding/main.tex). Author-reported architecture and benchmark claims.
[^f2llm-report]: [F2LLM-v2 technical report](../raw/2603.19223_F2LLM-v2/main.tex). Author-reported architecture, coverage, and benchmark claims.
[^multilingual-v2-snapshot]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied snapshot; its evaluation protocol is undocumented.
