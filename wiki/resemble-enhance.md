---
type: Concept
title: Resemble Enhance
description: Resemble AI's offline speech denoiser-plus-enhancer (44.1 kHz, latent CFM enhancer) with pip CLI, denoise-only mode, Gradio demo, and a three-step training recipe, but no metrics, latency, streaming, or license terms in its README.
tags: [pipeline, speech-enhancement, denoising, bandwidth-extension, flow-matching, offline]
status: draft
created: 2026-10-23
generated: { by: llm-wiki-agent/1, at: 2026-10-23T12:00:00Z }
stale_after: 2027-10-23
sources:
  - id: resemble-enhance-readme
    resource: ../raw/ResembleEnhance.md
    kind: documentation
    title: resemble-ai/resemble-enhance README capture
---

Resemble Enhance is an open-source speech-quality tool from Resemble AI built from two modules: a denoiser that separates speech from noisy audio, and an enhancer that restores distortions and extends bandwidth to improve perceptual quality. Both are said to be trained on high-quality 44.1 kHz speech. It installs from PyPI, runs as a directory-to-directory CLI (with a denoise-only switch) or a Gradio app, and ships training commands for the denoiser and a two-stage enhancer (autoencoder plus vocoder, then a latent conditional flow matching model). The README reports no quantitative quality, ASR, latency, or streaming evidence, so its fit for a realtime voice loop is not established; its batch directory interface suggests offline or pre-processing use (**Reported**; the fit judgment is **Synthesis**).[^resemble-enhance-readme]

## Architecture

- Two modules: a **denoiser** (separates speech from noisy audio) and an **enhancer** (restores audio distortions and extends audio bandwidth) (**Reported**).[^resemble-enhance-readme]
- Training data is described as high-quality 44.1 kHz speech, "guaranteeing" high-quality enhancement; no dataset names, sizes, or hours are given, so the guarantee is an unverified marketing claim (**Reported**, **Unverified**).[^resemble-enhance-readme]
- Enhancer training has two stages: stage 1 trains the autoencoder and vocoder; stage 2 trains the latent conditional flow matching (CFM) model (**Reported**).[^resemble-enhance-readme]
- The denoiser is trained jointly with the enhancer, though a separate warmup is recommended (**Reported**).[^resemble-enhance-readme]

## Usage

| Task | Command |
|---|---|
| Install stable | `pip install resemble-enhance --upgrade` |
| Install pre-release | `pip install resemble-enhance --upgrade --pre` |
| Enhance | `resemble-enhance in_dir out_dir` |
| Denoise only | `resemble-enhance in_dir out_dir --denoise_only` |
| Local web demo | `python app.py` (Gradio; hosted Space at `ResembleAI/resemble-enhance`) |

(**Reported**.)[^resemble-enhance-readme]

- The interface takes input and output directories, i.e. batch file processing; the README documents no streaming API, chunking, or real-time mode (**Observed** from the README's absence).[^resemble-enhance-readme]
- Denoise-only skips the enhancer, which is the lighter option when bandwidth extension is not wanted. That it is cheaper is **Synthesis**; no timing is given.[^resemble-enhance-readme]
- Python, PyTorch, CUDA, and hardware requirements are not stated (**Observed**).[^resemble-enhance-readme]

## Training recipe

- **Data layout:** three folders under `data/`: `fg/` (foreground speech `.wav`), `bg/` (background non-speech `.wav`), and `rir/` (room impulse responses as `.npy`; the README points to the RoyJames/room-impulse-responses collection for examples) (**Reported**).[^resemble-enhance-readme]
- **Denoiser warmup:** `python -m resemble_enhance.denoiser.train --yaml config/denoiser.yaml runs/denoiser` (**Reported**).[^resemble-enhance-readme]
- **Enhancer stage 1:** `python -m resemble_enhance.enhancer.train --yaml config/enhancer_stage1.yaml runs/enhancer_stage1` (**Reported**).[^resemble-enhance-readme]
- **Enhancer stage 2:** the same module with `config/enhancer_stage2.yaml` and `runs/enhancer_stage2` (**Reported**).[^resemble-enhance-readme]
- The data layout (clean speech mixed with non-speech background and RIR convolution) implies synthetic noisy/reverberant mixture generation; the README does not describe the mixing (**Synthesis**).[^resemble-enhance-readme]
- Whether stage 2 starts from stage-1 checkpoints, and how to load trained weights for the CLI, is not documented (**Unverified**).

## Evidence and trust

- The README contains no PESQ, STOI, SI-SDR, DNSMOS, or WER results, no RTF, and no comparisons. A demo video and a project webpage are linked but not captured (**Observed**).[^resemble-enhance-readme]
- Independent numbers exist elsewhere in the wiki: the [ClearVoice](clearvoice.md) README reports Resemble Enhance (resampled to 48 kHz for the test) at PESQ 2.84 on 48 kHz VoiceBank+DEMAND, behind `MossFormer2_SE_48K` (3.15) and DeepFilterNet (3.03), and SDR 4.06 versus DeepFilterNet's 15.79. Those are another vendor's self-reported results and not a verification of this tool (**Reported** by that source).
- Whether enhancement helps downstream ASR is contested; see [Speech Enhancement Before ASR](speech-enhancement-before-asr.md). This README offers no ASR evidence either way.
- License: the README has only a GitHub license badge, with no license name or text captured; the `LICENSE` file and the checkpoint terms are **Unverified**. Check them before commercial use.[^resemble-enhance-readme]

## Relationships

- Listed as an offline open enhancement option in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md); this page adds the tool's own documentation (**Synthesis**).[^resemble-enhance-readme]
- Compared in [ClearVoice](clearvoice.md)'s PESQ tables as a baseline; ClearVoice's six checkpoints cover enhancement, separation, and super-resolution (**Synthesis**).[^resemble-enhance-readme]
- Contrasts with [Facebook Denoiser](facebook-denoiser.md) and [Denoiser Live Streaming](denoiser-live-streaming.md): that model is causal and has a live mode, while Resemble Enhance documents only batch use (**Synthesis**).[^resemble-enhance-readme]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): neither this tool nor its README addresses echo cancellation (**Synthesis**).[^resemble-enhance-readme]

## Coverage and limits

- Ledger: the entry point `raw/ResembleEnhance.md` (README, 95 lines, undated, no revision) was read in full. Badge links (PyPI, Hugging Face Space, license, webpage), the demo video asset, `app.py`, `config/*.yaml`, the `resemble_enhance` package, the room-impulse-response repository, and the blog are external or not captured. Nothing was executed.
- All claims are vendor-reported and unreproduced. Model size, checkpoints, sample-rate handling at inference, VRAM, speed, and license are missing, which keeps the status at `draft`.

[^resemble-enhance-readme]: [resemble-ai/resemble-enhance README capture](../raw/ResembleEnhance.md) — locators: title and intro paragraph (two modules, 44.1 kHz training data); `Usage` › `Installation`, `Enhance`, `Denoise only`, `Web Demo`; `Train your own model` › `Data Preparation` (fg/bg/rir tree); `Training` › `Denoiser Warmup`, `Enhancer` › `Stage 1`, `Stage 2`; `Blog`; badge links (PyPI, Space, license, webpage).
