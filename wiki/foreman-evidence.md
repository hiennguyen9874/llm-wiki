---
type: Concept
title: Foreman Evidence and Request Budgets
description: Foreman selects bounded evidence per check, compacts model requests, and can run centrally configured trusted evidence commands.
tags: [foreman, evidence, security]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:50:51Z }
sources:
  - id: foreman
    resource: ../raw/foreman/README.md
    scope: ../raw/foreman/
    kind: code
    revision: c3142ef636617f32f772140125aa310d81ceece9
    title: Foreman
---

**Reported:** [Foreman](foreman-overview.md) separates evidence collection from model judgment. Built-in selections include workers, Git status and diffs, bounded untracked excerpts, repository instructions, tests, verification, events, and history. Omitted `evidence` selects all built-ins; an explicit list is the entire selection. Different selections require separate model calls.[^foreman]

## Budget and omissions

Default hard budgets are 30,000 bytes for state plus the longest question and 60,000 bytes for the whole request, with soft targets of 12,000 and 24,000 bytes. These JSON byte counts are proxies, not token counts. Compaction removes oldest history and shortens bulky material, while preserving essential work and current operation; it reports omissions as unknown, not success. If essential inputs cannot fit, the request fails locally.[^foreman]

Untracked content is bounded and the documented collector skips binary-looking, unreadable, sensitive-name, symlink and escaping paths. This is a filter, not a guarantee that all sensitive content is detected. Repository instructions are included in transient decision requests according to the README.[^foreman]

## Command safety

Centrally configured referenced providers execute sequentially as argv without an implicit shell, in the target repository. They run at successful managed worker completion or attached stop, and return bounded output, status, and exit code for the check to interpret—not automatic pass/fail policy. They inherit Foreman's OS permissions and environment and may execute repository-controlled code, so they require trust and review.[^foreman]

**Coverage limit:** Documentation-led findings; collector, budget and command implementations and tests are pending, and no command provider was executed.[^foreman]

[^foreman]: `docs/evidence.md` §§ Built-in providers and the default, Decision model request budgets, Command providers, Safety boundary; `docs/runtime.md` § Untracked-file evidence; `README.md` § What Foreman watches.
