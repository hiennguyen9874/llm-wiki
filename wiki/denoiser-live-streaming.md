---
type: Concept
title: Denoiser Live Streaming
description: Running Facebook Denoiser as a live loopback or microphone filter on macOS and Linux, with the README's CPU real-time-factor table, the 16 ms frame-stride latency tradeoff of the -f flag, and the audible failure modes when the CPU falls behind.
tags: [pipeline, streaming, latency, speech-enhancement, cpu, edge]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T12:00:00Z }
stale_after: 2027-10-13
sources:
  - id: denoiser-readme
    resource: ../raw/denoiser.md
    kind: documentation
    title: facebookresearch/denoiser README capture
---

`python -m denoiser.live` runs the [Facebook Denoiser](facebook-denoiser.md) model in a streaming loop between an input device and an output device, aimed at conferencing apps that consume a loopback device. The README's only real-time evidence is a CPU benchmark on a 2 GHz quad-core Intel i5: H=48 reaches RTF 0.8 on one thread and 0.6 on four, while H=64 reaches 1.2 on one thread (slower than real time) and 1.0 on four (borderline). Its example run reports a total lag of 41.3 ms with a 16 ms stride, and each extra `-f` frame adds 16 ms (**Reported**).[^denoiser-readme] The README measures no end-to-end voice-agent latency (**Observed**).

## Setup by platform

- **macOS:** the README uses the Soundflower loopback driver. Run `python -m denoiser.live`, then choose "Soundflower (2ch)" as the input in the conferencing app (**Reported**).[^denoiser-readme]
- **Linux (tested on Ubuntu 20.04):** create a PulseAudio null sink with `pacmd load-module module-null-sink sink_name=denoiser`, label it with `pacmd update-sink-proplist`, and run `python -m denoiser.live --out <loopback device>`. In `pavucontrol`'s Playback tab, route the app to the `denoiser` sink, and select "Monitor of Null Output" as its microphone (**Reported**).[^denoiser-readme]
- **Other platforms:** no official support; a soundcard with loopback support may work. List devices with `python -m sounddevice`. `--in` selects the input (default: system input). Windows uses `python.exe` (**Reported**).[^denoiser-readme]
- **Denoising received speech:** set the loopback as the conferencing app's output and run `python -m denoiser.live --in "Soundflower (2ch)" --out "<output device>"`. The README notes that your own and received speech cannot both be denoised unless enough loopback interfaces exist (**Reported**).[^denoiser-readme]

## Real-time budget

| Model | Threads | RTF |
|---|---:|---:|
| H=48 | 1 | 0.8 |
| H=64 | 1 | 1.2 |
| H=48 | 4 | 0.6 |
| H=64 | 4 | 1.0 |

(**Reported**; quad-core Intel i5 at 2 GHz, a pure-Python streaming implementation with optimized streaming convolutions.) Measure locally with `python -m denoiser.demucs --hidden=48 --num_threads=1`. The README's example prints `total lag: 41.3ms, stride: 16.0ms, time per frame: 12.2ms, ... RTF: 0.8` (**Reported**).[^denoiser-readme]

- RTF is read as processing time divided by audio duration, so values below 1 are needed to keep up. The README does not define RTF (**Synthesis**).
- The example's 12.2 ms per frame against a 16 ms stride is about 0.76, close to the reported 0.8 (**Synthesis**).
- At H=64 on one thread, RTF 1.2 means about 19 ms of compute per 16 ms stride, which falls behind real time (**Synthesis**).
- Processing several frames per call (`-f 2`, `-f 3`) trades latency for throughput. The README offers this for DDR3 machines (**Reported**).[^denoiser-readme]
- The README does not say whether the 41.3 ms total lag includes audio-device buffering or downstream stages (**Unverified**).

## Failure modes

- Very high noise levels can introduce distortion (**Reported**).[^denoiser-readme]
- If processing lags real time, audio becomes "crunchy" and the tool prints a warning. The README's remedy is to close non-essential applications (**Reported**).[^denoiser-readme]
- The tested machine was a MacBook Pro with a 2 GHz quad-core i5 and DDR4 memory; the README reports issues on DDR3 machines (**Reported**).[^denoiser-readme]

## Fit for a voice-agent pipeline

- The README documents only the CLI and benchmark commands, not a library streaming API for embedding in a VAD, ASR, or agent process (**Observed**).[^denoiser-readme]
- The working practice in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) is to enhance only the VAD/barge-in branch. If this model were used there, its lag and frame stride would add to that branch's latency, and its CPU use would compete with other components (**Synthesis**).[^denoiser-readme]
- Denoising does not cancel the agent's own playback. The README does not address echo, so acoustic echo cancellation remains a separate concern in [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) (**Synthesis**).

## Relationships

- Uses [Facebook Denoiser](facebook-denoiser.md) for its model and checkpoints (**Reported**).[^denoiser-readme]
- Related to [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) for the noise-preprocessing question (**Synthesis**).[^denoiser-readme]

## Coverage and limits

- Captured: the README's Live, Troubleshooting, Denoising-received-speech, and Online Evaluation sections. Not captured: `denoiser/live.py` and `denoiser/demucs.py`, so CLI flags beyond `--in`, `--out`, and `-f`, and the RTF measurement method, were not inspected. Nothing was executed (**Observed**).
- Hardware, OS, and audio-device conditions are dated (2 GHz i5, Ubuntu 20.04). No reproduction exists (**Unverified**).
- Soundflower, PulseAudio, and `pavucontrol` are external tools whose current status was not checked.

[^denoiser-readme]: [facebookresearch/denoiser README capture](../raw/denoiser.md) — locators: `Live Speech Enhancement` › `Mac OS X`, `Linux (tested on Ubuntu 20.04)`, `Other platforms`, and `Denoising received speech`; `Troubleshooting bad quality in separation`; `Online Evaluation` (RTF table and `python -m denoiser.demucs` example output).
