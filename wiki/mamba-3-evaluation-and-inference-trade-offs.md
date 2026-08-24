---
type: Concept
title: Mamba-3 evaluation and inference trade-offs
description: In author-run 100B-token tests, Mamba-3 improves listed recurrent and Transformer baselines, while fixed-state retrieval limits, parameter matching, and H100 kernel-specific latency qualify the results.
tags: [mamba, mamba-3, evaluation, inference, retrieval, ssm]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:15:43Z }
sources:
  - id: lahoti-et-al-2026
    resource: ../raw/2603.15569_Mamba-3/structure.tex
    title: "Mamba-3: Improved Sequence Modeling using State Space Principles"
---

# Mamba-3 evaluation and inference trade-offs

In the authors’ matched 100B-FineWeb-Edu-token comparisons, Mamba-3 SISO improves the listed Mamba-2, Gated DeltaNet, and Transformer baselines at all four reported scales; rank-4 MIMO improves the reported 1.5B average further. The results are author-run, configuration-bound comparisons, and MIMO’s quality gain is coupled to a reduced MLP width used for parameter matching.[^lahoti-et-al-2026]

## Experimental scope and language modeling

The report trains 180M, 440M, 880M, and 1.5B models for 100B FineWeb-Edu tokens, at 2K context length, with a Llama-3.1 tokenizer and BF16. Mamba variants use state size 128 and head dimension 64; the listed Gated DeltaNet has different Q/K and value dimensions, so equal parameter count does not make the internal memory layouts identical.[^lahoti-et-al-2026]

At 1.5B, the reported FineWeb-Edu validation perplexity / eight-task average is 10.35 / 56.4 for Mamba-3 SISO, compared with 10.45 / 55.8 for Gated DeltaNet, 10.47 / 55.7 for Mamba-2, and 10.51 / 55.4 for the Transformer. Mamba-3 MIMO ($R=4$) reports 10.24 / 57.6; its MLP width is reduced from 4096 to 3824 to match the SISO parameter count. These point estimates do not include multi-seed uncertainty.[^lahoti-et-al-2026]

At 440M, an ablation reports test perplexity 16.68 without both $B/C$ biases and trapezoidal discretization, 16.49 without bias, and 15.72 with both; adding an external short convolution to the final variant yields 15.85. This supports their joint usefulness in that recipe, not that convolution is generally unnecessary for recurrent models.[^lahoti-et-al-2026]

## State tracking, retrieval, and hybrids

On the report’s formal-language suite, Mamba-3’s data-dependent rotary variant reports 100.00% parity, 98.51% unbracketed modular arithmetic, and 87.75% bracketed modular arithmetic; Mamba-2 reports 0.90%, 47.81%, and 0.88%, respectively. The authors tune the listed small models and report the best validation result, so the table demonstrates capability under that protocol rather than production reasoning performance.[^lahoti-et-al-2026]

The 1.5B pure Mamba-3 models are competitive on several 2K cloze retrieval tasks and synthetic NIAH cases, but the paper reports weaker semi-structured/unstructured extraction than the Transformer on SWDE and FDA. A 5:1 Mamba-3/NoPE-attention hybrid reintroduces token-addressable access. Adding pre-gate grouped RMSNorm raises reported long NIAH performance but changes real-world retrieval results, leaving norm type and placement unresolved.[^lahoti-et-al-2026]

## Decode and kernel boundary

The authors frame MIMO as increasing arithmetic intensity in memory-bound recurrent decode: their formula gives about 2.5 operations/byte for a BF16 SISO update and growth with rank for MIMO. On a single H100 at batch 128, their one-token BF16 latency at state size 128 is 0.156 ms for Mamba-3 SISO, 0.179 ms for MIMO, 0.203 ms for Mamba-2, and 0.257 ms for Gated DeltaNet. The methods use different released or new kernels; Mamba-3 decode is implemented in CuTe plus Triton, so the comparison is also an implementation comparison.[^lahoti-et-al-2026]

In a separate 1.5B end-to-end H100 test at batch 128, Mamba-3 SISO reports lower prefill-plus-equal-length-decode time than Mamba-2 and Gated DeltaNet through 16K tokens, while MIMO is close to Mamba-2 but has higher prefill cost. The Transformer comparison is vLLM Llama-3.2-1B rather than a parameter-matched model, and its 16K batch-128 result is extrapolated from batch 16; it is not a controlled universal serving comparison.[^lahoti-et-al-2026]

## Relationships

- **Evaluates:** [Mamba-3 architecture and state-space methods](mamba-3-architecture-and-state-space-methods.md).
- **Compares with:** [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md) and [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md), under a distinct corpus, tokenizer, context length, kernel stack, and task suite.
- **Supports hybrid use of:** [Self-attention computational profile](self-attention-computational-profile.md), because the paper’s fixed-state mixer retains retrieval limits that periodic attention mitigates.

## Evidence limits

All quality, retrieval, throughput, and latency values are from the authors’ source bundle; no independent replication or variance estimates are provided. Fixed-state recurrence does not imply lossless long-context retrieval, and the reported 2K training context, state size, kernel fusion, precision, batch size, GPU, and comparison asymmetries constrain deployment conclusions.

[^lahoti-et-al-2026]: Aakash Lahoti et al., “Mamba-3: Improved Sequence Modeling using State Space Principles,” supplied LaTeX source, [source](../raw/2603.15569_Mamba-3/structure.tex), Sections 4–5, Tables 1–5, and Appendices D–E.
