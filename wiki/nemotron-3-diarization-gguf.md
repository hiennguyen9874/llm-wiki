---
type: Concept
title: Nemotron 3 Diarization GGUF
description: GGUF packaging of NVIDIA Nemotron 3 Diarization for audio.cpp with offline, streaming, and server-batch usage, BF16 and Q8_0 weights, and RTX 5090 C++/Python performance and quantization caveats.
tags: [vad, diarization, speaker-tagging, audio-cpp, gguf, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T09:00:00Z }
stale_after: 2027-10-06
sources:
  - id: nemotron-3-diar-gguf-card
    resource: ../raw/Nemotron-3-Diarization-GGUF.md
    kind: documentation
    title: Nemotron-3-Diarization-GGUF
---

Nemotron 3 Diarization GGUF is a GGUF conversion of the NVIDIA Nemotron 3 Diarization checkpoint for native inference with audio.cpp, supporting offline, streaming, and server-batch speaker diarization for up to eight speakers with speaker turns and timestamps but no transcribed words, distributed as BF16 and Q8_0 weight files with documented CLI/server usage, RTX 5090 C++/Python performance figures, and explicit Q8_0 output-consistency caveats (**Reported**).[^nemotron-3-diar-gguf-card]

## Package identity and capabilities

- Card title is "Nemotron-3-Diarization-GGUF"; frontmatter declares `license: openmdw-1.1`, `base_model: nvidia/Nemotron-3-Diarization`, `pipeline_tag: voice-activity-detection`, and tags `audio.cpp`, `gguf`, `speaker-diarization`, `streaming-sortformer`, `speaker-tagging`, and `audio` (**Reported**).[^nemotron-3-diar-gguf-card]
- This is a format conversion for audio.cpp, not an original NVIDIA release; upstream is [nvidia/Nemotron-3-Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization/tree/723e19c601d99b7e58fba6a14e32153e0afe48d9), pinned to revision `723e19c601d99b7e58fba6a14e32153e0afe48d9` (**Reported**).[^nemotron-3-diar-gguf-card]
- The model identifies who spoke when, with up to eight speakers; it returns speaker turns and timestamps, not transcribed words (**Reported**).[^nemotron-3-diar-gguf-card]
- Runtime target is [audio.cpp](https://github.com/0xShug0/audio.cpp), tested on CUDA, Vulkan, and Metal (Mac) backends (**Reported**).[^nemotron-3-diar-gguf-card]
- A 2026-09-26 update notes improved NeMo parity for ragged batches and streaming tails, selectable flash/eager attention, self-describing speaker-probability output, ASR-compatible latency profiles, and integration with Nemotron's speaker-tagged transcription pipeline; existing published GGUFs remain compatible (**Reported**).[^nemotron-3-diar-gguf-card]

## Weights and file layout

- Each GGUF file contains 362 tensors, frontend configuration, and an embedded model spec, with no separate weight or configuration files required; the package was converted from the original `.nemo` checkpoint, not from an existing GGUF (**Reported**).[^nemotron-3-diar-gguf-card]

| File | Precision | Size |
| --- | --- | ---: |
| `nemotron-3-diarization-bf16.gguf` | BF16 | 189.51 MiB |
| `nemotron-3-diarization-q8_0.gguf` | Q8_0 / mixed | 101.73 MiB |

Table values are source-reported file sizes and precisions as listed in the card's weights table (**Reported**).[^nemotron-3-diar-gguf-card]

- The BF16 file retains the original model weight precision, with the frontend mel filter stored in F32; BF16 is described as parity safe with NeMo with TF32 control (**Reported**).[^nemotron-3-diar-gguf-card]
- Q8_0 quantizes 130 tensors; 229 remain BF16, two use F16, and the mel filter remains F32; Q8_0 is explicitly not exact-parity-safe and can change speaker boundaries and turn counts (**Reported**).[^nemotron-3-diar-gguf-card]

## Usage

- Offline CLI diarization uses a current audio.cpp build with `nemotron_3_diar` support and a 16 kHz WAV: `audiocpp_cli --task diar --family nemotron_3_diar --model /path/to/nemotron-3-diarization-bf16.gguf --backend cuda --threads 8 --audio meeting.wav --turns-out turns.json --log` (**Reported**).[^nemotron-3-diar-gguf-card]
- For streaming, add `--mode streaming` and, for example, `--session-option nemotron_3_diar.latency_profile=low`; profiles and options are documented in the linked audio.cpp model documentation (**Reported**).[^nemotron-3-diar-gguf-card]
- Server batching uses a `server.json` with an absolute GGUF path, fields `host`, `port`, `backend`, `device`, `threads`, `lazy_load`, and a `models` entry with `id: nemotron-3-diar`, `family: nemotron_3_diar`, `path`, `task: diar`, and `mode: offline`, launched with `audiocpp_server --config server.json --log` (**Reported**).[^nemotron-3-diar-gguf-card]
- Different-length recordings can be sent in one request via `curl -N http://127.0.0.1:8080/v1/batches/transcriptions -F model=nemotron-3-diar -F file=@meeting-a.wav -F file=@meeting-b.wav -F file=@meeting-c.wav`; files do not need equal durations (**Reported**).[^nemotron-3-diar-gguf-card]
- The default batch response is SSE; each completed file receives a `batch.transcription.result` event containing `speaker_turns`, with `index` associating the result with the uploaded file (**Reported**).[^nemotron-3-diar-gguf-card]

## C++/Python performance comparison

- Test conditions: RTX 5090 with CUDA and eight CPU threads, matching input order and chunk settings; audio.cpp rows use the debug server, BF16 or Q8_0 GGUF, `--log`, and the default `very_high` latency profile with the card's server configuration; Python rows use the official NeMo model with PyTorch 2.11.0+cu128, `eval()` and `torch.inference_mode()`, `torch.set_num_threads(8)`, `torch.manual_seed(663)`, `_check_streaming_parameters()` after setting shared parameters, and `async_streaming=False` (**Reported**).[^nemotron-3-diar-gguf-card]
- Python inference called `diarize(audio=waveforms, sample_rate=16000, batch_size=len(waveforms), verbose=False)` with preloaded mono waveforms, and `batch_size=1` for single requests; both implementations used identical parameters `chunk_len=340`, `chunk_right_context=40`, `fifo_len=40`, `spkcache_update_period=300`, and `spkcache_len=264` (C++ default `very_high` profile values), with no precision or TF32 overrides (**Reported**).[^nemotron-3-diar-gguf-card]
- The batch test varied batch size from one to six files with shuffled order across repeated requests; recordings were 37–311 seconds long; 24 mixed batches held 12,482 seconds of audio and 10 non-batch requests held 1,531 seconds; models stayed loaded between requests (**Reported**).[^nemotron-3-diar-gguf-card]

| Workload | Runtime | Total inference time | Aggregate RTF | Sampled peak VRAM |
| --- | --- | ---:| ---:| ---: |
| 24 mixed batches | audio.cpp server, BF16 | 11.984 s | 0.000960 | 1,076 MiB |
| 24 mixed batches | audio.cpp server, Q8_0 | 10.836 s | 0.000868 | 948 MiB |
| 24 mixed batches | Official Python | 9.718 s | 0.000779 | 2,786 MiB |
| 10 single requests | audio.cpp server, BF16 | 1.417 s | 0.000926 | 820 MiB |
| 10 single requests | audio.cpp server, Q8_0 | 1.684 s | 0.001100 | 740 MiB |
| 10 single requests | Official Python | 1.795 s | 0.001173 | 1,504 MiB |

Table values are source-reported measurements as listed in the card's performance table (**Reported**).[^nemotron-3-diar-gguf-card]

- The card's reading: Python was faster on the mixed batches while audio.cpp was faster on the single requests with either GGUF; Q8_0 took about 10% less time than BF16 for batches but 19% more for single requests, while reducing peak VRAM in both (**Reported**).[^nemotron-3-diar-gguf-card]
- Measurement scope: the C++ rows are fresh sequential BF16/Q8_0 reruns while the Python rows retain earlier same-day measurements on identical request plans; each row is one workload sequence, not a median across repeated full benchmark runs; results depend on hardware, input lengths, and batch composition (**Reported**).[^nemotron-3-diar-gguf-card]
- RTF is total inference time divided by total audio duration (lower is better); timing includes frontend and postprocessing but excludes model loading, input file I/O, and HTTP transfer; VRAM is per-process memory sampled every 20 ms including weights and CUDA context; batch VRAM covers the full 33-request sequence including nine control/reference requests omitted from the timing table, single-request VRAM includes warmup, and brief peaks may be missed (**Reported**).[^nemotron-3-diar-gguf-card]

## Q8_0 output-consistency caveats

- Q8_0 output comparisons come from an earlier separate CUDA validation against C++ BF16, not against Python or human-annotated ground truth, using an RTX 5090, debug server, eight threads, logging enabled, and the default `very_high` latency profile without a TF32 override (**Reported**).[^nemotron-3-diar-gguf-card]
- Findings: five short recordings retained their turn counts with mostly 10 ms boundary shifts; the 97.6-second recording retained 31 turns with speaker activity differing over 0.174% of the timeline; the 311-second recording changed from 161 to 152 turns with speaker activity differing over 1.174% of the timeline; repeated requests within each precision produced identical turns and confidence (**Reported**).[^nemotron-3-diar-gguf-card]
- The percentages compare same-label speaker activity on a 10 ms grid and are not diarization error rates (DER); the card advises BF16 when preserving the original model's output matters, with Q8_0 trading output consistency for smaller weights and lower VRAM usage; the Q8_0 results do not validate streaming or other backends (**Reported**).[^nemotron-3-diar-gguf-card]

## License

- Weights are governed by [OpenMDW-1.1](https://openmdw.ai/license/1-1/), not audio.cpp's code license; a downloaded copy is included in `LICENSE.html`; retain the license and applicable notices of origin when redistributing; original model by NVIDIA with GGUF conversion for audio.cpp (**Reported**).[^nemotron-3-diar-gguf-card]

## Relationships

- Upstream model: [Nemotron 3 Diarization](nemotron-3-diarization.md) covers the NVIDIA source checkpoint with streaming latency configurations, training data, and DER/RTFx benchmarks, while this concept covers the audio.cpp GGUF conversion with CLI/server-batch usage and quantization caveats; neither deprecates the other (**Synthesis**).[^nemotron-3-diar-gguf-card]

- Related sibling packaging: [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md) is also a GGUF conversion for a llama.cpp-family CPU/edge runtime with quantization tradeoffs, while this concept covers speaker diarization (who spoke when) rather than transcription (**Synthesis**).[^nemotron-3-diar-gguf-card]
- Related sibling packaging: [Audio Flamingo 3 and Next GGUF](audio-flamingo-3-and-next-gguf.md) is also a self-contained audio.cpp GGUF packaging with CLI/server usage and RTX 5090 C++/Python reporting, while this concept covers the diarization family and its server-batch SSE result shape (**Synthesis**).[^nemotron-3-diar-gguf-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no GGUFs loaded, and no performance, VRAM, or Q8_0 output-difference figures reproduced (**Synthesis**).[^nemotron-3-diar-gguf-card]
- Referenced local artifacts (both GGUF files and `LICENSE.html`) were not present in `raw/` and were not inspected; linked external pages (audio.cpp repository, audio.cpp model documentation, upstream Hugging Face checkpoint at the pinned revision) were not fetched (**Synthesis**).[^nemotron-3-diar-gguf-card]
- All identity, compatibility, usage, performance, VRAM, and quantization characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^nemotron-3-diar-gguf-card]

[^nemotron-3-diar-gguf-card]: [Nemotron-3-Diarization-GGUF](../raw/Nemotron-3-Diarization-GGUF.md) — locators: frontmatter (`license`, `base_model`, `pipeline_tag`, `tags`); section `Use With audio.cpp` (audio.cpp target, CUDA/Vulkan/Metal backends, up-to-eight-speakers scope, offline/streaming/server-batch modes, turns-and-timestamps-not-words disclaimer, 2026-09-26 update paragraph with NeMo parity, flash/eager attention, speaker-probability output, latency profiles, speaker-tagged pipeline notes); section `Weights` (2-row file table with filenames, precisions, MiB sizes; 362-tensor / frontend-config / embedded-spec / `.nemo`-origin paragraph; BF16 F32-mel / TF32-control paragraph; Q8_0 130/229/2/F32 split paragraph; upstream link plus revision `723e19c...` and conversion disclaimer); section `Run` (CLI code fence with `--task diar --family nemotron_3_diar --model --backend --threads --audio --turns-out --log`, 16 kHz WAV note, `--mode streaming` plus `nemotron_3_diar.latency_profile=low` paragraph, model-documentation link); section `Server Batching` (`server.json` fence with `host`/`port`/`backend`/`device`/`threads`/`lazy_load`/`models[]` fields, `audiocpp_server --config` fence, multi-file `curl -N ... /v1/batches/transcriptions` fence, SSE `batch.transcription.result` / `speaker_turns` / `index` / unequal-duration paragraph); section `Performance Compared With Python` (RTX 5090 / CUDA / 8-thread / matching-order protocol, audio.cpp debug-server vs NeMo PyTorch 2.11.0+cu128 `eval`/`inference_mode`/threads/seed/`_check_streaming_parameters`/`async_streaming=False` paragraphs, `diarize(... batch_size ...)` paragraph, shared `chunk_len`/`chunk_right_context`/`fifo_len`/`spkcache_update_period`/`spkcache_len` values, 37–311 s / 24-batch 12,482 s / 10-single 1,531 s / loaded-models paragraph, 6-row workload table, Python-faster-batches / C++-faster-singles / Q8 ±10%/+19% / VRAM paragraph, rerun-vs-retained / one-sequence-not-median paragraph, RTF definition / inclusions-exclusions / 20-ms VRAM / 33-request and warmup paragraph); section `Q8 Results And Caveats` (not-exact-parity-safe warning, separate-CUDA-vs-C++-BF16 scope paragraph, short-recording / 97.6-s 31-turn 0.174% / 311-s 161→152-turn 1.174% / determinism bullets, 10-ms-grid-not-DER / BF16-vs-Q8 guidance / no-streaming-or-backend-validation paragraph); section `License` (OpenMDW-1.1 vs audio.cpp license, `LICENSE.html`, redistribution-notice, NVIDIA-origin paragraph). Referenced GGUF binaries and `LICENSE.html` have no locator available in `raw/` (files absent).
