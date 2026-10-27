---
type: Concept
title: "Chuyển model sang ARTPEC-9: quantize, export TFLite và chạy thử"
description: "Đường chuyển model cho DLPU ARTPEC-9: train bằng PyTorch/TensorFlow/JAX, lượng tử hóa int8/uint8 và export .tflite, rồi nạp trực tiếp bằng larod-client channel a9-dlpu-tflite mà không cần trình biên dịch offline."
tags: [edge-ai, axis, artpec-9, model-conversion, tflite]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:58:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-doc-artpec9-model-conversion
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/
    kind: docs
    title: "Model Conversion (ARTPEC-9) — Axis developer documentation"
  - id: axis-camera-chatgpt-research
    resource: ../raw/axis-camera-chatgpt-research.md
    kind: research
    title: "Kết quả tra cứu SoC của AXIS Q1728-LE và AXIS P1488-LE"
---

# Chuyển model sang ARTPEC-9: quantize, export TFLite và chạy thử

ARTPEC-9 không có bước biên dịch offline riêng: model sau khi lượng tử hóa và export thành `.tflite` được nạp thẳng lên thiết bị, khác với nhánh CV75 phải qua CNNGen. Quy trình chỉ gồm train, lượng tử hóa kèm export, rồi chạy thử bằng `larod-client` với channel `a9-dlpu-tflite`; bước 0 là đọc các khuyến nghị tối ưu model trước khi bắt đầu.[^axis-doc-artpec9-model-conversion]

## Quy trình

| Bước | Việc cần làm | Ghi chú |
| --- | --- | --- |
| 0 | Đọc Optimization Tips của ARTPEC-9 | Các ràng buộc này quyết định model có export được hay không; xem [ARTPEC-9 DLPU: operator được hỗ trợ và ràng buộc model](axis-artpec-9-operator-support.md). |
| 1 | Train model bằng framework tùy chọn | Tài liệu nêu PyTorch hoặc TensorFlow là lựa chọn phổ biến; sơ đồ còn vẽ JAX/Flax và một ô "…". |
| 2 | Lượng tử hóa int8/uint8 và export sang `.tflite` | Cách làm phụ thuộc framework; Axis có guide riêng cho PyTorch và TensorFlow (không có cục bộ, xem Giới hạn coverage). |
| 3 | Chạy model `.tflite` đã lượng tử hóa trên thiết bị | Lệnh mẫu bên dưới; trang test-your-model được dẫn link nhưng không có cục bộ. |

Lệnh chạy thử trên camera ARTPEC-9:[^axis-doc-artpec9-model-conversion]

```bash
larod-client -g <my-model>.tflite -c a9-dlpu-tflite -i ""
```

Lệnh này chỉ kiểm tra model nạp và chạy được trên DLPU; nó chưa phải ứng dụng AI hoàn chỉnh. Ứng dụng thực tế vẫn cần xử lý input tensor, frame, output tensor, post-processing và logic nghiệp vụ, như mô tả ở [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md).

## Sơ đồ chuyển đổi

Sơ đồ đính kèm trong trang vendor vẽ bốn nguồn (PyTorch, TensorFlow/Keras, JAX/Flax, "…") cùng hội tụ vào một hộp "export + int8 quantization", rồi `.tflite`, rồi ARTPEC-9 — tức chỉ một tầng chuyển đổi và không có toolchain vendor nào ở giữa. Văn bản trang chỉ nêu PyTorch và TensorFlow là lựa chọn phổ biến; danh sách JAX/Flax chỉ xuất hiện trong hình.[^axis-doc-artpec9-model-conversion]

Có một khác biệt nhỏ trong cùng tài liệu: nhãn hình ghi "int8" trong khi văn bản bước 2 và trang Optimization Tips ghi int8/uint8. Cả hai kiểu đều được DLPU nhận, nên coi int8/uint8 là quy tắc và "int8" trong hình là cách gọi tắt (Synthesis).

## Liên hệ với các SoC khác

ARTPEC-9 đối lập với CV75 ở chỗ không cần trình biên dịch của hãng thứ ba: CV75 bắt buộc đi qua Ambarella CNNGen Toolchain (không công khai) để sinh `.bin`, còn ARTPEC-9 dùng chính file `.tflite` làm artifact chạy trên thiết bị. Vì vậy mọi rủi ro về quyền truy cập toolchain và flag chưa được định nghĩa của nhánh CV75 không áp dụng cho ARTPEC-9; rủi ro còn lại nằm ở việc model có nằm trong tập operator được hỗ trợ hay không.[^axis-doc-artpec9-model-conversion]

**Đính chính phạm vi CNNGen.** Một ghi chú trước đây gắn "phải liên hệ Ambarella để có CNNGen" cho cả CV75 và ARTPEC-9; phần ARTPEC-9 trong ngoặc đó là nhầm. Nghĩa vụ liên hệ Ambarella chỉ áp dụng cho CV25 và CV75, nơi Axis xác nhận quy trình chuyển model cần CNNGen; ARTPEC-9 không có bước đó.[^axis-camera-chatgpt-research] Wiki đã nêu đúng phạm vi này từ trước (xem [Triển khai custom AI model](axis-custom-model-deployment.md) và [Chuyển model ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md)), nên đây là đính chính cho ghi chú ngoài wiki, không phải một supersession trong wiki. Văn bản gốc của ghi chú bị sửa không có trong `raw/`, nên chỉ ghi lại kết luận đúng.

## Thiết bị ARTPEC-9 cụ thể

Model `.tflite` ở trên chạy được trên mọi camera ARTPEC-9 có DLPU và cùng channel `a9-dlpu-tflite`; khác biệt giữa các model máy nằm ở RAM và form factor chứ không ở đường chuyển đổi. Ví dụ AXIS Q1728-LE (4 GB RAM) và AXIS P1488-LE (2 GB RAM) dùng chung đường model này — xem [Chọn camera ARTPEC-9 cho custom AI](axis-artpec-9-camera-selection.md).[^axis-camera-chatgpt-research]

## Giới hạn coverage

- Hai hướng dẫn `pytorch-to-tflite` và `tensorflow-to-tflite` được dẫn link nhưng không có trong `raw/`, nên chi tiết lượng tử hóa (bộ ảnh đại diện, chế độ per-tensor/per-channel, hiệu chỉnh tham số) chưa được kiểm chứng cục bộ.
- Trang `test-your-model` cũng không có cục bộ; ngữ nghĩa của `-i ""` và cách truyền input tensor chưa rõ từ nguồn này.
- Trang SoC không nêu phiên bản AXIS OS hay Larod tương ứng, nên `stale_after` được đặt theo quy ước domain.
- Chưa chạy thử: môi trường ingest không có thiết bị ARTPEC-9, nên không có kết quả **Reproduced**.

## Relationships

- **Part of** [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md), nhánh ARTPEC-9.
- **Constrained by** [ARTPEC-9 DLPU: operator được hỗ trợ và ràng buộc model](axis-artpec-9-operator-support.md).
- **Contrasts with** [Chuyển model ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md): một tầng export TFLite so với hai tầng qua CNNGen.
- **Runs on** [Axis DLPU](axis-dlpu.md), dùng Larod với channel `a9-dlpu-tflite`.
- **Refines** [giới hạn model trên DLPU](axis-dlpu-model-constraints.md), phần ARTPEC-9.
- **Deployed on** [các camera ARTPEC-9 cụ thể](axis-artpec-9-camera-selection.md): Q1728-LE và P1488-LE dùng chung channel `a9-dlpu-tflite`.

## Độ tin cậy

Trang này là **Reported** từ tài liệu vendor Axis và **Observed** qua static inspection của trang cùng sơ đồ đính kèm; không có claim nào **Reproduced** vì không có thiết bị để chạy `larod-client`. Phần So sánh với CV75 là **Synthesis** từ hai trang SoC.

[^axis-doc-artpec9-model-conversion]: Tài liệu chính thức: [Model Conversion (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md), §How to accelerate your model on ARTPEC-9, bước 0–3, và hình "DLPU Conversion Schematic" (`assets/convert-flowchart-a9-f26e427d2f31c9bf2bfdd0d8bb2c0782.png`).
[^axis-camera-chatgpt-research]: Nguồn thứ cấp: [Kết quả tra cứu SoC của AXIS Q1728-LE và AXIS P1488-LE](../raw/axis-camera-chatgpt-research.md), §2 "Đối chiếu bảng SoC và Larod của bạn" và §6 "Một điểm cần sửa trong ghi chú ban đầu" (phạm vi CNNGen chỉ là CV25/CV75).
