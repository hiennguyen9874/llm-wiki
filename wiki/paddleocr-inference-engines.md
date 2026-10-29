---
type: Concept
title: PaddleOCR inference engines
description: PaddleOCR configures PaddleX inference engines, automatic high-performance backends, and separate generative VLM server backends with different precedence and deployment constraints.
tags: [ml, ocr, inference, deployment]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T06:53:14Z }
stale_after: 2027-04-29
sources:
  - id: paddleocr-repo
    resource: ../raw/PaddleOCR/README.md
    scope: ../raw/PaddleOCR/
    kind: code
    revision: dab3fe3
    title: PaddleOCR repository
---

# PaddleOCR inference engines

**Observed:** The [PaddleOCR pipeline wrappers](paddleocr-repository-pipelines.md) pass engine and device configuration to PaddleX; their accepted engine names are `paddle`, `paddle_static`, `paddle_dynamic`, `transformers`, and `onnxruntime`. The VL recognition module has a separate backend selector for native inference or generative servers. Available engines and their behavior depend on the installed external runtime, model, and hardware.[^paddleocr-repo]

## Engine selection and precedence

**Observed:** `prepare_common_init_args` forwards an explicit `engine_config`; otherwise it builds static Paddle settings for `paddle_static`, or a `paddle_static` configuration bucket for `paddle` or the unspecified engine. The config includes device-dependent TensorRT or CPU settings. **Reported:** the engine guide says API/CLI settings override the pipeline configuration, while submodule settings can override upper-level configuration; explicitly specifying `engine` makes `enable_hpi` ineffective, and an explicit `engine_config` supersedes compatibility options such as `use_tensorrt`, `precision`, and `cpu_threads`.[^paddleocr-repo]

**Reported:** high-performance inference can select Paddle Inference, OpenVINO, ONNX Runtime or TensorRT and convert models to ONNX as needed. The documented CUDA 12.6/cuDNN 9.5 HPI path supports OpenVINO and ONNX Runtime but not TensorRT in this snapshot. Those are documentation claims, not a reproduced compatibility test.[^paddleocr-repo]

## Generative and deployment paths

**Observed:** `PaddleOCRVL` accepts `native`, `vllm-server`, `sglang-server`, `fastdeploy-server`, `mlx-vlm-server`, and `llama-cpp-server`, plus a server URL and concurrency settings. Its default pipeline version is v1.6. This selector concerns the recognition component and should not be mistaken for the whole layout-plus-recognition pipeline.[^paddleocr-repo]

The repository includes separate local, serving and client surfaces; the upstream README describes C++ and HTTP integration and HPI. The actual PaddleX engine dispatch, downloaded artifacts, device compatibility and performance were not independently checked. See the [PaddleOCR 3.0 overview](paddleocr-3.md) for the report's deployment claims.[^paddleocr-repo]

## Relationships

- **Used by:** [PaddleOCR repository pipelines](paddleocr-repository-pipelines.md).
- **Supports:** [PaddleOCR-VL 1.6](paddleocr-vl-1.6.md) through a separately configured generative recognition backend.[^paddleocr-repo]

[^paddleocr-repo]: [Repository README](../raw/PaddleOCR/README.md), “More Features”; revision `dab3fe3`: `paddleocr/_common_args.py::SUPPORTED_INFERENCE_ENGINE_LIST`, `prepare_common_init_args`; `paddleocr/_pipelines/paddleocr_vl.py::_SUPPORTED_VL_BACKENDS`, `PaddleOCRVL`; `docs/version3.x/inference_deployment/local_inference/inference_engine.en.md`, §§4.2–4.4; `docs/version3.x/inference_deployment/local_inference/high_performance_inference.en.md`, introduction and §1; `docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md`, introduction.
