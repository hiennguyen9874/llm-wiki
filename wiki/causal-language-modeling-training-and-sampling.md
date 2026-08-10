---
type: Synthesis
title: Causal language modeling: training and sampling
description: A beginner-first guide to next-token likelihood, teacher forcing, causal masking, training, debugging, and temperature/top-k/top-p decoding for an autoregressive language model.
tags: [causal-language-modeling, autoregressive-generation, teacher-forcing, causal-masking, sampling, pytorch]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T22:57:43+07:00 }
sources:
  - id: radford-generative-pre-training-2018
    resource: ../raw/gpt.pdf
    title: Improving Language Understanding by Generative Pre-Training
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: huggingface-openai-gpt-pytorch
    resource: ../raw/gpt-source.py
    title: PyTorch OpenAI GPT model
---

# Causal language modeling: training and sampling

**Causal language modeling (CLM)** dạy model trả lời một câu hỏi lặp lại: *với mọi token đã có ở bên trái, token nào có khả năng xuất hiện tiếp theo?* Model học câu hỏi này trong **training** bằng `teacher forcing`, và tự trả lời nó từng bước trong **generation**. Hai điều dễ nhầm nhất là: `target` luôn lệch một token so với `input`, và `causal mask` phải chặn mọi đường để một vị trí nhìn thấy token tương lai.

```text
training text → token IDs → shifted input/target → causal Transformer
              → logits → cross-entropy loss → backward → optimizer

prompt → logits của vị trí cuối → decoding policy → token mới → prompt mới → ...
```

GPT là một ví dụ `decoder-only Transformer` được pre-train bằng next-token likelihood trên văn bản liên tục.[^radford-generative-pre-training-2018]

> [!success] Sau bài này
> Bạn có thể tạo batch CLM đúng, giải thích `teacher forcing` mà không nhầm nó với leakage, kiểm tra `causal mask` theo hành vi, huấn luyện một `TinyCausalLM`, và chọn giữa `greedy decoding`, `temperature`, `top-k`, và `top-p`.

Các công thức, code, và quy trình debug là **synthesis mang tính sư phạm**. Chúng minh họa objective và architecture trong các nguồn dẫn, không phải recipe tái tạo kết quả training của GPT.

## 1. Bắt đầu từ một ví dụ

Giả sử tokenizer đã biến câu sau thành token:

```text
<BOS> Hôm nay trời đẹp <EOS>
```

Một CLM học các dự đoán:

| Context đã biết | Next token đúng |
|---|---|
| `<BOS>` | `Hôm` |
| `<BOS> Hôm` | `nay` |
| `<BOS> Hôm nay` | `trời` |
| `<BOS> Hôm nay trời` | `đẹp` |
| `<BOS> Hôm nay trời đẹp` | `<EOS>` |

Khi người dùng đưa prompt `<BOS> Hôm nay`, model không "lấy" token `trời` từ dữ liệu. Nó xuất ra một **distribution** trên toàn bộ vocabulary; `trời` chỉ là một ứng viên có thể có probability cao. Sau khi chọn một token, token đó trở thành một phần context cho bước kế tiếp.

Từ **causal** nghĩa là thông tin chỉ đi từ quá khứ sang hiện tại: dự đoán tại vị trí $t$ được điều kiện hóa trên $x_{\le t}$, không được dùng $x_{>t}$. Đây là lý do CLM có thể generate từ trái sang phải.

## 2. Objective: xác suất của cả sequence

Gọi token IDs của một sequence là

$$
x_{1:T}=(x_1,x_2,\ldots,x_T), \qquad x_t\in\{0,\ldots,V-1\},
$$

trong đó $V$ là `vocab_size`. Chain rule phân rã probability của toàn sequence:

$$
p_\theta(x_{1:T}) = p_\theta(x_1)\prod_{t=1}^{T-1}
p_\theta(x_{t+1}\mid x_{\leq t}).
$$

Trong code, token đầu tiên thường được cho bởi `BOS` hoặc prompt. Vì vậy, điều model trực tiếp học trên phần còn lại là:

$$
\log p_\theta(x_{2:T}\mid x_1)
=\sum_{t=1}^{T-1}\log p_\theta(x_{t+1}\mid x_{\leq t}).
$$

Tại mỗi vị trí, model trả về một vector **logits** $z_t\in\mathbb{R}^V$: một score chưa chuẩn hóa cho từng token ID. `softmax` biến scores thành probabilities:

$$
p_\theta(j\mid x_{\leq t})=
\frac{\exp(z_{t,j})}{\sum_{v=1}^{V}\exp(z_{t,v})}.
$$

Loss dùng trong training là **negative log-likelihood (NLL)** trung bình, hay `cross-entropy` theo token:

$$
\mathcal L=-\frac1N\sum_{(b,t)\in\mathcal I}
\log p_\theta(y_{b,t}\mid x_{b,\leq t}).
$$

$\mathcal I$ là tập các target hợp lệ và $N$ là số phần tử của tập đó. Tối thiểu hóa loss tương đương tối đa hóa probability model gán cho dữ liệu đúng. GPT được mô tả với objective tối đa hóa likelihood của mỗi token khi condition trên các token trước nó.[^radford-generative-pre-training-2018]

### Shapes cần kiểm tra trước tiên

Với `batch_size = B`, `sequence_length = L`, và `vocab_size = V`:

| Tensor | Shape | Ý nghĩa |
|---|---:|---|
| `input_ids` | `(B, L)` | token model được đọc |
| `targets` / `labels` | `(B, L)` | next token đúng tại mỗi vị trí |
| `logits` | `(B, L, V)` | score của mọi next-token candidate |
| `loss` | `()` | NLL trung bình trên target hợp lệ |

Trong PyTorch, `F.cross_entropy` nhận **raw logits**, không nhận probabilities. Vì vocabulary là chiều cuối, cách thông dụng là:

```python
loss = F.cross_entropy(logits.flatten(0, 1), targets.flatten())
# logits: (B * L, V), targets: (B * L,)
```

Không gọi `softmax` trước `F.cross_entropy`: hàm này tự thực hiện `log_softmax` theo cách ổn định số.

> [!note] Perplexity
> `perplexity = exp(loss)` thường được báo cáo cho language model. Nó chỉ so sánh được khi tokenizer, tập evaluation, quy tắc padding, và cách tính loss là tương đương. Một `perplexity` thấp hơn với tokenizer khác không tự động có nghĩa model tốt hơn.

## 3. `teacher forcing`: target shift và parallel training

Từ một token sequence dài $L+1$:

```text
IDs:     [BOS, Hôm, nay, trời, đẹp, EOS]
input:   [BOS, Hôm, nay, trời, đẹp]
target:  [Hôm, nay, trời, đẹp, EOS]
```

`input` và `target` là cùng stream nhưng **shift trái một vị trí**. Model ở `input[t]` phải dự đoán `target[t]`, tức token kế tiếp.

```python
x = ids[start : start + block_size]
y = ids[start + 1 : start + block_size + 1]
assert torch.equal(x[1:], y[:-1])
```

Trong `teacher forcing`, model luôn nhận prefix đúng từ training data, thay vì token mà chính nó vừa dự đoán. Nhờ đó, tất cả vị trí trong block có thể được tính trong một `forward pass` song song:

```text
position 0 đọc: [BOS]                 → đoán Hôm
position 1 đọc: [BOS, Hôm]            → đoán nay
position 2 đọc: [BOS, Hôm, nay]       → đoán trời
...
```

Điều này **không phải** là tiết lộ đáp án, miễn `causal mask` được áp dụng đúng. Ở position 1, token `nay` có mặt trong `target`, nhưng không nằm trong context mà hidden state tại position 1 được phép attention tới. Transformer decoder dùng input được shift và masked self-attention chính vì mục đích này.[^vaswani-transformer-2017]

### `training` và `generation` khác nhau ở đâu?

| Chế độ | Prefix tại một bước | Mục đích |
|---|---|---|
| `training` | gold tokens từ dataset | tính loss hiệu quả trên mọi position |
| `generation` | prompt + tokens model đã chọn | tạo sequence mới, từng token một |

Cả hai cùng định nghĩa distribution $p_\theta(x_{t+1}\mid x_{\leq t})$. `teacher forcing` chỉ là cách tính objective hiệu quả, không thay objective bằng một bài toán khác.

Trong generation, một token sai có thể đi vào context của các bước sau; trong training, prefix thường đúng. Khác biệt này thường được gọi là `exposure bias` hoặc `train–inference mismatch`. Đây là rủi ro thực tế, nhưng không phải lời giải thích duy nhất cho output kém: data, model capacity, prompt, và decoding policy đều quan trọng.

### Padding và document boundary

- Nếu cắt fixed-length block từ một token stream liên tục, thường không cần padding.
- Nếu batch có `PAD`, đặt `labels` ở padding thành `ignore_index` (thường là `-100`) để không tính loss **và** dùng `padding mask` để attention không đọc padding.
- `causal mask` và `padding mask` giải quyết hai vấn đề khác nhau: mask thứ nhất chặn future tokens; mask thứ hai chặn filler tokens.
- Đừng ghép hai document độc lập nếu không đặt `EOS` hoặc boundary token, trừ khi bạn thật sự muốn model học rằng cuối document thứ nhất nối với đầu document thứ hai.

## 4. `causal mask`: quy tắc cấm nhìn tương lai

Trong self-attention, mỗi position tạo `query` ($Q$), `key` ($K$), và `value` ($V$). Scores trước `softmax` là:

$$
S=\frac{QK^\top}{\sqrt{d_k}}.
$$

Causal attention cộng mask $M$ vào scores trước `softmax`:

$$
M_{ij}=\begin{cases}
0,&j\leq i\\
-\infty,&j>i,
\end{cases}
\qquad
A=\operatorname{softmax}(S+M).
$$

Hàng $i$ là `query position`; cột $j$ là `key position`. Vì $\exp(-\infty)=0$, position $i$ chỉ attention tới position $j\leq i$.

| query \ key | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| 0 | allow | block | block | block |
| 1 | allow | allow | block | block |
| 2 | allow | allow | allow | block |
| 3 | allow | allow | allow | allow |

Masked self-attention cho phép xử lý toàn bộ block song song ở training, nhưng vẫn bảo toàn rule "chỉ dùng left context". Transformer mô tả decoder self-attention mask các output position ở phía sau; scaled dot-product attention áp dụng mask trước softmax.[^vaswani-transformer-2017] Reference implementation OpenAI GPT trong kho cũng áp dụng lower-triangular causal mask vào attention scores trước softmax.[^huggingface-openai-gpt-pytorch]

> [!warning] Đừng đoán Boolean-mask convention
> Có API dùng `True` là **block**, API khác dùng `True` là **allow**. Hãy đọc documentation của layer đang dùng. Trong ví dụ `nn.TransformerEncoder` bên dưới, `True` trong `mask` nghĩa là vị trí attention bị chặn.

### Test causality theo hành vi

Nhìn mask tam giác chưa đủ. Một lỗi về chiều, broadcasting, hoặc convention vẫn có thể làm future token leak vào logits. Test sau thay các token **sau** `cut`; logits đến `cut` phải giữ nguyên khi model ở `eval()`:

```python
@torch.no_grad()
def assert_causal(model, ids, cut):
    """ids has shape (B, T); 0 <= cut < T - 1."""
    model.eval()
    changed = ids.clone()
    changed[:, cut + 1:] = torch.randint(
        0, model.vocab_size, changed[:, cut + 1:].shape, device=ids.device
    )
    before = model(ids)[:, :cut + 1]
    after = model(changed)[:, :cut + 1]
    torch.testing.assert_close(before, after, rtol=1e-5, atol=1e-6)
```

Test này không chứng minh model hiểu ngôn ngữ. Nó trực tiếp kiểm tra property cấu trúc quan trọng nhất: future input không được thay đổi past logits. Nếu test fail, kiểm tra mask orientation, `dropout`, position indexing, và bất kỳ operation nào trộn tokens qua thời gian.

## 5. Một `TinyCausalLM` để kiểm tra toàn pipeline

Mục tiêu code này là một model nhỏ, dễ đọc và đủ đúng về semantics. `nn.TransformerEncoder` chỉ là tên API: khi truyền causal mask, nó hoạt động như một stack causal self-attention; nó không có cross-attention với encoder khác.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class TinyCausalLM(nn.Module):
    def __init__(self, vocab_size, max_seq_len, d_model=192,
                 n_heads=6, n_layers=4, dropout=0.1):
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")

        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_seq_len, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.blocks = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

        # Optional weight tying: input embedding và output head dùng cùng weights.
        self.lm_head.weight = self.token_emb.weight

    def forward(self, input_ids):
        B, T = input_ids.shape
        if T > self.max_seq_len:
            raise ValueError(f"sequence length {T} exceeds {self.max_seq_len}")

        positions = torch.arange(T, device=input_ids.device)
        hidden = self.token_emb(input_ids) + self.pos_emb(positions)[None, :, :]

        # Với TransformerEncoder, True = position bị block.
        causal_mask = torch.triu(
            torch.ones(T, T, dtype=torch.bool, device=input_ids.device), diagonal=1
        )
        hidden = self.blocks(hidden, mask=causal_mask)
        return self.lm_head(self.ln_f(hidden))  # (B, T, V)
```

Ba phần cần nhớ:

1. `token_emb` biến mỗi token ID thành vector `d_model` chiều.
2. `pos_emb` cho model biết thứ tự; chỉ token embedding thì hai token giống nhau ở hai vị trí khác nhau ban đầu không phân biệt được vị trí.
3. Các `blocks` trộn left context nhờ causal self-attention, rồi `lm_head` chiếu hidden state thành $V$ logits.

`weight tying` là optional. Nó giảm parameter và buộc input/output token representations dùng cùng một weight matrix, nhưng không phải điều kiện để CLM hoạt động.

## 6. Data batch, training loop, và validation

Giả sử `train_ids` và `val_ids` là `torch.LongTensor` một chiều do tokenizer tạo ra. Hãy split theo document hoặc đoạn lớn **trước** khi tạo các window overlap; nếu split sau đó, validation có thể gần như sao chép training data.

```python
def next_token_batch(ids, batch_size, block_size, device):
    # Cần block_size input tokens và block_size targets lệch một token.
    if len(ids) <= block_size:
        raise ValueError("ids must contain more than block_size tokens")
    starts = torch.randint(0, len(ids) - block_size, (batch_size,))
    x = torch.stack([ids[i : i + block_size] for i in starts])
    y = torch.stack([ids[i + 1 : i + block_size + 1] for i in starts])
    return x.to(device), y.to(device)


@torch.inference_mode()
def estimate_loss(model, ids, *, batch_size, block_size, device, batches=20):
    was_training = model.training
    model.eval()
    losses = []
    for _ in range(batches):
        x, y = next_token_batch(ids, batch_size, block_size, device)
        logits = model(x)
        losses.append(F.cross_entropy(logits.flatten(0, 1), y.flatten()).item())
    model.train(was_training)
    return sum(losses) / len(losses)


device = "cuda" if torch.cuda.is_available() else "cpu"
block_size, batch_size = 128, 32
model = TinyCausalLM(vocab_size, max_seq_len=block_size).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)

for step in range(2_000):
    model.train()
    x, y = next_token_batch(train_ids, batch_size, block_size, device)
    logits = model(x)
    loss = F.cross_entropy(logits.flatten(0, 1), y.flatten())

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()

    if step % 100 == 0:
        val_loss = estimate_loss(
            model, val_ids, batch_size=batch_size,
            block_size=block_size, device=device
        )
        print(f"step={step:4d} train={loss.item():.3f} "
              f"val={val_loss:.3f} ppl={math.exp(val_loss):.1f} "
              f"grad_norm={grad_norm:.2f}")
```

Mỗi iteration có thứ tự bắt buộc:

1. `forward`: tạo logits.
2. `cross_entropy`: so logits với shifted targets.
3. `zero_grad`: xóa gradients của iteration trước.
4. `backward`: tính gradients bằng chain rule.
5. `optimizer.step`: cập nhật parameters.

PyTorch tích lũy gradients vào `.grad`, nên bỏ `zero_grad()` sẽ thay đổi training ngoài ý muốn. `eval()` tắt `dropout`; `torch.inference_mode()` không giữ activation graph, nên phù hợp cho validation và generation. `gradient clipping` chỉ giới hạn một update có gradient norm bất thường; nó không thể sửa target shift hay causal mask bị sai.

## 7. Generation: autoregressive loop

Sau một prompt, chỉ logits tại final position quyết định next token:

1. Chạy model trên current context.
2. Lấy `logits[:, -1, :]`.
3. Áp dụng decoding policy.
4. Chọn một `next_id`, append nó vào sequence.
5. Lặp lại đến khi đủ token hoặc gặp `EOS`.

```text
prompt:       [BOS, Hôm, nay]
model:        distribution cho token tiếp theo
choose:       trời
new context:  [BOS, Hôm, nay, trời]
```

Code dưới đây hỗ trợ `greedy`, `temperature`, `top-k`, `top-p`, và `EOS`. Nó không dùng `KV cache`, nên mỗi step chạy lại toàn bộ context window: semantics đúng nhưng chậm. [KV caching](kv-caching.md) giữ key/value của prefix để decode không phải tính lại chúng.

```python
@torch.inference_mode()
def generate(model, prompt_ids, *, max_new_tokens, temperature=1.0,
             top_k=None, top_p=None, do_sample=True, eos_id=None):
    """prompt_ids: LongTensor (B, T_prompt); return prompt + generated IDs."""
    if prompt_ids.ndim != 2 or prompt_ids.size(1) == 0:
        raise ValueError("prompt_ids must have non-empty shape (B, T)")
    if temperature <= 0:
        raise ValueError("temperature must be > 0; use do_sample=False for greedy")
    if top_k is not None and top_k <= 0:
        raise ValueError("top_k must be positive or None")
    if top_p is not None and not 0 < top_p <= 1:
        raise ValueError("top_p must lie in (0, 1]")

    model.eval()
    ids = prompt_ids
    finished = torch.zeros(ids.size(0), dtype=torch.bool, device=ids.device)

    for _ in range(max_new_tokens):
        context = ids[:, -model.max_seq_len:]
        filtered = model(context)[:, -1, :] / temperature  # (B, V)

        if top_k is not None:
            k = min(top_k, filtered.size(-1))
            cutoff = torch.topk(filtered, k, dim=-1).values[:, [-1]]
            filtered = filtered.masked_fill(filtered < cutoff, float("-inf"))

        if top_p is not None and top_p < 1.0:
            sorted_logits, sorted_indices = torch.sort(filtered, descending=True, dim=-1)
            sorted_probs = torch.softmax(sorted_logits, dim=-1)
            remove_sorted = torch.cumsum(sorted_probs, dim=-1) > top_p
            # Giữ token đầu tiên làm cumulative probability đạt/vượt top_p.
            remove_sorted[:, 1:] = remove_sorted[:, :-1].clone()
            remove_sorted[:, 0] = False
            remove = torch.zeros_like(remove_sorted).scatter_(1, sorted_indices, remove_sorted)
            filtered = filtered.masked_fill(remove, float("-inf"))

        if do_sample:
            next_id = torch.multinomial(torch.softmax(filtered, dim=-1), num_samples=1)
        else:
            next_id = torch.argmax(filtered, dim=-1, keepdim=True)

        if eos_id is not None:
            # Hàng đã kết thúc tiếp tục nhận EOS để batch giữ shape thống nhất.
            next_id = torch.where(finished[:, None], torch.full_like(next_id, eos_id), next_id)
            finished |= next_id.squeeze(1).eq(eos_id)

        ids = torch.cat((ids, next_id), dim=1)
        if eos_id is not None and finished.all():
            break
    return ids
```

Ví dụ, sau khi encode prompt:

```python
torch.manual_seed(7)  # tái lập một sampling run trong cùng môi trường
out = generate(model, prompt_ids, max_new_tokens=100,
               temperature=0.8, top_k=50, top_p=0.95,
               do_sample=True, eos_id=eos_id)
print(tokenizer.decode(out[0].tolist()))
```

## 8. Decoding policy thay đổi cách chọn, không thay kiến thức của model

### `greedy decoding`

Chọn token có logit lớn nhất:

$$
x_{t+1}=\operatorname{argmax}_j z_{t,j}.
$$

Nó deterministic với cùng model, prompt, và numeric environment, nên rất hữu ích khi debug. Nhược điểm là dễ rơi vào loop lặp lại.

### `temperature`

Với $\tau>0$:

$$
p_\tau(j)=\operatorname{softmax}(z_j/\tau).
$$

- `temperature = 1`: dùng distribution gốc.
- `0 < temperature < 1`: distribution sắc hơn, sampling tập trung hơn.
- `temperature > 1`: distribution phẳng hơn, đa dạng hơn nhưng dễ chọn low-probability token.

`temperature` giữ nguyên thứ tự logits nhưng thay đổi khoảng cách probability. Áp dụng nó **trước** `softmax` và trước filter dựa trên probability như `top-p`. Đừng dùng `temperature = 0` cho greedy: đó là chia cho 0; dùng `do_sample=False`.

### `top-k`

Giữ $k$ logits lớn nhất, đặt phần còn lại thành $-\infty$, rồi sample từ distribution đã chuẩn hóa lại. `top_k=1` kết hợp sampling tương đương chọn greedy. `top-k` giữ số candidate cố định, bất kể model đang chắc hay không chắc.

### `top-p` / `nucleus sampling`

Sắp tokens theo probability giảm dần, rồi giữ tập nhỏ nhất có cumulative probability ít nhất $p$.

- Distribution sắc: có thể chỉ giữ vài tokens.
- Distribution phẳng: có thể giữ nhiều tokens.

`top-p=0.9` **không** có nghĩa chỉ giữ từng token có probability lớn hơn 0.9. Nó nói về tổng probability của một tập tokens. Có thể phối hợp `top-k` và `top-p`: `top-k` đặt trần số candidate, sau đó `top-p` bỏ tail trong tập còn lại.

> [!warning] Sampling không sửa model
> `temperature`, `top-k`, và `top-p` chỉ chọn từ conditional distribution model đã học. Filter quá chặt có thể gây repetition hoặc bỏ mất token cần thiết; temperature cao với filter rộng có thể làm output hỗn loạn. Hãy log cấu hình decode khi đánh giá output.

## 9. Debug theo thứ tự rẻ nhất

| Check | Cách làm | Kết quả mong đợi | Khi fail, kiểm tra trước |
|---|---|---|---|
| Token IDs | `0 <= ids < V` | tất cả hợp lệ | tokenizer và vocabulary/checkpoint |
| Shift | `torch.equal(x[:, 1:], y[:, :-1])` | `True` | slicing, `EOS`, block boundary |
| Shapes | in shape | `(B,L)`, `(B,L,V)`, `(B,L)` | `batch_first`, vocabulary axis |
| Uniform baseline | logits toàn 0 | loss gần `log(V)` | targets, loss reduction |
| Tiny overfit | train 1–4 batch rất lâu | train loss giảm mạnh | target shift, learning rate, update loop |
| Causality | `assert_causal` | past logits không đổi | mask direction/convention, dropout |
| Validation | `eval()` trên data chưa thấy | không backward/update | split trước windowing |
| Greedy generation | `do_sample=False` | output lặp lại | context crop, `EOS`, decode |

`loss` thấp không đủ để kết luận pipeline đúng. Nếu future token leak qua mask, model có thể "chép" target và có loss rất thấp. Nếu train/validation windows overlap quá nhiều, validation loss có thể lạc quan giả tạo. Vì vậy `tiny overfit` và `assert_causal` là hai test nên chạy trước khi tăng corpus hay model size.

## 10. Những nhầm lẫn thường gặp

1. **"Chỉ cần causal mask khi generate."** Sai. Training có toàn bộ sequence; không mask thì model đọc future token và objective không còn là next-token prediction.
2. **"Teacher forcing nghĩa là input bằng target."** Sai. Target phải shift một token. Input và target cùng vị trí sẽ biến bài toán thành copy token.
3. **"Softmax trước rồi truyền vào `cross_entropy`."** Sai với PyTorch chuẩn: truyền logits thô cho `F.cross_entropy`.
4. **"Causal mask thay padding mask."** Sai. Một cái chặn future positions, cái kia chặn padding positions; padded batch thường cần cả hai.
5. **"Top-p giữ token có probability lớn hơn p."** Sai. Nó giữ một cumulative-probability set.
6. **"Temperature thấp làm model biết nhiều hơn."** Sai. Nó chỉ làm sampling tập trung vào logits đã có.
7. **"Seed làm mọi run giống hệt nhau ở mọi máy."** Không chắc. Nó giúp tái lập trong một environment xác định, nhưng kernels, device, precision, PyTorch version, và RNG state khác có thể đổi kết quả.

## 11. Ranh giới của ví dụ và bước tiếp theo

`TinyCausalLM` không bao gồm data curation, distributed training, mixed precision, learning-rate schedule, checkpointing, safety, hoặc task-level evaluation. Full self-attention còn có cost tăng theo bình phương sequence length trong training. Generation không có cache còn lặp lại computation của prefix; [KV caching](kv-caching.md) giải quyết redundancy đó bằng cách lưu attention keys/values, đổi compute lấy memory.

Bài này là Stage 2 trong [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Nó giữ tokenizer, logits, `cross-entropy`, optimizer, và sampling interface từ [Foundations for training a bigram language model](foundations-for-training-a-bigram-language-model.md); sau đó bạn nên học [scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) để hiểu bên trong attention block, và [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md) để đặt objective này vào GPT.

## Relationships

- **Elaborates:** Stage 2 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng objective, implementation, debugging checks, và decoding policy.
- **Builds on:** [Foundations for training a bigram language model](foundations-for-training-a-bigram-language-model.md), giữ next-token targets, logits, `cross-entropy`, optimizer, và basic sampling.
- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md)'s pre-softmax causal mask.
- **Operationalizes:** [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md)'s causal next-token objective trong một implementation nhỏ.
- **Prepares for:** [KV caching](kv-caching.md), nơi autoregressive generation lưu attention state của prefix.

[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training” (2018), [PDF](../raw/gpt.pdf), Sections 3–4.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), `model_architecture.tex`.
[^huggingface-openai-gpt-pytorch]: Hugging Face, “PyTorch OpenAI GPT model,” [source](../raw/gpt-source.py), attention implementation. The supplied source has no revision metadata.
