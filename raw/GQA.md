## 1. Bài báo GQA là gì?

**GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints** là bài báo của Joshua Ainslie và cộng sự tại Google Research, công bố năm 2023. Bài báo đưa ra hai đóng góp chính:

1. Chuyển một checkpoint Transformer đang dùng **Multi-Head Attention — MHA** sang kiến trúc tiết kiệm hơn mà không phải huấn luyện lại hoàn toàn.
2. Đề xuất **Grouped-Query Attention — GQA**, một kiến trúc trung gian giữa MHA và **Multi-Query Attention — MQA**.

Mục tiêu là đạt chất lượng gần MHA nhưng tốc độ sinh token và mức sử dụng bộ nhớ gần MQA. ([arXiv][1])

---

# 2. Vấn đề mà GQA giải quyết

Trong quá trình autoregressive decoding, LLM sinh từng token một. Ở mỗi layer attention, mô hình phải:

* tính query của token mới;
* đọc lại toàn bộ key và value của các token trước đó từ **KV cache**;
* thực hiện attention để dự đoán token tiếp theo.

Khi context dài hoặc batch lớn, lượng dữ liệu K và V phải đọc từ bộ nhớ rất lớn. Vì vậy, suy luận thường bị giới hạn không chỉ bởi FLOPs mà còn bởi **memory bandwidth**: tốc độ chuyển dữ liệu giữa HBM/VRAM và các compute unit. Đây cũng là động lực ban đầu của MQA. 

Nói đơn giản:

> Khi sinh từng token, GPU có thể không thiếu khả năng nhân ma trận; nó đang phải chờ dữ liệu KV được tải từ bộ nhớ.

GQA giảm số lượng KV head, từ đó giảm:

* kích thước KV cache;
* lượng dữ liệu phải đọc cho mỗi token;
* bộ nhớ cần thiết cho context dài hoặc batch lớn.

---

# 3. Nhắc lại Multi-Head Attention

Giả sử hidden state có kích thước (d_{\text{model}}), mô hình có (H) attention heads và mỗi head có chiều:

[
d_h = \frac{d_{\text{model}}}{H}
]

Với Multi-Head Attention, mỗi head (i) có các phép chiếu riêng:

[
Q_i = XW_i^Q,\qquad
K_i = XW_i^K,\qquad
V_i = XW_i^V
]

Attention của head (i):

[
O_i =
\operatorname{softmax}
\left(
\frac{Q_iK_i^\top}{\sqrt{d_h}} + M
\right)V_i
]

Sau đó nối kết quả từ tất cả các head:

[
O = \operatorname{Concat}(O_1,\ldots,O_H)W^O
]

Trong MHA:

[
H_Q = H_K = H_V = H
]

Tức là nếu mô hình có 32 query heads, nó cũng có 32 key heads và 32 value heads. Kiến trúc multi-head ban đầu là một thành phần cốt lõi của Transformer. ([arXiv][2])

---

# 4. Multi-Query Attention — MQA

MQA vẫn giữ nhiều query heads nhưng chỉ dùng **một key head và một value head**:

[
H_Q = H,\qquad H_K = H_V = 1
]

Mọi query head dùng chung cùng một (K) và (V):

[
O_i =
\operatorname{softmax}
\left(
\frac{Q_iK^\top}{\sqrt{d_h}}
\right)V
]

Ví dụ với 32 query heads:

* MHA: 32 K heads, 32 V heads;
* MQA: 1 K head, 1 V head.

Như vậy, phần KV cache giảm xấp xỉ 32 lần. MQA được Noam Shazeer đề xuất nhằm giảm đáng kể memory-bandwidth cost khi incremental decoding. ([arXiv][3])

Nhược điểm là tất cả query heads phải truy vấn cùng một biểu diễn K/V. Điều này tạo ra một “nút thắt biểu diễn”:

* các query heads vẫn có thể tìm những quan hệ khác nhau;
* nhưng chúng không còn có K/V subspace độc lập;
* chất lượng có thể giảm;
* bài báo GQA còn quan sát thấy MQA có thể kém ổn định khi huấn luyện hoặc fine-tuning, đặc biệt với input dài. 

---

# 5. Ý tưởng của Grouped-Query Attention

GQA chia (H) query heads thành (G) nhóm. Mỗi nhóm dùng chung một key head và một value head:

[
H_Q = H,\qquad H_K = H_V = G
]

Số query heads trong mỗi nhóm là:

[
R = \frac{H}{G}
]

với (R) đôi khi được gọi là **query-to-KV ratio**.

Ví dụ:

[
H=32,\qquad G=8
]

thì:

[
R = 32/8 = 4
]

Tức là:

* có 32 query heads;
* có 8 key heads;
* có 8 value heads;
* mỗi K/V head phục vụ 4 query heads.

Với query head (i), KV head tương ứng có thể được xác định bởi:

[
g(i) = \left\lfloor \frac{i}{R} \right\rfloor
]

và:

[
O_i =
\operatorname{softmax}
\left(
\frac{Q_iK_{g(i)}^\top}{\sqrt{d_h}}
\right)V_{g(i)}
]

Hai trường hợp biên:

[
G=H \Rightarrow \text{GQA trở thành MHA}
]

[
G=1 \Rightarrow \text{GQA trở thành MQA}
]

Do đó, GQA có thể được xem là một phổ liên tục:

[
\text{MHA}
\longleftrightarrow
\text{GQA}
\longleftrightarrow
\text{MQA}
]

Đây chính là định nghĩa trung tâm của bài báo. 

---

# 6. Minh họa cấu trúc

Với tám query heads:

```text
MHA
Q0 -> K0,V0
Q1 -> K1,V1
Q2 -> K2,V2
Q3 -> K3,V3
Q4 -> K4,V4
Q5 -> K5,V5
Q6 -> K6,V6
Q7 -> K7,V7
```

```text
GQA, 4 KV heads
Q0,Q1 -> K0,V0
Q2,Q3 -> K1,V1
Q4,Q5 -> K2,V2
Q6,Q7 -> K3,V3
```

```text
MQA
Q0,Q1,Q2,Q3,Q4,Q5,Q6,Q7 -> K0,V0
```

MHA có năng lực biểu diễn cao nhất nhưng KV cache lớn nhất. MQA có KV cache nhỏ nhất nhưng chia sẻ mạnh nhất. GQA chọn một điểm cân bằng ở giữa. Sơ đồ chính thức của bài báo thể hiện đúng cấu trúc này. 

---

# 7. GQA tiết kiệm KV cache bao nhiêu?

Với decoder-only Transformer, bỏ qua một số chi tiết implementation, kích thước KV cache xấp xỉ:

[
M_{\text{KV}}
=============

2
\times L
\times B
\times S
\times H_{KV}
\times d_h
\times b
]

Trong đó:

* (L): số layer;
* (B): batch size;
* (S): context length;
* (H_{KV}): số KV heads;
* (d_h): head dimension;
* (b): số byte trên mỗi phần tử;
* hệ số 2 là do lưu cả K và V.

Vì:

[
d_{\text{model}} = H_Qd_h
]

nên với MHA:

[
M_{\text{MHA}}
==============

# 2LBSH_Qd_hb

2LBSd_{\text{model}}b
]

Với GQA:

[
M_{\text{GQA}}
==============

2LBSH_{KV}d_hb
]

Tỷ lệ là:

[
\frac{M_{\text{GQA}}}{M_{\text{MHA}}}
=====================================

# \frac{H_{KV}}{H_Q}

\frac{1}{R}
]

Ví dụ 32 query heads và 8 KV heads:

[
\frac{M_{\text{GQA}}}{M_{\text{MHA}}}
=====================================

# \frac{8}{32}

\frac14
]

Phần KV cache chỉ còn khoảng **25%**, tức giảm khoảng **4 lần**.

## Ví dụ số cụ thể

Giả sử:

* 32 layers;
* context 4096;
* batch 1;
* 32 query heads;
* head dimension 128;
* dữ liệu FP16/BF16, tức 2 byte.

### MHA: 32 KV heads

[
2 \times 32 \times 1 \times 4096
\times 32 \times 128 \times 2
]

xấp xỉ:

[
2\text{ GiB}
]

### GQA: 8 KV heads

[
2 \times 32 \times 1 \times 4096
\times 8 \times 128 \times 2
]

xấp xỉ:

[
512\text{ MiB}
]

### MQA: 1 KV head

xấp xỉ:

[
64\text{ MiB}
]

Đây là phần tiết kiệm của KV cache, chưa bao gồm trọng số mô hình, activation tạm thời và overhead của framework.

---

# 8. GQA có giảm FLOPs của attention không?

Có, nhưng điểm quan trọng cần phân biệt là **giảm bộ nhớ không đồng nghĩa giảm toàn bộ phép tính attention theo cùng tỷ lệ**.

## Phần được giảm

Các phép chiếu K và V có output nhỏ hơn:

MHA thường có:

[
W^K,W^V\in
\mathbb{R}^{d_{\text{model}}\times d_{\text{model}}}
]

GQA có thể xem là:

[
W^K,W^V\in
\mathbb{R}^{d_{\text{model}}\times (H_{KV}d_h)}
]

Vì vậy số tham số và FLOPs của hai projection K/V giảm theo:

[
\frac{H_{KV}}{H_Q}
]

## Phần không giảm tương ứng

Mô hình vẫn có (H_Q) query heads. Mỗi query head vẫn phải:

* tính dot product với chuỗi key;
* tạo attention distribution riêng;
* kết hợp các value.

Do đó, số attention-score computations không giảm đơn giản từ (H_Q) xuống (H_{KV}). Trong decoding, lợi ích lớn nhất thường đến từ việc phải đọc ít dữ liệu KV hơn, không phải vì toàn bộ phép nhân attention giảm (R) lần.

---

# 9. GQA khác Head Grouping thông thường ở đâu?

Tên “grouped” dễ gây hiểu nhầm. GQA không đơn giản là gom các attention heads rồi trung bình output.

Mỗi query head trong cùng nhóm vẫn có:

* projection (W_i^Q) riêng;
* attention score riêng;
* attention distribution riêng;
* output head riêng.

Chỉ có K và V được dùng chung:

[
Q_i \neq Q_j
]

nhưng nếu (i,j) thuộc cùng nhóm:

[
K_{g(i)}=K_{g(j)},\qquad
V_{g(i)}=V_{g(j)}
]

Do đó các query heads vẫn có thể chú ý đến những vị trí khác nhau, dù chúng quan sát cùng một không gian K/V.

---

# 10. Phần thứ hai của bài báo: chuyển checkpoint MHA sang GQA

Một đóng góp quan trọng của bài báo không chỉ là kiến trúc GQA, mà là cách chuyển một checkpoint MHA đã được huấn luyện sang GQA hoặc MQA.

Giả sử một nhóm GQA được tạo từ các MHA heads trong tập (\mathcal{G}_j). Bài báo khởi tạo K/V head mới bằng cách lấy trung bình các projection matrices trong nhóm:

[
W_j^{K,\text{GQA}}
==================

\frac{1}{|\mathcal{G}*j|}
\sum*{i\in\mathcal{G}_j}
W_i^{K,\text{MHA}}
]

[
W_j^{V,\text{GQA}}
==================

\frac{1}{|\mathcal{G}*j|}
\sum*{i\in\mathcal{G}_j}
W_i^{V,\text{MHA}}
]

Các projection Q và output projection về cơ bản được giữ lại. Sau khi chuyển đổi, mô hình tiếp tục được pretrain trong một khoảng ngắn để thích ứng với cấu trúc mới. 

Bài báo thử ba cách khởi tạo:

1. **Mean pooling:** trung bình các K/V heads.
2. **First:** chọn một head đại diện.
3. **Random:** khởi tạo ngẫu nhiên.

Mean pooling đạt kết quả tốt nhất; chọn một head đứng thứ hai; khởi tạo ngẫu nhiên kém nhất. Cách giải thích của tác giả là mean pooling bảo tồn nhiều thông tin từ checkpoint gốc hơn. 

---

# 11. “Uptraining” là gì?

Sau khi thay đổi cấu trúc attention, checkpoint mới chưa hoàn toàn thích nghi. Các tác giả tiếp tục pretrain mô hình bằng cùng recipe và dữ liệu pretraining ban đầu.

Họ ký hiệu tỷ lệ uptraining là (\alpha). Ví dụ:

[
\alpha=0.05
]

nghĩa là tiếp tục huấn luyện bằng khoảng 5% số bước hoặc compute của quá trình pretraining gốc.

Trong thí nghiệm chính, các mô hình T5-XXL GQA/MQA được uptrain với (\alpha=0.05). Bài báo cho biết mức này tương ứng khoảng 600 TPUv3 chip-days trong setup của họ. Họ quan sát 5% uptraining tạo ra cải thiện đáng kể, còn tăng lên 10% có lợi ích giảm dần. 

Điểm thực tiễn quan trọng:

> Một tổ chức có checkpoint MHA đắt tiền không nhất thiết phải pretrain lại từ đầu để thu được lợi ích của GQA.

Tuy nhiên, recipe này đòi hỏi tiếp tục pretraining; chỉ mean-pool rồi sử dụng ngay có thể chưa đạt chất lượng tối ưu.

---

# 12. Thiết lập thí nghiệm của bài báo

Các tác giả sử dụng kiến trúc **T5.1.1**, chủ yếu so sánh:

* MHA T5-Large;
* MHA T5-XXL;
* MQA T5-XXL đã uptrain;
* GQA-8 T5-XXL đã uptrain.

GQA và MQA được áp dụng cho:

* decoder self-attention;
* decoder cross-attention;

nhưng không áp dụng cho encoder self-attention, vì encoder xử lý các token song song và memory bandwidth trong autoregressive decoding không phải là nút thắt tương tự. 

Các tác vụ đánh giá bao gồm:

* tóm tắt: CNN/Daily Mail, arXiv, PubMed, MediaSum, Multi-News;
* dịch máy: WMT 2014 English–German;
* hỏi đáp: TriviaQA.

Thời gian suy luận được đo trên TPUv4 với parallelization được tối ưu riêng cho từng mô hình. 

---

# 13. Kết quả chính

Bảng chính của bài báo báo cáo:

| Mô hình   | Thời gian suy luận | Điểm trung bình |
| --------- | -----------------: | --------------: |
| MHA-Large |             0,37 s |            46,0 |
| MHA-XXL   |             1,51 s |            47,2 |
| MQA-XXL   |             0,24 s |            46,6 |
| GQA-8-XXL |             0,28 s |            47,1 |

Trong setup này, GQA-8:

* nhanh gần MQA: 0,28 so với 0,24 giây;
* nhanh hơn nhiều so với MHA-XXL: 0,28 so với 1,51 giây;
* đạt điểm trung bình 47,1, gần như MHA-XXL với 47,2;
* tốt hơn MQA-XXL với 46,6. 

Tỷ lệ tốc độ trong thí nghiệm:

[
\frac{1.51}{0.28}\approx5.4
]

Tức GQA-8-XXL nhanh hơn MHA-XXL khoảng 5,4 lần trong **benchmark cụ thể của bài báo**. Không nên coi đây là hệ số tăng tốc phổ quát, vì nó phụ thuộc phần cứng, batch size, sequence length, kernel, sharding và hệ thống phục vụ.

---

# 14. Vì sao 8 KV groups?

Tác giả khảo sát số group:

[
G\in{1,4,8,16,32,64}
]

Trong đó:

* (G=1): MQA;
* (G=64): MHA trong cấu hình đó.

Kết quả cho thấy tăng từ 1 lên 4 hoặc 8 groups chỉ tạo thêm overhead tương đối nhỏ; khi số groups tiếp tục tăng và tiến gần MHA, thời gian suy luận tăng mạnh hơn. Tác giả chọn **8 groups** làm điểm cân bằng thuận lợi cho thí nghiệm chính. 

Tuy nhiên, “8 KV heads” không phải một hằng số tối ưu cho mọi LLM. Lựa chọn hợp lý phụ thuộc:

[
H_Q,\quad d_h,\quad
\text{model size},\quad
\text{context length},\quad
\text{tensor parallelism}
]

Điều quan trọng thường là tỷ lệ:

[
R=\frac{H_Q}{H_{KV}}
]

chứ không chỉ số KV heads tuyệt đối.

---

# 15. Tại sao chất lượng GQA gần MHA?

Có thể hiểu bằng góc nhìn capacity.

## MHA

Mỗi query head có K/V space riêng:

[
(Q_i,K_i,V_i)
]

Năng lực biểu diễn cao nhưng tốn bộ nhớ.

## MQA

Tất cả query heads dùng chung một cặp:

[
(Q_i,K,V)
]

Tiết kiệm lớn nhưng chia sẻ quá mạnh.

## GQA

Một nhóm nhỏ các query heads dùng chung K/V:

[
(Q_i,K_g,V_g)
]

Điều này vẫn tạo ra nhiều K/V subspaces khác nhau trong một layer, nhưng tránh phải có một K/V pair cho mọi query head.

Có thể xem số KV heads (G) như một **capacity knob**:

* (G) nhỏ: tiết kiệm bộ nhớ và bandwidth hơn;
* (G) lớn: capacity gần MHA hơn;
* giá trị trung gian thường mang lại Pareto trade-off tốt.

Đây là diễn giải kỹ thuật phù hợp với thiết kế và kết quả thực nghiệm của bài báo. 

---

# 16. GQA và Tensor Parallelism

Bài báo lưu ý một vấn đề của MQA khi mô hình được shard qua nhiều accelerator: chỉ có một KV head nên KV head đó có thể phải được nhân bản trên các model partitions. Điều này làm mất một phần lợi ích và gây lãng phí tài nguyên.

GQA có nhiều KV heads, nên các heads có thể được phân phối tự nhiên hơn qua các partitions. Chẳng hạn, nếu có 8 KV heads và 8 tensor-parallel ranks, mỗi rank có thể giữ một KV head tương ứng, tùy thiết kế implementation. Đây là một lý do GQA đặc biệt hấp dẫn cho mô hình lớn và hệ thống inference phân tán. 

Trong thực tế thường cần thỏa hoặc tối ưu các quan hệ như:

[
H_Q \bmod H_{KV}=0
]

và lý tưởng:

[
H_{KV} \bmod TP=0
]

hoặc ít nhất có một chiến lược replication/sharding hiệu quả.

---

# 17. GQA có làm giảm chất lượng không?

Có thể có, vì GQA giảm capacity của K/V projections so với MHA. Nhưng bài báo cho thấy với cấu hình GQA-8 và uptraining phù hợp, mức giảm rất nhỏ trong benchmark của họ.

Đây không phải bảo đảm rằng:

* mọi mô hình;
* mọi số KV heads;
* mọi tập dữ liệu;
* mọi context length;

đều giữ nguyên chất lượng.

Sự đánh đổi phụ thuộc vào:

* mức độ chia sẻ K/V;
* kích thước mô hình;
* cách huấn luyện;
* dữ liệu;
* thời lượng uptraining;
* nhiệm vụ đánh giá.

GQA thường được lựa chọn vì phần chất lượng mất đi nhỏ hơn nhiều so với lợi ích bộ nhớ và throughput.

---

# 18. Hạn chế của bài báo

Các tác giả tự nêu một số hạn chế đáng chú ý:

* Thí nghiệm chủ yếu trên mô hình encoder–decoder T5, không phải decoder-only LLM.
* Không có so sánh trực tiếp đầy đủ giữa GQA uptrained và một GQA model tương đương được pretrain từ đầu.
* Đánh giá tóm tắt chủ yếu dùng ROUGE, vốn không phản ánh đầy đủ chất lượng nội dung.
* Lợi ích memory bandwidth rõ nhất khi sequence dài, nhưng đánh giá chất lượng generation dài vốn khó.
* Kết quả timing gắn với TPU và cấu hình parallelization cụ thể. 

Bài báo dự đoán GQA có thể còn có lợi hơn trong decoder-only model, bởi các mô hình đó sử dụng decoder self-attention xuyên suốt, thay vì có encoder riêng. Đây là kỳ vọng của tác giả trong phần limitations, không phải một kết luận đã được kiểm chứng đầy đủ bởi thí nghiệm của chính bài báo. 

---

# 19. GQA so với FlashAttention

Hai kỹ thuật giải quyết các phần khác nhau và có thể dùng cùng nhau.

## GQA

Giảm số K/V heads:

[
H_{KV}<H_Q
]

Mục tiêu chính:

* giảm KV-cache capacity;
* giảm bandwidth khi đọc KV;
* giảm K/V projection parameters.

## FlashAttention

Tổ chức lại việc tính exact attention để giảm số lần đọc/ghi bộ nhớ trung gian và tránh materialize ma trận attention lớn trong HBM.

Mục tiêu chính:

* cải thiện IO efficiency của attention computation;
* giảm activation memory;
* tăng tốc training/prefill.

Do đó:

[
\text{GQA}+\text{FlashAttention}
]

là một tổ hợp tự nhiên. Bài báo cũng xếp FlashAttention vào nhóm kỹ thuật bổ sung để giảm chi phí bộ nhớ, chứ không phải đối thủ loại trừ GQA. 

---

# 20. GQA ảnh hưởng khác nhau ở prefill và decode

## Prefill

Ở giai đoạn prefill, toàn bộ prompt được xử lý song song. Tính toán attention trên nhiều token có thể tương đối compute-heavy. GQA vẫn giúp giảm:

* chi phí projection K/V;
* lượng KV phải ghi vào cache;
* một phần memory traffic.

Nhưng mức tăng tốc có thể không lớn như ở decode.

## Decode

Ở mỗi bước chỉ có một token query mới, nhưng mô hình phải đọc K/V của toàn bộ context trước đó. Đây là nơi KV-cache bandwidth trở thành vấn đề lớn.

Vì vậy GQA đặc biệt hữu ích cho:

* context dài;
* batch decoding lớn;
* continuous batching;
* serving nhiều request đồng thời;
* hệ thống bị giới hạn bởi VRAM và memory bandwidth.

---

# 21. Pseudocode đơn giản

```python
def grouped_query_attention(q, k, v, num_query_heads, num_kv_heads):
    """
    q: [batch, num_query_heads, query_len, head_dim]
    k: [batch, num_kv_heads, key_len, head_dim]
    v: [batch, num_kv_heads, key_len, head_dim]
    """
    assert num_query_heads % num_kv_heads == 0

    repeats = num_query_heads // num_kv_heads

    # Minh họa logic: mỗi KV head phục vụ nhiều query heads.
    # Implementation tối ưu thường tránh materialize bản sao vật lý.
    k_for_queries = repeat_kv_heads(k, repeats)
    v_for_queries = repeat_kv_heads(v, repeats)

    scores = q @ k_for_queries.transpose(-1, -2)
    scores = scores / sqrt(q.shape[-1])
    probs = softmax(scores, dim=-1)

    return probs @ v_for_queries
```

Điểm quan trọng là `repeat_kv_heads` thường chỉ là cách biểu diễn logic. Một kernel tốt không nên thật sự sao chép K/V (R) lần trong bộ nhớ, vì làm vậy sẽ xóa mất phần lớn lợi ích bandwidth của GQA.

---

# 22. Một lỗi implementation phổ biến

Giả sử:

```text
Q: [B, 32, Tq, D]
K: [B, 8,  Tk, D]
V: [B, 8,  Tk, D]
```

Một implementation ngây thơ tạo:

```text
K_repeated: [B, 32, Tk, D]
V_repeated: [B, 32, Tk, D]
```

bằng cách copy dữ liệu thực sự.

Về toán học kết quả đúng, nhưng về hệ thống:

* bộ nhớ tạm tăng;
* bandwidth tăng;
* lợi ích của GQA giảm.

Implementation hiệu quả nên dùng:

* broadcasting/view;
* grouped kernel;
* paged-attention kernel hỗ trợ `num_kv_heads`;
* FlashAttention kernel có GQA/MQA support.

---

# 23. Khi nào nên dùng MHA, GQA hay MQA?

| Kiến trúc | Chất lượng/capacity      | KV cache               | Decode                |
| --------- | ------------------------ | ---------------------- | --------------------- |
| MHA       | Cao nhất về mặt cấu trúc | Lớn nhất               | Thường chậm hơn       |
| GQA       | Gần MHA                  | Giảm theo (H_Q/H_{KV}) | Nhanh, cân bằng tốt   |
| MQA       | Chia sẻ mạnh nhất        | Nhỏ nhất               | Thường tiết kiệm nhất |

**MHA** hợp lý khi chất lượng tối đa quan trọng hơn chi phí serving hoặc context tương đối ngắn.

**GQA** thường là lựa chọn cân bằng cho LLM production: cần context dài, throughput cao nhưng không muốn dùng mức chia sẻ cực đoan của MQA.

**MQA** phù hợp khi memory/latency là ưu tiên hàng đầu và mức suy giảm chất lượng được chấp nhận hoặc đã được xử lý tốt trong pretraining.

---

# 24. Ý nghĩa lớn nhất của bài báo

Giá trị của GQA không nằm ở một công thức attention hoàn toàn mới. Điểm quan trọng hơn là bài báo xác định một trục thiết kế rõ ràng:

[
\text{số query heads}
\quad \text{và} \quad
\text{số KV heads}
]

không nhất thiết phải bằng nhau.

Bằng cách tách hai đại lượng này, nhà thiết kế mô hình có thể điều chỉnh độc lập:

* khả năng đa dạng hóa truy vấn;
* dung lượng K/V representation;
* KV-cache footprint;
* memory bandwidth;
* khả năng sharding;
* tốc độ decoding.

Kết luận cốt lõi của bài báo là:

> Không cần chọn cực đoan giữa MHA chất lượng cao nhưng đắt và MQA rất nhanh nhưng chia sẻ quá mạnh. Một số lượng KV groups trung gian có thể đạt gần như cả hai mục tiêu.

Trong thí nghiệm của tác giả, GQA-8 đạt chất lượng gần MHA-XXL với tốc độ gần MQA-XXL, đồng thời có thể được tạo từ checkpoint MHA bằng mean pooling và khoảng 5% additional pretraining compute. 

[1]: https://arxiv.org/abs/2305.13245?utm_source=chatgpt.com "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"
[2]: https://arxiv.org/abs/1706.03762?utm_source=chatgpt.com "Attention Is All You Need"
[3]: https://arxiv.org/abs/1911.02150?utm_source=chatgpt.com "Fast Transformer Decoding: One Write-Head is All You Need"
