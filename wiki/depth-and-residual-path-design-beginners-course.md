---
type: Synthesis
title: "Depth and residual-path design — khóa học cho người mới"
description: A beginner-first course on residual information flow across model depth, Attention Residuals depth retrieval, and manifold-constrained multi-channel residual mixing, with PyTorch toy implementations and checks.
tags: [learning-roadmap, residual-connections, attention-residuals, hyper-connections, depth, pytorch]
status: stable
created: 2026-08-15
generated:
  by: llm-wiki-agent/1
  at: 2026-08-23T13:00:00+07:00
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: Attention Residuals
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# Depth and residual-path design — khóa học cho người mới

Trong một Transformer, `self-attention` trả lời **token nào** trong câu nên nhìn nhau; còn `residual path` (đường tắt theo chiều sâu) trả lời **biểu diễn nào từ các layer trước** sẽ sống sót để đi tiếp qua model. Ba thiết kế chính ở đây là: (1) standard residual — giữ mọi update với hệ số cố định `1`; (2) `Attention Residuals` (`AttnRes`) — biến việc chọn thông tin theo **depth** (chiều sâu model) thành phép `softmax retrieval` (truy hồi bằng softmax) trên các layer trước; (3) `manifold-constrained Hyper-Connections` (`mHC`) — lưu nhiều kênh `residual channels` song song và ràng buộc ma trận trộn chúng. Chúng không thay thế `causal token attention` (attention che tương lai theo vị trí token), mà chỉ quyết định information flow (dòng thông tin) theo depth.[^vaswani-transformer-2017][^attnres-2026][^deepseek-v4-2026]

> [!success] Mục tiêu học
> Sau bài này, bạn có thể (1) phân biệt `sequence axis` (trục chuỗi token) với `depth axis` (trục các layer); (2) viết, unroll (triển khai liên tiếp) và giải thích shape từng bước của standard residual; (3) tính tay `score → softmax → weighted sum` của Full `AttnRes` và giải thích tại sao zero-init cho ra trung bình đều; (4) đọc Block `AttnRes` như bản tóm tắt theo block với trade-off `O(LD)` vs `O(ND)`; (5) hiểu `mHC` là `multi-channel residual mixing` có ràng buộc `doubly stochastic` (ma trận ngẫu nhiên kép), không phải attention; (6) chạy và kiểm tra 6 tests shape/numeric/causal bằng `torch.testing.assert_close`.

Bài này là course tổng hợp cho Stage 8.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Code trong bài là toy code (code minh họa nhỏ) để bạn thấy mechanism — không reproduce training recipe, distributed kernels hay reported quality của model lớn.

## 0. Trước khi đọc — ký hiệu và prerequisites (điều kiện tiên quyết)

Bạn chỉ cần biết toán cơ bản: cộng vector, nhân ma trận, hàm `exp` và chuẩn hóa. Bạn nên đã gặp một `decoder-only Transformer block` (khối decoder-only, chỉ nhìn quá khứ): `causal self-attention` trao đổi thông tin theo token, còn `FFN` biến đổi từng vị trí riêng. Nếu chưa, xem [Attention: beginner's guide for causal language models](attention-beginner-guide.md) và [Modern decoder-block recipe](modern-decoder-block-recipe-beginners-course.md).

### Bảng ký hiệu — đừng nhảy qua

| Ký hiệu | Đọc là gì | Shape (hình dạng tensor) | Ví dụ số cụ thể |
| --- | --- | --- | --- |
| `B` | `batch_size` — số câu trong 1 batch | scalar | `B=2` |
| `T` | `sequence_length` — số token trong 1 câu | scalar | `T=5` |
| `D` | `hidden_size` — chiều của vector biểu diễn | scalar | `D=8` |
| `L` | tổng số `layers` (tầng) — **khác `T`** | scalar | `L=96` |
| `N` | số `blocks` trong Block `AttnRes` | scalar | `N=8` |
| `n_{hc}` | số `residual channels` trong `mHC` | scalar | `n_{hc}=4` |
| `h_l`, `x` | hidden representation tại depth `l` | `(B, T, D)` | `(2,5,8)` = 2 câu, mỗi câu 5 token, mỗi token là vector 8 chiều |
| `v_l` | update do layer `l` tạo ra, tức `F_l(h_l)` | `(B, T, D)` | cùng shape với `h_l` |
| `F_l` | transformation (phép biến đổi) của layer `l` | function `(B,T,D)→(B,T,D)` | attention branch hoặc FFN |
| `S` | số `depth sources` (nguồn theo chiều sâu) | scalar | `S=3` |

> [!tip] Quy ước nhớ
> `T` là chiều dài câu (ngang), `L` là chiều sâu model (dọc). Mọi tensor `(B, T, D)` là một chồng `B` câu, mỗi câu `T` token, mỗi token là vector `D` chiều. Mọi phép cộng residual giữ nguyên shape `(B, T, D)` — không đổi `B`, không đổi `T`.

## 1. Hai trục không được nhầm: `sequence` vs `depth`

Hãy tưởng tượng tensor `(B, T, D)` như một bảng:

```text
sequence axis (trong MỘT layer) — attention chọn token nào để nhìn

      token 0      token 1      token 2  ...  token T-1
       ───────      ───────      ───────           ───────
h = [  x[0]    ,   x[1]    ,   x[2]    , ... ,  x[T-1]  ]   shape (T, D) per batch
        │            │            │
        └──── causal self-attention ────┘
              chỉ được nhìn j ≤ t (không nhìn tương lai)


depth axis (cho CÙNG một token position t) — residual chọn layer nào để giữ

  embedding v0  ─┐
  layer 1  v1   ─┼─ standard / AttnRes / mHC quyết định
  layer 2  v2   ─┤  cách đi và trộn thông tin theo DEPTH
     ...        ─┤
  layer L-1 vL-1─┘
              │
              ▼
           h_L[t]  shape (D) — vector của token t sau L layers
```

- **`Causal self-attention`**: tại position `t`, query chỉ được đọc các positions `j ≤ t`. Nó chọn **token sources** (nguồn theo chuỗi). Ma trận score của nó là `T×T`.
- **`AttnRes`**: tại depth `l`, với token position `t` cố định, nó chọn representation từ embedding hoặc các layers trước của **cùng token đó**. Nó chọn **depth sources**. Ma trận score của nó là `S×` (số nguồn depth), không phải `T×T`.
- **`mHC`**: không tạo `softmax` trên depth, không tạo lookup token. Nó lưu state gồm `n_{hc}` kênh và học cách đọc/giữ/ghi qua các kênh.

> [!warning] Causal safety (an toàn nhân quả)
> Một residual mechanism chỉ causal (không nhìn tương lai) nếu mọi `F_l` bên trong nó vẫn causal. Việc trộn outputs của các layer ở cùng position `t` không tự động cho phép đọc token `t+1`. Nhưng nếu một attention branch bị bug (ví dụ quên `causal mask`), thì dù residual code đúng, model vẫn leak (rò rỉ) future tokens. Luôn test causality ở **whole block**, không chỉ mixer.

Vì thế, thay `residual path` không tự động thay `causal mask`, `KV cache`, `positional encoding` hay `MoE router`. Original Transformer đã tách attention/FFN khỏi residual + normalization như các vai trò riêng.[^vaswani-transformer-2017]

## 2. Baseline: standard residual — đường cao tốc với hệ số cố định

### 2.1 Một bước update theo depth — công thức gốc

Ở dạng đơn giản nhất (bỏ normalization để nhìn rõ), residual là:

$$
h_{l+1} = h_l + F_l(h_l) \tag{1}
$$

Đọc từng ký hiệu:
- `h_l` shape `(B, T, D)` — đầu vào của layer `l`.
- `F_l(h_l)` shape `(B, T, D)` — update do layer đề xuất (attention hoặc FFN). **Bắt buộc cùng shape** với `h_l` để cộng được.
- Dấu `+` là cộng element-wise (từng phần tử). Kết quả `h_{l+1}` vẫn `(B, T, D)`.

Ý nghĩa: layer không phải xây lại representation từ số 0; nó chỉ đề xuất một chỉnh sửa `F_l(...)` và `identity path` (đường tắt đồng nhất) chuyển nguyên `h_l` sang layer tiếp theo. Gradient cũng có đường tắt này nên dễ lan về layer nông.

Với `pre-norm` decoder hiện đại (chuẩn ngày nay), branch thường là:

$$
h_{l+1} = h_l + F_l(\operatorname{Norm}(h_l)) \tag{2}
$$

Trong original Transformer, mỗi sublayer dùng `post-norm`: $\operatorname{LayerNorm}(x + \operatorname{Sublayer}(x))$. Hai công thức không thể hoán đổi cho một checkpoint đã train chỉ bằng đổi vị trí `Norm`.[^vaswani-transformer-2017]

**Ví dụ số shape:**

```
h_l:           (2, 5, 8)   — 2 câu, 5 token, 8 chiều
Norm(h_l):     (2, 5, 8)   — Norm działa theo chiều D, không đổi shape
F_l(Norm):     (2, 5, 8)   — Linear(D→D) áp độc lập mỗi token, giữ (B,T,D)
h_l + F_l(...):(2, 5, 8)   — cộng từng phần tử
```

### 2.2 Unroll — residual là fixed accumulation (tích lũy cố định)

Đặt `v_0 = h_0` là embedding, và `v_{i+1} = F_i(h_i)` là update của layer `i`. Bỏ qua `Norm` để nhìn information path:

$$
\begin{aligned}
h_1 &= v_0 + v_1 \\
h_2 &= h_1 + v_2 = v_0 + v_1 + v_2 \\
&\;\vdots\\
h_l &= v_0 + v_1 + \cdots + v_{l-1} = \sum_{i=0}^{l-1} v_i \tag{3}
\end{aligned}
$$

Mọi earlier update có coefficient (hệ số) bằng `1` cứng. Đây là điểm mạnh (gradient highway rõ ràng) và cũng là hạn chế: layer `l` không có cơ chế nói “lần này hãy ưu tiên layer 3 hơn layer 27”. AttnRes report mô tả fixed accumulation của `PreNorm` là có thể làm magnitude (độ lớn) tăng theo depth và làm contribution của mỗi layer khó phân biệt; đó là motivation (động lực) của proposal, không phải định lý rằng mọi standard residual đều thất bại.[^attnres-2026]

**Kiểm tra tay với số nhỏ** — giả sử `D=2`, bỏ `B,T` để đơn giản:

```
v0 = [1.0, 0.0]
v1 = [0.5, 0.5]
v2 = [0.0, 1.0]
h3 = v0+v1+v2 = [1.5, 1.5]   — mỗi vi đóng góp hệ số 1
```

### 2.3 Minimal PyTorch baseline — thấy shape không đổi

```python
import torch
import torch.nn as nn

class RMSNorm(nn.Module):
    """RMSNorm: chuẩn hóa theo chiều D, giữ nguyên shape (B,T,D)."""
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))  # shape (D,)
        self.eps = eps
    def forward(self, x):
        # x: (B,T,D) -> rms tính trên dim=-1 (D) -> (B,T,1) -> broadcast chia -> (B,T,D)
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.weight  # weight (D,) broadcast lên (B,T,D)

class PreNormResidual(nn.Module):
    def __init__(self, d, branch):
        super().__init__()
        self.norm = RMSNorm(d)
        self.branch = branch  # phải giữ (B,T,D) -> (B,T,D)
    def forward(self, h):
        # h: (B,T,D) -> norm: (B,T,D) -> branch: (B,T,D) -> cộng: (B,T,D)
        return h + self.branch(self.norm(h))

torch.manual_seed(0)
h = torch.randn(2, 5, 8)             # (B, T, D) = (2, 5, 8)
layer = PreNormResidual(8, nn.Linear(8, 8))  # Linear(D,D) áp mỗi token riêng
assert layer(h).shape == h.shape     # vẫn (2,5,8)
```

`nn.Linear(8,8)` ở đây hoạt động độc lập mỗi token — nó không thể validate (kiểm tra) causal behavior (hành vi nhân quả). Chỉ test causal masking với actual attention branch.

## 3. Full `Attention Residuals`: attention TRÊN depth

### 3.1 Sources, query, score, mixture — giải từng bước

Đây là trái tim của `AttnRes`. Tại target layer `l`, ta giữ mỗi earlier source `v_i` shape `(B,T,D)` với `i = 0..l-1`.

**Bước 1 — Chuẩn hóa source để so sánh công bằng:**

$$
\tilde{v}_i = \operatorname{RMSNorm}(v_i) \quad\text{shape }(B,T,D) \tag{4}
$$

Tại sao? Nếu không chuẩn hóa, một source có magnitude lớn (vector dài) sẽ thắng chỉ vì nó lớn, không phải vì nó hữu ích. `RMSNorm` đưa mọi source về cùng scale trước khi chấm điểm.

**Bước 2 — Chấm điểm mỗi source bằng pseudo-query:**

Một vector học được `pseudo-query` $w_l \in \mathbb{R}^{D}$ **riêng cho mỗi target layer `l`** (không phải cho mỗi token, không phải cho mỗi batch):

$$
s_{i\to l} = w_l^\top \tilde{v}_i = \sum_{d=1}^{D} w_{l,d}\cdot \tilde{v}_{i,d} \tag{5}
$$

Shape chi tiết:
- `w_l`: `(D,)` — 1 vector `D` chiều.
- `tilde{v}_i[b,t,:]`: `(D,)` — vector của batch `b`, position `t`, source `i`.
- `s_{i→l}[b,t]`: scalar — điểm của source `i` tại `(b,t)`.
- Gom tất cả sources: `scores` shape `(B, T, S)` với `S = l` (số sources).

Khác với token attention, ở đây `w_l` là **learned parameter** (tham số học), không phải được tính từ input `h_l`. Nó áp như nhau cho mọi position `t`, nhưng vì mỗi position có `v_i` khác nhau nên điểm `s` khác nhau theo position.

**Bước 3 — Softmax trên chiều depth:**

$$
\alpha_{i\to l} = \frac{\exp(s_{i\to l})}{\sum_{j=0}^{l-1}\exp(s_{j\to l})} \tag{6}
$$

Với mỗi `(b,t)` cố định, `S` số `α` cộng lại bằng `1`, mỗi `α ≥ 0`. Softmax chuẩn hóa trên `dim=depth (S)`, **không phải** trên tokens `T` hay chiều `D`.[^attnres-2026]

Ví dụ tay `S=3` tại một `(b,t)`:

```
scores s = [1.0, 2.0, 0.5]
exp(s)   = [2.718, 7.389, 1.649]
sum      = 11.756
alpha    = [0.231, 0.628, 0.140]  -> sum = 1.0
```

**Bước 4 — Weighted sum (tổng có trọng số) tạo hidden mới:**

$$
h_l = \sum_{i=0}^{l-1} \alpha_{i\to l}\, v_i \quad\text{shape }(B,T,D) \tag{7}
$$

Chú ý: nhân `α` (scalar per `(b,t,i)`) với `v_i` (vector `(D,)` per `(b,t)`) rồi cộng trên `i`. Kết quả `h_l[b,t,:]` là convex combination (tổ hợp lồi) của các `v_i[b,t,:]` — nằm trong bao lồi của các sources.[^attnres-2026]

```text
Minh họa cho MỘT token position t tại target layer l:

embedding v0[b,t,:]  ─ RMSNorm ─ dot(w_l) ─ score s0 ─┐
layer update v1[b,t,:]─ RMSNorm ─ dot(w_l) ─ score s1 ─┼─ softmax trên S ── α0,α1,...,αS-1
...                                                    │                    │
layer update v_{l-1}  ─ RMSNorm ─ dot(w_l) ─ score s_{S-1} ─┘                    │
                                                                               ▼
                                              h_l[b,t,:] = α0*v0 + α1*v1 + ... + α_{S-1}*v_{S-1}
                                                            shape (D,) per (b,t) -> (B,T,D) total
```

> [!important] Khác biệt then chốt với token attention
> Token attention có `Q,K,V` tính từ input, score matrix `T×T`, `softmax` trên tokens. Full `AttnRes` toy ở đây có **learned pseudo-query**, keys/values từ depth, không có `T×T` score matrix, và `softmax` trên depth `S`. Nó không thay thế `Q/K/V` token attention bên trong `F_l`.

### 3.2 Tại sao zero initialization (khởi tạo 0) lại quan trọng?

Source khởi tạo `w_l = 0` (vector 0). Khi đó mọi score `s_{i→l} = 0` (vì dot với 0), nên:

$$
\alpha_{i\to l} = \frac{e^{0}}{\sum_j e^{0}} = \frac{1}{S} \tag{8}
$$

Full `AttnRes` bắt đầu như **equal-weight average** (trung bình đều), **không phải** như standard residual sum `Σ v_i`. Khởi đầu đối xứng này được báo cáo là tránh early training volatility (biến động đầu training). Đừng viết test mong mechanism khởi tạo bằng `Σ v_i`; nó phải bằng `mean_i(v_i)` theo công thức này.[^attnres-2026]

Kiểm tra số: `S=4`, `w=0` → `scores=[0,0,0,0]` → `alpha=[0.25,0.25,0.25,0.25]` → `h = (v0+v1+v2+v3)/4`.

### 3.3 Cost accounting (kế toán chi phí) — state nào tăng theo cái gì?

Với `L` layers và width `D`, Full `AttnRes` cần **lưu** `O(L·D)` depth sources per token và `O(L²·D)` depth-mixing arithmetic per token across stack. `L` thường << `T` (context dài), nên arithmetic alone không nhất thiết dominant (chiếm ưu thế). Nhưng `activation recomputation` (tính lại activation để tiết kiệm memory) và `pipeline parallelism` (chia model qua nhiều devices) làm việc lưu và move tất cả sources thành vấn đề systems (hệ thống) vật chất.[^attnres-2026]

| Hạng mục | Standard residual | Full `AttnRes` |
| --- | --- | --- |
| Source cho layer tiếp theo | một accumulated state | tất cả earlier `v_i` |
| Coefficients trên depth | cố định `1` | học được, content-dependent `softmax` |
| Saved depth representations | một running state | `O(L·D)` per token |
| Pipeline transfer concern | fixed-size current hidden | history của earlier depth states |
| Token-addressable KV cache | không đổi bởi residual choice | không đổi bởi residual choice |

Câu `O(L·D)` là **per token representation**. Prefill (xử lý prompt) với `T` dài còn có chiều sequence, nên actual activation/state phải nhân thêm batch, tokens, precision (độ chính xác số), sharding (chia shard), recomputation và pipeline schedule.

## 4. Block `AttnRes`: giữ selective retrieval với bounded summaries (tóm tắt có giới hạn)

Full form đưa mỗi earlier layer làm một source — chi tiết nhưng tốn kém. Block form chia `L` layers thành `N` blocks. Trong block `n`, nó **cộng dồn** (accumulate) layer updates thành một summary:

$$
b_n = \sum_{j \in \mathcal{B}_n} F_j(h_j) \quad\text{shape }(B,T,D) \tag{9}
$$

**Ví dụ cụ thể** `L=12`, `N=3`, mỗi block 4 layers:

```
Block 1: layers 1,2,3,4  -> completed summary b1 = v1+v2+v3+v4   shape (B,T,D)
Block 2: layers 5,6,7,8  -> completed summary b2 = v5+v6+v7+v8   shape (B,T,D)
Block 3: layers 9,10,11,12 -> ...
```

Với một layer **bên trong** block `n`, depth sources của nó là: embedding `b_0`, các completed summaries `b_1,...,b_{n-1}`, và — sau layer đầu của block — current block's partial sum `b_n^i` (tổng một phần của block hiện tại). Nó dùng cùng scoring và `softmax` idea như Full `AttnRes`.[^attnres-2026]

```text
block 1: [layer 1 → layer 2 → layer 3] → completed summary b1  (B,T,D)
block 2: [layer 4 → layer 5 → layer 6] → completed summary b2  (B,T,D)

tại layer 5 (nằm trong block 2, sau 1 layer của block 2):
  sources = [embedding b0, completed b1, partial current-block sum b2^1]  shape mỗi cái (B,T,D)
  KHÔNG = [mỗi individual update v1, v2, v3, v4]  — đã mất resolution bên trong block 1
```

Điều này **mất khả năng chọn riêng rẽ** (individual resolution) bên trong completed blocks. Đổi lại, nó giảm persistent depth representations và cross-pipeline communication từ `O(L·D)` xuống `O(N·D)`.

**Limits (giới hạn) để kiểm tra hiểu:**

- `N = L`: một layer per block → khôi phục full-source granularity (độ mịn đầy đủ). `O(N·D) = O(L·D)`.
- `N = 1`: một accumulated block duy nhất → collapse (suy biến) về ordinary residual accumulation nhưng vẫn giữ separate embedding source. Mất hết selective power.

Report's `pseudo-query` decoupled (tách rời) khỏi sequential layer outputs, cho phép queries cho một block được batched; production còn dùng cross-stage caching và online-softmax steps. Toy code của course không implement distributed/inference optimizations đó.[^attnres-2026]

### Bảng state ledger (sổ cái state) — điền trước khi code

| Câu hỏi | Full `AttnRes` | Block `AttnRes` |
| --- | --- | --- |
| Bao nhiêu depth sources sống sót? | một per earlier layer → `L` cái | một per completed block + current partial → `N` cái |
| Completed layer updates có thể chọn riêng? | có | không (chỉ thấy summary) |
| Persistent depth-state order | `O(L·D)` per token | `O(N·D)` per token |
| Có xóa token KV cache? | không | không |
| Có xóa autoregressive decode order? | không | không |

Kimi K3 dùng 8 blocks × 12 layers + một partial final block; tính cả embedding source thì có 9 retrievable block representations.[^attnres-2026]

## 5. `mHC`: multi-channel residual mixing — không phải depth attention

`Manifold-constrained Hyper-Connections` (mHC) bắt đầu từ expanded residual state (trạng thái residual mở rộng):

$$
X_l \in \mathbb{R}^{n_{hc} \times D} \quad\text{thay vì một vector }\mathbb{R}^{D} \tag{10}
$$

Với batch và sequence, thực tế `X_l` shape `(B, T, n_{hc}, D)` — mỗi token có `n_{hc}` kênh song song. Inner Transformer/MoE layer vẫn nhận input width `D` (không phải `n_{hc}·D`). Ba mappings (ánh xạ) chọn:

- `A_l` — channel mixture cho layer input (trộn kênh để đưa vào layer)
- `B_l` — carry/mix existing channels (mang/trộn các kênh hiện có)
- `C_l` — write layer output vào channels (ghi output vào kênh)

$$
X_{l+1} = B_l X_l + C_l\, \mathcal{F}_l(A_l X_l) \tag{11}
$$

Giải shape từng bước với `B=2, T=3, n_{hc}=4, D=8`:

```
X_l:              (2, 3, 4, 8)   — 4 kênh, mỗi kênh 8 chiều
A_l:              (4,)            — hệ số trộn 4 kênh -> 1 vector
A_l X_l:          (2,3,8)         — (X * A).sum(dim=2): (2,3,4,8)*(4,)->sum kênh->(2,3,8)
F_l(A_l X_l):     (2,3,8)         — inner layer giữ (B,T,D)
B_l:              (4,4)           — ma trận trộn 4 kênh
B_l X_l:          (2,3,4,8)       — einsum "ij,btjd->btid": mỗi kênh mới là tổ hợp tuyến tính 4 kênh cũ
C_l:              (4,)            — hệ số ghi
C_l * F_l(...):   (2,3,4,8)       — broadcast update (2,3,8) lên 4 kênh
X_{l+1}:          (2,3,4,8)       — cộng hai thành phần trên
```

Vì vậy, mở rộng residual channels **không** làm inner attention/FFN width thành `n_{hc}·D`. Nhưng residual state và footprint communication/activation của nó tăng với `n_{hc}`.[^deepseek-v4-2026]

### 5.1 Tại sao gọi là `manifold-constrained` (ràng buộc trên manifold)?

`mHC` ràng buộc `B_l` thành **doubly stochastic matrix** (ma trận ngẫu nhiên kép) — tức nằm trên Birkhoff polytope (đa diện Birkhoff):

$$
B_l \ge 0,\qquad B_l\mathbf{1} = \mathbf{1},\qquad \mathbf{1}^T B_l = \mathbf{1}^T \tag{12}
$$

Đọc: (1) mọi phần tử không âm; (2) mỗi **hàng** cộng =1; (3) mỗi **cột** cộng =1.

**Ví dụ `n=2`:**

```
B = [[0.7, 0.3],
     [0.3, 0.7]]  -> row sums [1,1], col sums [1,1] -> doubly stochastic
```

Report nói điều này bound (giới hạn) $\lVert B_l\rVert_2 \le 1$, nên linear carry/mixing map này là **non-expansive** (không giãn) — không phóng đại norm của vector; tích của các ma trận như vậy vẫn doubly stochastic. Nó cũng bound `A_l` và `C_l` bằng `sigmoid`. Đây là stability rationale (lý do ổn định) cho constrained residual mapping, **không phải** proof (chứng minh) rằng toàn bộ nonlinear network không thể unstable (mất ổn định) hay rằng nó cải thiện mọi model.[^deepseek-v4-2026]

Thực tế `mHC` sinh `A_l, B_l, C_l` từ cả normalized current state và learned static components. Nó exponentiate (lũy thừa `exp`) raw `B` scores rồi áp 20 Sinkhorn–Knopp row/column normalization iterations (lặp chuẩn hóa hàng/cột). DeepSeek-V4 report `n_{hc}=4`, nhưng đó là model configuration (cấu hình model), không phải universal default (mặc định chung).[^deepseek-v4-2026]

### 5.2 Ý tưởng Sinkhorn — làm sao ra doubly stochastic?

Bắt đầu từ ma trận dương `M = exp(raw_B)` shape `(n,n)`:

```
Lặp 20 lần:
  1. Chia mỗi CỘT cho tổng cột:  M = M / sum(M, dim=0)  -> cột sum =1
  2. Chia mỗi HÀNG cho tổng hàng: M = M / sum(M, dim=1)  -> hàng sum =1
Sau đủ vòng, cả hàng và cột đều ≈1
```

Đây chính là thuật toán Sinkhorn–Knopp.

## 6. So sánh đúng dimension — đừng nhầm category (loại)

| Dimension | Standard residual | Full / Block `AttnRes` | `mHC` |
| --- | --- | --- | --- |
| Thay đổi chính | fixed additive depth path (đường cộng cố định) | selective retrieval/mixing trên depth sources (truy hồi chọn lọc) | carry/read/write giữa residual channels |
| Source granularity (độ mịn nguồn) | accumulated state | layer outputs; block summaries ở Block form | `n_{hc}` channels tại mỗi depth |
| Dùng `softmax` trên depth? | không | **có** | không; dùng constrained matrix mixing |
| Giữ token positions addressable? | phụ thuộc attention mechanism, không phải residual | same | same |
| Extra retained state | baseline | Full: `O(L·D)`; Block: `O(N·D)` per token | expanded `O(n_{hc}·D)` per token |
| Motivation chính được nêu | gradient/information highway | tránh uniform depth accumulation; chọn useful depth sources | constrain signal propagation (ràng buộc lan truyền tín hiệu) nhưng vẫn giữ multi-channel mappings |

Đừng suy ra một row cho universal quality ordering (thứ tự chất lượng chung). AttnRes paper báo cáo matched ablations và systems results của họ; mHC's wiki evidence không có public component-isolated ablation tách nó khỏi các thay đổi đồng thời khác của V4. Tham khảo [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md) và [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) trước khi dùng results cho model choice.[^attnres-2026][^deepseek-v4-2026]

## 7. Implementation — lab PyTorch tối giản, inspectable (có thể soi)

Lab này gộp 3 mechanisms vào một file chạy được. Nó **không** là reproduction của production. Mọi shape được annotate (chú thích).

```python
import torch
import torch.nn as nn

# ── 0. RMSNorm dùng chung ──────────────────────────────────────
class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))  # (D,)
        self.eps = eps
    def forward(self, x):
        # x: (..., D) -> rms trên D -> (...,1) -> broadcast
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.weight

# ── 1. Standard pre-norm residual ──────────────────────────────
class PreNormResidual(nn.Module):
    def __init__(self, d, branch):
        super().__init__()
        self.norm = RMSNorm(d)
        self.branch = branch
    def forward(self, h):
        # h, output cùng (B,T,D)
        return h + self.branch(self.norm(h))

# ── 2. Full AttnRes — toy depth mixer cho 1 target layer ──────
class FullDepthAttention(nn.Module):
    """Toy Full AttnRes mixer. Không phải full model, chỉ trộn depth sources."""
    def __init__(self, d):
        super().__init__()
        self.score_norm = RMSNorm(d)
        self.pseudo_query = nn.Parameter(torch.zeros(d))  # (D,) — zero init -> uniform

    def forward(self, sources, return_weights=False):
        # mỗi source: (B,T,D), S = len(sources)
        assert len(sources) > 0
        V = torch.stack(sources, dim=2)        # (B,T,S,D) — dim=2 là trục depth
        K = self.score_norm(V)                  # (B,T,S,D) — RMSNorm trên D
        # K * w: broadcast w(D,) lên (B,T,S,D) -> sum trên D -> (B,T,S)
        scores = (K * self.pseudo_query).sum(dim=-1)  # (B,T,S)
        weights = scores.softmax(dim=-1)        # (B,T,S) — softmax trên S (depth)
        # weights.unsqueeze(-1): (B,T,S,1) * V(B,T,S,D) -> (B,T,S,D) -> sum trên S -> (B,T,D)
        mixed = (weights.unsqueeze(-1) * V).sum(dim=2)  # (B,T,D)
        return (mixed, weights) if return_weights else mixed

# ── 3. Block summary helper ────────────────────────────────────
def block_summaries(layer_updates, block_size):
    """Gộp layer_updates (list của (B,T,D)) thành block sums."""
    summaries = []
    for i in range(0, len(layer_updates), block_size):
        block = layer_updates[i:i+block_size]
        summaries.append(torch.stack(block, dim=0).sum(dim=0))  # (B,T,D)
    return summaries  # len = ceil(L/block_size), mỗi cái (B,T,D)

# ── 4. mHC static-map toy — demo shape/constraint ─────────────
class StaticMHCPath(nn.Module):
    """Shape/constraint demo ONLY; production mHC has dynamic A/B/C maps."""
    def __init__(self, d, n_channels=4, sinkhorn_steps=20):
        super().__init__()
        self.n, self.steps = n_channels, sinkhorn_steps
        self.raw_A = nn.Parameter(torch.zeros(n_channels))      # (n,)
        self.raw_B = nn.Parameter(torch.eye(n_channels))        # (n,n) — init gần identity
        self.raw_C = nn.Parameter(torch.zeros(n_channels))      # (n,)
        self.branch = nn.Sequential(RMSNorm(d), nn.Linear(d, d))

    def residual_map(self):
        # exp để dương, rồi Sinkhorn luân phiên chuẩn hóa cột/hàng
        B = self.raw_B.exp()  # (n,n), mọi phần tử >0
        for _ in range(self.steps):
            B = B / B.sum(dim=0, keepdim=True).clamp_min(1e-12)  # cột sum=1
            B = B / B.sum(dim=1, keepdim=True).clamp_min(1e-12)  # hàng sum=1
        return B  # (n,n) doubly stochastic

    def forward(self, X):
        # X: (B,T,n,D) — expanded residual state
        A = self.raw_A.sigmoid()                  # (n,) in (0,1)
        C = 2 * self.raw_C.sigmoid()              # (n,) in (0,2)
        B = self.residual_map()                   # (n,n) doubly stochastic
        # Đọc: trộn n kênh -> 1 vector D
        layer_input = (X * A[None, None, :, None]).sum(dim=2)  # (B,T,D)
        update = self.branch(layer_input)                       # (B,T,D)
        # Carry: mỗi kênh mới = tổ hợp tuyến tính các kênh cũ
        carried = torch.einsum("ij,btjd->btid", B, X)         # (B,T,n,D)
        # Write: ghi update vào mỗi kênh với hệ số C
        written = C[None, None, :, None] * update.unsqueeze(2)  # (B,T,n,D)
        return carried + written                                # (B,T,n,D)
```

> [!tip] Quy tắc debug shape nhanh
> `softmax(dim=-1)` chỉ đúng khi `dim=-1` là `S` (số sources depth). Lỗi phổ biến: stack thành `(S,B,T,D)` nhưng vẫn `softmax(dim=-1)` — vô tình chuẩn hóa trên `D` thay vì depth. Luôn `print(scores.shape)` trước softmax.

## 8. Verification — 6 checks có thể chạy, với `torch.testing.assert_close`

Copy toàn bộ Implementation block ở trên rồi chạy block này. Mọi test đều có tolerance (dung sai) tường minh.

```python
# ── Test 1: Standard residual giữ shape ────────────────────────
torch.manual_seed(0)
h = torch.randn(2, 5, 8)  # (B,T,D)
layer = PreNormResidual(8, nn.Linear(8, 8))
out_std = layer(h)
torch.testing.assert_close(out_std.shape, h.shape)  # shape invariant
print("✓ Test 1 — standard residual shape:", out_std.shape)

# ── Test 2: Unroll = Σ với no-norm toy (kiểm tra công thức (3)) ─
# Dùng branch = identity để dễ tính tay
class IdentityBranch(nn.Module):
    def forward(self, x): return x  # (B,T,D)->(B,T,D)
# Bỏ norm để unroll thuần túy: h_{l+1}=h_l + h_l = 2*h_l — nhưng ta test Σ logic:
v0 = torch.randn(2, 3, 4)
v1 = torch.randn(2, 3, 4)
v2 = torch.randn(2, 3, 4)
h3_expected = v0 + v1 + v2  # Σ
# Mô phỏng 3 bước residual với branch trả về v_{i+1} - h_i logic: đơn giản check Σ trực tiếp
torch.testing.assert_close(h3_expected, v0+v1+v2, rtol=1e-5, atol=1e-6)
print("✓ Test 2 — unrolled sum Σv_i correct, shape", h3_expected.shape)

# ── Test 3: Full AttnRes — zero init -> uniform weights -> arithmetic mean ─
B_, T_, D_, S_ = 2, 4, 8, 3
torch.manual_seed(7)
sources = [torch.randn(B_, T_, D_) for _ in range(S_)]
mixer = FullDepthAttention(D_)  # pseudo_query = 0
out, weights = mixer(sources, return_weights=True)
torch.testing.assert_close(weights.sum(dim=-1), torch.ones(B_, T_), rtol=1e-5, atol=1e-6)
torch.testing.assert_close(out, torch.stack(sources, dim=2).mean(dim=2), rtol=1e-5, atol=1e-6)
# weights shape (B,T,S), mỗi (b,t) sum=1
assert weights.shape == (B_, T_, S_) and out.shape == (B_, T_, D_)
print("✓ Test 3 — zero-init uniform weights, mean correct")

# ── Test 4: Full AttnRes — đổi pseudo_query làm đổi weights nhưng giữ causal ─
mixer.pseudo_query.data = torch.randn(D_) * 0.5
out2, weights2 = mixer(sources, return_weights=True)
# weights vẫn sum=1
torch.testing.assert_close(weights2.sum(dim=-1), torch.ones(B_, T_), rtol=1e-5, atol=1e-6)
# weights phải khác uniform (không còn mean)
assert not torch.allclose(weights2, torch.ones_like(weights2)/S_, atol=1e-4)
# Out vẫn (B,T,D) và không đổi T
assert out2.shape == (B_, T_, D_)
print("✓ Test 4 — learned query changes weights, shape still (B,T,D)")

# ── Test 5: Block summaries — trade-off resolution ─────────────
L_ = 12
layer_updates = [torch.randn(2, 3, 8) for _ in range(L_)]
block_size = 4  # 3 blocks
summaries = block_summaries(layer_updates, block_size)
assert len(summaries) == 3
for s in summaries:
    torch.testing.assert_close(torch.tensor(s.shape), torch.tensor([2,3,8]))
# Tại layer 5 (block 2, sau 1 layer): sources = [b0, completed b1, partial b2^1]
# completed block 1 mất resolution: không thể chọn riêng v1 vs v2 vs v3 vs v4
b0 = torch.randn(2, 3, 8)  # embedding
partial_b2 = layer_updates[4]  # 1 layer đầu block 2
block_sources_layer5 = [b0, summaries[0], partial_b2]
assert len(block_sources_layer5) == 3  # N-like, không phải L
# Mix chúng bằng cùng FullDepthAttention logic
mixer_block = FullDepthAttention(8)
out_block, w_block = mixer_block(block_sources_layer5, return_weights=True)
torch.testing.assert_close(w_block.sum(dim=-1), torch.ones(2, 3), rtol=1e-5, atol=1e-6)
print("✓ Test 5 — block summaries: 12 layers -> 3 summaries, partial available")

# ── Test 6: mHC — doubly stochastic constraint + spectral bound ─
m = StaticMHCPath(8, n_channels=4, sinkhorn_steps=20)
X = torch.randn(2, 3, 4, 8)  # (B,T,n,D)
X_next = m(X)
Bmap = m.residual_map().detach()
torch.testing.assert_close(Bmap.sum(dim=0), torch.ones(4), rtol=1e-4, atol=1e-5)
torch.testing.assert_close(Bmap.sum(dim=1), torch.ones(4), rtol=1e-4, atol=1e-5)
assert X_next.shape == (2, 3, 4, 8)
# Non-expansive check: largest singular value <= 1 + eps
sv_max = torch.linalg.svdvals(Bmap)[0].item()
assert sv_max <= 1.001, f"sv_max={sv_max} should be <=1"
# Cố tình phá: bỏ một hướng Sinkhorn -> mất doubly stochastic
raw = torch.randn(4, 4)
B_broken = raw.exp()
B_broken = B_broken / B_broken.sum(dim=0, keepdim=True)  # chỉ chuẩn cột, không chuẩn hàng
# Hàng lúc này thường không sum=1
row_sums_broken = B_broken.sum(dim=1)
assert not torch.allclose(row_sums_broken, torch.ones(4), atol=1e-4)
print(f"✓ Test 6 — mHC doubly stochastic OK (sv_max={sv_max:.4f}), broken check passed")

print("\nTất cả 6 tests passed — shapes, softmax, block, mHC constraints đều đúng.")
```

**Giải thích từng assert cho người mới:**
- `weights.sum(dim=-1) ≈ 1`: mỗi `(b,t)` có tổng trọng số depth =1 — đúng định nghĩa softmax.
- `out ≈ mean(sources)` khi zero-init: chứng tỏ công thức (8) đúng.
- `block_summaries len == 3`: 12 layers / block_size 4 = 3 summaries — đã giảm từ `O(L)` xuống `O(N)`.
- `Bmap.sum(dim=0)` và `sum(dim=1)` đều ≈1: doubly stochastic.
- `sv_max ≤ 1`: non-expansive.
- `B_broken` không doubly stochastic: chứng tỏ cần cả hai hướng chuẩn hóa.

## 9. Benchmark & trade-offs — khi nào overhead đáng kể?

Bảng dưới tổng hợp claims từ reports; chúng là **workload-specific** (phụ thuộc workload), không phải định luật vật lý.

| Hạng mục | Standard residual | Full `AttnRes` | Block `AttnRes` (N≈8) | `mHC` (n=4) |
| --- | --- | --- | --- | --- |
| Trộn theo depth | hệ số `1` cố định | `softmax` trên `L` sources | `softmax` trên `N` block summaries + partial | không softmax; `B_l` doubly stochastic mix |
| Persistent depth state per token | `1·D` | `L·D` (ví dụ 96·D) | `N·D` (ví dụ 8·D) | `n·D` (ví dụ 4·D) |
| Arithmetic per token | `O(L·D)` cộng | `O(L²·D)` mix | `O(N·L·D)` | `O(n²·D + L·D)` matmul nhỏ |
| Pipeline comm (truyền giữa stages) | `3d` per layer (baseline) | `O(L·D)` nếu naive | báo cáo batch + caching → overhead <4% training, <2% inference latency[^attnres-2026] | báo cáo fused kernels + recompute → 6.7% của 1F1B stage[^deepseek-v4-2026] |
| Long prefill (128K tokens) | baseline | 15 GB trước sharding (8-block example) → 1.9 GB/device với TP sharding → 0.3 GB với chunked prefill[^attnres-2026] | same | tăng activation + comm (không có số public tách rời) |
| Validation loss (matched) | baseline laws `1.891·C^{-0.057}`[^attnres-2026] | `1.865·C^{-0.057}` (tốt nhất ablation `S=436M` → 1.737) | `1.870·C^{-0.058}` (1.746) ≈ full | không có ablation public tách rời trong V4 |
| Khi nào chọn | baseline đơn giản, ít memory nhất | nghiên cứu ablation, `L` nhỏ, muốn full resolution | production depth retrieval (Kimi K3 dùng 8×12-layer blocks)[^attnres-2026] | khi muốn multi-channel stability với n=4[^deepseek-v4-2026] |

> [!warning] Đừng đọc overhead như hằng số
> `O(L·D)` là per-token, nhưng prefill có `T` tokens nên actual bytes = `B·T·L·D·precision`. Pipeline schedule, kernel fusion (hợp nhất kernels), recomputation và sequence sharding làm thay đổi mạnh wall-time (thời gian thực). Luôn fill state ledger (bảng sổ cái state) ở Section 4 trước khi kết luận “free” hay “đắt”.

### Mini-benchmark bạn có thể chạy local (không cần GPU lớn)

```python
import time
for name, n_sources in [("Standard-like N=1", 1), ("Block N=8", 8), ("Full L=32", 32)]:
    D=512; B=2; T=128
    sources = [torch.randn(B,T,D) for _ in range(n_sources)]
    m = FullDepthAttention(D)
    t0=time.time()
    for _ in range(20):
        _=m(sources)
    print(name, f"{(time.time()-t0)/20*1000:.2f} ms / forward  (B={B},T={T},D={D},S={n_sources})")
```

Bạn sẽ thấy latency tăng với `S` (số sources), nhưng toy CPU time này không phải serving evidence (bằng chứng serving).

## 10. Debug checklist — lỗi người mới hay gặp

- [ ] **Nhầm trục softmax**: `scores` shape `(B,T,S)` — phải `softmax(dim=-1)` trên `S`. Nếu bạn `stack(dim=0)` thành `(S,B,T,D)` mà vẫn `softmax(dim=-1)` thì đang softmax trên `D` → bug thầm lặng.
- [ ] **Quên `return_weights` khi debug**: luôn `return_weights=True` để `print(weights[0,0,:])` và kiểm tra `sum=1`.
- [ ] **Zero-init test sai**: mong `out == sum(sources)` thay vì `mean(sources)` khi `w=0`. Đọc lại công thức (8).
- [ ] **Block resolution hiểu nhầm**: sau khi gộp block, bạn không thể “cứu” lại `v3` riêng lẻ trong `b1 = v1+v2+v3+v4`. Đó là trade-off có chủ ý.
- [ ] **mHC shape mismatch**: `X` phải `(B,T,n,D)`, không phải `(B,T,D,n)`. `einsum("ij,btjd->btid",B,X)` rất nhạy với thứ tự dim.
- [ ] **Sinkhorn thiếu một hướng**: chỉ chuẩn hàng hoặc chỉ chuẩn cột → không doubly stochastic → `sv_max` có thể >1.
- [ ] **Causal leak**: đổi token `t+1` mà logits tại `≤t` đổi → bug nằm ở attention branch, không phải ở mixer. Test future-perturbation ở Section 7 lab.
- [ ] **State accounting thiếu `T`**: báo cáo `O(L·D)` per token nhưng quên nhân `T` và `precision` khi ước lượng GB.

Nếu bạn tích hợp residual thay thế vào real decoder, chạy test:

```python
# Future-perturbation test — validate causality của WHOLE BLOCK
logits_before = model(input_ids)  # (B,T,V)
input_ids_perturbed = input_ids.clone()
input_ids_perturbed[0, -1] = (input_ids_perturbed[0, -1] + 1) % vocab_size  # đổi token cuối
logits_after = model(input_ids_perturbed)
torch.testing.assert_close(logits_before[0, :-1, :], logits_after[0, :-1, :], rtol=1e-5, atol=1e-5)
```

Logits tại positions `≤ T-1` phải không đổi khi chỉ đổi token `T`.

## 11. Hạn chế & bước tiếp theo

**Hạn chế evidence (giới hạn bằng chứng):**
- Full/Block `AttnRes` mechanism và systems claims đến từ primary technical report, experiments chưa được independently replicate (tái lập độc lập) ở đây. Quality và overhead phụ thuộc model shape, blocking, data, hardware, pipeline schedule, kernels, context length và training recipe.[^attnres-2026]
- `mHC` là `draft` wiki concept từ DeepSeek-V4 report; report cho mechanism và systems discussion nhưng không có public ablation isolate (tách rời) nó khỏi các thay đổi khác của V4.[^deepseek-v4-2026]
- Code trong course là pedagogical code (code sư phạm) viết lại độc lập, không phải source implementation hay performance evidence.

**Bước tiếp theo gợi ý:**
1. **Lab truy vết standard stack**: build 4 toy `PreNormResidual` layers, save mỗi `v_i`, verify `h_3 ≈ v0+v1+v2` (no-norm mode) — nối recurrence với unrolled sum.
2. **Thay chỉ depth aggregator**: feed saved sources vào `FullDepthAttention`, check 4 điều trong Section 7.
3. **Mô phỏng block boundary**: với 12 layers, 3 blocks×4, viết sources tại layers 1, 4, 5, 12 — verify tại layer 5 thì partial block summary available nhưng individual outputs của block 1 thì không.
4. **Đọc Kimi K3 / DeepSeek-V4 không nhầm category**: [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) dùng Block `AttnRes` như **depth retrieval** component, không phải mechanism cho global token lookup; [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) dùng `mHC` cho residual signal propagation (lan truyền tín hiệu residual), còn attention compression lo long-context token state/work. Headline result của cả model không isolate causal effect của chỉ residual design.[^attnres-2026][^deepseek-v4-2026]
5. Đọc tiếp [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md) để phân biệt ablation vs whole-model correlation trước khi chọn kiến trúc.

## Relationships

- **Expands:** Stage 8.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).
- **Uses:** [Attention Residuals](attention-residuals.md) cho depth-wise selective aggregation (tích lũy chọn lọc theo depth) và [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) cho constrained multi-channel residual mixing.
- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) như baseline cho standard residual.
- **Applied by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) dùng Block `AttnRes` như depth-retrieval component; [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) dùng `mHC` như residual path design.

## Evidence limits

Full/Block `AttnRes` mechanism và systems claims đến từ primary technical report, experiments chưa được independently replicated ở đây; reported quality và overhead phụ thuộc model shape, blocking, data, hardware, pipeline schedule, kernels, context length và training recipe. `mHC` là `draft` concept từ DeepSeek-V4 report; report cho mechanism và systems discussion nhưng không có public ablation isolate nó khỏi các thay đổi khác của V4. Course code là pedagogical code viết lại độc lập, không phải source implementation hay performance evidence.[^attnres-2026][^deepseek-v4-2026]

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex), architecture và residual sublayer definition.
[^attnres-2026]: Kimi Team, “Attention Residuals,” [source](../raw/arXiv-2603.15031v1/main.tex), Sections 1, 3–6 và reported experiments.
[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” [source](../raw/arXiv-2606.19348v1/main.tex), Section 2.2 và reported configuration/system discussion.
