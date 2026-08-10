---
type: Synthesis
title: Causal language modeling: training and sampling
description: A practical guide to next-token likelihood, teacher forcing, causal masking, and temperature/top-k/top-p decoding for a small autoregressive language model.
tags: [causal-language-modeling, autoregressive-generation, teacher-forcing, causal-masking, sampling, pytorch]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T15:10:13Z }
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

Causal language modeling (CLM) học phân phối của chuỗi bằng cách dự đoán **token kế tiếp từ tiền tố bên trái**. Khi huấn luyện, teacher forcing đưa cho mô hình tiền tố đúng để toàn bộ vị trí của một đoạn có thể tính song song; causal mask bảo đảm mỗi vị trí không thấy token tương lai. Khi sinh, mô hình phải tự dùng các token vừa sinh làm tiền tố mới, rồi chọn token tiếp theo từ logits bằng greedy decoding hoặc sampling có temperature, top-k và top-p. GPT là một ví dụ decoder-only được pre-train bằng mục tiêu này trên văn bản liên tục.[^radford-generative-pre-training-2018]

> [!success] Kết quả học tập
> Bạn có thể (1) tạo đúng cặp input–target lệch một token, (2) giải thích vì sao teacher forcing vẫn tương thích với mô hình tự hồi quy, (3) kiểm thử causal mask, và (4) huấn luyện/sinh văn bản bằng vòng lặp PyTorch nhỏ bên dưới.

Các công thức triển khai, quy tắc lấy mẫu và quy trình chẩn đoán trong bài là **tổng hợp sư phạm** dựa trên các nguồn kiến trúc được dẫn; chúng không phải là một cấu hình huấn luyện được đo đạc của GPT.

## 1. Mô hình hóa chuỗi bằng phân phối có điều kiện

Gọi chuỗi token đã gồm token bắt đầu (nếu tokenizer dùng nó) là

$$
x_{1:T}=(x_1,x_2,\ldots,x_T), \qquad x_t\in\{0,\ldots,V-1\},
$$

với $V$ là kích thước từ vựng. Quy tắc chuỗi phân rã xác suất cả dãy thành các xác suất kế tiếp:

$$
p_\theta(x_{1:T}) = p_\theta(x_1)\prod_{t=1}^{T-1}p_\theta(x_{t+1}\mid x_{\leq t}).
$$

Trong thực tế, token đầu tiên thường được điều kiện hóa trên một token BOS hoặc prompt; phần cần tối ưu trên một đoạn thường là

$$
\log p_\theta(x_{2:T}\mid x_1)=
\sum_{t=1}^{T-1}\log p_\theta(x_{t+1}\mid x_{\leq t}).
$$

Mô hình trả về logits $z_t\in\mathbb R^V$ tại vị trí $t$. Softmax biến chúng thành phân phối token kế tiếp:

$$
p_\theta(j\mid x_{\leq t})=
\frac{\exp(z_{t,j})}{\sum_{v=1}^{V}\exp(z_{t,v})}.
$$

Do đó negative log-likelihood (NLL) trung bình, hay cross-entropy token-level, là

$$
\mathcal L=-\frac{1}{N}\sum_{(b,t)\in\mathcal I}
\log p_\theta\bigl(y_{b,t}\mid x_{b,\leq t}\bigr),
$$

trong đó $\mathcal I$ chỉ gồm $N$ vị trí target hợp lệ. Tối thiểu hóa $\mathcal L$ tương đương tối đa hóa next-token likelihood. Perplexity thường được báo cáo là $\exp(\mathcal L)$; nó chỉ có ý nghĩa so sánh khi tokenizer, cách tính token hợp lệ và tập đánh giá tương đương.

GPT được mô tả là tối đa hóa likelihood của từng token với các token trước đó làm ngữ cảnh, dùng decoder Transformer có masked self-attention.[^radford-generative-pre-training-2018] Điều này khác masked language modeling: CLM không cần che ngẫu nhiên token trong dữ liệu đầu vào; ràng buộc “không nhìn phải” nằm trong kiến trúc attention.

### Shapes không được nhầm

Với batch $B$, độ dài đoạn $L$, và vocabulary $V$:

| Tensor | Shape | Ý nghĩa |
|---|---:|---|
| `input_ids` | `(B, L)` | các token được cung cấp cho model |
| `targets` | `(B, L)` | token đúng kế tiếp tại từng vị trí |
| `logits` | `(B, L, V)` | điểm chưa chuẩn hóa của token kế tiếp |
| `loss` | `()` | trung bình NLL trên các target hợp lệ |

`F.cross_entropy` nhận lớp vocabulary ở chiều cuối. Vì vậy, cách thông dụng là flatten `logits` thành `(B*L, V)` và `targets` thành `(B*L,)`; *không* softmax trước khi gọi hàm này vì hàm đã thực hiện log-softmax ổn định số.

## 2. Teacher forcing: dịch target, không phải “tiết lộ đáp án”

Từ một dãy

```text
<BOS> Tôi học mô hình ngôn ngữ <EOS>
```

teacher forcing tạo một dịch trái một bước:

```text
input : <BOS>  Tôi  học    mô hình  ngôn ngữ
target: Tôi    học  mô hình ngôn ngữ <EOS>
```

Ở vị trí chứa `học`, model nhận được tiền tố thật `<BOS> Tôi học` và bị phạt theo xác suất gán cho target `mô hình`. Nhờ causal mask, nó không được đọc `mô hình` từ input tại vị trí đó hoặc bất kỳ token tương lai nào.

### Vì sao huấn luyện song song được?

Nếu chạy tự hồi quy theo nghĩa đen, ta sẽ dự đoán $x_2$, đưa dự đoán đó trở lại model để dự đoán $x_3$, và cứ thế. Teacher forcing thay dự đoán trung gian bằng token đúng có sẵn trong corpus. Cả $L$ phép dự đoán vẫn dùng các tiền tố hợp lệ, nên một decoder có causal mask có thể tính logits cho mọi vị trí của đoạn trong một forward pass. Transformer gốc mô tả decoder input được dịch phải và self-attention bị mask để ngăn phụ thuộc vào vị trí sau.[^vaswani-transformer-2017]

> [!note] Hai chế độ, cùng một phân phối
> **Train:** tiền tố là token vàng, loss tính trên mọi vị trí song song.  
> **Generate:** tiền tố sau prompt gồm các token model đã chọn, một token được thêm mỗi bước.  
> Teacher forcing là cách tính likelihood hiệu quả; nó không làm thay đổi định nghĩa $p_\theta(x_{t+1}\mid x_{\le t})$.

### Khoảng cách train–generate

Ở inference, một token sai đã sinh nằm trong tiền tố của các bước sau, trong khi lúc train mô hình thường thấy tiền tố đúng. Đây thường được gọi là exposure bias hay train–inference mismatch. Nó là một rủi ro thực tế của decoding tự hồi quy, nhưng không chứng minh rằng teacher forcing sai hoặc mọi lỗi đều do nó: chất lượng dữ liệu, năng lực model, prompt và quy tắc sampling cũng thay đổi quỹ đạo sinh.

### Padding và ranh giới tài liệu

- Với các block độ dài cố định cắt từ dòng token liên tục, không cần padding; target luôn là token dịch trái.
- Với batch được pad, đặt nhãn pad thành `ignore_index` (thường `-100`) **và** đưa padding mask phù hợp vào attention. Chỉ bỏ loss ở pad nhưng vẫn để model attend vào pad có thể làm ngữ cảnh bị nhiễu.
- Đừng nối hai tài liệu độc lập mà không có EOS/ranh giới nếu bạn không muốn model học rằng cuối tài liệu thứ nhất nối tự nhiên sang đầu tài liệu thứ hai.
- Nếu prompt dài hơn context window, phải chọn chính sách: cắt tiền tố xa, dùng context dài hơn, hoặc cơ chế memory. Ví dụ minimal bên dưới chỉ giữ cửa sổ cuối.

## 3. Causal mask: ràng buộc thông tin, không phải chỉ là tensor tam giác

Với attention scores $S=QK^\top/\sqrt{d_k}$ cho một dãy dài $L$, mask nhân quả bổ sung một ma trận $M$ trước softmax:

$$
M_{ij}=\begin{cases}
0,&j\le i\\
-\infty,&j>i,
\end{cases}
\qquad
A=\operatorname{softmax}(S+M).
$$

Vì $\exp(-\infty)=0$, query tại vị trí $i$ chỉ phân bổ attention lên key ở $j\leq i$. Các attention layer cùng position-wise MLP có thể xử lý toàn bộ dãy song song khi train, nhưng không thể tạo một token chưa biết mà không chọn token trước đó. Scaled dot-product attention dùng pre-softmax mask để cấm các liên kết bất hợp pháp; decoder mask các vị trí output tương lai.[^vaswani-transformer-2017]

Ví dụ với $L=4$, hàng là query và cột là key:

| query \ key | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| 0 | ✓ | × | × | × |
| 1 | ✓ | ✓ | × | × |
| 2 | ✓ | ✓ | ✓ | × |
| 3 | ✓ | ✓ | ✓ | ✓ |

Dấu ✓ là được phép attention. Tùy API, mask Boolean có thể dùng `True` cho vị trí *bị cấm* hoặc *được phép*; cần đọc đúng quy ước của framework. OpenAI GPT reference trong kho áp dụng lower-triangular causal mask vào attention scores trước softmax.[^huggingface-openai-gpt-pytorch]

### Kiểm thử quan trọng hơn nhìn ma trận

Một mask có shape đúng vẫn có thể đảo chiều hoặc áp dụng sai broadcast. Hãy kiểm thử tính nhân quả theo hành vi:

1. Cho model ở `eval()` để tắt dropout.
2. Tạo `a` và `b` giống nhau đến vị trí `cut`, nhưng thay token từ `cut + 1` trở đi trong `b`.
3. So sánh `logits_a[:, :cut+1]` với `logits_b[:, :cut+1]`.
4. Chúng phải gần bằng nhau theo sai số dấu chấm động. Nếu khác, model đang rò token tương lai qua mask, position indexing, hoặc một phép trộn khác.

```python
@torch.no_grad()
def assert_causal(model, ids, cut):
    model.eval()
    changed = ids.clone()
    changed[:, cut + 1:] = torch.randint(
        0, model.vocab_size, changed[:, cut + 1:].shape, device=ids.device
    )
    before = model(ids)[:, :cut + 1]
    after = model(changed)[:, :cut + 1]
    torch.testing.assert_close(before, after, rtol=1e-5, atol=1e-6)
```

Đây là test structural: nó không chứng minh model học ngôn ngữ tốt, nhưng phát hiện trực tiếp leakage khiến train loss ảo thấp.

## 4. Một causal LM nhỏ có thể huấn luyện

Mã sau cố ý dùng `nn.TransformerEncoder` như một chồng self-attention block với mask nhân quả. Tên lớp “Encoder” là API PyTorch; với mask này nó hoạt động như stack self-attention causal, không có cross-attention. Mục tiêu là kiểm tra pipeline, không tái tạo GPT đầy đủ.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class TinyCausalLM(nn.Module):
    def __init__(self, vocab_size, max_seq_len, d_model=192, n_heads=6, n_layers=4, dropout=0.1):
        super().__init__()
        assert d_model % n_heads == 0
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

        # Tying là tùy chọn, nhưng giảm tham số và giữ cùng không gian token/output.
        self.lm_head.weight = self.token_emb.weight

    def forward(self, input_ids):
        B, T = input_ids.shape
        if T > self.max_seq_len:
            raise ValueError(f"sequence length {T} exceeds {self.max_seq_len}")
        pos = torch.arange(T, device=input_ids.device)
        hidden = self.token_emb(input_ids) + self.pos_emb(pos)[None, :, :]

        # PyTorch TransformerEncoder: True nghĩa là vị trí attention bị chặn.
        causal_mask = torch.triu(
            torch.ones(T, T, dtype=torch.bool, device=input_ids.device), diagonal=1
        )
        hidden = self.blocks(hidden, mask=causal_mask)
        return self.lm_head(self.ln_f(hidden))       # (B, T, V)
```

### Dữ liệu block và training loop

`ids` dưới đây là tensor `long` một chiều, đã được tokenizer encode. Chọn tokenizer trước, cố định vocabulary của nó, và chia train/validation theo tài liệu hoặc đoạn lớn trước khi lấy các cửa sổ chồng lấp. Không fit lại tokenizer trên validation để “cải thiện” kết quả đánh giá.

```python
def next_token_batch(ids, batch_size, block_size, device):
    # Mỗi start cần còn block_size input và block_size target dịch một token.
    starts = torch.randint(0, len(ids) - block_size - 1, (batch_size,))
    x = torch.stack([ids[i : i + block_size] for i in starts])
    y = torch.stack([ids[i + 1 : i + block_size + 1] for i in starts])
    return x.to(device), y.to(device)


def estimate_loss(model, ids, *, batch_size, block_size, device, batches=20):
    was_training = model.training
    model.eval()
    losses = []
    with torch.inference_mode():
        for _ in range(batches):
            x, y = next_token_batch(ids, batch_size, block_size, device)
            logits = model(x)
            loss = F.cross_entropy(logits.flatten(0, 1), y.flatten())
            losses.append(loss.item())
    model.train(was_training)
    return sum(losses) / len(losses)


device = "cuda" if torch.cuda.is_available() else "cpu"
block_size, batch_size = 128, 32
model = TinyCausalLM(vocab_size, max_seq_len=block_size).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)

for step in range(2_000):
    model.train()
    x, y = next_token_batch(train_ids, batch_size, block_size, device)
    logits = model(x)                                # (B, T, V)
    loss = F.cross_entropy(logits.flatten(0, 1), y.flatten())

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()

    if step % 100 == 0:
        val_loss = estimate_loss(
            model, val_ids, batch_size=batch_size, block_size=block_size, device=device
        )
        print(f"{step=:4d} train={loss.item():.3f} val={val_loss:.3f} "
              f"ppl={math.exp(val_loss):.1f} grad_norm={grad_norm:.2f}")
```

`optimizer.zero_grad` phải nằm trước `backward`: autograd tích lũy gradient vào `.grad`. `eval()`/`inference_mode()` trong validation và generate vừa tắt dropout vừa không lưu activation graph. Gradient clipping không sửa lỗi target/mask, nhưng giới hạn một update có norm bất thường.

> [!warning] Điều kiện dữ liệu
> `len(ids) > block_size + 1` là cần thiết. Với corpus quá nhỏ, hãy cố ý overfit vài batch để kiểm tra code; đừng diễn giải validation loss trên dữ liệu bị trùng mạnh với train là khả năng tổng quát hóa.

## 5. Generation là vòng lặp tự hồi quy

Sau prompt $x_{1:t}$, lấy vector logits cuối $z_t$, biến đổi nó theo chính sách decode, chọn $x_{t+1}$, rồi nối lại vào input. Code không cache KV nên forward lại toàn bộ cửa sổ mỗi bước; đây đúng về semantics nhưng chậm khi prompt dài. [KV caching](kv-caching.md) giữ key/value của tiền tố để decode chỉ tính projection của token mới.

### Temperature thay đổi độ sắc, không tự tạo kiến thức mới

Với temperature $\tau>0$:

$$
p_\tau(j)=\operatorname{softmax}(z_j/\tau).
$$

- $\tau=1$: phân phối model gốc.
- $0<\tau<1$: chênh lệch logits bị khuếch đại; sample tập trung hơn. Khi $\tau\to0$, hành vi gần greedy nhưng không nên chia cho 0.
- $\tau>1$: phân phối phẳng hơn; đa dạng hơn nhưng dễ chọn token xác suất thấp.

Temperature bảo toàn thứ tự logits nhưng thay đổi tỷ số xác suất. Nó phải được áp dụng **trước** softmax và trước các filter dựa trên xác suất như top-p.

### Top-k và top-p giới hạn support lấy mẫu

- **Top-k:** giữ đúng $k$ logits lớn nhất, gán các token khác $-\infty$, rồi softmax. `k=1` tương đương greedy nếu sample từ phân phối còn lại.
- **Top-p (nucleus):** sắp token theo xác suất giảm dần và giữ tập nhỏ nhất có tổng xác suất ít nhất $p$. Số token được giữ biến thiên theo độ bất định: distribution sắc có thể chỉ giữ ít token, distribution phẳng giữ nhiều token.
- Có thể dùng cả hai: top-k đặt trần số ứng viên, top-p tiếp tục bỏ phần đuôi trong các ứng viên còn lại. Đây là một chính sách thiết kế; hãy log cấu hình thực tế thay vì gọi chung là “sampling”.

Không filter nào sửa được xác suất có điều kiện kém; chúng chỉ chọn từ phân phối model đã học. Top-k/top-p quá nhỏ có thể lặp hoặc làm mất token cần thiết, còn quá lớn kết hợp temperature cao có thể cho đầu ra hỗn loạn.

### Sampler tham chiếu

```python
@torch.inference_mode()
def generate(model, prompt_ids, *, max_new_tokens, temperature=1.0,
             top_k=None, top_p=None, do_sample=True, eos_id=None):
    """prompt_ids: LongTensor (B, T_prompt); trả về prompt nối các token mới."""
    if temperature <= 0:
        raise ValueError("temperature must be > 0; use do_sample=False for greedy decoding")
    if top_k is not None and top_k <= 0:
        raise ValueError("top_k must be positive or None")
    if top_p is not None and not 0 < top_p <= 1:
        raise ValueError("top_p must lie in (0, 1]")

    model.eval()
    ids = prompt_ids
    finished = torch.zeros(ids.size(0), dtype=torch.bool, device=ids.device)

    for _ in range(max_new_tokens):
        context = ids[:, -model.max_seq_len:]
        logits = model(context)[:, -1, :]            # (B, V)
        filtered = logits / temperature

        if top_k is not None:
            k = min(top_k, filtered.size(-1))
            cutoff = torch.topk(filtered, k, dim=-1).values[:, [-1]]
            filtered = filtered.masked_fill(filtered < cutoff, float("-inf"))

        if top_p is not None and top_p < 1.0:
            sorted_logits, sorted_indices = torch.sort(filtered, descending=True, dim=-1)
            sorted_probs = torch.softmax(sorted_logits, dim=-1)
            remove_sorted = torch.cumsum(sorted_probs, dim=-1) > top_p
            # Giữ token đầu tiên khiến cumulative probability đạt/vượt p.
            remove_sorted[:, 1:] = remove_sorted[:, :-1].clone()
            remove_sorted[:, 0] = False
            remove = torch.zeros_like(remove_sorted).scatter_(1, sorted_indices, remove_sorted)
            filtered = filtered.masked_fill(remove, float("-inf"))

        if do_sample:
            probs = torch.softmax(filtered, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)
        else:
            next_id = torch.argmax(filtered, dim=-1, keepdim=True)

        # Batch có EOS: giữ EOS ở các hàng đã hoàn thành để không sinh nội dung mới.
        if eos_id is not None:
            next_id = torch.where(finished[:, None], torch.full_like(next_id, eos_id), next_id)
            finished |= next_id.squeeze(1).eq(eos_id)
        ids = torch.cat((ids, next_id), dim=1)
        if eos_id is not None and finished.all():
            break
    return ids
```

Ví dụ gọi sau khi encode prompt:

```python
torch.manual_seed(7)  # chỉ để tái lập một lần chạy sampling
out = generate(model, prompt_ids, max_new_tokens=100,
               temperature=0.8, top_k=50, top_p=0.95, eos_id=eos_id)
print(tokenizer.decode(out[0].tolist()))
```

`torch.multinomial` lấy mẫu từ xác suất, còn `argmax` là greedy và quyết định với model/prompt không đổi. Seed làm tái lập trong một môi trường xác định, nhưng kết quả có thể vẫn thay đổi theo phiên bản kernel, device, precision hoặc trạng thái RNG khác.

## 6. Thứ tự triển khai và kiểm tra trước khi scale

| Kiểm tra | Cách làm | Kết quả mong đợi | Nếu sai, kiểm tra trước |
|---|---|---|---|
| Shift | `torch.equal(x[:, 1:], y[:, :-1])` trên batch xây từ stream | `True` | slicing, EOS, boundary |
| Vocabulary | `0 <= ids < V` | mọi ID hợp lệ | tokenizer/checkpoint không khớp |
| Shape | in `x`, `logits`, `y` | `(B,T)`, `(B,T,V)`, `(B,T)` | trục vocabulary, `batch_first` |
| Baseline | logits bằng 0 | loss gần `log(V)` | nhãn, reduction, ignore index |
| Overfit | train 1–4 batch đủ lâu | training loss giảm mạnh | target shift, `zero_grad`, LR, model mode |
| Causality | `assert_causal` ở trên | logits tiền tố không đổi | chiều/dạng mask, dropout |
| Validation | `eval` + dữ liệu chưa thấy | không dùng gradient/update | data leakage, split sau chunking |
| Sampler | seed + `do_sample=False` | output lặp lại | prompt/context crop, EOS, decode |

Một loss train thấp không đủ chứng minh CLM đúng: model có thể đang đọc target tương lai nếu mask bị đảo, hoặc validation có thể chứa các window gần như giống train. Overfit ít batch và perturb-future test là hai kiểm tra rẻ có khả năng bắt lỗi cao nhất.

## 7. Các nhầm lẫn thường gặp

1. **“Causal mask chỉ cần khi generate.”** Sai. Lúc train, toàn bộ target có sẵn; nếu không mask, attention đọc token tương lai và loss không còn đo dự đoán từ tiền tố.
2. **“Teacher forcing nghĩa là input và target giống nhau.”** Sai. `target` phải shift trái một token. Input bằng target ở cùng vị trí biến bài toán thành sao chép token.
3. **“Softmax rồi đưa probability vào `cross_entropy`.”** Sai trong PyTorch chuẩn: `F.cross_entropy` nhận logits. Softmax trước đó làm mất ổn định số và áp dụng sai công thức.
4. **“Temperature bằng 0 là greedy.”** Không nên cài như vậy vì chia cho 0. Dùng `argmax` hoặc một nhánh `do_sample=False`.
5. **“Top-p giữ các token có xác suất lớn hơn p.”** Sai. Nó giữ *tập tích lũy* có tổng xác suất đạt $p$; một token xác suất nhỏ vẫn có thể được giữ nếu distribution phẳng.
6. **“Top-k/top-p luôn cải thiện chất lượng.”** Không có bảo đảm. Chúng đánh đổi đa dạng, lặp, độ bám prompt và xác suất đuôi; cần đánh giá theo nhiệm vụ.
7. **“Causal mask thay thế padding mask.”** Sai. Causal mask cấm tương lai; padding mask cấm token đệm. Batch có pad thường cần cả hai.

## 8. Ranh giới và bước tiếp theo

Ví dụ này không xử lý data curation, distributed training, mixed precision, schedule, checkpointing, safety, đánh giá task-level hay cache hiệu năng. Độ phức tạp training của full self-attention trên một đoạn vẫn tăng bậc hai theo độ dài; lúc generate không cache, mỗi bước còn lặp lại tính toán tiền tố. Đây là lý do [KV caching](kv-caching.md), attention tối ưu và các thiết kế context dài xuất hiện sau khi semantics cơ bản đã đúng.

Bài này cụ thể hóa Stage 2 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Nó kế thừa logits, cross-entropy và vòng lặp tối ưu từ [Foundations for training a bigram language model](foundations-for-training-a-bigram-language-model.md), rồi chuẩn bị trực tiếp cho [scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) và một decoder-only Transformer theo [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md).

## Relationships

- **Elaborates:** Stage 2 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng objective, test, training loop và sampler.
- **Builds on:** [Foundations for training a bigram language model](foundations-for-training-a-bigram-language-model.md), giữ nguyên tokenization, logits, cross-entropy và optimizer interface.
- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md)'s pre-softmax causal attention mask.
- **Operationalizes:** [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md)'s causal next-token objective in a small implementation.
- **Prepares for:** [KV caching](kv-caching.md), nơi generation tự hồi quy giữ lại trạng thái attention của tiền tố.

[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training” (2018), [PDF](../raw/gpt.pdf), Sections 3–4.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), `model_architecture.tex`.
[^huggingface-openai-gpt-pytorch]: Hugging Face, “PyTorch OpenAI GPT model,” [source](../raw/gpt-source.py), attention implementation. The supplied source has no revision metadata.
