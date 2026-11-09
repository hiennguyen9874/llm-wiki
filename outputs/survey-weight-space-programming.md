# Weight-Space Programming: Survey về các phương pháp đọc, viết và chỉnh sửa trọng số mạng nơ-ron bằng LLM

*Tổng hợp từ wiki ngày 2026-11-09. Bài này là deliverable dẫn xuất (nằm trong `outputs/`), không phải tri thức chuẩn. Nguồn chuẩn là các concept trong [`wiki/`](../wiki/index.md).*

> [!note] Cách đọc mức độ bằng chứng
> Gần như mọi con số trong bài đều là **Reported**, tức do nguồn tự công bố. Wiki chưa chạy lại (reproduce) bất kỳ thí nghiệm nào. Các nhận định do bài viết tự suy luận được gắn nhãn **Synthesis**. Cả 11 concept nguồn đều có `status: draft`, nghĩa là còn giới hạn về coverage và provenance.

---

## Tóm tắt (Abstract)

**Weight-space programming** (lập trình trong không gian trọng số) là cách để một LLM đa dụng (general-purpose) suy luận trực tiếp trên trọng số (weights) của một mạng nơ-ron khác: **đọc** trọng số để suy ra hành vi, hoặc **viết/sửa** trọng số để đáp ứng một đặc tả bằng ngôn ngữ tự nhiên. Cách này không cập nhật trọng số qua optimizer hay gradient descent ([Weight-space programming](../wiki/weight-space-programming.md)). Survey này hệ thống hóa nội dung wiki thành năm nhóm phương pháp:

1. đọc trọng số (weight reading);
2. dựng mạng từ đầu (from-scratch weight writing);
3. sửa có mục tiêu (targeted repair/editing) do LLM điều khiển;
4. chỉnh sửa do con người điều khiển theo luật (human-directed, rule-based editing);
5. các cơ chế thích nghi mô hình (model adaptation) liên quan, dùng làm đường cơ sở để so sánh.

Bài cũng tổng hợp các giao thức đánh giá, benchmark, phê bình, failure mode, và mối liên hệ với continual learning và recursive self-improvement.

---

## 1. Giới thiệu và định nghĩa

### 1.1 Định nghĩa gốc
Bài blog "Sparks of Weight-Space Programming" (Takehi, Teoh, Zhang, Khattab, 11/2026) đặt ra thuật ngữ này. Theo bài, một LLM (ở đây là GPT-6 Astra) suy luận và đọc/viết trọng số để thỏa một đặc tả, khác với hai hướng sau ([Weight-space programming](../wiki/weight-space-programming.md)):
- tối ưu hóa training code;
- dùng một mô hình được huấn luyện chuyên để sinh trọng số, chẳng hạn hypernetwork.

### 1.2 "Zero-gradient" không đồng nghĩa với "không có feedback"
**Synthesis:** Nhiều thí nghiệm vẫn dùng một ngân sách forward pass có giới hạn, ví dụ 50 pass trong các thí nghiệm Go và LLM, để hướng dẫn và chọn bản sửa. Vì vậy khi so sánh với baseline phải giữ nguyên cả **feedback budget** lẫn cấu hình huấn luyện của baseline ([Weight-space programming](../wiki/weight-space-programming.md)).

### 1.3 Vị trí so với các hướng sẵn có
Bài của Masood nhấn mạnh rằng sửa tham số trực tiếp đã có từ trước, qua các phương pháp như ROME, MEMIT, MEND và hypernetwork. Điểm khác biệt mà weight-space programming tự nhận là **cuộc điều tra mở (open-ended investigation) do một LLM đa dụng thực hiện**, không phải việc lần đầu sửa tham số trực tiếp ([Model adaptation mechanisms](../wiki/model-adaptation-mechanisms.md)).

---

## 2. Phân loại phương pháp (Taxonomy)

| Nhóm | Ai quyết định thay đổi | Tín hiệu đầu vào | Ví dụ trong wiki |
| --- | --- | --- | --- |
| A. Weight reading | LLM | Trọng số dạng text, có khi thêm Python hoặc attention pattern | Nhận diện game, diffusion, character transformer, sycophancy; audit CNN; audit mạng lâm sàng |
| B. From-scratch writing | LLM | Luật chơi, source code, layout I/O | MinAtar, Go 9×9, legal citation classifier |
| C. LLM-directed repair/editing | LLM | Trọng số, failure case, công cụ Python, forward pass có giới hạn | Kinetix car, Qwen3.5-0.8B, Gemma Italian, mạng lâm sàng, inject profile facts |
| D. Human-directed rule-based editing | Con người | DSL selector/op, hidden-state statistics | webWeightSpace, coarse normalization gain |
| E. Cơ chế thích nghi khác (để so sánh) | Optimizer, retriever | Dữ liệu, gradient, tài liệu | Fine-tuning, LoRA, distillation, prompt baking, RAG, ROME/MEMIT/MEND |

---

## 3. Nhóm A — Đọc trọng số (Weight reading)

### 3.1 Các thiết lập
Nguồn gốc phân biệt ba mức quyền truy cập. Kết quả ở các mức này **không phải một phép thử interpretability đồng nhất** ([Reading neural network weights with LLMs](../wiki/reading-neural-network-weights-with-llms.md)).

| Thiết lập | Mô tả | Kết quả được công bố (Reported) |
| --- | --- | --- |
| **Tool-free, text weights** | Đưa trọng số dạng text, không có công cụ, không có forward pass | 4 PPO policy cùng shape (Breakout, Pong, Pac-Man, Freeway) được nhận diện "đúng". Ba diffusion model được gọi đúng là hình tròn, vuông, tam giác, nhưng Astra vẽ đường viền trong khi mô hình sinh hình tô kín |
| **Tool-assisted (Python)** | Chỉ đưa 4 block giữa và cho phép phân tích bằng Python, không có forward pass | Phân loại đúng 3 character transformer (Python, romaji, English), mỗi mô hình mất 2 lần thử. Các copying head mà Astra chỉ ra khớp với kết quả đo bằng chuỗi ngẫu nhiên lặp |
| **Activation-assisted** | Cho xem attention pattern trên tối đa 16 văn bản tự viết, không cho xem output | Chỉ dùng weights: thất bại cả 4 lần khi nhận diện mô hình sycophantic. Có attention pattern: nhận diện đúng trong 3 cặp mô hình |

**Cơ chế được giả định:** các tác giả quy việc nhận diện game cho pattern không gian ở layer đầu và pattern ở output hành động.

### 3.2 Thử nghiệm độc lập trên máy cá nhân
Một tác giả, được nguồn thứ cấp cho là Simon Willison, chạy **Qwen 3.8 27B** (Q4_K_M GGUF, qua LM Studio) mà không dùng công cụ. Mô hình gọi đúng Pac-Man, Pong và Breakout, nhưng nhận nhầm Freeway thành một game giống Pac-Man. Mỗi lần chạy mất khoảng 46 phút đến 1 giờ 05 phút; riêng lần Pac-Man dùng khoảng 43.5K reasoning token. Nguồn thứ cấp (MindStudio) mô tả cấu hình khác (Ollama, khoảng 26 GB VRAM), và wiki ghi đây là **discrepancy chưa giải quyết** ([Reading neural network weights with LLMs](../wiki/reading-neural-network-weights-with-llms.md)).

### 3.3 Audit dataset prior (CNN)
Ahmed (arXiv-2611.08070) đặt câu hỏi: LLM thật sự lần theo dòng trọng số, hay chỉ dựa vào **prior về dataset quen thuộc**? ([Dataset-prior audit](../wiki/weight-reading-dataset-prior-audit.md))

- **Thiết lập:** 3 kiến trúc CNN, khoảng 124K–127K tham số; 5 dataset là CIFAR-10, KMNIST, Cats vs Dogs, fast food và SAT-6. Claude Opus 5.5 nhận toàn bộ trọng số (làm tròn 3 chữ số thập phân), không có nhãn, công cụ hay forward pass.
- **Các phép kiểm soát (controls):**
  - *Label permutation:* hoán vị class nhưng giữ nguyên accuracy (82.37%). Mô hình tìm ra đúng cụm output bị dịch chuyển nhưng **gọi sai cả 9 cặp class**.
  - *Shuffling:* xáo trộn giá trị làm accuracy rơi xuống 7.78%, nhưng mô hình vẫn đoán CIFAR-10 với độ tự tin 45%.
  - *Dataset familiarity:* KMNIST bị gọi là MNIST; fast food bị gọi là CIFAR-10; một mô hình SAT-6 đạt 99.57% bị mô tả thành "ảnh động vật CIFAR-10", đoán đúng 0/6 tên class.
- **Điểm làm được:** mô hình khôi phục được cấu trúc dấu của output và suy ra số bước huấn luyện (khoảng 3) từ thống kê batch-norm.
- **Diễn giải của tác giả:** LLM trích xuất được *thống kê cục bộ* nhưng gán *ngữ nghĩa* dựa vào prior. Đây là một diễn giải, không phải phép đo trực tiếp cơ chế bên trong LLM. Phần lớn điều kiện chỉ chạy 1 lần với 1 seed.

### 3.4 Audit mạng quyết định lâm sàng
Nusrat & Nusrat (arXiv-2611.05341, preprint chưa peer-review) dùng các mạng ReLU 2 lớp, 433 tham số, quyết định có escalate yêu cầu lập kế hoạch xạ trị hay không. Dữ liệu là synthetic, có cài sẵn lỗi: confound, threshold shift lệch 3 Gy, hoặc trigger ([Clinical decision network weight audit](../wiki/clinical-decision-network-weight-audit.md)).

- **Phát hiện lỗi:** Claude Opus 5.5 phát hiện 16/18 mạng có lỗi (12/12 confound, 3/3 shift, 1/3 trigger).
- **Kiểm định mạng khỏe:** chỉ 2/5 mạng khỏe được xác nhận "sạch" mà không cần ép kết luận. Một false alarm dẫn tới bản sửa làm 2,018 quyết định bị sai.

---

## 4. Nhóm B — Viết trọng số từ đầu (From-scratch construction)

### 4.1 Game policy (MinAtar)
- **Đầu vào:** luật chơi, **source code** của game, layout input/output. Không có công cụ, rollout, gradient hay dữ liệu ([LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)).
- **Kết quả:** vượt PPO 100M bước (lấy seed tốt nhất trong 3–10 seed) ở cả 3 game. **Không** vượt PPO 500M ở Seaquest và Asterix.
- **Breakout:** 517.4 điểm so với 25.3 của PPO 500M, gấp khoảng 20 lần. Policy là một luật "dự đoán điểm bóng rơi" được mã hóa thưa (sparse).
- **Đánh giá:** 1,000 episode, action được sample, sticky action 0.1.

### 4.2 Go 9×9
Policy được viết vào một mạng lớn hơn, khởi tạo bằng 0, với sự hỗ trợ của Python.
- **Không có forward pass:** thắng các PPO nhỏ hơn hơn một nửa số ván.
- **Với 50 pass:** thắng PPO cùng kích thước được huấn luyện trên 20M ván.
- **Số liệu từ explainer thứ cấp:** tỉ lệ thắng 42.6%, 26.3%, 36.3% khi không có pass; 74.2%, 70.0%, 78.5% với 50 pass. Mô tả về đối thủ trong nguồn gốc chưa nhất quán hoàn toàn.

### 4.3 Legal citation classifier
Mạng khoảng 100K tham số, phân loại citation pháp lý là thật hay giả ([LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)):

| Trọng số | Số nhãn đã thấy | Tham số khác 0 | Test accuracy |
| --- | ---: | ---: | ---: |
| Hand-written | 0 | 3,793 | 97.8% |
| Hand-written, đã sửa 1 lần | 5,062 | 3,828 | 98.9% |
| Trained | 8,192 | 107,745 | 94.6% |

- **Attribution chưa rõ:** nguồn khác nhau gán kết quả cho "Fable 5.1", cho "Claude", hoặc cho "Anthropic's Claude Fable". Wiki ghi đây là **attribution không được xác lập**.
- **Synthesis:** accuracy tổng thể không cho biết tỉ lệ false-citation hay false-positive nếu thiếu confusion matrix.

### 4.4 Writing Weights Index
@xingyudang đưa ra một chỉ số tính trên 3 game ([Writing Weights Index](../wiki/writing-weights-index.md)):

$$
\text{Index} = \frac{1}{3}\sum_{g} 100\cdot\frac{q_g}{1+q_g},\qquad q_g=\frac{\max(0,\ \text{score}-\text{random})}{\text{PPO}_{500M}-\text{random}}
$$

- **Ý nghĩa (Synthesis):** điểm random hoặc tệ hơn ánh xạ về 0; ngang PPO 500M ánh xạ về 50. Phép biến đổi này phi tuyến, nên chỉ số không phải tỉ lệ phần trăm so với PPO.
- **Điểm số (Reported):** GPT-6 Astra 60.7, Gemini 4 Carbon 57.7, Claude Opus 5.5 51.2, PPO 500M 50.0, Kimi K3.1 Pro 29.8, PPO 100M 25.2. Các mô hình open-weight phần lớn dưới 13 điểm.
- **Giới hạn:** không có protocol, không có điểm từng game, không có uncertainty. Concept đặt `stale_after: 2027-05-09`.

---

## 5. Nhóm C — Sửa trọng số có mục tiêu do LLM điều khiển

### 5.1 Sửa policy (Kinetix car)
Đầu vào là policy, mô tả scene và một lần thất bại đã ghi lại. Trong một lần thử không dùng công cụ, Astra sửa 3.5% trọng số; policy sau sửa thành công 1,024/1,024 episode, trong khi baseline thành công 0/256. Cơ chế được mô tả là thêm một nhánh "lùi xe" rồi trả quyền điều khiển lại cho policy gốc. Một bài phê bình cho rằng bản sửa đẩy 10 trọng số lên tới 876 và chỉ thành công trên một level lặp lại; nhận định này chưa được kiểm chứng ([LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)).

### 5.2 Sửa LLM bằng cách trừ một direction (Qwen3.5-0.8B)
Đây là thí nghiệm nổi bật nhất trong các nguồn ([LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)).

- **Ngân sách:** 50 forward pass trên dữ liệu luyện tập, không có gradient.
- **Can thiệp:** trừ một direction khỏi 64 cột output của MLP ở layer 15 và 19. Tổng cộng 131,072 trọng số, khoảng 0.016% mô hình.
- **Công thức (nguồn thứ cấp Kingy AI):** với `u` là repetition direction ước lượng riêng cho từng layer,

  $$W_{\text{new}} = W_{\text{orig}} - 6\cdot \mathrm{outer}\big(u,\ \text{mask}_{64}\odot(u^\top W_{\text{orig}})\big)$$

  Đây là một điều chỉnh có hệ số nhân 6, không đơn thuần là phép chiếu loại bỏ (projection removal). Ma trận có kích thước 1,024 × 3,584.
- **Kết quả (Reported):**

  | Benchmark | Trước | Sau |
  | --- | ---: | ---: |
  | MATH-500 | 7.9% | 48.1% |
  | GSM8K | 13.8% | 67.1% |
  | IFEval | 21.0% | 62.3% |
  | Tỉ lệ chạm giới hạn token (MATH-500) | 93.0% | 33.1% |

- **Diễn giải:** cải thiện chủ yếu đến từ việc **giảm vòng lặp (loop)**, không phải học thêm toán. Trên 1,152 mục practice, có 579 mục được "cứu", và 576 trong số đó vốn bị cắt cụt. Ngân sách 10 hoặc 25 pass cho mức tăng nhỏ hơn nhiều.
- **Đối chứng âm:** Gemma 3 270M, vốn hiếm khi loop, chỉ đạt 7.0–7.7% so với baseline 6.8%. Nghĩa là không có cải thiện đáng kể.
- **Tranh cãi về baseline:** khi chạy ở non-thinking mode, Qwen gốc được báo cáo đạt khoảng 43.95–47%. Các nguồn MindStudio và Kingy cho rằng thí nghiệm dùng thinking mode ở temperature thấp hơn khuyến nghị, điều kiện dễ gây loop. Các cấu hình này không khớp nhau, nên **chưa xác định được hiệu ứng gia tăng (incremental effect) của bản sửa**.

### 5.3 Neuron switch có điều kiện (Gemma 4 12B, dịch tiếng Ý)
Một người dùng Reddit nhờ Claude Opus 5.5 viết lại **8 MLP neuron** thành một "công tắc có điều kiện". Mục tiêu là chọn thì imperfect cho tình huống "đang diễn ra trong quá khứ thì bị gián đoạn". Mô hình được dùng một Python kernel và 50 forward pass; khoảng 92,000 trên 11.9B tham số bị thay đổi. Một linear probe ở layer giữa được dùng để định vị khái niệm ([Italian translation weight-edit experiment](../wiki/italian-translation-weight-edit-experiment.md)).

| Phương pháp | Test 1: còn dạng cũ | Test 2: còn dạng cũ | Controls bị hỏng | Unrelated không đổi /200 |
| --- | ---: | ---: | ---: | ---: |
| Base | 26% | 32% | — | 200 |
| System prompt | 4% | 2% | 49 | 82 |
| Diff-of-means ablation | 49% | 75% | 53 | 43 |
| LoRA | 12% | 23% | 0 | 120 |
| **Hand edit** | 5% | 16% | 2 | 182 |

**Synthesis:** việc probe tách được hai trường hợp không chứng minh mô hình dùng phân biệt đó một cách nhân quả. Ngoài ra, một người bản xứ phản bác chính lựa chọn ngữ pháp mà thí nghiệm nhắm tới.

### 5.4 Sửa thưa mạng lâm sàng
Cả 16 lỗi được phát hiện đều đưa được lỗi trong vùng cài đặt về 0 sau khi sửa. Trung vị **3 tham số** bị thay đổi; 14 bản sửa không tạo thêm quyết định sai nào. Tuy nhiên ([Clinical decision network weight audit](../wiki/clinical-decision-network-weight-audit.md)):
- **Lỗi số học:** mọi bản sửa đưa vào trọng số ≥ 10⁵ đều **thất bại ở fp16**. Overflow làm điểm số không xác định và bỏ sót các ca cần escalate.
- **So sánh baseline:** kiểm thử bằng protocol chính xác phân tách được cả 21 mạng trong 0.4 giây. Fine-tuning trên 200K ví dụ sửa được cả 18 mạng, nhưng thay đổi khoảng 432–433 tham số.

### 5.5 Inject tri thức và tín hiệu "done thinking"
- **Profile facts:** sửa 5/488 tensor của Qwen 0.8B để mô hình trả lời về hồ sơ cá nhân. Lưu ý đây là tỉ lệ số *tensor*, không phải số tham số. Nguồn không có đánh giá về việc tri thức khác có được bảo toàn hay không.
- **Qwen3.8-27B:** tăng gấp đôi một tín hiệu "done thinking", được báo cáo giảm 40% thinking token. Nguồn không cho biết chất lượng câu trả lời có được giữ hay không ([LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)).

### 5.6 Kết quả âm trên mô hình giọng nói
Một số người dùng báo cáo giai thoại (anecdotal):
- dựng một mô hình ASR từ đầu cho kết quả kém;
- sửa Pocket TTS để bắt chước giọng chỉ cho 1/20 mẫu tốt, trong khi cách dùng KV-cache với ngữ cảnh giọng nói cho kết quả tốt ([LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)).

---

## 6. Nhóm D — Chỉnh sửa do con người điều khiển theo luật

### 6.1 webWeightSpace: một DSL cho trọng số trong trình duyệt
Đây là demo WebGPU kết hợp WebLLM. Người dùng viết các dòng lệnh dạng `<selector> <op> [args]` ([Browser-based weight-space editing](../wiki/browser-weight-space-editing.md)):

| Op | Ví dụ | Cơ chế được báo cáo | Hiệu ứng được báo cáo |
| --- | --- | --- | --- |
| `mix a` | `* mix 0.1` | `w += a·(donor − w)` | Blend 10% sang Coder làm lặp prompt và hỏng code |
| `skip` | `layers.10-12 skip` | Đặt 0 cho 2 ma trận output mỗi layer | Câu trả lời vẫn trôi chảy nhưng kém tin cậy |
| `zero-heads` | `attn.o_proj zero-heads 0-6` | Đặt 0 cho cột o_proj của 7/14 head | Sinh ra nhiễu đa ngôn ngữ |
| `noise σ` | `layers.* noise 0.05` | `w ← w·(1+σ·N(0,1))` | 0.05 vẫn ổn; 0.12 làm câu trả lời lạc đề |
| `inject` | `layers.14-19 inject wedding 16` | Giải bài toán least squares cho value bias | Chủ đề "đám cưới" xuất hiện trong các câu trả lời không liên quan |

**Toán của `inject` (Reported):**
- Với embedding `e` và cường độ `c`, mục tiêu là $s = c\,e/\lVert e\rVert$.
- Qwen2.5-0.5B có 14 query head dùng chung 2 KV head 64 chiều, nên value bias có 128 phần tử.
- Dựng ma trận $M \in \mathbb{R}^{896\times128}$ bằng cách cộng 7 cột o_proj tương ứng, rồi giải $\arg\min_x \lVert Mx - s\rVert^2$ bằng normal equations với Cholesky float64.
- Kết quả là **activation steering được biên dịch vào trọng số**.
- Hiệu chỉnh: `ocean` ở cường độ 8 không thấy tác dụng; 12 cho văn bản trôi chảy theo chủ đề; 16 bắt đầu lặp; 24 sụp đổ.

**Triển khai:** shader đóng gói f16/bf16 và xử lý theo chunk 16 MB. Noise dùng PCG hash seed theo tên tensor kết hợp Box–Muller. Chỉ các shard bị sửa được ghi lại (khoảng 180 MB thay vì khoảng 1 GB).

### 6.2 Coarse normalization gain (một case study thất bại)
Das nhân trọng số normalization của các block cuối với một hệ số gain. Các block được chọn dựa trên khác biệt hidden-state giữa code và văn bản thường ([Coarse normalization-weight editing experiment](../wiki/coarse-normalization-weight-editing-experiment.md)):
- **Cải thiện ban đầu là ảo:** phép so khớp tên class đã bỏ sót các module normalization riêng của mô hình, nên bản sửa thực chất là **no-op**.
- **Baseline nhiễu:** sampling ở temperature 0.05 cho baseline dao động 4/8 đến 6/8.
- **Sau khi sửa lỗi:** Qwen2.5-Coder-1.5B tụt từ 4/8 xuống **0/8** ở cả gain 1.5 và 2.5.
- **Synthesis:** độ lớn hidden-state không đo được đóng góp gia tăng của một block, và khác biệt trung bình giữa code và văn bản không định vị được nhân quả.

---

## 7. Nhóm E — Đặt trong bức tranh model adaptation

Theo [Model adaptation mechanisms](../wiki/model-adaptation-mechanisms.md), các cơ chế khác nhau ở hai điểm: **thông tin nào chọn ra thay đổi**, và **hành vi mới nằm ở đâu**.

| Cơ chế | Thông tin chọn thay đổi | Hành vi nằm ở đâu | Ghi chú |
| --- | --- | --- | --- |
| Weight-space programming | LLM chẩn đoán và viết can thiệp | Tham số (thường thưa) | Việc gọi đây là "fine-tuning" hay không tùy cách định nghĩa |
| Gradient fine-tuning | Objective cộng ví dụ | Tham số | |
| LoRA | Gradient trên ma trận low-rank | Adapter, hoặc nhiều phần tử sau khi merge | Low-rank ≠ sparse |
| Distillation / Prompt baking | Supervision từ teacher hoặc từ chính mô hình khi có prompt | Tham số | Prompt baking dùng self-distillation bằng gradient |
| RAG | Tài liệu tại thời điểm truy vấn | Ngữ cảnh, không phải tham số | |
| ROME / MEMIT / MEND / hypernetwork | Gradient, editor được huấn luyện, hoặc mạng sinh trọng số | Tham số | Lịch sử của model editing |

---

## 8. Giao thức đánh giá và các bài học phương pháp luận

### 8.1 Failure mode đã được ghi nhận

| Failure mode | Nguồn minh họa |
| --- | --- |
| **Silent no-op**: bản sửa thực ra không chạy | [Coarse normalization](../wiki/coarse-normalization-weight-editing-experiment.md) |
| **Baseline nhiễu hoặc cấu hình sai** (thinking mode, temperature, giới hạn token) | [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md) |
| **Nhầm "gỡ vật cản" với "thêm năng lực"** | Qwen so với Gemma ([LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)) |
| **Ngữ nghĩa dựa trên prior** thay vì truy vết thật | [Dataset-prior audit](../wiki/weight-reading-dataset-prior-audit.md) |
| **Overflow fp16** khi trọng số được sửa quá lớn | [Clinical audit](../wiki/clinical-decision-network-weight-audit.md) |
| **Side effect**: hỏng chép chuỗi, làm theo chỉ dẫn kém, hỏng code | Video về copying task; [Browser editing](../wiki/browser-weight-space-editing.md) |
| **Tiêu chí chấm mơ hồ**: Frogger có được tính là Freeway không | [Weight reading](../wiki/reading-neural-network-weights-with-llms.md) |
| **Xác nhận sạch không đáng tin** cho mạng khỏe | [Clinical audit](../wiki/clinical-decision-network-weight-audit.md) |

### 8.2 Khuyến nghị gộp từ các nguồn (Reported recommendations)
1. **Measurement contract:** kiểm tra rằng tensor đích thực sự thay đổi. Dùng greedy decoding với seed cố định, và so kết quả từng task qua các lần chạy độc lập ([Coarse normalization](../wiki/coarse-normalization-weight-editing-experiment.md)).
2. **Baseline đúng cấu hình:** kiểm tra tỉ lệ hoàn thành và lặp, không chỉ độ đúng. Thử chỉnh mode, temperature và output limit trước khi sửa trọng số ([LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)).
3. **Ghi đủ ngân sách:** số forward pass, số lần chạy Python, số agent turn, và **chi phí tìm ra bản sửa**, không chỉ kích thước bản sửa (Williams).
4. **Controls cho weight reading:** ẩn nhãn, dùng dataset ít quen thuộc, hoán vị class, xáo trộn trọng số, và hỏi logit chính xác cho một input cụ thể. Nên preregister và có người chấm độc lập ([Dataset-prior audit](../wiki/weight-reading-dataset-prior-audit.md)).
5. **Kiểm tra trong arithmetic khi triển khai** (fp16, bf16) và recommission ([Clinical audit](../wiki/clinical-decision-network-weight-audit.md)).
6. **Model integrity:** pin hash, chữ ký và checksum; so với provenance đã ghi; chạy lại regression test cố định, kể cả hành vi refusal và policy (Williams, ITECS).
7. **So sánh công bằng** với inference control, fine-tuning và PEFT dưới cùng ngân sách. Lặp lại việc tìm bản sửa từ đầu và báo cáo cả các lần thất bại ([Continual learning](../wiki/continual-learning-and-recursive-improvement.md)).

---

## 9. Phê bình và tranh cãi chính

- **Bài toán quá dễ hoặc là chương trình nhỏ:** trọng số input của game "vẽ ra bản đồ"; nhiều bài toán có lời giải là chương trình xác định nhỏ, rồi chỉ được mã hóa thành trọng số ([Weight reading](../wiki/reading-neural-network-weights-with-llms.md), [LLM-directed editing](../wiki/llm-directed-neural-weight-editing.md)).
- **Không mới:** bình luận trên Hacker News, được trích qua Reddit, cho rằng bản sửa Qwen chỉ là **contrastive steering** quen thuộc.
- **Sycophancy:** một bài phê bình nói các lần thử chỉ dùng weights tương đương tung đồng xu, và việc can thiệp vào thành phần bị chỉ ra không làm thay đổi hành vi. Nhận định này chưa được kiểm chứng.
- **Comparator mạnh hơn cho Breakout:** một script ngắn được cho là vượt Astra. Chưa được kiểm chứng.
- **Recursive self-improvement:** @theojaffee và Masood đều cho rằng một bản sửa đơn lẻ **không** phải bằng chứng cho RSI.

---

## 10. Continual learning và recursive self-improvement

Theo [Continual learning and recursive improvement](../wiki/continual-learning-and-recursive-improvement.md):
- **Continual learning** đòi hỏi năng lực mới tích lũy được *và* năng lực cũ vẫn tồn tại. Sửa thưa vẫn có thể giao thoa qua các phép tính dùng chung. Nguồn báo cáo ROME và MEMIT xuống cấp khi sửa tuần tự.
- **Recursive self-improvement** đòi hỏi mô hình sau khi cải thiện phải **giỏi tạo ra cải thiện tiếp theo hơn** mô hình trước, trong điều kiện có kiểm soát qua nhiều thế hệ. Điểm task tăng không đủ để chứng minh điều này.
- Một editor cố định sửa một target riêng biệt không đáp ứng điều kiện nào trong hai điều kiện trên. STOP, Darwin Gödel Machine, Hyperagents và AlphaEvolve là các kết quả ở mức hệ thống phần mềm trong bối cảnh riêng của chúng.

---

## 11. Bảng tổng hợp các thí nghiệm

| Thí nghiệm | Mô hình editor | Target | Can thiệp | Feedback | Kết quả chính (Reported) | Giới hạn lớn |
| --- | --- | --- | --- | --- | --- | --- |
| Game ID | GPT-6 Astra | 4 PPO policy | Đọc | Không | 4/4, có tranh cãi về Frogger | Bài toán có thể dễ |
| Sycophancy | GPT-6 Astra | Cặp LM | Đọc | Attention pattern | 0/4 chỉ dùng weights; 3/3 khi có attention | Không phải weights-only |
| CNN prior audit | Claude Opus 5.5 | CNN ~125K | Đọc | Không | Thống kê cục bộ đúng, ngữ nghĩa sai | 1 seed, 1 lần chạy |
| Clinical audit | Claude Opus 5.5 | ReLU 433 tham số | Đọc + sửa | Không | 16/18 phát hiện; trung vị 3 tham số | Clearance kém, overflow fp16 |
| Kinetix | GPT-6 Astra | Car policy | Sửa 3.5% | Không | 1,024/1,024 so với 0/256 | Một level |
| MinAtar | GPT-6 Astra | Policy từ 0 | Viết | Không | > PPO 100M; Breakout gấp 20 lần PPO 500M | Có source code |
| Go 9×9 | GPT-6 Astra | Policy từ 0 | Viết (Python) | 0–50 pass | Thắng PPO cùng kích thước khi có 50 pass | Mô tả đối thủ chưa nhất quán |
| Legal citation | "Fable"/"Claude" | MLP ~100K | Viết | 0 hoặc 5,062 nhãn | 97.8–98.9% so với 94.6% | Attribution, protocol |
| Qwen loop | GPT-6 Astra | Qwen3.5-0.8B | Direction subtraction | 50 pass | MATH-500 7.9% → 48.1% | Cấu hình baseline |
| Italian tense | Claude Opus 5.5 | Gemma 4 12B | 8-neuron switch | 50 pass | 5–16% so với base 26–32% | Tự báo cáo, n chưa rõ |
| webWeightSpace | Con người | Qwen2.5-0.5B | DSL / inject | Quan sát trực tiếp | Steering có tác dụng phụ | Demo minh họa |
| Coarse gain | Con người | Qwen2.5-Coder-1.5B | Norm gain | Hidden-state statistics | 4/8 → 0/8 | Nhỏ, không có uncertainty |

---

## 12. Hướng mở

**Ứng dụng được đề xuất (Reported, prospective):** auditing, optimization, unlearning, model merging ([Weight-space programming](../wiki/weight-space-programming.md)), cùng với model maintenance và research automation ([Continual learning](../wiki/continual-learning-and-recursive-improvement.md)).

**Khoảng trống cần lấp (Synthesis):**
- benchmark có protocol công khai, chạy nhiều seed và có uncertainty;
- so sánh đúng cấu hình với fine-tuning, PEFT và steering dưới cùng ngân sách tìm kiếm;
- kiểm tra side effect diện rộng và sửa tuần tự;
- kiểm tra trong arithmetic khi triển khai;
- phép thử truy vết trực tiếp, ví dụ dự đoán logit, để tách lập luận khỏi prior.

---

## 13. Giới hạn của survey này

- **Chỉ dựa trên wiki đã biên dịch:** 11 concept, tất cả `draft`. Không mở thêm `raw/` vì không có trigger nào trong step 4 của wiki-query, và không chạy lại thí nghiệm nào.
- **Có nguồn trong `raw/` chưa được biên dịch nên không có mặt ở đây:** `2117313742891327994.md`, `2117350399271371113.md`, `2117406632229646689.md`, `sparks-of-weight-space-programming-explained.md`. Ngoài ra các thư mục ACAP SDK, `ultralytics` và `RAG-Anything` có vẻ thuộc chủ đề khác.
- **Phần lớn là nguồn thứ cấp:** blog, Reddit, X. Nhiều nguồn thiếu tác giả, ngày tháng hoặc protocol. Danh tính mô hình (GPT-6 Astra, Fable 5.1, Claude Opus 5.5…) là do nguồn tự ghi.
- **Absence ≠ false:** wiki không có nội dung về một chủ đề chỉ nghĩa là chủ đề đó chưa được biên dịch hoặc chưa được truy xuất, không có nghĩa là nó sai.

## Tài liệu tham khảo (concept trong wiki)
- [Weight-space programming](../wiki/weight-space-programming.md)
- [Reading neural network weights with LLMs](../wiki/reading-neural-network-weights-with-llms.md)
- [Dataset-prior audit of neural weight reading](../wiki/weight-reading-dataset-prior-audit.md)
- [Clinical decision network weight audit](../wiki/clinical-decision-network-weight-audit.md)
- [LLM-directed neural weight editing](../wiki/llm-directed-neural-weight-editing.md)
- [Italian translation weight-edit experiment](../wiki/italian-translation-weight-edit-experiment.md)
- [Writing Weights Index](../wiki/writing-weights-index.md)
- [Browser-based weight-space editing](../wiki/browser-weight-space-editing.md)
- [Coarse normalization-weight editing experiment](../wiki/coarse-normalization-weight-editing-experiment.md)
- [Model adaptation mechanisms](../wiki/model-adaptation-mechanisms.md)
- [Continual learning and recursive improvement](../wiki/continual-learning-and-recursive-improvement.md)

Footnote, locator và nguồn raw chi tiết nằm trong từng concept ở trên.
