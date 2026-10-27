---
type: Concept
title: "Chuẩn bị thiết bị Axis cho phát triển ACAP"
description: "Đưa camera Axis vào trạng thái phát triển: tìm thiết bị trên mạng, đặt mật khẩu root, kiểm tra hỗ trợ ACAP, đọc thông tin thiết bị qua VAPIX và nâng cấp AXIS OS."
tags: [edge-ai, axis, acap, device, vapix]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:12:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-device-setup
    resource: ../raw/acap/get-started/set-up-developer-environment/set-up-device/index.md
    scope: ../raw/acap/get-started/set-up-developer-environment/
    kind: docs
    revision: "ACAP version 12"
    title: "Set up device | Axis developer documentation"
---

# Chuẩn bị thiết bị Axis cho phát triển ACAP

Trước khi build và cài ACAP application, thiết bị Axis phải được tìm thấy trên mạng, truy cập được bằng tài khoản quản trị, xác nhận có hỗ trợ ACAP, và chạy AXIS OS phù hợp. Trang "Set up device" của Axis mô tả bốn việc đó cùng cách đọc thông tin thiết bị qua VAPIX — trong đó `Architecture` quyết định `ARCH` khi build và `Version` quyết định phiên bản ACAP/AXIS OS cần khớp.[^acap-device-setup]

## Tìm thiết bị trên mạng

Sau khi khởi động, thiết bị nhận địa chỉ theo DHCP, đặt tĩnh thủ công, hoặc tự gán địa chỉ link-local (`169.254.x.y`). Vì thường chưa biết địa chỉ, tài liệu đưa ra các cách discovery cho ngữ cảnh phát triển ACAP:[^acap-device-setup]

| Cách | Nền tảng | Ghi chú |
| --- | --- | --- |
| **Axis IP Utility** | Windows | Được đánh giá là cách dễ nhất; chạy trên Windows host khi Linux nằm trong WSL, hoặc qua Wine |
| **Axis Device Manager (ADM)** | Windows | Có discovery và quản lý fleet, cài được ACAP application; tiện vận hành hệ thống nhưng kém tiện cho discovery khi dev |
| **avahi-discover** | Linux | Dùng Bonjour; có GUI; đôi khi chỉ hiện địa chỉ link-local trước |
| **Hostname mDNS** | Linux/macOS | `axis-<serialnumber_in_lowercase>.local`, ví dụ serial `B8A44F3A9E07` → `axis-b8a44f3a9e07.local` |
| **nmap** | Linux | Quét dải mạng; cần `sudo` để thấy MAC và tên nhà sản xuất |

Ba công cụ đầu dựa trên Bonjour; `nmap` chỉ dùng chức năng mạng cơ bản nên cần biết dải địa chỉ. Quy trình nmap trong tài liệu: cài `nmap`, chạy `ip address` để lấy network/mask của interface, rồi `sudo nmap -sn 192.168.200.102/24`.[^acap-device-setup]

Với avahi-discover, thiết bị có thể hiện địa chỉ tự gán `169.254.*` trước. Nếu Linux chưa biết route tới link-local, thêm route:[^acap-device-setup]

```sh
sudo ip route add 169.254.0.0/16 via <local ip address>
```

Từ AXIS OS 12, thiết bị chỉ báo địa chỉ bình thường khi thực sự có, nên discovery bằng avahi-discover đơn giản hơn. Nếu mọi cách đều thất bại, đặc biệt với thiết bị không mới, cần factory default: địa chỉ IP tĩnh rất phổ biến trong video surveillance và có thể làm thiết bị không truy cập được dù vẫn xuất hiện khi discovery.[^acap-device-setup]

## Truy cập và bảo mật tài khoản

Mở trình duyệt tới IP hoặc hostname của thiết bị. Lần truy cập đầu tiên phải đặt mật khẩu root; sau đó trang live view mở ra. Tài liệu lưu ý **AXIS OS** và **device software** trước đây được gọi là **firmware**.[^acap-device-setup]

- Mặc định administrator username là `root`; mất mật khẩu root phải factory default.
- Axis không áp password policy vì thiết bị dùng trong nhiều loại hình lắp đặt; khuyến nghị tối thiểu 8 ký tự, tốt nhất do password generator tạo, không lộ mật khẩu, đổi định kỳ ít nhất mỗi năm.
- **Cảnh báo:** mật khẩu đặt lần đầu được gửi dạng clear text qua mạng. Sau lần đăng nhập đầu, phải bật HTTPS mã hóa rồi đổi mật khẩu.
- Để chắc chắn AXIS OS chưa bị can thiệp, factory default trước: secure boot bảo đảm trạng thái thiết bị sau reset, rồi mới cấu hình và cài đặt.

## Kiểm tra hỗ trợ ACAP

Dùng VAPIX CGI `param.cgi` để kiểm tra parameter `Properties.EmbeddedDevelopment.EmbeddedDevelopment`:[^acap-device-setup]

```html
http://192.168.0.90/axis-cgi/param.cgi?action=list&group=Properties.EmbeddedDevelopment.EmbeddedDevelopment
```

Thiết bị hỗ trợ ACAP trả về:

```bash
Properties.EmbeddedDevelopment.EmbeddedDevelopment=yes
```

## Đọc thông tin thiết bị qua VAPIX

Thông tin cơ bản (AXIS OS version, kiến trúc, model, SoC) lấy bằng POST tới `basicdeviceinfo.cgi` với method `getAllProperties`:[^acap-device-setup]

```sh
curl \
  -u <username>:<password> \
  --anyauth \
  --data '{"apiVersion":"1.3","context":"Client defined request ID","method":"getAllProperties"}' \
  "http://192.168.0.90/axis-cgi/basicdeviceinfo.cgi"
```

Response JSON chứa `propertyList` với các trường đáng chú ý:[^acap-device-setup]

| Trường | Ví dụ trong tài liệu | Dùng để |
| --- | --- | --- |
| `Architecture` | `aarch64` | Chọn `ARCH` khi build (`armv7hf` hoặc `aarch64`) |
| `Version` | `12.0.91` | Đối chiếu AXIS OS/ACAP và chọn SDK |
| `Soc` | `Axis Artpec-8` | Xác định thế hệ phần cứng và khả năng DLPU |
| `SerialNumber` | `B8A44F7D507D` | Định danh thiết bị, hostname mDNS, yêu cầu CFC |
| `SocSerialNumber` | `4E78C475-010102B7` | Processor Serial Number, dùng cho yêu cầu CFC |
| `BuildDate` | `Sep 26 2024 18:22` | Phiên bản build AXIS OS |

Có thể thêm `| jq` sau lệnh curl để pretty-print JSON. Đây cũng là nguồn thông tin cho yêu cầu Custom Firmware Certificate khi cần [SSH và Developer Mode](axis-device-ssh-developer-mode.md).

## Nâng cấp AXIS OS

Axis quản lý device software theo track active hoặc LTS; dù chọn track nào cũng nên nâng cấp thường xuyên để có bản vá bảo mật. Ở production nên dùng VMS (ví dụ AXIS Camera Station) hoặc phần mềm quản lý thiết bị; nâng cấp thủ công qua web interface hoặc VAPIX cũng được. File AXIS OS mới phải có sẵn trên máy phát triển trước khi nâng cấp.[^acap-device-setup]

### Qua web interface

Đường dẫn thay đổi theo phiên bản giao diện:[^acap-device-setup]

| AXIS OS hiện tại | Đường dẫn |
| --- | --- |
| 10.0 trở lên | **Maintenance** → **AXIS OS upgrade** → **Upgrade** |
| 7.10 – 9.80 | **Settings** → tab **System** → **Maintenance** → **Upgrade Server** |
| Trước 7.10 | **Setup** → **System Options** → **Maintenance** → **Upgrade Server** |

Sau khi chọn file và loại upgrade, quá trình mất 1–10 phút và gồm bốn bước: shutdown (application dừng, kết nối bị ngắt), upload AXIS OS (đèn nguồn nhấp nháy xanh/amber), reboot, rồi reconfiguration (đèn trạng thái amber). Khi hoàn tất và hệ thống sẵn sàng, đèn trạng thái chuyển xanh.[^acap-device-setup]

### Qua VAPIX

Dùng Firmware management API với method `upgrade`:[^acap-device-setup]

```sh
curl \
  -u <username>:<password> \
  --anyauth \
  -F json='{"apiVersion": "1.5", "context": "Client defined request ID", "method": "upgrade"}' \
  -F file=@<PATH_TO_SOFTWARE_FILE> \
  "http://192.168.0.90/axis-cgi/firmwaremanagement.cgi"
```

Response trả `firmwareVersion` của bản vừa nâng, ví dụ `12.0.91`.[^acap-device-setup]

## Độ phủ nguồn

- Entry point: `raw/acap/get-started/set-up-developer-environment/set-up-device/index.md` (2180 từ), thuộc bộ ACAP 12. Đã đọc toàn bộ trang.
- Ảnh duy nhất là thumbnail video hướng dẫn đặt mật khẩu (`assets/640.mp4_001.jpg`), không chứa thông tin ngoài các bước đã mô tả; loại trừ như asset trang trí.
- Các trang được nguồn dẫn tới nhưng **không có trong** `raw/`: hướng dẫn gán IP của help.axis.com, tải Axis IP Utility/ADM, tài liệu VAPIX basicdeviceinfo và firmware management, trang tải device software, tài liệu từng sản phẩm và VMS.
- Mọi lệnh curl trong trang dùng IP mẫu `192.168.0.90`; response JSON là ví dụ từ một thiết bị cụ thể (Q1656, AXIS OS 12.0.91), không phải giá trị cố định cho mọi thiết bị.
- Trang không nêu yêu cầu tối thiểu của AXIS OS cho ACAP ngoài việc kiểm tra parameter; điều kiện phiên bản được tổng hợp ở [phiên bản ACAP](acap-versioning.md).

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12). Không có claim nào **Reproduced**: không chạy curl, không discovery thiết bị thật, không nâng cấp AXIS OS trong lần ingest này. Các bước web interface có thể khác trên giao diện AXIS OS thực tế; kiểm tra lại trên thiết bị trước khi dùng làm runbook.

## Relationships

- **Requires** [Môi trường phát triển ACAP](acap-dev-environment-setup.md) trên máy host để build sau khi thiết bị đã sẵn sàng.
- **Constrained by** [phiên bản ACAP và AXIS OS](acap-versioning.md): `Version` đọc từ thiết bị quyết định bộ SDK và manifest schema.
- **Precedes** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): cần IP, tài khoản quản trị và AXIS OS phù hợp trước khi cài `.eap`.
- **Enables** [SSH và Developer Mode](axis-device-ssh-developer-mode.md): serial number, SoC và SoC serial number là đầu vào để xin CFC.
- **Uses** VAPIX (`param.cgi`, `basicdeviceinfo.cgi`, `firmwaremanagement.cgi`) để kiểm tra và nâng cấp thiết bị.
- **Used by** [triển khai custom AI model](axis-custom-model-deployment.md): cần kiến trúc và AXIS OS đúng trước khi chạy `larod-client`.
- **Configured by** [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md): đặt global proxy (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) khi application cần internet qua proxy.

[^acap-device-setup]: Tài liệu chính thức: [Set up device — Axis developer documentation](../raw/acap/get-started/set-up-developer-environment/set-up-device/index.md), toàn bộ trang: §Find the device on the network (Axis IP Utility, ADM, avahi-discover, serial number, nmap, still not found), §Access the device, §Setup the device on the network (tamper check, secure password), §Check device compatibility, §Check device properties, §How to upgrade (web interface theo phiên bản và VAPIX).
