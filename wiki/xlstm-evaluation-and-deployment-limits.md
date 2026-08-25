---
type: Concept
title: xLSTM evaluation and deployment limits
description: xLSTM reports lower matched validation perplexity than listed Transformer, SSM, and recurrent baselines, but its quality and throughput evidence is author-run and configuration-bound.
tags: [evaluation, efficiency, recurrent-models, xlstm]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T04:31:55Z }
sources:
  - id: beck-etal-2024
    resource: ../raw/2405.04517_xLSTM/xlstm.tex
    title: "xLSTM: Extended Long Short-Term Memory"
---

# xLSTM evaluation and deployment limits

The xLSTM paper reports favorable language-model, synthetic-memory, Long Range Arena, and limited 1.3B inference results versus its selected baselines. These are author-run comparisons with particular data, precision, implementations, kernels, and architecture choices, so they support the stated experiments rather than general quality, long-context, or serving superiority.[^beck-etal-2024]

## Reported language-model comparisons

In the matched approximately 350–456M-parameter, 15B-SlimPajama-token comparison, the paper reports validation perplexity 13.43 for xLSTM[1:0] and 13.48 for xLSTM[7:1], versus 14.25 for its Llama configuration and 13.70 for Mamba. The sweep uses a common GPT-2 tokenizer, 2,048-token context, batch size 256, 30K-step decay, and mixed precision where the authors report it worked; baseline repositories and precision paths nevertheless differed.[^beck-etal-2024]

For 300B-token SlimPajama training, the paper compares roughly 125M, 350M, 760M, and 1.3B models. At 1.3B, it reports validation perplexity 8.89 for xLSTM[1:0], 9.00 for xLSTM[7:1], 9.14 for Mamba, and 9.44 for Llama. The table also reports the top average downstream-task accuracy for xLSTM[1:0] at 760M (56.12) and 1.3B (58.48), narrowly above Mamba (53.86 and 58.41); individual task winners vary, including Mamba on several ARC scores.[^beck-etal-2024]

The source’s ablation at roughly 408–608M parameters attributes the reported 15B-token perplexity reduction from 26.01 for an LSTM with residual/up-projection backbone, to 17.70 after exponential gating, to 13.48 after adding matrix memory. A separate mLSTM block ablation reports 13.43 with pre-up-projection plus causal convolution versus 15.41 without the convolution. These are useful within-source comparisons, not isolated causal proofs because multiple architecture and parameter-count changes remain.[^beck-etal-2024]

## Recall and context evidence

- In its formal-language suite, the paper reports that models without memory mixing fail some state-tracking tasks, whereas xLSTM variants with sLSTM are intended to test exponential gating plus mixing. The benchmark is synthetic, two-block, and trained only up to length 40 before evaluation at 40–256, so it does not establish general reasoning or language capability.[^beck-etal-2024]
- In MQAR, the authors report xLSTM[1:1] as their best non-Transformer model at difficult key–value settings, including up to 256 pairs and 2,048-token contexts. This probes associative recall under a constructed vocabulary and protocol, not arbitrary token-addressable retrieval.[^beck-etal-2024]
- On five reported Long Range Arena tasks, xLSTM ranks first by the source’s mean rank (1.6) and is first on retrieval and grayscale image classification; Mamba is first on Pathfinder and RGB image. The selected xLSTM type differs by task, so this is a best-of-variants result.[^beck-etal-2024]
- The 1.3B sequence-extrapolation test trains at length 2,048 and evaluates to 16,384 tokens; the source reports 16K validation perplexity 8.92 for xLSTM[7:1] and 9.01 for [1:0], versus 13.75 RWKV-4, 14.00 Mamba, and 337.83 Llama. It is a single corpus/configuration result, not a general length-generalization guarantee.[^beck-etal-2024]

## Inference and deployment boundary

For 1.3B models on an A100-80GB, batch-1 generation with a 16-token prefill, the source plots linear sequence-length generation behavior for xLSTM, Mamba, and RWKV-4, against quadratic behavior for its Llama setup. It also reports that xLSTM[1:0] sustains higher batch sizes and outperforms Mamba in the plotted decoding throughput. The authors state that full-cache Transformer compilation and `torch.compile` for Mamba did not work at the time, so these are not equivalently optimized end-to-end serving comparisons.[^beck-etal-2024]

The reported implementation limits materially qualify deployment: sLSTM mixing is sequential; mLSTM CUDA kernels were stated to be about four times slower than FlashAttention or Mamba’s scan; matrix state is computationally expensive; and forget-gate initialization requires care. Fixed mLSTM state bounds sequence-length memory but may overload with longer contexts, although the reported tests reached 16K.[^beck-etal-2024]

## Relationships

- **Evaluates:** [xLSTM extended LSTM architecture](xlstm-extended-lstm-architecture.md).
- **Contrasts with:** [Mamba evaluation and implementation trade-offs](mamba-evaluation-and-implementation-trade-offs.md). The xLSTM paper includes one Mamba implementation in its comparisons, but neither source alone provides a universal architecture ranking.
- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md). Fixed recurrent state changes cache growth, but does not by itself establish lower production latency or better retrieval quality.

## Evidence limits

The primary source supplies experimental setup and results but no independent replications. “Best” is only within the named baselines, sizes, selected xLSTM mixtures, data, training duration, and evaluation harness. Benchmark and throughput claims should not be transferred to newer implementations or workloads without matched measurement; the paper itself notes unoptimized kernels and hyperparameters. The bundled PDFs were not visually rendered; plot-only values are therefore not independently transcribed here.[^beck-etal-2024]

[^beck-etal-2024]: Maximilian Beck et al., “xLSTM: Extended Long Short-Term Memory,” arXiv:2405.04517, bundled [LaTex source](../raw/2405.04517_xLSTM/xlstm.tex), Sections 3–6 and Appendix C–E; reported numerical values are in the included [model-comparison table](../raw/2405.04517_xLSTM/tables/comp_spaj15b_model_benchmark_val.tex), [downstream table](../raw/2405.04517_xLSTM/tables/lm_eval_mambatasks.tex), [LRA table](../raw/2405.04517_xLSTM/tables/lra_test_accuracy.tex), and [ablation tables](../raw/2405.04517_xLSTM/tables/abl_spaj15b_lstm_to_xlstm.tex).
