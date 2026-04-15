# Scheduled Maintenance Trigger Pattern

This repository supports **external scheduled maintenance triggers** through a small queue file plus a local pi extension.

The goal is to keep automation explicit and narrow:

- the scheduler decides **when** to request maintenance
- the extension bridges that request into pi
- the actual semantic work still happens in the normal prompts and skills

## What is implemented

### Queue file
Scheduled requests are written to:

- `.pi/state/maintenance-triggers.json`

Each trigger records:

- task
- mode (`notify` or `run`)
- created time
- optional reason
- requester label

### Extension bridge
The local extension:

- watches `.pi/state/maintenance-triggers.json` while pi is running
- supports these tasks:
  - `/review`
  - `/lint`
  - `/retention-pass`
  - `/privacy-scan`
- handles two modes:
  - `notify` = show a reminder in pi
  - `run` = enqueue the actual slash command in pi

### Opt-in commands inside pi
- `/maintenance-status`
- `/maintenance-trigger <task> [notify|run] [reason]`
- `/maintenance-run <task> [reason]`

Examples:

- `/maintenance-status`
- `/maintenance-trigger review notify weekly-review`
- `/maintenance-run lint monthly-cleanup`

## External trigger script
Use this helper from the repo root:

```bash
node .pi/scripts/trigger-maintenance.mjs review --reason weekly-cron
node .pi/scripts/trigger-maintenance.mjs lint --mode run --reason monthly-systemd
```

## Recommended modes

### `notify`
Use when you want a reminder during an interactive pi session.

Good default for:
- weekly review
- monthly privacy scan
- monthly retention pass

### `run`
Use only when you explicitly want pi to enqueue the maintenance workflow automatically.

Good for:
- controlled personal automation
- deliberate scheduled runs where the repository owner expects it

## Operational constraints

This works best in one of two ways:

1. **pi is already running**
   - the extension watcher sees the queue file change
   - pi notifies or enqueues the workflow

2. **an external scheduler writes triggers while pi is not running**
   - the requests remain in the queue file
   - they are processed the next time pi starts

## Cron example

```cron
# Weekly review reminder every Monday at 09:00
0 9 * * 1 cd /home/hiennx/Documents/llm-wiki && node .pi/scripts/trigger-maintenance.mjs review --reason weekly-cron

# Monthly lint auto-run on the first day at 10:00
0 10 1 * * cd /home/hiennx/Documents/llm-wiki && node .pi/scripts/trigger-maintenance.mjs lint --mode run --reason monthly-cron
```

## systemd user timer idea

Use a user service that runs:

```bash
cd /home/hiennx/Documents/llm-wiki
node .pi/scripts/trigger-maintenance.mjs review --reason weekly-systemd
```

Then pair it with a `.timer` unit on the cadence you want.

## Safety stance

This layer is intentionally narrow.
It does **not** decide:

- what findings matter
- how contradictions should be resolved
- what belongs in `wiki/`
- how canonical knowledge should change

It only bridges explicit maintenance requests into the existing prompt/skill workflows.
