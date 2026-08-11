---
type: Synthesis
title: "KV caching: cơ chế, implementation, và kiểm chứng"
description: A beginner-first course on per-layer KV cache mechanics, exact cached-versus-uncached verification, and latency and memory measurement in a small PyTorch GPT.
tags: [kv-cache, inference, decoding, prefill, pytorch, gpt, learning-roadmap]
status: stable
created: 2026-08-11
generated: { by: llm-wiki-agent/1, at: 2026-08-11T00:00:00+07:00 }
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: kv-caching-explained
    resource: ../raw/KVCachinginLLMsClearlyExplained.md
    title: "KV Caching in LLMs, Clearly Explained"
---

# KV caching: cơ chế, implementation, và kiểm chứng

`KV cache` là state dành riêng cho một generation request: ở mỗi Transformer layer, nó giữ `Key` (K) và `Value` (V) đã tính cho các token trong context. Khi decode một token mới, model chỉ tính Q/K/V cho token mới, append K/V mới vào cache, rồi cho query mới attention tới K/V của toàn bộ history. Nhờ đó model không tính lại K/V của prefix ở mỗi generation step; đổi lại, cache tăng tuyến tính theo số token, số layer, số KV heads và số request đồng thời.[^kv-caching-explained]

```text
prompt ── prefill ──► K/V(prompt) in every layer ──► logits ──► y1
                                                        │
             y1 ── decode with cache ──► append K/V(y1) ┘ ──► logits ──► y2
```

> [!success] Mục tiêu
> Sau bài này, bạn có thể (1) giải thích chính xác vì sao chỉ cache K/V, (2) thêm `past_key_values` vào GPT nhỏ, (3) kiểm tra logits/output của cached và uncached generation tương đương, và (4) đo latency cùng cache memory theo `context length` mà không nhầm `prefill` với `decode`.

Bài này là **pedagogical synthesis**. Code là một minimal PyTorch implementation để học và test semantics, không phải inference engine production. Bài giả định bạn đã biết `causal self-attention`, shape `(B, H, T, d_h)`, và next-token generation từ [Attention: beginner's guide for causal language models](attention-beginner-guide.md), [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), và [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md).

## 1. Bài toán: generation lặp lại cùng một work

Gọi prompt là $x_{1:P}$ và output lần lượt là $y_1,y_2,\ldots$. Một causal LM trước hết chạy:

$$
\operatorname{logits},\;\text{cache}_{x_{1:P}}
= f(x_{1:P}),
\qquad y_1\sim\operatorname{sample}(\operatorname{logits}_{P}).
$$

Để chọn $y_2$, token $y_1$ phải đi qua model. Nếu không dùng cache, cách đơn giản là gọi lại toàn model trên sequence dài hơn:

```text
f(x1 ... xP)             → distribution for y1
f(x1 ... xP y1)          → distribution for y2
f(x1 ... xP y1 y2)       → distribution for y3
...
```

Trong mỗi call mới, K/V của `x1 ... xP` và các output token cũ lại được tính lại, dù weights và input prefix không đổi. Với causal model ở `eval()` mode, K/V của một token cũ trong **cùng layer** cũng không thể thay đổi khi ta append token bên phải: causal mask không cho token cũ đọc future token.[^vaswani-transformer-2017]

### `KV cache` thay đường đi dữ liệu thế nào?

```text
prefill: f(x1 ... xP, cache=None)
         → cache contains K/V for x1 ... xP
         → distribution for y1

decode:  f(y1, cache for x1 ... xP)
         → append K/V(y1)
         → distribution for y2

decode:  f(y2, cache for x1 ... xP y1)
         → append K/V(y2)
         → distribution for y3
```

Đây vẫn là **cùng model và cùng causal-attention function**. Khác biệt chỉ là implementation nhận K/V history từ memory thay vì recompute chúng.

> [!note] Alignment quan trọng
> `prefill(prompt)` cho logits để sample `y1`. K/V của `y1` **chưa** có trong cache ở thời điểm vừa sample. Chúng chỉ được tạo ở decode forward pass nhận `y1`; pass này cho logits để sample `y2`. Nhầm alignment này là nguyên nhân phổ biến của cache bị lệch một token.

## 2. Vì sao cache `K` và `V`, không cache `Q`?

Trong một attention head, với hidden state $h_t$ tại layer đang xét:

$$
q_t=h_tW^Q,\qquad k_t=h_tW^K,\qquad v_t=h_tW^V,
$$
$$
o_t=\operatorname{softmax}\left(\frac{q_tK_{1:t}^{\top}}{\sqrt{d_h}}\right)V_{1:t}.
$$

Khi decode position $t$, chỉ cần output của **query mới** $q_t$. Query cũ $q_j$ đã phục vụ việc tính output tại position $j$ trong một forward pass trước; nó không xuất hiện trong công thức của $o_t$. Ngược lại, `K` và `V` của mọi $j\le t$ vẫn cần thiết để query mới chấm điểm và trộn content.

| Tensor của token cũ | Có cần khi tính output cho token mới? | Lý do |
|---|---|---|
| `Q` | Không | query cũ không được dùng lại cho query mới |
| `K` | Có | query mới phải so khớp với mọi key trong history |
| `V` | Có | attention weights mới phải trộn các value trong history |
| hidden state tổng quát | Không theo standard KV cache | K/V layer đó là sufficient state cho attention step; các layer tiếp theo xử lý token mới tuần tự |

Cache không phải một tensor dùng chung cho cả model. Với $L$ layers, mỗi layer có K/V riêng vì projections và representations ở từng depth khác nhau:

```text
past_key_values = (
    (K_layer_0, V_layer_0),
    (K_layer_1, V_layer_1),
    ...,
    (K_layer_L-1, V_layer_L-1),
)
```

Với standard multi-head attention, mỗi K hoặc V thường có shape `(B, H_kv, S, d_h)`, trong đó $S$ là current cache length. Query có thể có $H_q=H_{kv}$ heads (MHA) hoặc nhiều hơn (GQA/MQA).

## 3. `prefill` và `decode` có cost khác nhau

- **`prefill`** nhận cả prompt dài $P$ tokens. Nó tính K/V cho mọi prompt token và có thể xử lý các positions theo sequence song song với causal mask.
- **`decode`** thường nhận một token mới (`T_new=1`) cho mỗi active request. Nó chỉ viết K/V mới, nhưng query mới vẫn phải đọc cache dài $S$.

Vì vậy, cache không biến decode thành $O(1)$ theo context length. Nó loại bỏ recomputation của projections/hidden states cũ, còn attention của query mới vẫn có số score và cache reads tăng theo $S$.[^kv-caching-explained]

Một cách tách bạch hữu ích là:

| Phần work | Uncached (mỗi step chạy full prefix) | Cached decode |
|---|---|---|
| K/V projections cho tokens cũ | bị lặp lại | tính một lần rồi đọc cache |
| attention score cho query mới với history | có | vẫn có |
| full score matrix cho mọi query cũ | bị tính lại | không tính lại |
| memory state giữa steps | không đáng kể | K/V tăng theo context |

Đừng dùng một Big-O duy nhất cho mọi trường hợp. Nếu generate $G$ tokens từ scratch bằng cách full-forward prefix dài dần, việc materialize full attention ở mỗi call có tổng $\sum_{t=1}^{G}t^2=O(G^3)$ score work. Cache cho một prefill rồi one-token decode có $O(G^2)$ tổng query–history score work. Với prompt cố định, con số thực tế còn phụ thuộc $P$, $G$, batch, kernel, và dimensions. Điểm cốt lõi vẫn là: cache không xóa việc đọc history, nhưng xóa việc làm lại prefix work.

Xem [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md) để phân biệt `TTFT`, `prefill latency`, và `TPOT`.

## 4. Memory model trước khi đo

Đặt:

- $L$: số Transformer layers;
- $B$: số sequences cùng nằm trong batch/cache;
- $S$: số cached tokens;
- $H_{KV}$: số KV heads;
- $d_h$: head dimension;
- $p$: số bytes mỗi element (`2` với FP16/BF16, `4` với FP32).

Cache K/V thuần có dung lượng xấp xỉ:

$$
M_{KV}=2\,L\,B\,S\,H_{KV}\,d_h\,p \quad \text{bytes}.
$$

Hệ số $2$ là một K và một V. Do đó, giữ mọi thứ khác cố định thì doubling `context length` hoặc batch size sẽ doubling cache memory. Đây là lower-level tensor accounting; production GPU memory còn có model weights, temporary buffers, allocator fragmentation và state của các request khác.[^kv-caching-explained]

> [!example] GPT nhỏ
> `L=4`, `B=1`, `S=1024`, `H_kv=6`, `d_h=32`, BF16/FP16 (`p=2`) cần
> $2\times4\times1\times1024\times6\times32\times2=3{,}145{,}728$ bytes, xấp xỉ 3 MiB cho raw K/V tensors. Đây là nhỏ vì model nhỏ; quy luật tuyến tính vẫn giống model lớn.

`GQA`/`MQA` giảm $H_{KV}$, nên giảm trực tiếp cả cache bytes lẫn lượng K/V cần đọc ở decode. `KV-cache compression` giảm element width hoặc số entries; `PagedAttention` thay đổi cách allocate/share blocks. Các mechanism này giải quyết những phần khác nhau của vấn đề, xem [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md), và [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md).

## 5. Minimal implementation: thêm cache vào causal attention

Đoạn code dưới đây là minimal GPT độc lập, dùng learned absolute `position embedding` và MHA. Nó cố ý không dùng fused kernel, padding mask, GQA, quantization hay continuous batching để mechanics dễ nhìn. `use_cache=False` là baseline uncached; `use_cache=True` trả `past_key_values` mới.

```python
import math
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

KV = Tuple[torch.Tensor, torch.Tensor]  # each: (B, H, S, d_h)


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

    def _split_heads(self, x: torch.Tensor) -> torch.Tensor:
        # (B, T, D) -> (B, H, T, d_h)
        B, T, _ = x.shape
        return x.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,
        past_kv: Optional[KV] = None,
        use_cache: bool = False,
    ) -> tuple[torch.Tensor, Optional[KV]]:
        B, T_new, D = x.shape
        q = self._split_heads(self.q_proj(x))
        k_new = self._split_heads(self.k_proj(x))
        v_new = self._split_heads(self.v_proj(x))

        if past_kv is None:
            k, v = k_new, v_new
            past_len = 0
        else:
            k_past, v_past = past_kv
            if k_past.shape[:2] != (B, self.n_heads):
                raise ValueError("cache batch size or head count does not match")
            # Append only the K/V for newly supplied tokens.
            k = torch.cat((k_past, k_new), dim=-2)
            v = torch.cat((v_past, v_new), dim=-2)
            past_len = k_past.size(-2)

        # q: (B, H, T_new, d_h); k: (B, H, S, d_h)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # A new query at local i has absolute position past_len + i.
        # It may read keys at positions <= that position.
        S = k.size(-2)
        q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]
        k_pos = torch.arange(S, device=x.device)[None, :]
        causal = k_pos <= q_pos                     # (T_new, S)
        scores = scores.masked_fill(~causal, float("-inf"))

        weights = F.softmax(scores, dim=-1)
        y = weights @ v                              # (B, H, T_new, d_h)
        y = y.transpose(1, 2).contiguous().view(B, T_new, D)
        present_kv = (k, v) if use_cache else None
        return self.out_proj(y), present_kv


class Block(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.ln_1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_heads)
        self.ln_2 = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(),
            nn.Linear(4 * d_model, d_model),
        )

    def forward(self, x, past_kv=None, use_cache=False):
        a, present_kv = self.attn(self.ln_1(x), past_kv, use_cache)
        x = x + a
        x = x + self.mlp(self.ln_2(x))
        return x, present_kv


class TinyGPTWithCache(nn.Module):
    def __init__(self, vocab_size, max_seq_len, d_model=192, n_heads=6,
                 n_layers=4):
        super().__init__()
        self.max_seq_len = max_seq_len
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.position_emb = nn.Embedding(max_seq_len, d_model)
        self.blocks = nn.ModuleList(
            [Block(d_model, n_heads) for _ in range(n_layers)]
        )
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids, past_key_values=None, use_cache=False):
        B, T_new = input_ids.shape
        if T_new == 0:
            raise ValueError("input must contain at least one token")
        if past_key_values is not None:
            if len(past_key_values) != len(self.blocks):
                raise ValueError("one KV pair is required per layer")
            past_len = past_key_values[0][0].size(-2)
        else:
            past_len = 0
        if past_len + T_new > self.max_seq_len:
            raise ValueError("sequence exceeds max_seq_len")

        # Critical for learned absolute positions: incremental tokens need
        # positions P, P+1, ... rather than starting again from zero.
        position_ids = torch.arange(
            past_len, past_len + T_new, device=input_ids.device
        )
        x = self.token_emb(input_ids) + self.position_emb(position_ids)[None]

        present_key_values = []
        for layer_idx, block in enumerate(self.blocks):
            layer_past = None if past_key_values is None else past_key_values[layer_idx]
            x, present_kv = block(x, layer_past, use_cache)
            if use_cache:
                present_key_values.append(present_kv)

        logits = self.lm_head(self.ln_f(x))
        return logits, tuple(present_key_values) if use_cache else None
```

### Đọc code theo một `prefill` và một `decode` step

Với `prompt_ids.shape == (B, P)`:

```python
model.eval()
with torch.inference_mode():
    logits, cache = model(prompt_ids, use_cache=True)  # prefill
    y1 = logits[:, -1].argmax(dim=-1, keepdim=True)    # (B, 1)

    logits, cache = model(y1, cache, use_cache=True)   # decode y1
    y2 = logits[:, -1].argmax(dim=-1, keepdim=True)
```

Sau prefill, cache ở mỗi layer có `(B, H, P, d_h)`. Sau decode `y1`, nó có `(B, H, P + 1, d_h)`.

Ba chi tiết correctness không được bỏ qua:

1. **Cache phải ở từng layer.** Dùng K/V layer 0 cho layer 1 là sai về representation và shapes có thể vẫn tình cờ hợp lệ.
2. **Append ở sequence dimension.** Với layout trên là `dim=-2`, không phải head dimension (`-3`) hay feature dimension (`-1`).
3. **Position phải tiếp tục.** Learned absolute `position embedding` cần offset `past_len`. Với RoPE, code cũng phải áp dụng vị trí tuyệt đối/offset tương ứng cho Q/K mới; reset position về 0 sẽ làm cached và full forward khác nhau.

> [!warning] Đừng cache khi model đang stochastic
> Test equivalence với `model.eval()`, `torch.inference_mode()`/`no_grad()`, cùng dtype/device. `dropout` trong training mode làm hai forward passes khác nhau ngay cả khi cache đúng. Các sampling policy không deterministic cũng không phù hợp để so *logits*.

## 6. Kiểm chứng 1: cached logits phải khớp uncached logits

Đây là test quan trọng nhất. Thay vì so token text cuối cùng (dễ bị che bởi `argmax`), hãy so full logits ở từng step. Để kiểm tra nhiều step mà vẫn deterministic, đoạn test dưới đây dùng `teacher-forced` continuation: đưa token thật tiếp theo vào cả cached path lẫn full-prefix baseline.

```python
@torch.inference_mode()
def assert_cached_logits_match(model, prompt_ids, continuation_ids,
                               rtol=1e-4, atol=1e-5):
    """
    prompt_ids:       (B, P)
    continuation_ids: (B, G), supplied token-by-token for verification.

    At each point, compare logits predicting the following token.  It tests
    cache semantics, not sampling behavior.
    """
    model.eval()
    full_ids = prompt_ids.clone()

    # Prefill cache, then compare to a conventional complete forward pass.
    cached_logits, cache = model(prompt_ids, use_cache=True)
    full_logits, _ = model(full_ids, use_cache=False)
    torch.testing.assert_close(
        cached_logits[:, -1], full_logits[:, -1], rtol=rtol, atol=atol
    )

    # Feed one known token at a time. Both paths must predict identically.
    for token in continuation_ids.split(1, dim=1):
        full_ids = torch.cat((full_ids, token), dim=1)
        cached_logits, cache = model(token, cache, use_cache=True)
        full_logits, _ = model(full_ids, use_cache=False)
        torch.testing.assert_close(
            cached_logits[:, -1], full_logits[:, -1], rtol=rtol, atol=atol
        )

    return cache


device = "cuda" if torch.cuda.is_available() else "cpu"
torch.manual_seed(0)
model = TinyGPTWithCache(
    vocab_size=257, max_seq_len=128, d_model=96, n_heads=4, n_layers=3
).to(device)
prompt = torch.randint(0, 257, (2, 11), device=device)
continuation = torch.randint(0, 257, (2, 17), device=device)
cache = assert_cached_logits_match(model, prompt, continuation)
print("cached and uncached logits match")
```

`torch.testing.assert_close` có thể cần tolerance hơi lớn hơn với BF16/FP16 hoặc kernel khác nhau. Nếu FP32 trên cùng device vẫn sai đáng kể, đừng nới tolerance trước: xem checklist debug ở phần 9.

### Kiểm chứng output với greedy generation

Khi logits đã khớp, greedy output cũng phải khớp. Hàm dưới đây chạy hai đường khác nhau trên **cùng checkpoint**:

```python
@torch.inference_mode()
def generate_uncached(model, prompt_ids, max_new_tokens):
    ids = prompt_ids.clone()
    for _ in range(max_new_tokens):
        logits, _ = model(ids, use_cache=False)
        next_id = logits[:, -1].argmax(dim=-1, keepdim=True)
        ids = torch.cat((ids, next_id), dim=1)
    return ids


@torch.inference_mode()
def generate_cached(model, prompt_ids, max_new_tokens):
    ids = prompt_ids.clone()
    logits, cache = model(ids, use_cache=True)          # prefill
    for _ in range(max_new_tokens):
        next_id = logits[:, -1].argmax(dim=-1, keepdim=True)
        ids = torch.cat((ids, next_id), dim=1)
        # This pass puts next_id in cache and computes logits for the next loop.
        logits, cache = model(next_id, cache, use_cache=True)
    return ids

model.eval()
a = generate_uncached(model, prompt, max_new_tokens=20)
b = generate_cached(model, prompt, max_new_tokens=20)
torch.testing.assert_close(a, b)
print("greedy output match")
```

Code cached chạy một final forward pass không cần thiết sau output cuối để giữ loop đơn giản. Production loop có thể tránh pass này khi gặp `EOS` hoặc đạt `max_new_tokens`.

## 7. Kiểm chứng 2: đo latency và memory theo `context length`

Chỉ benchmark sau khi test logits pass. Một implementation nhanh nhưng tạo logits khác baseline là semantic regression, không phải optimization.

### 7.1 Cách đo có ý nghĩa

- Benchmark trong `model.eval()` và `torch.inference_mode()`.
- Warm up trước khi timing vì CUDA lazy initialization/JIT/allocation có thể làm run đầu chậm bất thường.
- Với CUDA, gọi `torch.cuda.synchronize()` trước và sau thời gian đo; nếu không, CPU timer chỉ đo thời điểm launch asynchronous kernels.
- Giữ model, dtype, batch size, number of generated tokens, sampling policy, GPU và clock policy cố định khi đổi `context length`.
- Tách **prefill** khỏi **decode** nếu muốn chẩn đoán. Benchmark end-to-end generation là useful nhưng trộn hai pha.

Đo raw cache bytes trực tiếp từ tensors đáng tin hơn `max_memory_allocated()` cho câu hỏi “cache tăng thế nào”, vì allocator có reserved blocks và temporaries.

```python
def kv_cache_bytes(cache):
    """Exact bytes of the K/V tensors presently retained by this toy model."""
    return sum(k.numel() * k.element_size() + v.numel() * v.element_size()
               for k, v in cache)


@torch.inference_mode()
def cached_decode_work(model, prompt_ids, new_tokens):
    """Generate greedily; return cache so its retained bytes can be inspected."""
    logits, cache = model(prompt_ids, use_cache=True)  # prefill
    for _ in range(new_tokens):
        next_id = logits[:, -1].argmax(dim=-1, keepdim=True)
        logits, cache = model(next_id, cache, use_cache=True)
    return cache


@torch.inference_mode()
def uncached_generation_work(model, prompt_ids, new_tokens):
    ids = prompt_ids
    for _ in range(new_tokens):
        logits, _ = model(ids, use_cache=False)
        next_id = logits[:, -1].argmax(dim=-1, keepdim=True)
        ids = torch.cat((ids, next_id), dim=1)


def measure_cuda_ms(fn, warmup=10, repeats=30):
    if not torch.cuda.is_available():
        raise RuntimeError("This timing helper requires CUDA")
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    for _ in range(repeats):
        fn()
    end.record()
    torch.cuda.synchronize()
    return start.elapsed_time(end) / repeats


# Make max_seq_len large enough for largest context + new_tokens.
device = "cuda"
model = TinyGPTWithCache(
    vocab_size=4096, max_seq_len=1152, d_model=192, n_heads=6, n_layers=4
).to(device).eval()
new_tokens = 64

print("context | uncached ms | cached ms | final raw KV MiB")
for context_len in (16, 64, 256, 512, 1024):
    prompt = torch.randint(0, 4096, (1, context_len), device=device)

    # A correctness check for each relevant context is cheap insurance.
    assert_cached_logits_match(model, prompt, prompt[:, :1])

    uncached_ms = measure_cuda_ms(
        lambda: uncached_generation_work(model, prompt, new_tokens)
    )
    cached_ms = measure_cuda_ms(
        lambda: cached_decode_work(model, prompt, new_tokens)
    )
    final_cache = cached_decode_work(model, prompt, new_tokens)
    cache_mib = kv_cache_bytes(final_cache) / (1024 ** 2)
    print(f"{context_len:7d} | {uncached_ms:11.2f} | {cached_ms:9.2f} | {cache_mib:16.2f}")
```

`max_seq_len=1152` trong ví dụ là $1024+64+\text{one optional final decode step}$; chọn margin rõ ràng hoặc điều chỉnh generator để không chạy pass cuối. Nếu chạy trên CPU, dùng `time.perf_counter()` thay CUDA events, tăng `repeats`, và chỉ so sánh trong cùng một machine/process; kết quả sẽ không đại diện GPU serving.

### 7.2 Kết quả mong đợi và cách diễn giải

| Quan sát | Diễn giải hợp lý |
|---|---|
| cached logits fail | cache semantics sai; chưa được benchmark performance |
| greedy outputs khớp nhưng logits không khớp | `argmax` che difference; vẫn là bug/numerical issue cần điều tra |
| raw KV MiB tăng gần tuyến tính theo context | đúng với công thức $M_{KV}$ |
| cached generation nhanh hơn uncached khi context lớn | expected direction: prefix work không bị làm lại |
| cached chưa nhanh hơn trên toy model/context ngắn | có thể đúng: `torch.cat`, Python loop, tiny matrix, kernel-launch overhead hoặc hardware làm overhead lớn hơn saving |
| GPU peak memory không đúng bằng raw KV MiB | expected: peak gồm weights, activations/temporaries và allocator behavior |

Đừng báo một “speedup” chung từ toy benchmark. Nó phụ thuộc model size, prompt/output length, batch size, implementation, precision và hardware. Raw explainer trong wiki có nêu khoảng `5x` như một minh họa thực tế, nhưng không có benchmark primary/reproducible kèm theo; không dùng nó làm expected value cho code trên.[^kv-caching-explained]

## 8. Đọc đường cong: prefill, decode, và cache growth

Để biết bottleneck nằm ở đâu, đo ba phép tách riêng:

1. **`prefill(P)`**: `model(prompt, use_cache=True)` một lần. Theo dõi latency khi tăng prompt length.
2. **one-token `decode` at context S**: prefill trước, rồi time `model(one_token, cache, use_cache=True)` nhiều lần hoặc với cache đã có length $S$.
3. **end-to-end generate G tokens**: bao gồm một prefill và $G$ decode steps.

```text
end-to-end generation
= prefill latency
+ sampling/control overhead
+ sum of incremental decode latencies
```

Đây là lý do không nên kết luận “KV cache làm TTFT nhanh”: prefill thực ra **xây** cache và prompt dài hơn thường làm TTFT cao hơn. KV cache chủ yếu loại bỏ repeat work ở decode. Prefix caching, chunked prefill và attention kernels là các vấn đề khác, dù đều liên quan serving.[^kv-caching-explained]

## 9. Khi equivalence fail: checklist theo thứ tự

| Triệu chứng | Nguyên nhân thường gặp | Cách kiểm tra/sửa |
|---|---|---|
| fail ngay sau prefill | full/cached forward không cùng weights/mode hoặc mask sai | gọi `eval()`, kiểm tra cùng model instance; test causal mask |
| chỉ fail từ decode step 1 | position IDs reset về 0 | dùng offset `past_len + arange(T_new)` |
| chỉ fail khi `T_new > 1` | causal mask chỉ đúng cho `T_new=1` | query local `i` chỉ đọc keys `<= past_len+i` |
| shapes đúng nhưng logits sai | concatenate sai dimension hoặc cache layer bị tráo | K/V phải append trên sequence dimension và cache phải map đúng layer |
| output khác không ổn định giữa runs | dropout/sampling/randomness | `eval()`, compare logits; dùng greedy hoặc fixed generator |
| sequence càng dài càng sai | cache bị overwrite, append duplicate, hoặc context/position limit | assert cache length tăng đúng `T_new` mỗi call |
| BF16/FP16 khác nhỏ | floating-point order/kernel khác | so FP32 trước; chỉ nới tolerance sau khi semantics đúng |

Một assertion có ích trong debug là kiểm tra cache length sau mỗi call:

```python
expected_len = prompt.size(1)
for token in continuation.split(1, dim=1):
    _, cache = model(token, cache, use_cache=True)
    expected_len += 1
    assert all(k.size(-2) == expected_len and v.size(-2) == expected_len
               for k, v in cache)
```

## 10. Từ toy cache đến serving thực tế

Toy code dùng `torch.cat` ở mỗi decode step. Điều này đơn giản, nhưng có thể allocate/copy growing tensors lặp lại. Production server thường preallocate cache blocks, reuse blocks, pack nhiều requests và quản lý fragmentation; [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md) là một ví dụ về logical-to-physical block mapping.

Các hướng mở rộng sau giữ hoặc thay đổi trade-off khác nhau:

- **GQA/MQA**: giảm số KV heads $H_{KV}$ ngay từ architecture, giảm cache bytes/token.
- **KV quantization/compression/eviction**: giảm bytes hoặc số token cached, nhưng có thể làm giảm quality hay thêm conversion overhead.
- **PagedAttention/prefix sharing**: giảm allocation waste và share common prefix; không làm mỗi K/V vector nhỏ hơn.
- **FlashAttention-style kernels**: tối ưu attention IO/kernels, đặc biệt khác nhau giữa long-prompt prefill và one-token decode.
- **linear/recurrent attention**: thay token-addressable growing KV state bằng fixed-size state, cùng một trade-off retrieval/capacity khác hẳn standard KV cache.

Các optimization này chỉ đáng thử sau khi baseline pass test equivalence. Nếu mechanism được thiết kế là exact, logits cần tương đương trong numerical tolerance; nếu nó lossy (quantization, eviction, compression), hãy chuyển câu hỏi thành quality/latency/memory trade-off có đo lường, không kỳ vọng equality tuyệt đối.

## 11. Bài tập tự kiểm chứng

1. Chạy test logits với `T_new=1`, rồi sửa test để prefill một chunk và decode một chunk `T_new>1`; chứng minh mask offset hoạt động.
2. Cố ý reset `position_ids` về zero trong decode; quan sát test fail và giải thích vì sao.
3. In cache shapes của mọi layer sau prefill và từng decode step; đối chiếu công thức memory.
4. Vẽ `context length → raw KV MiB`, `context length → prefill ms`, và `context length → one-token decode ms` thành ba biểu đồ riêng.
5. Thay MHA toy model bằng GQA có ít KV heads hơn; kiểm tra cache bytes giảm theo $H_{KV}$ và test logits baseline của **cùng architecture** vẫn pass.

## Relationships

- **Elaborates:** Stage 5 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng implementation, correctness tests, và measurements cho `KV caching`.
- **Builds on:** [KV caching](kv-caching.md) về cơ chế compute–memory; [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md) về request lifecycle và latency vocabulary.
- **Depends on:** [Attention: beginner's guide for causal language models](attention-beginner-guide.md) và [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) cho causal-attention semantics và minimal GPT baseline.
- **Prepares for:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md), và [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md).

## Evidence limits

Nguồn raw về `KV caching` là một explainer secondary không có benchmark code, hardware configuration hay citation primary cho con số speedup được nêu. Cơ chế K/V attention dựa trên Transformer gốc; phân tích cost, code, test và quy trình benchmark trong bài là **pedagogical synthesis**. Hãy chạy benchmark trên target model và serving stack của bạn trước khi suy ra latency, throughput, hoặc memory capacity production.[^vaswani-transformer-2017][^kv-caching-explained]

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially the scaled dot-product attention definition and masking discussion.
[^kv-caching-explained]: “KV Caching in LLMs, Clearly Explained,” [raw source](../raw/KVCachinginLLMsClearlyExplained.md), Parts 1–6 and tl;dr. It is secondary orientation material; its reported practical speedup and memory illustrations are not independently benchmarked in this wiki.
