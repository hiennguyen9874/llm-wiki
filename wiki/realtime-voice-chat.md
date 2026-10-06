---
type: Concept
title: RealtimeVoiceChat
description: Client-server realtime voice-chat pipeline combining browser capture, RealtimeSTT, pluggable Ollama/OpenAI LLM, and RealtimeTTS with barge-in and Docker deployment.
tags: [stt, llm, tts, vad, pipeline, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: realtimevoicechat-readme
    resource: ../raw/RealtimeVoiceChat.md
    kind: documentation
    title: Real-Time AI Voice Chat README
---

RealtimeVoiceChat by KoljaB is an MIT-licensed client-server system for spoken conversation with an LLM, chaining browser microphone capture over WebSockets to a Python backend that transcribes with `RealtimeSTT`, reasons with Ollama or OpenAI, synthesizes with `RealtimeTTS`, streams audio back, and supports barge-in interruption (**Reported**).[^realtimevoicechat-readme]

## Identity and status

- Project `KoljaB/RealtimeVoiceChat`, described as an early-preview first reasonably stable version; core codebase MIT-licensed, with external TTS engines such as Coqui XTTSv2 and LLM providers carrying their own license terms (**Reported**).[^realtimevoicechat-readme]
- Maintenance posture is community-driven: the author states they no longer implement features or provide support but will review and merge high-quality pull requests from time to time (**Reported**).[^realtimevoicechat-readme]
- Intended outcome is fluid conversation with realtime feedback: partial transcriptions and AI responses surface as they happen over an audio-chunk streaming architecture aimed at low latency (**Reported**).[^realtimevoicechat-readme]

## Pipeline architecture

- Seven-step loop: browser capture, WebSocket audio-chunk streaming to Python backend, `RealtimeSTT` transcription, LLM processing, `RealtimeTTS` synthesis, audio streaming back to the browser, and graceful interruption handling (**Reported**).[^realtimevoicechat-readme]
- Turn-taking uses dynamic silence detection in `turndetect.py` that adapts to conversation pace, plus explicit interrupt support for jumping in mid-response (**Reported**).[^realtimevoicechat-readme]
- Frontend is Vanilla JS with the Web Audio API and AudioWorklets; backend is FastAPI on Python below 3.13 with `torch`/`torchaudio`, `transformers` for turn detection and tokenization, `ollama`/`openai` clients, and `numpy`/`scipy` audio processing (**Reported**).[^realtimevoicechat-readme]
- Pluggable brains via `llm_module.py` (Ollama default, OpenAI supported) and pluggable voices via `audio_module.py` (Kokoro, Coqui, Orpheus engine choices) (**Reported**).[^realtimevoicechat-readme]

## Configuration

- TTS: set `START_ENGINE` in `server.py` to `coqui`, `kokoro`, or `orpheus`; engine-specific voice model path for Coqui, speaker ID for Orpheus, and speed live in `AudioProcessor.__init__` in `audio_module.py` (**Reported**).[^realtimevoicechat-readme]
- LLM: set `LLM_START_PROVIDER` (`ollama` or `openai`) and `LLM_START_MODEL` in `server.py`; personality is edited in `system_prompt.txt`; the Docker recipe pulls the default `hf.co/bartowski/huihui-ai_Mistral-Small-24B-Instruct-2501-abliterated-GGUF:Q4_K_M` into the Ollama container after startup (**Reported**).[^realtimevoicechat-readme]
- STT: `DEFAULT_RECORDER_CONFIG` in `transcribe.py` controls the Whisper model, language, and `silence_limit_seconds`; the default `base.en` model is pre-downloaded during the Docker build (**Reported**).[^realtimevoicechat-readme]
- Turn detection: pause-duration constants in `TurnDetector.update_settings` in `turndetect.py` (**Reported**).[^realtimevoicechat-readme]
- Network security: `USE_SSL`, `SSL_CERT_PATH`, and `SSL_KEY_PATH` in `server.py`; Docker users map the SSL port and mount certificates, with a `mkcert` localhost recipe documented for Windows (**Reported**).[^realtimevoicechat-readme]

## Deployment and hardware

- Docker Compose is the recommended path on Linux with GPU: `docker compose build` (customize `code/*.py` first), `docker compose up -d`, pull the Ollama model with `docker compose exec ollama ollama pull <model>`, with `logs -f app`/`ollama` and `down`/`up -d` lifecycle commands (**Reported**).[^realtimevoicechat-readme]
- Manual path: create and activate a venv, upgrade pip, install a matching PyTorch build inside `code/` (CUDA 12.1 example pins `torch==2.5.1+cu121` plus matching `torchaudio`), then `pip install -r requirements.txt`; the Windows `install.bat` attempts venv plus PyTorch CUDA 12.1 plus a precompiled DeepSpeed wheel (**Reported**).[^realtimevoicechat-readme]
- Hardware expectation: a powerful CUDA-enabled NVIDIA GPU is highly recommended, especially for Whisper STT and Coqui TTS; CPU-only or weak GPUs are significantly slower; Linux Docker GPU access requires the NVIDIA Container Toolkit (**Reported**).[^realtimevoicechat-readme]
- DeepSpeed is the fragile dependency: manual installation can fail on Windows and may need source builds or third-party patchers used at the user's own risk; Coqui TTS performance benefits most from it (**Reported**).[^realtimevoicechat-readme]
- Client access is `http://localhost:8000` with microphone permission, then Start/Stop/Reset controls; manual servers start with `python server.py` from `code/` after activating the venv (**Reported**).[^realtimevoicechat-readme]
- Authentication note: only the `OPENAI_API_KEY` environment variable name is documented for the OpenAI backend; no secret value is present in the source (**Observed** by static inspection).[^realtimevoicechat-readme]

## Relationships

- Uses [RealtimeSTT](realtimestt.md): that page is the library reference for the transcription stage used here; consult it for VAD-gated recording, engine profiles, and the production-server path when tuning `transcribe.py` settings (**Synthesis**).[^realtimevoicechat-readme]
- Complements [Community-Reported Usable STT for Voice Agents](community-usable-stt-voice-agents.md): that draft's checklist on first stable text, partial stability, endpointing, barge-in, and per-turn logs is the evaluation lens for this pipeline's partial-transcription display, dynamic silence detection, and interruption support (**Synthesis**).[^realtimevoicechat-readme]
- Compare with [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): that LLM-generated draft describes a `generation_id` cancellation and AEC design for the same browser-WebSocket interruption problem this project implements (**Synthesis**).[^realtimevoicechat-readme]
- Contrasts with [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md) and [PersonaPlex 7B v1](personaplex-7b-v1.md): those are open end-to-end full-duplex speech-to-speech models, while this is a cascaded STT–LLM–TTS integration around `RealtimeSTT`/`RealtimeTTS`; compare them when choosing cascaded controllability versus integrated full-duplex turn-taking (**Synthesis**).[^realtimevoicechat-readme]

## Coverage and limits

- Source inspected statically only; no Docker build, `pip install`, model pull, server launch, microphone session, or latency measurement was executed, so all install, configuration, performance, and recommendation claims are transcribed source assertions without independent verification in this wiki (**Synthesis**).[^realtimevoicechat-readme]
- Referenced but unfetched and absent from `raw/`: `code/` modules (`server.py`, `audio_module.py`, `llm_module.py`, `transcribe.py`, `turndetect.py`, `system_prompt.txt`), `docker-compose.yml`, Dockerfiles, `requirements.txt`, `install.bat`, `LICENSE`, and the demo video URL; effective defaults, interfaces, and defects in those files are not established here (**Synthesis**).[^realtimevoicechat-readme]
- Install, API, model-ID, and compatibility details (Python below 3.13, CUDA 12.1, pinned Torch builds, default Ollama GGUF ID, engine option names) carry `stale_after: 2027-10-06` per the `stt`/`vad`/`tts`/`llm` domain rules (**Synthesis**).[^realtimevoicechat-readme]

[^realtimevoicechat-readme]: [Real-Time AI Voice Chat README](../raw/RealtimeVoiceChat.md) — locators: title/intro plus demo-video link (spoken LLM conversation, early-preview stable claim); `Project Status: Community-Driven` callout (no active maintenance, PR review only); `What's Under the Hood?` 7-step pipeline (capture, WebSocket stream, `RealtimeSTT`, LLM, `RealtimeTTS`, return playback, interrupt); `Key Features` (fluid conversation, partial-transcription/response feedback, chunk-streaming latency, `turndetect.py` dynamic silence, `llm_module.py` Ollama/OpenAI, `audio_module.py` Kokoro/Coqui/Orpheus, Vanilla JS plus Web Audio API plus AudioWorklets, Docker Compose); `Technology Stack` (Python <3.13 FastAPI; HTML/CSS/JS; WebSockets; Docker; `RealtimeSTT`, `RealtimeTTS`, `transformers`, `torch`/`torchaudio`, `ollama`/`openai`, `numpy`/`scipy`); `Prerequisites` (Linux Docker GPU guidance, `install.bat` Windows, Python 3.9+, CUDA GPU recommendation with Whisper/Coqui emphasis, CUDA 12.1 assumption, NVIDIA Container Toolkit, Docker Engine plus Compose v2+, Ollama, `OPENAI_API_KEY`); `Installation` Option A Docker fences (`build`, `up -d`, `exec ollama ollama pull hf.co/bartowski/huihui-ai_Mistral-Small-24B-Instruct-2501-abliterated-GGUF:Q4_K_M`, `list`, `down`, `logs -f`); Option B manual fences (venv, `pip install --upgrade pip`, `cd code`, `torch==2.5.1+cu121` CUDA fence, CPU-only fence, `pip install -r requirements.txt`, DeepSpeed Windows note plus `deepspeedpatcher` risk note); `Running the Application` (`server.py`, `http://localhost:8000`, mic permission, Start/Stop/Reset); `Configuration Deep Dive` (`START_ENGINE`, `AudioProcessor.__init__`, `LLM_START_PROVIDER`/`LLM_START_MODEL`, `system_prompt.txt`, `DEFAULT_RECORDER_CONFIG` with `base.en` Docker pre-download, `TurnDetector.update_settings`, `USE_SSL`/`SSL_CERT_PATH`/`SSL_KEY_PATH` plus `mkcert` recipe); `Contributing`; `License` (MIT core plus Coqui XTTSv2/LLM-provider terms).
