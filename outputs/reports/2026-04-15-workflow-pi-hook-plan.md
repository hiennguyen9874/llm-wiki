# Pi Hooks Workflow Refactor Plan

## Goal

Refactor the current prompt-driven workflow so pi hooks handle the parts they are best at:

- routing
- reminders
- guardrails
- post-action verification
- optional event-driven triggers

while keeping semantic workflow logic in prompts and skills:

- ingest reasoning
- query synthesis
- contradiction resolution
- crystallization judgment
- taxonomy and canonical-page decisions

This plan follows the current repository stance from `AGENTS.md` and `llm-wiki-core`: **manual-first, human-steered, prompt-driven**, with hooks used to reduce bookkeeping and improve safety rather than hide important decisions.

---

## Non-goals

Do **not** move these into hook code:

- source understanding
- claim extraction
- contradiction or supersession judgment
- deciding what is durable enough for `wiki/`
- major taxonomy changes
- bulk merges or destructive cleanup

Those should remain in prompts and skills.

---

## Implementation status

### Completed on 2026-04-15
- Phase 1 scaffold and local extension layer
- `workflow-router.ts`
- `vault-guardrails.ts`
- `workflow-auditor.ts`
- `session-reminders.ts`
- shared helper modules in `.pi/extensions/lib/`
- `README.md` hook-layer documentation
- `AGENTS.md` implementation-stance clarification
- `docs/pi-hooks-local.md`

### Completed on 2026-04-15
- `compaction-memory.ts`
- `inbox-watcher.ts`
- Phase 2 documentation refresh

### Completed on 2026-04-15
- scheduled / external-trigger support
- optional user-facing automation commands

---

## Recommended rollout order

### Phase 1: high-value, low-risk
- [x] Add `.pi/extensions/` scaffold
- [x] Implement `workflow-router.ts`
- [x] Implement `vault-guardrails.ts`
- [x] Implement `workflow-auditor.ts`
- [x] Implement `session-reminders.ts`
- [x] Document behavior and usage

### Phase 2: optional, medium-risk
- [x] Implement `compaction-memory.ts`
- [x] Implement `inbox-watcher.ts` in notify-only mode

### Phase 3: scheduled/event-driven support
- [x] Add external trigger pattern for scheduled review/lint/retention/privacy tasks
- [x] Optionally add user-facing commands for opt-in automated runs

---

## Target architecture

Create a project-local hook layer in `.pi/extensions/`.

```text
.pi/
  extensions/
    workflow-router.ts
    vault-guardrails.ts
    workflow-auditor.ts
    session-reminders.ts
    compaction-memory.ts          # optional
    inbox-watcher.ts              # optional
    scheduled-trigger.ts          # optional
    lib/
      paths.ts
      policy.ts
      log.ts
      frontmatter.ts
      secrets.ts
      audit.ts
      maintenance.ts
  scripts/
    trigger-maintenance.mjs       # optional
```

### Design principles

- Keep each extension focused on one concern.
- Put reusable path/policy utilities in `.pi/extensions/lib/`.
- Prefer **warn/report** before **block**, unless the rule is deterministic and high-risk.
- Default to **notify and suggest a prompt** rather than silently running semantic workflows.
- Make hooks safe to reload with `/reload`.

---

## File-by-file implementation plan

## Step 0: scaffold the extension layer

### Status
Done on 2026-04-15.

### Files to create
- `.pi/extensions/workflow-router.ts`
- `.pi/extensions/vault-guardrails.ts`
- `.pi/extensions/workflow-auditor.ts`
- `.pi/extensions/session-reminders.ts`
- `.pi/extensions/lib/paths.ts`
- `.pi/extensions/lib/policy.ts`
- `.pi/extensions/lib/frontmatter.ts`
- `.pi/extensions/lib/secrets.ts`
- `.pi/extensions/lib/log.ts`
- `.pi/extensions/lib/audit.ts`

### Files to update
- `README.md`
- optionally `AGENTS.md`

### What to update

#### `README.md`
Add a short section describing:
- project-local pi extensions live in `.pi/extensions/`
- they provide workflow routing, guardrails, reminders, and verification
- how to reload them with `/reload`
- what is automated vs still manual

#### `AGENTS.md` (optional, small update only)
Add one short subsection under implementation stance or working style:
- hooks may automate routing, reminders, guardrails, and verification
- semantic knowledge work remains prompt/skill-driven

### Design notes
- No `.pi/settings.json` update is required for local auto-discovery; pi loads `.pi/extensions/` automatically.
- Keep helper utilities pure and filesystem-oriented.
- Avoid adding a build step; use plain TypeScript as pi expects.

### Acceptance criteria
- `.pi/extensions/` exists
- `/reload` can load extensions cleanly
- `README.md` explains the hook layer

---

## Step 1: implement input routing

### Status
Done on 2026-04-15.

### File to create
- `.pi/extensions/workflow-router.ts`

### Goal
Use the `input` hook to reduce friction and map simple inputs to the correct prompt workflow.

### Behavior

#### Route plain web URLs
Transform raw URL input into:
- `/ingest-url <url>`

Rules:
- only when the full input is a single URL
- do not rewrite if the user already used a slash command
- do not rewrite markdown file URLs differently here; the existing prompt/skill already handles `.md`

#### Route raw file paths
Transform likely raw paths into:
- `/ingest <path>`

Examples:
- `raw/inbox/foo.md`
- `./raw/articles/bar.md`

#### Add a few safe shorthand aliases
Examples:
- `review` -> `/review`
- `lint` -> `/lint`
- `privacy-scan` -> `/privacy-scan`
- `session-start` -> `/session-start`
- `session-end` -> `/session-end`

### Things to avoid
- no heavy natural-language rewriting
- no guessing between `query`, `brief`, `briefing`, `connections`, etc.
- no silent execution of maintenance tasks

### Internal design

#### In `.pi/extensions/lib/paths.ts`
Implement helpers such as:
- `isLikelyRawPath(text: string): boolean`
- `normalizeRepoRelativePath(text: string): string | null`
- `isSingleUrl(text: string): boolean`

#### In `workflow-router.ts`
Implement:
- `pi.on("input", ...)`
- return `{ action: "transform", text: ... }` for simple deterministic routing
- return `{ action: "continue" }` otherwise

### Acceptance criteria
- entering a bare URL routes to `/ingest-url`
- entering a raw path routes to `/ingest`
- slash commands still pass through unchanged
- freeform normal prompts remain unchanged

### Test cases
- `https://example.com/article`
- `raw/inbox/note.md`
- `/query redis caching`
- `What do we know about Redis?`
- `review`

---

## Step 2: implement guardrails and write-time policy checks

### Status
Done on 2026-04-15.

### File to create
- `.pi/extensions/vault-guardrails.ts`

### Goal
Use `tool_call` to enforce deterministic repository rules before tools run.

### Hooks used
- `tool_call`

### Rules to implement first

#### Rule A: protect raw-layer immutability
Block editing existing files under `raw/` except for approved capture creation flows.

Recommended behavior:
- block `edit` on `raw/**`
- block overwrite-style `write` on existing `raw/**`
- allow creation of new files in `raw/web-clips/`, `raw/inbox/`, `raw/captures/`, or other intended capture folders
- require confirmation or block risky bash commands affecting `raw/`

Why:
- `AGENTS.md` and core skill treat `raw/` as immutable capture

#### Rule B: protect sensitive governance files
Warn or require confirmation for edits to:
- `AGENTS.md`
- `.pi/prompts/**`
- `.pi/skills/**`

Recommended mode:
- warn first
- optionally block only destructive bash operations on these paths

#### Rule C: protect append-only `wiki/log.md`
Disallow overwrite patterns that replace the full file accidentally.

Recommended behavior:
- for `write` to `wiki/log.md`, warn or block unless content clearly appends the existing file intentionally
- simplest first version: block direct `write` to `wiki/log.md`, allow `edit`

#### Rule D: dangerous bash confirmation
Detect destructive shell commands involving:
- `rm`
- `mv`
- `find ... -delete`
- bulk rename loops
- `git clean`

Prioritize when they touch:
- `raw/`
- `wiki/`
- `outputs/`
- `.pi/`

#### Rule E: downstream secret / PII scan
Before `write` or `edit` targeting `wiki/` or `outputs/`, scan new content for:
- API keys
- auth tokens
- obvious secret formats
- email addresses
- phone numbers
- likely credential strings

Recommended behavior:
- first version: warn and optionally block only high-confidence secrets
- report the matched pattern category, not full secret value

#### Rule F: naming convention for new markdown artifacts
For new files in `wiki/` or `outputs/`:
- lowercase kebab-case filenames

Recommended behavior:
- warn first, do not block initially

#### Rule G: frontmatter presence for new wiki notes
When creating new `wiki/*.md`:
- warn if missing YAML frontmatter
- do not block initially

### Internal design

#### `.pi/extensions/lib/policy.ts`
Centralize path rules:
- protected files
- protected directories
- raw immutability policy
- dangerous bash patterns

#### `.pi/extensions/lib/secrets.ts`
Implement regex-based checks:
- `findSecretLikePatterns(text: string): SecretHit[]`
- keep false-positive-tolerant but conservative

#### `.pi/extensions/lib/frontmatter.ts`
Helpers:
- `hasYamlFrontmatter(text: string): boolean`
- `isKebabCaseFilename(path: string): boolean`

### Acceptance criteria
- edit to existing `raw/` file is blocked
- dangerous bash touching vault files asks for confirmation or blocks in no-UI mode
- suspicious secret-like content in `wiki/` or `outputs/` is surfaced
- new non-kebab-case wiki file triggers a warning
- missing frontmatter on new wiki note triggers a warning

### Test cases
- edit `raw/articles/foo.md`
- write `wiki/New Page.md`
- write `wiki/topic.md` without frontmatter
- write content containing a token-like string to `outputs/`
- bash `rm -rf wiki/tmp`

---

## Step 3: implement end-of-turn workflow auditor

### Status
Done on 2026-04-15.

### File to create
- `.pi/extensions/workflow-auditor.ts`

### Goal
Track what happened during a turn and verify whether the workflow looks incomplete.

### Hooks used
- `tool_call`
- `tool_result`
- `agent_start`
- `agent_end`

### Core idea
Track touched paths and action categories in memory during a single agent run, then evaluate at `agent_end`.

### What to track
- files written or edited
- whether any `raw/` files were read or referenced
- whether any `wiki/` files changed
- whether any `outputs/` files changed
- whether `wiki/index.md` changed
- whether `wiki/log.md` changed
- whether a source-like page was created

### Suggested audit checks

#### Audit A: wiki changed without log update
If any meaningful `wiki/` or `outputs/` pages changed but `wiki/log.md` did not, notify:
- "Workflow may be incomplete: changed durable artifacts without appending `wiki/log.md`."

#### Audit B: important new page without index update
If a new page was created in `wiki/` or visual artifacts were added in `wiki/bases/` or `wiki/canvases/`, but `wiki/index.md` was not touched, notify.

#### Audit C: crystallization/output created without wiki integration
If `outputs/crystallizations/` or high-value `outputs/` changed but no `wiki/` pages changed, notify.

#### Audit D: ingest-like work without source page or broad integration
If a raw source was processed and only one summary file changed, notify that ingest may not be fully integrated.

#### Audit E: downstream markdown lacks citations
For newly created `wiki/*.md` or durable `outputs/*.md`, check for at least one likely citation form:
- wikilinks to source pages
- markdown links
- source section markers

First version should be report-only, not block.

### Internal design

#### `.pi/extensions/lib/audit.ts`
Implement:
- `type TurnAuditState`
- `beginTurn()`
- `recordToolCall(...)`
- `recordToolResult(...)`
- `summarizeAudit(...)`
- `findLikelyWorkflowGaps(...)`

### Output style
Use `ctx.ui.notify(...)` with concise findings.
If there are multiple findings, show:
- title
- short list of gaps
- suggested next prompt, e.g. `/review`, `/session-end`, or manual fix

### Acceptance criteria
- when `wiki/` changes without `wiki/log.md`, user gets warned
- when new important pages are added without `wiki/index.md`, user gets warned
- warnings happen after the turn, not mid-edit
- no false hard blocks on ambiguous cases

---

## Step 4: implement session reminders and maintenance nudges

### Status
Done on 2026-04-15.

### File to create
- `.pi/extensions/session-reminders.ts`

### Goal
Use `session_start` and `session_shutdown` to show lightweight operational reminders.

### Hooks used
- `session_start`
- `session_shutdown`

### Startup checks

#### Check A: pending inbox/capture items
Count files in:
- `raw/inbox/`
- `raw/captures/`

Notify if above threshold.

#### Check B: overdue maintenance
Inspect `wiki/log.md` to find last entries for:
- `review`
- `lint`
- `crystallize`
- `update`

Then nudge if overdue.

Suggested thresholds:
- review: > 7 days
- lint: > 30 days
- privacy-scan: if explicitly logged, > 30 days
- retention-pass: if explicitly logged, > 30 days

#### Check C: recent outputs not integrated
Optionally inspect recent files in `outputs/crystallizations/` and compare timestamps to recent `wiki/` activity.

### Shutdown checks
If the session changed many files and no crystallization happened, notify:
- "Consider `/session-end` to distill this session."

Do not auto-run semantic prompts on shutdown.

### Internal design

#### `.pi/extensions/lib/log.ts`
Helpers:
- `parseLogActions(logContent: string)`
- `getLastActionDate(action: string)`
- `daysSince(date)`

### Acceptance criteria
- startup shows meaningful nudges without being noisy
- reminders are informational, not blocking
- shutdown can recommend `/session-end` after meaningful work

---

## Step 5: update docs after Phase 1 lands

### Status
Done on 2026-04-15.

### Files to update
- `README.md`
- optionally `AGENTS.md`
- optionally create `docs/pi-hooks-local.md`

### What to document
- which hooks exist locally
- what each one does
- what is block vs warn vs suggest
- how to disable or tune behavior
- examples of routed inputs
- examples of policy-protected operations

### Recommended documentation additions

#### `README.md`
Add a section like:
- "Local Hook Layer"
- list the four initial extensions
- note that semantic workflows remain prompt/skill-based

#### `AGENTS.md` (small note)
Add a sentence clarifying:
- hooks may assist workflow routing, verification, reminders, and deterministic policy enforcement

#### Optional `docs/pi-hooks-local.md`
This can become the canonical project-specific hook reference.

---

## Step 6: optional custom compaction aligned to crystallization

### Status
Done on 2026-04-15.

### File to create
- `.pi/extensions/compaction-memory.ts`

### Goal
Use `session_before_compact` to preserve structured episodic memory instead of generic summaries.

### Hooks used
- `session_before_compact`

### Desired summary shape
When compaction happens, preserve:
- original question
- what was done
- key findings
- changed files/pages
- unresolved questions
- next recommended steps

### Design choice
Do not write to `wiki/` or `outputs/` from compaction.
Compaction is for session memory only.

### Why this matters
This keeps long-running sessions consistent with your crystallization model without pretending compaction itself is durable knowledge integration.

### Acceptance criteria
- compacted sessions retain reusable structured state
- no durable files are modified during compaction

---

## Step 7: optional inbox watcher in notify-only mode

### Status
Done on 2026-04-15.

### File to create
- `.pi/extensions/inbox-watcher.ts`

### Goal
Watch `raw/inbox/` and `raw/captures/` for new files and notify the user.

### Hooks used
- `session_start`
- `session_shutdown`

### Behavior
On session start:
- start `fs.watch()` on selected folders

When a new file appears:
- notify user
- optionally suggest `/ingest <path>` or `/ingest-batch raw/inbox`

### First-version rule
Do **not** auto-run ingest.
Only notify.

### Optional later enhancement
Add an extension command like `/ingest-pending` that sends a user message or queues follow-up work.

### Acceptance criteria
- new files are detected while pi is running
- only a notification happens
- watcher is cleaned up on shutdown/reload

---

## Step 8: optional scheduled trigger support

### Status
Done on 2026-04-15.

### Goal
Support periodic maintenance using an external scheduler plus pi hooks.

### Recommended pattern
Use one of:
- cron
- systemd user timer
- launchd
- external script

The scheduler can:
- write to a trigger file
- or start pi with a command
- or use an extension command/event bridge

Implemented in this repo via:
- `.pi/extensions/scheduled-trigger.ts`
- `.pi/extensions/lib/maintenance.ts`
- `.pi/scripts/trigger-maintenance.mjs`
- `docs/pi-scheduled-maintenance.md`

### Suggested scheduled tasks
- weekly `/review`
- monthly `/lint`
- monthly `/retention-pass`
- monthly `/privacy-scan`

### Important constraint
This is reliable only when:
- pi is running and the watcher is active, or
- you explicitly launch pi from automation

### Recommendation
Treat this as explicit infrastructure, not hidden semantic automation.

### Acceptance criteria
- external tooling can queue a maintenance trigger via a file-backed bridge
- pi can notify or enqueue supported maintenance commands from that trigger queue
- user-facing opt-in commands exist for status, queueing, and immediate runs
- behavior is documented with concrete scheduler examples

---

## Shared utility design

## `.pi/extensions/lib/paths.ts`
Responsibilities:
- repo-relative path normalization
- identify whether a path is in `raw/`, `wiki/`, `outputs/`, `.pi/`
- detect likely new file vs existing file

Suggested functions:
- `toRepoRelative(path: string): string`
- `isRawPath(path: string): boolean`
- `isWikiPath(path: string): boolean`
- `isOutputsPath(path: string): boolean`
- `isProtectedPolicyPath(path: string): boolean`
- `fileExists(path: string): boolean`

## `.pi/extensions/lib/policy.ts`
Responsibilities:
- central policy configuration
- thresholds
- allowed/warn/block behavior per rule

Suggested constants:
- protected files/directories
- dangerous bash regexes
- reminder thresholds
- folders to watch

## `.pi/extensions/lib/frontmatter.ts`
Responsibilities:
- frontmatter detection
- markdown artifact checks
- filename convention checks

Suggested functions:
- `hasYamlFrontmatter(content: string): boolean`
- `isKebabCaseName(path: string): boolean`
- `looksLikeMarkdownCitation(content: string): boolean`

## `.pi/extensions/lib/secrets.ts`
Responsibilities:
- high-confidence secret detection
- lower-confidence PII hints

Suggested types:
- `type SecretHit = { kind: string; confidence: "high" | "medium"; preview: string }`

Suggested functions:
- `scanForSensitivePatterns(content: string): SecretHit[]`

## `.pi/extensions/lib/log.ts`
Responsibilities:
- parse `wiki/log.md`
- action recency analysis

Suggested functions:
- `extractLogEntries(markdown: string)`
- `findLastAction(entries, action)`
- `daysSince(date)`

## `.pi/extensions/lib/audit.ts`
Responsibilities:
- maintain per-agent-run audit state
- classify file touches
- compute post-run warnings

---

## Suggested initial warning/block policy

### Block immediately
- edit existing files in `raw/`
- overwrite-style writes to existing `raw/` files
- clearly destructive bash affecting vault folders in no-UI mode

### Warn first
- editing `AGENTS.md`, `.pi/prompts/`, `.pi/skills/`
- writing new wiki files without frontmatter
- non-kebab-case filenames
- likely missing citations
- missing `wiki/index.md` or `wiki/log.md` update

### Suggest only
- run `/review`
- run `/session-start`
- run `/session-end`
- run `/lint`
- run `/privacy-scan`

---

## Testing plan

## Manual tests after each file

### Router tests
- bare URL
- raw path
- normal question
- existing slash command

### Guardrail tests
- edit raw file
- create raw web-clip file
- write wiki file without frontmatter
- write token-like content
- dangerous bash

### Auditor tests
- change `wiki/` without `wiki/log.md`
- add page without `wiki/index.md`
- create crystallization without wiki promotion

### Reminder tests
- fake stale `wiki/log.md` dates
- add items to `raw/inbox/`
- session with many edits then shutdown

## Regression checks
- `/reload` works
- normal prompt flows still function
- prompts and skills remain primary semantic workflow engine
- no hidden auto-ingest or hidden wiki mutation occurs

---

## Rollback strategy

If any extension becomes noisy or unsafe:
- temporarily move the file out of `.pi/extensions/`
- or rename it so pi no longer auto-discovers it
- run `/reload`

Keep the implementation split so individual extensions can be disabled independently.

---

## Recommended implementation order in practice

1. Create utility files and `workflow-router.ts`
2. Implement and test `vault-guardrails.ts`
3. Implement and test `workflow-auditor.ts`
4. Implement and test `session-reminders.ts`
5. Update `README.md`
6. Optionally add small `AGENTS.md` clarification
7. Later: compaction and watcher

---

## Final recommendation

Start with these four extensions only:

- `workflow-router.ts`
- `vault-guardrails.ts`
- `workflow-auditor.ts`
- `session-reminders.ts`

That gives the best leverage while preserving the current repo philosophy:
- prompts remain the visible workflow entry points
- skills remain the durable procedure layer
- hooks reduce manual bookkeeping and prevent avoidable mistakes
- high-stakes semantic decisions remain human-steered
