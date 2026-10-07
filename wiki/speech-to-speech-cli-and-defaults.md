---
type: Concept
title: Speech-to-Speech CLI and Defaults
description: Exact dataclass defaults behind the HF speech-to-speech CLI for module/selector arguments, realtime server, VAD and Smart Turn, Qwen3-TTS, OmniVoice, OpenAI-compatible STT/TTS, Qwen3-ASR, and LLM base arguments.
tags: [vad, stt, tts, llm, pipeline, configuration]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T14:53:00Z }
stale_after: 2027-10-07
sources:
  - id: s2s-supporting-docs
    resource: ../raw/speech-to-speech-docs/README.md
    scope: ../raw/speech-to-speech-docs/
    kind: documentation
    revision: f9c23282a564cbe5b1f015ccb36d58e941de8520
    title: huggingface/speech-to-speech supporting docs
---

The [HF speech-to-speech pipeline](speech-to-speech-pipeline.md) builds its CLI from dataclass argument groups whose defaults are the runtime truth behind the README: selectors default to `--stt parakeet-tdt`, `--llm_backend responses-api`, and `--tts qwen3`, the server binds `127.0.0.1:8765` with one pipeline, VAD defaults are Silero at `--thresh 0.6` with Smart Turn enabled, and the OpenAI-compatible and per-backend argument classes define the remaining connection, device, and synthesis defaults (**Observed** by static inspection of the captured argument classes).[^s2s-supporting-docs]

## Module and selector arguments

- `diarization=False`, `diarization_model_name=None` (an optional Transformers streaming checkpoint adds session-local speaker metadata to LLM input), `diarization_revision=None`, `diarization_device="auto"` (auto selects CUDA then MPS then CPU, and the global `--device` overrides it), `diarization_dtype="float32"` (`float32`/`float16`/`bfloat16`), `diarization_streaming_mode="low_latency"` (`low_latency`/`very_low_latency`/`ultra_low_latency`), and `diarization_threshold=0.5` (**Observed**).[^s2s-supporting-docs]
- `detect_llm_output_language=False` (detect each assistant chunk's language before TTS and pass it on; no code for an initial chunk too short or ambiguous to classify; the detector is warmed at startup) and `device=None` (when set, overrides the device for all handlers) (**Observed**).[^s2s-supporting-docs]
- `mac_optimal_settings=False`: when set, provides macOS defaults of Parakeet TDT STT, MLX LM, Qwen3-TTS, and MPS for supported components, with explicit component, model, global-device, and component-device flags overriding; it does not select a command (**Observed**).[^s2s-supporting-docs]
- `stt="parakeet-tdt"` with choices from the STT registry; `"none"` sends VAD audio directly to an audio-input LLM and requires an explicitly audio-capable `--model_name`. `llm_backend="responses-api"` and `tts="qwen3"` select from their registries; `log_level="info"` (**Observed**).[^s2s-supporting-docs]
- `log_transcripts=False` keeps the application log free of full user/assistant transcript text because service managers, containers, and hosted log aggregators retain logs beyond the conversation (**Observed**).[^s2s-supporting-docs]
- `enable_live_transcription=True` (documented as working with Parakeet TDT) with `live_transcription_update_interval=0.5` seconds (**Observed**).[^s2s-supporting-docs]
- `enable_llm_proxy=False` exposes a proxy-capable LLM backend as an OpenAI-compatible HTTP endpoint with no authentication of its own; `llm_proxy_connect_timeout_s=10.0` bounds upstream connect (reads have no timeout because generation may take minutes) (**Observed**).[^s2s-supporting-docs]
- `num_pipelines=1` sets the number of isolated pipeline instances in the pool; one server routes each client to the next free pipeline, maximum concurrent WebSocket sessions equals `num_pipelines`, and further connections are rejected (**Observed**).[^s2s-supporting-docs]

## Server arguments

- `RealtimeServerArguments` defaults to `host="127.0.0.1"` (network exposure requires an explicit `--host 0.0.0.0`, which exposes the unauthenticated API) and `port=8765`; `LocalRealtimeServerArguments` uses the same `port=8765` for the loopback server and audio client (**Observed**).[^s2s-supporting-docs]

## VAD and Smart Turn arguments

- `vad="silero"` (`silero`/`firered`); FireRed requires the `fireredvad` extra and `vad_firered_model_dir` pointing at Stream-VAD weights containing `cmvn.ark`, with `vad_firered_use_gpu=False` (**Observed**).[^s2s-supporting-docs]
- Level and segment defaults: `thresh=0.6`, `sample_rate=16000`, `min_silence_ms=64`, `min_speech_ms=384`, `min_speech_continuation_ms=192` (hysteresis for speech continuing a soft-ended uncommitted turn; `0` disables the split and falls back to `min_speech_ms`; clamped to `[100, min_speech_ms]`; new turns and barge-ins always require `min_speech_ms`), `max_speech_ms=inf`, and `speech_pad_ms=500` (**Observed**).[^s2s-supporting-docs]
- `audio_enhancement=False`; `enable_realtime_transcription=False` with `realtime_processing_pause=0.5` seconds for progressive audio release during speech (**Observed**).[^s2s-supporting-docs]
- Reopen and merge: `speculative_reopen_ms=800`; `unanswered_reopen_ms=7000` (sanity cap for a soft-ended speculative turn not yet answered, no effect below `speculative_reopen_ms`, clamped to `smart_turn_max_wait_ms` when Smart Turn is on); `short_segment_merge_ms=0` (when positive, adjacent VAD segments below `min_speech_ms` are held and stitched before discard, fragments under 100 ms of active speech are never held, useful with very low `min_silence_ms`) (**Observed**).[^s2s-supporting-docs]
- Smart Turn: `smart_turn=True` (`--no_smart_turn` disables); `smart_turn_model_path=None` downloads the latest supported v3.2 CPU model from `pipecat-ai/smart-turn-v3`; `smart_turn_threshold=0.5`; `smart_turn_max_wait_ms=2000`; `smart_turn_incomplete_delay_ms=600`; `smart_turn_cpu_count=1` ONNX threads per inference (**Observed**).[^s2s-supporting-docs]

## Qwen3-TTS arguments

- `qwen3_tts_model_name="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"` (Apple Silicon auto-maps `Qwen/*` to `mlx-community/*` and defaults to the 6bit variant unless the name pins a suffix); `qwen3_tts_device="cuda"` for the torch backend; `qwen3_tts_dtype="auto"`; `qwen3_tts_attn_implementation="eager"` (recommended on Jetson) (**Observed**).[^s2s-supporting-docs]
- `qwen3_tts_backend="ggml"` (`ggml`/`torch`; mlx-audio is selected automatically on Apple Silicon and this flag is ignored); `qwen3_tts_ggml_quantization="BF16"` (`BF16`/`Q8_0`/`Q4_K_M`/`F32`); local GGUF requires `qwen3_tts_gguf_talker_path` and `qwen3_tts_gguf_codec_path` together and the GGML backend (**Observed**).[^s2s-supporting-docs]
- Voice cloning: `qwen3_tts_ref_cache_dir=None` (faster-qwen3-tts default cache when unset), `qwen3_tts_ref_audio=None` (leave unset for CustomVoice), `qwen3_tts_ref_spk=None` (mutually exclusive with `ref_audio`), `qwen3_tts_ref_rvq=None` (requires `ref_spk` and `ref_text`), and `qwen3_tts_ref_text` defaulting to a fixed sample sentence (**Observed**).[^s2s-supporting-docs]
- `qwen3_tts_speaker="Aiden"` (falls back to the first supported speaker when not provided); `qwen3_tts_instruct=None` (VoiceDesign); `qwen3_tts_xvec_only=False`; `qwen3_tts_parity_mode=False`; `qwen3_tts_non_streaming_mode=True` (pre-fills the full target text before decode on faster-qwen3-tts; currently ignored on Apple Silicon) (**Observed**).[^s2s-supporting-docs]
- `qwen3_tts_mlx_quantization="6bit"` (`bf16`/`4bit`/`6bit`/`8bit`); `qwen3_tts_language="auto"`; `qwen3_tts_streaming_chunk_size=None` uses a backend default of 8 on faster-qwen3-tts and 4 on mlx-audio; `qwen3_tts_max_new_tokens=1536` caps codec tokens (~12 tokens per second of audio, raise above 1536 for longer utterances); `qwen3_tts_blocksize=512` samples (**Observed**).[^s2s-supporting-docs]

## OmniVoice TTS arguments

- `omnivoice_model_name="k2-fsa/OmniVoice"`; `omnivoice_device="auto"` (`auto`/`cuda`/`cuda:0`/`npu`/`xpu`/`mps`/`cpu`); `omnivoice_dtype="float16"` (`float16`/`bfloat16`/`float32`); `omnivoice_num_steps=32`; `omnivoice_speed=1.0`; `omnivoice_blocksize=512` (**Observed**).[^s2s-supporting-docs]
- Voice control: `omnivoice_ref_audio=None` requires `omnivoice_ref_text`; `omnivoice_voice_clone_prompt=None` replaces the audio/text pair; `omnivoice_ref_voices_dir=None` accepts per-language `<language>.wav` plus matching `<language>.txt` and selects by exact code then base language with a default fallback; `omnivoice_instruct=None` is the voice-design instruction; `omnivoice_language=None` falls back to the per-utterance pipeline language (**Observed**).[^s2s-supporting-docs]

## OpenAI-compatible STT/TTS arguments

- STT HTTP: `openai_stt_base_url="http://localhost:8000/v1"`, `openai_stt_api_key=None` (`OPENAI_API_KEY` is used only for `https://api.openai.com/v1`), `openai_stt_model="nvidia/parakeet-tdt-0.6b-v3"`, `openai_stt_language=None`, `openai_stt_response_format="json"`, `openai_stt_timeout=60.0` (**Observed**).[^s2s-supporting-docs]
- Realtime STT: `openai_realtime_stt_base_url="wss://api.openai.com/v1"`, `openai_realtime_stt_model="gpt-live-transcribe"`, `openai_realtime_stt_audio_sample_rate=24000`, `openai_realtime_stt_connect_timeout=10.0`, `openai_realtime_stt_final_timeout=60.0` (**Observed**).[^s2s-supporting-docs]
- TTS: `openai_tts_base_url="http://localhost:8091/v1"`, `openai_tts_model="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"`, `openai_tts_voice="aiden"`, `openai_tts_task_type=None` (vLLM-Omni `CustomVoice`/`VoiceDesign`/`Base`), `openai_tts_instructions=None`, `openai_tts_response_format="pcm"` (`pcm`/`wav`), `openai_tts_sample_rate=24000`, `openai_tts_speed=1.0`, `openai_tts_stream=False`, `openai_tts_timeout=300.0`, `openai_tts_blocksize=512` (**Observed**).[^s2s-supporting-docs]

## Qwen3-ASR and LLM arguments

- Qwen3-ASR: `qwen3_asr_model_name="Qwen/Qwen3-ASR-0.6B-hf"` (the `1.7B-hf` checkpoint is more accurate and needs about 4 GB VRAM), `qwen3_asr_device="auto"` (first of CUDA, NPU, XPU, MPS, CPU), `qwen3_asr_torch_dtype="auto"` (bfloat16 on CUDA, float16 on MPS, float32 on CPU), `qwen3_asr_language="auto"`, `qwen3_asr_prompt=None` (context/hotwords), `qwen3_asr_gen_max_new_tokens=256` (**Observed**).[^s2s-supporting-docs]
- Chat-completions inherits the Responses-API connection fields (`responses_api_base_url` / `responses_api_api_key` / `responses_api_stream` / `responses_api_disable_thinking`) and adds `responses_api_reasoning_effort=None`, sent as `extra_body={'reasoning_effort': <value>}` for providers that ignore `chat_template_kwargs.enable_thinking`; when unset it falls back to disable-thinking behavior (**Observed**).[^s2s-supporting-docs]
- LLM base: `model_name="Qwen/Qwen3-4B-Instruct-2507"`, `user_role="user"`, `init_chat_role="system"`, `init_chat_prompt` a default concise-assistant prompt, `chat_size=30`, `stream_batch_sentences=3` (set to 1 for sentence-by-sentence streaming), `enable_lang_prompt=False`, `compact_history=True` (background summarization once chat exceeds `chat_size`, adding an extra LLM call per compaction) (**Observed**).[^s2s-supporting-docs]

## Relationships

- Part of [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md): these argument classes are the implementation behind that concept's documented flags and defaults (**Synthesis**).[^s2s-supporting-docs]
- The VAD group drives [Silero VAD](silero-vad.md) and the FireRed alternative recorded in [turn-detection models](turn-detection-models.md); the TTS groups configure [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md), [Faster Qwen3-TTS](faster-qwen3-tts.md), and [OmniVoice](omnivoice.md) / [G-OmniVoice](g-omnivoice.md); the STT groups configure [Qwen3-ASR family](qwen3-asr-family.md) and the models in [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](speech-to-speech-openai-compatible-backends.md) (**Synthesis**).[^s2s-supporting-docs]
- The measured timing fields that consume the `vad_decision_s`, `smart_*`, and stage settings are defined in [Speech-to-Speech Response Latency Instrumentation](speech-to-speech-latency-instrumentation.md) (**Synthesis**).[^s2s-supporting-docs]

## Coverage and limits

- Source inspected statically only: the 11 captured argument-class files are code, but only their dataclass defaults and help text were read; no CLI was run, no flag was passed, and no parser behavior was executed, so the defaults are **Observed** in code while their runtime effect is **Reported** by the accompanying guides (**Synthesis**).[^s2s-supporting-docs]
- The capture excludes `responses_api_language_model_arguments.py`, which `chat_completions_language_model_arguments.py` imports and the `responses-api` default path uses, so the Responses-API-specific defaults are not established here; the base `model_name` default `Qwen/Qwen3-4B-Instruct-2507` therefore differs from the documented `serve` default `gpt-5.6-terra`, and which layer overrides the other cannot be resolved from the captured files (**Synthesis**).[^s2s-supporting-docs]
- Also excluded by the capture are other argument classes (e.g. kokoro/pocket/supertonic/facebookMMS handlers, MLX/torch LLM splits, diarization arguments), so this page does not cover the full CLI despite the TTS handler README listing those backends (**Synthesis**).[^s2s-supporting-docs]
- Numeric defaults, flag names, model identifiers, and enum choices carry `stale_after: 2027-10-07` under the `vad`/`stt`/`tts`/`llm`/`pipeline` domain rules (**Synthesis**).[^s2s-supporting-docs]

[^s2s-supporting-docs]: [huggingface/speech-to-speech supporting docs](../raw/speech-to-speech-docs/README.md) — a capture at upstream revision `f9c23282a564cbe5b1f015ccb36d58e941de8520` (2026-10-07). Locators: `src/speech_to_speech/arguments_classes/module_arguments.py` (all module/selector fields), `realtime_server_arguments.py` (`RealtimeServerArguments`, `LocalRealtimeServerArguments`), `vad_arguments.py` (all VAD/Smart Turn fields), `qwen3_tts_arguments.py` (all Qwen3-TTS fields), `omnivoice_tts_arguments.py` (all OmniVoice fields), `openai_stt_arguments.py`, `openai_realtime_stt_arguments.py`, `openai_tts_arguments.py` (connection and audio fields), `qwen3_asr_stt_arguments.py` (model/device/language/prompt/token fields), `chat_completions_language_model_arguments.py` (inheritance plus `responses_api_reasoning_effort`), and `language_model_base_arguments.py` (base LLM fields); `src/speech_to_speech/STT/README.md` and `TTS/README.md` supply the runtime backend lists and example flags. Limitations: 11 of the repository's argument classes are captured (the manifest excludes the rest as irrelevant to the PoC), `responses_api_language_model_arguments.py` is not captured, and no CLI execution or parser test was performed.
