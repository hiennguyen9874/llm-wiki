---
type: Concept
title: Facebook Denoiser
description: CC-BY-NC causal waveform-domain speech enhancement model from Facebook Research (Interspeech 2020, Demucs-based) with dns48, dns64, and master64 checkpoints and training workflows, but no denoising-quality or ASR metrics in its README.
tags: [pipeline, speech-enhancement, denoising, waveform, demucs, real-time, cc-by-nc]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T12:00:00Z }
stale_after: 2027-10-13
sources:
  - id: denoiser-readme
    resource: ../raw/denoiser.md
    kind: documentation
    title: facebookresearch/denoiser README capture
---

Facebook Denoiser (the `denoiser` package from Facebook Research) is a causal speech-enhancement model that works on the raw waveform. It is an encoder-decoder with skip connections, adapted from the Demucs music-separation architecture, and trained with time- and frequency-domain losses plus waveform-level augmentation to remove stationary and non-stationary noise and room reverb. The README, the only captured artifact, claims real-time operation on a laptop CPU and documents pip, live, enhance, evaluate, and training entry points with three pretrained checkpoints. It reports no denoising-quality or ASR metrics, and its repository is CC-BY-NC 4.0, so commercial use needs a separate license decision (**Reported**; the commercial implication is **Synthesis**).[^denoiser-readme]

## Architecture and training objective

- Causal encoder-decoder on the raw waveform with skip connections, based on Demucs, which was originally proposed for music source separation. The figure's alt text names a convolutional encoder, an LSTM, and a transposed-convolution decoder (**Reported**).[^denoiser-readme]
- Optimized in both time and frequency domains with multiple loss functions. The README says the causal models used an STFT-loss weight of 0.1, not the 0.5 it attributes to the paper (see Contradictions) (**Reported**).[^denoiser-readme]
- Waveform-level data augmentation is claimed to improve performance and generalization (**Reported**).[^denoiser-readme]
- The architecture figure (`img/demucs.png`) is not in `raw/`; its content above comes only from alt text and prose.

## Checkpoints and entry points

| Checkpoint | Flag | Hidden size `H` | Training data |
|---|---|---:|---|
| `dns48` | `--dns48` | 48 | DNS |
| `dns64` | `--dns64` | 64 | DNS |
| `master64` | `--master64` | 64 | DNS and Valentini |

(**Reported**; the README labels all three "real time".)[^denoiser-readme]

- Install with `pip install denoiser`; the README recommends Python 3.7 (**Reported**).[^denoiser-readme]
- Enhance files with `python -m denoiser.enhance --dns64 --noisy_dir <in> --out_dir <out>`. For a local model, `--model_path` must point to a `best.th` file, not `checkpoint.th` (**Reported**).[^denoiser-readme]
- `--dry` mixes input and output (0 = input only, 1 = denoised only). Using it to trade residual noise against processing artifacts is **Synthesis**; the README gives only the knob's definition (**Reported**).[^denoiser-readme]
- `python -m denoiser.evaluate --data_dir <dir with noisy.json and clean.json>` computes PESQ unless `--no_pesq` is passed (**Observed** from the README's usage text).[^denoiser-readme]

## Training and reproduction

- Hydra-configured: defaults live in `conf/config.yaml`, dataset profiles in `conf/dset/` (for example `debug.yaml`), and options override on the command line, such as `./train.py demucs.hidden=32` (**Reported**).[^denoiser-readme]
- Dataset manifests come from `python -m denoiser.audio <folder> > noisy.json` (and `clean.json`), which list wav paths and lengths in frames (**Reported**).[^denoiser-readme]
- Experiment folders are named from command-line options. Rerunning resumes from `checkpoint.th` unless `restart=1` is passed (**Reported**).[^denoiser-readme]
- Outputs include `best.th`, `checkpoint.th`, `trainer.log`, and `history.json`; `./train.py ddp=1` enables distributed training (**Reported**).[^denoiser-readme]
- Fine-tuning starts from `continue_pretrained=dns48`, `dns64 demucs.hidden=64`, or `master64 demucs.hidden=64` (**Reported**).[^denoiser-readme]
- Paper reproduction uses the Valentini and DNS datasets. The launch scripts (`launch_valentini.sh`, `launch_valentini_nc.sh`, `launch_dns.sh`) and the DNS `interspeech2020` branch are referenced but not captured, so the reproduction path is **Unverified** (**Reported**).[^denoiser-readme]

## Evidence and benchmarks

- The README has no table of enhancement metrics (no PESQ, STOI, SI-SDR, or DNSMOS values) and no word-error results. The paper (arXiv:2006.12847) is linked but not captured (**Observed** from the README's absence).[^denoiser-readme]
- Quality claims are qualitative: removal of stationary and non-stationary background noise and of room reverb (**Reported**).[^denoiser-readme]
- Real-time CPU figures and their conditions are in [Denoiser Live Streaming](denoiser-live-streaming.md) (**Reported**).[^denoiser-readme]

## Licensing and provenance

- Repository license is CC-BY-NC 4.0 per the README's license section; the `LICENSE` file is not captured (**Reported**; **Unverified** against the file).[^denoiser-readme]
- `denoiser/stft_loss.py` is adapted from kan-bayashi/ParallelWaveGAN, and `scripts/matlab_eval.py` from santi-pdp/segan_pytorch; both adaptations are MIT (**Reported**).[^denoiser-readme]
- The README states no license or terms for the pretrained checkpoints (**Unverified**).
- No commit, release, or date is recorded. The 2020 citation and Python 3.7 instructions suggest the snapshot predates current tooling (**Synthesis**).[^denoiser-readme]

## Contradictions

- Paper versus causal training weight: the README says the paper states an STFT-loss weight of 0.5, while the causal models were trained with 0.1 ("unlike what we stated in the paper"). The paper is not captured, so its value is **Unverified** here; neither value is adopted (**Reported**).[^denoiser-readme]

## Relationships

- Related to [Speech Enhancement Before ASR](speech-enhancement-before-asr.md): a candidate causal enhancer for that concept's noise-preprocessing question, but the README reports no ASR effect (**Synthesis**).[^denoiser-readme]
- Related to [Denoiser Live Streaming](denoiser-live-streaming.md), which runs this model as a live loopback filter (**Synthesis**).[^denoiser-readme]
- Not the same model as HTDemucs in the [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md); [audio.cpp Framework](audio-cpp-framework.md) describes HTDemucs as six-stem separation (**Synthesis** from names and catalog descriptions).

## Coverage and limits

- Ledger: the entry point `raw/denoiser.md` (README) was read in full. Named but not captured: `conf/`, `train.py`, the `denoiser/` modules, `make_debug.sh`, `launch_*.sh`, `requirements*.txt`, and `LICENSE`. Figures `img/demucs.png` and `img/pavucontrol.png`, the arXiv paper, the Colab notebook, the samples page, and the demo video are external or absent. Nothing was executed.
- All numbers are vendor-reported and unreproduced. These gaps keep the status at `draft`.

[^denoiser-readme]: [facebookresearch/denoiser README capture](../raw/denoiser.md) — locators: title and intro paragraphs (paper, causal waveform model, noise and reverb claims, augmentation); `Installation` (pip, Python 3.7 note); `Live Speech Enhancement` › `Mac OS X` (Soundflower, pointer to model); `Training and evaluation` › `Configuration`, `Checkpointing`, `Setting up a new dataset`; `Usage` › `1. Data Structure`, `2. Training` (including `Fine tuning`), `3. Evaluating` (help text), `4. Denoising` (help text), `5. Reproduce Results` (Valentini and DNS steps, STFT-loss note); `Online Evaluation`; `Citation`; `License` (CC-BY-NC 4.0 and third-party adaptations); link references (arXiv 2006.12847, Demucs repository).
