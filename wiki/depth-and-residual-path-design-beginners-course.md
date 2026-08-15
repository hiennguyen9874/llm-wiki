---
type: Synthesis
title: "Depth and residual-path design — khóa học cho người mới"
description: A beginner-first course on residual information flow across model depth, Attention Residuals depth retrieval, and manifold-constrained multi-channel residual mixing, with PyTorch toy implementations and checks.
tags: [learning-roadmap, residual-connections, attention-residuals, hyper-connections, depth, pytorch]
status: stable
created: 2026-08-15
generated:
  by: llm-wiki-agent/1
  at: 2026-08-15T11:18:58+07:00
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: Attention Residuals
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# Depth and residual-path design — khóa học cho người mới

`Self-attention` trả lời câu hỏi **token nào** trong sequence nên trao đổi thông tin; `residual path` trả lời câu hỏi **biểu diễn nào từ các layer trước** sẽ tiếp tục đi qua model. Standard residual giữ mọi update với hệ số cố định; `Attention Residuals` (`AttnRes`) biến việc chọn thông tin theo **depth** thành `softmax retrieval`; `manifold-constrained Hyper-Connections` (`mHC`) giữ nhiều `residual channels` và ràng buộc cách trộn chúng. Đây là ba cách thiết kế information flow theo depth, không phải ba cách thay thế cho causal token attention.[^vaswani-transformer-2017][^attnres-2026][^deepseek-v4-2026]

> [!success] Mục tiêu học
> Sau bài này, bạn có thể (1) phân biệt `sequence position` với `model depth`; (2) triển khai và unroll standard residual; (3) giải thích Full/Block `AttnRes` và accounting state của chúng; (4) hiểu `mHC` là multi-channel residual mixing có constraint, không phải attention; và (5) kiểm tra shape, normalization, causal semantics của một toy implementation.

Bài này là course tổng hợp cho Stage 8.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Code chỉ minh họa mechanism và **không** reproduce training recipe, distributed kernels, hoặc reported quality của các model lớn.

## 0. Prerequisites và notation

Bạn nên đã hiểu một `decoder-only Transformer block`: causal self-attention trao đổi thông tin theo token position, còn `FFN` biến đổi từng position độc lập. Xem [Attention: beginner's guide for causal language models](attention-beginner-guide.md) và [Modern decoder-block recipe](modern-decoder-block-recipe-beginners-course.md) nếu các thành phần này còn mới.

| Ký hiệu | Nghĩa |
| --- | --- |
| `B`, `T`, `D` | `batch_size`, `sequence_length`, `hidden_size` |
| $x$ hoặc $h_l$ | hidden representation ở depth/layer $l$; khi có batch, shape là `(B, T, D)` |
| $F_l$ | transformation của layer $l$, ví dụ attention hoặc FFN branch |
| $v_l$ | update do layer tạo ra, thường $F_l(h_l)$ |
| $L$ | tổng số layers; **không** phải sequence length $T$ |
| $N$ | số depth blocks trong Block `AttnRes` |
| $n_{hc}$ | số `residual channels` trong `mHC` |

## 1. Hai trục retrieval không được nhầm lẫn

Một tensor `(B, T, D)` có ít nhất hai trục kiến trúc quan trọng:

```text
sequence axis (trong một layer)             depth axis (cho cùng token position)

x[0]  x[1]  x[2] ... x[T-1]                 embedding → layer 1 → layer 2 → ... → layer L
  │      │      │                                         │          │              │
  └── causal self-attention ──┘                          v0         v1             vL-1
             chọn token sources                       standard / AttnRes / mHC quyết định
                                                       cách đi và trộn thông tin theo depth
```

- `Causal self-attention`: query tại position $t$ chỉ được đọc allowed positions, thường $j\leq t$. Nó chọn **token sources**.
- `AttnRes`: tại một depth, nó chọn representation từ embedding hoặc earlier layers của **cùng token position**. Nó chọn **depth sources**.
- `mHC`: không tạo token lookup hay depth-softmax. Nó lưu một state gồm nhiều channels và học cách đọc, carry, ghi update qua channels.

Vì thế, thay `residual path` **không tự động** thay causal mask, KV cache, positional encoding, MoE router, hay token-access pattern. Original Transformer đã tách attention/FFN khỏi residual + normalization như các vai trò riêng.[^vaswani-transformer-2017]

> [!warning] Causal safety
> Một residual mechanism chỉ causal nếu mọi $F_l$ bên trong nó vẫn causal. Trộn layer outputs ở cùng position không cho phép đọc future token; nhưng một buggy attention branch vẫn có thể leak future tokens dù residual code hoàn toàn đúng.

## 2. Baseline: standard residual connection

### 2.1 Một update theo depth

Ở dạng đơn giản, residual update là:

$$
h_{l+1}=h_l+F_l(h_l).
$$

Nó có nghĩa: layer không phải xây lại representation từ đầu; layer chỉ đề xuất update và identity path chuyển $h_l$ sang layer tiếp theo. Với `pre-norm` decoder hiện đại, branch thường là:

$$
h_{l+1}=h_l+F_l(\operatorname{Norm}(h_l)).
$$

Trong original Transformer, mỗi sublayer dùng `post-norm`, $\operatorname{LayerNorm}(x+\operatorname{Sublayer}(x))$. Hai công thức không thể hoán đổi cho một checkpoint đã train chỉ bằng đổi vị trí `Norm`.[^vaswani-transformer-2017]

### 2.2 Unroll: residual là fixed accumulation

Đặt $v_0=h_0$ là embedding representation và $v_{i+1}=F_i(h_i)$. Bỏ qua placement của normalization để nhìn information path, ta có:

$$
h_l = v_0 + v_1 + \cdots + v_{l-1} = \sum_{i=0}^{l-1} v_i.
$$

Mọi earlier update có coefficient bằng 1. Đây là điểm mạnh của residual: identity gradient path rõ ràng. Đồng thời nó không có cơ chế để layer $l$ nói rằng “lần này hãy ưu tiên layer 3 hơn layer 27”. AttnRes report mô tả fixed accumulation của `PreNorm` là có thể làm magnitude tăng theo depth và làm contribution của mỗi layer khó phân biệt; đó là motivation của proposal, không phải định lý rằng mọi standard residual đều thất bại.[^attnres-2026]

### 2.3 Minimal PyTorch baseline

```python
import torch
import torch.nn as nn

class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x):
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.weight

class PreNormResidual(nn.Module):
    def __init__(self, d, branch):
        super().__init__()
        self.norm = RMSNorm(d)
        self.branch = branch  # must preserve (B, T, D)

    def forward(self, h):
        return h + self.branch(self.norm(h))

# Toy branch only: a real decoder block would use causal attention or an FFN.
torch.manual_seed(0)
h = torch.randn(2, 5, 8)             # (B, T, D)
layer = PreNormResidual(8, nn.Linear(8, 8))
assert layer(h).shape == h.shape
```

`nn.Linear` here operates independently at each token. It cannot validate causal behavior; test causal masking only with an actual attention branch.

## 3. Full `Attention Residuals`: attention over depth

### 3.1 Sources, query, score, mixture

At target layer $l$, Full `AttnRes` retains each earlier source $v_i$. A learned per-layer `pseudo-query` $w_l\in\mathbb{R}^D$ scores normalized sources:

$$
s_{i\to l}=w_l^\top\operatorname{RMSNorm}(v_i),\qquad
\alpha_{i\to l}=\frac{\exp(s_{i\to l})}{\sum_{j=0}^{l-1}\exp(s_{j\to l})},
$$

$$
h_l=\sum_{i=0}^{l-1}\alpha_{i\to l}v_i.
$$

`RMSNorm` in the score prevents a source with a large magnitude from winning only because it is large. Since $\alpha$ is a `softmax`, each $\alpha_{i\to l}\ge0$ and sources sum to one for **each batch item and token position**. The same learned $w_l$ is applied to all positions, but each position has different $v_i$, hence different weights.[^attnres-2026]

```text
for one token position t at target layer l:

embedding v0 ─ RMSNorm ─ dot(w_l) ─ score ─┐
layer update v1 ─ RMSNorm ─ dot(w_l) ─ score ─┼─ softmax over depth ─ weighted sum → h_l[t]
...                                           │
layer update v(l-1) ─ RMSNorm ─ dot(w_l) ─ score ─┘
```

**Important difference from token attention:** this toy equation has a learned `pseudo-query`, keys/values from depth, and no $T\times T$ score matrix. It does not replace Q/K/V token attention inside $F_l$.

### 3.2 Why zero initialization matters

The source initializes $w_l=0$. Then every score is zero, so Full `AttnRes` begins as an **equal-weight average**, not as the standard residual sum. This symmetric start was reported to prevent early training volatility. Do not write a test expecting the initial mechanism to exactly equal $\sum_i v_i$; it should equal $\operatorname{mean}_i(v_i)$ under this formula.[^attnres-2026]

### 3.3 Runnable toy depth mixer

This module accepts a Python list of same-shape depth sources. It deliberately excludes a full Transformer branch so the shapes and the `softmax(dim=depth)` are visible.

```python
class FullDepthAttention(nn.Module):
    """Toy Full AttnRes mixer for one target layer, not a full model."""
    def __init__(self, d):
        super().__init__()
        self.score_norm = RMSNorm(d)
        self.pseudo_query = nn.Parameter(torch.zeros(d))

    def forward(self, sources, return_weights=False):
        # each source: (B, T, D); source axis becomes dimension 2
        assert len(sources) > 0
        V = torch.stack(sources, dim=2)       # (B, T, S, D)
        K = self.score_norm(V)                # RMSNorm acts on D
        scores = (K * self.pseudo_query).sum(dim=-1)  # (B, T, S)
        weights = scores.softmax(dim=-1)      # normalize over depth, never tokens
        mixed = (weights.unsqueeze(-1) * V).sum(dim=2)  # (B, T, D)
        return (mixed, weights) if return_weights else mixed

B, T, D, S = 2, 4, 8, 3
torch.manual_seed(7)
sources = [torch.randn(B, T, D) for _ in range(S)]
mixer = FullDepthAttention(D)
out, weights = mixer(sources, return_weights=True)

assert out.shape == (B, T, D)
assert weights.shape == (B, T, S)
assert torch.allclose(weights.sum(dim=-1), torch.ones(B, T))
# zero pseudo-query => uniform depth weights => arithmetic mean
assert torch.allclose(out, torch.stack(sources, dim=2).mean(dim=2), atol=1e-6)
```

> [!tip] Debugging rule
> `softmax(dim=-1)` is correct above because last dimension of `scores` is `S`, the number of depth sources. A frequent bug is to stack as `(S, B, T, D)` but still normalize the last dimension, accidentally normalizing over `D`.

### 3.4 Cost accounting: which state grows with what?

For $L$ layers and width $D$, Full `AttnRes` needs $O(LD)$ saved depth sources per token and $O(L^2D)$ depth-mixing arithmetic per token across the stack. $L$ is normally much less than long context length $T$, so arithmetic alone is not necessarily dominant. But activation recomputation and `pipeline parallelism` make retaining and moving all those sources a material systems issue.[^attnres-2026]

| Item | Standard residual | Full `AttnRes` |
| --- | --- | --- |
| Source for next layer | one accumulated state | all earlier $v_i$ |
| Coefficients over depth | fixed 1 | learned, content-dependent `softmax` |
| Saved depth representations | one running state | $O(LD)$ per token |
| Pipeline transfer concern | fixed-size current hidden state | history of earlier depth states |
| Token-addressable KV cache | unchanged by residual choice | unchanged by residual choice |

The $O(LD)$ statement is **per token representation**. A prefill with long sequence $T$ also has a sequence dimension, so actual activation/state accounting must include batch, tokens, precision, sharding, recomputation and pipeline schedule.

## 4. Block `AttnRes`: preserve selective depth retrieval with bounded summaries

Full form offers each earlier layer as a source. Block form partitions $L$ layers into $N$ blocks. Within block $n$, it accumulates layer updates into a summary:

$$
b_n=\sum_{j\in\mathcal{B}_n}F_j(h_j).
$$

For a layer inside block $n$, its depth sources are embedding $b_0$, completed summaries $b_1,\ldots,b_{n-1}$, and—after the first layer—the current block's partial sum $b_n^i$. It uses the same scoring and `softmax` idea as Full `AttnRes`.[^attnres-2026]

```text
block 1: [layer 1 → layer 2 → layer 3] → completed summary b1
block 2: [layer 4 → layer 5 → layer 6] → completed summary b2

at layer 5:
  sources = [embedding b0, completed b1, partial current-block sum b2^1]
  not     = [every individual update v1, v2, v3, v4]
```

This loses individual resolution **inside completed blocks**. In return, it reduces persistent depth representations and cross-pipeline communication from $O(LD)$ to $O(ND)$. Limits are useful sanity checks:

- $N=L$: one layer per block, which recovers the full-source granularity.
- $N=1$: one accumulated block; this collapses toward ordinary residual accumulation while retaining a separate embedding source.

The report's `pseudo-query` is decoupled from sequential layer outputs, allowing queries for a block to be batched; its production approach further uses cross-stage caching and online-softmax steps. The course toy code does not implement those distributed/inference optimizations.[^attnres-2026]

### A state ledger before implementation

Before calling any residual method “efficient”, fill out this table for the exact workload:

| Question | Full `AttnRes` | Block `AttnRes` |
| --- | --- | --- |
| How many depth sources survive? | one per earlier layer | one per completed block plus current partial summary |
| Can completed layer updates be individually selected? | yes | no |
| Persistent depth-state order | $O(LD)$ | $O(ND)$ |
| Does it remove the token KV cache? | no | no |
| Does it remove autoregressive decode order? | no | no |

## 5. `mHC`: multi-channel residual mixing, not depth attention

`Manifold-constrained Hyper-Connections` starts from an expanded residual state:

$$
X_l\in\mathbb{R}^{n_{hc}\times D}
$$

rather than one vector in $\mathbb{R}^D$. The inner Transformer/MoE layer still receives a $D$-wide input. Three mappings choose a channel mixture for layer input ($A_l$), carry/mix existing channels ($B_l$), and write layer output into channels ($C_l$):

$$
X_{l+1}=B_lX_l+C_l\,\mathcal{F}_l(A_lX_l).
$$

For each token, $A_lX_l$ has shape $D$, so expanding residual channels does **not** make the inner attention/FFN width $n_{hc}D$. The residual state and its communication/activation footprint do grow with $n_{hc}$.[^deepseek-v4-2026]

### 5.1 Why the `manifold-constrained` name?

`mHC` constrains $B_l$ to a **doubly stochastic matrix**:

$$
B_l\ge0,\qquad B_l\mathbf{1}=\mathbf{1},\qquad \mathbf{1}^TB_l=\mathbf{1}^T.
$$

The report states this bounds $\lVert B_l\rVert_2\le1$, so this *linear carry/mixing map* is non-expansive; products of such matrices remain doubly stochastic. It also bounds $A_l$ and $C_l$ using `sigmoid`. This is a stability rationale for the constrained residual mapping, **not** a proof that the complete nonlinear network cannot be unstable or that it improves every model.[^deepseek-v4-2026]

Actual `mHC` generates $A_l$, $B_l$, and $C_l$ from both normalized current state and learned static components. It exponentiates raw $B$ scores then applies 20 Sinkhorn–Knopp row/column normalization iterations in the reported configuration. DeepSeek-V4 reports $n_{hc}=4$, but that is a model configuration, not a universal default.[^deepseek-v4-2026]

### 5.2 Small static-map demonstration

The following code is intentionally a **static-map toy**. It demonstrates shapes and the doubly stochastic constraint, but omits the reported input-dependent parameter generator; do not label it an `mHC` reproduction.

```python
class StaticMHCPath(nn.Module):
    """Shape/constraint demo only; production mHC has dynamic A/B/C maps."""
    def __init__(self, d, n_channels=4, sinkhorn_steps=20):
        super().__init__()
        self.n, self.steps = n_channels, sinkhorn_steps
        self.raw_A = nn.Parameter(torch.zeros(n_channels))
        self.raw_B = nn.Parameter(torch.eye(n_channels))
        self.raw_C = nn.Parameter(torch.zeros(n_channels))
        self.branch = nn.Sequential(RMSNorm(d), nn.Linear(d, d))

    def residual_map(self):
        # positive matrix, then alternating column/row normalization
        B = self.raw_B.exp()
        for _ in range(self.steps):
            B = B / B.sum(dim=0, keepdim=True).clamp_min(1e-12)
            B = B / B.sum(dim=1, keepdim=True).clamp_min(1e-12)
        return B

    def forward(self, X):
        # X: (B, T, n_channels, D), retained residual state
        A = self.raw_A.sigmoid()                  # (n_channels,)
        C = 2 * self.raw_C.sigmoid()              # (n_channels,)
        B = self.residual_map()                   # (n_channels, n_channels)

        layer_input = (X * A[None, None, :, None]).sum(dim=2)  # (B,T,D)
        update = self.branch(layer_input)                         # (B,T,D)
        carried = torch.einsum("ij,btjd->btid", B, X)           # (B,T,n,D)
        written = C[None, None, :, None] * update.unsqueeze(2)
        return carried + written

B, T, D, n = 2, 3, 8, 4
path = StaticMHCPath(D, n_channels=n)
X = torch.randn(B, T, n, D)
X_next = path(X)
B_map = path.residual_map().detach()

assert X_next.shape == (B, T, n, D)
assert torch.allclose(B_map.sum(dim=0), torch.ones(n), atol=1e-5)
assert torch.allclose(B_map.sum(dim=1), torch.ones(n), atol=1e-5)
print("largest singular value:", torch.linalg.svdvals(B_map)[0].item())
```

A complete implementation must decide how to initialize expanded state, produce dynamic maps at every layer, efficiently fuse operations, and account for the extra activation/pipeline communication. The V4 report says these overheads require fused kernels, selective recomputation and pipeline-overlap changes; its reported wall-time number is system-specific.[^deepseek-v4-2026]

## 6. So sánh đúng dimension

| Dimension | Standard residual | Full / Block `AttnRes` | `mHC` |
| --- | --- | --- | --- |
| Main change | fixed additive depth path | selective retrieval/mixing over depth sources | carry/read/write among residual channels |
| Source granularity | accumulated state | layer outputs; block summaries in Block form | $n_{hc}$ channels at each depth |
| Uses `softmax` over depth? | no | yes | no; uses constrained matrix mixing |
| Keeps token positions addressable? | depends on attention mechanism, not residual | same | same |
| Extra retained state | baseline residual stream | Full: $O(LD)$; Block: $O(ND)$ per token | expanded state $O(n_{hc}D)$ per token |
| Primary stated motivation | gradient/information highway | avoid uniform depth accumulation; choose useful depth sources | constrain signal propagation while retaining multi-channel mappings |

Do not infer that one row yields a universal quality ordering. The AttnRes paper reports its own matched ablations and systems results; mHC's wiki evidence has no public component-isolated ablation from V4's other simultaneous changes. Consult [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md) and [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) before using results in a model choice.[^attnres-2026][^deepseek-v4-2026]

## 7. A practical learning lab

### Step 1 — Trace a standard stack

Build 4 toy `PreNormResidual` layers. Save each branch output $v_i$ and verify numerically that, if you remove normalization for this controlled experiment, final state equals embedding plus all saved updates. This connects the recurrence to the unrolled sum.

### Step 2 — Replace only the depth aggregator

Feed those saved sources to `FullDepthAttention`. Check:

1. all source tensors have exactly `(B, T, D)`;
2. depth weights sum to 1 on dimension `S` for every `(B, T)`;
3. zero `pseudo_query` gives a mean over sources;
4. changing `pseudo_query` changes depth weights but never changes sequence length or causal mask.

### Step 3 — Simulate a block boundary

With 12 layers and 3 blocks of 4, write down sources at layers 1, 4, 5, and 12. At layer 5, verify the current partial block summary is available but individual layer outputs from completed block 1 are not. This exposes the resolution-versus-state trade-off without training a model.

### Step 4 — Verify an `mHC` constraint

Run the static toy and assert row and column sums of $B$ are one within tolerance. Then deliberately remove one Sinkhorn normalization direction: it may remain row-stochastic or column-stochastic but no longer satisfies the full doubly stochastic contract.

### Step 5 — Preserve causal correctness

If you integrate a residual alternative into a real decoder, run the future-perturbation test: change token $t+1$, then assert logits at positions $\le t$ are unchanged. This test validates causality of the **whole block**, not just the residual mixer.

## 8. Reading Kimi K3 and DeepSeek-V4 without category errors

[Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) uses Block `AttnRes` alongside KDA fixed-state sequence mixing, periodic MLA global token retrieval, and latent MoE. In that composition, `AttnRes` is the **depth retrieval** component; it is not the mechanism that gives K3 global token lookup.[^attnres-2026]

[DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) uses `mHC` together with compressed/sparse attention and MoE. `mHC` addresses residual signal propagation, while attention compression addresses long-context token state/work. A headline result from either whole model cannot isolate the causal effect of only its residual design.[^deepseek-v4-2026]

## 9. Checklist

Before moving on, you should be able to answer **yes** to all of these:

- [ ] I can draw `sequence axis` and `depth axis` and assign token attention versus `AttnRes` to the right axis.
- [ ] I can unroll $h_{l+1}=h_l+F_l(h_l)$ into a sum of depth updates.
- [ ] I know zero-initialized Full `AttnRes` produces a uniform average, not a standard residual sum.
- [ ] I can state what Block `AttnRes` loses: individual selection of sources inside completed blocks.
- [ ] I can state what `mHC` constrains: the residual mixing map $B_l$, not all nonlinear behavior of the network.
- [ ] I will measure state, pipeline communication, and causal correctness rather than calling a residual mechanism “free” or “causal” by name.

## Relationships

- **Expands:** Stage 8.1 of the [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).
- **Uses:** [Attention Residuals](attention-residuals.md) for depth-wise selective aggregation and [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) for constrained multi-channel residual mixing.
- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) as the standard residual baseline.
- **Applied by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) uses Block `AttnRes` as a depth-retrieval component.

## Evidence limits

The Full/Block `AttnRes` mechanism and system claims come from its primary technical report, whose experiments have not been independently replicated here. Its reported quality and overhead depend on model shape, blocking, data, hardware, pipeline schedule, kernels, context length and training recipe. `mHC` is a `draft` wiki concept sourced from the DeepSeek-V4 report; the report gives its mechanism and systems discussion but no public ablation that isolates it from V4's other changes. The course's code is independently written pedagogical code, not source implementation or performance evidence.[^attnres-2026][^deepseek-v4-2026]

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex), architecture and residual sublayer definition.
[^attnres-2026]: Kimi Team, “Attention Residuals,” [source](../raw/arXiv-2603.15031v1/main.tex), especially Sections 1, 3–6 and reported experiments.
[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” [source](../raw/arXiv-2606.19348v1/main.tex), Section 2.2 and reported configuration/system discussion.
