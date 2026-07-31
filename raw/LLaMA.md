## Bài báo LLaMA nói về điều gì?

**LLaMA: Open and Efficient Foundation Language Models** là bài báo do nhóm Meta AI công bố tháng 2/2023. LLaMA viết tắt của **Large Language Model Meta AI**. Công trình giới thiệu một họ mô hình ngôn ngữ nền tảng gồm bốn kích thước: khoảng **7B, 13B, 33B và 65B tham số**. ([arXiv][1])

Luận điểm trung tâm của bài báo là:

> Thay vì chỉ tăng số tham số, có thể huấn luyện một mô hình nhỏ hơn trên lượng dữ liệu lớn hơn để đạt hiệu năng cao, đồng thời giảm chi phí khi triển khai suy luận.

Ví dụ nổi bật là **LLaMA-13B vượt GPT-3 175B trên phần lớn benchmark được thử nghiệm**, mặc dù nhỏ hơn hơn 10 lần; LLaMA-65B đạt mức cạnh tranh với Chinchilla-70B và PaLM-540B. 

---

## 1. Động lực nghiên cứu

Trước LLaMA, xu hướng phổ biến là xây dựng LLM ngày càng lớn, chẳng hạn GPT-3 175B hay PaLM 540B. Tuy nhiên, việc tăng tham số gây ra hai loại chi phí:

* Chi phí huấn luyện rất cao.
* Chi phí suy luận và phục vụ người dùng lâu dài còn cao hơn.

Nhóm tác giả dựa trên kết quả từ nghiên cứu Chinchilla: trong một ngân sách tính toán nhất định, mô hình lớn nhất chưa chắc là lựa chọn tốt nhất; mô hình nhỏ hơn nhưng được huấn luyện bằng nhiều token hơn có thể hiệu quả hơn.

LLaMA điều chỉnh mục tiêu này theo hướng thực dụng hơn: **tối ưu hiệu năng tại một ngân sách suy luận nhất định**, chứ không chỉ tối ưu chi phí huấn luyện. Nhóm nhận thấy LLaMA-7B vẫn tiếp tục cải thiện ngay cả sau khi đã được huấn luyện qua một nghìn tỷ token. 

---

## 2. Dữ liệu tiền huấn luyện

Tập dữ liệu sau tokenization chứa khoảng **1,4 nghìn tỷ token**. Các mô hình 7B và 13B được huấn luyện trên 1,0T token; 33B và 65B dùng 1,4T token. Phần lớn dữ liệu chỉ được đi qua một lần, riêng Wikipedia và sách được sử dụng khoảng hai epoch. 

Cơ cấu dữ liệu:

| Nguồn dữ liệu       | Tỷ lệ |
| ------------------- | ----: |
| English CommonCrawl |   67% |
| C4                  |   15% |
| GitHub              |  4,5% |
| Wikipedia           |  4,5% |
| Gutenberg và Books3 |  4,5% |
| arXiv               |  2,5% |
| Stack Exchange      |    2% |

Điểm tác giả nhấn mạnh là họ chỉ sử dụng những nguồn dữ liệu **có thể truy cập công khai**, thay vì các kho dữ liệu độc quyền không được mô tả rõ. 

Tuy nhiên, “dữ liệu công khai” không đồng nghĩa với dữ liệu hoàn toàn sạch hoặc không có vấn đề bản quyền. Chẳng hạn, Books3 về sau trở thành nguồn dữ liệu gây nhiều tranh luận. Vì vậy, tuyên bố chính xác hơn là LLaMA sử dụng các tập dữ liệu đã có thể truy cập công khai tại thời điểm nghiên cứu, chứ không phải toàn bộ dữ liệu đều thuộc phạm vi công cộng.

### Tiền xử lý dữ liệu

Nhóm thực hiện nhiều bước lọc:

* Loại dữ liệu trùng lặp.
* Phân loại ngôn ngữ và chủ yếu giữ nội dung tiếng Anh.
* Lọc trang web chất lượng thấp bằng mô hình n-gram và heuristic.
* Với GitHub, chỉ giữ các dự án mang giấy phép Apache, BSD hoặc MIT.
* Loại boilerplate, tệp mã nguồn chất lượng thấp và các tệp trùng khớp.
* Với arXiv, xử lý trực tiếp mã LaTeX, bỏ phần tài liệu tham khảo và comment.
* Với sách, loại các cuốn có mức chồng lặp nội dung trên 90%. 

### Tokenizer

LLaMA sử dụng tokenizer **SentencePiece BPE**. Một số lựa chọn đáng chú ý:

* Chia chữ số thành từng chữ số riêng.
* Dùng byte fallback cho những ký tự UTF-8 không nằm trong từ vựng.
* Kích thước từ vựng khoảng 32.000 token.

Byte fallback giúp mô hình không rơi vào trạng thái hoàn toàn không biết một ký tự, nhưng việc chia số thành từng chữ số có thể làm chuỗi số dài hơn.

---

## 3. Kiến trúc mô hình

LLaMA là mô hình **decoder-only Transformer**, được huấn luyện theo mục tiêu causal language modeling:

[
P(x_1,\ldots,x_T)
=================

\prod_{t=1}^{T}P(x_t\mid x_1,\ldots,x_{t-1})
]

Nói đơn giản, mô hình liên tục dự đoán token tiếp theo dựa trên các token đứng trước.

LLaMA không đề xuất một kiến trúc hoàn toàn mới. Điểm mạnh của nó nằm ở việc kết hợp một số cải tiến đã xuất hiện trong các mô hình trước đó.

### Pre-normalization với RMSNorm

Transformer gốc thường chuẩn hóa đầu ra của mỗi khối. LLaMA chuẩn hóa **đầu vào** của mỗi lớp con:

[
h' = h + F(\operatorname{RMSNorm}(h))
]

Cách này giúp quá trình huấn luyện mô hình lớn ổn định hơn.

RMSNorm đơn giản hơn LayerNorm vì không trừ giá trị trung bình:

[
\operatorname{RMSNorm}(x)
=========================

\frac{x}
{\sqrt{\frac{1}{d}\sum_{i=1}^{d}x_i^2+\epsilon}}
\odot g
]

### Hàm kích hoạt SwiGLU

LLaMA thay ReLU/GELU trong feed-forward network bằng **SwiGLU**. Dạng khái quát:

[
\operatorname{FFN}(x)
=====================

\left(\operatorname{SiLU}(xW_1)\odot xW_3\right)W_2
]

SwiGLU cho phép một nhánh đóng vai trò “cổng”, kiểm soát lượng thông tin đi qua. Để cân bằng số tham số, kích thước ẩn của FFN được điều chỉnh về khoảng ( \frac{2}{3}(4d) ), sau đó làm tròn phù hợp với phần cứng.

### RoPE thay embedding vị trí tuyệt đối

LLaMA loại bỏ positional embedding học được và sử dụng **Rotary Positional Embedding – RoPE** trong từng lớp attention.

RoPE quay các thành phần của vector query và key theo góc phụ thuộc vào vị trí. Nhờ đó, tích vô hướng giữa query và key tự nhiên chứa thông tin về khoảng cách tương đối giữa các token.

Ba lựa chọn RMSNorm, SwiGLU và RoPE lần lượt được lấy cảm hứng từ GPT-3, PaLM và GPT-Neo. 

---

## 4. Cấu hình các mô hình

| Phiên bản | Tham số thực | Hidden size | Attention heads | Số lớp | Token huấn luyện |
| --------- | -----------: | ----------: | --------------: | -----: | ---------------: |
| LLaMA 7B  |         6,7B |       4.096 |              32 |     32 |             1,0T |
| LLaMA 13B |        13,0B |       5.120 |              40 |     40 |             1,0T |
| LLaMA 33B |        32,5B |       6.656 |              52 |     60 |             1,4T |
| LLaMA 65B |        65,2B |       8.192 |              64 |     80 |             1,4T |

Tất cả dùng batch size tổng cộng khoảng **4 triệu token**. Learning rate tối đa là (3\times10^{-4}) cho hai mô hình nhỏ và (1,5\times10^{-4}) cho hai mô hình lớn. 

---

## 5. Quy trình tối ưu

Các mô hình được huấn luyện bằng **AdamW**:

[
\beta_1=0.9,\qquad \beta_2=0.95
]

Những thiết lập khác:

* Weight decay: 0,1.
* Gradient clipping: 1,0.
* 2.000 bước warm-up.
* Cosine learning-rate schedule.
* Learning rate cuối bằng 10% learning rate cực đại. 

Nhóm cũng tối ưu hiệu suất bằng:

* Causal multi-head attention tiết kiệm bộ nhớ từ xFormers.
* Activation checkpointing.
* Model parallelism và sequence parallelism.
* Chồng lấp tính toán với giao tiếp giữa các GPU.
* Không lưu toàn bộ ma trận attention bị che bởi causal mask.

Khi huấn luyện LLaMA-65B trên 2.048 GPU A100 80GB, hệ thống xử lý khoảng **380 token/giây/GPU**; huấn luyện qua 1,4T token mất xấp xỉ 21 ngày. 

---

## 6. Phương pháp đánh giá

Bài báo đánh giá mô hình chủ yếu trong hai chế độ:

* **Zero-shot:** chỉ cung cấp mô tả nhiệm vụ hoặc câu hỏi, không cung cấp ví dụ minh họa.
* **Few-shot:** đặt một số ví dụ vào prompt trước câu hỏi cần giải.

Mô hình được kiểm tra trên khoảng 20 benchmark, bao gồm:

* Suy luận thường thức: BoolQ, PIQA, SIQA, HellaSwag, WinoGrande, ARC, OpenBookQA.
* Hỏi đáp kiến thức: NaturalQuestions, TriviaQA.
* Đọc hiểu: RACE.
* Toán: MATH, GSM8K.
* Sinh mã: HumanEval, MBPP.
* Kiến thức đa lĩnh vực: MMLU.
* Độ trung thực: TruthfulQA.
* Độc tính và thiên kiến: RealToxicityPrompts, CrowS-Pairs, WinoGender.

---

## 7. Kết quả quan trọng

### Suy luận thường thức

LLaMA-65B đạt kết quả mạnh trên nhiều tác vụ zero-shot. Ví dụ:

| Benchmark  | GPT-3 175B | LLaMA-13B | LLaMA-65B |
| ---------- | ---------: | --------: | --------: |
| PIQA       |       81,0 |      80,1 |      82,8 |
| HellaSwag  |       78,9 |      79,2 |      84,2 |
| WinoGrande |       70,2 |      73,0 |      77,0 |
| OpenBookQA |       57,6 |      56,4 |      60,2 |

LLaMA-13B vượt GPT-3 trên phần lớn benchmark trong bảng, nhưng không phải trên mọi bài kiểm tra. LLaMA-65B vượt Chinchilla-70B trên hầu hết các benchmark được báo cáo, ngoại trừ BoolQ. 

### Hỏi đáp đóng

Trên NaturalQuestions, LLaMA-65B đạt:

* 23,8 ở zero-shot.
* 31,0 ở one-shot.
* 35,0 ở five-shot.
* 39,9 ở 64-shot.

Kết quả 64-shot gần ngang hoặc nhỉnh hơn PaLM-540B trong thiết lập được báo cáo. 

### Đọc hiểu

Trên RACE-high, LLaMA-65B đạt 51,6, cao hơn PaLM-540B ở mức 49,1. LLaMA-13B cũng đạt kết quả cao hơn GPT-3 trên hai tập RACE được thử nghiệm. 

### Toán học

LLaMA không được fine-tune chuyên biệt cho toán, nhưng LLaMA-65B vẫn đạt kết quả tốt trên GSM8K và trong một số thiết lập vượt Minerva-62B, vốn là mô hình đã được tiếp tục huấn luyện trên dữ liệu toán học. Tuy nhiên, hiệu năng toán tuyệt đối của LLaMA 1 vẫn khá thấp so với các mô hình reasoning hiện đại. 

### Sinh mã

Kết quả pass@1:

| Mô hình   | HumanEval | MBPP |
| --------- | --------: | ---: |
| LLaMA-7B  |      10,5 | 17,7 |
| LLaMA-13B |      15,8 | 22,0 |
| LLaMA-33B |      21,7 | 30,2 |
| LLaMA-65B |      23,7 | 37,7 |
| PaLM-540B |      26,2 | 36,8 |

LLaMA-65B thấp hơn PaLM-540B trên HumanEval pass@1 nhưng nhỉnh hơn trên MBPP. Tác giả lưu ý LLaMA chưa được chuyên biệt hóa cho code. 

### MMLU

Trên MMLU, LLaMA-65B vẫn thấp hơn Chinchilla-70B và PaLM-540B vài điểm. Tác giả cho rằng một nguyên nhân có thể là LLaMA sử dụng lượng sách và tài liệu học thuật ít hơn các đối thủ. 

---

## 8. LLaMA gốc không phải chatbot

Đây là điểm dễ gây nhầm lẫn.

Bài báo LLaMA gốc chủ yếu mô tả **base model được tiền huấn luyện**, không phải trợ lý hội thoại hoàn chỉnh. Base model chỉ học phân phối của văn bản và nhiệm vụ dự đoán token tiếp theo.

Nó chưa được tối ưu đầy đủ để:

* Làm theo chỉ dẫn.
* Hội thoại nhiều lượt.
* Từ chối yêu cầu nguy hiểm.
* Đưa ra câu trả lời hữu ích và có cấu trúc.
* Phù hợp với sở thích của con người.

Bài báo có một thử nghiệm nhỏ về instruction tuning, gọi là **LLaMA-I**, nhưng đây không phải trọng tâm chính. Các kỹ thuật supervised fine-tuning, RLHF và an toàn hội thoại được mô tả chi tiết hơn ở bài báo Llama 2 sau đó. ([Ai Meta][2])

Có thể hình dung quy trình như sau:

[
\text{Base LLaMA}
\xrightarrow{\text{instruction tuning}}
\text{Instruction model}
\xrightarrow{\text{alignment/safety}}
\text{Chat assistant}
]

---

## 9. Hạn chế của công trình

### Hallucination

Trong TruthfulQA, LLaMA tốt hơn GPT-3 ở một số chỉ số, nhưng tỷ lệ trả lời đúng vẫn thấp. Chính tác giả thừa nhận mô hình có khả năng tạo ra câu trả lời sai nghe có vẻ hợp lý. 

### Độc tính và thiên kiến

Dữ liệu web chứa định kiến xã hội, nội dung độc hại và thông tin sai. LLaMA có thể học và tái tạo những vấn đề đó. Các benchmark trong bài chỉ đo được một phần nhỏ rủi ro thực tế.

### Chủ yếu là tiếng Anh

Kho dữ liệu nghiêng mạnh về tiếng Anh. Wikipedia có 20 ngôn ngữ dùng chữ Latin hoặc Cyrillic, nhưng 67% dữ liệu đến từ **English CommonCrawl**. Vì vậy, khả năng đa ngôn ngữ của LLaMA 1 không cân bằng. 

### Context ngắn

LLaMA 1 được huấn luyện với context length 2.048 token, ngắn hơn nhiều so với các LLM hiện đại. Nó không phù hợp để xử lý trực tiếp tài liệu dài nếu không dùng kỹ thuật chia đoạn hoặc retrieval.

### Benchmark contamination

Tác giả tìm kiếm sự trùng lặp giữa dữ liệu huấn luyện và benchmark. Một số tập có mức contamination đáng kể, dù họ nhận thấy tác động tổng thể lên kết quả thường không lớn. Dẫu vậy, việc dữ liệu huấn luyện không được công bố đầy đủ khiến kiểm chứng độc lập khó khăn.

### Chi phí môi trường

Riêng các lần huấn luyện cuối cùng của bốn mô hình sử dụng tổng cộng khoảng 1,77 triệu GPU-giờ theo số liệu trong bảng. LLaMA-65B tiêu thụ khoảng 449 MWh và được ước tính phát thải 173 tCO₂eq trong phép tính chuẩn hóa của bài báo. Khi tính cả quá trình nghiên cứu và thử nghiệm, tác giả ước lượng tổng điện năng khoảng 2.638 MWh và phát thải khoảng 1.015 tCO₂eq. 

---

## 10. Đóng góp quan trọng nhất

Giá trị lớn nhất của bài báo không phải là phát minh ra một loại Transformer hoàn toàn mới. Đóng góp chính nằm ở ba kết luận thực nghiệm:

1. **Dữ liệu huấn luyện nhiều hơn có thể quan trọng hơn việc chỉ tăng tham số.**

2. **Mô hình nhỏ nhưng được huấn luyện đủ lâu có thể cạnh tranh với mô hình lớn hơn nhiều.**
   Điều này làm giảm bộ nhớ và chi phí phục vụ sau khi huấn luyện.

3. **Một foundation model mạnh có thể được xây dựng từ các nguồn dữ liệu công khai.**
   Công trình tạo động lực rất lớn cho hệ sinh thái nghiên cứu và fine-tuning mô hình có trọng số mở.

LLaMA cũng góp phần phổ biến một “công thức kiến trúc” được nhiều LLM sau đó sử dụng:

[
\text{Decoder-only Transformer}
+
\text{RMSNorm}
+
\text{SwiGLU}
+
\text{RoPE}
]

---

## Kết luận

Thông điệp cốt lõi của bài báo LLaMA là:

> Hiệu quả của LLM không chỉ phụ thuộc vào số lượng tham số, mà còn phụ thuộc rất lớn vào lượng dữ liệu, chất lượng dữ liệu và cách phân bổ ngân sách tính toán giữa huấn luyện và suy luận.

LLaMA-13B là minh chứng rõ nhất: một mô hình tương đối nhỏ có thể vượt GPT-3 175B trên nhiều benchmark khi được huấn luyện bằng khoảng một nghìn tỷ token. Tuy nhiên, LLaMA 1 vẫn chỉ là base model, có khả năng hallucination, thiên kiến, context ngắn và chưa được căn chỉnh để trở thành chatbot an toàn. 

[1]: https://arxiv.org/abs/2302.13971?utm_source=chatgpt.com "LLaMA: Open and Efficient Foundation Language Models"
[2]: https://ai.meta.com/research/publications/llama-2-open-foundation-and-fine-tuned-chat-models/?utm_source=chatgpt.com "Llama 2: Open Foundation and Fine-Tuned Chat Models"
