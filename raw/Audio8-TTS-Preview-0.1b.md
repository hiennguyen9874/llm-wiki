---
license: other
license_name: audio8-community-license-v1.0
license_link: https://huggingface.co/Audio8/Audio8-TTS-Preview-0.1b/blob/main/LICENSE
language:
  - zh
  - en
  - de
  - es
  - fr
  - it
  - ja
  - ko
library_name: transformers
pipeline_tag: text-to-speech
tags:
  - audio
  - text-to-speech
  - tts
  - voice-cloning
  - zero-shot
  - multilingual
---

<div align="center">

<img src="./20260729-124515.jpeg" alt="Audio8" width="760">

<h1>Audio8 TTS Preview 0.1B</h1>

**The smallest zero-shot TTS worth running.**

[![GitHub](https://img.shields.io/badge/GitHub-Audio8__TTS-black?style=for-the-badge&logo=github)](https://github.com/Audio8-AI/Audio8_TTS)
[![Demo-0.1B Audio Samples](https://img.shields.io/badge/Demo--0.1B-Audio%20Samples-brightgreen?style=for-the-badge&logo=githubpages)](https://edge0-ai.github.io/Audio8_TTS/0.1B/) 

</div>

<div align="center">
  <video
    src="https://github.com/user-attachments/assets/d5f2b9a3-a87d-49a3-9df4-a3d1c377531d"
    controls
    playsinline
    preload="metadata"
    width="50%">
  </video>
  <p>
    <em>🎬Teaser video</em>
  </p>
</div>

**Audio8 TTS 0.1B** supports speech generation and zero-shot voice cloning. This
repository contains the complete v4 mixed checkpoint, its neural audio codec,
tokenizer, processor, and Hugging Face remote code.

## Compact Scale

The defining characteristic of this release is its size. The main generative
model is approximately **170M parameters**, while the codec decoder is a
separate approximately **120M-parameter** component. Even counting the codec
decoder, the complete audio generation stack remains much smaller than most
modern multilingual TTS systems.

| Model | Reported main-model scale |
|---|---:|
| **Audio8 TTS Preview 0.1B** | **~0.17B** |
| Audio8 TTS Preview 0.6B | ~0.6B |
| IndexTTS2.5 | ~0.8B |
| CosyVoice3 | ~1.5B |
| VoxCPM2 | ~2.3B |
| Fish S2 Pro | ~4.6B |
| Higgs Audio v2 | ~4.7B |
| MOSS-TTS | ~8.5B |

These figures are approximate reference scales collected from the respective
model reports and are not a strictly matched parameter-count audit. The 0.1B
checkpoint is intended to make zero-shot TTS practical with a much smaller
language/audio model footprint, not to claim identical quality across every
language or benchmark.

## Supported Languages

- Primary: Chinese and English
- Experimental/multilingual evaluation: German, Spanish, French, Italian,
  Japanese, and Korean

## Model Details

The model uses an Audio8 Falcon H1 architecture with slow and fast autoregressive
branches. The slow branch predicts semantic tokens, while the fast branch
predicts codec codebooks conditioned on the slow hidden state.

| Component | Configuration |
|---|---|
| Main model | Approximately 170M parameters, excluding the codec decoder |
| Slow AR | 24 layers, width 512, 8 attention heads, 2 KV heads |
| Fast AR | 4 layers, width 512, 8 attention heads, 2 KV heads |
| Acoustic tokens | 10 codebooks, 4,096 entries per codebook |
| Codec | 44.1 kHz, 2,048 samples per model frame (~21.5 frames/s) |
| Codec decoder | Approximately 120M parameters; bundled in `codec.pth` |
| Context | Up to 2,048 packed text/audio positions |

The codec is included in this repository. No additional codec checkpoint is
required.

## Deployment Options

### CPU deployment: ONNX INT8

[Audio8-TTS-Preview-0.1B-ONNX-INT8](https://huggingface.co/Audio8/audio8-TTS-0.1B-ONNX-INT8)
packages Audio8 TTS for low-resource CPU inference with ONNX Runtime. Slow and
Fast AR use per-token INT8 graphs, while the neural audio codec uses FP16.

| Advantage         | Details                                                            |
| ----------------- | ------------------------------------------------------------------ |
| CPU native        | Runs with ONNX Runtime `CPUExecutionProvider`; no CUDA required    |
| Low memory        | About **0.4 GiB after loading** in the tested Linux x86_64 configuration |
| Small runtime     | No PyTorch or Transformers dependency after model download         |
| Complete workflow | CLI, web and HTTP service, streaming PCM, and voice registration   |

Normal synthesis loads only the Slow AR, Fast AR, and codec decoder sessions.
Voice registration releases those sessions before loading the optional codec
encoder, keeping peak memory controlled.

Get the
[ONNX INT8 model](https://huggingface.co/Audio8/audio8-TTS-0.1B-ONNX-INT8)
and follow the
[CPU ONNX Runtime guide](https://github.com/Audio8-AI/Audio8_TTS/tree/master/onnx_runtime).

## Installation

Python 3.11 or newer and a CUDA-capable GPU are recommended.

```bash
pip install "torch>=2.5.0" "torchaudio>=2.5.0" \
  "transformers>=4.57.0,<5" "soundfile>=0.12" "safetensors>=0.4"
```

## Usage

The model includes custom Transformers code. Load it with
`trust_remote_code=True`.

### Voice cloning

The primary usage of this checkpoint is zero-shot voice cloning. Replace
`reference.wav` and the reference transcript with your own audio and text. The
reference transcript should match the spoken content of the reference audio.

```python
import soundfile as sf
import torch
from transformers import AutoModel, AutoProcessor

model_id = "Audio8/Audio8-TTS-Preview-0.1b"
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if device == "cuda" else torch.float32

processor = AutoProcessor.from_pretrained(
    model_id,
    trust_remote_code=True,
)
model = AutoModel.from_pretrained(
    model_id,
    trust_remote_code=True,
    dtype=dtype,
).eval().to(device)

inputs = processor(
    text=["这是一个语音合成测试。"],
    reference_audio=["reference.wav"],
    reference_text=["参考音频对应的完整文本。"],
    return_tensors="pt",
)
inputs = {name: value.to(device) for name, value in inputs.items()}

with torch.inference_mode():
    output = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        do_sample=True,
        return_dict_in_generate=True,
    )
    waveforms, waveform_lengths = model.decode_audio(output.codes)

audio = waveforms[0, : int(waveform_lengths[0])].float().cpu().numpy()
sf.write("output.wav", audio, model.config.codec_sample_rate)
```

For synthesis without cloning, omit `reference_audio` and `reference_text`.
For batch inference with audio or pre-encoded reference codes, see the Audio8
TTS training and inference repository.

## Evaluation

Lower WER/CER is better; higher SIM (similarity) is better.

### CV3 error-rate comparison

Lower is better. These comparison values follow the evaluation table published
for Audio8 TTS Preview 0.6B; they are reference comparisons rather than a
strictly matched re-evaluation.

| Model | Parameters | zh | en | ja | ko | de | es | fr | it |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Audio8 TTS Preview 0.1B** | **~0.17B** | 3.619 | 3.307 | 12.322 | 7.653 | 5.292 | 8.548 | 12.349 | 14.480 |
| Audio8 TTS Preview 0.6B | 0.6B | **3.205** | **3.128** | 7.205 | 4.223 | 3.447 | 3.641 | 8.790 | 4.790 |
| Fish S2 Pro | 4.6B | 3.600 | 3.493 | 5.139 | **4.111** | 3.605 | 2.972 | **8.600** | 4.229 |
| Higgs Audio v2 | 4.7B | 3.378 | 3.404 | **4.742** | 4.260 | **3.300** | **2.929** | 9.425 | **3.555** |
| CosyVoice3-1.5B | 1.5B | 3.91 | 4.99 | 7.57 | 5.69 | 6.43 | 4.47 | 11.8 | 10.5 |
| VoxCPM2 | 2.3B | 3.65 | 5.00 | 5.96 | 5.69 | 4.77 | 3.80 | 9.85 | 4.25 |
| IndexTTS2.5 | 0.8B | 4.36 | 5.12 | 5.66 | - | - | 3.75 | - | - |

### Seed-TTS comparison

Similarity values are shown as percentages in this comparison table. Lower
WER/CER is better; higher similarity is better.

| Model | Parameters | EN WER / SIM | ZH CER / SIM |
|---|---:|---:|---:|
| **Audio8 TTS Preview 0.1B** | **~0.17B** | 1.662 / 56.7 | 1.13 / 68.2 |
| Audio8 TTS Preview 0.6B | 0.6B | **1.506** / 63.2 | 0.950 / 73.1 |
| Fish S2 Pro | 4.6B | 1.607 / 64.6 | 1.038 / 73.8 |
| Higgs Audio v2 | 4.7B | 1.524 / 66.4 | **0.806** / 72.1 |
| CosyVoice3-1.5B | 1.5B | 2.22 / 72.0 | 1.12 / 78.1 |
| MOSS-TTS | 8.5B | 1.85 / 73.4 | 1.20 / 78.8 |
| VoxCPM2 | 2.3B | 1.84 / 75.3 | 0.97 / 79.5 |
| IndexTTS2.5 | 0.8B | 3.253 / **82.3** | 1.119 / **80.4** |

The IndexTTS2.5 row uses the Token-Level Concatenation result from the
Seed-TTS-Eval portion of Table 1 in the IndexTTS 2.5 technical report.

Parameter scales are approximate reference values from the respective model
reports (see the Compact Scale section); they are not a strictly matched
parameter-count audit. For reference, MOSS-TTS contains 8,489,841,664
parameters and VoxCPM2's main model contains 2,290,004,544 parameters; the
separate AudioVAE is not included in the parameter comparison.

Fish S2 Pro was reevaluated because its official evaluation uses its own
normalizer. Higgs Audio v2 was evaluated locally because concrete values were
unavailable. All other baseline values were collected from their official
reports through the [VoxCPM repository](https://github.com/OpenBMB/VoxCPM).

Different normalizers and evaluators make cross-project values reference
comparisons rather than a strictly matched ranking. Evaluation coverage does
not expand the Preview checkpoint's supported-language claim beyond the
languages listed above.

## Limitations and Responsible Use

- This is a compact preview checkpoint. Chinese and English are the primary
  target languages; other languages generally show weaker and more variable
  quality.
- Very long, noisy, or incorrectly transcribed reference clips can reduce
  generation stability and speaker similarity.
- Generated speech can be misused for impersonation or misinformation. Obtain
  consent before cloning a voice and disclose synthetic audio where appropriate.
- Evaluate the model for accuracy, safety, and legal compliance before
  deployment.

## License

This model is released under the
[**Audio8 Community License v1.0**](https://huggingface.co/Audio8/Audio8-TTS-Preview-0.1b/blob/main/LICENSE),
a revenue-capped custom license.

- **Non-Commercial Use** (research, personal, educational, evaluation) is free.
- **Commercial Use is free** for entities whose annual revenue (including
  parent companies, subsidiaries, and affiliates) is **less than US$2,000,000**.
- Entities with annual revenue **of US$2,000,000 or more** must obtain a
  separate written commercial license from Audio8 before any Commercial Use.

English text is authoritative; a Chinese translation is provided in the
`LICENSE` file for reference. For commercial licenses, contact the Audio8 team
via [the Audio8 GitHub repository](https://github.com/Audio8-AI/Audio8_TTS) or
an issue on this Hugging Face repository.
