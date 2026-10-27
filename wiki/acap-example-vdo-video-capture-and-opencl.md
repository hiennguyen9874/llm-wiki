---
type: Concept
title: "ACAP examples: VDO frame capture (vdostream) and OpenCL Sobel filtering"
description: "How the vdostream and vdo-opencl-filtering examples fetch frames from the VDO service: formats, manifest variants per format, stream and snapshot flow, the zero-copy OpenCL Sobel pipeline, constants, and the code defects found."
tags: [edge-ai, axis, acap, examples, vdo, video, opencl]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP examples: VDO frame capture (vdostream) and OpenCL Sobel filtering

Two examples show how a native ACAP application reads video from the Video capture API (VDO): `vdostream` captures frames or a single snapshot in a chosen format and logs their metadata, and `vdo-opencl-filtering` takes NV12 frames and runs a GPU Sobel filter on them through OpenCL without copying input buffers.[^native-examples] Both use the common build recipe in [shared build conventions](acap-examples-build-and-manifest-conventions.md). The inference examples that also use VDO are in [Larod inference examples](acap-example-larod-object-detection.md).

## vdostream

- **Library and calls** (`vdostream/app/Makefile`, `app/vdoencodeclient.c`): pkg-config `gio-2.0 gio-unix-2.0 vdostream`; `vdo_map_*` to build settings, `vdo_stream_new/get_info/start`, `vdo_stream_get_buffer`, `vdo_stream_snapshot`, `vdo_buffer_get_frame`, `vdo_frame_take_chunk`, `vdo_error_is_expected`.
- **Options:** `--format/-t` (default `h264`), `--frames/-n` (default `G_MAXUINT`), `--output/-o` (default `/dev/null`); resolution is hard-coded `640x360` and `frame.chunks=true`.
- **Format mapping:** `av1`, `avif`, `h264`, `h265`, `jpeg` map to matching `VDO_FORMAT_*`; `nv12` and `y800` are `VDO_FORMAT_YUV` with subformat `NV12`/`Y800`; `rgb` is `VDO_FORMAT_RGB`; anything else panics.
- **Flow:** with `--frames 1` it calls `vdo_stream_snapshot` once (this is how `avif` works); otherwise it creates and starts a stream, logs `Starting stream: <fmt>, WxH, N fps`, then loops `frames` times retrying on `VDO_ERROR_NO_DATA`, writing each frame (single contiguous chunk or drained chunks) and unreffing the buffer. A SIGINT handler stops the loop; an "expected" VDO error (maintenance/rotation) exits with success.
- **Manifest variants:** eight `app/manifest.json.<format>` files, selected by `ARG VDO_FORMAT` in the Dockerfile; each sets `appName: vdoencodeclient`, a per-format `friendlyName`, `runOptions: --format <fmt> --frames 25` (`avif` uses `--frames 1`), and `linux.user.groups: ["video"]`. CI builds h264, h265, y800, jpeg and nv12 on both architectures and av1/avif/rgb on `aarch64` only (av1/avif tagged ARTPEC-9, rgb also CV25).
- **Expected frame sizes (README, 640x360):** nv12 345600 bytes, y800 230400, rgb 691200; H.264 shows `type = I` first-frame lines.[^native-examples]

**Observed defects.** The README `avif` sample prints `640x360`, but the code reads `width`/`height` keys that `main` never sets (it sets `resolution`), so the log may print `0x0`; `vdo_buffer_is_contiguous` is passed a `VdoFrame*`; `--frames 0` silently does nothing; the `jpeg` manifest alone lacks the `video` group; `clean` deletes the generated `manifest.json`.

## vdo-opencl-filtering

- **Purpose:** NV12 capture plus GPU Sobel with zero-copy mapping. `Makefile` uses `gio-unix-2.0 glib-2.0 opencl vdostream`; the Dockerfile packages the kernel with `acap-build . -a 'sobel_nv12.cl'`. The manifest requests `groups: ["gpu","video"]`, `appName: vdo_cl_filter_demo`.
- **VDO setup** (`app/vdo_cl_filter_demo.c`): format YUV, subformat `NV12`, 1280x720, `buffer.count` 3, then `vdo_stream_new` → `vdo_stream_attach` → `vdo_stream_get_info` → `vdo_stream_start`.
- **OpenCL setup:** `clGetPlatformIDs`, `clGetDeviceIDs(CL_DEVICE_TYPE_DEFAULT)`, `clCreateContext`, program source read from the hard-coded `/usr/local/packages/vdo_cl_filter_demo/sobel_nv12.cl` (1 MiB cap), kernel `sobel_3x3`, command queue. Global work size is `{height, width/8}` for the full area or `{height, width/16}` for the half-area mode (default `HALF_AREA`).
- **Per frame:** map the VDO buffer into a `cl_mem` with `CL_MEM_USE_HOST_PTR` (a hash table caches one mapping per VDO buffer address, capped at the buffer count), create Y and CbCr sub-buffers of the output, run the kernel with local size `{8,4}` and offset `{1,0}`, `clFinish`, then write the frame to the output file. Five frames are processed; output is binary NV12 at `/usr/local/packages/vdo_cl_filter_demo/localdata/cl_vdo_demo.yuv`.
- **Kernel** (`app/sobel_nv12.cl`): `sobel_3x1` and `sobel_3x3` handle 8 luma pixels per work item via `vload16`/`vstore8`, write CbCr as 128 (greyscale), and clamp magnitude to 1..255.[^native-examples]

**Observed defects.** The last row reads and writes up to 15 bytes beyond the Y plane; the first `clCreateSubBuffer` result is overwritten before it is checked; frame size comes from `vdo_frame_get_size` instead of the computed Y+CbCr size; the `framerate` is read with the unsigned reader on a double-valued field and likely logs `0 fps`; failure messages are labelled `vdo-encode-client`; the cleanup path unmaps and frees OpenCL handles even if OpenCL never initialised; `localdata` is not declared in the manifest.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Uses** the VDO API listed in [Native SDK API catalog](acap-native-sdk-api-catalog.md).
- **Feeds** the same capture pattern into [using-opencv](acap-example-bundled-libraries-opencv-curl-openssl.md) (Y800 frames) and [Larod inference](acap-example-larod-object-detection.md) (model-sized frames).

[^native-examples]: `vdostream/app/vdoencodeclient.c::main, save_frame_to_file, handle_vdo_failed`; `vdostream/Dockerfile:8-15`; `vdostream/app/manifest.json.*`; `vdostream/README.md` output sections; `.github/workflows/vdostream.yml`; `vdo-opencl-filtering/app/vdo_cl_filter_demo.c::setup_opencl, create_cl_program, map_input_buffer, do_opencl_filtering`; `vdo-opencl-filtering/app/sobel_nv12.cl`; `vdo-opencl-filtering/app/manifest.json`.
