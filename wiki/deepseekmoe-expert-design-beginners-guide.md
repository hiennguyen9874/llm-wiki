---
type: Synthesis
title: "Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới"
description: A beginner-first course on DeepSeekMoE fine-grained routed experts, always-on shared experts, top-k trade-offs, compositional capacity, and a testable PyTorch reference implementation.
tags: [deepseekmoe, mixture-of-experts, sparse-models, routing, expert-specialization, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00+00:00 }
sources:
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
---

# Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới

`DeepSeekMoE` không chỉ tăng số lượng `experts`. Nó chia một bank ít expert lớn thành nhiều `fine-grained routed experts` nhỏ hơn, tăng `top-k` theo cùng tỷ lệ để giữ gần nguyên expert-FFN compute, rồi thêm `shared experts` luôn chạy cho mọi token. Ý tưởng là shared path học common features, còn routed path có điều kiện có thể học các phần khác biệt hơn. Đây là architecture hypothesis có bằng chứng ablation của authors, **không phải** bằng chứng rằng mỗi expert có một semantic role rõ ràng như “code expert” hay “math expert”.[^deepseekmoe-2024]

> [!success] Sau bài này
> Bạn có thể (1) phân biệt `fine-grained expert`, `routed expert`, và `shared expert`; (2) tự kiểm tra vì sao segmentation có thể giữ parameter count và compute gần không đổi; (3) giải thích đúng trade-off của `top-k`; (4) hiểu con số combinatorial capacity nói gì và không nói gì; và (5) chạy một PyTorch reference implementation có kiểm tra routing load và gradient.

Bài này tiếp nối [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md). Bài trước giải thích router và basic `top-1`/`top-k`; bài này chỉ tập trung vào **expert design và specialization** của [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md).

## 1. Điều kiện tiên quyết: MoE thay phần nào của Transformer?

Trong một `Transformer block`, `self-attention` cho tokens trao đổi information trong sequence. Sau đó, một `FFN` (còn gọi `MLP`) xử lý từng token independently with shared weights. Bỏ qua normalization để tập trung vào phần cần học:

$$
u_t = \operatorname{Attention}(x_{1:T})_t + x_t,
\qquad
h_t = \operatorname{FFN}(u_t) + u_t.
$$

Một dense FFN có hidden width $D$ và intermediate width $D_{ff}$ có dạng:

$$
\operatorname{FFN}(u) = W_2\,\phi(W_1u+b_1)+b_2,
$$

với $W_1\in\mathbb{R}^{D_{ff}\times D}$, $W_2\in\mathbb{R}^{D\times D_{ff}}$, và activation $\phi$ như `GELU` hoặc `SwiGLU`.

`MoE` thay **một số FFN layers** bằng một bank gồm nhiều FFN cùng input/output shape nhưng weights độc lập:

$$
E_1(u), E_2(u), \ldots, E_N(u).
$$

Một `router` nhìn token representation $u_t$, chấm affinity cho experts, và chỉ chạy một subset. Attention, residual connection, causal mask, và language-model loss không bị MoE thay thế.

```text
Dense FFN
u_t ─────────────────────► one shared FFN ─────► residual add

Routed MoE FFN
u_t ─► router ─► selected expert FFN(s) ───────► residual add
```

## 2. Conventional `top-k` MoE: điểm xuất phát để so sánh

Gọi $N$ là số routed experts và $K$ là số experts selected per token. Router có một vector hoặc linear projection cho mỗi expert. Với notation của paper, affinity và sparse gate là:

$$
s_{i,t}=\operatorname{Softmax}_i(u_t^\top e_i),
\qquad
g_{i,t}=\begin{cases}
s_{i,t}, & i\in \operatorname{TopK}(s_{:,t},K),\\
0, & \text{otherwise.}
\end{cases}
$$

Output của MoE branch là weighted sum:

$$
\operatorname{MoE}(u_t)=\sum_{i=1}^{N}g_{i,t}E_i(u_t).
$$

Vì chỉ $K$ gate values khác 0, token chỉ cần execute $K$ experts. `top-1` chọn một expert; `top-k` với $K>1$ combine nhiều expert outputs.[^deepseekmoe-2024]

### Một ví dụ nhỏ

Giả sử router có 4 affinities cho token `u`:

| Expert | Router probability | Được chọn bởi `top-2`? | Gate thực thi |
|---|---:|---|---:|
| $E_0$ | 0.05 | Không | 0 |
| $E_1$ | 0.52 | Có | 0.52 |
| $E_2$ | 0.31 | Có | 0.31 |
| $E_3$ | 0.12 | Không | 0 |

Token này chạy $E_1(u)$ và $E_2(u)$, rồi nhận $0.52E_1(u)+0.31E_2(u)$. Trong formulation của DeepSeekMoE, selected values là original softmax affinities; tổng selected gates vì thế có thể nhỏ hơn 1. Một library khác có thể re-normalize only selected gates; đó là implementation choice khác và không nên silently assume giống paper.[^deepseekmoe-2024]

> [!warning] Router selection không phải semantic label
> Router được train từ end-to-end language-model objective. Việc một token được gửi đến expert nào có thể phụ thuộc vào token identity, syntax, language, layer, position, hoặc feature không dễ diễn giải. Routing pattern tự nó không chứng minh expert “biết” một human-defined domain.

## 3. Vấn đề DeepSeekMoE muốn giải quyết

Paper gọi hai failure modes tiềm năng của conventional MoE là `knowledge hybridity` và `knowledge redundancy`.[^deepseekmoe-2024]

### 3.1 `Knowledge hybridity`: một expert lớn phải phục vụ quá nhiều thứ

Nếu chỉ có 8 hoặc 16 experts lớn, một expert có thể được chọn bởi tokens cần rất nhiều functions không giống nhau. Ví dụ minh họa:

```text
same routed expert
 ├─ punctuation/context pattern
 ├─ English syntax
 ├─ a code identifier
 ├─ arithmetic format
 └─ factual phrase
```

Vì tất cả phải sống trong weights của một FFN, authors hypothesize rằng expert này phải mix unrelated functions, làm specialization kém focused. Đây là motivation, không phải một theorem rằng 16 experts luôn insufficient hoặc rằng every smaller expert sẽ tự động specialize.[^deepseekmoe-2024]

### 3.2 `Knowledge redundancy`: nhiều routed experts lặp common work

Một token có different conditional needs, nhưng cũng cần common transformations: formatting, basic linguistic patterns, hoặc other broadly useful features. Nếu mọi computation đều đi qua routed experts, nhiều experts có thể independently learn similar common features. Authors hypothesize điều này lãng phí parameter capacity that could instead represent conditional functions.[^deepseekmoe-2024]

DeepSeekMoE có hai design responses tương ứng:

| Potential issue | Design response | Intended effect |
|---|---|---|
| `knowledge hybridity` | `fine-grained expert segmentation` | Cho router compose nhiều small functions thay vì chọn few large mixed experts |
| `knowledge redundancy` | `shared expert isolation` | Đặt common computation vào always-on path, để routed experts concentrate on conditional work |

## 4. Fine-grained expert segmentation

Bắt đầu với conventional MoE có:

- $N$ experts;
- mỗi expert có intermediate width $D_{ff}$;
- router chọn `top-K` experts.

Chọn segmentation factor $m$. DeepSeekMoE split mỗi large expert thành $m$ smaller experts:

- number of experts: $N\rightarrow mN$;
- intermediate width per expert: $D_{ff}\rightarrow D_{ff}/m$;
- selected experts: $K\rightarrow mK$.

### 4.1 Tại sao total expert parameters gần giữ nguyên?

Parameter count dominant của một two-linear-layer FFN tỷ lệ gần đúng với $2DD_{ff}$; bỏ qua bias và architecture details. Baseline expert bank có:

$$
P_{\text{bank}}\approx N(2DD_{ff}).
$$

Sau segmentation:

$$
P_{\text{bank, fine}}\approx mN\left(2D\frac{D_{ff}}{m}\right)
=N(2DD_{ff}).
$$

Vậy splitting không magic tạo thêm total FFN capacity miễn phí: nó repartitions gần cùng total expert parameters thành nhiều modules nhỏ hơn. Router parameters, bias, normalization, and exact gated-MLP structure can make actual counts differ slightly.

### 4.2 Tại sao routed-FFN compute per token gần giữ nguyên?

Một token ở baseline chạy $K$ experts, mỗi expert width $D_{ff}$:

$$
C_{\text{baseline}}\propto K(2DD_{ff}).
$$

Sau segmentation, token chạy $mK$ experts, mỗi expert width $D_{ff}/m$:

$$
C_{\text{fine}}\propto mK\left(2D\frac{D_{ff}}{m}\right)
=K(2DD_{ff}).
$$

Đây là lý do “`top-k` lớn hơn” không đồng nghĩa automatic more routed-FFN FLOPs: phải xem **expert width có bị giảm tương ứng không**. Với same-width experts, tăng $k$ thực sự tăng expert compute.

> [!note] “Approximately” là quan trọng
> Equality trên là accounting cho dominant dense matrix multiplies. Thực tế có overhead router, dispatch/combine, kernel launch, padding/capacity slots, activation, and cross-device communication. Smaller experts cũng có thể make hardware utilization worse. Do đó same nominal FFN FLOPs không bảo đảm same training time hay serving latency.

### 4.3 Một worked configuration

Giả sử baseline có 16 experts, `top-2`, mỗi expert intermediate width 4096. Chọn $m=4$:

| Quantity | Baseline | Fine-grained design |
|---|---:|---:|
| Routed expert count | 16 | $4\times16=64$ |
| Width / expert | 4096 | $4096/4=1024$ |
| Selected experts / token | 2 | $4\times2=8$ |
| Routed width processed / token | $2\times4096=8192$ | $8\times1024=8192$ |
| Expert-bank width total | $16\times4096=65536$ | $64\times1024=65536$ |

Cả parameter and dominant routed-FFN compute are approximately matched. Khác biệt architecture là token now receives a weighted combination of 8 small expert outputs selected from 64 candidates, not 2 large outputs from 16.

## 5. `Compositional capacity`: số tổ hợp lớn có nghĩa gì?

Nếu chỉ quan tâm **unweighted subset of selected experts**, number of possible `top-k` subsets là binomial coefficient:

$$
\binom{N}{K}=\frac{N!}{K!(N-K)!}.
$$

Ở worked configuration:

$$
\binom{16}{2}=120,
\qquad
\binom{64}{8}=4{,}426{,}165{,}368.
$$

Đó là comparison trong paper.[^deepseekmoe-2024]

### 5.1 Diễn giải đúng

Fine-grained routing makes far more **available expert subsets**. Nếu small experts học reusable components, router có more ways to combine them for different tokens/contexts. Đây là `compositional capacity`: capacity to form different combinations from a bank of components.

Ví dụ purely illustrative:

```text
Token/context A → [syntax, English, quotation, common]
Token/context B → [code-style, identifier, indentation, common]
Token/context C → [math-format, number-pattern, reasoning, common]
```

Không cần assign a whole large expert to every combination of needs. Router can select a different subset of smaller transformations.

### 5.2 Bốn điều nó **không** chứng minh

A large $\binom{N}{K}$ does **not** prove:

1. training visits or uses every subset;
2. each selected subset has useful behavior;
3. experts have disjoint semantic knowledge;
4. quality rises with no systems cost.

Actual routing is constrained by learned affinities, data distribution, load balancing, capacity limits, and training dynamics. Moreover, output is a **weighted** sum; gate values vary continuously, so a count of unordered subsets is only a useful intuition, not a count of functions the model realizes. The paper provides ablation and routing-sensitivity evidence consistent with better specialization, but does not directly label individual expert semantics.[^deepseekmoe-2024]

## 6. Shared expert isolation

Fine-grained segmentation addresses the authors’ `hybridity` motivation. `shared expert isolation` addresses their redundancy motivation.

Choose $K_s$ small experts as `shared experts`. Every token runs all of them. The router only chooses among the remaining `routed experts`.

```text
                         ┌─► Shared expert 0 ─┐
u_t ─────────────────────► Shared expert 1 ─┼─► sum + residual
  │                      └───────────────────┘
  │
  └─► router ─► top-(mK - K_s) routed experts ─► weighted sum ─┘
```

With $mN$ total fine-grained experts, complete DeepSeekMoE has:

- $K_s$ always-active shared experts;
- $mN-K_s$ routed experts;
- $mK-K_s$ selected routed experts per token.

The total activated small experts remains $mK$:

$$
K_s+(mK-K_s)=mK.
$$

Therefore, under the same small-expert width, adding shared experts does not have to change the intended active expert-FFN compute budget; it reallocates part of that budget from conditional routed work to unconditional shared work.[^deepseekmoe-2024]

The complete layer, omitting normalization, is:

$$
h_t=
\underbrace{\sum_{i=1}^{K_s}E_i(u_t)}_{\text{always-on shared path}}
+
\underbrace{\sum_{i=K_s+1}^{mN}g_{i,t}E_i(u_t)}_{\text{sparse routed path}}
+u_t,
$$

where only the top-$(mK-K_s)$ routed gates are nonzero.

### Why not route every expert?

A shared path gives every token a reliable common transformation without requiring router competition for it. Under the paper’s hypothesis, common knowledge can be consolidated there and routed experts can spend more capacity on conditional distinctions. But always-active means shared-expert compute occurs for **every** token; too much shared capacity reduces the conditional part of the fixed active budget. $K_s$ is a design hyperparameter to validate, not a universally correct constant.[^deepseekmoe-2024]

### Reported DeepSeekMoE 16B configuration

The paper reports 2 shared experts and 6 selected routed experts out of 64 fine-grained experts, each roughly one quarter of the standard FFN size. Thus each token activates 8 small experts in total. It also leaves the first Transformer layer dense because load balance in that layer converged slowly in that setup.[^deepseekmoe-2024]

Do not generalize these values to every MoE: later architectures can use different number of experts, $k$, balance mechanisms, placement, and capacity rules.

## 7. `top-k` is a multi-dimensional trade-off

It is tempting to say “higher `top-k` is better because it uses more experts.” That sentence misses the design context.

| Choice | Potential benefit | Cost or risk | What must be held constant for a fair comparison? |
|---|---|---|---|
| Larger $k$, same expert size | More outputs can contribute | More expert FLOPs, dispatch volume, capacity pressure | Parameter count, batch, hardware, router/balance setup |
| Larger $k$, smaller experts via segmentation | More compositional choices at approximately matched FFN compute | More small-expert routing/packing overhead; no guaranteed semantic specialization | Total bank parameters and active FFN width/FLOPs |
| `top-1` | Lowest expert calls and simplest dispatch | Less per-token mixture | Expert width/count, capacity and quality target |
| More shared experts | Common path is always available; may reduce routed redundancy | Less conditional budget; always-on compute | Total active small-expert count and width |
| More routed experts | More candidate modules | Harder load balance; potentially sparse/undertrained experts | Tokens per batch, capacity, expert placement |

`top-k` also changes training signal: every selected expert receives gradient for that token; non-selected routed experts do not execute that token’s FFN. More selection may distribute signals across components, but it raises the difficulty of routing balanced traffic and efficiently batching each expert.

### `Total parameters`, `active parameters`, and latency remain different

For a bank of $mN$ fine experts, each approximately $P_E/m$ parameters, total expert parameters are roughly $NP_E$. Per token, active expert parameters are roughly $mK\cdot(P_E/m)=KP_E$ before counting attention and other non-expert components. Shared experts are active too.

These arithmetic counts do not include:

- all model weights that must be stored and loaded;
- attention and dense layers;
- router computation;
- capacity padding and dropped/overflow assignments;
- `all-to-all` communication when experts are on different devices;
- kernel efficiency and batch-size effects.

Therefore an `active parameters` headline is not an end-to-end latency or cost measurement. Read [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) before making deployment claims.

## 8. PyTorch reference: fine-grained routed + shared experts

The following educational code implements the complete data flow: every token runs `n_shared` experts and is routed to `top_k_routed` experts among the rest. It prioritizes transparent correctness over speed:

- each expert is an ordinary small FFN;
- selected gates are the raw `softmax` values, matching the paper’s displayed formulation rather than re-normalizing `top-k` gates;
- `loads` counts routed assignments only;
- it intentionally excludes capacity limits, load-balance loss, distributed `all-to-all`, and fused kernels.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class SmallExpert(nn.Module):
    """One position-wise FFN. Different instances have different weights."""
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SharedFineGrainedMoE(nn.Module):
    """Readable reference, not a production distributed MoE kernel."""
    def __init__(
        self,
        d_model: int,
        small_d_ff: int,
        n_shared: int,
        n_routed: int,
        top_k_routed: int,
    ):
        super().__init__()
        if n_shared < 0 or n_routed < 1:
            raise ValueError("n_shared must be >= 0 and n_routed must be >= 1")
        if not 1 <= top_k_routed <= n_routed:
            raise ValueError("top_k_routed must satisfy 1 <= k <= n_routed")

        self.n_routed = n_routed
        self.top_k_routed = top_k_routed
        self.shared = nn.ModuleList(
            [SmallExpert(d_model, small_d_ff) for _ in range(n_shared)]
        )
        self.routed = nn.ModuleList(
            [SmallExpert(d_model, small_d_ff) for _ in range(n_routed)]
        )
        self.router = nn.Linear(d_model, n_routed)

    def forward(self, x: torch.Tensor):
        # x has shape (batch, sequence, d_model); routing is per token.
        B, T, D = x.shape
        tokens = x.reshape(B * T, D)

        # Shared branch: every token executes every shared expert.
        shared_out = torch.zeros_like(tokens)
        for expert in self.shared:
            shared_out = shared_out + expert(tokens)

        # Routed branch: only selected token--expert pairs are executed.
        # fp32 router softmax is an educational stability-minded choice.
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(tokens.dtype)
        gates, ids = probs.topk(self.top_k_routed, dim=-1)
        routed_out = torch.zeros_like(tokens)

        for expert_id, expert in enumerate(self.routed):
            token_rows, slots = torch.where(ids == expert_id)
            if token_rows.numel() == 0:
                continue
            expert_values = expert(tokens[token_rows])
            weighted_values = gates[token_rows, slots].unsqueeze(-1) * expert_values
            routed_out.index_add_(0, token_rows, weighted_values)

        # Each token has top_k_routed assignments; shared calls are not included.
        loads = torch.bincount(ids.reshape(-1), minlength=self.n_routed)
        y = shared_out + routed_out
        return y.reshape(B, T, D), probs, ids, loads
```

### Chạy một correctness smoke test

```python
torch.manual_seed(7)
B, T, D = 3, 5, 16
n_shared, n_routed, k = 2, 14, 6  # 2 shared + 6 routed = 8 active small experts

moe = SharedFineGrainedMoE(
    d_model=D,
    small_d_ff=32,
    n_shared=n_shared,
    n_routed=n_routed,
    top_k_routed=k,
)
x = torch.randn(B, T, D, requires_grad=True)
y, probs, ids, loads = moe(x)

assert y.shape == x.shape
assert probs.shape == (B * T, n_routed)
assert ids.shape == (B * T, k)
assert torch.allclose(probs.sum(dim=-1), torch.ones(B * T), atol=1e-6)
assert loads.sum().item() == B * T * k  # shared experts are deliberately excluded

loss = y.square().mean()
loss.backward()
assert moe.router.weight.grad is not None
assert all(e.net[0].weight.grad is not None for e in moe.shared)
print("routed assignments per expert:", loads.tolist())
print("router grad norm:", moe.router.weight.grad.norm().item())
```

For a toy analogue of the paper’s 16B layer, there are 64 total small experts: 2 shared and 62 routed; each token chooses 6 routed experts. The code uses 2 + 14 only to keep the printed histogram readable.

> [!warning] Không dùng code này để benchmark performance
> The Python loops and boolean indexing create many small operations. Real MoE systems group tokens by expert, execute larger packed batches, restore original order, and exchange tokens across devices when expert parallelism is used. A correct but simple reference can be drastically slower than a fused production implementation.

## 9. Quan sát và debug trước khi nói về specialization

Một expert “specialized” phải first be trained and used. Log these signals during training:

| Signal | Cách đọc | Warning sign |
|---|---|---|
| Routed load per expert | Count assignments in `ids` over batches | Một few experts receive nearly all tokens, hoặc many are nearly always zero |
| Router probability | Histogram/mean of `probs` | Extremely peaked or unstable distribution can precede collapse |
| Overflow/drop rate | Fraction assignments rejected by capacity rule | Low active FLOPs but degraded quality due to dropped assignments |
| Per-device load | Aggregate selected tokens for experts on each device | One device is straggler even if some individual expert loads look reasonable |
| Ablation | Remove/replace a subset and measure controlled loss/quality | Do not infer semantic roles from a route histogram alone |

DeepSeekMoE uses a small expert-level auxiliary balance loss against routing collapse and a separate device-level loss when experts are distributed. The paper argues that forcing strict equal load per expert can harm quality; balancing device computation is a different objective from making every expert equally popular.[^deepseekmoe-2024]

### A minimal load statistic for the reference code

```python
fraction = loads.float() / loads.sum().clamp_min(1)
print("routed-load fraction:", fraction.tolist())
print("least/most loaded expert:", loads.min().item(), loads.max().item())
```

A single small batch is noisy, so aggregate over many steps. Balanced traffic is not evidence of semantic specialization, but severe imbalance means unused experts cannot receive enough data/gradient to plausibly develop useful distinct functions.

## 10. What evidence supports the DeepSeekMoE claim?

The paper’s 2B ablations compare designs under matched parameter and compute accounting. It reports that fine-grained segmentation and shared experts improve its results, and that removing high-score routed experts affects DeepSeekMoE more than a GShard comparison; the authors interpret this as evidence of reduced redundancy and improved specialization. The paper also reports a 16B configuration broadly comparable to its dense DeepSeek 7B at lower reported expert-FFN FLOPs.[^deepseekmoe-2024]

This supports a narrower conclusion:

> In the paper’s training, data, and systems configuration, the fine-grained plus shared-expert design was empirically useful and routing ablations were consistent with the authors’ specialization interpretation.

It does **not** establish a universal rule that this design wins for every model, dataset, sequence length, or hardware configuration. The paper’s benchmarks are author-run; total weight memory, routing, communication, and kernel efficiency are outside a pure activated-FLOPs comparison. See [DeepSeekMoE evaluation and deployment trade-offs](deepseekmoe-evaluation-and-deployment-trade-offs.md) for the reported comparisons and their qualifications.

## 11. Checklist: đọc một expert design như một engineer

1. **Baseline accounting:** How many experts ($N$), what expert width ($D_{ff}$), and what `top-K`?
2. **Segmentation accounting:** Is each expert actually smaller by $m$ when expert count and `k` rise by $m$? Verify both bank parameters and active FFN width.
3. **Shared path:** How many `shared experts` run for every token? Is their compute counted in active parameters/FLOPs?
4. **Router semantics:** Is `top-k` taken over only routed experts? Are selected gates raw scores or re-normalized?
5. **Capacity and balance:** What prevents routing collapse and token overflow? Is balance measured per expert, per device, or both?
6. **Systems:** Where do experts live? What dispatch, `all-to-all`, padding, and batch-size costs are included in a speed claim?
7. **Evidence:** Are specialization claims direct probes/controlled ablations, or only interpretation of routing statistics? Is the comparison matched on data and training tokens?

## 12. Bài tập

1. Starting from $N=8$, $K=2$, $D_{ff}=512$, choose $m=4$. Calculate fine-grained expert count, width, and number selected per token. Verify both totals in Section 4.
2. In the PyTorch code, set `n_shared=0`, then `n_shared=2` while keeping `n_shared + top_k_routed` fixed. Explain what compute is now unconditional and what compute remains conditional.
3. Add a per-expert capacity to the routed branch. Count dropped assignments, then observe how load histogram and drop rate change with $k$.
4. Run an ablation that zeroes one routed expert at inference. Why would a loss change still not prove that the expert is “a math expert” or “a code expert”?
5. Read [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) to compare a later router-bias approach with DeepSeekMoE’s auxiliary-loss approach.

## Relationships

- **Builds on:** [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) for dense-FFN replacement, router basics, and basic top-$k$ code.
- **Explains:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) through compute accounting, compositional capacity, shared/routed data flow, and a reference implementation.
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) to qualify routing balance, capacity, distributed dispatch, and latency claims.
- **Evaluated by:** [DeepSeekMoE evaluation and deployment trade-offs](deepseekmoe-evaluation-and-deployment-trade-offs.md), which records the reported results and evidence limits.
- **Extends:** Stage 7, “Sparse capacity,” of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

This is a beginner-oriented synthesis and its PyTorch code is a didactic reference, not DeepSeek’s training or serving implementation. The architecture equations, 16-to-64 illustrative combination count, reported 16B configuration, balance objectives, and author-reported ablations come from the bundled primary DeepSeekMoE v1 paper. `Knowledge hybridity`, `knowledge redundancy`, and expert `specialization` are the authors’ explanatory framing; the source does not directly establish a stable human-readable semantic label for each expert. Same nominal routed-FFN compute also does not imply same wall-clock cost or deployment latency.[^deepseekmoe-2024]

[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Sections 2–6 and Appendix A.
