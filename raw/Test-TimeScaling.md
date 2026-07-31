Cụm “bài báo Test-Time Scaling” có thể chỉ nhiều công trình. Hai tài liệu thường được nhắc nhất là:

1. **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters** của Charlie Snell và cộng sự, 2024.
2. **s1: Simple Test-Time Scaling** của Muennighoff và cộng sự, 2025.

Dưới đây là phần giải thích tổng hợp, trọng tâm đặt vào bài của Snell vì đây là một trong những công trình nền tảng định hình khái niệm test-time scaling.

## 1. Test-Time Scaling là gì?

Trong cách phát triển LLM truyền thống, hiệu năng thường được cải thiện bằng cách tăng tài nguyên ở giai đoạn huấn luyện:

* nhiều tham số hơn;
* nhiều dữ liệu hơn;
* nhiều FLOPs huấn luyện hơn.

**Test-time scaling**, còn gọi là **inference-time scaling** hoặc **test-time compute**, chuyển một phần tài nguyên sang lúc mô hình đang trả lời.

Thay vì chỉ sinh một câu trả lời duy nhất, hệ thống có thể:

* cho mô hình “suy nghĩ” lâu hơn;
* sinh nhiều phương án;
* kiểm tra từng phương án;
* sửa lại các bước sai;
* tìm kiếm trên một cây lời giải;
* chọn phương án được verifier đánh giá cao nhất.

Có thể mô tả đơn giản:

[
\text{Câu trả lời cuối}
=======================

\operatorname{Select}
\left(
y_1,y_2,\ldots,y_N
\mid x
\right)
]

Trong đó (x) là câu hỏi, (y_i) là các lời giải được lấy mẫu, còn hàm `Select` có thể là majority voting, reward model, verifier hoặc một thuật toán tìm kiếm.

Ý tưởng trung tâm là:

> Một mô hình nhỏ nhưng được cấp thêm compute hợp lý ở lúc suy luận đôi khi có thể tốt hơn một mô hình lớn trả lời một lần.

## 2. Câu hỏi nghiên cứu của bài Snell et al.

Bài báo đặt ra câu hỏi:

> Với một ngân sách inference cố định, nên dùng số compute đó như thế nào để tăng xác suất giải đúng một bài toán khó?

Các tác giả không chỉ hỏi “sinh nhiều hơn có tốt hơn không”, mà hỏi sâu hơn:

* Nên sinh nhiều lời giải độc lập hay đào sâu một lời giải?
* Nên dùng search hay sampling?
* Có nên cấp cùng một lượng compute cho mọi câu hỏi?
* Khi nào mô hình nhỏ cộng thêm inference compute tốt hơn mô hình lớn?

Bài nghiên cứu hai nhóm cơ chế chính:

1. **Tìm kiếm với process-based verifier**
   Verifier đánh giá từng bước trung gian của lời giải, không chỉ đáp án cuối.

2. **Điều chỉnh phân phối sinh thích ứng theo câu hỏi**
   Hệ thống thay đổi cách lấy mẫu hoặc tìm kiếm dựa trên đặc điểm và độ khó của bài toán. ([arXiv][1])

## 3. Các chiến lược test-time scaling phổ biến

### Parallel scaling

Mô hình tạo nhiều lời giải độc lập:

[
y_i \sim p_\theta(y\mid x),\quad i=1,\ldots,N
]

Sau đó chọn bằng:

* **majority voting**: đáp án xuất hiện nhiều nhất;
* **best-of-(N)**: verifier chấm từng lời giải và chọn điểm cao nhất;
* **weighted voting**: mỗi đáp án được gán trọng số;
* **self-consistency**: nhiều chuỗi suy luận dẫn đến cùng đáp án được xem là bằng chứng mạnh hơn.

Ưu điểm:

* dễ triển khai song song;
* tận dụng tốt batching;
* hiệu quả khi mô hình có xác suất sinh đúng không quá thấp.

Nhược điểm:

* sinh nhiều lời giải gần giống nhau;
* lãng phí compute nếu verifier yếu;
* nếu xác suất thành công cơ sở gần bằng 0 thì lấy mẫu thêm thường không cứu được.

Với xác suất một lần sinh đúng là (p), xác suất có ít nhất một lời giải đúng trong (N) lần là:

[
P(\text{có lời giải đúng})=1-(1-p)^N
]

Nhưng hệ thống chỉ hưởng lợi từ xác suất này nếu có thể **nhận biết lời giải đúng**.

### Sequential scaling

Mô hình dành thêm token để tiếp tục suy luận trên cùng một trajectory:

* suy nghĩ lâu hơn;
* tự kiểm tra;
* quay lại bước trước;
* sửa lỗi;
* chia bài toán thành các bước nhỏ.

Các reasoning model thường thuộc nhóm này.

### Search-based scaling

Các trạng thái suy luận tạo thành cây:

* một node là trạng thái hoặc đoạn reasoning;
* các cạnh là bước suy luận tiếp theo;
* verifier chấm các node;
* beam search, best-first search hoặc MCTS quyết định nhánh cần mở rộng.

Đây là cách sử dụng compute tinh vi hơn sampling độc lập, nhưng phụ thuộc rất mạnh vào chất lượng verifier.

## 4. Kết quả quan trọng nhất của bài Snell

### Không có một chiến lược tốt nhất cho mọi bài toán

Hiệu quả của các phương pháp thay đổi theo **độ khó của prompt**.

* Bài dễ: ít compute đã đủ; search sâu có thể lãng phí.
* Bài trung bình: sampling thêm hoặc verifier-guided search có thể đem lại lợi ích lớn.
* Bài cực khó: nếu mô hình cơ sở gần như không thể tạo ra một hướng giải đúng, tăng sampling không giúp nhiều.

Do đó, test-time compute nên được phân bổ **thích ứng theo từng câu hỏi**, thay vì cấp một ngân sách cố định.

### Compute-optimal scaling

Các tác giả xây dựng một chiến lược chọn phương pháp và ngân sách dựa trên độ khó của bài. Cách phân bổ thích ứng này đạt hiệu quả compute tốt hơn hơn bốn lần so với best-of-(N) thuần túy trong thiết lập của họ. ([arXiv][1])

Hiểu trực giác:

* không dành 10.000 token cho câu hỏi đơn giản;
* không chỉ lấy vài mẫu cho câu hỏi khó;
* chọn chiến lược phù hợp với khả năng giải hiện tại của mô hình.

### Mô hình nhỏ có thể vượt mô hình lớn hơn nhiều

Trong đánh giá khớp theo FLOPs, một mô hình nhỏ được cấp inference compute thích hợp có thể vượt một mô hình lớn hơn 14 lần, với điều kiện mô hình nhỏ đã có xác suất thành công ban đầu ở mức không quá thấp. ([arXiv][1])

Điểm này không có nghĩa “mô hình nhỏ luôn tốt hơn mô hình lớn”. Nó có nghĩa:

[
\text{Model size} \times \text{Inference strategy}
]

mới là đơn vị cần tối ưu, thay vì chỉ so số tham số.

Một nghiên cứu inference scaling độc lập cũng cho thấy Llemma-7B kết hợp tree search có thể vượt Llemma-34B trên MATH trong các cấu hình được thử nghiệm. ([arXiv][2])

## 5. Bài s1 bổ sung điều gì?

Bài **s1: Simple Test-Time Scaling** tìm một công thức đơn giản hơn:

1. Fine-tune Qwen2.5-32B-Instruct trên chỉ 1.000 mẫu reasoning được chọn lọc.
2. Điều khiển thời lượng suy nghĩ bằng kỹ thuật **budget forcing**.

Ba tiêu chí chọn dữ liệu là:

* độ khó;
* tính đa dạng;
* chất lượng.

Các tác giả cho biết huấn luyện trên toàn bộ tập 59.000 mẫu không đem lại cải thiện đáng kể so với tập 1.000 mẫu được chọn kỹ; các chiến lược chọn ngẫu nhiên hoặc chỉ chọn reasoning dài cũng kém hơn rõ rệt. ([arXiv][3])

### Budget forcing hoạt động thế nào?

Khi muốn mô hình dừng sớm:

* ép sinh token kết thúc phần suy nghĩ.

Khi muốn mô hình suy nghĩ lâu hơn:

* chặn token kết thúc reasoning;
* chèn từ **“Wait”**;
* yêu cầu mô hình tiếp tục xem xét.

Việc này đôi khi khiến mô hình kiểm tra lại và sửa một bước suy luận sai. 

Trên AIME24, bài báo báo cáo hiệu năng tăng từ khoảng 50% lên 57% khi kéo dài reasoning bằng budget forcing. Biểu đồ cũng cho thấy sequential scaling của s1 tốt hơn majority voting của base model trong thiết lập GPQA được trình bày. 

## 6. Tại sao chỉ “suy nghĩ lâu hơn” không phải lúc nào cũng tốt?

Test-time scaling thường gặp hiện tượng **diminishing returns**:

[
\frac{\Delta \text{Accuracy}}{\Delta \text{Compute}}
\rightarrow 0
]

khi ngân sách tăng quá cao.

Nguyên nhân gồm:

* mô hình lặp lại cùng một suy luận;
* reasoning drift, càng nghĩ càng xa hướng đúng;
* self-correction sai: đổi đáp án đúng thành sai;
* các mẫu thiếu đa dạng;
* verifier chọn nhầm lời giải;
* giới hạn context window;
* mô hình không có kiến thức hoặc primitive cần thiết.

Ngay trong s1, các tác giả ghi nhận budget forcing cuối cùng cũng bị bão hòa và bị giới hạn bởi context window. ([arXiv][3])

Vì vậy, “more tokens” không đồng nghĩa với “more intelligence”. Compute phải tạo ra:

* exploration hữu ích;
* kiểm chứng đáng tin;
* hoặc sửa lỗi có định hướng.

## 7. Vai trò then chốt của verifier

Giả sử mô hình sinh được một lời giải đúng trong 100 mẫu, nhưng verifier chọn một lời giải sai. Khi đó phần compute dùng để sampling gần như bị lãng phí.

Verifier có thể là:

### Outcome Reward Model

Chấm toàn bộ lời giải hoặc đáp án cuối:

[
R_{\text{outcome}}(y)\in \mathbb{R}
]

Dễ huấn luyện hơn, nhưng khó xác định sai ở đâu.

### Process Reward Model

Chấm từng bước:

[
R_{\text{process}}(s_t,a_t)
]

Phù hợp với tree search và phát hiện sai lầm sớm, nhưng cần dữ liệu gán nhãn chi tiết và có thể bị reward hacking.

### Rule-based verifier

Dùng khi đáp án có thể kiểm tra tự động:

* chạy unit test cho code;
* kiểm tra biểu thức toán;
* thực thi SQL;
* đối chiếu constraint;
* dùng theorem prover.

Đây thường là bối cảnh thuận lợi nhất cho test-time scaling vì tín hiệu đúng/sai rõ ràng.

## 8. Khung phân loại hiện đại

Bài survey năm 2025 hệ thống hóa test-time scaling theo bốn câu hỏi: ([arXiv][4])

### What to scale?

Ta tăng cái gì?

* số token reasoning;
* số trajectory;
* độ rộng hoặc độ sâu search;
* số agent;
* số lần gọi tool;
* số vòng critique–revision.

### How to scale?

Tăng compute bằng cách nào?

* sampling;
* voting;
* reranking;
* search;
* reflection;
* debate;
* verifier-guided refinement;
* tool-assisted reasoning.

### Where to scale?

Compute được bổ sung ở đâu?

* bên trong một reasoning trajectory;
* giữa nhiều trajectory;
* ở bước lập kế hoạch;
* ở bước kiểm chứng;
* ở quá trình dùng tool;
* ở cấp agent hoặc multi-agent.

### How well to scale?

Đo hiệu quả bằng gì?

* accuracy;
* pass@(k);
* accuracy trên mỗi FLOP;
* chi phí trên mỗi câu đúng;
* latency;
* độ ổn định;
* độ tin cậy của verifier;
* đường Pareto chất lượng–chi phí.

## 9. Ý nghĩa thực tế khi xây dựng hệ thống LLM

Một kiến trúc inference hợp lý thường là:

```text
Câu hỏi
   ↓
Ước lượng độ khó / độ bất định
   ↓
Chọn ngân sách compute
   ↓
Sinh một hoặc nhiều trajectory
   ↓
Verifier / tool kiểm tra
   ↓
Refine hoặc search thêm nếu cần
   ↓
Trả lời cuối
```

Ví dụ policy:

* câu hỏi dễ: greedy hoặc một lần sinh;
* câu hỏi trung bình: 4–8 mẫu + voting;
* bài toán toán/code: nhiều mẫu + verifier;
* bài rất khó: tree search hoặc iterative refinement;
* dừng sớm khi confidence đủ cao.

Đây được gọi là **adaptive inference** hoặc **compute-optimal inference**.

## 10. Hạn chế của hướng nghiên cứu

Các kết quả mạnh nhất thường xuất hiện trên toán và lập trình, nơi đáp án có cấu trúc và dễ kiểm tra. Khả năng mở rộng sang:

* văn bản mở;
* tư vấn;
* phân tích xã hội;
* sáng tạo;
* factual QA không có nguồn kiểm chứng;

khó hơn đáng kể.

Ngoài ra:

* accuracy tăng nhưng latency cũng tăng;
* chi phí phục vụ có thể tăng gần tuyến tính với số mẫu;
* verifier có thể thiên lệch;
* benchmark contamination có thể làm kết quả trông tốt hơn;
* FLOPs-matched không phải lúc nào cũng phản ánh chi phí phần cứng thực;
* phương pháp tốt trên một model family chưa chắc chuyển sang family khác.

## Kết luận

Thông điệp quan trọng nhất của test-time scaling không phải là **“hãy để mô hình suy nghĩ càng lâu càng tốt”**, mà là:

> Hãy phân bổ inference compute một cách thích ứng, dùng đúng dạng search hoặc verification cho đúng độ khó của bài toán.

Ba kết luận cốt lõi:

1. **Inference compute là một trục scaling độc lập với số tham số.**
2. **Mô hình nhỏ cộng chiến lược inference tốt có thể cạnh tranh với mô hình lớn.**
3. **Verifier và cơ chế phân bổ compute quan trọng hơn việc đơn thuần tăng số token.**

[1]: https://arxiv.org/abs/2408.03314 "[2408.03314] Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"
[2]: https://arxiv.org/abs/2408.00724 "[2408.00724] Inference Scaling Laws: An Empirical Analysis of Compute-Optimal Inference for Problem-Solving with Language Models"
[3]: https://arxiv.org/pdf/2501.19393 "s1: Simple test-time scaling"
[4]: https://arxiv.org/abs/2503.24235 "[2503.24235] A Survey on Test-Time Scaling in Large Language Models: What, How, Where, and How Well?"
