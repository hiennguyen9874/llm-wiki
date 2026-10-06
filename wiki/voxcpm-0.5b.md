---
type: Concept
title: VoxCPM-0.5B
description: 0.5B-parameter tokenizer-free bilingual English-Chinese TTS model with context-aware prosody, zero-shot voice cloning, and 0.17 RTF streaming synthesis on RTX 4090.
tags: [tts, bilingual, voice-cloning, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:27:56Z }
stale_after: 2027-10-06
sources:
  - id: voxcpm-05b-card
    resource: ../raw/VoxCPM-0.5B.md
    kind: documentation
    title: VoxCPM-0.5B model card
---

VoxCPM-0.5B is a 0.5B-parameter tokenizer-free diffusion-autoregressive bilingual English-Chinese text-to-speech model on a MiniCPM-4 backbone, trained on a 1.8 million-hour bilingual corpus, offering context-aware expressive synthesis and zero-shot voice cloning from a short reference clip, with streaming synthesis at 0.17 real-time factor on an NVIDIA RTX 4090 GPU under the Apache-2.0 license (**Reported**).[^voxcpm-05b-card]

## Model identity and release

- Name is `VoxCPM-0.5B`; organization is OpenBMB (ModelBest); weights are `openbmb/VoxCPM-0.5B` on Hugging Face; base model is `openbmb/MiniCPM4-0.5B`; inference library is `voxcpm` (`pip install voxcpm`); upstream links are the GitHub `OpenBMB/VoxCPM` repository, Hugging Face model page, live demo Space, audio-samples page, and MiniCPM wiki (**Reported**).[^voxcpm-05b-card]
- Frontmatter declares `license: apache-2.0`, `library_name: voxcpm`, `pipeline_tag: text-to-speech`, languages `en, zh`, and tags including `text-to-speech`, `speech generation`, and `voice cloning` (**Reported**, with frontmatter fields **Observed** by static inspection).[^voxcpm-05b-card]

## Architecture and training

- Architecture is tokenizer-free and end-to-end diffusion autoregressive: it directly generates continuous speech representations from text instead of discrete speech tokens, with implicit semantic-acoustic decoupling through hierarchical language modeling and FSQ constraints (**Reported**).[^voxcpm-05b-card]
- Training data is a 1.8 million-hour bilingual (English-Chinese) corpus, which the source credits for content-adaptive speaking style (**Reported**).[^voxcpm-05b-card]
- Output sample rate in the usage example is 16 kHz (`sf.write("output.wav", wav, 16000)`) (**Reported**).[^voxcpm-05b-card]

## Capabilities

- Context-Aware Expressive Generation infers appropriate prosody from text content and spontaneously adapts speaking style, including poetry, lyrics, and dramatic monologues (**Reported**).[^voxcpm-05b-card]
- True-to-Life Zero-Shot Voice Cloning reproduces timbre plus fine-grained accent, emotional tone, rhythm, and pacing from a short reference audio clip with its transcript; prompt speech also carries over background sounds and ambiance unless prompt enhancement is enabled (**Reported**).[^voxcpm-05b-card]
- High-Efficiency Streaming Synthesis reaches a real-time factor as low as 0.17 on a consumer-grade NVIDIA RTX 4090 GPU, enabling real-time applications (**Reported**).[^voxcpm-05b-card]

## Inference usage

- Install with `pip install voxcpm`; the model downloads automatically on first run, or prefetch with `snapshot_download("openbmb/VoxCPM-0.5B")` via `huggingface_hub`; the web demo additionally uses `iic/speech_zipenhancer_ans_multiloss_16k_base` (prompt enhancement) and `iic/SenseVoiceSmall` (prompt ASR) via `modelscope.snapshot_download` (**Reported**).[^voxcpm-05b-card]
- Basic Python usage loads `VoxCPM.from_pretrained("openbmb/VoxCPM-0.5B")` and calls `model.generate` with `text`, optional `prompt_wav_path`/`prompt_text` for cloning, `cfg_value=2.0`, `inference_timesteps=10`, `normalize=True`, `denoise=True`, `retry_badcase=True`, `retry_badcase_max_times=3`, and `retry_badcase_ratio_threshold=6.0` (**Reported**).[^voxcpm-05b-card]
- CLI entry point is `voxcpm` (or `python -m voxcpm.cli`): direct synthesis with `--text`/`--output`; cloning with `--prompt-audio`/`--prompt-text` plus `--denoise`; batch with `--input` (one text per line) plus `--output-dir`; quality/speed with `--cfg-value`/`--inference-timesteps`; model selection with `--model-path` or `--hf-model-id` plus `--cache-dir`/`--local-files-only`; denoiser control with `--no-denoiser`/`--zipenhancer-path` (**Reported**).[^voxcpm-05b-card]
- Voice Chef guide: keep Text Normalization ON for regular text (numbers, abbreviations, and punctuation handled by the WeTextProcessing library); turn it OFF for phoneme input such as `{HH AH0 L OW1}` (English) or `{ni3}{hao3}` (Chinese); enable Prompt Speech Enhancement for clean studio-quality clones; with no reference the model improvises style from text via its MiniCPM-4 foundation (**Reported**).[^voxcpm-05b-card]
- Tuning guidance: lower CFG when the voice sounds strained (more relaxed and improvisational, good for expressive prompts); raise it slightly for maximum clarity and text adherence; lower inference timesteps for fast drafts, higher for refined gourmet output; start from defaults (**Reported**).[^voxcpm-05b-card]
- Web demo starts with `python app.py` and supports Voice Cloning and Voice Creation (**Reported**).[^voxcpm-05b-card]

## Performance and evaluation

Seed-TTS-eval zero-shot results; lower WER/CER is better, higher SIM is better; VoxCPM row plus nearby open-source peers (**Reported**):[^voxcpm-05b-card]

| Model | Parameters | Open-source | test-EN WER / SIM | test-ZH CER / SIM | test-Hard CER / SIM |
| --- | ---: | :---: | ---: | ---: | ---: |
| VoxCPM | 0.5B | ✅ | 1.85 / 72.9 | 0.93 / 77.2 | 8.87 / 73.0 |
| CosyVoice2 | 0.5B | ✅ | 3.09 / 65.9 | 1.38 / 75.7 | 6.83 / 72.4 |
| F5-TTS | 0.3B | ✅ | 2.00 / 67.0 | 1.53 / 76.0 | 8.67 / 71.3 |
| FireRedTTS-2 | 1.5B | ✅ | 1.95 / 66.5 | 1.14 / 73.6 | - |
| IndexTTS2 | 1.5B | ✅ | 2.23 / 70.6 | 1.03 / 76.5 | - |
| Qwen2.5-Omni | 7B | ✅ | 2.72 / 63.2 | 1.70 / 75.2 | 7.97 / 74.7 |

CV3-eval results; lower CER/WER is better, higher SIM/DNSMOS is better; VoxCPM row plus nearby open-source peers (**Reported**):[^voxcpm-05b-card]

| Model | zh CER | en WER | hard-zh CER / SIM / DNSMOS | hard-en WER / SIM / DNSMOS |
| --- | ---: | ---: | ---: | ---: |
| VoxCPM | 3.40 | 4.04 | 12.9 / 66.1 / 3.59 | 7.89 / 64.3 / 3.74 |
| CosyVoice2 | 4.08 | 6.32 | 12.58 / 72.6 / 3.81 | 11.96 / 66.7 / 3.95 |
| CosyVoice3-0.5B | 3.89 | 5.24 | 14.15 / 78.6 / 3.75 | 9.04 / 75.9 / 3.92 |
| IndexTTS2 | 3.58 | 4.45 | 12.8 / 74.6 / 3.65 | - |

- The source presents these tables under a `Performance Highlights` section claiming competitive results on public zero-shot TTS benchmarks; full 18-row Seed-TTS-eval and 10-row CV3-eval tables live in the source and only the VoxCPM rows plus nearby open-source peers are reproduced here (**Reported**).[^voxcpm-05b-card]

## Limitations and responsible use

- May produce unexpected, biased, or artifact-containing output despite large-scale training; occasionally unstable on very long or expressive inputs; limited direct control over emotion or speaking style (**Reported**).[^voxcpm-05b-card]
- Zero-shot cloning can be misused for impersonation, fraud, or disinformation deepfakes; infringing, illegal, or unethical use is strictly forbidden, and publicly shared generated content should be clearly marked as AI-generated (**Reported**).[^voxcpm-05b-card]
- Trained primarily on Chinese and English data; performance on other languages is not guaranteed and may be unpredictable or low quality (**Reported**).[^voxcpm-05b-card]
- Released for research and development only; production or commercial use is not recommended without rigorous testing and safety evaluation (**Reported**).[^voxcpm-05b-card]

## License

- Model weights and code are open-sourced under Apache-2.0 (**Reported**).[^voxcpm-05b-card]

## Relationships

- Successor: [VoxCPM2](voxcpm2.md) covers the 2B-parameter 30-language successor with voice design, controllable and ultimate cloning modes, and 48 kHz AudioVAE V2 output, while this concept covers the 0.5B bilingual predecessor with 16 kHz output, WeTextProcessing normalization, and Seed-TTS/CV3 benchmark tables; neither concept is marked deprecated and no shared checkpoint is asserted (**Synthesis**).[^voxcpm-05b-card]
- Same-scale benchmark comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B LLM-based streaming TTS model with zero-shot, cross-lingual, and instruct control, while this concept covers a 0.5B diffusion-autoregressive TTS model with continuous-space generation and FSQ-constrained hierarchical modeling; both appear as open-source 0.5B rows in the source's Seed-TTS-eval and CV3-eval tables and no shared codebase is asserted (**Synthesis**).[^voxcpm-05b-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no RTF, cloning-fidelity, WER/CER, SIM, or DNSMOS claims reproduced (**Synthesis**).[^voxcpm-05b-card]
- Header images (`assets/voxcpm_logo.png`, `assets/voxcpm_model.png`), GitHub repository, Hugging Face model page and demo Space, samples page, MiniCPM wiki, ModelScope ZipEnhancer and SenseVoiceSmall checkpoints, and the `app.py` web demo were linked but not fetched and are not in `raw/`; checkpoint, denoiser, reference-audio, and fine-tuning artifacts were listed but not present in `raw/` and were not inspected (**Synthesis**).[^voxcpm-05b-card]
- All identity, architecture, training-scale, capability, latency, benchmark, compatibility, and usage claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^voxcpm-05b-card]

[^voxcpm-05b-card]: [VoxCPM-0.5B model card](../raw/VoxCPM-0.5B.md) — locators: frontmatter (`license`, `language`, `base_model`, `pipeline_tag`, `library_name`, `tags`); `Overview` section (tokenizer-free continuous-space claim, diffusion autoregressive architecture, MiniCPM-4 backbone, hierarchical modeling plus FSQ decoupling, 1.8M-hour corpus); `Key Features` section (context-aware, cloning, 0.17 RTF on RTX 4090); `Quick Start` section (`pip install voxcpm`, `snapshot_download` fences for `openbmb/VoxCPM-0.5B`, ZipEnhancer, SenseVoiceSmall; `VoxCPM.from_pretrained` plus `model.generate` fence with `cfg_value`/`inference_timesteps`/`normalize`/`denoise`/`retry_badcase` arguments and 16 kHz `sf.write`; 7-item CLI fence; `python app.py` demo sentence); `A Voice Chef's Guide` section (3 steps: TN on/off with `{HH AH0 L OW1}`/`{ni3}{hao3}` phoneme examples and WeTextProcessing, prompt-speech/enhancement/improvise guidance, CFG/timesteps tuning); `Performance Highlights` section (18-row Seed-TTS-eval table, 10-row CV3-eval table); `Risks and limitations` section (5 bullets); `License` section (Apache-2.0).
