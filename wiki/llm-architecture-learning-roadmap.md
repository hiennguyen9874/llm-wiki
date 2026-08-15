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
  at: 2026-08-15T10:50:26+07:00
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
  - id: transformer-architecture-survey
    resource: ../raw/TongHopKienTrucTransformer.md
    title: "Tổng hợp kiến trúc Transformer"
  - id: devlin-bert-2018
    resource: ../raw/arXiv-1810.04805v2/main.tex
    title: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
  - id: llama-summary
    resource: ../raw/LLaMA.md
    title: "LLaMA overview (Vietnamese summary)"
  - id: alibi-summary
    resource: ../raw/ALiBi.md
    title: "ALiBi overview (Vietnamese summary)"
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: Attention Residuals
  - id: pagedattention-2023
    resource: ../raw/arXiv-2309.06180v1/main.tex
    title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  - id: speculative-decoding-summary
    resource: ../raw/SpeculativeDecoding.md
    title: "Speculative decoding overview (Vietnamese summary)"
  - id: qwen35-modeling
    resource: ../raw/Qwen3.5-27B/modeling_qwen3_5.py
    title: "Qwen3.5 Transformers reference modeling implementation"
  - id: rag-summary
    resource: ../raw/RAG.md
    title: "RAG overview (Vietnamese summary)"
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

## Additional stages to close coverage gaps

Take each substage immediately after its numbered parent; take stages 10 and 11 after stage 9. They extend the roadmap's architectural coverage without changing any existing stage. This ordering is editorial synthesis, not a claim that one implementation is universally preferable.[^transformer-architecture-survey][^devlin-bert-2018]

| Added stage | Learn | Build or verify before continuing | Primary concepts |
| --- | --- | --- | --- |
| 1.1. Architecture map and attention masks | Separate **sequence backbone**, capacity/context mechanism, and system architecture; distinguish encoder-only bidirectional self-attention, decoder-only causal self-attention, and encoder–decoder cross-attention | For the same toy input, visualize a bidirectional mask, causal mask, and a cross-attention score matrix; classify MoE, RAG, and multimodal input by layer rather than calling each a backbone | [Architecture map and attention masks course](architecture-map-and-attention-masks-beginners-course.md), [Sequence-model architecture taxonomy](sequence-model-architecture-taxonomy.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md) |
| 4.1. Modern decoder-block recipe | Treat the decoder block as interchangeable choices: input/position representation, pre- versus post-normalization, residual path, FFN nonlinearity/gating, and output/embedding tying—not just “attention + FFN” | Make the small GPT configurable; swap LayerNorm/RMSNorm and ReLU/SwiGLU while preserving tensor shapes, then record which changes alter parameter count, activation flow, and checkpoint compatibility | [Modern decoder-block recipe course](modern-decoder-block-recipe-beginners-course.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT-2 architecture](gpt-2-webtext-pre-training-and-architecture.md), [LLaMA](llama-efficient-pre-trained-language-models.md) |
| 6.1. Attention design matrix | Compare positional choices (sinusoidal/learned absolute, RoPE, ALiBi); KV-head sharing (MHA, MQA, GQA, MLA); and token-access patterns (full, sparse-selected, compressed plus local window) | Build a matrix recording what each choice changes: attention logits, retained KV bytes, which tokens remain addressable, full-sequence work, and decode-state growth; test causal equivalence before comparing long-context behavior | [Attention design matrix course](attention-design-matrix-beginners-course.md), [RoPE](rotary-position-embedding.md), [ALiBi](alibi-attention-with-linear-biases.md), [MQA/GQA](multi-query-and-grouped-query-attention.md), [MLA](multi-head-latent-attention.md), [DeepSeek Sparse Attention](deepseek-sparse-attention.md), [CSA/HCA](compressed-sparse-and-heavily-compressed-attention.md) |
| 8.1. Depth and residual-path design | Distinguish token-position retrieval from retrieval or mixing across **depth**; study ordinary residual accumulation, Attention Residuals, and constrained multi-channel residual mixing | Trace one token through a standard residual stack and an AttnRes block diagram; explicitly account for retained depth state and communication, rather than assuming a residual change is free | [Depth and residual-path design course](depth-and-residual-path-design-beginners-course.md), [Attention Residuals](attention-residuals.md), [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) |
| 10. Serving architecture and decode acceleration | Separate model semantics from runtime design: block-mapped/shared KV storage, batching and prefix reuse, attention engines, and draft–verify decoding | Implement a logical-to-physical KV block table or inspect one; measure prefill and decode separately; verify that speculative sampling preserves the target distribution under its stated procedure | [PagedAttention](pagedattention-kv-cache-serving.md), [FlashInfer](flashinfer-attention-engine.md), [Speculative decoding](speculative-decoding-exact-sampling.md) |
| 11. Multimodal and external-memory composition | Trace how a modality encoder reaches the text backbone, how positions are represented across modalities, and how external retrieved documents differ from parameters and KV state | Draw the Qwen text/vision boundary and state/cache ledger; separately diagram retriever → selected documents → generator, marking which component is trained, replaceable, and token-addressable | [Qwen3.5 checkpoint architecture](qwen3-5-27b-checkpoint-architecture.md), [Kimi K3 native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md), [RAG latent-document architecture](retrieval-augmented-generation-latent-document-architecture.md) |

These additions close the roadmap's coverage of architecture families, decoder modules, attention choices, depth-wise pathways, runtime systems, and multimodal/external-memory composition. They do **not** turn every system extension into an LLM backbone: RAG, serving schedulers, and modality encoders must still be evaluated alongside the sequence model they compose with.[^llama-summary][^alibi-summary][^deepseek-v3-2-2025][^deepseek-v4-2026][^attnres-2026][^pagedattention-2023][^speculative-decoding-summary][^qwen35-modeling][^rag-summary]

## Stage 9 curriculum: Frontier-model reading

Stage 9 should be split into **five learning parts**. The first establishes a repeatable reading method; the next three trace two architectural lineages and then decompose Kimi K3; the last prevents architecture-level conclusions from being inferred directly from headline model results. This split is editorial synthesis from the DeepSeek and Kimi reports and the GPT-2-to-Kimi-K3 explainer, not an experimentally validated course sequence.[^deepseek-v2-2024][^deepseek-v3-2024][^kimi-linear-2025][^kimi-k3-2026][^gpt2-kimi3-2026]

| Part | Learn | Reading path | Deliverable before continuing |
|---|---|---|---|
| 9.1. Baseline-to-bottleneck reading | Start from GPT-2's decoder block and classify each novelty by the bottleneck it targets: KV state, attention cost, FFN compute, routing balance, residual dilution, or hardware utilization | [Baseline-to-bottleneck course](baseline-to-bottleneck-frontier-model-reading-beginners-guide.md), [GPT-2 architecture](gpt-2-webtext-pre-training-and-architecture.md), [inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md), [KV caching](kv-caching.md) | Draw the dense baseline and create a four-column ledger: mechanism, replaced baseline, expected trade-off, evidence |
| 9.2. DeepSeek V2 → V3: efficient attention, sparse capacity, and co-design | Follow MLA and DeepSeekMoE from V2, then identify V3's auxiliary-loss-free balancing, multi-token prediction, FP8, and communication schedule; separate model architecture from training/serving systems | [DeepSeek V2→V3 course](deepseek-v2-to-v3-efficient-attention-sparse-capacity-co-design-beginners-course.md), [DeepSeek-V2](deepseek-v2-architecture-training-and-efficiency.md), [DeepSeek-V3 architecture](deepseek-v3-architecture-and-pretraining.md), [routing balance](auxiliary-loss-free-moe-load-balancing.md), [multi-token prediction](sequential-multi-token-prediction.md), [V3 systems and FP8](deepseek-v3-training-systems-and-fp8.md) | Make a V2→V3 diff and label every item as architecture, objective, numerical format, distributed system, or serving policy |
| 9.3. GPT-2 → Kimi Linear: changing the memory model | Trace softmax attention and sequence-growing KV cache through linear attention, delta correction, scalar decay, channel-wise KDA, and periodic MLA; explain why fixed-state memory needs correction/forgetting and why global retrieval remains | [GPT-2 → Kimi Linear course](gpt2-to-kimi-linear-memory-model-beginners-course.md), [Linear attention](linear-attention-as-fixed-state-memory.md), [delta and gated memory](delta-rule-and-gated-associative-memory.md), [parallel DeltaNet](parallel-deltanet-chunkwise-training.md), [Gated DeltaNet](gated-deltanet-architecture-and-training.md), [Kimi Linear](kimi-linear-hybrid-attention-architecture.md) | Implement or annotate the recurrence transitions and compare state size, retrieval ability, prefill parallelism, and decode behavior |
| 9.4. Kimi K3: integrated architecture by information path | Decompose K3 into sequence memory (KDA), token retrieval (MLA), depth retrieval (AttnRes), sparse channel mixing (Stable LatentMoE), and native vision input; treat their roles as complementary rather than one headline novelty | [Kimi K3 information-path course](kimi-k3-integrated-architecture-information-path-beginners-course.md), [Kimi K3 architecture](kimi-k3-hybrid-retrieval-architecture.md), [Attention Residuals](attention-residuals.md), [Stable LatentMoE](stable-latentmoe-and-quantile-balancing.md), [native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md), [lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) | Annotate one K3 macrocycle and trace what state grows with sequence length, remains fixed, grows with depth blocks, or is sparsely activated |
| 9.5. Comparative reading and evidence discipline | Compare design choices under matched dimensions—memory addressability, state growth, active versus total parameters, positional handling, training/serving cost—and distinguish component ablation from whole-model correlation | [Comparative reading và evidence discipline course](comparative-reading-evidence-discipline-beginners-course.md), [DeepSeek-V3 evaluation limits](deepseek-v3-post-training-evaluation-and-limitations.md), [Kimi K3 evaluation limits](kimi-k3-evaluation-and-limitations.md), [Kimi Linear evidence](kimi-linear-hybrid-attention-architecture.md) | Write a one-page comparison containing only scoped claims; mark author-reported results, missing ablations, workload dependencies, and unsupported causal claims |

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
[^transformer-architecture-survey]: “Tổng hợp kiến trúc Transformer,” [source](../raw/TongHopKienTrucTransformer.md). Secondary survey; model-specific attributions remain subject to its documented evidence limit.
[^devlin-bert-2018]: Devlin et al., “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,” [source](../raw/arXiv-1810.04805v2/main.tex).
[^llama-summary]: “LLaMA overview,” [source](../raw/LLaMA.md). Secondary-source evidence.
[^alibi-summary]: “ALiBi overview,” [source](../raw/ALiBi.md). Secondary-source evidence.
[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” [source](../raw/arXiv-2512.02556v1/main.tex).
[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” [source](../raw/arXiv-2606.19348v1/main.tex).
[^attnres-2026]: Kimi Team, “Attention Residuals,” [source](../raw/arXiv-2603.15031v1/main.tex).
[^pagedattention-2023]: Kwon et al., “Efficient Memory Management for Large Language Model Serving with PagedAttention,” [source](../raw/arXiv-2309.06180v1/main.tex).
[^speculative-decoding-summary]: “Speculative decoding overview,” [source](../raw/SpeculativeDecoding.md). Secondary-source evidence.
[^qwen35-modeling]: Qwen Team and Hugging Face, “Qwen3.5 Transformers reference modeling implementation,” [source](../raw/Qwen3.5-27B/modeling_qwen3_5.py).
[^rag-summary]: “RAG overview,” [source](../raw/RAG.md). Secondary-source evidence.
