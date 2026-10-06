---
license: apache-2.0
language:
  - zh
  - en
library_name: transformers
pipeline_tag: automatic-speech-recognition
tags:
  - streaming
  - realtime
  - speech-recognition
  - audio
---

<div align="center">

# Audio8 ASR Infinite

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Audio8--ASR--Infinite-yellow?style=for-the-badge)](https://huggingface.co/Edge0/Audio8-ASR-Infinite)
[![GitHub](https://img.shields.io/badge/GitHub-Audio8--ASR--Infinite-black?style=for-the-badge&logo=github)](https://github.com/Edge0-AI/Audio8-ASR-Infinite)
[![arXiv](https://img.shields.io/badge/arXiv-coming%20soon-b31b1b?style=for-the-badge&logo=arxiv&logoColor=white)](https://github.com/Edge0-AI/Audio8-ASR-Infinite)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](https://github.com/Edge0-AI/Audio8-ASR-Infinite/blob/main/LICENSE)

</div>

**Audio8 ASR Infinite** is a native streaming speech recognition model built to be
as responsive as possible. It offers a selectable audio clock (80/120/160 ms) and
a transcription delay (240–560 ms).
With our adapted vLLM build it transcribes unlimited-length audio **24/7** without drifting.

## Highlights

- **Super responsive** — the native streaming architecture decodes 12.5 times per second.
- **Unlimited-length transcription** — a rolling KV Cache keeps both **memory and
  latency constant**, even in **24/7 operation**.
- **Selectable streaming clock** — one text token per clock step
  (12.5 / 8.3 / 6.25 decisions per second), balancing perception granularity and resource cost.
- **Configurable transcription delay** — set how much delay to trade for accuracy.
- **Semantic VAD** — distinguishes thinking pauses, stuttering and real end of turn, where traditional acoustic VAD usually fails.
- **Bilingual** — Chinese and English.

## See Audio8-ASR-Infinite in action

The checkpoint has a native context of 30 seconds. But with Rolling KV Cache, it can transcribe 24/7 nonstop.

<video controls playsinline width="100%" preload="metadata"
  src="https://huggingface.co/Edge0/Audio8-ASR-Infinite/resolve/main/Audio8-Asr-Infinite-Demo.mp4"></video>

## Optimized operation points

The following combinations of frame length and delay are post-trained. Other combinations can be used but performance may not be optimum.

| audio clock | `frame_len` | `streaming_n_left_pad_tokens` | selectable `target_delay_ms` |
| --- | --- | --- | --- |
| 80 ms | 4 | 18 | 240 / 320 / 480 / 560 |
| 120 ms | 6 | 12 | 240 / 480 |
| 160 ms | 8 | 9 | 320 / 480 |

`target_delay_ms` must be an integer multiple of the selected clock, so longer
delays stay available at every clock even when they are not listed above.

## Architecture

Inherits the Voxtral realtime audio architecture and DSM-style streaming.

| Component | Initial weights | Trained |
| --- | --- | --- |
| Causal Audio Tower | Voxtral Realtime 4B | ✅ |
| Audio Projector  | random initialisation | ✅ |
| Frame Length Embedding | random initialisation | ✅ |
| Decoder | Qwen2.5-3B-Instruct | ✅ |
| LM Head | Qwen2.5-3B-Instruct | ✅ |

Checkpoint specification:

| | |
| --- | --- |
| audio tower | 32 layers, hidden 1280, 128 mel bins, sliding window 750 |
| text decoder | 36 layers, hidden 2048, 16 query heads / 2 KV heads |
| projector | max frame len 8 → projection size 10240, gelu |
| frame-length conditioning | enabled (`use_frame_len_embedding: true`) |
| semantic VAD heads | `semantic_vad_heads.safetensors`, 8 classes, horizons 0.5 / 1.0 / 2.0 / 3.0 s |
| vocab size | 151936 |
| dtype | bfloat16 |
| weights | 8.17 GB `model.safetensors` (+ `semantic_vad_heads.safetensors`) |

## Roadmap

This is the **preview release**: it delivers the transcription base. Realtime
semantic perception is being built on the same frame grid and the same acoustic
forward pass.

| Stage | Status | Scope |
| --- | --- | --- |
| **Preview — ASR base** | ✅ done | Streaming Chinese/English transcription: selectable 80/120/160 ms clock, configurable `target_delay_ms`, unlimited-length rolling KV window |
| **Formal release** | 🏃in progress | Frame-level semantic perception on the same grid, beyond transcription |

## Evaluation

### 480 ms Delay, 80ms frame length

| test set | metric | Audio8 ASR Infinite | Voxtral-Mini-4B-Realtime-2602 | nemotron-3.5-asr-streaming-0.6b |
| --- | --- | --- | --- | --- |
| aishell1/test | CER | **1.750** | 16.795 | 12.927@560ms |
| aishell4/test | CER | **2.893** | 16.456 | 14.677@560ms |
| librispeech test.clean | WER | 3.042 | **2.210** | 3.353@560ms |
| librispeech test.other | WER | 6.808 | **5.552** | 7.140@560ms |
| **average** | | **3.623** | 10.253 (2 sets) | 9.524 |

Greedy decode with EOS suppressed, at the 80 ms audio clock with
`target_delay_ms = 480` (6 delay tokens). Error rates in percent. No repetition
loops and no dropped trailing words.


## Usage

Programmatic simulated-streaming decode with the embedded remote code:

```python
import numpy as np
import torch
from transformers import AutoFeatureExtractor, AutoTokenizer

from audio8_asr_infinite.modeling.modeling_audio8_asr_infinite import (
    Audio8ASRInfiniteForConditionalGeneration,
    resolve_qwen_language_token_id,
    resolve_qwen_streaming_special_token_ids,
)
from audio8_asr_infinite.streaming_inference import simulated_streaming_greedy_decode_batch

checkpoint = "Edge0/Audio8-ASR-Infinite"
tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
feature_extractor = AutoFeatureExtractor.from_pretrained(checkpoint, trust_remote_code=True)
model = Audio8ASRInfiniteForConditionalGeneration.from_pretrained(
    checkpoint, trust_remote_code=True, torch_dtype=torch.bfloat16
).eval().cuda()

class AudioConfig:  # duck-typed: raw_audio_samples_per_token / streaming_n_left_pad_tokens / sampling_rate
    raw_audio_samples_per_token = 1280   # 80 ms @ 16 kHz
    streaming_n_left_pad_tokens = 18
    sampling_rate = 16000

waveform = np.load("sample.npy", allow_pickle=False).astype(np.float32)  # [-1, 1], 16 kHz mono
results = simulated_streaming_greedy_decode_batch(
    model=model,
    tokenizer=tokenizer,
    feature_extractor=feature_extractor,
    waveforms=[waveform],
    language_token_ids=[resolve_qwen_language_token_id(tokenizer, "zh")],
    special_ids=resolve_qwen_streaming_special_token_ids(tokenizer),
    audio_config=AudioConfig(),
    num_delay_tokens=[480 // 80],
    right_pad_text_tokens=10,
    dtype=torch.bfloat16,
    device=next(model.parameters()).device,
    max_new_tokens=512,
)
print(results[0]["final_text"])
```

Only a full merged weight directory is supported (this repository as-is);
adapter-style or partially converted weights are not.

## 24/7 inference with vLLM

Docker compose is the canonical deployment path; it also serves the web demo:

```bash
cd docker
AUDIO8_MODEL_DIR=/path/to/checkpoint docker compose up -d
```

Verify with the web client shipped in the same stack:

```
http://localhost:8080/     # plain HTTP
https://localhost:8443/    # TLS proxy; accept the self-signed certificate
```

The same socket can be driven from a terminal:

```bash
python -m audio8_asr_infinite.examples.vllm_realtime_client \
    --ws-url ws://127.0.0.1:18191/v1/realtime \
    --audio sample.wav --language zh --target-delay-ms 480 --pace
```

`18191` is the host port published by `docker/docker-compose.yml`; the service
itself listens on `18190` inside the compose network. The rolling KV window is
30 s with exact RoPE re-basing, which is what keeps memory and latency bounded
over 24/7 operation.

## Torch inference (simulated streaming decode)

```bash
python -m audio8_asr_infinite.examples.torch_streaming_decode \
    --checkpoint /path/to/checkpoint \
    --audio sample.wav --language zh --transcription-delay-ms 480
```

