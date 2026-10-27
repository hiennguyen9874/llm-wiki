# Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis

Nghiên cứu từ tài liệu Axis Developer, ACAP SDK, tài liệu về các SoC ARTPEC và Ambarella — cập nhật tháng 10/2026.

## 1. Kết luận quan trọng nhất

Axis cho phép developer triển khai AI model tự huấn luyện trực tiếp lên một số dòng camera thông qua AXIS Camera Application Platform (ACAP), đồng thời sử dụng DLPU để tăng tốc inference.

Đây không chỉ là hệ thống analytics đóng với một số tính năng do Axis cung cấp.

Tuy nhiên, cần phân biệt ba lớp:

| Thành phần                      | Mức độ custom                                                                        | Đánh giá                             |
| ------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------ |
| AI model                        | Tự train, quantize, thay đổi kiến trúc model                                         | Cao, nhưng bị giới hạn bởi phần cứng |
| ACAP application và SDK         | Tự viết inference pipeline, xử lý video, business logic, API, integration            | Cao                                  |
| DLPU hardware và runtime nội bộ | Truy cập thông qua API/driver do Axis cung cấp; không được tùy ý lập trình phần cứng | Hạn chế                              |

Có 4 phát hiện đặc biệt đáng chú ý:

- Axis có SDK công khai, tài liệu developer và các repository ví dụ trên GitHub. Có thể phát triển ứng dụng AI riêng, đóng gói rồi cài lên camera.
- Không bắt buộc dùng AI model của Axis. Có thể train bằng PyTorch hoặc TensorFlow, convert sang định dạng phù hợp với SoC rồi chạy inference.
- Không phải camera Axis nào cũng hỗ trợ DLPU, và không phải các DLPU đều tương thích với cùng một model.
- SDK phát triển ứng dụng mở, nhưng không có nghĩa phần cứng accelerator là open-source. Đặc biệt, một số chip Ambarella yêu cầu toolchain không được phát hành công khai.

Axis xác nhận trực tiếp khả năng chạy custom computer vision applications trên camera, sử dụng Video Capture API (VDO) và Machine Learning API (Larod).&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation+3



## 2. Axis DLPU thực sự là gì?

DLPU (Deep Learning Processing Unit) là bộ tăng tốc phần cứng dành cho inference neural network, được tích hợp trong các thiết bị Axis tương thích.

Có thể hình dung kiến trúc như sau:

Camera sensor

Image / video capture

AXIS OS + ACAP Application

VDO API lấy frame, resize, crop, preprocessing

Larod Machine Learning API

Nạp model, điều phối inference

DLPU

Accelerated inference

CPU

Ứng dụng và các phép toán hỗ trợ

Custom post-processing và integration

Detection, tracking, event, metadata, VMS, HTTP

Điểm quan trọng là DLPU chủ yếu tăng tốc phép toán neural network, còn logic ứng dụng như tracking, rule engine, kết nối server, xử lý kết quả model có thể được thực thi trên CPU.

Một model cũng có thể có các phép toán không được DLPU hỗ trợ. Một số nền tảng có khả năng chuyển phần đó sang CPU, nhưng việc chuyển qua lại giữa CPU và DLPU làm tăng latency.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation+1



## 3. Những dòng camera Axis nào hỗ trợ deploy custom AI model?

Theo tài liệu Axis hiện tại, có 5 nền tảng SoC hỗ trợ tăng tốc bằng DLPU. Đây là tiêu chí quan trọng hơn việc camera thuộc dòng M, P hay Q.

### Bảng so sánh khả năng deploy model

| SoC            | Format để chạy trên DLPU                   | Công cụ chuyển đổi         | Độ thuận tiện |
| -------------- | ------------------------------------------ | -------------------------- | ------------- |
| ARTPEC-7       | Quantized `.tflite` biên dịch cho Edge TPU | Edge TPU Compiler          | Trung bình    |
| ARTPEC-8       | INT8/UINT8 `.tflite`                       | TensorFlow Lite conversion | Tốt           |
| ARTPEC-9       | INT8/UINT8 `.tflite`                       | TensorFlow Lite conversion | Tốt           |
| Ambarella CV25 | Native `.bin`                              | Ambarella CNNGen           | Khó           |
| Ambarella CV75 | Native `.bin`                              | Ambarella CNNGen           | Khó           |

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation+5

### Một số camera thực tế để tham khảo

[Axis network camera M3216-LVE 4 MP, 0.16 lx, 190° rotation, 102° horizontal viewing angle, PoE, IR, digital PTZ, white | INSERV.LV](https://images.openai.com/static-rsc-4/f0w4c9Tw3Vdf4_NdmK3vzt9fF-_07pyW0DtCS7WCFeUQShIUivkfGiW5HuyLHGuAl9yzEVoYeSwpO9jWUk1ZKu8IxEPbECnIfOO6ppBRLisYh7PXe0q-uEUB3XeJJJ77bi7CYLh522edg9A1eZYfYrBkFv5M-TAluuYZvic57zk?purpose=inline)

AXIS M3216-LVE

ARTPEC-8 · 4 MP

Thuộc M32 Series, có DLPU và hỗ trợ phát triển ứng dụng deep learning tùy biến qua ACAP. Phù hợp để nghiên cứu pipeline TFLite trên ARTPEC-8.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.axis.com\&sz=32)

Axis Communications



[AXIS Q3548-LVE Dome Camera | Axis Communications](https://images.openai.com/static-rsc-4/gEAlfoioQmr_Vo6rorFLV5IJ0l-ERDRsgCT3Srxwdx2x0Ti7G50O97ufbVaYIQQAE4CKuo0fYopI9naDHWiQv4a0Hr7i0a5lrXVXt1_N4fUpjnLbk50ZQq5RD31M0mznZJHZKQH_9f1uBOs6Au_-pUm2yszltNsh1ThUvny3-kE?purpose=inline)

AXIS Q3548-LVE

ARTPEC-9 · 8 MP

Có DLPU thế hệ ARTPEC-9 và hỗ trợ chạy các ứng dụng analytics tại edge. Đây là lựa chọn đáng xem xét khi cần hiệu năng cao hơn.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.axis.com\&sz=32)

Axis Communications



[Buy AXIS M2036-LE Network Camera - Color | SRG Consultant Inc.](https://images.openai.com/static-rsc-4/93IhvZHRj0Ea8laNdDMUndqwyAZrJQS5wEYZXlrtJHvcnuo8bfDGetxpQWKKQV0ZDeXRXQnQhKQD7BC3scNFyGLRpl1v3tdDM3wWB0tNjY1nqK3qY6Hk_WJpQiqBLs8ONaiDw3HQnD8_KGoCVRpX8_SYu9eFuE8drfu1RLhqTDo?purpose=inline)

AXIS M2036-LE

Ambarella CV25 · 4 MP

Có DLPU và hỗ trợ analytics tại edge, nhưng để triển khai model riêng lên accelerator CV25 cần Ambarella CNNGen, không thuận tiện bằng ARTPEC-8/9.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.axis.com\&sz=32)

Axis Communications+1



Một điểm cần tránh: có DLPU không đồng nghĩa một model đã convert sẽ chạy được trên mọi camera Axis. Phải kiểm tra SoC, bộ nhớ, phiên bản AXIS OS, ACAP API và tập operator được hỗ trợ.

Axis cung cấp [Product Selector](https://www.axis.com/support/tools/product-selector?utm_source=chatgpt.com) để lọc theo `Hardware platform → Compute capabilities → DLPU`, sau đó chọn `System-on-chip`.

## 4. Deploy custom model lên camera bằng cách nào?

Có hai phần tách biệt:

1. Chuyển model đã train sang định dạng mà DLPU có thể chạy.
2. Viết một ACAP application để sử dụng model đó trên camera.

### 4.1. Quy trình deploy trên ARTPEC-8/9

Train custom model

PyTorch / TensorFlow · Custom dataset

Export và quantization

INT8 / UINT8 TensorFlow Lite

custom_model.tflite

Kiểm tra khả năng chạy trên DLPU của SoC đích

ACAP Native SDK

C/C++ application + model + manifest

Build `.eap` và cài vào camera

Web GUI hoặc VAPIX Application API

Ví dụ lệnh test model trực tiếp trên camera qua SSH theo tài liệu Axis:

ARTPEC-8

```
larod-client -g custom_model.tflite -c axis-a8-dlpu-tflite -i ""
```

ARTPEC-9

```
larod-client -g custom_model.tflite -c a9-dlpu-tflite -i ""
```

Đây là lệnh thử nạp và chạy model, chưa phải một ứng dụng AI hoàn chỉnh. Ứng dụng thực tế còn phải xử lý input tensor, frames, output tensors, post-processing và logic nghiệp vụ.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation+2



Axis có mã nguồn mẫu triển khai object detection, bao gồm YOLOv5:

[GitHub — ACAP Native SDK Examples](https://github.com/AxisCommunications/acap-native-sdk-examples?utm_source=chatgpt.com)

### 4.2. Đóng gói application

Với ACAP Native SDK, developer build ứng dụng bằng Docker trên máy tính phát triển. Kết quả là package `.eap`, sau đó có thể cài vào camera qua giao diện quản trị hoặc API.

Một ACAP application điển hình gồm:

```
custom-ai-app/
├── Dockerfile
└── app/
    ├── manifest.json
    ├── Makefile
    ├── main.cpp
    ├── custom_model.tflite
    └── LICENSE
```

Native SDK dùng toolchain cho kiến trúc tương ứng:

- `armv7hf` đối với ARTPEC-7.
- `aarch64` đối với ARTPEC-8/9.

Việc sử dụng Docker ở đây là để build SDK, không có nghĩa camera phải hỗ trợ chạy Docker container.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation



Hướng dẫn chính thức: [Create your first ACAP application](https://developer.axis.com/acap/get-started/create-your-first-acap-application/?utm_source=chatgpt.com).

## 5. SDK của Axis mở đến đâu?

Đây là phần quan trọng nhất nếu định xây dựng một sản phẩm AI riêng chạy trên camera Axis.

### Các khả năng mà ACAP SDK công khai

| Khả năng                             | Hỗ trợ                                   | Chi tiết                                 |
| ------------------------------------ | ---------------------------------------- | ---------------------------------------- |
| Custom model weights                 | Có                                       | Tự train, quantize và deploy             |
| Custom neural network architecture   | Có điều kiện                             | Phải phù hợp supported operators         |
| Custom preprocessing                 | Có                                       | Resize, crop, format conversion          |
| Custom post-processing               | Có                                       | NMS, tracking, logic ứng dụng            |
| Video frame capture                  | Có                                       | VDO API                                  |
| DLPU inference                       | Có                                       | Larod API                                |
| Bounding box / overlay               | Có                                       | Bounding Box, Axoverlay APIs             |
| Custom event                         | Có                                       | Axevent API                              |
| Giao tiếp HTTP/VMS                   | Có                                       | VAPIX, HTTP integration                  |
| Third-party libraries                | Có điều kiện                             | Phụ thuộc runtime, kiến trúc, tài nguyên |
| Custom accelerator driver / firmware | Không có API công khai được tài liệu hóa | Phải dựa vào interface do Axis cung cấp  |

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation+2

Ví dụ, bạn có thể phát triển một ứng dụng AI phát hiện hàng hóa trên băng chuyền:

- Sử dụng VDO API để lấy frame trực tiếp.
- Dùng Larod chạy model nhận diện sản phẩm trên DLPU.
- Dùng C++ để thực hiện NMS, tracking, đếm sản phẩm.
- Vẽ bounding box trên luồng video.
- Phát event khi có sản phẩm lỗi, gửi kết quả về backend hoặc VMS.

Tất cả có thể thực hiện trong ứng dụng của bạn mà không cần chỉnh sửa source code AXIS OS.

### Một điểm khác biệt: ACAP không phải SDK để viết NPU kernel

Axis không cung cấp ACAP như một môi trường để developer tùy ý định nghĩa instruction set hay lập trình trực tiếp các đơn vị tính toán trong DLPU.

API inference được cung cấp qua Larod, có nhiệm vụ điều phối truy cập đến phần cứng giữa các application.

Do đó:

- Custom application logic: mức linh hoạt cao.
- Custom model graph: linh hoạt trong phạm vi khả năng của DLPU.
- Custom hardware execution: phụ thuộc backend và các operator Axis hỗ trợ.

Open development framework không đồng nghĩa toàn bộ SDK, runtime, driver và firmware đều open-source. Axis công bố repository ví dụ mã nguồn dưới giấy phép Apache-2.0, nhưng điều này không mở mã nguồn của tất cả thành phần bên dưới.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1



## 6. Giới hạn lớn nhất khi chạy custom models

### 6.1. Giới hạn operators và quantization

DLPU không phải GPU/NPU đa dụng có thể chạy mọi model PyTorch hay ONNX.

Với ARTPEC-8:

- Yêu cầu model quantized INT8/UINT8.
- Không hỗ trợ dynamic tensor sizes trên DLPU.
- Per-tensor quantization được khuyến nghị vì hiệu năng tốt hơn.
- Axis khuyến nghị tối ưu convolution, channel count và activation function.

Với ARTPEC-9:

- INT8/UINT8 vẫn là yêu cầu chính.
- Hỗ trợ tensor tối đa 4 chiều.
- Không hỗ trợ batch size lớn hơn 1.
- Chủ yếu dùng layout NHWC.
- Per-channel quantization chỉ được hỗ trợ với một số operator nhất định.

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation+1

Đặc biệt, ARTPEC-9 có những hạn chế ở từng operator, ví dụ giới hạn kernel, stride, padding và channel alignment cho convolution. Một model xuất được thành TFLite vẫn có thể không chạy toàn bộ trên DLPU.

Hai bảng bắt buộc phải đọc khi chọn architecture:

[ARTPEC-8 — Supported Operators](https://developer.axis.com/computer-vision/on-device/system-on-chip/artpec-8/supported-ops/?utm_source=chatgpt.com)[ARTPEC-9 — Supported Operators](https://developer.axis.com/computer-vision/on-device/system-on-chip/artpec-9/supported-ops/?utm_source=chatgpt.com)

### 6.2. Model nào phù hợp?

| Model / bài toán           | Khả năng phù hợp                    | Lưu ý                                        |
| -------------------------- | ----------------------------------- | -------------------------------------------- |
| MobileNet / MobileNet-like | Cao                                 | Hợp với edge inference                       |
| YOLOv5 loại nhỏ            | Tốt, khi tối ưu đúng                | Có ví dụ chính thức                          |
| Custom small CNN           | Cao                                 | Dễ kiểm soát operators                       |
| Segmentation CNN nhỏ       | Có thể                              | Cần kiểm tra toàn bộ graph                   |
| YOLOv8/YOLO11              | Cần kiểm chứng                      | Không nên mặc định sẽ chạy toàn bộ trên DLPU |
| Vision Transformer         | Khó hơn                             | Cần đánh giá operator, memory, CPU offload   |
| Multimodal / VLM / LLM     | Không phải use case tối ưu mặc định | Chưa có bảo đảm tương thích hay hiệu năng    |

Đây là đánh giá kỹ thuật dựa trên đặc tính DLPU và supported operators, không phải danh sách tương thích chính thức cho mọi phiên bản model.

Axis có Axis Model Zoo, cung cấp model tham khảo và các số đo về hiệu năng, accuracy trên các SoC. Đây là tài liệu rất hữu ích để chọn backbone trước khi đầu tư train model riêng.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation



[GitHub — Axis Model Zoo](https://github.com/AxisCommunications/axis-model-zoo?utm_source=chatgpt.com)

### 6.3. Có thể chạy nhiều model cùng lúc không?

Có, nhưng phải hiểu đúng.

Theo FAQ của Axis, nhiều model có thể cùng hoạt động trên một thiết bị, nhưng các lần inference trên DLPU được chia sẻ theo thời gian, không phải chạy song song độc lập.

Nếu chạy AXIS Object Analytics đồng thời với application riêng, các workload sẽ cạnh tranh tài nguyên DLPU và có thể ảnh hưởng latency/FPS. Axis khuyến nghị tắt analytics mặc định nếu không cần thiết.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

Axis developer documentation



Điều này có nghĩa không nên tính tổng throughput theo cách: một model chạy 20 FPS riêng lẻ thì hai model sẽ cùng chạy được 20 FPS.

## 7. Có thể thay model bên trong AXIS Object Analytics không?

Cần phân biệt:

AXIS Object Analytics (AOA) là application chính thức của Axis, có sẵn trên nhiều camera. Nó cung cấp các chức năng phát hiện, phân loại và xử lý tình huống.

Axis có AOA API để thiết lập các scenario, vùng phát hiện, trigger, rule và overlay. Nhưng trong tài liệu API công khai mình kiểm tra, không có cơ chế được tài liệu hóa để upload model tùy ý nhằm thay thế backbone nhận diện bên trong AOA.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation



Vì vậy có hai hướng:

| Hướng phát triển                                     | Khả năng                                    |
| ---------------------------------------------------- | ------------------------------------------- |
| Dùng AOA và custom các rule/event                    | Có, theo API cung cấp                       |
| Thay detector gốc trong AOA bằng model PyTorch riêng | Không có interface công khai được xác nhận  |
| Viết ACAP application với model riêng, chạy cạnh AOA | Có, nếu tài nguyên cho phép                 |
| Tắt AOA và sử dụng hoàn toàn custom ACAP inference   | Có, nếu camera hỗ trợ application tương ứng |

Nếu cần nhận diện một loại đối tượng đặc thù như lỗi sản phẩm, vật thể công nghiệp hoặc các class ngoài tập nhãn mặc định, hướng phù hợp hơn là viết ACAP application riêng.

## 8. Một thay đổi rất đáng chú ý ở ACAP SDK

Axis từng có hai hướng phát triển chính:

|                        | ACAP Native SDK         | ACAP Computer Vision SDK / Solution     |
| ---------------------- | ----------------------- | --------------------------------------- |
| Ngôn ngữ chủ đạo       | C/C++                   | Python và các ngôn ngữ container hỗ trợ |
| Kiểu ứng dụng          | Native `.eap`           | Container                               |
| Mức độ tích hợp camera | Trực tiếp qua Axis APIs | Qua container và runtime integration    |
| Định hướng hiện tại    | Được Axis khuyến nghị   | Deprecated                              |

Theo tài liệu ACAP 12:

- ACAP Computer Vision solution đã được đánh dấu deprecated.
- Các sản phẩm Axis mới phát hành trên AXIS OS 12.x không có container support.
- Các sản phẩm đã hỗ trợ container từ trước tiếp tục được hỗ trợ đến cuối năm 2031 theo tài liệu hiện tại.
- Axis khuyến nghị sử dụng ACAP Native SDK cho các dự án computer vision và machine learning mới.&#x20;

  [image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

  Axis developer documentation+1



Đây là điều đặc biệt quan trọng với team quen sử dụng Python, OpenCV, PyTorch và Docker runtime.

Nếu định làm sản phẩm lâu dài trên nhiều camera Axis, mình nghiêng về C/C++ ACAP Native SDK thay vì thiết kế sản phẩm phụ thuộc container runtime trên camera.

Ngoài ra, với định hướng AXIS OS 13, Axis đã công bố các thay đổi về application signing, manifest schema và khai báo quyền truy cập DLPU. Ví dụ resource declaration:

```
{
  "deepLearningProcessor": {
    "enabled": true,
    "required": true
  }
}
```

Đây là phần cần tính đến khi chuẩn bị tương thích AXIS OS 13, không nên sao chép độc lập mà bỏ qua schema manifest tương ứng.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation



## 9. Khuyến nghị nếu muốn phát triển custom AI trên Axis

Với mục tiêu nghiên cứu, làm PoC rồi tiến tới production, mình sẽ ưu tiên:

Ưu tiên ARTPEC-8 hoặc ARTPEC-9

Có tài liệu convert TFLite tương đối rõ, có supported ops và code examples chính thức. ARTPEC-9 phù hợp để đánh giá các workload nặng hơn, nhưng vẫn phải benchmark thực tế.

Dùng ACAP Native SDK + Larod

Tránh phụ thuộc vào container support nếu cần duy trì sản phẩm trên các dòng camera mới.

Làm PoC bằng một CNN nhỏ hoặc YOLOv5 tối ưu cho TFLite

Kiểm tra khả năng nạp model bằng `larod-client`, độ chính xác sau quantization, inference latency và CPU utilization trước khi viết toàn bộ ứng dụng.

Cân nhắc kỹ CV25/CV75

Vẫn triển khai custom AI được về mặt nền tảng, nhưng quy trình biên dịch native model yêu cầu Ambarella CNNGen Toolchain không công khai. Đây là rào cản đáng kể cho development độc lập.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.developer.axis.com\&sz=32)

Axis developer documentation+1



### Tài liệu nên đọc tiếp

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

[Axis DLPU — tổng quan phần cứng và SoC](https://developer.axis.com/computer-vision/on-device/axis-dlpu/?utm_source=chatgpt.com)

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

[ACAP Native SDK — tài liệu chính thức](https://developer.axis.com/acap/?utm_source=chatgpt.com)

[image](https://www.google.com/s2/favicons?domain=https://developer.axis.com\&sz=32)

[Run computer vision models inside ACAP applications](https://developer.axis.com/acap/how-to-guides/computer-vision-on-device/?utm_source=chatgpt.com)

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

[Source code mẫu — VDO, Larod, YOLOv5, object detection](https://github.com/AxisCommunications/acap-native-sdk-examples?utm_source=chatgpt.com)

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

[Axis Model Zoo — model và benchmark tham khảo](https://github.com/AxisCommunications/axis-model-zoo?utm_source=chatgpt.com)

## Đánh giá cuối cùng

Axis là nền tảng tương đối mở ở mức phát triển Edge AI application, nhưng vẫn là một hệ sinh thái có kiểm soát ở mức DLPU hardware/runtime.

Nếu mục tiêu là tự phát triển một model object detection, classification hoặc analytics chuyên biệt chạy trực tiếp trong camera, Axis có khả năng đáp ứng. Đặc biệt, ARTPEC-8/9 cùng ACAP Native SDK là hướng đáng thử nghiệm.

Nếu mục tiêu là triển khai tùy ý bất kỳ model ONNX/PyTorch nào, tùy biến accelerator kernel, thay thế AI engine gốc hoặc có quyền kiểm soát sâu tương tự một hệ thống Linux với NPU SDK mở hoàn toàn, thì Axis có những giới hạn đáng kể.

Điều cần kiểm chứng bằng PoC không chỉ là model có load được không, mà còn là bao nhiêu phần trăm phép toán chạy trên DLPU, inference latency, FPS duy trì, RAM, độ trễ do preprocessing/post-processing và tài nguyên còn lại cho chức năng camera. Đây mới là những yếu tố quyết định khả năng triển khai sản phẩm thực tế.