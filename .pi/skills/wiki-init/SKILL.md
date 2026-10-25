---
name: wiki-init
description: Initialize or re-scope a knowledge base from this repository by writing SCOPE.md, then hand off to ingest or query.
disable-model-invocation: true
---

# Wiki Init

Turn this repository into a specific knowledge base: settle `SCOPE.md` first, then continue with the user's first ingest or query under that scope. `SCOPE.md` is the only file this skill writes, apart from confirmed inherited-content clearing. When the user wants a second, unrelated KB, recommend a fresh copy of the base repository instead of widening this scope.

## Steps

1. **Inspect the starting point.** From the repository root, read the current `SCOPE.md`, `wiki/index.md`, and the list of course profiles in `.pi/skills/wiki-learn/references/profiles/`. Classify the wiki state under the contract and inventory `raw/`. Classify the run:
   - **Fresh:** no concepts and no raw sources; `SCOPE.md` is absent or still the base default.
   - **Re-scope:** this KB already has concepts or sources and the user wants to change its scope.
   - **Inherited:** concepts or sources came from the copied base repository and don't belong to the new KB.

   This step is complete when the branch, wiki state, and any existing content are explicit.

2. **Elicit the scope.** Derive every `SCOPE.md` field from the user's request and any named sources: name, purpose, inclusion test, exclusions, initial domains with focus and rules, domain-to-course-profile mapping, interaction mode, concept prose language, and course prose language. Ask one batch of questions only for fields that can't be derived and would change meaning, privacy, or exclusions; offer the current value as the default for the rest. Map each domain to an existing course profile, or to `general` when none fits; create a new profile only when the user asks. This step is complete when every field has a value and a stated origin: user, derived, or default.

3. **Draft and check.** Write the proposed `SCOPE.md` in the existing file's section structure and show it as a diff against the current file. Check that it only refines `AGENTS.md`: provenance, privacy screening, validation, and human approval all survive. For **re-scope**, list existing concepts that fall outside the new scope or break new domain rules; leave them in place and route them to `wiki-lint`. For **inherited**, list the inherited `raw/` and `wiki/` content and propose clearing it as a separate, explicitly confirmed step (the one exception to `raw/` immutability); clearing resets `wiki/` to uninitialized and empties `raw/`. This step is complete when the diff, contract check, and any affected-content list are ready.

4. **Confirm and write.** Present the draft for approval: the scope defines this KB's governance, so confirmation is required in both interaction modes. Apply requested revisions and re-check. Write `SCOPE.md`; perform any confirmed inherited-content clearing; create no wiki scaffold and no log entry, since the first ingest creates them and Git records the scope change. This step is complete when the approved `SCOPE.md` is on disk and `python3 tools/wiki_check.py` reports a valid state, or reports uninitialized after a clear.

5. **Hand off.** When the request includes a source or question, continue with `wiki-ingest` or `wiki-query` under the new scope; they re-read `SCOPE.md` in their first step. Otherwise report the scope summary and the next useful command. This step is complete when the handoff ran, or the user has the summary and next step.
