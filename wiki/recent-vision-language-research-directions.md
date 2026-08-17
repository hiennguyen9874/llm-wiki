---
type: Synthesis
title: Recent vision-language research directions
description: A synthesis of 2024–2026 vision–language methods and emerging directions in multilingual data, dense alignment, efficient adaptation, visual document retrieval, model efficiency, and policy-conditioned safety.
tags: [multimodal-learning, vision-language-models, research-directions, synthesis]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:20:58Z }
sources:
  - id: chuang-2025-meta-clip-2
    resource: ../raw/2507.22062_MetaCLIP 2/paper.tex
    title: "Meta CLIP 2: A Worldwide Scaling Recipe"
  - id: tschannen-2025-siglip2
    resource: ../raw/2502.14786_SigLIP2/document.tex
    title: "SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"
  - id: cao-2026-tipsv2
    resource: ../raw/2604.12012_TIPSv2/main.tex
    title: "TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: Cascade Prompt Learning for Vision-Language Model Adaptation
  - id: faysse-2025-colpali-camera-ready
    resource: ../raw/2407.01449_ColPali/iclr2025_conference.tex
    title: "ColPali: Efficient Document Retrieval with Vision Language Models"
  - id: teiletche-2026-modernvbert-camera-ready
    resource: ../raw/2510.01149_ColModernVBert/iclr2026_conference.tex
    title: "ModernVBERT: Towards Smaller Visual Document Retrievers"
  - id: zeng-2025-shieldgemma2
    resource: ../raw/2504.01081_ShieldGemma2/main.tex
    title: "ShieldGemma 2: Robust and Tractable Image Content Moderation"
---

# Recent vision-language research directions

Các công trình 2024–2026 trong wiki cho thấy trọng tâm đang dịch chuyển từ chỉ tối ưu biểu diễn ảnh–văn bản toàn cục sang xây dựng hệ thống **đa ngôn ngữ, hiểu cục bộ, thích nghi theo miền, truy hồi trực tiếp trên tài liệu trực quan, nhỏ hơn và có lớp kiểm soát an toàn**. Đây là tổng hợp từ các bài báo được lưu trong kho; không phải tổng quan toàn bộ lĩnh vực.

## Các nhóm phương pháp

### 1. Mở rộng dữ liệu đa ngôn ngữ và đa văn hóa

[Meta CLIP 2](meta-clip-2-worldwide-clip-scaling.md) xây metadata riêng theo từng ngôn ngữ, nhận diện ngôn ngữ rồi cân bằng khái niệm head–tail theo ngưỡng riêng; kết quả của bài báo cho thấy dữ liệu toàn cầu chỉ phát huy đồng thời trên tiếng Anh và đa ngôn ngữ khi tăng cả lượng mẫu đã thấy lẫn năng lực mô hình.[^chuang-2025-meta-clip-2] [SigLIP 2](siglip2-multilingual-vision-language-encoders.md) chọn hướng khác: giữ sigmoid contrastive loss nhưng bổ sung tokenizer đa ngôn ngữ, captioning/grounding, tự chưng cất và masked-patch prediction.[^tschannen-2025-siglip2]

**Hàm ý tổng hợp:** đa ngôn ngữ không còn là thay text encoder hoặc dịch caption đơn thuần; hướng phát triển là phối hợp curation theo ngôn ngữ, tokenizer, phân bổ dữ liệu, scale và đánh giá thiên lệch địa lý–văn hóa.

### 2. Từ alignment toàn cục sang patch–text và đặc trưng dense

[SigLIP 2](siglip2-multilingual-vision-language-encoders.md) dùng decoder tạm thời cho captioning và grounding, sau đó thêm self-distillation và masked-patch prediction để cải thiện token ảnh chưa pooling.[^tschannen-2025-siglip2] [TIPSv2](tipsv2-patch-text-aligned-vision-language-pretraining.md) giám sát cả patch bị che lẫn patch nhìn thấy bằng iBOT++, kết hợp caption nhiều mức chi tiết và head-only EMA để giảm tham số huấn luyện.[^cao-2026-tipsv2]

**Hàm ý tổng hợp:** encoder vision–language tương lai có xu hướng phục vụ đồng thời retrieval/classification toàn cục và segmentation, localization, grounding ở mức patch; objective đa nhiệm và distillation cục bộ trở thành phần chính của pretraining.

### 3. Thích nghi tham số thấp theo miền

[CasPL](caspl-cascade-prompt-learning.md) tách thích nghi thành hai giai đoạn: chưng cất tri thức miền từ teacher vào boosting prompts bằng ảnh không nhãn, đóng băng chúng, rồi học adapting prompts bằng dữ liệu few-shot. Phương pháp có thể bọc CoOp, CoCoOp, MaPLe và PromptSRC mà không thay trọng số CLIP.[^wu-2024-caspl]

**Hàm ý tổng hợp:** hướng đáng chú ý là module hóa tri thức miền và tri thức nhiệm vụ, tận dụng dữ liệu không nhãn và teacher lớn nhưng giữ chi phí suy luận gần mô hình gốc. Điểm còn mở là kiểm chứng ngoài phân loại ảnh và ngoài họ CLIP.

### 4. Truy hồi tài liệu trực tiếp trong không gian thị giác

[ColPali](colpali-vision-space-document-retrieval.md) bỏ chuỗi OCR–layout parsing–chunking: mã hóa ảnh trang thành nhiều vector và dùng late interaction kiểu ColBERT với token truy vấn.[^faysse-2025-colpali-camera-ready] [ColQwen2](colqwen2-vision-space-document-retrieval.md) giữ công thức này nhưng đổi backbone sang Qwen2-VL và đạt điểm ViDoRe cao hơn trong thí nghiệm của bài báo.[^faysse-2025-colpali-camera-ready]

**Hàm ý tổng hợp:** visual RAG đang chuyển ingestion từ pipeline nhiều thành phần sang retriever end-to-end có khả năng giữ layout, bảng và hình. Nút thắt tiếp theo là dung lượng multi-vector, truy hồi corpus lớn, tài liệu nhiều trang, multilingual và benchmark dùng truy vấn thật.

### 5. Hiệu quả theo kích thước, độ trễ và độ phân giải

[ModernVBERT](modernvbert-small-visual-document-retriever.md) kết hợp vision tower SigLIP 2 với text encoder hai chiều trong early fusion, rồi dùng late interaction. Kết quả báo cáo cho thấy mô hình 250M gần ColPali lớn hơn trên các split ViDoRe được thử, với lợi thế chính nằm ở trade-off kích thước/độ trễ thay vì điểm tuyệt đối cao nhất.[^teiletche-2026-modernvbert-camera-ready]

**Hàm ý tổng hợp:** thay vì chỉ scale backbone sinh, nghiên cứu đang quay lại thiết kế encoder chuyên biệt, bidirectional attention, high-resolution cooldown, pooling/compression và kiến trúc phù hợp với serving.

### 6. Safety theo policy và dữ liệu biên

[ShieldGemma 2](shieldgemma-2-image-content-moderation.md) biến moderation thành phân loại có policy đầu vào, trả xác suất vi phạm có thể đặt ngưỡng. Dữ liệu huấn luyện kết hợp taxonomy tổng hợp, ảnh web được lọc và các ca biên nơi model/rater bất đồng.[^zeng-2025-shieldgemma2]

**Hàm ý tổng hợp:** safety đang chuyển từ taxonomy cố định sang policy-conditioned classifier có thể hiệu chỉnh theo ngữ cảnh triển khai. Các khoảng trống được chính bài báo nêu gồm chữ chèn trên ảnh, hội thoại xen kẽ nhiều ảnh và phạm vi ngoài ba policy mặc định.

## Các hướng phát triển ưu tiên

1. **Unified global–dense encoders:** hợp nhất chất lượng zero-shot/retrieval với grounding, segmentation và document understanding mà không cần nhiều model chuyên biệt.
2. **Multilingual curation có kiểm toán:** cân bằng theo từng ngôn ngữ và văn hóa, đồng thời đo leakage, PII, bias và độ phủ thay vì chỉ báo cáo trung bình đa ngôn ngữ.
3. **Retrieval vận hành được ở quy mô lớn:** nén multi-vector, coarse-to-fine retrieval, chỉ mục nhiều trang và đánh giá latency–memory–quality trên corpus thực.
4. **Adaptation theo miền không cần nhãn:** kết hợp prompt/adapters, teacher distillation và test-time signals nhưng cần đánh giá stability, calibration và chi phí cập nhật.
5. **Small specialized encoders:** tối ưu theo Pareto accuracy–latency–memory; kiểm chứng liệu bidirectional early fusion và high-resolution training có tiếp tục hiệu quả khi scale.
6. **Safety như một tầng có thể cấu hình:** policy tùy biến, threshold calibration, xử lý OCR/text-in-image và đánh giá drift/adversarial boundary sau triển khai.
7. **Benchmark thực tế hơn:** mở rộng ngôn ngữ, kích thước corpus, truy vấn người dùng thật, tài liệu nhiều trang và báo cáo uncertainty/significance.

## Giới hạn bằng chứng

Các con số giữa bài không so sánh trực tiếp được vì khác dữ liệu, backbone, quy mô, protocol và benchmark. Nhiều kết luận hiện chỉ được hỗ trợ bởi ablation hoặc benchmark của chính bài báo; các hướng ưu tiên phía trên là **suy luận tổng hợp**, chưa phải đồng thuận đã được kiểm chứng độc lập.

## Relationships

- Synthesizes: [Meta CLIP 2](meta-clip-2-worldwide-clip-scaling.md), [SigLIP 2](siglip2-multilingual-vision-language-encoders.md), [TIPSv2](tipsv2-patch-text-aligned-vision-language-pretraining.md), [CasPL](caspl-cascade-prompt-learning.md), [ColPali](colpali-vision-space-document-retrieval.md), [ColQwen2](colqwen2-vision-space-document-retrieval.md), [ModernVBERT](modernvbert-small-visual-document-retriever.md), and [ShieldGemma 2](shieldgemma-2-image-content-moderation.md).
- Synthesized by: [Vision-language task-to-model map](vision-language-task-to-model-map.md), which maps these research directions to concrete task families and model choices.

[^chuang-2025-meta-clip-2]: Chuang et al., “Meta CLIP 2: A Worldwide Scaling Recipe” (2025), [source](../raw/2507.22062_MetaCLIP%202/paper.tex).
[^tschannen-2025-siglip2]: Tschannen et al., “SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features” (2025), [source](../raw/2502.14786_SigLIP2/document.tex).
[^cao-2026-tipsv2]: Cao et al., “TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment” (2026), [source](../raw/2604.12012_TIPSv2/main.tex).
[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (ECCV 2024), [source](../raw/2409.17805_CasPL/main.tex).
[^faysse-2025-colpali-camera-ready]: Faysse et al., “ColPali: Efficient Document Retrieval with Vision Language Models” (2025), [source](../raw/2407.01449_ColPali/iclr2025_conference.tex).
[^teiletche-2026-modernvbert-camera-ready]: Teiletche et al., “ModernVBERT: Towards Smaller Visual Document Retrievers” (ICLR 2026), [source](../raw/2510.01149_ColModernVBert/iclr2026_conference.tex).
[^zeng-2025-shieldgemma2]: ShieldGemma Team, “ShieldGemma 2: Robust and Tractable Image Content Moderation” (2025), [source](../raw/2504.01081_ShieldGemma2/main.tex).
