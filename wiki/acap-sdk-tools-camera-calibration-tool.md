---
type: Concept
title: "ACAP SDK tools: camera-calibration-for-lens-distortion implementation"
description: "How the C++ camera-calibration-for-lens-distortion tool works at git 7250746: AprilGrid detection, OpenCV calibrateCamera with fixed K3 and zero tangential distortion, config.cfg output, Docker build, bundled datasets, and the code defects that limit its reliability."
tags: [edge-ai, axis, acap, computer-vision, calibration, opencv, apriltag, docker, cpp]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-08-31
sources:
  - id: sdk-tools-readme
    resource: ../raw/acap-sdk-tools/README.md
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746d39fb25384402d0f900eb5a6a27c29d69 (2026-08-18)"
    title: "AxisCommunications/acap-sdk-tools — root README (git submodule)"
  - id: ct-readme
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/README.md
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "camera-calibration-for-lens-distortion README"
  - id: ct-main
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/main.cpp
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "main.cpp — grid parameters and entry point"
  - id: ct-calibration
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/src/calibration.cpp
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "src/calibration.cpp — detection, calibrateCamera, validation"
  - id: ct-aprilgrid
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/src/AprilGrid.cpp
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "src/AprilGrid.cpp — object and image point construction"
  - id: ct-writeconfig
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/src/writeconfig.cpp
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "src/writeconfig.cpp — libconfig++ output"
  - id: ct-dockerfile
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/Dockerfile
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Calibration tool Dockerfile"
  - id: ct-cmake
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/CMakeLists-detection.txt
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "CMakeLists-detection.txt — replacement build file for ethzasl_apriltag2 (and the app CMakeLists.txt)"
  - id: ct-config
    resource: ../raw/acap-sdk-tools/camera-calibration-for-lens-distortion/config.cfg
    scope: ../raw/acap-sdk-tools/
    kind: dataset
    revision: "7250746"
    title: "Checked-in example config.cfg"
---

# ACAP SDK tools: camera-calibration-for-lens-distortion implementation

`camera-calibration-for-lens-distortion` is a small C++ program, built and run inside an aarch64 Docker image on the developer machine, that estimates the intrinsic matrix and lens distortion of an Axis camera from a folder of AprilGrid photographs and writes them to `config.cfg`.[^ct-readme] It is one of the two tools in the [acap-sdk-tools repository](acap-sdk-tools-repository.md).[^sdk-tools-readme] The *method* (why calibrate, the three parameter groups, undistortion, RMS validation) is explained in the vendor guide summarised in [Hiệu chỉnh méo ống kính cho camera Axis](axis-camera-calibration.md); this page records what the *code* actually does, which differs from that guide in several places. Everything below is **Observed** by static reading; nothing was built or run.

## Pipeline

1. `main.cpp::main` hard-codes the target: a 6 × 6 `AprilGrid` with `grid_size = 0.024` m, `grid_spacing = 0.696/2.4` (spacing as a fraction of tag size, so 0.29), start ID 0, image folder `../data/aprilgrid_wide`, and `numberofimages = imagesforcalibration = 39`. The program takes no command-line arguments.[^ct-main]
2. `calibration()` loops over image indices, reading `<folder>/img_00000<i>_1_1.jpg` as grayscale, and detects tags with `AprilTags::TagDetector(tagCodes36h11)` from ETH's `ethzasl_apriltag2`. An image is accepted only when it yields more than `rows*columns*4/4 = 36` corner points; the loop stops after 39 accepted images.[^ct-calibration]
3. `AprilGrid::objpoints` builds 3-D corner coordinates on the z = 0 plane from the tag ID: pitch = `size + spacing*size` (0.03096 m), column = `id % columns`, row = `id / columns`, corners pushed in the order top-right, top-left, bottom-left, bottom-right; `imgpoints` returns the matching detected corners, both ordered by ascending tag ID.[^ct-aprilgrid]
4. `cv::calibrateCamera` is called with `flag = CALIB_FIX_K3 + CALIB_ZERO_TANGENT_DIST`, so the result has only `k1`, `k2` free and `p1 = p2 = k3 = 0`.[^ct-calibration]
5. A validation pass re-detects tags in one hard-coded image `img_0000013_1_1.jpg`, projects its object points with the pose of view 13 (`R.row(13)`, `T.row(13)`) and averages the L2 pixel error over each tag's four corners.[^ct-calibration]
6. `writeconfig()` writes `../config.cfg` with libconfig++: `Calibration.Results.Intrinsics{fx,fy,cx,cy}`, `DistortionCoefficients{k1,k2,p1,p2,k3}` and `Validation{ReprojectionError, ErrorForTag0…N}`.[^ct-writeconfig]

The checked-in `config.cfg` shows the format: `fx≈1036.1`, `fy≈1037.1`, `cx≈333.2`, `cy≈217.2`, `k1≈-0.4195`, `k2≈0.4031`, `p1 = p2 = k3 = 0.0`, `ReprojectionError≈1.0988` and 36 per-tag errors (e.g. tag 1 ≈ 2.76 px).[^ct-config] The zero `p1/p2/k3` agree with the flags above.

## Build and run

The documented procedure is `docker build -t <APP_IMAGE> .`, `docker run -it --name <APP_CONTAINER> <APP_IMAGE>`, then `docker cp <APP_CONTAINER>:/app/config.cfg .`; it requires Docker 20.10.14 or newer and warns about a platform mismatch on non-arm64 hosts. The README states that the datasets were captured with a Q1656 and gives RMS 0.9 px (wide) and 1.1 px (tele) for the two bundled sets (**Reported**).[^ct-readme]

The `Dockerfile` does the following:[^ct-dockerfile]

- Takes OpenCV, Python, NumPy and OpenBLAS trees from `axisecp/acap-computer-vision-sdk:latest-aarch64-devel` into an `arm64v8/ubuntu:20.04` runtime image (the SDK tag is unpinned).
- Installs `make git cmake g++-10 gcc libeigen3-dev libconfig++-dev build-essential`, sets `CXX=g++-10`.
- Clones `https://github.com/ethz-asl/ethzasl_apriltag2.git` (unpinned default branch) with `GIT_SSL_NO_VERIFY=1`, overwrites its `CMakeLists.txt` with the local `CMakeLists-detection.txt`, then builds and installs it.
- Builds the application (`cmake .. && make` in `/app/build`) and sets `CMD ["./main"]`, so the paths `../data/...` and `../config.cfg` are relative to `/app/build`.

`CMakeLists-detection.txt` exists because the upstream package is a ROS/catkin project: the replacement builds `src/*.cc` as a shared library (`-fPIC -O3 -Werror`, version 0.0.1), links Threads, OpenCV and Eigen, and installs an exported CMake config so that the application's `find_package(ethzasl_apriltag2 REQUIRED CONFIG)` resolves from `/usr/local`.[^ct-cmake]

## Datasets

`data/aprilgrid_wide/` and `data/aprilgrid_tele/` each hold 40 JPEGs named `img_000000_1_1.jpg` to `img_0000039_1_1.jpg`; a sampled file is 640×480. `main.cpp` asks for 39, so index 39 is never used. The two SVGs (`calibration_diagram.svg`, `distortion.svg`) are README illustrations; `distortion.svg` (≈650 KB) is a diagram export with embedded rasters and no extractable text.[^ct-readme]

## Defects and documentation gaps

All **Observed** unless marked *Synthesis*.

| Finding | Locator | Consequence |
| --- | --- | --- |
| `calibrateCamera` receives `cv::Size(Grid.rows, Grid.columns)` = 6×6 as the image size | `calibration.cpp::calibration` | The image size is the wrong object (the photos are 640×480); the principal-point initialisation uses it (*Synthesis*: OpenCV uses `imageSize` to initialise the intrinsics). The fitted `cx≈333, cy≈217` still look plausible for 640×480 |
| Validation image 13 is also in the calibration set, and its pose is read as `R.row(13)` | `calibration.cpp`, validation block | The error is in-sample, and row 13 is the 14th *accepted* view, not necessarily image 13 (*Synthesis*: they coincide only if images 0–13 were all accepted) |
| Per-tag error indexes points by detection index `4*j` while the point arrays are ordered by tag ID | `calibration.cpp`, validation loop; `AprilGrid.cpp` | `ErrorForTagN` labels can belong to a different tag when detections are unsorted or tags are missing (*Synthesis*) |
| Image names are built as `"img_00000" + i + "_1_1.jpg"`; `imread` results are not checked; the loop ends only after 39 acceptances | `calibration.cpp` | Only that naming scheme (i < 100) works; fewer than 39 usable images loops forever or passes empty images to the detector; the README says the file "collects each image from the captured dataset" |
| The distortion writer loops `i < distortion.cols` over a five-name vector | `writeconfig.cpp` | A rational or thin-prism model (more than 5 coefficients) would overrun the vector; a 5×1 layout would write only `k1` |
| `main.cpp` defaults to `aprilgrid_wide`, but the checked-in `config.cfg` has `ReprojectionError≈1.10`, matching the README's *tele* figure (1.1) rather than wide (0.9) | `main.cpp`, `config.cfg`, README table | The shipped example output was produced from different settings than the shipped defaults (*Synthesis*) |
| The `totalnumberofimages` parameter is unused; the detected-ID matrix is built but never written | `calibration.cpp`, `writeconfig.cpp` | Dead code |
| Dead build `ARG`s before `FROM`, so `DEBIAN_FRONTEND` does not apply to the tzdata step; `GIT_SSL_NO_VERIFY=1`; unpinned base tag and git clone; a trailing space after `\` on one `RUN` line | `Dockerfile` | Non-reproducible builds and disabled TLS verification when cloning the detector |
| README tree names `aprilgird_wide`, `CMakelists.txt` and `CMakelists-detection.txt` | `README.md::Structure of this tool` | Typos; real names are `aprilgrid_wide`, `CMakeLists.txt`, `CMakeLists-detection.txt`. The vendor guide also names `src/AprilGrid.cc`, but the file is `AprilGrid.cpp` |
| Both CMake files carry leftovers: duplicate `find_package(OpenCV)`, undefined `${catkin_LIBRARIES}`, unused `DEFAULT_BUILD_TYPE`, duplicated `target_link_libraries` | `CMakeLists-detection.txt`, `CMakeLists.txt` | Harmless noise |

The vendor guide recommends at least 10 sample images and a configurable `threshold`; the code instead requires 39 accepted images and fixes the threshold at 36 corner points (a quarter of the 144 grid corners).[^ct-calibration][^ct-readme]

## Coverage and limits

- Inspected: root and tool READMEs, `main.cpp`, the three headers' public interface, the three `src/*.cpp` files, both Dockerfile and CMake inputs, `config.cfg`, the two SVG diagrams (the larger only structurally) and the image folders (counted, one file's dimensions checked).
- Not inspected: individual JPEG contents, the AprilGrid in the images, the upstream `ethzasl_apriltag2` source, the CV SDK image, and any runtime output; the RMS values and the `config.cfg` provenance are therefore **Reported**/unverified, and no claim here is **Reproduced**.
- Checksums and image-level duplication between the wide and tele sets were not recorded in the wiki.

## Relationships

- **Implements** the procedure described in [Hiệu chỉnh méo ống kính cho camera Axis](axis-camera-calibration.md); that page's coverage note on this code is superseded by this one.
- **Part of** [ACAP SDK tools repository](acap-sdk-tools-repository.md); built and checked by the workflow in [ACAP SDK tools CI and maintenance](acap-sdk-tools-ci-and-maintenance.md).
- **Uses** the ACAP Computer Vision SDK image described in the [CV SDK examples repository](acap-cv-sdk-examples-repository.md), which is archived upstream; the unpinned `latest-aarch64-devel` tag is a maintenance risk. (*Synthesis*)
- **Distinct from** [the AWS training tool](acap-sdk-tools-aws-training-tool.md): both run from a Docker image on the developer machine, but neither depends on the other.

[^sdk-tools-readme]: Root README, §Tools (list of the two tools); revision 7250746.
[^ct-readme]: Tool README: intro, §Requirements, §Structure of this tool, §Quicksteps steps 1–6, §Validation results table; `data/` listing.
[^ct-main]: `camera-calibration-for-lens-distortion/main.cpp::main`, lines 6–23.
[^ct-calibration]: `src/calibration.cpp::calibration`, lines 23–119 (loop 30–52, threshold 42–44, `calibrateCamera` 55–58, validation 64–108).
[^ct-aprilgrid]: `src/AprilGrid.cpp::AprilGrid::imgpoints` and `::objpoints`; class fields in `include/AprilGrid.hpp`.
[^ct-writeconfig]: `src/writeconfig.cpp::writeconfig`, lines 25–78 (output path `../config.cfg`, `distNames`, `ErrorForTag*` loop).
[^ct-dockerfile]: `camera-calibration-for-lens-distortion/Dockerfile`: `FROM` lines, apt block, `GIT_SSL_NO_VERIFY`, `git clone`, `CMD`.
[^ct-cmake]: `CMakeLists-detection.txt` lines 1–43; the application `CMakeLists.txt` lines 6–20 (`find_package(ethzasl_apriltag2 REQUIRED CONFIG)`).
[^ct-config]: `config.cfg`, keys `Calibration.Results.Intrinsics`, `.DistortionCoefficients`, `.Validation`.
