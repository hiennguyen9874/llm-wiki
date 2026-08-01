---
type: Synthesis
title: LLM architecture learning roadmap
description: A build-first learning sequence that progresses from dense causal Transformers to scaling, serving, MoE, and hybrid long-context architectures including Mamba/SSD and KDA/MLA.
tags:
  - learning-roadmap
  - llm-architecture
  - transformer
  - mixture-of-experts
  - long-context
status: stable
created: 2026-08-01
generated:
  by: llm-wiki-agent/1
  at: 2026-08-01T10:23:07+07:00
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: radford-generative-pre-training-2018
    resource: ../raw/gpt.pdf
    title: Improving Language Understanding by Generative Pre-Training
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# LLM architecture learning roadmap

This is a build-first study sequence: master a dense causal Transformer and its training/inference behavior before introducing sparsity or long-context hybrids. It treats Mamba/SSD and KDA as fixed-state sequence-mixing alternatives, and MLA as compressed token-addressable attention. It is editorial guidance synthesized from the linked concepts, rather than an experimentally validated curriculum.[^vaswani-transformer-2017][^radford-generative-pre-training-2018][^deepseek-v2-2024][^kimi-linear-2025][^dao-gu-2024][^kimi-k3-2026]

## Recommended order

| Stage                        | Learn                                                                                                             | Build or verify before continuing                                                                                        | Primary concepts                                                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Foundations               | Matrix multiplication, softmax, cross-entropy, backpropagation, AdamW, and subword tokenization                   | Train a character-level or BPE bigram language model                                                                     | [GPT generative pre-training](gpt-generative-pre-training-and-task-adaptation.md)                                                                                                             |
| 2. Causal language modeling  | Next-token likelihood, teacher forcing, causal masking, temperature/top-k/top-p sampling                          | Implement a small autoregressive training loop and generation sampler                                                    | [GPT generative pre-training](gpt-generative-pre-training-and-task-adaptation.md)                                                                                                             |
| 3. Attention                 | Q/K/V projections, scaled dot-product attention, multi-head composition, and causal masking                       | Implement one-head then multi-head causal attention; test that a future-token perturbation cannot change earlier outputs | [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md)                                                                                                 |
| 4. Decoder-only Transformer  | Token/position representations, normalization, FFN, residual paths, stacked decoder blocks, and output projection | Train a minimal GPT and debug shapes, masks, loss decrease, and generation                                               | [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT-2 architecture](gpt-2-webtext-pre-training-and-architecture.md)                     |
| 5. Scaling and inference     | Parameter/data/compute allocation; distinction between training, prefill, and decode; KV cache                    | Add KV caching and compare cached versus uncached output equivalence and latency                                         | [Chinchilla allocation](chinchilla-compute-optimal-training-allocation.md), [KV-cache trade-offs](kv-cache-compression-and-trade-offs.md)                                                     |
| 6. Efficient dense attention | RoPE or another position method; MQA/GQA; exact IO-aware attention kernels                                        | Add RoPE and GQA to the small model, then use a FlashAttention implementation without changing the attention semantics   | [RoPE](rotary-position-embedding.md), [MQA/GQA](multi-query-and-grouped-query-attention.md), [FlashAttention](flashattention-io-aware-exact-attention.md)                                     |
| 7. Sparse capacity           | MoE routing, top-k selection, shared experts, load balancing, expert parallelism                                  | Replace a toy FFN with a small MoE; plot expert load and diagnose routing collapse                                       | [Switch Transformer](switch-transformer-sparse-routing.md), [DeepSeekMoE](deepseekmoe-expert-specialization.md)                                                                               |
| 8. Fixed-state and long-context mixing | MLA KV compression; linear/recurrent memory; Mamba/SSD; delta-rule correction and its limits              | Compare a token-addressable cache with a fixed-state toy memory; explain the retrieval-versus-memory trade-off            | [MLA](multi-head-latent-attention.md), [Mamba-2](mamba-2-architecture-and-parallelism.md), [SSD](structured-state-space-duality.md), [KDA/delta memory](delta-rule-and-gated-associative-memory.md) |
| 9. Frontier-model reading    | Map every novelty to the dense baseline and identify its bottleneck, trade-off, and evidence                      | Annotate one technical report by component, rather than treating its headline metrics as component evidence              | [DeepSeek-V3](deepseek-v3-architecture-and-pretraining.md), [Kimi K3](kimi-k3-hybrid-retrieval-architecture.md)                                                                               |

## Learning principle

Do not begin by reproducing a frontier model. A learner who can implement and test causal masking, KV caching, and a small dense Transformer can then identify what a later mechanism replaces:

- [Mixture-of-Experts](mixture-of-experts-training-and-systems-trade-offs.md) replaces dense FFN computation with sparse conditional computation.
- [Multi-head Latent Attention](multi-head-latent-attention.md) reduces per-token KV state while retaining token-addressable attention.
- [Mamba-2](mamba-2-architecture-and-parallelism.md) replaces attention with a selective state-space recurrence; [SSD](structured-state-space-duality.md) makes its chunked training computation matrix-multiplication-friendly.
- [Kimi Delta Attention](delta-rule-and-gated-associative-memory.md) replaces sequence-growing token state with fixed-size recurrent associative memory, adding key-addressed correction and channel-wise retention control.
- [Kimi Linear](kimi-linear-hybrid-attention-architecture.md) and [Kimi K3](kimi-k3-hybrid-retrieval-architecture.md) combine KDA with periodic MLA because neither fixed-state memory nor global attention alone resolves every long-context constraint.

## Scope boundary

This roadmap focuses on model architecture and its immediate training/serving implications. Data curation, distributed systems, post-training alignment, evaluation, safety, and agent scaffolding should follow after the dense-model core is operationally understood.

## Relationships

- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md), [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md), [Multi-head Latent Attention](multi-head-latent-attention.md), and [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) as architectural milestones.
- **Synthesizes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), [Structured State Space Duality](structured-state-space-duality.md), and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) into a prerequisite order.

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex).
[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training,” [source](../raw/gpt.pdf).
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” [source](../raw/arXiv-2405.04434v5/main.tex).
[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” [source](../raw/arXiv-2510.26692v2/main.tex).
[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” [source](../raw/arXiv-2405.21060v1/structure.tex).
[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” [source](../raw/arXiv-2607.24653v1/main.tex).
