---
type: Concept
title: "ACAP Native SDK examples: shared build, manifest and install conventions"
description: "The Dockerfile, acap-build, manifest and install pattern every acap-native-sdk-examples app follows, the build-arg and manifest-variant switches (ARCH, CHIP, VDO_FORMAT), a privilege matrix per example, and the Dockerfile defaults that differ."
tags: [edge-ai, axis, acap, examples, build, manifest, docker]
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

# ACAP Native SDK examples: shared build, manifest and install conventions

All 38 SDK-based Dockerfiles in the examples repository use the same header and the same build step, so one recipe builds nearly every example: `docker build --platform=linux/amd64 --build-arg ARCH=<armv7hf|aarch64> --tag <IMAGE> .`, then `docker cp $(docker create <IMAGE>):/opt/app ./build` to extract the `.eap`, then upload it in the device web UI (Apps → "Allow unsigned apps" → Add app) and switch the app on.[^native-examples] This page records that pattern, the switches individual examples add, and the manifest settings that differ.

## Dockerfile pattern

- Header (`<example>/Dockerfile`, lines 1–7): `ARG ARCH`, `VERSION=12.11.0`, `UBUNTU_VERSION=24.04`, `REPO=axisecp`, `SDK=acap-native-sdk`, then `FROM ${REPO}/${SDK}:${VERSION}-${ARCH}-ubuntu${UBUNTU_VERSION}`. `VERSION` and `UBUNTU_VERSION` have exactly one value repo-wide; the SDK version for each example is therefore chosen in its Dockerfile, which is what the root README's issue guidance refers to.[^native-examples]
- Build step: `COPY ./app /opt/app/`, `WORKDIR /opt/app`, `RUN . /opt/axis/acapsdk/environment-setup* && acap-build .`. The environment script sets the cross compiler and `SDKTARGETSYSROOT`; `acap-build` compiles through the app `Makefile`, reads `manifest.json` and writes `<friendlyName or appName>_<version>_<arch>.eap`. Packaging internals are in [Build, install, and control ACAP applications](acap-build-install-control.md) and the SDK image in [Native SDK image assembly](acap-native-sdk-image-assembly.md).
- Default `ARCH` differs: 34 Dockerfiles default to `armv7hf`, five to `aarch64` (`ptz-control-ws-api`, `object-detection-cv25`, `object-detection-yolov5`, `axoverlay2-skia`, `container-example`), and `message-broker/consume-scene-metadata/Dockerfile` has an empty default, so a plain `docker build` there produces an invalid image reference.
- `container-example/Dockerfile` hardcodes `${REPO}/acap-native-sdk` instead of `${SDK}`.
- Extra pinned build arguments seen in individual Dockerfiles: `SKIA_VERSION=chrome/m137`, `OPENCV_VERSION=4.10.0`, `JPEGTURBO_VERSION=3.0.3`, `URIPARSER_VERSION=0.9.8`, `CIVETWEB_VERSION=v1.16`, `GDB_VERSION=9.2`, `OPENSSL_VER=1.1.1m`, `CURL_VER=7_83_1`.
- The three `tensorflow-to-larod*` Dockerfiles are training containers on TensorFlow images, not SDK images ([guides](acap-example-model-training-guides.md)); `object-detection-yolov5` is multi-stage with `tensorflow/tensorflow:2.21.0` plus the SDK.

## Selector switches

| Switch | Mechanism | Examples |
| --- | --- | --- |
| `ARCH` | `--build-arg ARCH=armv7hf` or `aarch64` selects the SDK image tag | all |
| `CHIP` | `--build-arg CHIP=<artpec8|artpec9|cpu|cv25|edgetpu>`; Dockerfile downloads the matching model and copies `manifest.json.<CHIP>` to `manifest.json` | `vdo-larod`, `object-detection`, `object-detection-yolov5` ([Larod page](acap-example-larod-object-detection.md)) |
| `VDO_FORMAT` | `ARG VDO_FORMAT` copies `manifest.json.<format>`; eight variants `av1 avif h264 h265 jpeg nv12 rgb y800` | `vdostream` ([VDO page](acap-example-vdo-video-capture-and-opencl.md)) |
| `TIMESTAMP` | exported as `SOURCE_DATE_EPOCH` before `acap-build` | `reproducible-package` ([page](acap-example-minimal-shell-and-reproducible-package.md)) |
| `BUILD_PROXY`, `APP_DEBUG` | proxy for the build-time `openssl s_client`; verbose curl | `curl-openssl`, `openssl_curl_example` |

Extra files go into the package with `acap-build . -a <file>` (models, labels, certificates, the OpenCL kernel, `alpine.tar`).[^native-examples]

## Manifest conventions

Every checked manifest uses `schemaVersion` `2.2.0`, `vendor` "Axis Communications", `version` 1.0.0, `runMode` `"never"` and `compatibleOsVersions: [{"max": "13"}]`; `ptz-control-ws-api` adds `min` `"12.11"`. `vendorId` is `1234567890` except the axoverlay examples (`0123456789`). The `appName` fixes the install path `/usr/local/packages/<appName>/`, which several examples hard-code in source. Because `runMode` is `never`, no example starts by itself after install. The schema itself is described in [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md) and the `max: 13` bound relates to [Preparing applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md).[^native-examples]

### Privilege matrix (observed `resources` and related keys)

| Need | Manifest setting | Examples |
| --- | --- | --- |
| Video frames | `linux.user.groups: ["video"]` | `vdostream` (not its jpeg variant), `bounding-box` |
| GPU | `groups: ["gpu"]` | `vdo-opencl-filtering` (with `video`), `axoverlay2-skia` |
| Audio | `groups: ["pipewire"]` | `audio-capture`, `audio-playback` |
| Serial port | `groups: ["admin"]` | `axserialport` |
| Storage | `groups: ["storage"]` | `axstorage` |
| Overlay (legacy) | `dbus.requiredMethods: com.axis.Graphics2.*, com.axis.Overlay2.*` | `axoverlay`, `bounding-box`, `object-detection*` |
| Overlay 2 | `resources.overlay: {enabled: true, required: true}` | `axoverlay2`, `axoverlay2-skia` |
| Recording | `dbus.requiredMethods` for `Search1.ListSpans`, `Search1.GetSpanAttributes`, `Playback1.GetSegment` | `recording-playback` |
| VAPIX credentials | `dbus.requiredMethods: com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials` | `ptz-control-ws-api` and [vapix](acap-vapix-service-account-access.md) |
| Device Data Hub | `resources.deviceDataHub.enabled: true` (`deviceDataHub_beta2` in PTZ) | [DDH examples](acap-example-device-data-hub-and-message-broker.md) |
| Deep learning processor | `deepLearningProcessor` resource in ARTPEC-8/9 variants | [Larod page](acap-example-larod-object-detection.md) |
| Hooks / copy protection | `installation.postInstallScript`, `uninstallation.preUninstallScript`; `copyProtection.method: axis` | `container-example`; `licensekey` |
| Parameters | `configuration.paramConfig` | `axparameter`, `object-detection-yolov5` |
| None | no `resources` | `hello-world`, `axevent`, `message-broker`, `curl-openssl`, `using-opencv`, `utility-libraries` |

`shell-script-example` sets `architecture: "all"` and yields `*_all.eap`.[^native-examples] This matrix is **Observed** from the manifests; whether a given resource is sufficient on a given AXIS OS version was not tested. Dynamic application-user rules are in [ACAP application user types and permissions](acap-application-user-permissions.md).

## Install and read results

README steps are uniform: unsigned install through the Apps page (see [signing](acap-application-signing.md) for why unsigned installs end at AXIS OS 13), start the app, then read the app log from `http://<AXIS_DEVICE_IP>/axis-cgi/admin/systemlog.cgi?appname=<appName>` or the web UI. The READMEs of 37 of 49 example directories mention "Allow unsigned"; none documents a VAPIX `upload.cgi` install, which is covered in [Deploying to many devices](acap-fleet-deployment-via-vapix.md).[^native-examples] Logs are written with `syslog`.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Uses** the SDK image from [ACAP Native SDK repository](acap-native-sdk-repository.md).
- **Complements** [Create, build and install your first ACAP application](acap-first-application-workflow.md).

[^native-examples]: Per-example `Dockerfile` (ARG block and `acap-build` line), `app/manifest.json*`, `README.md` build sections across the repository; `README.md` §"Issues"; `DEV.md` §"Logs and reports"; ARG tabulation by `grep` over all Dockerfiles; `container-example/Dockerfile:8`; `message-broker/consume-scene-metadata/Dockerfile:1`.
