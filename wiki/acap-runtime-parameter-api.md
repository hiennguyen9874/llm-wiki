---
type: Concept
title: "ACAP Runtime Parameter API: read-only KeyValueStore over AXParameter"
description: "The keyvaluestore.KeyValueStore gRPC service: single GetValues call, key validation regex, the app-scoped AXParameter backend, the empty-string-on-error behaviour, and how it relates to the examples and the legacy parhand path."
tags: [edge-ai, axis, acap, acap-runtime, grpc, parameters, axparameter, protobuf]
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
    title: "ACAP Runtime README (§APIs: Parameter API)"
  - id: rt-parameter
    resource: ../raw/acap-runtime/src/parameter.cpp
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "parameter.cpp / parameter.h — Parameter service"
  - id: rt-kvproto
    resource: ../raw/acap-runtime/apis/keyvaluestore.proto
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "keyvaluestore.proto"
  - id: rt-parametertest
    resource: ../raw/acap-runtime/test/parameter_test.cc
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "parameter_test.cc"
---

# ACAP Runtime Parameter API: read-only KeyValueStore over AXParameter

The Parameter API gives gRPC clients **read access to the parameters of an Axis device**, per the README, which points to the `parameter-api-python` example.[^rt-readme] It is the smallest of the three APIs: one RPC, `GetValues`, one key in and one string out.

## Contract

`package keyvaluestore; service KeyValueStore { rpc GetValues(Request) returns (Response); }` with `Request{string key = 1}` and `Response{string value = 1}`. There is no write, list or batch call.[^rt-kvproto]

## Behaviour

- The service is the C++ class `Parameter`, which opens `ax_parameter_new(APP_NAME, …)` at construction. `APP_NAME` is a compile-time constant: `acapruntime`, or `acapruntimetest` in the test build. Failure to initialise throws `Could not Init Parameter Service`.[^rt-parameter]
- `GetValues` validates the key with the regex `[a-zA-Z0-9.]+` and answers `INVALID_ARGUMENT` otherwise. Keys with `_` or `-` are therefore rejected even though real parameter names may contain them (**Observed**).
- It then calls `ax_parameter_get`. On failure it logs, uses an empty string and still returns **`Status::OK`**, so a missing parameter and an empty one look identical to the client. The empty string is allocated with `g_strdup` but released with `free()` (mismatched allocator, minor).[^rt-parameter]
- Fully-qualified names such as `root.Brand.Brand` work in the test: the test fetches `root.Brand.Brand` (`AXIS`), `root.Brand.WebURL` (`http://www.axis.com`), `root.Image.I0.Enabled` (`yes`) and `root.invalid` (empty).[^rt-parametertest] That is **Observed**; how `ax_parameter_get` scopes a name that starts with `root.` for a given app name is not shown here and is **Unverified**.
- The backend is the `axparameter` library, linked through pkg-config. The README's mount of `/run/dbus/system_bus_socket` suggests it talks to the parameter daemon over D-Bus, but that is **Synthesis**, not read from this code.

## Do not confuse with the `-o` path

The server's legacy `-o` flag reads *its own four settings* (`Verbose`, `IpPort`, `ChipId`, `UseTLS`) through `parhandclient`, a different mechanism, with its own defects; see [Server configuration](acap-runtime-server-configuration-and-security.md). The Parameter API serves *clients*; `-o` configures the server.

## Client side

No Python wrapper is shipped for this API: `Dockerfile.proto` generates `keyvaluestore_pb2*.py` into `/build/param/proto_utils` and copies nothing else, so clients build the stub themselves. The CV SDK example does that, uses TLS with a self-signed certificate and mounts a different device socket (`/run/confcache/confcachesocket`) than the ML examples ([Parameter API example](acap-cv-example-parameter-api.md); [Build and image packaging](acap-runtime-build-and-image-packaging.md)). For a native app reading parameters in-process see [Events and parameters examples](acap-example-events-and-parameters.md).

## Relationships

- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md); served by the process described in [Server configuration](acap-runtime-server-configuration-and-security.md).
- **Used by:** [Parameter API example](acap-cv-example-parameter-api.md), [Runtime architecture](acap-cv-examples-runtime-architecture.md).
- **Tested by:** `ParameterTest::GetValues` in the [test suite](acap-runtime-test-suite.md) (device- and firmware-specific expected values).

## Evidence class

**Observed** by static reading of the proto, `parameter.cpp` and the test; nothing was run, and the behaviour of `ax_parameter_get` is the library's, not read here.

[^rt-readme]: `README.md` §APIs (Parameter API), §Examples.
[^rt-parameter]: `src/parameter.cpp::{Parameter::Parameter (L33-38), GetValues (L46-66)}`, `src/parameter.h::{APP_NAME (L20-24), Parameter (L26-41)}`; `Makefile` L69 (`axparameter` in `PKGS`).
[^rt-kvproto]: `apis/keyvaluestore.proto::{KeyValueStore (L22-26), Request (L29-31), Response (L34-36)}`.
[^rt-parametertest]: `test/parameter_test.cc::ParameterTest.GetValues (L95-120)`.
