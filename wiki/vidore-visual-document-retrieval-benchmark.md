---
type: Benchmark
title: ViDoRe visual document retrieval benchmark
description: A page-level benchmark for visually rich document retrieval across document modalities, domains, languages, and practical retrieval tasks.
tags: [benchmark, document-retrieval, multimodal-retrieval, vision-language-models]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:45:00Z }
sources:
  - id: faysse-2024-colpali
    resource: ../raw/2407.01449_ColPali.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: faysse-2025-colpali-camera-ready
    resource: ../raw/2407.01449_ColPali/iclr2025_conference.tex
    title: ColPali: Efficient Document Retrieval with Vision Language Models
  - id: faysse-2025-colqwen2
    resource: ../raw/2407.01449_ColQwen2.md
    title: Efficient Document Retrieval with Vision Language Models
---

# ViDoRe visual document retrieval benchmark

ViDoRe evaluates page-level retrieval where a natural-language query must retrieve its relevant document page. It tests text, figures, infographics, and tables across academic and practical corpora in English and French, making visual document understanding part of retrieval evaluation rather than evaluating text embeddings alone.[^faysse-2024-colpali]

## Design

- The benchmark comprises ten retrieval tasks. Academic tasks repurpose visual-question-answering data by using each question as a query and its associated page as the relevant page; TabFQuAD adds French industrial-table retrieval.[^faysse-2024-colpali]
- Its practical tasks use topic-specific corpora of publicly accessible PDFs. For each topic, the authors collected 1,000 pages and retained 100 VLM-generated queries after human quality and relevance validation. The source describes at most three Claude-3-Sonnet question-answer pairs per page and a final manual review by four volunteer annotators; this construction should not be treated as an independent assessment of real-query distribution.[^faysse-2025-colpali-camera-ready]
- Main reported effectiveness is nDCG@5; Recall@K and MRR are also evaluated. The study additionally measures query latency and indexing throughput to represent operational retrieval constraints.[^faysse-2024-colpali]

## Scope and limits

- Candidate-corpus sizes are deliberately limited because some baseline ingestion methods, particularly captioning, can take dozens of seconds per page. Results therefore measure the supplied tasks rather than large-corpus scaling directly.[^faysse-2024-colpali]
- The practical benchmark queries were generated with Claude-3 Sonnet and then manually filtered. The paper states the source PDFs were public and that annotators flagged no PII during validation; this is a dataset-construction claim, not an independent privacy audit.[^faysse-2025-colpali-camera-ready]

## Relationships

- Evaluates: [ColPali vision-space document retrieval](colpali-vision-space-document-retrieval.md), [ColQwen2 vision-space document retrieval](colqwen2-vision-space-document-retrieval.md), and text-pipeline and vision-language retrieval baselines.[^faysse-2025-colqwen2]

[^faysse-2025-colqwen2]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2025 version), [source](../raw/2407.01449_ColQwen2.md).

[^faysse-2025-colpali-camera-ready]: Faysse et al., “ColPali: Efficient Document Retrieval with Vision Language Models” (2025 camera-ready manuscript), [source](../raw/2407.01449_ColPali/iclr2025_conference.tex).
[^faysse-2024-colpali]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2024), [source](../raw/2407.01449_ColPali.md).
