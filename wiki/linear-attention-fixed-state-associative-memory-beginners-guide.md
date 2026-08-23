---
type: Synthesis
title: "Linear attention như fixed-state associative memory — bài học cho người mới"
description: A beginner-first course that derives linear attention as fixed-state associative memory from softmax kernel to recurrent write/read, explains every formula and shape, shows interference and capacity limits, and verifies a PyTorch implementation.
tags: [attention, associative-memory, linear-attention, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-23T14:30:00Z }
sources:
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# Linear attention như fixed-state associative memory — bài học cho người mới

`Linear attention` có thể hiểu như một `fixed-state associative memory`: mỗi token **ghi (write)** một cặp `key → value` vào cùng một `matrix state` $S_t$, còn token sau **đọc (read)** state đó bằng `query` của mình. Khác với `softmax attention` giữ một `K/V slot` riêng cho từng token cũ (shape tăng với $S$), `linear attention` gom mọi history vào một ma trận có shape cố định $(m \times d_v)$ — không có trục $S$. Đổi lại, nhiều `association` chồng lên nhau trong cùng state gây `interference` (nhiễu chéo) và không còn bảo đảm `exact retrieval` như khi giữ slot riêng — đây là trade-off cốt lõi: **bounded state & decode cost hằng số** đổi lấy **retrieval precision & effective capacity hữu hạn**.[^fast-weight-programmers-2021][^kimi-linear-2025]

> [!success] Sau bài này, bạn có thể
> 1. Phân biệt `token-addressable memory` (mỗi token một slot) với `fixed-state memory` (một state chung) qua shape có chứa $S$ hay không.
> 2. Tự suy ra công thức `recurrent write/read` từ `kernel form` $\kappa(q,k)=\phi(q)^{\top}\phi(k)$ — giải thích từng ký hiệu, từng shape, từng phép nhân.
> 3. Giải thích vai trò riêng của `matrix state` $S_t$ và `normalization state` $z_t$ và vì sao cần $\varepsilon$.
> 4. Tạo ví dụ `interference` bằng tay: `crosstalk` khi keys không trực giao và `collision` khi cùng key ghi hai values.
> 5. Implement `normalized causal linear attention` bằng PyTorch và chứng minh `recurrent == parallel prefix` bằng `torch.testing.assert_close`.
> 6. Đọc đúng `memory & compute table` — vì sao `fixed-state` không đồng nghĩa với infinite context, lossless, hay constant latency toàn model.

## 1. Điều cần biết trước

**Bạn cần biết ở mức trực giác (nếu chưa, đọc trước các link sau):**
- `Q/K/V`, `scaled dot-product attention`, `causal mask` — xem [Attention: beginner's guide](attention-beginner-guide.md) và [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md).
- `KV caching` và vì sao cache tăng theo $S$ — xem [KV caching](kv-caching.md) và [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md).
- Phân biệt `prefill` (xử lý cả prompt) với `decode` (sinh từng token) — xem [LLM inference lifecycle: training, prefill, decode, và latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md).

**Toán tối thiểu cần:**
- Vector shape `(d,)` là một danh sách $d$ số; ma trận `(a, b)` là bảng $a$ hàng $b$ cột.
- Nhân ma trận: `(a, b) × (b, c) → (a, c)` — chiều giữa phải khớp.
- `Outer product` $u v^{\top}$: vector cột `(m, 1)` nhân vector hàng `(1, d_v)` → ma trận `(m, d_v)`.
- `Softmax` chuẩn hóa một vector về tổng = 1: $\operatorname{softmax}(x)_i = e^{x_i}/\sum_j e^{x_j}$.
- Ký hiệu `einsum` sẽ được giải thích ngay khi dùng.

**Bài này không cover:** `kernel CUDA`, `distributed training`, `MoE routing`, `quantization`, `PagedAttention` block layout. Code dùng `torch.einsum` và `for` loop để dễ đọc — không phải serving kernel.

> [!tip] Cách đọc mọi công thức trong bài
> Mỗi công thức sẽ mổ thành 4 dòng: **Ký hiệu là gì → Shape là gì → Phép toán làm gì → Kết quả shape ra sao**. Hãy theo dõi shape chảy — đó là cách nhanh nhất để không lạc.

**Ký hiệu thống nhất (đọc một lần, dùng cả bài):**

| Ký hiệu | Shape ở một `head` | Ý nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| $B$ | scalar | `batch size` — số sequences song song | 1, 2, 4 |
| $T$ | scalar | `sequence length` hiện tại | $S$ trong cache accounting |
| $d_k$ | scalar | chiều `key/query` gốc | ví dụ 128 |
| $d_v$ | scalar | chiều `value` | ví dụ 128 |
| $m$ | scalar | `feature width` sau $\phi$ | = $d_k$ nếu dùng ELU+1 toy, có thể > $d_k$ nếu DPFP |
| $q_t, k_t$ | $(d_k,)$ | `query`/`key` của token $t$ | vector |
| $v_t$ | $(d_v,)$ | `value` cần lưu | vector |
| $\phi(q_t), \phi(k_t)$ | $(m,)$ | `feature-mapped` query/key | vector dương nếu ELU+1 |
| $S_t$ | $(m, d_v)$ | `associative matrix state` | **không có trục $T$** |
| $z_t$ | $(m,)$ | `normalization state` | tổng $\phi(k)$ |
| $o_t$ | $(d_v,)$ | output đọc ra | vector |

Với `batch` và `multi-head`, thêm 2 trục: $S_t$ shape thực tế `(B, H, m, d_v)`, $z_t$ `(B, H, m)`.

## 2. Lý thuyết cốt lõi — giải từng công thức, từng shape

### 2.1 Ôn nhanh: softmax attention là gì, shape chảy ra sao?

Với một `head` tại token $t$, có `hidden state` $x_t \in \mathbb{R}^{d}$ (shape `(d,)`):

$$
q_t = x_t W^Q,\quad k_t = x_t W^K,\quad v_t = x_t W^V
$$

| Thành phần | Shape | Giải thích |
|---|---|---|
| $x_t$ | `(d,)` | vector ẩn của token $t$ |
| $W^Q,W^K$ | `(d, d_k)` | ma trận `projection` cho query/key |
| $W^V$ | `(d, d_v)` | ma trận `projection` cho value |
| $q_t,k_t$ | `(d_k,)` | `(1, d) × (d, d_k) → (1, d_k)` — nén qua projection |
| $v_t$ | `(d_v,)` | `(1, d) × (d, d_v) → (1, d_v)` |

Output causal tại $t$ (chỉ nhìn $j \le t$):

$$
o_t = \sum_{j=1}^{t} \alpha_{t,j}\,v_j,\qquad
\alpha_{t,j}=\frac{\exp(q_t^{\top}k_j/\sqrt{d_k})}{\sum_{i=1}^{t}\exp(q_t^{\top}k_i/\sqrt{d_k})}
$$

Giải từng mảnh:

| Mảnh | Shape | Ý nghĩa |
|---|---|---|
| $q_t^{\top}k_j$ | scalar | `dot product` — độ hợp giữa query hiện tại và key quá khứ $j$ |
| $/\sqrt{d_k}$ | scalar | `scale` — chia để tránh số lớn làm `softmax` bão hòa |
| $\exp(\cdot)$ | scalar | đưa score về dương, phóng đại gap |
| $\sum_i \exp(\cdot)$ | scalar | tổng mẫu số để chuẩn hóa |
| $\alpha_{t,j}$ | scalar | weight cho token $j$, $\sum_j \alpha_{t,j}=1$ |
| $\alpha_{t,j}v_j$ | `(d_v,)` | scalar × vector — value được cân |
| $\sum_j$ | `(d_v,)` | cộng $t$ vectors → output |

**Dạng ma trận cho cả sequence dài $S$ (dễ thấy shape hơn):**
Xếp $S$ tokens thành $X \in \mathbb{R}^{S \times d}$ (shape `(S, d)`):

$$
Q = XW^Q \in \mathbb{R}^{S \times d_k},\;
K = XW^K \in \mathbb{R}^{S \times d_k},\;
V = XW^V \in \mathbb{R}^{S \times d_v}
$$

$$
\text{Scores}=\frac{QK^{\top}}{\sqrt{d_k}}\in\mathbb{R}^{S\times S},\;
\text{Weights}=\operatorname{softmax}(\text{Scores}+M)\in\mathbb{R}^{S\times S},\;
O=\text{Weights}\,V\in\mathbb{R}^{S\times d_v}
$$

| Phép | Shape | Ý nghĩa |
|---|---|---|
| $QK^{\top}$ | `(S, d_k) × (d_k, S) → (S, S)` | mỗi hàng là 1 query so với mọi key |
| $M$ | `(S, S)` | `causal mask`: 0 ở $j\le i$, $-\infty$ ở $j>i$ — cộng trước softmax để $e^{-\infty}=0$ |
| `softmax` theo hàng | `(S, S)` | mỗi hàng tổng = 1 — hàng $i$ là weights của token $i$ |
| `Weights × V` | `(S, S) × (S, d_v) → (S, d_v)` | mỗi output là trung bình có trọng số của values quá khứ |

Với `batch` và `multi-head`: $Q$ shape `(B, H, S, d_k)`, Scores `(B, H, S, S)`. **Trục cuối $S$ chính là token-addressability** — mỗi cột là một token cụ thể.

**Vì sao KV cache tăng theo $S$?** Khi decode, ta cache $K$ và $V$ của mọi token cũ để không tính lại. Mỗi layer mỗi head lưu $S$ vectors $k_j$ và $S$ vectors $v_j$:

$$
M_{KV}=B\cdot L\cdot S\cdot(2Hd_h)\cdot p
$$

- $2Hd_h$: mỗi token mỗi layer: $H$ keys `(d_h,)` + $H$ values `(d_h,)` = $2Hd_h$ số.
- Nhân $S$: $S$ tokens → $S$ bản copy. **Có $S$ trong công thức.**
- $p$: bytes mỗi số (BF16 → 2). `FlashAttention` đổi thứ tự tính và giảm `HBM traffic` nhưng **vẫn là exact softmax attention** — không xóa trục $S$ trong cache.[^gpt2-kimi3-2026]

### 2.2 Hai câu hỏi phải tách — nếu gộp sẽ hiểu sai mọi paper

| Câu hỏi | Hỏi gì? | MLA trả lời | Fixed-state trả lời |
|---|---|---|---|
| **Mỗi token tốn bao nhiêu?** (`per-token state`) | bytes/token/layer — một ngăn tủ dày bao nhiêu? | Ít hơn MHA (ngăn mỏng) — $d_c + d_h^R$ | Là một phần của state chung |
| **Tổng state có tăng theo $S$?** (`sequence scaling`) | Shape có chứa $S$ không? | **Có** — vẫn $(B,S,\cdot)$ | **Không** — $(B,H,m,d_v)$ |

> [!important] Quy tắc đọc paper
> Thấy "giảm KV cache 90%" → hỏi ngay: **công thức còn thừa số $S$ không?** Nếu còn, đó là **giảm slope (độ dốc)**, không phải xóa slope. MLA làm ngăn tủ mỏng hơn; fixed-state thay tủ bằng bảng trắng chung — shape không còn trục $S$.

**Hình dung để nhớ:**

```text
MHA         = tủ hồ sơ: mỗi token = 1 ngăn riêng, mỗi ngăn DÀY (2·H·d_h số)
MLA         = cùng tủ đó nhưng mỗi ngăn MỎNG (d_c + d_h^R) — vẫn từng ngăn riêng
Fixed-state = bảng trắng: mọi token ghi đè lên nhau trên 1 mặt phẳng (H·m·d_v)
              Shape (m, d_v) ở token 10 và token 1,000,000 là như nhau
```

### 2.3 Từ kernel attention đến recurrent state — suy ra từng dòng

#### Bước 1 — Viết attention như kernel

$$
o_t=\frac{\sum_{j=1}^{t}\kappa(q_t,k_j)\,v_j}{\sum_{j=1}^{t}\kappa(q_t,k_j)}
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $\kappa(q_t,k_j)$ | scalar | `similarity kernel` — đo độ hợp giữa query $t$ và key $j$ |
| Tử số | `(d_v,)` | tổng values được cân bởi kernel |
| Mẫu số | scalar | tổng kernel để chuẩn hóa — giống mẫu số của softmax |
| Kết quả $o_t$ | `(d_v,)` | vector |

Softmax attention dùng kernel $\kappa(q,k)\approx\exp(q^{\top}k/\sqrt{d_k})$ — **không tách được thành $\phi(q)^{\top}\phi(k)$ với $m$ nhỏ**. Linear attention **chọn** kernel tách được:

$$
\kappa(q,k)=\phi(q)^{\top}\phi(k)=\sum_{r=1}^{m}\phi(q)_r\cdot\phi(k)_r
$$

| Thành phần | Shape | Ý nghĩa |
|---|---|---|
| $\phi(q_t)$ | `(m,)` | query sau feature map |
| $\phi(k_j)$ | `(m,)` | key sau feature map |
| $\phi(q_t)^{\top}\phi(k_j)$ | scalar | dot product trong feature space — thay cho $\exp(q^{\top}k)$ |

Ví dụ toy: $\phi(x)=\operatorname{ELU}(x)+1$ → mọi phần tử dương, $m=d_k$.

#### Bước 2 — Thay kernel và đổi thứ tự ngoặc (associativity)

Tử số với kernel tách được:

$$
\sum_{j=1}^{t}\big(\phi(q_t)^{\top}\phi(k_j)\big)\,v_j
$$

Vì $\phi(q_t)^{\top}\phi(k_j)$ là scalar, ta có thể viết $\big(\phi(q_t)^{\top}\phi(k_j)\big)v_j = \big(\phi(k_j)v_j^{\top}\big)^{\top}\phi(q_t)$ — nhưng cách trực quan hơn là dùng tính kết hợp của nhân ma trận:

$$
\sum_{j=1}^{t}\big(\phi(q_t)^{\top}\phi(k_j)\big)v_j^{\top}
= \phi(q_t)^{\top}\left(\sum_{j=1}^{t}\phi(k_j)v_j^{\top}\right)
$$

Giải shape từng mảnh:

| Mảnh | Shape | Phép toán |
|---|---|---|
| $\phi(k_j)$ | `(m,)` | vector cột `(m, 1)` |
| $v_j^{\top}$ | `(1, d_v)` | vector hàng |
| $\phi(k_j)v_j^{\top}$ | `(m, d_v)` | **outer product** — ma trận ghi association $k_j\to v_j$ |
| $\sum_{j=1}^{t}\phi(k_j)v_j^{\top}$ | `(m, d_v)` | cộng $t$ ma trận → **state** |
| $\phi(q_t)^{\top}$ | `(1, m)` | vector hàng |
| $\phi(q_t)^{\top}(\sum_j \cdots)$ | `(1, d_v)` | vector hàng × ma trận → output |

Đặt:

$$
S_t \triangleq \sum_{j=1}^{t}\phi(k_j)v_j^{\top}\in\mathbb{R}^{m\times d_v}
$$

Ta có **recurrent write** (cộng dồn):

$$
\boxed{S_t = S_{t-1} + \phi(k_t)\,v_t^{\top}}\qquad\text{shape: }(m,d_v)=(m,d_v)+(m,)(d_v,)
$$

Và **unnormalized read**:

$$
\boxed{\tilde{o}_t = \phi(q_t)^{\top}S_t}\qquad\text{shape: }(1,d_v)=(1,m)\times(m,d_v)
$$

> [!note] Vì sao gọi là "associative memory"?
> $S_t$ như một `weight matrix` được lập trình nhanh (fast weight) bởi chuỗi outer products. Mỗi dòng của $S_t$ ứng với một chiều feature của key; mỗi cột ứng với một chiều của value. Ghi là cộng outer product; đọc là query chấm với state.[^fast-weight-programmers-2021]

**Số chiều batch/head:** với $B$ sequences và $H$ heads, $S_t$ shape `(B, H, m, d_v)` — vẫn không có $T$.

#### Bước 3 — Normalization state $z_t$ (vì sao cần?)

Tử số đã gom được vào $S_t$, còn **mẫu số** của kernel form:

$$
\sum_{j=1}^{t}\phi(q_t)^{\top}\phi(k_j)=\phi(q_t)^{\top}\left(\sum_{j=1}^{t}\phi(k_j)\right)
$$

Đặt:

$$
z_t \triangleq \sum_{j=1}^{t}\phi(k_j)\in\mathbb{R}^{m}
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $z_t$ | `(m,)` | tổng các feature keys — **không chứa $v_j$** |
| $z_t = z_{t-1}+\phi(k_t)$ | `(m,)=(m,)+(m,)` | recurrent giống $S_t$ nhưng cộng vector |

Read đầy đủ có chuẩn hóa:

$$
\boxed{o_t = \frac{\phi(q_t)^{\top}S_t}{\phi(q_t)^{\top}z_t+\varepsilon}}\qquad
\begin{aligned}
\text{tử: }&(1,m)\times(m,d_v)\to(1,d_v)\\
\text{mẫu: }&(1,m)\times(m,1)\to\text{scalar}
\end{aligned}
$$

- Mẫu số là scalar — chia mỗi chiều của vector tử cho cùng một số.
- $\varepsilon$ (ví dụ $10^{-6}$) chỉ để tránh chia cho 0 khi $\phi(q_t)^{\top}z_t$ rất nhỏ — **không sửa được feature map kém hay state đã nhiễu**.
- Khi $\phi$ dương (ELU+1), mẫu số dương và diễn giải như tổng similarity.
- Với `batch`: $\phi(q_t)^{\top}z_t$ shape `(B,)` → `(B, 1)` để chia cho `(B, d_v)`.

> [!important] Convention causal: write trước hay read trước?
> Công thức trên là **write trước rồi read** → output tại $t$ bao gồm token hiện tại ($j\le t$). Nếu cần strict past ($j<t$) như training causal, hãy **read trước write**. Hai conventions lệch 1 vị trí — phải nhất quán giữa code và test.

**Tóm tắt dataflow một step (text diagram):**

```text
Token t:  k_t ──► φ(k_t) ──┐
          v_t ────────────┤──► outer product φ(k_t)·v_tᵀ ──► S_t = S_{t-1} + ...
          q_t ──► φ(q_t) ──┼──► read: φ(q_t)ᵀ S_t / (φ(q_t)ᵀ z_t + ε) ──► o_t
                          └──► z_t = z_{t-1} + φ(k_t)
Shape:         (m,)  (d_v,)      (m, d_v)         (m,)              (d_v,)
```

### 2.4 Vì sao đây là associative memory? — đọc bằng query giống key

Giả sử $m=2$, có hai `mapped keys` trực giao chuẩn hóa:

$$
u_A=[1,0]^{\top},\; u_B=[0,1]^{\top},\qquad S=u_Av_A^{\top}+u_Bv_B^{\top}
$$

| Phép | Shape | Kết quả |
|---|---|---|
| $u_A^{\top}S$ | `(1,2)×(2,d_v)→(1,d_v)` | $= (u_A^{\top}u_A)v_A^{\top}+(u_A^{\top}u_B)v_B^{\top}=1\cdot v_A^{\top}+0\cdot v_B^{\top}=v_A^{\top}$ |

Query bằng $u_A$ trả về đúng $v_A$ — **không cần biết $v_A$ được ghi ở token index nào**. Đó là `content-based retrieval` (địa chỉ là nội dung key, không phải số thứ tự token).

Tổng quát sau $n$ writes:

$$
q^{\top}S=\sum_{i=1}^{n}(q^{\top}k_i)\,v_i^{\top}
$$

Mỗi value được lấy theo similarity $q^{\top}k_i$ — giống attention nhưng similarity tính trong feature space $\phi$.

**So sánh trực tiếp:**

| Thuộc tính | Softmax + KV cache | Linear fixed-state |
|---|---|---|
| History | $S$ entries riêng `(S, d_k)+(S, d_v)` | 1 matrix `(m, d_v)` chung |
| Có trục $S$ trong state? | Có | Không |
| Query chấm từng token? | Có — `Scores` shape `(B,H,S,S)` | Không — đọc state đã gộp |
| State tăng theo $S$? | Có — $O(S)$ | Không — $O(m d_v)$ |
| Exact access slot $j$ | Có (cấu trúc) | Không bảo đảm |
| Rủi ro chính | cache/bandwidth tăng | superposition & interference |

> Token-addressable không bảo đảm model luôn retrieve đúng — nó chỉ giữ slots riêng. Fixed-state có thể retrieve rất tốt trên distribution đã học, nhưng không có slot lossless riêng cho mỗi token.

### 2.5 Interference — khi nhiều memories dùng chung một state

#### 2.5.1 Crosstalk khi keys không trực giao

Ghi $S=k_Av_A^{\top}+k_Bv_B^{\top}$, đọc bằng $q=k_A$:

$$
k_A^{\top}S = \|k_A\|^2 v_A^{\top} + (k_A^{\top}k_B)\,v_B^{\top}
$$

| Hạng | Scalar | Ý nghĩa |
|---|---|---|
| $\|k_A\|^2 v_A^{\top}$ | $\|k_A\|^2$ | signal mong muốn |
| $(k_A^{\top}k_B)v_B^{\top}$ | $k_A^{\top}k_B$ | **crosstalk** — $v_B$ rò vào |

Nếu $k_A^{\top}k_B\neq 0$, retrieval của $A$ bị nhiễm $B$. `Feature map` và `learned projections` có thể cố tách addresses, nhưng không gian $m$ chiều chỉ có tối đa $m$ hướng trực giao — không tạo được vô hạn directions.

**Ví dụ số cụ thể ($m=2, d_v=2$):**

```
k_A = [1, 0], v_A = [10, 0]
k_B = [0.8, 0.6] (unit, overlap với k_A), v_B = [0, 30]
S = k_A·v_Aᵀ + k_B·v_Bᵀ = [[10, 0],[0, 0]] + [[0, 24],[0, 18]] = [[10, 24],[0, 18]]
q = k_A = [1, 0] → qᵀS = [10, 24]  ← v_B rò 24 vào chiều thứ 2!
```

#### 2.5.2 Collision: cùng key, values khác nhau

Ghi cùng key $u$ hai lần với $v_1, v_2$:

$$
S = u v_1^{\top} + u v_2^{\top}=u(v_1+v_2)^{\top}
$$

Pure additive memory không biết write thứ hai là:
- evidence bổ sung cần cộng?
- record khác tình cờ trùng address?
- hay update mới cần thay thế?

Với normalized read và hai writes cùng key, kết quả có xu hướng là **mixture/average** thay vì tự động trả về latest value. Đây là lý do `delta rule` đọc association hiện tại rồi ghi correction, còn `decay` giúp quên rộng hơn.[^fast-weight-programmers-2021][^kimi-linear-2025]

#### 2.5.3 Capacity không phải "quên ở token $m+1$"

Trong phân tích lý tưởng của paper, để **không nhiễu hoàn toàn** (interference-free), các mapped keys phải đôi một trực giao. Không gian $m$ chiều chứa tối đa $m$ vectors trực giao → số associations không nhiễu ≤ $m$ (ví dụ $d_{\text{dot}}$).[^fast-weight-programmers-2021]

**Đừng diễn giải thành "model quên chính xác ở token $m+1$":**

- Keys không cần trực giao hoàn toàn để task thành công — nhiễu nhỏ có thể chấp nhận.
- Nhiều tokens có thể củng cố cùng association (cùng key, cùng value) — không tốn capacity mới.
- Model có thể học chỉ giữ task-relevant information, bỏ chi tiết thừa.
- `Values`, `sparsity`, `normalization`, `gates`, `data distribution` đều ảnh hưởng effective capacity.
- Đây là **representational bound** trong điều kiện lý tưởng, không phải ngưỡng benchmark chung.

### 2.6 Fixed-state trade-off qua memory và compute — công thức có $S$ hay không?

Gọi $m$ = feature width, $d_v$ = value width, bỏ qua $B,L,H$ để tập trung scaling theo $S$:

| Cơ chế | Persistent decode state | Work mỗi decode step | Retrieval |
|---|---:|---:|---|
| Softmax + KV cache | $O(S(d_k+d_v))$ — **có $S$** | tăng với $S$ — chấm $S$ entries | score từng token |
| MLA-like compressed | $O(S\cdot r)$ — **có $S$** | vẫn tăng với $S$ | score từng compressed entry |
| Linear fixed-state | $O(m d_v + m)$ — **không $S$** | $O(m d_v)$ — hằng số | đọc aggregated state |

Chi tiết:

- **State size:** $S_t$ `(m, d_v)` + $z_t$ `(m,)` → $m(d_v+1)$ số — ví dụ $m=128, d_v=128$ → ~16K số/head — không đổi khi $S$ từ 1K lên 1M.
- **Work/step:** outer product `(m, d_v)` + read `(m, d_v)` → $O(m d_v)$ — không chứa $S$.
- **Nhưng:** model vẫn phải xử lý từng token autoregressively; end-to-end latency còn `projections`, `FFN/MoE`, `kernels`, `memory movement`, `batching`.
- **Training/prefill:** cần tạo output cho mọi position — tổng work không phải $O(1)$; recurrent formulation có dependency tuần tự → systems dùng `parallel/chunkwise` formulations khi training/prefill.[^kimi-linear-2025][^kimi-k3-2026]
- **Hybrid:** Kimi Linear dùng `chunkwise KDA` cho multi-token và `recurrent` cho generation; KDA state shape `(d_k, d_v)` nhưng toàn model vẫn có `MLA cache` tăng theo $S$ ở global layers.[^kimi-linear-2025]

> [!warning] Chữ "Linear" đang nói về gì?
> `Linear attention` nói **sequence scaling** của state/compute theo $S$ dưới formulation phù hợp. Nó **không** có nghĩa mọi operation là hàm tuyến tính của input, model có constant total runtime, hay output là linear sau khi tính Q/K/V và $\phi$.

### 2.7 Feature map cũng là một trade-off — kernel hay state?

Reassociation chỉ hoạt động khi $\kappa(q,k)=\phi(q)^{\top}\phi(k)$. Architecture phải chọn $\phi$.

**Toy choice phổ biến để học:**

$$
\phi(x)=\operatorname{ELU}(x)+1=
\begin{cases}
x+1 & x\ge 0\\
e^{x} & x<0
\end{cases}
\quad\text{(luôn dương, shape giữ nguyên }(d_k,)\to(m,)\text{ với }m=d_k)
$$

| $\phi$ | $m$ | Tính chất | Trade-off |
|---|---|---|---|
| ELU+1 | $d_k$ | dương, đơn giản | kernel thô, capacity = $d_k$ |
| ReLU-product / DPFP | $>d_k$ (ví dụ $2d_k$) | deterministic, mở rộng feature space | capacity bound tăng nhưng state $m\times d_v$ lớn hơn[^fast-weight-programmers-2021] |
| Random features | $m$ lớn | xấp xỉ softmax kernel | variance, compute tăng |
| Learned $\phi$ + decay | $d_k$ | data-dependent | cần training |

**Hai nguồn mất retrieval precision — phải tách:**

1. **Kernel limitation:** $\phi(q)^{\top}\phi(k)$ không có toàn bộ selectivity của exact softmax kernel $\exp(q^{\top}k/\sqrt{d_k})$.
2. **State interference:** nhiều associations superpose trong finite state — dù kernel tốt, state hẹp vẫn nhiễu.

Tăng $m$ giúp cả hai, nhưng làm fixed state rộng hơn ($m\cdot d_v$ tăng). Không có "free infinite context": state shape bounded còn information phải được compress, overwritten, decayed hoặc mixed.

### 2.8 Từ additive memory đến delta rule và gating — vì sao cần?

Pure additive:

$$
S_t = S_{t-1} + k_t v_t^{\top}
$$

không có overwrite tường minh. `Delta rule` đọc prediction hiện tại rồi chỉ ghi **residual error**:

$$
\bar{v}_t = S_{t-1}^{\top}k_t \quad\text{shape: }(d_v,)=(d_v,m)\times(m,)
$$

$$
S_t = S_{t-1} + \beta_t\,k_t\,(v_t-\bar{v}_t)^{\top}\quad\text{shape: }(m,d_v)=(m,d_v)+\text{scalar}\cdot(m,1)\times(1,d_v)
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $\bar{v}_t$ | `(d_v,)` | value mà state hiện tại sẽ trả về cho key $k_t$ |
| $v_t-\bar{v}_t$ | `(d_v,)` | error — phần chưa đúng |
| $\beta_t\in[0,1]$ | scalar | `learning rate` / gate cho update này |

Nếu keys trực giao và $\beta_t=1$, update sửa đúng association được address mà ít ảnh hưởng associations trực giao. `Learned decay` bổ sung cơ chế quên rộng hơn (nhân state cũ với $\alpha_t<1$). Chi tiết đầy đủ xem [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — từ additive → DeltaNet → Gated DeltaNet → KDA (channel-wise decay).[^fast-weight-programmers-2021][^kimi-linear-2025]

Các cải tiến này quản lý finite state tốt hơn; chúng **không** biến state thành token-addressable lossless storage.

### 2.9 Vì sao hybrid hợp lý? — 3 KDA + 1 MLA

Pure fixed-state phù hợp khi model có thể nén history thành task-relevant sufficient state. Nó khó với bài cần **exact copy** hoặc truy xuất một item cụ thể trong history dài. Kimi Linear report gọi long-context retrieval là bottleneck chính của pure linear và kết hợp **3 KDA layers + 1 global MLA layer** trong pattern thử nghiệm của họ — tỷ lệ 3:1 cho perplexity tốt nhất trong ablation của họ (5.65 vs 5.66 ở 1:1, 5.70 ở 7:1), không phải universal optimum.[^kimi-linear-2025]

| Pathway | State | Retrieval | Dùng khi |
|---|---|---|---|
| **KDA/linear recurrent** | bounded `(d_k, d_v)` | learned compression, recurrent read | đa số layers — tiết kiệm memory |
| **Global MLA** | sequence-growing | token-level softmax retrieval | periodic — bù exact retrieval |

Kimi K3 cũng giữ hybrid fixed-state KDA + periodic global MLA, nên không nên mô tả toàn model như có memory hoàn toàn constant theo context.[^kimi-k3-2026] Hybrid là **kiến trúc cụ thể, đo được**, không phải tuyên bố lý thuyết.

## 3. Implementation (PyTorch tối thiểu) — đọc shape từng dòng

Code dưới ưu tiên semantics và testability — nhận Q/K/V đã projected cho **một head**. Production còn `multi-head layout`, `learned projections`, `output projection`, `normalization`, `gating`, `optimized kernels`. Toy dùng `torch.cat`-like `cumsum` cho reference — dễ đọc nhưng không phải serving.

- `position_ids` là **absolute** (0, 1, 2, ...) — không dùng relative offset trong toy này.
- Không dùng `RoPE` trong toy này (để tập trung vào state); nếu có, convention sẽ là `interleaved` (xoay cặp `(0,1),(2,3),...`) — ghi chú để không nhầm khi đọc production.
- Cache shape mỗi layer: `S_t` là `(B, m, d_v)` — **không có trục $T$** — đây là dấu hiệu fixed-state.

```python
import torch
import torch.nn.functional as F


def positive_feature(x: torch.Tensor) -> torch.Tensor:
    """Toy non-negative feature map φ(x) = ELU(x) + 1 — shape giữ nguyên."""
    # x: (B, T, d_k) -> (B, T, m) với m == d_k trong toy này
    return F.elu(x) + 1.0


def linear_attention_recurrent(q, k, v, eps=1e-6):
    """
    Normalized causal linear attention — write trước rồi read (bao gồm token hiện tại).
    Shapes:
      q, k: (B, T, d_k) — query/key đã projected
      v:    (B, T, d_v) — value
      return: (B, T, d_v)
    State shapes (không chứa T):
      S_t: (B, m, d_v)   — associative matrix
      z_t: (B, m)        — normalizer
    """
    qf = positive_feature(q)  # (B, T, m) — m == d_k trong toy
    kf = positive_feature(k)  # (B, T, m)

    B, T, M = qf.shape       # M = m = feature width
    Dv = v.size(-1)          # d_v
    state = q.new_zeros(B, M, Dv)   # S_0 = 0, shape (B, m, d_v)
    normalizer = q.new_zeros(B, M)  # z_0 = 0, shape (B, m)
    outputs = []

    for t in range(T):
        # Write: S_t = S_{t-1} + φ(k_t) ⊗ v_t
        #   φ(k_t): (B, m) — key feature của token t
        #   v_t:    (B, d_v) — value của token t
        #   outer:  (B, m, 1) × (B, 1, d_v) → (B, m, d_v) — einsum "bm,bv->bmv"
        state = state + torch.einsum("bm,bv->bmv", kf[:, t], v[:, t])
        #   kf[:,t]: (B, m), v[:,t]: (B, d_v) → state: (B, m, d_v)

        # Accumulate normalizer: z_t = z_{t-1} + φ(k_t) — shape (B, m)
        normalizer = normalizer + kf[:, t]

        # Read: o_t = φ(q_t)ᵀ S_t / (φ(q_t)ᵀ z_t + ε)
        #   φ(q_t): (B, m), S_t: (B, m, d_v) → numerator: (B, d_v) — einsum "bm,bmv->bv"
        numerator = torch.einsum("bm,bmv->bv", qf[:, t], state)
        #   φ(q_t)ᵀ z_t: (B, m) · (B, m) → (B,) → unsqueeze → (B, 1) để chia cho (B, d_v)
        denominator = torch.einsum("bm,bm->b", qf[:, t], normalizer).unsqueeze(-1)
        outputs.append(numerator / denominator.clamp_min(eps))

    # Stack T outputs: list of (B, d_v) → (B, T, d_v)
    return torch.stack(outputs, dim=1)


def linear_attention_parallel_reference(q, k, v, eps=1e-6):
    """
    Materialize mọi prefix state để verify — KHÔNG phải implementation tiết kiệm memory.
    Dùng cumsum để tạo S_1, S_2, ..., S_T rồi đọc song song.
    """
    qf = positive_feature(q)  # (B, T, m)
    kf = positive_feature(k)  # (B, T, m)

    # writes: (B, T, m, d_v) — mỗi position một outer product
    writes = torch.einsum("btm,btv->btmv", kf, v)
    # prefix_states: cumsum theo T → (B, T, m, d_v) — S_t tại mỗi t
    prefix_states = writes.cumsum(dim=1)
    # prefix_normalizers: (B, T, m) — z_t tại mỗi t
    prefix_normalizers = kf.cumsum(dim=1)

    # numerator: (B, T, m) · (B, T, m, d_v) → (B, T, d_v) — einsum "btm,btmv->btv"
    numerator = torch.einsum("btm,btmv->btv", qf, prefix_states)
    # denominator: (B, T, m) · (B, T, m) → (B, T) → (B, T, 1)
    denominator = torch.einsum("btm,btm->bt", qf, prefix_normalizers).unsqueeze(-1)
    return numerator / denominator.clamp_min(eps)
```

**Ba quan sát trực tiếp từ code — nhìn shape là thấy bản chất fixed-state:**

1. `state.shape == (B, m, d_v)` — **không có $T$** — token 10 và token 1000 cùng shape.
2. `normalizer.shape == (B, m)` — vector, không phải ma trận theo sequence.
3. `outputs` được tạo bằng loop qua $T$ nhưng **state không phình** — mỗi iteration chỉ cộng outer product.

> [!note] Vì sao toy bỏ RoPE và multi-head?
> Để tập trung vào **state semantics** (trục $S$ có hay không). Full KDA thêm `short convolution` state, `channel-wise decay`, và `chunkwise` execution — nhưng không đổi việc core state có shape `(d_k, d_v)` cố định.

## 4. Xác minh trước khi benchmark — 4 tests phải pass

> [!warning] Lab này chỉ chứng minh semantics của toy fixed-state
> Full KDA còn `delta correction`, `learned decay`, `short convolution` và `chunkwise kernels`. Các test dưới không chứng minh parity với full KDA hay quality — chỉ chứng minh **recurrent == prefix, causality, và shape cố định**.

```python
import torch


@torch.inference_mode()
def test_recurrent_equals_prefix():
    """Test 1: recurrent loop và parallel prefix cho cùng kết quả (reassociation đúng)."""
    torch.manual_seed(0)
    q = torch.randn(2, 7, 4, dtype=torch.float64)  # (B=2, T=7, d_k=4) — float64 để tolerance chặt
    k = torch.randn(2, 7, 4, dtype=torch.float64)
    v = torch.randn(2, 7, 3, dtype=torch.float64)  # (B=2, T=7, d_v=3)

    y_rec = linear_attention_recurrent(q, k, v)           # loop
    y_ref = linear_attention_parallel_reference(q, k, v)   # cumsum

    # Hai cách tính cùng công thức phải khớp — rtol/atol chặt với float64
    torch.testing.assert_close(y_rec, y_ref, rtol=1e-10, atol=1e-10)
    assert y_rec.shape == (2, 7, 3), f"output shape {y_rec.shape} != (2, 7, 3)"
    print("✓ Test 1 passed: recurrent == prefix reference, shape (2, 7, 3)")


@torch.inference_mode()
def test_causality_future_does_not_affect_past():
    """Test 2: đổi future K/V không ảnh hưởng past outputs (causal isolation)."""
    torch.manual_seed(0)
    q = torch.randn(2, 7, 4, dtype=torch.float64)
    k = torch.randn(2, 7, 4, dtype=torch.float64)
    v = torch.randn(2, 7, 3, dtype=torch.float64)
    y_rec = linear_attention_recurrent(q, k, v)

    # Perturb mạnh 2 tokens cuối — past (5 tokens đầu) phải giữ nguyên
    k_changed = k.clone()
    v_changed = v.clone()
    k_changed[:, 5:] = torch.randn_like(k_changed[:, 5:]) * 100
    v_changed[:, 5:] = torch.randn_like(v_changed[:, 5:]) * 100

    y_changed = linear_attention_recurrent(q, k_changed, v_changed)
    # Chỉ so 5 positions đầu — future không leak ngược
    torch.testing.assert_close(y_rec[:, :5], y_changed[:, :5], rtol=1e-10, atol=1e-10)
    print("✓ Test 2 passed: future perturbation does not affect the past (causal)")


@torch.inference_mode()
def test_state_shape_independent_of_T():
    """Test 3: persistent state shape không chứa T — fixed-state."""
    torch.manual_seed(1)
    q_short = torch.randn(2, 10, 4, dtype=torch.float64)  # T=10
    k_short = torch.randn(2, 10, 4, dtype=torch.float64)
    v_short = torch.randn(2, 10, 3, dtype=torch.float64)

    q_long = torch.randn(2, 100, 4, dtype=torch.float64)  # T=100
    k_long = torch.randn(2, 100, 4, dtype=torch.float64)
    v_long = torch.randn(2, 100, 3, dtype=torch.float64)

    # State shape chỉ phụ thuộc (B, m, d_v) = (2, 4, 3) — không phụ thuộc T
    B, M, Dv = 2, 4, 3
    state_elements = B * M * Dv + B * M  # S_t (B,m,d_v) + z_t (B,m)
    # Với T=10 hay T=100, state_elements đều = 2*4*3 + 2*4 = 32
    assert state_elements == 32, f"state elements {state_elements} != 32"
    # Output shape thì có T — nhưng state thì không
    y_short = linear_attention_recurrent(q_short, k_short, v_short)
    y_long = linear_attention_recurrent(q_long, k_long, v_long)
    assert y_short.shape == (2, 10, 3)
    assert y_long.shape == (2, 100, 3)
    print(f"✓ Test 3 passed: state elements={state_elements} (fixed), "
          f"output shapes {y_short.shape} vs {y_long.shape} (T varies, state does not)")


@torch.inference_mode()
def test_shapes_and_normalization():
    """Test 4: shapes đúng và denominator không zero (numerical sanity)."""
    torch.manual_seed(2)
    B, T, Dk, Dv = 2, 5, 4, 3
    q = torch.randn(B, T, Dk, dtype=torch.float64)
    k = torch.randn(B, T, Dk, dtype=torch.float64)
    v = torch.randn(B, T, Dv, dtype=torch.float64)

    y = linear_attention_recurrent(q, k, v)
    assert y.shape == (B, T, Dv), f"output shape {y.shape} != {(B, T, Dv)}"
    # Output không NaN/Inf — denominator clamp hoạt động
    assert torch.isfinite(y).all(), "output contains NaN/Inf — check eps clamping"
    # Với φ dương (ELU+1), output là convex-ish combination của values — không explode
    assert y.abs().max().item() < 1e4, f"output exploded: max {y.abs().max().item()}"
    print(f"✓ Test 4 passed: output shape {y.shape}, finite, no explosion (max {y.abs().max().item():.2f})")


# Chạy tất cả — copy block này vào python và chạy
test_recurrent_equals_prefix()
test_causality_future_does_not_affect_past()
test_state_shape_independent_of_T()
test_shapes_and_normalization()
```

**Cách đọc khi test fail:**

| Test fail | Triệu chứng | Check đầu tiên |
|---|---|---|
| Test 1 | `recurrent != prefix` | In `state` sau từng step vs `prefix_states[:,t]` — write/read order sai? `eps` khác nhau? |
| Test 2 | past đổi khi future đổi | Đang dùng `parallel_reference` không causal? Loop có vô tình đọc future `kf`? |
| Test 3 | state_elements sai | Nhầm `m` với `d_k`? DPFP mở rộng $m$ nhưng toy giữ $m=d_k$ |
| Test 4 | NaN/Inf | `denominator` tiến về 0 — `φ` có âm? `eps` quá nhỏ? Dùng `ELU+1` để đảm bảo dương |

Cả 4 tests phải pass trước khi đo benchmark — benchmark trên implementation sai là vô nghĩa.

**Lab nhỏ bổ sung — nhìn thấy interference trực tiếp (không cần feature map):**

```python
import torch

def write(state, key, value):
    """state: (m, d_v), key: (m,), value: (d_v,) → (m, d_v)"""
    return state + torch.outer(key, value)  # (m,1)×(1,d_v)→(m,d_v)

def read(state, query):
    """state: (m, d_v), query: (m,) → (d_v,)"""
    return query @ state  # (1,m)×(m,d_v)→(d_v,)

# Hai orthogonal addresses — retrieval tách biệt
e1 = torch.tensor([1.0, 0.0])  # (2,)
e2 = torch.tensor([0.0, 1.0])  # (2,)
v_a = torch.tensor([10.0, 0.0])  # (2,)
v_b = torch.tensor([0.0, 20.0])

S = torch.zeros(2, 2)  # (m=2, d_v=2)
S = write(S, e1, v_a)  # ghi A
S = write(S, e2, v_b)  # ghi B
print(read(S, e1))  # tensor([10., 0.]) — chỉ v_a, không nhiễm

# Non-orthogonal gây crosstalk
k_c = torch.tensor([0.8, 0.6])  # unit vector, overlap với e1 — dot(e1,k_c)=0.8
v_c = torch.tensor([0.0, 30.0])
S2 = write(S, k_c, v_c)
print(read(S2, e1))  # tensor([10., 24.]): v_c rò 0.8*30=24 vào read(e1)

# Cùng address — additive mixture, không "latest wins"
S3 = torch.zeros(2, 2)
S3 = write(S3, e1, torch.tensor([1.0, 0.0]))
S3 = write(S3, e1, torch.tensor([0.0, 1.0]))
print(read(S3, e1))  # tensor([1., 1.]): cộng dồn, không ghi đè
```

Thử: thay $k_c$ gần trực giao hơn và đo crosstalk; tăng số random keys với $m=2,8,32$; so với `delta update` $S+\beta k(v-\bar v)^{\top}$.

## 5. Benchmark / Trade-offs — đo đúng thứ, đọc đúng slope

### 5.1 Tách prefill và decode — hai phase bottleneck khác nhau

| Phase | Work chính | Softmax + KV cache | Linear fixed-state |
|---|---|---|---|
| **Prefill** ($S$ tokens) | tạo outputs cho $S$ positions | $O(S^2 d_h)$ scores — toàn bộ $S\times S$ | chunkwise parallel — $O(S)$ state updates, mỗi chunk update `(m, d_v)` |
| **Decode** (1 token) | 1 query với history | $O(S)$ reads + $O(S)$ scores — **tăng với $S$** | $O(m d_v)$ — **hằng số** — đọc state cố định |

> Đo riêng: `prefill latency` (ms cho $S$ tokens) và `decode latency` (ms/token khi $S$ đã lớn). Đừng suy latency từ bytes. Training/prefill của linear attention cần chunkwise algorithms để song song — recurrent loop từng token sẽ chậm.[^kimi-linear-2025]

### 5.2 Raw bytes — nhìn slope thay vì một con số

```python
def softmax_cache_bytes(B, L, S, H, d_h, bytes_per_element=2):
    """MHA KV cache: B·L·S·2·H·d_h·p — CÓ S"""
    return B * L * S * (2 * H * d_h) * bytes_per_element

def mla_cache_bytes(B, L, S, d_c, d_rope, bytes_per_element=2):
    """MLA cache: B·L·S·(d_c+d_rope)·p — CÓ S, nhưng slope nhỏ hơn"""
    return B * L * S * (d_c + d_rope) * bytes_per_element

def fixed_state_bytes(B, L, H, m, d_v, bytes_per_element=2):
    """Fixed-state: B·L·H·m·d_v·p + B·L·H·m·p — KHÔNG có S!"""
    return B * L * H * (m * d_v + m) * bytes_per_element

for S in (128, 1_024, 8_192, 32_768):
    mha = softmax_cache_bytes(1, 32, S, 32, 128)
    mla = mla_cache_bytes(1, 32, S, 512, 64)
    fixed = fixed_state_bytes(1, 32, 4, 128, 128)
    print(f"S={S:6d} | MHA={mha/2**20:8.1f} MiB | MLA={mla/2**20:8.1f} MiB | fixed={fixed/2**20:6.1f} MiB")
# Output kỳ vọng (B=1, L=32):
# S=   128 | MHA=    64.0 MiB | MLA=     4.5 MiB | fixed=   4.0 MiB
# S=  1024 | MHA=   512.0 MiB | MLA=    36.0 MiB | fixed=   4.0 MiB
# S=  8192 | MHA=  4096.0 MiB | MLA=   288.0 MiB | fixed=   4.0 MiB
# S= 32768 | MHA= 16384.0 MiB | MLA=  1152.0 MiB | fixed=   4.0 MiB
```

Kết quả cần đọc theo **shape trend**:
- MHA tăng tuyến tính slope lớn — đường dốc đứng (có $S$).
- MLA tăng tuyến tính slope nhỏ hơn (~14× trong ví dụ) — đường thoải hơn nhưng vẫn đi lên (có $S$).
- Fixed-state nằm ngang theo $S$ — đường phẳng (không $S$). Nhưng **toàn model hybrid vẫn tăng** vì MLA layers còn cache.[^kimi-linear-2025]

> [!warning] Đừng suy latency từ bytes
> `Projection absorption`, kernels, `memory bandwidth`, batching và hardware có thể thay đổi throughput. Công thức trên chỉ là `retained tensors`. Hãy benchmark trên target implementation, dtype (BF16/FP8) và hardware nếu cần quyết định deployment.

### 5.3 Khi nào chọn gì? — bảng quyết định

| Mục tiêu | Ưu tiên | Lựa chọn | Vì sao |
|---|---|---|---|
| Retrieval chính xác trên context dài (needle-in-haystack, exact copy) | Token-addressability — mỗi token một slot | Softmax / MLA | Query tạo weight riêng cho từng position — shape `(B,H,1,S)` |
| Context cực dài + memory cố định (streaming vô hạn) | Bounded state — memory không tăng | Fixed-state (KDA, Mamba-2, DeltaNet) | State `(m, d_v)` cố định |
| Cân bằng cả hai | Giảm slope nhưng giữ retrieval | **Hybrid 3×KDA + 1×MLA**[^kimi-linear-2025] | 75% layers fixed-state (giảm cache), 25% MLA (giữ token-addressability) |

## 6. Debug checklist — triệu chứng → nguyên nhân → check

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên (in shape ra) |
|---|---|---|
| `recurrent != prefix` | Write/read order khác nhau (inclusive vs strict-past); `eps` khác nhau | So `state` sau từng step vs `prefix_states[:,t]`; in `eps` |
| Future leakage (Test 2 fail) | Loop vô tình đọc `kf` tương lai; dùng parallel không causal | Kiểm tra loop chỉ dùng `kf[:,t]` hiện tại; `cumsum` đã causal chưa? |
| State shape chứa $T$ | Đang lưu `writes` `(B,T,m,d_v)` thay vì `state` `(B,m,d_v)` | `print(state.shape)` — phải là `(B,m,d_v)` không có $T$ |
| NaN/Inf output | `denominator` → 0 do `φ` âm hoặc `z_t` chưa đủ lớn ở $t$ nhỏ | `print(denominator[:3])`; đảm bảo `φ` dương (ELU+1) và `eps>0` |
| Output explode | `φ` quá lớn, `v` chưa normalize | `print(qf.abs().max(), kf.abs().max(), v.abs().max())` |
| Throughput không tăng dù state nhỏ | Bottleneck là compute/bandwidth, không phải capacity | Profile riêng prefill vs decode; đo `memory bandwidth` |
| Nhầm "infinite context" | Hiểu state bounded = nhớ vô hạn | Test retrieval accuracy theo $S$ — phải giảm khi $S\gg m$ |

## 7. Giới hạn & bước tiếp theo

**Lab này không chứng minh:**
- Quality parity giữa linear và softmax — cần ablation trên cùng data và task. Kimi Linear báo cáo hybrid 3:1 tốt hơn full MLA trên đa số benchmarks ở config của họ, nhưng đó là author-run, config-specific.[^kimi-linear-2025]
- Speedup thực tế — phụ thuộc kernel, dtype, hardware. Toy `for` loop là teaching, không phải serving (`chunkwise`/`fused_recurrent` kernels).[^kimi-linear-2025]
- Fixed-state có luôn kém retrieval — hybrid có thể bù đắp, nhưng trade-off phụ thuộc workload và tỷ lệ hybrid.[^kimi-k3-2026]
- Mọi `feature map` đều tốt như nhau — DPFP tăng capacity bound nhưng cũng tăng state/compute.[^fast-weight-programmers-2021]

**Những hiểu lầm thường gặp (đọc kỹ trước khi tin headline):**

1. "Linear attention là FlashAttention." — Sai. FlashAttention là exact softmax với IO-aware evaluation; linear attention đổi kernel để reassociate.
2. "Fixed-state nghĩa là nhớ vô hạn." — Sai. Shape không tăng nhưng information phải share finite state.
3. "Context window vô hạn nghĩa là exact retrieval vô hạn." — Sai. Retrieval quality vẫn giảm do interference/decay/distribution shift.
4. "Decode softmax luôn $O(T^2)$ mỗi token." — Sai. Với KV cache, một decode query chỉ chấm $T$ entries; $O(T^2)$ là full prefill/training.
5. "Normalization xóa interference." — Sai. Nó kiểm soát scale; overlapping addresses vẫn mix values.
6. "State constant nên toàn model constant memory." — Sai. Weights, activations, MLA caches ở hybrid layers vẫn tăng.
7. "Tăng feature width luôn tốt." — Không chắc. Capacity có thể tăng nhưng FLOPs/bandwidth/optimization khó hơn.

**Checklist khi đọc một linear-attention paper — trả lời trước khi tin headline:**

1. Persistent state shape nào? Có trục $S$ không?
2. Write rule là additive, delta, decay, gate hay combination?
3. Read rule có normalization state không? $\varepsilon$ bao nhiêu?
4. Feature map/kernel là gì? Exact hay approximation cho kernel nào?
5. Training/prefill dùng recurrent, parallel hay chunkwise?
6. Decode có thêm short-convolution state hoặc cache khác không?
7. Model pure linear hay hybrid với local/global attention? Tỷ lệ?
8. Benchmark đo perplexity, recall, exact copy hay end-task?
9. Efficiency number là batch-one latency, throughput hay theoretical FLOPs?
10. Evidence là author-run hay independently replicated?

**Học tiếp theo (theo roadmap):**

1. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — cách delta correction và decay cải thiện fixed-state.
2. [Deterministic parameter-free projection for linear attention](deterministic-parameter-free-projection-for-linear-attention.md) — tăng $m$ để tăng capacity bound.
3. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — vì sao periodic MLA bù retrieval limits.[^kimi-linear-2025]
4. [Multi-head Latent Attention](multi-head-latent-attention.md) và [MLA và token-addressable memory — bài học cho người mới](mla-token-addressable-memory-beginners-guide.md) — nén per-token nhưng giữ token-addressability.
5. [Structured State Space Duality](structured-state-space-duality.md) — linear attention như trường hợp riêng của semiseparable mask.[^dao-gu-2024]

**Bài tập đề xuất (làm theo thứ tự):**
1. Tự suy ra $S_t, z_t$ từ $\kappa(q,k)=\phi(q)^{\top}\phi(k)$ mà không nhìn công thức — viết shape từng bước.
2. Sửa code thành read-before-write và viết test position 0 trả zero (strict-past).
3. Với random unit keys/values, plot retrieval error theo số writes cho $m\in\{8,32,128\}$ — quan sát capacity.
4. Implement delta update $\beta=1$ và test repeated-key case — so với additive mixture.
5. So sánh element count MHA cache vs state $m\times d_v+m$ tại $S=128,8192,32768$.
6. Thay một attention head trong toy causal model bằng implementation trên; so sánh loss/speed/memory (đừng tuyên bố quality từ một run).

## Relationships

- **Depends on:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) — softmax attention là baseline để so sánh kernel và state scaling.
- **Depends on:** [KV caching](kv-caching.md) — hiểu vì sao cache tăng $O(S)$ trước khi học cách xóa trục $S$.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) — nén per-token nhưng vẫn sequence-growing, khác với fixed-state.
- **Elaborates:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — course này mở rộng concept thành derivation chi tiết và lab.
- **Improved by:** [Deterministic parameter-free projection for linear attention](deterministic-parameter-free-projection-for-linear-attention.md) — mở rộng $m$ để tăng capacity bound với chi phí state lớn hơn.
- **Improved by:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — delta correction và learned decay quản lý overwrite/forgetting.
- **Used by:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) và [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — KDA + periodic global MLA.[^kimi-linear-2025][^kimi-k3-2026]
- **Generalized by:** [Structured State Space Duality](structured-state-space-duality.md) — linear attention là trường hợp riêng của semiseparable mask.[^dao-gu-2024]
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) — fixed-state memory trong learning path.

## Evidence limits

Write/read equivalence, fast-weight interpretation và capacity analysis ($m$ orthogonal associations) được document trong primary paper 2021; KDA fixed matrix state, recurrent/chunkwise split và hybrid retrieval motivation được document trong Kimi Linear và Kimi K3 reports. Các so sánh quality, latency ($2.9\times$ prefill, $2.2\times$ decode) và throughput là author-run, architecture- và config-specific, không independently replicated ở đây. PyTorch labs, worked examples, complexity table và teaching sequence là **pedagogical synthesis** — toy code không implement `delta`, `decay`, `short convolution`, hay `chunkwise` kernels và không dùng để suy ra quality hay speedup. Fixed state bảo đảm bounded state dimensions, không bảo đảm lossless memory, constant end-to-end latency, infinite usable context hay quality parity với exact softmax attention.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, "Linear Transformers Are Secretly Fast Weight Programmers," ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), especially Sections 3–4 and Appendices A–B.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), "22580: From GPT2 to Kimi3, Explained," 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md). This is secondary explanatory evidence; primary-paper claims take precedence.

[^kimi-linear-2025]: Kimi Team, "Kimi Linear: An Expressive, Efficient Attention Architecture," arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 1–3, 5–6 and appendices.

[^kimi-k3-2026]: Kimi Team, "Kimi K3: Open Frontier Intelligence," arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.1 and 5.

[^dao-gu-2024]: Tri Dao and Albert Gu, "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality," arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 4–6.
