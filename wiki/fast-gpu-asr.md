---
type: Concept
title: Fast GPU ASR
description: Batched offline TensorRT inference library for Zipformer and Parakeet ASR on NVIDIA GPUs with GPU beam search, word timestamps, and published A100/H200/B300 RTFx-plus-WER benchmarks.
tags: [stt, asr, tensorrt, batch-inference, gpu, parakeet, zipformer]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T14:09:07Z }
stale_after: 2027-10-06
sources:
  - id: fast-gpu-asr-readme
    resource: ../raw/fast-gpu-asr.md
    kind: documentation
    title: Fast GPU ASR README
---

Fast GPU ASR by SoundsGoodAI is a batched offline speech-recognition library for NVIDIA GPUs that takes raw audio to text plus word timestamps through one Python API, covering Zipformer Transducer/CTC and Parakeet TDT/CTC with TensorRT engines, native CUDA plugins, and GPU beam search, requiring no NeMo or k2 installation (**Reported**).[^fast-gpu-asr-readme]

## Scope and positioning

- Offline batch inference library, not a streaming engine: engines have fixed batch capacity with dynamic audio length inside their exported profiles, so a smaller batch size or separate duration profiles is the stated lever when memory or latency matters more than aggregate throughput (**Reported**).[^fast-gpu-asr-readme]
- Checkpoints must match the exporters' supported architectures and checkpoint/configuration formats; compatible fine-tuned models can be exported, not just the example checkpoints below (**Reported**).[^fast-gpu-asr-readme]

## Supported models and decoder modes

| Family | Example checkpoints | Decoder modes |
|---|---|---|
| Zipformer Transducer | CR-CTC Transducer XL 290M, Transducer XL 290M | Modified beam search / beam one |
| Zipformer CTC | CR-CTC Transducer XL 290M (CTC head) | CTC greedy |
| Parakeet TDT | V3 0.6B, V2 0.6B | Modified beam search / beam one |
| Parakeet CTC | 0.6B, 1.1B | CTC greedy |

- The benchmark campaign uses transducer decoding (beam 6), not CTC (**Reported**).[^fast-gpu-asr-readme]
- Precision support is FP32, FP16, and BF16; BF16 requires Ampere or newer (**Reported**).[^fast-gpu-asr-readme]

## Requirements and installation

- Requires Linux x86-64, Python 3.12–3.14, a Turing (SM75) or newer NVIDIA GPU, and NVIDIA driver 580 or newer (the CUDA 13 family minimum); PTX JIT or newer CUDA features may need a newer driver; the package uses CUDA 13 and TensorRT, and the wheel bundles all nine TensorRT plugin libraries with no local compilation or TensorRT development headers needed (**Reported**).[^fast-gpu-asr-readme]
- Install fence uses a fresh environment with CPU-only PyTorch first, because TensorRT and CuPy provide GPU inference while PyTorch needs no CUDA support, and package metadata cannot select PyTorch's CPU index automatically: `pip install torch --index-url https://download.pytorch.org/whl/cpu` then `pip install fast-gpu-asr` (**Reported**).[^fast-gpu-asr-readme]

## Export workflow

- Example export profile is FP16 with batch size 8 and a 0.1 / 8 / 40-second minimum/typical/maximum audio-duration profile; transducer examples use beam 6 and CTC uses greedy decoding; checkpoints download from each model's `main` branch and are not bundled (**Reported**).[^fast-gpu-asr-readme]
- Exporter commands: `fast-gpu-asr-export-zipformer` (`--decoder-type transducer_modified_beam_search --beam 6` or `ctc_greedy_search --beam 1`) and `fast-gpu-asr-export-parakeet` with `--encoder-precision`/`--decoder-precision` (CTC omits `--decoder-precision`: it needs no transducer decoder engine or predictor table) and `--optimization-level 5` in the examples (**Reported**).[^fast-gpu-asr-readme]
- Build engines on the GPU used for inference with the same TensorRT/plugin stack; export deletes and recreates its output directory, so checkpoints and unrelated files must stay outside it; engine building takes time and extra host/GPU memory for tactic selection (**Reported**).[^fast-gpu-asr-readme]

## Python API

- Input is one or more nonempty 1D NumPy `float32` waveforms as a list, normalized to `[-1, 1]` at the bundle's sample rate; partial batches work with short clips padded internally; callers must stay within the exported batch and duration limits and resample or split audio beforehand; GPU selection is `ASR(..., device_id=0)` (**Reported**).[^fast-gpu-asr-readme]
- `ASR("exported/zipformer")` returns `(texts, word_timestamps)` with one transcript and one list of `(word, start, end)` tuples per clip; times are seconds rounded to milliseconds and are encoder-frame estimates, not forced alignments: word intervals extend to the next word boundary or the clip duration (**Reported**).[^fast-gpu-asr-readme]
- The worked example reads mono PCM16 WAV files at 16 kHz of at most 40 seconds (the export `max-audio-seconds`) and prints per-word `start–end` spans (**Reported**).[^fast-gpu-asr-readme]
- Direct encoder/decoder use requires a `cp.cuda.Device`, a CUDA stream, and serialized calls; encoder outputs reuse GPU buffers, so callers use the same stream or synchronize across streams and copy outputs worth keeping after the next call; each `ASR` instance reuses buffers and serializes calls with a lock, and model-bundle validation defaults to `validate=True` (**Reported**).[^fast-gpu-asr-readme]

## Benchmarks (FP16, decoder beam 6)

- Protocol: a reproduction of the Open ASR Leaderboard English evaluation with its datasets and WER scorer, reporting RTFx (total audio duration over total inference time: throughput, not request latency) and WER; each configuration processes 157.8 hours of audio across seven English datasets; full results, CSV, hardware, protocol, and plot-reproduction notes are linked, not compiled (**Reported**).[^fast-gpu-asr-readme]

| GPU | Model | Batch 1 RTFx | Batch 256 RTFx | Batch 1 suite time | Batch 256 suite time | Batch 1 mean WER | Batch 256 mean WER |
|---|---|---:|---:|---:|---:|---:|---:|
| A100 | Zipformer CR-CTC Transducer | 589.0 | 10,298.5 | 964.35 s | 55.15 s | 5.254% | 5.259% |
| A100 | Parakeet V3 TDT | 560.8 | 6,482.0 | 1012.79 s | 87.62 s | 4.824% | 4.816% |
| H200 | Zipformer CR-CTC Transducer | 578.2 | 18,100.2 | 982.29 s | 31.38 s | 5.254% | 5.260% |
| H200 | Parakeet V3 TDT | 593.6 | 12,352.7 | 956.80 s | 45.98 s | 4.803% | 4.804% |
| B300 | Zipformer CR-CTC Transducer | 879.8 | 25,108.6 | 645.57 s | 22.62 s | 5.257% | 5.261% |
| B300 | Parakeet V3 TDT | 897.5 | 19,398.7 | 632.82 s | 29.28 s | 4.814% | 4.810% |

- Key observations stated in the source: batching dominates (B300 FP16 batch 256 vs batch 1 is 28.5x for Zipformer and 21.6x for Parakeet V3 TDT); gains taper (128→256 adds +25.1% Zipformer, +23.0% Parakeet); BF16 is supported and slightly faster than FP16 at B300/batch 256 for both models; FP16 vs FP32 at B300/batch 128 is +22.2% Zipformer and +58.5% Parakeet; mean WER is consistent across precisions and batches (B300 span 0.014 pp Zipformer, 0.034 pp Parakeet), with WER recorded per configuration because precision can marginally change outputs (**Reported**).[^fast-gpu-asr-readme]

## Implementation

- One TensorRT engine turns raw waveforms into decoder-ready outputs with features and activations kept on GPU: a GPU-native audio frontend (batched cuFFT, cuBLAS mel projection, custom framing/windowing/normalization kernels, no CPU feature stage or upload), fused layout-aware kernels across the nine native plugin libraries (e.g. relative-position alignment plus masking plus softmax; depthwise convolution plus activation; attention reading projection layouts directly; dedicated Zipformer resampling/output kernels), export-time Parakeet optimizations (combined QKV projection, evaluation-mode BatchNorm folded into convolutions, constant feed-forward scaling absorbed into output projections), target-GPU tactic selection at engine build, and pinned host staging with async transfers, reusable buffers/workspaces, plus CUDA-graph replay for same-shape consecutive batches (**Reported**).[^fast-gpu-asr-readme]
- Both transducer decoders keep scores, candidate selection, and token histories on GPU with backpointers instead of copied histories, reusable buffers, CUDA graphs, and length-normalized log-probability final selection (**Reported**).[^fast-gpu-asr-readme]
- Zipformer RNN-T follows k2/Icefall's `modified_beam_search` (at most one nonblank token per encoder frame) with three stated differences: merge-first-then-prune (log-sum-exp score combination before retaining the top-`beam` unique hypotheses, so duplicates cannot waste beam slots); precomputed predictor (GPU table lookups for contexts up to two tokens replace per-frame stateless predictor evaluation, only the joiner runs per step); specialized CUDA kernels for beam/vocabulary/context size with prefix checks plus exact history comparisons against hash collisions (**Reported**).[^fast-gpu-asr-readme]
- Parakeet TDT follows NeMo's batched `ModifiedALSDBatchedTDTComputer` (batched hypotheses, GPU-resident LSTM states, reusable buffers, CUDA graphs) with four stated differences: merge-before-pruning on exact token histories, encoder positions, and zero-duration emission counts; full duration-alternative search (nonblanks across vocabulary × all configured durations plus blanks over every positive duration, with exact-history grouping avoiding full materialization); different symbol-limit advance (one frame after the capped zero-duration token, no blank transition, where NeMo forces a blank); TensorRT predictor/joiner plus CuPy-launched search/state kernels replaying fixed search chunks with periodic host completion checks versus NeMo's PyTorch full conditional CUDA-graph loop (**Reported**).[^fast-gpu-asr-readme]
- The source states these search changes can affect transcripts and do not guarantee better WER or identical upstream results, and frames them as implementation comparisons, not matched speedup measurements against upstream decoders (**Reported**).[^fast-gpu-asr-readme]

## Decoder settings and precision behavior

- `transducer_modified_beam_search` uses the exported beam width; `transducer_greedy_search` forces `beam=1` through the same modified beam-search implementation rather than a separate decoder; `ctc_greedy_search` needs a CTC head and uses neither a transducer decoder engine nor a predictor table (**Reported**).[^fast-gpu-asr-readme]
- Both exporters accept `--blank-penalty` (default `0.0`), subtracted from blank log probabilities after normalization; positive values discourage blanks in every mode including beam one; k2/Icefall's reference applies its penalty before softmax, so equal nonzero settings are not equivalent; mode, beam, and penalty persist in `model_config.yaml` (**Reported**).[^fast-gpu-asr-readme]
- `--encoder-precision` and `--decoder-precision` default to `fp32`; waveform frontends and CTC heads stay FP32 in both models, and FP32 permits TF32 plus eligible reduced-math plugin tactics; the source advises checking WER alongside throughput when changing precision (**Reported**).[^fast-gpu-asr-readme]
- Zipformer precision: final encoder projection and transducer log probabilities stay FP32; BF16 exports use FP16 for the first subsampling convolution. Parakeet precision: with input scaling enabled, FP16 exports rescale the first block's output weights, biases, and LayerNorm epsilons to keep residuals in range while retaining FP16 subsampling/Conformer layers; FP32/BF16 exports instead fold the scale into the subsampling projection's weights and bias (**Reported**).[^fast-gpu-asr-readme]
- Export keeps intermediate ONNX files only with `--debug`; otherwise successful exports remove them (**Reported**).[^fast-gpu-asr-readme]

## Build, tests, packaging, and reproduction

- Source build needs a CUDA-compatible C++20 host compiler and TensorRT development headers (`NvInfer.h`) matching `uv.lock` (`CPLUS_INCLUDE_PATH` when outside compiler search paths); fences are `uv sync --frozen --extra dev` and `uv run --frozen python -m fast_gpu_asr.tensorrt_plugins.build`, with `uv` supplying `nvcc`, CUDA headers/libraries, TensorRT, and CPU-only PyTorch; exporter commands then run prefixed with `uv run --frozen` (**Reported**).[^fast-gpu-asr-readme]
- Native targets are `sm_75`, `sm_80`, `sm_86`, `sm_87`, `sm_88`, `sm_89`, `sm_90`, `sm_100`, `sm_103`, `sm_110`, `sm_120`, and `sm_121`, plus a `compute_80` PTX fallback; callers verify execution and memory on their GPU (**Reported**).[^fast-gpu-asr-readme]
- Test fences are `pytest`, `ruff check .`, `ruff format --check .`, and `python src/fast_gpu_asr/decoder/lint_gpu_kernels.py --check`; GPU tests skip without CUDA and BF16 tests need SM80+; tests check decoder behavior and numerical tolerances, not identical transcripts across precisions; formatting limits are 88 columns Python and 100 CUDA/C++ (**Reported**).[^fast-gpu-asr-readme]
- Wheel fence is `scripts/build_wheel.sh` producing a repaired `manylinux_2_27_x86_64` wheel in `dist/`, additionally requiring `binutils` and `patchelf`; CUDA and TensorRT stay external; source distributions are unsupported; CI runs Python 3.12–3.14 CPU checks on `main` pushes and pull requests, with opt-in native and wheel smoke tests on the separately billed `gpu-t4` runner (SM80-only cases skip there) (**Reported**).[^fast-gpu-asr-readme]
- Measurement reproduction: the CSV regenerates the tables and plots on a CPU-only host; collecting new measurements needs the datasets, checkpoints, and a target GPU; the published campaign pins its source and scorer revisions; plot rebuild is `uv sync --frozen --extra benchmark`, `plotly_get_chrome -y` (skipped with existing Chrome/Chromium or `BROWSER_PATH`), and `python docs/benchmarks/render.py`, regenerating two SVGs, `results.md`, and only the marked performance block in the README (**Reported**).[^fast-gpu-asr-readme]
- Code license is Apache-2.0; model weights and datasets keep their own licenses (no commercial rights to noncommercial checkpoints via the code license); built on k2, NeMo, NVIDIA TensorRT/CUDA, with component attribution in `NOTICE` (**Reported**).[^fast-gpu-asr-readme]

## Relationships

- Serves [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): this library's benchmarked Parakeet path uses the V3 TDT 0.6B weights (beam-6 TDT search) as its offline batch alternative to that page's NeMo/Transformers/GGUF routes; consult that page for multilingual coverage, greedy-decoding WER grids, and long-audio limits (**Synthesis**).[^fast-gpu-asr-readme]
- Serves [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md) and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md): both CTC checkpoints are named as supported export inputs with GPU greedy decoding through a single encoder engine with integrated CTC head (**Synthesis**).[^fast-gpu-asr-readme]
- Related to [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md) and [Parakeet RNNT 1.1B](parakeet-rnnt-1.1b.md): same Parakeet model family served through a different (TensorRT plus custom-kernel TDT/RNN-T beam search) runtime; compare per-model cards for training and accuracy context (**Synthesis**).[^fast-gpu-asr-readme]
- Related to [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md): V2 is a named supported TDT export input alongside V3 (**Synthesis**).[^fast-gpu-asr-readme]
- Contrasts [Faster-Whisper](faster-whisper.md): both are offline batch-oriented ASR runtimes with word timestamps, but Faster-Whisper serves Whisper-family weights on CTranslate2 (CPU or GPU, INT8-capable) while this library serves Zipformer/Parakeet weights on TensorRT (NVIDIA GPU only, FP32/FP16/BF16); compare their benchmark tables when choosing a batch-transcription backend (**Synthesis**).[^fast-gpu-asr-readme]
- Contrasts [Parakeet ASR Server](parakeet-asr-server.md): that page deploys Parakeet TDT 0.6B as a self-hosted Go plus ONNX Runtime service behind a Whisper-compatible REST/SSE API, versus this page's Python-library TensorRT batch engine; prefer that page for service operations and this page for maximum GPU batch throughput (**Synthesis**).[^fast-gpu-asr-readme]
- Cataloged in [ASR/STT Model Survey](asr-stt-model-survey.md): the survey's serving-runtimes row records this engine's model coverage and headline B300 figures; consult it for cross-runtime comparison (**Synthesis**).[^fast-gpu-asr-readme]

## Coverage and limits

- Source inspected statically only; no `pip install`, engine export, transcription, or benchmark was executed, and no RTFx, suite-time, or WER figure was reproduced (**Synthesis**).[^fast-gpu-asr-readme]
- Referenced but unfetched and absent from `raw/`: the fast-gpu-asr package and wheel, TensorRT/plugin/CUDA stacks, all checkpoints (`soundsgoodai/Zipformer-cr-ctc-transducer-XL-290M`, `soundsgoodai/Zipformer-transducer-XL-290M`, `nvidia/parakeet-tdt-0.6b-v3/v2`, `nvidia/parakeet-ctc-0.6b/1.1b`), the seven Open ASR Leaderboard English datasets and scorer, `docs/benchmarks/results.md`, `methodology.md`, `measurements.csv`, rendered SVGs, `model_config.yaml`, `NOTICE`, CI workflow, and sample WAV files; all install, export, transcribe, build, test, and plot fences above are transcribed, not executed (**Synthesis**).[^fast-gpu-asr-readme]
- All throughput, accuracy, compatibility, and implementation-difference claims are source assertions without independent verification in this wiki; benchmark and compatibility figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^fast-gpu-asr-readme]

[^fast-gpu-asr-readme]: [Fast GPU ASR README](../raw/fast-gpu-asr.md) — locators: header (SoundsGoodAI, Zipformer plus Parakeet, batched offline, TensorRT engines, native CUDA plugins, GPU beam search, no NeMo/k2); `Batched speech recognition at up to 25,000 RTFx on B300` (RTFx definition, 157.8-hour seven-English-dataset suite, FP16 beam-6 A100/H200/B300 table with RTFx/suite-time/mean-WER, Open ASR Leaderboard reproduction with datasets plus scorer, methodology link); `Key Observations` (28.5x/21.6x batching, +25.1%/+23.0% taper, BF16 note, +22.2%/+58.5% FP16-vs-FP32, 0.014/0.034 pp WER spans, results plus CSV links); `Quick Start` (Linux x86-64, Python 3.12–3.14, SM75+, driver 580+, CUDA 13, nine plugin libraries; CPU-torch-first install fences; Parakeet TDT/CTC plus Zipformer Transducer/CTC families; FP16 batch-8 0.1/8/40 s profile, beam 6 vs greedy, `main`-branch checkpoints not bundled, target-GPU builds, output-dir deletion); `Zipformer CR-CTC Transducer/CTC`, `Parakeet V3/CTC` (checkpoint URLs, `fast-gpu-asr-export-zipformer/parakeet` fences, `--decoder-precision` omission for CTC, benchmark-uses-transducer note); `Transcribe` (`ASR` fence with mono PCM16 16 kHz ≤40 s WAV loading, float32 `[-1, 1]` inputs, partial batches, batch/duration limits, `(texts, word_timestamps)` millisecond encoder-frame estimates, `device_id`); `Models and Inference Precision` (family/checkpoint/decoder table, FP32/FP16/BF16 with BF16 Ampere+, offline-batch fixed-capacity guidance); `Implementation Details` (single-engine GPU frontend, nine plugins, export-time QKV/BatchNorm/scaling opts, tactic selection, CUDA-graph replay; GPU beam search with backpointers and length-normalized selection; Zipformer merge-first/precompute/specialize vs k2/Icefall; Parakeet merge-before-prune/duration-alternatives/symbol-limit/TRT-kernel differences vs NeMo; transcripts-may-differ disclaimer); `Decoder Settings` (`beam=1` greedy reuse, `--blank-penalty` 0.0 post-normalization vs k2 pre-softmax, `model_config.yaml`); `Export and Runtime Notes` (fp32 defaults, FP32 frontend/CTC heads, TF32 note, Zipformer/Parakeet precision details, `--debug` ONNX, lock-serialized `ASR` with `validate=True`); `Build From Source` (C++20, `NvInfer.h` via `uv.lock`/`CPLUS_INCLUDE_PATH`, `uv sync` plus plugin-build fences, `sm_*` targets plus `compute_80` PTX); `Tests and Packaging` (`pytest`, `ruff`, `lint_gpu_kernels.py --check`, CUDA/SM80 skips, tolerance-not-identity tests, 88/100-column limits, `build_wheel.sh` manylinux fence, CI CPU plus `gpu-t4` manual GPU); `Reproduce the Measurements` (CSV CPU regeneration, dataset/checkpoint/GPU needs, pinned revisions, `render.py` plus `plotly_get_chrome` fences); `License and Acknowledgments` (Apache-2.0 code, weights/datasets own licenses, k2/NeMo/TRT/CUDA, `NOTICE`).
