## 1. Bài báo LoRA là gì?

**LoRA: Low-Rank Adaptation of Large Language Models** do Edward Hu và cộng sự giới thiệu năm 2021, sau đó được công bố tại **ICLR 2022**. Mục tiêu của bài báo là giảm mạnh chi phí tinh chỉnh các mô hình ngôn ngữ lớn mà vẫn giữ chất lượng gần bằng hoặc tốt hơn full fine-tuning. ([arXiv][1])

Ý tưởng cốt lõi:

> Không cập nhật toàn bộ trọng số của LLM. Thay vào đó, đóng băng mô hình gốc và chỉ học một phần thay đổi có **hạng thấp** — low rank.

LoRA thuộc nhóm **Parameter-Efficient Fine-Tuning — PEFT**.

---

## 2. Vấn đề của full fine-tuning

Giả sử mô hình có ma trận trọng số:

[
W_0 \in \mathbb{R}^{d \times k}
]

Trong full fine-tuning, toàn bộ (W_0) được cập nhật:

[
W = W_0 + \Delta W
]

Trong đó (\Delta W) có cùng kích thước với (W_0).

Điều này gây ba vấn đề:

1. Phải lưu gradient và trạng thái optimizer cho hàng tỷ tham số.
2. Mỗi tác vụ hoặc khách hàng cần một bản sao gần như đầy đủ của mô hình.
3. Việc chuyển đổi giữa nhiều mô hình đã fine-tune tốn bộ nhớ và tài nguyên triển khai.

Ví dụ, với GPT-3 175B, một bản fine-tune đầy đủ có thể tương ứng với hàng trăm tỷ tham số riêng cho mỗi tác vụ. LoRA được thiết kế trực tiếp để xử lý vấn đề này. ([arXiv][1])

---

## 3. Giả thuyết quan trọng của LoRA

Tác giả giả định rằng:

> Mặc dù mô hình có không gian tham số rất lớn, sự thay đổi cần thiết khi thích nghi sang một tác vụ mới thường nằm trong một không gian có số chiều thấp hơn nhiều.

Nói cách khác, ma trận cập nhật (\Delta W) không nhất thiết phải là một ma trận đầy đủ. Nó có thể được xấp xỉ bằng tích của hai ma trận nhỏ:

[
\Delta W = BA
]

với:

[
B \in \mathbb{R}^{d \times r},
\qquad
A \in \mathbb{R}^{r \times k}
]

và:

[
r \ll \min(d,k)
]

(r) được gọi là **rank**, hay hạng của LoRA.

Trọng số hiệu dụng trở thành:

[
W = W_0 + BA
]

Trong quá trình huấn luyện:

* (W_0) bị đóng băng;
* chỉ (A) và (B) được cập nhật.

Đây là toàn bộ cơ chế nền tảng của LoRA. ([arXiv][1])

---

## 4. Forward pass của LoRA

Với đầu vào (x), lớp tuyến tính thông thường tính:

[
h = W_0x
]

Khi thêm LoRA:

[
h = W_0x + \Delta Wx
]

Thay (\Delta W = BA):

[
h = W_0x + BAx
]

Trong thực tế, LoRA thường sử dụng hệ số scale:

[
h = W_0x + \frac{\alpha}{r}BAx
]

Trong đó:

* (r): rank của adapter;
* (\alpha): hệ số điều chỉnh cường độ LoRA;
* (\alpha/r): hệ số scale.

Có thể hình dung LoRA như một nhánh song song:

```text
                  ┌──────────────┐
x ───────────────►│ Frozen W₀    │─────────┐
│                 └──────────────┘         │
│                                          ├──► h
│                 ┌─────┐    ┌─────┐       │
└────────────────►│  A  │───►│  B  │───────┘
                  └─────┘    └─────┘
                  k → r      r → d
```

Nhánh chính sử dụng trọng số pretrained. Nhánh LoRA học phần hiệu chỉnh cho tác vụ mới.

---

## 5. LoRA giảm bao nhiêu tham số?

Một ma trận đầy đủ:

[
W_0 \in \mathbb{R}^{d \times k}
]

có:

[
dk
]

tham số.

Hai ma trận LoRA có:

[
rk + dr = r(d+k)
]

tham số.

### Ví dụ

Giả sử:

[
d=k=4096
]

Ma trận đầy đủ có:

[
4096 \times 4096 = 16{,}777{,}216
]

tham số.

Nếu dùng LoRA rank (r=8):

[
8(4096+4096)=65{,}536
]

tham số.

Tỷ lệ:

[
\frac{65{,}536}{16{,}777{,}216}
\approx 0.39%
]

Như vậy, với riêng ma trận này, chỉ cần huấn luyện khoảng **0,39%** số tham số.

Mức tiết kiệm toàn mô hình phụ thuộc vào:

* LoRA được gắn vào bao nhiêu lớp;
* gắn vào loại projection nào;
* rank (r);
* kích thước hidden state;
* có huấn luyện thêm bias hoặc embedding hay không.

---

## 6. LoRA được chèn vào đâu trong Transformer?

Một lớp self-attention thường có các phép chiếu:

[
Q=XW_Q
]

[
K=XW_K
]

[
V=XW_V
]

[
O=\text{Attention}(Q,K,V)W_O
]

Trong thí nghiệm chính của bài báo, tác giả tập trung áp dụng LoRA vào các ma trận attention, đặc biệt là:

[
W_Q,\quad W_V
]

Khi đó:

[
W_Q' = W_Q + B_QA_Q
]

[
W_V' = W_V + B_VA_V
]

Các nghiên cứu và triển khai sau này thường thử nhiều cấu hình hơn:

* chỉ (q_proj) và (v_proj);
* (q,k,v,o);
* các lớp MLP như `up_proj`, `down_proj`, `gate_proj`;
* toàn bộ linear layers.

Việc LoRA vào nhiều module hơn thường tăng khả năng thích nghi nhưng cũng làm tăng số tham số và bộ nhớ huấn luyện.

---

## 7. Khởi tạo hai ma trận LoRA

Bài báo sử dụng cách khởi tạo sao cho khi bắt đầu huấn luyện:

[
\Delta W = BA = 0
]

Thông thường:

* (A) được khởi tạo ngẫu nhiên;
* (B) được khởi tạo bằng 0.

Do đó, ở bước đầu tiên:

[
W_0 + BA = W_0
]

Mô hình khởi đầu hoàn toàn giống mô hình pretrained, rồi nhánh LoRA dần học phần hiệu chỉnh.

Điểm này giúp quá trình fine-tuning ổn định hơn vì LoRA không làm thay đổi đầu ra của mô hình ngay khi vừa được chèn vào.

---

## 8. Vì sao low rank có thể hoạt động?

Đây là phần quan trọng nhất về trực giác.

Một ma trận lớn không đồng nghĩa rằng mọi hướng trong không gian tham số đều quan trọng như nhau. Khi mô hình đã được pretrain tốt, việc học một tác vụ mới có thể chỉ cần:

* tăng hoặc giảm một số đặc trưng;
* thay đổi một số quan hệ giữa token;
* dịch chuyển hành vi trong một số ít hướng quan trọng.

Nếu các thay đổi này tập trung trong một không gian con nhỏ, thì:

[
\Delta W
]

có thể có **effective rank** thấp.

LoRA không tuyên bố rằng bản thân trọng số pretrained (W_0) là low rank. Giả thuyết là:

[
\text{phần cập nhật } \Delta W \text{ trong quá trình thích nghi có thể low rank}
]

Đây là một khác biệt rất quan trọng.

Trong phần phân tích thực nghiệm, tác giả nghiên cứu cấu trúc hạng của các cập nhật và quan sát rằng các hướng học được bởi LoRA có tính tập trung đáng kể; tăng rank vượt một mức nhất định thường không đem lại lợi ích tương xứng. ([arXiv][1])

---

## 9. Rank (r) ảnh hưởng thế nào?

Rank quyết định năng lực biểu diễn của adapter.

### Rank nhỏ

Ví dụ:

[
r=1,2,4,8
]

Ưu điểm:

* ít tham số;
* ít bộ nhớ;
* checkpoint nhỏ;
* giảm nguy cơ overfit trong một số tình huống.

Nhược điểm:

* có thể không đủ năng lực cho tác vụ phức tạp;
* khó thay đổi hành vi mô hình sâu hoặc rộng.

### Rank lớn

Ví dụ:

[
r=32,64,128
]

Ưu điểm:

* không gian cập nhật linh hoạt hơn;
* có thể phù hợp với dữ liệu hoặc tác vụ phức tạp.

Nhược điểm:

* tốn bộ nhớ hơn;
* huấn luyện chậm hơn;
* không đảm bảo chất lượng tăng;
* có thể overfit nếu dữ liệu ít.

Một kết luận thực nghiệm đáng chú ý của bài báo là rank rất lớn không phải lúc nào cũng cần thiết. Trong một số thiết lập, rank khá nhỏ vẫn đạt hiệu quả tốt. ([arXiv][1])

---

## 10. Vai trò của (\alpha)

Forward pass thường được viết:

[
h = W_0x+\frac{\alpha}{r}BAx
]

Nếu giữ nguyên (\alpha) nhưng tăng (r), scale của nhánh LoRA sẽ giảm vì chia cho (r).

Ví dụ:

* (r=8,\alpha=16) → scale (=2);
* (r=16,\alpha=16) → scale (=1);
* (r=32,\alpha=16) → scale (=0.5).

(\alpha) không đơn giản là learning rate. Nó scale trực tiếp đóng góp của LoRA trong forward pass.

Trong triển khai thực tế, người ta thường chọn:

[
\alpha \approx r
\quad\text{hoặc}\quad
\alpha \approx 2r
]

nhưng đây là heuristic, không phải quy luật bắt buộc.

---

## 11. Tại sao LoRA tiết kiệm GPU memory?

Trong huấn luyện, bộ nhớ không chỉ dùng để lưu trọng số. Nó còn phải lưu:

* gradient;
* optimizer states;
* activations;
* temporary buffers.

Với Adam, mỗi tham số trainable thường cần thêm các trạng thái moment bậc nhất và bậc hai. Khi đóng băng (W_0), hệ thống không cần lưu gradient và optimizer states cho phần lớn trọng số đó.

Tuy nhiên, LoRA không loại bỏ hoàn toàn chi phí activation. Để tính gradient cho các adapter nằm sâu trong mạng, forward pass vẫn phải đi qua mô hình nền. Vì vậy:

> LoRA giảm rất mạnh bộ nhớ liên quan đến tham số và optimizer, nhưng không làm chi phí huấn luyện tỷ lệ thuận hoàn toàn với phần trăm tham số trainable.

Bài báo báo cáo rằng với GPT-3 175B, LoRA có thể giảm số tham số trainable khoảng **10.000 lần** và giảm yêu cầu GPU memory khoảng **3 lần** so với full fine-tuning bằng Adam trong thiết lập của tác giả. ([arXiv][1])

---

## 12. LoRA có làm chậm inference không?

Trong khi huấn luyện, đầu ra là:

[
h=W_0x+BAx
]

Sau huấn luyện, có thể merge adapter vào trọng số gốc:

[
W_{\text{merged}}
=================

W_0+\frac{\alpha}{r}BA
]

Khi inference:

[
h=W_{\text{merged}}x
]

Như vậy, không cần chạy riêng nhánh (A) và (B). Đây là lý do bài báo nhấn mạnh LoRA có thể không tạo thêm inference latency, khác với một số kiến trúc adapter chèn thêm các tầng tuần tự vào Transformer. ([arXiv][1])

Tuy nhiên, trong hệ thống phục vụ nhiều adapter động, người ta có thể không merge chúng vĩnh viễn. Khi đó vẫn có thêm một lượng tính toán nhỏ hoặc cần runtime chuyên biệt để batch nhiều adapter.

---

## 13. So sánh với các phương pháp khác

### Full fine-tuning

[
\text{Train tất cả } W
]

* khả năng thích nghi cao;
* tốn bộ nhớ;
* checkpoint lớn;
* khó lưu nhiều phiên bản.

### LoRA

[
W=W_0+BA
]

* đóng băng mô hình nền;
* checkpoint nhỏ;
* dễ thay adapter;
* thường đạt chất lượng cạnh tranh;
* bị giới hạn bởi giả định cập nhật low rank.

### Adapter layers

Adapter truyền thống thường thêm một mạng bottleneck vào giữa các tầng:

[
h' = h + W_{\text{up}}\sigma(W_{\text{down}}h)
]

Adapter có activation phi tuyến và nằm tuần tự trong đường forward, nên có thể làm tăng độ trễ inference.

LoRA sửa trực tiếp phép biến đổi tuyến tính và có thể merge vào (W_0).

### Prefix tuning / prompt tuning

Các phương pháp này học vector hoặc token ảo ở phần input hoặc key-value của attention.

* số tham số rất nhỏ;
* không trực tiếp sửa trọng số;
* có thể tiêu tốn một phần context;
* hiệu quả phụ thuộc mạnh vào mô hình và tác vụ.

Bài báo so sánh LoRA với nhiều phương pháp parameter-efficient adaptation và cho thấy LoRA thường đạt kết quả cạnh tranh hoặc tốt hơn trên các thiết lập được đánh giá. ([arXiv][1])

---

## 14. Các mô hình và thí nghiệm trong bài báo

Tác giả đánh giá LoRA trên nhiều họ mô hình, gồm:

* RoBERTa;
* DeBERTa;
* GPT-2;
* GPT-3.

Các tác vụ gồm cả:

* natural language understanding;
* text generation;
* adaptation trên các mô hình có quy mô khác nhau.

Kết luận chính của bài báo là LoRA đạt chất lượng ngang hoặc tốt hơn nhiều baseline fine-tuning/adaptation trong các thí nghiệm của họ, đồng thời dùng ít tham số trainable hơn và không cần thêm độ trễ inference sau khi merge. ([arXiv][1])

Không nên diễn giải điều này thành “LoRA luôn tốt hơn full fine-tuning”. Kết quả phụ thuộc vào:

* mô hình;
* dataset;
* kích thước dữ liệu;
* module được áp dụng;
* rank;
* learning rate;
* mục tiêu huấn luyện.

---

## 15. Ví dụ PyTorch tối giản

Một linear layer LoRA có thể được biểu diễn như sau:

```python
import math

import torch
from torch import nn


class LoRALinear(nn.Module):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 8,
        alpha: float = 16.0,
        bias: bool = True,
    ) -> None:
        super().__init__()

        if rank <= 0:
            raise ValueError("rank must be greater than zero")

        self.rank = rank
        self.scaling = alpha / rank

        # Trọng số mô hình nền.
        self.weight = nn.Parameter(
            torch.empty(out_features, in_features),
            requires_grad=False,
        )

        self.bias = (
            nn.Parameter(torch.zeros(out_features), requires_grad=False)
            if bias
            else None
        )

        # A: in_features -> rank
        self.lora_a = nn.Parameter(torch.empty(rank, in_features))

        # B: rank -> out_features
        self.lora_b = nn.Parameter(torch.zeros(out_features, rank))

        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.lora_a, a=math.sqrt(5))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base_output = nn.functional.linear(
            x,
            self.weight,
            self.bias,
        )

        lora_output = nn.functional.linear(
            nn.functional.linear(x, self.lora_a),
            self.lora_b,
        )

        return base_output + self.scaling * lora_output
```

Vì `lora_b` được khởi tạo bằng 0, lúc đầu:

[
BA=0
]

nên lớp hoạt động giống hệt lớp pretrained.

Mã nguồn chính thức `loralib` của tác giả cung cấp các lớp LoRA cho PyTorch và ví dụ tích hợp với mô hình Hugging Face. ([GitHub][2])

---

## 16. Merge và unmerge

Sau khi huấn luyện:

[
\Delta W=\frac{\alpha}{r}BA
]

Merge:

```python
merged_weight = base_weight + scaling * (lora_b @ lora_a)
```

Unmerge:

```python
base_weight = merged_weight - scaling * (lora_b @ lora_a)
```

Việc này mang lại hai cách triển khai:

### Merge cố định

* thích hợp khi chỉ phục vụ một adapter;
* inference giống mô hình thông thường;
* không thêm phép nhân ma trận riêng.

### Giữ adapter tách biệt

* dễ chuyển tác vụ;
* một base model có thể dùng nhiều adapter;
* cần quản lý adapter và runtime;
* có thể có overhead nhỏ.

---

## 17. Hạn chế của LoRA

### Giới hạn low-rank

Nếu thay đổi cần thiết cho tác vụ có rank cao, (BA) với (r) nhỏ có thể không biểu diễn đủ.

### Khó chọn module mục tiêu

Chỉ áp dụng vào (W_Q,W_V) có thể đủ cho một số tác vụ nhưng không đủ cho tác vụ khác. Thêm MLP projections thường tăng năng lực nhưng cũng tăng chi phí.

### Không tự giải quyết vấn đề dữ liệu

LoRA không khắc phục:

* dữ liệu nhiễu;
* label sai;
* mất cân bằng dữ liệu;
* catastrophic behavior do dataset;
* prompt format không nhất quán.

### Không nhất thiết nhanh hơn tương ứng

Huấn luyện 0,5% tham số không có nghĩa là nhanh hơn 200 lần. Phần lớn forward và backward activation vẫn đi qua Transformer.

### Có thể kém full fine-tuning

Khi có dữ liệu rất lớn, domain shift mạnh hoặc cần thay đổi sâu kiến thức và hành vi, full fine-tuning có thể vượt LoRA.

### Nhiều adapter tạo bài toán vận hành

Mỗi adapter nhỏ, nhưng hàng nghìn adapter vẫn cần:

* versioning;
* routing;
* batching;
* kiểm thử;
* kiểm soát quyền truy cập;
* quản lý base-model compatibility.

---

## 18. LoRA và QLoRA khác nhau thế nào?

LoRA gốc không yêu cầu mô hình nền phải được quantize.

* Base model thường ở FP16, BF16 hoặc FP32.
* Chỉ các ma trận LoRA được huấn luyện.

**QLoRA** là một phương pháp xuất hiện sau này:

* quantize base model, thường xuống 4-bit;
* vẫn huấn luyện LoRA adapters ở độ chính xác cao hơn;
* tiết kiệm thêm bộ nhớ.

Có thể hiểu:

[
\text{QLoRA}
============

\text{quantized frozen base model}
+
\text{LoRA training}
]

Do đó QLoRA không phải là cơ chế được đề xuất trong bài LoRA gốc.

---

## 19. Kết luận chính của bài báo

LoRA thành công nhờ ba lựa chọn đơn giản:

1. **Đóng băng mô hình pretrained.**
2. **Biểu diễn cập nhật bằng hai ma trận hạng thấp.**
3. **Merge cập nhật vào trọng số khi inference.**

Công thức quan trọng nhất là:

[
\boxed{
W' = W_0 + \frac{\alpha}{r}BA
}
]

Trong đó:

* (W_0): trọng số pretrained, không cập nhật;
* (A,B): tham số LoRA;
* (r): rank;
* (\alpha/r): hệ số scale.

Đóng góp lớn nhất của LoRA không phải chỉ là “huấn luyện ít tham số”, mà là chỉ ra rằng **phần thay đổi cần thiết để thích nghi một LLM thường có thể được tham số hóa trong một không gian nhỏ hơn rất nhiều so với toàn bộ mô hình**. Điều này giúp việc lưu, huấn luyện và chuyển đổi giữa nhiều phiên bản chuyên biệt của LLM trở nên thực tế hơn.

[1]: https://arxiv.org/abs/2106.09685?utm_source=chatgpt.com "LoRA: Low-Rank Adaptation of Large Language Models"
[2]: https://github.com/microsoft/LoRA?utm_source=chatgpt.com "Code for loralib, an implementation of \"LoRA: Low-Rank ..."
