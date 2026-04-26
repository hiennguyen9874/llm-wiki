---
title: Source - FinRL
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - FinRL README
  - FinRL source
  - AI4Finance FinRL README
  - FinRL: Financial Reinforcement Learning → FinRL-X
tags:
  - source
  - finance
  - reinforcement-learning
  - trading
domain: finance
importance: medium
review_status: active
related_sources:
  - [[finrl]]
confidence_score: 0.79
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
  - FinRL
  - FinRL-X
  - FinRL-Trading
  - FinRL-Meta
  - AI4Finance Foundation
  - Hongyang Bruce Yang
  - Stable Baselines3
  - Yahoo Finance
  - Alpaca
  - DOW 30
  - MVO
  - DJIA
source_file: raw/apps/FinRL.md
source_type: documentation
author: AI4Finance Foundation
canonical_url: https://github.com/AI4Finance-Foundation/FinRL
---

# Source - FinRL

## What this source is
A README / documentation source for `FinRL`, the original open-source financial reinforcement learning framework from AI4Finance Foundation.

## Why it matters
This source adds a durable reference for the original finance-RL stack, including:
- the classic train-test-trade workflow
- the three-layer architecture of market environments, DRL agents, and financial applications
- broad data-source support across equities, crypto, and other market feeds
- a 2026 stock-trading tutorial that uses Yahoo Finance data and Stable Baselines3 agents
- the transition messaging that positions `FinRL-X / FinRL-Trading` as the next-generation production-oriented successor

## Key claims
#### Claim
- Statement: FinRL is the original open-source financial reinforcement learning framework maintained by the AI4Finance Foundation.
- Status: active
- Confidence: 0.94
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim from the README.

#### Claim
- Statement: FinRL is organized around a three-layer architecture: market environments, DRL agents, and financial applications.
- Status: active
- Confidence: 0.93
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: This is the most durable architectural takeaway.

#### Claim
- Statement: The repo frames FinRL as an educational and research framework, while `FinRL-X / FinRL-Trading` is presented as the newer AI-native, modular, production-oriented direction.
- Status: active
- Confidence: 0.90
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Preserve this transition explicitly rather than flattening it.

#### Claim
- Statement: The 2026 tutorial demonstrates a DOW 30 stock-trading workflow using Yahoo Finance data, technical indicators, five DRL agents, and backtesting against MVO and the DJIA.
- Status: active
- Confidence: 0.82
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Source-specific tutorial claim; keep it as a snapshot.

#### Claim
- Statement: The README documents broad data-source coverage and a historical version history that shows the project’s evolution from TensorFlow-era roots to PyTorch / Stable Baselines3.
- Status: active
- Confidence: 0.81
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Useful for understanding repo maturity and historical transitions.

#### Claim
- Statement: The source includes a trademark notice for the FinRL name and logo.
- Status: active
- Confidence: 0.97
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Governance context; preserve downstream.

## Relationships
- `FinRL` uses the train-test-trade pipeline.
- `FinRL` depends on market-environment, DRL-agent, and application layers.
- `FinRL` is adjacent to [[source-fingpt]] and [[fingpt]] because the FinGPT README explicitly references FinRL as a related AI4Finance project.
- `FinRL` is conceptually succeeded by `FinRL-X / FinRL-Trading`.

## Notes
> [!note]
> The README is broad and partly promotional, but it clearly defines the original FinRL architecture and the repo’s historical transition toward FinRL-X.

> [!warning]
> Treat benchmark, capability, and data-source breadth claims as source claims unless corroborated by code, papers, or independent replication.

## Related pages
- [[finrl]]
- [[source-fingpt]]
- [[fingpt]]
- [[overview]]
- [[index]]

## Open questions
- Should `FinRL-X / FinRL-Trading` eventually get its own canonical page if additional sources arrive?
- Which data-source support claims are still current versus historical snapshot material?
- Should the repo later anchor a broader finance-RL synthesis page if more sources accumulate?
