---
type: Concept
title: OmniVoice
description: Massively multilingual zero-shot TTS model covering 600+ languages with diffusion language-model architecture, voice cloning and voice design, and 0.025 RTF.
tags: [ml, tts, multilingual, voice-cloning, zero-shot]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: omnivoice-card
    resource: ../raw/OmniVoice.md
    kind: documentation
    title: OmniVoice model card
---

OmniVoice is a massively multilingual zero-shot text-to-speech model supporting over 600 languages, built on a diffusion language-model-style architecture for high-quality speech at up to 40x faster than real time, with zero-shot voice cloning from a short reference clip and attribute-driven voice design (**Reported**).[^omnivoice-card]

## Model identity and release

- Title is `OmniVoice`; model ID is `k2-fsa/OmniVoice` on Hugging Face; inference library is `omnivoice` (`library_name: omnivoice`, `pipeline_tag: text-to-speech`); frontmatter declares `base_model: Qwen/Qwen3-0.6B` and tags `zero-shot`, `multilingual`, `voice-cloning`, and `voice-design`, with a `language` list of 600+ codes (**Reported**).[^omnivoice-card]
- Paper is `OmniVoice: Towards Omnilingual Zero-Shot Text-to-Speech with Diffusion Language Models` by Zhu, Ye, Kang, Yao, Guo, Kuang, Han, Zhuang, Lin, and Povey, arXiv `2604.00688` (2026); linked artifacts are the Hugging Face model page, Hugging Face Space demo, GitHub repository `k2-fsa/OmniVoice`, project demo page, and a Colab notebook (**Reported**).[^omnivoice-card]
- Code is released under Apache 2.0; the pre-trained model is licensed under CC-BY-NC, attributed to training-data constraints (e.g. Emilia) (**Reported**).[^omnivoice-card]

## Capabilities

- 600+ languages supported, described as the broadest language coverage among zero-shot TTS models (**Reported**).[^omnivoice-card]
- Voice cloning produces high-quality cloned speech from a short reference audio plus its transcription, characterized in the card as state-of-the-art cloning quality (**Reported**).[^omnivoice-card]
- Voice design controls voices via assigned speaker attributes such as gender, age, pitch, dialect/accent, and whisper without requiring reference audio (**Reported**).[^omnivoice-card]
- Fine-grained control supports non-verbal symbols such as `[laughter]` and pronunciation correction via pinyin or phonemes (**Reported**).[^omnivoice-card]
- Diffusion language-model-style architecture is described as clean, streamlined, and scalable, delivering both quality and speed (**Reported**).[^omnivoice-card]

## Performance

- Real-time factor as low as 0.025, i.e. approximately 40x faster than real time (**Reported**).[^omnivoice-card]

## Requirements and installation

- Card recommends a fresh virtual environment (`conda`, `venv`, etc.) to avoid conflicts (**Reported**).[^omnivoice-card]
- NVIDIA GPU setup installs a CUDA-matched PyTorch build, e.g. `pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128`; Apple Silicon setup installs `pip install torch==2.8.0 torchaudio==2.8.0`; then `pip install omnivoice` (**Reported**).[^omnivoice-card]

## Inference usage

- Zero-shot voice cloning loads the model with `OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)`, calls `model.generate(text=..., ref_audio="ref.wav", ref_text="...")`, and receives a list of `np.ndarray` waveforms at 24 kHz, writable with `sf.write("out.wav", audio[0], 24000)` (**Reported**).[^omnivoice-card]
- Further generation modes (e.g. voice design), functions (non-verbal symbols, pronunciation correction), and comprehensive usage are delegated to the upstream GitHub repository rather than detailed in the card (**Reported**).[^omnivoice-card]

## Limitations and responsible use

- Users are prohibited from unauthorized voice cloning, voice impersonation, fraud, scams, or other illegal or unethical uses; users must comply with applicable laws, regulations, and ethical standards; developers disclaim liability for misuse and advocate responsible AI use (**Reported**).[^omnivoice-card]
- Discussion channel is GitHub Issues, plus a WeChat group and official account via QR codes (**Reported**).[^omnivoice-card]

## Relationships

- Multilingual zero-shot TTS comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a compact 0.6B DualAR multilingual cloning model with 11 recommended languages and Seed-TTS numbers, while this concept covers a 600+-language diffusion-LM cloning/design model with 0.025 RTF; no shared codebase or vendor claim is asserted (**Synthesis**).[^omnivoice-card]
- Bilingual real-time TTS contrast: [Breeze TTS 2](breeze-tts-2.md) covers an English-Chinese real-time model with voice clone/design/direction and H100 TTFA/RTF figures, while this concept covers massively multilingual coverage and attribute-driven voice design; no shared codebase or vendor claim is asserted (**Synthesis**).[^omnivoice-card]
- LLM-based streaming TTS family: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) and [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md) cover 0.5B-parameter multilingual zero-shot TTS models with streaming and pronunciation-control features, while this concept covers a Qwen3-0.6B-based diffusion-LM model at 600+-language scale; no shared codebase claim is asserted beyond the comparable voice-cloning role (**Synthesis**).[^omnivoice-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no language-count, cloning-quality, voice-design, or RTF claims reproduced (**Synthesis**).[^omnivoice-card]
- Hugging Face model page and Space, paper page, GitHub repository, demo page, Colab notebook, PyTorch install indexes, and WeChat QR images were linked but not fetched and were not present in `raw/`; checkpoint contents, reference-audio files, and voice-design attribute schema were not inspected (**Synthesis**).[^omnivoice-card]
- All identity, language-coverage, capability, speed, compatibility, and usage claims are source assertions without independent verification in this wiki; model-release and speed figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^omnivoice-card]

[^omnivoice-card]: [OmniVoice model card](../raw/OmniVoice.md) — locators: frontmatter (`base_model`, `language`, `pipeline_tag`, `library_name`, `tags`); header badges/links (Hugging Face model/Space, arXiv paper 2604.00688, GitHub repo, demo page, Colab badge); intro paragraph (600+ languages, diffusion language-model architecture, cloning/design, speed); `Key Features` section (600+ languages, cloning, voice-design attributes, `[laughter]`/pinyin/phoneme control, RTF 0.025, architecture bullets); `Usage` section (fresh-venv note, NVIDIA-GPU and Apple-Silicon `pip install torch/torchaudio` fences, `pip install omnivoice` fence, Python `from_pretrained`/`generate` fence with `device_map`/`dtype`/`ref_audio`/`ref_text`/24 kHz, GitHub pointer); `Discussion & Communication` section (GitHub Issues, WeChat table); `Citation` section (Zhu et al. 2026 bibtex); `License` section (Apache 2.0 code, CC-BY-NC model, Emilia note); `Disclaimer` section (misuse prohibition, compliance, liability).
