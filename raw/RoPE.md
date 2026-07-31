## 1. Bài báo RoPE là gì?

**RoPE** được giới thiệu trong bài:

> **RoFormer: Enhanced Transformer with Rotary Position Embedding**
> Jianlin Su, Yu Lu, Shengfeng Pan, Ahmed Murtadha, Bo Wen và Yunfeng Liu, công bố lần đầu năm 2021.

Mục tiêu của bài báo là đưa thông tin vị trí vào Transformer theo cách:

* Không cộng trực tiếp vector vị trí vào token embedding.
* Mã hóa vị trí tuyệt đối bằng phép quay.
* Làm cho tích vô hướng giữa query và key phụ thuộc tự nhiên vào **khoảng cách tương đối** giữa hai token.

Các tác giả gọi Transformer sử dụng RoPE là **RoFormer**. ([arXiv][1])

---

# 2. Vì sao Transformer cần positional encoding?

Self-attention cơ bản tính:

[
\operatorname{Attention}(Q,K,V)
===============================

\operatorname{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}
\right)V
]

Nếu chỉ nhìn các token embedding, self-attention gần như không biết token nào đứng trước hoặc đứng sau. Việc hoán đổi thứ tự token sẽ không tự động tạo ra thông tin vị trí đúng nghĩa.

Ví dụ:

* “chó cắn người”
* “người cắn chó”

Hai câu có cùng tập token nhưng ý nghĩa khác hẳn do thứ tự.

Transformer gốc giải quyết bằng cách cộng positional encoding:

[
h_m=x_m+p_m
]

trong đó:

* (x_m): embedding của token tại vị trí (m)
* (p_m): vector biểu diễn vị trí (m)

Với RoPE, thay vì cộng (p_m), mô hình **xoay query và key theo vị trí của token**. ([ar5iv][2])

---

# 3. Trực giác quan trọng nhất của RoPE

Hãy xét một vector hai chiều:

[
x=
\begin{bmatrix}
x_1\
x_2
\end{bmatrix}
]

Phép quay vector này một góc (\phi) được viết:

[
R_\phi x
========

\begin{bmatrix}
\cos\phi & -\sin\phi\
\sin\phi & \cos\phi
\end{bmatrix}
\begin{bmatrix}
x_1\
x_2
\end{bmatrix}
]

RoPE chọn góc quay tỷ lệ với vị trí:

[
\phi=m\theta
]

Do đó token ở vị trí (m) được quay một góc (m\theta):

[
\operatorname{RoPE}(x,m)=R_{m\theta}x
]

Ví dụ:

* Token tại vị trí 0: quay (0\theta)
* Token tại vị trí 1: quay (\theta)
* Token tại vị trí 2: quay (2\theta)
* Token tại vị trí 10: quay (10\theta)

Nội dung của vector vẫn được giữ lại, nhưng “hướng” của nó trong không gian đã mang thông tin vị trí.

Một tính chất quan trọng của phép quay là bảo toàn độ dài:

[
|R_{m\theta}x|=|x|
]

Do ma trận quay là ma trận trực giao, RoPE không làm tăng hoặc giảm trực tiếp chuẩn của query và key. ([ar5iv][2])

---

# 4. Tại sao vị trí tương đối tự xuất hiện?

Giả sử query ở vị trí (m) và key ở vị trí (n):

[
q_m'=R_mq_m
]

[
k_n'=R_nk_n
]

Attention score là:

[
(q_m')^\top k_n'
================

(R_mq_m)^\top(R_nk_n)
]

Biến đổi:

[
(q_m')^\top k_n'
================

q_m^\top R_m^\top R_n k_n
]

Với ma trận quay:

[
R_m^\top=R_{-m}
]

và:

[
R_{-m}R_n=R_{n-m}
]

nên:

[
\boxed{
(q_m')^\top k_n'
================

q_m^\top R_{n-m}k_n
}
]

Đây là kết quả trung tâm của RoPE.

Attention score không còn phụ thuộc riêng biệt vào (m) và (n), mà phụ thuộc vào:

[
n-m
]

tức là **vị trí tương đối giữa query và key**. Đây chính là ràng buộc mà các tác giả đặt ra khi xây dựng RoPE. ([ar5iv][2])

### Tính bất biến khi dịch chuyển

Nếu đồng thời dịch cả hai token thêm (c) vị trí:

[
m'=m+c,\qquad n'=n+c
]

thì:

[
n'-m'=(n+c)-(m+c)=n-m
]

Vì vậy quan hệ attention dựa trên vị trí giữa chúng không thay đổi.

Ví dụ, khoảng cách giữa vị trí 3 và 8 giống khoảng cách giữa 103 và 108.

---

# 5. Mở rộng từ 2 chiều lên (d) chiều

Query và key trong Transformer thường có hàng chục hoặc hàng trăm chiều mỗi head. RoPE chia vector thành các cặp tọa độ:

[
(x_0,x_1),;(x_2,x_3),\ldots,(x_{d-2},x_{d-1})
]

Mỗi cặp được xem như một vector hai chiều và được quay bằng một tần số khác nhau.

Với cặp thứ (i):

[
\theta_i=10000^{-2i/d}
]

Tại vị trí (m), góc quay là:

[
m\theta_i
]

Do đó:

[
\begin{aligned}
x'*{2i}
&=
x*{2i}\cos(m\theta_i)
---------------------

x_{2i+1}\sin(m\theta_i)
\
x'*{2i+1}
&=
x*{2i}\sin(m\theta_i)
+
x_{2i+1}\cos(m\theta_i)
\end{aligned}
]

Toàn bộ ma trận RoPE là một ma trận block-diagonal:

[
R_m=
\begin{bmatrix}
R(m\theta_0) & 0 & \cdots & 0\
0 & R(m\theta_1) & \cdots & 0\
\vdots & & \ddots & \vdots\
0 & \cdots & 0 & R(m\theta_{d/2-1})
\end{bmatrix}
]

Các cặp chiều đầu có tần số cao hơn, còn các cặp sau thay đổi chậm hơn. Cấu trúc đa tần số này tương tự ý tưởng sinusoidal positional encoding, nhưng RoPE sử dụng sin và cos để **nhân và quay vector**, thay vì cộng một vector vị trí vào embedding. ([ar5iv][2])

---

# 6. RoPE được áp dụng ở đâu trong LLM?

Quy trình attention thông thường:

[
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
]

Sau khi tạo (Q) và (K), RoPE được áp dụng:

[
\widetilde Q_m=R_mQ_m
]

[
\widetilde K_m=R_mK_m
]

Sau đó attention được tính:

[
A=
\operatorname{softmax}
\left(
\frac{\widetilde Q\widetilde K^\top}{\sqrt{d_k}}
+\text{mask}
\right)
]

[
O=AV
]

Điểm cần chú ý:

[
\boxed{\text{RoPE thường áp dụng lên }Q\text{ và }K,\text{ không áp dụng lên }V}
]

Lý do là thông tin vị trí tương đối cần xuất hiện trong attention score (QK^\top). Value giữ nội dung mà attention sẽ tổng hợp.

RoPE thường được áp dụng độc lập trong từng attention head. Một số kiến trúc chỉ xoay một phần kích thước của mỗi head, gọi là **partial rotary embedding**.

---

# 7. Cách cài đặt hiệu quả

Không cần tạo ma trận quay đầy đủ. Ta có thể viết:

[
\operatorname{RoPE}(x)
======================

x\odot \cos\phi
+
\operatorname{rotate_half}(x)\odot\sin\phi
]

Trong đó `rotate_half` biến mỗi cặp:

[
(a,b)\longrightarrow(-b,a)
]

Một phiên bản PyTorch đơn giản:

```python
import torch


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """
    Với cách bố trí interleaved:
    (..., x0, x1, x2, x3, ...)
      -> (..., -x1, x0, -x3, x2, ...)
    """
    if x.shape[-1] % 2 != 0:
        raise ValueError("Rotary dimension must be even.")

    x_pairs = x.reshape(*x.shape[:-1], -1, 2)
    x1 = x_pairs[..., 0]
    x2 = x_pairs[..., 1]

    rotated = torch.stack((-x2, x1), dim=-1)
    return rotated.flatten(-2)


def apply_rope(
    x: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> torch.Tensor:
    """
    x:   [batch, heads, seq_len, rotary_dim]
    cos: broadcast được tới shape của x
    sin: broadcast được tới shape của x
    """
    return x * cos + rotate_half(x) * sin
```

Tạo tần số:

```python
def build_rope_cache(
    seq_len: int,
    head_dim: int,
    base: float = 10_000.0,
    device: torch.device | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    if head_dim % 2 != 0:
        raise ValueError("head_dim must be even.")

    pair_indices = torch.arange(
        0, head_dim, 2, dtype=torch.float32, device=device
    )

    inv_freq = 1.0 / (
        base ** (pair_indices / head_dim)
    )

    positions = torch.arange(
        seq_len, dtype=torch.float32, device=device
    )

    # [seq_len, head_dim / 2]
    angles = torch.outer(positions, inv_freq)

    # Interleave để tương ứng với từng cặp tọa độ.
    angles = torch.repeat_interleave(angles, repeats=2, dim=-1)

    # [1, 1, seq_len, head_dim]
    cos = angles.cos()[None, None, :, :]
    sin = angles.sin()[None, None, :, :]

    return cos, sin
```

Áp dụng:

```python
cos, sin = build_rope_cache(
    seq_len=q.shape[-2],
    head_dim=q.shape[-1],
    device=q.device,
)

q_rot = apply_rope(q, cos, sin)
k_rot = apply_rope(k, cos, sin)

scores = q_rot @ k_rot.transpose(-1, -2)
scores = scores / (q.shape[-1] ** 0.5)
```

Trong triển khai thực tế, cần kiểm tra cách ghép chiều vì có hai quy ước phổ biến:

1. **Interleaved:** ghép ((x_0,x_1), (x_2,x_3)).
2. **Split-half:** ghép nửa đầu vector với nửa sau.

Hai cách có thể tương đương về mặt toán học khi dùng nhất quán, nhưng không thể trộn checkpoint của quy ước này với hàm RoPE của quy ước kia.

---

# 8. Biểu diễn bằng số phức

Mỗi cặp hai chiều có thể được xem là một số phức:

[
z_i=x_{2i}+jx_{2i+1}
]

RoPE trở thành:

[
z_i'=z_i e^{jm\theta_i}
]

Với query tại (m) và key tại (n):

[
(q_ie^{jm\theta_i})
\overline{(k_ie^{jn\theta_i})}
==============================

q_i\overline{k_i}e^{j(m-n)\theta_i}
]

Dấu liên hợp làm xuất hiện hiệu góc:

[
m\theta_i-n\theta_i=(m-n)\theta_i
]

Đây là cách ngắn gọn nhất để thấy tại sao vị trí tương đối xuất hiện.

---

# 9. So sánh với các phương pháp positional encoding khác

| Phương pháp                | Cách đưa vị trí vào                      | Đặc điểm                                              |
| -------------------------- | ---------------------------------------- | ----------------------------------------------------- |
| Learned absolute embedding | Cộng vector học được (p_m) vào token     | Đơn giản nhưng thường gắn với số vị trí đã huấn luyện |
| Sinusoidal absolute        | Cộng sin/cos vào token                   | Không cần học tham số vị trí                          |
| Relative-position bias     | Cộng bias (b_{m-n}) vào attention logits | Mã hóa trực tiếp khoảng cách tương đối                |
| ALiBi                      | Cộng độ lệch tuyến tính theo khoảng cách | Đơn giản, tạo xu hướng ưu tiên token gần              |
| RoPE                       | Xoay (Q,K) theo vị trí                   | Vị trí tương đối xuất hiện trong tích vô hướng        |

Điểm khác biệt bản chất là:

[
\text{Absolute PE: }x_m+p_m
]

trong khi:

[
\text{RoPE: }R_mW_Qx_m,;R_mW_Kx_m
]

RoPE là một phép biến đổi **nhân**, không phải phép cộng. Các tác giả nhấn mạnh đây là một khác biệt quan trọng so với phần lớn phương pháp trước đó. ([ar5iv][2])

---

# 10. Ưu điểm chính của RoPE

### Không có embedding vị trí học được

Sin và cos được tính từ công thức cố định, nên RoPE hầu như không thêm tham số mô hình.

### Mã hóa vị trí tương đối tự nhiên

Tính chất:

[
R_m^\top R_n=R_{n-m}
]

đưa khoảng cách tương đối trực tiếp vào attention score.

### Bảo toàn chuẩn vector

Vì (R_m) là trực giao:

[
|R_mx|=|x|
]

Điều này giúp phép mã hóa không làm thay đổi độ lớn của (Q) và (K) chỉ vì vị trí.

### Tính toán nhẹ

Chỉ cần nhân theo phần tử với bảng sin/cos và hoán đổi một số chiều. Không cần tạo ma trận vị trí (N\times N).

### Thích hợp với KV cache

Khi sinh token tự hồi quy, key tại mỗi vị trí có thể được xoay một lần rồi lưu vào KV cache. Query mới chỉ cần dùng góc tương ứng với vị trí hiện tại.

### Có thể tính cho vị trí chưa xuất hiện

Không có bảng embedding hữu hạn kiểu:

[
P\in\mathbb{R}^{L_{\max}\times d}
]

Về mặt cơ học, ta có thể tính sin/cos cho vị trí lớn tùy ý. Bài báo mô tả điều này như sự linh hoạt về chiều dài chuỗi. ([ar5iv][2])

---

# 11. Hạn chế quan trọng: RoPE không tự động giải quyết long context

Đây là điểm dễ bị hiểu sai nhất.

Việc có thể tính:

[
R_m
]

cho (m) rất lớn **không đồng nghĩa** mô hình sẽ hoạt động tốt ở độ dài lớn hơn nhiều so với lúc huấn luyện.

Giả sử mô hình được huấn luyện tối đa 4.096 token nhưng chạy ở 100.000 token. Khi đó:

* Một số góc quay vượt rất xa phạm vi đã quan sát.
* Các chiều tần số cao quay nhiều vòng.
* Mẫu pha tại vị trí dài có thể rất khác dữ liệu huấn luyện.
* Attention có thể khó phân biệt hoặc sử dụng chính xác khoảng cách xa.
* Khả năng truy xuất thông tin thường giảm dần theo độ dài.

Vì vậy cần phân biệt:

[
\text{Có thể tính vị trí dài}
\neq
\text{Suy rộng độ dài tốt}
]

Bài gốc nêu các tính chất lý thuyết như tính linh hoạt về chiều dài và xu hướng suy giảm quan hệ khi khoảng cách tăng, nhưng chất lượng extrapolation thực tế còn phụ thuộc vào huấn luyện, dữ liệu, cấu hình tần số và kỹ thuật mở rộng ngữ cảnh. ([ar5iv][2])

---

# 12. “Long-term decay” trong bài báo nghĩa là gì?

Bài báo lập luận rằng với tập tần số:

[
\theta_i=10000^{-2i/d}
]

tổng đóng góp của nhiều thành phần dao động có xu hướng giảm khi khoảng cách tương đối tăng.

Attention score có dạng tổng:

[
\sum_i
a_i\cos((m-n)\theta_i)
+
b_i\sin((m-n)\theta_i)
]

Khi (|m-n|) lớn, các thành phần với tần số khác nhau dễ lệch pha và triệt tiêu lẫn nhau hơn. Điều này tạo ra một loại thiên kiến mềm rằng token gần thường liên hệ mạnh hơn token rất xa.

Tuy nhiên, đây không phải một hàm giảm đơn điệu bắt buộc cho mọi query và key. Do sin/cos dao động, một số khoảng cách xa vẫn có thể tạo score lớn tùy nội dung. Nên hiểu nó là **xu hướng tổng thể**, không phải một quy tắc cứng. Bài báo trình bày đặc tính suy giảm dài hạn trong phần phân tích lý thuyết. ([ar5iv][2])

---

# 13. Các kỹ thuật mở rộng context dựa trên RoPE

Khi muốn dùng mô hình ở context dài hơn lúc huấn luyện, ý tưởng chung là điều chỉnh ánh xạ từ vị trí đến góc.

RoPE gốc:

[
\phi_{m,i}=m\theta_i
]

Một cách đơn giản là position interpolation:

[
\phi_{m,i}
==========

\frac{m}{s}\theta_i
]

với (s>1). Như vậy context dài được “nén” vào miền góc gần với miền đã học.

Các biến thể khác có thể:

* Thay đổi `base` hay (\theta_i).
* Scale khác nhau theo từng nhóm tần số.
* Giữ tần số thấp và nén tần số cao.
* Fine-tune thêm trên chuỗi dài.
* Kết hợp scaling với lịch huấn luyện dài-ngữ-cảnh.

Những phương pháp này không phải nội dung cốt lõi của bài RoFormer ban đầu, mà là các phát triển sau đó nhằm khắc phục hạn chế extrapolation của RoPE nguyên bản.

---

# 14. RoPE và causal attention

Trong decoder-only LLM, RoPE không thay thế causal mask.

RoPE trả lời câu hỏi:

> Hai token cách nhau bao xa và mối quan hệ pha giữa chúng là gì?

Causal mask trả lời:

> Token hiện tại có được phép nhìn token tương lai không?

Attention đầy đủ vẫn là:

[
\operatorname{softmax}
\left(
\frac{\operatorname{RoPE}(Q)
\operatorname{RoPE}(K)^\top}
{\sqrt{d_k}}
+
M_{\text{causal}}
\right)V
]

với:

[
M_{m,n}=
\begin{cases}
0,&n\le m\
-\infty,&n>m
\end{cases}
]

Hai thành phần giải quyết hai vấn đề khác nhau.

---

# 15. Ví dụ trực quan nhỏ

Giả sử chỉ có một cặp chiều, với:

[
q=
\begin{bmatrix}
1\0
\end{bmatrix},
\qquad
k=
\begin{bmatrix}
1\0
\end{bmatrix}
]

Sau RoPE:

[
q_m=
\begin{bmatrix}
\cos(m\theta)\
\sin(m\theta)
\end{bmatrix}
]

[
k_n=
\begin{bmatrix}
\cos(n\theta)\
\sin(n\theta)
\end{bmatrix}
]

Tích vô hướng:

[
q_m^\top k_n
============

\cos(m\theta)\cos(n\theta)
+
\sin(m\theta)\sin(n\theta)
]

Dùng công thức lượng giác:

[
q_m^\top k_n
============

\cos((m-n)\theta)
]

Ví dụ:

* Nếu (m=n), score vị trí là (\cos(0)=1).
* Nếu cách nhau một token, score là (\cos(\theta)).
* Nếu cách nhau năm token, score là (\cos(5\theta)).

Attention đã nhận được thông tin về khoảng cách mà không cần một bảng relative-position embedding riêng.

---

# 16. Kết quả và phạm vi của bài báo gốc

Bài báo không chỉ trình bày RoPE như một mẹo cho decoder LLM. Các tác giả xây dựng **RoFormer**, thay thế positional embedding tuyệt đối bằng RoPE và thử nghiệm trên nhiều nhiệm vụ, trong đó có phân loại văn bản dài, dịch máy và mô hình tiền huấn luyện tiếng Trung. Họ báo cáo RoFormer nhìn chung vượt các baseline positional encoding được so sánh trong thiết lập của bài. ([ar5iv][2])

Tuy nhiên, cần đọc kết quả đúng bối cảnh:

* Bài được xây dựng quanh RoFormer và các benchmark tại thời điểm đó.
* Kết quả không chứng minh RoPE luôn tốt nhất cho mọi kiến trúc.
* Nó cũng không chứng minh RoPE nguyên bản có thể extrapolate hoàn hảo tới context tùy ý.
* Tầm ảnh hưởng lớn nhất của bài nằm ở công thức đơn giản, hiệu quả và dễ tích hợp vào attention.

---

# 17. Tóm tắt bản chất RoPE

Có thể ghi nhớ RoPE bằng bốn dòng:

[
Q_m=W_Qx_m,\qquad K_n=W_Kx_n
]

[
\widetilde Q_m=R_mQ_m
]

[
\widetilde K_n=R_nK_n
]

[
\widetilde Q_m^\top\widetilde K_n
=================================

Q_m^\top R_{n-m}K_n
]

Tức là:

> **Mỗi token xoay query và key theo vị trí tuyệt đối của nó; khi hai vector được so sánh, hiệu giữa hai góc quay biến thành vị trí tương đối.**

Đây là ý tưởng trung tâm khiến RoPE vừa gọn, vừa có diễn giải hình học rõ ràng, vừa phù hợp với attention trong LLM.

[1]: https://arxiv.org/abs/2104.09864?utm_source=chatgpt.com "RoFormer: Enhanced Transformer with Rotary Position Embedding"
[2]: https://ar5iv.labs.arxiv.org/html/2104.09864 "[2104.09864] RoFormer: Enhanced Transformer with Rotary Position Embedding"
