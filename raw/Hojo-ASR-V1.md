---
license: apache-2.0
language:
- zh
- en
---

# Hojo-ASR-V1

## Overview

### Introduction

Hojo-ASR-V1 is a high-performance conversational speech recognition model powered by the Qwen3 LLM decoder. It adopts the classic Encoder-Adapter-LLM framework with a customized multi-frame acoustic fusion architecture, fully leveraging acoustic fine-grained features and strong LLM semantic capabilities. 

Optimized with multi-stage modular training and reinforcement learning, the model specializes in complex real-world scenarios including noisy environments, informal pronunciation, oral correction and Chinese-English code-switching. It currently supports accurate recognition of Mandarin, English, Cantonese, and Sichuan dialect, delivering balanced accuracy and inference efficiency for industrial deployment.


## Quickstart

### Environment Setup

The easiest way to use Hojo-ASR is to install the `hojo-asr` Python package from PyPI.

```bash
conda create -n hojo-asr python=3.10
conda activate hojo-asr
```

Run the following command to get the minimal installation with transformers-backend support:

```bash
pip install -U hojo-asr
```

### Sample Usage

```python
from hojo_asr import HOJO_ASR

parser = argparse.ArgumentParser()
parser.add_argument(
    "--batch_size", type=int, default=10, help="batch size for inference"
)
parser.add_argument("--device", type=str, default="cuda:0")
args = parser.parse_args()

model = HOJO_ASR.load_model("/path/to/model_folder", device=args.device)

# Transcribe
# List of wav paths; for a single scp file pass a str (see dataset.resolve_infer_audio_input)
wav_paths = [
    "/path/to/audio.wav",
]
wav_scp = "test.scp"

with open(wav_paths[0], "rb") as f:
    wav_bytes = f.read()

#LIST OF BYTES
wav_bytes_list = [wav_bytes, wav_bytes]

res = model.run_infer(wav_scp, batch_size=args.batch_size)
# res = model.run_infer(wav_paths, batch_size=args.batch_size)
# res = model.run_infer(wav_bytes_list, batch_size=args.batch_size)

for val in res:
    print("key :", val["key"], " text :", val["text"])
```


## Evaluation

ASR Benchmarks on Public English Datasets (WER ↓)

| Dataset | Hojo-ASR 4B |
|:--------:|:-----------------:|
| AMI | 8.64 |
| Earnings22 | 8.54 |
| Gigaspeech | 7.6 |
| LibriSpeech Clean | 1.74 |
| LibriSpeech Other | 3.66 |
| SPGISpeech | 1.92 |
| Tedlium | 3.13 |
| Voxpopuli | 7.02 |


## Roadmap
- [x] release Hojo-ASR-4B model and inference engine
- [x] support Mandarin, English, Cantonese, and Sichuan dialect
- [ ] support multi-lingual and multi-dialect

  
## Commercial Support
We offer commercial support for teams integrating Hojo ASR into their products. This includes integration assistance, custom voice development, and enterprise licensing.

Contact us or email developer@hojoai.com to discuss your requirements.
  
## Credits
Thanks to the following open-source works:
- [Qwen](https://huggingface.co/Qwen)
- [WenetSpeech-Yue](https://github.com/ASLP-lab/WenetSpeech-Yue)
- [WenetSpeech-Chuan](https://github.com/ASLP-lab/WenetSpeech-Chuan)


## Licence
This project is open-sourced under the [Apache 2.0 License](LICENSE.txt), which can be freely used for academic research, personal projects, and commercial secondary development.