---
type: Synthesis
title: "SSD → Mamba-2: recurrence, duality, chunked training và parallelism — bài học cho người mới"
description: A beginner-first course from selective SSM recurrence through structured-attention duality and chunked SSD computation to the Mamba-2 block and its tensor/context parallelism.
tags: [ssd, mamba-2, ssm, recurrence, structured-attention, chunked-training, parallelism, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T05:29:20Z }
sources:
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# SSD → Mamba-2: recurrence, duality, chunked training và parallelism — bài học cho người mới

`Mamba-2` xây sequence mixer trên `Structured State Space Duality` (`SSD`): cùng một causal transformation có thể được tính như **recurrent state update** hoặc viết thành một **structured masked attention-like matrix**. Khi training, SSD chia sequence thành chunks: dùng matrix multiplication song song bên trong từng chunk và chỉ scan recurrent states ở mức chunk. Khi decode, model giữ một fixed-size state thay vì `KV cache` tăng theo context. Mamba-2 tiếp tục tổ chức projections, heads, normalization và sharding để block này phù hợp hơn với cách train Transformer ở quy mô lớn.[^dao-gu-2024]

> [!success] Mục tiêu
> Sau bài này, bạn có thể:
> 1. viết và unroll một `selective SSM recurrence`;
> 2. suy ra causal matrix $M$ từ recurrence;
> 3. giải thích `semiseparable structure` và duality với `structured masked attention`;
> 4. phân biệt recurrent, quadratic và chunked form;
> 5. implement và kiểm tra recurrent form = quadratic form bằng PyTorch;
> 6. mô tả bốn bước của block SSD algorithm;
> 7. đọc được data flow của một Mamba-2 block;
> 8. phân biệt `tensor parallelism`, `sequence parallelism` và `context parallelism`;
> 9. nêu đúng trade-off giữa fixed-state memory và token-addressable attention.

## 1. Prerequisites và bản đồ bài học

Nên học trước:

- [Attention: beginner's guide](attention-beginner-guide.md): Q/K/V, causal mask và multi-head attention;
- [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md): reassociation và matrix state;
- [Self-attention computational profile](self-attention-computational-profile.md): quadratic interaction và parallel training;
- [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md): khác biệt giữa training, prefill và decode.

Lộ trình của bài:

```text
recurrent SSM
    │ unroll theo thời gian
    ▼
causal semiseparable matrix
    │ scalar-identity transition
    ▼
structured masked attention-like form
    │ block decomposition
    ▼
chunked SSD training
    │ block + head + projection redesign
    ▼
Mamba-2 và distributed parallelism
```

> [!important] Hai tầng khái niệm
> `SSD` vừa là một **duality/framework** để nhìn SSM và structured attention, vừa dẫn tới một **hardware-oriented block algorithm**. `Mamba-2` là neural architecture sử dụng SSD layer; SSD không phải tên thay thế cho toàn bộ Mamba-2 block.

## 2. Từ recurrence đến fixed-size state

### 2.1 Scalar recurrence nhỏ nhất

Bắt đầu với:

$$
h_t=a_t h_{t-1}+x_t,
\qquad y_t=h_t.
$$

Ở mỗi token:

- $x_t$ ghi thông tin mới;
- $a_t$ quyết định state cũ được truyền qua bao nhiêu;
- nếu $a_t=1$, state cộng dồn toàn bộ history;
- nếu $0<a_t<1$, thông tin cũ decay theo khoảng cách;
- nếu $a_t$ phụ thuộc input, retention trở thành `selective`.

Unroll ba bước, với $h_{-1}=0$:

$$
\begin{aligned}
h_0 &= x_0,\\
h_1 &= a_1x_0+x_1,\\
h_2 &= a_2a_1x_0+a_2x_1+x_2.
\end{aligned}
$$

Cùng phép tính đó có matrix form:

$$
\begin{bmatrix}y_0\\y_1\\y_2\end{bmatrix}
=
\underbrace{
\begin{bmatrix}
1&0&0\\
a_1&1&0\\
a_2a_1&a_2&1
\end{bmatrix}}_{L=\operatorname{1SS}(a)}
\begin{bmatrix}x_0\\x_1\\x_2\end{bmatrix}.
$$

$L$ là causal: mọi phần tử phía trên diagonal bằng 0. Mỗi entry $L_{t,i}$ là tích transitions từ token $i$ đến token $t$:

$$
L_{t,i}=\prod_{r=i+1}^{t}a_r,\qquad i\le t,
$$

với empty product trên diagonal bằng 1. Paper gọi đây là `1-semiseparable` matrix và phép tính là `cumprodsum`.[^dao-gu-2024]

### 2.2 Vector input và matrix state

Một SSD head thực tế cần state chứa nhiều features. Dùng ký hiệu sư phạm:

| Tensor | Shape ở một head | Vai trò |
|---|---:|---|
| $x_t$ | $P$ | sequence input/value |
| $b_t$ | $N$ | expansion vector, tương tự key trong duality |
| $c_t$ | $N$ | contraction vector, tương tự query trong duality |
| $a_t$ | scalar | state transition/decay |
| $S_t$ | $P\times N$ | recurrent state |
| $y_t$ | $P$ | output |

Recurrence:

$$
S_t=a_tS_{t-1}+x_tb_t^\top,
\qquad
y_t=S_tc_t.
$$

`Outer product` $x_tb_t^\top$ mở rộng input vào state. $c_t$ co state trở lại output. Shape của $S_t$ là $P\times N$, không chứa sequence length $T$: đây là `fixed-state recurrence`.

Unroll:

$$
S_t=\sum_{i=0}^{t}
\left(\prod_{r=i+1}^{t}a_r\right)x_ib_i^\top.
$$

Sau đó:

$$
y_t
=\sum_{i=0}^{t}
\underbrace{\left(\prod_{r=i+1}^{t}a_r\right)}_{L_{t,i}}
\underbrace{(c_t^\top b_i)}_{\text{content interaction}}
x_i.
$$

Đây là chiếc cầu từ recurrence sang attention-like form.

> [!note] Convention
> Một số tài liệu đặt vectors theo hàng hoặc cột khác nhau. Khi đó bạn có thể thấy $b_tx_t^\top$ thay vì $x_tb_t^\top$. Ý nghĩa giống nhau nếu toàn bộ contractions và shapes nhất quán.

## 3. SSM là semiseparable matrix transformation

Với general SSM:

$$
h_t=A_th_{t-1}+B_tx_t,
\qquad y_t=C_t^\top h_t,
$$

unroll cho:

$$
y_t=\sum_{i=0}^{t}C_t^\top A_tA_{t-1}\cdots A_{i+1}B_i x_i.
$$

Vì vậy toàn sequence là $y=Mx$, với:

$$
M_{t,i}=C_t^\top A_tA_{t-1}\cdots A_{i+1}B_i,
\qquad i\le t.
$$

Paper chứng minh transformation của state-size $N$ tương ứng với một causal `N-semiseparable matrix`: các submatrices nằm trên hoặc dưới diagonal causal portion có rank không vượt quá $N$. `Sequentially semiseparable` (`SSS`) representation chính là factorization bằng $A,B,C$ ở trên.[^dao-gu-2024]

### 3.1 Tại sao low-rank off-diagonal blocks quan trọng?

Chọn một block output ở thời gian muộn và một block input ở thời gian sớm. Mọi influence từ block cũ sang block mới phải đi qua boundary state kích thước $N$. Do đó off-diagonal block factor qua một interface có rank bị chặn bởi $N$:

```text
earlier inputs ──> boundary state (N dimensions) ──> later outputs
```

Đây không chỉ là một mô tả toán học. Chính factorization này cho phép SSD:

1. tính local interactions bên trong chunk bằng matrix multiplication;
2. nén ảnh hưởng của chunk thành boundary state;
3. truyền boundary states qua một recurrence ngắn hơn;
4. bung state vào outputs của chunk sau.

### 3.2 Fixed state không phải token-addressable memory

Full softmax attention giữ K/V của từng token, nên query mới có thể chấm điểm từng vị trí. SSD gộp history qua state $S_t$ có shape cố định. Vì vậy:

- recurrent decode state không tăng theo $T$;
- nhưng không còn một slot độc lập cho mỗi token;
- state size $N$ là capacity bottleneck;
- bounded state không bảo đảm exact retrieval hoặc lossless long-context memory.

Đây là khác biệt nền tảng với [MLA](mla-token-addressable-memory-beginners-guide.md): MLA nén mỗi token nhưng cache vẫn có sequence axis; SSD bỏ sequence axis khỏi recurrent state.

## 4. Structured State Space Duality

### 4.1 Scalar-identity transition

SSD specialization đặt:

$$
A_t=a_tI.
$$

Khi đó products của transition matrices trở thành scalar product nhân identity, và matrix entry tách được:

$$
M_{t,i}=L_{t,i}(c_t^\top b_i).
$$

Gom toàn sequence:

$$
Y=\left(L\circ CB^\top\right)X.
$$

Theo vocabulary giống attention:

$$
Y=\left(L\circ QK^\top\right)V,
$$

với mapping:

| SSM/SSD | Structured masked attention analogy |
|---|---|
| $C$ | $Q$ |
| $B$ | $K$ |
| $X$ | $V$ |
| transition product $A_{t:i}$ | structured mask $L_{t,i}$ |
| state dimension $N$ | kernel feature dimension |

Dấu $\circ$ là elementwise product. $L$ không chỉ là binary causal mask; nó chứa input-dependent decay/selection qua products của $a_t$.[^dao-gu-2024]

### 4.2 Hai contraction orders, cùng kết quả

**Quadratic/attention-like order:**

1. tạo $G=CB^\top$ với shape $T\times T$;
2. tạo structured causal weights $M=L\circ G$;
3. tính $Y=MX$.

Cách này phơi bày pairwise token interactions nhưng materialize tensor quadratic theo $T$.

**Linear/recurrent order:**

1. update $S_t=a_tS_{t-1}+x_tb_t^\top$;
2. read $y_t=S_tc_t$.

Cách này không materialize $T\times T$, nhưng token recurrence thuần túy có sequential dependency và có thể không sử dụng GPU matrix units tốt bằng batched matmul.

`Duality` nghĩa là hai computational forms của **cùng transformation** trong SSD subset, không phải hai model gần giống nhau.

> [!warning] SSD không phải softmax attention
> $L\circ QK^\top$ không có row-wise `softmax`, và SSD dựa trên finite feature contraction. Standard softmax attention nói chung không thể reassociate thành fixed-size exact recurrence theo cách này. Vì vậy đừng suy ra SSD giữ nguyên semantics hoặc retrieval behavior của softmax attention.[^dao-gu-2024]

### 4.3 So với linear attention

Causal linear attention có thể xem như trường hợp $a_t=1$ cho mọi $t$, nên $L$ là all-ones lower-triangular causal mask. SSD tổng quát hóa mask đó bằng learned/input-dependent transition products:

$$
\text{linear attention: }L_{t,i}=1
\quad\longrightarrow\quad
\text{SSD: }L_{t,i}=\prod_{r=i+1}^{t}a_r.
$$

Paper còn chứng minh: nếu một `structured masked attention` instance là bounded-order autoregressive process, mask của nó phải là semiseparable. Đây là theorem về structure cần cho bounded-order autoregression, không phải tuyên bố mọi efficient attention đều là Mamba-2.[^dao-gu-2024]

## 5. Lab 1 — chứng minh recurrent form = quadratic form

Code sau ưu tiên tính rõ ràng, không tối ưu speed. `a` được chọn trong $(0,1)$ để products ổn định và dễ hiểu.

```python
import torch


def ssd_recurrent(x, a, b, c):
    """
    x: [batch, length, heads, d_head=P]
    a: [batch, length, heads]          scalar transition
    b: [batch, length, heads, d_state=N]
    c: [batch, length, heads, d_state=N]
    returns y: [batch, length, heads, d_head]
    """
    batch, length, heads, d_head = x.shape
    d_state = b.shape[-1]
    state = x.new_zeros(batch, heads, d_head, d_state)
    outputs = []

    for t in range(length):
        # Old state decays; current token writes an outer product.
        state = (
            a[:, t, :, None, None] * state
            + torch.einsum("bhp,bhn->bhpn", x[:, t], b[:, t])
        )
        # c_t contracts the state dimension N.
        y_t = torch.einsum("bhpn,bhn->bhp", state, c[:, t])
        outputs.append(y_t)

    return torch.stack(outputs, dim=1)


def one_ss_mask(a):
    """Build L[t, i] = product_{r=i+1..t} a[r]; reference only."""
    batch, length, heads = a.shape
    L = a.new_zeros(batch, heads, length, length)

    for t in range(length):
        L[:, :, t, t] = 1.0
        running = torch.ones_like(a[:, 0])
        for i in range(t - 1, -1, -1):
            running = running * a[:, i + 1]
            L[:, :, t, i] = running
    return L


def ssd_quadratic(x, a, b, c):
    """Materialize the structured attention-like matrix; reference only."""
    L = one_ss_mask(a)                              # [B,H,T,T]
    gram = torch.einsum("bthn,bshn->bhts", c, b) # c_t^T b_s
    M = L * gram                                    # structured causal weights
    return torch.einsum("bhts,bshp->bthp", M, x)


torch.manual_seed(0)
dtype = torch.float64
B, T, H, P, N = 2, 7, 3, 4, 5
x = torch.randn(B, T, H, P, dtype=dtype)
a = torch.sigmoid(torch.randn(B, T, H, dtype=dtype))
b = torch.randn(B, T, H, N, dtype=dtype)
c = torch.randn(B, T, H, N, dtype=dtype)

y_rec = ssd_recurrent(x, a, b, c)
y_quad = ssd_quadratic(x, a, b, c)

torch.testing.assert_close(y_rec, y_quad, rtol=1e-10, atol=1e-10)
print("max error:", (y_rec - y_quad).abs().max().item())
```

### 5.1 Điều test này chứng minh và không chứng minh

Nó chứng minh implementation của hai algebraic forms nhất quán trong toy setup. Nó **không** chứng minh:

- implementation production có cùng numerical behavior ở BF16/FP16;
- chunked kernel nhanh hơn trên GPU của bạn;
- SSD đạt cùng quality với softmax attention;
- Mamba-2 block hoàn chỉnh chỉ gồm recurrence này.

### 5.2 Causality test

Output trước thời điểm $k$ không được đổi khi perturb future inputs:

```python
k = 4
x_changed = x.clone()
x_changed[:, k:] += 100.0

y_before = ssd_recurrent(x, a, b, c)
y_after = ssd_recurrent(x_changed, a, b, c)

torch.testing.assert_close(
    y_before[:, :k], y_after[:, :k], rtol=1e-10, atol=1e-10
)
```

Nếu test fail, thường có lỗi index trong transition product hoặc causal mask.

## 6. Vì sao cần chunked SSD training?

Ta có một tension:

| Form | Ưu điểm | Nhược điểm |
|---|---|---|
| Recurrent | work linear theo $T$, fixed-size decode state | token-level dependency; GPU utilization khó hơn |
| Quadratic | matrix multiplication song song, đơn giản | materialize $T\times T$ và quadratic work |
| Chunked SSD | local matmul + short state scan | implementation phức tạp hơn; cần chọn chunk size |

SSD algorithm partition $T$ tokens thành $C=T/Q$ chunks, mỗi chunk dài $Q$. Semiseparable matrix $M$ trở thành block lower-triangular matrix.

### 6.1 Diagonal blocks: intra-chunk

$M^{(j,j)}$ chứa interactions giữa tokens cùng chunk $j$. Vì $Q$ nhỏ, tính block này bằng quadratic dual:

$$
Y_{\text{diag}}^{(j)}
=\left(L^{(j)}\circ C^{(j)}B^{(j)\top}\right)X^{(j)}.
$$

Mọi chunks có thể tính song song bằng batched matrix multiplication. Kết quả giả định state đầu chunk bằng 0.

### 6.2 Right factors: chunk input → chunk-final state

Mỗi chunk nén toàn bộ local inputs thành contribution vào final state:

```text
Q tokens in chunk j ──> one state contribution [P, N]
```

Đây là phần `B-block-factor` của low-rank off-diagonal blocks.

### 6.3 Center factors: inter-chunk recurrence

Scan qua $C=T/Q$ chunk states thay vì $T$ token states:

```text
state_0 ──transition──> state_1 ──transition──> ... ──> state_C
```

Sequential/scan length giảm từ $T$ xuống $T/Q$. Kết quả là đúng boundary state sau khi đã tính mọi chunks trước đó.

### 6.4 Left factors: boundary state → chunk outputs

Boundary state đi vào chunk $j$ được project bởi local $C$ factors để tạo contribution từ history trước chunk:

$$
Y^{(j)}=Y_{\text{diag}}^{(j)}+Y_{\text{off}}^{(j)}.
$$

Bốn bước cần nhớ:

```text
1. local inputs  ──quadratic dual──> intra-chunk outputs
2. local inputs  ──right factor───> chunk-final state contribution
3. chunk states  ──short scan─────> true boundary states
4. boundary state──left factor────> inter-chunk outputs
```

### 6.5 Complexity đúng ngữ cảnh

Với state dimension $N$, head width $P$ và chunk length $Q$ cùng bậc, đặc biệt $N=P=Q$, paper cho block SSD training:

- $O(TN^2)$ FLOPs;
- $O(TN)$ activation memory;
- work chủ yếu là matrix multiplication;
- recurrent inference state có $O(N^2)$ entries trên mỗi head khi $P=N$;
- recurrent inference cần $O(N^2)$ FLOPs mỗi token trên mỗi head theo setup đó.[^dao-gu-2024]

Các biểu thức này không nói wall-clock luôn nhanh hơn attention. Kernel, precision, sequence length, batch size, hardware và data layout vẫn quyết định performance thực tế.

## 7. Lab 2 — chunked SSD reference

Đây là phiên bản học tập dựa trên self-contained algorithm của primary source. Nó dùng `A` như **log-transition**, nên transition thực là $\exp(A_t)$. Cần cài `einops`.

```python
import torch
import torch.nn.functional as F
from einops import rearrange


def segsum(x):
    """exp(segsum(log_a)) builds a causal 1-SS matrix."""
    length = x.size(-1)
    prefix = torch.cumsum(x, dim=-1)
    segment_sum = prefix[..., :, None] - prefix[..., None, :]
    causal = torch.tril(
        torch.ones(length, length, device=x.device, dtype=torch.bool)
    )
    return segment_sum.masked_fill(~causal, -torch.inf)


def ssd_chunked(X, A, B, C, chunk_len=64, initial_state=None):
    """
    X: [batch, length, heads, d_head]
    A: [batch, length, heads]          log-transition
    B: [batch, length, heads, d_state]
    C: [batch, length, heads, d_state]
    """
    assert X.dtype == A.dtype == B.dtype == C.dtype
    assert X.shape[1] % chunk_len == 0

    # [batch, chunks, chunk_len, ...]
    X, A, B, C = [
        rearrange(t, "b (c l) ... -> b c l ...", l=chunk_len)
        for t in (X, A, B, C)
    ]
    A = rearrange(A, "b c l h -> b h c l")
    A_prefix = torch.cumsum(A, dim=-1)

    # 1) Diagonal blocks: intra-chunk quadratic dual.
    L = torch.exp(segsum(A))
    Y_diag = torch.einsum(
        "bclhn,bcshn,bhcls,bcshp->bclhp", C, B, L, X
    )

    # 2) Right factors: each chunk's final-state contribution.
    decay_to_end = torch.exp(A_prefix[..., -1:] - A_prefix)
    chunk_states = torch.einsum(
        "bclhn,bhcl,bclhp->bchpn", B, decay_to_end, X
    )

    # 3) Center factors: recurrence across chunk boundaries.
    if initial_state is None:
        initial_state = torch.zeros_like(chunk_states[:, :1])
    state_inputs = torch.cat([initial_state, chunk_states], dim=1)
    chunk_log_decay = A_prefix[..., -1]
    chunk_L = torch.exp(segsum(F.pad(chunk_log_decay, (1, 0))))
    boundary = torch.einsum("bhzc,bchpn->bzhpn", chunk_L, state_inputs)
    states_in, final_state = boundary[:, :-1], boundary[:, -1]

    # 4) Left factors: incoming boundary state -> outputs.
    decay_from_start = torch.exp(A_prefix)
    Y_off = torch.einsum(
        "bclhn,bchpn,bhcl->bclhp", C, states_in, decay_from_start
    )

    Y = rearrange(Y_diag + Y_off, "b c l h p -> b (c l) h p")
    return Y, final_state
```

Kiểm tra với recurrent reference:

```python
torch.manual_seed(1)
dtype = torch.float64
batch, length, heads, d_head, d_state = 2, 16, 2, 4, 3

X = torch.randn(batch, length, heads, d_head, dtype=dtype)
# Negative log-transition gives decay in (0, 1].
A = -torch.nn.functional.softplus(
    torch.randn(batch, length, heads, dtype=dtype)
)
B = torch.randn(batch, length, heads, d_state, dtype=dtype)
C = torch.randn(batch, length, heads, d_state, dtype=dtype)

Y_chunk, final_state = ssd_chunked(X, A, B, C, chunk_len=4)
Y_rec = ssd_recurrent(X, torch.exp(A), B, C)

torch.testing.assert_close(Y_chunk, Y_rec, rtol=1e-9, atol=1e-9)
print(Y_chunk.shape, final_state.shape)
# [2, 16, 2, 4], [2, 2, 4, 3]
```

> [!warning] Reference, không phải production kernel
> `segsum` materialize local matrices và code giả định length chia hết cho `chunk_len`. Production implementation cần fused kernels, numerical-stability handling, backward optimization, variable lengths, mixed precision và layout tuning. Không benchmark code sư phạm này rồi kết luận về Mamba-2 kernel.

## 8. Từ SSD layer đến Mamba-2 block

SSD chỉ định core sequence transformation. Mamba-2 block thêm projections, local convolution, gate, normalization và output projection.

Data flow ở mức khái niệm:

```text
                              ┌────────> z ──SiLU──┐
input u ──parallel projection─┼────────> X ─conv───┼─> SSD ─> gate ─> norm ─> out proj
                              ├────────> A         │
                              ├────────> B         │
                              └────────> C         │
```

Viết gọn:

$$
\begin{aligned}
(X,z,A,B,C)&=\operatorname{InputProjection}(u),\\
X_c&=\operatorname{DepthwiseConv1D}(X),\\
Y&=\operatorname{SSD}(A,B,C,X_c),\\
Y_g&=Y\odot\operatorname{SiLU}(z),\\
Y_n&=\operatorname{Norm}(Y_g),\\
\operatorname{out}&=W_oY_n.
\end{aligned}
$$

### 8.1 Khác biệt quan trọng với Mamba-1

Trong Mamba-1, $A,B,C$ được derive sau initial projected stream $X$. Điều này tạo dependency giữa projections. Mamba-2 tạo $A,B,C,X$ song song trực tiếp từ block input $u$, gần với cách attention tạo Q/K/V cùng lúc. Paper nêu hai lợi ích: block đơn giản hơn và phù hợp hơn với standard tensor-parallel sharding.[^dao-gu-2024]

### 8.2 Local convolution và gate

- `Depthwise Conv1D` trộn local neighboring tokens trên $X$ branch trước SSD.
- `Gate` dùng projected branch $z$ để modulate SSD output.
- Đây là các thành phần của Mamba-2 block, không xuất phát từ duality equation đơn thuần.

### 8.3 Extra normalization

Mamba-2 thêm normalization ngay trước output projection, sau multiplicative gate. Paper báo rằng thay đổi này giảm instabilities trong preliminary larger-model experiments. Đây là author-reported design evidence, không phải theorem rằng mọi SSM phải dùng đúng normalization này.[^dao-gu-2024]

### 8.4 Multi-input SSM head pattern

Mamba-2 thường có nhiều $X$ heads nhưng share $B,C$ theo group:

$$
X:(T,H,P),\quad
A:(T,H),\quad
B,C:(T,1,N)
$$

ở pattern share hoàn toàn, hoặc nhiều groups trong `grouped-input SSM`. Paper gọi analogy tương ứng là `multi-value attention`. Đừng nhầm với MQA/GQA optimization của ordinary attention: đây là vocabulary chuyển qua duality để mô tả parameter sharing; Mamba-2 không lưu ordinary shared-KV cache.[^dao-gu-2024]

### 8.5 Projection skeleton để đọc shapes

Code dưới chỉ minh họa parallel projections; nó không phải Mamba-2 implementation hoàn chỉnh:

```python
import torch
from torch import nn


class Mamba2ProjectionSkeleton(nn.Module):
    def __init__(self, d_model, n_heads, d_head, d_state):
        super().__init__()
        inner = n_heads * d_head
        self.n_heads = n_heads
        self.d_head = d_head
        self.d_state = d_state

        # Pedagogical separate layers; production may fuse them.
        self.to_x = nn.Linear(d_model, inner, bias=False)
        self.to_z = nn.Linear(d_model, inner, bias=False)
        self.to_a = nn.Linear(d_model, n_heads, bias=True)
        self.to_b = nn.Linear(d_model, d_state, bias=False)  # shared B
        self.to_c = nn.Linear(d_model, d_state, bias=False)  # shared C

    def forward(self, u):
        batch, length, _ = u.shape
        x = self.to_x(u).view(batch, length, self.n_heads, self.d_head)
        z = self.to_z(u).view(batch, length, self.n_heads, self.d_head)
        log_a = -torch.nn.functional.softplus(self.to_a(u))
        b = self.to_b(u)[:, :, None, :]  # [B,T,1,N], broadcast over heads
        c = self.to_c(u)[:, :, None, :]
        return x, z, log_a, b, c
```

Production Mamba-2 còn có parameterization của continuous/discretized SSM quantities, convolution state cho decode, grouped heads, normalization details và optimized kernels. Skeleton chỉ làm rõ rằng branches được tạo song song từ $u$.

## 9. Training, prefill và decode

### 9.1 Training/full-sequence prefill

Mọi tokens đã biết, nên chunked SSD khai thác parallel matmul bên trong chunks. Gradient vẫn có thể backpropagate qua toàn transformation; `chunked` ở đây là computational decomposition, không có nghĩa detach state hoặc truncated BPTT.

### 9.2 Autoregressive decode

Mỗi token mới update:

1. convolution state cho local Conv1D;
2. SSM state $S_t$ cho mỗi layer/head;
3. output mới từ state hiện tại.

SSM state shape không tăng theo generated length. Điều này khác attention `KV cache`, vốn thêm K/V entries theo token. Tuy nhiên end-to-end memory vẫn gồm model weights, activations/buffers, batching metadata và mọi attention layers nếu architecture là hybrid.

### 9.3 Không trộn lẫn các complexity statements

- `Linear in T` cho full-sequence SSD work không có nghĩa mỗi token miễn phí.
- `Fixed-state decode` không có nghĩa model nhớ vô hạn.
- `No growing KV cache` trong pure SSD layer không có nghĩa toàn hybrid model không có KV cache.
- FlashAttention giảm IO/intermediate memory nhưng vẫn giữ softmax attention semantics; SSD thay đổi sequence-mixing semantics.

## 10. Parallelism trong Mamba-2

### 10.1 Tensor parallelism: split feature/head dimensions

`Tensor parallelism` (`TP`) chia một layer qua nhiều devices. Với Mamba-1, vì $A,B,C$ phụ thuộc vào sharded $X_c$, shards cần gom $X_c$ trước khi derive parameters, tạo thêm synchronization. Với Mamba-2, mỗi shard project local $X,z,A,B,C$ trực tiếp từ $u$, giữ local SSM heads, rồi chỉ combine sau output projection.[^dao-gu-2024]

Với hai shards, mental model:

```text
shared input u
   ├─ shard 0: local projections → local conv → local SSD → local norm → partial output
   └─ shard 1: local projections → local conv → local SSD → local norm → partial output
                                                        │
                                          one output all-reduce
```

Paper's per-block analysis:

- Mamba-1 adaptation cần hai `all-reduce` theo data flow được phân tích;
- Mamba-2 cần một output `all-reduce`, tương tự attention hoặc MLP TP block;
- GroupNorm groups được chọn tương thích TP degree để normalization local không thêm communication.[^dao-gu-2024]

Đây là communication-count analysis, không phải end-to-end scaling benchmark trên mọi cluster.

### 10.2 Sequence parallelism cho residual/norm

Theo usage kiểu Megatron, `sequence parallelism` có thể split activations dọc sequence cho residual và normalization, phối hợp `reduce-scatter`/`all-gather` với TP. Vì Mamba-2 giữ residual/norm structure tương tự, paper nói kỹ thuật này áp dụng mà không cần thay đổi cơ bản.[^dao-gu-2024]

### 10.3 Context parallelism: split token-mixing sequence

Paper cũng dùng `sequence/context parallelism` cho chính token mixer. Mỗi worker giữ một contiguous chunk:

```text
worker 0: chunk 0, initial state 0 ──> final state 0
                                           │ send state
worker 1: chunk 1, initial state 0' ─> final state 1
                                           │ send state
worker 2: chunk 2, initial state 1' ─> final state 2
```

Đây là distributed version của block SSD decomposition. Mỗi chunk output gồm local contribution cộng contribution từ incoming state.

Với full attention, mỗi query block cần tương tác với key blocks khác; communication pattern vì thế khác và có thể cần ring/all-to-all-style movement. Với SSM, interface giữa neighboring chunks là recurrent state. Paper mô tả communication bandwidth tăng tuyến tính theo số workers thay vì quadratic query–key block interaction.[^dao-gu-2024]

> [!note] Parallelism không xóa dependency
> Boundary state của chunk sau vẫn phụ thuộc chunks trước. Parallel algorithm có thể tính local summaries trước rồi scan/combine summaries, nhưng causal dependency tồn tại về mặt toán học.

### 10.4 Ba khái niệm dễ nhầm

| Technique | Split axis/chức năng chính | Communication chính | Mục tiêu |
|---|---|---|---|
| Tensor parallelism | heads/features/weights trong layer | output all-reduce | layer quá lớn cho một device |
| Sequence parallelism cho residual/norm | sequence axis của replicated activations | reduce-scatter/all-gather | giảm activation duplication |
| Context parallelism cho SSM mixer | contiguous token chunks | recurrent boundary states | xử lý context rất dài |

Tên gọi trong hệ sinh thái có thể khác giữa frameworks; luôn kiểm tra tensor nào thực sự được shard.

### 10.5 Variable-length packed sequences

Có thể pack nhiều examples thành một long stream nhưng phải chặn state leak qua boundary. Với transition convention của paper, đặt transition factor ở boundary bằng 0 sẽ reset recurrence:

$$
S_t=0\cdot S_{t-1}+x_tb_t^\top.
$$

Khi dùng log-transition, không nên biểu diễn reset bằng một finite log gần 0 rồi giả định exact reset; production kernel thường cần boundary/reset handling rõ ràng. Cần test rằng thay đổi example trước không làm đổi output example sau.

## 11. Trade-offs và evidence limits

### 11.1 Điều được primary paper hỗ trợ

- SSM transformation tương ứng với semiseparable matrix transformation.
- Scalar-identity SSM và 1-semiseparable structured masked attention có cùng linear/quadratic forms.
- Block SSD algorithm kết hợp intra-chunk matmul với inter-chunk state scan.
- Mamba-2 dùng parallel parameter projections, multi-input/grouped head patterns và extra normalization.
- Architecture hỗ trợ Transformer-style TP với một output all-reduce theo per-block analysis.
- Context parallelism có thể truyền recurrent states giữa contiguous chunks.[^dao-gu-2024]

### 11.2 Điều không nên suy rộng

- Duality không chứng minh SSD tương đương standard softmax attention.
- Linear asymptotic scaling không bảo đảm nhanh hơn ở mọi sequence length/hardware.
- Fixed-size state không bảo đảm arbitrary exact recall.
- Một kernel benchmark không đại diện end-to-end serving.
- Một pure Mamba-2 result không chứng minh hybrid attention vô ích; chính paper báo hybrid attention cải thiện một số cấu hình được test, xem [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md).

### 11.3 So sánh nhanh

| Property | Full softmax attention | Recurrent SSM/SSD | Chunked SSD training |
|---|---|---|---|
| History representation at decode | per-token KV entries | fixed-size state | dùng recurrent state khi decode |
| Token-addressable | có | không trực tiếp | không thay semantics SSD |
| Full-sequence interaction work | quadratic theo $T$ | linear theo $T$, recurrence/scan | linear theo $T$ với local matmuls |
| Training hardware pattern | large matmuls | scan khó tối ưu hơn | batched local matmuls + short scan |
| Long-range interface | pairwise token scores | compressed state | compressed chunk-boundary state |

## 12. Debugging checklist

### 12.1 Algebra và shapes

- [ ] $S_t$ có shape `[batch, heads, d_head, d_state]`.
- [ ] Current token write không bị nhân nhầm bởi $a_t$.
- [ ] $L_{t,t}=1$.
- [ ] $L_{t,i}=0$ khi $i>t$.
- [ ] Product cho old token $i$ chạy từ $i+1$ đến $t$.
- [ ] Recurrent và quadratic references match ở float64.

### 12.2 Chunking

- [ ] `chunk_len=1` vẫn match recurrent reference.
- [ ] Nhiều `chunk_len` khác nhau cho cùng output trong tolerance.
- [ ] Initial state có đúng shape và được đưa vào chunk đầu.
- [ ] Final state match state của recurrent run.
- [ ] Không detach boundary state khi muốn full backpropagation.

### 12.3 Causality và packing

- [ ] Perturb future tokens không đổi prior outputs.
- [ ] Reset boundary ngăn cross-example leakage.
- [ ] Padding tokens không update state ngoài ý muốn.

### 12.4 Numerical stability

- [ ] Transition parameterization không làm products explode.
- [ ] `exp(cumulative log-transition)` được kiểm tra ở sequence dài.
- [ ] Mixed-precision output được so với FP32/FP64 reference.
- [ ] Tolerance không bị đặt rộng đến mức che implementation bug.

### 12.5 Distributed execution

- [ ] Mỗi TP shard giữ trọn local heads/state dimensions cần thiết.
- [ ] Norm groups chia hết cho TP degree nếu dựa trên local GroupNorm.
- [ ] Chỉ count collective sau khi vẽ data dependency thực tế.
- [ ] Context chunks có đúng thứ tự causal khi truyền/combine states.

## 13. Bài tập

### Bài 1 — unroll bằng tay

Cho $a=[1,0.5,0.2]$ và $x=[2,4,10]$. Tính $h_0,h_1,h_2$, dựng matrix $L$, rồi kiểm tra $Lx$.

<details>
<summary>Đáp án</summary>

$$
h_0=2,\quad h_1=0.5(2)+4=5,\quad h_2=0.2(5)+10=11.
$$

$$
L=\begin{bmatrix}
1&0&0\\
0.5&1&0\\
0.1&0.2&1
\end{bmatrix},
\qquad Lx=[2,5,11]^\top.
$$

</details>

### Bài 2 — kiểm tra chunk invariance

Chạy Lab 2 với `length=16` và `chunk_len` thuộc `{1, 2, 4, 8, 16}`. Mọi output phải match recurrent reference. Nếu chỉ một số chunk sizes fail, kiểm tra indexing ở `A_prefix`, padding boundary transition và incoming states.

### Bài 3 — visualize structured mask

Plot $L$ khi:

1. mọi $a_t=1$;
2. mọi $a_t=0.9$;
3. một $a_k\approx0$;
4. $a_t$ thay đổi theo token.

Giải thích đường nào trong history bị giữ, decay hoặc gần như reset.

### Bài 4 — capacity reasoning

Giữ $P$ cố định, tăng $N$ và đo khả năng khớp một synthetic associative-recall task. Không kết luận chỉ từ training loss; đo retrieval accuracy theo sequence length. Kết quả là experiment của bạn, không phải universal capacity theorem.

### Bài 5 — parallelism design

Với `n_heads=16`, `TP=4`, đề xuất cách shard heads và GroupNorm groups. Vẽ nơi diễn ra output all-reduce. Sau đó split sequence thành 8 context chunks và ghi shape của boundary state được truyền giữa workers.

## 14. Mental model cuối bài

Hãy giữ năm câu:

1. **Recurrence:** SSD nén prefix vào $S_t=a_tS_{t-1}+x_tb_t^\top$.
2. **Matrix view:** unroll recurrence tạo causal semiseparable transformation $M$.
3. **Duality:** với scalar-identity transitions, $M=L\circ CB^\top$ có structured attention-like quadratic form và exact recurrent form.
4. **Chunked training:** diagonal blocks dùng local matmul; off-diagonal blocks factor qua chunk-boundary states.
5. **Mamba-2 systems design:** parallel projections và local heads giúp TP cần một output all-reduce theo block analysis; long sequence có thể shard bằng state passing.

Bước tiếp theo nên là tự chạy hai labs, thêm gradient comparison giữa recurrent và chunked form, rồi đọc [Structured State Space Duality](structured-state-space-duality.md) và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) để đối chiếu concise concept notes với derivation trong bài này.

## Relationships

- **Depends on:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) và [Self-attention computational profile](self-attention-computational-profile.md) để hiểu memory/compute trade-off.
- **Synthesizes:** [Structured State Space Duality](structured-state-space-duality.md) và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) thành một learning sequence có derivation và labs.
- **Evaluated by:** [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md), nơi ghi các author-reported quality, recall và speed results cùng giới hạn evidence.
- **Part of:** [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md), Stage 8 về fixed-state và long-context mixing.

[^dao-gu-2024]: Tri Dao và Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), đặc biệt Sections 3–8 và self-contained SSD algorithm trong `structure/code.py`.
