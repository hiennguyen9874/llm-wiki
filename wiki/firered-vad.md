---
type: Concept
title: FireRedVAD
description: FireRedTeam's Apache-2.0 DFSMN-based voice activity detection and audio event detection toolkit with non-streaming VAD, streaming VAD, and speech/singing/music AED models of about 0.57–0.59 M parameters, a vendor-reported 97.57% F1 on its own 102-language FLEURS-VAD-102 set, and no published streaming-model metrics.
tags: [vad, aed, endpointing, streaming, multilingual, chinese, english, pytorch, ncnn, license-check]
status: stable
created: 2026-10-11
generated: { by: llm-wiki-agent/1, at: 2026-10-13T03:00:00Z }
stale_after: 2027-10-11
sources:
  - id: firered-vad
    resource: ../raw/FireRedVAD/README-github.md
    scope: ../raw/FireRedVAD/
    kind: documentation
    title: FireRedVAD (FireRedTeam) GitHub README and Hugging Face model card captures
---

FireRedVAD is the voice activity detection (VAD) and audio event detection (AED) component of FireRedTeam's FireRedASR2S speech system (alongside FireRedASR2-AED, FireRedLID, and FireRedPunc), also released as a standalone repository on 2026-03-03. It ships three small DFSMN-based (Deep Feedforward Sequential Memory Network) models: a non-streaming VAD, a streaming VAD (`Stream-VAD`), and a non-streaming AED that labels speech, singing, and music. On the authors' own 102-language FLEURS-VAD-102 set, the non-streaming VAD is reported at F1 97.57% and false-alarm rate 2.69%, ahead of [Silero VAD](silero-vad.md), [TEN VAD](ten-vad.md), FunASR-VAD, and WebRTC VAD. The test set is unreleased, metric definitions and operating thresholds are not given, and the captures publish no accuracy, latency, or RTF figures for the streaming model that voice-agent endpointing would use. Treat every figure as vendor-reported (**Reported**).[^firered-vad]

## Identity and licensing

- Publisher: FireRedTeam; code at `FireRedTeam/FireRedVAD` (GitHub), weights on Hugging Face (`FireRedTeam/FireRedVAD`) and ModelScope (`xukaituo/FireRedVAD`); demo is a Hugging Face Space for FireRedASR2S. Paper: FireRedASR2S technical report, arXiv 2603.10420 (not captured) (**Reported**).[^firered-vad]
- License: the Hugging Face card frontmatter declares `apache-2.0` (languages `en`, `zh`; pipeline tag `voice-activity-detection`). The GitHub capture contains no license statement, and no `LICENSE` file was captured, so the weight license is as declared on the model card only (**Reported**; **Unverified** beyond the card).[^firered-vad]
- Timeline in both captures: 2026-02-12 FireRedASR2S release (with FireRedVAD), 2026-03-03 standalone repository with weights and inference code, 2026-03-12 technical report. No release tag, commit, or capture date is recorded (**Reported**; freshness **Unverified**).[^firered-vad]
- Method statement is a single line: "DFSMN-based non-streaming/streaming VAD and AED". Architecture details, training data, and recipe are not described in the captures (**Reported**).[^firered-vad]

## Models and tasks

| Task | CLI `--task` / script | Python class | Model subdir | Params (CLI banner) |
|---|---|---|---|---|
| Non-streaming VAD | `vad` / `vad.py` | `FireRedVad`, `FireRedVadConfig` | `VAD` | 588,417 (2.2 MB fp32) |
| Streaming VAD | `stream_vad` / `stream_vad.py` | `FireRedStreamVad`, `FireRedStreamVadConfig` | `Stream-VAD` | 567,937 (2.2 MB fp32) |
| Audio event detection | `aed` / `aed.py` | `FireRedAed`, `FireRedAedConfig` | `AED` | 588,931 (2.2 MB fp32) |

- Parameter counts come from the `DetectModel` banner lines in the GitHub CLI examples; the "2.2 MB (float32)" label matches roughly 0.57–0.59 M parameters at 4 bytes each (**Observed** from README output, not executed).[^firered-vad]
- Claimed coverage is speech, singing, and music detection in "100+ languages"; streaming is VAD-only, while AED is non-streaming (**Reported**).[^firered-vad]
- The captures list a `runtime` directory with NCNN support for multiplatform deployment (GitHub only); its contents, supported platforms, and any ONNX export were not captured (**Reported**; details unknown).[^firered-vad]

## Interface and operating parameters

**Input.** 16 kHz, 16-bit, mono PCM WAV; other formats are converted with `ffmpeg -i <in> -ar 16000 -ac 1 -acodec pcm_s16le -f wav <out>` (**Reported**).[^firered-vad]

**Install and run.** Python 3.10 conda environment. The GitHub capture offers `pip install fireredvad` (CLI `fireredvad --task {vad,stream_vad,aed} --wav_path ... --model_dir ...`, plus a `[gpu]` extra for PyTorch) or a source install with `requirements.txt` (CUDA Linux/Windows) or `requirements-macos-arm64.txt`, then `PATH`/`PYTHONPATH` exports. The Hugging Face card is older and lists only the source install. Weights are fetched with `modelscope download` or `huggingface-cli download` into `pretrained_models/FireRedVAD` (**Reported**).[^firered-vad]

**Post-processing parameters.** All three tasks share a frame-level probability stage followed by smoothing, thresholding, and segment cleanup. Python-API example values (identical in both captures) and the CLI-example values (which differ between captures) are:[^firered-vad]

| Parameter | VAD API | Stream-VAD API | AED API | Meaning as inferred from the name |
|---|---:|---:|---:|---|
| `smooth_window_size` | 5 | 5 | 5 | probability smoothing window (frames) |
| `speech_threshold` | 0.4 | 0.4 | 0.4 | speech decision threshold |
| `singing_threshold` / `music_threshold` | — | — | 0.5 / 0.5 | AED per-event thresholds |
| `pad_start_frame` | — | 5 | — | frames added before detected start (streaming) |
| `min_speech_frame` | 20 | 8 | — | shortest accepted speech segment |
| `min_event_frame` | — | — | 20 | shortest accepted event |
| `max_speech_frame` / `max_event_frame` | 2000 | 2000 | 2000 | longest segment before forced split |
| `min_silence_frame` | 20 | 20 | 20 | silence needed to close a segment |
| `merge_silence_frame` | 0 | — | 0 | merge segments separated by short gaps |
| `extend_speech_frame` | 0 | — | 0 | extend segment boundaries |
| `chunk_max_frame` | 30000 | 30000 | 30000 | maximum frames per processed chunk |
| `use_gpu` | False | False | False | PyTorch device choice |

- The README never states the frame duration, so conversions to milliseconds are not documented. A 10 ms frame shift is the common default for this kind of front end but is **Unverified** here; if it holds, `min_silence_frame=20` is about 200 ms and `max_speech_frame=2000` about 20 s (**Synthesis**).[^firered-vad]
- Streaming and non-streaming differ in the knobs they expose: `Stream-VAD` adds `pad_start_frame` and has no `merge_silence_frame` or `extend_speech_frame` (**Observed**).[^firered-vad]
- CLI flags `--write_textgrid 1`, `--output`, and `--save_segment_dir` write a result file, Praat TextGrid labels, and per-segment audio (**Reported**).[^firered-vad]

**Outputs.**

- VAD: `{'dur', 'timestamps': [(start_s, end_s), ...], 'wav_path'}` plus per-frame `probs`; example `hello_zh.wav` (2.32 s) gives `(0.44, 1.82)` (**Reported**).[^firered-vad]
- Streaming VAD: per-frame `StreamVadFrameResult(frame_idx, is_speech, raw_prob, smoothed_prob, is_speech_start, is_speech_end, speech_start_frame, speech_end_frame)`; `detect_full(wav)` returns the frame results plus the same timestamp dictionary, e.g. `hello_en.wav` (2.24 s) gives `(0.28, 1.83)`. `frame_idx` starts at 1 in the example (**Reported**).[^firered-vad]
- AED: `event2timestamps` and `event2ratio` per event class. In the 22.016 s example, speech, singing, and music ratios are 0.848, 0.905, and 0.991, which sum above 1, so events are scored independently and can overlap (**Observed**).[^firered-vad]
- Only whole-file entry points (`detect`, `detect_full`) are documented. The captures do not show the incremental per-chunk call a live pipeline needs, so integrators must read the source or the consuming projects (**Observed** limit).[^firered-vad]

## Reported performance

Benchmark: **FLEURS-VAD-102**, built by the authors from about 100 randomly chosen files per language of the [FLEURS](https://huggingface.co/datasets/google/fleurs) test set (102 languages, 9,443 files) with manually annotated binary labels (speech = 1, silence = 0). The set is announced as "coming soon" open-source (**Reported**).[^firered-vad]

| Metric | FireRedVAD | Silero-VAD | TEN-VAD | FunASR-VAD | WebRTC-VAD |
|---|---:|---:|---:|---:|---:|
| AUC-ROC ↑ | **99.60** | 97.99 | 97.81 | — | — |
| F1 ↑ | **97.57** | 95.95 | 95.19 | 90.91 | 52.30 |
| False alarm rate ↓ | **2.69** | 9.41 | 15.47 | 44.03 | 2.83 |
| Miss rate ↓ | 3.62 | 3.95 | 2.95 | 0.42 | 64.15 |

- The authors note FunASR-VAD's low miss rate comes with a 44.03% false-alarm rate, i.e. over-prediction of speech (**Reported**).[^firered-vad]
- Reading the table (**Synthesis**): FireRedVAD is not best on every metric — TEN-VAD (2.95) and FunASR-VAD (0.42) miss less, and WebRTC's false-alarm rate (2.83) is close to FireRed's, but WebRTC misses 64% of speech. The F1 lead over Silero is 1.62 points, driven mainly by false alarms (2.69% vs 9.41%).[^firered-vad]
- Limits on interpretation: the benchmark and the system come from the same team; the threshold, frame or segment granularity, and metric definitions are not stated; the table is introduced for non-streaming VAD, and no streaming-VAD or AED metrics appear; FLEURS is read speech, so noisy telephony, far-field, and overlapping-speaker conditions are not represented; no Vietnamese-specific number is given (**Observed** gaps).[^firered-vad]
- No latency, RTF, memory, or CPU/GPU throughput figure is given, so the small model size is the only deployment-cost signal (**Observed** gap).[^firered-vad]

## Capture differences

The GitHub README is newer than the Hugging Face card (it adds the pip package, macOS requirements, and the NCNN runtime pointer; the evaluation table is the same). CLI example values differ between the captures while the Python examples match:[^firered-vad]

| CLI example | GitHub | Hugging Face |
|---|---|---|
| `vad.py` `--max_speech_frame` / `--min_silence_frame` | 2000 / 20 | 3000 / 10 |
| `stream_vad.py` `--speech_threshold` | 0.4 | 0.3 |
| `aed.py` `--max_event_frame` / `--min_silence_frame` | 2000 / 20 | 3000 / 10 |

Prefer the GitHub values as current defaults; the card's CLI values may be an earlier tuning. Which value is the true code default was not verified (**Observed** inconsistency; resolution **Unverified**).[^firered-vad]

## Relationships

- Peer of NVIDIA's [Frame-VAD Multilingual MarbleNet v2.0](frame-vad-multilingual-marblenet-v2-0.md), a smaller (91.5K versus ~0.57–0.59 M parameters) six-language NeMo frame VAD; its ROC-AUC figures are on different sets than FLEURS-VAD-102, so the two are not comparable (**Synthesis**).[^firered-vad]
- Compared in its own table against [Silero VAD](silero-vad.md) and [TEN VAD](ten-vad.md); the ordering Silero ahead of TEN on F1 matches the direction of the community benchmark recorded on the Silero page, and conflicts with TEN's own claim, but protocols and data differ so none of these settle the question (**Synthesis**).[^firered-vad]
- Used as the VAD in [Confucius4-R2T2](confucius4-r2t2.md)'s WebSocket server (`Stream-VAD` checkpoint) and as the non-default `firered` option in the [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md); its flags are listed in [Speech-to-Speech CLI and Defaults](speech-to-speech-cli-and-defaults.md), and its segment-end timing feeds the `vad_decision_s` field in [Speech-to-Speech Response Latency Instrumentation](speech-to-speech-latency-instrumentation.md) (**Synthesis**, from those pages).[^firered-vad]
- Sibling of the FireRedASR2S ASR components; it adds music/singing labeling that [Silero VAD](silero-vad.md) and [TEN VAD](ten-vad.md) do not document, and the card declares only `en` and `zh` language tags despite the "100+ languages" claim. Like both Silero and TEN, it detects speech presence only and has no end-of-turn semantics, so pair it with a turn model from [Turn Detection Models](turn-detection-models.md) for conversational endpointing (**Synthesis**).[^firered-vad]
- Selection use (**Synthesis**): consider it when music/singing separation, multilingual (including Chinese) robustness, or a tiny model with timestamped segment output matters. Validate threshold and `min_silence_frame` on in-domain audio before adopting it, as advised in [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md), because the source gives no streaming, Vietnamese, or noisy-call evidence.[^firered-vad]

- Selectable as `-vm firered` in [CrispASR](crispasr.md), where the README recommends it and quotes F1 = 97.57%. That is the same FireRed table, not an independent result; see [CrispASR VAD and Language Identification](crispasr-vad-language-id.md) (**Synthesis**).

## Coverage and limits

- Two files inspected statically: `README-github.md` (entry point) and `README-hf.md`; overlapping content was reconciled once and the differences recorded above (**Observed**).[^firered-vad]
- Not captured and not inspected: the arXiv technical report, model weights and `cmvn.ark`, Python source and `examples/*.sh`, the `runtime` (NCNN) directory, `requirements*.txt`, `assets/` audio, the Hugging Face Space demo, the unreleased FLEURS-VAD-102 test set, and any `LICENSE` file. Badges, news links, and the BibTeX entries (FireRedASR2S, FireRedASR) were treated as navigation or citation metadata only.
- Nothing was installed or run; CLI outputs, parameter counts, and benchmark numbers are quoted from the READMEs and were not reproduced.
- No revision or capture date is recorded; model architecture details, training data, streaming metrics, latency, RTF, noisy-condition accuracy, and Vietnamese performance are absent from the source.

[^firered-vad]: [FireRedVAD captures](../raw/FireRedVAD/README-github.md) — `README-github.md`: intro, `News`, `Evaluation` (FLEURS-VAD-102 table and footnote), `Quick Start` §Setup (pip, source, model download, ffmpeg), `Script Usage`, `Command-line Usage` (task outputs, parameter-count banners, flag sets), `Python API Usage` (VAD, Streaming VAD, AED), `Method`, `Runtime`, `FAQ`, `Citation`. `README-hf.md`: frontmatter (`license: apache-2.0`, `language`, `pipeline_tag`), `Evaluation`, `Quick Start` (source install only, differing CLI values), `Python API Usage`, `FAQ`.
