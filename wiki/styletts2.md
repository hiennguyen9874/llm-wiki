---
type: Concept
title: StyleTTS 2
description: StyleTTS 2 text-to-speech architecture with latent style diffusion and SLM adversarial training, MIT-licensed code, downloadable LJSpeech and LibriTTS checkpoints, README-reported human-level claims, and a GPL-dependent inference path.
tags: [tts, styletts2, style-diffusion, zero-shot, pretrained-models]
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

StyleTTS 2 is a text-to-speech (TTS) architecture that treats speaking style as a latent random variable, sampled by a diffusion model from the input text so that no reference speech is needed. Training adds adversarial discrimination by large pre-trained speech language models (SLMs) such as WavLM, plus a differentiable duration model for end-to-end training. The README's abstract claims human-level synthesis on LJSpeech and VCTK and better zero-shot speaker adaptation than prior public models when trained on LibriTTS. These are source-asserted and not verified in this wiki (**Reported**; **Unverified**).[^styletts2-readme] The capture is the README and its abstract, so no code, configuration, or paper body was inspected. The training and finetuning procedure is in [StyleTTS 2 Training and Finetuning](styletts2-training-and-finetuning.md).

## Method claims

- **Latent style by diffusion:** styles are modeled as a latent variable generated through diffusion, so the model can choose a style for new text without reference speech while keeping latent diffusion efficient (**Reported**).[^styletts2-readme]
- **SLM adversarial training:** large pre-trained SLMs, named as WavLM, serve as discriminators, which the README links to improved speech naturalness (**Reported**).[^styletts2-readme]
- **Differentiable duration modeling:** enables end-to-end training (**Reported**).[^styletts2-readme]
- **Single vs multispeaker:** the `multispeaker` setting changes the denoiser architecture, so the two model types are configured differently (**Reported**).[^styletts2-readme]
- **Lineage:** the README's References list names audio-diffusion-pytorch, HiFi-GAN, iSTFTNet-pytorch, and NSF scripts. It does not map them to modules, so the mapping is unknown (limit).[^styletts2-readme]

## Reported results

| Setting | Claim | Basis stated | Locator |
| --- | --- | --- | --- |
| LJSpeech, single speaker | Surpasses human recordings | Native English listeners | abstract (line 5) |
| VCTK, multispeaker | Matches human recordings | Same | abstract (line 5) |
| LibriTTS, zero-shot speaker adaptation | Outperforms prior public models | Not stated | abstract (line 5) |

The README gives no MOS, similarity, or WER values, listener counts, protocol, or variance. The sample site and paper are outside the capture, so these results stay **Unverified**.[^styletts2-readme]

## Checkpoints and demos

- LJSpeech single-speaker model at 24 kHz on Hugging Face, `yl4579/StyleTTS2-LJSpeech` (line 98).
- LibriTTS multispeaker model, `yl4579/StyleTTS2-LibriTTS` (line 102). Its demo also needs `reference_audio.zip` unpacked under `demo` (line 96).
- A hosted Hugging Face Space demo is linked (line 11). No checkpoint was downloaded, so no hashes or revision are recorded.

## Dependencies and environment

- Python 3.7 or later, then `pip install -r requirements.txt`. Windows users are told to install a cu118 PyTorch wheel (lines 23–36).
- The demo path also needs `phonemizer` and `espeak-ng` (lines 37–41). See [Phonemizer](phonemizer.md) and [eSpeak NG](espeak-ng.md).
- The README says inference "depends on a GPL-licensed package, so it is not included" (line 107). It points to a GPL fork with an importable script and an experimental streaming API, and to an MIT-licensed PyPI package `styletts2` that uses gruut. That package has lower quality "due to mismatch between phonemizer and gruut" (line 107).

## Licensing and usage terms

- Code: MIT (line 123).
- Pre-trained models: users agree to inform listeners that speech is synthesized by the models, unless they have permission to use the synthesized voice. The stated alternatives are to use only voices whose speakers permit cloning, or to announce that the voices are synthesized (lines 109, 125; **Reported**).[^styletts2-readme]
- A Common Issues entry narrows that duty to voices outside the training set, meaning reference speakers not from an open-access dataset (line 113). See [Contradictions](#contradictions).
- The GPL inference dependency sits beside the MIT code license. The README does not say how the two combine for a deployed inference path (limit). This wiki gives no licensing advice.

## Known limits

- Second-stage training and finetuning use DataParallel because DDP does not work for `train_second.py` (TODO line 20; lines 50, 78; issue #7).
- Inference on older GPUs can produce high-pitched background noise from float differences. The README advises modern GPUs or CPU inference (line 112; issue #13).
- Non-English use needs a PL-BERT suited to the language. The README's multilingual PL-BERT covers 14 languages (line 75; **Reported**).

## Contradictions

- **Scope of the pre-trained-model disclosure rule.** The Inference section (line 109) and License section (line 125) state the obligation without exception. The Common Issues entry (line 113) limits it to voices outside the training set and to reference speakers outside any open-access dataset. Neither version is chosen here. The issue it cites (#37) was not captured.[^styletts2-readme]

## Relationships

- Depends on [Phonemizer](phonemizer.md) and [eSpeak NG](espeak-ng.md) for the demo path (**Reported**).[^styletts2-readme]
- Used by [Kokoro-82M](kokoro-82m.md), which records its card's claim that the model uses this architecture (**Synthesis** from that page).
- Procedure: [StyleTTS 2 Training and Finetuning](styletts2-training-and-finetuning.md) covers its training and finetuning commands (**Synthesis**).

## Coverage and limits

- **Inspected:** `raw/styletts2.md`, the README capture from title through license. Read statically; nothing was installed, executed, or downloaded.
- **Excluded as decorative or non-durable:** Colab and Discord badges, the Discord invite, and contributor thanks.
- **Pending, not captured:** the paper body (arXiv 2306.07691), the audio sample site, repository code and `Configs/`, the `Utils/` pre-trained folders, `Demo/` and `Colab/` notebooks, `LICENSE`, `requirements.txt`, Hugging Face model cards, the GPL fork, the PyPI `styletts2` package, and linked issues and discussions (#7, #10, #11, #13, #37, #65, #70, #81, #100, #128).
- **Revision:** not recorded in the capture.

[^styletts2-readme]: [StyleTTS 2 README capture](../raw/styletts2.md) — locators: title and authors (lines 1–3); abstract (line 5); paper and samples links (lines 7, 9); online demo (line 11); TODO list (lines 15–20); prerequisites and environment (lines 22–41); data preparation (lines 42–43); training commands and checkpoints (lines 45–54); data list and speaker labels (line 56); configuration keys (lines 58–64); pre-trained modules (lines 66–70); common issues (lines 72–75); finetuning (lines 77–93); inference, checkpoints, and GPL note (lines 95–107); disclosure and common issues (lines 109–113); references (lines 115–119); license (lines 121–125). No revision recorded (limit).
