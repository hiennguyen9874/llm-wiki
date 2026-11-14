---
type: Concept
title: Eta Sandbox and Approval Boundaries
description: Eta's local and Bot execution modes differ in defaults, approval review, operating-system support, and full-access risks.
tags: [eta, security, agents]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:53:01Z }
sources:
  - id: eta
    resource: ../raw/eta/README.md
    scope: ../raw/eta/
    kind: code
    revision: fc520e4ef2a2ec8a23613e39a2a5181330673856
    title: Eta repository
---

**Reported:** Eta offers read-only, workspace-write and full-access execution. A new local desktop session defaults to full access unless a preference is saved; Bot threads default to workspace-write. Workspace-write allows workspace edits and network, with outside access subject to approval. Full access removes agent file and command filesystem and network boundaries and can reach Eta data; it is not a scheduled-task storage isolation guarantee.[^eta]

## Approval and platform limits

**Reported:** both desktop and Bot default to automatic model review of out-of-bound requests, with a user-review option. Review cannot expand the requested scope; certain sensitive requests, including other repositories' Git metadata or the entire home directory, go to the user. Approved temporary grants expire on stop or restart. The Bot's default allowlist includes full access unless deployment restricts it; the managed deployment defaults to excluding it. Existing threads retain their policies.[^eta]

**Reported:** restricted execution works on supported macOS and Linux backends but not current Windows; backend failure blocks restricted work rather than silently switching to full access. Bot's Linux container uses Landlock/seccomp, requires Landlock ABI 3 or newer, and rejects overlapping project and protected application-data roots. Runtime extensions are trusted host code. Experimental desktop control can affect other apps outside the workspace filesystem sandbox.[^eta]

## Limits

These are documentation claims, not a security audit: implementation, test suite, OS behavior, and deployment configuration remain uninspected and no sandbox was executed. Review the source and current configuration before exposing or trusting a deployment.[^eta]

## Relationships

- **Related:** [Eta Bot operation](eta-bot.md) covers remote access and recovery; [Eta architecture](eta-overview.md) places the execution modes in the product.

[^eta]: `docs/user/sandbox.md` §§ 选择代理的访问范围, 自动审查, 联网与代理, 在 worktree 中提交; `apps/bot/README.md` § Sandbox; `docs/user/desktop.md` § Experimental desktop control.
