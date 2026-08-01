---
type: Concept
title: DeepSeekMoE expert specialization
description: DeepSeekMoE replaces a few large FFN experts with many smaller routed experts plus always-on shared experts, increasing routing composition while keeping expert-FFN compute approximately fixed.
tags: [deepseekmoe, mixture-of-experts, sparse-models, routing, expert-specialization]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:06:40Z }
sources:
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
---

# DeepSeekMoE expert specialization

DeepSeekMoE uses fine-grained routed experts and always-active shared experts to reduce, respectively, mixed specialization within an expert and duplication of common knowledge across experts. The design increases the number of expert combinations available to a token without proportionally increasing the routed-FFN computation.[^deepseekmoe-2024]

## Fine-grained routed experts

Starting from $N$ experts of FFN size $d_{\mathrm{ff}}$ with top-$K$ routing, DeepSeekMoE splits each expert into $m$ smaller experts. It then has $mN$ experts of roughly $d_{\mathrm{ff}}/m$ each and routes each token to top-$mK$ experts. Thus, total expert parameters and the nominal routed-FFN compute per token remain approximately constant, while routing can compose much finer-grained functions.[^deepseekmoe-2024]

The paper characterizes this as reducing *knowledge hybridity*: with only a few large experts, one expert may have to cover unrelated functions such as syntax, mathematics, code, and world knowledge. It reports the illustrative change from selecting 2 of 16 experts (120 combinations) to selecting 8 of 64 experts (4,426,165,368 combinations); this measures available combinations, not combinations known to be used in training.[^deepseekmoe-2024]

## Shared expert isolation

Some experts are shared: they run for every token and are not selected by the router. Routed experts remain token-selective. The shared path is intended to hold broadly useful patterns, leaving routed-expert capacity for more conditional knowledge and reducing *knowledge redundancy* among routed experts.[^deepseekmoe-2024]

The reported 16B configuration uses two shared experts plus six selected routed experts out of 64, with each expert roughly one quarter of a standard FFN. It leaves the first layer dense because load balancing in that layer reportedly converged slowly.[^deepseekmoe-2024]

## Load-balance objectives

DeepSeekMoE applies a small expert-level auxiliary loss to prevent routing collapse, using both the fraction of tokens assigned to an expert and its mean routing score. For distributed expert placement, it separately groups routed experts by device and applies a device-level loss to balance aggregate device computation; the authors explicitly prefer this over strict per-expert balancing, which they report can harm model quality. In the 2B and 16B runs, all experts for a layer fit on one device, so they did not use the device-level loss or drop tokens; the preliminary 145B run uses expert parallelism and a device-level balance factor of 0.05.[^deepseekmoe-2024]

## Relationships

- **Specializes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) with top-$k$ fine-grained routing and an always-on shared path.
- **Contrasts with:** [Switch Transformer sparse routing](switch-transformer-sparse-routing.md), which uses top-1 routing rather than the paper’s fine-grained shared-and-routed design.
- **Evaluated by:** [DeepSeekMoE evaluation and deployment trade-offs](deepseekmoe-evaluation-and-deployment-trade-offs.md).

## Evidence limits

The bundled v1 paper is primary evidence for the architecture and its reported experiments. “Knowledge hybridity,” “redundancy,” and “specialization” are the authors’ interpretations of ablations and routing sensitivity, not direct semantic labels for individual experts.[^deepseekmoe-2024]

[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Sections 3–4 and Appendix A.