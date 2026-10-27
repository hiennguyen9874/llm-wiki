---
type: Concept
title: "Hiệu chỉnh méo ống kính cho camera Axis"
description: "Quy trình hiệu chỉnh méo hình ảnh camera Axis bằng AprilTag grid và OpenCV: ba nhóm tham số, pipeline calibrateCamera, làm thẳng bằng undistort, và kiểm chứng bằng lỗi tái chiếu RMS."
tags: [edge-ai, axis, acap, computer-vision, calibration]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-camera-calibration
    resource: ../raw/acap/how-to-guides/camera-calibration/index.md
    scope: ../raw/acap/how-to-guides/camera-calibration/
    kind: docs
    revision: "ACAP version 12"
    title: "Camera calibration | Axis developer documentation"
---

# Hiệu chỉnh méo ống kính cho camera Axis

Camera Axis ưu tiên quan sát rộng hơn là ảnh rectilinear, nên ảnh thường bị méo rõ ở vùng biên; méo này làm khó việc phát hiện vật thể hoặc đo khoảng cách. Cách khắc phục của Axis là hiệu chỉnh bằng một bảng **AprilTag grid** đã in, chụp nhiều ảnh mẫu ở các vị trí và hướng khác nhau, rồi để OpenCV `cv::calibrateCamera()` ước lượng bộ tham số và lưu vào `config.cfg`. Ảnh sau đó được làm thẳng bằng `cv::undistort()`, và chất lượng được kiểm chứng bằng lỗi tái chiếu RMS — tổng thể và theo từng tag. Toàn bộ công cụ nằm trong repository `acap-sdk-tools` và chạy trong Docker trên máy phát triển, không chạy trên camera.[^axis-camera-calibration]

## Ba nhóm tham số

| Nhóm | Định nghĩa theo hướng dẫn |
| --- | --- |
| Distortion coefficients | Méo do camera pinhole gây ra (radial và tangential) |
| Intrinsic camera parameters | Méo do ống kính gây ra: focal length, optical centers |
| Extrinsic parameters | Quan hệ giữa thế giới thực và ảnh: translation hoặc rotation |

Phải tìm đủ cả ba nhóm để lập được ánh xạ giữa thế giới thực và mặt phẳng ảnh. Cách làm là dựng một setup có các điểm đã biết ở cả hai phía: **object points** trong thế giới thực và **image points** trên ảnh. Pattern in sẵn (bàn cờ hoặc lưới MxN AprilTag) là cách dễ nhất để có đồng thời cả hai.[^axis-camera-calibration]

## Quy trình

1. Tạo và in AprilTag grid, ví dụ bằng công cụ của ETH:[^axis-camera-calibration]

   ```bash
   kalibr_create_target_pdf --type apriltag --nx <NUM_COLS> --ny <NUM_ROWS> --tsize <TAG_WIDTH_M> --tspace <TAG_SPACING_PERCENT>
   ```

   Tham số gồm số cột, số hàng, kích thước mỗi tag tính bằng mét (`TAG_WIDTH_M`) và tỉ lệ khoảng cách/kích thước giữa các tag (`TAG_SPACING_PERCENT`); nhờ đó grid được cá nhân hóa theo độ phân giải chụp.

2. Chụp ảnh mẫu: hướng camera vào grid ở nhiều vị trí và hướng khác nhau, **ít nhất 10 ảnh**. Pattern phải phủ vùng méo của khung hình — đặc biệt là các góc.
3. Sửa tham số pattern và đường dẫn thư mục ảnh trong `main.cpp`.
4. Build Docker image:[^axis-camera-calibration]

   ```sh
   docker build . -t <APP_IMAGE>
   ```

5. Chạy container; code hiệu chỉnh tự chạy và ghi tham số ước lượng vào `config.cfg`:[^axis-camera-calibration]

   ```sh
   docker run -it --name <APP_CONTAINER> <APP_IMAGE>
   ```

6. Copy kết quả ra máy host:[^axis-camera-calibration]

   ```sh
   docker cp calibration:/app/config.cfg .
   ```

`main.cpp` là entry point: đặt tham số pattern, gọi `calibration()`, rồi ghi kết quả bằng `writeconfig()`.[^axis-camera-calibration]

## Pipeline hiệu chỉnh

Với mỗi ảnh mẫu, ba bước đầu là: đọc ảnh; phát hiện AprilTag để lấy vị trí 4 góc và ID của tag; tính image points và object points. Một ảnh chỉ được dùng nếu số tag phát hiện đủ ngưỡng tham số `threshold`. Object points lấy từ hàm `objpoints()` trong `src/AprilGrid.cc`, dựa trên tham số dùng để tạo pattern; nhờ ID của tag mà object points được ánh xạ đúng.[^axis-camera-calibration]

Thuật toán phát hiện tag là AprilTag detection phát triển tại MIT và được ETH Zurich chuyển thể (`ethzasl_apriltag2`). Với object points, dùng grid là cách thông thường; với AprilTag grid thì object points suy ra được từ tham số pattern.[^axis-camera-calibration]

Khi đã có đủ điểm, `cv::calibrateCamera()` ước lượng camera matrix (intrinsic), distortion coefficients, và extrinsic (rotation và translation vector) cho từng ảnh. Hàm chạy lặp để cực tiểu hóa lỗi tái chiếu và trả về **RMS re-projection error** tổng thể.[^axis-camera-calibration]

Hai lỗi thường gặp và cách xử lý theo hướng dẫn:[^axis-camera-calibration]

| Triệu chứng | Nguyên nhân | Cách xử lý |
| --- | --- | --- |
| Lỗi cao hơn mong đợi | Chất lượng hoặc số lượng ảnh mẫu chưa đủ | Chụp thêm, cho pattern phủ các vùng méo mạnh (góc) |
| Overfitting | Quá nhiều ảnh giống nhau | Đa dạng vị trí và hướng chụp |

## Làm thẳng ảnh

Sau khi có tham số, làm thẳng bằng `cv::undistort()`. Có thể tinh chỉnh camera matrix bằng `cv::getOptimalNewCameraMatrix()` với tham số `alpha` để điều chỉnh mức scale của phép làm thẳng; bước này **không bắt buộc**.[^axis-camera-calibration]

```cpp
new_camera_mat = cv::getOptimalNewCameraMatrix(camera_mat, distortion_coeff, cv::Size(Grid.rows,Grid.columns), alpha);
cv::undistort(sample_im, output_im, camera_mat, distortion_coeff, new_camera_mat);
```

## Kiểm chứng

RMS re-projection error của `cv::calibrateCamera()` là tổng bình phương khoảng cách giữa image points và image points ước lượng (object points được chiếu lên mặt phẳng ảnh bằng tham số ước lượng); giá trị này tóm tắt số pixel sai lệch nhưng không chỉ ra lỗi nằm ở đâu.[^axis-camera-calibration]

Để biết vùng nào còn méo, tính lỗi riêng cho từng tag bằng `cv::projectPoints()`, với đầu vào là object points và bộ tham số ước lượng (rotation matrix, translation matrix, camera matrix, distortion coefficients). Mỗi tag có 4 điểm, tương ứng 4 góc.[^axis-camera-calibration]

Kết quả RMS tổng thể do Axis công bố, ảnh chụp với cấu hình quang học mặc định và lấy nét tự động (autofocus) trước ảnh đầu tiên:[^axis-camera-calibration]

| Camera | Wide (không zoom) | Tele (zoom tối đa) |
| --- | --- | --- |
| Q1656 | 0.9 px | 1.1 px |

Bảng chỉ có một dòng cho một model, nên không đủ để suy ra sai số kỳ vọng cho dòng camera hay tiêu cự khác.

## Độ phủ nguồn

- Entry point: `raw/acap/how-to-guides/camera-calibration/index.md` (1005 từ), site `developer.axis.com`, bộ ACAP 12, tiếng Anh. Đây là file duy nhất trong scope; không có hình ảnh hay tệp đính kèm, đã đọc toàn bộ trang.
- Code trong nguồn chỉ là đoạn trích `cv::getOptimalNewCameraMatrix()`/`cv::undistort()`. Phần implementation (`main.cpp`, `src/AprilGrid.cpp`, `Dockerfile`, `config.cfg`, `data/`) nay đã được đọc tĩnh trong repository `raw/acap-sdk-tools/` và ghi ở [ACAP SDK tools: implementation của camera-calibration-for-lens-distortion](acap-sdk-tools-camera-calibration-tool.md). Code lệch hướng dẫn ở vài điểm: file thật là `AprilGrid.cpp` (hướng dẫn ghi `.cc`); code đòi đúng 39 ảnh được chấp nhận và ngưỡng cố định 36 góc, thay vì "ít nhất 10 ảnh" và `threshold` tùy chỉnh; `calibrateCamera` nhận kích thước ảnh sai (6×6) và bước kiểm chứng là in-sample. Chưa build hay chạy gì.
- Liên kết ngoài chưa có trong `raw/`: `acap-sdk-tools` (GitHub), công cụ tạo target của kalibr (ETH), AprilTag của University of Michigan, `ethzasl_apriltag2`.
- Trang không nêu phiên bản OpenCV, không nêu camera/ống kính nào khác ngoài Q1656, không mô tả ảnh hưởng của zoom hoặc thay đổi tiêu cự lên bộ tham số đã hiệu chỉnh, và không nói tham số có hiệu lực lại sau khi nâng cấp AXIS OS hay không.
- Giấy phép: thư viện C++ AprilTags là open source theo GNU LGPL 2.1; giấy phép của `acap-sdk-tools` không được nêu trong trang.

## Độ tin cậy

Toàn bộ nội dung là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12), đọc ngày 2026-10-27. Không có claim nào **Reproduced**: không build Docker image, không chạy hiệu chỉnh, không đo lại RMS trên ảnh thật trong lần ingest này.

## Relationships

- **Feeds** [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md): ảnh đã làm thẳng là bước tiền xử lý cho detection và đo khoảng cách, hai việc mà méo biên ảnh gây khó. (Synthesis)
- **Implemented by** [ACAP SDK tools: camera-calibration-for-lens-distortion implementation](acap-sdk-tools-camera-calibration-tool.md) trong [repository acap-sdk-tools](acap-sdk-tools-repository.md); xem trang đó cho các lỗi code và lệch tài liệu. (Observed)
- **Uses** [Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers](acap-dev-environment-setup.md): cùng mô hình build trong Docker trên máy phát triển; OpenCV được thêm vào image bằng `RUN` trong `Dockerfile`.
- **Distinct from** [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): công cụ hiệu chỉnh nằm ở repository `acap-sdk-tools`, không phải `acap-native-sdk-examples`, và chạy ngoài camera chứ không phải một ACAP application đóng gói `.eap`.
- **Related to** [Chuẩn bị thiết bị Axis cho phát triển ACAP](axis-device-setup.md): kết quả phụ thuộc cấu hình quang học của thiết bị (autofocus, zoom) tại thời điểm chụp ảnh mẫu.

[^axis-camera-calibration]: Tài liệu chính thức: [Camera calibration — Axis developer documentation](../raw/acap/how-to-guides/camera-calibration/index.md), toàn bộ trang: §Quickstart, §Calibration procedure (§Straightening), §Validation procedure (§Validation results), §License.
