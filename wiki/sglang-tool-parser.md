---
type: Concept
title: SGLang Tool Parser
description: Model-specific tool-call parsing for SGLang function calling across OpenAI-compatible, native, and offline APIs with tool_choice and pythonic formats.
tags: [sglang, tool-calling, function-calling]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:16:04Z }
sources:
  - id: sgl-tool-parser
    resource: ../raw/sglang/advanced_features/tool_parser.mdx
    title: Tool Parser
---

SGLang implements OpenAI-compatible function calling by launching the server with a model-specific `--tool-call-parser` that interprets raw generations as tool calls across OpenAI-compatible, native `/generate` plus `/parse_function_call`, and offline-engine APIs[^sgl-tool-parser].

## Supported parsers

Parser and model pairings from the source[^sgl-tool-parser]:

| Parser | Supported models | Notes |
| --- | --- | --- |
| `deepseekv3` | DeepSeek-v3, e.g. `deepseek-ai/DeepSeek-V3-0324` | Recommend `--chat-template ./examples/chat_template/tool_chat_template_deepseekv3.jinja`. |
| `deepseekv31` | DeepSeek-V3.1 and DeepSeek-V3.2-Exp, e.g. `deepseek-ai/DeepSeek-V3.1`, `deepseek-ai/DeepSeek-V3.2-Exp` | Recommend `--chat-template ./examples/chat_template/tool_chat_template_deepseekv31.jinja`, or `..deepseekv32.jinja` for DeepSeek-V3.2. |
| `deepseekv32` | DeepSeek-V3.2, `deepseek-ai/DeepSeek-V3.2` | No additional notes. |
| `glm` | GLM series, e.g. `zai-org/GLM-4.6` | No additional notes. |
| `gpt-oss` | GPT-OSS, e.g. `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `lmsys/gpt-oss-120b-bf16`, `lmsys/gpt-oss-20b-bf16` | Filters out analysis-channel events and preserves only normal text; content can be empty when explanations are in the analysis channel. Work around by completing the tool round with `role="tool"` result messages so the model can generate final content. |
| `kimi_k2` | `moonshotai/Kimi-K2-Instruct` | No additional notes. |
| `llama3` | Llama 3.1 / 3.2 / 3.3, e.g. `meta-llama/Llama-3.1-8B-Instruct`, `meta-llama/Llama-3.2-1B-Instruct`, `meta-llama/Llama-3.3-70B-Instruct` | No additional notes. |
| `llama4` | Llama 4, e.g. `meta-llama/Llama-4-Scout-17B-16E-Instruct` | No additional notes. |
| `mistral` | Mistral, e.g. `mistralai/Mistral-7B-Instruct-v0.3`, `mistralai/Mistral-Nemo-Instruct-2407`, `mistralai/Mistral-7B-v0.3` | No additional notes. |
| `pythonic` | Llama-3.2 / Llama-3.3 / Llama-4 | Model outputs calls as Python code; requires `--tool-call-parser pythonic` and a matching chat template is recommended. |
| `qwen` | Qwen series except Qwen3-Coder, e.g. `Qwen/Qwen3-Next-80B-A3B-Instruct`, `Qwen/Qwen3-VL-30B-A3B-Thinking` | No additional notes. |
| `qwen3_coder` | Qwen3-Coder, e.g. `Qwen/Qwen3-Coder-30B-A3B-Instruct` | No additional notes. |
| `step3` | Step-3 | No additional notes. |

Server launch defines the parser used to interpret responses[^sgl-tool-parser]:

```bash
python3 -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --tool-call-parser qwen25 --host 0.0.0.0 --log-level warning
```

## OpenAI-compatible API

- Define `tools` as OpenAI-style `{"type": "function", "function": {"name", "description", "parameters": {"type": "object", "properties", "required"}}}` objects; the worked example is `get_current_weather` with required `city`, `state`, and `unit`[^sgl-tool-parser].
- Serve through an OpenAI-like client pointed at `/v1`, then call `client.chat.completions.create` with `messages`, `tools`, sampling settings, and `stream=False` or `stream=True`[^sgl-tool-parser].
- Non-streaming: read `choices[0].message.content` and `choices[0].message.tool_calls`, then read `tool_calls[0].function.name` and `.function.arguments`[^sgl-tool-parser].
- Streaming: accumulate `chunk.choices[0].delta.content` into text and collect `chunk.choices[0].delta.tool_calls[0]` fragments, printing `function.name` when present and joining `function.arguments` fragments into one JSON string[^sgl-tool-parser].
- Execute the selected local function from the parsed arguments, then append the assistant message and a `role: tool` message carrying `tool_call_id`, `content`, and `name` before sending the updated history back for the final response[^sgl-tool-parser].

## Native API and SRT

- Build the prompt with `tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, tools=tools)`, POST to `/generate` with `skip_special_tokens: False` preserved, then POST `{"text": gen_response, "tool_call_parser": ..., "tools": tools}` to `/parse_function_call`[^sgl-tool-parser].
- Read `normal_text` for the non-call text and `calls[0].name` plus `calls[0].parameters` for the parsed call[^sgl-tool-parser].

## Offline engine API

- Construct `sgl.Engine(model_path=...)`, apply the tokenizer chat template with `tools`, and generate with `skip_special_tokens: False` preserved[^sgl-tool-parser].
- Convert tool dicts to `Tool(type, Function(name, description, parameters))` objects, then call `FunctionCallParser(tools=tools, tool_call_parser=...).parse_non_stream(generated_text)` to get `normal_text` and `calls` (`ToolCallItem` entries with `name` and `parameters`)[^sgl-tool-parser].
- For the `gpt-oss` parser, add `"no_stop_trim": True` so the tool-call `<call>` token is not trimmed[^sgl-tool-parser].
- Finish with `llm.shutdown()`[^sgl-tool-parser].

## Tool choice mode

SGLang supports OpenAI's `tool_choice` parameter using EBNF grammar to constrain tool calling[^sgl-tool-parser]:

- `tool_choice="required"` forces the model to call at least one tool[^sgl-tool-parser].
- `tool_choice={"type": "function", "function": {"name": "specific_function"}}` forces a call to that specific function[^sgl-tool-parser].
- Tool choice is fully supported with the XGrammar backend, which is the default grammar backend (`--grammar-backend xgrammar`), but may not be fully supported with other backends such as Outlines[^sgl-tool-parser].

## Pythonic tool-call format

Some Llama models emit calls as Python code rather than JSON[^sgl-tool-parser]:

```python
[get_current_weather(city="San Francisco", state="CA", unit="celsius")]
```

- Output is a Python list of calls with Python-literal arguments; multiple calls can appear in the same list[^sgl-tool-parser].
- Enable with `--tool-call-parser pythonic`, preferably with the improved model template such as `--chat-template=examples/chat_template/tool_chat_template_llama4_pythonic.jinja`, because the template supplies the special tokens, message boundaries such as `<|eom|>`, and call delimiters the model expects; without it, tool calling may fail or be inconsistent[^sgl-tool-parser].
- Without a chat template, enforce the format with explicit system plus user instructions and examples, e.g. telling `Llama-3.2-1B-Instruct` to always respond only with a Python list and never JSON, variables, or other formats[^sgl-tool-parser].
- The model may still default to JSON if heavily fine-tuned on that format; without a chat template, prompt engineering with examples is the only way to raise the chance of pythonic output[^sgl-tool-parser].
- The source notes this feature is still under development on Blackwell[^sgl-tool-parser].

## Adding a new model

1. Update `TOOLS_TAG_LIST` in `sglang/srt/function_call_parser.py` with the model's tool tags; currently listed tags are `<|plugin|>`, `<function=`, `<tool_call>`, `<|python_tag|>`, and `[TOOL_CALLS]`[^sgl-tool-parser].
2. Create a new detector class inheriting from `BaseFormatDetector` to handle that model's function-call format[^sgl-tool-parser].
3. Add the new detector to the `MultiFormatParser` class that manages all format detectors[^sgl-tool-parser].

## Relationships

- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — advanced-features map; this tool-parser page is an unlisted `advanced_features/` source outside that map's listed entries.
- Uses [SGLang Structured Outputs](sglang-structured-outputs.md) — `tool_choice` is implemented with EBNF grammar and is fully supported on the default XGrammar grammar backend.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical launch reference for `--tool-call-parser`, `--chat-template`, and `--grammar-backend` flags used here.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — companion parser family for thinking models; Kimi K2 thinking needs `--tool-call-parser kimi_k2` for tool use, and both families define a `gpt-oss` channel-aware parser.
- Uses [vLLM Tool Calling](vllm-tool-calling.md) — vLLM analogue with named, auto, required, and none tool-choice modes plus model-specific parsers and templates.

## Coverage limits

- Local chat-template paths under `examples/chat_template/tool_chat_template_*.jinja` and implementation paths `sglang/srt/function_call_parser.py`, `BaseFormatDetector`, and `MultiFormatParser` were treated as identifiers and not inspected[^sgl-tool-parser].
- `sglang.test.doc_patch.launch_server_cmd`, `sglang.utils.wait_for_server`, `print_highlight`, `terminate_process`, `sgl.Engine`, `FunctionCallParser`, `Tool`, `Function`, and `AutoTokenizer` helpers were not independently verified beyond this source[^sgl-tool-parser].
- OpenAI function-calling docs and Meta zero-shot function-calling prompt-format docs were treated as identifiers and not fetched[^sgl-tool-parser].
- Worked OpenAI, native, offline, tool-choice, and pythonic examples use a `qwen25` parser name for `Qwen/Qwen2.5-7B-Instruct` that does not appear in the supported-parsers table, which lists `qwen` and `qwen3_coder`; the source does not explain whether this is a versioned alias or a table gap[^sgl-tool-parser].

[^sgl-tool-parser]: Tool Parser — `../raw/sglang/advanced_features/tool_parser.mdx`.
