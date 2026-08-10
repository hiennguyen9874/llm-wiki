---
type: Synthesis
title: Foundations for training a bigram language model
description: A practical mathematical foundation and build guide for a character-level or BPE bigram language model, connecting tokenization, logits, softmax cross-entropy, backpropagation, and AdamW to causal GPT pre-training.
tags: [foundations, language-modeling, bigram, tokenization, optimization, gpt]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T22:31:55+07:00 }
sources:
  - id: radford-generative-pre-training-2018
    resource: ../raw/gpt.pdf
    title: Improving Language Understanding by Generative Pre-Training
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: huggingface-openai-gpt-pytorch
    resource: ../raw/gpt-source.py
    title: PyTorch OpenAI GPT model
---

# Foundations for training a bigram language model

Một **bigram language model** là mô hình dự đoán token kế tiếp chỉ từ **một token ngay trước nó**. Nó quá đơn giản để hiểu một câu dài, nhưng lại là bài tập tốt nhất để hiểu cơ chế cốt lõi của GPT mà không bị che khuất bởi attention và hàng triệu tham số:

```text
văn bản → token ID → logits → softmax → cross-entropy loss
        → backward → AdamW → xác suất token kế tiếp
```

Mục tiêu của bài này là tự huấn luyện một mô hình ký tự nhỏ, biết vì sao từng dòng mã tồn tại, và có các kiểm tra để phát hiện lỗi trước khi mở rộng sang GPT nhỏ. Công thức, ví dụ số và mã PyTorch dưới đây là **tổng hợp sư phạm**; các tuyên bố về GPT, BPE và causal attention được dẫn nguồn riêng.

> [!success] Sau khi hoàn thành
> Bạn có thể biến một tệp văn bản thành dữ liệu huấn luyện, giải thích chính xác `input`, `target` và shape `(B, L, V)`, huấn luyện một bigram model có loss giảm, sinh token mới bằng sampling, và nêu được ba thành phần cần thêm để biến nó thành GPT nhỏ.

## 1. Bài toán trong một ví dụ nhỏ

Giả sử corpus chỉ là:

```text
mèo ăn cá
```

Nếu dùng tokenizer theo ký tự, chuỗi được tách thành các token như `m`, `è`, `o`, khoảng trắng, `ă`, `n`, ... Mỗi lần học, model nhìn một token hiện tại và cố đoán token ngay sau nó:

| Token hiện tại (`input`) | Token cần đoán (`target`) |
|---|---|
| `m` | `è` |
| `è` | `o` |
| `o` | khoảng trắng |
| khoảng trắng | `ă` |
| `ă` | `n` |

Nếu token hiện tại là `m`, bigram model học phân phối

$$
p_\theta(\text{token sau}=j\mid\text{token hiện tại}=\texttt{m}).
$$

Nó có thể học rằng sau `q` trong nhiều văn bản tiếng Anh thường là `u`, hoặc sau dấu cách có nhiều khả năng bắt đầu một từ. Nhưng khi phải chọn token sau `ăn` trong hai câu có chủ đề khác nhau, nó **không nhớ** các token trước đó. Đây là giới hạn của giả định bigram, không phải dấu hiệu model huấn luyện kém.

### So với một language model nhân quả đầy đủ

Với dãy token $x_1,x_2,\ldots,x_T$, language model nhân quả mô hình hóa xác suất dãy bằng quy tắc chuỗi:

$$
p_\theta(x_{1:T})=p_\theta(x_1)\prod_{t=1}^{T-1}p_\theta(x_{t+1}\mid x_{\leq t}).
$$

GPT cũng dự đoán token kế tiếp, nhưng có thể điều kiện hóa trên **toàn bộ tiền tố** $x_{\leq t}$ nhờ masked self-attention.[^radford-generative-pre-training-2018] Bigram thay điều kiện đó bằng chỉ token cuối:

$$
p_\theta(x_{t+1}\mid x_{\leq t})\approx p_\theta(x_{t+1}\mid x_t).
$$

Chính sự đơn giản này biến model thành một bảng chuyển tiếp có thể quan sát và kiểm thử hoàn toàn.

## 2. Tokenization: cho máy tính một từ vựng hữu hạn

Neural network không nhận trực tiếp chuỗi Unicode. Tokenizer biến văn bản thành số nguyên trong khoảng $[0,V)$, với $V$ là kích thước từ vựng:

$$
\text{text}\xrightarrow{\text{encode}}[x_1,\ldots,x_T],\qquad
[x_1,\ldots,x_T]\xrightarrow{\text{decode}}\text{text}.
$$

Ví dụ, nếu từ vựng là `{" ": 0, "a": 1, "b": 2}`, chuỗi `"ab"` được encode thành `[1, 2]`. Số `1` không có nghĩa toán học tự nhiên là “a”; đó chỉ là chỉ mục đã được tokenizer quy ước.

> [!warning] Tokenizer là một phần của model
> Lưu tokenizer cùng checkpoint. Ma trận trọng số chỉ có nghĩa nếu chỉ mục `17` vẫn biểu diễn đúng token như khi huấn luyện. Thay đổi thứ tự vocabulary, quy tắc chuẩn hóa Unicode hoặc special token sẽ làm checkpoint không còn tương thích.

### Bắt đầu bằng character-level

Với bài đầu tiên, hãy lấy mọi ký tự xuất hiện trong tập train làm vocabulary:

```python
chars = sorted(set(train_text))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
encode = lambda s: [stoi[ch] for ch in s]
decode = lambda ids: "".join(itos[i] for i in ids)
```

Ưu điểm là dễ kiểm tra: `decode(encode(s))` phải trả lại `s` cho văn bản nằm trong vocabulary. Nhược điểm là một từ dài thành nhiều bước dự đoán. Trong Python, “ký tự” thường là Unicode code point, không luôn trùng với một grapheme người đọc nhìn thấy; cần chú ý với emoji, dấu kết hợp và văn bản đa ngôn ngữ.

### BPE là gì, và tại sao chưa nên dùng vocabulary lớn?

Byte-pair encoding (BPE) bắt đầu từ đơn vị nhỏ (ký tự hoặc byte), lặp lại việc gộp các cặp kề nhau thường gặp thành token mới. Vì thế một token có thể là một ký tự, một mảnh từ, hoặc một từ phổ biến. GPT ban đầu dùng BPE với 40.000 merge; GPT-2 dùng byte-level BPE với vocabulary 50.257 token.[^radford-generative-pre-training-2018][^radford-gpt-2-2019]

BPE làm chuỗi ngắn hơn, nhưng bigram có một bảng $V\times V$. Số tham số vì vậy tăng theo **bình phương** vocabulary:

| $V$ | Số phần tử trong bảng bigram $V^2$ |
|---:|---:|
| 100 | 10.000 |
| 1.000 | 1.000.000 |
| 50.000 | 2.500.000.000 |

Do đó hãy dùng character-level, hoặc BPE rất nhỏ, khi học bigram. BPE vocabulary cỡ GPT là hợp lý cho Transformer có hidden size $d\ll V$, không phải cho bảng logits trực tiếp của bigram.

### Chia dữ liệu đúng thứ tự

Để đo khả năng tổng quát hóa một cách có ý nghĩa:

1. Chia corpus thành train/validation theo **tài liệu hoặc đoạn lớn** trước khi tạo cửa sổ chồng lấp.
2. Tạo vocabulary/tokenizer từ train, hoặc dùng một tokenizer đã được version hóa.
3. Encode từng split bằng cùng tokenizer.
4. Chỉ dùng train để gọi `backward()` và `optimizer.step()`.

Nếu chia sau khi cắt các cửa sổ gần như trùng nhau, validation có thể chứa gần nguyên văn dữ liệu train. Validation loss khi đó lạc quan giả tạo.

## 3. Bigram model thực chất là một bảng logits

Đặt $W\in\mathbb{R}^{V\times V}$ là tham số duy nhất của model.

- Hàng $i$, ký hiệu $W_i$, ứng với token hiện tại có ID $i$.
- Cột $j$ ứng với ứng viên token kế tiếp có ID $j$.
- Phần tử $W_{ij}$ là **logit**: điểm chưa chuẩn hóa cho việc “sau $i$ là $j$”.

Khi input hiện tại là ID $i$, model chỉ lấy hàng đó:

$$
z = W_i,\qquad z\in\mathbb{R}^{V}.
$$

Nếu viết input dưới dạng one-hot vector hàng $e_i\in\mathbb{R}^{1\times V}$, đây là phép nhân ma trận quen thuộc:

$$
z=e_iW.
$$

Vì $e_i$ chỉ có một giá trị bằng 1, phép nhân chọn đúng hàng $i$. Trong PyTorch, `W[input_ids]` hoặc `nn.Embedding` thực hiện lookup này hiệu quả hơn việc tạo one-hot, nhưng ý nghĩa toán học giống hệt nhau.

### Shapes cần thuộc lòng

Với batch size $B$, số vị trí trong một batch $L$, và vocabulary $V$:

| Tên | Shape | Ý nghĩa |
|---|---:|---|
| `input_ids` | `(B, L)` | token hiện tại ở mỗi vị trí |
| `targets` | `(B, L)` | token đúng ở vị trí kế tiếp |
| `logits` | `(B, L, V)` | điểm của mọi token ứng viên |
| `W` | `(V, V)` | bảng chuyển tiếp có thể học |

Ví dụ `input_ids[2, 5] = 17` nghĩa là model dùng hàng `W[17]` để tạo `logits[2, 5, :]`. Không có thông tin nào từ `input_ids[2, :5]` được trộn vào: đây là điểm khác biệt quyết định giữa bigram và Transformer.

## 4. Softmax: biến điểm thành xác suất

Logits có thể âm, dương và không có tổng bằng 1, nên chưa thể dùng để “bốc thăm” token. Softmax biến vector logits $z$ thành phân phối xác suất:

$$
p_j=\operatorname{softmax}(z)_j=
\frac{\exp(z_j)}{\sum_{k=1}^{V}\exp(z_k)}.
$$

Kết quả luôn có $p_j>0$ và $\sum_jp_j=1$. Logit càng lớn tương đối so với các logit khác, xác suất càng lớn.

### Ví dụ số

Giả sử vocabulary là `["a", "b", "c"]` và logits sau token hiện tại là:

$$
z=[2,1,0].
$$

Softmax xấp xỉ cho:

$$
p=[0{,}665,\ 0{,}245,\ 0{,}090].
$$

Model ưu tiên `a`, nhưng vẫn có thể sinh `b` hoặc `c` nếu lấy mẫu. Thêm cùng một hằng số vào mọi logit, ví dụ $[12,11,10]$, không đổi phân phối. Vì tính chất đó, softmax ổn định số thường trừ logit lớn nhất trước khi lấy mũ:

$$
\operatorname{softmax}(z)_j=
\frac{\exp(z_j-\max(z))}{\sum_k\exp(z_k-\max(z))}.
$$

Khi huấn luyện, không cần tự viết softmax rồi log. `torch.nn.functional.cross_entropy` nhận logits thô và dùng cách tính `log_softmax` ổn định hơn.

## 5. Cross-entropy: “phạt” model vì đặt xác suất thấp cho đáp án đúng

Nếu target đúng có ID $y$, loss của một dự đoán là:

$$
\ell(z,y)=-\log p_y.
$$

Trong ví dụ trên, nếu target là `b`, thì $p_y=0{,}245$ và loss xấp xỉ $-\log(0{,}245)=1{,}41$. Nếu model nâng xác suất của `b` lên gần 1, loss tiến gần 0. Nếu nó đặt xác suất cho `b` gần 0, loss rất lớn.

Trung bình loss của mọi vị trí trong batch là **cross-entropy**. Tối thiểu hóa nó chính là tối đa hóa xác suất model gán cho chuỗi dữ liệu đúng.

### Hai kiểm tra đơn giản nhưng rất hữu ích

- Nếu mọi logit bằng nhau, model đoán đều $p_y=1/V$. Loss phải gần $\log V$ (log tự nhiên). Đây là baseline trước khi học.
- Perplexity thường là $\exp(\text{cross-entropy})$. Nó có thể được hiểu gần đúng là số lựa chọn hiệu dụng của model, nhưng chỉ so sánh được giữa các thí nghiệm dùng cùng tokenizer và cùng cách tính loss.

### Vì sao gradient có dạng `p - y`?

Gọi $\mathbf y$ là one-hot vector của target: phần tử đúng bằng 1, các phần tử khác bằng 0. Với softmax kết hợp cross-entropy:

$$
\frac{\partial\ell}{\partial z_j}=p_j-y_j.
$$

Đây là trực giác quan trọng nhất của phân loại đa lớp:

- Với token đúng, $y_j=1$, nên gradient thường âm. Gradient descent sẽ **tăng** logit đó.
- Với token sai, $y_j=0$, nên gradient là $p_j>0$. Gradient descent sẽ **giảm** logit đó; token sai đang được model tin nhiều bị giảm mạnh hơn.

Trong ví dụ $p=[0{,}665,0{,}245,0{,}090]$ và target là `b`, gradient là $[0{,}665,-0{,}755,0{,}090]`. Vì input chỉ lookup một hàng của $W$, một ví dụ chỉ cập nhật hàng tương ứng token hiện tại.

## 6. Huấn luyện một model hoàn chỉnh bằng PyTorch

Đoạn mã dưới đây là một chương trình tối thiểu. Đặt corpus UTF-8 của bạn ở `input.txt`, cài PyTorch phù hợp với máy, rồi chạy nó. Mã dùng character-level để mọi bước đều quan sát được.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# 1. Đọc và tokenize. Với dự án thật, chia theo tài liệu trước bước này.
text = open("input.txt", encoding="utf-8").read()
if len(text) < 100:
    raise ValueError("Corpus quá ngắn để minh họa; hãy dùng văn bản dài hơn.")

chars = sorted(set(text))
vocab_size = len(chars)
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
encode = lambda s: [stoi[ch] for ch in s]
decode = lambda ids: "".join(itos[i] for i in ids)
ids = torch.tensor(encode(text), dtype=torch.long)

# Tách theo một ranh giới lớn. Với nhiều tài liệu, hãy split theo document thay vì theo ID.
n = int(0.9 * len(ids))
train_ids, val_ids = ids[:n], ids[n:]

# 2. Tạo cặp x/y dịch trái một token.
device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size, block_size = 32, 32

def get_batch(data):
    if len(data) <= block_size:
        raise ValueError("Split phải dài hơn block_size.")
    starts = torch.randint(0, len(data) - block_size, (batch_size,))
    x = torch.stack([data[i : i + block_size] for i in starts])
    y = torch.stack([data[i + 1 : i + block_size + 1] for i in starts])
    return x.to(device), y.to(device)

# 3. Mỗi hàng embedding chính là logits cho token kế tiếp.
class BigramLM(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.table = nn.Embedding(vocab_size, vocab_size)  # W có shape (V, V)

    def forward(self, input_ids, targets=None):
        logits = self.table(input_ids)                     # (B, L, V)
        loss = None
        if targets is not None:
            B, L, V = logits.shape
            loss = F.cross_entropy(logits.reshape(B * L, V), targets.reshape(B * L))
        return logits, loss

model = BigramLM(vocab_size).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-2, weight_decay=0.0)

# 4. Forward → loss → xóa gradient cũ → backward → update.
for step in range(2_000):
    model.train()
    x, y = get_batch(train_ids)
    _, loss = model(x, y)

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    if step % 200 == 0:
        print(f"step={step:4d}  train_loss={loss.item():.3f}  "
              f"baseline≈{math.log(vocab_size):.3f}")
```

Điều đáng chú ý là `nn.Embedding(vocab_size, vocab_size)` ở đây **không** phải token embedding nhỏ của GPT. Nó là một cách tiện dụng để lưu cả bảng $W\in\mathbb R^{V\times V}$ và lookup một hàng. GPT thường lookup embedding $V\times d$, xử lý vector $d$ chiều qua nhiều block, rồi chiếu về $V$ logits.

### Input và target đã lệch nhau như thế nào?

Nếu một lát token là:

```text
IDs:     [7, 2, 9, 4, 1]
x:       [7, 2, 9, 4]
y:       [2, 9, 4, 1]
```

thì `x[:, 1:]` phải bằng `y[:, :-1]`. Mỗi vị trí của `x` tạo đúng một dự đoán cho vị trí cùng chỗ trong `y`. Đây là quy tắc cần giữ nguyên khi đi từ bigram sang causal Transformer.

### Backpropagation và AdamW đang làm gì?

`loss.backward()` dùng chain rule để tính $\partial\mathcal L/\partial W$ rồi ghi vào `model.table.weight.grad`. PyTorch **tích lũy** gradient vào `.grad`, do đó cần gọi `zero_grad` trước mỗi update nếu bạn không chủ đích cộng gradient của nhiều batch.

SGD đơn giản cập nhật tham số theo $\theta\leftarrow\theta-\eta g$. AdamW thay đổi bước đi theo moment bậc một và hai của gradient, đồng thời áp dụng weight decay tách biệt:

$$
\theta_t\leftarrow(1-\eta\lambda)\theta_{t-1}
-\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}.
$$

Ở lần chạy đầu, `weight_decay=0.0` giúp cô lập lỗi pipeline. Sau khi model đã chạy đúng, có thể thử weight decay nhỏ, learning-rate schedule và gradient clipping. Không có optimizer nào sửa được target bị lệch sai hoặc tokenizer/checkpoint không khớp.

## 7. Sinh văn bản từ phân phối đã học

Huấn luyện dùng target đúng để tính loss. Khi sinh, model không biết target; nó phải chọn token mới, nối token đó vào chuỗi, rồi lặp lại.

```python
@torch.inference_mode()
def generate(model, start_id, max_new_tokens=300, temperature=1.0):
    if temperature <= 0:
        raise ValueError("temperature phải > 0")
    model.eval()
    out = torch.tensor([[start_id]], dtype=torch.long, device=device)

    for _ in range(max_new_tokens):
        # Với bigram, chỉ token cuối ảnh hưởng đến logits tiếp theo.
        logits, _ = model(out[:, -1:])
        next_logits = logits[:, -1, :] / temperature
        probs = F.softmax(next_logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)
        out = torch.cat((out, next_id), dim=1)
    return out[0].tolist()

# Chọn một ký tự có trong vocabulary; seed chỉ giúp tái lập sampling trong cùng môi trường.
torch.manual_seed(7)
print(decode(generate(model, stoi[text[0]])))
```

`torch.multinomial` lấy mẫu theo xác suất, nên token xác suất thấp vẫn đôi khi được chọn. Nếu thay bằng `torch.argmax`, đầu ra là greedy: quyết định và dễ debug hơn, nhưng rất dễ lặp.

**Temperature** chỉ thay đổi cách lấy mẫu, không thay đổi những gì model đã học:

$$
p_\tau(j)=\operatorname{softmax}(z_j/\tau),\qquad \tau>0.
$$

- $\tau<1$: phân phối sắc hơn, ít ngẫu nhiên hơn.
- $\tau=1$: dùng phân phối model gốc.
- $\tau>1$: phân phối phẳng hơn, đa dạng hơn nhưng thường nhiều lỗi hơn.

Đừng dùng $\tau=0$ để biểu thị greedy vì đó là phép chia cho 0; dùng `argmax` thay thế.

## 8. Cách biết model và dữ liệu có thật sự đúng

Loss giảm là cần thiết nhưng chưa đủ: target sai hoặc rò dữ liệu có thể cho loss thấp một cách giả. Hãy kiểm tra theo thứ tự sau.

| Kiểm tra | Cách làm | Kết quả mong đợi |
|---|---|---|
| Encode/decode | `decode(encode(s))` | trả lại `s` trong phạm vi vocabulary |
| ID hợp lệ | `0 <= ids < V` | mọi token ID đều thuộc khoảng hợp lệ |
| Shift | `torch.equal(x[:, 1:], y[:, :-1])` | `True` |
| Shape | in `x.shape`, `logits.shape`, `y.shape` | `(B,L)`, `(B,L,V)`, `(B,L)` |
| Baseline | logits bằng 0 | loss gần `log(V)` |
| Overfit | train lặp lại 1–4 batch | loss giảm mạnh |
| Validation | `eval()` và không update | đánh giá trên dữ liệu chưa thấy |

> [!tip] Overfit một batch trước
> Đây là cách debug rẻ nhất. Nếu model không thể học gần thuộc một batch rất nhỏ, đừng tăng corpus hay thêm attention. Kiểm tra trước: target đã shift chưa, `zero_grad → backward → step` có đủ không, learning rate có quá nhỏ/lớn không, và các ID có vượt vocabulary không.

Một bigram model tốt vẫn sẽ sinh văn bản ngắn và lặp nhiều hơn GPT. Nó chỉ học thống kê cặp kề nhau; đó là kết quả đúng với năng lực của kiến trúc.

## 9. Từ bigram sang GPT nhỏ: giữ gì, thay gì?

Giữ nguyên tokenizer, cặp `input`/`target` dịch trái, logits cuối cùng, cross-entropy, backpropagation, optimizer và sampler. Chỉ thay phần model theo ba bước:

1. **Token và position embeddings:** thay bảng $V\times V$ bằng embedding $V\times d$ và thêm thông tin vị trí.
2. **Trộn ngữ cảnh bên trái:** thêm causal self-attention, MLP, residual connection và normalization để hidden state ở vị trí $t$ có thể dùng token $\leq t$.
3. **Vocabulary head:** chiếu hidden states có shape `(B, L, d)` thành logits `(B, L, V)` và tính cùng cross-entropy.

Causal mask phải chặn vị trí $t$ nhìn token tương lai. Transformer gốc mô tả việc dịch input decoder một vị trí và mask self-attention để dự đoán tại vị trí $i$ chỉ phụ thuộc các output đã biết trước đó.[^vaswani-transformer-2017] Mã OpenAI GPT tham chiếu trong kho cũng áp dụng mask tam giác dưới lên attention scores trước softmax.[^huggingface-openai-gpt-pytorch]

> [!note] Bài tập này chưa dạy gì?
> Bigram không kiểm tra attention, positional representation, residual path, normalization, MLP sâu, KV cache, dữ liệu ở quy mô lớn, an toàn hay đánh giá mô hình. Giá trị của nó là làm cho pipeline dự đoán-token-kế-tiếp trở nên đủ nhỏ để bạn đo và hiểu từng phần.

Bước tiếp theo là [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md): cùng objective này, nhưng model nhìn được tiền tố nhờ teacher forcing và causal mask. Sau đó học [scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), và [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md). [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) đặt bigram ở Stage 1.

## Relationships

- **Elaborates:** Stage 1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng một bài thực hành có mã và kiểm thử.
- **Prepares for:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md), [scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md), [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), và [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md).
- **Uses:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md) để minh họa byte-level BPE.

[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training” (2018), [PDF](../raw/gpt.pdf), Sections 3–4.
[^radford-gpt-2-2019]: Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), [PDF](../raw/gpt2.pdf), Section 2.2.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), `model_architecture.tex`.
[^huggingface-openai-gpt-pytorch]: Hugging Face, “PyTorch OpenAI GPT model,” [source](../raw/gpt-source.py), attention implementation.
