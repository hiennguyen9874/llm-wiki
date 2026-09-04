---
type: Concept
title: Parametric memory for complex reasoning
description: In one synthetic large-search-space comparison task, a fully grokked transformer substantially outperformed evaluated prompted and retrieval-augmented frontier models.
tags: [parametric-memory, retrieval, reasoning, grokking]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:13:30Z }
sources:
  - id: wang2024grokked
    resource: ../raw/arXiv-2405.15071v3/neurips_2024.tex
    title: "Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization"
---

# Parametric memory for complex reasoning

On a synthetic comparison task requiring search for bridge entities and use of comparison, symmetry, and transitivity rules, the paper reports 99.3% accuracy for a fully grokked transformer versus 11.3–37.3% for its evaluated GPT-4-Turbo and Gemini-1.5-Pro prompting and retrieval setups.[^wang2024grokked]

## Task and results

- Test queries compare two OOD entities. Proofs require locating two ID bridge entities and applying both basic comparison and (anti-)symmetry/transitivity rules; the paper reports more than 50 facts connected to each query entity and more than 900 to each bridge entity on average.[^wang2024grokked]
- The non-parametric baselines received either all facts (Gemini; 28.2K on average) or retrieved two-hop neighborhoods (5.4K facts on average). Direct-answer and chain-of-thought prompts were evaluated; GPT-4-Turbo was tested only with retrieval because of its context limit.[^wang2024grokked]
- Reported accuracy was 33.3% (GPT-4-Turbo direct + retrieval), 31.3% (GPT-4-Turbo CoT + retrieval), 28.7%/11.3% (Gemini direct/CoT), and 37.3%/12.0% (Gemini direct/CoT + retrieval). The authors note that many Gemini CoT responses declared the answer undecidable and that many correct final answers had invalid rationales.[^wang2024grokked]
- The grokked transformer was trained on the task's facts and, according to the authors' analysis, gradually inferred OOD query-entity attributes despite not being directly trained to predict them.[^wang2024grokked]

## Trust boundary

This is a controlled, source-specific comparison, not a general benchmark of parametric memory, retrieval-augmented generation, chain-of-thought, GPT-4-Turbo, or Gemini. The models differ in access pattern and training: the transformer is extensively trained to compress the task facts, whereas the frontier-model baselines operate from provided context.[^wang2024grokked]

## Relationships

- **Uses**: [Grokking for implicit reasoning](grokking-for-implicit-reasoning.md) for the training phenomenon that produces the reported transformer.
- **Uses**: [Circuit organization and systematic generalization](circuit-organization-and-systematic-generalization.md) for the comparison-circuit interpretation the paper reports for this task.

[^wang2024grokked]: Wang, Yue, Su, and Sun, *Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization*, §5 and appendix (2024).