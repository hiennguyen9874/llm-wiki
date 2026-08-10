---
type: Synthesis
title: Attention: beginner's guide for causal language models
description: A beginner-first guide to Q/K/V projections, scaled dot-product attention, causal masking, multi-head attention, implementation shapes, and correctness tests.
tags: [attention, softmax-attention, multi-head-attention, causal-masking, pytorch, learning-roadmap]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T23:34:28+07:00 }
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
---

# Attention: beginner's guide for causal language models

`Attention` là cơ chế để mỗi token tạo một **weighted mixture** từ các token trong context. Với mỗi token đang xử lý, model tạo `Query` (Q), so Q với các `Key` (K) của những token có thể đọc, chuẩn hóa các scores bằng `softmax`, rồi dùng weights đó để trộn các `Value` (V). Trong một causal language model, `causal mask` buộc token ở vị trí $t$ chỉ được đọc vị trí $\leq t$; vì vậy training song song vẫn không làm lộ future token. `Multi-head attention` chạy nhiều phép truy xuất như vậy trên các learned projection khác nhau.[^vaswani-transformer-2017]

```text
hidden states X
    ├─ linear projection → Q: mỗi position đang tìm gì?
    ├─ linear projection → K: mỗi position phù hợp với truy vấn nào?
    └─ linear projection → V: nội dung sẽ được lấy và trộn

QKᵀ → scale → add mask → softmax → attention weights → weights V → output
```

> [!success] Sau bài này
> Bạn có thể đọc công thức `Attention(Q, K, V)`, theo dõi shapes trong code, phân biệt `self-attention` với `cross-attention`, tự viết causal `multi-head attention`, và test rằng future token không ảnh hưởng past output.

Các ví dụ số, code, và quy trình debug bên dưới là **synthesis mang tính sư phạm**. Chúng diễn giải cơ chế trong nguồn primary, không phải recipe tái tạo training hay benchmark của Transformer.

## 1. Vì sao một token cần `Attention`?

Một `FFN` (feed-forward network) xử lý từng token position độc lập: cùng một transformation được áp dụng tại mọi vị trí, nhưng bản thân nó không chọn đọc token ở vị trí khác. `Attention` là phần tạo communication giữa positions. Ví dụ, khi xử lý token `nó`, model có thể cần lấy thông tin từ một noun xuất hiện trước đó; khi xử lý một verb, nó có thể cần một subject hoặc adverb ở xa.

Điểm quan trọng: `Attention` không dùng luật ngữ pháp được viết sẵn. Q, K, V và output projection là parameters được học qua loss của nhiệm vụ. Một attention weight lớn chỉ nói rằng, trong head và layer đó, representation ở query position đã lấy nhiều numerical signal từ value position; nó **không tự nó chứng minh** model có một lời giải thích ngôn ngữ đáng tin cậy.

Trong full `self-attention`, một layer cho phép mọi cặp position hợp lệ tương tác trực tiếp. Đây là lợi thế về dependency path và parallel training, nhưng số query–key comparisons tăng theo $T^2$ với sequence length $T$.[^vaswani-transformer-2017] Xem thêm [self-attention computational profile](self-attention-computational-profile.md).

## 2. Trực giác về `Query`, `Key`, và `Value`

Hãy coi previous layer tạo hidden vector $x_t\in\mathbb{R}^{d_{model}}$ cho token ở position $t$. Một attention head tạo ba phiên bản learned của vector này:

$$
q_t=x_tW^Q,\qquad k_t=x_tW^K,\qquad v_t=x_tW^V.
$$

- `Query` ($q_t$): tín hiệu về loại thông tin mà position $t$ muốn truy xuất.
- `Key` ($k_j$): tín hiệu để position $j$ được so khớp với một query.
- `Value` ($v_j$): nội dung vector mà position $j$ đóng góp nếu được chọn.

Các mô tả trên chỉ là trực giác. Q, K, V không phải ba trường dữ liệu cố định như trong database; chúng là ba learned linear projection của hidden states. Một token có thể đóng góp key/value khác nhau ở head hoặc layer khác nhau.

Với query ở position $t$, compatibility score với key ở position $j$ là dot product $q_tk_j^\top$. Score cao hơn thường tạo weight lớn hơn sau `softmax`, nhưng score âm vẫn hợp lệ; chỉ relative scores trong cùng một row mới quyết định distribution.

## 3. `Scaled dot-product attention` từng bước

Xếp hidden states của một sequence dài $T$ thành $X\in\mathbb{R}^{T\times d_{model}}$. Với một head có key/query dimension $d_k$ và value dimension $d_v$:

$$
Q=XW^Q\in\mathbb{R}^{T\times d_k},\quad
K=XW^K\in\mathbb{R}^{T\times d_k},\quad
V=XW^V\in\mathbb{R}^{T\times d_v}.
$$

Công thức cho toàn bộ queries là:

$$
\operatorname{Attention}(Q,K,V)=
\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
$$

`softmax` được áp dụng trên **mỗi row** của score matrix, tức trên các key positions mà một query được phép xem.

| Bước | Shape (một sequence, một head) | Ý nghĩa |
|---|---:|---|
| `Q`, `K` | `(T, d_k)` | query/key vectors |
| `V` | `(T, d_v)` | value vectors |
| `Q @ K.transpose(-2, -1)` | `(T, T)` | mỗi row là scores từ một query đến mọi key |
| `softmax(scores, dim=-1)` | `(T, T)` | weights của mỗi query; mỗi row sum bằng 1 |
| `weights @ V` | `(T, d_v)` | weighted mixture cho mỗi query |

### Một ví dụ số nhỏ

Giả sử một query có ba compatibility scores đã scale là $[2,1,0]$, và ba value vectors là:

$$
v_1=[1,0],\qquad v_2=[0,1],\qquad v_3=[1,1].
$$

Sau `softmax`, weights xấp xỉ $[0.665,0.245,0.090]$. Output của query là:

$$
0.665v_1 + 0.245v_2 + 0.090v_3
\approx [0.755,0.335].
$$

Vì weights là positive và sum bằng 1, output của một head là weighted average của V vectors. `softmax` không chọn đúng một token một cách bắt buộc: query có thể lấy signal từ nhiều positions cùng lúc. Và output không phải token ID hay probability vocabulary; nó vẫn là một hidden vector, được đưa vào các phần tiếp theo của network.

### Vì sao phải chia cho $\sqrt{d_k}$?

Nếu các components của Q và K được giả sử độc lập, mean 0, variance 1, dot product của chúng có variance $d_k$. Khi $d_k$ lớn, scores dễ có magnitude lớn, `softmax` trở nên quá sắc, và gradients có thể rất nhỏ. Chia cho $\sqrt{d_k}$ giữ scale scores ổn định hơn trước `softmax`.[^vaswani-transformer-2017]

Đây là lý do tên gọi là **scaled** dot-product attention. Đừng thay bước này bằng việc chia output sau `softmax`: vị trí của scaling trong công thức ảnh hưởng distribution và gradients.

## 4. `Causal mask`: chặn future-token leakage

Trong next-token prediction, hidden state tại position $i$ không được lấy thông tin từ input ở position $j>i$. Nếu không, model có thể nhìn token sắp cần dự đoán trong training và loss sẽ thấp một cách giả tạo.

Đặt $S=QK^\top/\sqrt{d_k}$. Causal mask $M$ được **cộng trước `softmax`**:

$$
M_{ij}=\begin{cases}
0,&j\leq i\\
-\infty,&j>i,
\end{cases}
\qquad
A=\operatorname{softmax}(S+M).
$$

Row $i$ là query position; column $j$ là key position. Vì $\exp(-\infty)=0$, forbidden positions nhận attention weight bằng 0.

| query \ key | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| 0 | allow | block | block | block |
| 1 | allow | allow | block | block |
| 2 | allow | allow | allow | block |
| 3 | allow | allow | allow | allow |

Causal mask tạo lower triangle. Nó cho phép model tính tất cả rows trong một matrix operation khi training, nhưng mỗi row vẫn chỉ phụ thuộc left context. Transformer decoder kết hợp mask này với inputs offset by one position để bảo toàn autoregressive property.[^vaswani-transformer-2017] Bài [causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md) giải thích target shift và training/generation interface.

> [!warning] `causal mask` khác `padding mask`
> `causal mask` trả lời “position nào là future?”. `padding mask` trả lời “position nào chỉ là filler vì sequences trong batch có độ dài khác nhau?”. Một padded causal batch thường cần cả hai. Ngoài ra, Boolean-mask convention khác nhau giữa APIs: có API dùng `True = block`, API khác dùng `True = allow`. Luôn kiểm tra documentation và hành vi của layer đang dùng.

## 5. Ba cách dùng Q/K/V

Công thức giống nhau, nhưng nơi tạo Q/K/V quyết định loại attention:

| Loại | Q đến từ | K, V đến từ | Position nào có thể đọc? |
|---|---|---|---|
| `encoder self-attention` | encoder layer trước | encoder layer trước | mọi input position |
| causal `decoder self-attention` | decoder layer trước | decoder layer trước | chính nó và positions bên trái |
| `cross-attention` | decoder layer trước | encoder output | mọi input position |

Trong `self-attention`, cùng hidden-state matrix được projection thành cả Q, K, V, nhưng ba projection weights độc lập. Trong `cross-attention`, Q mô tả decoder đang cần gì, còn K/V là memory từ encoder. Decoder-only LLM thông thường dùng causal `self-attention`, không có encoder và do đó không có `cross-attention` trong backbone cơ bản.[^vaswani-transformer-2017]

## 6. Từ một head đến `multi-head attention`

Một head chỉ tạo một weight distribution trên positions và một weighted mixture của values. `Multi-head attention` cho mỗi head các projection $W_i^Q$, $W_i^K$, $W_i^V$ riêng, chạy attention song song, concatenate outputs, rồi dùng $W^O$ để trộn chúng:

$$
\operatorname{head}_i=\operatorname{Attention}(QW_i^Q,KW_i^K,VW_i^V),
$$

$$
\operatorname{MultiHead}(Q,K,V)=
\operatorname{Concat}(\operatorname{head}_1,\ldots,\operatorname{head}_h)W^O.
$$

Điều này cho model nhiều retrieval channels trên các representation subspaces khác nhau. Không nên gán nhãn cố định như “head 3 luôn làm syntax”: ý nghĩa một head phụ thuộc data, layer, checkpoint, và có thể phân tán giữa nhiều heads. Tuy nhiên, nhiều learned projections tránh việc một weighted average duy nhất phải gánh mọi kiểu retrieval.[^vaswani-transformer-2017]

Nếu $d_{model}=512$ và `n_heads=8`, base Transformer dùng $d_k=d_v=64$ mỗi head. Vì mỗi head hẹp hơn, tổng cost của eight heads xấp xỉ một full-width head, thay vì tăng gấp tám lần.[^vaswani-transformer-2017]

### Shapes trong batched implementation

Với `batch_size=B`, `sequence_length=T`, `d_model=D`, `n_heads=H`, và `head_dim=D/H`:

```text
input hidden states:       x      (B, T, D)
combined QKV projection:   qkv    (B, T, 3D)
split and reshape:         q,k,v  (B, H, T, head_dim)
attention scores:          scores (B, H, T, T)
attention output per head: out    (B, H, T, head_dim)
concatenate heads:         out    (B, T, D)
output projection:         y      (B, T, D)
```

A common bug là reshape đúng tổng số elements nhưng sai thứ tự axes. Sau `transpose(1, 2)`, cần đưa axes về `(B, T, H, head_dim)` trước khi `reshape(B, T, D)`; nếu không, head/time data bị trộn sai.

## 7. PyTorch: causal `multi-head attention` tối thiểu

Code này minh họa semantics, không tối ưu kernel hay KV cache. Nó nhận `x` từ prior layer và trả về tensor cùng shape.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.0):
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)
        self.dropout = dropout

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, D)
        B, T, D = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)

        # (B, T, D) -> (B, H, T, head_dim)
        def split_heads(t):
            return t.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        q, k, v = map(split_heads, (q, k, v))

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        causal = torch.ones(T, T, dtype=torch.bool, device=x.device).tril()
        scores = scores.masked_fill(~causal, float("-inf"))

        weights = F.softmax(scores, dim=-1)
        weights = F.dropout(weights, p=self.dropout, training=self.training)
        out = weights @ v  # (B, H, T, head_dim)

        out = out.transpose(1, 2).contiguous().view(B, T, D)
        return self.out_proj(out)


layer = CausalSelfAttention(d_model=128, n_heads=4)
x = torch.randn(2, 16, 128)
y = layer(x)
assert y.shape == x.shape
```

Implementation thực tế có thể fuse Q/K/V projection, use `scaled_dot_product_attention`, hoặc dùng FlashAttention. Những thay đổi đó nên giữ nguyên mathematical result (trừ floating-point variation và dropout) trong khi cải thiện data movement hoặc speed. [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) là một ví dụ; nó không biến full attention thành linear attention.

## 8. Kiểm tra correctness trước khi training lớn

### Test 1: future perturbation không đổi past outputs

Thay đổi tokens/hidden states sau `cut`. Với `eval()` để tắt dropout, output ở positions đến `cut` phải không đổi.

```python
@torch.no_grad()
def assert_causal(layer, x, cut):
    """x: (B, T, D), with 0 <= cut < T - 1."""
    layer.eval()
    changed = x.clone()
    changed[:, cut + 1:] = torch.randn_like(changed[:, cut + 1:])

    before = layer(x)[:, :cut + 1]
    after = layer(changed)[:, :cut + 1]
    torch.testing.assert_close(before, after, rtol=1e-5, atol=1e-6)

assert_causal(layer, x, cut=7)
```

Nếu test fail, kiểm tra trước: orientation của triangle, meaning của boolean mask, mask có được áp dụng **trước** `softmax` hay không, và `dropout`/`train()` state. Test này kiểm tra causality, không kiểm tra model đã học ngôn ngữ.

### Test 2: row sums và forbidden weights

Nếu expose `weights` khi debug, sau `softmax` mỗi allowed row phải có sum gần 1; weight ở upper triangle phải gần 0. Không dùng equality tuyệt đối với floating point. Nếu một row bị mask toàn bộ, `softmax` của toàn `-inf` có thể là `NaN`; causal self-attention bình thường luôn để diagonal position được phép đọc chính nó, nên không gặp trường hợp đó.

### Test 3: one-head trước, multi-head sau

Bắt đầu với `n_heads=1` và in shapes ở từng bước. Khi đúng, tăng lên nhiều heads. Điều này cô lập bug reshape/transpose khỏi bug mask hoặc optimizer. Sau đó, trong full causal LM, chạy behavioral causality test trực tiếp trên logits như mô tả ở [causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md).

## 9. Các nhầm lẫn phổ biến

1. **“`Attention` là tra cứu exact một token.”** Không hẳn. Standard softmax attention tạo weighted mixture của V vectors; weights thường dense.
2. **“Q là token hỏi, K/V là các token khác.”** Trong `self-attention`, mỗi position tạo đủ Q, K, V. Cùng position có thể vừa query vừa key/value.
3. **“`softmax(QKᵀ)` là đủ.”** Thiếu scaling $1/\sqrt{d_k}$ và, với causal LM, thiếu mask trước `softmax`.
4. **“Causal mask chỉ cần lúc generate.”** Sai. Training thấy cả sequence nên cần mask để chặn future leakage.
5. **“Mask sau `softmax` bằng setting weight thành 0.”** Chưa đủ nếu không renormalize; row weights sẽ không còn sum bằng 1. An toàn và thông dụng là mask scores bằng `-inf` trước `softmax`.
6. **“Nhiều heads nghĩa là mỗi head có một nhiệm vụ diễn giải được.”** Không có guarantee đó. Heads là learned channels, không phải annotation của con người.
7. **“Attention giải quyết sequence order.”** Attention core không tự biết position order. Transformer phải thêm positional information, chẳng hạn sinusoidal positional encoding hoặc [RoPE](rotary-position-embedding.md).
8. **“Full attention luôn nhanh.”** Nó parallel across known positions, nhưng score matrix có $T^2$ entries. Long context là bottleneck về compute và memory/IO, không chỉ là một implementation detail.[^vaswani-transformer-2017]

## 10. Bản đồ học tiếp

- Trước bài này: [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md) để hiểu next-token objective, target shift, và vì sao cần causality.
- Sau bài này: [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) để ghép attention với residual connection, normalization, FFN, và positional encoding thành block/model.
- Khi đã có model chạy được: [KV caching](kv-caching.md) giải thích vì sao generation không nên tính lại K/V của prefix ở mọi token; [multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) giảm KV-cache traffic bằng K/V sharing.
- Khi context dài: so sánh exact token-addressable attention với [linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md). Đây là trade-off architecture, không phải một toggle miễn phí.

Bài này triển khai Stage 3 trong [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md): hãy tự viết one-head, thêm causal test, rồi tổng quát thành `multi-head attention` trước khi xây decoder-only Transformer hoàn chỉnh.

## Relationships

- **Elaborates:** Stage 3 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng trực giác, công thức, implementation shapes, và correctness tests.
- **Builds on:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md), đặc biệt next-token objective và causal constraint.
- **Expands:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) với beginner-first implementation và debugging procedure.
- **Prepares for:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) và [KV caching](kv-caching.md).
- **Has profile:** [Self-attention computational profile](self-attention-computational-profile.md) khi attention spans toàn sequence.

[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” arXiv:1706.03762v7, [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially `model_architecture.tex` and `why_self_attention.tex`.
