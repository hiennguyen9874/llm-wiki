---
type: Concept
title: LongCat-2.0 evaluation, deployment, and release limits
description: LongCat-2.0’s card reports strong agentic, coding, search, and foundational scores and GPU/NPU deployment paths, but the results are largely in-house and the supplied artifact lacks reproducible configurations and end-to-end serving evidence.
tags: [longcat, evaluation, deployment, agentic-systems, safety, licensing]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:01:02Z }
sources:
  - id: longcat-2-card-2026
    resource: ../raw/LongCat-2.0.md
    title: LongCat-2.0 model card
---

# LongCat-2.0 evaluation, deployment, and release limits

Meituan’s LongCat-2.0 model card reports results across code-agent, general-agent, and foundational benchmarks, and directs GPU deployment to an SGLang cookbook and NPU deployment to an SGLang-FluentLLM guide. Scores without an asterisk are said to be measured in-house with a unified harness; asterisks denote values cited from other vendors’ official reports. The card supplies neither the harness nor deployment measurements, so it supports release claims rather than independent capability or efficiency conclusions.[^longcat-2-card-2026]

## Reported evaluation

The card reports 70.8 on Terminal-Bench 2.1, 59.5 on SWE-bench Pro, and 77.3 on SWE-bench Multilingual. Its general-agent entries are 73.2 on FORTE, 79.9 on BrowseComp, and 78.8 on RWSearch. Listed foundational scores include 90.0 on IFEval, 83.8 on Writing Bench, 81.8 on IMO-AnswerBench, and 88.9 on GPQA-diamond.[^longcat-2-card-2026]

The same table compares LongCat with named Gemini, GPT, and Claude systems, but most comparator values are marked as cited from their official reports. Even the unstarred LongCat scores cannot be read as a controlled cross-provider ranking: the source does not provide prompt formats, model versions, tool environments, reasoning budgets, decoding settings, run dates, scoring code, variance, or contamination controls.[^longcat-2-card-2026]

## Deployment and interface

The card states that LongCat-2.0 can run on GPU and NPU platforms, linking external SGLang and SGLang-FluentLLM documentation. Those guides were not included in the raw artifact, so supported devices, resource requirements, runtime versions, precision, concurrency, context envelope, and throughput are unverified here.[^longcat-2-card-2026]

Its Transformers example loads the tokenizer with `trust_remote_code=True` and applies the supplied chat template to messages and JSON-schema-like function tools. It exposes `enable_thinking` and `save_reasoning_content` controls. The shown tool-call representation uses an `arguments` dictionary rather than the string convention common in OpenAI-compatible tool schemas; integration code should follow the checkpoint template rather than assume wire compatibility.[^longcat-2-card-2026]

## License and usage boundary

The card releases model weights and repository contributions under MIT, while expressly withholding rights to Meituan trademarks and patents. It says the model has not been designed or comprehensively evaluated for every downstream use and assigns developers responsibility for accuracy, safety, fairness, data protection, content safety, and applicable-law compliance in sensitive or high-risk deployments.[^longcat-2-card-2026]

## Relationships

- **Evaluates and releases:** [LongCat-2.0 sparse-attention and embedding architecture](longcat-2-0-sparse-attention-and-embedding-architecture.md).
- **Can use:** [LLM inference serving stack](llm-inference-serving-stack.md); the linked runtimes are external and were not inspected.[^longcat-2-card-2026]
- **Uses an interface related to:** [Kimi K3 XTML chat and tool encoding](kimi-k3-xtml-chat-and-tool-encoding.md). Both expose structured tool use through a tokenizer template, but their encodings and compatibility claims are source-specific.

## Evidence limits

This synthesis is bounded to a vendor-authored model card. The benchmark chart SVG and all linked external deployment and technical-blog resources were unavailable locally, and no model execution, weight inspection, safety evaluation, or benchmark reproduction was performed. The table and prose were inspected; the missing chart was not used for any additional claim.[^longcat-2-card-2026]

[^longcat-2-card-2026]: Meituan LongCat team, “LongCat-2.0,” [model card](../raw/LongCat-2.0.md), Evaluation Results, Deployment, Chat Template, License Agreement, and Usage Considerations.
