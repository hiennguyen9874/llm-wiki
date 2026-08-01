---
type: Concept
title: DeepSeekMoE evaluation and deployment trade-offs
description: DeepSeekMoE reports dense-7B-comparable aggregate quality at lower expert-FFN FLOPs, while weight memory, routing and communication overhead, data confounding, and limited specialization evidence qualify that result.
tags: [deepseekmoe, mixture-of-experts, evaluation, inference, load-balancing]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:06:40Z }
sources:
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
---

# DeepSeekMoE evaluation and deployment trade-offs

DeepSeekMoE’s paper reports that its 16B model reaches roughly comparable aggregate results to DeepSeek 7B with substantially lower reported FLOPs, but sparse activation reduces neither total weight storage nor system overhead. Its specialization evidence is indirect, and comparisons with differently trained models do not isolate architecture from data.[^deepseekmoe-2024]

## Reported results

DeepSeekMoE 16B has 16.4B total and 2.8B activated parameters per token, and was trained for 2T tokens from the authors’ multilingual corpus. Against the 6.9B-parameter dense DeepSeek 7B trained on the same corpus and token count, it uses 74.4T versus 183.5T FLOPs per 4K tokens (40.5%) and is reported to have broadly comparable aggregate benchmark quality. It was stronger on Pile BPB, HellaSwag, ARC, math, code, and retrieval-style QA, but weaker on RACE, DROP, MMLU, WinoGrande, CLUEWSC, CEval, and CMMLU. The paper attributes the multiple-choice weakness to its 0.5B attention-parameter budget versus DeepSeek 7B’s 2.5B; that attribution is an internal correlation, not an isolated causal test.[^deepseekmoe-2024]

At smaller scale, the paper reports that removing shared experts and adding a routed expert at matched compute raised Pile loss from 1.808 to 2.414. It also reports ablations in which removing high-score experts harms DeepSeekMoE more than GShard, and fewer routed experts can approach GShard loss. These are suggestive of lower redundancy and specialization, but they do not directly identify a semantic capability learned by any individual expert.[^deepseekmoe-2024]

## Preliminary 145B scale-up

The v1 paper’s 145B result is explicitly preliminary: models were trained on 245B rather than the 16B run’s 2T tokens. DeepSeekMoE 145B (144.6B total, 22.2B active) is reported to outperform the matched-training GShard 137B and be broadly comparable to dense DeepSeek 67B at 585.6T versus 2,057.5T FLOPs per 4K tokens (28.5%). A 142B variant that activates only 2 shared and 6 routed experts is also reported to match the dense model at 18.2% of its FLOPs. These comparisons are promising but not final-scale training or independent replication.[^deepseekmoe-2024]

## Routing and systems limits

The router scores experts from each token representation, selects the highest-scoring routed experts, and uses balancing objectives over experts, devices, and communication. The authors distinguish expert-level collapse prevention from device-level balance: the latter targets aggregate device work rather than exact equal expert use, because they report that stronger expert-level constraints can compromise model quality.[^deepseekmoe-2024]

Active parameters and FLOPs are not deployment cost. All 16.4B weights still require storage, while routing, cross-device token exchange, small expert kernels, and imperfect expert parallelism add overhead. The paper reports up to roughly 2.5× inference speed relative to dense DeepSeek 7B with optimized operators, but states that realized latency depends on batch size, placement, communication bandwidth, kernels, and routing balance.[^deepseekmoe-2024]

## Interpretation limits

- MoE expands FFN capacity but does not directly strengthen attention; the paper attributes some multiple-choice weakness to the model’s smaller attention parameter budget.
- The internal DeepSeek 7B comparison controls training-token count, whereas comparisons with LLaMA 2 can also reflect corpus, tokenizer, and training-procedure differences.
- Later DeepSeek systems use additional routing and load-balancing techniques; their mechanisms should not be assumed to be identical to this initial architecture.[^deepseekmoe-2024]

## Relationships

- **Evaluates:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md).
- **Applies:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) to a reported DeepSeek architecture and deployment comparison.

## Evidence limits

The bundled v1 paper is primary evidence, but it reports author-run benchmarks and an internally curated corpus rather than independently reproduced results. Reported FLOPs exclude system costs; the 2.5× inference-speed statement is conditional on appropriate operator optimization, with no standalone latency methodology given.[^deepseekmoe-2024]

[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Sections 4–6 and Appendix A.