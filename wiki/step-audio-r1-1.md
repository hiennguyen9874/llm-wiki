---
type: Concept
title: Step-Audio-R1.1
description: Realtime spoken-dialogue model upgrade with dual-brain Mind-Paced Speaking and acoustic-grounded reasoning, served via custom vLLM on 4 GPUs.
tags: [llm, tts, realtime-dialogue, reasoning]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: step-audio-r1-1-card
    resource: ../raw/Step-Audio-R1.1.md
    kind: documentation
    title: Step-Audio-R1.1 model card
---

Step-Audio-R1.1 (Realtime) is stepfun-ai's major upgrade to Step-Audio-R1 for interactive spoken dialogue, combining a dual-brain Mind-Paced Speaking architecture that reasons while speaking with acoustic-grounded reasoning via iterative self-distillation, and is distributed as Apache-2.0-declared weights served through a customized vLLM backend on 4 GPUs (**Reported**).[^step-audio-r1-1-card]

## Model identity and release

- Name is Step-Audio-R1.1 (Realtime), described as a major upgrade to Step-Audio-R1; publisher is stepfun-ai via `huggingface.co/stepfun-ai/Step-Audio-R1.1`; source frontmatter declares `license: apache-2.0`, `pipeline_tag: audio-text-to-text`, `library_name: transformers`, and tags `audio-reasoning`, `chain-of-thought`, `multi-modal`, `step-audio-r1` (**Reported**, with the frontmatter fields **Observed** by static inspection).[^step-audio-r1-1-card]
- Intended use is interactive spoken dialogue with both real-time responsiveness and strong reasoning capability, explicitly positioned against conventional streaming speech models that trade intelligence for latency (**Reported**).[^step-audio-r1-1-card]
- No parameter count, training-data, language-coverage, or release-date statement appears in the captured text; model size and version history are unknown from this source (**Synthesis**).[^step-audio-r1-1-card]
- Demos are StepFun Audio Studio (requires an API key from the StepFun Open Platform) and the Hugging Face Space `stepfun-ai/Step-Audio-R1`; a WeChat group QR code is linked for discussion (**Reported**).[^step-audio-r1-1-card]

## Architecture and reasoning

- Realtime variant adopts a Dual-Brain Architecture from the cited *Mind-Paced Speaking* research: a Formulation Brain for high-level reasoning plus an Articulation Brain for speech generation, decoupling the two so Chain-of-Thought reasoning runs during speech output (**Reported**).[^step-audio-r1-1-card]
- The claimed effect is *thinking while speaking*: ultra-low latency maintained while handling complex tasks in real time (**Reported**).[^step-audio-r1-1-card]
- Acoustic-Grounded Reasoning grounds reasoning directly in acoustic representations rather than text transcripts, presented as the fix for an *inverted scaling* issue where reasoning over transcripts can degrade performance (**Reported**).[^step-audio-r1-1-card]
- Through iterative self-distillation, extended deliberation becomes a strength instead of a liability, enabling effective test-time compute scaling (**Reported**).[^step-audio-r1-1-card]
- The source claims state-of-the-art performance including top-ranking results on the AA benchmark, but the only supporting artifacts in the capture are three embedded benchmark-figure images with no transcribed numbers, so no metric, baseline, or protocol can be recorded from text (**Reported**, with the missing-figure-data qualifier **Synthesis**).[^step-audio-r1-1-card]

## Requirements, download, and serving

- Requirements are NVIDIA GPUs with CUDA support (tested on 4× L40S/H100/H800/H20), Linux, and Python >= 3.10.0 (**Reported**).[^step-audio-r1-1-card]
- Download paths are Git LFS (`git lfs install`, `git clone https://huggingface.co/stepfun-ai/Step-Audio-R1.1`) or the Hugging Face CLI (`hf download stepfun-ai/Step-Audio-R1.1 --local-dir ./Step-Audio-R1.1`) (**Reported**).[^step-audio-r1-1-card]
- Two serve paths use a customized vLLM backend: Docker (recommended) with image `stepfun2025/vllm:step-audio-2-v20250909`, or compiling the `github.com/stepfun-ai/vllm` fork on branch `feat/step-audio-support` with `VLLM_USE_PRECOMPILED=1 pip install -e .` in a venv (**Reported**).[^step-audio-r1-1-card]
- Docker serve example mounts `./Step-Audio-R1.1` to `/Step-Audio-R1.1`, exposes port 9999, and runs `vllm serve /Step-Audio-R1.1` with `--served-model-name Step-Audio-R1.1`, `--max-model-len 16384`, `--max-num-seqs 32`, `--tensor-parallel-size 4`, a long `--chat-template` handling `<audio_patch>` plus `<|BOT|>`/`<|EOT|>` roles and a `<think>` generation prompt, plus `--enable-log-requests --interleave-mm-strings --trust-remote-code` (**Reported**).[^step-audio-r1-1-card]
- Source-compile serve example runs `python3 -m vllm.entrypoints.openai.api_server` with `--model ../Step-Audio-R1.1`, same served name/port/template flags, plus `--host 0.0.0.0`, `--max-model-len 65536`, `--max-num-seqs 128`, `--tensor-parallel-size 4`, and `--gpu-memory-utilization 0.85`; both paths listen on `localhost:9999` after start (**Reported**).[^step-audio-r1-1-card]
- No latency, throughput, TTFA, concurrency, quantization, GGUF/edge, or offline-batch figures accompany the serving instructions in this source (**Synthesis**).[^step-audio-r1-1-card]

## Relationships

- Same-vendor editing sibling: [Step-Audio-EditX](step-audio-editx.md) covers stepfun-ai's 3B LLM-based expressive audio-editing model with dual-codebook tokenizer and GRPO training, while this concept covers the realtime reasoning-dialogue upgrade with dual-brain speaking architecture; no shared checkpoint or training data is asserted (**Synthesis**).[^step-audio-r1-1-card]
- Realtime speech-to-speech comparison: [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md) covers an 11B open end-to-end full-duplex model with ~450 ms turn-taking figures and tool calling, while this concept covers a realtime reasoning-dialogue model claiming ultra-low latency without published millisecond figures; no shared vendor or codebase is asserted (**Synthesis**).[^step-audio-r1-1-card]
- Full-duplex dialogue comparison: [PersonaPlex 7B v1](personaplex-7b-v1.md) covers a 7B open full-duplex speech-to-speech model with dual-stream listening-speaking, while this concept covers formulation/articulation decoupling for thinking-while-speaking; no shared vendor or benchmark is asserted (**Synthesis**).[^step-audio-r1-1-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no Docker image pulled, no vLLM compiled, and no latency, reasoning-quality, benchmark, or serving claim reproduced (**Synthesis**).[^step-audio-r1-1-card]
- Consequential material linked but absent from `raw/` and uninspected: the cited `MPS.pdf` (*Mind-Paced Speaking*) research, all three benchmark-figure CDN images, the WeChat QR image, StepFun Audio Studio and Open Platform pages, the Hugging Face Space, and the `stepfun-ai/vllm` fork branch contents (**Synthesis**).[^step-audio-r1-1-card]
- All architecture, latency, reasoning, benchmark, and deployment claims are source assertions without independent verification in this wiki; release and serving figures carry `stale_after: 2027-10-06` per the `llm`/`tts` domain rules (**Synthesis**).[^step-audio-r1-1-card]

[^step-audio-r1-1-card]: [Step-Audio-R1.1 model card](../raw/Step-Audio-R1.1.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, tags); `Introduction` (R1.1 Realtime upgrade, thinking-while-speaking positioning); `Mind-Paced Speaking (Low Latency)` (MPS.pdf citation, Dual-Brain Formulation/Articulation, CoT during output); `Acoustic-Grounded Reasoning (High Intelligence)` (inverted scaling, acoustic grounding, iterative self-distillation, test-time scaling, AA benchmark claim); three embedded `cdn-uploads.huggingface.co` benchmark images (untranscribed); `Online demonstration / StepFun Audio Studio` (Studio URL, Open Platform API-key requirement, Space link); `WeChat group` QR; `Model Usage / Requirements` (4× L40S/H100/H800/H20, Linux, Python ≥ 3.10); `Download Model` (Git LFS and `hf download` fences); `Deployment and Execution` Methods 1–2 (Docker image `stepfun2025/vllm:step-audio-2-v20250909`, `vllm serve` flags `--max-model-len 16384/65536`, `--max-num-seqs 32/128`, `--tensor-parallel-size 4`, `--chat-template` with `<audio_patch>`/`<|BOT|>`/`<think>`, `--interleave-mm-strings`, `feat/step-audio-support` branch, `VLLM_USE_PRECOMPILED=1`, `localhost:9999`).
