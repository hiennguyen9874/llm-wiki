---
type: Synthesis
title: Foundations for training a bigram language model
description: A practical mathematical foundation and build guide for a character-level or BPE bigram language model, connecting tokenization, logits, softmax cross-entropy, backpropagation, and AdamW to causal GPT pre-training.
tags: [foundations, language-modeling, bigram, tokenization, optimization, gpt]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T21:54:00+07:00 }
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

Một bigram language model là nơi nhỏ nhất nhưng đủ thật để học chuỗi nhân quả của huấn luyện GPT: **văn bản → token IDs → logits → softmax → cross-entropy → gradient → AdamW → phân phối token kế tiếp**. Nó chỉ ước lượng token kế tiếp từ *một* token hiện tại, nên không hiểu ngữ cảnh dài; chính giới hạn này làm từng tensor, từng phép nhân ma trận, và từng gradient có thể kiểm tra được. Phần giải thích công thức, mã giả và khuyến nghị triển khai dưới đây là tổng hợp sư phạm; các chi tiết lịch sử về mục tiêu GPT, BPE và causal Transformer được trích nguồn riêng.

> [!success] Kết quả học tập
> Sau bài này, bạn có thể huấn luyện một mô hình ký tự hoặc BPE có loss giảm trên tập huấn luyện, sinh văn bản từ phân phối kế tiếp, giải thích được $p-y$ là gradient của logits, và chỉ ra chính xác ba thay đổi cần thiết để đi từ bigram đến GPT nhỏ.

## 1. Bài toán: dự đoán token kế tiếp

Gọi chuỗi token là $x_1, x_2, \ldots, x_T$, với mỗi $x_t\in\{0,\ldots,V-1\}$ và $V$ là kích thước từ vựng. Mô hình ngôn ngữ nhân quả tối đa hóa xác suất có điều kiện

$$
P(x_{1:T})=\prod_{t=1}^{T-1}P(x_{t+1}\mid x_{\le t}).
$$

GPT cũng dùng mục tiêu dự đoán token kế tiếp trên văn bản liên tục, nhưng dùng masked self-attention để điều kiện hóa trên **toàn bộ** tiền tố; GPT đầu tiên báo cáo tokenizer BPE 40.000 merge và các đoạn huấn luyện dài 512 token.[^radford-generative-pre-training-2018] Bigram thay thế tiền tố $x_{\le t}$ bằng chỉ token gần nhất $x_t$:

$$
P_\theta(x_{t+1}=j\mid x_t=i).
$$

Do đó, nó không thể phân biệt hai câu có cùng token cuối nhưng ngữ cảnh trước đó khác nhau. Đây không phải lỗi huấn luyện mà là giả định mô hình.

### Ví dụ trực giác

Nếu token hiện tại là `q`, dữ liệu tiếng Anh thường khiến mô hình đặt xác suất lớn cho `u`; nếu token hiện tại là khoảng trắng, nó phân phối xác suất trên nhiều ký tự/mảnh từ có thể mở đầu. Bigram không biết câu đang nói về chủ đề gì, cũng không biết token cách đó hai bước. Nó chỉ học một bảng chuyển tiếp có điều kiện.

## 2. Tokenization: biến văn bản thành các đơn vị học được

Mạng không nhận chuỗi Unicode trực tiếp. Tokenizer cần một ánh xạ xác định được:

$$
\text{text}\xrightarrow{\text{encode}}[x_1,\ldots,x_T],\qquad
[x_1,\ldots,x_T]\xrightarrow{\text{decode}}\text{text}.
$$

Hãy lưu tokenizer cùng checkpoint: ma trận tham số chỉ có nghĩa khi hàng/cột số $i$ vẫn trỏ tới đúng token như lúc huấn luyện.

### Character-level: điểm xuất phát tốt nhất

Từ vựng là các ký tự xuất hiện trong corpus (nên có thể thêm token bắt đầu/kết thúc nếu dữ liệu gồm nhiều tài liệu). Ví dụ `chars = sorted(set(text))`, rồi lập `stoi` và `itos`.

- **Ưu điểm:** ngắn gọn, giải mã dễ, không có token ngoài từ vựng nếu tập ký tự đã bao phủ đầu vào; rất hợp để kiểm tra toàn bộ pipeline.
- **Nhược điểm:** chuỗi dài, một từ gồm nhiều bước dự đoán, và không biểu diễn được cấu trúc mảnh từ thường gặp ở LLM hiện đại.
- **Lưu ý:** “ký tự” trong Python thường là code point, không nhất thiết là grapheme người dùng nhìn thấy. Với emoji, dấu kết hợp, hay văn bản đa ngôn ngữ, hãy xác định rõ đơn vị bạn gọi là character.

### BPE: nén các cặp thường gặp thành subword

Byte-pair encoding (BPE) khởi đầu từ đơn vị nhỏ (ký tự hoặc byte), đếm các cặp kề nhau, gộp cặp thường gặp nhất thành token mới, rồi lặp lại đến ngân sách từ vựng. Khi mã hóa, áp dụng lại danh sách merge theo thứ tự đã học. Kết quả thường chứa cả mảnh từ phổ biến lẫn đơn vị nhỏ để ghép từ hiếm.

Ví dụ minh họa, nếu corpus làm cho `t`+`h` rồi `th`+`e` là các merge ưu tiên, `the` có thể trở thành một token. Đây là nén thống kê, không phải phân tích hình thái học hay đảm bảo token trùng với từ.

- BPE giảm số bước chuỗi, nhưng $V$ lớn hơn khiến lớp output $V\times V$ của bigram tăng theo **bình phương** từ vựng. Một bigram BPE 50.000 token cần $2.5$ tỷ logits/weights, không còn là bài tập nhỏ.
- Vì vậy, với bigram hãy dùng character-level, hoặc BPE có từ vựng nhỏ (chẳng hạn vài trăm đến vài nghìn) và corpus vừa phải.
- GPT dùng BPE 40.000 merge.[^radford-generative-pre-training-2018] GPT-2 dùng byte-level BPE với 256 byte cơ sở và từ vựng 50.257 token, cho phép gán xác suất cho mọi chuỗi Unicode mà không cần một `<unk>` riêng.[^radford-gpt-2-2019]

> [!warning] Không tự suy diễn tokenizer
> Chuẩn hóa Unicode, xử lý khoảng trắng, tiền tố từ, byte fallback, special token và thứ tự merge đều thay đổi token IDs. Hai tokenizer cùng gọi là “BPE” có thể mã hóa một câu khác nhau; hãy version hóa tệp tokenizer và thử nghiệm `decode(encode(s))` trên dữ liệu đa dạng.

## 3. Ma trận và tensor: hình học của một bigram

Có hai cách tương đương để biểu diễn bigram.

### Bảng logits trực tiếp

Đặt tham số $W\in\mathbb{R}^{V\times V}$. Hàng $W_i$ chứa logits của token kế tiếp khi token hiện tại là $i$:

$$
z=W_i,\qquad z_j\text{ là điểm chưa chuẩn hóa cho token kế tiếp }j.
$$

Nếu mã hóa input bằng one-hot row vector $e_i\in\mathbb{R}^{1\times V}$, cùng phép tính viết thành:

$$
z=e_iW\in\mathbb{R}^{1\times V}.
$$

Đây là matrix multiplication; do $e_i$ chỉ có một phần tử bằng 1, nó chọn đúng một hàng. Trong framework, `W[input_ids]` hay embedding lookup hiệu quả hơn việc vật hóa one-hot rồi nhân ma trận, nhưng cho cùng kết quả và cùng gradient đối với hàng được chọn.

### Batch và sequence

Với batch $B$ và độ dài block $L$:

| Tensor | Shape | Ý nghĩa |
|---|---:|---|
| `input_ids` | $(B,L)$ | token hiện tại tại từng vị trí |
| `targets` | $(B,L)$ | token kế tiếp đúng, đã shift trái một vị trí |
| `logits` | $(B,L,V)$ | điểm cho mọi token kế tiếp |
| `W` | $(V,V)$ | bảng chuyển tiếp có thể học |

Có thể reshape `logits` thành $(BL,V)$ và `targets` thành $(BL)$ trước khi tính loss. Kiểm tra shape là cách rẻ nhất để phát hiện bạn đảo trục vocabulary, quên shift target, hoặc lấy nhầm chiều softmax.

### Từ bigram đến Transformer

Trong GPT, token ID chọn một **embedding vector** thay vì trực tiếp chọn một hàng logits. Các phép nhân ma trận tiếp theo tạo Q/K/V, MLP và vocab logits. Scaled dot-product attention có dạng

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V,
$$

trong đó mask nhân quả $M$ gán giá trị rất âm cho vị trí tương lai. Transformer gốc mô tả việc chia $QK^\top$ cho $\sqrt{d_k}$ trước softmax và mask các liên kết bất hợp pháp trước softmax.[^vaswani-transformer-2017] Mã GPT tham chiếu cũng thực hiện nhân ma trận, mask tam giác dưới, softmax, rồi nhân trọng số attention với $V$.[^huggingface-openai-gpt-pytorch]

## 4. Softmax: logits thành phân phối xác suất

Logit không phải xác suất: có thể âm, dương, và tổng không bằng 1. Với $z\in\mathbb{R}^V$,

$$
p_j=\operatorname{softmax}(z)_j=\frac{e^{z_j}}{\sum_{k=1}^V e^{z_k}}.
$$

Tính chất quan trọng: $p_j>0$ và $\sum_jp_j=1$. Thêm cùng một hằng số vào tất cả logits không đổi softmax. Vì thế phải tính ổn định số:

$$
\operatorname{softmax}(z)_j=
\frac{e^{z_j-\max_kz_k}}{\sum_ke^{z_k-\max_kz_k}}.
$$

Trừ max không thay đổi kết quả lý thuyết, nhưng tránh `exp(large_number)` tràn số. Thông thường nên gọi `cross_entropy(logits, targets)` của framework thay vì tự làm `softmax`, `log`, rồi cộng: kernel chuẩn thường gộp `log_softmax` và negative-log-likelihood ổn định hơn.

**Nhiệt độ khi sinh** thay đổi độ sắc phân phối: $\operatorname{softmax}(z/\tau)$. $	au<1$ làm tập trung hơn; $	au>1$ làm đa dạng hơn. Nhiệt độ là quy tắc lấy mẫu, không phải loss huấn luyện mặc định.

## 5. Cross-entropy: loss chính là negative log-likelihood

Nếu nhãn đúng ở vị trí đó là $y$, loss một ví dụ là

$$
\ell(z,y)=-\log p_y.
$$

Dùng one-hot vector $\mathbf y$, cùng biểu thức là $-\sum_j y_j\log p_j$. Trung bình trên mọi vị trí hợp lệ là cross-entropy. Tối thiểu hóa nó tương đương tối đa hóa likelihood của dữ liệu token kế tiếp.

Hai phép kiểm tra nên làm ngay:

1. Nếu mọi logit đều bằng nhau, $p_y=1/V$, vì vậy loss phải xấp xỉ $\log V$ (dùng log tự nhiên). Đây là baseline ngẫu nhiên.
2. Perplexity thường được báo cáo là $\exp(\text{mean cross-entropy})$. Nó là số lựa chọn hiệu dụng trung bình theo tokenizer đó, nên không so sánh trực tiếp character-level với BPE khác nhau.

### Gradient then chốt

Đối với softmax + cross-entropy, đạo hàm theo mỗi logit là

$$
\frac{\partial\ell}{\partial z_j}=p_j-y_j.
$$

Vì vậy, token đúng nhận gradient âm nếu xác suất của nó chưa đủ lớn (gradient descent sẽ tăng logit), còn các token sai nhận gradient dương tỉ lệ với xác suất dự đoán (gradient descent sẽ giảm logit). Đây là lời giải thích cơ chế, không phải mẹo cần ghi nhớ: nó cho phép bạn dự đoán chiều cập nhật trong một ví dụ hai lớp.

Với bảng bigram, một ví dụ input $i$, target $y$ chỉ cập nhật hàng $W_i$; các hàng chưa xuất hiện trong batch có gradient bằng 0. Nếu loss không giảm, trước khi đổi kiến trúc hãy kiểm tra target có thực sự là `ids` dịch trái một token không.

## 6. Backpropagation: biến loss thành cập nhật tham số

Forward pass tạo đồ thị các phép toán, loss là một số vô hướng. Backpropagation dùng chain rule để truyền đạo hàm ngược qua đồ thị:

$$
\frac{\partial\ell}{\partial W}
=\frac{\partial\ell}{\partial z}
 \frac{\partial z}{\partial W}.
$$

Autograd thực hiện việc này khi gọi `loss.backward()`. Nó **tích lũy** vào `.grad`; do đó phải `optimizer.zero_grad(set_to_none=True)` (hoặc tương đương) trước mỗi cập nhật nếu không chủ đích gradient accumulation. Quy trình tối thiểu là:

1. lấy `(x, y)`;
2. tính `logits = model(x)` và `loss`;
3. xóa gradient cũ;
4. gọi backward;
5. cập nhật bằng optimizer.

Không gọi `backward()` trên tensor đã detach hoặc bên trong `no_grad()`. Trong validation và generation, dùng `eval()`/`no_grad()` để không tạo activation graph không cần thiết. Với mô hình mini, hãy làm **finite-difference gradient check** cho vài phần tử: so sánh gradient autograd với $(L(w+\epsilon)-L(w-\epsilon))/(2\epsilon)$. Sai khác nhỏ do sai số dấu chấm động là bình thường; sai dấu hoặc sai bậc độ lớn thường báo hiệu bug.

## 7. AdamW: adaptive moments và weight decay tách rời

SGD cơ bản cập nhật $\theta\leftarrow\theta-\eta g$. Adam theo dõi moment bậc một và bậc hai của gradient $g_t$:

$$
m_t=\beta_1m_{t-1}+(1-\beta_1)g_t,\qquad
v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2,
$$

sau đó hiệu chỉnh bias ở đầu quá trình ($\hat m_t,\hat v_t$) và dùng bước theo phần tử. AdamW thêm weight decay **tách khỏi** gradient adaptive:

$$
\theta_t\leftarrow(1-\eta\lambda)\theta_{t-1}
-\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}.
$$

Điểm phân biệt là không cộng $\lambda\theta$ vào gradient rồi để mẫu số Adam tái tỉ lệ nó. Thực tế dùng optimizer AdamW của framework thay vì tự chép công thức.

Quy tắc thực hành cho bài tập:

- Bắt đầu với `AdamW(model.parameters(), lr=...)`, weight decay nhỏ hoặc bằng 0 để cô lập bug; chỉ thêm decay sau khi loop đúng.
- Thường **không** weight-decay bias và các scale/shift của normalization khi có chúng; bigram chỉ có bảng $W$ nên chưa cần tách parameter group phức tạp.
- Log learning rate, training loss, validation loss và gradient norm. Loss `NaN` thường đòi hỏi kiểm tra learning rate, dữ liệu/mask, logits cực trị và mixed precision trước khi kết luận optimizer sai.
- AdamW không bù được nhãn bị shift sai, tokenizer không khớp, hay validation leakage.

Các LLM hiện đại có thể chọn schedule và siêu tham số khác nhau; chẳng hạn tài liệu trong wiki ghi nhận một cấu hình LLaMA sử dụng AdamW với warm-up, cosine decay và gradient clipping, nhưng đó là một cấu hình huấn luyện cụ thể chứ không phải mặc định phổ quát.[^llama-overview]

## 8. Xây dựng mô hình: bản tối thiểu có thể kiểm chứng

### Chuẩn bị dữ liệu

1. Chọn corpus bạn được phép sử dụng, lưu tên/phiên bản và giấy phép.
2. Chia train/validation **theo tài liệu hoặc đoạn lớn trước khi** tạo các cặp; đừng để cửa sổ gần trùng nhau xuất hiện ở cả hai split.
3. Fit tokenizer trên train (hoặc dùng tokenizer có phiên bản cố định), rồi encode cả hai split.
4. Tạo cặp `x = ids[:-1]`, `y = ids[1:]`. Với batch block, lấy những lát liên tiếp cùng độ dài; bigram không dùng ngữ cảnh xa nhưng layout này giữ API tương thích GPT sau này.

### Pseudocode PyTorch

```python
class BigramLM(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.table = nn.Embedding(vocab_size, vocab_size)  # W: (V, V)

    def forward(self, ids, targets=None):
        logits = self.table(ids)             # (B, L, V)
        loss = None
        if targets is not None:
            B, L, V = logits.shape
            loss = F.cross_entropy(logits.reshape(B * L, V), targets.reshape(B * L))
        return logits, loss

for x, y in train_loader:
    _, loss = model(x, y)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
```

`nn.Embedding(V, V)` ở đây là lookup của hàng logits, không phải embedding ngữ nghĩa $d\ll V$ trong Transformer. Đừng nhầm nó với GPT embedding; tên lớp framework giống nhau nhưng mục đích và shape khác.

### Sinh token

Bắt đầu bằng một token `ids`; lặp: lấy `logits[:, -1, :]`, chia nhiệt độ nếu dùng, softmax, rồi `multinomial` để sample token kế tiếp. Bigram chỉ cần token cuối; vẫn giữ interface `(B,L)` để khi thay bằng GPT không cần viết lại sampler.

Để tái lập debugging, cố định random seed và thử hai chế độ:

- `argmax`: xác định, nhanh lộ collapse hoặc indexing sai, nhưng thường lặp.
- sampling: phản ánh phân phối đã học, nhưng đầu ra thay đổi theo seed và nhiệt độ.

## 9. Tiêu chí hoàn thành và chẩn đoán lỗi

| Kiểm tra | Kết quả mong đợi | Nếu thất bại, kiểm tra trước |
|---|---|---|
| `encode`/`decode` | round-trip chính xác trong phạm vi tokenizer | Unicode, special token, byte/chuỗi |
| logits | $(B,L,V)$ | vocab size, lookup, broadcast |
| loss khởi tạo | gần $\log V$ với logits đồng đều | chiều softmax, target range, reduction |
| overfit một batch nhỏ | loss giảm mạnh, sample phản ánh batch | `zero_grad`, `backward`, learning rate, target shift |
| train vs validation | validation không dùng để cập nhật | split trước chunking, `eval`, data leak |
| generation | token ID luôn thuộc $[0,V)$ | softmax chiều cuối, sampler, decode |

> [!tip] Thứ tự debug hiệu quả
> Hãy overfit 1–4 batch trước, rồi corpus nhỏ, rồi mới huấn luyện đầy đủ. Một loss thấp trên train không chứng minh pipeline đúng nếu target vô tình chứa input tại cùng vị trí, hoặc validation bị rò dữ liệu.

## 10. Cầu nối sang GPT nhỏ

Sau khi bigram hoạt động, giữ nguyên tokenizer, shift, cross-entropy, training loop và sampler. Thay model theo ba bước:

1. **Embedding và position:** thay bảng $V\times V$ bằng token embedding $V\times d$ cộng position embedding; điều này cho vector biểu diễn ở mỗi vị trí.
2. **Causal mixing:** thêm decoder blocks để mỗi vị trí kết hợp các token ở bên trái qua masked self-attention và MLP. Perturb một token tương lai không được thay đổi logits ở vị trí trước đó; đây là unit test quan trọng.
3. **Vocabulary head:** chiếu hidden state $(B,L,d)$ thành logits $(B,L,V)$ rồi dùng đúng cross-entropy đã có.

Đó là cùng gia đình mục tiêu với GPT: pre-train decoder-only causal model trên văn bản liên tục, rồi mới xét fine-tuning hay task adaptation.[^radford-generative-pre-training-2018] Transformer gốc có encoder–decoder và cross-attention, nhưng GPT chỉ dùng phần decoder causal; vì vậy đừng sao chép encoder vào “minimal GPT” chỉ vì nó xuất hiện trong sơ đồ Transformer đầu tiên.[^vaswani-transformer-2017]

## 11. Giới hạn của bài tập

Bigram không kiểm tra được attention, positional representation, residual path, normalization, MLP sâu, KV cache, hay năng lực ngữ cảnh dài. Nó cũng không đại diện cho quy mô dữ liệu, compute, đánh giá, bản quyền, an toàn hoặc chi phí của pre-training thực tế. Giá trị của nó là kiểm tra nguyên lý tối ưu hóa và giao diện token-level ở quy mô mà bạn có thể hiểu và đo toàn bộ.

Bước tiếp theo phù hợp là [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md): giữ nguyên logits/cross-entropy nhưng thêm teacher forcing, causal mask và sampler. Sau đó học [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md), [scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md), và [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md). [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) đặt bài tập này ở Stage 1 trước causal LM đầy đủ và attention.

## Relationships

- **Elaborates:** Stage 1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng một bài thực hành và tiêu chí kiểm chứng.
- **Prepares for:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md), [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md), [scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md), và [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md).
- **Uses:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md) để minh họa byte-level BPE.

[^radford-generative-pre-training-2018]: Radford et al., “Improving Language Understanding by Generative Pre-Training” (2018), [PDF](../raw/gpt.pdf), Sections 3–4.
[^radford-gpt-2-2019]: Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), [PDF](../raw/gpt2.pdf), Section 2.2.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), `model_architecture.tex` and `training.tex`.
[^huggingface-openai-gpt-pytorch]: Hugging Face, “PyTorch OpenAI GPT model,” [source](../raw/gpt-source.py), attention implementation.
[^llama-overview]: “LLaMA overview” (Vietnamese summary), [source](../raw/LLaMA.md), “Quy trình tối ưu”. Đây là nguồn tổng quan trong kho, không phải chứng cứ gốc cho công thức AdamW.
