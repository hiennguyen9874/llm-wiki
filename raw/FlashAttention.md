## FlashAttention là gì?

**FlashAttention** là một thuật toán triển khai phép **self-attention chính xác** trên GPU, được giới thiệu trong bài:

> *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness* — Tri Dao và cộng sự, NeurIPS 2022.

Ý tưởng quan trọng nhất không phải là thay đổi công thức attention, mà là **thay đổi thứ tự tính toán để giảm việc đọc/ghi dữ liệu giữa bộ nhớ GPU HBM và bộ nhớ nhanh SRAM**. Vì vậy, kết quả về mặt toán học gần như giống attention thông thường, nhưng nhanh hơn và dùng ít VRAM hơn đáng kể. ([arXiv][1])

---

# 1. Vấn đề của attention thông thường

Với một chuỗi gồm (N) token, mỗi attention head có:

[
Q,K,V \in \mathbb{R}^{N\times d}
]

Scaled dot-product attention được tính như sau:

[
S = \frac{QK^T}{\sqrt d}
]

[
P = \operatorname{softmax}(S)
]

[
O = PV
]

Trong đó:

* (S) là ma trận attention score kích thước (N\times N).
* (P) là ma trận xác suất attention kích thước (N\times N).
* (O) là đầu ra.

Một cách triển khai đơn giản thường thực hiện:

1. Tính toàn bộ (S=QK^T).
2. Ghi (S) ra HBM.
3. Đọc lại (S) để tính softmax.
4. Ghi (P) ra HBM.
5. Đọc lại (P) và (V) để tính (O=PV).

Khi context dài, hai ma trận (S) và (P) trở nên cực lớn.

Ví dụ với:

[
N=32768
]

thì mỗi attention head có:

[
N^2 \approx 1.07\text{ tỷ phần tử}
]

Chỉ một ma trận FP16 đã chiếm khoảng:

[
1.07\times10^9\times2 \approx 2.15\text{ GB}
]

Đây mới chỉ là một head và chưa tính batch, gradient, mask cùng các tensor trung gian khác.

---

# 2. Điểm nghẽn thực sự không chỉ là FLOPs

Attention vẫn có độ phức tạp tính toán:

[
O(N^2d)
]

FlashAttention **không làm mất đi độ phức tạp bậc hai về số phép toán**.

Điều bài báo nhận ra là trên GPU hiện đại, attention thường bị giới hạn bởi **memory bandwidth**, chứ không phải khả năng nhân ma trận.

GPU có nhiều tầng bộ nhớ:

| Tầng bộ nhớ        | Dung lượng |         Tốc độ |
| ------------------ | ---------: | -------------: |
| Registers          |    Rất nhỏ |     Nhanh nhất |
| SRAM/shared memory |        Nhỏ |      Rất nhanh |
| HBM/VRAM           |        Lớn | Chậm hơn nhiều |

Việc liên tục ghi và đọc ma trận (N\times N) từ HBM tốn nhiều thời gian hơn đáng kể so với các phép toán số học bổ sung.

Do đó, FlashAttention chấp nhận **tính lại một số giá trị** để giảm lượng dữ liệu phải chuyển qua HBM.

Đây là tư tưởng:

[
\text{Tăng một ít compute để giảm rất nhiều memory IO}
]

Bài báo gọi cách tiếp cận này là **IO-aware attention**. ([arXiv][1])

---

# 3. Ý tưởng chính: tiling

Thay vì tính toàn bộ ma trận:

[
QK^T \in \mathbb{R}^{N\times N}
]

FlashAttention chia (Q,K,V) thành các block nhỏ:

[
Q=
\begin{bmatrix}
Q_1\Q_2\ \vdots
\end{bmatrix},
\qquad
K=
\begin{bmatrix}
K_1\K_2\ \vdots
\end{bmatrix},
\qquad
V=
\begin{bmatrix}
V_1\V_2\ \vdots
\end{bmatrix}
]

Mỗi block đủ nhỏ để nằm trong SRAM.

Với một block (Q_i), thuật toán lần lượt tải từng cặp (K_j,V_j) vào SRAM và tính:

[
S_{ij}=Q_iK_j^T
]

Sau đó:

* áp dụng mask nếu cần;
* cập nhật softmax;
* cộng đóng góp của (V_j) vào output;
* loại bỏ (S_{ij}) khỏi SRAM.

Do đó, FlashAttention **không bao giờ lưu toàn bộ ma trận attention (N\times N) trong HBM**.

Có thể hình dung:

```text
Attention thông thường:

Q,K → toàn bộ S → HBM
S   → softmax → toàn bộ P → HBM
P,V → O


FlashAttention:

Q block + K/V block → score nhỏ trong SRAM
                    → softmax online
                    → cập nhật O
                    → bỏ score nhỏ
```

---

# 4. Khó khăn: softmax cần toàn bộ hàng

Softmax của một vector (x) là:

[
\operatorname{softmax}(x_i)
===========================

\frac{e^{x_i}}{\sum_j e^{x_j}}
]

Để tính phần tử đầu tiên, dường như ta phải biết tất cả phần tử còn lại vì cần mẫu số:

[
\sum_j e^{x_j}
]

Điều này có vẻ khiến việc chia score thành từng block trở nên bất khả thi.

FlashAttention giải quyết bằng **online softmax**.

---

# 5. Online softmax

Để tính softmax ổn định số học, ta thường sử dụng:

[
m=\max_j x_j
]

[
l=\sum_j e^{x_j-m}
]

Khi đó:

[
\operatorname{softmax}(x_i)
===========================

\frac{e^{x_i-m}}{l}
]

Giả sử đã xử lý một phần vector và lưu:

* (m_{\text{old}}): giá trị lớn nhất hiện tại;
* (l_{\text{old}}): tổng exponential đã chuẩn hóa;
* (o_{\text{old}}): output attention tích lũy.

Khi nhận block mới (x_{\text{new}}), ta tính:

[
m_{\text{block}}=\max(x_{\text{new}})
]

Giá trị max mới:

[
m_{\text{new}}
==============

\max(m_{\text{old}},m_{\text{block}})
]

Tổng chuẩn hóa mới:

[
l_{\text{new}}
==============

e^{m_{\text{old}}-m_{\text{new}}}l_{\text{old}}
+
\sum_j e^{x_{\text{new},j}-m_{\text{new}}}
]

Phần output cũ cũng được rescale:

[
o_{\text{new}}
==============

e^{m_{\text{old}}-m_{\text{new}}}o_{\text{old}}
+
\sum_j e^{x_{\text{new},j}-m_{\text{new}}}v_j
]

Sau khi đã xử lý tất cả block:

[
O=\frac{o}{l}
]

Nhờ các đại lượng chạy (m,l,o), FlashAttention có thể xử lý từng block mà không cần giữ toàn bộ hàng attention score.

---

# 6. Pseudocode đơn giản

Một phiên bản trực giác có dạng:

```python
for each query block Qi:
    m = -inf
    l = 0
    Oi = 0

    for each key/value block Kj, Vj:
        Sij = Qi @ Kj.T / sqrt(d)

        if causal:
            Sij = apply_causal_mask(Sij)

        block_max = row_max(Sij)
        new_m = maximum(m, block_max)

        Pij = exp(Sij - new_m)

        correction = exp(m - new_m)

        new_l = correction * l + row_sum(Pij)
        Oi = correction * Oi + Pij @ Vj

        m = new_m
        l = new_l

    Oi = Oi / l
```

Trong triển khai CUDA thực tế, kích thước block, thread block, warp và việc đặt dữ liệu trong register/shared memory được tối ưu rất kỹ.

---

# 7. Vì sao FlashAttention vẫn là “exact attention”?

FlashAttention không:

* bỏ token;
* xấp xỉ ma trận attention;
* dùng low-rank projection;
* giới hạn attention vào cửa sổ cục bộ;
* thay đổi công thức softmax.

Nó chỉ **đổi thứ tự các phép toán và cách dữ liệu được lưu chuyển**.

Về toán học:

[
\text{FlashAttention}(Q,K,V)
============================

\operatorname{softmax}
\left(
\frac{QK^T}{\sqrt d}
\right)V
]

Sai khác nhỏ vẫn có thể xuất hiện do:

* FP16/BF16;
* thứ tự cộng khác nhau;
* rounding;
* mixed precision.

Đây là sai khác số học thông thường, không phải approximation về mặt thuật toán.

---

# 8. Độ phức tạp

## Attention thông thường

Số phép toán:

[
O(N^2d)
]

Bộ nhớ trung gian:

[
O(N^2)
]

vì lưu ma trận attention.

## FlashAttention

Số phép toán vẫn là:

[
O(N^2d)
]

Nhưng bộ nhớ bổ sung theo chiều dài chuỗi giảm xuống gần:

[
O(Nd)
]

thay vì (O(N^2)), bởi thuật toán chỉ giữ output và một số statistics cho từng hàng.

Điểm cải thiện chính là giảm số lần truy cập HBM. Bài báo chứng minh FlashAttention đạt I/O complexity tốt hơn attention truyền thống và tối ưu trong một miền kích thước SRAM nhất định. Các nghiên cứu lý thuyết sau đó cũng xây dựng lower bound khớp với FlashAttention cho các chế độ bộ nhớ quan trọng. ([arXiv][1])

---

# 9. Backward pass

Trong huấn luyện, backward thường cần ma trận softmax (P).

Cách thông thường là lưu (P) từ forward pass:

[
P=\operatorname{softmax}(QK^T)
]

Nhưng (P) có kích thước (N\times N), nên rất tốn VRAM.

FlashAttention không lưu (P). Thay vào đó, forward chỉ lưu một số thông tin nhỏ, chẳng hạn:

* output (O);
* row-wise maximum hoặc log-sum-exp;
* các seed/counter cần thiết cho dropout.

Trong backward, thuật toán tải lại các block (Q,K,V), sau đó **tính lại các block attention score và xác suất softmax** cần thiết.

Đây là một dạng selective recomputation:

[
\text{ít memory hơn}
\quad\Longleftrightarrow\quad
\text{tính lại một số phép toán}
]

Vì phép nhân ma trận trên GPU rất nhanh nhưng việc đọc/ghi HBM đắt đỏ, sự đánh đổi này thường có lợi.

---

# 10. Causal attention trong LLM

Decoder-only LLM dùng causal mask:

[
S_{ij}=-\infty
\quad\text{nếu }j>i
]

nghĩa là token ở vị trí (i) không được nhìn các token tương lai.

FlashAttention có thể áp dụng mask ngay trên từng tile. Những block nằm hoàn toàn phía trên đường chéo có thể được bỏ qua:

```text
      K blocks
      1  2  3  4

Q 1  ✓  ×  ×  ×
  2  ✓  ✓  ×  ×
  3  ✓  ✓  ✓  ×
  4  ✓  ✓  ✓  ✓
```

Điều này tránh thực hiện một phần phép tính không cần thiết cho causal attention.

---

# 11. Kernel fusion

Attention thông thường thường tương ứng với nhiều kernel GPU:

1. GEMM cho (QK^T);
2. scaling;
3. masking;
4. softmax;
5. dropout;
6. GEMM cho (PV).

Mỗi kernel có thể phải đọc đầu vào từ HBM rồi ghi đầu ra trở lại HBM.

FlashAttention fuse nhiều công đoạn vào một kernel hoặc một chuỗi kernel được phối hợp chặt chẽ:

[
QK^T
\rightarrow
\text{scale}
\rightarrow
\text{mask}
\rightarrow
\text{softmax}
\rightarrow
PV
]

Các tensor trung gian chủ yếu tồn tại trong registers hoặc SRAM.

Tiling giảm kích thước working set; kernel fusion giảm số lần round-trip tới HBM.

---

# 12. FlashAttention giúp LLM như thế nào?

## Huấn luyện

Khi huấn luyện LLM, FlashAttention có thể:

* giảm activation memory;
* cho phép tăng sequence length;
* tăng batch size;
* giảm thời gian mỗi training step;
* giảm nhu cầu activation checkpointing ở attention;
* tăng mức sử dụng GPU.

Bài FlashAttention đầu tiên báo cáo tốc độ huấn luyện end-to-end nhanh hơn trên BERT, GPT-2 và các tác vụ chuỗi dài; mức tăng cụ thể phụ thuộc rất nhiều vào model, chiều dài chuỗi và phần cứng. ([arXiv][1])

## Prefill khi inference

Khi người dùng gửi một prompt dài, model phải xử lý toàn bộ prompt. Giai đoạn này gọi là **prefill**.

Với prompt dài (N), prefill thực hiện attention giữa nhiều token cùng lúc, nên FlashAttention đặc biệt hữu ích.

## Decode từng token

Sau prefill, model thường tạo từng token một. Ở bước decode:

* query length thường chỉ bằng 1;
* key/value đến từ KV cache;
* phép toán thường bị giới hạn bởi việc đọc KV cache.

Vì thế, lợi ích của FlashAttention trong decode có thể nhỏ hơn so với prefill. Với decode, các kỹ thuật như:

* paged KV cache;
* Multi-Query Attention;
* Grouped-Query Attention;
* KV-cache quantization;
* continuous batching;

thường đóng vai trò rất lớn.

---

# 13. FlashAttention không giải quyết điều gì?

FlashAttention giảm memory traffic và tensor trung gian, nhưng không xóa bản chất:

[
O(N^2)
]

của full attention.

Nếu tăng context từ (N) lên (2N), lượng tính toán attention vẫn tăng xấp xỉ:

[
(2N)^2=4N^2
]

Do đó, FlashAttention giúp full attention chạy hiệu quả hơn, nhưng với context cực dài vẫn có thể cần:

* sliding-window attention;
* sparse attention;
* chunked attention;
* ring attention;
* sequence parallelism;
* retrieval;
* state-space models;
* các kiến trúc attention tuyến tính hoặc lai.

FlashAttention cũng chủ yếu tối ưu **activation/intermediate memory**, không làm mất chi phí lưu trọng số model hay toàn bộ KV cache.

---

# 14. So sánh với approximate attention

| Phương pháp        | Giảm FLOPs bậc hai | Giảm memory trung gian |         Attention chính xác |
| ------------------ | -----------------: | ---------------------: | --------------------------: |
| Standard attention |              Không |                  Không |                          Có |
| FlashAttention     |              Không |                     Có |                          Có |
| Sparse attention   |             Có thể |                     Có | Không so với full attention |
| Linear attention   |                 Có |                     Có |                Thường không |
| Low-rank attention |                 Có |                     Có |                Thường không |
| Sliding window     |                 Có |                     Có |  Chỉ chính xác trong cửa sổ |

Một đóng góp quan trọng của FlashAttention là chỉ ra rằng một thuật toán có FLOPs lý thuyết giống nhau vẫn có thể nhanh hơn nhiều trong thực tế nếu tối ưu theo memory hierarchy.

---

# 15. FlashAttention-2

FlashAttention phiên bản đầu đã giảm đáng kể IO, nhưng khả năng tận dụng GPU vẫn chưa gần với GEMM tối ưu.

FlashAttention-2 tập trung vào ba vấn đề:

1. Giảm các phép toán không phải matrix multiplication.
2. Tăng song song hóa theo sequence dimension, kể cả trong một attention head.
3. Phân công công việc giữa các warp tốt hơn để giảm giao tiếp qua shared memory.

Theo bài báo, FlashAttention-2 nhanh hơn khoảng (2\times) so với FlashAttention đầu tiên trong các benchmark kernel được thử nghiệm, đạt khoảng 50–73% peak FLOPs lý thuyết trên A100 và tới 225 TFLOPs/s mỗi A100 trong một số cấu hình huấn luyện GPT. ([arXiv][2])

## Khác biệt trực giác

FlashAttention-1 tối ưu:

> Nên đưa dữ liệu vào SRAM như thế nào?

FlashAttention-2 tối ưu thêm:

> Nên chia việc cho thread block và warp như thế nào để GPU không bị nhàn rỗi?

---

# 16. FlashAttention-3

FlashAttention-3 được thiết kế để tận dụng kiến trúc NVIDIA Hopper, đặc biệt là H100.

Ba ý tưởng chính gồm:

* **warp specialization:** các warp đảm nhận vai trò khác nhau, chẳng hạn tải dữ liệu và tính toán;
* **asynchronous pipeline:** chồng lấp việc chuyển dữ liệu với Tensor Core computation;
* **interleaving GEMM và softmax:** thực hiện softmax của một block trong khi phép nhân ma trận của block khác đang chạy;
* hỗ trợ FP8 với block quantization và kỹ thuật giảm sai số.

Bài báo báo cáo mức tăng tốc khoảng 1,5–2 lần so với FlashAttention-2 trên H100 trong các cấu hình thử nghiệm, đồng thời đạt thông lượng rất cao với FP16/BF16 và FP8. ([arXiv][3])

FlashAttention-3 không đơn giản là kernel FA2 được chỉnh nhẹ; nó khai thác các đặc tính riêng của Hopper như Tensor Memory Accelerator và khả năng thực thi bất đồng bộ.

---

# 17. Ví dụ định lượng bộ nhớ

Giả sử:

* batch size (B=4);
* số head (H=32);
* sequence length (N=8192);
* FP16, 2 byte/phần tử.

Nếu lưu một ma trận attention:

[
BHN^2
=====

4\times32\times8192^2
]

Số phần tử:

[
8{,}589{,}934{,}592
]

Dung lượng:

[
8{,}589{,}934{,}592\times2
\approx17.2\text{ GB}
]

Đây chỉ là một tensor (N\times N). Trong quá trình huấn luyện, còn có softmax output, dropout, gradient và các tensor khác.

FlashAttention tránh materialize những tensor (N\times N) này trong HBM, vì vậy mức tiết kiệm tăng mạnh khi context dài. Repository chính thức minh họa memory footprint của FlashAttention tăng tuyến tính theo sequence length đối với các tensor trung gian, thay vì tăng bậc hai như triển khai attention truyền thống. ([GitHub][4])

---

# 18. Tóm tắt thuật toán bằng một câu

FlashAttention biến:

[
\boxed{
\text{tính toàn bộ attention rồi lưu các ma trận khổng lồ}
}
]

thành:

[
\boxed{
\text{tính attention từng tile trong SRAM, dùng online softmax,
và chỉ ghi output cuối ra HBM}
}
]

Ba từ khóa quan trọng nhất là:

[
\boxed{\text{Tiling + Kernel fusion + Online softmax}}
]

Và thông điệp lớn nhất của bài báo là:

> Khi tối ưu LLM trên GPU, độ phức tạp FLOPs chưa đủ; cần tối ưu cả việc dữ liệu di chuyển qua hệ thống phân cấp bộ nhớ.

[1]: https://arxiv.org/abs/2205.14135?utm_source=chatgpt.com "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
[2]: https://arxiv.org/abs/2307.08691?utm_source=chatgpt.com "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"
[3]: https://arxiv.org/abs/2407.08608?utm_source=chatgpt.com "FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision"
[4]: https://github.com/dao-ailab/flash-attention?utm_source=chatgpt.com "Dao-AILab/flash-attention: Fast and memory-efficient ..."
