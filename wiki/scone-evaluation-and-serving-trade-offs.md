---
type: Concept
title: SCONE evaluation and serving trade-offs
description: Author-run SCONE experiments report that frequent n-gram-table size and f-gram-model size improve selected language-model and post-training results while moving inference capacity cost to host memory or NVMe and increasing training compute.
tags: [evaluation, embeddings, n-grams, inference, offloading, systems]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T15:29:19Z }
sources:
  - id: scone-2025
    resource: ../raw/2502.01637_ScalingEmbeddingLayersinLanguageModels/main.tex
    title: "Scaling Embedding Layers in Language Models"
---

# SCONE evaluation and serving trade-offs

Author-run experiments report that scaling either the number of cached frequent n-grams or the training-only f-gram Transformer improves SCONE’s held-out perplexity and selected downstream/post-training results. The reported inference advantage is lower accelerator footprint relative to selected larger dense baselines, paid for by added training FLOPs and substantial host-memory or NVMe storage—not a general proof of lower end-to-end serving cost.[^scone-2025]

## Reported scaling behavior

In GPT-2-size WebText experiments (9B-token corpus; 80B-token training), held-out perplexity generally declined as the retained f-gram count grew from 512K to 100M. With 100M f-grams, the 419M- and 589M-parameter SCONE main models matched or surpassed selected 759M- and 1,099M-parameter enlarged-main-model baselines, respectively; these comparisons equalize the authors’ stated training-time parameter accounting rather than inference storage.[^scone-2025]

For a fixed 100M table, increasing $\mathcal A_f$ from 0.5× to 3× the main model’s non-embedding parameters generally lowered perplexity, with diminishing gains. For example, the reported 419M main model moved from WikiText-103 perplexity 26.1 to 23.4 with a 170M f-gram model, compared with 24.7 for the 589M baseline. At 1,020M f-gram-model size, it reached 22.1, slightly above the 1,099M baseline’s 21.9; more training-only f-gram capacity was therefore not uniformly a better quality scaling route than enlarging the main model.[^scone-2025]

With a 20M table, raising maximum n-gram length from 2 to about 4 improved reported WikiText-103 perplexity and average matched length, after which both mostly plateaued or fluctuated. The paper uses $K=5$ for subsequent experiments. This is a result for its frequency ranking, tokenizer, corpus, and short n-gram range—not evidence that length 4 or 5 is universally optimal.[^scone-2025]

## Matched large-scale comparisons

On the OLMo/Dolma setting, dense OLMo-1B and OLMo-1.9B baselines train for 1T tokens, while SCONE variants use 500B tokens with a 1.8B f-gram model so the authors can approximately match total training FLOPs. Their six-task zero-shot average is 53.7 for OLMo-1B, 56.8 for OLMo-1.9B, 56.8 for OLMo-1.3B plus 10M f-grams, and 57.0 for OLMo-1B plus 1B f-grams. The last comparison is reported as about 48% lower inference FLOPs and accelerator memory than the 1.9B baseline; the 1.3B/10M comparison is reported as about 32% lower.[^scone-2025]

The 200B-token supplementary runs report the same directional pattern over an 11-corpus OLMo evaluation mixture. For example, the 1B baseline’s reported average perplexity is 16.082, compared with 14.581 for 1B plus 1B f-grams and a 1.8B f-gram model; the 1.9B baseline is 14.598. These are author-run curves and tables, not independent evidence that a smaller accelerator-resident model will dominate at other scales, data mixtures, or training allocations.[^scone-2025]

The paper also reports Qwen3-4B supervised fine-tuning with 10M f-grams: the listed AIME 2024/LiveCodeBench pass@1 scores change from 45.3/30.8 for the baseline to 48.3/34.5 with an 8B f-gram model and 51.6/36.3 with a 14B one. Reported decoding latency is 10.05 ms/token for baseline and 10.13 for both SCONE variants in that setup.[^scone-2025]

## Storage, lookup, and latency measurements

For 2,048-dimensional FP16 f-gram vectors, the reported 10M table occupies 41.4 GB in system memory or 77.3 GB on SSD; 100M takes 413.6 GB in memory or 766.8 GB on SSD; a 1B table is reported not to fit the 512-GB host-memory workstation and uses 7,665.4 GB on SSD. Capacity grows roughly linearly with table rows, so the method trades accelerator constraints for a nontrivial host-storage planning problem.[^scone-2025]

On the authors’ 64-core/512-GB workstation, a batch-1 NVMe lookup is reported at 1.1 ms for 10M f-grams and 2.3 ms for 1B; at batch size 16, the plotted 1B NVMe value is 0.5 ms amortized per token. The plotted 100M in-memory value at batch 16 is 0.017 ms. These measurements include retrieval through vector readiness on GPU, but hardware, database/cache state, batch shape, retrieval policy, and serving integration limit their transferability.[^scone-2025]

A separate A100-80GB, context-2,048, batch-4 table lists 8.38 GB peak GPU memory, 6.45 ms decode latency, and $2.73\times10^{13}$ training FLOPs/sequence for the 1.9B baseline. The 1.3B/10M SCONE case lists 5.60 GB, 4.83 ms, 41.76 GB CPU overhead, and $4.94\times10^{13}$ FLOPs; the 1B/1B case lists 4.45 GB, 4.90 ms, 7.67 TB disk, and $5.57\times10^{13}$ FLOPs. This supports the resource relocation claim under that configuration, not a workload-independent latency or cost conclusion.[^scone-2025]

## Evidence limits

- Results are author-run; large-scale pretraining lacked formal statistical-significance testing according to the paper’s checklist, and the bundle does not include released training code.
- The largest evaluated training-time model is at most 3B parameters; performance at larger scales, other languages, tokenization-free models, and longer/semantic keys is untested.
- SCONE only caches frequent short token n-grams. Sparse or semantically similar but surface-different contexts can miss the table; the authors identify longer-query key design as future work.
- Reported matching of training FLOPs does not equalize data exposure, parameter placement, storage cost, host/accelerator transfer, or production concurrency.

## Relationships

- **Evaluates:** [SCONE scalable contextualized offloaded n-gram embeddings](scone-scalable-contextualized-offloaded-n-gram-embeddings.md).
- **Compares with:** [Over-tokenized Transformer evaluation and systems trade-offs](over-tokenized-transformer-evaluation-and-systems-trade-offs.md); both report local n-gram input capacity, but their parameterization and training/storage layouts differ.
- **Contrasts with:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md); each separates total capacity from per-token dense FLOPs, but SCONE’s inference capacity is lookup storage rather than resident routed experts.
- **System context:** [LLM inference serving stack](llm-inference-serving-stack.md); host lookup, transfer, batching, and workload shape must be included in an end-to-end serving evaluation.

[^scone-2025]: Da Yu et al., “Scaling Embedding Layers in Language Models,” [LaTeX source](../raw/2502.01637_ScalingEmbeddingLayersinLanguageModels/main.tex), Sections 4–5 and Appendix “Additional Experiments,” “Apply SCONE in Post-training,” “Summary of Comparison on Computational Resources,” and “Limitations and Future Work”; bundled figures `olmo_headline.pdf`, `olmo_query_latency.pdf`, `olmo_all_loss_curves.pdf`, and `openwebtext_*.pdf` were rendered and reviewed.
