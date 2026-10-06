---
library_name: transformers
tags:
- automatic-speech-recognition
- speech
- audio
- transformers
- pytorch
- safetensors
- vllm
- ark-asr
pipeline_tag: automatic-speech-recognition
language:
- zh
- en
- de
- ja
- fr
- ko
- es
- pl
- it
- ro
- hu
- cs
- nl
- fi
- hr
- sk
- sl
- et
- lt
license: apache-2.0
repository: https://github.com/AutoArk/open-audio-opd
---

<div align="center">

# ARK-ASR-3B: State-of-the-Art Multilingual ASR

[![GitHub](https://img.shields.io/badge/GitHub-AutoArk%2Fopen--audio--opd-blue?logo=github)](https://github.com/AutoArk/open-audio-opd)
[![arXiv](https://img.shields.io/badge/arXiv-2605.28139-b31b1b?logo=arxiv)](https://arxiv.org/abs/2605.28139)
[![License](https://img.shields.io/badge/License-Apache--2.0-green)](https://www.apache.org/licenses/LICENSE-2.0)

</div>

> **TL;DR** ARK-ASR-3B is a multilingual automatic speech recognition model. It achieves current state-of-the-art results on the Hugging Face Open ASR Leaderboard English short-form benchmark, with an average WER of **5.04%** and RTFx of **490.98** across AMI, Earnings22, GigaSpeech, LibriSpeech, SPGISpeech, and VoxPopuli. The accompanying training, inference, and evaluation code is available at [AutoArk/open-audio-opd](https://github.com/AutoArk/open-audio-opd).

## Abstract

ARK-ASR-3B is a 3B-scale audio-capable autoregressive Transformers model for automatic speech recognition.

It combines a Whisper-style audio encoder, an MLP adapter, and a Qwen decoder with custom `arkasr` remote code.

ARK-ASR currently supports Chinese, English, German, Japanese, French, Korean, Spanish, Polish, Italian, Romanian, Hungarian, Czech, Dutch, Finnish, Croatian, Slovak, Slovene, Estonian, and Lithuanian ASR.

## Supported Languages

Chinese, English, German, Japanese, French, Korean, Spanish, Polish, Italian, Romanian, Hungarian, Czech, Dutch, Finnish, Croatian, Slovak, Slovene, Estonian, and Lithuanian.

## Model Overview

<div align="center">
  <img src="figures/ark_asr_architecture.png" width="95%" alt="ARK-ASR architecture"/>
  <br>
  <p><strong>Figure 1: ARK-ASR architecture.</strong> Audio is encoded by a Whisper-style encoder with RoPE, merged through an MLP adapter, and injected into a Qwen decoder by replacing audio placeholder token embeddings before transcript generation.</p>
</div>

- **Model size:** 3B-scale decoder LLM with a dedicated Whisper-style audio encoder and MLP adapter
- **Task:** automatic speech recognition
- **Architecture:** audio-capable autoregressive Transformers model with custom `arkasr` remote code
- **Checkpoint format:** `safetensors`
- **Sampling rate:** 16 kHz
- **Recommended inference code:** [`scripts/infer/ark_asr_transformers.py`](https://github.com/AutoArk/open-audio-opd/blob/main/scripts/infer/ark_asr_transformers.py)
- **vLLM serving:** [`scripts/vllm/ark_asr_vllm`](https://github.com/AutoArk/open-audio-opd/tree/master/scripts/vllm/ark_asr_vllm)

The model should be loaded with `trust_remote_code=True`. The official inference script handles the processor, tokenizer, audio prompt format, generation cleanup, and ASR token filtering.

## Performance

The following results are from the Hugging Face [Open ASR Leaderboard](https://huggingface.co/datasets/hf-audio/open-asr-leaderboard). Lower WER is better. ARK-ASR-3B reaches the current state of the art on this English short-form benchmark.

### English WER

| Model | AMI | Earnings22 | GigaSpeech | LS Clean | LS Other | SPGISpeech | VoxPopuli | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ARK-ASR-3B | **8.79%** | **8.23%** | **6.98%** | **1.03%** | **2.35%** | **2.46%** | **5.47%** | **5.04%** |
| ARK-ASR-0.6B | 10.02% | 9.77% | 8.00% | 1.53% | 3.51% | 2.63% | 6.31% | 5.97% |

### Chinese CER

| Model | AISHELL-1 | WenetSpeech test meeting | WenetSpeech test-net |
| --- | ---: | ---: | ---: |
| ARK-ASR-3B | **1.80%** | **4.97%** | **4.58%** |
| ARK-ASR-0.6B | 2.02% | 5.92% | 4.96% |

## Inference

Run ASR inference with Hugging Face Transformers:

```python
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer

model_path = "AutoArk-AI/ARK-ASR-3B"
audio_path = "assets/libai.wav"

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32

processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    torch_dtype=torch_dtype,
    attn_implementation="sdpa",
).to(device)
model.eval()


def build_bad_words_ids(tokenizer):
    eos_ids = tokenizer.eos_token_id
    keep_ids = {eos_ids} if isinstance(eos_ids, int) else set(eos_ids or [])
    bad_ids = set(tokenizer.all_special_ids) - keep_ids
    bad_ids.update(
        token_id
        for token, token_id in tokenizer.get_added_vocab().items()
        if token.startswith("<") and token.endswith(">") and token_id not in keep_ids
    )
    return [[token_id] for token_id in sorted(bad_ids)]

conversation = [
    {
        "role": "user",
        "content": [
            {"type": "audio", "path": audio_path},
            {"type": "text", "text": "Please transcribe this audio."},
        ],
    }
]

inputs = processor.apply_chat_template(
    conversation,
    add_generation_prompt=True,
    return_tensors="pt",
    sampling_rate=16000,
    audio_padding="longest",
    text_kwargs={"padding": "longest"},
    audio_max_length=30 * 16000,
)
inputs = inputs.to(device)
if "audios" in inputs:
    inputs["audios"] = inputs["audios"].to(dtype=torch_dtype)

bad_words_ids = build_bad_words_ids(tokenizer)
with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=256,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        bad_words_ids=bad_words_ids,
    )
decoded_outputs = tokenizer.batch_decode(
    outputs[:, inputs.input_ids.shape[1] :],
    skip_special_tokens=True,
)
print(decoded_outputs)
```

For batch JSONL inference, use the open-source inference code:

```bash
git clone https://github.com/AutoArk/open-audio-opd
cd open-audio-opd
pip install -e .
```

The input JSONL should contain one ASR sample per line:

```json
{"audio":"/path/to/audio.wav","text":"","task":"asr","begin_time":-1,"end_time":-1}
```

```bash
python scripts/infer/ark_asr_transformers.py \
  --input /path/to/input.jsonl \
  --output runs/infer/predictions.jsonl \
  --model_path AutoArk-AI/ARK-ASR-3B \
  --processor_path AutoArk-AI/ARK-ASR-3B \
  --batch_size 40 \
  --dtype bfloat16 \
  --attn_impl sdpa
```

The output JSONL preserves input metadata and adds:

- `pred_text`: cleaned prediction text for downstream evaluation
- `pred_text_raw`: raw decoded generation before cleanup

## vLLM Online Serving

ARK-ASR can also be deployed as a vLLM-backed online ASR service with the
adapter in
[`scripts/vllm/ark_asr_vllm`](https://github.com/AutoArk/open-audio-opd/tree/master/scripts/vllm/ark_asr_vllm).
The service exposes both a compact `/asr` endpoint and an OpenAI-style
`/v1/audio/transcriptions` endpoint.

Clone and install the serving code:

```bash
git clone https://github.com/AutoArk/open-audio-opd
cd open-audio-opd
pip install -e ".[vllm]"
```

Start the service:

```bash
MODEL=AutoArk-AI/ARK-ASR-3B \
GPU=0 \
PORT=8025 \
scripts/vllm/deploy_ark_asr_vllm_service.sh start
```

Check the service:

```bash
scripts/vllm/deploy_ark_asr_vllm_service.sh status
curl -sS http://127.0.0.1:8025/health
curl -sS http://127.0.0.1:8025/token-mask
```

Run one transcription request:

```bash
curl -sS -X POST http://127.0.0.1:8025/asr \
  -F file=@/path/to/audio.wav \
  -F max_new_tokens=256
```

OpenAI-style transcription endpoint:

```bash
curl -sS -X POST http://127.0.0.1:8025/v1/audio/transcriptions \
  -F file=@/path/to/audio.wav \
  -F model=ark-asr
```

Stop the service:

```bash
scripts/vllm/deploy_ark_asr_vllm_service.sh stop
```

The vLLM adapter registers the custom `arkasr` model, loads the local
processor/tokenizer with `trust_remote_code=True`, applies generation-time
token masking for non-ASR control tokens, and keeps `<|im_end|>` as the stop
token. Service logs and PID files are written under `runs/vllm/`.

## Evaluation

The reported leaderboard numbers are evaluated with the Hugging Face
[`open_asr_leaderboard`](https://github.com/huggingface/open_asr_leaderboard)
evaluation code.

For local J/WER evaluation, the repository also includes this entrypoint:

```bash
python scripts/eval/eval_jwer_ark_asr_transformers.py \
  --input /path/to/test.jsonl \
  --output runs/eval/result.jsonl \
  --model_path AutoArk-AI/ARK-ASR-3B \
  --processor_path AutoArk-AI/ARK-ASR-3B \
  --batch_size 40 \
  --dtype bfloat16 \
  --attn_impl sdpa
```

No evaluation audio or dataset files are bundled with this model repository.

## Acknowledgements

The training code is based on [THUNLP/OPD](https://github.com/thunlp/OPD/) and [verl](https://github.com/volcengine/verl). The OPD recipe uses a stronger ASR teacher to score online student rollouts.

## Citation

If you find ARK-ASR or open-audio-opd useful, please cite:

```bibtex
@misc{lin2026dataefficientopd,
  title={Data-Efficient On-Policy Distillation for Automatic Speech Recognition},
  author={Lin, Yu and Wang, Yiming and Cai, Runyuan and Zeng, Xiaodong},
  year={2026},
  eprint={2605.28139},
  archivePrefix={arXiv},
  primaryClass={cs.AI},
  url={https://arxiv.org/abs/2605.28139}
}
```
