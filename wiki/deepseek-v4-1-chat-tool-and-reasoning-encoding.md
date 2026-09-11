---
type: Concept
title: DeepSeek-V4.1 chat, tool, and reasoning encoding
description: DeepSeek-V4.1 uses a standalone non-Jinja prompt protocol with numeric reasoning effort, spaced DSML tool tags, mid-conversation system turns, reasoning-retention rules, tool namespaces, and ordered image placeholders.
tags: [deepseek-v4-1, prompt-format, tool-calling, reasoning-effort, multimodal, dsml]
status: draft
created: 2026-09-11
generated: { by: llm-wiki-agent/1, at: 2026-09-11T05:26:56Z }
sources:
  - id: deepseek-v41-encoding-readme
    resource: ../raw/DeepSeek-V4.1-Flash/encoding/README.md
    title: DeepSeek-V4.1 text and vision encoding
  - id: deepseek-v41-encoding-tests
    resource: ../raw/DeepSeek-V4.1-Flash/encoding/test_encoding.py
    title: DeepSeek-V4.1 encoding tests
---

# DeepSeek-V4.1 chat, tool, and reasoning encoding

DeepSeek-V4.1 has no Jinja chat template in the release bundle. Its standalone Python protocol renders system, user, assistant, tool, reminder, reasoning, and image content; parses well-formed completions back to structured messages; and adds three declared changes over V4: numeric reasoning effort, spaced DSML tool tags, and mid-conversation system turns.[^deepseek-v41-encoding-readme]

## Reasoning modes and retention

In thinking mode, an integer effort from 1 to 100 is rendered once at conversation index 0 as a system prefix. Aliases map `low` to 50, `high` to 75, and `max` to 100; the default is 75. In chat mode the assistant prefix immediately closes reasoning with `</think>`, and no effort prefix is emitted. Tests reject out-of-range integers, unknown aliases, booleans, and floats.[^deepseek-v41-encoding-readme][^deepseek-v41-encoding-tests]

With the default `drop_thinking=True`, reasoning from assistant turns before the latest ordinary user message is removed. When tools are present, the encoder disables that dropping so intermediate tool-use reasoning remains in context. This is a protocol/context policy, not evidence that visible reasoning faithfully describes model internals.[^deepseek-v41-encoding-readme]

## Tool protocol

V4.1’s DSML tags contain a space after the DSML marker—for example `<｜DSML｜ calls>`, `<｜DSML｜ invoke>`, and `<｜DSML｜ parameter>`—and the parser rejects the older unspaced V4 spelling. Parameters explicitly mark raw strings versus JSON values. Tool results are merged into a subsequent user turn as `<tool_result>` blocks and sorted to match the preceding assistant call order.[^deepseek-v41-encoding-readme][^deepseek-v41-encoding-tests]

Optional namespaces qualify tools as `namespace::name` in rendered schemas and calls, while parsed output separates the namespace and function name again. A mid-conversation system message receives its own `<｜System｜>` token and, when it is the final input turn, triggers an assistant generation header.[^deepseek-v41-encoding-readme][^deepseek-v41-encoding-tests]

## Images and auxiliary tasks

Interleaved image blocks become ordered `<｜deepseek_image｜>` placeholders plus a parallel media record; pixel loading and expansion happen later in the inference image processor. The encoder also supports quick-instruction tokens for search routing, title generation, query generation, authority/domain classification, and URL-reading decisions.[^deepseek-v41-encoding-readme]

## Relationships

- **Interface for:** [DeepSeek-V4.1-Flash architecture and pretraining](deepseek-v4-1-flash-architecture-and-pretraining.md).
- **Operational context for:** [DeepSeek-V4.1-Flash post-training, evaluation, and interface limits](deepseek-v4-1-flash-post-training-evaluation-and-interface-limits.md).
- **Revises:** the V4 DSML behavior described in [DeepSeek-V4 post-training and evaluation limits](deepseek-v4-post-training-and-evaluation-limits.md).

## Evidence limits

The source includes a readable implementation and fixture-based tests, but this ingestion did not claim production-parser robustness or compatibility with external API servers. The parser explicitly assumes well-formed model output. Numeric effort encoding proves that a control value is placed in the prompt, not that intermediate effort values produce calibrated or monotonic compute and accuracy.[^deepseek-v41-encoding-readme]

[^deepseek-v41-encoding-readme]: DeepSeek-AI, “DeepSeek-V4.1 text and vision encoding,” [encoding documentation](../raw/DeepSeek-V4.1-Flash/encoding/README.md), V4.1 changes, Message format, Reasoning effort, Tool calling, Tool namespaces, and Tests.

[^deepseek-v41-encoding-tests]: DeepSeek-AI, “DeepSeek-V4.1 encoding tests,” [test source](../raw/DeepSeek-V4.1-Flash/encoding/test_encoding.py), reasoning-effort, system-token, DSML, namespace, image, and round-trip tests.
