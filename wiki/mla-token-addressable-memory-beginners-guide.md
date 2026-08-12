---
type: Synthesis
title: "MLA và token-addressable memory — bài học cho người mới"
description: A beginner-first course on how MLA compresses each token's KV representation while preserving token-addressable softmax retrieval, why its cache still grows with context, and how it contrasts with fixed-state memory.
tags: [mla, attention, kv-cache, token-addressable-memory, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T12:14:42+07:00 }
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

`Multi-head Latent Attention` (MLA) không xóa `KV cache`; nó thay K/V lớn của mỗi token bằng một `KV latent` nhỏ dùng chung giữa các heads, cộng với một `rotary key` nhỏ cho position. Vì mỗi token vẫn có một cache entry riêng và query mới vẫn tạo attention weight cho từng token cũ, MLA vẫn là **token-addressable softmax attention**. Nó giảm số bytes **trên mỗi token**, nhưng tổng cache và lượng history phải đọc vẫn tăng tuyến tính theo `context length`. Đây là mốc so sánh quan trọng trước khi học `fixed-state memory`, nơi nhiều token được gộp vào một state có kích thước không tăng theo sequence nhưng không còn các slot độc lập cho từng token.[^deepseek-v2-2024][^fast-weight-programmers-2021]

> [!success] Mục tiêu
> Sau bài này, bạn có thể:
> 1. phân biệt `compression per token` với `fixed-state`;
> 2. suy ra memory growth của MHA, MLA và fixed-state;
> 3. giải thích `low-rank KV joint compression` và `decoupled RoPE`;
> 4. chỉ ra vì sao MLA vẫn `token-addressable`;
> 5. implement một MLA-like content path tối giản và test cached decode;
> 6. chọn đúng baseline khi đọc một long-context architecture.

Bài này giả định bạn đã biết Q/K/V, causal mask và `KV caching`. Nếu chưa, nên học [Attention: beginner's guide](attention-beginner-guide.md) và [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) trước. Code bên dưới là **pedagogical implementation**, không phải kernel MLA production.

## 1. Hai câu hỏi khác nhau: state có nhỏ không, và có tăng theo context không?

Một optimization có thể làm cache nhỏ hơn mà không làm cache trở thành fixed-size. Luôn tách hai trục:

1. **Per-token state:** mỗi token mới cần thêm bao nhiêu elements?
2. **Sequence scaling:** số elements tổng có tăng khi thêm token không?

Giả sử một request có:

- $B$: batch size;
- $L$: số attention layers;
- $S$: số cached tokens;
- $H$: số attention heads;
- $d_h$: dimension của một head;
- $p$: bytes trên mỗi element.

Với standard MHA, mỗi layer cache một K và một V cho từng head của từng token:

$$
M_{MHA}=BLS(2Hd_h)p.
$$

Nếu một architecture giảm phần trong ngoặc từ $2Hd_h$ xuống một số nhỏ hơn $r$, memory trở thành:

$$
M=BLSrp.
$$

Cache đã nhỏ hơn theo hệ số $2Hd_h/r$, nhưng vẫn tỷ lệ với $S$. Đó chính là kiểu cải thiện của MLA. `Fixed-state memory` khác về bản chất: recurrent state có shape do feature dimensions quyết định, không có sequence axis $S$:

$$
M_{fixed}\approx BLH(d_kd_v)p,
$$

có thể cộng thêm normalization state hoặc gates tùy mechanism. Khi $S$ tăng, state shape này không tăng; đổi lại, token cũ không còn nằm trong các slot tách biệt.

> [!important] Quy tắc đọc paper
> “Giảm KV cache 90%” không đồng nghĩa với “cache không tăng theo context”. Hãy tìm công thức có còn thừa số `sequence length` hay không.

## 2. Baseline: vì sao standard attention là token-addressable?

Ở một head, output tại token $t$ là:

$$
o_t=\sum_{j=1}^{t}\alpha_{t,j}v_j,
\qquad
\alpha_{t,j}=\operatorname{softmax}_j
\left(\frac{q_t^Tk_j}{\sqrt{d_h}}\right).
$$

Index $j$ có ý nghĩa rõ ràng: nó trỏ tới token thứ $j$ trong history. Query $q_t$ tạo một score riêng với từng $k_j$, rồi dùng weight riêng để lấy $v_j$. Vì vậy:

- cache có một K/V slot cho mỗi token;
- attention weights có sequence axis dài $S$;
- query có thể ưu tiên một position cụ thể;
- decode step mới vẫn phải đọc/chấm điểm history dài $S$.

`Token-addressable` không có nghĩa model chắc chắn nhớ hoặc truy xuất đúng mọi token. Nó chỉ mô tả **cấu trúc retrieval**: từng token vẫn có entry riêng mà query có thể chấm điểm trực tiếp.

## 3. Ý tưởng cốt lõi của MLA: cache latent, không cache K/V đã expand

Với hidden state $h_t\in\mathbb{R}^{d}$, MLA tạo một joint latent nhỏ:

$$
c_t^{KV}=W^{DKV}h_t,
\qquad c_t^{KV}\in\mathbb{R}^{d_c},
$$

rồi tạo content key và value từ cùng latent:

$$
k_t^C=W^{UK}c_t^{KV},
\qquad
v_t^C=W^{UV}c_t^{KV}.
$$

Điểm khác standard MHA nằm ở state được giữ qua decode steps:

```text
MHA cache at token t:
    [K of all heads | V of all heads]       size ≈ 2 H d_h

MLA cache at token t:
    [joint KV latent c_t | rotary key k_t^R] size = d_c + d_h^R
```

MLA không cần lưu materialized $k_t^C,v_t^C$ cho từng token. Theo DeepSeek-V2, matrix associativity cho phép hấp thụ (`absorb`) up-projections vào query/output paths trong inference.[^deepseek-v2-2024]

Với content score:

$$
q_t^T k_j^C=q_t^TW^{UK}c_j^{KV}
=\left((W^{UK})^Tq_t\right)^Tc_j^{KV},
$$

query có thể được transform trước rồi chấm trực tiếp với cached latent. Tương tự, linear value up-projection có thể được kết hợp với output projection thay vì expand mọi cached value trước mỗi query. Đây là optimization đại số; nó không biến nhiều token thành một state chung.

### `Low-rank` ở đây có nghĩa gì?

Mapping $h_t\rightarrow c_t^{KV}\rightarrow(k_t^C,v_t^C)$ đi qua bottleneck $d_c\ll Hd_h$. K và V content vì thế cùng được sinh từ một latent có dimension thấp hơn tổng K/V width.

Điều này khác với:

- **quantization:** giảm bits trên mỗi element;
- **token eviction:** bỏ một số token entries;
- **GQA/MQA:** share whole K/V heads giữa query heads;
- **fixed-state recurrence:** gộp history vào một state không có sequence axis.

Các kỹ thuật có thể được kết hợp, nhưng chúng thay đổi những trục khác nhau.

## 4. Vì sao cần `decoupled RoPE`?

Nếu áp dụng RoPE trực tiếp lên content key sau up-projection:

$$
k_{t}^{C,R}=R_tW^{UK}c_t^{KV},
$$

position-dependent rotation $R_t$ nằm giữa up-projection và latent. Ta không thể dùng một projection cố định để hấp thụ $W^{UK}$ cho mọi cached position, vì $R_t$ thay đổi theo $t$ và matrix multiplication không commutative. Nếu phải reconstruct lại position-rotated key cho toàn prefix ở mỗi step, mục tiêu inference efficiency bị phá vỡ.[^deepseek-v2-2024]

DeepSeek-V2 tách content path và position path:

$$
q_{t,i}=[q_{t,i}^{C};q_{t,i}^{R}],
\qquad
k_{t,i}=[k_{t,i}^{C};k_t^{R}].
$$

Trong đó:

- $q_{t,i}^{R}$ là rotary query riêng cho head $i$;
- $k_t^R$ là rotary key được share giữa heads;
- content K/V vẫn đi qua joint latent;
- cache giữ cả $c_t^{KV}$ và $k_t^R$.

Attention vẫn chạy theo từng token:

$$
o_{t,i}=\sum_{j=1}^{t}
\operatorname{softmax}_j
\left(
\frac{q_{t,i}^Tk_{j,i}}{\sqrt{d_h+d_h^R}}
\right)v_{j,i}^{C}.
$$

`Query compression` cũng xuất hiện trong MLA để giảm training activation memory, nhưng query của token hiện tại không phải history state cần giữ qua decode steps. Vì vậy query compression tự nó không làm KV cache nhỏ hơn.[^deepseek-v2-2024]

## 5. Memory accounting: MLA giảm slope, không xóa slope

MLA của DeepSeek-V2 cache trên mỗi token, mỗi layer:

$$
d_c+d_h^R
$$

elements. Tổng raw cache xấp xỉ:

$$
M_{MLA}=BLS(d_c+d_h^R)p.
$$

So với:

$$
M_{MHA}=BLS(2Hd_h)p.
$$

Compression ratio theo element count là:

$$
\frac{M_{MHA}}{M_{MLA}}
=\frac{2Hd_h}{d_c+d_h^R}.
$$

Trong configuration DeepSeek-V2, $d_c=4d_h$ và $d_h^R=d_h/2$, nên MLA dùng khoảng $4.5d_h$ elements/token/layer, được paper mô tả tương đương GQA có 2.25 KV groups. Đây là configuration-specific comparison, không phải hằng số chung của mọi MLA variant.[^deepseek-v2-2024]

### Ví dụ số học

Giả sử:

- $L=32$, $B=1$, $H=32$, $d_h=128$;
- BF16, nên $p=2$ bytes;
- MLA dùng $d_c=512$, $d_h^R=64$.

MHA cần mỗi token trên toàn model:

$$
32\times(2\times32\times128)\times2
=524{,}288\text{ bytes}\approx0.5\text{ MiB}.
$$

MLA cần:

$$
32\times(512+64)\times2
=36{,}864\text{ bytes}\approx0.035\text{ MiB}.
$$

Ở 1,024 tokens, hai con số raw cache xấp xỉ 512 MiB và 36 MiB; ở 32,768 tokens, cả hai cùng tăng 32 lần. MLA có đường memory–context với slope thấp hơn nhiều, nhưng slope vẫn khác zero.

Production memory còn phụ thuộc cache dtype, allocator, block layout, batching, prefix sharing và temporary buffers. Công thức trên chỉ accounting các retained cache tensors.

## 6. Tại sao MLA vẫn là `token-addressable memory`?

Sau khi cache $S$ tokens, MLA giữ:

$$
C^{KV}_{1:S}=[c_1^{KV},c_2^{KV},\ldots,c_S^{KV}]
$$

và position keys tương ứng. Sequence axis vẫn có $S$ entries. Với query mới, attention logits vẫn có shape đại ý:

```text
(B, H, 1, S)
```

Mỗi cột cuối cùng tương ứng một token position. Vì vậy MLA vẫn có các tính chất sau:

| Câu hỏi | MLA | Fixed-state memory |
|---|---:|---:|
| Có một state entry mới cho mỗi token? | Có | Không |
| Query tạo score/weight riêng cho từng position? | Có | Không theo recurrent read chuẩn |
| Có thể chỉ vào token thứ `j` qua attention axis? | Có | Không còn slot `j` độc lập |
| Decode state tăng theo $S$? | Có | Không |
| Nhiều associations có bị superpose vào cùng state? | Không theo cache layout | Có |

Compression có thể làm representation của mỗi token hẹp hơn, nhưng không xóa identity theo position của entry đó. Đây là lý do “latent” trong MLA không nên bị hiểu thành “một latent duy nhất tóm tắt cả context”. Đúng hơn là **một latent cho mỗi token, tại mỗi MLA layer**.

## 7. Fixed-state đổi memory scaling bằng một trade-off khác

Một linear-attention associative memory tối giản cập nhật:

$$
S_t=S_{t-1}+\phi(k_t)^Tv_t,
$$

và đọc:

$$
o_t=\phi(q_t)S_t.
$$

State $S_t\in\mathbb{R}^{d_k\times d_v}$ có cùng shape ở token 10 và token 1,000,000. Nhưng outer products của nhiều tokens cùng được cộng vào matrix đó. Query không tạo vector weights dài $t$ để chọn một token slot; nó đọc tổ hợp associations đã superpose.

Điều này tạo trade-off:

- **MLA:** sequence-growing compressed slots, direct token-level retrieval, softmax over history;
- **fixed-state:** bounded state, recurrent update/read, nhưng có capacity interference và không giữ isolated slot cho mọi token.

Phân tích associative memory trong `Linear Transformers Are Secretly Fast Weight Programmers` cho thấy additive memory có giới hạn từ orthogonality của mapped keys; đó là giới hạn biểu diễn, không phải một ngưỡng failure cố định cho mọi model.[^fast-weight-programmers-2021]

Hybrid architecture tồn tại vì hai phía giải quyết bottleneck khác nhau. Kimi Linear, chẳng hạn, dùng ba fixed-state KDA layers rồi một global MLA layer: KDA giảm sequence-growing state ở phần lớn layers, còn periodic MLA giữ khả năng token-level retrieval. Report này nêu tối đa 75% KV-cache reduction so với full MLA theo layer ratio, nhưng model tổng vẫn có cache tăng theo context ở các MLA layers.[^kimi-linear-2025]

## 8. Cost không chỉ là cache capacity

Đừng chỉ so raw bytes. Với decode một token mới:

### MLA

- append một latent và một rotary key;
- tạo/chuyển đổi query mới;
- chấm điểm query với $S$ cached entries;
- softmax trên $S$ positions;
- retrieve value content;
- cache reads và attention work tăng với $S$.

### Fixed-state recurrence

- update state bằng token mới;
- read state có fixed shape;
- recurrent decode state và per-step recurrent work không tăng theo $S$;
- nhưng representation phải nén/superpose history và có thể mất exact retrieval.

`Prefill` là câu chuyện khác: implementation có thể dùng chunkwise/parallel algorithms thay vì chạy Python recurrence từng token. Vì vậy cần đo riêng `prefill latency`, one-token `decode latency`, memory capacity và quality.

## 9. PyTorch lab: một MLA-like content cache tối giản

Code sau chỉ implement **content path** $c^{KV}\rightarrow K^C,V^C$. Nó cố ý bỏ `decoupled RoPE`, query compression, projection absorption và optimized kernels để làm rõ cache shape. Việc reconstruct K/V từ latent trong code là dễ đọc nhưng không phải đường inference tối ưu được mô tả trong DeepSeek-V2.

```python
import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class ToyLatentAttention(nn.Module):
    """MLA-like content path for studying cache semantics, not production MLA."""

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

    def _heads(self, x):
        B, T, D = x.shape
        return x.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,                         # (B, T_new, D)
        past_latent: Optional[torch.Tensor] = None,  # (B, S_past, d_c)
        use_cache: bool = False,
    ):
        B, T_new, D = x.shape
        q = self._heads(self.q_proj(x))
        c_new = self.kv_down(x)                  # one latent per new token

        if past_latent is None:
            c_all = c_new
            past_len = 0
        else:
            if past_latent.shape[:1] != (B,):
                raise ValueError("cache batch size does not match")
            c_all = torch.cat((past_latent, c_new), dim=1)
            past_len = past_latent.size(1)

        # Pedagogical reconstruction. Optimized MLA absorbs projections.
        k = self._heads(self.k_up(c_all))         # (B, H, S, d_h)
        v = self._heads(self.v_up(c_all))
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        S = c_all.size(1)
        q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]
        k_pos = torch.arange(S, device=x.device)[None, :]
        causal = k_pos <= q_pos
        scores = scores.masked_fill(~causal, float("-inf"))

        weights = F.softmax(scores, dim=-1)       # last axis indexes tokens
        y = weights @ v
        y = y.transpose(1, 2).contiguous().view(B, T_new, D)
        present = c_all if use_cache else None
        return self.out_proj(y), present, weights
```

Ba observations trực tiếp từ code:

1. `past_latent.shape == (B, S, d_latent)`: latent nhỏ nhưng vẫn có sequence axis `S`.
2. `weights.shape == (B, H, T_new, S)`: query vẫn address từng cached token.
3. Mỗi decode step dùng `torch.cat` để thêm một entry: cache không fixed-state.

### Test cached decode khớp full causal forward

Vì toy module dùng cùng content equations ở hai paths, output token cuối phải khớp trong numerical tolerance:

```python
@torch.inference_mode()
def test_cached_decode_matches_full():
    torch.manual_seed(0)
    layer = ToyLatentAttention(d_model=32, n_heads=4, d_latent=8).eval()
    x = torch.randn(2, 7, 32)

    full_y, _, full_w = layer(x, use_cache=False)

    _, cache, _ = layer(x[:, :6], use_cache=True)       # prefill
    step_y, cache, step_w = layer(
        x[:, 6:7], past_latent=cache, use_cache=True    # one-token decode
    )

    torch.testing.assert_close(step_y, full_y[:, 6:7], rtol=1e-5, atol=1e-6)
    assert cache.shape == (2, 7, 8)
    assert step_w.shape == (2, 4, 1, 7)
    print("cached decode matches; cache and weights still index 7 tokens")


test_cached_decode_matches_full()
```

> [!warning] Test này không chứng minh parity với full MLA
> Full MLA còn có `decoupled RoPE`, query compression và inference-time projection absorption. Test chỉ chứng minh semantics của toy joint-latent content cache và làm lộ sequence axis.

## 10. Lab memory: nhìn slope thay vì chỉ nhìn một con số

Hàm sau so raw cache bytes theo context length. `fixed_state_bytes` là shape accounting cho một matrix state minh họa, không phải implementation của KDA/Mamba.

```python
def mha_cache_bytes(B, L, S, H, d_h, bytes_per_element=2):
    return B * L * S * (2 * H * d_h) * bytes_per_element


def mla_cache_bytes(B, L, S, d_c, d_rope, bytes_per_element=2):
    return B * L * S * (d_c + d_rope) * bytes_per_element


def fixed_state_bytes(B, L, H, d_k, d_v, bytes_per_element=2):
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

- MHA tăng tuyến tính với slope lớn;
- MLA tăng tuyến tính với slope nhỏ hơn;
- fixed-state nằm ngang theo $S$ trong accounting này.

Đừng suy ra latency trực tiếp từ bytes. Projection absorption, kernels, memory bandwidth, batching và hardware có thể thay đổi throughput. Hãy benchmark target implementation nếu cần quyết định deployment.

## 11. Các nhầm lẫn thường gặp

### “MLA là fixed-state vì nó dùng một latent”

Sai. Đó là một latent **cho mỗi token**. Sau $S$ tokens có $S$ latents trên mỗi MLA layer, cộng position cache.

### “Low-rank compression nghĩa là attention gần đúng theo token”

Không nhất thiết theo nghĩa bỏ token hoặc sparse positions. MLA vẫn chạy softmax trên toàn bộ cached positions; bottleneck nằm trong representation K/V. Quality impact phải được đánh giá thực nghiệm.

### “MLA làm decode $O(1)$ theo context”

Sai. Query mới vẫn tương tác với history dài $S$. Cache bytes, cache reads và số token-level scores vẫn tăng với context.

### “Projection absorption làm cache biến mất”

Sai. Absorption tránh materialize expanded content K/V; cached $c_j^{KV}$ và rotary keys của từng token vẫn tồn tại.

### “Query compression giảm decode cache”

Sai. Query hiện tại được dùng để đọc history rồi không cần giữ như K/V history. Query compression chủ yếu nhắm training activation memory trong thiết kế DeepSeek-V2.[^deepseek-v2-2024]

### “Cache nhỏ hơn luôn cho throughput cao hơn cùng tỷ lệ”

Không được bảo đảm. Throughput còn phụ thuộc compute, kernels, memory bandwidth, batch scheduling và model architecture. Các số cache/throughput trong DeepSeek-V2 là author-reported cho configuration của họ, không phải universal conversion rule.[^deepseek-v2-2024]

## 12. Checklist khi phân tích một long-context mechanism

Hãy trả lời lần lượt:

1. **State unit là gì?** K/V head, per-token latent, compressed block hay recurrent matrix?
2. **Có sequence axis không?** Shape có chứa $S$ không?
3. **Query address cái gì?** Từng token, từng block hay state đã aggregate?
4. **Memory formula là gì?** Tách $B,L,S,H,d,p$ thay vì chỉ chép phần trăm.
5. **Decode work có đọc toàn history không?** Cache capacity nhỏ không đồng nghĩa per-step work fixed.
6. **Compression có lossy không?** Low-rank, quantization, eviction và aggregation có failure modes khác nhau.
7. **Position information nằm đâu?** RoPE, decoupled path, NoPE hay recurrent transition?
8. **Evidence là component ablation hay full-system result?** Không gán throughput toàn model cho riêng MLA nếu nhiều thay đổi cùng lúc.
9. **Baseline là gì?** MHA, GQA, full MLA hay fixed-state hybrid phải được matched rõ ràng.
10. **Production conditions là gì?** Context, batch, dtype, hardware và kernel quyết định kết quả thực tế.

## 13. Bài tập

1. Dùng các dimensions của một model bạn chọn để vẽ `context length → raw cache GiB` cho MHA và MLA.
2. Sửa `ToyLatentAttention` để cache thêm một `position key` nhỏ; xác nhận cache width trở thành `d_latent + d_rope`.
3. In `step_w[0, 0, 0]` và chứng minh vector có đúng $S$ weights — dấu hiệu trực tiếp của token-addressability.
4. Thay `d_latent` từ 32 xuống 4, train toy model trên copy task và quan sát quality/capacity trade-off; không so random untrained outputs.
5. Implement additive fixed-state update $S_t=S_{t-1}+\phi(k_t)^Tv_t$; so sánh state shapes ở 128 và 8,192 tokens.
6. Benchmark riêng prefill và one-token decode. Không dùng memory formula để thay cho latency measurement.
7. Đọc [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) và giải thích vì sao periodic MLA làm total model state vẫn sequence-growing dù đa số layers là fixed-state.

## Kết luận

MLA là baseline tốt nhất để bước từ efficient dense attention sang fixed-state long-context mixing vì nó làm rõ một distinction cơ bản:

```text
MHA:       nhiều bytes/token × số token
MLA:       ít bytes/token   × số token
fixed-state: một state có shape cố định, không có slot riêng cho mọi token
```

MLA giữ lợi thế của global softmax retrieval: query vẫn có thể chấm điểm từng token entry. Cái giá là cache capacity và decode history access vẫn tăng theo context. Fixed-state đổi scaling đó bằng cách aggregate history vào state bounded, nhưng phải chấp nhận superposition, capacity interference và retrieval không còn token-addressable theo cách attention chuẩn. Hybrid designs kết hợp hai loại layer chính vì không có phía nào miễn phí.

## Relationships

- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng lý thuyết, code và memory experiment cho MLA.
- **Builds on:** [Multi-head Latent Attention](multi-head-latent-attention.md), [KV caching](kv-caching.md), và [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md).
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), nơi history được aggregate vào bounded recurrent state thay vì giữ per-token latent slots.
- **Prepares for:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), [Structured State Space Duality](structured-state-space-duality.md), và [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md).
- **Contextualizes:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), nơi periodic MLA bù retrieval limits của fixed-state KDA.[^kimi-linear-2025]

## Evidence limits

Cơ chế, formulas và dimensions DeepSeek-V2 được lấy từ primary technical report. Các so sánh quality, cache reduction và throughput của report là author-run, architecture- và configuration-specific; bài này không tái lập chúng. Fixed-state contrast dựa trên primary associative-memory analysis và Kimi Linear report. Phần cost decomposition, toy code, tests, checklist và ví dụ số học là **pedagogical synthesis**; toy code không implement full production MLA và không dùng để suy ra quality hay speedup.[^deepseek-v2-2024][^fast-weight-programmers-2021][^kimi-linear-2025]

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and Appendices C–D.
[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4.
[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 1–3 and 6.
