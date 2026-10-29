# Triển khai YOLO trên AXIS Q1728-LE và P1488-LE

## 1. Kết luận nhanh

**Phương án có bằng chứng tốt nhất trong tài liệu hiện có là:**

```text
YOLOv5n/s/m
  → train hoặc fine-tune bằng YOLOv5 có áp dụng patch ARTPEC-9 của Axis
  → export TFLite INT8
  → kiểm tra bằng Larod trên a9-dlpu-tflite
  → tích hợp vào native ACAP application
  → lấy hình qua VDO, inference qua Larod, xử lý output/NMS trên application.
```

Axis có sẵn model, checkpoint, hướng dẫn train/export và ví dụ ACAP cho **YOLOv5 trên ARTPEC-9**. Đối với **YOLOv8, YOLO11 và các phiên bản khác**, dữ liệu trong `raw/` chưa đủ để khẳng định tương thích với ARTPEC-9; cần kiểm tra graph và thử trên camera, không thể suy ra từ việc export thành công TFLite. [Nguồn: hướng dẫn YOLOv5](raw/axis-model-zoo/docs/yolov5.md), [bảng Model Zoo](raw/axis-model-zoo/README.md).

**Giới hạn quan trọng về hai camera:** Ghi chú phần cứng trong wiki nói cả Q1728-LE và P1488-LE dùng ARTPEC-9, RAM lần lượt 4 GB và 2 GB. Tuy nhiên, thông tin *gắn SoC và RAM với đúng hai mã camera này* hiện đến từ một nguồn nghiên cứu thứ cấp; datasheet/trang sản phẩm Axis không có trong `raw/` để đối chiếu. Vì vậy, trước khi mua hoặc triển khai, cần xác nhận trực tiếp bằng datasheet hoặc thông tin SoC trên camera. Phần còn lại của câu trả lời giả định hai camera thực sự dùng **ARTPEC-9**. [Chi tiết và giới hạn nguồn](wiki/axis-artpec-9-camera-selection.md).

Tôi đã kiểm tra cả wiki lẫn các nguồn và code liên quan trong `raw/`; **chưa chạy model, build ứng dụng hoặc đo trên camera thực tế**.

---

## 2. Camera, SDK và runtime: mỗi thành phần làm gì?

Nếu xác nhận cả hai máy dùng ARTPEC-9, chúng đi theo cùng một đường triển khai model:

| Thành phần | Vai trò |
|---|---|
| **ACAP Native SDK** | Build ứng dụng native cho camera và đóng gói `.eap`. |
| **VDO / Video Capture API** | Lấy frame từ camera. |
| **Larod / Machine Learning API** | Nạp model, tạo tensor/job và gọi inference. |
| **`a9-dlpu-tflite`** | Larod device/channel để chạy model TFLite tương thích trên DLPU ARTPEC-9. |
| **`cpu-tflite`** | Backend TFLite trên CPU; không được nhầm với chạy trên DLPU. |
| **Bounding Box API** | Vẽ bounding box lên video trong ví dụ của Axis. |
| **AXParameter** | Lưu/đọc threshold và các tham số application. |

Pipeline tham khảo:

```text
Camera frame
   ↓ VDO
Resize / crop / chuyển pixel format
   ↓
Tensor input của model
   ↓ Larod → a9-dlpu-tflite
Tensor output đã quantize
   ↓ CPU/application: dequantize, lọc, NMS, map labels
Bounding box / event / logic nghiệp vụ
```

**SDK không đảm bảo mọi model có tên “YOLO” sẽ chạy được.** Tính tương thích phụ thuộc vào **graph sau export**, operator và các giới hạn của operator, quantization, kích thước tensor, bộ nhớ và AXIS OS trên thiết bị. [Nguồn: ví dụ Larod](wiki/acap-example-larod-object-detection.md), [giới hạn ARTPEC-9](wiki/axis-artpec-9-operator-support.md).

### Khác biệt đáng chú ý giữa hai camera

Nếu RAM 4 GB và 2 GB được xác nhận, Q1728-LE có thêm dư địa cho model, frame buffer và ứng dụng. Nhưng **không được suy ra 4 GB RAM thì inference nhanh gấp đôi**.

Axis cho biết các model YOLOv5n/s/m ARTPEC-9 trong guide được test trên **Q1728 với 4 GB RAM**, và cảnh báo thiết bị ít bộ nhớ hơn có thể gặp vấn đề với model lớn hơn. Do đó, với P1488-LE, nên bắt đầu từ `yolov5n`, theo dõi RAM rồi tăng dần. Đây là **khuyến nghị suy luận**, không phải bằng chứng P1488-LE không chạy được `s` hoặc `m`. [Nguồn: guide YOLOv5, đoạn đầu](raw/axis-model-zoo/docs/yolov5.md).

---

## 3. Những model nào có bằng chứng hỗ trợ?

### 3.1. YOLO trên ARTPEC-9

| Model | Bằng chứng trong nguồn hiện có | Đánh giá |
|---|---|---|
| **YOLOv5n** | Có `.tflite`, checkpoint, benchmark ARTPEC-9 và ví dụ ACAP mặc định. | Điểm bắt đầu tốt nhất. |
| **YOLOv5s** | Có `.tflite`, checkpoint và benchmark ARTPEC-9. | Nên thử khi `n` chưa đủ accuracy. |
| **YOLOv5m** | Có `.tflite`, checkpoint và benchmark ARTPEC-9. | Có thể thử, nhưng cần đo RAM và latency trên đúng thiết bị. |
| **YOLOv5 lớn hơn** | Guide khuyến nghị n/s/m để tránh vượt bộ nhớ. | Chưa có bảo đảm; cần PoC riêng. |
| **YOLOv8** | Model Zoo có `YOLOv8n_det` cho **CV75**, không phải ARTPEC-9. | Chưa đủ bằng chứng cho ARTPEC-9. |
| **YOLO11 và các biến thể khác** | Không thấy benchmark/guide ARTPEC-9 tương ứng trong các nguồn Axis đã kiểm tra. | Chưa xác nhận; không đồng nghĩa chắc chắn không chạy được. |

Các kết luận này áp dụng cho **snapshot nguồn trong repository**, không phải danh sách hỗ trợ toàn diện hay khẳng định về tài liệu Axis mới nhất trên Internet. [Nguồn trực tiếp: Model Zoo](raw/axis-model-zoo/README.md#object-detection), [guide train](raw/axis-model-zoo/docs/yolov5.md).

Ngoài YOLO, Model Zoo có **SSD MobileNet V2** và **SSDLite MobileDet** với số đo ARTPEC-9. Chúng hữu ích để dựng pipeline hoặc so sánh speed/accuracy với YOLO. [Nguồn](wiki/axis-model-zoo-benchmark-results.md).

### 3.2. Số benchmark tham khảo, không phải FPS thực tế của hai camera

Axis Model Zoo công bố, trên **ARTPEC-9 Q1728**, AXIS OS **12.11.72**:

| Model | Inference trung bình | mAP được README ghi |
|---|---:|---:|
| YOLOv5n | 31,85 ms | 23,3% |
| YOLOv5s | 35,00 ms | 32,2% |
| YOLOv5m | 42,70 ms | 38,1% |
| SSD MobileNet V2 | 10,48 ms | 25,6% |
| SSDLite MobileDet | 21,48 ms | 32,9% |

**Không lấy các số này làm FPS cam kết cho Q1728-LE hoặc P1488-LE.** Đây là thời gian job inference tham khảo, không bao gồm đầy đủ capture, preprocessing, NMS và nghiệp vụ. Nguồn cũng không định nghĩa rõ cách tính mAP trong bảng; accuracy của YOLO được dẫn đến bước evaluate trong guide nhưng dataset không được pin rõ. [Phân tích phương pháp và giới hạn](wiki/axis-model-zoo-benchmark-results.md).

---

## 4. Quy trình chi tiết: YOLOv5 custom → ARTPEC-9

Dưới đây là quy trình Axis tài liệu hóa; lệnh chưa được tôi thực thi.

### Bước 0 — Xác nhận thiết bị và firmware

Trước khi train:

1. Xác nhận camera thực sự là **ARTPEC-9**, có DLPU và architecture phù hợp.
2. Ghi lại chính xác **model camera, AXIS OS, ACAP SDK, Larod**.
3. Kiểm tra tài nguyên đang dùng: AOA/analytics khác, video stream, RAM.
4. Chọn SDK/manifest tương thích với AXIS OS thực tế.

Không nên lấy số benchmark của một model Q1728 làm chứng nhận cho camera khác. [Nguồn: tương thích SDK](wiki/acap-chip-architecture-and-sdk-compatibility.md), [camera selection](wiki/axis-artpec-9-camera-selection.md).

### Bước 1 — Clone đúng phiên bản YOLOv5 và áp dụng patch ARTPEC-9

Axis yêu cầu pin upstream commit cụ thể và áp dụng **đúng patch cho SoC**:

```bash
git clone https://github.com/ultralytics/yolov5
cd yolov5

git checkout 95ebf68f92196975e53ebc7e971d0130432ad107

curl -L \
  https://acap-ml-models.s3.amazonaws.com/yolov5/yolov5_artpec9.patch \
  | git apply

pip install -r requirements.txt
```

**Lưu ý:** Patch nằm trên S3 và chưa được tải/đọc trong lần kiểm tra này. Vì vậy, có thể xác nhận Axis yêu cầu áp dụng patch trước khi train, nhưng **không kết luận được patch thay chính xác layer hoặc phần export nào**. Khi triển khai thực tế nên tải patch thành file, lưu checksum và kiểm tra nội dung trước khi áp dụng, thay vì phụ thuộc mã từ xa không được pin checksum.

Guide không pin đầy đủ Python/PyTorch/CUDA, do đó nên cố định environment và lưu lại version để tái lập. [Nguồn: `docs/yolov5.md`, bước 1](raw/axis-model-zoo/docs/yolov5.md).

### Bước 2 — Chuẩn bị và train dataset riêng

Guide đưa ví dụ train từ đầu trên COCO:

```bash
python3 train.py \
  --name axis-train \
  --data coco.yaml \
  --epochs 300 \
  --weights '' \
  --cfg yolov5n.yaml \
  --batch-size 128
```

Để làm **custom detector**:

1. Chuẩn bị dữ liệu và annotation YOLO cho các class thực tế.
2. Tạo dataset YAML cho train/validation/test, với đúng thứ tự class.
3. Thay `coco.yaml` bằng YAML của bạn.
4. Chọn `yolov5n`, `s` hoặc `m` và batch size theo GPU/máy train.
5. Nếu fine-tune từ checkpoint, thay giá trị `--weights ''` bằng checkpoint tương ứng, thay vì thêm một `--weights` thứ hai.
6. Lưu checkpoint, commit YOLOv5, patch, cấu hình train và danh sách class.

Axis cung cấp checkpoint n/s/m trong Model Zoo. Vì patch ARTPEC-9 có thể thay đổi cách model được chuẩn bị, nên ưu tiên checkpoint và quy trình của Axis thay vì mặc định một checkpoint YOLO bất kỳ sẽ tương thích. [Nguồn: guide bước 2 và 7](raw/axis-model-zoo/docs/yolov5.md).

### Bước 3 — Export TFLite INT8 cho ARTPEC-9

Theo lệnh Axis:

```bash
python3 export.py \
  --weights runs/train/axis-train/weights/best.pt \
  --include tflite \
  --int8
```

Guide ghi output dự kiến:

```text
runs/train/axis-train/weights/best-int8.tflite
```

**Không thêm `--per-tensor` chỉ vì thấy trong hướng dẫn ARTPEC-8.** Trong guide này:

- ARTPEC-8: `--int8 --per-tensor`
- ARTPEC-9: `--int8`

Điều đó **không có nghĩa mọi kiểu per-channel đều được ARTPEC-9 hỗ trợ**: vendor chỉ nói per-channel được hỗ trợ cho weight/bias của một tập operator giới hạn. [Nguồn: guide export](raw/axis-model-zoo/docs/yolov5.md), [optimization tips](raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md).

### Bước 4 — Validate accuracy trước và sau quantization

Axis đưa lệnh:

```bash
python3 val.py \
  --weights runs/train/axis-train/weights/best-int8.tflite \
  --data path/to/custom-dataset.yaml
```

Nên so sánh ít nhất:

- Checkpoint float trước export.
- TFLite INT8 sau export.
- Kết quả thực tế trên camera, dùng cùng preprocessing/postprocessing dự kiến.
- Precision/recall, mAP và kết quả **theo từng class**, đặc biệt với object nhỏ, ban đêm, ngược sáng và góc camera thực tế.

Đây là checklist kỹ thuật đề xuất; nguồn không cung cấp phép đo custom dataset của bạn. Vendor FAQ cũng ghi giảm accuracy sau quantization là điều có thể xảy ra. [Guide](raw/axis-model-zoo/docs/yolov5.md), [FAQ](wiki/acap-developer-faq.md).

### Bước 5 — Kiểm tra model trên DLPU

Sau khi đưa file lên camera ARTPEC-9, vendor đưa ví dụ:

```bash
larod-client \
  -g /path/to/best-int8.tflite \
  -c a9-dlpu-tflite \
  -i ""
```

Lệnh này là **test nạp/chạy model**, không thay thế việc kiểm tra accuracy trên ảnh thật hoặc ứng dụng end-to-end. Tài liệu cục bộ không giải thích chi tiết ý nghĩa `-i ""`; không nên coi đây là kiểm thử dữ liệu camera thực. [Nguồn trực tiếp: model conversion](raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md).

Axis cũng có `model_performance_tester.py` để SSH lên camera và lấy mean inference time; xem [hướng dẫn và giới hạn benchmark](wiki/axis-model-zoo-speed-benchmark-pipeline.md). Tránh đưa password thực vào terminal history hoặc log khi sử dụng công cụ.

### Bước 6 — Build ACAP cho ARTPEC-9

Từ thư mục `object-detection-yolov5` trong `acap-native-sdk-examples`:

```bash
docker build \
  --platform=linux/amd64 \
  --tag object_detection_yolov5:1.0 \
  --build-arg ARCH=aarch64 \
  --build-arg CHIP=artpec9 \
  .
```

Copy build artifacts:

```bash
docker cp \
  "$(docker create --platform=linux/amd64 object_detection_yolov5:1.0)":/opt/app \
  ./build
```

Artifact theo README có dạng:

```text
object_detection_yolov5_artpec9_1_0_0_aarch64.eap
```

**Cẩn thận:** Dockerfile snapshot hiện tại mặc định `CHIP=artpec8`, nên cần truyền `CHIP=artpec9` rõ ràng. Dockerfile mặc định tải YOLOv5n và COCO labels từ xa; muốn dùng model riêng thì sửa Dockerfile để `COPY` model/labels của bạn vào build context hoặc tải từ nguồn được kiểm soát. Script `parameter_finder.py` sẽ đọc model và sinh `model_params.h` trước khi build ACAP. [README ví dụ](raw/acap-native-sdk-examples/object-detection-yolov5/README.md#build-the-application), [Dockerfile thực tế](raw/acap-native-sdk-examples/object-detection-yolov5/Dockerfile).

Cài qua trang Apps của camera, kiểm tra log và stream. **Signing phụ thuộc AXIS OS:** tài liệu Axis nói OS 12 có thể cho phép unsigned app khi phát triển nếu thay đổi policy; OS 13 bỏ tùy chọn này, nên cần chuẩn bị quy trình ký app. Không nên dựa vào bước “Allow unsigned apps” trong README như quy trình production chung. [Nguồn signing](wiki/acap-application-signing.md).

---

## 5. Quantization: cụ thể cần kiểm tra gì?

### 5.1. Yêu cầu của ARTPEC-9

Theo Axis:

- Model cần được quantize **INT8/UINT8**; operator nhận kiểu khác không được hỗ trợ trên DLPU.
- Tensor tối đa **4 chiều**.
- **Batch size > 1 không hỗ trợ**.
- Layout được hỗ trợ: **NHWC**.
- Per-channel quantization chỉ hỗ trợ với **weight và bias của một tập operator giới hạn**.
- Một file TFLite hợp lệ không tự động là file hợp lệ cho DLPU.

[Nguồn trực tiếp: ARTPEC-9 optimization tips](raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md).

### 5.2. Calibration cho custom data

Lệnh YOLOv5 của Axis dùng `--int8`, nhưng **guide không mô tả dataset calibration, số ảnh, preprocessing hoặc tham số calibration**. Tương tự, các guide PyTorch-to-TFLite và TensorFlow-to-TFLite được dẫn link nhưng không có trong `raw/` hiện tại.

Do đó:

- **Không thể khẳng định** lệnh export ở trên tự động sử dụng dataset custom của bạn để calibration.
- Trước khi chốt pipeline, cần kiểm tra **`export.py` sau patch** và cách phiên bản đó chọn representative/calibration data.
- Về thực hành, nên chọn dữ liệu đại diện cho phân bố camera thực tế: ánh sáng, ngày/đêm, khoảng cách, kích thước object, góc nhìn; sau đó đo accuracy sau quantization. Đây là **khuyến nghị kỹ thuật**, không phải chi tiết mà guide Axis hiện có đã quy định.
- Nếu accuracy giảm nhiều, cần xem lại calibration, preprocessing và cân nhắc quantization-aware training; nguồn hiện tại **không có quy trình QAT YOLOv5 ARTPEC-9 đã xác minh**.

### 5.3. Output quantization của ví dụ YOLOv5

Ví dụ ACAP của Axis giả định output là `uint8` và lấy `scale`, `zero_point` từ model ở build time. Công thức:

```c
real_value = (quantized_value - zero_point) * scale;
```

Đây là hợp đồng của **model và parser trong ví dụ**, không phải bảo đảm mọi model INT8/UINT8 đều có cùng output layout hoặc cùng kiểu output. Nếu model mới xuất `int8`, nhiều tensor, hoặc output layout khác thì phải sửa parser. [Nguồn: README ví dụ, “Output shape” và “Dequantization”](raw/acap-native-sdk-examples/object-detection-yolov5/README.md#explanation-of-yolov5-output-parsing).

---

## 6. ARTPEC-9 hỗ trợ layer/operator nào?

Axis liệt kê **23 operator**, mỗi operator có điều kiện riêng. Danh sách này là cho **DLPU ARTPEC-9**, không phải cam kết rằng layer cùng tên trong PyTorch sẽ tự chuyển thành đúng graph TFLite tương thích.

| Operator | Giới hạn quan trọng |
|---|---|
| `Add` | Element-wise. |
| `AveragePool` | Hỗ trợ 3×3, stride 1, `SAME`; dạng mean có giới hạn input/pool 7 hoặc 8. |
| `Concat` | Khi ghép theo channel, channel của **mọi input** phải chia hết cho 16; có giới hạn ratio scale. |
| `Constant` | Bảng không ghi giới hạn. |
| `Conv2D` | Kernel mỗi chiều thuộc `{1,2,3,5,7,9}`; stride 1 hoặc 2 và hai chiều bằng nhau; kernel >7 chỉ stride 1; `SAME`/`VALID`; giới hạn quantization scale. |
| `DepthToSpace` | Block size 2; depth chia hết cho bình phương block size. |
| `DepthwiseConvolution2D` | Kernel/stride tương tự Conv; channel multiplier phải là 1; có giới hạn scale. |
| `FullyConnected` | Weight `HWIO` với H=W=1; có giới hạn scale. |
| `LeakyReLU` | `0 < alpha < 1`. |
| `MaxPool` | Chỉ một số tổ hợp kernel, stride, padding và kích thước input; xem bảng gốc. |
| `MeanXY` | Chỉ reduction H×W với feature map 7×7 hoặc 8×8. |
| `Mul` | Chỉ một số trường hợp nhân với constant tensor/scalar; không mặc định hỗ trợ mọi phép nhân tensor. |
| `Pad` | Chỉ zero-pad H/W, tối đa 7 mỗi phía; input/output quantization phải giống nhau. |
| `Reinterpret quantization` | Bảng không ghi giới hạn. |
| `ReLU` | Lower bound nhỏ hơn upper bound. Axis khuyến nghị ưu tiên `ReLU6` khi có thể. |
| `Requantize` | Output scale không được nhỏ hơn input scale chia 128. |
| `Reshape` | Bảng không ghi giới hạn. |
| `Resize` | Kích thước sau resize phải là `2n` hoặc `2n−1`; một số cấu hình bilinear có thể giảm accuracy. |
| `Sigmoid` | Output scale cố định `1/256`; zero point là giá trị nhỏ nhất của kiểu quantized. |
| `Split` | Nếu split theo channel, channel của mỗi output phải chia hết cho 16. |
| `Tanh` | Output scale `1/128`; zero point ở giữa miền giá trị. |
| `Transpose` | Chỉ cho phép hoán vị height, width, channel. |
| `TransposeConvolution2D` | Kernel như Conv; **chỉ stride 2**; có giới hạn scale. |

Với Conv2D, DepthwiseConv, FullyConnected và TransposeConv, nguồn còn yêu cầu tỉ lệ `input_scale × weight_scale / output_scale` trong khoảng được ghi là **0–65536**.

**Quan trọng với YOLO:** `SiLU/Swish` không xuất hiện trong bảng operator này; điều đó chưa chứng minh mọi graph YOLO có SiLU đều thất bại, vì graph sau conversion/patch có thể khác. Nhưng cũng **không được mặc định SiLU chạy được**. Cần kiểm tra graph thực tế và test backend. Tương tự, nên kiểm tra các nhánh `Concat`, `Resize`, `Mul`, output head và scale sau quantization. Tài liệu cũng khuyến nghị channel chia hết cho 16 để tránh lãng phí compute; đây không phải quy tắc “mọi tensor đều bắt buộc chia hết cho 16” — `Concat`/`Split` theo channel mới có các điều kiện bắt buộc cụ thể ở trên.

Nguồn đầy đủ: [bảng Supported Ops gốc](raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md) và [phân tích trong wiki](wiki/axis-artpec-9-operator-support.md). Bảng có thể thay đổi theo version; cần đối chiếu tài liệu hiện hành trước production.

---

## 7. Custom model: những phần phải sửa ngoài việc thay `.tflite`

### 7.1. Model cùng họ YOLOv5 của Axis

Ví dụ `object-detection-yolov5` lấy tự động từ model:

- Input height/width.
- Output quantization scale và zero point.
- Số class `C`.
- Số detection `N`.

Nhưng script **giả định** input NHWC và output đầu tiên có shape tương đương:

```text
[1, N, 5 + C]
```

Parser giả định mỗi detection có:

```text
[x_center, y_center, width, height, object_likelihood, class_1, ..., class_C]
```

Một model YOLOv5 custom có cùng hợp đồng này là hướng thay thế dễ nhất. Cần:

1. Đưa đúng model và `labels.txt` vào Dockerfile.
2. Đảm bảo thứ tự label trùng class index khi train.
3. Kiểm tra input/output dtype, shape, scale, zero point.
4. Kiểm tra cách scale tọa độ, crop và map bounding box lên stream.
5. Chỉnh threshold và xác nhận accuracy trên ảnh thực tế.

[Nguồn: `parameter_finder.py`](raw/acap-native-sdk-examples/object-detection-yolov5/app/parameter_finder.py), [README ví dụ](raw/acap-native-sdk-examples/object-detection-yolov5/README.md).

### 7.2. YOLOv8/YOLO11 hoặc model custom có head khác

Ngay cả khi model nạp và inference được trên DLPU, **không thể mặc định dùng nguyên parser YOLOv5**. Cần tự xác minh:

- Có bao nhiêu output tensor, shape và thứ tự chiều.
- Có objectness riêng hay không, cách tính score theo class.
- Bounding box là `xywh`, `xyxy`, normalized hay pixel.
- Output có sẵn NMS hay chưa.
- `int8` hay `uint8`; scale/zero-point theo tensor nào.
- Preprocessing: RGB/BGR, normalization, resize/crop/letterbox.
- Mapping từ tọa độ model về hình camera.

Từ code đã đọc, đây là **điểm tích hợp cần thiết**, không phải tuyên bố rằng một phiên bản YOLO cụ thể chắc chắn dùng một layout nào. Nếu graph chứa operator ngoài khả năng ARTPEC-9, có thể phải đổi architecture/export/head hoặc xử lý một phần ngoài graph — nhưng cần kiểm tra cơ chế thực tế; nguồn đã đọc **không bảo đảm tự động CPU fallback** cho mọi operator không hỗ trợ.

### 7.3. Đừng copy nguyên postprocessing demo vào production mà không kiểm tra

Theo code và README:

- Ví dụ lọc theo **object likelihood**, sau đó dùng NMS so sánh cặp box và chọn class.
- Threshold mặc định: confidence **25%**, IoU **5%**; muốn áp dụng thay đổi qua AXParameter thì restart app.
- NMS trong code là so sánh cặp, có thể tốn CPU khi nhiều detection.
- Luồng ví dụ chọn stream theo aspect ratio camera rồi **crop** cho model; nếu lúc train/validation dùng letterbox khác, kết quả và tọa độ có thể lệch.
- Code demo có các giới hạn/defect đã được ghi nhận, trong đó label parser có thể làm lệch index nếu bỏ các dòng `n/a`.

Vì vậy cần đánh giá riêng threshold, class-aware/class-agnostic NMS, latency CPU, alignment của labels và preprocessing. [Nguồn code](raw/acap-native-sdk-examples/object-detection-yolov5/app/object_detection_yolov5.c), [phân tích ví dụ và defect](wiki/acap-example-larod-object-detection.md).

---

## 8. Checklist PoC đề xuất

1. **Xác thực từng camera:** SoC, RAM, AXIS OS, DLPU và quyền cài ACAP.
2. **Baseline:** chạy model YOLOv5n ARTPEC-9 do Axis cung cấp, build `CHIP=artpec9`.
3. **Test riêng DLPU:** `larod-client` với `a9-dlpu-tflite`; lưu log load/inference.
4. **Test end-to-end:** đo thời gian capture, preprocess, inference, postprocess và FPS thực tế.
5. **Train custom:** bắt đầu với cùng YOLOv5 + patch; kiểm tra dataset và labels.
6. **Quantization:** kiểm tra calibration thực tế, so sánh accuracy float và INT8.
7. **Thử n → s → m:** đo RAM, latency, nhiệt/độ ổn định và chất lượng trên **từng camera**, đặc biệt máy có RAM thấp hơn.
8. **Test đồng thời workload:** nếu chạy AOA/ACAP khác, DLPU được chia sẻ; đo lại thay vì cộng FPS lý thuyết. [FAQ Axis](wiki/acap-developer-faq.md).
9. **Production:** kiểm tra signing theo OS, version SDK, operator hiện hành, license, logging và khả năng khôi phục khi model load lỗi.
10. **License:** Axis ghi patch YOLOv5 và các model YOLOv5/YOLOv8 trong bảng liên quan là **AGPL-3.0-only**; cần review nghĩa vụ phân phối/sử dụng trước khi thương mại hóa. Tôi chưa tải hoặc phân tích toàn bộ license text. [Nguồn](raw/axis-model-zoo/docs/yolov5.md).

## Giới hạn kiểm tra và nguồn

- Wiki hiện **populated**; structural check chạy thành công: **98 concepts, 1 index**. Check này không chứng minh tính đúng của model hay benchmark.
- Tôi đã đọc trực tiếp trong `raw/`: guide YOLOv5, Model Zoo, ARTPEC-9 conversion/optimization/supported operators, Dockerfile, manifest, README, script đọc metadata và phần code postprocessing của ví dụ ACAP. Đồng thời tìm các tham chiếu YOLO phiên bản mới và calibration trong `raw/`.
- **Chưa có datasheet Axis cục bộ** để xác thực SoC/RAM cho chính hai camera; chưa tải patch S3, upstream YOLOv5, trang conversion ngoài hoặc tài liệu live mới nhất.
- **Chưa build, export, quantize hay chạy camera**; các số của Axis là kết quả vendor công bố, không phải số tôi đo.
- Tôi để kết quả này là **phân tích tạm thời trong câu trả lời**; không thay đổi wiki hoặc log.