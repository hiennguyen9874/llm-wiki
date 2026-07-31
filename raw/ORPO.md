## ORPO là gì?

**ORPO — Odds Ratio Preference Optimization** là phương pháp hậu huấn luyện LLM do Jiwoo Hong, Noah Lee và James Thorne đề xuất. Bài báo chính thức được công bố tại **EMNLP 2024** với tiêu đề *“ORPO: Monolithic Preference Optimization without Reference Model”*. ([ACL Anthology][1])

Ý tưởng trung tâm của ORPO là:

> Gộp **Supervised Fine-Tuning** và **preference alignment** vào cùng một quá trình huấn luyện, không cần reward model và cũng không cần reference model.

Một mẫu dữ liệu ORPO có dạng:

[
(x,; y_w,; y_l)
]

Trong đó:

* (x): prompt;
* (y_w): câu trả lời được ưu tiên, thường gọi là `chosen` hoặc winner;
* (y_l): câu trả lời bị từ chối, thường gọi là `rejected` hoặc loser.

---

## 1. Vấn đề mà ORPO muốn giải quyết

### Pipeline RLHF truyền thống

RLHF thường có các bước:

[
\text{Pretrained model}
\rightarrow \text{SFT}
\rightarrow \text{Reward Model}
\rightarrow \text{PPO}
]

Pipeline này khá phức tạp:

* cần huấn luyện reward model;
* PPO có thể không ổn định;
* cần giữ nhiều mô hình trong GPU;
* việc chọn learning rate, KL coefficient và reward scaling tương đối khó.

### Pipeline DPO

DPO đơn giản hóa RLHF:

[
\text{Pretrained model}
\rightarrow \text{SFT}
\rightarrow \text{DPO}
]

DPO không cần reward model và PPO, nhưng vẫn thường cần:

* một mô hình đã SFT;
* một policy model đang được cập nhật;
* một bản sao đóng băng làm reference model.

### Pipeline ORPO

ORPO rút gọn thành:

[
\text{Pretrained model}
\rightarrow \text{ORPO}
]

Trong một objective duy nhất, mô hình vừa:

1. học bắt chước câu trả lời tốt;
2. học phân biệt câu trả lời tốt với câu trả lời xấu.

Theo tác giả, ORPO vì vậy không cần SFT warm-up riêng và không cần reference model. ([arXiv][2])

---

## 2. Quan sát nền tảng của bài báo

Tác giả thực hiện một thí nghiệm với SFT thông thường: chỉ huấn luyện mô hình trên các câu trả lời `chosen`.

Ta có thể kỳ vọng:

* xác suất của `chosen` tăng;
* xác suất của `rejected` giảm.

Nhưng kết quả thực tế cho thấy xác suất của **cả chosen lẫn rejected đều có thể cùng tăng**.

Lý do là SFT chỉ nói với mô hình:

> “Hãy làm câu trả lời này có xác suất cao hơn.”

Nó không trực tiếp nói:

> “Đừng sinh câu trả lời kia.”

Ví dụ, trong miền hội thoại hỗ trợ khách hàng:

```text
Prompt: Tôi không đăng nhập được.

Chosen:
Bạn có thể thử đặt lại mật khẩu bằng đường dẫn...

Rejected:
Tôi không biết. Hãy tự tìm cách.
```

SFT trên `chosen` giúp mô hình học phong cách hội thoại và từ vựng liên quan. Tuy nhiên, vì `rejected` cũng thuộc cùng miền hội thoại, xác suất của nó chưa chắc giảm.

Thí nghiệm pilot của bài báo ghi nhận đúng hiện tượng này: khi chỉ SFT trên chosen response, log-probability của rejected response vẫn tăng tương tự. ([arXiv][2])

ORPO giải quyết vấn đề bằng cách thêm một thành phần **so sánh tương đối** giữa chosen và rejected.

---

## 3. Hàm loss của ORPO

Objective tổng quát:

[
\mathcal{L}_{ORPO}
==================

\mathbb{E}*{(x,y_w,y_l)}
\left[
\mathcal{L}*{SFT}
+
\lambda\mathcal{L}_{OR}
\right]
]

Trong đó:

* (\mathcal{L}_{SFT}): buộc mô hình học câu trả lời chosen;
* (\mathcal{L}_{OR}): buộc chosen được ưu tiên hơn rejected;
* (\lambda): kiểm soát độ mạnh của thành phần preference.

Đây là điểm quan trọng nhất của ORPO: **absolute learning signal** từ SFT và **relative preference signal** được tối ưu đồng thời. ([arXiv][2])

---

## 4. Thành phần SFT loss

Với câu trả lời chosen (y_w), SFT loss cơ bản là negative log-likelihood:

[
\mathcal{L}_{SFT}
=================

-\frac{1}{|y_w|}
\sum_{t=1}^{|y_w|}
\log \pi_\theta
\left(
y_{w,t}\mid x,y_{w,<t}
\right)
]

Nó làm tăng xác suất token của chosen response.

Việc chia cho độ dài câu trả lời tạo ra **average token log-probability**, giúp giảm ảnh hưởng trực tiếp của độ dài sequence:

[
\log P_\theta(y|x)
==================

\frac{1}{m}
\sum_{t=1}^{m}
\log P_\theta(y_t|x,y_{<t})
]

Đây cũng là định nghĩa xác suất sequence được bài báo dùng trong phần ORPO. ([arXiv][2])

---

## 5. Odds và odds ratio

### Probability và odds

Với xác suất (P), odds được định nghĩa:

[
\operatorname{odds}(P)=\frac{P}{1-P}
]

Ví dụ:

| (P) | Odds |
| --: | ---: |
| 0.2 | 0.25 |
| 0.5 |    1 |
| 0.8 |    4 |
| 0.9 |    9 |

Nếu (P=0.8), odds bằng 4, tức là biến cố có khả năng xảy ra gấp 4 lần khả năng không xảy ra.

Trong ORPO:

[
\operatorname{odds}_{\theta}(y|x)
=================================

\frac{P_\theta(y|x)}
{1-P_\theta(y|x)}
]

### Odds ratio giữa chosen và rejected

[
\operatorname{OR}_{\theta}(y_w,y_l)
===================================

\frac{
\operatorname{odds}*{\theta}(y_w|x)
}{
\operatorname{odds}*{\theta}(y_l|x)
}
]

Nếu odds ratio lớn hơn 1, mô hình đang nghiêng về chosen. Nếu nhỏ hơn 1, mô hình đang ưu tiên rejected.

---

## 6. Preference loss của ORPO

ORPO sử dụng:

[
\mathcal{L}_{OR}
================

-\log \sigma
\left(
\log
\frac{
\operatorname{odds}*\theta(y_w|x)
}{
\operatorname{odds}*\theta(y_l|x)
}
\right)
]

Đặt:

[
z=
\log\operatorname{odds}_\theta(y_w|x)
-------------------------------------

\log\operatorname{odds}_\theta(y_l|x)
]

thì:

[
\mathcal{L}_{OR}=-\log\sigma(z)
]

Loss này có hành vi như sau:

* nếu chosen được đánh giá cao hơn rejected nhiều, (z) lớn và loss nhỏ;
* nếu hai câu gần ngang nhau, loss còn đáng kể;
* nếu rejected được đánh giá cao hơn, loss lớn và gradient mạnh.

Do đó quá trình huấn luyện sẽ:

[
\operatorname{odds}(y_w|x)\uparrow
\qquad
\operatorname{odds}(y_l|x)\downarrow
]

Công thức objective và odds-ratio loss được trình bày trực tiếp trong mục 4.2 của bài báo. ([arXiv][2])

---

## 7. Tại sao dùng odds thay vì probability ratio?

Một lựa chọn đơn giản hơn có thể là:

[
\frac{P(y_w|x)}{P(y_l|x)}
]

ORPO thay vào đó dùng:

[
\frac{P_w/(1-P_w)}
{P_l/(1-P_l)}
]

Tức là:

[
\log OR
=======

\log P_w-\log P_l
-\log(1-P_w)+\log(1-P_l)
]

So với log probability ratio thông thường:

[
\log\frac{P_w}{P_l}
===================

\log P_w-\log P_l
]

odds ratio có thêm:

[
-\log(1-P_w)+\log(1-P_l)
]

Các thành phần này khiến objective không chỉ so sánh likelihood của hai câu mà còn xét “xác suất không tạo ra” mỗi câu.

Về gradient, bài báo phân tích ORPO thành hai phần:

[
\nabla_\theta \mathcal L_{OR}
=============================

\delta(d),h(d)
]

Trong đó:

* (\delta(d)) hoạt động như một trọng số thích nghi: khi mô hình đã phân biệt đúng chosen và rejected, gradient giảm;
* (h(d)) tạo sự tương phản giữa gradient của chosen và rejected.

Nói trực quan, ORPO tập trung mạnh hơn vào những cặp mà mô hình đang xếp sai hoặc chưa tạo đủ khoảng cách. ([arXiv][2])

---

## 8. Ví dụ số đơn giản

Giả sử mô hình cho:

[
P_w=0.7,\qquad P_l=0.4
]

Odds:

[
\operatorname{odds}_w
=====================

# \frac{0.7}{0.3}

2.333
]

[
\operatorname{odds}_l
=====================

# \frac{0.4}{0.6}

0.667
]

Odds ratio:

[
OR=\frac{2.333}{0.667}\approx3.5
]

Log odds ratio:

[
\log OR\approx1.253
]

Preference loss:

[
-\log\sigma(1.253)\approx0.251
]

Nếu mô hình xếp sai:

[
P_w=0.4,\qquad P_l=0.7
]

thì:

[
OR\approx0.286
]

[
-\log\sigma(\log OR)\approx1.504
]

Loss lớn hơn nhiều, nên mô hình nhận tín hiệu sửa mạnh hơn.

---

## 9. ORPO khác DPO như thế nào?

### DPO objective — dạng khái quát

DPO tối ưu sự khác biệt giữa policy model và reference model:

[
\mathcal L_{DPO}
================

-\log\sigma
\left[
\beta
\left(
\log\frac{\pi_\theta(y_w|x)}
{\pi_{\mathrm{ref}}(y_w|x)}
---------------------------

\log\frac{\pi_\theta(y_l|x)}
{\pi_{\mathrm{ref}}(y_l|x)}
\right)
\right]
]

Reference model đóng vai trò neo policy, hạn chế nó lệch quá xa khỏi mô hình ban đầu.

### ORPO

ORPO không dùng (\pi_{\mathrm{ref}}):

[
\mathcal L_{ORPO}
=================

\mathcal L_{SFT}
+
\lambda\mathcal L_{OR}
]

| Thuộc tính         | DPO                      | ORPO                      |
| ------------------ | ------------------------ | ------------------------- |
| Reward model       | Không                    | Không                     |
| PPO/RL             | Không                    | Không                     |
| Reference model    | Có                       | Không                     |
| SFT riêng trước đó | Thường có                | Không bắt buộc            |
| Loss trên chosen   | Gián tiếp qua preference | Trực tiếp bằng NLL        |
| Pipeline           | SFT rồi DPO              | Một giai đoạn             |
| Regularization     | Reference model          | SFT term và cấu trúc odds |
| GPU memory         | Cao hơn                  | Thấp hơn                  |

DPO phù hợp khi đã có một SFT checkpoint tốt và muốn alignment có một điểm neo rõ ràng. ORPO hấp dẫn khi muốn huấn luyện trực tiếp từ base model bằng preference dataset và giảm tài nguyên.

---

## 10. Hiệu quả tính toán

Đối với mỗi prompt, cả chosen và rejected đều cần forward pass.

Với DPO:

* policy forward cho chosen;
* policy forward cho rejected;
* reference forward cho chosen;
* reference forward cho rejected.

Tổng cộng về mặt khái niệm là bốn lượt forward.

Với ORPO:

* policy forward cho chosen;
* policy forward cho rejected.

Không cần reference model, nên giảm bộ nhớ dành cho model weights và giảm số phép tính forward. Bài báo mô tả ORPO có khoảng một nửa số forward pass cần thiết trên mỗi batch so với cấu hình DPO/reference-model tương ứng. ([arXiv][2])

Điều này không có nghĩa tổng thời gian huấn luyện luôn giảm chính xác 50%, vì còn:

* backward pass;
* optimizer;
* padding;
* communication giữa GPU;
* gradient checkpointing;
* cách implementation ghép chosen/rejected.

Nhưng về kiến trúc, ORPO rõ ràng nhẹ hơn.

---

## 11. Thiết lập thực nghiệm

Tác giả đánh giá các mô hình từ nhỏ tới 7B:

* OPT: 125M, 350M và 1.3B;
* Phi-2: 2.7B;
* Llama-2: 7B;
* Mistral: 7B.

Hai preference dataset chính:

* **Anthropic HH-RLHF**;
* **Binarized UltraFeedback**.

Các baseline gồm:

* SFT;
* PPO/RLHF;
* DPO;
* ORPO.

Các benchmark được dùng gồm AlpacaEval, MT-Bench, IFEval và đánh giá bằng reward model. ([arXiv][2])

---

## 12. Kết quả nổi bật

Theo kết quả được báo cáo trong bài:

* Phi-2 2.7B + ORPO đạt **6.35%** trên AlpacaEval 2.0, so với **0.78%** của Phi-2 SFT + DPO trong thiết lập của tác giả;
* Llama-2 7B + ORPO đạt **9.44%**;
* Mistral-ORPO-(\alpha) đạt **11.33%**;
* Mistral-ORPO-(\beta) đạt **12.20%**;
* Mistral-ORPO-(\beta) đạt **7.32** trên MT-Bench và **66.19%** IFEval instruction-level loose accuracy. ([arXiv][2])

Trong các thí nghiệm OPT:

* ORPO thường vượt SFT và PPO;
* mức thắng so với DPO tăng theo kích thước mô hình trong các cấu hình được thử;
* trên HH-RLHF, OPT-1.3B ORPO có win rate **70.9%** so với DPO theo reward model của nghiên cứu;
* trên UltraFeedback, con số tương ứng là **57.8%**. ([arXiv][2])

Các con số này nên được hiểu trong phạm vi thiết lập năm 2024 của bài báo, không phải bằng chứng rằng ORPO luôn vượt DPO trên mọi mô hình và dataset.

---

## 13. Điểm mạnh

### Pipeline đơn giản

Không cần chuỗi:

[
\text{SFT}\rightarrow\text{DPO}
]

mà có thể huấn luyện trực tiếp:

[
\text{Base model}\rightarrow\text{ORPO}
]

### Không cần reference model

Điều này tiết kiệm đáng kể VRAM, đặc biệt khi huấn luyện full fine-tuning.

### Không cần reward model hay RL

ORPO là một objective supervised có thể huấn luyện bằng backpropagation thông thường.

### Tận dụng cả chosen và rejected

SFT thông thường bỏ qua rejected. ORPO dùng nó để tạo tín hiệu âm có điều kiện theo từng prompt.

### Dễ tích hợp

Hugging Face TRL hiện cung cấp `ORPOTrainer`, với dữ liệu dạng `prompt`, `chosen`, `rejected`. ([Hugging Face][3])

---

## 14. Hạn chế

### Phụ thuộc mạnh vào dữ liệu preference

Nếu `chosen` và `rejected` bị gán nhãn sai, khác nhau do độ dài hoặc mang bias từ judge model, ORPO sẽ học trực tiếp các bias đó.

### Không có reference anchor tường minh

Không dùng reference model giúp giảm chi phí, nhưng đồng thời ORPO mất cơ chế neo rõ ràng như KL regularization hoặc reference ratio của DPO.

Nếu (\lambda) quá lớn, mô hình có thể tối ưu preference dataset quá mạnh và làm suy giảm một số năng lực tổng quát.

### Có thể giảm diversity trên cùng prompt

Phân tích lexical diversity của bài báo cho thấy ORPO có thể tạo các câu trả lời ít đa dạng hơn trên cùng một input so với DPO. Tác giả diễn giải rằng ORPO tập trung xác suất mạnh hơn vào những token được mong muốn. ([arXiv][2])

### Chưa chứng minh scaling lớn trong bài gốc

Bài báo chủ yếu kiểm tra đến 7B. Chính tác giả liệt kê việc chưa mở rộng quá 7B và chưa so sánh với phạm vi rộng hơn của các thuật toán preference optimization là hạn chế. ([arXiv][2])

### Kết quả benchmark có thể chịu ảnh hưởng bởi verbosity

Các benchmark dựa trên LLM-as-a-judge như AlpacaEval và MT-Bench có thể nhạy với độ dài, phong cách và judge bias. Vì vậy không nên dùng một benchmark duy nhất để kết luận chất lượng alignment.

---

## 15. Vai trò của hyperparameter (\lambda)

[
\mathcal L
==========

\mathcal L_{SFT}
+
\lambda\mathcal L_{OR}
]

* (\lambda) nhỏ: hành vi gần SFT; model học chosen nhưng có thể chưa phân biệt mạnh với rejected.
* (\lambda) lớn: preference separation mạnh hơn, nhưng có thể gây over-optimization hoặc làm mất ổn định.
* (\lambda) hợp lý phụ thuộc model, dataset, learning rate và cách chuẩn hóa sequence probability.

Trong các mô hình lớn của bài báo, tác giả dùng các giá trị như khoảng (0.1)–(0.25) ở một số cấu hình; chẳng hạn Phi-2 dùng (0.25), Llama-2 dùng (0.2). ([arXiv][2])

Trong thực nghiệm mới, nên tune đồng thời:

[
\lambda,\quad \text{learning rate},\quad \text{epochs},\quad \text{max length}
]

và theo dõi:

* chosen log-probability;
* rejected log-probability;
* reward margin;
* validation preference accuracy;
* benchmark năng lực nền.

---

## 16. Pseudocode

```python
for batch in dataloader:
    prompt = batch["prompt"]
    chosen = batch["chosen"]
    rejected = batch["rejected"]

    chosen_logps = model.sequence_log_probability(
        prompt, chosen, average_by_length=True
    )
    rejected_logps = model.sequence_log_probability(
        prompt, rejected, average_by_length=True
    )

    # NLL trên chosen
    sft_loss = -chosen_logps.mean()

    chosen_prob = chosen_logps.exp()
    rejected_prob = rejected_logps.exp()

    chosen_log_odds = (
        chosen_logps - torch.log1p(-chosen_prob)
    )
    rejected_log_odds = (
        rejected_logps - torch.log1p(-rejected_prob)
    )

    log_odds_ratio = chosen_log_odds - rejected_log_odds
    preference_loss = -F.logsigmoid(log_odds_ratio).mean()

    loss = sft_loss + lambda_orpo * preference_loss

    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

Trong implementation thực tế cần xử lý cẩn thận:

* masking prompt token;
* padding;
* sequence length normalization;
* numerical stability khi tính (\log(1-P));
* ghép chosen/rejected trong một forward batch để tăng hiệu quả.

---

## 17. Khi nào nên chọn ORPO?

ORPO phù hợp khi:

* bắt đầu từ base model hoặc checkpoint chưa instruction-tuned tốt;
* có dataset preference chất lượng cao;
* GPU memory hạn chế;
* muốn một pipeline đơn giản, không reward/reference model;
* muốn kết hợp instruction tuning và preference alignment.

DPO có thể phù hợp hơn khi:

* đã có SFT model mạnh;
* muốn giữ model gần checkpoint tham chiếu;
* cần hệ sinh thái recipe và kinh nghiệm triển khai rộng hơn;
* dataset preference nhỏ hoặc nhiễu và cần regularization rõ ràng.

## Kết luận

Đóng góp quan trọng nhất của ORPO không chỉ là bỏ reference model. Nó đưa ra quan điểm rằng:

[
\boxed{
\text{Preference alignment}
\approx
\text{SFT trên chosen}
+
\text{một penalty nhẹ đối với rejected}
}
]

SFT cung cấp tín hiệu mạnh để học câu trả lời mong muốn, còn odds-ratio loss tạo ranh giới tương đối giữa câu trả lời tốt và xấu. Nhờ kết hợp hai tín hiệu trong một objective, ORPO đạt pipeline đơn giản và tiết kiệm tài nguyên hơn RLHF/DPO truyền thống, dù vẫn cần kiểm soát chất lượng dữ liệu, (\lambda), diversity và khả năng overfit preference.

[1]: https://aclanthology.org/2024.emnlp-main.626/ "ORPO: Monolithic Preference Optimization without Reference Model - ACL Anthology"
[2]: https://arxiv.org/html/2403.07691v2 "ORPO: Monolithic Preference Optimization without Reference Model"
[3]: https://huggingface.co/docs/trl/en/orpo_trainer "ORPO Trainer · Hugging Face"
