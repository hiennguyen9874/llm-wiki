---
library_name: transformers
pipeline_tag: automatic-speech-recognition
tags:
- automatic-speech-recognition
- ctc
- conformer
- custom_code
language: en
datasets:
- librispeech_asr
license: apache-2.0
---

# AuroraASR-1M

A tiny weight-shared Conformer-CTC speech recognizer under 1M parameters. Four unique Conformer-lite blocks are each applied twice, followed by a CTC head over a 256-piece BPE vocabulary. Trained on the full LibriSpeech dataset for 379 epochs, English only, 16 kHz mono input, greedy CTC decoding, no external language model is required.

## Word error rate (LibriSpeech, greedy decoding)

WER (%) on the standard LibriSpeech test sets, all with greedy decoding and no external language model. Competitor figures are taken from each model's published card or paper.

| Model | Params | test-clean | test-other |
|---|---|---|---|
| **AuroraASR-1M** | **950K** | **11.43** | **26.50** |
| [Femto-ASR](https://huggingface.co/igorktech/femto-asr) | 2.39M | 10.95 | 25.36 |
| [Citrinet-256 CTC](https://huggingface.co/nvidia/stt_en_citrinet_256_ls) | 10M | 3.8 | 9.8 |
| [Moonshine Tiny](https://huggingface.co/UsefulSensors/moonshine-tiny) | 27M | 4.58 | n/a |
| [Whisper Tiny (English only)](https://huggingface.co/openai/whisper-tiny.en) | 39M | 5.6 | 14.6 |
| [Whisper Tiny (multilingual)](https://huggingface.co/openai/whisper-tiny) | 39M | 7.6 | 16.9 |

**Quantization:** WER is nearly lossless across precisions, all the way down to INT8 weight-only. The figures above are for FP32.

## Speed (FP32, full end-to-end pipeline)

Real-time factor (RTF) = processing time / audio duration (lower is better, 1.0 = real time). Batch size 1, 100 test-clean utterances (13.3 min of audio). End-to-end includes log-mel feature extraction and CTC decoding.

| Device | RTF (end-to-end) | x real-time |
|---|---|---|
| GPU (NVIDIA RTX PRO 6000 Blackwell Server Edition) | 0.0007 | 1362x |
| CPU (1 vCPU, single thread pinned to one core) | 0.0023 | 436x |

## Usage

This model uses custom code, so `trust_remote_code=True` is required.

```python
import soundfile as sf
from transformers import AutoModelForCTC, AutoFeatureExtractor

repo = "AuroraAI-Research/AuroraASR-1M"
model = AutoModelForCTC.from_pretrained(repo, trust_remote_code=True).eval() # FP32
# model = AutoModelForCTC.from_pretrained(repo, subfolder="int8", trust_remote_code=True).eval() # INT8
# model = AutoModelForCTC.from_pretrained(repo, subfolder="fp16", trust_remote_code=True).half().cuda().eval() # FP16
fe = AutoFeatureExtractor.from_pretrained(repo, trust_remote_code=True)

wav, sr = sf.read("audio.wav", dtype="float32")
print(model.transcribe(wav)[0])
```

Requires `torch`, `transformers`, `sentencepiece`.

## Precisions

- **FP32** (repo root, 3.81 MB): reference weights.
- **FP16** (`subfolder="fp16"`, 1.91 MB): half-precision weights.
- **INT8** (`subfolder="int8"`, 1.06 MB): Linear weights stored as int8 with per-output-channel scales and
  dequantised on the fly. Smaller download and memory, runs on CPU and GPU without special runtimes.
  It does not make the arithmetic faster.

## Training methodology

### Data
- **Training set:** LibriSpeech 960 h (`train-clean-100`, `train-clean-360`, `train-other-500`). No other audio or text data was used.
- **Filtering:** utterances shorter than 1 s or longer than 16 s were dropped, as were utterances whose token count exceeded one quarter of their feature frames.
- **Model selection:** `dev-clean` was used for per-epoch monitoring and checkpoint selection. `test-clean` and `test-other` were only used for the final evaluation.

### Text and tokenization
- Transcripts are lowercased and restricted to a-z, apostrophe and space. The model outputs no punctuation or casing.
- A 256-piece SentencePiece BPE tokenizer was trained on the training transcripts only. The CTC output layer has 257 classes (256 pieces + blank).

### Features
- 80-bin log-mel spectrogram (16 kHz, 25 ms window, 10 ms hop, 512-point FFT, 20 Hz to 8 kHz).
- Per-utterance mean/variance normalization of each mel bin.

### Architecture
- 4x time-subsampling convolutional stem, then 4 unique Conformer-lite blocks, each applied twice with separate LayerNorms per pass (weight sharing).
- Width 128, 4 attention heads (rotary position embeddings), feed-forward dim 384, depthwise conv kernel 15.
- 949,073 parameters in total.

### Objective
- CTC loss on the final layer (weight 0.7) plus an auxiliary intermediate CTC loss after the second unique block (weight 0.3). The auxiliary head reuses the final LayerNorm and output layer, so it adds no parameters and is discarded at inference.
- Loss is normalized by the number of target tokens.

### Optimization

| Setting | Value |
|---|---|
| Optimizers | Muon for 2-D weight matrices in the encoder blocks and stem projection; AdamW for everything else |
| Muon | lr 0.03, momentum 0.95 (Nesterov), 5 Newton-Schulz steps, weight decay 0.01 |
| AdamW | lr 5e-3, betas (0.9, 0.98), weight decay 0.01 on matrices (none on biases, norms, depthwise convs) |
| LR schedule | 100-step linear warmup, then cosine decay to 5% of peak |
| Gradient clipping | global norm 5.0 |
| Batching | dynamic, 2,400 s of audio per batch, length-bucketed with random jitter, padded to multiples of 64 frames |
| Curriculum | first epoch sorted by length (SortaGrad), random order afterwards |
| Precision | bfloat16 autocast, TF32 matmuls, `torch.compile` |
| Weight averaging | EMA of weights (decay 0.9995, with warmup); all reported results use the EMA weights |
| Regularization | SpecAugment from epoch 3 (2 frequency masks up to 8 bins, 3 time masks up to 4% of the utterance each); dropout 0.0 |
| Seed | 0 |

The schedule was time-budgeted: after a 200-step calibration, the total number of steps was fixed from the measured step time so the cosine decay completes within the budget. Training ran for 379 epochs (about 10 hours) on an RTX Pro 6000.

### Evaluation protocol
- Greedy CTC decoding (collapse repeats, remove blanks), no language model.
- WER is computed on normalized text (lowercase, no punctuation) with a standard word-level edit distance. Figures from models that report on differently normalized text are therefore not strictly comparable.
- No speed perturbation, noise augmentation or external data were used.