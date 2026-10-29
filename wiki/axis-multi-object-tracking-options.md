---
type: Synthesis
title: "Multi-object tracking sau detection trên camera Axis"
description: "Các phương án dùng Axis Scene Metadata, native ACAP tracker hoặc offload, cùng điểm tích hợp, rủi ro và kế hoạch PoC trên ARTPEC-9."
tags: [edge-ai, axis, multi-object-tracking, acap]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T03:41:16Z }
stale_after: 2027-04-30
sources:
  - id: examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e"
    title: ACAP Native SDK examples
  - id: cameras
    resource: ../raw/axis-camera-chatgpt-research.md
    kind: research
    title: Nghiên cứu thứ cấp về camera Axis ARTPEC-9
  - id: model-zoo
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: Axis Model Zoo
---

# Multi-object tracking sau detection trên camera Axis

**Synthesis:** Nếu dùng được detector của Axis, thử tiêu thụ Scene Metadata đã có track ID trước; nếu cần tracking detection custom, bắt đầu native ACAP với tracker motion/IoU hoặc ByteTrack-style trên CPU, sau đó mới cân nhắc appearance/ReID hoặc offload. Đây là phương án thiết kế, không phải benchmark hay xác nhận tương thích thư viện trên camera.[^examples]

## Cơ sở và lựa chọn

- **Observed:** Message Broker example nhận `com.axis.analytics_scene_description.v0.beta` theo frame với box, timestamp, `track_id` và delete operation; Device Data Hub example nhận `com.axis.scene.object_track.v1` với id, path và timestamps. Không có bằng chứng example cho phép truyền box detector custom vào tracker Axis. Kiểm tra producer, firmware, thời điểm phát, quyền và API beta trên máy thật.[^examples]
- **Observed:** Native YOLOv5 example đọc VDO, inference Larod, lọc confidence và NMS, rồi vẽ box; có điểm gắn tracker sau NMS. Score của code phân biệt object likelihood và class likelihood, cần thống nhất semantics trước khi tuning. NMS ví dụ quadratic và lọc confidence trước NMS; tracker cần low-score box phải nhận được chúng.[^examples]
- **Synthesis:** SORT-style Kalman + IoU/Hungarian là baseline nhẹ; ByteTrack-style ghép hai mức confidence là lựa chọn tiếp theo khi detector hay mất chắc chắn; appearance/ReID có thể giúp khi che khuất nhưng cần đo thêm CPU/DLPU, crop và kiểm tương thích model. Chưa tìm thấy implementation hay benchmark các tracker này trong các nguồn Axis đã khảo sát.
- **Synthesis:** Alternative là gửi detections và timestamp đến edge server để track tập trung, hoặc stream video để xử lý toàn bộ ngoài camera; hai đường có chi phí mạng, đồng bộ, riêng tư và lỗi mạng khác nhau. Không suy ra một giao thức detection-export cụ thể đã được Axis hỗ trợ từ các example này.

## Các điều kiện triển khai

Timestamp monotonic, thứ tự frame, xử lý dropped frame, phép chiếu crop/resize/rotation, vòng đời ID theo camera và session, threshold, NMS, class gating, timeout theo thời gian và tránh đếm lặp đều cần được xác định và test. Overlay box, event và data hub là các đường xuất khác nhau; Device Data Hub không nhằm stream binary.[^examples] Chọn track ID riêng cho từng camera; multi-camera identity cần bài toán association riêng.

Theo nghiên cứu thứ cấp, Q1728-LE và P1488-LE đều ARTPEC-9, RAM lần lượt 4 GB và 2 GB, nhưng datasheet chính hãng không có trong raw; đo trên đúng thiết bị. Axis Model Zoo đo ARTPEC-9 trên Q1728, không phải hai model LE, và inference timing không phải tracking FPS end-to-end.[^cameras][^model-zoo]

## Kiểm chứng và giới hạn

Dùng cùng clip và ground truth để so sánh IDF1, HOTA, ID switches, fragmentation và count error; đo end-to-end latency p50/p95, FPS, CPU, RAM và tải khi chạy dài ngày. Bao phủ cảnh đông, che khuất, đêm, đối tượng nhỏ, crossing, restart và mất kết nối. Chưa build, chạy camera hoặc benchmark tracker; không xác nhận tính sẵn có của các topic trên hai model, giấy phép hay khả năng cross-compile của bất kỳ thư viện tracker nào. Các thuật toán cụ thể là đề xuất cần nguồn và thử nghiệm độc lập.

## Relationships

- **Uses** [Larod object detection examples](acap-example-larod-object-detection.md) và [Scene Metadata examples](acap-example-device-data-hub-and-message-broker.md).
- **Constrained by** [camera selection](axis-artpec-9-camera-selection.md) và [model benchmark](axis-model-zoo-benchmark-results.md).
- **Uses** [overlay examples](acap-example-overlays-and-bounding-box.md) khi cần hiển thị.

[^examples]: `message-broker/consume-scene-metadata/README.md`, mục Introduction và payload; `device-data-hub/consume-scene-metadata/README.md`, payload và manifest; `device-data-hub/README.md`, mục About; `object-detection-yolov5/app/object_detection_yolov5.c::filter_detections, non_maximum_suppression, determine_class_and_object_likelihood`; `object-detection-yolov5/README.md`.
[^cameras]: `axis-camera-chatgpt-research.md`, §1–2; thông số là nguồn thứ cấp, chưa đối chiếu datasheet.
[^model-zoo]: `README.md`, bảng Object Detection, dòng ARTPEC-9 (Q1728) và thông tin benchmark.
