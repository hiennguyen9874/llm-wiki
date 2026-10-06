---
type: Concept
title: Voxtral Mini 4B Realtime 2602
description: Mistral AI 4B-scale natively streaming multilingual speech-transcription model with a causal audio encoder, configurable transcription delay, and vLLM realtime serving.
tags: [stt, asr, streaming, multilingual, realtime]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: voxtral-mini-4b-realtime-card
    resource: ../raw/Voxtral-Mini-4B-Realtime-2602.md
    kind: documentation
    title: Voxtral Mini 4B Realtime 2602 model card
---

Voxtral Mini 4B Realtime 2602 (`mistralai/Voxtral-Mini-4B-Realtime-2602`) is Mistral AI's 4B-parameter natively streaming multilingual speech-transcription model, pairing a ~970M causal audio encoder trained from scratch with a ~3.4B language model, with a configurable transcription delay whose recommended 480 ms operating point matches leading offline open-source transcription models and realtime APIs at under 500 ms of delay, served primarily through vLLM's realtime endpoint on a single ≥16 GB GPU (**Reported**).[^voxtral-mini-4b-realtime-card]

## Identity and release

- Checkpoint is `mistralai/Voxtral-Mini-4B-Realtime-2602`; base model is `mistralai/Ministral-3-3B-Base-2512`; weights are BF16 under the Apache-2.0 license with a third-party-rights disclaimer; frontmatter declares `library_name: vllm`, `pipeline_tag: automatic-speech-recognition`, `inference: false`, and 13 languages: en, fr, es, de, ru, zh, ja, it, pt, nl, ar, hi, ko (**Observed** by static inspection).[^voxtral-mini-4b-realtime-card]
- Positioned as among the first open-source solutions to reach offline-comparable accuracy below 500 ms of delay, aimed at voice assistants and live subtitling; listed use cases are private meeting transcription, live subtitle creation, and realtime assistants with speech understanding (**Reported**).[^voxtral-mini-4b-realtime-card]
- Upstream pointers are the Voxtral Transcribe 2 blog post, a Hugging Face Space demo, technical report arXiv 2602.11298, and the vLLM streaming-input blog; none was fetched into `raw/` (**Observed** by static inspection).[^voxtral-mini-4b-realtime-card]

## Architecture

- Two components: an ≈3.4B language model and an ≈970M audio encoder trained from scratch with causal attention for streaming; both the encoder and the LLM backbone use sliding-window attention for unbounded ("infinite") streaming (**Reported**).[^voxtral-mini-4b-realtime-card]
- One text token is worth 80 ms of audio, which sets context sizing: transcribing a 1-hour meeting needs `--max-model-len >= 3600 / 0.8 = 45000`; default vLLM parameters give 131072 tokens (~3 hours); throughput exceeds 12.5 tokens/second (**Reported**).[^voxtral-mini-4b-realtime-card]

## Streaming delay knob

- The transcription delay trades latency against accuracy; 480 ms is the recommended sweet spot, matching offline open-source leaders and realtime APIs (**Reported**).[^voxtral-mini-4b-realtime-card]
- The delay is set through `"transcription_delay_ms": 480` in `tekken.json`, adjustable to any multiple of 80 ms between 80 and 1200, plus 2400 as a standalone value (**Reported**).[^voxtral-mini-4b-realtime-card]
- Wording differs by section: the intro advertises configurable delays of 240 ms to 2.4 s, the features list says 80 ms to 2.4 s, and the recommended-settings section gives the 80–1200 ms multiples plus 2400; all three wordings are recorded here without choosing between them (**Observed** by static inspection).[^voxtral-mini-4b-realtime-card]

## Benchmarks

All figures are vendor-reported word error rates from the card; nothing was reproduced. FLEURS averages across the card's 13 evaluated languages (**Reported**):[^voxtral-mini-4b-realtime-card]

| Model | Delay | AVG | ar | de | en | es | fr | hi | it | nl | pt | zh | ja | ko | ru |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Voxtral Mini Transcribe 2.0 | Offline | 5.90% | 13.54% | 3.54% | 3.32% | 2.63% | 4.32% | 10.33% | 2.17% | 4.78% | 3.56% | 7.30% | 4.14% | 12.29% | 4.75% |
| **Voxtral Mini 4B Realtime 2602** | 480 ms | 8.72% | 22.53% | 6.19% | 4.90% | 3.31% | 6.42% | 12.88% | 3.27% | 7.07% | 5.03% | 10.45% | 9.59% | 15.74% | 6.02% |
| **Voxtral Mini 4B Realtime 2602** | 160 ms | 12.60% | 24.33% | 9.50% | 6.46% | 5.34% | 9.75% | 15.28% | 5.59% | 11.39% | 10.01% | 17.67% | 19.17% | 19.81% | 9.53% |
| **Voxtral Mini 4B Realtime 2602** | 240 ms | 10.80% | 23.95% | 8.15% | 5.91% | 4.59% | 8.00% | 14.26% | 4.41% | 9.23% | 7.51% | 13.84% | 15.17% | 17.56% | 7.87% |
| **Voxtral Mini 4B Realtime 2602** | 960 ms | 7.70% | 20.32% | 4.87% | 4.34% | 2.98% | 5.68% | 11.82% | 2.46% | 6.76% | 4.57% | 8.99% | 6.80% | 14.90% | 5.56% |
| **Voxtral Mini 4B Realtime 2602** | 2400 ms | 6.73% | 14.71% | 4.15% | 4.05% | 2.71% | 5.23% | 10.73% | 2.37% | 5.91% | 3.93% | 8.48% | 5.50% | 14.30% | 5.41% |

- Long-form English at 480 ms stays close to the offline Transcribe 2.0 baseline: Meanwhile (<10 m) 5.05% vs 4.08%, E-21 (<10 m) 10.23% vs 9.81%, E-22 (<10 m) 12.30% vs 11.69%, TEDLIUM (<20 m) 3.17% vs 2.86% (**Reported**).[^voxtral-mini-4b-realtime-card]
- Short-form English at 480 ms likewise tracks the offline baseline: CHiME-4 10.50% vs 10.39%, GigaSpeech 2k subset 7.35% vs 6.81%, AMI IHM 15.05% vs 14.43%, SwitchBoard 11.65% vs 11.54%, CHiME-4 SP 12.41% vs 10.42%, GISpeech 2k subset 1.73% vs 1.74% (**Reported**).[^voxtral-mini-4b-realtime-card]

## Recommended settings

- Always set temperature to 0.0 for transcription (**Reported**).[^voxtral-mini-4b-realtime-card]
- Size `--max-model-len` from the 80 ms-per-token rule (45000 minimum for 1 hour); the card recommends plain default vLLM parameters (131072, ~3 hours) for the best experience, and notes RoPE pre-allocation caps the theoretical unlimited recording (**Reported**).[^voxtral-mini-4b-realtime-card]
- Use websockets for audio streaming sessions; the 480 ms delay is the recommended default (**Reported**).[^voxtral-mini-4b-realtime-card]

## vLLM serving (recommended)

- Install the nightly vLLM package (`uv pip install -U vllm`), which pulls `mistral_common >= 1.9.0`; add audio libraries (`soxr`, `librosa`, `soundfile`); prefer Transformers v5 over v4 to avoid terminal warning clutter (**Reported**).[^voxtral-mini-4b-realtime-card]
- Runs on a single GPU with ≥16 GB memory in BF16; launch in eager mode with `VLLM_DISABLE_COMPILE_CACHE=1 vllm serve mistralai/Voxtral-Mini-4B-Realtime-2602 --compilation_config '{"cudagraph_mode": "PIECEWISE"}'`; `--max-num-batched-tokens` balances throughput against latency and `--max-model-len` can be lowered to save RoPE memory when long sessions are not needed (**Reported**).[^voxtral-mini-4b-realtime-card]
- Serving exposes vLLM's realtime endpoint (`/v1/realtime`); the card points to two example clients, an audio-file streamer and a Gradio live-microphone transcription demo (**Reported**).[^voxtral-mini-4b-realtime-card]
- The card warns the novel architecture is currently only supported in vLLM and welcomes community contributions for Transformers and llama.cpp ports (**Reported**).[^voxtral-mini-4b-realtime-card]

## Transformers use

- Supported natively from `transformers >= 5.2.0` with `VoxtralRealtimeForConditionalGeneration` plus `AutoProcessor`; install `mistral-common[audio]` for audio tokenization (**Reported**).[^voxtral-mini-4b-realtime-card]
- The documented pattern downloads a sample clip, resamples to the feature extractor's rate, moves inputs to the model device and dtype, calls `model.generate`, and decodes with `skip_special_tokens=True` (**Reported**).[^voxtral-mini-4b-realtime-card]

## On-device and community ports (untested)

- ExecuTorch support is explicitly untested with possible sharp edges; the card points to an offline MacBook demo (`mistral-labs/Voxtral-Mini-4B-Realtime-2602-ExecuTorch`) and the official ExecuTorch Voxtral realtime README, plus a pure-C tip (`voxtral.c`) (**Reported**).[^voxtral-mini-4b-realtime-card]
- Untested community integrations are listed for pure C, the mlx-audio framework, MLX (`voxmlx`), and Rust; all are contributor snapshots the card does not vouch for (**Reported**).[^voxtral-mini-4b-realtime-card]

## Relationships

- Non-streaming family member: [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md) is the Ministral-based audio-understanding checkpoint for transcription with language detection, audio Q&A, and voice function calling; read both when choosing between joint audio understanding (3B) and latency-tunable realtime transcription (4B Realtime) (**Synthesis**).[^voxtral-mini-4b-realtime-card]
- Derived streaming work: [Audio8 ASR Infinite](audio8-asr-infinite.md) initializes its causal audio tower from Voxtral Realtime 4B and re-reports this checkpoint as the competitor column in its Aishell/LibriSpeech table; read both when tracing what Audio8 changes (Qwen2.5-3B decoder, selectable clock, rolling KV cache, semantic VAD) (**Synthesis**).[^voxtral-mini-4b-realtime-card]
- Evaluated against [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md): the NVIDIA cache-aware multilingual streaming baseline appears in this card's comparison framing and in Audio8 Infinite's shared comparison table; read both when contrasting native causal-encoder streaming (Voxtral) against chunked cache-aware streaming with inference-time chunk selection (Nemotron) (**Synthesis**).[^voxtral-mini-4b-realtime-card]
- Packaging catalog: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) lists a `Voxtral-Mini-4B-Realtime-2602-GGUF` entry (BF16 + Q8 + Q4_K, Apache-2.0) for edge deployment; check that catalog before assuming a maturation path beyond vLLM serving (**Synthesis**).[^voxtral-mini-4b-realtime-card]

## Coverage and limits

- Source inspected statically only; no vLLM serve, no model download, no audio transcribed, and no WER, latency, throughput, or VRAM figure reproduced (**Synthesis**).[^voxtral-mini-4b-realtime-card]
- The architecture JPEG, `tekken.json`, blog posts, arXiv 2602.11298, vLLM documentation and example clients, ExecuTorch demo and README, and all four community ports were linked but not fetched and are absent from `raw/`; only `raw/Voxtral-Mini-4B-Realtime-2602.md` was inspected (**Synthesis**).[^voxtral-mini-4b-realtime-card]
- The capabilities list claims "dozens of languages" while the frontmatter and header enumerate 13; both wordings are preserved here and neither is resolved (**Observed** by static inspection).[^voxtral-mini-4b-realtime-card]
- All accuracy, delay, throughput, VRAM, install, and usage claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^voxtral-mini-4b-realtime-card]

[^voxtral-mini-4b-realtime-card]: [Voxtral Mini 4B Realtime 2602 model card](../raw/Voxtral-Mini-4B-Realtime-2602.md) — locators: frontmatter (`library_name`, 13-code `language` list, `license`, `base_model` Ministral-3-3B-Base-2512, `pipeline_tag`, `tags`, `inference`); header (multilingual realtime positioning, <500 ms claim, 13-language support, 4B on-device claim, >12.5 tok/s, BF16 Apache-2.0, blog/demo/technical-report/vLLM-blog links); `Key Features` (3.4B LM + 970M encoder bullets, causal training, sliding-window infinite streaming, architecture image, transcription/multilingual/realtime/delay capabilities, 80 ms–2.4 s delay range, use-case list); `Recommended Settings` (temperature 0.0, 80 ms-per-token rule with 45000/131072 figures, websockets, 480 ms sweet spot, `tekken.json` `transcription_delay_ms` multiples rule); `Benchmark Results > Fleurs` (6-row × 13-language WER table), `> Long-form English` (4-column table vs Transcribe 2.0), `> Short-form English` (6-column table vs Transcribe 2.0); `Usage` (vLLM/Transformers/ExecuTorch/community framework list, vLLM-only warning); `vLLM` (`Installation` pins `mistral_common >= 1.9.0`, `soxr/librosa/soundfile`, Transformers v5; `Serve` eager command with PIECEWISE cudagraph, ≥16 GB note, `max-num-batched-tokens`/`max-model-len` flags; `Client` `/v1/realtime` route and two example clients); `Transformers` (>= 5.2.0, `VoxtralRealtimeForConditionalGeneration` generate/decode fence); `ExecuTorch` (untested warning, demo link, README link, `voxtral.c` tip); `Community Contributions` (C, mlx-audio, MLX, Rust links); `License` (Apache-2.0 plus third-party-rights disclaimer).
