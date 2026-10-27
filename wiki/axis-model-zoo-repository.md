---
type: Concept
title: "Axis Model Zoo repository: overview, layout and coverage ledger"
description: "What AxisCommunications/axis-model-zoo at v1.0.7-42-g66bf5ea is: a collection of off-the-shelf models for Axis cameras with speed and accuracy tables, benchmark tooling and a YOLOv5 training guide, plus its layout, licensing, coverage ledger and headline README-versus-code gaps."
tags: [edge-ai, axis, model-zoo, repository, larod, benchmark, artpec, cv25, cv75]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:00:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-license
    resource: ../raw/axis-model-zoo/LICENSE
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "Apache License 2.0 (repository licence)"
  - id: mz-codeowners
    resource: ../raw/axis-model-zoo/CODEOWNERS
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "CODEOWNERS"
---

# Axis Model Zoo repository: overview, layout and coverage ledger

The Axis Model Zoo is a public GitHub repository that gathers **off-the-shelf machine-learning models known to run on Axis cameras**, each with a measured inference **speed** and a reported **accuracy**, together with the scripts used to measure them and a guide for training YOLOv5 for ARTPEC-8/-9.[^mz-readme] Its README says plainly that the models are "not production-quality … used for comparative and demonstration purposes only", and that models are mostly public so results can be reproduced.[^mz-readme] The repository is the practical "which model on which chip, how fast" companion to the Axis conversion guides ([ARTPEC-9 conversion](axis-artpec-9-model-conversion.md), [CV75 ONNX conversion](axis-cv75-onnx-conversion.md)) and to the [DLPU](axis-dlpu.md) constraints.

## Identity

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/AxisCommunications/axis-model-zoo` (branch `main`) — **Observed** from the checkout's git remote |
| Revision | `v1.0.7-42-g66bf5ea` = `66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8`, committed 2026-10-09; 84 commits; 78 tracked files |
| Licence | Apache-2.0 for the repository;[^mz-license] YOLOv5/YOLOv8 model files are AGPL-3.0-only, see [model files and licensing](axis-model-zoo-model-files-and-licensing.md) |
| Owner | `* @AxisCommunications/axis-model-zoo-admins` (single CODEOWNERS rule)[^mz-codeowners] |
| Languages | Python (scripts), C (accuracy app), shell (device benchmark), YAML (CI), Markdown |
| Freshness stamp | The README's tables state "Values for AXIS OS 12.11.72"[^mz-readme] |
| Stated goal | Keep extending the collection with models for other applications such as object detection and pose estimation; today only image classification and object detection are covered[^mz-readme] |

## What the README promises

- **Two tables** — image classification (10 rows: Top-1/Top-5) and object detection (17 rows: mAP) — each row naming SoC, reference device, model, link to the model file and, when public, a checkpoint (`ckpt`) link. Normalised in [benchmark results](axis-model-zoo-benchmark-results.md).[^mz-readme]
- **Speed** is the mean inference time measured by an ACAP application on a real camera, refreshed "with every AXIS OS release"; see [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md).[^mz-readme]
- **Accuracy** is not re-measured per release: classification models are tested with an on-camera ACAP ([accuracy harness](axis-model-zoo-accuracy-test-harness.md)); detection accuracy is taken from Coral's published figures except for Axis's own YOLOv5 models.[^mz-readme]
- **Guides:** the ACAP documentation and the [YOLOv5 on ARTPEC-8/9 guide](axis-model-zoo-yolov5-training-guide.md).[^mz-readme]
- **Own-model measuring:** `scripts/model_performance_tester.py` runs `larod-client` over SSH; chip names accepted are `CPU`, `A9-DLPU`, `A8-DLPU`, `A7-GPU`, `A7-TPU`, `CV25`.[^mz-readme]

## Layout

| Path | Role | Concept |
| --- | --- | --- |
| `README.md` | Tables, method description, licence note | this page, [results](axis-model-zoo-benchmark-results.md) |
| `models/` | 17 binary model files (96.6 MiB) | [model files](axis-model-zoo-model-files-and-licensing.md) |
| `docs/yolov5.md` | YOLOv5 train/export/deploy guide | [YOLOv5 guide](axis-model-zoo-yolov5-training-guide.md) |
| `scripts/auto-test-framework/` | `larod-test` ACAP app plus `readme_update.py` that rewrites speed cells | [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md) |
| `scripts/model_performance_tester.py` | Standalone SSH speed tester | [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md) |
| `scripts/accuracy-test/` | ImageNet top-1/top-5 ACAP, converters, ground truth | [accuracy harness](axis-model-zoo-accuracy-test-harness.md) |
| `.github/workflows/` | `benchmark.yml`, `linter.yml`, `teardown.yml` | [CI and maintenance](axis-model-zoo-ci-and-maintenance.md) |
| `renovate.json`, lint configs, `CONTRIBUTING.md`, `.editorconfig`, `.vscode/` | Maintenance and contribution rules | [CI and maintenance](axis-model-zoo-ci-and-maintenance.md) |

## Headline gaps between documentation and implementation

These were found by static inspection and are detailed in the linked concepts (**Observed**):

1. **The speed table is only partly automated.** The README says the framework updates "each model in the table", but four rows (CV25 YOLOv5s and the three CV75 rows) have no token in `readme_update.py`, no model folder and no CV75 camera in the workflow matrix, so they are edited by hand.
2. **"Every AXIS OS release" is a manual dispatch.** `benchmark.yml` only has `workflow_dispatch`, and its permissions block (`contents: read`) conflicts with its `git push` step.
3. **Accuracy provenance is thinner than stated.** Only MobileNet-V2 variants have an on-camera accuracy manifest; MobileNet-V3, EfficientNet-Lite0/Lite2, the CV75 MobileNet-V2 and the YOLOv8 row have no in-repo reproduction path.
4. **Model links are inconsistent.** 21 rows link to remote artefacts although byte-identical local copies exist for 13 of them; the three ARTPEC-9 YOLOv5 files exist only inside the benchmark app.
5. **Tooling comparability:** the recommended `model_performance_tester.py` omits the `-w 5` warm-up and uses 100 runs by default, whereas the table is produced with `-R 1000 -w 5`.

## Coverage ledger

| Artefact | Status |
| --- | --- |
| `README.md`, `LICENSE`, `CODEOWNERS`, `CONTRIBUTING.md`, `renovate.json`, lint configs, `.editorconfig`, `.vscode/*`, `.gitignore` | inspected statically |
| `docs/yolov5.md` | inspected |
| `scripts/auto-test-framework/**` (README, `readme_update.py`, `larod-test` app files, three `LICENSE` texts) | inspected; app shell script, Dockerfile, manifest and Makefile read in full |
| `scripts/accuracy-test/**` (README, Dockerfile, `larod_convert.py`, `rename_files.py`, `accuracy_measure.c`, `argparse.c/h`, five manifests, `LICENSE`) | inspected; `ground_truth.txt` verified by counting (50 000 lines, values 0–999); `LOC_synset_mapping.txt` read by head only |
| `scripts/model_performance_tester.py` | inspected |
| `.github/workflows/*.yml` | inspected |
| `models/*` (17 files) and `scripts/auto-test-framework/larod-test/app/models/**` (19 files) | listed, checksummed, header-identified; **not** executed or parsed. No Git LFS; real binaries |
| Remote artefacts (S3 `acap-ml-models`, Coral `test_data`, checkpoint URLs, Axis docs pages) | **not fetched**; links only |

No code, workflow, or model was executed; no live device was contacted. Nothing sensitive was found: workflow secrets (`DEVICE_IP`, `DEVICE_PASSWORD`) appear by name only.

## Relationships

- **Complements:** [Axis DLPU](axis-dlpu.md), [DLPU model constraints](axis-dlpu-model-constraints.md) and [ARTPEC-9 operator support](axis-artpec-9-operator-support.md) explain why models differ per chip; the [chip and SDK compatibility table](acap-chip-architecture-and-sdk-compatibility.md) lists the platforms.
- **Consumed by:** the [Larod object-detection examples](acap-example-larod-object-detection.md) download the YOLOv5 models from the same S3 bucket; the [tensorflow-to-larod guides](acap-example-model-training-guides.md) cover the training side for other models.
- **Referenced by:** the [ACAP developer FAQ](acap-developer-faq.md) and [release history](acap-release-history.md) (Model Zoo launched with ACAP 4.7).
- **Deployment of custom models:** [Custom model deployment](axis-custom-model-deployment.md).

## Evidence class

Identity, layout and gaps are **Observed** (static inspection of the checkout). Speed and accuracy numbers are **Reported** by the README; none was **Reproduced**. Roles and comparisons are **Synthesis**.

[^mz-readme]: `README.md` intro, §Guides, §Models (Image classification, Object detection), the "Values for AXIS OS 12.11.72" line, §How are the measures calculated? (Speed measure, Accuracy measure), §License; `git describe`, `git remote -v`, `git log` of the checkout.
[^mz-license]: `LICENSE` header (Apache License 2.0, January 2004).
[^mz-codeowners]: `CODEOWNERS` line 1.
