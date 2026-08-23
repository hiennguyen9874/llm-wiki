---
type: Synthesis
title: "SSD → Mamba-2: recurrence, duality, chunked training và parallelism — bài học cho người mới"
description: A beginner-first course from selective SSM recurrence through structured-attention duality and chunked SSD computation to the Mamba-2 block and its tensor/context parallelism, with every formula, shape, and PyTorch lab explained step-by-step.
tags: [ssd, mamba-2, ssm, recurrence, structured-attention, chunked-training, parallelism, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-23T14:30:00Z }
sources:
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# SSD → Mamba-2: recurrence, duality, chunked training và parallelism — bài học cho người mới

`Mamba-2` xây `sequence mixer` trên `Structured State Space Duality` (`SSD`): **cùng một phép biến đổi causal** có thể tính như **recurrent state update** (cập nhật state từng token) hoặc viết thành một **structured masked attention-like matrix** (ma trận có mask cấu trúc như attention). Khi training, SSD chia sequence thành chunks: dùng `matrix multiplication` song song bên trong từng chunk và chỉ `scan` (quét) recurrent states ở mức chunk. Khi decode, model giữ một `fixed-size state` (state có shape cố định, không tăng theo độ dài) thay vì `KV cache` tăng theo context. Mamba-2 tiếp tục tổ chức `projections`, `heads`, `normalization` và `sharding` để block này phù hợp hơn với cách train Transformer ở quy mô lớn.[^dao-gu-2024]

> [!success] Sau bài này, bạn có thể
> 1. Viết và **unroll** (mở vòng lặp) một `selective SSM recurrence` và nói đúng shape từng tensor.
> 2. Suy ra causal matrix $M$ và structured mask $L$ từ recurrence — giải thích từng entry $L_{t,i}$.
> 3. Giải thích `semiseparable structure` (cấu trúc off-diagonal rank thấp) và `duality` với `structured masked attention`.
> 4. Phân biệt `recurrent form`, `quadratic form` và `chunked form` — khi nào materialize $T\times T$, khi nào không.
> 5. Implement và kiểm chứng `recurrent == quadratic` bằng PyTorch với `torch.testing.assert_close` (rtol/atol chặt).
> 6. Mô tả 4 bước của `block SSD algorithm` (diagonal / right / center / left).
> 7. Đọc được data flow của một Mamba-2 block: `parallel projections → conv → SSD → gate → norm → out`.
> 8. Phân biệt `tensor parallelism`, `sequence parallelism` (cho residual/norm) và `context parallelism` (cho SSM mixer).
> 9. Nêu đúng trade-off giữa `fixed-state memory` và `token-addressable attention` qua shape có chứa $S$ hay không.

## 1. Trước khi đọc — bạn cần gì?

**Bạn chỉ cần toán cơ bản:**

| Khái niệm | Ý nghĩa 1 dòng |
|---|---|
| Vector shape `(d,)` | danh sách $d$ số |
| Ma trận shape `(a, b)` | bảng $a$ hàng $b$ cột |
| Nhân ma trận `(a,b)×(b,c)→(a,c)` | chiều giữa phải khớp |
| Outer product $u v^{\top}$ | cột `(m,1)` × hàng `(1,d_v)` → ma trận `(m,d_v)` |
| Tích $\prod_{r=i+1}^{t} a_r$ | nhân $a_{i+1}\cdot a_{i+2}\cdots a_t$ |
| `einsum` | ghi rõ chiều nào nhân với chiều nào |

**Nên đọc trước (để không lạc):**

- [Attention: beginner's guide](attention-beginner-guide.md): Q/K/V, causal mask, multi-head.
- [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md): reassociation và matrix state — bài này dùng lại notation $S_t = S_{t-1}+ x_tb_t^{\top}$.
- [Self-attention computational profile](self-attention-computational-profile.md): quadratic interaction và parallel training.
- [LLM inference lifecycle: training, prefill, decode, và latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md): khác biệt training / prefill / decode.

**Ký hiệu thống nhất (đọc một lần, dùng cả bài):**

| Ký hiệu | Shape ở một head | Ý nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| $B$ | scalar | `batch size` — số sequences song song | 1, 2 |
| $T$ | scalar | `sequence length` — độ dài chuỗi | $S$ trong cache accounting |
| $P$ | scalar | `head width` của $X$/`$x_t$` | ví dụ 4, 64 |
| $N$ | scalar | `state dimension` — chiều state | ví dụ 5, 64 |
| $Q$ | scalar | `chunk length` — độ dài một chunk | 64 thường gặp |
| $C$ | scalar | `number of chunks` $=T/Q$ |  |
| $x_t$ | $(P,)$ | `sequence input` / value tại token $t$ | vector |
| $b_t$ | $(N,)$ | `expansion vector` — tương tự $K$ trong duality | vector |
| $c_t$ | $(N,)$ | `contraction vector` — tương tự $Q$ trong duality | vector |
| $a_t$ | scalar | `scalar transition` / decay — giữ bao nhiêu state cũ | $0<a_t\le 1$ toy |
| $S_t$ | $(P,N)$ | `recurrent state` — ma trận gom history | **không có $T$** |
| $y_t$ | $(P,)$ | `output` tại token $t$ | vector |
| $A_t$ | $(N,N)$ | `transition matrix` tổng quát (general SSM) | $A_t=a_t I$ trong SSD |
| $L_{t,i}$ | scalar | `structured mask` entry — tích $a$ từ $i+1$ đến $t$ | $L_{t,t}=1$, $L_{t,i}=0$ nếu $i>t$ |

Với `batch` và `multi-head` (`H` heads): $x_t$ thực tế `(B,H,P)`, $S_t$ `(B,H,P,N)`, $a_t$ `(B,H)`.

> [!tip] Cách đọc mọi công thức trong bài
> Mỗi công thức sẽ mổ thành 4 dòng: **Ký hiệu là gì → Shape là gì → Phép toán làm gì → Kết quả shape ra sao**. Hãy theo dõi shape chảy — đó là cách nhanh nhất để không lạc.

**Bản đồ bài học:**

```text
scalar recurrence  h_t = a_t h_{t-1}+ x_t
       │ unroll theo thời gian (mở vòng lặp)
       ▼
causal semiseparable matrix  M  (mỗi entry là tích a's)
       │ scalar-identity  A_t = a_t I
       ▼
structured masked attention-like form  M = L ∘ (C Bᵀ)
       │ block decomposition (chia thành chunks)
       ▼
chunked SSD training  (4 bước: diagonal / right / center / left)
       │ block + head + projection redesign
       ▼
Mamba-2 và distributed parallelism  (TP / SP / CP)
```

> [!important] Hai tầng khái niệm — đừng lẫn
> `SSD` vừa là một **duality/framework** (góc nhìn toán học: cùng phép biến đổi có hai dạng tính), vừa dẫn tới một **hardware-oriented block algorithm** (thuật toán chia chunk để chạy nhanh trên GPU). `Mamba-2` là **neural architecture** dùng SSD layer; SSD không phải tên thay thế cho toàn bộ Mamba-2 block.

## 2. Từ recurrence đến fixed-size state — vì sao shape không chứa $T$?

### 2.1 Scalar recurrence nhỏ nhất — mọi thứ bắt đầu từ đây

Bắt đầu với recurrence vô hướng (một số duy nhất, không phải vector):

$$
\boxed{h_t = a_t\, h_{t-1} + x_t,\qquad y_t = h_t}
$$

Giải từng ký hiệu:

| Ký hiệu | Shape | Ý nghĩa | Ví dụ số |
|---|---|---|---|
| $h_t$ | scalar | `state` sau token $t$ | $h_2=11$ |
| $h_{t-1}$ | scalar | state trước đó | $h_1=5$ |
| $a_t$ | scalar | `transition/decay` — giữ bao nhiêu state cũ | $a_2=0.2$ |
| $x_t$ | scalar | `new input` — thông tin token mới | $x_2=10$ |
| $y_t$ | scalar | `output` — đọc state ra | $y_2=11$ |

Phép toán: `scalar × scalar + scalar → scalar`. Diễn giải:

- Nếu $a_t=1$: state cộng dồn toàn bộ history (nhớ mãi).
- Nếu $0<a_t<1$: thông tin cũ decay (phai) theo khoảng cách — giống hệ số quên.
- Nếu $a_t$ phụ thuộc input ($a_t = f(x_t)$): retention trở thành `selective` (chọn lọc) — model học khi nào nhớ, khi nào quên.

**Unroll (mở vòng lặp) 3 bước với $h_{-1}=0$:**

Công thức truy hồi nói $h_1$ phụ thuộc $h_0$, $h_2$ phụ thuộc $h_1$… Thay thế liên tiếp:

$$
\begin{aligned}
h_0 &= a_0 h_{-1}+x_0 = x_0,\\
h_1 &= a_1 h_0 + x_1 = a_1 x_0 + x_1,\\
h_2 &= a_2 h_1 + x_2 = a_2(a_1 x_0 + x_1)+x_2 = a_2a_1 x_0 + a_2 x_1 + x_2.
\end{aligned}
$$

Bạn thấy quy luật: $h_t$ là **tổng có trọng số** của mọi $x_i$ ($i\le t$), trọng số là tích các $a$ từ $i+1$ đến $t$.

**Ví dụ số cụ thể — tính tay để nhớ:**

Cho $a=[1, 0.5, 0.2]$ và $x=[2, 4, 10]$ (giả sử $a_0$ không dùng vì $h_{-1}=0$):

$$
\begin{aligned}
h_0 &=2,\\
h_1 &=0.5\times 2+4=5,\\
h_2 &=0.2\times 5+10=11.
\end{aligned}
$$

**Viết thành matrix form (dạng ma trận):**

$$
\begin{bmatrix}y_0\\y_1\\y_2\end{bmatrix}
=
\underbrace{
\begin{bmatrix}
1   &0  &0\\
0.5 &1  &0\\
0.1 &0.2&1
\end{bmatrix}}_{L = \operatorname{1SS}(a)}
\begin{bmatrix}x_0\\x_1\\x_2\end{bmatrix}
$$

Giải từng entry:

| Entry | Công thức | Tính | Shape |
|---|---|---|---|
| $L_{0,0}=1$ | empty product | 1 | scalar |
| $L_{1,0}=a_1$ | $0.5$ | $0.5$ | scalar |
| $L_{2,0}=a_2a_1$ | $0.2\times 0.5$ | $0.1$ | scalar |
| $L_{2,1}=a_2$ | $0.2$ | $0.2$ | scalar |
| $L_{t,i}=0$ nếu $i>t$ | causal | trên diagonal = 0 | scalar |

Tổng quát:

$$
\boxed{L_{t,i} = \prod_{r=i+1}^{t} a_r\quad (i\le t),\qquad L_{t,t}=1,\qquad L_{t,i}=0\ (i>t)}
$$

$L$ là `causal matrix` (ma trận nhân quả): mọi phần tử phía trên diagonal bằng 0 — future không ảnh hưởng past. Paper gọi đây là `1-semiseparable` matrix và phép tính là `cumprodsum` (tích lũy rồi cộng có trọng số).[^dao-gu-2024]

**Shape tổng quát:** $L$ shape `(T,T)` — nhưng đây là **teaching construction**, không phải thứ ta materialize khi $T$ lớn. Recurrent form chỉ cần scalar state.

### 2.2 Vector input và matrix state — thêm chiều feature

Scalar recurrence chỉ lưu 1 số. Thực tế cần lưu nhiều features. Dùng matrix state:

$$
\boxed{S_t = a_t\, S_{t-1} + x_t b_t^{\top}},\qquad
\boxed{y_t = S_t\, c_t}
$$

Giải từng ký hiệu, từng shape:

| Tensor | Shape ở một head | Phép toán | Kết quả shape | Vai trò |
|---|---|---|---:|---|
| $x_t$ | $(P,)$ | — | — | `sequence input` / value |
| $b_t$ | $(N,)$ | — | — | `expansion vector` — mở rộng vào state |
| $x_t b_t^{\top}$ | $(P,1)\times(1,N)$ | outer product | $(P,N)$ | ghi association vào state |
| $a_t S_{t-1}$ | scalar × $(P,N)$ | scale | $(P,N)$ | decay state cũ |
| $S_t$ | $(P,N)$ | cộng 2 ma trận | $(P,N)$ | `recurrent state` — **không có $T$** |
| $c_t$ | $(N,)$ | — | — | `contraction vector` — đọc state ra |
| $S_t c_t$ | $(P,N)\times(N,)$ | matrix-vector | $(P,)$ | output |

**Ví dụ shape số:** $P=4, N=5$ → $S_t$ là bảng $4\times 5=20$ số. Dù $T=1\,000$ hay $T=1\,000\,000$, $S_t$ vẫn $4\times 5$ — đây là `fixed-state recurrence` (trạng thái cố định).

**Với batch và heads:** thêm 2 trục đầu: $S_t$ shape `(B,H,P,N)`, $x_t$ `(B,H,P)`, $b_t,c_t$ `(B,H,N)`, $a_t$ `(B,H)`. Code dùng `einsum("bhp,bhn->bhpn", x, b)` chính là outer product có batch/head.

> [!note] Convention — đừng hoảng khi thấy $b_t x_t^{\top}$
> Một số tài liệu đặt vectors theo hàng/cột khác nhau: bạn có thể thấy $b_t x_t^{\top}$ thay vì $x_t b_t^{\top}$, hoặc $S_t$ shape $(N,P)$ thay vì $(P,N)$. Ý nghĩa giống nhau nếu toàn bộ contractions và shapes nhất quán — chỉ là transpose. Luôn check `einsum` string để biết chiều nào nhân chiều nào.

**Unroll vector recurrence:**

$$
S_t = \sum_{i=0}^{t}\left(\prod_{r=i+1}^{t} a_r\right) x_i b_i^{\top}
$$

$$
y_t = S_t c_t = \sum_{i=0}^{t}\underbrace{\left(\prod_{r=i+1}^{t} a_r\right)}_{L_{t,i}}\underbrace{(c_t^{\top} b_i)}_{\text{content interaction}} x_i
$$

Đây là **chiếc cầu** từ recurrence sang attention-like form: $y_t$ là tổng của mọi $x_i$ quá khứ, mỗi $x_i$ được cân bởi hai thứ nhân nhau: `structured mask` $L_{t,i}$ (tích decays) và `content score` $c_t^{\top}b_i$ (dot product giữa query-like và key-like).

## 3. SSM là semiseparable matrix transformation — vì sao rank bị chặn?

Xét general SSM (trường hợp tổng quát, $A_t$ là ma trận $N\times N$):

$$
h_t = A_t h_{t-1} + B_t x_t,\qquad y_t = C_t^{\top} h_t
$$

Giải shape:

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $h_t$ | $(N,)$ | hidden state vector |
| $A_t$ | $(N,N)$ | transition matrix |
| $B_t$ | $(N,P)$ | input matrix |
| $C_t$ | $(N,)$ | output vector (sau đó $C_t^{\top} h_t$ → scalar/vector) |
| $x_t$ | $(P,)$ | input |

Unroll:

$$
y_t = \sum_{i=0}^{t} C_t^{\top} A_t A_{t-1}\cdots A_{i+1} B_i\, x_i
$$

Vì vậy toàn sequence là phép nhân ma trận $y = M x$, với:

$$
\boxed{M_{t,i} = C_t^{\top} A_t A_{t-1}\cdots A_{i+1} B_i,\qquad i\le t}
$$

Paper chứng minh: transformation của state-size $N$ tương ứng với một causal `N-semiseparable matrix`: các submatrices nằm trên hoặc dưới diagonal của phần causal có **rank không vượt quá $N$**. `Sequentially semiseparable` (`SSS`) representation chính là factorization bằng $A,B,C$ ở trên.[^dao-gu-2024]

### 3.1 Vì sao low-rank off-diagonal blocks quan trọng? — hình dung boundary state

Chọn một block output ở thời gian muộn và một block input ở thời gian sớm. Mọi ảnh hưởng từ block cũ sang block mới **phải đi qua boundary state** kích thước $N$:

```text
earlier inputs (chunk j) ──> boundary state (N dimensions) ──> later outputs (chunk k>j)
         T tokens                P×N numbers                      T tokens
         shape (T,P)             shape (P,N)                      shape (T,P)
```

Đây không chỉ là mô tả toán học. Chính factorization này cho phép SSD:

1. Tính local interactions bên trong chunk bằng `matrix multiplication` (nhanh trên GPU).
2. Nén ảnh hưởng của chunk thành `boundary state` (nhỏ, cố định).
3. Truyền boundary states qua một recurrence ngắn hơn (chỉ $C=T/Q$ steps thay vì $T$).
4. Bung state vào outputs của chunk sau.

### 3.2 Fixed state không phải token-addressable memory — khác MLA ở đâu?

| Thuộc tính | Full softmax attention / MLA | SSD recurrence |
|---|---|---|
| History lưu gì? | $S$ entries riêng — mỗi token một slot | 1 matrix $(P,N)$ chung |
| Shape có chứa $S$? | Có — `(B,S,d)` | Không — `(B,H,P,N)` |
| Query chấm từng token? | Có — scores shape `(B,H,S,S)` | Không — đọc state đã gộp |
| State tăng theo $S$? | Có — $O(S)$ | Không — $O(PN)$ cố định |
| Exact retrieval token $j$ | Có slot riêng (cấu trúc) | Không bảo đảm — phụ thuộc compression |

Vì vậy:

- Recurrent decode state **không tăng** theo $T$ → tiết kiệm memory khi context dài.
- Nhưng **không còn slot độc lập** cho mỗi token → không bảo đảm exact retrieval.
- State size $N$ là **capacity bottleneck** — giống $m$ trong linear attention.
- Đây là khác biệt nền tảng với [MLA](mla-token-addressable-memory-beginners-guide.md): MLA nén mỗi token nhưng cache vẫn có trục $S$; SSD bỏ trục $S$ khỏi recurrent state.

## 4. Structured State Space Duality — cùng phép biến đổi, hai cách tính

### 4.1 Scalar-identity transition — chìa khóa của duality

SSD specialization đặt:

$$
\boxed{A_t = a_t\, I}
$$

Giải thích: $I$ là identity matrix $(N,N)$ — đường chéo =1, ngoài =0. Nhân $a_t I$ chỉ là scale toàn bộ state bởi scalar $a_t$, không trộn các chiều state với nhau.

Khi đó products của transition matrices trở thành scalar product nhân identity:

$$
A_t A_{t-1}\cdots A_{i+1} = \left(\prod_{r=i+1}^{t} a_r\right) I
$$

Và matrix entry tách được thành hai phần nhân nhau:

$$
M_{t,i}=L_{t,i}\cdot (c_t^{\top} b_i)
$$

Gom toàn sequence (viết dạng ma trận cho $T$ tokens):

$$
\boxed{Y = \left(L \circ C B^{\top}\right) X}
$$

| Ký hiệu | Shape (single head, $T$ tokens) | Ý nghĩa |
|---|---|---|
| $L$ | $(T,T)$ | structured mask — $L_{t,i}=\prod_{r=i+1}^{t} a_r$ nếu $i\le t$, else 0 |
| $C$ | $(T,N)$ | stack các $c_t$ — rows là $c_t^{\top}$ |
| $B$ | $(T,N)$ | stack các $b_t$ |
| $C B^{\top}$ | $(T,N)\times(N,T)\to(T,T)$ | content Gram matrix — $(C B^{\top})_{t,i}=c_t^{\top}b_i$ |
| $L\circ C B^{\top}$ | $(T,T)$ elementwise | nhân từng entry — mask × content |
| $X$ | $(T,P)$ | stack các $x_t$ |
| $Y$ | $(T,P)$ | stack các $y_t$ — kết quả |

Theo vocabulary giống attention (để dễ liên tưởng):

$$
\boxed{Y = \left(L \circ Q K^{\top}\right) V}
$$

Mapping:

| SSM/SSD | Structured masked attention analogy | Shape |
|---|---|
| $C$ | $Q$ (query) | $(T,N)$ |
| $B$ | $K$ (key) | $(T,N)$ |
| $X$ | $V$ (value) | $(T,P)$ |
| transition product $A_{t:i}$ | structured mask $L_{t,i}$ | $(T,T)$ |
| state dimension $N$ | kernel feature dimension | scalar |

Dấu $\circ$ là `elementwise product` (nhân từng phần tử, không phải matrix multiply). $L$ không chỉ là binary causal mask (0/1); nó chứa **input-dependent decay/selection** qua products của $a_t$ — học được từ data.[^dao-gu-2024]

### 4.2 Hai contraction orders — cùng kết quả, khác cách tính

**Quadratic / attention-like order (materialize $T\times T$):**

```text
Step 1: G = C Bᵀ          shape (T,T) — mọi cặp token
Step 2: M = L ∘ G         shape (T,T) — nhân mask
Step 3: Y = M X           shape (T,T)×(T,P)→(T,P)
```

- Ưu: phơi bày pairwise token interactions, dùng `batched matmul` song song.
- Nhược: materialize tensor quadratic theo $T$ — tốn $O(T^2)$ memory/compute.

**Linear / recurrent order (không materialize $T\times T$):**

```text
state = 0  shape (P,N)
for t in 0..T-1:
    state = a_t * state + x_t b_tᵀ    shape (P,N)
    y_t   = state c_t                 shape (P,)
```

- Ưu: không materialize $T\times T$, memory $O(PN)$ cố định, decode hằng số.
- Nhược: token recurrence thuần túy có sequential dependency — khó tận dụng GPU matrix units bằng batched matmul.

`Duality` nghĩa là hai computational forms của **cùng transformation** trong SSD subset (khi $A_t=a_t I$), không phải hai model gần giống nhau. Kết quả số phải khớp nhau (trong sai số floating point).

> [!warning] SSD không phải softmax attention — đừng lẫn
> $L\circ QK^{\top}$ **không có row-wise `softmax`**, và SSD dựa trên finite feature contraction. Standard softmax attention nói chung **không thể** reassociate thành fixed-size exact recurrence theo cách này. Vì vậy đừng suy ra SSD giữ nguyên semantics hoặc retrieval behavior của softmax attention.[^dao-gu-2024]

### 4.3 So với linear attention — SSD là generalization

Causal linear attention có thể xem như trường hợp $a_t=1$ cho mọi $t$, nên $L$ là all-ones lower-triangular (toàn 1 ở tam giác dưới):

$$
\text{linear attention: }L_{t,i}=1
\quad\longrightarrow\quad
\text{SSD: }L_{t,i}=\prod_{r=i+1}^{t}a_r
$$

Paper còn chứng minh: nếu một `structured masked attention` instance là bounded-order autoregressive process, mask của nó **phải** là semiseparable. Đây là theorem về structure cần cho bounded-order autoregression, không phải tuyên bố mọi efficient attention đều là Mamba-2.[^dao-gu-2024]

## 5. Lab 1 — chứng minh recurrent form = quadratic form (phải khớp!)

Code sau ưu tiên **tính rõ ràng**, không tối ưu speed. `a` được chọn trong $(0,1)$ để products ổn định và dễ hiểu. Dùng `float64` để tolerance chặt.

```python
import torch


def ssd_recurrent(x, a, b, c):
    """
    Recurrent form — loop từng token, state cố định.
    Shapes:
      x: [B, T, H, P]          — sequence input (value)
      a: [B, T, H]             — scalar transition
      b: [B, T, H, N]          — expansion (key-like)
      c: [B, T, H, N]          — contraction (query-like)
      returns y: [B, T, H, P]  — output
    State shape (không có T): [B, H, P, N]
    """
    B, T, H, P = x.shape
    N = b.shape[-1]
    # state: (B, H, P, N) — cố định, không tăng theo T
    state = x.new_zeros(B, H, P, N)
    outputs = []

    for t in range(T):
        # Write: state = a_t * state + x_t b_t^T
        #   a[:,t]: (B,H) → (B,H,1,1) để broadcast với (B,H,P,N)
        #   x[:,t]: (B,H,P), b[:,t]: (B,H,N) → einsum "bhp,bhn->bhpn" → (B,H,P,N)
        state = (
            a[:, t, :, None, None] * state
            + torch.einsum("bhp,bhn->bhpn", x[:, t], b[:, t])
        )
        # Read: y_t = S_t c_t
        #   state: (B,H,P,N), c[:,t]: (B,H,N) → einsum "bhpn,bhn->bhp" → (B,H,P)
        y_t = torch.einsum("bhpn,bhn->bhp", state, c[:, t])
        outputs.append(y_t)

    # Stack T outputs: list of (B,H,P) → (B,T,H,P)
    return torch.stack(outputs, dim=1)


def one_ss_mask(a):
    """Build L[t,i] = prod_{r=i+1..t} a[r] — reference only, materialize (T,T)."""
    B, T, H = a.shape
    # L: (B, H, T, T) — teaching only, không dùng khi T lớn
    L = a.new_zeros(B, H, T, T)

    for t in range(T):
        L[:, :, t, t] = 1.0  # diagonal = 1 (empty product)
        running = torch.ones_like(a[:, 0])  # (B,H)
        for i in range(t - 1, -1, -1):
            running = running * a[:, i + 1]  # tích từ i+1 đến t
            L[:, :, t, i] = running
    return L


def ssd_quadratic(x, a, b, c):
    """Materialize structured attention-like matrix — reference only."""
    L = one_ss_mask(a)                            # (B,H,T,T)
    gram = torch.einsum("bthn,bshn->bhts", c, b)  # (B,H,T,T) — c_t^T b_s
    M = L * gram                                  # (B,H,T,T) — elementwise
    # M: (B,H,T,T), x: (B,T,H,P) → einsum "bhts,bshp->bthp" → (B,T,H,P)
    return torch.einsum("bhts,bshp->bthp", M, x)


# ---- Chạy và kiểm chứng ----
torch.manual_seed(0)
dtype = torch.float64
B, T, H, P, N = 2, 7, 3, 4, 5
x = torch.randn(B, T, H, P, dtype=dtype)  # (2,7,3,4)
a = torch.sigmoid(torch.randn(B, T, H, dtype=dtype))  # (2,7,3) in (0,1)
b = torch.randn(B, T, H, N, dtype=dtype)  # (2,7,3,5)
c = torch.randn(B, T, H, N, dtype=dtype)  # (2,7,3,5)

y_rec = ssd_recurrent(x, a, b, c)   # (2,7,3,4)
y_quad = ssd_quadratic(x, a, b, c)  # (2,7,3,4)

torch.testing.assert_close(y_rec, y_quad, rtol=1e-10, atol=1e-10)
print("max error:", (y_rec - y_quad).abs().max().item())
# Kỳ vọng: max error ~ 1e-15 (sai số float64)
```

**Ba quan sát trực tiếp từ code — nhìn shape là thấy duality:**

1. `state.shape == (B,H,P,N)` — **không có $T$** — token 2 và token 7000 cùng shape.
2. `L.shape == (B,H,T,T)` — **có $T^2$** — chỉ materialize trong quadratic form.
3. Hai hàm cho cùng output shape `(B,T,H,P)` dù cách tính khác nhau.

### 5.1 Điều test này chứng minh và không chứng minh

| Chứng minh | Không chứng minh |
|---|---|
| Hai algebraic forms nhất quán trong toy setup (float64) | Implementation production có cùng numerical behavior ở BF16/FP16 |
| Duality đúng về toán học | Chunked kernel nhanh hơn trên GPU của bạn |
| Code recurrent không bug causal | SSD đạt cùng quality với softmax attention |
| | Mamba-2 block hoàn chỉnh chỉ gồm recurrence này |

### 5.2 Causality test — future không được leak vào past

Output trước thời điểm $k$ không được đổi khi perturb future inputs:

```python
k = 4
x_changed = x.clone()
x_changed[:, k:] += 100.0  # thay đổi mạnh future

y_before = ssd_recurrent(x, a, b, c)
y_after = ssd_recurrent(x_changed, a, b, c)

# Chỉ so T positions đầu (k=4) — past phải giữ nguyên
torch.testing.assert_close(
    y_before[:, :k], y_after[:, :k], rtol=1e-10, atol=1e-10
)
print(f"✓ Causality: past {k} positions unchanged after future perturbation")
```

Nếu test fail, thường có lỗi index trong transition product (nhầm $a_{i}$ vs $a_{i+1}$) hoặc causal mask không đúng.

## 6. Vì sao cần chunked SSD training? — tension giữa hai forms

Ta có một tension (xung đột) cốt lõi:

| Form | Ưu điểm | Nhược điểm |
|---|---|---|
| **Recurrent** | work linear theo $T$ ($O(T)$), fixed-size decode state | token-level dependency — sequential, GPU utilization khó hơn (không dùng matmul lớn) |
| **Quadratic** | `matrix multiplication` song song, đơn giản | materialize $T\times T$ → $O(T^2)$ memory/work |
| **Chunked SSD** | local matmul + short state scan — best of both | implementation phức tạp hơn; cần chọn chunk size $Q$ |

SSD algorithm partition $T$ tokens thành $C=T/Q$ chunks, mỗi chunk dài $Q$. Semiseparable matrix $M$ trở thành block lower-triangular matrix:

```text
M = ┌ M^{(0,0)}    0        0     ┐
    │ M^{(1,0)}  M^{(1,1)}   0     │  mỗi M^{(j,j)} là diagonal block (intra-chunk)
    │ M^{(2,0)}  M^{(2,1)} M^{(2,2)}│  mỗi M^{(j,i)} với j>i là off-diagonal (inter-chunk)
    └ ...       ...      ...   ┘
         j = chunk index (0..C-1)
```

### 6.1 Diagonal blocks: intra-chunk (trong chunk)

$M^{(j,j)}$ chứa interactions giữa tokens **cùng chunk $j$**. Vì $Q$ nhỏ (ví dụ 64), tính block này bằng quadratic dual — materialize $Q\times Q$ thay vì $T\times T$:

$$
Y_{\text{diag}}^{(j)} = \left(L^{(j)}\circ C^{(j)}B^{(j)\top}\right) X^{(j)}
$$

| Ký hiệu | Shape | Ý nghĩa |
|---|---|---|
| $X^{(j)}$ | $(Q,P)$ | inputs của chunk $j$ |
| $B^{(j)},C^{(j)}$ | $(Q,N)$ | key/query của chunk $j$ |
| $L^{(j)}$ | $(Q,Q)$ | local mask — tích $a$ trong chunk |
| $Y_{\text{diag}}^{(j)}$ | $(Q,P)$ | outputs chỉ từ tokens cùng chunk |

**Quan trọng:** Giả định state đầu chunk = 0 — chỉ tính contribution từ tokens trong chunk. Mọi chunks có thể tính **song song** bằng `batched matrix multiplication`.

### 6.2 Right factors: chunk input → chunk-final state

Mỗi chunk nén toàn bộ local inputs thành contribution vào final state — một **low-rank summary**:

```text
Q tokens trong chunk j  ──(right factor)──>  one state contribution  shape (P,N)
     shape (Q,P)  +  (Q,N)                        shape (P,N)
```

Đây là phần `B-block-factor` của low-rank off-diagonal blocks. Mỗi chunk tạo một `(P,N)` summary — rất nhỏ so với $(Q,P)$ inputs.

### 6.3 Center factors: inter-chunk recurrence (scan ngắn)

Scan qua $C=T/Q$ chunk states thay vì $T$ token states:

```text
state_0 ──transition(a's in chunk 0)──> state_1 ──transition──> ... ──> state_C
  (P,N)         scalar decay               (P,N)                    (P,N)
```

| Đại lượng | Recurrent thuần | Chunked |
|---|---|---|
| Sequential steps | $T$ (ví dụ 8192) | $C=T/Q$ (ví dụ 128 khi $Q=64$) |
| Mỗi step làm gì | update với 1 token | update với summary của Q tokens |
| Parallelism | khó | scan ngắn hơn $Q$ lần |

Kết quả là **đúng boundary state** sau khi đã tính mọi chunks trước đó — toán học tương đương recurrent thuần.

### 6.4 Left factors: boundary state → chunk outputs

Boundary state đi vào chunk $j$ được project bởi local $C$ factors để tạo contribution từ history **trước chunk**:

$$
Y^{(j)} = Y_{\text{diag}}^{(j)} + Y_{\text{off}}^{(j)}
$$

| Thành phần | Nguồn | Shape | Ý nghĩa |
|---|---|---|---|
| $Y_{\text{diag}}^{(j)}$ | tokens trong chunk $j$ | $(Q,P)$ | intra-chunk |
| $Y_{\text{off}}^{(j)}$ | boundary state từ chunks $<j$ | $(Q,P)$ | inter-chunk — history trước chunk |

**Tóm tắt 4 bước — phải thuộc:**

```text
1. local inputs  ──quadratic dual──> intra-chunk outputs   (Y_diag)
2. local inputs  ──right factor───> chunk-final state contribution
3. chunk states  ──short scan─────> true boundary states    (center)
4. boundary state──left factor────> inter-chunk outputs     (Y_off)

Tổng: Y = Y_diag + Y_off  — mỗi chunk song song ở bước 1,2,4; chỉ bước 3 là scan ngắn.
```

### 6.5 Complexity đúng ngữ cảnh — công thức nào có $T$, có $N$?

Với state dimension $N$, head width $P$ và chunk length $Q$ cùng bậc, đặc biệt $N=P=Q$, paper cho block SSD training:[^dao-gu-2024]

| Đại lượng | Công thức | Giải thích shape |
|---|---|---|
| Training FLOPs | $O(TN^2)$ | mỗi token: work $O(N^2)$ do matmul với state $(P,N)$ |
| Activation memory | $O(TN)$ | lưu $A,B,C,X$ mỗi token — không lưu $T\times T$ |
| Recurrent inference state | $O(N^2)$ entries/head khi $P=N$ | state $(N,N)$ — cố định |
| Recurrent inference FLOPs/token/head | $O(N^2)$ | update $(N,N)$ state |

**Đừng suy rộng sai:**

- Các biểu thức này không nói wall-clock luôn nhanh hơn attention — kernel, precision, sequence length, batch size, hardware và data layout vẫn quyết định.
- `Linear in T` cho full-sequence work không có nghĩa mỗi token miễn phí — vẫn $O(N^2)$ mỗi token.

## 7. Lab 2 — chunked SSD reference (4 bước tường minh)

Đây là phiên bản học tập dựa trên self-contained algorithm của primary source. Nó dùng `A` như **log-transition** (nên transition thực là $\exp(A_t)$ với $A_t\le 0$ để decay). Cần cài `einops` (`pip install einops`).

```python
import torch
import torch.nn.functional as F
from einops import rearrange


def segsum(x):
    """
    exp(segsum(log_a)) builds a causal 1-SS matrix.
    x: (..., T) — log-transitions
    returns: (..., T, T) — segment sums, upper triangle = -inf
    """
    T = x.size(-1)
    prefix = torch.cumsum(x, dim=-1)  # (..., T) — prefix sum của log a
    # segment_sum[t,i] = prefix[t] - prefix[i] = sum_{r=i+1}^{t} log_a[r] (khi i<t)
    segment_sum = prefix[..., :, None] - prefix[..., None, :]
    causal = torch.tril(torch.ones(T, T, device=x.device, dtype=torch.bool))
    return segment_sum.masked_fill(~causal, -torch.inf)


def ssd_chunked(X, A, B, C, chunk_len=64, initial_state=None):
    """
    Chunked SSD — 4 bước tường minh.
    Shapes:
      X: [B, T, H, P]          — sequence input
      A: [B, T, H]             — log-transition (≤0 để decay)
      B: [B, T, H, N]          — expansion
      C: [B, T, H, N]          — contraction
      chunk_len: Q             — độ dài chunk (T phải chia hết)
      returns: Y [B, T, H, P], final_state [B, H, P, N]
    """
    assert X.dtype == A.dtype == B.dtype == C.dtype
    assert X.shape[1] % chunk_len == 0

    # Chia T thành (C, Q): [B, T, ...] → [B, C, Q, ...]
    X, A, B, C = [
        rearrange(t, "b (c l) ... -> b c l ...", l=chunk_len)
        for t in (X, A, B, C)
    ]
    # A: [B, C, Q, H] → [B, H, C, Q] để cumsum theo Q
    A = rearrange(A, "b c l h -> b h c l")
    A_prefix = torch.cumsum(A, dim=-1)  # (B,H,C,Q) — prefix trong chunk

    # ── 1) Diagonal blocks: intra-chunk quadratic dual ──
    # L: (B,H,C,Q,Q) — local mask trong mỗi chunk
    L = torch.exp(segsum(A))
    # Y_diag: (B,C,Q,H,P) — batched matmul trong chunk
    Y_diag = torch.einsum(
        "bclhn,bcshn,bhcls,bcshp->bclhp", C, B, L, X
    )

    # ── 2) Right factors: mỗi chunk → final-state contribution ──
    # decay_to_end: (B,H,C,Q) — decay từ position l đến cuối chunk
    decay_to_end = torch.exp(A_prefix[..., -1:] - A_prefix)
    # chunk_states: (B,C,H,P,N) — summary của mỗi chunk
    chunk_states = torch.einsum(
        "bclhn,bhcl,bclhp->bchpn", B, decay_to_end, X
    )

    # ── 3) Center factors: recurrence across chunk boundaries ──
    if initial_state is None:
        initial_state = torch.zeros_like(chunk_states[:, :1])  # (B,1,H,P,N)
    # state_inputs: (B, C+1, H, P, N) — prepend initial state
    state_inputs = torch.cat([initial_state, chunk_states], dim=1)
    # chunk_log_decay: (B,H,C) — tổng log decay của mỗi chunk
    chunk_log_decay = A_prefix[..., -1]
    # chunk_L: (B,H,C+1,C+1) — inter-chunk transition matrix
    chunk_L = torch.exp(segsum(F.pad(chunk_log_decay, (1, 0))))
    # boundary: (B, C+1, H, P, N) — true boundary states
    boundary = torch.einsum("bhzc,bchpn->bzhpn", chunk_L, state_inputs)
    states_in, final_state = boundary[:, :-1], boundary[:, -1]
    # states_in: (B,C,H,P,N) — state đầu mỗi chunk
    # final_state: (B,H,P,N) — state cuối cùng

    # ── 4) Left factors: incoming boundary state → outputs ──
    # decay_from_start: (B,H,C,Q) — decay từ đầu chunk đến position l
    decay_from_start = torch.exp(A_prefix)
    # Y_off: (B,C,Q,H,P) — contribution từ history trước chunk
    Y_off = torch.einsum(
        "bclhn,bchpn,bhcl->bclhp", C, states_in, decay_from_start
    )

    # Tổng hợp: Y = Y_diag + Y_off
    Y = rearrange(Y_diag + Y_off, "b c l h p -> b (c l) h p")
    return Y, final_state
```

**Kiểm tra với recurrent reference — phải khớp:**

```python
torch.manual_seed(1)
dtype = torch.float64
B, T, H, P, N = 2, 16, 2, 4, 3

X = torch.randn(B, T, H, P, dtype=dtype)          # (2,16,2,4)
# Negative log-transition → decay in (0,1] khi exp
A = -F.softplus(torch.randn(B, T, H, dtype=dtype))  # (2,16,2) ≤ 0
B_ = torch.randn(B, T, H, N, dtype=dtype)          # (2,16,2,3)
C_ = torch.randn(B, T, H, N, dtype=dtype)          # (2,16,2,3)

Y_chunk, final_state = ssd_chunked(X, A, B_, C_, chunk_len=4)
Y_rec = ssd_recurrent(X, torch.exp(A), B_, C_)  # a = exp(A)

torch.testing.assert_close(Y_chunk, Y_rec, rtol=1e-9, atol=1e-9)
print(f"✓ Chunked == Recurrent | Y {Y_chunk.shape} | final_state {final_state.shape}")
# Kỳ vọng: Y (2,16,2,4), final_state (2,2,4,3)
# Thử chunk_len ∈ {1,2,4,8,16} — mọi giá trị phải cho cùng Y
```

> [!warning] Reference, không phải production kernel
> `segsum` materialize local matrices và code giả định length chia hết cho `chunk_len`. Production cần fused kernels, numerical-stability handling, backward optimization, variable lengths, mixed precision và layout tuning. **Không benchmark code sư phạm này rồi kết luận về Mamba-2 kernel.**

## 8. Từ SSD layer đến Mamba-2 block — thêm gì ngoài recurrence?

SSD chỉ định core sequence transformation (công thức $S_t = a_t S_{t-1}+x_t b_t^{\top}$). Mamba-2 block thêm `projections`, `local convolution`, `gate`, `normalization` và `output projection`.

**Data flow ở mức khái niệm — nhìn shape chảy:**

```text
                              ┌────────> z ──SiLU──┐
input u ──parallel projection─┼────────> X ─conv───┼─> SSD ─> gate(⊙) ─> norm ─> out proj ─> output
  (B,T,D)                     ├────────> A (log)   │
                              ├────────> B         │
                              └────────> C         │
```

Viết gọn (mỗi dòng là một phép biến đổi):

$$
\begin{aligned}
(X,z,A,B,C)&=\operatorname{InputProjection}(u),\\
X_c&=\operatorname{DepthwiseConv1D}(X),\\
Y&=\operatorname{SSD}(A,B,C,X_c),\\
Y_g&=Y\odot\operatorname{SiLU}(z),\\
Y_n&=\operatorname{Norm}(Y_g),\\
\operatorname{out}&=W_o\,Y_n.
\end{aligned}
$$

Giải từng dòng:

| Bước | Input shape | Output shape | Ý nghĩa |
|---|---|---|---|
| `InputProjection` | $u$ `(B,T,D)` | $X$ `(B,T,H,P)`, $z$ `(B,T,H,P)`, $A$ `(B,T,H)`, $B/C$ `(B,T,1,N)` | tạo mọi branches song song |
| `DepthwiseConv1D` | $X$ `(B,T,H,P)` | $X_c$ `(B,T,H,P)` | trộn local neighbors — mỗi head conv riêng |
| `SSD` | $X_c,A,B,C$ | $Y$ `(B,T,H,P)` | sequence mixer chính |
| `Gate` | $Y$ + $z$ | $Y_g$ `(B,T,H,P)` | $Y\odot \operatorname{SiLU}(z)$ — channel-wise modulation |
| `Norm` | $Y_g$ | $Y_n$ | GroupNorm/RMSNorm trước output |
| `OutProj` | $Y_n$ | `out` `(B,T,D)` | về lại model dimension |

### 8.1 Khác biệt quan trọng với Mamba-1 — vì sao Mamba-2 parallel hơn?

Trong **Mamba-1**, $A,B,C$ được derive **sau** initial projected stream $X$ — tạo dependency:

```text
Mamba-1:  u → X → (từ X sinh ra A,B,C) → SSD    — sequential
Mamba-2:  u → (X, A, B, C) song song → SSD       — parallel
```

Mamba-2 tạo $A,B,C,X$ song song trực tiếp từ block input $u$, gần với cách attention tạo $Q/K/V$ cùng lúc. Paper nêu hai lợi ích: block đơn giản hơn và **phù hợp hơn với standard tensor-parallel sharding** (không cần gather $X$ trước khi tính $A,B,C$).[^dao-gu-2024]

### 8.2 Local convolution và gate — không xuất phát từ duality

- `Depthwise Conv1D` trộn local neighboring tokens trên $X$ branch **trước** SSD — mỗi head/channel conv riêng, kernel nhỏ (ví dụ 4).
- `Gate` dùng projected branch $z$ để modulate SSD output: $Y_g = Y \odot \operatorname{SiLU}(z)$ — elementwise, shape `(B,T,H,P)` giữ nguyên.
- Đây là các thành phần của **Mamba-2 block**, không xuất phát từ duality equation đơn thuần — đừng nhầm chúng là hệ quả toán học của $L\circ QK^{\top}$.

### 8.3 Extra normalization — vì sao thêm?

Mamba-2 thêm normalization **ngay trước output projection**, sau multiplicative gate. Paper báo rằng thay đổi này **giảm instabilities trong preliminary larger-model experiments** — author-reported design evidence, không phải theorem rằng mọi SSM phải dùng đúng normalization này.[^dao-gu-2024]

### 8.4 Multi-input SSM head pattern — nhiều $X$ heads, share $B,C$

Mamba-2 thường có nhiều $X$ heads nhưng share $B,C$ theo group:

$$
X:(T,H,P),\quad A:(T,H),\quad B,C:(T,1,N)
$$

ở pattern share hoàn toàn, hoặc nhiều groups trong `grouped-input SSM`. Paper gọi analogy tương ứng là `multi-value attention`. Ví dụ: $H=8$ heads của $X$ nhưng chỉ 1 cặp $B,C$ chung — tiết kiệm parameters và cho phép `tensor parallelism` tốt hơn. **Đừng nhầm với MQA/GQA** optimization của ordinary attention: đây là vocabulary chuyển qua duality để mô tả parameter sharing; Mamba-2 không lưu ordinary shared-KV cache.[^dao-gu-2024]

### 8.5 Projection skeleton — đọc shapes

Code dưới chỉ minh họa parallel projections; nó **không phải** Mamba-2 implementation hoàn chỉnh (thiếu conv, SSD, gate, norm):

```python
import torch
from torch import nn


class Mamba2ProjectionSkeleton(nn.Module):
    """Chỉ minh họa parallel projections — không phải full block."""

    def __init__(self, d_model, n_heads, d_head, d_state):
        super().__init__()
        inner = n_heads * d_head  # tổng chiều của X
        self.n_heads = n_heads
        self.d_head = d_head
        self.d_state = d_state

        # Pedagogical separate layers; production có thể fuse chúng.
        self.to_x = nn.Linear(d_model, inner, bias=False)   # (D → H*P)
        self.to_z = nn.Linear(d_model, inner, bias=False)   # (D → H*P) gate branch
        self.to_a = nn.Linear(d_model, n_heads, bias=True)  # (D → H) log-decay
        self.to_b = nn.Linear(d_model, d_state, bias=False) # (D → N) shared B
        self.to_c = nn.Linear(d_model, d_state, bias=False) # (D → N) shared C

    def forward(self, u):
        """
        u: (B, T, D) — block input
        returns: x (B,T,H,P), z (B,T,H,P), log_a (B,T,H), b/c (B,T,1,N)
        """
        B, T, _ = u.shape
        x = self.to_x(u).view(B, T, self.n_heads, self.d_head)  # (B,T,H,P)
        z = self.to_z(u).view(B, T, self.n_heads, self.d_head)  # (B,T,H,P)
        log_a = -F.softplus(self.to_a(u))  # (B,T,H) ≤ 0 → exp → (0,1]
        b = self.to_b(u)[:, :, None, :]    # (B,T,1,N) — broadcast over heads
        c = self.to_c(u)[:, :, None, :]    # (B,T,1,N)
        return x, z, log_a, b, c


# Ví dụ shape:
m = Mamba2ProjectionSkeleton(d_model=256, n_heads=8, d_head=32, d_state=64)
u = torch.randn(2, 16, 256)  # (B=2, T=16, D=256)
x, z, log_a, b, c = m(u)
print(f"x {x.shape}, z {z.shape}, log_a {log_a.shape}, b {b.shape}")
# x (2,16,8,32), z (2,16,8,32), log_a (2,16,8), b (2,16,1,64)
```

Production Mamba-2 còn có parameterization của continuous/discretized SSM quantities, convolution state cho decode, grouped heads, normalization details và optimized kernels. Skeleton chỉ làm rõ rằng **branches được tạo song song từ $u$** — khác Mamba-1.

## 9. Training, prefill và decode — ba chế độ khác nhau

### 9.1 Training / full-sequence prefill — mọi tokens đã biết

Mọi tokens đã biết, nên chunked SSD khai thác `parallel matmul` bên trong chunks. Gradient vẫn backpropagate qua toàn transformation — `chunked` ở đây là **computational decomposition** (cách chia để tính nhanh), không có nghĩa detach state hoặc truncated BPTT (cắt gradient).

| Chế độ | Input | Computation | State |
|---|---|---|---|
| Training | toàn sequence $T$ đã biết | chunked: batched matmul + short scan | tính từ đầu, không cache |
| Prefill | prompt $S$ đã biết | tương tự training — chunked parallel | tạo initial state cho decode |

### 9.2 Autoregressive decode — sinh từng token, state cố định

Mỗi token mới update:

```text
token mới ──> 1. conv state (cho Depthwise Conv1D)  shape (kernel_size, P) per head
          ──> 2. SSM state S_t = a_t S_{t-1} + x_t b_t^T  shape (P,N) per head
          ──> 3. output y_t = S_t c_t              shape (P,) per head
```

| State | Shape mỗi layer/head | Tăng theo $T$? |
|---|---|---|
| SSM state $S_t$ | $(P,N)$ — ví dụ $(64,64)=4096$ số | Không |
| Conv state | $(W,P)$ — $W$ = kernel width | Không |
| **Tổng decode state** | $O(H\cdot P\cdot N)$ | **Không** |

Điều này khác attention `KV cache`, vốn thêm $K/V$ entries theo token:

| Cơ chế | Decode state | Tăng theo $S$? | Shape ví dụ ($S=8192$) |
|---|---|---|---|
| Softmax attention | $S$ entries `(S, d_k)+(S, d_v)` | Có — $O(S)$ | $8192\times 128 = 1M$ số/head |
| SSD recurrent | 1 matrix $(P,N)$ | Không — $O(1)$ | $64\times 64 = 4096$ số/head |

Tuy nhiên end-to-end memory vẫn gồm model weights, activations/buffers, batching metadata và mọi attention layers nếu architecture là hybrid (nhiều model thực tế là hybrid SSM + attention).

### 9.3 Không trộn lẫn các complexity statements — đọc kỹ

| Câu nói | Đúng | Sai nếu hiểu thành |
|---|---|---|
| "Linear in $T$" | full-sequence SSD work $O(TN^2)$ | mỗi token miễn phí |
| "Fixed-state decode" | state shape không tăng | model nhớ vô hạn / lossless |
| "No growing KV cache" trong pure SSD layer | pure layer không có KV cache | toàn hybrid model không có KV cache (có thể có ở attention layers) |
| FlashAttention giảm IO/memory | đúng — vẫn exact softmax semantics | SSD thay đổi semantics — không so sánh trực tiếp |

## 10. Parallelism trong Mamba-2 — ba loại, ba mục tiêu

### 10.1 Tensor parallelism: split feature/head dimensions

`Tensor parallelism` (`TP`) chia một layer qua nhiều devices (GPUs). Với Mamba-1, vì $A,B,C$ phụ thuộc vào sharded $X_c$, shards cần gom $X_c$ trước khi derive parameters — tạo thêm synchronization.

Với Mamba-2, mỗi shard project local $X,z,A,B,C$ trực tiếp từ $u$, giữ local SSM heads, rồi chỉ combine sau output projection:[^dao-gu-2024]

```text
shared input u  (B,T,D) — replicated hoặc sharded theo sequence
   ├─ shard 0: local proj → local conv → local SSD (heads 0..H/2-1) → local norm → partial output (B,T,D/2)
   └─ shard 1: local proj → local conv → local SSD (heads H/2..H-1) → local norm → partial output (B,T,D/2)
                                                        │
                                          one output all-reduce → full output (B,T,D)
```

Paper's per-block analysis:

| Architecture | Collectives per block | Lý do |
|---|---|---|
| Mamba-1 adaptation | **2** all-reduce | 1 để gather $X_c$ trước khi tính $A,B,C$ + 1 output all-reduce |
| **Mamba-2** | **1** output all-reduce | parallel projections — mỗi shard tự tính local $A,B,C$ |
| Attention / MLP TP block | 1 output all-reduce | tương tự Mamba-2 |

**Lưu ý:** GroupNorm groups được chọn tương thích TP degree để normalization local không thêm communication — ví dụ $H=8$, TP=4 → mỗi shard $2$ heads, GroupNorm với $G=8$ groups vẫn local.

Đây là **communication-count analysis** (đếm số lần giao tiếp), không phải end-to-end scaling benchmark trên mọi cluster. Actual speedup phụ thuộc interconnect, batch size, sequence length.

### 10.2 Sequence parallelism cho residual/norm — split sequence axis

Theo usage kiểu Megatron, `sequence parallelism` có thể split activations dọc sequence cho residual và normalization, phối hợp `reduce-scatter`/`all-gather` với TP. Vì Mamba-2 giữ residual/norm structure tương tự Transformer, paper nói kỹ thuật này áp dụng **mà không cần thay đổi cơ bản**.[^dao-gu-2024]

| Technique | Split axis | Communication chính | Mục tiêu |
|---|---|---|---|
| Tensor parallelism | heads/features/weights trong layer | output all-reduce | layer quá lớn cho một device |
| Sequence parallelism (residual/norm) | sequence axis của replicated activations | reduce-scatter / all-gather | giảm activation duplication |

Tên gọi trong hệ sinh thái có thể khác giữa frameworks (Megatron gọi là "sequence parallelism", vLLM gọi khác) — luôn kiểm tra tensor nào thực sự được shard.

### 10.3 Context parallelism: split token-mixing sequence — truyền state

Paper cũng dùng `sequence/context parallelism` cho chính token mixer. Mỗi worker giữ một contiguous chunk:

```text
worker 0: chunk 0 [0, Q)      initial state 0  ──> final state 0 ──┐
                                                                   │ send (P,N) state
worker 1: chunk 1 [Q, 2Q)     initial state 0' ──> final state 1 ──┤
                                                                   │ send
worker 2: chunk 2 [2Q, 3Q)    initial state 1' ──> final state 2 ──┘
```

Đây là **distributed version của block SSD decomposition**. Mỗi chunk output gồm local contribution + contribution từ incoming state.

| Cơ chế | Communication pattern | Bandwidth scaling |
|---|---|---|
| SSM context parallelism | truyền recurrent state `(P,N)` giữa neighbors | **tuyến tính** theo số workers — mỗi boundary một state |
| Full attention context parallelism | mỗi query block cần tương tác với key blocks khác | **quadratic** query–key block interactions — có thể cần ring/all-to-all |

Với SSM, interface giữa neighboring chunks là recurrent state — nhỏ và cố định. Với full attention, mỗi query block cần scores với mọi key block. Paper mô tả communication bandwidth tăng tuyến tính theo số workers cho SSM thay vì quadratic.[^dao-gu-2024]

> [!note] Parallelism không xóa dependency
> Boundary state của chunk sau **vẫn phụ thuộc** chunks trước về mặt toán học. Parallel algorithm có thể tính local summaries trước rồi scan/combine summaries, nhưng causal dependency tồn tại — không thể tính chunk 2 đúng nếu chưa biết state sau chunk 1.

### 10.4 Ba khái niệm dễ nhầm — tóm tắt

| Technique | Split axis / chức năng chính | Communication chính | Mục tiêu |
|---|---|---|---|
| **Tensor parallelism** | heads/features/weights trong layer | output all-reduce | layer quá lớn cho một device |
| **Sequence parallelism** cho residual/norm | sequence axis của replicated activations | reduce-scatter / all-gather | giảm activation duplication |
| **Context parallelism** cho SSM mixer | contiguous token chunks | recurrent boundary states `(P,N)` | xử lý context rất dài ($S$ lớn) |

### 10.5 Variable-length packed sequences — chặn state leak

Có thể pack nhiều examples (nhiều documents) thành một long stream để tận dụng GPU, nhưng phải chặn state leak qua boundary (không để document sau đọc state của document trước).

Với transition convention của paper, đặt transition factor ở boundary bằng 0 sẽ reset recurrence:

$$
S_t = 0\cdot S_{t-1} + x_t b_t^{\top} = x_t b_t^{\top}
$$

Khi dùng log-transition $A_t$, không nên biểu diễn reset bằng một finite log gần 0 rồi giả định exact reset (vì $\exp(-\infty)=0$ mới đúng) — production kernel thường cần boundary/reset handling rõ ràng (mask hoặc flag). Cần test rằng thay đổi example trước không làm đổi output example sau.

**Test packed isolation (gợi ý):**

```python
# Pack [doc1 (3 tokens) | doc2 (4 tokens)] thành 7 tokens
# Đặt a[3] = 0 (boundary giữa doc1 và doc2) → state reset
# Kiểm tra: đổi tokens của doc1 không ảnh hưởng outputs của doc2 sau reset
```

## 11. Benchmark / Trade-offs — đọc đúng số, không suy rộng

### 11.1 Điều được primary paper hỗ trợ (có evidence)[^dao-gu-2024]

- SSM transformation tương ứng với semiseparable matrix transformation.
- Scalar-identity SSM và 1-semiseparable structured masked attention có cùng linear/quadratic forms (duality).
- Block SSD algorithm kết hợp intra-chunk matmul với inter-chunk state scan.
- Mamba-2 dùng parallel parameter projections, multi-input/grouped head patterns và extra normalization.
- Architecture hỗ trợ Transformer-style TP với **một output all-reduce** theo per-block analysis.
- Context parallelism có thể truyền recurrent states giữa contiguous chunks.

### 11.2 Điều không nên suy rộng (dễ hiểu sai)

| Suy rộng sai | Vì sao sai |
|---|---|
| Duality chứng minh SSD tương đương standard softmax attention | SSD không có softmax, không tương đương retrieval behavior |
| Linear asymptotic scaling bảo đảm nhanh hơn ở mọi $T$/hardware | Wall-clock phụ thuộc kernel, precision, $T$, batch, hardware, layout |
| Fixed-size state bảo đảm arbitrary exact recall | Bounded state không bảo đảm lossless — có capacity limit |
| Một kernel benchmark đại diện end-to-end serving | Kernel speed ≠ model speed — còn projections, norms, communication |
| Pure Mamba-2 result chứng minh hybrid attention vô ích | Chính paper báo hybrid attention cải thiện một số cấu hình được test |

### 11.3 So sánh nhanh — ba cột, đọc shape

| Property | Full softmax attention | Recurrent SSM/SSD | Chunked SSD training |
|---|---|---|---|
| History representation at decode | per-token KV entries `(S, d)` | fixed-size state `(P,N)` | dùng recurrent state khi decode |
| Token-addressable | có — query chấm từng token | không trực tiếp — đọc aggregated state | không thay semantics SSD |
| Full-sequence interaction work | quadratic theo $T$ — $O(T^2)$ | linear theo $T$ — $O(T)$, recurrence/scan | linear theo $T$ với local matmuls $O(TN^2)$ |
| Training hardware pattern | large matmuls $(S,S)$ | scan khó tối ưu hơn (sequential) | batched local matmuls $(Q,Q)$ + short scan $(C)$ |
| Long-range interface | pairwise token scores $(T,T)$ | compressed state $(P,N)$ | compressed chunk-boundary state $(P,N)$ |
| Decode state growth | $O(S)$ — tăng | $O(1)$ — cố định | $O(1)$ khi decode |

## 12. Xác minh trước khi benchmark — 4 tests phải pass

> [!warning] Lab này chỉ chứng minh semantics của toy SSD
> Full Mamba-2 còn `depthwise conv` state, `grouped heads`, `normalization` và `fused kernels`. Các test dưới không chứng minh parity với full Mamba-2 hay quality — chỉ chứng minh **recurrent == quadratic == chunked** và causality.

```python
import torch
import torch.nn.functional as F


@torch.inference_mode()
def test_recurrent_equals_quadratic():
    """Test 1: recurrent và quadratic cho cùng kết quả (duality đúng)."""
    torch.manual_seed(0)
    B, T, H, P, N = 2, 7, 3, 4, 5
    x = torch.randn(B, T, H, P, dtype=torch.float64)
    a = torch.sigmoid(torch.randn(B, T, H, dtype=torch.float64))
    b = torch.randn(B, T, H, N, dtype=torch.float64)
    c = torch.randn(B, T, H, N, dtype=torch.float64)

    y_rec = ssd_recurrent(x, a, b, c)
    y_quad = ssd_quadratic(x, a, b, c)

    torch.testing.assert_close(y_rec, y_quad, rtol=1e-10, atol=1e-10)
    assert y_rec.shape == (B, T, H, P)
    print(f"✓ Test 1 passed: recurrent == quadratic, shape {y_rec.shape}")


@torch.inference_mode()
def test_causality():
    """Test 2: đổi future không ảnh hưởng past (causal isolation)."""
    torch.manual_seed(0)
    B, T, H, P, N = 2, 7, 3, 4, 5
    x = torch.randn(B, T, H, P, dtype=torch.float64)
    a = torch.sigmoid(torch.randn(B, T, H, dtype=torch.float64))
    b = torch.randn(B, T, H, N, dtype=torch.float64)
    c = torch.randn(B, T, H, N, dtype=torch.float64)
    y_rec = ssd_recurrent(x, a, b, c)

    k = 4
    x_changed = x.clone()
    x_changed[:, k:] += 100.0  # perturb mạnh future
    y_changed = ssd_recurrent(x_changed, a, b, c)

    torch.testing.assert_close(y_rec[:, :k], y_changed[:, :k], rtol=1e-10, atol=1e-10)
    print(f"✓ Test 2 passed: future perturbation (k={k}) does not affect past")


@torch.inference_mode()
def test_chunked_invariance():
    """Test 3: chunked với mọi chunk_len cho cùng kết quả."""
    torch.manual_seed(1)
    B, T, H, P, N = 2, 16, 2, 4, 3
    X = torch.randn(B, T, H, P, dtype=torch.float64)
    A = -F.softplus(torch.randn(B, T, H, dtype=torch.float64))
    B_ = torch.randn(B, T, H, N, dtype=torch.float64)
    C_ = torch.randn(B, T, H, N, dtype=torch.float64)

    Y_ref = ssd_recurrent(X, torch.exp(A), B_, C_)
    for chunk_len in [1, 2, 4, 8, 16]:
        Y_chunk, _ = ssd_chunked(X, A, B_, C_, chunk_len=chunk_len)
        torch.testing.assert_close(Y_chunk, Y_ref, rtol=1e-9, atol=1e-9)
    print("✓ Test 3 passed: chunked invariant across chunk_len ∈ {1,2,4,8,16}")


@torch.inference_mode()
def test_state_shape_fixed():
    """Test 4: state shape cố định — không chứa T."""
    B, H, P, N = 2, 3, 4, 5
    # State shape chỉ phụ thuộc (B,H,P,N) — không phụ thuộc T
    for T in [7, 16, 128]:
        x = torch.randn(B, T, H, P, dtype=torch.float64)
        a = torch.sigmoid(torch.randn(B, T, H, dtype=torch.float64))
        b = torch.randn(B, T, H, N, dtype=torch.float64)
        c = torch.randn(B, T, H, N, dtype=torch.float64)
        y = ssd_recurrent(x, a, b, c)
        assert y.shape == (B, T, H, P), f"T={T}: shape {y.shape} != {(B,T,H,P)}"
    # State elements = B*H*P*N = 2*3*4*5 = 120 — giống nhau với mọi T
    state_elements = B * H * P * N
    assert state_elements == 120
    print(f"✓ Test 4 passed: state elements={state_elements} (fixed), T varies but state does not")


# Chạy tất cả — copy block này vào python và chạy
test_recurrent_equals_quadratic()
test_causality()
test_chunked_invariance()
test_state_shape_fixed()
```

**Cách đọc khi test fail:**

| Test fail | Triệu chứng | Check đầu tiên |
|---|---|---|
| Test 1 `recurrent != quadratic` | max error lớn | In `state` sau từng step vs `prefix` — write/read order sai? $a$ có đúng `(0,1)$? |
| Test 2 past đổi khi future đổi | causality broken | Loop có vô tình đọc `b`/`x` tương lai? `L` upper triangle có đúng 0? |
| Test 3 chỉ một số chunk_len fail | indexing bug | Kiểm tra `A_prefix`, `decay_to_end`, `chunk_L` padding |
| Test 4 shape sai | state chứa $T$ | `print(state.shape)` — phải là `(B,H,P,N)` không có $T$ |

Cả 4 tests phải pass trước khi đo benchmark — benchmark trên implementation sai là vô nghĩa.

## 13. Debug checklist — triệu chứng → nguyên nhân → check

### 13.1 Algebra và shapes

- [ ] $S_t$ có shape `[B, H, P, N]` — **không có $T$**.
- [ ] Current token write không bị nhân nhầm bởi $a_t$ — `a_t` chỉ nhân `S_{t-1}`, không nhân `x_t b_t^{\top}`.
- [ ] $L_{t,t}=1$ (empty product).
- [ ] $L_{t,i}=0$ khi $i>t$ (causal — upper triangle zero).
- [ ] Product cho old token $i$ chạy từ $i+1$ đến $t$ — không phải $i$ đến $t$.
- [ ] Recurrent và quadratic references match ở `float64` trước khi test `bf16`.

### 13.2 Chunking

- [ ] `chunk_len=1` vẫn match recurrent reference (edge case nhỏ nhất).
- [ ] Nhiều `chunk_len` khác nhau cho cùng output trong tolerance.
- [ ] `initial_state` có đúng shape `(B,H,P,N)` và được đưa vào chunk đầu.
- [ ] `final_state` match state của recurrent run sau token cuối.
- [ ] Không detach boundary state khi muốn full backpropagation — chunked là decomposition, không phải truncated BPTT.

### 13.3 Causality và packing

- [ ] Perturb future tokens không đổi prior outputs (Test 2).
- [ ] Reset boundary ($a=0$) ngăn cross-example leakage khi pack sequences.
- [ ] Padding tokens không update state ngoài ý muốn — mask $a$ và $x$ cho padding.

### 13.4 Numerical stability

- [ ] Transition parameterization không làm products explode — $a_t\in(0,1]$ toy, thực tế $A_t\le 0$ rồi $\exp$.
- [ ] `exp(cumulative log-transition)` được kiểm tra ở sequence dài ($T=8192$) — không overflow/underflow.
- [ ] Mixed-precision output được so với FP32/FP64 reference — tolerance nới lỏng có kiểm soát.
- [ ] Tolerance không bị đặt rộng đến mức che implementation bug — bắt đầu chặt (`1e-10`) rồi mới nới.

### 13.5 Distributed execution

- [ ] Mỗi TP shard giữ trọn local heads/state dimensions cần thiết — không shard trong $(P,N)$.
- [ ] Norm groups chia hết cho TP degree nếu dựa trên local GroupNorm.
- [ ] Chỉ count collective sau khi vẽ data dependency thực tế — không đếm thừa.
- [ ] Context chunks có đúng thứ tự causal khi truyền/combine states — worker 1 đợi state từ worker 0.

## 14. Bài tập — tự tay kiểm chứng

### Bài 1 — unroll bằng tay (5 phút)

Cho $a=[1,0.5,0.2]$ và $x=[2,4,10]$. Tính $h_0,h_1,h_2$, dựng matrix $L$, rồi kiểm tra $Lx$.

<details>
<summary>Đáp án</summary>

$$
h_0=2,\quad h_1=0.5\cdot 2+4=5,\quad h_2=0.2\cdot 5+10=11.
$$

$$
L=\begin{bmatrix}1&0&0\\0.5&1&0\\0.1&0.2&1\end{bmatrix},
\qquad Lx=[2,5,11]^{\top}.
$$

</details>

### Bài 2 — kiểm tra chunk invariance

Chạy Lab 2 với `T=16` và `chunk_len ∈ {1, 2, 4, 8, 16}`. Mọi output phải match recurrent reference (Test 3). Nếu chỉ một số chunk sizes fail, kiểm tra indexing ở `A_prefix`, padding boundary transition và incoming states.

### Bài 3 — visualize structured mask

Plot $L$ (heatmap $T\times T$) khi:

1. mọi $a_t=1$ → $L$ toàn 1 ở tam giác dưới (giống linear attention).
2. mọi $a_t=0.9$ → $L$ decay theo khoảng cách — xa thì nhạt.
3. một $a_k\approx 0$ → hàng sau $k$ gần như reset — cột trước $k$ nhạt.
4. $a_t$ thay đổi theo token → pattern input-dependent.

Giải thích: đường nào trong history được giữ, decay hoặc gần như reset.

### Bài 4 — capacity reasoning

Giữ $P$ cố định, tăng $N$ (ví dụ $N=4,16,64$) và đo khả năng khớp một synthetic associative-recall task (ví dụ: ghi $K$ cặp key→value, đọc lại). Đừng kết luận chỉ từ training loss — đo retrieval accuracy theo sequence length. Kết quả là experiment của bạn, không phải universal capacity theorem.

### Bài 5 — parallelism design

Với `n_heads=16`, `TP=4`, đề xuất cách shard heads và GroupNorm groups. Vẽ nơi diễn ra output all-reduce. Sau đó split sequence thành 8 context chunks và ghi shape của boundary state được truyền giữa workers (ví dụ: mỗi boundary là `(B, H/TP, P, N)` hay `(B, H, P, N)` tùy sharding).

## 15. Mental model cuối bài — 5 câu phải nhớ

> 1. **Recurrence:** SSD nén prefix vào $S_t = a_t S_{t-1} + x_t b_t^{\top}$ — state shape $(P,N)$ cố định, không có $T$.
> 2. **Matrix view:** Unroll recurrence tạo causal semiseparable transformation $M$ — mỗi entry $M_{t,i}=L_{t,i}(c_t^{\top}b_i)$.
> 3. **Duality:** Với scalar-identity transitions $A_t=a_t I$, $M=L\circ C B^{\top}$ có **structured attention-like quadratic form** và **exact recurrent form** — cùng kết quả, khác cách tính.
> 4. **Chunked training:** Diagonal blocks dùng local matmul $(Q,Q)$; off-diagonal blocks factor qua chunk-boundary states $(P,N)$ — 4 bước: diagonal / right / center / left.
> 5. **Mamba-2 systems design:** Parallel projections và local heads giúp TP cần **một output all-reduce** theo block analysis; long sequence có thể shard bằng state passing — bandwidth tuyến tính theo workers.

Bước tiếp theo: tự chạy hai labs (Test 1–4 phải pass), thêm gradient comparison giữa recurrent và chunked form (`loss.backward()` và so sánh `grad`), rồi đọc [Structured State Space Duality](structured-state-space-duality.md) và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) để đối chiếu concise concept notes với derivation chi tiết trong bài này. Sau đó xem [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md) để hiểu evidence thực nghiệm và giới hạn.

## Relationships

- **Depends on:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — fixed-state recurrence và reassociation là nền tảng để hiểu SSD.
- **Depends on:** [Self-attention computational profile](self-attention-computational-profile.md) — quadratic interaction và parallel training là baseline để so sánh.
- **Synthesizes:** [Structured State Space Duality](structured-state-space-duality.md) và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) thành một learning sequence có derivation và labs.
- **Evaluated by:** [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md) — nơi ghi các author-reported quality, recall và speed results cùng giới hạn evidence.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) — MLA giữ token-addressability với cache tăng theo $S$, khác với fixed-state của SSD.
- **Part of:** [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) — Stage 8 về fixed-state và long-context mixing.

## Evidence limits

Duality, semiseparable structure, complexity claims ($O(TN^2)$ FLOPs, $O(TN)$ memory, $O(N^2)$ state) và block SSD algorithm là primary-paper results từ Dao & Gu 2024, Sections 3–8 và self-contained algorithm trong `structure/code.py`[^dao-gu-2024]. Wall-clock gains phụ thuộc implementation, state size $N$, sequence length $T$, chunk length $Q$, precision (BF16/FP16), và accelerator — matrix formulation không establish quality parity với softmax attention hoặc mọi selective SSM. PyTorch labs, worked examples, benchmark tables và teaching sequence là **pedagogical synthesis** — toy code dùng `float64`/`einsum`/`for` loop để dễ đọc, không implement fused kernels, backward optimization, hay mixed-precision handling, và không dùng để suy ra quality hay speedup. Fixed state bảo đảm bounded state dimensions, không bảo đảm lossless memory, constant end-to-end latency, hay infinite usable context.

[^dao-gu-2024]: Tri Dao và Albert Gu, "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality," arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), đặc biệt Sections 3–8 và self-contained SSD algorithm trong `structure/code.py`.
