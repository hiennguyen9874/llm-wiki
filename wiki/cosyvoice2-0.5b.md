---
type: Concept
title: CosyVoice2-0.5B
description: LLM-based streaming zero-shot TTS model with 0.5B parameters, multilingual voice cloning, instruct and cross-lingual control, and vLLM and streaming inference support.
tags: [ml, tts, voice-cloning, streaming, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T08:00:00Z }
stale_after: 2027-10-06
sources:
  - id: cosyvoice2-card
    resource: ../raw/CosyVoice2-0.5B.md
    kind: documentation
    title: CosyVoice2-0.5B README and model card
---

CosyVoice2-0.5B is FunAudioLLM's 0.5B-parameter large-language-model text-to-speech system for scalable streaming synthesis, released December 2024 as a 25 Hz model with zero-shot, cross-lingual, instruct, and bi-streaming inference modes plus vLLM serving support added May 2025 (**Reported**).[^cosyvoice2-card]

## Model identity and release

- Name is CosyVoice2-0.5B; family is CosyVoice by FunAudioLLM; weights are `FunAudioLLM/CosyVoice2-0.5B` on Hugging Face and `iic/CosyVoice2-0.5B` on ModelScope; demo site, paper `arXiv:2412.10117`, ModelScope, and Hugging Face links are listed in the header; frontmatter declares `pipeline_tag: text-to-speech`, languages `zh, en, fr, es, ja, ko, it, ru, de`, and license `apache-2.0` (**Reported**, with frontmatter fields **Observed** by static inspection).[^cosyvoice2-card]
- Release history in the roadmap records 25 Hz CosyVoice2-0.5B release in 2024/12, CosyVoice2-0.5B vLLM support in 2025/05, and Triton TRT-LLM runtime plus CosyVoice2 GRPO training support in 2025/08 credited to NVIDIA contributor Yuekai Zhang; earlier family milestones listed include streaming inference with KV cache and SDPA for RTF optimization, Repetition Aware Sampling (RAS) for LLM stability, flow-matching training, FastAPI server/client, and WeTextProcessing fallback (**Reported**).[^cosyvoice2-card]
- Family context lists CosyVoice 1.0 (300M, demos, `arXiv` v1 paper PDF, ModelScope `iic/CosyVoice-300M`, Hugging Face `FunAudioLLM/CosyVoice-300M`) and Fun-CosyVoice 3.0 (demos, `arXiv:2505.17589`, ModelScope `FunAudioLLM/Fun-CosyVoice3-0.5B-2512`, Hugging Face `Fun-CosyVoice3-0.5B-2512`, CV3-Eval); the 3.0 line is compiled separately in [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md) (**Reported**).[^cosyvoice2-card]

## Capabilities and inference modes

- Zero-shot voice cloning (`inference_zero_shot`) synthesizes English or Chinese text from a prompt transcript plus prompt audio (e.g. `./asset/zero_shot_prompt.wav`); saved zero-shot speakers can be reused via `add_zero_shot_spk` with a speaker id, `save_spkinfo`, and later `inference_zero_shot` with `zero_shot_spk_id`; passing `text_frontend=False` reproduces the demo-site results (**Reported**).[^cosyvoice2-card]
- Fine-grained paralinguistic control (`inference_cross_lingual`) supports inline tags such as `[laughter]`; supported controls are defined in `cosyvoice/tokenizer/tokenizer.py#L248` per the usage comment (**Reported**).[^cosyvoice2-card]
- Instruct control (`inference_instruct2`) steers output with a natural-language instruction plus `<|endofprompt|>`, e.g. Sichuan-dialect instruction `用四川话说这句话<|endofprompt|>` (**Reported**).[^cosyvoice2-card]
- Bi-streaming usage accepts a text generator as input (with a note that callers should keep basic sentence splitting because the LLM cannot handle arbitrary sentence length), exemplified with `stream=False` in the zero-shot generator example (**Reported**).[^cosyvoice2-card]
- Text normalization uses the `CosyVoice-ttsfrd` resource package by default via WeTextProcessing when the `ttsfrd` package is unavailable; optionally the `ttsfrd` resource is unzipped and installed from `ttsfrd_dependency` and `ttsfrd` wheels for better normalization performance (**Reported**).[^cosyvoice2-card]

## Performance and evaluation

- The evaluation table reports CosyVoice2 (open-source, 0.5B) at test-zh CER 1.45% with 75.7% speaker similarity, test-en WER 2.57% with 65.9% speaker similarity, and test-hard CER 6.83% with 72.4% speaker similarity, alongside human, closed-source (Seed-TTS, MiniMax-Speech), and open-source baselines (F5-TTS, Spark TTS, FireRedTTS2, Index-TTS2, VibeVoice, HiggsAudio-v2, VoxCPM, GLM-TTS, Fun-CosyVoice3 variants) (**Reported**).[^cosyvoice2-card]
- Paper lineage is `CosyVoice: A scalable multilingual zero-shot text-to-speech synthesizer based on supervised semantic tokens` (`arXiv:2407.05407`), `Cosyvoice 2: Scalable streaming speech synthesis with large language models` (`arXiv:2412.10117`), `CosyVoice 3: Towards In-the-wild Speech Generation via Scaling-up and Post-training` (`arXiv:2505.17589`), and an ICASSP 2025 paper on building LLM-based zero-shot streaming TTS with CosyVoice (**Reported**).[^cosyvoice2-card]

## Requirements and installation

- Requires a recursive clone (`git clone --recursive`, with `git submodule update --init --recursive` retry on network failure), Conda, a `cosyvoice` environment with Python 3.10, `pip install -r requirements.txt` (documented via an Aliyun mirror), and sox (`sox libsox-dev` on Ubuntu, `sox sox-devel` on CentOS) (**Reported**).[^cosyvoice2-card]
- Model download uses `huggingface_hub.snapshot_download` for `FunAudioLLM/CosyVoice2-0.5B` into `pretrained_models/CosyVoice2-0.5B` and `FunAudioLLM/CosyVoice-ttsfrd` into `pretrained_models/CosyVoice-ttsfrd`; the `ttsfrd` resource is optionally unzipped from `resource.zip` and installed from its two wheel files (**Reported**).[^cosyvoice2-card]
- Basic usage imports `AutoModel` from `cosyvoice.cli.cosyvoice` (with `third_party/Matcha-TTS` on `sys.path`), constructs `AutoModel(model_dir='pretrained_models/CosyVoice2-0.5B')`, and saves returned `tts_speech` chunks with `torchaudio.save` at `cosyvoice.sample_rate` (**Reported**).[^cosyvoice2-card]
- Acknowledged code sources are FunASR, FunCodec, Matcha-TTS, AcademiCodec, and WeNet; discussion is via GitHub Issues and an official DingDing chat group (QR image linked but not ingested) (**Reported**).[^cosyvoice2-card]

## Relationships

- Predecessor to [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md): this concept covers the 0.5B CosyVoice2 streaming model with saved-speaker reuse and vLLM/TRT-LLM serving mentions, while the successor covers the 0.5B Fun-CosyVoice 3.0 base and RL checkpoints with 9-language plus dialect coverage, Pinyin/CMU inpainting, and 150 ms bi-streaming; neither concept deprecates the other (**Synthesis**).[^cosyvoice2-card]
- TTS voice-cloning comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B multilingual zero-shot TTS model with DualAR architecture and ONNX/SGLang paths, while this concept covers a 0.5B LLM-based streaming TTS model with saved-speaker reuse, cross-lingual and instruct control, and vLLM/TRT-LLM serving mentions; no shared codebase is asserted (**Synthesis**).[^cosyvoice2-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice design/direction and H100 TTFA/RTF figures, while this concept covers a streaming LLM-based TTS model with RAS stability, KV-cache/SDPA streaming optimization, and CER/WER plus speaker-similarity table figures; no shared vendor or codebase is asserted (**Synthesis**).[^cosyvoice2-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no Conda environment created, no checkpoint or `ttsfrd` resource downloaded, no audio synthesized, and no CER, WER, speaker-similarity, latency, or instruction-following claims reproduced (**Synthesis**).[^cosyvoice2-card]
- Local prompt audio (`./asset/zero_shot_prompt.wav`), DingDing QR image, demo pages, papers, ModelScope/Hugging Face repositories, benchmark suites, and license/terms pages were linked but not fetched and are not in `raw/`; checkpoint contents, tokenizer implementation beyond the cited path comment, reference audio, and FastAPI/TRT-LLM/vLLM/GRPO runtime contents were not inspected (**Synthesis**).[^cosyvoice2-card]
- All capability, compatibility, serving, and benchmark claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `ml` domain rule (**Synthesis**).[^cosyvoice2-card]

[^cosyvoice2-card]: [CosyVoice2-0.5B README and model card](../raw/CosyVoice2-0.5B.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`); header model links (CosyVoice 2.0 demos/paper/ModelScope/HuggingFace, 1.0 and 3.0 links); `Highlight` section (3.0 feature context); `Roadmap` section (2024/12 25 Hz 0.5B release, 2025/05 vLLM support, 2025/08 Triton TRT-LLM + GRPO credit, streaming/KV-cache/SDPA, RAS, flow matching, FastAPI, WeTextProcessing entries); `Evaluation` table (CosyVoice2 row: test-zh 1.45%/75.7%, test-en 2.57%/65.9%, test-hard 6.83%/72.4%, plus baseline rows); `Install / Clone and install` fences (recursive clone, submodule retry, conda python=3.10, aliyun requirements, sox packages); `Model download` fences (`snapshot_download` calls, `ttsfrd` unzip + wheel installs, WeText fallback note); `Basic Usage` fences (`AutoModel`, `inference_zero_shot` en/zh, `add_zero_shot_spk`/`save_spkinfo`, `inference_cross_lingual` `[laughter]`, `inference_instruct2` Sichuan-dialect prompt, generator bi-stream example, `text_frontend=False` note, `tokenizer.py#L248` pointer); `Discussion & Communication`, `Acknowledge`, `Citations`, and `Disclaimer` sections.
