---
type: Concept
title: Gated DeltaNet evaluation and hybrid trade-offs
description: Gated DeltaNet reports better matched recurrent-model results than Mamba2 and DeltaNet, while attention hybrids improve retrieval and long-context scores under the paper’s training and hardware settings.
tags: [deltanet, evaluation, hybrid-attention, linear-attention, long-context, mamba]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:28:38Z }
sources:
  - id: gated-deltanet-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
---

# Gated DeltaNet evaluation and hybrid trade-offs

In the paper’s matched 1.3B-parameter, 100B-token setup, pure Gated DeltaNet reports stronger language-model, commonsense, recall, and LongBench averages than its listed recurrent baselines. Its H1/H2 hybrids report larger retrieval and long-context gains, so the evidence supports combining corrective fixed-state memory with local attention rather than claiming that recurrence alone matches token-addressable attention.[^gated-deltanet-2025]

## Experimental scope

The main comparisons train 1.3B-parameter models for 100B FineWeb-Edu tokens using the Llama 2 tokenizer, AdamW, a 4K training length, and a 2K sliding-attention window for Samba and the hybrids. The source reports point estimates, not repeated-seed uncertainty.[^gated-deltanet-2025]

## Reported recurrent-model results

On WikiText/LAMBADA, the paper reports Gated DeltaNet perplexities of 16.42 and 12.17 and a seven-task zero-shot commonsense average of 55.32. The corresponding reported averages are 54.89 for Mamba2 and 52.14 for DeltaNet. This is a comparison in the supplied recipe, not a general quality ranking.[^gated-deltanet-2025]

On six real-world recall tasks with inputs truncated to 2K tokens, pure Gated DeltaNet reports a 30.6 average, versus 29.8 for Mamba2 and 26.2 for DeltaNet. On the 14-task LongBench table, it reports a 16.6 recurrent-model average, the highest among the listed recurrent rows.[^gated-deltanet-2025]

The S-NIAH diagnostics qualify the aggregate results: ungated DeltaNet best retains simple repeated passkeys at longer lengths, while Mamba2’s decay helps filter realistic distractor context but loses retention. Gated DeltaNet improves the more complex distractor/UUID cases in the shown suite, consistent with—but not independently proving—the proposed division between targeted correction and broad forgetting.[^gated-deltanet-2025]

## Hybrid results and speed

H1 reports a 56.40 commonsense average and 39.0 recall average; H2 reports 56.18 and 40.1. Their LongBench averages are 17.8 and 18.4, respectively. These gains are inseparable from reintroducing sliding-window attention and, for H2, Mamba2 layers.[^gated-deltanet-2025]

On the paper’s single-H100 throughput figure, Gated DeltaNet stays near DeltaNet (about 46K tokens/s across the plotted fixed sequence-length-times-batch configurations) and trails Mamba2 by roughly 2–3K tokens/s. H1/H2 are faster than the standalone gated recurrence in that figure, while the full-attention baseline falls as sequence length increases. These are implementation-specific training-throughput measurements, not decode-latency or universal hardware claims.[^gated-deltanet-2025]

## Limits

- The study uses unaligned pretrained models, and the authors attribute part of the real-world retrieval error to repetition; instruction-tuned behavior was not evaluated.[^gated-deltanet-2025]
- Most main claims are from one 1.3B/100B-token recipe with 4K training context; extrapolation is tested only to 20K on six perplexity benchmarks.[^gated-deltanet-2025]
- Hybrid gains do not isolate the gated rule from Mamba2 or sliding-window attention, and reported results lack independent replication or variance estimates.[^gated-deltanet-2025]

## Relationships

- **Evaluates:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md).
- **Extends evaluation of:** [DeltaNet evaluation and hybrid-attention trade-offs](deltanet-evaluation-and-hybrid-attention-trade-offs.md) with a decay-gated corrective recurrence.
- **Compares with:** [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md) under a different training corpus and evaluation configuration.
- **Supports hybrid use of:** [Self-attention computational profile](self-attention-computational-profile.md) for local token-addressable access.

[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 4–5, Tables 1–4, Figures 2–3, and Appendix B.
