---
type: Concept
title: "ACAP Runtime Video capture API: NewStream, GetFrame and DeleteStream over VDO"
description: "The videocapture.v1 gRPC service: proto messages and enums, how streams are created with libvdo, the live-versus-saved-frame behaviour, the link to the inference API, the Python VideoCaptureClient and the concurrency and leak defects."
tags: [edge-ai, axis, acap, acap-runtime, grpc, vdo, video-capture, protobuf]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: rt-readme
    resource: ../raw/acap-runtime/README.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9 (e375fc9586e270042c9c46dde7645c20761b06bf)"
    title: "ACAP Runtime README (§APIs: Video capture API)"
  - id: rt-capture
    resource: ../raw/acap-runtime/src/video_capture.cpp
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "video_capture.cpp — Capture service"
  - id: rt-videoproto
    resource: ../raw/acap-runtime/apis/videocapture.proto
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "videocapture.proto"
  - id: rt-vdoutils
    resource: ../raw/acap-runtime/apis/wrappers/vdo_proto_utils.py
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "vdo_proto_utils.py — Python VideoCaptureClient"
---

# ACAP Runtime Video capture API: NewStream, GetFrame and DeleteStream over VDO

The README says only that the Video capture API "enables capture of images from a camera" and points at the `object-detector-python` example.[^rt-readme] The code is a thin gRPC wrapper over **VDO** (`vdostream`): a client creates a stream with a format and size, then pulls frames one RPC at a time; there is no push streaming, no channel or rotation control and no snapshot mode. Frames can also be consumed inside the server by the [Machine learning API](acap-runtime-machine-learning-api.md) through `stream_id`.

## Proto contract (`videocapture.v1`)

Three unary RPCs: `NewStream(NewStreamRequest) → NewStreamResponse{stream_id}`, `DeleteStream(DeleteStreamRequest{stream_id}) → empty`, `GetFrame(GetFrameRequest{stream_id, frame_reference}) → GetFrameResponse`.[^rt-videoproto]

- `StreamSettings{format, width, height, framerate, timestamp_type}`.
- `StreamFormat`: `H264=0`, `H265=1`, `JPEG=2`, `YUV=3`, `RGB=8`, `PLANAR_RGB=9` (VDO's `NONE=-1` is omitted because proto3 needs a zero first value; values 4-7 are skipped).
- `TimestampType`: a bit-flag set (NONE up to `MONO_CLIENT_SERVER_DIFF=52`, including the composite values 44 and 52).
- `GetFrameResponse{id, type, size, timestamp, custom_timestamp, sequence_nbr, data}` — `id` is **never set** by the server.

## Server behaviour

`NewStream` builds a `VdoMap` with `format`, `buffer.strategy = VDO_BUFFER_STRATEGY_INFINITE`, `width`, `height` and `framerate` taken directly from the request, creates the stream with `vdo_stream_new`, stores it in a map by `vdo_stream_get_id`, then starts it. `GetFrame` returns the **next live buffer** from `vdo_stream_get_buffer` unless `frame_reference > 0`, in which case it returns one of the saved frames; it copies the bytes into the response and unrefs the buffer.[^rt-capture]

**Saved frames.** Only the inference path (`GetImgDataFromStream`, called from `Predict` when `stream_id` is set) saves frames: it keeps at most `MAX_NBR_SAVED_FRAMES = 3` per stream with FIFO eviction, and returns a frame reference. A client can therefore fetch, with `GetFrame(frame_reference=…)`, one of the last three frames that `Predict` used — exactly what `PredictResponse.frame_reference` is for. Frames fetched by plain `GetFrame` are never saved.[^rt-capture]

`timestamp_type` is declared but never applied (no timestamp key is set on the VDO map), so `custom_timestamp` is whatever VDO defaults to (**Observed**).

Errors: `INTERNAL` for VDO failures (with the `GError` message), `FAILED_PRECONDITION` for an unknown stream and `NOT_FOUND` for an unknown frame reference. Unlike the ML API this uses distinct codes. The request context is unused (no deadline or cancel handling).

## Python helper

`vdo_proto_utils.py::VideoCaptureClient(socket, width, height, framerate)` opens an **insecure** channel, waits `RPC_TIMEOUT = 300` seconds for readiness, creates a stream with `format = YUV` and `timestamp_type = UTC`, and `get_frame()` asks for the latest frame (`frame_reference=0`), reshaping it as **NV12** `(height*1.5, width)` and converting with OpenCV to RGB. It deletes the stream in `__del__`, exits the process with `sys.exit(1)` on connection failure instead of raising, and imports `cv2`/`numpy`, which the protofiles image does not install.[^rt-vdoutils] Examples set their own stream sizes (see [Runtime architecture](acap-cv-examples-runtime-architecture.md) and [QR decoder](acap-cv-example-opencv-qr-decoder.md)). Note the TLS split: the helper is insecure-only, so a Runtime started with TLS cannot serve this client.

## Defects (Observed, static)

- `NewStream`/`DeleteStream` and the stream map are **not locked**; the mutex only guards the saved-frame functions, but gRPC dispatches RPCs on several threads, so concurrent stream creation or deletion races.
- `settingsMap` from `NewStream` is never unreffed (leak per stream).
- `DeleteStream` erases the map entry before stopping and never unrefs saved buffers still queued.
- `PrintStreamInfo` can dereference `error->message` through a `goto` path when both pointers are null.
- `GetTypeString` indexes the VDO enum class values without bounds checks and leaks the type-class reference.
- The frame ID field and the timestamp type are dead.

## Relationships

- **Backed by:** VDO from the Native SDK ([Native SDK API catalog](acap-native-sdk-api-catalog.md); native usage in [VDO capture examples](acap-example-vdo-video-capture-and-opencl.md)).
- **Feeds:** [Machine learning API](acap-runtime-machine-learning-api.md) via `stream_id`.
- **Configured by:** the same server as the other APIs ([Server configuration](acap-runtime-server-configuration-and-security.md)).
- **Untested:** the [test suite](acap-runtime-test-suite.md) passes a stub `Capture`.
- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md).

## Evidence class

All claims are **Observed** from `video_capture.cpp`, `videocapture.proto` and `vdo_proto_utils.py`. No stream was opened; device behaviour, including what VDO does with an unsupported size, is **Unverified**.

[^rt-readme]: `README.md` §APIs (Video capture API); the Python usage example is `object-detector-python` in the CV SDK examples repository.
[^rt-capture]: `src/video_capture.cpp::{NewStream (L40-76), DeleteStream (L79-99), GetFrame (L103-152), GetImgDataFromStream (L161-197), GetDataFromSavedFrame (L210-235), PrintStreamInfo (L236-260), OutputError (L262-281), GetTypeString (L284-291)}`; `src/video_capture.h::{MAX_NBR_SAVED_FRAMES (L86), _mutex (L87), _streams (L84)}`; `src/inference.cpp` L769 (caller).
[^rt-videoproto]: `apis/videocapture.proto` L19-85 (service L21-25, `GetFrameResponse` L32-40, enums L42-63, settings L65-71).
[^rt-vdoutils]: `apis/wrappers/vdo_proto_utils.py::{RPC_TIMEOUT (L9), VideoCaptureClient (L10-68), create_video_stream (L32-42), get_frame (L45-56)}`.
