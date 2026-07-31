## 1. Bài báo nào được gọi là “Speculative Decoding”?

Thông thường, thuật ngữ này chỉ bài:

**“Fast Inference from Transformers via Speculative Decoding”**
Yaniv Leviathan, Matan Kalman và Yossi Matias. Bản đầu tiên xuất hiện trên arXiv vào tháng 11/2022, sau đó được công bố tại ICML 2023. Bài báo đề xuất tăng tốc suy luận mô hình tự hồi quy mà **không làm thay đổi phân phối đầu ra** của mô hình gốc. ([Proceedings of Machine Learning Research][1])

Cùng thời điểm, một nhóm tại DeepMind công bố kỹ thuật gần như tương đương trong:

**“Accelerating Large Language Model Decoding with Speculative Sampling”**.
Bài này báo cáo mức tăng tốc khoảng **2–2,5 lần** trên mô hình Chinchilla 70B trong hệ thống phân tán. ([arXiv][2])

Hai tên gọi **speculative decoding** và **speculative sampling** hiện thường được dùng gần như đồng nghĩa.

---

# 2. Vấn đề mà bài báo giải quyết

LLM decoder-only sinh văn bản theo kiểu autoregressive:

[
p(x_{1:T})=\prod_{t=1}^{T}p(x_t\mid x_{<t})
]

Để sinh token thứ (t), mô hình phải biết toàn bộ token trước đó. Vì thế:

1. Chạy target LLM để sinh token 1.
2. Thêm token 1 vào context.
3. Chạy lại target LLM để sinh token 2.
4. Tiếp tục như vậy.

Muốn sinh (K) token, thông thường cần khoảng (K) bước forward tuần tự. Đây là nút thắt vì GPU có khả năng tính toán song song rất lớn, nhưng decoding từng token thường không tận dụng hết khả năng đó. Bài báo mô tả vấn đề này là việc sinh (K) token đòi hỏi (K) lần chạy tuần tự của mô hình. ([Proceedings of Machine Learning Research][1])

Ý tưởng speculative decoding là:

> Dùng một mô hình nhỏ và nhanh để “đoán trước” nhiều token, sau đó dùng mô hình lớn kiểm tra toàn bộ các token đó trong một lần chạy.

---

# 3. Hai mô hình trong speculative decoding

Ta có:

* **Target model** (p): mô hình lớn mà ta thực sự muốn lấy đầu ra.
* **Draft model** (q): mô hình nhỏ hơn, nhanh hơn, dùng để đề xuất token.
* (\gamma): số token mà draft model đề xuất trong mỗi vòng.

Ví dụ:

* Target model: Llama 70B.
* Draft model: Llama 1B hoặc 7B.
* (\gamma=4).

Draft model có thể đề xuất:

```text
The capital of France is Paris
```

Giả sử phần prefix hiện tại là:

```text
The capital
```

Draft model dự đoán trước 4 token:

```text
of → France → is → Paris
```

Sau đó target model nhận cả chuỗi:

```text
The capital of France is Paris
```

và trong một forward pass tính xác suất target cho tất cả vị trí được đề xuất.

Điểm quan trọng là Transformer vẫn giữ tính nhân quả bằng causal mask, nhưng GPU có thể tính các vị trí trong block hiệu quả hơn nhiều so với bốn lần gọi tuần tự hoàn toàn riêng biệt.

---

# 4. Thuật toán cơ bản

Giả sử context hiện tại là (x_{1:t}).

## Bước 1: Draft model đề xuất token

Draft model (q) sinh tuần tự (\gamma) token:

[
\tilde{x}_1,\tilde{x}*2,\ldots,\tilde{x}*{\gamma}
]

với:

[
\tilde{x}_i\sim q_i(\cdot)
]

Trong đó:

[
q_i(\cdot)
==========

q\left(\cdot\mid
x_{1:t},\tilde{x}*1,\ldots,\tilde{x}*{i-1}
\right)
]

Mặc dù draft model vẫn sinh autoregressive, nó nhỏ hơn đáng kể nên các bước này tương đối rẻ.

## Bước 2: Target model kiểm tra song song

Target model tính:

[
p_i(\cdot)
==========

p\left(\cdot\mid
x_{1:t},\tilde{x}*1,\ldots,\tilde{x}*{i-1}
\right)
]

cho tất cả các vị trí (i=1,\ldots,\gamma) trong một lần forward.

## Bước 3: Chấp nhận hoặc từ chối từng token

Với token draft (\tilde{x}_i), xác suất chấp nhận là:

[
A_i=
\min\left(
1,
\frac{p_i(\tilde{x}_i)}
{q_i(\tilde{x}_i)}
\right)
]

Lấy:

[
r_i\sim U(0,1)
]

Chấp nhận token nếu:

[
r_i \leq A_i
]

Việc kiểm tra diễn ra từ trái sang phải.

* Nếu token thứ nhất bị từ chối, các token draft phía sau không còn hợp lệ.
* Nếu token thứ nhất được chấp nhận nhưng token thứ hai bị từ chối, chỉ giữ token thứ nhất.
* Nếu tất cả được chấp nhận, giữ cả block.

---

# 5. Vì sao xác suất chấp nhận lại là (p/q)?

Đây là biến thể của **rejection sampling**.

Xét một token (x) được draft model lấy từ (q(x)). Xác suất token đó vừa được lấy vừa được chấp nhận là:

[
q(x)
\min\left(1,\frac{p(x)}{q(x)}\right)
====================================

\min(q(x),p(x))
]

Do đó, phần xác suất chung giữa (p) và (q) được giữ lại.

Có hai trường hợp:

### Trường hợp 1: (p(x)\ge q(x))

[
\min\left(1,\frac{p(x)}{q(x)}\right)=1
]

Token luôn được chấp nhận.

### Trường hợp 2: (p(x)<q(x))

[
\min\left(1,\frac{p(x)}{q(x)}\right)
====================================

\frac{p(x)}{q(x)}
]

Draft model đang đánh giá token này cao hơn target model, nên chỉ chấp nhận với xác suất tương ứng.

---

# 6. Khi token bị từ chối thì lấy token nào?

Không thể đơn giản lấy một token mới trực tiếp từ (p), vì phần xác suất đã được dùng trong quy trình chấp nhận. Làm như vậy sẽ làm sai phân phối tổng thể.

Thay vào đó, token sửa lỗi được lấy từ phân phối dư:

[
p_{\text{residual}}(x)
======================

\operatorname{Normalize}
\left(
\max(0,p(x)-q(x))
\right)
]

Hay viết gọn:

[
p_{\text{residual}}
===================

\operatorname{Normalize}\left((p-q)_+\right)
]

Trong đó:

[
(z)_+ = \max(z,0)
]

Trực giác:

* Phần (\min(p,q)) đã được draft-and-accept xử lý.
* Phần còn thiếu để tổng phân phối trở thành (p) chính là ((p-q)_+).

Nhờ bước hiệu chỉnh này, token cuối cùng vẫn có phân phối đúng bằng target model (p).

---

# 7. Chứng minh đầu ra không thay đổi phân phối

Xét một token (x).

Xác suất (x) được trả về qua nhánh chấp nhận là:

[
P_{\text{accept}}(x)=\min(p(x),q(x))
]

Tổng xác suất xảy ra từ chối là:

[
\beta
=====

1-\sum_y\min(p(y),q(y))
]

Phân phối residual là:

[
p_{\text{residual}}(x)
======================

\frac{(p(x)-q(x))_+}{\beta}
]

Xác suất (x) xuất hiện qua nhánh residual:

[
P_{\text{reject-and-resample}}(x)
=================================

\beta
\frac{(p(x)-q(x))_+}{\beta}
===========================

(p(x)-q(x))_+
]

Vì vậy tổng xác suất trả về (x) là:

[
\min(p(x),q(x))+(p(x)-q(x))_+
]

Nếu (p(x)\le q(x)), biểu thức bằng:

[
p(x)+0=p(x)
]

Nếu (p(x)>q(x)), biểu thức bằng:

[
q(x)+p(x)-q(x)=p(x)
]

Do đó:

[
P(\text{output}=x)=p(x)
]

Đây là điểm quan trọng nhất của bài báo:

> Speculative decoding không chỉ cố tạo ra văn bản “gần giống”; về mặt lý thuyết, nó lấy mẫu chính xác từ cùng phân phối với target model.

Bài ICML nhấn mạnh rằng phương pháp có thể tăng tốc mà không thay đổi phân phối đầu ra, không cần huấn luyện lại hoặc thay đổi kiến trúc target model. ([Proceedings of Machine Learning Research][1])

---

# 8. Token thưởng — bonus token

Giả sử draft model đề xuất (\gamma) token và target model chấp nhận toàn bộ.

Target model thực tế đã tính logits không chỉ cho các token draft mà còn cho vị trí kế tiếp. Vì vậy hệ thống có thể lấy thêm một token trực tiếp từ target:

[
x_{\gamma+1}\sim p_{\gamma+1}
]

Do đó, mỗi vòng có thể sinh tối đa:

[
\gamma+1
]

token chỉ với một lần chạy target model.

Ví dụ (\gamma=4):

* Draft đề xuất 4 token.
* Target chấp nhận cả 4.
* Hệ thống lấy thêm 1 token từ target.
* Tổng cộng sinh 5 token trong một vòng target.

---

# 9. Pseudocode đơn giản

```python
def speculative_decode(prefix, target, draft, gamma):
    # 1. Draft gamma tokens
    draft_tokens = []
    q_distributions = []

    current = prefix

    for _ in range(gamma):
        q = draft.next_token_distribution(current)
        token = sample(q)

        q_distributions.append(q)
        draft_tokens.append(token)
        current = current + [token]

    # 2. Target scores all proposed positions in one pass
    p_distributions = target.score_block(
        prefix,
        draft_tokens,
    )

    accepted = []

    # 3. Verify from left to right
    for i, token in enumerate(draft_tokens):
        p_prob = p_distributions[i][token]
        q_prob = q_distributions[i][token]

        accept_prob = min(1.0, p_prob / q_prob)

        if random_uniform() <= accept_prob:
            accepted.append(token)
        else:
            residual = positive_part(
                p_distributions[i] - q_distributions[i]
            )
            residual = normalize(residual)

            correction_token = sample(residual)
            return prefix + accepted + [correction_token]

    # 4. All draft tokens accepted: draw one bonus token
    bonus_distribution = p_distributions[gamma]
    bonus_token = sample(bonus_distribution)

    return prefix + accepted + [bonus_token]
```

Trong cài đặt thực tế, cần xử lý thêm KV cache, EOS, padding, sampling temperature, top-k/top-p và sai số số học.

---

# 10. Acceptance rate

Gọi (\alpha) là xác suất trung bình một draft token được target chấp nhận.

Với một vị trí:

[
\alpha
======

\sum_x q(x)
\min\left(1,\frac{p(x)}{q(x)}\right)
]

Suy ra:

[
\alpha
======

\sum_x\min(p(x),q(x))
]

Đại lượng này liên hệ trực tiếp với total variation distance:

[
D_{\mathrm{TV}}(p,q)
====================

\frac{1}{2}\sum_x|p(x)-q(x)|
]

Ta có:

[
\alpha = 1-D_{\mathrm{TV}}(p,q)
]

Điều này cho thấy:

* (q) càng giống (p), acceptance rate càng cao.
* Draft model không nhất thiết phải chính xác tuyệt đối.
* Nó chỉ cần vừa đủ gần target và rẻ hơn nhiều.

---

# 11. Số token kỳ vọng sinh được mỗi vòng

Nếu tạm giả sử acceptance rate tại mỗi vị trí đều là (\alpha), xác suất ít nhất (k) draft token đầu tiên được chấp nhận là:

[
\alpha^k
]

Số token đầu ra kỳ vọng mỗi vòng là:

[
E[N]
====

1+\alpha+\alpha^2+\cdots+\alpha^\gamma
]

Do đó:

[
E[N]
====

\frac{1-\alpha^{\gamma+1}}{1-\alpha}
]

với (\alpha\ne1).

Nếu (\alpha=1):

[
E[N]=\gamma+1
]

Ví dụ (\gamma=4):

| Acceptance rate (\alpha) | Token kỳ vọng/vòng |
| -----------------------: | -----------------: |
|                      0,5 |               1,94 |
|                      0,7 |               2,77 |
|                      0,8 |               3,36 |
|                      0,9 |               4,10 |
|                      1,0 |               5,00 |

Đây là lý do acceptance rate có ảnh hưởng rất lớn đến hiệu năng.

---

# 12. Mô hình tốc độ lý thuyết

Gọi:

* (T_p): thời gian một lần chạy target.
* (T_q): thời gian một bước draft.
* (c=T_q/T_p).
* (\gamma): số draft token.

Chi phí gần đúng cho một vòng:

[
T_{\text{round}}
\approx
T_p+\gamma T_q
==============

T_p(1+\gamma c)
]

Trong khi số token kỳ vọng sinh được là:

[
E[N]
====

\frac{1-\alpha^{\gamma+1}}{1-\alpha}
]

Vì standard decoding tốn khoảng (T_p) cho mỗi token, speedup lý thuyết gần đúng là:

[
S
\approx
\frac{1-\alpha^{\gamma+1}}
{(1-\alpha)(1+\gamma c)}
]

Ví dụ:

* (\alpha=0,8)
* (\gamma=4)
* Draft model tốn (c=0,05) lần target model

Ta có:

[
E[N]\approx3,36
]

và:

[
S\approx\frac{3,36}{1+4(0,05)}
=\frac{3,36}{1,2}
\approx2,8
]

Đây chỉ là mô hình lý tưởng. Hiệu năng thực còn phụ thuộc memory bandwidth, batch size, kernel launch, KV cache, communication giữa GPU và cách triển khai server.

---

# 13. Tại sao target kiểm tra nhiều token không đắt gấp nhiều lần?

Trong decoding thông thường, target xử lý từng token một. Với batch nhỏ, tác vụ thường bị giới hạn bởi:

* Đọc trọng số từ HBM.
* Memory bandwidth.
* Kernel-launch overhead.
* Mức sử dụng GPU thấp.

Khi kiểm tra một block ngắn gồm nhiều token, trọng số target có thể được sử dụng để tính nhiều vị trí trong cùng forward pass. Lượng FLOP tăng, nhưng latency không nhất thiết tăng tuyến tính theo số token.

Đây là giả định hệ thống quan trọng của speculative decoding:

[
\text{Cost verify }\gamma\text{ token}
\ll
\gamma \times \text{cost decode một token}
]

Nhóm DeepMind mô tả quan sát rằng latency để chấm điểm song song một continuation ngắn có thể gần với latency lấy mẫu một token từ mô hình lớn. ([arXiv][2])

---

# 14. Ví dụ số cụ thể

Giả sử draft model đề xuất token (a).

Target và draft cho xác suất:

[
q(a)=0,6,\qquad p(a)=0,3
]

Xác suất chấp nhận:

[
A(a)=\min\left(1,\frac{0,3}{0,6}\right)=0,5
]

Vì token (a) được draft lấy với xác suất (0,6), xác suất nó đi qua nhánh chấp nhận là:

[
0,6\times0,5=0,3
]

Đúng bằng xác suất target muốn dành cho (a).

Với token (b):

[
q(b)=0,1,\qquad p(b)=0,25
]

Ta có:

[
A(b)=1
]

Draft model chỉ đề xuất (b) với xác suất (0,1), nên nhánh chấp nhận cung cấp (0,1). Phần còn thiếu:

[
0,25-0,1=0,15
]

được bổ sung qua residual distribution.

Kết quả cuối cùng:

[
P(b)=0,1+0,15=0,25
]

chính xác bằng target.

---

# 15. Greedy decoding có đơn giản hơn không?

Có.

Nếu dùng greedy decoding, draft model đề xuất một chuỗi token. Target model tính argmax ở từng vị trí.

Ta chấp nhận liên tiếp các draft token miễn là:

[
\tilde{x}_i
===========

\arg\max_x p_i(x)
]

Ngay khi token draft khác token target, ta:

1. Dừng chấp nhận.
2. Lấy token argmax của target ở vị trí đó.
3. Bỏ toàn bộ draft token phía sau.

Không cần rejection sampling phức tạp vì greedy decoding là xác định, không phải lấy mẫu ngẫu nhiên.

---

# 16. Kết quả thực nghiệm của bài báo

Bài Leviathan và cộng sự thử nghiệm trên T5-XXL và báo cáo mức tăng tốc khoảng **2–3 lần** so với triển khai T5X chuẩn, trong khi giữ đầu ra giống hệt về mặt phân phối. ([Proceedings of Machine Learning Research][1])

Bài độc lập của Chen và cộng sự thử trên Chinchilla 70B, báo cáo mức tăng tốc khoảng **2–2,5 lần** trong môi trường phân tán mà không cần sửa kiến trúc mô hình hoặc đánh đổi chất lượng lấy mẫu. ([arXiv][2])

Các con số này không có nghĩa mọi hệ thống đều đạt 2–3 lần. Kết quả phụ thuộc mạnh vào:

* Tỷ lệ kích thước draft/target.
* Acceptance rate.
* Số token draft (\gamma).
* Batch size.
* Độ dài context.
* GPU và memory bandwidth.
* Chi phí giao tiếp giữa thiết bị.
* Chất lượng implementation và KV-cache management.

---

# 17. Khi nào speculative decoding hiệu quả?

Phương pháp hoạt động tốt nhất khi đồng thời thỏa mãn:

## Draft model đủ nhanh

Nếu draft model chỉ nhỏ hơn target một chút, chi phí tạo draft có thể xóa sạch lợi ích.

## Draft model đủ giống target

Nếu (q) khác (p) nhiều, token thường bị từ chối sớm. Target model vẫn phải chạy nhưng chỉ thu được một hoặc hai token.

## Batch size tương đối nhỏ

Speculative decoding thường đặc biệt hấp dẫn cho:

* Interactive chat.
* Single-user latency.
* Batch nhỏ.
* On-device inference.

Khi batch đã rất lớn và GPU được khai thác gần tối đa, việc thêm nhiều token verification có thể làm tăng compute đáng kể và lợi ích throughput có thể nhỏ hơn.

## Output có tính dễ đoán

Các đoạn như:

* Boilerplate.
* Cú pháp lập trình quen thuộc.
* Cụm từ phổ biến.
* Câu có cấu trúc rõ ràng.

thường có acceptance rate cao hơn.

Các tác vụ có phân phối token khó đoán hoặc temperature cao thường có acceptance rate thấp hơn.

---

# 18. Những hạn chế quan trọng

### 1. Cần thêm draft model

Việc giữ target và draft trên GPU làm tăng memory footprint. Nếu draft model đặt trên GPU khác, communication overhead có thể trở thành vấn đề.

### 2. Tokenizer phải tương thích

Cài đặt đơn giản nhất yêu cầu hai model dùng cùng vocabulary và tokenizer. Nếu tokenizer khác nhau, việc ánh xạ draft token sang target token phức tạp hơn nhiều.

### 3. Draft model tốt chưa chắc nhanh

Một draft model lớn có thể tăng acceptance rate nhưng cũng tăng chi phí draft. Có một trade-off:

[
\text{Draft chính xác hơn}
\quad\leftrightarrow\quad
\text{Draft đắt hơn}
]

Mục tiêu không phải tối đa hóa acceptance rate riêng lẻ mà là tối đa hóa:

[
\frac{\text{token được xác nhận}}
{\text{tổng latency}}
]

### 4. (\gamma) quá lớn có thể phản tác dụng

Draft nhiều token hơn cho phép target xác nhận block dài hơn. Tuy nhiên:

* Draft cost tăng.
* Xác suất toàn bộ prefix dài được chấp nhận giảm.
* Verification tensor lớn hơn.
* Nhiều phần draft sau token bị từ chối bị lãng phí.

Do đó (\gamma) thường cần được điều chỉnh theo model và workload.

### 5. Không giảm chi phí prefill

Speculative decoding chủ yếu tăng tốc **decode phase**. Nó không trực tiếp giải quyết chi phí xử lý prompt dài trong prefill.

### 6. “Lossless” không phải lúc nào cũng là bitwise identical

Về lý thuyết, phân phối đầu ra giống target. Trong hệ thống thực, sai khác nhỏ vẫn có thể xuất hiện do:

* Floating-point precision.
* Thứ tự phép toán.
* Kernel khác nhau.
* Random-number generator.
* Top-k/top-p implementation.

Bài speculative sampling mô tả việc bảo toàn phân phối trong phạm vi số học phần cứng. ([arXiv][2])

---

# 19. Các hướng phát triển sau bài gốc

## Self-speculative decoding

Không dùng mô hình phụ. Chính target model tạo draft bằng cách:

* Bỏ qua một số layer.
* Early exit.
* Dùng một head dự đoán nhỏ.
* Dùng hidden states trung gian.

Ưu điểm là giảm memory cho draft model và tránh phải duy trì hai model riêng.

## Multi-token prediction heads

Thêm các head dự đoán nhiều token tương lai vào model. Một forward pass tạo ra nhiều candidate token, sau đó target backbone xác minh.

## Tree-based speculation

Thay vì draft một chuỗi duy nhất:

```text
A → B → C → D
```

hệ thống tạo một cây candidate:

```text
       A
     /   \
    B     X
   / \     \
  C   Y     Z
```

Target dùng tree attention để kiểm tra nhiều nhánh. Cách này tăng khả năng một nhánh phù hợp với target nhưng làm verification và KV-cache phức tạp hơn.

## Retrieval-based speculation

Dùng chuỗi token đã xuất hiện trong prompt, cache hoặc corpus làm draft. Cách này đặc biệt hữu ích cho:

* Code completion.
* Văn bản lặp.
* Structured generation.

## Dynamic speculation length

Không cố định (\gamma). Hệ thống lựa chọn số token draft dựa trên:

* Độ tự tin của draft model.
* Acceptance history.
* Entropy.
* Loại request.
* Độ dài context.
* Tình trạng tải hệ thống.

---

# 20. Ý nghĩa lớn nhất của bài báo

Đóng góp quan trọng không đơn thuần là “dùng model nhỏ đoán token”.

Điểm đột phá là kết hợp ba yếu tố:

1. **Draft nhanh:** dùng mô hình xấp xỉ để đề xuất nhiều token.
2. **Parallel verification:** dùng target model chấm điểm cả block.
3. **Modified rejection sampling:** sửa phân phối để đầu ra vẫn chính xác theo target.

Nếu chỉ làm hai bước đầu và giữ token khi draft trùng với target, hệ thống có thể tăng tốc greedy decoding nhưng khó bảo đảm sampling chính xác.

Modified rejection sampling biến speculative decoding thành một tối ưu hóa suy luận **lossless về mặt phân phối**, thay vì một phương pháp xấp xỉ làm giảm chất lượng.

---

## Tóm tắt bằng một câu

Speculative decoding chuyển công việc từ:

[
\text{nhiều lần gọi target tuần tự}
]

sang:

[
\text{nhiều lần gọi draft rẻ}
+
\text{một lần target xác minh song song}
]

và dùng rejection sampling hiệu chỉnh để bảo đảm đầu ra vẫn được lấy từ đúng phân phối của target LLM.

[1]: https://proceedings.mlr.press/v202/leviathan23a.html "Fast Inference from Transformers via Speculative Decoding"
[2]: https://arxiv.org/abs/2302.01318 "[2302.01318] Accelerating Large Language Model Decoding with Speculative Sampling"
