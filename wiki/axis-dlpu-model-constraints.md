---
type: Concept
title: "Giới hạn model trên DLPU của camera Axis"
description: "Ràng buộc quantization, operator, layout và batch của DLPU ARTPEC-8/9, cùng mức phù hợp của các họ model phổ biến."
tags: [edge-ai, axis, dlpu, model-optimization]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T06:00:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-ai-chatgpt-research
    resource: ../raw/axis-ai-chatgpt-research.md
    kind: research
    title: "Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis"
  - id: axis-doc-artpec9-optimization-tips
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/
    kind: docs
    title: "Optimization Tips (ARTPEC-9) — Axis developer documentation"
  - id: axis-doc-artpec9-supported-ops
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/
    kind: docs
    title: "Supported Ops (ARTPEC-9) — Axis developer documentation"
---

# Giới hạn model trên DLPU của camera Axis

DLPU không phải GPU/NPU đa dụng có thể chạy mọi model PyTorch hay ONNX. Một model export được sang TFLite vẫn có thể không chạy toàn bộ trên DLPU; phải kiểm tra quantization, operator, layout, batch và tài nguyên của SoC đích.[^axis-ai-chatgpt-research]

## ARTPEC-8

- Yêu cầu model quantized INT8/UINT8.
- Không hỗ trợ dynamic tensor sizes trên DLPU.
- Per-tensor quantization được khuyến nghị vì hiệu năng tốt hơn.
- Axis khuyến nghị tối ưu convolution, channel count và activation function.

## ARTPEC-9

- INT8/UINT8 vẫn là yêu cầu chính.
- Hỗ trợ tensor tối đa 4 chiều.
- Không hỗ trợ batch size lớn hơn 1.
- Chủ yếu dùng layout NHWC.
- Per-channel quantization chỉ được hỗ trợ với một số operator nhất định.
- Có giới hạn ở từng operator, ví dụ kernel, stride, padding và channel alignment cho convolution.

Hai bảng bắt buộc phải đọc khi chọn architecture là Supported Operators của ARTPEC-8 và ARTPEC-9 trên tài liệu Axis. Một model xuất được thành TFLite vẫn có thể không chạy toàn bộ trên DLPU.[^axis-ai-chatgpt-research]

Tài liệu vendor Axis xác nhận các ràng buộc ARTPEC-9 nêu trên và bổ sung ba điểm định lượng: channel được chia thành nhóm 16 nên nên chọn số channel chia hết cho 16, nên dùng `ReLU6`, và nên tránh explicit padding.[^axis-doc-artpec9-optimization-tips] Bảng supported operators của ARTPEC-9 nay có cục bộ với đầy đủ 23 operator và giới hạn từng operator ở [ARTPEC-9 DLPU: operator được hỗ trợ và ràng buộc model](axis-artpec-9-operator-support.md).[^axis-doc-artpec9-supported-ops]

## Mức phù hợp của các họ model

| Model / bài toán | Khả năng phù hợp | Lưu ý |
| --- | --- | --- |
| MobileNet / MobileNet-like | Cao | Hợp với edge inference |
| YOLOv5 loại nhỏ | Tốt, khi tối ưu đúng | Có ví dụ chính thức |
| Custom small CNN | Cao | Dễ kiểm soát operators |
| Segmentation CNN nhỏ | Có thể | Cần kiểm tra toàn bộ graph |
| YOLOv8/YOLO11 | Cần kiểm chứng | Không nên mặc định sẽ chạy toàn bộ trên DLPU |
| Vision Transformer | Khó hơn | Cần đánh giá operator, memory, CPU offload |
| Multimodal / VLM / LLM | Không phải use case tối ưu mặc định | Chưa có bảo đảm tương thích hay hiệu năng |

Nguồn tự mô tả bảng này là đánh giá kỹ thuật dựa trên đặc tính DLPU và supported operators, không phải danh sách tương thích chính thức cho mọi phiên bản model. Axis Model Zoo cung cấp model tham khảo và số đo hiệu năng, accuracy trên các SoC, hữu ích để chọn backbone trước khi train model riêng.[^axis-ai-chatgpt-research]

## Nhiều model cùng lúc

Có thể chạy nhiều model trên một thiết bị, nhưng các lần inference trên DLPU được chia sẻ theo thời gian, không chạy song song độc lập. Nếu chạy AXIS Object Analytics đồng thời với application riêng, các workload sẽ cạnh tranh tài nguyên DLPU và có thể ảnh hưởng latency/FPS; Axis khuyến nghị tắt analytics mặc định nếu không cần thiết.[^axis-ai-chatgpt-research]

Không nên tính tổng throughput theo cách: một model chạy 20 FPS riêng lẻ thì hai model sẽ cùng chạy được 20 FPS.

## Relationships

- **Constrains** [triển khai custom model](axis-custom-model-deployment.md) và việc chọn architecture.
- **Depends on** thế hệ [Axis DLPU](axis-dlpu.md).
- **Affects** khả năng chạy song song với [AXIS Object Analytics](axis-object-analytics.md).
- **Drives** các metric cần đo trong [PoC](axis-edge-ai-adoption-guide.md).
- **Documented by** [bảng supported operators của ARTPEC-9](axis-artpec-9-operator-support.md); bảng của ARTPEC-8 chưa lưu cục bộ.

## Độ tin cậy

Trang này là **Reported** từ nguồn thứ cấp. Các giới hạn operator cụ thể có thể thay đổi theo phiên bản AXIS OS, SDK và SoC; phải đối chiếu bảng Supported Operators hiện hành trước khi thiết kế model.

[^axis-ai-chatgpt-research]: Nguồn thứ cấp: [Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis](../raw/axis-ai-chatgpt-research.md), §6.1 "Giới hạn operators và quantization", §6.2 "Model nào phù hợp?" và §6.3 "Có thể chạy nhiều model cùng lúc không?".
[^axis-doc-artpec9-optimization-tips]: Tài liệu chính thức: [Optimization Tips (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md), toàn bộ phần thân.
[^axis-doc-artpec9-supported-ops]: Tài liệu chính thức: [Supported Ops (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md), bảng "Operator | Known limitations".
