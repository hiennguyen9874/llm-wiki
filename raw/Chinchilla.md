## 1. Bài báo Chinchilla là gì?

**Tên:** *Training Compute-Optimal Large Language Models* — bản NeurIPS có tiêu đề *An Empirical Analysis of Compute-Optimal Large Language Model Training*.

**Tác giả:** Jordan Hoffmann và cộng sự, Google DeepMind. Bài được công bố năm 2022 và nhận giải **Outstanding Main Track Paper tại NeurIPS 2022**. ([arXiv][1])

Câu hỏi trung tâm của bài báo:

> Với một ngân sách tính toán huấn luyện cố định, nên dùng compute để tăng **số tham số** hay để cho mô hình đọc **nhiều token hơn**?

Kết luận nổi tiếng nhất là:

> Các LLM thời đó quá lớn so với lượng dữ liệu chúng được huấn luyện trên. Với cùng ngân sách compute, thường tốt hơn nếu dùng một mô hình nhỏ hơn nhưng huấn luyện trên nhiều token hơn.

---

## 2. Bối cảnh trước Chinchilla

Trước năm 2022, xu hướng phổ biến là:

* Tăng mạnh số tham số (N).
* Giữ lượng dữ liệu huấn luyện (D) quanh vài trăm tỷ token.
* Dựa nhiều vào scaling law của Kaplan và cộng sự.

Ví dụ:

| Mô hình    | Tham số | Token huấn luyện |
| ---------- | ------: | ---------------: |
| GPT-3      |    175B |             300B |
| Jurassic-1 |    178B |             300B |
| Gopher     |    280B |             300B |
| MT-NLG     |    530B |             270B |
| Chinchilla |     70B |      khoảng 1.4T |

Như vậy, GPT-3 chỉ đọc khoảng (1.7) token cho mỗi tham số; Gopher khoảng (1.1) token/tham số. Trong khi đó, Chinchilla đọc khoảng:

[
\frac{1.4\text{T token}}{70\text{B tham số}}\approx 20
]

token cho mỗi tham số. ([ar5iv][2])

Kaplan scaling law trước đó dự đoán rằng khi compute tăng (10\times):

* Kích thước mô hình nên tăng khoảng (5.5\times).
* Dữ liệu chỉ cần tăng khoảng (1.8\times).

Chinchilla cho rằng cách phân bổ này nghiêng quá nhiều về số tham số. ([ar5iv][2])

---

## 3. Phát biểu bài toán toán học

Gọi:

* (N): số tham số của mô hình.
* (D): số token được dùng để huấn luyện.
* (C): ngân sách tính toán, đo bằng FLOPs.
* (L(N,D)): loss cuối cùng của mô hình.

Bài toán tối ưu là:

[
(N_{\mathrm{opt}},D_{\mathrm{opt}})
===================================

\underset{N,D:,\mathrm{FLOPs}(N,D)=C}{\operatorname{argmin}}
L(N,D)
]

Đối với một dense Transformer, paper sử dụng xấp xỉ:

[
C \approx 6ND
]

Hệ số 6 đến từ chi phí gần đúng của forward pass và backward pass trong quá trình huấn luyện. Điều quan trọng không phải chính xác là 6, mà là compute huấn luyện tăng gần tuyến tính theo tích:

[
C \propto N D
]

Vì vậy, với compute cố định:

* Tăng (N) thì phải giảm (D).
* Tăng (D) thì phải giảm (N).

Mục tiêu là tìm điểm cân bằng cho loss thấp nhất. ([ar5iv][2])

---

## 4. Trực giác: hai loại thiếu hụt

Loss của mô hình có thể cao vì hai nguyên nhân khác nhau.

### Mô hình quá nhỏ

Mô hình không có đủ capacity để biểu diễn phân phối ngôn ngữ phức tạp. Ngay cả khi được huấn luyện rất lâu, nó vẫn bị giới hạn bởi số tham số.

### Mô hình chưa được huấn luyện đủ

Mô hình có rất nhiều tham số nhưng chưa nhìn thấy đủ dữ liệu hoặc chưa nhận đủ bước cập nhật để tận dụng capacity đó.

Các mô hình như GPT-3 và Gopher, theo Chinchilla, chủ yếu nằm trong trường hợp thứ hai: **nhiều tham số nhưng quá ít token**.

Nói cách khác, một phần lớn trọng số chưa được “khai thác” hiệu quả trước khi quá trình pretraining kết thúc.

---

## 5. Hàm scaling loss của Chinchilla

Phương pháp thứ ba của paper khớp một hàm loss có dạng:

[
\hat L(N,D)
===========

E+\frac{A}{N^\alpha}+\frac{B}{D^\beta}
]

Trong đó:

* (E): loss không thể loại bỏ, liên quan đến entropy nội tại của dữ liệu ngôn ngữ.
* (\frac{A}{N^\alpha}): phần loss do mô hình có capacity hữu hạn.
* (\frac{B}{D^\beta}): phần loss do chỉ huấn luyện trên lượng dữ liệu hữu hạn.

### Ý nghĩa

Nếu tăng số tham số:

[
N\uparrow
\quad\Rightarrow\quad
\frac{A}{N^\alpha}\downarrow
]

Nếu tăng dữ liệu:

[
D\uparrow
\quad\Rightarrow\quad
\frac{B}{D^\beta}\downarrow
]

Nhưng do (C\approx6ND), không thể tăng cả hai tùy ý khi compute đã cố định. Điểm compute-optimal là điểm cân bằng giữa hai thành phần loss này. ([ar5iv][2])

---

## 6. Suy ra nghiệm compute-optimal

Dưới ràng buộc:

[
C=6ND
]

paper suy ra:

[
N_{\mathrm{opt}}(C)
===================

G\left(\frac{C}{6}\right)^a
]

[
D_{\mathrm{opt}}(C)
===================

G^{-1}\left(\frac{C}{6}\right)^b
]

với:

[
G=
\left(\frac{\alpha A}{\beta B}\right)^{\frac{1}{\alpha+\beta}}
]

[
a=\frac{\beta}{\alpha+\beta},
\qquad
b=\frac{\alpha}{\alpha+\beta}
]

Do hai số mũ thực nghiệm gần nhau, paper thu được xấp xỉ:

[
N_{\mathrm{opt}}\propto C^{0.5}
]

[
D_{\mathrm{opt}}\propto C^{0.5}
]

Nghĩa là khi ngân sách compute tăng (k) lần:

[
N_{\mathrm{opt}}\approx\sqrt{k},N
]

[
D_{\mathrm{opt}}\approx\sqrt{k},D
]

Ví dụ compute tăng (4\times):

[
N\rightarrow2N,\qquad D\rightarrow2D
]

Compute mới là:

[
(2N)(2D)=4ND
]

Đây chính là ý nghĩa của câu “model size và training tokens nên được scale gần như đồng đều”. ([ar5iv][2])

---

## 7. Ba phương pháp thực nghiệm

Nhóm tác giả không chỉ dùng một phép fit. Họ kiểm tra kết luận bằng ba phương pháp.

### Phương pháp 1: cố định kích thước, thay đổi số token

Với mỗi kích thước mô hình, nhóm huấn luyện mô hình trong nhiều khoảng thời gian khác nhau.

Sau đó, ở mỗi mức FLOPs, họ tìm mô hình nào đạt loss thấp nhất. Đường nối các điểm tốt nhất tạo thành **compute-efficient frontier**.

Kết quả:

[
N_{\mathrm{opt}}\propto C^{0.50}
]

[
D_{\mathrm{opt}}\propto C^{0.50}
]

### Phương pháp 2: IsoFLOP profiles

Nhóm chọn chín ngân sách compute cố định. Ở mỗi ngân sách, họ thử nhiều kích thước mô hình.

Do:

[
D=\frac{C}{6N}
]

mỗi lựa chọn (N) tương ứng với một lượng token (D). Loss theo (N) có dạng chữ U:

* Mô hình quá nhỏ: thiếu capacity.
* Mô hình quá lớn: không có đủ token để huấn luyện.
* Điểm đáy: kích thước tối ưu.

Kết quả:

[
N_{\mathrm{opt}}\propto C^{0.49}
]

[
D_{\mathrm{opt}}\propto C^{0.51}
]

### Phương pháp 3: fit hàm loss tham số hóa

Nhóm fit trực tiếp:

[
L(N,D)=E+A/N^\alpha+B/D^\beta
]

Kết quả:

[
N_{\mathrm{opt}}\propto C^{0.46}
]

[
D_{\mathrm{opt}}\propto C^{0.54}
]

Cả ba phương pháp đều cho cùng thông điệp: compute bổ sung nên được chia khá cân bằng giữa tăng tham số và tăng dữ liệu. Trong khi đó, Kaplan scaling law cho các số mũ lần lượt là (0.73) và (0.27), tức ưu tiên tăng model size nhiều hơn. ([ar5iv][2])

---

## 8. Quy tắc “20 token trên mỗi tham số”

Từ các kết quả thực nghiệm, một quy tắc gần đúng thường được gọi là **Chinchilla ratio**:

[
D_{\mathrm{opt}}\approx20N
]

với (N) là số tham số và (D) là số token.

Ví dụ:

| Tham số | Token compute-optimal gần đúng |
| ------: | -----------------------------: |
|    400M |                             8B |
|      1B |                            20B |
|      7B |                    khoảng 140B |
|     10B |                    khoảng 200B |
|     70B |                    khoảng 1.4T |
|    175B |                  khoảng 3.5–4T |
|    280B |                  khoảng 5.6–6T |

Paper dự đoán một mô hình 175B cần vài nghìn tỷ token, còn mô hình 280B cần gần 6–7 nghìn tỷ token để nằm trên compute-optimal frontier. ([ar5iv][2])

Tuy nhiên, **20 token/tham số không phải hằng số vật lý**. Nó phụ thuộc vào:

* Kiến trúc.
* Chất lượng và phân phối dữ liệu.
* Tokenizer.
* Cách đếm tham số.
* Optimizer và learning-rate schedule.
* Miền compute được dùng để ngoại suy.
* Mục tiêu chỉ tối ưu pretraining hay còn tính cả inference.

Nên hiểu đây là một quy tắc thực nghiệm hữu ích, không phải định luật phổ quát tuyệt đối.

---

## 9. Thí nghiệm Chinchilla đối đầu Gopher

Để kiểm chứng scaling law, DeepMind so sánh:

|                    |        Gopher |      Chinchilla |
| ------------------ | ------------: | --------------: |
| Tham số            |          280B |             70B |
| Token              |          300B | khoảng 1.3–1.4T |
| Compute huấn luyện | Gần bằng nhau |   Gần bằng nhau |

Chinchilla:

* Nhỏ hơn (4\times).
* Đọc lượng dữ liệu lớn hơn khoảng (4\times).
* Dùng gần cùng training FLOPs.

Một số nguồn ghi 1.3T và paper/table ghi gần 1.4T; đây chủ yếu là khác biệt do cách làm tròn và cách báo cáo token. ([ar5iv][2])

Kết quả quan trọng là mô hình nhỏ hơn không chỉ đạt loss tốt hơn mà còn vượt Gopher trên phần lớn benchmark được đánh giá.

---

## 10. Kết quả benchmark

### MMLU

Ở thiết lập 5-shot:

| Mô hình    | Accuracy |
| ---------- | -------: |
| GPT-3      |    43.9% |
| Gopher     |    60.0% |
| Chinchilla |    67.6% |

Chinchilla tốt hơn Gopher trên:

* 51/57 tác vụ.
* Bằng nhau trên 2 tác vụ.
* Kém hơn trên 4 tác vụ. ([ar5iv][2])

### BIG-bench

Trung bình trên 62 tác vụ:

* Gopher: 54.4%.
* Chinchilla: 65.1%.

Mức tăng trung bình là 10.7 điểm phần trăm. ([ar5iv][2])

### Reading comprehension

| Benchmark | Chinchilla | Gopher |
| --------- | ---------: | -----: |
| LAMBADA   |       77.4 |   74.5 |
| RACE-m    |       86.8 |   75.1 |
| RACE-h    |       82.3 |   71.6 |

### Closed-book question answering

Trên Natural Questions:

* Chinchilla 5-shot: 31.5%.
* Gopher 5-shot: 24.5%.

Trên TriviaQA unfiltered, 0-shot:

* Chinchilla: 67.0%.
* Gopher: 52.8%.

Các kết quả này ủng hộ luận điểm rằng thêm dữ liệu không chỉ cải thiện next-token loss mà còn chuyển thành cải thiện đáng kể trên downstream tasks. ([ar5iv][2])

---

## 11. Vì sao Chinchilla quan trọng?

### “Nhiều tham số hơn” không đồng nghĩa “mô hình tốt hơn”

So sánh model size chỉ có ý nghĩa khi xem thêm:

* Số token huấn luyện.
* Training compute.
* Chất lượng dữ liệu.
* Kiến trúc.
* Mức độ tối ưu hóa.

Một mô hình 70B được huấn luyện đầy đủ có thể tốt hơn một mô hình 280B bị undertrained.

### Dữ liệu trở thành trục scaling ngang hàng với tham số

Trước Chinchilla, nhiều tổ chức tập trung vào việc làm mô hình lớn hơn. Paper cho thấy việc thu thập, lọc và huấn luyện trên lượng dữ liệu lớn hơn cũng quan trọng không kém.

### Giảm mạnh chi phí inference

Training compute của Chinchilla và Gopher gần bằng nhau, nhưng inference cost phụ thuộc mạnh vào số tham số phải được đọc và xử lý cho mỗi token.

Vì Chinchilla nhỏ hơn (4\times), nó có:

* Memory footprint thấp hơn.
* Latency thấp hơn.
* Chi phí serving thấp hơn.
* Fine-tuning thuận lợi hơn.
* Khả năng chạy trên phần cứng nhỏ hơn.

Đây là lợi ích vượt ra ngoài điểm benchmark. ([Google DeepMind][3])

---

## 12. Compute-optimal không đồng nghĩa deployment-optimal

Đây là một phân biệt rất quan trọng.

Chinchilla tối ưu gần như bài toán:

> Với một ngân sách **pretraining FLOPs cố định**, cấu hình nào cho loss thấp nhất ngay sau khi huấn luyện?

Nhưng trong sản phẩm, tổng chi phí có thể là:

[
C_{\text{total}}
================

C_{\text{training}}
+
C_{\text{inference}}
]

Nếu mô hình sẽ phục vụ hàng nghìn tỷ token inference, chi phí inference có thể lớn hơn training rất nhiều. Khi đó, có thể hợp lý để:

* Chọn mô hình nhỏ hơn.
* Huấn luyện nó trên nhiều token hơn mức Chinchilla-optimal.
* Tốn thêm pretraining compute một lần.
* Đổi lại giảm chi phí cho mỗi request trong suốt vòng đời sản phẩm.

Đây thường được gọi là **overtraining relative to Chinchilla**. “Overtrained” ở đây không nhất thiết có nghĩa là overfitting; nó chỉ có nghĩa là mô hình được huấn luyện trên nhiều token hơn mức tối ưu nếu chỉ xét training compute.

---

## 13. Những giới hạn của paper

Tác giả nêu một số hạn chế đáng chú ý.

### Ngoại suy từ mô hình nhỏ lên quy mô lớn

Hơn 400 thí nghiệm bao phủ mô hình từ khoảng 70M đến trên 16B tham số, nhưng Chinchilla là 70B. Do đó, một phần kết luận ở quy mô lớn dựa trên ngoại suy power law.

Nhóm chỉ có một phép kiểm chứng trực tiếp nổi bật ở quy mô lớn: Chinchilla so với Gopher.

### Giả định power law

Paper giả định quan hệ giữa compute, tham số, dữ liệu và loss có thể được mô tả bằng power law. Tác giả cũng nhận thấy một số độ cong ở mức compute cao, nên các số mũ có thể không hoàn toàn cố định ở mọi quy mô.

### Chủ yếu huấn luyện dưới một epoch

Các run dùng trong scaling analysis chủ yếu chưa đi qua toàn bộ dữ liệu nhiều lần. Kết quả không trực tiếp giải quyết trường hợp thiếu dữ liệu độc nhất và phải lặp dữ liệu qua nhiều epoch.

### Chất lượng dữ liệu chưa được mô hình hóa rõ

Trong công thức, (D) được xem như số token, nhưng 1 tỷ token chất lượng cao không nhất thiết tương đương 1 tỷ token nhiễu hoặc trùng lặp.

### Benchmark contamination

Chinchilla đọc nhiều dữ liệu hơn Gopher, nên xác suất benchmark hoặc nội dung tương tự benchmark xuất hiện trong dữ liệu cũng cao hơn. Paper thừa nhận vấn đề leakage và đặt nhiều trọng số hơn vào các đánh giá ít nhạy với leakage. ([ar5iv][2])

### Scaling không tự động giải quyết an toàn

Mô hình tốt hơn về language modeling vẫn có thể:

* Phản ánh thiên kiến xã hội.
* Sinh nội dung độc hại.
* Ghi nhớ thông tin riêng tư.
* Tái tạo vấn đề từ dữ liệu web.

Trong đánh giá của paper, Chinchilla cải thiện một số phép đo bias so với Gopher nhưng vẫn thể hiện chênh lệch giữa các nhóm; mức toxicity của hai mô hình nhìn chung tương tự nhau. ([ar5iv][2])

---

## 14. Cách hiểu ngắn gọn nhất

Chinchilla không nói rằng:

> Mô hình nhỏ luôn tốt hơn mô hình lớn.

Nó nói rằng:

> Với cùng training compute, mô hình quá lớn nhưng đọc quá ít dữ liệu thường kém hơn một mô hình nhỏ hơn được huấn luyện kỹ hơn.

Ba phương trình cốt lõi là:

[
C\approx6ND
]

[
L(N,D)\approx E+\frac{A}{N^\alpha}+\frac{B}{D^\beta}
]

[
N_{\mathrm{opt}}\propto C^{1/2},
\qquad
D_{\mathrm{opt}}\propto C^{1/2}
]

Và heuristic nổi tiếng:

[
D\approx20N
]

Di sản quan trọng nhất của bài báo là chuyển tư duy thiết kế LLM từ:

> “Có bao nhiêu tham số?”

sang:

> “Với lượng compute và dữ liệu này, tham số và token đã được phân bổ tối ưu chưa?”

[1]: https://arxiv.org/abs/2203.15556?utm_source=chatgpt.com "Training Compute-Optimal Large Language Models"
[2]: https://ar5iv.labs.arxiv.org/html/2203.15556 "[2203.15556] Training Compute-Optimal Large Language Models"
[3]: https://deepmind.google/blog/an-empirical-analysis-of-compute-optimal-large-language-model-training/ "An empirical analysis of compute-optimal large language model training — Google DeepMind"
