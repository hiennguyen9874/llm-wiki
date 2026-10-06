---
type: Concept
title: vLLM-Omni
description: GPU serving framework for omni-modality autoregressive and diffusion models with disaggregated stage execution, OpenAI-compatible APIs, and full-duplex realtime speech serving.
tags: [pipeline, serving, tts, stt, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T20:00:00Z }
stale_after: 2027-10-06
sources:
  - id: vllm-omni-readme
    resource: ../raw/vllm-omni.md
    kind: documentation
    title: vLLM-Omni GitHub README (v0.30.0-era, 2026/09 news)
---

vLLM-Omni is the vLLM community's omni-modality serving framework that extends vLLM's text autoregressive generation into any-to-any text, image, audio, video, and action inference, combining vLLM-derived KV-cache management with pipelined and fully disaggregated stage execution plus an OpenAI-compatible server and full-duplex realtime audio input/output for voice-loop deployment (**Reported**).[^vllm-omni-readme]

## Runtime identity and design target

- Upstream is `vllm-project/vllm-omni`, first community-released in 2025/11 to support omni-modality model serving; vLLM itself was originally designed for text-based autoregressive generation (**Reported**).[^vllm-omni-readme]
- Design target covers three extensions: omni-modality (text, image, audio, video, action data processing), non-autoregressive architectures (Diffusion Transformers and other parallel generation models beyond vLLM's AR support), and heterogeneous outputs (text generation through multimodal and action outputs) (**Reported**).[^vllm-omni-readme]
- Positioning is easy, fast, and cheap omni-modality model serving for everyone; speed claims are source assertions with no latency or throughput figures in the captured README (**Reported**).[^vllm-omni-readme]

## Release line and news

- Starting with 0.14.0, vLLM-Omni publishes a stable release aligned with every even-numbered upstream vLLM minor version; 0.16.0, 0.18.0, 0.20.0, and 0.22.0 continued this cadence (**Reported**).[^vllm-omni-readme]
- 0.30.0 (2026/09) is rebased onto vLLM 0.30.0 and features a unified full-duplex serving framework around engine-owned sessions for MiniCPM-o 4.5 and AURA, native cross-stage KV and multimodal payload transfer (Mooncake AR-to-DiT handoff and NIXL connectors), interactive world-model serving with LingBot World, and realtime MiniMax H3 Turbo inference on NVIDIA Blackwell and Ascend 950 (**Reported**).[^vllm-omni-readme]
- 0.28.0 (2026/08) features production-ready MiniMax H3 serving on GPU and NPU, a unified AR/DiT paged KV cache runtime, and enhanced realtime full-duplex serving for the MiniCPM-o series (**Reported**).[^vllm-omni-readme]
- 0.26.0 (2026/08), aligned with the vLLM 0.26 release line, features MiniMax H3 joint video/audio generation, an experimental full-duplex realtime runtime for MiniCPM-o 4.5, distributed layerwise diffusion offload, and broader model, hardware, streaming, TTS, and quantization support (**Reported**).[^vllm-omni-readme]
- 0.24.0 (2026/07), aligned with the vLLM 0.24 release line, expands production-ready TTS, speech, diffusion, image/video generation, and robot-policy coverage with Omni stage runtime refactoring, diffusion request-level batching, async output materialization, quantization/cache/memory improvements, and broad CUDA/ROCm/XPU/NPU support (**Reported**).[^vllm-omni-readme]
- The 0.14.0–0.22.0 line (2026/06) adds omni and world-model support with Cosmos3 and DreamZero, models such as MiniCPM-o 4.5, MOSS-TTS, and Lance, and advances TTS, diffusion, distributed execution, quantization, and RL integration through VeRL-Omni with CUDA/ROCm/MUSA/NPU/XPU coverage (**Reported**).[^vllm-omni-readme]
- VeRL-Omni `v0.2.0` (2026/08) is reported as faster diffusion RL powered by vLLM-Omni (request-level/step-wise batching with FA3) with rebuilt Qwen3-Omni multimodal training (DPO and GSPO) plus LTX-2.3 and Qwen-Image-Edit support; first public project deepdive was 2026/03 at the vLLM Hong Kong Meetup (**Reported**).[^vllm-omni-readme]

## Served model coverage

- Voice-loop-relevant served families named in the source: TTS models Qwen3-TTS, Tencent AuK, Breeze-TTS-2, and CosyVoice3; omni-modality models Qwen3-Omni and MiniCPM-o 4.5; speech and diffusion-audio generation via MiniMax H3 (**Reported**).[^vllm-omni-readme]
- Full catalog context retained from the source but out of voice-loop scope per `SCOPE.md` unless feeding VAD → STT → LLM → TTS: omni-modality Cosmos3, HunyuanImage, and BAGEL; diffusion image/video MAGI-2, LTX-2.5, Wan2.2, and LingBot World; robot-policy and action π0.5, GR00T-N1.7, DreamZero-DROID, and InternVLA-A1 (**Synthesis**).[^vllm-omni-readme]
- Deployment recipes are published per model through an external recipe site; recipe contents were not present in `raw/` and were not inspected (**Reported**, with unfetched-pointer limit).[^vllm-omni-readme]

## Architecture: speed and flexibility

- Speed mechanisms claimed: state-of-the-art AR support by leveraging efficient KV cache management from vLLM; pipelined stage execution overlapping for high throughput; fully disaggregated execution based on OmniConnector with dynamic resource allocation across stages (**Reported**).[^vllm-omni-readme]
- Voice-loop-relevant runtime advances: unified AR/DiT paged KV cache runtime (0.28.0); native cross-stage KV and multimodal payload transfer via Mooncake AR-to-DiT handoff and NIXL connectors plus engine-owned sessions for full-duplex serving (0.30.0); diffusion request-level batching with async output materialization and distributed layerwise diffusion offload (0.24.0/0.26.0) (**Reported**).[^vllm-omni-readme]
- Flexibility surface: heterogeneous pipeline abstraction for complex model workflows; seamless Hugging Face model integration; tensor, pipeline, data, and expert parallelism for distributed inference; streaming outputs; OpenAI-compatible API server; full-duplex realtime serving with streaming audio input and output via a dedicated realtime duplex API document that was linked but not present in `raw/` (**Reported**, with unfetched-pointer limit).[^vllm-omni-readme]

## Hardware, install, and usage pointers

- Hardware backends named across releases: CUDA, ROCm, XPU, and NPU (0.24.0); plus MUSA in the 0.14.0–0.22.0 line; GPU and NPU for production MiniMax H3 (0.28.0); NVIDIA Blackwell and Ascend 950 for realtime MiniMax H3 Turbo (0.30.0) (**Reported**).[^vllm-omni-readme]
- Entry pointers are the hosted documentation (installation, quickstart), nightly CUDA Docker images built from `main`, the supported-models list, and per-model deployment recipes; install commands, Docker tags, and guide contents were not present in `raw/` and were not inspected (**Reported**, with unfetched-pointer limit).[^vllm-omni-readme]
- Voice-loop serving evidence elsewhere in this wiki: [Higgs TTS 3](higgs-tts-3-4b.md) documents a `vllm-omni serve ... --omni` path exposing OpenAI-compatible `/v1/audio/speech` with zero-shot cloning, and [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) routes non-Vietnamese TTS through vLLM-Omni streaming (`POST /v1/audio/speech` PCM streaming and a WebSocket session protocol); those behaviors are reported by those concepts' sources, not verified against this README snapshot (**Synthesis**).[^vllm-omni-readme]

## Community, license, and citation

- Contribution is invited through a linked contributing guide; community channels are the `#sig-omni` Slack channel and the vLLM user forum; the captured README also links documentation, DeepWiki, WeChat, and a slide deck that were not inspected (**Reported**).[^vllm-omni-readme]
- License is Apache License 2.0 per the `License` section pointing at the upstream `LICENSE` file, which was not present in `raw/` (**Reported**).[^vllm-omni-readme]
- Research citation is `Yin et al., vLLM-Omni: Fully Disaggregated Serving for Any-to-Any Multimodal Models, arXiv:2602.02204, 2026`; the paper body was not present in `raw/` and its claims are not compiled here (**Reported**, with unfetched-paper limit).[^vllm-omni-readme]

## Relationships

- Serves: [AuK](auk.md) and [AuK-Flash](auk-flash.md) are named TTS families in this runtime's speech-generation coverage; consult those pages for 16-task instruction-driven generation/editing scope and weights (**Synthesis**).[^vllm-omni-readme]
- Serves: [Breeze TTS 2](breeze-tts-2.md), [CosyVoice2-0.5B](cosyvoice2-0.5b.md), and [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md) cover the bilingual/multilingual TTS families overlapping this runtime's Qwen3-TTS, Breeze-TTS-2, and CosyVoice3 entries; no shared codebase is asserted (**Synthesis**).[^vllm-omni-readme]
- Serves: [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md), [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md), and [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md) cover the Qwen3-TTS checkpoints and tokenizer this runtime fronts; for streaming behavior compare [Faster Qwen3-TTS](faster-qwen3-tts.md) as a CUDA-graph/GGML streaming wrapper alternative (**Synthesis**).[^vllm-omni-readme]
- Serves: [Higgs TTS 3](higgs-tts-3-4b.md) documents a `vllm-omni serve` zero-shot-cloning path behind the same OpenAI-compatible `/v1/audio/speech` API; consult that page for weights, tag controls, and H100 throughput (**Synthesis**).[^vllm-omni-readme]
- Contrasts with [SGLang-Omni](sglang-omni.md): SGLang-Omni is a multi-stage GPU runtime with stage-matched scheduling and control-plane plus relay-data-plane tensor transport composing with SGLang for AR execution, while vLLM-Omni is the vLLM-line counterpart with vLLM-derived KV-cache management, OmniConnector disaggregation, AR/DiT paged KV, and engine-owned full-duplex sessions; compare them when choosing a server-GPU omni/TTS serving stack (**Synthesis**).[^vllm-omni-readme]
- Contrasts with [audio.cpp Framework](audio-cpp-framework.md): audio.cpp is a native ggml-based C++ runtime for local CPU/edge GGUF deployment, while vLLM-Omni is a server-GPU disaggregated serving framework with distributed parallelism and OpenAI-compatible streaming; compare them on edge-local versus server-GPU placement (**Synthesis**).[^vllm-omni-readme]

## Coverage and limits

- Source inspected statically only; no repository cloned, no server launched, no model served, and no latency, throughput, streaming, quality, cost, or hardware-compatibility claim reproduced — all capability, release, and compatibility claims are source assertions (**Synthesis**).[^vllm-omni-readme]
- Architecture diagram, logos, realtime duplex API document, per-model recipes, documentation pages, Docker images, supported-models list, contributing guide, arXiv paper, slides, DeepWiki, forum, Slack, WeChat image, star-history chart, and `LICENSE` file were linked but not fetched and were not present in `raw/`; stage internals, scheduler behavior, connector semantics, session protocol, and checkpoint contents were not inspected (**Synthesis**).[^vllm-omni-readme]
- Image, video, action, robot-policy, world-model, and music-adjacent diffusion entries are retained only as catalog context per the `SCOPE.md` exclusion of non-speech modalities unless feeding the voice loop (**Synthesis**).[^vllm-omni-readme]
- Release, hardware-support, model-coverage, and API-surface claims carry `stale_after: 2027-10-06` per the `pipeline`, `tts`, `stt`, and `llm` domain rules (**Synthesis**).[^vllm-omni-readme]

[^vllm-omni-readme]: [vLLM-Omni GitHub README](../raw/vllm-omni.md) — locators: header badges and link row (Documentation, DeepWiki, User Forum, Developer Slack, WeChat, Paper arXiv:2602.02204, Slides); `Latest News` (2026/09 v0.30.0 rebase onto vLLM 0.30.0 with MiniCPM-o 4.5/AURA engine-owned sessions, Mooncake AR-to-DiT plus NIXL transfer, LingBot World, MiniMax H3 Turbo on Blackwell/Ascend 950; 2026/08 v0.28.0 GPU/NPU MiniMax H3 plus AR/DiT paged KV plus MiniCPM-o full-duplex; 2026/08 VeRL-Omni v0.2.0 FA3 batching plus Qwen3-Omni DPO/GSPO plus LTX-2.3/Qwen-Image-Edit; 2026/08 v0.26.0 vLLM 0.26 line with joint video/audio, experimental duplex, layerwise offload, TTS/quant support; 2026/07 v0.24.0 vLLM 0.24 line with stage refactor, request-level batching, async materialization, CUDA/ROCm/XPU/NPU; 2026/06 0.14.0–0.22.0 even-minor cadence with Cosmos3/DreamZero, MiniCPM-o 4.5/MOSS-TTS/Lance, VeRL-Omni, CUDA/ROCm/MUSA/NPU/XPU; 2026/03 Hong Kong deepdive; 2025/11 vllm-project release); `About` (vLLM text-AR origin; omni-modality/non-AR/heterogeneous-output bullets; architecture figure; speed bullets KV-cache/pipelined-overlap/OmniConnector-disaggregation; flexibility bullets pipeline-abstraction/HF/parallelisms/streaming/OpenAI-API/`docs/serving/realtime_duplex_api.md` duplex); `seamlessly supports` model lists (Qwen3-Omni/MiniCPM-o 4.5/Cosmos3/HunyuanImage/BAGEL; Qwen3-TTS/AuK/Breeze-TTS-2/CosyVoice3; MiniMax H3/LingBot World/MAGI-2/LTX-2.5/Wan2.2; π0.5/GR00T-N1.7/DreamZero-DROID/InternVLA-A1); `Getting Started` (docs, Installation, Quickstart, nightly CUDA Docker, Supported Models, Deployment Recipes at recipes.vllm.ai); `Contributing`, `Citation` (Yin et al. 2026 bibtex), `Join the Community` (#sig-omni/forum), `Star History`, `License` (Apache-2.0).
