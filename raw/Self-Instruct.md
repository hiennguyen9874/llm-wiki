## Self-Instruct là gì?

**Self-Instruct: Aligning Language Models with Self-Generated Instructions** là bài báo của Yizhong Wang và cộng sự, công bố tại ACL 2023. Ý tưởng trung tâm là:

> Dùng chính mô hình ngôn ngữ để tạo ra phần lớn dữ liệu instruction–response, lọc dữ liệu đó, rồi fine-tune lại mô hình để nó làm theo chỉ dẫn tốt hơn.

Phương pháp này giảm đáng kể nhu cầu phải thuê con người viết hàng chục nghìn câu lệnh và đáp án. Trong thí nghiệm chính, nhóm tác giả bắt đầu với **175 tác vụ do con người viết**, mở rộng thành **52.445 instructions và 82.439 instances**, rồi dùng chúng để supervised fine-tuning GPT-3. 

---

## 1. Vấn đề mà bài báo muốn giải quyết

Một mô hình ngôn ngữ pretrained chỉ được huấn luyện để dự đoán token tiếp theo. Nó có thể sở hữu nhiều kiến thức nhưng chưa chắc hiểu rằng:

* Người dùng đang đưa ra một yêu cầu.
* Nó cần thực hiện đúng yêu cầu đó.
* Nó phải trả lời theo định dạng mong muốn.
* Nó nên dừng sau khi hoàn thành.

Các mô hình như FLAN, T0 hay InstructGPT cải thiện điều này bằng **instruction tuning**: fine-tune mô hình trên các cặp dữ liệu dạng:

[
(\text{instruction}, \text{input}) \rightarrow \text{output}
]

Vấn đề là dữ liệu instruction do con người tạo thường:

* Tốn thời gian và chi phí.
* Khó mở rộng lên hàng chục nghìn tác vụ.
* Thiên về những tác vụ NLP quen thuộc.
* Bị giới hạn bởi khả năng sáng tạo của người xây dựng dataset.

Self-Instruct đặt câu hỏi: **Liệu một mô hình đủ lớn có thể tự tạo dữ liệu để dạy chính nó làm theo instruction hay không?** ([ACL Anthology][1])

---

## 2. Cấu trúc một mẫu dữ liệu Self-Instruct

Mỗi tác vụ (t) gồm:

* Instruction (I_t): mô tả nhiệm vụ.
* Input (X_{t,i}): dữ liệu cụ thể, có thể rỗng.
* Output (Y_{t,i}): câu trả lời đúng hoặc mong muốn.

Mục tiêu huấn luyện là:

[
M(I_t, X_{t,i}) \approx Y_{t,i}
]

Ví dụ:

```text
Instruction:
Viết lại câu sau theo phong cách trang trọng.

Input:
Tôi không đồng ý với cách làm này.

Output:
Tôi không thể đồng tình với phương thức thực hiện này.
```

Một số instruction không cần input riêng:

```text
Instruction:
Viết một đoạn văn ngắn giải thích hiện tượng cầu vồng.

Input:
<rỗng>

Output:
Cầu vồng hình thành khi ánh sáng Mặt Trời...
```

Tác giả cố ý cho phép input rỗng vì ranh giới giữa “instruction” và “input” trong ngôn ngữ tự nhiên không phải lúc nào cũng rõ ràng. 

---

# 3. Pipeline của Self-Instruct

Pipeline có thể được tóm tắt như sau:

```text
175 seed tasks do con người viết
             ↓
Mô hình tạo instruction mới
             ↓
Xác định classification / non-classification
             ↓
Sinh input-output instances
             ↓
Lọc trùng, lỗi và dữ liệu kém chất lượng
             ↓
Thêm instruction hợp lệ vào task pool
             ↓
Lặp lại quá trình
             ↓
Supervised fine-tuning mô hình gốc
```

Bài báo chia quá trình tạo dữ liệu thành bốn bước chính. 

---

## Bước 1: Sinh instruction mới

Task pool ban đầu chứa **175 tác vụ**, mỗi tác vụ có một instruction và một instance do con người viết.

Ở mỗi lượt, hệ thống chọn ngẫu nhiên tám instruction làm few-shot examples:

* Sáu instruction từ tập seed do con người viết.
* Hai instruction do mô hình tạo ra ở các vòng trước.

Sau đó mô hình được yêu cầu tạo thêm các tác vụ mới khác với những ví dụ đã có.

Ví dụ prompt khái quát:

```text
Hãy tạo các tác vụ đa dạng mà một mô hình ngôn ngữ có thể thực hiện.

1. Viết một email từ chối lời mời một cách lịch sự.
2. Phân loại cảm xúc của một bài đánh giá.
3. Tạo một câu hỏi toán học cho học sinh lớp 5.
...
9.
```

Mô hình hoàn thành phần còn lại bằng các instruction mới. Việc đưa hai instruction tự sinh vào prompt giúp quá trình bootstrapping dần mở rộng ra ngoài tập seed ban đầu. 

---

## Bước 2: Xác định tác vụ phân loại

Tác giả chia instruction thành hai nhóm:

1. **Classification task**: đầu ra thuộc một tập nhãn nhỏ, hữu hạn.
2. **Non-classification task**: đầu ra tự do như viết văn, giải thích, tóm tắt hoặc sinh mã.

Ví dụ classification:

```text
Instruction:
Xác định đánh giá sau là tích cực hay tiêu cực.

Labels:
Positive, Negative
```

Ví dụ non-classification:

```text
Instruction:
Giải thích vì sao bầu trời có màu xanh.
```

Mô hình thực hiện bước phân loại này bằng few-shot prompting, với các ví dụ classification và non-classification lấy từ tập seed. Việc tách hai loại tác vụ là cần thiết vì chúng sử dụng hai chiến lược sinh instance khác nhau. 

---

## Bước 3: Sinh các instance

### Input-first cho tác vụ sinh tự do

Với non-classification task, mô hình sinh theo thứ tự:

[
\text{Instruction} \rightarrow \text{Input} \rightarrow \text{Output}
]

Ví dụ:

```text
Instruction:
Viết lại câu ở thể bị động.

Input:
The researcher conducted the experiment.

Output:
The experiment was conducted by the researcher.
```

Đây là cách tự nhiên nhất: tạo một input hợp lệ trước, sau đó giải quyết input đó.

### Output-first cho tác vụ phân loại

Khi thử input-first cho classification, tác giả nhận thấy mô hình có xu hướng tạo dữ liệu lệch nhãn.

Ví dụ với tác vụ kiểm tra lỗi ngữ pháp, mô hình có thể liên tục tạo ra những câu đúng ngữ pháp, khiến dataset thiếu lớp “có lỗi”.

Self-Instruct xử lý bằng chiến lược **output-first**:

1. Xác định tập nhãn.
2. Chọn hoặc sinh một nhãn.
3. Sinh input phù hợp với nhãn đó.

Ví dụ:

```text
Label: Negative

Input:
The food was cold and the service was extremely slow.
```

Cách làm này giúp kiểm soát phân phối nhãn và giảm hiện tượng model chỉ sinh những ví dụ “dễ” hoặc thuộc lớp phổ biến. 

---

## Bước 4: Lọc và hậu xử lý

Dữ liệu tự sinh chứa nhiều lỗi, trùng lặp và trường hợp không khả thi. Vì vậy, filtering là phần rất quan trọng.

### Lọc instruction tương tự

Một instruction mới chỉ được giữ nếu độ tương đồng **ROUGE-L nhỏ hơn 0,7** so với tất cả instruction đã có trong task pool.

Ý tưởng:

[
\max_{I_j \in \text{pool}}
\operatorname{ROUGE\text{-}L}(I_{\text{new}}, I_j) < 0.7
]

Điều này chủ yếu loại bỏ các câu chỉ diễn đạt lại cùng một tác vụ.

Ví dụ:

```text
Write a positive product review.
```

và

```text
Create a favorable review for a product.
```

có khả năng bị xem là quá tương tự.

### Lọc tác vụ không phù hợp

Các instruction chứa từ như:

* image
* picture
* graph

bị loại vì GPT-3 sử dụng trong nghiên cứu là mô hình văn bản, không thể xử lý trực tiếp hình ảnh hoặc biểu đồ.

### Lọc instance lỗi

Nhóm tác giả cũng loại:

* Các instance trùng hoàn toàn.
* Cùng input nhưng có output mâu thuẫn.
* Instruction quá ngắn hoặc quá dài.
* Output chỉ lặp lại input.
* Dữ liệu không đúng định dạng.
* Các generation bị cắt hoặc không hoàn chỉnh. 

---

# 4. Fine-tuning mô hình

Sau khi tạo dataset, nhóm tác giả fine-tune chính mô hình GPT-3 đã dùng để sinh dữ liệu.

Prompt huấn luyện là kết quả nối instruction với input:

[
P_{t,i} = \operatorname{format}(I_t, X_{t,i})
]

Mô hình được huấn luyện bằng supervised learning để tối đa hóa xác suất của output:

[
\mathcal{L}
===========

-\sum_{k=1}^{|Y|}
\log P_\theta(y_k \mid P, y_{<k})
]

Đây là **standard supervised fine-tuning**, không phải reinforcement learning.

Tác giả sử dụng nhiều template khác nhau để tránh việc mô hình phụ thuộc vào một định dạng duy nhất:

```text
Task: {instruction}
Input: {input}
Output:
```

hoặc:

```text
{instruction}

{input}
```

hoặc:

```text
Instruction:
{instruction}

{input}

Response:
```

Sự đa dạng định dạng giúp mô hình phản ứng tốt hơn khi người dùng đặt câu hỏi theo những cách khác nhau. 

---

# 5. Dataset được tạo ra

Sau filtering, Self-Instruct tạo được:

| Thành phần                        | Số lượng |
| --------------------------------- | -------: |
| Instructions                      |   52.445 |
| Classification instructions       |   11.584 |
| Non-classification instructions   |   40.861 |
| Tổng instances                    |   82.439 |
| Instances có input rỗng           |   35.878 |
| Độ dài instruction trung bình     |  15,9 từ |
| Độ dài input khác rỗng trung bình |  12,7 từ |
| Độ dài output trung bình          |  18,9 từ |

Như vậy, phần lớn dữ liệu là tác vụ sinh tự do thay vì chỉ là classification. Đây là khác biệt quan trọng so với nhiều benchmark NLP cũ vốn tập trung mạnh vào phân loại. 

---

# 6. Kết quả thực nghiệm

## Super-NaturalInstructions

Nhóm tác giả đánh giá zero-shot trên 119 tác vụ của Super-NaturalInstructions, mỗi tác vụ có 100 instances.

Kết quả ROUGE-L:

| Mô hình                       |  ROUGE-L |
| ----------------------------- | -------: |
| Vanilla GPT-3                 |      6,8 |
| T0 11B                        |     33,1 |
| GPT-3 + T0 training           |     37,9 |
| **GPT-3 Self-Instruct**       | **39,9** |
| InstructGPT-001               |     40,8 |
| GPT-3 + SuperNI training      |     49,5 |
| GPT-3 Self-Instruct + SuperNI |     51,6 |

Self-Instruct nâng GPT-3 từ **6,8 lên 39,9 ROUGE-L**, tức tăng **33,1 điểm tuyệt đối**. Kết quả 39,9 cũng khá gần InstructGPT-001 ở mức 40,8. 

Một điểm đáng chú ý khác là khi kết hợp Self-Instruct với dữ liệu SuperNI, kết quả tăng từ 49,5 lên 51,6. Điều này cho thấy dữ liệu tự sinh không chỉ thay thế dữ liệu con người mà còn có thể đóng vai trò bổ sung. 

---

## Đánh giá trên các tác vụ hướng người dùng

SuperNI chủ yếu gồm các tác vụ NLP nghiên cứu. Vì vậy, nhóm tác giả còn xây dựng một tập instruction mới gần với ứng dụng thực tế, thuộc các nhóm như:

* Viết email.
* Nội dung mạng xã hội.
* Công cụ năng suất.
* Giải trí.
* Lập trình.
* Viết và biên tập nội dung.

Trong human evaluation, GPT-3 Self-Instruct vượt các phiên bản GPT-3 được fine-tune bằng những dataset instruction công khai khác và chỉ còn khoảng cách tuyệt đối khoảng **5%** so với InstructGPT-001. ([ACL Anthology][1])

---

# 7. Vì sao Self-Instruct hoạt động?

Có thể hiểu cơ chế của nó qua ba ý.

## 7.1 Mô hình đã có năng lực tiềm ẩn

Pretraining đã giúp GPT-3 học:

* Cấu trúc của nhiều nhiệm vụ.
* Kiến thức ngôn ngữ và thế giới.
* Cách viết, phân loại, giải thích, dịch và sinh mã.

Tuy nhiên, mô hình chưa được tối ưu trực tiếp để ánh xạ:

[
\text{yêu cầu của người dùng} \rightarrow \text{câu trả lời phù hợp}
]

Self-Instruct không nhất thiết “dạy thêm toàn bộ kiến thức mới”. Nó chủ yếu biến những năng lực tiềm ẩn thành hành vi instruction-following ổn định.

## 7.2 Sinh dữ liệu và giải bài là hai mức khó khác nhau

Một mô hình có thể không làm theo instruction tốt trong zero-shot, nhưng khi được cung cấp few-shot prompt rõ ràng, nó vẫn có thể tạo ra:

* Một mô tả nhiệm vụ hợp lý.
* Một input phù hợp.
* Một output tương đối đúng.

Dữ liệu này sau đó được chuyển từ kiến thức trong ngữ cảnh sang trọng số thông qua fine-tuning.

## 7.3 Độ phủ tác vụ quan trọng hơn nhiều ví dụ cho một tác vụ

Instruction tuning hướng đến khả năng tổng quát hóa sang tác vụ chưa thấy. Vì thế, việc có:

```text
50.000 tác vụ × một vài ví dụ
```

có thể hữu ích hơn:

```text
100 tác vụ × hàng nghìn ví dụ
```

Self-Instruct tập trung mạnh vào mở rộng **độ đa dạng của instruction**, thay vì chỉ tăng số lượng instance trong từng nhiệm vụ.

---

# 8. Self-Instruct không phải “mô hình tự thông minh vô hạn”

Tên gọi “self” có thể gây hiểu nhầm. Phương pháp không chứng minh rằng mô hình có thể tự cải thiện vô hạn mà không cần tín hiệu bên ngoài.

Nó vẫn phụ thuộc vào:

* 175 seed tasks do con người viết.
* Prompt templates do con người thiết kế.
* Các quy tắc filtering thủ công.
* Năng lực có sẵn của pretrained model.
* Hạ tầng fine-tuning.
* Benchmark và đánh giá của con người.

Quan trọng hơn, mô hình chủ yếu học lại từ phân phối kiến thức và lỗi của chính nó. Nếu mô hình sinh câu trả lời sai nhưng hợp lý về hình thức, lỗi đó có thể được đưa ngược vào tập huấn luyện.

Do đó, Self-Instruct nên được hiểu là **synthetic-data bootstrapping**, không phải recursive self-improvement không giới hạn.

---

# 9. Hạn chế của bài báo

## Chất lượng dữ liệu không được đảm bảo

Heuristic filtering loại được dữ liệu lỗi rõ ràng nhưng khó phát hiện:

* Hallucination.
* Lỗi suy luận tinh vi.
* Thông tin sai nhưng nghe hợp lý.
* Code chạy sai.
* Thành kiến xã hội.
* Câu trả lời không an toàn.

ROUGE-L chỉ đo tương đồng bề mặt, không đo liệu hai instruction có thật sự cùng ý nghĩa hay không.

## Giới hạn bởi năng lực của teacher

Trong bản gốc, GPT-3 vừa là bộ sinh dữ liệu vừa là mô hình được fine-tune. Nó khó tự tạo ra các lời giải vượt xa năng lực hiện có của chính nó.

Self-Instruct có thể cải thiện **cách sử dụng năng lực**, nhưng không bảo đảm tạo ra năng lực suy luận mới ở mức cao hơn.

## Dễ khuếch đại bias

Nếu pretrained model thường tạo ra:

* Chủ đề phổ biến hơn chủ đề hiếm.
* Văn phong Mỹ hoặc phương Tây.
* Câu trả lời theo một hệ giá trị nhất định.
* Stereotype về giới, nghề nghiệp hay văn hóa.

Dataset tự sinh có thể phản ánh và củng cố các khuynh hướng đó.

## Filtering còn đơn giản

Các heuristic như ROUGE-L, độ dài và keyword filtering phù hợp với thí nghiệm ban đầu, nhưng chưa phải hệ thống kiểm định chất lượng mạnh.

Các pipeline hiện đại thường bổ sung:

* LLM-as-a-judge.
* Reward model.
* Kiểm tra bằng unit test.
* Execution feedback.
* Deduplication bằng embedding.
* Kiểm chứng dữ kiện.
* Chấm điểm độ khó và độ đa dạng.

## Chi phí sinh dữ liệu

“Gần như không cần annotation” không đồng nghĩa với miễn phí. Phương pháp vẫn cần nhiều inference call để:

* Sinh instruction.
* Phân loại task.
* Sinh instance.
* Sinh lại khi dữ liệu lỗi.
* Fine-tune mô hình.

---

# 10. Self-Instruct khác RLHF như thế nào?

| Self-Instruct                         | RLHF                                             |
| ------------------------------------- | ------------------------------------------------ |
| Sinh instruction và response tổng hợp | Thu thập đánh giá hoặc preference của con người  |
| Huấn luyện chủ yếu bằng SFT           | Thường gồm SFT, reward modeling và RL            |
| Tập trung vào instruction-following   | Tập trung vào preference và alignment            |
| Rẻ hơn về annotation                  | Tốn công đánh giá của con người                  |
| Khó đánh giá chất lượng tinh vi       | Có tín hiệu trực tiếp về câu trả lời nào tốt hơn |
| Có thể học lại lỗi của chính model    | Có khả năng sửa lỗi dựa trên preference          |

Self-Instruct chủ yếu trả lời câu hỏi:

> “Làm thế nào tạo nhiều dữ liệu instruction?”

RLHF chủ yếu trả lời:

> “Làm thế nào khiến câu trả lời phù hợp hơn với preference của con người?”

Hai phương pháp có thể được kết hợp, không loại trừ nhau.

---

# 11. Ảnh hưởng của Self-Instruct

Đóng góp lớn nhất của bài báo không chỉ nằm ở con số benchmark, mà ở việc phổ biến một “công thức” tạo dữ liệu instruction tổng hợp:

[
\text{Seed examples}
\rightarrow
\text{LLM generation}
\rightarrow
\text{quality filtering}
\rightarrow
\text{SFT}
]

Công thức này trở thành nền tảng cho nhiều hướng sau đó như:

* Alpaca-style instruction generation.
* Evol-Instruct: tăng dần độ phức tạp của instruction.
* WizardLM.
* Synthetic code instruction datasets.
* Domain-specific self-instruction.
* LLM-as-a-judge filtering.
* Self-rewarding và iterative alignment.

Nhiều hệ thống sau này dùng một mô hình mạnh làm **teacher** để sinh dữ liệu cho mô hình nhỏ hơn. Về mặt kỹ thuật, đó gần với knowledge distillation bằng dữ liệu tổng hợp; còn Self-Instruct bản gốc nhấn mạnh việc bootstrapping từ chính mô hình gốc.

---

## Tóm tắt cốt lõi

Self-Instruct chứng minh rằng một lượng nhỏ seed data có thể được khuếch đại thành một tập instruction lớn bằng chính mô hình ngôn ngữ:

[
175\ \text{seed tasks}
\rightarrow
52.445\ \text{instructions}
\rightarrow
82.439\ \text{instances}
\rightarrow
\text{SFT GPT-3}
]

Kết quả là GPT-3 tăng từ **6,8 lên 39,9 ROUGE-L** trên Super-NaturalInstructions và tiến gần InstructGPT-001. Thành công này cho thấy dữ liệu tổng hợp có thể dạy mô hình **biểu diễn và sử dụng tốt hơn các năng lực đã học trong pretraining**, nhưng chất lượng cuối cùng vẫn bị giới hạn bởi model generator, phương pháp lọc và mức độ giám sát của con người. 

[1]: https://aclanthology.org/2023.acl-long.754/ "Self-Instruct: Aligning Language Models with Self-Generated Instructions - ACL Anthology"
