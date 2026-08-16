---
type: Concept
title: Foresee-to-Ground (F2G)
description: A Video-LLM temporal-grounding framework that cites a proposed event span before refining its metric boundaries.
tags: [video, video-llm, temporal-grounding, evidence, temporal-representation-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:46:05+07:00 }
sources:
  - id: f2g-paper
    resource: ../raw/Foresee-to-Ground/main.tex
    title: "Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding"
---

# Foresee-to-Ground (F2G)

Foresee-to-Ground (F2G) treats video temporal grounding as *Identify-then-Measure*: a Video-LLM first cites one candidate event span from a compact video-wide evidence pool, then emits the answer and refined metric interval under that cited hypothesis. The paper presents this as an alternative to direct timestamp generation from flattened visual tokens; citation makes the chosen intermediate segment attributable, but does not by itself verify that the segment or final interval is correct.[^f2g-paper]

## Evidence-mediated grounding

An evidence unit contains a discrete span ID, a coarse interval, and fixed-length segment-local visual tokens. The model receives the video, query, and all Top-$K$ evidence units in one context, and is supervised to emit exactly one span ID in a structured response. This realizes the cited factorization in one decoding pass rather than separate identification and measurement calls.[^f2g-paper]

The paper reports that the best span in the Top-$K$ pool is an upper bound on cite-only performance, the selected span tracks that bound, and evidence-conditioned refinement improves the final interval. On the reported citation-gap diagnostic, 87.8% of ActivityNet-Captions queries and 93.6% of Charades-STA queries had a cited-span IoU within 0.10 of the pool’s best IoU; the authors therefore identify candidate-pool coverage as the main remaining limitation. These are source-reported results, not independent verification.[^f2g-paper]

## Three-stage pipeline

1. **Predictive temporal perception:** spatially pool the Video-LLM vision features, then train a shared temporal module to predict a global-view latent from multiple cropped, strided, or subsampled local views. A sliced isotropic Gaussian regularizer is added to stabilize latent geometry; the predictor is discarded after pretraining.[^f2g-paper]
2. **Proposal warm-up:** train a query-agnostic self-attention proposal head on interval annotations to regress dense candidate spans and IoU-derived objectness scores, retaining the Top-$K$ candidates. Each retained temporal crop is encoded with a Q-Former-style Span Evidence Encoder (SEE) into fixed-length visual evidence tokens.[^f2g-paper]
3. **Evidence-driven fine-tuning:** apply LoRA to the LLM while training SEE and lightly updating the temporal module and proposal head. The loss combines structured language modeling, cited-span-ID supervision, timestamp-token supervision, and a small proposal-regression term.[^f2g-paper]

The stated Qwen3-VL-8B configuration uses one-FPS sampling, eight candidates, and four SEE queries; serializing the evidence pool adds approximately 100--200 context tokens, while the added components account for approximately 0.5B parameters and under 5% reported inference-latency overhead. These configuration-specific claims do not establish general cost or long-video coverage guarantees.[^f2g-paper]

## Reported evidence and limits

On the paper’s backbone-controlled Qwen3-VL-8B comparison, F2G fine-tuning reports higher Charades-STA R@0.7/mIoU (25.7/47.2) than conventional fine-tuning (21.6/42.9), and higher ActivityNet-Captions R@0.7/mIoU (28.4/45.7 versus 21.7/40.8). It also reports cross-backbone gains and no observable VideoMME degradation under its evaluated setting.[^f2g-paper]

F2G is evaluated for visual queries with one primary temporal interval. The authors identify multi-event, compositional, multi-span, spatial, and audio-visual grounding as unsupported extensions. The candidate pool constrains attainable accuracy: redundant Top-$K$ spans can trade coverage for alternative boundary hypotheses, and a missing suitable candidate cannot be recovered by later refinement.[^f2g-paper]

## Relationships

- **Instantiates:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) through cited candidate-span selection and evidence-conditioned interval refinement; it is evidence for temporal grounding, not general temporal reasoning.[^f2g-paper]
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through a compact, video-wide Top-$K$ proposal pool; the reported method does not establish lossless access to arbitrary-duration video.[^f2g-paper]
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through multi-view predictive pretraining of boundary-sensitive temporal features.[^f2g-paper]
- **Related to:** [UniTime](unitime.md), which makes timestamps addressable and retrieves coarse-to-fine, whereas F2G cites learned event-span hypotheses before refining the interval.[^f2g-paper]
- **Related to:** [VideoITG](videoitg.md), which selects instruction-conditioned frames for a separate answering Video-LLM, whereas F2G presents candidate span evidence to the grounding LLM in one structured response.[^f2g-paper]

[^f2g-paper]: [Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding](../raw/Foresee-to-Ground/main.tex)
