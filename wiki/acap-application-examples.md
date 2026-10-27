---
type: Concept
title: "Ví dụ ứng dụng ACAP chính thức"
description: "Kho acap-native-sdk-examples của Axis: mỗi API có ít nhất một ví dụ, các mẫu tích hợp computer vision như vdo-larod, object-detection và object-detection-yolov5, và cách tra theo use case."
tags: [edge-ai, axis, acap, examples]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-app-examples
    resource: ../raw/acap/get-started/acap-application-examples/index.md
    scope: ../raw/acap/get-started/acap-application-examples/
    kind: docs
    revision: "ACAP version 12"
    title: "ACAP application examples | Axis developer documentation"
  - id: acap-cv-on-device
    resource: ../raw/acap/how-to-guides/computer-vision-on-device/index.md
    scope: ../raw/acap/how-to-guides/computer-vision-on-device/
    kind: docs
    revision: "ACAP version 12"
    title: "Run computer vision models inside ACAP applications | Axis developer documentation"
  - id: acap-remote-debug
    resource: ../raw/acap/how-to-guides/debugging/index.md
    scope: ../raw/acap/how-to-guides/debugging/
    kind: docs
    revision: "ACAP version 12"
    title: "Debugging | Axis developer documentation"
---

# Ví dụ ứng dụng ACAP chính thức

Axis cung cấp bộ ví dụ ứng dụng ACAP mã nguồn mở trong repository GitHub `AxisCommunications/acap-native-sdk-examples`. Bộ ví dụ này là điểm bắt đầu thực hành cho ACAP Native SDK: mỗi API có ít nhất một ví dụ, một số ví dụ lớn kết hợp nhiều API, và mỗi ví dụ có README riêng để build và chạy ứng dụng.[^acap-app-examples]

## Nội dung bộ ví dụ

Theo trang giới thiệu của Axis:[^acap-app-examples]

| Khía cạnh | Thông tin |
| --- | --- |
| Vị trí | GitHub repository `AxisCommunications/acap-native-sdk-examples` |
| Giấy phép | Open-source; trang giới thiệu không nêu tên giấy phép cụ thể |
| Độ phủ API | Ít nhất một ví dụ cho mỗi API trong ACAP Native SDK |
| Tổ chức | README của repository phân loại ví dụ theo use case |
| Hướng dẫn | README của từng ví dụ có hướng dẫn build và chạy |
| Phản hồi | Issue trên repository GitHub |

Ví dụ tổng hợp được nêu tên là `object-detection-yolov5`. Ứng dụng này kết hợp bốn API: Video capture API (VDO) để lấy frame, Machine learning API (Larod) để chạy model, Parameter API để đọc/ghi tham số, và Bounding Box API để làm việc với bounding box.[^acap-app-examples]

Trang how-to computer vision on device của Axis nêu thêm hai ví dụ để tham khảo khi tích hợp model vào application: `vdo-larod` và `object-detection`, bên cạnh `object-detection-yolov5`. Trang nguồn chỉ nêu tên và dẫn tới repository GitHub, không mô tả nội dung từng ví dụ.[^acap-cv-on-device]

Bộ ví dụ cũng có `remote-debug-example`, ví dụ minh họa remote debugging application bằng GNU Debugger (GDB) và VS Code; trang debugging của Axis chỉ dẫn tới nó và không chép lại các bước. README và mã nguồn của chính ví dụ này đã được đọc và ghi lại ở trang remote debugging.[^acap-remote-debug] Chi tiết về phương pháp nằm ở [Remote debugging ACAP applications with GDB and VS Code](acap-remote-debugging.md).

Một ví dụ đã có trong `raw/`: thư mục `raw/acap-native-sdk-examples/vapix/` (submodule acap-native-sdk-examples) chứa README, `app/manifest.json`, `app/vapix_example.c`, `Makefile` và `Dockerfile` của ứng dụng gọi VAPIX. Luồng lấy credential qua D-Bus và gọi VAPIX trên `127.0.0.12` được biên soạn ở [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).

Thư mục `raw/acap-native-sdk-examples/web-server/` cũng đã có trong `raw/`: hai ví dụ `reverse-proxy-using-fixed-port` (CivetWeb + Apache reverse proxy) và `http-requests-using-fastcgi` (FastCGI trên Apache của thiết bị), mỗi ví dụ có README, `app/manifest.json`, `Makefile`, `Dockerfile` và mã nguồn C. Cách hai ví dụ này expose HTTP API được biên soạn ở [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md).

## Cách dùng trong thực hành

**Synthesis:** Khi cần tích hợp một API cụ thể, nên đọc README phân loại theo use case trước để chọn ví dụ gần với bài toán, sau đó đọc README của ví dụ để lấy lệnh build và cách chạy. Với bài toán cần nhiều API phối hợp, `object-detection-yolov5` là mẫu tham chiếu cho luồng VDO → Larod → xử lý kết quả → bounding box. Trang này không thay thế API reference; nó chỉ ra ví dụ để đọc song song.[^acap-app-examples]

## Độ phủ nguồn

- Entry point: `raw/acap/get-started/acap-application-examples/index.md`, 167 từ, thuộc bộ tài liệu ACAP 12, site `developer.axis.com`.
- Đã kiểm tra toàn bộ trang; trang không có mục con, hình ảnh hay tệp đính kèm.
- **Cập nhật 2026-10-27:** toàn bộ repository (revision `12.11.0-7-g3025a4e`) đã được ingest từng phần; xem [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md) làm danh mục và bảng đối chiếu. Các câu “chưa được kiểm chứng” ở dưới chỉ còn mô tả trạng thái của nguồn tài liệu Axis, không còn mô tả trạng thái của repository.
- Ngoại lệ đã kiểm chứng: `raw/acap-native-sdk-examples/vapix/` (revision `12.11.0-7-g3025a4e`) đã đọc README, manifest và mã nguồn, ghi lại ở [VAPIX access from ACAP applications](acap-vapix-service-account-access.md). `Makefile`, `LICENSE` và `Dockerfile` của ví dụ này chưa được phân tích.
- Ngoại lệ đã kiểm chứng thứ hai: `raw/acap-native-sdk-examples/web-server/` cùng revision, đã đọc cả hai README, hai `app/manifest.json`, hai `Makefile`, hai `Dockerfile`, `web_server_rev_proxy.c`, `fastcgi_example.c` và các file `html/`; ghi lại ở [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md).
- Trang không nêu ngày xuất bản hoặc cập nhật; `revision` chỉ suy ra từ tiêu đề bộ tài liệu "ACAP version 12".
- Nguồn bổ sung `raw/acap/how-to-guides/computer-vision-on-device/index.md` (137 từ) thêm tên `vdo-larod` và `object-detection`; nội dung và cách build của hai ví dụ này hiện được mô tả ở [Larod inference examples](acap-example-larod-object-detection.md).

## Độ tin cậy

Các thông tin về repository, độ phủ API, cách tổ chức README và tên các ví dụ `object-detection-yolov5`, `vdo-larod`, `object-detection` là **Reported** từ tài liệu chính thức của Axis. Trang này không có claim nào **Observed** trên repository hay **Reproduced**; các quan sát trên mã nguồn nằm ở các trang ví dụ liên kết trong Relationships. Việc "mỗi API có ít nhất một ví dụ" là tuyên bố của nhà cung cấp, chưa được đối chiếu với danh sách API reference.

## Relationships

- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): bộ ví dụ dùng API và toolchain của SDK.
- **Uses** VDO, Larod, Parameter API và Bounding Box API trong ví dụ `object-detection-yolov5`.
- **Documented by** README của repository và từng ví dụ, nay đã có trong `raw/` và được biên soạn tại [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md) cùng các trang phân nhóm: [build và manifest](acap-examples-build-and-manifest-conventions.md), [contribution, lint và CI](acap-examples-contribution-lint-and-ci.md), [VDO và OpenCL](acap-example-vdo-video-capture-and-opencl.md), [overlay và bounding box](acap-example-overlays-and-bounding-box.md), [Larod](acap-example-larod-object-detection.md), [CV25](acap-example-object-detection-cv25.md), [training guides](acap-example-model-training-guides.md), [events và parameters](acap-example-events-and-parameters.md), [Device Data Hub và Message Broker](acap-example-device-data-hub-and-message-broker.md), [PTZ WebSocket](acap-example-ptz-control-ws-api.md), [audio](acap-example-audio-pipewire.md), [storage, serial, recording, licensekey](acap-example-storage-serial-recording-licensekey.md), [thư viện bundle](acap-example-bundled-libraries-opencv-curl-openssl.md), [ví dụ tối thiểu và reproducible](acap-example-minimal-shell-and-reproducible-package.md) và [container](acap-example-container-in-native-acap.md).
- **Supports** [quy trình triển khai custom AI model](axis-custom-model-deployment.md) bằng mẫu build, packaging và kiểm tra model.
- **Counterpart** (container era, archived): [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md) — bảy ví dụ Docker cho camera aarch64, đã được ingest riêng.
- **Includes** `remote-debug-example`, được ghi lại ở [Remote debugging ACAP applications with GDB and VS Code](acap-remote-debugging.md).
- **Includes** `vapix`, được ghi lại ở [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).
- **Includes** `web-server/reverse-proxy-using-fixed-port` và `web-server/http-requests-using-fastcgi`, được ghi lại ở [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md).
- **Linked from** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): trang SDK mô tả workflow, còn how-to computer vision on device coi các ví dụ này là điểm bắt đầu khi tích hợp model vào application.

[^acap-app-examples]: Tài liệu chính thức: [ACAP application examples — Axis developer documentation](../raw/acap/get-started/acap-application-examples/index.md), toàn bộ phần nội dung chính (trang 167 từ, không chia mục); các liên kết tới repository và API reference là external link chưa được kiểm chứng.

[^acap-cv-on-device]: Tài liệu chính thức: [Run computer vision models inside ACAP applications — Axis developer documentation](../raw/acap/how-to-guides/computer-vision-on-device/index.md), §Integrate a model with an ACAP application; các repository được liên kết là external link chưa được kiểm chứng.

[^acap-remote-debug]: Tài liệu chính thức: [Debugging — Axis developer documentation](../raw/acap/how-to-guides/debugging/index.md), toàn bộ trang; liên kết tới `remote-debug-example` là external link chưa được kiểm chứng.
