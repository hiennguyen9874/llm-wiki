## 1. Bài báo là gì?

**“Chain-of-Thought Prompting Elicits Reasoning in Large Language Models”** là công trình của Jason Wei và cộng sự tại Google Research, công bố tại **NeurIPS 2022**. Bài báo đặt nền móng cho kỹ thuật **Chain-of-Thought prompting — CoT**, tức yêu cầu hoặc hướng dẫn mô hình tạo ra các bước suy luận trung gian trước khi đưa ra đáp án cuối cùng. ([arXiv][1])

Ý tưởng trung tâm có thể tóm tắt như sau:

> Thay vì chỉ cung cấp các ví dụ dạng “câu hỏi → đáp án”, hãy cung cấp ví dụ dạng “câu hỏi → các bước giải thích → đáp án”.

Ví dụ:

**Standard prompting**

```text
Q: Roger có 5 quả bóng. Anh ấy mua 2 hộp,
mỗi hộp có 3 quả. Tổng cộng có bao nhiêu quả?

A: 11
```

**Chain-of-Thought prompting**

```text
Q: Roger có 5 quả bóng. Anh ấy mua 2 hộp,
mỗi hộp có 3 quả. Tổng cộng có bao nhiêu quả?

A: Hai hộp chứa 2 × 3 = 6 quả.
Roger có 5 + 6 = 11 quả.
Đáp án là 11.
```

Trong bài báo, các ví dụ như vậy được đặt vào prompt theo cơ chế **few-shot in-context learning**. Mô hình không được fine-tune lại; nó học cách trình bày quá trình giải ngay từ các ví dụ nằm trong context. 

---

## 2. Vấn đề mà bài báo muốn giải quyết

Trước CoT, việc tăng số tham số của mô hình giúp cải thiện nhiều tác vụ NLP, nhưng kết quả trên các bài toán cần suy luận nhiều bước vẫn còn hạn chế. Standard few-shot prompting thường chỉ biểu diễn ánh xạ:

[
x \rightarrow y
]

Trong khi đó, một bài toán phức tạp thực chất cần chuỗi biến đổi:

[
x \rightarrow z_1 \rightarrow z_2 \rightarrow \cdots \rightarrow z_n \rightarrow y
]

Trong đó:

* (x): câu hỏi;
* (z_i): các bước suy luận trung gian;
* (y): đáp án cuối cùng.

CoT đưa các biến trung gian (z_i) ra dưới dạng ngôn ngữ tự nhiên. Theo tác giả, điều này cho phép mô hình phân rã một bài toán phức tạp thành các bước nhỏ và phân bổ thêm lượng tính toán bằng số token sinh ra. 

Một cách hiểu trực quan là:

* Standard prompting buộc mô hình “nhảy” trực tiếp đến đáp án.
* CoT tạo ra một **scratchpad bằng ngôn ngữ** để mô hình ghi lại các kết quả trung gian.

---

## 3. CoT prompting được triển khai như thế nào?

Prompt gồm một số ví dụ có cấu trúc:

```text
Câu hỏi 1
Lời giải từng bước
Đáp án cuối cùng

Câu hỏi 2
Lời giải từng bước
Đáp án cuối cùng

...

Câu hỏi mới
```

Mô hình tiếp tục mẫu đã quan sát và sinh:

```text
Các bước suy luận cho câu hỏi mới
Đáp án cuối cùng
```

Trong thí nghiệm nổi bật trên GSM8K, nhóm nghiên cứu chỉ dùng **8 ví dụ CoT** trong prompt cho PaLM 540B. Không có cập nhật trọng số hay huấn luyện thêm trên GSM8K. ([arXiv][1])

Điểm khác biệt quan trọng là CoT trong bài báo gốc là **few-shot CoT**. Nó không đơn giản chỉ là thêm câu “Hãy suy nghĩ từng bước”. Kỹ thuật zero-shot với câu lệnh kiểu “Let’s think step by step” được phổ biến bởi một công trình khác sau đó.

---

## 4. Các mô hình và nhóm bài toán được thử nghiệm

Các tác giả thực nghiệm trên ba họ mô hình:

* **LaMDA**
* **GPT-3**
* **PaLM**

với nhiều kích thước mô hình khác nhau. 

Ba nhóm năng lực chính được đánh giá:

### Suy luận số học

Các benchmark gồm:

* GSM8K
* SVAMP
* ASDiv
* AQuA
* MAWPS

Đây chủ yếu là các bài toán có lời văn, trong đó mô hình phải hiểu tình huống, xác định phép toán và thực hiện nhiều bước tính.

### Suy luận theo tri thức thông thường

Bài báo sử dụng một số benchmark hỏi đáp cần kết hợp ngôn ngữ và tri thức đời sống, chẳng hạn StrategyQA và CommonsenseQA.

### Suy luận ký hiệu

Hai tác vụ nhân tạo nổi bật là:

* **Last-letter concatenation:** ghép ký tự cuối của các từ hoặc tên.
* **Coin flip:** theo dõi trạng thái sấp/ngửa sau một chuỗi thao tác lật hoặc không lật đồng xu.

Các tác vụ ký hiệu còn được dùng để kiểm tra khả năng tổng quát hóa sang chuỗi dài hơn chuỗi đã xuất hiện trong các ví dụ. 

---

## 5. Kết quả quan trọng nhất

### Kết quả trên GSM8K

Với PaLM 540B:

* Standard prompting: khoảng **18%**
* Chain-of-Thought prompting: khoảng **57%**
* Kết quả tốt nhất trước đó: khoảng **55%**
* GPT-3 175B được fine-tune: khoảng **33%**

Như vậy, chỉ bằng prompt chứa 8 lời giải mẫu, PaLM 540B đã vượt kết quả tốt nhất trước đó trên GSM8K tại thời điểm công bố. 

### CoT hiệu quả hơn trên bài toán khó

Kết quả cho thấy mức cải thiện lớn nhất xuất hiện ở các bài toán:

* có nhiều bước;
* có ngữ nghĩa phức tạp;
* standard prompting vốn hoạt động kém.

Ngược lại, với bài toán chỉ cần một phép toán đơn giản, CoT thường cải thiện rất ít, đôi khi còn làm giảm hiệu suất. 

Lý do hợp lý là với bài toán quá đơn giản, việc sinh thêm nhiều bước:

* không cung cấp thêm thông tin cần thiết;
* tạo thêm cơ hội mắc lỗi;
* làm tăng độ dài và chi phí suy luận.

### Khả năng tổng quát hóa độ dài

Trong các tác vụ ký hiệu, mô hình được xem các ví dụ có số bước ngắn rồi được kiểm tra trên chuỗi dài hơn.

Standard prompting thường thất bại trong thiết lập ngoài phân phối này. CoT giúp các mô hình đủ lớn duy trì quy trình xử lý từng bước và tổng quát hóa tốt hơn sang chuỗi dài. 

---

## 6. Hiện tượng “năng lực nổi lên theo quy mô”

Một trong những phát hiện đáng chú ý nhất là CoT không mang lại lợi ích đồng đều cho mọi kích thước mô hình.

Trong thí nghiệm của bài báo:

* Các mô hình nhỏ thường tạo ra lời giải trôi chảy nhưng thiếu logic.
* Lợi ích rõ rệt bắt đầu xuất hiện ở các mô hình khoảng hàng trăm tỷ tham số.
* Đường hiệu suất của CoT tăng mạnh khi quy mô mô hình tăng, trong khi standard prompting có thể gần như đi ngang. 

Bài báo gọi đây là một **emergent ability**, tức năng lực dường như chỉ bộc lộ rõ sau khi mô hình đạt đến một quy mô nhất định.

Tuy nhiên, không nên hiểu con số khoảng 100B như một định luật phổ quát. Đó là quan sát trên các kiến trúc, dữ liệu huấn luyện và benchmark cụ thể của thời điểm 2022. Những mô hình nhỏ hơn hiện nay có thể suy luận tốt hơn nhờ dữ liệu chất lượng cao, instruction tuning, distillation và huấn luyện chuyên biệt.

---

## 7. Vì sao CoT có thể hoạt động?

Bài báo không chứng minh một cơ chế nhân quả duy nhất, nhưng đưa ra một số giải thích.

### Phân rã bài toán

CoT biến một ánh xạ phức tạp thành nhiều ánh xạ đơn giản hơn:

[
P(y\mid x)
]

trở thành:

[
P(z_1\mid x)
P(z_2\mid x,z_1)
\cdots
P(y\mid x,z_1,\ldots,z_n)
]

Mỗi bước chỉ cần giải quyết một phần nhỏ hơn của bài toán.

### Tạo thêm “compute” trong quá trình sinh

Transformer thực hiện thêm một lượt tính toán cho mỗi token được sinh ra. Khi mô hình viết ra các bước trung gian, nó có thêm nhiều vị trí để:

* lưu trạng thái tạm thời;
* suy ra kết quả phụ;
* tham chiếu lại thông tin trước đó;
* sửa hướng suy luận ở các bước tiếp theo.

Vì vậy, CoT có thể được xem như một hình thức **test-time computation bằng token**.

### Cung cấp cấu trúc giải quyết vấn đề

Các ví dụ CoT không chỉ cho mô hình biết đáp án mà còn cho biết loại thuật toán bằng ngôn ngữ cần mô phỏng:

* xác định đại lượng;
* thực hiện phép biến đổi;
* kiểm tra điều kiện;
* kết luận.

### Tách hiểu ngữ nghĩa khỏi tính toán

Trong bài toán có lời văn, mô hình phải đồng thời:

1. hiểu nội dung;
2. chuyển nội dung thành quan hệ toán học;
3. thực hiện phép tính.

CoT giúp trải ba quá trình này ra thành nhiều bước thay vì ép chúng xảy ra trong một lần dự đoán đáp án.

---

## 8. Các thí nghiệm ablation

Nhóm tác giả kiểm tra xem hiệu quả có đơn giản chỉ đến từ việc sinh thêm token hoặc viết ra phương trình hay không.

### Chỉ sinh phương trình

Mô hình được yêu cầu viết phương trình rồi đưa ra đáp án, nhưng không có phần giải thích ngôn ngữ tự nhiên.

Cách này có ích trên bài toán một hoặc hai bước, nhưng không cải thiện nhiều trên GSM8K. Tác giả cho rằng vấn đề khó không chỉ nằm ở phép tính mà còn ở việc diễn giải ngữ nghĩa của câu hỏi thành các quan hệ đúng. 

### Thêm lượng tính toán nhưng không có lập luận phù hợp

Các biến thể khiến mô hình sinh thêm nội dung nhưng không tạo chuỗi suy luận có cấu trúc cũng không đạt kết quả tương đương CoT.

Điều này cho thấy lợi ích không hoàn toàn đến từ việc “viết dài hơn”; nội dung và thứ tự của các bước vẫn quan trọng.

### Đặt phần giải thích sau đáp án

Khi mô hình đưa đáp án trước rồi mới giải thích, hiệu quả thấp hơn. Điều này hỗ trợ giả thuyết rằng các bước trung gian có ích vì chúng tham gia vào quá trình tạo đáp án, chứ không chỉ là lời giải thích hậu nghiệm. 

---

## 9. Phân tích lỗi

Khi kiểm tra thủ công các câu trả lời đúng của LaMDA 137B trên GSM8K, tác giả nhận thấy phần lớn chuỗi suy luận cũng đúng về logic và toán học, mặc dù có một số trường hợp mô hình tình cờ đi đến đáp án đúng từ lý luận sai.

Với các câu trả lời sai:

* khoảng một phần chứa quy trình gần đúng nhưng mắc lỗi nhỏ, như tính toán hoặc bỏ sót bước;
* phần còn lại mắc lỗi lớn về hiểu ngữ nghĩa hoặc tính nhất quán.

Việc tăng từ PaLM 62B lên 540B giúp khắc phục đáng kể cả lỗi thiếu bước lẫn lỗi hiểu ngữ nghĩa. 

Điểm này quan trọng vì nó gợi ý rằng CoT không chỉ cải thiện phép tính. Quy mô mô hình còn ảnh hưởng đến khả năng xây dựng đúng biểu diễn của bài toán.

---

## 10. Những đóng góp chính

Có thể cô đọng đóng góp của bài báo thành bốn điểm.

**Thứ nhất**, bài báo chứng minh rằng khả năng giải bài toán nhiều bước có thể được kích hoạt chỉ bằng prompting, không nhất thiết phải fine-tune mô hình.

**Thứ hai**, nó cho thấy định dạng đầu ra trong ví dụ few-shot có thể ảnh hưởng rất lớn đến năng lực biểu hiện của mô hình.

**Thứ ba**, công trình xác lập mối liên hệ thực nghiệm giữa CoT và quy mô mô hình.

**Thứ tư**, bài báo mở ra một dòng nghiên cứu lớn về tăng lượng tính toán lúc suy luận, gồm self-consistency, zero-shot CoT, least-to-most prompting, tree search, verifier và các mô hình reasoning chuyên biệt.

---

## 11. Các hạn chế quan trọng

### CoT không chứng minh mô hình “suy nghĩ như con người”

Tác giả nói rõ rằng việc mô hình tạo ra văn bản giống quá trình suy nghĩ không chứng minh mạng nơ-ron đang thực hiện cùng cơ chế nhận thức như con người. 

### Chuỗi suy luận không được bảo đảm là trung thực

Một mô hình có thể:

* đưa ra đáp án đúng nhưng giải thích sai;
* tạo lời giải nghe hợp lý nhưng chứa lỗi;
* quyết định đáp án trước rồi xây dựng lời giải thích phù hợp sau;
* sử dụng những tín hiệu nội bộ không xuất hiện trong phần giải thích.

Vì vậy, CoT là một **dấu vết suy luận được sinh ra**, không nhất thiết là bản ghi chính xác của toàn bộ tính toán nội bộ.

### Sai một bước có thể làm hỏng toàn bộ chuỗi

Do các bước sau phụ thuộc vào bước trước, lỗi sớm dễ lan truyền. CoT làm quá trình dễ kiểm tra hơn, nhưng không tự động bảo đảm tính đúng đắn.

### Tốn chi phí

CoT làm tăng số token đầu ra, kéo theo:

* độ trễ cao hơn;
* chi phí inference lớn hơn;
* context dài hơn;
* nguy cơ lan man.

### Phụ thuộc vào prompt

Bài báo ghi nhận sự chênh lệch đáng kể giữa các chuỗi ví dụ do những người chú giải khác nhau viết. Trong tác vụ coin-flip, một số bộ prompt đạt gần như tuyệt đối, trong khi bộ khác thấp hơn đáng kể dù vẫn tốt hơn baseline. 

---

## 12. Khi nào nên dùng CoT?

Theo kết quả và trực giác của tác giả, CoT hữu ích nhất khi:

1. Bài toán khó và thực sự cần nhiều bước.
2. Mô hình có đủ năng lực.
3. Standard prompting không cải thiện nhiều khi tăng quy mô.
4. Có thể thiết kế ví dụ suy luận rõ ràng và đúng.
5. Giá trị của độ chính xác cao hơn chi phí token bổ sung. 

CoT ít cần thiết hơn với:

* phân loại đơn giản;
* tra cứu trực tiếp;
* bài toán chỉ có một bước;
* tác vụ mà mô hình đã đạt gần mức trần;
* ứng dụng yêu cầu phản hồi cực nhanh và ngắn.

---

## 13. Ví dụ thực hành

Một few-shot CoT prompt có thể được viết như sau:

```text
Bạn hãy giải từng bước và kết thúc bằng dòng:
"Đáp án: <kết quả>".

Ví dụ 1:
Câu hỏi: Một cửa hàng có 15 chiếc bánh, bán 6 chiếc
và làm thêm 4 chiếc. Cửa hàng còn bao nhiêu chiếc?

Lời giải:
Sau khi bán 6 chiếc, cửa hàng còn 15 - 6 = 9 chiếc.
Làm thêm 4 chiếc nên có 9 + 4 = 13 chiếc.
Đáp án: 13

Ví dụ 2:
Câu hỏi: Mỗi hộp có 8 cây bút. Ba hộp có bao nhiêu cây?

Lời giải:
Có 3 hộp, mỗi hộp 8 cây nên tổng số bút là
3 × 8 = 24.
Đáp án: 24

Câu hỏi:
Lan có 20 viên bi. Lan cho bạn một phần tư số bi,
sau đó mua thêm 7 viên. Lan có bao nhiêu viên bi?
```

Chuỗi mong đợi:

```text
Một phần tư của 20 là 20 ÷ 4 = 5.
Lan còn 20 - 5 = 15 viên.
Sau khi mua thêm 7 viên, Lan có 15 + 7 = 22 viên.
Đáp án: 22
```

Trong hệ thống thực tế, nên kết hợp CoT với:

* định dạng đầu ra cố định;
* công cụ tính toán;
* kiểm tra đáp án;
* lấy nhiều lời giải rồi bỏ phiếu;
* giới hạn độ dài;
* tách phần giải thích cho người dùng khỏi quá trình tính toán nội bộ.

---

## 14. Kết luận

Thông điệp quan trọng nhất của bài báo không chỉ là “hãy bảo LLM giải từng bước”. Phát hiện sâu hơn là:

> Năng lực quan sát được của một LLM phụ thuộc mạnh vào cách ta cấu trúc quá trình tạo đầu ra, chứ không chỉ phụ thuộc vào kiến thức được lưu trong trọng số.

CoT biến ngôn ngữ thành một không gian làm việc trung gian. Nó cho phép mô hình dùng nhiều token hơn để biểu diễn trạng thái, phân rã bài toán và thực hiện các phép biến đổi tuần tự. Tuy vậy, một chuỗi giải thích hợp lý vẫn không đồng nghĩa với suy luận đúng hoặc trung thực; vì thế CoT nên được xem là một kỹ thuật tăng hiệu suất và khả năng kiểm tra, không phải bằng chứng tuyệt đối về tư duy của mô hình.

[1]: https://arxiv.org/abs/2201.11903?utm_source=chatgpt.com "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
