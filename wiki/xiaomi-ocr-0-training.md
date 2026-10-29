---
type: Workflow
title: Xiaomi-OCR-0 training and data engine
description: Xiaomi-OCR-0's reported training combines consensus-based OCR annotation, render-guided refinement, targeted data synthesis, and mixed-task reinforcement learning.
tags: [ml, ocr, data-curation, reinforcement-learning, synthetic-data]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T05:11:26Z }
sources:
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
---

# Xiaomi-OCR-0 training and data engine

**Reported:** [Xiaomi-OCR-0](xiaomi-ocr-0.md) uses an approximately 170-million-sample OCR-centric corpus and progressive training: Q-Mask text anchoring aligns text with location; OCR-centric continued pretraining (CPT) builds multi-task capability; and mixed-task reinforcement learning (Mix-RL) applies verifiable rewards to hard examples. The card does not specify reward formulas or training hyperparameters.[^xiaomi-card]

## Data engine

- **Ensemble Triplet Consensus:** heterogeneous text, table, and formula experts produce candidate annotations; pool-wide agreement ranks them, a three-expert subset is selected, and uncertain cases go to refinement.
- **Render-guided refine-and-judge:** candidates are rendered back to images and compared with the source region to detect and correct structural errors, especially in tables and formulas. Refined candidates return for re-consensus according to the diagram's text alternative.
- **Multi-factor mining:** selection uses expert agreement, model self-consistency, semantic clustering, and verified model failure patterns. Coverage-driven synthesis fills sparse structures, styles, glyphs, and domains; failure-driven synthesis targets recurrent errors.[^xiaomi-card]

## Reported training observations

- Adding understanding supervision changed parsing scores by −0.330, +0.639, and +0.0749 at stages using 9%, 29%, and 50% of parsing data respectively, each against its own stage baseline. This is not evidence that understanding data always improves parsing.[^xiaomi-card]
- On the authors' comparison, the 4B single-task parsing teacher scored 96.9745 versus 96.8277 for the 0.8B Mix-RL student; the 4B VQA teacher scored 88.1 versus 83.2. The card states that task data amounts match within each comparison, but the teachers specialize and the student trains jointly, so parameter count is not the sole changed factor.[^xiaomi-card]
- The 0.8B CPT, MOPD, and Mix-RL variants respectively scored 96.4739, 96.7417, and 96.8277 on OmniDocBench, and 78.1, 82.7, and 83.2 on the five-benchmark VQA mean. The authors report faster MOPD convergence and a higher eventual Mix-RL peak, but the underlying compute-trajectory figure is unavailable locally.[^xiaomi-card]

## Relationships

- **Used by:** [Xiaomi-OCR-0](xiaomi-ocr-0.md).[^xiaomi-card]
- **Related to:** [Document-parser data flywheel](document-parser-data-flywheel.md): failure-driven mining and synthesis share its weakness-to-data pattern, without establishing identical evaluation or overlap controls.[^xiaomi-card]

## Limits

The local model card is the only inspected source. Its linked technical report, training data, evaluation code, and figures are unavailable in this capture; exact experimental configurations, statistics, reward definitions, licensing of corpus components, and contamination controls cannot be checked. No training or evaluation was run. The descriptions are author-reported, with causal and generalization limits; the missing diagram is summarized only from its alternative text and adjacent prose.[^xiaomi-card]

[^xiaomi-card]: SeerRay Lab, [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), §§ About the model, Data Engine, and Key Findings (inspected 2026-10-29).
