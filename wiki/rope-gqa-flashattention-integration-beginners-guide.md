---
type: Synthesis
title: "Tích hợp RoPE, GQA, và FlashAttention vào GPT nhỏ"
description: A beginner-first integration lab that adds RoPE and GQA with per-layer KV caching to a small GPT, dispatches attention through PyTorch SDPA/FlashAttention when supported, verifies exact semantics, and benchmarks prefill separately from decode.
tags: [rope, grouped-query-attention, flashattention, kv-cache, prefill, decode, pytorch, gpt, learning-roadmap]
status: stable
created: 2026-08-11
generated:
  by: llm-wiki-agent/1
  at: 2026-08-11T00:00:00Z
sources:
  - id: rope-guide
    resource: rope-positional-encoding-beginners-guide.md
    title: "RoPE: positional encoding, implementation, và kiểm chứng cho người mới"
  - id: gqa-guide
    resource: mqa-gqa-kv-cache-decode-beginners-guide.md
    title: "MQA/GQA: giảm KV cache khi decode — bài học cho người mới"
  - id: flashattention-guide
    resource: flashattention-tiled-attention-beginners-guide.md
    title: "FlashAttention: tiled attention và online softmax cho người mới"
  - id: kv-cache-guide
    resource: kv-caching-beginners-guide.md
    title: "KV caching: cơ chế, implementation, và kiểm chứng"
  - id: inference-lifecycle-guide
    resource: llm-inference-lifecycle-training-prefill-decode-and-latency.md
    title: "LLM inference lifecycle: training, prefill, decode, and latency"
---

# Tích hợp RoPE, GQA, và FlashAttention vào GPT nhỏ

Đây là một integration lab cho Stage 6: thay learned absolute `position embedding` của một GPT nhỏ bằng `RoPE`, giảm số `KV heads` bằng `GQA`, và gọi `torch.nn.functional.scaled_dot_product_attention` (`SDPA`) để PyTorch có thể chọn một `FlashAttention` backend phù hợp. Ba thay đổi giải quyết ba việc khác nhau: RoPE đưa position vào `Q/K` scores; GQA giảm K/V cache giữ và đọc khi `decode`; FlashAttention giữ nguyên dense causal softmax attention nhưng giảm intermediate HBM IO, thường hữu ích nhất cho `prefill` dài. Chúng không được phép làm đổi causal-attention semantics, vì vậy lab xác minh output trước rồi mới benchmark.[^rope-guide][^gqa-guide][^flashattention-guide][^kv-cache-guide]

> [!success] Kết quả cần đạt
> Bạn có một `TinyGPT` chạy `RoPE + GQA + KV cache`, với cache shape `(B, H_KV, S, d_h)` ở **mỗi layer**. Bạn biết test nào chứng minh code giữ semantics, biết tại sao không so logits của MHA và GQA như một unit test, và biết đo riêng `prefill` với one-token `decode`.

## 1. Điều đã thay đổi — và điều không được thay đổi

Bắt đầu từ causal `Multi-Head Attention` (MHA), cho hidden states $X$:

$$
Q=XW_Q,
\quad K=XW_K,
\quad V=XW_V,
\quad O=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_h}}+M_{causal}\right)V.
$$

| Thành phần | Baseline GPT nhỏ | Sau integration | Ý nghĩa systems |
|---|---|---|---|
| Position | learned `position embedding` cộng vào input | RoPE xoay Q/K sau projection | score mang relative-position information |
| Heads | $H_Q=H_{KV}$ | $H_Q>H_{KV}$, với $H_Q\bmod H_{KV}=0$ | GQA: một KV head phục vụ một group query heads |
| Attention implementation | `scores → softmax → weights` materialized trong Python | `SDPA` semantic API | runtime *có thể* chọn fused FlashAttention kernel |
| Decode state | K/V per MHA head | K/V per KV head, per layer | raw cache bytes giảm theo $H_{KV}/H_Q$ |

Vẫn giữ nguyên các invariants sau:

1. `causal mask` vẫn cấm key ở future position. RoPE không thay mask.[^rope-guide]
2. Mỗi query head vẫn có Q riêng; chỉ K/V được shared trong group.[^gqa-guide]
3. RoPE xoay Q và K, không xoay V trong standard path.[^rope-guide]
4. `FlashAttention` (nếu backend được dispatch) tính **exact** allowed-token softmax attention, chỉ khác finite-precision/reduction order; nó không biến dense attention thành sparse hay linear attention.[^flashattention-guide]
5. Cached và uncached execution của **cùng architecture, cùng weights** phải cho logits gần bằng nhau trong tolerance phù hợp dtype/kernel.[^kv-cache-guide]

### Tại sao ba technique bổ sung nhau?

```text
input IDs
  └─ token embedding → hidden X
       ├─ Q heads: H_Q ── RoPE ─┐
       ├─ K heads: H_KV ─ RoPE ─┼─ SDPA / possible FlashAttention → output
       └─ V heads: H_KV ────────┘

per-layer decode cache: rotated K + unrotated V, shape (B, H_KV, S, d_h)
```

- `RoPE` là positional mechanism: nó quyết định Q/K vectors ở absolute positions được xoay thế nào.
- `GQA` là architectural capacity–cache trade-off: đổi `H_KV` thay đổi shape của K/V projection weights, nên không phải serving-only switch cho MHA checkpoint.[^gqa-guide]
- `FlashAttention` là exact-attention kernel strategy: nó không đổi số `KV heads` hay RoPE convention. Lợi ích thường rõ ở long-prompt prefill; one-token decode thường bị chi phối bởi việc đọc growing KV cache, nơi GQA có tác dụng trực tiếp hơn.[^flashattention-guide][^inference-lifecycle-guide]

## 2. Thiết kế lab và các điều kiện trước khi code

Code bên dưới dùng `interleaved pairs` cho RoPE: `(x0,x1), (x2,x3), ...`. Một checkpoint thật phải dùng đúng `rotary_dim`, frequency/base, scaling variant, pairing convention, normalization, tokenizer và weights của nó; không đổi convention chỉ vì tensor shapes vẫn hợp lệ.[^rope-guide]

Chọn một configuration nhỏ có thể chạy trên GPU:

```python
# All heads have d_h = d_model // num_query_heads = 32.
config = dict(
    vocab_size=512,
    d_model=128,
    num_layers=2,
    num_query_heads=4,  # H_Q
    num_kv_heads=2,     # H_KV; group_size = H_Q / H_KV = 2
    max_seq_len=512,
)
```

Điều kiện shape:

$$
d_{model}\bmod H_Q=0,
\qquad H_Q\bmod H_{KV}=0,
\qquad d_h=d_{model}/H_Q,
\qquad \texttt{rotary\_dim}\le d_h\text{ và even}.
$$

Với `num_query_heads=4`, `num_kv_heads=2`, mapping là `Q0,Q1 → KV0` và `Q2,Q3 → KV1`. Cache không bao giờ được lưu sau khi `repeat_interleave` thành 4 heads: retained K/V phải còn 2 heads để nhận đúng savings của GQA.[^gqa-guide]

> [!warning] `SDPA` không đồng nghĩa luôn chạy FlashAttention
> `F.scaled_dot_product_attention` là API diễn tả attention semantics. Backend thực tế phụ thuộc PyTorch version, CUDA/GPU, dtype, head dimension, mask, dropout và layout. Hãy profile/inspect diagnostics của runtime trên target environment; không suy ra kernel dispatch từ tên API.[^flashattention-guide]

## 3. Implementation: RoPE-GQA attention có KV cache

### 3.1 RoPE helpers

`cos/sin` được tạo từ **absolute** `position_ids`. Khi decode sau prefix length `P`, token mới dùng positions `P, P+1, ...`, không reset về zero. K cache giữ K đã xoay; không xoay lại cached K ở step sau.[^rope-guide][^kv-cache-guide]

```python
import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

KV = tuple[torch.Tensor, torch.Tensor]  # each: (B, H_KV, S, d_h)


def rotate_interleaved(x: torch.Tensor) -> torch.Tensor:
    """Adjacent pair rotation: (a, b) -> (-b, a)."""
    if x.size(-1) % 2:
        raise ValueError("rotary dimension must be even")
    pair = x.reshape(*x.shape[:-1], -1, 2)
    return torch.stack((-pair[..., 1], pair[..., 0]), dim=-1).flatten(-2)


def rope_cos_sin(position_ids: torch.Tensor, rotary_dim: int,
                 base: float = 10_000.0) -> tuple[torch.Tensor, torch.Tensor]:
    """Return cos/sin with shape (B, 1, T, rotary_dim)."""
    if rotary_dim <= 0 or rotary_dim % 2:
        raise ValueError("rotary_dim must be positive and even")
    # One angular frequency for each adjacent coordinate pair.
    indices = torch.arange(0, rotary_dim, 2, device=position_ids.device,
                           dtype=torch.float32)
    inv_freq = base ** (-indices / rotary_dim)
    angles = position_ids.float()[..., None] * inv_freq
    angles = torch.repeat_interleave(angles, 2, dim=-1)
    return angles.cos().unsqueeze(1), angles.sin().unsqueeze(1)


def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor,
               rotary_dim: int) -> torch.Tensor:
    """x: (B, heads, T, d_h); only the rotary prefix is transformed."""
    if rotary_dim > x.size(-1):
        raise ValueError("rotary_dim exceeds head_dim")
    x_rot, x_pass = x[..., :rotary_dim], x[..., rotary_dim:]
    x_rot = x_rot * cos + rotate_interleaved(x_rot) * sin
    return torch.cat((x_rot, x_pass), dim=-1)
```

### 3.2 Attention module

`enable_gqa=True` yêu cầu SDPA xử lý query/KV head mismatch. K/V cache vẫn được giữ ở layout compact `(B, H_KV, S, d_h)`; backend có thể có implementation-specific handling nội bộ, nhưng application code không được retain a repeated MHA-sized cache.

Với prefill không có cache, `is_causal=True` biểu đạt standard lower-triangular mask. Với ordinary one-token decode (`T_new=1`, `past_len>0`), new query được phép nhìn **tất cả** cached keys nên không cần mask. Với cached multi-token chunk, code tạo explicit offset mask; đừng dùng `is_causal=True` cho rectangular `(T_new, S)` rồi giả định nó tự biết `past_len`.[^kv-cache-guide]

```python
class RoPEGQASelfAttention(nn.Module):
    def __init__(self, d_model: int, num_query_heads: int,
                 num_kv_heads: int, rotary_dim: Optional[int] = None):
        super().__init__()
        if d_model % num_query_heads != 0:
            raise ValueError("d_model must divide num_query_heads")
        if num_query_heads % num_kv_heads != 0:
            raise ValueError("num_query_heads must divide num_kv_heads")

        self.hq = num_query_heads
        self.hkv = num_kv_heads
        self.head_dim = d_model // num_query_heads
        self.rotary_dim = self.head_dim if rotary_dim is None else rotary_dim
        if not 0 < self.rotary_dim <= self.head_dim or self.rotary_dim % 2:
            raise ValueError("rotary_dim must be even and within head_dim")

        self.q_proj = nn.Linear(d_model, self.hq * self.head_dim, bias=False)
        self.k_proj = nn.Linear(d_model, self.hkv * self.head_dim, bias=False)
        self.v_proj = nn.Linear(d_model, self.hkv * self.head_dim, bias=False)
        self.out_proj = nn.Linear(self.hq * self.head_dim, d_model, bias=False)

    @staticmethod
    def _split(x: torch.Tensor, heads: int, head_dim: int) -> torch.Tensor:
        # (B, T, heads*d_h) -> (B, heads, T, d_h)
        B, T, _ = x.shape
        return x.view(B, T, heads, head_dim).transpose(1, 2)

    def forward(self, x: torch.Tensor, past_kv: Optional[KV] = None,
                use_cache: bool = False) -> tuple[torch.Tensor, Optional[KV]]:
        B, T_new, _ = x.shape
        past_len = 0 if past_kv is None else past_kv[0].size(-2)
        positions = torch.arange(past_len, past_len + T_new, device=x.device)
        positions = positions.unsqueeze(0).expand(B, -1)

        q = self._split(self.q_proj(x), self.hq, self.head_dim)
        k_new = self._split(self.k_proj(x), self.hkv, self.head_dim)
        v_new = self._split(self.v_proj(x), self.hkv, self.head_dim)
        cos, sin = rope_cos_sin(positions, self.rotary_dim)
        q = apply_rope(q, cos, sin, self.rotary_dim)
        k_new = apply_rope(k_new, cos, sin, self.rotary_dim)

        if past_kv is None:
            k, v = k_new, v_new
        else:
            k_past, v_past = past_kv
            if k_past.shape[:2] != (B, self.hkv):
                raise ValueError("KV-cache batch size or head count mismatch")
            k = torch.cat((k_past, k_new), dim=-2)  # append sequence axis
            v = torch.cat((v_past, v_new), dim=-2)

        # Keep dropout behavior explicit: SDPA always applies supplied dropout_p.
        dropout_p = 0.0 if not self.training else 0.0
        if past_len == 0:
            # Prompt prefill: causal lower triangle over a square T_new x T_new matrix.
            y = F.scaled_dot_product_attention(
                q, k, v, dropout_p=dropout_p, is_causal=True, enable_gqa=True
            )
        elif T_new == 1:
            # Decode: the sole new query can attend every key in the cache.
            y = F.scaled_dot_product_attention(
                q, k, v, dropout_p=dropout_p, is_causal=False, enable_gqa=True
            )
        else:
            # Chunked decode: query i at absolute past_len+i sees keys <= it.
            S = k.size(-2)
            q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]
            k_pos = torch.arange(S, device=x.device)[None, :]
            allowed = k_pos <= q_pos  # SDPA bool mask: True means allowed.
            y = F.scaled_dot_product_attention(
                q, k, v, attn_mask=allowed, dropout_p=dropout_p,
                is_causal=False, enable_gqa=True,
            )

        y = y.transpose(1, 2).contiguous().view(B, T_new, -1)
        present = (k, v) if use_cache else None
        return self.out_proj(y), present
```

`dropout_p` được để `0.0` cho lab inference/correctness. Khi training, pass training dropout probability có chủ ý và compare test trong `eval()`; đừng để random dropout bị hiểu nhầm là cache/kernel bug.

### 3.3 Một GPT nhỏ hoàn chỉnh

`TinyGPT` dưới đây đủ để integration test. Nó dùng RoPE thay vì `position_emb`; mỗi `Block` trả cache riêng. Đây là implementation học tập, không phải production server: `torch.cat` reallocates/copies cache lớn dần, còn server thực tế dùng paged/preallocated blocks.[^kv-cache-guide]

```python
class Block(nn.Module):
    def __init__(self, d_model: int, num_query_heads: int, num_kv_heads: int):
        super().__init__()
        self.ln_1 = nn.LayerNorm(d_model)
        self.attn = RoPEGQASelfAttention(d_model, num_query_heads, num_kv_heads)
        self.ln_2 = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(),
            nn.Linear(4 * d_model, d_model),
        )

    def forward(self, x, past_kv=None, use_cache=False):
        a, present = self.attn(self.ln_1(x), past_kv, use_cache)
        x = x + a
        return x + self.mlp(self.ln_2(x)), present


class TinyRoPEGQAGPT(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, num_layers: int,
                 num_query_heads: int, num_kv_heads: int, max_seq_len: int):
        super().__init__()
        self.max_seq_len = max_seq_len
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.blocks = nn.ModuleList([
            Block(d_model, num_query_heads, num_kv_heads)
            for _ in range(num_layers)
        ])
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids, past_key_values=None, use_cache=False):
        B, T_new = input_ids.shape
        if T_new == 0:
            raise ValueError("input_ids cannot be empty")
        if past_key_values is None:
            past_len = 0
        else:
            if len(past_key_values) != len(self.blocks):
                raise ValueError("one KV pair is required per Transformer layer")
            past_len = past_key_values[0][0].size(-2)
        if past_len + T_new > self.max_seq_len:
            raise ValueError("sequence exceeds max_seq_len")

        x = self.token_emb(input_ids)  # RoPE, not a position embedding, supplies position.
        present_key_values = []
        for i, block in enumerate(self.blocks):
            layer_past = None if past_key_values is None else past_key_values[i]
            x, present = block(x, layer_past, use_cache)
            if use_cache:
                present_key_values.append(present)
        logits = self.lm_head(self.ln_f(x))
        return logits, tuple(present_key_values) if use_cache else None


# Example construction. This model has random weights until trained.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(0)
model = TinyRoPEGQAGPT(**config).to(device).eval()
```

> [!note] Không load MHA checkpoint vào model này như một weight-compatible replacement.
> `k_proj` và `v_proj` có fewer output features khi `H_KV < H_Q`; MHA and GQA have different parameter shapes. Conversion requires a documented grouping/averaging procedure followed by continued pretraining or evaluation, not a semantic unit test.[^gqa-guide]

## 4. Xác minh output semantics trước khi benchmark

### 4.1 Test A — `SDPA GQA` khớp dense reference nhỏ

Đây là test semantics của fused path. Reference tạm thời repeats K/V để đưa về MHA-shaped tensors; điều đó chấp nhận được **chỉ trong test**, không được dùng để retain production cache. Cả reference và SDPA đều dùng Q/K đã RoPE để test integration boundary đó.

```python
@torch.inference_mode()
def test_sdpa_gqa_matches_dense_reference():
    torch.manual_seed(1)
    B, H_Q, H_KV, T, d_h = 2, 4, 2, 7, 8
    group_size = H_Q // H_KV
    q = torch.randn(B, H_Q, T, d_h, device=device)
    k = torch.randn(B, H_KV, T, d_h, device=device)
    v = torch.randn(B, H_KV, T, d_h, device=device)
    pos = torch.arange(T, device=device)[None].expand(B, -1)
    cos, sin = rope_cos_sin(pos, rotary_dim=d_h)
    q, k = apply_rope(q, cos, sin, d_h), apply_rope(k, cos, sin, d_h)

    # Production semantic path: compact grouped K/V inputs.
    got = F.scaled_dot_product_attention(q, k, v, is_causal=True,
                                         dropout_p=0.0, enable_gqa=True)

    # Slow dense reference; materialized expansion exists only during this test.
    k_full = k.repeat_interleave(group_size, dim=1)
    v_full = v.repeat_interleave(group_size, dim=1)
    scores = q @ k_full.transpose(-2, -1) / math.sqrt(d_h)
    causal = torch.ones(T, T, dtype=torch.bool, device=device).tril()
    scores = scores.masked_fill(~causal, -torch.inf)
    expected = torch.softmax(scores, dim=-1) @ v_full
    torch.testing.assert_close(got, expected, rtol=1e-4, atol=1e-5)


test_sdpa_gqa_matches_dense_reference()
```

Nếu test fail in FP32 trên cùng device, kiểm tra trước: group mapping/order, scale $1/\sqrt{d_h}$, causal-mask orientation, RoPE pairing convention, `rotary_dim`, and whether the installed PyTorch supports `enable_gqa`. Với BF16/FP16, first reproduce in FP32 rồi mới chọn tolerance based on measured numerical variation.[^rope-guide][^flashattention-guide]

### 4.2 Test B — future tokens không làm đổi past logits

Causal correctness không được suy ra từ việc output “trông hợp lý”. Thay token IDs sau `cut`, chạy full no-cache model, rồi assert logits đến `cut` không đổi. Test này bắt lỗi mask orientation hoặc accidental non-causal branch.

```python
@torch.inference_mode()
def assert_no_future_leakage(model, ids, cut, rtol=1e-4, atol=1e-5):
    model.eval()
    baseline, _ = model(ids, use_cache=False)
    changed = ids.clone()
    changed[:, cut + 1:] = torch.randint(
        0, model.token_emb.num_embeddings, changed[:, cut + 1:].shape,
        device=ids.device,
    )
    changed_logits, _ = model(changed, use_cache=False)
    torch.testing.assert_close(baseline[:, :cut + 1], changed_logits[:, :cut + 1],
                               rtol=rtol, atol=atol)


ids = torch.randint(0, config["vocab_size"], (2, 13), device=device)
assert_no_future_leakage(model, ids, cut=6)
```

### 4.3 Test C — cached full-model logits khớp full prefill

Đây là test integration quan trọng nhất. Nó simultaneously kiểm tra per-layer cache mapping, append dimension, RoPE position offset, and mask offset. Dùng `teacher-forced` continuation thay vì sampling để hai paths nhận đúng cùng tokens.

```python
@torch.inference_mode()
def assert_cached_logits_match(model, prompt_ids, continuation_ids,
                               rtol=1e-4, atol=1e-5):
    model.eval()
    full_ids = prompt_ids.clone()

    cached_logits, cache = model(prompt_ids, use_cache=True)  # prefill
    full_logits, _ = model(full_ids, use_cache=False)
    torch.testing.assert_close(cached_logits[:, -1], full_logits[:, -1],
                               rtol=rtol, atol=atol)

    expected_len = prompt_ids.size(1)
    for token in continuation_ids.split(1, dim=1):
        full_ids = torch.cat((full_ids, token), dim=1)
        cached_logits, cache = model(token, cache, use_cache=True)  # decode
        full_logits, _ = model(full_ids, use_cache=False)
        torch.testing.assert_close(cached_logits[:, -1], full_logits[:, -1],
                                   rtol=rtol, atol=atol)
        expected_len += 1
        assert all(k.size(-2) == expected_len and v.size(-2) == expected_len
                   for k, v in cache)
        assert all(k.size(1) == config["num_kv_heads"] for k, _ in cache)
    return cache


prompt = torch.randint(0, config["vocab_size"], (2, 11), device=device)
continuation = torch.randint(0, config["vocab_size"], (2, 9), device=device)
cache = assert_cached_logits_match(model, prompt, continuation)
print("RoPE + GQA cached logits match full logits")
```

Không so MHA logits với GQA logits để gọi difference là bug: K/V projections and learned weights differ. So sánh MHA/GQA là một quality experiment chỉ có ý nghĩa khi training/uptraining and evaluation protocol được kiểm soát.[^gqa-guide]

## 5. Benchmark: tách `prefill` và one-token `decode`

Chỉ chạy benchmark khi Tests A–C pass. `prefill` nhận prompt dài và xây cache. `decode` benchmark ở đây dùng một cache length cố định, gửi một token mới nhiều lần từ **cùng initial cache**; như vậy mỗi timed call có cùng shape và không trộn đường cong context growth vào latency. Đây là layer/model microbenchmark, không phải `TTFT`, `TPOT`, throughput hay end-to-end server benchmark.[^inference-lifecycle-guide]

```python
import time


def kv_cache_bytes(cache) -> int:
    return sum(k.numel() * k.element_size() + v.numel() * v.element_size()
               for k, v in cache)


@torch.inference_mode()
def median_cuda_ms(fn, warmup=20, repeats=100) -> float:
    """CUDA-event timing; use a CPU timer only when CUDA is unavailable."""
    for _ in range(warmup):
        fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        samples = []
        for _ in range(repeats):
            start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            start.record()
            fn()
            end.record()
            torch.cuda.synchronize()
            samples.append(start.elapsed_time(end))
        return float(torch.tensor(samples).median())

    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(1e3 * (time.perf_counter() - start))
    return float(torch.tensor(samples).median())


@torch.inference_mode()
def benchmark(model, vocab_size, context_len, batch_size=1):
    model.eval()
    prompt = torch.randint(0, vocab_size, (batch_size, context_len), device=device)
    new_token = torch.randint(0, vocab_size, (batch_size, 1), device=device)

    # Build a correct fixed-length cache outside the decode timing loop.
    _, cache = model(prompt, use_cache=True)
    prefill_ms = median_cuda_ms(lambda: model(prompt, use_cache=True))
    decode_ms = median_cuda_ms(lambda: model(new_token, cache, use_cache=True))
    return {
        "context": context_len,
        "prefill_ms": prefill_ms,
        "decode_ms": decode_ms,
        "raw_kv_mib": kv_cache_bytes(cache) / 2**20,
        "cache_shape_layer0": tuple(cache[0][0].shape),
    }


# Keep all reported controls fixed: weights/config except H_KV, dtype,
# device, context length, batch, PyTorch/CUDA version, and timing protocol.
for length in (32, 128, 256, 512):
    print(benchmark(model, config["vocab_size"], context_len=length))
```

### Cách đọc bảng kết quả

| Đo được | Kỳ vọng có điều kiện | Không được kết luận |
|---|---|---|
| `raw_kv_mib` | tăng tuyến tính theo context; với same $H_Q,d_h,L$, GQA/MHA ratio là $H_{KV}/H_Q$ | peak GPU memory đúng bằng raw cache bytes |
| `prefill_ms` | thường tăng theo prompt length; an efficient attention kernel có thể giúp | API SDPA chắc chắn dispatched FlashAttention |
| `decode_ms` | thường chịu ảnh hưởng cache reads; GQA có thể giúp hơn khi context dài | speedup đúng bằng group size |
| cached/full logits | gần bằng trong numerical tolerance | MHA và GQA có cùng quality |

Raw K/V storage for $L$ layers is:

$$
M_{KV}=2LBSH_{KV}d_hp\ \text{bytes},
$$

where $p$ is bytes per element. For the example, GQA has $H_Q=4,H_{KV}=2$, therefore half MHA's raw cache tensor storage under the same other variables. GPU peak/reserved memory additionally contains weights, temporary tensors, allocator behavior, and the toy implementation's repeated `torch.cat` allocations.[^gqa-guide][^kv-cache-guide]

To compare MHA (`H_KV=H_Q`) versus GQA fairly at the systems level, instantiate models with same `d_model`, $H_Q$, layers, dtype, batch, context and device; run every model's own semantics tests first. To compare quality, train/uptrain controlled checkpoints and report task metrics as well—randomly initialized alternatives only measure tensor shapes and kernel behavior.[^gqa-guide]

## 6. Debug checklist

| Symptom | Most likely cause | First check |
|---|---|---|
| Test A fails | wrong GQA mapping, mask, scale, or unsupported `enable_gqa` path | run FP32; inspect SDPA API/version and dense reference |
| position 0 changes a vector | incorrect sin/cos/cache broadcasting | RoPE identity test in [RoPE guide](rope-positional-encoding-beginners-guide.md) |
| Test C fails at first decode token | new RoPE position reset to 0, or K/V appended on wrong axis | `past_len + arange(T_new)` and `dim=-2` |
| Test C fails only for chunks | rectangular causal mask ignores cache offset | use explicit `k_pos <= past_len + q_pos` mask |
| cache has `H_Q` heads under GQA | repeated K/V was retained | retain `(B,H_KV,S,d_h)`, not an expanded tensor |
| prefill improves but decode does not | expected possible bottleneck split | confirm query/cache shapes and benchmark longer context |
| result changes between test runs | dropout or nondeterminism | `eval()`, `dropout_p=0`, compare tolerance not bitwise equality |

## 7. Giới hạn và bước tiếp theo

- This lab's `torch.cat` cache is intentionally simple, but it copies growing tensors. Do not infer production serving performance from it; real servers manage KV blocks and batching differently.[^kv-cache-guide]
- An SDPA call may fall back to a non-Flash backend. Report actual hardware, PyTorch/CUDA version, dtype, sequence shapes, and backend evidence if claiming FlashAttention performance.[^flashattention-guide]
- FlashAttention preserves full dense-attention semantics but not its quadratic interaction count; very long context can require a different architectural trade-off.[^flashattention-guide]
- GQA cache reduction can trade representational capacity/quality. `num_kv_heads` is chosen during architecture/training or through conversion plus uptraining, not tuned freely at serving time.[^gqa-guide]

After this lab, replace the toy benchmark with a trained checkpoint and a serving workload that separately reports `TTFT`, `TPOT`, throughput, cache capacity, and task quality. The lifecycle and metric boundaries are explained in [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md).

## Relationships

- **Elaborates:** Stage 6 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) with one integrated, executable exercise.
- **Integrates:** [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md), [MQA/GQA: giảm KV cache khi decode — bài học cho người mới](mqa-gqa-kv-cache-decode-beginners-guide.md), and [FlashAttention: tiled attention và online softmax cho người mới](flashattention-tiled-attention-beginners-guide.md).
- **Depends on:** [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) for per-layer cache and cached-versus-full semantics.
- **Uses:** [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md) to separate measurement phases.

## Evidence limits

This is a pedagogical synthesis over the linked wiki guides. The supplied sources establish the mechanisms and their conditional trade-offs, but they do not establish a universal PyTorch kernel dispatch or a portable speedup. The exact code path, numerical tolerance, and measured prefill/decode result must be verified on the target PyTorch version, GPU, dtype, model shape, and serving workload.[^rope-guide][^gqa-guide][^flashattention-guide][^kv-cache-guide]

[^rope-guide]: [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md), especially RoPE placement, interleaved convention, and absolute decode positions; it in turn cites `raw/RoPE.md`.
[^gqa-guide]: [MQA/GQA: giảm KV cache khi decode — bài học cho người mới](mqa-gqa-kv-cache-decode-beginners-guide.md), especially grouped head layout, KV-cache accounting, and cache semantics; it in turn cites `raw/MQA.md` and `raw/GQA.md`.
[^flashattention-guide]: [FlashAttention: tiled attention và online softmax cho người mới](flashattention-tiled-attention-beginners-guide.md), especially exact-attention semantics, SDPA dispatch caveat, and prefill/decode boundary; it in turn cites `raw/FlashAttention.md`.
[^kv-cache-guide]: [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md), especially per-layer caches, position offsets, and cached-versus-uncached logits; it in turn cites `raw/KVCachinginLLMsClearlyExplained.md`.
[^inference-lifecycle-guide]: [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md), especially metric boundaries and phase-specific bottlenecks.
