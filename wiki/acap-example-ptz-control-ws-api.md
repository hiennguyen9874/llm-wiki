---
type: Concept
title: "ACAP example: PTZ continuous move over the VAPIX WebSocket API with Device Data Hub state"
description: "How ptz-control-ws-api obtains VAPIX credentials over D-Bus, opens a ptz-control-ws WebSocket on 127.0.0.12 with libcurl, sends a JSON-RPC continuousMove, and listens for pan-tilt and zoom state topics in Device Data Hub, with version limits and defects."
tags: [edge-ai, axis, acap, examples, ptz, websocket, vapix, device-data-hub]
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

# ACAP example: PTZ continuous move over the VAPIX WebSocket API

`ptz-control-ws-api` starts a PTZ continuous move through the **PTZ Control WS API** and, instead of polling `ptz.cgi`, listens to PTZ state published on **Device Data Hub** topics.[^native-examples] The README documents the PTZ Control WS API and PTZ topics from AXIS OS 12.11 and Device Data Hub from 12.10; PTZ topics exist only on mechanical PTZ cameras on ARTPEC-7 (with listed exceptions) and ARTPEC-9. The manifest accordingly sets `compatibleOsVersions` `{min: "12.11", max: "13"}`.

## Mechanism

1. **Credentials** (`app/websocket_client.c::get_credentials`): opens the system D-Bus with `sd_bus_open_system` and calls `GetCredentials` on `com.axis.HTTPConf1.VAPIXServiceAccounts1` for the hard-coded account `testuser`, caching the result in a static 256-byte buffer. The manifest grants only that D-Bus method. The mechanism is the same as in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).
2. **Session token:** `get_session_token` GETs `http://127.0.0.12/axis-cgi/wssession.cgi` with libcurl and `CURLAUTH_ANY`, then strips CR/LF.
3. **WebSocket:** `websocket_client_create` builds `ws://127.0.0.12/vapix/ws/v1?wssession=<token>&apis=ptz-control-ws` and connects with `CURLOPT_CONNECT_ONLY=2L`; messages go out with `curl_ws_send`.
4. **Command:** `main` sends a JSON-RPC text frame `{"jsonrpc":"2.0","method":"ptz-control-ws_v1:continuousMove","params":{"channel":1,"panSpeedDeg":100,"tiltSpeedDeg":10,"zoomSpeedNormalized":0}}` right after subscribing.
5. **State:** `subscriber.c` creates a Device Data Hub client and subscribes to `com.axis.ptz.pan-tilt-state.v1` and `com.axis.ptz.optical-zoom-state.v1`. `listener.c::on_data` parses JSON with jansson and logs `pan_deg`, `tilt_deg`, `pan_moving`, speeds (pan-tilt) or `zoom_mag`, FOV angles and `zoom_moving` (zoom).
6. **Stop:** `on_data` sends `continuousMove` with zeros on every message, so the app stops any move, including one started manually.[^native-examples]

Build: `PKGS = glib-2.0 jansson libcurl device-data-hub-client-c` plus `-lsystemd`; libcurl must support WebSocket. The manifest resource key is `deviceDataHub_beta2` (other DDH examples use `deviceDataHub`), and README text about extra manifest parameters has no `paramConfig` counterpart. Device Data Hub background is in [DDH and Message Broker examples](acap-example-device-data-hub-and-message-broker.md); the loopback `127.0.0.12` address and its proxy caveat are in [Proxy configuration](acap-proxy-configuration.md).

## Observed defects and limits

- Hard-coded `testuser`, channel 1, API version `1` and speeds; README admits capabilities should be queried instead.
- The app calls `panic()` (exit 1) on a null topic, a JSON error or an unknown topic.
- `subscriber_destroy` frees the client and subscriber without `dh_client_disconnect`; `dh_client_create` is called with a NULL error pointer.
- The Dockerfile defaults to `aarch64` and the README documents both architectures, but CI builds `armv7hf` only; the README has a malformed Markdown link for the Device Data Hub API and omits the version suffix from `.eap` names.
- The documented 3-minute default timeout of a continuous move is not handled.[^native-examples]

Evidence class: **Observed** (static); not run on a PTZ device.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Depends on** [VAPIX service-account access](acap-vapix-service-account-access.md) and Device Data Hub.
- **Alternative to** the `tnsaxis:Move` event used in [axevent subscribe_to_events](acap-example-events-and-parameters.md).

[^native-examples]: `ptz-control-ws-api/README.md`; `ptz-control-ws-api/app/{main.c,websocket_client.c,subscriber.c,listener.c,listener.h,Makefile,manifest.json}`; `ptz-control-ws-api/Dockerfile:1`; `.github/workflows/ptz-control-ws-api.yml`.
