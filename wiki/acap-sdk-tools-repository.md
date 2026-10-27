---
type: Concept
title: "ACAP SDK tools repository: overview and coverage ledger"
description: "What AxisCommunications/acap-sdk-tools at git 7250746 contains: two Docker-based developer tools (AprilGrid camera calibration and Ansible/AWS model training), their identity, layout, licence, relationships to other ACAP repositories, and a coverage ledger of all 118 files."
tags: [edge-ai, axis, acap, repository, tools, calibration, training, docker]
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
  - id: sdk-tools-license
    resource: ../raw/acap-sdk-tools/LICENSE
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "Apache License 2.0"
  - id: sdk-tools-codeowners
    resource: ../raw/acap-sdk-tools/CODEOWNERS
    scope: ../raw/acap-sdk-tools/
    kind: code
    revision: "7250746"
    title: "CODEOWNERS"
---

# ACAP SDK tools repository: overview and coverage ledger

`acap-sdk-tools` is a small Axis repository of **developer-side helper tools** that extend the ACAP SDK. It is not an SDK, not an ACAP application, and nothing in it is packaged as an `.eap`; both tools run in Docker on a development machine.[^sdk-tools-readme] The root README says the tools "facilitate the integration of compatible third-party solutions" and that each tool has its own README with an overview, example directory structure and step-by-step instructions.[^sdk-tools-readme]

## Tools

| Tool | Purpose | Concept |
| --- | --- | --- |
| `camera-calibration-for-lens-distortion` | C++ program that estimates camera intrinsics and distortion from AprilGrid photos and writes `config.cfg` | [implementation and defects](acap-sdk-tools-camera-calibration-tool.md); method in [Hiệu chỉnh méo ống kính cho camera Axis](axis-camera-calibration.md) |
| `train-tensorflow-model-using-aws` | Ansible playbook that runs the `tensorflow-to-larod-artpec8` training on a temporary AWS GPU instance and returns a `.tflite` | [Ansible EC2 training](acap-sdk-tools-aws-training-tool.md) |

Contribution rules, workflows, lint and Renovate configuration are in [ACAP SDK tools CI and maintenance](acap-sdk-tools-ci-and-maintenance.md).

## Identity

- **Upstream:** `https://github.com/AxisCommunications/acap-sdk-tools`, default branch `main`, mounted here as the git submodule `raw/acap-sdk-tools`. **Snapshot:** `7250746d39fb25384402d0f900eb5a6a27c29d69` (2026-08-18, "style: fix lint error"), no tags, 11 commits, 118 tracked files (**Observed** with `git`).
- **History:** first commit 2022-05-11 ("Initial commit for ACAP SDK extra tools"), OSS review 2022-05-24, small documentation edits in 2023, and a maintenance round on 2026-08-18 that added Renovate, SHA-pinned actions and read-only token permissions. (**Observed**; *Synthesis*: low activity.)
- **Licence:** Apache License 2.0. **Copyright:** Axis Communications AB, 2022 (README header). **Owners:** `@AxisCommunications/acap-sdk-tools-owners`.[^sdk-tools-license][^sdk-tools-codeowners]
- The name `extra tools` in the first commit and the vendor documentation's reference to `acap-sdk-extras` suggest an earlier repository name; the archived docs refer to both (see [ACAP documentation repository](acap-documentation-repository.md)). (*Synthesis*)

## Relationship to the rest of ACAP

- The calibration method page is the vendor guide in `raw/acap`; this repository supplies the code that guide links to. The code deviates from that guide in file names, the number of images required and the threshold handling.
- The training tool wraps a training example that lives in `acap-native-sdk-examples` (see [tensorflow-to-larod guides](acap-example-model-training-guides.md) and the [examples repository catalog](acap-native-sdk-examples-repository.md)); the README links the example's object-detection sibling and the archived `pose-estimator-with-flask` as consumers of trained models ([CV example](acap-cv-example-pose-estimator-flask.md)).
- The calibration Dockerfile builds on the archived [ACAP Computer Vision SDK](acap-cv-sdk-examples-repository.md) image.
- Both tools sit upstream of [custom model deployment](axis-custom-model-deployment.md): calibration for image preprocessing, training for model production. (*Synthesis*)

## Coverage ledger

| Artifact | Count | Status |
| --- | --- | --- |
| Root README, CONTRIBUTING, CODEOWNERS, LICENSE, CODE_OF_CONDUCT | 5 | README, CONTRIBUTING and CODEOWNERS read; LICENSE and CODE_OF_CONDUCT identified only |
| Lint/editor config: `.editorconfig`, `.gitignore`, `.hado-lint.yml`, `.markdownlint.yml`, `.yaml-lint.yml`, `.vscode/*` | 7 | Read; see [CI and maintenance](acap-sdk-tools-ci-and-maintenance.md) |
| `.github/` workflows (4) and `renovate.json` | 5 | Read |
| `camera-calibration-for-lens-distortion/` code, build, config, README | 12 | Read; see [calibration tool](acap-sdk-tools-camera-calibration-tool.md) |
| Calibration SVGs | 2 | `calibration_diagram.svg` labels extracted; `distortion.svg` (≈650 KB) has no text and was not interpreted |
| Calibration datasets `aprilgrid_wide/`, `aprilgrid_tele/` | 80 JPEGs | Excluded as sample data: counted, one file's dimensions checked, not viewed |
| `train-tensorflow-model-using-aws/` README, Dockerfile, Ansible files | 6 | Read; see [AWS training tool](acap-sdk-tools-aws-training-tool.md) |
| `security_diagram.svg` | 1 | Text labels extracted |

Total: 118 tracked files. Nothing was built or executed; the external dependencies (ethzasl_apriltag2, the CV SDK image, AWS, the training example) are not local. Findings come from static reading of each file; the repository was explored by three parallel read-only explorers (calibration tool, AWS tool, repository-level files) whose key claims were re-checked against the files.

## Relationships

- **Contains** [the calibration tool](acap-sdk-tools-camera-calibration-tool.md), [the AWS training tool](acap-sdk-tools-aws-training-tool.md) and [their CI](acap-sdk-tools-ci-and-maintenance.md).
- **Supports** [Hiệu chỉnh méo ống kính cho camera Axis](axis-camera-calibration.md) and [tensorflow-to-larod guides](acap-example-model-training-guides.md).
- **Distinct from** [ACAP Native SDK repository](acap-native-sdk-repository.md), which builds the SDK images, and from [ACAP Runtime](acap-runtime-repository.md), which runs on the camera.

[^sdk-tools-readme]: Root README, intro paragraph, §Tools, §How to work with GitHub repository; `git rev-parse HEAD`, `git log` of the submodule at 7250746.
[^sdk-tools-license]: `LICENSE` (Apache License, Version 2.0) and README §License.
[^sdk-tools-codeowners]: `CODEOWNERS`, line 1 (`* @AxisCommunications/acap-sdk-tools-owners`).
