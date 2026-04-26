---
title: Ingest Plan - Polymarket 5 Min Claude Code Bot are NUTS
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-polymarket-5-min-claude-code-bot-are-nuts]]
  - [[prediction-market-trading]]
  - [[moondev]]
---

# Ingest Plan - Polymarket 5 Min Claude Code Bot are NUTS

## Source identity
- Source file: `raw/articles/polymarket-5-min-claude-code-bot-are-nuts.md`
- Source type: transcript / YouTube-style demo
- Likely topic domain: prediction-market trading, short-interval backtesting, tick-data / order-flow experimentation, automated bot workflows
- Why it matters to `purpose.md`: it extends the trading-research branch from Polymarket consensus scanning into a more technical short-interval bot/backtest workflow, including 1-minute data, tick data, and CVD.

## Key entities and relationships
- Polymarket → market venue for the 5-minute markets being traded
- 5-minute markets → the target market structure the speaker says can be backtested using 1-minute data
- 1-minute data → used to infer the price to beat and backtest outcomes
- tick data → every trade / price change, used to build CVD
- CVD (cumulative volume delta) → derived order-flow signal from ticks
- MACD 3/15/3 → one of the reported profitable ideas from the backtest set
- MoonDev / Mundev → data/docs/API ecosystem referenced as the source of 1-minute data and tooling
- Claude Code → the automation tool used to build the bot

## Candidate claims
- The speaker says Polymarket 5-minute markets can be backtested with 1-minute data because the start-of-window price becomes the price to beat.
- The speaker says tick data is where the “alpha” is, and that CVD can be built from every tick / trade.
- The source reports that three ideas “print” in backtests, including MACD 3/15/3.
- The source claims one backtested idea takes 287 of 288 trades per day and has about a 60% win rate.
- The speaker explicitly warns that the result may be overfit.
- MoonDev / Mundev is referenced as the ecosystem providing data, docs, and API access.

## Existing pages likely affected
- `[[prediction-market-trading]]` — should be expanded to include short-interval backtesting and order-flow/tick-data experimentation alongside the earlier multi-model consensus workflow.
- `[[moondev]]` — likely needs another supporting claim about 1-minute market data / docs / API usage, not just liquidation data.
- `[[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]` — related Polymarket source, but different mechanism.
- `[[wiki/overview]]` — should note the Polymarket cluster now has both consensus-scanning and short-interval backtest / tick-data branches.
- `[[wiki/index]]` — add the new source page for discoverability.

## New vs reinforced vs uncertain
### New
- Backtesting 5-minute Polymarket markets using 1-minute data.
- Tick-data / CVD framing as the allegedly higher-resolution edge.
- A source-local MACD / 60% win-rate claim on very high trade frequency.

### Reinforced
- Polymarket is becoming a durable trading-research cluster, not just a one-off transcript.
- MoonDev / Mundev appears again as a recurring tooling/data reference in trading workflows.
- The vault’s trading pages should separate promotional claims from durable reusable mechanics.

### Uncertain
- The reported win rate, trade count, and “prints” language are likely overfit or source-local until independently validated.
- It is unclear whether CVD deserves its own canonical concept page now or should remain embedded under prediction-market-trading until reinforced by more sources.
- The exact data-access path for the 1-minute / tick data is not fully specified in the transcript.

## Proposed page actions
### Source page
Create a dedicated source page in `wiki/` with:
- source metadata
- concise summary of the bot/backtest and order-flow workflow
- claim blocks for the 5-minute backtest method, CVD/tick-data method, profitable-idea claim, and overfit warning
- open questions around robustness, data access, and whether the edge survives out of sample
- related pages linking to `prediction-market-trading` and `moondev`

### Canonical page updates
Update `prediction-market-trading` to add:
- a second branch: short-interval backtesting / tick-data / order-flow experimentation
- explicit separation between consensus-scanning workflows and execution/backtest workflows
- a new evidence block grounded in this source

Update `moondev` to add:
- 1-minute / tick-data references
- docs/API/tooling role in Polymarket bot experimentation

## Traceability updates
- Add `related_sources` on `[[prediction-market-trading]]` and `[[moondev]]` to include the new source.
- Add `related_sources` on the new source page to `[[prediction-market-trading]]`, `[[moondev]]`, and the earlier Polymarket transcript.
- Preserve the raw source unchanged.

## Review items
1. Should the 60% win-rate / 287-of-288-trades claim be treated as a durable claim or as a source-local promotional result?
   - Recommendation: source-local / low-confidence until validated.
2. Should CVD become its own canonical concept page now?
   - Recommendation: not yet; keep it inside the Polymarket/trading cluster unless another source reinforces it.
3. Should this source trigger a follow-up robustness note or future compile task for Polymarket short-interval bot research?
   - Recommendation: yes, capture a review item for overfit / out-of-sample validation.

## Integration scope
- Single-source ingest is sufficient, but this source broadens the existing Polymarket cluster.
- No `/compile` pass is required yet unless more short-interval prediction-market sources arrive.
- No Canvas/Base is needed right now.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because it documents a non-trivial cluster expansion and a likely review item.
- Create a review-queue item for robustness / overfit risk.
- Update `wiki/log.md` after integration.
- Update `wiki/index.md` for the new source page.
- Refresh `wiki/overview.md` to reflect the Polymarket short-interval branch.
