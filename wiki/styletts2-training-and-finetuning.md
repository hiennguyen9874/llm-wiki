---
type: Concept
title: StyleTTS 2 Training and Finetuning
description: Procedure for training and finetuning StyleTTS 2 from its README, covering data list format, two-stage training commands, key configuration options, pre-trained modules, LJSpeech and new-speaker finetuning, and the DDP, NaN, and OOM limits.
tags: [tts, styletts2, training, finetuning, procedure]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T05:10:00Z }
stale_after: 2027-04-13
sources:
  - id: styletts2-readme
    resource: ../raw/styletts2.md
    kind: documentation
    title: StyleTTS 2 README capture
---

StyleTTS 2 trains in two stages, `train_first.py` and then `train_second.py`, both driven by a YAML config. A separate finetuning script adapts a pre-trained multispeaker model to new speakers. The README gives commands, data format, and key options, but the scripts and configs were not captured, so this procedure is README-reported and not reproduced (**Reported**).[^styletts2-readme] Second-stage training and finetuning run under DataParallel because DDP does not work for them (issue #7). The model itself is summarized in [StyleTTS 2](styletts2.md).

## Data preparation

- **LJSpeech:** download and extract into the data folder, then upsample to 24 kHz. The pre-trained text aligner and pitch extractor were trained on 24 kHz data, so a different rate means retraining them with your own preprocessing (line 42).
- **LibriTTS:** combine `train-clean-360` and `train-clean-100`, and rename the folder `train-clean-460`. The README links an example list, `val_list_libritts.txt`, in the `yl4579/StyleTTS` repository (line 43).
- **Data list:** `filename.wav|transcription|speaker` (line 56). Speaker labels are required for multispeaker models because reference audio is sampled for style-diffusion training (line 56).

## Training stages

| Stage | README command | Notes | Locator |
| --- | --- | --- | --- |
| 1st | `accelerate launch train_first.py --config_path ./Configs/config.yml` | No mixed precision (NaN risk) | lines 46–49, 73 |
| 2nd | `python train_second.py --config_path ./Configs/config.yml` | DataParallel; DDP not working | lines 50–53 |

- The two stages can run back to back in one run (line 54).
- Checkpoints save as `epoch_1st_%05d.pth` and `epoch_2nd_%05d.pth` in `log_dir`, with TensorBoard logs (line 54).

## Key configuration options

| Key | README meaning | Locator |
| --- | --- | --- |
| `OOD_data` | Out-of-distribution texts for SLM adversarial training, in pipe-separated form with a free second field | line 60 |
| `min_length` | Minimum length of OOD texts, so synthesized speech has a minimum length | line 61 |
| `max_len` | Maximum training audio length in frames. Default hop size 300 is about 0.0125 s per frame at 24 kHz; lower it for OOM | line 62 |
| `multispeaker` | `true` for multispeaker models; changes the denoiser architecture | line 63 |
| `batch_percentage` | Limits the SLM adversarial batch to avoid OOM | line 64 |
| `joint_epoch` | A value above `epochs` skips SLM adversarial training, which may reduce quality | line 93 |

## Pre-trained modules

- **Text aligner (`Utils/ASR`):** pre-trained on English (LibriTTS), Japanese (JVS), and Chinese (AiShell) data. It works for most languages without finetuning. Retrain with [yl4579/AuxiliaryASR](https://github.com/yl4579/AuxiliaryASR) if needed (line 68).
- **Pitch extractor (`Utils/JDC`):** pre-trained on English LibriTTS only. The README treats F0 as language-independent and recommends a new extractor for singing, via [yl4579/PitchExtractor](https://github.com/yl4579/PitchExtractor) (line 69).
- **PL-BERT (`Utils/PLBERT`):** pre-trained on English Wikipedia only and probably weak on other languages. Retrain per language with [yl4579/PL-BERT](https://github.com/yl4579/PL-BERT), or use the multilingual PL-BERT, which covers 14 languages (lines 70, 75).

## Finetuning

- Start from a LibriTTS checkpoint, downloaded and unzipped into the project folder (line 82). The script is derived from `train_second.py` and uses DataParallel (line 78).
- Default command: `python train_finetune.py --config_path ./Configs/config_ft.yml` (lines 79–81).
- Single GPU: `accelerate launch --mixed_precision=fp16 --num_processes=1 train_finetune_accelerate.py --config_path ./Configs/config_ft.yml` (lines 84–87). The README credits a contributed script (PR #100).
- Reported run times: the default config (LJSpeech, around 1k samples, 1 hour of speech, 50 epochs) took about 4 hours on four A100 GPUs. Training from scratch on 24 hours of LJSpeech took about 2.5 days on four A100 GPUs. The README calls the finetuned quality "slightly worse" than from-scratch training (line 82).
- Community finetuning notes are linked (issues #81 and #128; line 91) but not captured.

## Known issues

| Symptom | README-stated cause or mitigation | Locator |
| --- | --- | --- |
| NaN loss, first stage | Do not use mixed precision; the README says batch size must exceed 16 to work well | line 73 |
| NaN loss, second stage | Larger batches are more NaN-prone; the README recommends batch size 16 (issues #10, #11) | line 73 |
| OOM during training | Lower `batch_size` or `max_len` (issue #10) | lines 64, 74 |
| OOM after `joint_epoch` | GPU RAM too small for the SLM adversarial stage; skipping it may reduce quality | line 93 |
| DDP fails | Unsupported for `train_second.py` and the finetune scripts (issue #7) | lines 20, 50, 78 |
| Non-English data | Use a PL-BERT suited to the language; the README links Chinese examples (StyleTTS #10, StyleTTS 2 #70) | line 75 |

## Limits and open questions

- The scripts and configs are not captured, so config keys the README does not list are unknown (**Unverified**).
- Batch-size guidance is not reconciled across stages. Stage 1 says batch size must exceed 16, while stage 2 recommends 16 and warns that larger batches are more NaN-prone (line 73).
- The first-stage warning against mixed precision is not extended to the fp16 single-GPU finetuning example (lines 84–87). The README does not say whether it applies there.
- Times and hardware come from the author's runs on four A100 GPUs (line 82), reported only. No seeds, dataset checksums, or evaluation protocol are given.

## Relationships

- Describes the training and finetuning of [StyleTTS 2](styletts2.md) (**Synthesis**; model claims live on that page).
- Uses the pre-trained text aligner, pitch extractor, and PL-BERT modules listed above. Their upstream repositories are linked, not captured (**Reported**).[^styletts2-readme]

## Coverage and limits

- **Inspected:** `raw/styletts2.md` lines 22–93, from prerequisites through finetuning, read statically. Nothing was installed, run, or trained.
- **Excluded as decorative:** Colab badges and contributor thanks.
- **Pending, not captured:** the training scripts, the `Configs/` YAML files, the `Utils/` pre-trained folders, the LJSpeech, LibriTTS, and VCTK datasets, and the linked issues and discussions.

[^styletts2-readme]: [StyleTTS 2 README capture](../raw/styletts2.md) — locators: title and authors (lines 1–3); TODO list (lines 15–20); prerequisites (lines 22–41); data preparation (lines 42–43); training commands and checkpoints (lines 45–54); data list and speaker labels (line 56); configuration keys (lines 58–64); pre-trained modules (lines 66–70); common issues (lines 72–75); finetuning and single-GPU example (lines 77–93). No revision recorded (limit).
