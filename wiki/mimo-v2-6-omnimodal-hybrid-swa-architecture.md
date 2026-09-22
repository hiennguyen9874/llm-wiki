---
type: Concept
title: MiMo-V2.6 omni-modal hybrid-SWA architecture
description: MiMo-V2.6 combines a sparse-MoE text backbone that interleaves 128-token sliding-window and global attention with visual and audio encoders, long-context mid-training, and a DFlash-style speculative decoder.
tags: [mimo-v2-6, multimodal, sliding-window-attention, mixture-of-experts, long-context]
status: stable
created: 2026-09-22
generated: { by: llm-wiki-agent/1, at: 2026-09-22T15:39:12Z }
sources:
  - id: mimo-v2-6-report-2026
    resource: ../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md
    scope: ../raw/MiMo-V2.6/
    kind: paper
    title: "MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement"
  - id: mimo-v2-6-checkpoint-bundle-2026
    resource: ../raw/MiMo-V2.6-Sources/MiMo-V2.6-Flash-RL.md
    scope: ../raw/MiMo-V2.6-Sources/
    kind: code
    title: MiMo-V2.6 Pro/Flash release bundle
---

# MiMo-V2.6 omni-modal hybrid-SWA architecture

MiMo-V2.6 is Xiaomi LLM-Core's omni-modal sparse-MoE family. The technical report describes Flash as 310B total/15B active parameters and Pro as 1.02T/42B; the later release card labels Flash 309B/15B. Both use a text backbone dominated by 128-token sliding-window attention (SWA), periodic global attention (GA), and modality encoders whose outputs replace reserved placeholders in the text-token stream. The report supports training claims, while the release bundle statically exposes checkpoint configuration and a partial Transformers inference path.[^mimo-v2-6-report-2026][^mimo-v2-6-checkpoint-bundle-2026]

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

## Released checkpoint implementation

The two supplied configs reproduce the reported 48-layer Flash schedule (39 SWA/9 GA, 256 routed experts) and 70-layer Pro schedule (60 SWA/10 GA, 384 experts); in each, only layer 0 has a dense FFN and every later layer routes to 8 experts. Both configs use fused QKV checkpoint layout, 192-dimensional Q/K heads, 128-dimensional V heads, partial RoPE over 64 Q/K dimensions, global RoPE base $10^7$, SWA base $10^4$, and a learned attention-sink bias only on SWA. Flash uses 64/8 SWA Q/KV heads and 64/4 global heads; Pro uses 128/8 for both.[^mimo-v2-6-checkpoint-bundle-2026]

Observed reference code applies pre-norm RMSNorm, causal full or sliding-window masks, grouped-query KV repetition, separate full/SWA rotary embeddings, and context-growing `DynamicCache`. Its MoE router takes sigmoid scores, adds a learned correction bias for expert choice, selects normalized top-8 weights, and combines expert outputs; because `n_group=topk_group=1` in both configs, group pruning does not reduce the candidate expert set. The `noaux_tc` router explicitly rejects training in this implementation.[^mimo-v2-6-checkpoint-bundle-2026]

The vision path patchifies $2\times16\times16$, uses GQA with full attention at layers 0, 9, 18, and 27, alternates row- and column-ordered local blocks, and merges $2\times2$ spatial groups before projecting to backbone width. The language-model wrapper replaces image, video, and audio placeholder embeddings only when counts match exactly. Audio input reaches the backbone as precomputed embeddings or 20-channel codec codes grouped four frames at a time; raw mel processing requires a separately loaded audio-tokenizer checkpoint that is not in the bundle.[^mimo-v2-6-checkpoint-bundle-2026]

## Contradictions and implementation gaps

- The technical report rounds Flash to 310B total parameters, while both release cards state 309B; no local weights are available for an independent parameter count.[^mimo-v2-6-report-2026][^mimo-v2-6-checkpoint-bundle-2026]
- Both cards advertise a five-layer speculative decoder that predicts seven subsequent tokens. Flash config instead contains `num_nextn_predict_layers: 3`, Pro has no corresponding key, and the shared reference class neither instantiates an MTP/DFlash module nor returns draft outputs; it explicitly ignores unexpected `model.mtp.*` weights. The advertised decoder is therefore not auditable through this code path.[^mimo-v2-6-checkpoint-bundle-2026]
- The attention-class docstring says Flash uses split Q/K/V projections and Pro fused QKV, but both supplied configs select `fused_qkv`. The executable config path takes precedence for these snapshots.[^mimo-v2-6-checkpoint-bundle-2026]

## Relationships

- **Uses:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md) according to the report and cards, although the supplied Transformers reference class omits that path.
- **Exposed through:** [MiMo-V2.6 release interface and evaluation limits](mimo-v2-6-release-interface-and-evaluation-limits.md).
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) through the row-norm-controlled Muown variant.
- **Supports:** [MiMo-V2.6 scaled agentic reinforcement learning](mimo-v2-6-scaled-agentic-rl.md) with sparse capacity, multimodal inputs, and one-million-token mid-training.
- **Deployed through:** [MiMo-V2.6 RL infrastructure and evidence limits](mimo-v2-6-rl-infrastructure-and-evidence-limits.md).

## Evidence and coverage limits

Report coverage included the full Markdown report and an inventory of all 31 sequentially named report figures. The architecture, grading, reward-hacking, and infrastructure diagrams were inspected directly; remaining figures were represented by captions, tables, or surrounding numerical prose. Fourteen unreferenced hash-named JPEGs were excluded as likely extraction by-products. The separate release bundle's six files—two cards, two configs, and two Python modules—were all statically inspected; Python syntax compilation and JSON parsing succeeded, but dependencies, weights, model construction, inference, and serving were not executed. Its referenced `assets/architecture.png`, weights, tokenizer/processors, and immutable upstream revision are absent.[^mimo-v2-6-report-2026][^mimo-v2-6-checkpoint-bundle-2026]

[^mimo-v2-6-report-2026]: Xiaomi LLM-Core, “MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement,” [technical report](../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md), Sections 1–3, Table 1, Figures 2–3, and Section 2.4 for the speculative decoder.
[^mimo-v2-6-checkpoint-bundle-2026]: Xiaomi MiMo Team, [MiMo-V2.6-Flash-RL card](../raw/MiMo-V2.6-Sources/MiMo-V2.6-Flash-RL.md) and package, 2026. Architecture tables; config keys `hybrid_layer_pattern`, `moe_layer_freq`, attention/rotary fields, and modality configs in both checkpoint JSON files; `configuration_mimo_v2.py::MiMoV2Config`; `modeling_mimo_v2.py::{MiMoV2MoEGate,MiMoV2Attention,MiMoVisionTransformer,MiMoAudioEncoder,MiMoV2ForCausalLM}`. Static syntax/JSON checks reproduced 2026-09-22; no immutable upstream revision was supplied.
