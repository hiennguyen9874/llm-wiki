---
type: Concept
title: Coarse normalization-weight editing experiment
description: A reported code-repair experiment illustrates silent no-op edits, noisy baselines, and failure after coarse normalization gains.
tags: [ml, interpretability, evaluation]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:20:23Z }
sources:
  - id: das-coarse-edit
    resource: ../raw/weight-space-programming-what-the/index.md
    scope: ../raw/weight-space-programming-what-the/
    kind: article
    title: "Weight-Space Programming: what the numbers actually showed"
---

**Reported:** Sayantan Das tried gradient-free normalization-weight gains as a code-repair intervention. Initial apparent gains were invalidated by a silent no-op and noisy sampling; after corrections, the reported Qwen2.5-Coder-1.5B score fell from 4/8 to 0/8 at both tested gains. This is a small, source-reported experiment, not a general test of all weight-space programming methods.[^das-coarse-edit]

## Method and results

**Reported:** The author compared code and ordinary-text hidden states per block, measuring mean token-state norm and the norm of the difference between group-mean states. The last Qwen block had reported values 213.5 and 135.0, respectively. Chosen block normalization weights were multiplied in place by a gain; generated fixes were extracted and run with unit tests on eight planted-bug tasks. The test is passed only when the subprocess exits successfully and prints `PASS`.[^das-coarse-edit]

**Synthesis:** Hidden-state magnitude is not itself a measurement of a block's incremental residual contribution, and code-versus-non-code mean differences do not establish causal localization. The article does not specify the exact chosen tail modules, all task inputs, or a complete executable harness, limiting interpretation and replication.[^das-coarse-edit]

**Reported:** With greedy decoding and a fixed seed, the author reports identical per-task outcomes on two independent T4 boxes: Qwen baseline 4/8, and gains of 1.5 and 2.5 each 0/8, with failures described as “no fenced code.” LFM2.5-1.2B-Thinking scored 0/8 at baseline; a separate tool-routing, JSON-extraction and multi-turn battery reportedly scored 12/12. No uncertainty estimate or independent verification is provided. The author proposes that changed normalization disrupts downstream calibration, but does not present measurements establishing that mechanism.[^das-coarse-edit]

## Failure modes and proposed controls

**Reported:** An exact class-name test missed model-specific normalization classes, leaving no selected modules and making edits no-ops. A separate restore bug attempted `.data.clone()` on a module rather than its weight and only surfaced after detection was fixed. Sampling at temperature 0.05 with `do_sample=True` produced unedited baselines of 4/8 to 6/8, making a one-point change unreliable.[^das-coarse-edit]

**Reported recommendations:** Check that intended tensors actually changed and the edit path ran; use a stable baseline and compare individual task outcomes across independent runs. The author proposes testing finer-grained attention-head output-projection slices, but presents only a sketch, not results. Greedy decoding and a seed are useful controls, not a guarantee of deterministic execution across all hardware and software.[^das-coarse-edit]

**Synthesis:** The author's assertions that an edit cannot create absent capability and that coarse scaling is categorically not weight-space programming are stronger than this experiment establishes. The original formulation emphasizes LLM reasoning over weights; this activation-guided manual gain experiment differs from the [LLM-directed edits](llm-directed-neural-weight-editing.md) rather than reproducing their exact intervention.[^das-coarse-edit]

## Relationships

- Contrasts with [LLM-directed neural weight editing](llm-directed-neural-weight-editing.md): this coarse gain experiment used a different model, task, and intervention.
- Relates to [weight-space programming](weight-space-programming.md): it tests a gradient-free weight perturbation but does not establish the original method's claimed results.

## Evidence and coverage

The English article by Sayantan Das is dated 2026-11-08 and gives its original URL in the local capture; capture date, license, model revisions, full tasks, exact selected modules, and experimental artifacts are unspecified. The entry point and both local diagrams were inspected: the loop diagram and bar chart repeat the textual method and results. External model cards, original research, infrastructure and purported packaged tooling were not inspected. Code snippets were inspected statically, not executed; generated code and remote execution pose execution risks. No experiment was reproduced. Draft status reflects these coverage and attribution limits.[^das-coarse-edit]

[^das-coarse-edit]: Das, “The target and the infra,” “What the method actually is,” “First pass: looks like it works,” “The corrected run,” “Why it collapses,” and “The measurement contract that would have saved me”; local loop diagram and coarse-edit bar chart.
