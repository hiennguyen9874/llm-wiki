# QLoRA là gì?

**QLoRA — Quantized Low-Rank Adaptation** là phương pháp fine-tune LLM bằng cách:

1. Nén trọng số của mô hình nền xuống **4-bit**.
2. Đóng băng toàn bộ trọng số nền.
3. Gắn các adapter **LoRA** có kích thước nhỏ.
4. Chỉ cập nhật các adapter trong quá trình huấn luyện.

Bài báo **“QLoRA: Efficient Finetuning of Quantized LLMs”** của Tim Dettmers và cộng sự được công bố tại NeurIPS 2023. Kết quả nổi bật nhất là fine-tune mô hình LLaMA 65B trên một GPU 48 GB, thay vì cần hơn 780 GB bộ nhớ cho full fine-tuning 16-bit. 

---

## 1. Vấn đề mà QLoRA giải quyết

Khi full fine-tune một LLM, bộ nhớ không chỉ dùng để chứa trọng số mà còn phải chứa:

* Gradient.
* Optimizer states.
* Activations.
* Bản sao trọng số phục vụ mixed-precision training.

Ví dụ, riêng trọng số của mô hình 65B ở BF16 đã chiếm khoảng:

[
65 \times 10^9 \times 2\ \text{bytes} \approx 130\text{ GB}
]

Nhưng khi cộng gradient, Adam optimizer states và các cấu trúc trung gian, tổng nhu cầu có thể vượt 780 GB.

LoRA giảm phần gradient và optimizer state bằng cách không cập nhật mô hình nền. Tuy nhiên, mô hình nền 16-bit vẫn phải nằm trong GPU. QLoRA tiếp tục giảm phần này bằng cách lưu mô hình nền ở 4-bit.

---

# 2. QLoRA kết hợp quantization và LoRA như thế nào?

Với một lớp tuyến tính thông thường:

[
Y = XW
]

LoRA thay đổi nó thành:

[
Y = XW + sX L_1 L_2
]

Trong đó:

* (W \in \mathbb{R}^{h \times o}): trọng số pretrained, bị đóng băng.
* (L_1 \in \mathbb{R}^{h \times r}).
* (L_2 \in \mathbb{R}^{r \times o}).
* (r) là rank nhỏ hơn nhiều so với (h) và (o).
* Chỉ (L_1, L_2) được cập nhật.

Ví dụ một ma trận (4096 \times 4096) có khoảng 16,8 triệu tham số. Với LoRA rank (r=16), số tham số bổ sung chỉ là:

[
4096\times16 + 16\times4096 = 131{,}072
]

Tức chưa đến 1% số tham số của ma trận gốc.

Trong QLoRA, (W) không được lưu bằng BF16 mà bằng **NF4**. Khi cần tính toán, trọng số được dequantize tạm thời sang BF16:

[
Y_{\text{BF16}}
===============

X_{\text{BF16}}
\operatorname{dequant}(W_{\text{NF4}})
+
X_{\text{BF16}}L_1^{\text{BF16}}L_2^{\text{BF16}}
]

Điểm quan trọng là:

* **Lưu trữ:** mô hình nền ở 4-bit.
* **Tính toán:** phép nhân ma trận thường thực hiện ở BF16.
* **Gradient:** chỉ được lưu và cập nhật cho các trọng số LoRA.
* QLoRA không trực tiếp cập nhật trọng số 4-bit của mô hình nền. 

Một hiểu nhầm phổ biến là QLoRA thực hiện toàn bộ training bằng số học 4-bit. Thực tế, **4-bit chủ yếu là định dạng lưu trữ trọng số nền**; computation vẫn dùng BF16 hoặc một kiểu 16-bit phù hợp.

---

# 3. Ba đóng góp kỹ thuật chính

## 3.1. NF4 — 4-bit NormalFloat

Quantization thông thường chia miền giá trị thành các khoảng đều nhau. Cách này không lý tưởng đối với trọng số mạng neural vì trọng số thường tập trung quanh 0 và có dạng gần phân phối chuẩn.

NF4 chọn 16 mức biểu diễn sao cho mỗi khoảng quantization chứa xấp xỉ cùng một lượng xác suất dưới phân phối chuẩn.

Nói đơn giản:

* Giá trị gần 0 xuất hiện nhiều → NF4 dành nhiều mức biểu diễn hơn quanh 0.
* Giá trị lớn hiếm hơn → số mức dành cho vùng biên ít hơn.
* Vì thế, NF4 sử dụng hiệu quả 16 giá trị có thể biểu diễn bởi 4 bit.

Quá trình khái quát:

1. Chia tensor thành các block.
2. Với mỗi block, lấy một hệ số scale, thường dựa trên trị tuyệt đối lớn nhất.
3. Chuẩn hóa trọng số về miền ([-1,1]).
4. Ánh xạ từng trọng số vào một trong 16 giá trị NF4 gần nhất.
5. Lưu mã 4-bit và scale của block.

Bài báo gọi NF4 là tối ưu theo lý thuyết thông tin đối với dữ liệu phân phối chuẩn, zero-centered. NF4 cũng có biểu diễn chính xác cho giá trị 0, điều cần thiết đối với padding và các phần tử zero. 

### NF4 khác INT4 thế nào?

INT4 thường có các mức cách đều:

[
-8,-7,\ldots,7
]

Sau khi nhân scale, khoảng cách giữa các mức vẫn đều nhau.

NF4 là kiểu số không đồng đều: khoảng cách giữa các mức nhỏ ở vùng gần 0 và lớn hơn ở vùng xa 0. Điều này phù hợp hơn với phân bố trọng số của LLM.

Trong thí nghiệm của bài báo, perplexity trung bình trên Pile Common Crawl là:

| Kiểu dữ liệu              | Mean perplexity |
| ------------------------- | --------------: |
| INT4                      |           34.34 |
| FP4 E2M1                  |           31.07 |
| FP4 E3M0                  |           29.48 |
| NF4 + Double Quantization |       **27.41** |

Perplexity thấp hơn là tốt hơn. 

---

## 3.2. Double Quantization

Khi quantize theo block, mỗi block cần lưu một scale factor.

Ví dụ:

* Block size: 64 trọng số.
* Mỗi scale được lưu bằng FP32, tức 32 bit.

Chi phí scale trung bình là:

[
\frac{32}{64}=0.5\text{ bit trên mỗi tham số}
]

Như vậy mô hình được gọi là “4-bit” thực tế có thể tốn gần 4.5 bit cho mỗi tham số.

Double Quantization tiếp tục quantize chính các scale factor này:

* Trọng số: NF4 theo block 64.
* Scale cấp 1: quantize xuống FP8.
* Scale cấp 2: FP32, nhưng dùng chung cho một block lớn hơn, chẳng hạn 256 scale.

Chi phí mới:

[
\frac{8}{64}+
\frac{32}{64\times256}
\approx 0.127\text{ bit/tham số}
]

Mức tiết kiệm:

[
0.5-0.127=0.373\text{ bit/tham số}
]

Với mô hình 65B, bài báo ước tính double quantization tiết kiệm khoảng 3 GB. 

---

## 3.3. Paged Optimizers

Trong training, memory không luôn ổn định. Một mini-batch có sequence dài có thể tạo ra đỉnh bộ nhớ, đặc biệt khi dùng gradient checkpointing.

Paged Optimizers dùng **NVIDIA Unified Memory**:

* Optimizer states thường nằm trên GPU.
* Khi GPU gần hết bộ nhớ, một phần state được chuyển sang CPU RAM.
* Khi optimizer update cần đến chúng, dữ liệu được đưa trở lại GPU.

Cơ chế này tương tự virtual-memory paging giữa RAM và ổ đĩa, nhưng ở đây là giữa GPU VRAM và CPU RAM.

Mục tiêu chính không phải giảm bộ nhớ trung bình mà là tránh lỗi **CUDA out of memory** do các đỉnh bộ nhớ nhất thời. Bài báo cho biết paged optimizers là thành phần quan trọng để fine-tune các mô hình 33B và 65B trên GPU 24/48 GB. 

---

# 4. Luồng forward và backward

## Forward pass

Đối với mỗi lớp:

1. Đọc trọng số NF4.
2. Dequantize scale cấp hai.
3. Dequantize scale cấp một.
4. Dequantize trọng số sang BF16.
5. Tính nhánh mô hình nền.
6. Tính nhánh LoRA.
7. Cộng hai kết quả.

[
Y =
XW_{\text{dequantized}}
+
XAB
]

Trong đó (A,B) là các ma trận LoRA.

## Backward pass

Gradient truyền xuyên qua nhánh mô hình nền để tính gradient cho:

* Input của lớp.
* Các adapter LoRA.

Nhưng gradient đối với (W) không được lưu để cập nhật:

[
\frac{\partial \mathcal{L}}{\partial W}
\quad\text{không dùng để update }W
]

Chỉ:

[
\frac{\partial \mathcal{L}}{\partial A},
\quad
\frac{\partial \mathcal{L}}{\partial B}
]

được optimizer sử dụng.

Điều này giải thích vì sao QLoRA có thể giữ mô hình nền dưới dạng quantized và bất biến.

---

# 5. Bộ nhớ được tiết kiệm ở đâu?

Có thể tách bộ nhớ training thành:

[
M =
M_{\text{weights}}
+
M_{\text{gradients}}
+
M_{\text{optimizer}}
+
M_{\text{activations}}
]

### Full fine-tuning

* Weights: toàn bộ mô hình.
* Gradients: toàn bộ mô hình.
* Optimizer states: toàn bộ mô hình.
* Activations: phụ thuộc batch size và sequence length.

### LoRA

* Weights nền: vẫn thường là FP16/BF16.
* Gradients: chỉ cho LoRA.
* Optimizer states: chỉ cho LoRA.
* Activations: vẫn cần.

### QLoRA

* Weights nền: NF4, khoảng 4 bit/tham số cộng metadata.
* Gradients: chỉ cho LoRA.
* Optimizer states: chỉ cho LoRA, có thể paging.
* Activations: BF16, thường kết hợp gradient checkpointing.

Do activations không được nén xuống 4-bit theo cùng cách, sequence length và batch size vẫn có thể làm tăng mạnh VRAM.

---

# 6. Kết quả thực nghiệm chính

Bài báo huấn luyện hơn 1.000 mô hình, từ khoảng 80M đến 65B tham số, trên nhiều kiến trúc và tám bộ dữ liệu instruction tuning. 

## QLoRA so với LoRA 16-bit

Trên LLaMA 7B–65B, fine-tune bằng Alpaca và FLAN v2, kết quả MMLU 5-shot trung bình:

| Phương pháp lưu trọng số | MMLU trung bình |
| ------------------------ | --------------: |
| BF16                     |            53.0 |
| FP4                      |            52.2 |
| NF4 + DQ                 |        **53.1** |

Theo thí nghiệm này, NF4 + Double Quantization đạt kết quả tương đương BF16 LoRA, trong khi FP4 thấp hơn khoảng một điểm phần trăm. 

Cần diễn giải chính xác: bài báo không chứng minh rằng QLoRA luôn ngang full fine-tuning trong mọi bài toán. Nó cho thấy kết quả tương đương trong những thiết lập và benchmark được đánh giá.

---

## Mô hình Guanaco

Nhóm tác giả dùng QLoRA để fine-tune LLaMA trên dữ liệu OpenAssistant OASST1, tạo ra họ mô hình **Guanaco**.

Một số footprint được báo cáo:

| Mô hình     | Dung lượng chạy mô hình |
| ----------- | ----------------------: |
| Guanaco 7B  |             khoảng 5 GB |
| Guanaco 13B |            khoảng 10 GB |
| Guanaco 33B |            khoảng 21 GB |
| Guanaco 65B |            khoảng 41 GB |

Trên benchmark Vicuna, theo đánh giá GPT-4 được dùng trong bài báo:

* Guanaco 65B đạt 99,3% mức điểm của ChatGPT.
* Guanaco 33B đạt 97,8%.
* Guanaco 7B đạt 87,0%. 

Tuy nhiên, đây không nên được hiểu là “Guanaco bằng 99,3% ChatGPT trong mọi khả năng”. Con số chỉ phản ánh một benchmark hội thoại, cách chấm và tập prompt cụ thể. Chính tác giả cũng lưu ý confidence interval rộng và cho rằng các benchmark chatbot thời điểm đó chưa đủ đáng tin cậy. 

---

# 7. Phát hiện quan trọng về dữ liệu

Một kết luận đáng chú ý của bài báo là **chất lượng và độ phù hợp của dữ liệu quan trọng hơn số lượng mẫu đơn thuần**.

Trong thí nghiệm:

* OASST1 có khoảng 9.000 mẫu.
* Một phiên bản FLAN v2 được lấy khoảng 450.000 mẫu.

Dù nhỏ hơn nhiều, OASST1 cho kết quả chatbot tốt hơn. Ngược lại, FLAN v2 có thể phù hợp hơn với các benchmark kiến thức như MMLU.

Điều này cho thấy không tồn tại một bộ instruction data tốt nhất cho mọi mục tiêu:

* Muốn chatbot tự nhiên → cần hội thoại chất lượng.
* Muốn giải bài thi kiến thức → cần dữ liệu tương đồng với bài toán đó.
* Muốn tuân thủ format hoặc thực hiện tác vụ doanh nghiệp → cần dữ liệu sát với workflow thực tế. 

---

# 8. QLoRA không phải là gì?

## Không phải quantization-aware training toàn mô hình

QLoRA không học lại toàn bộ trọng số lượng tử hóa. Base weights vẫn đóng băng.

## Không phải mọi tensor đều ở 4-bit

* Base weights: NF4.
* LoRA adapters: thường BF16.
* Activations: thường BF16.
* Một số optimizer states và scale metadata: 8/16/32-bit.

## Không nhất thiết tăng tốc training

QLoRA chủ yếu tối ưu **memory**. Vì mỗi lần tính toán phải dequantize trọng số, tốc độ có thể thấp hơn LoRA BF16 trong một số hệ thống.

## Không biến mô hình nhỏ thành mô hình lớn

QLoRA giúp fine-tune mô hình lớn với ít phần cứng hơn; nó không bù được giới hạn năng lực của base model.

---

# 9. Hạn chế được chính bài báo nêu ra

Các tác giả thừa nhận:

* Không thể trực tiếp so sánh full fine-tuning 16-bit với QLoRA ở quy mô 33B và 65B vì full fine-tuning quá tốn tài nguyên.
* Chỉ đánh giá một số benchmark như MMLU và các benchmark chatbot; chưa bao phủ BigBench, RAFT, HELM.
* Không khảo sát toàn diện các mức bit khác như 3-bit.
* Không so sánh đầy đủ với các adapter PEFT khác ngoài LoRA.
* Kết quả chatbot phụ thuộc đáng kể vào dữ liệu và phương pháp đánh giá.
* GPT-4-as-a-judge tương quan tương đối với đánh giá con người, nhưng vẫn có trường hợp bất đồng đáng kể. 

---

# 10. Cấu hình QLoRA điển hình hiện nay

Một cấu hình mang tính khởi đầu thường có dạng:

```python
from transformers import BitsAndBytesConfig

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="bfloat16",
)
```

Và LoRA:

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
)
```

Ý nghĩa:

* `load_in_4bit=True`: tải base model ở 4-bit.
* `nf4`: dùng NormalFloat 4.
* `double_quant=True`: quantize cả các scale.
* `bfloat16`: computation dtype.
* `r`: rank của LoRA.
* `lora_alpha`: hệ số scale của update LoRA.
* `target_modules`: các lớp tuyến tính được gắn adapter.

Bài báo nhận thấy việc đặt LoRA vào **tất cả các lớp tuyến tính phù hợp** quan trọng hơn việc chỉ tăng rank. Họ cũng nhận thấy rank ít ảnh hưởng hơn dự kiến khi adapter được áp dụng rộng trên toàn mạng. 

---

# 11. Khi nào nên dùng QLoRA?

QLoRA phù hợp khi:

* GPU không đủ để chạy LoRA BF16.
* Muốn fine-tune mô hình 7B–70B bằng một hoặc vài GPU.
* Cần tạo nhiều adapter cho nhiều khách hàng hoặc domain.
* Muốn giữ nguyên base model và phân phối các adapter nhỏ.
* Bài toán là supervised fine-tuning, instruction tuning hoặc domain adaptation.

LoRA BF16 có thể hợp lý hơn khi:

* GPU dư bộ nhớ.
* Ưu tiên tốc độ training.
* Muốn tránh overhead dequantization.
* Cần kiểm tra tối đa độ ổn định số học.

Full fine-tuning có thể thích hợp khi:

* Có đủ tài nguyên.
* Dữ liệu rất lớn.
* Cần thay đổi sâu kiến thức hoặc hành vi của toàn mô hình.
* LoRA/QLoRA không đạt chất lượng yêu cầu.

---

## Tóm tắt bằng một câu

**QLoRA giữ LLM nền ở NF4 4-bit, dequantize sang BF16 khi tính toán, đóng băng mô hình nền và chỉ huấn luyện các ma trận LoRA; Double Quantization và Paged Optimizers giúp giảm thêm bộ nhớ và tránh các đỉnh OOM.**
