---
type: Concept
title: Kimi Linear hybrid attention architecture
description: Kimi Linear interleaves three fixed-state Kimi Delta Attention layers with one global NoPE MLA layer to trade bounded recurrent memory against periodic token-level retrieval.
tags: [kimi-linear, hybrid-attention, linear-attention, long-context, mixture-of-experts]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T01:48:53Z }
sources:
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
---

# Kimi Linear hybrid attention architecture

Kimi Linear is a layerwise hybrid intended to retain fixed-state linear attention’s decode efficiency without relying on it for all retrieval. Its repeating token-mixing pattern uses three Kimi Delta Attention (KDA) layers followed by one global Multi-Head Latent Attention (MLA) layer; the report’s 48B-total, 3B-active MoE model uses this pattern and delegates positional bias to KDA while applying no explicit positional encoding in the MLA layers.[^kimi-linear-2025]

## Architecture

KDA maintains a fixed $d_k\times d_v$ recurrent state per head, with $d_k=d_v=128$ in the reported models. During prefill and training it uses a chunkwise-parallel kernel; autoregressive decoding switches to the recurrent update. Periodic MLA layers preserve direct access to token context, addressing the exact-copying and long-range retrieval limits of a purely fixed-state architecture.[^kimi-linear-2025]

The authors chose whole-layer rather than mixed-head hybridization for infrastructure simplicity and training stability. In their controlled ablation, the KDA:MLA ratios produced validation perplexities of 5.65 at 3:1, 5.66 at 1:1, 5.70 at 7:1, 5.82 at 15:1, and 5.77 for full MLA (0:1). The 3:1 choice is therefore an empirical result for this recipe, not a universal optimum.[^kimi-linear-2025]

All MLA layers use NoPE. The report argues that KDA’s data-dependent transition supplies positional and recency information, while NoPE lets MLA avoid RoPE retuning during context extension and permits conversion to pure MQA at inference. This assignment of positional responsibility is architecture-specific; its advantage is supported by the report’s Kimi Linear versus Kimi Linear (RoPE) long-context comparison rather than an isolated positional-encoding experiment.[^kimi-linear-2025]

## Reported quality evidence

The matched 1.4T-token comparison used the same 48B-total, 3B-active MoE scale, training setup, and post-training recipes for Kimi Linear, full MLA, and hybrid GDN-H. Kimi Linear led most reported base and instruction benchmarks, but not every task: for example, GDN-H led base EvalPlus, while MLA led instruction-tuned EvalPlus and LongBench V2.[^kimi-linear-2025]

At 128K, the report gives Kimi Linear a 54.5 average across its long-context suite, versus 52.2 for MLA, 51.2 for GDN-H, and 51.8 for the RoPE Kimi Linear variant. Kimi Linear led RULER (84.3), MRCR (29.6), HELMET-ICL (90.0), RepoQA (68.5), and one Long Code Arena subtask, while MLA led LongBench V2, Frames, and the other Long Code Arena subtask. These are author-run evaluations using an internal framework derived from LM Evaluation Harness.[^kimi-linear-2025]

The report also shows faster gains than MLA during one in-house mathematics RL run with matched algorithms and hyperparameters. Because the training prompts are internal and the figure supplies curves rather than uncertainty estimates, this supports a result for that run rather than a general claim that hybrid linear attention improves RL scaling.[^kimi-linear-2025]

## Reported efficiency evidence

The 3:1 pattern leaves only one quarter of token-mixing layers with a sequence-growing KV cache, motivating the report’s claim of up to 75% KV-cache reduction relative to full MLA. KDA state size itself is constant in sequence length, but total model decode memory still includes the periodic MLA caches and other runtime state.[^kimi-linear-2025]

On the reported 48B configuration at batch size one and a 1M-token context, prefill latency was 22.753 seconds for Kimi Linear versus 65.460 seconds for MLA (about $2.9\times$), and decode time per output token was 7.99 ms versus 17.76 ms (about $2.2\times$). A separate maximum-throughput setup used the freed memory for larger batches and reported 1.84 ms versus 11.48 ms, or $6.3\times$. The $6.3\times$ figure should not be conflated with the batch-one latency result.[^kimi-linear-2025]

## Relationships

- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through KDA’s channel-wise decay and corrective state update.
- **Mitigates limits of:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) with periodic global MLA retrieval.
- **Contrasts with:** [Rotary position embedding (RoPE)](rotary-position-embedding.md) by assigning positional behavior to KDA and leaving global MLA layers without explicit positional encoding.
- **Enables:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), according to the report’s claim that NoPE MLA can be converted to pure MQA for inference.

## Evidence limits

This page compiles the authors’ primary technical report, including its included TeX tables, plots, derivations, and pseudocode. Generated minted caches, bibliography data, logos, and decorative image assets were excluded from claim extraction. The comparisons are not independently replicated here. Most quality experiments control model scale and recipes, but changing the attention mechanism also changes positional treatment and kernels, so the results establish performance for the full Kimi Linear design rather than isolating every component. Hardware details needed to generalize the latency and throughput measurements are not fully specified in the report text.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), including the referenced section, table, figure, and appendix TeX files in the same source directory.
