---
type: Concept
title: Kimi Delta Attention (KDA)
description: Delta-rule linear attention with channel-wise decay gates used in Kimi K3, traced from softmax and linear attention through DeltaNet, with crosstalk limits, NoPE positioning, and serving consequences.
tags: [kimi-delta-attention, linear-attention, deltanet, hybrid-attention, recurrent-state, nope, kimi-k3, models]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T10:30:00Z }
sources:
  - id: sglang-k3-day0
    resource: ../raw/kimi-k3-day0-support/index.md
    kind: article
    title: 'Kimi K3: Architecture and SGLang Day-0 Support'
---

Kimi Delta Attention (KDA) is the linear-attention layer that makes up 69 of Kimi K3's 93 layers. Softmax attention keeps one KV entry per token. KDA instead keeps a fixed-size recurrent state `S` per head and edits it in place. Each step decays the state channel by channel, then applies a DeltaNet-style error-correcting write. That keeps decode memory and compute per step constant, and it gives the model position information without RoPE[^sglang-k3-day0]. The trade-off is a capacity limit: unrelated writes leak into each other (crosstalk), and the gates can only manage that leakage, not remove it. For serving, the state's in-place overwrite and lack of a token axis change how prefix caching and context parallelism work (see [Serving consequences](#serving-consequences)).

## From softmax attention to a fixed-size state

**Classic MHA.** To decode token `t`, MHA appends its KV to the cache, then scores against every earlier key (`z_{t,i} = q_t·k_i / √d_k`), softmax-normalizes, and takes a weighted sum of values. A length-`N` sequence does about `N²/2` dot products, so compute is `O(N²)` and the cache is `O(N)`. In exchange, each position can be read back individually[^sglang-k3-day0].

**Linear attention.** History is folded into one matrix, `S = Σ_i k_i v_iᵀ`, and read with `o = Sᵀq`. The key sets the write direction and the value is the content written along it. Each step reads and writes only `S`, however long the context gets. In K3, each head's `S` is 128×128[^sglang-k3-day0]. `S` has no token-position axis, so a readout mixes every earlier write. Plain linear attention also only adds: if the same key direction gets `1` and later `4`, the next read returns `1+4`[^sglang-k3-day0].

## DeltaNet: error-directed rewrites

DeltaNet first reads what the state already predicts for the current key, `r_old = S_{t-1}ᵀ k_t`. It then writes only the difference between the target and that prediction[^sglang-k3-day0]:

```text
S_t = S_{t-1} + β_t · k_t (v_t − r_old)ᵀ
readout along a unit k_t afterwards: (1 − β_t)·r_old + β_t·v_t
```

`β_t` is a scalar gate produced on the fly. At `β_t = 1` the old association is fully replaced, smaller values keep more of the old value, and `β_t = 0` leaves it unchanged. The source's example is a fact that changes mid-context ("lives in Beijing", later "moved to Shanghai"). Plain accumulation would answer with a blend of both. The delta rule can overwrite the old answer[^sglang-k3-day0].

## Crosstalk in a fixed-size state

If `S = k_a v_aᵀ + k_b v_bᵀ`, reading with `q = k_a` returns `v_a + cos θ · v_b`, where `θ` is the angle between the two keys. In general, writes interfere through the Gram matrix `G_ij = k_iᵀk_j`. The readout is free of crosstalk only when all keys are pairwise orthogonal, and `ℝ^{d_k}` holds at most `d_k` orthogonal directions. Once a fixed state stores more associations than that, crosstalk cannot be eliminated, only managed[^sglang-k3-day0]. The delta rule fixes rewrites along the same or a nearby key, but it does not clear out unrelated old signal. The effect grows with context length, which matters at 1M tokens[^sglang-k3-day0].

## KDA: channel-wise decay before the delta write

In K3, each of the 96 KDA heads projects the 7168-d hidden state down to 128 dimensions. A *channel* is one dimension of that per-head key space, and key channel `j` controls writes into row `j` of `S`[^sglang-k3-day0]. KDA adds a per-token, per-head vector gate `α_t ∈ (0,1)^{d_k}`, computed from the current hidden state[^sglang-k3-day0]:

```text
S_t = (I − β_t k_t k_tᵀ) · Diag(α_t) · S_{t-1} + β_t k_t v_tᵀ
```

- **Two steps per update.** First the gate decays the state: `S̃ = Diag(α_t) S_{t-1}`. Then the delta rule rewrites along the full key: `S_t = S̃ + β_t k_t (v_t − S̃ᵀk_t)ᵀ`[^sglang-k3-day0].
- **What the gate does and doesn't do.** `Diag(α_t)` scales row `j` by `α_t[j]`, so every earlier contribution in that row decays together. The gate does not separate individual associations and does not rotate keys toward orthogonality[^sglang-k3-day0].
- **Inputs (from the module diagram).** `q` and `k` go through a linear projection, short convolution, a nonlinearity, and L2 normalization. `v` goes through the same projection, convolution, and nonlinearity, but without L2 normalization. `α` and `β` come from sigmoid-activated projections. The output passes through a norm and is multiplied by a sigmoid output gate before the final linear projection (**Observed** in the architecture SVG)[^sglang-k3-day0].

## Position without RoPE

Unrolling the recurrence gives `S_t = Σ_{s≤t} [Π_{u=s+1..t} (I − β_u k_u k_uᵀ) Diag(α_u)] β_s k_s v_sᵀ`. An earlier write passes through more gates and rewrites before it reaches step `t`, so decay builds up with distance. Order and distance are therefore encoded implicitly, through learned decay that depends on the input. K3 uses no explicit position encoding (NoPE) anywhere, and its MLA layers run global attention without position encoding[^sglang-k3-day0]. The tech-report view of the same choice, including direct extrapolation to 1M without RoPE rescaling, is in [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md).

## K3 changes relative to Kimi Linear

- **Lower-bounded decay.** A scaled sigmoid with `g_min = −5` bounds the log-decay of `α`, so every step keeps more than `e^{-5} ≈ 6.7×10⁻³` of the state. Chunkwise computation rescales keys by the reciprocal of the cumulative decay. Bounding that range lets both diagonal and off-diagonal tiles run as dense Tensor Core matmuls. That removes the position-pair diagonal path Kimi Linear needed[^sglang-k3-day0].
- **Full-rank output gate.** The output gate changes from Kimi Linear's low-rank form to an input-dependent full-rank projection[^sglang-k3-day0].

## Serving consequences

These follow from the mechanism and are spelled out for K3 in [SGLang Kimi K3 Day-0 Inference](sglang-kimi-k3-inference.md)[^sglang-k3-day0]:

| Property | Softmax/MLA KV | KDA state |
| --- | --- | --- |
| Growth | Appends per token | Fixed size per request (~54MB per GPU for K3 at TP8) |
| Decode cost per step | Reads all prior tokens | `O(1)`: reads and writes only `S` |
| Prefix sharing | Shared KV is append-only and safe to share | In-place overwrite makes sharing unsafe; needs read-only checkpoints plus copy-on-write |
| Context parallelism | Can be striped by token position (DCP) | No token axis; stays sharded by TP/head |

Because of the crosstalk limit, KDA cannot replace global attention in every layer. K3 keeps one gated MLA layer for every three KDA layers to retain full-context interaction (**Synthesis** from the source's architecture rationale)[^sglang-k3-day0].

## Relationships

- Used by [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md): the canonical tech-report description of the 3:1 KDA/Gated-MLA hybrid, chunkwise form, and lower-bounded decay.
- Related to [SGLang Kimi K3 Day-0 Inference](sglang-kimi-k3-inference.md): how SGLang caches, pools, and parallelizes KDA state next to MLA KV.
- Related to [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md): FlashKDA kernels, KDA context parallelism, and replay-based speculative verification built on this recurrence.
- Related to [SGLang Unified Radix Cache](sglang-unified-radix-cache.md): the `MAMBA` checkpoint component that SGLang uses for recurrent states such as KDA.
- Related to [Qwen3.8-2.4T-A95B Architecture](qwen3.8-2.4t-a95b-architecture.md): a 3:1 hybrid of Gated DeltaNet and full attention with a fixed-size FP32 recurrent state. Both are delta-rule linear attention served through the same checkpoint-style cache (**Synthesis**; this source does not compare gate granularity with GDN).

## Coverage limits

- The source's MHA, linear-attention, DeltaNet, KDA, and crosstalk diagrams are interactive. Only their initial (t=0) state is captured, so step-by-step values are not available. The 2D `k_a`/`k_b` teaching slice is illustrative, and its numbers are not model parameters.
- The chunkwise (UT-transform) algorithm and the exact gate parameterization are not derived in this source. See the tech-report page. The Kimi Linear paper (arXiv 2510.26692), linked under "Further reading", was not inspected.

[^sglang-k3-day0]: Kimi K3: Architecture and SGLang Day-0 Support (SGLang Team, sglang.io) — `../raw/kimi-k3-day0-support/index.md`. Locators: "Attention mechanisms in detail: classic MHA" (score/normalize/aggregate, `O(N²)`); "…: linear attention" (`S = Σ k vᵀ`, 128×128 per head); "…: DeltaNet" (`r_old`, β semantics, Beijing/Shanghai example) and its "Math details" (Gram matrix, `d_k` bound); "…: KDA" (96 heads × 128-d channels, `Diag(α)` update, unrolled recurrence, `g_min = −5`, full-rank output gate, NoPE); architecture SVG KDA-module drawing and `<title>` elements; "SGLang's day-0 adaptations" state table, "RadixAttention: prefix caching for KDA state", and "Decode context parallelism (DCP)" for the serving consequences.
