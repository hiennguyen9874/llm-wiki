## 1. Bài báo là gì?

**Tree of Thoughts: Deliberate Problem Solving with Large Language Models** là bài báo của Shunyu Yao và cộng sự, công bố tại **NeurIPS 2023**.

Bài báo đề xuất **Tree of Thoughts — ToT**, một framework suy luận tại thời điểm inference, giúp LLM:

* tạo nhiều hướng giải khác nhau;
* đánh giá từng hướng;
* loại bỏ nhánh kém triển vọng;
* quay lui khi đi sai;
* tìm kiếm lời giải bằng BFS, DFS hoặc các thuật toán search khác.

Điểm quan trọng là ToT **không nhất thiết thay đổi hoặc huấn luyện lại trọng số mô hình**. Nó chủ yếu thay đổi cách gọi LLM và cách tổ chức quá trình suy luận. 

---

# 2. Vấn đề mà Tree of Thoughts muốn giải quyết

LLM tự hồi quy thông thường tạo token từ trái sang phải:

[
p(y)=\prod_{i=1}^{n}p(y_i\mid y_{<i})
]

Điều này khiến quá trình suy luận có tính “tham lam”:

1. mô hình chọn một bước;
2. tiếp tục dựa trên bước đó;
3. khi nhận ra bước ban đầu sai, việc sửa lại rất khó.

## So sánh với Chain of Thought

Trong **Chain of Thought — CoT**, mô hình sinh một chuỗi suy luận:

[
z_1 \rightarrow z_2 \rightarrow z_3 \rightarrow y
]

Ví dụ:

```text
Bước 1 → Bước 2 → Bước 3 → Đáp án
```

Vấn đề là chỉ có **một nhánh chính**. Một bước sai sớm có thể làm hỏng toàn bộ lời giải.

ToT thay chuỗi đó bằng một cây:

```text
                    Bài toán
                 /     |      \
             Ý A      Ý B      Ý C
            /  \       |       /  \
          A1   A2     B1     C1   C2
               |
             Đáp án
```

Nó cho phép mô hình giữ lại nhiều khả năng và so sánh chúng trước khi đi tiếp. Đây là sự khác biệt bản chất giữa **suy luận tuyến tính** và **tìm kiếm có chủ đích**. 

| Phương pháp          | Cấu trúc suy luận     | Có đánh giá trung gian? | Có quay lui? |
| -------------------- | --------------------- | ----------------------: | -----------: |
| Input–Output         | Không có bước rõ ràng |                   Không |        Không |
| Chain of Thought     | Một chuỗi             |            Thường không |        Không |
| Self-consistency CoT | Nhiều chuỗi độc lập   |    Chỉ chọn đáp án cuối |        Không |
| Tree of Thoughts     | Cây trạng thái        |                      Có |           Có |

---

# 3. “Thought” trong Tree of Thoughts là gì?

Một **thought** không nhất thiết là một token hay một câu. Nó là một đơn vị suy luận có ý nghĩa, với kích thước phụ thuộc bài toán.

Ví dụ:

* Trong Game of 24: một phép biến đổi số, chẳng hạn
  `10 - 4 = 6`.
* Trong viết sáng tạo: một kế hoạch cho đoạn văn.
* Trong ô chữ: một từ ứng viên cho một hàng hoặc cột.
* Trong lập trình: một chiến lược sửa lỗi hoặc một thay đổi kiến trúc.
* Trong lập kế hoạch: một hành động hoặc trạng thái trung gian.

Tác giả cho rằng thought cần:

* đủ nhỏ để có thể tạo nhiều phương án;
* đủ lớn để có thể đánh giá mức độ triển vọng.

Nếu thought quá nhỏ, chẳng hạn từng token, việc đánh giá gần như vô nghĩa. Nếu quá lớn, chẳng hạn cả bài giải, cây không còn lợi ích phân nhánh. 

---

# 4. Bốn thành phần chính của ToT

Bài báo mô tả một hệ thống ToT thông qua bốn quyết định thiết kế.

## 4.1. Thought decomposition — Chia bài toán thành các bước

Ta biểu diễn trạng thái ở độ sâu (i) là:

[
s_i = [x,z_1,z_2,\ldots,z_i]
]

Trong đó:

* (x): đề bài;
* (z_j): thought thứ (j);
* (s_i): toàn bộ trạng thái suy luận hiện tại.

Ví dụ với Game of 24:

```text
Input: 4, 5, 6, 10
```

Một trạng thái có thể là:

```text
10 - 4 = 6
Còn lại: 5, 6, 6
```

Thought tiếp theo có thể là:

```text
5 × 6 = 30
Còn lại: 6, 30
```

Và cuối cùng:

```text
30 - 6 = 24
```

---

## 4.2. Thought generator — Sinh các bước ứng viên

Từ một trạng thái (s), mô hình sinh ra (k) thought tiếp theo:

[
G(p_\theta,s)\rightarrow {z^{(1)},z^{(2)},\ldots,z^{(k)}}
]

Bài báo đưa ra hai cách chính.

### Cách A: Sample

Gọi LLM nhiều lần độc lập để lấy nhiều phương án.

```text
Trạng thái hiện tại
 ├── sample 1
 ├── sample 2
 ├── sample 3
 └── sample 4
```

Phù hợp khi không gian suy nghĩ rộng và mở, ví dụ viết sáng tạo.

### Cách B: Propose

Yêu cầu LLM đề xuất nhiều bước khác nhau trong cùng một lần gọi:

```text
Đưa ra 5 bước tiếp theo khả thi, không trùng nhau.
```

Phù hợp khi thought ngắn và có cấu trúc rõ ràng, như phép toán hoặc từ điền ô chữ.

Repository chính thức hỗ trợ cả hai chế độ `sample` và `propose`. ([GitHub][1])

---

## 4.3. State evaluator — Đánh giá trạng thái

Sau khi sinh các nhánh, hệ thống phải xác định nhánh nào đáng giữ lại.

[
V(p_\theta,S)\rightarrow \text{score hoặc ranking}
]

Bài báo dùng hai kiểu đánh giá.

### Value evaluation

Đánh giá từng trạng thái độc lập.

Ví dụ:

```text
Trạng thái: còn lại 6, 30
Khả năng đạt 24:
- sure
- maybe
- impossible
```

Trong Game of 24, tác giả dùng ba nhãn:

* `sure`
* `maybe`
* `impossible`

Mỗi trạng thái được đánh giá nhiều lần để giảm nhiễu.

### Vote evaluation

Đưa nhiều ứng viên vào cùng prompt và yêu cầu mô hình chọn phương án tốt nhất.

```text
Ứng viên 1: ...
Ứng viên 2: ...
Ứng viên 3: ...

Hãy phân tích và chọn ứng viên triển vọng nhất.
```

Cách này được dùng trong bài toán viết sáng tạo, nơi việc gán điểm tuyệt đối khó hơn so sánh tương đối. 

---

## 4.4. Search algorithm — Tìm kiếm trên cây

Sau khi có bộ sinh và bộ đánh giá, ToT dùng thuật toán search để khám phá cây.

### Breadth-First Search — BFS

Ở mỗi tầng:

1. mở rộng tất cả trạng thái hiện tại;
2. đánh giá các trạng thái mới;
3. giữ lại (b) trạng thái tốt nhất;
4. chuyển sang tầng tiếp theo.

Pseudo-code đơn giản:

```python
states = [initial_state]

for step in range(max_steps):
    candidates = []

    for state in states:
        candidates.extend(generate_thoughts(state))

    scores = evaluate(candidates)
    states = select_top_b(candidates, scores)

return best_final_state(states)
```

Tham số (b) tương tự **beam width**.

BFS phù hợp khi:

* số bước tương đối ngắn;
* cần giữ nhiều nhánh cạnh tranh;
* có thể đánh giá trạng thái ở từng tầng.

### Depth-First Search — DFS

DFS đi sâu vào một nhánh. Khi nhánh không còn triển vọng, nó quay lui:

```text
Đi tiếp → đi tiếp → thất bại
                    ↓
                backtrack
                    ↓
               thử nhánh khác
```

DFS phù hợp khi:

* lời giải có nhiều bước;
* cây rất rộng;
* có thể xác định sớm nhánh không khả thi.

Bài báo dùng BFS cho Game of 24 và Creative Writing, còn Mini Crosswords sử dụng DFS. 

---

# 5. Quy trình Tree of Thoughts tổng quát

Một vòng ToT có thể được mô tả như sau:

```text
1. Trạng thái hiện tại
        ↓
2. Sinh nhiều thought ứng viên
        ↓
3. Biến mỗi thought thành trạng thái mới
        ↓
4. Đánh giá hoặc bỏ phiếu
        ↓
5. Chọn các trạng thái tốt nhất
        ↓
6. Mở rộng tiếp hoặc quay lui
        ↓
7. Dừng khi có lời giải
```

Về hình thức:

[
S'*i =
\bigcup*{s\in S_{i-1}}
{s+z: z\in G(p_\theta,s)}
]

Sau đó chọn:

[
S_i=\operatorname{Select}_b
\left(S'*i,V(p*\theta,S'_i)\right)
]

Trong đó:

* (S_{i-1}): frontier hiện tại;
* (G): hàm sinh thought;
* (V): hàm đánh giá;
* (b): số trạng thái được giữ lại.

Nói cách khác, LLM đóng nhiều vai trò:

* **policy**: đề xuất hành động;
* **heuristic function**: ước lượng trạng thái;
* đôi khi là **judge**: so sánh các ứng viên.

Thuật toán tìm kiếm bên ngoài chịu trách nhiệm quản lý cây.

---

# 6. Ba thí nghiệm chính

## 6.1. Game of 24

### Bài toán

Cho bốn số, dùng mỗi số đúng một lần cùng các phép:

[
+,-,\times,\div
]

để tạo ra 24.

Ví dụ:

```text
4, 5, 6, 10
```

Lời giải:

[
5(10-4)-6=24
]

### Cấu hình ToT

* Mỗi thought là một phép toán trung gian.
* Cây có ba tầng.
* Sinh các phép toán tiếp theo.
* LLM đánh giá trạng thái là `sure`, `maybe` hoặc `impossible`.
* Dùng BFS.
* Giữ (b=5) trạng thái tốt nhất ở mỗi tầng.

### Kết quả

| Phương pháp                   | Tỉ lệ thành công |
| ----------------------------- | ---------------: |
| IO prompting                  |             7,3% |
| CoT                           |               4% |
| CoT self-consistency, 100 mẫu |               9% |
| IO + iterative refinement     |              27% |
| IO, oracle best-of-100        |              33% |
| CoT, oracle best-of-100       |              49% |
| ToT, (b=1)                    |              45% |
| **ToT, (b=5)**                |          **74%** |

Đây là kết quả nổi tiếng nhất của bài báo: ToT đạt 74%, so với 4% của CoT thông thường. Khoảng 60% chuỗi CoT thất bại ngay sau bước suy luận đầu tiên, cho thấy một lựa chọn sớm không tốt có thể phá hỏng toàn bộ chuỗi. 

Một điểm cần lưu ý: repository cho biết một lần tái chạy sau bài báo đạt **69% thay vì 74%**, do tính ngẫu nhiên của decoding. Vì vậy, 74% không nên được hiểu là một hằng số tuyệt đối cho mọi lần chạy. ([GitHub][1])

---

## 6.2. Creative Writing

### Bài toán

Đầu vào gồm bốn câu ngẫu nhiên. Mô hình phải viết bốn đoạn văn sao cho:

* mỗi đoạn kết thúc bằng một câu được cung cấp;
* toàn bộ bài vẫn mạch lạc và có tính liên kết.

### ToT thực hiện thế nào?

Tầng đầu tiên không viết bài ngay. Mô hình sinh nhiều **kế hoạch viết**:

```text
Plan 1: ...
Plan 2: ...
Plan 3: ...
Plan 4: ...
Plan 5: ...
```

Sau đó LLM bỏ phiếu chọn kế hoạch tốt nhất. Từ kế hoạch được chọn, mô hình sinh nhiều bài viết và lại bỏ phiếu.

Đây là ví dụ quan trọng vì nó cho thấy ToT không chỉ áp dụng cho bài toán có đáp án đúng–sai rõ ràng. Nó cũng có thể xử lý không gian mở bằng cách dùng **so sánh tương đối giữa các phương án**.

### Kết quả

Theo điểm mạch lạc do GPT-4 chấm:

* IO: khoảng **6,19**
* CoT: khoảng **6,93**
* ToT: khoảng **7,56**

Trong đánh giá mù của con người đối với CoT và ToT:

* ToT được ưu tiên trong 41 trường hợp;
* CoT được ưu tiên trong 21 trường hợp;
* 38 trường hợp được đánh giá tương đương.

Tuy nhiên, đánh giá này có hạn chế: một phần đánh giá tự động sử dụng chính GPT-4, và nghiên cứu người dùng được thực hiện bởi một nhóm tác giả chứ không phải một mẫu đánh giá độc lập lớn. 

---

## 6.3. Mini Crosswords

### Bài toán

Giải ô chữ (5\times5), gồm:

* năm gợi ý ngang;
* năm gợi ý dọc;
* các từ phải thỏa mãn ràng buộc giao nhau.

### Cấu hình ToT

* Mỗi thought là một từ ứng viên cho một gợi ý.
* Trạng thái chứa các từ đã điền và ràng buộc chữ cái.
* Dùng DFS.
* Khi độ tin cậy thấp hoặc xảy ra mâu thuẫn, hệ thống quay lui.
* Tối đa khoảng 5–10 bước suy luận.

### Kết quả

| Phương pháp | Đúng chữ cái | Đúng từ | Giải trọn game |
| ----------- | -----------: | ------: | -------------: |
| IO          |        38,7% |     14% |             0% |
| CoT         |        40,6% |   15,6% |             1% |
| **ToT**     |      **78%** | **60%** |        **20%** |

Các ablation trong bài báo cho thấy cả ba thành phần đều quan trọng:

* chọn trạng thái tốt;
* cắt tỉa nhánh;
* quay lui.

Khi loại bỏ pruning hoặc backtracking, kết quả giảm mạnh. 

---

# 7. Vì sao ToT hoạt động tốt hơn CoT?

## Giữ lại sự đa dạng

CoT cam kết vào một hướng rất sớm. ToT duy trì nhiều giả thuyết.

```text
CoT:   A → A1 → A2 → thất bại

ToT:   A → A1
       B → B1 → lời giải
       C → C1
```

## Có khả năng sửa sai

ToT không nhất thiết phải tiếp tục một nhánh đã chọn. Nó có thể:

* cắt nhánh;
* quay lại trạng thái trước;
* thử phương án khác.

## Phân bổ compute có định hướng

Self-consistency tạo nhiều chuỗi hoàn chỉnh độc lập. ToT dùng điểm đánh giá trung gian để dành compute cho các nhánh hứa hẹn hơn.

## Tận dụng LLM làm heuristic

Trong thuật toán A* hoặc game search cổ điển, heuristic thường do con người viết hoặc được học bằng mô hình riêng. Trong ToT, chính LLM diễn đạt bằng ngôn ngữ xem trạng thái nào có triển vọng.

Có thể hiểu ToT là một dạng **heuristic search**, trong đó LLM vừa tạo successor, vừa cung cấp heuristic. Chính các tác giả cũng liên hệ ToT với các thuật toán tìm kiếm cổ điển như A*. 

---

# 8. Tree of Thoughts không chỉ là một prompt

Một hiểu nhầm phổ biến là nghĩ rằng chỉ cần prompt:

```text
Hãy sử dụng Tree of Thoughts để giải bài toán.
```

là đã triển khai ToT đầy đủ.

Thực tế có hai mức.

## ToT trong một prompt

Yêu cầu mô hình:

1. tạo vài phương án;
2. đánh giá;
3. chọn phương án tốt;
4. giải tiếp.

Ví dụ:

```text
Hãy đề xuất 3 chiến lược.
Phân tích ưu nhược điểm của từng chiến lược.
Chọn chiến lược tốt nhất.
Sau đó đưa ra đáp án.
```

Đây là dạng mô phỏng ToT trong một lần gọi. Nó đơn giản nhưng:

* không có cây trạng thái thực;
* không có bộ nhớ search đáng tin cậy;
* backtracking chỉ được mô tả bằng văn bản;
* khó kiểm soát số node và ngân sách.

## ToT như một hệ thống

Implementation đúng tinh thần bài báo thường có một controller bên ngoài:

```python
while not done:
    thoughts = llm_generate(frontier)
    states = transition(frontier, thoughts)
    values = llm_evaluate(states)
    frontier = search_policy(states, values)
```

Controller quản lý:

* node ID;
* parent–child;
* frontier;
* trạng thái đã thăm;
* pruning;
* backtracking;
* điều kiện dừng;
* ngân sách token.

Đây mới là ToT dưới dạng thuật toán.

---

# 9. Ví dụ triển khai tối giản

```python
from dataclasses import dataclass
from typing import Callable


@dataclass
class Node:
    state: str
    score: float = 0.0
    depth: int = 0


def tree_of_thoughts(
    initial_state: str,
    generate: Callable[[str, int], list[str]],
    evaluate: Callable[[str], float],
    is_solution: Callable[[str], bool],
    beam_width: int = 5,
    branching_factor: int = 5,
    max_depth: int = 4,
) -> Node | None:
    frontier = [Node(initial_state)]

    for depth in range(max_depth):
        candidates: list[Node] = []

        for node in frontier:
            for thought in generate(node.state, branching_factor):
                new_state = f"{node.state}\n{thought}"
                new_node = Node(
                    state=new_state,
                    score=evaluate(new_state),
                    depth=depth + 1,
                )

                if is_solution(new_state):
                    return new_node

                candidates.append(new_node)

        if not candidates:
            return None

        candidates.sort(key=lambda node: node.score, reverse=True)
        frontier = candidates[:beam_width]

    return max(frontier, key=lambda node: node.score, default=None)
```

Trong hệ thống thật, nên thêm:

* kiểm tra ràng buộc bằng code thay vì chỉ nhờ LLM;
* cache prompt và kết quả;
* loại bỏ trạng thái trùng;
* giới hạn token và số lần gọi;
* đánh giá nhiều lần;
* log toàn bộ trajectory;
* cơ chế early stopping.

---

# 10. Chi phí tính toán

Nhược điểm lớn nhất của ToT là phải gọi mô hình nhiều lần.

Trong thí nghiệm Game of 24 của bài báo:

| Phương pháp     | Completion tokens | Chi phí mỗi bài thời điểm nghiên cứu | Thành công |
| --------------- | ----------------: | -----------------------------------: | ---------: |
| IO best-of-100  |              1,8k |                             0,13 USD |        33% |
| CoT best-of-100 |              6,7k |                             0,47 USD |        49% |
| ToT             |              5,5k |                             0,74 USD |        74% |

Trong Creative Writing, ToT dùng khoảng năm lần số token và chi phí so với IO hoặc CoT. Tác giả ước tính ToT có thể cần lượng token cao hơn CoT từ khoảng **5 đến 100 lần**, tùy bài toán và cấu hình search. Các mức giá trong bảng là giá API tại thời điểm thí nghiệm năm 2023, không phải giá hiện tại. 

Độ phức tạp thô, nếu mỗi node sinh (k) con trong (d) tầng, có thể tăng như:

[
O(k^d)
]

Trong thực tế, beam search giới hạn frontier ở (b), nên số node gần hơn với:

[
O(d\cdot b\cdot k)
]

nhưng mỗi node có thể cần nhiều lần gọi để sinh và đánh giá.

---

# 11. Hạn chế quan trọng

## LLM tự đánh giá không luôn đáng tin

Nếu cùng một mô hình vừa sinh vừa chấm, nó có thể:

* thiên vị cách diễn đạt của chính mình;
* chấm cao một lập luận nghe hợp lý nhưng sai;
* không phát hiện lỗi tính toán;
* tạo ra các điểm số thiếu hiệu chuẩn.

Vì thế, với bài toán có thể kiểm tra bằng chương trình, nên dùng verifier bên ngoài.

Ví dụ:

```text
LLM sinh phép toán
      ↓
Python kiểm tra phép toán có hợp lệ không
      ↓
LLM chỉ đánh giá chiến lược
```

## Search không sửa được kiến thức thiếu

Nếu LLM không biết thông tin cần thiết, mở thêm nhiều nhánh có thể chỉ tạo thêm nhiều phỏng đoán. Trong phụ lục, cải thiện trên StrategyQA khá nhỏ; tác giả cho rằng nút thắt nằm ở kiến thức bên ngoài hơn là suy luận. 

## Phụ thuộc mạnh vào thiết kế task

Ta phải quyết định:

* thought là gì;
* mỗi node sinh bao nhiêu nhánh;
* cách đánh giá;
* dùng BFS hay DFS;
* tiêu chí pruning;
* điều kiện dừng.

Không có một cấu hình ToT chung tối ưu cho mọi bài toán.

## Có thể tốn kém hơn giá trị mang lại

Với bài đơn giản mà CoT đã làm tốt, ToT thường không đáng dùng. Chính bài báo khuyến nghị áp dụng nó cho các nhiệm vụ cần lập kế hoạch hoặc tìm kiếm, nơi CoT gặp khó khăn. 

## Thực nghiệm ban đầu còn hẹp

Ba nhiệm vụ chính tương đối nhỏ và được thiết kế để nhấn mạnh khả năng search:

* Game of 24;
* Creative Writing;
* Mini Crosswords.

Do đó, không thể suy trực tiếp rằng ToT sẽ mang lại mức cải thiện tương tự trên mọi tác vụ thực tế.

---

# 12. Khi nào nên dùng ToT?

ToT phù hợp khi bài toán có những đặc điểm sau:

* có nhiều lựa chọn trung gian;
* quyết định ban đầu ảnh hưởng mạnh đến kết quả;
* có thể đánh giá một phần lời giải;
* cần lookahead hoặc backtracking;
* tồn tại ràng buộc kiểm tra được;
* chất lượng quan trọng hơn độ trễ.

Ví dụ:

* lập kế hoạch nhiều bước;
* giải puzzle;
* chứng minh hoặc suy luận toán học;
* thiết kế thuật toán;
* debug chương trình;
* lập kế hoạch tác nhân;
* viết nội dung có nhiều ràng buộc;
* phân tích nhiều giả thuyết.

Không nên mặc định dùng ToT cho:

* hỏi đáp kiến thức đơn giản;
* tóm tắt;
* dịch thuật;
* phân loại dễ;
* tác vụ yêu cầu latency thấp;
* bài toán chủ yếu thiếu dữ liệu hoặc kiến thức ngoài.

---

# 13. Đóng góp quan trọng nhất của bài báo

Giá trị lâu dài của Tree of Thoughts không chỉ nằm ở con số 74%. Đóng góp lớn hơn là cách nhìn:

> Suy luận bằng LLM có thể được tổ chức như một quá trình tìm kiếm trên không gian trạng thái, thay vì chỉ là sinh một chuỗi token duy nhất.

ToT đưa các ý tưởng AI cổ điển trở lại hệ thống LLM:

* state-space search;
* heuristic evaluation;
* breadth-first search;
* depth-first search;
* pruning;
* backtracking;
* planning.

LLM cung cấp khả năng biểu diễn và tạo các trạng thái bằng ngôn ngữ. Thuật toán search cung cấp cấu trúc và khả năng sửa sai.

Có thể tóm tắt:

[
\text{Tree of Thoughts}
=======================

\text{LLM generation}
+
\text{LLM/verifier evaluation}
+
\text{classical search}
]

Đây là lý do bài báo có ảnh hưởng lớn: nó chuyển trọng tâm từ **“prompt để mô hình nghĩ dài hơn”** sang **“xây dựng một quy trình suy luận có cấu trúc bên ngoài mô hình”**. Repository chính thức cung cấp mã, prompt và trajectory cho các thí nghiệm của bài báo. ([GitHub][1])

[1]: https://github.com/princeton-nlp/tree-of-thought-llm "GitHub - princeton-nlp/tree-of-thought-llm: [NeurIPS 2023] Tree of Thoughts: Deliberate Problem Solving with Large Language Models · GitHub"
