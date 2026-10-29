# Triển khai image classification trên AXIS Q1728-LE / P1488-LE

## Kết luận ngắn

Nếu hai camera thực tế đúng là **ARTPEC-9 + DLPU**, cả hai có thể đi theo cùng một hướng triển khai:

```text
Dataset ảnh → train/fine-tune classifier
            → full-integer quantization
            → export TensorFlow Lite (.tflite)
            → kiểm tra trên a9-dlpu-tflite
            → tích hợp VDO + Larod vào ACAP application
            → build .eap cho aarch64 → cài và đo trên camera
```

**Điểm cần lưu ý nhất:**

1. **Có một classifier được Axis công bố benchmark trên ARTPEC-9:** MobileNetV2 `mobilenet_v2_1.0_224_quant.tflite`. Đây là điểm bắt đầu tốt hơn YOLO nếu bài toán của bạn thực sự là *image classification*.
2. Axis không đưa ra danh sách “mọi model được SDK hỗ trợ”. Khả năng chạy phụ thuộc vào **graph TFLite cụ thể, quantization, operator, tensor shape và AXIS OS**, chứ không chỉ tên kiến trúc.
3. Model cho ARTPEC-9 được export thành **INT8/UINT8 TFLite**, rồi nạp qua Larod `a9-dlpu-tflite`; tài liệu Axis không có bước Edge TPU Compiler hay Ambarella CNNGen cho nhánh này.
4. Ví dụ native phù hợp nhất để bắt đầu là `[vdo-larod](raw/acap-native-sdk-examples/vdo-larod/README.md)`: nó đã lấy frame camera, preprocess và chạy **classification**. Tuy nhiên code mặc định chỉ xử lý model person/car của ví dụ; thay file model không đủ để hỗ trợ classifier tùy ý.
5. **Thông tin Q1728-LE và P1488-LE cùng ARTPEC-9 trong dữ liệu hiện tại vẫn đến từ bản research thứ cấp**, không có datasheet chính hãng lưu trong `raw/` để tôi đối chiếu trực tiếp. Cần xác nhận SoC, RAM và AXIS OS trên đúng SKU trước khi chốt mua hoặc thiết kế.

Tôi đã đọc cả wiki lẫn các tài liệu và mã liên quan trong `raw/`; chưa có camera để chạy thử model. Chi tiết nguồn và giới hạn ở cuối câu trả lời.

---



# 1. Hai camera có dùng chung cách triển khai không?

Theo [bản research hiện có trong raw](raw/axis-camera-chatgpt-research.md), cả Q1728-LE và P1488-LE đều dùng **ARTPEC-9**, và nguồn này ghi Q1728-LE có 4 GB RAM, P1488-LE có 2 GB RAM. Nhưng đây là **nguồn thứ cấp**, không phải bản datasheet Axis được lưu cục bộ; đặc biệt, nguồn ghi RAM của Q1728-LE trong bảng tổng hợp nhưng không ghi ở phần mô tả riêng.

Nếu xác nhận được SoC là ARTPEC-9, về mặt phần mềm hai camera dùng cùng nhánh:


| Thành phần              | Hướng triển khai                    |
| ----------------------- | ----------------------------------- |
| CPU architecture        | `aarch64`                           |
| Build SDK               | ACAP Native SDK tương thích AXIS OS |
| Model artifact cho DLPU | Quantized `.tflite`                 |
| Inference API           | Larod                               |
| Larod device            | `a9-dlpu-tflite`                    |
| Lấy ảnh camera          | VDO / Video Capture API             |
| Package ứng dụng        | `.eap`                              |


Nguồn trực tiếp cho quy trình ARTPEC-9 là [Model Conversion của Axis](raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md); ví dụ [manifest ARTPEC-9 của](raw/acap-native-sdk-examples/vdo-larod/app/manifest.json.artpec9) `vdo-larod` cũng dùng đúng backend `a9-dlpu-tflite`.

**Về chọn camera:** nếu mức RAM 4 GB so với 2 GB được datasheet xác nhận, Q1728-LE có thêm dư địa cho model, frame buffer và các ứng dụng đồng thời. Không thể suy ra nó inference nhanh gấp đôi. Axis cũng cảnh báo thiết bị ít RAM hơn có thể gặp khó với model lớn trong [YOLOv5 guide](raw/axis-model-zoo/docs/yolov5.md), dù cảnh báo đó không phải benchmark classifier trên hai camera này.

---



# 2. SDK hỗ trợ model image classification nào?

Cần phân biệt **model đã có bằng chứng chạy**, **model có thể thử**, và **model không có bằng chứng trong dữ liệu hiện tại**.

## 2.1. Model có bằng chứng cụ thể trên ARTPEC-9



### MobileNetV2, 224 × 224, quantized TFLite

[Axis Model Zoo — Image classification](raw/axis-model-zoo/README.md) công bố:


| Model                                                | Thiết bị benchmark  | Thời gian inference | ImageNet Top-1 / Top-5 |
| ---------------------------------------------------- | ------------------- | ------------------- | ---------------------- |
| MobileNetV2 TF1, `mobilenet_v2_1.0_224_quant.tflite` | ARTPEC-9, **Q1728** | **2,02 ms**         | **69,1% / 89,0%**      |


Model được README trỏ tới:

[MobileNetV2 quantized TFLite](https://raw.githubusercontent.com/google-coral/test_data/master/mobilenet_v2_1.0_224_quant.tflite)

**Giới hạn quan trọng:**

- Axis ghi thiết bị là **Q1728**, không ghi Q1728-LE hay P1488-LE. Không được xem `2,02 ms` là kết quả đã xác nhận cho hai SKU đang hỏi.
- Đây là thời gian benchmark inference, **không phải thời gian toàn pipeline** gồm lấy frame, resize, xử lý kết quả, event và các ứng dụng khác.
- Số `69,1%` là accuracy trên bài toán/dataset thử nghiệm của Axis, **không dự đoán accuracy cho dataset riêng**.
- README ghi số đo cho **AXIS OS 12.11.72**; accuracy không được đánh giá lại tự động theo từng bản OS.
- Axis nói các model trong Model Zoo là model tham khảo/demonstration, **không mặc định là production-ready**.

Xem thêm [phân tích benchmark trong wiki](wiki/axis-model-zoo-benchmark-results.md) và [mã accuracy test](raw/axis-model-zoo/scripts/accuracy-test/README.md).

### Custom ResNet person/car trong ví dụ `vdo-larod`

Ví dụ native `[vdo-larod](raw/acap-native-sdk-examples/vdo-larod/README.md)` có một classifier nhận ảnh **256 × 256 RGB**, trả score cho **person** và **car**.

Dockerfile của ví dụ dùng cùng artifact `custom_resnet_artpec8_car_human_256.tflite` cho các build `artpec8`, `artpec9` và `cpu`; [manifest ARTPEC-9](raw/acap-native-sdk-examples/vdo-larod/app/manifest.json.artpec9) chọn `a9-dlpu-tflite`.

Đây là ví dụ tốt để hiểu cách tích hợp ứng dụng chạy trực tiếp trên video, nhưng:

- **Không phải classifier tổng quát:** code mặc định chỉ hiểu hai score person/car.
- Artifact đó có tên ARTPEC-8, nhưng ví dụ Axis **chủ đích sử dụng nó cho ARTPEC-9**. Không được suy ra mọi artifact ARTPEC-8 đều tương thích ARTPEC-9.
- Log ví dụ là kết quả do Axis cung cấp, không phải kết quả tôi đã tái lập.

Nguồn: `[vdo-larod/Dockerfile](raw/acap-native-sdk-examples/vdo-larod/Dockerfile)`, `[README](raw/acap-native-sdk-examples/vdo-larod/README.md)`.

## 2.2. Những model khác: không nên kết luận chỉ từ tên


| Model                           | Trạng thái bằng chứng trong nguồn đã đọc                                                                                         |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **MobileNetV3**                 | Có trong Model Zoo cho ARTPEC-7, nhưng **không có dòng classification ARTPEC-9** trong bảng. Cần thử graph cụ thể trên A9.       |
| **EfficientNet-Lite**           | Model Zoo có dòng cho CV25/CV75, **không phải bằng chứng cho ARTPEC-9**.                                                         |
| **ResNet tùy biến**             | Có ví dụ person/car nêu trên; không có nghĩa mọi ResNet hoặc mọi cấu hình head đều chạy.                                         |
| **Custom CNN**                  | Có thể thử nếu graph và quantization phù hợp các giới hạn A9; phải test trực tiếp.                                               |
| **YOLOv5n/s/m**                 | Axis có guide và benchmark A9, nhưng đây là **object detection**, không phải bằng chứng cho YOLO classifier.                     |
| **ViT/Transformer, ONNX tùy ý** | Không có bằng chứng trong các nguồn đã đọc rằng chúng chạy trên A9 DLPU. Không nên cam kết trước khi kiểm operator và thử model. |


**Kết luận về “SDK hỗ trợ model nào”:** ACAP/Larod cung cấp đường để ứng dụng nạp và chạy model; không có danh sách đóng theo tên architecture trong nguồn này. Một file `.tflite` hợp lệ hoặc chạy trên `cpu-tflite` **không tự động chứng minh** nó chạy được trên `a9-dlpu-tflite`.

---



# 3. Phân biệt bài toán trước khi chọn model

Điều này ảnh hưởng trực tiếp đến dataset và cách tích hợp:


| Bài toán                       | Input                    | Output                      | Hướng                                                   |
| ------------------------------ | ------------------------ | --------------------------- | ------------------------------------------------------- |
| **Image classification**       | Toàn frame hoặc một crop | Một hoặc nhiều class/score  | MobileNetV2/custom CNN + Larod                          |
| **Object classification**      | Crop của từng object     | Class của crop              | Cần nguồn crop: detector, ROI cố định hoặc logic khác   |
| **Object detection**           | Toàn frame               | Box + class + score         | SSD/YOLO và post-processing detector                    |
| **Multi-label classification** | Một ảnh                  | Nhiều nhãn có thể cùng đúng | Train head/loss và xử lý threshold riêng cho từng class |


Ví dụ: nếu muốn nhận biết **“cửa mở hay đóng”** trong vùng cố định, một classifier trên ROI có thể đủ. Nếu muốn **tìm nhiều loại hàng hóa ở các vị trí khác nhau**, classifier toàn frame thường không thay thế được detector.

---



# 4. Quy trình triển khai thực tế: từ baseline đến custom model



## Bước 0 — Xác nhận thiết bị

Trên từng camera, ghi lại:

- Đúng model/SKU và SoC.
- AXIS OS version, Larod version và ACAP compatibility.
- Dung lượng RAM khả dụng khi các ứng dụng khác đang chạy.
- DLPU có sẵn và ứng dụng được cấp quyền truy cập.
- Chính sách ký ứng dụng và Developer Mode.

**Đừng lấy 2,02 ms trên Q1728 làm acceptance criterion cho hai camera.** Hãy tự định nghĩa target: accuracy, latency p95, FPS, RAM, nhiệt độ và tỷ lệ bỏ frame.

## Bước 1 — Chạy baseline của Axis trước

Tôi khuyến nghị chạy hai baseline khác nhau:

1. **MobileNetV2 Model Zoo** để kiểm tra một classifier ImageNet có benchmark trên A9.
2. `vdo-larod` **ARTPEC-9** để kiểm tra pipeline live video → preprocessing → inference → log.

Từ thư mục `[raw/acap-native-sdk-examples/vdo-larod/](raw/acap-native-sdk-examples/vdo-larod/README.md)`, README hướng dẫn build:

```bash
docker build \
  --platform=linux/amd64 \
  --build-arg ARCH=aarch64 \
  --build-arg CHIP=artpec9 \
  --tag vdo-larod:a9 .

docker cp \
  "$(docker create --platform=linux/amd64 vdo-larod:a9):/opt/app" \
  ./build
```

Sau đó cài `.eap` qua trang **Apps** của camera và xem log. Đây là lệnh **theo README**, chưa được tôi thực thi trong môi trường này.

**Chú ý:** README mẫu hướng dẫn bật `Allow unsigned apps`, nhưng chính sách này phụ thuộc AXIS OS và môi trường. [Tài liệu migration AXIS OS 13](wiki/acap-axis-os-13-14-migration.md) nêu yêu cầu ký ứng dụng và thay đổi manifest; không nên coi unsigned là phương án production lâu dài.

## Bước 2 — Chuẩn bị dataset custom

Với bài toán classification:

1. Chốt label: single-label hay multi-label, có class “unknown/other” hay không.
2. Thu ảnh từ **đúng góc nhìn camera**, khoảng cách, ngày/đêm, IR, thời tiết, motion blur và mức nén dự kiến.
3. Chia train/validation/test sao cho các frame gần nhau trong cùng video không rơi lẫn vào cả train và test — tránh đánh giá quá lạc quan.
4. Quyết định trước preprocessing: toàn frame hay ROI, RGB order, crop/letterbox/stretch, kích thước, normalization.
5. Dành tập **calibration representative** riêng hoặc lấy từ phần train, phản ánh phân bố input thực tế; không dùng test set để điều chỉnh model.

Đây là **khuyến nghị kỹ thuật**, không phải quy định cụ thể được Axis quy định trong tài liệu A9 lưu cục bộ.

## Bước 3 — Train / fine-tune

Điểm bắt đầu hợp lý:

- **MobileNetV2** hoặc một CNN nhỏ có kiến trúc dễ kiểm soát.
- Batch inference `1`.
- Cố định input shape, ví dụ `[1, 224, 224, 3]`, nếu model và preprocessing của bạn hỗ trợ.
- Thiết kế classifier head sao cho graph sau export nằm trong phạm vi operator A9.
- Chọn metric đúng nghiệp vụ: confusion matrix, precision/recall từng class, false positive theo thời gian, không chỉ accuracy tổng.

**Lưu ý đặc biệt cho classifier:** tài liệu A9 chỉ nêu `MeanXY` cho feature map **7×7 hoặc 8×8**. Không nên mặc định mọi `GlobalAveragePooling` ở mọi kích thước đều được accelerator chấp nhận. Đồng thời `Softmax` không có tên trong bảng operator A9; có thể xem xét xuất logits và tính softmax trên CPU, nhưng cần kiểm tra graph export thực tế và hành vi runtime.

Nguồn: [Supported Ops ARTPEC-9](raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md).

## Bước 4 — Quantize và export TFLite

Axis mô tả chính thức: train bằng framework tùy chọn, quantize **int8/uint8**, export `.tflite`, sau đó thử trên camera. Các guide chi tiết PyTorch→TFLite và TensorFlow→TFLite được Axis dẫn link nhưng **không có bản lưu cục bộ trong** `raw/`. [Nguồn](raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md).

### Ví dụ tham khảo: TensorFlow / Keras full-integer PTQ

Đây là **mẫu kỹ thuật minh họa**, không phải code nguyên văn Axis và **chưa chạy thử** ở đây. Cần thay `load_and_preprocess()` bằng preprocessing đúng với model của bạn:

```python
import numpy as np
import tensorflow as tf

# Keras model đã train. Ví dụ giả định 1 input float32, shape [1, H, W, 3].
model = tf.keras.models.load_model("classifier.keras", compile=False)

# Các ảnh đại diện cho dữ liệu runtime, lấy từ calibration set.
calibration_paths = [
    # "calibration/0001.jpg",
    # "calibration/0002.jpg",
]

def representative_dataset():
    for path in calibration_paths:
        # Phải tạo đúng float tensor mà model FP32 gốc nhận:
        # resize/crop, RGB, normalization... theo lúc train.
        image = load_and_preprocess(path)  # shape [H, W, 3], float32
        yield [np.expand_dims(image, axis=0).astype(np.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset

# Yêu cầu converter chỉ dùng các TFLite integer built-ins.
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]

# Ví dụ chọn int8 I/O. UINT8 là một lựa chọn khác cần kiểm tra theo model/runtime.
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

tflite_bytes = converter.convert()

with open("classifier_int8.tflite", "wb") as f:
    f.write(tflite_bytes)
```

**Mẫu này không bảo đảm model chạy trên DLPU.** `TFLITE_BUILTINS_INT8` chỉ ràng buộc phía converter TFLite; A9 còn có giới hạn operator và tham số riêng.

Nếu model export thất bại hoặc accuracy giảm mạnh:

- Kiểm tra preprocessing và calibration set trước.
- Thử điều chỉnh kiến trúc hoặc quantization strategy.
- Cân nhắc **quantization-aware training — QAT**.
- So sánh FP32 và quantized trên cùng test set.
- Chạy trên đúng backend A9, không chỉ TFLite interpreter trên máy tính.



### Nếu train bằng PyTorch

Axis xác nhận có thể train bằng PyTorch, nhưng bản hướng dẫn chuyển đổi chi tiết được link từ trang A9 **không nằm trong raw**. Tôi không thể xác nhận một pipeline hay version converter cụ thể cho custom PyTorch classifier từ nguồn hiện có.

Nên chọn pipeline PyTorch → TFLite có thể:

1. Giữ nguyên semantics/preprocessing.
2. Sinh full-integer graph, input/output và quantization parameters rõ ràng.
3. Cho phép kiểm tra operator sau export.
4. Được validate trên TFLite CPU và sau đó trên `a9-dlpu-tflite`.

**Không mặc định** PyTorch → ONNX là đủ: tài liệu A9 yêu cầu artifact `.tflite`, không phải `.onnx`.

---



# 5. Quantization: cần kiểm tra những gì?



## 5.1. Quy tắc Axis công bố cho ARTPEC-9

Theo [Optimization Tips](raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md):

- Model cần được lượng tử hóa **INT8/UINT8**; các operator nhận kiểu khác không được DLPU hỗ trợ.
- Tensor tối đa **4 chiều**.
- Batch size lớn hơn `1` không được hỗ trợ.
- Layout được hỗ trợ: **NHWC**.
- **Per-channel quantization** chỉ hỗ trợ cho weight/bias của một tập operator giới hạn.
- Ưu tiên `ReLU6`; tránh explicit padding khi có thể.
- Channel convolution chia thành nhóm **16**; chọn số channel chia hết cho 16 là tối ưu compute, **không phải điều kiện bắt buộc chung cho mọi layer**.

Nguồn này không cho biết đầy đủ danh sách operator nào hỗ trợ per-channel. **Không áp quy tắc ARTPEC-8 sang ARTPEC-9 một cách máy móc.**

Ví dụ YOLOv5 của Axis export A9 bằng `--int8`, trong khi A8 thêm `--per-tensor`; đó là bằng chứng về **pipeline YOLOv5 đó**, không phải chứng minh mọi classifier A9 hỗ trợ per-channel tùy ý. [Nguồn](raw/axis-model-zoo/docs/yolov5.md).

## 5.2. PTQ, calibration và QAT

- **PTQ — Post-Training Quantization:** train float trước, sau đó calibration với ảnh đại diện và chuyển sang integer. Phù hợp làm baseline.
- **QAT — Quantization-Aware Training:** đưa ảnh hưởng lượng tử hóa vào quá trình training/fine-tuning; đáng thử khi PTQ gây giảm accuracy đáng kể.
- **Representative dataset:** phải phản ánh đầu vào thực tế *sau preprocessing mà model float nhận*, gồm các điều kiện ngày/đêm, ánh sáng, ROI và background cần xử lý.
- **Dynamic-range hoặc float16 quantization** không nên coi là đủ cho A9: yêu cầu Axis là integer cho operator chạy trên DLPU.



## 5.3. Input/output quantization không được đoán

Với affine quantization:

```text
real_value ≈ scale × (quantized_value − zero_point)
```

Khi đưa input vào model, thường cần chuyển đổi theo `scale` và `zero_point` của **chính input tensor**; khi đọc output, áp dụng parameters của **output tensor**. Trường hợp input là pixel `uint8` vẫn phải kiểm tra hợp đồng model; không mặc định rằng mọi model đều nhận RGB bytes trực tiếp hoặc đều dùng `[0,1]`.

Có thể kiểm tra bằng TFLite interpreter trên máy build:

```python
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="classifier_int8.tflite")
interpreter.allocate_tensors()

for name, tensors in (
    ("INPUT", interpreter.get_input_details()),
    ("OUTPUT", interpreter.get_output_details()),
):
    for t in tensors:
        print(name, "shape=", t["shape"], "dtype=", t["dtype"])
        print("quantization=", t["quantization"])
        print("quantization_parameters=", t["quantization_parameters"])
```

Đây là đoạn kiểm tra tham khảo, **không phải phép thử DLPU**. Phải đối chiếu lại với tensor Larod và kết quả thực tế trên camera.

---



# 6. ARTPEC-9 hỗ trợ những layer/operator nào?

Axis liệt kê **23 operator** trong [Supported Ops](raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md). Danh sách này là điểm xuất phát để kiểm tra graph sau export, **không phải bảo đảm mọi cấu hình của từng operator đều chạy**.


| Operator                   | Giới hạn đáng chú ý                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `Add`                      | Cộng element-by-element.                                                                                                                   |
| `AveragePool`              | Hỗ trợ 3×3, stride 1, `SAME`; hoặc dạng mean với pool/input 7×7 hay 8×8.                                                                   |
| `Concat`                   | Concat theo channel: channel của **mỗi input** phải chia hết cho 16; có giới hạn quantization scale.                                       |
| `Constant`                 | Bảng không ghi giới hạn riêng.                                                                                                             |
| `Conv2D`                   | Kernel mỗi chiều thuộc `{1,2,3,5,7,9}`; stride 1 hoặc 2 và hai chiều bằng nhau; kernel >7 chỉ stride 1; `SAME`/`VALID`; có giới hạn scale. |
| `DepthToSpace`             | Block size 2; depth là bội số của bình phương block size.                                                                                  |
| `DepthwiseConvolution2D`   | Kernel/stride tương tự Conv2D; **channel multiplier chỉ 1**; có giới hạn scale.                                                            |
| `FullyConnected`           | Weight dạng `HWIO`, `H=W=1`; có giới hạn scale.                                                                                            |
| `LeakyReLU`                | `0 < alpha < 1`.                                                                                                                           |
| `MaxPool`                  | Chỉ các tổ hợp pool/stride/padding cụ thể; 3×3 stride 2 có giới hạn width 417.                                                             |
| `MeanXY`                   | Giảm H×W về 1×1, chỉ liệt kê input **7×7 hoặc 8×8**.                                                                                       |
| `Mul`                      | Chỉ các dạng nhân với constant được mô tả trong bảng, không mặc định tensor × tensor tùy ý.                                                |
| `Pad`                      | Zero padding H/W tối đa 7 mỗi phía; input/output quantization giống nhau.                                                                  |
| `Reinterpret quantization` | Bảng không ghi giới hạn riêng.                                                                                                             |
| `ReLU`                     | Lower bound phải nhỏ hơn upper bound.                                                                                                      |
| `Requantize`               | Output scale không được nhỏ hơn input scale / 128; hỗ trợ đổi input/output type.                                                           |
| `Reshape`                  | Bảng không ghi giới hạn riêng.                                                                                                             |
| `Resize`                   | Kích thước output mỗi chiều là `2n` hoặc `2n−1`; một số cấu hình bilinear có thể kém chính xác.                                            |
| `Sigmoid`                  | Output zero point cố định theo minimum của quantized dtype; scale `1/256`.                                                                 |
| `Split`                    | Split theo channel: channel của mỗi output phải chia hết cho 16.                                                                           |
| `Tanh`                     | Output zero point ở giữa miền dtype; scale `1/128`.                                                                                        |
| `Transpose`                | Chỉ cho phép hoán vị các chiều height, width và channel.                                                                                   |
| `TransposeConvolution2D`   | Kernel theo tập của Conv2D; chỉ stride 2; `SAME`/`VALID`; có giới hạn scale.                                                               |


Với `Conv2D`, `DepthwiseConvolution2D`, `FullyConnected` và `TransposeConvolution2D`, bảng quy định:

```text
0 ≤ input_scale × weight_scale / output_scale ≤ 65536
```

Các operator như **Softmax, SiLU/Swish, HardSwish, PReLU** không xuất hiện theo tên trong bảng này. Điều đó **không đủ để kết luận mọi graph chứa chúng chắc chắn thất bại**: converter/runtime có thể biến đổi graph hoặc xử lý theo cách khác. Nhưng cũng không có cơ sở để hứa chúng chạy trên DLPU. Cần kiểm graph thực tế và test backend.

Xem [bảng wiki đầy đủ](wiki/axis-artpec-9-operator-support.md) và nguồn Axis để tra chính xác từng cấu hình, nhất là `MaxPool`, `Resize` và `Mul`.

---



# 7. Kiểm tra model trên camera



## 7.1. Kiểm tra nạp/chạy qua Larod

Axis đưa ví dụ:

```bash
larod-client \
  -g classifier_int8.tflite \
  -c a9-dlpu-tflite \
  -i ""
```

Nguồn: [ARTPEC-9 Model Conversion](raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md).

Nên coi đây là **smoke test** cho đường model/backend, không phải kiểm định accuracy. Tài liệu local không giải thích đầy đủ ngữ nghĩa `-i ""`; không nên xem lệnh này là phép thử với ảnh thật.

Để tách lỗi, có thể thử backend CPU:

```bash
larod-client \
  -g classifier_int8.tflite \
  -c cpu-tflite \
  -i ""
```

Nhưng:

```text
CPU chạy được  ≠  DLPU chạy được
DLPU load được ≠  accuracy đúng
Benchmark nhanh ≠  FPS end-to-end
```



## 7.2. Benchmark nhiều lần

[Model Zoo](raw/axis-model-zoo/README.md) có `model_performance_tester.py`, dùng SSH và `larod-client` để đo inference trên dữ liệu random. Ví dụ theo README:

```bash
python3 scripts/model_performance_tester.py \
  --model_path classifier_int8.tflite \
  --test_duration 1000 \
  --chip A9-DLPU \
  --device_ip <CAMERA_IP> \
  --device_credentials <USER> <PASSWORD>
```

**Cảnh báo vận hành:** script nhận password qua command line; có thể lộ trong shell history/process list. Nó cũng tự chấp nhận SSH host key và chạy lệnh xóa output từ xa. Hãy xem [mã script](raw/axis-model-zoo/scripts/model_performance_tester.py) và dùng môi trường test phù hợp, hoặc sửa cách xác thực/cleanup trước khi áp dụng.

Đo thêm:

- Cold start/load model.
- Mean, p95/p99 latency và FPS **toàn pipeline**.
- RAM peak, CPU, DLPU contention.
- Với analytics mặc định hoặc application khác đang chạy.
- Input thực tế ngày/đêm, nhiệt độ và uptime dài.
- Accuracy trên test set độc lập.

---



# 8. Tích hợp custom classifier vào ACAP



## 8.1. Pipeline ứng dụng

```text
VDO: lấy frame
    ↓
Chọn toàn ảnh hoặc crop ROI
    ↓
Resize / crop / letterbox / RGB / normalize / quantize
    ↓
Larod: a9-dlpu-tflite
    ↓
Đọc output tensor theo dtype, shape, scale, zero point
    ↓
Argmax hoặc threshold theo class
    ↓
Business logic: lọc theo thời gian / event / API / log
```

Trong ví dụ Axis:

- `VDO` lấy frame RGB hoặc YUV tùy platform.
- `cpu-proc`/libyuv được dùng khi cần resize hoặc đổi màu.
- Larod nạp model và chạy inference.
- Ví dụ `vdo-larod` dùng synchronous `larodRunJob()`, chưa pipeline async; README nói `larodRunJobAsync()` có thể là hướng tối ưu hơn nhưng phức tạp hơn.

Nguồn: `vdo-larod` [README](raw/acap-native-sdk-examples/vdo-larod/README.md), [phân tích ví dụ Larod trong wiki](wiki/acap-example-larod-object-detection.md).

## 8.2. Những thứ phải sửa khi thay model

Không chỉ copy `custom_model.tflite` vào package. Cần kiểm và sửa:

1. **Input:** số tensor, shape, dtype, RGB/BGR, layout, normalization, quantization.
2. **Preprocessing:** ROI và cách resize phải khớp train/calibration.
3. **Output:** số tensor, kích thước, logits hay probability, dtype, scale/zero point.
4. **Labels:** thứ tự class đúng với training; version labels cùng version model.
5. **Single-label vs multi-label:** argmax và threshold không thay thế nhau.
6. **Post-processing:** tránh giả định score là `uint8 / 255` nếu model không dùng đúng quantization đó.
7. **Manifest/package:** bundle model, labels và khai báo resource DLPU.
8. **Kiểm thử:** cùng tập ảnh qua model gốc, TFLite trên máy và camera; đối chiếu chênh lệch score/class.

Đặc biệt, README của `vdo-larod` nói rõ model mặc định có **hai score person/car**. Vì vậy code xử lý output của nó phải được viết lại cho classifier N class hoặc output format khác.

## 8.3. Manifest và AXIS OS

Ví dụ ARTPEC-9 khai báo:

```json
"deepLearningProcessor": {
  "enabled": true,
  "required": true
}
```

Đây chỉ là **một phần của** `resources`, không phải manifest hoàn chỉnh. Xem [manifest mẫu](raw/acap-native-sdk-examples/vdo-larod/app/manifest.json.artpec9).

Với AXIS OS 13, tài liệu migration được lưu trong wiki nêu thêm các điểm đáng kiểm tra: khai báo DLPU, manifest schema v2/`compatibleOsVersions`, signing và Larod API v3. Hãy đối chiếu version thực tế của camera và SDK trước khi áp dụng. [Nguồn](wiki/acap-axis-os-13-14-migration.md).

---



# 9. Checklist PoC đề xuất


| Giai đoạn                  | Việc làm                                       | Tiêu chí đi tiếp                                        |
| -------------------------- | ---------------------------------------------- | ------------------------------------------------------- |
| **A. Hardware**            | Xác minh SoC/RAM/OS của từng SKU               | Có thông số từ thiết bị hoặc datasheet Axis             |
| **B. Baseline live**       | Build `vdo-larod` cho `artpec9`                | Frame và score được log ổn định                         |
| **C. Baseline classifier** | Thử MobileNetV2 Model Zoo                      | Load và chạy được A9; biết input/output thực tế         |
| **D. Custom FP32**         | Fine-tune model với dataset camera             | Đạt metric nghiệp vụ trên test độc lập                  |
| **E. Quantized**           | PTQ → so FP32 vs INT8; thử QAT nếu cần         | Mức mất accuracy nằm trong ngân sách                    |
| **F. DLPU**                | Smoke test và benchmark trên **cả hai camera** | Không lỗi operator/shape; latency và RAM đạt target     |
| **G. ACAP**                | Tích hợp VDO/Larod, labels và post-processing  | Kết quả khớp thử nghiệm offline trong sai số chấp nhận  |
| **H. Production**          | Chạy cùng workload thực, test dài hạn, ký app  | Đạt target p95/p99, độ ổn định và chính sách triển khai |


**Thứ tự khuyến nghị:** bắt đầu bằng `vdo-larod` và MobileNetV2, sau đó mới thay custom classifier. Nếu use case cần vị trí của nhiều object, xác định detector/ROI trước; không dùng YOLO detection benchmark để dự báo classifier.

---



## Nguồn đã kiểm tra và giới hạn

**Nguồn chính trong** `raw/`**:**

- [Axis Model Zoo — bảng classification, benchmark và phương pháp đo](raw/axis-model-zoo/README.md).
- [ARTPEC-9 Model Conversion](raw/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/index.md).
- [ARTPEC-9 Optimization Tips](raw/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/index.md).
- [ARTPEC-9 Supported Ops](raw/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/index.md).
- `vdo-larod` [README](raw/acap-native-sdk-examples/vdo-larod/README.md), [Dockerfile](raw/acap-native-sdk-examples/vdo-larod/Dockerfile), [manifest ARTPEC-9](raw/acap-native-sdk-examples/vdo-larod/app/manifest.json.artpec9).
- [Model Zoo accuracy test](raw/axis-model-zoo/scripts/accuracy-test/README.md), [manifest ARTPEC-9](raw/axis-model-zoo/scripts/accuracy-test/app/manifest.json.artpec9) và [preprocessing script](raw/axis-model-zoo/scripts/accuracy-test/larod_convert.py).
- [YOLOv5 guide](raw/axis-model-zoo/docs/yolov5.md), dùng để phân biệt ví dụ detection và khác biệt export A8/A9.
- [Research thứ cấp về hai camera](raw/axis-camera-chatgpt-research.md).

**Giới hạn:** Đã đọc raw, nhưng không có datasheet chính hãng của hai SKU và không có bản local của guide Axis chi tiết PyTorch/TensorFlow→TFLite. Không truy cập thiết bị, không chạy export/model/benchmark, không xác nhận phiên bản tài liệu mới nhất trên web. Kết quả này được để **transient**, chưa ghi synthesis mới vào wiki.