---
type: Concept
title: QUAN-Transcribe Inference and Live Streaming
description: Documented QUAN-Transcribe CLI and Python deployment with 16 kHz input, chunked file decoding, recomputed live partials, endpoint finalization, and optional KenLM beam search.
tags: [stt, vietnamese, streaming, inference, endpointing]
status: stable
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T05:00:50Z }
stale_after: 2027-04-15
sources:
  - id: quan-captures
    resource: ../raw/QUAN-Transcribe-1.0/README-hf.md
    scope: ../raw/QUAN-Transcribe-1.0/
    kind: documentation
    title: QUAN-Transcribe-1.0 model card and inference README captures
---

The documented runtime for [QUAN-Transcribe-1.0](quan-transcribe-1.0.md) provides file/batch transcription, streaming-equivalent file decoding, and a live microphone interface. A crucial distinction is that `streaming=True` processes a complete file, while live updates re-decode the current sentence from its beginning every 0.48 s; chunk-limited attention does not itself prove incremental cache reuse (**Reported** behavior; cache distinction **Synthesis**).[^quan-captures]

## Installation and input/output

Documented commands, **not executed**:[^quan-captures]

```bash
pip install git+https://github.com/qnguyen3/QUAN-Transcribe
quan-transcribe audio.wav
quan-transcribe --streaming audio.wav
quan-transcribe --mic
```

Install a PyTorch build matching the CUDA driver first if needed; the README gives the CUDA 12.6 wheel index as an example. Development uses `git clone`, `uv sync`, then `uv run quan-transcribe --mic`. First use downloads the gated `google/embeddinggemma-2` encoder after accepting terms and authenticating with `hf auth login` or the `HF_TOKEN` environment variable; no credential value is part of the captures (**Reported**).[^quan-captures]

```python
from quan_transcribe import QuanTranscribe
asr = QuanTranscribe.from_pretrained("qnguyen3/QUAN-Transcribe-1.0")
text = asr.transcribe("audio.wav")
streaming_text = asr.transcribe("audio.wav", streaming=True)
texts = asr.transcribe([wav_a, wav_b], sample_rate=16000)
```

Files supported by libsndfile (README examples: WAV, FLAC, OGG, MP3) and NumPy/Torch waveforms are accepted and converted to 16 kHz mono. Output is lowercase Vietnamese, no punctuation, numbers spelled out. Long recordings are split at quiet points into pieces of at most 30 s (`chunk_seconds`) and batch decoded. `batch_seconds` / `--batch-seconds` defaults to 600 s of **padded** audio per forward pass; reduce it on out-of-memory errors (**Reported**).[^quan-captures]

Device preference is CUDA/bf16, then Apple Silicon `mps`/fp32, then CPU/fp32; override with `device=` / `--device`. No minimum Python/PyTorch version, VRAM requirement or measured CPU/MPS speed is supplied (**Reported**, missing fields **Observed**).[^quan-captures]

## Streaming and live finalization contract

- File `streaming=True`: reader attention sees the current 0.48 s chunk and prior chunks; encoder attention is already chunked with left context only and reader convolution is causal. `left_chunks` / `--left-chunks` limits reader past context, default all. The README says no more than one chunk of future lookahead and returns a complete transcript matching streaming deployment behavior (**Reported**).[^quan-captures]
- Live microphone: update unfinished text every 0.48 s; finished chunks' text stays fixed so only newest words can change. After `--endpoint` silence (default **0.8 s**), re-decode the sentence with full context and print a final line; `--lm` applies the LM to that final line. Continuous speech longer than `--chunk-seconds` is cut at a quiet point (**Reported**).[^quan-captures]
- Every live update re-decodes the current sentence from its start. The README says a CUDA or Apple Silicon GPU is needed to keep up; CPU display falls behind on long sentences. Neither encoder/reader cache reuse nor bounded per-update compute is established by the documentation (**Reported** warning; **Synthesis** limit).[^quan-captures]
- `--list-devices` lists microphones; `--input-device` selects by index or name. When piped (`quan-transcribe --mic > notes.txt`), only finished sentences are written (**Reported**; this writes a local transcript file).[^quan-captures]

Python live interface (**Reported**, not run): `from quan_transcribe.live import LiveSession`; construct `session = LiveSession(asr)`. Feed any-sized blocks of **16 kHz mono float32** to `session.accept(block)`, which yields finished sentences; `session.partial` holds unfinished text; `session.flush()` finishes the session.[^quan-captures]

**Synthesis for voice agents:** preserve a partial/final distinction because full-context final re-decoding can revise the earlier sentence. Measure stable-text delay, endpoint-to-final, sentence-length-dependent recomputation and concurrency separately. The 0.48 s update cadence, 0.8 s silence default and H100 batch throughput are not interchangeable latency guarantees; endpoint detection internals and network-server/session-isolation contracts are not documented here.[^quan-captures]

## Optional four-gram KenLM

Default decoding is greedy. The optional word-level four-gram KenLM model is **91 MB**, shipped in model-repo `lm/` and downloaded when first enabled. Installation adds `kenlm`, requiring a C++ compiler (**Reported**):[^quan-captures]

```bash
pip install "quan-transcribe[lm] @ git+https://github.com/qnguyen3/QUAN-Transcribe"
quan-transcribe --lm audio.wav
```

Python enables it with `QuanTranscribe.from_pretrained(..., lm=True)` and disables it per call using `transcribe(..., use_lm=False)`. `beam_width` / `--beam-width` defaults to 32; CLI weights are `--lm-alpha` and `--lm-beta`. The evaluation uses alpha 0.3 and beta 1.0, but these are not explicitly documented as runtime defaults. Custom `lm="path/to/model.bin"` / `--lm-path` must use a word-level KenLM trained on lowercase, unpunctuated text with numbers written as words (**Reported**; default distinction **Observed**).[^quan-captures]

LM text comprises about 29M Vietnamese words from Leipzig news 2022 and Wikipedia 2021 plus training transcripts. Beam search runs on CPU, **one utterance at a time**. The README reports about 15 ms extra per utterance on one CPU core at beam 32, 7 ms at beam 8, and says this becomes the main cost on GPU. No CPU model, utterance-length distribution or concurrency protocol accompanies those timings (**Reported**, missing conditions **Observed**). Accuracy benefits and digit-filtering conditions are in the [model concept](quan-transcribe-1.0.md).[^quan-captures]

## Relationships and coverage

- Depends on [QUAN-Transcribe-1.0](quan-transcribe-1.0.md), the gated base encoder and the weights' Gemma terms; a runtime command does not establish deployment rights.[^quan-captures]
- Used by [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) as a GPU-oriented Vietnamese partial/final candidate, not as demonstrated cache-aware serving (**Synthesis**).
- Both package READMEs were inspected completely; source identity is the package scope and canonical model-card entry point. No revision/date is supplied. Implementation, manifests, tests, weights, base encoder, `lm/`, underlying data and license terms are linked/referenced but not captured or inspected. No install, code execution, microphone session or timing was performed. Repeated examples were excluded; coverage and benchmark limits are shared with the model concept.
- `stable` describes completed documentation synthesis only. Implemented causality, finalization behavior, authentication/download behavior and performance remain unverified by this wiki.

[^quan-captures]: [Model card](../raw/QUAN-Transcribe-1.0/README-hf.md) — `Quick start`, `Model`, `Benchmark`, `License`. Supporting [inference README](../raw/QUAN-Transcribe-1.0/README-github.md) — `Install`; `Usage` CLI/Python and I/O/device/memory bullets; `Streaming mode`; `Live microphone` CLI and `LiveSession` example, final paragraph on recomputation; `Optional n-gram language model` installation, tuning, custom LM, cost and training text; `Accuracy check` timing paragraph.
