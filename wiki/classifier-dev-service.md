---
type: Concept
title: 'Classifier.dev: Jev-Powered Zero-Shot Classification Service'
description: Hosted Jev-powered zero-shot classification service with batch, multi-label, dimension, and long-context APIs plus Cloudflare operations and agent surfaces.
tags: [jev, classification, hosted-service, agents, operations]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T19:30:00Z }
sources:
  - id: classifier-dev-docs
    resource: ../raw/classifier.dev.md
    kind: docs
    title: classifier.dev
---

# Classifier.dev: Jev-Powered Zero-Shot Classification Service

Synthesis: classifier.dev is a **reported** single-Cloudflare-Worker hosted classifier — plain text in, label plus calibrated confidence out, no key or signup for the base path — with Jev as primary, a reasoning-model smart tier, an LLM fallback chain, and durable operational choices around batching, privacy-preserving analytics, rate limiting, and agent discovery[^classifier-dev-docs].

## API shape

- Zero-shot entry points are **reported**: path form `curl https://classifier.dev/spam,not+spam/Win+a+free+iPhone` → `spam`, and an equivalent GET query form with `?labels=...&text=...`[^classifier-dev-docs].
- `POST /v1/classify` accepts ordinary batches plus `items` with `dimensions`, each `results[i].dimensions[name]` carrying its own label, confidence, scores, model, and latency; limits are **reported** as up to 1,000 texts per request, 1,000 decisions, and 20 dimensions, with each decision charged to quota[^classifier-dev-docs].
- Multimodal-style Jev dimensions share state across item–dimension questions; a question group is the smallest unit recovery keeps together — one input's questions for ordinary classification, one decision for dimensions — with shared input text counted once and execution split across question groups[^classifier-dev-docs].
- The site is single-sourced: `curl classifier.dev` returns canonical plain text while browsers sending `Accept: text/html` get the same `DOCS` and `BENCHMARK` documents rendered, with `?format=text` opt-out and `Vary: accept` on both responses[^classifier-dev-docs].

## Model, tiers, and calibration

- Both tiers answer from TypeSafe's Jev, described as a decision model returning calibrated per-option probabilities in ~150ms rather than a language model[^classifier-dev-docs].
- Batching packs `state` as `{id, text}` with one question per input in a single upstream call under a conservative token budget, running eight requests concurrently; **reported** measurements are 400 news headlines in 650 ms end to end with 100-item packing scoring the same as one-at-a-time[^classifier-dev-docs].
- Confidence behavior is **reported**: on 400 six-way emotion items, answers at ≥0.9 confidence were right 82% of the time versus 29% below 0.5, while the prior model's logprob confidence put 87% of news items above 0.9 and was right on 68% of those[^classifier-dev-docs].
- `tier: "smart"` is **reported** as re-asking single-label answers below 0.7 confidence from a fast reasoning model and replacing them marked `escalated: true`; on exactly the items Jev is unsure about, the selected chain is gemini-3.8-flash (news 87.5%→90.0%, emotion 61.8%→63.7%), with a frontier alternative at 72.3%/90.7% and ~3× price listed on `/benchmark`[^classifier-dev-docs].
- Multi-label is one yes/no question per label in one pass, returning labels at ≥0.7 most-likely-first with the full score map; **reported** F1 0.887 over seven cases versus 0.799 for the replaced sweep-and-verify LLM cascade, in 230 ms instead of 1.5 s, with reasoning-model re-judging making it worse and slower, so multi-label ignores the tier[^classifier-dev-docs].
- The LLM chains remain as fallback when TypeSafe is unavailable, limited to 20 inputs because they are one call per input; the digest marks which model answered with a `FALLBACK` marker after an earlier primary was delisted upstream and silently served backup at F1 0.546 for weeks[^classifier-dev-docs].
- Provider order is gateway-first when configured: Vercel AI Gateway serving Jev on free monthly credit is asked first when its key is set, with TypeSafe direct catching refusals; production is currently pinned to TypeSafe direct via `AI_GATEWAY_DISABLED = "true"` after repeated gateway 429s, with gateway-first restoration conditioned on verified capacity[^classifier-dev-docs].

## Long context

- Inputs over 32,000 characters on default or explicit `model: "jev"` use Chonkie RecursiveChunker 600-token `cl100k_base` chunks, parallel Jev screening for relevant or uncertain evidence including opposing evidence and exceptions, then final Jev over whole eligible chunks in source order under a 20,000-token evidence budget; eligible chunks may be omitted when the budget fills and `usage.long_context` reports selection counts, tokens, calls, and timing[^classifier-dev-docs].
- Synchronous Fast-path limits are **reported**: workspace key backed by paid balance or active paid subscription, 250,000 original context tokens summed across inputs, 20 documents, 32 decisions, 1 MB body, retail $0.084/M original `cl100k_base` tokens counted once across inputs, 8,192 UTF-16-code-unit cap per whitespace/non-whitespace run (`400 long_context_input`), and `422 long_context_no_evidence` without charge when no eligible evidence exists[^classifier-dev-docs].
- Whole-document async accepts up to 10 million input tokens (100 MB) to `POST /v1/classify` with a funded workspace key as normal JSON or `text/plain` with `labels` query parameter, returning `202` with `status_url` (`Prefer: respond-async` also works for smaller documents); source text is stored privately while queued and deleted as screened, with completion, failure, cancellation, and 24-hour expiry deleting remainders and refunds for failed or canceled work[^classifier-dev-docs].

## Operations: limiting, analytics, cost, alerts

- The Worker is described as a single Cloudflare Worker with no database, framework, or build step beyond esbuild; per-IP rate limiting is a Durable Object counting classifications at 3,000/min and 20,000/day fast plus 200/min and 2,000/day smart, after rejecting Cloudflare native `ratelimit` (never decremented in testing) and KV counters (edge-cached, eventually consistent)[^classifier-dev-docs].
- Every request writes one Analytics Engine datapoint without request text; long-context aggregates go to `classifier_long_context_events` without document text or caller identifiers, and Jev provider attempts go to `classifier_jev_attempts` through `JEV_AE` without input text, caller identifiers, or upstream messages[^classifier-dev-docs].
- Privacy is keyed hashing: caller IP and label set are keyed hashes with the UTC day mixed into the caller hash, so multi-day unique-caller counts are really caller-days; rotation renumbers fingerprints and double-counts across rotation, with fallback `PRIVACY_SALT` → `ADMIN_SIGNING_KEY` → `REPORT_KEY` → per-isolate random value[^classifier-dev-docs].
- Cost metering accumulates per-request upstream spend in `src/cost.ts` into `double3` from OpenRouter-returned charges and Jev input-token billing at the `eval/bench.py` benchmark rate; dimension traffic adds `blob9` and `double6`–`double9` fields with dimension configurations stored only as keyed fingerprints[^classifier-dev-docs].
- A 15:00 UTC cron emails a Resend digest while a separate 15-minute cron stays silent unless a condition fires: Jev key refused or not answering, 5xx rates, smart-escalation failures, mean latency, spend spike versus trailing day, traffic stopping, Jev-credit probe failures, provider-attempt failures (≥3 and >5% per provider), and dimension 5xx/fallback usage; each condition emails on start, every six hours while active, and on clear with state under `alert:`[^classifier-dev-docs].
- TypeSafe publishes no balance endpoint, so the credit check probes `/v1/models` with the key every 15 minutes and raises critical on 401/402/403 quoting TypeSafe's message; report and alert previews require `Authorization: Bearer $REPORT_KEY` header only, with `?demo=1&send=1` and `?send=1` gating actual email[^classifier-dev-docs].

## Deploy, secrets, and data boundaries

- Merging to `main` deploys via typecheck, Worker plus CLI tests, `wrangler deploy`, then live `/v1/health` and one classification so a broken Worker fails CI; manual deploy copies `wrangler.example.toml` to gitignored `wrangler.toml` and fills account-specific `account_id` and `STATS` KV id, while CI renders `wrangler.toml` from the example plus secrets so the example stays the deployed shape[^classifier-dev-docs].
- Worker secret names only — no values are stored here: `TYPESAFE_API_KEY`, `AI_GATEWAY_API_KEY`, `OPENROUTER_API_KEY`, `CONTEXT_API_KEY`, `RESEND_API_KEY`, `CF_ANALYTICS_TOKEN`, `REPORT_KEY`, `PRIVACY_SALT`, plus newsletter/database names below; secrets are compared with `secretEquals`, never `===`[^classifier-dev-docs].
- Newsletter subscription is double opt-in: form plus `POST /subscribe` returns `202 {"ok":true,"status":"pending_confirmation"}` with no database write until the emailed token reaches `POST /subscribe/confirm`; tokens are signed with `NEWSLETTER_CONFIRMATION_SECRET`, expire within 24 hours, ride roadmap ticks in the token, and rotation invalidates outstanding links[^classifier-dev-docs].
- Subscriber storage holds email, source, signup/confirmation/unsubscribe dates, `wants text[]` roadmap keys, requested latency, and internal id — explicitly no IP, request id, or classification traffic — sharing the application `DATABASE_URL` without subscribing account holders or changing consent[^classifier-dev-docs].
- DNS is split Porkbun registrar plus Cloudflare Worker with one manual zone step plus `./finish-dns.sh` for nameservers and apex/`www` attachment; the copy source is one `ROADMAP` constant read by plain text, rendered page, and `index.md`[^classifier-dev-docs].

## Agent, CLI, eval, and discovery surfaces

- The `classify` CLI is a separate dependency-free npm package (`classifier-dev`, bin `classify`) talking to the API like curl, with mock-API tests and semver releases tagging `cli-v<version>` for publish via `NPM_TOKEN`; the repository CLI also handles document upload and polling via `--document ... --json`[^classifier-dev-docs].
- Eval entry points are **reported**: `npm run bench` for seven-case multi-label, `npm run single -- --dataset emotion|ag_news --backend jev|openrouter:...` with first-use AG News/emotion downloads cached under `eval/data/results/`, and `python3 eval/escalate.py --dataset emotion` for smart-tier value; live TypeScript e2e runs against production or `CLASSIFIER_BASE_URL` with real inference counting toward quotas[^classifier-dev-docs].
- Agent skill discovery is served from the domain: `src/SKILL.md` artifact at `GET /skill.md` plus `GET /.well-known/agent-skills/index.json` (schema v0.2.0) with per-isolate sha256 hashing so editing `SKILL.md` is sufficient; the skill's stated reason to call out is context rather than capability, with hard-won notes to set an explicit `urllib` User-Agent for Cloudflare 403s and to instruct "when in doubt, keep it"[^classifier-dev-docs].
- Agent feedback implements `feedback.now` schema 1.1 (`/.well-known/agent-feedback.json`, `/api/v1/policy`, `/feedback`, `/observations`, `/feedback/{id}/attachments`, `/receipts/{id}`), emailing accepted reports to `REPORT_TO`, keeping them 90 days in KV, deduplicating domain+surface+category+title repeats without re-emailing, budgeting 100 per IP per hour, and scoring completeness deterministically via `quality_score`[^classifier-dev-docs].
- Discovery surfaces are `GET /openapi.json` (also `/.well-known/openapi.json`), `GET /llms.txt` linked from `robots.txt`, and `GET /benchmark` with measured accuracy, cost, and latency, all linked from the landing page's third paragraph[^classifier-dev-docs].
- **Reported** Cloudflare managed-robots limitation: enabling the zone prepends an AI Crawl Control block disallowing GPTBot, ClaudeBot, CCBot, Google-Extended, Bytespider, Amazonbot, and meta-externalagent ahead of the Worker's own `robots.txt`, blocking training crawlers but not runtime API use; dashboard toggles did not persist at the time of writing[^classifier-dev-docs].
- Operator bulk access uses a dedicated `AGENT_API_KEY` Bearer secret with unmetered classification quotas but a shared $2/day operator inference allowance, neither consuming nor expanding anonymous allowance and not authorizing reports or admin; funded bulk keys use `API_KEY_RATE_LIMIT_MULTIPLIERS` mapping SHA-256 key digests to 1–1,000× admission-quota multipliers[^classifier-dev-docs].

## Relationships

- Uses [Jev Decision Model](jev-decision-model.md) as its primary decision engine and fallback context.
- Uses [Jev API Patterns](jev-api-patterns.md) for choice, noul, and score invocation shapes.
- Requires [Classifier Calibration](classifier-calibration.md) for interpreting the 0.7/0.9 confidence thresholds and multi-label cutoffs.
- Informs [Classifier Selection](classifier-selection.md) as a buy-or-call hosted option versus clones and specialists.

## Coverage limits

- Static inspection of `../raw/classifier.dev.md` only; no code execution, live API calls, or benchmark reproduction was performed here.
- Referenced `src/*` modules, `CONTEXT.md`, `wrangler.example.toml`, migrations, `docs/postgres-setup.md`, `eval/README.md`, and linked upstream docs were not inspected; treat file-level behaviors, line-level symbols, and benchmark numbers as **reported**.
- Quotas, prices ($0.084/M, $2/day operator allowance), gateway flags, secret names, cron schedules, and crawler-control behavior are time-sensitive; verify against live docs and `/benchmark` before building or buying.
- Secret names above are redacted identifiers only; no secret values, tokens, emails, or caller data are stored here.

[^classifier-dev-docs]: classifier.dev service documentation, canonical local entry `../raw/classifier.dev.md`. Locators in text: top curl examples; `CLI`, `Layout`, `The site`, `Agent feedback`, `Deploy`, `The model`, `Updates list`, `Jev long context`, `Analytics`/`Alerts`/`Privacy`, `Eval`, `Rate limiting`, `DNS`, `Agent skill`, `Discovery surfaces`, `Known issue`, `Operator agent access`, `Finding the classification code`, `Multiple dimensions` sections.
