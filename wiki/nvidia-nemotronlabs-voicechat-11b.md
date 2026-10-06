---
type: Concept
title: NVIDIA NemotronLabs VoiceChat 11B
description: 11B-parameter open end-to-end full-duplex speech-to-speech model unifying streaming understanding and generation with ~450 ms turn-taking latency and first-open-FD tool calling.
tags: [llm, stt, tts, full-duplex, tool-calling]
status: stable
created: 2026-10-06
stale_after: 2027-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
sources:
  - id: voicechat-11b-card
    resource: ../raw/NVIDIA-NemotronLabs-VoiceChat-11B.md
    kind: documentation
    title: NVIDIA NemotronLabs VoiceChat 11B model card
---

NVIDIA NemotronLabs VoiceChat 11B is an 11B-parameter open end-to-end real-time full-duplex speech-to-speech model that jointly performs streaming speech understanding and speech generation in one unified architecture instead of a cascaded ASR → LLM → TTS stack, reporting ~450 ms turn-taking latency, #2 among open full-duplex models on VoiceBench and Full-Duplex-Bench 1.0, and first-open-full-duplex tool calling with live "on-hold" speech during tool execution (**Reported**).[^voicechat-11b-card]

## Model identity and release

- Card title is "NVIDIA NemotronLabs VoiceChat 11B"; creator is NVIDIA (NemotronLabs); frontmatter declares `license: openmdw-1.1`, `language: en`, and `base_model: nvidia/NVIDIA-Nemotron-Nano-9B-v2`; governing terms are the OpenMDW License Agreement v1.1; model version is v1.0; release date is August 3, 2026; deployment geography is Global (**Reported**).[^voicechat-11b-card]
- Stated use case targets researchers, developers, and professionals in NLP and speech technology for ASR, TTS, and voice-assistant development (**Reported**).[^voicechat-11b-card]
- Upstream checkpoint is `nvidia/NVIDIA-NemotronLabs-VoiceChat-11B` on Hugging Face; code is the `nemotron-labs-voicechat` branch of `NVIDIA-NeMo/Speech` on GitHub; the card embeds three audio players (natural turn-taking, barge-in/interruption, live tool calling) resolving to Hugging Face `resolve/main` WAV files (**Reported**).[^voicechat-11b-card]

## Architecture and I/O

- Architecture type is Hybrid Mamba/Transformer with 11B parameters: Fast Conformer speech encoder from `Nemotron-Speech-Streaming-En-0.6b`, [NVIDIA Nemotron Nano v2](https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-9B-v2) 9B LLM backbone predicting text tokens, NVIDIA TTS decoder and codec predicting audio codes for agent speech, plus a separate output channel predicting tool-calling scripts; audio signals are encoded by the fast conformer into audio tokens for the LLM backbone (**Reported**).[^voicechat-11b-card]
- For each tool, a specific "on-hold" message can be defined that the agent speaks as soon as the LLM generates the text triggering the tool call and response, keeping conversation flow during tool execution (**Reported**).[^voicechat-11b-card]
- Inputs are text prompt (string) and user speech (WAV/WebAudio) at 16 kHz; outputs are agent text, agent speech audio (WAV/WebAudio) at 22.05 kHz, and user transcription text (**Reported**).[^voicechat-11b-card]

## Software and hardware integration

- Runtime/acceleration engine is vLLM; test hardware is NVIDIA H100; supported GPUs are A100, H100, H200, B100, B200, and RTX-6000; preferred OS is Linux; the card notes GPU/CUDA acceleration over CPU-only and requires use-case-specific V-model testing before deployment (**Reported**).[^voicechat-11b-card]

## Training data

- Data modality is audio (speech) plus text with ~550k hours of audio training data; collection is Hybrid (Human, Synthetic, Automated) and labeling is Automated (**Reported**).[^voicechat-11b-card]
- Reported blend includes Nemotron 5.5 pre-training and SFT text, Brainy-mantis text, Greteal AI v1/v2 text, Ultrachat text, Blackwell studio real-speech recordings, Fisher real speech, LibriVox, LibriTTS, HiFi-TTS, internal Riva Speakers, public internet-scale data, PromptTTS, VCTK, Voxmovies, JL-Corpus, Nemotron Nano v3 function-calling data, and Persona Plex training datasets, including synthetic speech generated with various TTS systems over text corpora (**Reported**).[^voicechat-11b-card]

## Evaluation results

- VoiceBench (LLM voice-assistant benchmark over open-ended, multiple-choice QA, instruction-following, and adversarial subsets from real and synthetic speech): VoiceChat ranks #2 amongst all open full-duplex models (**Reported**).[^voicechat-11b-card]
- Full-Duplex-Bench 1.0 (pause handling, backchanneling, smooth turn-taking, interruption management with automatic metrics), #2 amongst all open models with these reported scores (**Reported**):[^voicechat-11b-card]

| Metric | Value |
| --- | --- |
| Pause Handling Synthetic TOR (lower better) | 0.153 |
| Pause Handling Candor TOR (lower better) | 0.255 |
| Smooth Turn Taking TOR (higher better) | 0.82 |
| Smooth Turn Taking Latency (lower better) | 448 ms |
| User Interruption TOR (higher better) | 1 |
| User Interruption Latency (lower better) | 480 ms |
| User Interruption GPT-4o (higher better) | 4.33 |

- AU Harness BFCL-v3 subset (textual BFCL-v3 instructions converted to spoken counterparts for in-audio tool calling): first open full-duplex model supporting tool calling with natural flow during execution; reported scores Simple 58.5%, Multiple 62.5%, Parallel 42.5%, Parallel Multiple 27.5%, Irrelevance 89.6%, Average 56.1% (**Reported**).[^voicechat-11b-card]
- Full-Duplex-Bench v3 (naturalistic speech, multi-step tool use; human-collected): competitive with frontier models on tool selection; reported scores Tool Selection 82.5%, Argument accuracy 42.2%, Pass@1 33% (**Reported**).[^voicechat-11b-card]

## Inference and deployment

- Two paths: offline inference from the Hugging Face checkpoint in a conda environment for non-interactive speech-to-speech checks, and interactive streaming via the optimized NVIDIA inference container (CUDA, Triton, vLLM) exposing a bidirectional WebSocket interface with function-calling support (**Reported**).[^voicechat-11b-card]
- Offline setup pins `torch==2.10.0`, `torchvision==0.25.0`, `torchaudio==2.10.0`, `transformers==4.56.0`, `tokenizers==0.22.0`, `lhotse==1.32.2`, `huggingface-hub==0.34.4`, `hf-xet==1.1.9`, `torchcodec==0.10.0`, plus `torch_audiomentations`, `jinja2`, `ninja`, `packaging`, `wheel`, `einops`, `causal-conv1d==1.6.2.post1`, and `mamba-ssm==2.3.2.post1` (installed `--no-build-isolation --no-deps` after removing `nvidia-resiliency-ext`); checkpoint fetched with `hf download`; inference scripts are `examples/speechlm2/offline_voicechat_infer.py` (general conversation) and `offline_voicechat_fc_infer.py` (function calling with `--api-response-json` pointing to a pre-written ASCII-only TTS-friendly tool response whose `tool_name` must match an available tool); custom audio needs trailing silence so the agent can respond (**Reported**).[^voicechat-11b-card]
- Offline function calling does not invoke a live tool; predicted calls surface in output JSON as `<TOOLCALL>[{"name": ..., "arguments": {...}}]</TOOLCALL>` (example: `generate_random_number` with `min`/`max`); interactive streaming supports live tool execution with prerequisites, deploy/run, model-repository generation, and API-reference docs in `voicechat_realtime_instructions/` (**Reported**).[^voicechat-11b-card]

## Function-calling prompt contract

- The default Jinja template appends available tools and the tool-call protocol to the system message; reference files are `offline_voicechat_fc_infer.py` (default prompt and construction logic) and `function_calling/template.jinja` (**Reported**).[^voicechat-11b-card]
- Rendered prompt rules: call a tool only when the request matches a name literally in `<AVAILABLE_TOOLS>` (never invent names); answer general-knowledge questions directly without tools; for uncovered external/live actions politely decline; use spoken values for arguments and ask when required arguments are missing instead of guessing; on tool failure report the API issue without retrying the same call; example tools are `get_weather(city)`, `get_stock_price(symbol)`, `get_top_news(topic?)`; tool responses return as `<TOOL_RESPONSE>[...]</TOOL_RESPONSE>` for follow-up (**Reported**).[^voicechat-11b-card]
- System prompts and API/tool responses must be ASCII-only (no em/en dashes, degree symbols, emoji, or other Unicode); convert tool responses into concise TTS-friendly ASCII sentences (**Reported**).[^voicechat-11b-card]

## Limitations, ethics, and references

- Known limitations are not enumerated in the card; it defers to the Known Limitations section of the branch README from internal testing (**Reported**).[^voicechat-11b-card]
- Ethical note states Trustworthy AI is a shared responsibility, developers must validate fitness for their industry/use case and misuse risks, and model quality, risk, or security issues go through NVIDIA's vulnerability-reporting channel (**Reported**).[^voicechat-11b-card]
- Cited foundations are the VoiceChat paper (arXiv:2609.21967, with BibTeX entry keyed `balam2026nemotronlabsvoicechatopenfullduplex`), SALM-Duplex (arXiv:2505.15670), an IEEE open full-duplex voice-agent paper, Audio Flamingo 3 (arXiv:2507.08128), and PersonaPlex (**Reported**).[^voicechat-11b-card]

## Relationships

- Builds on the [Audio Flamingo 3 and Next GGUF](audio-flamingo-3-and-next-gguf.md) family lineage: the VoiceChat card cites Audio Flamingo 3 as reference [4], while this concept covers the distinct end-to-end full-duplex speech-to-speech model rather than audio-understanding GGUF packaging (**Synthesis**).[^voicechat-11b-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no checkpoint loaded, and no latency, benchmark, or tool-calling figures reproduced (**Synthesis**).[^voicechat-11b-card]
- Referenced local artifact `VoiceChat-v1-TC voicechatv1.png`, embedded WAV samples, GitHub branch files, Hugging Face checkpoint, training datasets, benchmark suites, and cited papers were not fetched and remain uninspected; linked deploy/API docs were not fetched (**Synthesis**).[^voicechat-11b-card]
- All architecture, data-scale, latency, benchmark, tool-calling, and deployment claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per domain rules (**Synthesis**).[^voicechat-11b-card]

[^voicechat-11b-card]: [NVIDIA NemotronLabs VoiceChat 11B](../raw/NVIDIA-NemotronLabs-VoiceChat-11B.md) — locators: frontmatter (`license`, `language`, `base_model`); header audio-player table (3 samples); `Model Overview / Description` (11B end-to-end real-time full-duplex, ASR→LLM→TTS contrast, first-open-FD tool calling, on-hold messages, conformer→Nano-V2→TTS-decoder pipeline, separate tool channel); `Highlights` table (11B, ~450 ms, VoiceBench #2, 1st open FD, unified); `License/Terms`, `Use Case`, `Deployment Geography`, `Release Date`, `Model Version(s)`; `Model Architecture` (Hybrid Mamba/Transformer, 11B, 4-component list, diagram image); `Input`/`Output` tables (types, formats, 16 kHz / 22.05 kHz); `Software Integration` (vLLM, 6 GPUs, Linux, V-model note); `Training Dataset` (~550k hours, dataset blend, Hybrid/Automated); `Testing/Evaluation Dataset` (VoiceBench #2, FDB-1.0 #2 + 7-row table, AU-Harness/BFCL-v3 table, FDB-v3 table); `Inference` (vLLM/H100, offline vs streaming, conda pins, `hf download`, both scripts, `--api-response-json` contract, `<TOOLCALL>` example, realtime-instructions docs); `Function-calling system prompt example` (Jinja template files, ASCII-only rule, rendered rules, `<AVAILABLE_TOOLS>`/`<TOOLCALL>`/`<TOOL_RESPONSE>` protocol); `Known Limitations`, `Ethical Considerations`, `References` [1]–[5], `Citation` BibTeX.
