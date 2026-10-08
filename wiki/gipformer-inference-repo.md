---
type: Concept
title: Gipformer Inference Repository
description: MIT-licensed G-Group AI Lab scripts for running Gipformer Vietnamese Zipformer-RNNT ASR via sherpa-onnx (offline, non-streaming recognizer, fp32/int8) or icefall/k2 PyTorch, with CLI defaults, dependencies, and doc-versus-code discrepancies.
tags: [stt, asr, vietnamese, zipformer, rnnt, onnx, sherpa-onnx, icefall, edge]
status: stable
created: 2026-10-08
generated: { by: llm-wiki-agent/1, at: 2026-10-08T12:00:00Z }
stale_after: 2027-10-08
sources:
  - id: gipformer-repo
    resource: ../raw/gipformer/README.md
    scope: ../raw/gipformer/
    kind: code
    revision: 0cac5b183d2e1a9e3429ff69080e09cc62ebdf9b
    title: ggroup-ai-lab/gipformer (GitHub repository snapshot)
---

The `ggroup-ai-lab/gipformer` repository is a scripts-only package (no installable module) that runs the 68M-parameter Gipformer Vietnamese ASR models, [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md) (default) and [Gipformer 68M RNNT](gipformer-68m-rnnt.md), through two paths: ONNX Runtime via sherpa-onnx (recommended, cross-platform) and PyTorch via icefall/k2 (Linux + CUDA, research). Both fetch weights from Hugging Face at run time; no weights are in the repo (**Observed**).[^gipformer-repo]

## ONNX path (`infer_onnx.py`)

- Uses `sherpa_onnx.OfflineRecognizer.from_transducer(...)` with encoder/decoder/joiner/tokens, 16 kHz, 80-dim features. The whole file is passed through `accept_waveform` then `decode_streams`, so this path is **offline (non-streaming) decoding**: the repo ships no `OnlineRecognizer`, chunking, or endpointing code (**Observed**; `infer_onnx.py::create_recognizer`, `transcribe`).[^gipformer-repo]
- Model files per precision: `encoder/decoder/joiner.onnx` (fp32) or `*.int8.onnx`, plus `tokens.txt`; `--model-dir` loads locally, else `hf_hub_download` from `g-group-ai-lab/gipformer-68M-rnnt` (`--version 1`) or `gipformer1.5-68M-rnnt` (`1.5`, default) (**Observed**; `REPO_IDS`, `ONNX_FILES`).[^gipformer-repo]
- CLI defaults: `--quantize fp32`, `--num-threads 4`, `--decoding-method modified_beam_search` (alternative `greedy_search`). Stereo input is averaged to mono; the sample rate is passed through to sherpa-onnx rather than resampled in the script. The script prints text, wall time, audio duration, and RTF per file (**Observed**).[^gipformer-repo]
- No RTF, latency, or memory figure is documented in the repo, and no execution was performed here; edge/mobile suitability is README **Reported** only.[^gipformer-repo]

## PyTorch path (`infer_pytorch.py`)

- On first run shallow/sparse-clones `k2-fsa/icefall` (`icefall`, `egs/librispeech/ASR`) into `~/.cache/gipformer/icefall`, then imports its Zipformer `train.get_model`, so the network is fetched from an unpinned upstream at run time; `lhotse` is replaced by an import-hook mock because it is training-only (**Observed**; `setup_icefall`, `_LhotseFinder`).[^gipformer-repo]
- Files: `model.pt`, `bpe.model`, `tokens.txt`. Features: kaldifeat Fbank, 80 bins, `dither=0`, `snip_edges=False`, `high_freq=-400`. Decoding: `modified_beam_search` (beam 4, context size 2) or `greedy_search_batch`; device `auto` picks CUDA if available (**Observed**).[^gipformer-repo]
- The checkpoint is loaded with `torch.load(..., weights_only=False)` and `strict=False`, so unmatched weights do not raise an error and only trusted checkpoints should be loaded (**Observed**, security/robustness note).[^gipformer-repo]
- Pinned optional stack: torch/torchaudio 2.8.0, k2 and kaldifeat CUDA 12.8 wheels, sentencepiece 0.2.1, Linux x86_64 only (`pyproject.toml`, `[project.optional-dependencies].pytorch`).[^gipformer-repo]

## Dependencies and licensing

Core: `huggingface-hub`, `numpy`, `soundfile`, `sherpa-onnx`, and `sherpa-onnx-core` (needed explicitly from sherpa-onnx 1.13, where native `libonnxruntime.so` moved out of the main wheel); Python `>=3.9,<3.14`; managed by `uv` (`uv.lock` is git-ignored, so versions are not locked in the snapshot). README declares MIT and credits k2, icefall, and sherpa-onnx; no LICENSE file was in the snapshot despite the badge link (**Observed**).[^gipformer-repo]

## Benchmark claims

The README repeats the 16-column vendor WER table (private `tele-*` call-center sets plus public sets) with gipformer1.5-68M bolded as best on tele-medium, four domain sets, VietMed, MultiMED, and ViMD; details and caveats are in [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md). The table lists a `zipformer-rnnt` 68M row distinct from `hynt/Zipformer-30M-RNNT-6000h`. Normalization is lowercase, punctuation-stripped, numbers to spoken form (**Reported**; not reproduced).[^gipformer-repo]

## Discrepancies and limits

- `load_model()` has a function default of `quantize="int8"`, but the CLI default is `fp32`, and the README says fp32 is the default invocation and int8 is "smaller & faster" without numbers (**Observed**).[^gipformer-repo]
- README says the models rank "among the smallest" and are "state-of-the-art"; these are promotional claims (**Reported**).

## Relationships

- Resolves part of the open streaming question in [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md): the shipped reference code is offline-only, so it fits a final-pass/batch role in [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md), not a streaming role, unless the user builds streaming on a streaming-trained checkpoint (**Synthesis**; model training mode remains undocumented).
- Uses sherpa-onnx and icefall (k2-fsa) as runtimes.

## Coverage and limits

Inspected statically: `README.md`, `pyproject.toml`, `infer_onnx.py` (242 lines), `infer_pytorch.py` (399 lines), `.gitignore`, git metadata (revision, origin). Excluded: `data/audio1–18.wav` sample clips (binary test inputs, no transcripts in the repo; not decoded) and `.git` internals (hooks, pack files). No code was executed, no weights downloaded, and no benchmark rerun.

[^gipformer-repo]: [Gipformer repository](../raw/gipformer/README.md) at revision `0cac5b1` — `README.md` (Highlights, Benchmark Results, Quick Start, License, Acknowledgments); `infer_onnx.py::load_model, create_recognizer, transcribe, main`; `infer_pytorch.py::setup_icefall, _LhotseFinder, load_model_files, main`; `pyproject.toml` dependencies and `[tool.uv]`.
