---
type: Synthesis
title: "Kimi K3 theo information path — khóa học kiến trúc tích hợp cho người mới"
description: A beginner-first course that traces Kimi K3 through sequence memory, global token retrieval, depth retrieval, sparse channel mixing, and native vision input, with a state-growth ledger and runnable PyTorch toy model.
tags: [kimi-k3, kda, mla, attention-residuals, latentmoe, multimodal, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-12T14:01:33+07:00
sources:
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: kimi-linear-modeling-2026
    resource: ../raw/kimi-k3-sources/modeling_kimi_linear.py
    title: "Kimi K3 text-backbone reference modeling code"
  - id: kimi-k3-modeling-2026
    resource: ../raw/kimi-k3-sources/modeling_kimi_k3.py
    title: "Kimi K3 multimodal reference modeling code"
  - id: kimi-k3-processor-2026
    resource: ../raw/kimi-k3-sources/kimi_k3_processor.py
    title: "Kimi K3 multimodal processor reference code"
---

# Kimi K3 theo information path — khóa học kiến trúc tích hợp cho người mới

Kimi K3 nên được đọc như một **integrated information-flow architecture**, không phải một model có đúng một “headline novelty”. Trong backbone, `KDA` giữ fixed-size recurrent memory dọc sequence; periodic `Gated MLA` khôi phục global token-addressable retrieval; `Block AttnRes` chọn representation dọc depth; `Stable LatentMoE` trộn channel qua một expert pool sparse; còn `MoonViT-V2` biến visual input thành visual tokens trong cùng token stream. Năm path này bổ sung cho nhau nhưng không xóa trade-off của nhau.[^kimi-k3-2026]

> [!success] Learning outcomes
> Sau bài này, bạn có thể:
> - đọc Kimi K3 theo năm `information path`: sequence, token, depth, channel và modality;
> - vẽ một macrocycle `KDA → KDA → KDA → Gated MLA` và đặt `AttnRes` cùng `Stable LatentMoE` đúng chỗ;
> - giải thích vì sao `KDA` là fixed-state nhưng toàn bộ K3 không có constant-size context state;
> - phân biệt `token retrieval` của MLA với `depth retrieval` của AttnRes;
> - phân biệt `sparse activation` với việc chỉ lưu active expert weights;
> - trace một image từ patch encoder đến shared language backbone;
> - lập `state-growth ledger` cho prefill và autoregressive decode;
> - chạy một PyTorch toy model để quan sát shape, routing và cache growth;
> - tách documented mechanism, code-level observation, author-reported result và synthesis.

## 1. Prerequisites và cách đặt câu hỏi

Nên học trước:

1. [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md);
2. [GPT-2 → Kimi Linear: changing the memory model](gpt2-to-kimi-linear-memory-model-beginners-course.md);
3. [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md);
4. [Mixture-of-Experts và sparse routing](mixture-of-experts-sparse-routing-beginners-guide.md).

Đừng bắt đầu bằng câu “K3 dùng attention gì?”. Hãy hỏi:

> Với mỗi token, information đi qua path nào, được lưu ở state nào, được retrieve theo axis nào, và resource nào tăng khi sequence hoặc depth tăng?

| Axis | Câu hỏi đúng | Mechanism chính trong K3 |
|---|---|---|
| `Sequence memory` | History được nén và cập nhật qua token time như thế nào? | KDA |
| `Token retrieval` | Query có thể chấm điểm các token slot cũ ở đâu? | Gated MLA |
| `Depth retrieval` | Layer hiện tại chọn representation từ block trước ra sao? | Block AttnRes |
| `Channel mixing` | Token dùng capacity FFN nào mà không chạy toàn bộ experts? | Stable LatentMoE |
| `Modality input` | Image/video trở thành input của shared backbone thế nào? | MoonViT-V2 + projector |

`Information path` là cách đọc do bài này tổng hợp. Primary report tự tổ chức architecture theo token, layer, channel mixing và native vision; bài học tách thêm `KDA sequence memory` khỏi `MLA token retrieval` để làm rõ hai memory semantics khác nhau.[^kimi-k3-2026]

## 2. Bức tranh toàn cục

### 2.1 Những con số cần biết, không cần học thuộc

Kimi K3 được report là native multimodal MoE model với:

- 2.78T total parameters và 104.2B activated parameters;
- hidden width 7,168;
- 93 backbone layers;
- 69 KDA layers và 24 MLA layers;
- 896 routed experts, top-16 mỗi token, cùng 2 shared experts;
- latent MoE width 3,584;
- 27-layer, khoảng 401M-parameter vision encoder;
- context window được report đến một triệu tokens.[^kimi-k3-2026]

Những con số này mô tả configuration cụ thể. Chúng không tự chứng minh quality, efficiency hay khả năng dùng chính xác mọi token trong context.

### 2.2 Một macrocycle

Repeated pattern của sequence mixer là `3:1`:

```text
input representation
       │
       ├─ KDA layer ─ Stable LatentMoE
       ├─ KDA layer ─ Stable LatentMoE
       ├─ KDA layer ─ Stable LatentMoE
       └─ Gated MLA ─ Stable LatentMoE
                         │
                    next macrocycle
```

Một Gated MLA bổ sung nằm cuối backbone để final layer luôn thực hiện global attention. Layer đầu tiên dùng dense FFN; các attention layers còn lại được ghép với Stable LatentMoE trong reported architecture.[^kimi-k3-2026]

Sơ đồ trên vẫn chưa có depth path. Với `Block AttnRes`, input trước attention và trước FFN không nhất thiết chỉ là residual sum gần nhất; module có thể tạo softmax mixture từ embedding, completed block summaries và partial sum của block hiện tại.[^kimi-k3-2026][^kimi-linear-modeling-2026]

### 2.3 Pseudocode tích hợp

Đây là pseudocode để đọc data flow, không phải production implementation:

```python
block_sources = [token_or_multimodal_embeddings]
prefix_sum = token_or_multimodal_embeddings

for layer in backbone:
    # Depth retrieval before sequence mixing
    h = attn_res_select(block_sources, prefix_sum)

    # Sequence path: one of two different memory models
    if layer.is_kda:
        a, kda_state = kda(h, kda_state)
    else:
        a, mla_cache = gated_mla(h, mla_cache)
    prefix_sum = prefix_sum + a

    # Depth retrieval again before channel mixing
    h = attn_res_select(block_sources, prefix_sum)

    # Sparse width/channel path
    f = stable_latent_moe(h)
    prefix_sum = prefix_sum + f

    if layer.ends_attnres_block:
        block_sources.append(prefix_sum)
        prefix_sum = zeros_like(prefix_sum)

output = final_attn_res_select(block_sources, prefix_sum)
```

Reference code xác nhận AttnRes được áp dụng trước attention và trước FFN/MoE, nhưng chi tiết block-boundary bookkeeping khác pseudocode rút gọn trên. Code public là reference architecture path, không phải tài liệu đầy đủ về production kernels.[^kimi-linear-modeling-2026]

## 3. Path 1 — KDA: fixed-state sequence memory

### 3.1 KDA đang thay thế điều gì?

Conventional KV-cached softmax attention giữ một K/V entry cho mỗi token. KDA thay sequence-growing token slots ở phần lớn layers bằng recurrent matrix state. Với một head:

$$
S_t=
\left(I-\beta_t k_tk_t^T\right)
\operatorname{Diag}(\alpha_t)S_{t-1}
+\beta_tk_tv_t^T,
\qquad
\tilde o_t=S_t^Tq_t.
$$

Trong đó:

- $S_t\in\mathbb{R}^{d_k\times d_v}$ là associative state;
- $\alpha_t\in(0,1)^{d_k}$ là channel-wise retention;
- $\beta_t\in(0,1)$ điều khiển write strength;
- $k_tk_t^T$ tạo key-addressed correction;
- query $q_t$ đọc state **đã gộp**, không chấm từng token slot.[^kimi-k3-2026]

### 3.2 Đọc recurrence theo ba thao tác

Viết lại theo thứ tự trực giác:

```text
old state
  │
  ├─ channel-wise decay: quên khác nhau trên từng key channel
  ├─ delta correction: giảm association hiện được key k_t chọn
  └─ write: thêm association k_t → v_t
```

Ba thao tác có vai trò khác nhau:

1. `Decay` giải phóng capacity trên phạm vi rộng.
2. `Delta correction` sửa association được current key address.
3. `Write` đưa value mới vào memory.

KDA vì thế mạnh hơn additive linear memory đơn giản, nhưng vẫn là finite-dimensional superposition. Fixed shape không đồng nghĩa lossless memory hay infinite exact recall.

### 3.3 State có thực sự fixed không?

Nếu head dimensions cố định, recurrent state mỗi KDA layer có $d_kd_v$ elements, không chứa sequence length $T$:

$$
M_{KDA}=O(d_kd_v).
$$

Reference cache còn giữ ba short-convolution states cho Q/K/V. Chúng cũng có fixed length theo convolution kernel, không append toàn bộ history.[^kimi-linear-modeling-2026]

```text
KDA cache after T tokens
├─ recurrent matrix S_T      fixed shape
├─ q short-conv state        fixed shape
├─ k short-conv state        fixed shape
└─ v short-conv state        fixed shape
```

Nhưng đây chỉ là **KDA-layer state**. Periodic MLA và per-token AttnRes representations vẫn khiến full model có sequence-growing state.

### 3.4 Training/prefill khác decode

Direct recurrence thuận tiện cho one-token decode nhưng tuần tự theo $t$. K3 dùng chunkwise form: parallel bên trong chunk, recurrent giữa chunks. Reference code chọn:

- `chunk_kda` khi xử lý nhiều tokens;
- `fused_recurrent_kda` khi cached decode có đúng một token mới;
- training chỉ hỗ trợ chunk mode trong public reference path.[^kimi-linear-modeling-2026]

Đây là ví dụ quan trọng của `same semantics, different execution regime`.

### 3.5 K3 thay đổi KDA ở đâu?

K3 lower-bound log-decay bằng $g_{min}=-5$:

$$
g_t=g_{min}\operatorname{Sigmoid}(e^Az_t),
\qquad
\alpha_t=e^{g_t}.
$$

Trên tile 16 tokens, reciprocal cumulative decay được bounded dưới BF16 dynamic range theo derivation của report, cho phép diagonal và off-diagonal causal tiles dùng dense Tensor Core matrix multiplication. K3 cũng dùng input-dependent full-rank output gate thay cho low-rank gate của Kimi Linear.[^kimi-k3-2026]

> [!warning] Mechanism và result
> Lower-bounded decay giải thích numerical range và kernel path. Nó không tự chứng minh KDA giữ long-range facts tốt hơn ở mọi workload.

## 4. Path 2 — Gated MLA: global token retrieval

### 4.1 Vì sao vẫn cần MLA?

KDA đã nén many token writes vào shared state. Sau khi nén, query không còn một explicit slot cho từng token. Periodic MLA giữ một compressed latent cho mỗi token và chạy global softmax attention, nên structural ability để chọn token riêng lẻ vẫn còn.

```text
KDA
history ──compress──> shared recurrent state ──read──> output

MLA
history ──cache──> c_1, c_2, ..., c_T ──score each token──> output
```

Đây là division of labor:

- KDA ưu tiên bounded recurrent state và recency-sensitive sequence mixing;
- MLA ưu tiên global token-addressable retrieval;
- hybrid pattern trả MLA cost định kỳ thay vì ở mọi layer.[^kimi-k3-2026]

### 4.2 MLA nén gì, không nén gì?

Với hidden state $x_t$:

$$
c_t=W_cx_t.
$$

MLA cache giữ low-dimensional latent $c_t$ thay vì full per-head content K/V. Up-projections tạo content keys/values về mặt toán học; implementation có thể absorb các projections để không materialize mọi tensor. Tuy nhiên vẫn có một latent riêng cho từng token:

$$
M_{MLA}(T)=O(Td_c).
$$

Vì thế MLA là **compressed token-addressable memory**, không phải fixed-state memory.

### 4.3 NoPE và output gate trong K3

K3 áp dụng NoPE cho MLA: query/key của MLA không nhận explicit positional encoding. Primary report diễn giải rằng intervening KDA layers cung cấp position-sensitive và recency-aware mixing, còn MLA cung cấp global content interaction. Thiết kế này tránh retune RoPE khi context extension, nhưng không có nghĩa MLA tự biết position nếu tách khỏi surrounding KDA stack.[^kimi-k3-2026]

Gated MLA còn có channel-wise full-rank output gate:

$$
y_t=W_o\left[\operatorname{Sigmoid}(W_gx_t)\odot\tilde o_t\right].
$$

Gate điều chỉnh channel nào từ global-attention output được truyền tiếp; nó không thay topological fact rằng MLA vẫn đọc token cache tăng theo $T$.

## 5. Path 3 — Block AttnRes: depth retrieval

### 5.1 Standard residual có bottleneck gì?

Standard residual update:

$$
h_{l+1}=h_l+f_l(h_l)
$$

trộn mọi transformation trước đó vào một running state. Information từ layer sớm vẫn có thể tồn tại, nhưng layer sau không có explicit addressable set để chọn “embedding” hay “block 3 output” riêng.

AttnRes áp dụng attention idea lên depth axis. Full form dùng learned pseudo-query $w_l$ để score RMS-normalized earlier representations:

$$
\alpha_{i\to l}
=\operatorname{softmax}_i\left(w_l^T\operatorname{RMSNorm}(v_i)\right),
\qquad
h_l=\sum_{i<l}\alpha_{i\to l}v_i.
$$

Khác biệt axis rất quan trọng:

- MLA attention weights chạy qua **token positions**;
- AttnRes weights chạy qua **depth sources** cho từng token representation.[^kimi-k3-2026]

### 5.2 Vì sao dùng Block AttnRes?

Full AttnRes giữ every layer output, có memory $O(Ld)$ theo depth $L$. Block form cộng outputs trong block rồi chỉ expose:

- token embedding;
- completed block summaries;
- partial sum của current block.

K3 dùng block size 12: tám full blocks cộng một partial final block; nếu tính embedding source thì có chín retrievable block-level sources.[^kimi-k3-2026]

```text
Depth sources visible near the end

embedding ─┐
block 1  ──┤
block 2  ──┤
...        ├─ softmax over depth ─> selected representation
block 8  ──┤
partial 9 ─┘
```

### 5.3 State tăng theo depth hay sequence?

Cần phân biệt hai axes:

- số source slots tăng theo số blocks $N$, không phải mọi layer;
- mỗi source là representation cho từng token, nên long-context prefill storage vẫn tăng theo $T$.

Bỏ qua batch:

$$
M_{AttnRes}=O(TNd).
$$

Vì $N$ bounded bởi architecture, inference depth-state không tăng khi tiếp tục decode thêm layers—depth cố định. Nhưng khi context có thêm tokens, representation storage/cache liên quan vẫn tăng theo sequence. Primary AttnRes report mô tả sequence sharding và chunked prefill để quản lý overhead này; “block-bounded depth state” không đồng nghĩa constant-size sequence state.[^kimi-k3-2026]

### 5.4 Hai retrieval systems không thay nhau

| Retrieval | Candidate axis | Candidate còn riêng lẻ? | Câu hỏi model trả lời |
|---|---|---|---|
| MLA | token positions | Có, dưới dạng compressed per-token entries | “Token nào trong history liên quan?” |
| Block AttnRes | embedding/block representations | Có, theo block source | “Mức abstraction nào trong depth liên quan?” |

Một token có thể dùng AttnRes để lấy representation từ block sớm, rồi dùng MLA để retrieve token position khác. Đây là composition, không phải duplication.

## 6. Path 4 — Stable LatentMoE: sparse channel mixing

### 6.1 Attention và FFN giải quyết hai việc khác nhau

Attention/sequence mixer quyết định information đến từ đâu. FFN/MoE biến đổi channel của từng token. K3 đặt Stable LatentMoE sau mỗi attention layer, trừ first dense layer trong reported configuration.[^kimi-k3-2026]

Routed path:

$$
z=W^{down}x\in\mathbb{R}^{\ell},
$$

$$
u=\sum_{i\in\mathcal{T}_k(x)}p_iE_i^{routed}(z),
$$

$$
y=\sum_{j=1}^{2}E_j^{shared}(x)
+W^{up}\operatorname{RMSNorm}(u).
$$

K3 dùng $d=7168$, latent width $\ell=3584$, 896 routed experts và top-16. Hai shared experts luôn active trên full-width path.[^kimi-k3-2026]

### 6.2 `Sparse` chính xác là gì?

Mỗi token chỉ chạy 16/896 routed experts, nhưng:

- router vẫn cần chọn từ expert pool;
- deployment vẫn phải place hoặc shard toàn bộ expert weights ở đâu đó;
- shared experts luôn chạy;
- communication dispatch/combine và load balance vẫn có cost.

Do đó `104.2B activated parameters` không có nghĩa server chỉ cần lưu 104.2B parameters. `Sparse compute per token` khác `total weight memory`.

### 6.3 Vì sao có latent width?

Nếu token full width được gửi đến 16 experts, communication và expert traffic tăng theo routing multiplicity. LatentMoE down-project trước routing, cho expert chuyên biệt chạy trong compact space, rồi up-project về model width. Đây là width/channel path chứ không phải sequence compression.

### 6.4 Vì sao thêm stability controls?

Extreme sparse routing tạo ra hai nhóm rủi ro:

1. nhiều chained matrix multiplications trong routed latent path có thể gây activation outlier;
2. gần 1,000 experts khó balance ổn định.

Stable LatentMoE dùng:

- `RMSNorm` trước routed up-projection;
- bounded `SiTU-GLU`, với reported bounds từ $\beta_1=4$, $\beta_2=25$;
- `Quantile Balancing` để cập nhật expert-selection biases theo target-load quantile.[^kimi-k3-2026]

Routing bias chỉ đổi top-k selection; mixture weights lấy từ uncorrected router scores. Reference inference code xác nhận semantics này, nhưng không implement training-time QB updates hay distributed expert dispatch.[^kimi-linear-modeling-2026]

## 7. Path 5 — native vision input

### 7.1 Từ pixels đến shared token stream

Reported path là:

```text
image/video
  → patch embedding
  → MoonViT-V2
  → temporal pooling + 2×2 pixel shuffle
  → lightweight projector to language width
  → replace media placeholder with visual-token sequence
  → shared KDA/MLA + AttnRes + LatentMoE backbone
  → next-token prediction
```

MoonViT-V2 được report là 27-layer vision transformer khoảng 401M parameters, train from scratch cùng next-token objective. Image và video dùng shared parameters; pixel shuffle giảm visual-token count bốn lần trước projector.[^kimi-k3-2026]

### 7.2 `Native multimodal` không có nghĩa pixels đi thẳng vào LLM

Vẫn có specialized vision encoder và projector. `Native` ở đây nói đến joint optimization từ đầu và shared backbone/objective, thay vì gắn pretrained vision encoder vào pretrained language model bằng post-hoc alignment stage.[^kimi-k3-2026]

### 7.3 Visual tokens chịu cùng memory trade-off

Sau projection, visual features trở thành entries trong shared sequence. Vì vậy:

- KDA có thể nén visual/text history vào recurrent state;
- MLA có thể globally retrieve visual-token entries;
- AttnRes có thể retrieve earlier-depth visual/text representations;
- LatentMoE chọn channel transformations cho cả visual và text tokens.

High-resolution inputs vẫn tiêu tốn token budget. Vision encoder và pixel shuffle giảm nhưng không xóa sequence-length cost.

> [!warning] Unresolved implementation contradiction
> Technical report mô tả MoonViT-V2 factorized attention thành intra-frame spatial và inter-frame temporal passes.[^kimi-k3-2026] Public `modeling_kimi_k3.py` lại flatten toàn bộ $t\times h\times w$ grid của mỗi media item và chạy full non-causal self-attention, với time embeddings và repeated 2D RoPE.[^kimi-k3-modeling-2026] Public processor còn chỉ xác nhận image path và reject media type khác.[^kimi-k3-processor-2026]
>
> Repository hiện không đủ evidence để kết luận đây là simplified reference code, production divergence hay documentation mismatch. Vì vậy không nên dùng public code để khẳng định usable video inference path.

## 8. Trace một token qua integrated architecture

Giả sử token $x_t$ đi vào một KDA layer giữa AttnRes block:

1. **Depth read:** AttnRes score embedding, completed blocks và current partial block; tạo $h_t^{attn}$.
2. **Local projection:** KDA tạo Q/K/V qua linear projection, short convolution và activation.
3. **Sequence-memory update:** channel decay, delta correction và write cập nhật $S_t$.
4. **Sequence read:** $q_t$ đọc recurrent state; full-rank gate chọn output channels.
5. **Depth accumulation:** KDA output được cộng vào current block prefix.
6. **Depth read lần hai:** AttnRes tạo input cho FFN/MoE.
7. **Sparse channel path:** router chọn top-16 latent experts; 2 shared experts cũng chạy.
8. **Depth accumulation:** MoE output cập nhật block prefix.
9. **Boundary:** sau mỗi 12 layers, completed block summary được giữ làm depth source.

Nếu layer hiện tại là MLA thay vì KDA, bước 2–4 đổi thành:

1. tạo compressed per-token KV latent;
2. append latent vào MLA cache;
3. global softmax retrieval qua cached token entries;
4. full-rank gate điều chỉnh output channels.

Đó là cách đọc macrocycle bằng **state transition**, thay vì chỉ liệt kê module names.

## 9. State-growth ledger

Ký hiệu:

- $T$: context length;
- $L_K$: số KDA layers;
- $L_M$: số MLA layers;
- $N$: số AttnRes block sources;
- $d$: hidden width;
- $d_k,d_v$: KDA head dimensions;
- $d_c$: cached MLA latent width.

| State/capacity | Scale khái niệm | Tăng theo $T$? | Fixed/sparse ở nghĩa nào? |
|---|---:|---:|---|
| KDA recurrent matrices | $O(L_Kd_kd_v)$ theo head factors | Không | fixed shape per layer/head |
| KDA short-conv states | kernel-size × channels | Không | fixed temporal window |
| MLA cache | $O(L_MT d_c)$ | Có | compressed per token, không fixed-state |
| Block AttnRes representations | $O(TNd)$ trong long-context representation view | Có | bounded number of depth sources |
| Routed expert activation | top-16/896 per token | Theo processed tokens | sparse compute, không sparse total weights |
| Shared experts | 2 full-width paths per MoE layer | Theo processed tokens | always active |
| Visual tokens | phụ thuộc resolution/frame compression | Có | trở thành shared sequence tokens |
| Model weights | 2.78T total reported | Không theo request $T$ | static nhưng phải được placed/sharded |

### 9.1 Kết luận quan trọng nhất

$$
\boxed{\text{KDA fixed-state} \not\Rightarrow \text{Kimi K3 full context state fixed-size}}
$$

Periodic MLA cache và AttnRes per-token block representations vẫn tăng với context. Infrastructure phải quản lý KDA state và MLA pages cùng nhau khi prefix cache được reuse hoặc evict.[^kimi-k3-2026]

### 9.2 Prefill và decode

| Phase | KDA | MLA | AttnRes | MoE |
|---|---|---|---|---|
| `Prefill` | chunkwise parallel trong chunk, recurrence giữa chunks | global attention trên prompt tokens | giữ/aggregate block representations per token | route many prompt tokens, cần dispatch/load balance |
| `Decode` | one-token recurrent update | append latent và query growing cache | update representation cho token mới qua fixed depth | route token mới qua top-16 + shared experts |

Đừng gộp `prefill FLOPs`, `decode state`, `weight memory` và `network communication` thành một từ “efficiency”.

## 10. PyTorch lab: toy integrated information path

> [!important] Phạm vi của code
> Code dưới đây **không reproduce Kimi K3**. Nó là executable shape model để minh họa năm semantics: recurrent KDA-like state, per-token global cache, depth-source selection, top-k latent experts và visual-token insertion. Nó bỏ qua multi-head kernels, exact KDA parameterization, causal chunk algorithm, distributed dispatch, Quantile Balancing và production cache management.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


torch.manual_seed(7)


class ToyKDA(nn.Module):
    """Single-head recurrent delta memory; state shape does not contain T."""
    def __init__(self, d):
        super().__init__()
        self.q = nn.Linear(d, d, bias=False)
        self.k = nn.Linear(d, d, bias=False)
        self.v = nn.Linear(d, d, bias=False)
        self.alpha = nn.Linear(d, d)
        self.beta = nn.Linear(d, 1)
        self.out = nn.Linear(d, d, bias=False)

    def forward(self, x, state=None):
        # x: [B, T, D], state: [B, D, D]
        B, T, D = x.shape
        if state is None:
            state = x.new_zeros(B, D, D)

        outputs = []
        for t in range(T):
            xt = x[:, t]
            q = F.normalize(self.q(xt), dim=-1)
            k = F.normalize(self.k(xt), dim=-1)
            v = self.v(xt)
            alpha = torch.sigmoid(self.alpha(xt))
            beta = torch.sigmoid(self.beta(xt)).unsqueeze(-1)

            # Decay key channels: Diag(alpha) @ S.
            decayed = alpha.unsqueeze(-1) * state

            # Current retrieval and delta correction.
            retrieved = torch.einsum("bd,bde->be", k, decayed)
            error = v - retrieved
            state = decayed + beta * torch.einsum("bd,be->bde", k, error)

            read = torch.einsum("bd,bde->be", q, state)
            outputs.append(self.out(read))

        return torch.stack(outputs, dim=1), state


class ToyGlobalAttention(nn.Module):
    """Per-token K/V cache: cache length grows with T."""
    def __init__(self, d):
        super().__init__()
        self.q = nn.Linear(d, d, bias=False)
        self.k = nn.Linear(d, d, bias=False)
        self.v = nn.Linear(d, d, bias=False)
        self.gate = nn.Linear(d, d)

    def forward(self, x, cache=None):
        q, k_new, v_new = self.q(x), self.k(x), self.v(x)
        if cache is None:
            k_all, v_all = k_new, v_new
            past = 0
        else:
            k_all = torch.cat([cache[0], k_new], dim=1)
            v_all = torch.cat([cache[1], v_new], dim=1)
            past = cache[0].shape[1]

        scores = q @ k_all.transpose(-1, -2) / math.sqrt(x.shape[-1])
        # Query i in this call may see old cache and new positions <= i.
        causal = torch.arange(k_all.shape[1], device=x.device)[None, :] <= (
            past + torch.arange(x.shape[1], device=x.device)[:, None]
        )
        scores = scores.masked_fill(~causal[None], float("-inf"))
        out = scores.softmax(-1) @ v_all
        out = torch.sigmoid(self.gate(x)) * out
        return out, (k_all.detach(), v_all.detach())


class ToyBlockAttnRes(nn.Module):
    """Select over depth sources, not token positions."""
    def __init__(self, d):
        super().__init__()
        self.query = nn.Parameter(torch.randn(d) / math.sqrt(d))

    def forward(self, sources):
        # Each source: [B, T, D]; stack depth axis N.
        values = torch.stack(sources, dim=2)       # [B, T, N, D]
        keys = F.rms_norm(values, (values.shape[-1],))
        scores = torch.einsum("btnd,d->btn", keys, self.query)
        weights = scores.softmax(dim=-1)
        mixed = torch.einsum("btn,btnd->btd", weights, values)
        return mixed, weights


class Expert(nn.Module):
    def __init__(self, d, hidden):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d, hidden), nn.SiLU(), nn.Linear(hidden, d)
        )

    def forward(self, x):
        return self.net(x)


class ToyLatentMoE(nn.Module):
    """Top-k routed latent experts plus one always-on shared expert."""
    def __init__(self, d, latent, num_experts=4, top_k=2):
        super().__init__()
        self.top_k = top_k
        self.down = nn.Linear(d, latent, bias=False)
        self.router = nn.Linear(d, num_experts, bias=False)
        self.experts = nn.ModuleList([Expert(latent, 2 * latent)
                                      for _ in range(num_experts)])
        self.up = nn.Linear(latent, d, bias=False)
        self.shared = Expert(d, 2 * d)

    def forward(self, x):
        B, T, D = x.shape
        flat = x.reshape(B * T, D)
        z = self.down(flat)
        scores = self.router(flat)
        top_val, top_idx = scores.topk(self.top_k, dim=-1)
        weights = top_val.softmax(dim=-1)

        routed = torch.zeros_like(z)
        for expert_id, expert in enumerate(self.experts):
            for slot in range(self.top_k):
                mask = top_idx[:, slot] == expert_id
                if mask.any():
                    routed[mask] += (
                        weights[mask, slot, None] * expert(z[mask])
                    )

        routed = F.rms_norm(routed, (routed.shape[-1],))
        y = self.up(routed) + self.shared(flat)
        loads = torch.bincount(top_idx.flatten(), minlength=len(self.experts))
        return y.view(B, T, D), loads


class ToyMacrocycle(nn.Module):
    def __init__(self, d=16):
        super().__init__()
        self.mixers = nn.ModuleList([
            ToyKDA(d), ToyKDA(d), ToyKDA(d), ToyGlobalAttention(d)
        ])
        self.depth_reads = nn.ModuleList([ToyBlockAttnRes(d) for _ in range(8)])
        self.moes = nn.ModuleList([ToyLatentMoE(d, d // 2) for _ in range(4)])

    def forward(self, x, kda_states=None, mla_cache=None):
        kda_states = [None] * 3 if kda_states is None else kda_states
        embedding = x
        prefix = x
        depth_sources = [embedding]
        new_kda_states, loads = [], []

        for i, mixer in enumerate(self.mixers):
            depth_reader = self.depth_reads[2 * i]
            h, _ = depth_reader(depth_sources + [prefix])
            if i < 3:
                mixed, state = mixer(h, kda_states[i])
                new_kda_states.append(state.detach())
            else:
                mixed, mla_cache = mixer(h, mla_cache)
            prefix = prefix + mixed

            depth_reader = self.depth_reads[2 * i + 1]
            h, _ = depth_reader(depth_sources + [prefix])
            moe = self.moes[i]
            ff, expert_load = moe(h)
            prefix = prefix + ff
            loads.append(expert_load)

        # One macrocycle summary becomes a new depth source.
        depth_sources.append(prefix)
        return prefix, new_kda_states, mla_cache, loads, depth_sources


if __name__ == "__main__":
    model = ToyMacrocycle(d=16).eval()
    prompt = torch.randn(2, 5, 16)

    out, kda_states, mla_cache, loads, depth_sources = model(prompt)
    print("output:", out.shape)
    print("KDA states:", [tuple(s.shape) for s in kda_states])
    print("MLA cache length:", mla_cache[0].shape[1])
    print("depth sources:", len(depth_sources))
    print("expert loads per layer:", [x.tolist() for x in loads])

    # Decode one more token using prior sequence states.
    new_token = torch.randn(2, 1, 16)
    _, kda_states_2, mla_cache_2, _, _ = model(
        new_token, kda_states=kda_states, mla_cache=mla_cache
    )

    # KDA matrix shapes stay fixed; MLA cache appends one token.
    assert all(a.shape == b.shape for a, b in zip(kda_states, kda_states_2))
    assert mla_cache_2[0].shape[1] == mla_cache[0].shape[1] + 1
    print("state-growth assertions passed")
```

### 10.1 Kết quả cần quan sát

Không cần output numerical giống nhau giữa PyTorch versions. Cần kiểm tra invariants:

```text
output: [batch, prompt_length, hidden]
KDA states: mỗi state là [batch, hidden, hidden]
MLA cache length: prompt_length
expert loads: tổng mỗi layer = batch × tokens × top_k
```

Sau one-token decode:

- shape của từng KDA state không đổi;
- MLA cache length tăng đúng 1;
- top-k routing chỉ activate subset experts cho token mới.

### 10.2 Lab này cố ý đơn giản hóa gì?

| Toy code | Kimi K3 thật |
|---|---|
| single-head dense state | multi-head KDA với dedicated kernels |
| direct token loop | chunkwise prefill/training + recurrent decode |
| full K/V toy cache | compressed latent MLA, optimized projections/kernels |
| một macrocycle là một depth block | AttnRes block size 12 layers |
| 4 experts, top-2, 1 shared | 896 experts, top-16, 2 shared |
| Python loops | expert parallel dispatch và grouped GEMM |
| không vision encoder | MoonViT-V2 + projector + placeholder expansion |

Không benchmark toy code để suy ra K3 latency. Python dispatch và explicit recurrence đo interpreter overhead nhiều hơn architecture efficiency.

## 11. Bài tập thực hành

### Bài 1 — Annotate macrocycle

Vẽ bốn layers và ghi tại mỗi boundary:

- input depth sources;
- KDA recurrent state hoặc MLA cache;
- routed/shared expert paths;
- output được cộng vào current AttnRes prefix.

**Đạt** khi bạn không vẽ MLA cache như input của KDA và không vẽ expert routing như token retrieval.

### Bài 2 — State classification

Phân loại từng item thành một hoặc nhiều nhóm: `fixed by T`, `grows with T`, `bounded by depth blocks`, `sparsely activated`, `static weights`.

1. KDA recurrent matrix;
2. MLA latent cache;
3. eight completed AttnRes block summaries cho toàn sequence;
4. top-16 routed expert activations;
5. weights của 896 experts;
6. visual tokens sau projector.

<details>
<summary>Đáp án gợi ý</summary>

1. `fixed by T`;
2. `grows with T`;
3. `bounded by depth blocks` **và** `grows with T` theo token representations;
4. `sparsely activated`;
5. `static weights`, không biến mất vì sparse activation;
6. trở thành sequence entries nên đóng góp vào `grows with T`.

</details>

### Bài 3 — Thay đổi hybrid ratio

Giả sử đổi từ `3 KDA : 1 MLA` sang `7 KDA : 1 MLA`. Không kết luận quality; chỉ dự đoán direction:

- số sequence-growing global caches/layers giảm;
- tần suất direct global token retrieval giảm;
- KDA fixed-state work chiếm tỷ trọng lớn hơn;
- retrieval quality và speed cần experiment để xác nhận.

### Bài 4 — Instrument toy model

Thêm hooks để log:

- norm của từng KDA state sau mỗi token;
- entropy của AttnRes weights;
- expert load histogram;
- MLA cache elements theo decode step.

Test tối thiểu:

```python
assert loads[0].sum().item() == batch * tokens * top_k
assert mla_cache_len_after == mla_cache_len_before + decoded_tokens
assert kda_state.shape == initial_kda_state.shape
```

### Bài 5 — Evidence ledger

Với mỗi statement, gắn label:

- `documented mechanism`;
- `reference-code observation`;
- `author-reported result`;
- `course synthesis`;
- `unsupported causal claim`.

Ví dụ “K3 report dùng 69 KDA + 24 MLA” là documented configuration. “KDA một mình tạo ra toàn bộ 2.5× scaling gain” là unsupported causal claim vì architecture, data và training recipe thay đổi cùng nhau.[^kimi-k3-2026]

## 12. Những nhầm lẫn thường gặp

### 12.1 “K3 là linear-attention model nên cache constant-size”

Sai. Chỉ KDA layers có fixed-size recurrent state theo $T$. MLA cache và AttnRes token representations vẫn tăng theo context.

### 12.2 “MLA là linear attention”

Sai. `Low-rank` trong KV representation không đồng nghĩa linear attention theo sequence. MLA vẫn global softmax attention qua per-token entries.

### 12.3 “AttnRes giúp attention nhìn xa hơn theo token”

Không chính xác. AttnRes retrieve theo depth sources. KDA/MLA mới là sequence mixers.

### 12.4 “Top-16/896 nghĩa là chỉ cần load 16 experts”

Sai ở deployment level. Mỗi token activate subset, nhưng fleet/device mesh vẫn phải place toàn bộ expert pool hoặc có cơ chế phân phối chúng.

### 12.5 “NoPE nghĩa model không có position information”

Không đúng với integrated stack. MLA không dùng explicit PE; primary report quy position-sensitive behavior cho recurrent KDA transitions. Đây là division of labor, không phải absence of all positional signal.[^kimi-k3-2026]

### 12.6 “Native vision nghĩa không có vision encoder”

Sai. Có MoonViT-V2 và projector. `Native` nói về joint training/shared objective và backbone.

### 12.7 “Reported 1M context nghĩa exact recall trên mọi token”

Sai. Context-window support không phải guarantee về effective use, exact retrieval, mọi modality hay mọi task ở full length.

## 13. Cách đọc evidence đúng mức

### 13.1 Điều được document rõ

Primary report và public reference artifacts hỗ trợ các claims sau:

- hybrid `3 KDA : 1 Gated MLA` pattern và final global MLA;
- 69 KDA + 24 MLA trong 93-layer backbone;
- Block AttnRes với block size 12;
- two shared experts + top-16/896 routed latent experts;
- KDA fixed recurrent cache form và MLA append-style cache form trong reference code;
- MoonViT-V2/projector path và joint next-token objective trong report.[^kimi-k3-2026][^kimi-linear-modeling-2026]

### 13.2 Điều là synthesis của bài học

Các phát biểu sau là conceptual organization để học dễ hơn:

- gọi KDA là `sequence memory path` và MLA là `token retrieval path`;
- state-growth ledger hợp nhất KDA, MLA, AttnRes, MoE và vision;
- trace tám bước qua một integrated layer;
- toy implementation và các tests.

Chúng được suy ra từ documented mechanisms, không phải benchmark result của paper.

### 13.3 Điều chưa được chứng minh riêng

Report nêu khoảng $2.5\times$ overall scaling-efficiency improvement so với Kimi K2 từ combined architecture, data và training changes trên fitted held-out OOD validation-loss curves. Evidence đó không isolate causal contribution của KDA, MLA ratio, AttnRes, Stable LatentMoE, optimizer hay curriculum.[^kimi-k3-2026]

Public reference code cũng có boundaries:

- text MoE path không hỗ trợ training mode và không implement distributed QB/MoonEP;
- code được label là reference architecture implementation;
- multimodal path có contradiction với report về vision attention và chỉ xác nhận image processor path.[^kimi-linear-modeling-2026][^kimi-k3-modeling-2026][^kimi-k3-processor-2026]

## 14. Checklist hoàn thành Stage 9.4

Bạn sẵn sàng sang comparative reading khi có thể tự làm các việc sau:

- [ ] Vẽ đúng macrocycle `KDA ×3 → Gated MLA` và final MLA.
- [ ] Đặt Stable LatentMoE sau sequence mixer và AttnRes quanh attention/FFN inputs.
- [ ] Giải thích KDA recurrence bằng decay, correction, write và read.
- [ ] Nói rõ MLA giữ per-token latent nên cache vẫn tăng theo $T$.
- [ ] Phân biệt token-axis retrieval với depth-axis retrieval.
- [ ] Phân biệt active parameters với total expert weights.
- [ ] Trace visual features vào shared token stream.
- [ ] Hoàn thành state-growth ledger mà không gọi toàn model fixed-state.
- [ ] Chạy toy lab và pass assertions.
- [ ] Gắn đúng evidence label cho mechanism, code observation, result và synthesis.

## 15. Tóm tắt

Kimi K3 chia information flow theo nhiều axes:

1. **KDA** nén sequence history vào fixed-size recurrent state, dùng channel-wise decay và delta correction.
2. **Gated MLA** giữ periodic global token-addressable retrieval bằng compressed per-token cache.
3. **Block AttnRes** cho layer chọn embedding và block-level representations dọc depth.
4. **Stable LatentMoE** mở rộng channel capacity bằng top-k latent experts, shared experts và stability/load-balancing controls.
5. **MoonViT-V2** đưa visual features vào cùng shared token stream và next-token objective.

Cách đọc đúng không phải “cơ chế nào thắng”, mà là “mỗi mechanism giữ loại state nào, retrieve theo axis nào, và trade-off nào vẫn còn”. K3 dùng integration để phân công bottlenecks; integration không biến mọi cost thành constant và không cho phép gán whole-model result cho một component riêng.

## Relationships

- **Depends on:** [GPT-2 → Kimi Linear: changing the memory model](gpt2-to-kimi-linear-memory-model-beginners-course.md) để hiểu fixed-state KDA và periodic MLA.
- **Synthesizes:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), [Attention Residuals](attention-residuals.md), [Stable LatentMoE and Quantile Balancing](stable-latentmoe-and-quantile-balancing.md), và [Kimi K3 native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md).
- **Uses:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) để nối architectural state với prefill, decode, prefix caching và distributed execution.
- **Prepares for:** Stage 9.5 comparative reading trong [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), đặc biệt Sections 2–3 và 5.

[^kimi-linear-modeling-2026]: Moonshot AI Team, DeepSeek-AI, và Hugging Face, “Kimi K3 text-backbone reference modeling code,” [source](../raw/kimi-k3-sources/modeling_kimi_linear.py), đặc biệt `KimiDynamicCache`, `KimiDeltaAttention`, `KimiSparseMoeBlock`, `KimiDecoderLayer`, và `_apply_attn_res`.

[^kimi-k3-modeling-2026]: Moonshot AI Team và Hugging Face, “Kimi K3 multimodal reference modeling code,” [source](../raw/kimi-k3-sources/modeling_kimi_k3.py), đặc biệt vision encoder, projector và media-token expansion path.

[^kimi-k3-processor-2026]: Moonshot AI Team và Hugging Face, “Kimi K3 multimodal processor reference code,” [source](../raw/kimi-k3-sources/kimi_k3_processor.py), đặc biệt `preprocess_medias`.
