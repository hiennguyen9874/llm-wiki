---
type: Concept
title: dots.tts-soar
description: 2B-parameter continuous autoregressive TTS checkpoint with Self-corrective Alignment for highest zero-shot fidelity and speaker similarity at 48 kHz.
tags: [tts, voice-cloning, autoregressive, flow-matching]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: dots-tts-soar-card
    resource: ../raw/dots.tts-soar.md
    kind: documentation
    title: dots.tts-soar model card
---

dots.tts-soar is the 2B-parameter fully continuous end-to-end autoregressive text-to-speech checkpoint in the dots.tts family, pairing a semantic encoder, an LLM, and an autoregressive flow-matching head over a 48 kHz AudioVAE with no discrete codec tokens, refined from `dots.tts-base` with reward-free Self-corrective Alignment (SCA) for the highest zero-shot fidelity and speaker similarity of the three releases, making it the recommended default for production zero-shot voice cloning and a recommended fine-tuning starting point (**Reported**).[^dots-tts-soar-card]

## Model identity and release

- Full system name is `dots.tts` (2B parameters); this repository hosts `dots.tts-soar`, the pretrained backbone further refined with SCA; base model declared in frontmatter is `dots-studio/dots.tts-base`; weights are `dots-studio/dots.tts-soar` on Hugging Face; inference library is `dots_tts` (`library_name: dots_tts`); upstream links are the `studio-dots-ai/dots.tts` GitHub repository, Hugging Face Spaces playground, and live demo page (**Reported**, with frontmatter `base_model`/`library_name` **Observed** by static inspection).[^dots-tts-soar-card]
- Frontmatter declares `license: apache-2.0`, `pipeline_tag: text-to-speech`, `base_model: dots-studio/dots.tts-base`, and tags including `text-to-speech`, `tts`, `voice-cloning`, `autoregressive`, `flow-matching`, and `post-trained` (**Observed** by static inspection).[^dots-tts-soar-card]
- Family table lists three checkpoints: `dots.tts-base` (pretrain ~1.5M h; fine-tuning with full CFG/NFE control), `dots.tts-soar` (this checkpoint; + Self-corrective Alignment; highest zero-shot fidelity and speaker similarity; also recommended for fine-tuning), and `dots.tts-mf` (+ MeanFlow distillation; few-step inference NFE=4, low latency) (**Reported**).[^dots-tts-soar-card]

## Architecture

- Backbone pairs a semantic encoder, an LLM, and an autoregressive flow-matching acoustic head over a 48 kHz AudioVAE, with no discrete codec tokens anywhere in the pipeline (**Reported**).[^dots-tts-soar-card]
- Frozen AudioVAE encodes 48 kHz mono waveform into a continuous latent and decodes via a BigVGAN-style causal decoder; the autoregressive backbone predicts that latent one patch at a time (**Reported**).[^dots-tts-soar-card]
- Semantic encoder re-encodes each newly generated VAE patch into a compact embedding for the LLM, stripping high-variance acoustic detail; LLM is initialized from `Qwen2.5-1.5B-Base`, consumes BPE text directly with no phonemes, and emits one hidden state per audio step; AR flow-matching head is a DiT conditioning on the LLM hidden state and AR prefix to denoise the next VAE patch, with a frozen CAM++ speaker x-vector as side input (**Reported**).[^dots-tts-soar-card]
- Self-corrective Alignment is a reward-free, flow-matching-native post-training stage applied on top of `dots.tts-base`; it improves text and speaker adherence without changing inference cost or sampling schedule (**Reported**).[^dots-tts-soar-card]

## Requirements and inference usage

- Install creates a `python=3.10` conda env (`dots_tts`), upgrades pip, and installs `git+https://github.com/studio-dots-ai/dots.tts.git` constrained by `constraints/recommended.txt` (**Reported**).[^dots-tts-soar-card]
- CLI continuation voice cloning (reference audio + transcript, recommended) passes `--model-name-or-path dots-studio/dots.tts-soar` with `--text`, `--prompt-audio`, `--prompt-text` (exact transcript of the reference audio), and `--output` (**Reported**).[^dots-tts-soar-card]
- Python API loads `DotsTtsRuntime.from_pretrained("dots-studio/dots.tts-soar", precision="bfloat16")` and calls `runtime.generate` with `text`, `prompt_audio_path`, `prompt_text`, `num_steps=10`, and `guidance_scale=1.2`, writing `result["audio"]` with `soundfile` at `result["sample_rate"]` (**Reported**).[^dots-tts-soar-card]

## Recommended sampling settings

- `--num-steps` (flow-matching sampling steps) `10`–`32`; higher means better quality and slower inference (**Reported**).[^dots-tts-soar-card]
- `--guidance-scale` `1.2` (default standard CFG); SCA already tightens text and timbre adherence so small CFG suffices (**Reported**).[^dots-tts-soar-card]

## Fine-tuning

- Both `dots.tts-base` and `dots.tts-soar` are valid fine-tuning starting points; pick `dots.tts-soar` to inherit its tightened text/timbre alignment on top of the pretrained backbone (**Reported**).[^dots-tts-soar-card]
- Training entry points are `scripts/train_dots_tts.py` and smoke config `configs/dots_tts.yaml` in the source repository, launched via `accelerate launch scripts/train_dots_tts.py --config configs/dots_tts.yaml` (**Reported**).[^dots-tts-soar-card]

## Performance and evaluation

- Seed-TTS-Eval reports state-of-the-art average SIM 79.2 (zero-shot): Seed-TTS averages 3.65/77.8 (test-en 2.25/76.2, test-zh 1.12/79.6, test-zh-hard 7.59/77.6); Qwen3-TTS 1.7B averages 3.07/74.5 (1.23/71.7, 1.22/77.0, 6.76/74.8); VoxCPM 2 averages 3.65/76.7 (1.84/75.3, 0.97/79.5, 8.13/75.3); `dots.tts-base` averages 2.92/78.8 (1.34/76.8, 0.96/80.5, 6.46/79.2); `dots.tts-soar` averages 2.95/79.2 (test-en 1.30/77.1, test-zh 0.94/81.0, test-zh-hard 6.60/79.5) — metrics are WER↓/SIM↑ (**Reported**).[^dots-tts-soar-card]
- MiniMax Multilingual reports the highest average SIM 83.9 across 24 languages: MiniMax 2.8/76.6, Fish-Audio S2 3.7/78.0, VoxCPM 2 5.7/82.3, `dots.tts-base` 6.6/83.5, `dots.tts-soar` 6.8/83.9 — metrics are Avg WER↓/Avg SIM↑ (**Reported**).[^dots-tts-soar-card]
- CV3-Eval reports the lead on both cross-lingual SIM subsets: CosyVoice 3 (1.5B) en→zh 66.9 and zh→en 66.4; `dots.tts-base` 74.6 and 71.9; `dots.tts-soar` 75.0 and 72.8 (**Reported**).[^dots-tts-soar-card]
- EmergentTTS-Eval head-to-head judging vs. `gpt-4o-mini-tts` posts 65.7% on Syntactic Complexity — above every closed-source system listed — while keeping competitive Emotions/Questions scores (**Reported**).[^dots-tts-soar-card]
- Full benchmark tables including the complete MiniMax Multilingual and EmergentTTS-Eval breakdowns are deferred to the project README and are not reproduced in this source (**Reported**).[^dots-tts-soar-card]

## Limitations and responsible use

- High-fidelity zero-shot voice cloning can produce highly realistic synthetic speech; intended for research and authorized deployment; do not use for impersonation, fraud, or disinformation; combine downstream use with consent-aware reference-audio policies, synthetic-speech detection, content watermarking, and clear AI-generated labeling (**Reported**).[^dots-tts-soar-card]
- BPE backbone inherits the text LLM's language coverage at the cost of higher data appetite: on script-divergent and under-represented languages (Arabic, Hindi, Turkish, Vietnamese) WER is higher than on high-resource languages while speaker similarity is preserved (**Reported**).[^dots-tts-soar-card]
- Backbone is trained on a speech-heavy mixture; singing and unified speech-plus-sound generation are not covered (**Reported**).[^dots-tts-soar-card]

## License and citation

- Released under Apache-2.0 (**Reported**).[^dots-tts-soar-card]
- Citation is `dotstts2026`, `dots.tts Technical Report`, dots.tts Team, arXiv preprint 2026 (**Reported**).[^dots-tts-soar-card]

## Relationships

- Distilled variant: [dots.tts-mf](dots-tts-mf.md) covers the CFG-aware MeanFlow distillation of `dots.tts-soar` for few-step (NFE=4) low-latency inference, while this concept covers the SCA-refined teacher recommended for highest zero-shot fidelity (**Synthesis**).[^dots-tts-soar-card]
- Continuous-tokenizer TTS comparison: [VoxCPM2](voxcpm2.md) covers a 2B tokenizer-free diffusion-autoregressive 48 kHz multilingual TTS model with voice design and controllable/ultimate cloning, while this concept covers a 2B fully continuous (no codec tokens) AR flow-matching 48 kHz TTS family with SCA post-training; no shared vendor or codebase is asserted (**Synthesis**).[^dots-tts-soar-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with sub-40 ms TTFA streaming on H100, while this concept covers a 2B continuous-AR voice-cloning checkpoint tuned for fidelity (NFE 10–32, CFG 1.2) rather than few-step latency; no shared codebase is asserted (**Synthesis**).[^dots-tts-soar-card]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no checkpoint downloaded, no audio synthesized, and no WER, SIM, NFE/latency, language-coverage, or cloning-fidelity claims reproduced (**Synthesis**).[^dots-tts-soar-card]
- GitHub repository, Spaces playground, demo page, `constraints/recommended.txt`, training script (`scripts/train_dots_tts.py`), smoke config (`configs/dots_tts.yaml`), sibling checkpoints (`dots.tts-base`, `dots.tts-mf`), and full project-README benchmark tables (MiniMax Multilingual, EmergentTTS-Eval) were linked but not fetched and are not in `raw/`; checkpoint weights, AudioVAE/decoder weights, reference-audio files, and constraint pins were not inspected (**Synthesis**).[^dots-tts-soar-card]
- All identity, architecture, training-scale, sampling, benchmark, compatibility, and usage claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^dots-tts-soar-card]

[^dots-tts-soar-card]: [dots.tts-soar model card](../raw/dots.tts-soar.md) — locators: frontmatter (`license: apache-2.0`, `pipeline_tag: text-to-speech`, `tags`, `library_name: dots_tts`, `base_model: dots-studio/dots.tts-base`); intro paragraph (2B fully continuous end-to-end AR, semantic encoder + LLM + AR flow-matching head over 48 kHz AudioVAE, no codec tokens; SCA reward-free post-training; highest zero-shot fidelity/similarity; recommended production default); 3-row checkpoint table (`dots.tts-base` ~1.5M h, `dots.tts-soar` you-are-here + SCA, `dots.tts-mf` MeanFlow NFE=4); `Quick Start / Installation` conda+pip fence (`python=3.10`, `git+https://github.com/studio-dots-ai/dots.tts.git`, `constraints/recommended.txt`); `CLI` fence (`--model-name-or-path dots-studio/dots.tts-soar`, `--text`, `--prompt-audio`, `--prompt-text`, `--output`); `Python API` fence (`DotsTtsRuntime.from_pretrained`, `precision="bfloat16"`, `generate(num_steps=10, guidance_scale=1.2)`, `soundfile` write); `Recommended sampling settings` table (`--num-steps` 10–32, `--guidance-scale` 1.2 + SCA-tightening note); `Fine-tuning` section (base/soar starting points, `scripts/train_dots_tts.py`, `configs/dots_tts.yaml`, `accelerate launch` fence); `Architecture` section (frozen AudioVAE + BigVGAN-style causal decoder, per-patch AR, semantic-encoder/LLM `Qwen2.5-1.5B-Base` BPE-no-phonemes/DiT+CAM++ x-vector bullets, SCA paragraph); `Performance` Seed-TTS-Eval table (5 rows: Seed-TTS, Qwen3-TTS 1.7B, VoxCPM 2, base, soar with test-en/test-zh/test-zh-hard WER/SIM and Avg columns), MiniMax table (5 rows with Avg WER/SIM), CV3-Eval table (CosyVoice 3, base, soar en→zh/zh→en SIM), EmergentTTS-Eval paragraph (65.7% Syntactic Complexity vs `gpt-4o-mini-tts`) plus project-README pointer; `Risks and Limitations` section (misuse, low-resource WER gap Arabic/Hindi/Turkish/Vietnamese, speech-heavy no singing); `Citation` BibTeX (`dotstts2026`); `License` section (Apache-2.0).
