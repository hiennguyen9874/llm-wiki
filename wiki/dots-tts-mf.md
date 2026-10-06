---
type: Concept
title: dots.tts-mf
description: 2B-parameter continuous autoregressive TTS checkpoint with CFG-aware MeanFlow distillation for few-step (NFE=4) low-latency zero-shot voice cloning at 48 kHz.
tags: [tts, voice-cloning, low-latency, autoregressive, flow-matching]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: dots-tts-mf-card
    resource: ../raw/dots.tts-mf.md
    kind: documentation
    title: dots.tts-mf model card
---

dots.tts-mf is the 2B-parameter fully continuous end-to-end autoregressive text-to-speech checkpoint in the dots.tts family, distilled from `dots.tts-soar` with CFG-aware MeanFlow so per-patch sampling collapses to 2–4 function evaluations with one model evaluation per step, matching the teacher on average WER at NFE=4 with ~2.5× fewer evaluations and making it the recommended checkpoint for low-latency few-step zero-shot voice cloning at 48 kHz (**Reported**).[^dots-tts-mf-card]

## Model identity and release

- Full system name is `dots.tts` (2B parameters); this repository hosts `dots.tts-mf`, the CFG-aware MeanFlow distillation of `dots.tts-soar`; base model declared in frontmatter is `dots-studio/dots.tts-soar`; weights are `dots-studio/dots.tts-mf` on Hugging Face; inference library is `dots_tts` (`library_name: dots_tts`); upstream links are the `studio-dots-ai/dots.tts` GitHub repository, Hugging Face Spaces playground, and live demo page (**Reported**, with frontmatter `base_model`/`library_name` **Observed** by static inspection).[^dots-tts-mf-card]
- Frontmatter declares `license: apache-2.0`, `pipeline_tag: text-to-speech`, and tags including `text-to-speech`, `tts`, `voice-cloning`, `autoregressive`, `flow-matching`, `meanflow`, `distillation`, and `low-latency` (**Observed** by static inspection).[^dots-tts-mf-card]
- Family table lists three checkpoints: `dots.tts-base` (pretrain ~1.5M h; fine-tuning with full CFG/NFE control), `dots.tts-soar` (+ Self-corrective Alignment; highest zero-shot fidelity and speaker similarity; also recommended for fine-tuning), and `dots.tts-mf` (+ MeanFlow distillation; few-step inference NFE=4, low latency) (**Reported**).[^dots-tts-mf-card]

## Architecture

- Backbone pairs a semantic encoder, an LLM, and an autoregressive flow-matching acoustic head over a 48 kHz AudioVAE, with no discrete codec tokens anywhere in the pipeline (**Reported**).[^dots-tts-mf-card]
- Frozen AudioVAE encodes 48 kHz mono waveform into a continuous latent and decodes via a BigVGAN-style causal decoder; the autoregressive backbone predicts that latent one patch at a time (**Reported**).[^dots-tts-mf-card]
- Semantic encoder re-encodes each newly generated VAE patch into a compact embedding for the LLM, stripping high-variance acoustic detail; LLM is initialized from `Qwen2.5-1.5B-Base`, consumes BPE text directly with no phonemes, and emits one hidden state per audio step; AR flow-matching head is a DiT conditioning on the LLM hidden state and AR prefix to denoise the next VAE patch, with a frozen CAM++ speaker x-vector as side input (**Reported**).[^dots-tts-mf-card]
- CFG-aware MeanFlow distillation trains the flow-matching head as a MeanFlow student over the SCA teacher's velocity field with classifier-free guidance absorbed into the student, yielding a 2–4 NFE sampler that retains most teacher quality with a single model evaluation per step; `guidance_scale` has no effect at inference time (**Reported**).[^dots-tts-mf-card]

## Recommended sampling settings

- `--num-steps` (NFE) `4` is the recommended quality/latency trade-off; NFE=2/3 work but regress on WER/SIM (**Reported**).[^dots-tts-mf-card]
- `--guidance-scale` is ignored (no-op): CFG is fused into the distilled student and cannot be adjusted at inference, unlike `base`/`soar` (**Reported**).[^dots-tts-mf-card]

## Requirements and inference usage

- Install creates a `python=3.10` conda env (`dots_tts`), upgrades pip, and installs `git+https://github.com/studio-dots-ai/dots.tts.git` constrained by `constraints/recommended.txt` (**Reported**).[^dots-tts-mf-card]
- CLI few-step inference passes `--model-name-or-path dots-studio/dots.tts-mf` with `--text`, `--prompt-audio`, `--prompt-text` (exact transcript of the reference audio), `--num-steps 4`, and `--output`; `--guidance-scale` may be left at default (**Reported**).[^dots-tts-mf-card]
- Python API loads `DotsTtsRuntime.from_pretrained("dots-studio/dots.tts-mf", precision="bfloat16")` and calls `runtime.generate` with `text`, `prompt_audio_path`, `prompt_text`, and `num_steps=4`, writing `result["audio"]` with `soundfile` at `result["sample_rate"]` (**Reported**).[^dots-tts-mf-card]

## Performance and evaluation

- Seed-TTS-Eval (zero-shot, ~3 s reference) reports test-en / test-zh / test-zh-hard WER↓/SIM↑ and average: teacher `dots.tts-soar` NFE=10 averages 2.95/79.2 (1.30/77.1, 0.94/81.0, 6.60/79.5); `dots.tts-mf` NFE=4 averages 2.94/78.2 (1.29/76.2, 0.94/80.0, 6.60/78.5); NFE=3 averages 3.21/78.1; NFE=2 averages 3.43/77.0 — i.e. NFE=4 essentially matches the teacher on average WER with ~2.5× fewer model evaluations per patch and a single conditional pass per step (**Reported**).[^dots-tts-mf-card]
- CV3-Eval reports hard-en WER↓: Fish-Audio S2 — / 4.40; `dots.tts-soar` NFE=10 / 4.49; `dots.tts-mf` NFE=4 / 4.37 (**Reported**).[^dots-tts-mf-card]
- Full benchmark tables including MiniMax Multilingual and EmergentTTS-Eval are deferred to the project README and are not reproduced in this source (**Reported**).[^dots-tts-mf-card]

## Limitations and responsible use

- High-fidelity zero-shot voice cloning can produce highly realistic synthetic speech; intended for research and authorized deployment; do not use for impersonation, fraud, or disinformation; combine downstream use with consent-aware reference-audio policies, synthetic-speech detection, content watermarking, and clear AI-generated labeling (**Reported**).[^dots-tts-mf-card]
- At NFE=2/3 there is measurable WER and SIM regression vs. NFE=4; pick NFE to match the latency budget (**Reported**).[^dots-tts-mf-card]
- BPE backbone inherits the text LLM's language coverage at the cost of higher data appetite: on script-divergent and under-represented languages (Arabic, Hindi, Turkish, Vietnamese) WER is higher than on high-resource languages while speaker similarity is preserved (**Reported**).[^dots-tts-mf-card]
- Backbone is trained on a speech-heavy mixture; singing and unified speech-plus-sound generation are not covered (**Reported**).[^dots-tts-mf-card]

## License and citation

- Released under Apache-2.0 (**Reported**).[^dots-tts-mf-card]
- Citation is `dotstts2026`, `dots.tts Technical Report`, dots.tts Team, arXiv preprint 2026 (**Reported**).[^dots-tts-mf-card]

## Relationships

- Teacher checkpoint: [dots.tts-soar](dots-tts-soar.md) covers the SCA-refined 2B continuous-AR teacher this checkpoint is distilled from, reported in this source's Seed-TTS-Eval and CV3-Eval rows at NFE=10, while this concept covers its CFG-aware MeanFlow distillation for few-step (NFE=4) low-latency inference (**Synthesis**).[^dots-tts-mf-card]
- Low-latency TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with sub-40 ms TTFA and 0.32 RTF streaming on H100, while this concept covers a MeanFlow-distilled few-step (NFE=4) TTS checkpoint trading WER/SIM against NFE; no shared vendor or codebase is asserted (**Synthesis**).[^dots-tts-mf-card]
- Voice-cloning TTS comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a compact 0.6B multilingual zero-shot voice-cloning TTS model with DualAR architecture and ONNX/SGLang serving, while this concept covers a 2B continuous-AR voice-cloning checkpoint with AR flow-matching head and CAM++ x-vector conditioning; no shared codebase is asserted (**Synthesis**).[^dots-tts-mf-card]
- Continuous-tokenizer TTS comparison: [VoxCPM2](voxcpm2.md) covers a 2B tokenizer-free diffusion-autoregressive 48 kHz multilingual TTS model with voice design and controllable/ultimate cloning, while this concept covers a 2B fully continuous (no codec tokens) AR flow-matching 48 kHz TTS family with MeanFlow few-step distillation; no shared vendor or codebase is asserted (**Synthesis**).[^dots-tts-mf-card]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no checkpoint downloaded, no audio synthesized, and no WER, SIM, NFE/latency, language-coverage, or cloning-fidelity claims reproduced (**Synthesis**).[^dots-tts-mf-card]
- GitHub repository, Spaces playground, demo page, `constraints/recommended.txt`, sibling checkpoints (`dots.tts-base`, `dots.tts-soar`), and full project-README benchmark tables (MiniMax Multilingual, EmergentTTS-Eval) were linked but not fetched and are not in `raw/`; checkpoint weights, AudioVAE/decoder weights, reference-audio files, and constraint pins were not inspected (**Synthesis**).[^dots-tts-mf-card]
- All identity, architecture, training-scale, sampling, benchmark, compatibility, and usage claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^dots-tts-mf-card]

[^dots-tts-mf-card]: [dots.tts-mf model card](../raw/dots.tts-mf.md) — locators: frontmatter (`license`, `pipeline_tag`, `tags`, `library_name: dots_tts`, `base_model: dots-studio/dots.tts-soar`); intro paragraph (2B fully continuous end-to-end AR, semantic encoder + LLM + AR flow-matching head over 48 kHz AudioVAE, no codec tokens; CFG-aware MeanFlow 2–4 NFE single-eval, `guidance_scale` no effect; recommended low-latency checkpoint); 3-row checkpoint table (`dots.tts-base` ~1.5M h, `dots.tts-soar` self-corrective alignment, `dots.tts-mf` MeanFlow NFE=4); `Quick Start / Installation` conda+pip fence (`python=3.10`, `git+https://github.com/studio-dots-ai/dots.tts.git`, `constraints/recommended.txt`); `CLI` fence (`--model-name-or-path`, `--text`, `--prompt-audio`, `--prompt-text`, `--num-steps 4`, `--output`, guidance-scale no-op note); `Python API` fence (`DotsTtsRuntime.from_pretrained`, `precision="bfloat16"`, `generate(num_steps=4)`, `soundfile` write); `Recommended sampling settings` table (`--num-steps` 4, `--guidance-scale` ignored); `Architecture` section (frozen AudioVAE + BigVGAN-style causal decoder, per-patch AR, semantic-encoder/LLM `Qwen2.5-1.5B-Base` BPE-no-phonemes/DiT+CAM++ x-vector bullets, MeanFlow-over-SCA-teacher paragraph); `Performance` Seed-TTS-Eval table (4 rows: soar NFE=10, mf NFE=4/3/2 with test-en/test-zh/test-zh-hard WER/SIM and Avg columns) plus 2.5×-fewer-evaluations sentence and CV3-Eval table (Fish-Audio S2 4.40, soar 4.49, mf 4.37) plus project-README pointer; `Risks and Limitations` section (5 bullets: misuse, NFE=2/3 regression, CFG fused, low-resource WER gap Arabic/Hindi/Turkish/Vietnamese, speech-heavy no singing); `Citation` BibTeX (`dotstts2026`); `License` section (Apache-2.0).
