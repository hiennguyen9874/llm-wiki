---
type: Concept
title: SGLang Structured Outputs for Reasoning Models
description: Free-form reasoning with constrained final output for thinking models via --reasoning-parser across OpenAI, native, and offline APIs.
tags: [sglang, structured-outputs, reasoning]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:14:43Z }
sources:
  - id: sgl-reasoning-structured
    resource: ../raw/sglang/advanced_features/structured_outputs_for_reasoning_models.mdx
    title: Structured Outputs For Reasoning Models
---

SGLang allows free-form text inside reasoning sections while enforcing grammar constraints on the final output, enabled by launching the server with `--reasoning-parser`, which determines the `think_end_token` such as `</think>`[^sgl-reasoning-structured].

## Mechanism and server launch

- Reasoning models denote thinking spans with special tokens such as `<think>...</think>`; SGLang disables grammar restrictions inside those spans and enforces them on the rest of the output[^sgl-reasoning-structured].
- Enable with the `--reasoning-parser` launch flag; the source repeats this flag sentence twice with the same meaning[^sgl-reasoning-structured].
- OpenAI-compatible usage specifies the `--grammar-backend` and `--reasoning-parser` options[^sgl-reasoning-structured].
- Example launch in the source[^sgl-reasoning-structured]:

```bash
python -m sglang.launch_server --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --host 0.0.0.0 --reasoning-parser deepseek-r1 --log-level warning
```

## Supported models

Both listed series wrap reasoning content in `<think>` and `</think>` tags[^sgl-reasoning-structured]:

| Model series | Notes |
| --- | --- |
| DeepSeek R1 series | Reasoning content wrapped with `<think>` / `</think>` |
| QwQ | Reasoning content wrapped with `<think>` / `</think>` |

## OpenAI-compatible API

- JSON Schema via Pydantic: define a `BaseModel` such as `CapitalInfo` with `name` and `population`, pass `CapitalInfo.model_json_schema()` as `response_format={"type": "json_schema", "json_schema": {"name": "foo", "schema": ...}}`[^sgl-reasoning-structured].
- JSON Schema directly: pass an equivalent JSON Schema object with `properties.name`, `properties.population`, and `required: ["name", "population"]` through the same `response_format` shape[^sgl-reasoning-structured].
- EBNF: pass the grammar in `extra_body={"ebnf": ebnf_grammar}`; the example constrains city/description output over London, Paris, Berlin, and Rome[^sgl-reasoning-structured].
- Regex: pass `extra_body={"regex": "(Paris|London)"}`; the example asks for the capital of France[^sgl-reasoning-structured].
- Structural tag: pass `response_format={"type": "structural_tag", ...}` with `structures` entries carrying `begin`, JSON `schema`, and `end`, plus `triggers: ["<function="]`; the example defines `get_current_weather` and `get_current_date` function structures[^sgl-reasoning-structured].
- Read split output from `response.choices[0].message.reasoning_content` plus `response.choices[0].message.content`[^sgl-reasoning-structured].

## Native API and SRT (`/generate`)

- Workaround: set `require_reasoning: True` to ensure the model thinks before generating structured output; this is not required for the chat-completion API[^sgl-reasoning-structured].
- JSON via Pydantic or direct schema: build prompt text with the tokenizer chat template, then POST to `/generate` with `require_reasoning: True` and `sampling_params` carrying `json_schema`, `temperature: 0`, and `max_new_tokens: 2048`[^sgl-reasoning-structured].
- EBNF: POST with `sampling_params` carrying `ebnf`, `temperature: 0`, `max_new_tokens: 2048`, and `n: 3` in the example[^sgl-reasoning-structured].
- Regex: POST with `sampling_params` carrying `regex` such as `(France|England)`[^sgl-reasoning-structured].
- Structural tag: POST with `sampling_params` carrying `structural_tag` as a JSON-encoded object with the same `structures` plus `triggers` shape as the OpenAI API[^sgl-reasoning-structured].
- The native JSON example splits returned `text` on `</think>` into reasoning versus final content for display[^sgl-reasoning-structured].

## Offline engine API

- Construct `sgl.Engine(model_path="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", reasoning_parser="deepseek-r1", grammar_backend="xgrammar")`[^sgl-reasoning-structured].
- Generate with `llm.generate(prompts, sampling_params)` where `sampling_params` carries one constraint key: `json_schema`, `ebnf`, `regex`, or `structural_tag`[^sgl-reasoning-structured].
- JSON examples cover both Pydantic-derived schema and direct JSON Schema for capital name/population prompts; EBNF and regex examples reuse the same capital-city grammars and patterns as the server APIs[^sgl-reasoning-structured].
- Shut down with `llm.shutdown()`[^sgl-reasoning-structured].

## Relationships

- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — shared `--reasoning-parser deepseek-r1` setup and `reasoning_content` plus `content` split; this page adds grammar-constrained final output on top of that separation.
- Uses [SGLang Structured Outputs](sglang-structured-outputs.md) — general JSON-schema, regex, EBNF, and structural-tag constraints and grammar backends; this page adds free-form reasoning spans on top of those constraints.
- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — advanced-features map covering the Structured Outputs entry.
- Uses [vLLM Structured Outputs](vllm-structured-outputs.md) — vLLM analogue with choice, regex, JSON, grammar, and structural-tag constraints for online and offline inference.
- Uses [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — vLLM analogue that separates reasoning from constrained content and documents `Reasoner` start/end handling for structured-output engines.

## Coverage limits

- Hugging Face collection/model links and Pydantic documentation links were treated as identifiers and not fetched[^sgl-reasoning-structured].
- Test and runtime helpers in examples — `sglang.test.doc_patch.launch_server_cmd`, `sglang.utils.wait_for_server`, `print_highlight`, `terminate_process`, and `sgl.Engine` — were not independently verified beyond this source[^sgl-reasoning-structured].
- Source `<think>` tags appear HTML-escaped as `&lt;think&gt;`; they are recorded here as `<think>` / `</think>`[^sgl-reasoning-structured].

[^sgl-reasoning-structured]: Structured Outputs For Reasoning Models — `../raw/sglang/advanced_features/structured_outputs_for_reasoning_models.mdx`.
