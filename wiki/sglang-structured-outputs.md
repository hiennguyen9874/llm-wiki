---
type: Concept
title: SGLang Structured Outputs
description: Guaranteed JSON-schema, regex, EBNF, and structural-tag generation across OpenAI, native, and offline APIs with selectable XGrammar, Outlines, and llguidance backends.
tags: [sglang, structured-outputs, constrained-decoding]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:14:43Z }
sources:
  - id: sgl-structured-outputs
    resource: ../raw/sglang/advanced_features/structured_outputs.mdx
    title: Structured Outputs
---

SGLang guarantees model output follows one JSON-schema, regex, EBNF, or structural-tag constraint per request, served by a selectable XGrammar, Outlines, or llguidance grammar backend across OpenAI-compatible, native `/generate`, and offline engine APIs[^sgl-structured-outputs].

## Constraints and backends

- Constraint types are JSON schema, regular expression, and EBNF; only one of `json_schema`, `regex`, or `ebnf` can be specified for a request[^sgl-structured-outputs].
- Grammar backends and coverage[^sgl-structured-outputs]:

| Backend | JSON schema | Regex | EBNF | Selection |
| --- | --- | --- | --- | --- |
| XGrammar | yes | yes | yes | default when no backend is specified |
| Outlines | yes | yes | no | `--grammar-backend outlines` |
| llguidance | yes | yes | yes | `--grammar-backend llguidance` |

- The source recommends XGrammar for better performance and utility; XGrammar currently uses the GGML BNF format[^sgl-structured-outputs].
- Prompting advice: explicitly instruct the model to use the desired format, for example stating the expected JSON shape in the prompt, to improve output quality[^sgl-structured-outputs].

## OpenAI-compatible API

- JSON via Pydantic: define a model such as `CapitalInfo` with `name` and `population`, pass `CapitalInfo.model_json_schema()` as `response_format={"type": "json_schema", "json_schema": {"name": "foo", "schema": ...}}`, then validate the returned content with `model_validate_json`[^sgl-structured-outputs].
- JSON directly: pass an equivalent JSON Schema object through the same `response_format` shape[^sgl-structured-outputs].
- EBNF: pass the grammar as `extra_body={"ebnf": ebnf_grammar}`; the example constrains city and description output over London, Paris, Berlin, and Rome[^sgl-structured-outputs].
- Regex: pass `extra_body={"regex": ...}`, for example `"(Paris|London)"`[^sgl-structured-outputs].
- Structural tag with function-call triggers: pass `response_format={"type": "structural_tag", ...}` with `structures` entries carrying `begin`, JSON `schema`, and `end`, plus `triggers: ["<function="]`; the example defines `get_current_weather` and `get_current_date` structures[^sgl-structured-outputs].
- The source also documents the newer XGrammar structural-tag shape using `format: {"type": "triggered_tags", "triggers": [...], "tags": [{"begin": ..., "content": {"type": "json_schema", ...}, "end": ...}], "at_least_one": ..., "stop_after_first": ...}`[^sgl-structured-outputs].

## Native API and SRT (`/generate`)

- Build prompt text with the tokenizer chat template, then POST to `/generate` with one constraint key inside `sampling_params`[^sgl-structured-outputs].
- JSON: `sampling_params` carries `json_schema` as a JSON-encoded Pydantic-derived or direct schema, with `temperature: 0` and `max_new_tokens: 64` in the examples[^sgl-structured-outputs].
- EBNF: `sampling_params` carries `ebnf`, with `max_new_tokens: 128`, `temperature: 0`, and `n: 3` in the example[^sgl-structured-outputs].
- Regex: `sampling_params` carries `regex`, for example `"(France|England)"`[^sgl-structured-outputs].
- Structural tag: `sampling_params` carries `structural_tag` as a JSON-encoded object in either the legacy `structures` plus `triggers` shape or the newer `format.triggered_tags` shape[^sgl-structured-outputs].

## Offline engine API

- Construct `sgl.Engine(model_path="meta-llama/Meta-Llama-3.1-8B-Instruct", grammar_backend="xgrammar")` and finish with `llm.shutdown()`[^sgl-structured-outputs].
- Generate with `llm.generate(prompts, sampling_params)` where `sampling_params` carries one constraint key: `json_schema`, `ebnf`, `regex`, or `structural_tag`[^sgl-structured-outputs].
- JSON examples use capital name and population prompts for China, France, and Ireland with `temperature: 0.1`, `top_p: 0.95`, and either a Pydantic-derived schema validated with `model_validate_json` or a direct JSON Schema[^sgl-structured-outputs].
- EBNF and regex examples reuse the same capital-city grammar and `(France|England)` pattern family with `temperature: 0.8` and `top_p: 0.95`; structural-tag examples reuse the same weather and date function structures in both legacy and `triggered_tags` shapes[^sgl-structured-outputs].

## Relationships

- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — Advanced Features map whose Structured Outputs entry this concept implements.
- Uses [SGLang Structured Outputs for Reasoning Models](sglang-structured-outputs-reasoning.md) — reasoning-model variant that leaves thinking spans unconstrained and constrains only the final output via `--reasoning-parser`.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical launch reference documenting `--grammar-backend xgrammar|outlines|llguidance|none`.
- Uses [vLLM Structured Outputs](vllm-structured-outputs.md) — vLLM analogue with choice, regex, JSON, grammar, and structural-tag constraints for online and offline inference.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — parser setup needed when combining constrained generation with thinking models.

## Coverage limits

- External regex, EBNF, XGrammar, Outlines, llguidance, GGML BNF, Pydantic, and XGrammar structural-tag tutorial links were treated as identifiers and not fetched[^sgl-structured-outputs].
- Test and runtime helpers in examples — `sglang.test.doc_patch.launch_server_cmd`, `sglang.utils.wait_for_server`, `print_highlight`, `terminate_process`, `sgl.Engine`, and `AutoTokenizer` chat-template calls — were not independently verified beyond this source[^sgl-structured-outputs].
- Source structural-tag delimiters appear HTML-escaped as `&lt;function=` and `&lt;/function&gt;`; they are recorded here as `<function=` and `</function>`[^sgl-structured-outputs].

[^sgl-structured-outputs]: Structured Outputs — `../raw/sglang/advanced_features/structured_outputs.mdx`.
