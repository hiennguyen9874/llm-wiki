# huggingface/speech-to-speech supporting docs — captured 2026-10-07

Supporting upstream documentation captured for the Vietnamese voice-pipeline PoC review (`outputs/review-missing-document.md`). Upstream: https://github.com/huggingface/speech-to-speech at revision `f9c23282a564cbe5b1f015ccb36d58e941de8520`. Capture date: 2026-10-07 UTC. Files keep their upstream relative paths and are immutable snapshots; `checksums.json` records SHA-256 and byte length. No code was executed and no models were downloaded.

## Coverage ledger

| Artifact | Status |
|---|---|
| `docs/openai-compatible-stt.md` | Pending ingest. OpenAI-compatible STT backends, including stateful streaming / Realtime transcription. |
| `docs/openai-compatible-tts.md` | Pending ingest. OpenAI-compatible TTS backend (`/v1/audio/speech`, formats). |
| `docs/response-latency.md` | Pending ingest. Latency breakdown and tuning. |
| `src/speech_to_speech/{STT,TTS,VAD,LLM}/README.md` | Pending ingest. Per-stage handler references. |
| `src/speech_to_speech/api/openai_realtime/README.md` | Pending ingest. Realtime WebSocket/WebRTC protocol, turn handling. |
| `demo/README.md` | Pending ingest. Browser demo, HTTPS/mic requirements. |
| `src/speech_to_speech/arguments_classes/*.py` (11 files) | Pending ingest. CLI flag definitions for VAD/Smart Turn, Qwen3-ASR, OpenAI STT/Realtime STT/TTS, OmniVoice, Qwen3-TTS, chat-completions LLM, realtime server. Other argument classes excluded as irrelevant to the PoC. |
| Root `README.md` | Excluded: byte-identical to existing `../speech-to-speech.md` (canonical entry point). |
| `demo/CONTEXT.md`, `demo/DESIGN.md`, `demo/docs/adr/`, `docs/releases/`, `examples/`, `archive/`, `AGENTS.md`, tests, implementation | Excluded: not needed for PoC wiring questions. |
| `checksums.json` | Local capture manifest; hashes do not verify claims. |
