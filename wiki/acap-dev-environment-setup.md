---
type: Concept
title: "Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers"
description: "Yêu cầu máy phát triển, cách ACAP Native SDK phân phối qua Docker image, cấu hình VS Code Dev Container và validate manifest theo schema."
tags: [edge-ai, axis, acap, tooling, docker]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T18:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-dev-env-prereq
    resource: ../raw/acap/get-started/set-up-developer-environment/pre-requisites/index.md
    scope: ../raw/acap/get-started/set-up-developer-environment/
    kind: docs
    revision: "ACAP version 12"
    title: "Pre-requisites | Axis developer documentation"
  - id: acap-dev-env-vscode
    resource: ../raw/acap/get-started/set-up-developer-environment/setting-up-visual-studio-code/index.md
    scope: ../raw/acap/get-started/set-up-developer-environment/
    kind: docs
    revision: "ACAP version 12"
    title: "Setting up Visual Studio Code | Axis developer documentation"
---

# Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers

Máy phát triển ACAP cần Linux, Windows hoặc macOS, Docker, Git và một editor — Axis khuyến nghị Visual Studio Code nhưng không bắt buộc. Điểm cốt lõi là ACAP Native SDK **không phải gói cài đặt truyền thống**: nó được phân phối dưới dạng Docker image, và `Dockerfile` của từng project chỉ định phiên bản SDK để Docker tự tải và cache. VS Code Dev Containers biến chính container đó thành môi trường phát triển đầy đủ, kèm IntelliSense và validate manifest theo schema.[^acap-dev-env-prereq][^acap-dev-env-vscode]

## Yêu cầu máy phát triển

| Thành phần | Yêu cầu theo tài liệu ACAP 12 |
| --- | --- |
| Hệ điều hành | Linux, Windows hoặc macOS |
| Docker | Windows/macOS: **Docker Desktop stable** (tự cập nhật được). Linux: **Docker Engine 23.0.0** trở lên |
| Git | Cài từ git-scm.com |
| Editor | Visual Studio Code được khuyến nghị; có thể dùng editor khác |

## SDK được giao qua Docker, không qua cài đặt thủ công

Luồng build của ACAP Native SDK khác SDK truyền thống ở ba điểm:[^acap-dev-env-prereq]

1. `Dockerfile` trong mỗi project (hoặc mỗi example) chỉ định SDK version cần dùng.
2. Lần build đầu tiên, Docker tự tải SDK image về.
3. Application được build **bên trong** container đó.

Vì vậy không cần tải SDK riêng; chỉ cần chạy lệnh `docker build` theo hướng dẫn của project. SDK image được cache cục bộ nên các lần build sau nhanh hơn. Tài liệu nhấn mạnh Docker ở đây không chỉ là build tool mà là **cơ chế phân phối SDK**.[^acap-dev-env-prereq]

Base image có dạng `${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}`, với mặc định trong ví dụ Dev Container là `axisecp/acap-native-sdk:12.0.0-aarch64-ubuntu24.04`. `ARCH` phải khớp kiến trúc thiết bị đích (`aarch64` hoặc `armv7hf`); quy tắc chọn phiên bản SDK theo AXIS OS nằm ở [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md). Image đã có SDK tools, Git và một số công cụ khác; thư viện hay tool bổ sung (ví dụ `cppcheck`, OpenCV) được thêm bằng `RUN` trong `Dockerfile`.[^acap-dev-env-vscode] Cùng cơ chế `RUN` đó là nơi cài build tool và cross-compile thư viện bên thứ ba — xem [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md).

## VS Code Dev Container cho ACAP Native SDK

Dev Containers dùng một Docker container làm môi trường phát triển đầy đủ: code, runtime, system tools, thư viện và settings đều nằm trong container. Cách này tránh cài tool trực tiếp lên máy và giữ môi trường nhất quán, tái lập được giữa các thành viên.[^acap-dev-env-vscode]

Các bước theo tài liệu:[^acap-dev-env-vscode]

1. Cài extension **Dev Containers** (`ms-vscode-remote.remote-containers`) trong VS Code.
2. Tạo thư mục `.devcontainer` ở thư mục gốc của source project.
3. Trong `.devcontainer`, tạo `devcontainer.json`:

```json
{
    "name": "ACAP Native (aarch64)",
    "build": {
        "dockerfile": "Dockerfile",
        "args": {
            "ARCH": "aarch64"
        }
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-vscode.cpptools-extension-pack",
                "ms-vscode.makefile-tools",
                "ms-azuretools.vscode-docker"
            ]
        }
    }
}
```

4. Trong `.devcontainer`, tạo `Dockerfile`:

```dockerfile
ARG ARCH
ARG VERSION=12.0.0
ARG UBUNTU_VERSION=24.04
ARG REPO=axisecp
ARG SDK=acap-native-sdk
FROM ${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}
RUN apt-get update && apt-get install cppcheck -y
```

5. Tạo thư mục `.vscode` ở thư mục gốc project.
6. Trong `.vscode`, tạo `c_cpp_properties.json` để IntelliSense thấy header của SDK:

```json
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": ["${workspaceFolder}/**", "${SDKTARGETSYSROOT}/**"]
        }
    ],
    "version": 4
}
```

7. Chạy **View** > **Command Palette...** → `Dev Containers: Reopen in Container`. VS Code build container nếu chưa có rồi mở source trong container; lần đầu có thể mất thời gian.

Sau khi container được build, IntelliSense và code browsing hoạt động với thư viện Axis. `ARCH` trong `devcontainer.json` phải đổi theo thiết bị đích; danh sách kiến trúc được Axis dẫn sang trang "Axis devices & compatibility" bên ngoài `raw/`.[^acap-dev-env-vscode]

## Validate manifest trong editor

Dev Container cho phép validate `manifest.json` theo thời gian thực, giảm lỗi schema trước khi build:[^acap-dev-env-vscode]

1. Trong `.vscode`, tạo `settings.json` trỏ JSON schema tới manifest tools trong SDK image:

```json
{
    "json.schemas": [
        {
            "fileMatch": ["**/manifest.json*"],
            "url": "/opt/axis/acapsdk/axis-acap-manifest-tools/schema/schemas/v1/*.json"
        }
    ]
}
```

2. Thêm trường `$schema` vào `manifest.json`, và giá trị phải khớp với `schemaVersion`:

```json
{
    "$schema": "file:///opt/axis/acapsdk/axis-acap-manifest-tools/schema/schemas/v1/application-manifest-schema-v1.6.0.json",
    "schemaVersion": "1.6.0"
}
```

3. VS Code hiển thị lỗi trong mục **PROBLEMS**. Hai ví dụ trong tài liệu: đặt dấu hyphen trong `appName`, và nhập `appId` dạng số không có dấu nháy. Manifest tối thiểu và các trường bắt buộc được trình bày ở [luồng tạo application đầu tiên](acap-first-application-workflow.md).

## Độ phủ nguồn

- Package `raw/acap/get-started/set-up-developer-environment/` có bốn trang; trang được dùng ở đây là `pre-requisites/index.md` (181 từ) và `setting-up-visual-studio-code/index.md` (710 từ). Hai trang `set-up-device/` và `set-up-device-advanced/` được tổng hợp ở [chuẩn bị thiết bị](axis-device-setup.md) và [SSH/Developer Mode](axis-device-ssh-developer-mode.md).
- Đã đọc toàn bộ hai trang. Hai ảnh chụp trong `setting-up-visual-studio-code/assets/` chỉ minh họa IntelliSense và lỗi validate đã được mô tả bằng lời, nên được loại trừ như asset trang trí.
- Các liên kết ngoài chưa có trong `raw/`: Docker download, Git, VS Code, Dev Containers extension, trang Axis devices & compatibility, repository `using-opencv`, tài liệu từng extension.
- `12.0.0` và `1.6.0` là giá trị ví dụ trong nguồn, không phải phiên bản bắt buộc; nguồn không nói quan hệ giữa hai giá trị này ngoài yêu cầu `$schema` khớp `schemaVersion`.

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12). Không có claim nào **Observed** hay **Reproduced** trong lần ingest này: không chạy `docker build`, không mở container, không validate manifest thật. Các file JSON/Dockerfile được trích nguyên văn để có thể tái sử dụng, nhưng cần đối chiếu phiên bản SDK và AXIS OS thực tế trước khi dùng làm chuẩn.

## Relationships

- **Built from** [Dockerfile của `acap-native-sdk`](acap-native-sdk-image-assembly.md): image gồm `acap-api` và `acap-toolchain` trên `ubuntu:24.04`, chạy root, và chỉ source `environment-setup*` trong shell tương tác (qua `/etc/bash.bashrc`).
- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): base image, SDK tools và `acap-build` nằm trong container.
- **Constrained by** [phiên bản ACAP](acap-versioning.md): `VERSION` của SDK image và `$schema`/`schemaVersion` phải khớp phiên bản ACAP của AXIS OS đích.
- **Precedes** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): cấu hình môi trường trước, sau đó build `.eap` và cài lên thiết bị.
- **Requires** [thiết bị Axis đã được chuẩn bị](axis-device-setup.md) để có IP, tài khoản quản trị và AXIS OS phù hợp.
- **Supports** [triển khai custom AI model](axis-custom-model-deployment.md): cùng base image và vòng lặp build container.
- **Enables** [Remote debugging ACAP applications with GDB and VS Code](acap-remote-debugging.md): Dev Container là môi trường build/chạy của ví dụ debug, với VS Code làm front end.
- **Enables** [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md): `RUN apt-get` trong `Dockerfile` cài build tool trước khi cross-compile thư viện ngoài SDK.
- **Configured by** [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md): khi máy build nằm sau proxy, cấu hình Docker daemon và môi trường build trước khi pull SDK image.

[^acap-dev-env-prereq]: Tài liệu chính thức: [Pre-requisites — Axis developer documentation](../raw/acap/get-started/set-up-developer-environment/pre-requisites/index.md), toàn bộ trang: danh sách yêu cầu, §Understanding the ACAP SDK (§How it works, §What this means for you).

[^acap-dev-env-vscode]: Tài liệu chính thức: [Setting up Visual Studio Code — Axis developer documentation](../raw/acap/get-started/set-up-developer-environment/setting-up-visual-studio-code/index.md), §Set up for ACAP Native SDK (bước 1–7, `devcontainer.json`, `Dockerfile`, `c_cpp_properties.json`) và §Manifest validation (bước 1–3, `settings.json`, `$schema`).
