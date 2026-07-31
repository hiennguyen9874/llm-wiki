## 1. DPO là gì?

**Direct Preference Optimization — DPO** là phương pháp hậu huấn luyện LLM bằng dữ liệu sở thích, được giới thiệu trong bài:

> **Direct Preference Optimization: Your Language Model is Secretly a Reward Model**
> Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon, Christopher D. Manning và Chelsea Finn; công bố tại NeurIPS 2023. ([arXiv][1])

Ý tưởng trung tâm:

> Thay vì huấn luyện một **reward model** riêng rồi dùng reinforcement learning như PPO để tối ưu LLM, DPO tối ưu trực tiếp xác suất của câu trả lời được ưa thích bằng một loss phân loại đơn giản.

DPO vì vậy thường được mô tả là **“RLHF không cần RL”**. Tuy nhiên, nói chính xác hơn, DPO vẫn xuất phát từ cùng bài toán tối ưu có ràng buộc KL của RLHF; nó chỉ biến đổi bài toán để không cần chạy vòng lặp reinforcement learning. ([arXiv][2])

---

## 2. Vấn đề mà bài báo muốn giải quyết

Pipeline RLHF truyền thống thường gồm ba bước:

1. **Supervised Fine-Tuning — SFT**
   Huấn luyện mô hình trên các câu trả lời chất lượng cao.

2. **Reward modeling**
   Với mỗi prompt (x), thu thập hai câu trả lời:
   [
   y_w \succ y_l
   ]
   trong đó (y_w) là câu được chọn, (y_l) là câu bị loại.

   Một reward model (r_\phi(x,y)) được huấn luyện để cho:
   [
   r_\phi(x,y_w)>r_\phi(x,y_l)
   ]

3. **RL optimization**
   Dùng PPO hoặc một thuật toán RL để tối ưu LLM theo reward model, đồng thời không cho mô hình đi quá xa mô hình SFT ban đầu.

Mục tiêu RLHF chuẩn có dạng:

[
\max_\pi
\mathbb{E}_{x,y\sim\pi}
[r(x,y)]
--------

\beta
D_{\mathrm{KL}}
\left(
\pi(y|x),|,\pi_{\mathrm{ref}}(y|x)
\right)
]

Trong đó:

* (\pi): mô hình đang được tối ưu;
* (\pi_{\mathrm{ref}}): mô hình tham chiếu, thường là mô hình SFT;
* (r(x,y)): điểm reward;
* (\beta): mức phạt khi mô hình mới lệch khỏi mô hình tham chiếu.

Ràng buộc KL giúp hạn chế mode collapse, giữ độ đa dạng và ngăn mô hình khai thác các lỗi của reward model. ([arXiv][2])

Khó khăn là pipeline này phải duy trì nhiều thành phần:

* policy model;
* reference model;
* reward model;
* đôi khi thêm value model;
* sinh mẫu trong lúc huấn luyện;
* PPO với clipping, advantage estimation và nhiều siêu tham số nhạy cảm.

DPO đặt câu hỏi: **Có thể đi trực tiếp từ dữ liệu so sánh sang policy tối ưu hay không?**

---

## 3. Dữ liệu đầu vào của DPO

Mỗi mẫu huấn luyện thường là một bộ ba:

[
(x,y_w,y_l)
]

Ví dụ:

```text
Prompt:
Giải thích vì sao bầu trời có màu xanh.

Chosen:
Ánh sáng xanh bị tán xạ mạnh hơn bởi các phân tử trong khí quyển...

Rejected:
Bầu trời xanh vì phản chiếu màu của đại dương.
```

DPO không nhất thiết cần điểm reward tuyệt đối. Nó chỉ cần thông tin:

[
y_w \succ y_l
]

Nguồn nhãn có thể là:

* đánh giá của con người;
* AI feedback;
* rule-based verifier;
* reward model có sẵn;
* kết quả đúng/sai trong toán hoặc lập trình.

Điểm quan trọng là chất lượng DPO bị giới hạn rất mạnh bởi **chất lượng và độ phủ của các cặp preference**.

---

## 4. Bradley–Terry preference model

Bài báo giả định xác suất con người thích (y_1) hơn (y_2) tuân theo mô hình Bradley–Terry:

[
p(y_1\succ y_2|x)
=================

\frac{\exp(r(x,y_1))}
{\exp(r(x,y_1))+\exp(r(x,y_2))}
]

Tương đương:

[
p(y_1\succ y_2|x)
=================

\sigma\left(
r(x,y_1)-r(x,y_2)
\right)
]

với:

[
\sigma(z)=\frac{1}{1+e^{-z}}
]

Reward model trong RLHF được huấn luyện bằng binary cross-entropy:

[
\mathcal L_R
============

-\mathbb E
\left[
\log\sigma
\left(
r_\phi(x,y_w)-r_\phi(x,y_l)
\right)
\right]
]

Nghĩa là reward model phải xếp câu được chọn cao hơn câu bị loại. ([arXiv][2])

---

## 5. Phép suy ra cốt lõi của DPO

### Bước 1: Nghiệm tối ưu của RLHF có dạng đóng

Đối với mục tiêu reward trừ KL ở trên, policy tối ưu có dạng:

[
\pi_r(y|x)
==========

\frac{1}{Z(x)}
\pi_{\mathrm{ref}}(y|x)
\exp\left(\frac{r(x,y)}{\beta}\right)
]

Trong đó:

[
Z(x)
====

\sum_y
\pi_{\mathrm{ref}}(y|x)
\exp\left(\frac{r(x,y)}{\beta}\right)
]

là partition function. ([arXiv][2])

### Bước 2: Viết reward theo policy

Biến đổi biểu thức trên:

[
r(x,y)
======

\beta
\log
\frac{\pi_r(y|x)}
{\pi_{\mathrm{ref}}(y|x)}
+
\beta\log Z(x)
]

Đây là nguồn gốc của tiêu đề:

> **“Your language model is secretly a reward model.”**

Tỷ số giữa policy mới và reference policy có thể được diễn giải như một reward ngầm:

[
\hat r_\theta(x,y)
==================

\beta
\log
\frac{\pi_\theta(y|x)}
{\pi_{\mathrm{ref}}(y|x)}
]

### Bước 3: Partition function bị triệt tiêu

Bradley–Terry chỉ quan tâm đến **hiệu reward**:

[
r(x,y_w)-r(x,y_l)
]

Vì (y_w) và (y_l) có cùng prompt (x), thành phần:

[
\beta\log Z(x)
]

xuất hiện ở cả hai phía và bị triệt tiêu.

Do đó:

[
r(x,y_w)-r(x,y_l)
=================

\beta
\left[
\log\frac{\pi_\theta(y_w|x)}
{\pi_{\mathrm{ref}}(y_w|x)}
---------------------------

\log\frac{\pi_\theta(y_l|x)}
{\pi_{\mathrm{ref}}(y_l|x)}
\right]
]

Nhờ vậy, ta có thể huấn luyện policy trực tiếp mà không cần biết (Z(x)), không cần reward model riêng và không cần PPO. ([arXiv][2])

---

## 6. Hàm loss DPO

Loss cuối cùng là:

[
\boxed{
\mathcal L_{\mathrm{DPO}}
=========================

-\mathbb E_{(x,y_w,y_l)}
\left[
\log\sigma
\left(
\beta
\log\frac{\pi_\theta(y_w|x)}
{\pi_{\mathrm{ref}}(y_w|x)}
---------------------------

\beta
\log\frac{\pi_\theta(y_l|x)}
{\pi_{\mathrm{ref}}(y_l|x)}
\right)
\right]
}
]

Có thể viết gọn bằng log-ratio:

[
A_w=
\log\pi_\theta(y_w|x)
---------------------

\log\pi_{\mathrm{ref}}(y_w|x)
]

[
A_l=
\log\pi_\theta(y_l|x)
---------------------

\log\pi_{\mathrm{ref}}(y_l|x)
]

Khi đó:

[
\mathcal L_{\mathrm{DPO}}
=========================

-\log\sigma\bigl(\beta(A_w-A_l)\bigr)
]

DPO muốn:

[
A_w>A_l
]

Nói bằng lời:

> So với reference model, policy mới phải tăng xác suất tương đối của câu được chọn nhiều hơn câu bị loại.

Đây không đơn thuần là:

[
\log\pi_\theta(y_w|x)>
\log\pi_\theta(y_l|x)
]

Mà là so sánh **mức thay đổi so với reference model**. Reference model đóng vai trò neo giữ policy, tương tự KL regularization trong RLHF.

---

## 7. Trực giác về gradient

Reward ngầm của policy là:

[
\hat r_\theta(x,y)
==================

\beta
\log
\frac{\pi_\theta(y|x)}
{\pi_{\mathrm{ref}}(y|x)}
]

Gradient DPO có dạng khái quát:

[
\nabla_\theta\mathcal L_{\mathrm{DPO}}
\propto
-------

\sigma
\left(
\hat r_\theta(x,y_l)
--------------------

\hat r_\theta(x,y_w)
\right)
\left[
\nabla\log\pi_\theta(y_w|x)
---------------------------

\nabla\log\pi_\theta(y_l|x)
\right]
]

Nó thực hiện hai việc:

* tăng log-probability của (y_w);
* giảm log-probability của (y_l).

Nhưng mức cập nhật không cố định. Nếu mô hình đang xếp sai, tức:

[
\hat r(y_l)>\hat r(y_w)
]

thì trọng số gradient lớn hơn. Nếu mô hình đã phân biệt đúng với margin lớn, cập nhật nhỏ dần.

Đây là khác biệt quan trọng so với một loss “chosen lên, rejected xuống” quá đơn giản. Bài báo cho thấy bỏ trọng số động này có thể khiến mô hình suy biến. ([arXiv][2])

---

## 8. Vai trò của (\beta)

(\beta) là tham số quan trọng nhất trong DPO.

Trong cách suy ra lý thuyết, (\beta) là hệ số của KL constraint:

[
\text{reward}
-------------

\beta D_{\mathrm{KL}}(\pi|\pi_{\mathrm{ref}})
]

Diễn giải:

* **(\beta) lớn:** phạt lệch khỏi reference mạnh hơn; policy bảo thủ hơn.
* **(\beta) nhỏ:** cho phép policy thay đổi mạnh hơn để khớp preference.

Trong loss, (\beta) cũng điều chỉnh độ dốc của sigmoid. Vì vậy ảnh hưởng thực tế còn phụ thuộc:

* độ nhiễu của dữ liệu;
* learning rate;
* độ dài sequence;
* cách chuẩn hóa loss;
* độ gần nhau giữa policy và reference;
* chất lượng của rejected response.

Không nên hiểu đơn giản rằng “(\beta) càng nhỏ càng tốt”. Quá nhỏ có thể khiến mô hình overfit preference, thay đổi phân phối quá mạnh hoặc khai thác bias của dữ liệu.

---

## 9. Cách tính log-probability cho LLM

Với một response gồm các token:

[
y=(y_1,\dots,y_T)
]

log-probability của response là:

[
\log\pi_\theta(y|x)
===================

\sum_{t=1}^{T}
\log\pi_\theta
(y_t|x,y_{<t})
]

Chỉ các token thuộc response thường được đưa vào loss; token của prompt được mask.

Cho mỗi batch, cần bốn giá trị:

[
\log\pi_\theta(y_w|x),
\quad
\log\pi_\theta(y_l|x),
]

[
\log\pi_{\mathrm{ref}}(y_w|x),
\quad
\log\pi_{\mathrm{ref}}(y_l|x)
]

Sau đó:

```python
chosen_log_ratio = policy_chosen_logp - ref_chosen_logp
rejected_log_ratio = policy_rejected_logp - ref_rejected_logp

logits = beta * (chosen_log_ratio - rejected_log_ratio)
loss = -logsigmoid(logits).mean()
```

Reference model không nhận gradient.

Trong thực tế, reference log-probabilities có thể được tính trước và lưu vào dataset để tiết kiệm bộ nhớ/tính toán, miễn là reference model và tokenization không thay đổi.

---

## 10. DPO khác SFT như thế nào?

SFT trên chosen response tối ưu:

[
\mathcal L_{\mathrm{SFT}}
=========================

-\log\pi_\theta(y_w|x)
]

Nó không sử dụng (y_l). Do đó mô hình chỉ biết:

> “Hãy bắt chước câu này.”

DPO sử dụng cả hai:

> “Trong hai câu trả lời này, hãy ưu tiên câu A hơn B, nhưng vẫn giữ quan hệ với reference model.”

Ví dụ, cả chosen và rejected có thể đều khá tốt, chỉ khác nhau ở một chi tiết. DPO học được đường biên preference tinh hơn SFT.

Tuy nhiên, DPO không hoàn toàn thay thế SFT. Pipeline phổ biến vẫn là:

[
\text{Pretrained model}
\rightarrow
\text{SFT}
\rightarrow
\text{DPO}
]

SFT tạo ra policy/reference ban đầu có khả năng tuân thủ instruction; DPO tinh chỉnh hành vi theo preference.

---

## 11. DPO khác PPO-based RLHF

| Thành phần                         |                  PPO-RLHF |                     DPO |
| ---------------------------------- | ------------------------: | ----------------------: |
| Mô hình SFT                        |                        Có |               Thường có |
| Preference pairs                   |                        Có |                      Có |
| Reward model riêng                 |                        Có |                   Không |
| Value model                        |                 Thường có |                   Không |
| Sinh response trong vòng lặp train |                        Có |                   Không |
| Reinforcement learning             |                        Có |                   Không |
| Reference model                    |                        Có |                      Có |
| Loss chính                         |       Policy-gradient/PPO | Logistic classification |
| Dữ liệu                            | Có thể cập nhật on-policy |         Chủ yếu offline |
| Độ phức tạp triển khai             |                       Cao |                Thấp hơn |

Ưu điểm lớn của PPO là có thể:

* lấy mẫu từ policy hiện tại;
* thu thập feedback mới;
* tối ưu reward trên các response chưa có trong dataset;
* vận hành theo pipeline online hoặc iterative.

DPO chủ yếu là **offline preference optimization**. Nó rất hiệu quả khi đã có một dataset preference tốt, nhưng không tự khám phá response mới trong quá trình training.

---

## 12. Quy trình huấn luyện DPO thực tế

Một pipeline điển hình:

### Bước 1: Chuẩn bị model SFT

[
\pi_{\mathrm{SFT}}
]

Model phải biết trả lời instruction ở mức cơ bản.

### Bước 2: Tạo preference data

Với mỗi prompt:

1. sinh nhiều response;
2. con người hoặc AI chọn response tốt hơn;
3. tạo cặp:
   [
   (x,y_w,y_l)
   ]

### Bước 3: Tạo hai model giống nhau

* trainable policy:
  [
  \pi_\theta
  ]
* frozen reference:
  [
  \pi_{\mathrm{ref}}
  ]

Cả hai thường khởi tạo từ cùng checkpoint SFT.

### Bước 4: Forward chosen và rejected

Tính sequence log-probabilities dưới cả policy và reference.

### Bước 5: Tính DPO loss

[
-\log\sigma\left[
\beta
\left(
\Delta_w-\Delta_l
\right)
\right]
]

### Bước 6: Chỉ cập nhật policy

Reference model được đóng băng trong toàn bộ quá trình.

---

## 13. Kết quả thực nghiệm trong bài báo

Bài báo thử nghiệm trên ba nhóm tác vụ:

1. **Điều khiển sentiment** với IMDb và GPT-2-large.
2. **Tóm tắt Reddit TL;DR** với dữ liệu preference của con người.
3. **Đối thoại một lượt** với Anthropic Helpful–Harmless, khoảng 170.000 dialogue. ([arXiv][2])

Kết quả chính:

* Ở sentiment control, DPO tạo ra đường biên reward–KL tốt hơn các baseline PPO trong thiết lập của bài báo.
* Ở TL;DR summarization, DPO đạt khoảng **61% win rate**, trong khi PPO tốt nhất khoảng **57%**, theo GPT-4 evaluator của thí nghiệm.
* Trong đánh giá trực tiếp bằng con người, mẫu DPO được ưu tiên hơn PPO khoảng **58%** số lần.
* DPO ổn định hơn PPO khi thay đổi sampling temperature.
* Với Anthropic-HH single-turn dialogue, DPO là phương pháp hiệu quả tính toán duy nhất trong so sánh của bài báo có thể vượt preferred completion của test set. ([arXiv][2])

Các con số này nên được đọc trong đúng bối cảnh thí nghiệm năm 2023. Chúng không chứng minh DPO luôn vượt PPO trên mọi model, dataset hoặc loại reward.

---

## 14. Vì sao DPO đơn giản và ổn định hơn?

### Không phải học reward model độc lập

Reward model có thể bị:

* overfit;
* calibration kém;
* khai thác bởi policy;
* sai mạnh ngoài phân phối dữ liệu.

DPO không tạo một mạng reward riêng để policy tối ưu chống lại.

### Không có high-variance policy gradient

PPO phải ước lượng reward/advantage từ sample. DPO dùng teacher-forced likelihood và backpropagation thông thường.

### Không có on-policy generation trong mỗi vòng train

DPO dùng dataset cố định, tương tự supervised fine-tuning. Điều này giảm chi phí sinh mẫu đáng kể.

### Ít thành phần hơn

Không cần đồng thời tối ưu actor, critic và reward model. Bài báo lập luận rằng việc tránh ước lượng baseline/soft value cũng giúp giảm một nguồn bất ổn của actor–critic. ([arXiv][2])

---

## 15. Hạn chế quan trọng

### 15.1 Phụ thuộc mạnh vào dữ liệu preference

Nếu annotator thích câu trả lời:

* dài nhưng lan man;
* tự tin nhưng sai;
* tâng bốc người dùng;
* theo một phong cách cố định;
* có cấu trúc đẹp nhưng thiếu nội dung,

DPO sẽ học các bias đó.

DPO tối ưu **preference được quan sát**, không trực tiếp tối ưu chân lý, an toàn hay hữu ích theo nghĩa tuyệt đối.

### 15.2 Offline và thiếu exploration

DPO chỉ thấy các response trong dataset. Nó không trực tiếp thử các output mới rồi nhận reward như online RL.

Khi policy đi xa khỏi phân phối tạo dữ liệu, các cặp preference cũ có thể không còn cung cấp tín hiệu tốt.

### 15.3 Reference model rất quan trọng

Reward ngầm được định nghĩa tương đối:

[
\hat r_\theta
=============

\beta\log\frac{\pi_\theta}{\pi_{\mathrm{ref}}}
]

Do đó một reference model yếu hoặc không khớp với policy tạo dữ liệu có thể gây distribution shift. Bài báo đề xuất, khi không có SFT model gốc, huấn luyện reference trên các chosen completion để giảm chênh lệch phân phối. ([arXiv][2])

### 15.4 Giả định preference model

Suy ra chuẩn dựa vào Bradley–Terry hoặc các mô hình ranking tương tự. Preference thật của con người có thể:

* không bắc cầu;
* phụ thuộc ngữ cảnh;
* có nhiều tiêu chí xung đột;
* thay đổi giữa annotator;
* có tie hoặc mức độ chắc chắn khác nhau.

Một nhãn nhị phân chosen/rejected làm mất nhiều thông tin.

### 15.5 Có thể over-optimize

DPO vẫn có thể khai thác các pattern trong preference data. Việc không có reward model riêng không đồng nghĩa với không có reward hacking; reward chỉ được biểu diễn ngầm qua log-ratio.

Bản thân bài báo đặt vấn đề về reward over-optimization, khả năng tổng quát hóa ngoài phân phối và việc mở rộng từ model tối đa 6B trong thí nghiệm ban đầu. ([arXiv][2])

### 15.6 Length bias

Vì log-probability sequence là tổng theo token, độ dài response ảnh hưởng đến giá trị loss. Các implementation có thể dùng:

* tổng log-probability;
* trung bình theo token;
* length normalization;
* các biến thể loss.

Những lựa chọn này thay đổi hành vi và không phải lúc nào cũng còn đúng hoàn toàn với phép suy ra nguyên bản.

---

## 16. Một hiểu nhầm thường gặp

### “DPO chỉ tăng chosen và giảm rejected”

Chưa đầy đủ. DPO tối ưu **log-ratio so với reference**, không chỉ xác suất tuyệt đối.

### “DPO không có reward model”

DPO không có **reward network riêng**, nhưng policy biểu diễn một reward ngầm:

[
\hat r_\theta(x,y)
==================

\beta\log
\frac{\pi_\theta(y|x)}
{\pi_{\mathrm{ref}}(y|x)}
]

### “DPO luôn tốt hơn PPO”

Không. Bài báo cho thấy DPO tốt hơn trong các thiết lập cụ thể. PPO hoặc các phương pháp RL vẫn có lợi thế khi cần online exploration, verifier reward, môi trường nhiều bước hoặc cập nhật dữ liệu liên tục.

### “DPO có thể chạy trực tiếp từ pretrained model”

Về kỹ thuật có thể, nhưng thường không lý tưởng. Reference/policy nên có năng lực instruction-following và phân phối gần với dữ liệu preference. Vì vậy SFT trước DPO thường rất quan trọng.

---

## 17. Tóm tắt bằng một câu

DPO biến bài toán:

[
\text{học reward model}
\rightarrow
\text{dùng RL tối ưu policy}
]

thành:

[
\text{học trực tiếp policy từ chosen/rejected}
]

bằng cách nhận ra rằng reward tối ưu có thể được biểu diễn thông qua tỷ số:

[
\frac{\pi_\theta(y|x)}
{\pi_{\mathrm{ref}}(y|x)}
]

Nhờ đó, toàn bộ preference optimization trở thành một bài toán binary classification có regularization ngầm bởi reference model.

[1]: https://arxiv.org/abs/2305.18290?utm_source=chatgpt.com "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
[2]: https://arxiv.org/html/2305.18290v3 "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
