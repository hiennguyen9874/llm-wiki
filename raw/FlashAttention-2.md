## FlashAttention-2 là gì?

**FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning** là công trình của Tri Dao, công bố lần đầu tháng 7/2023 và được trình bày tại ICLR 2024. Đây không phải là một biến thể attention xấp xỉ hay một kiến trúc LLM mới; nó là một thuật toán/kernel GPU tính **chính xác cùng kết quả với attention thông thường**, nhưng tổ chức phép tính và dữ liệu hiệu quả hơn nhiều. ([arXiv][1])

Mục tiêu chính của bài báo là đưa tốc độ của attention đến gần hiệu suất của phép nhân ma trận GEMM trên GPU.

---

## 1. Vấn đề của attention trong LLM

Với đầu vào:

[
Q,K,V\in \mathbb{R}^{N\times d}
]

scaled dot-product attention được tính như sau:

[
S=\frac{QK^\top}{\sqrt d}
]

[
P=\operatorname{softmax}(S)
]

[
O=PV
]

Trong đó:

* (N): độ dài chuỗi.
* (d): kích thước mỗi attention head.
* (S) và (P): ma trận (N\times N).

### Nút thắt bộ nhớ

Cài đặt attention truyền thống thường:

1. Tính toàn bộ (S=QK^\top).
2. Ghi (S) ra HBM, tức bộ nhớ GPU.
3. Đọc (S) để tính softmax.
4. Ghi (P) ra HBM.
5. Đọc (P) để nhân với (V).

Do đó, ngoài lượng tính toán (O(N^2d)), nó còn cần lưu các ma trận trung gian kích thước (O(N^2)). Khi context tăng, việc đọc và ghi HBM trở thành nút thắt nghiêm trọng.

FlashAttention-1 giải quyết vấn đề này bằng cách chia dữ liệu thành các tile, đưa từng khối nhỏ từ HBM vào SRAM nhanh trên chip, rồi dùng online softmax để không phải materialize toàn bộ ma trận attention. Nhờ vậy, bộ nhớ phụ giảm từ bậc hai xuống gần tuyến tính theo chiều dài chuỗi, trong khi kết quả vẫn là exact attention. ([arXiv][2])

---

## 2. FlashAttention-1 hoạt động như thế nào?

FlashAttention xử lý (Q,K,V) theo từng block.

Giả sử chia:

[
Q =
\begin{bmatrix}
Q_1\
Q_2\
\vdots
\end{bmatrix},
\qquad
K =
\begin{bmatrix}
K_1\
K_2\
\vdots
\end{bmatrix},
\qquad
V =
\begin{bmatrix}
V_1\
V_2\
\vdots
\end{bmatrix}
]

Với một block (Q_i), thuật toán lần lượt đọc các block (K_j,V_j), tính:

[
S_{ij}=Q_iK_j^\top
]

Sau đó cập nhật softmax và output theo kiểu streaming.

### Online softmax

Softmax thông thường của hàng (x) là:

[
\operatorname{softmax}(x_i)
===========================

\frac{e^{x_i-m}}{\sum_j e^{x_j-m}}
]

với:

[
m=\max_j x_j
]

Khi dữ liệu đến theo từng block, ta duy trì ba đại lượng:

* (m): giá trị lớn nhất đã thấy.
* (\ell): tổng mũ đã chuẩn hóa.
* (O): output tích lũy.

Giả sử trạng thái hiện tại là (m_{\text{old}},\ell_{\text{old}},O_{\text{old}}), và block mới có maximum (m_{\text{block}}). Maximum mới:

[
m_{\text{new}}
==============

\max(m_{\text{old}},m_{\text{block}})
]

Tổng chuẩn hóa mới:

[
\ell_{\text{new}}
=================

e^{m_{\text{old}}-m_{\text{new}}}\ell_{\text{old}}
+
\sum_j e^{S_j-m_{\text{new}}}
]

Output được rescale và cập nhật tương tự. Nhờ đó, mỗi hàng softmax có thể được tính chính xác mà không cần lưu toàn bộ hàng attention trong HBM.

---

## 3. Tại sao cần FlashAttention-2?

FlashAttention-1 đã giảm mạnh memory traffic, nhưng kernel vẫn chỉ đạt khoảng **25–40% hiệu suất FLOPs lý thuyết của A100**. Nguyên nhân không còn chủ yếu nằm ở HBM mà nằm ở cách chia việc giữa:

* Streaming Multiprocessor, hay SM.
* Thread block.
* Warp.
* Tensor Core và CUDA Core.

FlashAttention-2 thay đổi cách phân chia công việc để:

1. Giảm các phép tính không phải matrix multiplication.
2. Tăng số thread block có thể chạy song song.
3. Giảm giao tiếp và đồng bộ giữa các warp.

Kết quả được báo cáo là nhanh khoảng gấp đôi FlashAttention-1 và đạt khoảng **50–73% FLOPs lý thuyết của A100** trong các cấu hình được thử nghiệm. ([arXiv][1])

---

# 4. Ba cải tiến chính của FlashAttention-2

## 4.1 Giảm số phép toán ngoài matmul

GPU hiện đại đặc biệt nhanh với phép nhân ma trận chạy trên Tensor Core. Ngược lại, những phép như:

* nhân vô hướng,
* cộng,
* exponentiation,
* so sánh max,
* chia,

thường chạy trên CUDA Core và có throughput thấp hơn đáng kể.

Trong FlashAttention-1, sau khi xử lý mỗi block (K_j,V_j), output đang tích lũy thường được chia hoặc chuẩn hóa ngay:

[
O^{(j)}
=======

\frac{
\ell^{(j-1)}e^{m^{(j-1)}-m^{(j)}}O^{(j-1)}
+
P^{(j)}V_j
}{
\ell^{(j)}
}
]

FlashAttention-2 trì hoãn phép chia này. Nó giữ output ở dạng chưa chuẩn hóa:

[
\widetilde O^{(j)}
==================

e^{m^{(j-1)}-m^{(j)}}\widetilde O^{(j-1)}
+
e^{S^{(j)}-m^{(j)}}V_j
]

Chỉ sau khi tất cả block (K,V) được xử lý mới thực hiện:

[
O=\frac{\widetilde O}{\ell}
]

Như vậy, thuật toán giảm số lần rescale và chia trong vòng lặp chính.

### Với causal mask

Ở causal attention:

[
S_{ij}=-\infty \quad \text{khi } j>i
]

FlashAttention-2 cũng tránh xử lý những block hoàn toàn nằm ngoài miền causal. Việc kiểm tra mask được tổ chức ở cấp block để giảm các phép toán vô ích.

Ý tưởng tổng quát là: **đẩy tỷ trọng công việc sang matmul càng nhiều càng tốt**, vì Tensor Core xử lý matmul hiệu quả hơn các phép scalar.

---

## 4.2 Tăng song song hóa theo chiều sequence

Một attention tensor thường có các chiều:

[
[B,H,N,d]
]

Trong FlashAttention-1, cách phân chia phổ biến là mỗi thread block xử lý một attention head của một phần tử trong batch. Do đó, số thread block song song chủ yếu tỷ lệ với:

[
B\times H
]

Điều này gây vấn đề khi:

* batch size nhỏ,
* số head không lớn,
* sequence rất dài.

Ví dụ:

[
B=1,\qquad H=16,\qquad N=8192
]

Nếu chỉ có khoảng (B\times H=16) đơn vị công việc lớn, nhiều SM trên A100 có thể bị nhàn rỗi.

FlashAttention-2 chia thêm theo chiều sequence của (Q):

[
[B,H,N,d]
\longrightarrow
[B,H,N/B_r,d]
]

Trong đó mỗi thread block phụ trách một block hàng (Q_i). Tổng số block song song trở thành gần:

[
B\times H\times
\left\lceil\frac{N}{B_r}\right\rceil
]

Ví dụ, nếu mỗi block xử lý 128 token:

[
1\times16\times\frac{8192}{128}
===============================

1024
]

thread block có thể được tạo ra thay vì chỉ 16 đơn vị công việc lớn.

### Tác dụng

* GPU occupancy cao hơn.
* Nhiều SM có việc để làm hơn.
* Đặc biệt hữu ích khi sequence dài và batch nhỏ.
* Phù hợp với huấn luyện LLM context dài, nơi kích thước batch trên mỗi GPU thường bị giới hạn bởi bộ nhớ.

Bài báo mô tả đây là việc song song hóa attention của **một head duy nhất qua nhiều thread block**, thay vì buộc một head phải được xử lý như một đơn vị quá lớn. ([arXiv][1])

---

## 4.3 Thay đổi cách chia việc giữa các warp: split-Q thay vì split-K

Đây là cải tiến quan trọng ở cấp kernel.

Một CUDA thread block chứa nhiều warp; mỗi warp thường có 32 thread.

### Cách của FlashAttention-1: split-K

Trong FlashAttention-1, các warp trong cùng thread block có thể:

* dùng chung một block (Q_i),
* mỗi warp xử lý một phần khác nhau của (K_j,V_j).

Có thể hình dung:

| Warp   | Q     | K/V               |
| ------ | ----- | ----------------- |
| Warp 0 | (Q_i) | (K_{j,0},V_{j,0}) |
| Warp 1 | (Q_i) | (K_{j,1},V_{j,1}) |
| Warp 2 | (Q_i) | (K_{j,2},V_{j,2}) |
| Warp 3 | (Q_i) | (K_{j,3},V_{j,3}) |

Sau đó, các warp tạo ra các kết quả trung gian khác nhau và phải cộng chúng lại.

Điều này yêu cầu:

* ghi kết quả trung gian vào shared memory,
* đồng bộ warp,
* đọc lại,
* thực hiện reduction.

Shared memory nhanh hơn HBM, nhưng vẫn có chi phí. Đồng bộ giữa warp cũng làm giảm hiệu suất.

### Cách của FlashAttention-2: split-Q

FlashAttention-2 đảo cách chia việc:

* các warp dùng chung (K_j,V_j),
* mỗi warp xử lý một phần khác nhau của (Q_i).

| Warp   | Q         | K/V       |
| ------ | --------- | --------- |
| Warp 0 | (Q_{i,0}) | (K_j,V_j) |
| Warp 1 | (Q_{i,1}) | (K_j,V_j) |
| Warp 2 | (Q_{i,2}) | (K_j,V_j) |
| Warp 3 | (Q_{i,3}) | (K_j,V_j) |

Mỗi warp tính output cho các hàng query độc lập:

[
O_{i,0},O_{i,1},O_{i,2},O_{i,3}
]

Do các hàng query độc lập, không cần reduction giữa các warp.

### Lợi ích

* Giảm đọc/ghi shared memory.
* Giảm synchronization.
* Mỗi warp giữ kết quả của mình trong register lâu hơn.
* Đường dữ liệu từ Tensor Core đến output ngắn hơn.
* Kernel gần với hiệu suất GEMM hơn.

Bài báo mô tả việc phân chia lại công việc giữa các warp là một trong ba nguyên nhân trực tiếp tạo ra mức tăng tốc của FlashAttention-2. ([arXiv][1])

---

# 5. Forward pass trong FlashAttention-2

Ở mức khái niệm, với mỗi block (Q_i):

1. Đưa (Q_i) từ HBM vào SRAM/register.
2. Khởi tạo:
   [
   m_i=-\infty,\qquad \ell_i=0,\qquad O_i=0
   ]
3. Lặp qua các block (K_j,V_j):

   * Đọc (K_j,V_j).
   * Tính:
     [
     S_{ij}=Q_iK_j^\top
     ]
   * Áp dụng scaling và causal mask nếu có.
   * Cập nhật row maximum:
     [
     m_i^{\text{new}}
     ================

     \max\left(m_i,\operatorname{rowmax}(S_{ij})\right)
     ]
   * Tính:
     [
     P_{ij}=e^{S_{ij}-m_i^{\text{new}}}
     ]
   * Rescale trạng thái cũ:
     [
     \alpha=e^{m_i-m_i^{\text{new}}}
     ]
   * Cập nhật:
     [
     \ell_i
     \leftarrow
     \alpha\ell_i+\operatorname{rowsum}(P_{ij})
     ]
     [
     O_i
     \leftarrow
     \alpha O_i+P_{ij}V_j
     ]
   * Gán:
     [
     m_i\leftarrow m_i^{\text{new}}
     ]
4. Chuẩn hóa một lần ở cuối:
   [
   O_i\leftarrow \frac{O_i}{\ell_i}
   ]
5. Ghi (O_i) về HBM.

Điểm quan trọng là ma trận:

[
P=\operatorname{softmax}(QK^\top)
]

không bao giờ được lưu đầy đủ trong HBM.

---

# 6. Backward pass

Đối với:

[
O=PV,\qquad P=\operatorname{softmax}(S),\qquad S=QK^\top
]

gradient cơ bản là:

[
dV=P^\top dO
]

[
dP=dOV^\top
]

Gradient qua softmax:

[
dS
==

P\odot
\left(
dP-
\operatorname{rowsum}(dP\odot P)
\right)
]

Sau đó:

[
dQ=dSK
]

[
dK=dS^\top Q
]

Nếu lưu toàn bộ (P), backward sẽ tốn (O(N^2)) bộ nhớ. FlashAttention không lưu (P); thay vào đó, nó lưu một lượng nhỏ thống kê softmax, rồi **tính lại các block (S) và (P)** trong backward.

Đây là sự đánh đổi:

* Tốn thêm một số FLOPs để recompute.
* Giảm rất nhiều truy cập HBM và activation memory.

Trên GPU, recompute thường rẻ hơn việc ghi rồi đọc lại một tensor (N\times N) từ HBM.

FlashAttention-2 cũng cải thiện việc phân chia công việc trong backward. Một thách thức là nhiều block có thể cùng đóng góp vào (dQ), (dK) hoặc (dV), nên thuật toán phải chọn hướng phân chia giúp giảm atomic operation và communication.

---

# 7. Độ phức tạp

## Standard attention

Về tính toán:

[
O(N^2d)
]

Về bộ nhớ trung gian:

[
O(N^2)
]

## FlashAttention-2

Về tính toán vẫn là:

[
O(N^2d)
]

Nó không biến attention thành thuật toán tuyến tính hoặc sub-quadratic.

Nhưng bộ nhớ phụ liên quan đến attention giảm xuống gần:

[
O(N)
]

theo sequence length, vì chỉ cần lưu:

* output,
* log-sum-exp hoặc thống kê softmax,
* một số block nhỏ trong SRAM/register.

Điều này cần được phân biệt rõ:

> FlashAttention-2 không loại bỏ độ phức tạp tính toán bậc hai; nó loại bỏ phần lớn memory traffic và bộ nhớ trung gian bậc hai.

---

# 8. Kết quả thực nghiệm chính

Theo bài báo, FlashAttention-2:

* Nhanh khoảng **2× FlashAttention-1** trong nhiều cấu hình.
* Đạt khoảng **50–73% peak FLOPs/s lý thuyết của A100**.
* Đạt tối đa khoảng **225 TFLOPs/s trên mỗi A100** khi huấn luyện end-to-end mô hình kiểu GPT.
* Tương ứng với khoảng **72% model FLOPs utilization** trong cấu hình tốt nhất được báo cáo. ([arXiv][1])

Các thí nghiệm kernel xem xét những yếu tố như:

* forward và backward,
* causal và non-causal attention,
* sequence length từ ngắn đến khoảng 16K,
* head dimension 64 và 128,
* các baseline gồm PyTorch attention, xFormers/CUTLASS và FlashAttention-1.

Kết quả end-to-end được thử trên các mô hình GPT-style cỡ 1,3B và 2,7B tham số, với các context length khác nhau. ([OpenReview][3])

---

# 9. Ý nghĩa đối với LLM

## Huấn luyện context dài

Khi context length tăng từ (N) lên (2N), số phần tử của ma trận attention tăng khoảng:

[
(2N)^2=4N^2
]

Nếu lưu attention matrix, activation memory nhanh chóng trở nên không khả thi. FlashAttention-2 cho phép huấn luyện sequence dài hơn nhờ không materialize ma trận đó.

## Tăng batch size

Khi attention dùng ít activation memory hơn, phần bộ nhớ còn lại có thể được dùng cho:

* batch size lớn hơn,
* sequence dài hơn,
* mô hình lớn hơn,
* giảm activation checkpointing.

## Tăng throughput

Attention thường chiếm tỷ trọng đáng kể trong mỗi Transformer layer. Kernel attention nhanh hơn giúp:

* giảm thời gian mỗi training step,
* tăng token/giây,
* giảm chi phí huấn luyện.

Tuy vậy, tăng tốc end-to-end thường nhỏ hơn tăng tốc riêng kernel, vì LLM còn có:

* MLP,
* linear projection,
* normalization,
* communication giữa GPU,
* optimizer,
* data loading.

## Suy luận

FlashAttention-2 đặc biệt hữu ích ở:

* prefill của prompt dài,
* xử lý nhiều token query cùng lúc,
* batched inference.

Trong autoregressive decoding, mỗi bước thường chỉ có một query token mới và phải đọc KV cache. Vì vậy, decoding có thể bị memory-bandwidth-bound theo cách khác; FlashAttention-2 không tự động giải quyết toàn bộ nút thắt của KV-cache decoding.

---

# 10. FlashAttention-2 không làm gì?

Một số hiểu nhầm phổ biến:

### Không thay đổi công thức attention

Nó vẫn tính:

[
\operatorname{softmax}(QK^\top/\sqrt d)V
]

Không có approximation hay bỏ bớt token.

### Không giảm compute từ (O(N^2)) xuống (O(N))

Nó chủ yếu giảm IO và cải thiện hiệu suất phần cứng.

### Không làm mô hình thông minh hơn trực tiếp

Với cùng model, dữ liệu và precision, output về mặt toán học tương đương attention chuẩn, ngoại trừ sai khác nhỏ do thứ tự phép toán floating point.

### Không phải cơ chế như MQA hoặc GQA

* FlashAttention-2: tối ưu kernel tính toán.
* MQA/GQA: thay đổi cách tổ chức key/value head của kiến trúc.
* Cả hai có thể được sử dụng đồng thời.

### Không phải paged attention

* FlashAttention-2 tập trung vào kernel attention dạng dense.
* Paged attention tập trung vào cách quản lý KV cache trong serving.
* Hai kỹ thuật giải quyết các lớp vấn đề khác nhau.

---

# 11. So sánh nhanh

| Đặc điểm                  |          Attention chuẩn | FlashAttention-1 | FlashAttention-2 |
| ------------------------- | -----------------------: | ---------------: | ---------------: |
| Exact attention           |                       Có |               Có |               Có |
| Compute complexity        |                (O(N^2d)) |        (O(N^2d)) |        (O(N^2d)) |
| Materialize ma trận (N^2) |                Thường có |            Không |            Không |
| IO-aware tiling           |                    Không |               Có |               Có |
| Online softmax            |           Không bắt buộc |               Có |   Có, tối ưu hơn |
| Song song theo sequence   | Hạn chế/kernel-dependent |      Hạn chế hơn |          Tốt hơn |
| Phân chia warp            |       Thường chung chung |     Split-K-like |     Split-Q-like |
| Giao tiếp shared memory   |                  Cao hơn |          Đã giảm |        Giảm thêm |
| Hiệu suất A100 báo cáo    |                 Thấp hơn |      25–40% peak |      50–73% peak |

Các tỷ lệ hiệu suất trong bảng là số liệu của bài báo trên những cấu hình cụ thể, không phải bảo đảm cho mọi mô hình hoặc GPU. ([arXiv][1])

---

# 12. Trực giác ngắn gọn

Có thể hình dung attention chuẩn như sau:

> Tạo một bảng (N\times N) rất lớn, ghi bảng xuống bộ nhớ, rồi nhiều lần đọc lại để hoàn thành phép tính.

FlashAttention-1 nói:

> Không cần tạo cả bảng. Hãy xử lý từng ô vuông nhỏ trong bộ nhớ nhanh và giữ thống kê softmax đang chạy.

FlashAttention-2 nói thêm:

> Cách xử lý từng ô đã đúng, nhưng phải chia ô cho các SM và warp tốt hơn, giảm việc phụ, giảm đồng bộ, và để Tensor Core làm phần lớn công việc.

Do đó, đóng góp lớn nhất của FlashAttention-2 không nằm ở một công thức attention mới, mà ở việc **đồng thiết kế thuật toán với kiến trúc GPU**: memory hierarchy, thread block, warp, register, shared memory và Tensor Core.

[1]: https://arxiv.org/abs/2307.08691?utm_source=chatgpt.com "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"
[2]: https://arxiv.org/abs/2205.14135?utm_source=chatgpt.com "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
[3]: https://openreview.net/pdf?id=mZn2Xyh9Ec&utm_source=chatgpt.com "FLASHATTENTION-2: FASTER ATTENTION WITH ..."
