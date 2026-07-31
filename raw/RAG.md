## 1. Bài báo RAG gốc

Bài báo thường được xem là nền tảng của RAG có tên:

**“Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks”**
Tác giả chính: Patrick Lewis và cộng sự
Công bố tại **NeurIPS 2020**. ([Proceedings NeurIPS][1])

Mục tiêu của bài báo là kết hợp hai loại “bộ nhớ”:

* **Bộ nhớ tham số — parametric memory:** kiến thức được lưu trong trọng số của mô hình ngôn ngữ.
* **Bộ nhớ phi tham số — non-parametric memory:** kho tài liệu bên ngoài có thể tìm kiếm và thay đổi độc lập với mô hình.

Ý tưởng cốt lõi là:

[
\text{Câu hỏi} \rightarrow \text{Truy xuất tài liệu} \rightarrow
\text{LLM sinh câu trả lời dựa trên tài liệu}
]

Thay vì yêu cầu mô hình phải nhớ toàn bộ kiến thức trong trọng số, RAG cho phép mô hình “tra cứu” trước khi trả lời.

---

## 2. Vấn đề mà bài báo muốn giải quyết

Các mô hình ngôn ngữ tiền huấn luyện có thể lưu rất nhiều kiến thức trong tham số, nhưng tồn tại ba vấn đề chính:

### Kiến thức khó cập nhật

Khi thông tin thế giới thay đổi, chẳng hạn tổng thống, giá sản phẩm hoặc chính sách công ty, việc cập nhật kiến thức trong trọng số thường đòi hỏi huấn luyện lại hoặc fine-tune mô hình.

### Không thể hiện rõ nguồn thông tin

Một mô hình ngôn ngữ thuần túy có thể đưa ra câu trả lời, nhưng khó xác định nó dựa trên tài liệu nào.

### Hallucination

Mô hình có thể tạo ra thông tin có vẻ hợp lý về mặt ngôn ngữ nhưng không đúng sự thật.

Các tác giả đề xuất rằng bộ nhớ bên ngoài có thể được cập nhật, kiểm tra và truy vết dễ dàng hơn bộ nhớ nằm trong trọng số mô hình. 

---

## 3. Kiến trúc RAG trong bài báo

Hệ thống gồm hai thành phần chính.

### 3.1 Retriever — bộ truy xuất

Retriever nhận đầu vào (x), chẳng hạn một câu hỏi, rồi tìm các đoạn văn liên quan nhất trong kho tài liệu:

[
p_\eta(z \mid x)
]

Trong đó:

* (x): câu hỏi hoặc input;
* (z): đoạn tài liệu;
* (\eta): tham số của retriever.

Bài báo sử dụng **Dense Passage Retriever — DPR** với kiến trúc bi-encoder:

[
q(x)=\operatorname{BERT}_{q}(x)
]

[
d(z)=\operatorname{BERT}_{d}(z)
]

Mức độ liên quan giữa câu hỏi và tài liệu được tính bằng tích vô hướng:

[
\operatorname{score}(x,z)=q(x)^\top d(z)
]

Retriever sau đó sử dụng **Maximum Inner Product Search — MIPS** để lấy top-(K) đoạn có điểm cao nhất. 

Điểm đáng chú ý là đây không phải tìm kiếm từ khóa kiểu BM25. Câu hỏi và tài liệu được biểu diễn bằng vector ngữ nghĩa, nên hệ thống có thể tìm được tài liệu liên quan ngay cả khi chúng không dùng đúng những từ giống nhau.

---

### 3.2 Generator — mô hình sinh

Generator nhận:

* câu hỏi (x);
* đoạn tài liệu được truy xuất (z);
* các token đã sinh trước đó.

Sau đó dự đoán token tiếp theo:

[
p_\theta(y_i\mid x,z,y_{1:i-1})
]

Bài báo sử dụng **BART-large**, một mô hình encoder–decoder khoảng 400 triệu tham số. Câu hỏi và đoạn tài liệu được nối lại rồi đưa vào BART. 

Có thể hình dung prompt đầu vào generator như sau:

```text
Question: Ai là tác giả của The Divine Comedy?

Context:
The Divine Comedy is an Italian narrative poem by Dante Alighieri...

Answer:
```

Trong hệ thống RAG hiện đại, generator này thường được thay bằng một LLM lớn hơn như Llama, Mistral, GPT hoặc Gemini. Tuy nhiên, tư tưởng nền tảng vẫn giống bài báo năm 2020.

---

## 4. Tài liệu là biến ẩn

Đóng góp quan trọng của bài báo là coi tài liệu được truy xuất (z) như một **biến ẩn — latent variable**.

Hệ thống không chỉ lấy tài liệu đứng đầu rồi xem nó là chân lý. Thay vào đó, nó lấy nhiều tài liệu top-(K), sinh dựa trên từng tài liệu và tổng hợp xác suất của chúng.

Ở mức trực giác:

[
P(\text{câu trả lời})
=====================

\sum_{\text{tài liệu}}
P(\text{tài liệu}\mid\text{câu hỏi})
\times
P(\text{câu trả lời}\mid\text{câu hỏi, tài liệu})
]

Như vậy, một tài liệu có xác suất truy xuất cao và hỗ trợ tốt cho câu trả lời sẽ đóng góp nhiều hơn vào kết quả cuối cùng.

---

## 5. Hai biến thể: RAG-Sequence và RAG-Token

### RAG-Sequence

RAG-Sequence giả định rằng một tài liệu cụ thể chịu trách nhiệm cho toàn bộ chuỗi đầu ra.

[
p_{\text{RAG-Seq}}(y\mid x)
\approx
\sum_{z\in\operatorname{top-k}}
p_\eta(z\mid x)
\prod_{i=1}^{N}
p_\theta(y_i\mid x,z,y_{1:i-1})
]

Ví dụ, khi trả lời một câu hỏi về Marie Curie, hệ thống có thể chọn một đoạn tiểu sử của bà và sử dụng đoạn đó cho toàn bộ câu trả lời.

**Ưu điểm:** câu trả lời thường nhất quán vì dựa trên cùng một tài liệu.

**Hạn chế:** khó kết hợp thông tin từ nhiều tài liệu khác nhau.

---

### RAG-Token

RAG-Token cho phép mỗi token đầu ra dựa trên một tài liệu khác nhau:

[
p_{\text{RAG-Token}}(y\mid x)
\approx
\prod_{i=1}^{N}
\sum_{z\in\operatorname{top-k}}
p_\eta(z\mid x)
p_\theta(y_i\mid x,z,y_{1:i-1})
]

Điều này cho phép mô hình tổng hợp nội dung từ nhiều đoạn tài liệu trong cùng một câu trả lời.

**Ưu điểm:** linh hoạt hơn trong câu hỏi cần nhiều nguồn.

**Hạn chế:** tính toán phức tạp hơn và có nguy cơ trộn thông tin thiếu nhất quán.

Đây là cách xây dựng xác suất cụ thể của bài báo gốc. Các pipeline RAG phổ biến hiện nay thường đơn giản hơn: lấy vài đoạn văn, nối tất cả vào context rồi gọi LLM một lần.

---

## 6. Dữ liệu và kho tri thức

Bài báo sử dụng Wikipedia tháng 12/2018 làm bộ nhớ ngoài:

* bài viết được chia thành các đoạn khoảng **100 từ**;
* tổng cộng khoảng **21 triệu đoạn**;
* mỗi đoạn được chuyển thành embedding;
* các vector được lập chỉ mục bằng FAISS;
* khi huấn luyện, hệ thống thường lấy top 5 hoặc top 10 tài liệu. 

Quy trình lập chỉ mục gần giống RAG hiện đại:

```text
Wikipedia
    ↓
Chia thành các đoạn
    ↓
Encoder tạo embedding
    ↓
FAISS vector index
    ↓
Tìm top-k đoạn cho mỗi câu hỏi
```

---

## 7. Cách huấn luyện

Retriever và generator được tối ưu chung bằng negative log-likelihood:

[
\mathcal{L}
===========

-\sum_j \log p(y_j\mid x_j)
]

Điểm quan trọng là mô hình không nhất thiết cần nhãn cho biết tài liệu nào phải được truy xuất. Nó chỉ có cặp:

[
(\text{input},\text{output đúng})
]

Gradient từ chất lượng câu trả lời giúp query encoder học cách truy xuất tài liệu hữu ích.

Tuy nhiên, bài báo:

* fine-tune query encoder của DPR;
* fine-tune BART generator;
* giữ nguyên document encoder;
* không cập nhật lại toàn bộ chỉ mục tài liệu trong quá trình huấn luyện.

Lý do là nếu document encoder thay đổi, embedding của hàng triệu đoạn cũng phải được tính lại, gây chi phí rất lớn. 

---

## 8. Các tác vụ được đánh giá

Các tác giả thử nghiệm RAG trên nhiều loại tác vụ cần kiến thức:

### Open-domain Question Answering

* Natural Questions
* TriviaQA
* WebQuestions
* CuratedTREC

Đầu vào là câu hỏi và đầu ra là câu trả lời tự do, không bị giới hạn phải sao chép nguyên văn một span từ tài liệu.

### Abstractive Question Answering

Sử dụng MS MARCO, trong đó mô hình phải tạo câu trả lời dạng câu hoàn chỉnh.

### Jeopardy Question Generation

Cho trước một thực thể hoặc đáp án, mô hình phải sinh ra câu hỏi kiểu Jeopardy chứa thông tin chính xác về thực thể đó.

### Fact Verification

Sử dụng FEVER để phân loại một phát biểu là:

* được hỗ trợ;
* bị bác bỏ;
* không đủ thông tin.

Bài báo nhờ đó chứng minh RAG không chỉ dùng cho hỏi đáp mà còn có thể áp dụng cho sinh văn bản và phân loại dựa trên kiến thức. 

---

## 9. Kết quả chính

Bài báo báo cáo kết quả hàng đầu tại thời điểm đó trên nhiều bộ dữ liệu hỏi đáp mở. Quan trọng hơn, RAG vượt các mô hình chỉ dựa vào kiến thức trong tham số và cạnh tranh tốt với các pipeline retrieve-and-extract chuyên biệt. 

Trong đánh giá con người cho tác vụ sinh câu hỏi Jeopardy:

* RAG được đánh giá **thực tế hơn BART trong 42,7%** trường hợp;
* BART thực tế hơn RAG chỉ trong **7,1%** trường hợp;
* RAG cụ thể hơn trong **37,4%** trường hợp;
* BART cụ thể hơn trong **16,8%** trường hợp. 

RAG cũng sinh văn bản đa dạng hơn. Tỷ lệ trigram khác biệt trên Jeopardy là:

* BART: 32,4%;
* RAG-Token: 46,8%;
* RAG-Sequence: 53,8%. 

Các thí nghiệm ablation cho thấy retriever được học theo tác vụ thường tốt hơn retriever bị đóng băng hoặc truy xuất BM25, mặc dù BM25 vẫn có thể mạnh trong một số bài toán phân loại như FEVER. 

---

## 10. Thí nghiệm cập nhật kiến thức

Một trong những thí nghiệm quan trọng nhất là thay thế chỉ mục Wikipedia theo thời gian.

Các tác giả tạo câu hỏi về những người giữ các chức vụ vào năm 2016 và 2018. Khi sử dụng đúng phiên bản chỉ mục:

* chỉ mục 2016 trả lời đúng khoảng 70% câu hỏi về lãnh đạo năm 2016;
* chỉ mục 2018 trả lời đúng khoảng 68% câu hỏi về lãnh đạo năm 2018.

Khi dùng sai phiên bản chỉ mục, độ chính xác giảm mạnh xuống 12% hoặc 4%. 

Điều này chứng minh một đặc tính rất quan trọng:

> Có thể thay đổi kiến thức của hệ thống bằng cách thay kho tài liệu, mà không nhất thiết phải huấn luyện lại toàn bộ mô hình ngôn ngữ.

Đây cũng là lý do RAG được sử dụng rộng rãi trong hệ thống doanh nghiệp.

---

## 11. Khác biệt giữa RAG trong bài báo và RAG hiện đại

Tên gọi giống nhau nhưng cách triển khai thường khác đáng kể.

| Bài báo RAG 2020                            | RAG ứng dụng hiện đại                           |
| ------------------------------------------- | ----------------------------------------------- |
| DPR làm retriever                           | Nhiều embedding model khác nhau                 |
| BART-large làm generator                    | LLM instruction-tuned                           |
| Wikipedia 21 triệu đoạn                     | PDF, database, wiki nội bộ, web                 |
| Retriever và generator được fine-tune chung | Thường không fine-tune end-to-end               |
| Marginalize xác suất qua tài liệu           | Nối các đoạn vào prompt                         |
| FAISS index                                 | FAISS, Milvus, Qdrant, Elasticsearch, pgvector… |
| Không tập trung vào citation UI             | Thường hiển thị nguồn và đường dẫn              |

Do đó, pipeline phổ biến hiện nay:

```text
Câu hỏi
  ↓
Embedding câu hỏi
  ↓
Vector search
  ↓
Top-k chunks
  ↓
Reranking
  ↓
Ghép context vào prompt
  ↓
LLM sinh câu trả lời
  ↓
Trích dẫn nguồn
```

thực chất là phiên bản kỹ thuật hóa và đơn giản hóa của ý tưởng “parametric memory + non-parametric memory”.

---

## 12. Điểm mạnh của RAG

**Cập nhật kiến thức dễ hơn:** chỉ cần cập nhật tài liệu và index.

**Hỗ trợ dữ liệu riêng:** có thể kết nối LLM với tài liệu doanh nghiệp mà không cần đưa toàn bộ dữ liệu vào quá trình huấn luyện.

**Có khả năng dẫn nguồn:** tài liệu được truy xuất có thể được hiển thị để người dùng kiểm chứng.

**Giảm phụ thuộc vào bộ nhớ tham số:** LLM không cần nhớ chính xác mọi dữ kiện.

**Phù hợp với kiến thức dài và chuyên ngành:** pháp lý, y khoa, kỹ thuật, tài liệu nội bộ, hướng dẫn sản phẩm.

---

## 13. Hạn chế

RAG không tự động loại bỏ hallucination.

### Retriever có thể lấy sai tài liệu

Nếu bằng chứng đúng không nằm trong top-(K), generator khó tạo câu trả lời chính xác.

### Generator có thể bỏ qua tài liệu

LLM có thể dựa vào kiến thức sẵn có hoặc suy diễn trái với context.

### Chunking làm mất ngữ cảnh

Chia tài liệu thành các đoạn nhỏ có thể tách rời bảng biểu, định nghĩa hoặc mối quan hệ giữa nhiều phần.

### Xung đột giữa các nguồn

Nếu các đoạn truy xuất mâu thuẫn, LLM có thể chọn tùy tiện hoặc trộn chúng thành một câu trả lời sai.

### Citation không đồng nghĩa với groundedness

Việc gắn một nguồn cạnh câu trả lời không đảm bảo nguồn đó thực sự hỗ trợ từng phát biểu.

### Độ trễ và chi phí

Embedding, tìm kiếm, reranking và đưa nhiều tài liệu vào context làm tăng thời gian phản hồi và số token.

---

## 14. Ý nghĩa học thuật

Đóng góp lớn nhất của bài báo không đơn thuần là “thêm tìm kiếm trước LLM”. Công trình đã đưa ra một mô hình xác suất thống nhất trong đó:

1. tài liệu là biến ẩn;
2. retriever tạo phân phối xác suất trên tài liệu;
3. generator sinh văn bản có điều kiện trên tài liệu;
4. hai thành phần có thể được tối ưu chung;
5. kiến thức tham số và phi tham số bổ sung cho nhau.

Bài báo đặt nền móng cho một hướng phát triển lớn của LLM: thay vì xây một mô hình phải nhớ mọi thứ, xây một mô hình biết **tìm đúng thông tin, đọc và tổng hợp nó**.

## 15. Tóm tắt một câu

**RAG là kiến trúc kết hợp khả năng diễn đạt và suy luận của mô hình sinh với một kho tri thức bên ngoài có thể tìm kiếm, kiểm tra và cập nhật.**

[1]: https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
