---
license: apache-2.0
language:
  - yue
  - zh
  - nl
  - en
  - fr
  - de
  - it
  - ja
  - ko
  - pl
  - es
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

<h1>&nbsp;&nbsp;Audio8 TTS Preview 0.6B: SOTA-Class TTS at Compact Scale</h1>

**A 0.6B-parameter multilingual text-to-speech model with zero-shot voice cloning.**

[![GitHub](https://img.shields.io/badge/GitHub-Audio8__TTS-black?style=for-the-badge&logo=github)](https://github.com/Audio8-AI/Audio8_TTS)
[![Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=githubpages)](https://audio8-ai.github.io/Audio8_TTS/)
[![ONNX INT4](https://img.shields.io/badge/ONNX-INT4-005CED?style=for-the-badge&logo=onnx)](https://huggingface.co/Audio8/Audio8-TTS-Preview-0.6B-ONNX-INT4)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](https://github.com/Audio8-AI/Audio8_TTS/blob/main/LICENSE)

</div>

Audio8 TTS Preview supports multilingual speech generation and zero-shot voice
cloning. This repository contains the complete checkpoint, its 44.1 kHz neural
audio codec, tokenizer, processor, and Hugging Face remote code.

> **Preview status:** Language coverage is intentionally limited in this
> release. For the best results, use one of the 11 recommended languages below.
> Broader multilingual coverage and Chinese dialect support are planned for
> future releases.

## Supported Languages

<p align="center">
  <strong>Cantonese</strong> &nbsp;·&nbsp;
  <strong>Chinese</strong> &nbsp;·&nbsp;
  <strong>Dutch</strong> &nbsp;·&nbsp;
  <strong>English</strong><br>
  <strong>French</strong> &nbsp;·&nbsp;
  <strong>German</strong> &nbsp;·&nbsp;
  <strong>Italian</strong> &nbsp;·&nbsp;
  <strong>Japanese</strong><br>
  <strong>Korean</strong> &nbsp;·&nbsp;
  <strong>Polish</strong> &nbsp;·&nbsp;
  <strong>Spanish</strong>
</p>

## Model Details

Audio8 TTS uses a DualAR architecture inspired by
[Fish Audio S2 Pro](https://github.com/fishaudio/fish-speech). The slow AR
transformer predicts one semantic token for each audio frame. The fast AR
transformer predicts the frame's codec codebooks, conditioned on the slow hidden
state and preceding codebooks.

| Component | Configuration |
|---|---|
| Main model | 601,159,424 parameters, excluding the codec |
| Slow AR | 24 layers, width 896, 14 attention heads, 2 KV heads |
| Fast AR | 4 layers, width 896, 14 attention heads, 2 KV heads |
| Acoustic tokens | 10 codebooks, 4,096 entries per codebook |
| Codec | 44.1 kHz, 2,048 samples per model frame (~21.5 frames/s) |
| Context | Up to 2,048 packed text/audio positions |

The bundled codec handles both reference-audio encoding and waveform decoding,
so no additional codec checkpoint is required.

## Installation

Python 3.10 or newer and a CUDA-capable GPU are recommended.

```bash
pip install "torch>=2.5.0" "torchaudio>=2.5.0" \
  "transformers>=4.57.0,<5" "soundfile>=0.12" "safetensors>=0.4"
```

## Usage

The model uses custom Transformers code. Review the files in this repository,
then load it with `trust_remote_code=True`.

### Zero-shot voice cloning

The reference transcript must match the spoken content in the reference audio.

```python
import soundfile as sf
import torch
from transformers import AutoModel, AutoProcessor

model_id = "Audio8/Audio8-TTS-Preview-0.6b"
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if device == "cuda" else torch.float32

processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_id,
    trust_remote_code=True,
    dtype=dtype,
).eval().to(device)

inputs = processor(
    text=["Welcome to Audio8 TTS."],
    reference_audio=["reference.wav"],
    reference_text=["The exact transcript of the reference recording."],
    return_tensors="pt",
)
inputs = {name: value.to(device) for name, value in inputs.items()}

with torch.inference_mode():
    output = model.generate(
        **inputs,
        max_new_tokens=1024,
        temperature=0.8,
        top_p=0.95,
        top_k=50,
        do_sample=True,
        return_dict_in_generate=True,
    )
    waveforms, waveform_lengths = model.decode_audio(output.codes)

audio = waveforms[0, : int(waveform_lengths[0])].float().cpu().numpy()
sf.write("output.wav", audio, model.config.codec_sample_rate)
```

### Generation without a reference

Omit `reference_audio` and `reference_text` when a cloned voice is not needed:

```python
inputs = processor(
    text=["This utterance does not use a reference voice."],
    return_tensors="pt",
)
```

For command-line inference, batching, and supervised fine-tuning, see the
[Audio8 TTS repository](https://github.com/Audio8-AI/Audio8_TTS).

## Deployment Options

### CPU deployment: ONNX INT4

[Audio8-TTS-Preview-0.6B-ONNX-INT4](https://huggingface.co/Audio8/Audio8-TTS-Preview-0.6B-ONNX-INT4)
packages Audio8 TTS for low-resource CPU inference with ONNX Runtime. Slow and
Fast AR weights use weight-only INT4, while activations, KV caches, and the
neural audio codec use FP16.

| Advantage | Details |
|---|---|
| CPU native | Runs with ONNX Runtime `CPUExecutionProvider`; no CUDA required |
| Low memory | About **1 GiB after loading** in the tested Apple M2 configuration |
| Small runtime | No PyTorch or Transformers dependency after model download |
| Complete workflow | CLI, web and HTTP service, streaming PCM, and voice registration |

Normal synthesis loads only the Slow AR, Fast AR, and codec decoder sessions.
Voice registration releases those sessions before loading the optional codec
encoder, keeping peak memory controlled.

Get the
[ONNX INT4 model](https://huggingface.co/Audio8/Audio8-TTS-Preview-0.6B-ONNX-INT4)
and follow the
[CPU ONNX Runtime guide](https://github.com/Audio8-AI/Audio8_TTS/tree/master/onnx_runtime).

### High-throughput serving: SGLang Omni

Audio8 TTS now includes an
[SGLang Omni adapter](https://github.com/Audio8-AI/Audio8_TTS/tree/master/sglang_omni)
for production-oriented GPU serving. It is installed as an independent model
plugin and does not overwrite SGLang Omni core files.

| Capability | Support |
|---|---|
| Attention and batching | SGLang paged attention and dynamic batching |
| DualAR execution | Slow AR serving with a fixed KV cache for the Fast AR codebook decoder |
| Voice cloning | Reference-audio encoding and waveform decoding |
| API | OpenAI-compatible `/v1/audio/speech` service |

The released adapter is validated against a pinned SGLang Omni revision and
supports both generation without a reference and zero-shot voice cloning. See
the
[SGLang Omni deployment guide](https://github.com/Audio8-AI/Audio8_TTS/tree/master/sglang_omni)
for tested versions, installation, server configuration, and API examples.

## Evaluation

Audio8 TTS Preview is the smallest model in this comparison at just **0.6B
parameters**. Despite using only a fraction of the parameters of the other
systems, it delivers results in the first tier of industry-leading SOTA TTS
models on the benchmarks below. In particular, it achieves the best English
WER and competitive Chinese CER on Seed-TTS, while remaining competitive
across the CV3 multilingual evaluation.

Lower WER/CER is better; higher SIM is better. Seed-TTS similarity values are
shown as percentages.

### Seed-TTS

| Model | Parameters | EN WER / SIM | ZH CER / SIM | Hard ZH CER / SIM |
|---|---:|---:|---:|---:|
| **Audio8 TTS Preview** | **0.6B** | **1.506** / 63.2 | 0.950 / 73.1 | 11.510 / 68.7 |
| Fish S2 Pro | 4.6B | 1.607 / 64.6 | 1.038 / 73.8 | 10.149 / 70.1 |
| Higgs Audio v2 | 4.7B | 1.524 / 66.4 | **0.806** / 72.1 | 10.622 / 69.3 |
| CosyVoice3-1.5B | 1.5B | 2.22 / 72.0 | 1.12 / 78.1 | **5.83** / **75.8** |
| MOSS-TTS | 8.5B | 1.85 / 73.4 | 1.20 / 78.8 | - |
| VoxCPM2 | 2.3B | 1.84 / **75.3** | 0.97 / **79.5** | 8.13 / 75.3 |

### CV3 multilingual error rate

| Model | Parameters | zh | en | hard-zh | hard-en | ja | ko | de | es | fr | it | ru |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Audio8 TTS Preview** | **0.6B** | **3.205** | **3.128** | 10.535 | 5.997 | 7.205 | 4.223 | 3.447 | 3.641 | 8.790 | 4.790 | - |
| Fish S2 Pro | 4.6B | 3.600 | 3.493 | 10.588 | 7.349 | 5.139 | **4.111** | 3.605 | 2.972 | **8.600** | 4.229 | **4.702** |
| Higgs Audio v2 | 4.7B | 3.378 | 3.404 | 10.424 | **5.754** | **4.742** | 4.260 | **3.300** | **2.929** | 9.425 | **3.555** | 5.423 |
| CosyVoice3-1.5B | 1.5B | 3.91 | 4.99 | 9.77 | 10.55 | 7.57 | 5.69 | 6.43 | 4.47 | 11.8 | 10.5 | 6.64 |
| VoxCPM2 | 2.3B | 3.65 | 5.00 | **8.55** | 8.48 | 5.96 | 5.69 | 4.77 | 3.80 | 9.85 | 4.25 | 5.21 |

Parameter counts are calculated directly from the released weight tensors.
MOSS-TTS contains 8,489,841,664 parameters. VoxCPM2's main model contains
2,290,004,544 parameters; the separate AudioVAE is not included in the
parameter comparison.

Fish S2 Pro was reevaluated because its official evaluation uses its own
normalizer. Higgs Audio v2 was evaluated locally because concrete values were
unavailable. All other baseline values were collected from their official
reports through the [VoxCPM repository](https://github.com/OpenBMB/VoxCPM).

Different normalizers and evaluators make cross-project values reference
comparisons rather than a strictly matched ranking. Evaluation coverage does
not expand the Preview checkpoint's supported-language claim beyond the 11
languages listed above.

## Limitations and Responsible Use

- This is a Preview checkpoint with limited multilingual and dialect coverage.
- Very long, noisy, or incorrectly transcribed reference clips can reduce
  stability and speaker similarity.
- Generated speech can be misused for impersonation or misinformation. Obtain
  consent before cloning a voice and clearly disclose synthetic audio where
  appropriate.
- Evaluate the model for accuracy, safety, and legal compliance before
  deployment.

## License and Acknowledgements

The code and model weights are released under the
[Apache License 2.0](https://github.com/Audio8-AI/Audio8_TTS/blob/main/LICENSE).
See the upstream [NOTICE](https://github.com/Audio8-AI/Audio8_TTS/blob/main/NOTICE)
for attribution details.

We thank the Fish Audio team for publishing the DualAR architecture used in
Fish Audio S2 Pro.
