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
  at: 2026-11-16T00:00:00Z
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
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
---

# LLM architecture learning roadmap

This is a build-first study sequence: master a dense causal Transformer and its training/inference behavior before introducing sparsity or long-context hybrids. It treats Mamba/SSD and KDA as fixed-state sequence-mixing alternatives, and MLA as compressed token-addressable attention. It is editorial guidance synthesized from the linked concepts, rather than an experimentally validated curriculum.[^vaswani-transformer-2017][^radford-generative-pre-training-2018][^deepseek-v2-2024][^kimi-linear-2025][^dao-gu-2024][^kimi-k3-2026]

## Recommended order

| Stage                        | Learn                                                                                                             | Build or verify before continuing                                                                                        | Primary concepts                                                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Foundations               | Matrix multiplication, softmax, cross-entropy, backpropagation, AdamW, and subword tokenization                   | Train a character-level or BPE bigram language model                                                                     | [GPT generative pre-training](gpt-generative-pre-training-and-task-adaptation.md)                                                                                                             |
| 2. Causal language modeling  | Next-token likelihood, teacher forcing, causal masking, temperature/top-k/top-p sampling                          | Implement a small autoregressive training loop and generation sampler                                                    | [Causal LM training and sampling](causal-language-modeling-training-and-sampling.md), [GPT generative pre-training](gpt-generative-pre-training-and-task-adaptation.md)                       |
| 3. Attention                 | Q/K/V projections, scaled dot-product attention, multi-head composition, and causal masking                       | Implement one-head then multi-head causal attention; test that a future-token perturbation cannot change earlier outputs | [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md)                                                                                                 |
| 4. Decoder-only Transformer  | Token/position representations, normalization, FFN, residual paths, stacked decoder blocks, and output projection | Train a minimal GPT and debug shapes, masks, loss decrease, and generation                                               | [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT-2 architecture](gpt-2-webtext-pre-training-and-architecture.md) |
| 5. Scaling and inference     | Parameter/data/compute allocation; distinction between training, prefill, and decode; [KV caching](kv-caching.md)                    | Add KV caching and compare cached versus uncached output equivalence and latency                                         | [Pretraining scaling guide](pretraining-scaling-beginners-guide.md), [Chinchilla allocation](chinchilla-compute-optimal-training-allocation.md), [Inference lifecycle and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md), [KV-cache trade-offs](kv-cache-compression-and-trade-offs.md)                             |
| 6. Efficient dense attention | RoPE or another position method; MQA/GQA; exact IO-aware attention kernels                                        | Add RoPE and GQA to the small model, then use a FlashAttention implementation without changing the attention semantics   | [RoPE](rotary-position-embedding.md), [MQA/GQA course](mqa-gqa-kv-cache-decode-beginners-guide.md), [RoPE + GQA + FlashAttention integration lab](rope-gqa-flashattention-integration-beginners-guide.md), [MQA/GQA concept](multi-query-and-grouped-query-attention.md), [FlashAttention course](flashattention-tiled-attention-beginners-guide.md), [FlashAttention concept](flashattention-io-aware-exact-attention.md)                                     |
| 7. Sparse capacity           | MoE routing, top-k selection, shared experts, load balancing, expert parallelism, and serving trade-offs             | Replace a toy FFN with a small MoE; simulate bounded dispatch, then plot expert/rank load and diagnose routing collapse | [MoE và sparse routing course](mixture-of-experts-sparse-routing-beginners-guide.md), [MoE capacity & stability lab](moe-capacity-load-balancing-stability-lab.md), [Expert parallelism course](expert-parallelism-serving-trade-offs-beginners-guide.md), [Switch Transformer](switch-transformer-sparse-routing.md), [DeepSeekMoE](deepseekmoe-expert-specialization.md), [DeepSeekMoE expert-design course](deepseekmoe-expert-design-beginners-guide.md) |
| 8. Fixed-state and long-context mixing | MLA KV compression; linear/recurrent memory; Mamba/SSD; delta-rule correction and its limits              | Compare a token-addressable cache with a fixed-state toy memory; explain the retrieval-versus-memory trade-off            | [MLA và token-addressable memory course](mla-token-addressable-memory-beginners-guide.md), [Linear attention như fixed-state memory course](linear-attention-fixed-state-associative-memory-beginners-guide.md), [SSD → Mamba-2 course](ssd-mamba2-beginners-guide.md), [Delta memory, KDA, và hybrid KDA–MLA mini-project](delta-memory-kda-hybrid-architecture-beginners-project.md), [MLA](multi-head-latent-attention.md), [Mamba-2](mamba-2-architecture-and-parallelism.md), [SSD](structured-state-space-duality.md), [KDA/delta memory](delta-rule-and-gated-associative-memory.md) |
| 9. Frontier-model reading    | Read a frontier model as a composition of sequence mixing, sparse capacity, residual flow, training objectives, and systems choices | Produce a component map and evidence ledger; distinguish architectural mechanism, implementation optimization, and whole-model result | [DeepSeek-V2](deepseek-v2-architecture-training-and-efficiency.md), [DeepSeek-V3](deepseek-v3-architecture-and-pretraining.md), [Kimi Linear](kimi-linear-hybrid-attention-architecture.md), [Kimi K3](kimi-k3-hybrid-retrieval-architecture.md) |

## Stage 9 curriculum: Frontier-model reading

Stage 9 should be split into **five learning parts**. The first establishes a repeatable reading method; the next three trace two architectural lineages and then decompose Kimi K3; the last prevents architecture-level conclusions from being inferred directly from headline model results. This split is editorial synthesis from the DeepSeek and Kimi reports and the GPT-2-to-Kimi-K3 explainer, not an experimentally validated course sequence.[^deepseek-v2-2024][^deepseek-v3-2024][^kimi-linear-2025][^kimi-k3-2026][^gpt2-kimi3-2026]

| Part | Learn | Reading path | Deliverable before continuing |
|---|---|---|---|
| 9.1. Baseline-to-bottleneck reading | Start from GPT-2's decoder block and classify each novelty by the bottleneck it targets: KV state, attention cost, FFN compute, routing balance, residual dilution, or hardware utilization | [GPT-2 architecture](gpt-2-webtext-pre-training-and-architecture.md), [inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md), [KV caching](kv-caching.md) | Draw the dense baseline and create a four-column ledger: mechanism, replaced baseline, expected trade-off, evidence |
| 9.2. DeepSeek V2 → V3: efficient attention, sparse capacity, and co-design | Follow MLA and DeepSeekMoE from V2, then identify V3's auxiliary-loss-free balancing, multi-token prediction, FP8, and communication schedule; separate model architecture from training/serving systems | [DeepSeek-V2](deepseek-v2-architecture-training-and-efficiency.md), [DeepSeek-V3 architecture](deepseek-v3-architecture-and-pretraining.md), [routing balance](auxiliary-loss-free-moe-load-balancing.md), [multi-token prediction](sequential-multi-token-prediction.md), [V3 systems and FP8](deepseek-v3-training-systems-and-fp8.md) | Make a V2→V3 diff and label every item as architecture, objective, numerical format, distributed system, or serving policy |
| 9.3. GPT-2 → Kimi Linear: changing the memory model | Trace softmax attention and sequence-growing KV cache through linear attention, delta correction, scalar decay, channel-wise KDA, and periodic MLA; explain why fixed-state memory needs correction/forgetting and why global retrieval remains | [Linear attention](linear-attention-as-fixed-state-memory.md), [delta and gated memory](delta-rule-and-gated-associative-memory.md), [parallel DeltaNet](parallel-deltanet-chunkwise-training.md), [Gated DeltaNet](gated-deltanet-architecture-and-training.md), [Kimi Linear](kimi-linear-hybrid-attention-architecture.md) | Implement or annotate the recurrence transitions and compare state size, retrieval ability, prefill parallelism, and decode behavior |
| 9.4. Kimi K3: integrated architecture by information path | Decompose K3 into sequence memory (KDA), token retrieval (MLA), depth retrieval (AttnRes), sparse channel mixing (Stable LatentMoE), and native vision input; treat their roles as complementary rather than one headline novelty | [Kimi K3 architecture](kimi-k3-hybrid-retrieval-architecture.md), [Attention Residuals](attention-residuals.md), [Stable LatentMoE](stable-latentmoe-and-quantile-balancing.md), [native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md), [lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) | Annotate one K3 macrocycle and trace what state grows with sequence length, remains fixed, grows with depth blocks, or is sparsely activated |
| 9.5. Comparative reading and evidence discipline | Compare design choices under matched dimensions—memory addressability, state growth, active versus total parameters, positional handling, training/serving cost—and distinguish component ablation from whole-model correlation | [DeepSeek-V3 evaluation limits](deepseek-v3-post-training-evaluation-and-limitations.md), [Kimi K3 evaluation limits](kimi-k3-evaluation-and-limitations.md), [Kimi Linear evidence](kimi-linear-hybrid-attention-architecture.md) | Write a one-page comparison containing only scoped claims; mark author-reported results, missing ablations, workload dependencies, and unsupported causal claims |

The recommended order is sequential: **9.1 → 9.2 → 9.3 → 9.4 → 9.5**. DeepSeek is read before Kimi not as a chronology claim, but because MLA and fine-grained MoE provide reusable reference points for understanding Kimi's hybrid retrieval and latent experts.

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

- **Uses:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md), [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md), [Multi-head Latent Attention](multi-head-latent-attention.md), and [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) as architectural milestones.
- **Synthesizes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), [Structured State Space Duality](structured-state-space-duality.md), and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) into a prerequisite order.

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex).
[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training,” [source](../raw/gpt.pdf).
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” [source](../raw/arXiv-2405.04434v5/main.tex).
[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” [source](../raw/arXiv-2510.26692v2/main.tex).
[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” [source](../raw/arXiv-2405.21060v1/structure.tex).
[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” [source](../raw/arXiv-2607.24653v1/main.tex).
[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” [source](../raw/arXiv-2412.19437v2/main.tex).
[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” [source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).
