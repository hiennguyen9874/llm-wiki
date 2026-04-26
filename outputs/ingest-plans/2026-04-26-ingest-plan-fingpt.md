---
title: Ingest Plan - FinGPT
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
review_status: active
tags:
  - ingest-plan
  - source
  - finance
  - ai
  - llm
  - fintech
domain: finance
importance: medium
retention_class: episodic
visibility: private
related_sources:
  - [[source-fingpt]]
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
  - Finogrid
---

# Ingest Plan - FinGPT

## Source identity
- Source file: `raw/apps/FinGPT.md`
- Source type: documentation / repository README
- Canonical URL: `https://github.com/AI4Finance-Foundation/FinGPT`
- Why it matters: adds a durable open-source financial LLM reference to the second brain, covering data curation, LoRA fine-tuning, benchmarked sentiment / relation / NER / QA tasks, and application demos such as FinGPT-Forecaster.

## Key entities and relationships
- `FinGPT` — open-source financial LLM project maintained by AI4Finance Foundation.
- `AI4Finance Foundation` → owns / maintains `FinGPT`.
- `Hongyang (Bruce) Yang` → named contributor and visible project lead.
- `FinGPT-Forecaster` → single-task robo-advisor / stock-movement demo.
- `FinGPT-RAG` → retrieval-augmented financial sentiment workflow.
- `FinGPT-FinNLP` → broader finance NLP pipeline / playground.
- `FinGPT-Benchmark` → instruction-tuning and evaluation benchmark suite.
- `BloombergGPT` → comparator used to justify lightweight adaptation.
- `LoRA`, `RLHF`, `ChatGLM2`, `Llama2`, `Qwen`, `Falcon`, `MPT`, `Bloom`, `InternLM` → model / training ecosystem.

## Candidate claims
- FinGPT is positioned as a lightweight, open-source alternative to BloombergGPT-style closed finance models.
- The repo emphasizes automatic data curation and fast fine-tuning over expensive retraining.
- The project claims strong financial sentiment performance on a single RTX 3090 for v3 models.
- The repo includes datasets, models, tutorials, a robo-advisor demo, and ecosystem projects.
- The README is promotional, so benchmark and cost claims should be preserved but framed as source claims rather than independently verified facts.

## Related existing pages
- No existing FinGPT page found.
- Likely affected canonical pages:
  - `wiki/source-fingpt.md`
  - `wiki/fingpt.md`
  - `wiki/overview.md`
  - `wiki/index.md`
  - `wiki/log.md`

## New / reinforced / uncertain
- New: a high-level open-source financial LLM project and its ecosystem are now in scope.
- Reinforced: the wiki’s broader AI-finance cluster already includes analysis, automation, and platform sources; FinGPT extends that cluster into model/data infrastructure.
- Uncertain: how much of the README reflects current code reality versus project marketing; keep snapshot-style counts and comparisons cautious.

## Proposed edits
1. Create `wiki/source-fingpt.md` as the source page with source metadata, claim blocks, ecosystem notes, and traceability.
2. Create `wiki/fingpt.md` as the canonical project page with a durable synthesis of the project shape, key capabilities, evidence blocks, and related pages.
3. Update `wiki/overview.md` to mention the new FinGPT / open-source financial LLM branch in the current-state synthesis and known gaps.
4. Update `wiki/index.md` to add the new source and project page.
5. Append `wiki/log.md` with an ingest entry describing the addition.

## Traceability updates
- `related_sources` should be added on `wiki/fingpt.md` and reflected on any overview/index references as appropriate.
- `wiki/source-fingpt.md` should point back to `wiki/fingpt.md` as its canonical page.

## Workflow decision
- This is a substantial source, but the integration remains single-source ingest rather than a `/compile` pass.
- No later compile appears necessary unless additional FinGPT sources are ingested and a broader finance-LLM synthesis becomes useful.

## Review items
- None blocking. The only caution is source-level promotional language, which should be preserved with explicit uncertainty and confidence framing rather than treated as independently verified.

## Outputs / visuals
- No Base or Canvas appears warranted yet.
- No separate analysis output is needed beyond this ingest plan and the wiki updates.
