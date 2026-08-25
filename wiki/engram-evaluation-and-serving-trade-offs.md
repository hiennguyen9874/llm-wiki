---
type: Concept
title: Engram evaluation and serving trade-offs
description: Author-run Engram experiments report an optimal mixed MoE-memory allocation, improved matched 27B results and 32K retrieval, while training communication, host lookup, benchmark comparability, and unreplicated mechanistic claims limit inference.
tags: [evaluation, embeddings, n-grams, conditional-memory, mixture-of-experts, long-context, serving]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T15:33:29Z }
sources:
  - id: conditional-memory-2026
    resource: ../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex
    title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
---

# Engram evaluation and serving trade-offs

The authors report that allocating part of an otherwise sparse MoE parameter budget to Engram improves their matched validation loss and 27B benchmark suite, and that an Engram-27B model improves selected 32K long-context tasks over their MoE-27B baseline. The evidence is author-run and configuration-specific; active FLOPs do not include the storage, all-to-all lookup, host transfer, or cache costs needed to operate large tables.[^conditional-memory-2026]

## Reported sparsity-allocation result

The paper defines inactive capacity as $P_{\rm sparse}=P_{\rm tot}-P_{\rm act}$ and allocates fraction $\rho$ to MoE experts, with the remainder assigned to Engram. Within each of two reported FLOP budgets, total and active parameters were held fixed at about a 10:1 total-to-active ratio. Validation loss was U-shaped in $\rho$: reassigning roughly 20–25% of sparse capacity to Engram ($\rho\approx0.75$–$0.80$) was the listed optimum. At the $6\times10^{20}$-FLOP setting, loss changed from 1.7248 for pure MoE to 1.7109 near the optimum.[^conditional-memory-2026]

With a fixed approximately 3B-total/568M-active MoE backbone trained for 100B tokens, the authors also increase Engram slots from $2.58\times10^5$ to $10^7$ (up to approximately 13B added parameters). Its displayed validation-loss curve decreases approximately linearly against log slot count and remains below the plotted Over-Encoding curve. This is an observed sweep, not a general scaling law or a controlled conclusion about all n-gram designs.[^conditional-memory-2026]

## Matched pre-training and downstream results

All reported 27B comparisons use 30 blocks, MLA, mHC, 3.8B activated parameters, and 262B training tokens. Engram-27B retains 26.7B total parameters by replacing 17 of the MoE-27B model’s 72 routed experts with a 5.7B Engram table; it uses 55 routed experts, top-6 routing, and Engram at layers 2 and 15. On the listed held-out losses, MoE-27B/Engram-27B are 1.960/1.950 on Pile and 1.634/1.622 on the validation set.[^conditional-memory-2026]

Selected author-reported score changes for Engram-27B relative to that matched MoE baseline are MMLU 57.4→60.4, CMMLU 57.9→61.9, BBH 50.9→55.9, ARC-Challenge 70.1→73.8, HumanEval pass@1 37.8→40.8, and MATH 28.3→30.7. Engram-40B holds the same active budget while raising table parameters from 5.7B to 18.5B; it lowers listed losses further but does not exceed Engram-27B on every benchmark. The authors suggest under-training, but the presented run does not establish that explanation.[^conditional-memory-2026]

## Long-context and mechanism experiments

After 5,000 32K-context extension steps, an Engram-27B checkpoint at 46K pre-training steps is matched to the MoE-27B 50K checkpoint on stated pre-training loss (1.63). It reports Multi-Query NIAH 97.0 versus 84.2 and Variable Tracking 87.2 versus 77.0; the full 50K Engram model reports 97.0 and 89.0 respectively. Base training progress also improves results within the Engram variants, so loss matching is an important but incomplete control.[^conditional-memory-2026]

On a 12-layer 3B MoE, a fixed 1.6B Engram reference at layers 2 and 6 reaches validation loss 1.768 versus 1.808 for the baseline. A single-module layer sweep is best at layer 2 (1.770) and degrades at later insertion points. The figure reports larger regressions when removing branch-specific fusion, token compression, or context-aware gating than when removing the short convolution; these are combined-model ablations, not independent causal validation of each claimed function.[^conditional-memory-2026]

LogitLens KL curves and CKA maps are consistent with earlier Engram layers aligning with deeper MoE layers, and the authors describe this as increased “effective depth.” Disabling the table at inference retains 81–93% of listed reading-comprehension scores but only 29–44% of listed factual-knowledge scores. Both probes alter the inference path or interpret similarity measurements, so they support a hypothesis about representation use rather than proving where knowledge is stored or why reasoning improved.[^conditional-memory-2026]

## Reported offload measurement

A nano-vLLM-derived harness puts a 100B-parameter table in host DRAM and asynchronously prefetches for an Engram layer in block 2. On one NVIDIA H800, 512 sequences, and uniform sequence lengths 100–1,024, reported throughput changes from 9,031.62 to 8,858.28 tok/s for a 4B dense backbone and 6,315.52 to 6,140.02 tok/s for an 8B dense backbone (at most 2.8%). This measures dense backbones rather than the 27B MoE comparison, one hardware/workload shape, and an all-host-memory table; it does not validate end-to-end MoE serving, cache hierarchy behavior, latency percentiles, or other interconnects.[^conditional-memory-2026]

## Relationships

- **Evaluates:** [Engram conditional-memory architecture](engram-conditional-memory-architecture.md).
- **Compares with:** [Over-tokenized Transformer evaluation and systems trade-offs](over-tokenized-transformer-evaluation-and-systems-trade-offs.md) and [SCONE evaluation and serving trade-offs](scone-evaluation-and-serving-trade-offs.md); their n-gram parameterization, placement, training computation, and storage layout differ.
- **Qualifies:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md): active parameters and FLOPs alone do not account for either expert dispatch or memory lookup/storage.

## Evidence limits

All quality, scaling, mechanistic, and throughput results are author-reported. The source bundle provides no inspected training/evaluation implementation, run variance, or independent reproduction. Benchmarks use varied prompting/shot counts and include an internal TriviaQA-ZH set; loss and score differences therefore cannot be generalized to other data, tokenizers, contexts, model scales, or serving workloads.[^conditional-memory-2026]

[^conditional-memory-2026]: Xin Cheng et al., “Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models,” [LaTeX source](../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex), Abstract; Sections 3–5; Appendix “Detailed Model Architecture and Hyper Parameters”; and rendered bundled scaling, ablation, benchmark, sensitivity, and LogitLens/CKA figures.