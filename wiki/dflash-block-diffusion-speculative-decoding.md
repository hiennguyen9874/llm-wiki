---
type: Concept
title: DFlash block-diffusion speculative decoding
description: DFlash conditions a lightweight block-diffusion drafter on frozen target-model hidden features injected as persistent KV entries, proposing a token block in one parallel pass for target verification.
tags: [speculative-decoding, diffusion, draft-model, kv-injection, inference]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-20T08:49:07Z }
sources:
  - id: dflash-2026
    resource: ../raw/arXiv-2602.06036v2/main.tex
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: nemotron-dflash-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DFlash.md
    title: NVIDIA Nemotron 3.5 Lightning DFlash model card
---

# DFlash block-diffusion speculative decoding

DFlash uses a small block-diffusion model to propose multiple future tokens in one parallel forward pass, then relies on the frozen autoregressive target to verify them. Its central conditioning mechanism fuses hidden states from several target layers and injects the result as persistent key/value entries into every draft layer, giving a deeper drafter repeated access to target context without making drafting autoregressive.[^dflash-2026]

## Inference mechanism

After target prefill produces a clean token, DFlash concatenates hidden states sampled from shallow through deep target layers and maps them through a shared projection and RMSNorm. Each draft layer computes queries only from draft tokens, while its keys and values concatenate projected target features with draft-token features:

$$
H_t=\operatorname{RMSNorm}(W_c[H^{(l_1)};\ldots;H^{(l_5)}]),
$$

$$
Q_i=W_i^QH_d,\qquad K_i=[W_i^KH_t;W_i^KH_d],\qquad V_i=[W_i^VH_t;W_i^VH_d].
$$

The target features are cached and reused as contextual KV entries at every draft layer. The drafter simultaneously predicts the masked positions following the clean target token; accepted proposals and the target’s next clean token then seed another cycle.[^dflash-2026]

This changes the draft-cost trade-off. An autoregressive drafter needs roughly one sequential pass per proposal step, whereas DFlash’s block cost is one parallel pass for a moderate block. A deeper diffusion drafter can therefore improve proposal quality without multiplying sequential latency, although depth still adds compute and eventually reduces end-to-end speedup.[^dflash-2026]

## Training alignment

The target remains frozen, and the draft shares its frozen token embedding and language-model head. Training differs from generic block diffusion in four important ways:[^dflash-2026]

- Random response tokens become clean block anchors, matching inference cycles that begin with a target-produced token; the remaining block positions are masked and predicted in parallel.
- Multiple sampled blocks are packed into one sequence with a sparse mask: attention is bidirectional within a block but blocked across blocks, while each block can read corresponding target features.
- Position-weighted cross-entropy uses $w_k=\exp(-(k-1)/\gamma)$ because an early mismatch invalidates the remaining speculative prefix.
- A fixed number of sampled anchors bounds long-context training cost and varies coverage across epochs.

The reported default uses five draft layers and block size 16 for Qwen3 instruct models, eight layers for Qwen3-Coder, and block size 10 for LLaMA-3.1. Target responses, rather than original dataset responses, form the training targets to increase target alignment.[^dflash-2026]

## Design evidence and costs

A five-layer diffusion drafter without target features produced only 2.65–3.73× author-measured speedup on four math evaluations, supporting the need for target conditioning within this setup. KV injection also outperformed one-time input fusion in matched five-layer ablations for both autoregressive and block-diffusion drafting. Increasing draft depth raised acceptance length, but five layers generally matched or exceeded eight-layer end-to-end speedup; larger training blocks generalized down to smaller inference blocks, while the reverse transfer was weaker.[^dflash-2026]

KV injection adds a shared $W_c\in\mathbb{R}^{D\times5D}$ projection plus activations and per-layer projected KV use. For the paper’s Qwen3.5-35B-A3B example at $D=2048$, the shared BF16 projection is about 42 MB versus a reported roughly 70 GB target, but cached target-feature storage grows linearly with the number of extracted layers during offline training.[^dflash-2026]

## Nemotron 3.5 Lightning checkpoint

NVIDIA’s target-specific Nemotron 3.5 Lightning DFlash release is an 833M-parameter NVFP4 draft (481M non-embedding parameters) with dense MLPs and non-causal, full-sequence GQA. It is intended to accompany the 30B-total/3B-active [Nemotron 3.5 Lightning target](nemotron-3-5-lightning-architecture-and-training.md), not run as a standalone language model. The card reports vLLM and llama.cpp support and positions it for low-concurrency data-centre and workstation serving, but does not disclose its layer count, target-feature injection details, memory footprint, or end-to-end latency.[^nemotron-dflash-card]

## Relationships

- **Operationalizes:** [Speculative decoding exact sampling](speculative-decoding-exact-sampling.md) by supplying parallel proposals for target verification.
- **Evaluated by:** [DFlash evaluation and serving trade-offs](dflash-evaluation-and-serving-trade-offs.md).
- **Extended by:** [DFlash 2 parallel selection and local convolution](dflash-2-parallel-selection-and-local-convolution.md), which adds coherent candidate selection and block-local convolution while retaining parallel drafting.
- **Extended by:** [DSpark parallel-draft speculative decoding](dspark-parallel-draft-speculative-decoding.md), according to the DSpark model card; the sources do not establish that DSpark preserves every DFlash training and KV-injection detail.
- **Qualified by:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md), because acceptance, block verification, concurrency, and draft cost determine realized acceleration.

## Evidence limits

The mechanism and ablations are primary author evidence, but the paper does not independently establish that target hidden states literally encode future tokens or that diffusion drafting is universally preferable. DFlash requires a separately trained, target-specific drafter; the reported training uses target-generated responses, frozen shared vocabulary projections, and model-specific feature layers and block sizes. Exact target-distribution preservation depends on the verification implementation, which this paper describes at a system level rather than re-deriving.[^dflash-2026]

[^dflash-2026]: Chen, Liang, and Liu, “DFlash: Block Diffusion for Flash Speculative Decoding,” arXiv:2602.06036v2, [source](../raw/arXiv-2602.06036v2/main.tex), Sections 3–5 and Appendix A–B, F, including the inference/training diagrams and ablation tables.

[^nemotron-dflash-card]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning DFlash,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DFlash.md), Model Architecture, Use Case, and DFlash Speculative Decoding.
