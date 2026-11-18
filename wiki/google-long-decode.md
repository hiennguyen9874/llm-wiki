---
type: Concept
title: Google long decode in Pydantic AI
description: How a Gemini 4 output larger than one request's cap is produced — the continuation token the SDK follows, the usage and limit arithmetic of one merged response, what a late failure costs streamed and non-streamed runs, and the Temporal and payload constraints it brings.
tags: [pydantic-ai, models, google, usage, temporal]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:44:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

`gemini-4-argon`, `gemini-4-carbon` and `gemini-4-hydrogen` cap the output of each request, with the caps and defaults on Google's long-decode documentation rather than stated in the source[^pydantic-google-2026] Set `max_tokens` above that cap and the `google-genai` SDK produces a longer answer anyway: a request that reaches its cap returns a **continuation token**, and the SDK issues another request to continue from it, repeating until the response is done or `max_tokens` is spent[^pydantic-google-2026] The SDK merges those requests into one `ModelResponse`, so **to Pydantic AI a long decode is one model request** — which is where every other rule on this page comes from[^pydantic-google-2026]

```python
agent = Agent('google:gemini-4-argon', model_settings={'max_tokens': 100_000})
result = agent.run_sync('Write the complete specification.')
```

## One request to the framework, several on the wire

| What you see | What happened |
| --- | --- |
| One `ModelResponse` | The SDK merged every continuation request into it |
| `usage` summed over the requests | Each request re-counts the output produced so far as **input**, which is what Google bills |
| One request in [usage limits](pydantic-ai-run-controls.md) | Token limits are checked once, after every request is done; `max_tokens` is what bounds the decode |
| `per_request_input_tokens_limit` | Checked against the **first** request's input tokens, not the summed total |
| `timeout` | Applies to each request separately, not to the merged whole |

The cost consequence is the one to plan for: because each continuation re-sends the output so far as input, a long decode's input tokens grow with the square of the number of continuations in the worst case (**Synthesis** from the re-counting rule and the one-check-at-the-end limit accounting), and `usage_limits` will not stop it early — `max_tokens` is the only ceiling[^pydantic-google-2026] The providers create their client with the 20-minute read timeout Google recommends, which is the transport half of this; the header and client rules are in [Google models in Pydantic AI](google-models-in-pydantic-ai.md).

## A late failure loses work, but only on a non-streamed run

If a later request fails, the model request fails as a whole[^pydantic-google-2026] A run that is **not streamed** then loses the output of the earlier requests, which have already been billed; a **streamed** run keeps what it streamed, as a response with `state='interrupted'` that carries the finished requests' usage, returned by `capture_run_messages()`[^pydantic-google-2026] Streaming is therefore the cheaper way to attempt a decode whose continuation you expect to be shaky (**Synthesis**: the source states the two outcomes, not the preference).

The SDK adds its own retry on top, and it is easy to under-count. With `google-genai` **2.31.0 and later**, a streamed run re-sends a later request that fails **before streaming any output** three more times from the same continuation token, with no wait; if all four fail, the model request fails as above[^pydantic-google-2026] That covers errors the HTTP client raises — a connection that cannot be opened or that drops, a timeout, or the `HTTPStatusError` of a retrying transport that gave up — and does **not** cover an error status the SDK reads itself[^pydantic-google-2026]

Neither `retry_options` nor `max_retries` can turn that behaviour off, and they apply on top of it: they also retry a connection that cannot be opened, or a timeout before the response arrives, on each of those four requests, so with `max_retries=2` such an error goes on the wire **12 times**[^pydantic-google-2026] The retry configuration itself is in [Google models in Pydantic AI](google-models-in-pydantic-ai.md) and the error taxonomy in [model API errors](pydantic-ai-model-api-errors.md).

A dropped stream is resumed from its last continuation token, unless output was streamed after that token — in which case the model request fails instead, because the resumed request would repeat that output[^pydantic-google-2026]

## Temporal constraints

Under [durable execution](pydantic-ai-temporal.md), the whole long decode runs in **one model-request activity**, so its `start_to_close_timeout` has to cover every request, not one[^pydantic-google-2026] A retried activity starts the response over, and because the merged response is the activity's single result, a very long output can exceed Temporal's payload limit[^pydantic-google-2026] That makes long decode a poor fit for a large specification on Temporal unless the output is chunked elsewhere.

## Without `max_tokens`, and where the model is served

Left unset, Google's own default output limit applies and a response that reaches it ends with `finish_reason='length'` rather than continuing — so long decode is opt-in through a large `max_tokens`[^pydantic-google-2026] The rest of the truncation surface is in [output truncation](pydantic-ai-output-truncation.md).

On Google Cloud, `gemini-4-argon` is served only on the `global` location and the `us` and `eu` multi-regions — not in single regions such as the default `us-central1` — so the provider's `location` has to be one of those[^pydantic-google-2026]

## Limits

- The source names **no Pydantic AI version** and no publication date; the one version it does name is `google-genai` 2.31.0, for the three extra retries, so the page is `draft` under the `pydantic-ai` domain rule[^pydantic-google-2026]
- The caps themselves, and the output defaults, are on Google's long-decode page, which was read as a link and not followed, so no token ceiling or continuation count is stated here[^pydantic-google-2026]
- Every claim is **Reported**: no continuation was followed, no stream dropped, no `interrupted` response captured, no activity retried and no payload limit hit.
- The 12-wire-attempt arithmetic is the source's own multiplication of its four SDK attempts by `max_retries=2`; nothing here reconciles it with [model API errors](pydantic-ai-model-api-errors.md)' transport-retry accounting.

## Relationships

- **Depends on** the client and timeout rules in [Google models in Pydantic AI](google-models-in-pydantic-ai.md), whose 20-minute default exists for this path.
- **Changes the accounting described in** [run controls](pydantic-ai-run-controls.md) and [model API errors](pydantic-ai-model-api-errors.md): many wire requests, one request in `RunUsage`, and a summed token bill.
- **Constrains** durable runs in [Pydantic AI Temporal](pydantic-ai-temporal.md), where one activity must cover every continuation and the merged result must fit a payload.
- **Alternative to** [output truncation](pydantic-ai-output-truncation.md): `finish_reason='length'` is what happens without a large `max_tokens`.
- **Sibling of** the Google batch route in [Google models in Pydantic AI](google-models-in-pydantic-ai.md): both trade request count for throughput or cost, but batch is a separate job while long decode is one call.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Long decode" (raw lines 501–525) for the three capped `gemini-4-*` models, the continuation token, the SDK's repeated continuation until `max_tokens` is spent, the merged single `ModelResponse`, the summed usage with each request re-counting prior output as input, the one-request usage-limit accounting and the `per_request_input_tokens_limit` first-request rule, the per-request timeout, the non-streamed loss against the streamed `state='interrupted'` response from `capture_run_messages()`, the `google-genai` 2.31.0 three-extra-attempts rule and the error kinds it covers, the `max_retries=2` twelve-wire-attempt multiplication, the resume-from-last-token rule and the output-streamed-after-token failure, the Temporal one-activity `start_to_close_timeout` and payload limit, the `finish_reason='length'` default without `max_tokens`, and the `global`/`us`/`eu` locations for `gemini-4-argon` on Google Cloud. Evidence class: **Reported** — vendor documentation; nothing was decoded, streamed, dropped, retried or made durable.
