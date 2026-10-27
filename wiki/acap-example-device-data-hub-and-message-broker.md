---
type: Concept
title: "ACAP examples: Device Data Hub and Message Broker subscribers and producers"
description: "How the device-data-hub examples (object detector producer, object consumer, scene-metadata and memory/CPU subscribers) and the message-broker scene-metadata example use topics, filters, ACLs and manifest resources, how the two scene-metadata examples differ, and the defects found."
tags: [edge-ai, axis, acap, examples, device-data-hub, message-broker, metadata]
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

# ACAP examples: Device Data Hub and Message Broker

Two repository areas show data-sharing APIs on AXIS OS: `device-data-hub` (four examples, MIT) uses the **Device Data Hub** publish/subscribe system, and `message-broker/consume-scene-metadata` uses the **Message Broker** API.[^native-examples] The Device Data Hub README describes a data-centric model with decoupled producers and consumers and states it is not for streaming binary data. Both ship scene-metadata consumers for the same use case, so they read as an API-migration pair.

## Device Data Hub examples

Common build: `PKGS = device-data-hub-client-c`, headers `<datahub/client.h>` and `<datahub/subscriber.h>`, `-std=c17`, manifest `resources.deviceDataHub.enabled: true`. The client connects as the Linux user `acap-<appName>`.[^native-examples]

| Example | Topic | Role and behaviour |
| --- | --- | --- |
| `acap-communication/object-detector` | `com.example.objectdetector` (JSON topic definition v1.0.0: `object` string required, `distance` integer) | Producer. Creates the topic if `dh_client_get_topic` returns `DH_ERR_INVALID_TOPIC`, creates a writer, registers production, and publishes three fake objects (`human`, `bird`, `dog`) once a second, only while a consumer match is signalled; deletes the topic at exit |
| `acap-communication/object-consumer` | same topic | Subscriber with a topic-name filter, data updates enabled, logs `Received Object Detection data: {...}`; relies on the detector's ACL to read |
| `consume-scene-metadata` | `com.axis.scene.object_track.v1` | Subscriber with an instance-key filter `channel_id = 1`; payload is one tracked object: `classes`, `duration`, start/end time, UUID `id`, base64 crop `image`, `path[]` of boxes and timestamps |
| `memory-cpu-utilization` | `com.axis.device.memory-utilization.v1` and `com.axis.device.cpu-utilization.v1` | One subscriber with both topics; logs memory (`mem_available`, `mem_total`, `mem_used`, `mem_used_pct`) and CPU (`core_utilization`, `number_of_cores`, `total_utilization`) samples |

**Access control.** The detector manifest grants topic `com.example.objectdetector` `all` to `acap-object_detector` and `read` to `acap-object_consumer`; default rights otherwise cover topics prefixed `acap.<appName>`, and violations return `DH_ERR_AUTHORIZATION_FAILED`. Subscribing to a topic that does not exist yet is allowed.[^native-examples]

## Message Broker example

`message-broker/consume-scene-metadata` links `mdb`, subscribes asynchronously to `com.axis.analytics_scene_description.v0.beta` on source `"1"` (the video channel) with `mdb_connection_create`, `mdb_subscriber_config_create`, `mdb_subscriber_create_async`, and logs the raw per-frame JSON (`frame.observations[]` with `bounding_box`, `class`, `track_id`; `frame.operations[]`). Its manifest has no `resources` block. README version notes: the Metadata Broker was beta from SDK 1.13 (AXIS OS 11.9), SDK 1.15 added a second topic with breaking function renames, and SDK 12.0 renamed it Message Broker.[^native-examples]

### The two scene-metadata examples

| Aspect | Message Broker | Device Data Hub |
| --- | --- | --- |
| Topic | `com.axis.analytics_scene_description.v0.beta`, per-frame description | `com.axis.scene.object_track.v1`, per tracked object |
| Channel selection | `source = "1"` argument | instance key `channel_id = 1` |
| Manifest | none needed | `deviceDataHub.enabled` |
| Errors | `abort()` on connection error | `EXIT_FAILURE` on setup errors |

Both set `appName: consume_scene_metadata`, so the two packages cannot be installed on one device at the same time.

## Observed defects

- Three subscribers (`object_consumer.c:43`, `consume_scene_metadata.c`, `memory_cpu_utilization.c:44`) use `if (!client && !handle_client_error(...))`, which does not return when client creation fails, so a null client can be used; the producer checks correctly.
- The `memory-cpu-utilization` README gives topic names with underscores (`memory_utilization`, `cpu_utilization`) while the code defines hyphenated names (re-verified at lines 14–15); the README's "every five seconds" has no timer in the code.
- The detector README claims it deletes an existing topic first and names the topic `acap.object_detector` with auto-prefixed ACL wildcards; the code never deletes up front and uses a literal `com.example.objectdetector` with a second ACL entry.
- The scene-metadata README says "the two topics described above" though only one is subscribed.
- Dockerfile `ARG ARCH=` has an empty default in the Message Broker example.[^native-examples]

Evidence class: **Observed**; no topic was subscribed on a device. For the PTZ variant that mixes this API with a WebSocket, see [PTZ control example](acap-example-ptz-control-ws-api.md).

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md); manifest resources in [shared conventions](acap-examples-build-and-manifest-conventions.md).
- **Uses** APIs catalogued in [Native SDK API catalog](acap-native-sdk-api-catalog.md).
- **Complements** the event mechanism in [axevent](acap-example-events-and-parameters.md).

[^native-examples]: `device-data-hub/README.md`; `device-data-hub/acap-communication/README.md`; `device-data-hub/acap-communication/{object-detector,object-consumer}/app/{*.c,manifest.json}`; `device-data-hub/consume-scene-metadata/app/consume_scene_metadata.c`; `device-data-hub/memory-cpu-utilization/app/memory_cpu_utilization.c` (lines 14–15, 44) and its README; `message-broker/README.md`; `message-broker/consume-scene-metadata/{Dockerfile,app/consume_scene_metadata.c,app/manifest.json}`.
