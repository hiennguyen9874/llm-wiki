---
type: Synthesis
title: Decoder-only Transformer: beginner's guide
description: A beginner-first guide to the components, data flow, PyTorch implementation, and debugging of a minimal GPT-style decoder-only Transformer.
tags: [decoder-only-transformer, gpt, causal-language-modeling, transformer, pytorch, learning-roadmap]
status: stable
created: 2026-08-11
generated: { by: llm-wiki-agent/1, at: 2026-08-11T15:35:02+07:00 }
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: radford-generative-pre-training-2018
    resource: ../raw/gpt.pdf
    title: Improving Language Understanding by Generative Pre-Training
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
  - id: huggingface-openai-gpt-pytorch
    resource: ../raw/gpt-source.py
    title: PyTorch OpenAI GPT model
---

# Decoder-only Transformer: beginner's guide

`Decoder-only Transformer` là backbone của GPT-style language model. Nó nhận một prefix token, biến prefix đó thành hidden states qua nhiều `decoder block`, rồi dùng hidden state cuối để cho distribution của `next token`. Mỗi block chỉ gồm hai phép biến đổi chính: causal `multi-head self-attention` cho token đọc left context, và `FFN`/`MLP` để biến đổi từng position. `Residual connection` và `normalization` giúp signal và gradient đi qua nhiều block ổn định hơn. Khác với Transformer encoder–decoder gốc, backbone này không có encoder hoặc `cross-attention`.[^radford-generative-pre-training-2018][^radford-gpt-2-2019]

```text
input token IDs
  → token embedding + position embedding
  → [decoder block 1]
  → [decoder block 2]
  → ...
  → [decoder block N]
  → final normalization
  → vocabulary projection (`lm_head`)
  → logits for every position and vocabulary token
```

> [!success] Mục tiêu
> Sau bài này, bạn có thể giải thích data flow của một minimal GPT, phân biệt chức năng của `attention`, `FFN`, `residual connection`, và `LayerNorm`, tự đọc shapes trong implementation, và kiểm tra các lỗi kiến trúc trước khi train model lớn hơn.

Bài này là **synthesis sư phạm** dựa trên kiến trúc Transformer/GPT. Code minh họa một pre-normalization GPT nhỏ để nhìn rõ mechanics; nó không phải recipe tái tạo checkpoint hay benchmark của GPT/GPT-2.

## 1. `decoder-only` nghĩa là gì?

Tên gọi dễ gây nhầm vì Transformer gốc có cả encoder và decoder. Trong encoder–decoder Transformer cho machine translation:

- `encoder` đọc toàn bộ source sequence bằng bidirectional `self-attention`;
- `decoder` tạo target sequence bằng causal `self-attention` **và** `cross-attention` tới encoder outputs.[^vaswani-transformer-2017]

Một GPT-style `decoder-only Transformer` giữ phần causal processing theo thứ tự từ trái sang phải, nhưng bỏ encoder và `cross-attention`. Toàn bộ prompt, instruction, retrieved text, chat history, và phần response đã sinh đều được serialise thành **một token sequence**. Vì vậy model dùng cùng một mechanism để đọc context và dự đoán continuation.[^radford-generative-pre-training-2018]

| Architecture | Mỗi token được đọc gì? | `cross-attention`? | Ví dụ use case |
|---|---|---|---|
| `encoder-only` | cả left và right context | Không | token/sequence representation |
| `encoder-decoder` | decoder đọc left target context, rồi đọc encoder memory | Có | conditional generation từ source riêng |
| `decoder-only` | chỉ left context trong một combined sequence | Không | autoregressive language model |

`decoder-only` **không** có nghĩa model chỉ chạy một token tại một thời điểm trong training. Với `causal mask`, toàn bộ block token trong batch vẫn được xử lý song song; chỉ dependency của từng position bị giới hạn ở left context. Xem [causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md) để biết vì sao `teacher forcing` vẫn không làm lộ target tương lai.

## 2. Một forward pass từ IDs đến logits

Đặt:

- $B$: `batch_size`;
- $T$: `sequence_length` (số token trong input window);
- $V$: `vocab_size`;
- $D$: `d_model` hoặc `hidden_size`;
- $H$: `n_heads`; cần $D\bmod H=0$;
- $d_h=D/H$: chiều của một attention head.

Input IDs có shape `(B, T)`. Mỗi ID chỉ là integer, chưa mang ý nghĩa vector. Model tạo hidden state đầu tiên:

$$
X^{(0)} = E_{token}[\text{input\_ids}] + E_{position}[0:T],
\qquad X^{(0)}\in\mathbb{R}^{B\times T\times D}.
$$

Sau $N$ blocks, final hidden states được chiếu sang vocabulary:

$$
Z = \operatorname{lm\_head}(\operatorname{Norm}(X^{(N)})),
\qquad Z\in\mathbb{R}^{B\times T\times V}.
$$

`Z[b, t]` là vector `logits` cho **token ngay sau** `input_ids[b, t]`. Để tính `cross-entropy`, so nó với shifted `target[b, t]`, không phải chính `input_ids[b, t]`.

| Tensor | Shape | Vai trò |
|---|---:|---|
| `input_ids` | `(B, T)` | integer token IDs đã có trong context |
| `token_emb(input_ids)` | `(B, T, D)` | vector learned cho identity của token |
| `position_emb` | `(T, D)` | vector learned cho index trong window |
| `hidden` | `(B, T, D)` | representation chạy qua các blocks |
| `logits` | `(B, T, V)` | score chưa chuẩn hóa của mọi next-token candidate |
| `targets` | `(B, T)` | IDs của token đúng kế tiếp |

### `token embedding` và `position embedding`

Nếu chỉ dùng `token embedding`, cùng token ở position 2 và 200 khởi đầu bằng cùng vector; `attention` tự nó không có thứ tự tuần tự cố định. Vì vậy GPT ban đầu dùng learned token embeddings cộng với learned position embeddings.[^radford-generative-pre-training-2018] GPT-2 cũng dùng byte-level BPE tokenization và context window 1,024 token, nhưng các choice tokenizer/context length là configuration lịch sử, không phải định nghĩa của mọi decoder-only model.[^radford-gpt-2-2019]

`Position embedding` ở đây cho biết **vị trí tuyệt đối trong input window**, không phải số thứ tự từ trong câu. Một tokenization có thể tách một từ thành nhiều token. Các model hiện đại có thể thay learned absolute position embedding bằng `RoPE` hoặc phương pháp khác; điều đó thay cách biểu diễn position, không thay causal language-model objective. Xem [Rotary position embedding (RoPE)](rotary-position-embedding.md).

> [!example] Với input `[<BOS>, "Học", "AI"]`, `hidden[0, 1]` bắt đầu từ tổng của vector cho token `"Học"` và vector cho position `1`. Qua các blocks sau, vector đó có thể lấy signal từ `<BOS>` và chính nó, nhưng không thể đọc token bên phải.

## 3. Một `decoder block` làm gì?

Một block nhận `x` shape `(B, T, D)` và trả một tensor cùng shape. Trong pre-normalization form thường dùng trong GPT-style model, có thể viết:

$$
u = x + \operatorname{Attention}(\operatorname{Norm}_1(x)),
$$
$$
\operatorname{Block}(x) = u + \operatorname{MLP}(\operatorname{Norm}_2(u)).
$$

Công thức cho thấy ba ý quan trọng:

1. `Attention` là **communication across positions**: mỗi token chọn và trộn signal từ các token hợp lệ khác.
2. `MLP`/`FFN` là **computation at each position**: cùng transformation được áp dụng độc lập cho từng token position.
3. `Residual connection` cộng input cũ vào update mới; block không phải thay thế hoàn toàn representation trước đó.

Transformer gốc dùng post-normalization, tức `LayerNorm(x + Sublayer(x))`.[^vaswani-transformer-2017] GPT-2 báo cáo chuyển `LayerNorm` về input của mỗi sub-block (pre-layer normalization).[^radford-gpt-2-2019] Cả hai là architecture variants hợp lệ; đừng trộn công thức của variant này với code của variant kia khi debug hoặc load checkpoint.

### 3.1 Causal `multi-head self-attention`

Từ normalized state $U\in\mathbb{R}^{B\times T\times D}$, mỗi head tạo learned projections:

$$
Q=UW^Q,\quad K=UW^K,\quad V=UW^V.
$$

Sau khi reshape thành $H$ heads, mỗi head tính:

$$
A=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_h}}+M\right),
\qquad O=AV,
$$

trong đó causal mask $M_{ij}$ bằng $0$ nếu $j\le i$, và là một số âm rất lớn nếu $j>i$. Như vậy row $i$ chỉ lấy `Value` từ current/past positions. Các head outputs được concatenate, rồi qua output projection để quay lại width $D$.[^vaswani-transformer-2017]

Ở layer thấp, attention có thể truyền local signal; ở layer cao, nó có thể kết hợp representation đã contextualized từ nhiều layer trước. Tuy nhiên, không nên đọc một attention weight lớn như bằng chứng chắc chắn về một "lý do" ngôn ngữ của model: weight chỉ là một phần của computation có residual paths, MLP, và nhiều layers.

Chi tiết Q/K/V, mask orientation, và shape theo head nằm trong [Attention: beginner's guide for causal language models](attention-beginner-guide.md).

### 3.2 `FFN` / `MLP`

Sau attention, mỗi position đi qua cùng một two-layer network:

$$
\operatorname{MLP}(u)=W_2\,\phi(W_1u+b_1)+b_2.
$$

Thông thường $W_1$ mở rộng từ $D$ lên `d_ff` (ví dụ $4D$), activation `GELU` hoặc variant khác, rồi $W_2$ chiếu về $D$. GPT pre-training báo cáo inner FFN width 3,072 với hidden width 768 (tức $4D$); reference implementation cũng tạo MLP four-times width.[^radford-generative-pre-training-2018][^huggingface-openai-gpt-pytorch]

Dù MLP áp dụng independently tại mọi position, input của nó đã mang context do attention trộn vào. Vì vậy, câu "MLP xử lý từng token độc lập" nói về **một MLP call trong một layer**, không có nghĩa output cuối cùng của token không biết context.

### 3.3 `Residual connection`, `LayerNorm`, và `dropout`

- `Residual connection`: $x + f(x)$ tạo đường trực tiếp để information/gradient đi qua block. Vì branch `f` chỉ cần học một update, model sâu dễ tối ưu hơn so với liên tục ghi đè representation.
- `LayerNorm`: chuẩn hóa features trong hidden vector của từng token rồi học scale/shift. Nó khác `BatchNorm`: không cần statistics chạy trên batch, phù hợp với variable-length sequence và autoregressive use.
- `Dropout`: trong training, ngẫu nhiên bỏ một phần activations/weights theo configuration để regularize; trong `eval()` nó phải tắt để output deterministic cho cùng input (trừ numerical nondeterminism).

Đây là trực giác thiết kế, không phải bảo đảm rằng mọi training run sẽ ổn định. Learning rate, initialization, data, precision, batch size, và optimizer vẫn quyết định training behavior.

## 4. Stack blocks và `lm_head`

Một block chỉ thêm một round communication + computation. Stack $N$ blocks để representation được refine nhiều lần:

```text
x0 = token embedding + position embedding
x1 = block_1(x0)
x2 = block_2(x1)
...
xN = block_N(xN-1)
logits = lm_head(final_norm(xN))
```

`lm_head` là linear layer từ `D → V`. Nó không chọn token; nó xuất raw scores. `softmax` chỉ cần khi bạn muốn probabilities để sample/generate. Trong training PyTorch, đưa raw logits trực tiếp vào `F.cross_entropy`, vì hàm này đã thực hiện stable `log_softmax`.

Một common option là `weight tying`: dùng cùng weight matrix cho input token embedding và `lm_head`. Reference OpenAI GPT wrapper khai báo language-model projection weight tied với input embeddings.[^huggingface-openai-gpt-pytorch] Đây là option kiến trúc/parameterization, không phải điều kiện để một decoder-only Transformer hoạt động.

## 5. Minimal implementation bằng PyTorch

Code dưới đây ưu tiên rõ data flow hơn kernel efficiency. Nó dùng learned absolute `position embedding`, pre-`LayerNorm`, causal `multi-head attention`, GELU MLP, final normalization, và optional weight tying. Không có `KV cache`, mixed precision, distributed training, padding mask, hay flash-attention kernel.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.0):
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, D = x.shape
        # (B, T, D) → (B, H, T, d_h)
        def split_heads(y):
            return y.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        q = split_heads(self.q_proj(x))
        k = split_heads(self.k_proj(x))
        v = split_heads(self.v_proj(x))

        # Mỗi row của score matrix là một query position.
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        causal_mask = torch.tril(
            torch.ones(T, T, dtype=torch.bool, device=x.device)
        )
        scores = scores.masked_fill(~causal_mask, float("-inf"))
        weights = self.attn_dropout(F.softmax(scores, dim=-1))

        # (B, H, T, d_h) → (B, T, D)
        y = weights @ v
        y = y.transpose(1, 2).contiguous().view(B, T, D)
        return self.resid_dropout(self.out_proj(y))


class MLP(nn.Module):
    def __init__(self, d_model, dropout=0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),
            nn.Linear(4 * d_model, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class DecoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.0):
        super().__init__()
        self.ln_1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_heads, dropout)
        self.ln_2 = nn.LayerNorm(d_model)
        self.mlp = MLP(d_model, dropout)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))  # attention residual branch
        x = x + self.mlp(self.ln_2(x))   # MLP residual branch
        return x


class TinyGPT(nn.Module):
    def __init__(self, vocab_size, max_seq_len, d_model=192,
                 n_heads=6, n_layers=4, dropout=0.1, tie_weights=True):
        super().__init__()
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.position_emb = nn.Embedding(max_seq_len, d_model)
        self.dropout = nn.Dropout(dropout)
        self.blocks = nn.ModuleList(
            [DecoderBlock(d_model, n_heads, dropout) for _ in range(n_layers)]
        )
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        if tie_weights:
            self.lm_head.weight = self.token_emb.weight

    def forward(self, input_ids):
        B, T = input_ids.shape
        if T == 0 or T > self.max_seq_len:
            raise ValueError("input length must be in [1, max_seq_len]")

        positions = torch.arange(T, device=input_ids.device)
        x = self.token_emb(input_ids) + self.position_emb(positions)[None]
        x = self.dropout(x)
        for block in self.blocks:
            x = block(x)
        return self.lm_head(self.ln_f(x))  # (B, T, vocab_size)
```

### Cách nối code với CLM training

Model không tự tạo shifted targets. Data pipeline chịu trách nhiệm cắt một stream dài $T+1$ thành `x` và `y`:

```python
# ids: (B, T + 1)
x = ids[:, :-1]      # (B, T)
y = ids[:, 1:]       # (B, T)

model = TinyGPT(vocab_size=50_000, max_seq_len=x.size(1))
logits = model(x)    # (B, T, 50_000)
loss = F.cross_entropy(logits.flatten(0, 1), y.flatten())
loss.backward()
```

Ở `x[:, t]`, model tạo logits cho `y[:, t] = ids[:, t+1]`. Causal mask bảo đảm hidden state ở $t$ không đọc `x[:, t+1:]`. Training loop, validation, và generation sampler được trình bày đầy đủ hơn ở [causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md).

> [!warning] Code rõ ràng không đồng nghĩa code production
> Code tạo causal mask $(T,T)$ mới cho mỗi forward pass và materialize full score tensor `(B, H, T, T)`. Nó phù hợp để học và test. Production implementations thường cache mask, dùng fused kernel như FlashAttention, và dùng `KV cache` khi decode. Những thay đổi đó cần giữ nguyên causal-attention semantics.

## 6. Đọc shapes trong attention implementation

Ví dụ `B=2`, `T=128`, `D=192`, `H=6`, thì `d_h=32`:

| Operation | Shape |
|---|---:|
| `x` | `(2, 128, 192)` |
| mỗi `q`, `k`, `v` trước split | `(2, 128, 192)` |
| mỗi `q`, `k`, `v` sau split | `(2, 6, 128, 32)` |
| `q @ k.transpose(-2, -1)` | `(2, 6, 128, 128)` |
| `weights @ v` | `(2, 6, 128, 32)` |
| merge heads + `out_proj` | `(2, 128, 192)` |
| `lm_head` | `(2, 128, V)` |

Hai lỗi đặc biệt phổ biến:

1. **Mask ngược chiều.** `torch.tril` là lower triangle: query ở row `i` có thể đọc key ở columns `0..i`. Nếu dùng `triu` hoặc phủ định sai, model nhìn future tokens.
2. **Softmax sai dimension.** `dim=-1` chuẩn hóa trên key positions của *mỗi query*. Softmax trên head dimension hoặc query dimension làm attention không còn mang nghĩa công thức trên.

## 7. Debug theo thứ tự trước khi scale

| Check | Cách kiểm tra | Kết quả mong đợi |
|---|---|---|
| Configuration | `d_model % n_heads == 0` | mỗi head có integer `head_dim` |
| ID range | `0 <= input_ids < vocab_size` | không lỗi embedding index |
| Output shape | `model(x).shape` | `(B, T, V)` |
| Target shift | `torch.equal(x[:, 1:], y[:, :-1])` | `True` |
| Initial baseline | logits gần uniform | loss gần `log(V)` (chỉ là sanity check) |
| Tiny overfit | train lặp một vài batches | training loss giảm mạnh |
| Causality | đổi tokens sau `cut` | logits tại `<= cut` không đổi khi `eval()` |
| Generation | `eval()`, greedy decode | cùng input cho output lặp lại được trong cùng environment |

Causality test kiểm tra architecture behavior trực tiếp:

```python
@torch.no_grad()
def assert_causal(model, ids, cut):
    """ids: (B, T), with 0 <= cut < T - 1."""
    model.eval()
    changed = ids.clone()
    changed[:, cut + 1:] = torch.randint(
        model.vocab_size, changed[:, cut + 1:].shape, device=ids.device
    )
    original_logits = model(ids)[:, :cut + 1]
    changed_logits = model(changed)[:, :cut + 1]
    torch.testing.assert_close(original_logits, changed_logits,
                               rtol=1e-5, atol=1e-6)
```

Nếu test fail, kiểm tra mask orientation trước; sau đó kiểm tra shape transpose, accidental mixing across sequence dimension, model mode (`dropout`), và position IDs. Loss giảm **không** đủ chứng minh causal mask đúng: future-token leakage có thể làm training loss đẹp một cách giả tạo.

## 8. Những nhầm lẫn thường gặp

1. **"`decoder-only` là chỉ có attention."** Sai. Mỗi block còn có MLP, normalization, residual paths, và thường dropout.
2. **"Position embedding nằm trong attention."** Không nhất thiết. Với learned absolute position embedding trong code trên, nó được cộng vào token embedding trước block đầu tiên. RoPE lại tác động lên Q/K trong attention.
3. **"`lm_head` chỉ chạy ở final token."** Trong training, nó chạy cho mọi position để tính loss song song. Trong generation, chỉ logits ở final position hiện tại được dùng để chọn next token.
4. **"Causal mask đủ để model biết thứ tự."** Sai. Mask nói token nào *không được đọc*; không tự cung cấp position representation cho attention.
5. **"FFN không dùng context nên không quan trọng."** Sai. FFN biến đổi contextualized vector sau attention và chiếm phần lớn parameters/computation trong dense Transformer cấu hình cổ điển.
6. **"Mọi GPT dùng cùng `LayerNorm` placement."** Sai. Transformer gốc và GPT-2 đã dùng post- và pre-normalization khác nhau.[^vaswani-transformer-2017][^radford-gpt-2-2019]
7. **"Cùng architecture sẽ cho cùng quality."** Sai. Data, tokenizer, number of parameters, context length, optimization, training compute, và post-training đều ảnh hưởng mạnh đến behavior.

## 9. Bước tiếp theo sau minimal GPT

Sau khi model nhỏ pass các test trên, học theo thứ tự sau:

1. Thêm [KV caching](kv-caching.md) để generation không recompute K/V của toàn prefix ở từng decode step.
2. Thay learned absolute position embedding bằng [RoPE](rotary-position-embedding.md), rồi hiểu length/generalization trade-off.
3. Học [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) để giảm decode-time KV traffic.
4. Dùng [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) mà không thay đổi kết quả toán học của causal attention.
5. Chỉ sau khi dense baseline hoạt động, thử thay dense MLP bằng `MoE` hoặc thay attention bằng fixed-state mechanisms.

Đây là Stage 4 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Mục tiêu không phải tái tạo một frontier model: bạn cần hiểu rõ baseline để sau này có thể chỉ ra chính xác một mechanism mới thay thế phần nào, tối ưu bottleneck nào, và đánh đổi điều gì.

## Relationships

- **Elaborates:** Stage 4 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng component-level architecture, implementation, và debugging checks.
- **Builds on:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md) cho next-token objective, shifted targets, và generation; [Attention: beginner's guide for causal language models](attention-beginner-guide.md) cho Q/K/V và causal attention.
- **Synthesizes:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md), [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), và [OpenAI GPT PyTorch reference implementation](openai-gpt-pytorch-reference-implementation.md) thành một dense GPT baseline.
- **Prepares for:** [KV caching](kv-caching.md), [Rotary position embedding (RoPE)](rotary-position-embedding.md), và [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md).

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially `model_architecture.tex`.
[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training” (2018), [PDF](../raw/gpt.pdf), Sections 3–4.
[^radford-gpt-2-2019]: Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), [PDF](../raw/gpt2.pdf), Section 2.1 and Table 2.
[^huggingface-openai-gpt-pytorch]: Hugging Face, “PyTorch OpenAI GPT model,” [source](../raw/gpt-source.py), `Attention`, `MLP`, `Block`, and language-model wrapper. The supplied source has no revision metadata.
