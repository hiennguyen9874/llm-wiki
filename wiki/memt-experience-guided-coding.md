---
type: Concept
title: MemT-1.0 experience-guided coding
description: Retrieval, native-memory injection, application-specific training, and reported SWE-bench outcomes for MemT-1.0-Nano.
tags: [agent-memory, coding-agents, benchmarks]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: '2026-11-08T02:52:52Z' }
sources:
  - id: memt-paper
    resource: ../raw/arXiv-2610.26825v2-MemT-1.0/paper.tex
    scope: ../raw/arXiv-2610.26825v2-MemT-1.0/
    kind: paper
    revision: arXiv-2610.26825v2
    title: 'MemT-1.0: Towards Memory-Native Evolution'
---

MemT-1.0-Nano's coding application retrieves external procedural guidance, writes it into a native memory state, then reads that state while working on a task rather than retaining the guidance as text in the task context. This is not autonomous discovery or continual training: the experience bank and retrieval process are external, and application-specific training is required.[^memt-paper]

## Pipeline and training

**Reported:** a bank of 1,040 reusable experiences is distilled from 41,057 successful Scale-SWE trajectories. BGE-M3 ranks experiences using the task description. Experience is stored either before execution or at a harness-detected breakpoint such as a command failure; at most one store operation is used per trajectory. Once stored, the state remains fixed for the rest of the task.[^memt-paper]

From 18,820 initial trajectories, the authors test 199,500 breakpoint interventions and retain 42,403 filtered training examples. The application checkpoint freezes backbone parameters and trains hyper memory; its selected setup uses full-suffix knowledge distillation, with the teacher seeing textual experience and the student seeing native memory.[^memt-paper]

## Reported results and limits

SWE-bench Verified has 500 tasks and Multilingual has 300; each task is run three times. On Verified, before-execution Nano averages 69.33% against 66.07% without experience and 68.87% with textual experience. The fraction solved in **all three runs** increases from 54.00% to 61.60% (also 61.60% for textual experience). On Multilingual the corresponding average is 62.89% vs 60.00%, and all-three success is 53.67% vs 45.33%. `pass@3` means at least one success; it does not consistently improve. The extra memory training and retrieval/write costs matter when interpreting comparisons; no independent execution was performed.[^memt-paper]

See [evaluation](memt-evaluation-and-efficiency.md) for general memory results and [source map](memt-source-map.md) for pending application appendix review.

[^memt-paper]: `sections/application.tex` §§ Experience-Guided Agentic Framework, Experience Construction and Model Training, Agentic Coding Evaluation and Case Study and Discussion.
