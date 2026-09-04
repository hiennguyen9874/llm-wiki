---
type: Concept
title: Program-of-layers inference over frozen LLMs
description: PoLar predicts an input-specific program that skips, retains, or once repeats contiguous segments of a frozen LLM, reporting improved math-reasoning pass@k and lower measured latency in its source evaluation.
tags: [adaptive-computation, dynamic-depth, inference, latent-reasoning, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:34:15Z }
sources:
  - id: li2026polar
    resource: ../raw/arXiv-2606.06574v2/camera_ready.tex
    title: "Skip a Layer or Loop It? Learning Program-of-Layers in LLMs"
---

# Program-of-layers inference over frozen LLMs

PoLar treats a frozen pretrained transformer's layers as callable functions and predicts, before execution, an input-specific sequence that skips or repeats contiguous layer segments. In the source's math-reasoning experiments, this learned execution-program selection improves reported pass@k over fixed inference and several dynamic-depth baselines; its deployment evidence is limited to four small-to-mid-sized instruction models, one predictor configuration, and source-controlled latency measurement.[^li2026polar]

## Representation and prediction

- A program is a finite sequence of layer indices. PoLar restricts this to a partition of the depth into contiguous segments of at most four layers, assigning each segment **skip**, **keep**, or **repeat**; repeat runs the segment exactly one additional time.[^li2026polar]
- The base LLM remains frozen. A roughly 2.1M-parameter predictor encodes the input with frozen Qwen3-Embedding-0.6B, uses learned layer embeddings as cross-attention queries over token representations, applies a small depth-wise transformer encoder, and emits boundary and operation logits.[^li2026polar]
- At inference it thresholds predicted segment boundaries, inserts boundaries to enforce the length cap, and beam-searches segment-operation combinations. Thus it selects whole programs before the base-model forward pass, rather than routing each layer from intermediate hidden states.[^li2026polar]
- MCTS is an offline diagnostic and label generator, not the deployed method: it starts from the standard layer order, applies bounded contiguous skip/repeat edits, and rewards a program only when it produces the known correct answer. This establishes source-specific existence of alternative successful paths, but is not an inference-time search procedure.[^li2026polar]

## Reported evidence

- In MCTS experiments on DART-Math, allowing both skip and recurrence produced higher reported accuracy than either alone for every listed model/difficulty pair. The combined search's gain over the standard forward pass ranged from 21.0 to 62.7 percentage points across the table; 71.9% of initially correct inputs and 34.0% of initially incorrect inputs were reported to have a shorter valid program.[^li2026polar]
- On LLaMA-3.2-3B-Instruct, PoLar's pass@5 on DART-Math is reported as 74.5, 46.9, 47.6, 45.1, and 41.9% across difficulty levels 1--5, respectively, versus 65.2, 41.2, 39.5, 38.5, and 34.5% for the source's best-temperature sampling baseline. These are oracle-style pass@k results over the top-$k$ programs or sampled outputs, not a claim that a deployment system can identify the correct candidate without a verifier.[^li2026polar]
- The paper reports pass@1 OOD gains from DART-Math-trained predictors on ASDiv, MAWPS, and many MMLU-Pro subject subsets. The breadth of that table is evidence of transfer under its evaluation protocol, not proof that the learned execution policy is domain-independent.[^li2026polar]
- On Qwen1.5-MoE-A2.7B-Chat with 24 layers, the source measures 3.05 ms predictor/beam/encoder overhead (0.8% of one full forward pass) and end-to-end latency of 0.83x on DM-1 and 0.95x on DM-5 relative to its base runtime. These measurements depend on that model and serving setup.[^li2026polar]

## Trust boundary and limitations

The in-distribution evidence uses deduplicated, difficulty-wise DART-Math train/validation/test splits and direct final-answer prompting; the authors state that this version removed duplicate questions before splitting and reran affected analyses. It does not test long-context, conversational, safety-critical, or production serving workloads.[^li2026polar]

The method is not training-free in the ordinary sense: only the base LLM is frozen; the execution predictor is supervised from MCTS-discovered, ground-truth-validated programs. The source's claims about latent reasoning capacity and the predictor's cross-domain mechanism are interpretations, rather than causal evidence that a selected program implements a particular reasoning process.[^li2026polar]

## Relationships

- Related to: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) — both adapt depth, but PoLar reuses individually pretrained frozen layer segments per input while Mixture-of-Recursions trains a weight-tied recursive architecture with token-level routing.
- Related to: [Ouro looped language models](ouro-looped-language-models.md) — both allocate recurrent depth, but PoLar predicts skip/keep/repeat programs across distinct pretrained layers rather than repeatedly applying a shared stack and exiting by round.

[^li2026polar]: Li, Li, and Zhou, *Skip a Layer or Loop It? Learning Program-of-Layers in LLMs*, source manuscript, abstract, §§1--5, appendix, figures, and Tables 1--6 (arXiv:2606.06574v2, 2026).