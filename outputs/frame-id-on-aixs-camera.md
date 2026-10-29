# Đề xuất gắn định danh frame trên camera Axis và truy xuất qua RTSP/Kafka

## 1. Kết luận trước

**Hướng nên thử đầu tiên** là để một ACAP application trên camera đọc **cùng một VDO H.264/H.265 stream**, tạo `frame_id` cho từng access unit, sau đó:

1. Gửi `frame_id` cùng kết quả xử lý qua Kafka.
2. Đưa cùng `frame_id` vào **SEI user-data** của access unit tương ứng.
3. Phát luồng đã chỉnh sửa đến server.
4. Server đọc SEI, lập index `frame_id → frame đang nằm trong buffer` và ghép với Kafka.

Tuy nhiên, có một điểm quyết định:

> **Nguồn trong `raw/` xác nhận ACAP có thể đọc encoded stream qua VDO, nhưng chưa chứng minh ACAP có thể chèn SEI vào luồng RTSP mặc định do Axis phát.** Muốn phương án này chạy, có thể phải tự phát một RTSP stream riêng hoặc đặt một media gateway ở giữa. Đây là giả thuyết triển khai cần PoC, không phải tính năng Axis đã xác nhận.

Nếu không muốn tự phát RTSP stream, hướng đáng thử tiếp theo là **timestamp matching giữa frame VDO và RTSP qua RTP/RTCP**. Hướng này ít can thiệp bitstream hơn, nhưng hiện chưa có bằng chứng trong nguồn rằng timestamp ở hai đường tương ứng chính xác đến từng frame.

Và một giới hạn cơ bản:

> Nếu camera không lưu ảnh, server cũng không lưu/buffer video, thì khi Kafka message đến sau thời điểm frame đã đi qua, **không thể lấy lại frame cũ chỉ từ ID**. ID là khóa tìm kiếm, không phải bản thân ảnh. Cần ít nhất một buffer video trên server hoặc một hệ thống recording bên ngoài.

---

## 2. Những gì tìm được trong `raw/`

Tôi đã kiểm tra trực tiếp các phần liên quan trong `raw/acap-native-sdk-examples/`, `raw/acap-runtime/`, tài liệu VDO cục bộ và các ghi chú camera; đồng thời đối chiếu với wiki. Các điểm đáng chú ý:

### 2.1. ACAP có thể đọc H.264/H.265 và metadata qua VDO

Ví dụ [vdoencodeclient.c](raw/acap-native-sdk-examples/vdostream/app/vdoencodeclient.c) tạo VDO stream, hỗ trợ H.264, H.265, JPEG, NV12…; đọc `VdoBuffer`, lấy `VdoFrame` và các chunk dữ liệu. Ví dụ này log `vdo_frame_get_sequence_nbr(frame)`.

Điều này tạo cơ sở cho một ACAP app đọc encoded video và metadata. Nhưng nó **không chứng minh** encoded stream mà app đọc và RTSP stream mặc định là cùng một encoder session hoặc có cùng frame IDs/timestamps.

Xem thêm [wiki: VDO frame capture](wiki/acap-example-vdo-video-capture-and-opencl.md).

### 2.2. VDO có timestamp và sequence number, nhưng không tự động là ID toàn cục

Tài liệu VDO cục bộ mô tả:

- [`vdo_frame_get_sequence_nbr()`](raw/acap-documentation/3.5/api/vdostream/html/vdo-frame_8h.html): sequence number bắt đầu từ `0`, điểm wrap-around **không được định nghĩa**.
- [`VdoStreamTimestamp`](raw/acap-documentation/3.5/api/vdostream/html/vdo-types_8h.html): có các lựa chọn UTC, monotonic capture, monotonic server/client…; UTC được mô tả là đọc từ `custom_timestamp`.

**Chưa tìm được trong các đoạn tài liệu đã kiểm tra** đảm bảo rằng:

- Sequence number giống nhau giữa hai VDO stream hoặc giữa VDO và RTSP.
- Timestamp VDO chính là timestamp được server suy ra từ RTSP.
- Giá trị timestamp có đơn vị và ngữ nghĩa giống nhau trên mọi pipeline/firmware.

Vì vậy, không nên lấy `sequence_nbr` hoặc timestamp đơn lẻ làm `frame_id` toàn cục.

### 2.3. ACAP Runtime có trường `id`, nhưng implementation hiện không gán

Trong [`videocapture.proto`](raw/acap-runtime/apis/videocapture.proto), `GetFrameResponse` có `id`, `timestamp`, `custom_timestamp`, `sequence_nbr`.

Nhưng [`video_capture.cpp::NewStream/GetFrame`](raw/acap-runtime/src/video_capture.cpp):

- Không gán `response.id`.
- Có trả `timestamp`, `custom_timestamp`, `sequence_nbr`.
- Nhận `timestamp_type` trong proto nhưng không đưa setting này vào VDO map.

Vì vậy, **không thể dựa vào `GetFrameResponse.id` hiện tại như frame UUID**; setting timestamp cũng cần sửa và kiểm chứng, không nên chỉ đặt enum ở client. [Chi tiết trong wiki](wiki/acap-runtime-video-capture-api.md).

### 2.4. Có enum SEI, nhưng chưa thấy API chèn SEI vào RTSP mặc định

Tài liệu [`vdo-types.h`](raw/acap-documentation/3.5/api/vdostream/html/vdo-types_8h.html) có các frame type liên quan H.264/H.265 SEI. Điều đó chỉ cho biết API có khái niệm loại dữ liệu SEI; **không chứng minh** có API để ghi SEI tùy ý vào luồng RTSP do camera phát.

Tương tự, `vdo_frame_set_timestamp()` là setter trên đối tượng VDO được tài liệu mô tả, **không phải bằng chứng** timestamp đó được ghi vào RTP/RTCP hoặc bitstream của luồng RTSP mặc định.

### 2.5. Scene Metadata có timestamp, nhưng chưa chứng minh là frame ID

Ví dụ [Message Broker scene metadata](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/README.md) có `frame.observations[]`, timestamp và `track_id`. [Device Data Hub example](wiki/acap-example-device-data-hub-and-message-broker.md) cũng có object track ID/UUID.

Các ID này phục vụ **object tracking**, không nên giả định là ID duy nhất của từng video frame. Timestamp metadata có thể là ứng viên để thử matching, nhưng chưa có bằng chứng trong nguồn rằng nó map chính xác với từng frame RTSP.

### 2.6. Hai model camera

[Wiki camera selection](wiki/axis-artpec-9-camera-selection.md) tổng hợp rằng Q1728-LE và P1488-LE thuộc ARTPEC-9, nhưng nguồn thông số là nghiên cứu thứ cấp; datasheet chính thức không có trong `raw/`. Chưa có bằng chứng theo từng model/firmware về:

- Chèn SEI tùy ý vào RTSP mặc định.
- RTP header extension tùy ý.
- Quan hệ timestamp giữa VDO, analytics và RTSP.
- Khả năng phát custom RTSP server và chi phí CPU/băng thông.

Các kết luận triển khai dưới đây vì vậy áp dụng như **thiết kế cần kiểm thử**, không phải cam kết hỗ trợ của hai model.

---

# 3. Định nghĩa đúng bài toán: ID, đồng bộ và lưu trữ

Có ba việc độc lập:

1. **Identity:** Tạo một ID duy nhất cho frame.
2. **Association:** Đảm bảo ID trong Kafka và ID/timestamp từ RTSP thực sự chỉ cùng frame.
3. **Retrieval:** Giữ video đủ lâu để khi message đến có thể lấy frame.

Tạo UUID giải quyết việc **không trùng ID**, nhưng không tự giải quyết association. Ví dụ, nếu ACAP lấy một frame NV12 để inference, còn server nhận một H.264 stream độc lập, không thể mặc định frame NV12 đó là đúng frame H.264 có timestamp gần nhất.

Nên phân biệt hai mức yêu cầu:

- **Exact frame:** đúng encoded/display frame gắn với message.
- **Approximate frame:** frame gần một thời điểm, có sai số cho phép, chẳng hạn ±1 frame.

Nếu nghiệp vụ cần exact, nên ưu tiên cùng pipeline/cùng access unit thay vì chỉ đồng bộ NTP.

---

# 4. Các option

| Option | Cách ghép | Có cần sửa/phát lại video? | Độ chắc chắn | Đánh giá |
|---|---|---:|---|---|
| **A. ACAP chèn SEI + custom RTSP** | ID giống hệt trong SEI và Kafka | Có, ít nhất repacketize/phát stream riêng | Có thể exact nếu ID gắn đúng access unit | **Ưu tiên PoC nếu kiểm soát được stream** |
| **B. RTP/RTCP + timestamp VDO** | Join theo thời gian capture ước lượng | Không nhất thiết | Chưa chứng minh exact; phụ thuộc camera/pipeline | **Ưu tiên PoC nếu phải giữ RTSP mặc định** |
| **C. SEI/metadata có sẵn từ Axis** | Parse metadata camera đã phát, nếu có | Không | Chưa xác nhận tồn tại ID phù hợp | Nên khảo sát trước khi tự làm |
| **D. Server tự gán ID khi đọc RTSP** | Server quản lý ID và video cùng chỗ | Không | Exact cho frame server nhận | Đơn giản, nhưng không đáp ứng đầy đủ “camera tự sinh ID” |
| **E. Gateway trên server/edge chèn SEI** | Gateway gắn ID vào RTSP và publish mapping | Có ở gateway | Exact với frame gateway nhận | Tốt nếu camera không cho can thiệp |
| **F. Overlay ID vào ảnh** | OCR/machine-readable overlay | Có, tác động pixel | Có thể nhận diện nhưng không đẹp | Chỉ nên làm PoC/debug |

Các option A–F là **synthesis/ý tưởng thiết kế**, không phải danh sách tính năng đã được Axis xác nhận.

---

# 5. Option A — ACAP sinh ID, chèn SEI và phát RTSP riêng

## 5.1. Kiến trúc

```text
                     Camera Axis
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  VDO encoded H.264/H.265                                │
│           │                                             │
│           ▼                                             │
│  ACAP frame-ID / packetizer                             │
│    - phân biệt access unit                              │
│    - sinh frame_id                                      │
│    - chèn SEI vào access unit tương ứng                 │
│           │                         │                   │
│           │                         └── Kafka message   │
│           ▼                                             │
│  Custom RTSP/RTP stream                                 │
└───────────┬─────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────── Server ───────────────────────┐
│ RTSP → depacketize → parse SEI → frame_id                │
│                          │                              │
│                          ├→ ring buffer / recording     │
│ Kafka message → frame_id ┴→ lookup                     │
└─────────────────────────────────────────────────────────┘
```

**Điểm quan trọng:** “custom RTSP” là một thành phần phải tự xây dựng hoặc tích hợp và kiểm thử; `raw/` chưa chứng minh có API thay payload của RTSP server mặc định.

## 5.2. Format ID đề xuất

Dùng UUID ngẫu nhiên 128 bit cho từng frame, hoặc ID có cấu trúc:

```text
frame_key = (
    camera_id,
    pipeline_epoch,
    access_unit_sequence
)
```

Trong đó:

- `camera_id`: ID ổn định do hệ thống quản lý.
- `pipeline_epoch`: UUID mới mỗi khi stream/pipeline khởi tạo lại, hoặc khi không còn đảm bảo sequence liên tục.
- `access_unit_sequence`: counter 64-bit tự quản lý.

Nếu cần một trường `frame_id` duy nhất, serialize ba trường này hoặc tạo UUID từ chúng bằng cách thống nhất canonical encoding. Đồng thời giữ các trường gốc để debug.

Không dùng VDO `sequence_nbr` đơn lẻ làm counter toàn cục vì tài liệu nói sequence bắt đầu từ 0 và điểm wrap không xác định.

## 5.3. SEI payload gợi ý

Ví dụ logic:

```text
SEI user_data_unregistered:
  schema_uuid        : 16 bytes   # định danh loại payload/schema
  version            : 1 byte
  camera_id          : ...
  pipeline_epoch     : 16 bytes
  access_unit_seq    : 8 bytes
  capture_timestamp  : optional
```

**Lưu ý:** UUID định danh *schema* trong `user_data_unregistered` và UUID/ID định danh *frame* là hai thứ khác nhau. Cần tuân thủ cú pháp NAL/SEI của codec, bao gồm escaping, payload type/size và vị trí SEI phù hợp. Với H.265 cần xử lý prefix/suffix SEI theo chuẩn và kiểm thử decoder thực tế; không nên giả định cùng một đoạn byte dùng được nguyên xi cho H.264 và H.265.

## 5.4. Điều kiện để thực sự “exact”

- Chèn ID **một lần cho đúng access unit** chứa picture cần tìm, không phải một lần cho mỗi RTP packet hoặc mỗi NAL tùy ý.
- Gắn Kafka result với cùng frame đã được xử lý; nếu inference lấy frame từ pipeline NV12 khác, phải chứng minh mapping từ NV12 sang access unit H.264/H.265.
- Server parse SEI trước khi decoder hoặc transcoder làm mất metadata, rồi giữ association đến decoded frame.
- Kiểm thử frame reorder/B-frame nếu cấu hình có dùng; không mặc định decode order bằng display order.
- Kiểm thử reconnect, packet loss, SEI bị mất và stream profile thay đổi.
- Nếu server nhận stream qua proxy/NVR/transcoder, xác minh từng thành phần có giữ SEI hay không.

**Rủi ro lớn nhất của phương án A:** nếu inference và encoded stream lấy từ hai nhánh độc lập, việc chèn UUID vào encoded stream vẫn chưa chứng minh UUID gắn đúng ảnh mà model đã xử lý. PoC phải xử lý mapping này trước.

## 5.5. Khi nào chọn?

Chọn nếu:

- Kiểm soát được stream camera → server.
- Chấp nhận phát RTSP riêng hoặc đẩy video qua một gateway.
- Cần lookup chính xác theo ID.
- Có thời gian kiểm thử codec, pipeline và hiệu năng.

Không kết luận rằng camera Axis có sẵn cơ chế chèn SEI vào RTSP mặc định.

---

# 6. Option B — Timestamp VDO + RTCP Sender Report, giữ RTSP mặc định

## 6.1. Ý tưởng

```text
Camera:
  ACAP lấy VDO frame
      → lấy timestamp + camera_id + epoch
      → inference / event → Kafka

Server:
  RTSP → RTP timestamp theo frame
       + RTCP Sender Report: cặp RTP timestamp ↔ NTP time
      → ước lượng thời điểm frame
      → index theo camera + thời gian
      → join Kafka message với frame gần nhất
```

Về nguyên lý, RTCP Sender Report cung cấp các cặp thời gian RTP/NTP để ánh xạ RTP media clock sang sender wall-clock. Nhưng **không được mặc định** thời gian suy ra là sensor capture time, hay bằng timestamp VDO của ACAP.

NTP synchronization giúp các đồng hồ gần nhau; nó **không tạo ra một UUID**, không đảm bảo hai encoder/session nhìn thấy cùng frame, và không loại bỏ độ trễ cố định hoặc jitter giữa các pipeline.

## 6.2. Matching có kiểm soát

Kafka message nên mang:

```json
{
  "schema_version": 1,
  "camera_id": "cam-001",
  "pipeline_epoch": "example-epoch",
  "frame_id": "example-id",
  "capture_time_value": "example-value",
  "capture_time_domain": "vdo-utc-or-other-verified-domain",
  "capture_time_unit": "verified-unit",
  "timestamp_uncertainty_us": null
}
```

Trên server:

```text
1. Xác định camera + stream profile.
2. Chuyển timestamp RTSP về time domain đã hiệu chuẩn.
3. Tìm candidate trong khoảng [T - window, T + window].
4. Nếu đúng 1 candidate đạt tiêu chuẩn → matched.
5. Nếu nhiều candidate → ambiguous, không tự tuyên bố exact.
6. Nếu không có candidate → missing/expired.
```

Không nên chọn bừa “frame gần nhất” rồi báo là exact. Ở 30 fps, các frame cách nhau khoảng **33,3 ms**; ở 60 fps khoảng **16,7 ms**. Sai số tổng đủ lớn so với khoảng cách frame sẽ làm matching trở nên mơ hồ.

## 6.3. Cần chứng minh trước khi dùng

1. Timestamp VDO đang đọc có **đơn vị, time domain và điểm lấy timestamp** nào?
2. RTCP SR có thực sự được camera phát và client giữ lại không?
3. Mapping RTP → NTP ở stream thực tế có sai số bao nhiêu?
4. VDO frame và RTSP frame có chung nguồn capture, hay bị drop/duplicate/scale/encode ở các nhánh khác nhau?
5. Zipstream, thay đổi FPS, reconnect, điều chỉnh clock có làm mapping thay đổi không?
6. Có cần ước lượng offset cố định và uncertainty theo từng profile không?

Tài liệu VDO cục bộ liệt kê UTC và monotonic types, nhưng phần đã kiểm tra chưa cung cấp đủ thông tin để khẳng định các điều này. [Hướng dẫn migration](raw/acap/how-to-guides/extend-compatibility-to-future-axis-os-major-versions/index.md) cũng nói kiểu chọn timestamp đang chuyển từ `uint16_t` sang `uint32_t`; cần dùng tài liệu API đúng SDK/AXIS OS khi triển khai.

## 6.4. Đánh giá

- **Ưu:** Có thể giữ RTSP chuẩn của camera; ít tác động codec.
- **Nhược:** Có thể chỉ đạt approximate match. Không có bằng chứng hiện tại về exact match trên hai model.
- **Phù hợp:** tìm ảnh “gần thời điểm event”; hoặc làm exact chỉ sau khi có bằng chứng đo và quy tắc xử lý ambiguity.

---

# 7. Option C — Khảo sát metadata đã có sẵn trên stream Axis

Trước khi tự viết SEI injector, nên capture một đoạn RTSP thực tế của từng camera rồi kiểm tra:

- Có H.264/H.265 SEI nào?
- Có payload UUID/vendor metadata nào?
- Có RTP header extension hay metadata track nào?
- RTCP SR có đều và ổn định không?
- Có metadata timestamp nào có thể đối chiếu với VDO hoặc scene metadata?

**Không có bằng chứng trong `raw/` đã kiểm tra rằng camera đang phát sẵn ID frame đáp ứng yêu cầu.** Nhưng nếu có một timestamp/metadata vendor đã được tài liệu đúng firmware xác nhận, có thể giảm đáng kể công phát triển.

Dù tìm thấy SEI, vẫn phải chứng minh:

1. SEI đó gắn với từng frame hay chỉ một số frame.
2. Có ổn định qua reconnect/profile.
3. Camera application có đọc được cùng giá trị để đưa vào Kafka.
4. Không bị strip qua các thành phần trung gian.

---

# 8. Option D — Server gán ID khi nhận RTSP

```text
Camera RTSP ──► Server:
                depacketize → tạo frame_id → buffer + index
                                 │
                                 └→ publish event / metadata
```

Đây là phương án đơn giản nhất nếu yêu cầu có thể đổi thành **ID do server sinh**:

- Server nhìn thấy cùng access unit mà nó lưu, nên association nội bộ rõ ràng.
- Không cần camera hỗ trợ SEI tùy biến.
- Có thể lưu `(camera_id, session_epoch, RTP timestamp, access_unit_seq)` làm metadata debug.

Nhưng nếu inference chạy trên camera và Kafka message phải mang ID **trước khi server thấy frame**, server-generated ID không tự giải quyết mapping ngược về camera. Cần một kênh phản hồi hoặc timestamp-based join, và lại quay về khó khăn của option B.

---

# 9. Option E — Media gateway chèn ID/SEI

```text
Axis RTSP ──► Gateway ──► RTSP/recording server
                 │
                 ├─ sinh ID
                 ├─ chèn SEI hoặc tạo sidecar index
                 └─ publish mapping/event
```

Phương án này tránh sửa camera và dễ kiểm soát pipeline hơn. Nhưng:

- ID thực tế do gateway sinh, không phải camera.
- Với event Kafka từ ACAP, vẫn cần một cơ chế ghép event với frame gateway.
- Nếu inference cũng chuyển sang gateway/server, association đơn giản hơn nhiều.

Nếu không thực sự cần ID “nằm trong bitstream”, một **sidecar index** ở gateway/server có thể đơn giản hơn chèn SEI:

```text
(camera_id, session_id, access_unit_seq)
    → RTP timestamp
    → recording segment + offset / buffer entry
```

SEI hữu ích khi muốn ID đi cùng video qua nhiều nơi; sidecar hữu ích khi kiểm soát toàn bộ hệ thống và muốn tránh sửa bitstream.

---

# 10. Option F — Overlay ID vào pixel

ACAP có ví dụ overlay trong [wiki overlay examples](wiki/acap-example-overlays-and-bounding-box.md). Về ý tưởng có thể hiển thị counter, timestamp hoặc mã 2D lên hình để server đọc lại.

Nhưng đây không phải giải pháp production mặc định:

- Làm thay đổi nội dung ảnh.
- Có thể ảnh hưởng analytics, privacy hoặc trải nghiệm xem.
- OCR/mã 2D có thể sai do nén/scale/crop.
- Chưa có bằng chứng overlay cập nhật đúng một lần cho từng frame encoded.
- Overlay pipeline có thể trễ so với frame inference.

Phù hợp nhất để **debug đồng bộ** hoặc làm bằng chứng trực quan trong PoC, không nên coi là frame ID chính xác nếu chưa đo.

---

# 11. Thiết kế server buffer và truy xuất

## 11.1. Ring buffer

Server liên tục nhận stream, giữ video trong RAM hoặc disk ngắn hạn:

```text
RTSP → parse access units → ring buffer
                           → index frame_id → buffer location

Kafka → frame_id → index lookup → decode / extract image
```

Server cần xử lý cả hai thứ tự:

- **Video đến trước Kafka:** giữ video đến khi message đến.
- **Kafka đến trước video:** giữ pending message một thời gian và retry khi frame vào buffer.

Ví dụ TTL thiết kế:

```text
buffer_TTL ≥ Kafka end-to-end delay p99.9
             + video/Kafka skew
             + retry allowance
             + safety margin
```

Đây là công thức thiết kế, không phải giá trị đo.

Ước lượng lưu **encoded video**:

```text
bytes ≈ bitrate_bits_per_second × duration_seconds / 8
```

Ví dụ 8 Mbps × 60 s ≈ **60 MB/camera**, chưa tính overhead/index và biến động bitrate. Nếu lưu decoded frames thì bộ nhớ có thể lớn hơn nhiều.

## 11.2. H.264/H.265 không phải frame nào cũng decode độc lập

Nếu frame cần tìm là P/B-frame, thường phải giữ đủ dữ liệu tham chiếu từ một random access point phù hợp và decode đến frame mục tiêu. Do đó index nên trỏ tới:

```text
frame_id → stream session + segment + timestamp/order
           + vị trí random-access point phù hợp
```

Không nên thiết kế `frame_id → một NAL P-frame` rồi kỳ vọng tự decode được. Kiểm thử GOP, IDR/IRAP, parameter sets, reorder và packet loss trên codec/profile thực tế.

## 11.3. Trạng thái API nên trả rõ ràng

```text
FOUND_EXACT
FOUND_APPROXIMATE
AMBIGUOUS
NOT_RECEIVED
EXPIRED
CORRUPT_OR_UNDECODABLE
UNKNOWN_STREAM_EPOCH
```

Không trả frame gần nhất dưới nhãn exact. Dedupe Kafka theo `frame_id`, nhưng vẫn giữ event ID riêng nếu một frame có nhiều detection/event.

---

# 12. Kafka message đề xuất

Nếu chọn option A:

```json
{
  "schema_version": 1,
  "event_id": "event-uuid",
  "camera_id": "cam-001",
  "stream_profile": "h264-main-1080p",
  "pipeline_epoch": "stream-epoch-uuid",
  "frame_id": "frame-uuid",
  "frame_sequence": 123456,
  "capture_time": {
    "value": "optional-verified-value",
    "domain": "optional-verified-domain",
    "unit": "optional-verified-unit"
  },
  "event_type": "object-detected",
  "objects": []
}
```

- `frame_id`: khóa để join, không dùng timestamp làm ID duy nhất.
- `event_id`: phân biệt nhiều event trên cùng frame và hỗ trợ dedupe.
- `pipeline_epoch`: tránh nhầm sau restart/reconnect.
- `capture_time`: phục vụ quan sát và fallback, chỉ khai báo domain/unit sau khi xác minh.
- `stream_profile`: cần thiết khi camera phát nhiều profile/encoder.

Nếu dùng option B, thêm `matching_method`, `uncertainty` và không gọi kết quả là exact khi chưa chứng minh.

---

# 13. Kế hoạch PoC thực tế

## Giai đoạn 1 — Đo khả năng hiện có, chưa chèn SEI

Trên **mỗi model và firmware thực tế**:

1. Ghi model, AXIS OS, ACAP SDK, codec, resolution, FPS, Zipstream, GOP, profile.
2. Chạy biến thể của [ví dụ VDO](raw/acap-native-sdk-examples/vdostream/app/vdoencodeclient.c), log:
   - VDO stream ID/session;
   - `sequence_nbr`;
   - `timestamp`, `custom_timestamp`;
   - frame type;
   - thời gian app nhận frame.
3. Đồng thời capture RTSP/RTP/RTCP trên server:
   - RTP timestamp, SSRC, sequence packet;
   - RTCP Sender Reports;
   - access-unit boundary;
   - SEI có sẵn.
4. Dùng nguồn hình thay đổi có thể nhận biết từng frame để đối chiếu nội dung; ví dụ đồng hồ/counter hiển thị trước camera ở tốc độ phù hợp. Đây là **thiết kế thí nghiệm**, cần chọn phương pháp đủ chính xác và tránh nhầm do exposure/rolling shutter.
5. Đo phân bố offset, jitter, duplicate/drop và ambiguity giữa hai đường.
6. Lặp khi restart ACAP, restart camera, reconnect RTSP, đổi FPS/profile và khi mạng có packet loss.

**Đầu ra:** có/không thể dùng timestamp matching, kèm sai số đo và tỷ lệ ambiguous—not just một ảnh khớp.

## Giai đoạn 2 — PoC SEI

1. Bắt đầu bằng H.264, một profile, không transcoder.
2. Đọc VDO encoded stream; tạo ID theo `camera_id + epoch + counter`.
3. Chèn SEI cho đúng access unit; phát luồng qua custom RTSP hoặc gateway thử nghiệm.
4. Parse SEI trên server trước decode; đối chiếu ID với Kafka.
5. Xác nhận association đến đúng frame inference, không chỉ đúng encoded frame được injector nhìn thấy.
6. Sau đó thử H.265 và các proxy/NVR/transcoder trong hệ thống thật.

**Chỉ coi là thành công** nếu kiểm thử có:

- Không duplicate ID trong phạm vi thiết kế.
- Tỷ lệ `Kafka ID ↔ access unit ID` khớp.
- Tỷ lệ đúng **nội dung frame inference ↔ decoded frame**.
- Đếm missing, ambiguous, SEI bị strip, reconnect, corruption.
- Đo CPU, RAM, bitrate, latency trên cả Q1728-LE và P1488-LE.

## Giai đoạn 3 — Lưu trữ và tải

- Đo phân phối độ trễ Kafka/video, từ đó chọn buffer TTL.
- Kiểm thử message đến trước/sau video.
- Kiểm thử lookup khi frame đã hết hạn và khi thiếu reference frame.
- Thử số camera, bitrate và thời gian lưu mục tiêu.

---

# 14. Khuyến nghị lựa chọn

**Nếu bắt buộc camera sinh ID và server phải tìm đúng frame:**

1. Khảo sát option C xem Axis đã phát metadata hữu ích chưa.
2. Song song đo option B để biết timestamp có đủ chính xác không.
3. Nếu B không đạt exact, triển khai PoC **A: cùng pipeline encoded + SEI + custom stream**, tập trung chứng minh mapping inference ↔ encoded frame.
4. Giữ ring buffer/recording trên server.

**Nếu không bắt buộc camera sinh ID:** chọn **D hoặc E** để giảm phụ thuộc firmware và codec API của camera.

**Nếu chỉ cần ảnh gần event:** option B có thể đủ, nhưng phải công bố sai số và xử lý ambiguous.

---

## Giới hạn nghiên cứu

- Tôi đã đọc trực tiếp các nguồn `raw/` liên quan đến VDO, Runtime, ví dụ metadata và camera; **không có camera, firmware, RTSP capture hay Kafka thực tế để chạy thử**.
- Tài liệu VDO được kiểm tra gồm bản cục bộ **3.5**; không nên coi mọi chi tiết là xác nhận cho SDK/AXIS OS hiện hành trên hai model.
- Không kiểm tra được datasheet/vendor documentation online của hai camera trong phiên này.
- Tôi chưa tìm thấy trong các nguồn đã kiểm tra bằng chứng về API Axis chèn SEI tùy ý vào RTSP mặc định hoặc bảo đảm timestamp VDO ↔ RTSP là exact. **Không tìm thấy bằng chứng không có nghĩa tính năng không tồn tại.**
- Đây là tổng hợp phục vụ câu hỏi, **chưa lưu thành concept mới trong wiki**; không thay đổi `wiki/` hoặc log.