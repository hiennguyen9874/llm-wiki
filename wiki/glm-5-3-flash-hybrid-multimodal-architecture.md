---
type: Concept
title: GLM-5.3-Flash hybrid multimodal architecture
description: GLM-5.3-Flash is a reported 320B-total/18B-active native multimodal MoE whose 45-layer text backbone combines 34 KDA layers, 11 pooled-index DSA layers, four-stream mHC residuals, and a separate image/video encoder.
tags: [glm-5-3-flash, hybrid-attention, kimi-delta-attention, deepseek-sparse-attention, mixture-of-experts, multimodal, mhc]
status: stable
created: 2026-08-26
generated: { by: llm-wiki-agent/1, at: 2026-08-26T15:18:07Z }
sources:
  - id: glm53-card
    resource: ../raw/GLM-5.3-Flash/README.md
    title: GLM-5.3-Flash model card
  - id: glm53-blog
    resource: ../raw/GLM-5.3-Flash/blog.md
    title: GLM-5.3-Flash release blog
  - id: glm53-config
    resource: ../raw/GLM-5.3-Flash/config.json
    title: GLM-5.3-Flash checkpoint configuration
  - id: glm53-modeling
    resource: ../raw/GLM-5.3-Flash/modeling_glm5_next.py
    title: GLM-5.3-Flash Transformers modeling implementation
  - id: glm53-processing
    resource: ../raw/GLM-5.3-Flash/processing_glm5_next.py
    title: GLM-5.3-Flash multimodal processor implementation
  - id: glm53-video-processing
    resource: ../raw/GLM-5.3-Flash/video_processing_glm5_next.py
    title: GLM-5.3-Flash video processor implementation
---

# GLM-5.3-Flash hybrid multimodal architecture

GLM-5.3-Flash is a vendor-reported 320B-total, 18B-active native multimodal MoE trained from a new base on a stated 30T-token multimodal corpus. Its released configuration implements a 45-layer text backbone with 34 fixed-state Kimi Delta Attention (KDA) layers and 11 token-cached DeepSeek Sparse Attention (DSA) layers, four-stream manifold-constrained Hyper-Connections (mHC), and a separate 24-block vision encoder for images and video.[^glm53-card][^glm53-config][^glm53-modeling]

## Text backbone and hybrid memory

The text backbone has width 4,096, a 154,880-token vocabulary, and an explicit three-KDA-to-one-DSA schedule through layer 43 followed by one final KDA layer. KDA uses 64 heads of width 128, depthwise causal convolution of width four, learned decay, a sigmoid delta-update strength, chunkwise sequence processing, and recurrent one-token decoding. Its cache stores convolution and recurrent states instead of appending token KV entries.[^glm53-config][^glm53-modeling]

Each DSA layer applies NoPE MLA with rank-1,536 query compression and rank-512 joint KV compression, then uses a 32-head indexer to choose among groups of four prior tokens. With configured top-k 2,048, it scores up to 512 complete pools, expands chosen pools back to raw token indices, and always appends the visible incomplete tail of at most three tokens. All 45 configured indexer modes are `full`, so this checkpoint does not use the implementation’s optional cross-layer top-k sharing.[^glm53-config][^glm53-modeling]

The reference path expands latent KV to 64 heads with 256-dimensional keys and values before updating its ordinary attention cache. Thus the bundle establishes sparse reads, but does not demonstrate an optimized latent-cache representation or bounded end-to-end context state; the 11 DSA layers and their indexer caches still grow with sequence length.[^glm53-modeling]

## Sparse capacity and residual paths

The first three FFNs are dense with intermediate width 12,288. The remaining 42 are MoE blocks with 288 routed experts and one shared expert, each of width 2,048; sigmoid routing selects eight routed experts per token, normalizes their selected weights, and scales them by 2.5. The router includes a non-trainable correction-bias buffer and the causal-LM wrapper can add a Switch-style auxiliary balancing loss with coefficient 0.001, so the release combines bias-adjusted assignment with an optional auxiliary objective rather than documenting auxiliary-loss-free training.[^glm53-config][^glm53-modeling]

At both attention and FFN sites, mHC expands the residual into four streams. Learned collapse and output-placement weights surround each sublayer, while a learned 4×4 stream mixer is projected toward a doubly stochastic matrix through 20 Sinkhorn iterations. The final text representation is the unweighted mean of the four streams, followed by RMS normalization.[^glm53-config][^glm53-modeling]

## Native image and video path

The vision encoder has 24 blocks at width 1,024, 16 full-attention heads, 14×14 spatial patches, temporal patch size two, and 2×2 spatial merging before projection to the 4,096-dimensional language space. Image and video features replace placeholder-token embeddings; videos are sampled at a default two frames per second, capped at 2,048 frames, grouped in temporal pairs, and rendered as timestamped image-token spans inside video delimiters.[^glm53-config][^glm53-modeling][^glm53-processing][^glm53-video-processing]

The release blog says visual-coding data synthesis trained trajectories in which the model inspects and iteratively refines rendered outputs. For frontend work it also reports reinforcement learning from environment feedback and agent-based GUI verification against user flows. These are high-level training claims: the source gives no corpus composition, trajectory counts, reward definition, ablation, or reproducible training procedure.[^glm53-blog]

## Reported efficiency and base-model evidence

Against GLM-4.5, the blog attributes lower inference cost to reducing the total scale from 355B to 320B, active parameters from 32B to 18B, and depth from 92 to 45 layers. In a normalized BF16 comparison averaging attention compute per head per layer and KV-cache size per layer, it reports 3.0× lower attention compute and 4.4× lower cache than GLM-5.3. It also says GLM-5.3-Flash has the lowest attention compute among the four compared models, while retaining slightly more cache than Kimi-K3 and DeepSeek-V4-Flash.[^glm53-blog]

These figures are architecture-normalized vendor calculations, not measured end-to-end latency or total serving memory. The blog’s base-model table reports GLM-5.3-Flash-Base ahead of GLM-4.5-Base on BBH, LiveCodeBench-Base, and SimpleQA, tied on HellaSwag, and behind by 0.5 on MMLU; it also reports a mixed comparison with GLM-5-Base and notes that DeepSeek-V4-Flash-Base was run in Z.ai’s internal framework.[^glm53-blog]

The model card and blog call this the first natively multimodal GLM-5-series model, but provide no detailed pre-training recipe beyond the 30T-token statement, modality mixture, vision-language ablations, or evidence isolating corpus, architecture, and training effects.[^glm53-card][^glm53-blog]

## Relationships

- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through its KDA-majority sequence mixer.[^glm53-modeling]
- **Uses:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) with four-token learned pooling before top-k selection.[^glm53-modeling]
- **Uses:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) at both sublayers of every text block.[^glm53-modeling]
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through top-8 routing plus a shared expert.[^glm53-config]
- **Evaluated by:** [GLM-5.3-Flash evaluation, serving, and evidence limits](glm-5-3-flash-evaluation-serving-and-evidence-limits.md).
- **Successor context:** Unlike [GLM-5 architecture, pre-training, and systems](glm-5-architecture-pretraining-and-systems.md), which uses MLA/DSA throughout, GLM-5.3-Flash places recurrent KDA in most layers and adds native vision input.[^glm53-card][^glm53-config]

## Evidence limits

The model card and blog supply the 320B/18B parameter counts, 30T-token statement, qualitative training account, and vendor-normalized efficiency comparisons; the configuration and generated Transformers module supply the layer-level implementation. The bundle contains no weights, tokenizer files, training code, optimizer schedule, data composition, architecture ablations, safety report, measured cache footprint, or end-to-end latency. `num_nextn_predict_layers` is set to one, but the causal-LM class builds no MTP module and ignores unexpected layer-45/shared-head keys, so this release does not establish a runnable MTP path.[^glm53-card][^glm53-blog][^glm53-config][^glm53-modeling]

[^glm53-card]: Z.ai, “GLM-5.3-Flash,” [model card](../raw/GLM-5.3-Flash/README.md), Introduction and serving-framework list.

[^glm53-blog]: Z.ai, “GLM-5.3-Flash,” [release blog](../raw/GLM-5.3-Flash/blog.md), “Architecture for Extreme Efficiency,” “Visual Intelligence in the Coding Loop,” and base-model comparison. The blog’s externally hosted figures and embedded PDF were not available as local attachments and were not independently inspected.

[^glm53-config]: Z.ai, “GLM-5.3-Flash checkpoint configuration,” [source](../raw/GLM-5.3-Flash/config.json), text, vision, quantization, and multimodal-token configuration.

[^glm53-modeling]: Z.ai and Hugging Face, “GLM-5.3-Flash Transformers modeling implementation,” [source](../raw/GLM-5.3-Flash/modeling_glm5_next.py), router, KDA, pooled DSA indexer, mHC, vision, multimodal model, and conditional-generation classes.

[^glm53-processing]: Z.ai and Hugging Face, “GLM-5.3-Flash multimodal processor implementation,” [source](../raw/GLM-5.3-Flash/processing_glm5_next.py), image/video token replacement, timestamps, and multimodal token types.

[^glm53-video-processing]: Z.ai and Hugging Face, “GLM-5.3-Flash video processor implementation,” [source](../raw/GLM-5.3-Flash/video_processing_glm5_next.py), frame sampling, limits, resizing, and patchification.
