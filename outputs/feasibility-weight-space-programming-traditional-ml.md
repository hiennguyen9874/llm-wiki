# Đánh giá tính khả thi của Weight-Space Programming cho các bài toán Machine Learning truyền thống

*Viết ngày 2026-11-09 từ toàn bộ 11 concept trong [`wiki/`](../wiki/index.md) và survey [`survey-weight-space-programming.md`](survey-weight-space-programming.md). Đây là một deliverable dẫn xuất, không phải tri thức chuẩn. Nguồn chuẩn là các concept trong wiki; footnote và locator nằm trong từng concept.*

> [!note] Cách đọc mức độ bằng chứng
> - **Reported:** số liệu hoặc khẳng định do nguồn tự công bố. Wiki chưa reproduce bất kỳ thí nghiệm nào, và cả 11 concept đều `status: draft`.
> - **Synthesis:** đánh giá của bài này, suy ra từ các bằng chứng được dẫn.
> - **Kiến thức nền:** hiểu biết ML phổ thông **không** có trong wiki. Phần này được đánh dấu riêng và chỉ dùng để đặt bối cảnh.
>
> Phần lớn kết luận về tính khả thi dưới đây là **Synthesis**. Wiki không có thí nghiệm nào được thiết kế riêng để kiểm tra weight-space programming (WSP) trên benchmark ML truyền thống.

---

## 1. Kết luận nhanh

**Synthesis:**

1. **WSP chưa khả thi để thay thế gradient training cho bài toán ML truyền thống khi có đủ dữ liệu.** Mọi kết quả tích cực đều đến từ mạng rất nhỏ, bài toán có đặc tả rõ, hoặc có source code. Gần như tất cả là Reported, chưa được kiểm chứng độc lập. Ở những nơi có so sánh, các baseline đơn giản (kiểm thử theo đặc tả, thống kê column norm, fine-tuning) cũng giải được bài toán, thường rẻ hơn.
2. **WSP có tiềm năng khả thi ở ba vai trò hẹp:**
   - (a) **audit/debug** mạng nhỏ;
   - (b) **targeted repair** thưa (sparse) cho một lỗi đã khoanh vùng;
   - (c) **"biên dịch" một luật đã biết thành trọng số** khi nhãn khan hiếm.

   Cả ba vai trò đều cần harness đánh giá chặt và phải kiểm tra trong arithmetic khi triển khai.
3. **Khả thi thấp với bài toán perception** (ảnh tự nhiên, giọng nói). Wiki ghi nhận việc gán ngữ nghĩa dựa trên prior và kết quả giai thoại kém với ASR/TTS. Với **regression, time series, recommendation, clustering**, và các mô hình phi nơ-ron (cây quyết định, SVM, …), wiki **chưa có tri thức nào được biên dịch**.

---

## 2. Phạm vi: "ML truyền thống" ở đây nghĩa là gì

Bài đánh giá hai nhóm:

- **Bài toán truyền thống giải bằng mạng nơ-ron nhỏ:** phân loại/hồi quy trên dữ liệu bảng (tabular), phân loại ảnh bằng CNN, phân loại văn bản, điều khiển/RL cổ điển.
- **Thuật toán ML cổ điển phi nơ-ron:** linear/logistic regression, SVM, cây quyết định, gradient boosting, kNN. Wiki không có bằng chứng nào cho nhóm này (xem §5.6).

Tiêu chí khả thi gồm năm mặt:

1. chất lượng so với baseline đã được huấn luyện;
2. chi phí và khả năng mở rộng (scale);
3. độ tin cậy, side effect và an toàn số học;
4. khả năng kiểm chứng và tái lập;
5. phụ thuộc vào năng lực của mô hình editor.

---

## 3. Tổng hợp bằng chứng liên quan trong wiki

### 3.1 Các điểm dữ liệu gần nhất với ML truyền thống

| Bài toán | Loại bài toán truyền thống | Vai trò WSP | Kết quả (Reported) | Baseline / đối chứng | Concept |
| --- | --- | --- | --- | --- | --- |
| Mạng quyết định xạ trị, ReLU 2 lớp, 433 tham số, 8 input | **Tabular binary classification** | Đọc và sửa | Phát hiện 16/18 mạng lỗi; sửa với trung vị 3 tham số; 14/16 bản sửa không tạo thêm lỗi mới | Kiểm thử theo protocol tách được cả 21 mạng trong 0.4 giây; column norm tìm ra mọi confound; fine-tuning trên 200K ví dụ sửa được cả 18 mạng | [Clinical audit](../wiki/clinical-decision-network-weight-audit.md) |
| Legal citation classifier, khoảng 100K tham số | **Text classification** | Viết từ đầu | Hand-written 97.8% (0 nhãn), 98.9% (5,062 nhãn) | Trained 94.6% (8,192 nhãn) | [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md) |
| CNN khoảng 124K–127K tham số, 5 dataset ảnh | **Image classification** | Chỉ đọc | Trích xuất đúng thống kê cục bộ, nhưng gán sai dataset và class (SAT-6: 0/6 tên class) | Label permutation và shuffling cho thấy ngữ nghĩa dựa vào prior | [Dataset-prior audit](../wiki/weight-reading-dataset-prior-audit.md) |
| MinAtar (3 game), Go 9×9, Kinetix | **RL / control** | Viết và sửa | Vượt PPO 100M ở cả 3 game MinAtar; Breakout gấp khoảng 20 lần PPO 500M; Kinetix 1,024/1,024 | Thua PPO 500M ở Seaquest và Asterix; Kinetix chỉ trên một level | [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md) |
| ASR từ đầu; Pocket TTS | **Speech** | Viết và sửa | Giai thoại: ASR kém; TTS chỉ 1/20 mẫu tốt | Cách dùng KV-cache với ngữ cảnh giọng nói được báo cáo là tốt hơn | [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md) |
| Game ID, 4 PPO policy | Model identification | Đọc | 4/4, có tranh cãi Frogger/Freeway; Qwen 3.8 27B chạy local đúng 3/4 | Trọng số input "vẽ ra bản đồ", nên có thể là bài dễ | [Weight reading](../wiki/reading-neural-network-weights-with-llms.md) |

### 3.2 Các bằng chứng gián tiếp quan trọng

- **Feedback vẫn cần thiết.** "Zero-gradient" không có nghĩa là không có feedback. Go và Qwen dùng tới 50 forward pass, và ngân sách 10 hoặc 25 pass cho kết quả kém hơn nhiều (Reported) ([Weight-space programming](../wiki/weight-space-programming.md), [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)).
- **"Gỡ vật cản" khác với "thêm năng lực".** Cải thiện trên Qwen chủ yếu đến từ giảm loop. Gemma 3 270M, vốn không loop, gần như không cải thiện (Reported) ([LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)).
- **Phụ thuộc mạnh vào editor.** Trong Writing Weights Index, các mô hình đóng như GPT-6 Astra (60.7), Gemini 4 Carbon (57.7) và Claude Opus 5.5 (51.2) đạt khoảng hoặc trên mức PPO 500M (50). Phần lớn mô hình open-weight dưới 13 điểm. Chỉ số này không công bố protocol (Reported) ([Writing Weights Index](../wiki/writing-weights-index.md)).
- **Failure mode đo lường.** Bản sửa có thể là silent no-op; baseline nhiễu tạo ra cải thiện ảo; coarse gain làm điểm tụt từ 4/8 xuống 0/8 (Reported) ([Coarse normalization](../wiki/coarse-normalization-weight-editing-experiment.md)).
- **Side effect.** Steering compiled vào weights làm mô hình trả lời task Python bằng văn xuôi; blend 10% làm hỏng code (Reported) ([Browser editing](../wiki/browser-weight-space-editing.md)). Bản sửa Italian có ít side effect hơn LoRA trên 200 câu không liên quan (182 so với 120 câu không đổi), nhưng làm hỏng 2 controls so với 0 của LoRA (Reported, tự báo cáo, không rõ n) ([Italian translation](../wiki/italian-translation-weight-edit-experiment.md)).
- **Tuần tự và tích lũy.** Sửa thưa vẫn có thể giao thoa qua các phép tính dùng chung. Nguồn báo cáo ROME và MEMIT xuống cấp khi sửa tuần tự (Reported) ([Continual learning](../wiki/continual-learning-and-recursive-improvement.md)).
- **Chọn cơ chế thích nghi.** RAG, fine-tuning, LoRA và direct edit giải quyết các nhu cầu khác nhau. Việc chọn cơ chế nào là phán đoán kỹ thuật, không có quy tắc phổ quát (Reported) ([Model adaptation mechanisms](../wiki/model-adaptation-mechanisms.md)).

---

## 4. Đánh giá theo năm tiêu chí

### 4.1 Chất lượng so với baseline được huấn luyện
**Synthesis:**
- Trong các bằng chứng có trong wiki, WSP **chỉ** thắng gradient training trong hai trường hợp:
  - legal citation: mức nhãn thấp, chưa kiểm chứng, attribution không rõ, thiếu confusion matrix;
  - RL: so với PPO ít bước, hoặc khi editor được cung cấp source code của môi trường.
- Khi baseline được huấn luyện đầy đủ (PPO 500M ở Seaquest/Asterix), hoặc khi có đặc tả chính xác (clinical), lợi thế biến mất hoặc đảo ngược.
- Một phê bình cho rằng các bài được chọn đều có lời giải là chương trình xác định nhỏ, sau đó chỉ được mã hóa vào trọng số (Reported critique, [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)). Nếu đúng, WSP thực chất là **program synthesis + compile-to-weights**. Cách này hiệu quả khi bài toán có lời giải ngắn gọn bằng luật, và kém khi tín hiệu nằm trong phân phối dữ liệu phức tạp, như ảnh tự nhiên hay giọng nói.

### 4.2 Chi phí và khả năng mở rộng
- **Reported:** replay một thí nghiệm đọc 17,253 trọng số tốn khoảng 73,700 input token ([LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)). Đọc tool-free bằng Qwen 3.8 27B local mất 46 phút đến 1 giờ 05 phút cho mỗi prompt ([Weight reading](../wiki/reading-neural-network-weights-with-llms.md)). Audit CNN khoảng 125K tham số đưa toàn bộ trọng số vào prompt, và 3 phiên phải chạy tiếp vì chạm giới hạn output ([Dataset-prior audit](../wiki/weight-reading-dataset-prior-audit.md)). Bản sửa Qwen 0.8B cần 50 pass, 80 lần chạy Python và 158 agent turn ([LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)).
- **Synthesis:**
  - Từ con số 17,253 trọng số ↔ khoảng 73.7K token, ước lượng **khoảng 4 token cho mỗi trọng số** (cận trên, vì prompt còn chứa mô tả mạng). Khi đó mạng 10⁶ tham số cần cỡ 4M token, vượt xa context. Đọc toàn bộ trọng số dạng text chỉ thực tế tới cỡ 10⁵ tham số. Lớn hơn thì phải chuyển sang phân tích bằng Python và chỉ đọc chọn lọc.
  - Williams nhấn mạnh rằng chi phí **tìm ra** bản sửa chưa được báo cáo, nên chưa thể so hiệu quả với fine-tuning (Reported, [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)).
- **Kiến thức nền (không có trong wiki):** huấn luyện một MLP vài trăm đến vài nghìn tham số trên dữ liệu bảng thường chỉ mất vài giây đến vài phút trên CPU. Vì vậy, với bài toán nhỏ có dữ liệu, WSP khó cạnh tranh về chi phí.

### 4.3 Độ tin cậy, side effect, an toàn số học
- **Reported:**
  - Clinical audit chỉ xác nhận được 2/5 mạng khỏe mà không cần ép kết luận. Một false alarm dẫn tới bản sửa làm 2,018 quyết định bị sai. Một bản sửa bị ép trên mạng trigger làm 1,181 quyết định đúng thành sai.
  - **Mọi** bản sửa có trọng số ≥ 10⁵ đều thất bại ở fp16 ([Clinical audit](../wiki/clinical-decision-network-weight-audit.md)).
  - Kinetix bị phê bình là có trọng số tới 876 (chưa kiểm chứng).
- **Synthesis:** với ML truyền thống trong production (scoring, fraud, triage), **khả năng chứng nhận "mạng sạch"** quan trọng ngang khả năng tìm lỗi. Đây đang là điểm yếu nhất. Bản sửa do LLM viết có xu hướng tạo trọng số cực đại, nên cần kiểm tra quantization/fp16 một cách bắt buộc.

### 4.4 Khả năng kiểm chứng và tái lập
- **Reported:** phần lớn nguồn là blog, Reddit hoặc X, thiếu protocol. Ngay cả preprint cũng không preregister. Audit CNN phần lớn chỉ chạy 1 seed, 1 lần. Harness sửa Qwen không được công bố đầy đủ ([LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md), [Dataset-prior audit](../wiki/weight-reading-dataset-prior-audit.md), [Clinical audit](../wiki/clinical-decision-network-weight-audit.md)).
- **Synthesis:** trong ML truyền thống đã có quy trình chuẩn (train/val/test split, cross-validation, nhiều seed). WSP hiện chưa đạt chuẩn đó. Bù lại, **diff thưa** (ví dụ 3 tham số) là một ưu điểm lớn cho review và audit, nếu kèm regression test.

### 4.5 Phụ thuộc vào editor
- **Synthesis:** khoảng cách lớn giữa mô hình đóng và open-weight trong Writing Weights Index, cùng kết quả Qwen local chỉ đúng 3/4 và mất gần 1 giờ mỗi prompt, cho thấy khả thi hiện tại gắn với **frontier model trả phí**. Đây là ràng buộc về chi phí, dữ liệu nhạy cảm (phải gửi trọng số ra ngoài) và tính tái lập, vì model alias có thể thay đổi. Clinical audit dùng một alias không ghi ngày, với sampling không kiểm soát (Reported).

---

## 5. Ma trận khả thi theo loại bài toán

Thang đánh giá: **Cao / Trung bình / Thấp / Chưa có dữ liệu**. Toàn bộ là **Synthesis**.

| # | Loại bài toán | Thay thế training | Audit / debug | Targeted repair | Căn cứ chính |
| --- | --- | --- | --- | --- | --- |
| 5.1 | Tabular classification, MLP rất nhỏ (≤ 10³–10⁴ tham số) | Thấp | **Trung bình** | **Trung bình** | Clinical: phát hiện tốt, sửa thưa; nhưng clearance kém, overflow fp16, baseline rẻ cũng làm được |
| 5.2 | Phân loại theo luật đã biết, nhãn khan hiếm (citation, format, protocol) | **Trung bình** | Trung bình | Trung bình | Legal citation 97.8% với 0 nhãn (chưa kiểm chứng); bản chất là compile luật vào trọng số |
| 5.3 | RL / control có simulator hoặc source code | Trung bình (so với PPO ít bước) | Trung bình | **Trung bình** | MinAtar, Go, Kinetix; thua PPO 500M ở 2/3 game; Kinetix một level |
| 5.4 | Image classification (CNN, ảnh tự nhiên/vệ tinh) | Thấp | Thấp–Trung bình (chỉ thống kê cục bộ) | Chưa có dữ liệu | Gán ngữ nghĩa dựa vào prior; không có thí nghiệm sửa CNN |
| 5.5 | Speech / audio | Thấp | Chưa có dữ liệu | Thấp | Giai thoại ASR và TTS kém |
| 5.6 | Regression, time series, recommendation, clustering, anomaly detection | Chưa có dữ liệu | Chưa có dữ liệu | Chưa có dữ liệu | Wiki chưa có tri thức |
| 5.7 | Mô hình phi nơ-ron (linear/logistic, SVM, tree, GBM, kNN) | Chưa có dữ liệu | Chưa có dữ liệu | Chưa có dữ liệu | Wiki chưa có tri thức (xem ghi chú) |

**Ghi chú 5.1.** Đây là trường hợp gần ML truyền thống nhất và có bằng chứng tốt nhất (preprint, dữ liệu synthetic). Kết luận quan trọng: khi **có đặc tả chính xác**, kiểm thử trực tiếp theo đặc tả (0.4 giây) hiệu quả hơn hẳn. Khi **có dữ liệu gắn nhãn**, fine-tuning sửa được mọi mạng nhưng thay đổi gần toàn bộ tham số. Giá trị riêng của WSP nằm ở **bản sửa nhỏ và đọc được**, không phải ở độ chính xác.

**Ghi chú 5.2.** Đây là vùng hứa hẹn nhất cho "viết từ đầu": bài toán có cấu trúc luật mà LLM hiểu được (cú pháp citation, luật game), và dữ liệu gắn nhãn đắt. Tuy vậy cần đặt câu hỏi: nếu luật đã viết được thành chương trình, **vì sao phải là mạng nơ-ron?** Các lý do có thể là: triển khai trên accelerator (nguồn Claude báo cáo 50 μs mỗi citation, 1.8M citation/s, chưa đối chiếu được), khởi tạo để fine-tune tiếp, hoặc tích hợp vào pipeline khả vi. Các lý do này **chưa được kiểm tra** trong wiki.

**Ghi chú 5.4.** Audit CNN cho thấy LLM tìm đúng *cấu trúc*, ví dụ cụm output bị hoán vị, nhưng sai *ngữ nghĩa*. Với ML truyền thống, điều này nghĩa là WSP có thể hỗ trợ phát hiện bất thường cấu trúc trong trọng số (dead unit, sign pattern, số bước huấn luyện qua batch-norm). Không nên tin WSP để trả lời câu hỏi "mạng này học gì".

**Ghi chú 5.7 (Kiến thức nền, không có trong wiki).** Với linear/logistic regression, trọng số vốn đã diễn giải được và chỉnh trực tiếp được bằng công cụ chuẩn, nên lợi thế "đọc trọng số" của WSP gần như biến mất. Cây quyết định và GBM không có "không gian trọng số" liên tục theo nghĩa của các thí nghiệm. Việc LLM sửa luật của cây thuộc phạm vi rộng hơn và chưa được wiki biên dịch.

---

## 6. Khi nào nên và không nên cân nhắc WSP

**Synthesis**, rút từ §3–§5.

**Điều kiện thuận lợi (cần nhiều điều kiện cùng lúc):**
- Mô hình nhỏ (≲ 10⁵ tham số) hoặc lỗi đã khoanh vùng được vào một vài tensor.
- Có đặc tả hoặc luật miền rõ ràng mà LLM hiểu, nhưng dữ liệu gắn nhãn khan hiếm hoặc đắt.
- Cần một **diff thưa, đọc được** cho audit, review hay compliance.
- Có harness đánh giá mạnh: test set cố định, regression suite, kiểm tra trong arithmetic khi triển khai, và ngân sách forward pass.
- Có quyền dùng frontier model, và được phép gửi trọng số ra ngoài.

**Điều kiện bất lợi:**
- Có đủ dữ liệu và training rẻ: gradient training, fine-tuning hoặc PEFT mạnh hơn và đã được kiểm chứng.
- Bài toán perception hoặc tín hiệu phân phối phức tạp.
- Mô hình lớn mà không có công cụ phân tích.
- Cần **bảo đảm** an toàn hoặc chứng nhận. Clinical audit tự nhận không phải phương pháp validation hay certification ([Clinical audit](../wiki/clinical-decision-network-weight-audit.md)).
- Chỉ có editor open-weight nhỏ.
- Vấn đề có thể giải bằng thay đổi rẻ hơn, như decoding, temperature hay giới hạn output (bài học từ Qwen).

---

## 7. Giao thức pilot đề xuất cho một bài toán ML truyền thống

**Synthesis**, gộp các khuyến nghị Reported trong [survey](survey-weight-space-programming.md) §8.2 và các concept liên quan.

1. **Chọn bài toán phù hợp.** MLP tabular ≤ 10⁴ tham số, có lỗi đã biết (ví dụ confound hoặc threshold shift) và có đặc tả miền.
2. **Baseline bắt buộc, cùng ngân sách:**
   - kiểm thử trực tiếp theo đặc tả;
   - thống kê đơn giản (column norm, unit activation);
   - fine-tuning và LoRA/PEFT;
   - nếu là LM: thay đổi decoding (repetition penalty, temperature).
3. **Ghi đủ ngân sách tìm bản sửa:** token, forward pass, số lần chạy Python, agent turn, thời gian thực, và tất cả lần thử thất bại.
4. **Measurement contract:**
   - kiểm tra tensor đích thực sự thay đổi, tránh no-op;
   - dùng greedy decoding hoặc seed cố định;
   - so kết quả từng mẫu qua các lần chạy độc lập;
   - chạy nhiều seed và báo cáo uncertainty.
5. **Kiểm tra side effect:** đo trên phân phối rộng ngoài vùng lỗi; báo cáo confusion matrix, không chỉ accuracy; đo trên **mạng khỏe** để tính tỉ lệ false alarm.
6. **Arithmetic khi triển khai:** chạy lại trong fp16/bf16/int8. Từ chối các bản sửa có trọng số vượt ngưỡng an toàn số học.
7. **Sửa tuần tự:** áp dụng nhiều bản sửa liên tiếp và đo khả năng giữ hành vi cũ.
8. **Integrity:** lưu hash/checksum trước và sau, lưu manifest diff, và chạy regression suite cố định.

**Tiêu chí "khả thi" gợi ý (Synthesis):** WSP được xem là khả thi cho một use case khi nó **ngang hoặc hơn** baseline rẻ nhất ở cả chất lượng lẫn side effect dưới cùng ngân sách, **và** mang lại lợi ích mà baseline không có (diff nhỏ, đọc được; không cần nhãn).

---

## 8. Câu hỏi mở cần nguồn mới để trả lời

- Có benchmark công khai nào chạy WSP trên dataset ML chuẩn (UCI/OpenML tabular, MNIST/CIFAR với editing) với nhiều seed hay không?
- Trọng số do WSP viết, khi dùng làm khởi tạo (warm-start) cho gradient training, có giúp hội tụ nhanh hơn hoặc giảm nhu cầu nhãn không?
- WSP có làm được unlearning hoặc khử bias cho mô hình tabular dưới đánh giá fairness chuẩn không? Unlearning chỉ được nêu như ứng dụng tương lai ([Weight-space programming](../wiki/weight-space-programming.md)).
- Chi phí tìm bản sửa so với fine-tuning, khi đo trên cùng phần cứng, là bao nhiêu?
- Các mô hình open-weight có thu hẹp khoảng cách trong Writing Weights Index không? Concept này có `stale_after: 2027-05-09`.

---

## 9. Giới hạn của bản đánh giá này

- **Chỉ dựa trên wiki đã biên dịch** (11 concept, tất cả `draft`) và survey trong `outputs/`. Không mở `raw/` và không chạy thí nghiệm nào. Mọi số liệu đều Reported, không phải Reproduced.
- **Wiki được xây quanh các thí nghiệm WSP gốc,** không quanh ML truyền thống. Vì vậy ma trận ở §5 chủ yếu là ngoại suy (Synthesis). Các ô "Chưa có dữ liệu" nghĩa là chưa được biên dịch, **không** có nghĩa là bất khả thi.
- **Ước lượng khoảng 4 token cho mỗi trọng số** suy ra từ đúng một điểm dữ liệu, với prompt chứa cả mô tả mạng. Đây là xấp xỉ thô.
- **Các nhận định "Kiến thức nền"** (§4.2, §5.7) không có nguồn trong wiki.
- **Danh tính mô hình** (GPT-6 Astra, Fable, Claude Opus 5.5, …) và attribution của legal citation classifier là theo nguồn, và một số còn tranh cãi.

## Tài liệu tham khảo (concept trong wiki)
- [Weight-space programming](../wiki/weight-space-programming.md)
- [LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)
- [Reading neural network weights with LLMs](../wiki/reading-neural-network-weights-with-llms.md)
- [Dataset-prior audit of neural weight reading](../wiki/weight-reading-dataset-prior-audit.md)
- [Clinical decision network weight audit](../wiki/clinical-decision-network-weight-audit.md)
- [Italian translation weight-edit experiment](../wiki/italian-translation-weight-edit-experiment.md)
- [Writing Weights Index](../wiki/writing-weights-index.md)
- [Browser-based weight-space editing](../wiki/browser-weight-space-editing.md)
- [Coarse normalization-weight editing experiment](../wiki/coarse-normalization-weight-editing-experiment.md)
- [Model adaptation mechanisms](../wiki/model-adaptation-mechanisms.md)
- [Continual learning and recursive improvement](../wiki/continual-learning-and-recursive-improvement.md)
- [Survey: Weight-Space Programming](survey-weight-space-programming.md)
