---
type: Concept
title: SGLang Reasoning Parser
description: Separate reasoning and final-answer content for thinking models via --reasoning-parser, separate_reasoning, and per-model parser tags.
tags: [sglang, reasoning, inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-reasoning
    resource: ../raw/sglang/advanced_features/separate_reasoning.mdx
    title: Reasoning Parser
---

SGLang parses thinking-model output into separate reasoning and normal content when the server is launched with the matching `--reasoning-parser`, following the DeepSeek R1 `reasoning_content` plus `content` contract for OpenAI-compatible APIs[^sgl-reasoning].

## Supported parsers

| Model series | Reasoning tags | Parser | Notes |
| --- | --- | --- | --- |
| DeepSeek-R1 series | `<think>` … `</think>` | `deepseek-r1` | All variants: R1, R1-0528, R1-Distill[^sgl-reasoning] |
| DeepSeek-V3 series | `<think>` … `</think>` | `deepseek-v3` | Includes V3.2; supports `thinking` parameter[^sgl-reasoning] |
| Standard Qwen3 | `<think>` … `</think>` | `qwen3` | Supports `enable_thinking` parameter[^sgl-reasoning] |
| Qwen3-Thinking | `<think>` … `</think>` | `qwen3` or `qwen3-thinking` | Always generates thinking content[^sgl-reasoning] |
| Kimi K2 Thinking | `◁think▷` … `◁/think▷` | `kimi_k2` | Special delimiters; also requires `--tool-call-parser kimi_k2` for tool use[^sgl-reasoning] |
| GPT OSS | `<|channel|>analysis<|message|>` … `<|end|>` | `gpt-oss` | No additional notes in source[^sgl-reasoning] |

## Model-specific behaviors

- DeepSeek-R1 jumps directly to thinking content with no `<think>` start tag, while R1-0528 generates both `<think>` and `</think>`; the same `deepseek-r1` parser handles both[^sgl-reasoning].
- DeepSeek-V3.1/V3.2 are hybrid thinking/non-thinking models using the `deepseek-v3` parser and `thinking` parameter, explicitly not `enable_thinking`[^sgl-reasoning].
- Standard Qwen3 such as Qwen3-2507 uses the `qwen3` parser with `enable_thinking` in chat templates, while Qwen3-Thinking such as Qwen3-235B-A22B-Thinking-2507 uses `qwen3` or `qwen3-thinking` and always thinks[^sgl-reasoning].
- Kimi K2 Thinking uses `◁think▷` / `◁/think▷` and needs `--tool-call-parser kimi_k2` for agentic tool use[^sgl-reasoning].
- GPT OSS uses `<|channel|>analysis<|message|>` through `<|end|>`[^sgl-reasoning].

## Server launch

Specify `--reasoning-parser`; it defines the parser used to interpret responses[^sgl-reasoning]:

```bash
python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --host 0.0.0.0 --reasoning-parser deepseek-r1 --log-level warning
```

## OpenAI-compatible API

The contract follows the DeepSeek API design: `reasoning_content` carries chain-of-thought and `content` carries the final answer[^sgl-reasoning].

- Non-streaming: pass `extra_body={"separate_reasoning": True}`, then read `message.reasoning_content` and `message.content`[^sgl-reasoning].
- Streaming: pass `extra_body={"separate_reasoning": True}`, then accumulate `delta.reasoning_content` and `delta.content` across chunks[^sgl-reasoning].
- Buffered streaming: add `"stream_reasoning": False` alongside `"separate_reasoning": True` to buffer reasoning content to the last reasoning chunk, or equivalently the first chunk after reasoning content[^sgl-reasoning].
- Disable: set `extra_body={"separate_reasoning": False}` to return the original combined output in `message.content`; the source states separation is enabled by default when the parser is specified, though the enabling sentence is truncated[^sgl-reasoning].

## Native and offline APIs

- Native `/generate` plus `/separate_reasoning`: generate text with `skip_special_tokens: False` in the example, then POST `{"text": gen_response, "reasoning_parser": "deepseek-r1"}` to `/separate_reasoning` and read `reasoning_text` plus `text`[^sgl-reasoning].
- Offline engine: generate with `sgl.Engine`, then split locally with `ReasoningParser("deepseek-r1").parse_non_stream(generated_text)` into `reasoning_text, text`[^sgl-reasoning].
- The native and offline examples use `max_new_tokens: 1024`, `temperature: 0.6`, and `top_p: 0.95`; `skip_special_tokens: False` preserves the reasoning tags for parsing[^sgl-reasoning].

## Adding a new schema

Implement the new parser as a subclass of `BaseReasoningFormatDetector` in `python/sglang/srt/reasoning_parser.py` and select it via the reasoning-parser option for the new schema[^sgl-reasoning].

## Relationships

- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — advanced-features map; this reasoning-parser page is an unlisted `advanced_features/` source outside that map's listed entries.
- Uses [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — vLLM analogue with separate `reasoning` output, per-model parsers, thinking toggles, budgets, and suppression controls.

## Coverage limits

- Hugging Face collection/model links and the DeepSeek reasoning-model API guide were treated as identifiers and not fetched[^sgl-reasoning].
- `sglang.test.doc_patch.launch_server_cmd` and the `sgl.Engine` / `ReasoningParser` example helpers were not independently verified beyond this source[^sgl-reasoning].
- The source sentence stating when separation is on by default is truncated ("when specify ."), so the exact enabling condition is recorded as stated with that gap[^sgl-reasoning].

[^sgl-reasoning]: Reasoning Parser — `../raw/sglang/advanced_features/separate_reasoning.mdx`.
