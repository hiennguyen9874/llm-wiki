---
license: cc-by-4.0
base_model: nvidia/parakeet-tdt-0.6b-v3
base_model_relation: quantized
language:
- en
library_name: mlx
pipeline_tag: automatic-speech-recognition
tags:
- mlx
- apple-silicon
- speech-to-text
- asr
- stt
- low-bit
- quantization-aware-training
- on-device
metrics:
- wer
---

# Phonon-2

Phonon-2 is the most accurate open speech recognition model for English under 900 MB. Across the Open ASR Leaderboard's
seven English sets it averages 5.21 % word error, beating models multiple times its size in raw bytes.
Set for set it holds the accuracy of its 2.5 GB full-precision teacher, reaching 100.8 % of the teacher's word accuracy on
parliamentary speech and beating it on meetings, from a download 15 times smaller. Its encoder holds each weight at one of
five learned levels in about 2.1 bits.

It transcribes an hour of audio in about 20 seconds on an M5 MacBook Air (174x realtime), at 143x on eight Zen 5 cores
(16 vCPU) and at 6,680x on one H100 in batches of 128.

## Benchmarks

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| **Phonon-2** | **164 MB** | 1.72 | 3.92 | 9.37 | 6.96 | 8.35 | 3.70 | **2.46** | 5.21 |
| Parakeet TDT 0.6B v3, teacher† | 2,508 MB | **1.52** | **3.13** | 9.42 | **5.85** | **7.99** | 3.63 | 3.19 | **4.96** |
| Parakeet Redux | 178 MB | 1.94 | 4.35 | **9.16** | 7.90 | 8.62 | 4.01 | 3.87 | 5.69 |
| Phonon-1 | 415 MB | 2.11 | 5.03 | 10.31 | 12.34 | 8.73 | 3.67 | 3.73 | 6.56 |
| Canary 180M Flash† | 737 MB | **1.52** | 3.42 | 12.09 | 8.33 | 8.87 | **2.04** | 3.57 | 5.69 |
| Voxtral Mini 4B Realtime† | ≈8,000 MB* | 1.62 | 4.94 | 13.34 | 9.31 | 8.80 | 2.23 | 2.60 | 6.12 |
| Whisper large-v3-turbo† | 1,618 MB | 2.13 | 3.71 | 13.88 | 8.09 | 8.47 | 2.79 | 7.02 | 6.58 |
| Nemotron 3.5 ASR Streaming 0.6B† | 2,368 MB | 2.83 | 6.79 | 13.43 | 15.30 | 9.86 | 3.27 | 4.24 | 7.96 |

† Open ASR Leaderboard's published row; the other rows use its code on the full test sets. * Size from the parameter count at 16 bits.

## Run it

Phonon-2 is the model inside [Detta](https://www.fermionresearch.com/products/detta), the dictation app for the Mac.

On Apple silicon, from the command line:

```bash
pip install fermion-research
pip install mlx mlx-audio mlx-lm soundfile scipy zstandard
phonon transcribe recording.wav
fermion transcribe phonon-2 recording.wav
```

`--json` adds a start and end time for every word. The command line and the server are documented at [fermionresearch.com/docs/speech](https://www.fermionresearch.com/docs/speech/).

The same package runs on Linux (x86-64 and Arm) and Windows CPUs; the engines are at [github.com/fermionresearch/phonon](https://github.com/fermionresearch/phonon). With Docker,
on a CPU or a GPU:

```bash
docker run --rm -v "$PWD":/audio -v phonon-cache:/home/phonon/.cache ghcr.io/fermionresearch/phonon-cpu:2.0.6 transcribe phonon-2 /audio/recording.wav
docker run --rm --gpus all -v "$PWD":/audio -v phonon-cache:/home/phonon/.cache ghcr.io/fermionresearch/phonon-cuda:1.0.5 transcribe phonon-2 /audio/recording.wav
```

## Notes

Based on parakeet-tdt-0.6b-v3 by NVIDIA; the tokenizer and output conventions (punctuation, casing, numerals) are the
original's. Licence CC-BY-4.0, same as the original; `NOTICE` lists the changes. The [command line](https://pypi.org/project/fermion-research/) and this
repository's code are Apache 2.0.
