---
type: Concept
title: "SSH và Developer Mode trên thiết bị Axis"
description: "Bật SSH bằng tài khoản non-root, cấp SSH cho application user bằng Developer Mode (CFC trên AXIS OS 11.11+, Developer Mode ACAP từ AXIS OS 13), và cách xác minh hoặc tắt."
tags: [edge-ai, axis, acap, ssh, developer-mode, security]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:14:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-device-ssh
    resource: ../raw/acap/get-started/set-up-developer-environment/set-up-device-advanced/index.md
    scope: ../raw/acap/get-started/set-up-developer-environment/
    kind: docs
    revision: "ACAP version 12"
    title: "Set up device - advanced | Axis developer documentation"
---

# SSH và Developer Mode trên thiết bị Axis

SSH trên thiết bị Axis mặc định bị tắt và phải được bật có chủ đích. Từ AXIS OS 12, SSH yêu cầu tài khoản **non-root** với quyền hạn giới hạn; còn để chính application (dynamic user) SSH được vào thiết bị thì cần **Developer Mode** — trên AXIS OS 11.11+ bằng Custom Firmware Certificate (CFC) theo từng thiết bị, và từ AXIS OS 13 bằng một Developer Mode ACAP application thay cho CFC.[^acap-device-ssh]

## Bật SSH và tạo tài khoản non-root

SSH có thể bật qua web interface hoặc SSH VAPIX API. Từ AXIS OS 12, tài khoản SSH phải là non-root; user này không làm được thao tác quản trị, phù hợp để duyệt file system, theo dõi tài nguyên và các việc phi quản trị khác.[^acap-device-ssh]

Các bước qua web interface:[^acap-device-ssh]

1. Mở `https://<AXIS_DEVICE_IP>/index.html#system/accounts`.
2. Tìm mục **SSH accounts**.
3. Bật switch **Enable SSH**.
4. Bấm **+ Add SSH account** và điền các trường trong dialog để tạo user SSH.

## Kết nối SSH

Dùng SSH client có sẵn trên Windows, macOS và hầu hết bản Linux:[^acap-device-ssh]

```sh
ssh <ssh-user>@<AXIS_DEVICE_IP>
```

Sau khi nhập đúng mật khẩu, shell prompt có dạng `<ssh-user>@axis-<serial_number>:~#`, trong đó `<serial_number>` là serial number hoặc MAC address của thiết bị. Đây là dấu hiệu kết nối thành công.

## Developer Mode

Developer Mode ra đời từ AXIS OS 11.11, cấp SSH cho dynamic user của ACAP application: khi bật, user động của application được thêm vào group `ssh`. Trên AXIS OS 11.11 trở lên, bật bằng cách cài Custom Firmware Certificate `axis-unlock-acap-devmode` lên thiết bị.[^acap-device-ssh]

### Xin Custom Firmware Certificate (CFC)

CFC là chứng chỉ riêng cho **từng thiết bị**, do Axis partner xin qua CFC Portal. Cần đăng nhập MyAxis trong bước xác minh, và cần các thông tin sau:[^acap-device-ssh]

| Thông tin | Cách lấy |
| --- | --- |
| `SerialNumber` | basicdeviceinfo API hoặc trang plain config của thiết bị |
| `Soc` | basicdeviceinfo API, ví dụ `artpec-7`, `artpec-8`, `ambarella-cv25` |
| `SocSerialNumber` (Processor Serial Number) | basicdeviceinfo API |
| Owner Authentication Key (OAK) | OAK API, hoặc trang network config → **Owner authentication key (OAK)** → **Get key** |

Nếu request thành công, nhận file `.fcr` — chính là certificate cần cài lên thiết bị. Cách đọc các trường này qua VAPIX có ở [chuẩn bị thiết bị Axis](axis-device-setup.md).

### Cài CFC và xác minh

1. Mở `http://<AXIS_DEVICE_IP>/index.html#system/security`.
2. Xuống mục **Custom Signed AXIS OS Certificate**.
3. Nếu `axis-unlock-acap-devmode` chưa có, cài qua nút **Install**.

Khi Developer Mode đã bật, mỗi lần cài ACAP application dùng [dynamic user](acap-application-user-permissions.md) thì một SSH account được tạo tự động. Để application user SSH được:[^acap-device-ssh]

1. Mở `https://<AXIS_DEVICE_IP>/index.html#system/accounts`.
2. Trong **SSH accounts**, bảo đảm **Enable SSH** đang bật.
3. Tìm user dạng `acap-<appName>`.
4. Đặt mật khẩu cho user đó qua menu ba chấm → **Update SSH account**; bước này bắt buộc để SSH được.

### Tắt Developer Mode

1. Mở `http://<AXIS_DEVICE_IP>/index.html#system/security` → **Custom Signed AXIS OS Certificate**.
2. Trong **Installed certificates**, chọn ba chấm cạnh `axis-unlock-acap-devmode` → **Delete certificate**.
3. Factory default thiết bị sau khi xóa certificate: mở `http://<AXIS_DEVICE_IP>/index.html#maintenance`, trong **Factory default** bấm **Default** rồi **Restore all**.

Kiểm tra lại bằng cách cài một ACAP application và xác nhận không có ACAP SSH user mới được thêm.[^acap-device-ssh]

## Thay đổi ở AXIS OS 13

Từ AXIS OS 13, CFC không còn và được thay bằng **Developer Mode ACAP application**. Tài liệu (trang alpha của ACAP 13) nêu các điểm chuyển tiếp quan trọng:[^acap-device-ssh]

- Developer Mode ACAP application có thể cài trên thiết bị AXIS OS 12.11 để chuẩn bị nâng cấp lên AXIS OS 13, nhưng **không có tác dụng trên 12.11**.
- Trên AXIS OS 12.11, unsigned ACAP application vẫn cần bật **Allow unsigned apps**, và SSH vẫn cần CFC.
- Team có kế hoạch nâng thiết bị từ 12.11 lên 13.x với unsigned application nên đọc trang hướng dẫn migrate của Axis trước khi nâng cấp.

Đây là vùng thay đổi theo phiên bản AXIS OS, nên cần đối chiếu lại tài liệu trước khi dựng quy trình chuẩn; xem [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md).

## Độ phủ nguồn

- Entry point: `raw/acap/get-started/set-up-developer-environment/set-up-device-advanced/index.md` (1057 từ), bộ ACAP 12; đã đọc toàn bộ trang.
- Trang không có asset hình ảnh; các bước đều ở dạng văn bản và lệnh shell.
- Nguồn dẫn ra ngoài `raw/`: SSH VAPIX API, OAK API, basicdeviceinfo API, trang application user (dynamic user), CFC Portal, và ba mục của bộ tài liệu ACAP 13 alpha (Developer Mode, migration từ 12.11 lên 13.x, nâng cấp với unsigned application). Các phần đó chưa được kiểm chứng trực tiếp.
- Trang nguồn có một callout thông tin bị lỗi định dạng (`> [!-info] -info` với nội dung lặp "info") ở hai chỗ; wiki bỏ phần nhiễu này và chỉ giữ nội dung có nghĩa.
- Quy trình CFC chỉ dành cho Axis partner và cần MyAxis; không có thông tin về giá, thời gian xử lý hay giới hạn số lượng CFC.

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12, riêng phần AXIS OS 13 là tài liệu alpha được dẫn lại). Không có claim nào **Reproduced**: không bật SSH, không tạo user, không xin/cài CFC, không factory default thiết bị thật. Thông tin về AXIS OS 13 có thể thay đổi trước bản phát hành chính thức.

## Relationships

- **Depends on** [chuẩn bị thiết bị Axis](axis-device-setup.md): cần serial number, SoC, SoC serial number và quyền quản trị để xin CFC.
- **Constrained by** [phiên bản ACAP và AXIS OS](acap-versioning.md): cơ chế Developer Mode khác nhau giữa AXIS OS 11.11, 12.11 và 13.x.
- **Enables** debug trên thiết bị cho [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): xem app log, duyệt file system, chạy lệnh trong AXIS OS.
- **Used by** [triển khai custom AI model](axis-custom-model-deployment.md): `larod-client` được chạy qua SSH trên camera.
- **Depends on** [loại application user và quyền của ACAP application](acap-application-user-permissions.md): Developer Mode chỉ có tác dụng với application dùng dynamic user, vì tài khoản SSH được tạo chính là `acap-<appName>`.
- **Requires** quyền Axis partner cho CFC; không phải quy trình self-service.
- **Replaced by** Developer Mode ACAP application từ AXIS OS 13 (theo tài liệu alpha), trong khi CFC vẫn là cơ chế của AXIS OS 11.11–12.11.

[^acap-device-ssh]: Tài liệu chính thức: [Set up device - advanced — Axis developer documentation](../raw/acap/get-started/set-up-developer-environment/set-up-device-advanced/index.md), toàn bộ trang: §Access the device through SSH (§Enable SSH and create a non-root user, §Connect to the device), §Developer Mode (§Get the Custom Firmware Certificate (CFC), §Install the CFC on your device, §Verify Developer Mode is enabled, §Disable Developer Mode), và callout về AXIS OS 13 (CFC thay bằng Developer Mode ACAP application, migration 12.11 → 13.x).
