---
type: Concept
title: Model adaptation mechanisms
description: A comparison of direct weight editing, fine-tuning, distillation, prompt baking, and retrieval by how they change model behavior.
tags: [ml, model-editing, fine-tuning]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:29:40Z }
sources:
  - id: masood-adaptation
    resource: ../raw/when-llms-edit-other-llms-weight-space-programming-and-the-conditions-for-recursive-self-improvement.md
    kind: article
    title: "When LLMs Edit Other LLMs: Weight-Space Programming and the Conditions for Recursive Self-Improvement"
---
**Reported:** Adaptation mechanisms differ in what information selects a change and where the resulting behavior resides. Direct weight-space programming has an LLM diagnose a target and author a parameter intervention; gradient fine-tuning optimizes an objective using examples. Whether a direct edit counts as fine-tuning depends on whether that term means gradient optimization or any persistent post-training parameter change.[^masood-adaptation]

## Mechanisms and relationships

- **Reported:** LoRA trains small low-rank matrices while freezing base weights; merging their product can change many original matrix entries. Low rank is a compact representation, while sparsity concerns how many entries change: neither implies the other.[^masood-adaptation]
- **Reported:** Prompt baking uses gradient-based self-distillation to train a model to behave like its prompted original without later supplying the prompt. Ordinary teacher–student distillation transfers behavior through supervision, whereas an editor supplies code or parameter changes; parent–child describes lineage rather than an update mechanism.[^masood-adaptation]
- **Reported:** Retrieval-augmented generation supplies information at query time without ordinarily changing parameters. A document update, a trained skill, and a targeted computational repair therefore address different adaptation needs; selecting among them is an engineering judgment, not a demonstrated universal rule.[^masood-adaptation]
- **Reported:** ROME uses gradient optimization to find a target representation even though its final matrix write is analytical; MEMIT edits multiple factual associations, MEND uses a trained gradient-transforming editor, and hypernetworks generate another network's weights. The article presents a general-purpose LLM's open-ended investigation as the distinction of weight-space programming, not the first instance of direct parameter editing.[^masood-adaptation]

## Relationships

- [LLM-directed neural weight editing](llm-directed-neural-weight-editing.md) documents a reported gradient-free repair and its evaluation limits.
- [Continual learning and recursive improvement](continual-learning-and-recursive-improvement.md) distinguishes isolated adaptation from retention and improved improvement processes.

## Evidence and coverage

The English secondary article is attributed by its original Medium URL to Adnan Masood and dated 2026-11-04; the capture is marked non-free. Capture date and license are unspecified. Its local text, including references and descriptions of figures, was inspected. The figures are remote and were not inspected; their relevant comparative content is also described in the text. Linked papers, research artifacts, and external websites were not inspected for this ingest, and no experiments were reproduced. Claims about those works are the article's reports, not independent verification. Draft status records these limits.[^masood-adaptation]

[^masood-adaptation]: Local article, “Gradient-free editing still requires evidence and computation,” “Fine-tuning already includes selective parameter updates,” “Targeted model editing has a substantial research history,” “Prompt Baking uses a different adaptation mechanism,” and “Teacher, student, parent, and editor describe different relationships.”
