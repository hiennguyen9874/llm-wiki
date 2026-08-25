---
type: Concept
title: DeepSeek Sparse Attention
description: DeepSeek Sparse Attention uses a lightweight indexer to select token-level MLA entries before MQA attention, reducing the main attention computation from quadratic to top-k-scaled while retaining an indexer pass.
tags: [attention, sparse-attention, deepseek, multi-head-latent-attention, long-context, inference]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:13:08Z }
sources:
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
  - id: glm5-code-2026
    resource: ../raw/glm-moe/modular_glm_moe_dsa.py
    title: Hugging Face GLM-MoE-DSA modular implementation
  - id: longcat-lsa-2026
    resource: ../raw/2608.01662_LongCatSparseAttention/longcat.tex
    title: "LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing"
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

## LongCat profile of the residual bottlenecks

A later LongCat report profiles DSA's token-level selections as memory-inefficient: its selected MLA vectors are scattered rather than coalesced, and its stated accelerator measurement reached about 4.5% of peak HBM bandwidth. The report also measures the indexer as 90% of per-layer decode latency at 1,024K context in its BF16, batch-4, $K=2048$ setup. These are useful motivation for LSA, but they are hardware-, kernel-, and configuration-specific measurements rather than properties established for every DSA implementation.[^longcat-lsa-2026]

## Continued-training recipe

The authors initialize DSA from a 128K-context DeepSeek-V3.1-Terminus checkpoint. A dense warm-up freezes the base model, aligns the indexer’s softmax scores to the head-summed main-attention distribution with KL loss, and trains only the indexer for 1,000 steps (2.1B tokens). Sparse training then enables top-$k$ selection, optimizes the main model only with language-model loss and the detached-input indexer only with its alignment loss, and uses $k=2{,}048$ for 15,000 steps (943.7B tokens).[^deepseek-v3-2-2025]

## Reported efficiency and parity boundary

The source reports no substantial short- or long-context benchmark degradation against V3.1-Terminus in its September 2025 suite, closely matched ChatbotArena Elo values from November 2025, and stronger results in two named external long-context evaluations. Its H800 service-cost plots show a much flatter DSA cost curve than V3.1-Terminus through 128K tokens for both prefill and decode; short prefill uses a separate masked-MHA simulation. These are author-selected comparisons and cost estimates at an assumed USD 2 per H800 GPU-hour, not a general serving-cost guarantee.[^deepseek-v3-2-2025]

## GLM-5 adaptation and implementation

GLM-5 reports adapting DSA from its mid-training MLA checkpoint with a 1,000-step indexer warm-up and only 20B sparse-training tokens. Its listed 128K evaluations are mixed rather than uniformly equal—DSA improves MV-NIAH and SQuAD but trails MLA on HotpotQA—and a GLM-4.7-Flash control closes most of its 128K warm-up deficit after 150B joint-training tokens. These results support model-specific recoverability, not the report’s broader claim that DSA is “lossless by construction.”[^glm5-report-2026]

The released implementation scores tokens with weighted ReLU indexer heads and selects up to 2,048 causal positions, consistent with the core DSA mechanism. GLM differs by applying interleaved RoPE in the indexer and exposing per-layer `full` versus `shared` modes: shared layers reuse the preceding full layer’s top-k positions. Eager/SDPA materializes a sparse additive mask, while another backend may consume indices directly. Cross-layer sharing is code evidence not documented in the GLM-5 report, and the generated module marks Flash-MLA support as incomplete.[^glm5-code-2026]

## Relationships

- **Specializes:** [Multi-head Latent Attention](multi-head-latent-attention.md) by selecting a sparse token subset before MQA over MLA entries.[^deepseek-v3-2-2025]
- **Used by:** [DeepSeek-V3.2 post-training, agentic synthesis, and evaluation limits](deepseek-v3-2-post-training-agentic-evaluation.md) during sparse continued pre-training and post-training.[^deepseek-v3-2-2025]
- **Addresses:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) at attention-read computation; DSA does not by itself make token cache state fixed-size.[^deepseek-v3-2-2025]
- **Extended by:** [LongCat Sparse Attention](longcat-sparse-attention.md), which targets reported selected-KV locality and repeated-indexing costs.[^longcat-lsa-2026]

## Evidence limits

The original mechanism, training counts, parity findings, and cost curves are from DeepSeek-AI’s report. It does not supply controlled ablations isolating the indexer, MQA instantiation, selected-token count, kernels, or continued-training data. GLM-5 adds a second architecture and a released model implementation, but its quality and efficiency evidence remains author-run and does not isolate DSA from data, model, or systems changes.[^deepseek-v3-2-2025][^glm5-report-2026][^glm5-code-2026]

[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” arXiv:2512.02556v1, [source](../raw/arXiv-2512.02556v1/main.tex), Sections 2.1–2.3; included [architecture figure](../raw/arXiv-2512.02556v1/figures/v32_arch.pdf) and [cost figures](../raw/arXiv-2512.02556v1/figures/cost_prefilling.pdf) and [decode cost figure](../raw/arXiv-2512.02556v1/figures/cost_decoding.pdf).

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [pre-training section](../raw/arXiv-2602.15763v2/2_pretrain.tex), Continued Pre-Training with DSA and efficient-attention ablations.

[^glm5-code-2026]: Hugging Face, “GLM-MoE-DSA modular implementation,” [source](../raw/glm-moe/modular_glm_moe_dsa.py), indexer, attention, and model classes; cross-checked against the generated [modeling module](../raw/glm-moe/modeling_glm_moe_dsa.py).

[^longcat-lsa-2026]: Wen Zan et al., “LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing,” 2026, [source](../raw/2608.01662_LongCatSparseAttention/longcat.tex), Sections 2–4.
