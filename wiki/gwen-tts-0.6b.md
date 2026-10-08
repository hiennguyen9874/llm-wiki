---
type: Concept
title: Gwen-TTS 0.6B
description: Vietnamese-optimized Qwen3-TTS-0.6B-Base finetune for zero-shot voice cloning trained on about 1,000 hours of Vietnamese audio, with eleven listed languages, nine demo voices, and no published benchmarks or streaming figures.
tags: [tts, vietnamese, voice-cloning, zero-shot]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-08T12:00:00Z }
stale_after: 2027-10-07
sources:
  - id: gwen-tts-card
    resource: ../raw/gwen-tts-0.6B.md
    kind: documentation
    title: Gwen-TTS 0.6B model card
  - id: gwen-tts-repo
    resource: ../raw/gwen-tts/README.md
    scope: ../raw/gwen-tts/
    kind: code
    revision: f0f24d8636596dc635323e02f41bee42bb64385e
    title: ggroup-ai-lab/gwen-tts repository snapshot
---

Gwen-TTS 0.6B is a Vietnamese-optimized text-to-speech model by G-Group AI Lab, fine-tuned from `Qwen/Qwen3-TTS-12Hz-0.6B-Base` on roughly 1,000 hours of Vietnamese audio crawled from TikTok, offering zero-shot voice cloning from a short reference clip plus its transcript with a vendor-recommended sampling configuration (**Reported**).[^gwen-tts-card]

## Model identity and lineage

- Title is `Gwen-TTS 0.6B - Natural Vietnamese Voice Cloning`; model ID is `g-group-ai-lab/gwen-tts-0.6B` on Hugging Face; card frontmatter declares `base_model` of `Qwen/Qwen3-TTS-12Hz-0.6B-Base`, `pipeline_tag: text-to-speech`, `license: mit`, `language` codes `vi, zh, en, ja, ko, fr, de, it, pt, ru, es`, and tags `tts`, `voice-cloning`, `vietnamese`, `gwen-tts`, `qwen3-tts`, and `speech-synthesis` (**Reported**, frontmatter presence **Observed**).[^gwen-tts-card]
- Stated contribution is natural and expressive Vietnamese voice cloning, cloning any voice from a few seconds of reference audio (**Reported**).[^gwen-tts-card]
- Frontmatter names `library_name: transformers`, while the usage section installs and imports the `qwen-tts` package (`from qwen_tts import Qwen3TTSModel`); the card does not explain the two names (**Observed**).[^gwen-tts-card]

## Training data

- Fine-tuned on approximately 1,000 hours of Vietnamese audio data crawled from TikTok (**Reported**).[^gwen-tts-card]
- The card states no collection method, filtering, consent, split, training hyperparameters, or evaluation protocol beyond the data volume (**Observed** absence).[^gwen-tts-card]

## Capabilities and inference usage

- Zero-shot voice cloning via `model.generate_voice_clone(text=..., language="Vietnamese", ref_audio="<path/to/reference.wav>", ref_text="<transcript of the reference audio>", **generation_config)`, taking target text, a reference waveform, and the reference transcript (**Reported**).[^gwen-tts-card]
- Recommended generation configuration: `temperature=0.3`, `top_k=20`, `top_p=0.9`, `max_new_tokens=4096`, `repetition_penalty=2.0`, `subtalker_do_sample=True`, `subtalker_temperature=0.1`, `subtalker_top_k=20`, `subtalker_top_p=1.0` (**Reported**).[^gwen-tts-card]
- Loading path: `Qwen3TTSModel.from_pretrained("g-group-ai-lab/gwen-tts-0.6B", device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="flash_attention_2")`, returning `(wavs, sr)` writable with `sf.write("output.wav", wavs[0], sr)`; installation is `pip install -U qwen-tts` with optional `pip install -U flash-attn --no-build-isolation` for optimized performance (**Reported**).[^gwen-tts-card]
- Practical synthesis tips: apply TTS text normalization (numbers, symbols, abbreviations) proactively and split input into chunks before passing text to the model (**Reported**).[^gwen-tts-card]
- The `generate_voice_clone` examples return complete waveforms; the card states no time-to-first-audio, streaming, concurrency, VRAM, or CPU/edge figures (**Observed** absence).[^gwen-tts-card]

## Repository, installation, and CLI

- Repository snapshot `f0f24d8` (commit dated 2026-04-03, origin `ggroup-ai-lab/gwen-tts`) is MIT per `pyproject.toml`, version `0.1.0`, `requires-python >=3.11`; dependencies are `qwen-tts>=0.1.1`, `torch>=2.5.0`, `torchaudio>=2.5.0`, `soundfile`, `numpy`, with torch/torchaudio pinned to the `pytorch-cu124` index (**Observed**).[^gwen-tts-repo]
- README states a tested environment of Python 3.11, CUDA 12.4, NVIDIA driver ≥ 550.54, and VRAM ≥ 4 GB; install is `uv sync --python 3.11` plus `flash-attn --no-build-isolation`. The 4 GB figure is a stated minimum for the tested environment, not a measured footprint (**Reported**).[^gwen-tts-repo]
- `inference.py` CLI: `--text`, `--speaker` (built-in key), `--ref_audio` with mandatory `--ref_text`, `--model_path` (default `g-group-ai-lab/gwen-tts-0.6B`), `--output` (default `output.wav`), `--device` (default `cuda:0`), `--list_speakers`. It loads in bfloat16, writes one complete WAV, and has no streaming path (**Observed**).[^gwen-tts-repo]
- The CLI falls back to `sdpa` attention when `flash_attn` fails to import, unlike the card's hard-coded `flash_attention_2` (**Observed**).[^gwen-tts-repo]
- Code/doc discrepancy: the README example passes `language="Vietnamese"`, but `generate_voice_clone` in `inference.py` has `# language=language` commented out, so the CLI `--language` option has no effect and language is not passed to the model. Whether the API requires or ignores it was not tested (**Observed**, effect **Unverified**).[^gwen-tts-repo]
- Sampling configuration in `GENERATION_CONFIG` matches the card's recommended values exactly (**Observed**).[^gwen-tts-repo]
- `data/ref_info.json` maps nine speaker keys to `name`, `audio_path`, and reference `text`; `data/infer_info.json` holds the generated-clip scripts. `.gitignore` excludes `*.safetensors` (weights stay on Hugging Face) and `output*.wav` (**Observed**).[^gwen-tts-repo]

## Voice samples

- The card publishes nine demo voices, each pairing a reference clip with a generated inference clip hosted under `https://huggingface.co/g-group-ai-lab/gwen-tts-0.6B/resolve/main/data/` (`ref_audio/` plus `infer-audio/`): `yen_nhi`, `my_van`, `ai_vy`, `an_nhi`, `dieu_linh`, `khanh_toan`, `tran_lam`, `nsnd_ha_phuong`, and `nsnd_kim_cuc` (**Reported**, URL pattern **Observed**).[^gwen-tts-card]
- Inference transcripts span telesales patter, economic-news reading, tech-product review, and sleep-time narration styles, illustrating expressive range; transcripts are demo content, not quality measurements, and are not reproduced here (**Synthesis**).[^gwen-tts-card]
- The repository snapshot contains 9 reference and 9 inference WAV files (`data/ref_audio/` and `data/infer-audio/`) plus an extra unreferenced `ref_audio/tao_thao.wav`; the clips were not played or measured, so clone quality and speaker similarity remain unverified (**Observed** file presence, quality **Unverified**).[^gwen-tts-repo]
- Several inference clips reuse one script across different reference voices, and the ref_info lists only built-in speakers, so the demo set shows voice transfer, not multi-text coverage (**Synthesis**).[^gwen-tts-repo]

## Languages

- Vietnamese is the primary and optimized language; Chinese, English, Japanese, Korean, French, German, Italian, Portuguese, Russian, and Spanish are also listed (**Reported**).[^gwen-tts-card]
- Performance on non-Vietnamese languages may differ from the base Qwen3-TTS model, with no per-language figures stated (**Reported**).[^gwen-tts-card]

## Demo and repository

- Live demo at `https://g-voice.g-ailab.com/tts`, described as integrated with TTS text normalization and serving; source repository at `https://github.com/ggroup-ai-lab/gwen-tts` (**Reported**).[^gwen-tts-card]
- The README notes the demo adds TTS text normalization and serving; the repository ships neither normalization code nor a server, only `inference.py` (**Observed**).[^gwen-tts-repo]
- The live demo was not inspected (**Synthesis**).[^gwen-tts-card]

## Licensing

- Card frontmatter and `## License` section state the MIT License, with a `LICENSE` link target that is not in `raw/` (**Reported**).[^gwen-tts-card]
- Commercial usability also depends on the Qwen3-TTS base lineage and the TikTok-crawled training data, whose consent and rights are undisclosed in this capture; neither question is resolved here (**Synthesis**).[^gwen-tts-card]

## Citation and acknowledgments

- Card supplies one BibTeX entry, `gwen-tts` (G-Group AI Lab, 2026, GitHub URL) (**Reported**).[^gwen-tts-card]
- Acknowledged parties: the Qwen Team (Qwen3-TTS base model) and G-Group AI Lab (training and release) (**Reported**).[^gwen-tts-card]

## Relationships

- Finetuned from the Qwen3-TTS 0.6B Base checkpoint [Qwen3-TTS-12Hz-0.6B-Base](qwen3-tts-12hz-0.6b-base.md), whose cloning API this finetune reuses, and covered alongside the preset-timbre [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md) (same 0.6B scale and `qwen-tts` plus FlashAttention 2 loading path, 10 official languages without Vietnamese, 97 ms serving-layer streaming claim); this concept covers the Vietnamese-specialized Base finetune with a fixed sampling configuration and no streaming or latency evidence (**Synthesis**).[^gwen-tts-card]
- Same-lab sibling [G-OmniVoice](g-omnivoice.md) covers the other G-Group AI Lab Vietnamese finetune (OmniVoice lineage, 3–10 s cloning plus attribute voice design, vendor-reported held-out WER 0.0259 / SIM 0.890 / MOS 7.685); this concept carries no numeric benchmark table (**Synthesis**).[^gwen-tts-card]
- Vietnamese deployment comparison: [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) covers the dedicated Vietnamese on-device family (48 kHz, preset voices, frame-level streaming, RTX 3060/CPU latency tables), while this concept covers a Base-lineage Vietnamese finetune with demo clips but no streaming, latency, or benchmark evidence; no shared codebase is asserted (**Synthesis**).[^gwen-tts-card]
- Included by [TTS Model Survey](tts-model-survey.md) as a Vietnamese-finetuned catalog row and by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as a cloning candidate pending benchmarks, streaming, and data-rights checks (**Synthesis**).[^gwen-tts-card]

## Coverage and limits

- Sources inspected statically only: the model-card capture and the repository snapshot (README, `pyproject.toml`, `inference.py`, `data/*.json`, `.gitignore`; audio WAVs listed but not decoded; `.git` metadata used only for revision/remote); no package installed, no checkpoint downloaded, no audio synthesized, and no cloning-quality, language-coverage, or usage claim reproduced (**Synthesis**).[^gwen-tts-card]
- Unavailable or uninspected artifacts: Hugging Face checkpoint and weights, `LICENSE` text, live demo, audio clip content, training dataset, and linked Qwen3-TTS base pages were not in `raw/` and were not fetched (**Synthesis**).[^gwen-tts-card]
- No numeric benchmark (WER, CER, SIM, MOS), latency, throughput, or VRAM figure appears in the capture; quality comparisons against any baseline are therefore unestablished (**Synthesis**).[^gwen-tts-card]
- All identity, training-data, capability, usage, language, demo, and licensing claims are source assertions without independent verification in this wiki; model-release figures carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^gwen-tts-card]

[^gwen-tts-repo]: [ggroup-ai-lab/gwen-tts snapshot](../raw/gwen-tts/README.md) at revision `f0f24d8636596dc635323e02f41bee42bb64385e` — locators: `README.md` `## Installation` (tested environment), `## Quick Start` (Python API, CLI); `pyproject.toml` `[project]` and `[tool.uv.*]`; `inference.py::GENERATION_CONFIG`, `::load_model` (sdpa fallback), `::generate_voice_clone` (`# language=language`), `::main` (argparse); `data/ref_info.json`, `data/infer_info.json`; `data/ref_audio/`, `data/infer-audio/`; `.gitignore`. Excluded: `.git` packfiles and hooks (VCS internals).

[^gwen-tts-card]: [Gwen-TTS 0.6B model card](../raw/gwen-tts-0.6B.md) — locators: frontmatter (`library_name: transformers`, `license: mit`, `language` 11 codes, `pipeline_tag: text-to-speech`, `tags`, `base_model: Qwen/Qwen3-TTS-12Hz-0.6B-Base`); intro plus `Key highlights` bullets (voice cloning from a few seconds of reference, natural expressive Vietnamese, ~1,000 h TikTok-crawled finetune data); `Demo` and `GitHub` link lines; `## How to Use` (`pip install -U qwen-tts`, optional `flash-attn`, normalization-plus-chunking note, `Qwen3TTSModel.from_pretrained` fence with `device_map`/`dtype`/`attn_implementation`, full `generation_config` dict, `generate_voice_clone` fence with `language="Vietnamese"`/`ref_audio`/`ref_text`, `sf.write` line); `## Voice Samples` (9 speaker tables with `yen_nhi`, `my_van`, `ai_vy`, `an_nhi`, `dieu_linh`, `khanh_toan`, `tran_lam`, `nsnd_ha_phuong`, `nsnd_kim_cuc`, `ref_audio/` plus `infer-audio/` audio URLs and transcripts); `## Supported Languages` (Vietnamese primary, 10 others, non-Vietnamese performance caveat); `## Citation` (gwen-tts 2026 bibtex); `## License` (MIT); `## Acknowledgments` (Qwen Team, G-Group AI Lab).
