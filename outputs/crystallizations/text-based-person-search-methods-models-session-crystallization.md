---
title: Text-based Person Search Methods and Models Session Crystallization
created: 2026-04-23
last_updated: 2026-04-23
source_count: 9
status: reviewed
page_type: crystallization
aliases:
  - TBPS session crystallization
  - text-based person search session summary
tags:
  - machine-learning
  - multimodal
  - retrieval
  - crystallization
  - episode
  - person-retrieval
visibility: private
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2308-10045-tbps-clip
  - source-arxiv-2407-04287-mars
  - source-arxiv-2507-10195-mra
  - source-arxiv-2509-09118-ga-dms
  - source-arxiv-2601-18625-conquer
  - source-arxiv-2510-17685-bi-irra
  - source-arxiv-2604-18376-mvr
related_pages:
  - text-based-person-search-methods-models-briefing
  - text-to-image-person-retrieval
  - irra
  - tbps-clip
  - rde
  - mars
  - mra
  - ga-dms
  - conquer
  - bi-irra
  - mvr
---

# Text-based Person Search Methods and Models Session Crystallization

## Original question
User asked for a focused briefing on **text-based person search methods and models**, restricted to information already in the knowledge base, with citations to the pages informing each section. The session also later asked for a compact benchmark table showing the best method per dataset.

## What was done
1. Activated the required wiki/query workflow and used QMD to orient through the vault.
2. Began with broad task-level retrieval on [[text-to-image-person-retrieval]] rather than relying on the exact phrase in the prompt.
3. Retrieved and read the canonical method/source pages for [[irra]], [[tbps-clip]], [[rde]], [[mars]], [[mra]], [[ga-dms]], [[conquer]], [[bi-irra]], and [[mvr]].
4. Synthesized these into a reusable briefing saved at `outputs/briefings/text-based-person-search-methods-models-briefing.md`.
5. Updated [[wiki/index]] and [[wiki/log]] during the session so the new briefing was discoverable.
6. Answered the follow-up benchmark question with a dataset-specific table rather than claiming a single global winner.

## Key findings
- The vault now frames text-based person search as a **multi-lever design space**: CLIP recipe tuning ([[tbps-clip]]), pair-noise robustness ([[rde]]), attribute-aware supervision ([[mars]]), domain-aligned synthetic pretraining ([[mra]]), token-level noise handling with curated web data ([[ga-dms]]), query enhancement ([[conquer]]), multilingual supervision ([[bi-irra]]), and training-free semantic compensation ([[mvr]]).
- The best model is **dataset-dependent**, not universal.
  - **CUHK-PEDES:** [[bi-irra]] / [[source-arxiv-2510-17685-bi-irra]]
  - **ICFG-PEDES:** [[mvr]] / [[source-arxiv-2604-18376-mvr]]
  - **RSTPReid:** [[mvr]] / [[source-arxiv-2604-18376-mvr]]
- The session reinforced that benchmark history in this vault should be tracked as **time- and dataset-scoped**, because later sources supersede earlier ones on some datasets but not all.

## Affected files, pages, and entities
- `outputs/briefings/text-based-person-search-methods-models-briefing.md`
- `outputs/crystallizations/text-based-person-search-methods-models-session-crystallization.md`
- `wiki/index.md`
- `wiki/log.md`
- [[text-to-image-person-retrieval]]
- [[irra]]
- [[tbps-clip]]
- [[rde]]
- [[mars]]
- [[mra]]
- [[ga-dms]]
- [[conquer]]
- [[bi-irra]]
- [[mvr]]

## Unresolved questions
- How should future TBPS notes rank competing levers when a method combines several of them at once?
- Is there a reusable cross-benchmark rubric for comparing training-time robustness, inference-time adaptation, and data-centric pretraining?
- Should future benchmark summaries keep using dataset-specific leader tables rather than any single “current best” statement? The session suggests yes.

## Reusable lessons
- For TBPS-style questions, search both the exact task label and the broader topic label, because the vault uses multiple aliases for the same area.
- If the topic is broad, start from the task-level synthesis page and fan out to source pages instead of searching only by method names.
- When a summary is reusable, save it in `outputs/briefings/` and surface it through `wiki/index.md`.
- Treat benchmark leadership as **dataset-dependent** unless a source explicitly supports a global claim.
- HTML-based paper clips may require a quick table re-check because rendering artifacts can hide or distort benchmark values.

## Confidence and uncertainty
- Confidence in the session’s synthesis is **high** for the high-level design-space summary because it is supported by multiple canonical pages.
- Confidence is **medium-high** for the exact benchmark table values because the source pages are strong, but one MVR table contained HTML rendering noise and therefore deserves conservative reuse.
- The “best method per benchmark” answer is best treated as a **vault-local snapshot**, not a field-final ranking.

## Visibility
- **Private**: the artifact is useful for internal reuse and contains only vault-local synthesis.
- No sensitive content was introduced.

## Links back to durable knowledge
- [[text-based-person-search-methods-models-briefing]]
- [[text-to-image-person-retrieval]]
- [[bi-irra]]
- [[mvr]]
- [[conquer]]
