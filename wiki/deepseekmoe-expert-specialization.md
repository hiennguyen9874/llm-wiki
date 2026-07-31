---
type: Concept
title: DeepSeekMoE expert specialization
description: DeepSeekMoE replaces a few large FFN experts with many smaller routed experts plus always-on shared experts, increasing routing composition while keeping expert-FFN compute approximately fixed.
tags: [deepseekmoe, mixture-of-experts, sparse-models, routing, expert-specialization]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:19:23Z }
sources:
  - id: deepseekmoe-overview-2026
    resource: ../raw/DeepSeekMoE.md
    title: "DeepSeekMoE: chuyên biệt hóa expert trong LLM"
---

# DeepSeekMoE expert specialization

DeepSeekMoE uses fine-grained routed experts and always-active shared experts to reduce, respectively, mixed specialization within an expert and duplication of common knowledge across experts. The design increases the number of expert combinations available to a token without proportionally increasing the routed-FFN computation.[^deepseekmoe-overview-2026]

## Fine-grained routed experts

Starting from $N$ experts of FFN size $d_{\mathrm{ff}}$ with top-$K$ routing, DeepSeekMoE splits each expert into $m$ smaller experts. It then has $mN$ experts of roughly $d_{\mathrm{ff}}/m$ each and routes each token to top-$mK$ experts. Thus, total expert parameters and the nominal routed-FFN compute per token remain approximately constant, while routing can compose much finer-grained functions.[^deepseekmoe-overview-2026]

The supplied overview characterizes this as reducing *knowledge hybridity*: with only a few large experts, one expert may have to cover unrelated functions such as syntax, mathematics, code, and world knowledge. It reports the illustrative change from selecting 2 of 16 experts (120 combinations) to selecting 8 of 64 experts (4,426,165,368 combinations); this measures available combinations, not combinations known to be used in training.[^deepseekmoe-overview-2026]

## Shared expert isolation

Some experts are shared: they run for every token and are not selected by the router. Routed experts remain token-selective. The shared path is intended to hold broadly useful patterns, leaving routed-expert capacity for more conditional knowledge and reducing *knowledge redundancy* among routed experts.[^deepseekmoe-overview-2026]

The reported 16B configuration uses two shared experts plus six selected routed experts out of 64, with each expert roughly one quarter of a standard FFN. It leaves the first layer dense because load balancing in that layer reportedly converged slowly.[^deepseekmoe-overview-2026]

## Relationships

- **Specializes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) with top-$k$ fine-grained routing and an always-on shared path.
- **Contrasts with:** [Switch Transformer sparse routing](switch-transformer-sparse-routing.md), which uses top-1 routing and has no shared-expert path in the supplied comparison.
- **Evaluated by:** [DeepSeekMoE evaluation and deployment trade-offs](deepseekmoe-evaluation-and-deployment-trade-offs.md).

## Evidence limits

This page compiles a secondary Vietnamese overview that cites the DeepSeekMoE paper and project repository; neither primary artifact is bundled here. Architectural details and the authors’ interpretation of specialization therefore remain attributed to the overview.[^deepseekmoe-overview-2026]

[^deepseekmoe-overview-2026]: “DeepSeekMoE: chuyên biệt hóa expert trong LLM,” [raw source](../raw/DeepSeekMoE.md), citing DeepSeek-AI, “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024).