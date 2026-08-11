---
type: Synthesis
title: "RoPE: positional encoding, implementation, và kiểm chứng cho người mới"
description: A beginner-first guide to how Rotary Position Embedding rotates per-head Q/K pairs, how its relative-position score arises, and how to implement and test one rotary convention in PyTorch.
tags: [rope, positional-encoding, attention, pytorch, kv-cache, learning-roadmap]
status: stable
created: 2026-08-11
generated:
  by: llm-wiki-agent/1
  at: 2026-08-11T21:18:07Z
sources:
  - id: rope-summary
    resource: ../raw/RoPE.md
    title: "RoPE overview (Vietnamese summary)"
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
---

# RoPE: positional encoding, implementation, và kiểm chứng cho người mới

`Rotary Position Embedding` (`RoPE`) đưa position vào `self-attention` **sau** các linear projection: với mỗi attention head, model xoay từng cặp tọa độ của `Query` (`Q`) và `Key` (`K`) một góc phụ thuộc absolute position. Khi lấy dot product giữa query ở position $m$ và key ở position $n$, hai phép xoay gộp thành một phép xoay theo $n-m$. Vì vậy attention score có relative-position information mà không cần cộng một position vector vào token embedding. `Value` (`V`) thông thường không bị xoay. Bài này là synthesis sư phạm: dùng quy ước `interleaved pairs`, triển khai PyTorch rõ ràng, và biến các tính chất toán học thành tests có thể chạy được.[^rope-summary]

> [!success] Mục tiêu
> Sau bài này, bạn có thể (1) chỉ ra chính xác RoPE nằm ở đâu trong đường đi $X\rightarrow Q,K,V\rightarrow QK^\top$, (2) tự suy ra vì sao score phụ thuộc relative offset, (3) thay learned absolute `position embedding` trong attention layer bằng RoPE, và (4) phát hiện lỗi dấu quay, cache sin/cos, position offset, hoặc pairing convention trước khi train lớn.

## 1. Điều cần biết trước

Bài này giả sử bạn đã biết:

- `Q`, `K`, `V`, scaled dot-product attention, và `causal mask`; xem [Attention: beginner's guide for causal language models](attention-beginner-guide.md).
- shape của causal multi-head attention: `(B, H, T, d_h)`, với `B` = batch size, `H` = số heads, `T` = sequence length, và `d_h` = `head_dim`.
- decoder-only Transformer có thể dùng learned absolute `position embedding` trước block đầu tiên; RoPE là một lựa chọn khác đặt positional mechanism vào attention. Xem [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).

RoPE **không** thay `causal mask`. RoPE cho score biết quan hệ position giữa query/key; mask quyết định key position nào được phép nhìn. Với causal language model, cả hai vẫn xuất hiện trước `softmax`:

$$
A=\operatorname{softmax}\left(
  \frac{\operatorname{RoPE}(Q)\operatorname{RoPE}(K)^\top}{\sqrt{d_h}}
  + M_{\text{causal}}
\right),\qquad O=AV.
$$

`M_causal` đặt score của future keys thành $-\infty$. Nếu bỏ mask, RoPE không ngăn future-token leakage.[^vaswani-transformer-2017]

## 2. Vì sao attention cần positional information?

Trong một head, hidden state $x_t\in\mathbb{R}^{D}$ của token tại position $t$ được chiếu thành:

$$
q_t=x_tW_Q,\qquad k_t=x_tW_K,\qquad v_t=x_tW_V.
$$

Core attention chỉ so nội dung của learned vectors qua $q_tk_j^\top$. Bản thân linear projection và dot product không có một coordinate nào được mặc định là “token thứ 17”. Causal mask tạo ràng buộc trái-phải, nhưng không cung cấp một representation liên tục về absolute position hay exact relative distance cho content vectors. Vì vậy Transformer cần một positional mechanism.[^vaswani-transformer-2017]

Có hai vị trí dễ nhầm:

| Cách làm | Position đi vào đâu? | Ví dụ công thức |
|---|---|---|
| Learned/sinusoidal absolute `position embedding` | cộng vào input hidden state trước attention | $h_t=x_t+p_t$ |
| `RoPE` | xoay projected `Q` và `K` trong từng head | $\tilde q_t=R_tq_t,\ \tilde k_t=R_tk_t$ |

Với RoPE, không cộng $p_t$ vào $x_t$ trong attention layer. Model vẫn có token embedding và vẫn tạo Q/K/V bằng learned weights; RoPE chỉ biến đổi Q/K **sau projection, trước score**.

```text
hidden states X: (B, T, D)
    ├─ Wq → Q: (B, H, T, dh) ── RoPE ─┐
    ├─ Wk → K: (B, H, T, dh) ── RoPE ─┼─ QKᵀ / √dh + causal mask → softmax
    └─ Wv → V: (B, H, T, dh) ─────────┘                              │
                                                                         └→ weights V
```

> [!warning] Không cộng cả learned `position embedding` lẫn RoPE chỉ vì “càng nhiều position càng tốt”. Một checkpoint/architecture xác định nơi position đi vào. Thêm hoặc bỏ một mechanism khi load pretrained weights thay đổi input distribution và không phải conversion trung tính.

## 3. Một phép quay 2D là toàn bộ ý tưởng

Xét một cặp components của một Q hoặc K vector, viết dưới dạng column vector $u=[a,b]^\top$. Phép quay ngược chiều kim đồng hồ một góc $\phi$ là:

$$
R(\phi)=
\begin{bmatrix}
\cos\phi & -\sin\phi\\
\sin\phi & \cos\phi
\end{bmatrix},\qquad
R(\phi)u=
\begin{bmatrix}
a\cos\phi-b\sin\phi\\
a\sin\phi+b\cos\phi
\end{bmatrix}.
$$

RoPE chọn $\phi=m\theta$ cho token ở absolute position $m$, trong đó $\theta$ là frequency của cặp đó:

$$
\operatorname{RoPE}(u,m)=R(m\theta)u.
$$

Các tính chất cần nhớ:

1. $R(0)=I$, nên position 0 không đổi vector.
2. $R(\phi)^\top=R(-\phi)$.
3. $R(\alpha)R(\beta)=R(\alpha+\beta)$.
4. $R(\phi)$ là orthogonal, nên $\lVert R(\phi)u\rVert_2=\lVert u\rVert_2$.

Tính chất cuối chỉ nói phép quay không tự thay đổi norm của **rotary slice**. Nó không nói activation, attention score, hay model output giữ nguyên, vì Q/K còn nội dung khác và score so sánh hai vector khác nhau.

### Ví dụ một cặp

Cho $q=k=[1,0]^\top$, query ở $m$ và key ở $n$. Sau RoPE:

$$
\tilde q_m=[\cos(m\theta),\sin(m\theta)]^\top,
\quad
\tilde k_n=[\cos(n\theta),\sin(n\theta)]^\top.
$$

Do đó:

$$
\tilde q_m^\top\tilde k_n=\cos((m-n)\theta).
$$

Cùng content vectors nhưng score thay đổi theo offset. Nếu $m=n$, positional factor là $\cos(0)=1$. Đây chỉ là ví dụ hình học đơn giản, không phải công thức đầy đủ của score với learned multi-dimensional Q/K.

## 4. Từ absolute rotation đến relative-position score

Đặt unrotated query ở position $m$ là $q_m$ và key ở position $n$ là $k_n$. Với $R_m=R(m\theta)$:

$$
\tilde q_m=R_mq_m,\qquad \tilde k_n=R_nk_n.
$$

Dot product là:

$$
\begin{aligned}
\tilde q_m^\top\tilde k_n
&=(R_mq_m)^\top(R_nk_n)\\
&=q_m^\top R_m^\top R_nk_n\\
&=q_m^\top R_{n-m}k_n.
\end{aligned}
$$

Vì $R_m^\top=R_{-m}$, hai absolute rotations còn lại một relative rotation $R_{n-m}$. Nếu bạn định nghĩa score với query/key theo thứ tự hay rotation matrix theo chiều ngược lại, công thức có thể hiện $m-n$ thay vì $n-m$. Điều quan trọng là **một code path phải nhất quán**; đổi dấu không được phép ở một bên Q hay K riêng lẻ.[^rope-summary]

### `relative offset` không có nghĩa score chỉ phụ thuộc distance

Công thức vẫn chứa $q_m$ và $k_n$, là learned content vectors khác nhau theo token/layer/context. Vì vậy score phụ thuộc **cả content lẫn relative position**, không phải chỉ khoảng cách. Khi giữ nguyên hai vectors và dịch đồng thời $m,n$ thêm cùng $c$, relative offset không đổi:

$$
(n+c)-(m+c)=n-m.
$$

Đây là shift invariance của riêng positional part. Không nên kết luận toàn bộ Transformer output bất biến nếu “dịch câu” trong input: token boundaries, causal context, padding, và representations từ các layers trước có thể đổi.

## 5. Nhiều dimensions và nhiều frequencies

Một `head_dim` chẵn $d_h$ được chia thành $d_h/2$ cặp. Với `interleaved pairs`:

$$
(x_0,x_1),\ (x_2,x_3),\ \ldots,\ (x_{d_h-2},x_{d_h-1}).
$$

Cặp $i$ dùng frequency cố định:

$$
\theta_i=\texttt{base}^{-2i/d_h},
\qquad i=0,\ldots,d_h/2-1,
$$

trong đó `base=10000` là conventional default của RoPE gốc. Position $m$ tạo angle $m\theta_i$. Cặp đầu quay nhanh hơn; cặp sau quay chậm hơn. Toàn bộ phép biến đổi là block-diagonal matrix gồm các rotation 2D độc lập.[^rope-summary]

Nhiều implementations chỉ xoay `rotary_dim < head_dim`, gọi là `partial RoPE`. Phần prefix kích thước `rotary_dim` (phải chẵn) được quay; suffix giữ nguyên. Đây là choice của architecture/configuration, không tự suy ra từ công thức. `Q` và `K` phải dùng cùng `rotary_dim`, frequencies, positions, và convention.

## 6. Hai pairing conventions: phải chọn một

Công thức $x\cos+\operatorname{rotate\_half}(x)\sin$ xuất hiện trong nhiều codebase, nhưng `rotate_half` không có một meaning phổ quát.

| Convention | Các cặp của vector `[x0, x1, x2, x3]` | `rotate_half` tương ứng |
|---|---|---|
| `interleaved` | `(x0,x1)`, `(x2,x3)` | `[-x1,x0,-x3,x2]` |
| `split-half` | `(x0,x2)`, `(x1,x3)` | `[-x2,-x3,x0,x1]` |

Cả hai có thể biểu diễn các rotation blocks hợp lệ; chúng liên hệ với nhau qua một permutation của coordinates. Nhưng weights của pretrained model đã học ý nghĩa của mỗi coordinate trong pairing convention cụ thể. Dùng sin/cos cache `interleaved` với `rotate_half` `split-half` (hoặc ngược lại) tạo một transformation khác với checkpoint mong đợi.[^rope-summary]

Bài này chọn **`interleaved`** vì dễ nhìn trực tiếp từng cặp liền nhau. Nếu đang reproduce một repository hoặc load checkpoint, hãy đọc configuration/source của chính checkpoint; không suy đoán convention từ tên `RoPE`.

## 7. PyTorch implementation: cache sin/cos và áp dụng `interleaved` RoPE

Code dưới đây ưu tiên inspectability. Nó không materialize matrix $R_m$: chỉ dùng elementwise multiply và đổi chỗ components. `position_ids` có shape `(B, T)` để hỗ trợ batch có position offsets khác nhau; `cos`/`sin` được broadcast qua head dimension.

```python
import torch


def rotate_interleaved(x: torch.Tensor) -> torch.Tensor:
    """Rotate each adjacent pair: (a, b) -> (-b, a)."""
    if x.size(-1) % 2 != 0:
        raise ValueError("rotary dimension must be even")
    pairs = x.reshape(*x.shape[:-1], -1, 2)
    rotated = torch.stack((-pairs[..., 1], pairs[..., 0]), dim=-1)
    return rotated.flatten(-2)


def rope_cos_sin(
    position_ids: torch.Tensor,
    rotary_dim: int,
    base: float = 10_000.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return cos/sin with shape (B, 1, T, rotary_dim).

    position_ids: integer tensor (B, T), with absolute token positions.
    """
    if rotary_dim <= 0 or rotary_dim % 2 != 0:
        raise ValueError("rotary_dim must be positive and even")

    # One frequency per 2D pair: (0,1), (2,3), ...
    pair_indices = torch.arange(
        0, rotary_dim, 2, device=position_ids.device, dtype=torch.float32
    )
    inv_freq = base ** (-pair_indices / rotary_dim)  # (rotary_dim / 2,)

    # (B, T, rotary_dim / 2): angle m * theta_i
    angles = position_ids.to(torch.float32)[..., None] * inv_freq
    # Repeat each pair's angle for its two adjacent coordinates.
    angles = torch.repeat_interleave(angles, repeats=2, dim=-1)
    return angles.cos().unsqueeze(1), angles.sin().unsqueeze(1)


def apply_rope_interleaved(
    x: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    rotary_dim: int,
) -> torch.Tensor:
    """Apply partial/full RoPE to x of shape (B, H, T, head_dim)."""
    if rotary_dim > x.size(-1):
        raise ValueError("rotary_dim cannot exceed head_dim")
    x_rotary, x_pass = x[..., :rotary_dim], x[..., rotary_dim:]
    x_rotary = x_rotary * cos + rotate_interleaved(x_rotary) * sin
    return torch.cat((x_rotary, x_pass), dim=-1)
```

### Kiểm tra một ví dụ bằng tay

Với `head_dim=4`, `base=10000`, position 1, vector `[1, 0, 1, 0]`, expected output theo `interleaved` là:

$$
[\cos(1),\sin(1),\cos(0.01),\sin(0.01)].
$$

Cặp đầu dùng $\theta_0=1$, cặp sau dùng $\theta_1=10000^{-2/4}=0.01$. Ví dụ này kiểm tra đồng thời thứ tự frequency, dấu của sine, và việc repeat mỗi angle cho đúng hai components.

```python
pos = torch.tensor([[1]])
cos, sin = rope_cos_sin(pos, rotary_dim=4)
x = torch.tensor([[[[1.0, 0.0, 1.0, 0.0]]]])  # (B=1, H=1, T=1, dh=4)
y = apply_rope_interleaved(x, cos, sin, rotary_dim=4)

expected = torch.tensor([[[[
    torch.cos(torch.tensor(1.0)), torch.sin(torch.tensor(1.0)),
    torch.cos(torch.tensor(0.01)), torch.sin(torch.tensor(0.01)),
]]]])
torch.testing.assert_close(y, expected, rtol=1e-5, atol=1e-6)
```

## 8. Gắn RoPE vào causal multi-head attention

Sau `q_proj`/`k_proj`, reshape Q/K/V thành heads rồi xoay Q và K. Không xoay V trong standard RoPE path. Ví dụ tối thiểu sau dùng full RoPE (`rotary_dim=head_dim`) và vẫn materialize full attention scores để dễ học; production kernels có thể fuse những bước này.

```python
import math
import torch.nn as nn
import torch.nn.functional as F


class CausalSelfAttentionWithRoPE(nn.Module):
    def __init__(self, d_model: int, n_heads: int, rotary_dim: int | None = None):
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.rotary_dim = self.head_dim if rotary_dim is None else rotary_dim
        if self.rotary_dim <= 0 or self.rotary_dim > self.head_dim:
            raise ValueError("invalid rotary_dim")
        if self.rotary_dim % 2 != 0:
            raise ValueError("rotary_dim must be even")

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor, position_ids: torch.Tensor | None = None):
        # x: (B, T, D); position_ids: (B, T)
        B, T, D = x.shape
        if position_ids is None:
            position_ids = torch.arange(T, device=x.device)[None].expand(B, -1)
        if position_ids.shape != (B, T):
            raise ValueError("position_ids must have shape (B, T)")

        def split_heads(y):
            return y.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        q = split_heads(self.q_proj(x))
        k = split_heads(self.k_proj(x))
        v = split_heads(self.v_proj(x))

        cos, sin = rope_cos_sin(position_ids, self.rotary_dim)
        q = apply_rope_interleaved(q, cos, sin, self.rotary_dim)
        k = apply_rope_interleaved(k, cos, sin, self.rotary_dim)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        causal = torch.ones(T, T, dtype=torch.bool, device=x.device).tril()
        scores = scores.masked_fill(~causal, float("-inf"))
        weights = F.softmax(scores, dim=-1)

        out = weights @ v
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        return self.out_proj(out)
```

Nếu bạn đang sửa `TinyGPT` trong [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), thay attention class bằng class trên và **bỏ** `position_emb` khỏi model input. Đó là một toy architecture change để học mechanism, không phải cách an toàn để chuyển một checkpoint đã train với learned absolute embeddings.

## 9. `KV cache`: absolute positions không được reset

Khi autoregressive decode, key của token cũ đã được xoay bằng absolute position của nó và lưu trong `KV cache`. Ở step mới, model chỉ:

1. projection Q/K/V cho new token;
2. xoay Q/K với position ID tuyệt đối hiện tại;
3. append rotated K và unrotated V vào cache;
4. so new Q với toàn bộ rotated K cache.

Ví dụ, nếu prompt có 10 tokens ở positions `0..9`, decode token đầu tiên phải dùng position `10`, không phải `0`. Reset position IDs khi decode làm phase của new Q/K không khớp với cached keys và thay đổi model behavior.

```python
# Pseudocode for one decode chunk of length new_T.
past_len = cached_k.size(-2)              # number of cached positions
position_ids = torch.arange(
    past_len, past_len + new_T, device=x_new.device
)[None].expand(batch_size, -1)

# Create/rotate q_new and k_new with these absolute IDs, then:
cached_k = torch.cat([cached_k, k_new_rotated], dim=-2)
cached_v = torch.cat([cached_v, v_new], dim=-2)
```

Đây là lý do RoPE phù hợp với [KV caching](kv-caching.md): cached K không cần xoay lại ở mỗi step. Cache phải là per-layer; mỗi layer có projections và rotated keys riêng. Xem [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) để kiểm tra cached versus uncached logits cho toàn model.

> [!warning] `position_ids` không luôn là `arange(T)`
> Trong prompt prefill đơn lẻ bắt đầu từ position 0, `arange(T)` là đúng. Nhưng padding, packed sequences, sliding windows, cache reuse, hoặc decode continuation có thể cần IDs khác. Contract là: position ID của Q/K phải khớp absolute-position convention mà checkpoint và KV cache dùng.

## 10. Tests: biến tính chất RoPE thành executable checks

Loss giảm không chứng minh RoPE đúng. Các test dưới đây cô lập lỗi trước khi model có thể “học bù” cho một implementation sai.

### Test 1 — position 0 là identity; norm của rotary slice được bảo toàn

```python
@torch.no_grad()
def test_identity_and_norm():
    torch.manual_seed(0)
    x = torch.randn(2, 3, 4, 8)  # (B, H, T, head_dim)
    pos = torch.zeros(2, 4, dtype=torch.long)
    cos, sin = rope_cos_sin(pos, rotary_dim=6)
    y = apply_rope_interleaved(x, cos, sin, rotary_dim=6)

    # phi = 0: rotary slice is exactly x; suffix is never touched.
    torch.testing.assert_close(y, x, rtol=1e-5, atol=1e-6)
    torch.testing.assert_close(
        y[..., :6].norm(dim=-1), x[..., :6].norm(dim=-1),
        rtol=1e-5, atol=1e-6,
    )
```

Nếu test fail, kiểm tra cache sin/cos, broadcasting shape, hoặc implementation `rotate_interleaved`. Test này không tự phát hiện việc bạn dùng `split-half` nhất quán; convention đó vẫn có thể pass identity và norm.

### Test 2 — kết quả khớp rotation matrix 2D và phát hiện dấu sai

```python
@torch.no_grad()
def test_one_pair_against_matrix():
    phi = torch.tensor(0.7)
    x = torch.tensor([[[[2.0, -3.0]]]])
    cos = phi.cos().reshape(1, 1, 1, 1).expand_as(x)
    sin = phi.sin().reshape(1, 1, 1, 1).expand_as(x)

    got = apply_rope_interleaved(x, cos, sin, rotary_dim=2)
    R = torch.tensor([[phi.cos(), -phi.sin()], [phi.sin(), phi.cos()]])
    expected = x @ R.T  # x is stored as a row, while math above used a column
    torch.testing.assert_close(got, expected, rtol=1e-5, atol=1e-6)
```

Test dùng vector không đối xứng `[2,-3]`; dùng `[1,0]` vẫn tốt cho ví dụ trực giác nhưng kém hơn trong việc phát hiện lỗi hoán đổi hoặc dấu.

### Test 3 — dot product chỉ còn `relative offset` khi Q/K content cố định

```python
@torch.no_grad()
def rotate_one_vector(x, position: int, rotary_dim: int):
    pos = torch.tensor([[position]])
    cos, sin = rope_cos_sin(pos, rotary_dim)
    return apply_rope_interleaved(x, cos, sin, rotary_dim)


def test_relative_shift_invariance():
    torch.manual_seed(1)
    q = torch.randn(1, 1, 1, 6)
    k = torch.randn(1, 1, 1, 6)
    m, n, shift = 3, 11, 100

    score_1 = (rotate_one_vector(q, m, 6) * rotate_one_vector(k, n, 6)).sum()
    score_2 = (
        rotate_one_vector(q, m + shift, 6)
        * rotate_one_vector(k, n + shift, 6)
    ).sum()
    torch.testing.assert_close(score_1, score_2, rtol=1e-5, atol=1e-6)
```

Test này giữ Q/K raw vectors cố định một cách có chủ ý. Nó kiểm tra algebra của RoPE, **không** kiểm tra whole-model translation invariance.

### Test 4 — `partial RoPE` không làm thay đổi suffix

```python
@torch.no_grad()
def test_partial_rope_suffix_unchanged():
    x = torch.randn(2, 2, 3, 8)
    pos = torch.arange(3)[None].expand(2, -1)
    cos, sin = rope_cos_sin(pos, rotary_dim=4)
    y = apply_rope_interleaved(x, cos, sin, rotary_dim=4)
    torch.testing.assert_close(y[..., 4:], x[..., 4:])
```

Lỗi hay gặp là build cache rộng bằng `head_dim` rồi vô tình xoay toàn vector dù configuration chỉ yêu cầu `partial RoPE`.

### Test 5 — full pass và cache-style score phải khớp

```python
@torch.no_grad()
def test_cached_key_score_matches_full_score():
    torch.manual_seed(2)
    B, H, T, dh = 1, 2, 5, 4
    q = torch.randn(B, H, T, dh)
    k = torch.randn(B, H, T, dh)
    pos = torch.arange(T)[None]
    cos, sin = rope_cos_sin(pos, rotary_dim=dh)
    q_rot = apply_rope_interleaved(q, cos, sin, dh)
    k_rot = apply_rope_interleaved(k, cos, sin, dh)

    full_scores = q_rot @ k_rot.transpose(-2, -1)
    final_query_score = q_rot[:, :, -1:] @ k_rot.transpose(-2, -1)
    torch.testing.assert_close(final_query_score, full_scores[:, :, -1:])
```

Đây là unit test của rotary/cache path. Toàn model còn cần test cached-versus-uncached logits vì lỗi có thể nằm ở concatenate cache, causal mask, layer indexing, hoặc position offset chứ không nằm trong RoPE.

### Test 6 — checkpoint convention bằng reference output

Nếu dùng external checkpoint, hãy lấy một fixed input và `position_ids`, rồi so Q/K rotated hoặc final logits với trusted reference implementation của **cùng checkpoint** trong `eval()` mode. Đây là test có giá trị nhất để phát hiện `interleaved`/`split-half` mismatch. So sánh shapes, norm, hay loss không đủ vì cả hai conventions đều có thể tạo tensor hợp lệ.

Khi compare floating point, chấp nhận tolerance phù hợp dtype/kernel. Trước hết tắt dropout; sau đó kiểm tra dtype, `base`, `rotary_dim`, scaling variant, and position IDs trước khi kết luận weights hỏng.

## 11. Các lỗi phổ biến và cách khoanh vùng

| Triệu chứng | Nguyên nhân khả dĩ | Check đầu tiên |
|---|---|---|
| position 0 đổi Q/K | cache không có `cos=1`, `sin=0`, hoặc broadcast sai | Test 1 |
| manual rotation có dấu ngược | `rotate_half` là `(b,-a)` thay vì `(-b,a)`, hoặc sine bị trừ | Test 2 |
| score không giữ khi dịch cả $m,n$ | Q và K dùng position/frequency/base khác nhau | Test 3 |
| load checkpoint cho logits khác reference | pairing convention, `rotary_dim`, base, scaling, hoặc position IDs không khớp | Test 6 |
| cached decode khác full prefill | reset position về 0, rotate cached K lần nữa, hoặc append sai dimension | Test 5 rồi full-model cache test |
| past logits đổi khi đổi future tokens | causal mask thiếu/ngược; RoPE không phải nguyên nhân thay thế mask | causal test từ bài Attention |
| code chạy nhưng context dài chất lượng kém | extrapolation/training issue, không nhất thiết implementation bug | xác nhận tests, rồi xem long-context setup |

## 12. RoPE không tự giải quyết `long context`

Sin/cos có thể được tính cho position lớn hơn training length, nên RoPE không bị chặn cơ học bởi một learned table có số rows cố định. Nhưng “tính được angle” không đồng nghĩa model có usable retrieval ở length đó. Position phases, training distribution, frequency/base configuration, and long-sequence fine-tuning ảnh hưởng extrapolation. Position interpolation và các RoPE scaling/frequency modifications là những kỹ thuật phát triển sau; chúng không phải behavior mặc định của RoPE gốc.[^rope-summary]

Cũng không nên diễn giải tổng nhiều frequencies như một hard monotonic distance penalty. Phase cancellation có thể tạo soft tendency với distance trong một phân tích, nhưng individual Q/K content và periodic sin/cos vẫn có thể tạo high score ở offset xa.[^rope-summary] Nếu mục tiêu là bias tuyến tính theo distance thay vì rotation trong Q/K space, [ALiBi attention with linear biases](alibi-attention-with-linear-biases.md) là một alternative mechanism.

## 13. Checklist trước khi tiếp tục Stage 6

- [ ] `head_dim` và `rotary_dim` là even; `rotary_dim <= head_dim`.
- [ ] RoPE chạy sau Q/K projection và head reshape, trước QK score.
- [ ] Q và K dùng cùng `base`, frequencies, `rotary_dim`, pairing convention, và `position_ids`.
- [ ] V không bị xoay trừ khi architecture cụ thể nói rõ điều đó.
- [ ] Causal mask vẫn được cộng vào scores trước `softmax`.
- [ ] Tests identity, manual 2D rotation, relative shift, partial suffix, và cache-style score đều pass.
- [ ] Decode dùng absolute position tiếp nối cached prefix, không reset về 0.
- [ ] Nếu dùng checkpoint, output khớp trusted implementation theo tolerance thích hợp.

Sau khi baseline pass checklist, học [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) để giảm K/V cache traffic, rồi dùng [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) để thay đổi data movement mà không thay đổi exact attention semantics. Đây là phần positional-encoding của Stage 6 trong [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Relationships

- **Elaborates:** Stage 6 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng theory, PyTorch implementation, và verification procedure cho RoPE.
- **Builds on:** [Attention: beginner's guide for causal language models](attention-beginner-guide.md) cho Q/K/V và causal masking; [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) cho baseline model và shapes.
- **Expands:** [Rotary position embedding (RoPE)](rotary-position-embedding.md) với một `interleaved` implementation và tests cho convention/cache.
- **Uses:** [KV caching](kv-caching.md), vì rotated K được lưu theo absolute position trong decode state.
- **Contrasts with:** [ALiBi attention with linear biases](alibi-attention-with-linear-biases.md), vốn cộng distance bias vào logits thay vì xoay Q/K.

[^rope-summary]: “RoPE overview” (Vietnamese summary), [raw source](../raw/RoPE.md), Sections 1–15. Đây là nguồn secondary tóm tắt RoFormer; primary paper của RoPE chưa được ingest độc lập trong repository.
[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), phần scaled dot-product attention và decoder masking.
