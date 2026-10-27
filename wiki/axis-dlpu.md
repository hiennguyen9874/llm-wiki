---
type: Concept
title: "Axis DLPU (Deep Learning Processing Unit)"
description: "Bộ tăng tốc inference trong camera Axis: vai trò so với CPU, năm SoC có DLPU, cách xác định DLPU theo SoC, vị trí trong pipeline, cùng use case và lợi ích của edge inference."
tags: [edge-ai, axis, dlpu, hardware, computer-vision]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:49:15Z }
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
  - id: axis-doc-computer-vision-index
    resource: ../raw/computer-vision/index.md
    kind: docs
    title: "Computer vision — Axis developer documentation"
---

# Axis DLPU (Deep Learning Processing Unit)

DLPU là bộ tăng tốc phần cứng dành cho inference neural network, được tích hợp trong một số sản phẩm Axis. Axis thiết kế DLPU để thực thi model nhanh hơn đáng kể so với CPU, nhưng đổi lại DLPU bị giới hạn hơn CPU đa dụng về những gì nó có thể xử lý. Nó không thay thế CPU cho toàn bộ ứng dụng: DLPU chủ yếu tăng tốc các phép toán của mạng, còn logic ứng dụng và những phép toán không được hỗ trợ vẫn chạy trên CPU.[^axis-doc-dlpu][^axis-ai-chatgpt-research]

## Vị trí trong pipeline

```text
Camera sensor
  → Image / video capture
  → AXIS OS + ACAP application
  → VDO API: lấy frame, resize, crop, preprocessing
  → Larod Machine Learning API: nạp model, điều phối inference
  → DLPU: accelerated inference
  → CPU: ứng dụng, phép toán hỗ trợ, custom post-processing, integration
  → Detection, tracking, event, metadata, VMS, HTTP
```

Điểm quan trọng là DLPU chủ yếu tăng tốc phép toán neural network; tracking, rule engine, kết nối server và xử lý kết quả model có thể chạy trên CPU. Một model cũng có thể chứa phép toán không được DLPU hỗ trợ. Một số nền tảng có khả năng chuyển phần đó sang CPU, nhưng việc chuyển qua lại giữa CPU và DLPU làm tăng latency.[^axis-ai-chatgpt-research]

## Nền tảng SoC có DLPU

Không phải mọi sản phẩm Axis đều có DLPU, và các sản phẩm có DLPU không dùng cùng một loại DLPU. Axis xác định loại DLPU của một sản phẩm qua tên System on Chip (SoC); hiện có năm SoC hỗ trợ tăng tốc bằng DLPU: ARTPEC-7, ARTPEC-8, ARTPEC-9, Ambarella CV25 và Ambarella CV75. Để tìm sản phẩm có DLPU, dùng Product Selector với bộ lọc trong mục "Hardware platform".[^axis-doc-dlpu]

Năm SoC này hoạt động và cho hiệu năng khác nhau, đồng thời quy trình đưa model lên DLPU cũng khác nhau theo SoC. Axis xếp ARTPEC-7 là dễ nhất trong nhóm DLPU, ARTPEC-8 và ARTPEC-9 ở mức trung bình, CV25 và CV75 ở mức khó; tốc độ chỉ được mô tả định tính và cố ý không định lượng vì phụ thuộc model, mức tối ưu hóa và cấu hình phần cứng như clock và memory. Đường chuyển đổi model cụ thể theo từng SoC nằm ở [quy trình triển khai](axis-custom-model-deployment.md), với nhánh CV75 chi tiết ở [Chuyển model ONNX sang định dạng native cho CV75](axis-cv75-onnx-conversion.md).[^axis-doc-dlpu]

Việc camera thuộc dòng M, P hay Q không phải tiêu chí quyết định bằng SoC.[^axis-ai-chatgpt-research] Có DLPU là điều kiện cần nhưng chưa đủ để một model đã convert chạy được: còn phải kiểm tra bộ nhớ, phiên bản AXIS OS, ACAP API và tập operator được hỗ trợ.

## Ứng dụng và lợi ích của edge inference

Axis định vị DLPU là nền tảng chạy custom computer vision application ngay trên camera: model tự huấn luyện được triển khai tại edge để phân tích video thời gian thực, giảm phụ thuộc xử lý trên cloud và cải thiện hiệu quả hệ thống. DLPU được thiết kế cho object detection, classification và tracking thời gian thực.[^axis-doc-computer-vision-index]

Ba nhóm ứng dụng vendor nêu:[^axis-doc-computer-vision-index]

- **Object and people detection** — nhận diện object, người hoặc phương tiện ngay trên camera.
- **Behavior analysis and anomaly detection** — nhận ra hoạt động bất thường và trigger event.
- **Traffic and retail analytics** — theo dõi pattern di chuyển để lấy insight và tự động hóa.

Năm lợi ích vendor quy cho edge processing:[^axis-doc-computer-vision-index]

- **Efficient edge processing** — không cần server ngoài, giảm chi phí và độ phức tạp hạ tầng.
- **Low latency** — inference thời gian thực ngay trên camera cho quyết định nhanh hơn.
- **Reduced bandwidth** — chỉ truyền metadata thay vì raw video stream.
- **Scalability** — triển khai application trên nhiều camera trong mạng.
- **Security and privacy** — dữ liệu nhạy cảm ở on-premise, giảm exposure ra mạng ngoài.

Đây là positioning của Axis, không phải kết quả benchmark độc lập: trang không nêu con số latency, bandwidth hay độ chính xác, và mức đạt được của từng lợi ích phụ thuộc model, cấu hình camera và hạ tầng thực tế.

## Relationships

- **Part of** [khả năng tùy biến AI trên camera Axis](axis-custom-ai-capability.md).
- **Exposes** inference qua Larod trong [ACAP Native SDK](axis-acap-native-sdk.md).
- **Constrained by** [giới hạn model và operator](axis-dlpu-model-constraints.md).
- **Deployed through** [quy trình triển khai custom model](axis-custom-model-deployment.md).
- **Present on** ARTPEC-7/8/9 và Ambarella CV25/CV75.

## Độ tin cậy

Định nghĩa DLPU, danh sách năm SoC và cách xác định DLPU theo SoC nay là **Reported** từ tài liệu vendor Axis, thay cho mô tả chỉ dựa trên nguồn thứ cấp trước đây. Danh sách use case và năm lợi ích của edge inference là **Reported** từ trang tổng quan Computer vision của Axis, mang tính positioning và không kèm số đo. Kiến trúc pipeline chi tiết (VDO → Larod → DLPU → CPU) vẫn là **Reported** từ nguồn thứ cấp và chưa được tài liệu vendor cục bộ xác nhận từng bước. Các trang vendor không kèm attachment kỹ thuật nào cần kiểm tra thêm. Không có claim nào được **Reproduced** trong lần ingest này.

[^axis-doc-dlpu]: Tài liệu chính thức: [Axis Deep Learning Processing Unit (DLPU) — Axis developer documentation](../raw/computer-vision/on-device/axis-dlpu/index.md), phần mở đầu và §Axis products with DLPU, gồm bảng SoC / Speed / Ease of use / Conversion from source model.
[^axis-ai-chatgpt-research]: Nguồn thứ cấp: [Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis](../raw/axis-ai-chatgpt-research.md), §2 "Axis DLPU thực sự là gì?" và §3 "Những dòng camera Axis nào hỗ trợ deploy custom AI model?".
[^axis-doc-computer-vision-index]: Tài liệu chính thức: [Computer vision — Axis developer documentation](../raw/computer-vision/index.md), §Leverage the DLPU for Edge AI và §Benefits of running deep learning on Axis cameras.
