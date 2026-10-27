---
type: Concept
title: "Axis Model Zoo speed pipeline: larod-test ACAP, benchmark workflow and model_performance_tester"
description: "How the Axis Model Zoo measures inference speed end to end (manual GitHub workflow, per-camera ACAP build, larod-client mean job time, readme_update.py cell rewriting), how the standalone SSH tester differs, and the verified defects and drifts in the pipeline."
tags: [edge-ai, axis, model-zoo, benchmark, larod, github-actions, acap, speed]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:15:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-benchmark
    resource: ../raw/axis-model-zoo/.github/workflows/benchmark.yml
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "benchmark.yml — Test model speed workflow"
  - id: mz-larod-sh
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/larod-test/app/larod_test.sh
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "larod_test.sh — on-device benchmark script"
  - id: mz-larod-docker
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/larod-test/Dockerfile
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "larod-test Dockerfile (ACAP build)"
  - id: mz-larod-readme
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/larod-test/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "larod-test README"
  - id: mz-readme-update
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/readme_update.py
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "readme_update.py — speed-cell rewriter"
  - id: mz-perf-tester
    resource: ../raw/axis-model-zoo/scripts/model_performance_tester.py
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "model_performance_tester.py — SSH larod-client tester"
  - id: mz-teardown
    resource: ../raw/axis-model-zoo/.github/workflows/teardown.yml
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "teardown.yml — stop and remove the test app"
---

# Axis Model Zoo speed pipeline: larod-test ACAP, benchmark workflow and model_performance_tester

Speed in the [Axis Model Zoo](axis-model-zoo-repository.md) tables is the **mean `larod-client` job time over 1000 runs with 5 warm-up runs on random input**, taken by a purpose-built ACAP (`larod_test`) installed on five lab cameras by a manually dispatched GitHub Actions workflow, then written back into `README.md` by a Python script.[^mz-benchmark][^mz-larod-sh][^mz-readme-update] A second, standalone tool (`model_performance_tester.py`) lets users time their own models over SSH, but with a different methodology. All mechanism statements below are **Observed** by static reading; nothing was executed (no camera available).

## End-to-end flow of the workflow

| Step | What happens | Locator |
| --- | --- | --- |
| Trigger | `workflow_dispatch` only, `ubuntu-latest`, `permissions: contents: read`. The README's "every AXIS OS release" is therefore a human habit, not an event trigger.[^mz-benchmark][^mz-readme] | `benchmark.yml` top |
| Camera matrix | `matrix.arch` is really a camera slot: `camera1` ARTPEC-7 Q1615 Mk III, `camera2` ARTPEC-8 Q1656-LE, `camera3` CV25 M3085-V, `camera4` ARTPEC-8 P1465-LE, `camera5` ARTPEC-9 Q1728. Access is over plain HTTP to one secret host with a `/<camera>/` path prefix and `root` credentials from secrets `DEVICE_IP`/`DEVICE_PASSWORD` (names only).[^mz-benchmark] | matrix, every `curl` step |
| 1. Clean state | Reboot through `firmwaremanagement.cgi`, poll `systemready.cgi` every 5 s until ready, so the system log is empty (the parser takes the first `Model name:` match).[^mz-benchmark] | reboot step |
| 2. Stabilise | Set `ImageSource.I0.Sensor.MotionAdaptiveExposure=off` and read it back; no other sensor, thermal or firmware-version control or recording.[^mz-benchmark] | param step |
| 3. Build | Map camera slot to `device` (artpec7/8/9/cv25), `docker build --no-cache --build-arg device=…`, copy `/opt/app` out. The Dockerfile uses the Native SDK image `12.0.0`, `armv7hf`, Ubuntu 24.04, and `acap-build . -a models/${device}/`, so only that SoC's model folder is packaged.[^mz-benchmark][^mz-larod-docker] | build step, Dockerfile |
| 4. Install and run | Upload hard-coded `larod_test_1_0_0_all.eap`, start through `control.cgi`, poll `systemlog.cgi` once a second until the text `Done` appears, store the log in `/tmp/larod_out.txt`. The manifest sets `runMode: never` so the workflow starts the app.[^mz-benchmark] | install step |
| 5. Parse and commit | `readme_update.py` rewrites the `<!--TOKEN--> value ms <!--end_TOKEN-->` cells; the workflow then commits "Updating test results" and pushes inside a retry loop.[^mz-benchmark][^mz-readme-update] | final step |
| Cleanup | `teardown.yml` (manual) stops and removes the app on `camera1`–`camera4`.[^mz-teardown] | teardown matrix |

## What `larod_test.sh` measures

The app reads the product number (`root.Brand.ProdNbr`) and SoC (`root.Properties.System.Soc`) with `parhandclient`, picks a model folder and larod backend, and for every file runs `larod-client -R 1000 -w 5 -p -c <chip> -g <file> -i ''`, keeping the line "Mean execution time for job:". It prints `Done` at the end.[^mz-larod-sh]

| SoC string | Model folder | larod chip |
| --- | --- | --- |
| Ambarella CV25 | `models/cv25/` | `ambarella-cvflow` |
| Axis Artpec-9 | `models/artpec9/` | `a9-dlpu-tflite` |
| Axis Artpec-8 | `models/artpec8/` | `axis-a8-dlpu-tflite` |
| Axis Artpec-7 | `models/artpec7/` | `google-edge-tpu-tflite` |

Any other SoC exits 1. The quantity is pure model execution on empty input, not a camera pipeline. The meaning of `-R`/`-w` is not documented anywhere in the repository (**Unverified**; treated here as run count and warm-up).

## How the README cells are updated

`readme_update.py` holds 23 tokens and a dictionary mapping `(model path under ./models, camera product number)` to a token, so the same file maps to different rows for P1465-LE and Q1656-LE. It extracts the product name from the first `Model name:` match and each `result:` line with a regex, rewrites the file, and re-reads it between tokens (a fix for lost updates). Tokens missing from the log only print "Can't find token".[^mz-readme-update] To add a model, copy it to `models/`, link it into the app folder, add a README row with a unique tag and extend the dictionary.[^mz-readme]

## Standalone tester: `scripts/model_performance_tester.py`

It connects with `paramiko` (SSH, `AutoAddPolicy`), uploads the model through SFTP to `/tmp`, runs `larod-client -R <duration> -p -c <larod device> -g <model> -i ""`, parses the last decimal in the "Mean execution time for job" line, and removes the files. CLI: `--model_path`, `--test_duration` (default 100), `--chip` (`CPU`→`cpu-tflite`, `A9-DLPU`, `A8-DLPU`, `A7-GPU`→`axis-a7-gpu-tflite`, `A7-TPU`, `CV25`), `--device_ip`, `--device_port` (22), `--device_credentials USER PASS`.[^mz-perf-tester]

## Verified defects and drifts

Severity is the explorer's judgement; each was confirmed by reading the cited file (**Observed**), none by running.

| # | Finding | Locator |
| --- | --- | --- |
| 1 | The workflow declares `contents: read` yet runs `git push`; the push is expected to be refused. | `benchmark.yml` permissions vs final step |
| 2 | After a failed push, the next loop iteration finds nothing to commit, `grep` matches "nothing to commit", `RET` becomes 0 and the job ends successfully with results stranded on the runner. | `benchmark.yml` retry loop |
| 3 | Readiness, log-harvest and retry loops have no timeout; a crashed app leaves the job waiting for `Done` until the runner limit. | `benchmark.yml` loops |
| 4 | `ARCH` build-arg is never passed, so all cameras (including ARTPEC-9) build with `armv7hf`; the documented `device` values omit `artpec7` and list `cpu`/`edgetpu` for which no model folder exists. | `Dockerfile`, `larod-test/README.md`[^mz-larod-readme] |
| 5 | Four README rows (CV25 YOLOv5s, three CV75 rows) have no tokens, no model folder and no CV75 camera, so they cannot be auto-refreshed. | `readme_update.py::tokens`, matrix |
| 6 | `teardown.yml` omits `camera5`, leaving the ARTPEC-9 test app installed. | `teardown.yml` matrix |
| 7 | The SDK image is pinned at `12.0.0` while the table claims 12.11.72, and Renovate is configured not to bump Dockerfiles ([CI and maintenance](axis-model-zoo-ci-and-maintenance.md)). | `Dockerfile` ARG VERSION |
| 8 | Parsing depends on `echo $result > /tmp/larod_out.txt` (unquoted, collapses newlines) and a regex with an unescaped dot; the paths `/tmp/larod_out.txt` and `README.md` are hard-coded. | `benchmark.yml`, `readme_update.py` |
| 9 | Standalone tester omits `-w 5` warm-up and defaults to 100 runs versus 1000 with warm-up in the table pipeline, so its numbers are not directly comparable; it swallows parse errors (exit code 0), takes the password on the command line and trusts any SSH host key; `paramiko` is an undeclared dependency. | `model_performance_tester.py` |
| 10 | Documentation drift: `larod-test/README.md` omits `artpec9/` in its tree; the README says `<DURATION>` is "the number of inferences" while the code passes it as `-R`. | READMEs |

## Relationships

- **Part of:** [Axis Model Zoo repository](axis-model-zoo-repository.md).
- **Produces:** speed column of [benchmark results](axis-model-zoo-benchmark-results.md); inputs are the [model files](axis-model-zoo-model-files-and-licensing.md).
- **Maintained under:** [CI and maintenance](axis-model-zoo-ci-and-maintenance.md).
- **Related ACAP techniques:** larod usage in [Larod examples](acap-example-larod-object-detection.md), the [Runtime ML API](acap-runtime-machine-learning-api.md), device [developer mode and SSH](axis-device-ssh-developer-mode.md).
- **Official guidance on testing models:** the developer-site "Test your model" page is linked by the README but was not ingested.[^mz-readme]

## Evidence class

Pipeline mechanics and defects are **Observed**; the interpretation of `-R`/`-w` and of the failing push (permission semantics of the platform) is **Synthesis**.

[^mz-readme]: `README.md` §Speed measure (flow description, `model_performance_tester.py` usage and chip list); intro sentence on AXIS OS releases.
[^mz-benchmark]: `.github/workflows/benchmark.yml` — `on`, `permissions`, `strategy.matrix.arch`, reboot/systemready, MotionAdaptiveExposure, build, upload/start/log loop, commit-and-push retry loop; `git log` for `d340d8f`.
[^mz-larod-sh]: `scripts/auto-test-framework/larod-test/app/larod_test.sh` — SoC dispatch, `larod-client -R 1000 -w 5 -p` loop, `Done`.
[^mz-larod-docker]: `scripts/auto-test-framework/larod-test/Dockerfile` — `ARG ARCH/VERSION/UBUNTU_VERSION`, `acap-build . -a "models/${device}/"`.
[^mz-larod-readme]: `scripts/auto-test-framework/larod-test/README.md` — structure tree, `--build-arg device` list, licence section.
[^mz-readme-update]: `scripts/auto-test-framework/readme_update.py` — `tokens`, `token_parameters`, `extract_inference_time`, `rewrite_md_file`, `main`.
[^mz-perf-tester]: `scripts/model_performance_tester.py` — `chipset`, `run_speed_test`, argparse block.
[^mz-teardown]: `.github/workflows/teardown.yml` — matrix `camera1`–`camera4`, `control.cgi` stop/remove.
