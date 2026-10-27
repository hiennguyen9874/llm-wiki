---
type: Concept
title: "Build, install, and control ACAP applications"
description: "Operational ACAP workflow: Dockerfile versus interactive SDK builds, acap-build packaging and manifest rewriting, three install channels, and three ways to start, stop, or remove an app."
tags: [edge-ai, axis, acap, build, deployment]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T18:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-build-install-run
    resource: ../raw/acap/how-to-guides/build-install-run/index.md
    scope: ../raw/acap/how-to-guides/build-install-run/
    kind: docs
    revision: "ACAP version 12"
    title: "Build, install, control | Axis developer documentation"
---

# Build, install, and control ACAP applications

Axis documents the operational half of the ACAP lifecycle as a choice of two build paths — a Dockerfile build for reproducible and CI output, or an interactive shell inside the SDK container for development — followed by three interchangeable delivery channels: the device web GUI, `eap-install.sh` inside the SDK container, and the VAPIX Applications API. The durable value is the division of labor: Docker supplies and runs the toolchain, `acap-build` produces and annotates the `.eap`, and the same package can be installed or controlled through GUI, script, or API without rebuilding.[^acap-build-install-run]

## Two build paths

| Path | Optimized for | Mechanism |
| --- | --- | --- |
| Dockerfile-based | Production, CI/CD, reproducible builds across environments | Docker builds the project from a Dockerfile; all compilation and packaging happen inside a container |
| Interactive | Active development, debugging, iterative testing | The project's `app/` directory is bind-mounted into a running SDK container; commands run in an interactive shell |

Both paths use Docker as the SDK delivery mechanism: the correct SDK image is pulled automatically, cached locally, and reused on later builds. A Dockerfile build is described as the better fit when the application code is stable and the goal is a final deployable package; the interactive path gives immediate feedback and control during development.[^acap-build-install-run]

### Dockerfile-based build

The Dockerfile declares the SDK version, target architecture, Ubuntu version, registry, and SDK repository. The project also keeps its application files in an `app/` directory at the top level.[^acap-build-install-run]

Because that Dockerfile executes inside the SDK container, it is also the place where extra Ubuntu build tooling is installed and where a third-party library is cross-compiled and copied into `app/lib` before packaging — the `lib/` folder `acap-build` includes in the `.eap`. That extension of the Dockerfile path is covered in [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md).

```bash
docker build --build-arg ARCH=<ARCH> --tag <APP_IMAGE> .
```

- `<ARCH>` is `armv7hf` or `aarch64`; omitting `--build-arg` uses the `ARCH` value declared in the Dockerfile.
- `<APP_IMAGE>` is the Docker image name and tag, for example `my_acap:1.0`.
- The image tag is **not** the application version. The real version comes from `acapPackageConf.setup.version` in `manifest.json`.
- On Apple Silicon, add `--platform=linux/amd64` to `docker build` and `docker create` to suppress the `InvalidBaseImagePlatform` warning.

After the build, `docker image ls` confirms the image exists, and the package files are copied out of a temporary container into a local `build/` directory:[^acap-build-install-run]

```bash
docker cp $(docker create <APP_IMAGE>):/opt/app ./build
```

The resulting `build/` contains the executable, `<APP_NAME>_<VERSION>_<ARCH>.eap`, a copy of `LICENSE`, `manifest.json`, `package.conf`, `package.conf.orig`, `param.conf`, and the original sources. The documentation calls this layout a generic example; real projects may add files.[^acap-build-install-run]

### Interactive build inside the SDK container

Run the SDK image from the directory that contains `app/`, bind-mounting that directory to `/opt/app`:[^acap-build-install-run]

```bash
docker run -v $PWD/app:/opt/app --rm -i -t axisecp/acap-native-sdk:<SDK_VERSION>-<ARCH>-<UBUNTU_VERSION>
```

`--rm` removes the container on exit, `-i` keeps stdin open, and `-t` allocates a TTY. The image tag combines SDK version, architecture, and Ubuntu base, for example `12.6.0-armv7hf-ubuntu24.04` or `12.6.0-aarch64-ubuntu24.04`. On Apple Silicon, add `--platform=linux/amd64` to `docker run`. After startup the prompt appears inside `/opt/app`, and edits made there are reflected in the host's `$PWD/app` through the bind mount.[^acap-build-install-run]

## Packaging with acap-build

Inside the container, `acap-build .` compiles and packages the application into an `.eap` file. Its documented behavior is broader than running `make`:[^acap-build-install-run]

- Runs `make`, including the cross-compilation defined in the Makefile.
- Rewrites only the `manifest.json` **inside the EAP**, not the project's original manifest:
  - sets `schemaVersion` to the highest schema version available in the SDK within the same major version (introduced in SDK 12.11.0);
  - sets `architecture` from the SDK architecture if omitted;
  - sets `compatibleOsVersions.min` to the AXIS OS version the SDK is based on when omitted and `schemaVersion` is v2.x or later (introduced in SDK 12.10.0).
- Validates the manifest against the manifest schema.
- Generates `package.conf` and related files for backward compatibility.
- Creates the `.eap`, including the executable, `LICENSE`, any `html/` and `lib/` folders, postinstall and preuninstall scripts named in `manifest.json`, files listed with `-a`, and the generated compatibility files.

**Synthesis:** because the `schemaVersion` rewrite is confined to the same major version, moving from schema 1.x to 2.x is a manual manifest upgrade, not something `acap-build` performs; see [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md).[^acap-build-install-run]

`acap-build -h` lists the remaining options. The guide also states an operational constraint: systemd starts and stops the application and treats the main process dying as execution failure, so the process must not fork into the background.[^acap-build-install-run]

## Installing the package

An unsigned application requires **Allow unsigned apps** to be enabled, which may need administrator privileges. That development route ends with AXIS OS 13: from then on applications must be signed, unsigned packages are not installable in the preview release, and `compatibleOsVersions` in the manifest becomes mandatory — see [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md). The GUI path is `http://<AXIS_DEVICE_IP>/index.html#apps` or the **Apps** tab; use **+ Add app**, select the architecture-matched file, and click **Install**:[^acap-build-install-run]

- ARM64: `<APP_NAME>_<VERSION>_aarch64.eap`
- ARMv7: `<APP_NAME>_<VERSION>_armv7hf.eap`

### Installing with eap-install.sh

From the application project directory inside the SDK container, run:[^acap-build-install-run]

```bash
eap-install.sh <axis_device_ip> <admin_account> <password> install
eap-install.sh 192.168.0.90 admin-user admin-password install
```

The script remembers the device IP and password after the first successful run, after which `eap-install.sh install` is enough. If the device is HTTPS-only, the script asks whether to continue with HTTPS despite not supporting certificate verification; accepting makes it call cURL with `-k`/`--insecure`, skipping certificate checks. Running `eap-install.sh` without arguments prints help.[^acap-build-install-run]

### Installing through VAPIX

The VAPIX Applications API exposes upload, start, stop, and remove operations for remote and automated deployment. For unsigned packages, `AllowUnsigned` can be enabled through the VAPIX **Configure Applications** action before uploading.[^acap-build-install-run]

## Controlling an installed application

| Channel | Start / stop | Logs | Remove |
| --- | --- | --- | --- |
| Device web GUI | Toggle the application switch | Three-dot menu → **App log** | Three-dot menu → **Delete** |
| `eap-install.sh` | `eap-install.sh start` / `stop` | Not described in this guide | `eap-install.sh remove` |
| VAPIX Applications API | Control Application endpoint | Not described in this guide | Control Application endpoint |

The `eap-install.sh` control commands assume a prior successful install, because the script reuses the remembered device credentials. The VAPIX API also provides a list-installed-applications endpoint for verifying presence and status.[^acap-build-install-run]

## Coverage and limits

- **Entry point and scope:** `raw/acap/how-to-guides/build-install-run/index.md`, one 2,485-word page under `raw/acap/how-to-guides/build-install-run/`, part of the ACAP 12 documentation on `developer.axis.com`. No subpages, images, or attachments are present in the captured folder.
- **Inspected:** the entire page, including the build, packaging, installation, and control sections and all command examples.
- **Not verified:** linked material outside `raw/` — application project structure, manifest schemas, Docker documentation, and the VAPIX Application API — was not read. Claims that depend on it are reported only as the guide states them. Application signing has since been ingested as [ACAP application signing](acap-application-signing.md), the manifest upgrade as [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md), and the `axparameter` example repository is still absent from `raw/`.
- **No execution:** no Docker build, container run, device install, or VAPIX call was performed. Version-specific behavior (SDK 12.10.0 and 12.11.0 manifest rewriting) is reported, not reproduced.
- **Overlap:** the minimal project and first-build path are covered in more depth by [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md); this page focuses on the operational build choices, `acap-build` packaging behavior, and the install/control channels.

## Evidence class

All substantive claims are **Reported** from Axis's official ACAP 12 documentation, read on 2026-10-27. No claim is **Reproduced**; commands and file names are transcribed from the source and should be checked against the installed SDK and target AXIS OS before being treated as a standard procedure.

## Relationships

- **Environment defined by** [ACAP Native SDK image assembly](acap-native-sdk-image-assembly.md): the SDK image's tools, `eap-install.sh` prerequisites (`curl`, `iputils-ping`) and environment-script patches.
- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): SDK container images, `acap-build`, and `eap-install.sh`.
- **Elaborates** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): same Docker-based build, expanded into production versus interactive paths and GUI/script/API delivery.
- **Elaborated by** [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md): the Dockerfile path extended with build-tool installation, cross-compilation of an external library, and bundling it in `app/lib`.
- **Elaborated by** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md): the interactive container is where the legacy conversion script runs, and `-a` replaces the `OTHERFILES` packaging option.
- **Elaborated by** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): the manifest rewrite performed here is same-major only, so the 1.x-to-2.x upgrade remains a manual step with its own required fields and resource rules.
- **Requires** [Môi trường phát triển ACAP](acap-dev-environment-setup.md) for Docker and editor setup, and [thiết bị Axis đã chuẩn bị](axis-device-setup.md) for network access and credentials.
- **Constrained by** [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): SDK version and `ARCH` must match the target device.
- **Uses** [Application logging trong ACAP](acap-application-logging.md) when inspecting application output through App log or `journalctl`.
- **Needs** signing or **Allow unsigned apps** before installation; from AXIS OS 13 signing is enforced and `compatibleOsVersions` is mandatory ([migration notes](acap-axis-os-13-14-migration.md), [signing paths](acap-application-signing.md)).
- **Extended by** [Deploying an ACAP application to many devices](acap-fleet-deployment-via-vapix.md): the `upload.cgi` and `control.cgi` calls behind the VAPIX channel, scripted for many devices.
- **Uses** Docker locally only; the target device runs the `.eap`, not a container.

[^acap-build-install-run]: Tài liệu chính thức: [Build, install, control — Axis developer documentation](../raw/acap/how-to-guides/build-install-run/index.md), §How to build an ACAP application (Building using a Dockerfile; Building interactively inside the SDK container; The `acap-build` tool), §How to install an ACAP application (web GUI; `eap-install.sh`; VAPIX API), §How to run and control an ACAP application (web GUI; SDK container; VAPIX).
