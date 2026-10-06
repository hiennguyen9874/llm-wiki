---
license: apache-2.0
pipeline_tag: audio-to-audio
tags:
- audio
- tts
- speech
- codec
---
---

# Qwen3-TTS-Tokenizer-12Hz

This repository contains the **Qwen3-TTS-Tokenizer-12Hz**, as presented in the paper [Qwen3-TTS Technical Report](https://huggingface.co/papers/2601.15621).

Qwen3-TTS-Tokenizer-12Hz achieves extreme bitrate reduction and ultra-low-latency streaming, enabling immediate first-packet emission through its 12.5 Hz, 16-layer multi-codebook design and a lightweight causal ConvNet.

* **Paper:** [Qwen3-TTS Technical Report](https://huggingface.co/papers/2601.15621)
* **GitHub Repository:** [QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)
* **Demo:** [Hugging Face Space](https://huggingface.co/spaces/Qwen/Qwen3-TTS)

## Quickstart

### Environment Setup

Install the `qwen-tts` Python package from PyPI:

```bash
pip install -U qwen-tts
```

### Tokenizer Encode and Decode

You can encode audio into discrete tokens for storage or transport and decode them back into speech using the snippet below:

```python
import soundfile as sf
from qwen_tts import Qwen3TTSTokenizer

tokenizer = Qwen3TTSTokenizer.from_pretrained(
    "Qwen/Qwen3-TTS-Tokenizer-12Hz",
    device_map="cuda:0",
)

# Encode audio from a URL (or local path)
enc = tokenizer.encode("https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/tokenizer_demo_1.wav")

# Decode codes back into waveforms
wavs, sr = tokenizer.decode(enc)
sf.write("decode_output.wav", wavs[0], sr)
```

## Overview
### Introduction

<p align="center">
    <img src="https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/qwen3_tts_introduction.png" width="90%"/>
<p>

Qwen3-TTS covers 10 major languages (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, and Italian) as well as multiple dialectal voice profiles. Key features:

* **Powerful Speech Representation**: Powered by the self-developed Qwen3-TTS-Tokenizer-12Hz, it achieves efficient acoustic compression and high-dimensional semantic modeling of speech signals. It fully preserves paralinguistic information and acoustic environmental features.
* **Extreme Low-Latency Streaming Generation**: Based on the innovative Dual-Track hybrid streaming generation architecture, it can output the first audio packet immediately after a single character is input, with end-to-end synthesis latency as low as 97ms.

### Model Architecture

<p align="center">
    <img src="https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/overview.png" width="80%"/>
<p>

### Released Tokenizers

| Tokenizer Name | Description |
|----------------|-------------|
| **Qwen3-TTS-Tokenizer-12Hz** | The Qwen3-TTS-Tokenizer-12Hz model which can encode the input speech into codes and decode them back into speech. |

## Evaluation

For detailed evaluation results on speech generation consistency, speaker similarity, and tokenizer benchmarks (ASR tasks, PESQ, STOI, UTMOS), please refer to the [technical report](https://huggingface.co/papers/2601.15621) or the [GitHub repository](https://github.com/QwenLM/Qwen3-TTS).

## Citation

```bibtex
@article{Qwen3-TTS,
  title={Qwen3-TTS Technical Report},
  author={Hangrui Hu and Xinfa Zhu and Ting He and Dake Guo and Bin Zhang and Xiong Wang and Zhifang Guo and Ziyue Jiang and Hongkun Hao and Zishan Guo and Xinyu Zhang and Pei Zhang and Baosong Yang and Jin Xu and Jingren Zhou and Junyang Lin},
  journal={arXiv preprint arXiv:2601.15621},
  year={2026}
}
```