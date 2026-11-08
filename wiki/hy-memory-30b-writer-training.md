---
type: Concept
title: Hy-Memory-30B-A3B writer and training
description: Framework-integrated memory-writer model, on-policy distillation, attributed reinforcement learning, and deployment boundaries.
tags: [agent-memory, hy-memory, memory-writer, training, paper]
status: stable
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: 2026-11-08T02:52:40Z }
sources:
  - id: hy-writer
    resource: ../raw/arXiv-2610.22196v1-Hy-Memory-30B-A3B/Hy-Memory-30B-A3B.md
    scope: ../raw/arXiv-2610.22196v1-Hy-Memory-30B-A3B/
    kind: paper
    revision: arXiv-2610.22196v1
    title: "Hy-Memory-30B-A3B: Attributed Reinforcement Learning for Long-Term Memory Writing"
---

# Hy-Memory-30B-A3B writer and training

**Reported:** Tencent Hunyuan's Hy-Memory-30B-A3B is a specialized external-memory **writer**, not a replacement memory store or reader. The report trains a Hy3-30B-A3B instruction checkpoint (~3B active parameters) to operate existing Mem0, MemOS and [Hy-Memory](hy-memory-overview.md) write paths; it evaluates generalization to an unseen EverMemOS harness. It does not independently establish performance outside the reported setup (`main.tex`, Abstract, §Problem Formulation and §Experiments).[^hy-writer]

## Training and state

- A chunk is roughly ten turns within one session; an RL window contains at most five consecutive chunks and may cross sessions. A writer acts through harness-generated prompts and operations; the external bank persists between calls. Candidate rollouts use isolated bank copies (`main.tex`, §Data hierarchy, §Memory writing as an MDP).[^hy-writer]
- **Stage 1, Memory on-policy distillation (OPD):** student-generated writes create subsequent bank states; a frozen Hy3 flagship teacher scores the student token stream with top-50 approximate reverse KL. Two rollouts per row, learning rate 1e-6, entropy coefficient 0.005; OPD step 375 initializes RL. Calls retain separate segments and reset position IDs (`main.tex`, §Stage 1: Memory on-policy distillation).[^hy-writer]
- **Stage 2:** eight rollouts start from copies of a common parent and write a window. A frozen answer model reads retrieved memory; a frozen judge scores against a rubric. Chunk-level advantages compare rollouts at the same chunk position; the final bank with the largest sum of chunk scores becomes the next window's parent (`main.tex`, §Stage 2, §Chunk-level GRPO, §Bank carry-forward). See [reward and credit assignment](hy-memory-30b-reward-and-credit.md).[^hy-writer]
- Reported RL configuration: 16 × 8 H20 GPUs, 64 windows × 8 rollouts per batch, learning rate 5e-6, PPO-style clipping without KL penalty, replayed MoE routing, 28,672 prompt and 4,096 response tokens (`main.tex`, §Training System).[^hy-writer]

## Use and limitations

The model card identifies Apache-2.0 and English/Chinese; it reports an OpenAI-compatible example using vLLM v0.31.0, a local endpoint, `reasoning_effort: no_think`, and structured fact-extraction output. It links weights and configuration externally; these, the actual evaluation stack, and serving compatibility were not inspected or executed. The source does not establish a paper license (`Hy-Memory-30B-A3B.md`, frontmatter, §Quickstart, §Resource Availability).[^hy-writer]

**Reported:** Attribution is not counterfactual; effects inherited from earlier optimizer steps cannot receive retrospective gradient. Multi-call chunks may still carry more loss mass even though each rollout has one baseline vote. Controlled training-component ablations, repeated seeds, judge calibration and broader OOD testing remain future work (`main.tex`, §Future ablations and audits, §Limitations and Future Work).[^hy-writer]

## Relationships

- Uses: [Reward construction and credit assignment](hy-memory-30b-reward-and-credit.md) for selective, downstream-useful writes.
- Evaluated in: [Writer benchmark protocol and results](hy-memory-30b-writer-evaluation.md); operates within, rather than replacing, [Hy Memory](hy-memory-overview.md).[^hy-writer]

## Source coverage

The v1 package's model card and complete `main.tex`, including all tables and appendix, were inspected as text. PDF figure text was extracted: figures 1–3 duplicate material captured in captions, prose, or tables; figure 2 also reports pilot separation 0.95/0.87 without a prose explanation, so it is not interpreted here. Figures were not visually inspected. `00README.json` was inspected; `references.bib` and `main.bbl` are bibliography, not independently verified evidence; style/BST files are typesetting dependencies, and logos are decorative. The model card refers to PNG versions of figures absent locally; equivalent PDFs are present. External links, weights, dataset, implementation and benchmark outputs were not fetched; no compilation, training, or benchmark was run. Bibliographic date beyond the v1 identifier is not established from these artifacts.[^hy-writer]

[^hy-writer]: Tencent Hunyuan technical report, arXiv 2610.22196v1, package `main.tex` and model card; specific sections and artifacts identified inline. Findings are source-reported unless explicitly labeled otherwise.
