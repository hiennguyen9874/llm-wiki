---
type: Concept
title: Qwen3.8-2.4T-A95B release interface and evaluation limits
description: The Qwen3.8-2.4T-A95B card specifies a text-only, thinking-required interface with adjustable reasoning effort and reports broad author-run capability results whose harness and comparability limits constrain deployment conclusions.
tags: [qwen3-8, model-card, reasoning, agentic-systems, evaluation, deployment]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T04:30:52Z }
sources:
  - id: qwen38-card
    resource: ../raw/Qwen3.8-2.4T-A95B/README.md
    title: Qwen3.8-2.4T-A95B model card
---

# Qwen3.8-2.4T-A95B release interface and evaluation limits

The supplied Qwen3.8-2.4T-A95B model card describes a text-only, post-trained causal LM whose interactions require thinking mode: responses begin with reasoning in `<think>…</think>` before final output. It exposes `reasoning_effort` (`xhigh`, `medium`, or `low`) and enables `preserve_thinking` by default. The same card reports broad coding, agentic, general-capability, and long-context results, but those are author-reported measurements with varied harnesses, comparison conditions, and incomplete deployment information.[^qwen38-card]

## Interface and operating guidance

The card says multimodal inputs are unsupported and thinking cannot be disabled for this checkpoint. Its OpenAI-compatible chat-completions example passes `enable_thinking` and `preserve_thinking` through `chat_template_kwargs`; it notes that Qwen Cloud instead expects those fields directly in `extra_body`. This is integration guidance, not evidence that every compatible server implements the fields identically.[^qwen38-card]

For generation, the card recommends temperature 1.0, top-p 0.95, top-k 20, min-p 0, zero presence penalty, and repetition penalty 1.0, while noting framework-dependent parameter support. It recommends up to 262,144 reasoning tokens and 131,072 final-output tokens when a serving framework separates the two budgets, within its stated one-million-token context setting. These are vendor recommendations, not tested operating guarantees in the supplied bundle.[^qwen38-card]

The checkpoint has a native 262,144-token configured position limit; the card describes context as extensible to 1,010,000 tokens but does not disclose the extension method, quality measurement, memory cost, or serving configuration.[^qwen38-card]

## Reported evaluation evidence

The card’s table reports Qwen3.8-Max, which it describes as the official version based on this checkpoint but with additional features, alongside other models. It reports, for example, 86.6 on Terminal Bench 2.1, 67.7 on SWE-bench Pro, 93.0 on PaperBench, 70.2 on SkillsBench, 92.6 on GPQA Diamond, and 92.9 on MRCR v2 256K. These figures are evidence for the card’s stated evaluation, not direct measurements of the supplied local checkpoint, because the table column is Qwen3.8-Max rather than Qwen3.8-2.4T-A95B.[^qwen38-card]

Several disclosed conditions differ across benchmarks: Terminal Bench uses Claude Code with average-at-10 and a five-hour timeout; SWE-bench Pro uses Claude Code, temperature 1.0, top-p 0.95, and 256K context; some competing Terminal Bench results are best published scores from other harnesses. Other entries use Qwen-Agent, OpenCode, model judges, proprietary or in-house benchmarks, different sample counts, and selected public subsets. The table therefore supports task-specific author claims, not a controlled universal ranking among the displayed models.[^qwen38-card]

## Relationships

- **Describes:** [Qwen3.8-2.4T-A95B checkpoint architecture](qwen3-8-2-4t-a95b-checkpoint-architecture.md)’s text-only checkpoint interface and stated context behavior.[^qwen38-card]
- **Uses:** [Test-time compute allocation](test-time-compute-allocation.md) operationally through its discrete `reasoning_effort` control, without establishing the policy that selects a level.[^qwen38-card]
- **Qualified by:** [Test-time scaling strategies and verification limits](test-time-scaling-strategies-and-verification-limits.md): the card’s longer-reasoning and agentic-task claims do not establish faithful reasoning or outcome verification.[^qwen38-card]

## Evidence limits

This source is a vendor model card and its cited benchmark table, not independent replication. The raw directory contains no weights, evaluation scripts, prompts, model-judge settings, per-task results, variance, safety evaluation, pricing, hardware configuration, throughput, or end-to-end serving benchmark.

The card explicitly distinguishes Qwen3.8-Max from this checkpoint: Max adds vision input, non-thinking support, default one-million-token context, and built-in tools. Those Max-only capabilities should not be attributed to Qwen3.8-2.4T-A95B.[^qwen38-card]

[^qwen38-card]: Qwen Team, “Qwen3.8-2.4T-A95B,” [model card](../raw/Qwen3.8-2.4T-A95B/README.md), Qwen3.8 Highlights, Benchmark Results and notes, API Usage, and Best Practices.
