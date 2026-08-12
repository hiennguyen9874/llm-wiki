---
type: Synthesis
title: "DeepSeek-V2 → V3: efficient attention, sparse capacity, và co-design — khóa học cho người mới"
description: A beginner-first course that traces MLA and DeepSeekMoE from DeepSeek-V2 to V3, then separates V3's routing control, multi-token objective, FP8 numerical format, distributed schedule, and serving policy.
tags: [deepseek-v2, deepseek-v3, mla, mixture-of-experts, multi-token-prediction, fp8, distributed-training, co-design, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T13:48:02+07:00 }
sources:
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# DeepSeek-V2 → V3: `efficient attention`, `sparse capacity`, và `co-design`

DeepSeek-V2 đặt hai nền móng chính: `Multi-head Latent Attention` (MLA) giảm `KV cache` trên mỗi token nhưng vẫn giữ `token-addressable softmax attention`; `DeepSeekMoE` tăng tổng model capacity bằng nhiều `fine-grained routed experts` và một số `shared experts`, trong khi mỗi token chỉ activate một phần nhỏ experts. DeepSeek-V3 không thay hai nền móng đó bằng architecture hoàn toàn mới. V3 scale chúng lên, đổi cách giữ `load balance`, thêm `Multi-Token Prediction` (MTP), rồi đồng thiết kế `FP8`, `DualPipe`, `expert parallelism`, communication kernels và serving placement để model có thể train và deploy trên hệ thống cụ thể.[^deepseek-v2-2024][^deepseek-v3-2024]

> [!success] Sau bài này
> Bạn có thể:
> - giải thích MLA giảm `per-token KV state` như thế nào và vì sao cache vẫn là $O(T)$;
> - phân biệt `total parameters`, `activated parameters` và `expert communication` trong MoE;
> - so sánh V2 `auxiliary losses + token dropping` với V3 `routing bias + no token dropping`;
> - giải thích MTP là `training objective`, không phải attention architecture;
> - phân biệt `FP8 numerical format`, `DualPipe distributed schedule` và `redundant-expert serving policy`;
> - tạo một `V2→V3 diff` không gán whole-model result cho một component riêng lẻ.

Bài này là phần triển khai chi tiết cho Stage 9.2 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Nên hoàn thành [Baseline-to-bottleneck](baseline-to-bottleneck-frontier-model-reading-beginners-guide.md) trước; nếu chưa quen MLA hoặc MoE, xem [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) và [DeepSeekMoE expert design](deepseekmoe-expert-design-beginners-guide.md).

## 1. Cách nhìn tổng thể: model, objective và system không phải một thứ

Một câu như “DeepSeek-V3 dùng MLA, MoE, MTP, FP8 và DualPipe” đúng nhưng chưa giải thích được design. Mỗi item tác động vào một layer khác nhau:

| Layer phân tích | Câu hỏi | DeepSeek example |
|---|---|---|
| `architecture` | Learned computation graph thay đổi ở đâu? | MLA, shared/routed experts |
| `routing control` | Expert assignment được giữ cân bằng thế nào? | V2 auxiliary losses; V3 adaptive bias |
| `training objective` | Loss cung cấp training signal gì? | next-token loss + MTP loss |
| `numerical format` | Tensor nào dùng precision và scale nào? | FP8 GEMM, BF16/FP32 exceptions |
| `distributed system` | Work và communication được đặt/schedule ra sao? | EP, PP, DualPipe, all-to-all kernels |
| `serving policy` | Request-time load được quản lý thế nào? | prefill/decode separation, redundant experts |

Sai lầm phổ biến là nối trực tiếp:

```text
FP8 → model hiểu tốt hơn
DualPipe → attention rẻ hơn về algorithm
MoE → latency chắc chắn thấp hơn
MTP → sinh nhiều token mà không cần verification
```

Các suy luận này không đúng. `FP8` và `DualPipe` chủ yếu thay physical execution; MoE chuyển dense FFN compute thành sparse compute nhưng tạo weight-memory và communication costs; MTP thêm training targets và chỉ trở thành draft mechanism khi có speculative-decoding verification.

## 2. Dense baseline và ba loại tài nguyên

Trong một pre-norm decoder block đơn giản:

$$
u=x+\operatorname{Attention}(\operatorname{Norm}(x)),
$$

$$
y=u+\operatorname{FFN}(\operatorname{Norm}(u)).
$$

DeepSeek lineage tối ưu hai sublayers khác nhau:

- MLA tác động vào `Attention`: giảm retained KV representation;
- DeepSeekMoE tác động vào `FFN`: tăng sparse parameter capacity.

Nhưng end-to-end efficiency còn phụ thuộc ba loại tài nguyên:

1. **State:** KV cache, activations, gradients, optimizer states, total expert weights.
2. **Compute:** attention GEMMs, active expert GEMMs, backward, optimizer updates.
3. **Movement:** HBM reads, token dispatch/combine, NVLink/InfiniBand traffic, pipeline transfers.

Một optimization thường chuyển cost thay vì xóa cost. MLA giảm KV bytes trên mỗi token nhưng vẫn đọc history; MoE giảm active expert compute nhưng thêm routing và `all-to-all`; FP8 giảm bytes và tăng low-precision throughput nhưng cần scaling, accumulation và higher-precision exceptions.

## 3. DeepSeek-V2: hai nền móng architecture

DeepSeek-V2 được report là model 60 layers, 236B total parameters và 21B activated parameters mỗi token. Attention dùng 128 heads, `head_dim=128`, KV latent width 512, query latent width 1,536 và decoupled rotary width 64. Ngoại trừ FFN đầu tiên, mỗi FFN có hai shared experts và 160 routed experts; mỗi token chọn sáu routed experts.[^deepseek-v2-2024]

### 3.1 MLA: nén representation, không xóa token slots

Với hidden state $h_t$, MLA tạo joint KV latent:

$$
c_t^{KV}=W^{DKV}h_t,
$$

rồi tạo content key/value:

$$
k_t^C=W^{UK}c_t^{KV},\qquad v_t^C=W^{UV}c_t^{KV}.
$$

Thay vì cache full K/V của mọi heads, inference cache $c_t^{KV}$. Matrix associativity cho phép absorb key up-projection vào query path và value up-projection vào output path, nên không nhất thiết reconstruct full K/V của toàn prefix ở mỗi decode step.[^deepseek-v2-2024]

RoPE tạo một vấn đề: nếu rotation phụ thuộc position nằm trực tiếp trên content key sau up-projection, projection không còn absorb được bằng một matrix cố định. MLA vì thế tách `content path` khỏi `position path`:

$$
q_{t,i}=[q_{t,i}^{C};q_{t,i}^{R}],\qquad
k_{t,i}=[k_{t,i}^{C};k_t^{R}].
$$

Cache thực tế giữ:

```text
per token, per layer = [joint KV latent c_t^KV | shared rotary key k_t^R]
```

Với $L$ layers, context $T$, batch $B$ và $p$ bytes/element:

$$
M_{MLA}=BLT(d_c+d_h^R)p.
$$

Standard MHA xấp xỉ:

$$
M_{MHA}=BLT(2n_hd_h)p.
$$

Cả hai đều có thừa số $T$. MLA giảm **slope** của memory growth, không biến cache thành fixed-state. Query mới vẫn tạo score riêng cho từng prefix position, nên retrieval vẫn `token-addressable`.

> [!important] Scope đúng
> “MLA giảm KV state mỗi token” là claim architecture/accounting. “DeepSeek-V2 đạt throughput cao hơn” là whole serving-stack measurement còn chứa quantization, batching, kernels và deployment configuration.

### 3.2 DeepSeekMoE: sparse compute, dense capacity

Một dense FFN chạy cùng một parameter set cho mọi token. DeepSeekMoE dùng:

- `shared experts`: luôn chạy, dành capacity cho patterns phổ biến;
- `routed experts`: router chỉ chọn top-$k$ cho từng token;
- `fine-grained experts`: nhiều experts nhỏ hơn thay vì ít experts lớn.

Dạng khái quát:

$$
h'_t=u_t+
\sum_{i=1}^{N_s}\operatorname{FFN}^{(s)}_i(u_t)+
\sum_{i=1}^{N_r}g_{i,t}\operatorname{FFN}^{(r)}_i(u_t).
$$

Nếu một expert lớn được chia thành $m$ experts nhỏ, rồi top-$K$ trở thành top-$mK$, nominal active FFN compute có thể gần giữ nguyên trong khi router có nhiều tổ hợp functions hơn. Đây là `conditional computation`: total weights lớn, nhưng mỗi token chỉ dùng một subset.[^deepseek-v2-2024]

Ba số không được trộn lẫn:

| Quantity | Ý nghĩa | Cost liên quan |
|---|---|---|
| `total parameters` | Toàn bộ learned capacity | storage, checkpoint, deployment weight memory |
| `activated parameters` | Parameters tham gia forward của một token | nominal per-token compute |
| `assignments/devices` | Experts và devices nhận token | dispatch, combine, straggler, network traffic |

`21B activated` không có nghĩa deployment chỉ cần giữ 21B weights. Một request batch có thể gọi nhiều experts khác nhau; serving system vẫn phải place total expert weights trên deployment unit.

### 3.3 V2 routing controls

Fine-grained routing tạo nguy cơ một token fan out tới nhiều devices và một số devices nhận quá nhiều work. V2 dùng:

- `device-limited routing`: target experts của một token nằm trên tối đa ba devices trong reported configuration;
- expert-, device- và communication-level auxiliary balance losses;
- per-device capacity factor 1.0 và drop low-affinity assignments khi overflow trong phần lớn training sequences;
- không drop trong evaluation.[^deepseek-v2-2024]

Đây là architecture–system coupling đầu tiên: router không chỉ học semantic affinity; placement và communication budget còn giới hạn feasible assignments.

## 4. DeepSeek-V3 giữ gì và thay gì?

V3 được report là model 61 layers, 671B total và 37B activated parameters mỗi token. Nó vẫn dùng 128 attention heads, `head_dim=128`, KV latent 512, query latent 1,536 và rotary width 64. Ba FFNs đầu là dense; mỗi MoE layer sau đó có một shared expert, 256 routed experts, và mỗi token chọn tám routed experts.[^deepseek-v3-2024]

### V2→V3 diff

| Item | V2 | V3 | Primary label |
|---|---|---|---|
| Attention | MLA | giữ MLA với cùng reported latent widths | `architecture continuity` |
| Total/active scale | 236B / 21B | 671B / 37B | `scale/configuration` |
| MoE experts | 2 shared + 160 routed; top-6 | 1 shared + 256 routed; top-8 | `architecture configuration` |
| Initial dense FFNs | first layer | first three layers | `architecture configuration` |
| Router affinity | softmax form trong V2 report | sigmoid affinity, normalize selected affinities | `routing architecture` |
| Main load control | multiple auxiliary losses | adaptive selection bias; tiny sequence loss remains | `routing control` |
| Cross-node bound | at most 3 devices/token | at most 4 nodes/token | `distributed constraint` |
| Token dropping | training capacity/drop policy | report states no token dropping | `training system policy` |
| Objective | ordinary next-token objective | next-token + one-depth sequential MTP | `training objective` |
| Precision/system | V2 serving includes low precision; training stack khác | fine-grained FP8 training + DualPipe/custom communication | `numerics + distributed system` |
| Serving balance | deployment-specific stack | prefill/decode split + redundant high-load experts | `serving policy` |

Bảng này cho thấy V3 không phải “MLA v2”. Attention mechanism cốt lõi được giữ lại; phần mới nổi bật nằm ở sparse scaling, balancing, training signal và execution stack.

## 5. `Auxiliary-loss-free` balancing: feedback controller cho selection

V3 tính affinity của token $t$ với routed expert $i$ bằng sigmoid:

$$
s_{i,t}=\operatorname{Sigmoid}(u_t^Te_i).
$$

Nó thêm per-expert bias $b_i$ **chỉ khi chọn top-$k$**:

$$
S_t=\operatorname{TopK}_i(s_{i,t}+b_i,K).
$$

Nhưng output gate của expert đã chọn vẫn dùng unmodified affinity:

$$
g_{i,t}=\frac{s_{i,t}}{\sum_{j\in S_t}s_{j,t}},\qquad i\in S_t.
$$

Cuối mỗi training step:

```text
expert overloaded  → b_i ← b_i - γ
expert underloaded → b_i ← b_i + γ
```

Bias vì thế thay `assignment eligibility`, không trực tiếp phóng đại contribution của expert output. Có thể xem nó như feedback controller dùng observed batch load để điều chỉnh routing ở step sau.[^deepseek-v3-2024]

Trong reported V3 run, $\gamma=0.001$ cho 14.3T tokens đầu rồi bằng 0 cho 500B cuối. V3 vẫn giữ sequence-wise balance loss rất nhỏ với $\alpha=0.0001$ để tránh extreme imbalance trong một sequence. Vì vậy `auxiliary-loss-free` nghĩa là **main batch-level balance không dựa vào auxiliary loss**, không phải mọi balance loss đều biến mất.[^deepseek-v3-2024]

### V2 và V3 giải hai bài toán hơi khác nhau

- V2 auxiliary losses đưa balance pressure vào optimization objective; capacity/drop bảo vệ bounded work.
- V3 bias controller tác động trực tiếp vào top-$k$ assignment dựa trên actual load; node-limited routing bảo vệ communication; report cho biết không drop token.

Không có cơ sở để suy ra routing bias luôn tốt hơn trên mọi data, batch size, expert count hoặc hardware. Controller có update speed, delayed statistics và domain-shift risk; inference traffic còn có thể khác training distribution.

## 6. MTP: thêm target tương lai nhưng vẫn giữ causal chain

Ordinary causal language modeling dùng hidden state tại position $i$ để predict $t_{i+1}$. V3 thêm sequential MTP modules. Ở depth $k$, module kết hợp representation từ depth trước với embedding của token $t_{i+k}$:

$$
h_i'^k=M_k[
\operatorname{RMSNorm}(h_i^{k-1});
\operatorname{RMSNorm}(\operatorname{Emb}(t_{i+k}))
],
$$

sau đó chạy một Transformer block riêng:

$$
h_{1:T-k}^{k}=\operatorname{TRM}_k(h_{1:T-k}'^k),
$$

và shared output head predict $t_{i+k+1}$. Tổng MTP loss là:

$$
\mathcal{L}_{MTP}=\frac{\lambda}{D}
\sum_{k=1}^{D}\mathcal{L}_{MTP}^{k}.
$$

V3 dùng $D=1$: ngoài next token, model có thêm một prediction depth cho token tiếp theo nữa. Loss weight được report là 0.3 trong 10T tokens đầu và 0.1 trong 4.8T tokens còn lại.[^deepseek-v3-2024]

Hai vai trò phải tách riêng:

1. **Training:** densify prediction signals và khuyến khích representation hữu ích cho tương lai xa hơn; đây là mục tiêu chính trong report.
2. **Inference:** MTP module có thể tạo draft tokens cho `speculative decoding`, nhưng target model vẫn phải verify để giữ target sampling distribution. Nếu không dùng speculative decoding, module có thể bị bỏ khi deploy.

MTP không làm main attention từ quadratic thành linear, không giảm KV cache, và không tự bảo đảm 2× generation speed.

## 7. FP8: `mixed precision framework`, không phải “mọi tensor đều 8-bit”

V3 chạy nhiều GEMMs bằng FP8 nhưng giữ các phần nhạy cảm ở precision cao hơn. Report mô tả:

- activation scales theo tile `1×128` — mỗi token, mỗi 128 channels;
- weight scales theo block `128×128`;
- online scale calculation thay vì chỉ dùng delayed history;
- E4M3 cho các FP8 tensor roles;
- promote partial accumulation sang FP32 trên CUDA cores sau mỗi 128 inner-dimension elements;
- BF16 AdamW moment states, nhưng FP32 master weights và gradients;
- attention, normalization, gating và một số sensitive paths không bị ép đồng loạt xuống FP8.[^deepseek-v3-2024]

### Vì sao scaling granularity quan trọng?

Với symmetric quantization đơn giản:

$$
q=\operatorname{clip}(\operatorname{round}(x/s),q_{min},q_{max}),
\qquad \hat{x}=sq.
$$

Nếu một scale $s$ dùng cho tensor rất lớn, một outlier có thể kéo scale lên, khiến phần lớn values nhỏ mất resolution. Tile/block scaling cô lập outliers tốt hơn nhưng cần lưu nhiều scales và kernel phải support dequantization theo groups.

Low precision vì thế là co-design giữa:

```text
format + scale granularity + accumulation + kernel + hardware + stability tests
```

Chỉ đổi dtype trong PyTorch không tái tạo V3 FP8 framework. Reported FP8 ablations cũng nhỏ hơn full V3 và là author-run evidence.

## 8. Vì sao MoE cần `DualPipe` và custom all-to-all?

Trong `expert parallelism`, experts nằm trên nhiều GPUs. Mỗi MoE layer cần:

```text
router
  → dispatch token representations tới expert GPUs
  → expert MLP computation
  → combine weighted outputs về token owners
```

`dispatch` và `combine` thường là all-to-all-like communication. Nếu chạy tuần tự:

$$
time\approx time_{attention}+time_{dispatch}+time_{MLP}+time_{combine},
$$

GPU/network có nhiều khoảng chờ. V3 report dùng 16-way pipeline parallelism, 64-way expert parallelism trên tám nodes và ZeRO-1 data parallelism, không dùng tensor parallelism trong training configuration.[^deepseek-v3-2024]

`DualPipe`:

- feed microbatches từ hai đầu pipeline;
- tách backward thành `backward for input` và `backward for weights`;
- rearrange attention, dispatch, MLP, combine và pipeline communication;
- overlap forward/backward compute với communication để giảm visible bubble.

Custom kernels khai thác topology không đồng nhất:

- cross-node: InfiniBand;
- intra-node: NVLink/NVSwitch;
- token bị giới hạn ở tối đa bốn nodes;
- traffic đi tới same-index GPU trên target node qua IB rồi forward tới expert GPU qua NVLink;
- report cấp 20 SMs cho mười communication channels.[^deepseek-v3-2024]

> [!warning] “Hidden communication” không có nghĩa communication miễn phí
> Overlap chỉ che latency khi có đủ independent compute, phù hợp timing, bandwidth và SM budget. Network bytes vẫn tồn tại; communication kernels còn tranh SM/L2 resources với compute. Claim phụ thuộc H800 topology và workload.

## 9. Serving là một design layer riêng

Training balance không bảo đảm production traffic balance. Domain/request mix có thể làm một số experts nóng hơn. V3 report tách `prefill` và `decode`, rồi periodically duplicate high-load experts:

- prefill deployment unit được report là 32 GPUs;
- decode deployment unit được report là 320 GPUs;
- redundant experts được chọn từ observed online load;
- expert placement và microbatch overlap khác nhau giữa prefill và decode.[^deepseek-v3-2024]

Đây là `serving policy`, không phải learned model architecture. Nó có thể giảm straggler nhưng tăng weight replicas, deployment-unit size và operational complexity.

## 10. Co-design map: một constraint kéo theo nhiều quyết định

Có thể trace V3 bằng dependency chain sau:

```text
Nhiều fine-grained experts
  → sparse active compute nhưng nhiều expert destinations
  → expert parallelism + dispatch/combine traffic
  → node-limited routing + load controller
  → custom IB/NVLink all-to-all
  → DualPipe overlap để che communication
  → FP8 storage/dispatch/GEMM để giảm bytes và tăng throughput
  → precision exceptions + fine-grained scales để giữ stability
  → redundant experts khi inference distribution làm load lệch
```

Không item nào đứng hoàn toàn độc lập:

- tăng top-$k$ có thể tăng active capacity nhưng cũng tăng assignments;
- siết node limit giảm network fan-out nhưng thu hẹp feasible expert set;
- routing bias cân load nhưng có thể đổi expert choice;
- FP8 giảm traffic nhưng yêu cầu scale metadata và numerical safeguards;
- overlap giảm exposed latency nhưng cần đủ compute và memory cho concurrent work.

Đó là ý nghĩa của `co-design`: architecture, router, numerical representation, placement, network topology và schedule được chọn cùng nhau quanh một bottleneck thực tế.

## 11. PyTorch lab: kiểm tra accounting, routing controller và MTP targets

Lab dưới đây không tái tạo DeepSeek. Nó cung cấp ba probes nhỏ, runnable trên CPU:

1. so sánh raw MHA/MLA cache accounting;
2. mô phỏng V3-style routing bias update;
3. tạo đúng shifted targets cho one-depth MTP.

```python
import torch
import torch.nn.functional as F


def cache_bytes(batch, layers, seq_len, elements_per_token_layer, dtype_bytes=2):
    return batch * layers * seq_len * elements_per_token_layer * dtype_bytes


def compare_cache(batch=1, layers=32, seq_len=8192,
                  n_heads=32, head_dim=128, d_latent=512, d_rope=64):
    mha_elems = 2 * n_heads * head_dim
    mla_elems = d_latent + d_rope
    return {
        "MHA_GiB": cache_bytes(batch, layers, seq_len, mha_elems) / 2**30,
        "MLA_GiB": cache_bytes(batch, layers, seq_len, mla_elems) / 2**30,
        "element_ratio": mha_elems / mla_elems,
    }


@torch.no_grad()
def update_routing_bias(bias, load, gamma=1e-3):
    """Toy sign controller; a production rule must define target/tie handling."""
    target = load.float().mean()
    bias[load > target] -= gamma
    bias[load < target] += gamma
    return bias


def route_with_bias(router_logits, bias, k=2):
    # V3 uses sigmoid affinity; bias affects selection only.
    affinity = router_logits.sigmoid()
    expert_ids = (affinity + bias).topk(k, dim=-1).indices

    # Output weights come from unmodified affinity.
    selected_affinity = affinity.gather(1, expert_ids)
    gates = selected_affinity / selected_affinity.sum(dim=-1, keepdim=True)
    load = torch.bincount(expert_ids.flatten(), minlength=affinity.shape[-1])
    return expert_ids, gates, load


def next_token_and_mtp_targets(token_ids):
    """For D=1: main predicts x[t+1], MTP depth 1 predicts x[t+2]."""
    if token_ids.ndim != 2 or token_ids.shape[1] < 3:
        raise ValueError("expected shape (batch, sequence>=3)")
    main_input = token_ids[:, :-1]
    main_target = token_ids[:, 1:]
    mtp_input_positions = token_ids[:, :-2]
    mtp_known_next_token = token_ids[:, 1:-1]  # Emb(t_{i+1}) in depth 1
    mtp_target = token_ids[:, 2:]
    return main_input, main_target, mtp_input_positions, mtp_known_next_token, mtp_target


print(compare_cache())

torch.manual_seed(0)
logits = torch.randn(12, 4)
bias = torch.zeros(4)
for step in range(5):
    ids, gates, load = route_with_bias(logits, bias, k=2)
    print(f"step={step} load={load.tolist()} bias={bias.tolist()}")
    update_routing_bias(bias, load)

x = torch.tensor([[10, 11, 12, 13, 14]])
main_x, main_y, mtp_pos, mtp_known, mtp_y = next_token_and_mtp_targets(x)
print("main target:", main_y.tolist())       # [11, 12, 13, 14]
print("MTP known token:", mtp_known.tolist()) # [11, 12, 13]
print("MTP target:", mtp_y.tolist())          # [12, 13, 14]
```

### Cách đọc output

- `element_ratio` chỉ là raw retained-state ratio theo dimensions đã chọn; không phải latency speedup.
- Mỗi routing step giữ nguyên logits để cô lập controller. Bias dần phạt experts quá tải và ưu tiên experts nhẹ tải.
- `gates` không lấy từ `affinity + bias`; bias chỉ thay selection.
- One-depth MTP target lệch hai positions so với original token position, nhưng module được cung cấp embedding của token trung gian để giữ causal chain.

### Các giới hạn cố ý của lab

- Không implement MLA projections/RoPE hay cached decode; xem [MLA course](mla-token-addressable-memory-beginners-guide.md) cho implementation đầy đủ hơn.
- Không dispatch expert computation hoặc capacity/drop; xem [MoE capacity lab](moe-capacity-load-balancing-stability-lab.md).
- Không mô phỏng `all-to-all`, `DualPipe` hay H800 timing.
- Không cast thật sang FP8; CPU toy quantization không đại diện Tensor Core accumulation.

## 12. Evidence ledger cho V2→V3

| Mechanism | Replaced baseline | Expected trade-off | Evidence scope |
|---|---|---|---|
| MLA joint KV latent + decoupled RoPE | full per-head K/V cache | giảm elements/token; vẫn $O(T)$ cache và global retrieval work | equations, accounting, author-run ablations[^deepseek-v2-2024] |
| Fine-grained shared/routed experts | dense FFN | tăng total capacity với sparse active compute; thêm total-weight memory và routing/communication | architecture + author-run comparisons[^deepseek-v2-2024] |
| Adaptive routing bias | primary batch balance pressure từ auxiliary losses | assignment balance ít tác động trực tiếp vào task loss hơn; thêm feedback dynamics | V3 mechanism + author-run ablations[^deepseek-v3-2024] |
| One-depth MTP | chỉ next-token objective | thêm future-token signal; thêm training module/compute | V3 objective + author-run ablations[^deepseek-v3-2024] |
| Fine-grained FP8 | higher-precision GEMMs/storage | giảm bytes/tăng low-precision throughput; quantization và stability complexity | smaller-model FP8 ablations + full-run report[^deepseek-v3-2024] |
| DualPipe + custom all-to-all | less-overlapped PP/EP execution | giảm exposed communication/bubbles; topology- và schedule-dependent | author system design, không có independent reproduction trong wiki[^deepseek-v3-2024] |
| Redundant serving experts | một physical copy/expert | giảm runtime load skew; tăng weight copies và deployment complexity | reported deployment policy[^deepseek-v3-2024] |

## 13. Bài tập Stage 9.2

### Bài 1 — classification

Gán đúng một primary label cho từng item: `MLA`, `query compression`, `routing bias`, `MTP loss`, `FP8 tile scaling`, `DualPipe`, `node-limited routing`, `redundant experts`. Với mỗi item, ghi thêm phase hưởng lợi chính: `training`, `prefill`, `decode` hoặc `serving operations`.

### Bài 2 — memory slope

Dùng `compare_cache` để plot MHA và MLA raw cache từ 1K đến 128K context. Trả lời:

- hai đường có complexity theo $T$ thế nào?
- ratio có đổi theo $T$ không?
- tại sao ratio memory không phải ratio throughput?

### Bài 3 — routing stress test

Tạo logits làm expert 0 vượt trội mạnh. Plot load và bias qua 100 steps với ba giá trị $\gamma$. Quan sát:

- quá nhỏ: controller phản ứng chậm;
- quá lớn: assignments có thể oscillate;
- batch nhỏ: load statistics noisy hơn.

Sau đó giải thích vì sao production controller cần distributed load aggregation và rule rõ cho ties/target load.

### Bài 4 — MTP alignment test

Với sequence `[A, B, C, D, E]`, tự viết bảng:

| Position representation | Main target | MTP depth-1 known token | MTP target |
|---|---|---|---|

Kiểm tra bằng code để tránh off-by-one. Giải thích vì sao đưa `known token` trong training không đồng nghĩa inference được nhìn thấy future ground truth.

### Bài 5 — co-design failure analysis

Giả sử bỏ từng component sau và dự đoán bottleneck quay lại:

1. bỏ node-limited routing;
2. giữ MoE nhưng bỏ communication overlap;
3. dùng one-scale-per-tensor FP8;
4. không duplicate hot experts khi serving traffic shift;
5. tăng expert count nhưng giữ network và deployment unit không đổi.

Mỗi câu trả lời phải nêu `state`, `compute` hoặc `movement` nào tăng, và evidence nào còn thiếu để biết end-to-end effect.

## 14. Những hiểu lầm cần tránh

1. **“V3 thay attention của V2.”** V3 report giữ MLA; thay đổi lớn nằm ở scale, routing, objective và systems.
2. **“MLA là fixed-state.”** MLA vẫn thêm latent + rotary key cho từng token.
3. **“671B parameters chạy mỗi token.”** Report phân biệt 671B total và 37B activated.
4. **“Auxiliary-loss-free nghĩa là không có balance loss.”** V3 vẫn có tiny sequence-wise auxiliary loss.
5. **“Không drop token nghĩa là không cần capacity planning.”** Load, buffer, communication và serving skew vẫn phải quản lý.
6. **“MTP sinh hai token chính xác trong một pass.”** Training objective và speculative-decoding proposal là hai vai trò khác nhau; proposal cần verification.
7. **“FP8 là cast toàn model sang 8-bit.”** V3 dùng mixed precision, group scales và higher-precision accumulation/state.
8. **“DualPipe giảm algorithmic FLOPs.”** Nó chủ yếu schedule/overlap work và communication.
9. **“Author-reported whole-model quality chứng minh từng component.”** Data, scale, objective và system thay đổi cùng lúc.
10. **“Ít active FLOPs luôn cho latency thấp.”** Sparse execution còn phụ thuộc batch size, weight reads, all-to-all và stragglers.

## 15. Deliverable trước khi sang Stage 9.3

Tạo một trang `V2→V3 diff` gồm đúng năm nhóm:

```text
Architecture:
  MLA continuity; MoE configuration changes

Routing / objective:
  adaptive bias; tiny sequence loss; one-depth MTP

Numerical format:
  fine-grained FP8 + precision exceptions

Distributed system:
  PP/EP/DP layout; node limit; DualPipe; all-to-all kernels

Serving policy:
  prefill/decode split; redundant experts
```

Với mỗi row, bắt buộc có:

- baseline bị thay hoặc component được giữ;
- bottleneck mục tiêu;
- cost/failure mode mới;
- phase hưởng lợi;
- evidence type và setup;
- marker `documented`, `synthesis`, hoặc `uncertain`.

Nếu bạn làm đúng, kết luận sẽ không phải “V3 tốt hơn vì nhiều innovations”, mà là một causal map có scope: **MLA giảm per-token KV state; sparse experts tách capacity khỏi active compute; routing và communication controls làm sparse execution khả thi; MTP đổi training signal; FP8 và DualPipe đổi cách hệ thống thực thi graph đó.**

## Relationships

- **Elaborates:** Stage 9.2 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).
- **Builds on:** [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md), [Multi-head Latent Attention](multi-head-latent-attention.md), và [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md).
- **Uses:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md), [Sequential multi-token prediction](sequential-multi-token-prediction.md), và [DeepSeek-V3 training systems and FP8](deepseek-v3-training-systems-and-fp8.md) để phân tách routing, objective, numerical và system layers.
- **Prepares for:** Stage 9.3, nơi growing token-addressable MLA cache được so với fixed-state recurrent memory và hybrid retrieval.

## Evidence limits

Bài này là pedagogical synthesis từ hai DeepSeek technical reports và các concept đã compile trong wiki, không phải independent reproduction. Architecture equations và reported configurations là documented knowledge; cách nhóm chúng thành `state–compute–movement`, dependency chain co-design và curriculum exercises là synthesis. Headline cost, cache, throughput, stability và benchmark results đều do authors report; full V2/V3 comparisons thay đổi scale, data, objective và systems cùng lúc, nên không isolate causal contribution của từng component. Code là diagnostic toy implementation, không tái tạo production MLA, distributed MoE, DualPipe hoặc FP8 kernels.

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 1–3 and Appendices B–D.

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Sections 1–5 and Appendix A, including the [FP8 section](../raw/arXiv-2412.19437v2/content/fp8.tex).
