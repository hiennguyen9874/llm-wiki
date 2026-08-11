---
type: Synthesis
title: "FlashAttention: tiled attention và online softmax cho người mới"
description: A beginner-first course on how FlashAttention preserves exact causal softmax attention while reducing HBM traffic and quadratic intermediate memory through tiling, online softmax, and recomputation.
tags: [flashattention, attention, gpu, memory-io, online-softmax, pytorch, learning-roadmap]
status: stable
created: 2026-08-11
generated:
  by: llm-wiki-agent/1
  at: 2026-08-11T21:32:06+07:00
sources:
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
---

# FlashAttention: `tiled attention` và `online softmax` cho người mới

`FlashAttention` là cách triển khai GPU cho **exact scaled dot-product attention**. Thay vì materialize rồi đọc/ghi các ma trận `scores` và `attention weights` kích thước $T\times T$ trong HBM/VRAM, nó xử lý từng `tile` của Q, K, V trong on-chip SRAM/registers, duy trì các statistics của `online softmax`, và chỉ giữ output cuối cùng cùng state theo từng query row. Vì vậy, FlashAttention thay đổi **data movement và evaluation order**, không thay đổi attention formula, causal mask, hay token nào được phép attend (ngoại trừ sai khác floating-point rất nhỏ do precision và reduction order).[^flashattention-summary]

> [!success] Sau bài này
> Bạn có thể giải thích vì sao `O(T²)` FLOPs và `O(T²)` intermediate memory là hai vấn đề khác nhau; tự suy ra `online softmax`; viết một reference tiled implementation để test correctness; và phân biệt FlashAttention với sparse, sliding-window, hay linear attention.

Các ví dụ, code, và cách kiểm chứng dưới đây là **pedagogical synthesis**. Code Python minh họa semantics và không phải CUDA kernel đủ nhanh để thay production implementation.

## 1. Prerequisites và mục tiêu học

Bài này giả sử bạn đã biết công thức `scaled dot-product attention`, ý nghĩa Q/K/V, và `causal mask`. Nếu chưa, hãy đọc [Attention: beginner's guide for causal language models](attention-beginner-guide.md) trước. Công thức nền tảng cho một head là:

$$
S=\frac{QK^\top}{\sqrt d}+M,\qquad
P=\operatorname{softmax}(S),\qquad
O=PV,
$$

trong đó $Q,K\in\mathbb{R}^{T\times d}$, $V\in\mathbb{R}^{T\times d_v}$, và $M_{ij}=-\infty$ khi key $j$ bị mask. Với causal self-attention, $j>i$ bị block: query ở position $i$ chỉ đọc current/past keys.[^vaswani-transformer-2017]

`FlashAttention` không thay Q/K/V projections, positional encoding, MHA/GQA grouping, hay output projection. Nó tối ưu phần tính $P$ và $PV$ sau khi Q/K/V đã có.

## 2. Vấn đề của implementation attention ngây thơ

Một implementation dễ đọc thường làm theo ba bước:

```python
scores = q @ k.transpose(-2, -1) / math.sqrt(head_dim)  # (..., T, T)
scores = scores.masked_fill(~causal_mask, float("-inf"))
weights = torch.softmax(scores, dim=-1)                 # (..., T, T)
out = weights @ v                                        # (..., T, d_v)
```

`q @ kᵀ` tạo một score cho mọi cặp query–key. Với sequence length $T$, mỗi head có $T^2$ scores và $T^2$ softmax weights. Chẳng hạn, $T=32{,}768$ cho khoảng $1.07$ billion entries; một tensor FP16 như vậy riêng nó xấp xỉ 2 GiB. Batch size, head count, gradients, dropout state, và các activations khác làm memory training còn lớn hơn.[^flashattention-summary]

Điểm cần phân biệt:

| Đại lượng | Full dense attention | FlashAttention |
|---|---:|---:|
| Query–key interactions/FLOPs | $O(T^2d)$ | vẫn $O(T^2d)$ |
| `scores`/`weights` intermediate trong HBM | $O(T^2)$ | không materialize toàn bộ |
| Attention semantics | full softmax trên allowed keys | như cũ |
| Cách đạt efficiency | nhiều HBM round trips | `tiling`, kernel fusion, on-chip working set |

Do đó, nói “FlashAttention là linear attention” là sai. Nó không làm number of query–key comparisons trở thành linear; nó giảm **IO và intermediate-memory traffic** của exact full attention.[^flashattention-summary]

## 3. Vì sao `memory IO` có thể quan trọng hơn FLOPs?

GPU có memory hierarchy: registers và shared-memory/SRAM rất nhanh nhưng nhỏ; HBM/VRAM lớn hơn nhưng chậm hơn đáng kể. Pipeline ngây thơ thường tạo `scores`, ghi chúng ra HBM, đọc lại để softmax, ghi `weights`, rồi đọc `weights` cùng V để tạo output. Các round trip đó có thể giới hạn wall-clock speed, dù GPU vẫn có năng lực matrix multiplication cao.[^flashattention-summary]

`IO-aware` nghĩa là algorithm được thiết kế theo nơi dữ liệu nằm và số byte phải di chuyển, không chỉ theo FLOPs asymptotic. FlashAttention cho một query block $Q_i$ lần lượt load các $(K_j,V_j)$ blocks vừa SRAM, cập nhật output, rồi bỏ score tile $S_{ij}$. Nó không cần lưu toàn bộ $S=QK^\top$ hoặc $P=\operatorname{softmax}(S)$.[^flashattention-summary]

```text
naive path:  Q,K → whole scores → HBM → softmax → whole weights → HBM → output

FlashAttention:
             Q tile + K/V tile → score tile in SRAM
                                  → mask + online softmax + output accumulator
                                  → discard score tile
```

`Tiling` giới hạn working set; `kernel fusion` giữ các bước score → scale → mask → softmax → weighted-V gần nhau để không phải persist intermediate tensors ở HBM.[^flashattention-summary]

## 4. Vì sao chia tile lại khó: `softmax` cần mẫu số toàn row

Với một query row có logits $x_1,\ldots,x_T$:

$$
\operatorname{softmax}(x)_j=\frac{e^{x_j}}{\sum_{r=1}^{T}e^{x_r}}.
$$

Nếu xử lý keys theo block, block đầu tiên chưa biết future blocks sẽ đóng góp bao nhiêu vào denominator. Cách stable thông thường cũng cần row maximum:

$$
m=\max_j x_j,\qquad l=\sum_j e^{x_j-m},\qquad
\operatorname{softmax}(x)_j=\frac{e^{x_j-m}}{l}.
$$

`Online softmax` giải quyết điều đó bằng cách cập nhật $m$ và $l$ khi mỗi key tile đến. Ta cũng cập nhật unnormalized value accumulator $o$, để cuối cùng chỉ cần chia $o/l$.

## 5. Derivation của `online softmax`

Giả sử đã xử lý các blocks trước, với row-wise state:

$$
m_{old}=\max(\text{logits đã thấy}),\qquad
l_{old}=\sum_{x\ \text{đã thấy}} e^{x-m_{old}},
$$

$$
o_{old}=\sum_{x\ \text{đã thấy}} e^{x-m_{old}}v_x.
$$

Đến tile mới có logits $s$ và corresponding value rows $V_{tile}$, đặt:

$$
m_{tile}=\max(s),\qquad m_{new}=\max(m_{old},m_{tile}).
$$

Mọi contribution cũ phải đổi từ scale $m_{old}$ sang scale $m_{new}$, nên có correction:

$$
\alpha=e^{m_{old}-m_{new}}.
$$

Vì $e^{x-m_{new}}=e^{x-m_{old}}e^{m_{old}-m_{new}}$, state mới là:

$$
l_{new}=\alpha l_{old}+\sum_j e^{s_j-m_{new}},
$$

$$
o_{new}=\alpha o_{old}+\sum_j e^{s_j-m_{new}}v_j.
$$

Sau key tile cuối:

$$
O=\frac{o}{l}.
$$

Các phép toán này là đúng đại số với softmax toàn row: block mới không bị chuẩn hóa độc lập rồi concatenate. Đó là lý do FlashAttention vẫn `exact`. Rescale theo maximum cũng giữ exponentials trong range ổn định về numerical precision.[^flashattention-summary]

> [!warning] Lỗi trực giác thường gặp
> Không được chạy `softmax` riêng trên từng key tile rồi cộng các outputs. Mỗi tile khi đó có denominator khác nhau, nên result khác full attention. Cần giữ $m$, $l$, và rescale contribution cũ như các công thức trên.

## 6. `Tiled attention` với causal mask

Chia Q thành row tiles $Q_i$ và K/V thành column tiles $(K_j,V_j)$. Với mỗi $Q_i$, kernel stream tất cả allowed K/V tiles:

$$
S_{ij}=Q_iK_j^\top/\sqrt d.
$$

- Tile nằm hoàn toàn phía trên causal diagonal không có allowed entries, nên có thể skip.
- Tile cắt diagonal cần mask những entries có `key_position > query_position` thành $-\infty$ **trước** exponential.
- Mỗi query row có $m$, $l$, $o$ riêng. Không được dùng một maximum/denominator chung cho cả query tile.

```text
causal tiles (Q rows × K columns)

          K0     K1     K2
Q0      process  skip   skip
Q1      process  process skip
Q2      process  process process

Diagonal tiles vẫn cần element-wise causal mask.
```

Causal constraint giữ nguyên. FlashAttention không cho token nhìn future token; nó chỉ tránh compute/write không cần thiết và thay đổi schedule.[^flashattention-summary]

## 7. Reference PyTorch: implement semantics trước

Hàm dưới đây dùng một head, một sequence `(T, d)` để làm rõ algorithm. Nó materialize **một score tile** `(query_block, key_block)` tại một thời điểm; Python loops khiến nó chậm hơn built-in kernel, nhưng output phải khớp với dense reference trong `float32`.

```python
import math
import torch
import torch.nn.functional as F


def dense_causal_attention(q, k, v):
    """Reference semantics; q/k: (T, d), v: (T, d_v)."""
    T, d = q.shape
    scores = q @ k.T / math.sqrt(d)
    causal = torch.ones(T, T, dtype=torch.bool, device=q.device).tril()
    scores = scores.masked_fill(~causal, -torch.inf)
    return F.softmax(scores, dim=-1) @ v


def tiled_causal_attention(q, k, v, block_size=64):
    """Pedagogical online-softmax implementation, not a fast GPU kernel."""
    T, d = q.shape
    d_v = v.shape[-1]
    out = torch.empty(T, d_v, dtype=q.dtype, device=q.device)

    for q_start in range(0, T, block_size):
        q_end = min(q_start + block_size, T)
        q_tile = q[q_start:q_end]
        rows = q_end - q_start

        # One m/l/o state per query row.
        m = torch.full((rows, 1), -torch.inf, dtype=q.dtype, device=q.device)
        l = torch.zeros((rows, 1), dtype=q.dtype, device=q.device)
        o = torch.zeros((rows, d_v), dtype=q.dtype, device=q.device)
        q_positions = torch.arange(q_start, q_end, device=q.device)[:, None]

        for k_start in range(0, T, block_size):
            # This and later K tiles are entirely in the future of every Q row.
            if k_start >= q_end:
                break
            k_end = min(k_start + block_size, T)
            k_tile, v_tile = k[k_start:k_end], v[k_start:k_end]

            scores = q_tile @ k_tile.T / math.sqrt(d)
            k_positions = torch.arange(k_start, k_end, device=q.device)[None, :]
            scores = scores.masked_fill(k_positions > q_positions, -torch.inf)

            tile_m = scores.max(dim=-1, keepdim=True).values
            m_new = torch.maximum(m, tile_m)
            alpha = torch.exp(m - m_new)          # rescale previous tile state
            p_unnormalized = torch.exp(scores - m_new)

            l = alpha * l + p_unnormalized.sum(dim=-1, keepdim=True)
            o = alpha * o + p_unnormalized @ v_tile
            m = m_new

        out[q_start:q_end] = o / l
    return out


torch.manual_seed(0)
q = torch.randn(11, 8, dtype=torch.float32)
k = torch.randn(11, 8, dtype=torch.float32)
v = torch.randn(11, 6, dtype=torch.float32)

dense = dense_causal_attention(q, k, v)
tiled = tiled_causal_attention(q, k, v, block_size=4)
torch.testing.assert_close(tiled, dense, rtol=1e-5, atol=1e-6)
```

`m=-∞` lúc khởi tạo là hợp lệ vì causal row đầu tiên luôn được phép attend chính nó. `alpha` ở tile đầu là $e^{-\infty}=0$, nên state bắt đầu chỉ từ tile hiện tại. Để hỗ trợ padding/cross-attention, cần bảo đảm mỗi valid query row có ít nhất một allowed key; `softmax` trên một row toàn $-∞$ là undefined/`NaN`.

## 8. Dùng production API, không tự viết CUDA kernel

Trong code model, hãy dùng implementation được framework/runtime hỗ trợ. Với PyTorch, `scaled_dot_product_attention` là semantic API; ở CUDA, nó **có thể** select FlashAttention hoặc backend khác tùy PyTorch version, device, dtype, tensor shape, mask, và enabled backend. Không nên assume mọi call đều dùng FlashAttention chỉ vì API này được gọi.

```python
# q, k, v: (batch, heads, sequence, head_dim)
# Causal masking is part of the requested semantics.
out = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=0.0)
```

Đúng workflow là: (1) làm dense reference nhỏ; (2) test backend output against reference với fixed inputs, `eval`/no dropout; (3) profile memory và time trên target GPU/workload; (4) kiểm tra backend diagnostics/documentation của runtime nếu việc dispatch là requirement. Không chuyển `is_causal=True` thành `False` để kernel chạy được: đó là semantic bug trong causal language model.

## 9. Kiểm chứng: “exact” nghĩa gì trong thực hành?

So sánh output của tiled/kernel implementation với dense reference ở sequence ngắn và precision đủ cao. Kiểm tra cả non-causal và causal path nếu model dùng cả hai; với causal path, test future perturbation vẫn không đổi earlier outputs.

```python
@torch.no_grad()
def assert_causal_output(attention_fn, q, k, v, cut):
    baseline = attention_fn(q, k, v)
    changed_k, changed_v = k.clone(), v.clone()
    changed_k[cut + 1:] = torch.randn_like(changed_k[cut + 1:])
    changed_v[cut + 1:] = torch.randn_like(changed_v[cut + 1:])
    changed = attention_fn(q, changed_k, changed_v)
    torch.testing.assert_close(baseline[:cut + 1], changed[:cut + 1])

assert_causal_output(tiled_causal_attention, q, k, v, cut=5)
```

Expected equality là `close`, không phải bitwise identical. `FP16`/`BF16`, fused operations, parallel reduction order, và dropout có thể tạo numerical difference. Nhưng nếu discrepancy lớn, hoặc future perturbation làm past outputs thay đổi, hãy kiểm tra mask orientation, scale $1/\sqrt d$, row-wise normalization, và whether dropout is disabled/controlled before đổ lỗi cho floating point.[^flashattention-summary]

## 10. Training backward: đổi compute lấy memory

Training backward cần thông tin về softmax probabilities. Dense implementation có thể retain full $T\times T$ probability matrix, rất tốn activation memory. FlashAttention forward giữ output và small row-wise normalization state thay vì toàn bộ P; backward reload/recomputes tiles cần thiết. Đây là selective recomputation: thêm một phần compute để giảm HBM traffic và saved activations.[^flashattention-summary]

Điều này không có nghĩa model “không dùng memory”. Weights, other activations, gradients, optimizer state, KV cache (khi serving) vẫn có chi phí riêng. FlashAttention tối ưu một bottleneck cụ thể: attention intermediates và data movement.[^flashattention-summary]

## 11. FlashAttention không phải các kỹ thuật sau

| Kỹ thuật | Giữ full softmax trên mọi allowed token? | Giảm FLOPs bậc hai? | Bottleneck chính được xử lý |
|---|---|---:|---|
| FlashAttention | Có, up to floating-point variation | Không | HBM IO và $T^2$ intermediate tensors |
| `sliding-window`/sparse attention | Không, bỏ một số token pairs | Có thể | số interactions và memory |
| linear attention | Không theo standard softmax token-addressable form | Có | recurrent state và asymptotic cost |
| MQA/GQA | Có trong chosen head layout | Không ở prefill full attention | decode KV-cache bandwidth/capacity |
| KV caching | Có | Không cho one prompt prefill | recomputation across decode steps |

`MQA/GQA`, KV caching, và FlashAttention có thể cùng tồn tại trong một model/server vì chúng nhắm các bottleneck khác nhau. Đặc biệt, FlashAttention thường hữu ích cho training và prompt `prefill`; một-token `decode` thường phải đọc accumulated KV cache và có thể bị bandwidth-bound.[^flashattention-summary]

## 12. Khi nào FlashAttention chưa đủ?

Nếu double context length, exact full attention vẫn có roughly four times query–key interaction work. FlashAttention có thể làm dense attention practical hơn nhưng không xóa giới hạn quadratic. Context rất dài có thể cần sparse/restricted attention, sequence-parallel execution, retrieval, hoặc architecture thay đổi retrieval/state trade-off như [linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md). Đó là thay đổi algorithm/architecture, khác bản chất với FlashAttention.[^flashattention-summary]

Phiên bản FlashAttention-2/-3 tiếp tục giữ tiled exact attention nhưng tối ưu work partitioning và hardware execution. Hãy xem [FlashAttention implementation evolution](flashattention-implementation-evolution.md) sau khi hiểu invariant `exact semantics, different IO schedule` của bài này.

## 13. Checklist trước khi tích hợp

1. **Giữ semantics:** scale, mask, dropout behavior, GQA/MHA layout, và output dtype phải khớp model hiện tại.
2. **Test nhỏ:** compare với dense reference trên nhiều $T$ không chia hết cho tile size; test causal future perturbation.
3. **Đo đúng phase:** separate training, prefill, và decode; đừng suy ra decode speed từ prefill benchmark.
4. **Đo trên target:** benchmark phụ thuộc GPU, PyTorch/runtime, dtype, head dimension, batch/sequence shape, và kernel dispatch.
5. **Profile memory:** xác nhận peak memory giảm trên workload thật; saving attention intermediate không đồng nghĩa mọi memory bottleneck biến mất.

## 14. Tóm tắt

`FlashAttention = tiled exact attention + online softmax + kernel fusion`. Nó giữ result của standard masked softmax attention, nhưng thay vì materialize full quadratic `scores`/`weights` trong HBM, nó stream tiles qua on-chip memory và dùng $(m,l,o)$ per query row để chuẩn hóa đúng. Đây là bài học systems quan trọng: cùng một attention algorithm và cùng asymptotic FLOPs vẫn có thể có tốc độ/memory khác xa nhau khi data movement thay đổi.[^flashattention-summary]

Bài này mở rộng Stage 6 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Học nó sau Q/K/V và causal masking, trước khi đánh giá các phương pháp thực sự thay đổi attention semantics.

## Relationships

- **Elaborates:** Stage 6 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng theory, reference code, và correctness tests.
- **Builds on:** [Attention: beginner's guide for causal language models](attention-beginner-guide.md) và [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md).
- **Expands:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) theo hướng beginner-first.
- **Optimizes:** [Self-attention computational profile](self-attention-computational-profile.md)'s intermediate-memory traffic while retaining its quadratic arithmetic.
- **Extended by:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md).
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which changes the retrieval/state formulation.

[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [raw source](../raw/FlashAttention.md), Sections 1–18. This is secondary-source evidence summarizing Dao et al., “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness” (NeurIPS 2022); the primary paper has not been independently ingested here.
[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” arXiv:1706.03762v7, [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially `model_architecture.tex`.
