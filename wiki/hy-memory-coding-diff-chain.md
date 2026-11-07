---
type: Concept
title: Hy Memory coding version-evolution diff chain
description: The zero-LLM SQLite decorator that records every revision of a code block and attaches the revision history under retrieved coding facts.
tags: [agent-memory, hy-memory, coding-memory, diff-chain, git]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory coding version-evolution diff chain

Fact extraction deliberately avoids pasting code, so a version later reverted never appears in a fact and is usually absent from HEAD; the chain stores the real diff of every version with zero LLM and zero embedding calls (`README.md::3. Coding`; `hy_memory/coding/chain_store.py` header `HyCodeMem`).[^hy-memory] It is a **decorator, not a retriever**: the vector layer chooses facts, and the chain only attaches the revisions of code each fact touches (`README.md::Design highlights`).[^hy-memory] Off by default.

## Mechanism (`coding/chain_store.py`)

- Tables `thread(owner, branch, file, symbol, pkey, lo, hi, n_rounds, body)`, `round(thread_id, seq, said, patch, adds, created_at)`, `repo_symbol` (lines 148–166).[^hy-memory]
- `observe()` drops noise/eval/final turns, obtains a patch from an in-text `diff --git`, a git lookup by commit, or a synthesised diff from `path/old/new` edit actions (with an edit-failure gate), and splits hunks by `@@` (`_pass_gate`, `_get_patch`, `_patch_from_edits`, `_split_hunks`).[^hy-memory]
- Thread key is 3-tier within `owner`: (branch, file, symbol, pkey) → (branch, file, line region) → (branch, file); regions merge within ±`HCM_LINE_MERGE`; synthetic diffs have fake line numbers, so they key by symbol only (`_upsert_thread`).[^hy-memory]
- `decorate()` attaches a block only to the first fact with usable chains (`HCM_TOPN_FACTS=1`), up to 3 chains ranked by instruction-token overlap, labelling `第N版`, revocations and `← 当前代码`, ending with a "checkout this branch first" warning; truncation order is said → code lines → body (`_render`).[^hy-memory]
- Isolation: `owner = "<user_id>|<workspace_id>"` (`client.py::_chain_owner`); empty owner matches only empty; scope filtering prevents cross-repo chains (`_in_scope`).[^hy-memory]

## Configuration

`MEMORY_CODING_CHAIN_BLOCK_ENABLED` (default **false**) and `MEMORY_CODING_CHAIN_REPO_ROOT` (`config.py:1161–1184`). `HCM_*` tunables (`HCM_CODE_LINES=6`, `HCM_CODE_CHARS=480`, `HCM_SAID_CHARS=800`, `HCM_BLOCK_CHARS=14000`, `HCM_BODY_CHARS=900`, …) are documented as non-contractual (`docs/scene_coding_usage.md` §7).[^hy-memory]

## Limits

Best-effort and regex/git-based: unparsable edits are skipped; integration swallows errors (`client.py::_observe_chain`, `_decorate_with_chain`); `chain_rounds` counts hunks, not merged rounds; facts are not removed from `facts` when a chain is attached (`docs/scene_coding_usage.md` §4).[^hy-memory] Default-off is pinned by `tests/coding/test_chain_block_config.py`.[^hy-memory]

## Relationships

- Extends: [Working and coding memory](hy-memory-working-coding-memory.md).
- Evidence for value: ablation in the [CMB benchmark](cmb-coding-memory-benchmark.md) (removing Diff drops Resolved from 35.6% to 20.8% on one backbone — Reported by the paper).

## Coverage and limits

Static inspection (delegated); the chain was not executed against a real repo.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
