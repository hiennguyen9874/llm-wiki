---
type: Synthesis
title: "MLA và token-addressable memory — bài học cho người mới"
description: A beginner-first course on how MLA compresses each token's KV representation while preserving token-addressable softmax retrieval, why its cache still grows with context, and how it contrasts with fixed-state memory.
tags: [mla, attention, kv-cache, token-addressable-memory, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-23T14:00:00Z }
sources:
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
---

# MLA và token-addressable memory — bài học cho người mới

`Multi-head Latent Attention` (MLA) không xóa `KV cache` — nó làm mỗi `cache entry` nhỏ hơn. Với mỗi token, MLA thay cặp `key`/`value` cồng kềnh của nhiều `heads` bằng một `KV latent` nhỏ (`joint latent`) dùng chung + một `rotary key` nhỏ cho vị trí. Vì mỗi token vẫn có một entry riêng và `query` mới vẫn tạo một `attention weight` cho từng token cũ, MLA vẫn là **token-addressable softmax attention**. Kết quả: số `bytes` **trên mỗi token** giảm mạnh, nhưng tổng `cache` và lượng history phải đọc vẫn tăng tuyến tính theo `context length` $S$. Đây là baseline cần nắm trước khi học `fixed-state memory`, nơi nhiều token được gộp vào một `state` có kích thước cố định và không còn slot riêng cho từng token.[^deepseek-v2-2024][^fast-weight-programmers-2021]

> [!success] Sau bài này, bạn có thể
> 1. Phân biệt `compression per token` (làm mỗi entry nhỏ hơn) với `fixed-state` (không còn entry theo token) qua công thức có chứa $S$ hay không.
> 2. Viết và đọc đúng công thức `memory growth` cho `MHA`, `MLA` và `fixed-state`, giải thích từng ký hiệu, từng `shape` và ý nghĩa "giảm 90% cache".
> 3. Giải thích `low-rank KV joint compression` và `decoupled RoPE` bằng một hình dung duy nhất và theo dõi `shape` qua từng phép nhân ma trận.
> 4. Chỉ ra vì sao MLA vẫn `token-addressable` qua `shape` của `attention weights` là `(B, H, 1, S)`.
> 5. Implement một `content path` tối giản dạng MLA và test `cached decode == full forward` bằng `torch.testing.assert_close`.
> 6. Chọn baseline đúng khi đọc một long-context architecture (`MHA` vs `GQA` vs `MLA` vs `hybrid`).

## 1. Trước khi đọc

**Bạn cần biết trước (mức tối thiểu):**
- Đã biết `Q/K/V`, `scaled dot-product attention`, `causal mask` và `KV caching` ở mức trực giác. Nếu chưa, đọc trước [Attention: beginner's guide](attention-beginner-guide.md) và [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md).
- Hiểu `prefill` (xử lý cả prompt một lần) khác `decode` (sinh từng token) ở đâu — xem [LLM inference lifecycle: training, prefill, decode, và latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md).
- Toán cần: nhân ma trận $(a \times b) \times (b \times c) \to (a \times c)$, `softmax` chuẩn hóa một hàng về tổng = 1, và khái niệm `shape` của `tensor`.

**Bạn không cần:** kernel `Triton`, `distributed training`, hay `paged blocks`. Code dưới là **pedagogical** (`torch.cat` cho cache) — dễ đọc, không phải serving kernel production.

**Bài này không cover:** `training loss` của MLA, `MoE routing`, `quantization`, hay `PagedAttention`. Chúng thay đổi trục khác và được link ở mục 7.

> [!tip] Cách đọc bài này nếu bạn chỉ biết toán cơ bản
> Mỗi công thức sẽ được mổ thành 4 dòng: **Ký hiệu là gì → Shape là gì → Phép toán làm gì → Kết quả shape ra sao**. Đừng nhớ công thức thuộc lòng — hãy nhớ shape chảy như thế nào.

## 2. Lý thuyết cốt lõi — giải từng công thức, từng shape

### 2.1 Ôn nhanh: standard attention là gì, shape chảy ra sao?

Với một `head` tại token $t$, ta có:

$$
q_t = x_t W^Q,\qquad k_t = x_t W^K,\qquad v_t = x_t W^V
$$

- $x_t \in \mathbb{R}^{d}$: `hidden state` của token $t$. Shape `(d,)` — một vector hàng.
- $W^Q, W^K, W^V \in \mathbb{R}^{d \times d_h}$: ma trận `projection` đã học. Shape `(d, d_h)`.
- $q_t, k_t, v_t \in \mathbb{R}^{d_h}$: kết quả sau nhân. Shape `(d_h,)`.

Output tại token $t$ (chỉ nhìn quá khứ $j \le t$):

$$
o_t = \sum_{j=1}^{t} \alpha_{t,j}\, v_j,\qquad
\alpha_{t,j}= \operatorname{softmax}_j\!\left(\frac{q_t^{\top} k_j}{\sqrt{d_h}}\right)
$$

Giải từng mảnh:

| Mảnh | Ý nghĩa tiếng Việt | Shape | Ghi chú |
|---|---|---|---|
| $q_t^{\top} k_j$ | `dot product` giữa query hiện tại và key quá khứ $j$ | scalar (1 số) | Đo độ "hợp" giữa $t$ và $j$ |
| $\sqrt{d_h}$ | `scale factor` | scalar | Chia để tránh số quá lớn làm `softmax` bão hòa |
| $\operatorname{softmax}_j(\cdot)$ | chuẩn hóa $t$ số thành $t$ weights tổng = 1 | vector `(t,)` | $j$ chạy từ $1$ tới $t$ |
| $\alpha_{t,j} v_j$ | weight nhân với value vector | `(d_h,)` | Mỗi $v_j$ được cân |
| $\sum_j$ | cộng $t$ vector lại | `(d_h,)` | Ra output $o_t$ |

**Dạng ma trận cho cả sequence dài $S$ (dễ thấy shape hơn):**

$$
Q = X W^Q \in \mathbb{R}^{S \times d_h},\quad
K = X W^K \in \mathbb{R}^{S \times d_h},\quad
V = X W^V \in \mathbb{R}^{S \times d_h}
$$

$$
\text{Scores} = \frac{Q K^{\top}}{\sqrt{d_h}} \in \mathbb{R}^{S \times S},\quad
\text{Weights} = \operatorname{softmax}(\text{Scores} + M) \in \mathbb{R}^{S \times S},\quad
O = \text{Weights}\, V \in \mathbb{R}^{S \times d_h}
$$

- $X \in \mathbb{R}^{S \times d}$: xếp $S$ hidden states chồng lên nhau. Shape `(S, d)`.
- $QK^{\top}$: `(S, d_h) × (d_h, S) → (S, S)` — mỗi hàng là một query so với mọi key.
- $M$: `causal mask` — ma trận `(S, S)` chứa `0` ở vùng cho phép ($j \le i$) và `-inf` ở vùng cấm ($j > i$). Cộng trước `softmax` để `exp(-inf)=0`.
- `softmax` áp theo **hàng** (`dim=-1`): mỗi hàng $i$ tổng = 1.
- **Batched + multi-head:** thêm 2 trục → `Q` shape `(B, H, S, d_h)`, Scores shape `(B, H, S, S)`.

> [!note] Token-addressable nghĩa là gì?
> Index $j$ chính là **địa chỉ của token thứ $j$**. Query $q_t$ chấm điểm riêng với từng $k_j$, rồi lấy $v_j$ với weight riêng $\alpha_{t,j}$. Hệ quả: cache có một `K/V slot` cho mỗi token, và `attention weights` có trục dài $S$.

### 2.2 Hai câu hỏi phải tách rời — nếu không sẽ hiểu sai mọi paper

Mọi tối ưu long-context đều trả lời hai câu hỏi khác nhau. Nhầm lẫn phổ biến là gộp chúng:

| Câu hỏi | Hỏi gì? | Ký hiệu | MLA trả lời | Fixed-state trả lời |
|---|---|---|---|---|
| **Mỗi token tốn bao nhiêu?** (`per-token state`) | `bytes/token/layer` — một ngăn tủ dày bao nhiêu? | $r$ elements | Ít hơn `MHA` nhiều (ngăn mỏng hơn) | Một phần của `state` chung |
| **Tổng state có tăng theo context?** (`sequence scaling`) | Shape có chứa $S$ không? | có/không $S$ | Có — tăng tuyến tính với $S$ | Không — shape cố định |

> [!important] Quy tắc đọc paper
> Thấy "giảm KV cache 90%" → hỏi ngay: **công thức còn thừa số $S$ (sequence length) không?** Nếu còn, đó là **giảm slope (độ dốc)**, không phải xóa slope. Giống như giảm tiền thuê mỗi mét vuông — tổng tiền vẫn tăng khi diện tích tăng.

**Định nghĩa ký hiệu (đọc chậm, mỗi ký hiệu một dòng):**

| Ký hiệu | Tên tiếng Anh | Ý nghĩa | Ví dụ |
|---|---|---|---|
| $B$ | `batch size` | số sequences chạy song song | 1, 4, 32 |
| $L$ | `layers` | số attention layers có cache | 32 |
| $S$ | `sequence length` | số tokens đã cache | 1024, 8192 |
| $H$ | `heads` | số attention heads mỗi layer | 32 |
| $d_h$ | `head dimension` | chiều mỗi head | 128 |
| $d$ | `model dimension` | $= H \times d_h$ | 4096 |
| $p$ | `bytes/element` | số bytes mỗi số | BF16 → 2, FP8 → 1 |

**Công thức 1 — MHA (baseline chưa nén):**

$$
M_{MHA}=B \cdot L \cdot S \cdot (2\,H\,d_h) \cdot p
$$

Đọc từng thừa số:

- $2\,H\,d_h$: mỗi token mỗi layer lưu **cả K và V** (`2 ×`), mỗi cái có $H$ heads, mỗi head $d_h$ số. Shape logic: `(2, H, d_h)` gộp thành $2Hd_h$ số.
- Nhân với $S$: $S$ tokens → $S$ bản copy.
- Nhân với $L$: $L$ layers → $L$ bản copy.
- Nhân với $B$: $B$ sequences song song.
- Nhân với $p$: mỗi số tốn $p$ bytes.

**Công thức 2 — Bất kỳ cách giảm per-token nào (GQA, quantization, MLA đều là trường hợp riêng):**

$$
M = B \cdot L \cdot S \cdot r \cdot p
$$

- $r$: số `elements` còn lại **trên mỗi token mỗi layer** sau khi nén. MHA có $r = 2Hd_h$, MLA có $r = d_c + d_h^R$.
- Tỷ lệ nén so với MHA: $\frac{2Hd_h}{r}$ — chỉ là phép chia hai số.
- **Điểm mấu chốt:** $S$ vẫn ở đó. Cache vẫn là đường thẳng đi lên theo $S$, chỉ là dốc ít hơn.

**Công thức 3 — Fixed-state (bản chất khác):**

$$
M_{fixed}\approx B \cdot L \cdot H \cdot (d_k \cdot d_v) \cdot p
$$

- Không có $S$! Shape là `(H, d_k, d_v)` — do `feature dimensions` quyết định, không phải số tokens.
- Token 10 và token 1,000,000 có cùng shape state.

**Hình dung để nhớ:**

```text
MHA  = tủ hồ sơ: mỗi token = một ngăn riêng, mỗi ngăn DÀY (2·H·d_h số)
MLA  = cùng tủ đó nhưng mỗi ngăn MỎNG hơn (d_c + d_h^R số) — vẫn từng ngăn riêng
Fixed-state = bảng trắng: mọi token ghi đè lên nhau trên MỘT mặt phẳng cố định (H·d_k·d_v)
```

### 2.3 Ý tưởng cốt lõi của MLA: cache latent, không cache K/V đã expand

#### Bước 1 — Tạo joint latent nhỏ (nén)

Với hidden state $h_t \in \mathbb{R}^{d}$ (shape `(d,)`):

$$
c_t^{KV}=W^{DKV}h_t,\qquad c_t^{KV}\in\mathbb{R}^{d_c},\quad d_c \ll H d_h
$$

| Thành phần | Shape | Giải thích |
|---|---|---|
| $h_t$ | `(d,)` | vector ẩn của token $t$ (ví dụ $d=4096$) |
| $W^{DKV}$ | `(d_c, d)` | ma trận **down-projection** — học cách nén |
| $c_t^{KV}$ | `(d_c,)` | **joint latent** — bản tóm tắt nhỏ của token $t$ (ví dụ $d_c=512$) |
| $d_c \ll H d_h$ | — | latent nhỏ hơn nhiều so với K/V gốc ($H d_h = 4096$) |

Phép nhân: `(d_c, d) × (d, 1) → (d_c, 1)` — nén từ chiều rộng $d$ xuống $d_c$.

#### Bước 2 — Sinh lại K/V content từ cùng một latent (khi cần)

$$
k_t^C = W^{UK}c_t^{KV},\qquad v_t^C = W^{UV}c_t^{KV}
$$

| Thành phần | Shape | Giải thích |
|---|---|---|
| $W^{UK}$ | `(H·d_h, d_c)` | **up-projection** cho key — nở lại từ latent |
| $k_t^C$ | `(H·d_h,)` → reshape `(H, d_h)` | content key cho mọi heads |
| $W^{UV}$ | `(H·d_h, d_c)` | **up-projection** cho value |
| $v_t^C$ | `(H·d_h,)` → reshape `(H, d_h)` | content value cho mọi heads |

Điểm mấu chốt: $k_t^C$ và $v_t^C$ **cùng sinh từ một latent $c_t^{KV}$ duy nhất** — đó là "joint" (chung). Không phải mỗi head một latent riêng.

#### Bước 3 — Cái gì được giữ qua các decode steps? (quyết định memory)

```text
MHA cache tại token t — lưu TRỰC TIẾP:
  [K của mọi heads | V của mọi heads]     ≈ 2·H·d_h  số
  Shape logic: (H, d_h) cho K  +  (H, d_h) cho V

MLA cache tại token t — lưu GIÁN TIẾP:
  [joint KV latent c_t  |  rotary key k_t^R]  =  d_c + d_h^R  số
  Shape logic: (d_c,)        +  (d_h^R,)
  (KHÔNG lưu k_t^C, v_t^C đã expand — sẽ tái tạo khi cần)
```

**Tại sao không cần lưu $k_t^C, v_t^C$? Nhờ tính kết hợp của phép nhân ma trận (associativity).**[^deepseek-v2-2024]

Xét phép chấm điểm $q_t^{\top} k_j^C$:

$$
q_t^{\top} k_j^C = q_t^{\top} (W^{UK}c_j^{KV}) = \big((W^{UK})^{\top} q_t\big)^{\top} c_j^{KV}
$$

| Biến đổi | Shape | Ý nghĩa |
|---|---|---|
| $W^{UK}c_j^{KV}$ | `(H·d_h, d_c) × (d_c,) → (H·d_h,)` | Cách thông thường: nở latent thành key rồi chấm với query |
| $(W^{UK})^{\top} q_t$ | `(d_c, H·d_h) × (H·d_h,) → (d_c,)` | Cách MLA: biến đổi query TRƯỚC, rồi chấm trực tiếp với latent đã cache |
| Kết quả | scalar | Bằng nhau! Nhưng cách 2 không cần lưu $k_j^C$ |

Tương tự, $W^{UV}$ được gộp vào `output projection` $W^O$. DeepSeek-V2 gọi đây là **hấp thụ (absorb)** các up-projections vào đường `query`/`output` trong `inference` — một tối ưu đại số, không phải gộp nhiều token.[^deepseek-v2-2024]

> [!tip] Hiểu "hấp thụ" bằng ví dụ số nhỏ
> Giả sử $q_t = [1,2]$, $W^{UK} = \begin{bmatrix}3&4\\5&6\end{bmatrix}$, $c_j = [7,8]$.
> Cách 1: $k_j = W^{UK}c_j = [3·7+4·8, 5·7+6·8] = [53, 83]$, rồi $q_t^{\top}k_j = 1·53+2·83=219$.
> Cách 2: $\tilde{q}_t = (W^{UK})^{\top}q_t = [3·1+5·2, 4·1+6·2]=[13,16]$, rồi $\tilde{q}_t^{\top}c_j =13·7+16·8=219$. Cùng kết quả, nhưng cách 2 chỉ cần $c_j$.

#### `Low-rank` nghĩa là gì? (giải cho người mới)

Ma trận $W^{DKV}$ có shape `(d_c, d)` với $d_c < d$ — nó có `rank` tối đa $d_c$. Đường đi $h_t \to c_t^{KV} \to (k_t^C, v_t^C)$ buộc phải đi qua **cổ chai (bottleneck)** hẹp $d_c$.

- `Low-rank` = ép thông tin qua cổ chai hẹp → mất một ít chi tiết nhưng tiết kiệm memory.
- Khác với **quantization** (giảm bits mỗi số, không giảm số lượng số).
- Khác với **token eviction** (bỏ hẳn entry của một số token).
- Khác với **GQA/MQA** (share nguyên head K/V giữa các query heads — giảm $H$ hiệu dụng).
- Khác với **fixed-state recurrence** (gộp history vào state không có trục $S$).

Các kỹ thuật này có thể kết hợp, nhưng chúng tác động lên trục khác nhau.

### 2.4 Vì sao cần `decoupled RoPE`? — rotation làm hỏng phép hấp thụ

`RoPE` (Rotary Position Embedding) xoay cặp tọa độ của `query`/`key` theo vị trí $t$ để mã hóa thứ tự. Nếu áp `RoPE` trực tiếp lên content key sau up-projection:

$$
k_{t}^{C,R}=R_t\,W^{UK}c_t^{KV}
$$

- $R_t \in \mathbb{R}^{(H d_h)\times(H d_h)}$: ma trận xoay phụ thuộc vị trí $t$. Shape `(H·d_h, H·d_h)` — block-diagonal xoay từng cặp chiều.
- Vấn đề: $R_t$ nằm **giữa** $W^{UK}$ và $c_t^{KV}$. Ta không thể gộp $W^{UK}$ vào query bằng một projection cố định cho mọi $t$, vì $R_t$ thay đổi theo $t$ và phép nhân ma trận **không giao hoán** ($R_t W^{UK} \neq W^{UK} R_t$).[^deepseek-v2-2024]

**Giải pháp MLA — tách hai đường (decoupled):**

$$
q_{t,i}=[q_{t,i}^{C};\,q_{t,i}^{R}],\qquad
k_{t,i}=[k_{t,i}^{C};\,k_t^{R}]
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $q_{t,i}^{C}$ | `(d_h,)` | `content query` cho head $i$ — đi qua latent path |
| $q_{t,i}^{R}$ | `(d_h^R,)` | `rotary query` riêng cho head $i$ — mang thông tin vị trí |
| $k_{t,i}^{C}$ | `(d_h,)` | `content key` — sinh từ $c_t^{KV}$ |
| $k_t^{R}$ | `(d_h^R,)` | `rotary key` — **share giữa mọi heads**, nhỏ ($d_h^R$ thấp, ví dụ 64) |
| $[a; b]$ | `(d_h+d_h^R,)` | `concat` — nối hai vector dọc theo chiều feature |

- Content K/V vẫn đi qua `joint latent` và được hấp thụ như trước.
- Rotary key $k_t^{R}$ được tạo từ một đường riêng (không qua $W^{UK}$) và được cache cùng latent.
- Cache giữ cả $c_t^{KV}$ (shape `(d_c,)`) và $k_t^{R}$ (shape `(d_h^R,)`) → tổng `width` = $d_c + d_h^R$.

Attention vẫn chạy theo từng token (mỗi token một entry):

$$
o_{t,i}=\sum_{j=1}^{t}\operatorname{softmax}_j\!\left(\frac{q_{t,i}^{\top} k_{j,i}}{\sqrt{d_h+d_h^R}}\right)v_{j,i}^{C}
$$

- $q_{t,i} \in \mathbb{R}^{d_h+d_h^R}$ (shape `(d_h+d_h^R,)` — đã concat).
- $k_{j,i} \in \mathbb{R}^{d_h+d_h^R}$ (shape `(d_h+d_h^R,)` — đã concat).
- Mẫu số $\sqrt{d_h+d_h^R}$: scale theo tổng chiều (cả content + rotary).

> [!warning] `Query compression` không làm cache nhỏ hơn
> MLA cũng nén `query` ($h_t \to c_t^Q \to q_t$) để giảm `training activation memory`, nhưng query của token hiện tại **không phải history state** cần giữ qua decode — nên nó **không làm KV cache nhỏ hơn**.[^deepseek-v2-2024] Đừng nhầm hai loại compression này.

```text
        ┌─────────────────────────────────────────────────┐
h_t ──► │ W^{DKV} ──► c_t^{KV} ─┬──► W^{UK} ──► k_t^C ─┐   │
        │                      │                      ├──► concat ──► attention
        │                      └──► W^{UV} ──► v_t^C ─┘         ▲
        │                                                ┌──────┘
        └─► rotary path ──► k_t^R (share, nhỏ) ──────────┘

Cache mỗi token: [ c_t^{KV} (d_c số) | k_t^R (d_h^R số) ]  × S tokens
Shape cache tổng: (B, S, d_c + d_h^R)  — vẫn có trục S!
```

### 2.5 Memory accounting chi tiết — MLA giảm slope, không xóa slope

**Mỗi token mỗi layer, MLA cache bao nhiêu?**

$$
r_{MLA}= d_c + d_h^R\quad\text{(số elements)}
$$

- $d_c$: width của `joint latent` (ví dụ 512).
- $d_h^R$: width của `rotary key` share (ví dụ 64).
- Tổng $r_{MLA}=576$ elements/token/layer.

**Tổng raw cache cả model:**

$$
M_{MLA}=B\cdot L\cdot S\cdot(d_c+d_h^R)\cdot p
$$

Đọc từng thừa số (giống công thức MHA, chỉ thay $r$):

- $B$: batch, $L$: layers, $S$: tokens — ba trục nhân vào.
- $(d_c+d_h^R)$: elements mỗi token mỗi layer.
- $p$: bytes mỗi element.

**So sánh với MHA:**

$$
M_{MHA}=B\cdot L\cdot S\cdot(2Hd_h)\cdot p
$$

**Tỷ lệ nén (compression ratio) — phép chia đơn giản:**

$$
\frac{M_{MHA}}{M_{MLA}}=\frac{2Hd_h}{d_c+d_h^R}
$$

Trong config DeepSeek-V2, $d_c=4d_h$ và $d_h^R=d_h/2$ → mẫu số $=4.5d_h$, tử số $=2Hd_h$ → ratio $=2H/4.5$. Với $H=32$, ratio $\approx 14.2\times$. Được mô tả tương đương `GQA` với 2.25 `KV groups` — nhưng đây là **con số của một config cụ thể**, không phải hằng số chung của mọi MLA variant.[^deepseek-v2-2024]

**Ví dụ số học — tính từng bước (dễ nhẩm theo):**

Giả sử $L=32$, $B=1$, $H=32$, $d_h=128$, BF16 ($p=2$), MLA $d_c=512$, $d_h^R=64$:

*Bước 1 — MHA per-token:*
- $2Hd_h = 2 \times 32 \times 128 = 8192$ elements/token/layer
- $8192 \times p = 8192 \times 2 = 16384$ bytes/token/layer
- $\times L = 16384 \times 32 = 524288$ bytes/token toàn model ≈ **0.50 MiB/token**

*Bước 2 — MLA per-token:*
- $d_c+d_h^R = 512+64 = 576$ elements/token/layer
- $576 \times 2 = 1152$ bytes/token/layer
- $\times 32 = 36864$ bytes/token toàn model ≈ **0.035 MiB/token**

*Bước 3 — Nhân với $S$:*

| Context $S$ | MHA raw cache | MLA raw cache | Cùng tăng? |
|---|---:|---:|---|
| 1,024 | ~512 MiB | ~36 MiB | — |
| 8,192 | ~4 GiB | ~288 MiB | 8× so với 1,024 |
| 32,768 | ~16 GiB | ~1.1 GiB | 32× so với 1,024 |

Cả hai cùng tăng 32× khi $S$ tăng 32× — MLA có **slope thấp hơn ~14×**, nhưng slope vẫn khác 0. Production memory còn phụ thuộc `dtype`, `allocator`, `block layout`, `batching`, `prefix sharing` và `temporary buffers` — công thức trên chỉ accounting các `retained cache tensors`.

> [!important] Đừng suy latency từ bytes
> `Projection absorption`, kernels, `memory bandwidth`, batching và hardware có thể thay đổi throughput. Công thức trên chỉ là `retained tensors`. Hãy benchmark trên target implementation, dtype (BF16/FP8) và hardware nếu cần quyết định deployment.

### 2.6 Tại sao MLA vẫn là `token-addressable memory`? — nhìn vào shape

Sau khi cache $S$ tokens, MLA giữ:

$$
C^{KV}_{1:S}=[c_1^{KV},c_2^{KV},\ldots,c_S^{KV}] \in \mathbb{R}^{B \times S \times d_c}
$$

và rotary keys tương ứng $\in \mathbb{R}^{B \times S \times d_h^R}$. Trục sequence vẫn dài $S$.

Khi decode 1 token mới, query $q_{new} \in \mathbb{R}^{B \times H \times 1 \times (d_h+d_h^R)}$ chấm với mọi cached keys $K_{cache} \in \mathbb{R}^{B \times H \times S \times (d_h+d_h^R)}$:

$$
\text{Scores} = Q_{new} K_{cache}^{\top} \in \mathbb{R}^{B \times H \times 1 \times S}
$$

- Shape `(B, H, 1, S)` — mỗi cột trong chiều cuối **ứng với một token position cụ thể**. Đó chính là token-addressability.
- Sau `softmax` trên chiều $S$: `Weights` shape `(B, H, 1, S)` — mỗi weight là xác suất dành cho token $j$.
- `Output = Weights × V_cache` — `V_cache` shape `(B, H, S, d_h)`, kết quả `(B, H, 1, d_h)`.

| Câu hỏi kiểm tra | MLA | Fixed-state memory |
|---|:---:|:---:|
| Có state entry mới cho mỗi token? | ✅ `(B, S, d_c)` tăng với $S$ | ❌ shape cố định |
| Query tạo score/weight riêng cho từng position? | ✅ `(B,H,1,S)` | ❌ đọc state đã gộp |
| Có thể chỉ vào token thứ `j` qua attention axis? | ✅ cột $j$ | ❌ không còn slot $j$ |
| Decode state tăng theo $S$? | ✅ tuyến tính | ❌ hằng số |
| Nhiều associations bị superpose vào cùng state? | ❌ mỗi token riêng | ✅ cộng dồn vào matrix |

> Đừng hiểu "latent" trong MLA là "một latent tóm tắt cả context". Đúng hơn là **một latent cho mỗi token, tại mỗi MLA layer** — vẫn là tủ hồ sơ, chỉ ngăn mỏng hơn.

### 2.7 Fixed-state đổi memory scaling bằng trade-off khác

Một `linear-attention associative memory` tối giản:

$$
S_t = S_{t-1} + \phi(k_t)^{\top} v_t,\qquad o_t = \phi(q_t)\,S_t
$$

Giải từng mảnh cho người mới:

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $\phi(\cdot)$ | $\mathbb{R}^{d} \to \mathbb{R}^{d_k}$ | `feature map` — biến key/query thành vector dương/hilbert để thay `softmax` |
| $k_t, q_t$ | `(d,)` | key/query gốc |
| $\phi(k_t)$ | `(d_k,)` | key sau feature map |
| $v_t$ | `(d_v,)` | value |
| $\phi(k_t)^{\top} v_t$ | `(d_k, 1) × (1, d_v) → (d_k, d_v)` | `outer product` — một ma trận nhỏ ghi association $k_t \to v_t$ |
| $S_t$ | `(d_k, d_v)` | **state** — cộng dồn mọi outer products. **Cùng shape ở token 10 và token 1,000,000** |
| $\phi(q_t) S_t$ | `(1, d_k) × (d_k, d_v) → (1, d_v)` | đọc: query nhân với state |

Hệ quả:

- **MLA:** `sequence-growing compressed slots`, `direct token-level retrieval`, `softmax over history` — mỗi token một ngăn.
- **Fixed-state:** `bounded state`, `recurrent update/read`, nhưng có **capacity interference** — nhiều associations chồng lên cùng ma trận, có thể nhiễu lẫn nhau.

Phân tích trong `Linear Transformers Are Secretly Fast Weight Programmers` chỉ ra: với additive memory, để retrieval không nhiễu cần mapped keys trực giao — đó là giới hạn biểu diễn, không phải ngưỡng failure cố định cho mọi model. Số associations trực giao tối đa ≤ $d_k$ (chiều của feature space).[^fast-weight-programmers-2021]

**Vì sao có hybrid?** Kimi Linear dùng 3 layers `fixed-state KDA` rồi 1 layer `global MLA`: `KDA` giảm sequence-growing state ở đa số layers, periodic `MLA` giữ khả năng token-level retrieval. Report nêu tối đa 75% `KV-cache` reduction so với full MLA theo `layer ratio` (3/4 layers không còn cache tăng theo $S$), nhưng model tổng vẫn có cache tăng theo context ở các MLA layers.[^kimi-linear-2025]

### 2.8 Cost không chỉ là cache capacity — prefill vs decode

Khi decode một token mới, hai kiến trúc làm việc khác nhau:

**MLA (mỗi step làm gì, shape nào):**
1. `Append` một latent + một rotary key → cache `(B, S+1, d_c+d_h^R)` — shape tăng 1 ở trục $S$
2. Tạo/transform query mới → `(B, H, 1, d_h+d_h^R)`
3. Chấm query với $S$ cached entries → scores `(B, H, 1, S)` → softmax trên $S$ positions → retrieve value `(B, H, S, d_h)` → output `(B, H, 1, d_h)`
4. **Cache reads và attention work tăng với $S$** — mỗi token mới đọc toàn bộ history

**Fixed-state (mỗi step làm gì, shape nào):**
1. Update state: $S_t = S_{t-1} + \phi(k_t)^{\top} v_t$ → `(d_k, d_v)` không đổi shape
2. Read state: $o_t = \phi(q_t) S_t$ → `(d_v,)` — đọc state có shape cố định
3. **Work per-step không tăng theo $S$**, nhưng representation phải nén history và có thể mất exact retrieval

> Prefill có thể dùng `chunkwise/parallel algorithms` thay vì recurrence từng token — nên cần đo riêng **prefill latency** và **one-token decode latency**. Đừng suy latency từ bytes.

## 3. Implementation (PyTorch tối thiểu) — đọc shape từng dòng

Code dưới chỉ implement **content path** $c^{KV}\to K^C,V^C$ để làm rõ cache semantics. Cố ý bỏ `decoupled RoPE`, `query compression`, `projection absorption` và optimized kernels — những thứ này không đổi bản chất `per-token latent`.

- `position_ids` là **absolute** (0,1,2,...) — không dùng relative offset trong toy này.
- `RoPE` convention nếu có sẽ là `interleaved` (xoay cặp `(0,1),(2,3),...`) — toy này bỏ RoPE nên không áp dụng, nhưng ghi chú để bạn không nhầm khi đọc code production.
- Cache shape mỗi layer: `(B, S, d_c)` — có trục $S$ — đây là dấu hiệu token-addressable.
- Toy dùng `torch.cat` để append — dễ đọc nhưng không phải `paged blocks` của serving (serving dùng block table để tránh copy).

```python
import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class ToyLatentAttention(nn.Module):
    """MLA-like content path — học cache semantics, không phải production MLA."""

    def __init__(self, d_model: int, n_heads: int, d_latent: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads  # d_h
        self.d_latent = d_latent            # d_c

        self.q_proj = nn.Linear(d_model, d_model, bias=False)   # (d -> d) = (H*d_h -> H*d_h)
        self.kv_down = nn.Linear(d_model, d_latent, bias=False) # (d -> d_c) down-projection W^{DKV}
        self.k_up = nn.Linear(d_latent, d_model, bias=False)    # (d_c -> H*d_h) up-projection W^{UK}
        self.v_up = nn.Linear(d_latent, d_model, bias=False)    # (d_c -> H*d_h) up-projection W^{UV}
        self.out_proj = nn.Linear(d_model, d_model, bias=False) # (d -> d) output mix

    def _heads(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, d_model) -> (B, H, T, d_h)
        B, T, D = x.shape
        return x.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,                          # (B, T_new, d_model) — input mới
        past_latent: Optional[torch.Tensor] = None,  # (B, S_past, d_c) — cache cũ
        use_cache: bool = False,
    ):
        B, T_new, D = x.shape
        q = self._heads(self.q_proj(x))            # (B, T_new, d) -> (B, H, T_new, d_h)
        c_new = self.kv_down(x)                    # (B, T_new, d) -> (B, T_new, d_c) — one latent per token!

        if past_latent is None:
            c_all = c_new                          # (B, T_new, d_c) — chưa có history
            past_len = 0
        else:
            if past_latent.shape[0] != B:
                raise ValueError("cache batch size does not match")
            c_all = torch.cat((past_latent, c_new), dim=1)  # (B, S_past+T_new, d_c) — append!
            past_len = past_latent.size(1)         # S_past

        # Pedagogical reconstruction — optimized MLA absorbs projections, không reconstruct như này
        k = self._heads(self.k_up(c_all))          # (B, S, d_c) -> (B, S, d) -> (B, H, S, d_h)
        v = self._heads(self.v_up(c_all))          # tương tự cho V
        # q: (B, H, T_new, d_h), k: (B, H, S, d_h) -> scores: (B, H, T_new, S)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        S = c_all.size(1)  # S = S_past + T_new — tổng tokens đã cache
        # absolute position_ids: past tokens 0..past_len-1, new tokens past_len..past_len+T_new-1
        q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]  # (T_new, 1)
        k_pos = torch.arange(S, device=x.device)[None, :]                 # (1, S)
        causal = k_pos <= q_pos  # (T_new, S) — True nếu k_pos <= q_pos (được phép nhìn)
        scores = scores.masked_fill(~causal, float("-inf"))  # cấm future bằng -inf trước softmax

        weights = F.softmax(scores, dim=-1)        # (B, H, T_new, S) — last axis indexes tokens!
        y = weights @ v  # (B, H, T_new, S) @ (B, H, S, d_h) -> (B, H, T_new, d_h)
        y = y.transpose(1, 2).contiguous().view(B, T_new, D)  # (B, T_new, d_model)
        present = c_all if use_cache else None     # (B, S, d_c) — cache cho step sau
        return self.out_proj(y), present, weights
```

**Ba quan sát trực tiếp từ code — nhìn shape là thấy bản chất:**

1. `past_latent.shape == (B, S, d_latent)` — latent nhỏ (`d_latent=8` trong toy) nhưng vẫn có **trục $S$** — mỗi token một hàng.
2. `weights.shape == (B, H, T_new, S)` — query vẫn address từng cached token — chiều cuối dài $S$.
3. Mỗi decode step `torch.cat` thêm một entry — cache **không** fixed-state — shape $S$ tăng dần.

> [!note] Vì sao toy bỏ RoPE?
> Để bạn tập trung vào **cache semantics** (trục $S$). Full MLA thêm `decoupled RoPE` như Section 2.4, nhưng không đổi việc cache có shape `(B, S, d_c+d_h^R)`.

## 4. Xác minh trước khi benchmark — 4 tests phải pass

> [!warning] Lab này chỉ chứng minh semantics của toy content cache
> Full MLA còn `decoupled RoPE`, `query compression` và `projection absorption`. Các test dưới không chứng minh parity với full MLA — chỉ chứng minh **sequence axis và token-addressability** của joint-latent cache.

```python
import torch


@torch.inference_mode()
def test_cached_decode_matches_full():
    """Test 1: cached decode (prefill + 1 step) khớp full causal forward."""
    torch.manual_seed(0)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(2, 7, 32)  # (B=2, S=7, d=32)

    full_y, _, full_w = layer(x, use_cache=False)  # full forward — không cache

    _, cache, _ = layer(x[:, :6], use_cache=True)          # prefill 6 tokens -> cache (2, 6, 8)
    step_y, cache, step_w = layer(x[:, 6:7], past_latent=cache, use_cache=True)  # decode 1 token

    # Logits/output của token cuối phải khớp trong tolerance
    torch.testing.assert_close(step_y, full_y[:, 6:7], rtol=1e-5, atol=1e-6)
    assert cache.shape == (2, 7, 8), f"cache shape {cache.shape} != (2, 7, 8)"
    assert step_w.shape == (2, 4, 1, 7), f"weights {step_w.shape} != (2, 4, 1, 7)"
    # Mỗi query position chỉ attend tới quá khứ (causal) — hàng softmax tổng = 1
    assert torch.allclose(step_w.sum(dim=-1), torch.ones_like(step_w.sum(dim=-1)))
    print("✓ Test 1 passed: cached decode matches full forward, shapes correct")
    print(f"  step_y shape {step_y.shape}, cache shape {cache.shape}, weights shape {step_w.shape}")


@torch.inference_mode()
def test_weights_are_token_addressable():
    """Test 2: attention weights có đúng S cột — mỗi cột là một token."""
    torch.manual_seed(1)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(1, 5, 32)  # (B=1, S=5, d=32)
    _, _, weights = layer(x)  # (1, 4, 5, 5) with causal mask — mỗi hàng là 1 query
    assert weights.shape == (1, 4, 5, 5)
    # Hàng causal: token 0 chỉ thấy 1 token, token 4 thấy 5 tokens
    # weights[0,0,0] should be [1, 0, 0, 0, 0] (masked future = 0 after softmax)
    assert weights[0, 0, 0, 1:].abs().max().item() < 1e-6  # future weights ≈ 0
    assert abs(weights[0, 0, 4].sum().item() - 1.0) < 1e-5  # hàng cuối tổng = 1
    print("✓ Test 2 passed: weights index tokens — causal structure intact")
    print(f"  weights[0,0,4] (query cuối attend 5 tokens): {weights[0,0,4].tolist()}")
    print(f"  weights[0,0,0] (query đầu chỉ thấy token 0): {weights[0,0,0].tolist()}")


@torch.inference_mode()
def test_cache_grows_with_sequence():
    """Test 3: cache tăng tuyến tính với S, không fixed-state."""
    torch.manual_seed(2)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x_short = torch.randn(1, 10, 32)   # 10 tokens
    x_long = torch.randn(1, 100, 32)   # 100 tokens
    _, cache_short, _ = layer(x_short, use_cache=True)  # (1, 10, 8)
    _, cache_long, _ = layer(x_long, use_cache=True)    # (1, 100, 8)
    assert cache_short.shape == (1, 10, 8)
    assert cache_long.shape == (1, 100, 8)
    assert cache_long.numel() == 10 * cache_short.numel()  # 10× tokens → 10× elements
    print(f"✓ Test 3 passed: cache grows linearly — 10 tokens: {cache_short.shape}, 100 tokens: {cache_long.shape}")
    print(f"  numel short={cache_short.numel()}, long={cache_long.numel()}, ratio={cache_long.numel()/cache_short.numel():.0f}x")


@torch.inference_mode()
def test_no_future_leakage():
    """Test 4: future tokens không ảnh hưởng quá khứ (causal isolation)."""
    torch.manual_seed(3)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(1, 6, 32)
    y_full, _, _ = layer(x)  # (1, 6, 32)

    # Thay token tương lai bằng noise — output của 3 token đầu không đổi
    x_perturbed = x.clone()
    x_perturbed[:, 3:] = torch.randn(1, 3, 32)
    y_perturbed, _, _ = layer(x_perturbed)

    torch.testing.assert_close(y_full[:, :3], y_perturbed[:, :3], rtol=1e-5, atol=1e-6)
    print("✓ Test 4 passed: no future leakage — past outputs unchanged")


# Chạy tất cả — copy block này vào python và chạy
test_cached_decode_matches_full()
test_weights_are_token_addressable()
test_cache_grows_with_sequence()
test_no_future_leakage()
```

**Cách đọc kết quả khi test fail:**

| Test fail | Triệu chứng | Check đầu tiên |
|---|---|---|
| Test 1 | `cached decode != full forward` | In `past_len`, `q_pos`, `k_pos` và `causal` matrix — offset sai? |
| Test 2 | `weights` không có shape `(B,H,S,S)` | Kiểm tra `_heads` reshape/transpose |
| Test 3 | `cache_long.numel()` không = 10× `cache_short` | Đang cache nhầm `K/V` expand thay vì latent? |
| Test 4 | past outputs đổi khi future đổi | Mask dùng `>=` thay vì `<=`, hoặc thiếu `masked_fill(-inf)` |

Cả 4 tests đều phải pass trước khi đo benchmark — benchmark trên implementation sai là vô nghĩa.

## 5. Benchmark / Trade-offs — đo đúng thứ, đọc đúng slope

### 5.1 Tách prefill và decode — hai phase bottleneck khác nhau

Đừng gộp chung. Hai phase có bottleneck khác nhau:

| Phase | Work chính | MLA cost | Fixed-state cost |
|---|---|---|---|
| **Prefill** ($S$ tokens) | Chấm toàn bộ $S\times S$ (có thể chunkwise) | Vẫn $O(S^2)$ scores nhưng mỗi entry nhỏ hơn → ít bytes đọc hơn | Chunkwise parallel, $O(S)$ state updates — mỗi chunk update ma trận `(d_k, d_v)` |
| **Decode** (1 token) | Chấm 1 query với $S$ history | $O(S)$ reads + $O(S)$ scores — **tăng với $S$** — scores shape `(B,H,1,S)` | $O(1)$ — đọc state cố định `(d_k, d_v)` |

> Đo riêng: `prefill latency` (ms cho $S$ tokens) và `decode latency` (ms/token khi $S$ đã lớn). Đừng suy latency từ bytes.

### 5.2 Raw KV bytes — nhìn slope thay vì một con số

```python
def mha_cache_bytes(B, L, S, H, d_h, bytes_per_element=2):
    # B*L*S*2*H*d_h*p — mỗi token mỗi layer: K (H*d_h) + V (H*d_h)
    return B * L * S * (2 * H * d_h) * bytes_per_element


def mla_cache_bytes(B, L, S, d_c, d_rope, bytes_per_element=2):
    # B*L*S*(d_c+d_rope)*p — mỗi token mỗi layer: latent (d_c) + rotary (d_rope)
    return B * L * S * (d_c + d_rope) * bytes_per_element


def fixed_state_bytes(B, L, H, d_k, d_v, bytes_per_element=2):
    # B*L*H*d_k*d_v*p — shape accounting cho một matrix state minh họa — không phải KDA/Mamba thực
    # Không có S!
    return B * L * H * d_k * d_v * bytes_per_element


for S in (128, 1_024, 8_192, 32_768):
    mha = mha_cache_bytes(1, 32, S, 32, 128)
    mla = mla_cache_bytes(1, 32, S, 512, 64)
    fixed = fixed_state_bytes(1, 32, 4, 64, 64)
    print(
        f"S={S:6d} | MHA={mha / 2**20:8.1f} MiB "
        f"| MLA={mla / 2**20:8.1f} MiB "
        f"| fixed={fixed / 2**20:6.1f} MiB"
    )
# Output kỳ vọng (B=1, L=32):
# S=   128 | MHA=    64.0 MiB | MLA=     4.5 MiB | fixed=   1.0 MiB
# S=  1024 | MHA=   512.0 MiB | MLA=    36.0 MiB | fixed=   1.0 MiB
# S=  8192 | MHA=  4096.0 MiB | MLA=   288.0 MiB | fixed=   1.0 MiB
# S= 32768 | MHA= 16384.0 MiB | MLA=  1152.0 MiB | fixed=   1.0 MiB
```

Kết quả cần đọc theo **shape trend** (hình dáng đường cong):
- `MHA` tăng tuyến tính với slope lớn — đường dốc đứng.
- `MLA` tăng tuyến tính với slope nhỏ hơn (~14× trong ví dụ) — đường dốc thoải hơn nhưng vẫn đi lên.
- `Fixed-state` nằm ngang theo $S$ — đường phẳng.

> [!warning] Đừng suy latency từ bytes
> `Projection absorption`, kernels, `memory bandwidth`, batching và hardware có thể thay đổi throughput. Công thức trên chỉ là `retained tensors`. Hãy benchmark trên target implementation, dtype (BF16/FP8) và hardware nếu cần quyết định deployment. Các số cache/throughput trong DeepSeek-V2 là author-reported cho config của họ, không phải universal conversion.[^deepseek-v2-2024]

### 5.3 Khi nào chọn gì? — bảng quyết định

| Mục tiêu | Ưu tiên | Lựa chọn | Vì sao |
|---|---|---|---|
| Retrieval chính xác trên context dài (cần chỉ vào token cụ thể, ví dụ needle-in-haystack) | Token-addressability — mỗi token một slot | `MLA` / `MHA` / `GQA` | Query tạo weight riêng cho từng position — shape `(B,H,1,S)` |
| Context cực dài + memory cố định (ví dụ streaming vô hạn) | Bounded state — memory không tăng | Fixed-state (`KDA`, `Mamba-2`, `DeltaNet`) | State shape `(d_k, d_v)` cố định, không có trục $S$ |
| Cân bằng cả hai — vừa dài vừa cần retrieval | Giảm slope nhưng giữ retrieval ở một số layers | **Hybrid** (ví dụ 3×KDA + 1×MLA)[^kimi-linear-2025] | 75% layers fixed-state (giảm cache), 25% layers MLA (giữ token-addressability) |

## 6. Debug checklist — triệu chứng → nguyên nhân → check

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên (in shape ra) |
|---|---|---|
| Cache shape `(B, H, S, d)` thay vì `(B, S, d_c)` | Đang cache K/V đã expand, chưa cache latent | `print(present.shape)` — có chứa $S$ × $d_c$ không? Phải là `(B, S, d_c)` |
| `cached decode != full forward` (Test 1 fail) | `past_len` offset sai hoặc causal mask sai | In `past_len`, `q_pos`, `k_pos` và `causal` matrix — `q_pos` có = `past_len + arange(T_new)` không? |
| Future leakage (Test 4 fail) | Mask dùng `>=` thay vì `<=`, hoặc thiếu `masked_fill(-inf)` | Kiểm tra `scores` trước softmax có `-inf` ở future không: `print(scores[0,0])` |
| Throughput không tăng dù cache nhỏ hơn | Bottleneck là compute/bandwidth, không phải capacity | Profile riêng prefill vs decode, đo `memory bandwidth` — bytes nhỏ nhưng vẫn phải chấm $S$ scores |
| `query compression` không giảm cache | Hiểu nhầm — nó giảm `activation memory` khi training, không giảm decode cache | Đọc lại Section 2.4 — query hiện tại không phải history[^deepseek-v2-2024] |
| OOM ở context dài dù đã MLA | $S$ vẫn nhân với $L$ và $B$; batch lớn vẫn OOM | Tính $M_{MLA}=B·L·S·(d_c+d_h^R)·p$ với $B,L,S$ thực tế — thử giảm $B$ hoặc $S$ |
| `weights` shape sai (ví dụ `(B, T, H, S)`) | Transpose/reshape sai thứ tự axes | Kiểm tra `_heads`: `view(B,T,H,d_h).transpose(1,2)` → `(B,H,T,d_h)` mới đúng |

## 7. Giới hạn & bước tiếp theo

**Lab này không chứng minh:**
- Quality parity giữa MLA và MHA/GQA — cần ablation trên cùng data và task. DeepSeek-V2 báo cáo MLA cao hơn ở 3/4 benchmarks khó ở mỗi scale, nhưng đó là author-run, config-specific.[^deepseek-v2-2024]
- Speedup thực tế — phụ thuộc kernel, dtype, hardware. Toy `torch.cat` là teaching, không phải serving (`paged blocks`).[^deepseek-v2-2024]
- Fixed-state có luôn kém retrieval — hybrid có thể bù đắp, nhưng trade-off phụ thuộc workload.[^kimi-linear-2025]

**Học tiếp theo (theo roadmap):**

1. [Linear attention như fixed-state associative memory — bài học cho người mới](linear-attention-fixed-state-associative-memory-beginners-guide.md) — hiểu $S_t$ và `capacity interference` chi tiết.
2. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — cách delta correction và decay cải thiện fixed-state.
3. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — vì sao periodic MLA bù retrieval limits của KDA.[^kimi-linear-2025]
4. [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) và [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md) — các kỹ thuật giảm cache ở serving layer.
5. [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md) — hiểu rotation hoạt động như thế nào trước khi học decoupled RoPE.

**Bài tập đề xuất (làm theo thứ tự):**
1. Vẽ đồ thị `context length → raw cache GiB` cho MHA và MLA với dimensions của model bạn chọn — quan sát hai đường thẳng slope khác nhau.
2. Sửa `ToyLatentAttention` để cache thêm `position key` nhỏ (thêm $d_h^R$ chiều); xác nhận cache width = $d_c + d_h^R$ bằng `assert present.shape[-1] == d_c + d_h_R`.
3. In `step_w[0,0,0]` và chứng minh vector có đúng $S$ weights — dấu hiệu token-addressability — và tổng = 1.
4. Thay `d_latent` từ 32 xuống 4, train toy trên copy task và quan sát quality/capacity trade-off — latent càng nhỏ càng mất chi tiết.
5. Implement additive fixed-state $S_t = S_{t-1} + \phi(k_t)^{\top} v_t$ với $\phi = \text{elu}+1$; so sánh state shapes ở 128 và 8,192 tokens — phải bằng nhau.
6. Đọc [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) và giải thích vì sao total model state vẫn sequence-growing dù đa số layers là fixed-state.

## Relationships

- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng lý thuyết, code và memory experiment cho MLA.
- **Builds on:** [Multi-head Latent Attention](multi-head-latent-attention.md), [KV caching](kv-caching.md) và [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md).
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — nơi history được aggregate vào bounded recurrent state thay vì giữ per-token latent slots.
- **Prepares for:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), [Structured State Space Duality](structured-state-space-duality.md) và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md).
- **Contextualizes:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — nơi periodic MLA bù retrieval limits của fixed-state KDA.[^kimi-linear-2025]

## Evidence limits

Cơ chế, formulas và dimensions DeepSeek-V2 được lấy từ primary technical report. Các so sánh quality, cache reduction và throughput là author-run, architecture- và config-specific; bài này không tái lập chúng. Fixed-state contrast dựa trên primary associative-memory analysis và Kimi Linear report. Phần cost decomposition, toy code, tests, checklist và ví dụ số học là **pedagogical synthesis** — toy code không implement full production MLA (thiếu `decoupled RoPE`, `query compression`, `projection absorption`) và không dùng để suy ra quality hay speedup.[^deepseek-v2-2024][^fast-weight-programmers-2021][^kimi-linear-2025]

[^deepseek-v2-2024]: DeepSeek-AI, "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model," arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and Appendices C–D.
[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, "Linear Transformers Are Secretly Fast Weight Programmers," ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4.
[^kimi-linear-2025]: Kimi Team, "Kimi Linear: An Expressive, Efficient Attention Architecture," arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 1–3 and 6.
