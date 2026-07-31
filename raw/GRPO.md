## GRPO là gì?

**GRPO — Group Relative Policy Optimization** là một thuật toán reinforcement learning dùng để hậu huấn luyện LLM. Nó được giới thiệu trong bài:

**“DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models”** của DeepSeek-AI, công bố năm 2024.

GRPO không phải một bài báo độc lập ban đầu; nó là đóng góp chính trong phần reinforcement learning của DeepSeekMath. Sau đó, DeepSeek tiếp tục dùng GRPO ở quy mô lớn để huấn luyện **DeepSeek-R1-Zero** và **DeepSeek-R1**. ([arXiv][1])

---

## 1. Vấn đề GRPO muốn giải quyết

Trong RLHF/RL cho LLM, PPO thường cần ít nhất bốn thành phần:

1. **Policy/actor**: LLM đang được huấn luyện.
2. **Reference policy**: mô hình tham chiếu để hạn chế policy thay đổi quá xa.
3. **Reward model**: chấm điểm câu trả lời.
4. **Value/critic model**: dự đoán giá trị kỳ vọng để tính advantage.

Điểm tốn kém là **critic thường có kích thước gần bằng policy**. Với một LLM lớn, việc lưu tham số, optimizer states, activations và gradient cho thêm một critic gây áp lực đáng kể lên GPU.

GRPO bỏ critic. Thay vì học một value function (V_\psi), nó lấy **điểm trung bình của nhiều câu trả lời cho cùng một prompt** làm baseline. Đây là nguyên nhân chính GRPO tiết kiệm bộ nhớ hơn PPO. ([arXiv][1])

---

## 2. Trực giác cốt lõi

Giả sử có một câu hỏi:

> Giải phương trình (x^2-5x+6=0).

Mô hình sinh ra (G=4) lời giải:

| Output                                  | Reward |
| --------------------------------------- | -----: |
| (o_1): trả lời (x=2,3), giải thích đúng |    1.0 |
| (o_2): trả lời (x=2,3), trình bày kém   |    0.8 |
| (o_3): trả lời (x=1,6)                  |    0.0 |
| (o_4): không đưa đáp án đúng format     |    0.2 |

GRPO không nhất thiết hỏi critic rằng “mỗi output có giá trị bao nhiêu”. Nó so sánh các output **trong cùng nhóm**:

* Output tốt hơn mức trung bình nhận advantage dương.
* Output kém hơn mức trung bình nhận advantage âm.
* Output gần trung bình có cập nhật nhỏ.

Nói đơn giản:

> “Trong các câu trả lời cho cùng một câu hỏi, hãy tăng xác suất những câu tốt tương đối và giảm xác suất những câu kém tương đối.”

Tên **Group Relative** xuất phát từ chính phép so sánh tương đối trong nhóm này.

---

## 3. Cách tính advantage

Với prompt (q), policy cũ sinh ra một nhóm:

[
{o_1,o_2,\ldots,o_G}.
]

Mỗi output nhận reward:

[
r_i = r(q,o_i).
]

Trong thiết lập outcome supervision đơn giản, advantage được chuẩn hóa theo nhóm:

[
\hat A_i
========

\frac{r_i-\operatorname{mean}(r_1,\ldots,r_G)}
{\operatorname{std}(r_1,\ldots,r_G)+\delta}.
]

Trong đó (\delta) là một số nhỏ để tránh chia cho 0.

Với ví dụ reward:

[
[1.0,\ 0.8,\ 0.0,\ 0.2],
]

ta có:

[
\mu=0.5,
\qquad
\sigma\approx0.412.
]

Advantage gần đúng:

[
[1.21,\ 0.73,\ -1.21,\ -0.73].
]

Vì vậy:

* (o_1,o_2) được củng cố.
* (o_3,o_4) bị giảm xác suất.
* Mức độ cập nhật phụ thuộc vị trí tương đối trong nhóm, không chỉ reward tuyệt đối.

Trong outcome-level GRPO, cùng một advantage thường được gán cho tất cả token thuộc cùng output:

[
\hat A_{i,t}=\hat A_i.
]

DeepSeekMath cũng mô tả biến thể **process supervision**, trong đó reward và advantage có thể được gán theo từng bước reasoning thay vì chỉ cho toàn bộ câu trả lời. ([arXiv][1])

---

## 4. Hàm mục tiêu GRPO

Đặt importance ratio tại token (t):

[
\rho_{i,t}(\theta)
==================

\frac{
\pi_\theta(o_{i,t}\mid q,o_{i,<t})
}{
\pi_{\theta_{\text{old}}}(o_{i,t}\mid q,o_{i,<t})
}.
]

Thành phần PPO-style clipped objective là:

[
\min
\left(
\rho_{i,t}\hat A_{i,t},
\operatorname{clip}
(\rho_{i,t},1-\epsilon,1+\epsilon)
\hat A_{i,t}
\right).
]

Hàm mục tiêu GRPO có thể viết khái quát:

[
J_{\text{GRPO}}(\theta)
=======================

\mathbb{E}
\left[
\frac{1}{G}
\sum_{i=1}^{G}
\frac{1}{|o_i|}
\sum_{t=1}^{|o_i|}
\left(
\min
\left[
\rho_{i,t}\hat A_{i,t},
\operatorname{clip}
(\rho_{i,t},1-\epsilon,1+\epsilon)
\hat A_{i,t}
\right]
-------

\beta D_{\mathrm{KL}}
(\pi_\theta\Vert\pi_{\mathrm{ref}})
\right)
\right].
]

Có ba phần quan trọng:

### Importance ratio

[
\rho_{i,t}
==========

\frac{\pi_\theta}{\pi_{\theta_{\text{old}}}}
]

cho biết policy mới đã thay đổi xác suất token bao nhiêu so với policy đã dùng để lấy mẫu.

### Clipping

[
\operatorname{clip}(\rho,1-\epsilon,1+\epsilon)
]

ngăn policy thay đổi quá mạnh trong một bước cập nhật.

Ví dụ với (\epsilon=0.2), ratio hiệu dụng thường bị giới hạn trong khoảng:

[
[0.8,1.2].
]

### KL regularization

[
-\beta D_{\mathrm{KL}}(\pi_\theta\Vert\pi_{\mathrm{ref}})
]

giữ policy gần mô hình tham chiếu, tránh việc mô hình tối ưu reward bằng các hành vi bất thường như:

* lặp lại vô hạn;
* khai thác lỗi reward model;
* mất khả năng ngôn ngữ chung;
* thay đổi phong cách quá cực đoan.

DeepSeekMath đưa KL trực tiếp vào objective thay vì coi KL là một phần reward token như một số thiết lập PPO. ([arXiv][1])

---

## 5. Quy trình huấn luyện GRPO

Một iteration điển hình gồm:

### Bước 1: Lấy một batch prompt

[
q_1,q_2,\ldots,q_B.
]

### Bước 2: Sinh nhiều output cho mỗi prompt

Với mỗi (q), lấy mẫu (G) output từ policy cũ:

[
o_1,\ldots,o_G
\sim
\pi_{\theta_{\text{old}}}(\cdot\mid q).
]

Việc sampling cần có đủ độ đa dạng, thường sử dụng temperature khác 0.

### Bước 3: Chấm reward

Reward có thể đến từ:

* reward model;
* unit test cho code;
* kiểm tra đáp án toán;
* symbolic verifier;
* format checker;
* human preference model;
* nhiều reward kết hợp.

### Bước 4: Chuẩn hóa reward trong từng nhóm

[
\hat A_i
========

\frac{r_i-\mu_q}{\sigma_q+\delta}.
]

Lưu ý: chuẩn hóa được thực hiện **riêng cho từng prompt**, không phải trên toàn batch.

### Bước 5: Tính loss token-level

Policy tăng xác suất các token trong output có advantage dương, giảm xác suất output có advantage âm.

### Bước 6: Cập nhật policy

Có thể thực hiện một hoặc nhiều gradient step trên cùng rollout batch.

### Bước 7: Làm mới old policy

Sau một số bước:

[
\pi_{\theta_{\text{old}}}\leftarrow\pi_\theta.
]

Sau đó sinh rollout mới và lặp lại.

---

## 6. GRPO khác PPO như thế nào?

| Thành phần                     | PPO                   | GRPO                                     |
| ------------------------------ | --------------------- | ---------------------------------------- |
| Actor/policy                   | Có                    | Có                                       |
| Reference model                | Thường có             | Có                                       |
| Reward model/verifier          | Có                    | Có                                       |
| Critic/value model             | Có                    | **Không**                                |
| Advantage                      | Từ value model và GAE | Từ reward tương đối trong nhóm           |
| Số output mỗi prompt           | Có thể một hoặc nhiều | Thường bắt buộc nhiều                    |
| Bộ nhớ                         | Cao hơn               | Thấp hơn do bỏ critic                    |
| Độ phân giải credit assignment | Có thể theo token     | Thường thô hơn nếu chỉ có outcome reward |

GRPO không đơn giản là PPO “bỏ value model”. Phần thay thế critic là một **baseline Monte Carlo theo nhóm**:

[
b(q)\approx\frac{1}{G}\sum_{i=1}^{G}r(q,o_i).
]

Baseline này phụ thuộc vào prompt. Điều đó quan trọng vì độ khó của các prompt khác nhau rất lớn.

Ví dụ reward (0.5):

* Có thể là xuất sắc đối với một bài rất khó.
* Có thể là tệ đối với một bài rất dễ.

So sánh trong cùng prompt giúp giảm ảnh hưởng của sự khác biệt độ khó này.

---

## 7. Tại sao GRPO hợp với reasoning LLM?

### Reward có thể kiểm chứng

Toán và code thường có reward tương đối đáng tin:

* đáp án cuối đúng hay sai;
* test case pass hay fail;
* proof checker chấp nhận hay không;
* output có đúng format không.

Do đó không nhất thiết cần một reward model học từ sở thích con người cho mọi ví dụ.

### Có thể khám phá nhiều chiến lược

Khi lấy nhiều output cho cùng một bài, policy có thể thử:

* nhiều chuỗi suy luận;
* nhiều phép biến đổi;
* nhiều thuật toán;
* tự kiểm tra hoặc sửa lỗi.

Những trajectory thành công nhận advantage dương, khiến các pattern đó dần trở nên phổ biến.

### So sánh trong cùng bài toán hợp lý hơn

Reward model thường đáng tin hơn khi so sánh hai câu trả lời cho cùng một câu hỏi hơn là so sánh reward tuyệt đối giữa hai câu hỏi hoàn toàn khác nhau. DeepSeekMath nêu đây là một động lực tự nhiên cho cách tính group-relative advantage. ([arXiv][1])

---

## 8. Reward trong DeepSeek-R1

Trong **DeepSeek-R1-Zero**, DeepSeek ưu tiên reward dựa trên quy tắc thay vì phụ thuộc hoàn toàn vào neural reward model. Hai loại chính được mô tả gồm:

* **Accuracy reward**: đáp án có đúng hay không.
* **Format reward**: output có tuân theo cấu trúc reasoning/answer yêu cầu hay không.

Cách này giảm nguy cơ reward model tự mắc lỗi trên các bài reasoning phức tạp. DeepSeek-R1-Zero áp dụng GRPO trực tiếp lên DeepSeek-V3-Base mà không cần SFT trước; paper báo cáo khả năng reasoning, tự kiểm tra và chuỗi suy luận dài xuất hiện trong quá trình RL. Tuy nhiên, mô hình Zero gặp vấn đề về khả năng đọc và trộn ngôn ngữ, nên DeepSeek-R1 sau đó bổ sung cold-start data và pipeline nhiều giai đoạn. ([arXiv][2])

Pipeline R1 ở mức khái quát:

[
\text{Base}
\rightarrow
\text{cold-start SFT}
\rightarrow
\text{reasoning GRPO}
\rightarrow
\text{rejection sampling + SFT}
\rightarrow
\text{RL tổng quát}.
]

Điều này cho thấy **GRPO là một thành phần**, không phải toàn bộ bí quyết của DeepSeek-R1.

---

## 9. Điểm mạnh

### Tiết kiệm bộ nhớ

Không cần critic có kích thước gần bằng policy.

### Đơn giản hóa hệ thống RL

Không cần đồng thời huấn luyện value function và xử lý value loss.

### Hợp với reward kiểm chứng được

Đặc biệt phù hợp với:

* toán;
* code;
* logic;
* theorem proving;
* tool use có trạng thái thành công rõ ràng.

### Tự cân bằng độ khó theo prompt

Reward được chuẩn hóa trong nhóm nên baseline thích nghi với từng bài.

### Hỗ trợ online exploration

Rollout được sinh từ policy hiện tại hoặc policy cũ gần hiện tại, nên mô hình liên tục khám phá các cách giải mới.

---

## 10. Hạn chế quan trọng

### 10.1 Nhóm có reward giống nhau thì gần như không học được

Nếu tất cả output đều sai:

[
r_1=r_2=\cdots=r_G=0,
]

thì:

[
\hat A_i\approx0.
]

Gradient từ policy objective biến mất hoặc rất nhỏ.

Tương tự, nếu tất cả đều đúng với cùng reward, GRPO không biết output nào tốt hơn. Đây thường được gọi là hiện tượng **advantage collapse** hoặc zero-variance group.

Hệ quả thực tế:

* Prompt quá khó: tất cả câu trả lời sai.
* Prompt quá dễ: tất cả câu trả lời đúng.
* Cả hai loại có thể cung cấp tín hiệu học yếu.

Do đó, chọn dữ liệu có độ khó phù hợp với năng lực hiện tại của model rất quan trọng.

### 10.2 Tốn chi phí rollout

GRPO bỏ critic nhưng cần sinh (G) output cho mỗi prompt.

Chi phí sampling gần tỷ lệ:

[
B\times G\times L,
]

với (B) là số prompt và (L) là độ dài output.

Nếu reasoning dài hàng nghìn token, rollout có thể trở thành phần tốn chi phí nhất.

### 10.3 Credit assignment thô

Nếu chỉ dùng reward cuối:

[
\hat A_{i,1}=\hat A_{i,2}=\cdots=\hat A_{i,|o_i|},
]

mọi token trong câu trả lời đúng đều nhận tín hiệu dương, kể cả những bước:

* dư thừa;
* sai nhưng được sửa sau;
* không liên quan;
* suy luận vòng vo.

Process reward có thể cải thiện việc này, nhưng xây dựng process verifier đáng tin lại khó.

### 10.4 Phụ thuộc mạnh vào reward

Mô hình tối ưu đúng thứ được chấm, không nhất thiết đúng ý định thật.

Nếu reward chỉ kiểm tra đáp án cuối, model có thể học:

* đoán đáp án;
* khai thác lỗi parser;
* chèn nhiều đáp án;
* tạo output thỏa regex nhưng reasoning không hợp lệ.

### 10.5 Group-relative không thể hiện chất lượng tuyệt đối

Output tốt nhất trong một nhóm rất tệ vẫn có thể nhận advantage dương.

Ví dụ:

[
[0.01,\ 0.00,\ 0.00,\ 0.00].
]

Output reward (0.01) sẽ được củng cố tương đối dù chất lượng tuyệt đối gần như bằng không. Reward design, filtering và curriculum phải xử lý trường hợp này.

### 10.6 Có thể tạo áp lực tăng độ dài

Trong reasoning RL, câu trả lời dài hơn có thể có nhiều cơ hội tự sửa và tìm đúng đáp án. Nếu không có length control, policy đôi khi học cách dùng ngày càng nhiều token, kể cả khi hiệu quả biên thấp. Một số nghiên cứu tiếp nối đã phân tích các bias và failure mode kiểu này; vì vậy thực nghiệm GRPO hiện đại thường theo dõi cả accuracy, length, entropy, KL và reward hacking chứ không chỉ reward trung bình. ([arXiv][3])

---

## 11. GRPO và REINFORCE

Ở góc nhìn đơn giản, GRPO khá gần **REINFORCE with a prompt-dependent baseline**.

Policy gradient cơ bản:

[
\nabla_\theta J
===============

\mathbb{E}
\left[
(r-b)
\nabla_\theta\log\pi_\theta(o\mid q)
\right].
]

GRPO chọn:

[
b(q)=\operatorname{mean}_{j=1}^{G}r(q,o_j),
]

sau đó thêm:

* chuẩn hóa độ lệch chuẩn;
* PPO clipping;
* importance sampling;
* KL regularization;
* token-level objective.

Vì vậy có thể hình dung:

[
\boxed{
\text{GRPO}
\approx
\text{group-normalized REINFORCE}
+
\text{PPO clipping}
+
\text{KL control}
}
]

Đây là mô tả trực giác, không phải định nghĩa hình thức đầy đủ.

---

## 12. Pseudocode tối giản

```python
for prompts in dataloader:
    # G outputs cho mỗi prompt
    outputs = old_policy.generate(
        prompts,
        num_return_sequences=group_size,
        do_sample=True,
    )

    rewards = reward_function(prompts, outputs)

    # Chuẩn hóa riêng trong từng nhóm/prompt
    advantages = normalize_within_each_prompt(rewards)

    logp = policy.log_probs(prompts, outputs)
    old_logp = old_policy.log_probs(prompts, outputs)

    ratio = torch.exp(logp - old_logp)

    unclipped = ratio * advantages
    clipped = torch.clamp(
        ratio,
        1 - epsilon,
        1 + epsilon,
    ) * advantages

    policy_objective = torch.minimum(
        unclipped,
        clipped,
    )

    kl = compute_kl(policy, reference_policy, prompts, outputs)

    loss = -(policy_objective - beta * kl).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

Một implementation thực tế còn cần xử lý:

* padding mask;
* token mask cho phần prompt và completion;
* distributed generation;
* stale rollouts;
* reward aggregation;
* std bằng 0;
* sequence length normalization;
* gradient accumulation;
* entropy và KL monitoring;
* clipping phạm vi gradient;
* loại bỏ output không parse được.

---

## 13. Một hiểu lầm phổ biến

**“GRPO tự tạo ra reasoning từ con số 0.”**

Không hoàn toàn.

GRPO chỉ củng cố hành vi mà policy có khả năng khám phá trong quá trình sampling. Nếu base model chưa có:

* kiến thức nền;
* năng lực sinh lời giải;
* khả năng làm theo instruction;
* xác suất dù rất nhỏ để tạo trajectory đúng,

thì reward không thể cung cấp nội dung lời giải chi tiết từ hư không.

Một cách diễn đạt chính xác hơn:

> GRPO làm tăng xác suất của các reasoning pattern hữu ích mà model có thể khám phá, đồng thời giảm xác suất các pattern kém hiệu quả.

Chất lượng pretraining, dữ liệu prompt, reward/verifier, sampling budget và curriculum vẫn quyết định rất lớn kết quả cuối cùng.

---

## 14. Kết luận

Ý tưởng trung tâm của GRPO rất gọn:

[
\boxed{
\text{Sinh nhiều câu trả lời cho cùng prompt}
\rightarrow
\text{chấm điểm}
\rightarrow
\text{chuẩn hóa reward trong nhóm}
\rightarrow
\text{tăng xác suất output tốt tương đối}
}
]

Giá trị lớn nhất của nó là:

* loại bỏ critic;
* giảm chi phí bộ nhớ so với PPO;
* tận dụng reward kiểm chứng được;
* phù hợp với online RL cho reasoning.

Nhưng GRPO không tự giải quyết các vấn đề cơ bản của RL cho LLM: reward hacking, rollout cost, credit assignment, zero-variance groups, length inflation và sự phụ thuộc vào năng lực của base model.

[1]: https://arxiv.org/html/2402.03300v3 "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"
[2]: https://arxiv.org/html/2501.12948v1 "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"
[3]: https://arxiv.org/abs/2503.20783?utm_source=chatgpt.com "Understanding R1-Zero-Like Training: A Critical Perspective"
