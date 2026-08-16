---
type: Concept
title: Perceiver IO structured input–output architecture
description: A latent-attention architecture that maps arbitrary input arrays to query-defined structured outputs with linear scaling in input and output size.
tags: [attention, multimodal-learning, multitask-learning, structured-prediction, efficient-architectures]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:29:21Z }
sources:
  - id: jaegle-2021-perceiver-io
    resource: ../raw/2107.14795_Perceiver.md
    title: Perceiver IO: A General Architecture for Structured Inputs & Outputs
---

# Perceiver IO structured input–output architecture

Perceiver IO maps arbitrary input arrays to arbitrary, structured output arrays through a fixed-size latent array. It cross-attends from learned latents to inputs, processes only the latents with self-attention, then cross-attends from output queries to latents; each query specifies the semantics of one output element.[^jaegle-2021-perceiver-io]

## Architecture

- **Read:** An encoder cross-attention module maps an input array $x \in \mathbb{R}^{M \times C}$ into $N$ latent vectors $z \in \mathbb{R}^{N \times D}$, with the latents supplying the queries and input elements supplying keys and values.[^jaegle-2021-perceiver-io]
- **Process:** A stack of latent self-attention and MLP modules refines the $N$ latent vectors. Its depth is independent of input and output array sizes.[^jaegle-2021-perceiver-io]
- **Write:** A decoder cross-attention module maps an output-query array to $O$ output elements. Queries may combine position encodings, task or modality embeddings, input features, or learned vectors; their index dimension determines the output shape.[^jaegle-2021-perceiver-io]
- For attention feature size $F$ and $L$ latent-processing blocks, the paper gives attention complexity $\mathcal{O}([M + O + LN]NF)$. Thus encoding and decoding scale linearly with input and output sizes, while deep processing occurs in the fixed latent space rather than at full input/output resolution.[^jaegle-2021-perceiver-io]

## Output queries and training

- Position queries can address sequence or spatial outputs; learned task or modality embeddings distinguish heterogeneous outputs; and input-dependent queries can associate predictions with entities or locations. Output elements depend only on their query and the latent array, so they can be decoded in parallel.[^jaegle-2021-perceiver-io]
- For very large output arrays, the authors subsample queried output points and compute loss only on that subset during training, then decode the complete output in batches at test time.[^jaegle-2021-perceiver-io]
- A single query also supplies a classification head. Compared with Perceiver’s uniform average-and-project decoder, the query-based attention decoder uses data-dependent latent pooling and an MLP; the paper reports small, consistent classification improvements on its ImageNet and AudioSet experiments.[^jaegle-2021-perceiver-io]

## Reported evidence and limits

- In the paper’s GLUE evaluation, a byte-level model operating directly on 2,048 UTF-8 bytes achieved a mean score of 81.0 at 113B FLOPs, compared with 71.5 for its FLOPs-matched byte-level BERT baseline; the larger Perceiver IO++ model reached 81.8. These are benchmark-specific, author-reported results rather than a general performance guarantee.[^jaegle-2021-perceiver-io]
- The authors report Sintel optical-flow endpoint errors of 1.81 (clean) and 2.42 (final), versus 1.95 and 2.57 for the cited RAFT baseline, despite omitting explicit cost volumes, warping, and hierarchical 2D latent structure.[^jaegle-2021-perceiver-io]
- The architecture handled joint video, audio, and label autoencoding, but all input points still must be encoded simultaneously. The authors identify this input-side requirement as a limitation for scaling to still larger raw inputs.[^jaegle-2021-perceiver-io]

[^jaegle-2021-perceiver-io]: Jaegle et al., “Perceiver IO: A General Architecture for Structured Inputs & Outputs” (2021), [source](../raw/2107.14795_Perceiver.md).
