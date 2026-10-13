---
license: apache-2.0
language:
- en
- zh
- ja
- ko
- de
- fr
- es
- pt
- ru
- it
tags:
- asr
- speech-recognition
- gguf
- qwen3
base_model: Qwen/Qwen3-ASR-1.7B
pipeline_tag: automatic-speech-recognition
---

# Qwen3-ASR-1.7B — GGUF

GGUF quantizations of [Qwen/Qwen3-ASR-1.7B](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) for use with [CrispASR](https://github.com/CrispStrobe/CrispASR).

Qwen3-ASR-1.7B is a multilingual speech recognition model supporting 30 languages + 22 Chinese dialects, with support for speech, singing voice, and songs with background music. Audio inputs up to 5 minutes.

## Files

| File | Quant | Size | Notes |
|------|-------|------|-------|
| `qwen3-asr-1.7b-q4_k.gguf` | Q4_K | ~1.5 GB | Recommended for most use cases (audio tower kept at Q8_0 — see rebake note) |
| `qwen3-asr-1.7b-q8_0.gguf` | Q8_0 | ~2.5 GB | Higher quality, more memory |
| `qwen3-asr-1.7b-f16.gguf` | F16 | ~4.7 GB | Full precision (needs ~5 GB RAM) |

### 2026-07 rebake — audio tower now Q8_0 (fixes empty / repeated transcripts)

`qwen3-asr-1.7b-q4_k.gguf` was re-baked with the 24-layer **audio encoder kept
at Q8_0** (previously Q4_K like the LLM body; ~0.15 GB larger). The earlier
Q4_K export could emit an **empty transcript** (or, on longer audio, a repeated
phrase) while still reporting success
([CrispASR #240](https://github.com/CrispStrobe/CrispASR/issues/240)) — the same
sub-8-bit encoder drift diagnosed in
[#218](https://github.com/CrispStrobe/CrispASR/issues/218). Encoder-output
cosine vs the F16 reference (jfk): **0.9632 → 0.9989** min, **0.9913 → 0.9998**
mean — i.e. the tower is back to near-lossless and decode no longer degenerates.
The Q8_0 and F16 files were never affected.

## Usage with CrispASR

```bash
# Auto-download and transcribe (Q4_K)
crispasr -m qwen3-1.7b -f audio.wav

# Or specify the model path directly
crispasr -m qwen3-asr-1.7b-q4_k.gguf -f audio.wav --backend qwen3

# With language hint
crispasr -m qwen3-1.7b -f audio.wav -l ja

# Translation mode
crispasr -m qwen3-1.7b -f audio.wav --translate --target-lang en
```

## Performance

On JFK speech sample (11s, English):
- Q4_K: 0.2x realtime on CPU (4 threads)
- Perfect transcription accuracy

## Conversion

Converted from the **non-HF** variant (`Qwen/Qwen3-ASR-1.7B`, not the `-hf` variant):

```bash
python models/convert-qwen3-asr-to-gguf.py \
    --input Qwen/Qwen3-ASR-1.7B \
    --output qwen3-asr-1.7b-f16.gguf
crispasr-quantize qwen3-asr-1.7b-f16.gguf qwen3-asr-1.7b-q4_k.gguf q4_k
```

> **Note:** The converter also supports the `-hf` variant (`Qwen/Qwen3-ASR-1.7B-hf`) which uses a different tensor naming convention. Both produce identical results.

## Architecture

- Audio encoder: 24-layer Whisper-style encoder (d=1024, 16 heads, GELU)
- Projector: 2-layer MLP (1024 → GELU → 2048)
- LLM decoder: 28-layer Qwen3 (d=2048, 16Q/8KV heads, head_dim=128, SwiGLU)
- Vocab: 151,936 tokens (GPT-2 BPE)
- RoPE theta: 1,000,000

## License

Apache 2.0

## Provenance and EU AI Act Art. 53 note

- **Upstream model:** [Qwen/Qwen3-ASR-1.7B](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) — published by `Qwen`.
- **Upstream licence:** `apache-2.0`. This repository redistributes under the same terms; it grants no rights the upstream licence does not.
- **What was done here:** format conversion and/or quantisation only (GGUF). No training, no fine-tuning, no merging, no distillation, no change to architecture, vocabulary or capability. Only the numeric representation of the upstream weights differs.
- **Training data:** documented — where it is documented at all — by the upstream provider; see the upstream model card. No training data was used, added or selected by this repository.
- **Provider status:** under Regulation (EU) 2024/1689 the upstream authors remain the provider of this model. Converting the serialisation format does not make this repository the provider of a new general-purpose AI model, and no such claim is made. Questions about training content, copyright policy or model capability belong upstream.
