---
type: Concept
title: Frame-VAD Multilingual MarbleNet v2.0
description: NVIDIA NeMo's 91.5K-parameter CNN frame-level voice activity detector emitting a speech probability per 20 ms frame for six languages, trained on about 3,930 hours including noise, with vendor-reported ROC-AUC of 92.27–97.59 across seven diarization-style sets, an ONNX export recipe, and no published latency, streaming, or Vietnamese evidence.
tags: [vad, nemo, nvidia, marblenet, multilingual, onnx, diarization-frontend, license-check]
status: stable
created: 2026-10-11
generated: { by: llm-wiki-agent/1, at: 2026-10-11T20:00:00Z }
stale_after: 2027-10-11
sources:
  - id: marblenet-v2-card
    resource: ../raw/Frame_VAD_Multilingual_MarbleNet_v2.0.md
    kind: documentation
    title: Frame-VAD Multilingual MarbleNet v2.0 Hugging Face model card capture (nvidia/frame_vad_multilingual_marblenet_v2.0)
---

Frame-VAD Multilingual MarbleNet v2.0 (`nvidia/frame_vad_multilingual_marblenet_v2.0`) is a very small convolutional voice activity detector (VAD) from NVIDIA's NeMo toolkit. It is a frame-based MarbleNet (a 1D time-channel separable CNN) with 91.5K parameters that outputs one speech probability per 20 ms frame of 16 kHz mono audio, and the card positions it as the first step before speech recognition and speaker diarization. It covers Chinese, English, French, German, Russian, and Spanish, and was trained with noise and volume perturbation plus non-speech sounds (cough, laughter, breathing) to cut false positives. The card reports ROC-AUC between 92.27 (AISHELL4-test) and 97.59 (VoxConverse-dev) but gives no latency, throughput, streaming, threshold, or baseline-comparison figures, and the license is the NVIDIA Open Model License rather than a standard OSS license. All figures are vendor-reported (**Reported**).[^marblenet-v2-card]

## Identity and licensing

- Publisher: NVIDIA; library `nemo`, pipeline tag `voice-activity-detection`, declared languages `en, es, fr, de, ru, zh`, tags include `onnx` and `onnxruntime`. Version string is simply "Frame-VAD Multilingual MarbleNet v2.0"; the capture records no revision, date, or commit (**Reported**).[^marblenet-v2-card]
- License: frontmatter says `license: other`; the body names the [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license) as governing terms and states the model is "ready for commercial use". The agreement text was not captured, so its actual permissions, attribution, and redistribution terms are **Unverified**; check them before shipping, as with other `other`-licensed models in this wiki (**Reported**).[^marblenet-v2-card]
- Method reference: MarbleNet, Jia, Majumdar and Ginsburg, ICASSP 2021 (arXiv 2010.13886; not captured) (**Reported**).[^marblenet-v2-card]

## Model and interface

| Item | Value |
|---|---|
| Architecture | MarbleNet CNN; spectrogram features in, per-frame speech probability out |
| Parameters | 91.5K (≈0.37 MB at fp32, **Synthesis** from 4 bytes each) |
| Frame resolution | 20 ms per output frame; no finer granularity is supported |
| Input | `.wav`, 16 kHz mono; card says "Pre-Processing Not Needed" (the NeMo model includes its own `preprocessor`) |
| Output | 1D float array of speech probabilities per frame |
| Runtime | NeMo 2.3.0 (`pip install -U nemo_toolkit['asr']`); Linux; Ampere, Blackwell, Hopper, Lovelace, Pascal, Turing, Volta, and Jetson listed |
| Test hardware | RTX 5000, A100, V100 (no timings given) |

(**Reported**)[^marblenet-v2-card]

- The probabilities "may need post-processing": smoothing to reduce fluctuation and thresholding (example cutoff 0.5) to label frames speech versus silence/noise. No recommended smoothing window, threshold, hangover, or minimum-duration values are given in the card text (**Reported**; gap).[^marblenet-v2-card]
- Longer inputs are supported by splitting into 20 ms segments internally; outputs are never finer than 20 ms (**Reported**, Technical Limitations).[^marblenet-v2-card]

## Usage paths

1. **PyTorch / NeMo.** Load with `nemo_asr.models.EncDecFrameClassificationModel.from_pretrained(model_name="nvidia/frame_vad_multilingual_marblenet_v2.0")`, move to GPU if present, call `vad_model(input_signal=..., input_signal_length=...)` on a librosa-loaded 16 kHz float tensor under `torch.no_grad()` (**Reported**).[^marblenet-v2-card]
2. **ONNX export.** With NeMo typechecking disabled, run `vad_model.preprocessor` to get `processed_signal` and `processed_signal_length`, then `torch.onnx.export` with inputs `processed_signal` and `processed_signal_length`, output `output`, and dynamic axes on batch and sequence length. The ONNX graph therefore takes pre-computed spectrogram features, not raw waveform, so a consuming runtime must reproduce NeMo's feature extraction (parameters not stated in the card) — an inference from the export code (**Observed**, static; not executed).[^marblenet-v2-card]
3. **ONNX Runtime.** `onnxruntime.InferenceSession(..., providers=["CPUExecutionProvider"])` fed the same two arrays (**Reported**).[^marblenet-v2-card]
4. **Segment / RTTM output.** NeMo's `examples/asr/speech_classification/frame_vad_infer.py` with config `frame_vad_infer_postprocess.yaml`, `vad.parameters.shift_length_in_sec=0.02`, `prepare_manifest.auto_split=True`, `prepare_manifest.split_duration=7200`, an input manifest, and an output manifest path writes RTTM (Rich Transcription Time Marked) files. Post-processing parameters live in that YAML, which was not captured (**Reported**).[^marblenet-v2-card]

The captured examples are all whole-file / batch inference. No incremental, chunk-by-chunk streaming call, state handling, or online-latency figure is documented, although the card lists latency and throughput among its performance metrics (**Observed** gap).[^marblenet-v2-card]

## Training, test, and evaluation data

- **Training:** about 2,600 h real data, 1,000 h synthetic data, and 330 h noise data from ICSI and AMI (en), MLS (fr, es), Common Voice 7 (de, ru), RULS and SOVA (ru), AISHELL-2 (zh), LibriSpeech and Fisher (en), plus noise/non-speech sources MUSAN, Freesound, VocalSound, ICBHI, and Coswara. Collection and labeling are "Hybrid: Human, Annotated, Synthetic" (**Reported**).[^marblenet-v2-card]
- **Test:** about 100 h across the six languages from Freesound, MUSAN, LibriSpeech, Fisher, MLS, MCV7, AMI, AISHELL-2, and CH109. No results are given for this set (**Reported**).[^marblenet-v2-card]
- **Evaluation (the table below):** about 182 h of "multilingual (Chinese, English)" audio from VoxConverse (test, dev), AMI-test, Earnings21, AISHELL4-test, CH109, and AVA-SPEECH. Only Chinese and English are evaluated; the other four trained languages have no reported number, and the card does not break results down by language (**Reported**; **Observed** gap).[^marblenet-v2-card]
- AMI and CH109 appear in more than one of the training, test, and evaluation lists; split definitions are not given, so train/eval overlap cannot be ruled out from the card (**Synthesis**; **Unverified**).[^marblenet-v2-card]
- Bias/privacy fields: the stated mitigation is noise and volume perturbation plus non-speech training audio; the named bias metric is false-positive rate, but no FPR value is reported. The card states no personal data was used and dataset provenance exists (**Reported**).[^marblenet-v2-card]

## Reported performance

| Evaluation set | ROC-AUC (higher is better) |
|---|---:|
| VoxConverse-dev | 97.59 |
| Earnings21 | 97.11 |
| VoxConverse-test | 96.65 |
| AMI-test | 96.25 |
| AVA-SPEECH | 95.26 |
| CH109 | 94.44 |
| AISHELL4-test | 92.27 |

(**Reported**, "Performance" table)[^marblenet-v2-card]

- Reading the table (**Synthesis**): the unweighted mean of the seven values is about 95.65; the lowest score is on Mandarin meeting speech (AISHELL4-test), the highest on English broadcast/conference-style VoxConverse. Because the table only gives threshold-free ROC-AUC, it shows ranking quality of the probabilities, not frame accuracy, false-alarm rate, miss rate, or segment-level error at any operating point.
- No baseline (Silero, TEN, WebRTC, earlier MarbleNet versions) is evaluated, no confidence interval or variance is given, and no latency, RTF, memory, or throughput table appears despite the metric list (**Observed** gaps).[^marblenet-v2-card]
- Stated risk: quality may degrade for languages and accents outside the six trained languages (**Reported**).[^marblenet-v2-card]

## Relationships

- Peer of [Silero VAD](silero-vad.md), [TEN VAD](ten-vad.md), and [FireRedVAD](firered-vad.md) as an open frame-level VAD. It is the smallest by parameter count on the pages (91.5K versus roughly 0.57–0.59 M for FireRedVAD), but the cards use different metrics (ROC-AUC here; ROC-AUC, F1, false-alarm and miss rates on FireRedVAD's own set; precision/RTF claims for TEN), so the numbers are not comparable and none of the pages offers a head-to-head result (**Synthesis**).[^marblenet-v2-card]
- Designed as the front end for ASR and diarization in the NeMo ecosystem; the card's model-application list names ASR, speaker diarization, speech processing, and VAD. Related NVIDIA components in the wiki include [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md), [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md), and [Nemotron 3 Diarization](nemotron-3-diarization.md); the card does not state that any of them uses this VAD internally (**Synthesis**).[^marblenet-v2-card]
- Appears as a baseline in the [PulseVAD](pulsevad.md) README (91,000 parameters, 630 ms latency, labeled non-commercial, AUC 0.970 clean / 0.910 windy versus PulseVAD 2.1k at 0.976 / 0.938); that setup, version, and licensing label differ from this card and are unreconciled, see PulseVAD's Contradictions (**Synthesis**).
- A community thread recorded on [audio.cpp Framework](audio-cpp-framework.md) reports a MarbleNet VAD arriving in audio.cpp on 06/26; that thread does not name this checkpoint version, so the link is by model-family name only and the port's parity with the NeMo model is **Unverified** (**Synthesis**).
- Like the other VADs it detects speech presence only, with no end-of-turn semantics; for conversational endpointing pair it with a model from [Turn Detection Models](turn-detection-models.md) and tune smoothing and silence thresholds on in-domain audio, as advised in [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) (**Synthesis**).
- Selection use (**Synthesis**): worth considering where a NeMo/NVIDIA stack, six-language coverage including Mandarin and Russian, a very small CPU-runnable ONNX model, or a diarization front end matters. Before voice-agent use, validate Vietnamese and noisy-call behavior, streaming wrapper overhead, and the license terms, since the card offers evidence for none of them.

## Coverage and limits

- One file inspected statically: `raw/Frame_VAD_Multilingual_MarbleNet_v2.0.md` (frontmatter, description, architecture, I/O, usage code, software integration, datasets, performance, ethics/bias/explainability/privacy/safety tables). Dataset and reference links are listed in the card but their targets were not fetched.
- Not captured and not inspected: the checkpoint, NeMo source (`EncDecFrameClassificationModel`, `frame_vad_infer.py`, `frame_vad_infer_postprocess.yaml`), the MarbleNet paper, the license text, and the Model Card++ subcards. NVIDIA's generic ethics, security-reporting, and GPU-marketing boilerplate was treated as non-durable.
- Nothing was installed or run; code snippets, parameter counts, and ROC-AUC values are quoted from the card and were not reproduced.
- Absent from the source: revision/date, frame-level or segment-level accuracy at a threshold, false-positive-rate value, per-language results, streaming support and latency, CPU/GPU timings, Vietnamese or noisy-telephony evidence, and baseline comparisons.

[^marblenet-v2-card]: [Frame-VAD Multilingual MarbleNet v2.0 model card capture](../raw/Frame_VAD_Multilingual_MarbleNet_v2.0.md) — frontmatter (`license: other`, `language`, `metrics: roc_auc`, `pipeline_tag`, `library_name`); `Description` and `Key Features`; `License/Terms of Use`; `Model Architecture`; `Input` / `Output`; `How to Use the Model` (automatic load, PyTorch inference, ONNX export, ONNX Runtime, RTTM output); `Software Integration`; `Training, Testing, and Evaluation Datasets`; `Inference` (test hardware); `Performance` (ROC-AUC table); `Bias`, `Explainability` (Technical Limitations, Potential Known Risks), `Privacy`, `Safety`.
