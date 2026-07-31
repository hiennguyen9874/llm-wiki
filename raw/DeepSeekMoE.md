# DeepSeekMoE: chuyên biệt hóa expert trong LLM

**DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models** là bài báo của nhóm DeepSeek-AI, công bố đầu năm 2024 và sau đó xuất hiện tại ACL 2024. Mục tiêu chính là cải thiện kiến trúc Mixture-of-Experts để mỗi expert học một nhóm kiến thức rõ ràng hơn, ít trùng lặp hơn, trong khi vẫn giữ chi phí tính toán trên mỗi token thấp. ([arXiv][1])

## 1. Vấn đề mà bài báo muốn giải quyết

Trong Transformer dense thông thường, mọi token đều đi qua toàn bộ FFN của từng layer:

[
h_t^l = \operatorname{FFN}(u_t^l)+u_t^l
]

Với MoE, FFN được thay bằng nhiều mạng FFN nhỏ gọi là **experts**. Router chỉ chọn một số expert cho mỗi token:

[
h_t^l =
\sum_{i=1}^{N} g_{i,t}\operatorname{FFN}_i(u_t^l)+u_t^l
]

Trong đó (g_{i,t}) chỉ khác 0 đối với các expert nằm trong top-(K).

Ưu điểm là mô hình có thể chứa rất nhiều tham số, nhưng mỗi token chỉ kích hoạt một phần nhỏ. Tuy nhiên, DeepSeek chỉ ra hai vấn đề của MoE truyền thống như GShard:

**Knowledge hybridity — kiến thức bị pha trộn.** Khi chỉ có 8 hoặc 16 expert lớn, mỗi expert phải xử lý rất nhiều loại token và lĩnh vực khác nhau. Một expert có thể đồng thời phải học ngữ pháp, toán, lập trình và kiến thức thế giới, nên khó chuyên biệt hóa.

**Knowledge redundancy — kiến thức bị trùng lặp.** Nhiều expert đều phải học các kiến thức phổ thông giống nhau, chẳng hạn cú pháp ngôn ngữ, cấu trúc câu hoặc các phép biến đổi cơ bản. Điều này lãng phí dung lượng tham số. 

DeepSeekMoE giải quyết hai vấn đề này bằng hai ý tưởng:

1. **Fine-grained expert segmentation**
2. **Shared expert isolation**

---

## 2. Fine-grained expert segmentation

### Ý tưởng

Thay vì dùng một số ít expert lớn, DeepSeek chia mỗi expert thành (m) expert nhỏ hơn.

Giả sử MoE truyền thống có:

* (N) expert;
* kích hoạt (K) expert cho mỗi token;
* mỗi expert có kích thước FFN là (d_{\text{ff}}).

DeepSeekMoE biến thành:

* (mN) expert;
* mỗi expert có kích thước khoảng (d_{\text{ff}}/m);
* kích hoạt (mK) expert cho mỗi token.

Như vậy:

* tổng số tham số expert gần như không đổi;
* lượng tính toán cho mỗi token gần như không đổi;
* nhưng router có nhiều cách phối hợp expert hơn.

[
h_t^l =
\sum_{i=1}^{mN}
g_{i,t}\operatorname{FFN}_i(u_t^l)+u_t^l
]

với router chọn top-(mK) trong tổng số (mN) expert. 

### Ví dụ trong bài báo

Với MoE thông thường:

* 16 expert;
* chọn 2 expert mỗi token.

Số tổ hợp có thể chọn là:

[
\binom{16}{2}=120
]

Nếu chia mỗi expert thành 4 expert nhỏ:

* tổng cộng 64 expert;
* chọn 8 expert mỗi token.

Số tổ hợp trở thành:

[
\binom{64}{8}=4{,}426{,}165{,}368
]

Điều này không có nghĩa mô hình sẽ sử dụng mọi tổ hợp, nhưng không gian routing trở nên linh hoạt hơn rất nhiều. Một token có thể lấy một phần kiến thức từ expert cú pháp, một phần từ expert toán, một phần từ expert lập trình, thay vì phải dựa vào hai expert lớn chứa hỗn hợp tất cả kiến thức đó. 

### Trực giác

Có thể hình dung:

* MoE truyền thống giống như chọn 2 cuốn bách khoa toàn thư lớn.
* DeepSeekMoE giống như chọn 8 chương chuyên môn nhỏ từ một thư viện lớn.

Tổng số trang phải đọc tương đương, nhưng lựa chọn thứ hai chính xác và linh hoạt hơn.

---

## 3. Shared expert isolation

Fine-grained segmentation vẫn chưa giải quyết hoàn toàn việc các routed expert cùng học kiến thức chung. Vì vậy, DeepSeekMoE tách một số expert thành **shared experts**.

### Hai loại expert

**Shared experts**

* Luôn được kích hoạt cho mọi token.
* Không phụ thuộc vào router.
* Học kiến thức nền và các mẫu phổ biến dùng trong nhiều ngữ cảnh.

**Routed experts**

* Chỉ được kích hoạt khi router lựa chọn.
* Tập trung vào kiến thức đặc thù hơn: lĩnh vực, loại token, cấu trúc, ngôn ngữ hoặc kỹ năng cụ thể.

Đầu ra của một layer có thể hiểu là:

[
h_t^l =
\sum_{i=1}^{K_s}
\operatorname{FFN}^{\text{shared}}*i(u_t^l)
+
\sum*{j \in \operatorname{TopK}(t)}
g_{j,t}\operatorname{FFN}^{\text{routed}}_j(u_t^l)
+
u_t^l
]

Trong đó (K_s) là số shared expert. 

### Vì sao shared expert hữu ích?

Không có shared expert, mỗi routed expert đều có thể phải dành một phần dung lượng để học:

* ngữ pháp cơ bản;
* cấu trúc câu;
* kiến thức ngôn ngữ phổ thông;
* các biến đổi thường gặp;
* những mẫu được dùng trong hầu hết đầu vào.

Khi phần kiến thức chung được gom vào shared expert, routed expert có thêm dung lượng để học phần chuyên biệt. Điều này làm giảm redundancy và tăng hiệu quả sử dụng tham số.

Trong phân tích ablation, khi nhóm nghiên cứu tắt shared expert và thay bằng thêm một routed expert để giữ nguyên chi phí tính toán, Pile loss tăng từ **1.808 lên 2.414**. Kết quả này cho thấy shared expert đã học một phần kiến thức nền khó thay thế bằng routing thông thường. 

---

## 4. Kiến trúc DeepSeekMoE 16B

Phiên bản được công bố rộng rãi có khoảng:

* **16.4 tỷ tổng tham số**;
* khoảng **2.8 tỷ tham số được kích hoạt cho mỗi token**;
* huấn luyện trên **2 nghìn tỷ token tiếng Anh và tiếng Trung**. ([GitHub][2])

Trong mỗi MoE layer của DeepSeekMoE 16B:

* 2 shared expert;
* 64 routed expert;
* mỗi expert chỉ bằng khoảng 0.25 kích thước FFN chuẩn;
* mỗi token luôn đi qua 2 shared expert;
* router chọn thêm 6 trong 64 routed expert.

Có thể viết ngắn gọn:

[
2\text{ shared}+6\text{ routed}/64
]

Các FFN đều được thay bằng MoE layer, ngoại trừ layer đầu tiên. Nhóm tác giả cho biết cân bằng tải ở layer đầu hội tụ chậm hơn, nên giữ FFN dense ở đó. 

### “16B nhưng chỉ kích hoạt 2.8B” nghĩa là gì?

* **16.4B total parameters** quyết định dung lượng kiến thức mà mô hình có thể lưu.
* **2.8B activated parameters** gần với lượng tham số thực sự tham gia tính toán cho một token.

Tuy nhiên, không nên kết luận rằng chi phí triển khai hoàn toàn giống mô hình dense 2.8B:

* toàn bộ 16.4B trọng số vẫn cần được lưu trong bộ nhớ;
* routing và trao đổi token giữa thiết bị tạo thêm overhead;
* kernel nhỏ và expert parallelism có thể không tận dụng GPU tốt như một phép nhân ma trận dense lớn.

MoE chủ yếu giảm **FLOPs trên mỗi token**, không tự động làm giảm tương ứng bộ nhớ trọng số hoặc độ phức tạp hệ thống.

---

## 5. Router và cân bằng tải

Router tính độ phù hợp giữa hidden state của token (u_t) và vector đại diện của expert (e_i):

[
s_{i,t}=
\operatorname{Softmax}_i(u_t^\top e_i)
]

Sau đó chọn các routed expert có score cao nhất.

Một vấn đề phổ biến là **expert collapse**: router gửi quá nhiều token vào một vài expert, khiến chúng quá tải còn các expert khác ít được huấn luyện.

DeepSeekMoE sử dụng các mục tiêu cân bằng ở nhiều mức:

* cân bằng tải giữa expert;
* cân bằng tải giữa các thiết bị;
* cân bằng giao tiếp, nhằm tránh một thiết bị phải gửi hoặc nhận quá nhiều token.

Một điểm đáng chú ý là nhóm tác giả không muốn ép mọi expert cân bằng tuyệt đối. Ràng buộc quá mạnh có thể buộc router chọn expert không phù hợp chỉ để cân tải, từ đó giảm chất lượng mô hình. Mục tiêu thực tế quan trọng hơn là tránh nút thắt tính toán ở cấp thiết bị. 

Đây là kiến trúc DeepSeekMoE ban đầu; các phiên bản DeepSeek sau này bổ sung những kỹ thuật cân bằng tải mới hơn, vì vậy không nên đồng nhất mọi cơ chế routing của DeepSeek-V2/V3 với đúng thiết kế trong bài báo này.

---

## 6. Thí nghiệm ở quy mô 2B

Nhóm tác giả trước hết thử nghiệm kiến trúc ở khoảng 2B tham số để có thể thực hiện nhiều ablation.

Cấu hình DeepSeekMoE 2B điển hình gồm:

* 1 shared expert;
* 63 routed expert;
* kích hoạt 7 routed expert cho mỗi token;
* tức (1+7) expert hoạt động.

Trong so sánh với GShard:

* DeepSeekMoE có khoảng 1.89B tham số expert;
* GShard×1.5 có khoảng 2.83B tham số expert;
* DeepSeekMoE vẫn đạt hiệu năng tương đương hoặc tốt hơn trên nhiều benchmark;
* lượng FLOPs trên 2K token là khoảng 4.3T so với 5.8T của GShard×1.5. 

Điểm đáng chú ý là DeepSeekMoE gần đạt chất lượng của một biến thể dense có cùng tổng dung lượng FFN. Dense được xem là “cận trên” trong phép so sánh này vì mọi tham số FFN đều được kích hoạt cho mỗi token, trong khi MoE chỉ kích hoạt một phần.

### Phân tích mức độ chuyên biệt hóa

Nhóm tác giả thực hiện ba kiểm tra quan trọng.

**Tắt các expert có routing score cao nhất.** DeepSeekMoE bị suy giảm mạnh hơn GShard. Tác giả diễn giải điều này là mỗi expert quan trọng và khó thay thế hơn, tức redundancy thấp hơn.

**Giảm số routed expert được kích hoạt.** Chỉ với 4 routed expert hoạt động, DeepSeekMoE đã đạt Pile loss gần với GShard top-2, dù lượng tham số expert được kích hoạt thấp hơn.

**Huấn luyện cấu hình tiết kiệm hơn từ đầu.** Với 1 shared expert và chỉ 3 trong 63 routed expert, mô hình vẫn vượt GShard trong thí nghiệm tương ứng, dù lượng tham số expert hoạt động chỉ bằng khoảng một nửa. 

Các thí nghiệm này hỗ trợ giả thuyết rằng mô hình không chỉ có nhiều expert hơn, mà router thực sự học cách kết hợp các expert nhỏ một cách chính xác hơn.

---

## 7. Kết quả DeepSeekMoE 16B

Khi so với DeepSeek 7B dense, cả hai đều được huấn luyện trên 2T token:

| Thuộc tính        | DeepSeek 7B dense | DeepSeekMoE 16B |
| ----------------- | ----------------: | --------------: |
| Tổng tham số      |              6.9B |           16.4B |
| Tham số kích hoạt |              6.9B |            2.8B |
| FLOPs/4K token    |            183.5T |           74.4T |
| Training tokens   |                2T |              2T |

DeepSeekMoE chỉ sử dụng khoảng **40.5% lượng tính toán**, nhưng đạt kết quả tương đương tổng thể. Nó tốt hơn trên một số tác vụ như:

* HellaSwag: 77.1 so với 75.4;
* TriviaQA: 64.8 so với 59.7;
* NaturalQuestions: 25.5 so với 22.2;
* GSM8K: 18.8 so với 17.4;
* HumanEval: 26.8 so với 26.2.

Tuy nhiên, nó kém hơn ở một số benchmark multiple-choice và tiếng Trung, chẳng hạn MMLU, CEval và CMMLU. 

So với LLaMA 2 7B, DeepSeekMoE 16B dùng khoảng **39.6% FLOPs** và thắng trên phần lớn benchmark được báo cáo. Tuy vậy, một phần lợi thế ở toán, code và tiếng Trung có thể đến từ khác biệt dữ liệu huấn luyện, chứ không thể quy hoàn toàn cho kiến trúc MoE. 

---

## 8. Điểm yếu và giới hạn

### Ít tham số attention

DeepSeekMoE 16B chỉ có khoảng 0.5B tham số attention, trong khi DeepSeek 7B dense có khoảng 2.5B tham số attention. Tác giả cho rằng đây có thể là nguyên nhân mô hình yếu hơn trên một số tác vụ multiple-choice như MMLU. 

MoE chủ yếu mở rộng FFN; nó không trực tiếp làm attention mạnh hơn. Vì vậy, MoE đặc biệt phù hợp để tăng dung lượng lưu trữ và xử lý kiến thức, nhưng không nhất thiết cải thiện tương ứng các kỹ năng phụ thuộc mạnh vào tương tác giữa token hoặc suy luận nhiều bước.

### FLOPs không đồng nghĩa với tốc độ thực tế

Bài báo cho biết với operator được tối ưu, mô hình có thể đạt tốc độ suy luận gần 2.5 lần mô hình dense 7B và có thể triển khai trên GPU 40 GB. Tuy nhiên, mức tăng tốc này phụ thuộc mạnh vào:

* batch size;
* cách sắp xếp expert;
* expert parallelism;
* băng thông kết nối;
* kernel fusion;
* độ cân bằng routing.

Do đó, giảm FLOPs 60% không đảm bảo latency cũng giảm đúng 60%. 

### Bằng chứng chuyên biệt hóa còn gián tiếp

Bài báo dùng độ nhạy khi tắt expert và các thí nghiệm ablation để suy ra mức độ chuyên biệt hóa. Đây là bằng chứng hợp lý, nhưng chưa trực tiếp chứng minh một expert cụ thể học “toán”, “code” hoặc “tiếng Trung”. Phân tích ngữ nghĩa của từng expert vẫn là một hướng nghiên cứu riêng.

### So sánh giữa các mô hình chưa hoàn toàn tách biệt dữ liệu

So sánh nội bộ với DeepSeek 7B khá thuyết phục vì hai mô hình dùng cùng corpus 2T token. Ngược lại, so sánh với LLaMA 2 chịu ảnh hưởng của dữ liệu, tokenizer và quy trình huấn luyện khác nhau.

---

## 9. Ý nghĩa đối với các LLM DeepSeek sau này

DeepSeekMoE đặt nền móng cho hướng thiết kế sau này của DeepSeek:

* nhiều routed expert nhỏ;
* một hoặc nhiều shared expert;
* chỉ kích hoạt một phần expert trên mỗi token;
* tăng tổng dung lượng mô hình mà không tăng FLOPs theo tỷ lệ tương ứng.

DeepSeek-V2 và DeepSeek-V3 tiếp tục sử dụng kiến trúc DeepSeekMoE, kết hợp thêm các kỹ thuật khác như Multi-head Latent Attention và các phương pháp cân bằng tải mới. Chẳng hạn DeepSeek-V3 có 671B tổng tham số nhưng chỉ kích hoạt khoảng 37B cho mỗi token. ([GitHub][3])

Vì vậy, đóng góp quan trọng nhất của bài báo không đơn thuần là tạo ra mô hình 16B. Nó đề xuất một nguyên tắc thiết kế:

> Thay vì xây ít expert lớn và để chúng học kiến thức pha trộn, hãy xây nhiều expert nhỏ, tách kiến thức chung sang shared expert và cho router ghép các expert chuyên biệt theo từng token.

## 10. Tóm tắt bản chất kiến trúc

[
\boxed{
\text{DeepSeekMoE}
==================

\text{fine-grained routed experts}
+
\text{always-on shared experts}
}
]

* **Fine-grained experts** giảm knowledge hybridity.
* **Shared experts** giảm knowledge redundancy.
* **Sparse routing** giữ chi phí tính toán thấp.
* **Nhiều tổ hợp expert** tăng khả năng biểu diễn.
* **Load balancing** giúp huấn luyện ổn định trên nhiều thiết bị.

Kết quả chính của bài báo là DeepSeekMoE 16B có **16.4B tổng tham số nhưng chỉ kích hoạt 2.8B mỗi token**, đạt hiệu năng gần các mô hình dense 7B với khoảng 40% FLOPs. Đây là một trong những bước kiến trúc quan trọng dẫn tới các LLM MoE quy mô lớn của DeepSeek sau này.

[1]: https://arxiv.org/abs/2401.06066?utm_source=chatgpt.com "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
[2]: https://github.com/deepseek-ai/DeepSeek-MoE?utm_source=chatgpt.com "DeepSeekMoE: Towards Ultimate Expert Specialization in ..."
[3]: https://github.com/deepseek-ai/deepseek-v3?utm_source=chatgpt.com "deepseek-ai/DeepSeek-V3"
