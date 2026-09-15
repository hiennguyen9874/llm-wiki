---
type: Concept
title: FlashAttention Original Paper Evaluation
description: Training speed, long-context quality, and kernel benchmark evidence from the NeurIPS 2022 FlashAttention paper up to 64K sequences.
tags: [attention, flashattention, benchmarks, training, long-context, lra]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T14:00:00Z }
sources:
  - id: fa-exp
    resource: ../raw/arXiv-2205.14135v2/src/experiments.tex
    title: FlashAttention Experiments
  - id: fa-supp
    resource: ../raw/arXiv-2205.14135v2/src/exp_supp.tex
    title: FlashAttention Full Experimental Results
  - id: fa-theory
    resource: ../raw/arXiv-2205.14135v2/src/theory.tex
    title: 'Analysis: IO Complexity of FlashAttention'
---

The NeurIPS 2022 FlashAttention paper reports end-to-end training speedups at unchanged model quality, quality gains from longer context, and attention-kernel runtime plus memory benchmarks to 64K sequences[^fa-exp].

## Faster training

- BERT-large on Wikipedia to 72.0% masked-LM accuracy on 8×A100-80GB (LAMB, FP16 Apex AMP O2, 10 runs): NVIDIA MLPerf 1.1 record 20.0±1.5 min vs FlashAttention 17.4±1.4 min, about 15% faster[^fa-exp].
- GPT-2 on OpenWebText on 8×A100-40GB (400K steps, same hyperparameters, PyTorch AMP): small — HuggingFace 9.5 days versus Megatron-LM 4.7 days versus FlashAttention 2.7 days at equal 18.2 perplexity; medium — HuggingFace 21.0 days versus Megatron-LM 11.5 days versus FlashAttention 6.9 days at 14.2–14.3 perplexity[^fa-exp].
- Validation perplexity curves overlap the HuggingFace baseline, supporting exactness and numerical stability rather than a changed model definition[^fa-supp].
- Long-Range Arena (1K–4K, geometric-mean speedup): Transformer 59.3 average vs FlashAttention 59.8 at 2.4× vs block-sparse FlashAttention 59.6 at 2.8×; tested approximate baselines score 54.9–59.6 at 1.3–2.5×[^fa-exp].

## Longer context, higher quality

- GPT-2 small with 4× context is still faster than the 1K Megatron baseline while gaining 0.7 perplexity: Megatron 1K 18.2 in 4.7 days vs FlashAttention 1K 18.2 in 2.7 days, 2K 17.6 in 3.0 days, 4K 17.5 in 3.6 days[^fa-exp].
- Long-document classification with RoBERTa plus repeated positional embeddings: MIMIC-III rises from 52.8 micro-F1 at 512 to 57.1 at 16K (+4.3); ECtHR rises from 72.2 at 512 to 80.7 at 8K (+8.5, 79.2 at 16K)[^fa-supp].
- Path-X at 16K (128×128 pixels fed pixel-by-pixel): FlashAttention reaches 61.4 accuracy after Path-64 pretraining plus spatial interpolation of positional embeddings and extended fine-tuning, the first reported better-than-chance Transformer result; all tested prior Transformer variants fail or run out of memory[^fa-exp].
- Path-256 at 64K: block-sparse FlashAttention reaches 63.1 accuracy, the first reported better-than-chance sequence-model result[^fa-exp].

## Attention kernel benchmarks

Setup for the main sweep is one 40GB A100, 8 heads of dim 64, batch 16, FP16, dropout 0.1 plus random padding mask; runtime is forward plus backward averaged over 100 calls[^fa-supp].

- FlashAttention is up to about 3× faster than the PyTorch exact baseline over common lengths up to 2K and scales to 64K[^fa-exp].
- Memory grows linearly with sequence length; FlashAttention is up to about 20× more memory-efficient than exact baselines and more efficient than tested approximate baselines; except Linformer, all other baselines run out of memory before 64K[^fa-exp].
- Approximate-method runtimes cross over FlashAttention between about 512 and 1024 tokens; block-sparse FlashAttention stays faster than all tested exact, sparse, and approximate implementations across lengths[^fa-exp].
- IO determinant micros (GPT-2 medium, seq 1024, head dim 64, 16 heads, batch 64, A100): standard 66.6 GFLOPs, 40.3 GB HBM traffic, 41.7 ms vs FlashAttention 75.2 GFLOPs, 4.4 GB HBM traffic, 7.3 ms — more FLOPs but far less HBM traffic and much faster runtime[^fa-theory].

## Against Apex fused attention

Apex FMHA was the fastest short-sequence baseline known at project start but targets at most 512 tokens, head dim 64, and A100 only, and it stores the attention matrix for backward so it offers little memory saving[^fa-supp].

FlashAttention builds from FMHA code plus tiling and recomputation to reach 64K, head dims 16/32/64/128, and Turing plus Ampere GPUs[^fa-supp].

Short-sequence comparison (batch 64, 16 heads, dim 64, A100, with masking and dropout): FlashAttention forward is faster at 128/256/512 (0.08 vs 0.10, 0.22 vs 0.29, 0.81 vs 1.14 ms), backward is slightly slower (0.20 vs 0.17, 0.53 vs 0.52, 2.00 vs 1.81 ms), combined is about 4% slower at 128 and 8% and 5% faster at 256 and 512[^fa-supp].

## Hardware dependence

Speedup over standard PyTorch attention varies with HBM bandwidth and SRAM size[^fa-supp].

Reported shapes are A100 2–4× (more with dropout and masking from fusion), A100 dim-128 smaller gains except up to 3× with causal masking from skipped blocks, RTX 3090 2.5–4.5× on lower bandwidth, and T4 smaller gains from smaller SRAM-dictated blocks with forward-only numbers also reported for inference[^fa-supp].

## Relationships

- Evaluates [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: this page holds the paper's numbers; the main concept holds the reusable mechanism.
- Uses [Block-Sparse FlashAttention](flashattention-block-sparse.md) — synthesis: sparse-variant LRA, Path-256, and kernel-crossover claims belong to the sparse extension.
- Contrasts with [FlashAttention-2 Exact Attention Kernel](flashattention-2.md) — synthesis: FA2 numbers are separate throughput follow-up evidence, not repeated here.

## Coverage limits

- Compiled from `src/experiments.tex`, `src/exp_supp.tex`, `src/theory.tex`, and `tables/long_documents.tex` plus `tables/pathx.tex` captions; JPG/PDF speedup and training-curve figures were not visually inspected.
- Full per-configuration timing and memory tables under `tables/` were treated as non-durable raw evidence; only the summary speedups, perplexities, F1 scores, accuracies, and FMHA deltas above are canonical.
- No secrets, credentials, or PII were found in the compiled tex sources.

[^fa-exp]: FlashAttention Experiments — `../raw/arXiv-2205.14135v2/src/experiments.tex`.
[^fa-supp]: FlashAttention Full Experimental Results — `../raw/arXiv-2205.14135v2/src/exp_supp.tex`.
[^fa-theory]: Analysis: IO Complexity of FlashAttention — `../raw/arXiv-2205.14135v2/src/theory.tex`.
