---
type: Concept
title: Ultravox
description: Fast multimodal speech LLM that maps audio directly into LLM embedding space without a separate ASR stage, with Llama 3.3 70B default, 8B variant, and adapter-only training.
tags: [llm, stt, multimodal, realtime]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:53:22Z }
stale_after: 2027-10-06
sources:
  - id: ultravox-readme
    resource: ../raw/ultravox.md
    kind: documentation
    title: Ultravox GitHub repository README
---

Ultravox is Fixie.ai's fast multimodal LLM for real-time voice interaction that understands text and human speech without a separate ASR stage by using a multimodal projector to convert audio directly into the LLM's high-dimensional embedding space, shipping as a Llama 3.3 70B default plus an 8B variant with audio-in streaming-text-out behavior, managed Realtime APIs, and an adapter-only training workflow for new backbones or languages (**Reported**).[^ultravox-readme]

## Model identity and releases

- Name is Ultravox, subtitled "A fast multimodal LLM designed for real-time voice interactions"; publisher is Fixie.ai via `github.com/fixie-ai/ultravox`, Hugging Face org `fixie-ai`, Realtime platform at `ultravox.ai`, demo at `demo.ultravox.ai`, and docs at `docs.ultravox.ai` (**Reported**).[^ultravox-readme]
- Release history in the capture's Latest News section runs v0.3 (2024/08), v0.4 (2024/08), v0.4.1 (2024/11), v0.5 (2025/02), v0.6 (2025/06), and v0.7 (2025/12, latest named); each entry links a Hugging Face collection or GitHub release tag except v0.7 and v0.6 which link Hugging Face collections (**Reported**).[^ultravox-readme]
- Default model is built on Llama 3.3 70B with an 8B variant available on Hugging Face; the project also reports trained versions on Llama 3, Mistral, and Gemma backbones and states Ultravox can be trained against any open-weight model (**Reported**).[^ultravox-readme]
- Research lineage named in the About section is AudioLM, SeamlessM4T, Gazelle, and SpeechGPT (**Reported**).[^ultravox-readme]
- No license, parameter count for the projector/adapter, supported-language list, or benchmark numbers appear in the captured README text (**Synthesis**).[^ultravox-readme]

## Architecture and I/O

- Architecture extends any open-weight LLM with a multimodal projector/adapter that converts audio directly into the LLM's high-dimensional space; the direct coupling is claimed to respond much more quickly than systems combining separate ASR and LLM components (**Reported**).[^ultravox-readme]
- Stated future direction is natively understanding paralinguistic cues of timing and emotion omnipresent in human speech (**Reported**).[^ultravox-readme]
- Current I/O is audio in and streaming text out; the roadmap is to emit a stream of speech tokens convertible directly into raw audio by an appropriate unit vocoder, which is not yet the captured behavior (**Reported**).[^ultravox-readme]
- An architecture diagram image is linked in the capture but its nodes and data flow are not transcribed in text, so structural detail here comes from prose only (**Synthesis**).[^ultravox-readme]

## Inference and deployment

- Interactive demo is hosted at `demo.ultravox.ai`; voice-to-voice agents can be built on the Realtime platform at `ultravox.ai` (**Reported**).[^ultravox-readme]
- Offline-style trial path is an Ultravox instance on partner BaseTen accepting user WAV audio, with free starting credits noted; real-time use points to managed APIs documented at `docs.ultravox.ai` (**Reported**).[^ultravox-readme]
- Weights are distributed via the Ultravox Hugging Face page; no checkpoint filename, quantization, GGUF/edge packaging, latency figure, or API pricing appears in the capture (**Synthesis**).[^ultravox-readme]

## Training and adaptation

- Training freezes both the LLM and the audio encoder and trains only the adapter/projector; v0.4 training cost is stated as 2–3 hours on 8×H100 GPUs for 14K steps (**Reported**).[^ultravox-readme]
- Three retraining motives are documented: a different LLM or audio-encoder backbone by re-training the adapter via `example_config.yaml` with `--text-model <hf-model-id-for-llm>` and/or `--audio-model <hf-model-id-for-encoder>`; better model knowledge preferably via RAG or by fine-tuning the LLM backbone without re-training Ultravox; and new-language or own-audio-data support by preparing samples with at least `audio` and text `continuation` fields using `ultravox/tools/ds_tool/ds_tool.py` plus `continuation.jinja` (with a Common Voice 17.0 French variant cited as example) and adding the dataset to the mix in `example_config.yaml` (**Reported**).[^ultravox-readme]
- Environment setup is Mac-oriented: Homebrew, `just`, pyenv with Python 3.11, `just install` for Poetry dependencies, optional `just install-augs-system` for augmentation system packages, with conda explicitly not recommended alongside Poetry (**Reported**).[^ultravox-readme]
- Training launch is `poetry run python -m ultravox.training.train --config_path ultravox/training/configs/example_config.yaml`, with weight prefetch via `ultravox.training.helpers.prefetch_weights` and DDP via `torchrun --nproc_per_node=8`; debug runs use smaller models, datasets, or batch size, e.g. TinyLlama config `ultravox/training/configs/asr_tinyllama_100s.yaml` with `--batch_size 1 --report_logs_to tensorboard`; configs use SimpleParsing composition with `meta_config.yaml` as default and tunable parameters in `ultravox/training/config_base.py` such as `--text-model`, `--device`, and `--exp-name` (**Reported**).[^ultravox-readme]
- Multi-node training updates the `compute.gpus` line in `mcli_train.yaml` with all factors of 8 supported; beyond 4 nodes `val_dataset_args.max_samples` may need increasing; W&B is noted as main-node-only (**Reported**).[^ultravox-readme]
- Evaluation is `just eval --config_path ultravox/evaluation/configs/eval_config.yaml`; new datasets need a config in `ultravox/data/configs/` with an `eval_config` metrics field plus registration in `ultravox/data/registry.py` (**Reported**).[^ultravox-readme]
- Common `Justfile` commands are `just update` (dependencies), `just format` (black/isort/autoflake), `just test`, and `just python` (venv python); most training tooling and docs assume the MosaicML platform, which the capture notes was being shut down at end of July 2025 while leaving its configs in place (**Reported**).[^ultravox-readme]

## Relationships

- Collapsed-pipeline alternative to [Community-Reported STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md): that concept wires separate single-GPU STT, LLM, and TTS HTTP services with VAD and sentence-chunked streaming, while Ultravox removes the standalone ASR stage by projecting audio straight into the LLM; no shared checkpoint or serving code is asserted (**Synthesis**).[^ultravox-readme]
- End-to-end comparison with [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md): VoiceChat is an 11B open full-duplex speech-to-speech model with ~450 ms turn-taking and tool calling, while Ultravox in this snapshot is audio-in streaming-text-out with a future speech-token plus unit-vocoder path; no shared vendor or benchmark is asserted (**Synthesis**).[^ultravox-readme]
- Realtime-dialogue comparison with [Step-Audio-R1.1](step-audio-r1-1.md): Step-Audio-R1.1 targets interactive spoken dialogue with dual-brain thinking-while-speaking and acoustic-grounded reasoning on 4 GPUs, while Ultravox targets faster response via direct audio-to-LLM projection with adapter-only retraining; no shared vendor or codebase is asserted (**Synthesis**).[^ultravox-readme]
- Modular-pipeline contrast with [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md): that pipeline exposes swappable VAD, STT, LLM, and TTS backends over the OpenAI Realtime event set, while Ultravox unifies the STT-plus-LLM portion into one multimodal model; no integration between the two is asserted (**Synthesis**).[^ultravox-readme]

## Coverage and limits

- Source inspected statically only; no environment installed, no training launched, no checkpoint downloaded, no WAV transcribed, and no latency or quality claim reproduced (**Synthesis**).[^ultravox-readme]
- Linked but unfetched and uninspected: Hugging Face collections and weights, Ultravox Realtime/demo/docs pages, BaseTen library entry, Discord invite, careers page, architecture-diagram asset and its linked slide deck, augmentation guide, `setup.sh`, `Justfile`, `example_config.yaml`, training/eval/dataset configs, `ds_tool` scripts, and the cited AudioLM/SeamlessM4T/Gazelle/SpeechGPT research (**Synthesis**).[^ultravox-readme]
- All architecture, latency, release, and training-cost claims are source assertions without independent verification in this wiki; model-release and API details carry `stale_after: 2027-10-06` per the `llm` domain rule (**Synthesis**).[^ultravox-readme]

[^ultravox-readme]: [Ultravox GitHub repository README](../raw/ultravox.md) — locators: header subtitle (multimodal LLM for real-time voice); `Latest News` list (v0.3 2024/08 through v0.7 2025/12); `Key Links` (Realtime, Hugging Face); `About` paras 1–2 (no separate ASR, AudioLM/SeamlessM4T/Gazelle/SpeechGPT lineage, projector into LLM space, Llama 3/Mistral/Gemma training, faster-response claim, paralinguistic future, audio-in streaming-text-out, future speech tokens plus unit vocoder); `About` (Llama 3.3 70B default, 8B variant, any open-weight model); `Demo`, `Inference Server` (demo page, ultravox.ai Realtime, BaseTen WAV plus credits, managed APIs docs); `Model`, `Architecture` (HF weights link, diagram image); `Environment Setup (Mac)` (Homebrew/Just/pyenv 3.11/`just install`/`just install-augs-system`, Poetry, conda note); `Training` (frozen LLM plus encoder, adapter-only, v0.4 2–3h on 8×H100 for 14K steps); `Use-Cases` items 1–3 (`example_config.yaml`, `--text-model`/`--audio-model`, RAG vs fine-tune, `audio` plus `continuation`, `ds_tool.py`/`continuation.jinja`, Common Voice variant); `How to Train` (MosaicML shutdown July 2025, `setup.sh`, `train --config_path`, `prefetch_weights`, `torchrun --nproc_per_node=8`, TinyLlama debug config, SimpleParsing/`meta_config.yaml`/`configs_base.py`); `Multi-node training` (`compute.gpus`, factors of 8, `val_dataset_args.max_samples`, W&B note); `Running evaluations` (`just eval`, `eval_config.yaml`, `ultravox/data/configs/`, `registry.py`); `Misc` (`just update/format/test/python`).
