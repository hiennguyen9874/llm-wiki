---
type: Concept
title: Parakeet TDT 0.6B V3
description: NVIDIA 600M-parameter multilingual offline FastConformer-TDT ASR model covering 25 European languages with auto language detection, punctuation, timestamps, long-audio support, and published FLEURS/MLS/CoVoST plus Open ASR Leaderboard WER tables.
tags: [stt, asr, multilingual, fastconformer, tdt, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T14:09:07Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-v3-card
    resource: ../raw/parakeet-tdt-0.6b-v3.md
    kind: documentation
    title: Parakeet TDT 0.6B V3 multilingual model card
  - id: parakeet-server-readme
    resource: ../raw/parakeet.md
    kind: documentation
    title: Parakeet ASR server README (achetronic/parakeet)
  - id: fast-gpu-asr-readme
    resource: ../raw/fast-gpu-asr.md
    kind: documentation
    title: Fast GPU ASR README
---

Parakeet TDT 0.6B V3 (`nvidia/parakeet-tdt-0.6b-v3`) is NVIDIA's ~600M-parameter multilingual offline ASR model that auto-detects one of 25 European languages and transcribes 16 kHz mono speech into punctuated, capitalized text with word- and segment-level timestamps, using a FastConformer encoder with a TDT decoder served via NeMo, Transformers, and a NeMo-Speech.cpp GGUF runtime (**Reported**).[^parakeet-v3-card]

## Identity and lineage

- Hugging Face ID `nvidia/parakeet-tdt-0.6b-v3`; extends [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md) from English-only to 25 European languages with no prompting required; release date 08/14/2025; ready for commercial and non-commercial use (**Reported**).[^parakeet-v3-card]
- Supported languages (25): Bulgarian (bg), Croatian (hr), Czech (cs), Danish (da), Dutch (nl), English (en), Estonian (et), Finnish (fi), French (fr), German (de), Greek (el), Hungarian (hu), Italian (it), Latvian (lv), Lithuanian (lt), Maltese (mt), Polish (pl), Portuguese (pt), Romanian (ro), Slovak (sk), Slovenian (sl), Spanish (es), Swedish (sv), Russian (ru), Ukrainian (uk) (**Reported**).[^parakeet-v3-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, 25-language list, tags including `Transducer`, `TDT`, `FastConformer`, `NeMo`, `hf-asr-leaderboard`, training datasets `nvidia/Granary` and `nemo/asr-set-3.0`, license `cc-by-4.0`, and a large per-dataset `model-index` of test WER values (**Observed** by static inspection).[^parakeet-v3-card]
- License CC-BY-4.0; deployment geography global; demo space `huggingface.co/spaces/nvidia/parakeet-tdt-0.6b-v3`; full details deferred to the card's Technical Report (`arXiv:2509.14128`) (**Reported**).[^parakeet-v3-card]

## Architecture and capabilities

- FastConformer encoder with TDT decoder; ~600M parameters; full-attention single pass up to 24 minutes on A100 80GB, or up to 3 hours with local attention (**Reported**).[^parakeet-v3-card]
- Native output features: automatic punctuation and capitalization, accurate word-level and segment-level timestamps (plus char level via NeMo), and long-audio transcription (**Reported**).[^parakeet-v3-card]
- Input: 16 kHz mono audio in `.wav`/`.flac`; output: 1D text string with punctuation and capitalization; NVIDIA GPU acceleration via CUDA stated as the performance path over CPU-only (**Reported**).[^parakeet-v3-card]

## Training data and procedure

- Initialized from a CTC multilingual checkpoint pretrained on the Granary dataset; trained 150,000 steps on 128 A100 GPUs with temperature sampling 0.5 for corpus/language balancing; stage-2 fine-tuning 5,000 steps on 4 A100 GPUs on ~7,500 hours of high-quality human-transcribed NeMo ASR Set 3.0 data (**Reported**).[^parakeet-v3-card]
- Training data: ~10,000 hours human-transcribed NeMo ASR Set 3.0 (LibriSpeech 960 hours, Fisher Corpus, National Speech Corpus Part 1, VCTK, Europarl-ASR, Multilingual LibriSpeech, Mozilla Common Voice v7.0, AMI) plus ~660,000 hours pseudo-labeled Granary data (YTC/YouTube-Commons, MOSEL, YODAS); all transcripts preserve punctuation and capitalization; Granary slated for public release after Interspeech 2025 (**Reported**).[^parakeet-v3-card]
- Unified SentencePiece tokenizer with 8,192 vocabulary built from training transcripts; training used the `speech_to_text_rnnt_bpe.py` example script with the `fastconformer_hybrid_tdt_ctc_bpe.yaml` TDT config (**Reported**).[^parakeet-v3-card]
- Evaluation datasets named: FLEURS, MLS, and CoVoST/CoVoST2 for multilingual; Hugging Face Open ASR Leaderboard sets for English (**Reported**).[^parakeet-v3-card]

## Benchmarks (greedy Transducer WER without external LM)

All numbers below are source assertions for greedy Transducer decoding without an external language model, WER percent with punctuation/capitalization stripped before scoring unless noted; nothing was executed or reproduced for this wiki (**Synthesis**).[^parakeet-v3-card]

- Multilingual averages: FLEURS 11.97%, MLS 7.83%, CoVoST 11.98% (**Reported**):[^parakeet-v3-card]

| Language | FLEURS | MLS | CoVoST |
| --- | --- | --- | --- |
| bg | 12.64 | - | - |
| cs | 11.01 | - | - |
| da | 18.41 | - | - |
| de | 5.04 | - | 4.84 |
| el | 20.70 | - | - |
| en | 4.85 | - | 6.80 |
| es | 3.45 | 4.39 | 3.41 |
| et | 17.73 | - | 22.04 |
| fi | 13.21 | - | - |
| fr | 5.15 | 4.97 | 6.05 |
| hr | 12.46 | - | - |
| hu | 15.72 | - | - |
| it | 3.00 | 10.08 | 3.69 |
| lt | 20.35 | - | - |
| lv | 22.84 | - | 38.36 |
| mt | 20.46 | - | - |
| nl | 7.48 | 12.78 | 6.50 |
| pl | 7.31 | 7.28 | - |
| pt | 4.76 | 7.50 | 3.96 |
| ro | 12.44 | - | - |
| ru | 5.51 | - | 3.00 |
| sk | 8.82 | - | - |
| sl | 24.03 | - | 31.80 |
| sv | 15.08 | - | 20.16 |
| uk | 6.79 | - | 5.10 |

- Evaluation notes: plotted comparison covers 24 supported languages excluding Latvian because `seamless-m4t-v2-large`/`medium` do not support it; Portuguese gaps may partly reflect European-Portuguese training data versus Brazilian-Portuguese benchmarks (**Reported**).[^parakeet-v3-card]
- English Open ASR Leaderboard row, average 6.34% (**Reported**):[^parakeet-v3-card]

| AMI | Earnings-22 | GigaSpeech | LS test-clean | LS test-other | SPGI Speech | TEDLIUM-v3 | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11.31 | 11.42 | 9.59 | 1.93 | 3.59 | 3.97 | 2.75 | 6.14 |

- Frontmatter `model-index` repeats these plus per-language FLEURS/MLS/CoVoST test splits and configs (e.g. FLEURS `bg_bg` 12.64 through `uk_ua` 6.79; MLS spanish 4.39 / french 4.97 / italian 10.08 / dutch 12.78 / polish 7.28 / portuguese 7.50; CoVoST de 4.84 through uk 5.10), each `args.language` set accordingly (**Observed** by static inspection).[^parakeet-v3-card]
- Noise robustness on Open ASR sets with MUSAN music/noise (average WER and card-stated relative change): clean 6.34; SNR 10 → 7.12 (−12.28%); SNR 5 → 8.23 (−29.81%); SNR 0 → 11.66 (−83.97%); SNR −5 → 19.88 (−213.64%), with per-dataset columns as printed in the card (**Reported**).[^parakeet-v3-card]

## Inference and usage

- NeMo-Speech.cpp local runtime: `hf download nvidia/parakeet-tdt-0.6b-v3 parakeet-tdt-0.6b-v3.q8_0.gguf --local-dir models`, then `nemo-speech transcribe audio.wav --model models/parakeet-tdt-0.6b-v3.q8_0.gguf` (**Reported**).[^parakeet-v3-card]
- NeMo Python: install recent PyTorch then `pip install -U nemo_toolkit['asr']`; `ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v3")`, then `transcribe([...])`; timestamps via `transcribe([...], timestamps=True)` returning char/word/segment levels (`output[0].timestamp['word' | 'segment' | 'char']`); long-form via `change_attention_model(self_attention_model="rel_pos_local_attn", att_context_size=[256, 256])` before transcribe (**Reported**).[^parakeet-v3-card]
- Chunked streaming path reuses the RNNT streaming example (`speech_to_text_streaming_infer_rnnt.py`) with e.g. `right_context_secs=2.0 chunk_secs=2 left_context_secs=10.0 batch_size=32` (**Reported**).[^parakeet-v3-card]
- Transformers (install from source until an official release): `pipeline("automatic-speech-recognition", model="nvidia/parakeet-tdt-0.6b-v3")`, or `AutoModelForTDT` + `AutoProcessor` with `model.generate(...)` and `processor.decode(..., durations=..., skip_special_tokens=True)` for timestamped tokens; a training fence shows processor-prepared `labels`, forward loss, and `loss.backward()` (**Reported**).[^parakeet-v3-card]
- Card also links the v2 NVIDIA NIM endpoint (`build.nvidia.com/nvidia/parakeet-tdt-0_6b-v2`) as the hosted option; no v3 NIM is named in the card (**Reported**).[^parakeet-v3-card]

## Deployment requirements

- Runtime engine NeMo 2.4; supported microarchitectures Ampere, Blackwell, Hopper, Volta; preferred OS Linux; at least 2 GB RAM to load, with larger RAM supporting larger audio inputs (**Reported**).[^parakeet-v3-card]
- Test hardware listed: A10, A100, A30, H100, L4, L40, Turing T4, Volta V100 (**Reported**).[^parakeet-v3-card]

## Limitations and trust notes

- Card-stated limits: transcripts may not be 100% accurate, varying with domain, accent, noise, speech type, and context; words outside the trained vocabulary are unlikely to be recognized; not recommended for word-for-word or incomplete-sentence use (**Reported**).[^parakeet-v3-card]
- Bias subcard: no participation considerations from protected groups and no mitigation measures stated; privacy subcard asserts dataset provenance and labeling compliant with privacy law, but notes externally sourced data cannot honor correction/removal requests (**Reported**).[^parakeet-v3-card]

## Relationships

- Extends [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md): same ~0.6B FastConformer-TDT offline recipe and CC-BY-4.0 terms, expanded from English-only (~120K-hour Granary English recipe, NeMo 2.2) to 25 European languages (10K-hour human + 660K-hour pseudo Granary recipe, NeMo 2.4, SentencePiece-8192); prefer this page for multilingual coverage and the v2 page for its English-only SNR/telephone robustness rows (**Synthesis**).[^parakeet-v3-card]
- Multilingual counterpart of [Canary-1b-v2](canary-1b-v2.md): both cover 25 European languages with punctuation and timestamps on NeMo, differing in size (~0.6B TDT here versus ~1B multitask there); compare FLEURS/MLS/CoVoST tables across the two pages when choosing a NeMo multilingual checkpoint (**Synthesis**).[^parakeet-v3-card]
- Contrast streaming operating points with [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) and [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): those pages cover cache-aware chunked streaming and overlapped-multitalker streaming respectively, versus this page's offline up-to-24-minute (3-hour local-attention) single-pass transcription with a chunked-inference script as the only streaming path (**Synthesis**).[^parakeet-v3-card]
- [Parakeet ASR Server](parakeet-asr-server.md) deploys these weights as a self-hosted Go service via the istupakov ONNX conversion behind a Whisper-compatible REST/SSE API, with CPU/CUDA images and silence-aware long-audio chunking; prefer that page for deployment and operations (**Synthesis**).[^parakeet-server-readme]
- Served at batch scale by [Fast GPU ASR](fast-gpu-asr.md): that TensorRT library benchmarks these V3 weights with beam-6 TDT search (B300 FP16 batch-256: 19,398.7 RTFx at 4.810% mean English WER over 157.8 h) as its offline batch alternative to this page's NeMo/Transformers/GGUF routes; prefer that page for maximum GPU batch throughput (**Synthesis**).[^fast-gpu-asr-readme]
- Compare offline multilingual accuracy with [Qwen3-ASR family](qwen3-asr-family.md), [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md), and [Audio8-ASR-0.1B](audio8-asr-0.1b.md): this page's differentiator in the wiki is the 0.6B TDT greedy WER grid across FLEURS/MLS/CoVoST per language plus the 6.34% English Open ASR average and MUSAN SNR rows (**Synthesis**).[^parakeet-v3-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, no checkpoint or GGUF download, no audio transcribed, and no WER figure reproduced (**Synthesis**).[^parakeet-v3-card]
- Referenced but unfetched and absent from `raw/`: `plots/asr.png` WER comparison figure, Technical Report (`arXiv:2509.14128`), Granary dataset, NeMo toolkit example/config/tokenizer scripts, FastConformer/TDT/SentencePiece papers, NeMo documentation, Hugging Face demo space and ASR leaderboard, v2 model/collection/NIM links, FLEURS/MLS/CoVoST/MUSAN datasets, sample audio; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-v3-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-v3-card]

[^parakeet-v3-card]: [Parakeet TDT 0.6B V3 multilingual model card](../raw/parakeet-tdt-0.6b-v3.md) — locators: frontmatter (`pipeline_tag`, `library_name: transformers`, 25-language list, `license: cc-by-4.0`, `datasets: nvidia/Granary + nemo/asr-set-3.0`, per-dataset `model-index` WERs incl. AMI 11.31 / Earnings22 11.42 / GigaSpeech 9.59 / LS-clean 1.93 / LS-other 3.59 / SPGI 3.97 / TEDLIUM 2.75 / VoxPopuli 6.14 and FLEURS/MLS/CoVoST per-language rows); `Description` (600M params, v2→25-language extension, auto language detection, demo link, 25-language list); `Key Features` (punctuation/capitalization, word+segment timestamps, 24-min full / 3-h local audio, CC-BY-4.0, Technical Report link); `License`, `Deployment Geography` (Global), `Use Case`, `Release Date` (08/14/2025), `Model Architecture` (FastConformer-TDT); `Input` (16 kHz mono wav/flac) / `Output` (punctuated capitalized string); `How to Use` (NeMo-Speech.cpp `q8_0.gguf` fences; NeMo `pip install`, `ASRModel.from_pretrained`, `transcribe`, timestamps fence, `change_attention_model(rel_pos_local_attn, [256,256])`, RNNT streaming script fence with `right_context_secs/chunk_secs/left_context_secs/batch_size`; Transformers `pipeline`/`AutoModelForTDT`/`AutoProcessor`/`generate`/`decode(durations)`/training fences; v2 NIM link); `Software Integration` (NeMo 2.4, Ampere/Blackwell/Hopper/Volta, Linux, 2 GB RAM); `Training` (CTC-multilingual init, 150k steps / 128 A100, temp sampling 0.5, stage-2 5k steps / 4 A100 on ~7.5k h, SentencePiece-8192, example script + TDT yaml); `Training Dataset` (10k h human across 8 named sources + 660k h pseudo YTC/MOSEL/YODAS, Interspeech-2025 note); `Evaluation Datasets` (FLEURS/MLS/CoVoST + Open ASR Leaderboard); `Performance` (FLEURS avg 11.97 / MLS 7.83 / CoVoST 11.98 25-row table, English avg-6.34 8-dataset row, MUSAN SNR 10/5/0/-5 table, eval notes 1–2); `Inference` (NeMo engine, A10/A100/A30/H100/L4/L40/T4/V100); `Ethical/Bias/Explainability/Privacy/Safety` subcards; `References [1]–[14]`.

[^parakeet-server-readme]: [Parakeet ASR server README](../raw/parakeet.md) — locators: header (Go server, Parakeet TDT 0.6B via ONNX Runtime, Whisper-compatible API); `Model Architecture` (istupakov ONNX conversion of `nvidia/parakeet-tdt-0.6b-v3`); `Installation` (`ghcr.io/achetronic/parakeet:latest` CPU + `:latest-cuda` GPU images); `API Reference` (Whisper-compatible REST/SSE `transcript.text.delta/done`); `Long Audio` (`-long-audio` silence-aware chunking).
[^fast-gpu-asr-readme]: [Fast GPU ASR README](../raw/fast-gpu-asr.md) — locators: `Batched speech recognition at up to 25,000 RTFx on B300` (FP16 beam-6 table, B300 batch-256 Parakeet V3 TDT 19,398.7 RTFx at 4.810% mean WER, 157.8-hour seven-English-dataset suite); `Models and Inference Precision` (Parakeet TDT V3/V2 export support); `Transcribe` (`ASR` fence).
