---
type: Concept
title: Anthropic request constraints in Pydantic AI
description: What a Claude request in Pydantic AI may not carry — forced tool choice under thinking, grammar limits on strict schemas and the fallbacks Pydantic AI takes before sending, thinking blocks bound to their conversation prefix, carried-over thinking replayed as text, and the repeated-prompt refusal.
tags: [pydantic-ai, anthropic, thinking, structured-output, errors]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:26:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

Claude constrains a request in ways that surface as either a `UserError` before anything is sent or a 400 after it, and the two failure shapes differ in what a fallback can do about them: a schema over Anthropic's grammar limits can be avoided locally, while a thinking block bound to the wrong conversation prefix has to be dropped or the run fails.[^pydantic-anthropic-2026] This page collects the four constraints that change how a request is *assembled* — forced tool choice, strict-schema complexity, thinking-block binding and the extraction refusal — plus the one artefact that explains a `user` turn you never wrote. Caching and prefix stability are in [Anthropic prompt caching](anthropic-prompt-caching.md); the route itself is [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md).

## Forced tool choice

Most Anthropic models let a request force a tool call with `tool_choice='required'` or a list of tool names — except while extended thinking is enabled[^pydantic-anthropic-2026] Adaptive thinking accepts forcing, but Claude then answers a forced tool choice *without thinking*[^pydantic-anthropic-2026] Anthropic documents Claude Fable 5.1 and 5.2, Mythos 5.1 and 5.2, Opus 5.5 and Sonnet 5.5 as rejecting a forced tool choice unconditionally, even without thinking, and Pydantic AI marks those with `supports_forced_tool_choice=False`[^pydantic-anthropic-2026]

What happens next depends on who asked for the force:

- An **explicit** `tool_choice='required'` or name list, on a model that does not support forcing or while extended thinking is enabled, raises a `UserError`; `tool_choice='auto'` is the documented alternative[^pydantic-anthropic-2026]
- A `required` choice **Pydantic AI resolved on your behalf** — from an output tool, for instance — falls back softly to `'auto'`[^pydantic-anthropic-2026] If it named a single tool, the available tool list is filtered to that tool while `tool_choice` stays `'auto'`, which invalidates Anthropic's prompt cache because the cached prefix includes the tool array[^pydantic-anthropic-2026] The model may then answer with text instead of calling the tool, and when an output tool is required Pydantic AI retries with a prompt to call one[^pydantic-anthropic-2026]

While adaptive thinking is on, an explicit forcing choice is still sent and comes back without thinking, whereas a choice Pydantic AI resolved falls back to `'auto'` so the model keeps thinking[^pydantic-anthropic-2026]

### Which output mode that forces

Tool Output forces a call to the output tool on every request that cannot end with text, so a bare structured `output_type` would need output-tool forcing — and instead, where the model supports it, Pydantic AI uses Native Output whenever the request thinks[^pydantic-anthropic-2026] "Thinks" here covers a thinking setting *and* a model that thinks by default, such as Claude Opus 5 and later, Sonnet 5, Haiku 5.5 and the Fable and Mythos models[^pydantic-anthropic-2026] On a model without JSON-schema support, extended thinking falls back to Prompted Output, while adaptive thinking keeps Tool Output with the output tool offered under `tool_choice='auto'`; turning thinking off with `thinking=False`, where the model allows it, keeps Tool Output, and an explicit `ToolOutput(...)` keeps it regardless[^pydantic-anthropic-2026]

The output mode is chosen on the run's **first** request and kept for the rest of the run — except behind a `FallbackModel`, where each model chooses on every request — so a thinking setting that changes between steps, through a `model_settings` callable or a capability, cannot add or remove the output tool mid-run and invalidate the prompt cache[^pydantic-anthropic-2026] A run that starts with Tool Output keeps it once thinking turns on, with the output tool offered under `tool_choice='auto'`[^pydantic-anthropic-2026]

## Strict schemas and grammar limits

Anthropic compiles every strict schema in a request into a grammar that constrains generation, and enforces complexity limits on it — on the number of strict tools, optional parameters and union-typed parameters, counted across **all** strict schemas in the request combined[^pydantic-anthropic-2026] Which schemas are strict is narrow:

- The output schema of Native Output is always strict, and `NativeOutput(..., strict=False)` raises a `UserError` — this includes a bare structured `output_type` on a request that thinks, since that uses Native Output[^pydantic-anthropic-2026]
- Function and output tools are strict only when `strict=True` is set, so the default Tool Output is unaffected[^pydantic-anthropic-2026]
- Prompted Output sends no schema to compile, so it is never affected[^pydantic-anthropic-2026]

In a Pydantic model, a field with a default is optional and a field typed `X | None` or another union has a union type, so both count; Anthropic also rejects a recursive schema in strict mode and has other documented JSON-schema limitations[^pydantic-anthropic-2026]

Pydantic AI checks the explicit limits and recursion **before** sending, and the two outcomes differ:

| What you asked for | Result when over a limit |
| --- | --- |
| A bare structured `output_type` that would use Native Output | Falls back to Tool Output, whose tool is not strict and so does not count; on a thinking request it is offered under `tool_choice='auto'`, so the model may answer with text and get a retry prompt |
| An explicit `NativeOutput(...)` or `strict=True` on a tool or `ToolOutput` | Raises `ModelRequestRejectedError` naming the limit, without waiting for a 400 |

The resolved output mode is recorded in the `model_request_parameters` attribute of the request's span, which is how a silent downgrade becomes visible in a trace[^pydantic-anthropic-2026] `ModelRequestRejectedError` is the same error category as the 400 Anthropic would have sent, so a `FallbackModel` still falls back to its next model and `except ModelAPIError` still catches it — but it is **not** a `ModelHTTPError`, because no request was sent[^pydantic-anthropic-2026] Both error surfaces are catalogued in [model API errors](pydantic-ai-model-api-errors.md).

The pre-flight check applies to the Anthropic API and to Claude on Amazon Bedrock, through `BedrockConverseModel` or an `AnthropicModel` with a Bedrock client[^pydantic-anthropic-2026] On Google Cloud and Microsoft Foundry the limits have not been verified, so Pydantic AI sends such a request for Anthropic to judge unless you set `anthropic_enforces_strict_schema_limits=True` in the model's profile[^pydantic-anthropic-2026]

Being within the explicit limits is not sufficient. A schema can still exceed Anthropic's internal limit on grammar size — deeply nested models, many optional or union-typed fields — and the request then fails with a 400 saying the compiled grammar is too large or the schema too complex, which can arrive immediately or only after Anthropic's **180-second** compilation timeout[^pydantic-anthropic-2026] Pydantic AI raises that 400 as a `ModelHTTPError` *and* a `ModelRequestRejectedError`, with a `hint` pointing at the remedy, and does not retry it[^pydantic-anthropic-2026] There is a trap around it: a `timeout` shorter than the compilation makes the request time out first, and the Anthropic SDK retries a timed-out request twice by default, so a run can wait several times the timeout before failing[^pydantic-anthropic-2026]

The documented remedies are to make fields required, flatten nested models, set `strict=True` only on the tools that need it, and wrap a large output type in `ToolOutput` without `strict=True` or in `PromptedOutput` — neither is compiled, so the model is not constrained and Pydantic AI validates the output and asks it to try again on failure[^pydantic-anthropic-2026]

## Thinking blocks bound to their conversation prefix

Several Claude models tie each thinking block to the conversation prefix that produced it: Claude Fable 5.1 and 5.2, Mythos 5.2, Opus 5.5, Sonnet 5.5 and Haiku 5.5[^pydantic-anthropic-2026] Replaying such history after the `system` field, the `tools` or an earlier `messages` entry changed is rejected with a documented 400 — *The block is bound to a different conversation* — and two ordinary Pydantic AI features change that prefix[^pydantic-anthropic-2026]

- a dynamic instructions function whose text differs between runs, unless it uses `on_change='append'`, and
- a filtered toolset that advertises a new tool mid-conversation, unless the tool uses deferred loading[^pydantic-anthropic-2026]

This is the same instability that costs a provider's prompt cache, and the source's argument is that the thinking block turns it into a 400 you can see while the cache turns it into a bill you cannot: every request after the change re-sends the whole conversation at uncached rates[^pydantic-anthropic-2026] Where the prefix can be held stable, that is worth more than handling the rejection[^pydantic-anthropic-2026]

**Who enforces it.** Claude Fable 5.2 and Mythos 5.2 enforce the check on every account[^pydantic-anthropic-2026] On the other models Anthropic enforces it for accounts created on or after 31 August 2026; for an older account it records the mismatch but returns the error only if the request sets `thinking.block_binding.prefix_mismatch_behavior`[^pydantic-anthropic-2026] Pydantic AI sets nothing by default, so an older account keeps replaying its reasoning untouched on those models[^pydantic-anthropic-2026]

**What Pydantic AI does when the check fires.** The rejected request is retried once with `prefix_mismatch_behavior='drop_block'`: the stale block is dropped, the run continues, and an `AnthropicStaleThinkingBlockWarning` explains what happened[^pydantic-anthropic-2026] The trade is explicit — the model no longer sees that turn's reasoning, one turn's thinking against a failed run[^pydantic-anthropic-2026] Only models marked `anthropic_binds_thinking_blocks=True` retry, and a request whose thinking type is not `adaptive` — `anthropic_thinking={'type': 'between_tools'}`, for instance — is not retried at all, because Anthropic accepts `block_binding` only alongside adaptive thinking; that conversation's prefix has to be kept stable instead[^pydantic-anthropic-2026]

**The drop is scoped to one request, then remembered.** Anthropic applies the drop to a single request, and its response records the transformation, so Pydantic AI uses that response history to keep sending `drop_block` for the rest of the affected conversation — avoiding another rejected request on every later turn without storing mutable state on the model or changing an unrelated conversation[^pydantic-anthropic-2026] `count_tokens()` behaves the same way: it retries the first matching rejection once, and later counts carrying the recovery history send the drop immediately[^pydantic-anthropic-2026] A recovery seen only while counting applies only to later counts, because counting omits MCP servers and, on Bedrock, Vertex AI and Foundry, server-side tools — so it can have a different prefix from inference[^pydantic-anthropic-2026] An explicit `block_binding` still wins for both counting and inference[^pydantic-anthropic-2026]

**Where it works, and how it shows up.** The automatic behaviour is available through the direct Anthropic API, the Pydantic AI Gateway and other `AsyncAnthropic`-compatible proxies, Claude Platform on AWS, both Bedrock clients and Vertex AI — but not Microsoft Foundry, where the beta is not currently documented; explicit settings remain pass-through on every transport[^pydantic-anthropic-2026] Under instrumentation the model request span carries an `anthropic.input_transformations` event, so a drop is visible in the trace as it happens and an unrelated ambient application span is never modified, and on the response it is always recorded in `provider_details`[^pydantic-anthropic-2026]

**Choosing the behaviour.** Asking for `{'type': 'adaptive', 'block_binding': {'prefix_mismatch_behavior': 'drop_block'}}` up front skips both the rejected request and the warning, and Pydantic AI sends the explicit field with the beta it requires and never retries[^pydantic-anthropic-2026] `'error'` in the same place fails loudly instead of losing the reasoning, and `warnings.simplefilter('ignore', AnthropicStaleThinkingBlockWarning)` keeps the retry without the warning[^pydantic-anthropic-2026] There is no third behaviour — `prefix_mismatch_behavior` is either `'error'` or `'drop_block'` — and passing `None` asks for Anthropic's account default explicitly, keeping the block only where the check is not enforced[^pydantic-anthropic-2026]

Models that do not bind thinking blocks are unaffected by default: with no explicit `block_binding` their requests carry neither the field nor the beta, and a 400 from them is never retried[^pydantic-anthropic-2026] Setting `block_binding` yourself puts both on the wire for *any* model — the beta follows the field, not the profile flag — and such a request is never retried either[^pydantic-anthropic-2026] Claude Mythos 5.1 is documented as not running the check, so it is marked neither way[^pydantic-anthropic-2026]

## Carried-over thinking

A `ThinkingPart` from history that cannot ride Anthropic's native reasoning channel — most often because its signature did not survive a storage round trip — is sent as text in a `user` message of its own, ahead of the assistant turn it came from, wrapped in an `<assistant_thinking>` tag[^pydantic-anthropic-2026] That is why a request can carry a `user` turn you never wrote; the reasoning why the assistant turn is the wrong place for it, and the opt-out, belong to the thinking capability rather than to this page[^pydantic-anthropic-2026]

## The repeated-prompt refusal

Claude's `reasoning_extraction` classifier can refuse a conversation that repeats the same user prompt while the model's earlier reasoning is in context, and a refusal is more likely right after an instruction changes — whether the instructions were rewritten or appended[^pydantic-anthropic-2026] Conversations with varied prompts and tool loops were unaffected in the vendor's testing[^pydantic-anthropic-2026] The refusal propagates as a `ContentFilterError`, and two remedies exist: add `ModelFallback`, which falls back to another model on such a refusal by default, or strip thinking from history with `ProcessHistory`[^pydantic-anthropic-2026]

## Limits

- The page names **no Pydantic AI version** and no date, so every flag, beta id and error name here is version-unknown; the page is `draft` under the `pydantic-ai` domain rule[^pydantic-anthropic-2026]
- Evidence class is **Reported** throughout: no request was sent, no 400 received, no thinking block dropped, no schema compiled, and the 180-second compilation ceiling is Anthropic's figure rather than a measurement[^pydantic-anthropic-2026]
- The per-model force/thinking/binding matrices are Anthropic's snapshot; the linked capability lists were read as links, not followed[^pydantic-anthropic-2026]
- The internal grammar-size limit is unnamed — the page says a schema within the explicit limits can still fail — so the remedies are guidance, not a calculation[^pydantic-anthropic-2026]
- Anthropic's account-creation cut-off for enforcing block binding (31 August 2026) is a policy date that will not move with this wiki's `stale_after`[^pydantic-anthropic-2026]

## Relationships

- **Constrains requests built by** [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), and explains the `anthropic_thinking` and profile fields that page's settings list only names.
- **Shares the strict-schema surface with** [Pydantic AI structured output](pydantic-ai-structured-output.md), which owns output-mode selection and where Native Output falls back to Tool Output.
- **Invalidates the prefix** that [Anthropic prompt caching](anthropic-prompt-caching.md) depends on, which is why binding failures and cache misses have the same two causes.
- **Raises** the errors in [model API errors](pydantic-ai-model-api-errors.md) — a pre-send `ModelRequestRejectedError` or a post-send `ModelHTTPError` — and the `ContentFilterError` that [model fallback](pydantic-ai-model-fallback.md) handles by default.
- **Visible in** [observability](pydantic-ai-observability.md) as the `anthropic.input_transformations` span event and the `model_request_parameters` span attribute.
- **Interacts with** [Anthropic context management](anthropic-context-management.md), since compaction drops a trailing response's unresolved tool calls and never returns images or documents.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Forced tool choice" (raw lines 670–684) for the extended-thinking exception, adaptive thinking without thinking, the `supports_forced_tool_choice=False` model list, the explicit-`UserError` versus resolved-`'auto'` split, the tool-list filter's cache cost, the retry prompt, and the Native/Tool/Prompted Output selection with the first-request mode lock; §"Schema complexity limits" (685–706) for the compiled-grammar limits, the always-strict Native Output schema, the `strict=True` tool scope, Prompted Output's exemption, the across-request counting, the default-as-optional and union rules, the recursion rejection, the bare-`output_type` fallback, the pre-send `ModelRequestRejectedError` and its category, the `model_request_parameters` span attribute, the Bedrock and Google-Cloud/Foundry scopes with `anthropic_enforces_strict_schema_limits`, the 180-second compilation ceiling and its hint/retry rules, and the four remedies; §"Thinking block binding" (707–774) for the binding model list, the documented 400, the two prefix-changing features, the Fable 5.2/Mythos 5.2 enforcement against the 31 August 2026 account cut-off, the once-per-request `drop_block` retry and warning, the adaptive-only retry rule, the response-recorded recovery, the counting behaviour, the transport coverage, the `anthropic.input_transformations` event and `provider_details` record, the explicit `block_binding`/`'error'`/`None` options and the unaffected-model rules; §"Carried-over thinking" (567–570) for the `<assistant_thinking>` user message; §"Refusals on repeated prompts" (610–613) for the `reasoning_extraction` classifier, `ContentFilterError` and the two remedies. Evidence class: **Reported** — vendor documentation; nothing was sent, compiled, dropped or refused.
