---
type: Concept
title: "ACAP Runtime test suite: gtest on-device app and the pytest device runner"
description: "How ACAP Runtime is tested: one gtest binary shipped as the Acapruntimetest ACAP with gRPC and in-process inference suites plus a Parameter API test, the pytest runner that installs and runs it on real cameras, what it asserts, and what it does not cover."
tags: [edge-ai, axis, acap, acap-runtime, testing, gtest, pytest, larod]
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
    title: "ACAP Runtime README (§Test suite)"
  - id: rt-inferencetest
    resource: ../raw/acap-runtime/test/inference_test.cc
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "inference_test.cc — gRPC-level inference tests"
  - id: rt-unittest
    resource: ../raw/acap-runtime/test/inference_unittest.cc
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "inference_unittest.cc — in-process inference tests"
  - id: rt-runner
    resource: ../raw/acap-runtime/.github/test/test_acapruntimetest.py
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "test_acapruntimetest.py — device runner"
  - id: rt-testdata
    resource: ../raw/acap-runtime/test/testdata.h
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "testdata.h and test helpers (bitmap, memory_use, verbose_setting)"
---

# ACAP Runtime test suite: gtest on-device app and the pytest device runner

Runtime tests do not run on a developer host. They are compiled into **one GoogleTest binary**, packaged as a standalone ACAP called `Acapruntimetest` (`appName acapruntimetest`, built with `TEST=yes`), installed on a real camera, and judged by a Python runner that reads the app's syslog. The README describes the manual route: build the `-test` image, `docker run … install`, start from the device GUI or `start|stop|remove`, read the log at `…/axis-cgi/admin/systemlog.cgi?appname=acapruntimetest`, and look for `[  PASSED  ]`.[^rt-readme]

## Test suites

| Suite | File | Scope |
| --- | --- | --- |
| `InferenceTest` | `test/inference_test.cc` | Machine learning API **over gRPC**: server started in a thread, client on `unix:///tmp/acap-runtime.sock`; CPU, DLPU (aarch64) and TPU (armv7hf) models, TLS authentication, preloaded versus on-demand model, failure for an unknown model |
| `InferenceUnittest` | `test/inference_unittest.cc` | the same models by calling `Inference::Predict()` **in-process** with a `ServerContext` |
| `ParameterTest` | `test/parameter_test.cc` | `GetValues` for `root.Brand.Brand`, `root.Brand.WebURL`, `root.Image.I0.Enabled` and an invalid key |

Chips: CPU `2`, TPU `4`, DLPU `12`. Server spin-up builds an argv such as `acapruntime [-v] -p 0 -t <s> -j <chip> [-c cert -k key] [-m model]` and calls `AcapRuntime()` in a `std::thread` (the reason the real `main` is a shim).[^rt-inferencetest][^rt-unittest]

**What is asserted.** For the SSD MobileNet v2 detector, output sizes `80/20/20/1` floats, `count == 20`, first classes `0` and `31` and exact scores with `EXPECT_FLOAT_EQ` (ARM and x86 constants differ); for MobileNet v2 and EfficientNet classifiers, an argmax class index (`653`, `458`) and a fixed score. Both input paths are exercised: shared memory (`shm_open` plus a `DT_STRING` tensor) and copied `tensor_content` (`DT_UINT8`). Timing is printed but never asserted; memory (RSS from `/proc/self/statm`) is logged only inside disabled tests.[^rt-inferencetest]

**Required on-device files**, all under `/usr/local/packages/acapruntimetest/testdata/`: `server.pem`, `server.key`, `coco_labels.txt`, three `.tflite` model families (plus `_edgetpu` variants) and two Grace Hopper BMPs. Only two of the repo's BMPs are tracked (`grace_hopper_300x300.bmp`, and `solid_300x300.bmp`, used by no test); certificates, labels and models are fetched by the Dockerfile `testdata` stage, so `make test` on a bare checkout cannot run.[^rt-testdata]

## The device runner

`.github/test/test_acapruntimetest.py` needs `AXIS_TARGET_ADDR`, `AXIS_TARGET_ARCH`, `AXIS_TARGET_USER`, `AXIS_TARGET_PASS` and `ACAP_DOCKER_IMAGE_NAME` (optional `AXIS_EXTERNAL_POOL` switches basic auth and the install path). Flow:[^rt-runner]

1. Wait for `systemready.cgi`; check the architecture against `basicdeviceinfo.cgi getAllProperties`.
2. Install: `docker run --rm <image> <ip> <pw> install`, or with an external device pool extract the `.eap` from the image and POST it to `upload.cgi`.
3. Start the app; require exactly one `Running main() from` line; poll `systemlog.cgi?appname=acapruntimetest` every 5 s (30 s initial sleep, 3-minute cap) for `Global test environment tear-down`.
4. Parse `[ RUN ]`/`[ OK ]`/`[ FAILED ]` and the totals; pass only if every test passed.
5. Teardown: stop, remove, verify removal, **always reboot**, wait up to 360 s.

CI wiring (matrix `armv7hf`, `aarch64`, devices reached through a device-server proxy, `pytest-action` with Python 3.9, log uploaded on failure) is in [CI and maintenance](acap-runtime-ci-and-maintenance.md).

## Coverage gaps and fragilities (Observed)

- **Video capture API is untested**; the inference tests pass a stub `Capture`. The network-socket path (`-a`, non-zero `-p`) and the legacy `-o` override are never exercised.
- **TLS**: only the happy path with a local self-signed cert and a target-name override; the "insecure client must fail" test is `DISABLED_`. No client-certificate, wrong-cert or hostname tests.
- Disabled tests: `DISABLED_PredictDlpuModel3` (EfficientNet on DLPU fails to load, in both suites) and the 24-hour `DISABLED_PredictLoop`.
- Expected values are architecture-, model- and firmware-specific; `ParameterTest` asserts `AXIS` and a camera-specific `Enabled=yes`.
- Hard-coded paths and a root-level shared-memory name `/test.bmp` with `O_CREAT|O_EXCL`, which fails if a stale segment survives a crash.
- Helper robustness: `ReadImage` has no `fopen` NULL check (a missing BMP segfaults); empty-string argv elements are passed in place of omitting `-v`; `ASSERT_*` in helpers and threads only returns from the helper; `memory_use()` returns `size_t` as `int`.
- Runner robustness: the syslog is not cleared yet exactly one `Running main() from` is required, so a persisted entry fails the run; the 3-minute cap is tight; the README's "log ends with `[  PASSED  ]`" is not what the runner checks.[^rt-runner]

## Relationships

- **Tests:** [Machine learning API](acap-runtime-machine-learning-api.md) and [Parameter API](acap-runtime-parameter-api.md); [Video capture API](acap-runtime-video-capture-api.md) is not covered.
- **Built by:** [Build and image packaging](acap-runtime-build-and-image-packaging.md) (`TEST` switch).
- **Uses:** the legacy native-eap install path (`upload.cgi`), compare [Fleet deployment via VAPIX](acap-fleet-deployment-via-vapix.md).
- **Run by:** [CI and maintenance](acap-runtime-ci-and-maintenance.md).
- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md).

## Evidence class

**Observed** by reading the test sources and runner; nothing was built or run, so pass/fail on any device, and whether the pinned scores hold on newer TF Lite runtimes, is **Unverified**.

[^rt-readme]: `README.md` §Test suite.
[^rt-inferencetest]: `test/inference_test.cc::{Service (L66-77), ServiceSecurity (L79-99), ServiceModel (L101-121), chip ids (L42-44), tests (L415-755)}`; `test/memory_use.cc` L25-36; `test/verbose_setting.cc` L24-26; `test/bitmap.cc` L46-50; `manifest-test.json` L17-25.
[^rt-unittest]: `test/inference_unittest.cc::{InferenceUnittest tests (L309-615), chip ids (L38-40)}`, `test/parameter_test.cc::ParameterTest.GetValues (L95-120)`.
[^rt-runner]: `.github/test/test_acapruntimetest.py::{verify_required_env_variables (L26-35), setup_method (L91-108), teardown (L109-128), test_method (L131-143), check_acap_test_suite_finished (L196), evaluate_acap_runtime_test_suite_result (L222), check_dut_status (L246), get_dut_info (L287), acap_ctrl (L295)}`; `.github/actions/pytest-action/action.yml` L46.
[^rt-testdata]: `test/testdata.h` L17-31 (paths and file names); `Dockerfile` L48-90 (testdata stage); `testdata/` (two BMPs, 300x300 24-bit).
