---
type: Synthesis
title: Vision-language task-to-model map
description: A task-oriented map from vision-language problems to model families and specific models, with selection guidance and evidence boundaries.
tags: [multimodal-learning, vision-language-models, task-taxonomy, model-selection, synthesis]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-20T10:14:19Z }
sources:
  - id: clip-lineage
    resource: evolution-of-clip-style-vision-language-pretraining.md
    title: Evolution of CLIP-style vision–language pretraining
  - id: unified-vlm
    resource: from-unified-pretraining-to-modern-vision-language-models.md
    title: From unified pretraining to modern vision-language models
  - id: recent-directions
    resource: recent-vision-language-research-directions.md
    title: Recent vision-language research directions
  - id: bridgetower
    resource: bridgetower-layerwise-vision-language-fusion.md
    title: BridgeTower layer-wise vision–language fusion
  - id: mammut
    resource: mammut-two-pass-multimodal-learning.md
    title: MaMMUT two-pass multimodal learning
  - id: one-peace
    resource: one-peace-multimodal-representation-learning.md
    title: ONE-PEACE multimodal representation learning
  - id: simeoni-2025-dinov3
    resource: ../raw/2508.10104_dinov3/main.tex
    title: DINOv3
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

# Vision-language task-to-model map

Các mô hình vision–language trong wiki có thể quy về ba giao diện chính: **dual encoder** cho phân loại zero-shot và retrieval nhanh; **fusion encoder** cho hiểu quan hệ ảnh–text; và **encoder–decoder/vision-to-LLM** cho sinh văn bản. Late interaction, prompt learning và safety classifier là các nhánh chuyên biệt. Vì một mô hình thường được đánh giá trên nhiều benchmark, bảng dưới đây phân biệt mô hình phù hợp trực tiếp với bài toán và mô hình chỉ dùng được sau fine-tuning hoặc gắn task head.[^clip-lineage][^unified-vlm][^recent-directions]

## Bản đồ bài toán → mô hình

| Nhóm bài toán | Mô hình nên dùng trong phạm vi wiki | Cách dùng và ranh giới |
|---|---|---|
| **Phân loại ảnh zero-shot / open-vocabulary** | [CLIP](clip-natural-language-image-pretraining.md), [ALIGN](align-noisy-image-text-learning.md), [LiT](lit-locked-image-tuning.md), [SigLIP](siglip-sigmoid-contrastive-language-image-pretraining.md), [OpenCLIP](openclip-reproducible-contrastive-language-image-scaling.md), [MetaCLIP](metaclip-metadata-curated-language-image-pretraining.md), [Meta CLIP 2](meta-clip-2-worldwide-clip-scaling.md), [SigLIP 2](siglip2-multilingual-vision-language-encoders.md), [MoE-ViE](moe-vie-mixture-of-experts-vision-encoder.md), [FILIP](filip-fine-grained-interactive-language-image-pretraining.md), [SLIP](slip-self-supervised-language-image-pre-training.md), [DeCLIP](declip-data-efficient-contrastive-language-image-pretraining.md), [CoCa](coca-contrastive-captioner-image-text-foundation-model.md) | Nhúng ảnh và prompt tên lớp vào cùng không gian rồi so độ tương đồng. CLIP là baseline; SigLIP thuận lợi khi tối ưu loss/batch; LiT khi đã có vision tower mạnh; MetaCLIP/Meta CLIP 2 khi trọng tâm là curation; SigLIP 2 khi cần thêm multilingual và dense transfer; MoE-ViE khi sparse capacity và source-specific kernel latency trade-off phù hợp.[^clip-lineage][^zhang-2026-moe-vie] |
| **Retrieval ảnh ↔ text** | CLIP, ALIGN, LiT, SigLIP/SigLIP 2, MoE-ViE, FILIP, FLAVA, BLIP, CoCa, BEiT-3, BLIP-2 stage 1, MaMMUT, ONE-PEACE | Dual encoder phù hợp truy hồi corpus lớn vì có thể index hai modality độc lập. FILIP dùng token-level late interaction cho tương ứng chi tiết nhưng score/index đắt hơn. MoE-ViE có kết quả retrieval zero-shot do tác giả báo cáo, nhưng không có bằng chứng trong source này về chi phí index corpus lớn. BLIP và BridgeTower thường dùng contrastive retrieval trước rồi rerank bằng image–text matching; BEiT-3 đạt retrieval tốt hơn khi có intermediate contrastive tuning.[^clip-lineage][^unified-vlm][^bridgetower][^mammut][^one-peace][^zhang-2026-moe-vie] |
| **Video zero-shot classification/retrieval hoặc vision encoder cho LLM** | [MoE-ViE](moe-vie-mixture-of-experts-vision-encoder.md), SigLIP 2, PEcore (được MoE-ViE dùng làm baseline) | MoE-ViE là encoder frame-based được video fine-tune với distillation và freezing; báo cáo có cả video zero-shot và alignment với Llama/Qwen, không phải bằng chứng cho streaming hoặc phản hồi chủ động. Chỉ coi 1.1B active-parameter / kernel-latency trade-off là source-specific vì training data có phần proprietary và protocol khác baseline.[^zhang-2026-moe-vie] |
| **Hiểu ảnh–text: VQA, NLVR2, visual entailment, matching** | [FLAVA](flava-foundational-language-vision-alignment.md), [BLIP](blip-bootstrapping-language-image-pre-training.md), [BridgeTower](bridgetower-layerwise-vision-language-fusion.md), [CoCa](coca-contrastive-captioner-image-text-foundation-model.md), [BEiT-3](beit-3-multiway-masked-multimodal-pretraining.md), [PaLI](pali-jointly-scaled-multilingual-language-image-model.md), [BLIP-2](blip-2-bootstrapping-frozen-vision-language-models.md), [MaMMUT](mammut-two-pass-multimodal-learning.md) | Ưu tiên fusion encoder khi cần phân biệt/matching; ưu tiên mô hình sinh khi câu trả lời là text mở. BridgeTower chỉ có bằng chứng cho tác vụ discriminative, không phải captioning. BLIP-2 phù hợp khi muốn tái sử dụng frozen vision encoder và LLM qua Q-Former.[^unified-vlm][^bridgetower][^mammut] |
| **Captioning và sinh text từ ảnh** | BLIP, CoCa, PaLI, BLIP-2, MaMMUT, BEiT-3 | BLIP hợp nhất encoder/decoder và dùng CapFilt; CoCa và MaMMUT giữ cả contrastive retrieval lẫn generation; PaLI chuẩn hóa nhiều tác vụ thành prompt → text; BLIP-2 là lựa chọn module hóa, ít tham số train hơn. BEiT-3 dùng conditional generation sau task adaptation.[^unified-vlm][^mammut] |
| **Grounding, referring expression, detection, segmentation và dense prediction** | [SigLIP 2](siglip2-multilingual-vision-language-encoders.md), [TIPSv2](tipsv2-patch-text-aligned-vision-language-pretraining.md), BEiT-3, ONE-PEACE; FILIP cho alignment patch–word | SigLIP 2 và TIPSv2 được pretrain để làm giàu unpooled patch features; BEiT-3 hỗ trợ detection/segmentation qua fine-tuning và task heads; ONE-PEACE có dense vision và referring-expression transfer. FILIP chỉ cho thấy correspondence định tính và cải thiện retrieval/classification, không chứng minh trực tiếp detection/segmentation.[^recent-directions][^clip-lineage][^one-peace] |
| **Đa ngôn ngữ / đa văn hóa** | [AltCLIP](altclip-multilingual-text-encoder-alignment.md), [Chinese CLIP](chinese-clip-language-specific-vision-language-pretraining.md), multilingual ALIGN/LiT/SigLIP, [PaLI](pali-jointly-scaled-multilingual-language-image-model.md), [SigLIP 2](siglip2-multilingual-vision-language-encoders.md), [Meta CLIP 2](meta-clip-2-worldwide-clip-scaling.md) | AltCLIP hoặc Chinese CLIP khi mở CLIP sang ngôn ngữ cụ thể; PaLI khi đầu ra là text đa ngôn ngữ; SigLIP 2 khi cần encoder global+dense; Meta CLIP 2 khi vấn đề chính là native-language data curation và scaling. Kết quả không chứng minh chất lượng đồng đều giữa mọi ngôn ngữ/văn hóa.[^clip-lineage][^unified-vlm][^recent-directions] |
| **Dense vision, geometry, segmentation, detection** | [DINOv3](dinov3-self-supervised-visual-foundation-model.md), SigLIP 2, TIPSv2, BEiT-3, ONE-PEACE | DINOv3 là lựa chọn vision-first khi cần dense patches, correspondence/geometry, hoặc head riêng trên backbone frozen; nó không phải image–text encoder gốc. Chỉ dùng biến thể `dino.txt` khi cần zero-shot text alignment, và vẫn cần decoder/head cho box, mask, depth hay 3D output.[^simeoni-2025-dinov3][^recent-directions] |
| **Few-shot/domain adaptation cho phân loại ảnh** | [CoOp](coop-context-optimization.md), [CoCoOp](cocoop-conditional-context-optimization.md), [MaPLe](maple-multimodal-prompt-learning.md), [PromptSRC](promptsrc-self-regulating-prompts.md), [CasPL](caspl-cascade-prompt-learning.md), [Tip-Adapter](tip-adapter-cache-based-few-shot-clip-adaptation.md), [WiSE-FT](wise-ft-robust-zero-shot-fine-tuning.md) | CoOp học prompt tĩnh; CoCoOp điều kiện theo ảnh; MaPLe prompt cả hai tower; PromptSRC giảm quên representation gốc; CasPL thêm unlabeled-domain teacher distillation; Tip-Adapter dùng cache và có bản không train; WiSE-FT nội suy checkpoint để giữ robustness. Bằng chứng chủ yếu chỉ cho image classification, không nên mặc định chuyển sang retrieval/generation.[^recent-directions] |
| **Test-time adaptation dưới distribution shift** | [PromptAlign](promptalign-test-time-distribution-alignment.md) | Cập nhật prompt theo từng mẫu bằng entropy minimization và alignment thống kê token. Cần proxy-source statistics và nhiều augmented views; bằng chứng hiện thuộc zero-shot image classification.[^recent-directions] |
| **Visual document retrieval / visual RAG** | [ColPali](colpali-vision-space-document-retrieval.md), [ColQwen2](colqwen2-vision-space-document-retrieval.md), [ModernVBERT/ColModernVBERT](modernvbert-small-visual-document-retriever.md) | Mã hóa ảnh trang trực tiếp và dùng multi-vector late interaction, tránh OCR–layout–chunking ở ingestion. ColQwen2 có điểm ViDoRe cao hơn ColPali trong cùng báo cáo; ModernVBERT ưu tiên trade-off kích thước/CPU latency. Chưa có bằng chứng mạnh cho corpus rất lớn hoặc tài liệu nhiều trang.[^recent-directions] |
| **Offline video understanding / proactive streaming / real-time interaction** | [Mage-VL](mage-vl-codec-native-streaming-vision-language-model.md) cho video codec-native và gate phản hồi; [MOSS-VL](moss-vl-realtime-vision-language-model.md) khi cần L2-L4 streaming được đánh giá và L5 định tính; MaMMUT cho video; [ONE-PEACE](one-peace-multimodal-representation-learning.md) cho image/audio/text | Mage-VL chọn patch theo codec trước encoder rồi dùng gate `silent`/`speak`; MOSS-VL giữ visual tokens ngoài decoded sequence và học `silence`/`response` trực tiếp trong decoder để nhận frame mới khi đang sinh. Cả hai chỉ nên dùng với giới hạn technical-report tự đánh giá; MOSS-VL chưa có benchmark công khai cho L5, và Mage-VL không chứng minh ưu thế trên mọi video task. MaMMUT thêm sparse spatiotemporal tube tokens rồi fine-tune video. ONE-PEACE là lựa chọn rõ nhất trong wiki cho audio–text retrieval/classification và representation ba modality.[^microsoft-mage-2026][^openmoss-moss-vl-2026][^mammut][^one-peace] |
| **Moderation/an toàn ảnh theo policy** | [ShieldGemma 2](shieldgemma-2-image-content-moderation.md) | Nhận ảnh + policy, trả xác suất vi phạm có thể đặt threshold. Phù hợp single-image moderation cho sexual, dangerous và violence/gore; chưa bao phủ chắc text chèn trong ảnh, hội thoại nhiều ảnh hoặc policy ngoài miền fine-tuning.[^recent-directions] |

## Chọn nhanh theo giao diện hệ thống

1. **Cần index lớn, latency thấp:** bắt đầu từ CLIP/SigLIP/MetaCLIP-family; dùng global vector. MoE-ViE là lựa chọn có bằng chứng source-specific cho tăng sparse vision capacity và latency kernel-tuned, nhưng chưa có benchmark index lớn hay replication. Chỉ chuyển sang FILIP hoặc late interaction khi độ chi tiết đáng đổi lấy memory và scoring cost.[^zhang-2026-moe-vie]
2. **Cần VQA/matching hơn là retrieval thuần:** dùng FLAVA hoặc BridgeTower cho discriminative fusion; dùng BLIP, PaLI, BLIP-2, CoCa hoặc MaMMUT nếu đầu ra cần sinh tự do.
3. **Cần một encoder vừa global vừa local:** ưu tiên SigLIP 2 hoặc TIPSv2 khi cần image–text representation gốc; chọn DINOv3 khi pipeline là vision-first dense/geometry rồi mới gắn head hoặc text alignment; BEiT-3 phù hợp khi chấp nhận task-specific fine-tuning/head.[^simeoni-2025-dinov3]
4. **Cần multilingual:** chọn theo đầu ra: Meta CLIP 2/SigLIP 2 cho embedding, PaLI cho generation, AltCLIP/Chinese CLIP cho retrofit CLIP.
5. **Cần thích nghi với ít nhãn:** Tip-Adapter cho baseline nhanh; CoOp/MaPLe/PromptSRC cho prompt learning; CasPL khi có ảnh miền không nhãn và teacher; PromptAlign khi chỉ được thích nghi lúc test.
6. **Cần RAG trên PDF giàu layout:** dùng ColPali/ColQwen2; chọn ModernVBERT khi CPU latency và kích thước quan trọng hơn điểm tuyệt đối.

## Những thứ không nên đồng nhất

- **Model và training recipe:** MetaCLIP, Meta CLIP 2, OpenCLIP scaling, SLIP, DeCLIP và TIPSv2 chủ yếu đóng góp recipe/objective/data; checkpoint cụ thể vẫn phụ thuộc backbone và training budget.
- **Retrieval và reasoning:** điểm retrieval tốt của dual encoder không tự suy ra VQA hoặc reasoning tốt; các tác vụ này thường cần fusion hoặc decoder.
- **Dense feature và task output:** patch representation tốt không đồng nghĩa model tự xuất box/mask; nhiều kết quả của BEiT-3, SigLIP 2 và ONE-PEACE cần head hoặc downstream fine-tuning.
- **Benchmark chéo bài:** không dùng điểm từ các bài khác data, backbone, resolution và protocol để xếp hạng tuyệt đối.

## Khoảng trống bằng chứng

Wiki hiện vẫn thiếu concept nguồn chính cho nhiều assistant-style VLM sau BLIP-2 như LLaVA, Flamingo và Qwen2-VL độc lập; Qwen2-VL chỉ xuất hiện gián tiếp trong ColQwen2. Mage-VL và MOSS-VL bổ sung bằng chứng technical-report cho video streaming, nhưng không làm bản đồ này thành catalog đầy đủ cho multimodal assistant, multi-image/video reasoning hay tool use.[^unified-vlm][^microsoft-mage-2026][^openmoss-moss-vl-2026]

## Relationships

- Synthesizes: [Evolution of CLIP-style vision–language pretraining](evolution-of-clip-style-vision-language-pretraining.md), [From unified pretraining to modern vision-language models](from-unified-pretraining-to-modern-vision-language-models.md), and [Recent vision-language research directions](recent-vision-language-research-directions.md).
- Uses: task evidence from [BridgeTower](bridgetower-layerwise-vision-language-fusion.md), [MaMMUT](mammut-two-pass-multimodal-learning.md), and [ONE-PEACE](one-peace-multimodal-representation-learning.md) to cover fusion, video, and audio frontiers not fully enumerated in the three source syntheses.

[^clip-lineage]: [Evolution of CLIP-style vision–language pretraining](evolution-of-clip-style-vision-language-pretraining.md).
[^unified-vlm]: [From unified pretraining to modern vision-language models](from-unified-pretraining-to-modern-vision-language-models.md).
[^recent-directions]: [Recent vision-language research directions](recent-vision-language-research-directions.md).
[^bridgetower]: [BridgeTower layer-wise vision–language fusion](bridgetower-layerwise-vision-language-fusion.md).
[^mammut]: [MaMMUT two-pass multimodal learning](mammut-two-pass-multimodal-learning.md).
[^one-peace]: [ONE-PEACE multimodal representation learning](one-peace-multimodal-representation-learning.md).
[^simeoni-2025-dinov3]: Siméoni et al., “DINOv3” (technical report, 2025), [complete supplied manuscript source](../raw/2508.10104_dinov3/main.tex).
[^microsoft-mage-2026]: Microsoft Mage Team, “Mage-VL: An Efficient Codec-Native Streaming Multimodal Foundation Model” (technical report, July 2026), [complete supplied manuscript source](../raw/2607.24904_Mage-VL/main.tex).
[^openmoss-moss-vl-2026]: OpenMOSS Team, “MOSS-VL Technical Report” (technical report, August 2026), [complete supplied manuscript source](../raw/2608.15045_MOSS-VL/main.tex).
[^zhang-2026-moe-vie]: Zhang et al., “MoE-ViE: Mixture of Experts Vision Encoder for Efficient Image and Video Understanding” (supplied manuscript, August 2026), [complete supplied manuscript source](../raw/2608.17402_MoE-ViE/main.tex).
