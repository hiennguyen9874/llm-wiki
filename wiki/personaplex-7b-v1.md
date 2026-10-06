---
type: Concept
title: PersonaPlex 7B v1
description: 7B-parameter open full-duplex speech-to-speech model based on Moshi/Moshiko with dual-stream listening-speaking, voice-plus-text persona conditioning, and published FullDuplexBench scores.
tags: [llm, stt, tts, full-duplex, voice-cloning]
status: stable
created: 2026-10-06
stale_after: 2027-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
sources:
  - id: personaplex-7b-card
    resource: ../raw/personaplex-7b-v1.md
    kind: documentation
    title: PersonaPlex 7B v1 model card
---

PersonaPlex 7B v1 is NVIDIA's 7B-parameter open real-time full-duplex speech-to-speech conversational model that jointly performs streaming speech understanding and generation in one Moshi-based architecture instead of a cascaded ASR → LLM → TTS stack, conditioning each conversation on a voice prompt plus a text persona prompt and reporting FullDuplexBench conversational-dynamics and latency figures (**Reported**).[^personaplex-7b-card]

## Model identity and release

- Card title is "PersonaPlex: Voice and role control for full duplex conversational speech models"; creator is NVIDIA; Hugging Face checkpoint is `nvidia/personaplex-7b-v1`; code is `nvidia/personaplex` on GitHub; demo is the PersonaPlex project page; paper is the PersonaPlex preprint (arXiv:2602.06053); frontmatter declares `pipeline_tag: audio-to-audio`, `library_name: moshi`, `language: en`, base model `kyutai/moshiko-pytorch-bf16`, and tags `speech-to-speech` and `agent` (**Reported**).[^personaplex-7b-card]
- Governing terms are the NVIDIA Open Model License Agreement, with additional information pointing to CC-BY-4.0 for the `kyutai/moshiko-pytorch-bf16` base; the card states the model is ready for commercial use; deployment geography is Global; model version is v1.0; release date is 01/15/2026 on both Hugging Face and GitHub (**Reported**).[^personaplex-7b-card]
- Stated use case is English speech response for English speech input wherever NVIDIA speech-to-speech conversational models are used (**Reported**).[^personaplex-7b-card]

## Architecture and conversational behavior

- Architecture type is Transformer with 7B parameters, developed from Moshi (Moshiko weights): Moshi uses the Mimi speech encoder (ConvNet, Transformer), Moshi Temporal Transformer plus Depth Transformer, and Mimi speech decoder (Transformer, ConvNet) (**Reported**).[^personaplex-7b-card]
- The model operates on continuous audio encoded with a neural codec and predicts both text tokens and audio tokens autoregressively to produce spoken responses; incoming user audio is incrementally encoded and fed to the model while it simultaneously generates outgoing speech (**Reported**).[^personaplex-7b-card]
- It runs in a dual-stream configuration in which listening and speaking occur concurrently, updating internal state from ongoing user speech while producing fluent output audio, enabling interruptions, barge-ins, overlaps, and rapid turn-taking (**Reported**).[^personaplex-7b-card]
- Before a conversation begins, the model is conditioned on two prompts: a voice prompt of audio tokens establishing target vocal characteristics and speaking style, and a text prompt specifying persona attributes such as role, background, and scenario context; together they define conversational identity and guide linguistic and acoustic behavior (**Reported**).[^personaplex-7b-card]

## Inputs and outputs

- Inputs are text prompt (string) and user speech audio (WAV/WebAudio), one-dimensional parameters, with 24 kHz sample rate for audio (**Reported**).[^personaplex-7b-card]
- Outputs are agent text (string) and agent speech audio (WAV/WebAudio), one-dimensional parameters, with 24 kHz sample rate for audio (**Reported**).[^personaplex-7b-card]

## Software and hardware integration

- Runtime and acceleration engine is PyTorch; test hardware is NVIDIA A100 80 GB; supported microarchitectures are NVIDIA Ampere (A100) and NVIDIA Hopper (H100); preferred OS is Linux (**Reported**).[^personaplex-7b-card]
- The card notes GPU/CUDA acceleration over CPU-only solutions and requires additional use-case-specific testing following V-model methodology at unit and system levels before deployment (**Reported**).[^personaplex-7b-card]

## Training data

- Training modality is audio (speech) under 10,000 hours; collection method is Human and labeling method is Automated; the named source is Fisher English Part 1 and Part 2, with 7,303 conversations of up to 10 minutes each (**Reported**).[^personaplex-7b-card]

## Evaluation results

- Testing source is FullDuplexBench, described as a public benchmark aggregating various synthetic and real datasets, with Hybrid (Human, Synthetic, Automated) collection and Automated labeling; speaker similarity (SSIM) between voice prompts and model outputs on the User Interruption portion was measured with WavLM-TDNN embedding cosine similarity (**Reported**).[^personaplex-7b-card]
- Reported FullDuplexBench scores (**Reported**):[^personaplex-7b-card]

| Metric | Value |
| --- | --- |
| Pause Handling (Synthetic) TOR, lower better | 0.358 |
| Pause Handling (Candor) TOR, lower better | 0.431 |
| Backchannel TOR, lower better | 0.273 |
| Backchannel Freq, higher better | 0.042 |
| Backchannel JSD, lower better | 0.662 |
| Smooth Turn Taking TOR, higher better | 0.908 |
| Smooth Turn Taking Latency, lower better | 0.170 |
| User Interruption TOR, higher better | 0.950 |
| User Interruption GPT-4o, higher better | 4.290 |
| User Interruption Latency, lower better | 0.240 |
| User Interruption SSIM (WavLM), higher better | 0.650 |

- The card asserts PersonaPlex outperforms other open-source and commercial systems on conversational dynamics, response and interruption latency, and task adherence in both question-answering assistant and customer-service roles (**Reported**).[^personaplex-7b-card]
- Three result figures are embedded with captions: FullDuplexBench conversational-dynamics evaluation (success rate uses Takeover Rate for Smooth Turn-Taking and User Interruption, and 1-TOR for Pause Handling); FullDuplexBench latency evaluation (smooth turn-taking latency from user stop to agent start; interruption latency from user interruption to agent stop); task-adherence evaluation (FullDuplexBench general-knowledge QA in User Interruption judged by GPT-4o, plus ServiceDuplexBench customer-service scenarios noted as to be released soon) (**Reported**).[^personaplex-7b-card]

## Limitations, ethics, and references

- Ethical note states Trustworthy AI is a shared responsibility, developers must work with their model team to validate fitness for industry and use case and address misuse, and model quality, risk, or security issues go through NVIDIA's vulnerability-reporting channel; detailed Model Card++ subcards for Bias, Explainability, Safety and Security, and Privacy are linked as `bias.md`, `explainability.md`, `safety.md`, and `privacy.md` (**Reported**).[^personaplex-7b-card]
- Cited foundations are Moshi and Mimi (arXiv:2410.00037) and FullDuplexBench (arXiv:2503.04721); the paper citation is Roy et al. 2026 `roy2026personaplexvoicerolecontrol` with BibTeX entry for arXiv:2602.06053 (**Reported**).[^personaplex-7b-card]

## Relationships

- End-to-end full-duplex comparison: [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md) covers NVIDIA's 11B-parameter Hybrid Mamba/Transformer full-duplex speech-to-speech model with Conformer encoder, Nano-v2 backbone, and tool calling, which cites PersonaPlex as a foundation and lists Persona Plex datasets in its training blend, while this concept covers the distinct 7B Moshi/Moshiko-based PersonaPlex checkpoint with voice-plus-text persona conditioning (**Synthesis**).[^personaplex-7b-card]
- Edge-packaging catalog: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) lists a `PersonaPlex-GGUF` row (`personaplex` family, Q4_K + Q8, NVIDIA Open Model License) for the audio.cpp runtime, while this concept covers the upstream PyTorch `nvidia/personaplex-7b-v1` checkpoint; no shared weight file is asserted (**Synthesis**).[^personaplex-7b-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no checkpoint loaded, no inference executed, and no latency, benchmark, SSIM, or task-adherence figures reproduced (**Synthesis**).[^personaplex-7b-card]
- Referenced but unfetched and absent from `raw/`: `figures/results_conversation_dynamics.png`, `figures/results_latency.png`, `figures/results_task_adherence.png`, Model Card++ subcards (`bias.md`, `explainability.md`, `safety.md`, `privacy.md`), GitHub code repository, Hugging Face checkpoint, demo page, preprint, Fisher LDC parts, FullDuplexBench suite, WavLM-TDNN paper, and Moshi/Mimi/Moshiko artifacts (**Synthesis**).[^personaplex-7b-card]
- All architecture, I/O, hardware, data-scale, benchmark, comparison, and deployment claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per domain rules (**Synthesis**).[^personaplex-7b-card]

[^personaplex-7b-card]: [PersonaPlex 7B v1](../raw/personaplex-7b-v1.md) — locators: frontmatter (`license`, `language`, `base_model: kyutai/moshiko-pytorch-bf16`, `library_name: moshi`, `pipeline_tag: audio-to-audio`, `tags`); header links (code, demo, paper); `Description` (streaming understanding+generation, neural-codec text+audio autoregression, incremental encoding, dual-stream listening/speaking, interruptions/barge-ins/overlaps/turn-taking, voice-prompt + text-prompt persona conditioning, commercial-use sentence); `License/Terms of Use`, `Use Case`, `Deployment Geography`, `Release Date`, `Model Version(s)`; `Model Architecture` (Transformer, Moshi, Mimi encoder/Temporal+Depth/decoder bullets, Moshiko basis, 7B); `Input(s)`/`Output(s)` (types, formats, 1D, 24 kHz); GPU-optimization paragraph; `Software Integration` (PyTorch, Ampere/Hopper, Linux, V-model note); `Inference` (PyTorch, A100 80 GB); `Training Dataset` (Fisher Part1/Part2 links, <10k hours, Human/Automated, 7303 conversations); `Testing/Evaluation Dataset` (FullDuplexBench link, Hybrid/Automated, SSIM WavLM-TDNN sentence, 11-row benchmark table, comparison sentence); three `figure` blocks with captions (dynamics TOR convention, latency definitions, task-adherence GPT-4o/ServiceDuplexBench note); `Ethical Considerations` (shared-responsibility paragraph, subcard links, reporting link); `Citation` BibTeX; `References` [1]–[2].
