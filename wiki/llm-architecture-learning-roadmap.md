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
  at: 2026-08-30T11:19:42+07:00
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
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
  - id: longcat-lsa-2026
    resource: ../raw/2608.01662_LongCatSparseAttention/longcat.tex
    title: "LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing"
  - id: ssm-introduction
    resource: ../raw/IntroductiontoStateSpaceModels.md
    title: Introduction to State Space Models
  - id: mamba-3-2026
    resource: ../raw/2603.15569_Mamba-3/structure.tex
    title: "Mamba-3: Improved Sequence Modeling using State Space Principles"
  - id: gated-deltanet-2-2026
    resource: ../raw/2605.22791_GatedDeltaNet-2/main.tex
    title: "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
  - id: hyena-2023
    resource: ../raw/2302.10866_HyenaHierarchy/main.tex
    title: "Hyena Hierarchy: Towards Larger Convolutional Language Models"
  - id: xlstm-2024
    resource: ../raw/2405.04517_xLSTM/xlstm.tex
    title: "xLSTM: Extended Long Short-Term Memory"
  - id: rwkv-x-2025
    resource: ../raw/2504.21463_RWKV-X/acl_latex.tex
    title: "RWKV-X: A Linear Complexity Hybrid Language Model"
  - id: mixture-of-layers-2026
    resource: ../raw/2605.09516_MixtureofLayerswithHybridAttention/submission.tex
    title: "Mixture of Layers with Hybrid Attention: Parallel Thin Blocks for Sparse Transformer Compute"
  - id: engram-2026
    resource: ../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex
    title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
  - id: flexattention-2024
    resource: ../raw/2412.05496_FlexAttention/main.tex
    title: "FlexAttention: A Programming Model for Generating Optimized Attention Kernels"
  - id: dflash-2026
    resource: ../raw/arXiv-2602.06036v2/main.tex
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
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

## Further additive stages for complete wiki coverage

These stages and substages are additive: they do not replace or rewrite any existing stage. Take 4.2 after 4.1, 6.2 after 6.1, 7.1 after Stage 7, 8.2–8.5 after the existing 8.1, 9.6–9.8 after 9.5, 10.1–10.2 within Stage 10, and Stage 12 after Stage 11. The order is editorial synthesis; architecture rankings remain workload-, implementation-, and evidence-dependent.[^qwen38-next-report][^mamba-3-2026][^engram-2026]

| Added stage | Learn | Build or verify before continuing | Primary concepts |
| --- | --- | --- | --- |
| 4.2. Encoder-only and encoder–decoder practice | Compare bidirectional encoding, causal decoding, and encoder–decoder cross-attention as distinct backbone and objective choices.[^vaswani-transformer-2017][^devlin-bert-2018] | Implement one encoder block and one cross-attention decoder block; verify bidirectional, causal, padding, and cross-attention masks on the same toy input | [Architecture map and masks](architecture-map-and-attention-masks-beginners-course.md), [Transformer sequence transduction](transformer-sequence-transduction-architecture.md), [BERT transfer architecture](bert-bidirectional-transfer-learning.md), [BERT MLM/NSP](bert-masked-language-and-next-sentence-pre-training.md) |
| 6.2. Sparse-attention architecture | Trace fixed local/block masks through learned token selection, pooled block retrieval, locality-aware index reuse, and compressed-entry attention; separate sparse reads from KV representation and cache retention.[^deepseek-v3-2-2025][^qwen38-next-report][^longcat-lsa-2026][^deepseek-v4-2026] | Implement local attention and a toy block top-k selector; record indexer work, selected-token recall, gather locality, retained cache, and whether remote tokens remain individually addressable | [Sparse Attention evolution](sparse-attention-evolution-and-architecture-comparison.md), [DSA](deepseek-sparse-attention.md), [QSA](qwen-sparse-attention.md), [LongCat Sparse Attention](longcat-sparse-attention.md), [CSA/HCA](compressed-sparse-and-heavily-compressed-attention.md) |
| 7.1. Sparse capacity beyond MoE | Distinguish routed FFN compute, routed complete blocks, and sparse lookup memory; account separately for total, active, resident, and accessed parameters.[^mixture-of-layers-2026][^engram-2026] | Build a hashed n-gram lookup with collision accounting and a toy whole-block router; compare bytes accessed per token, active FLOPs, dispatch, and parameter residency against a toy MoE | [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md), [Engram](engram-conditional-memory-architecture.md), [SCONE](scone-scalable-contextualized-offloaded-n-gram-embeddings.md), [Over-Encoding](over-encoding-hierarchical-n-gram-input-embeddings.md), [Mixture of Layers](mixture-of-layers-block-routing.md) |
| 8.2. Recurrent and SSM foundations | Derive continuous, discrete-recurrent, and convolutional SSM views; then trace selective SSMs through Mamba, SSD/Mamba-2, and Mamba-3.[^ssm-introduction][^dao-gu-2024][^mamba-3-2026] | Verify recurrence–convolution equivalence on a toy LTI SSM; annotate what Mamba selection, SSD chunking, and Mamba-3 transitions change in state update and parallel execution | [SSM foundations](state-space-models-continuous-recurrent-convolutional-forms.md), [Mamba selective SSM](mamba-selective-state-spaces-and-architecture.md), [SSD](structured-state-space-duality.md), [Mamba-2](mamba-2-architecture-and-parallelism.md), [Mamba-3](mamba-3-architecture-and-state-space-methods.md) |
| 8.3. Fixed-state memory-update frontier | Follow additive associative memory through delta correction, scalar forgetting, channel-wise KDA, and independently gated erase/write in Gated DeltaNet-2.[^kimi-linear-2025][^gated-deltanet-2-2026] | Implement the recurrence reductions showing when Gated DeltaNet-2 becomes KDA or Gated DeltaNet; compare interference, overwrite behavior, state size, and chunkwise training constraints | [Delta-rule memory](delta-rule-and-gated-associative-memory.md), [Gated DeltaNet](gated-deltanet-architecture-and-training.md), [Gated DeltaNet-2 course](gated-deltanet-2-beginners-course.md), [Mamba/KDA/Gated DeltaNet comparison](mamba-kda-gated-deltanet-comparison.md) |
| 8.4. Alternative sequence mixers and bounded hybrids | Compare Hyena's gated long convolutions, xLSTM's scalar/matrix memories, and RWKV-X's recurrent path plus bounded sparse token retention.[^hyena-2023][^xlstm-2024][^rwkv-x-2025] | Build a comparison ledger for recurrence/convolution form, training parallelism, decode state, token addressability, eviction, and unresolved complexity claims; implement one minimal mixer or recurrence | [Hyena](hyena-hierarchy-architecture.md), [xLSTM](xlstm-extended-lstm-architecture.md), [RWKV-X](rwkv-x-hybrid-architecture-and-training.md) |
| 8.5. Residual-path extensions and cross-layer routing | Extend the existing depth-path stage with feature-gated multi-stream residuals and side routing from recurrent memory; distinguish capacity widening, constrained mixing, depth retrieval, and cross-layer value injection.[^qwen38-next-report][^attnres-2026] | Trace one token through standard residual, mHC, Gated Residual, Block AttnRes, and CLVR diagrams; account for retained state, extra reads/writes, communication, and guarantees that do or do not transfer | [Residual-path comparison](residual-path-architecture-comparison.md), [Qwen Gated Residual](qwen-gated-residual.md), [mHC](manifold-constrained-hyper-connections.md), [Attention Residuals](attention-residuals.md), [CLVR](cross-layer-value-routing-for-delta-memories.md) |
| 9.6. Long-context architecture archetypes | Compare attention-centric token retrieval, compressed-entry retrieval, and recurrent-majority hybrids under matched addressability, state-growth, locality, and indexer dimensions.[^deepseek-v4-2026][^kimi-k3-2026] | Produce an archetype matrix and trace one remote fact through DeepSeek-V4-style CSA/HCA, GLM-style MLA/DSA, and Kimi-style KDA plus periodic MLA | [DeepSeek-V4 vs Kimi K3](deepseek-v4-and-kimi-k3-architecture-comparison.md), [GLM-5 vs Kimi K3](glm-5-and-kimi-k3-architecture-comparison.md), [Sparse Attention evolution](sparse-attention-evolution-and-architecture-comparison.md) |
| 9.7. Recurrent-majority frontier models | Read modern hybrids by mixer ratio, periodic-attention core, residual topology, MoE, conditional memory, modality path, and context-growing state rather than by model name alone.[^qwen38-next-report] | Decompose two released checkpoints into a per-layer schedule and state/cache ledger; separate config/code facts from vendor speed and quality claims | [GLM-5.3 vs Qwen3.8-Flash-Next](glm-5-3-flash-and-qwen3-8-flash-next-architecture-comparison.md), [Qwen3.8-A95B](qwen3-8-2-4t-a95b-checkpoint-architecture.md), [Nemotron 3.5 Lightning](nemotron-3-5-lightning-architecture-and-training.md), [Ling-3.0-flash](ling-3-0-flash-hybrid-architecture.md), [LongCat-2.0](longcat-2-0-sparse-attention-and-embedding-architecture.md) |
| 9.8. Workload-conditioned architecture selection | Choose among recurrent-plus-periodic attention, token-addressable sparse attention, and compressed-entry attention from workload constraints; design matched ablations rather than infer causality from whole-model results.[^deepseek-v4-2026][^kimi-k3-2026][^qwen38-next-report] | Write a requirement ledger and ablation plan covering mixer ratio, retrieval type, MoE routing, residual design, context curriculum, TTFT, decode latency, memory, and long-context recall | [Workload-conditioned selection](workload-conditioned-frontier-llm-architecture-selection.md), [Delta-rule vs SSM adoption](delta-rule-vs-ssm-frontier-adoption.md), [Comparative evidence discipline](comparative-reading-evidence-discipline-beginners-course.md) |
| 10.1. Programmable attention execution | Separate exact attention semantics, semantic sparsity, block-level skipping, paged KV indirection, and generated kernels.[^flexattention-2024] | Express local, causal, and custom sparse patterns with score/mask modification; inspect the resulting block mask and compare semantic output against a reference implementation | [FlashAttention evolution](flashattention-implementation-evolution.md), [FlexAttention programming model](flexattention-programming-model-and-compilation.md), [FlexAttention BlockMask and paging](flexattention-block-sparsity-and-paged-attention.md), [PagedAttention](pagedattention-kv-cache-serving.md) |
| 10.2. Draft-model and block-decoding architectures | Extend exact speculative decoding with target-specific parallel drafts, diffusion block drafting, hidden-feature conditioning, candidate-path selection, and the concurrency boundary.[^dflash-2026] | Diagram target, drafter, persistent draft state, verification, and acceptance; measure accepted length and end-to-end latency separately at low and high concurrency | [Speculative decoding trade-offs](speculative-decoding-performance-trade-offs.md), [DSpark](dspark-parallel-draft-speculative-decoding.md), [DFlash](dflash-block-diffusion-speculative-decoding.md), [DFlash 2](dflash-2-parallel-selection-and-local-convolution.md) |
| 12. Reference-implementation ladder | Consolidate the build-first path by reading progressively richer GPT implementations: scalar autograd, readable PyTorch, GPT-2 reproduction, then a modern cached GPT | Reproduce the same tiny corpus and generation checks where practical; annotate which implementation first introduces tensor autograd, checkpoint import, distributed training, modern attention choices, and KV-cached chat | [microgpt](microgpt-pure-python-gpt-reference-implementation.md), [minGPT](mingpt-educational-gpt-reference-implementation.md), [nanoGPT](nanogpt-gpt-2-reference-implementation.md), [nanochat](nanochat-modern-gpt-reference-implementation.md), [implementation comparison](mingpt-nanogpt-microgpt-comparison.md) |

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
[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture,” [source](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md).
[^longcat-lsa-2026]: LongCat Team, “LongCat Sparse Attention,” [source](../raw/2608.01662_LongCatSparseAttention/longcat.tex).
[^ssm-introduction]: “Introduction to State Space Models,” [source](../raw/IntroductiontoStateSpaceModels.md). Introductory supplied source; use the linked concept for its evidence boundary.
[^mamba-3-2026]: Lahoti et al., “Mamba-3: Improved Sequence Modeling using State Space Principles,” [source](../raw/2603.15569_Mamba-3/structure.tex).
[^gated-deltanet-2-2026]: Hatamizadeh, Choi, and Kautz, “Gated DeltaNet-2,” [source](../raw/2605.22791_GatedDeltaNet-2/main.tex).
[^hyena-2023]: Poli et al., “Hyena Hierarchy,” [source](../raw/2302.10866_HyenaHierarchy/main.tex).
[^xlstm-2024]: Beck et al., “xLSTM: Extended Long Short-Term Memory,” [source](../raw/2405.04517_xLSTM/xlstm.tex).
[^rwkv-x-2025]: Hou et al., “RWKV-X: A Linear Complexity Hybrid Language Model,” [source](../raw/2504.21463_RWKV-X/acl_latex.tex); the linked concept records an unresolved end-to-end complexity gap.
[^mixture-of-layers-2026]: Ternovtsii and Bilak, “Mixture of Layers with Hybrid Attention,” [source](../raw/2605.09516_MixtureofLayerswithHybridAttention/submission.tex).
[^engram-2026]: Cheng et al., “Conditional Memory via Scalable Lookup,” [source](../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex).
[^flexattention-2024]: FlexAttention authors, “FlexAttention: A Programming Model for Generating Optimized Attention Kernels,” [source](../raw/2412.05496_FlexAttention/main.tex).
[^dflash-2026]: DFlash authors, “DFlash: Block Diffusion for Flash Speculative Decoding,” [source](../raw/arXiv-2602.06036v2/main.tex).
