---
type: Synthesis
title: "MQA/GQA: giảm KV cache khi decode — bài học cho người mới"
description: A beginner-first course on how MQA and GQA reduce decode-time KV-cache memory and bandwidth, with PyTorch implementation, correctness tests, and measurement guidance.
tags: [attention, multi-query-attention, grouped-query-attention, kv-cache, decoding, inference, pytorch, learning-roadmap]
status: stable
created: 2026-08-11
generated:
  by: llm-wiki-agent/1
  at: 2026-08-11T00:00:00Z
sources:
  - id: mqa-summary
    resource: ../raw/MQA.md
    title: "MQA overview (Vietnamese summary)"
  - id: gqa-summary
    resource: ../raw/GQA.md
    title: "GQA overview (Vietnamese summary)"
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
---

# MQA/GQA: giảm KV cache khi decode — bài học cho người mới

`Multi-Query Attention` (MQA) và `Grouped-Query Attention` (GQA) giữ nhiều `query heads` nhưng dùng ít `key/value heads` hơn `Multi-Head Attention` (MHA). Vì `KV cache` được lưu theo số `KV heads`, chúng giảm trực tiếp `memory` và lượng K/V phải đọc ở `autoregressive decode`; GQA chọn số KV heads ở giữa MHA và MQA để đổi một phần tiết kiệm đó lấy `representational capacity` cao hơn.[^mqa-summary][^gqa-summary]

> [!success] Mục tiêu
> Sau bài này, bạn có thể giải thích chuỗi **MHA → MQA → GQA**, tính chính xác KV-cache bytes, implement GQA mà không copy vật lý K/V cho mọi query head, kiểm chứng cache semantics, và đo riêng `memory` cùng `decode latency` trước khi kết luận về quality–bandwidth trade-off.

Bài này là **pedagogical synthesis** cho Stage 6 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Nó giả định bạn đã hiểu causal attention và `KV caching`; nếu chưa, hãy học [Attention: beginner's guide for causal language models](attention-beginner-guide.md) và [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) trước. Code là minimal PyTorch để học mechanics, không phải production inference engine.

## 1. Vì sao chỉ `decode` mới làm vấn đề này nổi bật?

Một causal LLM phục vụ prompt qua hai pha:

```text
prompt tokens ── prefill ──► KV cache(prompt) ──► sample y1
                                              │
                 y1 ── decode ──► append K/V(y1) ──► sample y2
```

- Trong **`prefill`**, model nhận nhiều prompt tokens cùng lúc. Nó tính K/V cho prompt và có thể dùng matrix operations lớn.
- Trong **`decode`**, model thường nhận chỉ một token mới cho mỗi request. Query mới vẫn phải so khớp và trộn với K/V của toàn bộ context đã cache.

`KV cache` tránh tính lại K/V của prefix, nhưng không làm decode thành $O(1)$ theo context length: với cache length $S$, token mới vẫn cần đọc K/V của $S$ positions. Vì thế decode dài thường nhạy với `memory bandwidth` và KV-cache capacity.[^mqa-summary]

> [!note] Đừng gộp `prefill latency` và `decode latency`
> MQA/GQA có thể giảm K/V projection work và cache writes ở prefill, nhưng mục tiêu chính của chúng là giảm K/V cache **read traffic** trong one-token decode. `TTFT` và `TPOT` là metric cho hai phần khác nhau của một request; xem [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md).

## 2. Baseline: `Multi-Head Attention` (MHA)

Với $H_Q$ query heads, head width $d_h$, và input hidden state $X$, MHA tạo projection độc lập cho mọi head:

$$
Q_i=XW_i^Q,\qquad K_i=XW_i^K,\qquad V_i=XW_i^V,
$$

$$
O_i=\operatorname{softmax}\left(
\frac{Q_iK_i^\top}{\sqrt{d_h}}+M
\right)V_i.
$$

$M$ là causal mask: query tại position $t$ không được đọc key ở future position $>t$. Sau đó các $O_i$ được concatenate và qua output projection. Đây là `scaled dot-product attention` nhiều head tiêu chuẩn.[^vaswani-transformer-2017]

Với MHA:

$$
H_K=H_V=H_{KV}=H_Q.
$$

Ví dụ có 8 heads:

```text
Q0 → K0, V0      Q4 → K4, V4
Q1 → K1, V1      Q5 → K5, V5
Q2 → K2, V2      Q6 → K6, V6
Q3 → K3, V3      Q7 → K7, V7
```

Mỗi head có thể học K/V subspace riêng. Đây là capacity hữu ích, nhưng cũng nghĩa là cache phải lưu 8 bản K và 8 bản V cho từng token ở từng layer.

## 3. `Multi-Query Attention` (MQA): nhiều Q, một K/V

MQA vẫn có $H_Q$ query projections riêng, nhưng chỉ có **một** key head và một value head:

$$
Q_i=XW_i^Q,\qquad K=XW^K,\qquad V=XW^V,
$$

$$
O_i=\operatorname{softmax}\left(
\frac{Q_iK^\top}{\sqrt{d_h}}+M
\right)V.
$$

Do đó:

$$
H_Q=H,\qquad H_K=H_V=H_{KV}=1.
$$

```text
Q0 ─┐
Q1 ─┤
Q2 ─┼──→ K0, V0  (shared)
... ─┤
Q7 ─┘
```

`Multi-Query` **không** có nghĩa là gộp mọi query thành một head. $Q_0,Q_1,\ldots,Q_{H-1}$ vẫn khác nhau, nên chúng có thể sinh attention weights khác nhau trên cùng K/V. Điều bị chia sẻ là representation để *match* (K) và content để *retrieve* (V).[^mqa-summary]

### Lợi và mất của MQA

- **Được:** K/V projections ít hơn, K/V cache nhỏ hơn, ít K/V bytes phải đọc hơn mỗi decode step.
- **Mất:** mọi query head phải dùng cùng K/V subspace. Các head vẫn chọn vị trí khác nhau, nhưng không còn value representations độc lập như MHA.

Nguồn MQA báo cáo chất lượng gần MHA trên WMT14 English–German trong cấu hình được thử, nhưng dev perplexity cao hơn nhẹ trên Billion Word. Đây là evidence theo các setup đó, không phải bảo đảm mọi model/task đều giữ quality.[^mqa-summary]

## 4. `Grouped-Query Attention` (GQA): điểm giữa MHA và MQA

GQA chia $H_Q$ query heads thành $H_{KV}$ groups. Mỗi group dùng một K head và một V head:

$$
1 < H_{KV} < H_Q,\qquad R=\frac{H_Q}{H_{KV}}.
$$

$R$ là số query heads chia sẻ một KV head. Với query head $i$, KV group là:

$$
g(i)=\left\lfloor\frac{i}{R}\right\rfloor,
$$

$$
O_i=\operatorname{softmax}\left(
\frac{Q_iK_{g(i)}^\top}{\sqrt{d_h}}+M
\right)V_{g(i)}.
$$

Ví dụ $H_Q=8$, $H_{KV}=2$, nên $R=4$:

```text
Q0, Q1, Q2, Q3 → K0, V0
Q4, Q5, Q6, Q7 → K1, V1
```

Hai endpoint là cùng một family:

| Layout | $H_{KV}$ | $R=H_Q/H_{KV}$ | Ý nghĩa |
|---|---:|---:|---|
| MHA | $H_Q$ | 1 | Mỗi Q head có K/V riêng |
| GQA | giữa 1 và $H_Q$ | giữa 1 và $H_Q$ | Một group Q heads share K/V |
| MQA | 1 | $H_Q$ | Mọi Q heads share một K/V |

Vì số K/V subspaces nhiều hơn MQA, GQA thường là compromise thực dụng: giảm mạnh cache nhưng ít ép sharing hơn. Báo cáo GQA trên T5-XXL cho GQA-8 score 47.1, MHA 47.2, và MQA 46.6; các inference times lần lượt là 0.28 s, 1.51 s, và 0.24 s. Các số này phụ thuộc TPUv4, workload, parallelization và model encoder–decoder của nghiên cứu, nên chỉ là benchmark có điều kiện.[^gqa-summary]

## 5. Tính `KV cache memory`: biến $H_{KV}$ là đòn bẩy

Ở mỗi layer, K hoặc V cache có shape thường dùng:

```text
(B, H_KV, S, d_h)
```

với $B$ là batch/cache sequences, $S$ là current cached length. Với $L$ layers và element width $p$ bytes, raw K/V tensor storage xấp xỉ:

$$
M_{KV}=2\,L\,B\,S\,H_{KV}\,d_h\,p\quad\text{bytes}.
$$

Hệ số 2 là K và V. Khi giữ $L,B,S,d_h,p$ cố định:

$$
\frac{M_{\mathrm{GQA}}}{M_{\mathrm{MHA}}}
=\frac{H_{KV}}{H_Q}=\frac{1}{R},
\qquad
\frac{M_{\mathrm{MQA}}}{M_{\mathrm{MHA}}}=\frac{1}{H_Q}.
$$

> [!example] Ví dụ cụ thể
> $L=32$, $B=1$, $S=4096$, $H_Q=32$, $d_h=128$, FP16/BF16 ($p=2$ bytes):
>
> - MHA ($H_{KV}=32$): $2$ GiB raw K/V.
> - GQA-8 ($H_{KV}=8$): $512$ MiB raw K/V.
> - MQA ($H_{KV}=1$): $64$ MiB raw K/V.
>
> Đây là tensor accounting, không phải GPU peak memory: weights, temporary buffers, allocator fragmentation, padding và request metadata chưa được tính.

Tỷ lệ trên cũng là lý do MQA/GQA giảm lượng K/V data lý tưởng cần đọc ở mỗi decode step. Tuy nhiên, đừng suy ra latency giảm đúng $R$ lần: query heads vẫn là $H_Q$, attention-score work vẫn tồn tại, và observed latency còn phụ thuộc kernel, context, batch, hardware, scheduling, tensor parallelism cùng bottleneck khác.[^mqa-summary][^gqa-summary]

## 6. Shapes cần thuộc trước khi code

Dùng layout `(B, heads, T, d_h)`:

| Tensor | MHA | GQA với $H_Q=8,H_{KV}=2$ |
|---|---|---|
| `q` | `(B, 8, T_new, d_h)` | `(B, 8, T_new, d_h)` |
| `k_new`, `v_new` | `(B, 8, T_new, d_h)` | `(B, 2, T_new, d_h)` |
| cached `k`, `v` | `(B, 8, S, d_h)` | `(B, 2, S, d_h)` |
| attention output | `(B, 8, T_new, d_h)` | `(B, 8, T_new, d_h)` |

GQA **không** lưu cache shape `(B, H_Q, S, d_h)`. Nếu code tạo `k.repeat_interleave(R, dim=1)` rồi giữ tensor ấy làm cache, bạn đã materialize lại MHA-sized K/V và xóa lợi ích memory chính.

## 7. Minimal PyTorch GQA với KV cache

Module dưới đây biểu diễn grouping trực tiếp bằng `einsum`: query được reshape thành `(B, H_KV, R, T, d_h)` để mỗi KV head phục vụ $R$ query heads. Nó không materialize copy K/V theo query-head dimension.

```python
import math
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

KV = Tuple[torch.Tensor, torch.Tensor]  # each: (B, H_KV, S, d_h)


class GroupedQueryAttention(nn.Module):
    def __init__(self, d_model: int, num_query_heads: int,
                 num_kv_heads: int):
        super().__init__()
        if d_model % num_query_heads != 0:
            raise ValueError("d_model must divide num_query_heads")
        if num_query_heads % num_kv_heads != 0:
            raise ValueError("num_query_heads must divide num_kv_heads")

        self.hq = num_query_heads
        self.hkv = num_kv_heads
        self.group_size = num_query_heads // num_kv_heads
        self.head_dim = d_model // num_query_heads

        # Q retains one d_h vector for every query head.
        self.q_proj = nn.Linear(d_model, self.hq * self.head_dim, bias=False)
        # K/V only create vectors for KV heads: smaller when H_KV < H_Q.
        self.k_proj = nn.Linear(d_model, self.hkv * self.head_dim, bias=False)
        self.v_proj = nn.Linear(d_model, self.hkv * self.head_dim, bias=False)
        self.out_proj = nn.Linear(self.hq * self.head_dim, d_model, bias=False)

    @staticmethod
    def _split(x: torch.Tensor, heads: int, head_dim: int) -> torch.Tensor:
        # (B, T, heads * d_h) -> (B, heads, T, d_h)
        B, T, _ = x.shape
        return x.view(B, T, heads, head_dim).transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,                         # (B, T_new, d_model)
        past_kv: Optional[KV] = None,
        use_cache: bool = False,
    ) -> tuple[torch.Tensor, Optional[KV]]:
        B, T_new, _ = x.shape
        q = self._split(self.q_proj(x), self.hq, self.head_dim)
        k_new = self._split(self.k_proj(x), self.hkv, self.head_dim)
        v_new = self._split(self.v_proj(x), self.hkv, self.head_dim)

        if past_kv is None:
            k, v, past_len = k_new, v_new, 0
        else:
            k_past, v_past = past_kv
            expected = (B, self.hkv)
            if k_past.shape[:2] != expected or v_past.shape[:2] != expected:
                raise ValueError("cache batch size or KV-head count mismatch")
            # Append on the sequence dimension, never on heads/features.
            k = torch.cat((k_past, k_new), dim=-2)
            v = torch.cat((v_past, v_new), dim=-2)
            past_len = k_past.size(-2)

        # Associate contiguous query-head groups with one KV head.
        # q_grouped: (B, H_KV, R, T_new, d_h)
        q_grouped = q.reshape(B, self.hkv, self.group_size, T_new,
                              self.head_dim)
        # scores: (B, H_KV, R, T_new, S)
        scores = torch.einsum("bhgtd,bhsd->bhgts", q_grouped, k)
        scores = scores / math.sqrt(self.head_dim)

        # Correct even when T_new > 1 and a cache already exists.
        S = k.size(-2)
        q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]
        k_pos = torch.arange(S, device=x.device)[None, :]
        causal = k_pos <= q_pos                   # (T_new, S)
        scores = scores.masked_fill(~causal[None, None, None], float("-inf"))

        probs = F.softmax(scores, dim=-1)
        # (B, H_KV, R, T_new, d_h) -> (B, H_Q, T_new, d_h)
        y = torch.einsum("bhgts,bhsd->bhgtd", probs, v)
        y = y.reshape(B, self.hq, T_new, self.head_dim)
        y = y.transpose(1, 2).contiguous().view(B, T_new, -1)

        present = (k, v) if use_cache else None
        return self.out_proj(y), present
```

### Chọn MHA, GQA, hoặc MQA bằng một tham số

```python
# d_model=512, H_Q=8, d_h=64 in all three configurations
mha = GroupedQueryAttention(512, num_query_heads=8, num_kv_heads=8)
gqa = GroupedQueryAttention(512, num_query_heads=8, num_kv_heads=2)
mqa = GroupedQueryAttention(512, num_query_heads=8, num_kv_heads=1)
```

- `num_kv_heads == num_query_heads` là MHA.
- `num_kv_heads == 1` là MQA.
- Giá trị giữa hai endpoint là GQA.

Đây là ba **architecture khác nhau**, có K/V projection shapes khác nhau. Vì vậy không so logits của checkpoint MHA và checkpoint GQA ngẫu nhiên rồi gọi difference là bug. Correctness test cần so cached và uncached execution của **cùng architecture/cùng weights**.

## 8. Kiểm chứng semantics trước khi benchmark

Với self-attention module độc lập, full forward trên $x_{1:T}$ phải khớp với prefill $x_{1:P}$ rồi cached forward $x_{P+1:T}$, trong numerical tolerance. Test này phát hiện mask offset, concatenate dimension và grouping errors.

```python
@torch.inference_mode()
def assert_cached_attention_matches(attn, x, prefix_len,
                                    rtol=1e-4, atol=1e-5):
    """x is the same input representation for both mathematical paths."""
    attn.eval()
    full, _ = attn(x, use_cache=False)

    first, cache = attn(x[:, :prefix_len], use_cache=True)
    rest, cache = attn(x[:, prefix_len:], past_kv=cache, use_cache=True)
    cached = torch.cat((first, rest), dim=1)

    torch.testing.assert_close(cached, full, rtol=rtol, atol=atol)
    assert all(k.size(-2) == x.size(1) and v.size(-2) == x.size(1)
               for k, v in (cache,))
    return cache


torch.manual_seed(0)
attn = GroupedQueryAttention(96, num_query_heads=6, num_kv_heads=2).eval()
x = torch.randn(2, 13, 96)
cache = assert_cached_attention_matches(attn, x, prefix_len=7)
print("cached GQA matches full GQA")
```

Trong một Transformer hoàn chỉnh, test cached-versus-uncached logits cần chạy toàn model, giữ cache riêng theo layer, tắt `dropout` bằng `eval()`, và dùng correct position offset (learned positions hoặc RoPE) cho token mới. Xem implementation/test đầy đủ ở [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md).

> [!warning] `repeat` có thể đúng về toán nhưng sai mục tiêu systems
> Nhiều API reference dùng `repeat_kv` để đưa K/V thành số query heads trước khi gọi attention generic. Kết quả attention vẫn đúng, nhưng nếu copy đó tồn tại trong retained cache hoặc temporary HBM traffic lớn, benchmark không còn đo lợi ích GQA thực tế. Hãy xác nhận kernel/backend của bạn hỗ trợ grouped K/V layout.

## 9. Đo `memory`: công thức phải khớp tensors

Đo bytes của tensor retained là cách trực tiếp nhất để kiểm tra layout toy model:

```python
def kv_cache_bytes(cache: KV) -> int:
    k, v = cache
    return k.numel() * k.element_size() + v.numel() * v.element_size()


@torch.inference_mode()
def build_cache(attn, batch, context_len, d_model, device):
    x = torch.randn(batch, context_len, d_model, device=device)
    _, cache = attn(x, use_cache=True)
    return cache


def expected_kv_bytes(layers, batch, context_len, kv_heads,
                      head_dim, bytes_per_element):
    return 2 * layers * batch * context_len * kv_heads * head_dim * bytes_per_element


# One attention layer, FP32 on the selected device.
device = "cuda" if torch.cuda.is_available() else "cpu"
for hkv in (8, 2, 1):
    layer = GroupedQueryAttention(512, 8, hkv).to(device).eval()
    cache = build_cache(layer, batch=1, context_len=1024,
                        d_model=512, device=device)
    print(f"H_KV={hkv}: {kv_cache_bytes(cache) / 2**20:.2f} MiB")
```

Trong đoạn code này, `$H_{KV}=2$` phải chiếm $2/8=25\%$ bytes của MHA `$H_{KV}=8$`; MQA chiếm $1/8=12.5\%$. Với $L$ layers, nhân raw per-layer result với $L$ nếu mọi layer có cùng layout/dtype.

Đừng dùng chỉ `torch.cuda.max_memory_allocated()` để xác nhận công thức: nó có cả model weights, activation/temporary tensors và allocator behavior. Nó vẫn hữu ích cho capacity planning, nhưng hãy báo rõ metric nào đang dùng.

## 10. Đo `decode latency` đúng câu hỏi

Đầu tiên kiểm tra logits/output equivalence. Sau đó đo **one-token decode at fixed cache length**; không trộn `prefill` vào phép đo nếu câu hỏi là GQA giảm cache-read cost bao nhiêu.

```python
import time


@torch.inference_mode()
def measure_one_token_decode_ms(attn, cache, d_model, repeats=100, warmup=20):
    """Measures this toy layer at a fixed cache length, including its cat append."""
    device = cache[0].device
    x_new = torch.randn(cache[0].size(0), 1, d_model, device=device)

    def run():
        attn(x_new, past_kv=cache, use_cache=True)

    for _ in range(warmup):
        run()
    if device.type == "cuda":
        torch.cuda.synchronize()
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        for _ in range(repeats):
            run()
        end.record()
        torch.cuda.synchronize()
        return start.elapsed_time(end) / repeats

    start = time.perf_counter()
    for _ in range(repeats):
        run()
    return 1e3 * (time.perf_counter() - start) / repeats


# Compare only after each independently initialized architecture passes its
# own cached-vs-full test. Use the same d_model, H_Q, dtype, cache length,
# batch, device, and benchmark protocol.
for hkv in (8, 2, 1):
    layer = GroupedQueryAttention(512, 8, hkv).to(device).eval()
    cache = build_cache(layer, batch=8, context_len=2048,
                        d_model=512, device=device)
    print(hkv, measure_one_token_decode_ms(layer, cache, 512), "ms")
```

### Protocol tối thiểu để kết quả có ý nghĩa

1. Giữ fixed: checkpoint/model quality, $H_Q$, `d_model`, layers, dtype, cache length, batch, GPU, sampling policy và concurrency.
2. Warm up; với CUDA phải `synchronize()` hoặc dùng CUDA events vì kernel launch bất đồng bộ.
3. Báo riêng `prefill`, fixed-context one-token `decode`, và end-to-end generation (`TTFT`, `TPOT`) nếu cần.
4. Đo cả raw KV bytes và peak/reserved GPU memory; không gọi chúng là cùng một quantity.
5. Xác nhận backend không materialize repeated K/V; nếu không, report đó là performance của implementation ấy, không phải intrinsic GQA.
6. Đo quality trên task/domain của bạn. Cache nhỏ không tự chứng minh quality giữ nguyên.

## 11. Cách đọc quality–bandwidth trade-off

| Nếu thay đổi | Thường nhận được | Thường đánh đổi |
|---|---|---|
| MHA → GQA (giảm $H_{KV}$ vừa phải) | ít cache bytes/read traffic, nhiều KV subspaces hơn MQA | ít K/V capacity hơn MHA |
| GQA → MQA ($H_{KV}=1$) | cache/bandwidth nhỏ nhất | sharing mạnh nhất, quality có thể giảm |
| tăng $H_{KV}$ | quality/capacity thường gần MHA hơn | cache, bandwidth và K/V projection cost tăng |

`H_{KV}` là một **architecture and training decision**, không phải knob serving thuần túy: changing it changes K/V projection parameter shapes. Nếu bạn đã có MHA checkpoint, GQA paper mô tả cách mean-pool K/V projections trong từng target group rồi `continue pretraining` (`uptraining`). Trong T5 experiments của nguồn, 5% original pretraining compute là một điểm hiệu quả được báo cáo; đó không phải guarantee cho decoder-only checkpoint hay mọi dataset.[^gqa-summary]

DeepSeek-V2 cũng báo cáo MHA dẫn GQA-8 và MQA trong matched 7B dense ablation trên các benchmark của họ. Điều này củng cố rằng reduced KV-head count là trade-off chất lượng–cache theo model/configuration, không phải kiến trúc nào luôn thắng.[^deepseek-v2-2024]

## 12. Những lỗi suy luận và implementation thường gặp

1. **“GQA giảm attention FLOPs $R$ lần.”** Không chính xác. Q heads vẫn là $H_Q$; điểm mạnh khi decode là giảm retained/read K/V state, không phải xóa mọi per-query attention work.
2. **“GQA/MQA luôn nhanh $R$ lần.”** Không đúng. Context length, batch, kernel, HBM bandwidth, `torch.cat`, sharding và other layers quyết định speedup thực tế.
3. **“`repeat_interleave` là GQA implementation tối ưu.”** Nó có thể đúng output nhưng physical copies có thể che lợi ích cache traffic.
4. **“So output GQA với MHA để test correctness.”** Hai kiến trúc có weights/shapes khác; hãy test cached-vs-full của cùng model. So MHA/GQA là evaluation quality, không phải unit test.
5. **“Cache có một tensor chung cho mọi layer.”** Sai. Mỗi Transformer layer có K/V cache riêng.
6. **“Đổi `num_kv_heads` lúc serving là đủ.”** Sai với standard weights: K/V projection shape đã thay đổi. Cần checkpoint được train cho layout đó, hoặc conversion + uptraining.
7. **“KV cache nhỏ hơn tức TTFT chắc chắn tốt hơn.”** Không chắc. TTFT gồm queueing, tokenization, prefill, scheduler/network; GQA tập trung nhất vào incremental decode.

## 13. Bài tập

1. Chạy `GroupedQueryAttention(96, 6, 6)`, `(96, 6, 2)`, `(96, 6, 1)` và in K/V cache shapes; giải thích vì sao output head dimension không đổi.
2. Vẽ `H_KV → raw KV MiB` với $H_Q$ fixed; xác nhận đường thẳng theo công thức.
3. Cố ý cache `k.repeat_interleave(group_size, dim=1)`; đo raw bytes và chỉ ra vì sao nó quay lại MHA-sized cache.
4. Mở rộng test để prefill chunk $P$ rồi decode từng token; assert cache length tăng đúng 1 sau mỗi call.
5. Với một model train được, thử nhiều `$H_{KV}$`; report task metric, `TPOT`, raw KV bytes, peak memory, hardware và kernel. Không kết luận Pareto frontier nếu thiếu quality evaluation.

## Relationships

- **Elaborates:** Stage 6 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng theory, implementation, verification, và measurement cho MQA/GQA.
- **Builds on:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) và [KV caching](kv-caching.md); MQA/GQA chỉ thay K/V-head sharing, không thay causal-attention objective.
- **Depends on:** [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) và [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md) cho cache semantics và measurement boundaries.
- **Extends:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) từ concept-level summary thành course thực hành cho người mới.
- **Related conversion:** [GQA checkpoint conversion and uptraining](gqa-checkpoint-conversion-and-uptraining.md) mô tả mean-pooling K/V và continued pretraining cho MHA checkpoint.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md), vốn nén token-addressable cache thành latent representation thay vì share full K/V heads.

## Evidence limits

Các result định lượng MQA/GQA trong bài này đến từ `MQA.md` và `GQA.md`, là summaries thứ cấp của các paper primary chưa được ingest độc lập trong wiki. Timing được báo cáo phụ thuộc đặc biệt vào TPU, model, sequence/workload và parallelization; không dùng chúng làm dự báo latency cho serving stack khác. Công thức tensor, code, test, và benchmark protocol ở đây là **pedagogical synthesis**; hãy benchmark trên checkpoint, context distribution, backend kernel, concurrency, và accelerator mục tiêu trước khi chọn $H_{KV}$.[^mqa-summary][^gqa-summary]

[^mqa-summary]: “MQA overview” (Vietnamese summary), [raw source](../raw/MQA.md), Sections 1–14. Secondary evidence summarizing Shazeer, “Fast Transformer Decoding: One Write-Head is All You Need” (2019); the primary paper has not been independently ingested here.
[^gqa-summary]: “GQA overview” (Vietnamese summary), [raw source](../raw/GQA.md), Sections 3–24. Secondary evidence summarizing Ainslie et al., “GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints” (2023); the primary paper has not been independently ingested here.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTex source](../raw/arXiv-1706.03762v7/ms.tex), attention definition and decoder masking.
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and Appendix C.
