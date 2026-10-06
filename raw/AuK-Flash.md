---
license: mit
language:
- zh
- en
pipeline_tag: text-to-speech
tags:
- speech
- text-to-speech
- zero-shot-tts
- voice-cloning
- speech-generation
- speech-editing
- speech-enhancement
- source-separation
- speech-separation
- instruction-guided
- diffusion
- distillation
- few-step-inference
base_model: tencent/AuK
---

<div align="center">

# AuK-Flash: Fast 4-Step Speech Generation and Editing

[![Website](https://img.shields.io/badge/🌐_Website-AuK-1a73e8)](https://auk-project.github.io/)
[![GitHub](https://img.shields.io/badge/GitHub-Code-181717?logo=github)](https://github.com/Tencent-Hunyuan/AuK)
[![Paper](https://img.shields.io/badge/📄_Paper-arXiv-b5212f)](https://arxiv.org/abs/2609.08936)
[![Hugging Face](https://img.shields.io/badge/🤗_Hugging_Face-Demo-ffbd45)](https://huggingface.co/spaces/tencent/AuK)
[![ModelScope](https://img.shields.io/badge/🤖_ModelScope-Demo-624aff)](https://modelscope.cn/studios/Tencent-Hunyuan/AuK)

</div>

## News

- **[2026/09/09]** 🎉 **AuK** is now open-source. Code and model weights are publicly available. Try it on the [🤗 Demo Space](https://huggingface.co/spaces/tencent/AuK) or the [🤖 ModelScope Space](https://modelscope.cn/studios/Tencent-Hunyuan/AuK)!

## Contents

- [News](#news)
- [Introduction](#introduction)
- [Performance](#performance)
- [Model Architecture](#model-architecture)
- [Supported Tasks](#supported-tasks)
- [Download the weights](#download-the-weights)
- [Citation](#citation)
- [License](#license)

## Introduction

**AuK** is a 1.5B foundation model for speech generation and editing. Trained on millions of hours of diverse audio data, AuK supports zero-shot and
instruction-based TTS, content and acoustic editing, paralinguistic editing,
speech enhancement, and source separation through a unified natural-language
instruction interface. AuK has two variants:

| Model | Description | Weight |
| --- | --- | --- |
| AuK | Base model for high-quality generation | 🤗 [Hugging Face](https://huggingface.co/tencent/AuK) · 🤖 [ModelScope](https://modelscope.cn/models/Tencent-Hunyuan/AuK) |
| AuK-Flash | Distilled model for fast 4-step inference | 🤗 [Hugging Face](https://huggingface.co/tencent/AuK-Flash) · 🤖 [ModelScope](https://modelscope.cn/models/Tencent-Hunyuan/AuK-Flash) |

This repository contains the official weights for **AuK-Flash, the distilled variant with fast 4-step inference**.

## Performance

![AuK performance across speech generation, editing, enhancement, and separation benchmarks](assets/performance.png)

## Model Architecture

![Model Architecture](assets/arch.png)

## Supported Tasks

AuK exposes every task through the same natural-language instruction interface. The table below groups the supported tasks by category, with a short description and a link to its section in the [Cookbook](https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md), which provides instruction templates plus CLI and Python examples.

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Task</th>
      <th>Description</th>
      <th>Cookbook</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">Speech Generation</td>
      <td>Zero-shot TTS</td>
      <td>Speak the target text in the voice of the reference audio.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#11-zero-shot-tts">Zero-shot TTS</a></td>
    </tr>
    <tr>
      <td>Instruct TTS</td>
      <td>Generate speech from a voice description alone — no reference audio.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#12-instruct-tts">Instruct TTS</a></td>
    </tr>
    <tr>
      <td rowspan="2">Content Editing</td>
      <td>Speech Content Editing</td>
      <td>Rewrite <em>what is said</em> — replace, insert, or remove text.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#21-speech-content-editing">Speech Content Editing</a></td>
    </tr>
    <tr>
      <td>Lyric Editing</td>
      <td>Rewrite lyrics in a singing recording while preserving the melody and voice.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#22-lyric-editing">Lyric Editing</a></td>
    </tr>
    <tr>
      <td rowspan="3">Acoustic Editing</td>
      <td>Pitch Editing</td>
      <td>Raise or lower the pitch by semitones.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#31-pitch-editing">Pitch Editing</a></td>
    </tr>
    <tr>
      <td>Speed Editing</td>
      <td>Adjust the speaking rate; output length scales with the speed factor.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#32-speed-editing">Speed Editing</a></td>
    </tr>
    <tr>
      <td>Volume Editing</td>
      <td>Raise or lower the volume by decibels.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#33-volume-editing">Volume Editing</a></td>
    </tr>
    <tr>
      <td rowspan="5">Paralinguistic Editing</td>
      <td>Emotion</td>
      <td>Change the emotion while preserving content and voice.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#41-emotion">Emotion</a></td>
    </tr>
    <tr>
      <td>Timbre</td>
      <td>Change the timbre to a description while keeping the content unchanged.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#42-timbre">Timbre</a></td>
    </tr>
    <tr>
      <td>De-accent</td>
      <td>Remove a regional accent while preserving the speaker's voice and content.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#43-de-accent">De-accent</a></td>
    </tr>
    <tr>
      <td>Nonverbal Editing</td>
      <td>Remove or add nonverbal sounds such as breaths, laughs, or coughs.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#44-nonverbal-editing">Nonverbal Editing</a></td>
    </tr>
    <tr>
      <td>Whisper Conversion</td>
      <td>Convert between normal speech and whisper while preserving speaker and content.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#45-whisper-conversion">Whisper Conversion</a></td>
    </tr>
    <tr>
      <td rowspan="4">Enhancement &amp; Separation</td>
      <td>Speech Enhancement</td>
      <td>Denoise, dereverberate, or restore natural, clear speech.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#51-speech-enhancement">Speech Enhancement</a></td>
    </tr>
    <tr>
      <td>Speech Separation</td>
      <td>Keep one speaker by talking order and remove the others.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#52-speech-separation">Speech Separation</a></td>
    </tr>
    <tr>
      <td>Music Separation</td>
      <td>Extract the singing voice from a mix, or keep all human voices.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#53-music-separation">Music Separation</a></td>
    </tr>
    <tr>
      <td>Target Speaker Extraction</td>
      <td>Keep the target speaker identified by <em>what they say</em>.</td>
      <td><a href="https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md#54-target-speaker-extraction">Target Speaker Extraction</a></td>
    </tr>
  </tbody>
</table>

## Download the weights
**🤗 HuggingFace**

```bash
pip install -U "huggingface_hub[cli]"

# AuK-Base
hf download tencent/AuK --local-dir ./ckpts/AuK

# AuK-Flash (4-step distilled) 
hf download tencent/AuK-Flash --local-dir ./ckpts/AuK-Flash

# MLLM Encoder
hf download Qwen/Qwen2.5-Omni-3B  --local-dir ./ckpts/Qwen2.5-Omni-3B
```

**🤖 ModelScope**

```bash
pip install -U modelscope

# AuK-Base
modelscope download --model Tencent-Hunyuan/AuK --local_dir ./ckpts/AuK

# AuK-Flash (4-step distilled)
modelscope download --model Tencent-Hunyuan/AuK-Flash  --local_dir ./ckpts/AuK-Flash

# MLLM Encoder
modelscope download --model Qwen/Qwen2.5-Omni-3B --local_dir ./ckpts/Qwen2.5-Omni-3B
```

The expected directory structure is:

```text
ckpts/
├── AuK/
├── AuK-Flash/          # optional
└── Qwen2.5-Omni-3B/
```

The model checkpoint contains the diffusion transformer and layer-fusion weights. The MLLM encoder and VAE are loaded from separate files at runtime, so missing `text_encoder.*` keys during checkpoint loading are expected.

For installation, inference, Gradio, ComfyUI, and fine-tuning, see the [GitHub README](https://github.com/Tencent-Hunyuan/AuK#quick-start) and [Cookbook](https://github.com/Tencent-Hunyuan/AuK/blob/main/docs/COOKBOOK.md).

## Citation

Research using AuK can cite the following entry:

```bibtex
@misc{ma2026auktechnicalreportopensource,
  title={AuK Technical Report: An Open-Source Foundational Model for Speech Generation and Editing},
  author={Ziyang Ma and Zhikang Niu and Wenming Tu and Tianrui Wang and Ruiqi Yan and Junxi Liu and Yanru Huo and Nickk Huang and Yang Liu and Qicong Xie and Zeyu Xie and Hui Wang and Haitao Li and Zixuan Jiang and Yalin Li and Jie Fang and Yifan Duan and Zeyue Tian and Guangzheng Li and Haina Zhu and Shuyi Wang and Jinwen Wang and Mingyu Cui and Tian Tan and Auden and Sen Liang and Steve Yves and Shan Yang and Liefeng Bo and Zilong Zheng and Kai Yu and Eng-Siong Chng and Xie Chen},
  year={2026},
  eprint={2609.08936},
  archivePrefix={arXiv},
  primaryClass={cs.SD},
  url={https://arxiv.org/abs/2609.08936},
}
```

## License

AuK is released under the **MIT License**. See [`LICENSE`](LICENSE) for the full terms.
