---
type: Concept
title: DeepSeek-V3.2 post-training, agentic synthesis, and evaluation limits
description: DeepSeek-V3.2 combines specialist distillation, mixed GRPO, persistent tool-use reasoning, and real and synthetic agent environments, with author-reported gains bounded by internal environments, context management, and token cost.
tags: [deepseek-v3-2, post-training, grpo, agents, tool-use, evaluation, limitations]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T16:27:51Z }
sources:
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
---

# DeepSeek-V3.2 post-training, agentic synthesis, and evaluation limits

DeepSeek-V3.2’s reported post-training distils thinking and non-thinking data from task specialists, then uses a single mixed Group Relative Policy Optimization (GRPO) stage for reasoning, agentic, and alignment tasks. Its agent recipe retains reasoning across tool-result turns, trains on real and synthesized environments, and reports strong agent scores; those results remain author-run, framework-sensitive, and dependent on explicit context-management interventions.[^deepseek-v3-2-2025]

## Specialist distillation and mixed RL

The authors fine-tune domain specialists from a shared V3.2 base for writing, general QA, mathematics, programming, logical reasoning, general agents, coding agents, and search agents, each in thinking and non-thinking modes. Specialist-generated data trains the final checkpoint; the report says later RL closes the remaining specialist-versus-distilled gap. The final mixed GRPO stage uses rule-based outcome rewards, a length penalty, and language-consistency reward for reasoning and agent tasks, and a per-prompt-rubric generative reward model for general tasks.[^deepseek-v3-2-2025]

The report also introduces a reasoning-focused V3.2-Speciale variant, trained with a weaker length penalty and DeepSeekMath-V2 data and rewards for proof capability. Its reported gains use longer outputs: for example, the supplied table reports 96.0 AIME 2025 Pass@1 at 23K output tokens, versus 93.1 at 16K for V3.2 Thinking. The same paper explicitly identifies lower token efficiency than Gemini-3.0-Pro as a deployment limitation.[^deepseek-v3-2-2025]

## Tool-use trajectories and agent data

When only tool messages are added, the policy retains historical reasoning; when a new user message arrives, it removes reasoning but retains tool calls and tool results. This avoids re-reasoning after each tool output, but makes thinking mode less compatible with frameworks that represent tool interactions as user messages; the authors recommend non-thinking mode for those frameworks.[^deepseek-v3-2-2025]

The training mix contains real code, search, and notebook environments as well as synthesized general-agent environments. For the latter, an environment-synthesis agent builds data and tool functions, generates tasks plus solution and verifier functions, then raises difficulty while ensuring the solution accesses data only through the tool interface. After RL filtering for non-zero pass@100, the paper reports 1,827 environments and 4,417 general-agent tasks. Its synthetic-only non-thinking RL plot improves over the cited SFT and code/search-only baselines on listed Tau2Bench, MCP-Mark, and MCP-Universe settings; this is evidence from the authors’ training and evaluation pipeline, not proof of transfer to arbitrary tools or users.[^deepseek-v3-2-2025]

## Reported evaluation and context limit

The main table uses 128K context and temperature 1.0. MCP-Universe and MCP-Mark use the authors’ internal environments because their search and Playwright environments may differ from the official settings. On BrowseComp, the report gives V3.2 Thinking 51.4 without search-context management and 67.6 with it; it notes that over 20% of cases exceed the model’s 128K context limit.[^deepseek-v3-2-2025]

For such overflow, the paper triggers a new strategy after 80% of the window: summarize and restart, discard the first 75% of tool history, or discard all tool history. On its BrowseComp curve, discard-all reaches 67.6 with substantially fewer real steps than its parallel-fewest-step comparison at similar score, while the summary strategy reaches 60.2 at 364 average steps. These are search-task observations; discarding history can lose relevant evidence, and neither result establishes a generally optimal serial/parallel allocation policy.[^deepseek-v3-2-2025]

## Limitations

- The reported model comparisons mix author evaluations, API-accessed systems, internal agent environments, bespoke prompts, and framework-specific execution; they are not independent capability rankings.[^deepseek-v3-2-2025]
- The paper reports that redundant self-verification can overrun context, especially on MCP-Mark GitHub and Playwright tasks; its own context management is therefore part of the reported performance boundary.[^deepseek-v3-2-2025]
- Training data, specialist checkpoints, reward models, environments, synthesized task generators, and full evaluation harnesses are not available in this bundle for independent reproduction or leakage assessment.[^deepseek-v3-2-2025]

## Relationships

- **Uses:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) throughout sparse post-training.[^deepseek-v3-2-2025]
- **Applies:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) with stabilization procedures documented in the V3.2 report.[^deepseek-v3-2-2025]
- **Extends:** [ReAct reasoning-and-acting agent loop](react-reasoning-and-acting-agent-loop.md) with a model-specific policy for retaining or deleting reasoning across message roles.[^deepseek-v3-2-2025]
- **Applies:** [Test-time scaling strategies and verification limits](test-time-scaling-strategies-and-verification-limits.md) through serial context management and a parallel-trajectory comparator.[^deepseek-v3-2-2025]

[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” arXiv:2512.02556v1, [source](../raw/arXiv-2512.02556v1/main.tex), Sections 3–4 and Appendix; included [main evaluation table](../raw/arXiv-2512.02556v1/tables/eval_main.tex), [non-thinking table](../raw/arXiv-2512.02556v1/tables/nonthink.tex), [synthetic-task table](../raw/arXiv-2512.02556v1/tables/synthesis-eval.tex), [synthetic-RL figure](../raw/arXiv-2512.02556v1/figures/synthesis-rl-plot.png), and [search-context figure](../raw/arXiv-2512.02556v1/figures/search.pdf).
