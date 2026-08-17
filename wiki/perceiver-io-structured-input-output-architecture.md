---
type: Concept
title: Perceiver IO structured input–output architecture
description: A latent-attention architecture that maps arbitrary input arrays to query-defined structured outputs with linear scaling in input and output size.
tags: [attention, multimodal-learning, multitask-learning, structured-prediction, efficient-architectures]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:29:48Z }
sources:
  - id: jaegle-2021-perceiver-io
    resource: ../raw/2107.14795_Perceiver/perceiver.tex
    title: Perceiver IO: A General Architecture for Structured Inputs & Outputs
---

# Perceiver IO structured input–output architecture

Perceiver IO maps arbitrary input arrays to query-defined, structured output arrays through a fixed-size latent array. It uses cross-attention to read inputs into latents and write from latents to output queries, concentrating deep self-attention in the latent space.[^jaegle-2021-perceiver-io]

## Architecture and scaling

- **Read:** An encoder cross-attention module maps an input array $x \in \mathbb{R}^{M \times C}$ into $N$ latent vectors $z \in \mathbb{R}^{N \times D}$; latents supply queries and input elements supply keys and values.[^jaegle-2021-perceiver-io]
- **Process:** A stack of latent self-attention and MLP modules refines the $N$ latents. Its depth is independent of input and output array sizes.[^jaegle-2021-perceiver-io]
- **Write:** Decoder cross-attention maps an $O$-element output-query array to $O$ outputs. A query can combine position, task or modality embeddings, input features, or learned vectors, so its index dimension determines the output shape and semantics.[^jaegle-2021-perceiver-io]
- For attention feature size $F$ and $L$ latent blocks, the paper gives attention complexity $\mathcal{O}([M + O + LN]NF)$: input and output cost is linear, while deep processing is performed in the fixed latent space.[^jaegle-2021-perceiver-io]

## Queries and decoding

- Position queries address sequence or spatial outputs; task and modality embeddings distinguish heterogeneous outputs; input-dependent queries associate predictions with entities or locations. Since each output depends only on its query and the latents, outputs can be decoded in parallel.[^jaegle-2021-perceiver-io]
- For large output arrays, training can sample query points and compute loss on that subset; inference can decode the full array in batches.[^jaegle-2021-perceiver-io]
- A single learned query is also a classification or regression head. Unlike Perceiver’s average-and-project decoder, the attention decoder uses data-dependent latent weights, a value projection, and an MLP; this is more expressive and extends directly to dense outputs.[^jaegle-2021-perceiver-io]
- The paper sometimes omits the decoder residual from a query to its result when that query contains input-space features, avoiding a requirement for the model to offset those features in its prediction.[^jaegle-2021-perceiver-io]

## Reported evidence

- On GLUE, a model operating directly on 2,048 UTF-8 bytes scored 81.0 at 113B FLOPs, versus 71.5 for the paper’s FLOPs-matched byte-level BERT; Perceiver IO++ reached 81.8. These are author-reported, benchmark-specific results.[^jaegle-2021-perceiver-io]
- For optical flow, the paper reports Sintel endpoint errors of 1.81 (clean) and 2.42 (final), compared with 1.95 and 2.57 for its cited RAFT baseline, without explicit cost volumes, warping, or hierarchical 2D latents.[^jaegle-2021-perceiver-io]
- In ImageNet experiments, query decoding consistently beat the original Perceiver decoder; the reported JFT-pretrained configurations reached 84.5% without convolutional preprocessing and 86.4% with it. On AudioSet, query decoding improved mAP from 42.4 to 43.3 for raw-audio-plus-video and from 43.6 to 44.9 for mel-spectrogram-plus-video configurations.[^jaegle-2021-perceiver-io]
- Replacing AlphaStar’s entity Transformer with a 32-latent Perceiver IO preserved the reported 87% win rate against the Elite bot after behavioral cloning while reducing the entity encoder’s FLOPs from 3.3B to 0.93B. This did not improve whole-system training throughput because that encoder was not the bottleneck.[^jaegle-2021-perceiver-io]

## Limits

- All input points must still be encoded simultaneously. Query batching reduces output cost but not this input-side memory requirement; the authors identify it as the limiting factor for larger raw video and audio inputs.[^jaegle-2021-perceiver-io]
- The paper finds that convolutional downsampling and RAFT-style upsampling change the optical-flow accuracy/efficiency trade-off, and reports that its full-resolution model is slower than RAFT on GPUs but faster on the tested TPU. Such hardware and benchmark results are not general deployment guarantees.[^jaegle-2021-perceiver-io]

[^jaegle-2021-perceiver-io]: Jaegle et al., “Perceiver IO: A General Architecture for Structured Inputs & Outputs” (2021), [source manuscript](../raw/2107.14795_Perceiver/perceiver.tex).
