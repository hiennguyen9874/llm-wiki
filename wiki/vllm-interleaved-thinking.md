---
type: Concept
title: vLLM Interleaved Thinking
description: Reasoning between tool calls for chained tool use with intermediate decisions.
tags: [vllm, tool-calling, reasoning]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: interleaved-thinking
    resource: ../raw/vllm/features/interleaved_thinking.md
    title: Interleaved Thinking
---

vLLM interleaved thinking lets supported models emit reasoning between tool calls, so each subsequent tool choice can reflect intermediate tool results rather than a single upfront plan[^interleaved-thinking].

## Capabilities

- Reason about a tool result before deciding what to do next[^interleaved-thinking].
- Chain multiple tool calls with reasoning steps in between[^interleaved-thinking].
- Make nuanced decisions based on intermediate results[^interleaved-thinking].
- Expose transparent reasoning for tool selection[^interleaved-thinking].

## Cost

- Increases token usage and response latency; weigh budget and performance requirements before enabling[^interleaved-thinking].

## Supported models

| Model series | Reasoning parser name |
| ------------ | --------------------- |
| moonshotai/Kimi-K2-Thinking | kimi_k2 |
| MiniMaxAI/MiniMax-M2 | minimax_m2 |

Table content is from the source[^interleaved-thinking].

## Configuration

- Serve a supporting model with matching tool-call and reasoning parsers plus auto tool choice[^interleaved-thinking]:

```text
vllm serve MiniMaxAI/MiniMax-M2 \
  --tensor-parallel-size 4 \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2 \
  --enable-auto-tool-choice
```

- In chat-completion requests, enable tool calls with `tools` and `tool_choice="auto"`[^interleaved-thinking].

## Multi-turn tool loop

The source demonstrates a weather-tool loop[^interleaved-thinking]:

1. Send user message plus tool definition in the first `chat.completions.create`.
2. Append the assistant turn with both `tool_calls` and `reasoning` to preserve reasoning history.
3. Execute the requested tools locally and append one `role: tool` message per call with `content`, `tool_call_id`, and `name`.
4. Send the extended message list in a second `chat.completions.create` to get the final content.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — the example serves via `vllm serve` and drives the loop through the OpenAI-compatible chat-completions API.

[^interleaved-thinking]: Interleaved Thinking — `../raw/vllm/features/interleaved_thinking.md`, full page.
