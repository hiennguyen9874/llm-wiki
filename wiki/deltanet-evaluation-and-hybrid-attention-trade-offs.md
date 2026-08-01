---
type: Concept
title: DeltaNet evaluation and hybrid-attention trade-offs
description: Parallel DeltaNet improves several reported linear-recurrent and recall benchmarks, while hybrid local or global attention improves its results and state-size, throughput, and length-generalization limits remain.
tags: [deltanet, evaluation, hybrid-attention, linear-attention, retrieval]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:28:38Z }
sources:
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
  - id: gated-deltanet-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
---

# DeltaNet evaluation and hybrid-attention trade-offs

The paper reports that DeltaNet is stronger than its tested linear-recurrent baselines on several language-modeling and associative-recall settings, but a fixed-state DeltaNet loses to a larger-state GLA on some 1.3B recall tasks. Interleaving sliding-window attention or inserting two global-attention layers improves the reported results, supporting complementarity rather than pure-recurrence dominance.[^parallel-deltanet-2024]

## Reported language-model results

All main-table models use the same SlimPajama subset and Mistral tokenizer; the 340M and 1.3B configurations train for 15B and 100B tokens, respectively. At 340M with convolution, DeltaNet reports 28.24 WikiText perplexity and 42.1 average zero-shot accuracy, versus 28.39 and 41.8 for Mamba with convolution. At 1.3B, it reports 16.87 perplexity and 51.6 average zero-shot accuracy, versus 17.06 and 50.0 for Mamba, and 17.25 and 50.4 for convolutional GLA.[^parallel-deltanet-2024]

On the paper’s recall-intensive SWDE/SQuAD/FDA evaluations, 340M DeltaNet with convolution reports 26.4/28.9/12.8 accuracy, higher than the matched-state GLA variants shown in the table. At 1.3B, however, its 49.5/37.4/17.2 trails the larger-state GLA without convolution at 50.6/42.6/19.9. This is compatible with the paper’s interpretation that DeltaNet’s slower practical head-width scaling limits memory size; it does not isolate recurrence from convolution, state size, or other architectural choices.[^parallel-deltanet-2024]

## Synthetic recall and larger-scale evidence

The authors report perfect accuracy in their hardest shown multi-query associative-recall setting. The displayed RegBench curve for DeltaNet without short convolution rises from 44.5% at 1,000 training examples to 85.0% at 10,000, but remains below the plotted Transformer and Mamba-with-convolution results at the latter point. On the MAD suite, DeltaNet leads Fuzzy Recall (35.7), In-Context Recall (100), Noisy Recall (100), and Selective Copy (100), but scores 52.8 on Memorize and has a 71.8 average versus Transformer’s 74.5. Thus the synthetic evidence is capability-specific, not a uniform win.[^parallel-deltanet-2024]

A 3B DeltaNet trained on 1T tokens reports a 59.8 six-task zero-shot average: below the cited Transformer PowerLM-3B’s 62.3, but above the cited recurrent baselines in the table. Those external baselines use differing training-token counts, so the comparison is suggestive rather than controlled.[^parallel-deltanet-2024]

## Hybrid attention

At 1.3B, alternating DeltaNet with sliding-window attention reports 16.56 WikiText perplexity and 52.1 average zero-shot accuracy. Replacing just two DeltaNet layers with global attention reports 16.55 and 51.8, while yielding the strongest reported recall-intensive results: 71.0 SWDE, 43.0 SQuAD, and 29.8 FDA. The paper’s Transformer++ reference reports 16.85 perplexity, 50.9 average accuracy, and 66.6/31.5/27.4 on those recall tasks.[^parallel-deltanet-2024]

These designs address limits of fixed associative state differently: sliding-window layers provide exact local token access every other layer, while two global layers provide selected full-context access. Both remove the claim that the corresponding model has exclusively fixed, sequence-independent attention state.[^parallel-deltanet-2024]

## Limits

The source says DeltaNet’s training throughput is close to GLA’s and faster than Mamba’s in its plotted 1.3B H100 comparison, while separately identifying DeltaNet as slower than GLA because its state-to-state dependency is not elementwise. It also reports limited length generalization relative to GLA and RetNet, speculating that the absence of explicit decay is responsible. These findings motivate adding a decay gate, but do not prove that diagnosis or guarantee a gated variant resolves it.[^parallel-deltanet-2024]

The reported tables give point estimates without run-to-run uncertainty. Main 340M/1.3B experiments use eight H100 GPUs; the standalone throughput plot uses one H100. Results should therefore not be generalized beyond the documented training recipe, state sizes, evaluations, and hardware.[^parallel-deltanet-2024]

## Relationships

- **Evaluates:** [Parallel DeltaNet chunkwise training](parallel-deltanet-chunkwise-training.md) in synthetic, language-modeling, and throughput settings.
- **Evaluates:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md)’s corrective update against additive and elementwise-decay recurrent baselines.
- **Extended by:** [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md), which evaluates scalar decay plus the corrective update under a separate training recipe.[^gated-deltanet-2025]
- **Mitigates limits of:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) through local or global token-addressable attention.
- **Supports hybrid use of:** [Self-attention computational profile](self-attention-computational-profile.md), with scope limited to the paper’s architectures and tests.

[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 4–5, Tables 2–3, Figures 1–3, and experimental appendix.

[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–5 and Appendix B.
