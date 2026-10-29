# Axis camera gửi custom event qua ONVIF như thế nào?

**Có thể triển khai:** chạy ứng dụng **ACAP Native** trên camera, dùng thư viện **AXEvent** để khai báo và phát event vào hệ thống event của camera. Phía NVR/VMS hoặc một ONVIF client bên ngoài tạo subscription và lấy event qua ONVIF Events.

Điểm quan trọng là custom code **không nhất thiết tự tạo SOAP XML hay tự mở ONVIF server**. Trong ví dụ Axis, ứng dụng gọi AXEvent; sau đó client dùng ONVIF để khám phá topic và nhận notification.

```text
Camera Axis
┌─────────────────────────────────────────────────────────┐
│ Custom ACAP                                             │
│  VDO → AI/model → logic phát hiện → AXEvent             │
│                                      │                  │
│                            Axis event system             │
└──────────────────────────────────────┼──────────────────┘
                                       │
                 ONVIF Events: GetEventProperties
                 → CreatePullPointSubscription → PullMessages
                                       │
                              NVR / VMS / client
```

Đây là **synthesis** từ ví dụ producer và ONVIF client của Axis, không phải kết quả đã chạy trên camera trong phiên này. Nguồn chính là [wiki: ACAP events](wiki/acap-example-events-and-parameters.md), cùng [README và source `send_event`](raw/acap-native-sdk-examples/axevent/send_event/README.md) và [ONVIF helper `get_eventlist.py`](raw/acap-native-sdk-examples/axevent/get_eventlist.py).

## 1. Trước hết cần phân biệt: “ONVIF event chuẩn” và “event tùy biến được truyền qua ONVIF”

Axis có ví dụ chính thức phát **event chuẩn**:

```text
Topic:  tns1:Monitoring/ProcessorUsage
Source: Token
Data:   Value
```

Ví dụ này dùng namespace `tns1`, topic và cấu trúc `ProcessorUsage` theo ONVIF. Tuy nhiên, **không nên lấy topic `ProcessorUsage` rồi nhét vào đó kết quả AI không liên quan**: client có thể hiểu `Value` là processor usage.

Với event riêng như `HelmetViolation`, `PersonInZone` hay `VehicleDetected`, tài liệu ví dụ hướng dẫn dùng **Axis-defined namespace `tnsaxis`**, với `topic0` là `CameraApplicationPlatform`. Theo README, event kiểu Axis này cũng hiển thị trong trang event/rule của camera, khác với ví dụ event `tns1`. Nguồn: [send_event README, “Generate Axis events”](raw/acap-native-sdk-examples/axevent/send_event/README.md).

Điều đó dẫn đến hai câu hỏi tích hợp khác nhau:

1. **Camera có cung cấp notification của custom topic qua ONVIF Events không?** Cần kiểm tra topic thực tế bằng `GetEventProperties` và `PullMessages`.
2. **NVR/VMS đích có nhận và cho tạo rule từ topic vendor-specific đó không?** Phụ thuộc client; nguồn hiện có không chứng minh mọi NVR đều hỗ trợ custom `tnsaxis`.

> **Chưa có bằng chứng chạy thực tế trong nguồn đã kiểm tra** rằng mọi custom `tnsaxis` event đều xuất hiện và được mọi VMS xử lý qua ONVIF. Đây là điểm bắt buộc PoC với đúng camera, firmware và VMS.

## 2. Cấu trúc event ONVIF nhìn từ client

README của Axis đưa ra notification mẫu như sau; đây là **trích lược từ ví dụ `ProcessorUsage`**, không phải output thực tế từ camera của bạn:

```xml
<wsnt:NotificationMessage>
  <wsnt:Topic
      Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">
    tns1:Monitoring/ProcessorUsage
  </wsnt:Topic>

  <wsnt:Message>
    <tt:Message UtcTime="2020-08-11T11:48:43Z"
                PropertyOperation="Initialized">
      <tt:Source>
        <tt:SimpleItem Name="Token" Value="0"/>
      </tt:Source>
      <tt:Data>
        <tt:SimpleItem Name="Value" Value="100.000000"/>
      </tt:Data>
    </tt:Message>
  </wsnt:Message>
</wsnt:NotificationMessage>
```

Ý nghĩa:

- **Topic:** loại event; client dùng để lọc.
- **Source:** định danh nguồn event, ví dụ `Token`.
- **Data:** giá trị event, ví dụ `Value`.
- **UtcTime:** thời gian event.
- **PropertyOperation:** ví dụ `Initialized` cho trạng thái ban đầu và `Changed` cho thay đổi. README cũng minh họa `Changed` qua RTSP metadata.

Ở ví dụ này event là **stateful/property event**. Vì vậy khi subscribe, client có thể nhận trạng thái khởi tạo; không nên coi mọi `Initialized` là một vi phạm mới. Nguồn: [README `send_event`, phần output ONVIF và GStreamer](raw/acap-native-sdk-examples/axevent/send_event/README.md).

AXEvent còn được tài liệu SDK mô tả có **stateless/pulse, stateful và data events**. Chọn loại theo ý nghĩa nghiệp vụ; nguồn ví dụ cụ thể đã đọc triển khai stateful, không đủ để kết luận chi tiết hành vi của mọi loại. Xem [API catalog](wiki/acap-native-sdk-api-catalog.md).

## 3. Ví dụ triển khai: bắt đầu từ source `send_event` của Axis

### 3.1. Vòng đời trong code

Trong [`send_event.c`](raw/acap-native-sdk-examples/axevent/send_event/app/send_event.c), trình tự thực tế là:

1. `ax_event_handler_new()` tạo handler.
2. Tạo `AXEventKeyValueSet` mô tả topic, source và data.
3. `ax_event_handler_declare(...)` đăng ký event.
4. Chờ callback `declaration_complete`: source ghi rõ chỉ sau callback này declaration mới dùng để gửi event.
5. Khi có dữ liệu, tạo `AXEvent` bằng `ax_event_new2(...)`.
6. Gửi qua `ax_event_handler_send_event(...)`.
7. Khi kết thúc, undeclare và giải phóng handler.

Ví dụ Axis dùng GLib main loop và timer gửi mỗi 10 giây. Với AI thực tế, thay timer bằng logic của bạn: **khi kết quả inference làm trạng thái thay đổi thì gửi event**, và cân nhắc debounce/cooldown để tránh spam. Đây là khuyến nghị thiết kế, không phải hành vi mặc định của ví dụ.

### 3.2. Chỗ cần sửa trong source mẫu

Trong `setup_declaration`, source hiện tại có đoạn:

```c
ax_event_key_value_set_add_key_value(
    key_value_set,
    "Value",
    NULL,
    &start_value,              // source mẫu hiện tại
    AX_VALUE_TYPE_DOUBLE,
    NULL);
```

Nhưng `start_value` đã là `gdouble *`; `&start_value` là địa chỉ của biến con trỏ, không phải địa chỉ của giá trị `gdouble`. Với đoạn source này, cần sửa thành:

```c
ax_event_key_value_set_add_key_value(
    key_value_set,
    "Value",
    NULL,
    start_value,               // gdouble *
    AX_VALUE_TYPE_DOUBLE,
    NULL);
```

Đây là nhận xét **static inspection**, không phải bản vá đã build/chạy. Wiki cũng ghi nhận lỗi này: [ACAP events — observed defects](wiki/acap-example-events-and-parameters.md).

### 3.3. Chuyển ví dụ sang Axis-defined topic

README đề xuất đổi topic declaration sang:

```c
ax_event_key_value_set_add_key_value(
    key_value_set, "topic0", "tnsaxis",
    "CameraApplicationPlatform", AX_VALUE_TYPE_STRING, NULL);

ax_event_key_value_set_add_key_value(
    key_value_set, "topic1", "tnsaxis",
    "ProcessorUsage", AX_VALUE_TYPE_STRING, NULL);
```

Cho ứng dụng của bạn, về mặt thiết kế có thể đặt topic thứ hai theo nghiệp vụ, chẳng hạn `HelmetViolation`, **nhưng phải kiểm tra declaration và output thực tế trên camera**.

**Lưu ý quan trọng:** không chỉ đổi hai dòng `topic0`/`topic1` một cách máy móc. README còn thay namespace của `Token` và `Value`; trong khi phần `mark_as_source`, `mark_as_data` và đoạn gửi event trong source gốc cũng tham chiếu đến các key đó. Cần điều chỉnh nhất quán namespace/key ở toàn bộ các chỗ declaration, đánh dấu source/data và send, rồi kiểm tra bằng `GetEventProperties`/`PullMessages`. README chỉ đưa một đoạn thay declaration, không cung cấp một producer custom hoàn chỉnh đã xác minh end-to-end.

Một thiết kế ban đầu dễ kiểm thử:

```text
Topic:  tnsaxis:CameraApplicationPlatform/HelmetViolation
Source: định danh camera/channel hoặc detector
Data:   trạng thái active / inactive
```

Đây là **đề xuất schema**, không phải XML output hay API code đã được xác thực. Tên field, kiểu ONVIF, namespace và khả năng VMS nhận custom field phải được xác minh trên thiết bị đích. Với bài toán object metadata chi tiết như bounding box, track ID, class, confidence, không nên mặc định rằng mọi VMS sẽ hiển thị các field tùy biến trong event.

## 4. Build, cài và chạy thử ví dụ chính thức

Ví dụ nằm tại:

- [README tổng của AXEvent](raw/acap-native-sdk-examples/axevent/README.md)
- [README build `send_event`](raw/acap-native-sdk-examples/axevent/send_event/README.md)
- [Source `send_event.c`](raw/acap-native-sdk-examples/axevent/send_event/app/send_event.c)

Sau khi copy source sang thư mục làm việc riêng và sửa lỗi con trỏ, trong thư mục `send_event`:

```bash
# Ví dụ cho camera aarch64
docker build --platform=linux/amd64 \
  --build-arg ARCH=aarch64 \
  --tag send-event:1.0 .

docker cp "$(docker create --platform=linux/amd64 send-event:1.0):/opt/app" ./build
```

Sau đó upload `.eap` tại **Apps** trong giao diện camera và **Start** ứng dụng. Manifest mẫu đặt `runMode: "never"`, nên không nên giả định app tự chạy sau cài đặt. Nguồn: [Dockerfile](raw/acap-native-sdk-examples/axevent/send_event/Dockerfile), [manifest](raw/acap-native-sdk-examples/axevent/send_event/app/manifest.json), [README](raw/acap-native-sdk-examples/axevent/send_event/README.md).

**Chú ý tương thích:**

- Dockerfile snapshot này mặc định `armv7hf` và SDK `12.11.0`; không dùng nguyên mặc định cho camera `aarch64`.
- Chọn SDK theo **AXIS OS và API trên camera**, không chỉ theo kiến trúc CPU. Xem [bảng tương thích SDK/AXIS OS](wiki/acap-chip-architecture-and-sdk-compatibility.md).
- README mẫu nói bật **Allow unsigned apps**, nhưng chính sách ký phụ thuộc AXIS OS; wiki ghi nhận AXIS OS 13 yêu cầu signed app. Kiểm tra [ACAP signing](wiki/acap-application-signing.md) trước khi triển khai.
- Code ví dụ bỏ qua nhiều xử lý lỗi; production cần xử lý lỗi declare/send, lifecycle, restart và tài nguyên.

## 5. Kiểm tra từ ONVIF client

### Bước A — Tạo ONVIF user

README yêu cầu tạo **ONVIF account** trên camera tại trang System → ONVIF. Đừng giả định tài khoản đăng nhập web thông thường mặc nhiên là ONVIF user. [Nguồn](raw/acap-native-sdk-examples/axevent/README.md).

### Bước B — Khám phá topic

Axis cung cấp `get_eventlist.py`, cần Python `requests` và `xmllint`:

```bash
cd raw/acap-native-sdk-examples/axevent

python3 get_eventlist.py getlist \
  -i <CAMERA_IP> -u <ONVIF_USER> -p '<ONVIF_PASSWORD>'
```

Script gọi **`GetEventProperties`**; code hiện tại ghi kết quả vào:

```text
onviflist.xml
```

Tìm topic và xem `MessageDescription`, các trường `Source`/`Data`, kiểu dữ liệu và `IsProperty`. README gọi file là `onviflist.xml.new`, nhưng code dùng `onviflist.xml`; nên tin tên trong code snapshot này. Tránh để password thật trong shell history hoặc danh sách process khi dùng lâu dài.

### Bước C — Subscribe và lấy notification

```bash
python3 get_eventlist.py getsent \
  -i <CAMERA_IP> -u <ONVIF_USER> -p '<ONVIF_PASSWORD>' \
  -t 20
```

Theo code, script gọi:

```text
CreatePullPointSubscription
        ↓
đợi
        ↓
PullMessages
        ↓
sentonviflist.xml
```

**Cảnh báo trước khi dùng `getsent`:** SOAP payload trong script hard-code:

```xml
<wsa:To>http://192.168.0.90/onvif/services</wsa:To>
```

Dù bạn đã truyền `-i <CAMERA_IP>`, trường này không tự đổi. Hãy sửa trong **bản copy làm việc**, không sửa `raw/`, hoặc dùng một ONVIF client khác tuân theo subscription endpoint của camera. Script cũng có các giới hạn xử lý lỗi và dùng shell để format XML; chỉ nên xem là công cụ demo, không bê nguyên vào production. Nguồn: [`get_eventlist.py`](raw/acap-native-sdk-examples/axevent/get_eventlist.py) và [wiki defects](wiki/acap-example-events-and-parameters.md).

Để debug riêng ứng dụng trên camera, README đưa log:

```text
http://<CAMERA_IP>/axis-cgi/admin/systemlog.cgi?appname=send_event
```

**Checklist PoC với VMS thực:**

1. App start và declaration callback thành công.
2. `GetEventProperties` thấy đúng topic, source/data và kiểu.
3. `PullMessages` nhận được event khi kích hoạt điều kiện.
4. Phân biệt trạng thái `Initialized` với thay đổi thực tế.
5. VMS đích thấy topic custom, cho lọc và tạo rule/action.
6. Thử app restart, camera restart, mất/kết nối lại và tình huống nhiều event. Các hành vi này cần đo, không được suy từ demo.

## 6. Camera nào phù hợp?

Không có một model camera duy nhất bắt buộc. Theo [API catalog](wiki/acap-native-sdk-api-catalog.md), AXEvent được liệt kê cho ARTPEC-6/7/8/9 và CV25; tuy nhiên **khả năng thực tế còn phụ thuộc sản phẩm, AXIS OS và phiên bản SDK**.

Nếu bạn cần **custom AI chạy trực tiếp trên camera**, hai ứng viên để khảo sát là **AXIS Q1728-LE** và **AXIS P1488-LE**, được wiki ghi nhận là ARTPEC-9. Tuy nhiên, thông tin riêng của hai model trong wiki dựa chủ yếu trên nguồn thứ cấp; datasheet sản phẩm chưa được đối chiếu cục bộ. Vì vậy đây là **ứng viên PoC**, chưa phải xác nhận rằng tổ hợp model + firmware + custom ONVIF event + VMS của bạn đã được hỗ trợ. Xem [trang chọn camera](wiki/axis-artpec-9-camera-selection.md).

Nếu chỉ cần phát event từ một logic đơn giản, không nhất thiết cần ARTPEC-9/DLPU; chọn camera hỗ trợ ACAP và AXEvent phù hợp là điều cần kiểm tra. Nếu cần model AI, thêm yêu cầu về VDO, Larod, model format và tài nguyên.

---

### Giới hạn kiểm chứng

Tôi đã đọc wiki và kiểm tra trực tiếp `raw/`: README, source producer, subscriber, helper ONVIF, Dockerfile, manifest và Makefile của ví dụ. **Chưa build code, chưa kết nối camera, chưa capture SOAP thật và chưa thử với NVR/VMS.** Các kết luận về workflow là từ source Axis; khả năng tương tác của custom topic với một VMS cụ thể vẫn cần PoC. Tôi để câu trả lời này ở dạng tra cứu tạm thời, chưa ghi thêm synthesis vào wiki.