---
type: Concept
title: Kokoro-FastAPI
description: Dockerized FastAPI server wrapping Kokoro-82M with an OpenAI-compatible speech endpoint, CPU, CUDA, and ROCm images plus a native Apple MPS path, opt-in debug routes, and Apache-2.0 wrapper code.
tags: [tts, kokoro, fastapi, openai-compatible, docker, server]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-21T15:00:00Z }
stale_after: 2027-10-13
sources:
  - id: kokoro-fastapi-readme
    resource: ../raw/Kokoro-FastAPI.md
    kind: documentation
    title: Kokoro-FastAPI README capture
  - id: kokoro-fastapi-readme-remsky
    resource: ../raw/remsky-Kokoro-FastAPI.md
    kind: documentation
    title: Kokoro-FastAPI README capture (remsky-prefixed variant)
---

Kokoro-FastAPI is a Dockerized FastAPI wrapper around the Kokoro-82M text-to-speech model, published as `remsky/Kokoro-FastAPI`. It exposes an OpenAI-compatible `/v1/audio/speech` route for Kokoro, plus `/dev/*` and `/debug/*` helper routes that the README says may change between minor releases. The README presents it as a self-hosted server for long-form generation, multi-speaker output, and caption timestamps. It says the author made the wrapper "for ease of use and personal projects" and has no affiliation with the model's authors (**Reported**).[^kokoro-fastapi-readme]

## Identity and pins

- The banner reads "FastKoko: Dockerized Kokoro-82M TTS, OpenAI-compatible API"; the upstream model links to `hexgrad/Kokoro-82M` (lines 1, 16; **Reported**).[^kokoro-fastapi-readme] Upstream model: [Kokoro-82M](kokoro-82m.md).
- Test pins, from badges: `kokoro` 0.9.4, `misaki` 0.9.4, and "Tested at Model Commit" `1.0::41e5892`, which links to git commit `41e5892b9d8b43e56fc560f892312a328a410973` (lines 9–11; **Reported**).[^kokoro-fastapi-readme] These are the author's test pins, not a wrapper release.
- This git commit is a different identifier from the v1.0 file SHA256 prefix `496dba11` recorded in [Kokoro-82M](kokoro-82m.md). They do not conflict (**Synthesis**).
- No wrapper release number, tag, or revision is named in the capture. The README advises pinning a release tag rather than `:latest` (line 52; **Reported**).[^kokoro-fastapi-readme]

## Deployment paths

| Path | Entry point | Hardware and status (README) |
| --- | --- | --- |
| Docker CPU | `ghcr.io/remsky/kokoro-fastapi-cpu:latest` | CPU; linux/amd64 and linux/arm64; models baked in (lines 50, 26) |
| Docker NVIDIA | `ghcr.io/remsky/kokoro-fastapi-gpu:latest`; `-cu128` for RTX 50-series | CUDA; cu126 for GTX 900 through RTX 40; amd64 and arm64 (lines 58–69) |
| Docker AMD | `ghcr.io/remsky/kokoro-fastapi-rocm:latest` with `/dev/kfd` and `/dev/dri` | ROCm, experimental, linux/amd64 only (lines 27, 74) |
| Apple Silicon | `./start-gpu_mac.sh` | Native MPS through UV, no image; the Docker GPU image is CUDA-only (lines 28, 79, 104–105) |
| Direct run | `./start-cpu.sh` or `./start-gpu.sh` (`.ps1` on Windows) | Hot-reload dev run via astral uv; install [eSpeak NG](espeak-ng.md) (`espeak-ng`) as a fallback for unknown words (lines 117–128) |

- Compose: `docker/gpu`, `docker/cpu`, or `docker/rocm`, then `docker compose up --build`. Models auto-download; a manual download script exists (lines 90–111; **Reported**).[^kokoro-fastapi-readme]
- The `:latest` CUDA version conflicts across two README sections; see Contradictions.

## API surface

- `POST /v1/audio/speech` takes `model`, `input`, `voice`, `response_format` (mp3, wav, opus, flac, aac, pcm), `speed`, and, in streaming examples, `stream` (lines 184–230, 303–316, 673–700; **Reported**).[^kokoro-fastapi-readme] Clients use `base_url="http://localhost:8880/v1"`.
- `GET /v1/audio/voices` lists voice IDs. OpenAI-style voice names map through `api/src/core/openai_mappings.json` (line 192; file not captured).
- Human-facing pages: API docs at `/docs` and a WebUI at `/web` (lines 168–170).
- Stability tiers: `/v1/*` is the stable OpenAI-compatible surface. `/dev/*` and `/debug/*` are "operational helpers" that "may change or move behind flags between minor releases" (line 796; **Reported**).[^kokoro-fastapi-readme]
- Extension fields such as `allow_voice_tags`, `voice_aliases`, `ssml`, and `normalization_options` sit outside the OpenAI request schema. The README passes `allow_voice_tags` through `extra_body` for the official client (lines 451–458; **Reported**).[^kokoro-fastapi-readme] See [Kokoro-FastAPI Voice and Markup Controls](kokoro-fastapi-voice-and-markup.md).
- Debug routes (`/debug/threads`, `/debug/storage`, `/debug/system`) are off unless `ENABLE_DEBUG_ENDPOINTS=true`, because they expose host and process internals (lines 785–790). Model unload and reload routes need `ALLOW_DEV_UNLOAD=true` (lines 792–794).

## Configuration

Settings are environment variables or lines in a root `.env` file. The full reference is `docs/configuration.md`, which was not captured (lines 778–781; **Reported**).[^kokoro-fastapi-readme] Flags named in the README:

- `ENABLE_DEBUG_ENDPOINTS` (off), `ALLOW_DEV_UNLOAD` (off), `ENABLE_INNO_TUNER` (off), `ALLOW_LOCAL_VOICE_SAVING` (off).
- `ENABLE_VOICE_TAGS` (on). Setting it to `false` refuses the `allow_voice_tags` parameter and makes `/dev/dialogue` return 403 (line 437).
- `MODEL_AUTO_UNLOAD_TIMEOUT_SECONDS` (default `0`, disabled).
- `API_LOG_LEVEL` (loguru level, default `DEBUG`; the README's logging section).
- `TARGET_MIN_TOKENS`, `TARGET_MAX_TOKENS`, `ABSOLUTE_MAX_TOKENS` (defaults 175, 250, 450) and `SSML_MAX_DEPTH` (default 10) (lines 556, 539).

## Known issues

- Text normalization can drop or change phrases. The README's workaround is `"normalization_options": {"normalize": false}` in the request JSON (lines 808–835; **Reported**).[^kokoro-fastapi-readme]
- WAV responses use the streaming sentinel `0xFFFFFFFF` in size fields. Python's stdlib `wave` then reports a wrong duration; use `soundfile`, `pydub`/ffmpeg, or `ffprobe` (lines 851–855; **Reported**).[^kokoro-fastapi-readme]
- Linux GPU device permissions and AMD ROCm tuning (HSA overrides, MIOpen warmup, hipBLAS fallback) live in `docs/troubleshooting.md`, which was not captured (lines 837–849).

## Licensing and provenance

- Wrapper code: Apache 2.0. Kokoro weights: Apache 2.0, per the model page. Inference code adapted from StyleTTS2: MIT (lines 893–898; **Reported**).[^kokoro-fastapi-readme]
- The README links the Apache text at apache.org; the repository `LICENSE` file was not captured (**Observed** limit).
- The README requires permission before tuning a voice (line 416; see [Kokoro-FastAPI Voice and Markup Controls](kokoro-fastapi-voice-and-markup.md)).

## Ecosystem and integrations

- The README's "Integration & Guides" block links four in-repo guides: Helm chart (`docs/deployment/kubernetes.md`), DigitalOcean (`docs/deployment/digitalocean.md`), SillyTavern and OpenWebUI (`docs/integrations/`). None of those guides was captured (lines 31–35 in both captures; **Reported**).[^kokoro-fastapi-readme][^kokoro-fastapi-readme-remsky]
- It also lists community projects that "use, recommend, or enable" the server as a backend, grouped as: Home Assistant (`wyoming_openai`, `openai_tts`, `Kokoro-TTS`); app stores and templates (Umbrel, Unraid Apps, GPUStack, jetson-containers); readers and audiobooks (openreader, epub_to_audiobook, audiobook-creator, Zotero-OpenReader); assistants and agents (xiaozhi-esp32-server, call-me, agent-cli, voice-chat-ai); and browser tools (kokoro-extension, customtts) (earlier capture lines 37–43; remsky capture lines 37–51; **Reported**).[^kokoro-fastapi-readme][^kokoro-fastapi-readme-remsky] For a voice loop, the agent entries show the server used as the TTS stage behind its OpenAI-compatible route (**Synthesis**). No linked project was inspected, and the README does not say which integrations the author tested.
- The earlier capture heads the list "use, recommend, or enable"; the remsky capture says "enable" only. The earlier capture gives a Docker "Downloads 2.6M+" badge; the remsky capture gives "pulls per month 250K+". The two measure different things and neither is dated or verifiable here, so no adoption figure is relied on (**Observed** difference; **Unverified**).[^kokoro-fastapi-readme][^kokoro-fastapi-readme-remsky]

## Contradictions

- **CUDA version of `:latest`:** the Quickest Start note says `gpu:latest` "is the same image as `gpu:latest-cu126`" (line 84). The NVIDIA arm64 row says the same `:latest` tag "ships cu129" on Jetson and GH200 (line 69). The README may mean one tag with per-architecture images, but the capture does not say. Neither reading is chosen here; check the registry manifest before relying on a CUDA version (**Observed** discrepancy).

## Relationships

- Serves the [Kokoro-82M](kokoro-82m.md) weights. The README's language list (English US/GB, Spanish, French, Hindi, Italian, Japanese, Brazilian Portuguese, Mandarin Chinese; line 19) gives eight languages if English (US/GB) counts once. That matches the card's v1.0 release row. It does not resolve the card's `language: en` metadata (**Synthesis**).
- Peer Kokoro server: [Speaches](speaches.md) also serves `hexgrad/Kokoro-82M` behind an OpenAI-compatible API, alongside Piper and faster-whisper STT. This README describes only Kokoro-82M, with no STT or Piper path (**Observed** absence; **Synthesis**).
- Vietnamese: the language list has no Vietnamese entry. For Vietnamese Kokoro artifacts see [Kokoro Vietnamese](kokoro-vietnamese.md); the capture does not link the two (**Synthesis**).
- Selection framework: [Speech deployment tools comparison](speech-deployment-tools-comparison.md) treats OpenAI-compatible APIs as usually partial subsets and advises schema tests (**Synthesis**).
- Detail pages: [Kokoro-FastAPI Voice and Markup Controls](kokoro-fastapi-voice-and-markup.md) (voices, tags, SSML, dialogue, captions) and [Kokoro-FastAPI Performance and Evaluation](kokoro-fastapi-performance.md) (latency, throughput, VRAM, WER).

## Coverage and limits

- Inspected statically: the whole README capture, `raw/Kokoro-FastAPI.md` (917 lines) (**Observed**).[^kokoro-fastapi-readme]
- Second capture: `raw/remsky-Kokoro-FastAPI.md` (925 lines, undated, file written later than the first) was reconciled by `diff` against the first. Only five head-of-file spots differ: the Docker downloads/pulls badge, "Custom voicepack generation" versus "Custom voicepacks" (line 20), the DeepWiki badge image, and the community-projects list, which is flat in the first capture and a collapsed `<details>` list in the second. Everything from `## Get Started` onward is identical in content, so no other claim here changed. The capture order is not established by the documents themselves (**Observed**).[^kokoro-fastapi-readme-remsky]
- Not executed: no image pulled, no container started, no server run, no synthesis or API call, no benchmark rerun.
- Linked but not captured: `docs/configuration.md`, `docs/troubleshooting.md`, `docs/inno-tune.md`, `docs/deployment/*`, `docs/integrations/*`, `docker/scripts/download_model.py`, the `start-*` launchers, the compose files, `api/src/core/openai_mappings.json`, `examples/`, `CHANGELOG.md`, the GitHub repository, and `assets/` images. The missing configuration and troubleshooting docs are the main limit on the operations section.
- Excluded as decorative or non-substantive: badges other than the test pins (Trendshift, Codecov, CI, downloads/pulls, DeepWiki/CodeWiki), donation and Spaces links, the contributor graph, and the repoglyph image.
- Sensitive-value screen: the README uses only the placeholder `api_key="not-needed"` (lines 156, 189, 238, 381). No credentials, tokens, or private data appear (**Observed**).
- No wrapper revision is recorded, so every fact here is time-bound (`stale_after` 2027-10-13).

[^kokoro-fastapi-readme]: [Kokoro-FastAPI README capture](../raw/Kokoro-FastAPI.md) — locators: line 1 banner; lines 7–11 badges (`kokoro` 0.9.4, `misaki` 0.9.4, tested model commit `41e5892`); lines 16–28 intro features and platform matrix; line 19 language list; lines 48–88 docker run; line 52 `:latest` pin advice; line 69 NVIDIA arm64 row; line 84 `gpu:latest` note; lines 90–115 compose; lines 117–145 direct run; lines 147–177 Up and Running (`/docs`, `/web`); lines 184–230 OpenAI-compatible endpoint; lines 303–316 output formats; line 437 `ENABLE_VOICE_TAGS` opt-out; lines 451–458 `extra_body` example; lines 539 `SSML_MAX_DEPTH`; line 556 chunk token defaults; lines 778–783 configuration; lines 785–797 debug endpoints and stability; lines 808–835 normalization issue; lines 851–855 WAV sentinel; lines 886–899 model and license.

[^kokoro-fastapi-readme-remsky]: [Kokoro-FastAPI README capture (remsky-prefixed variant)](../raw/remsky-Kokoro-FastAPI.md) — locators: line 13 Docker pulls-per-month badge; line 20 voicepack wording; lines 31–35 Integration & Guides; lines 37–51 collapsed community-projects list; line 53 `## Get Started`; content from there is identical to the earlier capture.
