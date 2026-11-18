---
type: Concept
title: Pydantic AI output truncation
description: What a response cut off at the token limit raises under each output mode — plain truncated text, OutputTokenLimitExceeded, or IncompleteToolCall — what happens when the cut leaves valid data, and the three documented remedies.
tags: [pydantic-ai, agents, structured-output, errors]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:08:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-output
    resource: ../raw/core-concepts/output/index.md
    scope: ../raw/core-concepts/output/
    kind: documentation
    revision: sha256:c70422e8bdd3e28400b6ca8c611c3097e9f9dc1a39a9328fc36e440fa3e1193f
    title: "Output"
---

**Reported, Pydantic AI version unspecified:** when a response reaches the `max_tokens` model setting or the model's own output limit, the provider cuts it off and the response's `finish_reason` is `'length'`. What the caller sees next depends entirely on the [output mode](pydantic-ai-structured-output.md): text has no shape to check and the truncated text *is* the output, while structured and tool outputs are validated and their malformed JSON is a hard error rather than a retry.[^pydantic-docs-output]

## Text output passes through

`str` and `TextOutput` functions have nothing to validate, so a truncated answer is returned as the run's output like any other. The docs' `cut_off` sample manufactures exactly this — a `FunctionModel` returning `TextPart('The three largest cities are Tokyo, Delhi and')` with `finish_reason='length'` under `max_tokens=10` — and then reads `result.response.finish_reason` to detect it:[^pydantic-docs-output]

```python
result = agent.run_sync('Name the three largest cities.', model_settings={'max_tokens': 10})
print(result.output)
#> The three largest cities are Tokyo, Delhi and
if result.response.finish_reason == 'length':
    print('The answer was cut off.')
```

Checking the finish reason is the documented rule whenever a complete answer matters.[^pydantic-docs-output]

## Structured output is validated, so truncation usually raises

The mode decides the exception, and none of these paths asks the model to try again — it would hit the same limit:[^pydantic-docs-output]

| Mode | What the truncation produces |
| --- | --- |
| Native Output, Prompted Output | JSON that does not parse raises `OutputTokenLimitExceeded`, with a message naming the token limit, in `run()` and `run_stream()` alike |
| Tool Output | An output-tool call whose argument JSON does not parse raises `IncompleteToolCall` immediately, in `run()` and `run_stream()` alike |
| Any mode, cut off before any output | A response truncated before producing output — say while the model was thinking — raises `OutputTokenLimitExceeded` |

Truncation is only a hard error when the fragment cannot be parsed. Text that was cut off but **still parses** is validated as usual: it is the output when it satisfies the schema, and it is retried when the schema or an [output validator](pydantic-ai-structured-output.md) rejects it. The same applies to tool-call arguments that were cut off but still parse.[^pydantic-docs-output]

The documented remedies are to raise `max_tokens`, ask for a shorter answer, or let [another model take over](pydantic-ai-model-fallback.md) through the token-limit fallback path.[^pydantic-docs-output]

## Evidence and coverage

The sole artifact is the Pydantic documentation capture `index.md` (8,218 words as declared), inspected as text, with no attachments, includes, downloads or supporting files. It names no Pydantic AI version, author, publication date or licence, so the exact class hierarchy of `OutputTokenLimitExceeded` and `IncompleteToolCall`, and whether either carries the limit as an attribute, are unverified — both are only linked, not read. The `FunctionModel` sample was read but not executed, `max_tokens` behaviour was not reproduced against a provider, and no truncation was induced, so every claim is **Reported**. The page is `draft` under the `pydantic-ai` domain rule and carries `stale_after` because exception names and provider limits are release-sensitive.

## Relationships

- **Depends on** [Pydantic AI structured output](pydantic-ai-structured-output.md): the selected output mode is what decides between truncated text, `OutputTokenLimitExceeded` and `IncompleteToolCall`.
- **Applies to** [Pydantic AI streamed output](pydantic-ai-streamed-output.md): the docs state the same errors for `run()` and `run_stream()`, and a cut-off fragment is a `state` the stream consumer must handle rather than a different failure mode.
- **Fixed by** [Pydantic AI model fallback](pydantic-ai-model-fallback.md): the token-limit fallback handler is the documented way to hand a truncated request to another model.
- **Related to** [Pydantic AI model API errors](pydantic-ai-model-api-errors.md): a truncation is not a provider/API error category, so the classification and retry predicate on that page do not cover it.

[^pydantic-docs-output]: Pydantic Docs, "Output" (`https://pydantic.dev/docs/ai/core-concepts/output/`, 8,218 words as declared); local capture `raw/core-concepts/output/index.md`, content digest sha256:c70422e8. "Output cut off by the token limit" (lines 838–872) for the `max_tokens` and provider-limit rule, `finish_reason='length'`, the `cut_off`/`FunctionModel` sample and the finish-reason check, text output passing through, `OutputTokenLimitExceeded` under Native and Prompted Output in `run()` and `run_stream()`, `IncompleteToolCall` under tool output, the still-parses case being validated and retried, the no-output-yet case, and the three remedies. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no release version.
