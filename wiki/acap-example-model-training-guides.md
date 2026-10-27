---
type: Concept
title: "ACAP examples: tensorflow-to-larod training and conversion guides for ARTPEC-7, 8, 9 and CV25"
description: "How the four tensorflow-to-larod guides train a person/car ResNet on COCO and convert it per SoC: Edge TPU compile, ARTPEC-8 quantization-aware training with TensorFlow 1.15, the ARTPEC-9 pointer README, and the manual CV25 Ambarella pipeline, with differences and defects."
tags: [edge-ai, axis, acap, examples, training, quantization, tensorflow, larod]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP examples: tensorflow-to-larod training and conversion guides

Four directories show how to train a small model and make it runnable by Larod on a given SoC. They are guides run in Docker, not applications; the resulting file is consumed by the [`vdo-larod` example](acap-example-larod-object-detection.md).[^native-examples] All train the same model: a small ResNet that classifies a 256x256 RGB frame with two independent sigmoid outputs (`A_person_pred`, `B_car_pred`; the `A_`/`B_` prefixes force alphabetical order in the `.tflite` converter) on MS COCO 2017, with cars defined as COCO categories 3, 6 and 8 (car, bus, truck).

## Per-SoC pipelines

| Guide | Target and backend | Base image | Training | Quantization and conversion |
| --- | --- | --- | --- | --- |
| `tensorflow-to-larod` | ARTPEC-7, Google Edge TPU (`google-edge-tpu-tflite`) | `tensorflow/tensorflow:2.4.2-gpu` plus Coral `edgetpu-compiler` | one pass, Adam, `bce`, batch 16, 8 epochs, SavedModel | post-training INT8 with 1000-sample representative set, uint8 input and output, then `edgetpu_compiler -s`; deployable file is `converted_model_edgetpu.tflite` |
| `tensorflow-to-larod-artpec8` | ARTPEC-8 DLPU (`axis-a8-dlpu-tflite`) | `tensorflow/tensorflow:1.15.5-gpu` | three passes: train (8 epochs), quantization-aware fine-tune with `tf.contrib.quantize` (4 epochs), export frozen eval graph | legacy `from_frozen_graph`, `quantized_input_stats (0,255)`, uint8, per-tensor quantization (per-axis runs much slower); no representative dataset |
| `tensorflow-to-larod-artpec9` | ARTPEC-9 (`a9-dlpu-tflite`) | none | none | README only: "follows the same steps as the ARTPEC-8 version" and links to it |
| `tensorflow-to-larod-cv25` | Ambarella CV25 (`ambarella-cvflow`) | `tensorflow/tensorflow:latest-gpu-py3` (unpinned) | same script as ARTPEC-7 | same TFLite conversion, then manual Ambarella steps: `gen_image_list.py` for the DRA image list, `tfparser.py` (NCHW input, scale 255.00446258, fp32 outputs, activations and coefficients forced to **fx16**), `vas -auto`, `cavalry_gen` → `car_human_model_cavalry.bin` |

`vdo-larod` maps `artpec9` and `cpu` to the same ARTPEC-8 model file, which is why the ARTPEC-9 guide has no pipeline of its own.[^native-examples] Ambarella tools are partner-only and not installed in the image, so the CV25 section is not runnable from the repository; see [ONNX conversion for CV75](axis-cv75-onnx-conversion.md) for the newer Ambarella path and [Deploying a custom AI model](axis-custom-model-deployment.md) for the cross-SoC overview.

## Model and data code

- `env/training/model.py`: `create_model` with residual blocks (strides 1 and 2, filters doubling from 16 to 256), global max pooling emulated by `MaxPooling2D(side)` (the Edge TPU lacks it), `Dense(64)` then two heads. ARTPEC-8 uses `use_bias=False` convolutions so batch norm fuses under TF 1.15 and a named input `image_input`.
- `env/training/utils.py`: `SimpleCOCODataGenerator` keeps images that exist and are RGB, resizes to 256x256, applies horizontal flip (p=0.5, not in the ARTPEC-8 variant), divides by 255, and oversamples four subsets with weights `[1,1,1,3]`.
- `env/convert_model.py` is byte-identical in the ARTPEC-7 and CV25 guides; the ARTPEC-8 converter is a separate TF 1 lineage.
- Run recipe: `docker build --platform=linux/amd64 --tag <IMAGE> [--build-arg TRAIN_EPOCHS=N] .` then `docker cp` the `.tflite` out.[^native-examples]

## Observed defects and limits

- The ARTPEC-8 `train.py` hard-codes `n_blocks: 5` (the function default is 4) and absolute `/env/models/...` paths; conversion does not set `inference_output_type`.
- All data generators define `__len__` from the annotation count while oversampling inflates the index array, so each epoch visits only about a quarter of the balanced indices (derived from the code; not run).
- ARTPEC-7 README says the published model used 10 epochs on COCO train2017 (~80%/~90%), while the Dockerfile trains 8 epochs on val2017; prerequisites still mention TensorFlow r1.15, copied from ARTPEC-8.
- CV25: the Dockerfile downloads an unused prebuilt `.bin` through a misspelled bucket path (`tenosrflow_...`); the README refers to a `pics` directory that no step creates and ends its "expected output" without naming the cavalry `.bin`.
- `np.random.choice(..., size=1000, replace=False)` needs at least 1000 images in the dataset; the CV25 base image `latest` is likely incompatible with the legacy converter flags.[^native-examples]

Evidence class: **Observed** by reading code and `diff` between the shared files; nothing was trained or converted.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Feeds** [Larod inference examples](acap-example-larod-object-detection.md).
- **Automated by** [ACAP SDK tools: train-tensorflow-model-using-aws](acap-sdk-tools-aws-training-tool.md), an Ansible playbook that runs the ARTPEC-8 guide on a temporary AWS GPU instance; it hard-codes the `tensorflow-to-larod-artpec8` directory and image names, so it does not cover the other three guides. (Observed)
- **Complements** [DLPU model constraints](axis-dlpu-model-constraints.md) (per-tensor quantization on ARTPEC-8) and [ARTPEC-9 model conversion](axis-artpec-9-model-conversion.md), which documents the current vendor route to a9-dlpu-tflite.

[^native-examples]: `tensorflow-to-larod/{Dockerfile,README.md,env/convert_model.py,env/training/{model,train,utils}.py}`; the same paths under `tensorflow-to-larod-artpec8/` and `tensorflow-to-larod-cv25/`; `tensorflow-to-larod-artpec9/README.md`; `vdo-larod/Dockerfile` (model mapping per CHIP); `README.md` §"Train and convert models for Axis devices".
