---
type: Concept
title: Hindsight control plane
description: "The Next.js web UI for Hindsight: stack, views, how it proxies to the API, authentication and environment variables."
tags: [agent-memory, hindsight, ui, nextjs]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: cp-package
    resource: ../raw/hindsight/hindsight-control-plane/package.json
    kind: code
    revision: eb963cb
    title: Control plane package manifest
---

The control plane is the web UI (default `http://localhost:9999`) for browsing and operating Hindsight banks; the README's Docker quick start exposes API on 8888 and UI on 9999.[^readme] It ships as the npm package `@vectorize-io/hindsight-control-plane` (bin `./bin/cli.js`) and as a Docker target.[^cp-package]

## Stack and structure (Observed)

- Next.js 16 App Router, React 19, TypeScript 5.9, Tailwind 4 + shadcn/ui, `next-intl` with 10 locales; standalone build output.[^cp-package]
- Pages: `/dashboard` (all banks), `/login`, `/banks/[bankId]` — one client component switching on `?view=` (home, profile, recall, reflect, data, documents, entities, knowledge with Pages and Mental Models tabs, plus stats, operations, webhooks, audit logs, LLM requests, bank config, memory defense, search debug).[^cp-package]
- Data path: browser → Next route handlers `src/app/api/**/route.ts` (~70) → dataplane via the generated TypeScript client (`src/lib/hindsight-client.ts`); see [Clients and CLI](hindsight-clients-cli-embed.md).[^cp-package]
- Feature gating: `/api/version` returns a `features` map (observations, mcp, worker, bank_config_api, audit_log, llm_trace, …) read by `src/lib/features-context.tsx`.[^cp-package]

## Auth and configuration

Optional `HINDSIGHT_CP_ACCESS_KEY` gates the UI with an HMAC-signed 24 h cookie (`hindsight_cp_access`); public paths are `/login`, `/api/auth/`, `/api/health`, `/api/version`. Env: `HINDSIGHT_CP_DATAPLANE_API_URL` (default `http://localhost:8888`), `HINDSIGHT_CP_DATAPLANE_API_KEY`, `HINDSIGHT_CP_MAX_UPLOAD_SIZE` (default `100mb`), `NEXT_PUBLIC_BASE_PATH`, `PORT`, `HOSTNAME`. The Helm chart runs it on port 3000 instead of 9999 (see [Deployment](hindsight-deployment-and-ci.md)).[^cp-package]

## Tests and rules

Vitest suites under `tests/`, ESLint and a `knip` dead-code gate. A project-local `AGENTS.md` warns the Next.js version differs from model training data. New API routes need a route handler, type updates in `src/lib/api.ts` and UI consumers ([Contributor workflow](hindsight-contributor-workflow.md)).[^cp-package]

## Relationships

Depends on the [API surface](hindsight-api-surface.md); administers [banks](hindsight-memory-banks.md).

[^readme]: `README.md` § "Quick Start → Docker" (UI: http://localhost:9999).
[^cp-package]: `hindsight-control-plane/package.json`, `next.config.ts`, `src/middleware.ts`, `src/lib/auth/session.ts`, `src/lib/hindsight-client.ts`, `src/lib/features-context.tsx`, `src/app/[locale]/`.
