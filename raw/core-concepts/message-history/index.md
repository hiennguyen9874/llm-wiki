---
title: "Messages and chat history"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/message-history/"
domain: "pydantic.dev"
language: "en"
description: "Continue multi-turn conversations with Pydantic AI message history: reuse and store messages as JSON, inject messages mid-run, and trim or summarize history."
word_count: 15322
---

Pydantic AI provides access to messages exchanged during an agent run. These messages can be used both to continue a coherent conversation, and to understand how an agent performed.

### Accessing Messages from Results

After running an agent, you can access the messages exchanged during that run from the `result` object.

Both [`RunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult) (returned by [`Agent.run`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run), [`Agent.run_sync`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_sync)) and [`StreamedRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult) (returned by [`Agent.run_stream`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream)) have the following methods:

- [`all_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.all_messages): returns all messages, including messages from prior runs. There’s also a variant that returns JSON bytes, [`all_messages_json()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.all_messages_json).
- [`new_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.new_messages): returns only the messages from the current run. There’s also a variant that returns JSON bytes, [`new_messages_json()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.new_messages_json).

Example of accessing methods on a [`RunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult):

run\_result\_messages.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

result = agent.run_sync('Tell me a joke.')
print(result.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

# all messages from the run
print(result.all_messages())
"""
[
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        instructions='Be a helpful assistant.',
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.'
            )
        ],
        usage=RequestUsage(cost=Decimal('0.00023'), input_tokens=55, output_tokens=12),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
]
"""
```

*(This example is complete, it can be run “as is”)*

Example of accessing methods on a [`StreamedRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult):

streamed\_run\_result\_messages.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

async def main():
    async with agent.run_stream('Tell me a joke.') as result:
        # incomplete messages before the stream finishes
        print(result.all_messages())
        """
        [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content='Tell me a joke.',
                        timestamp=datetime.datetime(...),
                    )
                ],
                timestamp=datetime.datetime(...),
                instructions='Be a helpful assistant.',
                run_id='...',
                conversation_id='...',
            )
        ]
        """

        async for text in result.stream_text():
            print(text)
            #> Did you hear
            #> Did you hear about the toothpaste
            #> Did you hear about the toothpaste scandal? They called
            #> Did you hear about the toothpaste scandal? They called it Colgate.

        # complete messages once the stream finishes
        print(result.all_messages())
        """
        [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content='Tell me a joke.',
                        timestamp=datetime.datetime(...),
                    )
                ],
                timestamp=datetime.datetime(...),
                instructions='Be a helpful assistant.',
                run_id='...',
                conversation_id='...',
            ),
            ModelResponse(
                parts=[
                    TextPart(
                        content='Did you hear about the toothpaste scandal? They called it Colgate.'
                    )
                ],
                usage=RequestUsage(input_tokens=50, output_tokens=12),
                model_name='gpt-6.1-sol',
                model_id='openai:gpt-6.1-sol',
                timestamp=datetime.datetime(...),
                run_id='...',
                conversation_id='...',
            ),
        ]
        """
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

### Using Messages as Input for Further Agent Runs

The primary use of message histories in Pydantic AI is to maintain context across multiple agent runs.

To use existing messages in a run, pass them to the `message_history` parameter of [`Agent.run`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run), [`Agent.run_sync`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_sync) or [`Agent.run_stream`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream).

If `message_history` is set and not empty, a new system prompt is not generated — we assume the existing message history includes a system prompt. If your history comes from a source that doesn’t round-trip system prompts (a UI frontend, a database that didn’t persist them, a compaction pipeline), add the [`ReinjectSystemPrompt`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ReinjectSystemPrompt) capability so the agent’s configured `system_prompt` is reinjected at the head of the first request when it’s missing.

Reusing messages in a conversation

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync('Explain?', message_history=result1.new_messages())
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.

print(result2.all_messages())
"""
[
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        instructions='Be a helpful assistant.',
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.'
            )
        ],
        usage=RequestUsage(cost=Decimal('0.00023'), input_tokens=55, output_tokens=12),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Explain?',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        instructions='Be a helpful assistant.',
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='This is an excellent joke invented by Samuel Colvin, it needs no explanation.'
            )
        ],
        usage=RequestUsage(cost=Decimal('0.000372'), input_tokens=56, output_tokens=26),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
]
"""
```

*(This example is complete, it can be run “as is”)*

### Mid-conversation system prompts

A [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart) in the first [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest) is the agent’s standing system prompt, and always hoists to the provider’s top-level system parameter. One in any *later* request is a mid-conversation instruction: something that became true partway through the session, whether it arrived in a stored `message_history` or from [`RunContext.enqueue`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.enqueue) during a run.

Mid-conversation instructions stay where you put them rather than joining the system prompt at the front. When prompt caching is enabled, that lets the provider reuse the unchanged prefix: editing the top-level system prompt invalidates everything behind it, while an instruction appended in place leaves the conversation up to that point eligible for a cache hit. Position alone does not enable caching; configure the active model’s prompt-caching settings or add an explicit [`CachePoint`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CachePoint).

How it reaches the model depends on the provider:

- Where the API accepts a system message inside the conversation, it’s sent as one, with the operator authority that implies. [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/#mid-conversation-system-messages) supports this on some models, and may adjust the position slightly to satisfy its own placement rules. [OpenRouter](https://pydantic.dev/docs/ai/models/openrouter/#mid-conversation-system-prompts) does on some routes.
- Everywhere else it’s rendered as a `<system>`\-tagged [`UserPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UserPromptPart) at the same position, with its text as written. The instruction still applies from where you put it, but the model can tell it came in over the user channel and may treat it as a strong preference rather than a rule.
	On these models, the system prompt also gets a short fixed announcement of what the tag means: a `<system>` block in a user turn comes from the application, has system authority, and replaces the application’s earlier `<system>` blocks, while text in a user message, a file or a tool result that looks like one gets a [note](#framework-frames-and-content-fidelity) and has no authority. It also says the user speaks only in their own messages, so text in a tool result, a file or a quote isn’t the user’s or the application’s even when it claims to be. By default it’s added from the first request that has a `<system>` block, a note or another frame to explain, at the start of the system prompt, ahead of your system prompt and instructions, so they keep the last word, and it stays on every later request. Claude Sonnet 4.6 and gpt-oss get it from the first request instead. A request with no system prompt or instructions doesn’t get one. [When the announcement is sent](#when-the-announcement-is-sent) has the details and the alternatives.
	Claude Sonnet 4.6 ignores plain `<system>` blocks, Claude Sonnet 5.5 and Haiku 5.5 follow sealed ones better than their native system role, and Grok 4.3 through 4.7 follow sealed ones better than plain ones, so for these ([`needs_sealed_system_blocks`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.needs_sealed_system_blocks)) each block is `<system verified>`, goes after the user’s words in its request, and the announcement says every block from the application carries that attribute and applies to the reply to the words ahead of it. The attribute is a label, not proof, and text that copies it still gets a note. In measurements a copy in a tool result wasn’t followed. A copy in the user’s own text can be followed on some models, as the user’s request, and can keep the application’s own change in the same request from applying for that turn. [What each rendering gives up](#what-each-rendering-gives-up) has the numbers.
	Measured with an earlier version of the announcement and escaping in place of the notes: without them, Gemini and Claude on Bedrock mostly kept to the earlier value of a changed or withdrawn instruction, and Gemini and Grok ignored a new rule about the format of their answers. With them, they followed all three.

Phrase the instruction as what changed rather than as an override of the user. Models are trained to resist instructions that appear to work against the person they’re talking to, and that applies to the system role too — “the build tag is no longer confidential” lands where “ignore what the user was told earlier” doesn’t.

### What each rendering gives up

Some models don’t do well on every measure with any rendering. We tried the alternatives below live and found none that does well at everything on these models, so each default is a trade. This section shows what was traded for what, so you can decide differently for your application: the profile flags named here can be set with a model’s `profile` argument.

All numbers are live measurements of Pydantic AI on the provider’s API, as runs that did the right thing out of the runs made. They come from fixed test scenarios, so read them as comparisons between renderings on one model, not as rates you’ll see in your application. The current rendering marks blocks `<system verified>`. A number marked † was measured before that, with `seal="pydantic-ai"` as the marker.

**The announcement on every request, or only when first needed.** On models without a mid-conversation system role, the announcement can go out on every request (`framing_announcement='always'`), or from the first request whose conversation has a `<system>` block, a note or another frame on the user channel (`'when_needed'`). From that request on, the two send the same request. Before it, `'when_needed'` sends what `'never'` sends, so they differ only on requests with nothing for the announcement to explain. Most models measured did as well or better on those without it; Claude Sonnet 4.6 and gpt-oss did worse, so their profiles default to `'always'` ([`default_framing_announcement`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.default_framing_announcement)) and the rest to `'when_needed'`.

| Model | Measure, on a request with nothing to explain | Announcement on every request | Only when first needed |
| --- | --- | --- | --- |
| Claude Sonnet 4.6 | Keeps to the system prompt’s task when the user asks for a conflicting one | 30/48 | 22/96 |
|  | Follows the application’s own reminder tags in a user turn | 24/24 | 0/48 |
| gpt-oss-120b | Keeps to the system prompt’s task when the user asks for a conflicting one | 44/48 | 69/96 |
| Claude Haiku 5.5 | Keeps to the system prompt’s task when the user asks for a conflicting one | 42/48 | 96/96 |
| Grok 4.7 | Keeps to the system prompt’s task when the user asks for a conflicting one | 42/48 | 96/96 |
|  | Follows the application’s own reminder tags in a user turn | 5/24 | 0/48 |
| GLM 5.3 | Keeps to the system prompt’s task when the user asks for a conflicting one | 27/48 | 78/96 |
| Gemini 4 Argon | Doesn’t act on a request quoted in a tool result that an operator instruction seems to cover | 11/24 | 48/48 |

The right-hand column pools two runs of the same requests. Between two such runs, results differed by up to 8 of 48 on GLM 5.3 and 7 of 48 on gpt-oss-120b, so read a gap of that size on one model as noise. The cached prompt prefix changes once with `'when_needed'`, at the request that first needs the announcement.

**The `<system verified>` block rather than a native system role, on Claude Sonnet 5.5.** Opt out with `supports_inline_system_prompts=True` in the model’s profile.

| Measure | `<system verified>` (default) | Native system role |
| --- | --- | --- |
| Says correctly who asked for a change | 24/24 | 18/24 |
| Doesn’t follow a `<system>` lookalike the user typed | 14/24 | 8/24 |
| Follows a change next to a `<system>` lookalike the user typed | 8/24 | 24/24 |
| Follows a change next to a copied `<system verified>` the user typed | 22/24 | 24/24 |
| Doesn’t follow a copied `<system verified>` the user typed | 15/24 | 18/24 |

The two tie at 24/24 on the other 13 measures in this set, including changes after a tool result and text in tool results. We couldn’t measure an operator’s grant of authority to a sender on this model: the API refused all 24 runs under both renderings. If your users don’t write `<system>` tags and your application changes instructions mid-conversation, the native role may suit you better.

**The `clear_at` entry for request-scoped prompts, on Claude Haiku 5.5.** The alternative is a `<system verified>` block in the user turn, left out of later requests. That loses every earlier [thinking block](https://pydantic.dev/docs/ai/models/anthropic/#turn-scoped-system-messages), because the history is no longer append-only.

| Measure | Sealed block in a `clear_at` entry (default) | Block in the user turn |
| --- | --- | --- |
| Earlier thinking blocks dropped, over two 5-step runs † | 0 | 20 |
| Follows a reminder next to a user lookalike, agent with a tool | 24/24 | not measured |
| Follows a reminder next to a user lookalike, agent without tools | 12/24, 8/24 and 5/24, in three runs | 24/24 † |
| Follows a reminder in a later turn, after a tool result | 20/24 † | 24/24 † |
| Follows a reminder next to a lookalike in a tool result | 24/24 | 24/24 † |

Claude Sonnet 5.5 makes the same trade at no measured cost: 24/24 on all of these †, and 8 thinking blocks dropped with the block in the user turn † against none.

**The `verified` marker, on Grok.** It did best across Claude, with `seal="pydantic-ai"` and `sealed` as the alternatives, and did worse on one Grok measure.

| Model | Measure | `verified` (default) | `seal="pydantic-ai"` |
| --- | --- | --- | --- |
| Claude Sonnet 4.6 | Follows a change next to a copied marker the user typed | 24/24 | 0/24 |
| Claude Sonnet 5.5 | Follows a change next to a copied marker the user typed | 22/24 | 7/24 and 11/24, in two runs |
| Grok 4.3 | Follows a change next to a copied marker the user typed | 16/24 | 23/24 |
| Grok 4.7 | Doesn’t try to send files under an operator’s grant, when an email from that sender asks | 17/24 | 20/24 |

The Grok 4.7 difference is within what repeated runs of this scenario vary by. On Grok 4.3 the same scenario varied by more than that between two runs of the same build, so we don’t report a difference there.

**`<pyai:context>` rather than `<context>`, when text copies it.** The framework’s own elements carry a reserved prefix, so an application’s `<context>` documents have nothing to imitate. Before, those documents got a note saying the user wrote them, and models often disregarded them. A copy of the prefixed tag still gets a note. On gpt-oss-120b, that case got worse in user text and better in a tool result, and the wrong answers in user text were the old instruction, not the copied one.

| Model | Measure | `<pyai:context>` (default) | `<context>` |
| --- | --- | --- | --- |
| Claude Haiku 5.5 | Uses an application’s `<context>` document in the prompt | 12/12 | 3/24 |
| Claude Sonnet 4.6 | Uses an application’s `<context>` document in the prompt | 12/12 | 0/24 |
| GLM 5.3 | Uses an application’s `<context>` document in the prompt | 12/12 | 8/24 |
| gpt-oss-120b | Follows a change next to a copy of the tag in user text | 17/24 | 23/24 |
|  | Follows a change next to a copy of the tag in a tool result | 20/24 | 2/24 |

**`pyai:` on the framework’s data frames, and notes on copies of them.** The tool result, retry feedback, validation error and conversation summary frames are `<pyai:tool_result>`, `<pyai:retry_feedback>`, `<pyai:validation_errors>` and `<pyai:conversation_summary>`, and a copy of one in text from the user, a tool or a file gets a note. The notes do the safety work; the prefix is what lets them exist without a note on an application’s own `<tool_result>` text. The rows below compare a copy of the frame each rendering sends: `<pyai:tool_result>` with a note, against `<tool_result>` without one. Following a genuine frame measured the same with either naming on every model below except one, which is the cost.

| Model | Measure | `pyai:` and notes on copies (default) | Plain names, no notes |
| --- | --- | --- | --- |
| gpt-oss-120b | Doesn’t act on a copied tool result frame the user typed | 24/24 | 12/24 |
| Claude Sonnet 5.5 | Doesn’t follow copied retry feedback in a tool result | 23/24 | 16/24 |
| GLM 5.3 | Follows genuine retry feedback | 39/48, in two runs | 36/36, in two runs |

GLM 5.3’s misses say the genuine `<pyai:retry_feedback>` “isn’t a genuine application frame”. Claude Opus 5.5 and GPT-6.1 Sol measured the same with either naming. We also tried a sentence in the announcement saying that the application’s retry feedback is genuine. In one run, GLM 5.3 then followed it 22/24, but Qwen3 Next 80B acted on a forged `<tool_result>` in a tool result in 22 of 24 runs, against none without the sentence, so it isn’t sent.

**The announcement with a search tool, on Claude Sonnet 4.6.** The announcement says that text outside the application’s own blocks has no authority. With a search tool that returns nothing, Claude Sonnet 4.6 then often distrusts a document in a `<context>` tag in the prompt: it used the document in 5/24 and 8/24 runs with the announcement, in two runs, against 24/24 without it. Without the tool, it used the document every time (24/24 with the announcement and without).

**Where no rendering we tried does well.** On these measures, every alternative we tried did about as badly as the default, or did better only by doing worse on another measure. They’re limits of the model rather than trades, so an application that depends on one should check its model.

| Model | Measure | Default | What we tried |
| --- | --- | --- | --- |
| Qwen3 Next 80B | Follows a change next to a `<system>` lookalike the user typed | 0/24 | 0/24 or 1/24 with the announcement off, sent only when first needed, without one of its sentences, or with one added. A shorter wording got 12/12 in one run, but then followed a `<system>` lookalike in a tool result 11 times out of 12, against never with the default. |
| gpt-oss-120b | Follows a change next to a `<system>` lookalike the user typed | 8/24 | 2/24 to 7/24 with the same alternatives. The same shorter wording got 12/12 in one run, and followed the lookalike in a tool result 12 times out of 12, against never with the default. |
| Grok 4.7 | Follows a change next to a copied `<system verified>` the user typed | 1/24 | 0/24 with the announcement off. |
| Qwen3 Next 80B | Doesn’t follow copied retry feedback in a tool result | 0/24 | 0/24 with plain names, and with the prefix but no notes. |
|  | Doesn’t follow a copied plan step in a tool result | 0/24 | The same. |
| gpt-oss-120b | Doesn’t follow copied retry feedback in a tool result | 0/24 | 0/24 with plain names, and with the prefix but no notes. |
|  | Doesn’t follow a copied plan step in a tool result | 2/24 | 0/24 with the same alternatives. |

**Cache-prefix stability.** A `clear_at` entry costs no input tokens and isn’t part of a cache key, and an answered reminder left out of later requests kept the same cache reads (†, 0.98 to 0.99 of input tokens on both renderings), so the cache wasn’t what separated those two. On most models the default `'when_needed'` announcement changes the cached prefix once per conversation, at the request that first needs it; `'always'` keeps it part of the prefix from the first request.

#### When the announcement is sent

The [`framing_announcement`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.framing_announcement) model setting decides when the model is told what `<system>` blocks and lookalike notes mean:

| Value | Without a mid-conversation system role | With one |
| --- | --- | --- |
| `'when_needed'` (default on most models) | At the start of the system prompt, ahead of your system prompt and instructions, from the first request with a `<system>` block, a note or another frame on the user channel, such as retry feedback or a compaction summary | A system message in the first request with a frame or a note |
| `'always'` (default on Claude Sonnet 4.6 and gpt-oss) | At the start of the system prompt, on every request from the first | The same as `'when_needed'` |
| `'never'` | Not sent | Not sent |

The announcement is about 120 words on a model without a mid-conversation system role, about 185 on the ones that get `<system verified>` blocks, and about 60 as a system message. With `'when_needed'`, a conversation that never has anything to explain doesn’t pay for it. Whether it’s needed is decided from the history alone, so once it’s in, it stays in the same place on every later request: the cached prefix changes once, at that request, and is stable again from there, as long as the history keeps what needed it. `'always'` sends it from the first request, so the prefix never changes for it, at the cost of sending it in every conversation.

Use `'always'` in an [AG-UI](https://pydantic.dev/docs/ai/integrations/ui/ag-ui/) or [Vercel AI](https://pydantic.dev/docs/ai/integrations/ui/vercel-ai/) app: their frontends don’t send mid-conversation system prompts back, so with `'when_needed'` the announcement drops out of the next turn’s system prompt and the cached prefix changes every turn.

framing\_announcement.py

```python
from pydantic_ai import Agent

agent = Agent('google:gemini-3.8-flash', model_settings={'framing_announcement': 'always'})
```

`'never'` leaves the lookalike notes in place: they only appear next to text that resembles one of the application’s frames, so they cost nothing in a conversation without any. Without the announcement, though, the model isn’t told what the notes or the application’s `<system>` blocks mean, and it may not follow a `<system>` block it has no explanation for. With it turned off, Claude Sonnet 4.6 and Grok 4.7 followed none of 24 instruction changes (all 24 with it), and Claude Sonnet 5.5, Claude Haiku 5.5 and Gemini 4 Argon couldn’t say who had asked for a change (0 of 24, against 24 of 24). Turn it off only if your application doesn’t change instructions mid-conversation and you’ve checked your model without it.

### Framework frames and content fidelity

Where Pydantic AI has to say something on the user channel, it frames it in a tag: a mid-conversation system prompt as `<system>` on a model [without mid-conversation system messages](#mid-conversation-system-prompts), a tool’s file that the provider can’t take in a tool result as `<pyai:tool_result>` ([details](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-return-file-provenance)), [retry feedback](https://pydantic.dev/docs/ai/core-concepts/retries/) as `<pyai:retry_feedback>` or `<pyai:validation_errors>`, a [compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) summary as `<pyai:conversation_summary>`, and another model’s reasoning as `<assistant_thinking>`. Three of these speak in the application’s voice: `<system>`, and the `<pyai:context>` and `<pyai:context_diff>` elements that [appended instruction changes](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes) are sent as. Every tag only Pydantic AI writes carries the reserved `pyai:` prefix; `<system>` and `<assistant_thinking>` keep their plain names. So a plain `<context>` or `<tool_result>` tag, which applications commonly put their own documents and tool output in, is ordinary text: it gets no note and no announcement.

Nothing the user, a tool or a file wrote is rewritten to make room for these frames: prompts, uploaded files, tool results and the content of frames go out byte for byte, so a model asked to edit an XML file that contains a `<system>` tag writes back the tag, not an escaped copy of it. Text that resembles one of the application’s voice tags (an opening or closing `<system>`, `<pyai:context>` or `<pyai:context_diff>` tag in any case or spacing, also when hidden behind invisible characters, look-alike letters or an HTML-entity-encoded `<`) instead gets a short note in the application’s voice next to the item it’s in, saying the text was written by the user, the tool, the model or the file’s author and is part of that item, not instructions. The same goes for a compaction summary, for the text retry feedback quotes, not for the fence around it, and for another model’s reasoning sent as `<assistant_thinking>`, whose note ends the request before that reply so the cached prefix doesn’t move, or goes in the next request when no request comes right before the reply. The same goes for text in a [capability part](#capability-parts)’s content that opens or closes the part’s own tag: the note says the tag is its author’s and doesn’t open or close the application’s element. The note is a mid-conversation system message, or a `<system>` block on models without one, and goes after a request’s tool results, unless the model has no mid-conversation system messages and the provider takes the note ahead of them. A copy of one of the framework’s data frames (`<pyai:tool_result>`, `<pyai:retry_feedback>`, `<pyai:validation_errors>`, `<pyai:conversation_summary>` or `<assistant_thinking>`) gets a note too, saying the item’s author wrote it and it opens or closes no element the application sent. A closing tag alone counts as well, for these and for the voice tags, so text that quotes one can’t end the frame around it unnoticed. A note on a tool result names the tool and the call, and a note on a `<pyai:context>` or `<pyai:context_diff>` lookalike first says that only the elements the application sends change the instructions. A note on a tool result or a file also says that the application’s own messages still apply, and names the application’s own system message when the same request has one (unless the user’s text in it has a lookalike too). On models without mid-conversation system messages, the request’s own `<system>` blocks go ahead of a note and the text it describes, so they still read as the application’s.

The model is told what these notes mean, and that other tags in a user message, such as an application’s own reminders, keep their usual meaning: in the system prompt on models without mid-conversation system messages, as described above, and elsewhere in a mid-conversation system message the first time the conversation has a frame or a note. By default, a conversation that never has either gets nothing, except on Claude Sonnet 4.6 and gpt-oss; see [When the announcement is sent](#when-the-announcement-is-sent). A judge or summarizer that reads the conversation as a flattened transcript, such as a Pydantic AI Harness judge or compaction summarizer, gets neither the announcement nor notes: it isn’t talking to the transcript’s authors.

A [realtime session](https://pydantic.dev/docs/ai/realtime/overview/) has neither these notes nor the announcement: on the live channel, text that resembles a frame goes out as written with nothing said about it. A capability part’s body still has the note saying who wrote it, and in a body from a source with less than operator authority every framing tag, `<system>` included, is neutralized as `&lt;` on the live channel, since nothing there could say whose the tag is. The stored part keeps the body as written.

### Request-scoped system prompts

Some instructions are only true for the model request they’re sent with: the budget left right now, a nudge against instruction fade. Give such a [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart) [`scope='request'`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart.scope). The model sees a request-scoped prompt only in the model request it’s part of: the next request, even the next step of the same run, no longer shows it.

That suits a value that changes from one request to the next and is sent with every request, so each request shows the current value and none of the stale ones. A capability does this from `before_model_request`, with a [capability part](https://pydantic.dev/docs/ai/capabilities/custom/#capability-parts) in the system voice. Content enqueued there goes into the request being prepared and into the message history, as a `ModelRequest` of its own:

request\_scoped\_reminder\_capability.py

```python
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, InstructionCapabilityPart, OperatorSource, OperatorText, RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.models import ModelRequestContext

@dataclass(kw_only=True)
class RequestsLeftPart(InstructionCapabilityPart, namespace='requests_left'):
    pass

@dataclass
class ShowRequestsLeft(AbstractCapability[Any]):
    async def before_model_request(
        self, ctx: RunContext[Any], request_context: ModelRequestContext
    ) -> ModelRequestContext:
        limit = ctx.usage_limits.request_limit if ctx.usage_limits else None
        if limit is not None:
            left = limit - ctx.usage.requests
            ctx.enqueue(
                RequestsLeftPart(
                    content=OperatorText(f'{left} model request(s) left in this run.'),
                    source=OperatorSource(),
                    scope='request',
                )
            )
        return request_context

agent = Agent('anthropic:claude-opus-5-5', capabilities=[ShowRequestsLeft()])
```

[Wrapping up before the request limit](https://pydantic.dev/docs/ai/core-concepts/agent/#wrapping-up-before-the-request-limit) builds this into a capability that also takes the tools away on the last request. The Harness [System Reminders](https://pydantic.dev/docs/ai/harness/system-reminders/) capability is built this way too.

Text the model must follow at every step belongs in the agent’s [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions), which every request sends. A request-scoped reminder can restate it at the end of a request, against instruction fade, but doesn’t replace it. And something the model must still act on after the next request needs the default `scope='conversation'`, or it’s gone by the time it matters. A note that the user can’t see a tool’s output has to hold until the final answer, and the model may call more tools before it gives one, so record the note as a lasting system prompt, or put it in the tool’s return value:

lasting\_system\_prompt.py

```python
from pydantic_ai import Agent, RunContext, SystemPromptPart

agent = Agent('anthropic:claude-opus-5-5')

@agent.tool
def run_tests(ctx: RunContext) -> str:
    ctx.enqueue(
        SystemPromptPart(
            "The user can't see the output of `run_tests`. "
            'Summarize its failures in your final answer.'
        )
    )
    return '3 failed, 41 passed'
```

A request-scoped prompt is not a request-only change: the prompt stays in history and only what the model is shown changes, while a request-only change, such as assigning `request_context.messages`, never reaches history at all. So don’t add it to `request_context.messages` alone: it then never enters the history, so the next request doesn’t send it, and on a model that ties its reasoning to the exact conversation, dropping it from one request to the next counts as editing the conversation. See [Changing what the model sees](https://pydantic.dev/docs/ai/capabilities/custom/#steering-messages-and-reminders) for the other ways a capability can change what’s sent, and what each does to the prompt cache.

A request-scoped prompt stays in the message history like any other part, so the history records what each request was sent. How it reaches the model depends on the provider:

- Where the API can keep it in the conversation and stop showing it to the model itself, every request-scoped prompt is sent unchanged with every request, and costs nothing once its request has been answered. [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/#turn-scoped-system-messages) supports this on the models that take mid-conversation system messages. Sending it unchanged is what keeps the cached prefix valid, and on models that tie their reasoning to the exact conversation it was produced in, it keeps that reasoning valid as well: removing an instruction from a later request counts as editing the conversation. The API stops showing it at the next user message, so one followed by a request with none, such as a retry for a response that held nothing usable, is left out of that request and every later one instead.
- Everywhere else, it’s sent with its own request and left out of every later one. It goes at the end of that request and renders like any other [mid-conversation system prompt](#mid-conversation-system-prompts).

A model request span’s `gen_ai.input.messages` in [traces](https://pydantic.dev/docs/ai/integrations/logfire/) records the messages that request was sent. Where every request-scoped prompt is sent again, a later request’s span adds `"visible": false` to the part of each one whose request has already been answered, since the model no longer sees it. Everywhere else, it isn’t in a later span at all.

With server-side conversation state, each request sends only the messages after the last response, and the provider replays everything it was sent before. How that combines with a request-scoped prompt depends on the setting:

- With OpenAI Responses’ `openai_previous_response_id`, a response is only [continued from](https://pydantic.dev/docs/ai/models/openai/#referencing-earlier-responses) while the messages before it are unchanged. Leaving a request-scoped prompt out of the next request changes them, so that request sends the full history without `previous_response_id`, and the model sees the prompt only in its own request. Using one gives up chaining for the request after it.
- With `openai_conversation_id`, the conversation keeps every message it was sent. A request-scoped prompt it was sent once stays visible to the model on every later request, and leaving it out of a later request changes nothing.

With either rendering, the cache breakpoints Pydantic AI places for you, through settings like `anthropic_cache_messages`, land before it, so the next request can still read what was cached. A request and any continuation of it (such as an Anthropic `pause_turn`) count as the same request, and so does a retry or [fallback](https://pydantic.dev/docs/ai/models/overview/#fallback-model) attempt at it. A request-scoped prompt in a request that never gets a response, because the run failed or was cancelled, is removed from the history when the run gives up on that request, so it doesn’t carry into the next one.

Use a request-scoped prompt for something about the current moment. Something that stays true belongs in the agent’s [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions) or a regular mid-conversation system prompt, and the same rule about untrusted content applies to both. For instructions whose text changes over the conversation, [`on_change='append'`](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes) delivers each change this way for you, keeping the instruction prefix cached; [keep untrusted text out of instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#untrusted-instruction-text).

### Capability parts

A [`CapabilityPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityPart) is something a capability or your application tells the model mid-conversation, defined as a subclass per kind of record: of [`DataCapabilityPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.DataCapabilityPart) for data in a frame on the user channel, or [`InstructionCapabilityPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.InstructionCapabilityPart) for the application’s voice. See [Telling the model things mid-conversation](https://pydantic.dev/docs/ai/capabilities/custom/#capability-parts) for how to define one.

In the message history it stays the part it was enqueued as, so code that reads the history, such as a history processor, a compaction summarizer or a UI, finds it by type and never mistakes it for something the user said. It’s rendered into the parts above only on the way to the model, in [`prepare_messages`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model.prepare_messages), which every model calls before it maps the history, so a [custom model](https://pydantic.dev/docs/ai/models/overview/#custom-models)’s adapter only ever gets the request parts it already maps. An override of `prepare_messages` sees the typed parts before calling the base implementation. A [`Model.request`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model.request) call made outside an agent run calls `prepare_messages` too; a model that maps a capability part it never rendered raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError).

The part’s [source](https://pydantic.dev/docs/ai/capabilities/custom/#where-the-content-came-from) decides how it’s rendered: in the application’s voice, in the user’s turn labelled as attached on the user’s behalf, or as data in a tag with a note naming who wrote it.

Rendering reads only the part’s content, the declared attributes and the [rendering facts](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityPart.rendering) stored with it, so the same history renders to the same bytes on every request, in every process, and after a round trip through [`ModelMessagesTypeAdapter`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelMessagesTypeAdapter), which keeps the prompt cache warm. History from a client is another matter: the [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/) never send capability parts to a frontend, and [`sanitize_messages`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.sanitize_messages) drops any a client sends.

### Identifying system prompts

Code that adds a system prompt sometimes needs to find it again: to add a note only once, to count the reminders it has sent, to replace a note it wrote earlier, or to tell its own records apart from prompts that came from somewhere else. Give the [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart) a [`metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart.metadata) dictionary and identify it by that, never by its visible text:

system\_prompt\_metadata.py

```python
from pydantic_ai import Agent, ModelMessage, ModelRequest, RunContext, SystemPromptPart

ORIGIN = 'my_app.hidden_test_output'

def has_note(messages: list[ModelMessage]) -> bool:
    return any(
        isinstance(part, SystemPromptPart)
        and part.metadata is not None
        and part.metadata.get('origin') == ORIGIN
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
    )

agent = Agent('anthropic:claude-opus-5-5')

@agent.tool
def run_tests(ctx: RunContext) -> str:
    if not has_note(ctx.messages):  # (1)
        ctx.enqueue(
            SystemPromptPart(
                "The user can't see the output of `run_tests`. "
                'Summarize its failures in your final answer.',
                metadata={'origin': ORIGIN},
            )
        )
    return '3 failed, 41 passed'
```

The note is a lasting system prompt, as in [Request-scoped system prompts](#request-scoped-system-prompts), so one copy covers every later call: adding it only when the history doesn't hold it yet keeps a second call from adding another.

The metadata is never sent to the model, so it doesn’t change the request or the prompt cache. It stays with the part wherever the part goes: into [`all_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.all_messages), through [`ModelMessagesTypeAdapter`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelMessagesTypeAdapter), and into a continued conversation. [`ModelRequest.metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.metadata) is no substitute: Pydantic AI merges consecutive requests in the history a run starts with and in each request it prepares, and a merged request keeps only Pydantic AI’s own metadata. Visible text is no substitute either: the wording changes, and a user can type the same words.

Like other application-only fields, the metadata doesn’t survive a round trip through the [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/), whose wire formats have no place for it. A system prompt that comes back from a frontend has no metadata.

### Making histories provider-valid

Model providers reject a request whose message history has broken tool-call/tool-result pairing — a tool call with no result, or a result with no call. A run that is cancelled or crashes partway through can leave the history in exactly this state, and so can a hand-built, truncated, or context-evicted history. You don’t need to clean these up yourself: before each model request, Pydantic AI repairs the history it was given so the provider accepts it.

Tool additions are stored as [`ToolAvailabilityDeltaPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolAvailabilityDeltaPart) request parts; tool removal is not represented. A tool returning \[`ToolReturn(tools=[...])`\]\[pydantic\_ai.messages.ToolReturn\] authors the part immediately after its [`ToolReturnPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturnPart) in the same request, with the call’s `tool_call_id` as a causal link. The executor deduplicates names in first-occurrence order and omits names already revealed. Replaying history keeps each `added` name revealed; tool definitions continue to come from the current run, so unknown or already-visible names have no effect when rendering a request.

An [on-demand capability loaded from code](https://pydantic.dev/docs/ai/capabilities/on-demand/#loading-from-code) is recorded the same way, as a [`CapabilityLoadDeltaPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityLoadDeltaPart) on the request it takes effect on, after the return of the tool call that loaded it, if any. The model never sees it.

Changes to recorded model settings, today the thinking effort, are stored the same way, as [`ModelSettingsDeltaPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelSettingsDeltaPart) request parts at the end of the request they apply to; see [Changing effort mid-conversation](https://pydantic.dev/docs/ai/capabilities/thinking/#changing-effort-mid-conversation).

The guiding rule is to adapt the history to what the provider accepts without ever discarding something you meant to send. Repairs only **add** synthesized parts or **remove** parts that are fundamentally unsendable (no provider could accept them); nothing meaningful is silently dropped. Concretely, before each request Pydantic AI:

- **Adds** a synthesized [`ToolReturnPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturnPart) for a tool call that has no result, telling the model the call was interrupted before a result was produced. It has [`outcome='interrupted'`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BaseToolReturnPart.outcome) — a neutral outcome that (unlike `'failed'` and `'retried'`) is not surfaced as a provider error — and carries `{'pydantic_ai_synthesized_tool_return': True}` in its [`metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BaseToolReturnPart.metadata) so your code can tell it apart from real tool results. This also covers a call whose arguments were cut off mid-stream: the call is kept as-is and closed out the same way. Its arguments stay verbatim in the history, but the request serializers send them as `{"INVALID_JSON": "<raw args>"}` (see [`args_as_json_str`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BaseToolCallPart.args_as_json_str)) so that a provider requiring an object still accepts the request.
- **Removes** an orphaned tool result — a [`ToolReturnPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturnPart) (whatever its `outcome`) or a legacy tool-bound [`RetryPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.RetryPromptPart) whose tool call is absent from the history (including a result placed before its call). If this empties an interior [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest) the request is removed; if it empties the last message, an empty request is kept so the history still ends on a `ModelRequest`.

After the invalid parts are handled, consecutive compatible messages are **merged** into one (two adjacent [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest) s become a single turn, with tool results ordered ahead of user parts). This changes message boundaries but preserves all content, so processed history you inspect afterwards may have fewer messages than you passed in. The tool results answering a response are also sent in the order of the calls they answer, however the history stores them: `end_strategy='early'` stores output tool results first, and a UI client may rebuild them in the order the tools completed.

The repair is deterministic and idempotent: repairing the same history always produces the same output, running a repaired history through another run leaves it untouched, and synthesized parts contain no wall-clock data, so reuse doesn’t invalidate provider prompt caches.

Tool calls that can still receive a real result are left alone: when the history ends on a `ModelResponse` with tool calls, running without a new `user_prompt` executes them, and [deferred tool calls](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) are matched to their `deferred_tool_results` — including when a ‘complete’ `ModelRequest` with the already-executed results follows the response. Repair of that live frontier only happens when the interruption is evident: a trailing request with [`state='interrupted'`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.state) (e.g. from a crash during tool execution), whose response’s unanswered calls will never be executed, or a final response with [`state='interrupted'`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.state) (e.g. from a [cancelled stream](https://pydantic.dev/docs/ai/core-concepts/output/#cancelling-streams), or one that crossed a token or cost [usage limit](https://pydantic.dev/docs/ai/core-concepts/agent/#usage-limits)) followed by a new user prompt. Without a new prompt, a run executes an interrupted final response’s tool calls like any other.

The one case the repair leaves to you is a new user prompt on top of a history whose final response, not marked `state='interrupted'`, still has unanswered tool calls: those calls can still be answered — by resuming the run, or with `deferred_tool_results` — so Pydantic AI raises rather than abandon them. When you do mean to abandon them, [`repair_messages`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.repair_messages) runs the same pipeline on demand and closes them out:

repairing\_a\_stored\_history.py

```python
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    ToolCallPart,
    ToolReturnPart,
    repair_messages,
)

stored: list[ModelMessage] = [
    ModelResponse(parts=[ToolCallPart('get_weather', {'city': 'Mexico City'}, tool_call_id='c1')])
]

runnable = repair_messages(stored)
closed_out = runnable[-1].parts[-1]
assert isinstance(closed_out, ToolReturnPart)
print(closed_out.content)
#> The tool call was interrupted before a result was produced.
```

`runnable` can now be passed as `message_history=` alongside a new prompt. It is also what to reach for outside a run — in a store, a UI, or a capability that wants to record a history it knows a later run can pick up. Pass `repair_last_response=False` to leave the live frontier alone and repair only the rest.

This pipeline handles regular, locally-executed tool calls only. Provider-native tool parts — produced and resolved by the provider inline — are left untouched and repaired by each model’s own serializer instead. Some other provider-invalid histories are also out of scope and may be rejected: duplicate tool results for one call, and provider-specific ordering rules beyond call/result pairing — where one of those rules is known and verified, the model’s own serializer normalizes the request for it instead.

### Special tokens in content

Open-weight models mark their turns with special tokens in a chat template, such as `<|im_start|>`, `<|eot_id|>` or `[INST]`. Many hosts of these models also encode those characters as the real control token when they find them in message content. Text from a tool, a file or a user can then close the current turn and open a new one in any role, and a note beside the text can’t help, because it sits in a turn the forged one has already closed. Which hosts do this depends on the host and the model, not only on the model family, and a routing service can pick a different host per request.

So on routes that can reach such a host, Pydantic AI puts a zero-width joiner (U+200D) inside each of these tokens before sending, so `<|im_start|>` goes out as `<\u200d|im_start|>` and reaches the model as ordinary text. This is the exception to sending your content as written, and it’s limited to this one character:

- **What goes out with the joiner:** user prompts, tool results, inlined text files, retry feedback, summaries sent as user text, and the model’s own text, tool names, tool call arguments and reasoning when they’re sent back in later requests, unless the reasoning goes back to the provider that signed it. Text without a special token goes out unchanged.
- **What doesn’t:** the message history you store, system prompts, instructions and tool definitions. A file or URL a provider fetches itself isn’t changed either. Tool definitions tokenize on these hosts too, so a tool description from an MCP server you don’t trust is not protected by this.
- **Prompt cache:** the same text always gets the same joiners, so resending a history sends the same bytes.

The flag is [`may_tokenize_special_tokens_in_content`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.may_tokenize_special_tokens_in_content). It’s on for self-hosted servers ([vLLM](https://pydantic.dev/docs/ai/models/compatible-apis/#vllm), [Ollama](https://pydantic.dev/docs/ai/models/ollama/), [Hugging Face](https://pydantic.dev/docs/ai/models/huggingface/)), for most hosts of open-weight models, and for routing services and [`OpenAICompatibleProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai_compatible.OpenAICompatibleProvider) for every model that isn’t only available from its own lab, such as Claude, GPT or Gemini. [`AzureProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.azure.AzureProvider) and [`OpenAIProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider) are treated like routing services, since a custom deployment name or base URL can serve anything: a name that isn’t one of those labs’ own gets the flag, including a custom Azure deployment of a GPT model. It’s off for those labs’ own APIs and for hosts that have sent these tokens as text wherever we’ve checked. To change it for a model, use `profile=`, as below.

The model reads the joiner as part of the text and copies it into what it writes, or writes another invisible character for it, so Pydantic AI removes any zero-width character inside these tokens in each response, on the same routes. Your tools, your output validators, your users and the stored history get `<|im_start|>`, streamed or not, including when a token is split across stream chunks. When that text goes back in a later request, the joiner is put back, so the model gets the bytes it wrote. An agent that reads a chat template and writes it back therefore writes the real tokens.

This has two consequences you can observe:

- **Tool call arguments and response text can differ from the model’s raw output in this one way.** That’s the only change Pydantic AI makes to them. Reasoning and the provider’s own tool calls stay as the model wrote them.
- **A file that deliberately contains a broken token gets repaired** if the model copies it: `<\u200d|im_start|>` in a file is indistinguishable from a token Pydantic AI broke, so what the tool receives is `<|im_start|>`. A zero-width character anywhere else, such as in an emoji sequence, stays as it is.

Breaking the token only stops the host from creating a turn boundary. A model can still follow text written to look like a turn, and some do, which no change to these characters can prevent: in measurements on routes that tokenize, breaking the token stopped forged turns from being followed on most runs of Qwen 3.8, GLM 5 and DeepSeek V4 Flash, and made no measurable difference on DeepSeek V4 Pro, Qwen3 Next, Llama 3.3 and gpt-oss.

To send these tokens as written, turn the flag off for that model, which also stops the removal from responses:

turn\_off\_special\_token\_breaking.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

model = OpenRouterModel(
    'qwen/qwen3.8-27b',
    profile={'may_tokenize_special_tokens_in_content': False},
)
agent = Agent(model)
```

Only do this when you trust that text, or when you’ve pinned a host that treats these tokens as text. On a host that tokenizes them, the text can then forge a turn, and the model usually can’t copy the tokens at all, since it never sees them as text.

### Correlating runs with run\_id and conversation\_id

Each `ModelRequest` and `ModelResponse` carries two identifiers:

- [`run_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.run_id) — unique per agent run. Also available as [`RunContext.run_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.run_id) and [`AgentRunResult.run_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.run_id), and emitted on the OpenTelemetry agent run span as `gen_ai.agent.call.id`.
- [`conversation_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.conversation_id) — shared across all runs that build on the same `message_history`. Also available as [`AgentRunResult.conversation_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.conversation_id), and emitted as `gen_ai.conversation.id`.

A fresh `run_id` is generated for every agent run (or you can pass `run_id='<your-id>'` to use an ID minted by your application — e.g. one created, stored, or handed out to a client before the run starts). Unlike `conversation_id`, `run_id` is **never** inherited from `message_history`. Each [`Agent.run`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run) call — including a [deferred-tool resume](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) — is a separate run with its own `run_id`. Passing an empty `run_id=''`, or a `run_id` that already appears on `message_history`, raises [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError), because both break [`new_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.new_messages) boundary detection. Correlate pause/resume or multi-turn work with `conversation_id` instead. When retrying a failed run with the same `run_id`, rebuild `message_history` without the failed attempt’s messages.

A fresh `conversation_id` is generated on the first run, stamped onto every message produced by that run, and inherited by subsequent runs that pass the messages back via `message_history`. This means you can correlate traces from a multi-turn conversation in [Logfire](https://pydantic.dev/docs/ai/integrations/logfire/) (or any OpenTelemetry backend) without tracking anything yourself — as long as the message history round-trips, the conversation ID does too.

conversation\_id is shared across runs in the same conversation

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')

result1 = agent.run_sync('Tell me a joke.')
result2 = agent.run_sync('Explain?', message_history=result1.all_messages())

assert result1.conversation_id == result2.conversation_id
assert result1.run_id != result2.run_id
```

pass a pre-minted run\_id

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agent = Agent(TestModel())

result = agent.run_sync('Tell me a joke.', run_id='run-from-api-42')
assert result.run_id == 'run-from-api-42'
```

To override or fork `conversation_id`:

- Pass `conversation_id='<your-id>'` to use an ID from your own application (e.g. a chat thread ID stored in your database).
- Pass `conversation_id='new'` to start a fresh conversation that ignores any `conversation_id` already on `message_history` — useful for branching off an existing thread without making the caller generate an ID.

forking a conversation

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')

result1 = agent.run_sync('Tell me a joke.')
forked = agent.run_sync(
    'Tell me a different joke.',
    message_history=result1.all_messages(),
    conversation_id='new',
)

assert forked.conversation_id != result1.conversation_id
```

The [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/) auto-populate `conversation_id` from the protocol’s own thread/chat ID, so frontends using these protocols get conversation correlation for free. Protocol-level run IDs (for example AG-UI’s `runId`) are **not** mapped into the agent’s `run_id` — pass `run_id=` explicitly on `AGUIAdapter.run_stream` / `dispatch_request` (or a plain `Agent.run`) if you need them to match.

### Which model answered

Each `ModelResponse` the agent gets from a model request records the model it sent the request to as [`model_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.model_id): the string the model was selected by, like `'openai:gpt-6.1-sol'` or an alias a capability resolved, or otherwise the model’s own `model_id`. That’s the model as you configured it, while [`model_name`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.model_name) is what the provider reported, often a dated version, and the same for two configurations of one model. When a capability moves a request to another model, such as a [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) candidate, the response records that model, so a later run continuing the history can tell which of your models answered and send a request back to it.

## Storing and loading messages (to JSON)

While maintaining conversation state in memory is enough for many applications, often times you may want to store the messages history of an agent run on disk or in a database. This might be for evals, for sharing data between Python and JavaScript/TypeScript, or any number of other use cases.

The intended way to do this is using a `TypeAdapter`.

We export [`ModelMessagesTypeAdapter`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelMessagesTypeAdapter) that can be used for this, or you can create your own.

To store a conversation you mean to continue, store its [`Conversation`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.Conversation) rather than its messages alone, with [`ConversationTypeAdapter`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.ConversationTypeAdapter) or as a field on a model of your own: it serializes its messages the same way, and keeps the usage, conversation ID and deferred tool requests that the messages don’t. See [Persistence](https://pydantic.dev/docs/ai/core-concepts/persistence/#storing-a-conversation-yourself).

Here’s an example showing how:

serialize messages to json

```python
from pydantic_core import to_jsonable_python

from pydantic_ai import (
    Agent,
    ModelMessagesTypeAdapter,  # (1)
)

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
history_step_1 = result1.all_messages()
as_python_objects = to_jsonable_python(history_step_1)  # (2)
same_history_as_step_1 = ModelMessagesTypeAdapter.validate_python(as_python_objects)

result2 = agent.run_sync(  # (3)
    'Tell me a different joke.', message_history=same_history_as_step_1
)
```

Alternatively, you can create a `TypeAdapter` from scratch:

```python
from pydantic import TypeAdapter
from pydantic_ai import ModelMessage
ModelMessagesTypeAdapter = TypeAdapter(list[ModelMessage])
```

Alternatively you can serialize to/from JSON directly:

```python
from pydantic_core import to_json
...
as_json_objects = to_json(history_step_1)
same_history_as_step_1 = ModelMessagesTypeAdapter.validate_json(as_json_objects)
```

You can now continue the conversation with history `same_history_as_step_1` despite creating a new agent run.

*(This example is complete, it can be run “as is”)*

### Storing complete run results

An [`AgentRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult) can be stored directly as a field on a Pydantic model:

serialize a run result to json

```python
from pydantic import BaseModel

from pydantic_ai import Agent, AgentRunResult

class StoredRun(BaseModel):
    result: AgentRunResult[str]

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')
result = agent.run_sync('Tell me a joke.')

stored_json = StoredRun(result=result).model_dump_json()
loaded = StoredRun.model_validate_json(stored_json)

assert loaded.result.output == result.output
assert loaded.result.all_messages() == result.all_messages()
```

The round-trip preserves the output, messages and new-message boundary, output tool name, usage, run and conversation IDs, metadata, and trace context. Run-local state used only while the agent is executing is not stored.

A [`StreamedRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult) reads its values off the stream that is producing them, so it lasts only as long as that stream. Once the stream has finished, take [`StreamedRunResult.result`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.result) to get the same run in settled form and store that:

store a streamed run

```python
async with agent.run_stream('Tell me a joke.') as streamed:
    async for text in streamed.stream_text():
        print(text)

    stored_json = StoredRun(result=streamed.result).model_dump_json()
```

### Loading untrusted history

The `message_history` parameter is trusted server-side state. If you load history that came from a browser request or another untrusted boundary, sanitize it before passing it to the agent.

[`sanitize_messages`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.sanitize_messages) applies the same default message sanitization used by the [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/): it strips client-supplied system prompts and request-level [`instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.instructions), pins client-returned retry feedback to the voice its cause allows, drops non-HTTP file URL schemes, resets non-allowlisted [`FileUrl.force_download`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.FileUrl.force_download) values to `False`, drops uploaded file references, resets [workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/) references so a client can’t point your agent at another environment, resets [`ModelResponse.model_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.model_id) so a client can’t pick which of your models a request is routed back to, drops [`TextContent.metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.TextContent.metadata) from user prompts and tool return content so a client can’t pass its text off as content your application or a capability added, drops the framework-reserved `__pydantic_ai__` key from message [`metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.metadata) (keeping your own keys) so a client can’t set state Pydantic AI and its capabilities act on, and removes unresolved tool calls at the end of the history.

`strip_system_prompts` strips [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart) s, and keeps the [`RetryFeedbackPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.RetryFeedbackPart) s that carry Pydantic AI’s own [retry feedback](https://pydantic.dev/docs/ai/core-concepts/retries/#feedback-that-belongs-to-no-tool-call), so the model still sees why it corrected itself. The client picks a submitted feedback part’s cause, so what the part may say is pinned to that cause: `'validation_error'` and `'model_retry'` feedback reach the model in the user voice, fenced behind a line attributing it to the application, which a client could write as plain user text anyway. `'no_output'` is the one cause in the system voice, and a client can forge the part as easily as a system prompt, so a client-submitted one is demoted to the same fenced, attributed user text, whatever it says. A tool-less legacy [`RetryPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.RetryPromptPart) is translated into the feedback part it always meant and takes the same rule. If stripping empties a `ModelRequest`, the request is dropped from the history entirely.

Client-supplied [`CompactionPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CompactionPart) s are kept, so the conversation stays [compacted](https://pydantic.dev/docs/ai/capabilities/compaction/) — but they are never trusted to stand in for the system prompt. Whether that prompt is a [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart) already in the history or one re-injected by [`ReinjectSystemPrompt`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ReinjectSystemPrompt), it is re-sent to the model even where a provider’s own compaction state would normally let it be skipped. If you combine the sanitized history with trusted server-side `message_history`, also pass `strip_compaction_parts=True`: everything before a compaction item is hidden from the model, so a client-supplied one would hide the server’s history — see [Client-held history](https://pydantic.dev/docs/ai/capabilities/compaction/#client-held-history). The [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/) apply this rule automatically when a run combines server-side `message_history` with client-submitted messages.

sanitize untrusted message history

```python
from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_ai.messages import sanitize_messages

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

# `request_json` is the body submitted by an untrusted client.
loaded_history = ModelMessagesTypeAdapter.validate_python(request_json['message_history'])
message_history = sanitize_messages(loaded_history)

result = agent.run_sync('Tell me a different joke.', message_history=message_history)
```

Most of these sanitizations can be turned off individually when the corresponding parts were created by trusted server-side code: pass `strip_system_prompts=False` to keep both the system prompts and the retry feedback, `strip_instructions=False` to keep request-level instructions, add schemes to `allowed_file_url_schemes`, add values to `allowed_file_url_force_download`, set `allow_uploaded_files=True`, or set `strip_workspace_refs=False`. The others can’t: [`TextContent.metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.TextContent.metadata) is always dropped from user prompts and tool return content, `model_id` is always reset on responses, and the framework-reserved `__pydantic_ai__` metadata key from every message, so pass history that should keep them as trusted server-side `message_history` instead. To continue client-supplied history in the same workspace, pass a reference you saved server-side as `workspace=` (see [Continuing in the same workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/#continuing-in-the-same-workspace)). See [file URL input security](https://pydantic.dev/docs/ai/core-concepts/input/#user-side-download-vs-direct-file-url) for the file input trust model.

`sanitize_messages` keeps, as sent, the references to state the model provider holds: [`ModelResponse.provider_response_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.provider_response_id), the `conversation_id` and `container_id` keys of [`ModelResponse.provider_details`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.provider_details), and [`ModelResponse.state`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.state). The UI adapters’ protocols don’t carry these, so history an adapter loads has none, but history you load yourself keeps whatever the client sent. These provider-generated IDs are enough on their own to reach the state they name, and the settings and the resume path below do so with your provider credentials. An ID a client sends is not proof that it owns that state (see the [threat model](https://github.com/pydantic/pydantic-ai/blob/main/THREAT_MODEL.md#persistent-state-and-tenant-identity)), so with client-held history, save the references you need on your server, bound to the user they belong to, and set each of these as follows:

- [`openai_conversation_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id): pass a concrete ID you saved, not `'auto'`.
- [`anthropic_container`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_container): pass a container ID you saved, or `False` for a fresh container, rather than relying on its default reuse of the latest container in the history.
- [`openai_previous_response_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id): don’t use it, as a response ID in the history can take precedence even over a concrete one. With `openai_transport='websocket'`, where it defaults to `'auto'`, pass a concrete `openai_conversation_id` instead to turn it off.
- [`openai_prompt_cache_diagnostics`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_prompt_cache_diagnostics): set it to `False`. It is on by default for models that support it, and sends the latest response ID in the history to compare the new request against.
- [`anthropic_cache_diagnostics`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_diagnostics): leave it off, its default; it does the same with the latest Anthropic response.
- A history that ends in a response with `state='suspended'`: don’t accept one from a client. A run without a new prompt resumes it, fetching the stored response or batch result it names, and no setting turns this off, so resume suspended runs only from server-side history.

## Persisting sessions

[Serializing a history](#storing-and-loading-messages-to-json) turns it into bytes and back, but that is only the primitive. Deciding where those bytes live, which conversation they belong to, and when to reload them is left to your application, and [Persistence](https://pydantic.dev/docs/ai/core-concepts/persistence/) lays out the choice, including the cases a stored history doesn’t answer. [`conversation_id`](#correlating-runs-with-run_id-and-conversation_id) is the key to store them under: pass your own chat thread ID, or let Pydantic AI resolve one, and read the resolved value back off the result as [`AgentRunResult.conversation_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.conversation_id).

### Carrying a conversation whole

A history is not quite everything a conversation carries. [`usage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) and the [`conversation_id`](#correlating-runs-with-run_id-and-conversation_id) travel alongside it, and so do the [deferred tool requests](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#pausing-a-conversation) of a run that paused, which the messages show as unanswered calls without saying what answer each needs. Passed one argument at a time, a conversation reassembled by hand tends to lose them one at a time. Losing `usage` is the one that bites: pass `message_history` without it and every turn’s [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) budget starts over from zero, so a cap set across the conversation is never reached.

[`AgentRunResult.conversation`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.conversation) bundles them as a [`Conversation`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.Conversation), which serializes like any other Pydantic value, so the whole thing can be stored under one key and handed back intact:

carry a conversation between runs

```python
from pydantic_ai import Agent, Conversation

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

conversation: Conversation = agent.run_sync('Tell me a joke.').conversation
print(len(conversation.messages))
#> 2
print(conversation.usage.requests)
#> 1
print(conversation.conversation_id == conversation.messages[-1].conversation_id)
#> True
```

*(This example is complete, it can be run “as is”)*

Hand it to the next run as `conversation=`, in place of `message_history`, `usage` and `conversation_id`, and all three carry together:

continue a conversation

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

first = agent.run_sync('Tell me a joke.')
second = agent.run_sync('Explain?', conversation=first.conversation)
print(second.usage.requests)
#> 2
print(second.conversation_id == first.conversation_id)
#> True
```

*(This example is complete, it can be run “as is”)*

`conversation=` stands in for the three arguments it carries, so passing it alongside any of them raises [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). The run works on a copy of the conversation’s `usage`, so the same `Conversation` can be continued more than once, as a point to branch from.

A conversation loaded from a [`ConversationStore`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation-store/#pydantic_ai.conversation_store.ConversationStore) also carries its [`revision`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.Conversation.revision), which a run passes through to its result, so saving the result back can tell whether someone else saved the conversation in the meantime. It also carries its [`new_message_index`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.Conversation.new_message_index), which a run moves to where the messages it added start, so saving the result appends just those, even when a [history processor](#processing-message-history) trimmed the history the run was sent.

[`agent.realtime()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.realtime) takes `conversation=` too, and a [realtime session](https://pydantic.dev/docs/ai/api/pydantic-ai/realtime/#pydantic_ai.realtime.RealtimeSession) exposes the same bundle as [`conversation`](https://pydantic.dev/docs/ai/api/pydantic-ai/realtime/#pydantic_ai.realtime.RealtimeSession.conversation), so a conversation can move between text and speech in either direction without losing its running total.

For a chat application that is usually the whole design: load a thread’s conversation, pass it as `conversation=`, and store the result’s `conversation` back once the run finishes, with [`ConversationTypeAdapter`](https://pydantic.dev/docs/ai/api/pydantic-ai/conversation/#pydantic_ai.conversation.ConversationTypeAdapter) or as a field on a model of your own. For a long thread, store the messages separately and append each run’s [`new_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.new_messages) instead of rewriting them, which keeps each write proportional to the turn rather than to the conversation; [Persistence](https://pydantic.dev/docs/ai/core-concepts/persistence/#storing-a-conversation-yourself) covers both.

To keep that history in your database with each message stored once, conflicting saves caught, and forking built in, implement a [`ConversationStore`](https://pydantic.dev/docs/ai/core-concepts/persistence/#using-a-conversation-store) on its five storage primitives. A [UI adapter](https://pydantic.dev/docs/ai/integrations/ui/overview/#saving-to-a-conversation-store) given one makes the load and save calls for you.

[Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/) adds capabilities that keep more than the conversation:

| Capability | What it stores | Scoped by |
| --- | --- | --- |
| [`StepPersistence`](https://pydantic.dev/docs/ai/harness/step-persistence/) | A record of each run for recovering it, not a session store: message snapshots taken at settled points in a run, alongside an event log and a tool-effect ledger, so a run that ends early can be continued or forked from its last settled point rather than restarted | `conversation_id` and `run_id` |
| [`ConversationSearch`](https://pydantic.dev/docs/ai/harness/conversation-search/) | Nothing of its own: it ranks the history `StepPersistence` already stored and gives the model a tool to pull earlier turns back into context on demand, including turns [compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) dropped | `conversation_id` |
| [`Memory`](https://pydantic.dev/docs/ai/harness/memory/) | Markdown notes the agent writes and reads itself, deliberately outliving any single conversation | A namespace you choose |

`StepPersistence` ships in-memory, file, SQLite, PostgreSQL, and MongoDB backends, and its store is a protocol you can implement against your own database.

As an alternative to holding the history yourself, some providers keep conversation state on their side and reconstruct earlier turns from it, so each request carries only what is new. On the OpenAI Responses API that is [`openai_conversation_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id), covered under [Using durable conversations](https://pydantic.dev/docs/ai/models/openai/#using-durable-conversations). Weigh it against a store of your own: it is one provider’s feature, OpenAI documents that earlier input tokens in a chain are still billed, and it is unavailable to organizations with Zero Data Retention enabled.

## Trust boundary for client-supplied history

Pydantic AI’s server-side surfaces are stateless: a run is reconstructed from the `message_history` (and any `deferred_tool_results`) supplied with the request, whether that request arrives through a [UI adapter](https://pydantic.dev/docs/ai/integrations/ui/overview/) or through an endpoint you wrote yourself. A client that can submit history can therefore fabricate it — including [`ToolCallPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolCallPart) s the model never emitted and [approvals](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) no human granted — and the server will process them as genuine, up to and including executing the tools they name.

Pydantic AI does not sign or cryptographically verify tool calls, tool results, or approvals, and neither do comparable agent frameworks: signing is only meaningful for a server that kept the run itself, and such a server doesn’t need the client’s copy of the history in the first place. The defaults described under [Loading untrusted history](#loading-untrusted-history) and in the [UI adapter trust model](https://pydantic.dev/docs/ai/integrations/ui/overview/#trust-model-for-client-submitted-messages) narrow what a fabricated history can reach; they don’t make it trustworthy.

Possession of the endpoint is therefore the authorization boundary, so design around that:

- **Authenticate and authorize at the transport layer.** Run the agent inside your own authenticated route handler, and treat every caller that gets through as able to submit any history it likes.
- **Scope the toolset to the caller.** Expose only the tools the authenticated caller is entitled to use, by [building the toolset per run](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#dynamically-building-a-toolset) or [filtering](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#filtering-tools) it against the user carried in your [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/).
- **Re-validate high-stakes effects server-side.** [Approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) guards against the *model* acting without human sign-off, not against the client. Where the stakes demand it, check the caller’s authority against server-side state inside the tool function itself, or persist paused runs server-side and resume them with your own `deferred_tool_results` instead of the client’s.
- **Don’t read prompt-level framing as proof.** Where a model API can’t carry a tool’s file in its tool result, Pydantic AI frames it as coming from that call ([Where a returned file is sent](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-return-file-provenance)), and a mid-conversation system prompt a provider can’t send natively is framed as `<system>...</system>`. Both are ordinary prompt text, and a client that can submit history can still submit system prompts of its own unless you [strip them](#loading-untrusted-history). They tell the model where content came from; they don’t attest it.

## Other ways of using messages

Since messages are defined by simple dataclasses, you can manually create and manipulate, e.g. for testing.

The message format is independent of the model used, so you can use messages in different agents, or the same agent with different models.

Provider-specific metadata is less portable than the message itself. For example, [citations](https://pydantic.dev/docs/ai/core-concepts/citations/#citations-in-message-history) are sent to a different provider as plain text, though they stay on the stored messages.

In the example below, we reuse the message from the first agent run, which uses the `openai:gpt-6.1-sol` model, in a second agent run using the `google:gemini-4-argon` model.

Reusing messages with a different model

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync(
    'Explain?',
    model='google:gemini-4-argon',
    message_history=result1.new_messages(),
)
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.

print(result2.all_messages())
"""
[
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        instructions='Be a helpful assistant.',
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.'
            )
        ],
        usage=RequestUsage(cost=Decimal('0.00023'), input_tokens=55, output_tokens=12),
        model_name='gpt-6.1-sol',
        model_id='openai:gpt-6.1-sol',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Explain?',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        instructions='Be a helpful assistant.',
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='This is an excellent joke invented by Samuel Colvin, it needs no explanation.'
            )
        ],
        usage=RequestUsage(cost=Decimal('0.000372'), input_tokens=56, output_tokens=26),
        model_name='gemini-4-argon',
        model_id='google:gemini-4-argon',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
]
"""
```

*(This example is complete, it can be run “as is”)*

### Sending history to another provider

Some of what a response holds can only be sent back to a provider that can verify it. Pydantic AI decides what to send back to each provider by two rules:

- **Server-side state** is kept by the endpoint that returned it, and looked up by ID: stored response, item, conversation and container IDs. It’s judged by endpoint: it’s only sent back to a provider with the same [`provider_name`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.provider_name) whose base URL matches the response’s [`provider_url`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.provider_url). A response without a `provider_url`, such as one built by hand, is judged by its name alone.
- **Stateless signed or encrypted data** is judged by family, and checked by the provider’s own key and format: OpenAI encrypted reasoning and compaction items, Anthropic thinking signatures and redacted thinking, Gemini thought signatures, xAI encrypted reasoning and tool results, and OpenRouter and Snowflake reasoning details. It’s sent back to a provider with the same *canonical system* (the [`canonical_system`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.Provider.canonical_system) of its provider), or one that lists it in its [`compatible_systems`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.Provider.compatible_systems).

Data that can’t be sent back gets each model’s fallback: thinking is written out as text, a foreign OpenAI compaction item is left out, and so is the history before it, which the model then gets in full, and a Gemini function call gets the documented `skip_thought_signature_validator` signature in place of a foreign one.

The canonical systems differ from the provider names where providers share a key, or where one name covers two transports:

| Provider | Canonical system |
| --- | --- |
| `openai`, `openai-codex`, and the Pydantic AI Gateway’s OpenAI route | `openai` |
| `azure`, and `OpenAIProvider` with an `AsyncAzureOpenAI` client | `azure` |
| `anthropic` with any client (Anthropic API, Bedrock, Claude Platform on AWS, Vertex AI, Foundry), Bedrock Converse with a Claude model, and the Gateway’s Anthropic route | `anthropic` |
| `bedrock`, with any other model | `bedrock` |
| `google` and `google-cloud` with a Google Cloud client, and the Gateway’s Google route | `google-cloud` |
| `google` and `google-cloud` with a Gemini API client | `google` |
| Every other provider, including `bedrock-mantle`, `openai-chatgpt`, `openrouter` and `snowflake` | its name |

So history from the Codex backend continues on the OpenAI API with its encrypted reasoning and compaction items, and Claude’s thinking moves between the Anthropic API and Bedrock with its signatures. A response records its canonical system in [`ModelResponse.canonical_system`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.canonical_system) when it differs from `provider_name`, and always when the provider’s canonical system depends on its client, as for Google providers and `OpenAIProvider`, which is how a Gemini API response and a Google Cloud one, both named `google`, are told apart: the two reject each other’s thought signatures. For a `google` response recorded before Pydantic AI stored the canonical system, its `provider_url` says which: a first-party Gemini API or Google Cloud URL decides, and any other, like a proxy’s, keeps the earlier behavior of sending the signatures to a model with the same provider name. A Bedrock Converse response from a model with OpenAI’s encrypted reasoning, like GPT-5.6, records `bedrock` too, so Claude models on Bedrock don’t take that reasoning for their own. One recorded by an earlier version has none and keeps the name-based behavior, so its reasoning is still sent to Claude models on Bedrock.

Some providers accept data they can’t use: OpenAI ignores encrypted reasoning from another organization, and Claude models with [account-bound thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#account-bound-thinking) ignore thinking from another account. Neither fails the request.

[`Model.accepts_stateless_artifacts()`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model.accepts_stateless_artifacts) tells you whether a model would send a part’s data back. A provider subclass that only changes its name, such as one that signs in differently to the same API, keeps its parent’s canonical system, except for subclasses of [`OpenAIProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider), which are assumed to talk to another service. To declare your own, override `canonical_system` or `compatible_systems` on your provider, or pass them to [`OpenAICompatibleProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai_compatible.OpenAICompatibleProvider).

The canonical system names the service a provider speaks to, whose signed data it verifies and whose provider-native features it shares, so a renamed subclass keeps both. Code that decides by service rather than by provider name reads it too, such as the [Pydantic AI Harness `Advisor`](https://pydantic.dev/docs/ai/harness/advisor/), which uses it to tell whether an executor takes Anthropic or OpenRouter advisor model IDs. It doesn’t group providers by wire protocol: `azure`, and providers like `deepseek` that speak the OpenAI API, each have their own.

So a response from an `OpenAIProvider` at one `base_url` continued at another (a different gateway, say) gets its text, function calls and encrypted reasoning sent, but not its `previous_response_id` or item IDs, which the other endpoint couldn’t look up. The base URLs are compared ignoring the case of the scheme and host, a default port and a trailing `/`. [`Model.accepts_server_state()`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model.accepts_server_state) tells you whether a model would send a response’s server-side state back; when two URLs reach the same stored state, like a proxy alias, override [`shares_server_state_with()`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.Provider.shares_server_state_with) on your provider. Files you upload yourself aren’t judged this way: an [`UploadedFile`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UploadedFile) is sent to the endpoint of whichever model you pass it to, so pass it to one that can read it.

## Sharing messages between agents

The same `message_history` parameter also works when the next run uses a different [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent). This is useful for [programmatic agent hand-off](https://pydantic.dev/docs/ai/guides/multi-agent-applications/#programmatic-agent-hand-off), where your application runs one agent, then gives another agent the conversation so far as context.

sharing\_messages\_between\_agents.py

```python
from pydantic_ai import Agent

biography_agent = Agent(
    'openai:gpt-6.1-sol',
    instructions='Answer biographical questions concisely.',
)

science_agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Answer science questions for a general audience.',
)

biography_result = biography_agent.run_sync('Who was Albert Einstein?')
print(biography_result.output)
#> Albert Einstein was a German-born theoretical physicist.

science_result = science_agent.run_sync(
    'What was his most famous equation?',
    message_history=biography_result.new_messages(),
)
print(science_result.output)
#> Albert Einstein's most famous equation is (E = mc^2).
```

*(This example is complete, it can be run “as is”)*

For more complex multi-agent patterns, see the [multi-agent applications](https://pydantic.dev/docs/ai/guides/multi-agent-applications/) documentation.

## Editing existing messages

To change the conversation mid-run, build *new* message objects rather than modifying existing ones: [inject new messages](#injecting-messages-mid-run) with `enqueue`, or prune, summarize, or otherwise rewrite the history the model receives with a [history processor](#processing-message-history). When you need to edit an earlier message — say, compacting a large tool output — copy it with [`dataclasses.replace`](https://docs.python.org/3/library/dataclasses.html#dataclasses.replace), passing a new `parts` list of new (or reused) part objects; edited parts are likewise built with `replace` rather than modified. Replacing a message in the history and reassigning its `parts` list are both safe.

## Injecting messages mid-run

Tools, capability hooks, external code driving an agent run, and code driving a realtime session can inject extra content into the conversation mid-run with [`RunContext.enqueue`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.enqueue) (when a `RunContext` is in scope, e.g. inside a tool or capability hook) or [`AgentRun.enqueue`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRun.enqueue) (from external code driving [`agent.iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.iter)), or [`RealtimeSession.enqueue`](https://pydantic.dev/docs/ai/api/pydantic-ai/realtime/#pydantic_ai.realtime.RealtimeSession.enqueue) (from external code driving a realtime session). Use this when something happens during a run that the agent should know about — a tool wants to add follow-up context, an external event needs to *steer* the agent’s plan, or background work needs to reach the agent when it completes. You can call any of these directly from synchronous or asynchronous code, including a tool or callback running in another thread. Calls after the run or session has ended raise [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). For standard runs, submission is synchronized with the final drain, so a concurrent call is either accepted for delivery or rejected as the run ends.

A `priority` controls when the enqueued content is delivered:

- `'asap'` (default): delivered at the earliest opportunity — added to the next [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest), or, if the agent would otherwise terminate before another request, used to redirect the run into one more request. Use when the new context should reach the model as soon as possible; this is what other frameworks often call **steering** an in-flight agent.
- `'when_idle'`: delivered only when the agent would otherwise terminate, after any `'asap'` messages. Use when the agent shouldn’t be interrupted but should pick up the new work — a follow-up task — once it’s done with what it’s doing.

A run that pauses for [deferred tools](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) is not redirected. Content still queued at the pause is added to the message history instead, so a resumed run sees it. This applies when the paused step’s tool results end the history. If every call in that step was deferred, the history ends with those calls, so the queued content redirects the run as usual, and so does content that includes a [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse). With [`run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream), the streamed result’s messages don’t include it.

`enqueue` is variadic — each positional argument is one item, and can be:

- a piece of [`UserContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UserContent) — a `str` or multi-modal content like an [`ImageUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ImageUrl). Adjacent user content is gathered into a single [`UserPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UserPromptPart), so `enqueue('caption', image)` forms one user turn. To pass an existing list, spread it: `enqueue(*items)`;
- a [`ModelRequestPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequestPart), such as a [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart);
- a complete [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest) or [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse), to control request-level fields like `instructions`/`metadata` or to inject a synthetic prior turn.

Adjacent part-style items (user content and [`ModelRequestPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequestPart) s) are coalesced into one [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest); complete messages stay separate. This lets a single call inject an interleaved exchange — for example a synthetic tool call (a [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse)) followed by its result (a [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest)). The content must end in a request, so the agent has something to respond to.

The standard-run `enqueue` methods return an `enqueue_id` (`str`) for a non-empty call, or `None` when called with no content. When the queued content is actually delivered into run history, the [event stream](https://pydantic.dev/docs/ai/core-concepts/agent/#streaming-all-events) yields an [`EnqueuedMessagesEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.EnqueuedMessagesEvent) carrying that `enqueue_id` and the delivered content, so a client can observe when its steering message took effect. The event carries the delivered message objects themselves, the same objects held in the run’s message history. Content that went into a tool call’s request (see [below](#from-inside-a-tool-or-hook)) has no message of its own in history, so `messages` holds a request of its own with the delivered parts, and `parts` holds the [`ModelRequestPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequestPart) s as they sit in history. A history processor that replaces history with new message objects does not affect the event, but [in-place mutation](#editing-existing-messages) of delivered content will be visible through it. `RealtimeSession.enqueue` also returns an `enqueue_id` or `None`; realtime delivery is documented under [enqueuing prompts](https://pydantic.dev/docs/ai/realtime/tools/#enqueuing-prompts).

### From inside a tool or hook

Use [`RunContext.enqueue`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.enqueue) when you have a `RunContext` in scope. For a capability adding steering messages or reminders from `before_model_request`, see [Changing what the model sees](https://pydantic.dev/docs/ai/capabilities/custom/#steering-messages-and-reminders):

enqueue\_from\_tool.py

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import SystemPromptPart

agent = Agent('anthropic:claude-opus-5-5')

@agent.tool
def trigger_alert(ctx: RunContext) -> str:
    ctx.enqueue('Alert: production is degraded, prioritize triage.')
    return 'alert raised'

@agent.tool
def enter_incident_mode(ctx: RunContext) -> str:
    # Enqueue a `SystemPromptPart` to adjust the agent's standing instructions mid-run.
    ctx.enqueue(SystemPromptPart(content='You are now in incident mode: be terse and action-oriented.'))
    return 'incident mode enabled'
```

The `'asap'` message is added to the agent’s message history and is visible to the model on the next request. Content enqueued during a tool call, from the tool or from a capability hook wrapping the call, is a side effect of that call, so it goes into the [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest) that carries the call’s [`ToolReturnPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturnPart), right after it. When parallel tool calls each enqueue something, each call’s content follows its own return, in the order that call enqueued it. The model still gets all of a request’s tool results ahead of the enqueued content, as providers require. A complete `ModelRequest` or `ModelResponse` passed to `enqueue` keeps its message-level fields, so it’s added as its own message instead, as is anything enqueued outside a tool call. So is content whose call has no `ToolReturnPart` in the next request (because the tool raised [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry), say), content that’s delivered in a later step, and content enqueued after something that was added as its own message. A [`SystemPromptPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.SystemPromptPart) is delivered the same way, and lands as a [mid-conversation system prompt](#mid-conversation-system-prompts) — it keeps its position in the history instead of being lifted into the top-level system prompt, so it doesn’t invalidate the cached prefix ahead of it. Only enqueue a `SystemPromptPart` for an instruction you authored; see the warning in that section for why late-arriving tool or webhook output belongs in user content instead.

### From external code driving agent.iter()

Use [`AgentRun.enqueue`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRun.enqueue) when you’re driving a run from outside (e.g. forwarding events from a webhook, chat platform, or job queue):

enqueue\_from\_agent\_run.py

```python
from pydantic_ai import Agent
from pydantic_graph import End

agent = Agent('anthropic:claude-opus-5-5')

async def main():
    async with agent.iter('Summarize the latest deploy report') as agent_run:
        # An external system pushes a follow-up while the agent is working.
        # When the agent would otherwise finish, the message redirects it
        # into a fresh model request so it can incorporate the new context.
        agent_run.enqueue(
            'A new error was just reported — include it in the summary.',
            priority='when_idle',
        )
        node = agent_run.next_node
        while not isinstance(node, End):
            node = await agent_run.next(node)
```

`'when_idle'` messages are only drained when the agent would otherwise reach an `End`. That drain runs after every capability’s `after_node_run` hook, so a capability that redirects the run can still enqueue there. `'asap'` messages are drained in `before_model_request`, once ahead of the other capabilities’ hooks and once after them, so content a `before_model_request` hook enqueues goes into the request being prepared. They’re also drained at the same end-of-run point if anything arrived during the final step. Both fire however you drive the run, so [`Agent.run`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run), [`AgentRun.next()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRun.next), and a bare `async for node in agent_run:` loop all deliver enqueued messages. A `wrap_model_request` hook that short-circuits without calling its handler skips `before_model_request`, so it also skips that request-time drain.

### Dequeuing a message or changing its priority

Until it’s delivered, a queued message can be changed by its `enqueue_id`. [`AgentRun.dequeue`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRun.dequeue) removes it, and [`AgentRun.set_enqueue_priority`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRun.set_enqueue_priority) gives it a new `priority`, keeping its place in the queue and its `enqueue_id`. That’s what a chat UI needs for a message the user typed while the agent was working: a “send now” button promotes it from `'when_idle'` to `'asap'`, and a remove button dequeues it.

dequeue\_or\_send\_now.py

```python
from pydantic_ai import Agent
from pydantic_graph import End

agent = Agent('anthropic:claude-opus-5-5')

async def main():
    async with agent.iter('Refactor the billing module') as agent_run:
        # Messages the user typed while the agent was working.
        follow_up = agent_run.enqueue('Then update the changelog.', priority='when_idle')
        typo = agent_run.enqueue('Also rename `foo`', priority='when_idle')
        assert follow_up is not None and typo is not None

        clicked = False
        node = agent_run.next_node
        while not isinstance(node, End):
            if Agent.is_call_tools_node(node) and not clicked:
                # The user pressed "send now" on one message and "remove" on the other.
                # `False` would mean the message was no longer queued, e.g. already delivered.
                sent_now = agent_run.set_enqueue_priority(follow_up, 'asap')
                removed = agent_run.dequeue(typo)
                print(sent_now, removed)
                #> True True
                clicked = True
            node = await agent_run.next(node)
```

Both return `False` once the message is no longer queued: it was delivered, it was already dequeued, or the run has ended. That’s not an error, as a click can race with the delivery: the check and the change happen under the same lock as delivery, so exactly one of them wins. `False` doesn’t say which of these happened. To tell the user a message was sent, watch for the [`EnqueuedMessagesEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.EnqueuedMessagesEvent) carrying its `enqueue_id`. A dequeued message gets no such event; one whose priority changed is announced under its original `enqueue_id` when it’s delivered.

A message enqueued at `'when_idle'` and promoted goes into the next model request as its own [`ModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest), after any `'asap'` messages queued before it. Content a tool enqueued at `'asap'` and then demoted to `'when_idle'` is delivered like other `'when_idle'` content, not next to that tool’s result. Tools and capability hooks can do the same with [`RunContext.dequeue`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.dequeue) and [`RunContext.set_enqueue_priority`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.set_enqueue_priority), and code driving a realtime session with [`RealtimeSession.dequeue`](https://pydantic.dev/docs/ai/api/pydantic-ai/realtime/#pydantic_ai.realtime.RealtimeSession.dequeue) and [`RealtimeSession.set_enqueue_priority`](https://pydantic.dev/docs/ai/api/pydantic-ai/realtime/#pydantic_ai.realtime.RealtimeSession.set_enqueue_priority). Inside a [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) unit, both raise [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError), like `enqueue`, since the change would be lost on replay.

## Processing Message History

Sometimes you may want to modify the message history before it’s sent to the model. This could be for privacy reasons (filtering out sensitive information), to save costs on tokens, to give less context to the LLM, or custom processing logic.

Pydantic AI provides the [`ProcessHistory`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ProcessHistory) capability that allows you to intercept and modify the message history before each model request.

That includes every request inside a run, not only the first: once the model calls a tool, the processor runs again before the next request and sees the run’s own tool calls and results after the earlier history. To process only the history from earlier runs, use a [context-aware processor](#runcontext-parameter) and leave unchanged the messages whose [`run_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.run_id) equals [`ctx.run_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.run_id).

### Usage

Each [`ProcessHistory`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ProcessHistory) wraps a callable that takes a list of [`ModelMessage`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelMessage) and returns a modified list of the same type.

Each processor is applied in sequence, and processors can be either synchronous or asynchronous.

simple\_history\_processor.py

```python
from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.capabilities import ProcessHistory

def filter_responses(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Remove all ModelResponse messages, keeping only ModelRequest messages."""
    return [msg for msg in messages if isinstance(msg, ModelRequest)]

# Create agent with history processor
agent = Agent('openai:gpt-6.1-sol', capabilities=[ProcessHistory(filter_responses)])

# Example: Create some conversation history
message_history = [
    ModelRequest(parts=[UserPromptPart(content='What is 2+2?')]),
    ModelResponse(parts=[TextPart(content='2+2 equals 4')]),  # This will be filtered out
]

# When you run the agent, the history processor will filter out ModelResponse messages
# result = agent.run_sync('What about 3+3?', message_history=message_history)
```

#### Keep Only Recent Messages

You can use the `history_processor` to only keep the recent messages:

keep\_recent\_messages.py

```python
from pydantic_ai import Agent, ModelMessage
from pydantic_ai.capabilities import ProcessHistory

async def keep_recent_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Keep only the last 5 messages to manage token usage."""
    return messages[-5:] if len(messages) > 5 else messages

agent = Agent('openai:gpt-6.1-sol', capabilities=[ProcessHistory(keep_recent_messages)])

# Example: Even with a long conversation history, only the last 5 messages are sent to the model
long_conversation_history: list[ModelMessage] = []  # Your long conversation history here
# result = agent.run_sync('What did we discuss?', message_history=long_conversation_history)
```

#### RunContext parameter

History processors can optionally accept a [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) parameter to access additional information about the current run, such as dependencies, model information, and usage statistics:

context\_aware\_processor.py

```python
from pydantic_ai import Agent, ModelMessage, RunContext
from pydantic_ai.capabilities import ProcessHistory

def context_aware_processor(
    ctx: RunContext,
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    # Access current usage
    current_tokens = ctx.usage.total_tokens

    # Filter messages based on context
    if current_tokens > 1000:
        return messages[-3:]  # Keep only recent messages when token usage is high
    return messages

agent = Agent('openai:gpt-6.1-sol', capabilities=[ProcessHistory(context_aware_processor)])
```

This allows for more sophisticated message processing based on the current state of the agent run.

Whether the processor wants a [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) is detected by resolving its type hints at runtime, so every annotated type in the processor signature must be imported at runtime rather than only under `if TYPE_CHECKING:`. If any annotation can’t be resolved, a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError) is raised instead of the processor being silently called without the context.

#### Summarize Old Messages

Use an LLM to summarize older messages to preserve context while reducing tokens. This is one of several ways to keep a conversation within the context window — see [Compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) for the full picture, including provider-native compaction and ready-made strategies from [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/compaction/).

summarize\_old\_messages.py

```python
from pydantic_ai import (
    Agent,
    CompactionPart,
    ModelMessage,
    ModelRequest,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.capabilities import ProcessHistory

# Use a cheaper model to summarize old messages.
summarize_agent = Agent(
    'openai:gpt-6-luna',
    instructions="""
Summarize this conversation, omitting small talk and unrelated topics.
Focus on the technical discussion and next steps.
""",
)

def starts_a_turn(message: ModelMessage) -> bool:
    # A request with a user prompt and no tool results answers no earlier tool call
    return isinstance(message, ModelRequest) and (
        any(isinstance(part, UserPromptPart) for part in message.parts)
        and not any(isinstance(part, ToolReturnPart) for part in message.parts)
    )

async def summarize_old_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    if len(messages) <= 10:
        return messages
    # Keep the first request (the task) and the latest turn, and summarize everything
    # between them. The latest turn starts at a request that answers no tool call, so
    # no call is cut off from its result.
    latest_turn = max(
        index for index, message in enumerate(messages) if starts_a_turn(message)
    )
    if latest_turn <= 1:
        return messages
    summary = await summarize_agent.run(
        'Summarize the conversation so far.', message_history=messages[1:latest_turn]
    )
    # Every model receives the summary as framed user-voice text
    summary_request = ModelRequest(parts=[CompactionPart(content=summary.output)])
    return [messages[0], summary_request, *messages[latest_turn:]]

agent = Agent('openai:gpt-6.1-sol', capabilities=[ProcessHistory(summarize_old_messages)])
```

#### Compact when the context window fills

The processors above rewrite history on every run. To wait until the conversation approaches the model’s [`context_window`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.context_window), check [`ctx.context_window_used`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.context_window_used). It returns the fraction of the window occupied after the latest response, or `None` when Pydantic AI cannot calculate it reliably.

compact\_when\_window\_fills.py

```python
from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelRequest,
    RunContext,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.capabilities import ProcessHistory

def compact_when_window_fills(
    ctx: RunContext,
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    used = ctx.context_window_used
    if used is None or used <= 0.8:
        return messages

    # Keep the most recent complete user turn, including any later tool calls and returns.
    for index in range(len(messages) - 1, -1, -1):
        message = messages[index]
        if not isinstance(message, ModelRequest):
            continue
        has_user_prompt = any(isinstance(part, UserPromptPart) for part in message.parts)
        has_tool_result = any(isinstance(part, ToolReturnPart) for part in message.parts)
        if has_user_prompt and not has_tool_result:
            return messages[index:]
    return messages

agent = Agent(
    'openai:gpt-6.1-sol',
    instructions='You are a helpful assistant.',
    capabilities=[ProcessHistory(compact_when_window_fills)],
)
```

Treat `None` as unknown, not as an empty context window. It is returned before the first model response and when the model’s window or response usage is unknown. The example leaves history unchanged in these cases. A [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel) measures against the smallest window among its candidates, so compaction happens early enough for whichever candidate answers. On Anthropic, a response that ran a [server-side tool loop or a compaction](https://pydantic.dev/docs/ai/models/anthropic/#server-side-tool-loops) is measured by its last pass only under a beta that reports the passes.

[Instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions) are sent with every request rather than stored in the history, so compaction can’t drop them. If you use [`system_prompt`](https://pydantic.dev/docs/ai/core-concepts/agent/#system-prompts) instead, add [`ReinjectSystemPrompt`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ReinjectSystemPrompt) after the compaction processor so the system prompt dropped with the old history is put back. The example keeps everything from the latest plain user turn onward; a turn that pairs tool results with a new prompt is kept whole, so a run started that way may keep more history than needed.

Pydantic AI fills the window size from [genai-prices](https://github.com/pydantic/genai-prices) where its data records one. For a custom or local model, or one genai-prices doesn’t cover yet, set the size explicitly with `profile={'context_window': 128_000}` — see [Inspecting a model’s profile](https://pydantic.dev/docs/ai/models/overview/#inspecting-a-models-profile).

#### Scheduling maintenance into cache-cold windows

See [Caching](https://pydantic.dev/docs/ai/capabilities/caching/#prefix-stability-guarantees) for the full prefix-stability contract and monitoring guidance.

History-mutating maintenance (summarizing, pruning, repair) has two costs: the work itself, and a *cache cost* — the next request re-writes the entire prompt prefix at full input price, since a mutated prefix can no longer hit the provider’s prompt cache. That cache cost is only real while the cache is still warm. Once a conversation has been idle longer than the provider retains the prefix, the next request pays full price anyway, so that turn is a free moment to run any deferrable maintenance.

Providers publish retention windows for their prompt caches. Pydantic AI records the documented default at the provider layer as [`ModelProfile.default_cache_retention`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.default_cache_retention): 5 minutes for Anthropic, 30 minutes for OpenAI’s GPT-5.6 and later. Where a provider’s retention depends on account configuration rather than the model — as OpenAI’s does for earlier models, where the default hinges on whether the organization has zero data retention enabled — the default is left unset, and the outlook is `'unknown'` unless you pass `retention=` yourself. [`prompt_cache_outlook()`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.prompt_cache_outlook) uses it to predict, from a message history alone, whether the next request is likely to hit a warm cache:

cache\_cold\_maintenance.py

```python
from datetime import UTC, datetime, timedelta

from pydantic_ai import ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.profiles import prompt_cache_outlook

profile = AnthropicModel('claude-sonnet-5-5').profile

now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
history = [
    ModelRequest(parts=[UserPromptPart(content='Hi')], timestamp=now - timedelta(minutes=30)),
    ModelResponse(parts=[TextPart(content='Hello!')], timestamp=now - timedelta(minutes=30)),
]

# The last exchange was 30 minutes ago, well past Anthropic's 5-minute default.
outlook = prompt_cache_outlook(history, profile=profile, now=now)
print(outlook)
#> cold
```

A `'cold'` outlook is the signal to flush pending maintenance for free; `'warm'` means the mutation would sacrifice a live cache hit, so defer it if it can wait; `'unknown'` (no documented retention, or a history without timestamps) should be treated like `'warm'` — never mutate on a guess.

Retention you request through model settings, such as the unified [`cache='1h'`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.cache), `anthropic_cache='1h'` or `openai_prompt_cache_retention='24h'` on OpenAI models before GPT-5.6, replaces the provider’s default. [`Model.resolve_cache_retention()`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model.resolve_cache_retention) works it out from the settings a request is made with, returning `None` when they don’t ask for anything, so passing its result as `retention=` keeps the profile’s default in that case. A [`before_model_request`](https://pydantic.dev/docs/ai/core-concepts/hooks/) hook has both the model and the request’s settings at hand, so it can decide whether to do the expensive work this turn:

cache\_cold\_hook.py

```python
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.profiles import prompt_cache_outlook

hooks = Hooks()

@hooks.on.before_model_request
async def compact_when_cold(ctx: RunContext, request_context: ModelRequestContext) -> ModelRequestContext:
    messages = request_context.messages
    model = request_context.model
    outlook = prompt_cache_outlook(
        messages,
        profile=model.profile,
        retention=model.resolve_cache_retention(request_context.model_settings),
    )
    over_budget = ctx.usage.total_tokens > 100_000
    if len(messages) > 10 and (over_budget or outlook == 'cold'):
        # Expensive: replace with your real summarization/pruning pass.
        request_context.messages = messages[:1] + messages[-4:]
    return request_context

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    model_settings=AnthropicModelSettings(anthropic_cache='1h'),  # (1)
    capabilities=[hooks],
)
```

With the 1-hour cache requested, the outlook only turns `'cold'` after an hour of idleness rather than Anthropic's default 5 minutes.

`CachePoint(ttl='1h')` markers in history extend the boundary in the same way, when the provider supports that retention (one of the profile’s [`supported_cache_retentions`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_cache_retentions)): OpenAI ignores `CachePoint.ttl`, so a `'1h'` marker doesn’t extend GPT-5.6’s 30 minutes. Azure and providers without a single documented default leave the field `None`, producing `'unknown'` unless the settings request a retention or you pass one explicitly.

### Testing History Processors

You can test what messages are actually sent to the model provider using [`FunctionModel`](https://pydantic.dev/docs/ai/api/models/function/#pydantic_ai.models.function.FunctionModel):

test\_history\_processor.py

```python
import pytest

from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.models.function import AgentInfo, FunctionModel

@pytest.fixture
def received_messages() -> list[ModelMessage]:
    return []

@pytest.fixture
def function_model(received_messages: list[ModelMessage]) -> FunctionModel:
    def capture_model_function(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        # Capture the messages that the provider actually receives
        received_messages.clear()
        received_messages.extend(messages)
        return ModelResponse(parts=[TextPart(content='Provider response')])

    return FunctionModel(capture_model_function)

def test_history_processor(function_model: FunctionModel, received_messages: list[ModelMessage]):
    def filter_responses(messages: list[ModelMessage]) -> list[ModelMessage]:
        return [msg for msg in messages if isinstance(msg, ModelRequest)]

    agent = Agent(function_model, capabilities=[ProcessHistory(filter_responses)])

    message_history = [
        ModelRequest(parts=[UserPromptPart(content='Question 1')]),
        ModelResponse(parts=[TextPart(content='Answer 1')]),
    ]

    agent.run_sync('Question 2', message_history=message_history)
    assert received_messages == [
        ModelRequest(parts=[UserPromptPart(content='Question 1')]),
        ModelRequest(parts=[UserPromptPart(content='Question 2')]),
    ]
```

### Multiple Processors

You can also use multiple processors:

multiple\_history\_processors.py

```python
from pydantic_ai import Agent, ModelMessage, ModelRequest
from pydantic_ai.capabilities import ProcessHistory

def filter_responses(messages: list[ModelMessage]) -> list[ModelMessage]:
    return [msg for msg in messages if isinstance(msg, ModelRequest)]

def summarize_old_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    return messages[-5:]

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[ProcessHistory(filter_responses), ProcessHistory(summarize_old_messages)],
)
```

In this case, the `filter_responses` processor will be applied first, and the `summarize_old_messages` processor will be applied second.

## Examples

For a more complete example of using messages in conversations, see the [chat app](https://pydantic.dev/docs/ai/examples/conversational-agents/chat-app/) example.
