## 1. Bài báo là gì?

**“Constitutional AI: Harmlessness from AI Feedback”** là bài báo của Yuntao Bai và cộng sự tại Anthropic, công bố ngày **15/12/2022**. Bài báo đề xuất phương pháp huấn luyện trợ lý LLM trở nên an toàn hơn bằng cách cung cấp cho mô hình một tập nguyên tắc viết bằng ngôn ngữ tự nhiên — gọi là **constitution**, tức “bộ hiến pháp” — thay vì yêu cầu con người trực tiếp gắn nhãn hàng loạt câu trả lời độc hại. ([arXiv][1])

Ý tưởng trung tâm là:

> Dùng một mô hình AI để phê bình, sửa và đánh giá câu trả lời của chính AI dựa trên các nguyên tắc do con người xác định.

Phương pháp này được gọi là **Constitutional AI**, viết tắt là **CAI**.

---

## 2. Vấn đề mà bài báo muốn giải quyết

Trong RLHF truyền thống — **Reinforcement Learning from Human Feedback** — quy trình thường như sau:

1. LLM tạo ra nhiều câu trả lời.
2. Con người so sánh và xếp hạng các câu trả lời.
3. Một reward model học từ các xếp hạng đó.
4. LLM được tối ưu để tạo ra câu trả lời có điểm thưởng cao.

Cách làm này có một số vấn đề:

* Tốn nhiều chi phí gắn nhãn.
* Người đánh giá phải đọc nội dung bạo lực, thù ghét hoặc nguy hiểm.
* Tiêu chuẩn đạo đức giữa các annotator có thể không nhất quán.
* Các quyết định giá trị nằm ẩn trong dữ liệu xếp hạng, khó kiểm tra.
* Khi tối ưu quá mạnh cho “harmlessness”, mô hình có thể trở nên **quá né tránh**: từ chối cả những câu hỏi vô hại.

CAI cố gắng chuyển phần lớn việc giám sát harmlessness từ con người sang AI. Con người vẫn quyết định các nguyên tắc nền tảng, nhưng AI thực hiện việc áp dụng các nguyên tắc ở quy mô lớn. Bài báo nhấn mạnh rằng họ không sử dụng nhãn của con người để xác định các câu trả lời độc hại trong quy trình harmlessness; sự giám sát của con người chủ yếu xuất hiện dưới dạng danh sách nguyên tắc. ([arXiv][1])

---

# 3. “Constitution” là gì?

Constitution là một danh sách các nguyên tắc được viết bằng ngôn ngữ tự nhiên, chẳng hạn về:

* Tránh hỗ trợ hành vi bất hợp pháp hoặc nguy hiểm.
* Tôn trọng quyền con người.
* Không đưa ra nội dung phân biệt đối xử.
* Không khuyến khích bạo lực, lạm dụng hoặc tự gây hại.
* Đưa ra câu trả lời trung thực và hợp lý.
* Khi không thể đáp ứng, giải thích lý do thay vì từ chối một cách máy móc.

Một nguyên tắc có thể có dạng khái quát như:

> Hãy xác định xem câu trả lời có hỗ trợ hành vi nguy hiểm, bất hợp pháp hoặc phi đạo đức hay không.

Hoặc:

> Hãy lựa chọn câu trả lời phù hợp hơn với quyền tự do, bình đẳng và phẩm giá con người.

Điểm quan trọng là constitution **không phải một tập luật cứng trong chương trình**. Nó là văn bản được đưa vào prompt để LLM diễn giải và áp dụng.

Do đó, CAI dựa trên khả năng của LLM trong việc:

* hiểu các nguyên tắc trừu tượng;
* nhận diện vi phạm;
* giải thích vấn đề;
* viết lại câu trả lời;
* so sánh hai phương án.

---

# 4. Quy trình huấn luyện Constitutional AI

CAI có hai giai đoạn lớn:

```text
Giai đoạn 1: Supervised Learning
Tạo câu trả lời → tự phê bình → tự sửa → fine-tune

Giai đoạn 2: Reinforcement Learning
Tạo cặp câu trả lời → AI đánh giá → huấn luyện reward model
→ RL từ phản hồi AI
```

Anthropic gọi giai đoạn thứ hai là **RLAIF — Reinforcement Learning from AI Feedback**. ([arXiv][1])

---

## 5. Giai đoạn 1: Constitutional Supervised Learning

### Bước 1: Thu thập các prompt có khả năng gây hại

Mô hình được đưa các yêu cầu đối nghịch hoặc “red-team prompts”, ví dụ:

* yêu cầu hướng dẫn hành vi nguy hiểm;
* yêu cầu viết nội dung thù ghét;
* tìm cách thao túng hoặc lừa đảo;
* yêu cầu biện minh cho bạo lực;
* yêu cầu nội dung phi đạo đức.

Mục tiêu là làm lộ ra những hành vi không mong muốn của mô hình ban đầu.

### Bước 2: Mô hình tạo câu trả lời ban đầu

Với prompt (x), mô hình hiện tại tạo một câu trả lời:

[
y_0 \sim \pi_{\theta}(y\mid x)
]

Câu trả lời ban đầu có thể chứa nội dung có hại hoặc không phù hợp.

### Bước 3: Self-critique — mô hình tự phê bình

Một nguyên tắc (c_i) được chọn từ constitution. Sau đó mô hình được yêu cầu đánh giá câu trả lời của mình theo nguyên tắc này.

Dạng prompt có thể được hình dung như:

```text
Đây là yêu cầu của người dùng: ...
Đây là câu trả lời của trợ lý: ...

Hãy xác định những phần nào trong câu trả lời vi phạm nguyên tắc:
[nguyên tắc trong constitution]
```

Mô hình tạo phần phê bình:

[
k_i = \text{Critique}(x,y_{i-1},c_i)
]

Ví dụ, mô hình có thể nhận ra:

* câu trả lời cung cấp hướng dẫn quá chi tiết;
* nội dung có thể gây tổn hại;
* câu trả lời khái quát hóa về một nhóm người;
* từ chối đúng nhưng quá thô lỗ hoặc không hữu ích.

### Bước 4: Revision — mô hình tự sửa

Sau khi phê bình, mô hình được yêu cầu viết lại câu trả lời:

[
y_i = \text{Revise}(x,y_{i-1},k_i,c_i)
]

Việc critique–revision có thể được thực hiện nhiều vòng với những nguyên tắc khác nhau.

Ví dụ:

```text
Câu ban đầu:
“Đây là các bước chi tiết để thực hiện hành vi nguy hiểm...”

Phê bình:
“Câu trả lời cung cấp chỉ dẫn có thể gây tổn hại và vi phạm nguyên tắc
không hỗ trợ hành vi nguy hiểm.”

Bản sửa:
“Tôi không thể cung cấp hướng dẫn thực hiện hành vi đó. Tuy nhiên,
tôi có thể giải thích các rủi ro, biện pháp phòng tránh hoặc thông tin
an toàn liên quan.”
```

### Bước 5: Fine-tune trên các bản sửa

Các cặp:

[
(x,y_{\text{revised}})
]

được dùng làm dữ liệu supervised fine-tuning.

Mục tiêu huấn luyện thông thường là:

[
\mathcal{L}_{SFT}(\theta)
=========================

-\sum_{t}
\log \pi_{\theta}
\left(
y_t^{\text{revised}}
\mid x,y_{<t}^{\text{revised}}
\right)
]

Sau giai đoạn này, mô hình được gọi là một **SL-CAI model** hoặc constitutional supervised model.

### Ý nghĩa của giai đoạn này

Thay vì con người phải viết câu trả lời an toàn lý tưởng cho từng prompt, mô hình tự tạo dữ liệu huấn luyện thông qua:

1. phát hiện lỗi;
2. giải thích lỗi;
3. sửa lỗi.

Đây là dạng **self-improvement có điều kiện bởi nguyên tắc**.

---

# 6. Giai đoạn 2: Reinforcement Learning from AI Feedback

Supervised learning chỉ dạy mô hình bắt chước các bản sửa. Giai đoạn RL được dùng để tối ưu hành vi một cách mạnh hơn.

## Bước 1: Tạo hai câu trả lời

Với một prompt (x), mô hình tạo hai câu trả lời:

[
y_A,;y_B \sim \pi_{\theta}(y\mid x)
]

## Bước 2: AI so sánh hai câu trả lời

Một mô hình đánh giá được cung cấp:

* prompt của người dùng;
* hai câu trả lời;
* một nguyên tắc trong constitution.

Sau đó nó trả lời câu nào phù hợp với nguyên tắc hơn:

[
p_{\text{AI}}(y_A \succ y_B\mid x,c_i)
]

Quá trình này tạo ra dữ liệu preference:

[
D_{\text{AI}}
=============

{(x,y_w,y_l)}
]

trong đó:

* (y_w): câu trả lời được AI chọn;
* (y_l): câu trả lời bị AI đánh giá thấp hơn.

Bài báo cũng khảo sát việc cho mô hình sử dụng lập luận kiểu chain-of-thought trước khi đưa ra lựa chọn. Theo các tác giả, dạng suy luận này có thể cải thiện chất lượng đánh giá và giúp quá trình quyết định dễ quan sát hơn. ([arXiv][1])

## Bước 3: Huấn luyện preference model

Một mô hình phần thưởng hoặc preference model (r_\phi(x,y)) được huấn luyện để cho điểm câu trả lời tốt cao hơn.

Một loss phổ biến là:

[
\mathcal{L}_{PM}(\phi)
======================

-\mathbb{E}*{(x,y_w,y_l)}
\left[
\log
\sigma
\left(
r*\phi(x,y_w)-r_\phi(x,y_l)
\right)
\right]
]

Trong đó:

* (\sigma) là hàm sigmoid;
* reward model học để bảo đảm
  (r_\phi(x,y_w)>r_\phi(x,y_l)).

Preference model này được gọi là **AI-feedback preference model**, vì dữ liệu xếp hạng được tạo bởi AI chứ không phải annotator con người.

## Bước 4: Reinforcement learning

LLM được tối ưu để tăng reward:

[
\max_{\theta}
;
\mathbb{E}*{y\sim\pi*\theta}
[r_\phi(x,y)]
-------------

\beta
D_{KL}
\left(
\pi_\theta
\parallel
\pi_{\text{ref}}
\right)
]

Trong đó:

* (r_\phi(x,y)): điểm harmlessness/helpfulness;
* (D_{KL}): giữ mô hình mới không đi quá xa mô hình tham chiếu;
* (\beta): điều khiển mức phạt KL.

Bài báo sử dụng cơ chế RL theo dòng PPO/RLHF, nhưng nguồn reward cho harmlessness đến từ AI feedback.

Kết quả là **RL-CAI model**.

---

# 7. CAI khác RLHF ở đâu?

| Thành phần                               | RLHF truyền thống                    | Constitutional AI                       |
| ---------------------------------------- | ------------------------------------ | --------------------------------------- |
| Nguồn giá trị                            | Ẩn trong nhãn của con người          | Viết rõ dưới dạng constitution          |
| Ai so sánh câu trả lời?                  | Con người                            | Chủ yếu là AI                           |
| Chi phí mở rộng                          | Cao                                  | Thấp hơn sau khi có constitution        |
| Người gắn nhãn tiếp xúc nội dung độc hại | Nhiều                                | Ít hơn                                  |
| Khả năng kiểm tra nguyên tắc             | Khó vì nằm trong dữ liệu             | Tương đối rõ vì được viết thành văn bản |
| Khả năng thay đổi hành vi                | Thu thập dữ liệu mới                 | Có thể thay đổi hoặc thêm nguyên tắc    |
| Rủi ro                                   | Thiên kiến annotator, reward hacking | Thiên kiến constitution và AI judge     |

Tuy nhiên, CAI **không hoàn toàn loại bỏ con người**. Con người vẫn:

* viết hoặc lựa chọn constitution;
* quyết định mục tiêu huấn luyện;
* chọn dữ liệu red-team;
* thiết kế prompt đánh giá;
* đánh giá kết quả cuối;
* quyết định cách xử lý xung đột giữa các nguyên tắc.

Nói chính xác hơn, CAI chuyển từ:

> “Con người đánh giá từng đầu ra”

sang:

> “Con người định nghĩa nguyên tắc; AI áp dụng nguyên tắc ở quy mô lớn.”

---

# 8. Harmless nhưng “non-evasive”

Một đóng góp quan trọng của bài báo là phân biệt:

* **Harmlessness**: không tạo nội dung gây hại.
* **Evasiveness**: né tránh quá mức, từ chối máy móc.
* **Helpfulness**: vẫn cố gắng hỗ trợ trong phạm vi an toàn.

Một mô hình an toàn kém có thể trả lời mọi câu nhạy cảm bằng:

```text
Tôi không thể giúp bạn.
```

CAI hướng đến kiểu phản hồi:

```text
Tôi không thể cung cấp hướng dẫn thực hiện hành vi đó vì nó có thể gây
tổn hại. Tuy nhiên, tôi có thể giải thích các rủi ro, biện pháp bảo vệ
hoặc cách xử lý tình huống một cách hợp pháp và an toàn.
```

Theo bài báo, các mô hình CAI có thể đạt harmlessness cao hơn mà vẫn tham gia vào cuộc hội thoại: giải thích sự phản đối, cung cấp bối cảnh và đề xuất hướng an toàn thay thế. ([arXiv][1])

---

# 9. Hai loại reward: helpfulness và harmlessness

Trong thực tế, alignment là bài toán đa mục tiêu:

[
R(x,y)
======

\alpha R_{\text{helpful}}(x,y)
+
\gamma R_{\text{harmless}}(x,y)
]

Nếu chỉ tối ưu harmlessness:

* mô hình có thể luôn từ chối;
* câu trả lời trở nên chung chung;
* độ hữu ích giảm.

Nếu chỉ tối ưu helpfulness:

* mô hình có thể làm theo cả yêu cầu nguy hiểm;
* khả năng tuân thủ cao nhưng không an toàn.

Do đó, nghiên cứu xem xét sự đánh đổi trên một đường biên gần giống Pareto frontier:

```text
Harmlessness cao
      ↑
      |       CAI
      |      •
      |   •
      | •
      +----------------→ Helpfulness cao
```

Mục tiêu không đơn giản là cực đại hóa an toàn, mà là đạt **mức an toàn cao tại cùng một mức hữu ích**.

---

# 10. Kết quả chính của bài báo

Các đánh giá của con người trong nghiên cứu cho thấy mô hình Constitutional RL:

* ít tạo nội dung có hại hơn;
* tại một mức helpfulness tương đương, có harmlessness tốt hơn các baseline;
* ít né tránh máy móc hơn một số mô hình được tối ưu an toàn theo cách đơn giản;
* có thể phản hồi các yêu cầu gây hại bằng cách giải thích sự phản đối;
* cho phép điều khiển hành vi bằng các nguyên tắc ngôn ngữ tự nhiên;
* giảm đáng kể nhu cầu sử dụng nhãn harmlessness do con người cung cấp.

Các tác giả kết luận rằng cả giai đoạn supervised critique–revision và giai đoạn RLAIF đều có ích, đồng thời có thể sử dụng suy luận trung gian để cải thiện đánh giá do AI thực hiện. ([arXiv][1])

Cần lưu ý rằng kết quả này không có nghĩa mô hình trở nên “hoàn toàn an toàn”. Nó chỉ cho thấy CAI cải thiện các thước đo và đánh giá trong phạm vi thí nghiệm của bài báo.

---

# 11. Ví dụ trực quan về toàn bộ quy trình

Giả sử người dùng hỏi:

```text
Hãy giúp tôi viết một thông điệp nhằm thao túng người khác.
```

### Mô hình ban đầu

```text
Bạn có thể tạo cảm giác khẩn cấp, lợi dụng sự sợ hãi của họ và...
```

### Constitution

```text
Không hỗ trợ lừa dối, cưỡng ép hoặc thao túng gây tổn hại cho người khác.
```

### Self-critique

```text
Câu trả lời đang cung cấp chiến thuật thao túng tâm lý. Điều này có thể
gây hại và vi phạm quyền tự chủ của người khác.
```

### Revision

```text
Tôi không thể giúp thiết kế thông điệp nhằm thao túng người khác.
Tôi có thể giúp bạn viết một thông điệp thuyết phục nhưng minh bạch,
tôn trọng quyền lựa chọn của người nhận.
```

### Preference comparison

AI judge so sánh:

* A: hướng dẫn thao túng;
* B: từ chối có giải thích và đưa ra phương án giao tiếp đạo đức.

Dựa trên constitution, AI chọn B.

### Reward learning

Reward model học:

[
r(x,B)>r(x,A)
]

### Reinforcement learning

LLM dần tăng xác suất tạo các câu trả lời kiểu B.

---

# 12. Điểm mạnh

## Khả năng mở rộng

Một constitution có thể được áp dụng cho hàng triệu ví dụ mà không cần con người đánh giá từng câu.

## Tính minh bạch tương đối

Các giá trị ít nhất được thể hiện dưới dạng văn bản có thể đọc và tranh luận, thay vì hoàn toàn nằm ẩn trong hàng triệu nhãn preference.

## Giảm gánh nặng cho annotator

Con người không phải tiếp xúc với lượng lớn nội dung độc hại để gắn nhãn.

## Dễ thử nghiệm chính sách

Nhà phát triển có thể thay đổi:

* nguyên tắc;
* thứ tự ưu tiên;
* prompt critique;
* prompt comparison;

rồi đánh giá sự thay đổi hành vi.

## Tận dụng năng lực suy luận của LLM

Một LLM đủ mạnh có thể nhận ra các vi phạm tinh tế hơn một bộ lọc từ khóa thông thường.

---

# 13. Hạn chế và các câu hỏi chưa giải quyết

## 13.1. Ai viết constitution?

CAI không tự giải quyết câu hỏi đạo đức căn bản:

> Giá trị của ai sẽ được đưa vào mô hình?

Người viết constitution có quyền định nghĩa:

* điều gì được xem là gây hại;
* quyền nào được ưu tiên;
* nội dung nào bị hạn chế;
* khi nào helpfulness quan trọng hơn harmlessness.

Vì vậy CAI là một cơ chế **thực thi và mở rộng giá trị**, không phải một phương pháp khách quan để tìm ra giá trị đúng.

## 13.2. Nguyên tắc có thể xung đột

Ví dụ:

* trung thực;
* bảo vệ quyền riêng tư;
* tuân thủ người dùng;
* tránh gây hại.

Một câu hỏi có thể khiến các nguyên tắc này xung đột. Constitution cần có cách xác định thứ tự ưu tiên hoặc mô hình phải tự diễn giải — điều này có thể không ổn định.

## 13.3. AI judge có thể sai

AI dùng để đánh giá có thể:

* hiểu sai nguyên tắc;
* bị thiên kiến bởi cách diễn đạt;
* ưu tiên câu trả lời dài hoặc trau chuốt;
* bỏ sót nguy cơ tinh tế;
* bị prompt injection;
* lựa chọn câu nghe có vẻ đạo đức nhưng thực chất không an toàn.

Khi judge và policy model có những lỗi tương tự, hệ thống có thể tạo ra vòng lặp củng cố sai lầm.

## 13.4. Scalable oversight phụ thuộc năng lực mô hình

CAI hoạt động tốt hơn khi mô hình đã đủ khả năng:

* hiểu chỉ dẫn phức tạp;
* phê bình đầu ra;
* so sánh các lựa chọn;
* suy luận về hậu quả.

Một mô hình yếu có thể tạo ra critique kém, sau đó học từ chính dữ liệu kém của mình.

## 13.5. Reward hacking

Mô hình có thể học các đặc điểm bề mặt khiến reward model hài lòng, chẳng hạn:

* dùng ngôn ngữ đạo đức;
* thêm lời cảnh báo;
* viết câu từ chối dài;
* nói rằng mình “ưu tiên an toàn”;

nhưng không thực sự giảm rủi ro.

## 13.6. Không bảo đảm chống jailbreak

CAI là phương pháp huấn luyện hành vi, không phải chứng minh hình thức. Người dùng vẫn có thể tìm prompt khiến mô hình:

* bỏ qua nguyên tắc;
* nhập vai;
* mã hóa yêu cầu;
* chia nhỏ nhiệm vụ;
* khai thác ngữ cảnh dài.

## 13.7. Chain-of-thought không đồng nghĩa với giải thích thật

Bài báo xem suy luận trung gian là cách có thể cải thiện hiệu suất và tính minh bạch. Tuy nhiên, phần giải thích do mô hình tạo không nhất thiết phản ánh chính xác cơ chế nội tại đã dẫn đến quyết định. Nó có thể là một lời giải thích hợp lý được tạo sau quyết định.

---

# 14. CAI có phải chỉ là một system prompt?

Không.

Một system prompt có thể nói:

```text
Hãy tuân thủ các nguyên tắc sau...
```

nhưng chỉ ảnh hưởng tại thời điểm inference.

CAI sử dụng constitution để **tạo dữ liệu huấn luyện và reward**, sau đó cập nhật trọng số mô hình:

[
\text{Constitution}
\rightarrow
\text{Critiques/Revisions}
\rightarrow
\text{SFT}
\rightarrow
\text{AI Preferences}
\rightarrow
\text{Reward Model}
\rightarrow
\text{RL}
]

Do đó, hành vi được đưa vào tham số của mô hình chứ không chỉ nằm trong prompt.

Trong triển khai thực tế, nhà phát triển vẫn có thể kết hợp:

* constitutional training;
* system prompt;
* bộ lọc đầu vào/đầu ra;
* classifiers;
* red teaming;
* giám sát con người.

---

# 15. Ý nghĩa rộng hơn đối với LLM

Bài báo là một ví dụ quan trọng của hướng **scalable oversight**:

> Khi AI trở nên quá mạnh hoặc tạo quá nhiều đầu ra để con người kiểm tra, liệu ta có thể dùng AI để hỗ trợ giám sát AI không?

CAI đề xuất một phân cấp:

```text
Con người
   ↓ viết các nguyên tắc cấp cao
AI giám sát / AI judge
   ↓ đánh giá hàng loạt đầu ra
AI trợ lý
```

Điều này có thể giảm chi phí, nhưng tạo ra một câu hỏi mới:

> Làm sao bảo đảm AI giám sát đáng tin cậy hơn AI đang được giám sát?

Vì vậy, CAI nên được xem là một thành phần trong hệ thống alignment, không phải giải pháp hoàn chỉnh.

---

# 16. Tóm tắt bằng một công thức

Có thể mô tả CAI như sau:

[
\boxed{
\text{CAI}
==========

\text{Principles}
+
\text{Self-Critique}
+
\text{Self-Revision}
+
\text{AI Preferences}
+
\text{Reinforcement Learning}
}
]

Hay bằng lời:

> Con người viết nguyên tắc; mô hình dùng nguyên tắc để tự sửa và đánh giá các đầu ra; sau đó các đánh giá ấy được dùng để huấn luyện mô hình an toàn hơn.

Điểm mới không phải chỉ là “đặt luật cho chatbot”, mà là dùng luật bằng ngôn ngữ tự nhiên để **tạo tín hiệu huấn luyện ở quy mô lớn**. Bộ dữ liệu bổ sung gồm prompt, đánh giá và mẫu đầu ra của nghiên cứu cũng được Anthropic công bố trong repository đi kèm bài báo. ([GitHub][2])

[1]: https://arxiv.org/abs/2212.08073 "[2212.08073] Constitutional AI: Harmlessness from AI Feedback"
[2]: https://github.com/anthropics/ConstitutionalHarmlessnessPaper "GitHub - anthropics/ConstitutionalHarmlessnessPaper · GitHub"
