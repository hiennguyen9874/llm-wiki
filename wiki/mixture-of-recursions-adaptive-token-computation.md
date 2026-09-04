---
type: Concept
title: Mixture-of-Recursions adaptive token computation
description: Mixture-of-Recursions combines tied recursive transformer blocks, learned token-specific recursion depth, and two KV-cache designs to trade quality, training compute, cache memory, and throughput.
tags: [adaptive-computation, kv-cache, parameter-sharing, recursive-transformers, routing]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T00:00:00Z }
sources:
  - id: bae2025mor
    resource: ../raw/arXiv-2507.10524v3/paper.tex
    title: "Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation"
---

# Mixture-of-Recursions adaptive token computation

Mixture-of-Recursions (MoR) is a recursively weight-tied transformer in which lightweight routers choose how many applications of a shared block each token receives. Its central systems claim is that routing, recursion-wise KV caching, and continuous depth-wise batching can jointly reduce unique parameters, selective attention work, cache traffic, and decoding bubbles; the reported quality and throughput trade-offs are limited to the paper's pretrained Llama/SmolLM-style models and evaluation protocol.[^bae2025mor]

## Design

- A shared recursive block is unrolled up to a configured maximum depth. The paper's preferred **Middle-Cycle** schedule keeps unique first and last layers while cycling shared middle layers.[^bae2025mor]
- **Expert-choice** routing selects a capacity-limited top-$k$ subset at each recursion depth, with hierarchical filtering: only a token selected at one depth can be considered at the next. This fixes the per-depth compute budget but is non-causal during full-sequence training; the authors use an auxiliary loss to make the main router's selected/unselected scores separable for inference.[^bae2025mor]
- **Token-choice** routing assigns a token's complete depth path at the outset. It avoids that leakage but needs load balancing; in the reported ablation it underperformed the expert-choice configuration.[^bae2025mor]
- With **recursion-wise caching**, only tokens active at a depth store and attend to KV pairs at that depth. Assuming the decreasing capacities used in the paper, it gives relative total KV memory/IO of $(N_r+1)/(2N_r)$ and per-layer attention FLOPs of $(k/N_{ctx})^2$ versus a vanilla transformer. **Recursive KV sharing** instead reuses first-recursion KV pairs at later depths, lowering total KV memory to $1/N_r$ but retaining full-context KV IO and giving per-layer attention FLOPs of $k/N_{ctx}$.[^bae2025mor]

## Reported evidence

- At 16.5e18 training FLOPs on the paper's 360M-base setup, two-recursion expert-choice MoR with recursion-wise caching used 167M non-embedding parameters, processed 27B training tokens, and reported FineWeb-Edu NLL 2.7511 and mean six-task few-shot accuracy 43.1%, versus 315M, 20B, 2.7824, and 42.3% for the vanilla baseline.[^bae2025mor]
- Holding training data at 20B tokens in that setup, the two-recursion expert-choice model used 12.3e18 FLOPs and reported 42.9% mean few-shot accuracy, versus vanilla's 16.5e18 FLOPs and 42.3%; the authors also report 19% lower training time and 25% lower peak memory than vanilla.[^bae2025mor]
- In the isoFLOP table using three recursions and expert-choice routing, MoR beat the recursive baseline across the listed 135M--1.7B base scales and budgets. Relative to vanilla, it was weaker at 135M but had higher reported mean few-shot accuracy at every listed 360M, 730M, and 1.7B budget point.[^bae2025mor]
- For 360M-base models at 16.5e18 FLOPs, the paper reports up to 2.06x decoding throughput for four-recursion MoR in its maximum-batch configuration. This is a configuration-specific measurement, not a general throughput guarantee.[^bae2025mor]
- Recursive KV sharing slightly degraded the listed expert-choice MoR result (41.9% versus 42.6% mean few-shot accuracy at three recursions and fixed FLOPs) but lowered memory needs. In a separate 10B-token comparison, it also degraded the listed token-choice result (38.6% versus 39.1%), contrary to the paper's narrative suggestion that extra shared context can sometimes help weaker token-choice routing.[^bae2025mor]

## Trust boundary and limitations

The evidence is from models pretrained from scratch on a deduplicated FineWeb-Edu subset, evaluated on FineWeb-Edu validation and six few-shot benchmarks, using 135M--1.7B base configurations; it does not establish behavior for instruction-tuned, reasoning, long-context, or production models.[^bae2025mor]

Expert-choice routing's fixed capacity depends on future-token information during training. The auxiliary-loss workaround made selected and unselected scores nearly perfectly separated in the authors' analysis, which they identify as making post-training capacity adjustment difficult. The authors also report a 1.7B, 68.5e18-FLOP comparison where the vanilla model's mean accuracy (48.9%) exceeded their best expert-choice MoR result (48.4%), so scaling superiority is not established.[^bae2025mor]

## Relationships

- Builds on: [Virtual logical depth scaling](virtual-logical-depth-scaling.md) — both reuse transformer weights across effective depth, while MoR additionally routes individual tokens and defines KV-cache policies.

[^bae2025mor]: Bae et al., *Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation*, source manuscript, abstract, §§1--5, appendix, and Tables 1--4 (arXiv:2507.10524v3, 2025).