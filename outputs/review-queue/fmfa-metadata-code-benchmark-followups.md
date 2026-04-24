---
title: FMFA Metadata, Code, and Benchmark Follow-ups
created: 2026-04-24
last_updated: 2026-04-25
status: open
page_type: review_item
action_type: deep_research
priority: medium
tags:
  - review-queue
  - deep-research
  - machine-learning
  - retrieval
visibility: private
related_sources:
  - source-arxiv-2509-13754-fmfa
  - source-github-yinhao1102-fmfa
related_entities:
  - FMFA
  - text-to-image person retrieval
---

# FMFA Metadata, Code, and Benchmark Follow-ups

## Trigger
The FMFA ingest plan and reviewer flagged non-blocking follow-ups after ingesting `raw/web-clips/cross-modal-full-mode-fine-grained-alignment-text-to-image-person-retrieval.md`.

## Review questions
- Verify the live arXiv metadata for arXiv `2509.13754v2`, especially exact publication date/version and formal title formatting.
- Validate whether the apparent `processor/processor.py` pretraining-path hazard noted in [[source-github-yinhao1102-fmfa]] is a snapshot-specific bug, a known issue, or a real reproduction blocker.
- Later compare [[fmfa]] against [[mra]], [[ga-dms]], [[conquer]], [[bi-irra]], and [[mvr]] under a normalized benchmark taxonomy so “best global matching method” does not get confused with overall practical leadership.

## Recommended action
The code companion ingest is complete. Run a small metadata-and-reproduction-caveat follow-up first, then defer the broader benchmark taxonomy comparison until enough new method/source pages justify a compile pass.
