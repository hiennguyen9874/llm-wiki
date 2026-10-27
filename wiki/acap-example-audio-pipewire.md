---
type: Concept
title: "ACAP examples: capturing and playing audio with PipeWire"
description: "How audio-capture and audio-playback use the PipeWire stream API on Axis devices: registry discovery, stream setup, peak-level logging, 440 Hz tone generation, the pipewire user group, expected output and defects."
tags: [edge-ai, axis, acap, examples, audio, pipewire]
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

# ACAP examples: capturing and playing audio with PipeWire

Audio in the Native SDK examples goes through the **PipeWire** stream API (`libpipewire-0.3`), not a bespoke Axis audio library. `audio-capture` reads from audio source nodes and logs peak levels; `audio-playback` writes a sine tone to an output node.[^native-examples] Both manifests request `resources.linux.user.groups: ["pipewire"]` and use `runMode: "never"`, so the app must be started by hand.

## audio-capture

- **Discovery:** `pw_core_get_registry` plus a `registry_event_global` listener creates one capture stream per `PW_TYPE_INTERFACE_Node`; for nodes whose `media.class` is `Audio/Sink` it sets `PW_KEY_STREAM_CAPTURE_SINK` to capture the monitor.
- **Processing:** `on_process` dequeues buffers and scans each channel's planar float data for min and max, keeping a running peak; a PipeWire loop timer fires every 5 seconds and logs `peak %.1f dBFS`, resetting the peak (`-inf dBFS` for silence). Format is built with `spa_format_audio_raw_build`.
- **Exit:** SIGINT/SIGTERM call `pw_main_loop_quit`; debug logging via `PIPEWIRE_DEBUG=audiocapture:5,2`.
- **Output sample (README):** `Found Audio/Source node AudioDevice0Input0.Unprocessed with id 90`, state changes `unconnected→connecting→paused→streaming`, `Capturing from node …, N channel(s), rate 48000.`

**Observed defects:** node types are filtered only by `PW_TYPE_INTERFACE_Node`, so a stream is attempted for every node in the graph; the channel loop assumes `buf->datas[c]` exists; README log line numbers (`audiocapture.c:368`) do not match the source.[^native-examples]

## audio-playback

- Selects output nodes with the regex `^AudioDevice[0-9]+Output[0-9]+$` (`regcomp` in `main`), creates a `PW_DIRECTION_OUTPUT` stream with category `Playback`, one channel `SPA_AUDIO_FORMAT_F32P`, rate 0 (inherits the device rate).
- `on_process` fills `buf->datas[0]` with `sinf(angle)*VOLUME` using hard-coded `FREQUENCY 440` and `VOLUME 0.5f`, advancing the angle by `2π·440/rate`, and sets chunk offset, stride and size. `on_param_changed` logs `Playing to node AudioDevice0Output0, rate 48000.`
- **Defect:** only `datas[0]` is written even if the device negotiates more channels; the `goto out` error path still queues the buffer, producing silence.[^native-examples]

Evidence class: **Observed**; neither app was run and the node names above are README samples.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md); group privileges in [shared conventions](acap-examples-build-and-manifest-conventions.md).
- **Related** [ACAP application user types and permissions](acap-application-user-permissions.md) (why a Linux group grants device access).

[^native-examples]: `audio-capture/app/audiocapture.c::main, registry_event_global, on_process, on_timeout`, `audio-capture/README.md`, `audio-capture/app/{Makefile,manifest.json}`; `audio-playback/app/audioplayback.c::main, on_process, on_param_changed`, `audio-playback/README.md`.
