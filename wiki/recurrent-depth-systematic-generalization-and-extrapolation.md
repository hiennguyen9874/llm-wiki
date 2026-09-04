---
type: Concept
title: Recurrent-depth systematic generalization and extrapolation
description: A controlled synthetic study reports that shared transformer depth enables systematic composition and inference-time depth extrapolation, but excessive recurrence can degrade predictions.
tags: [adaptive-computation, compositional-generalization, depth-extrapolation, depth-recurrence, systematic-generalization]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:28:50Z }
sources:
  - id: kohli2026loop
    resource: ../raw/arXiv-2604.07822v2/colm2026_conference.tex
    title: "Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers"
---

# Recurrent-depth systematic generalization and extrapolation

In controlled synthetic knowledge-graph tasks, this study reports that a decoder-only transformer with a shared four-layer block can systematically compose atomic facts withheld from compositional training and can extrapolate beyond trained hop depths by using more recurrent inference iterations. These results are restricted to small, structured-vocabulary models trained from scratch; the source explicitly does not claim direct transfer to frontier LLMs.[^kohli2026loop]

## Systematic composition

- The two-hop task supplies all 40,000 atomic facts but forms training compositions only from a 95% atomic-fact partition. The OOD test uses two-hop compositions of the remaining partition, so success requires composing known atomic facts that never appeared in a training composition.[^kohli2026loop]
- The non-recurrent four-layer baseline ($R=1$) reportedly fails this OOD split, while recurrent models ($R=2,4,8$) attain non-trivial to roughly 0.8 accuracy; $R=4$ reached that level in about 2,000 epochs versus about 7,000 for $R=2$ in the reported curves.[^kohli2026loop]
- For $R=4$, the reported trajectory has three stages: training-set fit, delayed ID generalization, then delayed systematic OOD generalization. Logit-lens and activation-patching analyses associate OOD failure in the vanilla model with recovering the bridge entity too late to compose the target; in the recurrent model, first-iteration bridge states have causal influence on the final prediction and later iterations reuse the shared block.[^kohli2026loop]

## Depth extrapolation and training strategy

- The multi-hop task uses 200 entities and 10 relations, with each relation a permutation. This construction prevents a tail entity from being inferred from a short relation suffix, an identified shortcut in an earlier dataset version.[^kohli2026loop]
- Models use an easy-to-hard hop curriculum, a zero-initialized residual output projection for stable unrolling, and no positional embeddings. A four-layer block is trained with fixed $R=1$--$8$ or a per-batch clipped-Poisson recurrence ($R_{min}=2$, $R_{max}=8$).[^kohli2026loop]
- Inference-time recurrence enabled OOD hop-depth extrapolation only for models trained with more than four fixed iterations. In matched training data through 12 hops, the reported fixed-$R=8$ and dynamic models both reached 19 hops, compared with 14 for fixed $R=6$; larger training recurrence therefore helped in this setup, but the paper does not establish a general scaling law.[^kohli2026loop]
- Dynamic training increased the maximum in-distribution depth in the curriculum and showed more stable extrapolation across the reported seeds. Neither increasing block depth nor the maximum dynamic training recurrence produced a clear, consistent improvement in the paper's generalization-ratio metric.[^kohli2026loop]

## Overthinking and halting

Further recurrence can overwrite a correct prediction: logit margins peaked and then declined across the tested fixed and dynamic models, with sharper degradation for fixed recurrence and smaller peaks on harder hops. Dynamic recurrence was more robust but did not remove this limitation.[^kohli2026loop]

The paper's adaptive halting requires both a small KL divergence between successive output distributions and low output entropy. On its dynamic model, this avoided the premature stopping observed with the KL-only rule and allocated more iterations to harder samples. This is evidence for a task-specific stopping heuristic, not a validated general halting mechanism.[^kohli2026loop]

## Trust boundary and limitations

The source studies one synthetic implicit-reasoning family with dedicated entity and relation tokens, limited vocabulary, and models far smaller than modern LLMs. Surface variation, distractors, natural-language distribution shift, web-scale pretraining, and post-training are out of scope. Its causal evidence is useful for the particular two-hop setup, but does not establish that recurrent states are faithful or interpretable reasoning traces in general.[^kohli2026loop]

## Relationships

- **Supports**: [Circuit organization and systematic generalization](circuit-organization-and-systematic-generalization.md) — its causal results test the proposed cross-layer access limitation and report that shared recurrence mitigates it in a related synthetic composition task.
- **Extends**: [Grokking for implicit reasoning](grokking-for-implicit-reasoning.md) — it reports a further delayed stage of systematic OOD generalization after ID grokking.
- **Related to**: [Depth-recurrent transformers for compositional generalization](depth-recurrent-transformers-for-compositional-generalization.md) — both test OOD benefits of latent weight sharing, but use different architectures, tasks, and stability mechanisms.
- **Related to**: [Recurrence and parametric knowledge manipulation](recurrence-and-parametric-knowledge-manipulation.md) — both interpret recurrence as improving composition of stored synthetic facts rather than storage capacity itself.

[^kohli2026loop]: Kohli, Parthasarathy, Sun, and Yao, *Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers*, source manuscript, abstract, §§2--5 and appendices (arXiv:2604.07822v2, 2026).