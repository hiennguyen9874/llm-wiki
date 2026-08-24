---
type: Concept
title: Gated DeltaNet-2 evaluation and hybrid trade-offs
description: In one author-run 1.3B/100B-token comparison, Gated DeltaNet-2 leads the listed recurrent and hybrid baselines on aggregate language, reasoning, synthetic retrieval, and real-world recall metrics, with a modest H100 training-throughput cost versus KDA.
tags: [deltanet, evaluation, hybrid-attention, linear-attention, long-context, retrieval]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:20:33Z }
sources:
  - id: gated-deltanet-2-2026
    resource: ../raw/2605.22791_GatedDeltaNet-2/main.tex
    title: "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
---

# Gated DeltaNet-2 evaluation and hybrid trade-offs

In the paper’s author-run, matched 1.3B-parameter, 100B-FineWeb-Edu-token study, Gated DeltaNet-2 has the best reported aggregate among its listed Mamba-2, Gated DeltaNet, KDA, and Mamba-3 recurrent and SWA-hybrid rows. The result is configuration-bound evidence for decoupled gating, not an independent or universal architecture ranking.[^gated-deltanet-2-2026]

## Experimental scope

Models use AdamW (peak learning rate $4\times10^{-4}$), 4K training sequences, 0.5M-token global batches, and a 1B-token warm-up. Recurrent delta models use 16 heads with $d_k=d_v=128$; the paper matches their main recurrent state size to the Mamba-2/3 settings. Hybrid models use a 2K SWA window. The source reports point estimates, with no multi-seed uncertainty or independent replication.[^gated-deltanet-2-2026]

## Reported results

For recurrent-only models, Gated DeltaNet-2 reports WikiText/LAMBADA perplexities of 15.90/11.41 and a LAMBADA-plus-commonsense average of 53.11, versus the next highest listed recurrent average of 52.39 for Mamba-3 MIMO. Its hybrid row reports 15.62/10.43 and 53.97, versus 52.72 for the next highest listed hybrid average. These aggregate comparisons are limited to the source’s model and training recipe.[^gated-deltanet-2-2026]

On six real-world recall tasks truncated to 2K tokens, the recurrent model reports a 29.88 average (KDA: 28.67; Mamba-3 MIMO: 28.35); the hybrid reports 42.28 (Mamba-3 SISO: 41.01). On the interference-heavy multi-key RULER NIAH task at 1K/2K/4K, the recurrent row reports 72.6/51.4/37.8%, and the hybrid row 93.0/84.6/48.0%; these are the highest listed values within their respective table sections.[^gated-deltanet-2-2026]

Ablations retain parameter count while scalarizing one gate at runtime. Channel-wise erase with scalar write (29.51 recall average) is closer to the full recurrent model (29.88) than scalar erase with channel-wise write (28.92), but both trail the full 53.11 commonsense average and the listed retrieval diagnostics. Expanding erase-gate range from $[0,1]$ to $[0,2]$ gives no consistent gain at this scale.[^gated-deltanet-2-2026]

## Throughput and deployment boundary

On the paper’s single-H100 hybrid training plot, Gated DeltaNet-2 declines from 38.00K to 36.11K tokens/s as sequence-length-by-batch settings run from $2$K$\times8$ to $16$K$\times1$. It remains far flatter than the plotted Transformer (45.83K to 29.36K), but trails KDA (39.81K to 38.50K). These are training-throughput measurements under one fused-kernel implementation; they do not establish decoding latency, serving throughput, or portability to other accelerators.[^gated-deltanet-2-2026]

The hybrid gains also cannot be attributed solely to the recurrent update because SWA restores local token-addressable interaction. The reported real-world retrieval gaps on NQ and DROP further indicate that decoupled fixed-state editing does not remove the need for local evidence aggregation.[^gated-deltanet-2-2026]

## Relationships

- **Evaluates:** [Gated DeltaNet-2 decoupled delta rule and training](gated-deltanet-2-decoupled-delta-rule-and-training.md).
- **Compares with:** [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md) and [Mamba-3 evaluation and inference trade-offs](mamba-3-evaluation-and-inference-trade-offs.md), under a different model configuration and kernel stack.
- **Supports hybrid use of:** [Self-attention computational profile](self-attention-computational-profile.md) for bounded local token access alongside fixed-state memory.

## Evidence limits

All metric and throughput values are author-reported point estimates. The corpus, 100B-token budget, 4K training length, state layout, benchmark truncation, SWA window, kernel implementation, H100 hardware, and lack of reported variance constrain comparison and deployment conclusions.

[^gated-deltanet-2-2026]: Ali Hatamizadeh, Yejin Choi, and Jan Kautz, “Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention,” supplied LaTeX source, [source](../raw/2605.22791_GatedDeltaNet-2/main.tex), Section 4, Tables 1–4, Figure 2, and Appendix D.
