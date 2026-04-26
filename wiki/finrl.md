---
title: FinRL
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - AI4Finance FinRL
  - FinRL framework
  - FinRL README
tags:
  - finance
  - ai
  - reinforcement-learning
  - trading
  - quant-finance
domain: finance
importance: high
review_status: active
related_sources:
  - [[source-finrl]]
confidence_score: 0.84
quality_score: 0.86
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
  - Hongyang Bruce Yang
  - FinRL-Meta
  - FinRL-X
  - FinRL-Trading
  - market environments
  - DRL agents
  - financial applications
  - Stable Baselines3
  - Yahoo Finance
  - Alpaca
  - MVO
  - DJIA
---

# FinRL

## Summary
FinRL is the original open-source financial reinforcement learning framework from the AI4Finance Foundation. The durable takeaways are the classic train-test-trade workflow, the three-layer architecture, and the educational / research orientation of the original repo.

The README now also positions `FinRL-X / FinRL-Trading` as the next-generation AI-native, modular, production-oriented successor. That makes FinRL useful both as a historical foundation and as a reference implementation for the original finance-RL stack.

> [!note]
> Preserve the distinction between the original FinRL framework and the newer FinRL-X messaging. The repo is not just a generic trading repo; it is a specific lineage with historical transitions.

## Key capabilities
### Core architecture
- market environments
- DRL agents
- financial applications
- train-test-trade workflow

### Training and experimentation
- classic stock-trading tutorials
- Stable Baselines3-based DRL training
- backtesting against benchmark strategies
- research/prototyping emphasis

### Data-source ecosystem
- Yahoo Finance and other equities feeds
- Alpaca and other trading interfaces
- crypto and global market-source adapters
- wide README-level catalog of supported providers

### Ecosystem / lineage
- FinRL-Meta as the related market-environment and benchmark branch
- FinRL-X / FinRL-Trading as the production-oriented successor path
- adjacent AI4Finance finance tooling, including [[fingpt]]

## Evidence / claims
#### Claim
- Statement: FinRL is the original open-source financial reinforcement learning framework maintained by the AI4Finance Foundation.
- Status: active
- Confidence: 0.94
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim.

#### Claim
- Statement: FinRL is organized around market environments, DRL agents, and financial applications.
- Status: active
- Confidence: 0.93
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Stable architecture summary.

#### Claim
- Statement: FinRL is framed primarily as an educational and research framework, while `FinRL-X / FinRL-Trading` is presented as the newer production-oriented direction.
- Status: active
- Confidence: 0.90
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Important for lifecycle / lineage.

#### Claim
- Statement: The README’s 2026 stock-trading tutorial uses Yahoo Finance data, technical indicators, five DRL agents, and benchmark backtests against MVO and the DJIA.
- Status: active
- Confidence: 0.82
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Tutorial-specific snapshot.

#### Claim
- Statement: The repo documents broad data-source support and a historical evolution from earlier TensorFlow-era releases to PyTorch / Stable Baselines3.
- Status: active
- Confidence: 0.81
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Useful context, but still source-anchored.

#### Claim
- Statement: The README includes a trademark notice for the FinRL name and logo.
- Status: active
- Confidence: 0.97
- Evidence: [[source-finrl]]
- Last confirmed: 2026-04-26
- Notes: Governance context.

## Relationships
- `FinRL` depends on the train-test-trade pipeline.
- `FinRL` supports the classic finance-RL stack across environment, agent, and application layers.
- `FinRL` is adjacent to [[fingpt]] and [[source-fingpt]] because both belong to the AI4Finance finance toolchain.
- `FinRL` is conceptually succeeded by `FinRL-X / FinRL-Trading`.

## Notes
> [!warning]
> The README mixes current branding, historical version history, and successor positioning. Keep those distinctions visible in downstream notes.

> [!info]
> The repo is most useful here as a canonical reference for the original FinRL architecture and its training / backtesting flow.

## Related pages
- [[source-finrl]]
- [[source-fingpt]]
- [[fingpt]]
- [[overview]]
- [[index]]

## Open questions
- Should `FinRL-X / FinRL-Trading` become its own canonical page if more sources arrive?
- Which README data-source claims are still current in code versus historical documentation?
- Should the wiki later add a broader finance-RL synthesis page if this branch grows?
