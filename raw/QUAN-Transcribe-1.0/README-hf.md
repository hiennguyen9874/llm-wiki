---
language: vi
license: gemma
base_model: google/embeddinggemma-2
pipeline_tag: automatic-speech-recognition
tags: [ctc, vietnamese, streaming, embeddinggemma]
---

# QUAN-Transcribe-1.0

SOTA Fast Vietnamese speech recognition, offline and streaming, built on top of Google's
[EmbeddingGemma 2](https://huggingface.co/google/embeddinggemma-2).

- **Trained in ~3 hours on 8×H100.**
- **~3,700× faster than real time on a single H100**: one forward pass, no autoregressive decoder.
- **Streaming support**: the same weights decode with full context or in streaming mode (0.48 s chunks).
- **Inference code**: [github.com/qnguyen3/QUAN-Transcribe](https://github.com/qnguyen3/QUAN-Transcribe)

## Quick start

```bash
pip install git+https://github.com/qnguyen3/QUAN-Transcribe
quan-transcribe audio.wav
```

```python
from quan_transcribe import QuanTranscribe

asr = QuanTranscribe.from_pretrained("qnguyen3/QUAN-Transcribe-1.0")
print(asr.transcribe("audio.wav"))
print(asr.transcribe("audio.wav", streaming=True))
```

The base encoder `google/embeddinggemma-2` is downloaded on first use; accept its terms on the model page first.
Output is lowercase Vietnamese without punctuation, with numbers written as words.

## Model

The EmbeddingGemma 2 audio encoder (USM-style conformer, top 2 of 12 layers fine-tuned) feeds a learned mix of its
layer outputs into a 6-layer transformer reader (d=768) trained with CTC. Output units are 14,917 Gemma tokenizer
tokens, about one per Vietnamese syllable. The reader was trained with dynamic chunk sizes, so it can run in streaming
mode on top of the encoder's own chunked attention.

Training data: ~2,800 h of Vietnamese speech (Bud500, viVoice, VLSP2020, FPT FOSD, InfoRe 1/2, LSVSC, ViMD,
Common Voice 17, FLEURS, PhoAudiobook), including utterances with numbers spelled out in words.

## Benchmark

Word error rate on Vietnamese test sets. Every model was run on the same utterances, with the same text
normalization and scoring, greedy decoding, one H100 per model (bf16/fp16). Speed is audio duration divided by
wall-clock time from waveform to text.

| Model | Params | **Avg** | Speed (×RT) | bud500 | cv17 | fleurs | gigaspeech2 | lsvsc | phoaudiobook | vimd | VIVOS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **QUAN-Transcribe-1.0** | **356M** | **6.87%** | **3,713** | **1.62%** | 10.19% | 6.75% | 12.34% | **5.48%** | 1.35% | **9.05%** | 8.15% |
| Gemini-Flash-3.8 | N/A | 6.92% | N/A | 1.80% | 10.30% | 5.90% | 10.70% | 5.70% | 1.60% | 10.00% | 9.36% |
| MAI-Transcribe-2.0 | N/A | 6.96% | N/A | 2.45% | 10.15% | 5.80% | 10.15% | 6.00% | 1.40% | 10.25% | 9.48% |
| Cohere Transcribe 03-2026 | 2,066M | 7.01% | 430 | 3.93% | 11.09% | 5.64% | 10.27% | 6.98% | 1.74% | 10.34% | 6.07% |
| Qwen3-ASR-1.7B | 2,038M | 7.01% | 224 | 5.20% | 11.31% | **4.88%** | **8.47%** | 6.60% | 1.85% | 10.54% | 7.25% |
| ElevenLabs Scribe v2 | N/A | 7.08% | N/A | 3.15% | 10.50% | 5.60% | 10.50% | 6.25% | 1.45% | 10.05% | 9.14% |
| PhoWhisper-large | 1,543M | 7.21% | 197 | 9.51% | **9.12%** | 5.31% | 10.14% | 6.81% | **0.87%** | 11.38% | **4.52%** |
| PhoWhisper-medium | 764M | 7.74% | 261 | 10.36% | 9.39% | 6.40% | 10.71% | 7.01% | 1.84% | 11.38% | 4.87% |
| PhoWhisper-small | 242M | 9.32% | 429 | 10.35% | 11.99% | 8.14% | 13.16% | 7.93% | 2.85% | 13.91% | 6.20% |
| Qwen3-ASR-0.6B | 782M | 9.81% | 231 | 6.53% | 17.41% | 7.69% | 12.09% | 7.86% | 3.31% | 13.48% | 10.14% |
| PhoWhisper-base | 73M | 13.52% | 539 | 19.23% | 17.47% | 11.13% | 19.03% | 9.52% | 5.34% | 18.06% | 8.37% |
| PhoWhisper-tiny | 38M | 14.92% | 525 | 11.67% | 19.84% | 17.46% | 21.40% | 10.23% | 6.37% | 22.09% | 10.35% |
| Whisper large-v2 | 1,543M | 15.63% | 180 | 32.71% | 19.35% | 10.75% | 19.70% | 11.07% | 3.06% | 17.29% | 11.09% |
| Whisper large-v3-turbo | 809M | 17.66% | 417 | 59.56% | 17.61% | 7.95% | 15.76% | 12.67% | 2.30% | 16.14% | 9.31% |
| Whisper large-v3 | 1,543M | 18.04% | 193 | 64.03% | 18.43% | 7.09% | 14.19% | 13.96% | 1.85% | 15.56% | 9.18% |
| Whisper small | 242M | 28.81% | 308 | 65.50% | 31.08% | 20.59% | 27.44% | 20.21% | 11.21% | 30.66% | 23.80% |
| Whisper medium | 764M | 30.12% | 188 | 125.56% | 26.06% | 11.98% | 23.40% | 15.13% | 5.83% | 19.91% | 13.07% |

## License

This model is a derivative of EmbeddingGemma 2 and is subject to the
[Gemma Terms of Use](https://ai.google.dev/gemma/terms).
