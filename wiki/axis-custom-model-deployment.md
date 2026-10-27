---
type: Concept
title: "Triển khai custom AI model lên camera Axis"
description: "Quy trình đưa model tự huấn luyện lên camera Axis: chọn SoC, quantization, đường chuyển đổi theo SoC, kiểm tra bằng larod-client và đóng gói ACAP application."
tags: [edge-ai, axis, deployment, tflite]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-doc-dlpu
    resource: ../raw/computer-vision/on-device/axis-dlpu/index.md
    scope: ../raw/computer-vision/on-device/axis-dlpu/
    kind: docs
    title: "Axis Deep Learning Processing Unit (DLPU) — Axis developer documentation"
  - id: axis-ai-chatgpt-research
    resource: ../raw/axis-ai-chatgpt-research.md
    kind: research
    title: "Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis"
  - id: axis-doc-artpec9-model-conversion
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/
    kind: docs
    title: "Model Conversion (ARTPEC-9) — Axis developer documentation"
  - id: axis-doc-cv75-model-conversion
    resource: ../raw/computer-vision/on-device/system-on-chip/cv75/model-conversion/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/cv75/model-conversion/
    kind: docs
    title: "Model Conversion (CV75) — Axis developer documentation"
---

# Triển khai custom AI model lên camera Axis

Triển khai gồm hai phần tách biệt: (1) chuyển model đã train sang định dạng mà DLPU chạy được; (2) viết ACAP application để dùng model đó trên camera. Chọn SoC là tiêu chí quan trọng hơn chọn dòng camera M, P hay Q, vì định dạng model và toolchain khác nhau theo SoC.[^axis-ai-chatgpt-research]

## Định dạng model theo SoC

Axis dùng CPU làm baseline: model cho CPU chỉ cần `.tflite` nhưng chạy chậm. Với DLPU, phải đi qua đường chuyển đổi riêng của SoC, và độ khó tăng dần từ ARTPEC-7 đến CV25/CV75.[^axis-doc-dlpu]

| SoC | Đường chuyển đổi từ source model | Công cụ chuyển đổi | Độ dễ (Axis) |
| --- | --- | --- | --- |
| CPU (baseline) | ─> `.tflite` | TensorFlow Lite conversion | Dễ |
| ARTPEC-7 | ─> `quantized.tflite` ─> `edge-tpu.tflite` | TensorFlow Lite + Edge TPU Compiler | Dễ |
| ARTPEC-8 | ─> `quantized.tflite` | TensorFlow Lite conversion | Trung bình |
| ARTPEC-9 | ─> `quantized.tflite` | TensorFlow Lite conversion | Trung bình |
| Ambarella CV25 | ─> `.onnx` ─> `native.bin`, hoặc `.tflite` ─> `native.bin` | Ambarella CNNGen | Khó |
| Ambarella CV75 | ─> `.onnx` ─> `native.bin` | Ambarella CNNGen | Khó |

Tên định dạng và mức độ dễ là **Reported** từ bảng của Axis; tên công cụ lấy từ nguồn thứ cấp. Axis cố ý không định lượng tốc độ vì tốc độ phụ thuộc model, mức tối ưu hóa và cấu hình phần cứng của từng sản phẩm (clock, memory).[^axis-doc-dlpu][^axis-ai-chatgpt-research] Với CV75, [Chuyển model ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md) ghi lại quy trình CNNGen cụ thể để đi từ `.onnx` đến `.bin`; đây là nhánh chi tiết của bảng trên.

Trang SoC của Axis xác nhận hai đầu mút của bảng: ARTPEC-9 nhận thẳng `.tflite` đã lượng tử hóa, không có bước biên dịch offline, còn CV75 chỉ nhận `.onnx` và phải qua CNNGen Toolchain — toolchain này không công khai nên phải liên hệ Ambarella.[^axis-doc-artpec9-model-conversion][^axis-doc-cv75-model-conversion] Chi tiết nhánh ARTPEC-9 nằm ở [Chuyển model sang ARTPEC-9](axis-artpec-9-model-conversion.md).

## Camera tham khảo

| Camera | SoC | Điểm chính |
| --- | --- | --- |
| AXIS M3216-LVE | ARTPEC-8, 4 MP | Thuộc M32 Series, có DLPU và hỗ trợ phát triển ứng dụng deep learning tùy biến qua ACAP; phù hợp để nghiên cứu pipeline TFLite trên ARTPEC-8 |
| AXIS Q3548-LVE | ARTPEC-9, 8 MP | Có DLPU ARTPEC-9 và hỗ trợ analytics tại edge; đáng cân nhắc khi cần hiệu năng cao hơn |
| AXIS M2036-LE | Ambarella CV25, 4 MP | Có DLPU và analytics tại edge, nhưng custom model trên CV25 cần Ambarella CNNGen, kém thuận tiện hơn ARTPEC-8/9 |

Đây là các ví dụ minh họa, không phải danh sách bảo đảm tương thích. Có DLPU không đồng nghĩa một model đã convert chạy được trên mọi camera Axis; phải kiểm tra SoC, bộ nhớ, phiên bản AXIS OS, ACAP API và tập operator được hỗ trợ.[^axis-ai-chatgpt-research]

## Quy trình trên ARTPEC-8/9

```text
Train custom model (PyTorch / TensorFlow, custom dataset)
  → Export và quantization: INT8 / UINT8 TensorFlow Lite (custom_model.tflite)
  → Kiểm tra khả năng chạy trên DLPU của SoC đích
  → ACAP Native SDK: C/C++ application + model + manifest
  → Build .eap và cài vào camera qua web GUI hoặc VAPIX Application API
```

Có thể kiểm tra nạp model trực tiếp trên camera qua SSH bằng `larod-client`:[^axis-ai-chatgpt-research]

ARTPEC-8:

```bash
larod-client -g custom_model.tflite -c axis-a8-dlpu-tflite -i ""
```

ARTPEC-9:

```bash
larod-client -g custom_model.tflite -c a9-dlpu-tflite -i ""
```

Đây chỉ là lệnh thử nạp và chạy model, chưa phải ứng dụng AI hoàn chỉnh. Lệnh ARTPEC-9 khớp với lệnh mẫu trong tài liệu vendor, nơi model `.tflite` đã lượng tử hóa được nạp trực tiếp mà không qua bước biên dịch offline.[^axis-doc-artpec9-model-conversion] Ứng dụng thực tế còn phải xử lý input tensor, frames, output tensors, post-processing và logic nghiệp vụ.

## Đóng gói application

Một ACAP application điển hình có cấu trúc:[^axis-ai-chatgpt-research]

```text
custom-ai-app/
├── Dockerfile
└── app/
    ├── manifest.json
    ├── Makefile
    ├── main.cpp
    ├── custom_model.tflite
    └── LICENSE
```

Native SDK dùng toolchain theo kiến trúc: `armv7hf` cho ARTPEC-7, `aarch64` cho ARTPEC-8/9. Docker được dùng để build SDK trên máy phát triển, không phải để chạy container trên camera. Chi tiết nền tảng và lifecycle của SDK nằm ở [ACAP Native SDK](axis-acap-native-sdk.md).[^axis-ai-chatgpt-research]

Để lọc camera theo năng lực phần cứng, Axis cung cấp Product Selector với đường dẫn `Hardware platform → Compute capabilities → DLPU`, sau đó chọn `System-on-chip`.

## Relationships

- **Depends on** [ACAP Native SDK](axis-acap-native-sdk.md) để build và đóng gói `.eap`.
- **Uses** [quy trình chuyển ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md) khi đích là CV75.
- **Detailed by** [Chuyển model sang ARTPEC-9](axis-artpec-9-model-conversion.md), nhánh TFLite trực tiếp, và **constrained by** [bảng operator của ARTPEC-9](axis-artpec-9-operator-support.md).
- **Targets** [Axis DLPU](axis-dlpu.md) và SoC cụ thể.
- **Constrained by** [giới hạn quantization, operator và batch](axis-dlpu-model-constraints.md).
- **Constrained by** [breaking changes của AXIS OS 13/14](acap-axis-os-13-14-migration.md): `.larod` model format và Larod API v1/v2 bị bỏ, phải dùng `.tflite` và Larod v3, đồng thời khai báo `deepLearningProcessor` trong manifest.
- **Preceded by** [hiệu chỉnh méo ống kính](axis-camera-calibration.md) khi cần ảnh không méo trước detection hoặc đo khoảng cách. (Synthesis)
- **Guided by** [khuyến nghị triển khai và PoC](axis-edge-ai-adoption-guide.md).
- **Alternative to** [tùy biến AOA](axis-object-analytics.md) khi cần class hoặc detector riêng.
- **Illustrated by** [ACAP examples: training guides](acap-example-model-training-guides.md) and [Larod inference examples](acap-example-larod-object-detection.md): working per-SoC training, conversion and on-device inference code from `acap-native-sdk-examples`.

## Độ tin cậy

Đường chuyển đổi định dạng theo SoC nay được xác nhận bởi tài liệu vendor Axis, gồm cả hai nhánh ARTPEC-9 và CV75; CNNGen Toolchain cũng được [guide chuyển CV75](axis-cv75-onnx-conversion.md) nhắc tên. Tên "Ambarella", các lệnh `larod-client`, tên model và tham số `-c` vẫn là **Reported** từ nguồn thứ cấp và chưa được thực thi hoặc kiểm chứng trên thiết bị thật trong lần ingest này. Cần xác nhận lại với AXIS OS và SoC cụ thể.

[^axis-doc-dlpu]: Tài liệu chính thức: [Axis Deep Learning Processing Unit (DLPU) — Axis developer documentation](../raw/computer-vision/on-device/axis-dlpu/index.md), §Axis products with DLPU, bảng SoC / Speed / Ease of use / Conversion from source model.
[^axis-ai-chatgpt-research]: Nguồn thứ cấp: [Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis](../raw/axis-ai-chatgpt-research.md), §3 "Những dòng camera Axis nào hỗ trợ deploy custom AI model?", §4.1 "Quy trình deploy trên ARTPEC-8/9" và §4.2 "Đóng gói application".
[^axis-doc-artpec9-model-conversion]: Tài liệu chính thức: [Model Conversion (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md), §How to accelerate your model on ARTPEC-9, bước 2–3.
[^axis-doc-cv75-model-conversion]: Tài liệu chính thức: [Model Conversion (CV75) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/cv75/model-conversion/index.md), §How to accelerate your model on CV75, bước 2–4.
