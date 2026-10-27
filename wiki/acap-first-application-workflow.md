---
type: Concept
title: "Tạo, build và cài ACAP application đầu tiên"
description: "Luồng thực hành end-to-end cho ACAP application: cấu trúc project tối thiểu, manifest bắt buộc, build .eap bằng Docker SDK, cài unsigned app, đọc app log và dùng AXParameter API."
tags: [edge-ai, axis, acap, build]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:15:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-first-app
    resource: ../raw/acap/get-started/create-your-first-acap-application/index.md
    scope: ../raw/acap/get-started/create-your-first-acap-application/
    kind: docs
    revision: "ACAP version 12"
    title: "Create your first ACAP application | Axis developer documentation"
---

# Tạo, build và cài ACAP application đầu tiên

Hướng dẫn chính thức của Axis dựng một ứng dụng C "Hello World" từ project rỗng, build thành file `.eap` bằng ACAP Native SDK trong Docker, cài lên thiết bị dưới dạng unsigned app, rồi mở rộng ứng dụng bằng AXParameter API để đọc tham số cấu hình. Giá trị sử dụng lại nằm ở bốn mảnh: cấu trúc project tối thiểu, manifest tối thiểu, chuỗi lệnh build/lấy artifact, và cách bật một API có sẵn trong AXIS OS mà không phải tự mang thư viện vào.[^acap-first-app]

## Cấu trúc project tối thiểu

Project gồm thư mục `app/` (root của application, chứa toàn bộ file cần để build) và một `Dockerfile` ở cấp project:[^acap-first-app]

```text
hello-world
├── app
│   ├── hello_world.c
│   ├── LICENSE
│   ├── Makefile
│   └── manifest.json
└── Dockerfile
```

Bốn file trong `app/` là bắt buộc. Mã nguồn viết bằng `C`, `C++` hoặc `shell`; hướng dẫn dùng `C`. `LICENSE` phải liệt kê mọi source code open-source phân phối kèm application, và **build sẽ fail nếu file này rỗng** — hướng dẫn chỉ ghi `No licenses`.[^acap-first-app]

## Manifest tối thiểu

`manifest.json` định nghĩa application và cấu hình của nó, được dùng khi cài lên thiết bị Axis. Bản tối thiểu chỉ chứa các trường bắt buộc, và các trường này được validate trong quá trình build và signing:[^acap-first-app]

```json
{
  "schemaVersion": "1.7.4",
  "acapPackageConf": {
    "setup": {
      "appName": "hello_world",
      "vendor": "Example",
      "version": "1.0.0",
      "runMode": "never",
      "embeddedSdkVersion": "3.0"
    }
  }
}
```

| Trường | Vai trò theo hướng dẫn |
| --- | --- |
| `schemaVersion` | Phiên bản manifest schema dùng để validate |
| `acapPackageConf.setup.appName` | Định danh application; giữ nguyên khi cài lại thì lần cài sau là upgrade |
| `acapPackageConf.setup.vendor`, `version` | Thông tin package; `version` cũng xuất hiện trong tên file `.eap` |
| `acapPackageConf.setup.runMode` | Giá trị mẫu là `never`; trang không giải thích ngữ nghĩa |
| `acapPackageConf.setup.embeddedSdkVersion` | Giá trị mẫu là `3.0`; trang không giải thích ngữ nghĩa |

Bản tối thiểu không chứa thông tin user, nên ứng dụng chạy bằng dynamic user mặc định. Cách khai báo static user, cấp group và D-bus method, cùng việc migrate quyền sở hữu dữ liệu khi đổi user nằm ở [loại application user và quyền của ACAP application](acap-application-user-permissions.md).

## Build thành file .eap

ACAP Native SDK là một Docker container chứa toàn bộ công cụ build. Dockerfile dùng SDK làm base image, copy `app/` vào container rồi chạy `acap-build`:[^acap-first-app]

```dockerfile
ARG ARCH=armv7hf
ARG VERSION=12.5.0
ARG UBUNTU_VERSION=24.04
ARG REPO=axisecp
ARG SDK=acap-native-sdk

FROM ${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}

# Building the ACAP application
COPY ./app /opt/app/
WORKDIR /opt/app
RUN . /opt/axis/acapsdk/environment-setup* && acap-build ./
```

`ARCH` phải khớp kiến trúc thiết bị đích: `armv7hf` cho ARTPEC-7, `aarch64` cho ARTPEC-8 trở lên. `VERSION` phụ thuộc AXIS OS của thiết bị đích; quy tắc chọn nằm ở [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md). Việc source `/opt/axis/acapsdk/environment-setup*` là bước bắt buộc để export biến môi trường trước khi gọi `acap-build`.[^acap-first-app]

Hai lệnh tạo image và lấy artifact ra thư mục `build`:[^acap-first-app]

```bash
docker build --tag <APP_IMAGE> --build-arg ARCH=<ARCH> .
docker cp $(docker create <APP_IMAGE>):/opt/app ./build
```

Kết quả là một file `.eap` theo kiến trúc đã chọn, ví dụ `hello_world_1_0_0_aarch64.eap` hoặc `hello_world_1_0_0_armv7hf.eap`. Hướng dẫn chọn Dockerfile vì đó là cách repository ví dụ đang dùng, nhưng ghi nhận build tương tác bên trong container SDK cho vòng lặp code → build → test nhanh hơn. Trước khi `docker cp` lần build mới, phải xóa thư mục `build` cũ. Target `clean` trong Makefile xóa `*.o`, `*.eap*`, `package.conf*`, `param.conf` và `tmp*`.[^acap-first-app]

## Cài, chạy và kiểm chứng

Ứng dụng chưa ký (unsigned) nên phải bật tùy chọn cho phép:[^acap-first-app]

1. Mở `http://<AXIS_DEVICE_IP>/index.html#apps` (tab **Apps** trong device GUI).
2. Bật **Allow unsigned app**.
3. Bấm **(+ Add app)**, chọn file `.eap` vừa build, bấm **Install**.
4. Bật switch **Start** để chạy application.

Kiểm chứng bằng app log, theo một trong hai đường: `http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=hello_world`, hoặc trang **Apps** → **App log**. Chi tiết về priority level, `LOG_DEBUG`, `openlog()` và `journalctl` nằm ở [Application logging trong ACAP](acap-application-logging.md). Log đúng có dạng:[^acap-first-app]

```text
----- Contents of SYSTEM_LOG for 'hello_world' -----

[ INFO ] hello_world[6425]: Hello World!
```

Việc ký application và lợi ích của nó được trình bày ở [ACAP application signing: service portal and signing service](acap-application-signing.md); lần ingest này không chạy thử quy trình signing.

## Dùng một API có sẵn trong AXIS OS

Có thể dùng nhiều API của AXIS OS mà không phải include thủ công khi build. Điều kiện là API đó phải nằm trong ACAP Native SDK; SDK có các API Axis như VDO (video capture), AXEvent (gửi/subscribe event), Larod (machine learning trên DLPU), cùng một số API open-source như `curl` và OpenCL.[^acap-first-app]

Ví dụ mở rộng dùng AXParameter. Makefile phải link thêm `axparameter` cùng `glib-2.0` và `gio-2.0` (hai thư viện `axparameter` cần để chạy), qua `pkg-config`:[^acap-first-app]

```makefile
PKGS = glib-2.0 gio-2.0 axparameter

CFLAGS += $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --cflags $(PKGS))
LDLIBS += $(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) pkg-config --libs $(PKGS))
```

Cách link này chỉ dùng được cho thư viện **đã có trong SDK** (hoặc có trong base image Ubuntu). Thư viện ngoài SDK phải được cross-compile trong `Dockerfile` và mang theo trong application; quy trình đó nằm ở [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md).[^acap-first-app]

Khai báo tham số mặc định trong `manifest.json` bằng `configuration.paramConfig`; ví dụ một tham số `string` tên *Message* với default `"Hello World!"`:[^acap-first-app]

```json
"configuration": {
  "paramConfig": [
    {
      "name": "Message",
      "default": "Hello World!",
      "type": "string"
    }
  ]
}
```

Phía C, dùng handle của chính application để đọc tham số:[^acap-first-app]

```c
AXParameter* handle = ax_parameter_new(APP_NAME, NULL);
gchar* message;
ax_parameter_get(handle, "Message", &message, NULL);
syslog(LOG_INFO, "%s", message);
free(message);
ax_parameter_free(handle);
```

Truyền `APP_NAME` cho `ax_parameter_new` cho phép truy cập tham số của application mà không cần qualifier, đồng thời cho phép thêm/xóa tham số. Giá trị đang in ra vẫn là `"Hello World!"` vì đó là default trong manifest; đổi giá trị bằng **Apps** → application options → **Settings**, chạy lại application thì giá trị mới được log.[^acap-first-app]

Hai lưu ý khi đổi định danh: (1) nếu không đổi `appName` thì lần cài sau là upgrade của application cũ; (2) nếu đổi `appName` thì phải đổi cả tên file `.c`, biến `#define APP_NAME` trong file đó và tham chiếu tới file `.c` trong `Makefile`. Mỗi API trong SDK có reference documentation riêng, liên kết từ trang Native SDK API.[^acap-first-app]

## Độ phủ nguồn

- Entry point: `raw/acap/get-started/create-your-first-acap-application/index.md`, 1929 từ, thuộc bộ tài liệu ACAP 12, site `developer.axis.com`; trang không có mục con, hình ảnh hay tệp đính kèm.
- Đã đọc toàn bộ trang. Các khối code (manifest, Dockerfile, Makefile, C, lệnh shell) được trích lại nguyên văn từ nguồn.
- Nguồn dẫn tới nhưng **không có trong** `raw/`: Application project structure, manifest schemas, supported languages, Native SDK API, AXParameter API reference, và hai repository `hello-world` / `axparameter`. Vì vậy wiki không mô tả chi tiết các phần đó và không khẳng định chúng khớp với hướng dẫn. Trang Build/install/control đã được ingest riêng tại [Build, install, and control ACAP applications](acap-build-install-control.md); trang signing đã được ingest riêng tại [ACAP application signing](acap-application-signing.md).
- Yêu cầu môi trường phát triển và thiết lập thiết bị nằm trong package `raw/acap/get-started/set-up-developer-environment/`, đã được tổng hợp ở [môi trường phát triển](acap-dev-environment-setup.md) và [chuẩn bị thiết bị](axis-device-setup.md); lần ingest này không kiểm chứng lại các bước đó.
- Ngữ nghĩa của `runMode` và `embeddedSdkVersion` không được trang giải thích; wiki giữ nguyên giá trị mẫu thay vì suy diễn.

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12), đọc ngày 2026-10-27. Không có claim nào **Reproduced**: không chạy `docker build`, không cài lên thiết bị, không đọc app log thật trong lần ingest này. Các lệnh và tên file là bản trích từ nguồn, chưa được thực thi; cần đối chiếu với phiên bản SDK và AXIS OS thực tế trước khi dùng làm quy trình chuẩn.

## Relationships

- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): base image Docker, `acap-build`, environment setup và các API có sẵn.
- **Constrained by** [phiên bản ACAP](acap-versioning.md): `ARCH` theo SoC và `VERSION` của SDK theo AXIS OS LTS của thiết bị đích.
- **Uses** AXParameter API; VDO, AXEvent và Larod có trong SDK nhưng không được dùng trong ví dụ này.
- **Uses** [Application logging trong ACAP](acap-application-logging.md) để ghi log bằng `syslog()` và xem lại qua App log hoặc `journalctl`.
- **Practices** [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): project dựa trên `hello-world` và `axparameter`.
- **Elaborated by** [Build, install, and control ACAP applications](acap-build-install-control.md): mở rộng cùng luồng build Docker thành hai chế độ Dockerfile/tương tác và ba kênh cài đặt, điều khiển.
- **Upgraded from** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md): a legacy `package.conf` project converts into the same `manifest.json` format and project layout used here.
- **Upgraded by** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): the schema 1.7.4 manifest used here needs the v2 field and resource changes before it can target AXIS OS 13.
- **Contrasts with** [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md): ở đây link thư viện có sẵn trong SDK bằng `pkg-config`; thư viện ngoài SDK phải cross-compile và bundle trong `.eap`.
- **Precedes** [triển khai custom AI model](axis-custom-model-deployment.md): cùng cấu trúc `Dockerfile` + `app/`, sau đó thêm model và logic inference.
- **Requires** [môi trường phát triển ACAP](acap-dev-environment-setup.md) và [thiết bị Axis đã chuẩn bị](axis-device-setup.md) trước khi build và cài.
- **Needs** signing hoặc bật "Allow unsigned app" để cài được lên thiết bị.

[^acap-first-app]: Tài liệu chính thức: [Create your first ACAP application — Axis developer documentation](../raw/acap/get-started/create-your-first-acap-application/index.md), toàn bộ trang: §Set up the ACAP application project, §Write the application (Manifest file, Main program, Makefile, LICENSE file), §Build the application, §Install and start the application, §Test the application, §Use your first API. Các liên kết ra ngoài (project structure, manifest schemas, supported APIs, signing, repository ví dụ) chưa được kiểm chứng.
