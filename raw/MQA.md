## 1. MQA là gì?

**Multi-Query Attention — MQA** được Noam Shazeer giới thiệu trong bài:

> **Fast Transformer Decoding: One Write-Head is All You Need** — 2019.

Mục tiêu chính không phải làm phép attention ít tính toán hơn đáng kể, mà là giảm lượng dữ liệu **Key/Value phải đọc từ bộ nhớ trong quá trình sinh token tự hồi quy**. Bài báo nhận thấy decoding Transformer thường bị giới hạn bởi **băng thông bộ nhớ**, đặc biệt khi phải liên tục tải lại KV cache ở từng layer và từng bước sinh token. ([arXiv][1])

Điểm cốt lõi:

* **Multi-Head Attention — MHA:** mỗi query head có một bộ Key và Value riêng.
* **Multi-Query Attention — MQA:** vẫn có nhiều query head, nhưng tất cả dùng chung **một Key head và một Value head**.

Vì vậy, tên “Multi-Query” nên được hiểu là:

> Nhiều query heads truy vấn cùng một bộ Key/Value.

Chứ không phải “một head chứa nhiều query”.

---

## 2. Nhắc lại Multi-Head Attention

Giả sử mô hình có:

* hidden dimension: (d_{\text{model}})
* số query heads: (H)
* kích thước mỗi head: (d_h=d_{\text{model}}/H)

Với đầu vào (X), MHA tạo ra:

[
Q_h = XW_h^Q,\qquad
K_h = XW_h^K,\qquad
V_h = XW_h^V
]

cho từng head (h=1,\ldots,H).

Attention của head thứ (h):

[
O_h =
\operatorname{softmax}
\left(
\frac{Q_hK_h^\top}{\sqrt{d_h}}
\right)V_h
]

Sau đó nối hoặc tổng hợp các head:

[
Y=\operatorname{Concat}(O_1,\ldots,O_H)W^O
]

Như vậy, trong MHA:

[
H_Q=H_K=H_V=H
]

Mỗi head có thể học:

* cách biểu diễn query khác nhau;
* không gian key khác nhau;
* nội dung value khác nhau.

Đây là cơ chế Multi-Head Attention tiêu chuẩn của Transformer. ([arXiv][2])

---

## 3. MQA thay đổi điều gì?

MQA vẫn giữ các query projection riêng:

[
Q_h=XW_h^Q
]

nhưng chỉ sử dụng một projection cho Key và một projection cho Value:

[
K=XW^K,\qquad V=XW^V
]

Mỗi query head tính:

[
O_h =
\operatorname{softmax}
\left(
\frac{Q_hK^\top}{\sqrt{d_h}}
\right)V
]

Tức là:

[
H_Q=H,\qquad H_K=H_V=1
]

Các query head vẫn có thể tạo ra **attention distribution khác nhau**, bởi (Q_h) của chúng khác nhau. Tuy nhiên, mọi head nhìn vào cùng một tập vector Key và lấy thông tin từ cùng một tập vector Value. Đây chính là thay đổi kiến trúc trung tâm của bài báo. 

### Minh họa

**MHA với 8 heads**

```text
Q1 ── K1, V1
Q2 ── K2, V2
Q3 ── K3, V3
...
Q8 ── K8, V8
```

**MQA với 8 query heads**

```text
Q1 ─┐
Q2 ─┤
Q3 ─┤
... │── K, V dùng chung
Q8 ─┘
```

Điều quan trọng là MQA **không gộp các query head thành một head**. Nó chỉ loại bỏ chiều head khỏi tensor Key và Value.

---

## 4. Tại sao KV cache là nút thắt?

Trong decoder tự hồi quy, mô hình sinh từng token:

```text
token 1 → token 2 → token 3 → ...
```

Không thể tính trước token tiếp theo vì token đó phụ thuộc vào token vừa sinh.

Ở mỗi layer, Key và Value của những token trước được lưu trong **KV cache**. Khi sinh token mới, query mới phải attention tới toàn bộ cache:

[
q_tK_{1:t}^\top
]

Ở mỗi bước, mô hình phải:

1. đọc Key cache;
2. tính attention scores;
3. đọc Value cache;
4. tổng hợp đầu ra;
5. thêm Key/Value mới vào cache.

Trong MHA, KV cache có chiều gần như:

[
[B,L,S,H,d_h]
]

với:

* (B): batch size;
* (L): số layer;
* (S): độ dài context;
* (H): số KV heads;
* (d_h): head dimension.

Vì cache phải được đọc lại nhiều lần trong decoding, lượng truyền dữ liệu có thể trở thành giới hạn lớn hơn FLOPs. Đây là vấn đề chính mà bài báo nhắm tới. 

---

## 5. MQA giảm KV cache bao nhiêu?

Kích thước KV cache xấp xỉ:

[
\text{KV bytes}
===============

2BLSH_{KV}d_h,p
]

Trong đó:

* hệ số (2) là Key và Value;
* (H_{KV}) là số KV heads;
* (p) là số byte cho mỗi phần tử.

### MHA

[
H_{KV}=H_Q
]

### MQA

[
H_{KV}=1
]

Do đó, tỷ lệ giảm lý tưởng là:

[
\frac{\text{KV}*{MHA}}{\text{KV}*{MQA}}=H_Q
]

Ví dụ mô hình có:

* 32 layers;
* 32 query heads;
* head dimension (128);
* context 4096 token;
* FP16, tức 2 byte;
* batch size 1.

Với MHA:

[
2\times32\times4096\times32\times128\times2
\approx 2\text{ GiB}
]

Với MQA:

[
2\times32\times4096\times1\times128\times2
\approx64\text{ MiB}
]

Tức là KV cache giảm lý tưởng khoảng:

[
32\times
]

Đây là tính toán lý thuyết cho riêng tensor K/V, chưa bao gồm allocator, padding, metadata hoặc các buffer trung gian.

---

## 6. MQA có giảm FLOPs không?

Có giảm một phần, nhưng **lợi ích lớn nhất thường đến từ giảm memory traffic**, không phải từ việc loại bỏ phần lớn phép tính attention.

Trong MHA, mỗi token cần tạo:

[
H
]

Key vectors và (H) Value vectors.

Trong MQA, mỗi token chỉ tạo:

[
1
]

Key vector và (1) Value vector.

Điều này làm giảm:

* chi phí projection (W^K,W^V);
* số tham số K/V;
* kích thước KV cache;
* lượng dữ liệu phải đọc từ HBM/DRAM.

Tuy nhiên, MQA vẫn có (H) query heads. Mỗi query head vẫn cần tính attention score với chuỗi Key:

[
Q_hK^\top
]

Do đó, phần attention-score computation vẫn tăng theo số query heads. Bài báo phân tích rằng MQA giảm thành phần memory-access bất lợi của incremental attention theo hệ số xấp xỉ bằng số heads (h). 

---

## 7. Tại sao decoding được tăng tốc mạnh?

### Giai đoạn prefill

Khi đưa cả prompt vào mô hình, tất cả token trong prompt thường được xử lý song song:

[
QK^\top
]

được thực hiện dưới dạng các phép nhân ma trận lớn. GPU/TPU được tận dụng tốt và giai đoạn này thường thiên về compute hơn.

### Giai đoạn decode

Mỗi bước chỉ có một query token mới:

[
Q:[B,H,1,d_h]
]

nhưng Key/Value có thể rất dài:

[
K,V:[B,H,S,d_h]
]

Phép toán trở thành nhiều phép nhân ma trận-vector nhỏ. Trong khi đó, toàn bộ K/V của context phải được tải từ bộ nhớ. Vì vậy arithmetic intensity thấp và phần cứng dễ bị **memory-bandwidth bound**.

MQA chuyển cache từ:

[
[B,H,S,d_h]
]

thành:

[
[B,1,S,d_h]
]

nên lượng dữ liệu K/V cần đọc giảm khoảng (H) lần. Điều này đặc biệt hữu ích khi:

* context dài;
* batch inference lớn;
* mô hình có nhiều layer;
* số attention heads lớn;
* GPU bị giới hạn dung lượng hoặc băng thông HBM.

Bài báo gốc tập trung chính vào incremental decoding vì ở đây lợi ích rõ nhất. 

---

## 8. Kết quả trong bài báo gốc

Thí nghiệm chính sử dụng Transformer encoder–decoder khoảng 211 triệu tham số trên bài toán dịch WMT14 English–German. Baseline có 6 layer, (d_{\text{model}}=1024), 8 heads và head dimension 128. Để so sánh công bằng về số tham số, phiên bản MQA mở rộng feed-forward network sau khi giảm tham số K/V. 

### Chất lượng dịch

Kết quả test BLEU:

| Mô hình | Greedy | Beam-4 |
| ------- | -----: | -----: |
| MHA     |   27.7 |   28.4 |
| MQA     |   27.5 |   28.5 |

MQA hơi thấp hơn ở greedy decoding nhưng đạt điểm beam-search tương đương, thậm chí nhỉnh hơn một chút trong thí nghiệm đó. Tuy nhiên, một kết quả đơn lẻ không có nghĩa MQA luôn tốt hơn MHA; kết luận hợp lý là chất lượng giảm ít trên thiết lập được thử nghiệm. 

### Tốc độ decoding

Chi phí decoder incremental trên TPUv2 được báo cáo:

| Mô hình | Decoder inference/token |
| ------- | ----------------------: |
| MHA     |                   46 μs |
| MQA     |                  3.8 μs |

Tỷ lệ trên thiết lập này là khoảng:

[
\frac{46}{3.8}\approx12.1\times
]

Với beam search 4:

| Mô hình |    Encoder + decoder |
| ------- | -------------------: |
| MHA     | (2.0 + 203) μs/token |
| MQA     |  (1.6 + 32) μs/token |

Các con số này phụ thuộc mạnh vào phần cứng, batch size, kernel và cách triển khai; không nên coi (12\times) là mức tăng tốc cố định cho mọi LLM. 

### Language modeling

Trên Billion Word Language Modeling Benchmark:

| Mô hình | Dev perplexity |
| ------- | -------------: |
| MHA     |           29.9 |
| MQA     |           30.2 |

MQA giảm chất lượng nhẹ, nhưng tốt hơn những phương án đơn giản như giảm trực tiếp số head hoặc giảm mạnh kích thước K/V trong thí nghiệm của bài báo. 

---

## 9. Tại sao chia sẻ K/V có thể làm giảm chất lượng?

MHA cho mỗi head quyền học một không gian Key/Value riêng:

[
K_h=XW_h^K,\qquad V_h=XW_h^V
]

Ví dụ, các head khác nhau có thể chuyên biệt hóa cho:

* quan hệ cú pháp;
* coreference;
* vị trí;
* thông tin thực thể;
* pattern dài hạn;
* token lân cận.

MQA buộc tất cả query heads dùng chung:

[
K=XW^K,\qquad V=XW^V
]

Điều đó tạo ra hai giới hạn.

### Giới hạn biểu diễn Key

Mọi head phải so sánh query của mình với cùng một biểu diễn Key. Các head không còn tự chọn không gian Key hoàn toàn riêng biệt.

### Giới hạn biểu diễn Value

Ngay cả khi các query head tạo attention weights khác nhau, chúng vẫn tổng hợp từ cùng một tập Value vectors.

MQA vẫn giữ được một phần đa dạng vì:

[
Q_1\ne Q_2\ne\cdots\ne Q_H
]

nên:

[
\operatorname{softmax}(Q_1K^\top)
\ne
\operatorname{softmax}(Q_2K^\top)
]

Nhưng năng lực biểu diễn nhìn chung thấp hơn MHA, đặc biệt với mô hình hoặc tác vụ cần nhiều kiểu biểu diễn KV độc lập.

---

## 10. MQA khác GQA thế nào?

**Grouped-Query Attention — GQA** là điểm trung gian giữa MHA và MQA.

Giả sử:

[
H_Q=32
]

Ta có thể chọn:

* MHA: (H_{KV}=32)
* GQA: (H_{KV}=8)
* MQA: (H_{KV}=1)

Trong GQA, mỗi nhóm query heads dùng chung một KV head:

```text
Q1–Q4    → K1,V1
Q5–Q8    → K2,V2
Q9–Q12   → K3,V3
...
```

Quan hệ tổng quát:

[
1\le H_{KV}\le H_Q
]

* (H_{KV}=H_Q): MHA
* (1<H_{KV}<H_Q): GQA
* (H_{KV}=1): MQA

Bài GQA năm 2023 chỉ ra rằng MQA có thể gây suy giảm chất lượng và đề xuất GQA như một phương án cân bằng: chất lượng gần MHA nhưng tốc độ gần MQA. Bài này cũng trình bày cách chuyển checkpoint MHA sang MQA/GQA bằng uptraining với khoảng 5% compute tiền huấn luyện ban đầu trong thiết lập của nhóm tác giả. ([arXiv][3])

| Thuộc tính            |        MHA |               GQA |             MQA |
| --------------------- | ---------: | ----------------: | --------------: |
| Query heads           |        (H) |               (H) |             (H) |
| KV heads              |        (H) |               (G) |               1 |
| KV cache              |   Lớn nhất |        Trung bình |        Nhỏ nhất |
| Năng lực biểu diễn    |        Cao |           Gần MHA | Có thể thấp hơn |
| Decode bandwidth      |        Cao |              Thấp |       Thấp nhất |
| Mức cân bằng phổ biến | Chất lượng | Chất lượng/tốc độ |   Tốc độ/bộ nhớ |

---

## 11. Pseudocode

### MHA

```python
# x: [batch, seq, d_model]

q = q_proj(x).view(batch, seq, num_heads, head_dim)
k = k_proj(x).view(batch, seq, num_heads, head_dim)
v = v_proj(x).view(batch, seq, num_heads, head_dim)

scores = einsum("bthd,bshd->bhts", q, k)
weights = softmax(scores / sqrt(head_dim), dim=-1)
output = einsum("bhts,bshd->bthd", weights, v)
```

### MQA

```python
# x: [batch, seq, d_model]

q = q_proj(x).view(batch, seq, num_query_heads, head_dim)

# Chỉ có một KV head
k = k_proj(x).view(batch, seq, 1, head_dim)
v = v_proj(x).view(batch, seq, 1, head_dim)

# K/V được broadcast logic tới mọi query head
scores = einsum("bthd,bs1d->bhts", q, k)
weights = softmax(scores / sqrt(head_dim), dim=-1)
output = einsum("bhts,bs1d->bthd", weights, v)
```

Trong triển khai tối ưu, không nên sao chép vật lý K/V thành (H) bản. Kernel cần hỗ trợ broadcasting hoặc grouped-query layout; nếu dùng `repeat` để nhân tensor K/V, lợi ích băng thông và bộ nhớ có thể bị giảm đáng kể.

---

## 12. Ảnh hưởng đến số tham số

Bỏ qua bias, trong MHA:

[
W^Q,W^K,W^V,W^O\in\mathbb{R}^{d_{\text{model}}\times d_{\text{model}}}
]

Tổng tham số attention xấp xỉ:

[
4d_{\text{model}}^2
]

Trong MQA:

[
W^Q,W^O\in\mathbb{R}^{d_{\text{model}}\times d_{\text{model}}}
]

nhưng:

[
W^K,W^V\in
\mathbb{R}^{d_{\text{model}}\times d_h}
]

nên tổng gần:

[
2d_{\text{model}}^2
+
2d_{\text{model}}d_h
]

Vì:

[
d_h=\frac{d_{\text{model}}}{H}
]

ta có:

[
2d_{\text{model}}^2
+
\frac{2d_{\text{model}}^2}{H}
]

Ví dụ (H=32), phần projection attention giảm từ khoảng:

[
4d_{\text{model}}^2
]

xuống:

[
2.0625d_{\text{model}}^2
]

Tuy nhiên, tổng tham số toàn LLM không giảm một nửa vì feed-forward network, embedding và các thành phần khác vẫn chiếm phần lớn. Trong bài báo gốc, tác giả còn tăng kích thước FFN của mô hình MQA để giữ tổng số tham số ngang baseline, nhằm tách hiệu ứng kiến trúc khỏi hiệu ứng số tham số. 

---

## 13. Khi nào MQA đặc biệt hữu ích?

MQA phù hợp nhất khi ưu tiên:

* tốc độ sinh token;
* context dài;
* batch serving lớn;
* giảm dung lượng KV cache;
* tăng số request đồng thời;
* chạy trên phần cứng có băng thông bộ nhớ hạn chế.

Lợi ích thường ít nổi bật hơn khi:

* chỉ đo tốc độ prefill;
* sequence rất ngắn;
* batch nhỏ và mô hình vẫn compute-bound;
* kernel chưa được tối ưu cho MQA;
* các thành phần khác như FFN hoặc communication mới là bottleneck.

Một điểm thực tế quan trọng: KV cache nhỏ hơn không chỉ tăng tốc một request. Nó còn cho phép giữ nhiều sequence hơn trong bộ nhớ, do đó có thể cải thiện **throughput toàn hệ thống serving**.

---

## 14. Hạn chế của bài báo gốc

Khi đọc kết quả năm 2019, cần lưu ý:

1. Mô hình thử nghiệm khoảng 192–211 triệu tham số, nhỏ hơn nhiều so với LLM hiện đại.
2. Thử nghiệm chủ yếu trên dịch máy và Billion Word Benchmark.
3. Phần cứng được sử dụng là TPUv2/TPUv3.
4. Context thử nghiệm tốc độ dài 128 token, ngắn hơn context hiện đại.
5. Kernel, quantization, paged KV cache và hệ thống serving hiện nay đã thay đổi đáng kể.

Vì vậy, đóng góp lâu dài của paper không phải một con số speedup cụ thể, mà là nhận định kiến trúc:

> Trong autoregressive decoding, số KV heads là một biến số quan trọng quyết định dung lượng KV cache và memory bandwidth.

Kết luận của bài báo là MQA giảm đáng kể yêu cầu băng thông bộ nhớ trong incremental inference, trong khi chỉ gây suy giảm chất lượng nhỏ trên các thí nghiệm của tác giả. 

---

## 15. Tóm tắt bản chất của MQA

Có thể ghi nhớ MQA bằng ba dòng:

[
\boxed{H_Q=H,\quad H_K=H_V=1}
]

[
\boxed{\text{KV cache giảm khoảng }H\text{ lần so với MHA}}
]

[
\boxed{\text{Đổi một phần năng lực biểu diễn để lấy tốc độ và bộ nhớ}}
]

MQA không làm Transformer “không cần multi-head”. Nó vẫn duy trì nhiều query heads, nhưng nhận ra rằng trong decoding, việc lưu một bộ K/V riêng cho từng head có chi phí rất lớn. Bằng cách chia sẻ K/V, MQA giải quyết trực tiếp nút thắt băng thông bộ nhớ. GQA sau đó mở rộng ý tưởng bằng cách dùng một số lượng KV heads nằm giữa 1 và số query heads, tạo ra điểm cân bằng thực dụng hơn giữa chất lượng và hiệu suất. 

[1]: https://arxiv.org/abs/1911.02150 "[1911.02150] Fast Transformer Decoding: One Write-Head is All You Need"
[2]: https://arxiv.org/abs/1706.03762?utm_source=chatgpt.com "Attention Is All You Need"
[3]: https://arxiv.org/abs/2305.13245?utm_source=chatgpt.com "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"
