---
type: Concept
title: Fast Jev Compaction for Agent Transcripts
description: Delete-only Jev compaction that scores each tool call and result with noul probabilities and drops or truncates stale ones verbatim, plus its Claude Code plugin adapter.
tags: [jev, agents, context-management, compaction]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:59:00Z }
sources:
  - id: reddit-jev-287-2026-09
    resource: ../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md
    scope: ../raw/i-reviewed-287-opensource-jev-projects-here-are/
    kind: thread
    title: 'I reviewed 287 open-source Jev projects. Here are 20 that actually helped me understand what Jev is good at'
  - id: fast-jev-compaction-2026
    resource: ../raw/fast-jev-compaction.md
    kind: docs
    title: fast-jev-compaction
---

# Fast Jev Compaction for Agent Transcripts

Synthesis: fast-jev-compaction replaces lossy summarization with delete-only Jev compaction — every tool call and result is scored by Jev against the full conversation, stale calls are removed, stale results are truncated, and everything kept stays verbatim in order; the same package serves as an npm library and as a Claude Code plugin that replaces the built-in compaction summary[^fast-jev-compaction-2026].

## Delete-only principle

- Standard compaction asks an LLM to summarize old turns, which is lossy: file paths, exact errors, constraints, or commands can disappear even when they matter later[^fast-jev-compaction-2026].
- This library never rewrites anything: it only deletes tool calls and tool results Jev says are no longer needed, while user and assistant text stays verbatim and in order[^fast-jev-compaction-2026].
- Only tool calls and results are candidates; text messages are never removed or shortened in the output — they are only abridged in the state Jev sees ("Limitations")[^fast-jev-compaction-2026].

## How it decides

- Pairing and pinning ("How it works" step 1): every `tool_use` is paired with its `tool_result` by `tool_use_id`; calls in the first message and in the newest `preserveRecentMessages` messages are pinned and never touched[^fast-jev-compaction-2026].
- State ("How it works" step 2): Jev sees the whole conversation so far, oldest first, with every tool result replaced by a short note (`ok, 4213 chars (omitted)`); tool inputs and texts are included, nothing is summarized[^fast-jev-compaction-2026].
- Fitting ("How it works" step 3): the state is fitted into `maxStateTokens` (default 25k) in stages, each applied only if the previous one was not enough — tool inputs truncated to 1000, then 200, then 60 characters; long texts abridged to head plus tail, oldest non-pinned first; old non-pinned messages collapsed to a `[… N chars omitted …]` note; old tool calls reduced to one line each (`t12 Read file_path=src/a.ts → ok 480ch`); old call-less messages left out; runs of old call-only messages folded into one entry; if it still does not fit, compaction throws[^fast-jev-compaction-2026].
- Token estimates ("How it works" step 3): sizes are estimated without a tokenizer — a word per six letters, half a token per digit, about one per other symbol — calibrated to land a little above the counts Jev reports[^fast-jev-compaction-2026].
- Dual questions ("How it works" step 4): for every non-pinned call Jev gets two `noul` questions — should the **call** stay (knowing it was made, with its input, still matters), and should the **result** stay verbatim (its contents are still needed and re-running the tool would not do)[^fast-jev-compaction-2026].
- Batching ("How it works" step 5): questions are split into as many requests as needed so state plus questions stays under `maxRequestTokens` (default 30k, under Jev's 32k request limit); the same full state is resent with every request, requests run concurrently, and answers are merged[^fast-jev-compaction-2026].
- Decision rule ("How it works" step 6, against `keepThreshold`, default 0.5): `keepResult ≥ threshold` keeps call and result; else `keepCall ≥ threshold` keeps the call and truncates the result to its first `truncateHeadChars` characters plus a one-line note; else the call is removed together with its result[^fast-jev-compaction-2026].
- Rebuild ("How it works" step 7): the message list is rebuilt so a message that loses all its content is removed, untouched messages are returned as the same objects, and no result is ever left without its call[^fast-jev-compaction-2026].
- Failure ("How it works" closing): Jev failures, malformed answers, a missing key, or a history that cannot be fitted throw; the caller (or the Claude Code hook) decides what to fall back to[^fast-jev-compaction-2026].

## Library interface

- Install is `npm install fast-jev-compaction` with `export TYPESAFE_API_KEY=...`; `Message` is a subset of Claude Code's `SessionMessage`, so a session transcript can be passed in as is ("Install and usage")[^fast-jev-compaction-2026].
- `compactMessages(transcript, { preserveRecentMessages: 4 })` returns `messages`, `decisions`, and `stats`; `reductionRatio(result) < 0.25` is the documented not-worth-it signal — keep the original transcript or summarize instead ("Install and usage")[^fast-jev-compaction-2026].
- Bring-your-own transport: implement `JevAsker` (one `ask(state, questions)` method) and call `compact(messages, asker, options)`; `buildJevRequest` and `parseJevResponse` expose the HTTP request body and response validation, and the building blocks (`collectToolCalls`, `fitState`, `batchCalls`, `decideCall`, `applyDecisions`) are exported too ("Install and usage")[^fast-jev-compaction-2026].
- `apiKey` defaults to `process.env.TYPESAFE_API_KEY`, and the source warns never to commit the key or put it in a source file — no live credential is stored here ("Install and usage," "Options")[^fast-jev-compaction-2026].

| Option | Default | Description |
| --- | --- | --- |
| `apiKey` | `TYPESAFE_API_KEY` | TypeSafe API key (`compactMessages`/`JevClient`) |
| `model` | `jev-latest` | Jev model name |
| `baseUrl` | `https://api.typesafe.ai/v1/systemone` | System One endpoint |
| `fetch` | native `fetch` | Injectable fetch for tests |
| `goal` | last 3 user prompts | Ongoing task description in the state |
| `keepThreshold` | `0.5` | Minimum keep probability for a call or result to stay |
| `preserveRecentMessages` | `6` | Newest messages never touched (the first is always kept) |
| `maxStateTokens` | `25000` | Estimated token ceiling for the state |
| `maxRequestTokens` | `30000` | Estimated ceiling for state plus one batch |
| `truncateHeadChars` | `300` | Characters of a dropped result retained before its note |

- `result.stats` reports message and character counts before and after, per-reason decision counts, state size in estimated tokens, which fitting stage was needed, and the number of requests ("Options")[^fast-jev-compaction-2026].

## Claude Code plugin

- The repository root is a Claude Code function-hook plugin: `hooks/fast-jev.ts` is a thin adapter feeding `session.compact` transcripts through `src/`, falling back to Claude Code's built-in summary on errors or insufficient reduction ("Claude Code plugin")[^fast-jev-compaction-2026].
- Requires Claude Code 2.1.274+ with the opt-in flag set where Claude Code runs, e.g. `{ "env": { "CLAUDE_CODE_ENABLE_FUNCTION_HOOKS": "1", "TYPESAFE_API_KEY": "<your key>" } }` in `~/.claude/settings.json` ("Install in Claude Code")[^fast-jev-compaction-2026].
- Installed via `claude plugin marketplace add tamaratran/fast-jev-compaction` and `claude plugin install fast-jev-compaction@fast-jev-compaction` (prompts for plugin options; defaults use `TYPESAFE_API_KEY` from the environment), then restart or `/reload-plugins`; from a checkout, `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1 claude --plugin-dir .` runs without installing ("Install in Claude Code")[^fast-jev-compaction-2026].
- From then on `/compact` and auto-compaction go through Jev: the toast reads `fast-jev-compaction: kept N/M messages, no summary (…)` when the pruned history replaced the built-in summary, or `fallback to built-in summary (…)` when Jev could not remove enough — short sessions, or when it fails ("Install in Claude Code")[^fast-jev-compaction-2026].

## Development and demo

- Commands: `npm install`, `npm run typecheck`, `npm test`, `npm run build`, `npm run validate:plugin`, and `TYPESAFE_API_KEY="$(cat ~/.typesafe_key)" npm run demo`; unit tests use a fake Jev and never contact TypeSafe, while the demo is the live network check ("Development")[^fast-jev-compaction-2026].
- `demo/JevDemo` is a small native macOS SwiftUI app playing a scripted, dramatized compaction flow in a Claude Code-style terminal — scored tool calls turn red and collapse, the rest stays verbatim; it never calls the API and exists to be screen recorded via `demo/JevDemo/build.sh`, with space replaying from the start ("Animated demo")[^fast-jev-compaction-2026].

## Limitations

- Token sizes are estimates from character counts, not a tokenizer ("Limitations")[^fast-jev-compaction-2026].
- Calibration is at the request level: a probability is not a proof that a result is safe to delete — but the assistant can always re-run the tool ("Limitations")[^fast-jev-compaction-2026].
- Cost scaling: the full state repeats with every request, so a history near the state ceiling costs one request per handful of questions ("Limitations")[^fast-jev-compaction-2026].
- Independent field check is **reported**: at the default 0.5 keep cutoff, a reviewer sent 120 tool calls through scoring and it kept none of them[^reddit-jev-287-2026-09].
- Reversible-pruning proposal is **reported**: keep lightweight references to discarded outputs for later retrieval when a failure changes what matters, and stress-test with a bug whose explanation was discarded earlier to measure recovery without restart[^reddit-jev-287-2026-09].

## Relationships

- Uses [Jev Decision Model](jev-decision-model.md) `noul` keep-probabilities as the per-call, per-result retention signal.
- Uses [Jev API Patterns](jev-api-patterns.md) `noul` invocation shape, applied here as a paired call/result question per tool use.
- Complements [Conservative Jev Routing for Coding Agents](conservative-jev-routing.md), which governs model switching, whereas this pattern governs what history survives.
- Complements [Jev-Evaluated Agent Memory](jev-evaluated-agent-memory.md): this pattern forgets stale tool evidence, whereas Beacon promotes high-signal runs into reusable skills.
- Informs [Classifier Selection](classifier-selection.md) agent-harness uses with a concrete delete-only pruning implementation.
- Exemplified by [Jev Project Patterns](jev-project-patterns.md) alongside garbage-collection and referee context roles.

## Coverage limits

- Single documentation file inspected by static reading; the package implementation (`src/`), hook adapter (`hooks/fast-jev.ts`, `hooks/README.md`), plugin manifests (`.claude-plugin/`), tests, and the SwiftUI demo app were not inspected and no commands were executed — behavior above is **reported**, not reproduced[^fast-jev-compaction-2026].
- No revision, date, license, or upstream repository URL is stated in the source; the marketplace identifier `tamaratran/fast-jev-compaction` and npm name `fast-jev-compaction` are **reported** install handles, not verified registry entries[^fast-jev-compaction-2026].
- No credentials, keys, tokens, or non-public PII were found in the source; only the `TYPESAFE_API_KEY` placeholder and its never-commit warning appear.
- Pins are time-sensitive: Claude Code 2.1.274+ function hooks, `jev-latest`, and the System One endpoint default — verify before depending on them.
- Survey field check above is single-reviewer Reddit anecdote (2026-09-23) with no transcript or outcome log inspected; treat the 120-call/0-kept result as a **reported** threshold warning, not a reproduced measurement[^reddit-jev-287-2026-09].

[^fast-jev-compaction-2026]: `fast-jev-compaction` documentation, canonical local entry `../raw/fast-jev-compaction.md`. Locators in text: title and opening paragraphs (verbatim delete-only principle); "What and why" (summary-lossless motivation); "How it works" steps 1–7 and failure paragraph; "Install and usage" (npm install, `TYPESAFE_API_KEY`, `compactMessages`/`compact`/`JevAsker`/`buildJevRequest`/`parseJevResponse`/building blocks, `reductionRatio` 0.25 rule, never-commit-key warning); "Options" table and `result.stats`; "Limitations" (text never removed, estimates, request-level calibration, repeated-state cost); "Claude Code plugin" and "Install in Claude Code" (hook adapter, fallback, settings flag, marketplace commands, toast strings, `--plugin-dir` checkout run); "Development" (commands, fake-Jev tests, live demo); "Animated demo (macOS)" (scripted SwiftUI dramatization, no API calls, build script, space replay).
[^reddit-jev-287-2026-09]: u/chenrongwei plus commenters, "I reviewed 287 open-source Jev projects," r/LLMDevs, post with comments 2026-09-19–2026-10-01, canonical local entry `../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md`, package scope `../raw/i-reviewed-287-opensource-jev-projects-here-are/`, upstream `https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/`. Locators in text: `fast-jev-compaction` verbatim-survivor item; `peeeanuts` pbi1v71 120-call/0-kept check; `Crescitaly` pbbpx7r reversible-pruning proposal; `Appropriate_Joke2454` pb76e6k context-window puzzle.
