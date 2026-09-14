---
type: Concept
title: vLLM Reasoning Outputs
description: Separate reasoning and content fields for thinking models via reasoning parsers, thinking toggles, budgets, and response controls.
tags: [vllm, reasoning, inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: reasoning-outputs
    resource: ../raw/vllm/features/reasoning_outputs.md
    title: Reasoning Outputs
---

vLLM exposes thinking-model traces in a separate `reasoning` field alongside `content` when the server is started with the matching `--reasoning-parser`, with per-model thinking toggles, token budgets, effort mapping, and response suppression[^reasoning-outputs].

## Output model

- Reasoning models return `reasoning` plus `content`; other models have no `reasoning` field[^reasoning-outputs].
- `reasoning` was formerly `reasoning_content`; migrate by replacing the name and updating client code, otherwise clients can silently read an empty `reasoning_content` while `reasoning` is populated[^reasoning-outputs].

## Supported parsers

Serve with `vllm serve <model> --reasoning-parser <name>`[^reasoning-outputs]:

| Model series | Parser name | Structured output | Tool calling |
| ------------ | ----------- | ----------------- | ------------ |
| Cohere Command A Reasoning | `cohere_command3` | `json`, `regex` | ✅ |
| Cohere Command A Plus | `cohere_command4` | `json`, `regex` | ✅ |
| DeepSeek R1 series | `deepseek_r1` | `json`, `regex` | ❌ |
| Gemma 4 series | `gemma4` | `json`, `regex` | ✅ |
| DeepSeek-V3.1 | `deepseek_v3` | `json`, `regex` | ❌ |
| ERNIE-4.5-VL series | `ernie45` | `json`, `regex` | ❌ |
| ERNIE-4.5-21B-A3B-Thinking | `ernie45` | `json`, `regex` | ✅ |
| GLM-4.5 series | `glm45` | `json`, `regex` | ✅ |
| Holo2 series | `holo2` | `json`, `regex` | ✅ |
| Hunyuan A13B series | `hunyuan_a13b` | `json`, `regex` | ✅ |
| IBM Granite 3.2 language models | `granite` | ❌ | ❌ |
| MiniMax-M2 | `minimax_m2_append_think` | `json`, `regex` | ✅ |
| Qwen3 series | `qwen3` | `json`, `regex` | ✅ |
| QwQ-32B | `deepseek_r1` | `json`, `regex` | ✅ |

Table content is from the source[^reasoning-outputs].

## Thinking enablement defaults

- Disabled by default, enable with `chat_template_kwargs`: IBM Granite 3.2 and DeepSeek-V3.1 need `thinking=True`; Gemma 4 needs `enable_thinking=True` or `reasoning_effort`[^reasoning-outputs].
- Enabled by default, disable with `chat_template_kwargs`: Qwen3 needs `enable_thinking=False`; Holo2 needs `thinking=False`[^reasoning-outputs].
- DeepSeek-V3.1 tool calling is supported in non-thinking mode[^reasoning-outputs].

## Request handling

- Non-streaming chat completions read `message.reasoning` and `message.content`[^reasoning-outputs].
- Streaming chat completions carry `reasoning` in `delta`; the OpenAI Python client has no official `reasoning` attribute, so use `getattr(delta, "reasoning", None)` and check before accessing[^reasoning-outputs].
- With tool calling plus reasoning parser, `reasoning` is returned alongside `tool_calls`, but function parsing reads only `content`, not `reasoning`[^reasoning-outputs].

## Server defaults and overrides

- Set cross-request thinking defaults with `--default-chat-template-kwargs`, for example `'{"enable_thinking": false}'` for Qwen3 or `'{"thinking": true}'` for Granite 3.2 / DeepSeek-V3.1[^reasoning-outputs].
- Per-request `extra_body={"chat_template_kwargs": {...}}` always overrides the server default[^reasoning-outputs].

## Thinking budget control

- `--reasoning-parser` enables extraction; `--reasoning-config` sets `ReasoningConfig` boundary strings `reasoning_start_str` and `reasoning_end_str`; otherwise vLLM tries to infer them from the parser[^reasoning-outputs].
- Per-request `thinking_token_budget` limits reasoning tokens counted from `reasoning_start_str`; at the limit vLLM forces `reasoning_end_str`, ending the reasoning block[^reasoning-outputs].
- Without `thinking_token_budget`, only normal generation limits such as `max_tokens` apply[^reasoning-outputs].
- `reasoning_end_str` may include a transition phrase for a more natural cutoff[^reasoning-outputs].
- Offline use is `LLM(..., reasoning_config=ReasoningConfig(...))` with `SamplingParams(thinking_token_budget=...)`; online use passes `thinking_token_budget` in the chat-completions request[^reasoning-outputs].

## Automatic `enable_thinking` from `reasoning_effort`

- `reasoning_effort` `"low"`, `"medium"`, or `"high"` injects `enable_thinking=true`; `"none"` injects `false`; unset injects nothing[^reasoning-outputs].
- Applies to Chat Completions `reasoning_effort` and Responses API `reasoning.effort`, covering models such as Gemma 4, DeepSeek-V4-Pro, and Granite 3.2 that otherwise generate no reasoning tokens[^reasoning-outputs].
- Explicit `enable_thinking` in `chat_template_kwargs` wins; for templates without that kwarg such as DeepSeek R1, the injected value is harmlessly filtered out[^reasoning-outputs].

## Suppressing reasoning in responses

- `include_reasoning=false` still generates reasoning tokens so quality is unchanged, but omits them to reduce traffic; supported for streaming and non-streaming Chat Completions and Responses APIs[^reasoning-outputs].
- Chat Completions passes it as `extra_body={"include_reasoning": false}` with reasoning included by default; Responses API passes `include_reasoning=False` and then emits no `reasoning` output items[^reasoning-outputs].
- Suppression also hides per-token metadata such as logprobs and token IDs to avoid leaking reasoning through decoded token text or raw IDs[^reasoning-outputs].

## Limitations

- Reasoning content is only available on online serving chat completions (`/v1/chat/completions`), Anthropic Messages (`/v1/messages`), and Responses (`/v1/responses`) endpoints[^reasoning-outputs].

## Adding a new reasoning model

- Subclass `ReasoningParser` with `extract_reasoning` for complete outputs and `extract_reasoning_streaming` for partial/streaming outputs, then register with `ReasoningParserManager.register_lazy_module(name, module_path, class_name)` and serve with `--reasoning-parser <name>`[^reasoning-outputs].
- For structured output, define a `Reasoner` with start/end token IDs such as `<think>` / `</think>`; engines including xgrammar use `end_token_id` to detect reasoning and skip structured constraints while it is present[^reasoning-outputs].

## Coverage limits

- Locally referenced parser and example paths such as `../../vllm/reasoning/deepseek_r1_reasoning_parser.py` and `../../examples/reasoning/*.py` are outside `raw/` and were not inspected[^reasoning-outputs].
- External Hugging Face, OpenAI API, and xgrammar links were treated as identifiers and not fetched[^reasoning-outputs].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — reasoning parsers apply to `vllm serve` online endpoints, with offline `LLM` support via `ReasoningConfig`.
- Uses [vLLM Interleaved Thinking](vllm-interleaved-thinking.md) — interleaved thinking is the chained tool-use variant where reasoning appears between tool calls.

[^reasoning-outputs]: Reasoning Outputs — `../raw/vllm/features/reasoning_outputs.md`, full page.
