# Knowledge Base Scope

Instance configuration under the base contract [`AGENTS.md`](AGENTS.md). Initialize or re-scope it with the `wiki-init` skill.

## Identity

- **Name:** Voice pipeline knowledge base (VAD → STT → LLM → TTS)
- **Purpose:** Durable, comparable knowledge for building and deploying realtime voice agents across the VAD → STT → LLM → TTS pipeline: model selection, streaming/latency tradeoffs, benchmarks, and edge/server deployment.
- **Inclusion test:** a source or question is in scope when it yields durable knowledge about VAD/endpointing, STT/ASR, dialogue LLM in the voice loop, TTS/synthesis, or end-to-end pipeline integration (orchestration, streaming latency, evaluation, GGUF/edge packaging of those components).
- **Exclusions:** material the human marks as off-limits; plus music-only generation and non-speech modalities unless they directly feed the VAD → STT → LLM → TTS loop.

## Domains

Domains emerge from ingested knowledge. Register a domain when it recurs across several concepts, needs its own rules, or selects domain tooling.

| Domain | Focus | Course profile | Rules |
| --- | --- | --- | --- |
| `vad` | Voice activity detection, endpointing/EOU, and diarization for turn-taking | `general` | Use `stale_after` for model/API releases and benchmark numbers. |
| `stt` | Speech-to-text / ASR, streaming and batch, hotwords, ITN | `general` | Use `stale_after` for model/API releases and benchmark numbers. |
| `llm` | Dialogue and reasoning LLM inside the voice loop | `ml` | Use `stale_after` for model/API releases and benchmark numbers. |
| `tts` | Text-to-speech, voice cloning/design, vocoders, streaming synthesis | `general` | Use `stale_after` for model/API releases and benchmark numbers. |
| `pipeline` | End-to-end voice-loop integration: orchestration frameworks, turn-taking, barge-in/echo handling, noise preprocessing, latency and VRAM budgets | `general` | Use `stale_after` for framework/model releases, latency budgets, and benchmark numbers. |

- Name domains as the human does; they may be broad (`health`) or narrow (`home-network`).
- A concept belongs to its primary domain through tags and, once groups exist, its group path.
- Domain rules cover things like citation style, verification expectations, or staleness windows.
- An unregistered domain uses the defaults below.

## Conventions

| Setting | Value |
| --- | --- |
| Default interaction mode | `autonomous` |
| Concept prose language | Match the human's request; keep technical terms in their original language. |
| Course prose language | Vietnamese, with technical keywords in English and an English gloss on first use. |
| Default course profile | `general` |

Course profiles live in `.pi/skills/wiki-learn/references/profiles/`. A domain without a matching profile uses `general`.

## Governance

- Registering a new domain or course-profile mapping needs no approval; record it here in the same change as the first affected concept.
- Narrowing scope, adding exclusions, or adding domain rules that change meaning, governance, or human control requires human approval, as defined in the base contract's contract evolution section.
