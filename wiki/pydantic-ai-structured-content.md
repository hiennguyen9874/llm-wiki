---
type: Concept
title: Pydantic AI structured content
description: How StructuredContent puts a typed value into a Pydantic AI prompt — compact JSON or XML rendering under a reserved tag, text frozen at creation for cache and replay stability, what survives a reload, and the decision-model exception.
tags: [pydantic-ai, agents, input, prompt-caching]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:12:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-input-docs
    resource: ../raw/core-concepts/input/index.md
    scope: ../raw/core-concepts/input/
    kind: documentation
    revision: sha256:8d3034fd3ee8f26e5c8a864f5afe7a7fecaea79d4470362b67d35fd0aa0e2196
    title: "Multimodal Input"
---

**Reported, Pydantic AI version unspecified:** `StructuredContent` carries a typed value inside a user prompt — the UI state a user is looking at, or the material a [decision model](jev-decision-model.md) should judge — while keeping the value structured in the message history, so a history processor or an evaluator can read it back after the model has seen only text[^pydantic-input-docs] The design is deliberately two-faced: the model receives a rendering, the history keeps the value. That split is what makes it useful for evaluation and what makes its rendering rules — tag choice, escaping, when the text is frozen — the load-bearing details.

## The prompt contract

`agent.run_sync([StructuredContent(ui_state, tag='ui_state'), 'Why did the total jump?'])` sends the model:

```text
<ui_state>{"url":"/products/42","cart_total":949.0}</ui_state>
```

followed by the question[^pydantic-input-docs] The default rendering is compact JSON, wrapped in `tag` when one is given, with `<`, `>` and `&` escaped so that a value from an untrusted client, rendered on your server, cannot close the tag[^pydantic-input-docs] Two alternative renderings are accepted: `format='xml'` renders through `format_as_xml`, and a callable taking the value and returning text renders it however you like.

Three further rules constrain the tag and the surrounding text[^pydantic-input-docs]:

- `tag` is lowercase with `_` between words.
- It cannot be one of the tags the framework frames its own text in, such as `system` or `tool_result`, so the value cannot read as the framework speaking.
- A `description` is written on the line before the value.

## The text is frozen at creation

The text is rendered once, when the item is created, and stored in `content` beside `value`[^pydantic-input-docs] A message history that is stored and loaded again is therefore sent exactly as before, which keeps the [prompt-cache](pydantic-ai-prompt-caching.md) prefix intact even when the text came from a function that was not stored. This is the property that makes the part usable in cached, persisted conversations: replay does not re-render, so the prefix is byte-stable by construction rather than by luck.

The cost is that the text is *not* re-rendered when the value changes[^pydantic-input-docs] To change a value you either create a new item, or call `dataclasses.replace(item, value=..., content='')` and pass `format` again if the item was created with one. Mutating `value` in place leaves the model seeing the old text — a silent divergence between what the history holds and what the model was told.

After loading a stored history, `value` is the JSON-compatible form of the original, such as a `dict` in place of a Pydantic model[^pydantic-input-docs] Code that reads `value` back therefore has to accept the plain-data shape, not the class it was constructed from.

## Reusing a rendering: subclass and `render`

To render a kind of value the same way everywhere, subclass `StructuredContent` and override `render`[^pydantic-input-docs]:

```python
from pydantic import BaseModel

from pydantic_ai import StructuredContent, format_as_xml

class UIState(BaseModel):
    url: str
    cart_total: float

class UIStateContent(StructuredContent):
    value: UIState

    def render(self) -> str:
        return format_as_xml(self.value, root_tag='ui_state')

print(UIStateContent(UIState(url='/products/42', cart_total=949.0)).content)
"""
<ui_state>
  <url>/products/42</url>
  <cart_total>949.0</cart_total>
</ui_state>
"""
```

The subclass is the documented way to pull a project's rendering policy out of every call site; the example prints `content` directly, showing that the rendered text is an ordinary attribute of the part.

## Text consumers and the decision-model exception

`StructuredContent` *is* a `TextContent`, so code that reads the text of a prompt handles it like any other text[^pydantic-input-docs] A [decision model](jev-decision-model.md) is the documented exception: when the prompt is a single `StructuredContent`, it is sent the value itself rather than the rendering.

That exception sets the rule for rewriting code[^pydantic-input-docs]: a redaction or rewrite step should replace the item with a plain `TextContent` holding the new text, as the Harness's guardrails and compaction do, rather than editing `content` in place and leaving a value that no longer matches its text. The same page records the UI adapters — Vercel AI and AG-UI dump the item as ordinary text in the user message, which a frontend shows like any other user text, and carry its value in the metadata of that text part (Vercel AI) or message (AG-UI, from `ag-ui-protocol` 0.1.11), so it loads back whole. An item enqueued mid-run with `ctx.enqueue` is accepted like any other user content. As with `TextContent.metadata`, its `metadata` does not make the round-trip.

## Limits

- Single vendor reference page: 2,163 words as declared, 2,282 by local `wc -w` including frontmatter and markup, no publication date, no author, and **no Pydantic AI version**, so every API name is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-input-docs]
- Nothing was executed: no package installed, no agent run, no XML rendering printed, no history stored or reloaded, no cache hit measured. Every claim is **Reported**[^pydantic-input-docs]
- Unstated by the source: the validation timing for `tag` (construction versus render), the signature a custom `format` callable receives, whether `render` may be async, any size ceiling on the rendered text, and how the UI adapters serialize a value that is not JSON-compatible.
- The `format_as_xml` API page was read as a link and not followed, so the exact XML shape for nested or non-scalar values is unverified; the example's own flat `UIState` is the only printed output.
- The AG-UI round-trip is tied to `ag-ui-protocol` **0.1.11** in the source; whether earlier or later versions carry the value the same way is not stated.

## Relationships

- **Is a** [`TextContent`](pydantic-ai-multimodal-input.md) and therefore one of the input parts a prompt can mix with file parts.
- **Feeds** [decision models](jev-decision-model.md), which receive the value itself when the prompt is a single `StructuredContent`.
- **Protects** the [prompt-cache](pydantic-ai-prompt-caching.md) prefix by freezing its rendering at creation time.
- **Travels with** persisted message history through [Conversation state](pydantic-ai-conversation-state.md), where the stored `content` is what replay sends.
- **Is rewritten by** the Harness's guardrails and compaction, which replace the item with plain `TextContent` rather than editing it — see [Pydantic AI Harness](pydantic-ai-harness.md).

[^pydantic-input-docs]: Pydantic Docs, "Multimodal Input", <https://pydantic.dev/docs/ai/core-concepts/input/>; local capture `raw/core-concepts/input/index.md`, content digest sha256:8d3034fd, 2,163 words as declared (2,282 by `wc -w` including frontmatter and markup), no publication date, author or framework version. Lines 133–135 for the purpose, the history-versus-model split and the `structured_content_input.py` example; 137–141 for the compact-JSON rendering, the `tag` wrapper, the `<`/`>`/`&` escaping, `format='xml'` and the callable form; 143 for the `description` line and the lowercase/underscore and reserved-tag rules; 145–147 for rendering once at creation, the stored `content`, the reload/cache argument, the no-re-render rule, `dataclasses.replace(..., content='')` and the loaded `value` shape; 149–165 for the `UIStateContent` subclass overriding `render`; 167 for the `TextContent` relationship, the decision-model exception, the rewrite-to-`TextContent` rule and the guardrails/compaction reference; 169 for the Vercel AI and AG-UI adapters, `ag-ui-protocol` 0.1.11, `ctx.enqueue` and the non-round-tripping `metadata`. Evidence class: **Reported** — vendor documentation with no execution behind it.
