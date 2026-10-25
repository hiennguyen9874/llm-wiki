---
type: Concept
title: "Home, Cloud, and Durable Agents: Where Work Runs and Whether It Survives"
description: A comparison of running coding agents on your own machine versus a cloud virtual machine, and why durability is an orthogonal harness layer that resumes work after process death rather than a third place to run.
tags: [agent-deployment, cloud-agents, durable-agents, agent-harness]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:14:17Z }
stale_after: 2027-01-25
sources:
  - id: cloud-agents-durable-agents-video
    resource: ../raw/CloudAgentsAndDurableAgents.md
    kind: video-transcript
    title: "Cloud Agents và Durable Agents – Lại một Meta mới rồi! (YouTube)"
---

Running an agent at home or on a cloud virtual machine changes *where* the work happens, not *whether it survives*: both are live processes, and a stopped process takes the unfinished job with it. The talk separates these into two independent axes — a placement decision (own machine vs rented VM, with different trust, trigger, and environment costs) and a durability decision (does a ledger record each step so a new process resumes from the last checkpoint). Its worked example is a multi-step release whose data backfill loses its place when a laptop closes; cloud keeps the process alive but cannot tell a restarted agent how far a migration got, whereas the Pi Durable ledger can.[^cloud-agents-durable-agents-video]

## Two axes, three placements

| Placement | Runs on | Started by | Stops when | Survives process death |
| --- | --- | --- | --- | --- |
| **Home agent** | Your own machine, sharing the repository, terminal, and configuration you already use | You, typing a prompt | The machine sleeps, closes, or shuts down | No |
| **Cloud agent** | A rented VM per task that clones the repository and installs its own dependencies | You, or a trigger — an assigned issue, a red CI pipeline, an alert, a schedule | The VM is stopped or evicted; your laptop is irrelevant | No, on its own |
| **Durable agent** | Either of the above, plus a recording layer | The same entries, but the ledger decides the next step | The process may die; a new process continues from the recorded checkpoint | Yes, up to the last committed step |

The talk's framing is that durability is "a new harness layer", not a way to make the model smarter: a wrong model still produces wrong work, but the work is no longer silently lost.[^cloud-agents-durable-agents-video] That matches the [Pi Durable harness](pi-durable-overview.md), whose commits precede display and whose [tasks](pi-durable-tasks.md) checkpoint each phase.

## Home agents: convenience bought with privilege

A home agent is the familiar setup: Claude Code, Codex, Pi, or similar running on the same PC, using the same repository, terminal, and config files, which makes it fast and immediately useful for pairing on a problem. The costs are environmental and physical. It runs with the human's own privileges, so it can read SSH keys, cookies, and environment files, and a destructive command can erase local data. It also stops with the machine: closing a laptop for a meeting interrupts whatever it was doing.[^cloud-agents-durable-agents-video]

## Cloud agents: triggers and an environment written down

A cloud agent gets its own machine, works independently of the human's computer, and keeps going while the human sleeps. Because the human is no longer at the keyboard, the interesting question becomes who starts it: the talk lists an assigned issue, a failing CI/CD pipeline, an error alert, or a schedule, and sketches a 3 a.m. production incident where the agent investigates, opens a pull request, and leaves only the review for the morning. It reports that providers are competing on cloud agents and on VMs with very small boot times — "under 1 ms" as stated — a figure treated as unverified below.[^cloud-agents-durable-agents-video]

The second benefit is that the environment has to be written down, like a Dockerfile with every prerequisite and tool, so every run and every person gets the same setup instead of "works on my machine". That artifact also shortens a new teammate's first day.[^cloud-agents-durable-agents-video]

The costs are symmetrical:[^cloud-agents-durable-agents-video]

- **Environment construction** is real work, especially for a backend with several databases and internal services.
- **Feedback is slower** than a local loop, and access has to be granted per machine.
- **Spend** is direct and per-VM.
- **The bottleneck moves to review**: the volume of pull requests a human must read becomes the limit.

## Which task belongs where

The talk treats the two placements as different niches rather than competitors:[^cloud-agents-durable-agents-video]

| Prefer a home agent for | Prefer a cloud agent for |
| --- | --- |
| Brainstorming, joint design of a hard problem | Work already specified precisely |
| Debugging a difficult bug in one area of code | Issue-shaped work with a defined fix mechanism |
| Exploring a new idea interactively | Writing tests, upgrading dependencies, mass refactors |
| Anything where the local feedback loop is the value | Trying several approaches in parallel |

## Where both placements fail

Both are live processes, so a hang, a block, or a crash collapses the work in progress. The talk's example is a game release: add a column to the player table, backfill about five million rows, deploy, get lead approval, then open the servers to players — and the backfill must finish first.[^cloud-agents-durable-agents-video]

Run by a home agent from 10:00, the backfill reaches roughly three million rows by mid-afternoon, then the laptop is closed for a meeting and the process stops. On return nobody knows how far it got; the only way to find out is to open the database, check, and tell the agent where to resume.[^cloud-agents-durable-agents-video]

The cloud avoids the closed laptop but not the failure class: the VM can run out of resources or be restarted, and the replacement agent then has only the conversation history — the transcript, the tool calls — with no record of where the deploy or migration actually got to. Rerunning the migration may apply it twice, unless the script was written to defend against exactly that.[^cloud-agents-durable-agents-video]

## What the durability layer adds

Pi Durable's answer in the talk is a ledger — a book of record for each step the agent took. The backfill example marks "batch 3000 of 5000 done, about to deploy version 2.4"; when the machine dies, a fresh process reads the last entry and starts at batch 3001, then deploys with the strategy that was intended, and continues once the approval arrives.[^cloud-agents-durable-agents-video]

Durability does not make dangerous tools safe. The talk quotes the author of Pi: rerunning an unsafe batch command is not acceptable, while rerunning a fresh sub-agent is fine, and anything like a deploy, a money transfer, or an email still needs an idempotency mechanism and careful validation before a repeat. Those per-operation rules are compiled in [replay safety and external effects](pi-durable-replay-safety.md).[^cloud-agents-durable-agents-video]

The price is that every step now passes through a recording layer, which makes the system more complex. The talk therefore scopes the payoff: durability is worth it when the agent must survive, when runs are very long, or when work may sit pending for days waiting on a decision before it continues.[^cloud-agents-durable-agents-video]

It also changes what "resume" means. A conventional chat-based agent can be resumed, but only from a transcript of all prior history and tool calls, and it often cannot reproduce the earlier result; a durable resume starts from the latest recorded state and continues from the missing point instead of re-reading the whole history. The talk adds that this also helps summarize and bound context, because the record says where the run stands.[^cloud-agents-durable-agents-video]

## Evidence and limits

**Reported** throughout: the source is a single speaker's comparison video, captured as a transcript with no headings, no timestamps, and no publication date, and nothing in it was executed or measured here. The **Synthesis** is the two-axis framing in the first table and the claim that placement and durability are independent choices; the speaker presents the ideas but not that table.

Concrete limits:

- The transcript is machine-generated Vietnamese and garbles several proper nouns. Product names are therefore described by role ("coding agents", "specialized personal-assistant agents", "packaged agent products") rather than asserted; the specific products are not relied on.
- The claimed sub-millisecond VM boot time is **Unverified** and implausible as stated, probably a garbled cold-start figure. It should not be quoted as fact.
- The backfill numbers (five million rows, three million by mid-afternoon) are one illustrative anecdote with no timings or measurements.
- The characterization of transcript-based resume as unable to reproduce results is the speaker's claim; it is not checked here against any particular product, and the Pi Durable mechanics behind the ledger claim are in [crash recovery](pi-durable-crash-recovery.md) and [tasks](pi-durable-tasks.md), not in this source.
- Coverage: the file is a self-contained transcript plus its YouTube URL; there are no attachments, includes, or supporting artifacts, and the video itself was not watched, so anything said on screen or omitted by transcription is unavailable. The speaker mentions a comparison table prepared for the video; it was not captured.

## Relationships

- **Positions** the [Pi Durable overview](pi-durable-overview.md) as a durability layer that composes with either placement, not as a third runtime location.
- **Explains the deployment motivation for** [Pi Durable on Cloudflare Durable Objects](pi-durable-on-cloudflare.md), where the cloud host can evict the process at any time.
- **Depends on** [crash recovery](pi-durable-crash-recovery.md) and [task checkpoints](pi-durable-tasks.md) for the resume mechanics it describes abstractly.
- **Constrains** which repeated operations are safe, detailed in [replay safety and external effects](pi-durable-replay-safety.md).
- **Contrasts with** stateless chat-style agent usage, whose only recovery source is the transcript.

[^cloud-agents-durable-agents-video]: YouTube talk “Cloud Agents và Durable Agents – Lại một Meta mới rồi!” (`raw/CloudAgentsAndDurableAgents.md`; <https://www.youtube.com/watch?v=GFJQsPb5nqw>), locators by quoted phrase because the captured transcript has no headings or timestamps: home agent “Mình gọi một cái tên vui là Home Agent”, “SSH key, cookie trong file environment”, “gập máy mình đi họp”; cloud agent “được đưa lên một cái virtual machine”, “đánh thức khi mà có một cái chuyện gì đấy nó xảy ra”, “nửa đêm, 3:00 sáng”, “boot time nhỏ hơn 1 ms”, “giống như một cái dockerfile”, “on board một cái bạn mới”, “cái nút thắt nó đang chuyển dịch sang cho mình”; release backfill “backfill khoảng độ 5 triệu dòng”, “được khoảng 3 triệu dòng”, “hết resource rồi nó nghẽn rồi nó bị restart”, “chỉ còn những cái lịch sử trò chuyện thôi”, “rất có thể là cứ bị migrate nhầm”; durable agent “một cái ledger là một cái sổ cái”, “batch 3000/5000”, “bắt đầu cái batch từ 3001”, “một cái tầng harness mới”, “chạy lại một cái lệnh batch không an toàn”, “process idempotency”, “chờ những cái decision vài ngày”, “gửi dưới dạng … transcript”, “bắt đầu từ cái điểm gọi là missing point”.
