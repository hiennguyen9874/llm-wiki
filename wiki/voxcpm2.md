---
type: Concept
title: VoxCPM2
description: 2B-parameter tokenizer-free diffusion-autoregressive multilingual TTS model with 30-language 48 kHz output, voice design, controllable and ultimate cloning, and ~0.3 RTF streaming on RTX 4090.
tags: [tts, multilingual, voice-cloning, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:27:56Z }
stale_after: 2027-10-06
sources:
  - id: voxcpm2-card
    resource: ../raw/VoxCPM2.md
    kind: documentation
    title: VoxCPM2 model card
---

VoxCPM2 is a 2B-parameter tokenizer-free diffusion-autoregressive multilingual text-to-speech model outputting 48 kHz audio across 30 languages, trained on over 2 million hours of multilingual speech, with reference-free voice design, controllable and ultimate voice cloning, context-aware prosody, real-time streaming at ~0.3 RTF on NVIDIA RTX 4090 (~0.13 with Nano-vLLM), and Apache-2.0 commercial-ready licensing (**Reported**).[^voxcpm2-card]

## Model identity and release

- Name is `VoxCPM2`; creator is the VoxCPM Team (OpenBMB); weights are `openbmb/VoxCPM2` on Hugging Face; inference library is `voxcpm` (`pip install voxcpm`); upstream links are the GitHub `OpenBMB/VoxCPM` repository, ReadTheDocs quick-start and fine-tuning guides, Hugging Face live playground, audio-samples demo page, Discord, Feishu group, and MiniCPM wiki (**Reported**).[^voxcpm2-card]
- Frontmatter declares `license: apache-2.0`, `library_name: voxcpm`, `pipeline_tag: text-to-speech`, 30 language codes (`zh, en, ar, my, da, nl, fi, fr, de, el, he, hi, id, it, ja, km, ko, lo, ms, no, pl, pt, ru, es, sw, sv, tl, th, tr, vi`), and tags including `text-to-speech`, `tts`, `multilingual`, `voice-cloning`, `voice-design`, `diffusion`, and `audio` (**Reported**, with frontmatter fields **Observed** by static inspection).[^voxcpm2-card]
- Paper lineage is `VoxCPM2: Tokenizer-Free TTS for Multilingual Speech Generation, Creative Voice Design, and True-to-Life Cloning` (VoxCPM Team, GitHub, 2026) and `VoxCPM: Tokenizer-Free TTS for Context-Aware Speech Generation and True-to-Life Voice Cloning` (`arXiv:2509.24650`, 2025) (**Reported**).[^voxcpm2-card]

## Architecture and training

- Architecture is tokenizer-free diffusion autoregressive: `LocEnc → TSLM → RALM → LocDiT`; backbone is based on MiniCPM-4, totalling 2B parameters (**Reported**).[^voxcpm2-card]
- Audio VAE is AudioVAE V2 with asymmetric encode/decode: accepts 16 kHz reference audio and outputs 48 kHz via built-in super-resolution, with no external upsampler needed (**Reported**).[^voxcpm2-card]
- Training data is 2M+ hours of multilingual speech; LM token rate is 6.25 Hz; max sequence length is 8192 tokens; dtype is `bfloat16`; VRAM is ~8 GB (**Reported**).[^voxcpm2-card]

## Supported languages

Arabic, Burmese, Chinese, Danish, Dutch, English, Finnish, French, German, Greek, Hebrew, Hindi, Indonesian, Italian, Japanese, Khmer, Korean, Lao, Malay, Norwegian, Polish, Portuguese, Russian, Spanish, Swahili, Swedish, Tagalog, Thai, Turkish, and Vietnamese — 30 languages with no language tag needed; Chinese dialects listed are 四川话, 粤语, 吴语, 东北话, 河南话, 陕西话, 山东话, 天津话, and 闽南话 (**Reported**).[^voxcpm2-card]

## Capabilities

- Voice Design generates a novel voice from a natural-language description alone with no reference audio (gender, age, tone, emotion, pace); usage puts the description in parentheses at the start of `text`, e.g. `(A young woman, gentle and sweet voice)Hello, welcome to VoxCPM2!` (**Reported**).[^voxcpm2-card]
- Controllable Cloning clones any voice from a short `reference_wav_path` clip, with optional inline style guidance in parentheses to steer emotion, pace, and expression while preserving timbre, e.g. `(slightly faster, cheerful tone)` (**Reported**).[^voxcpm2-card]
- Ultimate Cloning provides reference audio plus its exact transcript for audio-continuation cloning; passing the same clip to both `reference_wav_path` and `prompt_wav_path` with `prompt_text` gives highest similarity and reproduces vocal nuance (**Reported**).[^voxcpm2-card]
- Context-Aware Synthesis automatically infers prosody and expressiveness from text content (**Reported**).[^voxcpm2-card]
- Real-Time Streaming synthesizes via `generate_streaming` chunk iteration (concatenated with `numpy.concatenate` in the example); RTF is ~0.3 on NVIDIA RTX 4090, and ~0.13 accelerated by Nano-vLLM (**Reported**).[^voxcpm2-card]

## Performance and evaluation

- Source claims state-of-the-art or competitive results on zero-shot and controllable TTS benchmarks; full benchmark tables (Seed-TTS-eval, CV3-eval, InstructTTSEval, MiniMax Multilingual Test) are deferred to the GitHub repository and are not reproduced in the source (**Reported**).[^voxcpm2-card]

## Requirements and inference usage

- Requires Python ≥ 3.10, PyTorch ≥ 2.5.0, and CUDA ≥ 12.0; install with `pip install voxcpm` (**Reported**).[^voxcpm2-card]
- Basic TTS loads `VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)` and calls `model.generate` with `cfg_value=2.0` and `inference_timesteps=10`, writing output with `soundfile.write` at `model.tts_model.sample_rate` (**Reported**).[^voxcpm2-card]
- Voice-design and controllable-cloning examples reuse the same `cfg_value=2.0` and `inference_timesteps=10` defaults; basic cloning omits those arguments and passes only `text` plus `reference_wav_path` (**Reported**).[^voxcpm2-card]

## Fine-tuning

- Supports full SFT and LoRA fine-tuning with as little as 5–10 minutes of audio via `python scripts/train_voxcpm_finetune.py` with `--config_path conf/voxcpm_v2/voxcpm_finetune_lora.yaml` (LoRA, recommended) or `conf/voxcpm_v2/voxcpm_finetune_all.yaml` (full); full instructions are in the fine-tuning guide (**Reported**).[^voxcpm2-card]

## Limitations and responsible use

- Voice Design and Style Control results may vary between runs; generating 1–3 times is recommended to obtain the desired output (**Reported**).[^voxcpm2-card]
- Performance varies across languages with training-data availability; occasional instability may occur with very long or highly expressive inputs (**Reported**).[^voxcpm2-card]
- Use for impersonation, fraud, or disinformation is strictly forbidden; AI-generated content should be clearly labeled; production deployments need thorough testing and safety evaluation tailored to the use case (**Reported**).[^voxcpm2-card]

## License

- Released under Apache-2.0, free for commercial use (**Reported**).[^voxcpm2-card]

## Relationships

- Baseline comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) evaluates VoxCPM2 (2.3B main-model parameters excluding AudioVAE) as a baseline on Seed-TTS and CV3 tables, while this concept covers the VoxCPM2 model card itself (2B total, 30 languages, AudioVAE V2, voice design and cloning modes); no shared codebase is asserted (**Synthesis**).[^voxcpm2-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice design/direction and H100 TTFA/RTF figures, while this concept covers a 30-language diffusion-autoregressive TTS model with parenthetical voice-design/style syntax and RTX 4090 RTF figures; no shared vendor or codebase is asserted (**Synthesis**).[^voxcpm2-card]
- Streaming TTS comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B LLM-based streaming TTS model with zero-shot/cross-lingual/instruct modes and vLLM support, while this concept covers a 2B diffusion-autoregressive streaming TTS model with `generate_streaming` and Nano-vLLM acceleration; no shared codebase is asserted (**Synthesis**).[^voxcpm2-card]

- Predecessor: [VoxCPM-0.5B](voxcpm-0.5b.md) covers the 0.5B bilingual predecessor with continuous-space generation, 16 kHz output, WeTextProcessing normalization, and Seed-TTS/CV3 benchmark tables, while this concept covers the 2B 30-language successor with voice design and controllable/ultimate cloning; neither concept is marked deprecated (**Synthesis**).[^voxcpm2-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no RTF, VRAM, language-coverage, voice-design, cloning-fidelity, or benchmark claims reproduced (**Synthesis**).[^voxcpm2-card]
- GitHub repository, ReadTheDocs quick-start and fine-tuning guides, live playground, audio-samples page, Discord/Feishu/MiniCPM community links, and Nano-vLLM accelerator were linked but not fetched and are not in `raw/`; checkpoint, denoiser, AudioVAE V2 weights, reference-audio files, and fine-tuning scripts/configs were listed but not present in `raw/` and were not inspected (**Synthesis**).[^voxcpm2-card]
- All identity, architecture, training-scale, language-coverage, capability, latency, memory, compatibility, and usage claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^voxcpm2-card]

[^voxcpm2-card]: [VoxCPM2 model card](../raw/VoxCPM2.md) — locators: frontmatter (`language` 30-code list, `license`, `library_name`, `pipeline_tag`, `tags`); intro paragraph (tokenizer-free diffusion autoregressive, 2B, 30 languages, 48 kHz, 2M+ hours); `Highlights` section (8 bullets: multilingual no-tag, voice design, controllable cloning, ultimate cloning, 48 kHz super-resolution, context-aware prosody, RTF 0.3/0.13 streaming, Apache-2.0); `Supported Languages` collapsible (30-language list plus 9 Chinese dialects); `Quick Start / Installation` section (`pip install voxcpm`, Python ≥ 3.10 / PyTorch ≥ 2.5.0 / CUDA ≥ 12.0); `Text-to-Speech`, `Voice Design`, `Controllable Voice Cloning`, `Ultimate Cloning`, and `Streaming` subsections (5 Python fences with `from_pretrained`, `cfg_value`, `inference_timesteps`, `reference_wav_path`/`prompt_wav_path`/`prompt_text`, `generate_streaming`); `Model Details` table (architecture chain, MiniCPM-4 2B backbone, AudioVAE V2 16→48 kHz, 2M+ hours, 6.25 Hz, 8192 tokens, bfloat16, ~8 GB VRAM, RTF rows); `Performance` section (SOTA/competitive claim plus 4-benchmark pointer); `Fine-tuning` section (SFT/LoRA, 5–10 min audio, 2 `train_voxcpm_finetune.py` fences); `Limitations` section (4 bullets); `Citation` section (2026 VoxCPM2 and 2025 `arXiv:2509.24650` BibTeX); `License` section (Apache-2.0 commercial-use plus safety-testing sentence).
