---
type: Concept
title: MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)
description: Self-contained GGUF weights of MOSS-Transcribe-Diarize for the zero-Python moss-transcribe.cpp CPU runtime, with joint transcription, diarization and timestamps, quantization ladder, and CLI usage.
tags: [stt, diarization, gguf, moss-transcribe-cpp, cpu, edge]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: moss-transcribe-cpp-gguf-card
    resource: ../raw/moss-transcribe.cpp-gguf.md
    kind: documentation
    title: MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)
  - id: moss-transcribe-diarize-card
    resource: ../raw/MOSS-Transcribe-Diarize.md
    kind: documentation
    title: MOSS-Transcribe-Diarize 0.9B HF model card
---

MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp) is a GGUF distribution of `OpenMOSS-Team/MOSS-Transcribe-Diarize` for [moss-transcribe.cpp](https://github.com/mudler/moss-transcribe.cpp), a from-scratch C++/ggml inference port that does joint long-form transcription, speaker diarization, and timestamps in one pass on CPU with no Python, PyTorch, or CUDA toolkit at inference, shipped as self-contained files embedding weights, tokenizer, mel filterbank, and config (**Reported**).[^moss-transcribe-cpp-gguf-card]

## Package identity and provenance

- Card title is `MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)`; weights are brought by the LocalAI team (**Reported**).[^moss-transcribe-cpp-gguf-card]
- Frontmatter declares `license: apache-2.0`, `base_model: OpenMOSS-Team/MOSS-Transcribe-Diarize`, `library_name: moss-transcribe.cpp`, `pipeline_tag: automatic-speech-recognition`, and tags including `gguf`, `ggml`, `speech-to-text`, `transcription`, `diarization`, `timestamps`, `moss-transcribe.cpp`, and `localai` (**Observed** by static inspection).[^moss-transcribe-cpp-gguf-card]
- Upstream model is MOSS-Transcribe-Diarize by the OpenMOSS / MOSI.AI team (arXiv:2601.01554) under Apache-2.0; the moss-transcribe.cpp engine is MIT-licensed and these GGUF weights keep the model's Apache-2.0 license (**Reported**).[^moss-transcribe-cpp-gguf-card]
- Each GGUF file is fully self-contained (weights, tokenizer, mel filterbank, and all config inside the GGUF); GPU execution is through ggml backends as those land (**Reported**).[^moss-transcribe-cpp-gguf-card]

## Files and quantization

- Only the large `ggml_mul_mat`-fed weights (Qwen3 and Whisper attention/FFN projections, the adaptor linears, and the token embedding, 343 tensors) are quantized; norms, biases, the conv stem, positional embeddings, and the mel filterbank stay F32 (**Reported**).[^moss-transcribe-cpp-gguf-card]
- Every file was verified end-to-end against the reference on the JFK sample (CPU, greedy, 8 threads); "Transcript" is versus the original PyTorch model and "speed" is total wall time on an 11 s clip on a 20-core x86 CPU at 8 threads, whole model plus load, with the autoregressive decode memory-bandwidth bound so smaller weights run faster (**Reported**).[^moss-transcribe-cpp-gguf-card]
- The F32 GGUF (3.4 GB, the parity reference) is not published here; produce it with the converter if needed (**Reported**).[^moss-transcribe-cpp-gguf-card]

| file | size | vs f32 | wall (11 s) | speed vs f32 | transcript vs reference |
| --- | ---: | ---: | ---: | ---: | --- |
| `moss-transcribe-f16.gguf` | 1.8 GB | 50% | 4.96 s | 1.6x | byte-identical |
| `moss-transcribe-q8_0.gguf` | 942 MB | 27% | 3.97 s | 2.0x | byte-identical |
| `moss-transcribe-q6_k.gguf` | 733 MB | 21% | 4.16 s | 1.9x | byte-identical |
| `moss-transcribe-q5_k.gguf` | 619 MB | 18% | 4.47 s | 1.8x | byte-identical |
| `moss-transcribe-q5_0.gguf` | 619 MB | 18% | 3.81 s | 2.1x | byte-identical |
| `moss-transcribe-q4_k.gguf` | 511 MB | 15% | 3.81 s | 2.1x | word-identical (one timestamp off 0.02 s) |
| `moss-transcribe-q4_0.gguf` | 511 MB | 15% | 3.57 s | 2.2x | word-identical (one timestamp off 0.07 s) |

Table values are source-reported measurements from the card's `Variants` table (**Reported**).[^moss-transcribe-cpp-gguf-card]

- Card recommendation: **q5_k** or **q5_0** for best size and accuracy (byte-identical to the reference at about one sixth the size); **q4_k**/**q4_0** for smallest and fastest (word-identical); **q8_0** for the largest fidelity margin; **f16** as the near-lossless full-precision equivalent (**Reported**).[^moss-transcribe-cpp-gguf-card]

## Benchmarks

- Same audio, same F32 weights, same threads, byte-identical transcript: moss-transcribe.cpp (ggml, CPU) stays under real time where PyTorch does not, and the gap holds as clips get longer, shown in `benchmarks/rtf_vs_length.png` (**Reported**, figure not reproduced here).[^moss-transcribe-cpp-gguf-card]
- Quantization makes the model both smaller and faster (decode is memory-bandwidth bound), with the transcript byte-identical through q5, shown in `benchmarks/quant_ladder.png` (**Reported**, figure not reproduced here).[^moss-transcribe-cpp-gguf-card]
- Full methodology and the reproducible harness are in the external `benchmarks/BENCHMARK.md` in the moss-transcribe.cpp repository, which was not fetched (**Reported**, with unfetched-pointer limit).[^moss-transcribe-cpp-gguf-card]

## Usage

- Build then run (example pins the q5_k file): `git clone --recursive https://github.com/mudler/moss-transcribe.cpp`, `cmake -B build && cmake --build build -j`, `hf download mudler/moss-transcribe.cpp-gguf moss-transcribe-q5_k.gguf --local-dir .`, `./build/moss-transcribe transcribe moss-transcribe-q5_k.gguf audio.wav` (**Reported**).[^moss-transcribe-cpp-gguf-card]
- Output is the compact `[start][Sxx]text[end]` transcript with inline speaker tags and timestamps, e.g. `[0.28][S01] And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.[10.59]` (**Reported**).[^moss-transcribe-cpp-gguf-card]
- Set `MTD_THREADS` to tune CPU threads (8 is a good default on a 20-core box; the decode is bandwidth bound, so fewer busy threads often beat more) (**Reported**).[^moss-transcribe-cpp-gguf-card]
- For production serving, the card points to LocalAI for an OpenAI-compatible `/v1/audio/transcriptions` endpoint with model gallery, concurrency, auth, and metrics (**Reported**).[^moss-transcribe-cpp-gguf-card]

## Relationships

- Upstream checkpoint: [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md) covers the upstream 0.9B Transformers card this GGUF port derives from — 90-minute 50+ language joint transcription plus diarization plus timestamps, CER/cpCER/Delta-cp benchmarks, hotword prompting, and SGLang/vLLM serving — while this concept covers the CPU GGUF files and quantization ladder (**Synthesis**).[^moss-transcribe-cpp-gguf-card][^moss-transcribe-diarize-card]
- Sibling GGUF distribution with a different runtime: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs a `MOSS-Transcribe-Diarize-GGUF` row (`moss_transcribe_diarize`, BF16 + Q8 + Q4_K, Apache-2.0) for audio.cpp, while this concept covers the `mudler/moss-transcribe.cpp-gguf` files (f16 through q4_0) for the moss-transcribe.cpp runtime; no shared weight file is asserted (**Synthesis**).[^moss-transcribe-cpp-gguf-card]
- Joint transcription-plus-diarization comparison: [VibeVoice-ASR](vibevoice-asr.md) covers a unified long-form ASR model with speaker, timestamp, and hotword-guided output, while this concept covers a GGUF CPU deployment of a joint transcription/diarization/timestamp model with a published quantization ladder and CLI; no shared architecture is asserted (**Synthesis**).[^moss-transcribe-cpp-gguf-card]
- Diarization-only comparison: [Nemotron 3 Diarization](nemotron-3-diarization.md) covers a streaming/offline diarization-only model with latency profiles and DER/RTFx benchmarks, while this concept covers joint one-pass transcription plus diarization with transcript-identity (not DER) quality figures; no shared architecture is asserted (**Synthesis**).[^moss-transcribe-cpp-gguf-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no GGUF downloaded, no build or transcribe command executed, and no size, speed, RTF, or transcript-identity figure reproduced (**Synthesis**).[^moss-transcribe-cpp-gguf-card]
- Linked but unfetched and not in `raw/`: the moss-transcribe.cpp repository and its converter, all seven `.gguf` weight files, the JFK sample audio, `benchmarks/rtf_vs_length.png`, `benchmarks/quant_ladder.png`, `benchmarks/BENCHMARK.md`, the upstream OpenMOSS model repository and arXiv:2601.01554, the LocalAI repository and serving stack, and the Hugging Face `mudler/moss-transcribe.cpp-gguf` repo (**Synthesis**).[^moss-transcribe-cpp-gguf-card]
- All architecture, self-containment, file-size, speed, transcript-identity, thread-tuning, and serving claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^moss-transcribe-cpp-gguf-card]

[^moss-transcribe-diarize-card]: [MOSS-Transcribe-Diarize 0.9B HF model card](../raw/MOSS-Transcribe-Diarize.md) — locators: header (0.9B joint transcription plus diarization plus timestamps, 50+ languages, 90-minute single pass, hotword prompting); `Evaluation` (CER/cpCER/Delta-cp table); `Serve with SGLang and VLLM`; `Subtitle Web App`.

[^moss-transcribe-cpp-gguf-card]: [MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)](../raw/moss-transcribe.cpp-gguf.md) — locators: frontmatter (`license`, `base_model`, `library_name`, `pipeline_tag`, `tags`); H1 plus intro paragraphs (from-scratch C++/ggml port of `OpenMOSS/MOSS-Transcribe-Diarize`, joint long-form transcription plus diarization plus timestamps in one pass, CPU plus ggml-backend GPU, no Python/PyTorch/CUDA toolkit, self-contained files, LocalAI-team credit); `Variants` section plus 7-row table (file names, sizes 1.8 GB/942/733/619/619/511/511 MB, vs-f32 50/27/21/18/18/15/15%, walls 4.96/3.97/4.16/4.47/3.81/3.81/3.57 s, speeds 1.6/2.0/1.9/1.8/2.1/2.1/2.2x, byte- vs word-identical notes with 0.02/0.07 s timestamp deltas; JFK-sample CPU greedy 8-thread verification sentence; 11 s clip 20-core x86 8-thread wall-time sentence; bandwidth-bound decode sentence; q5_k/q5_0 vs q4_k/q4_0 vs q8_0 vs f16 recommendation sentence; unpublished 3.4 GB F32 parity-reference plus converter sentence; 343-tensor `ggml_mul_mat` quantization-scope sentence); `Benchmarks` section (same-audio/weights/threads byte-identical sentence, under-real-time CPU-vs-PyTorch gap sentence, `benchmarks/rtf_vs_length.png` and `benchmarks/quant_ladder.png` figures, `benchmarks/BENCHMARK.md` harness link); `Usage` section (`git clone --recursive`, `cmake -B build && cmake --build build -j`, `hf download mudler/moss-transcribe.cpp-gguf moss-transcribe-q5_k.gguf --local-dir .`, `./build/moss-transcribe transcribe ... audio.wav` fence; `[0.28][S01] ... [10.59]` output example; `MTD_THREADS` 8-on-20-core tuning sentence); `For production serving` section (LocalAI `/v1/audio/transcriptions` endpoint, gallery, concurrency, auth, metrics); `Model` section (OpenMOSS/MOSI.AI credit, arXiv:2601.01554, Apache-2.0 weights, MIT engine); `Citation` bibtex (`moss_transcribe_cpp`, 2026). No publication date or pinned revision is stated in the source.
