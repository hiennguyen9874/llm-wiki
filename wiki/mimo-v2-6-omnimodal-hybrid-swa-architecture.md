---
type: Concept
title: MiMo-V2.6 omni-modal hybrid-SWA architecture
description: MiMo-V2.6 combines a sparse-MoE text backbone that interleaves 128-token sliding-window and global attention with visual and audio encoders, long-context mid-training, and a DFlash-style speculative decoder.
tags: [mimo-v2-6, multimodal, sliding-window-attention, mixture-of-experts, long-context]
status: stable
created: 2026-09-22
generated: { by: llm-wiki-agent/1, at: 2026-09-22T15:21:59Z }
sources:
  - id: mimo-v2-6-report-2026
    resource: ../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md
    scope: ../raw/MiMo-V2.6/
    kind: paper
    title: "MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement"
---

# MiMo-V2.6 omni-modal hybrid-SWA architecture

MiMo-V2.6 is Xiaomi LLM-Core's reported omni-modal sparse-MoE family. Flash has 310B total/15B active parameters and Pro 1.02T/42B; both use a text backbone dominated by 128-token sliding-window attention (SWA), periodic global attention (GA), and modality encoders whose outputs join the text-token stream. The supplied artifact establishes report-level architecture and training claims, not released checkpoint behavior.[^mimo-v2-6-report-2026]

## Text backbone

The backbone repeats hybrid groups of $N$ SWA blocks followed by one GA block. The first Transformer block is an exception: global attention plus a dense FFN is used for reported early-training stability; subsequent SWA and GA blocks use sparse MoE FFNs without shared experts. Flash has 48 main layers (39 SWA/9 GA), hidden size 4,096, 256 experts with 8 active, and Q/KV head counts of 64/8 for SWA and 64/4 for GA. Pro has 70 layers (60/10), hidden size 6,144, 384 experts with 8 active, and 128/8 Q/KV heads for both attention types.[^mimo-v2-6-report-2026]

This design bounds attention span in most layers but does **not** make model state context-independent: periodic GA layers still attend over the full retained sequence and require context-growing KV state. The architecture therefore trades the frequency of full-context computation against direct global access rather than replacing global retrieval with fixed-state memory. This is synthesis from the reported layer schedule.[^mimo-v2-6-report-2026]

## Visual and audio paths

MiMo-ViT has 28 layers (24 sink-augmented SWA/4 GA), alternates row-major and column-major visual-token serialization, and was reportedly pretrained from scratch on more than 4T image tokens while paired with a trainable small LLM. The report attributes cross-window propagation to attention sinks, alternating spatial serialization, and periodic GA, but refers elsewhere for controlled analysis.[^mimo-v2-6-report-2026]

Audio first passes through a log-mel convolutional front end, causal hybrid-SWA Transformer, downsampling to 25 Hz, and a 20-codebook residual vector quantizer. A jointly trained six-layer patch encoder sums codebook embeddings per frame, applies bidirectional attention within groups of four frames, concatenates the four outputs, and projects one backbone embedding per patch, reducing the sequence to 6.25 Hz. The tokenizer was reportedly trained on 20 million hours of speech, music, and other audio.[^mimo-v2-6-report-2026]

## Pre-training and long-context transition

Training proceeds from text-only backbone pre-training to joint omni-modal training. Flash reportedly sees 48T tokens (26T text, 22T omni), while Pro sees 30T (27T/3T), with context extended from 32K to 256K. Agent-centric mid-training then uses coding, general, visual, research, repository-code, and multimodal data, first at 256K and finally at 1M context.[^mimo-v2-6-report-2026]

Mid-training switches hidden matrices from AdamW to Muown, a Muon variant with explicit row-norm control, while embeddings, LM head, and router remain on AdamW. It also introduces MXFP4 quantization-aware training. The authors report no loss spike during the optimizer transition, but provide no matched ablation establishing which mid-training choice causes downstream gains.[^mimo-v2-6-report-2026]

## Speculative decoder

A five-layer dense-FFN drafter follows the block-diffusion design of [DFlash](dflash-block-diffusion-speculative-decoding.md). Conditioned on backbone features and a clean anchor token, it predicts seven following tokens in parallel; draft-token attention is bidirectional within the block and can read at most 1,024 preceding backbone positions. All draft layers use SWA and grouped queries. This module is distinct from the pre-training MTP objective despite the report's architecture diagram labeling the auxiliary path as MTP.[^mimo-v2-6-report-2026]

## Relationships

- **Uses:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md) for rollout and deployment drafting.
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) through the row-norm-controlled Muown variant.
- **Supports:** [MiMo-V2.6 scaled agentic reinforcement learning](mimo-v2-6-scaled-agentic-rl.md) with sparse capacity, multimodal inputs, and one-million-token mid-training.
- **Deployed through:** [MiMo-V2.6 RL infrastructure and evidence limits](mimo-v2-6-rl-infrastructure-and-evidence-limits.md).

## Evidence and coverage limits

Coverage included the full Markdown report and an inventory of all 31 sequentially named report figures. The architecture, grading, reward-hacking, and infrastructure diagrams were inspected directly; the remaining plots, diagrams, and qualitative examples were excluded from direct visual review because their material claims were reproduced in captions, tables, or surrounding numerical prose. Fourteen hash-named JPEGs are unreferenced by the report and were excluded as likely extraction duplicates or fragments. No source code, checkpoint configuration, bibliography file, explicit license, immutable revision, or upstream URL is present in the supplied package, and no training or inference claim was independently reproduced.[^mimo-v2-6-report-2026]

[^mimo-v2-6-report-2026]: Xiaomi LLM-Core, “MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement,” [technical report](../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md), Sections 1–3, Table 1, Figures 2–3, and Section 2.4 for the speculative decoder.
