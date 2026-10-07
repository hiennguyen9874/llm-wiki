---
type: Concept
title: NeMo-Speech.cpp ASR Models and Quantization
description: The NeMo-Speech.cpp ASR model roster and CLI pull names, its one-GGUF-per-model loader and default Nemotron 3.5 choice, the `--outtype` quantization ladder with alignment caveats, the CUDA planar Q8 layout, and the optional Silero VAD, Sortformer, and PnC companion GGUFs.
tags: [stt, pipeline, gguf, quantization, diarization, vad, deployment]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:12:00Z }
stale_after: 2027-10-07
sources:
  - id: nemo-speech-cpp-docs
    resource: ../raw/nemo-speech-cpp-docs/README.md
    scope: ../raw/nemo-speech-cpp-docs/
    kind: documentation
    revision: 8642eaa5cc51efbc17ad0f3e433944ba858a873f
    title: NVIDIA/NeMo-Speech.cpp supporting docs
---

[NeMo-Speech.cpp](nemo-speech-cpp.md) loads exactly one **GGUF** per ASR model, resolves models by short name, full repository ID, or a local path, and indexes ready-to-run Q8 GGUFs with `nemo-speech model list` / `nemo-speech pull`; `nemotron-3.5` is the default when `--model` is omitted, and quantization is chosen at conversion time with `--outtype` (portable `q8_0` default) while the runtime also loads optional Silero VAD, Sortformer diarization, and PnC companion GGUFs (**Reported**).[^nemo-speech-cpp-docs]

## Model roster and selection

- The runtime ships with a model roster indexed by the CLI; `nemotron-3.5` is the default for the CLI and `nemo-speech pull nemotron-3.5` fetches it, while `nemotron-en`, `parakeet-tdt`, and `parakeet-ctc` are the English and Parakeet pull names (**Reported**).[^nemo-speech-cpp-docs]
- Short names are documented alongside their Hugging Face checkpoints: [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) (`nvidia/nemotron-3.5-asr-streaming-0.6b`, prompt-conditioned RNNT, 40+ language-locales, `auto` detection, the CLI default), [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) (`nemotron-en`), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) (`parakeet-tdt`, offline-only, streaming rejected), and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md) (`parakeet-ctc`, offline or buffered streaming) (**Reported**).[^nemo-speech-cpp-docs]
- [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) explicitly does not support cache-aware streaming; streaming requests are rejected with an error, so it is restricted to `nemo-speech transcribe`, `POST /v1/audio/transcriptions`, or gRPC `Recognize` (**Reported**).[^nemo-speech-cpp-docs]
- Custom checkpoints or alternate quantizations are converted with the root `convert_model.py`; ASR head type (CTC, RNNT, or TDT) is auto-detected, with `--head-type` only as an override (**Reported**).[^nemo-speech-cpp-docs]

## Quantization (`--outtype`)

`python3 convert_model.py model.nemo --outfile model.gguf --outtype q8_0` quantizes linear and pointwise-convolution weights while other tensors keep their supported floating-point formats (**Reported**).[^nemo-speech-cpp-docs]

| `--outtype` | format | bytes/elem | use case |
|---|---|---|---|
| `q8_0` (default) | Q8_0 | 1.062 | compact, high-quality default |
| `bf16` | BF16 | 2.000 | modern NVIDIA / ARM v9 |
| `fp16` | F16 | 2.000 | Apple Silicon, older GPUs |
| `q6_k` | Q6_K | 0.820 | smaller artifact, more quantization |
| `q5_k` | Q5_K | 0.688 | smaller artifact, more quantization |
| `q4_k` | Q4_K | 0.562 | compact K-quant |
| `nvfp4` | NVFP4 | 0.562 | FP4; native acceleration on supported Blackwell GPUs |
| `mxfp4` | MXFP4 | 0.531 | compact FP4; acceleration depends on the backend |

- K-quants (`q4_k`/`q5_k`/`q6_k`) require the inner dimension divisible by 256; any tensor failing alignment falls back to F16 and is reported by the converter. NVFP4 and MXFP4 require the inner dimension divisible by 64 and use the same fallback (**Reported**).[^nemo-speech-cpp-docs]
- FP4 accuracy and performance should be validated on the target model and backend before deployment (**Reported**).[^nemo-speech-cpp-docs]

### CUDA planar Q8 layout

- The default Q8 layout is portable; for high-concurrency CUDA inference the converter can emit a planar Q8 layout with `--outtype q8_0 --q8-layout planar`. Planar Q8 is CUDA-only, so a default-layout artifact should be kept for other backends (**Reported**).[^nemo-speech-cpp-docs]

## Companion models

These optional GGUFs load alongside the ASR model and can change without reconverting it; they are enabled with runtime options in [ASR configuration](nemo-speech-asr-configuration.md) (**Reported**).[^nemo-speech-cpp-docs]

### Silero VAD

- Used for VAD feature masking and VAD-driven endpointing; convert from the public package with `pip install "silero-vad==6.2.0"` then `python3 convert_model.py silero --outfile models/silero-v6.2.0.gguf`, or from an existing whisper.cpp Silero checkpoint with `--from-whisper-ggml` (**Reported**).[^nemo-speech-cpp-docs]

### Sortformer speaker diarization

- Used for ASR speaker tags and standalone `nemo-speech diarize`; both models stream long recordings and run full attention over short ones (**Reported**).[^nemo-speech-cpp-docs]

| Model | Preset name | Speakers | Output frame |
|---|---|---|---|
| [Streaming Sortformer 4-speaker v2](diar-streaming-sortformer-4spk-v2.md) | V2 | 4 | 80 ms |
| [Nemotron 3 Diarization](nemotron-3-diarization.md) | V3 | 8 | 10 ms |

- Default streaming geometry in 80 ms frames: V2 chunk 20 / right context 0 / FIFO 80 / speaker cache 160 / update period 80; V3 chunk 13 / right context 1 / FIFO 80 / speaker cache 264 / update period 40. Override with `--diar-preset` or the `asr.diar.*` keys (**Reported**).[^nemo-speech-cpp-docs]
- Segment postprocessing defaults follow the checkpoint and may need tuning for the audio; `--outtype f32` is the default for `convert_model.py nvidia/...`, while f16 and q8_0 produce smaller artifacts (**Reported**).[^nemo-speech-cpp-docs]

### PnC (punctuation + capitalization)

- Restores casing and `. , ?` for models that emit lowercase unpunctuated text (for example [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md)); use a compatible PnC GGUF or convert a local NeMo BERT PnC `.nemo` checkpoint with `convert_model.py pnc.nemo --outfile pnc-bert.q8_0.gguf --outtype q8_0` (**Reported**).[^nemo-speech-cpp-docs]

## Relationships

- Packages models for [NeMo-Speech.cpp](nemo-speech-cpp.md): this is the model/quantization sibling of that page's runtime identity, while key-by-key recognizer behavior lives in [NeMo-Speech.cpp ASR Configuration](nemo-speech-asr-configuration.md) (**Synthesis**).[^nemo-speech-cpp-docs]
- Serves [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md); those pages hold the checkpoint-level accuracy, language, and training detail (**Synthesis**).[^nemo-speech-cpp-docs]
- Uses [Silero VAD](silero-vad.md), [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md), and [Nemotron 3 Diarization](nemotron-3-diarization.md) as optional companion GGUFs; consult those pages for model-level behavior while this page holds the runtime conversion and preset geometry (**Synthesis**).[^nemo-speech-cpp-docs]
- Compare with [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) and [transcribe.cpp](transcribe-cpp.md) for other ggml runtimes where a GGUF is a runtime-matched container rather than an interchangeable format (**Synthesis**).[^nemo-speech-cpp-docs]

## Coverage and limits

- Source inspected statically only; the capture's five documents were read as captured Markdown and their SHA-256 digests re-computed to match `checksums.json` (**Observed** for capture integrity; the manifest is a local capture record, not independent provenance). Roster, quantization, and geometry claims are documentation assertions (**Reported**).[^nemo-speech-cpp-docs]
- No model or companion GGUF was downloaded or converted, no `convert_model.py` invocation was executed, and no quantized artifact was benchmarked, so the size/precision tradeoff, alignment fallback, and planar-Q8 acceleration claims are unverified for any specific checkpoint (**Synthesis**).[^nemo-speech-cpp-docs]
- `convert_model.py`, `docs/model-conversion.md`, the linked Hugging Face checkpoint pages, and the diarization model cards are outside this capture and were not fetched; per-quantization accuracy figures are not stated here (**Synthesis**).[^nemo-speech-cpp-docs]
- Model names, pull aliases, and quantization options are version-sensitive and carry `stale_after: 2027-10-07` under the `stt` domain rule (**Synthesis**).[^nemo-speech-cpp-docs]

[^nemo-speech-cpp-docs]: [NVIDIA/NeMo-Speech.cpp supporting docs](../raw/nemo-speech-cpp-docs/README.md) — capture at upstream revision `8642eaa5cc51efbc17ad0f3e433944ba858a873f` (2026-10-07). Locators: `docs/asr/models.md` → intro (`model list`, `pull nemotron-3.5`, default model, short name/repository ID/local path), `Nemotron 3.5 (0.6B, multilingual, prompt-conditioned RNNT)` (HF repo, `--language auto`, ITN grammar selection), `Nemotron-Speech Streaming (0.6B, cache-aware RNNT)`, `Parakeet TDT (0.6B v3, multilingual, offline transducer)` (streaming rejection), `Parakeet CTC (1.1B, offline / buffered streaming)`, `Converting custom ASR checkpoints` (auto head detection, `--head-type`), `Quantization (--outtype)` table + K-quant/NVFP4 alignment paragraph + FP4 validation note, `CUDA batching: planar Q8 layout` (`--q8-layout planar`, CUDA-only), `Companion models (optional)` intro, `Silero VAD` (`pip install "silero-vad==6.2.0"`, `--from-whisper-ggml`), `Sortformer speaker diarization` (V2/V3 table, `f32` default, geometry table, `--diar-preset`/`asr.diar.*`), `PnC (punctuation + capitalization)` (`convert_model.py pnc.nemo`). Limitations: `convert_model.py`, `docs/model-conversion.md`, Hugging Face checkpoint pages, and the diarization model cards are outside this capture.
