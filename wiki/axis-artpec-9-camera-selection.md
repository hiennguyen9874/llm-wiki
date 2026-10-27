---
type: Concept
title: "Chọn camera ARTPEC-9 cho custom AI: AXIS Q1728-LE và P1488-LE"
description: "So sánh AXIS Q1728-LE và P1488-LE khi triển khai model tự huấn luyện: cùng SoC ARTPEC-9/DLPU và cùng channel a9-dlpu-tflite, khác nhau ở RAM 4 GB so với 2 GB và form factor, kèm giới hạn của số benchmark Axis công bố."
tags: [edge-ai, axis, artpec-9, camera-selection, hardware, dlpu]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T16:20:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-camera-chatgpt-research
    resource: ../raw/axis-camera-chatgpt-research.md
    kind: research
    title: "Kết quả tra cứu SoC của AXIS Q1728-LE và AXIS P1488-LE"
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-yolov5
    resource: ../raw/axis-model-zoo/docs/yolov5.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "axis-model-zoo — docs/yolov5.md"
  - id: axis-doc-artpec9-model-conversion
    resource: ../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/
    kind: docs
    title: "Model Conversion (ARTPEC-9) — Axis developer documentation"
---

# Chọn camera ARTPEC-9 cho custom AI: AXIS Q1728-LE và P1488-LE

AXIS Q1728-LE (block camera) và AXIS P1488-LE (bullet camera) cùng dùng SoC ARTPEC-9 với accelerator DLPU, cùng kiến trúc CPU `aarch64` và cùng đường chạy model: `.tflite` đã lượng tử hóa INT8/UINT8 nạp trực tiếp qua Larod device `a9-dlpu-tflite`, không cần compiler offline. Vì vậy khác biệt quyết định khi chọn giữa hai máy cho một ứng dụng AI tùy chỉnh không phải là đường chuyển đổi model mà là **dung lượng RAM** (4 GB so với 2 GB), **form factor** và mức độ đã được benchmark của model bạn định dùng — không phải tốc độ inference DLPU.[^axis-camera-chatgpt-research]

## Phần cứng

| Thuộc tính | AXIS Q1728-LE | AXIS P1488-LE |
| --- | --- | --- |
| Form factor | Block camera | Bullet camera |
| SoC | ARTPEC-9 | ARTPEC-9 |
| AI accelerator | DLPU | DLPU |
| Kiến trúc CPU | ARM64 (`aarch64`) | ARM64 (`aarch64`) |
| RAM | 4 GB | 2 GB |
| Flash | 8 GB | 8 GB |
| Độ phân giải | 8 MP (4K) | 8 MP (4K) |
| Cảm biến | 1/1.2 inch | 1/1.2 inch |
| Video tối đa | 50/60 fps | 50/60 fps |
| Codec | H.264, H.265, AV1 | H.264, H.265, AV1 |
| Larod device cho DLPU | `a9-dlpu-tflite` | `a9-dlpu-tflite` |
| Model chạy trên DLPU | INT8/UINT8 `.tflite` | INT8/UINT8 `.tflite` |
| Compiler offline cần thiết | Không | Không |

Tất cả giá trị trong bảng là **Reported** từ một bản tra cứu thứ cấp; trang sản phẩm của Axis và datasheet mà nó dẫn link không có trong `raw/`, nên chưa đối chiếu được với vendor. Có một điểm không nhất quán ngay trong nguồn: danh sách ở §1 của nguồn không ghi RAM/Flash cho Q1728-LE (chỉ P1488-LE có), còn bảng đối chiếu ở §2 ghi Q1728-LE 4 GB RAM và 8 GB Flash. Trang này dùng giá trị của bảng §2 và ghi lại khác biệt đó như một hạn chế, không phải một xác nhận.[^axis-camera-chatgpt-research]

Kiến trúc `aarch64` cho ARTPEC-9 khớp với bảng chip của tài liệu ACAP đã lưu cục bộ (xem [ACAP generations, chip architectures and SDK-to-Axis OS compatibility](acap-chip-architecture-and-sdk-compatibility.md)), nên đây là điểm duy nhất của bảng được nguồn thứ hai củng cố.

## Vì sao RAM khác nhau nhưng tốc độ không gấp đôi

Hai máy dùng cùng SoC ARTPEC-9 nên phần tính toán của model chạy trên cùng một loại DLPU; RAM nhiều hơn không làm DLPU nhanh hơn, nó chỉ giữ được nhiều thứ hơn cùng lúc (model, buffer frame, thư viện, nhiều stream). Nguồn diễn đạt đúng ý này: 4 GB có lợi khi ACAP application dùng nhiều bộ nhớ, "nhưng không đồng nghĩa tốc độ inference DLPU gấp đôi" (**Reported** cho phần RAM, phần suy luận về tốc độ là **Synthesis**).[^axis-camera-chatgpt-research]

Hướng dẫn YOLOv5 của Axis củng cố giả thuyết này bằng một quan sát cục bộ: model YOLOv5n/s/m của Axis được test cho ARTPEC-9 trên một thiết bị Q1728 **4 GB RAM**, và hướng dẫn cảnh báo "thiết bị ít bộ nhớ hơn có thể gặp vấn đề khi xử lý model lớn hơn" (**Observed** trên văn bản hướng dẫn).[^mz-yolov5] Suy ra (**Synthesis**): với YOLOv5m cỡ 640 và model tự huấn luyện lớn hơn, P1488-LE 2 GB là biến rủi ro thực sự, còn Q1728-LE 4 GB rơi đúng cấu hình mà Axis đã test.

## Benchmark của Axis áp dụng cho camera nào

Bảng benchmark của Axis Model Zoo (AXIS OS 12.11.72) ghi platform là `ARTPEC-9 (Q1728)` — tức Q1728 thường, không phải Q1728-LE và không phải P1488-LE (**Observed** trên README).[^mz-readme] Với ARTPEC-9, các dòng đã có số đo gồm MobileNetV2 (2.02 ms), SSD MobileNet v2 (10.48 ms), SSDLite MobileDet (21.48 ms) và YOLOv5n/s/m (31.85 / 35.00 / 42.70 ms). Chi tiết bảng và cách quy đổi nằm ở [Axis Model Zoo benchmark results](axis-model-zoo-benchmark-results.md).

Ba giới hạn khi dùng các số này để chọn giữa hai camera:

- Thiết bị đo không phải hai camera đang so sánh, nên không được coi là FPS của Q1728-LE hay P1488-LE.
- Số công bố là thời gian inference trung bình của job Larod, không phải FPS end-to-end của ứng dụng (capture, preprocessing, post-processing và phần chạy CPU vẫn cộng thêm).
- Cùng một SoC vẫn có thể cho kết quả khác nhau giữa các camera: bảng của Model Zoo cho thấy hai camera ARTPEC-8 chênh nhau tới 1.85× trên cùng model bytes, và README không giải thích nguyên nhân (xem [benchmark results](axis-model-zoo-benchmark-results.md)).

Vì vậy quy tắc thực dụng là: dùng bảng ARTPEC-9 để **chọn họ model và cỡ model**, rồi đo lại trên đúng camera sẽ triển khai (**Synthesis**).

## Model nào đã có bằng chứng trên ARTPEC-9

- **YOLOv5n/s/m:** là lựa chọn có cơ sở rõ ràng nhất để bắt đầu — có artifact `.tflite` riêng cho ARTPEC-9, có số benchmark, và hướng dẫn huấn luyện kèm patch của Axis.[^mz-readme][^mz-yolov5]
- **SSD MobileNetV2 / SSDLite MobileDet:** có số đo trên ARTPEC-9 và phù hợp để thử pipeline trước khi đầu tư model riêng.[^mz-readme]
- **YOLOv8:** bằng chứng duy nhất trong Model Zoo là dòng YOLOv8n_det trên CV75, không phải trên ARTPEC-9; đây không phải bằng chứng YOLOv8 chạy được trên DLPU ARTPEC-9.[^mz-readme]
- **YOLO11:** không có benchmark chính thức tương ứng trong Model Zoo; vẫn phải kiểm operator, quantization và chạy thử thực tế.[^mz-readme]

Danh sách này chỉ nói về **bằng chứng công bố**, không phải danh sách tương thích: một model không có trong bảng vẫn có thể chạy nếu nằm trong tập operator được hỗ trợ. Ràng buộc operator/quantization/layout và trạng thái bằng chứng theo họ model nằm ở [Giới hạn model trên DLPU](axis-dlpu-model-constraints.md) và [bảng operator ARTPEC-9](axis-artpec-9-operator-support.md).

## Nên chọn camera nào

- Nếu ưu tiên phát triển ứng dụng AI tùy chỉnh chạy trực tiếp trên camera, Q1728-LE là lựa chọn mặc định hợp lý vì 4 GB RAM, trong khi đường model và DLPU giống P1488-LE (**Synthesis** từ bảng phần cứng và cảnh báo bộ nhớ của hướng dẫn YOLOv5).[^mz-yolov5]
- P1488-LE vẫn đúng nếu ràng buộc là form factor bullet/lắp đặt ngoài trời: cùng ARTPEC-9, cùng `a9-dlpu-tflite`, nhưng phải chấp nhận 2 GB RAM và giới hạn cỡ model.
- Cả hai trường hợp, đường triển khai giống nhau: ACAP Native SDK + Video Capture API (VDO) + Machine Learning API (Larod), bắt đầu từ model YOLOv5 mà Axis cung cấp rồi mới thay bằng model riêng. Quy trình chung ở [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md); nhánh ARTPEC-9 ở [Chuyển model sang ARTPEC-9](axis-artpec-9-model-conversion.md).[^axis-camera-chatgpt-research]

Khuyến nghị trên là quyết định kỹ thuật dựa trên thông số, không phải kết quả đo: khả năng chạy model và FPS thực tế vẫn phải kiểm chứng bằng model cụ thể trên từng camera.

## Giới hạn coverage

- Nguồn là **research thứ cấp** (một bản tra cứu do trợ lý AI tổng hợp, không phải trang vendor). Trang sản phẩm `axis.com` của Q1728-LE và P1488-LE, datasheet và Product Selector đều không có trong `raw/`, nên mọi thông số phần cứng ở đây chưa được đối chiếu vendor.
- Nguồn không nêu phiên bản AXIS OS hay firmware cho các thông số sản phẩm; `stale_after` đặt theo quy ước domain `edge-ai` vì đây là dữ liệu phụ thuộc model máy.
- Không nhất quán nội bộ của nguồn: Q1728-LE không có RAM/Flash ở §1 nhưng có ở §2 (xem trên).
- Không chạy gì: không có camera ARTPEC-9 trong môi trường ingest, nên lệnh `larod-client` và mọi con số FPS đều không **Reproduced**.
- Ảnh/favicon trong nguồn là link ngoài (favicon Google, thumbnail sản phẩm) và không được tải — bị loại vì trang trí.

## Relationships

- **Depends on** [Axis DLPU](axis-dlpu.md) và đường chuyển model [ARTPEC-9](axis-artpec-9-model-conversion.md): cả hai camera dùng `a9-dlpu-tflite` và `.tflite` lượng tử hóa, không cần compiler offline.
- **Refines** [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md): biến "chọn SoC ARTPEC-9" thành chọn giữa hai model máy cụ thể.
- **Constrained by** [Giới hạn model trên DLPU](axis-dlpu-model-constraints.md) và [bảng operator ARTPEC-9](axis-artpec-9-operator-support.md).
- **Uses** [Axis Model Zoo benchmark results](axis-model-zoo-benchmark-results.md): nguồn số đo duy nhất cho ARTPEC-9, nhưng đo trên Q1728 thường.
- **Corroborated by** [ACAP generations, chip architectures and SDK-to-Axis OS compatibility](acap-chip-architecture-and-sdk-compatibility.md) cho kiến trúc `aarch64` của ARTPEC-9.
- **Guided by** [Hướng triển khai custom AI trên Axis](axis-edge-ai-adoption-guide.md) khi cần quyết định PoC trước khi mua thiết bị.

## Độ tin cậy

Bảng phần cứng và khuyến nghị chọn máy là **Reported** từ nguồn thứ cấp, chưa đối chiếu với trang sản phẩm Axis (không có cục bộ). Sự tương thích `aarch64` và cảnh báo bộ nhớ 4 GB cho YOLOv5 ARTPEC-9 là **Observed** trên tài liệu cục bộ trong `raw/` (bảng chip ACAP và `axis-model-zoo/docs/yolov5.md`). Phần suy luận "RAM không tăng tốc DLPU", "2 GB là biến rủi ro cho model lớn" và khuyến nghị chọn Q1728-LE là **Synthesis**. Không có claim nào **Reproduced** — không thiết bị, không chạy `larod-client`.

[^axis-camera-chatgpt-research]: Nguồn thứ cấp: [Kết quả tra cứu SoC của AXIS Q1728-LE và AXIS P1488-LE](../raw/axis-camera-chatgpt-research.md), §1 "So sánh phần cứng hai camera", §2 "Đối chiếu bảng SoC và Larod của bạn", §3 "Cách chuyển model để chạy trên hai camera" và §7 "Nên chọn camera nào để triển khai AI?".
[^mz-readme]: Repository (cục bộ, revision `v1.0.7-42-g66bf5ea`): [axis-model-zoo README](../raw/axis-model-zoo/README.md), bảng "Object Detection" các dòng `ARTPEC-9 (Q1728)` và `CV75 (M2048-LE)` và dòng ghi chú *"Values for AXIS OS 12.11.72."*.
[^mz-yolov5]: Repository (cục bộ, revision `v1.0.7-42-g66bf5ea`): [axis-model-zoo — docs/yolov5.md](../raw/axis-model-zoo/docs/yolov5.md), đoạn mở đầu: YOLOv5 được test với yolov5n/s/m trên Q1728 4 GB cho ARTPEC-9, và cảnh báo thiết bị ít bộ nhớ hơn có thể gặp vấn đề với model lớn hơn.
[^axis-doc-artpec9-model-conversion]: Tài liệu chính thức: [Model Conversion (ARTPEC-9) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md), §How to accelerate your model on ARTPEC-9, bước 2–3 (`larod-client ... -c a9-dlpu-tflite`, không có bước compiler).
