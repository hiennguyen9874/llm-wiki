---
type: Concept
title: "ACAP Runtime Machine learning API: Predict over larod, inputs, outputs and limits"
description: "What the Runtime's TensorFlow-Serving-style inference service really implements: only Predict, the two proto fields added by a patch, the larod load/preprocess/run flow, the three input modes, output construction, Python client helper, and the defects and unsupported features."
tags: [edge-ai, axis, acap, acap-runtime, grpc, tensorflow-serving, larod, inference, tflite]
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
    title: "ACAP Runtime README (§APIs, §Chip id)"
  - id: rt-inference
    resource: ../raw/acap-runtime/src/inference.cpp
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "inference.cpp — Inference service (Predict, LoadModel, preprocessing)"
  - id: rt-patch
    resource: ../raw/acap-runtime/apis/predict_additions.patch
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "predict_additions.patch — stream_id and frame_reference"
  - id: rt-tfutils
    resource: ../raw/acap-runtime/apis/wrappers/tf_proto_utils.py
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "tf_proto_utils.py — Python InferenceClient"
---

# ACAP Runtime Machine learning API: Predict over larod, inputs, outputs and limits

The README calls the Machine learning API "an implementation of TensorFlow Serving".[^rt-readme] In code it is narrower: the class `Inference` derives from `tensorflow::serving::PredictionService::Service` and overrides **only `Predict`**; `GetModelMetadata`, `Classify`, `Regress` and `MultiInference` fall back to the generated base class, which in gRPC returns `UNIMPLEMENTED` (**Observed** override list, **Synthesis** for the base-class behaviour, as the generated header was not read).[^rt-inference] A client sends image bytes as a tensor, the server runs the model through the device's **larod** library on the configured chip, and returns the model's output tensors. It is a single-image, single-input-tensor service, and its limits are the main thing a client author must know.

## Wire contract and the added fields

Protos come from TensorFlow and TensorFlow Serving branch `r2.9`, symlinked into `apis/` at image build time; `apis/predict_additions.patch` is applied to `predict.proto` before compiling the C++ server. It adds exactly two fields:[^rt-patch]

| Message | Field | Meaning |
| --- | --- | --- |
| `PredictRequest` | `uint32 stream_id = 10` | if non-zero, run the prediction on a frame captured from this [video-capture stream](acap-runtime-video-capture-api.md) instead of the input tensors |
| `PredictResponse` | `uint32 frame_reference = 10` | reference to the frame used; usable with `GetFrame` to fetch it |

Neither field is in the README (**Observed**). The service is always registered, even when chip id is 0, in which case every `Predict` returns `CANCELLED` rather than `UNIMPLEMENTED`, contrary to the README's statement that the service "will not be started" ([configuration](acap-runtime-server-configuration-and-security.md)).[^rt-inference]

**Python stubs lack the patch.** `Dockerfile.proto` builds the Python TF protos from stock TF Serving `2.9.0` without applying the patch, so Python clients using the published `-protofiles` image cannot set `stream_id` or read `frame_reference` (**Observed**; see [Build and image packaging](acap-runtime-build-and-image-packaging.md)).

## Flow inside `Predict`

1. **Construction.** If the chip id is 0 or negative the constructor returns without connecting to larod. Otherwise it connects, lists chips for tracing, and loads each `-m` model with `LAROD_ACCESS_PRIVATE`. The in-memory map is keyed by the **full model path**; the larod model name is the basename.[^rt-inference]
2. **Model selection.** `model_spec.name` is looked up in the map; on a miss the same string is **loaded as a filesystem path** with no allow-list. `model_spec.version` is ignored.
3. **Serialisation.** A single `std::mutex` makes the larod calls atomic, because per-request scratch state is kept in members; model lookup and loading happen before the lock, so the model map is unsynchronised (likely data race).
4. **Input** (three modes, picked from the request):
   - `DT_STRING` tensor: `string_val(0)` is a **POSIX shared-memory name**, opened with `shm_open` (zero-copy from the client's side).
   - `stream_id != 0`: the frame is fetched from the capture service and copied to a temporary file (a `TODO` notes the VDO buffer fd could be used directly).
   - otherwise: `tensor_content` bytes are copied to a temporary file. **Other typed fields (`float_val`, `int_val`, …) are ignored**, so a stock TF client that fills them sends an empty input silently.
5. **Preprocessing.** NHWC is assumed. If the request's size and dimensions already equal the model input, the fd is used directly; otherwise a second larod model on `LAROD_CHIP_LIBYUV` is created to convert/scale (input format `nv12` for stream frames, else `rgb-interleaved`; output `rgb-interleaved`). Only tensor `[0]` is wired, so effectively one image input is supported. Dimension count is not checked before reading dims 1 and 2.
6. **Run.** A preprocessing job (if any) then the inference job, via `larodCreateJobRequest` / `larodRunJob`; timings use wall-clock milliseconds and are logged only when verbose.
7. **Output.** One temporary file per output tensor; the response copies each tensor's dtype, dims and bytes into `tensor_content`, keyed by the larod tensor name, with `model_spec` echoed and `version_number` fixed at 0. Dimensions are all appended under the name `size`.[^rt-inference]

Input tensor **names are ignored**: inputs are consumed in map order and assigned by index (only their count is checked); the examples send the key `data`.

## Errors and context

Every failure — no larod connection, null arguments, unknown model, preprocessing or job failure, output parse failure — returns `Status::CANCELLED`; there is no `INVALID_ARGUMENT`, `NOT_FOUND` or `INTERNAL`. The `ServerContext` is discarded, so client deadlines and cancellation do not interrupt a running job.[^rt-inference]

## Python client helper

`apis/wrappers/tf_proto_utils.py` (copied into the protofiles image) gives Python clients `make_tensor_proto`, `make_ndarray`, `build_signature_def`, dtype maps, `RPC_TIMEOUT = 120.0` and `InferenceClient(host, port=0)`. Port 0 means a Unix-socket channel; `infer(inputs, model_name, model_version=None, outputs=[])` returns `(ok, dict)` and swallows exceptions into `(False, {})`. `make_tensor_proto` always writes `tensor_content` and coerces float64 to float32.[^rt-tfutils] Its use in examples is shown in [ML inference and object detection](acap-cv-example-ml-inference-and-object-detection.md) and [Runtime architecture](acap-cv-examples-runtime-architecture.md).

## Defects and limitations (Observed, static)

- `CloseTmpFile` calls `fclose(file)` and then `close(fd)` where `fd` is that file's descriptor: a likely **double close**.
- `response->set_frame_reference(frame_ref)` is called unconditionally while `frame_ref` is only assigned in the stream path: an uninitialised value is returned when `stream_id == 0`.
- A single `pread` per output tensor with no length check; short reads give truncated tensors.
- Shared-memory segments opened with `shm_open` are closed but never `shm_unlink`ed by the server.
- `TfToLarodDataType` and `PrintTensorProtoDebug` are dead code; FLOAT16/FLOAT64 mappings are commented out; the `USE_MEMFD_CREATE` branch is never enabled.
- Preprocessing state for a second preprocessed input overwrites and leaks the first.
- In `tf_proto_utils.py`, `make_ndarray`'s typed-field branch reads `float_val` for every dtype and compares the wrong enum for complex128; bool input is unverified (**Unverified**, numpy absent here).
- Copy-paste error messages in the output path ("Failed retrieving input tensors").
- A client-supplied path can load an arbitrary file as a model.

## Relationships

- **Uses:** larod from the SDK sysroot ([Native SDK API catalog](acap-native-sdk-api-catalog.md) covers the native Machine learning API); chip selection in [Server configuration](acap-runtime-server-configuration-and-security.md).
- **Consumes frames from:** [Video capture API](acap-runtime-video-capture-api.md) through `stream_id`.
- **Tested by:** [Test suite](acap-runtime-test-suite.md) (CPU, DLPU and TPU models, shared-memory and copy inputs).
- **Model constraints:** [DLPU model constraints](axis-dlpu-model-constraints.md) and [Custom model deployment](axis-custom-model-deployment.md) apply to what can be loaded on chip 12.
- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md).

## Evidence class

The service surface, flow and defects are **Observed** by reading `inference.cpp`, the patch and the Python helper. No request was sent; behaviour on a device, including whether the generated base class returns `UNIMPLEMENTED`, is **Unverified**.

[^rt-readme]: `README.md` §APIs (Machine learning API), §Chip id.
[^rt-inference]: `src/inference.cpp::{Inference::Inference (L54-101), Predict (L132-301), LoadModel (L666-707), SetupPreprocessing (L710-870), SetupOutputTensors (L919-951), LarodOutputToPredictResponse (L954-1000), CloseTmpFile (L648-657)}`, `src/inference.h` L23-40, `src/acap_runtime.cpp` L113-119.
[^rt-patch]: `apis/predict_additions.patch` L1-24 (patches `tensorflow_serving/apis/predict.proto`); `Dockerfile` L183-189.
[^rt-tfutils]: `apis/wrappers/tf_proto_utils.py::{make_tensor_proto (L29-38), make_ndarray (L41-92), build_signature_def (L95-105), RPC_TIMEOUT (L144), InferenceClient (L147-173)}`.
