# ALiBi trong LLM

**ALiBi** là viết tắt của **Attention with Linear Biases**, được giới thiệu trong bài:

> **Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation**
> Ofir Press, Noah A. Smith và Mike Lewis, công bố lần đầu năm 2021 và xuất bản tại ICLR 2022. ([arXiv][1])

Mục tiêu chính của bài báo là giải quyết câu hỏi:

> Một Transformer được huấn luyện với chuỗi ngắn có thể xử lý chuỗi dài hơn khi suy luận mà không cần huấn luyện lại hay không?

Ý tưởng của ALiBi rất đơn giản: **không dùng positional embedding truyền thống**, mà trừ trực tiếp một lượng tuyến tính phụ thuộc vào khoảng cách giữa query và key khỏi attention score.

---

## 1. Vấn đề vị trí trong Transformer

Self-attention thuần túy không nhận biết thứ tự token.

Giả sử ta hoán đổi vị trí các token, nếu không có thông tin vị trí thì attention gần như chỉ nhìn thấy một tập hợp vector, không biết token nào đứng trước hay sau.

Transformer thường thêm thông tin vị trí bằng một trong các cách:

* Learned absolute position embedding
* Sinusoidal position encoding
* Relative position encoding
* RoPE — Rotary Position Embedding
* ALiBi

Với absolute positional embedding, đầu vào thường là:

[
x_i = e_i + p_i
]

Trong đó:

* (e_i): embedding của token ở vị trí (i)
* (p_i): embedding vị trí (i)

Vấn đề xuất hiện khi mô hình được huấn luyện với chiều dài tối đa (L=2048), nhưng lúc inference lại nhận 4096 hoặc 8192 token.

Với learned positional embedding, các vị trí ngoài 2048 đơn giản là **chưa có embedding được học**. Với sinusoidal encoding, về toán học ta có thể tạo vị trí bất kỳ, nhưng mô hình vẫn có thể hoạt động kém vì chưa từng thấy các mẫu pha tương ứng trong quá trình training.

Bài ALiBi cho rằng chỉ cần thay đổi cách biểu diễn vị trí là có thể cải thiện đáng kể khả năng **length extrapolation**. ([arXiv][1])

---

# 2. Công thức ALiBi

## Attention thông thường

Trong một attention head, score giữa query ở vị trí (i) và key ở vị trí (j) là:

[
s_{ij}
======

\frac{q_i^\top k_j}{\sqrt{d_k}}
]

Sau đó áp dụng softmax:

[
a_{ij}
======

\operatorname{softmax}*j(s*{ij})
]

Với causal language model, token (i) chỉ được nhìn các token (j \le i).

---

## Attention với ALiBi

ALiBi sửa score thành:

[
s_{ij}^{(h)}
============

## \frac{q_i^{(h)\top} k_j^{(h)}}{\sqrt{d_k}}

m_h(i-j)
]

với:

[
j \le i
]

Trong đó:

* (h): chỉ số attention head
* (i-j): khoảng cách giữa query và key
* (m_h > 0): slope riêng của head (h)
* (m_h) là hằng số, **không được học**

Với các vị trí tương lai (j>i), causal mask vẫn đặt score thành (-\infty).

Có thể viết đầy đủ:

[
s_{ij}^{(h)}
============

\begin{cases}
\dfrac{q_i^{(h)\top}k_j^{(h)}}{\sqrt{d_k}}
------------------------------------------

m_h(i-j), & j \le i [6pt]
-\infty, & j>i
\end{cases}
]

Sau đó:

[
a_{ij}^{(h)}
============

\operatorname{softmax}*j
\left(s*{ij}^{(h)}\right)
]

Nhóm tác giả mô tả ALiBi là việc thêm một **linear bias** vào mỗi attention score; slope (m_h) phụ thuộc vào head, được đặt từ đầu và không phải tham số học được. ([GitHub][2])

---

# 3. Trực giác của linear bias

Giả sử một head có:

[
m_h = 0.1
]

Đối với query tại vị trí 100:

| Key position | Khoảng cách | ALiBi bias |
| -----------: | ----------: | ---------: |
|          100 |           0 |          0 |
|           99 |           1 |     (-0.1) |
|           95 |           5 |     (-0.5) |
|           90 |          10 |     (-1.0) |
|           50 |          50 |     (-5.0) |

Token càng xa thì attention score càng bị phạt.

Điều này tạo ra một **recency bias**:

> Khi nội dung tương đương nhau, mô hình ưu tiên token gần query hơn.

Tuy nhiên, ALiBi không cấm mô hình nhìn xa. Nếu dot product giữa query và một key ở xa đủ lớn, key đó vẫn có thể nhận attention cao.

Ví dụ:

[
\frac{q_i^\top k_j}{\sqrt{d_k}}=12
]

và penalty là (-5), score cuối vẫn là:

[
12-5=7
]

Do đó ALiBi là một **soft bias**, không phải local attention mask cứng.

---

# 4. Vì sao mỗi head có slope khác nhau?

Nếu tất cả các head dùng cùng slope, chúng sẽ có xu hướng hoạt động ở cùng một phạm vi khoảng cách.

ALiBi dùng nhiều slope khác nhau:

* Head có slope lớn: phạt khoảng cách mạnh, tập trung vào ngữ cảnh rất gần
* Head có slope nhỏ: phạt nhẹ, có thể theo dõi quan hệ xa hơn

Ví dụ trực quan:

| Head   |  Slope | Xu hướng               |
| ------ | -----: | ---------------------- |
| Head 1 |    0.5 | Rất cục bộ             |
| Head 2 |   0.25 | Cục bộ                 |
| Head 3 |  0.125 | Trung bình             |
| Head 4 | 0.0625 | Xa hơn                 |
| Head 8 | 0.0039 | Có thể quan sát rất xa |

Với 8 head, một ví dụ điển hình cho dãy slope là:

[
\frac{1}{2},
\frac{1}{4},
\frac{1}{8},
\ldots,
\frac{1}{256}
]

Các slope được phân bố theo cấp số nhân thay vì tuyến tính. Điều này cung cấp nhiều “thang thời gian” khác nhau cho attention:

* Một số head chuyên quan hệ sát nhau như cụm từ
* Một số head có thể theo dõi chủ thể qua nhiều câu
* Một số head chịu penalty rất nhỏ và xử lý phụ thuộc dài

Có thể xem đây như một dạng **multi-scale memory decay**.

---

# 5. Tại sao ALiBi extrapolate tốt hơn?

Đây là điểm quan trọng nhất của bài báo.

## Absolute positional embedding học “vị trí cụ thể”

Một learned positional embedding có thể khiến mô hình học những quy luật gắn với index cụ thể:

* Vị trí 100 thường nằm gần đầu tài liệu
* Vị trí 1024 thường nằm ở cuối context
* Không tồn tại vị trí 1025 trong training

Khi context dài hơn, mô hình gặp các vị trí hoặc tổ hợp vị trí ngoài phân phối huấn luyện.

---

## ALiBi chỉ dùng khoảng cách tương đối

ALiBi không cần một vector riêng cho vị trí 100, 1000 hay 10000.

Nó chỉ tính:

[
i-j
]

Quan hệ “cách nhau 20 token” có cùng ý nghĩa dù nó xảy ra giữa:

* Vị trí 30 và 10
* Vị trí 1030 và 1010
* Vị trí 10030 và 10010

Do đó quy tắc vị trí của ALiBi có tính **translation-invariant** theo trục chuỗi.

Khi tăng chiều dài context, ALiBi chỉ tiếp tục đường thẳng:

[
-m_h d
]

với (d) lớn hơn. Không cần:

* Sinh embedding vị trí mới
* Nội suy embedding
* Học vị trí ngoài context training
* Thay đổi tham số mô hình

Đây là lý do kiến trúc có thể chạy trên chuỗi dài hơn về mặt cơ học.

---

# 6. “Train short, test long” nghĩa là gì?

Trong thí nghiệm nổi bật, nhóm tác giả huấn luyện một mô hình khoảng **1,3 tỷ tham số** với chuỗi dài 1024 token, sau đó đánh giá trên chuỗi dài 2048 token.

Theo bài báo, mô hình ALiBi huấn luyện ở độ dài 1024 đạt perplexity tương đương mô hình dùng sinusoidal positional embedding được huấn luyện trực tiếp ở độ dài 2048. Việc huấn luyện trên chuỗi ngắn hơn giúp quá trình đó nhanh hơn khoảng 11% và sử dụng ít bộ nhớ hơn khoảng 11%. ([arXiv][1])

Thông điệp không phải là:

> Huấn luyện 1K token thì chắc chắn dùng hoàn hảo ở 1 triệu token.

Mà là:

> Cách mã hóa vị trí của ALiBi giảm đáng kể sự phụ thuộc vào chiều dài context đã thấy trong training.

---

# 7. Tại sao huấn luyện chuỗi ngắn tiết kiệm tài nguyên?

Full self-attention có độ phức tạp:

[
O(L^2)
]

về số attention score, với (L) là chiều dài chuỗi.

Nếu tăng từ 1024 lên 2048 token:

[
\frac{2048^2}{1024^2}=4
]

Ma trận attention theo từng sample lớn gấp bốn lần.

Trên thực tế, tổng chi phí training còn phụ thuộc batch size, số token mỗi batch, kernel và nhiều yếu tố khác. Vì vậy bài báo báo cáo mức tiết kiệm thực nghiệm 11%, không phải giảm đúng bốn lần toàn bộ thời gian huấn luyện. ([arXiv][1])

Điểm kinh tế của ALiBi là:

1. Train chủ yếu bằng sequence ngắn.
2. Tận dụng batch lớn hơn hoặc giảm memory.
3. Khi inference, cho phép context dài hơn mức training.

---

# 8. ALiBi không làm attention rẻ hơn

Đây là hiểu lầm khá phổ biến.

ALiBi giúp **position extrapolation**, nhưng không thay đổi bản chất dense attention:

[
O(L^2)
]

Nếu chạy từ 4K lên 32K token, attention matrix vẫn tăng rất lớn.

ALiBi không tự cung cấp:

* Sparse attention
* Sliding-window attention
* Linear attention
* KV-cache compression
* Ring attention
* FlashAttention
* Paged attention

Nó có thể kết hợp với các kỹ thuật này, nhưng bản thân ALiBi chỉ thay đổi **attention logits**.

Nói cách khác:

> ALiBi có thể làm mô hình “biết cách diễn giải vị trí dài hơn”, nhưng không khiến việc tính toán context dài trở nên miễn phí.

---

# 9. Ví dụ số cụ thể

Giả sử query ở vị trí (i=8), có thể nhìn các key từ 0 đến 8.

Với slope:

[
m=0.25
]

Bias sẽ là:

[
[-2.0,-1.75,-1.5,-1.25,-1.0,-0.75,-0.5,-0.25,0]
]

Nếu attention logits ban đầu là:

[
[1.2,0.4,0.7,1.5,0.3,1.0,0.8,0.9,0.5]
]

Sau ALiBi:

[
[-0.8,-1.35,-0.8,0.25,-0.7,0.25,0.3,0.65,0.5]
]

Key ở vị trí 0 ban đầu có score khá tốt là 1.2, nhưng do cách query 8 token nên bị trừ 2.0.

Key ở vị trí 7 ban đầu chỉ có score 0.9, nhưng vì ở rất gần nên chỉ bị trừ 0.25.

Softmax sau đó có xu hướng ưu tiên các vị trí gần hơn.

---

# 10. Biểu diễn ma trận

Với sequence dài 5, causal ALiBi bias cho một head có slope (m) có dạng:

[
B =
\begin{bmatrix}
0 & -\infty & -\infty & -\infty & -\infty\
-m & 0 & -\infty & -\infty & -\infty\
-2m & -m & 0 & -\infty & -\infty\
-3m & -2m & -m & 0 & -\infty\
-4m & -3m & -2m & -m & 0
\end{bmatrix}
]

Attention logits trở thành:

[
S =
\frac{QK^\top}{\sqrt{d_k}} + B
]

Một điểm triển khai thuận lợi là bias này:

* Không phụ thuộc dữ liệu
* Không phụ thuộc layer
* Có thể tạo sẵn
* Có thể tính trực tiếp trong attention kernel
* Không thêm tham số học được

Trong implementation chính thức, nhóm tác giả loại bỏ position embedding, tạo relative-bias matrix, rồi cộng matrix đó vào mask/attention score. ([GitHub][2])

---

# 11. Pseudocode PyTorch

```python
import torch
import torch.nn.functional as F


def alibi_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    slopes: torch.Tensor,
) -> torch.Tensor:
    """
    query, key, value: [batch, heads, seq_len, head_dim]
    slopes: [heads]
    """
    batch_size, num_heads, seq_len, head_dim = query.shape

    # Standard scaled dot-product attention logits
    logits = torch.matmul(
        query,
        key.transpose(-1, -2),
    ) / (head_dim ** 0.5)

    positions = torch.arange(seq_len, device=query.device)

    # distance[i, j] = i - j
    distance = positions[:, None] - positions[None, :]

    # Shape: [1, heads, seq_len, seq_len]
    alibi_bias = -slopes.view(1, num_heads, 1, 1) * distance.view(
        1, 1, seq_len, seq_len
    )

    # Future positions must not be visible.
    causal_mask = distance < 0
    logits = logits + alibi_bias
    logits = logits.masked_fill(
        causal_mask.view(1, 1, seq_len, seq_len),
        float("-inf"),
    )

    attention = F.softmax(logits, dim=-1)
    return torch.matmul(attention, value)
```

Trong implementation tối ưu, thường không nên materialize toàn bộ bias matrix như đoạn minh họa trên nếu context rất dài. Bias có thể được fuse vào kernel attention.

---

# 12. So sánh ALiBi với RoPE

## Cách đưa vị trí vào attention

### ALiBi

Cộng bias vào logits:

[
QK^\top \rightarrow QK^\top + B
]

### RoPE

Xoay các vector query và key theo vị trí:

[
q_i' = R_i q_i,\qquad k_j'=R_j k_j
]

Sau đó:

[
q_i'^\top k_j'
]

chứa thông tin về khoảng cách tương đối (i-j).

---

## Khác biệt trực giác

| Đặc điểm                  | ALiBi                            | RoPE                                 |
| ------------------------- | -------------------------------- | ------------------------------------ |
| Vị trí tác động vào       | Attention logits                 | Query và key                         |
| Có tham số học được       | Không                            | Không                                |
| Cơ chế                    | Phạt tuyến tính theo khoảng cách | Xoay theo tần số                     |
| Recency bias rõ ràng      | Có                               | Không trực tiếp                      |
| Extrapolation nguyên bản  | Tương đối tự nhiên               | Có thể suy giảm ngoài training range |
| Long-context extension    | Đơn giản                         | Thường dùng scaling/interpolation    |
| Khả năng biểu diễn vị trí | Khá đơn giản                     | Phong phú hơn về pha và tần số       |

ALiBi áp đặt prior khá mạnh: token xa thường ít quan trọng hơn. RoPE linh hoạt hơn vì không nhất thiết buộc attention giảm đơn điệu theo khoảng cách.

Trong thực tế, hai khái niệm thường được nhìn nhận như:

* **ALiBi:** đơn giản, ổn định, ưu tiên extrapolation
* **RoPE:** biểu diễn vị trí tinh tế hơn, nhưng mở rộng context thường cần các kỹ thuật như position interpolation hoặc frequency scaling

---

# 13. Ưu điểm

## Không có position embedding

ALiBi không cần bảng:

[
P \in \mathbb{R}^{L_{\max}\times d}
]

Do đó không bị ràng buộc cứng bởi số hàng trong bảng positional embedding.

## Không thêm tham số học được

Các slope được đặt trước, nên ALiBi gần như không làm tăng số tham số.

## Thay đổi code nhỏ

Về cơ bản chỉ cần:

1. Bỏ positional embedding.
2. Tạo slope cho mỗi head.
3. Cộng linear distance bias vào attention logits.

Repository chính thức mô tả việc triển khai theo đúng ba bước chính này. ([GitHub][2])

## Có inductive bias hợp lý cho ngôn ngữ

Trong văn bản, nhiều phụ thuộc quan trọng có tính cục bộ:

* Từ và cụm từ gần nhau
* Chủ ngữ và động từ thường không quá xa
* Câu hiện tại thường liên quan mạnh đến vài câu gần nhất

ALiBi biến quy luật đó thành prior trong attention.

## Có thể dùng bất kỳ chiều dài nào về mặt công thức

Không tồn tại giới hạn index cố định. Với context dài hơn, chỉ cần tính khoảng cách lớn hơn.

---

# 14. Hạn chế

## Recency bias có thể quá mạnh

Một số nhiệm vụ cần truy xuất chính xác thông tin rất xa:

* “Mật khẩu được nêu ở đầu tài liệu là gì?”
* Đối chiếu một định nghĩa ở trang đầu với kết luận ở cuối
* Theo dõi biến hoặc thực thể qua hàng chục nghìn token

Với khoảng cách (d), penalty là:

[
-m_hd
]

Khi (d) rất lớn, một số head có thể gần như bỏ qua token xa.

Các head có slope nhỏ giúp giảm vấn đề này, nhưng không loại bỏ hoàn toàn.

---

## Extrapolation không đồng nghĩa với chất lượng không suy giảm

Mô hình có thể chấp nhận tensor dài 32K dù chỉ train ở 2K, nhưng điều đó không bảo đảm:

* Needle-in-a-haystack tốt
* Reasoning xuyên toàn context tốt
* Perplexity không tăng
* Attention đến đầu context còn đủ mạnh
* Mô hình sử dụng hiệu quả mọi token

Cần phân biệt:

1. **Có thể chạy ở độ dài dài hơn**
2. **Loss/perplexity vẫn ổn**
3. **Truy xuất thông tin xa tốt**
4. **Reasoning dài tốt**

ALiBi chủ yếu giải quyết mạnh nhất hai tầng đầu.

---

## Không giảm quadratic complexity

Như đã nói, dense attention vẫn là (O(L^2)).

## Bias chỉ dựa trên khoảng cách

ALiBi bias không phụ thuộc:

* Nội dung token
* Cấu trúc tài liệu
* Ranh giới đoạn
* Loại quan hệ cú pháp
* Mức độ quan trọng của key

Nó giả định một dạng suy giảm đều và tuyến tính theo khoảng cách.

## Bản gốc tập trung vào decoder causal LM

Ma trận khoảng cách của causal LM chỉ xét quá khứ. Với encoder hai chiều, cần xác định bias đối xứng hoặc thiết kế biến thể phù hợp. Repository của tác giả cũng chỉ dẫn sang các phương pháp riêng cho bidirectional Transformer. ([GitHub][2])

---

# 15. Kết quả chính của bài báo

Các kết luận nổi bật được nhóm tác giả báo cáo gồm:

* ALiBi cải thiện khả năng đánh giá trên chuỗi dài hơn chuỗi training.
* Mô hình 1,3B được train với 1024 token có thể đánh giá ở 2048 token với kết quả cạnh tranh với baseline train trực tiếp ở 2048.
* Thiết lập đó nhanh hơn khoảng 11% và dùng ít memory hơn khoảng 11%.
* ALiBi cũng cải thiện kết quả trên WikiText-103 ngay cả khi không xét extrapolation, được nhóm tác giả liên hệ với inductive bias ưu tiên thông tin gần. ([arXiv][1])
* Trong quá trình phát triển, nhóm tác giả đã thử một số dạng penalty khác; theo FAQ của tác giả, dạng tuyến tính hoạt động tốt hơn dạng exponential trong các thử nghiệm của họ. ([GitHub][2])

Cần hiểu các con số này trong phạm vi kiến trúc, dữ liệu và quy mô thí nghiệm của bài báo. Chúng không tự động chuyển nguyên vẹn sang mọi LLM hoặc mọi bài toán long-context.

---

# 16. Một cách hiểu sâu hơn về ALiBi

Sau softmax, linear penalty trong logit tương ứng với một hệ số suy giảm theo hàm mũ trong trọng số chưa chuẩn hóa:

[
\exp\left(
\frac{q_i^\top k_j}{\sqrt{d_k}} - m_hd
\right)
]

có thể tách thành:

[
\exp\left(
\frac{q_i^\top k_j}{\sqrt{d_k}}
\right)
\exp(-m_hd)
]

Như vậy, dù bias tuyến tính trong logit space, nó tương đương với việc nhân mức tương thích nội dung với một **exponential decay theo khoảng cách** trước khi chuẩn hóa:

[
\text{content similarity}
\times
\text{distance decay}
]

Đây là một diễn giải rất hữu ích:

> ALiBi coi attention là sự kết hợp giữa mức độ liên quan về nội dung và prior suy giảm theo khoảng cách.

Các head với slope khác nhau tương ứng với các tốc độ memory decay khác nhau.

---

# 17. Khi nào nên dùng ALiBi?

ALiBi phù hợp khi:

* Xây decoder-only language model từ đầu
* Muốn implementation positional mechanism rất đơn giản
* Muốn inference dài hơn độ dài training mà không cần bảng embedding mới
* Muốn mô hình có prior tập trung vào ngữ cảnh gần
* Chi phí huấn luyện long sequence là một hạn chế lớn
* Không cần tương thích với checkpoint RoPE có sẵn

ALiBi ít hấp dẫn hơn khi:

* Đang tiếp tục pretrain một mô hình đã sử dụng RoPE
* Nhiệm vụ phụ thuộc đặc biệt mạnh vào các token cực xa
* Muốn positional representation giàu cấu trúc hơn
* Muốn mở rộng một hệ sinh thái kernel và checkpoint đã tối ưu quanh RoPE
* Cần thay đổi context length nhưng vẫn phải huấn luyện hoặc fine-tune để đạt chất lượng long-context cao nhất

---

# 18. Tóm tắt bản chất

ALiBi có thể được tóm lại bằng một dòng:

[
\boxed{
\text{Attention score}
======================

## \text{content score}

\text{head-specific slope}
\times
\text{distance}
}
]

Ba ý quan trọng nhất:

1. **Không thêm positional embedding vào token embedding.**
2. **Mỗi attention head nhận một linear distance penalty khác nhau.**
3. **Do quy tắc phụ thuộc khoảng cách thay vì index tuyệt đối, mô hình có khả năng extrapolate sang chuỗi dài hơn.**

ALiBi là một ý tưởng rất tối giản nhưng mạnh: thay vì dạy mô hình “vị trí số 1734 trông như thế nào”, nó dạy mô hình rằng “thông tin càng xa thường càng cần nhiều bằng chứng nội dung để được chú ý”.

[1]: https://arxiv.org/abs/2108.12409 "[2108.12409] Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation"
[2]: https://github.com/ofirpress/attention_with_linear_biases "GitHub - ofirpress/attention_with_linear_biases: Code for the ALiBi method for transformer language models (ICLR 2022) · GitHub"
