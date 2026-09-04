---
type: Concept
title: Circuit organization and systematic generalization
description: The paper links OOD generalization in synthetic implicit reasoning to whether a learned transformer circuit accesses atomic knowledge in shared or separate layer regions.
tags: [mechanistic-interpretability, systematic-generalization, transformers, circuits]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:28:50Z }
sources:
  - id: wang2024grokked
    resource: ../raw/arXiv-2405.15071v3/neurips_2024.tex
    title: "Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization"
  - id: kohli2026loop
    resource: ../raw/arXiv-2604.07822v2/colm2026_conference.tex
    title: "Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers"
---

# Circuit organization and systematic generalization

The paper's causal-tracing and logit-lens analysis associates systematic OOD generalization with a parallel comparison circuit that retrieves both atomic facts in the same lower-layer region, unlike a composition circuit that must use atomic knowledge stored in separate lower and upper layers.[^wang2024grokked]

## Reported circuits

- In two-hop composition, lower layers retrieve $(h,r_1,b)$ and represent the bridge entity at layer 5; upper layers use that representation and $r_2$ to retrieve $(b,r_2,t)$. During grokking, causal influence from the bridge state to the prediction and representation of $r_2$ strengthen.[^wang2024grokked]
- The authors argue that the upper layers need only store facts seen as a second hop in training. Atomic OOD facts, seen only in atomic form, therefore are unavailable to the upper-layer lookup even though the lower circuit can represent the bridge and second relation. This explains the reported failure of OOD composition.[^wang2024grokked]
- In comparison, the circuit retrieves the two attribute values in parallel in lower layers, while a separate stream prepares the attribute's three comparison labels. The upper layers compare the values and select a label. Because ID and OOD atomic facts are retrieved from the same lower-layer region, the model achieved OOD generalization in the reported task.[^wang2024grokked]

## Implications and limits

The authors suggest cross-layer memory sharing—such as memory augmentation, recurrence, or parameter sharing—could mitigate the composition limitation. In their parameter-sharing variant (first four and last four layers shared), OOD composition generalization appeared, but more slowly than ID generalization.[^wang2024grokked]

A later synthetic study reports compatible activation-patching evidence: on its OOD composition split, a vanilla model recovers the bridge only too late to compose the target, whereas causal bridge states in the first recurrent iteration support the final prediction in a shared-block model. This is corroboration in a related setup, not a replication of the original circuit or a general mechanism.[^kohli2026loop]

These circuits are an interpretation of particular trained models, inferred from causal interventions and logit-lens probes. They do not establish that all transformer reasoning, composition tasks, or OOD failures have the same mechanism.[^wang2024grokked]

## Relationships

- **Explains**: [Grokking for implicit reasoning](grokking-for-implicit-reasoning.md) provides the reported training behavior this circuit analysis interprets.
- **Supported by**: [Recurrent-depth systematic generalization and extrapolation](recurrent-depth-systematic-generalization-and-extrapolation.md) reports a related shared-recurrence intervention and causal analysis.

[^wang2024grokked]: Wang, Yue, Su, and Sun, *Grokked Transformers are Implicit Reasoners: A Mechanistic Journey to the Edge of Generalization*, §§3–4 and appendix (2024).
[^kohli2026loop]: Kohli, Parthasarathy, Sun, and Yao, *Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers*, §§4 and A (arXiv:2604.07822v2, 2026).