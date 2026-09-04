---
type: Concept
title: Loss scaling for looped language models
description: In one small-scale study, looped-transformer total and per-round losses fit proposed power-law forms, while untied transformers retained a performance advantage at equal effective depth.
tags: [parameter-sharing, scaling-laws, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:21:45Z }
sources:
  - id: zhu2025ouro
    resource: ../raw/arXiv-2510.25741v5/paper.tex
    title: "Scaling Latent Reasoning via Looped Language Models"
---

# Loss scaling for looped language models

A small-scale Ouro study fits total loss and per-round loss of looped transformers as power-law-like functions of parameter count, training data, and recurrence depth. In its matched-depth comparison, an untied standard transformer always outperformed the weight-tied model, so the fitted laws characterize the source's LoopLM training regime rather than showing that tying improves performance at equal compute.[^zhu2025ouro]

## Study and findings

- The study trains 53M–1.36B models on 20B FineWeb-Edu tokens with maximum recurrence depths of 1, 2, 4, or 8, then averages six benchmark scores. A standard model at recurrence $T$ has effectively $T$ times as many untied layers; the LoopLM shares those weights.[^zhu2025ouro]
- Both model families generally improved with model size and recurrence depth. At the same settings, the standard model's average score exceeded the LoopLM's; the reported standard-minus-looped gap generally grew with recurrence and, at lower recurrence, tended to shrink with model size.[^zhu2025ouro]
- The proposed total-loss fit adds inverse power terms for parameters, data, and maximum recurrence depth. Fitting all reported points gave $R^2=0.9596$; selecting subsets of model sizes, data prefixes, or maximum depths gave reported average/all-point $R^2$ values around 0.94–0.96.[^zhu2025ouro]
- Separate per-round-loss fits substitute current recurrence depth for maximum depth. The full-data fits reported $R^2$ of 0.8898, 0.8146, and 0.795 for maximum depths 2, 4, and 8, after omitting anomalous points where shallow-round loss increased with more data.[^zhu2025ouro]

## Interpretation and limits

The authors attribute the anomalous shallow-round behavior in under-sized models to the learned exit distribution shifting weight toward deeper, lower-loss rounds. This is a proposed explanation, not an independently tested mechanism.[^zhu2025ouro]

Reported $R^2$ values mainly assess the stated fit family on a small grid, and some generalization evaluations calculate it over all points after fitting on a subset. They do not establish reliable extrapolation to frontier scale, other datasets, different tying schedules, or adaptive inference policies.[^zhu2025ouro]

## Relationships

- Characterizes: [Ouro looped language models](ouro-looped-language-models.md) — the paper's deployed family uses four recurrent steps after small-scale scaling experiments.
- Related to: [Virtual logical depth scaling](virtual-logical-depth-scaling.md) — both examine performance as shared weights create more effective depth.

[^zhu2025ouro]: Zhu et al., *Scaling Latent Reasoning via Looped Language Models*, source manuscript, appendix “Scaling Law for UTs” and “Details of the Scaling Law for UTs” (arXiv:2510.25741v5, 2025).