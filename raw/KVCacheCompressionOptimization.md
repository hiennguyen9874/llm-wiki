## Bài báo được nhắc tới là bài nào?

Cụm **“KV Cache Compression & Optimization”** thường được dùng như tên một **chủ đề nghiên cứu**, không phải tên duy nhất của một paper kinh điển. Paper gần khớp nhất là:

**“KV Cache Compression for Inference Efficiency in LLMs: A Review”** — Yanyu Liu và cộng sự, đăng trên arXiv tháng 8/2025. Đây là bài tổng quan, hệ thống hóa các phương pháp nén KV cache thành ba nhóm chính: **chọn lọc token, lượng tử hóa và nén/cải tiến attention**. ([arXiv][1])

Một survey rộng và kỹ thuật hơn là **“A Survey on Large Language Model Acceleration based on KV Cache Management”**, phân loại giải pháp theo ba tầng: **token-level, model-level và system-level**. ([arXiv][2])

Dưới đây là phần giải thích tổng hợp, chủ yếu dựa trên hai bài này.

---

# 1. KV cache là gì?

Trong một Transformer decoder, tại mỗi layer, hidden state của token được chiếu thành:

[
Q_t = X_tW_Q,\qquad K_t=X_tW_K,\qquad V_t=X_tW_V
]

Attention tại thời điểm (t):

[
\text{Attention}(Q_t,K_{\le t},V_{\le t})
=========================================

\text{softmax}
\left(
\frac{Q_tK_{\le t}^{T}}{\sqrt{d_h}}
\right)V_{\le t}
]

Khi sinh token tự hồi quy, các vector (K) và (V) của token cũ không thay đổi. Vì thế, thay vì tính lại chúng ở mỗi bước decoding, hệ thống lưu chúng trong **KV cache**.

Ví dụ:

* Bước 1 sinh token 1: lưu (K_1,V_1)
* Bước 2: chỉ tính (K_2,V_2), sau đó attention trên token 1–2
* Bước 3: chỉ tính (K_3,V_3), attention trên token 1–3
* Và tiếp tục tương tự

KV cache giảm rất nhiều phép tính lặp lại, nhưng đổi lại tiêu tốn bộ nhớ ngày càng lớn. Các survey xác định đây là một nút thắt quan trọng khi phục vụ LLM với context dài hoặc batch lớn. ([arXiv][1])

---

# 2. KV cache chiếm bao nhiêu bộ nhớ?

Với Multi-Head Attention tiêu chuẩn, bộ nhớ KV cache gần đúng là:

[
M_{\text{KV}}
=============

2
\times L
\times B
\times S
\times H_{\text{kv}}
\times d_h
\times b
]

Trong đó:

* (2): lưu cả Key và Value
* (L): số Transformer layers
* (B): batch size
* (S): số token trong context
* (H_{\text{kv}}): số KV heads
* (d_h): chiều của mỗi head
* (b): số byte cho mỗi phần tử

Với MHA:

[
H_{\text{kv}}=H_q
]

và vì (H_qd_h=d_{\text{model}}):

[
M_{\text{KV}}
\approx
2LBSd_{\text{model}}b
]

### Ví dụ gần đúng

Giả sử:

* 32 layers
* hidden size 4096
* FP16/BF16: 2 byte
* batch size 1
* context 32.768 token
* MHA tiêu chuẩn

Ta có:

[
M_{\text{KV}}
=============

2 \times 32 \times 1 \times 32768
\times 4096 \times 2
\approx 16\text{ GiB}
]

Đây mới chỉ là KV cache cho **một request**, chưa tính:

* model weights
* activation tạm thời
* CUDA workspace
* fragmentation
* nhiều request đồng thời

Một điểm cần chỉnh trong cách diễn đạt của bài review 2025: bài viết nói nhu cầu KV cache “tăng theo cấp số nhân” trong một số đoạn, nhưng xét theo công thức, bộ nhớ KV cache thực tế tăng **tuyến tính** theo context length và batch size. Chính bài cũng mô tả đúng quan hệ tuyến tính ở phần sau. ([arXiv][1])

---

# 3. Mục tiêu của KV cache compression

Các kỹ thuật nén KV cache cố gắng tối ưu một hoặc nhiều trục:

[
\text{Memory}
\leftrightarrow
\text{Accuracy}
\leftrightarrow
\text{Latency}
\leftrightarrow
\text{Throughput}
]

Một phương pháp tốt không chỉ làm cache nhỏ hơn. Nó còn phải tránh:

* giảm chất lượng sinh văn bản
* mất thông tin ở đầu context
* hỏng khả năng truy xuất “needle in a haystack”
* tăng overhead chọn token hoặc giải nén
* làm GPU kernel kém hiệu quả
* phá tính tương thích với batching và PagedAttention

Không có một giải pháp duy nhất tốt nhất cho mọi workload. Cách chọn phụ thuộc vào context length, phần cứng, mô hình attention và yêu cầu độ chính xác.

---

# 4. Nhóm 1: Token selection và eviction

Ý tưởng cơ bản:

> Không phải mọi token cũ đều quan trọng như nhau. Chỉ giữ KV của các token có khả năng được attention truy cập lại.

Thay vì lưu toàn bộ:

[
{(K_i,V_i)}_{i=1}^{S}
]

hệ thống chỉ lưu một tập con:

[
{(K_i,V_i):i\in\mathcal{I}},\qquad |\mathcal{I}| \ll S
]

## 4.1 Sliding-window cache

Chỉ giữ (W) token mới nhất:

[
\mathcal{I}={S-W+1,\ldots,S}
]

Ưu điểm:

* rất đơn giản
* bộ nhớ cố định
* phù hợp với local attention hoặc hội thoại chỉ phụ thuộc đoạn gần

Nhược điểm:

* làm mất thông tin xa
* kém trên retrieval, code và tài liệu dài

---

## 4.2 Sink tokens

Nhiều attention head có xu hướng đặt attention đáng kể lên một số token đầu tiên, kể cả khi chúng không có ý nghĩa ngữ nghĩa rõ ràng. Vì vậy cache thường giữ:

* vài token đầu
* một cửa sổ token gần nhất

[
\mathcal{I}
===========

{1,\ldots,S_{\text{sink}}}
\cup
{S-W+1,\ldots,S}
]

Cách này ổn định hơn sliding window thuần túy.

---

## 4.3 Heavy-hitter eviction

Phương pháp như **H2O** giữ các token đã nhận tổng attention score lớn:

[
\text{score}(i)
===============

\sum_{t>i} A_{t,i}
]

với (A_{t,i}) là attention từ query tại bước (t) tới token (i).

Cache được chia thành:

* recent tokens
* heavy hitters có attention tích lũy cao

Ý tưởng là attention thường mang tính thưa: một số ít token chi phối phần lớn khối lượng attention.

Hạn chế:

* attention trong quá khứ không đảm bảo token sẽ quan trọng trong tương lai
* cộng dồn score có thể thiên về token cũ
* việc duy trì score cũng tạo overhead

H2O, Keyformer và NACL là các phương pháp tiêu biểu được survey liệt kê trong nhóm dynamic selection có permanent eviction. ([arXiv][1])

---

## 4.4 Observation-window selection

Các phương pháp như **SnapKV** dùng một cửa sổ quan sát gần cuối prompt. Chúng xem các query gần nhất đang attention đến những token prompt nào, rồi giữ KV của các token đó cho giai đoạn decoding.

Sơ đồ:

1. Chạy prefill trên toàn prompt.
2. Lấy attention từ một cửa sổ query cuối prompt.
3. Cộng hoặc gộp attention score.
4. Giữ top-(k) token.
5. Loại phần cache còn lại trước decoding.

Ưu điểm:

* selection chỉ thực hiện một lần
* decoding không phải liên tục cập nhật cache
* hiệu quả với nhiều tác vụ long-context

Nhược điểm:

* token không quan trọng ở cuối prefill vẫn có thể trở nên quan trọng ở giai đoạn sinh sau
* permanent eviction không thể phục hồi token bị xóa

Survey rộng hơn phân biệt rõ **static selection**, **dynamic selection với permanent eviction** và **dynamic retrieval không xóa vĩnh viễn**. ([arXiv][2])

---

## 4.5 Head-aware selection

Các attention head có chức năng khác nhau:

* retrieval heads: tìm thông tin xa
* local heads: chủ yếu nhìn token gần
* syntactic heads
* positional hoặc delimiter heads

Vì vậy dùng cùng một cache policy cho mọi head là lãng phí.

Ví dụ, **RazorAttention** nhận diện retrieval heads và cấp cache đầy đủ hoặc lớn hơn cho chúng; các head còn lại sử dụng cache nén mạnh hơn. Paper review mô tả phương pháp này như một chiến lược dựa trên đặc tính của attention head và sử dụng compensation tokens để hạn chế suy giảm chất lượng. ([arXiv][1])

Ngân sách có thể biểu diễn:

[
C_h =
\begin{cases}
S,&h\in\mathcal{H}*{\text{retrieval}}\
C*{\text{small}},&\text{ngược lại}
\end{cases}
]

Đây thường hiệu quả hơn một budget đồng nhất:

[
C_1=C_2=\cdots=C_H
]

---

# 5. Nhóm 2: Budget allocation

Token selection trả lời:

> Giữ token nào?

Budget allocation trả lời:

> Mỗi layer hoặc mỗi head được phép giữ bao nhiêu token?

Một cách tổng quát:

[
\min_{{C_{l,h}}}
\mathcal{L}_{\text{quality}}
]

với ràng buộc:

[
\sum_{l,h} C_{l,h}\le C_{\text{total}}
]

Các layer không nhạy như nhau:

* layer có attention phân tán cần cache lớn hơn
* layer có attention tập trung có thể nén mạnh
* retrieval heads cần budget lớn
* local heads chỉ cần recent window

**ZigZagKV** phân bổ budget động dựa trên độ bất định của attention và hidden-state output. **SqueezeAttention** và **PyramidInfer** cũng khai thác sự không đồng nhất giữa các layer. Các phương pháp này xuất hiện trong taxonomy của các review. ([arXiv][1])

Một cấu hình “hình kim tự tháp” có thể cấp cache giảm dần theo layer:

[
C_1>C_2>\cdots>C_L
]

Tuy nhiên chiều phân bổ tối ưu phụ thuộc vào mô hình và task; không phải mô hình nào cũng thích cùng một hình dạng budget.

---

# 6. Nhóm 3: KV cache quantization

Thay vì bỏ token, quantization giữ mọi token nhưng biểu diễn mỗi phần tử bằng ít bit hơn.

Từ FP16:

[
x\in\mathbb{R}^{16\text{-bit}}
]

sang INT8, INT4, INT2 hoặc thấp hơn:

[
q =
\operatorname{clip}
\left(
\operatorname{round}\left(\frac{x-z}{s}\right),
q_{\min},q_{\max}
\right)
]

Khôi phục:

[
\hat{x}=s q+z
]

Trong đó:

* (s): scale
* (z): zero point
* (q): giá trị lượng tử hóa

### Mức tiết kiệm lý tưởng

So với FP16:

* INT8: khoảng (2\times)
* INT4: khoảng (4\times)
* INT2: khoảng (8\times)

Thực tế thấp hơn do phải lưu:

* scale
* zero point
* metadata
* alignment/padding
* residual hoặc outlier

---

## 6.1 Vì sao K và V phải xử lý khác nhau?

Sai số ở Key ảnh hưởng trực tiếp tới attention logits:

[
\ell_i=\frac{QK_i^T}{\sqrt{d_h}}
]

Nếu:

[
\hat K_i=K_i+\epsilon_i
]

thì:

[
\hat\ell_i
==========

\ell_i+
\frac{Q\epsilon_i^T}{\sqrt{d_h}}
]

Sau đó softmax có thể khuếch đại sai số, đặc biệt khi hai token có logits gần nhau.

Sai số ở Value chủ yếu ảnh hưởng tổ hợp tuyến tính cuối:

[
\hat O
======

# \sum_i A_i(V_i+\delta_i)

O+\sum_iA_i\delta_i
]

Do đó nhiều phương pháp dùng chiến lược bất đối xứng:

* Key có precision cao hơn
* Value có precision thấp hơn
* hoặc Key và Value dùng cách group khác nhau

Survey liệt kê **KIVI**, KVQuant, QAQ, AlignedKV và AsymKV trong nhóm lượng tử hóa KV cache. ([arXiv][1])

---

## 6.2 Per-token và per-channel quantization

### Per-token

Mỗi token có scale riêng:

[
s_i=
\frac{\max_j|x_{i,j}|}{q_{\max}}
]

Phù hợp khi độ lớn vector thay đổi mạnh giữa token.

### Per-channel

Mỗi chiều feature có scale riêng:

[
s_j=
\frac{\max_i|x_{i,j}|}{q_{\max}}
]

Phù hợp khi một số channel thường xuyên có outlier.

KIVI nổi bật với lượng tử hóa bất đối xứng ở mức 2 bit, dựa trên quan sát rằng phân bố outlier của Key và Value khác nhau. ([arXiv][1])

---

## 6.3 Residual cache

Để tránh lượng tử hóa token mới ngay lập tức, hệ thống có thể:

* giữ (R) token gần nhất ở FP16
* lượng tử hóa các token cũ
* khi residual buffer đầy, chuyển một block sang dạng nén

[
\text{Cache}
============

\text{Quantized old blocks}
+
\text{FP16 recent block}
]

Cách này giảm overhead cập nhật từng token và bảo vệ thông tin gần nhất.

---

## 6.4 Vấn đề thực tế của quantization

Quantization chỉ tăng tốc khi chi phí giảm memory bandwidth lớn hơn chi phí:

* dequantization
* unpack bit
* xử lý scale
* chuyển layout
* kernel launch

Một triển khai INT4 bằng Python hoặc kernel không tối ưu hoàn toàn có thể:

* dùng ít VRAM hơn
* nhưng chạy chậm hơn FP16

Vì vậy paper-level compression ratio không tự động chuyển thành production throughput tương ứng.

---

# 7. Nhóm 4: KV merging

Thay vì xóa hoàn toàn token cũ, có thể gộp các token tương tự.

Giả sử nhóm token (\mathcal{G}) có Key gần nhau:

[
\bar K =
\frac{\sum_{i\in\mathcal{G}}w_iK_i}
{\sum_{i\in\mathcal{G}}w_i}
]

[
\bar V =
\frac{\sum_{i\in\mathcal{G}}w_iV_i}
{\sum_{i\in\mathcal{G}}w_i}
]

Sau đó thay nhiều KV pairs bằng một pair đại diện.

Ưu điểm:

* ít mất thông tin hơn hard eviction
* khai thác redundancy giữa token

Nhược điểm:

* gộp Key có thể thay đổi attention distribution
* cluster hoặc similarity search tạo overhead
* position encoding, đặc biệt RoPE, làm việc gộp token ở vị trí khác nhau phức tạp hơn

**EMS** sử dụng hướng “evict-then-merge”: xóa một phần token và hợp nhất thông tin để giảm mất mát. Survey ghi nhận đây là một chiến lược thích nghi theo từng head, kết hợp global-local importance. ([arXiv][1])

---

# 8. Nhóm 5: Low-rank và sparse coding

KV tensors đôi khi có cấu trúc dư thừa trong chiều feature hoặc chiều token.

Có thể xấp xỉ:

[
K \approx U_KR_K
]

với:

[
U_K\in\mathbb{R}^{S\times r},
\qquad
R_K\in\mathbb{R}^{r\times d_h},
\qquad r\ll d_h
]

Thay vì lưu (Sd_h) phần tử, ta lưu:

[
Sr+rd_h
]

Tương tự với (V).

Một hướng khác là sparse coding:

[
K\approx DA
]

trong đó:

* (D): dictionary dùng chung
* (A): hệ số thưa

Ưu điểm:

* có thể đạt tỷ lệ nén cao
* giữ thông tin theo cách “mềm” hơn eviction

Nhược điểm:

* projection/reconstruction tốn compute
* khó cập nhật online từng token
* cần kernel chuyên dụng
* rank phù hợp thay đổi theo layer, head và request

Survey token-level rộng hơn xem low-rank decomposition là một trong năm nhóm chính, bên cạnh selection, budget allocation, merging và quantization. ([arXiv][2])

---

# 9. Nhóm 6: Model-level optimization

Đây không hẳn là nén cache sau khi sinh ra, mà là thiết kế mô hình để cache nhỏ ngay từ đầu.

## 9.1 Multi-Query Attention

MHA có:

* (H_q) query heads
* (H_q) key heads
* (H_q) value heads

MQA dùng:

[
H_{\text{kv}}=1
]

Tất cả query heads chia sẻ cùng một K/V head.

Tỷ lệ giảm cache gần đúng:

[
\frac{M_{\text{MHA}}}{M_{\text{MQA}}}
\approx H_q
]

Ưu điểm: giảm KV cache rất mạnh.

Nhược điểm: chia sẻ quá nhiều có thể giảm năng lực biểu diễn.

---

## 9.2 Grouped-Query Attention

GQA là trung gian:

[
1<H_{\text{kv}}<H_q
]

Mỗi nhóm query heads dùng chung một KV head.

Tỷ lệ giảm:

[
\frac{M_{\text{MHA}}}{M_{\text{GQA}}}
=====================================

\frac{H_q}{H_{\text{kv}}}
]

Ví dụ:

* 32 query heads
* 8 KV heads

thì KV cache giảm khoảng:

[
32/8=4\times
]

MQA/GQA thường là tối ưu “rẻ” và ổn định nhất nếu có thể chọn kiến trúc ngay từ giai đoạn huấn luyện. Survey model-level xếp các phương pháp attention grouping và sharing vào nhóm tối ưu cấu trúc mô hình. ([arXiv][2])

---

## 9.3 Cross-layer sharing

Một số layer có KV representations tương tự. Thay vì mỗi layer lưu cache riêng:

[
K^{(1)},K^{(2)},\ldots,K^{(L)}
]

có thể dùng chung hoặc tái sử dụng giữa các layer gần nhau.

**KVSharer** nghiên cứu việc chia sẻ KV cache không đồng nhất giữa các layer; review cho biết phương pháp này giảm bộ nhớ và tăng tốc inference, đồng thời có thể kết hợp với các kỹ thuật khác. ([arXiv][1])

Rủi ro là các layer không hoàn toàn tương đương; sharing quá mạnh có thể mất các representation riêng biệt theo độ sâu.

---

# 10. Nhóm 7: System-level optimization

Không phải mọi tối ưu KV đều nén dữ liệu. Nhiều giải pháp cải thiện cách bố trí và vận chuyển KV cache.

## 10.1 Paged KV cache

Thay vì cấp một vùng bộ nhớ liên tục cho toàn bộ sequence, chia cache thành block/page.

Lợi ích:

* giảm fragmentation
* cấp phát động
* batching request có độ dài khác nhau
* dễ prefix sharing
* tránh reserve toàn bộ maximum context

PagedAttention trong vLLM là ví dụ tiêu biểu của hướng quản lý bộ nhớ này.

---

## 10.2 Prefix caching

Nếu nhiều request có chung system prompt hoặc prefix:

[
P=(x_1,\ldots,x_m)
]

thì KV cache của prefix có thể được tái sử dụng.

Thay vì prefill lại (P) cho mỗi request:

[
\text{KV}(P)
]

được tính một lần và chia sẻ.

Đây không làm cache của một request nhỏ hơn, nhưng giảm:

* prefill compute
* time-to-first-token
* bộ nhớ tổng nếu pages được chia sẻ

---

## 10.3 Offloading và hierarchical cache

KV có thể đặt trên:

* GPU HBM
* CPU RAM
* NVMe
* remote/disaggregated memory

Một cache policy có thể giữ:

* KV nóng trên GPU
* KV ít dùng trên CPU
* context rất cũ trên storage

Khi cần, hệ thống prefetch lại.

Vấn đề chính chuyển từ dung lượng sang bandwidth và latency:

[
T_{\text{transfer}}
\approx
\frac{\text{KV bytes}}{\text{interconnect bandwidth}}
]

Nếu retrieval từ CPU chậm hơn thời gian attention tiết kiệm được, offloading có thể làm decoding chậm.

Survey rộng phân loại memory management và scheduling là hai thành phần chính của system-level KV optimization. ([arXiv][2])

---

# 11. Phân loại của bài review 2025

Bài **KV Cache Compression for Inference Efficiency in LLMs: A Review** tổ chức nội dung chủ yếu thành:

### A. Selective compression

* chọn token quan trọng
* eviction
* budget động
* head-aware caching
* layer sharing
* merge/fusion

Các phương pháp được nhắc đến gồm ZigZagKV, KVSharer, EMS, CacheBlend, RazorAttention và NACL. ([arXiv][1])

### B. Quantization compression

* giảm precision của K/V
* asymmetric quantization
* per-channel/per-token
* quality-adaptive bit width

Các ví dụ gồm KVQuant, KIVI, QAQ, AlignedKV và AsymKV. ([arXiv][1])

### C. Attention compression

* heavy hitters
* key-token selection
* sparsity-aware cache
* layer-wise budget
* pyramid cache
* inter-layer similarity
* MHA-to-GQA conversion

Các ví dụ được liệt kê gồm H2O, Keyformer, ALISA, SqueezeAttention và PyramidInfer. ([arXiv][1])

### D. Hybrid methods

Kết hợp nhiều hướng, chẳng hạn:

[
\text{Eviction}
+
\text{Quantization}
+
\text{Per-head budget}
+
\text{Paged memory}
]

Bài kết luận rằng hướng tương lai quan trọng là:

* hybrid optimization
* chiến lược động, thích nghi theo request
* software–hardware co-design ([arXiv][1])

---

# 12. Đánh giá ưu và nhược điểm của bài review

## Điểm mạnh

Bài đưa ra bản đồ khá dễ tiếp cận cho người mới:

* gom nhiều paper KV-cache nổi bật giai đoạn 2023–2025
* phân biệt selection, quantization và attention compression
* chú ý cả compression ratio, throughput và quality
* nhấn mạnh rằng cần kết hợp thuật toán với triển khai phần cứng

Danh mục tham khảo bao phủ nhiều phương pháp quan trọng như H2O, KIVI, KVQuant, RazorAttention, PyramidInfer, CacheBlend và GEAR. ([arXiv][1])

## Hạn chế

### 1. Taxonomy có phần chồng lấn

“Selective compression” và “attention compression” không tách biệt hoàn toàn. Ví dụ:

* H2O vừa là attention-based selection
* RazorAttention vừa là head-aware attention analysis vừa là cache eviction
* PyramidInfer vừa là budget allocation vừa là structural compression

Taxonomy token/model/system của survey 2024–2025 thường rõ ràng và tổng quát hơn. ([arXiv][2])

### 2. So sánh số liệu chưa hoàn toàn apples-to-apples

Các paper dùng:

* model khác nhau
* context length khác nhau
* GPU khác nhau
* benchmark khác nhau
* cách đo throughput khác nhau
* compression budget khác nhau

Vì vậy không nên nhìn một bảng rồi kết luận phương pháp có throughput cao nhất là tốt nhất.

### 3. Chưa phân tích đủ kernel-level overhead

Một phương pháp có compression ratio cao nhưng vẫn có thể chậm vì:

* gather KV không liên tục
* top-(k) selection
* dequantization
* irregular sparsity
* CPU–GPU transfer
* thiếu fused kernels

### 4. Một số phát biểu thiếu chính xác

Như đã lưu ý, KV cache không tăng “exponential” theo context length; nó tăng tuyến tính. Attention computation trong prefill mới thường có độ phức tạp bậc hai theo sequence length nếu dùng dense attention.

### 5. Là review, không phải một thuật toán mới

Bài này không đề xuất một compressor hoàn chỉnh để tải về triển khai. Giá trị chính của nó là:

* taxonomy
* tổng hợp paper
* hướng dẫn chọn nhóm phương pháp
* xác định khoảng trống nghiên cứu

---

# 13. Chọn phương pháp nào trong thực tế?

| Trường hợp                            | Hướng phù hợp                                          |
| ------------------------------------- | ------------------------------------------------------ |
| Mô hình đã dùng GQA/MQA               | Bắt đầu bằng paged cache và prefix caching             |
| Cần giữ chất lượng gần full-cache     | INT8/INT4 quantization hoặc hybrid nhẹ                 |
| Context rất dài, retrieval quan trọng | Head-aware selection hoặc dynamic retrieval            |
| Chat thông thường                     | Recent window + sink/heavy-hitter tokens               |
| GPU ít VRAM                           | Quantization + offload                                 |
| Batch serving lớn                     | PagedAttention + continuous batching + prefix sharing  |
| RAG có prefix/block tái sử dụng       | CacheBlend hoặc prefix/block cache                     |
| Edge device                           | GQA/MQA + low-bit KV quantization                      |
| Accuracy-critical reasoning           | Nén bảo thủ, giữ retrieval heads và recent tokens      |
| Muốn tỷ lệ nén cực cao                | Hybrid pruning + quantization, nhưng phải benchmark kỹ |

Một pipeline thực tế có thể là:

[
\boxed{
\text{GQA}
\rightarrow
\text{Paged KV}
\rightarrow
\text{Prefix cache}
\rightarrow
\text{INT4/INT8}
\rightarrow
\text{Head-aware eviction}
}
]

Thứ tự này hợp lý vì:

1. Tối ưu kiến trúc và layout thường ít mất chất lượng.
2. Quantization giữ lại toàn bộ token.
3. Eviction là bước rủi ro nhất vì thông tin đã xóa khó phục hồi.

---

# 14. Các metric cần dùng khi đánh giá

Không nên chỉ báo cáo “giảm bao nhiêu GB”. Cần đo đồng thời:

### Bộ nhớ

[
\text{Compression ratio}
========================

\frac{M_{\text{full KV}}}{M_{\text{compressed KV}}}
]

### Chất lượng

* perplexity
* exact match / F1
* LongBench score
* RULER
* Needle-in-a-Haystack
* code completion accuracy
* summarization quality

### Độ trễ

* TTFT: time to first token
* TPOT: time per output token
* inter-token latency
* prefill latency
* decode latency

### Năng suất hệ thống

* tokens/second
* requests/second
* maximum concurrent requests
* goodput dưới latency SLO

### Overhead

* thời gian selection
* quantization/dequantization
* cache migration
* metadata memory
* kernel efficiency

Survey nhấn mạnh rằng tác động lên performance và throughput phải được đánh giá cùng với memory reduction, thay vì xem tỷ lệ nén là mục tiêu độc lập. ([arXiv][1])

---

# Kết luận

Thông điệp quan trọng nhất của chủ đề **KV Cache Compression & Optimization** là:

> KV cache giúp decoding tránh tính lại quá khứ, nhưng trở thành nút thắt bộ nhớ và bandwidth khi context hoặc concurrency tăng.

Các giải pháp nằm trên bốn tầng chính:

1. **Giữ ít token hơn:** selection, eviction, merging
2. **Lưu mỗi token rẻ hơn:** quantization, low-rank, sparse coding
3. **Sinh ra ít KV hơn:** GQA, MQA, cross-layer sharing
4. **Quản lý cache tốt hơn:** paging, prefix reuse, scheduling, offloading

Trong production, giải pháp tốt thường không phải một kỹ thuật đơn lẻ mà là một **pipeline thích nghi**, kết hợp kiến trúc, nén số học và quản lý bộ nhớ. Đây cũng là hướng tương lai mà các review nhấn mạnh: hybrid optimization, dynamic policies và software–hardware co-design. ([arXiv][1])

[1]: https://arxiv.org/html/2508.06297v1 "KV Cache Compression for Inference Efficiency in LLMs: A Review"
[2]: https://arxiv.org/html/2412.19442v2 "A Survey on Large Language Model Acceleration based on KV Cache Management"
