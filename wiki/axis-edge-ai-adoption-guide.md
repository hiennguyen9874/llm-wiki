---
type: Concept
title: "Hướng triển khai custom AI trên Axis: quyết định và PoC"
description: "Khuyến nghị chọn ARTPEC-8/9 và ACAP Native SDK, tránh phụ thuộc container, cùng checklist PoC trước khi cam kết sản phẩm."
tags: [edge-ai, axis, poc, decision]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:39:36Z }
stale_after: 2027-04-30
sources:
  - id: axis-ai-chatgpt-research
    resource: ../raw/axis-ai-chatgpt-research.md
    kind: research
    title: "Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis"
  - id: axis-doc-dlpu
    resource: ../raw/computer-vision/on-device/axis-dlpu/index.md
    scope: ../raw/computer-vision/on-device/axis-dlpu/
    kind: docs
    title: "Axis Deep Learning Processing Unit (DLPU) — Axis developer documentation"
  - id: acap-container-compat
    resource: ../raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/index.md
    scope: ../raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/
    kind: docs
    revision: "ACAP version 12"
    title: "Axis devices & compatibility | Axis developer documentation"
---

# Hướng triển khai custom AI trên Axis: quyết định và PoC

Với mục tiêu nghiên cứu → PoC → production, hướng ưu tiên là ARTPEC-8 hoặc ARTPEC-9, ACAP Native SDK + Larod, và một CNN nhỏ hoặc YOLOv5 tối ưu cho TFLite để kiểm chứng trước khi đầu tư toàn bộ ứng dụng.[^axis-ai-chatgpt-research]

## Ưu tiên

1. **Chọn ARTPEC-8 hoặc ARTPEC-9.** Hai nền tảng này có tài liệu convert TFLite tương đối rõ, supported ops và code example chính thức. ARTPEC-9 phù hợp để đánh giá workload nặng hơn nhưng vẫn phải benchmark thực tế.
2. **Dùng ACAP Native SDK + Larod.** Tránh phụ thuộc container support nếu cần duy trì sản phẩm trên các dòng camera mới: tài liệu vendor xác nhận container path là legacy, sản phẩm mới trên AXIS OS 12.x không có container support, và các sản phẩm còn hỗ trợ container chỉ được hỗ trợ đến hết năm 2031.[^acap-container-compat]
3. **Làm PoC bằng CNN nhỏ hoặc YOLOv5 tối ưu cho TFLite.** Kiểm tra nạp model bằng `larod-client`, độ chính xác sau quantization, inference latency và CPU utilization trước khi viết toàn bộ ứng dụng.
4. **Cân nhắc kỹ CV25/CV75.** Vẫn triển khai custom AI được về mặt nền tảng, nhưng Axis xếp mức chuyển đổi model của CV25 và CV75 là "Hard", so với "Easy" ở ARTPEC-7 và "Medium" ở ARTPEC-8/9;[^axis-doc-dlpu] biên dịch native model còn cần Ambarella CNNGen Toolchain không công khai, một rào cản đáng kể cho development độc lập.[^axis-ai-chatgpt-research] Quy trình cụ thể cho CV75 nằm ở [Chuyển model ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md).

## Checklist PoC

Điều cần kiểm chứng không chỉ là model có load được, mà còn là:[^axis-ai-chatgpt-research]

- bao nhiêu phần trăm phép toán chạy trên DLPU;
- inference latency;
- FPS duy trì;
- RAM sử dụng;
- độ trễ do preprocessing/post-processing;
- tài nguyên còn lại cho các chức năng camera khác.

Đây là những yếu tố quyết định khả năng triển khai sản phẩm thực tế, không phải chỉ danh sách model "chạy được".

## Khi nào Axis phù hợp

Axis phù hợp khi mục tiêu là tự phát triển model object detection, classification hoặc analytics chuyên biệt chạy trực tiếp trong camera. Axis có giới hạn đáng kể nếu mục tiêu là triển khai tùy ý bất kỳ model ONNX/PyTorch nào, tùy biến accelerator kernel, thay thế AI engine gốc, hoặc có quyền kiểm soát sâu tương tự một hệ thống Linux với NPU SDK mở hoàn toàn.[^axis-ai-chatgpt-research]

## Relationships

- **Depends on** [khả năng tùy biến AI](axis-custom-ai-capability.md), [quy trình triển khai](axis-custom-model-deployment.md) và [giới hạn DLPU](axis-dlpu-model-constraints.md).
- **Uses** [ACAP Native SDK](axis-acap-native-sdk.md) và Larod.
- **Prefers** ARTPEC-8/9 over CV25/CV75 cho development độc lập.
- **Narrows to** [chọn camera ARTPEC-9 cụ thể](axis-artpec-9-camera-selection.md) khi đã quyết định dùng ARTPEC-9 và phải chọn giữa Q1728-LE và P1488-LE.
- **Uses** [quy trình chuyển ONNX sang native cho CV75](axis-cv75-onnx-conversion.md) khi phải triển khai trên CV75.
- **Informs** quyết định sản phẩm và phạm vi PoC.
- **Excludes** việc thay detector trong [AOA](axis-object-analytics.md) bằng model riêng.
- **Constrained by** [container application compatibility](acap-container-compatibility.md): container support giới hạn theo thiết bị và AXIS OS, `armv7hf` không còn sau AXIS OS 11.11, và matrix image chỉ áp dụng cho bản trước AXIS OS 12.0.

## Độ tin cậy

Mức độ dễ chuyển đổi model theo SoC được xác nhận bởi tài liệu vendor; các khuyến nghị còn lại là **Reported** từ nguồn thứ cấp và không phải kết quả benchmark độc lập. Các con số latency/FPS/RAM phải được đo trên thiết bị và AXIS OS cụ thể.

[^axis-doc-dlpu]: Tài liệu chính thức: [Axis Deep Learning Processing Unit (DLPU) — Axis developer documentation](../raw/computer-vision/on-device/axis-dlpu/index.md), §Axis products with DLPU, bảng SoC / Speed / Ease of use / Conversion from source model.
[^axis-ai-chatgpt-research]: Nguồn thứ cấp: [Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis](../raw/axis-ai-chatgpt-research.md), §9 "Khuyến nghị nếu muốn phát triển custom AI trên Axis" và "Đánh giá cuối cùng".

[^acap-container-compat]: Tài liệu chính thức: [Axis devices & compatibility — Axis developer documentation](../raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/index.md), warning banner "Note on container applications" và §Computer Vision solution and device compatibility.
