---
type: Synthesis
title: Expert parallelism và serving trade-offs — bài học cho người mới
description: A beginner-first course on MoE expert-parallel dispatch/combine, device placement, all-to-all bottlenecks, capacity padding, and why serving still pays total-weight memory.
tags: [mixture-of-experts, expert-parallelism, distributed-systems, llm-serving, pytorch, learning-roadmap]
status: stable
created: 2026-11-16
generated: { by: llm-wiki-agent/1, at: 2026-08-23T00:00:00Z }
sources:
  - id: moe-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# Expert parallelism và serving trade-offs — bài học cho người mới

`Expert parallelism` (EP) là cách chia các `expert` của MoE ra nhiều GPU. `Router` chọn expert cho mỗi token, sau đó hệ thống phải **dispatch** (gửi activation đến GPU chứa expert), chạy expert FFN, rồi **combine** (gửi kết quả về đúng token ban đầu). Hai lần `all-to-all communication`, `expert capacity` có giới hạn, `padding`, và `placement` (expert đặt ở đâu) quyết định MoE có thực sự nhanh không. Quan trọng nhất: `active parameters` (tham số kích hoạt/token) thấp **không** làm giảm memory chứa toàn bộ expert weights khi serving — mọi expert vẫn phải nằm đâu đó trong cluster.[^moe-overview-2026]

> [!success] Sau bài này
> 1. **Giải thích được:** vì sao sparse ≠ local, đường đi của một token qua 2 lần `all-to-all`, và `all-to-all` khác `all-reduce` ở đâu.
> 2. **Tính được:** `capacity` và `padding` với ví dụ số cụ thể, và đọc được per-expert load.
> 3. **Cài và kiểm được:** một toy `dispatch → combine` bằng PyTorch với metadata đầy đủ, và tránh suy luận sai từ `active parameters` sang latency/memory.

Bài này nối tiếp [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md): bài trước trả lời "token đi expert nào?", bài này trả lời "làm sao token **đến được** expert đó trên cluster?". Ví dụ Switch được dẫn qua overview thứ cấp; DeepSeek-V2/V4 là cấu hình author-reported, không phải công thức chung.[^moe-overview-2026][^deepseek-v2-2024][^deepseek-v4-2026]

## 1. Điều cần biết trước

- **Đã hiểu:** `dense FFN` xử lý mọi token bằng cùng một weight matrix; `router` + `top-1`/`top-k` chọn expert cho mỗi token. Nếu chưa, xem [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md).
- **Đã quen:** khái niệm `data / tensor / pipeline parallelism` ở mức tên gọi.
- **Chưa cần:** công thức balance loss, FP8, hay kernel fusion — sẽ gặp trong [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) và [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md).
- **Không cover ở đây:** tối ưu kernel chi tiết, hay chứng minh MoE luôn nhanh hơn dense.

## 2. Lý thuyết cốt lõi

### 2.1 Sparse compute ≠ local compute

Với dense FFN, mọi token trên GPU chạy ngay local weight. Với MoE có $E$ experts, nếu expert được chọn nằm ở GPU khác, activation của token **bắt buộc phải đi qua interconnect**.

```text
Dense:  token local ──► FFN local ──► output local

MoE:    token local ──► router ──► maybe remote expert ──► output về lại token gốc
```

> [!note] Analogy — bưu điện chia thư
> Hãy tưởng tượng 4 bưu cục (4 ranks), mỗi nơi giữ 2 chuyên gia (experts). Mỗi lá thư (token) được lễ tân (router) dán nhãn “gửi đến chuyên gia E3 ở bưu cục 1”. Thư phải được **gom theo địa chỉ**, **vận chuyển**, xử lý, rồi **gửi trả** về bưu cục gốc để sắp lại đúng thứ tự. `Expert parallelism` chính là cách chia chuyên gia ra các bưu cục.

Bốn kiểu parallelism hay đi cùng nhau:

| Kiểu | Chia cái gì? | Communication chính | Vai trò trong MoE |
|---|---|---|---|
| `Data parallelism` (DP) | batch | sync gradients khi training | tăng batch, không đặt expert |
| `Tensor parallelism` (TP) | một layer lớn | collectives trong layer | chia một expert quá lớn |
| `Pipeline parallelism` (PP) | các layer theo depth | activation giữa stages | chia model theo chiều sâu |
| `Expert parallelism` (EP) | các expert | `all-to-all` activation | chia expert bank — trọng tâm bài này |

Một deployment thực tế thường kết hợp cả bốn, nên “dùng 8 GPU” chưa nói được token phải đi bao xa.[^moe-overview-2026][^deepseek-v2-2024]

### 2.2 Đường đi của token: 6 bước `dispatch → expert → combine`

Giả sử 4 ranks, 8 experts, mỗi rank giữ 2 experts:

```text
Rank 0: E0,E1 | Rank 1: E2,E3 | Rank 2: E4,E5 | Rank 3: E6,E7
Rank 0 đang giữ tokens t0 t1 t2 t3
Router chọn:         E3 E0 E6 E3
Đích đến:            R1 R0 R3 R1
```

Với `top-1`, mỗi assignment cần tối thiểu: `activation` (vector $D$ chiều), `expert_id`, `original position`, `gate weight`.

```text
(1) Routing local:          token ──router──► (expert_id, gate, position)
(2) Pack theo đích:         gom tokens theo (rank đích, expert)
(3) All-to-all #1 Dispatch: mỗi rank gửi buffer đến mọi rank khác
(4) Expert compute local:   mỗi rank chạy FFN cho experts nó giữ
(5) All-to-all #2 Combine:  kết quả trả về rank nguồn
(6) Scatter & combine:      đặt output về đúng position, cộng gate*output (top-k thì sum)
```

> [!example] Một token, hai lần di chuyển
> `t0` ở Rank 0 → `E3` ở Rank 1: `t0` đi R0→R1 ở dispatch, `E3(t0)` tính ở R1, rồi đi R1→R0 ở combine. Với `top-2`, một token tạo hai assignments và cần cộng hai weighted outputs.

`All-to-all` ≠ `all-reduce`: `all-reduce` cộng cùng-shaped tensors; `all-to-all` **đổi ownership** của token data theo routing decisions.[^moe-overview-2026]

### 2.3 Vì sao `all-to-all` dễ thành bottleneck?

Sparse routing bớt expert FLOPs nhưng **thêm data movement** không có trong dense local FFN. Ước lượng thô cho `top-k`:

$$
\text{dispatched elements} \approx T \cdot k \cdot D
$$

với $T$ là số tokens, $k$ là số experts/token, $D$ là `d_model`. Có cả chiều dispatch và return nên traffic nhân đôi về mặt logic. Đây **không** phải latency model — bytes thực tế còn phụ thuộc dtype, metadata, padding, placement.

6 yếu tố quyết định bottleneck:

1. **Interconnect & topology** — trong-node vs cross-node bandwidth khác nhau; placement tốt ở topology này có thể kém ở topology khác.
2. **Small messages** — decode gửi rất ít token/step, overhead launch + sync có thể lấn át GEMM.
3. **Load imbalance** — hot expert làm rank chứa nó chậm nhất, cả collective phải chờ.
4. **`top-k`** — $k$ lớn hơn tăng số assignments và traffic gần tuyến tính.
5. **Padding / capacity** — static buffers tiện cho kernel nhưng truyền cả empty slots.
6. **Overlap** — có thể overlap dispatch/compute/combine nhưng không xóa dependency hay bytes.

DeepSeek-V4 báo cáo MegaMoE kernel chia experts thành `waves` để overlap 3 pha; speedup báo cáo là so với non-fused baselines của họ, không phải end-to-end serving cho mọi MoE.[^deepseek-v4-2026]

### 2.4 `Expert placement` — expert đặt ở đâu là quyết định thiết kế

`Placement` là mapping `expert_id → rank`. Nó quyết định token nào local, rank nào nhận bao nhiêu work.

**Hai cực đơn giản:**

| Placement | Lợi | Hại |
|---|---|---|
| Mọi expert của một layer ở 1 device | Có thể local, tránh cross-device | Bị giới hạn memory/compute 1 device |
| Experts shard ra nhiều devices | Chia được expert bank lớn | Tạo `all-to-all`, phải lo balance |

DeepSeekMoE minh họa rõ: config 2B/16B để toàn bộ experts/layer trên 1 device nên không cần device-level loss và không drop token; config 145B shard experts/layer ra 4 devices và thêm device-level balance. Cùng một kiến trúc routing, placement khác → objective khác.[^deepseek-v2-2024]

**Giảm fan-out theo device:** với `top-k`, nếu mỗi expert ở device khác, một token có thể fan-out đến $k$ devices. DeepSeek-V2 giới hạn: chọn tối đa $M$ devices trước, rồi chỉ chọn experts trong đó. Điều này giảm traffic nhưng cũng thu hẹp không gian chọn của router — $M$ là trade-off quality–communication–utilization phải đo, không phải hằng số chung.[^deepseek-v2-2024]

**Placement không giảm total weight:**

$$
M_{\text{expert weights}} \approx E \cdot P_E
$$

với $P_E$ là bytes/expert sau quantization. `Top-1` chỉ chạy 1 expert/token, không biến $E\cdot P_E$ thành $P_E$ khi load model hay reserve memory. Không được đọc “21B active” như “chỉ cần memory của 21B”.[^moe-overview-2026]

### 2.5 `Expert capacity`, overflow, và padding — ví dụ tính tay

Router có thể gửi không đều token. Hardware cần buffer có giới hạn, nên mỗi expert được cấp `capacity` $C$. Với `top-1`, rule kiểu Switch trong source:

$$
C = \frac{T}{E}\times \text{capacity factor}
$$

**Ví dụ:** $T=1024$, $E=8$, `capacity factor` $=1.25$:

$$
C = \frac{1024}{8}\times 1.25 = 128 \times 1.25 = 160 \text{ slots/expert}
$$

Nếu `E3` nhận 190 assignments nhưng chỉ có 160 slots → 30 assignments **overflow**. Design có thể drop chúng (nhờ residual path), retry, hoặc reroute. Với `top-k`, capacity có thể giới hạn **tokens** hay **token–expert assignments** — phải kiểm tra convention trước khi áp dụng công thức `top-1`.[^moe-overview-2026]

**Padding là gì?** Để chạy batched GEMM và predictable buffers, runtime allocate:

```text
[expert, capacity, d_model]  → ví dụ [8, 160, D]
```

Dù E0 nhận 20 tokens và E1 nhận 150 tokens, cả hai vẫn chiếm 160 slots:

```text
E0: [20 real | 140 padding]    E1: [150 real | 10 padding]
```

- Tăng `capacity factor` → bớt overflow/drop nhưng tăng padding, memory, communication, wasted GEMM.
- Giảm `capacity factor` → ngược lại.

> [!warning] Đừng chỉ nhìn mean load
> Mean lý tưởng $T/E$ không nói được tail. Serving latency bị quyết định bởi hot expert/rank, overflow rate, padding fraction, và slowest rank. Hãy log per-expert assignments, per-rank received tokens, dropped assignments, và time của dispatch/GEMM/combine.

### 2.6 Training vs prefill vs decode — cùng một MoE, workload khác

| Khía cạnh | Training | Prefill (prompt) | Decode (autoregressive) |
|---|---|---|---|
| Tokens cùng lúc | rất nhiều (global batch) | nhiều (toàn prompt) | ~1 token/request/step |
| Expert GEMM | batch lớn, dễ đầy | thường đủ batch | dễ thành small GEMM |
| Thách thức EP | balance, capacity, overlap | TTFT & prompt throughput | per-token latency, stragglers |
| Extra state | activations/gradients | KV-cache write | KV-cache read/write mỗi step |

Prefill thường đủ tokens để fill expert batches. Decode tạo ít token/step nên experts nhận tiny batches hoặc empty slots — `all-to-all` và sync khó amortize. Engine có thể continuous-batch để tăng tokens/step nhưng trade off queueing delay và fairness. Đây là suy luận từ data-flow, không phải benchmark chung.[^moe-overview-2026]

## 3. Implementation (PyTorch tối thiểu)

Code dưới **không** gọi distributed collective và không phải implementation hiệu năng. Mục tiêu là làm rõ metadata runtime phải giữ: `expert_id`, `destination rank`, `slot`, `token_id`, `gate`, và dropped assignments. Trong production, `send` buffers đi qua `all-to-all` #1, outputs đi qua `all-to-all` #2 trước khi scatter.

```python
import math
import torch
import torch.nn.functional as F


def plan_top1_dispatch(tokens, router, expert_to_rank, capacity_factor=1.25):
    """Lập kế hoạch dispatch fixed-capacity cho một MoE layer (top-1).

    tokens:         [T, D] activations local
    router:         module D -> n_experts
    expert_to_rank: [n_experts] rank đích cho mỗi expert
    Trả về buffers dạng [n_ranks, n_experts, capacity, D] để thấy rõ padding.
    Lưu ý: vòng lặp Python + CPU metadata là cố ý để dễ đọc, không phải serving.
    """
    T, D = tokens.shape
    expert_to_rank = expert_to_rank.to(tokens.device)
    n_experts = expert_to_rank.numel()
    n_ranks = int(expert_to_rank.max().item()) + 1
    capacity = math.ceil(capacity_factor * T / n_experts)

    probs = F.softmax(router(tokens.float()), dim=-1)
    gates, expert_ids = probs.max(dim=-1)       # top-1
    destinations = expert_to_rank[expert_ids]

    # Static slots: [rank, expert, slot, hidden] — thấy rõ padding
    send = tokens.new_zeros(n_ranks, n_experts, capacity, D)
    token_ids = torch.full(
        (n_ranks, n_experts, capacity), -1, dtype=torch.long, device=tokens.device
    )
    slot_gates = torch.zeros(
        n_ranks, n_experts, capacity, dtype=tokens.dtype, device=tokens.device
    )
    used = torch.zeros(n_experts, dtype=torch.long, device=tokens.device)
    dropped = []

    for token_id, (expert, rank) in enumerate(zip(expert_ids.tolist(),
                                                   destinations.tolist())):
        slot = used[expert].item()
        if slot >= capacity:
            dropped.append(token_id)
            continue
        send[rank, expert, slot] = tokens[token_id]
        token_ids[rank, expert, slot] = token_id
        slot_gates[rank, expert, slot] = gates[token_id].to(tokens.dtype)
        used[expert] += 1

    return {
        "send": send,
        "token_ids": token_ids,   # cần để restore thứ tự ban đầu
        "gates": slot_gates,
        "expert_ids": expert_ids,
        "destinations": destinations,
        "used": used,
        "capacity": capacity,
        "dropped": dropped,
    }


def combine_top1_return(expert_outputs, plan, n_tokens):
    """Sau all-to-all #2, scatter outputs về đúng token gốc (top-1)."""
    output = expert_outputs.new_zeros(n_tokens, expert_outputs.size(-1))
    valid = plan["token_ids"] >= 0
    restored_ids = plan["token_ids"][valid]
    restored_values = expert_outputs[valid] * plan["gates"][valid].unsqueeze(-1)
    output.index_copy_(0, restored_ids, restored_values)
    return output
```

Đọc output theo thứ tự:

1. `torch.bincount(expert_ids)` = demand trước capacity.
2. `used` = assignments được admit. Chênh lệch là overflow.
3. `send.shape == [n_ranks, n_experts, capacity, D]` cho thấy static padding.
4. `token_ids` là điều kiện để combine đúng token. Bỏ metadata này sẽ gán nhầm output.

> [!note] Mở rộng sang `top-k`
> Mỗi token tạo $k$ rows (token, expert, gate), capacity phải theo convention đã chọn, và `combine` phải dùng `index_add_` để cộng weighted outputs từ nhiều experts. Đừng giả định traffic/capacity/latency giữ nguyên khi đổi $k$.

## 4. Xác minh trước khi benchmark

Chạy 5 tests dưới trước khi đo tốc độ. Mỗi test ghi rõ `rtol`/`atol` và dtype. Code là single-process, không đo collective thực.

```python
torch.manual_seed(0)
T, D, E = 12, 16, 8
tokens = torch.randn(T, D)
router = torch.nn.Linear(D, E)
expert_to_rank = torch.tensor([0, 0, 1, 1, 2, 2, 3, 3])

plan = plan_top1_dispatch(tokens, router, expert_to_rank, capacity_factor=1.25)

# Test 1 — capacity tính đúng công thức C = ceil(T/E * factor)
expected_cap = math.ceil(1.25 * T / E)
assert plan["capacity"] == expected_cap
print(f"✓ Test 1 capacity OK: {plan['capacity']} == ceil(1.25*{T}/{E})=={expected_cap}")

# Test 2 — shape padded buffers và metadata khớp
n_ranks = 4
assert plan["send"].shape == torch.Size([n_ranks, E, expected_cap, D])
assert plan["token_ids"].shape == torch.Size([n_ranks, E, expected_cap])
print(f"✓ Test 2 shape OK: send {tuple(plan['send'].shape)}")

# Test 3 — accounting: admitted + dropped == T (top-1, mỗi token 1 assignment)
admitted = int(plan["used"].sum().item())
dropped = len(plan["dropped"])
assert admitted + dropped == T
print(f"✓ Test 3 accounting OK: admitted {admitted} + dropped {dropped} == T={T}")
print(f"  bincount selected: {torch.bincount(plan['expert_ids'], minlength=E).tolist()}")
print(f"  admitted per expert: {plan['used'].tolist()}")
print(f"  dropped token IDs: {plan['dropped']}")

# Test 4 — combine khôi phục đúng token với gate weighting (atol 1e-5)
expert_outputs = plan["send"]  # identity expert để test scatter metadata
restored = combine_top1_return(expert_outputs, plan, n_tokens=T)
# Với identity expert, restored[token] == gate * tokens[token] nếu admitted, else 0
for tid in range(T):
    exp = plan["expert_ids"][tid].item()
    # kiểm tra token này có được admit không
    is_admitted = tid not in plan["dropped"]
    if is_admitted:
        # tìm gate của token đó
        gate = F.softmax(router(tokens.float()), dim=-1)[tid, exp]
        torch.testing.assert_close(restored[tid], gate * tokens[tid], rtol=0, atol=1e-5)
    else:
        torch.testing.assert_close(restored[tid], torch.zeros(D), rtol=0, atol=1e-5)
print("✓ Test 4 combine OK: restored == gate*tokens (admitted) hoặc 0 (dropped)")

# Test 5 — capacity_factor nhỏ hơn làm tăng drop (monotonic sanity)
plan_small = plan_top1_dispatch(tokens, router, expert_to_rank, capacity_factor=1.0)
plan_large = plan_top1_dispatch(tokens, router, expert_to_rank, capacity_factor=2.0)
assert len(plan_small["dropped"]) >= len(plan["dropped"])
assert len(plan_large["dropped"]) <= len(plan["dropped"])
# total static slots = E * C
assert plan_large["send"].numel() > plan["send"].numel()
print(f"✓ Test 5 capacity trade-off OK: dropped c=1.0 {len(plan_small['dropped'])} >= c=1.25 {len(plan['dropped'])} >= c=2.0 {len(plan_large['dropped'])}")
print(f"  static slots: c=1.0 {E*plan_small['capacity']} | c=1.25 {E*plan['capacity']} | c=2.0 {E*plan_large['capacity']}")

# Test 6 — per-rank received tokens quan sát được (để suy ra imbalance)
per_rank_received = (plan["token_ids"] >= 0).sum(dim=(1, 2)).tolist()
print(f"✓ Test 6 per-rank load: {per_rank_received} tokens/rank (tổng {sum(per_rank_received)}=={admitted})")
assert sum(per_rank_received) == admitted
```

**Cách đọc kết quả:**
- Test 3 fail → kiểm tra `capacity` hoặc `bincount`.
- Test 4 fail → kiểm tra `token_ids`/`gates` có đúng slot không.
- Dropped tăng khi `capacity_factor` giảm là expected — đó chính là trade-off overflow vs padding.
- `per_rank_received` lệch mạnh (ví dụ [8,1,0,3]) là signal hot rank, dù mean $T/E$ trông cân.

## 5. Benchmark / Trade-offs

Toy code không đo wall-clock distributed. Bảng dưới tách các trade-offs cần đo riêng khi scale lên hệ thực.

### 5.1 Khi nào `active parameters` gây hiểu nhầm?

| Câu hỏi serving | Cần nhìn quantity nào? | Vì sao `active` chưa đủ? |
|---|---|---|
| Model có fit vào serving group không? | Total quantized weight bytes; replication/sharding | Inactive experts vẫn phải nằm ở đâu đó[^moe-overview-2026] |
| Một token tốn bao nhiêu compute? | Active expert FLOPs + attention/dense | Routing, attention, dense branch vẫn chạy |
| Request nhanh bao nhiêu? | TTFT, time per output token, EP collective time | Cross-device traffic, padding, queueing có thể dominate |
| Cluster phục vụ bao nhiêu users? | Throughput dưới request mix, batch policy, KV-cache | Decode workload và load skew đổi utilization |

Ngoài weights còn `KV cache`, router buffers, dispatch/combine buffers, temporary activations. `KV cache` tăng theo số active requests/context, còn expert weights gắn với total capacity. Giảm KV state không tự giảm expert-weight memory, và ngược lại.[^moe-overview-2026][^deepseek-v2-2024]

> [!warning] Số headline của DeepSeek-V2
> Throughput và KV-cache figures của DeepSeek-V2 kết hợp MoE + MLA + FP8 weights + KV-cache quantization + H800 + serving config cụ thể. Không thể lấy đó làm bằng chứng rằng expert parallelism một mình tạo ra speedup.[^deepseek-v2-2024]

### 5.2 Checklist đo đúng (khi bạn có distributed runtime)

```text
Model/config: total & active params; expert count, width, top-k
Placement:    expert_to_device map; EP/TP/DP/PP degrees
Capacity:     rule, capacity factor, overflow/drop policy

Routing health (log bắt buộc):
  per-expert & per-rank load, overflow/drop rate, padding fraction, device fan-out/token

System time (đo riêng, đo slowest rank):
  router/packing | dispatch all-to-all | expert GEMM | combine all-to-all | overlap

Workload:
  hardware/interconnect; weight precision
  request rate, input/output length dist., batch policy
  tách prefill throughput/TTFT và decode time per output token
  KV-cache policy & memory headroom
```

Chỉ so quality hoặc expert FLOPs là không đủ. Chỉ so tokens/s cũng không đủ nếu prompt/output mix, latency target, quantization, hay batch policy khác nhau.

## 6. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| Sparse FLOPs thấp nhưng latency cao | `all-to-all`, small batches, padding | Time dispatch/combine vs expert GEMM; tokens/rank/step |
| Một rank luôn chậm | Hot experts đặt trên rank đó | Per-rank received assignments & expert histogram |
| Drop rate cao | Capacity quá nhỏ hoặc router collapse | Demand vs admitted load; capacity factor; balance loss |
| Drop thấp nhưng throughput kém | Capacity quá lớn → padding cao | Real tokens per slot; padded communication/GEMM work |
| Decode chậm hơn prefill | Ít new tokens/step, collective overhead | Đo decode riêng; thử continuous batching |
| Model không fit dù active nhỏ | Total experts/replicas + KV cache vượt memory | Quantized total weight bytes, EP group size, cache headroom |
| Network traffic cao dù quality tốt | Selected experts spread nhiều devices | Device fan-out/token; placement; device-limited routing |

## 7. Giới hạn & bước tiếp theo

**Bài này không chứng minh:**
- Rằng cấu hình DeepSeek-V2/V4 là tối ưu phổ quát — các lựa chọn $M$, balance factors, placement, capacity rule là trade-offs phải đo trên workload của bạn.[^deepseek-v2-2024][^deepseek-v4-2026]
- Rằng toy PyTorch cho kết luận về throughput production — code chỉ minh họa routing mechanics, không đo collective, kernel utilization, hay end-to-end serving latency.
- Rằng `active parameters` suy ra serving cost — cần đo total weight memory, KV cache, communication riêng.[^moe-overview-2026]

**Học tiếp theo (theo [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) Stage 7):**

1. [MoE capacity, load balancing & stability — bài lab cho người mới](moe-capacity-load-balancing-stability-lab.md) — `capacity factor` chi tiết, `auxiliary loss` vs `routing bias`, và vẽ expert load.
2. [Thiết kế expert và specialization trong DeepSeekMoE — bài học cho người mới](deepseekmoe-expert-design-beginners-guide.md) — fine-grained routed experts + shared experts.
3. [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md) — wave-scheduled fused EP, deterministic kernels.

**Bài tập gợi ý:**
1. Chạy code với `capacity_factor` 1.0, 1.25, 2.0. So sánh `used`, `dropped`, và total static slots $E\times C$.
2. Đổi `expert_to_rank` để các experts phổ biến nằm ít ranks hơn. Quan sát `destinations` rồi giải thích vì sao placement thực phải dựa trên real routing statistics.
3. Mở rộng plan sang `top-2`; verify mỗi token tạo tối đa 2 admitted assignments và combine dùng weighted sum (`index_add_`).
4. Với distributed runtime thực, profile riêng router/pack, dispatch, expert GEMM, combine. Đừng suy luận từ wall-clock tổng.

## Relationships

- **Builds on:** [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) — router, `top-k`, và capacity cơ bản.
- **Explains:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — mô hình dispatch/combine và serving cost ở mức người mới.
- **Operationalized by:** [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) — device-limited routing, device balance, training-time dropping.
- **Specialized by:** [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md) — wave-scheduled fused expert-parallel execution.
- **Extends:** Stage 7, “Sparse capacity,” của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Mechanics Switch và công thức $C=(T/E)\times \text{capacity factor}$ được tổng hợp từ bundled Vietnamese overview trích Switch Transformer; primary Switch paper không có trong `raw/`. Cấu hình và số speedup của DeepSeek-V2/V4 là author-reported và gắn với hardware/serving config cụ thể. Code là simulation single-process để dạy metadata và capacity — không đo collective performance, model quality, hay production serving latency.[^moe-overview-2026][^deepseek-v2-2024][^deepseek-v4-2026]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), Sections 7, 10–11, and 16; it cites Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022).
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.2–2.3 and 3.1.
[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Section 4.1.
