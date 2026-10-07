---
language: vie
datasets:
- legacy-datasets/common_voice
- vlsp2020_vinai_100h
- AILAB-VNUHCM/vivos
- doof-ferb/vlsp2020_vinai_100h
- doof-ferb/fpt_fosd
- doof-ferb/infore1_25hours
- linhtran92/viet_bud500
- doof-ferb/LSVSC
- doof-ferb/vais1000
- doof-ferb/VietMed_labeled
- NhutP/VSV-1100
- doof-ferb/Speech-MASSIVE_vie
- doof-ferb/BibleMMS_vie
- capleaf/viVoice
metrics:
- wer
pipeline_tag: automatic-speech-recognition
tags:
- transcription
- audio
- speech
- chunkformer
- asr
- automatic-speech-recognition
license: cc-by-nc-4.0
model-index:
- name: ChunkFormer Large Vietnamese
  results:
  - task:
      name: Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: common-voice-vietnamese
      type: common_voice
      args: vi
    metrics:
    - name: Test WER
      type: wer
      value: 6.66
    source:
      name: Common Voice Vi Leaderboard
      url: https://paperswithcode.com/sota/speech-recognition-on-common-voice-vi
  - task:
      name: Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: VIVOS
      type: vivos
      args: vi
    metrics:
    - name: Test WER
      type: wer
      value: 4.18
    source:
      name: Vivos Leaderboard
      url: https://paperswithcode.com/sota/speech-recognition-on-vivos
  - task:
      name: Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: VLSP - Task 1
      type: vlsp
      args: vi
    metrics:
    - name: Test WER
      type: wer
      value: 14.09
---

# **ChunkFormer-CTC-Large-Vie: Large-Scale Pretrained ChunkFormer for Vietnamese Automatic Speech Recognition**
<style>
img {
 display: inline;
}
</style>

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) 
[![GitHub](https://img.shields.io/badge/GitHub-ChunkFormer-blue)](https://github.com/khanld/chunkformer)
[![Paper](https://img.shields.io/badge/Paper-ICASSP%202025-green)](https://arxiv.org/abs/2502.14673)
[![Model size](https://img.shields.io/badge/Params-110M-lightgrey#model-badge)](#description)

---
## Table of contents
1. [Model Description](#description)
2. [Documentation and Implementation](#implementation)
3. [Benchmark Results](#benchmark)
4. [Usage](#usage)
6. [Citation](#citation)
7. [Contact](#contact)

---
<a name = "description" ></a>
## Model Description
**ChunkFormer-CTC-Large-Vie** is a large-scale Vietnamese Automatic Speech Recognition (ASR) model based on the **ChunkFormer** architecture, introduced at **ICASSP 2025**. The model has been fine-tuned on approximately **3000 hours** of public Vietnamese speech data sourced from diverse datasets. A list of datasets can be found [**HERE**](dataset.tsv). 

---
<a name = "implementation" ></a>
## Documentation and Implementation
The [Documentation](https://arxiv.org/abs/2502.14673) and [Implementation](https://github.com/khanld/chunkformer) of ChunkFormer are publicly available.

---
<a name = "benchmark" ></a>
## Benchmark Results
We evaluate the models using **Word Error Rate (WER)**. To ensure consistency and fairness in comparison, we manually apply **Text Normalization**, including the handling of numbers, uppercase letters, and punctuation.

1. **Public Models**:
| STT | Model                                                                  | #Params | Vivos | Common Voice | VLSP - Task 1 | Avg. |
|-----|------------------------------------------------------------------------|---------|-------|--------------|---------------|------|
| 1   | **ChunkFormer**                                                            | 110M    | 4.18   | 6.66           | 14.09             | **8.31**    |
| 2   | [vinai/PhoWhisper-large](https://huggingface.co/vinai/PhoWhisper-large)  | 1.55B   | 4.67  | 8.14         | 13.75         | 8.85 |
| 3   | [nguyenvulebinh/wav2vec2-base-vietnamese-250h](https://huggingface.co/nguyenvulebinh/wav2vec2-base-vietnamese-250h) | 95M     | 10.77 | 18.34        | 13.33         | 14.15 |
| 4   | [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) | 1.55B   | 8.81     | 15.45            | 20.41          | 14.89    |
| 5   | [khanhld/wav2vec2-base-vietnamese-160h](https://huggingface.co/khanhld/wav2vec2-base-vietnamese-160h) | 95M     | 15.05 | 10.78        | 31.62             | 19.16    |
| 6   | [homebrewltd/Ichigo-whisper-v0.1](https://huggingface.co/homebrewltd/Ichigo-whisper-v0.1) | 22M   | 13.46     | 23.52            | 21.64          | 19.54    |

2. **Private Models (API)**:
| STT | Model  | VLSP - Task 1 |
|-----|--------|---------------|
| 1   | **ChunkFormer** | **14.1**             |
| 2   | Viettel     | 14.5          |
| 3   | Google  | 19.5          |
| 4   | FPT   | 28.8          |

---
<a name = "usage" ></a>
## Quick Usage
To use the ChunkFormer model for Vietnamese Automatic Speech Recognition, follow these steps:

### Option 1: Install from PyPI (Recommended)
```bash
pip install chunkformer
```

### Option 2: Install from source
```bash
git clone https://github.com/khanld/chunkformer.git
cd chunkformer
pip install -e .
```

### Python API Usage
```python
from chunkformer import ChunkFormerModel

# Load the Vietnamese model from Hugging Face
model = ChunkFormerModel.from_pretrained("khanhld/chunkformer-ctc-large-vie")

# For single long-form audio transcription
transcription = model.endless_decode(
    audio_path="path/to/long_audio.wav",
    chunk_size=64,
    left_context_size=128,
    right_context_size=128,
    total_batch_duration=14400,  # in seconds
    return_timestamps=True
)
print(transcription)

# For batch processing of multiple audio files
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
transcriptions = model.batch_decode(
    audio_paths=audio_files,
    chunk_size=64,
    left_context_size=128,
    right_context_size=128,
    total_batch_duration=1800  # Total batch duration in seconds
)

for i, transcription in enumerate(transcriptions):
    print(f"Audio {i+1}: {transcription}")
```

### Command Line Usage
After installation, you can use the command line interface:

```bash
chunkformer-decode \
    --model_checkpoint khanhld/chunkformer-ctc-large-vie \
    --long_form_audio path/to/audio.wav \
    --total_batch_duration 14400 \
    --chunk_size 64 \
    --left_context_size 128 \
    --right_context_size 128
```

Example Output:
```
[00:00:01.200] - [00:00:02.400]: this is a transcription example
[00:00:02.500] - [00:00:03.700]: testing the long-form audio
```

**Advanced Usage** can be found [HERE](https://github.com/khanld/chunkformer/tree/main?tab=readme-ov-file#usage)

---
<a name = "citation" ></a>
## Citation
If you use this work in your research, please cite:

```bibtex
@INPROCEEDINGS{10888640,
  author={Le, Khanh and Ho, Tuan Vu and Tran, Dung and Chau, Duc Thanh},
  booktitle={ICASSP 2025 - 2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)}, 
  title={ChunkFormer: Masked Chunking Conformer For Long-Form Speech Transcription}, 
  year={2025},
  volume={},
  number={},
  pages={1-5},
  keywords={Scalability;Memory management;Graphics processing units;Signal processing;Performance gain;Hardware;Resource management;Speech processing;Standards;Context modeling;chunkformer;masked batch;long-form transcription},
  doi={10.1109/ICASSP49660.2025.10888640}}
}
```

---
<a name = "contact"></a>
## Contact
- khanhld218@gmail.com
- [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/khanld)
- [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/khanhld257/)