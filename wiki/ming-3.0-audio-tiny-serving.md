---
type: Concept
title: Ming-3.0-audio-tiny Serving
description: Deployment routes documented by the Ming-3.0-audio-tiny card — Transformers example scripts, vLLM-Omni text and full-audio profiles with a Thinker/Talker GPU split, single-GPU SGLang for text output, and SGLang-Omni exposing transcription, speech and chat endpoints with built-in and preset voice selection.
tags: [stt, tts, serving, vllm-omni, sglang-omni, streaming]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T13:10:00Z }
stale_after: 2027-04-21
sources:
  - id: ming-audio-tiny-card
    resource: ../raw/inclusionAI-Ming-3.0-audio-tiny.md
    kind: documentation
    title: Ming-3.0-audio-tiny model card capture
---

The [Ming-3.0-audio-tiny](ming-3.0-audio-tiny.md) card documents four runtime families — Hugging Face Transformers example scripts, vLLM-Omni in a text/ASR profile or a full-audio profile that splits Thinker and Talker across two GPUs, a validated single-GPU SGLang profile that serves text, and SGLang-Omni on one GPU with speech synthesis colocated — around one 9.3B-total audio-language checkpoint, with SGLang-Omni exposing OpenAI-compatible transcription, speech and chat endpoints (**Reported**).[^ming-audio-tiny-card] The routes differ mainly in where the Talker runs and whether audio output is reachable at all; the card prints no latency, throughput, concurrency, VRAM or quantization figure for any of them (**Observed** coverage limit).[^ming-audio-tiny-card]

## Route overview

| Route | Output reachable | GPU placement stated by the card | Notes |
| --- | --- | --- | --- |
| Transformers examples | Text; text plus speech via `transformers_thinker_talker.py` | Not stated for the Talker script; the inline Python path uses `device_map="auto"` | Repository clone plus `requirements-transformers.txt`; no version pins[^ming-audio-tiny-card] |
| vLLM-Omni, `MING_OUTPUT_MODE=text` | Text, including ASR | Thinker on one GPU | Deployment YAML selected per text-only / ASR use[^ming-audio-tiny-card] |
| vLLM-Omni, `MING_OUTPUT_MODE=audio` | Text plus synthesized speech | Reference full-audio profile: Thinker on GPU 0, Talker on GPU 1 | Chat Completions `audio.voice` selects the voice[^ming-audio-tiny-card] |
| SGLang | Text only (validated Tiny profile) | One GPU (`CUDA_VISIBLE_DEVICES=0`) | Client example `examples/sglang_audio_chat.py`[^ming-audio-tiny-card] |
| SGLang-Omni | Transcription, chat and speech synthesis | One GPU; `--talker.gpu 0` colocates the Talker | Exposes three OpenAI-compatible endpoints[^ming-audio-tiny-card] |

## vLLM-Omni profiles

The launcher is a wrapper script parameterized by two environment variables, `MING_MODEL_VARIANT` and `MING_OUTPUT_MODE` (**Reported** shells, not run):[^ming-audio-tiny-card]

```bash
export MODEL_PATH=inclusionAI/Ming-3.0-audio-tiny
MING_MODEL_VARIANT=tiny MING_OUTPUT_MODE=text \
  ./scripts/serve_vllm_omni.sh "$MODEL_PATH"
```

```bash
export MODEL_PATH=inclusionAI/Ming-3.0-audio-tiny
MING_MODEL_VARIANT=tiny MING_OUTPUT_MODE=audio \
  ./scripts/serve_vllm_omni.sh "$MODEL_PATH"
```

- The card says text output and ASR use the Tiny Thinker on one GPU, while the reference full-audio profile places the Thinker on GPU 0 and the Talker on GPU 1; the deployment YAML must match text-only, ASR or Talker output (**Reported**).[^ming-audio-tiny-card]
- The audio client is `examples/vllm_omni_audio_chat.py <audio> --audio-response --voice US_Stella --output-audio outputs/answer.wav`; the `--voice` value is sent as Chat Completions `audio.voice: {"id": "..."}` (**Reported**).[^ming-audio-tiny-card]
- When no voice is given, vLLM-Omni uses the built-in IP voice `灵小柔`. The model directory also ships `灵楷` and `US_James` as preset reference voices under `voice_presets/voice_audio/` with matching transcripts in `voice_presets/voice_prompts.json`; both are additionally available as built-in IP voices (**Reported**).[^ming-audio-tiny-card]
- Contents of the wrapper scripts and YAML profiles, the voice preset audio, and the client's request schema beyond the `audio.voice` field were not captured, so flag defaults, port, batching and streaming behavior on this route are unknown (**Observed** coverage limit).[^ming-audio-tiny-card]

## SGLang (text only)

```bash
export MODEL_PATH=inclusionAI/Ming-3.0-audio-tiny
MING_MODEL_VARIANT=tiny CUDA_VISIBLE_DEVICES=0 \
  ./scripts/serve_sglang.sh "$MODEL_PATH"
```

- The card calls the Tiny SGLang profile validated, single-GPU and text-output only; client usage is the linked `examples/sglang_audio_chat.py` (**Reported**).[^ming-audio-tiny-card]
- Because this profile provides no Talker, a voice agent needing spoken replies from this checkpoint must use the vLLM-Omni full-audio profile or SGLang-Omni, not the SGLang route (**Synthesis**).[^ming-audio-tiny-card]

## SGLang-Omni

```bash
sgl-omni serve --model-path inclusionAI/Ming-3.0-audio-tiny --talker.gpu 0
```

- The card states the Tiny checkpoint fits on a single GPU and that `--talker.gpu 0` colocates speech synthesis with the other stages (**Reported**).[^ming-audio-tiny-card]
- The server exposes OpenAI-compatible `/v1/audio/transcriptions`, `/v1/audio/speech` and `/v1/chat/completions`; the linked SGLang-Omni cookbook `cookbook/ming3_audio.html` is said to show client examples that also work with the Tiny model name (**Reported**).[^ming-audio-tiny-card]
- No runtime version floor, request schema, streaming event format, session protocol or concurrency limit is printed for this route, and the cookbook was not fetched (**Observed** coverage limit).[^ming-audio-tiny-card]

## Voice selection and identity

- Two voice sources are described: built-in IP voices addressed by name, and reference-audio prompting for a supplied voice clip; the Transformers speech path takes the same `--voice` argument, for example `--voice US_Stella` (**Reported**).[^ming-audio-tiny-card]
- The complete roster, naming rules and reference-audio invocation rules live in the linked `docs/voices.md`, which was not captured; the card names only `灵小柔` (default), `灵楷` and `US_James` as presets plus `US_Stella` in examples, so the total voice count is unknown (**Observed** coverage limit).[^ming-audio-tiny-card]
- Preset voices are shipped as audio plus transcripts inside the model directory, which makes them cloning references rather than fixed embeddings; the card does not say whether a preset can be overridden per request on every route (**Synthesis**).[^ming-audio-tiny-card]

## Limits for a voice-loop deployment

- No figure is printed for time-to-first-token, time-to-first-audio, RTF, tokens per second, concurrent sessions, peak VRAM or supported quantization, so neither the two-GPU vLLM-Omni profile nor the single-GPU SGLang-Omni colocation can be sized or compared with other runtimes from this card (**Observed** coverage limit).[^ming-audio-tiny-card]
- "Fits on a single GPU" is a card assertion without a GPU model, precision or memory number; it also applies to the checkpoint plus Talker at whatever precision the launcher selects (**Reported/Synthesis**).[^ming-audio-tiny-card]
- Streaming is not characterized: the routes name OpenAI-compatible endpoints, but no SSE or chunk protocol, chunk size or partial-transcript behavior is documented, so realtime suitability is unestablished (**Observed**).[^ming-audio-tiny-card]
- Serving claims are `stale_after: 2027-04-21` per the `pipeline`, `stt` and `tts` domain rules because vLLM-Omni, SGLang and SGLang-Omni release frequently and the wrapper flags are version-sensitive (**Synthesis**).[^ming-audio-tiny-card]

[^ming-audio-tiny-card]: [Ming-3.0-audio-tiny model card](../raw/inclusionAI-Ming-3.0-audio-tiny.md) — locators: header link row (GitHub repository, Examples, voice-guide and deployment-guide links); `Quick Start with Transformers` (repository clone, `requirements-transformers.txt`, `examples/transformers_audio.py`); `Speech Output` (`examples/transformers_thinker_talker.py`, `--voice US_Stella`, `docs/voices.md`); `Serving` → `vLLM-Omni` (both env-var launcher fences, Thinker/Talker GPU split, deployment-YAML note, `examples/vllm_omni_audio_chat.py`, `audio.voice` id, default `灵小柔`, presets `灵楷` and `US_James` under `voice_presets/voice_audio/` with `voice_prompts.json`); `Serving` → `SGLang` (single-GPU validated Tiny profile, `examples/sglang_audio_chat.py`); `Serving` → `SGLang-Omni` (`sgl-omni serve ... --talker.gpu 0`, three endpoints, `cookbook/ming3_audio.html`); `Model Summary` (9.3B/2.7B, languages, license). Scripts, YAML profiles, voice assets, cookbook and voice guide were not captured or inspected; no server was launched.
