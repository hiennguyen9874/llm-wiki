## Tổng quan

**“OPT: Open Pre-trained Transformer Language Models”** là báo cáo kỹ thuật của Meta AI, công bố tháng 5/2022 bởi Susan Zhang và cộng sự. Bài báo giới thiệu **OPT — Open Pre-trained Transformers**, một họ mô hình ngôn ngữ tự hồi quy có quy mô từ **125 triệu đến 175 tỷ tham số**.

Mục tiêu chính không phải tạo ra kiến trúc hoàn toàn mới, mà là:

1. tái tạo năng lực của dòng GPT-3;
2. công khai trọng số, mã nguồn và kinh nghiệm huấn luyện;
3. tạo điều kiện nghiên cứu về độ an toàn, thiên lệch và khả năng tái lập của các mô hình ngôn ngữ rất lớn. ([arXiv][1])

---

## 1. Động lực nghiên cứu

Tại thời điểm đó, các mô hình lớn như GPT-3 chủ yếu chỉ được truy cập qua API. Nhà nghiên cứu không có trọng số mô hình, trạng thái optimizer, mã huấn luyện hoặc nhật ký vận hành nên khó:

* tái lập kết quả;
* phân tích bên trong mô hình;
* nghiên cứu bias, toxicity và robustness;
* thử các phương pháp nén, tinh chỉnh hoặc giải thích mô hình;
* đánh giá chi phí thực tế của việc huấn luyện ở quy mô hàng trăm tỷ tham số.

OPT được xây dựng như một **bản sao mở, gần tương đương GPT-3 về quy mô và chất lượng**, thay vì một nỗ lực đạt trạng thái tốt nhất tuyệt đối.

Điểm quan trọng là chữ **“Open”** trong OPT chủ yếu nói đến việc mở trọng số, mã thực nghiệm và log huấn luyện cho cộng đồng nghiên cứu. Phiên bản 175B ban đầu được cấp quyền có kiểm soát và sử dụng theo giấy phép phi thương mại, nên không hoàn toàn “open source” theo nghĩa phần mềm tự do truyền thống. 

---

## 2. Kiến trúc mô hình

OPT là **decoder-only Transformer**, cùng họ kiến trúc với GPT:

[
P(x_1,\ldots,x_T)=\prod_{t=1}^{T}P(x_t\mid x_1,\ldots,x_{t-1})
]

Mô hình nhận các token trước đó và dự đoán token tiếp theo.

Họ OPT gồm các kích thước:

| Mô hình  | Số lớp | Attention heads | Hidden size |
| -------- | -----: | --------------: | ----------: |
| OPT-125M |     12 |              12 |         768 |
| OPT-350M |     24 |              16 |       1.024 |
| OPT-1.3B |     24 |              32 |       2.048 |
| OPT-2.7B |     32 |              32 |       2.560 |
| OPT-6.7B |     32 |              32 |       4.096 |
| OPT-13B  |     40 |              40 |       5.120 |
| OPT-30B  |     48 |              56 |       7.168 |
| OPT-66B  |     64 |              72 |       9.216 |
| OPT-175B |     96 |              96 |      12.288 |

OPT-175B có kích thước gần với GPT-3 175B. Các siêu tham số phần lớn được lựa chọn để bám sát GPT-3, giúp việc so sánh có ý nghĩa hơn. 

Một số thiết lập chính:

* chiều dài ngữ cảnh: **2.048 token**;
* activation: **ReLU**;
* dropout: **0,1**, không dropout ở embedding;
* tokenizer: **GPT-2 byte-level BPE**;
* optimizer: **AdamW**;
* (\beta_1=0,9), (\beta_2=0,95);
* weight decay: **0,1**;
* gradient clipping thông thường ở mức **1,0**;
* lịch learning rate tuyến tính với warm-up rồi giảm dần.

Khác với nhiều LLM hiện đại, OPT nguyên bản chưa được instruction-tune hay RLHF. Nó là **base language model**, chủ yếu học nhiệm vụ dự đoán token tiếp theo. Vì vậy, nó thường hoàn thành văn bản tốt hơn là trực tiếp tuân thủ mệnh lệnh như chatbot hiện nay.

---

## 3. Dữ liệu tiền huấn luyện

Corpus cuối cùng có khoảng **180 tỷ token**, chủ yếu bằng tiếng Anh. Dữ liệu là sự kết hợp của:

* một số thành phần từng dùng cho RoBERTa:

  * BookCorpus;
  * Stories;
  * CC-News;
* các thành phần được chọn từ The Pile:

  * Common Crawl;
  * DM Mathematics;
  * Project Gutenberg;
  * Hacker News;
  * OpenSubtitles;
  * OpenWebText2;
  * USPTO;
  * Wikipedia;
* dữ liệu hội thoại Reddit từ Pushshift.io.

Nhóm tác giả loại bỏ tài liệu gần trùng nhau bằng MinHashLSH, với ngưỡng Jaccard từ 0,95. Họ lưu ý The Pile chứa khá nhiều bản sao và khuyến nghị các nghiên cứu sau cần khử trùng lặp kỹ hơn. 

### Điểm đáng chú ý

OPT-175B có 175 tỷ tham số nhưng chỉ được huấn luyện trên khoảng 180 tỷ token, tức gần **một token cho mỗi tham số**. Theo quan điểm scaling hiện đại, đây là mức dữ liệu khá thấp. Sau này, các nghiên cứu như Chinchilla cho thấy mô hình có thể đạt hiệu quả tính toán tốt hơn khi dùng nhiều token hơn và ít tham số hơn.

Do đó, OPT-175B là ví dụ tiêu biểu của giai đoạn “mở rộng tham số rất mạnh”, trước khi cộng đồng chuyển sang tối ưu cân bằng giữa kích thước mô hình và lượng dữ liệu.

---

## 4. Hạ tầng và quá trình huấn luyện

OPT-175B được huấn luyện trên **992 GPU NVIDIA A100 80 GB**. Hệ thống kết hợp:

* Fully Sharded Data Parallel;
* Megatron-LM tensor parallelism;
* mixed-precision training;
* phân mảnh tham số, gradient và trạng thái optimizer.

Nhóm tác giả báo cáo mức sử dụng lên tới khoảng **147 TFLOP/s trên mỗi GPU**. 

Một đóng góp thực tế rất đáng giá là **logbook huấn luyện**. Trong đó, tác giả ghi lại:

* lỗi phần cứng;
* máy hoặc GPU hỏng;
* job bị gián đoạn;
* loss spike;
* gradient instability;
* các checkpoint phải khởi động lại;
* những lần thay đổi learning rate hoặc gradient clipping giữa quá trình huấn luyện.

Đây là điểm hiếm gặp trong các bài báo LLM: thay vì trình bày quá trình huấn luyện như một pipeline hoàn hảo, nhóm nghiên cứu công khai các quyết định “mid-flight” và chi phí nhân lực để giữ một job gần 1.000 GPU hoạt động ổn định.

---

## 5. Hiệu năng của OPT

Nhóm tác giả đánh giá OPT trên các tác vụ zero-shot và few-shot tương tự GPT-3, gồm:

* language modeling;
* hoàn thành câu;
* commonsense reasoning;
* reading comprehension;
* question answering;
* natural language inference;
* dialogue.

Kết luận tổng quát là **OPT-175B đạt hiệu năng gần tương đương GPT-3 175B**, nhưng không vượt trội đồng đều trên mọi benchmark. Các mô hình OPT nhỏ cũng thường có xu hướng tương đương với các phiên bản GPT-3 cùng quy mô. ([arXiv][1])

### Đánh giá hội thoại

Dù chưa được fine-tune chuyên biệt cho hội thoại, OPT-175B đạt kết quả khá cạnh tranh với một số chatbot đã được supervised fine-tuning trên các bộ như ConvAI2, Wizard of Wikipedia và Blended Skill Talk.

Tuy nhiên, đây không có nghĩa OPT là chatbot an toàn hoặc đáng tin cậy. Kết quả chủ yếu cho thấy pretraining ở quy mô lớn có thể tự hình thành một số khả năng hội thoại và duy trì persona. 

---

## 6. Đánh giá bias và safety

Một điểm mạnh của bài báo là tác giả không chỉ báo cáo benchmark năng lực, mà còn đánh giá:

* nhận diện hate speech;
* thiên lệch định kiến;
* sinh nội dung độc hại;
* an toàn trong hội thoại.

### Hate-speech detection

Trên bộ ETHOS, OPT-175B đạt F1 cao hơn GPT-3 Davinci trong các thiết lập zero-shot, one-shot và few-shot.

Tuy nhiên, đây là một nghịch lý quan trọng: mô hình nhận diện ngôn ngữ độc hại tốt hơn không có nghĩa nó an toàn hơn. Có thể nó làm tốt vì đã tiếp xúc với nhiều nội dung không được kiểm duyệt trong dữ liệu mạng xã hội. 

### Thiên lệch định kiến

Trên CrowS-Pairs, điểm tổng thể của OPT-175B là **69,5**, so với **67,2** của Davinci; điểm cao hơn ở benchmark này thể hiện thiên lệch lớn hơn. OPT kém hơn ở phần lớn nhóm như giới, chủng tộc, xu hướng tính dục, tuổi và tình trạng kinh tế xã hội.

Nhóm tác giả cho rằng một nguyên nhân có thể là tỷ trọng dữ liệu Reddit, nơi có nhiều biểu đạt mang tính định kiến hoặc phân biệt đối xử. 

Trên StereoSet, hai mô hình có kết quả tổng hợp khá gần nhau; không mô hình nào loại bỏ được vấn đề định kiến. 

### Toxicity

Trên RealToxicityPrompts, OPT-175B có xu hướng tạo phần tiếp nối độc hại **cao hơn cả Davinci và PaLM**. Mức độc hại đầu ra cũng tăng khi prompt đầu vào độc hại hơn. 

Điều này cho thấy đánh đổi giữa:

* khả năng mô hình hóa chính xác ngôn ngữ thực tế trên Internet;
* và việc tạo ra đầu ra phù hợp, an toàn.

Một base model học trực tiếp từ Internet có thể tái tạo cả kiến thức lẫn những đặc điểm xấu của dữ liệu.

---

## 7. Chi phí năng lượng và phát thải

Bài báo ước tính việc phát triển OPT-175B tạo ra khoảng **75 tấn CO₂ tương đương**, so với con số được dẫn lại khoảng:

* GPT-3: 500 tấn;
* Gopher: 380 tấn.

Từ đó, tác giả tuyên bố OPT-175B có footprint phát triển bằng khoảng **1/7 GPT-3**. Nguyên nhân gồm phần cứng A100 thế hệ mới hơn và hệ thống huấn luyện hiệu quả hơn. 

Cần diễn giải thận trọng: đây không nhất thiết là phép so sánh hoàn toàn đồng nhất, vì phương pháp tính carbon giữa các dự án chưa được chuẩn hóa. Con số cũng chủ yếu liên quan đến quá trình phát triển và huấn luyện, chưa phản ánh đầy đủ chi phí inference dài hạn.

---

## 8. Hạn chế của OPT

Chính tác giả thừa nhận OPT-175B:

* không tuân thủ tốt các câu lệnh trực tiếp;
* đôi khi mô phỏng một cuộc hội thoại thay vì thực hiện yêu cầu;
* dễ lặp lại và mắc kẹt trong vòng lặp;
* có thể tạo thông tin sai hoặc “hallucination”;
* chứa và củng cố định kiến xã hội;
* có xu hướng sinh nội dung độc hại;
* không phù hợp để triển khai thương mại hoặc dùng trong môi trường thực tế nhạy cảm mà không có biện pháp giảm thiểu.

Những hạn chế về tuân thủ chỉ dẫn là dễ hiểu vì OPT chưa qua instruction tuning hoặc RLHF. Tác giả trực tiếp đề cập rằng các phương pháp theo hướng InstructGPT có thể cải thiện vấn đề này. 

---

## 9. Đóng góp quan trọng nhất

Giá trị của bài báo không nằm ở một thuật toán Transformer mới. Đóng góp chính là:

**Minh bạch ở quy mô lớn.** OPT cung cấp một trong những bộ trọng số lớn đầu tiên đủ gần GPT-3 để cộng đồng có thể nghiên cứu trực tiếp.

**Một họ mô hình có kiểm soát quy mô.** Các phiên bản từ 125M đến 175B giúp nghiên cứu scaling, pruning, quantization, interpretability và distributed training.

**Công khai quá trình huấn luyện thực tế.** Logbook cho thấy huấn luyện LLM không chỉ là lựa chọn kiến trúc, mà còn là bài toán vận hành hệ thống phân tán đầy lỗi và quyết định ứng biến.

**Đưa safety vào báo cáo chính.** Bias và toxicity không được giấu trong phần phụ; chúng là một phần trung tâm của đánh giá.

**Thúc đẩy hệ sinh thái open-weight.** OPT trở thành nền tảng cho nhiều nghiên cứu về lượng tử hóa, nén mô hình, suy luận phân tán, fine-tuning hiệu quả và instruction tuning.

---

## 10. Cách nhìn phê bình

OPT là một công trình có ảnh hưởng lớn về **open science**, nhưng có ba điểm cần lưu ý:

1. **“Open” vẫn có giới hạn.** Việc phát hành ban đầu áp dụng quyền truy cập và giấy phép hạn chế, đặc biệt với OPT-175B.

2. **Không tái lập hoàn toàn từ dữ liệu gốc.** Trọng số và code được mở, nhưng một số nguồn dữ liệu không thể được tái phân phối đầy đủ; do đó việc huấn luyện lại y hệt vẫn khó.

3. **Mô hình chưa được căn chỉnh.** So sánh trực tiếp OPT với chatbot hiện đại là không công bằng. OPT là base model; nó gần với GPT-3 nguyên bản hơn là ChatGPT, InstructGPT hay các mô hình instruction-tuned sau này.

---

## Kết luận

OPT có thể được hiểu là **một nỗ lực tái tạo GPT-3 theo hướng minh bạch và có thể nghiên cứu được**. Công trình không tạo ra bước nhảy lớn về kiến trúc hay benchmark, nhưng đã chứng minh rằng một mô hình 175B có thể được phát hành cùng code, trọng số, model card và nhật ký huấn luyện.

Thông điệp quan trọng nhất của bài báo là: để hiểu và quản trị rủi ro của LLM, cộng đồng cần quyền tiếp cận trực tiếp với mô hình, chứ không chỉ tương tác qua một API đóng. Đồng thời, kết quả bias và toxicity của OPT cũng cho thấy **mở mô hình không tự động làm mô hình an toàn hơn**; openness chủ yếu tạo điều kiện để các vấn đề đó được kiểm tra và cải thiện.

[1]: https://arxiv.org/abs/2205.01068?utm_source=chatgpt.com "OPT: Open Pre-trained Transformer Language Models"
