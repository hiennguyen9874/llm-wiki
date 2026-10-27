---
type: Concept
title: "ACAP examples: sending and subscribing to events (axevent) and managing parameters (axparameter)"
description: "How the axevent and axparameter examples work: declaring and sending a stateful ONVIF-style event, subscribing to custom and predefined Axis events, the ONVIF event-list helper script, parameter callbacks and their restriction, manifest paramConfig, and defects."
tags: [edge-ai, axis, acap, examples, axevent, axparameter, events, parameters]
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

# ACAP examples: events (axevent) and parameters (axparameter)

`axevent` teaches the event system through one producer and two consumers plus a helper script; `axparameter` shows how an app defines, reads, writes and reacts to parameters.[^native-examples] None of these apps needs special privileges in its manifest, and all log through syslog.

## axevent

README concepts: events have a topic path in namespace `tns1` (ONVIF) or `tnsaxis` (Axis-defined); a *producer* declares then sends, a *consumer* subscribes.

| Part | Role and keys | Notes |
| --- | --- | --- |
| `send_event` | Declares `tns1:Monitoring/ProcessorUsage` with source key `Token` (int) and data key `Value` (double); sends a stateful event every 10 s cycling 0..100 in steps of 10 | `ax_event_handler_declare` → on completion `g_timeout_add_seconds(10, …)` → `ax_event_new2` + `ax_event_handler_send_event`; undeclare at exit |
| `subscribe_to_event` | Subscribes to the same topic and logs `Received event with value: %lf` | `ax_event_handler_subscribe`, `ax_event_key_value_set_get_double`; fixed subscription token 1234 |
| `subscribe_to_events` | Subscribes to five predefined Axis events: audio `tnsaxis:TriggerLevel`, day/night `tnsaxis:DayNightVision`, manual trigger `tnsaxis:IO/VirtualPort` (port 1), PTZ `tnsaxis:Move`, tampering `tnsaxis:Tampering` | two callbacks (token dispatch and a PTZ struct); README explains how to trigger each event and that availability varies per product |
| `get_eventlist.py` | Calls ONVIF `GetEventProperties` and a pull-point subscription with `PullMessages` to dump declared and sent events to XML | needs `requests` and `xmllint`; defaults `--auth digest`, `--user root`, `--ip 192.168.0.90`, `--time 10` |

The declared-event pattern is a stateful (property) event, so the first received message is the initial state.[^native-examples]

**Observed defects.**

- `send_event.c::setup_declaration` passes `&start_value`, a pointer to the pointer parameter, to `ax_event_key_value_set_add_key_value` (re-verified at lines 124, 153, 175), so the declared initial value is read from the wrong address; it should pass `start_value`.
- `subscribe_to_events.c::ptzmove_callback` indexes an 8-element array with the ONVIF token and no bounds check.
- `get_eventlist.py`: README names `*.xml.new` output files while the constants are `*.xml`; `<wsa:To>` is hard-coded to `192.168.0.90`; `subscription_id` can be unbound after a non-200 reply; shell `echo '…' | xmllint` is fragile.
- Several C files rely on transitive includes for `calloc`/`free`.[^native-examples]

## axparameter

- **Manifest:** `configuration.paramConfig` declares `IsCustomized` (default `no`, type `bool:no,yes`, shown as a checkbox) and `BackupValue` (default `"restored from backup"`, type `hidden:string`).
- **API use:** `ax_parameter_new("axparameter", …)` (group = appName, so unqualified names work and add/remove are allowed), `ax_parameter_get("Properties.System.SerialNumber")`, `ax_parameter_register_callback` for `root.axparameter.IsCustomized` and `CustomValue`, `ax_parameter_list`, `_add`, `_set`, `_remove`, `_free`.
- **Callback restriction:** AXParameter calls must not be made inside the change callback. The example logs and schedules `monitor_parameters` with `g_timeout_add_seconds(1, …)`, duplicating the strings because AXParameter owns the originals and heap-allocating the message because callbacks can queue up.
- **Behaviour:** when `IsCustomized` becomes `yes` and `CustomValue` is missing, the value is restored from `BackupValue`; when it becomes `no`, the value is backed up and `CustomValue` removed. The Apps page must be reloaded to see added or removed parameters.
- **Hazard:** `name_without_qualifiers = &name[strlen("root.axparameter.")]` assumes the callback always passes the fully qualified name.[^native-examples]

The same Parameter API supplies the runtime thresholds of [object-detection-yolov5](acap-example-larod-object-detection.md); the first-application workflow that touches AXParameter is in [Create, build and install your first ACAP application](acap-first-application-workflow.md). `axparameter` is named, with `vapix`, as a canonical example in the [example guidelines](acap-examples-contribution-lint-and-ci.md).

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Uses** the event and parameter APIs from [Native SDK API catalog](acap-native-sdk-api-catalog.md).
- **Related** [Device Data Hub and Message Broker examples](acap-example-device-data-hub-and-message-broker.md) for newer data-sharing APIs, and [PTZ control](acap-example-ptz-control-ws-api.md) for PTZ state over a different channel than the `tnsaxis:Move` event.

[^native-examples]: `axevent/README.md`; `axevent/send_event/app/send_event.c::setup_declaration, declaration_complete, send_event`; `axevent/subscribe_to_event/app/subscribe_to_event.c`; `axevent/subscribe_to_events/app/subscribe_to_events.c::common_callback, ptzmove_callback`; `axevent/get_eventlist.py`; `axparameter/README.md`; `axparameter/app/axparameter.c::parameter_changed, monitor_parameters`; `axparameter/app/manifest.json` (`configuration.paramConfig`).
