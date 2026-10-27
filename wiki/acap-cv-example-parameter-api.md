---
type: Concept
title: "CV SDK example: reading device parameters through the ACAP Runtime Parameter API"
description: "How parameter-api-python reads Axis device parameters over a TLS-protected gRPC Unix socket from ACAP Runtime's beta KeyValueStore service: certificate generation at build time, compose wiring, the five hard-coded keys, API limits and defects."
tags: [edge-ai, axis, acap, parameter-api, grpc, tls, acap-runtime, examples]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: cvex-readme
    resource: ../raw/acap-computer-vision-sdk-examples/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "ACAP Computer Vision SDK examples — repository README"
  - id: cvex-param-docs
    resource: ../raw/acap-computer-vision-sdk-examples/parameter-api-python/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "parameter-api-python README"
  - id: cvex-param-code
    resource: ../raw/acap-computer-vision-sdk-examples/parameter-api-python/app/parameter.py
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "parameter-api-python implementation (parameter.py, Dockerfile, compose)"
---

# CV SDK example: reading device parameters through the ACAP Runtime Parameter API

`parameter-api-python` demonstrates the third service of the containerized ACAP Runtime: a **Parameter API** (a gRPC `KeyValueStore`) that lets a container read an Axis device's parameters — for example brand, product number or whether an image source is enabled. It is part of the [CV SDK examples](acap-cv-sdk-examples-repository.md) and is the only one that runs the Runtime with **TLS** on its gRPC channel. The README titles it a *beta* version of the API, and the repository README lists it as reading camera parameters with the beta Parameter API.[^cvex-readme][^cvex-param-docs][^cvex-param-code]

## What the API can do

Per the README, the Parameter API can read parameters only: it **cannot read parameter groups and cannot set values**, and it needs the exact parameter name. The complete list of names is obtained from the device at `http://<ip address>/axis-cgi/param.cgi?action=list`. The example reads five keys — `root.Brand.Brand`, `root.Brand.WebURL`, `root.Image.I0.Enabled`, `root.Brand.ProdFullName`, `root.Brand.ProdNbr` — and prints `name : value`. The README's expected output, from an AXIS Q1615 Mk III, shows `AXIS`, `http://www.axis.com`, `yes`, `AXIS Q1615 Mk III Network Camera` and `Q1615 Mk III`.[^cvex-param-docs][^cvex-param-code]

## Composition

- **Client** (`parameter-api`): the image built from the example, `ENTRYPOINT ["python3","parameter.py","/opt/certificates/server.pem"]`. The Dockerfile uses the standard two-stage pattern (`axisecp/acap-runtime:2.0.1-protofiles` and `ubuntu:24.04`), installs `python3`, `python3-pip`, `python3-venv`, `ca-certificates`, creates `/opt/venv`, copies the generated `keyvaluestore_pb2` modules from `/build/param/proto_utils`, and generates a self-signed certificate at build time: `openssl req -x509 -subj '/CN=localhost' -days 365 -newkey rsa:4096 -nodes` → `/opt/certificates/server.{pem,key}`.[^cvex-param-code]
- **Server** (`acap-runtime`): `axisecp/acap-runtime:2.0.1-aarch64-containerized` started as `acapruntime -k /opt/app/certificates/server.key -c /opt/app/certificates/server.pem`. It mounts the D-Bus socket, **`/run/confcache/confcachesocket`**, `/usr/lib` and `/usr/bin`; the ML examples mount `/run/parhand/parhandsocket` instead, so the Parameter API uses a different device socket than the video/inference services (**Observed**; the repository does not explain why).[^cvex-param-code]
- **Sharing.** Named volumes `acap-runtime` (at `/tmp`, carrying `acap-runtime.sock`) and `parameter-api` (carrying the certificates, copied to the Runtime's `/opt/app/certificates`). The certificate therefore travels image → named volume → Runtime container.[^cvex-param-code]

The generic wiring (Unix socket in a shared volume, device mounts, image pattern) is in [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md).

## Client behavior

`app/parameter.py` hard-codes `target = "unix:///tmp/acap-runtime.sock"` — unlike the other examples it does not read `INFERENCE_HOST`. If a PEM path is passed as `argv[1]`, it creates `grpc.ssl_channel_credentials(root_cert)` with option `grpc.default_authority = localhost` (to match the certificate CN) and a `grpc.secure_channel`; without the argument it falls back to `grpc.insecure_channel`. It builds a `KeyValueStoreStub`, calls `GetValues(Request(key=name))` per key, and catches `grpc.RpcError` to print an error.[^cvex-param-code]

## Defects and risks

- **Credentials in the image.** The private key is generated inside the image layer and the certificate is valid for 365 days; the named volume is only seeded on first creation, so after expiry or an image rebuild the old certificate persists until the volume is removed with `down --volumes` (**Synthesis** from the compose and Dockerfile behavior). It is a demo credential for a loopback-only socket, not a secret of value, but it should not be reused.
- **Dead insecure branch.** Compose always passes the certificate path, so the `insecure_channel` fallback is unused under this deployment.
- **Error handling.** `err.details` is printed without calling it; in grpc `RpcError`, `details` is a method, so the message would show a bound method rather than text (**Observed**, expected-behavior caveat not executed).
- **Hard-coded socket path** and a README title that still says "Beta" while the examples pin Runtime 2.0.1.
- **Repository hygiene.** `CODEOWNERS` and `.gitignore` refer to `parameter-api-cpp` and `parameter-api/models`, neither of which exists ([CI and maintenance](acap-cv-examples-ci-and-maintenance.md)).

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Uses:** [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md) — the Parameter service, whose proto, key regex and empty-on-error behaviour are in [ACAP Runtime Parameter API](acap-runtime-parameter-api.md).
- **Compare (synthesis):** a native ACAP reads parameters in process through `AXParameter`, as in [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md); a container does not use that library in these examples and goes through the Runtime instead.
- **Deploy:** [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md); no `--env-file` is needed beyond exporting `APP_NAME`.

## Source coverage

- Inspected statically: `README.md`, `Dockerfile`, `docker-compose.yml`, `app/parameter.py`. The Runtime's Parameter service protocol is now read in [ACAP Runtime Parameter API](acap-runtime-parameter-api.md) (`keyvaluestore.proto`). Not verified: the `confcache` socket's role, the meaning of "beta", or any device output. Nothing was executed.

## Evidence class

Flow and configuration are **Observed**; API limits, requirements and sample output are **Reported** by the README; the key-lifetime and native-comparison points are **Synthesis**.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Example applications (parameter-api-python entry), at `12.10.0-3-g98b1ea7`.
[^cvex-param-docs]: `parameter-api-python/README.md` §intro, §Overview, §Requirements, §How to run the code, §The expected output (L95-103), at `12.10.0-3-g98b1ea7`.
[^cvex-param-code]: `parameter-api-python/app/parameter.py::{target (L24), get_parameter_value, main (L33-63)}`; `Dockerfile::{L3-39}`; `docker-compose.yml::{parameter-api, acap-runtime}` (L3-34), at `12.10.0-3-g98b1ea7`.
