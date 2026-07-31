## ReAct là gì?

**ReAct** là viết tắt của **Reasoning + Acting**, được giới thiệu trong bài:

> **“ReAct: Synergizing Reasoning and Acting in Language Models”**
> Shunyu Yao và cộng sự — Princeton University và Google Research; công bố tại **ICLR 2023**. 

Ý tưởng trung tâm rất đơn giản nhưng có ảnh hưởng lớn:

> Thay vì để LLM chỉ **suy luận** rồi trả lời, hoặc chỉ **thực hiện hành động**, ReAct cho mô hình luân phiên giữa suy nghĩ, hành động và quan sát kết quả hành động.

Chu trình điển hình là:

```text
Thought → Action → Observation → Thought → Action → Observation → ... → Answer
```

Ví dụ:

```text
Question:
Nhà khoa học nào phát hiện penicillin, và ông sinh ở đâu?

Thought:
Tôi cần xác định người phát hiện penicillin.

Action:
Search["discoverer of penicillin"]

Observation:
Alexander Fleming discovered penicillin in 1928.

Thought:
Bây giờ cần tìm nơi sinh của Alexander Fleming.

Action:
Search["Alexander Fleming birthplace"]

Observation:
Alexander Fleming was born in Lochfield, Scotland.

Thought:
Tôi đã có đủ thông tin.

Final Answer:
Alexander Fleming; ông sinh tại Lochfield, Scotland.
```

Ở đây:

* **Thought** dùng để lập kế hoạch và quyết định bước tiếp theo.
* **Action** là lời gọi công cụ, chẳng hạn tìm kiếm, mở trang, lấy dữ liệu hoặc thao tác trong môi trường.
* **Observation** là thông tin môi trường trả lại.
* Mô hình dùng quan sát mới để cập nhật suy luận thay vì dựa hoàn toàn vào trí nhớ tham số.

---

## 1. Vấn đề mà ReAct muốn giải quyết

Trước ReAct, hai hướng chính thường được nghiên cứu tương đối tách biệt.

### Chain-of-Thought: suy luận nhưng không tương tác

Chain-of-Thought, hay CoT, yêu cầu mô hình tạo các bước suy luận trung gian:

```text
Question → Reasoning → Answer
```

Ưu điểm của CoT là giúp giải các bài toán nhiều bước. Tuy nhiên, suy luận diễn ra chủ yếu dựa trên kiến thức đã có trong mô hình. Mô hình không nhất thiết kiểm tra được một dữ kiện còn thiếu hoặc sửa một giả định sai bằng thông tin bên ngoài.

Do đó, một sai sót đầu chuỗi có thể tiếp tục lan truyền:

```text
Giả định sai
   ↓
Suy luận tiếp trên giả định sai
   ↓
Kết luận có vẻ hợp lý nhưng không chính xác
```

Các tác giả gọi đây là vấn đề **hallucination** và **error propagation** của suy luận chỉ dựa trên kiến thức nội tại. 

### Acting-only: tương tác nhưng thiếu suy luận cấp cao

Một agent “chỉ hành động” có thể gọi công cụ hoặc điều khiển môi trường:

```text
Observation → Action → Observation → Action
```

Nhưng nếu không có bước suy luận rõ ràng, agent có thể:

* không phân rã được mục tiêu;
* lặp lại hành động không hiệu quả;
* không nhớ tiến độ;
* không tổng hợp được các quan sát;
* không biết lúc nào cần đổi chiến lược.

Hình 1 của bài báo minh họa một agent trong ALFWorld cứ cố lấy một vật ở nơi không có vật đó, trong khi ReAct ghi nhận thất bại, cập nhật kế hoạch và chuyển sang vị trí khác. 

---

## 2. Trực giác cốt lõi

ReAct tạo ra hai chiều hỗ trợ lẫn nhau.

### Reason to act — suy luận để hành động

Suy luận giúp agent:

* phân rã nhiệm vụ thành các mục tiêu nhỏ;
* chọn công cụ phù hợp;
* quyết định truy vấn gì;
* theo dõi những gì đã hoàn thành;
* phát hiện ngoại lệ;
* điều chỉnh kế hoạch.

Ví dụ:

```text
Thought:
Kết quả tìm kiếm đầu tiên nói về phim chứ không phải cuốn sách.
Tôi nên thêm tên tác giả vào truy vấn.
```

### Act to reason — hành động để suy luận

Hành động cung cấp dữ liệu mới để mô hình suy luận tốt hơn:

* tìm kiếm kiến thức;
* đọc một trang web;
* truy vấn cơ sở dữ liệu;
* thực thi mã;
* quan sát trạng thái trò chơi;
* kiểm tra một giả thuyết.

```text
Action:
Search["tên sách" + "tác giả"]

Observation:
Thông tin chính xác hơn được trả về.

Thought:
Quan sát này bác bỏ giả định trước đó...
```

Bài báo mô tả ReAct như việc để mô hình **tạo và cập nhật kế hoạch bằng suy luận**, đồng thời **tương tác với môi trường để bổ sung thông tin cho suy luận**. 

---

## 3. Mô hình hóa chính thức

Giả sử tại bước (t), agent nhận quan sát (o_t) và chọn hành động (a_t) dựa trên toàn bộ ngữ cảnh trước đó:

[
c_t = (o_1,a_1,o_2,a_2,\ldots,o_t)
]

Một agent thông thường học chính sách:

[
\pi(a_t \mid c_t)
]

ReAct mở rộng không gian hành động từ các hành động môi trường (A) thành:

[
\hat{A} = A \cup L
]

Trong đó:

* (A): hành động tác động lên môi trường;
* (L): các chuỗi ngôn ngữ dùng làm “thought” hoặc reasoning trace.

Nếu agent tạo một thought:

[
\hat{a}_t \in L
]

thì môi trường không thay đổi. Thought chỉ được thêm vào ngữ cảnh để hỗ trợ những quyết định tiếp theo:

[
c_{t+1} = (c_t,\hat{a}_t)
]

Điểm quan trọng là **reasoning cũng được xem như một loại hành động nội bộ**, còn tool call là hành động bên ngoài. 

---

## 4. ReAct được huấn luyện như thế nào?

Trong thiết lập chính của bài báo, ReAct **không yêu cầu huấn luyện lại mô hình từ đầu**.

Các tác giả dùng một LLM đóng băng, chủ yếu là **PaLM-540B**, rồi cung cấp một số ít ví dụ trong prompt. Mỗi ví dụ là một trajectory do con người viết, gồm:

```text
Question / Task
Thought
Action
Observation
Thought
Action
Observation
...
Answer
```

Đây là **few-shot in-context prompting**.

Số lượng ví dụ khá nhỏ:

* khoảng 1–6 trajectory tùy tác vụ;
* ALFWorld dùng các trajectory có suy luận thưa;
* WebShop có thể dùng chỉ một ví dụ ReAct.

Bài báo cũng thử nghiệm ban đầu với fine-tuning, nhưng đóng góp chính là **prompting paradigm**, không phải kiến trúc neural mới. 

---

## 5. Khi nào Thought xuất hiện?

ReAct không nhất thiết ép agent phải suy nghĩ trước mọi hành động.

### Tác vụ hỏi đáp, kiểm chứng

Thought và action thường xen kẽ đều đặn:

```text
Thought 1
Action 1
Observation 1
Thought 2
Action 2
Observation 2
...
```

Điều này phù hợp vì mỗi lần truy xuất thông tin thường thay đổi hướng suy luận.

### Tác vụ điều khiển dài

Trong ALFWorld hoặc WebShop, một trajectory có thể có nhiều thao tác đơn giản. Việc sinh thought ở mọi bước vừa tốn token vừa không cần thiết.

Do đó, tác giả dùng **sparse reasoning**:

```text
Thought: Lập kế hoạch
Action
Action
Action
Thought: Kiểm tra tiến độ và đổi mục tiêu
Action
Action
...
```

Mô hình tự quyết định khi nào cần suy nghĩ và khi nào chỉ cần tiếp tục hành động. 

---

## 6. Các benchmark trong bài

Bài báo đánh giá trên bốn nhóm nhiệm vụ.

| Benchmark | Loại nhiệm vụ                                     | Môi trường/công cụ       |
| --------- | ------------------------------------------------- | ------------------------ |
| HotpotQA  | Hỏi đáp nhiều bước                                | Wikipedia API            |
| FEVER     | Kiểm chứng phát biểu                              | Wikipedia API            |
| ALFWorld  | Điều khiển trong môi trường gia đình dạng văn bản | Text-game environment    |
| WebShop   | Tìm và mua sản phẩm theo yêu cầu                  | Website mua sắm mô phỏng |

Các nhiệm vụ được chọn để kiểm tra cả hai phía:

* **reasoning-intensive:** HotpotQA, FEVER;
* **action-intensive:** ALFWorld, WebShop. 

---

## 7. Kết quả trên HotpotQA và FEVER

Các baseline gồm:

* **Standard:** trả lời trực tiếp;
* **CoT:** chỉ suy luận;
* **CoT-SC:** Chain-of-Thought với self-consistency;
* **Act:** chỉ hành động/truy xuất;
* **ReAct:** suy luận và hành động xen kẽ;
* các biến thể kết hợp ReAct với CoT-SC.

Kết quả PaLM-540B trong bài:

| Phương pháp    | HotpotQA EM | FEVER Accuracy |
| -------------- | ----------: | -------------: |
| Standard       |        28.7 |           57.1 |
| CoT            |        29.4 |           56.3 |
| CoT-SC         |        33.4 |           60.4 |
| Act            |        25.7 |           58.9 |
| ReAct          |        27.4 |           60.9 |
| CoT-SC → ReAct |        34.2 |       **64.6** |
| ReAct → CoT-SC |    **35.1** |           62.0 |



Một điểm dễ bị hiểu sai là **ReAct thuần không thắng CoT trên mọi chỉ số**. Trên HotpotQA, ReAct đạt 27.4 EM, thấp hơn CoT và CoT-SC.

Giá trị chính ở đây là tính bổ sung:

* CoT sử dụng tốt kiến thức nội tại và cấu trúc suy luận;
* ReAct có thể kiểm tra dữ kiện qua nguồn ngoài;
* phương án kết hợp hai cơ chế đạt kết quả tốt nhất.

Các tác giả đề xuất hai chiến lược chuyển đổi:

1. **ReAct → CoT-SC:** nếu ReAct không tìm được câu trả lời trong số bước giới hạn, chuyển sang CoT-SC.
2. **CoT-SC → ReAct:** nếu các mẫu CoT không đạt đồng thuận, chuyển sang truy xuất bằng ReAct.

Điều này thể hiện một insight quan trọng: **không phải câu hỏi nào cũng cần tool**, nhưng khi kiến thức nội tại không đáng tin, agent nên biết chuyển sang tương tác bên ngoài.

---

## 8. Kết quả trên ALFWorld

ALFWorld là môi trường gia đình dạng văn bản. Ví dụ nhiệm vụ:

```text
Đặt bình xịt tiêu vào ngăn kéo.
```

Agent phải:

* tìm đồ vật;
* di chuyển giữa các địa điểm;
* mở vật chứa;
* lấy vật;
* xác định ngăn kéo phù hợp;
* đặt vật vào đó.

Kết quả tổng thể:

| Phương pháp                     | Success rate |
| ------------------------------- | -----------: |
| Act — tốt nhất trong 6 prompt   |          45% |
| ReAct — trung bình              |          57% |
| ReAct — tốt nhất trong 6 prompt |      **71%** |
| ReAct-IM — tốt nhất             |          53% |
| BUTLER — tốt nhất               |          37% |

ReAct tốt nhất đạt 71%, cao hơn Act tốt nhất 26 điểm phần trăm và cao hơn BUTLER 34 điểm phần trăm. Ngay cả prompt ReAct kém nhất trong các thử nghiệm cũng đạt 48%, cao hơn hai baseline tốt nhất được so sánh. 

Lý do quan sát được:

* Act-only thường không phân rã mục tiêu;
* quên trạng thái hiện tại;
* lặp lại hành động;
* không nhận ra một subgoal đã hoàn thành;
* không biết chuyển sang subgoal tiếp theo.

Thought của ReAct hoạt động gần giống một **working memory bằng ngôn ngữ**:

```text
Tôi đã tìm thấy vật cần lấy.
Bước tiếp theo là tìm ngăn kéo, không cần tiếp tục tìm vật nữa.
```

---

## 9. Kết quả trên WebShop

WebShop yêu cầu agent mua sản phẩm thỏa các ràng buộc tự nhiên, chẳng hạn:

```text
Tìm một ghế dài có khoang chứa đồ,
màu nâu, kích thước phù hợp,
giá dưới 140 USD.
```

Agent phải:

* tạo truy vấn tìm kiếm;
* đọc tiêu đề và mô tả;
* chọn sản phẩm;
* chọn tùy chọn như màu, kích thước;
* quyết định có mua hay không.

Kết quả:

| Phương pháp        |    Score | Success rate |
| ------------------ | -------: | -----------: |
| Act                |     62.3 |        30.1% |
| ReAct              | **66.6** |    **40.0%** |
| Imitation Learning |     59.9 |        29.1% |
| IL + RL            |     62.4 |        28.7% |
| Human expert       |     82.1 |        59.6% |



ReAct tăng success rate gần **10 điểm phần trăm tuyệt đối** so với Act. Tuy nhiên, khoảng cách với con người vẫn lớn.

Thought giúp kết nối quan sát web nhiều nhiễu với yêu cầu ban đầu:

```text
Sản phẩm này có màu xanh và đúng kích thước,
nhưng người dùng yêu cầu màu nâu.
Tôi không nên mua và cần quay lại kết quả tìm kiếm.
```

Nếu không có reasoning trace, agent dễ chọn sản phẩm chỉ khớp một phần yêu cầu.

---

## 10. So sánh ReAct với các phương pháp liên quan

### ReAct và Chain-of-Thought

| Chain-of-Thought                          | ReAct                                       |
| ----------------------------------------- | ------------------------------------------- |
| Suy luận nội bộ                           | Suy luận kết hợp công cụ                    |
| Thường tạo một chuỗi suy luận rồi trả lời | Lặp qua nhiều vòng suy nghĩ–hành động       |
| Có thể không được grounding               | Có observation từ môi trường                |
| Phù hợp bài toán đóng                     | Phù hợp bài toán cần dữ liệu hoặc tương tác |
| Không nhất thiết cập nhật kiến thức       | Có thể cập nhật kế hoạch sau mỗi quan sát   |

ReAct có thể xem là **CoT trong vòng lặp có môi trường**, nhưng không hoàn toàn đồng nhất: ReAct còn xác định giao thức hành động và cách đưa observation trở lại context.

### ReAct và RAG

RAG thường có luồng:

```text
Query → Retrieve documents → Generate answer
```

ReAct có luồng:

```text
Reason → quyết định cần tìm gì
→ Retrieve
→ đọc kết quả
→ quyết định có cần tìm tiếp hay dùng công cụ khác
→ Generate
```

Khác biệt lớn nhất:

* RAG cơ bản thường truy xuất một hoặc một vài lần theo pipeline cố định.
* ReAct cho phép **truy xuất thích ứng nhiều bước**.
* RAG là một kỹ thuật cung cấp ngữ cảnh; ReAct là một **chính sách điều phối suy luận và hành động**.
* Một ReAct agent hoàn toàn có thể dùng retriever/RAG như một trong các tool.

### ReAct và function calling

Function calling cung cấp cơ chế có cấu trúc để mô hình trả về:

```json
{
  "name": "search",
  "arguments": {
    "query": "..."
  }
}
```

ReAct trả lời câu hỏi khác:

> Agent nên gọi công cụ nào, vào lúc nào, dựa trên quan sát trước đó, và tiếp tục ra sao?

Vì vậy:

* function calling là **giao diện thực thi**;
* ReAct là **mẫu điều khiển vòng lặp agent**.

### ReAct và Plan-and-Execute

Plan-and-Execute thường lập kế hoạch đầy đủ trước:

```text
Plan toàn bộ → Execute từng bước
```

ReAct thiên về phản ứng:

```text
Lập kế hoạch cục bộ → hành động → quan sát → sửa kế hoạch
```

ReAct phù hợp khi môi trường không chắc chắn. Plan-and-Execute có thể hiệu quả hơn khi nhiệm vụ rõ ràng và kế hoạch ít thay đổi. Nhiều agent hiện đại kết hợp cả hai.

---

## 11. Vì sao ReAct có ảnh hưởng lớn?

ReAct không giới thiệu kiến trúc transformer mới hay hàm loss mới. Ảnh hưởng của nó đến từ việc đưa ra một abstraction đơn giản cho agent LLM:

```text
LLM = bộ điều khiển
Tools = các hành động
Tool outputs = observations
Prompt/context = trạng thái và bộ nhớ tạm thời
```

Mô hình này xuất hiện trong rất nhiều hệ thống agent:

* trợ lý tìm kiếm web;
* agent lập trình;
* agent phân tích dữ liệu;
* agent điều khiển trình duyệt;
* trợ lý kết nối API doanh nghiệp;
* agent nhiều bước trong các framework orchestration.

Nói cách khác, ReAct giúp chuyển quan niệm từ:

```text
LLM như một hàm sinh văn bản
```

sang:

```text
LLM như một policy ra quyết định trong một vòng lặp tương tác
```

---

## 12. Ưu điểm

### Grounding tốt hơn

Mô hình có thể kiểm tra kiến thức thay vì chỉ dựa vào trí nhớ. Điều này giúp giảm một số dạng hallucination, đặc biệt là lỗi dữ kiện có thể xác minh.

### Điều chỉnh kế hoạch động

Observation mới có thể làm thay đổi kế hoạch ngay giữa quá trình.

### Dễ diễn giải hơn acting-only

Ta có thể xem vì sao agent gọi một tool, vì sao bỏ một kết quả hoặc vì sao đổi chiến lược.

### Few-shot và không cần kiến trúc mới

Trong bài gốc, chỉ một số trajectory mẫu đã tạo được hành vi tương đối mạnh trên nhiều loại tác vụ.

### Dễ can thiệp

Con người có thể sửa một thought hoặc thay đổi prompt để điều hướng agent. Trang dự án minh họa khả năng sửa trajectory thất bại bằng việc chỉnh một vài reasoning step. ([react-lm.github.io][1])

---

## 13. Hạn chế

### Reasoning trace không bảo đảm trung thực

Một chuỗi thought hợp lý không chứng minh đó là cơ chế thực sự dẫn tới quyết định của mô hình. Nó có thể là lời giải thích hậu nghiệm hoặc chứa giả định sai.

Vì thế, **interpretability** ở đây chủ yếu là khả năng kiểm tra trajectory, không phải bằng chứng đầy đủ về tính faithful của suy luận nội bộ.

### Có thể rơi vào vòng lặp

Ví dụ:

```text
Search A → kết quả không đủ
Search A → kết quả không đủ
Search A → ...
```

Cần giới hạn bước, phát hiện lặp hoặc chiến lược phục hồi.

### Tốn token và độ trễ

Mỗi vòng đều bổ sung:

* thought;
* action;
* observation;
* lịch sử trước đó.

Chi phí tăng nhanh với nhiệm vụ dài.

### Nhạy với prompt và ví dụ demonstration

Cách viết trajectory mẫu có thể ảnh hưởng đáng kể đến:

* tần suất suy nghĩ;
* lựa chọn công cụ;
* độ dài kế hoạch;
* hành vi khi thất bại.

### Context window hữu hạn

Các tác giả thừa nhận rằng tác vụ có không gian hành động lớn cần nhiều demonstration, nhưng demonstration dài có thể vượt giới hạn context của in-context learning. 

### Công cụ sai thì agent vẫn sai

ReAct không tự động bảo đảm độ chính xác. Search API có thể trả nguồn yếu; parser có thể lỗi; API có thể trả dữ liệu cũ; agent có thể diễn giải sai observation.

### Rủi ro hành động

Một hallucination trong câu trả lời chỉ tạo văn bản sai. Một hallucination trong agent có quyền gửi email, xóa dữ liệu hoặc mua hàng có thể tạo hậu quả thật.

Do đó, hệ thống production cần:

* permission boundaries;
* xác nhận trước hành động rủi ro;
* schema validation;
* logging;
* sandbox;
* giới hạn số bước và ngân sách;
* kiểm tra kết quả thực thi.

---

## 14. Một phiên bản ReAct tối giản

Pseudo-code:

```python
history = [user_request]

for step in range(max_steps):
    response = llm.generate(
        system_prompt=react_prompt,
        messages=history,
        tools=available_tools,
    )

    if response.final_answer:
        return response.final_answer

    if response.tool_call:
        observation = execute_tool_safely(response.tool_call)

        history.append({
            "role": "assistant",
            "content": response.tool_call
        })
        history.append({
            "role": "tool",
            "content": observation
        })

raise RuntimeError("Agent exceeded maximum number of steps")
```

Trong triển khai hiện đại, `Thought` thường không cần được hiển thị trực tiếp cho người dùng. Hệ thống có thể giữ một trạng thái kế hoạch ngắn gọn hoặc chỉ yêu cầu mô hình phát ra tool call có cấu trúc.

Một dạng prompt khái niệm:

```text
Bạn có thể sử dụng các công cụ được cung cấp.

Ở mỗi bước:
1. Xác định thông tin còn thiếu hoặc hành động cần thực hiện.
2. Chọn đúng một công cụ khi cần.
3. Dựa vào kết quả công cụ để cập nhật kế hoạch.
4. Không lặp lại một hành động không tạo thêm thông tin.
5. Khi đã đủ bằng chứng, trả lời và nêu nguồn.
```

---

## 15. Bài học quan trọng nhất

Đóng góp lớn nhất của ReAct không phải là cú pháp `Thought/Action/Observation`, mà là nguyên lý:

> **Suy luận của agent phải được đặt trong một vòng phản hồi với thế giới bên ngoài.**

Suy luận không có hành động dễ trở thành phỏng đoán không được kiểm chứng. Hành động không có suy luận dễ trở thành chuỗi thao tác thiếu mục tiêu. ReAct kết hợp hai mặt đó thành một quy trình:

[
\text{Reason} \rightarrow \text{Act} \rightarrow
\text{Observe} \rightarrow \text{Revise}
]

Đây là một trong những nền tảng khái niệm quan trọng của LLM agent hiện đại.

### Kết luận đánh giá

ReAct là một bài báo có ý tưởng **đơn giản, tổng quát và có tính hệ thống cao**. Kết quả thực nghiệm không chứng minh ReAct luôn vượt mọi phương pháp reasoning-only; thực tế trên HotpotQA, biến thể ReAct thuần còn thấp hơn CoT-SC. Điểm thuyết phục nhất của bài là:

* reasoning giúp agent hành động có mục tiêu;
* external observation giúp reasoning được grounding;
* kết hợp ReAct với phương pháp dùng kiến thức nội tại có thể tốt hơn từng phương pháp riêng lẻ;
* reasoning trace làm trajectory dễ chẩn đoán hơn, dù không bảo đảm hoàn toàn faithful;
* mô hình few-shot này đã mở đường cho kiến trúc agent dùng tool phổ biến hiện nay. 

[1]: https://react-lm.github.io/ "ReAct: Synergizing Reasoning and Acting in Language Models"
