---
type: Concept
title: Confucius4-R2T2
description: NetEase Youdao true-streaming ASR model built on Qwen3-ASR-1.7B with append-only 80 ms–2 s chunked output, Longest Stable Prefix training, 200–600 ms reported latency, and vLLM plus WebSocket serving.
tags: [stt, asr, streaming, realtime, low-latency, multilingual, chinese, english, vllm, websocket]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T15:55:25Z }
stale_after: 2027-10-06
sources:
  - id: confucius4-r2t2-readme
    resource: ../raw/Confucius4-R2T2.md
    kind: documentation
    title: Confucius4-R2T2 GitHub README
---

Confucius4-R2T2 (R2T2, short for Real Real-Time Transcription) is a NetEase Youdao true-streaming automatic speech recognition model built on Qwen3-ASR-1.7B that emits committed, append-only transcript text in configurable 80 ms to 2 s decoding chunks with a vendor-reported 200 to 600 ms average latency, targeting live captioning, downstream NLP and LLM-agent pipelines, and simultaneous speech translation without the text revisions and visual flickering of pseudo-streaming systems (**Reported**).[^confucius4-r2t2-readme]

## Model identity and lineage

- Developer is NetEase Youdao; the ingested card frontmatter declares `base_model: Qwen/Qwen3-ASR-1.7B`, `pipeline_tag: automatic-speech-recognition`, and a NetEase model-use license for the weights (**Observed** by static inspection).[^confucius4-r2t2-readme]
- The README thanks the Alibaba Qwen team for open-sourcing the Qwen3-ASR modeling code that provides the architectural foundation for R2T2 (**Reported**).[^confucius4-r2t2-readme]
- Dual licensing splits code from weights: repository code is under Apache License 2.0 while model weights are under the NetEase Model Use License Agreement, so the weights need a license review before commercial deployment (**Reported**; commercial reading is **Synthesis**, not legal advice).[^confucius4-r2t2-readme]
- Model distribution spans Hugging Face (`netease-youdao/Confucius4-R2T2`), ModelScope, an online demo, and the project website plus GitHub repository with inference code and a vLLM backend for offline and realtime streaming inference (**Reported**).[^confucius4-r2t2-readme]

## Streaming design

- True streaming with append-only output: emitted text is committed permanently and never revised, so downstream consumers can act on partial transcripts instantly (**Reported**).[^confucius4-r2t2-readme]
- Training combines stable-prefix data construction, forced time-alignment data, and token-level audio segmentation with a Longest Stable Prefix (LSP) learning paradigm under which the model exposes only stable prefixes and waits for more audio context otherwise; the promised LSP tech report is not yet released, so the mechanism has no independent description beyond the README (**Reported**, with the missing report flagged as **Synthesis**).[^confucius4-r2t2-readme]
- Decoding chunks are configurable from 80 ms to 2 s for latency/accuracy tradeoffs, with 160 ms as the representative evaluation point; accuracy is claimed to stay close to offline recognition with no loss in offline accuracy from adding streaming support (**Reported**).[^confucius4-r2t2-readme]
- Context and hotword prompts are natively supported via a `context`/`CONTEXT` hint prepended to the prompt, alongside an explicit language hint (**Reported**).[^confucius4-r2t2-readme]
- A side-by-side demo video processes the same audio with GPT-Live-Transcribe and R2T2 in realtime; the video itself was not inspected, only its caption (**Observed**, uninspected remote media).[^confucius4-r2t2-readme]

## Reported accuracy at 160 ms chunks

All figures below are vendor self-reports from the comparison tables at 160 ms chunks, using WER (%) for English and CER (%) for Chinese, lower is better. The card marks pseudo-streaming rivals with ※ (their partials may revise text) and invites included maintainers to dispute results via its issue tracker; no figure here has been reproduced (**Reported**, trust note is **Synthesis**).[^confucius4-r2t2-readme]

### English (WER %, 160 ms)

| Dataset | R2T2 | Qwen3-ASR pseudo-streaming (2s/u2/t5) | Qwen3-ASR base at 160 ms |
| --- | ---: | ---: | ---: |
| AMI | 11.37 | 9.25 | 24.79 |
| Giga-clean | 9.60 | 8.61 | 24.37 |
| LS-clean | 2.13 | 1.67 | 22.30 |
| Earnings22 | 9.36 | 6.68 | 29.72 |
| TED-LIUM | 3.34 | 2.33 | 19.18 |
| EN-RealSI | 8.40 | 6.54 | 13.75 |

- Against open-source true-streaming rivals at 160 ms, the card reports R2T2 ahead on every English set: X-ASR trails by roughly 0.4–6.6 points (e.g. AMI 14.41, Earnings22 15.95), Nemotron streaming trails by roughly 1.7–7.9 points (e.g. AMI 18.11, Giga-clean 12.67, TED-LIUM 5.11), and Voxtral trails by roughly 1.3–4.6 points (e.g. AMI 15.94, Earnings22 11.66); WhisperRT at 200 ms is pseudo-streaming (**Reported**).[^confucius4-r2t2-readme]
- Against proprietary pseudo-streaming systems the card reports a split: R2T2 beats AssemblyAI at min_latency on AMI (11.37 vs 12.00) but trails it on Earnings22 (9.36 vs 7.47), and beats Commercial A on AMI (11.37 vs 13.27) and Giga-clean (9.60 vs 8.84 loses); Commercial A/B are undisclosed systems, so these cells are unverifiable from the card alone (**Reported**, anonymity limit is **Synthesis**).[^confucius4-r2t2-readme]

### Chinese (CER %, 160 ms)

| Dataset | R2T2 | Qwen3-ASR pseudo-streaming (2s/u2/t5) | Qwen3-ASR base at 160 ms |
| --- | ---: | ---: | ---: |
| Wenet-net | 5.87 | 4.94 | 19.79 |
| Wenet-meeting | 7.27 | 5.97 | 20.38 |
| SPEECHIO-06 | 7.30 | 6.10 | 24.50 |
| SPEECHIO-07 | 8.20 | 6.19 | 21.16 |
| CN-RealSI | 3.48 | 3.34 | 39.72 |

- Against open-source true-streaming rivals at 160 ms, the card reports R2T2 ahead of X-ASR (e.g. Wenet-net 8.81, Wenet-meeting 11.33, CN-RealSI 4.92), Nemotron streaming (e.g. Wenet-net 24.70, CN-RealSI 11.52), and Voxtral (e.g. Wenet-net 23.53, Wenet-meeting 60.54, CN-RealSI 8.74); WhisperRT is unsupported on these Chinese sets (U) and AssemblyAI trails (e.g. Wenet-net 12.91) (**Reported**).[^confucius4-r2t2-readme]
- Against proprietary pseudo-streaming systems the card reports R2T2 within about a point of Commercial A on most sets (e.g. Wenet-net 5.87 vs 5.13, CN-RealSI 3.48 vs 3.99 wins) and mixed against Commercial B (Wenet-meeting 7.27 vs 3.75 loses, SPEECHIO-06 7.30 vs 5.34 loses) (**Reported**).[^confucius4-r2t2-readme]

## Streaming latency evidence

- The headline latency claim is 200 to 600 ms average with near-offline accuracy; the English/Chinese Pareto and WER/latency figures (Figures 3–5) use retrospective chunk-wise mean fuzzy latency with lower-left better, but the figures are remote SVGs whose numeric series were not parsed, so only the headline range and the 80 ms–2 s chunk knob are compiled (**Reported**, with the unparsed-figure limit as **Synthesis**).[^confucius4-r2t2-readme]
- The Qwen3-ASR-base-at-160 ms column functions as an ablation for the streaming training: forcing the unmodified base model to 160 ms chunks collapses accuracy (e.g. AMI 24.79, CN-RealSI 39.72 CER), while R2T2 at the same chunk size stays near its pseudo-streaming teacher (**Reported**; ablation reading is **Synthesis**).[^confucius4-r2t2-readme]

## Inference and serving

- Environment: a fresh isolated Python 3.12 environment is tested (3.10+ supported) via conda (`conda create -n confucius4-r2t2 python=3.12`) or `uv venv`, then editable install `pip install -e .` with the vLLM backend; the strict vLLM CUDA/PyTorch version matrix must match the host runtime (**Reported**).[^confucius4-r2t2-readme]
- Docker (recommended path) runs on the `qwenllm/qwen3-asr` image with the NVIDIA Container Toolkit, mounting the workspace at `/data/shared/confucius4-r2t2` and mapping host port 8000 to container port 80; services must bind `0.0.0.0` (**Reported**).[^confucius4-r2t2-readme]
- `run_example.sh` takes an audio file (any sample rate, resampled to 16 kHz internally) with env-var configuration: `MODEL_PATH` (required), `INFER_MODE` (`stream_vllm` default, or `onetime_vllm`), `LANGUAGE` (default `Chinese`), `CHUNK_SIZE_MS` (default 160), `UNFIXED_TOKEN_NUM` (default 1, rollback window), `CONTEXT`, `CUDA_VISIBLE_DEVICES`, and `LOG_FILE` (**Reported**).[^confucius4-r2t2-readme]
- The Python API reuses the `qwen_asr.Qwen3ASRModel.LLM` interface: offline `transcribe` with language and timestamp options, and streaming via `init_streaming_state` (`context`, `language`, `unfixed_chunk_num`, `unfixed_token_num`, `chunk_size_sec`) fed 160 ms waveform slices through `streaming_transcribe` with small `max_new_tokens`, closed by `finish_streaming_transcribe`; vLLM code must run under `if __name__ == '__main__':` to avoid spawn errors (**Reported**).[^confucius4-r2t2-readme]
- A ready-to-run WebSocket server (`ws_server.py` plus `run_start_server.sh start|kill|restart` and reference client `ws_client.py`) serves multi-client realtime ASR on port 8272 by default with a FireRedVAD `Stream-VAD` model (default `checkpoints/vad/Stream-VAD`, fetched from Hugging Face via `hf download` or git clone); the endpoint is `/asr_stream_api_v1`, each message carrying the new incremental `text` chunk, with clients sending raw 16 kHz mono int16 binary frames and the string `YOUDAO_ONETIME_ASR_STREAM_EOS` to end audio, and server replies shaped as status plus requestId plus message text, reset flag, and per-message cost fields (**Reported**).[^confucius4-r2t2-readme]

## Language coverage

- Streaming recognition is optimized for Chinese and English; beyond them the card claims useful cross-lingual streaming on French, German, Italian, Japanese, Korean, Portuguese, Russian, Spanish, Arabic, and others, with no per-language figures published (**Reported**).[^confucius4-r2t2-readme]

## Relationships

- Derived from [Qwen3-ASR family](qwen3-asr-family.md): the card names `Qwen/Qwen3-ASR-1.7B` as the base model, so read that concept for the encoder lineage language coverage, unified streaming/offline behavior, and serving toolkit (**Synthesis**).[^confucius4-r2t2-readme]
- Compared with [Audio8 ASR Infinite](audio8-asr-infinite.md): both are true-streaming Chinese/English recognizers with 80–160 ms chunk or clock settings, but Audio8 Infinite runs a native one-token-per-clock design with rolling KV cache for 24/7 operation and semantic VAD, while R2T2 keeps the Qwen3-ASR audio-LLM architecture with LSP-gated prefix emission (**Synthesis**).[^confucius4-r2t2-readme]
- Compared with [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) and [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md): the card benchmarks all three at 160 ms chunks and reports R2T2 ahead, but the protocol and hardware are undisclosed, so treat the ordering as a vendor claim pending independent measurement (**Reported**, caution is **Synthesis**).[^confucius4-r2t2-readme]
- VAD pairing uses the external FireRedVAD Stream-VAD model, which has no concept page in this wiki; contrast with the in-wiki [Silero VAD](silero-vad.md) frontend pattern when designing the streaming pipeline (**Synthesis**).[^confucius4-r2t2-readme]

## Coverage and limits

- Source inspected statically only: the single-file README in `raw/` was read end to end; no package was installed, no model was downloaded, and no WER, CER, or latency figure was reproduced (**Synthesis**).[^confucius4-r2t2-readme]
- Remote and linked assets were excluded without fetching: Hugging Face and ModelScope model pages, the online demo, project website, the `qwenllm/qwen3-asr` Docker image, FireRedVAD weights, the comparison video (caption only), the SVG latency figures (numeric series unparsed), logo and framework images, badges, and the WeChat QR code (**Synthesis**).[^confucius4-r2t2-readme]
- The LSP tech report is announced but unreleased, the anonymous Commercial A/B baselines and undisclosed benchmark hardware and protocol limit independent verification, and the card itself invites included maintainers to dispute results; business-contact details from the contact section are intentionally omitted (**Synthesis**).[^confucius4-r2t2-readme]

[^confucius4-r2t2-readme]: [Confucius4-R2T2 GitHub README](../raw/Confucius4-R2T2.md) — locators: frontmatter (`base_model`, `pipeline_tag`, `license_name`); intro feature bullets (latency, chunking, backends, hotwords, multilingual); `## Evaluation` / `### Streaming performance` (Figures 3–5, retrospective chunk-wise mean fuzzy latency) / `### Accuracy` (`#### English` and `#### Chinese` tables at 160 ms, ※ pseudo-streaming note); `## Installation`, `## Docker (recommended)`, `## Quick Start` / `### Configuration` (env-var table); `## Python API` (offline and streaming snippets); `## WebSocket Server` (launcher flags, VAD download, endpoint, message-format JSON, client flags); `## Supported Languages`; `## Acknowledgements`; `## Citation` (2026); `## License` (dual Apache-2.0 / NetEase Model Use License Agreement).

