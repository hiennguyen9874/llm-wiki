---
type: Concept
title: Attention Residuals evaluation and systems trade-offs
description: Attention Residuals lower reported validation loss across five MoE scaling sizes and improve a matched 48B Kimi Linear model’s evaluated benchmarks, subject to blocking, systems, and author-run-evaluation limits.
tags: [attention-residuals, evaluation, residual-stream, systems, mixture-of-experts]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:45:17Z }
sources:
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: "Attention Residuals"
---

# Attention Residuals evaluation and systems trade-offs

In the authors’ matched experiments, Full and Block Attention Residuals (AttnRes) lower validation loss versus a PreNorm baseline across five MoE sizes, while the block variant trades some granularity for bounded cross-stage state. A 48B-total/3B-active Kimi Linear comparison reports improvements or ties on all 15 listed benchmarks, but these results are author-run and specific to the model, recipe, and evaluation setup.[^attnres-2026]

## Scaling and ablations

The scaling study trains 194M–528M activated-parameter MoE models at 8,192-token context, holding each size group’s baseline-selected hyperparameters fixed across the baseline, Full AttnRes, and Block AttnRes variants. The fitted loss laws are $1.891C^{-0.057}$ for the baseline, $1.870C^{-0.058}$ for Block AttnRes, and $1.865C^{-0.057}$ for Full AttnRes. At 5.6 PFLOP/s-days, the fitted Block result is 1.692 versus 1.714 for baseline, which the report characterizes as a 1.25× compute advantage.[^attnres-2026]

At the 436M model, validation loss is 1.766 for baseline, 1.737 for Full AttnRes, and 1.746 for Block AttnRes; mHC-lite is 1.747. Full attention is best in that ablation, while blocks of size 2, 4, or 8 are reported near 1.746, and larger blocks move toward baseline. An eight-block setting is therefore a reported quality–systems compromise, not a general optimum.[^attnres-2026]

The report attributes the advantage to content-dependent competitive selection: fixed scalar mixing scores 1.749, sigmoid gating 1.741, and full softmax AttnRes 1.737 in its 16-head experiment. Input-dependent queries score 1.731 but require a $d\times d$ projection per layer and sequential decode access; the deployed default uses learned, input-independent pseudo-queries instead. These component comparisons isolate the paper’s configurations, not all possible residual mechanisms.[^attnres-2026]

## Matched 48B result

The main comparison adds nine-block AttnRes to a 27-Transformer-block Kimi Linear MoE model (48B total and 3B activated parameters), keeping the stated architecture otherwise unchanged. Both variants use Muon, a WSD schedule, 1T-token pre-training plus about 400B high-quality mid-training tokens, and then context extension. AttnRes has higher scores on 14 of 15 listed benchmarks and ties MMLU-Pro: GPQA-Diamond is 44.4 versus 36.9, HumanEval 62.2 versus 59.1, MMLU 74.6 versus 73.5, and C-Eval 82.5 versus 79.6.[^attnres-2026]

The authors also report lower validation loss throughout the 1T-token comparison, bounded periodic residual-output magnitude rather than monotonic depth growth, and more uniform layer gradient magnitudes. These training-dynamics observations support the proposed explanation but do not independently establish its causal mechanism.[^attnres-2026]

## Architecture-allocation evidence

In a 25-configuration sweep fixed at about $6.5\times10^{19}$ FLOPs and $2.3\times10^8$ active parameters, AttnRes has lower loss than the baseline in every reported cell (by 0.019–0.063). The baseline optimum is 1.847 at $d_{\mathrm{model}}/L_b\approx60$ and $H/L_b\approx0.3$; AttnRes’s is 1.802 at $d_{\mathrm{model}}/L_b\approx45$ and the same head ratio. Under this fixed budget, the lower width-to-depth ratio means a deeper, narrower model, suggesting AttnRes benefits more from depth in this sweep. It is not a deployment prescription because increased depth also raises sequential inference latency.[^attnres-2026]

## Operational trade-offs

Full AttnRes must preserve and, in pipeline parallelism, transfer $L$ representations. Block AttnRes transfers $N$ summaries, and cross-stage caching reduces redundant transfers across virtual pipeline stages. The report measures less than 4% end-to-end training overhead under pipeline parallelism and less than 2% inference-latency overhead on its typical workloads.[^attnres-2026]

Blockwise inference batches each block’s learned queries against preceding summaries, then sequentially incorporates the current partial sum using online-softmax statistics. This amortizes inter-block reads, but does not eliminate long-context prefill storage or the sequential depth dependency. The paper’s I/O accounting excludes the internal I/O of the layer function and therefore should not be read as end-to-end serving cost.[^attnres-2026]

## Relationships

- **Evaluates:** [Attention Residuals](attention-residuals.md), including Full and Block forms.
- **Uses:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) as the main model baseline.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) only in the report’s depth-mixing discussion; AttnRes changes residual aggregation, not Kimi Linear’s token-attention mechanism.

## Evidence limits

The source is a Kimi Team technical report. Its benchmark, scaling-law, overhead, and training-dynamics results have not been independently replicated here; source text does not provide uncertainty estimates for the reported benchmark differences. Blocking, pipeline schedule, hardware, kernels, context lengths, data recipe, and the Kimi Linear base architecture can all affect practical quality and cost. The PDF-equivalent TeX source, included tables, and appendices were inspected; decorative assets, bibliography data, and minted build-cache artifacts were not used for claim extraction.

[^attnres-2026]: Kimi Team, “Attention Residuals,” arXiv:2603.15031v1, [source](../raw/arXiv-2603.15031v1/main.tex), including referenced sections, tables, and appendices in the source directory.
