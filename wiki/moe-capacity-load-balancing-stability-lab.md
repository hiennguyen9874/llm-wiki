---
type: Synthesis
title: "MoE capacity, load balancing & stability — bài lab cho người mới"
description: A beginner-first MoE lab that makes capacity factor, token dropping, auxiliary loss and routing bias observable through per-expert load plots and verifiable PyTorch code.
tags: [mixture-of-experts, load-balancing, routing, capacity, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-23T00:00:00Z }
sources:
  - id: switch-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# MoE `capacity`, `load balancing` & `stability` — bài lab cho người mới

`MoE` (Mixture-of-Experts) tiết kiệm `expert-FFN` compute chỉ khi `router` chia token đều vào các `expert` có `capacity` (sức chứa) cố định. Nếu một `expert` bị dồn quá nhiều token, hệ thống phải `pad` (đệm chỗ trống), `drop` (bỏ bớt assignment), hoặc để một device thành `straggler` (nút thắt cổ chai). Nếu expert khác không được chọn, nó thiếu `training signal` và không học được gì. Bài lab này biến những ý đó thành thứ đo được: đếm `offered load` (nhu cầu router muốn gửi) vs `accepted load` (thực tế được chạy), tính `capacity factor`, quan sát `overflow`, so sánh hai cơ chế cân bằng `auxiliary loss` và `routing bias`, và vẽ `expert-load` qua nhiều step.[^switch-overview-2026][^deepseekmoe-2024][^deepseek-v2-2024][^deepseek-v3-2024]

> [!success] Sau bài này bạn sẽ
> 1. **Giải thích được:** tại sao `capacity factor` là budget (ngân sách chỗ) chứ không phải cách sửa router lệch; đọc `offered` vs `accepted` không nhầm lẫn.
> 2. **Tính được:** `capacity` cho `top-k` bất kỳ; phân biệt `assignment drop` với `fully-dropped token`; hiểu trade-off khi tăng/giảm `capacity factor`.
> 3. **Cài & kiểm được:** một `CapacityAwareTopKMoE` tối thiểu trong PyTorch, log `drop rate`/`router entropy`/`expert share`, chạy 6 test với `torch.testing.assert_close`, và vẽ hai panel `offered` vs `accepted`.

Bài này nối tiếp [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) (router và `top-k` cơ bản). Code ưu tiên **dễ quan sát và đúng logic**, không phải `fused kernel` hay `distributed MoE` production.

## 1. Điều cần biết trước

- **Đã hiểu:** một `decoder block` — `attention` trao đổi thông tin theo sequence, `FFN` xử lý từng position. [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md)
- **Đã quen:** `softmax`, `top-k`, `Linear(D → N)` và cách đọc `loss`. Bài trước [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) đã cài `TopKMoE` không có capacity.
- **Chưa cần:** `expert parallelism`, `all-to-all`, `capacity factor`, `auxiliary loss` — chính là nội dung bài này.
- **Không cover:** kernel tối ưu, sharding qua nhiều GPU, hay chứng minh expert “chuyên về code”.

> [!note] Analogy — căng-tin có N quầy
> Hãy tưởng tượng $T$ sinh viên (token) mỗi người cầm $K$ phiếu ăn. Router là người hướng dẫn chỉ mỗi sinh viên tới $K$ quầy (expert) phù hợp nhất. Mỗi quầy chỉ có $C$ chỗ ngồi (`capacity`). `Offered load` = số phiếu muốn tới quầy. `Accepted load` = số phiếu thực sự có chỗ. Phiếu dư = `overflow` và bị `drop` theo policy. Căng-tin cân bằng khi mọi quầy đều có khách, không quầy nào quá tải, không quầy nào vắng.

## 2. Lý thuyết cốt lõi

### 2.1 Từ $T$ token tới $TK$ assignments

Với $T$ token trong batch, $N$ routed experts, `top-k` $K$, router tạo đúng $TK$ **token–expert assignments** *trước* khi áp capacity.

```text
Ví dụ: T=12, N=4, K=2 → 24 assignments
Token 0 → expert 3, 1
Token 1 → expert 3, 0
...
```

Nếu router chia đều hoàn hảo, mỗi expert nhận trung bình:

$$
\mathbb{E}[\text{assignments/expert}] = \frac{TK}{N}
$$

Điểm dễ nhầm: với `top-1` ($K=1$) công thức quen thuộc là $T/N$. Với `top-k`, nhớ nhân thêm $K$. Một số hệ thống định nghĩa capacity theo token hoặc theo device — luôn kiểm tra definition trước khi so sánh số liệu.[^switch-overview-2026]

### 2.2 Ba loại load — đừng chỉ nhìn một

| Metric | Hỏi điều gì? | Tính cho expert $i$ |
|---|---|---|
| `offered load` | Router **muốn** gửi bao nhiêu? | Count của $i$ trong `top-k` **trước** capacity |
| `accepted load` | Expert **thực sự chạy** bao nhiêu? | Count còn lại **sau** capacity/`drop` |
| `load share` | Expert chiếm bao nhiêu traffic? | `load / total assignments` |

> [!warning] Chỉ nhìn `accepted` sẽ bị lừa
> Capacity có thể cắt đỉnh (peak) của expert quá tải, làm biểu đồ `accepted` trông cân bằng dù router vẫn dồn demand vào một expert. Luôn vẽ **cả offered lẫn accepted**.

Ví dụ nhỏ $T=8$, $N=4$, $K=1$:

```text
top_ids (offered): [0,0,0,0, 1,2,3,1]  → offered = [4,2,1,1]
capacity C=2                         → accepted = [2,2,1,1]  (expert 0 bị cắt từ 4→2)
```

Panel `offered` lộ collapse, panel `accepted` che nó đi — gap chính là chi phí overflow.

### 2.3 `Capacity factor`, `overflow` và `token dropping`

Để giữ tensor shape cố định, mỗi expert được pre-allocate $C$ slots:[^switch-overview-2026]

$$
C = \left\lceil \frac{TK}{N}\times c \right\rceil
$$

với $c$ là `capacity factor`. Với `top-1` công thức trở về $\lceil (T/N)c\rceil$ quen thuộc kiểu Switch.

**Ví dụ tính tay:** $T=1024$, $N=8$, $K=2$, $c=1.25$:

$$
C = \left\lceil \frac{1024\times2}{8}\times1.25\right\rceil = 320
$$

Tổng capacity = $8\times320=2560$ slots, trong khi batch chỉ đề xuất $2048$ assignments — phần dư $512$ là buffer chịu dao động.

| `capacity factor` $c$ | Lợi ích | Chi phí / rủi ro |
|---|---|---|
| Nhỏ (≈1.0) | Ít `padding`, ít compute thừa | `Overflow`/`drop` tăng khi router lệch hoặc batch nhỏ |
| Lớn (≈1.5–2.0) | Ít assignment bị drop | Lãng phí memory, communication, compute cho slots trống |
| Vô hạn (toy code) | Dễ viết | Không mô phỏng bounded buffer của hệ thực |

Khi offered vượt $C$, đó là `overflow`. Policy đơn giản: giữ các assignments có `gate`/`affinity` cao hơn, drop phần còn lại. DeepSeek-V2 mô tả `device-level token dropping` — giới hạn average device budget ở $c=1.0$, drop token có affinity thấp nhất trên device đó; balance losses chỉ khuyến khích chứ không bảo đảm cân bằng tuyệt đối.[^deepseek-v2-2024]

> [!warning] "Dropped token" cần định nghĩa chính xác
> - `top-1`: drop assignment ≈ token không nhận expert branch (chỉ còn residual).
> - `top-k`: token có thể mất **một phần** experts (`partial drop`) hoặc mất **tất cả** (`fully dropped`). Hãy log `assignment drop rate` và `fully-dropped-token rate` riêng.

`Token dropping` là van an toàn cho bounded work, không phải thuốc chữa `routing collapse`. Drop cao nghĩa model đang train trên computation khác với router intended; tăng $c$ chỉ che demand concentration và tăng systems cost.

### 2.4 `Routing collapse` là gì?

`Routing collapse` = router liên tục chọn chỉ 1–2 experts, nhiều experts gần như không nhận token. Hệ quả: expert vắng khách thiếu training, và imbalance giữa devices tạo bottleneck.[^deepseekmoe-2024][^deepseek-v3-2024]

```text
8 experts, top-1, share lý tưởng: [12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5] %
share khi collapse:             [78.0,  9.0,  4.0,  3.0,  2.0,  2.0,  1.0,  1.0] %
```

Expert 0 không nhất thiết “giỏi hơn” — có thể chỉ có lợi thế logit ban đầu. Vì token đi qua nó nhiều, nó nhận nhiều gradient và giỏi lên nhanh hơn → vòng lặp phản hồi làm lệch kéo dài.

**Signals chẩn đoán (quan sát qua nhiều steps, không phải một batch):**

| Signal | Healthy (không phải yêu cầu cứng) | Warning sign |
|---|---|---|
| `offered load share` | Không expert nào chiếm phần lớn kéo dài | 1/few experts dominate; nhiều expert ≈0 |
| `accepted` vs `drop rate` | Accepted ≈ offered, overflow thấp | Offered peak bị cắt, drop tăng |
| `max load / mean load` | Gần 1 | Tăng dai dẳng, vượt $c$ |
| `router entropy` | Không lao dốc | Phân phối rất peaked hoặc dao động mạnh |
| Expert grad norm | Nhiều experts có signal | Nhiều experts luôn ≈0 |
| Per-device load | Aggregate work tương đối đều | Một device straggle dù experts khác rảnh |

`Router entropy` chỉ là signal phụ — router có thể entropy cao nhưng `top-k` vẫn lặp cùng experts; ngược lại uneven use có thể hợp lý theo domain.

### 2.5 Hai cách control load — khác nhau ở đâu?

#### A. `Auxiliary loss` — thêm áp lực vào training objective

Gọi $a_i$ là offered assignments của expert $i$:

$$
f_i=\frac{a_i}{TK},\qquad
P_i=\frac{1}{T}\sum_{t=1}^{T}p_{i,t},\qquad
L_{\text{balance}}=\alpha N\sum_{i=1}^{N}f_iP_i,\quad L=L_{\text{task}}+L_{\text{balance}}
$$

$f_i,P_i$ đều sum-to-1. Khi uniform $f_i=P_i=1/N$ → $L_{\text{balance}}=1$; khi concentrate → loss lớn hơn. $f_i$ discrete nhưng $P_i$ differentiable qua `softmax` nên router vẫn nhận gradient. DeepSeekMoE dùng expert-level và device-level balance losses riêng.[^deepseekmoe-2024]

`alpha` là trade-off: quá nhỏ → collapse vẫn xảy ra; quá lớn → ép uniform dù specialization hữu ích, làm task quality kém. Luôn log cả task loss và routing metrics khi tune.

#### B. `Routing bias` — đổi cách chọn, không đổi trực tiếp main loss

DeepSeek-V3 dùng bias $b_i$ cho selection:[^deepseek-v3-2024]

$$
\text{selected}(t)=\operatorname{TopK}_i(s_{i,t}+b_i)
$$

nhưng gate weight để combine outputs vẫn tính từ affinity gốc $s_{i,t}$ (không cộng bias). Cuối mỗi step: overloaded → $b_i\leftarrow b_i-\gamma$, underloaded → $b_i\leftarrow b_i+\gamma$.

```text
selection score:  affinity + routing bias  → expert nào được CHỌN?
mixture weight:   affinity (gốc)          → expert đó đóng góp BAO NHIÊU?
```

Bias như bộ điều khiển feedback cho eligibility, không trực tiếp nói output expert phải lớn. V3 vẫn giữ một sequence-wise auxiliary loss rất nhỏ ($\alpha=0.0001$) — “auxiliary-loss-free” không nghĩa mọi balance loss = 0.[^deepseek-v3-2024]

| Cơ chế | Tác động chính | Ưu điểm | Giới hạn |
|---|---|---|---|
| `auxiliary loss` | Gradient của router weights | Objective differentiable | `alpha` lớn cạnh tranh với task loss |
| `routing bias` | Eligibility của discrete `top-k` | Feedback trực tiếp trên actual assignments | `gamma` và delay/noise của batch stats cần tune |
| Device/rank balancing | Aggregate work & communication | Giảm straggler, `all-to-all` imbalance | Không bảo đảm từng expert được train đều |
| Capacity/drop policy | Bounded work | Bảo vệ memory/latency | Không sửa offered-load concentration |

Sơ đồ luồng (per step):

```text
tokens [B*T, D] → router → probs [B*T, N] ─┬─→ + bias → top-k → offered load
                                          └─→ gate (probs gốc) → weighted expert outputs
offered ──capacity C──► accepted (giữ gate cao) → drop rate, entropy
                      │
                      └─► bias update (gamma) hoặc auxiliary loss (alpha)
```

## 3. Implementation (PyTorch tối thiểu)

Code này làm đúng 5 việc: `top-k` per token, đếm `offered` trước capacity và `accepted` sau capacity, giữ assignment có gate cao khi overflow, tính `auxiliary_loss` từ pre-selection probs, và cho phép update `routing_bias` dựa trên **offered** load. Cố ý bỏ `all-to-all`, padding kernels, sharding, shared experts.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class ExpertFFN(nn.Module):
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class CapacityAwareTopKMoE(nn.Module):
    """Educational reference: transparent metrics, not a fast MoE kernel."""
    def __init__(
        self, d_model: int, d_ff: int, n_experts: int, k: int,
        capacity_factor: float = 1.25,
    ):
        super().__init__()
        if not 1 <= k <= n_experts:
            raise ValueError("k must satisfy 1 <= k <= n_experts")
        if capacity_factor <= 0:
            raise ValueError("capacity_factor must be positive")
        self.n_experts, self.k = n_experts, k
        self.capacity_factor = capacity_factor
        self.router = nn.Linear(d_model, n_experts)
        self.experts = nn.ModuleList(
            [ExpertFFN(d_model, d_ff) for _ in range(n_experts)]
        )
        # Controller state: chỉ ảnh hưởng selection, không đổi output gate.
        self.register_buffer("routing_bias", torch.zeros(n_experts))

    def capacity(self, n_tokens: int) -> int:
        # Đơn vị là assignment, nên top-k phải nhân K.
        return math.ceil(n_tokens * self.k * self.capacity_factor / self.n_experts)

    def forward(self, x: torch.Tensor):
        B, T, D = x.shape
        n_tokens = B * T
        tokens = x.reshape(n_tokens, D)

        # Router ở fp32 là lựa chọn stability cho toy lab.
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(tokens.dtype)
        selection_scores = probs + self.routing_bias.to(tokens.dtype)
        _, top_ids = selection_scores.topk(self.k, dim=-1)  # (n_tokens, k)

        # Gate lấy từ probs gốc, rồi normalize trong selected set.
        raw_gates = probs.gather(1, top_ids)
        gates = raw_gates / raw_gates.sum(dim=-1, keepdim=True).clamp_min(1e-9)

        offered_load = torch.bincount(top_ids.reshape(-1), minlength=self.n_experts)
        accepted_load = torch.zeros_like(offered_load)
        accepted = torch.zeros_like(top_ids, dtype=torch.bool)
        output = torch.zeros_like(tokens)
        cap = self.capacity(n_tokens)

        for expert_id, expert in enumerate(self.experts):
            token_rows, slots = torch.where(top_ids == expert_id)
            if token_rows.numel() == 0:
                continue
            # Khi overflow, giữ assignments có gate gốc cao nhất.
            order = gates[token_rows, slots].argsort(descending=True)
            keep = order[:cap]
            kept_rows, kept_slots = token_rows[keep], slots[keep]
            accepted[kept_rows, kept_slots] = True
            accepted_load[expert_id] = kept_rows.numel()

            values = expert(tokens[kept_rows])
            weighted = gates[kept_rows, kept_slots].unsqueeze(-1) * values
            output.index_add_(0, kept_rows, weighted)

        # Token không có accepted assignment thì MoE branch = 0;
        # residual của block (bên ngoài module) vẫn đưa token đi tiếp.
        assignment_drop_rate = 1.0 - accepted.float().mean()
        fully_dropped_token_rate = 1.0 - accepted.any(dim=-1).float().mean()
        entropy = -(probs * probs.clamp_min(1e-9).log()).sum(dim=-1).mean()
        stats = {
            "probs": probs,
            "top_ids": top_ids,
            "offered_load": offered_load,
            "accepted_load": accepted_load,
            "capacity": cap,
            "assignment_drop_rate": assignment_drop_rate,
            "fully_dropped_token_rate": fully_dropped_token_rate,
            "router_entropy": entropy,
        }
        return output.reshape(B, T, D), stats

    def auxiliary_loss(self, probs: torch.Tensor, top_ids: torch.Tensor) -> torch.Tensor:
        """Switch-style top-k adaptation; cộng alpha * kết quả này vào task loss."""
        offered = torch.bincount(top_ids.reshape(-1), minlength=self.n_experts)
        f = offered.float() / offered.sum().clamp_min(1)  # offered share
        P = probs.float().mean(dim=0)                     # mean share (differentiable)
        return self.n_experts * (f * P).sum()

    @torch.no_grad()
    def update_routing_bias(self, offered_load: torch.Tensor, gamma: float):
        """V3-inspired sign update, simplified cho lab."""
        target = offered_load.sum().float() / self.n_experts
        direction = torch.sign(target - offered_load.float())
        self.routing_bias.add_(gamma * direction)
        self.routing_bias.sub_(self.routing_bias.mean())  # giữ relative bias
```

> [!note] Design choice được nêu rõ
> Code normalize gate **trước capacity**, sau đó không re-normalize khi token bị `partial drop`. Nhờ vậy output branch giảm khi assignment bị drop và metric dễ diễn giải. Production có thể chọn policy khác — đổi mà không log rõ sẽ làm so sánh misleading.

## 4. Xác minh trước khi benchmark

Chạy 6 test dưới đây **trước** khi đo tốc độ hay so quality. Mỗi test nêu `rtol`/`atol` và dtype.

```python
torch.manual_seed(7)
moe = CapacityAwareTopKMoE(d_model=16, d_ff=64, n_experts=4, k=2, capacity_factor=1.0)
x = torch.randn(3, 5, 16, requires_grad=True)  # 15 tokens, 30 assignments

y, stats = moe(x)

# Test 1 — shape cơ bản
assert y.shape == torch.Size([3, 5, 16])
assert stats["top_ids"].shape == torch.Size([15, 2])
print("✓ Test 1 shape OK:", y.shape, stats["top_ids"].shape)

# Test 2 — softmax sum-to-one (fp32 path, atol 1e-6)
torch.testing.assert_close(
    stats["probs"].sum(dim=-1), torch.ones(15), rtol=0, atol=1e-6
)
print("✓ Test 2 probs sum to 1")

# Test 3 — loads accounting
assert stats["offered_load"].sum().item() == 3 * 5 * 2  # T*K
assert (stats["accepted_load"] <= stats["capacity"]).all()
assert stats["accepted_load"].sum() <= stats["offered_load"].sum()
print("✓ Test 3 loads:", stats["offered_load"].tolist(),
      "accepted:", stats["accepted_load"].tolist(),
      "capacity:", stats["capacity"])

# Test 4 — capacity formula cho top-k (assignment unit)
# C = ceil(T*K/N * c) = ceil(15*2/4 * 1.0) = 8
torch.testing.assert_close(
    torch.tensor(stats["capacity"]), torch.tensor(8), rtol=0, atol=0
)
print("✓ Test 4 capacity = 8 đúng công thức TK/N")

# Test 5 — gradient chảy vào router (qua gate, không qua argmax)
loss = y.square().mean() + 0.01 * moe.auxiliary_loss(stats["probs"], stats["top_ids"])
loss.backward()
assert moe.router.weight.grad is not None
assert moe.router.weight.grad.norm().item() > 0
print("✓ Test 5 router grad norm:", moe.router.weight.grad.norm().item())

# Test 6 — đổi K thay đổi accounting, không đổi total expert params
moe1 = CapacityAwareTopKMoE(d_model=16, d_ff=64, n_experts=4, k=1, capacity_factor=1.0)
y1, s1 = moe1(x.detach())
assert s1["offered_load"].sum().item() == 15          # T*1
assert stats["offered_load"].sum().item() == 30        # T*2
print("✓ Test 6 K=1→2: offered 15→30, total expert params phụ thuộc N không phụ thuộc K")

# Bonus — kiểm tra drop semantics
print(f"  assignment drop: {stats['assignment_drop_rate'].item():.3f}")
print(f"  fully-dropped token: {stats['fully_dropped_token_rate'].item():.3f}")
```

**Cách đọc kết quả:**
- Test 2 fail → kiểm tra `softmax` dim, dtype, hoặc router shape.
- `loads` một expert dominate → chưa phải bug shape, nhưng là signal để đọc phần routing collapse.
- Grad `None`/0 → kiểm tra `gate * expert_out` có nhân đúng selected probability không.

## 5. Lab: vẽ `load` của mỗi expert

Một batch đơn lẻ luôn noisy — hãy aggregate nhiều steps. Target dưới là synthetic `tanh(x.roll)` chỉ để kiểm instrumentation, không phải LM training.

```python
import matplotlib.pyplot as plt


def run_lab(use_aux_loss: bool, use_bias_controller: bool, steps: int = 300):
    torch.manual_seed(0)
    moe = CapacityAwareTopKMoE(d_model=32, d_ff=96, n_experts=8, k=1, capacity_factor=1.0)
    # Tạo lợi thế ban đầu để ca "no balance" dễ chẩn đoán.
    with torch.no_grad():
        moe.router.bias[0] = 2.0

    opt = torch.optim.AdamW(moe.parameters(), lr=3e-3)
    history = {key: [] for key in [
        "offered", "accepted", "capacity", "assign_drop", "full_drop", "entropy", "task", "balance"
    ]}

    for step in range(steps):
        x = torch.randn(16, 8, 32)       # T = 128 tokens / step
        target = torch.tanh(x.roll(1, dims=-1))
        y, stats = moe(x)

        task_loss = F.mse_loss(y, target)
        balance = moe.auxiliary_loss(stats["probs"], stats["top_ids"])
        loss = task_loss + (0.05 * balance if use_aux_loss else 0.0)

        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if use_bias_controller:
            moe.update_routing_bias(stats["offered_load"], gamma=0.01)

        history["offered"].append(stats["offered_load"].detach().cpu())
        history["accepted"].append(stats["accepted_load"].detach().cpu())
        history["capacity"].append(stats["capacity"])
        history["assign_drop"].append(stats["assignment_drop_rate"].item())
        history["full_drop"].append(stats["fully_dropped_token_rate"].item())
        history["entropy"].append(stats["router_entropy"].item())
        history["task"].append(task_loss.item())
        history["balance"].append(balance.item())

    return moe, history


_, no_balance = run_lab(use_aux_loss=False, use_bias_controller=False)
_, controlled = run_lab(use_aux_loss=True, use_bias_controller=True)
```

### Plot 1: `load share` từng expert theo step

```python
def plot_expert_load(history, title):
    offered = torch.stack(history["offered"]).float()      # (steps, N)
    accepted = torch.stack(history["accepted"]).float()
    offered_share = offered / offered.sum(dim=1, keepdim=True).clamp_min(1)
    accepted_share = accepted / accepted.sum(dim=1, keepdim=True).clamp_min(1)
    steps, n_experts = offered_share.shape

    fig, axes = plt.subplots(1, 2, figsize=(14, 4), sharey=True)
    for e in range(n_experts):
        axes[0].plot(offered_share[:, e], label=f"expert {e}")
        axes[1].plot(accepted_share[:, e], label=f"expert {e}")
    for ax, label in zip(axes, ["offered load", "accepted load"]):
        ax.axhline(1 / n_experts, color="black", linestyle="--", label="uniform target")
        ax.set(title=label, xlabel="optimizer step", ylabel="assignment share")
        ax.grid(alpha=0.25)
    axes[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.suptitle(title)
    plt.tight_layout()


plot_expert_load(no_balance, "A. No load balancing")
plot_expert_load(controlled, "B. Auxiliary loss + routing-bias controller")
plt.show()
```

**Cách đọc:** panel `offered` mỗi line lý tưởng dao động quanh $1/N$. Nếu expert 0 duy trì cao, nhiều experts bám 0 → collapsed. Panel `accepted` có thể trông bớt lệch vì capacity cắt đỉnh. Nếu hai panel khác xa nhau, capacity đang **che** overload, không phải router đã cân.

### Plot 2: trung bình load vs capacity

```python
def plot_summary(history, title):
    offered = torch.stack(history["offered"]).float()
    accepted = torch.stack(history["accepted"]).float()
    n_experts = offered.shape[1]
    mean_offered = offered.mean(dim=0)
    mean_accepted = accepted.mean(dim=0)
    mean_capacity = torch.tensor(history["capacity"], dtype=torch.float32).mean()
    capacity = mean_accepted.new_full((n_experts,), mean_capacity)

    x = torch.arange(n_experts)
    plt.figure(figsize=(10, 4))
    plt.bar(x - 0.2, mean_offered, width=0.4, label="mean offered")
    plt.bar(x + 0.2, mean_accepted, width=0.4, label="mean accepted")
    plt.plot(x, capacity, "k--", label="observed capacity ceiling")
    plt.xticks(x, [f"expert {i}" for i in x])
    plt.ylabel("assignments / step")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


plot_summary(no_balance, "A. Offered vs accepted (no balance)")
plot_summary(controlled, "B. Offered vs accepted (controlled)")
```

Lưu `stats["capacity"]` mỗi step trong lab production thay vì reconstruct. `mean offered > capacity` → overflow; `mean accepted` sát capacity trong khi offered cao hơn → drop policy đang active thường xuyên.

## 6. Benchmark / Trade-offs — đo gì, không kết luận gì vội

### 6.1 Metrics có thể hành động

```python
def summarize(history):
    offered = torch.stack(history["offered"]).float()
    accepted = torch.stack(history["accepted"]).float()
    mean_share = offered.sum(dim=0) / offered.sum().clamp_min(1)
    entropy = -(mean_share * mean_share.clamp_min(1e-9).log()).sum()
    mean_load = offered.mean()
    return {
        "max/mean offered load": (offered.mean(dim=0).max() / mean_load).item(),
        "effective experts (offered)": entropy.exp().item(),  # exp(H), descriptive
        "mean assignment drop rate": sum(history["assign_drop"]) / len(history["assign_drop"]),
        "mean fully-dropped token rate": sum(history["full_drop"]) / len(history["full_drop"]),
        "mean router entropy": sum(history["entropy"]) / len(history["entropy"]),
        "unused experts (accepted total = 0)": int((accepted.sum(dim=0) == 0).sum()),
    }

print("no balance:", summarize(no_balance))
print("controlled:", summarize(controlled))
```

Không hard-code ngưỡng kiểu “`max/mean > 2` luôn là collapse”. Ngưỡng phụ thuộc $N,K$, batch tokens, domain mixture, intended specialization. Hãy chạy nhiều seeds với router init không bias để biết fluctuation ngẫu nhiên trông thế nào.

### 6.2 Trade-off table — khi nào chọn gì?

| Điều chỉnh | Giảm được | Trả giá | Khi nào dùng |
|---|---|---|---|
| Tăng $c$ (1.0→1.5) | `drop rate` | Padding, memory, communication, compute slots trống tăng | Cần bảo vệ quality khi router chưa cân |
| Thêm `auxiliary loss` (tăng $\alpha$) | Concentration, `max/mean` | Có thể ép uniform quá mức, task loss xấu đi | Router collapse kéo dài |
| Thêm `routing bias` ($\gamma$ lớn) | Overload tức thì | Dao động giữa experts nếu $\gamma$ quá lớn | Cần feedback nhanh trên actual assignments |
| Giảm $N$ hoặc tăng batch tokens | Empty experts, variance | Giảm total capacity | Batch quá nhỏ so với $N K$ |
| Device-level balancing | Straggler, `all-to-all` imbalance | Không bảo đảm từng expert đều | Per-expert ổn nhưng device chậm |

> [!warning] Uniform hơn ≠ tốt hơn
> Luôn so sánh validation loss và drop rate cùng lúc. “Load đều hơn” không tự chứng minh model tốt hơn nếu task quality giảm.

## 7. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| `probs` không sum ≈1 | Softmax sai dim / fp16 overflow | `probs.sum(-1)` với `atol=1e-6`; in router shape |
| `offered` concentrate, `accepted` cũng concentrate | Router collapse thật sự | Inspect router logits/probs, tune balance, check grad coverage |
| `offered` concentrate nhưng `accepted` capped ≈ capacity | Capacity che overload | Log assignment + fully-token drop; fix router hoặc tăng budget có chủ ý |
| Loads per expert ổn nhưng device chậm | Placement/rank imbalance | Sum assignments theo device, check `all-to-all` |
| Loads dao động mạnh theo domain | Domain shift | Plot per request/domain, không chỉ global average |
| Uniform nhưng task loss tệ hơn | Balance pressure quá mạnh hoặc $c$ quá nhỏ | Giảm `alpha`/`gamma`, so validation loss & drop |
| Nhiều empty experts, drop thấp | Batch quá nhỏ so với $N K$ | Tăng tokens/group, giảm experts |
| Entropy cao nhưng cùng `top-k` lặp lại | Borderline probs vẫn rank giống nhau | Plot `top_ids`/offered share; entropy alone không đủ |

Cho distributed MoE, thêm **ba scopes** vào dashboard: (1) `expert` — offered/accepted per expert, (2) `device/rank` — aggregate compute & straggler, (3) `communication` — tokens sent/received và `all-to-all` volume. DeepSeekMoE phân biệt expert-level vs device-level loss; DeepSeek-V2 thêm communication balance.[^deepseekmoe-2024][^deepseek-v2-2024]

## 8. Lab experiments — mỗi lần đổi một biến

Lưu plots + validation metrics sau mỗi thí nghiệm:

1. **Capacity sweep:** Giữ router & `alpha` cố định, thử $c=1.0,1.25,1.5$. So offered share (capacity không sửa được router), assignment drop, fully-dropped rate, padding budget.
2. **Auxiliary-loss sweep:** `alpha` 0, 0.001, 0.01, 0.05. So task/validation loss vs `effective experts` và overflow.
3. **Bias controller sweep:** `alpha=0`, thử `gamma` 0, 0.001, 0.01. Plot luôn `routing_bias`. Gamma lớn có thể làm load dao động.
4. **Top-k accounting:** $K=1→2$. Verify offered total $T→2T$, recompute capacity $TK/N$.
5. **Partial drop:** $K=2$, $c=1.0$, ép router preference. So assignment drop vs fully-dropped-token rate — tại sao cái đầu cao mà cái sau thấp?
6. **Device aggregation:** Giả sử experts 0–3 ở device 0, 4–7 ở device 1. Sum offered theo group. Per-expert trông ổn nhưng device totals có thể không?

## 9. Giới hạn & bước tiếp theo

**Bài này không chứng minh:**
- `top-k` luôn tốt hơn `top-1`, hay expert có role semantic cố định — đó là design choices phải đánh giá cùng width, capacity, batch, hardware.[^switch-overview-2026][^deepseekmoe-2024]
- `active parameters` suy ra serving cost — cần đo total weight memory, KV cache, communication riêng.[^switch-overview-2026]
- Toy PyTorch cho kết luận throughput production — code minh họa routing mechanics, không có `all-to-all` hay distributed dispatch.

**Học tiếp (theo [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) Stage 7):**

1. [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) — ôn dense-vs-MoE và `top-k` cơ bản nếu cần.
2. [Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới](deepseekmoe-expert-design-beginners-guide.md) — fine-grained routed + shared experts.
3. [Expert parallelism và serving trade-offs — bài học cho người mới](expert-parallelism-serving-trade-offs-beginners-guide.md) — dispatch/combine qua `all-to-all`, placement, vì sao serving vẫn trả total-weight memory.

> [!success] Điều cần nhớ trước khi scale up
> - `Capacity factor` là budget có giới hạn — không làm router cân bằng.
> - Vẽ `offered` và `accepted` cùng nhau; gap là chi phí overflow.
> - Với `top-k`, đếm assignments: expected/expert = $TK/N$, không phải $T/N$.
> - `Auxiliary loss` đổi pressure tối ưu; `routing bias` đổi eligibility của `top-k`. Cả hai cần check task quality.
> - Balanced histogram không chứng minh semantic specialization; expert-level balance không suy ra device/communication balance.

## Relationships

- **Depends on:** [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) — dense-FFN baseline và `top-k` cơ bản.
- **Operationalizes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — biến capacity, overflow, balance thành thứ đo được.
- **Explains:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) — cơ chế routing-bias và giới hạn của nó.
- **Uses:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) và [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) làm ví dụ expert- và device-level.
- **Extends:** Stage 7, “Sparse capacity,” của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Lab code và dashboard là tổng hợp sư phạm, không phải code của Switch, DeepSeekMoE, DeepSeek-V2/V3. Công thức capacity và mô tả residual đến từ bundled secondary overview. DeepSeekMoE/V2/V3 cung cấp primary evidence cho cơ chế balance/drop/bias tương ứng, nhưng config báo cáo không thiết lập hyperparameter hay performance phổ quát. Không toy plot nào chứng minh production `all-to-all` cost, distributed straggler, quality ở scale, hay semantic role của expert.[^switch-overview-2026][^deepseekmoe-2024][^deepseek-v2-2024][^deepseek-v3-2024]

[^switch-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), Sections 7–9; overview thứ cấp của Switch Transformer.
[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Section 3.3.
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model” (2024), [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.2–2.3.
[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report” (2024), [source](../raw/arXiv-2412.19437v2/main.tex), Section 2.1.
