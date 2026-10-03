---
type: Concept
title: Jev Ultrafast Browser Agent
description: Browser agent that picks one operation plus element per Jev request with typing-only small LLM, measured 7.1 s Flights run and MVP DOM limits.
tags: [jev, agents, browser-automation]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T18:00:00Z }
sources:
  - id: jev-ultrafast-2026
    resource: ../raw/jev-ultrafast.md
    kind: code
    title: Jev Ultrafast
---

# Jev Ultrafast Browser Agent

Synthesis: Jev Ultrafast is a **reported** Browser Use × TypeSafe browser agent that turns each page observation into an indexed element table, asks Jev once for operation plus compatible target, and calls a small LLM only to produce text for `TYPE_TEXT` — a clean Jev-decides plus code-executes split with measured single-task speedups and explicit MVP DOM limits[^jev-ultrafast-2026].

## Action space and one-round speculative decision

- Dynamic element table is **reported**: every observation produces a new indexed table such as `[1] button Change ticket type`, `[2] combobox Where from?`, `[3] combobox Where to?`, `[4] textbox Departure`[^jev-ultrafast-2026].
- Operations are **reported** as `CLICK`, `TYPE_TEXT`, `SELECT`, `SCROLL_UP`, `SCROLL_DOWN`, `WAIT`, `DONE`, and `BLOCKED`, with only supported operations and targets offered per cycle[^jev-ultrafast-2026].
- One-request speculative fan-out is **reported**: one TypeSafe request returns `operation` plus `click_target`, `type_text_target`, and `select_target` when present; the agent uses the target matching the chosen operation, so two decisions cost one network round trip[^jev-ultrafast-2026].
- Compatibility constraint is **reported**: each target head contains only compatible elements, and native dropdown choices carry an observed element/option index[^jev-ultrafast-2026].
- No site scripts in policy is **reported**: there are no site-specific action scripts or prepared field strings; the Flights example supplies a goal and independently verifies the outcome[^jev-ultrafast-2026].

## Typing-only generation split

- Small-LLM gating is **reported**: a small LLM writes text only when the operation is `TYPE_TEXT`[^jev-ultrafast-2026].
- JSON gate is **reported**: text-helper output must parse as a small JSON object before typing[^jev-ultrafast-2026].
- Interrupted-request reuse is **reported**: a generated value survives a stale-page retry only if the entire text-helper input is unchanged[^jev-ultrafast-2026].
- Example text model is **reported**: the demo config uses an OpenRouter-compatible text helper with `inception/mercury-2.5` and reasoning disabled; Gemini, GLM, and DeepSeek can use the same OpenAI-compatible helper with their own model, endpoint, and reasoning setting[^jev-ultrafast-2026].

## Loop and latency optimizations

- One request per decision cycle is **reported**: operation and target heads share the same observed state[^jev-ultrafast-2026].
- Structured state instead of screenshots is **reported**: Jev consumes structured state in the default loop; the inspector opts into screenshots and the demo video uses a separate continuous screencast[^jev-ultrafast-2026].
- One browser call per snapshot is **reported**: read visible controls, names, values, and text atomically and keep references to actual DOM nodes[^jev-ultrafast-2026].
- Target validation is **reported**: clicks check the document, form values, target, and nearby context; animation alone does not force another prediction; current geometry is resolved and covered controls are rejected before input[^jev-ultrafast-2026].
- Useful-state waits are **reported**: after typing into a combobox wait for visible suggestions capped at 200 ms; other interactions get at most two animation frames or 50 ms; these reads happen after execution is logged[^jev-ultrafast-2026].
- Rendering and context trims are **reported**: focus emulation keeps hidden tabs rendering without switching Chrome's visible tab, and only visible text is sent while offscreen article bodies and footers stay out of model context[^jev-ultrafast-2026].
- Label-afterward note is **reported**: the screenshot renderer adds labels afterward and does not drive the browser[^jev-ultrafast-2026].

## Executor guards and policy limits

- Observed-node execution is **reported**: every executed target is resolved from an observed node; the executor rechecks page freshness and click occlusion[^jev-ultrafast-2026].
- Output confinement is **reported**: model output never becomes selectors, coordinates, shell commands, or executable JavaScript[^jev-ultrafast-2026].
- `DONE` verification rule is **reported**: a `DONE` choice still requires independent outcome verification[^jev-ultrafast-2026].
- DOM-reader scope is **reported**: the reader handles common HTML and ARIA controls, not the full accessible-name specification[^jev-ultrafast-2026].
- MVP exclusions are **reported**: shadow roots, frames, canvas, uploads, pop-up tabs, nested scrolling, and arbitrary keyboard widgets remain outside this MVP; owned tabs share the existing Chrome profile[^jev-ultrafast-2026].

## Use, inspector, and setup

- Library shape is **reported**: `from jev_ultrafast import Agent` with `Agent(url, goal)` used as a context manager; `agent.run()` yields states with `elapsed_ms` and `status`; the Flights URL plus one-way Zurich-to-London goal and a Wikipedia Gödel goal are shown as examples[^jev-ultrafast-2026].
- Trace example is **reported**: `examples/flights.py --keep-open` performs the flight search, checks the actual route/date/results, saves its trace, and does not select or book a flight[^jev-ultrafast-2026].
- Inspector is **reported**: local UI at `http://127.0.0.1:8766` with `Start demo → Run automatically`; it shows numbered elements, operation probabilities, target probabilities, and executed actions, while `Choose next` pauses before execution[^jev-ultrafast-2026].
- Setup is **reported**: `uv sync`, `cp .env.example .env` with placeholder `TYPESAFE_API_KEY` and `TEXT_MODEL_API_KEY`, `uv run jev`; Chrome connects through Browser Harness installed by `uv sync` with `uv run browser-harness --doctor` and allow-remote-debugging prompt when needed — **observed**: only placeholder key names appear here, no live credential[^jev-ultrafast-2026].
- Code map is **reported**: `agent.py` loop plus text-helper handoff, `snapshot.js` atomic snapshot plus freshness guards, `browser.py` connection plus geometry plus execution, `model.py` dynamic heads plus text generation, `questions.py` model instructions, `demo.py` local inspector[^jev-ultrafast-2026].
- Dev checks are **reported**: `uv run ruff check .`, `uv run pytest`, `node --check` on static/demo/snapshot JS, `uv build`; tests are offline and `scripts/check_guards.py` checks real controls in a local browser without model calls; live examples and recording scripts make paid API calls; `scripts/record_flights.py` captures timestamps and `scripts/render_demo.py` renders a verified run at 1× while cropping the Google account strip; credentials and raw traces stay ignored[^jev-ultrafast-2026].

## Evidence and MVP limits

- Headline run is **reported**: 7,073 ms Google Flights run for Zürich → London; timing starts after initial page observation and includes model calls, generated text, browser work, stale decisions, and loading waits; an independent check verifies one-way setting, Zürich, London, September 20, 2026, and visible flight options; video plays at 1× with no opening hold and 0.5 s final hold[^jev-ultrafast-2026].
- Six-run comparison is **reported**: six alternating runs with identical models and settings, both versions passed 3/3; median task time 9.450 s → 7.092 s (25% reduction); median browser protocol calls 1,092 → 101; the source explicitly limits this to three repeats of one task on one browser profile, not a general reliability benchmark[^jev-ultrafast-2026].
- Other single-task times are **reported**: same policy opened the requested Wikipedia article in 2.798 s and passed a local hotel search/filter task in 1.896 s; runs, failures, source hashes, and measurement boundaries are delegated to `docs/performance.md`[^jev-ultrafast-2026].
- **Synthesis**: treat this as a single-workload speed and call-count signal with independent outcome checks, not a general reliability or cross-site benchmark; verify current models, settings, and `performance.md` before reusing the numbers.

## Relationships

- Refines [Jev Project Patterns](jev-project-patterns.md) by replacing its secondary 7-second summary with the primary README mechanism, loop trims, and MVP limits.
- Exemplifies [Jev Decision Model](jev-decision-model.md) bounded-decision positioning as Jev-decides plus code-executes with generation only when generation is needed.
- Informs [Classifier Selection](classifier-selection.md) agent-harness uses as a browser-use case with speculative operation-plus-target decisions.
- Uses [Jev API Patterns](jev-api-patterns.md) decision framing with custom operation/target heads rather than generic Choice/Noul/Score shapes.

## Coverage limits

- Single README inspected by static reading; no code was executed and no live browser, model, or paid API call was made — all behaviors and timings above are **reported**, not reproduced[^jev-ultrafast-2026].
- Linked `docs/performance.md`, `docs/demo.mp4`, `docs/demo.gif`, `docs/banner.svg`, `jev_ultrafast/` Python/JS sources, `examples/`, `scripts/`, Browser Harness, TypeSafe speculative fan-out docs, and OpenRouter/model endpoints were not inspected; measurement boundaries, run failures, and source hashes inherit that uninspected limit.
- Revision and capture date are unknown from this file; API shapes, model IDs, setup commands, and availability are time-sensitive — verify against the live repo before building.
- No live credentials, private keys, tokens, or non-public PII were found; only placeholder `TYPESAFE_API_KEY` and `TEXT_MODEL_API_KEY` names appear.

[^jev-ultrafast-2026]: Browser Use × TypeSafe, "Jev Ultrafast," repo README, canonical local entry `../raw/jev-ultrafast.md`, upstream `https://github.com/browser-use/jev-ultrafast` via clone URL in text. Locators in text: intro goal plus TypeSafe Jev operation/element plus small-LLM typing-only claim and 7.1 s Zürich→London demo; "The action space" element-table block, 8-operation list, one-request diagram plus speculative target-head and native index notes, no-scripts plus label-afterward notes; "Try it" `uv sync`/`.env`/inspector/Browser-Harness/OpenRouter-`inception/mercury-2.5` notes; "Use the library" `Agent`/`run`/`elapsed_ms`/`status` plus `examples/run.py` and `examples/flights.py --keep-open` notes; "Why it moves" 8-bullet loop trims plus observed-node/occlusion/no-selector-or-JS plus JSON-gate and reuse-if-unchanged notes; "Small enough to read" 6-file table; "Evidence and limits" 7,073 ms boundaries plus 6-run 9.450 s→7.092 s/1,092→101 plus 3-repeat/1-profile caveat plus 2.798 s/1.896 s plus `DONE`-needs-verification, ARIA-scope, MVP-exclusion, and shared-profile notes; "Development" `ruff`/`pytest`/`node --check`/`uv build`, offline tests, `check_guards.py`, paid-call, `record_flights.py`/`render_demo.py`, and ignored-credential notes.
