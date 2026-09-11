---
type: Concept
title: DSpark parallel-draft speculative decoding
description: DSpark is a target-specific parallel-draft family whose Kimi K3 and DeepSeek-V4.1 instances disclose different Markov/confidence designs, while Nemotron exposes a smaller sliding-window draft with fewer details.
tags: [speculative-decoding, draft-model, dspark, dflash, distillation]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-09-11T05:35:45Z }
sources:
  - id: deepseek-v41-tech-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: kimi-k3-dspark-card
    resource: ../raw/KimiK3DSparkspeculator.md
    title: "Kimi K3 DSpark speculator (Hugging Face model card)"
  - id: dflash-2026
    resource: ../raw/arXiv-2602.06036v2/main.tex
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: nemotron-dspark-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md
    title: NVIDIA Nemotron 3.5 Lightning DSpark model card
  - id: deepseek-v41-reference-model
    resource: ../raw/DeepSeek-V4.1-Flash/inference/model.py
    title: DeepSeek-V4.1-Flash minimal inference model
---

# DSpark parallel-draft speculative decoding

DSpark is a target-specific parallel-draft family rather than one fully disclosed topology. The published Kimi K3 card describes an extension of the DFlash parallel backbone with Markov logit-bias and per-position confidence heads: a 2.25B-parameter, five-layer full-attention GQA draft trained from random initialization by SpecForge online distillation against a frozen Kimi K3 target. NVIDIA’s Nemotron checkpoint instead discloses a 967M causal sliding-window GQA draft without documenting those heads, so Kimi-specific details should not be assumed for every DSpark release.[^kimi-k3-dspark-card][^nemotron-dspark-card]

## Draft architecture

- **DFlash backbone:** DSpark builds on DFlash's parallel-draft backbone, which proposes a masked token block in parallel. The DFlash paper defines its own backbone as a target-conditioned block-diffusion drafter with target features injected as KV entries at every draft layer; the DSpark card does not establish which of those exact implementation and training details DSpark retains.[^dflash-2026]
- **Markov logit-bias head:** biases draft logits during proposal, adding Markov-conditioned bias on top of the backbone's output.
- **Per-position confidence head:** predicts acceptance confidence at each draft position, supplying a per-position signal the architecture can use for draft behavior such as adaptive stopping.
- **Topology:** 5 full-attention Qwen3-style GQA layers, hidden size 7168, 64 query heads / 16 KV heads; `block_size=7`; verification width of 1 current token + 7 draft tokens.
- **Auxiliary target layers:** `[7, 23, 51, 67, 83]` — the draft reads hidden states from these Kimi K3 layers as auxiliary features.
- **Checkpoint:** 2,249,289,601 parameters in a single-file BF16 safetensors; target embedding and unembedding weights are not included, so the draft carries its own vocabulary projections.
- **Scale note:** at about 2.25B parameters against a roughly 2.8T-parameter Kimi K3 target, this draft is far larger than the small drafts typical of textbook speculative decoding, which changes the draft-cost side of the speedup trade-off.[^kimi-k3-dspark-card]

## Training

SpecForge online distillation captures hidden states from a frozen Kimi K3 target served by a live SGLang engine; the draft is trained from random initialization rather than fine-tuned from target layers.

- **Loss:** `0.1 CE + 0.9 L1 distillation + 1.0 confidence BCE`, with decay gamma 4.0, 512 sampled anchors per sequence, and `block_size=7`.
- **Topology:** 4 nodes × 4 GB300 (16 ranks) — 2 × TP8 target replicas, DP2 sampler, FSDP16 `SHARD_GRAD_OP` on the draft, and TP-batch scatter.
- **Global batch:** 8 per replica × 32 accumulation steps × 2 replicas = global batch 512.[^kimi-k3-dspark-card]

## Nemotron 3.5 Lightning checkpoint

NVIDIA’s Nemotron 3.5 Lightning DSpark release shows that DSpark topology is target-specific. This checkpoint is a 967M-parameter NVFP4 draft (615M non-embedding parameters) with dense MLPs and causal GQA, a 1,024-token sliding window on every layer, and per-head attention-sink bias. It is intended to accompany the 30B-total/3B-active [Nemotron 3.5 Lightning target](nemotron-3-5-lightning-architecture-and-training.md) in vLLM on DGX Spark or low-concurrency data-centre deployments. Unlike the Kimi card, this card does not disclose block size, confidence-head use, target-feature layers, or training loss, so the shared DSpark name does not establish implementation identity beyond the stated parallel-draft family.[^nemotron-dspark-card]

## DeepSeek-V4.1-Flash instance

The DeepSeek-V4.1-Flash reference defines a three-stage DSpark path over target-layer inputs 37–39. It initializes a five-position proposal with one current token and four noise tokens, uses sliding-window draft attention, sequentially adds a rank-256 Markov-logit bias while sampling the block, and predicts per-position confidence from draft hidden state plus Markov embedding. Its draft MoE has 128 routed experts and activates three.[^deepseek-v41-reference-model]

The technical report clarifies that the confidence head estimates conditional acceptance, the scheduler converts these to prefix-survival estimates, and verification length is selected against profiled engine-throughput curves and current load. DSpark is trained after pretraining against a frozen backbone, then continues alongside post-training without sending draft-objective gradients into the backbone. The readable runtime still omits confidence-scheduled target verification, and the report supplies no acceptance or throughput evaluation for this checkpoint.[^deepseek-v41-tech-report]

## Long-context extension

The Kimi draft is trained at a 65,536-token context. The published draft config enables YaRN-16 by default with `original_max_position_embeddings=65536` and `max_position_embeddings=1048576`, so 1M-token serving works without a separate draft config override.[^kimi-k3-dspark-card]

## Relationships

- **Extends:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md) with the Markov logit-bias and per-position confidence heads, according to the DSpark card.
- **Drafts for:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md); proposals still require target verification as in [Speculative decoding exact sampling](speculative-decoding-exact-sampling.md).
- **Used by:** [DeepSeek-V4.1-Flash architecture and pretraining](deepseek-v4-1-flash-architecture-and-pretraining.md), whose readable runtime omits the target-verification loop.
- **Differs from:** the Kimi K3 report's own EAGLE-3-style draft, which fine-tunes the target's pre-trained multi-token-prediction layer over AttnRes features; DSpark is a separate externally trained parallel-draft checkpoint for the same target.[^kimi-k3-dspark-card]
- **Evaluated by:** [DSpark speculator evaluation and deployment](dspark-speculator-evaluation-and-deployment.md).

## Evidence limits

The DFlash paper now supplies primary evidence for the base method, but the DSpark model card still does not specify how closely DSpark follows DFlash's KV injection, masking, loss weighting, or shared embedding/head design. It also does not define how the Markov condition is applied or how the confidence head is consumed at runtime. Parameter counts, layer choices, and loss weights are checkpoint-specific and may not generalize to other targets or draft sizes. DeepSeek-V4.1 exposes another forward architecture but still omits its confidence-scheduled verification loop.[^kimi-k3-dspark-card][^dflash-2026][^deepseek-v41-reference-model]

[^deepseek-v41-tech-report]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [technical report](../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md), Section 2.4.3.

[^kimi-k3-dspark-card]: RadixArk, “Kimi K3 DSpark speculator,” Hugging Face model card, [source](../raw/KimiK3DSparkspeculator.md), Overview, Model Specifications, and Training Details.

[^dflash-2026]: Chen, Liang, and Liu, “DFlash: Block Diffusion for Flash Speculative Decoding,” arXiv:2602.06036v2, [source](../raw/arXiv-2602.06036v2/main.tex), Sections 3–4 and Appendix B.

[^nemotron-dspark-card]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning DSpark,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md), Model Architecture, Use Case, and DSpark Speculative Decoding.

[^deepseek-v41-reference-model]: DeepSeek-AI, [DeepSeek-V4.1-Flash minimal inference model](../raw/DeepSeek-V4.1-Flash/inference/model.py), `ModelArgs`, `DSparkAttention`, `DSparkMarkovHead`, `DSparkConfidenceHead`, `DSparkBlock`, and `Transformer.forward_spec`.
