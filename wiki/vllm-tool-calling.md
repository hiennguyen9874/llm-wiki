---
type: Concept
title: vLLM Tool Calling
description: Named, auto, required, and none tool-choice modes with model-specific parsers and schema-constrained decoding for vLLM.
tags: [vllm, tool-calling, inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: tool-calling
    resource: ../raw/vllm/features/tool_calling.md
    title: Tool Calling
---

vLLM supports `auto`, named-function, `required`, and `none` options for `tool_choice` in the chat-completion API, using structured-outputs constraints for named/`required` modes and model-specific tool-call parsers plus chat templates for `auto` mode[^tool-calling].

## Tool-choice modes

- `auto`: model decides whether to emit tool calls; requires `--enable-auto-tool-choice` plus `--tool-call-parser`[^tool-calling].
- Named function: `tool_choice={"type": "function", "function": {"name": ...}}` forces that tool; uses the structured-outputs backend, so first use incurs FSM-compilation latency before caching[^tool-calling].
- Named calling is enabled by default, works with most structured-outputs backends, and guarantees a validly parsable call, not a high-quality one; for best results restate the expected output format/schema in the prompt[^tool-calling].
- `required` (`tool_choice='required'`, `vllm>=0.8.3`): model must produce one or more tool calls from `tools`; uses structured outputs, enabled by default for any supported model; alternative decoding backends for V1 are on the roadmap[^tool-calling].
- `none`: model produces no tool calls and returns regular text even when `tools` are defined[^tool-calling].
- Tool definitions are included in the prompt by default even when `tool_choice='none'`; use `--exclude-tools-when-tool-choice-none` to exclude them[^tool-calling].
- Caller responsibilities: define appropriate `tools`, include relevant context in messages, and execute tool calls in application logic[^tool-calling].

## Constrained decoding and strict mode

Whether the tool parameter schema is enforced depends on mode and per-tool `strict`[^tool-calling]:

| `tool_choice` | Schema-constrained decoding | Behavior |
| --- | --- | --- |
| Named function | Yes, via structured outputs | Arguments guaranteed valid JSON conforming to parameter schema. |
| `required` | Yes, via structured outputs | Same guarantee; at least one tool call required. |
| `auto` | Only when `strict: true` on at least one tool | With opt-in, structural-tag parsers constrain arguments; without it, model generates freely and calls are extracted from raw text. |
| `none` | N/A | No tool calls produced. |

Table content is from the source[^tool-calling].

- For `required`/named calling, structural-tag constraints always apply regardless of `strict`; for `auto`, `strict: true` on at least one tool opts in, otherwise extraction is unconstrained and arguments may be malformed or violate the schema[^tool-calling].
- `strict` is supported across Chat Completion, Responses, and Anthropic Messages APIs[^tool-calling].
- For strict-schema compatibility, define parameters in OpenAI strict style: `additionalProperties: false` on each object, all `properties` marked required, optional fields expressed as nullable e.g. `{"type": ["string", "null"]}`[^tool-calling].
- Global toggle `VLLM_ENFORCE_STRICT_TOOL_CALLING` defaults to `true`; `false` disables structural-tag attachment regardless of per-tool `strict`, without changing schema-derived structured outputs used by named/`required` modes[^tool-calling].
- With `auto`, schema-level constraint additionally requires parser support for structural tags; example startup: `VLLM_ENFORCE_STRICT_TOOL_CALLING=false vllm serve ...`[^tool-calling].

## Automatic function calling setup

- `--enable-auto-tool-choice` — mandatory auto-tool-choice enablement[^tool-calling].
- `--tool-call-parser` — select parser from the list below; `--tool-parser-plugin` optionally registers user-defined parsers whose names can then be passed to `--tool-call-parser`[^tool-calling].
- `--chat-template` — optional path handling `tool`-role and prior-tool-call assistant messages; Hermes, Mistral, and Llama models already carry tool-compatible templates in `tokenizer_config.json`, and `tool_use` selects a model-provided tool-use template per the Transformers specification[^tool-calling].
- If a model is unsupported, contribute a parser and tool-use chat template[^tool-calling].
- Minimal server example for Llama 3.1 8B[^tool-calling]:

```text
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --enable-auto-tool-choice \
  --tool-call-parser llama3_json \
  --chat-template examples/tool_chat_template_llama3.1_json.jinja
```

## Model-specific parsers

Parser and template pairings from the source[^tool-calling]:

| Family / parser | Models | Flags / template |
| --- | --- | --- |
| `hermes` | Nous Hermes 2 Pro/Theta and Hermes 3 newer than Hermes 2 Pro; also Qwen2.5 and QwQ-32B | `--tool-call-parser hermes` |
| `mistral` | Mistral function-calling models incl. `Mistral-7B-Instruct-v0.3` | `--tool-call-parser mistral`; Transformers-format variant adds `--tokenizer_mode hf --config_format hf --load_format hf --chat-template examples/tool_chat_template_mistral_parallel.jinja` |
| `llama3_json` | Llama 3.1/3.2/4 JSON-based tool calling | `--tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.1_json.jinja` or `..._llama3.2_json.jinja` (adds images) |
| `llama4_pythonic` | Llama 4, pythonic recommended | `--tool-call-parser llama4_pythonic --chat-template examples/tool_chat_template_llama4_pythonic.jinja` |
| `pythonic` | Python-list emitters e.g. Llama-3.2-1B/3B, ToolACE-8B, Ultravox-ToolACE-8B, Llama-4-Scout/Maverick | `--tool-call-parser pythonic --chat-template {model-specific, e.g. examples/tool_chat_template_llama3.2_pythonic.jinja, ..._toolace.jinja, ..._llama4_pythonic.jinja}` |
| `granite`, `granite4`, `granite-20b-fc` | Granite 4.0 H small, 3.0-8B, 3.1-8B, 20b-functioncalling | `granite4` with no custom template; `granite` for 3.1 (HF template) or with `examples/tool_chat_template_granite.jinja` for 3.0; `granite-20b-fc` with `examples/tool_chat_template_granite_20b_fc.jinja` |
| `internlm` | `internlm2_5-7b-chat` plus compatible 2.5 models | `--tool-call-parser internlm --chat-template examples/tool_chat_template_internlm2_tool.jinja` |
| `jamba` | AI21 Jamba-1.5 Mini/Large | `--tool-call-parser jamba` |
| `xlam` | Salesforce Llama-xLAM and Qwen-xLAM fc-r models | `--tool-call-parser xlam --chat-template examples/tool_chat_template_xlam_llama.jinja` or `..._xlam_qwen.jinja` |
| `deepseek_v3` | DeepSeek-V3-0324, R1-0528 | `--tool-call-parser deepseek_v3 --chat-template {examples/tool_chat_template_deepseekv3.jinja or ..._deepseekr1.jinja}` |
| `deepseek_v31` | DeepSeek-V3.1 | `--tool-call-parser deepseek_v31 --chat-template examples/tool_chat_template_deepseekv31.jinja` |
| `openai` | `openai/gpt-oss-20b`, `gpt-oss-120b` | `--tool-call-parser openai` |
| `kimi_k2` | `moonshotai/Kimi-K2-Instruct` | `--tool-call-parser kimi_k2` |
| `hunyuan_a13b` | `tencent/Hunyuan-A13B-Instruct` (HF template included) | non-reasoning `--tool-call-parser hunyuan_a13b`; reasoning adds `--reasoning-parser hunyuan_a13b` |
| `cohere_command3` / `cohere_command4` | Command-A-Reasoning (`command3`); Command-A-Plus and North-Mini-Code (`command4`) | `--tool-call-parser cohere_command4 --reasoning-parser cohere_command4`; requires `cohere_melody` package |
| `longcat` | LongCat-Flash-Chat and FP8 | `--tool-call-parser longcat` |
| `glm45` | GLM-4.5, 4.5-Air, 4.6 | `--tool-call-parser glm45` |
| `glm47` | GLM-4.7, 4.7-Flash | `--tool-call-parser glm47` |
| `functiongemma` | `google/functiongemma-270m-it` (`<start_function_call>` format) | `--tool-call-parser functiongemma --chat-template examples/tool_chat_template_functiongemma.jinja` |
| `qwen3_xml` | Qwen3-Coder-480B and 30B Instruct | `--tool-call-parser qwen3_xml` |
| `olmo3` | Olmo-3-7B-Instruct, 32B-Think (pythonic-like, newline-delimited, `<function_calls>` wrapped, JSON booleans/null allowed) | `--tool-call-parser olmo3` |
| `gigachat3` | GigaChat3 10B/702B preview variants (HF template) | `--tool-call-parser gigachat3` |
| `apertus` | Apertus-8B/70B-Instruct-2509 | `--tool-call-parser apertus --chat-template examples/tool_chat_template_apertus.jinja` |

- `xlam` detects direct JSON arrays, `<think>` blocks, ```json fences, and `[TOOL_CALLS]` / `<tool_call>` tags, supports parallel calls, and separates text from calls[^tool-calling].
- FunctionGemma is a 270M edge-oriented model intended to be fine-tuned for the target function set[^tool-calling].

## Known limitations

- Hermes 2 Theta models have degraded tool-call quality from their merge step[^tool-calling].
- Mistral 7B struggles with parallel tool calls; Transformers-backend Mistral templates require exactly 9-digit `tool_call_id`s, so vLLM ships tweaked `tool_chat_template_mistral.jinja` (truncates IDs) and `tool_chat_template_mistral_parallel.jinja` (adds tool-use system prompt)[^tool-calling].
- Official Mistral models have two formats: default `mistral` tokenizer/config/load path via `mistral-common`, versus `hf` path for the Transformers format[^tool-calling].
- Llama 3 lacks parallel tool calls (supported on Llama 4); Llama JSON tool calling excludes built-in python/custom variants; models may serialize arrays as strings; smaller Llama models frequently emit malformed calls[^tool-calling].
- `pythonic` models must not mix text and tool calls in one generation; consensus on start/end tokens is still missing, notably Llama 3.2 emits none[^tool-calling].
- InternLM2 tool results are unstable on `internlm2-chat-7b`[^tool-calling].

## Benchmarking and plugins

- Benchmark tool-calling serving latency/throughput with the BFCL dataset via `vllm bench serve`; full commands are in the BFCL benchmark example, not ingested here[^tool-calling].
- Custom parsers subclass `ToolParser` (`adjust_request`, `extract_tool_calls_streaming`, `extract_tool_calls`), register with `ToolParserManager.register_lazy_module(name, module_path, class_name)`, and serve with `--tool-parser-plugin <absolute-path> --tool-call-parser <name> --chat-template <template>`; reference implementation is `Hermes2ProToolParser`, not inspected here[^tool-calling].

## Coverage limits

- Example chat templates under `examples/tool_chat_template_*.jinja`, `vllm/tool_parsers/hermes_tool_parser.py`, and referenced usage/benchmark pages (`usage/v1_guide.md`, `benchmarking/cli.md`) were outside `raw/` and were not inspected[^tool-calling].
- Hugging Face model pages, Transformers chat-templating docs, `mistral-common`, `cohere_melody`, FunctionGemma fine-tuning docs, and the BFCL dataset were treated as identifiers and not fetched[^tool-calling].

## Relationships

- Uses [vLLM Structured Outputs](vllm-structured-outputs.md) — named and `required` modes enforce parameter schemas via the structured-outputs backend; `auto` plus `strict: true` uses structural-tag constraints.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — tool calling is served through `vllm serve` OpenAI-compatible chat completions with `tools` and `tool_choice`.
- Uses [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — Hunyuan-A13B and Cohere parsers combine `--tool-call-parser` with `--reasoning-parser`, returning `reasoning` alongside `tool_calls`.
- Uses [vLLM Interleaved Thinking](vllm-interleaved-thinking.md) — interleaved thinking chains tool calls with reasoning steps between them.

[^tool-calling]: Tool Calling — `../raw/vllm/features/tool_calling.md`, full page.
