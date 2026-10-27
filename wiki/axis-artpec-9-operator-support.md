---
type: Concept
title: "ARTPEC-9 DLPU: operator được hỗ trợ và ràng buộc model"
description: "Bảng 23 operator mà DLPU ARTPEC-9 chấp nhận với giới hạn cụ thể về kernel, stride, channel alignment và quantization scale, cùng các khuyến nghị tối ưu model trước khi export TFLite."
tags: [edge-ai, axis, artpec-9, dlpu, operators, model-optimization]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:58:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-doc-artpec9-supported-ops
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/
    kind: docs
    title: "Supported Ops (ARTPEC-9) — Axis developer documentation"
  - id: axis-doc-artpec9-optimization-tips
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/
    kind: docs
    title: "Optimization Tips (ARTPEC-9) — Axis developer documentation"
---

# ARTPEC-9 DLPU: operator được hỗ trợ và ràng buộc model

DLPU ARTPEC-9 chỉ chấp nhận model int8/uint8 quantized, và mỗi operator có thêm giới hạn riêng về kernel, stride, padding, channel và quantization scale. Bảng Supported Ops liệt kê đúng 23 operator kèm hạn chế đã biết, nên nó là điều kiện tiên quyết khi chọn architecture chứ không phải bước kiểm tra sau khi train.[^axis-doc-artpec9-supported-ops] Trang Optimization Tips bổ sung các ràng buộc toàn cục áp lên mọi model trước khi lượng tử hóa.[^axis-doc-artpec9-optimization-tips]

## Ràng buộc toàn cục

- Model phải lượng tử hóa int8/uint8; operator nhận kiểu dữ liệu khác không được DLPU hỗ trợ.[^axis-doc-artpec9-optimization-tips]
- Tensor tối đa 4 chiều; batch size lớn hơn 1 không được hỗ trợ.[^axis-doc-artpec9-optimization-tips]
- Layout được hỗ trợ là NHWC.[^axis-doc-artpec9-optimization-tips]
- Per-channel quantization chỉ được hỗ trợ cho weight và bias tensor của một tập operator giới hạn.[^axis-doc-artpec9-optimization-tips]
- Nên dùng activation `ReLU6` khi có thể.[^axis-doc-artpec9-optimization-tips]
- Tránh explicit padding khi có thể.[^axis-doc-artpec9-optimization-tips]
- Convolution chia channel thành nhóm 16, nên số channel chia hết cho 16 sẽ không lãng phí compute.[^axis-doc-artpec9-optimization-tips]

Ba nhóm Conv2D, DepthwiseConvolution2D, FullyConnected và TransposeConvolution2D còn ràng buộc tỉ lệ quantization `I*W/O` nằm trong khoảng 0–65536, với `I` là scale đầu vào, `W` là scale weight, `O` là scale đầu ra. Đây là ràng buộc dễ làm hỏng một model "hợp lệ" về mặt TFLite nhưng không chạy được trên DLPU.[^axis-doc-artpec9-supported-ops]

## Hạn chế theo operator

| Operator | Hạn chế đã biết |
| --- | --- |
| Add | Cộng element by element. |
| AveragePool | Pool 3×3, stride 1,1, padding `SAME`. "Mean" average pooling khi pooling size là 7 hoặc 8 và chiều cao/rộng đầu vào bằng pool size. |
| Concat | Output quantization scale nhỏ hơn input scale chia 128 là không hỗ trợ. Ghép theo channel thì channel của mọi input phải là bội số của 16. |
| Constant | Không ghi hạn chế. |
| Conv2D | Weight định dạng `HWIO`; kernel {1, 2, 3, 5, 7, 9} (không cần vuông); stride {1, 2} với stride cao = stride rộng; kernel >7 chỉ hỗ trợ stride 1; padding `SAME`/`VALID`; `I*W/O` trong 0–65536. |
| DepthToSpace | Block size 2; depth phải là bội số của bình phương block size. |
| DepthwiseConvolution2D | Weight định dạng `HWIM`; kernel {1, 2, 3, 5, 7, 9}; stride {1, 2}; kernel >7 chỉ stride 1; `SAME`/`VALID`; channel multiplier 1 (lớn hơn 1 không hỗ trợ); `I*W/O` trong 0–65536. |
| FullyConnected | Weight `HWIO` với `H` và `W` bằng 1; `I*W/O` trong 0–65536. |
| LeakyReLU | Alpha lớn hơn 0 và nhỏ hơn 1. |
| MaxPool | 1×1 pool với stride 2,2 (tương đương downsample 2×2); 2×2 pool stride 2,2 `VALID` với input chẵn; 2×2 pool stride 2,2 `SAME` với input lẻ; 3×3 pool stride 2,2 `VALID` hoặc `SAME` (input chẵn hoặc lẻ) với chiều rộng tensor tối đa 417; stride 1,1 với pool tới 9×9 cho `VALID` và tới 17×17 cho `SAME`; input không nhỏ hơn pool size. |
| MeanXY | Giảm chiều `H × W` về 1×1, chỉ hỗ trợ đầu vào `N×7×7×C` và `N×8×8×C`. |
| Mul | Nhân tensor với tensor hằng có shape `1×1×1×C`; nhân biến với scalar hằng khi giá trị quantized của output giống input. |
| Pad | Chỉ zero padding theo `H` và `W`, tối đa 7 mỗi phía, lượng pad có thể lệch giữa hai phía; quantization input và output phải giống nhau. |
| Reinterpret quantization | Không ghi hạn chế. |
| ReLU | Lower bound phải nhỏ hơn upper bound. |
| Requantize | Output scale nhỏ hơn input scale chia 128 là không hỗ trợ; đổi kiểu dữ liệu input/output được hỗ trợ. |
| Reshape | Không ghi hạn chế. |
| Resize | Chiều cao/rộng sau resize phải là `2n` hoặc `2n−1` so với kích thước gốc; nếu hai chiều không cùng chẵn hoặc cùng lẻ thì kết quả có thể kém chính xác hơn; một số cấu hình Resize Bilinear (`align_corners=True`, `half_pixel_centres=True` khi hai chiều không cùng chẵn/lẻ) cho kết quả không chính xác. |
| Sigmoid | Output luôn có quantization zero point bằng giá trị nhỏ nhất của kiểu dữ liệu lượng tử và scale 1/256. |
| Split | Tách theo channel thì channel của mọi output phải là bội số của 16. |
| Tanh | Output luôn có zero point bằng giá trị giữa của kiểu dữ liệu lượng tử và scale 1/128. |
| Transpose | Chỉ cho phép hoán vị chiều height, width và channel. |
| TransposeConvolution2D | Weight `HWIO`; kernel {1, 2, 3, 5, 7, 9}; chỉ stride 2; `SAME`/`VALID`; `I*W/O` trong 0–65536. |

## Hệ quả thiết kế (Synthesis)

- Các ràng buộc của bảng nghiêng về CNN cổ điển: kernel nhỏ, stride 1–2, channel chia hết cho 16, activation `ReLU`/`ReLU6`/`LeakyReLU`. Kiến trúc dùng depthwise channel multiplier lớn hơn 1 hoặc stride lớn hơn 2 sẽ phải thiết kế lại.
- Một số operator quen thuộc không xuất hiện trong bảng: `Softmax`, `SiLU`/`Swish`, `HardSwish`, `PReLU`, `GlobalAveragePool`. Bảng không tuyên bố là danh sách phủ định, nhưng không có lý do để mặc định chúng chạy được; model dùng chúng cần kiểm chứng trước khi cam kết architecture.
- Global average pooling chỉ có dạng `MeanXY` cho feature map 7×7 hoặc 8×8; backbone có head GAP trên feature map lớn hơn phải thay bằng cấu trúc khác.
- `Sigmoid` và `Tanh` bị cố định zero point và scale (1/256, 1/128), nên không thể tùy ý chọn độ phân giải lượng tử cho layer cuối.
- `Resize` chỉ nhân đôi hoặc gần nhân đôi kích thước (`2n`/`2n−1`); các tỉ lệ resize tự do trong tiền xử lý nên làm trên CPU thay vì trong graph.

## Giới hạn coverage

- Bảng Supported Ops của ARTPEC-8 và trang test-your-model không có trong `raw/`, nên không so sánh được hai thế hệ DLPU từ nguồn cục bộ.
- Các trang con trỏ tới (hướng dẫn TFLite, test-your-model) không có cục bộ.
- Không chạy thử trên thiết bị: toàn bộ bảng là **Reported**, được **Observed** bằng static inspection file Markdown; không có kết quả **Reproduced**.
- Bảng có thể thay đổi theo phiên bản AXIS OS và SDK, nên phải đối chiếu lại trước khi thiết kế model mới.

## Relationships

- **Refines** [giới hạn model trên DLPU của camera Axis](axis-dlpu-model-constraints.md) bằng bảng operator cụ thể của ARTPEC-9.
- **Constrains** [Chuyển model sang ARTPEC-9](axis-artpec-9-model-conversion.md) và việc chọn architecture trong [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md).
- **Depends on** [Axis DLPU](axis-dlpu.md) làm phần cứng đích.
- **Contrasts with** [Chuyển model ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md): CV75 không có bảng operator cục bộ, phải dựa vào tài liệu Ambarella.

## Độ tin cậy

Nội dung bảng là **Reported** từ tài liệu vendor Axis và **Observed** khi đọc trực tiếp file nguồn (23 dòng operator, ba dòng có cột hạn chế để trống). Phần "Hệ quả thiết kế" là **Synthesis** của agent, không phải khuyến nghị của Axis, và cần kiểm chứng bằng cách chạy model thật trên thiết bị.

[^axis-doc-artpec9-supported-ops]: Tài liệu chính thức: [Supported Ops (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md), bảng "Operator | Known limitations", toàn bộ 23 dòng.
[^axis-doc-artpec9-optimization-tips]: Tài liệu chính thức: [Optimization Tips (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md), toàn bộ phần thân (quantization, số chiều, batch, layout, per-channel, `ReLU6`, padding, channel nhóm 16).
