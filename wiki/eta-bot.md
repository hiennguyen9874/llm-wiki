---
type: Concept
title: Eta Bot Operation and Recovery
description: Eta Bot hosts remote agent threads with request deduplication, snapshot streaming, recovery controls, and optional Discord intake.
tags: [eta, agents, deployment]
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

**Reported:** Eta Bot runs a separately persisted remote agent service, serving HTTP and SSE and optionally accepting Discord issues. It defaults to loopback port 8080; remote access should go through an HTTPS reverse proxy. Desktop connects to one Bot at a time and local and cloud histories are separate.[^eta]

## Admission, recovery and backup

**Reported:** create threads and submit messages using request IDs. A `202` means the input was saved, not that execution completed; query the operation ID for the result. Retrying the same ID and payload handles network uncertainty, while a different payload produces `409`; Busy means not admitted. SSE reconnects to the latest snapshot rather than replaying every event. Safe pending work resumes on startup, but interrupted tools with uncertain side effects and missing task definitions need maintainer review. Blocked recovery reserves the project checkout.[^eta]

Back up the entire data volume after stopping the Bot, including catalog/session data and Bot and Discord databases, plus project checkouts separately. Use one replica per data root. **Reported:** restoring only session files loses deduplication and delivery state.[^eta]

## Discord and delivery

**Reported:** eligible channel messages create a Discord thread and an Eta thread; subsequent thread messages queue. Backfill is bounded and inaccessible or deleted messages cannot be recovered. Delivery uses saved IDs and stable markers to reconcile uncertain sends, and ambiguous outcomes may require human review; it is not an end-to-end exactly-once guarantee. Disabling the extension retains its task definitions, while removing its configuration can block recovery.[^eta]

## Documentation conflict and coverage

The same Bot README says model credentials are persisted and not configured through environment variables, but its Docker paragraph says to supply provider keys through the deployment environment. These statements are unresolved; inspect the implementation and current deployment configuration before relying on either. Implementation, API tests, deployment files, mobile guide, and other repository materials remain pending; no Bot commands or tests were run.[^eta]

## Relationships

- **Related:** [Eta architecture](eta-overview.md) distinguishes local and cloud state; [Eta security](eta-security.md) describes sandbox and approval limits.

[^eta]: `apps/bot/README.md` §§ introduction, Sandbox, Desktop connection, Discord issues; paragraphs on HTTP admission, SSE, Docker and backup.
