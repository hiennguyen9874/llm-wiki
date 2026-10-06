---
type: Concept
title: Fun-CosyVoice3-0.5B-2512
description: LLM-based multilingual zero-shot TTS model with 0.5B parameters, base and RL checkpoints, 9-language plus Chinese dialect coverage, pronunciation inpainting, and 150 ms bi-streaming.
tags: [ml, tts, voice-cloning, multilingual, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T08:00:00Z }
stale_after: 2027-10-06
sources:
  - id: fun-cosyvoice3-card
    resource: ../raw/Fun-CosyVoice3-0.5B-2512.md
    kind: documentation
    title: Fun-CosyVoice3-0.5B-2512 README and model card
---

Fun-CosyVoice3-0.5B-2512 is FunAudioLLM's 0.5B-parameter large-language-model text-to-speech system for zero-shot multilingual speech synthesis in the wild, released December 2025 as base and RL checkpoints that the source presents as surpassing CosyVoice 2.0 on content consistency, speaker similarity, and prosody naturalness (**Reported**).[^fun-cosyvoice3-card]

## Model identity and release

- Name is Fun-CosyVoice3-0.5B-2512; family is CosyVoice / Fun-CosyVoice 3.0 by FunAudioLLM; weights are `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` on Hugging Face and ModelScope; header links list demos, paper `arXiv:2505.17589`, ModelScope, Hugging Face, and CV3-Eval; frontmatter declares `pipeline_tag: text-to-speech`, languages `zh, en, fr, es, ja, ko, it, ru, de`, and license `apache-2.0` (**Reported**, with frontmatter fields **Observed** by static inspection).[^fun-cosyvoice3-card]
- Roadmap dates the 2025/12 release to the Fun-CosyVoice3-0.5B-2512 base model, RL model, training/inference script, and ModelScope Gradio space; the same roadmap carries the family history already compiled in [CosyVoice2-0.5B](cosyvoice2-0.5b.md): 2025/08 Triton TRT-LLM runtime plus CosyVoice2 GRPO training support credited to NVIDIA contributor Yuekai Zhang, 2025/07 Fun-CosyVoice 3.0 eval set, 2025/05 CosyVoice2-0.5B vLLM support, 2024/12 25 Hz CosyVoice2-0.5B release, and earlier streaming, Repetition Aware Sampling (RAS), flow-matching, FastAPI, and WeTextProcessing entries (**Reported**).[^fun-cosyvoice3-card]
- Family context lists CosyVoice 2.0 (demos, `arXiv:2412.10117`, ModelScope `iic/CosyVoice2-0.5B`, Hugging Face `FunAudioLLM/CosyVoice2-0.5B`) and CosyVoice 1.0 (demos, v1 paper PDF, ModelScope `iic/CosyVoice-300M`, Hugging Face `FunAudioLLM/CosyVoice-300M`); this concept is the 3.0 successor to [CosyVoice2-0.5B](cosyvoice2-0.5b.md), which remains a separate maintained checkpoint rather than a deprecated predecessor (**Reported**, succession scope **Synthesis**).[^fun-cosyvoice3-card]

## Capabilities and controllability

- Language coverage is 9 common languages (Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Russian) plus 18+ Chinese dialects/accents (Guangdong, Minnan, Sichuan, Dongbei, Shan3xi, Shan1xi, Shanghai, Tianjin, Shandong, Ningxia, Gansu, and others), with multilingual and cross-lingual zero-shot voice cloning (**Reported**).[^fun-cosyvoice3-card]
- Content consistency and naturalness are presented as state-of-the-art on consistency, speaker similarity, and prosody naturalness; no independent verification was performed in this wiki (**Reported**).[^fun-cosyvoice3-card]
- Pronunciation inpainting supports Chinese Pinyin and English CMU phonemes for added controllability in production use; the usage example demonstrates a Chinese hotfix with inline Pinyin `[j][ǐ]` (**Reported**).[^fun-cosyvoice3-card]
- Text normalization reads numbers, special symbols, and various text formats without a traditional frontend module; normalization defaults to WeTextProcessing when the `ttsfrd` package is unavailable, with optional `ttsfrd` resource install for better performance (**Reported**).[^fun-cosyvoice3-card]
- Bi-streaming supports text-in streaming and audio-out streaming with latency as low as 150 ms while maintaining high-quality output (**Reported**).[^fun-cosyvoice3-card]
- Instruct support covers languages, dialects, emotions, speed, volume, and similar controls via `inference_instruct2` with a natural-language instruction plus `<|endofprompt|>`; supported controls are defined in `cosyvoice/utils/common.py#L28` per the usage comment (**Reported**).[^fun-cosyvoice3-card]

## Performance and evaluation

- The evaluation table reports Fun-CosyVoice3-0.5B-2512 (open-source, 0.5B) at test-zh CER 1.21% with 78.0% speaker similarity, test-en WER 2.24% with 71.8% speaker similarity, and test-hard CER 6.71% with 75.8% speaker similarity (**Reported**).[^fun-cosyvoice3-card]
- The RL variant Fun-CosyVoice3-0.5B-2512_RL (open-source, 0.5B) reports test-zh CER 0.81% with 77.4% speaker similarity, test-en WER 1.68% with 69.5% speaker similarity, and test-hard CER 5.44% with 75.0% speaker similarity — the lowest CER/WER in their columns among the table's listed rows (**Reported**, column-minimum reading **Observed** by static inspection).[^fun-cosyvoice3-card]
- Table context includes human reference, closed-source baselines (Seed-TTS, MiniMax-Speech), and open-source baselines (F5-TTS, Spark TTS, CosyVoice2, FireRedTTS2, Index-TTS2, VibeVoice-1.5B, VibeVoice-Realtime, HiggsAudio-v2, VoxCPM, GLM-TTS, GLM-TTS RL); CosyVoice2 is listed at test-zh 1.45%/75.7%, test-en 2.57%/65.9%, test-hard 6.83%/72.4% (**Reported**).[^fun-cosyvoice3-card]
- Paper lineage is `CosyVoice: A scalable multilingual zero-shot text-to-speech synthesizer based on supervised semantic tokens` (`arXiv:2407.05407`), `Cosyvoice 2: Scalable streaming speech synthesis with large language models` (`arXiv:2412.10117`), `CosyVoice 3: Towards In-the-wild Speech Generation via Scaling-up and Post-training` (`arXiv:2505.17589`), and an ICASSP 2025 paper on building LLM-based zero-shot streaming TTS with CosyVoice (**Reported**).[^fun-cosyvoice3-card]

## Requirements, installation, and usage

- Requires a recursive clone (`git clone --recursive`, with `git submodule update --init --recursive` retry on network failure), Conda, a `cosyvoice` environment with Python 3.10, `pip install -r requirements.txt` (documented via an Aliyun mirror), and sox (`sox libsox-dev` on Ubuntu, `sox sox-devel` on CentOS) (**Reported**).[^fun-cosyvoice3-card]
- Model download uses `huggingface_hub.snapshot_download` for `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` into `pretrained_models/Fun-CosyVoice3-0.5B` and `FunAudioLLM/CosyVoice-ttsfrd` into `pretrained_models/CosyVoice-ttsfrd`; the `ttsfrd` resource is optionally unzipped from `resource.zip` and installed from `ttsfrd_dependency-0.1-py3-none-any.whl` and `ttsfrd-0.4.2-cp310-cp310-linux_x86_64.whl` (**Reported**).[^fun-cosyvoice3-card]
- Basic usage imports `AutoModel` from `cosyvoice.cli.cosyvoice` (with `third_party/Matcha-TTS` on `sys.path`), constructs `AutoModel(model_dir='pretrained_models/Fun-CosyVoice3-0.5B')`, and saves returned `tts_speech` chunks with `torchaudio.save` at `cosyvoice.sample_rate`; examples call zero-shot, cross-lingual, and instruct methods with `stream=False` and a prompt WAV `./asset/zero_shot_prompt.wav` (**Reported**).[^fun-cosyvoice3-card]
- Zero-shot usage (`inference_zero_shot`) synthesizes English or Chinese text from a prompt transcript plus prompt audio, e.g. English `CosyVoice is undergoing a comprehensive upgrade...` and Chinese `八百标兵奔北坡...` against prompt text `You are a helpful assistant.<|endofprompt|>希望你以后能够做的比我还好呦。` (**Reported**).[^fun-cosyvoice3-card]
- Fine-grained control (`inference_cross_lingual`) demonstrates inline `[breath]` tags in a Chinese passage; supported controls are defined in `cosyvoice/tokenizer/tokenizer.py#L280` per the usage comment (**Reported**).[^fun-cosyvoice3-card]
- Instruct usage (`inference_instruct2`) demonstrates a Cantonese-dialect instruction `请用广东话表达。<|endofprompt|>` and a fast-speech instruction `请用尽可能快地语速说一句话。<|endofprompt|>` (**Reported**).[^fun-cosyvoice3-card]
- Acknowledged code sources are FunASR, FunCodec, Matcha-TTS, AcademiCodec, and WeNet; discussion is via GitHub Issues and an official DingDing chat group (QR image linked but not ingested) (**Reported**).[^fun-cosyvoice3-card]

## Relationships

- Successor to [CosyVoice2-0.5B](cosyvoice2-0.5b.md): this concept covers the 0.5B Fun-CosyVoice 3.0 base and RL checkpoints with 9-language plus dialect coverage, Pinyin/CMU inpainting, and 150 ms bi-streaming, while the earlier concept covers the 0.5B CosyVoice2 streaming model with saved-speaker reuse and vLLM/TRT-LLM serving mentions; no shared training-data claim is asserted (**Synthesis**).[^fun-cosyvoice3-card]
- TTS voice-cloning comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B multilingual zero-shot TTS model with DualAR architecture and ONNX/SGLang paths, while this concept covers a 0.5B LLM-based model with RL post-training and CER/WER plus speaker-similarity table figures; no shared vendor or codebase is asserted (**Synthesis**).[^fun-cosyvoice3-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice design/direction and H100 latency figures, while this concept covers a multilingual streaming model with instruct control over language, dialect, emotion, speed, and volume; no shared vendor or codebase is asserted (**Synthesis**).[^fun-cosyvoice3-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no Conda environment created, no checkpoint or `ttsfrd` resource downloaded, no audio synthesized, and no CER, WER, speaker-similarity, latency, dialect, instruction-following, or text-normalization claims reproduced (**Synthesis**).[^fun-cosyvoice3-card]
- Local prompt audio (`./asset/zero_shot_prompt.wav`), DingDing QR image, SVG banner, demo pages, papers, ModelScope/Hugging Face repositories, Gradio space, CV3-Eval suite, and license/terms pages were linked but not fetched and are not in `raw/`; checkpoint contents, tokenizer and `common.py` implementations beyond the cited path comments, training/inference scripts, TRT-LLM/vLLM/GRPO runtime contents, and reference audio were not inspected (**Synthesis**).[^fun-cosyvoice3-card]
- All capability, compatibility, serving, and benchmark claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `ml` domain rule (**Synthesis**).[^fun-cosyvoice3-card]

[^fun-cosyvoice3-card]: [Fun-CosyVoice3-0.5B-2512 README and model card](../raw/Fun-CosyVoice3-0.5B-2512.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`); header model links (Fun-CosyVoice 3.0 demos/paper/ModelScope/HuggingFace/CV3-Eval, CosyVoice 2.0 and 1.0 links); `Highlight / Key Features` section (9 languages, 18+ dialects with listed examples, cross-lingual zero-shot cloning, SOTA consistency/similarity/naturalness claim, Pinyin/CMU inpainting, text normalization, 150 ms bi-streaming, instruct dimensions); `Roadmap` section (2025/12 base+RL+script+Gradio release, 2025/08 Triton TRT-LLM + GRPO credit, 2025/07 eval set, 2025/05 vLLM, 2024/12 25 Hz 0.5B, earlier streaming/RAS/flow-matching/FastAPI/WeText entries); `Evaluation` table (base row 1.21%/78.0%, 2.24%/71.8%, 6.71%/75.8%; RL row 0.81%/77.4%, 1.68%/69.5%, 5.44%/75.0%; CosyVoice2 and baseline rows; human reference); `Install / Clone and install` fences (recursive clone, submodule retry, conda python=3.10, aliyun requirements, sox packages); `Model download` fences (`snapshot_download` calls, `ttsfrd` unzip + wheel installs, WeText fallback note); `Basic Usage` fences (`AutoModel`, `inference_zero_shot` en/zh prompts, `inference_cross_lingual` `[breath]` passage with `tokenizer.py#L280` pointer, `inference_instruct2` Cantonese and fast-speech prompts with `common.py#L28` pointer, hotfix `[j][ǐ]` example, `torchaudio.save` at `sample_rate`, `stream=False`); `Discussion & Communication`, `Acknowledge`, `Citations`, and `Disclaimer` sections.
