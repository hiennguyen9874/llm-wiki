# Switch Transformer và Mixture of Experts trong LLM

**Switch Transformer** là kiến trúc Mixture of Experts do William Fedus, Barret Zoph và Noam Shazeer đề xuất trong bài báo *“Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity”*. Bản đầu tiên xuất hiện năm 2021 và phiên bản hoàn chỉnh được công bố trên JMLR năm 2022. Mục tiêu chính là tăng số lượng tham số của Transformer lên hàng trăm tỷ hoặc nghìn tỷ mà không làm lượng tính toán cho mỗi token tăng tương ứng. ([arXiv][1])

## 1. Vấn đề của Transformer dense

Trong một Transformer thông thường, mỗi block thường gồm:

[
x \rightarrow \text{Self-Attention} \rightarrow \text{FFN}
]

Feed-forward network — FFN — thường có dạng:

[
\operatorname{FFN}(x)
=====================

W_2,\sigma(W_1x)
]

Mọi token đều đi qua cùng một FFN và sử dụng cùng tập tham số.

Giả sử:

* (d_{\text{model}}): kích thước hidden state;
* (d_{\text{ff}}): kích thước lớp trung gian;
* số tham số FFN xấp xỉ:

[
2d_{\text{model}}d_{\text{ff}}
]

Khi tăng độ rộng của FFN, ta đồng thời tăng:

* số tham số;
* FLOPs;
* bộ nhớ activation;
* thời gian huấn luyện và suy luận.

Switch Transformer tìm cách **tăng số tham số mà không tăng đáng kể FLOPs trên mỗi token**. Tác giả coi số tham số và lượng tính toán là hai trục scaling tương đối độc lập: thêm nhiều expert làm tăng capacity của mô hình, nhưng mỗi token chỉ kích hoạt một expert. 

---

## 2. Ý tưởng Mixture of Experts

Thay vì chỉ có một FFN, ta tạo nhiều FFN song song:

[
E_1, E_2, \dots, E_N
]

Mỗi FFN được gọi là một **expert**.

Một router — hay gating network — quyết định token nào sẽ được gửi đến expert nào:

[
x \rightarrow \text{Router}(x) \rightarrow E_i(x)
]

Các expert không nhất thiết được gán trước cho những lĩnh vực như toán học, lập trình hoặc ngôn ngữ. Sự phân công được học tự động thông qua quá trình tối ưu.

MoE đã tồn tại trước Switch Transformer. Công trình năm 2017 của Shazeer và cộng sự sử dụng một router thưa để chọn một nhóm top-(k) expert cho mỗi input. Switch Transformer đơn giản hóa thiết kế đó bằng cách chỉ chọn **một expert duy nhất cho mỗi token**, tức (k=1). ([arXiv][2])

---

## 3. Switch Transformer thay đổi phần nào?

Switch Transformer chủ yếu thay thế các FFN dense bằng **Switch FFN layer**:

```text
Transformer dense:

Token
  ↓
Self-Attention
  ↓
Một FFN chung
  ↓
Output
```

```text
Switch Transformer:

Token
  ↓
Self-Attention
  ↓
Router
  ├── Expert 1
  ├── Expert 2
  ├── ...
  └── Expert N
  ↓
Output
```

Router hoạt động độc lập trên từng token. Vì vậy, hai token nằm cạnh nhau trong cùng một câu vẫn có thể được gửi đến hai expert khác nhau. Trong kiến trúc của bài báo, mỗi expert về bản chất vẫn là một FFN thông thường với bộ trọng số riêng. 

Không nhất thiết tất cả block đều dùng MoE. Trong nhiều cấu hình của bài báo, Switch FFN được đặt xen kẽ với FFN dense, chẳng hạn một Switch layer sau mỗi hai FFN layer. 

---

## 4. Router hoạt động như thế nào?

Cho hidden state của token:

[
x\in \mathbb{R}^{d_{\text{model}}}
]

Router có một ma trận:

[
W_r \in \mathbb{R}^{N\times d_{\text{model}}}
]

Router logits:

[
h(x)=W_rx
]

Sau đó áp dụng softmax:

[
p_i(x)
======

\frac{\exp(h_i(x))}
{\sum_{j=1}^{N}\exp(h_j(x))}
]

Trong đó (p_i(x)) là xác suất router gán token (x) cho expert (i). 

Switch Transformer chọn expert có xác suất lớn nhất:

[
i^*=\arg\max_i p_i(x)
]

Output của Switch layer là:

[
y=p_{i^*}(x)E_{i^*}(x)
]

Điểm cần chú ý:

* Quyết định chọn expert bằng `argmax` là rời rạc.
* Tuy nhiên, output vẫn được nhân với (p_{i^*}(x)).
* Vì (p_{i^*}(x)) phụ thuộc vào router weights, gradient vẫn có thể cập nhật router.

Đây là nguyên nhân top-1 routing vẫn học được dù chỉ có một expert thực hiện FFN cho mỗi token. 

---

## 5. Vì sao top-1 routing là đóng góp quan trọng?

MoE trước đó thường sử dụng top-2 hoặc top-(k):

[
y=\sum_{i\in \operatorname{TopK}}p_i(x)E_i(x)
]

Switch Transformer đặt:

[
k=1
]

Điều này mang lại ba lợi ích chính:

1. **Ít tính toán hơn:** mỗi token chỉ chạy qua một FFN expert.
2. **Giảm dung lượng cần dành cho mỗi expert:** token không bị nhân đôi để gửi đến nhiều expert.
3. **Giảm communication:** trong hệ phân tán, mỗi token chỉ cần được truyền đến một thiết bị chứa expert tương ứng.

Bài báo cho thấy top-1 routing không làm giảm chất lượng so với thiết kế MoE phức tạp hơn trong các thử nghiệm của họ, đồng thời đạt tỷ lệ chất lượng trên thời gian huấn luyện tốt hơn. 

---

## 6. Tổng tham số khác active parameters

Đây là điểm quan trọng nhất khi đọc các thông báo về LLM MoE.

Giả sử một layer có 128 expert, mỗi expert chứa (P) tham số.

Tổng số tham số expert là:

[
P_{\text{total}}=128P
]

Nhưng vì mỗi token chỉ dùng một expert:

[
P_{\text{active/token}}\approx P
]

Do đó:

* **Total parameters:** tất cả trọng số trong tất cả expert.
* **Active parameters:** trọng số thực sự được sử dụng cho một token.
* **FLOPs/token:** gần với một expert, không phải tổng của 128 expert.

Ví dụ khái niệm:

```text
Dense model:
20B tổng tham số
20B tham số được kích hoạt mỗi token

MoE model:
200B tổng tham số
20B tham số được kích hoạt mỗi token
```

MoE không làm 200B tham số hoạt động với chi phí của 20B theo nghĩa hoàn toàn miễn phí: router, truyền dữ liệu giữa thiết bị, padding, load balancing và bộ nhớ lưu trọng số vẫn phát sinh chi phí. Nhưng phép nhân ma trận chính của FFN chỉ xảy ra trên expert được chọn.

Trong bảng mô hình của bài báo, Switch-Base có khoảng 7 tỷ tham số nhưng được thiết kế với cùng FLOPs trên mỗi sequence như T5-Base khoảng 0,2 tỷ tham số. Tương tự, Switch-XXL có 395 tỷ tham số và được FLOP-match với T5-XXL 11 tỷ tham số. 

---

## 7. Expert capacity và token overflow

Nếu router tự do chọn expert, một số expert có thể nhận quá nhiều token trong khi những expert khác gần như không có token.

Để triển khai hiệu quả trên TPU/GPU, mỗi expert được cấp một batch có kích thước cố định, gọi là **expert capacity**:

[
C
=

\frac{T}{N}
\times \text{capacity factor}
]

Trong đó:

* (T): tổng số token trong batch;
* (N): số expert;
* capacity factor: hệ số tạo vùng đệm.

Ví dụ:

* 1.024 token;
* 8 expert;
* capacity factor = 1,25.

Khi đó:

[
C=\frac{1024}{8}\times1.25=160
]

Mỗi expert có thể nhận tối đa 160 token. 

### Khi expert bị quá tải

Giả sử expert 3 được router gửi 190 token nhưng capacity chỉ là 160. Ba mươi token vượt quá giới hạn sẽ bị **drop khỏi Switch FFN**.

Trong thiết kế của bài báo, token bị drop không biến mất hoàn toàn. Nó bỏ qua expert computation nhưng vẫn đi tiếp qua residual connection:

[
y=x+\operatorname{SwitchFFN}(x)
]

Nếu phần Switch FFN bị bỏ qua:

[
y\approx x
]

Capacity factor lớn giúp giảm dropped tokens nhưng làm tăng:

* padding;
* bộ nhớ;
* communication;
* phép tính lãng phí trên các slot trống.

Bài báo báo cáo tỷ lệ token bị drop thường dưới 1% khi load-balancing loss được thiết lập phù hợp. 

---

## 8. Vấn đề expert collapse

Nếu chỉ tối ưu language-modeling loss, router có thể nhanh chóng học cách gửi phần lớn token đến một hoặc vài expert.

Ví dụ:

```text
Expert 1: 80% token
Expert 2: 10%
Expert 3: 5%
Expert 4: 5%
```

Hậu quả:

* expert 1 liên tục overflow;
* nhiều token bị drop;
* các expert khác ít được huấn luyện;
* tài nguyên thiết bị không được tận dụng;
* router dễ rơi vào trạng thái mất cân bằng kéo dài.

Đây thường được gọi là **expert collapse** hoặc load imbalance.

---

## 9. Auxiliary load-balancing loss

Switch Transformer thêm một loss phụ để phân phối token tương đối đều giữa các expert.

Đặt:

[
f_i
===

\frac{1}{T}
\sum_{x\in B}
\mathbf{1}
\left[
\arg\max p(x)=i
\right]
]

(f_i) là tỷ lệ token thực sự được gửi đến expert (i).

Tiếp theo:

[
P_i
===

\frac{1}{T}
\sum_{x\in B}p_i(x)
]

(P_i) là trung bình probability mass mà router cấp cho expert (i).

Loss phụ:

[
L_{\text{balance}}
==================

\alpha N
\sum_{i=1}^{N}f_iP_i
]

Phân phối lý tưởng là:

[
f_i=P_i=\frac{1}{N}
]

Khi các token tập trung vào cùng một expert, tích (f_iP_i) của expert đó tăng và loss lớn hơn. Trong bài báo, tác giả dùng:

[
\alpha=10^{-2}
]

Loss cuối cùng:

[
L
=

L_{\text{language model}}
+
L_{\text{balance}}
]

Vector (f) chứa quyết định `argmax` nên không khả vi, nhưng (P) được tính từ softmax nên khả vi. Gradient qua (P) vẫn hướng router đến việc phân phối probability mass đồng đều hơn. 

Một lưu ý: load balancing không buộc mỗi expert phải học cùng một chức năng. Nó chỉ khuyến khích chúng nhận lượng token tương đối cân bằng; expert vẫn có thể chuyên môn hóa theo những pattern khác nhau.

---

## 10. Luồng xử lý phân tán

Các expert thường được chia lên nhiều accelerator:

```text
TPU/GPU 0: Expert 0
TPU/GPU 1: Expert 1
TPU/GPU 2: Expert 2
TPU/GPU 3: Expert 3
```

Một batch ban đầu cũng được chia trên các thiết bị. Router được tính cục bộ cho các token, sau đó token phải được gửi đến thiết bị đang giữ expert tương ứng.

Quy trình tổng quát:

```text
1. Mỗi thiết bị nhận một phần batch
2. Router chọn expert cho từng token
3. Gom token theo expert
4. All-to-all communication
5. Mỗi thiết bị chạy FFN expert của mình
6. All-to-all communication lần hai
7. Đưa output về đúng vị trí token ban đầu
```

Đây gọi là **expert parallelism**.

Trong bài báo, thao tác all-to-all chuyển từ cách chia tensor theo batch/device sang cách chia theo expert, sau đó chuyển ngược trở lại sau expert computation. Vì vậy, chi phí mạng giữa các accelerator là một trong những hạn chế lớn nhất của MoE. 

---

## 11. Data, model và expert parallelism

Switch Transformer kết hợp ba kiểu song song hóa.

### Data parallelism

Mỗi thiết bị giữ bản sao của mô hình nhưng xử lý batch khác nhau:

[
\text{batch}\rightarrow \text{chia theo thiết bị}
]

Sau backward pass, gradient được đồng bộ.

### Model parallelism

Một ma trận lớn hoặc một layer được chia trên nhiều thiết bị:

[
W=[W^{(1)},W^{(2)},\dots]
]

Mỗi thiết bị giữ một phần trọng số.

### Expert parallelism

Mỗi thiết bị giữ một hoặc một nhóm expert khác nhau:

[
E_1\rightarrow \text{GPU 1},\quad
E_2\rightarrow \text{GPU 2}
]

Switch-C chủ yếu sử dụng expert parallelism, trong khi Switch-XXL kết hợp expert, model và data parallelism. Việc kết hợp cả ba làm bài toán ánh xạ model lên phần cứng trở nên phức tạp vì phải cân bằng FLOPs, bộ nhớ, all-reduce và all-to-all communication. 

---

## 12. Các kỹ thuật ổn định huấn luyện

### 12.1 Selective precision

Router softmax nhạy với sai số số học. Chạy toàn bộ model bằng `bfloat16` có thể khiến quá trình huấn luyện mất ổn định.

Giải pháp của bài báo:

* FFN, attention và phần lớn model dùng `bfloat16`;
* router logits và softmax tạm thời được tính bằng `float32`;
* dispatch/combine tensors sau đó được cast lại về `bfloat16`.

```python
router_logits = x.float() @ router_weight.float()
router_probs = softmax(router_logits)
router_probs = router_probs.to(bfloat16)
```

Cách này giữ được tốc độ gần với huấn luyện bfloat16 nhưng đạt độ ổn định tương tự float32, đồng thời tránh truyền tensor float32 qua các thao tác all-to-all đắt đỏ. 

### 12.2 Giảm initialization scale

Tác giả nhận thấy khởi tạo mặc định của Transformer quá lớn đối với Switch Transformer. Họ khuyến nghị giảm initialization scale xuống khoảng 0,1 lần:

[
s_{\text{Switch}}=0.1s_{\text{default}}
]

Trong thí nghiệm của bài báo, việc giảm scale làm giảm mạnh variance giữa các lần chạy và cải thiện độ ổn định từ model nhỏ đến model trên một nghìn tỷ tham số. 

### 12.3 Tăng regularization khi fine-tuning

Sparse model có capacity rất lớn nhưng dữ liệu fine-tuning thường nhỏ. Điều này dễ dẫn đến overfitting, đặc biệt ở các expert FFN.

Tác giả thử tăng dropout trong các expert khi fine-tuning, thay vì tăng dropout đồng đều trên toàn model. Đây là một dạng regularization có mục tiêu cho phần tham số lớn nhất của mô hình. 

---

## 13. Kết quả chính của bài báo

Các kết quả nổi bật mà nhóm tác giả báo cáo gồm:

* Mô hình dựa trên T5-Base và T5-Large đạt tốc độ pre-training đến cùng một mức chất lượng nhanh hơn tới khoảng 7 lần trong một số thiết lập.
* Trên dữ liệu đa ngôn ngữ, model cải thiện trên cả 101 ngôn ngữ được đánh giá; 91% số ngôn ngữ đạt speedup ít nhất 4 lần so với mT5 baseline để đạt perplexity mục tiêu.
* Nhóm huấn luyện các model khoảng 395 tỷ và 1,6 nghìn tỷ tham số.
* Switch-C 1,6 nghìn tỷ tham số có khoảng 890 tỷ FLOPs mỗi sequence, thấp hơn đáng kể so với 6,3 nghìn tỷ FLOPs mỗi sequence của T5-XXL 11 tỷ tham số trong bảng cấu hình.
* Switch-C đạt khoảng 4 lần speedup so với T5-XXL để đạt một mức perplexity cố định trong thí nghiệm của bài báo. 

Cần hiểu đúng rằng “7× speedup” không có nghĩa một bước forward luôn nhanh hơn 7 lần. Nó chủ yếu là **thời gian hoặc số bước cần để đạt cùng mức chất lượng**, trong một cấu hình phần cứng và huấn luyện cụ thể.

---

## 14. Vì sao nhiều tham số giúp dù chỉ kích hoạt một expert?

Một cách trực giác, mỗi token không cần sử dụng toàn bộ kiến thức của model trong mọi lần tính toán.

Ví dụ:

* token liên quan đến cú pháp lập trình có thể kích hoạt một expert;
* token là tên riêng có thể kích hoạt expert khác;
* token thuộc ngôn ngữ khác có thể đi sang một expert khác.

Mỗi expert có thể học một phần khác nhau của phân phối dữ liệu. Vì vậy, toàn mô hình có capacity lưu trữ pattern lớn hơn, trong khi chi phí xử lý một token chỉ tương ứng với một phần nhỏ của model.

Tuy nhiên, không nên hiểu rằng mỗi expert chắc chắn trở thành một lĩnh vực rõ ràng, dễ diễn giải. Router có thể phân chia dựa trên:

* ngôn ngữ;
* vị trí token;
* loại từ;
* cấu trúc câu;
* pattern thống kê;
* tổ hợp đặc trưng khó giải thích bằng nhãn con người.

---

## 15. So sánh Dense Transformer, MoE và Switch Transformer

| Thuộc tính                   |                 Dense |    MoE top-(k) | Switch Transformer |
| ---------------------------- | --------------------: | -------------: | -----------------: |
| Số expert được dùng/token    | Không có expert riêng |          (k>1) |                  1 |
| Toàn bộ FFN được kích hoạt   |                    Có |          Không |              Không |
| FLOPs tăng theo tổng tham số |        Gần tuyến tính | Chậm hơn dense |     Chậm hơn dense |
| Router                       |                 Không |             Có |                 Có |
| Load-balancing loss          |                 Không |      Thường có |                 Có |
| Communication giữa expert    |                 Không |            Cao |   Thấp hơn top-(k) |
| Nguy cơ token overflow       |                 Không |             Có |                 Có |
| Độ đơn giản                  |                   Cao |           Thấp |         Trung bình |
| Capacity trên cùng FLOPs     |              Thấp hơn |            Cao |                Cao |

---

## 16. Hạn chế của Switch Transformer

### Communication có thể trở thành nút thắt

Phép tính FFN ít hơn không đồng nghĩa latency thấp hơn. Nếu token thường xuyên phải đi qua mạng giữa nhiều node, all-to-all communication có thể chiếm phần lớn thời gian.

### Tổng trọng số vẫn phải được lưu

Một model 1 nghìn tỷ tham số vẫn cần lưu 1 nghìn tỷ tham số trên cụm máy, dù mỗi token chỉ kích hoạt một phần nhỏ.

Do đó MoE giảm:

* compute trên mỗi token;

nhưng không tự động giảm tương ứng:

* tổng bộ nhớ weights;
* dung lượng checkpoint;
* chi phí tải model;
* độ phức tạp phục vụ.

### Batch nhỏ gây khó load balancing

Khi số token trong batch nhỏ so với số expert:

* mỗi expert chỉ nhận rất ít token;
* phân phối dễ mất cân bằng;
* matrix multiplication nhỏ và kém hiệu quả;
* nhiều slot capacity bị bỏ trống.

Vì thế MoE thường hiệu quả hơn với batching đủ lớn.

### Fine-tuning không đơn giản

Một expert có thể nhận rất ít token từ dữ liệu downstream. Điều này gây:

* expert under-training;
* router thay đổi quá mạnh;
* overfitting;
* chất lượng downstream không tương xứng với perplexity pre-training.

Chính bài báo cũng ghi nhận các model lớn nhất không phải lúc nào cũng chuyển lợi thế pre-training sang SuperGLUE một cách tương ứng. 

### Active parameters không phải toàn bộ chi phí

Khi nói một MoE “chỉ kích hoạt 20B trong tổng 200B”, con số 20B thường không phản ánh đầy đủ:

* attention;
* embedding;
* router;
* dense layers;
* KV cache;
* communication;
* padding và token dropping.

Do đó không nên so sánh active parameters giữa hai model mà bỏ qua FLOPs/token, kiến trúc và hệ thống triển khai.

---

## 17. Pseudocode đơn giản

```python
def switch_ffn(x, experts, router):
    """
    x: [num_tokens, d_model]
    experts: danh sách các FFN
    """

    # Router probabilities
    logits = router(x.float())
    probs = softmax(logits, dim=-1)

    # Top-1 routing
    expert_idx = probs.argmax(dim=-1)
    gate = probs.max(dim=-1).values

    output = zeros_like(x)

    for i, expert in enumerate(experts):
        mask = expert_idx == i
        tokens = x[mask]

        # Thực tế cần giới hạn expert capacity
        expert_output = expert(tokens)

        output[mask] = gate[mask, None] * expert_output

    return output
```

Trong triển khai thực tế, không dùng vòng lặp Python như trên. Token được:

1. sắp xếp hoặc đóng gói theo expert;
2. truyền bằng all-to-all;
3. xử lý theo batch lớn trên từng expert;
4. truyền ngược và phục hồi thứ tự ban đầu.

Loss huấn luyện có dạng:

```python
loss = language_model_loss + alpha * load_balance_loss
```

---

## 18. Đóng góp cốt lõi của bài báo

Bài báo không phát minh ra khái niệm Mixture of Experts. Đóng góp quan trọng nhất là làm MoE trong Transformer **đơn giản và có khả năng scale thực tế hơn**:

[
\boxed{\text{Top-1 routing}}
]

kết hợp với:

[
\boxed{\text{Expert capacity}}
]

[
\boxed{\text{Load-balancing loss}}
]

[
\boxed{\text{Selective float32 router}}
]

[
\boxed{\text{Reduced initialization scale}}
]

[
\boxed{\text{Expert parallelism}}
]

Thông điệp trung tâm có thể tóm lại là:

> Thay vì bắt mỗi token sử dụng toàn bộ tham số của LLM, hãy xây dựng một model có rất nhiều tham số và chỉ kích hoạt phần phù hợp với từng token.

Switch Transformer vì thế là một cột mốc quan trọng trong hướng **sparse LLM và conditional computation**, cho thấy số tham số có thể tăng rất mạnh mà FLOPs trên mỗi token không cần tăng cùng tỷ lệ.

[1]: https://arxiv.org/abs/2101.03961?utm_source=chatgpt.com "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity"
[2]: https://arxiv.org/abs/1701.06538?utm_source=chatgpt.com "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer"
