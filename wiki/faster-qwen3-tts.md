---
type: Concept
title: Faster Qwen3-TTS
description: CUDA-graph and GGML inference wrapper for Qwen3-TTS with streaming synthesis, clone/custom/design APIs, and multi-GPU RTF/TTFA benchmarks.
tags: [tts, streaming, inference-optimization, cuda-graphs, ggml]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:35:26Z }
stale_after: 2027-10-06
sources:
  - id: faster-qwen3-tts-readme
    resource: ../raw/faster-qwen3-tts.md
    kind: documentation
    title: Faster Qwen3-TTS README
---

Faster Qwen3-TTS is a real-time inference wrapper around Qwen3-TTS that accelerates the Talker plus Code Predictor decode step with `torch.cuda.CUDAGraph` static-cache replay on NVIDIA GPUs and an experimental GGML backend via `qwentts.cpp` for CUDA and Apple Silicon Metal, exposing streaming and non-streaming voice clone, CustomVoice, and VoiceDesign generation through Python, CLI, server, demo UI, and OpenAI-compatible API paths with published multi-GPU RTF/TTFA benchmarks (**Reported**).[^faster-qwen3-tts-readme]

## Backends and install

- Torch backend uses `torch.cuda.CUDAGraph` and requires an NVIDIA GPU with CUDA; GGML backend supports CUDA and Apple Silicon Metal (**Reported**).[^faster-qwen3-tts-readme]
- Requires Python 3.10+ and PyTorch 2.5.1+; install with `pip install faster-qwen3-tts` (**Reported**).[^faster-qwen3-tts-readme]
- Default install uses `qwen-tts-hf`, described as a temporary PyPI compatibility build of Qwen3-TTS with Transformers 5 support providing the same `qwen_tts` package as upstream `qwen-tts`; the source warns not to install both distributions in the same environment (**Reported**).[^faster-qwen3-tts-readme]
- PyTorch floor is 2.5.1 because CUDA-graph capture in the fast path is described as unreliable on `torch<=2.5.0` ("operation not permitted when stream is capturing") (**Reported**).[^faster-qwen3-tts-readme]
- Blackwell RTX 50xx GPUs need CUDA 12.8 PyTorch wheels; the source recommends a `cu128` PyTorch build (PyTorch 2.7+) if default setup fails (**Reported**).[^faster-qwen3-tts-readme]
- On driver/CUDA mismatches (e.g. T4, A10G, CUDA-12.4 hosts where `torch.cuda.is_available()` returns `False`), install a PyTorch wheel matching the driver's CUDA version shown by `nvidia-smi`; the documented CUDA 12.4 example is `pip install "torch==2.5.1" "torchaudio==2.5.1" --index-url https://download.pytorch.org/whl/cu124` (**Reported**).[^faster-qwen3-tts-readme]
- CLI selects Torch when CUDA is available and GGML otherwise; `--backend` overrides explicitly. On native Apple Silicon Python the default install includes the GGML Metal runtime and the CLI selects it automatically; Intel Macs and Rosetta Python are not supported by the Metal wheel (**Reported**).[^faster-qwen3-tts-readme]
- On other platforms install the `ggml` extra (`pip install "faster-qwen3-tts[ggml]"`), which requires `qwentts-cpp-python>=0.5.0`; PyPI provides Metal (macOS 14+, native Apple Silicon) and CUDA 12.8 Linux wheels with no local native build needed, while other Linux runtimes install the matching wrapper wheel from the Hugging Face wheelhouse (documented `cu128` Ubuntu 22.04 and `cu130` CUDA 13 / DGX Spark variants, same ABI v5) (**Reported**).[^faster-qwen3-tts-readme]
- GGML backend defaults to `log_level="warning"` in Python and CLI; `--verbose` or `qwentts_log_level="debug"` restores native diagnostics (**Reported**).[^faster-qwen3-tts-readme]
- GGML backend caches raw reference audio as qwentts.cpp `.spk` speaker latents plus `.rvq` acoustic latents after the first clone request, and also accepts precomputed references directly (`--ref-spk`, `--ref-rvq`, `--ref-text`) so repeat requests skip reference-audio encoding (**Reported**).[^faster-qwen3-tts-readme]

## Interfaces

- Python: `FasterQwen3TTS.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-Base")` with `generate_voice_clone_streaming(text, language, ref_audio, ref_text, chunk_size=8)` yielding `(audio_chunk, sr, timing)` tuples and `generate_voice_clone(text, language, ref_audio, ref_text)` returning `(audio_list, sr)` (**Reported**).[^faster-qwen3-tts-readme]
- `model.warmup(prefill_len=100)` explicitly prepares a model before serving; it captures CUDA graphs for Torch and is a safe no-op for GGML, while normal generation also performs lazy preparation (**Reported**).[^faster-qwen3-tts-readme]
- Local playback helper `examples/audio.py:StreamPlayer` keeps one output stream open and queues chunks; a one-shot player such as `sounddevice.play(audio_chunk, sr)` restarts playback per chunk and can introduce gaps (**Reported**).[^faster-qwen3-tts-readme]
- CLI voice cloning: `faster-qwen3-tts clone --model Qwen/Qwen3-TTS-12Hz-1.7B-Base --text ... --language English --ref-audio ref_audio.wav --ref-text ... --output out.wav` (**Reported**).[^faster-qwen3-tts-readme]
- CLI CustomVoice: `faster-qwen3-tts custom --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --list-speakers` and synthesis with `--speaker aiden`; CLI VoiceDesign: `faster-qwen3-tts design --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --instruct ...` (**Reported**).[^faster-qwen3-tts-readme]
- CLI streaming to file appends `--streaming` and prints RTF after write; server mode `faster-qwen3-tts serve --mode custom --model ... --speaker aiden --language English --streaming` keeps the model hot until `exit` (**Reported**).[^faster-qwen3-tts-readme]
- Demo UI (`pip install -e ".[demo,ggml]"`, `python demo/server.py --backend ggml`, `http://localhost:7860`) streams audio in real time with TTFA/RTF display, voice clone upload/microphone, 1.7B-VoiceDesign design, GGML/Torch toggle, streaming toggle, adjustable chunk size, and WAV download; it defaults to GGML/qwentts.cpp (**Reported**).[^faster-qwen3-tts-readme]
- OpenAI-compatible server (`examples/openai_server.py`, `POST /v1/audio/speech`) works with OpenWebUI, llama-swap, and other OpenAI clients; `--ref-audio/--ref-text/--language/--port` configure a single voice, `--voices voices.json` maps `voice` names to reference-audio configs, WAV/PCM stream per chunk while MP3 requires `pydub` (**Reported**).[^faster-qwen3-tts-readme]

## Streaming design

- CUDA graphs are unchanged in streaming mode: predictor and talker graphs replay per step, codec-ID chunks are yielded every `chunk_size` steps, and each chunk is decoded with a sliding window plus 25-frame left context matching the upstream codec `chunked_decode` pattern to avoid boundary artifacts (**Reported**).[^faster-qwen3-tts-readme]
- Python streaming methods are pull-based generators; blocking after each yielded chunk prevents generation/playback overlap, so realtime local playback needs a queue-backed player such as `StreamPlayer` (**Reported**).[^faster-qwen3-tts-readme]
- Chunk-size tradeoff on Jetson AGX Orin 0.6B (TTFA, RTF, audio per chunk): 1 → 240 ms / 0.750 / 83 ms; 2 → 266 ms / 1.042 / 167 ms; 4 → 362 ms / 1.251 / 333 ms; 8 → 556 ms / 1.384 / 667 ms; 12 → 753 ms / 1.449 / 1000 ms; non-streaming RTF 1.57. Smaller chunks lower latency at higher decode overhead; `chunk_size=2` is the smallest that stays real-time on Jetson (**Reported**).[^faster-qwen3-tts-readme]
- Model modes are effectively the same speed with first-clone prefill cached (0.6B, `chunk_size=8` example: VoiceClone xvec 152 ms TTFA / 5.470 RTF, VoiceClone full ICL 149 ms / 5.497, CustomVoice 148 ms / 5.537); reproduce with `benchmarks/compare_modes.py` (**Reported**).[^faster-qwen3-tts-readme]

## Voice-cloning quality controls

- `generate_voice_clone(xvec_only)`: `True` is x-vector embedding only (shorter prefill, clean language switching, no `ref_text` needed); `False` default matches upstream ICL with full reference audio in context (requires accurate `ref_text`, may start with a brief continuation artifact) (**Reported**).[^faster-qwen3-tts-readme]
- ICL decoder context: the 12 Hz codec's causal `chunked_decode` prepends reference-audio codec tokens before decoding and trims the reference portion, so the decoder does not start cold in the wrong voice; handled automatically (**Reported**).[^faster-qwen3-tts-readme]
- `non_streaming_mode=None` sentinel preserves upstream defaults per method: `generate_voice_clone` and its streaming variant resolve `None` to `False` (step-by-step text feeding), while CustomVoice and VoiceDesign methods resolve `None` to `True`; the GGML backend has no qwentts.cpp ABI switch for step-by-step feeding, so `non_streaming_mode=False` warns and uses the native prompt layout (**Reported**).[^faster-qwen3-tts-readme]
- Text-feeding performance impact is negligible in the reported RTX 4090 1.7B ICL `chunk_size=8` test: TTFA unchanged (~159 ms), RTF 4.87 vs 4.85 (**Reported**).[^faster-qwen3-tts-readme]
- `instruct` on Base voice cloning is experimental with `xvec_only=True`; instruction-following is described as more predictable in ICL mode (**Reported**).[^faster-qwen3-tts-readme]
- ICL phoneme-bleed fix is on by default: 0.5 s of silence is appended to the reference audio before encoding so a mid-word cutoff does not condition the first generated token; `append_silence=False` restores exact upstream behavior (**Reported**).[^faster-qwen3-tts-readme]

## Performance (as reported)

Benchmarks include tokenization plus inference; RTF above 1.0 is faster than real-time and TTFA is time to first playable chunk at `chunk_size=8`. All figures below are source assertions without in-wiki reproduction (**Reported**).[^faster-qwen3-tts-readme]

### 0.6B model

| GPU | Baseline RTF | Baseline TTFA | CUDA Graphs RTF | CUDA Graphs TTFA | Speedup |
|---|---|---|---|---|---|
| Jetson AGX Orin 64GB | 0.179 | 3,641 ms | 1.307 | 597 ms | 7.3x / 6.1x |
| DGX Spark (GB10) | 1.17 | 567 ms | 2.56 | 280 ms | 2.2x / 2.0x |
| RTX 4090 | 0.82 | 800 ms | 4.78 | 156 ms | 5.8x / 5.1x |
| RTX 4060 (Windows) | 0.23 | 2,697 ms | 2.26 | 413 ms | 9.8x / 6.5x |
| H100 80GB HBM3 | 0.435 | 1,474 ms | 3.884 | 228 ms | 8.9x / 6.5x |
| Tesla T4 16GB | 0.467 | 1,671 ms | 1.068 | 901 ms | 2.3x / 1.9x |

### 1.7B model

| GPU | Baseline RTF | Baseline TTFA | CUDA Graphs RTF | CUDA Graphs TTFA | Speedup |
|---|---|---|---|---|---|
| Jetson AGX Orin 64GB | 0.183 | 3,573 ms | 1.089 | 693 ms | 6.0x / 5.2x |
| DGX Spark (GB10) | 1.01 | 661 ms | 1.87 | 400 ms | 1.9x / 1.7x |
| RTX 4090 | 0.82 | 850 ms | 4.22 | 174 ms | 5.1x / 4.9x |
| RTX 4060 (Windows) | 0.23 | 2,905 ms | 1.83 | 460 ms | 7.9x / 6.3x |
| H100 80GB HBM3 | 0.439 | 1,525 ms | 3.304 | 241 ms | 7.5x / 6.3x |
| Tesla T4 16GB | 0.453 | 1,811 ms | 0.925 | 1,096 ms | 2.0x / 1.7x |

- Baselines are streaming TTFA from the community `Qwen3-TTS-streaming` fork or the dynamic-cache parity streaming path where available; official `Qwen3-TTS` has no streaming, so a non-streaming baseline would be time-to-full-audio. Both sides include text tokenization; speedup is throughput / TTFA improvement. The streaming fork's extra `torch.compile` speedups could not be reproduced on Jetson-class devices without `torch.compile` (**Reported**).[^faster-qwen3-tts-readme]
- GPU note: RTX 4090 (2.5 GHz clocks) beats H100 (1.8 GHz) on single-stream work; H100's lower single-stream baseline reflects batch-oriented design (**Reported**).[^faster-qwen3-tts-readme]
- Per-component Jetson AGX Orin 0.6B breakdown per step: Talker (28 layers) 75 ms → 12 ms; Predictor (15 steps) 190 ms → 26 ms; overhead 65 ms → 16 ms; total 330 ms → 54 ms (**Reported**).[^faster-qwen3-tts-readme]
- Benchmark from source with `./setup.sh` plus `./benchmark.sh` (Linux/macOS/WSL, needs `uv`) or `setup_windows.bat` plus `benchmark_windows.bat` (Windows, with `0.6B`/`1.7B`/`both` selectors); results land in `bench_results_<GPU_NAME>.json` with `sample_0.6B.wav` / `sample_1.7B.wav` (**Reported**).[^faster-qwen3-tts-readme]

## Mechanism

Qwen3-TTS runs two autoregressive transformers per decode step: a 28-layer Talker generating the first codebook token from text and a 5-layer Code Predictor generating 15 more codebook tokens; a single step otherwise costs ~500 small CUDA kernel launches with Python overhead dominating, so the GPU waits more than it computes. The fast path pre-allocates fixed-size static KV-cache tensors, reuses the model's native SDPA plus RoPE attention layers, captures predictor and talker graphs with `torch.cuda.CUDAGraph`, and handles variable-length KV inside fixed buffers with a padded attention mask (**Reported**).[^faster-qwen3-tts-readme]

## Parity and validation

- Two-layer parity claim: fast static-cache plus CUDA-graph streaming and non-streaming share one decode core and match upstream over the initial window where artifacts are most audible (prefix parity enforced deterministically in tests); test-only dynamic-cache parity mode calls `talker.generate(...)` with no graphs to prove exact token-level equality for all model types (**Reported**).[^faster-qwen3-tts-readme]
- Static vs dynamic divergence is attributed to kernel selection, not math: fixed max-length KV plus explicit mask often picks a different SDPA kernel than short-K/V mask-free `is_causal=True` dynamic cache, and BF16/TF32 reduction-order differences break bit-exactness (**Reported**).[^faster-qwen3-tts-readme]
- Parity streaming is intentionally slow (reported RTX 4090 ~0.77 s TTFA at `chunk_size=8`, ~1.17 s at `chunk_size=12`, vs ~0.16–0.18 s in the CUDA-graph path) and is for validation only (**Reported**).[^faster-qwen3-tts-readme]
- Tests in `tests/test_e2e_parity.py` cover voice-clone x-vector prefix parity, streaming vs non-streaming fast-path parity, and full equality in parity mode for CustomVoice, VoiceDesign, and ICL clone; model IDs are overridable via `QWEN_TTS_MODEL`, `QWEN_TTS_CUSTOM_MODEL`, `QWEN_TTS_VOICE_DESIGN_MODEL` (**Reported**).[^faster-qwen3-tts-readme]
- Quality samples are side-by-side WAV pairs under `samples/parity/` (1.7B, ~14 s cap, 2 voices × 2 prompts × static/dynamic, CustomVoice aiden/serena plus ICL refs) and `samples/non_streaming_mode/` (1.7B ICL, 3 refs × 2 prompts × nsm false/true), described but not auditioned in this wiki (**Reported**).[^faster-qwen3-tts-readme]

## Production pattern: precomputed speaker embeddings

- Extract once (`python examples/extract_speaker.py --ref_audio voice.wav --output speaker.pt`, ~10 s), then synthesize with `python examples/generate_with_embedding.py --speaker speaker.pt --text ... --language ... --output ...` (**Reported**).[^faster-qwen3-tts-readme]
- The embedding is a 4 KB file (2048-dim bf16 vector); in `x_vector_only` mode there is no accent bleed, prefill drops to ~10 tokens vs ~80+ in full ICL, and no reference audio is needed at runtime (**Reported**).[^faster-qwen3-tts-readme]
- Public APIs accept `voice_clone_prompt` as either the raw `prompt_items` list from `create_voice_clone_prompt(ref_audio, ref_text, x_vector_only_mode=True)` or the compact dict from `_prompt_items_to_voice_clone_prompt(...)`; a `ref_spk_embedding`-only dict plus saved `speaker.pt` rebuilds the compact form. When `voice_clone_prompt` is given, `ref_audio` extraction is skipped and `ref_text` is ignored for x-vector-only prompts; ICL precomputed prompts need `x_vector_only_mode=[False]`, `icl_mode=[True]`, non-`None` `ref_code`, and populated `ref_text` (**Reported**).[^faster-qwen3-tts-readme]

## Relationships

- Depends on [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md): the 0.6B CustomVoice checkpoint is one of the accelerated model targets; this wrapper supplies the CUDA-graph/GGML streaming runtime while that concept covers the checkpoint itself (**Synthesis**).[^faster-qwen3-tts-readme]
- Depends on [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md): the 1.7B CustomVoice checkpoint is the primary benchmark and CustomVoice CLI target here; checkpoint capabilities stay in that concept (**Synthesis**).[^faster-qwen3-tts-readme]
- Uses [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md): the 12.5 Hz 16-codebook codec whose `chunked_decode` sliding-window pattern this wrapper reuses for streaming chunk decode and ICL reference-context handling (**Synthesis**).[^faster-qwen3-tts-readme]
- Depends on [Qwen3-TTS-12Hz-0.6B-Base](qwen3-tts-12hz-0.6b-base.md): the cloning checkpoint is another accelerated target (`from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-Base")` with `generate_voice_clone`/`generate_voice_clone_streaming`); checkpoint capability and license stay in that concept (**Synthesis**).[^faster-qwen3-tts-readme]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no RTF, TTFA, parity, or quality claim reproduced (**Synthesis**).[^faster-qwen3-tts-readme]
- Linked but unfetched and absent from `raw/`: `docs/ggml-backend.md`, `examples/audio.py`, `examples/streaming_playback.py`, `examples/extract_speaker.py`, `examples/generate_with_embedding.py`, `examples/openai_server.py`, `demo/server.py`, `benchmarks/compare_modes.py`, `tests/test_e2e_parity.py`, `setup.sh`/`benchmark.sh` and Windows `.bat` scripts, `qwentts.cpp`/`qwentts-cpp-python` packages and Hugging Face wheelhouse, PyPI `faster-qwen3-tts`/`qwen-tts-hf` distributions, and `samples/parity/` plus `samples/non_streaming_mode/` WAV audio (not auditioned) and architecture/code references (**Synthesis**).[^faster-qwen3-tts-readme]
- All install, compatibility, latency, benchmark, and quality figures are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^faster-qwen3-tts-readme]
- No sensitive values were found in the source; CLI/Python examples use placeholder audio paths and a public-domain-style philosophical reference sentence (**Synthesis**).[^faster-qwen3-tts-readme]

[^faster-qwen3-tts-readme]: [Faster Qwen3-TTS README](../raw/faster-qwen3-tts.md) — locators: title plus lead paragraph (Torch `torch.cuda.CUDAGraph`, GGML CUDA/Metal); `Install` section (`pip install faster-qwen3-tts`, Python 3.10+/Torch 2.5.1+, `qwen-tts-hf` note, `torch<=2.5.0` capture note, Blackwell `cu128`/2.7+ note, T4/A10G `cu124` fence, `nvidia-smi` guidance); `Experimental GGML backend` section (`--backend` selection, Metal/Intel-Mac notes, `[ggml]` extra, `qwentts-cpp-python>=0.5.0`, `cu128`/`cu130` wheelhouse fences, `docs/ggml-backend.md` link, `log_level`/`--verbose`/`qwentts_log_level`, `.spk`/`.rvq` cache fence); `Quick Start/Python` and `CLI` fences (`from_pretrained`, `generate_voice_clone_streaming` with `chunk_size=8`, `generate_voice_clone`, `warmup`, `StreamPlayer`, `clone`/`custom --list-speakers`/`design`/`--streaming`/`serve`, `sounddevice` note); `Demo UI` and `OpenAI-compatible API server` fences (`demo/server.py`, `examples/openai_server.py`, `/v1/audio/speech`, `--voices`, `pydub`); `Results` 0.6B/1.7B benchmark tables plus baseline/GPU-architecture notes; `Benchmark your hardware` fences (`./setup.sh`, `./benchmark.sh`, `setup_windows.bat`, `bench_results_<GPU_NAME>.json`); `Streaming` chunk-size table, model-seed table with `benchmarks/compare_modes.py`, `How streaming works` paragraphs (25-frame context, pull-based generators); `Voice Cloning Quality` tables and paragraphs (`xvec_only`, `chunked_decode`, `non_streaming_mode` defaults and RTX 4090 figures, `instruct`, `append_silence`); `Quality Samples` `samples/parity` and `samples/non_streaming_mode` audio-tag lists; `Parity` paragraphs plus `tests/test_e2e_parity.py` list and `QWEN_TTS_*` env fences; `How It Works` paragraphs plus Jetson per-component table (Talker 28 layers, Predictor 5 layers/15 steps, ~500 launches); `Voice Cloning with Precomputed Speaker Embeddings` fences (`extract_speaker.py`, `generate_with_embedding.py`, 4 KB/2048-dim bf16, `prompt_items`/`voice_clone_prompt` dict); `License` (MIT) and `Acknowledgments` links.
