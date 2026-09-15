---
type: Concept
title: Kimi K3 Architecture and Pre-training
description: 2.8T/104B hybrid KDA-MLA MoE with AttnRes, Stable LatentMoE, MoonViT-V2, and 2.5x scaling efficiency over Kimi K2.
tags: [kimi-k3, moonshot-ai, mixture-of-experts, kimi-delta-attention, mla, attention-residuals, latent-moe, situ-glu, quantile-balancing, moonvit, muon, long-context, pre-training]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: k3-main
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: Kimi K3 Technical Report — main
  - id: k3-intro
    resource: ../raw/arXiv-2607.24653v1/1-introduction.tex
    title: Kimi K3 Technical Report — introduction
  - id: k3-arch
    resource: ../raw/arXiv-2607.24653v1/2-model-architecture.tex
    title: Kimi K3 Technical Report — model architecture
  - id: k3-pretrain
    resource: ../raw/arXiv-2607.24653v1/3-pre-training.tex
    title: Kimi K3 Technical Report — pre-training
---

Kimi K3 is a 2.8T-parameter Mixture-of-Experts model with 104B activated parameters, native vision, and 1M-token context, built to scale information flow across sequence, depth, and width via hybrid KDA-MLA attention, Attention Residuals, and Stable LatentMoE for about 2.5x overall scaling efficiency over Kimi K2[^k3-main][^k3-intro][^k3-pretrain].

## Scale and K2 comparison

Kimi K2 to K3 architectural deltas[^k3-pretrain]:

| Item | Kimi K2 | Kimi K3 |
| --- | --- | --- |
| Layers | 61 | 93 (+52%) |
| Total / active params | 1.04T / 32.6B | 2.78T / 104.2B (+167% / +220%) |
| Hidden dim / vocab | 7168 / 160K | 7168 / 160K (same) |
| Latent MoE dim | — | 3584 (0.5x) |
| Expert hidden / routed / active / shared | 2048 / 384 / 8 / 1 | 3072 / 896 / 16 / 2 |
| Attention heads | 64 | 96 |
| Attention | MLA (61 layers) | Hybrid: 69 KDA + 24 MLA |
| Activation | SwiGLU | SiTU-GLU |
| Training context | 128K | 1M (8x) |
| MTP layers | 1 | 1 |
| ViT | — | 401M, 27 layers, patch 14, 12 heads |

Each backbone block holds 3 KDA layers plus 1 Gated MLA layer (3:1), plus one final Gated MLA layer so output always uses global attention[^k3-arch].

## Hybrid attention

### Kimi Delta Attention

KDA extends delta-rule recurrence with a channel-wise forget gate[^k3-arch]:

```text
S_t = (I - beta_t k_t k_t^T) Diag(alpha_t) S_{t-1} + beta_t k_t v_t^T
o_t = S_t^T q_t
```

- Q/K use ShortConv plus Swish plus L2Norm; V uses ShortConv plus Swish; `beta` is sigmoid; decay logits come from low-rank projection plus head bias[^k3-arch].
- Chunkwise form is recurrent across chunks and parallel within chunks, with inter-chunk term from incoming state and intra-chunk causal term[^k3-arch].
- Kimi Linear used unbounded negative-Softplus log-decay; K3 uses scaled sigmoid `g = g_min * Sigmoid(e^A z)` with `g_min=-5`, so `alpha in (e^-5,1)` and a 16-token tile reciprocal stays below `e^80` within BF16, letting diagonal and off-diagonal tiles all use dense Tensor Core GEMMs[^k3-arch].
- Output gate changes from low-rank to input-dependent full-rank: sigmoid-gated RMSNormed recurrent output through `W_o`[^k3-arch].

### Gated MLA

MLA compresses KV to latent `c_t = W_c x_t`, caches the latent, and reconstructs content keys/values during attention[^k3-arch].

- K3 applies NoPE to all MLA layers; intervening KDA supplies position-sensitive and recency-aware mixing while MLA supplies unrestricted global content interaction, avoiding RoPE retuning or YaRN when extending context[^k3-arch].
- Adds full-rank input-dependent channel-wise output gate matching KDA[^k3-arch].
- Keeps attention output in FP32 during training to correct biased rounding error; redesigned kernel overlaps the larger output tile with KV staging buffers instead of the query tile for deeper KV pipeline and higher throughput[^k3-arch].

## Attention Residuals

Standard residuals compress all prior depth into one state; AttnRes lets each layer selectively retrieve from all preceding layers[^k3-arch].

- Full form: learnable pseudo-query `q_l = w_l`, keys/values from embedding plus prior layer outputs, softmax kernel `exp(q^T RMSNorm(k))`, weighted sum over depth; `O(L^2 d)` arithmetic is affordable for `L<100` but `O(Ld)` memory and pipeline communication for retaining layer outputs[^k3-arch].
- Block form partitions `L` layers into `N` blocks, sums each block to one representation, attends over `N` block representations plus intra-block partial sum; memory/communication drops to `O(Nd)` and online-softmax merging reduces inference cost[^k3-arch].
- `N≈8` recovers most benefit; K3 uses 8 blocks of 12 layers plus partial final block and embedding source, i.e. 9 total sources[^k3-arch].

## Stable LatentMoE

LatentMoE separates full model width from routed-expert width so 896 routed experts with 16 active per token (sparsity 56) stay affordable; shared experts keep full-width common path while routed experts operate in compact latent width `l`[^k3-arch]:

```text
u = sum_{i in Top_k} p_i E_i_routed(W_down x)
y = sum_{j=1..Ns} E_j_shared(x) + W_up RMSNorm(u), Ns=2
```

Extreme sparsity amplifies activation explosion (nearly four chained matmuls in routed branch at 2.8T scale) and load-balancing stress near 1K experts; Stable LatentMoE adds RMSNorm before up-projection, SiTU-GLU, and Quantile Balancing[^k3-arch].

### SiTU-GLU

SwiGLU is unbounded in both factors, risking outliers and low-precision overflow; original GLU sigmoid gate loses Swish-like linear positive regime[^k3-arch].

```text
SiTU-GLU(x) = [beta1 tanh(W_g x / beta1) * Sigmoid(W_g x)] * [beta2 tanh(W_u x / beta2)]
```

- K3 sets `beta1=4`, `beta2=25`; near origin `beta tanh(z/beta)=z+O(z^3/beta^2)`, so first-order match to SwiGLU and pointwise recovery as betas go to infinity; output bound `||.||_inf <= beta1*beta2 = 100`; smooth cap preserves nonzero gradients unlike hard clamping[^k3-arch].

### Quantile Balancing

Auxiliary-loss-free routing adds bias `b` only to Top-k selection, not mixture weights: `T_i = argtop_k(s_i+b)`, `p` normalized from raw sigmoid scores `s_i`[^k3-arch].

- Fixed-step sign update `b+=gamma sign(mean-load)` trades slow adaptation against oscillation and struggles at 896 experts[^k3-arch].
- QB derives next bias from Top-(k+1) cutoff `alpha_i`: count routed to expert `j` under candidate bias is monotone in threshold, so setting count to target `q=mk/n` makes `-b_j` the `(q+1)`-th largest margin `s_{i,j}-alpha_i`, i.e. `(1-k/n)`-quantile; mean-center to remove irrelevant common offset; causal (next-step only); frozen at inference[^k3-arch].
- At scale uses histogram estimator: bin required bias `r=alpha-s` over `[b_min-1,b_max+1]` with `B=1000`, per-rank scatter-add, one integer all-reduce of `nB` values, linear interpolation in selected bin; error bounded by bin width (few 1e-3), <1% of gathering raw margins, invariant to sharding, optionally EMA-smoothed across steps[^k3-arch].
- Derivation is exact coordinate minimization of balanced-assignment LP dual; SignSGD on same dual recovers old sign update, explaining why QB needs no LR-like hyperparameter and equilibrates in few steps[^k3-arch].

## Native vision

K3 is natively multimodal with text, images, and video in one context and no post-hoc alignment, enabling vision-in-the-loop loops such as write-code, inspect screenshot/frame, refine UI/graphics/video[^k3-arch][^k3-intro].

- MoonViT-V2 is trained from scratch with next-token prediction, departing from SigLIP-initialized MoonViT-3D; from-scratch run shows lower gradient norms with fewer spikes and matches SigLIP-init on vision evals, suggesting contrastive init is unnecessary at scale and representations are shaped directly by LM objective[^k3-arch].
- 27-layer ~0.4B ViT with RMSNorm and no biases; shared image/video parameters, factorized spatial plus temporal attention, temporal pooling, 2x2 pixel-shuffle 4x token reduction, inputs up to 3584x3584 affordable in 1M context[^k3-arch].

## Per-Head Muon

K3 uses Muon for matrix parameters; attention QKV momentum is partitioned along head dim and Newton-Schulz orthogonalized per head rather than on full matrix, equalizing update scale across heads, improving stability at scale, and slightly reducing optimizer overhead on tall per-head blocks[^k3-arch].

## Pre-training data and recipe

- Four text domains (Web, Code, Mathematics, Knowledge) plus large vision corpus (captions, interleaved image-text, OCR, perception, video, visual coding); rule plus classifier plus dedup filtering, domain rates by small-model ablations; knowledge/math rephrased with style/perspective-diverse prompts, chunk-wise autoregressive generation, fidelity verification[^k3-pretrain].
- Vision follows K2.5 taxonomy with open plus in-house filtering/synthesis/dedup; coordinate supervision in absolute and normalized [0,1]; scaled programmatic multimodal code-plus-render data across SVG, 3D, Webpage, Game, CAD[^k3-pretrain].
- Scaling-law study retunes batch size, LR, tokens-per-parameter, and shape; held-out OOD curves give ~2.5x efficiency over K2; independent per-schedule search favors cosine decay over Warmup Stable Decay under respective optima[^k3-pretrain].
- Native multimodal joint optimization from start with single next-token objective; Per-Head Muon plus K2 weight clipping plus QB; cosine schedule with 1% linear warmup; weight decay 0.1; 8K start extended to 64K in later pretraining phase[^k3-pretrain].

## Long-context extension

- NoPE: position comes implicitly from KDA gating/decay, so direct extrapolation to 1M without RoPE rescaling or interpolation[^k3-pretrain].
- Long documents/videos cleaned with exact/fuzzy dedup, perceptual frame hashing, heuristic/classifier filtering, structural validation; genuinely long coherent sources upsampled; synthetic permuted/concatenated multimodal documents and subtasks solvable only by attending across full 1M prevent local-pattern degeneration[^k3-pretrain].
- Progressive curriculum 8K to 64K in pretraining and 256K to 1M in cooldown concentrates costly long-sequence compute in small fraction of budget; KDA sequence partitioning makes million-token training tractable[^k3-pretrain].

## Relationships

- Uses [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md) — architecture defined here; FlashKDA, intra-device CP, and KDA Context Parallelism that make it trainable are compiled there.
- Related to [Kimi K3 Local Deployment](kimi-k3.md) — same 2.8T/104B Moonshot model; deployment, GGUF, and sampling guidance live there.
- Related to [Kimi K3 DSpark Speculator](kimi-k3-dspark.md) — server-side speculative path for the same base model.

## Coverage limits

- Equations are synthesis summaries; full UT-transform derivation, QB histogram error bound, and SiTU limiting-case proofs are in source and appendix and not reproduced in full.
- Scaling-law curves, ViT grad-norm figure, and KDA lower-bound figure were read as described in text; pixel-level figure values were not independently measured.
- `references.bib` was declared ignore in `00README.json` and not compiled.

[^k3-main]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/main.tex`, 2.8T/104B MoE, native vision, 1M context, KDA plus AttnRes plus Stable LatentMoE, ~2.5x over Kimi 2, weights at `https://huggingface.co/moonshotai/Kimi-K3`.
[^k3-intro]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/1-introduction.tex`, dual-axis scaling thesis, 2.8T/104B/1M identity, KDA plus AttnRes plus 896-expert Stable LatentMoE, multi-effort RL plus MOPD preview, infra preview, open-frontier claim.
[^k3-arch]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/2-model-architecture.tex`, 3:1 KDA/Gated-MLA hybrid plus final MLA, KDA recurrence/chunkwise/lower-bounded-decay/full-rank gate, Gated MLA NoPE plus FP32 output, full/block AttnRes with 8x12 layout, LatentMoE equation with Ns=2 plus RMSNorm plus SiTU-GLU betas plus QB quantile/histogram, MoonViT-V2 from-scratch design, Per-Head Muon.
[^k3-pretrain]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/3-pre-training.tex`, four text domains plus vision taxonomy, filtering/rephrasing/coordinate/programmatic data, scaling-law 2.5x plus cosine-over-WSD finding, K2/K3 comparison table, native multimodal recipe with Per-Head Muon/clipping/QB/cosine/0.1 decay/8K-to-64K, NoPE extrapolation plus cleaning/upsampling/synthetic 1M data plus 8K-64K-256K-1M curriculum.
