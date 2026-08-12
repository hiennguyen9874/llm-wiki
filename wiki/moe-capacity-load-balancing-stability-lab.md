---
type: Synthesis
title: "MoE capacity, load balancing & stability — bài lab cho người mới"
description: A beginner-first MoE course and PyTorch lab on capacity factor, overflow and token dropping, auxiliary loss and routing bias, routing-collapse diagnosis, and expert-load plots.
tags: [mixture-of-experts, load-balancing, routing, capacity, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T11:59:52+07:00 }
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

Một `MoE` chỉ tiết kiệm expert-FFN computation khi router phân phối token đủ đều để các expert có thể chạy trong capacity cố định. Nếu một expert nhận quá nhiều token, implementation phải pad buffer lớn hơn, drop một phần assignment, hoặc để một device trở thành straggler; nếu expert khác hầu như không được chọn, chúng thiếu training signal. Bài này biến các khái niệm đó thành một lab PyTorch: đo và vẽ load của từng expert, thêm `capacity factor`, quan sát overflow, rồi so sánh `auxiliary loss` với `routing bias`.[^switch-overview-2026][^deepseekmoe-2024][^deepseek-v2-2024][^deepseek-v3-2024]

> [!success] Mục tiêu học
> Sau lab, bạn có thể phân biệt `offered load` với `accepted load`; tự tính capacity cho `top-k`; giải thích trade-off của `token dropping`; log `drop rate`, router entropy và expert-load share; nhận diện `routing collapse`; và hiểu tại sao `auxiliary loss` cùng `routing bias` là hai control mechanisms khác nhau.

Bài này tiếp nối [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md), nơi giải thích router và `top-k` cơ bản. Code dưới đây ưu tiên observability và correctness, **không** phải fused hoặc distributed production MoE.

## 1. Vấn đề thực tế sau `top-k`

Với $T$ token trong một batch, $N$ routed experts, và `top-k` $K$, router tạo đúng $T K$ **token–expert assignments** trước khi áp dụng capacity. Ví dụ $T=12$, $N=4$, $K=2$ tạo 24 assignments:

```text
Token 0 → expert 3, expert 1
Token 1 → expert 3, expert 0
...
```

Nếu router perfectly balanced, mỗi expert nhận trung bình:

$$
\operatorname{expected\ assignments/expert}=\frac{TK}{N}.
$$

Đây là điểm dễ nhầm: với `top-1`, $K=1$, nên công thức quen thuộc là $T/N$. Với `top-k`, capacity thường cần tính theo **assignment**, tức có thêm $K$. Một system cụ thể có thể định nghĩa capacity theo token, per device, hoặc theo packed slot khác; luôn kiểm tra definition của implementation trước khi so sánh số liệu.

### Ba loại load cần tách riêng

| Metric | Câu hỏi trả lời | Cách tính cho expert $i$ |
|---|---|---|
| `offered load` | Router muốn gửi bao nhiêu assignments đến expert? | Count của $i$ trong `top-k` **trước** capacity |
| `accepted load` | Expert thực sự chạy bao nhiêu assignments? | Count còn lại **sau** capacity/drop policy |
| `load share` | Expert chiếm bao nhiêu traffic của batch? | `load / total assignments` |

Không được chỉ nhìn `accepted load`: capacity có thể cắt peak, làm biểu đồ trông cân bằng dù router vẫn luôn dồn demand vào một expert. Vì vậy lab phải vẽ **cả offered lẫn accepted load**.

## 2. `Capacity factor`, overflow, và `token dropping`

Một implementation thường pre-allocate số slot tối đa cho mỗi expert để giữ tensor shape và work bounded:

$$
C=\left\lceil \frac{TK}{N}\times c\right\rceil,
$$

trong đó $c$ là `capacity factor`. Với `top-1`, đây trở về $\lceil(T/N)c\rceil$, công thức Switch-style quen thuộc.[^switch-overview-2026]

Ví dụ: $T=1{,}024$, $N=8$, $K=2$, $c=1.25$:

$$
C=\left\lceil\frac{1024\times2}{8}\times1.25\right\rceil=320.
$$

Mỗi expert có tối đa 320 assignment slots, tổng capacity là 2,560 slots trong khi batch chỉ đề xuất 2,048 assignments. Phần chênh là buffer để chịu dao động routing.

| `capacity factor` | Lợi ích | Chi phí/rủi ro |
|---|---|---|
| Nhỏ, gần 1 | Ít padding và compute slots | Overflow/drop tăng khi routing lệch hoặc batch nhỏ |
| Lớn | Ít assignment bị drop | Padding, memory, communication, và compute lãng phí tăng |
| Không giới hạn trong toy code | Dễ viết | Không mô phỏng bounded buffer hay real system pressure |

Khi offered assignments đến một expert vượt $C$, đó là `overflow`. Một policy đơn giản là giữ các assignments có gate/affinity cao hơn và drop phần còn lại. DeepSeek-V2 mô tả device-level token dropping: giới hạn average device budget ở capacity factor 1.0, rồi drop token có affinity thấp nhất trên device đó; balance losses chỉ khuyến khích chứ không bảo đảm strict balance.[^deepseek-v2-2024]

> [!warning] “Dropped token” cần định nghĩa chính xác
> Với `top-1`, drop assignment thường có nghĩa token không nhận expert branch và residual path vẫn tồn tại. Với `top-k`, token có thể mất **một số** selected experts nhưng còn experts khác (`partial drop`), hoặc mất tất cả (`fully dropped`). Hãy log assignment drop rate và fully-dropped-token rate riêng; một con số chung dễ che mất failure mode.

`Token dropping` là safety valve cho bounded work, không phải cách chữa router collapse. Nếu drop rate cao, model có thể train trên computation khác với router intended; tăng capacity chỉ che demand concentration và tăng systems cost.

## 3. `Routing collapse` là gì?

`Routing collapse` xảy ra khi router repeatedly selects chỉ một few experts, còn nhiều experts hầu như không nhận token. DeepSeekMoE nêu hai hệ quả: expert không được chọn thiếu training, và imbalance giữa devices tạo compute bottleneck.[^deepseekmoe-2024] DeepSeek-V3 cũng mô tả unbalanced expert load gây routing collapse và làm giảm efficiency khi dùng expert parallelism.[^deepseek-v3-2024]

Ví dụ với 8 experts, `top-1`:

```text
ideal offered share:  [12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5] %
collapsed share:      [78.0,  9.0,  4.0,  3.0,  2.0,  2.0,  1.0,  1.0] %
```

Expert 0 không nhất thiết “tốt hơn”; nó có thể chỉ có initial logit advantage. Vì tokens đi qua expert 0, expert 0 nhận nhiều gradient và có thể tốt lên nhanh hơn. Experts ít được gọi tiếp tục thiếu gradient: feedback loop này làm imbalance kéo dài.

### Signals để chẩn đoán

| Signal | Healthy pattern (không phải strict requirement) | Warning sign |
|---|---|---|
| `offered load share` qua nhiều steps | Không một expert chiếm kéo dài phần lớn traffic | Một/few experts dominate; nhiều expert gần 0 |
| `accepted load` và `drop rate` | Accepted gần offered, low overflow theo chosen budget | Offered peak bị cắt, drop tăng |
| `max load / mean load` | Gần 1 hơn là tốt cho utilization | Tăng dai dẳng, đặc biệt vượt capacity factor |
| `router entropy` | Không đột ngột về rất thấp | Distribution rất peaked hoặc dao động mạnh |
| Expert gradient/update norm | Nhiều experts có signal theo thời gian | Nhiều experts luôn không có/near-zero update |
| Per-device load | Aggregate work tương đối cân bằng | Một device straggles dù vài experts khác rảnh |

`Router entropy` chỉ là signal phụ. Router có thể có high-probability uncertainty nhưng `top-k` vẫn repeatedly chọn cùng experts; ngược lại, uneven expert use có thể hợp lý trong một batch/domain. Kết luận collapse cần time series, overflow, training quality, và systems context — không chỉ một histogram.

## 4. Hai cách control load

### 4.1 `Auxiliary loss`: thêm pressure vào training objective

Gọi $a_i$ là số offered assignments của expert $i$. Một normalization tiện dụng cho `top-k` là:

$$
f_i=\frac{a_i}{TK},\qquad
P_i=\frac{1}{T}\sum_{t=1}^{T}p_{i,t},
$$

với $p_{i,t}$ là router probability trước sparse selection. $f_i$ và $P_i$ đều sum to 1 across experts. Một Switch-style form là:

$$
L_{\mathrm{balance}}=\alpha N\sum_{i=1}^{N}f_iP_i,
\qquad L=L_{\mathrm{task}}+L_{\mathrm{balance}}.
$$

Khi uniform, $f_i=P_i=1/N$ và expression bằng $1$. Nếu load/probability cùng concentrate vào một expert, loss lớn hơn. Assignment count $f_i$ là discrete, nhưng $P_i$ differentiable qua `softmax`, nên router vẫn nhận gradient. DeepSeekMoE sử dụng expert-level balance loss để giảm routing-collapse risk, đồng thời dùng device-level loss riêng khi cần cân bằng computation giữa devices.[^deepseekmoe-2024]

`alpha` là trade-off, không phải magic constant:

- quá nhỏ: task loss có thể vẫn cho router collapse;
- quá lớn: router bị ép uniform ngay cả khi specialization hữu ích, có thể làm task quality kém;
- đúng value phụ thuộc data, number of experts, batch size, $K$, architecture, và training phase.

Vì vậy, log task loss **và** routing metrics khi tune `alpha`; “load uniform hơn” không tự chứng minh model tốt hơn.

### 4.2 `Routing bias`: thay đổi selection, không trực tiếp thêm main loss

DeepSeek-V3 dùng expert-specific bias $b_i$ cho **top-k selection**:

$$
\operatorname{selected}(t)=\operatorname{TopK}_i(s_{i,t}+b_i),
$$

nhưng gate weight dùng để combine expert outputs vẫn được tính từ unmodified affinity $s_{i,t}$. Cuối mỗi training step, bias của expert overloaded giảm $b_i\leftarrow b_i-\gamma$; expert underloaded tăng $b_i\leftarrow b_i+\gamma$.[^deepseek-v3-2024]

Tách hai việc này rất quan trọng:

```text
selection score:  affinity + routing bias  → expert nào được chạy?
mixture weight:   affinity (unmodified)    → expert đã chọn đóng góp bao nhiêu?
```

Do đó bias acts như feedback controller cho assignment eligibility, thay vì trực tiếp nói output của một expert phải lớn hơn. V3 vẫn thêm sequence-wise auxiliary loss rất nhỏ để tránh extreme imbalance trong từng sequence; “auxiliary-loss-free” ở đây không có nghĩa mọi balance-related loss đều bằng 0.[^deepseek-v3-2024]

| Mechanism | Tác động chính | Ưu điểm | Giới hạn |
|---|---|---|---|
| `auxiliary loss` | Gradient của router parameters | Differentiable training objective | `alpha` lớn có thể compete với task objective |
| `routing bias` | Discrete top-k eligibility từ observed load | Direct feedback on actual assignments | Update speed và delayed/noisy batch statistics cần tune |
| Device/rank balancing | Aggregate work/communication placement | Giảm straggler và `all-to-all` imbalance | Không bảo đảm individual experts được train đều |
| Capacity/drop policy | Bounded expert/device work | Protects memory and latency budget | Does not fix offered-load concentration |

## 5. Lab: một readable `capacity-aware` MoE

Code này implements:

- `top-k` routing per token;
- `offered_load` before capacity và `accepted_load` after it;
- keep highest unmodified gate assignments when one expert overflows;
- `auxiliary_loss` from pre-selection probabilities;
- optional V3-inspired `routing_bias` update based on **offered** load;
- metrics needed to plot and diagnose.

It deliberately excludes `all-to-all`, padding kernels, expert sharding, shared experts, and distributed synchronization. Capacity is per expert, not per device.

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
        # This controller state changes selection only, not output gate values.
        self.register_buffer("routing_bias", torch.zeros(n_experts))

    def capacity(self, n_tokens: int) -> int:
        # Capacity unit is a token--expert assignment, so top-k includes k.
        return math.ceil(n_tokens * self.k * self.capacity_factor / self.n_experts)

    def forward(self, x: torch.Tensor):
        B, T, D = x.shape
        n_tokens = B * T
        tokens = x.reshape(n_tokens, D)

        # fp32 router computation is a stability-minded choice for the toy lab.
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(tokens.dtype)
        selection_scores = probs + self.routing_bias.to(tokens.dtype)
        _, top_ids = selection_scores.topk(self.k, dim=-1)  # (n_tokens, k)

        # Gates come from unmodified probabilities, then normalize selected gates.
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

            # On overflow, retain this expert's highest unmodified gates.
            order = gates[token_rows, slots].argsort(descending=True)
            keep = order[:cap]
            kept_rows, kept_slots = token_rows[keep], slots[keep]
            accepted[kept_rows, kept_slots] = True
            accepted_load[expert_id] = kept_rows.numel()

            values = expert(tokens[kept_rows])
            weighted = gates[kept_rows, kept_slots].unsqueeze(-1) * values
            output.index_add_(0, kept_rows, weighted)

        # A token with no accepted assignment has zero MoE branch here; its block
        # residual connection, outside this module, still carries the token onward.
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
        """Switch-style top-k adaptation; add alpha * this result to task loss."""
        offered = torch.bincount(top_ids.reshape(-1), minlength=self.n_experts)
        f = offered.float() / offered.sum().clamp_min(1)  # realized offered share
        P = probs.float().mean(dim=0)                     # differentiable mean share
        return self.n_experts * (f * P).sum()

    @torch.no_grad()
    def update_routing_bias(self, offered_load: torch.Tensor, gamma: float):
        """V3-inspired sign update, intentionally simplified for this lab."""
        target = offered_load.sum().float() / self.n_experts
        direction = torch.sign(target - offered_load.float())
        self.routing_bias.add_(gamma * direction)
        self.routing_bias.sub_(self.routing_bias.mean())  # preserve relative biases
```

### Smoke test: kiểm tra accounting trước khi train

```python
torch.manual_seed(7)
moe = CapacityAwareTopKMoE(
    d_model=16, d_ff=64, n_experts=4, k=2, capacity_factor=1.0
)
x = torch.randn(3, 5, 16, requires_grad=True)  # 15 tokens, 30 assignments

y, stats = moe(x)
print("capacity/expert:", stats["capacity"])       # ceil(15 * 2 / 4) = 8
print("offered:", stats["offered_load"].tolist())
print("accepted:", stats["accepted_load"].tolist())
print("assignment drop:", stats["assignment_drop_rate"].item())

assert y.shape == x.shape
assert stats["offered_load"].sum().item() == 3 * 5 * 2
assert (stats["accepted_load"] <= stats["capacity"]).all()
assert stats["accepted_load"].sum() <= stats["offered_load"].sum()

loss = y.square().mean() + 0.01 * moe.auxiliary_loss(
    stats["probs"], stats["top_ids"]
)
loss.backward()
assert moe.router.weight.grad is not None
```

> [!note] Một design choice được nêu rõ
> Code normalizes selected **pre-capacity** gates, sau đó không re-normalize gate của token bị partial drop. Như vậy output branch giảm khi assignment bị drop và metric dễ diễn giải. Một production implementation có thể dùng policy khác; thay policy mà không log rõ sẽ làm comparison misleading.

## 6. Vẽ `load` của mỗi expert

Đo qua một batch gần như luôn noisy. Hãy aggregate nhiều optimizer steps. Đoạn dưới là training harness tối thiểu: target chỉ là synthetic tensor để kiểm tra instrumentation, không phải language-model training.

```python
import matplotlib.pyplot as plt


def run_lab(use_aux_loss: bool, use_bias_controller: bool, steps: int = 300):
    torch.manual_seed(0)
    moe = CapacityAwareTopKMoE(
        d_model=32, d_ff=96, n_experts=8, k=1, capacity_factor=1.0
    )
    # Intentional initial advantage: makes the no-balance run easier to diagnose.
    with torch.no_grad():
        moe.router.bias[0] = 2.0

    opt = torch.optim.AdamW(moe.parameters(), lr=3e-3)
    history = {key: [] for key in [
        "offered", "accepted", "capacity", "assign_drop", "full_drop", "entropy", "task", "balance"
    ]}

    for step in range(steps):
        x = torch.randn(16, 8, 32)       # T = 128 tokens per step
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


# Compare a deliberately unbalanced setup with two balancing mechanisms.
_, no_balance = run_lab(use_aux_loss=False, use_bias_controller=False)
_, controlled = run_lab(use_aux_loss=True, use_bias_controller=True)
```

### Plot 1: load share của **từng** expert theo step

```python
def plot_expert_load(history, title):
    offered = torch.stack(history["offered"]).float()      # (steps, n_experts)
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

**Cách đọc plot:** ở panel `offered`, mỗi line lý tưởng dao động quanh $1/N$. Nếu expert 0 duy trì cao và nhiều experts bám gần 0, router is collapsed. Ở panel `accepted`, lines có thể nhìn bớt lệch vì capacity clipped expert 0. Nếu hai panel khác xa nhau, đó là evidence capacity đang che offered overload, không phải router đã balanced.

### Plot 2: average load, capacity, và overflow

```python
def plot_summary(history, title):
    offered = torch.stack(history["offered"]).float()
    accepted = torch.stack(history["accepted"]).float()
    n_experts = offered.shape[1]
    mean_offered = offered.mean(dim=0)
    mean_accepted = accepted.mean(dim=0)
    mean_capacity = torch.tensor(history["capacity"], dtype=torch.float32).mean()
    capacity = mean_accepted.new_full((n_experts,), mean_capacity)
    # This lab uses the same capacity for every expert. Logging it still makes
    # the plot correct if a later experiment changes batch-token count.

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


plot_summary(no_balance, "A. Offered versus accepted assignments")
plot_summary(controlled, "B. Offered versus accepted assignments")
```

Trong production lab, lưu `stats["capacity"]` ở mỗi step thay vì reconstruct như snippet minh họa. `mean offered > capacity` cho một expert nghĩa overflow; `mean accepted` sát capacity trong khi offered cao hơn nghĩa drop policy đang frequently activate.

## 7. Tính metrics có thể hành động

Thêm summary sau để so sánh conditions. `max/mean` đo concentration trực tiếp; `effective experts` là $\exp(H)$, với $H$ là entropy của average offered share. Nó là “effective number” descriptive, không phải số expert có semantic specialization.

```python
def summarize(history):
    offered = torch.stack(history["offered"]).float()
    accepted = torch.stack(history["accepted"]).float()
    mean_share = offered.sum(dim=0) / offered.sum().clamp_min(1)
    entropy = -(mean_share * mean_share.clamp_min(1e-9).log()).sum()
    mean_load = offered.mean()
    return {
        "max/mean offered load": (offered.mean(dim=0).max() / mean_load).item(),
        "effective experts (offered)": entropy.exp().item(),
        "mean assignment drop rate": sum(history["assign_drop"]) / len(history["assign_drop"]),
        "mean fully-dropped token rate": sum(history["full_drop"]) / len(history["full_drop"]),
        "mean router entropy": sum(history["entropy"]) / len(history["entropy"]),
        "unused experts (accepted total = 0)": int((accepted.sum(dim=0) == 0).sum()),
    }

print("no balance:", summarize(no_balance))
print("controlled:", summarize(controlled))
```

Không hard-code pass/fail threshold như “`max/mean > 2` luôn là collapse”. Threshold hợp lý phụ thuộc $N$, $K$, batch token count, domain mixture, and intended specialization. Để biết random fluctuation alone trông như thế nào, hãy chạy nhiều seeds với router initialization không bị bias.

## 8. Diagnosis → nguyên nhân có thể → bước kiểm tra

| Quan sát | Có thể đang xảy ra | Kiểm tra/response tiếp theo |
|---|---|---|
| Offered load concentrate, accepted cũng concentrate | Router collapse thật sự | Inspect router logits/probs, add/tune balance control, check expert gradient coverage |
| Offered concentrate nhưng accepted capped gần bằng capacity | Capacity che overload, drop policy đang discard demand | Log assignment và fully-token drop; fix router/load or raise budget knowingly |
| Loads per expert ổn nhưng one device slow | Placement/rank imbalance, not expert-level collapse | Aggregate assignment and communication by device; use device/rank balance or replication |
| Loads change sharply giữa data domains | Domain shift | Plot per request/domain and serving batch, not just training global average |
| Uniform load nhưng task loss worse | Balance pressure too strong hoặc capacity too small | Lower `alpha`/bias speed, compare validation loss and drop rate |
| Many empty experts, low drop | Batch too small relative to $N K$ | Increase tokens per routing group, reduce experts, or accept lower utilization |
| Router entropy high nhưng same `top-k` repeat | Borderline probabilities still rank same experts | Plot `top_ids`/offered share; entropy alone is insufficient |

For distributed MoE, add **three scopes** to the dashboard:

1. `expert`: offered/accepted assignments per expert, collapse and undertraining;
2. `device` or `expert-parallel rank`: aggregate compute, stragglers;
3. `communication`: tokens sent/received per rank and `all-to-all` volume.

Expert-level uniformity is not the only objective. DeepSeekMoE explicitly distinguishes a small expert-level loss to limit collapse from a device-level loss that promotes balanced device computation.[^deepseekmoe-2024] DeepSeek-V2 further distinguishes expert, device, and communication balance.[^deepseek-v2-2024]

## 9. Lab experiments

Run one change at a time and save the plots plus validation metrics.

1. **Capacity sweep:** Hold router and `alpha` fixed; try `capacity_factor` 1.0, 1.25, 1.5. Compare offered share (should not be repaired by capacity alone), assignment drop, fully dropped token rate, and padding/capacity budget.
2. **Auxiliary-loss sweep:** Try `alpha` 0, 0.001, 0.01, 0.05. Compare task/validation loss against `effective experts` and overflow. Do not choose highest uniformity automatically.
3. **Bias controller sweep:** With `alpha=0`, try `gamma` 0, 0.001, 0.01. Plot `routing_bias` too. A large gamma may make load oscillate between experts rather than converge.
4. **Top-k accounting:** Change $K$ from 1 to 2. Verify offered assignment total changes from $T$ to $2T$, and recompute capacity using $TK/N$.
5. **Partial drop:** Set $K=2$, capacity factor 1.0, and force router preference. Compare assignment drop with fully-dropped-token rate. Why can the first be high while the second stays low?
6. **Device aggregation:** Pretend experts 0–3 are on device 0 and 4–7 on device 1. Sum offered loads by group. Can per-expert plots look acceptable while device totals are not?

## 10. Điều cần nhớ trước khi scale up

- `Capacity factor` allocates a bounded budget; it does not make router demand balanced.
- Plot `offered load` and `accepted load` together. The gap is the operational cost of overflow.
- For `top-k`, count token–expert assignments: expected per-expert load is $TK/N$, not merely $T/N$.
- `Auxiliary loss` changes optimization pressure; `routing bias` changes top-k selection from observed load. Both require task-quality checks.
- `Token dropping` can protect fixed compute but may skip some or all routed computation for a token; log the exact drop semantics.
- A balanced expert histogram does not prove semantic specialization, and expert-level balance does not imply balanced devices or communication.

## Relationships

- **Builds on:** [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) for the dense-FFN baseline and basic `top-k` routing.
- **Operationalizes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through capacity, overflow, balance, and observability.
- **Explains:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) with a transparent routing-bias controller and its limits.
- **Uses:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) and [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) as expert- and device-level examples.
- **Extends:** Stage 7, “Sparse capacity,” of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

The lab code and recommended dashboard are pedagogical synthesis, not code from Switch, DeepSeekMoE, DeepSeek-V2, or DeepSeek-V3. The Switch capacity formula and residual-path description come from the bundled secondary overview. DeepSeekMoE/V2/V3 provide primary evidence for their respective balance, drop, and bias mechanisms, but author-reported configurations do not establish universal hyperparameters or performance. In particular, no toy plot can demonstrate production `all-to-all` cost, distributed stragglers, quality at scale, or a human-readable semantic role for an expert.[^switch-overview-2026][^deepseekmoe-2024][^deepseek-v2-2024][^deepseek-v3-2024]

[^switch-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), Sections 7–9; it is a secondary overview of Switch Transformer.
[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Section 3.3.
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model” (2024), [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.2–2.3.
[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report” (2024), [source](../raw/arXiv-2412.19437v2/main.tex), Section 2.1.
