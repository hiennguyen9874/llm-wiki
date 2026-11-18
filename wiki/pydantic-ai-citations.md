---
type: Concept
title: Pydantic AI citations
description: How provider citations reach a Pydantic AI answer — the Citations capability that asks for them, the Citation/anchor/source shape on TextPart.citations, why structured output and forced tool calls lose them, per-provider support, and what survives a round trip through history.
tags: [pydantic-ai, agents, citations]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-citations-docs
    resource: ../raw/core-concepts/citations/index.md
    scope: ../raw/core-concepts/citations/
    kind: documentation
    revision: sha256:6cb9167e1a6af894f0bf7d4a277e7fb70528a89365f72507ce12cf481d3d1b84
    title: "Citations"
---

A citation says which source backs up part of a model's answer: a web page it searched or fetched, a document you sent, or a file in a provider's file store. Pydantic AI normalises them onto `TextPart.citations` — one envelope shape for every provider — and never rewrites the model's text[^pydantic-citations-docs] Asking for them is a separate act: most models cite search-tool results unasked, while others cite only the documents you send, or on xAI any source at all, only when the `Citations` [capability](pydantic-ai-capability-primitive.md) is attached[^pydantic-citations-docs] The three things a build has to plan around are that citations ride on **text**, that the anchor inside a citation is provider-shaped rather than framework-shaped, and that only some citations survive being sent back to the provider.

## Turning citations on

Most models cite the results of search tools — [web search](pydantic-ai-native-or-local-capabilities.md), web fetch, file search — without being asked. Some providers instead require a request: they cite documents you send, or on xAI any source, only on request, and Anthropic behaves that way for web fetch and, on the Anthropic API, for web search on models using the `20260209` or `20260318` web tools[^pydantic-citations-docs] The lever is the `Citations` capability:

```python
from pydantic_ai import Agent, BinaryContent, TextPart
from pydantic_ai.capabilities import Citations

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[Citations()])
result = agent.run_sync(
    [
        'How long do customers have to return an item?',
        BinaryContent(data=b'Items may be returned within 30 days.', media_type='text/plain'),
    ]
)
for part in result.response.parts:
    if isinstance(part, TextPart):
        for citation in part.citations or []:
            print(citation.sources[0].excerpts)
            #> ['Items may be returned within 30 days.']
```

It is a request, not a guarantee: the model can still answer without citations[^pydantic-citations-docs] Under the `pydantic-ai` domain rule this page is vendor material for a capability against provider APIs that are not pinned to a release, so the availability of the `pydantic_ai.capabilities.Citations` import and of `TextPart.citations` is version-unknown here.

## Reading a citation

A `Citation` has two fields, and they answer different questions[^pydantic-citations-docs]:

| Field | What it holds | What it does not tell you |
| --- | --- | --- |
| `sources` | Where the information came from — `WebCitationSource` carries the page's `url`; `DocumentCitationSource` covers any other source and its `document_id` is the **provider's ID, not a file path** | A document you sent in the prompt may have no ID or title at all |
| each source's `excerpts` | The passages the provider quoted as evidence | How well the text is supported — several sources on one citation are the ones the provider grouped, and they may copy each other, so their number says nothing |
| `anchor` | Which part of the text the citation is about, as character positions: `part.content[anchor.start:anchor.end]` | See the three cases below |

The anchor is the part that is *not* uniform. A `ContentCitationAnchor` covers the text the sources support — and some providers, Anthropic among them, cite whole text parts, so the anchor covers the whole part; a `MarkerCitationAnchor` covers a marker the model itself wrote, such as `[1]` or a link; and `None` means the provider never said which text is cited[^pydantic-citations-docs] That last case is common enough to plan for: OpenAI file citations give only a position, which is kept in the part's `provider_details['citations']`[^pydantic-citations-docs]

The same answer looks like this from three providers[^pydantic-citations-docs]:

```python
TextPart(
    'Pydantic validates data.',
    citations=[Citation(
        sources=[WebCitationSource('https://a.example'), WebCitationSource('https://b.example')],
        anchor=ContentCitationAnchor(start=0, end=24),
    )],
)   # Google selects the supported text, and here lists both sources for it

TextPart(
    'Pydantic validates data. ([example.com](https://example.com))',
    citations=[Citation(
        sources=[WebCitationSource('https://example.com')],
        anchor=MarkerCitationAnchor(start=25, end=61),
    )],
)   # OpenAI selects the link the model wrote

TextPart(
    'Pydantic validates data.',
    citations=[Citation(sources=[WebCitationSource('https://example.com')])],
)   # some providers give no position in the text
```

**Synthesis:** the envelope is uniform but the anchor's specificity is not, so a renderer needs three branches — supported spans, model-written markers, and "somewhere in this part" — and only the first can be highlighted from the citation alone. The source's own rendering example does exactly that: it branches on `ContentCitationAnchor`, then `MarkerCitationAnchor`, then treats everything else as unlocated[^pydantic-citations-docs] Note that the marker branch usually prints a Markdown link the model already wrote into the text, which is why the sample's output is a link followed by a title rather than a bare number.

## Text output, structured output and tools

Citations attach to text, so they come back only when the agent's output **is** text[^pydantic-citations-docs] With [structured output](pydantic-ai-structured-output.md) — including an output type that merely combines `str` with a structured type, such as `[str, Answer]` — the answer arrives as tool-call arguments, which cannot carry citations. The source's rule is blunt: if you need citations, use text output[^pydantic-citations-docs]

That single fact produces three provider-specific failure modes on Anthropic, and on Bedrock with Anthropic models, because there the model writes citation markup into anything that is *not* text — for example `summary='<cite index="1-1">Items may be returned within 30 days.</cite>'`[^pydantic-citations-docs]:

| Situation, with `Citations()` attached | What happens |
| --- | --- |
| Structured output | The model is not asked for citations, so fields stay clean and you get no document citations; Anthropic rejects citations with `NativeOutput` |
| A tool call forced with `tool_choice`, in a request carrying a document or Web Fetch | `UserError` raised **before** the request is sent, because the markup reaches the tool's arguments every time; a run that forces a tool on a later step fails at that step |
| Tools the model chooses to call | Citations stay on, but smaller models often write the markup into the tool's arguments — about half the time in the vendor's tests when the arguments summarise a document, so check arguments that end up in front of people, such as an email body, or leave `Citations()` off for those agents |

On xAI the conflict resolves the other way: with citations on, the model answers in text instead of calling the output tool, so structured output gets no citations from `Citations()` either, and tools work as usual[^pydantic-citations-docs]

Two Anthropic paths keep citations even in structured output, because they do not depend on the capability[^pydantic-citations-docs] Web search results are cited whenever the model calls the tool directly, so the markup can appear in structured output with or without `Citations()`; web fetch behaves the same once `provider_settings={'anthropic': {'enable_citations': True}}` is set on the tool, which also makes the model call it directly on the Anthropic API on models with the `20260209` or `20260318` web tools. Results the model reads inside code execution come back uncited, and with structured output `Citations()` does not change which tools the model calls from code execution — the caller switch compiled in [Anthropic server-side tools](anthropic-server-side-tools.md).

On other providers `Citations()` has no effect on structured output, but `NativeOutput` and `PromptedOutput` still produce **JSON text**, so web search citations can come back on that text with positions in the JSON rather than in your fields[^pydantic-citations-docs] Those positions are not usable as field-level provenance.

## Streaming, adapters and trusting the excerpts

When streaming, citations can arrive after the text they support: at the end of each text part on Anthropic, Bedrock and OpenAI Responses, and only at the end of the response on Google and OpenAI Chat[^pydantic-citations-docs] The rule is therefore to read citations from the final response rather than from a stream of parts; see [streamed output](pydantic-ai-streamed-output.md). On xAI they land on the last text part at end of response, so a streamed answer followed by a tool call gets none at all[^pydantic-citations-docs]

The [AG-UI adapter](https://pydantic.dev/docs/ai/integrations/ui/ag-ui/) does not send citations to the frontend, whereas the Vercel AI adapter keeps them when the frontend holds the message history[^pydantic-citations-docs] So a UI whose history lives client-side is also a UI deciding whether it gets citations at all, which is the same client-holds-state trade-off recorded in [client-supplied history](pydantic-ai-client-supplied-history.md).

Two trust rules follow from where the data comes from[^pydantic-citations-docs] Citation URLs, titles and excerpts come from the sources themselves, and excerpts can include text from your own documents, so check them before logging them or showing them to users. And anything else the provider attached about a citation — Google's confidence scores, for instance — is kept verbatim in the part's `provider_details['citations']`, in the provider's shape, which can change.

## What survives a round trip through history

Saved [message history](pydantic-ai-message-history.md) keeps every citation, and citations sent back to the same provider travel with the text, so the model knows where its earlier statements came from[^pydantic-citations-docs] Only two combinations carry citations back natively:

| Provider | Citations sent back |
| --- | --- |
| Anthropic | Web search citations, except on clients without web search, such as Bedrock |
| OpenAI Responses | Web and file citations, when message IDs are sent — the default for reasoning models; see `openai_send_reasoning_ids` |

Everything else stays on the saved messages but its **text** goes back as plain text: document and fetched-page citations, citations from OpenAI Chat, any history sent to a different provider, and any citation whose text was changed or joined with other text[^pydantic-citations-docs] The asymmetry matters for any agent that crosses providers mid-conversation: the citation objects remain in your stored history for rendering, but the next model reads them as ordinary prose.

Editing a saved answer is the case where stored citations go stale. Clear that part's `citations` and its `provider_details['citations']` alongside the text edit; Pydantic AI leaves out citations whose text clearly changed, but an edit that keeps the same length can go unnoticed[^pydantic-citations-docs] History that is sent back unchanged goes out identically every turn, which is the property [prompt caching](pydantic-ai-prompt-caching.md) depends on[^pydantic-citations-docs]

## Provider support

| Provider | What is citable | How to turn it on | Notes |
| --- | --- | --- | --- |
| [Anthropic](https://platform.claude.com/docs/en/build-with-claude/citations) | Web search, web fetch and documents | Web search is always on for direct calls, which `Citations()` makes the model use on the Anthropic API on models with the `20260209`/`20260318` web tools; web fetch and documents — including documents returned by tools — via `Citations()`; `enable_citations` turns it on for web fetch only | Anchors cover whole text parts; a fetched PDF is a document source; citations of search results you provided yourself are not included; on those web-tool versions, results read in code execution are uncited |
| [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_CitationsContentBlock.html) | Documents, on Anthropic models | `Citations()`, for text and PDF documents, including documents returned by tools | Other models on Bedrock do not support citations and ignore the setting; anchors cover whole text parts; a document's title is the name Pydantic AI gives it, such as `Document 1`; documents read from S3 are not cited; with citations on, a text document must be UTF-8 or Pydantic AI raises `UserError` |
| [Google Gemini API](https://ai.google.dev/gemini-api/docs/google-search) | Google Search, file search and web fetch | Turn on the tool | Google Search URLs are Google redirect links, and titles are often just the site's domain |
| [Google Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview) | Google Search | Turn on the tool | Same as the Gemini API |
| [OpenAI Chat and Responses](https://platform.openai.com/docs/guides/tools-web-search) | Web pages, and files on Responses | Turn on web search, or file search for files | Other annotation types, such as `container_file_citation`, are available only with `openai_include_raw_annotations` |
| [OpenRouter](https://openrouter.ai/docs/guides/features/server-tools/web-search) | Web pages | Turn on web search | Perplexity Sonar models always search and OpenRouter rejects them with the web search tool; OpenRouter says nothing about where in the text a citation belongs, so citations have no anchor |
| [xAI](https://docs.x.ai/developers/tools/citations) | Web, X and collection citations | `Citations()`, with a search tool such as web search or X search | Turning citations on changes the answer: the model writes Markdown markers such as `[[1]](https://x.com/...)` and the anchor covers the marker; collection citations are document sources |

The table is a snapshot of vendor documentation, not a capability matrix: it records which providers the page speaks for and where each one's caveats sit, and it omits anything the page does not name — notably Anthropic's own raw citation object, and any provider reached through a generic OpenAI-compatible endpoint.

## Limits

- The source is a single vendor documentation page: 1,618 words as declared, 1,692 by local `wc -w` including frontmatter and markup, with **no publication date, author or Pydantic AI version** — so every API name here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule, with `stale_after` set[^pydantic-citations-docs]
- Nothing was executed: no package installed, no agent run, no provider called, no stream consumed, no history serialized and reloaded, and no citation rendered. Every behavioural claim is **Reported**[^pydantic-citations-docs] The one number in the source — smaller models writing markup into tool arguments "about half the time in our tests" — is the vendor's own measurement, quoted and not reproduced.
- The capture lists `MarkerCitationAnchor` and the `None` case nested under `ContentCitationAnchor`, which reads as a Markdown-rendering artifact rather than a class hierarchy; this page treats the three as alternatives, and whether the taxonomy is exhaustive is unstated[^pydantic-citations-docs]
- Unstated by the source: whether citations carry any cost or latency, whether sources or excerpts are de-duplicated or capped, how citations interact with deferred tool approvals or with a fallback model mid-run, which other UI adapters drop citations besides AG-UI, and how a citation behaves when the same text part is replayed through [durable execution](pydantic-ai-durable-execution.md).
- The Anthropic and Bedrock rows are the same publisher's material as [Anthropic server-side tools](anthropic-server-side-tools.md), which covers the caller switch from the models page; the two captures restate each other rather than independently corroborating the citation-versus-sandbox trade-off.
- The samples' model aliases (`anthropic:claude-sonnet-5-5`, `openai:gpt-6.1-sol`) are unpinned, and the `#>` outputs are illustrative rather than recorded runs.

## Relationships

- **Is a core** [capability](pydantic-ai-capability-primitive.md), imported from `pydantic_ai.capabilities` and listed as core in the [capability catalog](pydantic-ai-capability-catalog.md) because provider support, not local logic, decides whether it does anything.
- **Asks the** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md) for their provenance: the web search, web fetch, file search and X search tools on that page are what produce citable results.
- **Routes Anthropic web tools to direct calls**, trading away dynamic filtering — the caller switch compiled in [Anthropic server-side tools](anthropic-server-side-tools.md).
- **Is excluded by** [structured output](pydantic-ai-structured-output.md): tool-call arguments cannot carry citations, so the capability and a structured `output_type` are an either-or unless you accept JSON-text positions.
- **Arrives late under** [streamed output](pydantic-ai-streamed-output.md): citations can trail their text, so the final response is the only complete source.
- **Survives selectively through** [message history](pydantic-ai-message-history.md): the objects are always stored, but only Anthropic web search and OpenAI Responses web/file citations are replayed as citations to the same provider.
- **Keeps** [prompt caching](pydantic-ai-prompt-caching.md) valid when the cited history is sent back unchanged, and breaks it when an edit forces citations to be dropped or re-rendered.
- **Is not forwarded by** the AG-UI adapter, which makes the adapter choice in [client-supplied history](pydantic-ai-client-supplied-history.md) a citation-visible boundary.
- **Quotes evidence from** documents sent as [multimodal input](pydantic-ai-multimodal-input.md), which is why excerpts can contain your own document text and need screening before being logged.

[^pydantic-citations-docs]: Pydantic Docs, "Citations", <https://pydantic.dev/docs/ai/core-concepts/citations/>, 1,618 words as declared and 1,692 by local `wc -w`, no publication date, author or Pydantic AI version; local capture `raw/core-concepts/citations/index.md`, 179 lines, content digest sha256:6cb9167e. Lines 10–12 for the definition, `TextPart.citations` and the unchanged text; §"Turning citations on" (14–38) for unasked search-tool citation, the providers that must be asked, the `Citations()` import and document sample, and the answer-without-citations caveat; §"Reading citations" (40–124) for `sources`, `WebCitationSource`/`DocumentCitationSource`, the provider-ID `document_id`, the excerpt and grouping caveats, the `anchor` character positions with `ContentCitationAnchor`/`MarkerCitationAnchor`/`None`, the OpenAI `provider_details['citations']` position, the render sample and the three-provider rendering; §"Citations, tools and structured output" (126–142) for text-only citation attachment, the `[str, Answer]` case, the Anthropic markup in non-text fields, the three `Citations()` outcomes, the `NativeOutput` rejection, the xAI text answer, the web search and `enable_citations` exceptions, the code-execution uncited rule, and the JSON-text behaviour on other providers; §"Good to know" (144–149) for late citations per provider, AG-UI, excerpt trust and `provider_details['citations']`; §"Citations in message history" (151–166) for the round-trip table, the plain-text degradation, the edit rule and the prompt-caching reason, plus the Vercel AI adapter; §"Provider support" (168–178) for the seven provider rows. Evidence class: **Reported** — vendor documentation; nothing was run, streamed, cited or replayed.
