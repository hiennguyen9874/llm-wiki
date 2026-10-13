---
type: Concept
title: VietASR (dangvansam, QuartzNet)
description: Community Vietnamese ASR project from dangvansam on NVIDIA NeMo's QuartzNet, with a 13M-parameter pretrained model trained on about 100 hours of mixed Vietnamese speech, file-transcription and web-app entry points, and no published WER, streaming, or license evidence in the captured README.
tags: [stt, asr, vietnamese, nemo, quartznet, open-source, community]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T05:20:00Z }
stale_after: 2027-10-13
sources:
  - id: dangvansam-viet-asr-readme
    resource: ../raw/dangvansam-viet-asr.md
    kind: documentation
    title: VietASR (dangvansam/viet-asr) README capture
---

VietASR in this README is a community Vietnamese speech-to-text project by `dangvansam` (repository `dangvansam/viet-asr`) built as an NVIDIA NeMo experiment. The README says its ASR uses QuartzNet, "a smaller version" of Jasper, and that the repository's pretrained model (13M parameters) was trained on about 100 hours of Vietnamese speech from YouTube, radio, 8 kHz call-center audio, text-to-speech output, and public corpora (VLSP, VIVOS, FPT) (**Reported**).[^dangvansam-viet-asr-readme] It offers offline file transcription through `infer.py` and a web app through `app.py`. The README gives no accuracy figure and describes speed only qualitatively. Its branch note points to a PyTorch rewrite on `v2.0`, so this capture covers only the earlier NeMo line. This project is **not** the arXiv 2505.21527 VietASR (see [Disambiguation](#disambiguation)).

## Model and training data

- **Framework and model:** NVIDIA NeMo with QuartzNet. The README links the NeMo docs and cites only the NeMo toolkit paper (Kuchaiev et al., 2019), not a paper for this model.[^dangvansam-viet-asr-readme]
- **Size:** "very small model (13M parameters)"; the README gives no memory figure or checkpoint file name.[^dangvansam-viet-asr-readme]
- **Training data:** about 100 hours of Vietnamese speech from YouTube, radio, call-center audio at 8 kHz, text-to-speech data, and the public VLSP, VIVOS, and FPT corpora. The README does not state licenses, consent, or redistribution rights for these sources.[^dangvansam-viet-asr-readme]
- **Speed:** "inference so fast"; no latency, real-time factor, or hardware is given (**Reported**, unquantified).[^dangvansam-viet-asr-readme]
- **Accuracy:** the capture reports no WER, CER, or test-set result.

## Setup and entry points

- **System libraries and Python:** `libsndfile1` and `ffmpeg` via apt; "python>=3.8"; dependencies from `requirements.txt` (not captured).[^dangvansam-viet-asr-readme]
- **Torch:** `torch==1.8.1+cpu` (CUDA optional) with torchvision 0.9.1 and torchaudio 0.8.1 from the PyTorch stable index.[^dangvansam-viet-asr-readme]
- **LM decoding:** install kenlm from its GitHub master archive ("only support Linux"). The README does not say which language model to use or whether `infer.py` or `app.py` applies it.[^dangvansam-viet-asr-readme]
- **Batch transcription:** `python infer.py audio_samples` transcribes the audio files in a folder; the output format is not stated.[^dangvansam-viet-asr-readme]
- **Web app:** `python app.py`, with the address given as `https://localhost:5000`. The scheme and port were not checked against `app.py`, which was not captured.[^dangvansam-viet-asr-readme]

## Contradictions

- **Python and torch versions:** the badge says Python 3.10, the install step says Python 3.8 or newer, and torch 1.8.1 is pinned. The README does not reconcile these, and this run did not check whether torch 1.8.1 wheels exist for Python 3.10 (**Unverified**).[^dangvansam-viet-asr-readme]

## Roadmap

The README's TODO list names a Conformer model, data augmentation (speed, noise, pitch shift, time shift), FastAPI, and a Dockerfile. These are intentions, not evidence of current state. A commented-out English pretrained link is inactive.[^dangvansam-viet-asr-readme]

## Disambiguation

- Other wiki pages use "VietASR" for the arXiv 2505.21527 paper and project `zzasdf/VietASR`, for example [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) (Whisper large-v3 16.44% mean WER). Those figures do not describe this project. That paper's concept page is [VietASR (zzasdf, arXiv 2505.21527)](zzasdf-viet-asr.md), with its run procedure in [VietASR Training and Checkpoint Procedure](zzasdf-viet-asr-procedure.md).
- Other "VietASR" names in the wiki, such as the "VietASR-zipformer (68M)" column in [Gipformer 68M RNNT](gipformer-68m-rnnt.md), were not checked against this project and should not be assumed to refer to it.
- The README author handle `dangvansam` also appears on the community Namo turn detector in [Turn Detection Models](turn-detection-models.md). The capture does not link the two, so no relationship is asserted.

## Relationships

- **Uses:** NVIDIA NeMo, the toolkit named in the README. The wiki has no NeMo framework concept; NeMo-based ASR models are compared in [ASR/STT Model Survey](asr-stt-model-survey.md).
- **Compared with, not ranked against:** Vietnamese ASR models [PhoWhisper](phowhisper.md), [ChunkFormer Vietnamese](chunkformer-vietnamese.md), [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md), and [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md) carry vendor WER tables. This capture has none, so the wiki implies no ranking (**Synthesis**).
- Not on the shortlist in [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md). Without streaming or Vietnamese accuracy evidence, this capture does not change that shortlist (**Synthesis**).

## Coverage and limits

- **Inspected:** the single README capture `raw/dangvansam-viet-asr.md`, read statically. No revision, release tag, or commit is recorded.[^dangvansam-viet-asr-readme]
- **Pending or not captured:** `LICENSE` (the README shows only a license badge, so the license type is not established); `requirements.txt`; `infer.py` and `app.py`, so their behavior is unverified; the `v2.0` PyTorch branch, a different artifact; the `demo.JPG` web-app screenshot and the two YouTube demo videos; the sibling `viet-tts` (VietTTS) repository the README links; `README_VN.md` (a Vietnamese duplicate of this README); and `assets/viet-asr-logo.png` (decorative, excluded).
- **Consequential limits:** no confirmed license blocks any reuse decision; training-data provenance and the privacy status of the call-center portion are unknown; no accuracy, streaming, or hardware evidence exists. Promotion to `stable` needs the LICENSE, requirements, and entry-point files; an accuracy claim needs an evaluation event, not a README statement.
- No install, execution, inference, or benchmark was run. The capture contains only public URLs and no sensitive values.

[^dangvansam-viet-asr-readme]: [VietASR (dangvansam/viet-asr) README capture](../raw/dangvansam-viet-asr.md) — locators: title block and badges (lines 1–16, including the Python 3.10 badge at line 7 and the LICENSE badge at line 9); intro on NeMo, QuartzNet, 13M parameters, and about 100 h of training data (lines 18–21); v2.0 branch note (line 23); `Installation` (lines 27–46); `Transcribe audio file` (lines 47–51); `Run web application` (lines 52–64, with the `demo.JPG` screenshot at line 58 and video links at lines 60–64); commented-out English model (line 66); `TODO` (lines 68–73); `Citation` (lines 75–84).
