---
type: Concept
title: "ACAP Native SDK examples repository: catalog, layout and coverage ledger"
description: "What AxisCommunications/acap-native-sdk-examples contains at 12.11.0-7: about 35 example directories grouped by use case, the shared layout, license, revision, where each example is compiled in this wiki, and a ledger of what was and was not inspected."
tags: [edge-ai, axis, acap, examples, repository, native-sdk]
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

# ACAP Native SDK examples repository: catalog, layout and coverage ledger

`acap-native-sdk-examples` is Axis's official set of small, self-contained ACAP Native SDK applications. Each example is a directory with a `Dockerfile`, an `app/` folder (source, `Makefile`, `manifest.json`, `LICENSE`) and a README with build, install and expected-output steps; every example builds with the published `axisecp/acap-native-sdk` image and is packaged as an `.eap` by `acap-build`.[^native-examples] The root README only lists the examples by group and points to the Axis documentation, `DEV.md` and the Docker Hub image; the technical content is in the per-example READMEs and code, which this wiki compiles in the pages linked below.

## Identity

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/AxisCommunications/acap-native-sdk-examples` (git remote `origin`), vendored as a submodule at `raw/acap-native-sdk-examples/` |
| Revision | `3025a4e9db74f1af5bb878d4efc82ac0e300a792` on `main`, `git describe` = `12.11.0-7-g3025a4e`, commit date 2026-09-01 (subject "Update CODEOWNERS"); latest tag `12.11.0`, 28 tags |
| SDK version used | every SDK-based Dockerfile pins `VERSION=12.11.0` on Ubuntu 24.04 |
| License | Apache License 2.0 at the root and in nearly every `app/LICENSE` (exceptions: [device-data-hub](acap-example-device-data-hub-and-message-broker.md), [ptz-control-ws-api](acap-example-ptz-control-ws-api.md), [recording-playback](acap-example-storage-serial-recording-licensekey.md) and [axoverlay2 and axoverlay2-skia](acap-example-overlays-and-bounding-box.md) carry MIT text) |
| Size | 430 tracked files, 49 READMEs, 41 Dockerfiles, 35 top-level example directories |

Evidence class: **Observed** from static inspection of the working tree and `git`; **Reported** where a README is the only source. Nothing was built or run on a device.[^native-examples]

## Example catalog

The README groups the examples as follows (`README.md`, "Example applications"); the right-hand column names the wiki page that compiles each one.[^native-examples]

| Group | Examples | Compiled in |
| --- | --- | --- |
| Introduction | `hello-world` | [Minimal, shell-script and reproducible-package examples](acap-example-minimal-shell-and-reproducible-package.md) |
| Streaming video | `vdostream` | [VDO video capture and OpenCL filtering](acap-example-vdo-video-capture-and-opencl.md) |
| Audio | `audio-capture`, `audio-playback` | [PipeWire audio examples](acap-example-audio-pipewire.md) |
| Machine learning: object detection | `object-detection`, `object-detection-yolov5` (and `vdo-larod`, listed under training) | [Larod inference examples](acap-example-larod-object-detection.md) |
| Machine learning: CV25 | `object-detection-cv25` | [Object detection on CV25](acap-example-object-detection-cv25.md) |
| Machine learning: train and convert | `tensorflow-to-larod`, `-artpec8`, `-artpec9`, `-cv25`, `vdo-larod` | [Model training and conversion guides](acap-example-model-training-guides.md); `vdo-larod` in the Larod page |
| Custom libraries | `using-opencv`, `utility-libraries` (plus `curl-openssl` under networking) | [Bundling third-party libraries](acap-example-bundled-libraries-opencv-curl-openssl.md) |
| Graphical components | `axoverlay`, `axoverlay2`, `axoverlay2-skia`, `bounding-box`, `vdo-opencl-filtering` | [Overlays and bounding boxes](acap-example-overlays-and-bounding-box.md); OpenCL in the VDO page |
| Networking and web | `curl-openssl`, `web-server/*` | [Bundling libraries](acap-example-bundled-libraries-opencv-curl-openssl.md); [web server](acap-web-server-reverse-proxy-fastcgi.md) |
| Event handling | `axevent` | [Events and parameters](acap-example-events-and-parameters.md) |
| Parameter handling | `axparameter` | [Events and parameters](acap-example-events-and-parameters.md) |
| Debugging and testing | `remote-debug-example` | [Remote debugging ACAP applications](acap-remote-debugging.md) |
| Container applications | `container-example` | [Containers inside a native ACAP](acap-example-container-in-native-acap.md) |
| Miscellaneous | `axserialport`, `axstorage`, `licensekey`, `recording-playback` | [Storage, serial, recording and licensekey](acap-example-storage-serial-recording-licensekey.md) |
| Miscellaneous | `message-broker`, `device-data-hub` | [Device Data Hub and Message Broker](acap-example-device-data-hub-and-message-broker.md) |
| Miscellaneous | `ptz-control-ws-api` | [PTZ control over WebSocket](acap-example-ptz-control-ws-api.md) |
| Miscellaneous | `reproducible-package`, `shell-script-example` | [Minimal, shell-script and reproducible-package examples](acap-example-minimal-shell-and-reproducible-package.md) |
| Miscellaneous | `vapix` | [VAPIX access from ACAP applications](acap-vapix-service-account-access.md) |

Repo-wide build, manifest and install behaviour is in [Build and manifest conventions](acap-examples-build-and-manifest-conventions.md); contribution rules, linters and CI are in [Contribution, lint and CI](acap-examples-contribution-lint-and-ci.md).

## Layout

- Minimum layout per example: `example/{app/{source, LICENSE, Makefile, manifest.json}, Dockerfile, README.md}` (`EXAMPLE_GUIDELINES.md`, "Minimum layout"). Observed exceptions: `container-example` keeps its files at the example root; the three `tensorflow-to-larod*` guides with code have `env/` instead of `app/`; `tensorflow-to-larod-artpec9` holds only a README; `shell-script-example` has no `Makefile`.[^native-examples]
- Multi-example directories: `axevent` (3 apps), `device-data-hub` (4), `message-broker` (1), `utility-libraries` (2), `web-server` (2).
- Hidden repo files carry the lint and CI setup (`.github/`, `.clang-format`, `.hadolint.yaml`, `.markdownlint.yml`, `.textlintrc`, `.yamllint.yml`, `.eslintrc.yml`, `.vscode/`, `.editorconfig`, `.gitignore`).
- `DEV.md` covers only SSH access, Developer Mode (AXIS OS 11.11+), reading system, app and server-report logs through `systemlog.cgi`/`serverreport.cgi`, and proxy use at build time and run time. The root README advertises it for "migrating from an old version of ACAP SDK", but it contains no migration notes (`DEV.md`; `README.md`, "ACAP application development").[^native-examples] Developer Mode and SSH are explained in [SSH and Developer Mode on Axis devices](axis-device-ssh-developer-mode.md); logging in [Application logging in ACAP](acap-application-logging.md).

## Cross-cutting findings

- **Observed:** most README log samples and file names drift from the code; examples include [axoverlay](acap-example-overlays-and-bounding-box.md), [vdostream](acap-example-vdo-video-capture-and-opencl.md), [axstorage](acap-example-storage-serial-recording-licensekey.md) and [memory-cpu-utilization](acap-example-device-data-hub-and-message-broker.md). Treat code as the authority and READMEs as orientation.
- **Observed:** every example runs with `runMode: "never"`, so the app must be started manually after install; all manifests use `schemaVersion` 2.2.0 and `compatibleOsVersions.max` `"13"` (see [Build and manifest conventions](acap-examples-build-and-manifest-conventions.md)).
- **Synthesis:** the repository is the Native-SDK successor to [the archived CV SDK examples](acap-cv-sdk-examples-repository.md): the same use cases (inference, MJPEG-like capture, web server, parameter access) run directly on the device without Docker ACAP, Runtime or gRPC.

## Coverage ledger

| Artifact | State |
| --- | --- |
| Root README, `DEV.md`, `EXAMPLE_GUIDELINES.md`, `LINT.md`, `CONTRIBUTING.md`, `CODEOWNERS` | inspected |
| `.github/` (49 files: 4 linter and 31 example workflows, custom linters, utils, renovate, super-linter env) and dot-config files | inspected; `diff`/`grep` used for repetitive workflows |
| README, `Dockerfile`, manifest(s), `Makefile` and main sources of all 35 example directories | inspected by six parallel read-only explorers; consequential claims (argument handling in `vdo-larod`, truncated thresholds in `object-detection-cv25`, `&start_value` in `send_event`, topic names in `memory-cpu-utilization`, the dummy ARTPEC-9 workflow, `renovate.json`, `deviceDataHub_beta2`) were re-checked against the files |
| `vapix/` and `web-server/` | covered earlier in [VAPIX access](acap-vapix-service-account-access.md) and [web server](acap-web-server-reverse-proxy-fastcgi.md); not re-derived here |
| Image assets (`bbox.jpeg`, `bbox-view.jpeg`, `screenshot.jpg` ×2, `object-detection*.jpeg`, `loopback-diagram.png`, SVGs) | listed; not interpreted visually — READMEs' captions are the only source |
| `vdostream/app/manifest.json.jpeg` | a manifest variant (the name only looks like an image) |
| Downloaded models (`acap-ml-models.s3.amazonaws.com`, Coral `test_data`), Skia, OpenCV, OpenSSL, curl, GDB, CivetWeb sources, base images | not local; behaviour is inferred from Dockerfiles |
| Execution | none: no builds, no device runs, no scripts executed |

## Relationships

- **Depends on** [ACAP Native SDK and platform](axis-acap-native-sdk.md) and its image, described in [ACAP Native SDK repository](acap-native-sdk-repository.md).
- **Supersedes** the weaker coverage statements in [Official ACAP application examples](acap-application-examples.md), which previously described this repository only from vendor documentation.
- **Counterpart of** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).

[^native-examples]: `raw/acap-native-sdk-examples/README.md`, §"Example applications" and §"Getting started with the repository"; `EXAMPLE_GUIDELINES.md` §"Minimum layout"; `DEV.md`; `git describe` and `git log -1` at the submodule root; file counts from `find` over the working tree excluding `.git`.
