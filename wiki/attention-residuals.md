---
type: Concept
title: Attention Residuals
description: Attention Residuals replace uniform residual accumulation with learned softmax retrieval over earlier depth-wise representations, with a block form that bounds cache and communication overhead.
tags: [attention-residuals, residual-stream, depth, retrieval]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:43:29Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: "Attention Residuals"
---

# Attention Residuals

Attention Residuals (AttnRes) make representations selectively addressable across model depth. Instead of passing only the uniform additive accumulation of prior layer outputs, each layer uses a learned pseudo-query and softmax weights to mix the embedding and preceding representations.[^attnres-2026][^kimi-k3-2026]

## Full form

For layer $l$, a learned query $w_l$ scores RMS-normalized earlier layer outputs. Softmax-normalized scores $\alpha_{i\to l}$ produce

$$
h_l=\sum_{i=0}^{l-1}\alpha_{i\to l}v_i.
$$

RMS normalization prevents output magnitude alone from dominating depth attention. The report initializes every pseudo-query to zero, making the initial depth weights uniform and thereby avoiding early training volatility. Token attention and depth attention then have distinct jobs: one retrieves sequence positions, while AttnRes retrieves intermediate transformations.[^attnres-2026][^kimi-k3-2026]

Full AttnRes costs $O(L^2d)$ arithmetic and retains $O(Ld)$ layer outputs. Those outputs already overlap with saved activations in ordinary backpropagation, but activation recomputation and pipeline parallelism make their retention and cross-stage transfer material overheads.[^attnres-2026]

## Block form

Block AttnRes sums outputs within each block and applies depth attention only over the embedding, completed block representations, and—inside the current block—its partial sum. It reduces persistent representations and pipeline communication from $O(Ld)$ to $O(Nd)$ for $N$ blocks. $N=L$ recovers Full AttnRes, while $N=1$ reduces to standard residual accumulation with a separate embedding source.[^attnres-2026][^kimi-k3-2026]

Kimi K3 uses eight 12-layer blocks plus a partial final block; counting the embedding source yields nine retrievable block representations. This corrects the earlier secondary summary’s ambiguous statement that the model had only eight total block sources.[^gpt2-kimi3-2026][^kimi-k3-2026]

## Systems implications

For pipeline-parallel training, the report caches received block summaries across virtual stages so only incremental summaries are transferred; it reports under 4% end-to-end training overhead under pipeline parallelism. For inference, learned queries can be batched per block against prior block summaries, then merged with sequential intra-block attention by online softmax. The reported implementation gives Block AttnRes an amortized residual-mechanism I/O of $5.5d$ per layer under its typical setting, versus $3d$ for standard residuals.[^attnres-2026]

Long-context prefill still stores block representations per token. The report's 128K-token, eight-block example requires 15 GB before sequence sharding; tensor-parallel sequence sharding reduces this to about 1.9 GB per device, and 16K chunked prefill to under 0.3 GB. These are configuration-specific design and measurement claims, not architecture-independent guarantees.[^attnres-2026]

## Relationships

- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Operationalized by:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md).
- **Evaluated by:** [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md).

## Evidence limits

The primary AttnRes report provides mechanism, systems, and author-run experiments; the Kimi K3 report documents a later deployment. Neither has been independently replicated here. Reported quality, cost, and the finding that roughly eight blocks recover most benefits remain architecture-, training-recipe-, hardware-, and workload-dependent.[^attnres-2026][^kimi-k3-2026]

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.2 and 5.

[^attnres-2026]: Kimi Team, “Attention Residuals,” arXiv:2603.15031v1, [source](../raw/arXiv-2603.15031v1/main.tex), including referenced sections, tables, and appendices in the source directory.
