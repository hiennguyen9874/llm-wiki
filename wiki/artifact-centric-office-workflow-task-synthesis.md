---
type: Concept
title: Artifact-centric office workflow task synthesis
description: A proposed data pipeline builds multi-artifact office tasks from clustered professional materials, judges resulting trajectories and deliverables, and recycles validated artifacts into later synthesis rounds.
tags: [agent-training, data-curation, office-agents, synthetic-data, tool-use]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:42:05Z }
sources:
  - id: nanbeige2026compactagent
    resource: ../raw/arXiv-2607.22083v2/main.tex
    title: "Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model"
---

# Artifact-centric office workflow task synthesis

Nanbeige4.2's authors describe a closed-loop pipeline for agentic office-task data: construct a balanced multi-domain, multi-format artifact repository; cluster and sample coherent artifact bundles; synthesize and judge tasks, trajectories, and deliverables; then re-ingest validated outputs as later source material. It is a design and source-reported production process, not an independently evaluated general recipe.[^nanbeige2026compactagent]

## Pipeline

- The proposed repository spans professional domains including finance, trade, law, and healthcare, and formats such as reports, slides, spreadsheets, PDFs, emails, and code. Artifacts are parsed into structured representations, embedded in a shared space, clustered, and sampled into multi-artifact bundles.[^nanbeige2026compactagent]
- A task-synthesis agent explores bundles in a sandbox to create tasks and rubrics. The source says task difficulty is evolved along cross-artifact dependencies, tool requirements, workflow length, constraints, and verification demands.[^nanbeige2026compactagent]
- Open-source models execute tasks to produce trajectories and deliverable artifacts. An independent judge agent checks deliverable fidelity, rubric consistency, and trace quality; only high-quality samples proceed to later synthesis, and validated deliverables re-enter the artifact repository.[^nanbeige2026compactagent]

## Trust boundary

The manuscript does not report corpus size, inter-rater reliability, contamination controls, judge accuracy, or an ablation isolating clustering, judging, or recycling. Recycling model-produced artifacts can amplify judge and task-synthesis errors; the source presents it as a scaling mechanism rather than validating that risk is controlled.[^nanbeige2026compactagent]

## Relationships

- Related to: [Hybrid environments for tool-use trajectory synthesis](hybrid-environments-for-tool-use-trajectory-synthesis.md) — both use closed-loop task evolution, but this pipeline centers multi-artifact office work rather than tool interfaces.
- Used by: [Nanbeige4.2 compact looped agent model](nanbeige4-2-compact-looped-agent-model.md) — the model report identifies agentic cowork data as one component of its post-training corpus.

[^nanbeige2026compactagent]: Nanbeige LLM Lab and Boss Zhipin, *Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model*, source manuscript, abstract, §§1--4, appendix, and figures (arXiv:2607.22083v2, 2026).