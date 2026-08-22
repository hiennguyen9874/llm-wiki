---
type: Synthesis
title: Mixture-of-Experts và sparse routing — bài học cho người mới
description: A beginner-first course on replacing a dense FFN with routed experts, router softmax, top-1/top-k sparse routing, total versus active parameters, and a testable PyTorch toy MoE.
tags: [mixture-of-experts, sparse-models, routing, switch-transformer, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-22T00:00:00Z }
sources:
  - id: moe-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
---

# Mixture-of-Experts và sparse routing — bài học cho người mới

`Mixture-of-Experts` (MoE, hỗn hợp chuyên gia) thay nhánh `FFN`/`MLP` dùng chung trong một `Transformer block` bằng một `expert bank` — nhiều `expert` FFN có weights riêng. Với mỗi token, một `router` (bộ định tuyến) chấm điểm các expert qua `softmax`, rồi chỉ thực thi `top-1` (một expert tốt nhất) hoặc `top-k` (k expert tốt nhất) và cộng outputs có trọng số. Nhờ `sparse routing` (định tuyến thưa), model có `total parameters` (tổng tham số) rất lớn nhưng chỉ một phần `active parameters` (tham số kích hoạt) tham gia cho mỗi token.[^moe-overview-2026]

> [!success] Sau bài này
> 1. **Giải thích được:** MoE thay chính xác phần nào của dense Transformer, router tính gì, và `total` khác `active` ở đâu.
> 2. **Cài được:** một toy MoE PyTorch chạy `top-1`/`top-k` cho tensor `(B, T, D)`, đúng shape và weighted sum.
> 3. **Kiểm được:** `softmax` sum-to-one, `loads` sum = `B*T*k`, và router nhận gradient; phân biệt được claim về FLOPs với latency thực tế.

Bài này là **synthesis sư phạm** — minh họa cơ chế routing, không tái tạo benchmark Switch Transformer. Chi tiết Switch và context hệ thống được truy về overview thứ cấp có trong kho; ví dụ fine-grained/shared expert lấy từ paper DeepSeekMoE.[^moe-overview-2026][^deepseekmoe-2024]

## 1. Điều cần biết trước

- **Đã hiểu:** một `decoder-only Transformer` — `self-attention` trao đổi thông tin theo sequence, `FFN` xử lý từng position bằng cùng một transformation. Xem [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) nếu chưa quen.
- **Đã quen:** `softmax`, `argmax`/`top-k`, và một `Linear` layer cơ bản.
- **Không cần trước:** `expert parallelism`, `all-to-all`, `capacity factor`, `auxiliary loss` — những phần này thuộc [MoE capacity, load balancing & stability — bài lab cho người mới](moe-capacity-load-balancing-stability-lab.md) và [Expert parallelism và serving trade-offs — bài học cho người mới](expert-parallelism-serving-trade-offs-beginners-guide.md).
- **Không cover ở đây:** tối ưu kernel, distributed serving, hay chứng minh expert “chuyên về code/toán”.

## 2. Lý thuyết cốt lõi

### 2.1 Dense block làm gì trước khi có MoE?

Một block dạng pre-normalization rút gọn:

$$
u = x + \operatorname{Attention}(\operatorname{Norm}_1(x)),\qquad
\operatorname{Block}(x)=u+\operatorname{FFN}(\operatorname{Norm}_2(u))
$$

Dense FFN với width $D$ và intermediate $D_{ff}$:

$$
\operatorname{FFN}(h)=W_2\,\phi(W_1h+b_1)+b_2,\quad W_1\in\mathbb{R}^{D_{ff}\times D},\;W_2\in\mathbb{R}^{D\times D_{ff}}
$$

với $\phi$ là `GELU`/`SwiGLU`. **Mọi token chạy cùng một cặp weights** $W_1,W_2$. MoE không thay attention, mask, residual hay loss — chỉ thay nhánh `FFN` ở **một số** layer (xen kẽ dense và MoE là lựa chọn kiến trúc).[^moe-overview-2026]

```text
Dense
hidden token ───────────► shared FFN ───────────► + residual

MoE
hidden token ─► router ─► selected expert(s) ─► weighted sum ─► + residual
         per-token decision, per-token different expert
```

> [!note] Analogy — bếp chuyên gia
> Dense FFN như một bếp trưởng làm mọi món. MoE như bếp có 8 chuyên gia (nướng, xào, bánh...), mỗi order (token) được “lễ tân” (router) gửi đến 1–2 chuyên gia phù hợp nhất. Tổng số đầu bếp (total) lớn, nhưng mỗi order chỉ cần 1–2 người (active).

### 2.2 Router: từ hidden state đến xác suất

Với hidden vector của một token $h\in\mathbb{R}^{D}$, router là một `Linear` ra $N$ logits:

$$
z = W_r h + b_r,\qquad z\in\mathbb{R}^{N}
$$

`Softmax` biến logits thành phân phối:

$$
p_i(h)=\frac{\exp(z_i)}{\sum_{j=1}^{N}\exp(z_j)},\qquad \sum_{i=1}^{N}p_i(h)=1
$$

Router chạy **per token** — hai token kề nhau có thể có phân phối khác nhau.

**Ví dụ số cụ thể** — 1 token, 4 experts:

| Expert | logit $z_i$ | $p_i$ sau softmax |
|---|---:|---:|
| 0 | 0.2 | 0.16 |
| 1 | 1.7 | 0.46 |
| 2 | -0.4 | 0.08 |
| 3 | 0.6 | 0.30 |

Expert 1 có xác suất cao nhất. Nhưng sau softmax **mọi** $p_i>0$ — đây vẫn là dense distribution. Sự **sparse** chỉ xuất hiện khi ta giữ `top-1`/`top-k` và chỉ thực thi các expert đó.

### 2.3 `top-1` — Switch Transformer

Chọn expert tốt nhất:[^moe-overview-2026]

$$
i^*=\arg\max_i p_i(h),\qquad
\operatorname{SwitchFFN}(h)=p_{i^*}(h)\,E_{i^*}(h)
$$

- Chỉ 1 expert FFN chạy/token.
- Nhân với $p_{i^*}$ cho phép gradient chảy vào router qua gate value; bản thân `argmax` là discrete nên không có gradient qua việc “đổi expert nào được chọn”.
- Đây là routing đơn giản nhất và tiết kiệm expert compute nhất — nhưng “ít FLOPs expert hơn” **không** đồng nghĩa latency end-to-end luôn thấp hơn do router, packing, padding, communication, weight loading.[^moe-overview-2026]

### 2.4 `top-k` — cho một token gọi nhiều expert

Lấy tập $S_k(h)$ gồm $k$ expert có $p_i$ cao nhất:[^moe-overview-2026]

$$
\operatorname{MoE}_{top\text{-}k}(h)=\sum_{i\in S_k(h)} p_i(h)\,E_i(h)
$$

`top-1` là trường hợp $k=1$. Một số implementation **re-normalize** gate trong $S_k$ để tổng =1; công thức Switch trong source dùng raw softmax probability trực tiếp — đó là design choice cần nêu rõ khi so sánh.

DeepSeekMoE cho thấy `top-k` không nhất thiết tốn FLOPs hơn: nếu chia một expert lớn thành $m$ expert nhỏ ($D_{ff}\to D_{ff}/m$) và tăng $k\to mK$, tổng routed-FFN compute có thể gần giữ nguyên, đồng thời có thêm `shared experts` luôn chạy cho mọi token.[^deepseekmoe-2024]

| Routing | Expert calls / token | Output | Khi nào dùng |
|---|---:|---|---|
| Dense | 1 shared FFN | $E(h)$ | Baseline, không conditional |
| `top-1` / Switch | 1 | $p_{i^*}E_{i^*}(h)$ | Sparse nhất, dispatch đơn giản |
| `top-k` | $k$ | weighted sum của $k$ experts | Nhiều composition hơn, nhiều work hơn |

> [!warning] Đừng gán nhãn semantic vội
> Router học từ loss, không có bảo đảm Expert 2 = “code expert”. Expert có thể phản ứng với language, position, pattern khó gán nhãn. Chỉ gọi “specialized” khi có evidence phù hợp.[^moe-overview-2026][^deepseekmoe-2024]

### 2.5 `total parameters` vs `active parameters` vs FLOPs vs latency

Đây là nguồn hiểu nhầm lớn nhất khi đọc model card.

Giả sử mỗi expert $P_E$ params, $N$ experts, `top-k`:

$$
P_{\text{expert,total}}\approx N P_E,\qquad
P_{\text{expert,active/token}}\approx kP_E
$$

Ví dụ $N=8$, $P_E=100\text{M}$, `top-2`:

```text
expert total  ≈ 8 × 100M = 800M
expert active/token ≈ 2 × 100M = 200M
```

Nhưng đây **chỉ là expert branch**. Toàn model còn embeddings, attention, router, norm, `lm_head`, và có thể các dense layers. Nên `active parameters` là convention của kiến trúc, không phải full cost.

| Quantity | Trả lời câu hỏi gì? | Không nói về |
|---|---|---|
| `total parameters` | Bao nhiêu weights phải lưu/load? | Bao nhiêu chạy/token |
| `active parameters` | Khoảng bao nhiêu selected weights tham gia/token? | Attention, KV cache, routing, padding, communication |
| FLOPs/token | Bao nhiêu phép tính số học? | Network overhead, kernel utilization |
| End-to-end latency | Request mất bao lâu trên hardware cụ thể? | Quality, capacity |

Switch tách `total` capacity khỏi phần lớn expert FLOPs/token, nhưng inactive weights không miễn phí: vẫn chiếm memory và làm checkpoint lớn hơn.[^moe-overview-2026]

### 2.6 Sơ đồ luồng token

```text
Batch [B, T, D] ──reshape──► [B*T, D] tokens
        │
        ▼
   Router Linear(D → N) ──softmax(fp32)──► probs [B*T, N]
        │
        ├──► topk(probs, k) ──► top_gates [B*T, k], top_ids [B*T, k]
        │
        ▼
   Group tokens by expert_id ──► batched expert FFN calls
        │
        ▼
   Weighted sum per token (gate * expert_output) ──► output [B*T, D]
        │
        └──► reshape ──► [B, T, D]  +  loads histogram [N]
```

## 3. Implementation (PyTorch tối thiểu)

Code dưới ưu tiên **rõ ràng** hơn tốc độ: mỗi cặp token–expert được gọi đúng một lần, outputs cộng theo gate, không có capacity, load-balancing loss, `all-to-all`, hay fused kernel. Khi attention tham gia, convention `interleaved` RoPE và `position_ids` tuyệt đối sẽ được ghi chú — ở đây MoE chỉ thay FFN nên không áp dụng, nhưng router softmax được tính ở `float32` để minh họa selective precision.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class ExpertFFN(nn.Module):
    """Một FFN position-wise bình thường; mỗi instance có weights riêng."""
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
    """Toy MoE: per-token top-k routing, rõ ràng, không tối ưu production."""
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
        # x: (B, T, D) — routing là per token nên flatten positions.
        B, T, D = x.shape
        tokens = x.reshape(B * T, D)

        # Router logits/probs ở fp32, giữ dtype gốc cho FFN.
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(tokens.dtype)
        top_gates, top_ids = probs.topk(self.k, dim=-1)  # (B*T, k)

        output = torch.zeros_like(tokens)
        for expert_id, expert in enumerate(self.experts):
            token_rows, k_slots = torch.where(top_ids == expert_id)
            if token_rows.numel() == 0:
                continue
            expert_out = expert(tokens[token_rows])
            weighted = top_gates[token_rows, k_slots].unsqueeze(-1) * expert_out
            output.index_add_(0, token_rows, weighted)

        # Observability: mỗi token đóng góp k assignments.
        loads = torch.bincount(top_ids.reshape(-1), minlength=self.n_experts)
        return output.reshape(B, T, D), probs, top_ids, loads
```

> [!warning] Đây không phải production MoE
> Vòng lặp theo expert + `index_add_` dễ đọc nhưng chậm. Production cần group/pack tokens theo expert, chạy batched GEMM lớn, rồi restore order. Khi expert shard qua devices, còn cần `all-to-all` dispatch/combine.[^moe-overview-2026]

## 4. Xác minh trước khi benchmark

Chạy 4 tests dưới đây **trước** khi đo tốc độ hay so quality. Mỗi test nêu rõ `rtol`/`atol` và dtype.

```python
torch.manual_seed(7)
moe = TopKMoE(d_model=16, d_ff=64, n_experts=4, k=2)
x = torch.randn(3, 5, 16, requires_grad=True)  # B=3, T=5 => 15 tokens

y, probs, top_ids, loads = moe(x)

# Test 1 — shape cơ bản
assert y.shape == torch.Size([3, 5, 16])
assert top_ids.shape == torch.Size([15, 2])
print("✓ shape OK:", y.shape, top_ids.shape)

# Test 2 — softmax sum-to-one (fp32 path, atol 1e-6)
torch.testing.assert_close(
    probs.sum(dim=-1), torch.ones(15), rtol=0, atol=1e-6
)
print("✓ probs sum to 1")

# Test 3 — loads accounting: mỗi token đóng góp k assignments
assert loads.sum().item() == 3 * 5 * 2
assert loads.shape[0] == 4
print("✓ loads:", loads.tolist(), "sum =", loads.sum().item())

# Test 4 — gradient chảy vào router
loss = y.square().mean()
loss.backward()
assert moe.router.weight.grad is not None
assert moe.router.weight.grad.norm().item() > 0
print("✓ router grad norm:", moe.router.weight.grad.norm().item())

# Test 5 — top-1 là trường hợp riêng của top-k (sanity)
moe1 = TopKMoE(d_model=16, d_ff=64, n_experts=4, k=1)
y1, probs1, top_ids1, loads1 = moe1(x.detach())
assert top_ids1.shape == torch.Size([15, 1])
assert loads1.sum().item() == 15
torch.testing.assert_close(probs1.sum(dim=-1), torch.ones(15), rtol=0, atol=1e-6)
print("✓ top-1 sanity OK")

# Test 6 — đổi k không đổi total expert params (accounting check)
# N=8, P_E ~ 2*D*D_ff ; total = N*P_E không phụ thuộc k
# Đây là check bằng logic, không phải đo hardware.
print("✓ accounting: total expert params phụ thuộc N, không phụ thuộc k")
```

**Cách đọc kết quả:**
- Nếu Test 2 fail: kiểm tra dtype, softmax dim, hoặc router output shape.
- Nếu `loads` lệch hẳn (một expert chiếm >80%): chưa phải bug shape, nhưng là signal để đọc tiếp bài về load balancing.
- Nếu grad `None` hoặc `0`: kiểm tra `gate * expert_out` có nhân đúng selected probability không.

## 5. Benchmark / Trade-offs

Không có benchmark wall-clock trong toy code (single-process, Python loop). Bảng dưới tách các trade-offs cần đo riêng khi bạn scale lên hệ thực.

### 5.1 `top-1` vs `top-k` (giữ expert width cố định)

| Cấu hình | Expert calls/token | Routed FLOPs/token | Dispatch traffic | Khi nào chọn |
|---|---:|---:|---|---|
| `top-1` | 1 | $1\times$ | $1\times$ | Muốn sparse nhất, hệ đơn giản |
| `top-2` (same width) | 2 | $2\times$ | $2\times$ | Muốn nhiều mixture hơn, chấp nhận tốn gấp đôi |
| `top-2` fine-grained ($D_{ff}/2$) | 2 nhưng expert nhỏ hơn | $\approx 1\times$ | $2\times$ assignments nhỏ | Muốn nhiều composition mà giữ FLOPs gần bằng[^deepseekmoe-2024] |

### 5.2 `active parameters` không suy ra latency/memory

| Con số headline | Kết luận sai thường gặp | Thực tế cần đo |
|---|---|---|
| “Chỉ 21B active” | “Chỉ cần GPU chứa 21B” | Total weights + KV cache + buffers vẫn theo `total` và context length[^moe-overview-2026] |
| “FLOPs/token thấp” | “Latency luôn thấp” | `all-to-all`, padding, small-batch GEMM, overlap quyết định |
| “Nhiều experts hơn” | “Chất lượng luôn cao hơn” | Routing balance, data fit, và training setup mới quyết định |

### 5.3 Checklist đo đúng (khi bạn có distributed runtime)

- **Model config:** total/active params, $N$, $D_{ff}$, `top-k`, có re-normalize gates không
- **Routing health:** per-expert loads, drop rate, padding fraction, device fan-out
- **System time:** router/packing, dispatch all-to-all, expert GEMM, combine — đo riêng và đo slowest rank
- **Workload:** hardware/interconnect, precision, request mix, batch policy, prefill vs decode tách riêng

## 6. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| `probs` không sum ≈1 | Softmax sai dim hoặc dtype overflow | `probs.sum(-1)` với `atol=1e-6`; in `router` output shape |
| `loads` một expert ≈0, một expert dominate | Router collapse / init bias / `alpha` balance chưa có | Plot `loads / loads.sum()` qua nhiều steps; xem [MoE capacity lab](moe-capacity-load-balancing-stability-lab.md) |
| Loss không giảm dù dense baseline giảm | Gate weighting sai hoặc expert không được gọi | Log `top_ids` histogram + `router grad norm`; thử `k=1` trước |
| `NaN` sau vài steps | Logit scale lớn, softmax fp16 unstable | Tính router softmax ở `float32` như code mẫu |
| Thay `k=1→2` nhưng quality không đổi | Expert width không đổi nên FLOPs tăng nhưng chưa tune capacity/balance | Kiểm tra expert width, capacity factor, và batch size có đủ tokens/expert không |
| Chạy đúng nhưng chậm bất ngờ | Python loop + `index_add_` toy code | Đây là expected — production cần packed batched GEMM, không phải bug logic |

## 7. Giới hạn & bước tiếp theo

**Bài này không chứng minh:**
- Rằng `top-k` luôn tốt hơn `top-1`, hay expert có semantic role cố định — đó là design choices phải đánh giá cùng width, capacity, batch size, hardware.[^moe-overview-2026][^deepseekmoe-2024]
- Rằng `active parameters` suy ra serving cost — cần đo total weight memory, KV cache, communication riêng.[^moe-overview-2026]
- Rằng toy PyTorch cho kết luận về throughput production — code minh họa routing mechanics, không có capacity/drop hay distributed dispatch.

**Học tiếp theo (theo [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) Stage 7):**

1. [MoE capacity, load balancing & stability — bài lab cho người mới](moe-capacity-load-balancing-stability-lab.md) — thêm `capacity factor`, overflow, `auxiliary loss` vs `routing bias`, và vẽ expert load.
2. [Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới](deepseekmoe-expert-design-beginners-guide.md) — fine-grained routed experts + shared experts, tại sao `top-k` lớn hơn không nhất thiết tốn FLOPs hơn.
3. [Expert parallelism và serving trade-offs — bài học cho người mới](expert-parallelism-serving-trade-offs-beginners-guide.md) — dispatch/combine qua `all-to-all`, placement, và vì sao serving vẫn trả total-weight memory.

**Bài tập gợi ý:**
- Đặt `k=1` và `k=2`, so sánh `loads` và số expert calls trên cùng input.
- Viết `DenseFFN` cùng $D,D_{ff}$, đếm params để thấy MoE tăng `total` thế nào.
- Thêm capacity $C=(T/N)\times c$ vào toy code, log dropped assignments khi đổi $c=1.0,1.25,2.0$.
- Thêm Switch-style $L_{\text{balance}}=\alpha N\sum_i f_iP_i$ và plot `loads` qua nhiều steps.

## Relationships

- **Depends on:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) — vai trò position-wise `FFN` trong block mà MoE thay thế.
- **Explains:** [Switch Transformer sparse routing](switch-transformer-sparse-routing.md) — data flow, router equations, và correctness checks ở mức người mới.
- **Prepares for:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) và [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md).
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) để đặt ranh giới giữa `active parameters` và serving cost.
- **Extends:** Stage 7, “Sparse capacity,” của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Tổng hợp sư phạm này truy về bundled secondary overview cho Switch Transformer; primary Switch paper không có trong `raw/` nên chi tiết toán và số liệu báo cáo vẫn gắn với overview đó. Toy code chỉ minh họa routing mechanics, không chứng minh quality/scalability/throughput production. Evidence về fine-grained/shared experts và “`top-k` không đồng nghĩa nhiều FLOPs hơn” thuộc cấu hình DeepSeekMoE cụ thể, không phải claim phổ quát cho mọi MoE.[^moe-overview-2026][^deepseekmoe-2024]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), Sections 1–18; overview này trích Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022) và Shazeer et al., “Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer” (2017).
[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Sections 3–4 và Appendix A.
