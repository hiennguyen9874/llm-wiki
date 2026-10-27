---
type: Concept
title: "ACAP Native SDK và nền tảng ứng dụng camera Axis"
description: "Nền tảng phát triển ứng dụng camera Axis: API VDO/Larod/overlay/event, đóng gói .eap, ranh giới SDK mở và lộ trình thay thế container bằng native."
tags: [edge-ai, axis, acap, sdk]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-ai-chatgpt-research
    resource: ../raw/axis-ai-chatgpt-research.md
    kind: research
    title: "Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis"
  - id: acap-docs-index-v12
    resource: ../raw/acap/index/index.md
    scope: ../raw/acap/index/
    kind: docs
    revision: "ACAP version 12"
    title: "ACAP version 12 | Axis developer documentation"
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
  - id: acap-container-build-run
    resource: ../raw/acap/reference/develop-container-applications/build-install-run/index.md
    scope: ../raw/acap/reference/develop-container-applications/build-install-run/
    kind: docs
    revision: "ACAP version 12"
    title: "Build, install, run | Axis developer documentation"
---

# ACAP Native SDK và nền tảng ứng dụng camera Axis

ACAP (AXIS Camera Application Platform) là nền tảng để phát triển ứng dụng chạy trực tiếp trên camera Axis. SDK công khai, có tài liệu developer và repository ví dụ trên GitHub; ứng dụng native được đóng gói thành `.eap` và cài qua web GUI hoặc VAPIX Application API. Axis xác nhận có thể chạy custom computer vision application bằng VDO và Larod.[^axis-ai-chatgpt-research]

## Nền tảng và toolchain theo tài liệu Axis

Tài liệu chính thức mô tả ACAP là **open development framework** để phát triển ứng dụng chạy trực tiếp trên thiết bị mạng Axis, không chỉ camera mà còn intercom, loa (speaker) và radar. Vì ứng dụng dùng khả năng xử lý trên thiết bị, dữ liệu được xử lý cục bộ: giảm latency hệ thống, giảm băng thông và cho phép triển khai phân tán quy mô lớn. ACAP Native SDK cung cấp API, công cụ và runtime cần thiết để develop, package và deploy application trên thiết bị chạy AXIS OS.[^acap-docs-index-v12]

Các tính năng nền tảng mà tài liệu nêu:[^acap-docs-index-v12]

- Truy cập phần lớn tính năng sản phẩm: video, event system, parameter system và cổng I/O.
- Tăng tốc phần cứng cho một số tác vụ như tính toán image analysis và overlay graphics.
- Toolchain hỗ trợ nhiều kiến trúc để build cho toàn bộ thiết bị Axis hỗ trợ ACAP.
- Tài liệu, tutorial và example application cho các API.

Toolchain chạy bằng Docker và được phân phối dưới dạng container, nên môi trường phát triển tách khỏi OS của máy host và cho cùng một trải nghiệm build trên Linux, Windows và macOS. Docker chỉ cần trên máy phát triển để build SDK, không phải runtime trên camera — khớp với phần build và đóng gói bên dưới.[^acap-docs-index-v12]

Phiên bản ACAP dùng để build phải khớp AXIS OS LTS của thiết bị đích; quy tắc chọn phiên bản nằm ở [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md).[^acap-docs-index-v12]

## Khả năng SDK công khai

| Khả năng | Hỗ trợ | Chi tiết |
| --- | --- | --- |
| Custom model weights | Có | Tự train, quantize và deploy |
| Custom neural network architecture | Có điều kiện | Phải phù hợp supported operators |
| Custom preprocessing | Có | Resize, crop, format conversion |
| Custom post-processing | Có | NMS, tracking, logic ứng dụng |
| Video frame capture | Có | VDO API |
| DLPU inference | Có | Larod API |
| Bounding box / overlay | Có | Bounding Box, Axoverlay APIs |
| Custom event | Có | Axevent API |
| Giao tiếp HTTP/VMS | Có | VAPIX, HTTP integration |
| Third-party libraries | Có điều kiện | Phụ thuộc runtime, kiến trúc, tài nguyên; phải cross-compile và bundle trong application ([quy trình](acap-third-party-libraries.md)) |
| Custom accelerator driver / firmware | Không có API công khai được tài liệu hóa | Phải dựa vào interface do Axis cung cấp |

Ví dụ, một ứng dụng phát hiện hàng hóa trên băng chuyền có thể dùng VDO để lấy frame, Larod để chạy model trên DLPU, C++ để làm NMS/tracking/đếm sản phẩm, vẽ bounding box lên luồng video, rồi phát event khi có sản phẩm lỗi và gửi kết quả về backend hoặc VMS. Tất cả thực hiện trong application mà không cần sửa source code AXIS OS.[^axis-ai-chatgpt-research]

## Computer vision trên thiết bị

How-to chính thức của Axis tách công việc chạy computer vision trên camera thành hai phần. Phần một là chuẩn bị model — train, convert và tối ưu cho thiết bị Axis — theo tài liệu Computer Vision. Phần hai là tích hợp model vào ACAP application: dùng Video capture API (VDO) để lấy frame từ camera và Machine learning API (Larod) để chạy inference tăng tốc DLPU. Mục tiêu của hướng này là phân tích video theo thời gian thực ngay trên thiết bị, giảm phụ thuộc vào xử lý trên cloud.[^acap-cv-on-device]

Trang nguồn chỉ là điểm nối giữa hai bộ tài liệu; nội dung train/convert/optimize nằm ở tài liệu Computer Vision bên ngoài `raw/`. **Observed:** bản capture hiện có của `raw/` không chứa các trang đó, nên phần chuẩn bị model chưa được kiểm chứng ở đây; phần convert và kiểm tra model đã ingest từ nguồn khác được tổng hợp tại [triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md).[^acap-cv-on-device]

## ACAP không phải SDK để viết NPU kernel

Axis không cung cấp ACAP như môi trường để developer tùy ý định nghĩa instruction set hoặc lập trình trực tiếp các đơn vị tính toán trong DLPU. Inference được cung cấp qua Larod, thành phần điều phối truy cập phần cứng giữa các application.[^axis-ai-chatgpt-research]

- Custom application logic: mức linh hoạt cao.
- Custom model graph: linh hoạt trong phạm vi khả năng của DLPU.
- Custom hardware execution: phụ thuộc backend và các operator Axis hỗ trợ.

Open development framework không đồng nghĩa toàn bộ SDK, runtime, driver và firmware đều open-source. Repository ví dụ của Axis dùng Apache-2.0, nhưng không mở mã nguồn của mọi thành phần bên dưới.[^axis-ai-chatgpt-research]

## Build và đóng gói

Với ACAP Native SDK, developer build ứng dụng bằng Docker trên máy phát triển; kết quả là package `.eap` để cài lên camera. Toolchain phụ thuộc kiến trúc: `armv7hf` cho ARTPEC-7, `aarch64` cho ARTPEC-8/9. Docker ở đây dùng để build SDK, không có nghĩa camera phải chạy Docker container. Cấu trúc application mẫu và lệnh kiểm tra model được trình bày ở [quy trình triển khai](axis-custom-model-deployment.md).[^axis-ai-chatgpt-research]

## Chuyển dịch từ container sang Native SDK

Axis từng có hai hướng phát triển chính:

| | ACAP Native SDK | ACAP Computer Vision SDK / Solution |
| --- | --- | --- |
| Ngôn ngữ chủ đạo | C/C++ | Python và các ngôn ngữ container hỗ trợ |
| Kiểu ứng dụng | Native `.eap` | Container |
| Mức độ tích hợp camera | Trực tiếp qua Axis APIs | Qua container và runtime integration |
| Định hướng hiện tại | Được Axis khuyến nghị | Deprecated |

Tài liệu vendor cho hướng container xác nhận trực tiếp các mốc lifecycle:[^acap-container-build-run]

- Container path là legacy: ACAP Computer Vision SDK bị archive từ AXIS OS 12.0, utility library và script chuyển sang ACAP Runtime.
- Sản phẩm Axis mới phát hành trên AXIS OS 12.x không có container support.
- Sản phẩm đã hỗ trợ container từ trước được hỗ trợ đến hết năm 2031, khi AXIS OS 2026 LTS hết vòng đời.
- Axis khuyến nghị ACAP Native SDK cho application analytics, computer vision và machine learning mới.

Cơ chế build, transfer và run của container, cùng ma trận thiết bị và image version, nằm ở [Container-based ACAP applications](acap-container-applications.md) và [Container application compatibility](acap-container-compatibility.md).

Điều này đặc biệt quan trọng với team quen Python, OpenCV, PyTorch và Docker runtime. Với sản phẩm lâu dài trên nhiều camera Axis, thiết kế phụ thuộc container runtime trên camera là hướng có rủi ro.

Với định hướng AXIS OS 13, Axis đã công bố thay đổi về application signing, manifest schema và khai báo quyền truy cập DLPU. Ví dụ resource declaration:[^axis-ai-chatgpt-research]

```json
{
  "deepLearningProcessor": {
    "enabled": true,
    "required": true
  }
}
```

Đây là phần cần tính đến khi chuẩn bị tương thích AXIS OS 13; không nên sao chép độc lập mà bỏ qua schema manifest tương ứng. Danh sách đầy đủ các thay đổi breaking của AXIS OS 13 và 14, kèm quy trình migrate, được tổng hợp ở [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md).

## Tài liệu và kênh hỗ trợ

Tài liệu ACAP 12 chia theo mục đích sử dụng, hữu ích khi cần biết tra ở đâu trước khi đọc sâu:[^acap-docs-index-v12]

| Khu vực | Nội dung |
| --- | --- |
| Get started | Pre-requisites, application đầu tiên, example application |
| How-to guides | [Build/install/control](acap-build-install-control.md), third-party libraries, VAPIX access cho ACAP application, [application user](acap-application-user-permissions.md), upgrade manifest, [signing](acap-application-signing.md) |
| Reference | Supported APIs, manifest schema, thiết bị và tương thích, cấu trúc application project |
| FAQ | Câu hỏi thường gặp, tương thích, ảnh hưởng dung lượng lưu trữ |

Kênh tương tác chính thức với team Axis là GitHub: `AxisCommunications/acap-native-sdk`, `acap-native-sdk-examples`, `acap-computer-vision-sdk-examples` cho issue và discussion, cùng general ACAP discussions của organization; ngoài ra có chương trình Axis For Developers.[^acap-docs-index-v12] Mã nguồn `acap-computer-vision-sdk-examples` (bộ ví dụ container, đã archived) đã được tổng hợp tại [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md); mã nguồn các repository còn lại vẫn chưa được ingest; trang giới thiệu bộ ví dụ đã được tổng hợp tại [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md).[^acap-app-examples]

## Relationships

- **Packaged by** [repository `acap-native-sdk`](acap-native-sdk-repository.md): chỉ chứa Dockerfile, không chứa mã SDK; cách ghép image ở [SDK image assembly](acap-native-sdk-image-assembly.md), danh sách thư viện bị ẩn khỏi sysroot ở [sysroot pruning](acap-native-sdk-sysroot-pruning.md) và CI ở [CI and maintenance](acap-native-sdk-repo-ci-and-maintenance.md).
- **Runs on** AXIS OS trên thiết bị Axis: camera, intercom, loa và radar.
- **Provides** VDO, Larod, Axoverlay, Axevent và VAPIX cho application.
- **Uses** [Axis DLPU](axis-dlpu.md) cho inference tăng tốc.
- **Supersedes** [hướng ACAP Computer Vision SDK/container](acap-container-applications.md): container path đã deprecated từ ACAP 12, không có container support trên sản phẩm mới chạy AXIS OS 12.x và chỉ còn hỗ trợ đến hết năm 2031.
- **Constrained by** [phiên bản ACAP](acap-versioning.md) tương ứng AXIS OS LTS của thiết bị đích.
- **Detailed by** [Native SDK API catalog](acap-native-sdk-api-catalog.md) (API, phiên bản SDK đưa vào, chip hỗ trợ), [ACAP generations, chip architectures and SDK compatibility](acap-chip-architecture-and-sdk-compatibility.md) và [ACAP release history](acap-release-history.md).
- **Succeeded** [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md): Native SDK thay SDK 3.x và nhiều API cũ.
- **Hosts** AXIS Object Analytics và custom application.
- **Used by** [quy trình triển khai custom model](axis-custom-model-deployment.md).
- **Practiced via** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): dùng base image Docker, `acap-build`, manifest và AXParameter của SDK.
- **Operationalized by** [Build, install, and control ACAP applications](acap-build-install-control.md): chọn build Dockerfile hay tương tác, đóng gói bằng `acap-build`, cài và điều khiển qua GUI, `eap-install.sh` hoặc VAPIX.
- **Extended by** [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md): build tool, cross-compile và bundle thư viện ngoài SDK trong `Dockerfile`.
- **Constrained by** [breaking changes của AXIS OS 13/14](acap-axis-os-13-14-migration.md): application signing bắt buộc, khai báo DLPU trong manifest, `.larod` và Larod API v1/v2 bị bỏ.
- **Documented by** [bộ ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): mỗi API có ít nhất một ví dụ và có mẫu tổng hợp nhiều API.
- **How-to for** computer vision on device: chuẩn bị model theo tài liệu Computer Vision, rồi tích hợp bằng VDO và Larod.
- **Set up via** [Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers](acap-dev-environment-setup.md): SDK image, Dev Container và validate manifest.
- **Requires** [thiết bị Axis đã được chuẩn bị](axis-device-setup.md) và [SSH/Developer Mode](axis-device-ssh-developer-mode.md) khi cần debug trên thiết bị.
- **Marketed publicly as** [hệ sinh thái ACAP](acap-ecosystem-public-case-studies.md): định vị "create and install scalable, customizable applications" trên camera, loa và access control, kèm case study đối tác Buddywise và SAFR; trang marketing không dùng để xác nhận khả năng kỹ thuật.
- **Examples** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md): catalog, conventions, CI and per-API example pages compiled from the local repository.

## Độ tin cậy

Phần nền tảng, toolchain, cấu trúc tài liệu và kênh hỗ trợ là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12) đã đọc ngày 2026-10-27, nên đáng tin hơn các claim cùng chủ đề lấy từ nguồn thứ cấp. Các mốc lifecycle của hướng container (deprecated, hỗ trợ đến 2031) nay là **Reported** từ tài liệu vendor chính thức của Axis, không còn chỉ dựa vào nguồn thứ cấp; riêng các thay đổi manifest ở AXIS OS 13 vẫn là **Reported** từ nguồn thứ cấp trong trang này và được biên soạn đầy đủ ở [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md).

[^axis-ai-chatgpt-research]: Nguồn thứ cấp: [Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis](../raw/axis-ai-chatgpt-research.md), §4.2 "Đóng gói application", §5 "SDK của Axis mở đến đâu?" và §8 "Một thay đổi rất đáng chú ý ở ACAP SDK".

[^acap-docs-index-v12]: Tài liệu chính thức: [ACAP version 12 — Axis developer documentation](../raw/acap/index/index.md), §Introduction, §Where to start, §Key features, §Docker-based SDK, §ACAP versioning và §Get help and give feedback.

[^acap-app-examples]: Tài liệu chính thức: [ACAP application examples — Axis developer documentation](../raw/acap/get-started/acap-application-examples/index.md), toàn bộ phần nội dung chính; repository và từng README là external link chưa được kiểm chứng.

[^acap-container-build-run]: Tài liệu chính thức: [Build, install, run — Axis developer documentation](../raw/acap/reference/develop-container-applications/build-install-run/index.md), warning banner "Note on container applications" (container support lifecycle, ACAP Native SDK recommendation, ACAP Computer Vision SDK archive và ACAP Runtime) và §The Docker Compose ACAP. Phần build/transfer/run của container được biên soạn ở [Container-based ACAP applications](acap-container-applications.md).

[^acap-cv-on-device]: Tài liệu chính thức: [Run computer vision models inside ACAP applications — Axis developer documentation](../raw/acap/how-to-guides/computer-vision-on-device/index.md), toàn bộ phần nội dung (137 từ); các liên kết tới tài liệu Computer Vision, API reference và repository ví dụ là external link chưa được kiểm chứng.
