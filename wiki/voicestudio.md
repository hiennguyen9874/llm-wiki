---
type: Concept
title: VoiceStudio
description: AGPL-3.0 open-source Electron desktop app and local API/MCP for voice cloning, voice design, dubbing, dictation, transcription, and audiobooks, defaulting to the OmniVoice engine, with README-reported install routes, hardware tiers, and separate model-weight licensing.
tags: [tts, stt, pipeline, voice-cloning, dubbing, dictation, desktop-app, deployment, mcp]
status: draft
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T14:00:00Z }
stale_after: 2027-04-21
sources:
  - id: voicestudio-readme
    resource: ../raw/debpalash-VoiceStudio.md
    kind: documentation
    title: debpalash/VoiceStudio README (undated capture, no revision)
---

VoiceStudio is a GUI-first speech application: a cross-platform Electron app (and web UI) that bundles voice cloning, text-description voice design, timed video dubbing, a floating dictation widget, transcription, and story/audiobook/batch jobs, with a local API and MCP server so agents can call it. Its default engine is [OmniVoice](omnivoice.md) (k2-fsa/OmniVoice), with other engines selectable. It sits at the application layer *above* the models and runtimes in this wiki, not inside a realtime VAD → STT → LLM → TTS loop. Everything below is **Reported** by the project README; nothing was installed or executed (**Unverified**).[^voicestudio-readme]

## What it offers

| Area | README claim | Notes |
| --- | --- | --- |
| Headline | Voice cloning, voice design, video dubbing, dictation, transcription, audiobook creation "in 646 languages" | The 646 figure is a marketing headline; no per-engine language list in this capture. Compare OmniVoice's "600+ languages" in [OmniVoice](omnivoice.md) (**Synthesis**: plausibly the engine's coverage, not stated by the README). |
| Create | Clone a voice or design your own; dictate with a floating widget | |
| Produce | Dub videos with timed speech; stories, audiobooks, batch jobs | Long-form reliability is disputed by community reports; see below. |
| Connect | Local API and MCP for agents; reusable recipes and watch folders | API and MCP details live in `docs/speech-platform.md` and `docs/mcp.md`, which were not captured. |
| Engines | "Start with VoiceStudio (default, powered by k2-fsa/OmniVoice), or choose another engine" | Engine catalog is in `docs/feature-catalog.md`, uncaptured; no engine count is given. |
| Privacy | Local workflows run on your hardware; remote services optional; usage analytics requires consent | |

All rows: [^voicestudio-readme] (sections "Your voice. Your workflow." and header tagline).

## Install and hardware

- **Packaging:** Electron is the only desktop app and web UI. Version 0.5.3 was the final Tauri release; Tauri users must install Electron separately and the Tauri shell and legacy UI entry points were removed (**Reported**).[^voicestudio-readme]
- **Install routes:** a one-command `curl … | sh` installer (macOS/Linux; `irm … | iex` on Windows) with `--version X.Y.Z`, `--main` (build from source), and `--uninstall` options; release downloads (`.dmg`, `.exe`, `.AppImage`, `.deb`); Docker and per-OS guides; and source run with `bun install`, `bun run setup:api`, `bun run dev`. The installer needs curl and a SHA-256 tool for releases; `--main` needs Git, Node.js 22+, Bun, Rust/Cargo, and platform build tools. It preserves settings, projects, and models (**Reported**). The pipe-to-shell pattern was not inspected or run; review `scripts/install.sh` before use (**Synthesis**).[^voicestudio-readme]
- **Hardware tiers (README table):**

| Hardware | Support |
| --- | --- |
| NVIDIA GPU (Windows/Linux) | CUDA acceleration |
| Apple Silicon | Metal (MPS) acceleration |
| No dedicated GPU | Fully usable on CPU but slower; small CPU build of PyTorch, about 5 GB free disk |
| Windows on ARM | Experimental, validation pending; native ARM64 app, x64 Python backend under emulation, CPU only |
| Intel Mac | App UI only; connect to a remote backend |

  Per-engine hardware needs are deferred to `docs/performance.md` (uncaptured). No latency, RTF, or VRAM figure appears in the capture.[^voicestudio-readme]
- **Agent install:** the README offers a prompt for coding agents that follows `docs/install/agent.md` (hardware detection, reuse of existing data, asking before model downloads, a test generation), plus `npx skills add debpalash/VoiceStudio` with `voicestudio` and `voicestudio-maintainer` skills (**Reported**).[^voicestudio-readme]

## Licensing and responsible use

- The application is AGPL-3.0, including commercial use under its conditions. Model weights, tokenizers, voices, and generated-output conditions are separate; "a paid app licence does not grant those rights" (**Reported**).[^voicestudio-readme]
- The README says clone voices only with permission, and that Model Manager shows versioned model-source notices, evidence links, and unresolved review gaps from a shared inventory (`docs/licensing/model-inventory.md`). An optional reviewed-file preview does not enforce ordinary downloads or certify commercial permission (**Reported**). For a deployment, check each engine's own license; for OmniVoice lineage see [OmniVoice](omnivoice.md) and [KhanhTTS-OmniVoice](khanhtts-omnivoice.md).[^voicestudio-readme]

## Contradictions

- **Paid or closed-source version.** The [Reddit comparison thread](audio-cpp-frontends-community-comparison.md) says VoiceStudio has a disliked closed-source paid version. The README declares the app AGPL-3.0 and, separately, refers to "a paid app licence" and a paid sponsor placement program, so a paid licence exists but the README does not say whether its code is closed. Neither claim is chosen; neither was verified against the repository's LICENSE or `LICENSE-NOTICE.md` (not captured).[^voicestudio-readme]
- **Model count.** The thread's original post says VoiceStudio supports 27 models. The README gives no count, so the figure is neither confirmed nor contradicted.[^voicestudio-readme]

## Relationships

- Uses: [OmniVoice](omnivoice.md) as the default engine.
- Related: [audio.cpp Framework](audio-cpp-framework.md) — the thread reports some VoiceStudio models are based on audio.cpp; the README does not mention audio.cpp (**Reported** by thread only).
- Compared in: [audio.cpp and Local Speech Frontends Community Comparison](audio-cpp-frontends-community-comparison.md) for community opinion on model coverage, pricing, and long-job reliability.
- Related: [Speech Deployment Tools Comparison](speech-deployment-tools-comparison.md) for the runtime/server layer a pipeline would use instead of a GUI app.

## Coverage, limits, and freshness

- The README capture (118 lines, single file) was read statically in full (**Observed**). It has no date, revision, or release version beyond the "0.5.3 final Tauri" note, so the claims are a dated snapshot (`stale_after` 2027-04-21). The page stays `draft` because the engine catalog, API/MCP, performance, and licensing documents are uninspected.
- Referenced but not captured: `docs/feature-catalog.md`, `docs/engines/`, `docs/benchmarks.md`, `docs/performance.md`, `docs/speech-platform.md`, `docs/mcp.md`, `docs/mobile.md` (iOS/Android phone companion, preview), install guides, `scripts/install.sh`, licensing docs, `CHANGELOG.md`, `LICENSE`, and localized READMEs (`README_CN.md`, `README_JA.md`).
- Excluded as decorative or non-durable: logo, badges (CI, release, Trendshift, view counters), screenshots and GIF (not inspected as images; local files absent from the capture), Discord and website links, sponsorship, donation, and partner contact details.
- No installation, execution, listening, or benchmark was run; no sensitive values compiled.

[^voicestudio-readme]: [VoiceStudio README](../raw/debpalash-VoiceStudio.md) — locators: header tagline ("646 languages"); "Your voice. Your workflow." table and engine sentence; "Get started" install script, hardware table, agent-install prompt, and Electron-from-source block; Electron/Tauri note blockquote; "Documentation" table; "License & responsible use" section.
