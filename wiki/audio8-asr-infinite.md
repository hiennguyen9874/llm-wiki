---
type: Concept
title: Audio8 ASR Infinite
description: Native streaming bilingual Chinese-English ASR model with selectable 80/120/160 ms clock, configurable transcription delay, rolling KV cache for 24/7 operation, and semantic VAD.
tags: [ml, asr, streaming, speech-recognition]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: audio8-infinite-card
    resource: ../raw/Audio8-ASR-Infinite.md
    kind: documentation
    title: Audio8 ASR Infinite model card
---

Audio8 ASR Infinite is a native streaming automatic speech recognition model for Chinese and English that emits one text token per selectable audio clock step (80/120/160 ms) with a configurable transcription delay (240–560 ms), using a rolling KV cache with exact RoPE re-basing to keep memory and latency constant over unlimited-length 24/7 transcription (**Reported**).[^audio8-infinite-card]

## Identity and release

- Card title is `Audio8 ASR Infinite`; checkpoint is `Edge0/Audio8-ASR-Infinite`; repository is `https://github.com/Edge0-AI/Audio8-ASR-Infinite`; frontmatter declares `license: apache-2.0`, languages `zh` and `en`, `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, and tags `streaming`, `realtime`, `speech-recognition`, and `audio` (**Reported**).[^audio8-infinite-card]
- Task is streaming speech recognition; advertised positioning is maximum responsiveness with a native streaming architecture decoding 12.5 times per second at the 80 ms clock (**Reported**).[^audio8-infinite-card]
- Bilingual coverage is Chinese and English (**Reported**).[^audio8-infinite-card]
- Semantic VAD distinguishes thinking pauses, stuttering, and real end of turn, where traditional acoustic VAD usually fails (**Reported**).[^audio8-infinite-card]

## Streaming operation points

- Selectable streaming clock emits one text token per clock step: 12.5 decisions per second at 80 ms, 8.3 at 120 ms, and 6.25 at 160 ms, trading perception granularity against resource cost (**Reported**).[^audio8-infinite-card]
- Post-trained combinations (**Reported**):[^audio8-infinite-card]

| audio clock | `frame_len` | `streaming_n_left_pad_tokens` | selectable `target_delay_ms` |
| --- | --- | --- | --- |
| 80 ms | 4 | 18 | 240 / 320 / 480 / 560 |
| 120 ms | 6 | 12 | 240 / 480 |
| 160 ms | 8 | 9 | 320 / 480 |

- `target_delay_ms` must be an integer multiple of the selected clock, so longer delays remain available at every clock even when not listed in the table (**Reported**).[^audio8-infinite-card]
- Native checkpoint context is 30 seconds; the rolling KV cache extends this to 24/7 nonstop transcription (**Reported**).[^audio8-infinite-card]

## Architecture and checkpoint

- Inherits the Voxtral realtime audio architecture with DSM-style streaming (**Reported**).[^audio8-infinite-card]
- Trained components (**Reported**):[^audio8-infinite-card]

| Component | Initial weights | Trained |
| --- | --- | --- |
| Causal Audio Tower | Voxtral Realtime 4B | ✅ |
| Audio Projector | random initialisation | ✅ |
| Frame Length Embedding | random initialisation | ✅ |
| Decoder | Qwen2.5-3B-Instruct | ✅ |
| LM Head | Qwen2.5-3B-Instruct | ✅ |

- Checkpoint specification: audio tower with 32 layers, hidden size 1280, 128 mel bins, sliding window 750; text decoder with 36 layers, hidden size 2048, 16 query heads and 2 KV heads; projector with max frame length 8 to projection size 10240 with GELU; frame-length conditioning enabled (`use_frame_len_embedding: true`); semantic VAD heads in `semantic_vad_heads.safetensors` with 8 classes and horizons 0.5 / 1.0 / 2.0 / 3.0 s; vocabulary size 151936; dtype bfloat16; weights 8.17 GB `model.safetensors` plus `semantic_vad_heads.safetensors` (**Reported**).[^audio8-infinite-card]

## Evaluation

- Greedy decode with EOS suppressed at the 80 ms audio clock with `target_delay_ms = 480` (6 delay tokens); error rates in percent; source states no repetition loops and no dropped trailing words (**Reported**):[^audio8-infinite-card]

| test set | metric | Audio8 ASR Infinite | Voxtral-Mini-4B-Realtime-2602 | nemotron-3.5-asr-streaming-0.6b |
| --- | --- | --- | --- | --- |
| aishell1/test | CER | **1.750** | 16.795 | 12.927@560ms |
| aishell4/test | CER | **2.893** | 16.456 | 14.677@560ms |
| librispeech test.clean | WER | 3.042 | **2.210** | 3.353@560ms |
| librispeech test.other | WER | 6.808 | **5.552** | 7.140@560ms |
| **average** | | **3.623** | 10.253 (2 sets) | 9.524 |

- Competitor Nemotron figures in the table are marked `@560ms`, differing from the 480 ms setting used for Audio8 ASR Infinite (**Reported**).[^audio8-infinite-card]

## Deployment and usage

- Only a full merged weight directory is supported as-is; adapter-style or partially converted weights are not (**Reported**).[^audio8-infinite-card]
- Programmatic simulated-streaming decode uses remote code with `trust_remote_code=True`: `AutoTokenizer` and `AutoFeatureExtractor` from the checkpoint, `Audio8ASRInfiniteForConditionalGeneration` in bfloat16 on CUDA, duck-typed audio config with `raw_audio_samples_per_token = 1280` (80 ms at 16 kHz), `streaming_n_left_pad_tokens = 18`, `sampling_rate = 16000`, plus `simulated_streaming_greedy_decode_batch` with language token, streaming special-token IDs, `num_delay_tokens = 480 // 80`, `right_pad_text_tokens = 10`, and `max_new_tokens = 512` (**Reported**).[^audio8-infinite-card]
- Torch simulated-streaming CLI form is `python -m audio8_asr_infinite.examples.torch_streaming_decode --checkpoint /path/to/checkpoint --audio sample.wav --language zh --transcription-delay-ms 480` (**Reported**).[^audio8-infinite-card]
- Canonical 24/7 deployment is Docker Compose, which also serves the web demo: `cd docker` then `AUDIO8_MODEL_DIR=/path/to/checkpoint docker compose up -d`; web client at `http://localhost:8080/` (plain HTTP) and `https://localhost:8443/` (TLS proxy with self-signed certificate); terminal client `python -m audio8_asr_infinite.examples.vllm_realtime_client --ws-url ws://127.0.0.1:18191/v1/realtime --audio sample.wav --language zh --target-delay-ms 480 --pace`; host port `18191` maps to service port `18190` inside the compose network (**Reported**).[^audio8-infinite-card]
- The rolling KV window is 30 s with exact RoPE re-basing, which is what keeps memory and latency bounded over 24/7 operation (**Reported**).[^audio8-infinite-card]

## Roadmap and limitations

- Current card is the preview release delivering the transcription base; realtime semantic perception on the same frame grid and acoustic forward pass is in progress as the formal release (**Reported**).[^audio8-infinite-card]
- Operation outside the post-trained clock and delay combinations is possible but performance may not be optimum (**Reported**).[^audio8-infinite-card]

## Relationships

- Name-similar but distinct model: [Audio8-ASR-0.1B](audio8-asr-0.1b.md) is the compact 0.1B-LM short-form multilingual model from `AutoArk-AI` with hotword boosting and ONNX/iOS edge packaging, while this concept covers the `Edge0` native streaming bilingual model with selectable clock, transcription delay, rolling KV cache, and semantic VAD (**Synthesis**).[^audio8-infinite-card]
- Related streaming ASR reference: [ARK-ASR-3B](ark-asr-3b.md) is a larger 3B-scale multilingual short-form ASR model, useful as a non-streaming accuracy reference against this streaming-first design (**Synthesis**).[^audio8-infinite-card]
- Evaluated against [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md): that concept covers the NVIDIA 0.6B cache-aware multilingual streaming baseline whose 560 ms figures appear in this concept's Aishell/LibriSpeech table; read both when contrasting bilingual native-streaming with fixed clock and delay (Audio8) against multilingual chunked streaming with inference-time chunk selection (Nemotron) (**Synthesis**).[^audio8-infinite-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio transcribed, and no CER/WER, latency, memory-constancy, or 24/7-stability figures reproduced (**Synthesis**).[^audio8-infinite-card]
- Demo video asset, Hugging Face checkpoint files, GitHub repository, Docker Compose stack, vLLM build, and evaluation datasets were linked but not fetched and were not present in `raw/`; only `raw/Audio8-ASR-Infinite.md` was inspected (**Synthesis**).[^audio8-infinite-card]
- All accuracy, latency, architecture, usage, and deployment claims are source assertions without independent verification in this wiki (**Synthesis**).[^audio8-infinite-card]

[^audio8-infinite-card]: [Audio8 ASR Infinite model card](../raw/Audio8-ASR-Infinite.md) — locators: frontmatter (`license`, `language`, `library_name`, `pipeline_tag`, `tags`); header badges (Hugging Face `Edge0/Audio8-ASR-Infinite`, GitHub `Edge0-AI/Audio8-ASR-Infinite`, license); intro paragraph (streaming clock 80/120/160 ms, delay 240–560 ms, adapted vLLM 24/7); section `Highlights` (12.5/s, rolling KV cache, one token per clock step, delay tradeoff, semantic VAD, bilingual); section `See Audio8-ASR-Infinite in action` (30 s native context, demo video); section `Optimized operation points` (clock/frame_len/pad/delay table, integer-multiple rule); section `Architecture` (Voxtral + DSM lineage table, 5 component rows); `Checkpoint specification` table (tower, decoder, projector, frame-length conditioning, VAD heads, vocab, dtype, 8.17 GB weights); section `Roadmap` (preview vs formal release table); section `Evaluation` (480 ms / 80 ms greedy table with AIShell and LibriSpeech rows, EOS-suppressed note); section `Usage` (simulated-streaming Python fence, merged-weights-only note); section `24/7 inference with vLLM` (compose commands, ports 8080/8443/18191/18190, realtime client command, 30 s RoPE re-basing); section `Torch inference` (torch_streaming_decode command).
