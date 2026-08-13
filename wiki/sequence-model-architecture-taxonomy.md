---
type: Synthesis
title: Sequence-model architecture taxonomy
description: A layered taxonomy separates sequence backbones from capacity/context mechanisms and system-level architectures, clarifying their distinct memory, retrieval, and serving trade-offs.
tags: [architecture, attention, ssm, linear-attention, moe, memory, multimodal, agents]
status: draft
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T09:33:24Z }
sources:
  - id: transformer-architecture-survey
    resource: ../raw/TongHopKienTrucTransformer.md
    title: "Tổng hợp kiến trúc Transformer"
---

# Sequence-model architecture taxonomy

A useful comparison separates three layers that are often conflated: the **sequence backbone** that mixes tokens, **capacity and context mechanisms** that change cost or memory behavior, and the **system architecture** around a model. Under this framing, MoE, RAG, agents, and multimodal adapters usually extend or compose a backbone rather than replace it.[^transformer-architecture-survey]

## 1. Sequence backbones

| Family | Memory and retrieval model | Core trade-off |
|---|---|---|
| Full or restricted Transformer | Token-addressable attention over retained K/V entries | Direct global retrieval versus context-growing cache and quadratic full-sequence interactions |
| SSM / recurrent mixer | A recurrent state summarizes history | Linear sequence processing and bounded state versus lossy compression of prior tokens |
| Linear attention / delta-rule memory | Fixed-size associative or fast-weight state | Recurrent decoding and bounded state versus association interference and imperfect exact recall |
| Long convolution | A long-range convolutional kernel with gating | Near-linear processing versus weaker content-addressable retrieval |
| Hybrid | Recurrent or local layers plus periodic attention | Retains a cheaper main path while restoring some direct retrieval |

These labels describe the token-mixing mechanism, not a universal quality ranking. Full attention supplies direct token-to-token paths; fixed-state alternatives must encode multiple historical associations in finite state. Practical costs also depend on training versus prefill versus decode, kernels, cache representation, and hardware.[^transformer-architecture-survey]

## 2. Orthogonal scaling and context mechanisms

- **MoE** ordinarily replaces or augments the FFN with sparsely routed experts. It increases total parameter capacity without making every token execute every expert, but adds router, load-balancing, dispatch, and total-weight-memory constraints.[^transformer-architecture-survey]
- **Attention efficiency** includes MQA/GQA, latent KV representations, windows, and sparse selection. These retain Transformer-style retrieval to different degrees while reducing cache size, bandwidth, or token interactions.[^transformer-architecture-survey]
- **Memory extensions** include external retrieval, hierarchical summaries, and learned or fast-weight memory updated at inference. They should be evaluated separately from the backbone: retrieval quality, update policy, and evidence use can each fail independently.[^transformer-architecture-survey]
- **Adaptive compute** varies expert routing, depth, attention pattern, or inference budget by token or task. It is a computation-allocation policy, not a standalone sequence backbone.[^transformer-architecture-survey]

## 3. System architectures

Multimodal systems commonly attach modality encoders and project their features into a language-model token space; unified-token designs instead model several modalities together. Agentic systems add planning, tools, observations, verification, and persistent memory around a model. World and action models learn or use state transitions conditioned on actions. None of these system patterns implies one required backbone.[^transformer-architecture-survey]

The source further presents object- and event-centric representations as a practical alternative to passing every video pixel or frame token through global attention: maintain per-object temporal state, apply cross-object interaction selectively, and predict events. This is a design hypothesis for traffic or surveillance workloads, not comparative evidence that it is universally superior.[^transformer-architecture-survey]

## Decision guide

- Prefer **token-addressable attention** when exact copying, associative recall, and global in-context retrieval are central requirements.
- Consider **recurrent, SSM, or linear-memory paths** when streaming or context-independent decode state is decisive, while testing retrieval and overwrite workloads directly.
- Consider a **hybrid** when both bounded-state processing and periodic global retrieval are required.
- Treat **MoE** as capacity scaling, **RAG/external memory** as knowledge access, and **agents** as a control loop; assess each alongside the underlying sequence model.

## Relationships

- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md), which specifies full and restricted attention's asymptotic path and complexity trade-offs.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which details fixed-state associative-memory interference.
- **Uses:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) as a concrete state-space backbone.
- **Uses:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) as a concrete recurrent-plus-attention hybrid.
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) for MoE's routing and systems constraints.
- **Uses:** [Retrieval-augmented generation operational pipeline and trust limits](retrieval-augmented-generation-operational-pipeline-and-trust-limits.md) for external-memory failure modes.
- **Uses:** [ReAct reasoning-and-acting agent loop](react-reasoning-and-acting-agent-loop.md) as an agentic control-loop pattern.

## Evidence limits

This page compiles the supplied secondary survey's taxonomy and design guidance. It does not independently verify the source's model-specific attributions (including GLM-5.x, Mamba-3, Gated DeltaNet-2, and Titans), cited external papers, reported dates, numerical performance, or forward-looking forecasts. Existing linked concepts with primary local sources remain the stronger evidence for their individual mechanisms and evaluations.

[^transformer-architecture-survey]: “Tổng hợp kiến trúc Transformer,” [raw source](../raw/TongHopKienTrucTransformer.md). Secondary survey; its linked external citations were not independently ingested for this operation.
