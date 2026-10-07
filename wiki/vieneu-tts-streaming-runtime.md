---
type: Concept
title: VieNeu-TTS Streaming Runtime and Performance
description: How VieNeu-TTS v3 Turbo streams on GPU (CUDA-graph slots, continuous batching, one shared MOSS codec call) and CPU (torch-free ONNX, 4-frame lead-in, adaptive pacing), with RTX 3060 TTFA/RTF/lead measurements, `max_streams` sizing, unmeasured other-GPU estimates, and measurement and troubleshooting guidance.
tags: [tts, vietnamese, streaming, performance, gpu, cpu, onnx]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:32:00Z }
stale_after: 2027-10-07
sources:
  - id: vieneu-tts-docs
    resource: ../raw/vieneu-tts-docs/README.md
    scope: ../raw/vieneu-tts-docs/
    kind: documentation
    revision: 85344322b7258b4e25479b692e8e3396baf9db34
    title: VieNeu-TTS supporting docs (streaming guide and Docker Compose)
---

VieNeu-TTS v3 Turbo streams frame by frame through one GPU process that batches every running request into a single CUDA graph, or through a torch-free ONNX path on CPU; on an RTX 3060 the guide reports one stream at ~115 ms time to first audio and RTF 0.49, with 16 concurrent streams still real-time (median 185 ms, RTF 0.59) and 32 streams at RTF 0.93 with a negative lead, while a 6-core CPU does exactly one fp32 stream (RTF 0.55–0.61, two requests stall at RTF 1.19) or two int8 streams (RTF 0.35) (**Reported**).[^vieneu-tts-docs] The structurally important finding is that the **shared codec call is essentially the whole GPU cost and scales with the number of reserved `max_streams` slots, not with the streams actually running**, so every spare slot slows every request and `max_streams` should equal the real simultaneous load (**Reported**).[^vieneu-tts-docs]

## Three numbers: TTFA, RTF, lead

- **TTFA** (time to first audio) is measured from sending the request to the first **real audio byte**; with `wav` the header arrives after ~2 ms and is not counted (**Reported**).[^vieneu-tts-docs]
- **RTF** (real-time factor) is generation time divided by audio duration; a stream never stalls while RTF stays below 1, and RTF 0.5 leaves half the time spare (**Reported**).[^vieneu-tts-docs]
- **Lead** is audio received minus wall time since the first chunk; negative lead means a gap. The measured minimum lead is +80 ms on GPU at every load ≤ 16 streams and +320 ms on CPU (the 4-frame lead-in); clients should **pre-buffer 150–300 ms** to absorb network jitter (**Reported**).[^vieneu-tts-docs]
- One codec frame is 80 ms of audio (12.5 frames/s); the first chunk holds 2 frames on GPU or 4 on CPU, and later chunks hold 4 frames = 320 ms (**Reported**).[^vieneu-tts-docs]

## GPU: how streaming works

Code paths: `src/vieneu/v3_turbo_serve/stream.py` and `fused.py` (**Reported**).[^vieneu-tts-docs]

1. **One CUDA graph, B slots** (`max_streams`). Every 80 ms frame is one graph replay for all slots at once — the 16-codebook acoustic decoder, sampling, repetition penalty, and one backbone step — costing 7 ms per frame at B = 1 and 10 ms at B = 32, nearly independent of the number of streams (**Reported**).[^vieneu-tts-docs]
2. **Continuous batching.** A new request is prefilled (~21 ms for one prompt) and written into a free slot of the running graph (`StaticBackbone.load_row`: the KV cache is a ring buffer, the prompt lands right-aligned to the shared write index, rotary positions are per row); when a request hits EOS or its frame cap its slot frees immediately. Sampling settings are per-row tensors, so each request keeps its own temperature/top-k/top-p/penalty (**Reported**).[^vieneu-tts-docs]
3. **One shared streaming codec session** (MOSS). Every 4 frames the codes of every running row go through one `batch_decode(streaming=True)` call; a new row is decoded early once it has 2 frames (the lead-in) instead of waiting for the 4-frame boundary. The decoder has no lookahead, and streamed audio matches the full decode to 6e-4 (**Reported**).[^vieneu-tts-docs]
4. **One worker thread owns the GPU.** `infer_stream` from N HTTP threads is just N audio queues; the server never forks (**Reported**).[^vieneu-tts-docs]

| Component | Cost (RTX 3060, bf16) | Notes |
|---|---|---|
| Prefill (HF) | 21 ms (1 prompt) · 39 (8) · 73 (16) · 125 (32) | Once per request, between two frames |
| Graph frame | 7 ms (B=1) · 8 (8) · 9 (16) · 10 (32) | For the **whole** batch |
| Codec (4 frames) | ~65 ms + ~2.5 ms × reserved slots | Independent of frame count and of rows actually in use; launch-bound |

- The codec's built-in `use_cuda_graph` mode is 3x cheaper but produces wrong audio (correlation 0.2 with the plain decode), so it is not used (**Reported**).[^vieneu-tts-docs]
- The old pre-2026-09-15 path was a single-sequence engine without CUDA graphs: TTFA 280–360 ms, one lock for a whole utterance → 1 stream, RTF 0.85 (**Reported**).[^vieneu-tts-docs]

## GPU: measurements on an RTX 3060

Test machine: RTX 3060 12 GB, 12th-gen i5 (6 P-cores), Windows 11, torch 2.8 + cu128, bf16, preset voice (69-frame reference), sentences of 88–147 characters, `apply_watermark=False` for in-process runs, 2026-09-15 (**Reported**).[^vieneu-tts-docs]

Direct `infer_stream` (in process), N threads starting together:

| `max_streams` | N=1 | N=2 | N=4 | N=8 | N=16 | N=24 | N=32 |
|---|---|---|---|---|---|---|---|
| 8 — TTFA median / worst RTF | 89 ms / 0.39 | 151 / 0.44 | 147 / 0.43 | 162 / 0.45 | — | — | — |
| 16 (default) — TTFA median (max) / worst RTF | 115 / 0.49 | 130 / 0.51 | 130 / 0.52 | 164 / 0.56 | 185 (339) / 0.59 | — | — |
| 32 — TTFA median (max) / worst RTF | 141 / 0.70 | 165 / 0.71 | 174 / 0.73 | 207 / 0.77 | 220 (389) / 0.82 | 448 / 0.86 | 456 (629) / 0.93 |

- Minimum lead is +160 ms at N=1 and +80 ms elsewhere up to 16 streams; at 24 and 32 streams it turns negative (−1 ms and −28 ms) (**Reported**).[^vieneu-tts-docs]
- A new request arriving while others play: at `max_streams=16`, 115 ms among 3 streams, 145 ms among 7, and 134 ms among 15; at 32, 274 ms among 4, 180 ms among 8, 227 ms among 16, and 181 ms among 32 (**Reported**).[^vieneu-tts-docs]
- VRAM including the 0.5 GB model: `max_streams=8` 0.64 GB idle / 0.72 GB peak; 16: 0.91 / 1.10; 32: 1.45 / 1.82 (**Reported**).[^vieneu-tts-docs]

Over HTTP (`apps/openai_speech.py`, client on the same machine, watermark on):

| Scenario | TTFA | RTF |
|---|---|---|
| 1 request, `pcm` 48 kHz | 106 ms | 0.47 |
| 1 request, `pcm` + `sample_rate=24000` | 105 ms | 0.46 |
| 1 request, `sse` | 99 ms | — |
| 4 clients at once | median 160 ms | 0.51 |
| 8 clients at once | 207 ms | 0.53 |
| 16 clients at once | 197 ms (max 336) | 0.59 |
| 40 clients (16 slots + 16 queue) | 32 OK, 8 × `429`; queued see TTFA 1.5–3 s | — |

- HTTP TTFA is within ~0–10 ms of the in-process number; add network RTT in production (**Reported**).[^vieneu-tts-docs]

**A "cold" GPU after idling pays 100–300 ms extra.** Within ~2 s of idle the NVIDIA driver parks the GPU in its power-saving state (RTX 3060: P8, 210 MHz, 12 W); the next request runs its prefill, two lead-in frames, and the codec call at those clocks before ramping back to ~1950 MHz. Warm 118 ms vs **403 ms after 8 s idle**; 16 clients warm median 194 ms (max 354) vs median 330–400 ms (max 450–540) after 5–8 s idle. Keeping it warm from inside the process **does not work** (a 2048² matmul or whole-graph replays every 100–250 ms still let the driver park the GPU); the fix is host-side: lock clocks with `nvidia-smi -lgc 1500,2100` (undo `-rgc`; on Linux also `nvidia-smi -pm 1`, run on the host when using Docker), or Windows NVIDIA Control Panel → Manage 3D settings → *Power management mode* = **Prefer maximum performance**, or accept that only the first request after > 2 s idle is affected (**Reported**).[^vieneu-tts-docs]

## Choosing `max_streams`

| Goal | `max_streams` | On a 3060 |
|---|---|---|
| Lowest latency, few users | 8 | 1 stream 89 ms, 8 streams 162 ms, GPU 45 % busy |
| Balanced (default) | 16 | 1 stream 115 ms, 16 streams ≤ 200 ms, GPU 59 % busy |
| Maximum throughput | 32 | 32 streams do not stall (RTF 0.93) but first audio takes ~450 ms with no margin; 24 is more tolerable |

- Rule: set `max_streams` to the highest number of **simultaneous** streams actually needed, no more — every spare slot adds ~2.5 ms to **every** codec call for **everyone** (**Reported**).[^vieneu-tts-docs]
- **Streams ≠ users.** A stream exists only while one reply plays (a few seconds). A voice-chat user holds a stream ~20–35 % of the time, so 16 streams ≈ **45–80 active users**; for continuous reading (news, books) 16 streams = 16 users. Rule of thumb: `users ≈ max_streams / fraction of time spent listening to TTS` (**Reported**).[^vieneu-tts-docs]
- "N at once" is the worst case (up to 8 requests admitted per tick and their lead-in codec calls pile up); spread-out real traffic behaves like the "new request among N−1" column, ~135 ms at 16 streams (**Reported**).[^vieneu-tts-docs]

## GPU: estimates for other machines

**Nothing but the RTX 3060 was measured**; the table below is the source's own reasoning from the cost structure, for planning and to be verified locally (**Reported** estimate, not measured).[^vieneu-tts-docs]

- VRAM is not the limit: 4 GB fits 16 streams, 6 GB fits 32 (**Reported**).[^vieneu-tts-docs]
- The limit is per-call, **launch-bound overhead, not FLOPS**: the 12-layer/768-wide backbone and the 11M-parameter codec are tiny, so a much larger GPU (4090, A100) does **not** cut TTFA much; host CPU speed, driver, and PCIe matter as much (**Reported**).[^vieneu-tts-docs]
- GPU generation matters through dtype and CUDA graphs: Ampere and newer run bf16 like the test machine; Turing/Pascal lack bf16 and fall back to **fp16**, a path **unverified for quality** (activation overflow possible); CUDA graphs need a CUDA ≥ 11 driver, available since Maxwell (**Reported**).[^vieneu-tts-docs]

| Machine | VRAM | Est. TTFA, 1 stream | Est. real-time streams |
|---|---|---|---|
| RTX 3060 12 GB (measured) | 12 | 105–115 ms | 16 comfortably, 32 max |
| RTX 3050 / 4060 8 GB, 3060 Ti / 4070 | 6–12 | 100–130 ms | 16, up to ~32 |
| RTX 3050 laptop 4 GB, RTX A2000 | 4 | 120–160 ms | 8–12 (`max_streams=8`–`12`) |
| RTX 4090 / A10 / L4 | 16–24 | 90–110 ms | 24–32 |
| T4 16 GB (cloud) | 16 | 150–220 ms | 8–12 |
| GTX 1660 / RTX 2060 6 GB | 6 | 140–200 ms | 8–12 |
| GTX 1650 4 GB, GTX 1050 Ti | 4 | 180–250 ms | 4–8 |
| GPU < 4 GB | <4 | — | 2–4, or use the CPU |

- Planning formulas: `TTFA ≈ prefill (20–40 ms) + 2 graph frames (15–25 ms) + one codec call (60–120 ms)`; `streams ≈ (80 ms − graph frame) / (codec cost ÷ 4 frames)`, keeping RTF ≤ 0.6–0.7 for margin. On 4–6 GB cards set `VIENEU_MAX_STREAMS=8` (or 12) from the start (**Reported**).[^vieneu-tts-docs]

## CPU: how streaming works, measurements

Code path: `src/vieneu/_v3_turbo_engine/onnx_runtime_lite.py` (`infer_stream`). A CPU-only machine runs **without torch**: backbone and acoustic decoder are ONNX, and the codec is `moss_audio_tokenizer_decode_step.onnx`, a streaming decoder **bit-exact** with the full one (no lookahead, no clicks at chunk edges) (**Reported**).[^vieneu-tts-docs]

1. The prompt (reference codes + phonemes) is prefilled once; then per frame the 16-codebook acoustic decoder runs as 16 small ONNX calls plus one backbone step with a KV cache (**Reported**).[^vieneu-tts-docs]
2. **4-frame lead-in** (320 ms of audio) is buffered before the first chunk is decoded, so the client survives fluctuations in generation speed (**Reported**).[^vieneu-tts-docs]
3. **Adaptive pacing** (`_target_frames`): if emitted audio exceeds elapsed time by < 0.2 s, decode every 4 frames; < 0.55 s → 6; < 1.1 s → 8; with a comfortable lead, up to 25 frames per call (fewer codec calls, better RTF) (**Reported**).[^vieneu-tts-docs]
4. ORT `intra_op_threads` = physical cores (max 8, `Vieneu(threads=...)`), `inter_op = 1`, no spinning, so an idle server does not burn CPU (**Reported**).[^vieneu-tts-docs]
5. A **per-frame** `RLock` lets two simultaneous requests interleave rather than fully queue, but they share the cores and each slows down (**Reported**).[^vieneu-tts-docs]

Measurements (12th-gen i5, 6 P-cores, 6 ORT threads; sentences of 27 / 88 / 147 characters):

| Precision | TTFA (27 / 88 / 147 chars) | RTF, 1 stream | Min lead | 2 requests at once |
|---|---|---|---|---|
| **fp32** (default) | 264–282 / 313–357 / 345–401 ms | 0.61 / 0.57 / 0.55 | +320 ms | TTFA 399 / 564 ms, **RTF 1.19 / 1.19 → both stall** |
| **int8** | 141–144 / 163–169 / 192–194 ms | 0.35 / 0.35 / 0.35 | +320 ms | TTFA 224 / 336 ms, RTF 0.58 / 0.67 → real-time |

- **fp32: exactly one stream.** The server defaults to `max_streams=1`; a second request waits in the queue (`VIENEU_QUEUE`, default = `max_streams`; the Docker `api-cpu` profile sets 4) for up to `VIENEU_QUEUE_TIMEOUT` seconds, then gets `429`. The wait equals the remaining generation of the sentence playing (a 7 s sentence generates in ~4 s) (**Reported**).[^vieneu-tts-docs]
- **int8: two streams** (default `max_streams=2`) on 6 cores at RTF ~0.65 each; a third would hit 1.0. 8–12 physical cores may sustain 3–4, but measure first (**Reported**).[^vieneu-tts-docs]
- TTFA depends on the first sentence's length (longer prefill) and the core count: a 4-core laptop sees fp32 ~400–600 ms / int8 ~200–300 ms; on 2–4 cores fp32 RTF can exceed 1, so use int8 only (**Reported**).[^vieneu-tts-docs]
- int8 **needs a CPU with VNNI** (Intel Cascade Lake / Ice Lake / Alder Lake, AMD Zen 4); without VNNI the int8 acoustic decoder saturates and babbles — use fp32 (**Reported**).[^vieneu-tts-docs]
- Clients should pre-buffer ≥ 300 ms (exactly the lead-in) because other processes compete for the CPU, and there is no CPU batching scheduler: more requests means splitting cores, nothing comes "for free" as on GPU. For more streams without a GPU, run several containers pinned with `docker --cpuset-cpus`, or accept `429` and let clients retry (**Reported**).[^vieneu-tts-docs]

## Measuring it on your machine

```bash
uv run python -m apps.openai_speech &                     # or the docker api-gpu / api-cpu profiles
uv run python examples/openai_speech_client.py            # 1 request: TTFA, RTF, out_stream.wav
uv run python examples/openai_speech_client.py --bench 8  # 8 clients at once
uv run python examples/openai_speech_client.py --bench 16
```

- `RTF max` must be < 1, ideally ≤ 0.7; if `--bench N` shows RTF > 0.8, N exceeds the machine and `VIENEU_MAX_STREAMS` should drop (**Reported**).[^vieneu-tts-docs]
- A `TTFA max` far above the median (339 vs 185 at 16 streams) is prefill pile-up, while spread-out traffic sits near the median. The server logs `ttfa=… total=… audio=… rtf=… active=…` per request; on GPU watch `nvidia-smi`, or use `torch.cuda.max_memory_allocated()` in process for precision (**Reported**).[^vieneu-tts-docs]

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Slow first chunk even with few users (GPU) | `max_streams` too large → codec pads many slots | Lower `VIENEU_MAX_STREAMS` to the real load (8 for ≤ 8 streams) |
| First request after a few idle seconds is 100–300 ms slower (GPU) | GPU parked at low clocks (P8) | Lock clocks with `nvidia-smi -lgc`, or Windows "Prefer maximum performance" |
| Frequent `429` | Slots and queue exhausted | Raise `VIENEU_QUEUE` / `VIENEU_QUEUE_TIMEOUT` if waiting is acceptable, else add a GPU/container |
| Choppy audio at the client | No pre-buffer, or RTF > 1 (CPU fp32 with several requests) | Pre-buffer 150–300 ms (GPU) / ≥ 300 ms (CPU); on CPU use int8 and keep 1–2 streams |
| First request after start-up takes 1–2 s | Warm-up not finished | Wait for `/health` to return `ok` before sending traffic |
| Turing/Pascal GPU, odd audio | fp16 fallback is unverified | Try `Vieneu(dtype="float32")` (~1.5× slower) or file an issue with a sample |
| Need `mp3`/`opus` | Not supported | Put a reverse proxy/ffmpeg in front, or take `pcm` and encode client-side (adds ~20–40 ms) |
| A non-default `repetition_window` has no effect (GPU) | The penalty window is the scheduler's fixed ring size | Tune `repetition_penalty` instead |

- A dropped connection does **not** keep a slot: closing the response closes the generator and the GPU slot frees at the next tick (stated as verified by the source) (**Reported**).[^vieneu-tts-docs]
- `VIENEU_FUSED_FRAME=0` disables the CUDA-graph path for debugging and falls back to the single engine (1 stream, ~300 ms) (**Reported**).[^vieneu-tts-docs]

## Relationships

- Served over HTTP by [VieNeu-TTS OpenAI-Compatible Speech API](vieneu-tts-openai-speech-api.md): request fields, formats, and `/health` expose this engine (**Synthesis**).[^vieneu-tts-docs]
- Deployed by [VieNeu-TTS Docker Compose Deployment](vieneu-tts-docker-deployment.md), whose `api-gpu`/`api-cpu` profiles set `VIENEU_MAX_STREAMS`, `VIENEU_QUEUE`, and the healthcheck described here (**Synthesis**).[^vieneu-tts-docs]
- Measures the serving behavior of [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md); its repository-README TTFA/RTF figures are the same operating point, expanded here with per-`max_streams` tables and the codec-cost explanation (**Synthesis**).[^vieneu-tts-docs]
- Deployment comparison: [Speech-to-Speech Realtime Engine](speech-to-speech-realtime-engine.md) covers a different realtime pipeline whose stage-level instrumentation and concurrency model differ from this single-process CUDA-graph scheduler; no shared codebase is asserted (**Synthesis**).

## Coverage and limits

- Inspected statically as the captured `docs/streaming.md` (SHA-256 `7d20149c…` matching `checksums.json`); no server, GPU, or ONNX session was run, no audio was synthesized, and no TTFA, RTF, lead, VRAM, stream-count, or throughput figure was reproduced (**Synthesis**).[^vieneu-tts-docs]
- The other-machine table is explicitly the source's own estimate, not a measurement, and remains **Reported/unverified** (**Synthesis**).[^vieneu-tts-docs]
- Referenced implementation paths (`src/vieneu/v3_turbo_serve/stream.py`, `fused.py`, `src/vieneu/_v3_turbo_engine/onnx_runtime_lite.py`), `examples/openai_speech_client.py`, tests under `tests/fused/`, and the MOSS codec checkpoint are not in `raw/` and were not inspected, so the mechanism description is a source claim (**Synthesis**).[^vieneu-tts-docs]
- Latency, throughput, and compatibility figures are version-, hardware-, and driver-specific and carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^vieneu-tts-docs]

[^vieneu-tts-docs]: [VieNeu-TTS supporting docs](../raw/vieneu-tts-docs/README.md) — locators: package README coverage ledger; `docs/streaming.md` §At a glance table; §Three numbers (TTFA/RTF/lead definitions, 80 ms frame and chunk sizes); §GPU: how streaming works (stream.py/fused.py, 4 numbered mechanism points, component-cost table, `use_cuda_graph` rejection, pre-2026-09-15 path); §GPU: measurements (test-machine paragraph, `max_streams` 8/16/32 tables, new-request and VRAM rows, HTTP table, cold-GPU table and P8 paragraph); §choosing `max_streams` (goal table, spare-slot rule, streams-vs-users rule, "N at once" note); §other-machine estimates (three facts, machine table, TTFA/streams formulas); §CPU (onnx_runtime_lite.py, 5 mechanism points, precision table, fp32/int8 conclusions, VNNI, pre-buffer); §Measure it (client commands and reading notes); §Tuning and troubleshooting table (incl. dropped-connection and `VIENEU_FUSED_FRAME=0` rows); SHA-256 recorded in `checksums.json`.
