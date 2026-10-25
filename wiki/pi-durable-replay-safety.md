---
type: Concept
title: Pi Durable Replay Safety and External Effects
description: Why a reused requestId deduplicates submissions but not side effects, how interrupted tool calls recover, and the per-operation checks that keep email, pull requests, and deployments from repeating.
tags: [pi-durable, replay, idempotency, side-effects, tools]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:09:52Z }
stale_after: 2027-01-25
sources:
  - id: flaviocopes-pi-durable
    resource: ../raw/flaviocopes-pi-durable/index.md
    scope: ../raw/flaviocopes-pi-durable/
    kind: article
    title: "How to build agents that survive crashes with Pi Durable"
---

Durable recovery is not exactly-once execution. Pi Durable can deduplicate a submission and can refuse to rerun an interrupted tool call, but it cannot undo an external action or learn from its own database whether that action happened. A tool that sends an email or opens a pull request therefore needs an application-level answer before it may be declared replay-safe.[^flaviocopes-pi-durable]

## Three separate layers

| Layer | Mechanism | Protects | Does not protect |
| --- | --- | --- | --- |
| Submission admission | `requestId` reused by the client | One request becomes one submission and one run | Side effects of tool calls inside that run |
| Tool-call recovery | Replay policy of the tool; the article calls `unsafe` the default | Whether `execute()` runs again after an interruption | Repeated external effects, unless the implementation itself makes repeats harmless |
| External operation | Operation ID plus the provider's idempotency, or reconciliation against the external system | The outer effect happens once | Is not supplied by the harness |

Submission deduplication and tool idempotency solve different parts of the problem: a stable `requestId` alone does not make an external action happen exactly once.[^flaviocopes-pi-durable]

## What happens after an interrupted effectful call

Consider replacing a read-only fixture with an email sender. The provider accepts the message, then the process dies before Pi Durable commits the tool result. On restart the local database cannot tell whether the email went out, so automatically running the tool again could send a duplicate.[^flaviocopes-pi-durable]

With the unsafe default, the harness reports an interrupted result to the model instead of rerunning the call, but the model may request a fresh call anyway — so the application must still prevent a repeat of an action whose outcome is uncertain. For email or pull-request creation, pass an operation ID to the external service's idempotency mechanism where one exists; otherwise reconcile against the external system before allowing another attempt. If the outcome cannot be established, ask a person to resolve it. Declare an effectful tool replay-safe only once its implementation makes repeated execution safe.[^flaviocopes-pi-durable]

## Per-operation checklist

The article's decision table:[^flaviocopes-pi-durable]

| Operation | What to check before enabling replay |
| --- | --- |
| Read service status | Repeating the read is acceptable; the answer may have changed |
| Search issues | The search has no mutation; repeated queries may still cost money |
| Send an email | The sender deduplicates the same operation ID |
| Create a pull request | The application finds or reuses the existing operation's PR |
| Deploy a release | The deployment system reconciles the operation and its outcome |

This is guidance about the tool's semantics, not a property of the harness. A read-only tool with no external effect is the easy case; anything that mutates a remote system shifts the burden to that system's idempotency key or to a reconciliation step.[^flaviocopes-pi-durable]

## Atomicity boundary

A single commit can update the agent's own documents, append entries, and create tasks atomically — useful for recording an incident's investigation status alongside the transcript. That transaction covers Pi Durable's storage only; it does not include a remote GitHub or email API call, so the external effect and the local record can diverge.[^flaviocopes-pi-durable]

## Choosing and reusing request IDs

An ID should identify one logical job: reuse it when redelivering that job, mint a new one for a genuinely new job even with an identical prompt, and never reuse an old ID for a different prompt. For webhooks, derive it from a stable event identifier and keep an incident-to-investigation mapping, since one incident can arrive as several events. None of this makes the investigation's tools idempotent.[^flaviocopes-pi-durable]

## Evidence and limits

This is **Reported** guidance from a practitioner tutorial (published 2026-10-16) plus **Synthesis** of its two deduplication mechanisms; no crash, duplicate email, or reconciliation was attempted here, and the table's per-provider claims were not verified. Which providers offer idempotency keys, and how long they retain them, is outside the source and remains an application-specific check.

## Relationships

- **Constrains** which [tools](pi-durable-tools-nested-calls.md) may set `replay: "safe"` and how effectful ones must be written.
- **Complements** the `requestId` admission rule in [crash recovery](pi-durable-crash-recovery.md) and [conversations](pi-durable-conversations.md).
- **Applies to** the webhook and pull-request flow sketched in the [build and crash-test recipe](pi-durable-build-crash-test.md).
- **Depends on** application state kept in [documents](pi-durable-documents.md) when the external system cannot answer whether the operation happened.
- **Is the external-effect layer of** [the effect sandwich](pi-durable-effect-sandwich.md), whose GitHub Actions run key is the pre-minted operation ID.

[^flaviocopes-pi-durable]: Flavio Copes, “How to build agents that survive crashes with Pi Durable” (`raw/flaviocopes-pi-durable/index.md`, published 2026-10-16), locators: §Retry a request without creating a second job, §Decide which tools may run again, §Separate the transcript from the work, §From this demo to an agent that investigates errors.
