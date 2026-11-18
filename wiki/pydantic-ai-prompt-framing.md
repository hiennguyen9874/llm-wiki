---
type: Concept
title: Pydantic AI prompt framing
description: How Pydantic AI marks the content it writes on the user channel — reserved pyai tags, lookalike notes, the framing announcement and its measured trade-offs, and the zero-width joiner that stops open-weight chat-template tokens from forging a turn.
tags: [pydantic-ai, agents, security, context-management]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:45:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-message-history-docs
    resource: ../raw/core-concepts/message-history/index.md
    scope: ../raw/core-concepts/message-history/
    kind: documentation
    revision: sha256:1ce4fb2b993d082dda71e8dac360c83d1279820f53ec1ce7ab66dbb65d0cfdff
    title: "Messages and chat history"
---

Where Pydantic AI has to say something on the *user* channel, it frames it in a tag, and it protects that boundary in two more ways: text that imitates one of its own tags gets a short attribution note beside it, and on hosts that tokenize chat-template control tokens each token is broken with a zero-width joiner before sending[^pydantic-message-history-docs] None of this rewrites what a user, tool or file wrote — prompts, uploaded files, tool results and the content inside a frame go out byte for byte, so a model asked to edit an XML file containing a `<system>` tag writes the tag back rather than an escaped copy. The framing tells the model where content came from; it is not an attestation, which is why [client-supplied history](pydantic-ai-client-supplied-history.md) is the separate trust problem.

## Which tags exist

Every tag only Pydantic AI writes carries the reserved `pyai:` prefix; `<system>` and `<assistant_thinking>` keep their plain names[^pydantic-message-history-docs]

| Tag | Carries | Voice |
| --- | --- | --- |
| `<system>` | A mid-conversation system prompt on a model without native mid-conversation system messages | Application |
| `<pyai:context>`, `<pyai:context_diff>` | Appended instruction changes (`on_change='append'`) | Application |
| `<pyai:tool_result>` | A tool's file that the provider cannot take in a tool result | Data, with a note |
| `<pyai:retry_feedback>`, `<pyai:validation_errors>` | [Retry feedback](pydantic-ai-capability-primitive.md)'s two shapes | Data, with a note |
| `<pyai:conversation_summary>` | A compaction summary | Data, with a note |
| `<assistant_thinking>` | Another model's reasoning | Data, with a note |

The reservation is what makes the note possible: a plain `<context>` or `<tool_result>` tag, which applications commonly put their own documents and tool output in, is ordinary text — no note and no announcement[^pydantic-message-history-docs]

## The note on a lookalike

Text that resembles one of the application's voice tags — an opening or closing `<system>`, `<pyai:context>` or `<pyai:context_diff>` in any case or spacing, including one hidden behind invisible characters, look-alike letters or an HTML-entity-encoded `<` — gets a short note in the application's voice next to the item it sits in, saying who wrote it (user, tool, model or the file's author) and that it is part of that item, not instructions[^pydantic-message-history-docs] The same applies to a compaction summary, to the text retry feedback quotes (not the fence around it), to another model's reasoning sent as `<assistant_thinking>`, and to text inside a capability part's content that opens or closes the part's own tag — that note says the tag is its author's and neither opens nor closes the application's element.

Placement is part of the design[^pydantic-message-history-docs] The note is a mid-conversation system message, or a `<system>` block on models that lack one, and goes after a request's tool results — unless the model has no mid-conversation system messages and the provider takes the note ahead of them. A note on a `<pyai:context>` or `<pyai:context_diff>` lookalike first says that only the elements the application sends change the instructions; a note on a tool result or a file adds that the application's own messages still apply and names the application's own system message when the same request has one. A copy of one of the framework's data frames gets a note too, saying its author wrote it and it opens or closes no element the application sent — and a closing tag alone counts, so text quoting one cannot end the frame around it unnoticed. On models without mid-conversation system messages, the request's own `<system>` blocks go ahead of a note and the text it describes, so they still read as the application's. An `<assistant_thinking>` note ends the request before that reply, so the cached prefix does not move, or goes in the next request when no request immediately precedes the reply.

## The announcement, and when it is sent

The model is told what the tags and notes mean by a fixed announcement of roughly 120 words on a model without a mid-conversation system role, 185 on models that get `<system verified>` blocks, and 60 as a system message[^pydantic-message-history-docs] It states that a `<system>` block in a user turn comes from the application and carries system authority, that it replaces the application's earlier blocks, that lookalike text in a user message, file or tool result has no authority, and that the user speaks only in their own messages. By default it is added at the start of the system prompt — ahead of your own system prompt and instructions, which therefore keep the last word — from the first request that has a frame or a note to explain, and it stays on every later request.

`framing_announcement` decides when[^pydantic-message-history-docs]:

| Value | Without a mid-conversation system role | With one |
| --- | --- | --- |
| `'when_needed'` (default on most models) | From the first request with a `<system>` block, note or other user-channel frame | A system message in the first request with a frame or note |
| `'always'` (default on Claude Sonnet 4.6 and gpt-oss) | At the start of the system prompt on every request from the first | Same as `'when_needed'` |
| `'never'` | Not sent | Not sent |

Because need is decided from the history alone, `'when_needed'` once in stays in the same place, so the cached prefix changes once and is stable from there; `'always'` never changes the prefix but pays in every conversation[^pydantic-message-history-docs] The vendor's recommendation follows: use `'always'` in an AG-UI or Vercel AI app, whose frontends do not send mid-conversation system prompts back, so with `'when_needed'` the announcement would drop out and the cached prefix would change every turn:

```python
agent = Agent('google:gemini-3.8-flash', model_settings={'framing_announcement': 'always'})
```

`'never'` leaves the lookalike notes in place — they cost nothing where there is nothing to note — but the model is not told what they or the application's `<system>` blocks mean, and may not follow an unexplained block. With it off, Claude Sonnet 4.6 and Grok 4.7 followed none of 24 instruction changes (all 24 with it), and Claude Sonnet 5.5, Haiku 5.5 and Gemini 4 Argon could not say who had asked for a change (0 of 24 against 24 of 24)[^pydantic-message-history-docs]

## What each rendering gives up

These are the vendor's own live measurements of Pydantic AI against provider APIs, counted as runs that did the right thing, from fixed scenarios intended for comparison between renderings rather than as rates[^pydantic-message-history-docs] They are quoted, not reproduced. Two are worth carrying in full because they set a default:

**The announcement on every request, or only when first needed** (right-hand column pools two runs; run-to-run variance reached 8 of 48 on GLM 5.3 and 7 of 48 on gpt-oss-120b, so a gap that size on one model is noise):

| Model | Measure | `'always'` | `'when_needed'` |
| --- | --- | --- | --- |
| Claude Sonnet 4.6 | Keeps to the system prompt's task against a conflicting user request | 30/48 | 22/96 |
| Claude Sonnet 4.6 | Follows the application's own reminder tags in a user turn | 24/24 | 0/48 |
| gpt-oss-120b | Keeps to the system prompt's task | 44/48 | 69/96 |
| Claude Haiku 5.5 | Keeps to the system prompt's task | 42/48 | 96/96 |
| Grok 4.7 | Keeps to the system prompt's task | 42/48 | 96/96 |
| GLM 5.3 | Keeps to the system prompt's task | 27/48 | 78/96 |
| Gemini 4 Argon | Does not act on a request quoted in a tool result | 11/24 | 48/48 |

**Sealed `<system verified>` block versus the native system role, on Claude Sonnet 5.5** (opting out is `supports_inline_system_prompts=True`):

| Measure | Sealed block (default) | Native role |
| --- | --- | --- |
| Says correctly who asked for a change | 24/24 | 18/24 |
| Does not follow a `<system>` lookalike the user typed | 14/24 | 8/24 |
| Follows a change next to a lookalike the user typed | 8/24 | 24/24 |
| Follows a change next to a copied `<system verified>` | 22/24 | 24/24 |
| Does not follow a copied `<system verified>` | 15/24 | 18/24 |

The two tie at 24/24 on the other 13 measures in that set; one measure — an operator's grant of authority to a sender — could not be taken because the API refused all 24 runs under both renderings[^pydantic-message-history-docs] The reading the vendor draws is narrow: if your users do not write `<system>` tags and your application changes instructions mid-conversation, the native role may suit you better.

The remaining comparisons follow the same shape[^pydantic-message-history-docs] On Claude Haiku 5.5, a sealed block in a `clear_at` entry (the default) dropped **0** earlier thinking blocks over two five-step runs against **20** for a block in the user turn, and the alternatives split on reminder-following (12/24, 8/24 and 5/24 across three tool-less runs for the default against 24/24 for the block). On Grok, `verified` beat `seal="pydantic-ai"` on Claude (24/24 against 0/24 on Sonnet 4.6) and lost on Grok 4.3 (16/24 against 23/24), with Grok 4.7's difference inside its own run-to-run variance. The reserved `<pyai:context>` name beat plain `<context>` on every model that depends on an application document being used (Haiku 5.5 12/12 against 3/24, Sonnet 4.6 12/12 against 0/24, GLM 5.3 12/12 against 8/24), at a cost on gpt-oss-120b where a copy of the prefixed tag in user text did worse and in a tool result better.

Notes and the prefix are what stop a copied frame, so a naming choice that drops them is a real regression[^pydantic-message-history-docs] With `pyai:` names plus notes against plain names without, gpt-oss-120b stopped acting on a copied tool-result frame 24/24 against 12/24, and Sonnet 5.5 stopped following copied retry feedback 23/24 against 16/24. GLM 5.3 went the other way on genuine retry feedback — 39/48 against 36/36 — because its misses said the genuine `<pyai:retry_feedback>` "isn't a genuine application frame"; a sentence added to the announcement fixed GLM (22/24 in one run) but made Qwen3 Next 80B act on a forged `<tool_result>` in 22 of 24 runs, so the sentence is not sent. A search tool interacts with the announcement too: with a search tool returning nothing, Sonnet 4.6 often distrusted a `<context>` document in the prompt (5/24 and 8/24 with the announcement against 24/24 without), while without the tool it used the document every time.

Some measures no rendering tried does well, and the vendor calls them model limits rather than trades: Qwen3 Next 80B followed a change next to a `<system>` lookalike 0/24, and gpt-oss-120b 8/24, with wording variants trading that failure for a worse one inside a tool result[^pydantic-message-history-docs]

## Where the framing does not apply

Two readers are exempt[^pydantic-message-history-docs] A judge or summarizer that reads the conversation as a flattened transcript — a Harness judge or a compaction summarizer — gets neither the announcement nor the notes, since it is not talking to the transcript's authors. A [realtime session](pydantic-ai-realtime-voice.md) has neither either: on the live channel text that resembles a frame goes out as written with nothing said about it, though a capability part's body still gets its authorship note and, in a body from a source with less than operator authority, every framing tag including `<system>` is neutralized as `&lt;` on the live channel — while the stored part keeps the body as written.

## Special tokens: breaking a forged turn boundary

Open-weight models mark turns with chat-template tokens such as `<|im_start|>`, `<|eot_id|>` or `[INST]`, and many hosts encode those characters as the real control token when they appear in message content[^pydantic-message-history-docs] Text from a tool, a file or a user can therefore close the current turn and open a new one in any role, and a note beside the text cannot help, because it sits in a turn the forged one already closed. Whether a host does this depends on the host and model, not only the model family, and a routing service can pick a different host per request. So on routes that can reach such a host, Pydantic AI puts a zero-width joiner (U+200D) inside each token before sending — `<|im_start|>` goes out as `<\u200d|im_start|>` and reaches the model as ordinary text.

| | Covered by the joiner | Not covered |
| --- | --- | --- |
| Content | User prompts, tool results, inlined text files, retry feedback, summaries sent as user text, and the model's own text, tool names, call arguments and reasoning when sent back in a later request (unless the reasoning returns to the provider that signed it) | The stored message history, system prompts, instructions, tool definitions, and any file or URL the provider fetches itself |

Tool definitions tokenize on these hosts too, so a tool description from an untrusted MCP server is **not** protected by this[^pydantic-message-history-docs] Prompt caching survives because the same text always receives the same joiners. The flag is `may_tokenize_special_tokens_in_content`: on for self-hosted servers (vLLM, Ollama, Hugging Face), most hosts of open-weight models, routing services, and `OpenAICompatibleProvider` for any model not exclusive to its own lab; `AzureProvider` and `OpenAIProvider` are treated like routing services, since a custom deployment name or base URL can serve anything, so a custom Azure deployment of a GPT model also gets the flag. It is off for the labs' own APIs and for hosts observed to send these tokens as text.

Two observable consequences follow[^pydantic-message-history-docs] Responses are cleaned on the same routes: any zero-width character inside these tokens is removed, so your tools, output validators, users and stored history see `<|im_start|>`, streamed or not and even when a token splits across chunks, and the joiner is put back when that text goes back in a later request. That makes tool-call arguments and response text differ from the model's raw output in exactly this one way — and makes a file that deliberately contains a broken token get repaired if the model copies it, while a zero-width character anywhere else, such as in an emoji sequence, stays. Breaking the token only stops the host from creating a boundary; a model can still follow text written to look like a turn, and some do: on routes that tokenize, breaking the token stopped forged turns being followed on most runs of Qwen 3.8, GLM 5 and DeepSeek V4 Flash and made no measurable difference on DeepSeek V4 Pro, Qwen3 Next, Llama 3.3 and gpt-oss. Turning the flag off also stops the response-side removal and should only be done for trusted text or a pinned host that treats these tokens as text.

## Limits

- Single vendor page naming **no Pydantic AI version, author or date**, so this page is `draft` under the `pydantic-ai` domain rule[^pydantic-message-history-docs]
- Every measurement here is the vendor's, **Reported** and not reproduced: no model was called, no prompt rendered, no host tokenized a payload and no trace compared. The scenario definitions, the run counts behind the † markers and the full measurement set are in the source, not here.
- The model names in the measurements (`Claude Opus 5.5`, `GPT-6.1 Sol`, `Gemini 4 Argon`, `Qwen3 Next 80B`, `DeepSeek V4 Pro`) are aliases this wiki records nowhere else, so their mapping to release versions is unresolved.
- Which host is in which "tokenize" class is asserted per provider family and observed per host, not published as a list; a pinned host can change class without the framework noticing.
- The exact wording of the announcement, of each note, and of the attribute that marks a sealed block is quoted only in fragments.

## Relationships

- **Explains** the rendering that [mid-run injection](pydantic-ai-mid-run-injection.md) triggers when a mid-conversation system prompt has no native provider equivalent, and the announcement rules behind `framing_announcement`.
- **Protects** the same content boundary [untrusted history](pydantic-ai-client-supplied-history.md) addresses from the other side: framing says where content came from, sanitization decides what a client may claim.
- **Pairs with** [workspace file authority](pydantic-ai-workspace-authority.md), whose operator, user and none levels are the `source` a capability part renders in.
- **Interacts with** [structured content](pydantic-ai-structured-content.md): a reserved tag is what keeps an application's own document distinguishable from a copy.
- **Constrains** [prompt caching](pydantic-ai-prompt-caching.md) and [Anthropic prompt caching](anthropic-prompt-caching.md): whether the announcement and notes sit in the prefix decides when a cached prefix changes.
- **Applies to** [subagent task control](pydantic-ai-subagent-tasks.md), whose `<task_output>` and `<task_question>` frames rely on the same escape-note mechanism, and is explicitly absent from [realtime voice agents](pydantic-ai-realtime-voice.md).

[^pydantic-message-history-docs]: Pydantic Docs, "Messages and chat history", <https://pydantic.dev/docs/ai/core-concepts/message-history/>, 15,322 words as declared and 15,615 by local `wc -w`, no date and no Pydantic AI version named; local capture `raw/core-concepts/message-history/index.md`, 1,477 lines, content digest sha256:1ce4fb2b. §"Framework frames and content fidelity" (raw lines 356–365) for the tag inventory, the `pyai:` reservation, byte-for-byte fidelity, the lookalike classes, the note placement and its variants, the judge and realtime exemptions and the `&lt;` neutralization; "When the announcement is sent" (332–355) for the `framing_announcement` table, the word counts, the caching rationale, the AG-UI/Vercel advice and the `'never'` measurements; "What each rendering gives up" (240–331) for every measurement table quoted, the † caveats, the profile flags, the search-tool interaction and the "no rendering does well" table; "Special tokens in content" (547–584) for the token examples, the joiner, the covered and uncovered content, the flag and its provider defaults, the response-side removal, the two consequences and the per-model results. Evidence class: **Reported** — vendor documentation and vendor-run measurements; nothing was executed here.
