---
type: Concept
title: Pydantic AI pending batch responses
description: How a Pydantic AI batched run stops waiting — PendingModelResponse in output_type, the stored history that records the batch, what resuming requires, how usage and credentials behave across submit and collect, and what happens when the provider's retention expires.
tags: [pydantic-ai, capabilities, models, batching, durable-history]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:25:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-batch-2026
    resource: ../raw/core-concepts/batch/index.md
    scope: ../raw/core-concepts/batch/
    kind: documentation
    revision: sha256:53d4b659984b6eae8adbebe06233751631e17a8e05d828ffab66252c2232be08
    title: "Batch Processing"
---

**Reported, Pydantic AI version unspecified:** a batch can take hours, which is longer than many processes should live, so Pydantic AI splits a batched run in two by putting `PendingModelResponse` in the agent's `output_type`[^pydantic-batch-2026] A run then ends as soon as its request has been **submitted**, returning a `PendingModelResponse` as its output, and its message history ends in that pending response, which records the batch[^pydantic-batch-2026] Store the history, run the agent with it again later — in this process or another — and that run checks the batch once: if the result has arrived it continues as usual, and otherwise it ends with a `PendingModelResponse` again[^pydantic-batch-2026] The mechanism is the same one [background mode](openai-responses-api-features.md) uses for a server-side response, and the batching itself is in [batch processing](pydantic-ai-batch-processing.md).

## The submit-and-collect cycle

The documented shape is two functions over stored bytes: submit a set of inputs as one batch and keep `result.all_messages_json()` per run, then later validate a stored history with `ModelMessagesTypeAdapter` and run the agent on it, storing the new history again if the output is still pending[^pydantic-batch-2026] Three details make it work:

- **Start the runs together.** Submitting a request waits up to `max_wait` for others to join its batch, so runs awaited one after another each wait alone and get a batch each; a script that exits after submitting should lower `max_wait`[^pydantic-batch-2026]
- **Both phases need the capability.** Collecting with an agent that has no `BatchModelRequests` raises a `UserError` rather than sending the waiting request again as a new request at the full price[^pydantic-batch-2026]
- **Store the model name when the model is dynamic.** If the model was chosen by a capability such as `SelectModel`, resuming raises a `UserError` unless the submitting model is passed to the run as `model=`[^pydantic-batch-2026]

A run that needs several model requests — to call a tool, or to retry after an output validator raised — ends with a `PendingModelResponse` for **each** of them, so one job can take several submit-and-collect cycles[^pydantic-batch-2026]

## Usage accounting across the split

The runs of a submit-and-collect cycle do not share one usage record: each run counts the request in its own `usage.requests`, so adding `usage.requests` across the cycle counts one request once per run, while that request's tokens and cost are attributed only to the run that received the result[^pydantic-batch-2026] Anything that meters by request count — usage limits, dashboards, per-tenant billing — therefore has to decide whether it wants attempts or results; the limits themselves are in [run controls](pydantic-ai-run-controls.md). The same accounting applies to any request the provider keeps working on after it was sent, OpenAI background mode included[^pydantic-batch-2026]

## Collecting from another process

The collector does not need the API key that submitted the batch: the provider decides who may check a batch, so a rotated key of the same project or workspace works[^pydantic-batch-2026] A key from another project or workspace is refused, and is reported as the expired case below rather than as a permission error[^pydantic-batch-2026] Collection is also batched: checks of one batch within `poll_interval` of each other share one status request, and the results are downloaded once while they are cached, so collecting many stored histories costs about one check per batch rather than one per run[^pydantic-batch-2026] That cache holds the results of the last 32 ended batches up to 256 MB, which is why the advice is to collect one batch's histories together rather than interleaved with many others[^pydantic-batch-2026]

## Retention and expiry

A batch left for a later run keeps running whether or not anything collects it, so results must be collected well inside the provider's retention window — 30 days for OpenAI, 29 days from creation for Anthropic, 6 weeks by default for Google[^pydantic-batch-2026] A run resumed from a history whose batch the provider no longer has raises `SuspendedResponseExpired`, and the request is **not** resubmitted, because the provider may have run and billed it[^pydantic-batch-2026] To run it again you resume from the history with the pending response removed from its end[^pydantic-batch-2026]

## When a request is not actually left pending

Ending with a pending response is the *only* way a request is left waiting for a later run[^pydantic-batch-2026] A pending response that an `after_model_request` hook rejects, by raising or by returning another response, is abandoned; so is one whose run fails or is cancelled afterwards, one that ends with another output — for example from an `after_run` hook — and one left early while iterating with `iter()`[^pydantic-batch-2026] Cancelling a run that resumes a pending request leaves the batch running, since the same history may be resumed elsewhere[^pydantic-batch-2026] Abandoned requests follow the cancellation rules in [batch processing](pydantic-ai-batch-processing.md): the provider batch is cancelled once nothing else submitted in it still waits.

Two environments cannot use this escape at all. Inside a [dynamic workflow](pydantic-ai-dynamic-workflow.md) script, or behind a [subagent](pydantic-ai-subagents.md) delegation, `PendingModelResponse` is stripped from the sub-agent's return type and a run that ends with one fails the call instead — a workflow script can neither approve a deferral nor resume a pending request[^pydantic-batch-2026] There, the alternative to holding the process is [durable execution](pydantic-ai-durable-execution.md): the capability's submission and checks become durable steps that resume on the same batch, with per-engine limits recorded in [batch processing](pydantic-ai-batch-processing.md).

## Limits

- The capture names **no Pydantic AI version, publication date, author or licence**, so the pending-response behaviour, the `UserError` conditions and the cache figures are version-unknown and this page is `draft` under the `pydantic-ai` domain rule[^pydantic-batch-2026]
- The retention periods (30 days, 29 days, 6 weeks) are the batching page's restatement of three providers' policies; the providers' own documentation owns them and was not read here.
- Unstated: the fields a `PendingModelResponse` carries and whether it is safe to render to a user, whether the status cache is per process or per capability instance, what happens when two processes collect the same batch concurrently, and whether the 32-batch cache bound counts ended batches only (the page says it does, without saying what happens to older entries still referenced by a stored history).
- Nothing was installed, no run submitted, no history stored or resumed, no cache measured and no key rotated, so every claim is **Reported** and none **Observed** or **Reproduced**. One reading is **Synthesis**: because cost and tokens land on the collecting run while request counts land on both, a cycle's aggregate cost per request is unaffected but its per-run cost is not, which is the shape a billing or limit check has to be written against.

## Relationships

- **Depends on** [batch processing](pydantic-ai-batch-processing.md) for the capability, the polling settings, the resubmission rules and the credential constraints; this page is only the submit-now-collect-later half.
- **Shares its mechanism with** [OpenAI background mode](openai-responses-api-features.md), which ends a run the same way and whose history the same collector pattern resumes.
- **Is the non-durable alternative to** [durable execution](pydantic-ai-durable-execution.md), and the two compose: a durable batched run does not need a pending response, but may use one to outlast a step budget.
- **Is refused by** [dynamic workflows](pydantic-ai-dynamic-workflow.md) and [subagent delegation](pydantic-ai-subagents.md), where the marker is stripped from the return type and a pending child run is a steering-message failure.
- **Interacts with** [message history](pydantic-ai-message-history.md) as the transport: the batch reference travels in the stored history, which is why the collect phase validates it with `ModelMessagesTypeAdapter` and why the cycle pairs a stored history with the agent's `output_type` unchanged (**Synthesis**: a history whose tail is truncated or rewritten no longer names the batch, so the stored bytes are the contract between submit and collect).
- **Is billed and limited through** [run controls](pydantic-ai-run-controls.md), where the per-run `usage.requests` over-count described above meets `UsageLimits`.

[^pydantic-batch-2026]: Pydantic Docs, "Batch Processing" (<https://pydantic.dev/docs/ai/core-concepts/batch/>; 4,953 words as declared, 5,013 by local `wc -w` including frontmatter and markup; 487 lines; language `en`; no publication date, author, licence or Pydantic AI version), local capture `raw/core-concepts/batch/index.md`, content digest sha256:53d4b659. "Submitting now and collecting later" (raw lines 159–225) for `PendingModelResponse` in `output_type`, the run ending at submission, the pending response recording the batch, the store-and-resume cycle, the `submit`/`collect` sample, the `max_wait` note and the start-runs-together rule, the `UserError`s for a missing capability and a dynamically chosen model, the per-request pending output of a multi-request run, the `usage.requests` accounting, the collector-key and status-cache rules with their 32-batch/256 MB bounds, and the retention warning; "Errors and resubmission" (279–290) for the resubmission and failed-check counters recorded in history; "Durable execution" (226–278) for the pending-response-versus-durable-execution choice; "Cancellation and async with" (471–478) for the abandoned-versus-left-pending distinction and the four cases in which a pending response is not left for a later run; "Retention" (483–487) for the three retention periods and `SuspendedResponseExpired`; and the subagent, dynamic-workflow and OpenAI-background cross-references as linked, not followed. Evidence class: **Reported** — vendor documentation naming no version; no run submitted, no history stored or resumed and no cache measured.
