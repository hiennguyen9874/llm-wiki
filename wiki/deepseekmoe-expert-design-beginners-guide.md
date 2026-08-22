---
type: Synthesis
title: "Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới"
description: A beginner-first course on DeepSeekMoE fine-grained routed experts, always-on shared experts, top-k trade-offs, compositional capacity, and a testable PyTorch reference implementation.
tags: [deepseekmoe, mixture-of-experts, sparse-models, routing, expert-specialization, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-22T00:00:00+00:00
sources:
  - id: deepseekmoe-concept
    resource: deepseekmoe-expert-specialization.md
    title: "DeepSeekMoE expert specialization"
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
  - id: moe-systems
    resource: mixture-of-experts-training-and-systems-trade-offs.md
    title: "Mixture-of-Experts training and systems trade-offs"
---

# Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới

`DeepSeekMoE` là một biến thể `Mixture-of-Experts` (MoE, hỗn hợp chuyên gia) cho nhánh `FFN`: thay vì chọn vài `experts` lớn, nó chia chúng thành nhiều `fine-grained routed experts` nhỏ hơn và chọn nhiều expert nhỏ hơn cho mỗi token. Một vài `shared experts` luôn chạy để tạo đường tính chung. Khi tăng số expert và `top-k` theo cùng tỉ lệ nghịch với width của mỗi expert, **dominant expert-FFN compute** và số expert parameters có thể gần giữ nguyên; thứ thay đổi là các tổ hợp expert mà router có thể dùng.[^deepseekmoe-2024] Đây là giải thích kiến trúc và bằng chứng ablation của paper, không phải bằng chứng rằng từng expert có nhãn semantic cố định như “code expert”.[^deepseekmoe-concept]

> [!success] Kết quả cần đạt
> 1. Giải thích được vì sao `m` lần nhiều expert nhỏ hơn và `m` lần lớn hơn `top-k` có thể giữ gần nguyên parameter/FFN-compute budget.
> 2. Phân biệt được `shared expert` luôn chạy với `routed expert` được chọn theo token.
> 3. Chạy, đọc, và kiểm chứng một PyTorch reference bằng `torch.testing.assert_close`, gồm weighted sum, accounting và tính position-wise.
> 4. Báo cáo được trade-off thay vì suy ra latency hoặc semantic specialization từ một con số `top-k`.

Bài này đi sau [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md). Nếu chưa rõ router, `softmax`, và `top-k`, hãy học bài đó trước; ở đây trọng tâm là **cách phân mảnh và kích hoạt expert** trong DeepSeekMoE.

## 1. Điều cần biết trước

- Cần biết một `Transformer block` có `self-attention`, residual connection, và một `FFN` position-wise. Xem [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).
- Cần biết `softmax`, phép nhân ma trận, và PyTorch `nn.Linear`.
- Không cần biết `expert parallelism` hay `all-to-all` để chạy code. Những chủ đề đó cùng `capacity factor`, overflow, và balance loss nằm trong [MoE capacity, load balancing & stability — bài lab cho người mới](moe-capacity-load-balancing-stability-lab.md) và [Expert parallelism và serving trade-offs — bài học cho người mới](expert-parallelism-serving-trade-offs-beginners-guide.md).
- Không cover: huấn luyện một LLM, kernel production, hay chứng minh một expert chứa một loại kiến thức có thể đọc bằng nhãn người.

## 2. Lý thuyết cốt lõi

### 2.1 MoE thay phần nào?

Bỏ qua normalization, một decoder block rút gọn là:

$$
u_t = \operatorname{Attention}(x_{1:T})_t + x_t,
\qquad
h_t = \operatorname{FFN}(u_t) + u_t.
$$

`FFN` dense có model width $D$ và intermediate width $D_{ff}$:

$$
\operatorname{FFN}(u)=W_2\,\phi(W_1u+b_1)+b_2,
$$

với $W_1\in\mathbb{R}^{D_{ff}\times D}$, $W_2\in\mathbb{R}^{D\times D_{ff}}$. Trong MoE, chỉ nhánh `FFN` ở một số layers được thay bằng nhiều FFN có weights riêng; attention, causal mask, residual, và language-model loss vẫn là các phần khác của block.[^deepseekmoe-2024]

```text
Dense FFN
u_t ─────────────────────► one shared FFN ───► + residual

DeepSeekMoE FFN
u_t ─► shared experts (always on) ───────────┐
  └─► router ─► selected routed experts ─────┼──► sum + residual
                                             │
```

### 2.2 Từ router đến `top-k`

Với $N$ routed experts, router tạo một affinity cho mỗi expert rồi `softmax` theo expert:

$$
s_{i,t}=\operatorname{Softmax}_i(u_t^\top e_i),
\qquad
\sum_{i=1}^{N}s_{i,t}=1.
$$

Nó chỉ giữ $K$ affinity lớn nhất làm gates:

$$
g_{i,t}=\begin{cases}
s_{i,t}, & i\in\operatorname{TopK}(s_{:,t},K),\\
0, & \text{otherwise.}
\end{cases}
\qquad
\operatorname{MoE}(u_t)=\sum_{i=1}^{N}g_{i,t}E_i(u_t).
$$

Trong công thức được trình bày của DeepSeekMoE, gates được chọn giữ **raw softmax probability**; chúng không nhất thiết sum bằng 1 sau khi bỏ các expert ngoài `top-k`. Một implementation khác có thể re-normalize gates đã chọn, nhưng đó là semantics khác cần ghi rõ khi so kết quả.[^deepseekmoe-2024]

| Khái niệm | Có chạy cho token này? | Weight trong output | Router quyết định? |
|---|---|---|---|
| Dense FFN | Luôn, một lần | implicit 1 | Không |
| `shared expert` | Luôn | implicit 1 | Không |
| `routed expert` trong `top-k` | Có | gate $g_{i,t}$ | Có |
| `routed expert` ngoài `top-k` | Không | 0 | Không được chọn |

> [!warning] `top-k` không phải semantic classifier
> Router được tối ưu end-to-end từ training objective. Một histogram route có thể phản ánh token, position, language, syntax, hoặc features khó quan sát. Nó không đủ để kết luận expert đó là “math expert” hay “code expert”.[^deepseekmoe-concept]

### 2.3 Fine-grained expert segmentation: một phép tính trước, rồi mới là trực giác

Bắt đầu với $N$ experts, mỗi expert có width $D_{ff}$, và `top-K`. Chọn segmentation factor $m$:

$$
N\rightarrow mN,
\qquad D_{ff}\rightarrow\frac{D_{ff}}{m},
\qquad K\rightarrow mK.
$$

Bỏ qua bias, activation và router, dominant parameter count của FFN hai projections tỷ lệ với $2DD_{ff}$. Vì vậy:

$$
P_{\text{before}}\approx N(2DD_{ff}),
\qquad
P_{\text{after}}\approx mN\left(2D\frac{D_{ff}}{m}\right)=P_{\text{before}}.
$$

Mỗi token cũng giữ gần nguyên active routed-FFN work:

$$
C_{\text{before}}\propto K(2DD_{ff}),
\qquad
C_{\text{after}}\propto mK\left(2D\frac{D_{ff}}{m}\right)=C_{\text{before}}.
$$

Đây là **accounting synthesis** từ shape FFN: không phải năng lực miễn phí. Nó chỉ repartition gần cùng parameter bank thành nhiều modules nhỏ hơn. Paper dùng chính strategy giảm intermediate dimension và tăng số activated experts để giữ parameter và compute cost không đổi theo thiết kế.[^deepseekmoe-2024]

Ví dụ có thể tính tay với $N=16$, $K=2$, $D_{ff}=4096$, $m=4$:

| Đại lượng | Conventional MoE | Fine-grained MoE |
|---|---:|---:|
| Số routed experts | 16 | $4\times16=64$ |
| Width mỗi expert | 4096 | $4096/4=1024$ |
| Experts chạy/token | 2 | $4\times2=8$ |
| Routed width chạy/token | $2\times4096=8192$ | $8\times1024=8192$ |
| Tổng expert width trong bank | $16\times4096=65536$ | $64\times1024=65536$ |

Điều mới là token có thể combine 8 expert nhỏ từ 64 candidates, thay vì 2 expert lớn từ 16 candidates. Authors gọi motivation là giảm `knowledge hybridity`: một expert lớn, ít về số lượng, có thể phải trộn nhiều functions không liên quan.[^deepseekmoe-2024]

### 2.4 `Compositional capacity`: con số tổ hợp nói được gì?

Nếu chỉ đếm subset không xét thứ tự hay gate weight, số lựa chọn `top-k` là:

$$
\binom{N}{K}=\frac{N!}{K!(N-K)!}.
$$

Ví dụ trên thay đổi từ $\binom{16}{2}=120$ thành $\binom{64}{8}=4{,}426{,}165{,}368$ possible subsets; đây là ví dụ minh họa trong paper.[^deepseekmoe-2024]

Diễn giải đúng: router **có nhiều subset khả dĩ hơn** để compose functions nhỏ. Nó không chứng minh rằng training đã dùng mọi subset, mọi subset có ích, các experts disjoint về semantics, hoặc chất lượng/latency nhất định tốt hơn. Gate weights còn continuous, nên binomial coefficient là trực giác về subset availability, không phải số functions model thực hiện.

### 2.5 Shared expert isolation: dành một phần budget cho đường chung

Sau segmentation, lấy $K_s$ experts làm `shared experts`. Mỗi token chạy tất cả chúng; router chỉ chọn among the remaining experts. Tổng số activated small experts vẫn giữ $mK$ khi routed `top-k` giảm còn $mK-K_s$:

$$
\underbrace{K_s}_{\text{always-on shared}}
+
\underbrace{(mK-K_s)}_{\text{selected routed}}
=mK.
$$

Với $mN$ experts tổng cộng, layer là:

$$
h_t=
\underbrace{\sum_{i=1}^{K_s}E_i(u_t)}_{\text{shared path}}
+
\underbrace{\sum_{i=K_s+1}^{mN}g_{i,t}E_i(u_t)}_{\text{routed path}}
+u_t,
$$

trong đó router chọn top-$(mK-K_s)$ chỉ từ routed experts. Authors hypothesize rằng shared path có thể consolidate common knowledge, để routed path tập trung hơn vào phần conditional; đây là intended effect được ablation ủng hộ trong configuration của paper, không phải định luật chung.[^deepseekmoe-2024]

```text
                       ┌─► shared 0 ─┐
u_t ───────────────────┼─► shared 1 ─┼──► sum
                       └─────────────┘
  │
  └─► router over routed experts ─► top-(mK - Ks) ─► weighted sum ─┘
```

Paper báo cáo configuration 16B có 64 fine-grained experts, 2 shared experts và 6 routed experts activated per token; mỗi small expert xấp xỉ một phần tư standard FFN. Tức mỗi token kích hoạt 8 small experts, nhưng chỉ 6 trong số đó do router chọn.[^deepseekmoe-2024]

### 2.6 Balance là điều kiện để specialization có cơ hội xảy ra

Nếu router luôn chọn vài experts, experts còn lại thiếu tokens và gradient: đó là `routing collapse`. DeepSeekMoE thêm expert-level auxiliary balance loss. Với $N'=mN-K_s$ routed experts và $K'=mK-K_s$ selected routed experts, paper định nghĩa:

$$
\mathcal{L}_{\mathrm{ExpBal}}=\alpha_1\sum_{i=1}^{N'}f_iP_i,
\quad
f_i=\frac{N'}{K'T}\sum_{t=1}^{T}\mathbb{1}(t\text{ chọn }i),
\quad
P_i=\frac{1}{T}\sum_{t=1}^{T}s_{i,t}.
$$

Khi experts nằm trên nhiều devices, paper thêm device-level objective để cân aggregate device work, thay vì ép mọi expert có load bằng hệt nhau. Điều này tách hai mục tiêu: tránh expert không được train và tránh một device thành straggler.[^deepseekmoe-2024] Capacity limits, padding, token drop và `all-to-all` vẫn là những ràng buộc systems riêng; bài code sau cố ý không mô phỏng chúng.[^moe-systems]

## 3. Implementation (PyTorch tối thiểu)

Code dưới triển khai **đúng data flow sư phạm**: mọi token chạy mọi `shared` expert, rồi chỉ các pair token–routed-expert có trong `top-k` mới chạy. `router softmax` dùng `float32`; selected gates là raw softmax values như công thức ở trên. Không có attention nên không có `RoPE`, `position_ids`, hay `KV cache`; các convention đó không áp dụng cho FFN position-wise này.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class SmallExpert(nn.Module):
    """Một FFN position-wise; mỗi instance có weights riêng."""
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
    """Reference dễ inspect; không phải distributed/fused production kernel."""
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
            raise ValueError("n_shared >= 0 and n_routed >= 1 are required")
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
        # x: (B, T, D); router quyết định độc lập cho từng token row.
        B, T, D = x.shape
        tokens = x.reshape(B * T, D)

        shared_out = torch.zeros_like(tokens)
        for expert in self.shared:                 # every token, every shared expert
            shared_out = shared_out + expert(tokens)

        # fp32 cho softmax; đưa gates về dtype của FFN để nhân output.
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(tokens.dtype)
        gates, ids = probs.topk(self.top_k_routed, dim=-1)  # (B*T, k)
        routed_out = torch.zeros_like(tokens)

        # Production sẽ pack tokens by expert và dùng batched GEMM lớn hơn.
        for expert_id, expert in enumerate(self.routed):
            token_rows, slots = torch.where(ids == expert_id)
            if token_rows.numel() == 0:
                continue
            values = expert(tokens[token_rows])
            weighted = gates[token_rows, slots].unsqueeze(-1) * values
            routed_out.index_add_(0, token_rows, weighted)

        loads = torch.bincount(ids.reshape(-1), minlength=self.n_routed)
        return (shared_out + routed_out).reshape(B, T, D), probs, gates, ids, loads
```

> [!warning] `torch.cat`/`index_add_` style này là teaching code, không phải serving code
> Python loop và gather/scatter nhỏ rất chậm. Runtime thật pack token rows theo expert, chạy grouped/batched GEMM, restore order, và có thể `all-to-all` qua devices.[^moe-systems]

## 4. Xác minh trước khi benchmark

Các tests dùng `float32` trên CPU/GPU. `rtol=1e-5, atol=1e-6` là tolerance phù hợp cho phép tính floating-point nhỏ này; nếu đổi sang `float16`/`bfloat16`, nới tolerance và báo dtype. Test “future leakage” của attention **không áp dụng**: module này không trộn positions. Thay vào đó, Test 4 xác minh property mạnh hơn của code này: đổi token cuối không thể đổi output các token trước.

```python
# Chạy sau định nghĩa classes ở Section 3.
torch.manual_seed(7)
B, T, D = 2, 4, 8
moe = SharedFineGrainedMoE(
    d_model=D, small_d_ff=16,
    n_shared=2, n_routed=6, top_k_routed=3,
)
x = torch.randn(B, T, D, dtype=torch.float32, requires_grad=True)
y, probs, gates, ids, loads = moe(x)

# Test 1 — shapes và softmax distribution.
assert y.shape == x.shape
assert ids.shape == (B * T, 3)
torch.testing.assert_close(
    probs.sum(dim=-1), torch.ones(B * T), rtol=1e-5, atol=1e-6
)

# Test 2 — gates chính là probs được chọn theo ids (không re-normalize).
torch.testing.assert_close(
    gates, probs.gather(dim=-1, index=ids), rtol=1e-5, atol=1e-6
)

# Test 3 — independently recompute weighted sum, không dùng index_add_.
tokens = x.detach().reshape(B * T, D)
expected_rows = []
for row in range(B * T):
    shared_sum = sum((expert(tokens[row:row + 1]) for expert in moe.shared),
                     torch.zeros_like(tokens[row:row + 1]))
    routed_sum = sum(
        (gates[row, slot].detach() * moe.routed[ids[row, slot].item()](tokens[row:row + 1])
         for slot in range(moe.top_k_routed)),
        torch.zeros_like(tokens[row:row + 1]),
    )
    expected_rows.append(shared_sum + routed_sum)
expected = torch.cat(expected_rows, dim=0).reshape(B, T, D)
torch.testing.assert_close(y.detach(), expected, rtol=1e-5, atol=1e-6)

# Test 4 — position-wise: thay token cuối không đổi outputs positions trước nó.
x_changed = x.detach().clone()
x_changed[:, -1] += 100.0
y_changed, *_ = moe(x_changed)
torch.testing.assert_close(
    y.detach()[:, :-1], y_changed[:, :-1], rtol=1e-5, atol=1e-6
)

# Test 5 — mỗi token tạo đúng k routed assignments; shared không được tính vào loads.
torch.testing.assert_close(
    loads.sum(), torch.tensor(B * T * moe.top_k_routed), rtol=0, atol=0
)

# Test 6 — gradient đi vào router qua selected gate values.
loss = y.square().mean()
loss.backward()
assert moe.router.weight.grad is not None
assert torch.isfinite(moe.router.weight.grad).all()
assert moe.router.weight.grad.norm().item() > 0
print("OK; routed loads:", loads.tolist())
```

Nếu Test 3 fail, check pairing `(token_rows, slots)` từ `torch.where(ids == expert_id)`: `slots` chọn đúng gate của expert đó. Nếu Test 4 fail, code đã vô tình đưa operation trộn batch/sequence (ví dụ `BatchNorm` theo tokens) vào module. Nếu Test 5 fail, phân biệt `n_shared` (always-active calls) với routed assignment histogram.

## 5. Benchmark / Trade-offs

### 5.1 Giữ cố định cái gì khi so sánh?

| Thay đổi | Benefit có thể có | Chi phí/risk | Fair comparison phải giữ/đo |
|---|---|---|---|
| Tăng `k`, expert size không đổi | Nhiều expert outputs | Expert FLOPs và dispatch assignments tăng | $N$, $D_{ff}$, batch, capacity, hardware |
| Segmentation $m$, $k\rightarrow mk$, $D_{ff}\rightarrow D_{ff}/m$ | More available compositions ở nominal FFN budget gần bằng | Nhiều small kernels/packing hơn; không đảm bảo specialize | Total bank params, active FFN width, quality |
| Tăng `shared experts` trong tổng active budget cố định | Common path luôn có mặt | Ít conditional routed slots hơn | $mK$, small expert width |
| Nhiều routed experts hơn | Nhiều candidates | Ít tokens/expert, imbalance dễ hơn | Batch tokens, balance/capacity, placement |

`Total parameters`, `active parameters`, nominal FLOPs, và wall-clock latency là bốn đại lượng khác nhau. Cùng nominal FFN FLOPs vẫn có router cost, padding, packing, small-GEMM utilization, và communication cost; toàn bộ weights vẫn phải giữ trong memory.[^moe-systems]

### 5.2 Mini benchmark đúng phạm vi

Reference không đủ để tạo performance number có ý nghĩa. Dùng harness sau để **đo trên máy của bạn**, báo hardware/dtype/batch, và so cùng code path. Đây đo MoE FFN cho một tensor; nó không tách `prefill`/`decode` của full Transformer vì module này không có `KV cache`.

```python
import time

def time_forward(module, x, warmup=20, repeats=100):
    module.eval()
    with torch.inference_mode():
        for _ in range(warmup):
            module(x)
        if x.is_cuda:
            torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(repeats):
            module(x)
        if x.is_cuda:
            torch.cuda.synchronize()
    return (time.perf_counter() - start) / repeats

# Ví dụ: thay đổi B/T/k chỉ một biến mỗi lần, không khẳng định kết quả trước khi chạy.
x_bench = torch.randn(8, 128, D, device=next(moe.parameters()).device)
print("seconds / forward:", time_forward(moe, x_bench))
```

Không kết luận từ benchmark này về throughput serving: Python dispatch là bottleneck của toy. Với full model, báo `prefill` và one-token `decode` tách riêng, cùng context length, batch policy, placement, precision, capacity/drop rate, và slowest-rank time.[^moe-systems]

## 6. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| `probs.sum(-1)` không gần 1 | `softmax` sai dimension/dtype | Test 1; logits phải shape `(B*T, n_routed)` |
| Output khác manual sum | Gate và expert output ghép sai slot | Test 3; inspect `ids[row]`, `gates[row]` |
| `loads.sum()` sai | Đếm shared experts lẫn routed assignments | Phải bằng `B*T*top_k_routed` |
| Một expert gần luôn 0 load | Collapse hoặc batch quá nhỏ | Aggregate `loads` qua nhiều batches; thêm balance/capacity lab |
| Gradient router bằng 0/None | Gate bị detach hoặc output không nhân gate | Test 6; check `gates * expert_output` |
| Toy code chậm | Expected Python gather/scatter overhead | Không tối ưu vòng lặp; dùng packed/fused runtime |
| Nominal FLOPs tốt nhưng latency xấu | Dispatch/communication/kernel utilization | Profile router, pack, expert GEMM, combine, all-to-all riêng |

## 7. Giới hạn & bước tiếp theo

Lab chứng minh routing arithmetic và code semantics, **không** chứng minh chất lượng LLM, generalization, balance khi train, hay speed production. `Compositional capacity` là số possible subsets; evidence specialization trong paper là ablation/routing-sensitivity evidence, không phải probe trực tiếp gán nhãn semantic cho từng expert.[^deepseekmoe-concept] Paper cũng là author-run evidence trong configuration riêng; hãy đọc [DeepSeekMoE evaluation and deployment trade-offs](deepseekmoe-evaluation-and-deployment-trade-offs.md) trước khi lặp lại claim về quality, FLOPs hoặc inference speed.

Lộ trình tiếp theo trong Stage 7 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md):

1. [MoE capacity, load balancing & stability — bài lab cho người mới](moe-capacity-load-balancing-stability-lab.md) — thêm capacity, token drop, và quan sát collapse.
2. [Expert parallelism và serving trade-offs — bài học cho người mới](expert-parallelism-serving-trade-offs-beginners-guide.md) — theo dõi dispatch/combine qua devices.
3. [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) — so sánh một hướng routing-bias về sau với auxiliary loss của DeepSeekMoE.

## Relationships

- **Builds on:** [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) — router, sparse `top-k`, và dense-FFN replacement.
- **Explains:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) — segmentation, shared/routed paths, và balance rationale.
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — giới hạn capacity, dispatch, communication và latency.
- **Evaluated by:** [DeepSeekMoE evaluation and deployment trade-offs](deepseekmoe-evaluation-and-deployment-trade-offs.md) — các results được báo cáo và giới hạn deployment.
- **Extends:** Stage 7, “Sparse capacity,” của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Đây là synthesis sư phạm và reference PyTorch tự viết; nó không phải DeepSeek training/serving implementation. Các equations, 16→64 illustrative combination count, shared/routed configuration, và balance objectives được kiểm tra trực tiếp với bundled primary paper.[^deepseekmoe-2024] Paper mô tả `knowledge hybridity`, `knowledge redundancy`, và `specialization` như explanatory framing; evidence không xác lập nhãn semantic ổn định cho mỗi expert.[^deepseekmoe-concept] Nominal expert-FFN accounting không bao gồm end-to-end system cost, do đó mọi claim về throughput hay latency cần benchmark trên workload/hardware đích.[^moe-systems]

[^deepseekmoe-concept]: [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) — maintained synthesis, evidence limits, and links to the primary source.
[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [bundled primary source](../raw/arXiv-2401.06066v1/main.tex), Sections 2–4 and 6.
[^moe-systems]: [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — maintained synthesis; Switch-specific material remains bounded by its stated secondary-source evidence limit.
