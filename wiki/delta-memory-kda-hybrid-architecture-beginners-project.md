---
type: Synthesis
title: "Delta memory, KDA, và hybrid KDA–MLA — mini-project cho người mới"
description: A beginner-first course and PyTorch mini-project on delta correction, scalar and channel-wise decay, KDA, fixed-state retrieval limits, and why hybrid architectures periodically insert global MLA layers.
tags: [delta-rule, kda, associative-memory, fixed-state, hybrid-attention, mla, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-23T20:00:00+07:00
sources:
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
  - id: gated-deltanet-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
---

# Delta memory, KDA, và hybrid KDA–MLA — mini-project cho người mới

`Delta memory` (bộ nhớ hiệu chỉnh theo sai số) giải quyết lỗi cốt lõi của `additive associative memory` (bộ nhớ cộng dồn): khi cùng một `key` (khóa) xuất hiện với `value` (giá trị) mới, memory cần **sửa association cũ** thay vì cộng dồn hai values. `Decay` (hệ số quên) bổ sung khả năng quên rộng hơn; `Kimi Delta Attention` (KDA) kết hợp `delta correction` với `channel-wise decay` (quên theo từng kênh) để điều khiển `retention` (lưu giữ) chi tiết hơn. Tuy nhiên, mọi associations vẫn chia sẻ một `fixed-size matrix state` (trạng thái ma trận kích thước cố định), nên `interference` (nhiễu chéo) và giới hạn `precise retrieval` (truy xuất chính xác) không biến mất. `Kimi Linear` vì thế dùng pattern theo chiều sâu `3 KDA layers → 1 global MLA layer`: phần lớn layers có `bounded recurrent state` (trạng thái truy hồi bị chặn), còn `periodic MLA` (MLA định kỳ) khôi phục `token-level retrieval` (truy xuất mức token) tại một số layers.[^fast-weight-programmers-2021][^gated-deltanet-2025][^kimi-linear-2025]

> [!success] Sau bài này, bạn có thể
> 1. Giải thích vì sao `additive write` không có semantics `overwrite` (ghi đè).
> 2. Tự suy ra `delta correction` từ `retrieval error` (sai số truy xuất).
> 3. Phân biệt vai trò của $\beta_t$ (`write strength`) và `decay gate` $\alpha_t$ (`forget gate`).
> 4. Đọc `recurrence` (công thức truy hồi) của `DeltaNet`, `Gated DeltaNet` và `KDA` và chỉ ra shape từng tensor.
> 5. Giải thích vì sao `fixed state` vẫn gặp `interference` và `retrieval bottleneck`.
> 6. Phân biệt `periodic` **theo layer depth** (độ sâu mạng) với periodic theo `token/time`.
> 7. Chạy `mini-project` so sánh `token-level KV storage` với `fixed associative state` trên `exact recall`, `overwrite` và `capacity stress` và đọc đúng kết quả.

## 1. Trước khi đọc — Prerequisites

**Bạn cần biết ở mức trực giác (nếu chưa, đọc trước):**

1. [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) — vì sao `KV cache` tăng theo $S$ và `decode` đọc $S$ entries.
2. [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) — `MLA` nén mỗi token nhưng vẫn giữ `slot` riêng cho từng token.
3. [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — `linear attention` gom history vào một matrix state cố định, không có trục $S$.

**Toán tối thiểu — đọc một lần, dùng cả bài:**

| Khái niệm | Shape ví dụ | Ý nghĩa |
|---|---|---|
| Vector `(d,)` | `(128,)` | danh sách $d$ số |
| Ma trận `(a, b)` | `(64, 128)` | bảng $a$ hàng, $b$ cột |
| Outer product $u v^{\top}$ | `(a,1) \times (1,b) \to (a,b)` | ghép vector cột và vector hàng thành ma trận |
| Dot product $q^{\top}k$ | `(128,)·(128,) \to` scalar | một số đo độ hợp |
| `Diag(alpha)` | `(d_k, d_k)` | ma trận chéo — nhân `alpha[i]` vào hàng $i$ |

**Ký hiệu thống nhất trong bài:**

| Ký hiệu | Shape ở một `head` | Ý nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| $B$ | scalar | `batch size` | số sequences song song |
| $T$ | scalar | `sequence length` | $S$ trong cache accounting |
| $d_k$ | scalar | chiều `key/query` | ví dụ 128 |
| $d_v$ | scalar | chiều `value` | ví dụ 128 |
| $S_t$ | $(d_k, d_v)$ | `associative matrix state` | **không có trục $T$** |
| $k_t$ | $(d_k,)$ | `key` đã mapped | sau $\phi$ nếu có |
| $v_t$ | $(d_v,)$ | `value` cần lưu | |
| $q_t$ | $(d_k,)$ | `query` để đọc | |
| $\beta_t$ | scalar $\in[0,1]$ | `write strength` | học từ input |
| $\alpha_t$ | scalar hoặc $(d_k,)$ | `decay gate` | scalar = global, vector = channel-wise |
| $c_t^{KV}$ | $(d_c,)$ | `MLA latent` | chỉ ở MLA layers |

> [!tip] Cách đọc mọi công thức trong bài
> Mỗi công thức sẽ mổ thành 4 dòng: **Ký hiệu là gì → Shape là gì → Phép toán làm gì → Kết quả shape ra sao**. Hãy theo dõi shape chảy — đó là cách nhanh nhất để không lạc.

**Bài này không cover:** `CUDA kernel`, `distributed training`, `MoE routing`, `quantization`. Code dùng `torch.einsum` và `for` loop để dễ đọc — không phải `serving kernel`. `position_ids` là **absolute** (0,1,2,...) khi nhắc tới vị trí — không dùng `relative offset` trong toy này. Nếu có `RoPE`, convention sẽ là `interleaved` (xoay cặp `(0,1),(2,3),...`) — ghi chú để không nhầm khi đọc production.

## 2. Bài toán cần giải — overwrite là gì?

Ta xét stream các `key–value pairs` (cặp khóa-giá trị) như một database tối giản:

```text
WRITE(user_17, plan_free)      # ghi lần 1
QUERY(user_17)                 -> plan_free   # phải trả đúng
WRITE(user_17, plan_pro)       # ghi đè — cùng key, value mới
QUERY(user_17)                 -> plan_pro    # phải trả value MỚI
```

Một memory hữu ích phải trả lời hai loại yêu cầu:

- **Exact recall:** key đã lưu phải trả đúng value.
- **Overwrite:** khi key cũ được gán value mới, query sau đó phải trả value mới chứ không phải tổng hay trung bình của hai values.

Đây là **toy abstraction** (trừu tượng đồ chơi). Trong LLM thật, `keys`, `values`, `gates` và `queries` được học từ `hidden states`; model không nhận sẵn `integer key` hay thao tác database rõ ràng. Toy giúp tách **storage semantics** (ngữ nghĩa lưu trữ) khỏi `learned retrieval policy` (chính sách truy xuất được học).

> [!example] Vì sao bài toán này quan trọng cho long-context?
> Trong hội thoại dài, cùng một `entity` có thể đổi trạng thái nhiều lần. Model cần nhớ **giá trị mới nhất**, không phải cộng dồn lịch sử. Nếu memory chỉ biết cộng, nó sẽ trả mixture sai.

## 3. Hai cách lưu history — nhìn vào shape là thấy khác

### 3.1 Token-level KV cache: giữ từng slot riêng

`Token-addressable attention` giữ một `K/V entry` cho mỗi token:

$$
K_{1:T}=[k_1,\ldots,k_T],\qquad
V_{1:T}=[v_1,\ldots,v_T]
$$

Giải từng ký hiệu:

| Ký hiệu | Shape ở một head, một layer | Ý nghĩa |
|---|---|---|
| $k_j$ | $(d_k,)$ | key của token $j$ |
| $v_j$ | $(d_v,)$ | value của token $j$ |
| $K_{1:T}$ | $(T, d_k)$ | xếp $T$ keys dọc theo trục $T$ |
| $V_{1:T}$ | $(T, d_v)$ | xếp $T$ values dọc theo trục $T$ |

Query $q$ tạo score riêng cho từng retained key:

$$
a_i=\operatorname{softmax}_i(q^{\top}k_i),\qquad
o=\sum_i a_i v_i
$$

| Mảnh | Shape | Ý nghĩa |
|---|---|---|
| $q^{\top}k_i$ | scalar | độ hợp giữa query và key $i$ |
| $\operatorname{softmax}_i$ | scalar, $\sum_i a_i=1$ | chuẩn hóa thành weights |
| $a_i v_i$ | $(d_v,)$ | value được cân |
| $\sum_i$ | $(d_v,)$ | output |

Ưu điểm: association ở token $i$ không bị bắt buộc cộng vào cùng `matrix slot` với token $j$. Hệ thống còn giữ `sequence axis` (trục chuỗi) để model chọn từng `candidate token`.

Cái giá là `persistent cache` tăng theo context:

$$
M_{KV}=O(T(d_k+d_v))\quad\text{— có }T
$$

Với $B$ sequences và $L$ layers: $M_{KV}=B\cdot L\cdot T\cdot(2Hd_h)\cdot p$ bytes ($p$ = bytes/số). `Token-addressable` không đồng nghĩa model luôn recall đúng — `softmax` có thể chọn sai, `duplicate keys` có thể tạo mixture, và `positional/recency` phải được học hoặc mã hóa. Nó chỉ nói rằng các `token slots` vẫn còn riêng biệt để `retrieval mechanism` chấm điểm.

### 3.2 Fixed-state associative memory: gộp history vào một ma trận

Một `additive memory` tối giản có `matrix state`:

$$
S_t = S_{t-1} + k_t v_t^{\top},\qquad S_t\in\mathbb{R}^{d_k\times d_v}
$$

Mổ công thức thành shape — **đây là dòng quan trọng nhất của fixed-state**:

| Ký hiệu | Shape | Phép toán | Kết quả |
|---|---|---|---|
| $k_t$ | $(d_k,)$ | vector cột $(d_k,1)$ | — |
| $v_t^{\top}$ | $(1,d_v)$ | vector hàng | — |
| $k_t v_t^{\top}$ | $(d_k, d_v)$ | **outer product** — mỗi phần tử $(i,j)=k_t[i]\cdot v_t[j]$ | ma trận ghi association |
| $S_{t-1}$ | $(d_k, d_v)$ | cộng ma trận | — |
| $S_t$ | $(d_k, d_v)$ | $S_{t-1}+$ outer product | **cùng shape với $S_{t-1}$** |

Query đọc:

$$
\hat v_t = S_t^{\top} q_t
$$

| Mảnh | Shape | Ý nghĩa |
|---|---|---|
| $S_t^{\top}$ | $(d_v, d_k)$ | chuyển vị của state |
| $q_t$ | $(d_k,)$ | query |
| $S_t^{\top} q_t$ | $(d_v,d_k)\times(d_k,)\to(d_v,)$ | đọc state bằng query |

Hoặc viết $q_t^{\top}S_t$ tùy convention hàng/cột — ý nghĩa như nhau: **query chấm với state**.

State size là:

$$
M_{fixed}=O(d_k d_v)\quad\text{— không chứa }T
$$

Nhưng tất cả writes cùng nằm trong $S_t$. Nếu keys không trực giao, retrieval chứa `crosstalk` (nhiễu chéo); nếu nhiều `logical keys` dùng cùng hoặc gần cùng `address`, chúng không còn slot độc lập.[^fast-weight-programmers-2021]

**Hình dung để nhớ:**

```text
Token-level = tủ hồ sơ: mỗi token = 1 ngăn riêng, mỗi ngăn DÀY
              Shape cache: (B, S, d_c) — có trục S, mỗi token một hàng

Fixed-state = bảng trắng: mọi token ghi đè lên nhau trên 1 mặt phẳng
              Shape state: (B, H, d_k, d_v) — KHÔNG có trục S
              Token 10 và token 1_000_000 cùng shape
```

> [!important] Quy tắc đọc mọi paper về long-context
> Thấy "giảm KV cache 75%" → hỏi ngay: **công thức còn thừa số $T$ không?** Nếu còn, đó là **giảm slope (độ dốc)**, không phải xóa slope. `MLA` làm ngăn tủ mỏng hơn; `fixed-state` thay tủ bằng bảng trắng — shape không còn trục $S$.

## 4. Vì sao additive memory thất bại khi overwrite? — ví dụ số

Giả sử một `unit key` $k$ (chuẩn hóa $\|k\|=1$, $k^{\top}k=1$) được ghi lần lượt với $v_{old}$ và $v_{new}$:

$$
S = k v_{old}^{\top} + k v_{new}^{\top}
$$

Đọc bằng cùng key:

$$
S^{\top}k = (v_{old}k^{\top}+v_{new}k^{\top})k = (k^{\top}k)(v_{old}+v_{new}) = v_{old}+v_{new}
$$

Mổ từng bước:

| Bước | Shape | Kết quả |
|---|---|---|
| $k v_{old}^{\top}$ | $(d_k,d_v)$ | outer product thứ 1 |
| $k v_{new}^{\top}$ | $(d_k,d_v)$ | outer product thứ 2 |
| $S = $ tổng | $(d_k,d_v)$ | cộng hai ma trận |
| $S^{\top}k$ | $(d_v,d_k)\times(d_k,)\to(d_v,)$ | $(k^{\top}k)=1$ nên ra $v_{old}+v_{new}$ |

Memory không biết write thứ hai mang nghĩa thay thế, thêm evidence, hay collision. `Normalization` có thể biến tổng thành `mixture/average`, nhưng vẫn không tự tạo `latest value wins`.

**Ví dụ số cụ thể ($d_k=2, d_v=2$):**

```
k = [1, 0]ᵀ,  v_old = [10, 0], v_new = [0, 30]
S = [[10, 0],[0,0]] + [[0,30],[0,0]] = [[10,30],[0,0]]
Sᵀk = [10, 30]  ← tổng, không phải [0,30]!
```

> [!example] Intuition (trực giác)
> `Additive write` giống viết tiếp mực lên cùng tờ giấy trong suốt — hai nét chồng lên nhau thành hỗn hợp. `Delta write` trước tiên nhìn xem trên giấy đang có gì, rồi chỉ thêm phần **sai lệch** để hình hiện tại tiến về mục tiêu mới.

## 5. Delta correction: đọc trước, sửa error sau — suy ra từng dòng

### 5.1 Ý tưởng: chỉ ghi phần sai

Gọi prediction hiện tại của memory tại key $k_t$ là:

$$
\bar v_t = S_{t-1}^{\top} k_t \qquad\text{shape: }(d_k,d_v)^{\top}\times(d_k,)\to(d_v,)
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $S_{t-1}$ | $(d_k,d_v)$ | state trước khi ghi token $t$ |
| $k_t$ | $(d_k,)$ | key của token $t$ |
| $\bar v_t$ | $(d_v,)$ | value mà state **hiện tại** sẽ trả về nếu query bằng $k_t$ — "dự đoán" |

`Retrieval error` (sai số truy xuất) là:

$$
e_t = v_t - \bar v_t \qquad\text{shape: }(d_v,)=(d_v,)-(d_v,)
$$

Thay vì ghi toàn bộ $v_t$, `delta rule` chỉ ghi error:

$$
\boxed{S_t = S_{t-1} + \beta_t\, k_t\, e_t^{\top}}
$$

hay viết đầy đủ:

$$
\boxed{S_t = S_{t-1} + \beta_t\, k_t\,(v_t - S_{t-1}^{\top}k_t)^{\top}}
$$

Mổ từng mảnh:

| Mảnh | Shape | Ý nghĩa |
|---|---|---|
| $S_{t-1}^{\top}k_t$ | $(d_v,)$ | đọc prediction cũ |
| $v_t - \bar v_t$ | $(d_v,)$ | error — phần chưa đúng |
| $k_t e_t^{\top}$ | $(d_k,1)\times(1,d_v)\to(d_k,d_v)$ | outer product của key với error |
| $\beta_t$ | scalar $\in[0,1]$ | `learning rate` / `gate` — điều khiển strength |
| $S_t$ | $(d_k,d_v)$ | state mới — **cùng shape** |

### 5.2 Chứng minh overwrite đúng với key chuẩn hóa

Với $\|k_t\|_2=1$ ($k_t^{\top}k_t=1$) và $\beta_t=1$:

$$
\begin{aligned}
S_t^{\top}k_t &= \big(S_{t-1}+k_t(v_t-S_{t-1}^{\top}k_t)^{\top}\big)^{\top}k_t \\
&= S_{t-1}^{\top}k_t + (v_t-S_{t-1}^{\top}k_t)(k_t^{\top}k_t) \\
&= S_{t-1}^{\top}k_t + v_t - S_{t-1}^{\top}k_t \\
&= v_t
\end{aligned}
$$

Từng dòng shape:

| Dòng | Shape | Giải thích |
|---|---|---|
| $S_{t-1}^{\top}k_t$ | $(d_v,)$ | prediction cũ |
| $k_t^{\top}k_t$ | scalar = 1 | vì key chuẩn hóa |
| $S_t^{\top}k_t$ | $(d_v,)$ | **chính xác bằng $v_t$ mới** |

Association được address bởi $k_t$ trở thành value mới chỉ sau một update. Nếu một key $u$ trực giao với $k_t$ ($u^{\top}k_t=0$), update không thay đổi read tại $u$ — vì $u^{\top}k_t=0$ nên hạng $u^{\top}k_t e_t^{\top}=0$.

### 5.3 Dạng ma trận thường thấy trong DeltaNet

$$
\boxed{S_t = (I - \beta_t k_t k_t^{\top})\,S_{t-1} + \beta_t k_t v_t^{\top}}
$$

Mổ từng hạng:

| Hạng | Shape | Ý nghĩa |
|---|---|---|
| $k_t k_t^{\top}$ | $(d_k,1)\times(1,d_k)\to(d_k,d_k)$ | ma trận chiếu lên direction $k_t$ |
| $I - \beta_t k_t k_t^{\top}$ | $(d_k,d_k)$ | **xóa một phần** association cũ theo direction $k_t$ |
| $(I-\beta_t k_t k_t^{\top})S_{t-1}$ | $(d_k,d_k)\times(d_k,d_v)\to(d_k,d_v)$ | state cũ sau khi xóa |
| $\beta_t k_t v_t^{\top}$ | $(d_k,d_v)$ | ghi association mới |

Đây cũng có thể được diễn giải là một `online gradient step` trên `reconstruction loss` $\tfrac12\|S^{\top}k_t-v_t\|^2$ — đạo hàm theo $S$ cho ra chính delta update.[^parallel-deltanet-2024][^kimi-linear-2025]

### 5.4 Vai trò của $\beta_t$ — bảng quyết định

| Giá trị $\beta_t$ | Tác dụng | Khi nào dùng |
|---|---|---|
| $0$ | không sửa memory | token không cần ghi |
| $0<\beta_t<1$ | cập nhật một phần, smooth | write có thể nhiễu, cần làm mượt |
| $1$ | full correction theo addressed direction (nếu key chuẩn hóa) | overwrite chính xác |

Trong model thật, $\beta_t$ thường được sinh từ input qua `learned projection` và `sigmoid` — ví dụ `beta_t = sigmoid(W_beta x_t)` — nó không phải hyperparameter luôn bằng 1. Với `batch` và `multi-head`, $\beta_t$ shape `(B, H)` hoặc `(B, H, 1)`.

## 6. Delta rule sửa được gì, chưa sửa được gì?

### 6.1 Sửa tốt trong trường hợp lý tưởng — keys trực giao

Nếu mapped keys là `orthonormal` (trực chuẩn):

$$
k_i^{\top}k_j=\begin{cases}1&i=j\\0&i\ne j\end{cases}
$$

thì delta update có thể overwrite association $i$ mà không chạm association $j$ — vì $k_j^{\top}k_i=0$ nên hạng $k_j^{\top}(k_i e_i^{\top})=0$.

**Ví dụ với $d_k=2$:**

```
k1=[1,0], k2=[0,1] — trực giao
S = k1·v1ᵀ + k2·v2ᵀ = [[v1ᵀ],[v2ᵀ]]
Đọc k1 → v1, đọc k2 → v2 — không nhiễm
Ghi đè k1 với v1_new bằng delta → chỉ hàng 1 đổi, hàng 2 giữ nguyên
```

### 6.2 Không loại bỏ finite-capacity interference

Nếu $k_A^{\top}k_B\ne0$ (keys chồng lấn), update cho $B$ làm read tại $A$ đổi theo:

$$
\Delta \hat v_A = \beta\,(k_A^{\top}k_B)\,(v_B-\hat v_B)
\qquad\text{shape: }(d_v,)=\text{scalar}\times\text{scalar}\times(d_v,)
$$

| Thừa số | Shape | Ý nghĩa |
|---|---|---|
| $k_A^{\top}k_B$ | scalar | độ overlap giữa hai keys — càng gần 1 càng nhiễm mạnh |
| $v_B-\hat v_B$ | $(d_v,)$ | error của $B$ |
| $\Delta \hat v_A$ | $(d_v,)$ | thay đổi ngoài ý muốn ở $A$ |

Overlap càng lớn, `collateral update` càng lớn. Trường hợp cực đoan $k_A=k_B$ có nghĩa hai `logical keys` dùng đúng một `address`; bất kỳ rule chỉ nhìn address đó đều không thể phân biệt chúng.

Vì vậy delta rule cho memory semantics tốt hơn additive write, nhưng **không biến fixed-size state thành database có vô hạn exact slots**.

## 7. Tại sao cần decay? — quên để có chỗ

Delta correction chỉ sửa `direction` được `current key` address. Nó không trực tiếp giải quyết mọi `state content` đã lỗi thời, nhiễu hoặc không còn hữu ích ở các directions khác.

### 7.1 Scalar decay — quên toàn bộ

Một `scalar decay` đơn giản tạo `intermediate state`:

$$
\widetilde S_{t-1} = \alpha_t\, S_{t-1},\qquad \alpha_t\in[0,1]
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $\alpha_t$ | scalar | hệ số quên chung — 1 = giữ hết, 0 = xóa hết |
| $S_{t-1}$ | $(d_k,d_v)$ | state cũ |
| $\widetilde S_{t-1}$ | $(d_k,d_v)$ | state sau khi co lại — mọi phần tử nhân cùng $\alpha_t$ |

Sau đó delta correction chạy trên state đã decay:

$$
S_t = (I-\beta_t k_t k_t^{\top})\,\widetilde S_{t-1} + \beta_t k_t v_t^{\top}
$$

### 7.2 So sánh ba cơ chế — bảng cốt lõi

| Control | Phạm vi tác dụng | Shape của gate | Vai trò chính |
|---|---|---|---|
| `Delta correction` | `key-addressed direction` — chỉ direction $k_t$ | scalar $\beta_t$ nhân outer product $(d_k,d_v)$ | sửa association được chọn |
| Scalar `decay` | toàn `state/head` | scalar $\alpha_t$ nhân toàn ma trận $(d_k,d_v)$ | quên rộng, giải phóng capacity |
| Channel-wise `decay` | từng `key channel` — từng hàng của state | vector $\alpha_t\in[0,1]^{d_k}$ | `retention horizon` chi tiết hơn |

`Decay` tạo trade-off không tránh được:

- decay yếu ($\alpha\approx1$): giữ lâu hơn nhưng nhiễu cũ tồn tại;
- decay mạnh ($\alpha\approx0$): dọn state nhanh hơn nhưng `exact retention` dài hạn suy giảm.

`Gated DeltaNet` kết hợp scalar `learned decay` với `delta rule`; paper cho thấy hai cơ chế bổ sung nhau trong recipe được đánh giá, nhưng kết quả vẫn phụ thuộc model, data và benchmark.[^gated-deltanet-2025]

> [!warning] Decay không miễn phí
> Quên giúp có chỗ cho thông tin mới, nhưng cũng xóa thông tin cũ. Không có cách nào vừa giữ vô hạn history trong finite state vừa không mất gì.

## 8. KDA: channel-wise decay + delta correction — mổ recurrence

`KDA` thay scalar decay bằng vector:

$$
\alpha_t\in[0,1]^{d_k}\qquad\text{shape: }(d_k,)
$$

Mỗi phần tử $\alpha_t[i]$ điều khiển retention của **hàng $i$** của state (ứng với `key channel` $i$).

State được decay theo từng hàng:

$$
\widetilde S_{t-1} = \operatorname{Diag}(\alpha_t)\,S_{t-1}
\qquad\text{shape: }(d_k,d_k)\times(d_k,d_v)\to(d_k,d_v)
$$

| Mảnh | Shape | Phép toán |
|---|---|---|
| $\operatorname{Diag}(\alpha_t)$ | $(d_k,d_k)$ | ma trận chéo — phần tử $(i,i)=\alpha_t[i]$ |
| $S_{t-1}$ | $(d_k,d_v)$ | state cũ |
| $\widetilde S_{t-1}[i,:]$ | $(d_v,)$ | hàng $i$ được nhân với $\alpha_t[i]$ — hàng khác giữ hệ số riêng |

Recurrence đầy đủ của KDA là:

$$
\boxed{S_t = (I-\beta_t k_t k_t^{\top})\,\operatorname{Diag}(\alpha_t)\,S_{t-1} + \beta_t k_t v_t^{\top}}
$$

Thứ tự quan trọng: **decay trước, rồi delta correction** — `prediction` cũng đọc từ state đã decay.

Một cách implement tương đương, dễ đọc:

```python
# state: (d_k, d_v), alpha: (d_k,), key: (d_k,), value: (d_v,), beta: scalar
decayed = alpha[:, None] * state          # (d_k,1) * (d_k,d_v) -> (d_k,d_v) — từng hàng nhân alpha[i]
prediction = key @ decayed                # (d_k,) @ (d_k,d_v) -> (d_v,) — đọc từ decayed
state = decayed + beta * torch.outer(key, value - prediction)  # (d_k,d_v) + scalar*(d_k,d_v)
```

Mổ từng dòng code:

| Dòng | Shape | Ý nghĩa |
|---|---|---|
| `alpha[:, None]` | $(d_k,1)$ | biến vector thành cột để broadcast |
| `alpha[:, None] * state` | $(d_k,d_v)$ | mỗi hàng $i$ nhân $\alpha[i]$ |
| `key @ decayed` | $(d_v,)$ | query bằng key hiện tại trên state đã decay |
| `value - prediction` | $(d_v,)$ | error |
| `torch.outer(key, error)` | $(d_k,d_v)$ | correction theo direction $k_t$ |

KDA có thể học để một số channels giữ information lâu ($\alpha\approx1$), trong khi channels khác quên nhanh ($\alpha\approx0$) theo input. `Kimi Linear` còn dùng `normalized Q/K`, `short convolution`, `output normalization` và `output gate`; recurrence trên chỉ là lõi memory, không phải toàn bộ KDA layer.[^kimi-linear-2025]

### Tại sao gọi là `fixed-state`?

Với một head, $S_t$ luôn có shape $d_k\times d_v$ — ví dụ $128\times128=16\text{K}$ số. Token thứ một triệu cập nhật cùng tensor shape như token thứ mười. During `autoregressive decode`, `recurrent update` không cần `append` một `K/V slot` mới cho KDA state.

Điều này **không** có nghĩa:

- state chứa vô hạn information;
- retrieval luôn exact;
- toàn model có memory constant;
- training/prefill nhất thiết chạy token-by-token.

KDA dùng `chunkwise formulation` để `parallelize` training/prefill và `recurrent update` khi decode; hybrid model vẫn có `sequence-growing cache` tại MLA layers.[^kimi-linear-2025]

```text
Decode step t — KDA (fixed-state):                    MLA (token-addressable):
  S_t shape (d_k, d_v) — không đổi                     Cache shape (B, S, d_c) — tăng 1 mỗi step
  ┌──────────────┐                                     ┌──────────────┐
  │ S_{t-1}      │ ──► decay + delta ──► S_t           │ c_1 ... c_S  │ ──► append c_{S+1}
  │ (128, 128)   │      (128,128)  (128,128)            │ (S, d_c)     │      (S+1, d_c)
  └──────────────┘                                     └──────────────┘
```

## 9. Vì sao periodic MLA vẫn cần thiết? — hybrid theo depth

`Kimi Linear` report xác định `long-context retrieval` là bottleneck chính của `pure linear attention` và chọn `layerwise hybrid`:[^kimi-linear-2025]

```text
Block 1: KDA              ─┐
Block 2: KDA               │  repeat across depth
Block 3: KDA               │  "3 KDA layers → 1 MLA layer"
Block 4: global NoPE MLA  ─┘  (pattern 3:1)
          ↓ repeat ...
```

> [!important] "Periodic" là theo layer depth — không phải theo token
> Pattern `3:1` **không** có nghĩa model dùng MLA sau mỗi ba tokens. **Mọi token** đi qua tất cả layers. MLA xuất hiện định kỳ khi đi **lên network depth**: ba `KDA token-mixing layers` rồi một `global MLA layer`. Nếu model có 32 layers, khoảng 8 layers là MLA, 24 là KDA.

### 9.1 Hai pathways bổ sung nhau

**KDA layers** cung cấp:

- `fixed-size recurrent matrix state` — shape $(d_k,d_v)$ không đổi;
- `per-step state update` không tăng theo prefix length;
- `delta overwrite` và `learned channel-wise forgetting`;
- `learned compression` của history thành `task-relevant state`.

**Global MLA layers** cung cấp:

- một `compressed latent entry` cho mỗi retained token — shape $(d_c,)$ mỗi token;
- `score/weight` riêng theo `token position` — `attention weights` shape $(B,H,1,S)$;
- `direct token-level retrieval` và `fine-grained selection`;
- đường truy cập phù hợp hơn với `exact copying` và `recall` từ history dài.

MLA giảm bytes trên mỗi token so với `standard MHA`, nhưng cache vẫn tăng theo $T$ — công thức $M_{MLA}=B\cdot L\cdot S\cdot(d_c+d_h^R)\cdot p$.

### 9.2 Tại sao không dùng toàn MLA?

Full MLA giữ `token-addressability` ở mọi attention layer nhưng phải trả `cache/read cost` tăng theo context ở mọi layer. Dùng KDA ở phần lớn layers giảm số layers cần giữ cache theo token. Với pattern 3:1, chỉ một phần tư `token-mixing layers` là MLA, dẫn tới claim "up to 75% KV-cache reduction" so với full MLA trong cấu hình report — đây là `layer-ratio accounting` và `author-reported system result`, không phải universal guarantee.[^kimi-linear-2025]

### 9.3 Tại sao không dùng toàn KDA?

`Fixed state` phải compress ngày càng nhiều history vào cùng số dimensions. Delta correction và decay quản lý state tốt hơn, nhưng không khôi phục `isolated token slots` sau khi associations interfere hoặc collide. Primary report nhấn mạnh `exact copying` và `fine-grained long-context retrieval` là điểm yếu còn lại của pure linear attention.[^kimi-linear-2025]

### 9.4 Tỷ lệ 3:1 không phải định luật

Trong ablation của Kimi Linear, 3:1 có `validation PPL` 5.65; 1:1 là 5.66; 7:1 là 5.70; 15:1 là 5.82; full MLA là 5.77. Kết quả 3:1 tốt nhất trong configurations và training recipe được test, nhưng không chứng minh đây là optimum cho mọi `scale`, `workload` hoặc `hardware`.[^kimi-linear-2025]

| Ratio KDA:MLA | MLA layers / 32 | PPL (thấp hơn tốt hơn) | Cache reduction (layer ratio) |
|---:|---:|---:|---|
| 0:1 (full MLA) | 32 | 5.77 | 0% |
| 1:1 | 16 | 5.66 | 50% |
| **3:1** | **8** | **5.65** | **75%** |
| 7:1 | 4 | 5.70 | 87.5% |
| 15:1 | 2 | 5.82 | 93.75% |

Đọc bảng: PPL tốt nhất ở 3:1 trong recipe này, nhưng 1:1 gần như tương đương, còn 15:1 tệ hơn cả full MLA — cho thấy **quá ít MLA làm mất retrieval capacity**.

## 10. Mini-project: KV slots vs fixed associative state

### 10.1 Câu hỏi nghiên cứu

Ta sẽ kiểm tra bốn hypotheses (giả thuyết):

1. Token-level storage có thể giữ mỗi write trong slot riêng, nhưng memory tăng theo số writes.
2. Delta memory có thể `exact recall` khi addresses trực giao và capacity đủ.
3. Delta correction xử lý `repeated-key overwrite` tốt hơn additive write.
4. Khi `logical keys` collide trong `fixed address space` (cùng address), delta correction không thể giữ cả hai exact; token slots vẫn giữ được evidence riêng.

### 10.2 Fairness và scope — đọc kỹ trước khi chạy

Mini-project cố ý so sánh **storage semantics** (ngữ nghĩa lưu trữ), không so chất lượng hai `neural architectures` đã train:

- `TokenLevelKV` dùng `exact logical-key match` và chọn write mới nhất. Đây là `oracle retrieval policy` (chính sách truy xuất lý tưởng) trên retained token slots, **không phải** implementation của `softmax attention`.
- `FixedAssociativeMemory` nhận `address vectors` đã định sẵn. Trong model thật, các vectors và gates phải được học.
- `Exact lookup baseline` cho thấy token slots còn giữ information nào; nó không chứng minh Transformer tự học được lookup policy đó.
- Code chạy `FP64` để test algebra, không benchmark `production kernel`, `BF16 stability` hay `throughput`.
- `position_ids` là **absolute** — `MLA`/`KDA` layers trong toy đều dùng `past_len + arange(T_new)` để tính vị trí.
- Nếu có `RoPE`, convention là `interleaved` — xoay cặp `(0,1),(2,3),...` — toy này không dùng RoPE nên không áp dụng, nhưng ghi chú để không nhầm khi đọc production code.

### 10.3 Runnable PyTorch code

```python
from dataclasses import dataclass

import torch


torch.set_default_dtype(torch.float64)


def one_hot(index: int, size: int) -> torch.Tensor:
    """One-hot vector — shape (size,), giá trị 1 tại index, 0 nơi khác."""
    return torch.nn.functional.one_hot(
        torch.tensor(index), num_classes=size
    ).to(torch.get_default_dtype())


class TokenLevelKV:
    """
    Oracle latest-match retrieval over separate token slots.
    Mỗi write là một slot riêng — shape tăng theo số writes.

    This isolates storage capacity. Standard attention would learn a scoring
    policy over retained slots rather than receive exact integer-key matching.
    """

    def __init__(self):
        self.slots = []  # list[(logical_key: int, value: Tensor)]

    def write(self, logical_key: int, value: torch.Tensor) -> None:
        # Append — không ghi đè slot cũ, chỉ thêm slot mới
        self.slots.append((logical_key, value.clone()))

    def read(self, logical_key: int) -> torch.Tensor:
        # Quét ngược — trả slot mới nhất khớp key
        for stored_key, stored_value in reversed(self.slots):
            if stored_key == logical_key:
                return stored_value.clone()
        raise KeyError(logical_key)

    @property
    def state_elements(self) -> int:
        # Count values only; real KV cache also stores key vectors/metadata.
        return sum(value.numel() for _, value in self.slots)


@dataclass
class FixedAssociativeMemory:
    """Fixed-state associative memory — state shape (d_address, d_value) không đổi."""
    d_address: int  # d_k — số key channels (số hàng của state)
    d_value: int    # d_v — chiều value (số cột của state)

    def __post_init__(self):
        self.state = torch.zeros(self.d_address, self.d_value)  # (d_k, d_v)

    def read(self, address: torch.Tensor) -> torch.Tensor:
        # address: (d_k,) @ state: (d_k, d_v) -> (d_v,)
        return address @ self.state

    def write_additive(
        self, address: torch.Tensor, value: torch.Tensor
    ) -> None:
        # S = S + k·vᵀ  — shape: (d_k,d_v) = (d_k,d_v) + (d_k,)(d_v,)
        self.state = self.state + torch.outer(address, value)

    def write_delta(
        self,
        address: torch.Tensor,
        value: torch.Tensor,
        beta: float = 1.0,
        alpha: torch.Tensor | None = None,
    ) -> None:
        # KDA-like ordering: channel-wise decay, then delta correction.
        # address: (d_k,), value: (d_v,), alpha: (d_k,), beta: scalar
        if alpha is None:
            alpha = torch.ones(self.d_address)  # (d_k,) — mặc định không quên
        if alpha.shape != (self.d_address,):
            raise ValueError("alpha must have shape (d_address,)")

        # Step 1: decay từng hàng — shape (d_k,d_v)
        decayed = alpha[:, None] * self.state   # (d_k,1)*(d_k,d_v) -> (d_k,d_v)
        # Step 2: đọc prediction từ decayed state — shape (d_v,)
        prediction = address @ decayed           # (d_k,) @ (d_k,d_v) -> (d_v,)
        # Step 3: error — shape (d_v,)
        error = value - prediction
        # Step 4: delta correction — shape (d_k,d_v)
        self.state = decayed + beta * torch.outer(address, error)

    @property
    def state_elements(self) -> int:
        return self.state.numel()  # d_k * d_v — hằng số


def is_exact(actual: torch.Tensor, expected: torch.Tensor) -> bool:
    return torch.allclose(actual, expected, rtol=0.0, atol=1e-10)


def decoded_id(value: torch.Tensor) -> int:
    return int(value.argmax())


# ------------------------------------------------------------------
# Experiment 1: exact recall with orthogonal addresses and enough state.
# Shape: d_address=4, d_value=4 — đủ chỗ cho 4 keys trực giao.
# ------------------------------------------------------------------
d_address = 4
d_value = 4
kv = TokenLevelKV()
delta = FixedAssociativeMemory(d_address, d_value)

for key_id in range(4):
    address = one_hot(key_id, d_address)  # (4,) — one-hot: trực giao hoàn hảo
    value = one_hot(key_id, d_value)      # (4,)
    kv.write(key_id, value)
    delta.write_delta(address, value, beta=1.0)

for key_id in range(4):
    expected = one_hot(key_id, d_value)
    assert is_exact(kv.read(key_id), expected)
    assert is_exact(delta.read(one_hot(key_id, d_address)), expected)

print("E1: both memories recall 4/4 with orthogonal addresses")


# ------------------------------------------------------------------
# Experiment 2: repeated-key overwrite — cùng address, value mới.
# ------------------------------------------------------------------
old_value = one_hot(0, d_value)  # [1,0,0,0]
new_value = one_hot(1, d_value)  # [0,1,0,0]
address = one_hot(0, d_address)  # cùng address cho cả hai writes

kv_overwrite = TokenLevelKV()
kv_overwrite.write(0, old_value)
kv_overwrite.write(0, new_value)

additive = FixedAssociativeMemory(d_address, d_value)
additive.write_additive(address, old_value)
additive.write_additive(address, new_value)

corrective = FixedAssociativeMemory(d_address, d_value)
corrective.write_delta(address, old_value, beta=1.0)
corrective.write_delta(address, new_value, beta=1.0)

print("E2 token latest:", kv_overwrite.read(0).tolist())
print("E2 additive:    ", additive.read(address).tolist())
print("E2 delta:       ", corrective.read(address).tolist())

assert is_exact(kv_overwrite.read(0), new_value)
assert not is_exact(additive.read(address), new_value)
assert is_exact(corrective.read(address), new_value)


# ------------------------------------------------------------------
# Experiment 3: two logical keys collide at exactly the same address.
# ------------------------------------------------------------------
collision_address = one_hot(0, d_address)
value_a = one_hot(2, d_value)  # [0,0,1,0]
value_b = one_hot(3, d_value)  # [0,0,0,1]

kv_collision = TokenLevelKV()
kv_collision.write(100, value_a)
kv_collision.write(200, value_b)

fixed_collision = FixedAssociativeMemory(d_address, d_value)
fixed_collision.write_delta(collision_address, value_a)
fixed_collision.write_delta(collision_address, value_b)

assert is_exact(kv_collision.read(100), value_a)
assert is_exact(kv_collision.read(200), value_b)
assert not is_exact(fixed_collision.read(collision_address), value_a)
assert is_exact(fixed_collision.read(collision_address), value_b)

print("E3 token slots retain A and B; fixed state retains latest collision")


# ------------------------------------------------------------------
# Experiment 4: decay trades retention for forgetting.
# ------------------------------------------------------------------
decaying = FixedAssociativeMemory(d_address, d_value)
key_a = one_hot(0, d_address)
key_b = one_hot(1, d_address)
decaying.write_delta(key_a, value_a)

alpha = torch.full((d_address,), 0.5)  # (4,) — quên 50% toàn state
decaying.write_delta(key_b, value_b, alpha=alpha)

read_a = decaying.read(key_a)
assert not is_exact(read_a, value_a)  # old association was scaled by 0.5
print("E4 old value after decay:", read_a.tolist())


# Persistent-state trend. Fixed count is independent of writes.
print("KV value elements after 4 writes:", kv.state_elements)
print("fixed-state elements:             ", delta.state_elements)
kv.write(99, one_hot(0, d_value))
assert kv.state_elements == 5 * d_value
assert delta.state_elements == d_address * d_value
```

### 10.4 Expected output

```text
E1: both memories recall 4/4 with orthogonal addresses
E2 token latest: [0.0, 1.0, 0.0, 0.0]
E2 additive:     [1.0, 1.0, 0.0, 0.0]
E2 delta:        [0.0, 1.0, 0.0, 0.0]
E3 token slots retain A and B; fixed state retains latest collision
E4 old value after decay: [0.0, 0.0, 0.5, 0.0]
KV value elements after 4 writes: 16
fixed-state elements:              16
```

Sau write thứ năm, `TokenLevelKV.state_elements` tăng lên 20, còn fixed state vẫn là 16. Đừng so hai con số tuyệt đối như production memory: baseline đã cố ý không đếm `key vectors`, `layer/head/batch dimensions`, `dtype` và `allocator`. Điều cần quan sát là **slope theo số writes** — token-level tăng tuyến tính, fixed-state nằm ngang.

## 11. Đọc kết quả mini-project đúng cách

### Experiment 1: fixed state không mặc định kém

Khi có đủ `orthogonal addresses` (keys trực giao), delta memory `exact recall` hoàn hảo trong toy algebra. Fixed state có thể rất hiệu quả nếu `task-relevant state` fit vào dimensions và `learned representation` tách được associations.

**Shape giải thích:** $d_k=4$ cho phép tối đa 4 hướng trực giao. Với 4 keys one-hot, mỗi key chiếm một hàng riêng của state — không chồng lấn.

### Experiment 2: delta tạo overwrite semantics

Additive memory trả $v_{old}+v_{new}=[1,1,0,0]$. Delta correction đọc prediction cũ và ghi residual, nên với normalized key và $\beta=1$, output trở thành chính xác $v_{new}=[0,1,0,0]$.

Token-level baseline cũng trả value mới vì `retrieval policy` quét từ slot mới nhất. Lưu ý `standard softmax attention` không tự có policy này chỉ vì cache tồn tại; model vẫn phải dùng `content/position` để chọn slot đúng.

### Experiment 3: collision là information loss

Hai `logical keys` (100 và 200) dùng cùng address `[1,0,0,0]` nhưng values khác nhau. Fixed state không thể biết query muốn key 100 hay 200 vì hai queries nhìn giống hệt nhau trong address space — cùng vector `[1,0,0,0]`. Delta rule chọn latest association cho direction đó, đồng thời phá recall của association trước.

Token cache giữ cả hai writes ở slots riêng — key 100 ở slot 0, key 200 ở slot 1. Đây là động cơ `representation-level` cho periodic `token-addressable attention`.

### Experiment 4: decay không miễn phí

Global decay 0.5 giúp old state nhỏ đi, nhưng `exact old value` cũng giảm một nửa: `[0,0,1,0]` thành `[0,0,0.5,0]`. Trong KDA thật, `channel-wise gate` được học và phụ thuộc input, nên model có thể chọn quên/giữ tinh vi hơn toy scalar-like vector. Dù vậy, learned gate không tạo guarantee rằng mọi old fact quan trọng sẽ được giữ.

## 12. Capacity stress mở rộng — khi random keys chồng lấn

Thay exact collision bằng nhiều random normalized addresses để quan sát gradual interference:

```python
def random_unit_addresses(n_keys: int, d_address: int, seed: int = 0):
    """Tạo n_keys random unit vectors — shape (n_keys, d_address)."""
    generator = torch.Generator().manual_seed(seed)
    addresses = torch.randn(n_keys, d_address, generator=generator)
    # Chuẩn hóa mỗi hàng về norm 1: (n_keys, d_address) / (n_keys, 1)
    return addresses / addresses.norm(dim=-1, keepdim=True)


def delta_recall_accuracy(n_keys: int, d_address: int) -> float:
    """Đo accuracy khi ghi n_keys associations vào fixed state."""
    # One-hot values let argmax act as a discrete recall decision.
    memory = FixedAssociativeMemory(d_address, n_keys)
    addresses = random_unit_addresses(n_keys, d_address)

    for key_id in range(n_keys):
        memory.write_delta(addresses[key_id], one_hot(key_id, n_keys))

    correct = 0
    for key_id in range(n_keys):
        prediction = memory.read(addresses[key_id])  # (d_address,) @ (d_address, n_keys) -> (n_keys,)
        correct += decoded_id(prediction) == key_id
    return correct / n_keys


for width in (8, 16, 32, 64):
    accuracy = delta_recall_accuracy(n_keys=64, d_address=width)
    print(f"d_address={width:2d} | recall={accuracy:.3f}")
```

Không hard-code expected accuracy: kết quả phụ thuộc `seed`, `write order`, `value coding` và `metric`. Hãy chạy nhiều seeds, báo `mean/std` và plot:

- x-axis: số keys hoặc số writes;
- y-axis: `exact-match accuracy` và `MSE`;
- các curves: `address width` 8, 16, 32, 64;
- baseline: `token-level latest-match lookup`;
- variants: `additive`, `delta`, `scalar decay`, `channel-wise decay`.

### Questions cần trả lời trong report của bạn

1. Khi nào delta memory đạt `exact recall`?
2. Accuracy giảm ra sao khi số keys lớn hơn `address width`?
3. `Repeated-key overwrite` khác `collision` giữa hai logical keys như thế nào?
4. Decay nào cải thiện `recent recall` nhưng làm hỏng `old recall`?
5. `State elements` tăng theo context ở từng baseline ra sao?
6. Kết quả nào là `algebraic guarantee` (bảo đảm đại số), kết quả nào chỉ là `empirical observation` (quan sát thực nghiệm)?

## 13. Nếu muốn gần KDA thật hơn — học gates

Mini-project chưa học gates. Có thể mở rộng bằng một small controller:

```python
# x_t: (d_model,) — hidden state của token t
beta_t = torch.sigmoid(beta_proj(x_t))    # scalar per head, shape ()
alpha_t = torch.sigmoid(alpha_proj(x_t))  # vector per key channel, shape (d_k,)
# beta_proj: Linear(d_model -> 1), alpha_proj: Linear(d_model -> d_k)
```

Sau đó train `end-to-end` trên sequence gồm `WRITE`, `QUERY`, `repeated overwrite` và `distractors`. Cần tách datasets:

- `train length` và `longer test length` — test `length extrapolation`;
- `seen` và `unseen key/value combinations`;
- `recall without overwrite`;
- `overwrite` cùng key;
- `collision/capacity stress`;
- `recent versus distant query`.

Đừng gọi toy này là `KDA` đầy đủ nếu thiếu `learned Q/K/V projections`, `normalization`, `short convolution`, `output gate`, `multi-head composition` và `chunkwise training algorithm`.

## 14. Vì sao mini-project giải thích hybrid architecture?

Toy experiments tạo ba vùng behavior:

1. **State đủ và addresses tách tốt:** fixed `delta memory` recall chính xác với `bounded state` — KDA layers đủ.
2. **Overwrite cùng address đúng semantics:** delta correction thắng additive update — KDA sửa được.
3. **Nhiều distinct items vượt separability:** associations `interfere/collide`; không update rule nào phục hồi identity đã bị nén mất — cần `token-addressable` slots.

Hybrid `KDA–MLA` khai thác vùng 1–2 ở phần lớn layers, nhưng không đặt cược toàn bộ model vào việc mọi `long-context detail` luôn fit vào vùng đó. Periodic `global MLA layers` giữ `per-token candidates` để network có cơ hội truy xuất `fine-grained evidence` sau khi KDA layers đã thực hiện `recurrent mixing`.

MLA không phải một "backup database" được gọi conditionally trong Kimi Linear. Hai loại layers nối tiếp trong network; `hidden states` được biến đổi qua cả hai pathways. Mini-project chỉ minh họa `trade-off storage/retrieval`, không mô phỏng đầy đủ `information flow` giữa layers.

## 15. Complexity và serving implications

Bỏ qua `batch/layer/head` factors để tập trung scaling theo $T$:

| Mechanism | Persistent decode state | New-token history access | Retrieval risk chính |
|---|---:|---:|---|
| `MHA KV cache` | $O(T(d_k+d_v))$ — **có $T$** | $O(T)$ slots | `bandwidth/cache growth` |
| `MLA cache` | $O(Tr)$ — **có $T$**, $r=d_c+d_h^R$ | $O(T)$ compressed slots | `low-rank compression` + cache growth |
| `Delta/KDA state` | $O(d_k d_v)$ — **không $T$** | `fixed-shape state` | `interference`, `decay`, `capacity` |
| `Hybrid KDA–MLA` (3:1) | fixed KDA states + MLA cache ở 1/4 layers | mixed | cả hai trade-offs, nhưng ít `global-cache layers` hơn |

Kimi Linear report đo `speedups` và `cache reduction` cho `full model/configuration` của họ. Không suy `throughput` chỉ từ `Big-O`: `kernels`, `batch size`, `context`, `dtype`, `hardware`, `MoE`, `short convolution` và `memory allocator` đều ảnh hưởng.[^kimi-linear-2025]

**Ví dụ số — raw bytes với $B=1, L=32, H=32, d_h=128, p=2$ (BF16):**

| Context $S$ | MHA cache | MLA ($d_c=512, d_h^R=64$) | Fixed-state ($d_k=d_v=128, H=4$) | Hybrid 3:1 |
|---:|---:|---:|---:|---|
| 1K | 512 MiB | 36 MiB | 4 MiB | ~12 MiB |
| 8K | 4 GiB | 288 MiB | 4 MiB | ~76 MiB |
| 32K | 16 GiB | 1.1 GiB | 4 MiB | ~280 MiB |

Đọc trend: `MHA` dốc đứng, `MLA` dốc thoải hơn (~14×), `fixed-state` nằm ngang, `hybrid` tăng nhưng slope chỉ bằng 1/4 của full MLA.

## 16. Xác minh trước khi benchmark — 4 tests phải pass

> [!warning] Lab này chỉ chứng minh semantics của toy fixed-state
> Full KDA còn `delta correction` với `learned gates`, `short convolution` và `chunkwise kernels`. Các test dưới không chứng minh parity với full KDA hay quality — chỉ chứng minh **recurrent correctness, overwrite, collision và shape cố định**.

```python
import torch


@torch.inference_mode()
def test_delta_overwrite_exact():
    """Test 1: delta overwrite cho exact recall với normalized key và beta=1."""
    torch.manual_seed(0)
    d = 4
    mem = FixedAssociativeMemory(d, d)
    k = one_hot(0, d)  # (4,) — unit vector
    v_old = one_hot(0, d)
    v_new = one_hot(1, d)
    mem.write_delta(k, v_old, beta=1.0)
    mem.write_delta(k, v_new, beta=1.0)
    result = mem.read(k)  # (4,)
    torch.testing.assert_close(result, v_new, rtol=0.0, atol=1e-10)
    print("✓ Test 1 passed: delta overwrite exact —", result.tolist())


@torch.inference_mode()
def test_additive_fails_overwrite():
    """Test 2: additive write KHÔNG cho overwrite — phải ra tổng."""
    torch.manual_seed(0)
    d = 4
    mem = FixedAssociativeMemory(d, d)
    k = one_hot(0, d)
    v_old = one_hot(0, d)
    v_new = one_hot(1, d)
    mem.write_additive(k, v_old)
    mem.write_additive(k, v_new)
    result = mem.read(k)
    expected_sum = v_old + v_new  # [1,1,0,0]
    torch.testing.assert_close(result, expected_sum, rtol=0.0, atol=1e-10)
    assert not torch.allclose(result, v_new)
    print("✓ Test 2 passed: additive gives sum, not overwrite —", result.tolist())


@torch.inference_mode()
def test_orthogonal_no_crosstalk():
    """Test 3: orthogonal keys không gây crosstalk — sửa key này không ảnh hưởng key kia."""
    torch.manual_seed(0)
    d = 4
    mem = FixedAssociativeMemory(d, d)
    k_a = one_hot(0, d)  # [1,0,0,0]
    k_b = one_hot(1, d)  # [0,1,0,0] — trực giao với k_a
    v_a = one_hot(2, d)  # [0,0,1,0]
    v_b = one_hot(3, d)  # [0,0,0,1]
    mem.write_delta(k_a, v_a, beta=1.0)
    mem.write_delta(k_b, v_b, beta=1.0)
    torch.testing.assert_close(mem.read(k_a), v_a, rtol=0.0, atol=1e-10)
    torch.testing.assert_close(mem.read(k_b), v_b, rtol=0.0, atol=1e-10)
    print("✓ Test 3 passed: orthogonal keys no crosstalk")


@torch.inference_mode()
def test_fixed_state_shape_independent_of_writes():
    """Test 4: state shape không đổi dù số writes tăng — fixed-state."""
    torch.manual_seed(0)
    d_k, d_v = 8, 8
    mem = FixedAssociativeMemory(d_k, d_v)
    assert mem.state.shape == (8, 8)
    assert mem.state_elements == 64
    for i in range(100):
        k = torch.randn(d_k, dtype=torch.float64)
        k = k / k.norm()
        v = torch.randn(d_v, dtype=torch.float64)
        mem.write_delta(k, v, beta=0.5)
        assert mem.state.shape == (8, 8), f"state shape changed at write {i}"
        assert mem.state_elements == 64
    print("✓ Test 4 passed: state shape (8,8)=64 elements after 100 writes — fixed!")


# Chạy tất cả — copy block này vào python và chạy
test_delta_overwrite_exact()
test_additive_fails_overwrite()
test_orthogonal_no_crosstalk()
test_fixed_state_shape_independent_of_writes()
```

**Cách đọc khi test fail:**

| Test fail | Triệu chứng | Check đầu tiên |
|---|---|---|
| Test 1 | `delta overwrite != v_new` | `beta` có bằng 1 không? `k` có chuẩn hóa `||k||=1` không? Thứ tự `decayed` và `prediction` đúng chưa? |
| Test 2 | `additive == v_new` (đáng lẽ phải fail) | Đang vô tình dùng `write_delta` thay vì `write_additive`? |
| Test 3 | `orthogonal crosstalk` | Keys có thực sự trực giao? `k_a @ k_b` phải = 0 — in ra kiểm tra |
| Test 4 | `state shape` đổi | Đang `append` thay vì `in-place update`? `state` phải là `(d_k, d_v)` cố định |

Cả 4 tests phải pass trước khi đo benchmark — benchmark trên implementation sai là vô nghĩa.

## 17. Benchmark / Trade-offs — đo đúng thứ, đọc đúng slope

### 17.1 Tách prefill và decode — hai phase bottleneck khác nhau

| Phase | Work chính | Token-level cache | Fixed-state |
|---|---|---|---|
| **Prefill** ($S$ tokens) | tạo outputs cho $S$ positions | $O(S^2)$ scores (có thể chunkwise) | `chunkwise parallel` — $O(S)$ state updates |
| **Decode** (1 token) | 1 query với history | $O(S)$ reads + $O(S)$ scores — **tăng với $S$** | $O(d_k d_v)$ — **hằng số** — đọc state cố định |

> Đo riêng: `prefill latency` (ms cho $S$ tokens) và `decode latency` (ms/token khi $S$ đã lớn). Đừng suy latency từ bytes. Training/prefill của `linear attention` cần `chunkwise algorithms` để song song — `recurrent loop` từng token sẽ chậm.[^kimi-linear-2025]

### 17.2 Khi nào chọn gì? — bảng quyết định

| Mục tiêu | Ưu tiên | Lựa chọn | Vì sao |
|---|---|---|---|
| Retrieval chính xác trên context dài (`needle-in-haystack`, `exact copy`) | `Token-addressability` — mỗi token một slot | `Softmax` / `MLA` | Query tạo weight riêng cho từng position — shape `(B,H,1,S)` |
| Context cực dài + memory cố định (`streaming` vô hạn) | `Bounded state` — memory không tăng | `Fixed-state` (`KDA`, `Mamba-2`, `DeltaNet`) | State `(d_k, d_v)` cố định |
| Cân bằng cả hai | Giảm slope nhưng giữ retrieval | **Hybrid 3×KDA + 1×MLA**[^kimi-linear-2025] | 75% layers fixed-state (giảm cache), 25% MLA (giữ token-addressability) |

## 18. Debug checklist — triệu chứng → nguyên nhân → check

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên (in shape ra) |
|---|---|---|
| `delta overwrite != v_new` | $\beta\ne1$ hoặc $\\|k\\|\ne1$ hoặc thứ tự `decay/prediction` sai | `print(beta, k.norm(), prediction)` — phải là `1.0, 1.0, v_old` |
| Future leakage (sửa future làm past đổi) | Dùng `parallel` không causal | Loop chỉ dùng `k_t` hiện tại; `cumsum` đã causal chưa? |
| State shape chứa $T$ | Đang lưu `writes` `(B,T,d_k,d_v)` thay vì `state` `(B,d_k,d_v)` | `print(state.shape)` — phải là `(B,d_k,d_v)` không có $T$ |
| NaN/Inf output | `alpha` hoặc `beta` ngoài $[0,1]$ | `print(alpha.min(), alpha.max(), beta)` — phải trong $[0,1]$ |
| Accuracy giảm khi $S$ tăng | `Interference` — keys không trực giao, $d_k$ quá nhỏ | `print(k_a @ k_b)` — overlap bao nhiêu? Thử tăng $d_k$ |
| Throughput không tăng dù state nhỏ | Bottleneck là `compute/bandwidth`, không phải `capacity` | Profile riêng `prefill` vs `decode`; đo `memory bandwidth` |
| Nhầm "infinite context" | Hiểu `state bounded = nhớ vô hạn` | Test `retrieval accuracy` theo $S$ — phải giảm khi $S\gg d_k$ |
| `alpha` shape mismatch | `alpha` là scalar nhưng code expect `(d_k,)` | `print(alpha.shape)` — phải là `(d_k,)` cho KDA |

## 19. Giới hạn & bước tiếp theo

**Lab này không chứng minh:**

- Quality parity giữa `linear` và `softmax` — cần ablation trên cùng data và task. Kimi Linear báo cáo hybrid 3:1 tốt hơn full MLA trên đa số benchmarks ở config của họ, nhưng đó là `author-run`, `config-specific`.[^kimi-linear-2025]
- Speedup thực tế — phụ thuộc `kernel`, `dtype`, `hardware`. Toy `for` loop là teaching, không phải serving (`chunkwise`/`fused_recurrent` kernels).[^kimi-linear-2025]
- Fixed-state có luôn kém retrieval — hybrid có thể bù đắp, nhưng trade-off phụ thuộc workload và tỷ lệ hybrid.
- Mọi `feature map` đều tốt như nhau — `DPFP` tăng `capacity bound` nhưng cũng tăng `state/compute`.

**Những hiểu lầm thường gặp (đọc kỹ trước khi tin headline):**

1. "Delta rule làm fixed state lossless." — Sai. Nó sửa addressed association; overlapping addresses vẫn gây collateral update.
2. "Decay tăng capacity mà không mất gì." — Sai. Forgetting dọn state bằng cách giảm old information.
3. "Channel-wise decay tạo một slot cho mỗi token." — Sai. State vẫn không có sequence axis — shape vẫn $(d_k,d_v)$.
4. "MLA là fixed-state vì dùng latent." — Sai. MLA giữ một latent **trên mỗi token** — shape $(B,S,d_c)$ có $S$.
5. "Periodic MLA nghĩa là thỉnh thoảng mới xử lý token." — Sai. Periodic mô tả pattern **theo layer depth** — mọi token đi qua mọi layer.
6. "3:1 luôn tối ưu." — Sai. Đây là empirical choice trong Kimi Linear recipe — 1:1 gần như tương đương.[^kimi-linear-2025]
7. "KV cache bảo đảm exact recall." — Sai. Nó giữ candidate slots; scoring/retrieval vẫn có thể sai.
8. "Hybrid có constant total cache." — Sai. Periodic MLA layers vẫn có cache tăng theo context.
9. "Toy latest-match KV là softmax attention." — Sai. Nó là oracle storage baseline để tách storage khỏi learned retrieval.
10. "Chunkwise training đổi recurrence." — Không nên mặc định. Mục tiêu của derivation/kernel là tính cùng recurrence hiệu quả hơn; equivalence phải được kiểm chứng theo implementation và precision.[^parallel-deltanet-2024][^kimi-linear-2025]

**Checklist khi đọc một delta/hybrid paper — trả lời trước khi tin headline:**

1. State có shape gì và có sequence axis không? $(d_k,d_v)$ hay $(S,d)$?
2. Update là `additive`, `delta`, `decay` hay cả hai?
3. Delta prediction đọc trước hay sau decay? Thứ tự quan trọng!
4. $\beta$ là scalar, vector hay matrix; có nằm trong $[0,1]$ không?
5. $\alpha$ là scalar per head hay channel-wise vector $(d_k,)$?
6. Keys có được normalize không? $\|k\|=1$?
7. Training/prefill dùng `recurrent` hay `chunkwise algorithm`?
8. Decode cache còn `short-convolution state` hoặc auxiliary state nào?
9. Hybrid là `headwise` hay `layerwise`? Kimi Linear là layerwise.
10. Global attention là `MHA`, `GQA`, `MLA`, `local` hay `sparse`?
11. "Periodic" được định nghĩa theo depth hay time?
12. Benchmark có `exact copy`, `MQAR`, overwrite và distractors không?
13. Ratio ablation có `matched compute/model/data` không?
14. Efficiency number là `theoretical FLOPs`, `batch-one latency` hay `max throughput`?
15. Claim là `derivation`, `author-run experiment` hay `independent replication`?

**Học tiếp theo (theo roadmap Stage 8):**

1. [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — derivation chi tiết từ kernel đến recurrent.
2. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — cách delta correction và decay cải thiện fixed-state.
3. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — vì sao periodic MLA bù retrieval limits.
4. [Multi-head Latent Attention](multi-head-latent-attention.md) và [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) — nén per-token nhưng giữ token-addressability.
5. [Structured State Space Duality](structured-state-space-duality.md) — linear attention như trường hợp riêng của semiseparable mask.

**Bài tập đề xuất (làm theo thứ tự):**

1. Tự suy ra $S_t, z_t$ từ $\kappa(q,k)=\phi(q)^{\top}\phi(k)$ mà không nhìn công thức — viết shape từng bước.
2. Chạy $\beta\in\{0,0.25,0.5,1\}$ và plot `MSE` sau mỗi repeated write — quan sát partial overwrite.
3. Đặt $\alpha=[1,1,0.1,0.1]$; kiểm tra channels nào giữ association lâu hơn — channel-wise decay.
4. Thay one-hot addresses bằng vectors có `cosine similarity` được kiểm soát và đo collateral update.
5. Sửa token baseline để chọn `first match`, `latest match` và `softmax mixture`; giải thích retrieval policy khác storage layout.
6. Thêm `key element count` và tìm context $T$ nơi token cache lớn hơn matrix state — memory crossover.
7. Chèn hàng nghìn `distractor writes` giữa old và new value; đo `recent/old recall`.
8. Train gates $\alpha_t,\beta_t$ trên synthetic `WRITE/QUERY` task và test `length extrapolation`.
9. Tạo `explicit prefix reference` cho recurrence và so với `online update` bằng `torch.testing.assert_close`.
10. Đối chiếu synthetic KDA tasks với `end-to-end long-context benchmarks`; không dùng một bên để chứng minh bên kia.

## Relationships

- **Depends on:** [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — `linear attention` là nền tảng để hiểu vì sao cần delta.
- **Depends on:** [KV caching](kv-caching.md) và [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) — hiểu vì sao cache tăng $O(S)$ trước khi học cách xóa trục $S$.
- **Builds on:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — delta correction và learned decay.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) — nén per-token nhưng vẫn sequence-growing, khác với fixed-state.
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng lý thuyết delta/KDA và mini-project exact recall/overwrite.
- **Explains:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), đặc biệt pattern layerwise 3:1 và retrieval-versus-memory trade-off.
- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — KDA + periodic MLA trong frontier model.
- **Supported by:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md), nơi `gating` cải thiện retrieval trong recipe được test.

## Evidence limits

Delta update, associative-memory interpretation và orthogonality argument đến từ primary `fast-weight/DeltaNet` papers. Scalar decay evidence đến từ `Gated DeltaNet`; `channel-wise KDA recurrence`, `3:1 hybrid`, `synthetic tasks`, `ratio ablation` và `efficiency claims` đến từ `Kimi Linear` primary report. Các papers cung cấp `author-run results`, không phải `independent replication`. Derivations trong course này follow documented recurrences; `oracle KV baseline`, `collision experiments`, `code organization`, `expected outputs` và `teaching sequence` là **pedagogical synthesis**. Chúng minh họa `representation trade-offs`, không dự đoán trực tiếp `perplexity`, `long-context benchmark score` hoặc `production speed`.[^fast-weight-programmers-2021][^parallel-deltanet-2024][^gated-deltanet-2025][^kimi-linear-2025]

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, "Linear Transformers Are Secretly Fast Weight Programmers," ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4 and Appendices A–B.
[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, "Parallelizing Linear Transformers with the Delta Rule over Sequence Length," NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–3 and appendices.
[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, "Gated Delta Networks: Improving Mamba2 with Delta Rule," ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–5 and Appendix A.
[^kimi-linear-2025]: Kimi Team, "Kimi Linear: An Expressive, Efficient Attention Architecture," arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 2–6 and the chunkwise derivation appendices.
