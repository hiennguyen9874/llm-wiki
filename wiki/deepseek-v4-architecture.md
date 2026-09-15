---
type: Concept
title: DeepSeek-V4 Architecture
description: 1.6T Pro and 284B Flash MoE with hybrid CSA plus HCA sparse attention, manifold-constrained hyper-connections, Muon, and 1M context at reduced FLOPs and KV.
tags: [deepseek-v4, moe, sparse-attention, mhc, muon, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v4-report
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: 'DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence'
---

DeepSeek-V4 is a preview MoE series with DeepSeek-V4-Pro at 1.6T total / 49B activated and DeepSeek-V4-Flash at 284B total / 13B activated, both supporting 1M-token context through hybrid Compressed Sparse Attention plus Heavily Compressed Attention, manifold-constrained hyper-connections, and the Muon optimizer[^v4-report].

## Model snapshot

Pro uses 61 layers with hidden size 7168; Flash uses 43 layers with hidden size 4096[^v4-report]. Both keep Transformer plus 1-depth Multi-Token Prediction from DeepSeek-V3, use 128K vocabulary with added context-construction specials, and inherit token-splitting and fill-in-middle handling[^v4-report].

Flash uses pure sliding-window attention in the first two layers and interleaved CSA/HCA after; Pro uses HCA in the first two layers and interleaved CSA/HCA after[^v4-report]. CSA compression rate `m=4`; HCA compression rate `m'=128`; sliding-window branch `n_win=128` in both[^v4-report].

CSA sparse top-k is 512 for Flash and 1024 for Pro; both use 64 indexer query heads of dimension 128, query heads 64 for Flash and 128 for Pro with head dimension 512 and query compression dimension 1024 for Flash and 1536 for Pro; grouped output projection uses 8 groups for Flash and 16 for Pro with intermediate dimension 1024[^v4-report]. mHC expansion `n_hc=4` with 20 Sinkhorn iterations in both[^v4-report].

## MoE and MTP deltas from V3

Both retain DeepSeekMoE with auxiliary-loss-free balancing plus a small sequence-wise balance loss against within-sequence extreme imbalance[^v4-report]. Affinity activation changes from Sigmoid to `Sqrt(Softplus)`; Pro removes the cap on routing target nodes with a redesigned parallelism strategy[^v4-report].

All blocks use MoE: Flash has 1 shared plus 256 routed experts of intermediate size 2048 with 6 active; Pro has 1 shared plus 384 routed experts of intermediate size 3072 with 6 active[^v4-report]. The first 3 MoE layers in both use hash routing keyed by input token ID[^v4-report].

MTP configuration is unchanged from DeepSeek-V3[^v4-report].

## Manifold-constrained hyper-connections

mHC widens the residual stream from `R^d` to `R^{n_hc x d}` with input map `A_l`, residual map `B_l`, and output map `C_l`, keeping inner-layer width at `d` for a low-cost complementary scaling axis[^v4-report].

Standard hyper-connections are numerically unstable when deeply stacked; mHC constrains `B_l` to doubly stochastic matrices via the Birkhoff polytope, bounding spectral norm by 1 for non-expansive forward and backward passes with closure under multiplication, while `A_l` and `C_l` are Sigmoid-bounded to non-negative ranges to avoid cancellation[^v4-report].

Parameters split into input-dependent dynamic and static parts from RMS-normalized flattened input with small-initialized gating, then `A_l=sigmoid(tilde A)`, `C_l=2*sigmoid(tilde C)`, and `B_l` from Sinkhorn projection of `exp(tilde B)` with 20 row/column normalizations[^v4-report].

## Compressed Sparse Attention

CSA first builds two KV series `C^a/C^b` and weights `Z^a/Z^b` from hidden states, then compresses each `m` entries with learnable positional biases over an overlapped `2m` window into one entry, cutting sequence length to `1/m`[^v4-report].

Indexer keys reuse the same compression path; queries use a shared low-rank latent `c_t^Q` for both indexer and attention queries, with head weights `w^I` and ReLU-scored dot products selecting top-k compressed entries per query under strict causality over preceding blocks[^v4-report].

Core attention is shared-KV MQA where each selected compressed entry serves as both key and value; grouped output projection splits `n_h` heads into `g` groups through narrow intermediates before the final projection to curb the `c*n_h` projection cost[^v4-report].

## Heavily Compressed Attention

HCA uses the same compression idea with larger non-overlapped rate `m'=128`, cutting length to `1/m'`, and skips sparse selection by attending densely over all compressed entries[^v4-report]. It reuses shared-KV MQA and grouped output projection with the same low-rank query construction[^v4-report].

## Shared attention details

Both apply RMSNorm to queries and single-head compressed KV before core attention, partial RoPE on the last 64 dimensions of queries and KV, and compensating RoPE with position `-i` on core outputs so weighted KV sums keep relative rather than absolute position[^v4-report].

Both add a sliding-window branch over the most recent `n_win` uncompressed tokens to cover intra-block causality gaps and local dependence, plus per-head learnable attention-sink logits added to the softmax denominator so total attention mass can fall below 1[^v4-report].

## Efficiency and optimizer

KV uses BF16 for RoPE dimensions and FP8 elsewhere, nearly halving storage versus pure BF16; indexer QK runs in FP4 and index scores quantize FP32 to BF16 for 2x top-k speed at 99.7% recall; a smaller top-k than V3.2 helps short/medium text[^v4-report]. Against a BF16 GQA8 baseline with head dimension 128, V4 KV falls to about 2% at 1M context; Pro needs about 27% of V3.2 single-token FLOPs and 10% of its KV at 1M[^v4-report].

Muon updates most parameters with momentum 0.95, decay 0.1, Nesterov trick, and 0.18 RMS rescaling to reuse AdamW rates; embeddings, prediction head, mHC statics/gates, and RMSNorm weights stay on AdamW[^v4-report]. Orthogonalization uses 10 hybrid Newton-Schulz steps: 8 fast-convergence steps then 2 stabilizing steps; QK-Clip is omitted because query/KV RMSNorm already bounds logits[^v4-report].

## Relationships

- Uses [DeepSeek-V4 Systems and Infrastructure](deepseek-v4-systems.md) — training and inference realization of mHC, CSA/HCA, and Muon described here.
- Uses [DeepSeek-V4 Training and Evaluation](deepseek-v4-training-evaluation.md) — data, schedule, and benchmark context for these model sizes.
- Related to [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md) — successor that removes CSA overlapping entries and absolute positions and reuses main KV for indexer K.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — serving-side companion with ShadowRadix, MTP, HiSparse, and fused kernels for this hybrid layout.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — training-side companion with Megatron rebuild and stability controls for mHC plus compressed attention.

## Coverage limits

- Figures under `raw/arXiv-2606.19348v1/figures/` were not pixel-verified; structural claims follow prose, equations, and captions[^v4-report].
- Open-source inference implementation link and `main.bib` citations were not inspected[^v4-report].

[^v4-report]: DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence — `../raw/arXiv-2606.19348v1/main.tex`, covering Pro/Flash sizes, MoE/MTP deltas, mHC formulation, CSA/HCA compression plus indexer/MQA/grouped projection, RoPE/norm/SWA/sink details, KV/FLOP efficiency, and Muon configuration.
