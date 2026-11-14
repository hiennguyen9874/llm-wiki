---
type: Concept
title: Pi Orbs Security and Approval Boundaries
description: Pi Orbs exposes a public Sprite endpoint while separating local credentials, gateway keys, webhook authentication, and command approvals.
tags: [pi-orbs, security]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: '2026-11-14T15:54:17Z' }
sources:
  - id: pi-orbs
    resource: ../raw/pi-orbs/README.md
    scope: ../raw/pi-orbs/
    kind: code
    revision: 6a2ab3b507504045bedf7a6837047d62c2c8f42d
    title: Pi Orbs
---

**Reported:** [Pi Orbs](pi-orbs-overview.md) makes the Sprite URL public; normal bot API access uses a generated secret while `/version` is public. The local state file contains sensitive Sprites, connector, service, and optional integration credentials and must remain private.[^pi-orbs]

## Distinct boundaries

- Model requests use a Sprites gateway connection that holds the connector key; the service receives placeholder model-key values instead. Existing named connections are reused as-is, so changing a key in a retry does not necessarily update the connection.[^pi-orbs]
- A voice key stays on the client, although the browser receives a short-lived session token. The optional cron service key is also placed in the Sprite service environment and saved alongside the roster for settings changes. Per-bot webhook URLs contain bearer-like tokens; signed MCP event hooks use an additional signature.[^pi-orbs]
- Bash commands are subject to review: allow-once applies to an exact command and always-allow to a class for that bot until revoked. Bots share the workspace, so separate threads are not separate filesystem isolation boundaries. **Synthesis:** these controls should not be mistaken for comprehensive isolation.[^pi-orbs]
- Bot vault secrets are not returned through the listing or intentionally written to chat; documented transcript, search, template and export redaction applies to saved values of at least 16 characters. Do not assume shorter values are redacted.[^pi-orbs]

## Coverage and limits

Security and architecture documents were read; server authentication was searched but not comprehensively audited. These are reported design claims, not a security assessment. Client and server implementation, tests, and dependency behavior remain pending; no deployed system was tested. Security documentation's broad description of authenticated routes must be read alongside its architecture's token-authenticated webhook exceptions.[^pi-orbs]

## Relationships

- [Integrations](pi-orbs-integrations.md) explains webhook and voice data flows.
- [Coordination](pi-orbs-coordination.md) explains the shared bot workspace and peer communication.

[^pi-orbs]: `SECURITY.md` § API secrets and the xAI key; `docs/architecture.md` §§ State, Connector, Voice, Scheduled messages, Bots and `/home/sprite/work`, Search, templates, memory, secrets, review, and the Main Bot, Troubleshooting.
