---
type: Concept
title: "Tích hợp third-party library vào ACAP application"
description: "Build và bundle thư viện bên thứ ba trong ACAP Native SDK: cài build tool trong Dockerfile, cross-compile dưới /opt/build, copy vào /opt/app/lib, link bằng LDLIBS/LDFLAGS và đặt RPATH theo $ORIGIN."
tags: [edge-ai, axis, acap, build, docker, dependencies]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-third-party-libs
    resource: ../raw/acap/how-to-guides/include-third-party-libraries/index.md
    scope: ../raw/acap/how-to-guides/include-third-party-libraries/
    kind: docs
    revision: "ACAP version 12"
    title: "Include third party libraries | Axis developer documentation"
---

# Tích hợp third-party library vào ACAP application

Với ACAP Native SDK, thư viện bên thứ ba **không được cài trên camera và không được cài trên máy host**: toàn bộ việc build thư viện diễn ra trong `Dockerfile` của project, cross-compile bằng toolchain của SDK, rồi bản đã biên dịch được copy vào `/opt/app/lib` để `acap-build` đóng gói kèm application. Chuỗi bốn bước là: cài build tool bằng `apt-get`, clone source vào một work directory cố định, source `environment-setup*` rồi `configure`/`make`, và cuối cùng link trong `Makefile` với `LDFLAGS` chứa `-rpath,'$$ORIGIN/lib'`. Điểm dễ sai nhất là RPATH: thiếu nó thì library có mặt trong `.eap` nhưng không được tìm thấy lúc chạy.[^acap-third-party-libs]

## Dockerfile lo cả build tool và build thư viện

Hướng dẫn mô tả cách làm generic: phần build thư viện bên thứ ba do `Dockerfile` đảm nhiệm, nên khi build một thư viện cụ thể phải cập nhật và cài mọi build tool cần thiết cho thư viện đó.[^acap-third-party-libs]

```dockerfile
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
         <ubuntu-package>
```

Source code phải được clone vào một work directory xác định trong container, không phải thư mục tùy ý:[^acap-third-party-libs]

```dockerfile
WORKDIR /opt/build
RUN git clone <Third-party source code github path>
WORKDIR /opt/build/<cloned directory>
```

Nguồn dẫn tới các ví dụ trong [`utility-libraries`](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/utility-libraries) của repository `acap-native-sdk-examples` để xem build tool phụ trợ được cài thế nào và cách compile thư viện bên thứ ba cho **armv7hf** bằng `Dockerfile`. Repository đó chưa có trong `raw/`.[^acap-third-party-libs]

## Cross-compile thư viện

Trước khi build phải làm bốn việc, theo đúng thứ tự mà hướng dẫn liệt kê: source file setup môi trường cross-compilation, cấu hình thư mục output của library bằng `--prefix`, thêm cross compiler flag nếu có, rồi chạy `make`. Ví dụ với cURL:[^acap-third-party-libs]

```dockerfile
#  lib generate
# - Source the SDK environment script to get links to cross compiler through
# - CONFIGURE_FLAGS environment variable
WORKDIR /opt/build/curl
RUN . /opt/axis/acapsdk/environment-setup* && \
    autoreconf -fi && \
    ./configure --prefix=${PWD}/build ${CONFIGURE_FLAGS} --without-ssl && \
    make && \
    make install
```

Hai chi tiết đáng chú ý trong ví dụ này:[^acap-third-party-libs]

- `environment-setup*` không chỉ export toolchain mà còn đặt `CONFIGURE_FLAGS`, biến được truyền thẳng vào `./configure` để lấy đúng cross compiler và flag của SDK.
- `--prefix=${PWD}/build` giữ toàn bộ kết quả build trong thư mục của project, để bước sau copy ra ngoài thay vì cài vào hệ thống container.

`--without-ssl` là lựa chọn riêng của ví dụ cURL, không phải yêu cầu chung.[^acap-third-party-libs]

## Đóng gói library vào /opt/app/lib

Sau khi build thành công, thư mục library sinh ra được copy vào `/opt/app/lib`. Theo hướng dẫn, `/opt/app/lib` chứa các shared library đã cross-compile và chúng sẽ được đóng gói vào ACAP application.[^acap-third-party-libs]

```dockerfile
# Copy the library to application folder
ARG BUILDDIR=/opt/build/curl
COPY ./app /opt/app/
WORKDIR /opt/app
RUN mkdir lib && cp -r ${BUILDDIR}/build lib
```

Thứ tự quan trọng: `COPY ./app /opt/app/` chạy trước `mkdir lib`, và `BUILDDIR` được khai báo bằng `ARG` để đổi thư viện nguồn mà không sửa phần còn lại. Đường dẫn `/opt/app/lib` cũng chính là thư mục mà `acap-build` đưa vào `.eap` cùng với `html/` và các file khác — xem [Build, install, and control ACAP applications](acap-build-install-control.md).[^acap-third-party-libs]

## Link trong Makefile

Trong `Makefile` của application, khai báo header path và library path của thư viện vừa bundle, rồi link thư viện:[^acap-third-party-libs]

```bash
LDLIBS += -Llib/
CFLAGS += -Ilib/include
SHLIB_DIR = ./lib
LDFLAGS = -L$(SHLIB_DIR) -Wl,--no-as-needed,-rpath,'$$ORIGIN/lib'
SHLIBS += -lm -l[lib]
```

| Biến | Giá trị trong nguồn | Vai trò theo hướng dẫn |
| --- | --- | --- |
| `LDLIBS` | `-Llib/` | Đường dẫn tìm library khi link |
| `CFLAGS` | `-Ilib/include` | Đường dẫn header của thư viện |
| `SHLIB_DIR` | `./lib` | Thư mục chứa shared library, dùng lại trong `LDFLAGS` |
| `LDFLAGS` | `-L$(SHLIB_DIR) -Wl,--no-as-needed,-rpath,'$$ORIGIN/lib'` | Đường dẫn link và RPATH cho runtime |
| `SHLIBS` | `-lm -l[lib]` | Danh sách library cần link |

Dòng `SHLIBS` trong bản capture chứa placeholder `-l[lib]` theo sau bởi một marker link `linking-third-party-lib` trong ngoặc tròn: đó là lỗi capture của trang, không phải cú pháp thật. Tên library cụ thể phải thay vào chỗ `[lib]`.[^acap-third-party-libs]

Trang nguồn không giải thích `--no-as-needed`; theo ngữ nghĩa của linker, flag này giữ library lại ngay cả khi chưa thấy symbol nào được dùng trực tiếp tại thời điểm link — cần thiết khi application chỉ dùng thư viện một cách gián tiếp. Phần giải thích này là **Synthesis**.[^acap-third-party-libs]

## RPATH và $ORIGIN

RPATH thay đổi library search path để một executable hoặc library có thể link tới các dependent library mong muốn **tại runtime**. Hướng dẫn yêu cầu đặt RPATH trỏ tới thư mục chứa shared library bằng `$ORIGIN`, để linker tìm và include library dưới đường dẫn đã chỉ định; cách này thường dùng để override các library path mặc định.[^acap-third-party-libs]

Trong `Makefile` phải viết `$$ORIGIN` vì `make` tiêu thụ một dấu `$`, còn linker nhận literal `$ORIGIN` — biến này được loader thay bằng thư mục chứa chính binary lúc chạy, nên `$ORIGIN/lib` trỏ tới `lib/` nằm cạnh executable trong application đã cài. Đây là **Synthesis** từ cách nguồn escape `$$ORIGIN`, không phải giải thích mà trang nguồn đưa ra.[^acap-third-party-libs]

## Troubleshooting: thiếu file Configure

Hướng dẫn ghi nhận: thông thường file `Configure` có sẵn khi build một custom library cho một kiến trúc cụ thể. Nếu không có, phải tạo output build directory bằng `Makefile` rồi copy các file library sinh ra vào thư mục library output:[^acap-third-party-libs]

```bash
mkdir -p build
mkdir -p build/include
cp *.h build/include
cp [lib.so] build/
```

Kết quả cuối là cùng một layout `build/include` + `build/*.so` mà các bước copy và link phía trên mong đợi. `[lib.so]` cũng là placeholder trong bản capture, phải thay bằng tên file thật.[^acap-third-party-libs]

## Độ phủ nguồn

- **Entry point và scope:** `raw/acap/how-to-guides/include-third-party-libraries/index.md`, một trang 508 từ thuộc bộ tài liệu ACAP 12 trên `developer.axis.com`; scope `raw/acap/how-to-guides/include-third-party-libraries/`. Không có trang con, hình ảnh hay tệp đính kèm trong folder được capture.
- **Đã đọc:** toàn bộ trang, gồm phần tổng quan Docker, các khối `Dockerfile`, phần RPATH và phần troubleshooting.
- **Không kiểm chứng:** repository `utility-libraries` và `acap-native-sdk-examples`, trang "Building using a Dockerfile" (đã ingest riêng tại [Build, install, and control ACAP applications](acap-build-install-control.md)), tài liệu Docker, autotools và linker. Các phần đó là external link, không có trong `raw/`.
- **Không thực thi:** không chạy `docker build`, không cross-compile thư viện nào, không cài `.eap` lên thiết bị. Mọi lệnh là bản trích từ nguồn.
- **Lỗi capture:** placeholder `-l[lib]` kèm marker link `linking-third-party-lib` trong khối `Makefile`, placeholder `[lib.so]` trong phần troubleshooting, và callout `> [!-info] -info` bị lỗi định dạng ở phần RPATH. Wiki giữ nguyên nội dung có nghĩa và ghi rõ chỗ nào là lỗi capture.
- **Chồng lấn:** hai chế độ build Docker và cơ chế `acap-build` đóng gói thư mục `lib/` nằm ở [Build, install, and control ACAP applications](acap-build-install-control.md); cách link một thư viện **có sẵn trong SDK** (`axparameter`, `curl`, OpenCL) bằng `pkg-config` nằm ở [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md).

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12), đọc ngày 2026-10-27; không có claim nào **Reproduced** vì không có bước build hay chạy thử. Trang nguồn tự nhận là "generic guide" và đẩy phần lớn chi tiết cụ thể sang repository ví dụ bên ngoài, nên các bước ở đây là khung quy trình chứ chưa phải công thức đã kiểm chứng cho một thư viện cụ thể. Riêng giải thích về `$$ORIGIN` được đánh dấu **Synthesis**.

## Relationships

- **Constrained by** [SDK sysroot pruning](acap-native-sdk-sysroot-pruning.md): libraries such as Boost, GnuTLS, libjpeg, SQLite and libpaho are removed from the SDK sysroot, so applications must build and bundle them.
- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): base image, `environment-setup*`, `CONFIGURE_FLAGS` và `acap-build`.
- **Elaborates** [Build, install, and control ACAP applications](acap-build-install-control.md): mở rộng nhánh Dockerfile bằng bước cài build tool, cross-compile và bundle `lib/`.
- **Contrasts with** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): thư viện đã có trong SDK thì chỉ cần `pkg-config`; thư viện ngoài SDK phải cross-compile và mang theo trong `.eap`.
- **Requires** [Môi trường phát triển ACAP](acap-dev-environment-setup.md): Docker và SDK image, nơi `RUN apt-get` bổ sung tool.
- **Constrained by** [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): kiến trúc build (`armv7hf`, `aarch64`) và phiên bản SDK phải khớp thiết bị đích.
- **Uses** RPATH với `$ORIGIN` để application tìm thấy library đã bundle lúc runtime.
- **Precedes** cài đặt và kiểm chứng application trên thiết bị, theo cùng kênh GUI, `eap-install.sh` hoặc VAPIX.
- **Illustrated by** [ACAP examples: bundling libraries](acap-example-bundled-libraries-opencv-curl-openssl.md): `using-opencv`, `curl-openssl` and `utility-libraries` are now compiled from the local examples repository (revision `12.11.0-7-g3025a4e`), which supersedes this page's note that those examples were unverified.

[^acap-third-party-libs]: Tài liệu chính thức: [Include third party libraries — Axis developer documentation](../raw/acap/how-to-guides/include-third-party-libraries/index.md), toàn bộ trang: §ACAP Native SDK (Docker commands to install supporting build tools; clone và work directory; build thư viện với ví dụ cURL; copy library vào `/opt/app/lib`; Makefile link flags), §Importance of setting RPATH, §Troubleshooting. Các external link (`utility-libraries`, `acap-native-sdk-examples`, "Building using a Dockerfile") chưa được kiểm chứng trong `raw/`.
