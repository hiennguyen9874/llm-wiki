---
title: FinGPT
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - FinGPT project
  - AI4Finance FinGPT
  - FinGPT: Open-Source Financial Large Language Models
tags:
  - finance
  - ai
  - llm
  - fintech
  - nlp
  - machine-learning
domain: finance
importance: high
review_status: active
related_sources:
  - [[source-fingpt]]
confidence_score: 0.80
quality_score: 0.85
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: working
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - AI4Finance Foundation
  - FinRL
  - Hongyang Bruce Yang
  - FinGPT-Forecaster
  - FinGPT-RAG
  - FinGPT-FinNLP
  - FinGPT-Benchmark
  - FinRL-Meta
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
---

# FinGPT

## Summary
FinGPT is an open-source financial large language model project maintained by the AI4Finance Foundation. The README presents it as a finance-specific LLM ecosystem built around lightweight adaptation, frequent updates, and a layered workflow that connects data curation, model fine-tuning, benchmark tasks, and application demos.

The durable takeaway is not a single model release; it is the platform shape: finance data pipelines, LoRA-based adaptation, task-specific instruction tuning, and downstream products such as FinGPT-Forecaster and FinGPT-RAG.

> [!note]
> The repository is highly promotional. Preserve the architecture and benchmark claims, but treat cost and leaderboard-style comparisons as source claims rather than independently verified conclusions.

## Key capabilities
### Core positioning
- open-source financial LLM project
- designed for dynamic finance use cases that need frequent updates
- emphasizes lightweight adaptation over expensive retraining

### Training and adaptation
- automatic data curation pipeline
- instruction tuning
- LoRA fine-tuning
- RLHF-oriented personalization framing

### Datasets and benchmarks
- sentiment analysis training instructions
- financial relation extraction
- financial headline analysis
- financial named-entity recognition
- financial QA
- Chinese multiple-choice evaluation
- benchmark comparisons across base models and SFT variants

### Application layer
- FinGPT-Forecaster robo-advisor / stock-movement demo
- retrieval-augmented financial sentiment workflows via FinGPT-RAG
- broader finance NLP playground via FinGPT-FinNLP
- benchmark and evaluation infrastructure via FinGPT-Benchmark

### Model ecosystem
- base-model coverage across Llama2, Falcon, MPT, Bloom, ChatGLM2, Qwen, and InternLM
- sentiment-focused LoRA models and multi-task variants
- local and cloud inference notes in the README

## Evidence / claims
#### Claim
- Statement: FinGPT is an open-source financial LLM project developed and maintained by the AI4Finance Foundation.
- Status: active
- Confidence: 0.92
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim.

#### Claim
- Statement: The project’s central design choice is lightweight adaptation for a highly dynamic finance domain, rather than periodic full retraining.
- Status: active
- Confidence: 0.86
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: This is the key architectural rationale.

#### Claim
- Statement: FinGPT’s ecosystem centers on data curation, instruction tuning, LoRA fine-tuning, and benchmark-driven evaluation.
- Status: active
- Confidence: 0.85
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Stable synthesis of the README.

#### Claim
- Statement: The README presents a v3 sentiment stack with strong benchmark results and low fine-tuning cost on a single RTX 3090.
- Status: active
- Confidence: 0.74
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Keep benchmark and cost figures as source claims.

#### Claim
- Statement: FinGPT-Forecaster extends the project into a robo-advisor-style stock-analysis demo that uses ticker/date/news/financial inputs.
- Status: active
- Confidence: 0.80
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Important because it shows the project is not only model infrastructure.

#### Claim
- Statement: The README includes a disclaimer that the code is for academic purposes and is not financial advice.
- Status: active
- Confidence: 0.97
- Evidence: [[source-fingpt]]
- Last confirmed: 2026-04-26
- Notes: Important governance context.

## Relationships
- `FinGPT` depends on a layered architecture: data source layer, data engineering layer, LLM layer, task layer, and application layer.
- `FinGPT` uses LoRA and instruction tuning to adapt base models to finance tasks.
- `FinGPT` is adjacent to [[finrl]], [[source-finrl]], [[fincept-terminal]], [[daily-stock-analysis]], [[vibe-trading]], and [[tradingagents]] as part of a broader AI-finance tooling cluster.
- `FinGPT` is conceptually related to [[overview]] because it expands the wiki from trading-automation tools into finance-LLM infrastructure.

## Open questions
- Which benchmark numbers and cost claims are worth tracking as durable facts versus historical snapshots?
- Should this become part of a broader finance-LLM synthesis page if more sources arrive?
- Are the cloud-provider notes a project-specific deployment detail or a reusable pattern for future finance agents?

## Related pages
- [[source-fingpt]]
- [[finrl]]
- [[source-finrl]]
- [[fincept-terminal]]
- [[daily-stock-analysis]]
- [[vibe-trading]]
- [[tradingagents]]
- [[overview]]
- [[index]]
