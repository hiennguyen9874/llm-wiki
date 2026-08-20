---
type: Synthesis
title: From unified pretraining to modern vision-language models
description: A synthesis of the FLAVA–BLIP–CoCa–BEiT-3–PaLI–BLIP-2 transition and its continuation into modular, multilingual, dense, efficient, retrieval-oriented, and safety-aware VLMs.
tags: [multimodal-learning, vision-language-models, vision-language-pretraining, research-directions, synthesis]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-20T10:14:19Z }
sources:
  - id: singh-2022-flava
    resource: ../raw/2112.04482_FLAVA/arxiv_strip.tex
    title: "FLAVA: A Foundational Language And Vision Alignment Model"
  - id: li-2022-blip
    resource: ../raw/2201.12086_BLIP/main.tex
    title: "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation"
  - id: yu-2022-coca
    resource: ../raw/2205.01917_CoCa/main.tex
    title: "CoCa: Contrastive Captioners are Image-Text Foundation Models"
  - id: wang-2022-beit-3
    resource: ../raw/2208.10442_BEiT-3/main.tex
    title: "Image as a Foreign Language: BEiT Pretraining for All Vision and Vision-Language Tasks"
  - id: chen-2022-pali
    resource: ../raw/2209.06794_PaLI/main.tex
    title: "PaLI: A Jointly-Scaled Multilingual Language-Image Model"
  - id: li-2023-blip2
    resource: ../raw/2301.12597_BLIP-2/main.tex
    title: "BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models"
  - id: tschannen-2025-siglip2
    resource: ../raw/2502.14786_SigLIP2/document.tex
    title: "SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features"
  - id: faysse-2025-colpali-camera-ready
    resource: ../raw/2407.01449_ColPali/iclr2025_conference.tex
    title: "ColPali: Efficient Document Retrieval with Vision Language Models"
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: "Cascade Prompt Learning for Vision-Language Model Adaptation"
  - id: zeng-2025-shieldgemma2
    resource: ../raw/2504.01081_ShieldGemma2/main.tex
    title: "ShieldGemma 2: Robust and Tractable Image Content Moderation"
  - id: microsoft-mage-2026
    resource: ../raw/2607.24904_Mage-VL/main.tex
    title: "Mage-VL: An Efficient Codec-Native Streaming Multimodal Foundation Model"
  - id: openmoss-moss-vl-2026
    resource: ../raw/2608.15045_MOSS-VL/main.tex
    title: MOSS-VL Technical Report
  - id: zhang-2026-moe-vie
    resource: ../raw/2608.17402_MoE-ViE/main.tex
    title: "MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding"
---

# From unified pretraining to modern vision-language models

Chuỗi FLAVA → BLIP → CoCa → BEiT-3 → PaLI → BLIP-2 nên được đọc như một bản đồ các ý tưởng hội tụ, không phải phả hệ tuyến tính. Trọng tâm chuyển từ một backbone làm tốt cả unimodal và multimodal, sang hợp nhất alignment với generation, chuẩn hóa mọi tác vụ thành token prediction, scale dữ liệu/ngôn ngữ, rồi tái sử dụng các backbone đóng băng qua connector nhỏ. Các VLM sau đó phân nhánh thành assistant sinh, encoder global–dense, adaptation tham số thấp, visual retrieval chuyên biệt và safety có policy.

## Bản đồ phương pháp

| Mốc | Bài toán chính | Cơ chế trung tâm | Di sản |
|---|---|---|---|
| [FLAVA](flava-foundational-language-vision-alignment.md) | Giữ năng lực ảnh, text và suy luận kết hợp trong một foundation model | Image encoder + text encoder + fusion transformer; contrastive, matching, masked image/text; paired và unpaired data[^singh-2022-flava] | Đặt mẫu multi-tower + fusion và multi-objective, nhưng chưa lấy generation làm giao diện chung |
| [BLIP](blip-bootstrapping-language-image-pre-training.md) | Hợp nhất understanding và generation, đồng thời giảm nhiễu caption web | MED đổi vai giữa text encoder, grounded encoder và grounded decoder; ITC + ITM + LM; CapFilt sinh và lọc caption[^li-2022-blip] | Đưa data bootstrapping và encoder–decoder parameter sharing thành phần cốt lõi |
| [CoCa](coca-contrastive-captioner-image-text-foundation-model.md) | Giữ retrieval/zero-shot đồng thời có captioning | Một causal decoder tách phần text-only và phần cross-attend ảnh; contrastive + autoregressive captioning trong một stage[^yu-2022-coca] | Cho thấy alignment và generation có thể cùng tồn tại trong kiến trúc đơn giản, huấn luyện từ đầu |
| [BEiT-3](beit-3-multiway-masked-multimodal-pretraining.md) | Dùng một backbone và objective cho nhiều modality/task | Shared self-attention, modality-specific FFN experts, masked token prediction cho ảnh, text và cặp ảnh–text[^wang-2022-beit-3] | Đẩy hướng “image as language”, shared backbone và conditional generation; retrieval tốt hơn vẫn dùng contrastive intermediate tuning |
| [PaLI](pali-jointly-scaled-multilingual-language-image-model.md) | Scale đồng thời vision, language và multilingual transfer | ViT + mT5 encoder–decoder; mọi tác vụ thành prompt → text; mixture 1.6B ví dụ và WebLI đa ngôn ngữ[^chen-2022-pali] | Củng cố text generation như API chung, tái sử dụng unimodal checkpoints, task prompting và multilingual scaling |
| [BLIP-2](blip-2-bootstrapping-frozen-vision-language-models.md) | Tránh end-to-end pretraining rất đắt khi image encoder và LLM đã mạnh | Frozen image encoder + frozen LLM + Q-Former 188M; stage 1 học representation, stage 2 tạo soft visual prompts[^li-2023-blip2] | Định hình mô thức connector/adaptor giữa vision tower và LLM, huấn luyện tham số ít hơn nhưng phụ thuộc chất lượng và rủi ro của backbone |

## Các chuyển dịch lớn

### 1. Từ fusion chuyên biệt sang generation làm giao diện chung

FLAVA ưu tiên ba loại representation: ảnh, text và fused. BLIP và CoCa thêm generation nhưng vẫn giữ contrastive/matching để retrieval và understanding không bị mất. PaLI đi xa hơn khi biểu diễn hầu hết tác vụ dưới dạng prompt-to-text; ưu điểm là bỏ task-specific heads, còn chi phí là retrieval/classification có thể không còn giao diện tự nhiên như dual encoder.[^singh-2022-flava][^li-2022-blip][^yu-2022-coca][^chen-2022-pali]

### 2. Từ một loss sang phối hợp objective có vai trò rõ ràng

Contrastive loss tạo global alignment và retrieval; matching/cross-attention học tương tác chi tiết; masked modeling tận dụng dữ liệu unimodal; language modeling tạo đầu ra mở. CoCa tối giản hóa thành contrastive + captioning, BEiT-3 thử thống nhất bằng masked prediction, còn BLIP-2 tách representation alignment khỏi LLM generation thành hai giai đoạn.[^li-2022-blip][^yu-2022-coca][^wang-2022-beit-3][^li-2023-blip2]

### 3. Từ “thêm dữ liệu” sang data engine và multilingual mixture

FLAVA phối hợp paired/unpaired public data; BLIP biến model thành captioner và filter để tái tạo supervision; PaLI scale sang WebLI đa ngôn ngữ, OCR và nhiều task mixture. Vì vậy data quality, task mixture, language balance, deduplication và synthetic supervision trở thành biến thiết kế ngang hàng với kiến trúc.[^singh-2022-flava][^li-2022-blip][^chen-2022-pali]

### 4. Từ train end-to-end sang tái sử dụng backbone và connector

CoCa huấn luyện mô hình lớn từ đầu; PaLI khởi tạo từ ViT và mT5; BLIP-2 đóng băng cả image encoder lẫn LLM và chỉ học cầu nối. Đây là chuyển dịch từ xây một monolith sang tổ hợp các foundation model chuyên modality. Đổi lại, bottleneck connector có thể làm mất thông tin ảnh, và lỗi factual, bias hay dữ liệu cũ của LLM vẫn truyền sang hệ thống.[^yu-2022-coca][^chen-2022-pali][^li-2023-blip2]

## Từ BLIP-2 đến các VLM hiện đại

Các bằng chứng 2024–2026 trong wiki cho thấy nhiều nhánh bổ sung thay vì một kiến trúc thống trị:

1. **Assistant-style generative VLM:** tiếp tục công thức vision encoder → projector/resampler/connector → LLM, rồi bổ sung instruction tuning, dữ liệu xen kẽ ảnh–text, nhiều ảnh/video và tool use. [Mage-VL](mage-vl-codec-native-streaming-vision-language-model.md) là bằng chứng trong wiki cho biến thể video chọn patch từ tín hiệu codec trước projector vào Qwen3-4B và dùng gate cho phản hồi streaming. [MOSS-VL](moss-vl-realtime-vision-language-model.md) cho biến thể khác: Qwen3-8B decoder cross-attend tới visual KV cache thay vì đưa visual patches vào decoded sequence; Realtime-SFT dạy state token silence/response và báo cáo L2-L4 streaming, còn L5 chỉ có bằng chứng định tính. Cả hai là technical report tự đánh giá, không xác nhận toàn bộ nhánh assistant-style hay lợi thế trên mọi video task.[^microsoft-mage-2026][^openmoss-moss-vl-2026] Wiki vẫn chưa có concept nguồn chính cho LLaVA, Flamingo hay Qwen2-VL, nên chi tiết của nhánh này còn là khoảng trống truy hồi.
2. **Encoder global–dense và sparse scaling:** [SigLIP 2](siglip2-multilingual-vision-language-encoders.md) giữ dual-encoder alignment nhưng thêm captioning/grounding, self-distillation và masked-patch prediction để phục vụ cả retrieval lẫn localization và dense prediction.[^tschannen-2025-siglip2] [MoE-ViE](moe-vie-mixture-of-experts-vision-encoder.md) thay phần lớn FFN của vision tower bằng expert fine-grained để tăng total capacity mà giữ active capacity thấp hơn, đồng thời cần grouped GEMM và kernel fusion để biến lợi ích FLOPs thành latency thực tế. Kết quả đối chiếu là self-reported và bị giới hạn bởi data/protocol riêng.[^zhang-2026-moe-vie]
3. **Multilingual và culturally broader data:** tokenizer, curation, mixture và model capacity phải được đồng thiết kế; dịch caption hoặc thay text encoder đơn thuần không đủ để bảo đảm chất lượng cân bằng.
4. **Thích nghi tham số thấp:** [CasPL](caspl-cascade-prompt-learning.md) tách domain knowledge và task knowledge qua cascade prompts, cho thấy hướng freeze backbone rồi học prompt/adapters từ dữ liệu ít nhãn.[^wu-2024-caspl]
5. **VLM chuyên biệt cho retrieval/RAG:** [ColPali](colpali-vision-space-document-retrieval.md) mã hóa trực tiếp ảnh trang và dùng multi-vector late interaction, bỏ pipeline OCR–layout–chunking nhưng đổi lại tăng chi phí index và scoring.[^faysse-2025-colpali-camera-ready]
6. **Safety như một module có policy:** [ShieldGemma 2](shieldgemma-2-image-content-moderation.md) nhận policy cùng ảnh và trả điểm vi phạm có thể đặt ngưỡng, biểu hiện xu hướng tách moderation khỏi model sinh chính.[^zeng-2025-shieldgemma2]

## Hướng phát triển ưu tiên

Các mục sau là **suy luận tổng hợp** từ các nguồn trên:

- **Connector giàu thông tin hơn nhưng rẻ:** adaptive visual tokens, token pruning, coarse-to-fine attention và dynamic resolution để giảm bottleneck kiểu fixed queries.
- **Unified global–dense–generative representation:** một visual backbone vừa retrieval nhanh, vừa grounding/segmentation, vừa cung cấp token tốt cho LLM.
- **Dữ liệu xen kẽ và có cấu trúc:** từ một ảnh–một caption sang nhiều ảnh, video, tài liệu nhiều trang, OCR/layout và hội thoại dài; cần deduplication và leakage audit tương ứng.
- **Multilingual/multicultural có kiểm toán:** cân bằng theo ngôn ngữ, địa lý và long tail; báo cáo riêng coverage, bias, PII và chất lượng thay vì chỉ macro-average.
- **Module hóa huấn luyện và serving:** chọn freeze/unfreeze, adapter, expert hay encoder chuyên biệt theo Pareto quality–latency–memory thay vì chỉ scale monolithic LLM.
- **Retrieval và tool use làm nền cho factuality:** tách tri thức cập nhật khỏi weights và đánh giá grounding/citation, thay vì xem caption fluency là bằng chứng reasoning.
- **Safety end-to-end:** policy-conditioned moderation, OCR/text-in-image, prompt injection qua ảnh, nhiều ảnh và calibration sau triển khai.
- **Benchmark thực tế:** temporal video, multi-image consistency, document corpus lớn, truy vấn thật, robustness và uncertainty; tránh so điểm chéo bài khi data/backbone/protocol khác nhau.

## Giới hạn bằng chứng

Chuỗi trên chủ yếu phản ánh các bài 2022–2025 có trong kho. Các benchmark không so sánh trực tiếp được vì khác dữ liệu, scale, resolution, fine-tuning và task formulation. Wiki bao phủ tốt nhánh pretraining và encoder hiện đại nhưng thiếu nguồn chính chuyên biệt cho phần lớn assistant-style VLM sau BLIP-2; do đó không nên dùng trang này như survey đầy đủ của toàn lĩnh vực.

## Relationships

- Synthesizes: [FLAVA](flava-foundational-language-vision-alignment.md), [BLIP](blip-bootstrapping-language-image-pre-training.md), [CoCa](coca-contrastive-captioner-image-text-foundation-model.md), [BEiT-3](beit-3-multiway-masked-multimodal-pretraining.md), [PaLI](pali-jointly-scaled-multilingual-language-image-model.md), and [BLIP-2](blip-2-bootstrapping-frozen-vision-language-models.md).
- Related: [Evolution of CLIP-style vision–language pretraining](evolution-of-clip-style-vision-language-pretraining.md) expands the dual-encoder branch.
- Related: [Recent vision-language research directions](recent-vision-language-research-directions.md) expands the 2024–2026 frontier in dense representation, adaptation, document retrieval, efficiency, safety, and streaming.
- Related: [Mage-VL codec-native streaming vision-language model](mage-vl-codec-native-streaming-vision-language-model.md) and [MOSS-VL real-time vision-language model](moss-vl-realtime-vision-language-model.md) illustrate separate codec-native and cross-attention-cache variants for proactive/real-time video interaction.[^microsoft-mage-2026][^openmoss-moss-vl-2026]
- Related: [MoE-ViE mixture-of-experts vision encoder](moe-vie-mixture-of-experts-vision-encoder.md) illustrates sparse capacity scaling and kernel co-design at the vision-encoder interface used by downstream LLM alignment.[^zhang-2026-moe-vie]
- Synthesized by: [Vision-language task-to-model map](vision-language-task-to-model-map.md), which reorganizes unified and modular VLMs by downstream problem and system interface.

[^singh-2022-flava]: Singh et al., “FLAVA” (2022), [source manuscript](../raw/2112.04482_FLAVA/arxiv_strip.tex).
[^li-2022-blip]: Li et al., “BLIP” (2022), [source manuscript](../raw/2201.12086_BLIP/main.tex).
[^yu-2022-coca]: Yu et al., “CoCa” (2022), [source manuscript](../raw/2205.01917_CoCa/main.tex).
[^wang-2022-beit-3]: Wang et al., “BEiT-3” (2022), [source manuscript](../raw/2208.10442_BEiT-3/main.tex).
[^chen-2022-pali]: Chen et al., “PaLI” (2022), [source manuscript](../raw/2209.06794_PaLI/main.tex).
[^li-2023-blip2]: Li et al., “BLIP-2” (2023), [source manuscript](../raw/2301.12597_BLIP-2/main.tex).
[^tschannen-2025-siglip2]: Tschannen et al., “SigLIP 2” (2025), [source manuscript](../raw/2502.14786_SigLIP2/document.tex).
[^faysse-2025-colpali-camera-ready]: Faysse et al., “ColPali” (2025), [source manuscript](../raw/2407.01449_ColPali/iclr2025_conference.tex).
[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (2024), [source manuscript](../raw/2409.17805_CasPL/main.tex).
[^zeng-2025-shieldgemma2]: ShieldGemma Team, “ShieldGemma 2” (2025), [source manuscript](../raw/2504.01081_ShieldGemma2/main.tex).
[^microsoft-mage-2026]: Microsoft Mage Team, “Mage-VL: An Efficient Codec-Native Streaming Multimodal Foundation Model” (technical report, July 2026), [complete supplied manuscript source](../raw/2607.24904_Mage-VL/main.tex).
[^openmoss-moss-vl-2026]: OpenMOSS Team, “MOSS-VL Technical Report” (technical report, August 2026), [complete supplied manuscript source](../raw/2608.15045_MOSS-VL/main.tex).
[^zhang-2026-moe-vie]: Zhang et al., “MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding” (supplied manuscript, August 2026), [complete supplied manuscript source](../raw/2608.17402_MoE-ViE/main.tex).
