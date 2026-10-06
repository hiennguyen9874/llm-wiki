---
license: openmdw-1.1
base_model: nvidia/Nemotron-3-Diarization
tags:
- audio.cpp
- gguf
- speaker-diarization
- streaming-sortformer
- speaker-tagging
- audio
pipeline_tag: voice-activity-detection
---

# Nemotron-3-Diarization-GGUF

## Use With audio.cpp

**Update 2026-09-26**: Since the initial release, Nemotron 3 Diarization has received improved NeMo parity 
for ragged batches and streaming tails, selectable flash/eager attention, self-describing speaker-probability output, 
ASR-compatible latency profiles, and integration with Nemotron’s speaker-tagged transcription pipeline. 
Existing published GGUFs remain compatible.

GGUF weights for native inference with [audio.cpp](https://github.com/0xShug0/audio.cpp). Tested on CUDA, Vulkan, and Metal(Mac) backends.
Nemotron 3 Diarization identifies who spoke when, with up to eight
speakers. It supports offline, streaming, and server batch diarization.
It returns speaker turns and timestamps, not transcribed words. 

PRs are welcome!

## Weights

| File | Precision | Size |
|---|---|---:|
| `nemotron-3-diarization-bf16.gguf` | BF16 | 189.51 MiB |
| `nemotron-3-diarization-q8_0.gguf` | Q8_0 / mixed | 101.73 MiB |

This package was converted from the original `.nemo` checkpoint, not from an
existing GGUF. Each file contains 362 tensors, frontend configuration, and an
embedded model spec, with no separate weight or configuration files required.
The BF16 file retains the original model weight precision, with the frontend
mel filter stored in F32. BF16 is parity safe with Nemo with TF32 control.

Q8_0 quantizes 130 tensors; 229 remain BF16, two use
F16, and the mel filter remains F32. See the Q8 caveats below before choosing it.

Upstream: [nvidia/Nemotron-3-Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization/tree/723e19c601d99b7e58fba6a14e32153e0afe48d9),
pinned to revision `723e19c601d99b7e58fba6a14e32153e0afe48d9`.
This is a format conversion for audio.cpp, not an original NVIDIA release.

## Run

Use a current audio.cpp build with `nemotron_3_diar` support and a 16 kHz WAV:

```bash
audiocpp_cli --task diar --family nemotron_3_diar \
  --model /path/to/nemotron-3-diarization-bf16.gguf \
  --backend cuda --threads 8 --audio meeting.wav \
  --turns-out turns.json --log
```

For streaming, add `--mode streaming` and, for example,
`--session-option nemotron_3_diar.latency_profile=low`.
See the [model documentation](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/nemotron_3_diar.md)
for profiles and options.

## Server Batching

Create `server.json` with an absolute path to the GGUF:

```json
{
  "host": "127.0.0.1",
  "port": 8080,
  "backend": "cuda",
  "device": 0,
  "threads": 8,
  "lazy_load": false,
  "models": [
    {
      "id": "nemotron-3-diar",
      "family": "nemotron_3_diar",
      "path": "/path/to/nemotron-3-diarization-bf16.gguf",
      "task": "diar",
      "mode": "offline"
    }
  ]
}
```

```bash
audiocpp_server --config server.json --log
```

Send different-length recordings in one request:

```bash
curl -N http://127.0.0.1:8080/v1/batches/transcriptions \
  -F model=nemotron-3-diar \
  -F file=@meeting-a.wav \
  -F file=@meeting-b.wav \
  -F file=@meeting-c.wav
```

The default response is SSE. Each completed file receives a
`batch.transcription.result` event containing `speaker_turns`; use `index` to
associate it with the uploaded file.
Files do not need to have equal durations.

## Performance Compared With Python

Measured on an RTX 5090 using CUDA and eight CPU threads, with matching input
order and chunk settings:

- audio.cpp: debug server, BF16 or Q8_0 GGUF, `--log`, and the default `very_high`
  latency profile, using the server configuration above.
- Python: official NeMo model with PyTorch 2.11.0+cu128, `eval()` and
  `torch.inference_mode()`, `torch.set_num_threads(8)`, and
  `torch.manual_seed(663)`. Called `_check_streaming_parameters()` after
  setting the shared parameters below. `async_streaming=False`.
- Python inference used `diarize(audio=waveforms, sample_rate=16000,
  batch_size=len(waveforms), verbose=False)` with preloaded mono waveforms.
  Single requests used `batch_size=1`.
- Both C++ and Python used identical parameters: `chunk_len=340`,
  `chunk_right_context=40`, `fifo_len=40`, `spkcache_update_period=300`,
  and `spkcache_len=264`. These are C++'s default `very_high` profile values.
- No precision or TF32 overrides were applied.

The batch test varied batch size from one to six files and shuffled their order
across repeated requests. Recordings were 37-311 seconds long. The 24 mixed
batches contained 12,482 seconds of audio in total; the ten non-batch requests
contained 1,531 seconds. Models stayed loaded between requests.

| Workload | Runtime | Total inference time | Aggregate RTF | Sampled peak VRAM |
|---|---|---:|---:|---:|
| 24 mixed batches | audio.cpp server, BF16 | 11.984 s | 0.000960 | 1,076 MiB |
| 24 mixed batches | audio.cpp server, Q8_0 | 10.836 s | 0.000868 | 948 MiB |
| 24 mixed batches | Official Python | 9.718 s | 0.000779 | 2,786 MiB |
| 10 single requests | audio.cpp server, BF16 | 1.417 s | 0.000926 | 820 MiB |
| 10 single requests | audio.cpp server, Q8_0 | 1.684 s | 0.001100 | 740 MiB |
| 10 single requests | Official Python | 1.795 s | 0.001173 | 1,504 MiB |

Python was faster on the mixed batches; audio.cpp was faster on the single
requests with either GGUF. Q8 took about 10% less time than BF16 for batches,
but 19% more time for single requests, while reducing peak VRAM in both.
The C++ rows are fresh sequential BF16/Q8 reruns; the Python rows retain the
earlier same-day measurements on the identical request plans. Each row is one
workload sequence, not a median across repeated full benchmark runs. Results
depend on hardware, input lengths, and batch composition.

RTF is total inference time divided by total audio duration; lower is better.
Timing includes frontend and postprocessing, but excludes model loading, input
file I/O, and HTTP transfer. VRAM is per-process memory sampled every 20 ms,
including weights and CUDA context. Batch VRAM covers the full 33-request
sequence, including nine control/reference requests omitted from the timing
table; single-request VRAM includes warmup. Brief peaks may be missed.

## Q8 Results And Caveats

**Q8_0 is not exact-parity-safe. Use at your own risk: it can change speaker boundaries and turn
counts.** Performance and VRAM for matched BF16/Q8 workloads are reported above.
The following output comparisons come from the earlier separate CUDA validation
against C++ BF16, not Python or human-annotated ground truth. It used an RTX
5090, debug server, eight threads, logging enabled, and the default `very_high`
latency profile, without a TF32 override.

- Five short recordings retained their turn counts, with mostly 10 ms boundary
  shifts.
- The 97.6-second recording retained 31 turns; speaker activity differed over
  0.174% of the timeline.
- The 311-second recording changed from 161 to 152 turns; speaker activity
  differed over 1.174% of the timeline.
- Repeated requests within each precision produced identical turns and confidence.

The percentages compare same-label speaker activity on a 10 ms grid; they are
**not diarization error rates (DER)**. Use BF16 when preserving the original
model's output matters; Q8 trades output consistency for smaller weights and
lower VRAM usage. The Q8 results above do not validate streaming or other backends.

## License

The weights are governed by [OpenMDW-1.1](https://openmdw.ai/license/1-1/),
not audio.cpp's code license. A downloaded copy is included in
[`LICENSE.html`](LICENSE.html). Retain the license and applicable notices of
origin when redistributing this package. Original model by NVIDIA; GGUF
conversion for audio.cpp.
