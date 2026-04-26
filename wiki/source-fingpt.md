---
title: Source - FinGPT
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - FinGPT README
  - FinGPT source
  - FinGPT: Open-Source Financial Large Language Models
  - AI4Finance FinGPT README
tags:
  - source
  - finance
  - ai
  - llm
  - fintech
  - nlp
domain: finance
importance: medium
review_status: active
related_sources:
  - [[fingpt]]
confidence_score: 0.78
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - FinGPT
  - AI4Finance Foundation
  - Hongyang Bruce Yang
  - FinGPT-Forecaster
  - FinGPT-RAG
  - FinGPT-FinNLP
  - FinGPT-Benchmark
  - BloombergGPT
  - LoRA
  - RLHF
  - Llama2
  - ChatGLM2
  - Qwen
  - Falcon
  - MPT
  - Bloom
  - InternLM
  - Finogrid
source_file: raw/apps/FinGPT.md
source_type: documentation
author: AI4Finance Foundation
canonical_url: https://github.com/AI4Finance-Foundation/FinGPT
---

# Source - FinGPT

## What this source is
A README / documentation source for `FinGPT`, an open-source financial large language model project maintained by the AI4Finance Foundation.

## Why it matters
This source adds a durable reference for the finance-LLM layer of the wiki. It is not just about one model; it describes a broader stack:
- financial data curation and instruction tuning
- LoRA-based fine-tuning and lightweight adaptation
- sentiment, relation extraction, headline classification, NER, QA, and Chinese multiple-choice benchmarks
- a robo-advisor / forecasting demo
- a surrounding ecosystem of datasets, tutorials, and application layers

## Key claims
#### Claim
- Statement: FinGPT is an open-source financial LLM project developed and maintained by the AI4Finance Foundation.
- Status: active
- Confidence: 0.92
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim from the README.

#### Claim
- Statement: The project argues that finance is highly dynamic, so lightweight adaptation and frequent updates are preferable to expensive retraining.
- Status: active
- Confidence: 0.86
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: This is the central rationale for the project.

#### Claim
- Statement: FinGPT emphasizes automatic data curation, instruction tuning, LoRA fine-tuning, and RLHF-oriented personalization for finance use cases.
- Status: active
- Confidence: 0.84
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Preserve the technical framing, but keep the RLHF claim as the README presents it.

#### Claim
- Statement: The README presents FinGPT v3 sentiment models as highly cost-efficient and competitive on standard financial sentiment benchmarks, including comparisons to GPT-4, FinBERT, Llama2-7B, OpenAI fine-tune, and BloombergGPT.
- Status: active
- Confidence: 0.73
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Strong promotional / benchmark claim; keep it source-backed rather than independently verified.

#### Claim
- Statement: FinGPT-Forecaster is framed as a robo-advisor / stock-movement demo that combines ticker input, historical news retrieval, and optional financials to produce a prediction-oriented analysis.
- Status: active
- Confidence: 0.80
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Durable demo-level capability.

#### Claim
- Statement: The ecosystem includes datasets, base-model comparisons, tutorials, and subprojects such as FinGPT-RAG, FinGPT-FinNLP, and FinGPT-Benchmark.
- Status: active
- Confidence: 0.85
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: This is the source’s biggest structural contribution.

#### Claim
- Statement: The README includes a disclaimer that the code is for academic purposes and is not financial advice or a recommendation to trade real money.
- Status: active
- Confidence: 0.97
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Keep this visible downstream.

## Relationships
- `FinGPT` uses a layered stack: data source layer, data engineering layer, LLM layer, task layer, and application layer.
- `FinGPT` depends on lightweight adaptation methods such as LoRA and on a broad benchmark / dataset ecosystem.
- `FinGPT` is adjacent to [[fingpt]] because the project page should hold the durable synthesis of the same source.
- `FinGPT` is adjacent to [[fincept-terminal]], [[daily-stock-analysis]], [[vibe-trading]], and [[tradingagents]] because all sit in the broader AI-finance tooling space.

## Notes
> [!info]
> The README is broad and promotional, but it clearly defines a coherent finance-LLM ecosystem. The durable takeaways are the project architecture, datasets, benchmarks, and application layers.

> [!warning]
> Snapshot benchmark numbers and cost comparisons should be treated as source claims until corroborated by code, papers, or independent replication.

## Related pages
- [[fingpt]]
- [[fincept-terminal]]
- [[daily-stock-analysis]]
- [[vibe-trading]]
- [[tradingagents]]

## Open questions
- Which model, dataset, and benchmark claims are still current versus historical snapshot material?
- Should FinGPT later anchor a broader `financial-llm` or `finance-ai` synthesis page if more sources accumulate?
- Are the cloud-provider inference notes durable product guidance or just a Finogrid-specific integration snapshot?
