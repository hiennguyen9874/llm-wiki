---
type: Synthesis
title: Mixture-of-Experts và sparse routing — bài học cho người mới
description: A beginner-first course on replacing a dense FFN with routed experts, router softmax, top-1/top-k sparse routing, total versus active parameters, and a testable PyTorch toy MoE.
tags: [mixture-of-experts, sparse-models, routing, switch-transformer, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T11:50:56+07:00 }
sources:
  - id: moe-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
---

# Mixture-of-Experts và sparse routing — bài học cho người mới

`Mixture-of-Experts` (MoE) thay `FFN`/`MLP` dùng chung trong một `Transformer block` bằng nhiều `expert` FFN. Với mỗi token, một `router` tính điểm cho các expert và chỉ gọi `top-1` hoặc `top-k` expert có điểm cao nhất. Vì vậy model có thể có nhiều `total parameters`, nhưng chỉ một phần expert parameters là `active` cho một token. `Switch Transformer` là điểm bắt đầu dễ hiểu nhất: nó chọn đúng một expert (`top-1`) cho mỗi token.[^moe-overview-2026]

> [!success] Mục tiêu
> Sau bài này, bạn có thể chỉ ra chính xác MoE thay phần nào của dense Transformer, tự tính một forward pass của router, phân biệt `top-1` với `top-k`, giải thích đúng con số `active parameters`, và chạy một toy MoE PyTorch có kiểm tra shape, routing load, và gradient.

Bài này là một **synthesis sư phạm**, không phải recipe để tái tạo kết quả benchmark của Switch Transformer. Claims lịch sử và cơ chế Switch được lấy từ overview thứ cấp có trong repository; phần `top-k` fine-grained và shared expert có thêm bằng chứng từ paper DeepSeekMoE.[^moe-overview-2026][^deepseekmoe-2024]

## 1. Điều kiện tiên quyết và bức tranh lớn

Bạn nên đã hiểu một `decoder-only Transformer`: `self-attention` cho token trao đổi information theo sequence, còn `FFN` xử lý từng position bằng cùng một transformation. Xem [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) nếu phần này còn mới.

Một dense block dạng pre-normalization có thể rút gọn thành:

$$
u = x + \operatorname{Attention}(\operatorname{Norm}_1(x)),
\qquad
\operatorname{Block}(x) = u + \operatorname{FFN}(\operatorname{Norm}_2(u)).
$$

Với hidden width $D$ và FFN intermediate width $D_{ff}$, dense FFN thường là:

$$
\operatorname{FFN}(h)=W_2\,\phi(W_1h+b_1)+b_2,
$$

trong đó $W_1$ mở rộng $D\to D_{ff}$, activation $\phi$ có thể là `GELU`/`SwiGLU`, và $W_2$ chiếu về $D$. **Mọi token đều chạy cùng một cặp trọng số** $W_1,W_2$.

MoE không thay `attention`, `causal mask`, `residual connection`, hoặc language-model objective. Nó chủ yếu thay branch `FFN` trong một số block:

```text
Dense block
hidden token → shared FFN → update

MoE block
hidden token → router → selected expert FFN(s) → weighted update
```

Một model có thể xen kẽ dense FFN và MoE FFN thay vì biến mọi layer thành MoE.[^moe-overview-2026] Điều đó là architecture choice, không phải định nghĩa bắt buộc của MoE.

## 2. Từ một shared FFN đến một expert bank

Tạo $N$ bản FFN độc lập, gọi là `experts`:

$$
E_1(h), E_2(h), \ldots, E_N(h).
$$

Mỗi expert nhận cùng shape input và trả cùng shape output như dense FFN, nhưng có weights riêng. Tập các expert này là `expert bank`.

Ví dụ với $N=4$:

```text
token "def"  ──router──► Expert 2
token "("    ──router──► Expert 0
token "Paris"──router──► Expert 3
```

Router học assignment từ training loss; **không có rule nào bảo đảm** Expert 2 là “code expert” hoặc Expert 3 là “geography expert”. Expert có thể phản ứng với language, position, token pattern, hoặc feature khó gán nhãn. Chỉ gọi chúng là “specialized” khi có evidence phù hợp.[^moe-overview-2026][^deepseekmoe-2024]

### Dense và MoE khác nhau ở đâu?

| Câu hỏi | Dense FFN | MoE FFN |
|---|---|---|
| Có bao nhiêu FFN weights? | Một FFN | $N$ expert FFN độc lập |
| Token chạy qua gì? | Cùng một FFN | Một nhóm expert do router chọn |
| Token kề nhau có thể xử lý khác nhau? | Cùng weights | Có thể đến expert khác nhau |
| Cần router? | Không | Có |
| Có nguy cơ expert overload? | Không | Có |

## 3. Router: từ hidden state đến routing probabilities

Với hidden vector của một token $h\in\mathbb{R}^{D}$, router là một linear layer có $N$ outputs:

$$
z = W_rh+b_r, \qquad z\in\mathbb{R}^{N}.
$$

$z_i$ là `router logit` của expert $i$, chưa phải probability. `softmax` biến logits thành distribution:

$$
p_i(h)=\frac{\exp(z_i)}{\sum_{j=1}^{N}\exp(z_j)},
\qquad \sum_{i=1}^{N}p_i(h)=1.
$$

Ví dụ một token với bốn experts:

| Expert | Router logit | `softmax` probability |
|---|---:|---:|
| 0 | 0.2 | 0.16 |
| 1 | 1.7 | 0.71 |
| 2 | -0.4 | 0.09 |
| 3 | 0.6 | 0.24 |

`Expert 1` có xác suất lớn nhất. Router được áp dụng **per token**, không phải một lần cho cả sequence. Vì thế token khác trong cùng batch có thể có distribution khác.

> [!note] `softmax` không tự tạo sparsity
> Sau `softmax`, mọi $p_i$ thường dương: đây vẫn là dense distribution. Sự sparse xuất hiện khi ta giữ only `top-1` hoặc `top-k` entries rồi chỉ thực thi các expert tương ứng.

## 4. `top-1`: Switch Transformer

`Switch Transformer` chọn expert có probability lớn nhất:

$$
i^*=\arg\max_i p_i(h),
$$

và output routed branch là:

$$
\operatorname{SwitchFFN}(h)=p_{i^*}(h)E_{i^*}(h).
$$

Chỉ một expert FFN chạy cho token đó. Nhân output với selected probability cho phép gradient cập nhật router qua giá trị gate; bản thân lựa chọn `argmax` là discrete, nên không có gradient trực tiếp đi qua việc đổi expert nào được chọn.[^moe-overview-2026]

`top-1` giảm số expert computations và token dispatch so với routing nhiều expert. Tuy nhiên, “ít FLOPs expert hơn” **không đồng nghĩa** end-to-end latency luôn thấp hơn: router, packing, padding, network communication, và weight loading vẫn có chi phí.[^moe-overview-2026]

## 5. `top-k`: cho một token gọi nhiều expert

Với `top-k`, lấy tập $S_k(h)$ gồm $k$ experts có $p_i(h)$ cao nhất và cộng các outputs có trọng số:

$$
\operatorname{MoE}_{top-k}(h)=
\sum_{i\in S_k(h)}p_i(h)E_i(h).
$$

- `top-1` là trường hợp $k=1$.
- `top-k` tăng số expert FFN evaluations từ một lên $k$ cho mỗi token.
- Một implementation có thể re-normalize selected gate weights để chúng tổng bằng 1; đó là design choice. Công thức Switch trong source ở trên dùng selected softmax probability trực tiếp.[^moe-overview-2026]

DeepSeekMoE cho thấy `top-k` không nhất thiết có nghĩa “nhiều FLOPs hơn dense baseline”: nếu split một expert lớn thành nhiều expert nhỏ hơn và tăng $k$ tương ứng, total routed-FFN compute có thể gần giữ nguyên trong cấu hình đó. Nó cũng thêm `shared experts` luôn chạy cho mọi token, tách common computation khỏi routed branch.[^deepseekmoe-2024]

### So sánh trực giác

| Routing | Expert calls/token | Output | Điểm chính |
|---|---:|---|---|
| Dense | 1 shared FFN | $E(h)$ | Không conditional computation |
| `top-1` / Switch | 1 selected expert | $p_{i^*}E_{i^*}(h)$ | Đơn giản nhất, sparse nhất |
| `top-k` | $k$ selected experts | weighted sum | Nhiều routing composition hơn, nhiều expert work hơn |

Đừng suy luận rằng `top-k` luôn tốt hơn `top-1`, hoặc experts chắc chắn có semantic role rõ ràng. Đây là choices phải đánh giá cùng model width, capacity rule, batch size, hardware, và training setup.

## 6. `total parameters`, `active parameters`, và FLOPs

Đây là nguồn gây hiểu nhầm phổ biến nhất khi đọc model card MoE.

Giả sử mỗi expert có $P_E$ parameters, có $N$ experts, và token dùng `top-k`. Expert-bank counts gần đúng là:

$$
P_{\text{expert,total}}\approx N P_E,
\qquad
P_{\text{expert,active/token}}\approx kP_E.
$$

Ví dụ: 8 experts, mỗi expert 100M parameters, `top-2`:

```text
expert total parameters       ≈ 8 × 100M = 800M
expert active parameters/token ≈ 2 × 100M = 200M
```

Nhưng đây **chỉ là expert branch**. Toàn model còn embeddings, attention projections, router, normalization, `lm_head`, và có thể dense FFN layers. Vì vậy, reported `active parameters` thường là architecture-specific convention, không phải complete cost summary.

| Quantity | Hỏi điều gì? | Không nói đầy đủ về |
|---|---|---|
| `total parameters` | Bao nhiêu weights phải lưu/load/checkpoint? | Bao nhiêu weights mỗi token chạy |
| `active parameters` | Khoảng bao nhiêu selected weights tham gia cho một token? | Attention, KV cache, routing, padding, communication |
| FLOPs/token | Bao nhiêu arithmetic work trong một configuration? | Network overhead và kernel utilization |
| End-to-end latency | Request mất bao lâu trên hệ cụ thể? | Quality hoặc model capacity |

Switch tách `total` expert capacity khỏi phần lớn expert-FFN compute per token, nhưng inactive weights không “miễn phí”: chúng vẫn chiếm memory và làm checkpoint/model loading lớn hơn.[^moe-overview-2026]

## 7. PyTorch toy implementation

Code dưới đây implement `top-1` hoặc `top-k` MoE cho tensor `(batch, sequence, d_model)`. Nó cố ý ưu tiên rõ ràng hơn performance:

- router softmax được tính ở `float32` để minh họa selective precision;
- every selected token-expert pair được gọi đúng một lần;
- outputs của một token được cộng theo gate weights;
- **không** có `expert capacity`, load-balancing loss, `all-to-all`, hay fused kernel.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class ExpertFFN(nn.Module):
    """One ordinary position-wise FFN; each instance owns different weights."""
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TopKMoE(nn.Module):
    def __init__(self, d_model: int, d_ff: int, n_experts: int, k: int):
        super().__init__()
        if not 1 <= k <= n_experts:
            raise ValueError("k must satisfy 1 <= k <= n_experts")
        self.n_experts = n_experts
        self.k = k
        self.router = nn.Linear(d_model, n_experts)
        self.experts = nn.ModuleList(
            [ExpertFFN(d_model, d_ff) for _ in range(n_experts)]
        )

    def forward(self, x: torch.Tensor):
        # x: (B, T, D); flatten positions because routing is per token.
        B, T, D = x.shape
        tokens = x.reshape(B * T, D)

        # Keep router logits/probabilities in fp32, then retain input dtype for FFNs.
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(tokens.dtype)
        top_gates, top_ids = probs.topk(self.k, dim=-1)  # both: (B*T, k)

        output = torch.zeros_like(tokens)
        for expert_id, expert in enumerate(self.experts):
            # One row exists for every (token, selected-expert) assignment.
            token_rows, k_slots = torch.where(top_ids == expert_id)
            if token_rows.numel() == 0:
                continue
            expert_output = expert(tokens[token_rows])
            weighted = top_gates[token_rows, k_slots].unsqueeze(-1) * expert_output
            output.index_add_(0, token_rows, weighted)

        # Useful observability: assignments count k times per token.
        loads = torch.bincount(top_ids.reshape(-1), minlength=self.n_experts)
        return output.reshape(B, T, D), probs, top_ids, loads
```

### Chạy và kiểm tra tối thiểu

```python
torch.manual_seed(7)
moe = TopKMoE(d_model=16, d_ff=64, n_experts=4, k=2)
x = torch.randn(3, 5, 16, requires_grad=True)  # B=3, T=5 => 15 tokens

y, probs, top_ids, loads = moe(x)
print(y.shape)             # torch.Size([3, 5, 16])
print(top_ids.shape)       # torch.Size([15, 2])
print(loads.tolist())      # assignments per expert; their sum must be 15 * 2

assert torch.allclose(probs.sum(dim=-1), torch.ones(15), atol=1e-6)
assert loads.sum().item() == 3 * 5 * 2

loss = y.square().mean()
loss.backward()
assert moe.router.weight.grad is not None
print("router gradient norm:", moe.router.weight.grad.norm().item())
```

Nếu đổi `k=1`, `top_ids` có shape `(B*T, 1)` và mỗi token có exactly one selected expert: đó là routing pattern của Switch. Code này dùng raw selected `softmax` gates, phù hợp công thức đã trình bày; nó không normalize lại top-k gates.

> [!warning] Đây không phải production MoE
> Python loop theo expert, boolean indexing, và `index_add_` là dễ đọc nhưng chậm. Production implementation cần group/pack tokens theo expert, chạy expert batches lớn, rồi restore original token order. Khi expert được shard qua devices, quy trình còn cần `all-to-all` dispatch và combine.[^moe-overview-2026]

## 8. Tại sao một router cần load balancing?

Nếu chỉ tối ưu language-model loss, router có thể gửi phần lớn tokens vào vài experts. Khi đó popular expert quá tải, experts còn lại ít nhận gradient, và capacity của whole bank bị lãng phí. Hiện tượng này thường được gọi là `expert collapse` hoặc `load imbalance`.[^moe-overview-2026]

Một Switch-style batch-level auxiliary objective dùng:

$$
f_i=\frac{1}{T}\sum_{h\in B}\mathbf{1}[\arg\max p(h)=i],
\qquad
P_i=\frac{1}{T}\sum_{h\in B}p_i(h),
$$

trong đó $f_i$ là fraction tokens thật sự routed đến expert $i$, và $P_i$ là mean router probability của expert đó. Loss phụ:

$$
L_{\text{balance}}=\alpha N\sum_{i=1}^{N}f_iP_i,
\qquad
L=L_{\text{LM}}+L_{\text{balance}}.
$$

$f_i$ có `argmax` discrete, nhưng $P_i$ có gradient qua `softmax`; do đó router vẫn nhận learning signal. Mục tiêu khuyến khích traffic cân bằng hơn, **không** bắt mọi expert học cùng function.[^moe-overview-2026]

Trong toy code, `loads` là signal quan sát đầu tiên. Log histogram theo training step; nếu một expert nhận gần toàn bộ assignments hoặc thường bằng 0, hãy kiểm tra router distribution, capacity/drop rate (nếu đã thêm), balance loss, batch size, và learning rate—không vội kết luận expert đó “tốt hơn”.

## 9. `expert capacity` và token overflow

Hardware thường cần shape/buffer bounded, nên mỗi expert có maximum token capacity gần đúng:

$$
C=\frac{T}{N}\times\text{capacity factor},
$$

với $T$ là số batch tokens và $N$ là số experts. Nếu 1,024 tokens, 8 experts, capacity factor 1.25 thì $C=160$ tokens/expert.

Khi router gửi quá $C$ tokens đến một expert, phần overflow có thể skip expert computation và đi qua residual path. Capacity factor lớn giảm dropped tokens nhưng tăng padding, memory, communication, và wasted slots.[^moe-overview-2026]

Đây giải thích vì sao toy MoE phía trên chưa đủ để kết luận performance: nó không đặt capacity, không drop token, và không mô hình hóa sparse dispatch cost.

## 10. Checklist khi đọc hoặc build MoE

1. **Baseline:** dense model thay FFN nào, ở layer nào, và expert width có thay đổi không?
2. **Routing:** `top-1` hay `top-k`? Gates có re-normalize không? Router operates per token hay per sequence?
3. **Counts:** `total` và `active parameters` có bao gồm attention/dense layers không? `k` là bao nhiêu?
4. **Balance:** có auxiliary loss, bias update, hoặc capacity rule nào? Báo cáo expert loads và drop rate không?
5. **Systems:** experts đặt trên đâu? Có `all-to-all`, padding, expert parallelism, hay small-batch utilization problem không?
6. **Evidence:** quality/throughput được so với baseline nào, trên hardware và batch configuration nào?

## 11. Bài tập tiếp theo

- Đặt `k=1` và `k=2`, so sánh `loads`, loss, và số expert calls trên cùng input.
- Viết `DenseFFN` cùng $D,D_{ff}$, rồi tính parameter counts để thấy MoE tăng `total parameters` thế nào.
- Thêm capacity $C$ vào toy code: retain only first $C$ assignments của mỗi expert, log dropped assignments, và quan sát trade-off khi đổi capacity factor.
- Thêm Switch-style `load-balancing loss` và plot `loads / loads.sum()` trong nhiều optimization steps.
- Sau khi hiểu baseline, đọc [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) để thấy fine-grained `top-k` và `shared experts`; đọc [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) trước khi suy luận từ `active parameters` sang serving cost.

## Relationships

- **Builds on:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), đặc biệt vai trò position-wise `FFN` trong một block.
- **Explains:** [Switch Transformer sparse routing](switch-transformer-sparse-routing.md) bằng data flow, router equations, toy code, và correctness checks cho người mới.
- **Prepares for:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) và [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md).
- **Extends:** Stage 7, “Sparse capacity,” của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

`Switch Transformer` facts in this course are traced to a bundled secondary overview; primary Switch paper source is not present in `raw/`. The toy code demonstrates routing mechanics only and does not substantiate quality, scalability, or production throughput. DeepSeekMoE evidence supports its own fine-grained/shared-expert configuration, not a universal superiority claim for `top-k` routing.[^moe-overview-2026][^deepseekmoe-2024]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), Sections 1–18; it cites Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022), and Shazeer et al., “Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer” (2017).

[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Sections 3–4 and Appendix A.
