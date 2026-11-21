---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../AGENTS.md) for storage and maintenance rules.

## Concepts

- [Code mode for agent tool orchestration](code-mode-agent-tool-orchestration.md) — Programmatic batching of agent tools and a reported long-running coding-task cost comparison.
- [Compositional generalization in LM harnesses](compositional-generalization-in-lm-harnesses.md) — How context offloading, programmatic tools, and sub-calls can help language-model harnesses transfer learned strategies to new tasks.
- [Deep Agents interpreter and programmatic tool calling](deep-agents-interpreter.md) — A constrained QuickJS runtime for persistent agent state, allowlisted tool orchestration, and selective context return.
- [Prime Agent evaluation](prime-agent-evaluation.md) — Reported benchmark results, comparisons, and safety limits for the Prime Agent recursive harness.
- [Prime Agent harness](prime-agent.md) — A persistent recursive agent harness combining programmable execution, session orchestration, and revisable external state.
- [Prime Agent implementation](prime-agent-implementation.md) — A partial static inspection of Prime Agent's Rust workspace, Python kernel shim, and operational boundaries.
- [Prime Intellect RLM scaffold](prime-intellect-rlm.md) — An experimental depth-one RLM variant with parallel sub-models, delegated tools, and an editable answer variable.
- [Recursive language models](recursive-language-models.md) — An inference scaffold that externalizes prompts and uses code to orchestrate language-model calls over their parts.
- [Recursive-llm evaluation](recursive-llm-evaluation.md) — Project-reported benchmark and document-citation experiments for the grishahq recursive-llm implementation.
- [Recursive-llm implementation](recursive-llm-grishahq.md) — A Python RLM implementation with bounded execution, document citation checks, and an explicitly limited REPL security model.
- [RLM evaluation and benchmarks](rlm-evaluation.md) — Reported long-context and long-reasoning results, baselines, costs, and limits for recursive language models.
- [rlm.pi evaluation](rlm-pi-evaluation.md) — Project-reported OOLONG results and protocol limits for the rlm.pi plugin.
- [rlm.pi implementation](rlm-pi-implementation.md) — A Pi RLM plugin with persistent Python execution, recursive delegation, and important security and documentation limits.
- [RLM workflows in Deep Agents](deep-agents-rlm-workflows.md) — Reported code-interpreter orchestration and long-context evaluation of recursive workflows in Deep Agents.
- [Surrogate harness training](surrogate-harness-training.md) — Training individual harness calls on synthetic task environments that preserve target solution strategies, sometimes with simulated sub-calls.
- [Training recursive language models](training-recursive-language-models.md) — Distillation and reinforcement-learning experiments for improving models operating recursive language-model scaffolds.
