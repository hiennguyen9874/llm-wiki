---
type: Synthesis
title: Evolution of CLIP-style vision–language pretraining
description: A synthesis of how CLIP-style research evolved through web-scale data, frozen towers, fine-grained interaction, auxiliary self-supervision, open scaling, loss redesign, metadata curation, multilinguality, and dense visual features.
tags: [multimodal-learning, vision-language-models, contrastive-learning, research-directions, synthesis]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:20:58Z }
sources:
  - id: radford-2021-clip
    resource: ../raw/2103.00020_CLIP/clip_paper.tex
    title: Learning Transferable Visual Models From Natural Language Supervision
  - id: align-2021
    resource: ../raw/2102.05918_ALIGN/align.tex
    title: Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision
  - id: zhai-2021-lit
    resource: ../raw/2111.07991_Vision Text Dual Encoder/c.tex
    title: "LiT: Zero-Shot Transfer with Locked-image Text Tuning"
  - id: yao-2022-filip
    resource: ../raw/2111.07783_FILIP/filip_arxiv.tex
    title: "FILIP: Fine-grained Interactive Language-Image Pre-Training"
  - id: li-2022-declip
    resource: ../raw/2110.05208_DeCLIP/declip.tex
    title: "Supervision Exists Everywhere: A Data Efficient Contrastive Language-Image Pre-training Paradigm"
  - id: mu-2022-slip
    resource: ../raw/2112.12750_SLIP/slip.tex
    title: "SLIP: Self-supervision Meets Language-Image Pre-training"
  - id: cherti-2022-openclip-scaling
    resource: ../raw/2212.07143_OpenCLIP-Scaling/main.tex
    title: Reproducible scaling laws for contrastive language-image learning
  - id: zhai-2023-siglip
    resource: ../raw/2303.15343_SigLIP.md
    title: Sigmoid Loss for Language Image Pre-Training
  - id: xu-2024-metaclip
    resource: ../raw/2309.16671_MetaCLIP/iclr2024_conference.tex
    title: Demystifying CLIP Data
  - id: tschannen-2025-siglip2
    resource: ../raw/2502.14786_SigLIP2/document.tex
    title: "SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"
  - id: chuang-2025-meta-clip-2
    resource: ../raw/2507.22062_MetaCLIP 2/paper.tex
    title: "Meta CLIP 2: A Worldwide Scaling Recipe"
---

# Evolution of CLIP-style vision–language pretraining

Chuỗi CLIP → ALIGN → LiT → FILIP → SLIP/DeCLIP → OpenCLIP → SigLIP → MetaCLIP → SigLIP 2 → Meta CLIP 2 không phải một phả hệ tuyến tính. Nó là nhiều nhánh nghiên cứu cùng sửa các nút thắt của dual encoder: **quy mô và nhiễu dữ liệu, cách huấn luyện hai tower, độ chi tiết của alignment, hiệu quả supervision, khả năng scale, hàm loss, curation, đa ngôn ngữ và đặc trưng dense**. Đến năm 2025, hai hướng nổi bật hội tụ khác nhau: SigLIP 2 mở rộng objective và representation; Meta CLIP 2 mở rộng data recipe ra toàn cầu.

## Bản đồ phương pháp

| Mốc | Nút thắt được nhắm tới | Thay đổi chính | Ý nghĩa phát triển |
|---|---|---|---|
| [CLIP](clip-natural-language-image-pretraining.md) | Học thị giác có vocabulary cố định | Hai encoder, symmetric contrastive softmax trên ảnh–text web; prompt biến text embedding thành zero-shot classifier | Đặt giao diện nền: shared embedding, retrieval và open-vocabulary classification[^radford-2021-clip] |
| [ALIGN](align-noisy-image-text-learning.md) | Dữ liệu caption sạch khó mở rộng | Huấn luyện từ đầu trên 1.8B cặp alt-text được lọc nhẹ | Chứng minh scale có thể bù một phần cho nhiễu, nhưng không làm curation trở nên vô nghĩa[^align-2021] |
| [LiT](lit-locked-image-tuning.md) | Joint training đắt và có thể làm hỏng visual representation tốt | Khóa image tower pretrained, chỉ học text tower để đọc không gian ảnh | Tách visual pretraining khỏi language alignment; tiết kiệm gradient/memory, mạnh cho zero-shot nhưng không luôn tối ưu retrieval[^zhai-2021-lit] |
| [FILIP](filip-fine-grained-interactive-language-image-pretraining.md) | Một global vector bỏ mất tương ứng patch–word | Late interaction hai chiều: mean-MaxSim giữa token ảnh và token text | Đưa alignment xuống mức cục bộ mà vẫn mã hóa hai modality độc lập; đổi lại similarity/indexing đắt hơn[^yao-2022-filip] |
| [SLIP](slip-self-supervised-language-image-pre-training.md) | Caption supervision chưa học đủ cấu trúc thị giác | Thêm image-only self-supervision qua cùng image encoder | Joint multimodal + unimodal learning cải thiện transfer, nhưng cần thêm view và compute[^mu-2022-slip] |
| [DeCLIP](declip-data-efficient-contrastive-language-image-pretraining.md) | Phụ thuộc quá nhiều cặp ảnh–text | Thêm SimSiam, MLM, multi-view cross-modal và nearest-neighbor positives | Khai thác supervision “ở mọi nơi” để tăng data efficiency; recipe phức tạp và từng step đắt hơn[^li-2022-declip] |
| [OpenCLIP scaling](openclip-reproducible-contrastive-language-image-scaling.md) | Kết quả scale của CLIP khó tái lập do WIT riêng | Open code/data; quét model size, dataset size và samples seen | Scaling là đồng thiết kế ba trục; đường luật phụ thuộc task và data distribution, không có một exponent chung[^cherti-2022-openclip-scaling] |
| [SigLIP](siglip-sigmoid-contrastive-language-image-pretraining.md) | Global softmax/all-gather và batch rất lớn | Binary sigmoid loss độc lập cho mọi cặp positive/negative | Loss dễ chunk/shard hơn, hiệu quả ở batch vừa; vẫn coi semantic false negatives là âm[^zhai-2023-siglip] |
| [MetaCLIP](metaclip-metadata-curated-language-image-pretraining.md) | “Bí quyết dữ liệu” của CLIP thiếu minh bạch | Vocabulary WordNet/Wikipedia, substring matching và cân bằng head–tail, không dùng CLIP teacher filter | Chuyển trọng tâm từ thêm dữ liệu sang kiểm soát distribution; trong ablation, 400M balanced tốt hơn pool 1.6B unbalanced[^xu-2024-metaclip] |
| [SigLIP 2](siglip2-multilingual-vision-language-encoders.md) | Global embedding chưa đủ multilingual, grounding và dense tasks | Giữ sigmoid loss; thêm tokenizer đa ngôn ngữ, decoder caption/grounding, self-distillation, masked patches, active curation và NaFlex | Encoder trở thành representation backbone đa nhiệm, hỗ trợ cả global và local semantics[^tschannen-2025-siglip2] |
| [Meta CLIP 2](meta-clip-2-worldwide-clip-scaling.md) | Curation tiếng Anh không đại diện thế giới | Metadata và balancing riêng theo ngôn ngữ; native-language data; scale exposure và capacity | Multilinguality là bài toán data distribution + tokenizer + compute + capacity, không chỉ dịch caption hay thay text encoder[^chuang-2025-meta-clip-2] |

## Các trục tiến hóa chính

### 1. Từ “scale thô” sang “scale có cấu trúc”

ALIGN cho thấy lượng dữ liệu rất lớn có thể thắng tập nhỏ sạch hơn trong thiết lập được báo cáo.[^align-2021] OpenCLIP sau đó chỉ ra rằng dataset size, samples seen và model capacity phải tăng phối hợp, đồng thời classification và retrieval có thể có scaling trend khác nhau.[^cherti-2022-openclip-scaling] MetaCLIP và Meta CLIP 2 tiến thêm một bước: scale không chỉ là số cặp mà là **phân phối khái niệm và ngôn ngữ nào được nhìn thấy bao nhiêu lần**.[^xu-2024-metaclip][^chuang-2025-meta-clip-2]

### 2. Từ một objective tối giản sang supervision tổ hợp

CLIP tạo baseline tối giản bằng image–text contrast. SLIP thêm self-supervision phía ảnh; DeCLIP thêm cả image/text self-supervision, multi-view và neighbor positives.[^mu-2022-slip][^li-2022-declip] SigLIP thay chính cơ chế contrastive normalization.[^zhai-2023-siglip] SigLIP 2 kết hợp sigmoid alignment với captioning, grounding, self-distillation và masked-patch prediction theo giai đoạn.[^tschannen-2025-siglip2]

**Suy luận tổng hợp:** hướng phát triển không phải bỏ contrastive learning, mà giữ nó làm “xương sống” global alignment và gắn thêm các objective chuyên trách cho semantics cục bộ, invariance, ngôn ngữ và dense transfer.

### 3. Từ joint training mặc định sang tái sử dụng và module hóa

LiT chứng minh một image encoder mạnh có thể được giữ nguyên rồi gắn khả năng ngôn ngữ bằng text tuning.[^zhai-2021-lit] SigLiT sau đó ghép nguyên tắc này với sigmoid loss.[^zhai-2023-siglip] Nhánh này mở đường cho việc coi vision backbone là tài sản tái sử dụng, thay vì luôn phải pretrain hai tower từ đầu.

### 4. Từ global semantics sang local/dense semantics

FILIP đưa patch–word late interaction vào score contrastive.[^yao-2022-filip] SigLIP 2 vẫn giữ global retrieval/classification nhưng huấn luyện unpooled visual tokens bằng grounding, self-distillation và masked prediction.[^tschannen-2025-siglip2]

**Suy luận tổng hợp:** có hai chiến lược bổ sung nhau: (a) làm interaction chi tiết hơn ở lúc so khớp như FILIP; hoặc (b) làm từng visual token giàu nghĩa hơn trong pretraining như SigLIP 2. Chiến lược (a) tăng chi phí scoring/index; chiến lược (b) giữ inference global rẻ hơn nhưng đòi recipe pretraining phức tạp.

### 5. Từ English-centric zero-shot sang multilingual và culturally broader transfer

ALIGN đã thử hơn 100 ngôn ngữ và LiT khảo sát multilingual tuning, nhưng thế hệ mới xử lý bài toán có hệ thống hơn.[^align-2021][^zhai-2021-lit] SigLIP 2 phối hợp tokenizer, mixture dữ liệu và auxiliary tasks; Meta CLIP 2 xây metadata và ngưỡng cân bằng riêng theo ngôn ngữ, đồng thời cho thấy cần tăng cả exposure lẫn model capacity để tránh đánh đổi tiếng Anh.[^tschannen-2025-siglip2][^chuang-2025-meta-clip-2]

## Hai nhánh hội tụ năm 2025

- **SigLIP 2 là hướng model/objective-centric:** mục tiêu là một encoder đa ngôn ngữ có global embedding tốt đồng thời cung cấp dense features, localization và VLM transfer. Công cụ chính là multi-task staged training và cải tiến representation.
- **Meta CLIP 2 là hướng data-centric:** mục tiêu là mở CLIP ra dữ liệu native-language toàn cầu mà vẫn giữ chất lượng tiếng Anh. Công cụ chính là metadata, balancing, tokenizer, training exposure và capacity.
- Hai bài không tạo so sánh nhân quả trực tiếp: chúng khác loss, dữ liệu, backbone, auxiliary objectives và protocol. Không thể kết luận recipe nào “tốt hơn” chỉ từ bảng benchmark chéo bài.[^tschannen-2025-siglip2][^chuang-2025-meta-clip-2]

## Hướng phát triển tiếp theo

Các hướng sau là **suy luận tổng hợp** từ chuỗi bằng chứng trên, chưa phải đồng thuận đã được kiểm chứng độc lập:

1. **Đồng tối ưu data–objective–capacity:** scaling law tương lai cần mô hình hóa chất lượng/cân bằng dữ liệu, không chỉ FLOPs và số mẫu.
2. **Unified global–dense encoder:** một backbone phục vụ zero-shot, retrieval, grounding, segmentation và VLM connector mà không hy sinh chi phí inference.
3. **Fine-grained alignment hiệu quả:** nén token, token pruning hoặc coarse-to-fine scoring để giữ lợi ích kiểu FILIP ở corpus lớn.
4. **Positive/negative semantics tốt hơn:** giảm false negatives và tận dụng nhiều caption, paraphrase, neighbor hay teacher signal mà không làm recipe mất ổn định.
5. **Multilingual curation có kiểm toán:** đo riêng coverage, cultural bias, PII, copyright, leakage và long-tail theo ngôn ngữ thay vì chỉ báo cáo điểm trung bình.
6. **Tái sử dụng tower và modular training:** chọn linh hoạt freeze/unfreeze theo mục tiêu; zero-shot classification và retrieval có thể cần policy khác nhau.
7. **Pareto thực tế:** báo cáo đồng thời quality, training compute, memory, index size, latency và data-governance cost.

## Giới hạn bằng chứng

- Thứ tự mũi tên là khung trình bày, không phản ánh đầy đủ thời gian hay quan hệ kế thừa; ALIGN có preprint sớm hơn CLIP và nhiều nhánh phát triển song song.
- Các con số giữa bài không so sánh trực tiếp vì khác dữ liệu, model, samples seen, prompt, benchmark và protocol.
- Phần lớn bằng chứng là thí nghiệm do chính nhóm tác giả báo cáo; thiếu kiểm chứng độc lập thống nhất trên cùng data/compute budget.
- Scale và curation web không tự giải quyết bias, PII, copyright, benchmark leakage hay misuse; các pipeline chỉ cung cấp biện pháp giảm thiểu có giới hạn.

## Relationships

- Synthesizes: [CLIP](clip-natural-language-image-pretraining.md), [ALIGN](align-noisy-image-text-learning.md), [LiT](lit-locked-image-tuning.md), [FILIP](filip-fine-grained-interactive-language-image-pretraining.md), [SLIP](slip-self-supervised-language-image-pre-training.md), [DeCLIP](declip-data-efficient-contrastive-language-image-pretraining.md), [OpenCLIP scaling](openclip-reproducible-contrastive-language-image-scaling.md), [SigLIP](siglip-sigmoid-contrastive-language-image-pretraining.md), [MetaCLIP](metaclip-metadata-curated-language-image-pretraining.md), [SigLIP 2](siglip2-multilingual-vision-language-encoders.md), and [Meta CLIP 2](meta-clip-2-worldwide-clip-scaling.md).
- Related: [Recent vision-language research directions](recent-vision-language-research-directions.md) broadens the frontier beyond CLIP-style pretraining to adaptation, document retrieval, efficiency, and safety.
- Synthesized by: [Vision-language task-to-model map](vision-language-task-to-model-map.md), which reorganizes the model lineage by downstream problem and selection boundary.

[^radford-2021-clip]: Radford et al., “Learning Transferable Visual Models From Natural Language Supervision” (2021), [source manuscript](../raw/2103.00020_CLIP/clip_paper.tex).
[^align-2021]: Jia et al., “Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision” (2021), [source manuscript](../raw/2102.05918_ALIGN/align.tex).
[^zhai-2021-lit]: Zhai et al., “LiT: Zero-Shot Transfer with Locked-image Text Tuning” (2021), [source manuscript](../raw/2111.07991_Vision%20Text%20Dual%20Encoder/c.tex).
[^yao-2022-filip]: Yao et al., “FILIP: Fine-grained Interactive Language-Image Pre-Training” (2022), [source manuscript](../raw/2111.07783_FILIP/filip_arxiv.tex).
[^li-2022-declip]: Li et al., “Supervision Exists Everywhere” (2022), [source manuscript](../raw/2110.05208_DeCLIP/declip.tex).
[^mu-2022-slip]: Mu et al., “SLIP: Self-supervision Meets Language-Image Pre-training” (2022), [source manuscript](../raw/2112.12750_SLIP/slip.tex).
[^cherti-2022-openclip-scaling]: Cherti et al., “Reproducible scaling laws for contrastive language-image learning” (2022), [source manuscript](../raw/2212.07143_OpenCLIP-Scaling/main.tex).
[^zhai-2023-siglip]: Zhai et al., “Sigmoid Loss for Language Image Pre-Training” (2023), [source](../raw/2303.15343_SigLIP.md).
[^xu-2024-metaclip]: Xu et al., “Demystifying CLIP Data” (2024), [source manuscript](../raw/2309.16671_MetaCLIP/iclr2024_conference.tex).
[^tschannen-2025-siglip2]: Tschannen et al., “SigLIP 2” (2025), [source manuscript](../raw/2502.14786_SigLIP2/document.tex).
[^chuang-2025-meta-clip-2]: Chuang et al., “Meta CLIP 2: A Worldwide Scaling Recipe” (2025), [source manuscript](../raw/2507.22062_MetaCLIP%202/paper.tex).
