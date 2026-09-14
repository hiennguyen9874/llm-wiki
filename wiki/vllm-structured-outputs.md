---
type: Concept
title: vLLM Structured Outputs
description: Constrained generation via choice, regex, JSON schema, grammar, and structural tags for online and offline inference.
tags: [vllm, structured-outputs, inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: structured-outputs
    resource: ../raw/vllm/features/structured_outputs.md
    title: Structured Outputs
---

vLLM constrains generation to a choice list, regex, JSON schema, EBNF grammar, or JSON schema inside structural tags, served by `xgrammar` or `guidance` backends for both online OpenAI-compatible serving and offline `SamplingParams` inference[^structured-outputs].

## Backends

- Supported backends are `xgrammar` and `guidance`[^structured-outputs].
- Online serving enables structured outputs by default; select a backend with `vllm serve --structured-outputs-config.backend`, where `auto` chooses per request and a named backend accepts additional options documented in `vllm serve --help`[^structured-outputs].

## API migration

- Legacy request fields were removed in v0.12.0; migrate to `structured_outputs` or `StructuredOutputsParams`[^structured-outputs]:
  - `guided_json` -> `{"structured_outputs": {"json": ...}}`
  - `guided_regex` -> `{"structured_outputs": {"regex": ...}}`
  - `guided_choice` -> `{"structured_outputs": {"choice": ...}}`
  - `guided_grammar` -> `{"structured_outputs": {"grammar": ...}}`
  - `guided_whitespace_pattern` -> `{"structured_outputs": {"whitespace_pattern": ...}}`
  - `structural_tag` -> `{"structured_outputs": {"structural_tag": ...}}`
  - `guided_decoding_backend` -> remove the field.

## Online serving

- Applies to OpenAI Completions and Chat Completions APIs as extra request parameters[^structured-outputs].
- Constraint keys are `choice`, `regex`, `json`, `grammar`, and `structural_tag`; the complete parameter list is on the OpenAI-Compatible Server page, which was not ingested here[^structured-outputs].
- `choice` constrains output to exactly one listed string, for example `extra_body={"structured_outputs": {"choice": ["positive", "negative"]}}`[^structured-outputs].

## Constraint details

- `regex`: output follows the pattern; syntax depends on backend — `xgrammar`, `guidance`, and `outlines` use Rust-style regex while `lm-format-enforcer` uses Python `re`[^structured-outputs].
- `json`: supply a JSON Schema directly or derive it from a Pydantic model via `model_json_schema()`; OpenAI-style use is `response_format={"type": "json_schema", "json_schema": {"name": ..., "schema": ...}}`[^structured-outputs].
- Prompting tip: restating the JSON schema and field meanings in the prompt usually improves results[^structured-outputs].
- `grammar`: defines a context-free EBNF language such as restricted SQL, and is the most expressive but hardest option to author[^structured-outputs].
- `structural_tag`: enforces a JSON schema only within specified tags in otherwise free text[^structured-outputs].

## Reasoning interaction

- Structured outputs compose with reasoning parsers; any structured-output feature can be used with a reasoning model served with `--reasoning-parser`, with reasoning returned separately from constrained content[^structured-outputs].
- Qwen3 Coder with reasoning enabled may silently disable structured outputs when reasoning is not parsed into a separate `reasoning` field (`v0.11.2+`); explicitly opt in with `--structured-outputs-config.enable_in_reasoning=True`[^structured-outputs].

## Experimental automatic parsing

- The OpenAI client beta `client.beta.chat.completions.parse()` maps `response_format` Pydantic models to validated `message.parsed` objects; documented against `openai==1.54.4` and `meta-llama/Llama-3.1-8B-Instruct`[^structured-outputs].
- Supports nested Pydantic models, for example a `MathResponse` with `steps: list[Step]` plus `final_answer`[^structured-outputs].

## Offline inference

- Configure with `StructuredOutputsParams` inside `SamplingParams`, using the same `json`, `regex`, `choice`, `grammar`, and `structural_tag` keys as online serving[^structured-outputs].
- Example: `StructuredOutputsParams(choice=["Positive", "Negative"])` passed as `SamplingParams(structured_outputs=...)` to `llm.generate(...)`[^structured-outputs].

## Coverage limits

- The OpenAI-Compatible Server page, `examples/features/structured_outputs/README.md`, and `structured_outputs_offline.py` are referenced by the source but were not present in `raw/` and were not inspected[^structured-outputs].
- External `xgrammar`, `guidance`, Pydantic, JSON Schema, and OpenAI API links were treated as identifiers and not fetched[^structured-outputs].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — constraints apply both to `vllm serve` online requests and offline `LLM.generate` via `SamplingParams`.
- Uses [vLLM Reasoning Outputs](vllm-reasoning-outputs.md) — reasoning parsers separate thinking traces from constrained content, with explicit opt-in needed for Qwen3 Coder reasoning mode.

[^structured-outputs]: Structured Outputs — `../raw/vllm/features/structured_outputs.md`, full page.
