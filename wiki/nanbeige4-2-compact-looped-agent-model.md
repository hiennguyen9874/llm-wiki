---
type: Concept
title: Nanbeige4.2 compact looped agent model
description: Nanbeige4.2-3B is a source-reported 3B non-embedding-parameter agent model that applies its transformer stack twice, combines long-context SFT with multi-stage RL, and reports strong agentic benchmarks against larger open models.
tags: [agent-training, language-models, parameter-sharing, recurrent-depth, tool-use]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:47:53Z }
sources:
  - id: nanbeige2026compactagent
    resource: ../raw/arXiv-2607.22083v2/main.tex
    title: "Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model"
  - id: nanbeige42modelcard
    resource: ../raw/Nanbeige4.2-3B.md
    title: "Nanbeige4.2-3B model card"
---

# Nanbeige4.2 compact looped agent model

Nanbeige4.2-3B is a 3B non-embedding-parameter model whose authors train a two-pass, full-stack Looped Transformer from scratch on 28T tokens, then apply long-context SFT and a multi-stage RL pipeline. In the authors' evaluations it outperforms their Qwen3.5-9B and Gemma4-12B comparators on the listed general-agent and code-agent benchmarks, but the architecture, data, scaffolds, and evaluation choices all change together, so those results do not establish which component caused the gains.[^nanbeige2026compactagent]

## Architecture and pretraining

- Hidden states traverse the shared Transformer stack a second time. The authors report that two passes offered their best tested trade-off: about 75% of a standard transformer's token efficiency with a significant capacity gain. More passes gave marginal improvement but slower, less stable optimization.[^nanbeige2026compactagent]
- Training the looped architecture from scratch reportedly outperformed conversion of a pretrained standard Transformer by upcycling. A KV-cache-sharing variant halved cache use but had consistently weaker gains in the authors' experiments, so the released configuration retains separate pass caches.[^nanbeige2026compactagent]
- The pretraining mixture totals 28T tokens and increases math, code, and synthetic-QA sampling weights, with a small amount of agentic trajectory data. The reported base-model table exceeds three listed 4B non-embedding-parameter comparators on six selected benchmarks; this does not separate data-mixture effects from recurrence.[^nanbeige2026compactagent]

## Post-training pipeline

- SFT expands maximum context from 64K to 128K to 256K tokens and shifts supervised target tokens from 82.7% reasoning / 5.7% agentic at 64K to 22.4% reasoning / 68.9% agentic at 256K. Assistant turns assessed as unreliable are masked out of the SFT loss while their observations remain in context for later recovery.[^nanbeige2026compactagent]
- Two-stage RLHF first covers Think and then primarily Non-Think responses. In three selected Think-mode evaluations, the authors report lower bad-case rates and shorter output alongside higher accuracy after the second stage; this observational checkpoint comparison does not establish cross-task or cross-mode generalization.[^nanbeige2026compactagent]
- Reasoning RL applies [difficulty-aware reasoning length control](difficulty-aware-reasoning-length-control.md). Agentic RL combines outcome rewards with action-centric process rubrics for tool-call accuracy and per-turn information gain, selecting shorter, relatively easy tasks based on the reasoning-RL model's pass@8 estimates. On its rapid-validation tasks, the source reports an approximately 20% reduction in normalized single-turn error and a peak score increase from 66.0 to 71.0.[^nanbeige2026compactagent]

## Evaluation boundary

The model report uses varying harnesses, search backends, judges, timeouts, and reasoning-context handling across benchmarks; several measures are judge-scored or in-house. Its OpenClaw comparison states that all models use the same scaffold, tools, and protocol, but the larger cross-benchmark results remain source-reported, non-independent evidence rather than a general size-normalized ranking.[^nanbeige2026compactagent]

## Deployment guidance

- The model card specifies a 262,144-token context window. Its chat template enables reasoning by default; it recommends retaining prior reasoning only for multi-turn tool, office, and code-agent workflows, and recommends XML-formatted tool calls when tools are passed.[^nanbeige42modelcard]
- The card recommends temperature 1.0 with up to 65,536 generated tokens for agentic/tool-use tasks, and temperature 0.6 with up to 131,072 generated tokens for reasoning/chat. These are author guidance, not independently validated operating limits.[^nanbeige42modelcard]
- It documents Transformers (with remote code), SGLang, vLLM, llama.cpp, and Ollama deployment paths. SGLang, vLLM, llama.cpp, and Ollama instructions reference Nanbeige branches or parsers, so they should be treated as release-specific rather than general compatibility claims.[^nanbeige42modelcard]

> The local model card references benchmark-image assets that are not present alongside this raw file. This compilation covers its textual tables and instructions; it does not independently inspect those figures.

## Relationships

- Uses: [Virtual logical depth scaling](virtual-logical-depth-scaling.md) — both reuse Transformer weights across extra depth, while this report applies a two-pass full stack in a production-oriented training run.
- Contrasts with: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) — Nanbeige4.2 uses fixed whole-stack recurrence and separate caches rather than token-specific routed depth.
- Uses: [Execution-grounded repository-to-trajectory synthesis](execution-grounded-repository-to-trajectory-synthesis.md), [Hybrid environments for tool-use trajectory synthesis](hybrid-environments-for-tool-use-trajectory-synthesis.md), and [Artifact-centric office workflow task synthesis](artifact-centric-office-workflow-task-synthesis.md) as its reported post-training data pipelines.

[^nanbeige2026compactagent]: Nanbeige LLM Lab and Boss Zhipin, *Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model*, source manuscript, abstract, §§1--4, appendix, and figures (arXiv:2607.22083v2, 2026).
[^nanbeige42modelcard]: Nanbeige, *Nanbeige4.2-3B model card*, model repository README, §§1--3 (local copy).