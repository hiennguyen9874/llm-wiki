---
type: Concept
title: "Axis Model Zoo accuracy harness: ImageNet top-1/top-5 ACAP, converters and known defects"
description: "How scripts/accuracy-test measures classification accuracy on an Axis camera (ILSVRC2012 validation set, raw .bin tensors on SD card, per-chip ACAP manifests, larod inference, syslog results), its preprocessing and scoring logic, and the verified bugs that limit trust, especially on CV25."
tags: [edge-ai, axis, model-zoo, accuracy, imagenet, larod, acap, mobilenet, cv25]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:20:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-acc-readme
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "accuracy-test README (runbook)"
  - id: mz-acc-c
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/app/accuracy_measure.c
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "accuracy_measure.c — larod accuracy app"
  - id: mz-acc-argparse
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/app/argparse.c
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "argparse.c — argp command-line parser (Axis, 2023)"
  - id: mz-acc-convert
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/larod_convert.py
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "larod_convert.py — JPEG to raw tensor converter"
  - id: mz-acc-rename
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/rename_files.py
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "rename_files.py — validation image renamer"
  - id: mz-acc-docker
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/Dockerfile
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "accuracy-test Dockerfile (per-chip ACAP build)"
  - id: mz-acc-manifest
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/app/manifest.json.cv25
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "manifest.json.cv25 (one of five per-chip manifests)"
  - id: mz-acc-gt
    resource: ../raw/axis-model-zoo/scripts/accuracy-test/app/ground_truth.txt
    scope: ../raw/axis-model-zoo/
    kind: dataset
    revision: "v1.0.7-42-g66bf5ea"
    title: "ground_truth.txt — ILSVRC2012 validation labels (50 000 lines)"
---

# Axis Model Zoo accuracy harness: ImageNet top-1/top-5 ACAP, converters and known defects

`scripts/accuracy-test/` is the only in-repo way to reproduce the classification accuracy column of the [Axis Model Zoo](axis-model-zoo-repository.md). It is a **batch scorer, not a demo**: images of the ILSVRC2012 validation set are converted on a host into raw tensor files, copied to the camera's SD card, and an ACAP application feeds them one by one through `larod`, comparing the predicted class with a bundled ground-truth file and logging top-1/top-5 to syslog.[^mz-acc-readme][^mz-acc-c] The README states that only classification models are tested this way; object-detection accuracy was never evaluated on a camera.[^mz-readme] Findings below are **Observed** by static reading; nothing was built or run.

## Procedure

1. **Prerequisites:** camera in Developer Mode, the 50 000-image ILSVRC2012 validation archive, and (undocumented) Python 3 with `opencv-python` and `numpy`.[^mz-acc-readme][^mz-acc-convert]
2. **Rename** images with `rename_files.py <VAL_DIR> ./dataset`: `ILSVRC2012_val_00013453.JPEG` becomes `13453.JPEG` because the app addresses image *n* by integer.[^mz-acc-rename]
3. **Convert** with `larod_convert.py 224 224 ./dataset` (add `-p` for CV25 planar layout) into a hard-coded relative `output/` directory (`mkdir output` is mandatory). The conversion is BGR→RGB, bilinear resize to the target size ignoring aspect ratio, uint8 by default (float32 with `--float` and optional subtract/divide), interleaved RGB or planar, optional row padding.[^mz-acc-convert]
4. **Build** the ACAP per chip with Docker (`--build-arg CHIP=<artpec8|artpec9|cpu|cv25|edgetpu> --build-arg ARCH=…`). The Dockerfile downloads the model (plain-HTTP TensorFlow tarball, Coral Edge TPU file renamed, or Axis S3 CV25 `.bin`) and labels, copies `manifest.json.<CHIP>`, and runs `acap-build` with the model, labels and `ground_truth.txt`. SDK image `12.2.0`, digest pinned; models are not checksummed.[^mz-acc-docker]
5. **Install** the `.eap` (allow unsigned apps), enable Developer Mode, set the password of the SSH account `acap-accuracy_measure`, create `/var/spool/storage/SD_DISK/imagenet` and `scp output/*` there (about **7.5 GB**: 50 000 × 150 528 bytes).[^mz-acc-readme]
6. **Run** by starting the app (manifests set `runMode: never`). Results exist only in syslog: per-image lines then a final block with `top1 sum`, `top5 sum`, and the two averages; the process exits successfully regardless of accuracy.[^mz-acc-c]

## The scoring app

- **CLI:** `accuracy_measure MODEL WIDTH HEIGHT OUTPUT_SIZE [-c DEVICE] [-l LABELS] [-g ANNOTATIONS]`; `OUTPUT_SIZE` is in bytes. The parser is Axis's own `argp` code; its help text is stale (describes a VDO/YUV pipeline that the app does not have).[^mz-acc-argparse]
- **Inference:** `larodConnect`, `larodGetDevice`, `larodLoadModel`, two mmap'd anonymous tmp-file buffers for one input and one output tensor, then `larodRunJob` per image. Tensor shape is never queried; correctness depends on manifest constants (224, 224, 1001 or 32032).[^mz-acc-c]
- **Decoding:** for the device string `ambarella-cvflow` the output is read as float32 at a 32-byte stride (1001 classes → 32032 bytes); for every other device it is uint8 with a softmax over the argmax. The device *name* therefore selects the decoder.[^mz-acc-c]
- **Ground truth:** `ground_truth.txt` has 50 000 lines of class indices 0–999 (each value exactly 50 times, **Reproduced** by counting); the app adds 1 to match TFLite's 1001-class output with background at index 0.[^mz-acc-gt]
- **Per-chip manifests** differ only in `friendlyName` and `runOptions`: device `axis-a8-dlpu-tflite`, `a9-dlpu-tflite`, `cpu-tflite`, `google-edge-tpu-tflite` or `ambarella-cvflow`; model `mobilenet_v2_1.0_224_quant.tflite` (artpec8/9/cpu), its Edge TPU variant, or `mobilenet_v2_cavalry.bin` (cv25, output size 32032).[^mz-acc-manifest]

## Defects that limit trust (all Observed)

| Defect | Effect | Locator |
| --- | --- | --- |
| CV25 top-5 selection loops to `outputBytes` (32032) instead of 1001 elements, reading uninitialised stack floats | CV25 top-5 unreliable | `accuracy_measure.c` cv25 top-5 branch |
| CV25 float scores swapped through an `int` temporary | scores truncated during selection | same branch |
| `manifest.json.cpu` passes `label/ground_truth.txt` but the package ships `ground/ground_truth.txt` | CPU build fails to open annotations | `manifest.json.cpu`, Dockerfile[^mz-acc-docker] |
| Fixed `N_IMAGES 50000`; missing or unreadable `.bin` files count as zero and the denominator stays 50 000; short reads still run inference on stale buffer data | silently lower or corrupted accuracy | `accuracy_measure.c` loop |
| `ground_truth[50000]` read without bound and uninitialised | overflow or garbage on wrong-sized files | same |
| Label lookups use `labels[maxIdx]` although indices are shifted by the background class; guard uses `>` not `>=`; `labels` dereferenced without NULL check | wrong label text, possible out-of-bounds read, crash when `-l` omitted | same |
| `larod_convert.py` ignores `-o`, hard-codes `output/`, writes padding byte by byte, does not validate `--pitch` | surprising behaviour and slow runs | `larod_convert.py` |
| `rename_files.py` builds `mkdir`/`cp` shell strings unquoted, no argument checking | breaks on unusual paths | `rename_files.py` |
| Cleanup calls `larodDestroyTensors` after `larodDisconnect` set the connection to NULL; `model` may be uninitialised after early `goto end` | latent undefined behaviour on error paths | `accuracy_measure.c` end section |

## Documentation versus implementation

- The README lists supported chips as `artpec8`, `cpu`, `cv25`, `edgetpu`, but the Dockerfile and a manifest also support `artpec9`.[^mz-acc-readme][^mz-acc-docker]
- It says models and labels come from `coral.ai/models`; the Dockerfile fetches from `download.tensorflow.org` (HTTP), Coral's GitHub test data and the Axis S3 bucket.
- `LOC_synset_mapping.txt` is listed in the README but read by no code (read by head only here).
- The `edgetpu` build downloads `tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite` and stores it under the TF1 file name, so the TF1 ARTPEC-7 accuracy row (68.9/88.2) cannot be tied to current tooling (**Synthesis**).
- Only MobileNetV2 variants have manifests; the table's MobileNetV3, EfficientNet-Lite0/Lite2 and CV75 MobileNetV2 accuracies have no reproduction path here ([benchmark results](axis-model-zoo-benchmark-results.md)).

## Interpretation limits (Synthesis)

Preprocessing is a direct resize to 224×224 with distorted aspect ratio, with no 256-resize and centre crop, so absolute numbers are not comparable with published ImageNet figures; only comparisons across chips using the same conversion are meaningful. Same-bytes accuracy differs by about 0.3 points between ARTPEC-8 and ARTPEC-9 rows, which sets a practical noise floor.

## Relationships

- **Part of:** [Axis Model Zoo repository](axis-model-zoo-repository.md); results feed [benchmark results](axis-model-zoo-benchmark-results.md).
- **Uses:** the larod C API patterns described in [Larod examples](acap-example-larod-object-detection.md) and the [Native SDK API catalog](acap-native-sdk-api-catalog.md); requires [SSH developer mode](axis-device-ssh-developer-mode.md).
- **Models tested:** [model files](axis-model-zoo-model-files-and-licensing.md).
- **Sibling method:** speed uses a different app, see [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md).

[^mz-readme]: `README.md` §Accuracy measure.
[^mz-acc-readme]: `scripts/accuracy-test/README.md` — prerequisites, build, install, SSH/scp, run steps; chip list.
[^mz-acc-c]: `scripts/accuracy-test/app/accuracy_measure.c` — `N_IMAGES`, `setupLarod`, buffer creation, main loop (decode, top-5 selection, scoring), `RESULTS:` log block, `end:` cleanup.
[^mz-acc-argparse]: `scripts/accuracy-test/app/argparse.c` — argp option table, `parseOpt`, `parsePosInt`; stale help text.
[^mz-acc-convert]: `scripts/accuracy-test/larod_convert.py` — `ConvertImage.convert`, `check_arguments`, `write_data_with_padding`, `-o` option.
[^mz-acc-rename]: `scripts/accuracy-test/rename_files.py` — `os.system("mkdir …")` and `cp` lines.
[^mz-acc-docker]: `scripts/accuracy-test/Dockerfile` — `ARG` lines, model/label downloads, CHIP dispatch and `acap-build` calls.
[^mz-acc-manifest]: `scripts/accuracy-test/app/manifest.json.cv25::runOptions` (and the four sibling manifests, `manifest.json.cpu::runOptions` for the path error).
[^mz-acc-gt]: `scripts/accuracy-test/app/ground_truth.txt` — 50 000 integer lines, values 0–999, 50 each (counted).
