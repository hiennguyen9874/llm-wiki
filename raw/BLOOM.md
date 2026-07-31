## BLOOM là gì?

**BLOOM** là viết tắt của **BigScience Large Open-science Open-access Multilingual Language Model**. Đây là mô hình ngôn ngữ lớn với khoảng **176 tỷ tham số**, được phát triển bởi dự án cộng tác quốc tế **BigScience** và công bố năm 2022.

Bài báo chính có tên:

> **“BLOOM: A 176B-Parameter Open-Access Multilingual Language Model”**

Mục tiêu của nhóm không chỉ là tạo ra một mô hình lớn, mà còn thử nghiệm một cách xây dựng LLM **minh bạch, hợp tác và có trách nhiệm hơn** so với mô hình nghiên cứu đóng của các công ty lớn. Hàng trăm nhà nghiên cứu thuộc nhiều lĩnh vực đã tham gia vào quá trình lựa chọn dữ liệu, thiết kế mô hình, huấn luyện, đánh giá và xây dựng giấy phép sử dụng. ([arXiv][1])

---

## 1. Đóng góp chính của bài báo

Bài báo có bốn đóng góp quan trọng:

1. Xây dựng một LLM decoder-only có quy mô **176B tham số**.
2. Huấn luyện mô hình trên tập dữ liệu đa ngữ ROOTS, gồm **46 ngôn ngữ tự nhiên và 13 ngôn ngữ lập trình**.
3. Công khai trọng số, mã nguồn, checkpoint trung gian và tài liệu về quá trình huấn luyện.
4. Đưa các vấn đề đạo đức, quản trị dữ liệu, tác động xã hội và giấy phép sử dụng vào ngay trong quá trình phát triển mô hình.

Điểm thứ tư khá đặc biệt. BLOOM không chỉ là một bài báo về “mô hình đạt điểm bao nhiêu”, mà còn là một nghiên cứu về cách tổ chức một dự án LLM quy mô lớn theo hướng khoa học mở.

---

## 2. Kiến trúc của BLOOM

BLOOM sử dụng kiến trúc **Transformer decoder-only**, tương tự họ GPT.

Điều đó có nghĩa là mô hình nhận một chuỗi token và dự đoán token tiếp theo:

[
P(x_1,\ldots,x_n)
=================

\prod_{t=1}^{n}P(x_t\mid x_1,\ldots,x_{t-1})
]

Hàm mất mát được dùng là cross-entropy cho bài toán next-token prediction:

[
\mathcal{L}
===========

-\frac{1}{T}
\sum_{t=1}^{T}
\log P_\theta(x_t\mid x_{<t})
]

### Thông số của BLOOM-176B

| Thuộc tính                 |                         Giá trị |
| -------------------------- | ------------------------------: |
| Tổng số tham số            |                 176.247.271.424 |
| Số Transformer layer       |                              70 |
| Hidden dimension           |                          14.336 |
| Attention heads            |                             112 |
| Kích thước mỗi head        |                             128 |
| Độ dài ngữ cảnh huấn luyện |                     2.048 token |
| Vocabulary                 |                   250.680 token |
| Kiểu mô hình               | Causal decoder-only Transformer |

Khoảng 3,6 tỷ tham số nằm trong embedding; phần còn lại chủ yếu thuộc các khối attention và feed-forward. ([Hugging Face][2])

### Một số thay đổi so với GPT thông thường

#### ALiBi positional bias

Thay vì positional embedding học được hoặc sinusoidal embedding truyền thống, BLOOM sử dụng **ALiBi — Attention with Linear Biases**.

Trong attention thông thường:

[
\operatorname{Attention}(Q,K,V)
===============================

\operatorname{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}
\right)V
]

Với ALiBi, một bias phụ thuộc vào khoảng cách token được cộng trực tiếp vào attention score:

[
\operatorname{Attention}(Q,K,V)
===============================

\operatorname{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}+B
\right)V
]

Trong đó, với mỗi attention head (h):

[
B_{i,j}^{(h)}=-m_h|i-j|
]

Token càng xa nhau thì bị phạt càng mạnh. Mỗi attention head có một hệ số dốc (m_h) khác nhau, giúp một số head tập trung cục bộ và một số head xử lý quan hệ xa hơn.

Ưu điểm là ALiBi không cần bảng positional embedding riêng và có khả năng ngoại suy sang chuỗi dài hơn tốt hơn một số phương pháp positional embedding tuyệt đối.

#### StableEmbedding

BLOOM áp dụng layer normalization sau word embedding. Thay đổi này được gọi là **StableEmbedding**, nhằm làm quá trình huấn luyện mô hình rất lớn ổn định hơn.

#### Activation

Các lớp feed-forward sử dụng hàm kích hoạt **GELU**.

Nhìn chung, BLOOM không đưa ra một kiến trúc hoàn toàn mới. Giá trị của công trình nằm nhiều hơn ở **quy mô, tính đa ngữ, dữ liệu, kỹ thuật huấn luyện phân tán và quá trình phát triển mở**.

---

## 3. Tokenizer

BLOOM sử dụng **byte-level BPE**, với vocabulary gồm **250.680 token**.

Tokenizer có một số đặc điểm:

* Hoạt động ở mức byte nên có thể biểu diễn gần như mọi chuỗi Unicode.
* Không thực hiện Unicode normalization.
* Được huấn luyện trên dữ liệu lấy mẫu từ nhiều ngôn ngữ.
* Áp dụng alpha-weighting để tránh các ngôn ngữ có nhiều dữ liệu hoàn toàn chi phối vocabulary.

Trong BPE, mô hình bắt đầu với các đơn vị nhỏ rồi liên tục gộp cặp đơn vị xuất hiện thường xuyên:

[
(a,b)\rightarrow ab
]

Quá trình này tạo ra vocabulary chứa cả ký tự, mảnh từ và từ hoàn chỉnh.

Vocabulary của BLOOM lớn hơn đáng kể so với nhiều mô hình chỉ tập trung vào tiếng Anh. Lý do là một tokenizer đa ngữ phải đại diện cho nhiều bảng chữ cái, hệ chữ viết và cấu trúc từ khác nhau. ([Hugging Face][2])

---

## 4. Dữ liệu ROOTS

BLOOM được huấn luyện trên tập dữ liệu **ROOTS**, viết tắt của:

**Responsible Open-science Open-collaboration Text Sources**

ROOTS có dung lượng khoảng **1,6 TB**, tập hợp từ hàng trăm nguồn và bao phủ tổng cộng **59 ngôn ngữ**, gồm:

* 46 ngôn ngữ tự nhiên;
* 13 ngôn ngữ lập trình.

Phiên bản dữ liệu sau tiền xử lý tương ứng với khoảng **350 tỷ token duy nhất**; trong toàn bộ quá trình huấn luyện, BLOOM đã nhìn thấy khoảng **366 tỷ token**. ([arXiv][3])

### Các nhóm ngôn ngữ

ROOTS không chỉ chứa các ngôn ngữ phổ biến như tiếng Anh, tiếng Pháp, tiếng Tây Ban Nha, tiếng Trung hay tiếng Ả Rập mà còn có dữ liệu từ:

* Các ngôn ngữ Niger–Congo;
* Các ngôn ngữ Ấn Độ;
* Các ngôn ngữ châu Âu;
* Một số ngôn ngữ có tài nguyên thấp;
* Mã nguồn thuộc nhiều ngôn ngữ lập trình.

Tuy nhiên, “hỗ trợ 46 ngôn ngữ” không có nghĩa chất lượng của mọi ngôn ngữ là ngang nhau. Ngôn ngữ có ít dữ liệu vẫn có thể cho kết quả kém, không ổn định hoặc dễ chuyển sang ngôn ngữ khác.

### Dữ liệu lập trình

Corpus chứa mã nguồn như:

* Java;
* PHP;
* C và C++;
* Python;
* JavaScript;
* C#;
* Ruby;
* Go;
* TypeScript;
* Rust;
* Scala và một số ngôn ngữ khác.

Mã nguồn giúp BLOOM có khả năng sinh code nhất định, nhưng BLOOM không được tối ưu riêng cho lập trình như các code model chuyên dụng.

### Quy trình quản trị dữ liệu

Một đóng góp đáng chú ý của ROOTS là nhóm nghiên cứu không chỉ “crawl toàn bộ web”. Họ xây dựng data governance theo hướng:

* Làm việc với các chuyên gia và cộng đồng ngôn ngữ;
* Ghi lại nguồn và đặc tính của từng tập dữ liệu;
* Thảo luận về quyền riêng tư, bản quyền và sự đồng thuận;
* Loại bỏ một phần nội dung không phù hợp;
* Phân tích sự mất cân bằng giữa các ngôn ngữ và khu vực.

Dù vậy, ROOTS vẫn có thể chứa thông tin cá nhân, định kiến, nội dung độc hại hoặc dữ liệu có nguồn gốc chưa hoàn toàn rõ ràng. Chính nhóm tác giả cũng xem đây là một hạn chế chứ không tuyên bố dữ liệu đã “sạch hoàn toàn”.

---

## 5. Quá trình huấn luyện

BLOOM được huấn luyện trên siêu máy tính công cộng **Jean Zay** tại Pháp.

Hạ tầng chính gồm:

* 384 GPU NVIDIA A100 80 GB được sử dụng thường xuyên;
* 32 GPU A100 bổ sung làm tài nguyên dự phòng;
* 48 node chính, mỗi node có 8 GPU;
* Kết nối GPU nội bộ bằng NVLink;
* Huấn luyện phân tán bằng Megatron-DeepSpeed.

Checkpoint chỉ chứa trọng số BF16 có kích thước khoảng **329 GB**. Checkpoint đầy đủ, gồm optimizer state, có thể lên đến khoảng **2,3 TB**. ([Hugging Face][2])

### Song song hóa

Một mô hình 176B không thể đặt trên một GPU. BLOOM kết hợp nhiều dạng phân tán:

#### Data parallelism

Mỗi nhóm GPU xử lý các batch dữ liệu khác nhau rồi đồng bộ gradient.

#### Tensor parallelism

Các phép nhân ma trận bên trong một layer được chia nhỏ giữa nhiều GPU.

Ví dụ:

[
Y=XW
]

Ma trận (W) có thể được chia thành:

[
W=[W_1,W_2,\ldots,W_p]
]

Mỗi GPU tính một phần:

[
Y_i=XW_i
]

#### Pipeline parallelism

70 layer được chia thành nhiều stage. Micro-batch lần lượt đi qua các stage theo pipeline.

#### ZeRO

DeepSpeed ZeRO phân chia optimizer state, gradient và trong một số cấu hình cả tham số giữa các GPU, giúp giảm bộ nhớ trùng lặp.

### Độ chính xác số

BLOOM được huấn luyện chủ yếu bằng **BF16**. BF16 có số bit exponent tương tự FP32 nên thường ổn định hơn FP16 đối với huấn luyện mô hình rất lớn, trong khi vẫn tiết kiệm đáng kể bộ nhớ và tăng tốc tính toán.

---

## 6. BLOOM được đánh giá như thế nào?

Bài báo đánh giá BLOOM trên nhiều nhóm nhiệm vụ:

* Language modeling;
* Zero-shot và few-shot prompting;
* Question answering;
* Reading comprehension;
* Natural language inference;
* Text completion;
* Machine translation;
* Code generation;
* Bias và toxicity.

### Kết quả tổng quát

BLOOM đạt hiệu năng cạnh tranh với một số mô hình decoder-only cùng thời kỳ, đặc biệt trong các ngôn ngữ mà nó được huấn luyện tốt.

Tuy nhiên, BLOOM cơ sở không phải lúc nào cũng vượt GPT-3, OPT hoặc các mô hình chuyên biệt. Kết quả phụ thuộc mạnh vào:

* Ngôn ngữ;
* Cách viết prompt;
* Số lượng few-shot examples;
* Kích thước phiên bản BLOOM;
* Mức độ xuất hiện của ngôn ngữ và miền dữ liệu trong ROOTS.

Một phát hiện quan trọng là **multitask prompted fine-tuning** giúp hiệu năng tốt hơn rõ rệt. Phiên bản liên quan thường được biết đến dưới tên **BLOOMZ**.

Có thể hiểu:

[
\text{BLOOM}
\xrightarrow{\text{multitask instruction tuning}}
\text{BLOOMZ}
]

BLOOM chủ yếu được pretrained để dự đoán token tiếp theo, còn BLOOMZ được tinh chỉnh để hiểu và làm theo instruction tốt hơn.

---

## 7. Zero-shot và few-shot

Mặc dù BLOOM thể hiện khả năng zero-shot, nó vẫn là một **base language model**, không phải chatbot đã được instruction-tuned.

Ví dụ, đưa prompt:

```text
Translate English to French:
The weather is beautiful today =>
```

mô hình có thể học cấu trúc từ prompt và tiếp tục bằng bản dịch.

Trong few-shot prompting:

```text
English: Good morning
French: Bonjour

English: Thank you
French: Merci

English: I love this book
French:
```

các ví dụ giúp mô hình xác định rõ hơn nhiệm vụ, ngôn ngữ đầu ra và định dạng mong muốn.

Các nghiên cứu sau đó cho thấy BLOOM có thể gặp hiện tượng:

* Sinh quá dài;
* Lặp lại prompt;
* Dịch sang sai ngôn ngữ;
* Tiếp tục sinh nhiều ví dụ không được yêu cầu.

Các vấn đề này giảm đáng kể khi sử dụng few-shot examples hoặc instruction tuning. ([arXiv][4])

---

## 8. Ý nghĩa của BLOOM đối với cộng đồng LLM

### Mở trọng số ở quy mô rất lớn

Tại thời điểm công bố, một mô hình 176B tham số có trọng số được cung cấp công khai là một bước tiến lớn. Trước đó, nhiều mô hình lớn chỉ có API hoặc mô tả trong bài báo.

Việc mở BLOOM cho phép cộng đồng nghiên cứu:

* Phân tích activation và attention;
* Nghiên cứu quantization;
* Fine-tune mô hình;
* Đánh giá bias và toxicity;
* Nghiên cứu multilingual transfer;
* Thử nghiệm distributed inference;
* Kiểm tra tác động của dữ liệu và quy mô.

### Công khai checkpoint trung gian

Nhóm phát hành các checkpoint theo từng giai đoạn huấn luyện. Điều này cho phép nghiên cứu cách năng lực của LLM hình thành theo thời gian:

[
\theta_{5k},\theta_{10k},\theta_{15k},\ldots,\theta_{95k}
]

Chẳng hạn, nhà nghiên cứu có thể kiểm tra tại bước nào mô hình bắt đầu có khả năng dịch, làm toán đơn giản hoặc sinh code.

### Khoa học mở nhưng không hoàn toàn “open source”

BLOOM thường được gọi là open-access, nhưng giấy phép của nó có các hạn chế về mục đích sử dụng. Vì thế, tùy định nghĩa, BLOOM không nhất thiết đáp ứng mọi tiêu chí của phần mềm nguồn mở truyền thống.

Trọng số được phát hành theo **Responsible AI License — RAIL**, trong đó cấm hoặc hạn chế các ứng dụng gây hại như:

* Theo dõi không có sự đồng thuận;
* Mạo danh;
* Phát tán thông tin sai lệch;
* Quấy rối;
* Phân biệt đối xử;
* Một số hoạt động ra quyết định rủi ro cao.

---

## 9. Hạn chế

### Không phải mô hình hội thoại

BLOOM gốc chỉ được tối ưu cho next-token prediction. Nó có thể không làm theo lệnh tốt và đôi khi chỉ tiếp tục văn bản của người dùng.

### Hallucination

Mô hình có thể tạo ra thông tin nghe hợp lý nhưng sai. Model card không khuyến nghị dùng BLOOM trực tiếp cho các quyết định y tế, pháp lý, tài chính hoặc các ứng dụng ảnh hưởng nghiêm trọng đến con người. ([Hugging Face][2])

### Mất cân bằng đa ngữ

Số lượng dữ liệu giữa các ngôn ngữ chênh lệch lớn. Các ngôn ngữ ít dữ liệu không nhận được cùng mức chất lượng với các ngôn ngữ giàu tài nguyên.

### Context ngắn theo tiêu chuẩn hiện nay

Độ dài huấn luyện 2.048 token từng là phổ biến năm 2022, nhưng khá ngắn so với các LLM hiện đại có context hàng chục nghìn hoặc hàng trăm nghìn token.

### Chi phí suy luận lớn

Riêng trọng số BF16 khoảng 329 GB. Chỉ để lưu trọng số đã cần nhiều GPU:

[
176\text{B parameters}\times 2\text{ bytes}
\approx 352\text{ GB}
]

Chênh lệch với kích thước thực tế đến từ cách đếm tham số, định dạng lưu trữ và chia sẻ embedding.

Quantization 8-bit hoặc 4-bit có thể giảm bộ nhớ lý thuyết xuống khoảng:

[
176\text{ GB ở 8-bit}
]

và:

[
88\text{ GB ở 4-bit}
]

nhưng vẫn cần hạ tầng mạnh, đồng thời có thể làm giảm chất lượng hoặc tốc độ tùy phương pháp.

### Dữ liệu độc hại và định kiến

BLOOM có thể:

* Sinh nội dung thù ghét hoặc xúc phạm;
* Tái tạo stereotype;
* Phản ánh quan điểm chiếm ưu thế trong dữ liệu;
* Làm lộ hoặc tái tạo một phần thông tin cá nhân;
* Tạo nội dung sai nhưng thể hiện với giọng tự tin.

Những rủi ro này được ghi thẳng trong model card thay vì chỉ được đề cập sơ lược. ([Hugging Face][2])

---

## 10. BLOOM khác gì GPT-3?

| Tiêu chí             | BLOOM                                      | GPT-3                                         |
| -------------------- | ------------------------------------------ | --------------------------------------------- |
| Quy mô               | 176B                                       | 175B                                          |
| Kiến trúc            | Decoder-only                               | Decoder-only                                  |
| Đa ngữ               | Thiết kế đa ngữ có chủ đích                | Dữ liệu thiên mạnh về tiếng Anh               |
| Trọng số             | Công khai có điều kiện                     | Không công khai                               |
| Dữ liệu              | ROOTS được tài liệu hóa tương đối chi tiết | Không công khai đầy đủ                        |
| Positional mechanism | ALiBi                                      | Learned positional embedding                  |
| Giấy phép            | RAIL có hạn chế sử dụng                    | Truy cập chủ yếu qua dịch vụ thương mại       |
| Mục tiêu dự án       | Khoa học mở và cộng tác                    | Mô hình nghiên cứu/thương mại của một tổ chức |

Về kiến trúc cốt lõi, BLOOM không khác GPT-3 một cách cách mạng. Khác biệt lớn nhất là **triết lý phát triển, tính đa ngữ, khả năng tiếp cận và mức độ tài liệu hóa**.

---

## 11. Kết luận quan trọng nhất của bài báo

Thông điệp chính của BLOOM không phải là:

> “Chúng tôi tạo ra mô hình tốt nhất.”

Mà gần hơn với:

> “Một cộng đồng nghiên cứu quốc tế có thể cùng xây dựng, tài liệu hóa và công khai một LLM quy mô tương đương các mô hình lớn của doanh nghiệp.”

Về mặt kỹ thuật, BLOOM là một decoder-only Transformer lớn, dùng ALiBi, StableEmbedding, tokenizer đa ngữ và huấn luyện phân tán trên 384 GPU A100.

Về mặt khoa học, đóng góp lớn hơn nằm ở:

* ROOTS và quy trình xây dựng dữ liệu đa ngữ;
* Mô hình cộng tác BigScience;
* Công khai trọng số và checkpoint;
* Model card chi tiết;
* Đưa đạo đức và quản trị vào vòng đời xây dựng LLM;
* Tạo nền tảng cho các mô hình sau này như BLOOMZ.

BLOOM vì thế là một công trình quan trọng trong lịch sử LLM mở, mặc dù chất lượng hiện nay đã bị nhiều mô hình nhỏ hơn, mới hơn và được instruction-tune tốt hơn vượt qua.

[1]: https://arxiv.org/abs/2211.05100?utm_source=chatgpt.com "BLOOM: A 176B-Parameter Open-Access Multilingual Language Model"
[2]: https://huggingface.co/bigscience/bloom "bigscience/bloom · Hugging Face"
[3]: https://arxiv.org/abs/2303.03915?utm_source=chatgpt.com "The BigScience ROOTS Corpus: A 1.6TB Composite Multilingual Dataset"
[4]: https://arxiv.org/abs/2303.01911?utm_source=chatgpt.com "Investigating the Translation Performance of a Large Multilingual Language Model: the Case of BLOOM"
