---
title: Freqtrade scope review
created: 2026-04-26
last_updated: 2026-04-26
page_type: review_item
status: draft
action_type: approve_edit
tags:
  - review
  - trading
  - crypto
  - bot
  - synthesis
visibility: private
retention_class: working
---

# Freqtrade scope review

## Decision needed
Decide whether Freqtrade should stay as a standalone project page or later be folded into a broader `trading-automation` synthesis page.

## Context
The current ingest adds a new source/project pair for the Freqtrade README/documentation. The source is a classic open-source crypto trading bot with backtesting, dry-run, WebUI, Telegram control, and exchange support. It fits the existing trading-automation cluster but is not itself LLM-centric.

## Recommendation
Keep it standalone for now. Revisit only if several more classic trading-bot sources arrive and a broader synthesis would reduce fragmentation.

## Options
- Keep standalone project/source pair
- Fold into a broader trading-automation synthesis later
- Reclassify as a topic instead of a project if future evidence suggests a more general conceptual use

## Status
Safe to defer; no immediate blocking issue.
