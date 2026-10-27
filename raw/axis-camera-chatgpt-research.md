# Kết quả tra cứu SoC của AXIS Q1728-LE và AXIS P1488-LE

Cả hai camera đều sử dụng SoC ARTPEC-9 của Axis, có tích hợp bộ tăng tốc AI Deep Learning Processing Unit (DLPU).

Đây là thông tin được xác nhận trong tài liệu chính thức của Axis, không phải suy đoán từ tên sản phẩm.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://help.axis.com\&sz=32)

Technical Documentation+2



## 1. So sánh phần cứng hai camera

[AXIS Q1728-LE Block Camera | Axis Communications](https://images.openai.com/static-rsc-4/gxrKpwL_j0q1yz0KVyeSOfgRvNePXZDZGjx0NgQOtAeAmtLpWFBk6EX11pcmFNviOXemQFV8IucbAy_zD8RhBc6SIiictwprJjW1TrXu1xxsfKaLfv7vjvmKkmKvOJgOSjx07MSe-1oXIR_zz1H9tqip1oeAICiXKNZH3BAr4G8?purpose=inline)

AXIS Q1728-LE

Block camera

- SoC: ARTPEC-9
- AI accelerator: DLPU
- Độ phân giải: 8 MP (4K)
- Cảm biến: 1/1.2 inch
- Video tối đa: 50/60 fps
- Codec: H.264, H.265, AV1

[Trang sản phẩm Axis](https://www.axis.com/products/axis-q1728-le?utm_source=chatgpt.com)

[AXIS P1488-LE 8MP AI-Powered Outdoor Bullet IP Camera with 5.9-13.8mm Wide-Angle Lens, 164ft IR - 03184-001](https://images.openai.com/static-rsc-4/QxLZa1sYuvOjs0dKIEKyPnHHFdYoNg9KJk_opF6zUHrQS7Hkl31qPTvm28zX40d71Tl5isR1T9UZQHJ49c_JeTl-hhJUha7lUroT6RwwSGSEfF0D5GugxBoPZTLoZNrgBDc89xkR6HpDyJRqsDmD63Vc4gC6K3B7Q_-Yq56UW6c?purpose=inline)

AXIS P1488-LE

Bullet camera

- SoC: ARTPEC-9
- AI accelerator: DLPU
- RAM: 2 GB
- Flash: 8 GB
- Độ phân giải: 8 MP (4K)
- Cảm biến: 1/1.2 inch
- Video tối đa: 50/60 fps
- Codec: H.264, H.265, AV1

[Trang sản phẩm Axis](https://www.axis.com/en-vn/products/axis-p1488-le?utm_source=chatgpt.com)

Kết luận ban đầu: Nếu mục tiêu của bạn là chạy mô hình AI tùy chỉnh trực tiếp trên camera qua AXIS Camera Application Platform (ACAP), thì cả hai thuộc cùng nhóm triển khai ARTPEC-9. Không cần quy trình biên dịch của Edge TPU (ARTPEC-7) hay Ambarella CNNGen (CV25/CV75).

## 2. Đối chiếu bảng SoC và Larod của bạn

| Thuộc tính           | Q1728-LE             | P1488-LE             |
| -------------------- | -------------------- | -------------------- |
| SoC                  | ARTPEC-9             | ARTPEC-9             |
| Kiến trúc CPU        | ARM64 (`aarch64`)    | ARM64 (`aarch64`)    |
| RAM                  | 4 GB                 | 2 GB                 |
| Flash                | 8 GB                 | 8 GB                 |
| AI accelerator       | DLPU                 | DLPU                 |
| Model chạy trên DLPU | INT8/UINT8 `.tflite` | INT8/UINT8 `.tflite` |
| Larod device         | `a9-dlpu-tflite`     | `a9-dlpu-tflite`     |
| Biên dịch offline    | Không cần            | Không cần            |
| Edge TPU Compiler    | Không cần            | Không cần            |
| Ambarella CNNGen     | Không cần            | Không cần            |
| Độ khó theo Axis     | Trung bình           | Trung bình           |

Nguồn: Datasheet Q1728-LE, Product Selector P1488-LE và tài liệu Larod chính thức.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.axis.com\&sz=32)

Axis Communications+3



Điểm khác biệt đáng chú ý: Q1728-LE có 4 GB RAM, gấp đôi P1488-LE. Điều này có lợi khi ứng dụng ACAP sử dụng nhiều bộ nhớ, nhưng không đồng nghĩa tốc độ inference DLPU gấp đôi.

## 3. Cách chuyển model để chạy trên hai camera

PyTorch / TensorFlow

Model đã train

Quantization INT8 / UINT8

Xuất model `.tflite`

Larod: `a9-dlpu-tflite`

Không cần compiler offline

ARTPEC-9 DLPU

Inference trực tiếp trên camera

Lệnh kiểm tra model trên camera theo tài liệu Axis:

```
larod-client -g my_model.tflite -c a9-dlpu-tflite -i ""
```

Nếu cần kiểm tra bản chạy trên CPU:

```
larod-client -g my_model.tflite -c cpu-tflite -i ""
```

Đây là hai backend khác nhau. Model chạy thành công trên `cpu-tflite` không đảm bảo chạy được trên `a9-dlpu-tflite`, vì DLPU chỉ hỗ trợ một tập operator và cấu hình tensor giới hạn.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation+1



## 4. Giới hạn DLPU ARTPEC-9

Mình đối chiếu lại trực tiếp với trang Optimization Tips và Supported Ops của Axis.

| Đặc điểm                 | Kết quả xác minh                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| INT8 / UINT8             | Bắt buộc đối với operator chạy trên DLPU                                                   |
| Batch                    | Chỉ hỗ trợ batch = 1                                                                       |
| Số chiều tensor          | Tối đa 4                                                                                   |
| Data layout              | NHWC                                                                                       |
| Per-tensor quantization  | Có thể sử dụng                                                                             |
| Per-channel quantization | Hỗ trợ giới hạn cho weight và bias của một số operator                                     |
| Channel chia hết cho 16  | Khuyến nghị để tối ưu hiệu suất                                                            |
| ReLU6                    | Khuyến nghị                                                                                |
| Dynamic shape            | Nên dùng static shape; tài liệu ARTPEC-9 này chưa xác nhận rõ mọi trường hợp dynamic shape |
| Supported operators      | 23 operator được liệt kê, mỗi loại có giới hạn riêng                                       |

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation+1

Ví dụ, danh sách operator được hỗ trợ có `Conv2D`, `DepthwiseConvolution2D`, `Concat`, `Add`, `Reshape`, `Resize`, `Sigmoid`, `MaxPool`, `Transpose`.

Tuy nhiên, một operator có tên trong danh sách không có nghĩa tất cả cấu hình của nó đều được hỗ trợ. Ví dụ `Concat` theo chiều channel yêu cầu số channel của mỗi input là bội số của 16.

Tài liệu chi tiết:

- [ARTPEC-9 Optimization Tips](https://developer.axis.com/computer-vision/on-device/system-on-chip/artpec-9/optimization-tips/?utm_source=chatgpt.com)
- [ARTPEC-9 Supported Ops](https://developer.axis.com/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/?utm_source=chatgpt.com)
- [ARTPEC-9 Model Conversion](https://developer.axis.com/computer-vision/on-device/system-on-chip/artpec-9/model-conversion/?utm_source=chatgpt.com)

## 5. YOLOv5, YOLOv8 và YOLO11 có chạy được không?

Mình tìm được benchmark thực tế từ kho [Axis Model Zoo](https://github.com/AxisCommunications/axis-model-zoo?utm_source=chatgpt.com).

Benchmark inference trên AXIS Q1728 (ARTPEC-9), AXIS OS 12.11.72

| Model           | Thời gian / inference | FPS lý thuyết\* |
| --------------- | --------------------- | --------------- |
| SSD MobileNetV2 | 10.48 ms              | \~95            |
| YOLOv5n         | 31.85 ms              | \~31            |
| YOLOv5s         | 35.00 ms              | \~29            |
| YOLOv5m         | 42.70 ms              | \~23            |

\*FPS tính từ thời gian inference trung bình, không phải FPS end-to-end của camera. Benchmark được Axis đo trên Q1728, không phải trực tiếp trên Q1728-LE hoặc P1488-LE. Không thể bảo đảm hai camera cho kết quả giống hệt.

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

Theo đó:

- YOLOv5n/s/m: Axis có model ARTPEC-9 được benchmark, nên đây là lựa chọn có cơ sở rõ ràng để bắt đầu.
- SSD MobileNetV2: Đã có benchmark và là một lựa chọn phù hợp để thử nghiệm.
- YOLOv8: Axis có benchmark YOLOv8n cho CV75, nhưng đó không phải bằng chứng YOLOv8 hoạt động trên ARTPEC-9.
- YOLO11: Chưa tìm thấy benchmark chính thức tương ứng cho ARTPEC-9 trong Axis Model Zoo; cần kiểm tra operator, quantization và chạy thử thực tế.

## 6. Một điểm cần sửa trong ghi chú ban đầu

Bạn ghi:

> CV25/CV75: CNNGen không công khai, phải liên hệ Ambarella (CV75, ARTPEC-9).

Phần ARTPEC-9 trong ngoặc là nhầm. Quy trình cần liên hệ Ambarella để có CNNGen áp dụng cho CV25 và CV75, không áp dụng cho ARTPEC-9. Axis xác nhận điều này trong hướng dẫn chuyển model cho CV25/CV75.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation+1



## 7. Nên chọn camera nào để triển khai AI?

Nếu ưu tiên phát triển ứng dụng AI tùy chỉnh chạy trực tiếp trên camera, mình nghiêng về Q1728-LE, vì có 4 GB RAM thay vì 2 GB, trong khi cả hai cùng dùng ARTPEC-9 và `a9-dlpu-tflite`.

Tuy vậy, khả năng chạy thành công model và FPS thực tế vẫn cần kiểm chứng bằng model cụ thể trên từng camera.

Bạn có thể bắt đầu từ model YOLOv5 được Axis cung cấp, sau đó triển khai bằng ACAP Native SDK với Video Capture API (VDO) và Machine Learning API (Larod).&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation



Tóm lại: Cả AXIS Q1728-LE và AXIS P1488-LE đều thuộc đúng dòng ARTPEC-9 → INT8/UINT8 TFLite → `a9-dlpu-tflite` → độ khó trung bình trong bảng của bạn. Không cần Edge TPU Compiler hoặc Ambarella CNNGen.