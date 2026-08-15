---
type: Synthesis
title: Architecture map and attention masks — khóa học cho người mới
description: A beginner-first course that separates sequence backbones, capacity/context mechanisms, and system architecture, then implements and verifies bidirectional, causal, padding, and cross-attention masks.
tags: [architecture, attention, attention-mask, transformer, bert, encoder-decoder, pytorch, learning-roadmap]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T00:00:00Z }
sources:
  - id: transformer-architecture-survey
    resource: ../raw/TongHopKienTrucTransformer.md
    title: "Tổng hợp kiến trúc Transformer"
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: devlin-bert-2018
    resource: ../raw/arXiv-1810.04805v2/main.tex
    title: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
---

# Architecture map and attention masks — khóa học cho người mới

Khi gặp một tên model mới, đừng vội gọi toàn bộ nó là một `architecture`. Trước hết hãy tách nó thành ba layer: **sequence backbone** trộn thông tin giữa các token như thế nào; **capacity/context mechanism** thay đổi capacity, memory, hoặc chi phí ra sao; và **system architecture** ghép model với modality, retrieval, hay tools thế nào. Với Transformer backbone, `attention mask` là rule quyết định ô nào của score matrix được phép đọc: `bidirectional self-attention` dùng mọi token hợp lệ, `causal self-attention` chặn future token, còn `cross-attention` để query của một sequence đọc key/value của sequence khác.[^transformer-architecture-survey][^vaswani-transformer-2017][^devlin-bert-2018]

> [!success] Sau bài này
> Bạn có thể (1) vẽ một architecture map không lẫn `backbone` với MoE, RAG, hoặc multimodal system; (2) đọc đúng row/column của attention matrix; (3) tự tạo `bidirectional`, `causal`, `padding`, và `cross-attention` mask; và (4) kiểm chứng bằng code rằng future-token leakage không xảy ra.

Nội dung giải thích, checklist, và code là **synthesis sư phạm**. Các facts lịch sử về original Transformer và BERT dùng nguồn primary; taxonomy ba layer được tổng hợp từ một secondary survey nên không phải bằng chứng rằng mọi model phải được phân loại theo đúng một cách.[^transformer-architecture-survey][^vaswani-transformer-2017][^devlin-bert-2018]

## 1. Bản đồ lớn: một model không chỉ có một loại kiến trúc

Hãy dùng ba câu hỏi theo thứ tự. Câu trả lời của câu trước là context cho câu sau, không phải câu trả lời thay thế.

| Layer | Câu hỏi cần hỏi | Ví dụ câu trả lời | Không nên nhầm với |
|---|---|---|---|
| `sequence backbone` | Token representations giao tiếp qua sequence bằng cơ chế nào? | full `self-attention`, recurrent/SSM state, linear attention, long convolution, hybrid | số expert, RAG, batching server |
| `capacity/context mechanism` | Capacity, token access, context state, hay compute allocation thay đổi ra sao? | MoE, MQA/GQA, KV compression, local window, sparse selection, external memory | một backbone hoàn chỉnh |
| `system architecture` | Những component nào bao quanh và compose với model? | vision encoder, retriever, tool loop, cache manager, scheduler | phép trộn token trong mỗi layer |

### 1.1 `Sequence backbone`: đường chính của information flow

`Sequence backbone` là mechanism lặp lại qua layers để biến một sequence representations thành sequence representations mới.

- **Full Transformer attention:** mỗi query token có thể so score với các key token được mask cho phép. Nó giữ token-addressable retrieval: model có thể trực tiếp lấy weighted mixture từ representation của từng token còn được giữ. Đổi lại, full attention có số score pairs tăng theo $T^2$ với sequence length $T$.[^vaswani-transformer-2017]
- **Recurrent/SSM/linear-memory backbone:** history được nén vào state cập nhật theo thời gian. Decode state có thể không tăng theo số token, nhưng state hữu hạn có thể bị interference hoặc không truy xuất chính xác từng token cũ như full attention.[^transformer-architecture-survey]
- **Hybrid backbone:** kết hợp một path state-efficient (recurrent/local) với các attention layers định kỳ để lấy lại một phần global token retrieval.[^transformer-architecture-survey]

Vì vậy, khi đọc “model has MoE”, câu hỏi còn thiếu là: **MoE được gắn lên backbone nào?** MoE thường thay dense `FFN`, chứ không tự trả lời token $i$ đọc token $j$ theo rule nào.

### 1.2 `Capacity/context mechanism`: thay một trục, không nhất thiết thay backbone

Một mechanism có thể rất quan trọng nhưng vẫn không phải `sequence backbone`:

| Thành phần | Nó thay đổi gì? | Phân loại hữu ích |
|---|---|---|
| `MoE` | chọn một vài `FFN expert` cho mỗi token, tăng total parameter capacity mà không chạy mọi expert | capacity / compute allocation |
| `MQA`, `GQA`, latent KV | giảm số hoặc kích thước K/V state cho attention | attention-state efficiency |
| local/sliding-window attention | hạn chế token positions có thể được đọc | attention access pattern |
| `RAG` | lấy documents từ external store rồi đưa text vào generator | external knowledge access |
| `KV cache` / PagedAttention | lưu và quản lý K/V của prefix khi decode | serving state management |
| adaptive depth / test-time search | phân bổ compute khác nhau theo token hoặc task | adaptive compute |

Ví dụ, một `decoder-only Transformer + GQA + MoE + RAG` vẫn có thể có **causal Transformer** là backbone. GQA thay KV-head sharing; MoE thay channel-wise computation trong FFN; RAG chọn text sẽ được đưa vào context. Không component nào trong ba cái đó tự động biến model thành encoder–decoder hoặc recurrent model.[^transformer-architecture-survey]

### 1.3 `System architecture`: component ở ngoài hoặc ở biên của backbone

`Multimodal` system thường có image/audio/video encoder, projector, và text backbone. `Agent` system thêm planning, tool calls, observations, retry policy, và persistent memory. Những component này quyết định end-to-end behavior, nhưng chúng không cho biết self-attention trong language backbone là causal hay bidirectional.[^transformer-architecture-survey]

> [!tip] Quy tắc một dòng
> Nếu bỏ component đó đi mà token-mixing layers vẫn vận hành, nó thường là mechanism hoặc system component; nếu thay nó đi làm rule truyền information theo sequence đổi căn bản, nó có khả năng là một phần của backbone.

## 2. Ba Transformer patterns cần nhận ra trước

`Attention` dùng cùng một core operation, nhưng origin của Q/K/V và `mask` tạo ra các behavior khác nhau.

| Pattern | Q đến từ | K, V đến từ | Mask chính | Use case điển hình |
|---|---|---|---|---|
| `encoder-only` / bidirectional `self-attention` | input sequence | cùng input sequence | padding mask (nếu cần), không causal | representation, classification, token labeling |
| `decoder-only` causal `self-attention` | prefix sequence | cùng prefix sequence | causal mask + padding mask (nếu batch padded) | next-token generation |
| `encoder–decoder` | decoder states | encoder outputs, ở `cross-attention` | decoder self-attention là causal; cross-attention thường chỉ mask source padding | translation, conditional generation |

### 2.1 `Encoder-only`: đọc cả left và right context

BERT là multi-layer Transformer encoder. Trong mỗi self-attention layer, token có thể attend sang token ở cả bên trái lẫn bên phải trong input sequence; BERT pre-training bằng masked-token objective thay vì next-token causal objective.[^devlin-bert-2018]

Với sequence `[CLS] tôi học AI [SEP]`, representation của `học` có thể dùng `tôi` và `AI` trong **cùng layer**. Điều này hữu ích khi output là representation của toàn sequence hoặc mỗi token, nhưng không phù hợp trực tiếp để autoregressively predict token kế tiếp khi future tokens đang hiện diện trong input.

`Bidirectional` không có nghĩa “không mask gì”. Nếu batch có padding, model vẫn phải block padded **key** positions; nếu không, padding embeddings sẽ đi vào weighted average của real tokens.

### 2.2 `Decoder-only`: chỉ đọc prefix để sinh continuation

GPT-style `decoder-only` model đặt prompt và response đã sinh thành một sequence. Tại position $i$, query chỉ được đọc key positions $j\le i$. Rule đó đảm bảo logit ở position $i$ không thấy token input ở $i+1$ trở đi, dù training tính mọi positions song song.[^vaswani-transformer-2017]

Với 4 positions, `causal mask` có dạng lower triangle:

| query \ key | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| 0 | allow | block | block | block |
| 1 | allow | allow | block | block |
| 2 | allow | allow | allow | block |
| 3 | allow | allow | allow | allow |

Row là **query position**; column là **key position**. Nhớ orientation này sẽ tránh phần lớn lỗi `tril`/`triu`.

### 2.3 `Encoder–decoder`: hai sequence, hai loại attention

Original Transformer tách source sequence và target sequence.[^vaswani-transformer-2017]

```text
source IDs → encoder → encoder memory (S positions)
                         ↑ K, V
partial target IDs → decoder causal self-attention → queries (T positions)
                         ↓
                    cross-attention → next-target logits
```

Trong decoder layer:

1. **masked self-attention:** target token chỉ đọc target prefix;
2. **cross-attention:** query từ target decoder đọc K/V của toàn bộ encoder memory;
3. **FFN:** biến đổi từng target position độc lập, sau khi attention đã trộn context.

Cross-attention score matrix có shape `(target_length, source_length)`, nên thường là **rectangular**, không phải square. Source sentence đã được encoder đọc trọn vẹn, vì vậy cross-attention không cần causal mask theo target time. Nó vẫn phải block source padding positions.

> [!note] BERT text pair không mặc định là cross-attention
> BERT có thể pack question và passage trong một input, ngăn bởi `[SEP]`, với segment embeddings A/B. Các tokens sau đó tương tác bằng một bidirectional encoder self-attention stack; không có decoder queries đọc một encoder-memory riêng như original encoder–decoder Transformer.[^devlin-bert-2018]

## 3. Attention matrix và mask: toán học tối thiểu nhưng chính xác

Với query length $T_q$, key/value length $T_k$, và head dimension $d_h$:

$$
S = \frac{QK^\top}{\sqrt{d_h}} \in \mathbb{R}^{T_q\times T_k}.
$$

- $S_{ij}$ là compatibility score của **query ở row $i$** với **key ở column $j$**.
- Mask $M$ được cộng **trước** `softmax`.
- `softmax` chạy theo key dimension (mỗi row):

$$
A_{i,:}=\operatorname{softmax}(S_{i,:}+M_{i,:}),
\qquad O=AV.
$$

Với convention additive mask:

$$
M_{ij}=\begin{cases}
0,&\text{nếu query }i\text{ được phép đọc key }j\\
-\infty,&\text{nếu bị block.}
\end{cases}
$$

Sau `softmax`, blocked entry có weight 0. Vì vậy, hãy block `scores` trước `softmax`, không phải zero weights sau `softmax` (trừ khi renormalize đúng cách).

### 3.1 Bốn mask nên phân biệt

| Mask | Shape logic | Rule | Dùng ở đâu |
|---|---|---|---|
| `bidirectional` | `(T, T)` | mọi real query đọc mọi real key | encoder self-attention |
| `causal` | `(T, T)` | row $i$ chỉ đọc columns $\le i$ | decoder self-attention |
| `key padding mask` | `(B, T_k)` rồi broadcast | block keys là padding | encoder, decoder, cross-attention |
| `cross-attention mask` | `(T_{target}, T_{source})` | thường allow mọi non-padding source key | decoder cross-attention |

`Padding mask` và `causal mask` giải quyết hai câu hỏi khác nhau:

- **causal:** “key này có ở future so với query không?”
- **padding:** “key này có phải filler để cùng batch shape không?”

Với right-padded causal batch, allowed pairs là intersection của hai điều kiện: `key_index <= query_index` **và** `key_is_real`. Thực tế cũng nên tránh tính loss trên padded target positions.

> [!warning] API convention không thống nhất
> Bài này dùng Boolean `allow=True`. Nhiều PyTorch APIs lại nhận Boolean mask với `True=block`, còn một số API nhận additive float mask. Đọc docstring, viết một toy test, và đừng đổi `~mask` theo cảm tính.

## 4. Code lab: tạo, nhìn, và test masks

Code dưới đây cố tình không dùng fused kernel để thấy rõ semantics. Nó chạy với PyTorch và dùng convention **`True = allow`**.

```python
import math
import torch
import torch.nn.functional as F


def causal_allow_mask(length: int, device=None) -> torch.Tensor:
    """(T, T): row=query, column=key; True means attention is allowed."""
    return torch.ones(length, length, dtype=torch.bool, device=device).tril()


def bidirectional_allow_mask(length: int, device=None) -> torch.Tensor:
    """(T, T): every position can read every position."""
    return torch.ones(length, length, dtype=torch.bool, device=device)


def cross_allow_mask(target_length: int, source_length: int, device=None) -> torch.Tensor:
    """(T_target, T_source): target queries can read all source keys."""
    return torch.ones(target_length, source_length, dtype=torch.bool, device=device)


def scaled_dot_product_attention(q, k, v, allow_mask=None):
    """
    q: (B, H, Tq, Dh), k/v: (B, H, Tk, Dh)
    allow_mask: broadcastable to (B, H, Tq, Tk), True means allow.
    """
    scores = (q @ k.transpose(-2, -1)) / math.sqrt(q.size(-1))
    if allow_mask is not None:
        scores = scores.masked_fill(~allow_mask, float("-inf"))
    weights = F.softmax(scores, dim=-1)
    return weights @ v, weights


# Visualize masks as 1=allow, 0=block.
print("bidirectional\n", bidirectional_allow_mask(4).int())
print("causal\n", causal_allow_mask(4).int())
print("cross (target=3, source=5)\n", cross_allow_mask(3, 5).int())
```

Expected causal output:

```text
tensor([[1, 0, 0, 0],
        [1, 1, 0, 0],
        [1, 1, 1, 0],
        [1, 1, 1, 1]], dtype=torch.int32)
```

### 4.1 Causal test: thay future, past output phải giữ nguyên

Test này tạo Q/K/V từ cùng input `x`, rồi thay đổi suffix sau `cut`. Với causal mask, outputs tại positions `<= cut` phải không đổi.

```python
@torch.no_grad()
def self_attention(x, allow_mask):
    # Pedagogical one-head identity projections: x supplies Q, K, and V.
    q = k = v = x[:, None]          # (B, 1, T, D)
    out, _ = scaled_dot_product_attention(q, k, v, allow_mask)
    return out[:, 0]                # (B, T, D)


torch.manual_seed(0)
x = torch.randn(2, 6, 8)
cut = 2
causal = causal_allow_mask(x.size(1))

changed = x.clone()
changed[:, cut + 1:] = torch.randn_like(changed[:, cut + 1:])

a = self_attention(x, causal)
b = self_attention(changed, causal)
torch.testing.assert_close(a[:, :cut + 1], b[:, :cut + 1])
print("passed: no future-token leakage")
```

Bỏ causal mask hoặc dùng upper triangle sẽ làm assertion này fail. Ngược lại, test pass không chứng minh model “hiểu language”; nó chỉ xác nhận dependency rule của layer.

### 4.2 Bidirectional contrast: future *được phép* thay đổi past output

```python
full = bidirectional_allow_mask(x.size(1))
a_full = self_attention(x, full)
b_full = self_attention(changed, full)

# Position 0 can read the changed suffix, so this is normally nonzero.
difference = (a_full[:, :cut + 1] - b_full[:, :cut + 1]).abs().max()
print("max bidirectional difference:", difference.item())
assert difference > 0
```

Đây là lý do không thể dùng unmasked BERT-style self-attention trực tiếp cho causal next-token prediction: logit ở early position sẽ nhận information từ future input.

### 4.3 Kết hợp causal mask với padding mask

Giả sử batch có `valid_lengths = [4, 2]` và right padding đến `T=4`. `key_valid` có shape `(B, T)`; thêm dimensions để broadcast sang heads và query rows.

```python
def causal_with_key_padding(valid_lengths: torch.Tensor, max_len: int) -> torch.Tensor:
    # Result: (B, 1, T_query, T_key), True = allowed.
    positions = torch.arange(max_len, device=valid_lengths.device)
    key_valid = positions[None, :] < valid_lengths[:, None]  # (B, T)
    causal = causal_allow_mask(max_len, valid_lengths.device)  # (T, T)
    return causal[None, None] & key_valid[:, None, None, :]

mask = causal_with_key_padding(torch.tensor([4, 2]), max_len=4)
print(mask[0, 0].int())  # regular causal mask
print(mask[1, 0].int())  # columns 2 and 3 are blocked as padding keys
```

Với sample dài 2, output ở padded **query** rows có thể không có semantic value. Cách đơn giản là exclude padded positions khỏi loss và downstream use. Một production implementation có thể compact/unpad sequences để không tốn compute cho chúng; đó là optimization, không đổi rule mask.

### 4.4 `Cross-attention` là rectangular matrix

```python
B, H, T_target, T_source, Dh = 2, 3, 4, 6, 8
q = torch.randn(B, H, T_target, Dh)  # from decoder states
k = torch.randn(B, H, T_source, Dh)  # from encoder outputs
v = torch.randn(B, H, T_source, Dh)

# No causal relation between target index and source index.
source_is_real = torch.tensor([
    [1, 1, 1, 1, 1, 1],  # six real source tokens
    [1, 1, 1, 1, 0, 0],  # two padded source positions
], dtype=torch.bool)
cross = cross_allow_mask(T_target, T_source)[None, None]
cross = cross & source_is_real[:, None, None, :]

out, weights = scaled_dot_product_attention(q, k, v, cross)
assert out.shape == (B, H, T_target, Dh)
assert torch.all(weights[1, :, :, 4:] == 0)  # padded source keys get zero weight
```

Đừng dùng `torch.tril(T_target, T_source)` mặc định cho cross-attention. Nó sẽ vô tình cấm target query 0 đọc nhiều source tokens chỉ vì hai sequences có index numbers, dù source đã có đầy đủ từ encoder.

## 5. Cách vẽ architecture map cho một model bất kỳ

Dùng template này trước khi đọc bảng benchmark hoặc claims marketing:

```text
Input / modality boundary:
  text tokens? image/audio encoder? external documents? tool observations?

Sequence backbone:
  full attention / causal attention / encoder-decoder / SSM / linear memory / hybrid?
  which sequence positions can directly interact?

Capacity and context mechanisms:
  dense FFN or MoE? KV layout? window/sparse access? external memory?

Training objective and interface:
  masked token, next token, sequence-to-sequence, contrastive, ...?

Serving system:
  KV cache? batching? retrieval timing? tool loop? cache sharing?
```

### Worked classification examples

| Description | Phân loại đúng hơn | Lý do |
|---|---|---|
| BERT encoder + `[CLS]` classifier | bidirectional Transformer encoder backbone + task head | all input tokens contextualize each other; classifier đọc final `[CLS]` state |
| GPT-style chat model | causal decoder-only Transformer backbone + serialized chat interface | prompt và generated response ở một causal sequence; không có mandatory cross-attention |
| translation Transformer | encoder–decoder backbone | encoder self-attention, decoder causal self-attention, và decoder-to-encoder cross-attention đều là core layers |
| causal Transformer whose FFN is top-k MoE | causal Transformer backbone + sparse-capacity mechanism | routing changes FFN execution, not causal token-access rule |
| RAG app using a decoder-only model | decoder-only backbone + external retrieval system | retriever selects documents; generator still processes supplied tokens causally |
| vision encoder projected into text tokens then fed to LLM | multimodal system with a text backbone | need separately describe vision encoder, projector, and text sequence mixer |

Một model thật có thể chứa nhiều rows cùng lúc. Mục tiêu không phải ép nó vào một label duy nhất mà là chỉ ra **component nào thực hiện nhiệm vụ nào**.

## 6. Debug checklist: mask sai thường trông như thế nào?

| Symptom | Nguyên nhân thường gặp | Test/fix đầu tiên |
|---|---|---|
| training loss giảm bất thường nhưng generation kém | future-token leakage | perturb suffix; kiểm tra lower triangle và target shift |
| attention row có `NaN` | toàn bộ keys trong row bị block | bảo đảm ít nhất một valid key cho mỗi real query; thường causal diagonal được allow |
| padded sample cho output lạ | chỉ mask queries, không block padded keys; hoặc loss tính cả padding | mask padded key columns; use loss ignore index/mask |
| cross-attention không dùng hết source | vô tình dùng causal square/triangular mask | in shape `(T_target, T_source)` và test all real source columns are allowed |
| output khác nhau giữa run dù test causality đúng | dropout hoặc train mode | `model.eval()` trước deterministic comparison |
| mask code chạy nhưng inverted semantics | `True=allow`/`True=block` bị đảo giữa APIs | in tiny 3×3 mask và check forbidden weights exactly 0 |

> [!warning] Không suy luận quá mức từ attention weights
> Weight bằng 0 ở blocked position chứng minh mask applied theo expectation. Weight lớn ở allowed position không tự chứng minh một linguistic explanation hay causal explanation cho output; attention là một component trong residual, multi-layer computation.

## 7. Bài tập tự kiểm chứng

1. **Vẽ mask.** Với `T=5`, tự viết causal matrix và chỉ rõ row/column của score $S_{3,1}$.
2. **Thêm padding.** Với lengths `[5, 3]`, in mask `(B, 1, 5, 5)` và xác nhận sample thứ hai block key columns 3–4.
3. **Break rồi repair.** Đổi `.tril()` thành `.triu()`; chạy causal test, quan sát failure, rồi sửa lại.
4. **Cross-attention shape.** Tạo `T_target=2`, `T_source=7`; giải thích vì sao mask không phải 2×2 hay 7×7.
5. **Classify a paper.** Chọn một model trong wiki và điền template ở section 5. Với mỗi claim, đánh dấu `backbone`, `mechanism`, hoặc `system`.

Bạn sẵn sàng đi tiếp khi có thể giải thích bằng một câu: **mask không tạo knowledge cho model; nó giới hạn information paths mà attention được phép dùng.**

## 8. Đường học tiếp

- [Attention: beginner's guide for causal language models](attention-beginner-guide.md) đi sâu Q/K/V, multi-head shapes, causal attention, và full minimal layer.
- [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) mô tả original encoder–decoder Transformer, residual paths, FFN, và positional encoding.
- [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md) nối bidirectional encoder với pre-training và downstream fine-tuning.
- [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) ghép causal attention thành minimal GPT.
- [Sequence-model architecture taxonomy](sequence-model-architecture-taxonomy.md) mở rộng architecture map sang recurrent/SSM, linear memory, hybrid, MoE, RAG, và agents; note này có evidence limit của secondary survey.

Bài này triển khai Stage 1.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Hãy hoàn thành mask tests trước khi đổi backbone hoặc thêm mechanisms như MoE và RAG.

## Relationships

- **Elaborates:** Stage 1.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng architecture map, mask theory, PyTorch lab, và verification checklist.
- **Synthesizes:** [Sequence-model architecture taxonomy](sequence-model-architecture-taxonomy.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), và [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md).
- **Builds on:** [Attention: beginner's guide for causal language models](attention-beginner-guide.md) cho scaled dot-product attention và multi-head mechanics.
- **Prepares for:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) và [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md).

[^transformer-architecture-survey]: “Tổng hợp kiến trúc Transformer,” [raw source](../raw/TongHopKienTrucTransformer.md). Secondary survey; model-specific attributions were not independently verified by this course.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially the architecture and scaled-attention sections.
[^devlin-bert-2018]: Devlin et al., “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,” [LaTeX source](../raw/arXiv-1810.04805v2/main.tex), especially input representation, model architecture, and fine-tuning sections.
