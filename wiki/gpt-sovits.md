---
type: Concept
title: GPT-SoVITS
description: Few-shot multilingual voice-conversion and TTS WebUI with 5-second zero-shot cloning, 1-minute fine-tuning, and v1–v5 checkpoints with local and Docker deployment.
tags: [tts, voice-cloning, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: gpt-sovits-readme
    resource: ../raw/GPT-SoVITS.md
    kind: documentation
    title: GPT-SoVITS-WebUI README
---

GPT-SoVITS is RVC-Boss's open-source few-shot voice-conversion and text-to-speech WebUI for zero-shot cloning from a 5-second sample and few-shot fine-tuning from about 1 minute of audio, with cross-lingual inference, dataset-building tools, and a v1 through v5 plus v2Pro checkpoint lineage for local and Docker deployment (**Reported**).[^gpt-sovits-readme]

## Model identity and release

- Name is `GPT-SoVITS-WebUI`, described as "A Powerful Few-shot Voice Conversion and Text-to-Speech WebUI"; upstream is `github.com/RVC-Boss/GPT-SoVITS`; license badge declares MIT; Python badge declares 3.10–3.12; docs are linked in Simplified Chinese, English, Japanese, Korean, and Turkish plus Yuque, rentry, changelog, Colab, Hugging Face demo, and Docker Hub pointers (**Reported**).[^gpt-sovits-readme]
- User guides are the Yuque Chinese guide and the rentry English guide; demo evidence is a Bilibili video (`BV12g4y1m7Uw`) and an unseen-speaker few-shot fine-tuning clip (**Reported**).[^gpt-sovits-readme]

## Capabilities

- Zero-shot TTS converts text from a 5-second vocal sample with no training (**Reported**).[^gpt-sovits-readme]
- Few-shot TTS fine-tunes with about 1 minute of training data for improved voice similarity and realism; zero-shot and few-shot voice conversion are both marked done in the Todo list (**Reported**).[^gpt-sovits-readme]
- Cross-lingual inference supports output in languages different from the training dataset; the supported list is English, Japanese, Korean, Cantonese, and Chinese (**Reported**).[^gpt-sovits-readme]
- WebUI tooling bundles voice-accompaniment separation (UVR5), automatic training-set segmentation, Chinese ASR, and text labeling to help beginners build datasets and GPT/SoVITS models; TTS speaking-speed control is marked done while enhanced emotion control is deferred to possible pretrained preset GPT models (**Reported**).[^gpt-sovits-readme]
- Dataset annotation format is `vocal_path|speaker_name|language|text`, with language codes `zh` (Chinese), `ja` (Japanese), `en` (English), `ko` (Korean), and `yue` (Cantonese); the example is `D:\GPT-SoVITS\xxx/xxx.wav|xxx|en|I like playing Genshin.` (**Reported**).[^gpt-sovits-readme]
- Fine-tune path in the WebUI is: fill in audio path, slice into chunks, optional denoise, ASR, proofread transcriptions, then move to the next tab and fine-tune (**Reported**).[^gpt-sovits-readme]

## Inference speed

- v2 ProPlus real-time factor (RTF) is reported as 0.028 on RTX 4060 Ti, 0.014 on RTX 4090 (about 1,400 words / ~4 minutes in 3.36 s), and 0.526 on M4 CPU, with a half-H200 Hugging Face demo offered for high-speed testing (**Reported**).[^gpt-sovits-readme]
- No measurement protocol, batch size, precision, text, checkpoint variant, or variance accompanies the RTF figures in this source; they are source assertions without independent verification in this wiki (**Synthesis**).[^gpt-sovits-readme]

## Version lineage

| Line | Durable change vs prior line | Upgrade assets named in source |
| --- | --- | --- |
| v2 | Adds Korean and Cantonese, optimized text frontend, pretrained-model expansion from 2k to 5k hours, better synthesis from low-quality reference audio | `gsv-v2final-pretrained` plus Chinese-only `G2PWModel` |
| v3 | Higher timbre similarity with less training data, more stable GPT output with fewer repetitions/omissions and richer emotional expression | `s1v3.ckpt`, `s2Gv3.pth`, `models--nvidia--bigvgan_v2_24khz_100band_256x`, optional AP-BWE 24k-to-48k super-resolution |
| v4 | Fixes v3 metallic artifacts from non-integer-multiple upsampling; native 48k output instead of v3 native 24k; presented as a direct v3 replacement pending further testing | `gsv-v4-pretrained/s2v4.pth` and `gsv-v4-pretrained/vocoder.pth` |
| v2Pro | Slightly higher VRAM than v2; claimed to surpass v4 performance at v2 hardware cost and speed; v1/v2/v2Pro share one behavior family and v3/v4 another, with average-quality training sets favoring v1/v2/v2Pro and v3/v4 leaning toward the reference timbre | `v2Pro/s2Dv2Pro.pth`, `v2Pro/s2Gv2Pro.pth`, `v2Pro/s2Dv2ProPlus.pth`, `v2Pro/s2Gv2ProPlus.pth`, `sv/pretrained_eres2netv2w24s4ep4.ckpt` |
| v5 | Improved similarity without SoVITS fine-tuning, updated vocoder reducing high-frequency spectral mirroring and aliasing, `cuda_graph` plus `flash_attention` acceleration (credited to `@XXXXRT666`) | `gsv-v5-pretrained` subdirectory preserved under `GPT_SoVITS/pretrained_models`, from the `cuda_graph_accel_v5` branch |

Table values are source assertions (**Reported**).[^gpt-sovits-readme]

## Requirements, installation, and deployment

- Tested environments matrix lists Python 3.10 with PyTorch 2.5.1/CUDA 12.4, Python 3.11 with PyTorch 2.5.1/CUDA 12.4 and 2.7.0/CUDA 12.8, Python 3.9 with PyTorch 2.8.0dev/CUDA 12.8, Python 3.9 and 3.11 with PyTorch 2.5.1/2.7.0 on Apple silicon, and Python 3.9 with PyTorch 2.2.2 on CPU (**Reported**).[^gpt-sovits-readme]
- Windows integrated package is `GPT-SoVITS-v3lora-20250228.7z` started with `go-webui.bat` (or `go-webui.ps1`; `go-webui-v1` and `go-webui-v2` variants switch major versions); conda path is `conda create -n GPTSoVits python=3.10` then `pwsh -F install.ps1 --Device <CU126|CU128|CPU> --Source <HF|HF-Mirror|ModelScope> [--DownloadUVR5]` (**Reported**).[^gpt-sovits-readme]
- Linux path is the same conda environment then `bash install.sh --device <CU126|CU128|ROCM|CPU> --source <HF|HF-Mirror|ModelScope> [--download-uvr5]`; macOS path uses `--device <MPS|CPU>` with the caveat that GPU-trained Mac models yield significantly lower quality so CPUs are temporarily used (**Reported**).[^gpt-sovits-readme]
- Manual path is `pip install -r extra-req.txt --no-deps` plus `pip install -r requirements.txt`, with FFmpeg via conda, apt (`ffmpeg`, `libsox-dev`), Windows `ffmpeg.exe`/`ffprobe.exe` in the project root plus Visual Studio 2017 redistributable, or `brew install ffmpeg` on macOS (**Reported**).[^gpt-sovits-readme]
- Pretrained-model placement: `lj1995/GPT-SoVITS` weights into `GPT_SoVITS/pretrained_models` (skippable if `install.sh` succeeds); `G2PWModel.zip` from Hugging Face or ModelScope unzipped/renamed to `G2PWModel` under `GPT_SoVITS/text` for Chinese TTS; UVR5 weights into `tools/uvr5/uvr5_weights` with same-name model/config pairs containing `roformer` for `bs_roformer`/`mel_band_roformer` types; Damo ASR/VAD/punctuation models into `tools/asr/models` for Chinese; Faster-Whisper Large V3 (or similar Systran checkpoints) into `tools/asr/models` for English/Japanese (**Reported**).[^gpt-sovits-readme]
- Inference entry points are `python webui.py [v1] [<language>]` or `python GPT_SoVITS/inference_webui.py [<language>]`, then the `1-GPT-SoVITS-TTS/1C-inference` tab; command-line dataset utilities are `python tools/uvr5/webui.py`, `python audio_slicer.py` (threshold/min-length/min-interval/hop-size), `python tools/asr/funasr_asr.py -i <input> -o <output>` for Chinese, and `python ./tools/asr/fasterwhisper_asr.py -i <input> -o <output> -l <language> -p <precision>` for other languages (**Reported**).[^gpt-sovits-readme]
- Docker guidance is to check Docker Hub tags because code moves faster than images; `Lite` services omit ASR and UVR5 models; compose mounts the project root so callers pull latest code first; `is_half` toggles fp16; Windows Docker Desktop needs larger `shm_size` (e.g. `16g`); full services are `GPT-SoVITS-CU126`/`CU128` vs `Lite` variants run via `docker compose run --service-ports <service>`; local builds use `bash docker_build.sh --cuda <12.6|12.8> [--lite]` and shells via `docker exec -it <service> bash` (**Reported**).[^gpt-sovits-readme]

## Relationships

- Open voice-cloning comparison: [Chatterbox TTS](chatterbox-tts.md) covers a 0.5B Llama-backbone TTS family with 23-language V3, exaggeration/CFG controls, and watermarking, while this concept covers a WebUI-centered few-shot VC/TTS system with 5-second zero-shot and 1-minute fine-tune paths across 5 listed languages; no shared vendor or checkpoint is asserted (**Synthesis**).[^gpt-sovits-readme]
- Streaming multilingual comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B streaming zero-shot TTS model with instruct and cross-lingual control plus vLLM/streaming inference, while this concept covers cross-lingual few-shot cloning plus dataset/fine-tune tooling and a v1–v5 upgrade lineage; no shared vendor or training data is asserted (**Synthesis**).[^gpt-sovits-readme]
- Voice-cloning deployment comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B DualAR zero-shot TTS model with ONNX INT4 CPU and SGLang Omni serving, while this concept covers conda/manual/Docker local deployment with CUDA/ROCM/MPS/CPU device flags and integrated UVR5/slicer/ASR dataset tools; no shared vendor or codebase is asserted (**Synthesis**).[^gpt-sovits-readme]
- Emotion-control comparison: [GLM-TTS](glm-tts.md) covers a bilingual TTS system with GRPO multi-reward emotion alignment and phoneme-level control, while this concept marks enhanced TTS emotion control as open and points at preset GPT models as a possible route; no shared vendor or training data is asserted (**Synthesis**).[^gpt-sovits-readme]
- Lightweight inference engine: [Genie-TTS](genie-tts.md) packages V2/V2ProPlus checkpoints from this GPT-SoVITS family into a CPU-first ONNX inference engine with conversion tooling and FastAPI serving, while this concept covers the upstream WebUI, fine-tune tooling, and v1–v5 lineage; Genie-TTS V3/V4 support is open (**Synthesis**).[^gpt-sovits-readme]

## Coverage and limits

- Source inspected statically only; no environment created, no installer or Docker image run, no checkpoint downloaded, no fine-tune or inference executed, and no zero-shot quality, similarity, cross-lingual, RTF, VRAM, or version-delta claims reproduced (**Synthesis**).[^gpt-sovits-readme]
- Linked badges, demo video/clip, Colab notebook, Hugging Face/ModelScope checkpoints, Yuque/rentry guides, wiki feature pages, Docker Hub tags, and acknowledged upstream projects (VITS/SoundStorm/contentvec/HiFi-GAN/Fish-Speech/F5-TTS/BigVGAN/eres2netv2/G2PW/frontend, UVR/audio-slicer/SubFix/FFmpeg/gradio/Faster-Whisper/FunASR/AP-BWE) were not fetched and are not in `raw/`; parameter counts, training data, hyperparameters, sample rates (other than v3 24k / v4 48k natives), and serving-latency details are absent from the captured source (**Synthesis**).[^gpt-sovits-readme]
- All capability, compatibility, serving, and benchmark claims are source assertions without independent verification in this wiki; model-release and RTF figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^gpt-sovits-readme]

[^gpt-sovits-readme]: [GPT-SoVITS-WebUI README](../raw/GPT-SoVITS.md) — locators: header (title, tagline, RVC-Boss upstream, MIT/Python 3.10–3.12 badges, Colab/HF/Docker links, five-language doc links); `Features` list (5-second zero-shot, 1-minute few-shot, en/ja/ko/yue/zh cross-lingual, UVR5/slicer/Chinese-ASR/labeling tools); RTF paragraph (`RTF(inference speed) of GPT-SoVITS v2 ProPlus`: 0.028 on 4060Ti, 0.014 on 4090 for ~1400 words/~4 min in 3.36 s, 0.526 on M4 CPU, half-H200 demo) and `User guide` links; `Installation` plus `Tested Environments` table (7 Python/PyTorch/device rows); `Windows`/`Linux`/`macOS`/`Install Manually`/`Install FFmpeg` subsections (integrated `GPT-SoVITS-v3lora-20250228.7z`, `go-webui*.bat/*.ps1`, `install.ps1`/`install.sh` device/source flags, Mac CPU caveat, `extra-req.txt`/`requirements.txt`, per-OS FFmpeg, VS2017); `Running GPT-SoVITS with Docker` (Hub tags, `Lite` ASR/UVR5 exclusion, arch auto-pull, compose mount plus pull-latest, `is_half`, `shm_size`, full vs `Lite` services, `docker compose run --service-ports`, `docker_build.sh`, `docker exec -it`); `Pretrained Models` items 1–5 (`GPT_SoVITS/pretrained_models`, `GPT_SoVITS/text/G2PWModel`, `tools/uvr5/uvr5_weights` roformer naming rule, `tools/asr/models` Damo and Faster-Whisper Large V3); `Dataset Format` fence (`vocal_path|speaker_name|language|text`, zh/ja/en/ko/yue dict, Genshin example); `Finetune and inference` (`webui.py [v1] [<language>]`, `GPT_SoVITS/inference_webui.py`, `1-GPT-SoVITS-TTS/1C-inference`, six-step finetune list); `V2`/`V3`/`V4`/`V2Pro`/`V5 Release Notes` (v2 Korean/Cantonese, frontend, 2k→5k hours, low-quality-ref fix; v3 timbre/stability/emotion with `s1v3/s2Gv3/BigVGAN` plus AP-BWE; v4 metallic-artifact fix with native 48k and `s2v4/vocoder.pth`; v2Pro VRAM/perf/cost claim with family split and five checkpoint paths; v5 no-SoVITS-finetune similarity, vocoder mirroring/aliasing fix, `cuda_graph`/`flash_attention`, `cuda_graph_accel_v5` branch plus `gsv-v5-pretrained` subdir); `Todo List` (done JA/EN localization, guides, JA/EN finetune, VC, speed control, EN/JA frontend, Colab, 2k→10k data, better SoVITS base; open emotion control, GPT-vocab token inputs, tiny/larger models, model mix); `(Additional) Method for running from the command line` (`tools/uvr5/webui.py`, `audio_slicer.py`, `tools/asr/funasr_asr.py`, `tools/asr/fasterwhisper_asr.py`, custom list path); `Credits`/`Thanks` (ar-vits, SoundStorm, vits, TransferTTS, contentvec, hifi-gan, fish-speech, f5-TTS, shortcut flow matching, Chinese Speech Pretrain, Chinese-Roberta-WWM-Ext-Large, BigVGAN, eres2netv2, zh_normalization, split-lang, g2pW, pypinyin-g2pW, UVR, audio-slicer, SubFix, FFmpeg, gradio, faster-whisper, FunASR, AP-BWE, Naozumi520 Cantonese set).
