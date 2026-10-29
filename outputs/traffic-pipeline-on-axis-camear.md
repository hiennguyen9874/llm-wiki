# Đánh giá khả thi: traffic detection → tracking → LPD → LPR trên camera Axis

## 1. Kết luận ngắn

**Pipeline full on-camera là khả thi về mặt kiến trúc**, nếu xác nhận hai camera có ARTPEC-9 và nếu các model tự huấn luyện thực sự chạy được trên DLPU. Nhưng tài liệu trong repository **chưa đủ để khẳng định pipeline này đạt FPS, số xe đồng thời hoặc độ chính xác cụ thể** trên AXIS Q1728-LE hay P1488-LE.

Phương án tôi khuyến nghị triển khai PoC đầu tiên:

```text
Frame camera
  ├─► Traffic detector: YOLOv5n INT8 → ARTPEC-9 DLPU
  │        └─► SORT-style tracker → CPU → track_id
  │
  └─► Frame độ phân giải cao, đồng bộ timestamp
           └─► Chọn crop xe tốt nhất theo từng track
                  └─► LPD: YOLOv5n custom INT8 → DLPU
                         └─► crop biển số
                                └─► Character detector custom → DLPU
                                       └─► CPU: sắp xếp ký tự,
                                           kiểm tra và vote theo track
```

**Không chạy LPD và LPR cho mọi xe ở mọi frame.** Chỉ xử lý những track đủ điều kiện và chọn một số frame tốt nhất. Đây là chìa khóa để pipeline có cơ hội chạy ổn trên camera.

Điểm quan trọng nhất về batch:

> Theo tài liệu Axis trong `raw/`, **ARTPEC-9 DLPU không hỗ trợ batch size > 1**. Do đó, dù một model LPD/LPR trên máy train hoặc backend khác có hỗ trợ batch, khi đưa lên `a9-dlpu-tflite` phải thiết kế quanh **mỗi inference job xử lý một input**. Nhiều object được xử lý bằng nhiều job batch 1, hoặc dùng model nhận một ảnh và trả nhiều detection—not batch nhiều ảnh.  
> [Nguồn: ARTPEC-9 optimization tips](raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md).

Tôi đã đọc cả hai survey được yêu cầu, tra cứu wiki và tìm trực tiếp trong các nguồn Axis liên quan ở `raw/`. **Chưa build, chưa train/export model LPD/LPR, chưa chạy camera, chưa đo benchmark thực tế.**

---

## 2. Trong wiki và raw có ví dụ tương tự không?

### 2.1. Có các mảnh ghép rất gần, nhưng chưa tìm thấy pipeline ALPR hoàn chỉnh

| Ví dụ tìm được | Có gì tương tự? | Thiếu gì so với yêu cầu? |
|---|---|---|
| [YOLOv5 object detection](raw/acap-native-sdk-examples/object-detection-yolov5/README.md) | VDO → Larod → detector → decode/NMS; có đường ARTPEC-9 | Không có tracking, LPD, LPR |
| [Scene Metadata consumer](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/README.md) | Nhận nhiều object trong một frame, có `Car`, `track_id`, timestamp | Dùng detector/tracker của Axis; không chứng minh có thể đưa box custom vào tracker Axis; không có LPD/LPR |
| [Object detection + crop](raw/acap-native-sdk-examples/object-detection-cv25/README.md) | Detector, stream thứ hai, crop từng object từ ảnh lớn | Ví dụ chỉ chạy **CV25**, không phải ARTPEC-9; không có LPD/LPR. Chỉ dùng làm ý tưởng |
| [Axis Model Zoo YOLOv5](raw/axis-model-zoo/docs/yolov5.md) | Có quy trình train/export YOLOv5 cho ARTPEC-9; có thể dùng làm cơ sở train detector custom | Không cung cấp model biển số hoặc ký tự đã được chứng minh chạy trên ARTPEC-9 |
| [Release notes ACAP 4.10](raw/acap-documentation/docs/release-notes/4.10.md) | Có liệt kê hai sản phẩm **License Plate Verifier Kit** | Chỉ là tên sản phẩm trong danh sách tương thích; không có kiến trúc, source code, benchmark hay bằng chứng hỗ trợ hai camera đang hỏi |

Ví dụ crop CV25 là ví dụ **gần nhất về ý tưởng cascade**, nhưng không nên copy nguyên sang ARTPEC-9. Wiki còn ghi nhận các vấn đề trong code, bao gồm threshold bị truncate và crop chưa clamp an toàn: [phân tích ví dụ CV25](wiki/acap-example-object-detection-cv25.md).

**Kết quả tìm kiếm có giới hạn:** trong các tài liệu Axis, model zoo và examples cục bộ đã khảo sát, tôi **chưa tìm thấy** implementation đầy đủ traffic detector + tracking + LPD + character detector, cũng chưa tìm thấy model LPD/LPR cụ thể kèm benchmark ARTPEC-9. Đây không phải kết luận rằng ngoài thị trường không có giải pháp tương tự.

### 2.2. Về sản phẩm Axis License Plate Verifier

Việc release notes nhắc đến License Plate Verifier Kit cho thấy Axis có sản phẩm thuộc nhóm bài toán biển số, nhưng nguồn cục bộ **không chứng minh**:

- Ứng dụng đó hỗ trợ Q1728-LE hoặc P1488-LE;
- Có thể lấy detection/recognition nội bộ của nó cho pipeline custom;
- Có thể chạy đồng thời với custom ACAP trong ngân sách DLPU mong muốn;
- Nó dùng character detector, model nào hay batch nào.

Nếu được phép dùng sản phẩm đóng của Axis, đây là **một hướng cần xác minh riêng với Axis**, không phải giải pháp đã được xác nhận trong nghiên cứu này.

---

## 3. Điều kiện tiên quyết: xác nhận chính xác hai camera

Hai survey trước dựa trên ghi chú nghiên cứu thứ cấp nói:

| Camera | SoC theo nguồn thứ cấp | RAM theo nguồn thứ cấp |
|---|---|---:|
| AXIS Q1728-LE | ARTPEC-9 | 4 GB |
| AXIS P1488-LE | ARTPEC-9 | 2 GB |

**Giới hạn:** repository chưa có datasheet Axis để đối chiếu trực tiếp các thông số gắn với đúng hai mã camera. Xem [camera selection](wiki/axis-artpec-9-camera-selection.md).

Trước khi chốt kiến trúc, xác minh trên thiết bị hoặc datasheet:

1. SoC, DLPU và Larod device `a9-dlpu-tflite`.
2. AXIS OS, ACAP Native SDK, Larod version.
3. RAM khả dụng thực tế khi camera đã chạy video, analytics và các ứng dụng khác.
4. Resolution, field of view, zoom, exposure và bitrate theo bối cảnh giao thông.

**Phần còn lại giả định cả hai camera dùng ARTPEC-9.** Nếu RAM được xác nhận, tôi sẽ bắt đầu PoC trên Q1728-LE trước để có thêm dư địa RAM, nhưng sau đó bắt buộc đo lại trên P1488-LE; RAM nhiều hơn không đồng nghĩa DLPU nhanh hơn.

---

# 4. Batch size > 1: chính xác là bị giới hạn ở đâu?

## 4.1. Phân biệt ba việc thường bị gọi chung là “batch”

### A. Một inference, nhiều ảnh đầu vào: **batch > 1**

```text
input: [B, H, W, C], B = 4

crop xe 1 ┐
crop xe 2 ├──► một model invocation ──► 4 kết quả
crop xe 3 │
crop xe 4 ┘
```

Đây là **batch thực sự**. Tài liệu Axis nói **ARTPEC-9 không hỗ trợ batch size > 1** trên DLPU. Không nên lập kế hoạch dùng `[4,H,W,C]` với `a9-dlpu-tflite`. [Nguồn](raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md).

### B. Một ảnh đầu vào, nhiều object trong ảnh: **batch 1, multi-object detection**

```text
input: [1, H, W, C]

một frame có 4 xe
        └──► một lần traffic detector
                └──► output: nhiều bounding boxes
```

Điều này **không phải batch > 1**. Tương tự:

- Một ảnh xe có thể chứa một hoặc nhiều biển số, LPD trả nhiều box.
- Một ảnh biển số có nhiều ký tự, **character detector có thể trả nhiều character boxes trong một lần inference**.

Ví dụ YOLOv5 của Axis sử dụng output được parser giả định theo dạng `[1, N, 5+C]`, với `N` là số candidate detections, không phải batch size. Xem [script đọc model parameters](raw/acap-native-sdk-examples/object-detection-yolov5/app/parameter_finder.py) và [phân tích ví dụ](wiki/acap-example-larod-object-detection.md).

### C. Nhiều job batch 1 được xếp hàng

```text
job LPD xe A: [1,H,W,C]
job LPD xe B: [1,H,W,C]
job LPD xe C: [1,H,W,C]
```

Đây là hướng thực tế cho nhiều object. Các job có thể được **submit và điều phối theo queue**, nhưng không được suy ra là chúng chạy song song thực sự trên DLPU.

FAQ Axis trong snapshot cục bộ mô tả nhiều model chạy “**concurrently but not in parallel**”, DLPU chuyển giữa các inference; FAQ này cũ hơn ARTPEC-9 nên cần xác nhận hành vi trên firmware thực tế. Không giả định các model sẽ được chia tài nguyên công bằng. [Nguồn](wiki/acap-developer-faq.md).

---

## 4.2. Những model LPD/LPR nào hỗ trợ batch > 1?

Từ evidence có trong repository, câu trả lời cụ thể là:

| Model / hướng | Batch > 1 trong framework hoặc CPU? | Batch > 1 trên ARTPEC-9 DLPU? | Tình trạng evidence |
|---|---|---|---|
| **YOLOv5n custom cho LPD**, dự kiến train từ quy trình Axis | Chưa kiểm tra một artifact custom cụ thể | **Không**, theo giới hạn DLPU | Có guide YOLOv5 ARTPEC-9, chưa có model LPD custom |
| **YOLOv5n custom character detector** | Chưa kiểm tra một artifact custom cụ thể | **Không**, theo giới hạn DLPU | Chưa có model ký tự hoặc kết quả export/test |
| **OCR/LPR model khác** | Phụ thuộc model, export và backend | **Không** nếu chạy trên ARTPEC-9 DLPU với batch > 1 | Không tìm thấy model OCR cụ thể trong nguồn cục bộ |
| Model chạy `cpu-tflite` | Có thể phụ thuộc model và interpreter; **chưa xác minh** | Không áp dụng giới hạn DLPU theo cùng cách | Chưa benchmark CPU, không thể đảm bảo đủ nhanh |
| Một model nhận **một ảnh** và phát hiện nhiều biển/ký tự | Không cần batch > 1 | Có thể là batch 1 **nếu graph tương thích** | Cần build/export/test trên camera |

Nói rõ hơn: **tôi chưa thể xác nhận một model LPD/LPR cụ thể nào trong repository hỗ trợ batch > 1**, vì chưa tìm thấy artifact hoặc tài liệu model tương ứng để kiểm tra. Ngay cả khi tìm được model upstream hỗ trợ batch, kết luận cho DLPU ARTPEC-9 vẫn là batch 1 theo tài liệu Axis.

Cũng cần phân biệt `--batch-size` trong lệnh **train** với batch của model **inference export**. Giá trị batch khi train không chứng minh shape inference trên camera. Guide Axis có ví dụ train batch 128, nhưng điều đó không thay đổi giới hạn DLPU. [Nguồn](raw/axis-model-zoo/docs/yolov5.md).

---

# 5. Pipeline đề xuất đầu tiên: 3 model + tracker trên camera

## 5.1. Kiến trúc

```text
                     ┌──────────────────────────────────────┐
                     │       Native ACAP application        │
                     │                                      │
VDO frame ──────────►│ Traffic detector, batch=1           │
                     │ YOLOv5n INT8 → a9-dlpu-tflite        │
                     │          │                           │
                     │          ▼                           │
                     │ NMS → tracker SORT-style trên CPU    │
                     │          │                           │
                     │          ▼                           │
                     │ track_id + vehicle box + timestamp   │
                     │          │                           │
                     │          ▼                           │
                     │ Chọn track/frame đủ chất lượng       │
                     │          │                           │
                     │          ▼                           │
                     │ Crop xe từ frame độ phân giải cao    │
                     │          │                           │
                     │          ▼                           │
                     │ LPD model, batch=1 → DLPU             │
                     │          │                           │
                     │          ▼                           │
                     │ Crop biển số + kiểm tra chất lượng   │
                     │          │                           │
                     │          ▼                           │
                     │ Character detector, batch=1 → DLPU   │
                     │          │                           │
                     │          ▼                           │
                     │ Decode + sắp xếp + temporal vote     │
                     │          │                           │
                     │          ▼                           │
                     │ Plate result gắn với track_id        │
                     └──────────────────────────────────────┘
```

Ở đây “3 model” là:

1. **Traffic detector**: phát hiện xe hoặc các traffic class cần thiết.
2. **LPD**: phát hiện biển số trong crop xe.
3. **Character detector**: phát hiện các ký tự trong crop biển.

Tracker, logic chọn frame, NMS, sắp xếp ký tự và voting chạy trên CPU, theo thiết kế đề xuất.

### Vì sao chọn YOLOv5n làm baseline?

Axis có guide và benchmark **YOLOv5n/s/m trên ARTPEC-9**, cùng ví dụ ACAP tích hợp YOLOv5. Đây là bằng chứng tốt cho **họ model và đường triển khai**, nhưng **không phải bằng chứng hai model YOLOv5n custom cho biển và ký tự sẽ tự động chạy được hoặc đạt accuracy**. Cần train, export, inspect graph và chạy thử từng model. [Guide](raw/axis-model-zoo/docs/yolov5.md), [Model Zoo](raw/axis-model-zoo/README.md).

---

## 5.2. Không crop biển từ ảnh input đã resize xuống 640 nếu có thể tránh

Điểm rủi ro lớn nhất là **số pixel thực sự của biển số**.

Ví dụ minh họa:

```text
Frame gốc: 3840 px chiều ngang
Biển số trên frame gốc: 120 px chiều ngang

Nếu resize toàn frame xuống 640 px:
biển số còn khoảng 120 × 640 / 3840 = 20 px
```

Biển 20 px có thể không còn đủ chi tiết cho LPR, tùy thực tế và yêu cầu accuracy. Resize phóng to lại không khôi phục thông tin đã mất.

Do đó, cách nên thử là:

```text
frame nhỏ → traffic detector → tọa độ box
frame lớn tương ứng cùng thời điểm → crop xe / crop biển
```

Cần làm rõ:

- Mapping giữa hai resolution, crop, aspect ratio, rotation và letterbox.
- Độ lệch timestamp giữa các stream; **không mặc định hai frame lấy cùng lúc là cùng exposure**.
- Buffer ownership: frame gốc phải còn hiệu lực tới khi crop xong; nếu cần, copy crop hoặc giữ reference đúng vòng đời.
- Clamp box vào biên ảnh; xử lý box bị cắt và frame đã quá cũ.
- Chi phí RAM và copy ảnh lớn.

Ví dụ Axis CV25 sử dụng stream riêng để crop ở độ phân giải cao, nhưng **chưa chứng minh khả năng đồng bộ và performance của thiết kế này trên hai camera ARTPEC-9**. [Nguồn ví dụ](raw/acap-native-sdk-examples/object-detection-cv25/README.md).

---

## 5.3. Xử lý character detector

Một inference trên **một crop biển số** có thể trả nhiều character boxes:

```text
crop biển
  → character detector
  → [(box, class, confidence), ...]
  → NMS / lọc candidate
  → nhóm theo dòng
  → sắp xếp trái → phải trong từng dòng
  → ghép thành chuỗi
```

Các vấn đề cần thiết kế và test:

- Biển một dòng và hai dòng.
- Ký tự dễ nhầm như `0/O`, `1/I`, `8/B` tùy bộ ký tự được train.
- Ký tự nghiêng, chồng nhau, bị ốc vít/ánh sáng che.
- Box ký tự trùng hoặc thiếu; NMS theo class hay class-agnostic.
- Plate bị quay hoặc perspective mạnh: cân nhắc rectification trước detector, nhưng chi phí và độ chính xác phải đo.
- Áp dụng quy tắc format theo loại biển **như một prior**, không ép output thành biển hợp lệ khi evidence yếu.

**Khuyến nghị dữ liệu:** train và đánh giá theo đúng loại biển, quốc gia, camera, góc nhìn, ngày/đêm và điều kiện thực tế. Nếu dự kiến biển Việt Nam, cần dữ liệu biển Việt Nam và xử lý hai dòng; không nên suy từ benchmark biển nước khác.

### Temporal vote theo track

Một xe xuất hiện trong nhiều frame:

```text
track 42:
  frame A → 30A12345, score ...
  frame B → 30A12845, score ...
  frame C → 30A12345, score ...

→ chọn kết quả theo nhiều quan sát, chất lượng ảnh và confidence
```

Đây là **đề xuất thuật toán**, không phải code Axis có sẵn. Nên giữ cả confidence, số lần quan sát và trạng thái `uncertain`; voting không thể sửa lỗi nếu tất cả frame đều mờ hoặc track bị đổi ID.

---

# 6. Nhiều xe trong một frame: chạy cụ thể như thế nào?

## 6.1. Ví dụ với 4 xe

```text
Frame F có: A, B, C, D

1. Traffic detector:
   1 job, batch=1, output 4 vehicle boxes.

2. Tracker:
   gắn ID:
   A → track 17
   B → track 21
   C → track 33
   D → track 34

3. Scheduler:
   - Track 17: đã đọc biển tốt → không cần LPR lại ngay.
   - Track 21: xe quá nhỏ → chờ frame tốt hơn.
   - Track 33: đủ điều kiện → enqueue crop xe.
   - Track 34: đủ điều kiện → enqueue crop xe.

4. LPD:
   job 1: crop xe track 33
   job 2: crop xe track 34

5. Character detector:
   job 1: crop biển track 33
   job 2: crop biển track 34

6. CPU:
   decode, vote và cập nhật kết quả theo từng track_id.
```

Đây là **1 traffic job + 2 LPD jobs + 2 LPR jobs**, không phải một batch 4 cho LPD/LPR.

## 6.2. Scheduler nên lưu gì?

Ví dụ state cho mỗi track:

```text
track_id
vehicle_bbox + timestamp
first_seen / last_seen
best_vehicle_or_plate_crop
crop_quality
LPD_attempts / LPR_attempts
last_attempt_time
candidate_plate_strings + confidence
result_status: pending / accepted / uncertain / expired
```

Kèm mỗi job:

```text
camera_session_id
track_id
frame_id
capture_timestamp
crop transform / coordinate mapping
model_version
deadline
```

Khi kết quả job trả về phải kiểm tra track/session còn hợp lệ. Không gắn kết quả vào track mới chỉ vì ID nội bộ bị tái sử dụng.

## 6.3. Chính sách ưu tiên

Gợi ý:

1. Chỉ nhận track đã `confirmed`.
2. Ưu tiên xe sắp rời ROI hoặc sắp vượt line.
3. Ưu tiên ảnh có biển lớn, ít blur, ít nghiêng, không bị cắt.
4. Hạn chế số lần thử mỗi track và đặt **cooldown**.
5. Giới hạn queue và thời gian sống của job.
6. Khi quá tải, bỏ job cũ/chất lượng thấp theo policy; không để queue tăng vô hạn.
7. Ghi nhận số track không được đọc vì quá tải, không chỉ FPS.

**Lưu ý trade-off:** nếu chờ “frame tốt nhất” quá lâu, xe có thể ra khỏi hình trước khi được xử lý. Có thể chụp ứng viên sớm, cập nhật nếu có crop tốt hơn và đặt deadline theo vị trí/velocity.

## 6.4. Dùng track khi detector không chạy trên mọi frame

Traffic detector có thể chạy ở tần số thấp hơn frame camera để dành DLPU cho LPD/LPR. Tracker dự đoán vị trí giữa các lần detection, nhưng:

- Sai số box tăng khi xe tăng tốc, đổi hướng hoặc bị che;
- Không được coi box dự đoán là ground truth;
- Cần giới hạn thời gian extrapolation;
- Phải dùng timestamp thực, và đánh giá ID switch khi giảm detector FPS.

[Synthesis dựa trên phương án tracking](wiki/axis-multi-object-tracking-options.md).

---

# 7. Các phương án triển khai full on-camera

## Phương án A — Custom 3 model + custom tracker: **khuyến nghị đầu tiên**

```text
Traffic detector → SORT/ByteTrack-style
                 → LPD theo track
                 → character detector theo plate crop
```

**Ưu điểm**

- Chủ động về traffic class, LPD, bộ ký tự và logic track.
- Dễ tách lỗi: traffic recall, track, LPD, LPR.
- Có đường YOLOv5 ARTPEC-9 làm nền cho từng detector.

**Nhược điểm**

- Nhiều job và nhiều model cạnh tranh DLPU.
- Cần dataset cho cả ba tác vụ.
- Phải tự viết scheduling, crop, association và postprocessing.

**Dùng khi:** cần kiểm soát detector/tracker và muốn một pipeline minh bạch để phát triển sản phẩm.

---

## Phương án B — Axis Scene Metadata + custom LPD/LPR

```text
Axis Scene Metadata → vehicle box + track_id
                    → crop xe
                    → LPD
                    → character detector
```

**Ưu điểm**

- Không cần tự xây traffic detector + tracker ngay từ đầu.
- Nhanh đánh giá LPD/LPR và camera geometry.
- Ví dụ Axis có metadata nhiều object cùng frame, gồm `Car`, box, timestamp và `track_id`. [Nguồn](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/README.md).

**Nhược điểm/rủi ro**

- Phải xác nhận metadata producer/topic, class và firmware trên từng camera.
- Topic ví dụ là beta.
- Cần đồng bộ timestamp metadata với frame độ phân giải cao.
- Axis analytics có thể cạnh tranh DLPU với model custom; phải đo khi chạy đồng thời.
- Không điều khiển trực tiếp model traffic/tracker nội bộ.

**Dùng khi:** class và chất lượng tracking của Axis đủ cho bài toán. Đây là phương án tôi sẽ thử **song song ở giai đoạn đầu**, vì có thể giảm đáng kể công phát triển, nhưng không mặc định tiết kiệm DLPU.

---

## Phương án C — Traffic + tracking; LPD trực tiếp trên frame/ROI

```text
frame/road ROI ─► traffic detector ─► tracker
       │
       └────────► LPD toàn ROI ─► nhiều plate boxes
                                  └─► match plate với vehicle track
                                      └─► LPR theo plate
```

Ở đây một job LPD, batch 1, có thể phát hiện **nhiều biển trong cùng ảnh** nếu model được train cho tình huống đó.

**Ưu điểm**

- Có thể giảm từ `N` LPD jobs theo số xe xuống một job LPD cho ROI.
- Hữu ích khi nhiều xe cùng xuất hiện.

**Nhược điểm**

- Nếu resize cả ROI xuống kích thước input nhỏ, biển có thể mất chi tiết.
- Phải ghép biển với đúng xe/track, đặc biệt khi xe chồng lấn.
- Có thể phải dùng tiled inference, tức lại tăng số job.
- Cần train LPD cho scale và bối cảnh toàn cảnh, không chỉ crop xe.

**Dùng khi:** camera nhìn một vùng đường tương đối hẹp, biển đủ lớn trong input LPD và nhiều xe cùng lúc. Phải so sánh accuracy lẫn số job với phương án A.

---

## Phương án D — Gộp traffic detector + LPD thành một detector đa class

```text
frame → detector classes: vehicle, plate
      → track vehicle
      → match plate box với vehicle track
      → character detector theo plate crop
```

**Ưu điểm**

- Có thể bỏ một lần chạy LPD riêng.
- Đơn giản hơn về số loại model/job nếu một detector làm tốt cả hai tác vụ.

**Nhược điểm**

- Vehicle lớn và biển nhỏ có scale rất khác nhau.
- Nếu input quá nhỏ, detector có thể nhận xe nhưng bỏ sót biển.
- Cần dataset và đánh giá riêng cho cả hai class.
- Việc ghép plate–vehicle vẫn có thể nhầm khi occlusion/crossing.

**Dùng khi:** ảnh đầu vào và góc camera giúp biển đủ lớn; cần benchmark thực tế. Đây là hướng tối ưu sau khi đã có baseline A, không nên mặc định là tốt hơn.

---

## Phương án E — LPR nguyên biển thay character detector

```text
plate crop → sequence recognizer / OCR → plate string
```

**Ưu điểm kỳ vọng:** bỏ bước detect từng character box và sắp xếp.

**Rủi ro:** repository chưa có model OCR cụ thể đã chứng minh tương thích ARTPEC-9. Các graph OCR có thể có operator, layout hoặc quantization không phù hợp; phải kiểm tra graph và test thực tế. Không mặc định một model TFLite OCR bất kỳ chạy trên DLPU.

Vì anh/chị muốn **character detector**, tôi chọn A làm baseline; E là nhánh so sánh sau.

---

## So sánh nhanh

| Phương án | Traffic + tracking | LPD | LPR | Độ phù hợp để bắt đầu |
|---|---|---|---|---|
| **A** | Custom | Per-vehicle crop | Character detector | **Baseline chính**, kiểm soát tốt |
| **B** | Axis Scene Metadata | Per-vehicle crop | Character detector | **PoC song song**, nếu metadata có sẵn |
| **C** | Custom hoặc Axis | Một job cho road ROI | Per-plate | Thử khi nhiều xe và biển đủ lớn |
| **D** | Detector đa class + tracker | Gộp vào traffic detector | Per-plate | Tối ưu sau baseline |
| **E** | Tùy chọn | Tùy chọn | OCR nguyên biển | Nghiên cứu thêm; chưa có model chứng minh tương thích |

Tất cả phương án trên đều xử lý trên camera; không cần edge server.

---

# 8. Ngân sách hiệu năng: tính trước khi chọn FPS

## 8.1. Công thức gần đúng

Gọi:

- `f_T`: số job traffic detector/giây.
- `r_P`: số job LPD/giây.
- `r_R`: số job character detector/giây.
- `t_T`, `t_P`, `t_R`: thời gian DLPU trung bình cho từng job, tính bằng giây.

Ước lượng tải DLPU:

```text
U ≈ f_T × t_T + r_P × t_P + r_R × t_R + workload_DLPU_khác
```

Muốn hệ thống ổn định, tổng công việc phải thấp hơn năng lực xử lý thực tế và còn **headroom** cho biến động, queue, workload khác và latency. Đây là mô hình sơ bộ, không thay thế phép đo scheduling thực tế.

Với mỗi track:

```text
r_P ≈ số track cần LPD/giây × số lần thử LPD trung bình/track

r_R ≈ số plate crop cần nhận dạng/giây × số lần thử LPR trung bình/crop
```

### Ví dụ giả định — không phải benchmark LPD/LPR

Giả sử sau khi đo riêng trên một thiết bị:

```text
Traffic: 5 jobs/s × 32 ms = 160 ms DLPU/s
LPD:     4 jobs/s × 25 ms = 100 ms DLPU/s
LPR:     4 jobs/s × 20 ms =  80 ms DLPU/s
                              ──────
Tổng giả định              = 340 ms/s
```

Các số `25 ms` và `20 ms` ở đây **chỉ để minh họa**, không có model LPD/LPR thực tế trong repository để xác nhận. Số `32 ms` được làm tròn từ benchmark YOLOv5n Axis công bố trên Q1728, không phải số cam kết cho pipeline hay P1488-LE.

Ngay cả khi tổng ước lượng thấp, vẫn cần đo:

- Peak khi nhiều xe đến cùng lúc.
- Queue wait và latency p95/p99.
- CPU preprocess, crop, NMS, tracker, character decode.
- RAM peak khi giữ nhiều frame/crop.
- Tải AOA/analytics khác, encoding và stream video.

### Benchmark có thật để định hướng

Axis Model Zoo báo cáo trên **ARTPEC-9 Q1728**, AXIS OS 12.11.72:

- YOLOv5n: **31,85 ms**
- YOLOv5s: **35,00 ms**
- YOLOv5m: **42,70 ms**

Đây là benchmark vendor của các model trong Model Zoo, **không phải model LPD/LPR custom** và không bao gồm toàn bộ pipeline. [Nguồn](raw/axis-model-zoo/README.md#object-detection).

---

# 9. Kế hoạch PoC thực tế

## Giai đoạn 0 — Chốt bài toán và dữ liệu

Trước khi train, cần xác định:

1. Mỗi camera nhìn **bao nhiêu làn**, khoảng cách và hướng xe?
2. Xe đứng yên hay chạy nhanh? Tốc độ dự kiến?
3. Loại biển, quốc gia, biển một/hai dòng, xe máy hay ô tô?
4. Mục tiêu: **tỉ lệ xe có biển đọc đúng**, latency tối đa, số xe/phút và peak đồng thời?
5. Ngày/đêm, mưa, ngược sáng, IR, biển phản quang?
6. Quy định lưu trữ biển số và ảnh: lưu bao lâu, ai được truy cập?

Điểm quyết định sớm nhất không phải model: **thu clip từ đúng vị trí lắp camera và đo kích thước biển bằng pixel** trên frame thực tế, cả ban ngày lẫn ban đêm.

## Giai đoạn 1 — Dựng baseline trên Q1728-LE

1. Xác nhận SoC/OS và `a9-dlpu-tflite`.
2. Build [YOLOv5 example](raw/acap-native-sdk-examples/object-detection-yolov5/) cho ARTPEC-9.
3. Chạy traffic detector mẫu, đo FPS và latency.
4. Gắn tracker SORT-style, xuất track ID và timestamp.
5. Kiểm tra crop xe từ frame độ phân giải cao và mapping tọa độ.
6. Đồng thời thử [Scene Metadata consumer](raw/acap-native-sdk-examples/message-broker/consume-scene-metadata/) để so với traffic + tracker custom.

**Gate:** box, timestamp và crop phải đúng trước khi đầu tư LPR.

## Giai đoạn 2 — LPD

1. Chuẩn bị dataset **vehicle crop → plate bounding box**, bao gồm các negative cases.
2. Train YOLOv5n custom theo quy trình Axis.
3. Export INT8 batch 1; kiểm tra input/output, operator và calibration.
4. Test `larod-client` với `a9-dlpu-tflite`.
5. Tích hợp LPD và đo plate recall theo:
   - kích thước biển;
   - góc;
   - ngày/đêm;
   - số xe và occlusion.
6. Test với nhiều crop xe trong một frame bằng các job batch 1.

**Gate:** model phải load/chạy trên DLPU và LPD recall đạt mục tiêu ở khoảng cách thực tế.

## Giai đoạn 3 — Character detector

1. Label ký tự theo bộ ký tự và các layout biển mục tiêu.
2. Train model, export INT8 batch 1 và test DLPU.
3. Viết decoder cho biển một/hai dòng.
4. Đánh giá:
   - character precision/recall;
   - **exact plate string accuracy**;
   - lỗi theo nhóm ký tự;
   - chất lượng sau quantization.
5. Thêm voting theo track, không ép chấp nhận nếu confidence thấp.

**Gate:** exact-match trên dữ liệu camera thật đạt yêu cầu, không chỉ mAP character.

## Giai đoạn 4 — Scheduler và stress test

1. Thêm ROI, quality gate, cooldown và queue có giới hạn.
2. Test nhiều xe vào đồng thời.
3. Đo throughput trung bình lẫn burst.
4. So sánh A/B/C/D trên cùng clip nếu có thời gian.
5. Chạy tải dài, restart app/camera và kiểm tra memory peak.
6. Lặp lại trên P1488-LE, không dùng số Q1728-LE làm đại diện.

### Metrics nên báo cáo

| Nhóm | Chỉ số |
|---|---|
| Traffic | Vehicle recall/precision; kích thước xe và mật độ |
| Tracking | ID switches, fragmentation, tỷ lệ track usable |
| LPD | Plate recall theo track và theo kích thước/góc |
| LPR | Character accuracy, **exact plate accuracy**, tỷ lệ `uncertain` |
| End-to-end | Tỷ lệ xe đi qua có đúng biển gắn đúng track; false accept |
| Hiệu năng | Jobs/s theo model, queue wait, latency p50/p95/p99, CPU, DLPU, peak RAM |
| Quá tải | Số track bị bỏ, số crop hết hạn, queue overflow |
| Vận hành | Ngày/đêm, nhiều stream, analytics khác, chạy dài, restart |

Đánh giá end-to-end nên tính **trên tổng số xe đủ điều kiện**, không chỉ trên những crop đã được LPR; nếu không, pipeline có thể có OCR accuracy cao nhưng bỏ sót nhiều xe.

---

# 10. Các rủi ro có thể làm PoC thất bại

1. **Biển quá nhỏ hoặc motion blur:** model tốt không phục hồi được chi tiết chưa được ghi lại.
2. **Đồng bộ frame–metadata sai:** đọc biển đúng nhưng gắn nhầm xe.
3. **Model custom không tương thích DLPU:** YOLOv5 family có ví dụ không đồng nghĩa mọi custom graph/export đều hợp lệ.
4. **DLPU overload theo burst:** trung bình đủ nhanh nhưng queue bị dồn khi nhiều xe đến đồng thời.
5. **Traffic track đổi ID:** vote hoặc kết quả biển bị gắn nhầm track.
6. **P1488-LE thiếu RAM thực dụng:** đặc biệt nếu giữ frame lớn, nhiều model và analytics khác.
7. **Sai preprocessing hoặc quantization:** resize, màu, normalization, output dtype, scale/zero point và parser phải đúng với từng model.
8. **Privacy:** biển số và crop xe có thể là dữ liệu nhạy cảm theo bối cảnh; cần hạn chế log, phân quyền, mã hóa và retention theo yêu cầu áp dụng.
9. **License:** Model Zoo ghi các model YOLOv5/YOLOv8 được liệt kê là **AGPL-3.0-only**; cần rà soát model, patch, training code và tracker trước thương mại hóa. [Nguồn](raw/axis-model-zoo/README.md#object-detection).

---

## Khuyến nghị cuối cùng

Tôi sẽ triển khai theo thứ tự:

1. **Thu clip và đo pixel biển số** từ hai vị trí camera dự kiến.
2. **PoC B:** thử Axis Scene Metadata + crop để biết có thể tận dụng track sẵn không.
3. **PoC A:** custom YOLOv5n traffic + SORT-style + LPD YOLOv5n + character detector, tất cả model chạy **batch 1**.
4. Dùng **scheduler theo track**, chỉ chạy LPD/LPR trên frame tốt, thay vì mỗi xe ở mọi frame.
5. Sau khi có baseline, thử **C hoặc D** để giảm số job nếu biển vẫn đủ lớn trong input.
6. Đo riêng trên từng camera và đưa ra quyết định dựa trên **exact plate accuracy + tỷ lệ xe được đọc đúng + latency khi burst**, không chỉ FPS detector.

**Giới hạn nghiên cứu:** chưa tìm được model LPD/LPR cụ thể trong nguồn cục bộ để xác nhận batch hay benchmark; chưa truy cập tài liệu live hoặc datasheet chính hãng của hai camera trong lần này; chưa chạy model/camera. Structural check của wiki đã chạy thành công: **99 concept, 1 index**; kiểm tra này chỉ xác nhận cấu trúc, không xác thực hiệu năng. Tôi để phân tích này ở dạng trả lời tạm thời, không thay đổi wiki hoặc log.