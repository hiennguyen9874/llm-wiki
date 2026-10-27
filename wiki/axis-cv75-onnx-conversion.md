---
type: Concept
title: "Chuyển model ONNX sang định dạng native cho CV75"
description: "Quy trình CNNGen để chuyển .onnx sang .bin chạy trên DLPU CV75: thu thập ảnh đại diện, tạo danh sách ảnh lượng tử hóa, parse ONNX, biên dịch VAS và sinh model."
tags: [edge-ai, axis, cv75, model-conversion]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T06:00:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-doc-onnx-to-cv75
    resource: ../raw/computer-vision/on-device/how-to-guides/onnx-to-cv75/index.md
    scope: ../raw/computer-vision/on-device/how-to-guides/onnx-to-cv75/
    kind: docs
    title: "onnx-to-cv75 — Axis developer documentation"
  - id: axis-doc-cv75-model-conversion
    resource: ../raw/computer-vision/on-device/system-on-chip/cv75/model-conversion/index.md
    scope: ../raw/computer-vision/on-device/system-on-chip/cv75/model-conversion/
    kind: docs
    title: "Model Conversion (CV75) — Axis developer documentation"
---

# Chuyển model ONNX sang định dạng native cho CV75

Guide của Axis mô tả đường chuyển đổi `.onnx` → `my_model_cv75.bin` cho các thiết bị dùng SoC CV75, thực hiện bên trong container của CNNGen Toolchain. Đây là nhánh CV75 của bảng đường chuyển đổi theo SoC trong [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md); guide lưu ý phải sửa các bước theo từng model, nên script bên dưới là mẫu chứ không phải quy trình chạy nguyên trạng cho mọi model.[^axis-doc-onnx-to-cv75]

Trang SoC CV75 của Axis xác nhận cùng đường đi ở mức cao hơn và bổ sung hai điểm mà guide không nêu: CNNGen Toolchain không công khai nên phải liên hệ trực tiếp Ambarella để lấy quyền truy cập, và model `.bin` sau khi sinh được chạy thử bằng `larod-client` với channel `cv75-dlpu-native`.[^axis-doc-cv75-model-conversion]

```bash
larod-client -g <my-model>.bin -c cv75-dlpu-native -i ""
```

Đây mới là bước kiểm tra model nạp được; nó không thay thế việc đóng gói vào ACAP application.

## Điều kiện đầu vào

- Model nguồn ở định dạng `.onnx`.
- Một bộ ảnh đại diện cho cảnh model sẽ gặp khi chạy trên camera, đặt trong một thư mục như `./representative_images`.
- Quyền truy cập CNNGen Toolchain và container của nó.
- Kích thước ảnh đầu vào khớp với model; ví dụ trong guide dùng `224 × 224`.[^axis-doc-onnx-to-cv75]

Guide khuyến nghị khoảng 100–200 ảnh đa dạng để có kết quả tốt nhất; dùng ít ảnh hơn vẫn được nhưng có nguy cơ model chạy kém hơn sau lượng tử hóa.[^axis-doc-onnx-to-cv75]

## Script mẫu

Chạy trong container CNNGen, sau khi sửa các biến và tham số theo model:[^axis-doc-onnx-to-cv75]

```bash
#!/bin/bash
INPUT_MODEL=my_model.onnx
OUTPUT_MODEL=my_model_cv75.bin
IMAGE_SIZE=(224 224)
image_height=${IMAGE_SIZE[0]}
image_width=${IMAGE_SIZE[1]}

gen_image_list.py -f ./representative_images -o img_list.txt -ns -e .jpg -c 0 -d 0,0 \
  -r $image_height,$image_width -bf dra_image_bin -bo dra_image_bin/dra_bin_list.txt

onnxparser.py -m $INPUT_MODEL \
  -isrc "is:1,3,$image_height,$image_width|iq|idf:0,0,8,0|i:images=dra_image_bin/dra_bin_list.txt" \
  -o quantized -of quantized -odst "o:output0|odf:fp32"

vas -auto -show-progress quantized/quantized.vas

cavalry_gen -d vas_output/ -f $OUTPUT_MODEL
```

## Vai trò từng bước

| Bước | Đầu vào / đầu ra quan sát được | Vai trò |
| --- | --- | --- |
| `gen_image_list.py` | `./representative_images` → `img_list.txt`, `dra_image_bin/`, `dra_image_bin/dra_bin_list.txt` | Lập danh sách ảnh và tạo ảnh nhị phân để dùng cho lượng tử hóa; `-r` đặt kích thước ảnh theo `IMAGE_SIZE`, `-e .jpg` lọc ảnh JPEG. |
| `onnxparser.py` | `INPUT_MODEL` + danh sách ảnh → thư mục `quantized/` và `quantized/quantized.vas` | Parse ONNX, khai báo input `1×3×H×W`, dùng ảnh đại diện cho bước lượng tử hóa, và khai báo output `output0` ở định dạng `fp32`. |
| `vas` | `quantized/quantized.vas` → `vas_output/` | Biên dịch/tối ưu graph VAS với chế độ `-auto`. |
| `cavalry_gen` | `vas_output/` → `OUTPUT_MODEL` | Sinh model native `.bin` cho CV75. |

Các kết luận về vai trò từng lệnh là **Synthesis** từ tên lệnh, tham số và tên file mà script tạo ra; guide không giải thích chi tiết ngữ nghĩa của từng flag.[^axis-doc-onnx-to-cv75]

## Phải sửa theo model

- `INPUT_MODEL` và `OUTPUT_MODEL`: tên model nguồn và đích.
- `IMAGE_SIZE`: phải khớp kích thước input mà model mong đợi; `224 × 224` chỉ là ví dụ.
- `output0`: tên output trong `-odst` phải là tên tensor output thực tế của model.
- `-e .jpg`: chỉ nhận ảnh `.jpg`; đổi nếu bộ ảnh dùng định dạng khác.
- Các flag số như `-c 0`, `-d 0,0`, `idf:0,0,8,0` và `odf:fp32` là giá trị mẫu; guide không định nghĩa chúng, nên phải đối chiếu tài liệu và ví dụ của CNNGen trước khi dùng cho model khác.[^axis-doc-onnx-to-cv75]

## Giới hạn coverage

Guide dừng ở việc sinh file `.bin`; trang SoC CV75 chỉ bổ sung lệnh chạy thử, không nêu cách nạp model vào ACAP application hay cách đóng gói `.eap`. Các bước đó thuộc [quy trình triển khai](axis-custom-model-deployment.md) và vẫn chưa được kiểm chứng trong các lần ingest này. Các hướng dẫn PyTorch/TensorFlow-to-ONNX, tài liệu Ambarella và trang `test-your-model` không có cục bộ, nên ngữ nghĩa các flag của CNNGen và cách truyền input vẫn là khoảng trống.[^axis-doc-onnx-to-cv75][^axis-doc-cv75-model-conversion]

## Relationships

- **Part of** [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md), nhánh CV75.
- **Contrasts with** [Chuyển model sang ARTPEC-9](axis-artpec-9-model-conversion.md): ARTPEC-9 dùng thẳng `.tflite`, không cần toolchain của hãng thứ ba.
- **Depends on** [Axis DLPU](axis-dlpu.md): CV75 là một trong năm SoC có DLPU.
- **Requires** Ambarella CNNGen Toolchain (chưa có concept riêng).
- **Constrained by** [giới hạn model trên DLPU](axis-dlpu-model-constraints.md), đặc biệt quantization và operator.
- **Informs** [Hướng triển khai custom AI trên Axis](axis-edge-ai-adoption-guide.md) về chi phí thực tế của nhánh CV75.

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ hướng dẫn vendor và được **Observed** bằng static inspection của trang và script; trang SoC CV75 xác nhận lại đường đi và lệnh chạy thử nhưng không giải thích thêm flag nào. Chưa **Reproduced** vì không có CNNGen Toolchain trong môi trường này. Trang để `status: draft` vì ngữ nghĩa các flag, cấu trúc `vas_output/` và tên tensor `output0` vẫn cần đối chiếu tài liệu Ambarella hoặc chạy thử trên model thật trước khi coi là quy trình hoàn chỉnh.

[^axis-doc-onnx-to-cv75]: Tài liệu chính thức: [onnx-to-cv75 — Axis developer documentation](../raw/computer-vision/on-device/how-to-guides/onnx-to-cv75/index.md), §Steps: bước 1 (ảnh đại diện) và bước 2 (khối script bash với `gen_image_list.py`, `onnxparser.py`, `vas`, `cavalry_gen`).
[^axis-doc-cv75-model-conversion]: Tài liệu chính thức: [Model Conversion (CV75) — Axis developer documentation](../raw/computer-vision/on-device/system-on-chip/cv75/model-conversion/index.md), §How to accelerate your model on CV75, bước 1–4 (export `.onnx`, CNNGen không công khai, lệnh `larod-client -c cv75-dlpu-native`) và hình "DLPU Conversion Schematic" (`assets/convert-flowchart-cv75-455326d49bb064c189626efd3f0d4995.png`).
