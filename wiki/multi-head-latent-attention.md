---
type: Concept
title: Multi-head Latent Attention
description: Multi-head Latent Attention caches a low-dimensional joint KV latent plus a decoupled rotary key, preserving token-addressable attention while greatly reducing per-token decode state.
tags: [attention, multi-head-latent-attention, mla, kv-cache, inference, rope]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-14T06:56:09Z }
sources:
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
---

# Multi-head Latent Attention

Multi-head Latent Attention (MLA) replaces per-head key/value cache entries with a joint low-rank KV latent, while a small decoupled key carries rotary position information. It retains token-addressable softmax attention but reduces the representation cached for each token; the model-specific cache is still linear in context length.[^deepseek-v2-2024]

## Joint low-rank KV state

For input $h_t$, MLA down-projects to a compressed latent $c_t^{KV}=W^{DKV}h_t$ and obtains conventional content keys and values from separate up-projections. At decode time, the cache retains $c_t^{KV}$ rather than materialized per-head content K/V. Associativity permits the key up-projection to be absorbed into the query path and the value up-projection into the output path, so those materialized tensors need not be reconstructed for every query.[^deepseek-v2-2024]

MLA also down- and up-projects queries. Query compression reduces training activation memory but does not itself reduce the cached decode state.[^deepseek-v2-2024]

## Decoupled position path

Applying RoPE to a low-rank content key would make its up-projection position-dependent and prevent its absorption into the query projection. MLA instead forms per-head rotary queries and a shared rotary key, concatenating each with its content counterpart before the attention score. The cache therefore stores the KV latent and the shared rotary key. This preserves the projection optimization while retaining positional information.[^deepseek-v2-2024]

For a layer with content-latent width $d_c$ and rotary-key width $d_h^R$, MLA caches $(d_c+d_h^R)$ elements per token, rather than MHA’s $2n_hd_h$. In DeepSeek-V2, $d_c=4d_h$ and $d_h^R=d_h/2$, yielding about $4.5d_h$ elements per layer—presented as comparable to 2.25-group GQA. This is an architecture-specific dimensional comparison, not a universal MLA compression ratio.[^deepseek-v2-2024]

## Reported evidence and limits

In controlled small and large MoE comparisons, the authors report MLA cache sizes of 15.6K versus 110.6K elements per token (small) and 34.6K versus 860.2K (large) relative to MHA, with higher scores on three of four listed hard benchmarks at each scale. Their MHA, GQA, and MQA ablation also reports MHA ahead on its four tested 7B benchmarks; these author-run results motivate MLA but do not establish superiority across architectures, data, or tasks.[^deepseek-v2-2024]

MLA compresses token state; it does not make exact global attention fixed-state. Cache bytes, cache reads, and attention work still grow with context length, while actual serving also depends on precision, kernels, batching, and allocation policy.[^deepseek-v2-2024]

DeepSeek-V3.2 supplies a later sparse-use case: its DeepSeek Sparse Attention instantiates MLA in MQA mode, shares one latent KV entry across query heads, and selects only top-ranked prior entries before core attention. This reduces the main attention work but does not change MLA’s cache from context-linear to fixed-size; its lightning indexer also retains a lower-cost quadratic scoring pass.[^deepseek-v3-2-2025]

GLM-5 reports that ordinary Muon orthogonalization left its 576-dimensional MLA cache behind GQA-8 in a listed ablation. Splitting Q/K/V up-projection matrices by head before orthogonalization closes that measured gap, while increasing effective Q/K width from 192 to 256 and reducing head count by one third is intended to lower decode dot-product work without changing reported parameter or prefill compute. This is architecture-and-optimizer-specific evidence, not a general MLA requirement.[^glm5-report-2026]

## Relationships

- **Modifies:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) through a jointly compressed key/value representation.
- **Uses:** [Rotary position embedding (RoPE)](rotary-position-embedding.md) only in its decoupled position path.
- **Addresses:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) with an architectural reduction in the per-token representation.
- **Contrasts with:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which shares whole K/V heads rather than caching a joint latent.
- **Used by:** [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md), [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md), [DeepSeek Sparse Attention](deepseek-sparse-attention.md), and the global-attention layers in [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).[^deepseek-v3-2024][^deepseek-v3-2-2025][^kimi-linear-2025][^kimi-k3-2026]

## Evidence limits

This is primary evidence from the bundled DeepSeek-V2 technical report and its included formulas and ablation tables. The reported quality, cache, training-cost, and throughput figures are author-run and configuration-specific; later MLA variants may change the position treatment, gating, dimensions, or inference implementation.[^deepseek-v2-2024]

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.1, 3.1–3.2, and Appendix C–D.

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Sections 1–2 and 5.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 2–3.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2–3.

[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” arXiv:2512.02556v1, [source](../raw/arXiv-2512.02556v1/main.tex), Section 2.1.

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [pre-training section](../raw/arXiv-2602.15763v2/2_pretrain.tex), Multi-latent Attention; [appendix](../raw/arXiv-2602.15763v2/9_appendix.tex), architecture table.
