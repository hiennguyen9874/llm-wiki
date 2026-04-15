# PI Hook Recommend Update

## Quick read on the current design

Your repo is already shaped the right way for hooks:

- **prompts are thin entry points**
- **skills hold the real workflow policy**
- **repo stance is manual-first, human-steered**
- hooks should mainly help with:
  - routing
  - reminders
  - guardrails
  - verification
  - scheduled follow-up

Also: there is **currently no local `.pi/extensions/` hook implementation yet**. `.pi/settings.json` only has packages; no project hook code exists.

---

## What pi hook support is actually useful here

From `docs/pi-hook.md` + pi docs, the hooks that matter most for this repo are:

- `input`
- `session_start`
- `before_agent_start`
- `tool_call`
- `tool_result`
- `agent_end`
- `session_before_compact`
- `session_shutdown`

And two related patterns:

- **bash `spawnHook`** if you want to wrap bash behavior specifically
- **external trigger + extension** for scheduled/event-driven workflows
  - e.g. `fs.watch`, cron, or the `file-trigger.ts` example

For this repo, **extensions via `.pi/extensions/*.ts` are the right mechanism**.  
I would **not** use SDK `session.subscribe(...)` unless you’re embedding pi in another app.

---

# Best hook opportunities for this repo

## 1. Input routing: move workflow selection into hooks
This is the cleanest first win.

### Use `input`
Detect common inputs and rewrite them to the correct prompt flow:

- plain URL → `/ingest-url <url>`
- `raw/...` path → `/ingest <path>`
- “review” → `/review`
- “lint” → `/lint`
- “what do we know about X” → maybe rewrite to `/query X` if you want explicit routing

### Why it fits
Your prompts are intentionally thin. This means hooks can improve ergonomics without moving the real workflow logic out of skills.

### Recommendation
Keep this **explicit and predictable**.  
Good:
- URL/path detection
- a few shorthand aliases

Bad:
- too much “magic” natural-language rewriting

---

## 2. Session-start automation: reminders and context loading
This is probably the next best use.

### Use `session_start`
On startup/resume/reload:

- inspect `wiki/log.md`
- check if review/lint/privacy/retention passes are overdue
- count pending files in:
  - `raw/inbox/`
  - `raw/captures/`
- optionally show:
  - “you have 5 unprocessed captures”
  - “last lint was 26 days ago”
  - “recent crystallization exists but not promoted”

### Optional behavior
If you want, the hook can:
- just `ctx.ui.notify(...)`
- or ask whether to run:
  - `/session-start`
  - `/review`
  - `/ingest-batch raw/inbox`

### Why it fits
This supports the repo’s existing `session-start`, `review`, and maintenance prompts without making them invisible automation.

---

## 3. Raw inbox watcher: event-driven ingest queue
This is a good semi-automatic hook.

### Use `session_start` + `fs.watch(...)`
Like pi’s `examples/extensions/file-trigger.ts`:

- watch `raw/inbox/`, `raw/captures/`, maybe `raw/web-clips/`
- when a new file appears:
  - notify user
  - optionally queue a follow-up prompt
  - or append to a lightweight “pending ingest” queue

### Best mode
Start with:
- **watch + notify**
- not immediate auto-ingest

### Why
Ingest is still a semantic workflow:
- privacy screen
- entity extraction
- contradiction handling
- broad wiki integration

That’s still best done by prompt+skill, not hardcoded hook logic.

---

## 4. Guardrails before writes: strongest hook use-case
This is where hooks shine.

### Use `tool_call`
For `write`, `edit`, and `bash`, enforce repo rules.

## Good checks to enforce

### A. Protect raw-layer immutability
From `AGENTS.md` / core skill: `raw/` is immutable capture.

Hook rules:
- block `edit` on existing `raw/**`
- allow new writes to expected capture folders if intended
- require confirmation for `rm`, `mv`, bulk changes in `raw/`

### B. Protect high-risk files
Require confirmation or block destructive changes to:

- `AGENTS.md`
- `.pi/prompts/**`
- `.pi/skills/**`
- `wiki/index.md`
- `wiki/log.md`

### C. Destructive bash confirmation
Detect dangerous `bash` touching:

- `raw/`
- `wiki/`
- `outputs/`

Examples:
- `rm`
- `mv`
- bulk rename
- globbed edits
- `git clean`

### D. Secret / PII regex screen on downstream writes
Before writing to `wiki/` or `outputs/`, scan content for:
- API keys
- tokens
- emails / phone numbers
- likely secrets

This aligns directly with your privacy policy.

### E. Enforce filename conventions
For new wiki/output pages:
- lowercase kebab-case

### F. Require frontmatter on new `wiki/*.md`
At least warn; possibly block.

This is one of the best deterministic checks you can automate.

---

## 5. Post-write verification: report-only first
Use hooks to re-check what happened.

### Use `tool_result` or track state and inspect at `agent_end`
This is ideal for “verify, don’t decide.”

Possible checks:

- new `wiki/*.md` missing frontmatter
- malformed `.canvas` / `.base`
- suspiciously empty pages
- downstream markdown contains no citations
- writes to `wiki/` happened without touching `wiki/log.md`
- major new pages were created without touching `wiki/index.md`

### Important nuance
Some checks are deterministic, some are fuzzy.

#### Good deterministic checks
- file naming
- frontmatter present
- secrets regex
- protected path touched
- log file append vs overwrite
- raw edit happened

#### Fuzzy checks → report only
- “does this page have enough evidence?”
- “should this page be in index?”
- “is contradiction resolution adequate?”
- “is this durable enough to save?”

Those should stay prompt/skill-driven.

---

## 6. End-of-turn completeness auditor
This is a very good repo-specific design.

### Use `agent_end`
Track touched files during the turn. Then warn if the workflow looks incomplete.

Examples:

- changed `wiki/` but not `wiki/log.md`
- created important new page but not `wiki/index.md`
- updated `outputs/crystallizations/` but didn’t promote lessons into `wiki/`
- ingested from `raw/` but no source page was created

This is probably the best place for your “re-check / verify” logic.

### Why
It doesn’t fight the model mid-turn.  
It evaluates the whole workflow outcome.

---

## 7. Scheduled maintenance: hooks + external trigger
Pi hooks alone are not a scheduler. But they can support one well.

### Best pattern
Use:
- cron/systemd/task scheduler
- write to a trigger file or call a command
- pi extension watches that and sends a user message

Then schedule:
- weekly `/review`
- monthly `/lint`
- monthly `/retention-pass`
- regular `/privacy-scan`

This matches the “Automation Direction” already written in `.pi/skills/llm-wiki-maintenance/SKILL.md`.

### Important limitation
This only works cleanly if:
- pi is running
- or you launch a pi session from an external script

So I’d treat scheduled automation as **phase 2**, not phase 1.

---

## 8. Better compaction summaries
This is a subtle but high-value hook.

### Use `session_before_compact`
Customize compaction so summaries preserve:

- original question
- what was investigated
- key findings
- changed files/pages
- unresolved questions
- next steps

Basically: compact using the same shape as your crystallization workflow.

### Why
It keeps long sessions aligned with your memory model:
- episodic memory
- later crystallization
- less context loss

This is much better than generic compaction.

---

## 9. Session shutdown: reminder, not full automation
### Use `session_shutdown`
Good for:
- reminder: “This session changed 8 files; run `/session-end`?”
- save extension state
- flush pending audit info

### Not recommended
Don’t auto-run full crystallization on shutdown.

Why:
- shutdown is a fragile place
- user may want to quit fast
- semantic distillation is still better as an explicit action

---

# What should stay in prompts/skills, not hooks

I would **not** move these into hook code:

- source interpretation
- claim extraction
- contradiction resolution
- supersession judgment
- deciding what is “durable”
- deciding what belongs in `wiki/` vs `outputs/`
- creating canonical pages
- taxonomy / merges / structural redesign
- major privacy cleanup decisions

Those are exactly the parts your prompts/skills are already good at.

So the rule is:

> **Move orchestration and enforcement into hooks. Keep semantic reasoning in skills.**

---

# Recommended rollout order

## Phase 1 — low risk, high value
1. `input` router
2. `tool_call` guardrails
3. `agent_end` completeness auditor
4. `session_start` reminders

## Phase 2 — semi-automatic
5. raw inbox watcher
6. overdue maintenance trigger
7. custom compaction

## Phase 3 — optional automation
8. scheduled review/lint via external trigger
9. opt-in auto-queue ingest when new raw files arrive

---

# Suggested extension split

I’d likely create:

- `.pi/extensions/workflow-router.ts`
  - `input`
- `.pi/extensions/vault-guardrails.ts`
  - `tool_call`
- `.pi/extensions/workflow-auditor.ts`
  - touched-path tracking + `agent_end`
- `.pi/extensions/session-reminders.ts`
  - `session_start`, `session_shutdown`
- `.pi/extensions/compaction-memory.ts`
  - `session_before_compact`

---

# My strongest recommendation

If you only implement **three** things first:

1. **`input` routing**
2. **`tool_call` governance/privacy guardrails**
3. **`agent_end` workflow completeness checks**

That gives you the most leverage while still respecting the repo’s current **manual-first, human-steered** design.

If you want, next I can turn this into a concrete hook architecture doc for this repo, or draft the first `.pi/extensions/*.ts` files.