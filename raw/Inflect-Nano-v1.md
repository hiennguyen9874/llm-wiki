---
license: apache-2.0
language:
- en
tags:
- text-to-speech
- tts
- speech-synthesis
- pytorch
- ultra-small
- local-tts
- efficient-inference
- experimental
pipeline_tag: text-to-speech
library_name: pytorch
---

<p align="center">
  <img src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/assets/inflect-nano-banner.png" alt="Inflect-Nano banner" width="100%">
</p>

# Inflect-Nano-v1

**Inflect-Nano-v1 is a tiny English text-to-speech model with 4.63M total inference parameters, including its vocoder.**

It is not trying to beat large TTS models. It is a small, local, complete text-to-waveform stack built to test how far ultra-lightweight speech synthesis can go.

## Highlights

- **4.63M parameters total**
- **Includes the vocoder**
- **24 kHz audio**
- **Single English male voice**
- **Runs locally with PyTorch**
- Built for tiny-model experiments, local assistants, embedded demos, and efficient inference research

## Listen

| Text | Audio |
|---|---|
| "Did the timing change?" she answered. "Then why did Logan leave?" | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_01.wav"></audio> |
| Who puts a parking meter next to an ER label? | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_02.wav"></audio> |
| Please say neighborhood, statistics, and anesthesiologist clearly, without rushing through the middle syllables. | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_03.wav"></audio> |
| I said 91, not 306, which is a very different number. | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_04.wav"></audio> |
| The inference path looked natural, but the decoder still needed a smoother transition before Marcus approved the final test. | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_05.wav"></audio> |
| The appointment moved to 1:25, the invoice was $674.96, and the archive was labeled 1998. | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_06.wav"></audio> |
| If Logan sounded uneasy, then it happened near Long Beach, and the pause has to carry that. | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_07.wav"></audio> |
| The word aluminum should not steal attention from the softer ending after entrepreneur. | <audio controls preload="none" src="https://huggingface.co/owensong/Inflect-Nano-v1/resolve/main/examples/example_08.wav"></audio> |

## Install

```bash
git clone https://huggingface.co/owensong/Inflect-Nano-v1
cd Inflect-Nano-v1
pip install -r requirements.txt
```

## Generate Speech

```bash
python inference.py --text "Wait, are you actually being for real now?" --out sample.wav
```

CPU:

```bash
python inference.py --device cpu --text "Please say neighborhood clearly." --out sample_cpu.wav
```

With simple controls:

```bash
python inference.py \
  --text "The appointment moved to 1:25." \
  --length-scale 1.03 \
  --pitch-scale 1.00 \
  --energy-scale 1.00 \
  --out sample_controlled.wav
```

Local Gradio demo:

```bash
python app.py
```

## Model Size

| Part | Parameters |
|---|---:|
| Acoustic model | **3.465M** |
| Vocoder generator | **1.167M** |
| Total inference stack | **4.632M** |

The model files are:

```text
weights/inflect_nano_v1_acoustic.pt
weights/inflect_nano_v1_vocoder.pt
```

## Repo Layout

```text
weights/                         model weights
examples/                        audio examples
assets/                          README banner
inflect_nano/                    runtime model code
third_party/tiny_tts_frontend/   vendored text frontend used for English G2P/token IDs
inference.py                     simple CLI inference
app.py                           local Gradio demo
```

The model itself is in `weights/`. The vendored frontend is included only so the released model can reproduce the same text normalization and tokenization path.

## What Makes It Different

Many small TTS projects depend on a separate larger vocoder. Inflect-Nano-v1 includes the vocoder in the published inference stack, so the full text-to-waveform path stays under 5M parameters.

Pipeline:

```text
text
-> English text frontend
-> compact FastSpeech-style acoustic model
-> 80-bin mel spectrogram
-> small Snake HiFi-GAN-style vocoder
-> 24 kHz waveform
```

## Architecture

The acoustic model is a compact non-autoregressive FastSpeech-style network. It predicts duration, pitch, energy, and brightness, then decodes an 80-bin mel spectrogram.

The vocoder is a small Snake-activation HiFi-GAN-style generator trained for 24 kHz waveform reconstruction.

Main settings:

| Setting | Value |
|---|---:|
| Sample rate | 24 kHz |
| Mel bins | 80 |
| Acoustic hidden size | 168 |
| Encoder layers | 5 |
| Decoder layers | 6 |
| Vocoder upsample rates | 8, 8, 2, 2 |

## Good For

- Tiny local TTS experiments
- Offline assistant prototypes
- Efficient inference research
- Embedded speech demos
- Browser/WASM-style exploration
- A baseline for sub-5M TTS work

## Not Good For

- Production narration
- Accessibility-critical output
- Voice cloning
- Multilingual speech
- High-fidelity audiobook generation
- Matching large modern TTS systems

## Limitations

This is a very small experimental model. It can sound robotic, buzzy, or unstable, especially on difficult unseen text. Long prompts and unusual phrasing are less reliable. The vocoder is also a clear quality bottleneck.

Use it as a tiny-model research/demo release, not as a production TTS engine.

## License

Apache-2.0.

This repository includes a small third-party English text frontend for tokenization/G2P compatibility. Its license is included at `third_party/tiny_tts_frontend/LICENSE`.
