---
type: Concept
title: Pretraining scaling for beginners
description: A beginner-first explanation of how parameters, training tokens, and FLOPs trade off during dense-Transformer pretraining, including the Chinchilla allocation and its contrast with Kaplan.
tags: [pre-training, scaling-laws, chinchilla, kaplan, training-compute, beginners]
status: stable
created: 2026-08-11
generated: { by: llm-wiki-agent/1, at: 2026-08-11T17:07:19+07:00 }
sources:
  - id: chinchilla-summary
    resource: ../raw/Chinchilla.md
    title: Chinchilla overview (summary)
  - id: kaplan-scaling-laws-2020-v1
    resource: ../raw/arXiv-2001.08361v1/main.tex
    title: Scaling Laws for Neural Language Models
---

# Pretraining scaling for beginners

Khi lên kế hoạch **pretraining** một dense Transformer, không thể hỏi riêng “model bao nhiêu parameters?”: chất lượng cuối cùng phụ thuộc đồng thời vào số parameters $N$, số training tokens $D$, và training compute $C$. Với cùng $C$, Chinchilla cho trực giác thực nghiệm rằng nên tăng gần cân bằng cả $N$ lẫn $D$, thay vì chỉ làm model lớn hơn. Đây là bài toán phân bổ ngân sách, không phải định luật vật lý hay một công thức deployment hoàn chỉnh.[^chinchilla-summary]

## 1. Ba đại lượng cần phân biệt

| Ký hiệu | English term | Nghĩa là gì? | Nếu tăng nó |
| --- | --- | --- | --- |
| $N$ | **parameter count** | Số trọng số model phải học. Đây là một thước đo gần đúng của **capacity**. | Model có thể biểu diễn quy luật phức tạp hơn, nhưng mỗi token training tốn hơn và inference thường đắt hơn. |
| $D$ | **training tokens** | Tổng số token model thực sự nhìn thấy trong pretraining. | Model có nhiều tín hiệu học hơn, nhưng phải chạy training lâu hơn. |
| $C$ | **training compute** | Tổng phép tính dùng cho pretraining, thường đo bằng **FLOPs**. | Có thể mua thêm $N$, thêm $D$, hoặc cả hai. |

**Token** không phải là word. Tokenizer có thể tách một word thành nhiều token, nên $D$ phải luôn được hiểu theo tokenizer và cách đếm của run đó.

> [!note] Capacity không phải chất lượng
> Một model có $N$ lớn có capacity lớn hơn, nhưng capacity chưa được biến thành chất lượng nếu model chỉ thấy quá ít training tokens. Ngược lại, một model rất nhỏ vẫn có giới hạn dù được train lâu.

## 2. Vì sao training FLOPs xấp xỉ $6ND$?

Một **FLOP** là một phép tính dấu phẩy động. Với dense Transformer, một parameter được dùng gần như cho mỗi token trong forward pass. Theo quy ước ước lượng phổ biến trong các scaling-law này, một multiply-add được tính khoảng hai FLOPs; forward pass vì thế có chi phí cỡ $2ND$. Backward pass cần thêm tính toán cho gradient, nên tổng training cost được xấp xỉ:

$$
C \approx 6ND.
$$

Đây là một **accounting approximation**, hữu ích để so sánh và lập kế hoạch, không phải chi phí đúng đến từng FLOP. Context length, attention, embeddings, activation recomputation, sparse routing, hardware utilization và cách đếm parameters đều có thể làm chi phí thực lệch đi. Kaplan dùng dạng $C\approx6NBS$, trong đó $B$ là batch size tính theo tokens và $S$ là số update steps; vì $D=BS$, hai cách viết cùng trực giác $C\propto ND$.[^kaplan-scaling-laws-2020-v1]

### Ví dụ trực giác

Giả sử một run có $N=10\text{B}$ và $D=200\text{B}$ tokens. Bỏ qua đơn vị tiền tố, tích $ND$ là $2\times10^{21}$; training compute xấp xỉ $1.2\times10^{22}$ FLOPs.

Nếu giữ nguyên compute và tăng model lên $20\text{B}$ parameters, ta chỉ còn khoảng $100\text{B}$ tokens. Model lớn gấp đôi nhưng mỗi parameter có ít dữ liệu hơn để học. Nếu thay vào đó tăng tokens lên $400\text{B}$, model phải giảm về khoảng $5\text{B}$ parameters. Không lựa chọn nào luôn đúng: cần cân bằng hai loại thiếu hụt bên dưới.

## 3. Hai cách một model bị giới hạn

Hãy tách final validation loss thành hai phần trực giác:

1. **Finite-capacity limitation:** $N$ quá nhỏ. Model không có đủ capacity để nén và biểu diễn các regularity của data, kể cả khi train thêm.
2. **Finite-data limitation:** $D$ quá nhỏ. Model có nhiều weights nhưng chưa nhận đủ training signal để tận dụng chúng.

Chinchilla mô hình hóa hai hiệu ứng bằng fitted loss law:

$$
\hat L(N,D)=E+\frac{A}{N^\alpha}+\frac{B}{D^\beta}.
$$

- $E$ là phần loss không thể giảm tiếp trong model này.
- $A/N^\alpha$ giảm khi tăng **parameter count**: phạt vì thiếu capacity.
- $B/D^\beta$ giảm khi tăng **training tokens**: phạt vì thiếu data/training exposure.
- $A$, $B$, $\alpha$, $\beta$ là các giá trị được fit từ experiments, không phải constants phổ quát.[^chinchilla-summary]

Vì $C\approx6ND$, fixed compute buộc ta đánh đổi hai phần loss: tăng $N$ làm phần capacity giảm nhưng bắt buộc giảm $D$, khiến phần data tăng; và ngược lại. Trên một **IsoFLOP curve** (nhiều run có cùng $C$), loss thường có dạng chữ U: model quá nhỏ ở một đầu, model quá lớn nhưng undertrained ở đầu kia. Đáy chữ U là **compute-optimal allocation**.

## 4. Trực giác Chinchilla: scale cả model và data

Tối ưu fitted loss trên với ràng buộc $C=6ND$ cho kết quả:

$$
N_{\mathrm{opt}}\propto C^{\frac{\beta}{\alpha+\beta}},
\qquad
D_{\mathrm{opt}}\propto C^{\frac{\alpha}{\alpha+\beta}}.
$$

Trong experiments của Chinchilla, hai exponents này gần $0.5$. Ba phương pháp estimate trong nguồn lần lượt cho cặp exponent khoảng $(0.50,0.50)$, $(0.49,0.51)$ và $(0.46,0.54)$. Vì vậy, quy tắc dễ nhớ là:

$$
N_{\mathrm{opt}}\propto C^{0.5},
\qquad
D_{\mathrm{opt}}\propto C^{0.5}.
$$

Nếu compute tăng $4\times$, hãy hình dung tăng gần $2\times$ parameters **và** $2\times$ training tokens. Khi đó $ND$ tăng $4\times$. Điều này không nói rằng mọi run phải có chính xác hai số mũ $0.5$; nó tóm tắt fit trong phạm vi và setting mà Chinchilla khảo sát.[^chinchilla-summary]

### Heuristic “20 tokens per parameter”

Một cách chuyển trực giác thành kế hoạch ban đầu là:

$$
D_{\mathrm{opt}}\approx20N.
$$

Với $N$ tính bằng parameters và $D$ tính bằng tokens:

| Model size | Training tokens theo heuristic |
| ---: | ---: |
| $1\text{B}$ | $20\text{B}$ |
| $7\text{B}$ | $140\text{B}$ |
| $70\text{B}$ | $1.4\text{T}$ |
| $175\text{B}$ | $3.5\text{T}$ |

Ví dụ nổi bật là Chinchilla: $70\text{B}$ parameters và khoảng $1.3$–$1.4\text{T}$ tokens, gần bằng $20$ tokens per parameter. Ở training compute gần Gopher, nguồn báo cáo model này nhỏ hơn $4\times$ nhưng được train trên khoảng $4\times$ tokens và đạt loss/downstream results tốt hơn trong đánh giá được báo cáo.[^chinchilla-summary]

> [!warning] Đừng biến heuristic thành luật
> Ratio $20$ phụ thuộc vào architecture, tokenizer, data quality và distribution, optimizer, schedule, parameter-count convention, cũng như compute range dùng để fit. Đặc biệt, “$D$ tokens” không đánh giá được duplicate, noise hoặc mức độ phù hợp của data.

## 5. Kaplan và Chinchilla: khác ở đâu?

Cả hai đều là **empirical scaling laws**, nhưng fit khác nhau nên đưa đến recommendation khác nhau.

| | Kaplan (2020) | Chinchilla (2022) |
| --- | --- | --- |
| Câu hỏi | Phân bổ compute hiệu quả theo fitted laws của experiments đó | Phân bổ fixed pretraining compute giữa $N$ và $D$ |
| Kết luận về scale | $N_{\mathrm{opt}}\propto C^{0.73}$; serial steps tăng rất ít | $N_{\mathrm{opt}}$ và $D_{\mathrm{opt}}$ đều gần $C^{0.5}$ |
| Trực giác | Ưu tiên model lớn hơn và early stopping trước convergence | Nhiều frontier models khi đó quá lớn so với số tokens đã train |

Không nên nói Kaplan “sai” theo nghĩa toán học. Nó là kết quả fit từ decoder-only Transformers, WebText2, 1,024-token context và setting training riêng; chính paper cũng nêu giới hạn khi extrapolate. Chinchilla là fit sau đó, với cách ước lượng và experimental evidence khác, nên **contradicts** Kaplan về allocation trong fixed pretraining compute. Khi đọc một scaling rule, câu hỏi đúng là: *nó được fit trên architecture, data, optimizer, compute range và objective nào?*[^kaplan-scaling-laws-2020-v1][^chinchilla-summary]

## 6. Compute-optimal không đồng nghĩa deployment-optimal

Chinchilla tối ưu final loss khi **pretraining FLOPs** bị cố định. Sản phẩm thực tế còn có lifetime cost:

$$
C_{\mathrm{lifetime}} = C_{\mathrm{pretraining}} + C_{\mathrm{inference}}.
$$

Nếu một model phục vụ rất nhiều generated tokens, inference cost có thể quan trọng hơn chi phí train một lần. Khi đó, có thể hợp lý để dùng model nhỏ hơn, train trên nhiều tokens hơn heuristic Chinchilla, rồi đổi thêm training cost lấy serving cost thấp hơn. Cách nói **overtraining relative to Chinchilla** chỉ có nghĩa là vượt token allocation tối ưu cho mục tiêu fixed-pretraining-compute; nó không tự động có nghĩa **overfitting**.[^chinchilla-summary]

Ngoài ra, Chinchilla allocation là cho dense-model pretraining. Với **Mixture-of-Experts**, active parameters, total parameters, routing và communication tạo thêm các câu hỏi về compute accounting; không nên áp dụng $6ND$ hay $20N$ một cách máy móc.

## 7. Cách dùng trong một planning pass

1. **Chốt objective.** Bạn tối ưu validation loss ở fixed pretraining budget, hay tổng training + inference cost?
2. **Đếm đúng $N$ và $D$.** Ghi rõ total hay non-embedding parameters, tokenizer và số tokens thực đã processed.
3. **Ước lượng budget.** Với dense baseline, dùng $C\approx6ND$ như một first-order estimate; sau đó kiểm tra memory, throughput và context-length overhead trên hardware thật.
4. **Chọn một point khởi đầu.** Nếu chưa có scaling experiments của riêng mình, Chinchilla ratio là baseline hợp lý để so sánh, không phải đích bắt buộc.
5. **Chạy small-scale sweep.** Giữ compute gần nhau, thay đổi $N$ và $D$, rồi đo held-out loss. Nếu data quality, architecture hoặc optimizer đổi, frontier cũng có thể đổi.
6. **Tính serving.** So sánh latency, memory và cost per generated token trước khi chốt model size cho deployment.

## 8. Điều cần nhớ

- $N$ quyết định gần đúng **capacity**; $D$ quyết định mức độ capacity được train; $C$ là ngân sách buộc hai thứ phải trade off.
- Với dense Transformer, $C\approx6ND$ là ước lượng tiện dụng, không phải cost model hoàn chỉnh.
- Chinchilla cho trực giác: ở fixed pretraining compute, tăng gần cân bằng parameters và tokens thường tốt hơn việc chỉ tăng parameters.
- $D\approx20N$ là empirical heuristic, không phải universal constant.
- Kaplan là quan điểm scaling-law cũ khác biệt; sự khác nhau nhắc ta không extrapolate một fit vượt quá evidence của nó.
- Quyết định cuối phải phân biệt **training-optimal** với **deployment-optimal**.

## Relationships

- **Explains:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md) for beginners.
- **Contrasts:** [Kaplan compute-optimal training allocation](kaplan-compute-optimal-training-allocation.md), whose fitted allocation favors parameter growth more strongly.
- **Uses:** [Empirical language-model loss scaling laws](empirical-language-model-loss-scaling-laws.md) for the original Kaplan experimental scope and compute convention.
- **Validates context from:** [Chinchilla training validation and evaluation](chinchilla-training-validation-and-evaluation.md).

[^chinchilla-summary]: “Chinchilla overview (summary),” [raw source](../raw/Chinchilla.md), especially Sections 3–13. This is a secondary Vietnamese-language summary; the primary Chinchilla paper has not been independently ingested into this wiki.

[^kaplan-scaling-laws-2020-v1]: Jared Kaplan et al., “Scaling Laws for Neural Language Models,” [source](../raw/arXiv-2001.08361v1/main.tex), especially Sections 4–6 and Appendix A.
