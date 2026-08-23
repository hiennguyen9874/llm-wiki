---
type: Synthesis
title: "MLA và token-addressable memory — bài học cho người mới"
description: A beginner-first course on how MLA compresses each token's KV representation while preserving token-addressable softmax retrieval, why its cache still grows with context, and how it contrasts with fixed-state memory.
tags: [mla, attention, kv-cache, token-addressable-memory, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-23T12:00:00Z }
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

`Multi-head Latent Attention` (MLA) không xóa `KV cache` — nó làm mỗi `cache entry` nhỏ hơn. Với mỗi token, MLA thay cặp K/V lớn của nhiều heads bằng một `KV latent` nhỏ (`joint latent`) dùng chung + một `rotary key` nhỏ cho position. Vì mỗi token vẫn có một entry riêng và query mới vẫn tạo một `attention weight` cho từng token cũ, MLA vẫn là **token-addressable softmax attention**. Kết quả: bytes **trên mỗi token** giảm mạnh, nhưng tổng cache và lượng history phải đọc vẫn tăng tuyến tính theo `context length`. Đây là baseline cần nắm trước khi học `fixed-state memory`, nơi nhiều token được gộp vào một `state` có kích thước cố định và không còn slot riêng cho từng token.[^deepseek-v2-2024][^fast-weight-programmers-2021]

> [!success] Sau bài này, bạn có thể
> 1. Phân biệt `compression per token` (làm mỗi entry nhỏ hơn) với `fixed-state` (không còn entry theo token).
> 2. Viết công thức `memory growth` cho MHA, MLA và fixed-state, và đọc đúng ý nghĩa của "giảm 90% cache".
> 3. Giải thích `low-rank KV joint compression` và `decoupled RoPE` bằng một hình dung duy nhất.
> 4. Chỉ ra vì sao MLA vẫn `token-addressable` qua shape của `attention weights`.
> 5. Implement một MLA-like `content path` tối giản và test `cached decode == full forward`.
> 6. Chọn baseline đúng khi đọc một long-context architecture (MHA vs GQA vs MLA vs hybrid).

## 1. Điều cần biết trước

- Đã biết Q/K/V, `scaled dot-product attention`, `causal mask` và `KV caching` cơ bản. Nếu chưa, đọc trước [Attention: beginner's guide](attention-beginner-guide.md) và [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md).
- Đã hiểu `prefill` (xử lý prompt một lần) và `decode` (sinh từng token) khác nhau ở đâu — xem [LLM inference lifecycle: training, prefill, decode, và latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md).
- Không cần biết kernel Triton hay distributed training. Code dưới là **pedagogical** (`torch.cat` cho cache) — không phải serving kernel production.

**Bài này không cover:** training loss của MLA, MoE routing, quantization hay `PagedAttention`. Chúng thay đổi trục khác và được link ở mục 7.

## 2. Lý thuyết cốt lõi

### 2.1 Hai câu hỏi phải tách rời

Mọi tối ưu long-context đều trả lời hai câu hỏi khác nhau. Nhầm lẫn phổ biến là gộp chúng:

| Câu hỏi | Ý nghĩa | MLA trả lời | Fixed-state trả lời |
|---|---|---|---|
| **Mỗi token tốn bao nhiêu?** (`per-token state`) | `bytes/token/layer` | Ít hơn MHA nhiều | Một phần của `state` chung |
| **Tổng state có tăng theo context?** (`sequence scaling`) | Shape có chứa `S`? | Có — tăng tuyến tính với `S` | Không — shape cố định |

> [!important] Quy tắc đọc paper
> Thấy "giảm KV cache 90%" → hỏi ngay: công thức còn thừa số `S` (sequence length) không? Nếu còn, đó là **giảm slope**, không phải xóa slope.

**Công thức tổng quát:**

- $B$: `batch size`, $L$: số `attention layers`, $S$: số `cached tokens`
- $H$: số `heads`, $d_h$: `dimension` mỗi head, $p$: `bytes/element` (ví dụ BF16 → 2)

MHA:

$$
M_{MHA}=B \cdot L \cdot S \cdot (2Hd_h) \cdot p
$$

Cơ chế giảm `per-token` xuống $r$ elements:

$$
M = B \cdot L \cdot S \cdot r \cdot p
$$

Cache nhỏ hơn theo hệ số $2Hd_h/r$, nhưng vẫn tỷ lệ với $S$. Fixed-state khác bản chất:

$$
M_{fixed}\approx B \cdot L \cdot H \cdot (d_k d_v) \cdot p
$$

Không có $S$ — shape do `feature dimensions` quyết định.[^fast-weight-programmers-2021]

**Hình dung:**
- MHA = tủ hồ sơ: mỗi token = một ngăn riêng, mỗi ngăn dày.
- MLA = cùng tủ đó nhưng mỗi ngăn mỏng hơn (nén).
- Fixed-state = bảng trắng: mọi token ghi đè lên nhau trên một mặt phẳng cố định.

### 2.2 Baseline: vì sao standard attention là token-addressable?

Ở một head, token $t$ tính output:

$$
o_t=\sum_{j=1}^{t}\alpha_{t,j}\,v_j,\qquad
\alpha_{t,j}=\operatorname{softmax}_j\!\left(\frac{q_t^T k_j}{\sqrt{d_h}}\right)
$$

Index $j$ chính là **địa chỉ của token thứ $j$**. Query $q_t$ chấm điểm riêng với từng $k_j$, rồi lấy $v_j$ với weight riêng $\alpha_{t,j}$. Hệ quả:

- Cache có một K/V slot cho mỗi token.
- `Attention weights` có trục dài $S$ — `shape (B, H, 1, S)` khi decode một token.
- Query có thể "chỉ" vào position cụ thể (ví dụ token chứa đáp án).
- Mỗi decode step phải đọc và chấm điểm toàn bộ history dài $S$.

> [!note] Token-addressable ≠ nhớ đúng
> Nó chỉ mô tả **cấu trúc retrieval**: mỗi token có entry riêng để query chấm điểm. Model vẫn có thể học kém và không truy xuất đúng.

### 2.3 Ý tưởng cốt lõi của MLA: cache latent, không cache K/V đã expand

Với hidden state $h_t \in \mathbb{R}^{d}$, MLA tạo một `joint latent` nhỏ:

$$
c_t^{KV}=W^{DKV}h_t,\qquad c_t^{KV}\in\mathbb{R}^{d_c},\quad d_c \ll H d_h
$$

Rồi sinh content key/value từ cùng latent:

$$
k_t^C = W^{UK}c_t^{KV},\qquad v_t^C = W^{UV}c_t^{KV}
$$

Điểm mấu chốt là **cái gì được giữ qua decode steps**:

```text
MHA cache tại token t:
  [K của mọi heads | V của mọi heads]     ≈ 2·H·d_h  elements

MLA cache tại token t:
  [joint KV latent c_t | rotary key k_t^R] = d_c + d_h^R  elements
  (không lưu k_t^C, v_t^C đã expand)
```

Tại sao không cần lưu $k_t^C, v_t^C$? Nhờ **matrix associativity**, DeepSeek-V2 "hấp thụ" (`absorb`) các up-projections vào đường query/output trong inference[^deepseek-v2-2024]:

$$
q_t^T k_j^C = q_t^T W^{UK}c_j^{KV}= \big((W^{UK})^T q_t\big)^T c_j^{KV}
$$

Query được biến đổi trước rồi chấm trực tiếp với cached latent. Tương tự, $W^{UV}$ được gộp vào `output projection`. Đây là tối ưu đại số — không phải gộp nhiều token vào một state.

**`Low-rank` nghĩa là gì?**

Đường đi $h_t \to c_t^{KV} \to (k_t^C, v_t^C)$ qua bottleneck $d_c$. K và V content cùng được sinh từ một latent hẹp. Khác với:

- **Quantization:** giảm bits/element.
- **Token eviction:** bỏ hẳn entry của một số token.
- **GQA/MQA:** share nguyên head K/V giữa các query heads.
- **Fixed-state recurrence:** gộp history vào state không có trục $S$.

Các kỹ thuật này có thể kết hợp, nhưng chúng tác động lên trục khác nhau.

### 2.4 Vì sao cần `decoupled RoPE`?

Nếu áp RoPE trực tiếp lên content key sau up-projection:

$$
k_{t}^{C,R}=R_t\,W^{UK}c_t^{KV}
$$

thì rotation $R_t$ phụ thuộc position $t$ nằm giữa $W^{UK}$ và latent $c_t^{KV}$. Ta không thể dùng một projection cố định để hấp thụ $W^{UK}$ cho mọi cached position — vì $R_t$ thay đổi theo $t$ và matrix multiplication không giao hoán.[^deepseek-v2-2024]

MLA tách hai đường:

$$
q_{t,i}=[q_{t,i}^{C};\,q_{t,i}^{R}],\qquad
k_{t,i}=[k_{t,i}^{C};\,k_t^{R}]
$$

- $q_{t,i}^{R}$: rotary query riêng cho head $i$
- $k_t^{R}$: rotary key **share giữa heads**, nhỏ ($d_h^R$ thấp)
- Content K/V vẫn đi qua joint latent
- Cache giữ cả $c_t^{KV}$ và $k_t^{R}$

Attention vẫn chạy theo từng token:

$$
o_{t,i}=\sum_{j=1}^{t}\operatorname{softmax}_j\!\left(\frac{q_{t,i}^T k_{j,i}}{\sqrt{d_h+d_h^R}}\right)v_{j,i}^{C}
$$

`Query compression` cũng xuất hiện trong MLA để giảm `training activation memory`, nhưng query của token hiện tại không phải history state cần giữ qua decode — nên nó **không làm KV cache nhỏ hơn**.[^deepseek-v2-2024]

```text
h_t ──► W^{DKV} ──► c_t^{KV} ─┬──► W^{UK} ──► k_t^C ─┐
                             │                      ├──► concat ──► attention
                             └──► W^{UV} ──► v_t^C ─┘         ▲
h_t ──► rotary path ──► k_t^R (share) ────────────────────────┘
         cache = [c_t^{KV} | k_t^R]  × S tokens
```

### 2.5 Memory accounting: MLA giảm slope, không xóa slope

Mỗi token mỗi layer, MLA cache:

$$
d_c + d_h^R\quad\text{elements}
$$

Tổng raw cache:

$$
M_{MLA}=B\cdot L\cdot S\cdot(d_c+d_h^R)\cdot p
$$

So với $M_{MHA}=BLS(2Hd_h)p$, **compression ratio** (tính theo element count):

$$
\frac{M_{MHA}}{M_{MLA}}=\frac{2Hd_h}{d_c+d_h^R}
$$

Trong config DeepSeek-V2, $d_c=4d_h$ và $d_h^R=d_h/2$ → khoảng $4.5d_h$ elements/token/layer, được mô tả tương đương GQA với 2.25 KV groups. Đây là **con số của một config cụ thể**, không phải hằng số chung của mọi MLA variant.[^deepseek-v2-2024]

**Ví dụ số học (dễ nhẩm theo):**

Giả sử $L=32$, $B=1$, $H=32$, $d_h=128$, BF16 ($p=2$), MLA $d_c=512$, $d_h^R=64$:

- MHA: $32 \times (2\times32\times128)\times2 = 524{,}288$ bytes/token ≈ **0.50 MiB/token** trên toàn model
- MLA: $32 \times (512+64)\times2 = 36{,}864$ bytes/token ≈ **0.035 MiB/token**

| Context $S$ | MHA raw cache | MLA raw cache |
|---|---:|---:|
| 1,024 | ~512 MiB | ~36 MiB |
| 8,192 | ~4 GiB | ~288 MiB |
| 32,768 | ~16 GiB | ~1.1 GiB |

Cả hai cùng tăng 32× khi $S$ tăng 32× — MLA có **slope thấp hơn ~14×**, nhưng slope vẫn khác 0. Production memory còn phụ thuộc `dtype`, `allocator`, `block layout`, `batching`, `prefix sharing` và `temporary buffers` — công thức trên chỉ accounting các `retained cache tensors`.

### 2.6 Tại sao MLA vẫn là `token-addressable memory`?

Sau khi cache $S$ tokens, MLA giữ:

$$
C^{KV}_{1:S}=[c_1^{KV},c_2^{KV},\ldots,c_S^{KV}]
$$

và position keys tương ứng. Trục sequence vẫn dài $S$. Query mới tạo logits shape `(B, H, 1, S)` — mỗi cột ứng với một token position.

| Câu hỏi | MLA | Fixed-state memory |
|---|:---:|:---:|
| Có state entry mới cho mỗi token? | ✅ | ❌ |
| Query tạo score/weight riêng cho từng position? | ✅ | ❌ (đọc state đã gộp) |
| Có thể chỉ vào token thứ `j` qua attention axis? | ✅ | ❌ (không còn slot `j`) |
| Decode state tăng theo $S$? | ✅ | ❌ |
| Nhiều associations bị superpose vào cùng state? | ❌ | ✅ |

> Đừng hiểu "latent" trong MLA là "một latent tóm tắt cả context". Đúng hơn là **một latent cho mỗi token, tại mỗi MLA layer**.

### 2.7 Fixed-state đổi memory scaling bằng trade-off khác

Một `linear-attention associative memory` tối giản:

$$
S_t = S_{t-1} + \phi(k_t)^T v_t,\qquad o_t = \phi(q_t)\,S_t
$$

State $S_t \in \mathbb{R}^{d_k \times d_v}$ có **cùng shape ở token 10 và token 1,000,000**. Outer products của nhiều tokens cùng cộng vào một matrix. Query không tạo vector weights dài $t$ — nó đọc tổ hợp đã superpose.

Hệ quả:

- **MLA:** `sequence-growing compressed slots`, `direct token-level retrieval`, `softmax over history`.
- **Fixed-state:** `bounded state`, `recurrent update/read`, nhưng có **capacity interference** và không giữ isolated slot.

Phân tích trong `Linear Transformers Are Secretly Fast Weight Programmers` chỉ ra: với additive memory, để retrieval không nhiễu cần mapped keys trực giao — đó là giới hạn biểu diễn, không phải ngưỡng failure cố định cho mọi model.[^fast-weight-programmers-2021]

**Vì sao có hybrid?** Kimi Linear dùng 3 layers fixed-state KDA rồi 1 layer global MLA: KDA giảm sequence-growing state ở đa số layers, periodic MLA giữ khả năng token-level retrieval. Report nêu tối đa 75% KV-cache reduction so với full MLA theo layer ratio, nhưng model tổng vẫn có cache tăng theo context ở các MLA layers.[^kimi-linear-2025]

### 2.8 Cost không chỉ là cache capacity

Khi decode một token mới:

**MLA:**
1. Append một latent + một rotary key
2. Tạo/transform query mới
3. Chấm query với $S$ cached entries → softmax trên $S$ positions → retrieve value
4. Cache reads và attention work **tăng với $S$**

**Fixed-state:**
1. Update state bằng token mới
2. Read state có shape cố định
3. Work per-step **không tăng theo $S$**, nhưng representation phải nén history và có thể mất exact retrieval

> Prefill có thể dùng `chunkwise/parallel algorithms` thay vì recurrence từng token — nên cần đo riêng **prefill latency** và **one-token decode latency**. Đừng suy latency từ bytes.

## 3. Implementation (PyTorch tối thiểu)

Code dưới chỉ implement **content path** $c^{KV}\to K^C,V^C$ để làm rõ cache semantics. Cố ý bỏ `decoupled RoPE`, `query compression`, `projection absorption` và optimized kernels — những thứ này không đổi bản chất `per-token latent`.

- `position_ids` là **absolute** (0,1,2,...) — không dùng relative offset trong toy này.
- Cache shape mỗi layer: `(B, S, d_c)` — có trục $S$.
- Toy dùng `torch.cat` để append — dễ đọc nhưng không phải `paged blocks` của serving.

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
        self.head_dim = d_model // n_heads
        self.d_latent = d_latent

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.kv_down = nn.Linear(d_model, d_latent, bias=False)
        self.k_up = nn.Linear(d_latent, d_model, bias=False)
        self.v_up = nn.Linear(d_latent, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

    def _heads(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        return x.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,                          # (B, T_new, D)
        past_latent: Optional[torch.Tensor] = None,  # (B, S_past, d_c)
        use_cache: bool = False,
    ):
        B, T_new, D = x.shape
        q = self._heads(self.q_proj(x))            # (B, H, T_new, d_h)
        c_new = self.kv_down(x)                    # (B, T_new, d_c) — one latent per token

        if past_latent is None:
            c_all = c_new
            past_len = 0
        else:
            if past_latent.shape[0] != B:
                raise ValueError("cache batch size does not match")
            c_all = torch.cat((past_latent, c_new), dim=1)
            past_len = past_latent.size(1)

        # Pedagogical reconstruction — optimized MLA absorbs projections
        k = self._heads(self.k_up(c_all))          # (B, H, S, d_h)
        v = self._heads(self.v_up(c_all))          # (B, H, S, d_h)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        S = c_all.size(1)
        # absolute position_ids: past tokens 0..past_len-1, new tokens past_len..past_len+T_new-1
        q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]
        k_pos = torch.arange(S, device=x.device)[None, :]
        causal = k_pos <= q_pos
        scores = scores.masked_fill(~causal, float("-inf"))

        weights = F.softmax(scores, dim=-1)        # last axis indexes tokens
        y = weights @ v
        y = y.transpose(1, 2).contiguous().view(B, T_new, D)
        present = c_all if use_cache else None
        return self.out_proj(y), present, weights
```

Ba quan sát trực tiếp từ code:

1. `past_latent.shape == (B, S, d_latent)` — latent nhỏ nhưng vẫn có trục `S`.
2. `weights.shape == (B, H, T_new, S)` — query vẫn address từng cached token.
3. Mỗi decode step `torch.cat` thêm một entry — cache không fixed-state.

## 4. Xác minh trước khi benchmark

> [!warning] Lab này chỉ chứng minh semantics của toy content cache
> Full MLA còn `decoupled RoPE`, `query compression` và `projection absorption`. Các test dưới không chứng minh parity với full MLA — chỉ chứng minh **sequence axis và token-addressability** của joint-latent cache.

```python
import torch


@torch.inference_mode()
def test_cached_decode_matches_full():
    """Test 1: cached decode (prefill + 1 step) khớp full causal forward."""
    torch.manual_seed(0)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(2, 7, 32)

    full_y, _, full_w = layer(x, use_cache=False)

    _, cache, _ = layer(x[:, :6], use_cache=True)          # prefill 6 tokens
    step_y, cache, step_w = layer(x[:, 6:7], past_latent=cache, use_cache=True)

    # Logits/output của token cuối phải khớp trong tolerance
    torch.testing.assert_close(step_y, full_y[:, 6:7], rtol=1e-5, atol=1e-6)
    assert cache.shape == (2, 7, 8), f"cache shape {cache.shape} != (2, 7, 8)"
    assert step_w.shape == (2, 4, 1, 7), f"weights {step_w.shape} != (2, 4, 1, 7)"
    # Mỗi query position chỉ attend tới quá khứ (causal)
    assert torch.allclose(step_w.sum(dim=-1), torch.ones_like(step_w.sum(dim=-1)))
    print("✓ Test 1 passed: cached decode matches full forward, shapes correct")


@torch.inference_mode()
def test_weights_are_token_addressable():
    """Test 2: attention weights có đúng S cột — mỗi cột là một token."""
    torch.manual_seed(1)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(1, 5, 32)
    _, _, weights = layer(x)  # (1, 4, 5, 5) with causal mask
    assert weights.shape == (1, 4, 5, 5)
    # Hàng causal: token 0 chỉ thấy 1 token, token 4 thấy 5 tokens
    # weights[0,0,0] should be [1, 0, 0, 0, 0] (masked future = 0 after softmax)
    assert weights[0, 0, 0, 1:].abs().max().item() < 1e-6
    assert weights[0, 0, 4].sum().item() == torch.tensor(1.0).item() or abs(weights[0, 0, 4].sum().item() - 1.0) < 1e-5
    print("✓ Test 2 passed: weights index tokens — causal structure intact")
    # In ra để thấy trực quan
    print(f"  weights[0,0,4] (query cuối attend 5 tokens): {weights[0,0,4].tolist()}")


@torch.inference_mode()
def test_cache_grows_with_sequence():
    """Test 3: cache tăng tuyến tính với S, không fixed-state."""
    torch.manual_seed(2)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x_short = torch.randn(1, 10, 32)
    x_long = torch.randn(1, 100, 32)
    _, cache_short, _ = layer(x_short, use_cache=True)
    _, cache_long, _ = layer(x_long, use_cache=True)
    assert cache_short.shape == (1, 10, 8)
    assert cache_long.shape == (1, 100, 8)
    assert cache_long.numel() == 10 * cache_short.numel()
    print(f"✓ Test 3 passed: cache grows linearly — 10 tokens: {cache_short.shape}, 100 tokens: {cache_long.shape}")


@torch.inference_mode()
def test_no_future_leakage():
    """Test 4: future tokens không ảnh hưởng quá khứ (causal isolation)."""
    torch.manual_seed(3)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(1, 6, 32)
    y_full, _, _ = layer(x)

    # Thay token tương lai bằng noise — output của 3 token đầu không đổi
    x_perturbed = x.clone()
    x_perturbed[:, 3:] = torch.randn(1, 3, 32)
    y_perturbed, _, _ = layer(x_perturbed)

    torch.testing.assert_close(y_full[:, :3], y_perturbed[:, :3], rtol=1e-5, atol=1e-6)
    print("✓ Test 4 passed: no future leakage — past outputs unchanged")


# Chạy tất cả
test_cached_decode_matches_full()
test_weights_are_token_addressable()
test_cache_grows_with_sequence()
test_no_future_leakage()
```

**Cách đọc kết quả:**
- Nếu Test 1 fail → kiểm tra `causal mask` hoặc `past_len` offset.
- Nếu Test 4 fail → mask sai, model đang "nhìn" tương lai.
- Cả 4 tests đều phải pass trước khi đo benchmark — benchmark trên implementation sai là vô nghĩa.

## 5. Benchmark / Trade-offs

### 5.1 Tách prefill và decode

Đừng gộp chung. Hai phase có bottleneck khác nhau:

| Phase | Work chính | MLA cost | Fixed-state cost |
|---|---:|---:|---:|
| **Prefill** ($S$ tokens) | Chấm toàn bộ $S\times S$ (có thể chunkwise) | Vẫn $O(S^2)$ scores nhưng mỗi entry nhỏ hơn | Chunkwise parallel, $O(S)$ state updates |
| **Decode** (1 token) | Chấm 1 query với $S$ history | $O(S)$ reads + $O(S)$ scores — tăng với $S$ | $O(1)$ — đọc state cố định |

### 5.2 Raw KV bytes — nhìn slope thay vì một con số

```python
def mha_cache_bytes(B, L, S, H, d_h, bytes_per_element=2):
    return B * L * S * (2 * H * d_h) * bytes_per_element


def mla_cache_bytes(B, L, S, d_c, d_rope, bytes_per_element=2):
    return B * L * S * (d_c + d_rope) * bytes_per_element


def fixed_state_bytes(B, L, H, d_k, d_v, bytes_per_element=2):
    # Shape accounting cho một matrix state minh họa — không phải KDA/Mamba thực
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
```

Kết quả cần đọc theo **shape trend**:
- MHA tăng tuyến tính với slope lớn.
- MLA tăng tuyến tính với slope nhỏ hơn (~14× trong ví dụ).
- Fixed-state nằm ngang theo $S$.

> [!warning] Đừng suy latency từ bytes
> `Projection absorption`, kernels, `memory bandwidth`, batching và hardware có thể thay đổi throughput. Công thức trên chỉ là `retained tensors`. Hãy benchmark trên target implementation, dtype (BF16/FP8) và hardware nếu cần quyết định deployment. Các số cache/throughput trong DeepSeek-V2 là author-reported cho config của họ, không phải universal conversion.[^deepseek-v2-2024]

### 5.3 Khi nào chọn gì?

| Mục tiêu | Ưu tiên | Lựa chọn |
|---|---|---|
| Retrieval chính xác trên context dài (cần chỉ vào token cụ thể) | Token-addressability | MLA / MHA / GQA |
| Context cực dài + memory cố định | Bounded state | Fixed-state (KDA, Mamba-2, DeltaNet) |
| Cân bằng cả hai | Giảm slope nhưng giữ retrieval | **Hybrid** (ví dụ 3×KDA + 1×MLA)[^kimi-linear-2025] |

## 6. Debug checklist

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên |
|---|---|---|
| Cache shape `(B, H, S, d)` thay vì `(B, S, d_c)` | Đang cache K/V đã expand, chưa cache latent | `present.shape` có chứa $S$ × $d_c$ không? |
| `cached decode != full forward` (Test 1 fail) | `past_len` offset sai hoặc causal mask sai | In `past_len`, `q_pos`, `k_pos` và `causal` matrix |
| Future leakage (Test 4 fail) | Mask dùng `>=` thay vì `<=`, hoặc thiếu `masked_fill(-inf)` | Kiểm tra `scores` trước softmax có `-inf` ở future không |
| Throughput không tăng dù cache nhỏ hơn | Bottleneck là compute/bandwidth, không phải capacity | Profile riêng prefill vs decode, đo `memory bandwidth` |
| `query compression` không giảm cache | Hiểu nhầm — nó giảm `activation memory` khi training, không giảm decode cache | Đọc lại Section 2.4[^deepseek-v2-2024] |
| OOM ở context dài dù đã MLA | $S$ vẫn nhân với $L$ và $B$; batch lớn vẫn OOM | Tính $M_{MLA}=BLS(d_c+d_h^R)p$ với $B,L,S$ thực tế |

## 7. Giới hạn & bước tiếp theo

**Lab này không chứng minh:**
- Quality parity giữa MLA và MHA/GQA — cần ablation trên cùng data và task.[^deepseek-v2-2024]
- Speedup thực tế — phụ thuộc kernel, dtype, hardware. Toy `torch.cat` là teaching, không phải serving (paged blocks).[^deepseek-v2-2024]
- Fixed-state có luôn kém retrieval — hybrid có thể bù đắp, nhưng trade-off phụ thuộc workload.[^kimi-linear-2025]

**Học tiếp theo (theo roadmap):**
1. [Linear attention như fixed-state associative memory — bài học cho người mới](linear-attention-fixed-state-associative-memory-beginners-guide.md) — hiểu `S_t` và `capacity interference`.
2. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — cách delta correction và decay cải thiện fixed-state.
3. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — vì sao periodic MLA bù retrieval limits của KDA.[^kimi-linear-2025]
4. [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) và [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md) — các kỹ thuật giảm cache ở serving layer.

**Bài tập đề xuất:**
1. Vẽ `context length → raw cache GiB` cho MHA và MLA với dimensions của model bạn chọn.
2. Sửa `ToyLatentAttention` để cache thêm `position key` nhỏ; xác nhận cache width = $d_c + d_h^R$.
3. In `step_w[0,0,0]` và chứng minh vector có đúng $S$ weights — dấu hiệu token-addressability.
4. Thay `d_latent` từ 32 xuống 4, train toy trên copy task và quan sát quality/capacity trade-off.
5. Implement additive fixed-state $S_t = S_{t-1} + \phi(k_t)^T v_t$; so sánh state shapes ở 128 và 8,192 tokens.
6. Đọc [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) và giải thích vì sao total model state vẫn sequence-growing dù đa số layers là fixed-state.

## Relationships

- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng lý thuyết, code và memory experiment cho MLA.
- **Builds on:** [Multi-head Latent Attention](multi-head-latent-attention.md), [KV caching](kv-caching.md) và [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md).
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — nơi history được aggregate vào bounded recurrent state thay vì giữ per-token latent slots.
- **Prepares for:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), [Structured State Space Duality](structured-state-space-duality.md) và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md).
- **Contextualizes:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — nơi periodic MLA bù retrieval limits của fixed-state KDA.[^kimi-linear-2025]

## Evidence limits

Cơ chế, formulas và dimensions DeepSeek-V2 được lấy từ primary technical report. Các so sánh quality, cache reduction và throughput là author-run, architecture- và config-specific; bài này không tái lập chúng. Fixed-state contrast dựa trên primary associative-memory analysis và Kimi Linear report. Phần cost decomposition, toy code, tests, checklist và ví dụ số học là **pedagogical synthesis** — toy code không implement full production MLA và không dùng để suy ra quality hay speedup.[^deepseek-v2-2024][^fast-weight-programmers-2021][^kimi-linear-2025]

[^deepseek-v2-2024]: DeepSeek-AI, "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model," arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and Appendices C–D.
[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, "Linear Transformers Are Secretly Fast Weight Programmers," ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4.
[^kimi-linear-2025]: Kimi Team, "Kimi Linear: An Expressive, Efficient Attention Architecture," arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 1–3 and 6.
