## Bài báo chính

Trong bối cảnh LLM, “bài báo Muon Optimizer” thường chỉ technical report:

**“Muon is Scalable for LLM Training”** — Kimi Team, Moonshot AI và UCLA, công bố ngày **24/2/2025**, arXiv:2502.16982. Bài báo mở rộng thuật toán Muon ban đầu của Keller Jordan để có thể huấn luyện mô hình ngôn ngữ quy mô hàng tỷ tham số. ([arXiv][1])

Muon là viết tắt của:

> **MomentUm Orthogonalized by Newton-Schulz**

Ý tưởng cốt lõi là: thay vì chuẩn hóa gradient theo từng phần tử như AdamW, Muon xem gradient của một lớp tuyến tính là **một ma trận**, rồi “trực giao hóa” ma trận momentum trước khi cập nhật trọng số.

---

# 1. Vấn đề với AdamW

Giả sử lớp tuyến tính có ma trận trọng số:

[
W\in\mathbb{R}^{A\times B}.
]

AdamW xử lý mỗi phần tử của gradient gần như độc lập:

[
\Delta W_{ij}
\approx
-\eta
\frac{m_{ij}}
{\sqrt{v_{ij}}+\epsilon}.
]

Cách này rất hiệu quả, nhưng không sử dụng trực tiếp cấu trúc ma trận của lớp tuyến tính.

Trong Transformer, gradient hoặc momentum của các ma trận Q, K, V, O và MLP thường có phổ singular value rất lệch: một vài singular direction rất lớn, còn nhiều hướng khác rất nhỏ. Điều đó có nghĩa là update gần như tập trung vào một không gian hạng thấp.

Muon cố gắng cân bằng lại các hướng này bằng cách biến các singular value của update về gần cùng một độ lớn. ([Keller Jordan][2])

---

# 2. Thuật toán Muon cơ bản

Muon trước hết tính momentum giống SGD:

[
M_t=\mu M_{t-1}+\nabla \mathcal{L}*t(W*{t-1}).
]

Sau đó trực giao hóa momentum:

[
O_t=\operatorname{Ortho}(M_t).
]

Cuối cùng cập nhật:

[
W_t=W_{t-1}-\eta_t O_t.
]

Trong đó (\mu) thường được đặt là (0.95). ([arXiv][1])

Nếu phân rã SVD momentum:

[
M_t=U\Sigma V^\top,
]

thì phép trực giao hóa lý tưởng là:

[
\operatorname{Ortho}(M_t)=UV^\top.
]

Nói cách khác, Muon giữ lại hai không gian singular vector (U,V), nhưng thay toàn bộ singular value trong (\Sigma) bằng 1:

[
U
\begin{bmatrix}
\sigma_1&&\
&\sigma_2&\
&&\ddots
\end{bmatrix}
V^\top
\quad\longrightarrow\quad
UIV^\top.
]

Đây còn được gọi là **polar factor** của ma trận momentum.

---

# 3. Trực giác của phép trực giao hóa

Giả sử momentum có singular value:

[
\Sigma=\operatorname{diag}(100,10,0.1,0.001).
]

SGD momentum sẽ ưu tiên gần như hoàn toàn hướng đầu tiên.

Sau trực giao hóa:

[
\Sigma'
\approx
\operatorname{diag}(1,1,1,1).
]

Do đó:

* các hướng đang quá lớn bị giới hạn;
* các hướng yếu nhưng có thể hữu ích được khuếch đại;
* update không bị chi phối bởi một vài singular direction;
* spectral norm của update được kiểm soát.

Tuy vậy, không nên hiểu rằng Muon làm các neuron “vuông góc với nhau” vĩnh viễn. Muon chỉ trực giao hóa **ma trận update tại mỗi bước**, không áp đặt trực tiếp rằng ma trận trọng số phải trực giao.

---

# 4. Tại sao không dùng SVD trực tiếp?

Tính SVD cho mọi ma trận trọng số ở mỗi training step quá đắt và khó tận dụng tốt Tensor Core.

Muon dùng một phép lặp Newton–Schulz để xấp xỉ (UV^\top).

Đầu tiên chuẩn hóa:

[
X_0=\frac{M_t}{|M_t|_F+\epsilon}.
]

Sau đó chạy khoảng 5 vòng lặp dạng đa thức:

[
X_{k+1}
=======

aX_k+
(bA_k+cA_k^2)X_k,
\qquad
A_k=X_kX_k^\top.
]

Các hệ số được triển khai trong Muon gốc là:

[
a=3.4445,\qquad
b=-4.7750,\qquad
c=2.0315.
]

Bản triển khai thường chạy phép lặp bằng **bfloat16**, gồm chủ yếu các phép nhân ma trận, nên phù hợp với GPU hiện đại. Nhóm tác giả nhận thấy 5 vòng lặp đủ tốt; tăng lên 10 làm phép trực giao chính xác hơn nhưng không cải thiện đáng kể chất lượng mô hình. ([Keller Jordan][2])

Pseudo-code đơn giản:

```python
def zeropower_via_newton_schulz(G, steps=5, eps=1e-7):
    X = G.bfloat16()
    X = X / (X.norm() + eps)

    transposed = X.shape[0] > X.shape[1]
    if transposed:
        X = X.T

    a, b, c = 3.4445, -4.7750, 2.0315

    for _ in range(steps):
        A = X @ X.T
        X = a * X + (b * A + c * A @ A) @ X

    return X.T if transposed else X
```

---

# 5. Hai thay đổi quan trọng để Muon chạy được trên LLM lớn

Đây là đóng góp trung tâm của bài báo Moonshot.

## 5.1 Thêm weight decay

Muon ban đầu không sử dụng weight decay. Khi huấn luyện dài, nhóm tác giả quan sát thấy RMS của một số trọng số và activation tiếp tục tăng, thậm chí tiến gần giới hạn biểu diễn an toàn của bf16.

Họ thêm weight decay kiểu AdamW:

[
W_t
===

## W_{t-1}

\eta_t
\left(
O_t+\lambda W_{t-1}
\right).
]

Trong thí nghiệm mô hình 800M tham số huấn luyện trên 100B token, Muon không có weight decay hội tụ nhanh ở đầu quá trình, nhưng về lâu dài kém hơn. Muon có weight decay đạt validation loss thấp hơn cả vanilla Muon và AdamW trong chế độ huấn luyện nhiều token. ([arXiv][1])

Điểm đáng chú ý là weight decay ở đây không chỉ nhằm cải thiện generalization; nó còn đóng vai trò kiểm soát scale của trọng số và ổn định numerical dynamics.

---

## 5.2 Hiệu chỉnh update theo kích thước ma trận

Với ma trận đầy đủ hạng có shape ([A,B]), bài báo chỉ ra RMS lý thuyết của update Muon là:

[
\operatorname{RMS}(O)
=====================

\sqrt{\frac{1}{\max(A,B)}}.
]

Điều này tạo ra một vấn đề khi mô hình lớn lên:

* ma trận MLP rất rộng có update quá nhỏ;
* các ma trận nhỏ, chẳng hạn từng KV head, có thể nhận update quá lớn;
* cùng một learning rate tạo ra scale update khác nhau cho mỗi loại tham số.

Để loại bỏ phụ thuộc vào shape, họ nhân update với:

[
\sqrt{\max(A,B)}.
]

Sau đó, để scale gần với update thực tế của AdamW, họ nhân thêm hệ số (0.2):

[
W_t
===

## W_{t-1}

\eta_t
\left[
0.2\sqrt{\max(A,B)},O_t
+
\lambda W_{t-1}
\right].
]

Đây là phiên bản Muon quan trọng nhất trong paper. Nhờ điều chỉnh này, nhóm tác giả có thể tái sử dụng learning rate và weight decay đã tune cho AdamW, thay vì phải tune lại toàn bộ optimizer. ([arXiv][1])

### Ví dụ

Giả sử:

[
W_{\text{attn}}\in\mathbb{R}^{4096\times4096},
]

và:

[
W_{\text{MLP}}\in\mathbb{R}^{4096\times14336}.
]

Nếu không hiệu chỉnh, update RMS tương ứng xấp xỉ:

[
\frac{1}{\sqrt{4096}}=\frac1{64},
]

và:

[
\frac{1}{\sqrt{14336}}\approx\frac1{119.7}.
]

Như vậy MLP nhận update nhỏ gần một nửa attention. Nhân với (\sqrt{\max(A,B)}) sẽ đưa chúng về cùng một scale RMS.

---

# 6. Muon không dùng cho toàn bộ tham số

Muon phù hợp chủ yếu với các tham số dạng ma trận trong hidden layers:

* attention projection: (W_Q,W_K,W_V,W_O);
* MLP up projection;
* gate projection;
* down projection;
* ma trận expert trong MoE.

Các tham số sau thường vẫn dùng AdamW:

* token embedding;
* LM head;
* bias;
* RMSNorm/LayerNorm gain;
* các scalar hoặc vector parameter;
* đôi khi router hoặc các tham số đặc biệt.

Muon gốc cũng khuyến nghị tách Q, K và V để trực giao hóa riêng, thay vì xem packed QKV như một ma trận duy nhất. ([GitHub][3])

Một cấu hình đơn giản:

```python
matrix_params = []
adamw_params = []

for name, p in model.named_parameters():
    is_hidden_matrix = (
        p.ndim == 2
        and "embed" not in name
        and "lm_head" not in name
    )

    if is_hidden_matrix:
        matrix_params.append(p)
    else:
        adamw_params.append(p)
```

Vì vậy, trong thực tế “dùng Muon” thường có nghĩa là một **hybrid optimizer**:

[
\text{Muon cho hidden matrices}
+
\text{AdamW cho phần còn lại}.
]

---

# 7. So sánh trạng thái optimizer với AdamW

AdamW lưu hai trạng thái cho mỗi tham số:

[
m_t \quad\text{và}\quad v_t,
]

tức first moment và second moment.

Muon thường chỉ cần một momentum buffer:

[
M_t.
]

Do đó, đối với các ma trận được Muon quản lý:

* optimizer-state memory thấp hơn;
* không cần second-moment tensor;
* thuận lợi hơn khi training mô hình lớn.

Trong Distributed Muon của bài báo, phần optimizer state cho Muon được báo cáo chỉ bằng khoảng một nửa AdamW, vì Muon có một momentum buffer còn AdamW có hai. ([arXiv][1])

Tuy nhiên tổng memory saving của cả mô hình còn phụ thuộc vào:

* bao nhiêu tham số vẫn dùng AdamW;
* mixed precision;
* master weights;
* ZeRO/FSDP;
* activation memory;
* tensor và pipeline parallelism.

---

# 8. Chi phí tính toán

Muon thêm các phép nhân ma trận từ Newton–Schulz. Với ma trận (n\times m), (m\le n), chi phí phụ thuộc vào khoảng:

[
O(Tnm^2),
]

với (T\approx5).

Bài viết gốc ước tính overhead tương đối gần:

[
\frac{Tm}{B},
]

trong đó:

* (m) là model dimension;
* (B) là số token trong global batch;
* (T) là số vòng Newton–Schulz.

Vì LLM thường sử dụng batch token rất lớn, overhead lý thuyết có thể nhỏ hơn 1%. Bài viết đưa ra các ví dụ khoảng 0,7% cho NanoGPT và khoảng 0,5% với cấu hình tương tự Llama 405B. Đây là ước tính FLOPs; wall-clock overhead thực tế vẫn phụ thuộc kernel, communication và cách gom các ma trận. ([Keller Jordan][2])

---

# 9. Distributed Muon

ZeRO-1 thông thường phân mảnh optimizer state giữa các data-parallel worker. Điều này dễ với AdamW vì update được tính element-wise.

Muon khó hơn vì Newton–Schulz cần nhìn thấy **toàn bộ ma trận momentum**.

Quy trình Distributed Muon của paper là:

1. Reduce-scatter gradient trên data-parallel group.
2. Cập nhật momentum trên shard cục bộ.
3. Gather các shard momentum để khôi phục ma trận đầy đủ.
4. Chạy Newton–Schulz trên ma trận.
5. Chỉ giữ lại shard update tương ứng với worker.
6. Cập nhật shard tham số.
7. All-gather tham số đã cập nhật.

Nhóm tác giả đánh giá communication volume của Distributed Muon vào khoảng (1) đến (1.25) lần Distributed AdamW; phần gather bổ sung có thể dùng bf16. ([arXiv][1])

---

# 10. Thí nghiệm scaling law

Nhóm tác giả huấn luyện một chuỗi dense Llama-style model từ khoảng:

* 399M;
* 545M;
* 822M;
* 1.1B;
* 1.5B tham số,

với số token được chọn theo compute-optimal scaling. AdamW được grid-search khá kỹ; Muon tái sử dụng hyperparameter của AdamW sau khi update RMS đã được căn chỉnh. ([arXiv][1])

Kết luận scaling-law được báo cáo:

[
\text{FLOPs}*{\text{Muon}}
\approx
0.52,
\text{FLOPs}*{\text{AdamW}}
]

để đạt mức loss tương đương.

Nói cách khác, nhóm tác giả diễn đạt kết quả này là Muon đạt gần **2× compute efficiency** so với AdamW trong compute-optimal training. Đây là kết quả empirical của thiết lập paper, không phải một bảo đảm rằng mọi mô hình đều tự động train nhanh gấp đôi. ([arXiv][1])

Cần phân biệt:

* **sample/compute efficiency:** cần ít token hoặc FLOPs hơn để đạt loss nhất định;
* **throughput mỗi bước:** số token xử lý mỗi giây;
* **wall-clock time:** tổng thời gian huấn luyện.

Muon có thể cải thiện yếu tố thứ nhất dù mỗi bước hơi đắt hơn AdamW.

---

# 11. Mô hình Moonlight

Dựa trên Muon, nhóm tác giả huấn luyện **Moonlight**, một mô hình MoE:

[
\text{2.24B active parameters}
/
\text{15.29B total parameters}
]

nếu không tính embedding; thường được gọi gần đúng là mô hình **3B active / 16B total**.

Mô hình được huấn luyện trên:

[
5.7\text{ nghìn tỷ token}.
]

Tại checkpoint 1.2T token, Moonlight dùng Muon được so sánh trực tiếp với Moonlight-A có cùng kiến trúc nhưng dùng AdamW. Một số kết quả nổi bật:

| Benchmark | AdamW | Muon |
| --------- | ----: | ---: |
| MMLU-Pro  |  26.8 | 28.1 |
| HumanEval |  29.3 | 37.2 |
| MBPP      |  49.2 | 52.9 |
| GSM8K     |  43.8 | 45.0 |
| MATH      |  16.1 | 19.8 |
| C-Eval    |  57.2 | 59.9 |

Muon không thắng ở mọi benchmark; chẳng hạn BBH trong bảng này thấp hơn AdamW. Tuy nhiên mức tăng rõ hơn xuất hiện ở nhiều bài toán code và toán. ([arXiv][1])

---

# 12. Cách diễn giải hình học

Muon có thể được nhìn như steepest descent dưới ràng buộc spectral norm.

Với gradient (G), ta muốn tìm update (\Delta W) làm giảm loss nhanh nhất, nhưng giới hạn:

[
|\Delta W|_2\le \rho,
]

trong đó (|\cdot|_2) là spectral norm.

Bài toán tuyến tính hóa:

[
\min_{|\Delta W|_2\le\rho}
\langle G,\Delta W\rangle
]

có nghiệm liên quan đến polar factor:

[
\Delta W^*
\propto
-UV^\top,
\qquad
G=U\Sigma V^\top.
]

Do ma trận trọng số của neural network hoạt động như một toán tử biến đổi hidden representation, các tác giả lập luận rằng giới hạn theo operator norm có thể tự nhiên hơn việc chuẩn hóa element-wise. ([arXiv][1])

Tuy nhiên đây là một cách giải thích lý thuyết hợp lý, chưa phải bằng chứng hoàn chỉnh rằng spectral-norm geometry là nguyên nhân duy nhất khiến Muon hoạt động tốt.

---

# 13. Điểm mạnh

**Hiệu quả dữ liệu và compute:** trong các thí nghiệm scaling law của paper, Muon đạt loss mục tiêu với khoảng 52% FLOPs của AdamW.

**Ít optimizer state hơn:** chỉ cần một momentum buffer cho các matrix parameter.

**Khai thác cấu trúc ma trận:** không xem từng phần tử trọng số hoàn toàn độc lập.

**Phù hợp GPU:** Newton–Schulz dùng matrix multiplication bf16 thay vì SVD chính xác.

**Có thể dùng learning rate gần AdamW:** nhờ quy tắc scale (0.2\sqrt{\max(A,B)}).

**Có bằng chứng ở quy mô lớn:** không chỉ NanoGPT mà còn một MoE 16B được huấn luyện trên 5.7T token. ([arXiv][1])

---

# 14. Hạn chế và câu hỏi mở

## Không phải drop-in replacement tuyệt đối

Bạn phải phân loại parameter group đúng. Dùng Muon cho embedding, LM head hoặc vector parameter có thể làm chất lượng giảm.

## Cần full matrix để trực giao hóa

Điều này làm việc kết hợp với tensor parallel, FSDP hoặc ZeRO phức tạp hơn AdamW.

## Không có per-coordinate second moment

AdamW thích nghi với noise và scale của từng tọa độ. Muon bỏ cơ chế này cho matrix parameter, nên chưa chắc tối ưu trong mọi chế độ dữ liệu, batch size hoặc fine-tuning.

## Pretraining–fine-tuning mismatch

Paper ghi nhận mô hình pretrain bằng AdamW rồi fine-tune bằng Muon, hoặc ngược lại, có thể cho kết quả kém tối ưu. Vì thế Muon chưa chắc là lựa chọn tốt để fine-tune trực tiếp một checkpoint AdamW có sẵn. ([arXiv][1])

## Kết quả chưa chứng minh tính phổ quát

Khẳng định gần 2× hiệu quả đến từ một hệ thống kiến trúc, dataset, schedule và implementation cụ thể. Khi chuyển sang model khác, hiệu quả có thể thay đổi.

## Cơ chế thực sự vẫn đang được nghiên cứu

Các giả thuyết hiện có gồm:

* tăng cường các singular direction yếu;
* điều hòa spectral norm;
* cải thiện conditioning của update;
* tạo implicit regularization;
* xử lý tốt large-batch training.

Chưa có một lý thuyết thống nhất giải thích đầy đủ toàn bộ kết quả.

---

# 15. Cấu hình thực tế khởi đầu

Theo implementation gốc và paper, một điểm khởi đầu hợp lý là:

```text
Muon parameters:
    hidden 2D weight matrices
    momentum = 0.95
    nesterov = True
    Newton–Schulz steps = 5
    weight decay = giống AdamW baseline
    learning rate = giống hoặc gần AdamW
    update scale = 0.2 * sqrt(max(A, B))

AdamW parameters:
    embeddings
    LM head
    norm weights
    biases
    scalar/vector parameters
```

Implementation gốc của Keller Jordan dùng learning rate Muon theo convention khác, ví dụ khoảng `0.02`, trong khi auxiliary AdamW dùng khoảng `3e-4`. Còn phiên bản Moonshot căn chỉnh update RMS để tái sử dụng learning rate của AdamW. Vì vậy không nên trộn hyperparameter từ hai implementation mà không kiểm tra hàm `adjust_lr` hoặc quy tắc scale update. ([GitHub][3])

---

## Kết luận

Muon thay đổi đơn vị tư duy của optimizer:

* AdamW tối ưu ở mức **phần tử**;
* Muon tối ưu ở mức **toàn bộ ma trận biến đổi**.

Công thức quan trọng nhất của phiên bản dành cho LLM là:

[
\boxed{
W_t
===

## W_{t-1}

\eta_t
\left[
0.2\sqrt{\max(A,B)}
\operatorname{NS}(M_t)
+
\lambda W_{t-1}
\right]
}
]

với:

[
M_t=\mu M_{t-1}+\nabla\mathcal L_t(W_{t-1}).
]

Giá trị của bài báo không chỉ nằm ở phép trực giao hóa, mà ở ba yếu tố kết hợp:

1. orthogonalized momentum;
2. weight decay để kiểm soát scale dài hạn;
3. hiệu chỉnh RMS theo shape để chạy ổn định khi LLM được mở rộng.

[1]: https://arxiv.org/html/2502.16982v1 "Muon is Scalable for LLM Training"
[2]: https://kellerjordan.github.io/posts/muon/ "Muon: An optimizer for hidden layers in neural networks | Keller Jordan blog"
[3]: https://github.com/KellerJordan/muon "GitHub - KellerJordan/Muon: Muon is an optimizer for hidden layers in neural networks · GitHub"
