---
type: Synthesis
title: Expert parallelism và serving trade-offs — bài học cho người mới
description: A beginner-first course on MoE expert-parallel dispatch/combine, device placement, all-to-all bottlenecks, capacity padding, and why serving still pays total-weight memory.
tags: [mixture-of-experts, expert-parallelism, distributed-systems, llm-serving, pytorch, learning-roadmap]
status: stable
created: 2026-11-16
generated: { by: llm-wiki-agent/1, at: 2026-11-16T00:00:00Z }
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

`Expert parallelism` phân bố các MoE `expert` lên nhiều accelerator. Sau khi router chọn expert cho từng token, runtime phải **dispatch** activation đến device giữ expert, chạy expert FFN, rồi **combine** output về đúng token ban đầu. `All-to-all communication`, bounded `expert capacity`, padding, và placement quyết định liệu sparse MoE có thực sự nhanh; số `active parameters` thấp không làm weight memory, checkpoint, hay model-loading cost giảm xuống theo vì toàn bộ expert weights vẫn phải được giữ trong deployment.[^moe-overview-2026]

> [!success] Mục tiêu
> Sau bài này, bạn có thể vẽ được đường đi của một token qua hai lần `all-to-all`, giải thích `expert placement` thay đổi traffic và load thế nào, tính được capacity/padding trong một ví dụ nhỏ, và tránh suy luận sai từ `active parameters` sang serving latency hoặc memory.

Đây là bài học tiếp theo sau [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md): bài trước giải thích router chọn expert nào; bài này giải thích **làm sao token đến được expert đó trên một cluster**. Các cơ chế Switch được truy về bundled secondary overview; ví dụ DeepSeek-V2 và DeepSeek-V4 là các thiết kế author-reported, không phải recipe phổ quát.[^moe-overview-2026][^deepseek-v2-2024][^deepseek-v4-2026]

## 1. Điều kiện tiên quyết: sparse compute không có nghĩa là local compute

Trong một dense `FFN`, mọi token trên GPU có thể chạy qua cùng local weight matrix. Trong một MoE layer có $E$ experts, router chọn `top-1` hoặc `top-k` expert cho mỗi token. Nếu selected expert nằm trên GPU khác, token activation phải đi qua interconnect.

```text
Dense FFN on one rank
local tokens ─────────────► local FFN ─────────────► local outputs

MoE FFN with sharded experts
local tokens ─► router ─► remote/local expert ─► return output ─► original token order
```

`Expert parallelism` (EP) là cách shard **expert bank** theo rank/device. Nó khác với:

| Kiểu parallelism | Chia cái gì? | Communication điển hình | Vai trò trong MoE system |
|---|---|---|---|
| `Data parallelism` (DP) | Batch; mỗi replica xử lý data khác | Gradient synchronization khi training | Tăng global batch, không tự đặt expert |
| `Tensor parallelism` (TP) | Một tensor/linear layer lớn | Collectives bên trong layer | Chia một expert hoặc dense layer quá lớn |
| `Pipeline parallelism` (PP) | Các layer theo depth | Activation giữa pipeline stages | Chia model theo depth |
| `Expert parallelism` (EP) | Các expert khác nhau | `all-to-all` token activation trước/sau expert FFN | Cho expert bank lớn vừa cluster |

Một deployment thực tế có thể kết hợp cả bốn. Vì vậy, “dùng 8 GPUs” chưa nói được routing traffic hay một token phải đi bao xa.[^moe-overview-2026][^deepseek-v2-2024]

## 2. Bức tranh data flow: `dispatch → expert compute → combine`

Giả sử có 4 ranks và 8 experts, mỗi rank giữ 2 experts:

```text
Rank 0: E0, E1       Rank 1: E2, E3
Rank 2: E4, E5       Rank 3: E6, E7
```

Ban đầu, mỗi rank giữ một shard của batch. Router chạy trên hidden states local và tạo assignment, ví dụ:

```text
Rank 0 owns token positions: t0 t1 t2 t3
selected experts:             E3 E0 E6 E3
expert locations:             R1 R0 R3 R1
```

Với `top-1`, một assignment chứa tối thiểu:

- `activation`: hidden vector của token, kích thước $D$;
- `expert id` hoặc local slot để expert biết input thuộc expert nào;
- `original token position` và `gate weight`, để trả output đúng nơi và nhân gate.

Luồng tổng quát là:

```text
(1) Local routing
    token states ──router──► (expert_id, gate, original_position)

(2) Pack by destination and expert
    R0: [E0 inputs for R0] [E3 inputs for R1] [E6 inputs for R3]

(3) First all-to-all: dispatch
    each source rank sends its packed token activations to destination ranks

(4) Local expert compute
    each rank batches inputs for its resident experts and runs their FFNs

(5) Second all-to-all: combine/return
    expert outputs travel back to source ranks

(6) Scatter and combine
    restore original token positions; sum weighted outputs for top-k
```

`All-to-all` nghĩa là mỗi rank *có thể* gửi một different-sized (hoặc padded fixed-sized) buffer đến mọi rank khác. Nó không phải `all-reduce`: `all-reduce` cộng/aggregate cùng-shaped tensors; `all-to-all` hoán đổi ownership của token data theo routing decisions.

> [!example] Một token, hai lần di chuyển
> Token `t0` trên Rank 0 được router gửi đến `E3` trên Rank 1. `t0` đi R0 → R1 cùng activation trong dispatch. `E3(t0)` được tính ở R1; output lại đi R1 → R0 trong combine. Cuối cùng runtime scatter output vào position của `t0`. Với `top-2`, token có thể tạo hai token–expert assignments và cần cộng hai weighted outputs.

Các nguồn mô tả đúng pattern `group → all-to-all → expert → all-to-all → restore order`; đó là nguyên nhân communication là ràng buộc cốt lõi của distributed MoE.[^moe-overview-2026]

## 3. Tại sao `all-to-all` có thể là bottleneck?

Sparse routing giảm số expert FFN evaluations trên mỗi token, nhưng nó thêm data movement không tồn tại trong local dense FFN. Một ước lượng payload thô cho `top-k` là:

$$
\text{dispatched activation elements} \approx T\,k\,D,
$$

với $T$ là số token trong batch shard/global theo convention, $k$ là số selected experts, và $D$ là `d_model`. Có dispatch và return, nên activation traffic có hai chiều logic. Actual bytes còn phụ thuộc dtype, metadata, padding, placement, và implementation; công thức này **không** là một latency model.

Các yếu tố quyết định bottleneck:

1. **Interconnect bandwidth và topology.** Remote traffic trong một node và traffic qua nodes có latency/bandwidth khác nhau. Một expert placement tốt trên topology này có thể kém trên topology khác.
2. **Small messages và synchronization.** Decode gửi rất ít token mỗi step; launch overhead, collective synchronization, và stragglers có thể lấn át expert GEMM.
3. **Load imbalance.** Một hot expert khiến rank chứa nó chậm hơn; toàn collective thường phải chờ rank chậm nhất, kể cả các rank khác rảnh.
4. **`top-k`.** $k$ lớn hơn tăng expert work và gần đúng tăng số assignments/token, do đó tăng packing và traffic.
5. **Padding/capacity.** Static buffers tiện cho kernels và collective nhưng có thể truyền hoặc process empty slots.
6. **Overlap.** Runtime tốt có thể overlap dispatch, expert GEMM, và combine; overlap che bớt thời gian nhưng không xóa dependency hay network bytes.

DeepSeek-V4 báo cáo một MegaMoE kernel chia experts thành `waves` để overlap dispatch, compute, và combine. Các speedup được báo cáo là so với non-fused baselines của họ và không chứng minh end-to-end serving speedup cho mọi MoE model.[^deepseek-v4-2026]

## 4. `Expert placement`: expert ở device nào là một design decision

`Placement` là mapping từ expert ID đến device/rank. Nó quyết định token nào local, rank nào nhận bao nhiêu work, và mỗi token phải fan out đến bao nhiêu devices.

### 4.1 Hai cực đơn giản

| Placement | Ý nghĩa | Lợi ích | Trade-off |
|---|---|---|---|
| All experts of a layer trên một device | Một token routed trong layer đó có thể local nếu batch ở cùng device | Có thể tránh cross-device dispatch cho layer | Bị giới hạn bởi memory/compute của một device; khó scale expert bank |
| Experts shard trên nhiều devices | Mỗi rank giữ một subset experts | Total weights và expert compute được phân bố | Routing tạo `all-to-all`; placement/load balance trở thành vấn đề |

DeepSeekMoE nêu một configuration 2B/16B đặt toàn bộ experts của một layer trên một device, không cần device-level loss và không drop token; preliminary 145B configuration phân bố experts của một layer trên bốn devices và thêm device-level balance. Điều này minh họa rằng routing objective phụ thuộc placement, chứ không chỉ phụ thuộc số expert.[^deepseek-v2-2024]

### 4.2 Giảm fan-out theo device

Với `top-k`, selected experts của một token có thể nằm trên nhiều devices. Nếu `k=6` và mỗi expert ở device khác, một token có thể fan out đến sáu destinations. Một system có thể hạn chế router: trước hết chọn một số devices có affinity cao, sau đó chỉ chọn experts bên trong chúng.

DeepSeek-V2 dùng exactly ý tưởng này: chọn tối đa $M$ devices trước rồi chọn `top-k` experts trong tập đó. Điều này giới hạn cross-device fan-out trong configuration của họ, nhưng cũng giới hạn không gian lựa chọn của router; $M$, placement và balance objectives là trade-offs quality–communication–utilization phải đo, không phải constants áp dụng chung.[^deepseek-v2-2024]

### 4.3 Placement không thay đổi total weight ownership

Placement shard weights qua cluster để một device không phải chứa toàn bộ expert bank. Tuy vậy, deployment vẫn phải provision tất cả expert weights **ở đâu đó** trong serving replica/group. Nếu có $E$ experts, mỗi expert $P_E$ bytes sau quantization, expert-weight storage xấp xỉ:

$$
M_{\text{expert weights}} \approx E P_E.
$$

`Top-1` chỉ đọc/tính một expert cho token, không biến $E P_E$ thành $P_E$ để load model, store checkpoint, hay reserve cluster memory. Replication để tăng throughput còn có thể tăng tổng cluster memory. Đây là lý do không được diễn giải “21B active” như “chỉ cần memory của 21B parameters.”[^moe-overview-2026]

## 5. `Expert capacity`, overflow, và padding

Router có thể gửi không đều token. Hardware/runtime thường cần buffer bounded, nên mỗi expert được một `capacity` $C$. Với `top-1`, Switch-style rule trong source là gần đúng:

$$
C = \frac{T}{E}\times \text{capacity factor}.
$$

Ví dụ, $T=1{,}024$, $E=8$, `capacity factor` $=1.25$:

$$
C=160\text{ token slots per expert}.
$$

Nếu `E3` nhận 190 tokens nhưng có 160 slots, 30 assignments overflow. Một design có thể drop chúng khỏi MoE branch và để residual path tiếp tục; design khác có thể retry/reroute hoặc dùng rule khác. Với `top-k`, capacity convention phải nói rõ nó giới hạn **tokens** hay **token–expert assignments**; không nên tự áp dụng công thức `top-1` mà không kiểm tra implementation.[^moe-overview-2026]

### Padding là gì?

Để chạy batched expert GEMM và predictable collective buffers, runtime có thể allocate tensor dạng:

```text
[expert, capacity, d_model]
```

Ngay cả khi E0 nhận 20 tokens và E1 nhận 150 tokens, cả hai có thể có 160 slots. Slots chưa dùng là `padding`.

```text
E0: [20 real tokens | 140 padding slots]
E1: [150 real tokens | 10 padding slots]
```

`Capacity factor` lớn hơn:

- giảm overflow/dropped assignments;
- tăng padding, activation memory, communication buffer, và potentially wasted GEMM work.

`Capacity factor` nhỏ hơn làm ngược lại. Vì vậy, tỷ lệ active parameters không mô tả đủ cost: một expert bank có thể sparse về logical routing nhưng vẫn execute/communicate nhiều padded slots.[^moe-overview-2026]

> [!warning] Đừng đo load chỉ bằng mean
> Mean lý tưởng là $T/E$, nhưng serving latency bị quyết định bởi tail: hot expert/rank, overflow rate, padding fraction, và slowest rank. Log per-expert assignments, per-rank received tokens, dropped assignments, và time của dispatch/GEMM/combine.

## 6. Code: mô phỏng `top-1` packing, capacity, và return path

Code dưới đây không gọi distributed collective và không phải performance implementation. Nó làm rõ metadata runtime phải giữ: `expert_id`, `destination rank`, `slot`, `token_id`, `gate`, và dropped assignments. Trong production, `send` buffers sẽ được chuyển qua first `all-to-all`; expert outputs được chuyển ngược qua second `all-to-all` trước khi scatter.

```python
import math
import torch
import torch.nn.functional as F


def plan_top1_dispatch(tokens, router, expert_to_rank, capacity_factor=1.25):
    """Build a readable, fixed-capacity dispatch plan for one MoE layer.

    tokens:         [T, D] local token activations
    router:         module mapping D -> n_experts
    expert_to_rank: [n_experts] integer destination rank for every expert

    This is a teaching reference: Python loops and CPU metadata are intentional.
    """
    T, D = tokens.shape
    expert_to_rank = expert_to_rank.to(tokens.device)
    n_experts = expert_to_rank.numel()
    n_ranks = int(expert_to_rank.max().item()) + 1
    capacity = math.ceil(capacity_factor * T / n_experts)

    probs = F.softmax(router(tokens.float()), dim=-1)
    gates, expert_ids = probs.max(dim=-1)       # top-1 routing
    destinations = expert_to_rank[expert_ids]   # destination rank per token

    # Static slots make the padding visible: [rank, expert, slot, hidden].
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
        "send": send,                 # would be sent to destination ranks
        "token_ids": token_ids,       # needed to restore original order
        "gates": slot_gates,
        "expert_ids": expert_ids,
        "destinations": destinations,
        "used": used,
        "capacity": capacity,
        "dropped": dropped,
    }


def combine_top1_return(expert_outputs, plan, n_tokens):
    """After the return all-to-all, scatter top-1 expert outputs to tokens."""
    output = expert_outputs.new_zeros(n_tokens, expert_outputs.size(-1))
    valid = plan["token_ids"] >= 0
    restored_ids = plan["token_ids"][valid]
    restored_values = expert_outputs[valid] * plan["gates"][valid].unsqueeze(-1)
    output.index_copy_(0, restored_ids, restored_values)
    return output


# Example: 12 local tokens, 8 experts, 4 ranks; two experts reside on each rank.
torch.manual_seed(0)
T, D, E = 12, 16, 8
tokens = torch.randn(T, D)
router = torch.nn.Linear(D, E)
expert_to_rank = torch.tensor([0, 0, 1, 1, 2, 2, 3, 3])
plan = plan_top1_dispatch(tokens, router, expert_to_rank, capacity_factor=1.25)

print("capacity per expert:", plan["capacity"])
print("tokens selected per expert:", torch.bincount(plan["expert_ids"], minlength=E))
print("tokens admitted per expert:", plan["used"])
print("dropped token IDs:", plan["dropped"])
print("padded send shape:", tuple(plan["send"].shape))

# Placeholder only: real code dispatches plan["send"] to its destination ranks,
# runs each resident expert, then returns outputs to the source rank.
expert_outputs = plan["send"]  # identity expert, solely to test scatter metadata
restored = combine_top1_return(expert_outputs, plan, n_tokens=T)
assert restored.shape == tokens.shape
```

Đọc output theo thứ tự sau:

1. `torch.bincount(expert_ids)` là router demand trước capacity.
2. `used` là assignments được admit. Khác biệt giữa hai vector là overflow.
3. `send.shape == [n_ranks, n_experts, capacity, D]` cho thấy static padding: shape này có thể lớn hơn real token count.
4. `token_ids` là điều kiện để combine output về sequence order ban đầu. Bỏ metadata này sẽ làm output bị gán nhầm token.

Để mở rộng sang `top-k`, mỗi token tạo $k$ rows (token, expert, gate), capacity phải áp dụng theo chosen convention, và `combine` phải dùng `index_add_` thay vì `index_copy_` để cộng outputs từ nhiều experts. Đừng thay đổi code sang `top-k` rồi giả định network traffic, capacity, hay latency giữ nguyên.

## 7. Training và serving khác nhau ở đâu?

Cùng một MoE layer, nhưng token shape và objective hệ thống khác nhau đáng kể.

| Khía cạnh | Training | Prefill | Autoregressive decode |
|---|---|---|---|
| Tokens available cùng lúc | Nhiều tokens từ global batch | Toàn prompt tokens của batched requests | Khoảng một new token/request/step |
| Expert GEMM | Có thể batch lớn | Thường có batch tokens đáng kể | Dễ thành small GEMM |
| EP challenge chính | Balance, capacity, collective overlap | TTFT và prompt throughput | Per-token latency, batching, stragglers |
| Extra state chính | Activations/gradients/optimizer | KV-cache write | KV-cache read/write mỗi step |

`Prefill` thường có đủ prompt tokens để fill expert batches. `Decode` tạo ít token hơn mỗi step, nên experts có thể nhận tiny batches hoặc empty slots; all-to-all and synchronization khó amortize. Serving engine có thể continuous-batch requests để tăng tokens/step, nhưng điều đó trade off queueing delay, fairness, context lengths, and latency target. Đây là systems inference từ data-flow và small-batch limitation, không phải universal benchmark claim.[^moe-overview-2026]

## 8. Serving cost: bốn câu hỏi thay vì một con số `active parameters`

Khi một model card ghi “$A$ active / $P$ total parameters,” hãy tách bốn câu hỏi:

| Câu hỏi | Quantity cần xem | Vì sao `active parameters` chưa đủ? |
|---|---|---|
| Model có fit vào serving group không? | Total quantized weight bytes; replication/sharding | Inactive experts vẫn phải reside trên device group |
| Một token tốn bao nhiêu arithmetic? | Active expert FLOPs + attention/dense branch | Routing, attention và dense components vẫn chạy |
| Request nhanh bao nhiêu? | TTFT, time per output token, EP collective time | Cross-device traffic, padding và queueing có thể dominate |
| Cluster phục vụ bao nhiêu users? | Throughput under request mix, batch policy, KV-cache capacity | Decode workload và load skew thay đổi utilization |

Ngoài weights, serving còn cần `KV cache`, router buffers, dispatch/combine buffers, temporary activations, và runtime workspace. `KV cache` tăng theo active requests/context, còn expert weights gắn với total model capacity. Một optimization giảm KV state không tự giảm expert-weight memory; ngược lại MoE sparse compute không tự giảm KV cache. Đây là các memory terms khác nhau.[^moe-overview-2026][^deepseek-v2-2024]

DeepSeek-V2’s reported serving figures combine MoE, MLA, FP8 weights, KV-cache quantization, H800 hardware, and a specified serving configuration. Vì vậy, không thể lấy throughput đó làm bằng chứng rằng expert parallelism một mình tạo ra speedup.[^deepseek-v2-2024]

## 9. Cách đo đúng trước khi kết luận MoE “efficient”

Một benchmark hữu ích cần report đồng thời:

```text
Model/configuration
- total and active parameters; expert count, expert width, top-k
- expert_to_device placement; EP/TP/DP/PP degrees
- capacity rule, capacity factor, overflow/drop policy

Routing health
- per-expert and per-rank load distribution
- overflow/drop rate; padding fraction; selected-device fan-out

System time
- router/packing, dispatch all-to-all, expert GEMM, combine all-to-all
- their overlap and the slowest-rank time

Serving workload
- hardware/interconnect; weight precision
- request arrival rate, input/output length distributions, batch policy
- separate prefill throughput/TTFT and decode time per output token
- KV-cache policy and memory headroom
```

Chỉ so quality hoặc expert FLOPs là insufficient. Chỉ so tokens/s cũng insufficient nếu prompt/output mix, latency target, model quantization, hay batch policy khác nhau.

## 10. Troubleshooting map cho người mới

| Quan sát | Nguyên nhân có thể | Kiểm tra trước |
|---|---|---|
| Sparse FFN FLOPs thấp nhưng latency cao | `all-to-all`, small batches, padding | Time dispatch/combine versus expert GEMM; tokens/rank/step |
| Một rank luôn chậm | Hot experts đặt trên rank đó hoặc imbalance | Per-rank received assignments và expert histogram |
| Drop rate cao | Capacity quá nhỏ hoặc router collapse | Demand versus admitted load; capacity factor; balance loss |
| Drop rate thấp nhưng throughput kém | Capacity quá lớn/padding cao | Real tokens per slot; padded communication/GEMM work |
| Decode chậm hơn prefill dự kiến | Ít new tokens per step, collective overhead | Đo decode riêng; continuous batching; output-length mix |
| Model không fit dù active count nhỏ | Total experts/replicas và KV cache vượt memory | Quantized total weight bytes, EP group size, cache headroom |
| Router quality tốt nhưng network traffic cao | Selected experts spread across many devices | Device fan-out/token; placement; device-limited routing |

## 11. Bài tập thực hành

1. Chạy code với `capacity_factor` 1.0, 1.25, 2.0. So sánh `used`, `dropped`, và total static slots $E\times C$.
2. Đổi `expert_to_rank` để các experts phổ biến nằm trên ít ranks hơn. Đây chỉ là toy placement: quan sát `destinations`, rồi giải thích vì sao true placement phải dựa trên real routing statistics, không phải một batch.
3. Mở rộng plan sang `top-2`; verify mỗi token tạo tối đa hai admitted assignments và combine dùng weighted sum.
4. Với một real distributed runtime, profile riêng router/pack, dispatch, expert GEMM, combine. Không suy luận từ wall-clock tổng nếu chưa biết phần nào dominate.
5. Chạy benchmark prefill và decode riêng với cùng model, cùng precision, cùng serving policy. Thay đổi batch size/request mix trước khi kết luận về MoE serving.

## Relationships

- **Builds on:** [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md) for router, `top-k`, and basic capacity concepts.
- **Explains:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through an explicit beginner-level dispatch/combine and serving-cost model.
- **Operationalized by:** [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) with device-limited routing, device balance, and training-time dropping.
- **Specialized by:** [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md) with wave-scheduled fused expert-parallel execution.
- **Extends:** Stage 7, “Sparse capacity,” of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

The Switch implementation mechanics and capacity formula are compiled from a bundled Vietnamese overview that cites the Switch paper; the primary Switch paper is not present in `raw/`. DeepSeek-V2/V4 configuration and speed claims are author-reported and configuration-specific. The code is an educational single-process simulation: it does not measure collective performance, model quality, kernel utilization, or production serving latency.[^moe-overview-2026][^deepseek-v2-2024][^deepseek-v4-2026]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), Sections 7, 10–11, and 16; it cites Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022).
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.2–2.3 and 3.1.
[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Section 4.1.
