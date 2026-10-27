---
type: Concept
title: "Application logging trong ACAP"
description: "Ghi log từ ACAP application bằng syslog library, chọn priority level, đặt identifier bằng openlog, và xem log qua device web interface hoặc journalctl."
tags: [edge-ai, axis, acap, logging, debugging]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:14:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-app-logging
    resource: ../raw/acap/how-to-guides/application-logging/index.md
    scope: ../raw/acap/how-to-guides/application-logging/
    kind: docs
    revision: "ACAP version 12"
    title: "Application logging | Axis developer documentation"
---

# Application logging trong ACAP

ACAP application ghi log qua **syslog library** của AXIS OS: gọi `syslog()` với một priority level, hoặc `printf`-style format. Log hiện ở hai nơi khác nhau — **device web interface** (dành cho người dùng application) và **`journalctl`** qua SSH (dành cho developer) — và hai đường này không hoàn toàn tương đương, vì `LOG_DEBUG` chỉ xuất hiện trong `journalctl`. Nếu đặt identifier tùy biến bằng `openlog()`, các lệnh xem log mặc định sẽ không còn khớp và phải truyền đúng identifier đó.[^acap-app-logging]

## Ghi log bằng syslog

Thêm syslog library vào application:[^acap-app-logging]

```c
#include <syslog.h>
```

Sau đó dùng `syslog()`, cách dùng tương tự `printf()` nhưng tham số đầu tiên là priority level:[^acap-app-logging]

```c
syslog(LOG_INFO, "%s", "Hello World!");
```

| Priority | Ý nghĩa theo hướng dẫn |
| --- | --- |
| `LOG_INFO` | Thông tin |
| `LOG_WARNING` | Điều kiện cảnh báo |
| `LOG_ERR` | Điều kiện lỗi |
| `LOG_CRIT` | Điều kiện nghiêm trọng |

Priority thứ năm là `LOG_DEBUG`: dùng khi **không muốn** log hiện trong device web interface, nhưng chúng vẫn hiện khi xem bằng `journalctl`. Đây là lựa chọn phù hợp cho log chẩn đoán nội bộ mà người dùng cuối không cần thấy.[^acap-app-logging]

Hướng dẫn không mô tả định dạng đầy đủ của một dòng log do `syslog()` sinh ra, cũng không nói về việc log có bị giới hạn dung lượng, xoay vòng hay lưu bền qua reboot; các điểm đó chưa được kiểm chứng trong wiki này.

## Định danh log bằng openlog()

Có thể gọi `openlog()` trước lần `syslog()` đầu tiên để cấu hình cách application gửi message vào system log, ví dụ đặt identifier tùy biến. Identifier mặc định là `appName` khai báo trong `manifest.json`.[^acap-app-logging]

Điểm cần lưu ý: các phương thức xem log mặc định giả định **không** dùng identifier tùy biến. Khi đã đặt identifier riêng, log sẽ không hiện ở device web interface trừ khi sửa tham số `appname` trong URL thành identifier đó:[^acap-app-logging]

```text
http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=<CUSTOM_IDENTIFIER>
```

Với `journalctl`, identifier tùy biến là giá trị phải truyền cho `-t/--identifier`.

## Xem log

### Device web interface

Đây là cách dễ tiếp cận nhất và cũng là cách người dùng application thường xem log. Mở thiết bị tại `http://<AXIS_DEVICE_IP>`, rồi:[^acap-app-logging]

1. Vào tab **Apps**.
2. Mở application options.
3. Bấm **App log**.

Hoặc mở trực tiếp:[^acap-app-logging]

```text
http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=<APPNAME>
```

Trong URL này `<APPNAME>` là tên application (tức identifier mặc định), trừ khi application đã đặt identifier tùy biến bằng `openlog()`.

### journalctl

Khi đã SSH vào thiết bị, dùng `journalctl` để xem log. Lọc theo application bằng `-t/--identifier` và theo dõi log mới bằng `-f/--follow`:[^acap-app-logging]

```sh
journalctl -t <APPNAME> -f
```

Trợ giúp của công cụ: `journalctl -h`.[^acap-app-logging]

So với web interface, `journalctl` là đường duy nhất trong hai đường được hướng dẫn nêu là thấy được `LOG_DEBUG`, nên nó cần thiết khi debug sâu. Cần bật SSH trên thiết bị trước; xem [SSH và Developer Mode trên thiết bị Axis](axis-device-ssh-developer-mode.md).

## Độ phủ nguồn

- Entry point: `raw/acap/how-to-guides/application-logging/index.md` (445 từ), site `developer.axis.com`, bộ ACAP 12. Chỉ có một file trong scope, không có hình ảnh hay tệp đính kèm; đã đọc toàn bộ trang.
- Đã trích nguyên văn các đoạn code C và lệnh shell. Hai khối URL trong nguồn được đánh dấu fence `markdown` dù là URL trần; wiki ghi lại dưới dạng text.
- Nguồn dẫn ra ngoài `raw/`: example application `hello-world` trong repository `acap-native-sdk-examples`, và các mục *Device web interface* / *journalctl* nội bộ trang. Repository ví dụ chưa được kiểm chứng.
- Trang không nêu phiên bản AXIS OS tối thiểu, không nói log có persist qua reboot hay bị giới hạn kích thước, và không mô tả `openlog()` option nào khác ngoài identifier.

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12), đọc ngày 2026-10-27. Không có claim nào **Reproduced**: không build application, không cài lên thiết bị, không mở `systemlog.cgi` hay chạy `journalctl` thật trong lần ingest này.

## Relationships

- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): syslog library và các API của AXIS OS có sẵn trong SDK, không phải mang thư viện riêng.
- **Used by** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): bước kiểm chứng application chạy đúng dựa vào App log.
- **Requires** [SSH trên thiết bị Axis](axis-device-ssh-developer-mode.md) để dùng `journalctl` và xem `LOG_DEBUG`.
- **Constrained by** `appName` trong `manifest.json`: identifier mặc định của log, và là giá trị `appname` trong URL xem log.
- **Complements** [Remote debugging ACAP applications with GDB and VS Code](acap-remote-debugging.md): log ghi lại message application tự phát ra, còn debugger dừng application và đọc state trực tiếp.

[^acap-app-logging]: Tài liệu chính thức: [Application logging — Axis developer documentation](../raw/acap/how-to-guides/application-logging/index.md), toàn bộ trang: §Produce logs (§Basic use, §Debug logging, §Using openlog()), §View logs (§Device web interface, §journalctl). Các liên kết ra ngoài (`hello-world` example, `journalctl` help) chưa được kiểm chứng.
