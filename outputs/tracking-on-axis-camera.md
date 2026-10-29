# Các phương án multi-object tracking trên camera Axis

## Kết luận trước

Nếu anh/chị **đã có detector riêng chạy trên camera**, phương án đáng thử đầu tiên là:

> **ACAP Native + detector chạy trên DLPU + tracker chạy trên CPU**, bắt đầu bằng **SORT-style** làm baseline, sau đó thử **ByteTrack-style** nếu có hiện tượng mất ID khi detection confidence giảm.

Nếu **không bắt buộc dùng detector riêng**, nên thử **Axis Scene Metadata** trước: ví dụ chính thức trong `raw/` cho thấy Axis có thể cung cấp bounding box kèm `track_id`, giúp tránh phải tự xây tracker. Nhưng đây là **sử dụng track do hệ thống Axis tạo**, không phải bằng chứng rằng có thể đưa box từ custom detector vào tracker nội bộ của Axis.

Tôi đã tìm trong `raw/`, đọc trực tiếp ví dụ detection, Message Broker, Device Data Hub và các tài liệu camera liên quan. **Chưa chạy thử trên Q1728-LE hoặc P1488-LE**; các lựa chọn tracker bên dưới là đề xuất kỹ thuật cần PoC, không phải benchmark đã được xác nhận.

---

## 1. Phân biệt hai bài toán trước khi chọn giải pháp

### A. Muốn track đối tượng mà Axis đã nhận diện

Ví dụ: người hoặc xe thuộc các class có sẵn trong scene metadata.

```text
Camera / Axis analytics
    → Axis Scene Metadata có track ID
    → ACAP consumer
    → Đếm / rule / event / backend
```

Đây là đường ngắn nhất để kiểm tra khả năng tracking sẵn có.

### B. Muốn track kết quả của custom detector

Ví dụ: detector tự huấn luyện phát hiện hàng hóa, xe nâng, thiết bị bảo hộ hoặc loại vật thể không có trong detector mặc định.

```text
VDO frame
    → custom detector trên DLPU
    → post-processing + NMS
    → custom tracker trên CPU
    → track ID / trajectory / event
```

Trong các nguồn đã kiểm tra, tôi **không thấy interface được chứng minh** để đưa detection box tùy ý vào tracker tạo ra Axis Scene Metadata. Do đó không nên thiết kế dựa trên giả định đó.

---

# 2. So sánh các option

| Option | Detection | Tracking | Khi nên chọn | Điểm cần kiểm chứng |
|---|---|---|---|---|
| **1. Dùng Axis Scene Metadata** | Axis | Axis | Class có sẵn đáp ứng yêu cầu; muốn PoC nhanh | Topic có dữ liệu trên camera/firmware thực tế; chất lượng ID; latency |
| **2. Native ACAP + SORT-style** | Custom trên camera | CPU camera | Camera cố định, cảnh tương đối thưa; baseline nhẹ | ID switch khi crossing hoặc che khuất |
| **3. Native ACAP + ByteTrack-style** | Custom trên camera | CPU camera | Detector đôi lúc trả confidence thấp; cần giữ track tốt hơn | Detector phải giữ được low-score boxes; CPU và NMS |
| **4. Native ACAP + appearance/ReID** | Custom trên camera | CPU và có thể thêm model | Cảnh đông, che khuất, cần phân biệt đối tượng giống nhau | Chi phí crop, model thứ hai, RAM/DLPU và tương thích model |
| **5. Detection trên camera, tracking ở edge server** | Custom trên camera | Server | Có nhiều camera, muốn dễ thay tracker và mở rộng tài nguyên | Đồng bộ timestamp, mạng, mất kết nối |
| **6. Video + detection + tracking ở server** | Server | Server | Muốn thử thuật toán nhanh hoặc cần GPU mạnh | Băng thông video, độ trễ, riêng tư và chi phí server |

Các tên SORT, ByteTrack và ReID ở đây là **hướng thuật toán**, không phải khẳng định có sẵn thư viện tương ứng trong SDK Axis hay đã được Axis hỗ trợ chính thức.

---

# 3. Option 1 — Dùng Axis Scene Metadata có sẵn track ID

## 3.1. Message Broker: metadata theo frame

Trong ví dụ chính thức [consume-scene-metadata qua Message Broker](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/README.md), ACAP subscribe topic:

```text
com.axis.analytics_scene_description.v0.beta
```

Payload mẫu chứa:

```json
{
  "frame": {
    "observations": [
      {
        "bounding_box": {
          "left": 0.4396,
          "top": 0.4234,
          "right": 0.7661,
          "bottom": 0.7413
        },
        "class": {
          "type": "Car",
          "score": 0.74
        },
        "timestamp": "2024-02-14T15:37:21.040577Z",
        "track_id": "25"
      }
    ],
    "operations": [
      {"id": "35", "type": "DeleteOperation"}
    ]
  }
}
```

Điểm đáng chú ý:

- Metadata có **track ID theo observation**, không chỉ detection box.
- Có timestamp và ví dụ về `DeleteOperation`.
- Code ví dụ subscribe với `source = "1"` tương ứng video channel 1.
- API/topic trong ví dụ là **beta**.
- README cũng nhắc đến `com.axis.consolidated_track.v1.beta`, nhưng ví dụ code đang subscribe topic frame-level ở trên; không nên coi đây là cùng một payload hay lifecycle.

Nguồn: [README](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/README.md), [code subscriber](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/app/consume_scene_metadata.c).

### Dùng để làm gì?

Có thể viết ACAP consumer:

```text
nhận metadata
→ parse observation
→ duy trì state theo track_id
→ kiểm tra crossing line / ROI / dwell time
→ phát event hoặc gửi backend
```

Ví dụ đếm xe qua line:

1. Lưu vị trí trước của `track_id`.
2. Lấy vị trí hiện tại.
3. Kiểm tra track đi từ phía A sang phía B.
4. Chỉ đếm một lần cho mỗi track và chiều.
5. Xử lý delete, timeout và restart.

**Không nên giả định track ID là danh tính vĩnh viễn**, hoặc duy nhất qua restart hay giữa các camera, nếu chưa có tài liệu và test cho trường hợp đó.

## 3.2. Device Data Hub: object track với path

Ví dụ [Device Data Hub consume-scene-metadata](raw/acap-native-sdk-examples/device-data-hub/consume-scene-metadata/README.md) subscribe:

```text
com.axis.scene.object_track.v1
```

Payload mẫu có:

- `id`
- `channel_id`
- `classes`
- `start_time`, `end_time`, `duration`
- `path[]`: chuỗi box và timestamp
- crop image trong payload mẫu

Manifest ví dụ bật:

```json
{
  "resources": {
    "deviceDataHub": {
      "enabled": true
    }
  }
}
```

**Điểm cần test:** payload mẫu có trajectory và thời gian kết thúc, nhưng tôi chưa có bằng chứng đủ để khẳng định topic phát ngay theo từng frame, chỉ khi track kết thúc, hay theo một lifecycle khác trên hai camera này. Hãy đo thời điểm nhận message trên firmware thực tế trước khi dùng cho rule real-time.

[Device Data Hub README](raw/acap-native-sdk-examples/device-data-hub/README.md) nói API này **không nhằm stream binary data**. Dù ví dụ payload có crop, không nên chọn Data Hub làm kênh truyền video.

### Khi nào option 1 phù hợp?

- Class của Axis đáp ứng bài toán.
- Chấp nhận logic detection/tracking do Axis quyết định.
- Cần line crossing, dwell time, ROI, thống kê hoặc event.

### Khi nào không phù hợp?

- Phải track class do custom detector định nghĩa.
- Cần điều khiển trực tiếp association, threshold, lifecycle và mô hình track.
- Chưa xác nhận được metadata producer/topic trên đúng firmware.

---

# 4. Option 2 — Native ACAP + SORT-style tracker

Đây là **baseline tôi đề xuất cho custom detector**.

## Kiến trúc

```text
VDO frame + timestamp
       │
       ▼
Larod + custom model trên ARTPEC-9 DLPU
       │
       ▼
Decode → confidence filtering → NMS
       │
       ▼
Detection list:
[x1, y1, x2, y2, score, class]
       │
       ▼
CPU tracker:
predict → associate → update → create/delete track
       │
       ├── track ID + trajectory
       ├── overlay
       ├── line/zone/event
       └── metadata → backend
```

Ví dụ [object-detection-yolov5 của Axis](raw/acap-native-sdk-examples/object-detection-yolov5/) đã có các phần VDO, Larod, decode, filtering, NMS và overlay. Điểm thêm tracker hợp lý là **sau khi đã có danh sách detection sau NMS**, trước rule/event và rendering.

Trang wiki [phân tích ví dụ Larod detection](wiki/acap-example-larod-object-detection.md) ghi rõ pipeline, device `a9-dlpu-tflite` và các giới hạn của ví dụ.

## Tracker làm gì?

Một thiết kế SORT-style thường có:

1. **State per track:** box, velocity ước lượng, class, ID, last timestamp, số lần match.
2. **Predict:** dự đoán box ở timestamp hiện tại bằng motion model, ví dụ Kalman filter.
3. **Association:** tính overlap/IoU giữa predicted boxes và detection boxes; ghép cặp, chẳng hạn bằng Hungarian assignment.
4. **Update:** cập nhật track được ghép.
5. **Create:** tạo tentative track từ detection chưa ghép.
6. **Delete:** xóa track sau một khoảng không được match.

Đây là thiết kế đề xuất, **không phải code có sẵn trong ví dụ Axis**.

## Ưu điểm

- Không cần model ReID thứ hai.
- Tách detector trên DLPU và association trên CPU.
- Dễ đo và debug.
- Hợp với camera cố định, luồng đối tượng không quá đông.

## Nhược điểm

- Dễ đổi ID khi hai đối tượng giao nhau hoặc che khuất lâu.
- Khó nhận lại đúng ID sau khi ra khỏi hình và quay lại.
- Phụ thuộc mạnh vào chất lượng detector, FPS và điều kiện camera.

## Các quyết định thiết kế quan trọng

- Dùng **timestamp thực**, không mặc định mọi frame cách đều nhau; ví dụ Axis có thể điều chỉnh frame rate theo thời gian xử lý.
- Timeout theo **giây** hoặc quy đổi theo FPS thực, không chỉ dùng số frame cố định.
- Chỉ ghép các class tương thích; cân nhắc class smoothing nếu detector hay đổi nhãn.
- Có trạng thái `tentative → confirmed → lost → deleted`.
- Định nghĩa track ID theo `(camera_id, session_id, local_track_id)`.
- Nếu frame bị drop hoặc đến trễ, quy định rõ xử lý thay vì cập nhật sai thứ tự.

---

# 5. Option 3 — Native ACAP + ByteTrack-style

Nếu baseline SORT mất track khi detector trả confidence thấp trong lúc vật thể bị che khuất hoặc nhỏ, đây là option tiếp theo đáng thử.

## Ý tưởng

Thay vì loại toàn bộ box confidence thấp trước tracking:

```text
detections sau decode/NMS
    ├── high-confidence detections
    └── low-confidence detections

Pass 1: match track với high-confidence
Pass 2: thử match các track còn lại với low-confidence
New track: dùng điều kiện chặt hơn
```

Lợi ích kỳ vọng: box confidence thấp vẫn có thể giúp **duy trì một track đã tồn tại**, thay vì lập tức làm mất track.

## Điểm tích hợp rất quan trọng trong ví dụ Axis

Trong [code YOLOv5](raw/acap-native-sdk-examples/object-detection-yolov5/app/object_detection_yolov5.c), `filter_detections()` lọc theo `conf_threshold` **trước NMS**. Nếu threshold ở detector đã loại hết low-score boxes thì tracker kiểu ByteTrack không còn dữ liệu cho lượt association thứ hai.

Vì vậy cần:

1. Chọn ngưỡng detector đủ thấp để giữ candidate cần thiết.
2. Chạy NMS và đưa tracker cả hai nhóm confidence.
3. Dùng ngưỡng tạo track mới cao hơn ngưỡng duy trì track.
4. Giới hạn số candidate và đo CPU: ngưỡng thấp có thể làm tăng chi phí NMS và association.
5. Thống nhất định nghĩa score: code ví dụ phân biệt **object likelihood** và **class likelihood**; không được mặc định chúng là cùng một confidence.

**Cảnh báo:** wiki phân tích example ghi nhận NMS của ví dụ là quadratic; hạ threshold có thể làm bottleneck rõ hơn. Cần profile thay vì mặc định tracker là phần tốn CPU nhất. Xem [phân tích example](wiki/acap-example-larod-object-detection.md).

## Khi nào ưu tiên?

- Occlusion ngắn.
- Detector khá tốt nhưng confidence dao động.
- Muốn cải thiện ID continuity mà chưa muốn thêm ReID model.

**Giới hạn bằng chứng:** chưa tìm thấy implementation ByteTrack hay benchmark ByteTrack trên hai camera này trong các nguồn đã khảo sát. Cần tự chọn implementation, kiểm tra license, cross-compile và đo trên thiết bị.

---

# 6. Option 4 — Tracker có appearance / ReID

## Ý tưởng

Ngoài vị trí và chuyển động, lấy crop của đối tượng rồi tính **appearance embedding** để hỗ trợ ghép track:

```text
detection box
    → crop / resize
    → ReID model
    → embedding

association cost =
    motion / IoU
  + appearance similarity
  + class constraints
```

Đây là hướng tương tự nhóm DeepSORT hoặc các tracker có appearance association. Tên cụ thể không đồng nghĩa mọi implementation đều có cùng hành vi hoặc chi phí.

## Khi đáng thử

- Nhiều người hoặc xe giao nhau.
- Che khuất tương đối lâu.
- Chi phí ID switch cao hơn chi phí CPU/DLPU bổ sung.
- Có dữ liệu thực tế để kiểm tra embedding có phân biệt được đối tượng trong môi trường đó.

## Rủi ro trên camera

- Thêm crop/resize, model inference và bộ nhớ.
- ReID chạy CPU có thể chậm; chạy DLPU lại cạnh tranh tài nguyên với detector.
- Cần kiểm tra model ReID có thể lượng tử hóa, export và chạy được trên ARTPEC-9 hay không.
- Appearance không bảo đảm đúng ID: đồng phục giống nhau, thay đổi ánh sáng, góc nhìn hoặc box quá nhỏ đều có thể gây nhầm.
- License của model và thư viện phải được kiểm tra riêng.

**Khuyến nghị:** không bắt đầu từ option này nếu chưa đo được baseline SORT/ByteTrack-style. Chỉ bổ sung ReID khi dữ liệu thực cho thấy ID switch là bottleneck và chi phí bổ sung chấp nhận được.

---

# 7. Option 5 — Detection trên camera, tracking ở edge server

```text
Camera:
VDO → DLPU detector → detections + timestamp
                              │
                              ▼
Edge server:
association → tracking → rules → database / VMS
```

## Ưu điểm

- Vẫn tận dụng detector trên camera.
- Server dễ chạy tracker nặng hơn, Python/C++, hoặc nhiều cấu hình thử nghiệm.
- Có thể gom tracking/rule của nhiều camera về một nơi.

## Hạn chế

- Cần tự thiết kế hoặc xác nhận đường xuất detection phù hợp; các ví dụ đã đọc **không chứng minh sẵn một API export custom detection end-to-end**.
- Mất mạng hoặc reorder message có thể làm sai association.
- Camera và server cần xử lý clock/timestamp, frame ID và reconnect.
- Gửi box không mang đủ appearance để làm ReID; muốn ReID cần gửi thêm crop, embedding hoặc video, kéo theo chi phí và vấn đề riêng tư.

### Payload đề xuất

```json
{
  "camera_id": "camera-01",
  "session_id": "boot-or-app-session",
  "frame_id": 12345,
  "capture_timestamp": "...",
  "coordinate_space": "frame-normalized",
  "detections": [
    {
      "bbox_xyxy": [0.10, 0.20, 0.30, 0.70],
      "class_id": 1,
      "score": 0.83
    }
  ]
}
```

Đây là **schema gợi ý**, không phải schema Axis chuẩn. Cần bổ sung version, clock semantics, crop/rotation, bảo mật và chính sách khi mất kết nối.

---

# 8. Option 6 — Đưa video về server, detection và tracking đều ở server

```text
Axis camera → video stream → edge server/GPU
                              ├── detector
                              └── tracker
```

Phù hợp khi:

- Cần thử nhanh nhiều detector/tracker.
- Camera CPU/RAM không đủ.
- Cần ReID nặng, phân tích nhiều camera hoặc xử lý thêm downstream.

Đổi lại:

- Tốn băng thông video và tài nguyên server.
- Cần quản lý độ trễ, buffering, mất kết nối và quyền truy cập video.
- Có thể không đáp ứng yêu cầu privacy hoặc hoạt động độc lập tại edge.

**Lưu ý:** multi-camera tracking là bài toán riêng. Track ID trong từng camera không tự động trở thành cùng một identity giữa camera; cần association xuyên camera, đồng bộ thời gian và chính sách privacy riêng.

---

# 9. Khác biệt giữa Q1728-LE và P1488-LE

Nguồn nghiên cứu thứ cấp trong `raw/` báo cáo cả hai dùng **ARTPEC-9**; Q1728-LE có **4 GB RAM**, P1488-LE **2 GB RAM**. Tuy nhiên wiki đã ghi rõ các thông số sản phẩm này **chưa được đối chiếu datasheet chính hãng lưu cục bộ**, và nguồn thứ cấp còn có điểm không nhất quán về thông số Q1728-LE. Xem [camera selection](wiki/axis-artpec-9-camera-selection.md).

Nếu các thông số đó đúng:

- **Q1728-LE:** có thêm dư địa thử nhiều buffer, detector lớn hơn hoặc ReID; không đồng nghĩa DLPU nhanh gấp đôi.
- **P1488-LE:** nên bắt đầu bằng detector nhỏ + tracker motion/IoU và theo dõi peak memory.
- Cả hai vẫn cần đo trên đúng thiết bị, AXIS OS, model và workload.

Axis Model Zoo có benchmark ARTPEC-9 trên **Q1728**, nhưng không phải benchmark end-to-end tracking trên Q1728-LE/P1488-LE. Không lấy số inference đó làm FPS tracking. Xem [benchmark results](wiki/axis-model-zoo-benchmark-results.md).

---

# 10. Kế hoạch PoC đề xuất

## Giai đoạn 1 — Kiểm tra Axis track có sẵn

1. Ghi lại model camera, AXIS OS và trạng thái analytics.
2. Build example Message Broker cho kiến trúc phù hợp.
3. Cho người/xe di chuyển, giao nhau, bị che khuất.
4. Quan sát:
   - Topic có dữ liệu không?
   - `track_id` ổn định bao lâu?
   - Có delete operation không?
   - Độ trễ từ hình ảnh đến metadata?
   - ID xử lý thế nào khi restart?
5. Thử Device Data Hub topic nếu firmware hỗ trợ và đo lifecycle của message.

Nếu metadata Axis đáp ứng class và chất lượng, có thể dừng ở đây và chỉ viết business logic.

## Giai đoạn 2 — Custom detection + baseline tracking

1. Bắt đầu từ [object-detection-yolov5](raw/acap-native-sdk-examples/object-detection-yolov5/) hoặc detector đang có.
2. Ghi detection sau NMS kèm timestamp.
3. Thêm SORT-style tracker trên CPU.
4. Xuất `track_id`, box, class và trạng thái track.
5. So sánh:
   - Detection-only.
   - Detection + SORT-style.
   - Detection + ByteTrack-style.
6. Sau đó mới thử ReID nếu vẫn chưa đạt mục tiêu.

Nếu hiển thị box/trajectory trên video, xem [các ví dụ overlay và bounding box](wiki/acap-example-overlays-and-bounding-box.md); cần xử lý đúng phép biến đổi tọa độ giữa frame gốc, crop, resize và rotation.

## Giai đoạn 3 — Đánh giá bằng dữ liệu thực

Dùng **cùng video và ground truth** cho các option:

| Nhóm đo | Chỉ số |
|---|---|
| Tracking quality | IDF1, HOTA, ID switches, fragmentation |
| Bài toán nghiệp vụ | Sai số đếm, đếm lặp, bỏ sót crossing |
| Hiệu năng | FPS end-to-end, latency p50/p95, CPU, RAM peak |
| Vận hành | Chạy dài ngày, restart, frame drop, mất mạng, tải đồng thời |

Test ít nhất: **cảnh thưa/đông, ngày/đêm, vật thể nhỏ, crossing, che khuất, vật thể dừng rồi đi tiếp**.

---

## Khuyến nghị chọn nhanh

- **Class Axis có sẵn và đủ dùng:** thử **Message Broker Scene Metadata** đầu tiên.
- **Custom detector, camera cố định, cảnh không quá đông:** **Native ACAP + SORT-style**.
- **Custom detector, hay mất track vì confidence giảm:** thử **ByteTrack-style**, đồng thời sửa đường giữ low-score boxes.
- **Cảnh đông, ID switch do che khuất là vấn đề chính:** thử **appearance/ReID**, nhưng đo chi phí trước.
- **Nhiều camera hoặc tracking quá nặng trên camera:** thử **camera detection + edge-server tracking**.

Tôi đã lưu tổng hợp có thể tái sử dụng tại [wiki/axis-multi-object-tracking-options.md](wiki/axis-multi-object-tracking-options.md). Structural check chạy thành công; **chưa build ACAP, chưa chạy thiết bị và chưa xác minh benchmark tracker**.