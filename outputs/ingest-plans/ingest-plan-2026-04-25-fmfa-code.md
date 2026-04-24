---
title: Ingest Plan - FMFA Code Companion
created: 2026-04-25
last_updated: 2026-04-25
status: completed
page_type: ingest_plan
source_type: code
tags:
  - ingest-plan
  - machine-learning
  - retrieval
  - code
visibility: private
related_sources:
  - source-arxiv-2509-13754-fmfa
  - source-github-yinhao1102-fmfa
related_entities:
  - FMFA
  - IRRA
  - A-SDM
  - EFA
---

# Ingest Plan - FMFA Code Companion

## Source identity and why it matters
- Source: `raw/codes/FMFA/`
- Canonical URL: [https://github.com/yinhao1102/FMFA](https://github.com/yinhao1102/FMFA)
- Type: public GitHub code companion for [[source-arxiv-2509-13754-fmfa]]
- Why it matters: the paper ingest left implementation claims unverified. This repo can confirm whether FMFA really preserves global-feature inference, how A-SDM and EFA are operationalized, what the public recipe looks like, and whether there are reproduction caveats worth recording.

## Key entities, relationships, and candidate claims
- **FMFA codebase** `supports` [[fmfa]] and [[text-to-image-person-retrieval]].
- **IRRA scaffold** `supports` FMFA implementation lineage via shared CLIP/MLM/ID structure.
- **A-SDM** `uses` weighted SDM with similarity-gap-based upweighting for unmatched positives.
- **EFA** `uses` token-patch similarity, min-max normalization, fixed sparsity threshold, row normalization, aggregated patch embeddings, and min-max information loss.
- **Global evaluator** `supports` the claim that FMFA still ranks with normalized global text/image embeddings.
- **NAM/HAM checkpoints** `supports` the paper's two-regime story: no-ReID-domain pretraining vs ReID-domain finetuning.

## Related existing pages and likely affected pages
- Update [[fmfa]] with code-verified implementation details and caveats.
- Update [[source-arxiv-2509-13754-fmfa]] to reflect that the code companion has now been ingested.
- Update [[irra]] because FMFA now has code-level evidence for remaining inside the IRRA-family scaffold.
- Update [[text-to-image-person-retrieval]] to add the new source and strengthen the design-space synthesis.
- Update [[overview]], [[index]], and [[log]].
- Update `outputs/review-queue/fmfa-metadata-code-benchmark-followups.md` so the code-ingest subtask is marked complete and the remaining follow-ups are explicit.

## What is new, reinforced, contradicted, superseded, or uncertain
### New
- Public code confirms global-feature inference through `encode_text`, `encode_image`, feature normalization, and direct similarity ranking in `utils/metrics.py`.
- Public scripts expose two concrete recipes: `run.sh` for no ReID-domain pretraining and `finetune.sh` for checkpoint-based finetuning.
- Public code shows A-SDM and EFA implementations in `model/objectives.py` and `model/build_finetune.py`.

### Reinforced
- FMFA stays close to the IRRA family rather than introducing a new inference-time reranking architecture.
- The paper's claim that FMFA adds explicit token-patch grounding while keeping efficient inference is implementation-consistent.

### Caveats / uncertain
- The inspected snapshot contains an apparent hazard in `processor/processor.py` for the `train.py` / `do_pretrain` path: `ret` appears to be referenced without definition after `model(image, text, ori_text)`. This should be recorded as a reproduction caveat rather than a resolved fact about all released versions.
- The repo contains local/default paths and public contact metadata that should not be promoted as canonical knowledge.

## Proposed edits
- Create `wiki/source-github-yinhao1102-fmfa.md`.
- Update [[fmfa]] frontmatter, summary, evidence, and open questions.
- Update [[source-arxiv-2509-13754-fmfa]] limitations/follow-up to note that the code companion is now ingested separately.
- Update [[irra]] and [[text-to-image-person-retrieval]] with code-level FMFA lineage details.
- Refresh [[overview]], [[index]], and [[log]].
- Narrow the FMFA review queue item to remaining metadata and benchmark-taxonomy work.

## Related_sources updates needed
- [[fmfa]] → add `source-github-yinhao1102-fmfa`
- [[irra]] → add `source-github-yinhao1102-fmfa`
- [[text-to-image-person-retrieval]] → add `source-github-yinhao1102-fmfa`
- [[overview]] → add `source-github-yinhao1102-fmfa`
- [[source-arxiv-2509-13754-fmfa]] → add `source-github-yinhao1102-fmfa`

## Compile vs single-source ingest
- Stay as single-source ingest.
- Defer broader benchmark-taxonomy normalization to a later `/compile` pass after more code/source comparisons accumulate.

## Review items for human judgment
- Non-blocking: verify exact publication metadata for the FMFA paper if citation precision matters.
- Non-blocking: later normalize FMFA against MRA / GA-DMS / CONQUER / Bi-IRRA / MVR under a consistent benchmark taxonomy.
- Non-blocking: optionally validate whether the apparent `do_pretrain` hazard is a snapshot issue, a known bug, or only affects one training regime.

## Outputs / visualization decision
- Save this plan because it contains durable audit value: it closes a previously queued code-ingest follow-up, records a concrete reproduction caveat, and identifies remaining work.
- No Base or Canvas update needed yet; the TBPS method cluster remains navigable through linked markdown pages.
