---
type: Concept
title: DeepSeek Sparse Attention
description: DeepSeek Sparse Attention uses a lightweight indexer to select token-level MLA entries before MQA attention, reducing the main attention computation from quadratic to top-k-scaled while retaining an indexer pass.
tags: [attention, sparse-attention, deepseek, multi-head-latent-attention, long-context, inference]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T16:27:51Z }
sources:
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
---

# DeepSeek Sparse Attention

DeepSeek Sparse Attention (DSA) first scores prior tokens with a lightweight learned indexer, selects the highest-scoring token-level MLA entries, then performs core Multi-Query Attention (MQA) only over that selected set. In DeepSeek-V3.2, the authors report reducing the main attention computation from $O(L^2)$ to $O(Lk)$ for sequence length $L$ and selected-token count $k$; the indexer remains quadratic, so this is a lower-cost sparse-attention design rather than elimination of all quadratic work.[^deepseek-v3-2-2025]

## Index then select

For query-token representation $h_t$ and prior-token representation $h_s$, the lightning indexer produces a score by summing weighted ReLU dot products across a small number of indexer heads:

$$
I_{t,s}=\sum_{j=1}^{H^I} w^I_{t,j}\operatorname{ReLU}(q^I_{t,j}\cdot k^I_s).
$$

The selected set is the top-$k$ prior entries by $I_{t,s}$. Core attention then attends from the query to only their MLA key-value entries. The report attributes the indexer’s lower cost to few heads and an FP8 implementation, but does not provide an independent latency decomposition.[^deepseek-v3-2-2025]

DSA is instantiated in MLA’s MQA mode: one latent key-value entry is shared across the query heads of a token. The source states that this sharing is required for kernel efficiency. Thus DSA retains MLA’s compressed, token-addressable entries but limits which prior entries each query reads.[^deepseek-v3-2-2025]

## Continued-training recipe

The authors initialize DSA from a 128K-context DeepSeek-V3.1-Terminus checkpoint. A dense warm-up freezes the base model, aligns the indexer’s softmax scores to the head-summed main-attention distribution with KL loss, and trains only the indexer for 1,000 steps (2.1B tokens). Sparse training then enables top-$k$ selection, optimizes the main model only with language-model loss and the detached-input indexer only with its alignment loss, and uses $k=2{,}048$ for 15,000 steps (943.7B tokens).[^deepseek-v3-2-2025]

## Reported efficiency and parity boundary

The source reports no substantial short- or long-context benchmark degradation against V3.1-Terminus in its September 2025 suite, closely matched ChatbotArena Elo values from November 2025, and stronger results in two named external long-context evaluations. Its H800 service-cost plots show a much flatter DSA cost curve than V3.1-Terminus through 128K tokens for both prefill and decode; short prefill uses a separate masked-MHA simulation. These are author-selected comparisons and cost estimates at an assumed USD 2 per H800 GPU-hour, not a general serving-cost guarantee.[^deepseek-v3-2-2025]

## Relationships

- **Specializes:** [Multi-head Latent Attention](multi-head-latent-attention.md) by selecting a sparse token subset before MQA over MLA entries.[^deepseek-v3-2-2025]
- **Used by:** [DeepSeek-V3.2 post-training, agentic synthesis, and evaluation limits](deepseek-v3-2-post-training-agentic-evaluation.md) during sparse continued pre-training and post-training.[^deepseek-v3-2-2025]
- **Addresses:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) at attention-read computation; DSA does not by itself make token cache state fixed-size.[^deepseek-v3-2-2025]

## Evidence limits

The mechanism, training counts, parity findings, and cost curves are all from DeepSeek-AI’s report. It does not supply controlled ablations isolating the indexer, MQA instantiation, selected-token count, kernels, or continued-training data, and the paper does not establish generalization to other architectures or workloads.[^deepseek-v3-2-2025]

[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” arXiv:2512.02556v1, [source](../raw/arXiv-2512.02556v1/main.tex), Sections 2.1–2.3; included [architecture figure](../raw/arXiv-2512.02556v1/figures/v32_arch.pdf) and [cost figures](../raw/arXiv-2512.02556v1/figures/cost_prefilling.pdf) and [decode cost figure](../raw/arXiv-2512.02556v1/figures/cost_decoding.pdf).
