---
library_name: transformers
tags:
- automatic-speech-recognition
- speech
- audio
- transformers
- pytorch
- safetensors
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

# ARK-ASR-0.6B: Efficient Multilingual ASR with Online Policy Distillation

[![GitHub](https://img.shields.io/badge/GitHub-AutoArk%2Fopen--audio--opd-blue?logo=github)](https://github.com/AutoArk/open-audio-opd)
[![arXiv](https://img.shields.io/badge/arXiv-2605.28139-b31b1b?logo=arxiv)](https://arxiv.org/abs/2605.28139)
[![License](https://img.shields.io/badge/License-Apache--2.0-green)](https://www.apache.org/licenses/LICENSE-2.0)

</div>

> **TL;DR** ARK-ASR-0.6B is an automatic speech recognition model trained with teacher-data adaptation and on-policy distillation, using a compact 0.6B-scale decoder LLM together with a dedicated audio encoder and adapter. The accompanying training, inference, and evaluation code is available at [AutoArk/open-audio-opd](https://github.com/AutoArk/open-audio-opd).

## Abstract

ARK-ASR is an audio ASR student model optimized with the **teacher-data adaptation + online policy distillation (TD + OPD)** recipe from `open-audio-opd`.

Instead of relying only on static supervised transcripts, OPD lets the student generate transcripts online and trains it against token-level teacher scores on the student's own generated behavior. This checkpoint corresponds to the `Ark-Base+TD+OPD` model reported in the open-audio-opd results.

ARK-ASR currently supports Chinese, English, German, Japanese, French, Korean, Spanish, Polish, Italian, Romanian, Hungarian, Czech, Dutch, Finnish, Croatian, Slovak, Slovene, Estonian, and Lithuanian ASR.

## Supported Languages

Chinese, English, German, Japanese, French, Korean, Spanish, Polish, Italian, Romanian, Hungarian, Czech, Dutch, Finnish, Croatian, Slovak, Slovene, Estonian, and Lithuanian.

## Model Overview

<div align="center">
  <img src="figures/ark_asr_architecture.png" width="95%" alt="ARK-ASR architecture"/>
  <br>
  <p><strong>Figure 1: ARK-ASR architecture.</strong> Audio is encoded by a Whisper-style encoder with RoPE, merged through an MLP adapter, and injected into a Qwen2 decoder by replacing audio placeholder token embeddings before transcript generation.</p>
</div>

- **Model size:** 0.6B decoder LLM parameters, with a separate 0.6B-scale Whisper-style audio encoder and MLP adapter
- **Task:** automatic speech recognition
- **Architecture:** audio-capable autoregressive Transformers model with custom `arkasr` remote code
- **Checkpoint format:** `safetensors`
- **Sampling rate:** 16 kHz
- **Recommended inference code:** [`scripts/infer/ark_asr_transformers.py`](https://github.com/AutoArk/open-audio-opd/blob/main/scripts/infer/ark_asr_transformers.py)

The model should be loaded with `trust_remote_code=True`. The official inference script handles the processor, tokenizer, audio prompt format, generation cleanup, and ASR token filtering.

## Performance

The following results are from the `open-audio-opd` evaluation. Lower CER/WER is better.

### English WER

| Model | AMI | Earnings22 | GigaSpeech | LS Clean | LS Other | SPGISpeech | VoxPopuli | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ark-ASR | 11.54% | 10.07% | 8.95% | 1.87% | 3.89% | 2.89% | 6.63% | 6.55% |
| Qwen3-ASR-0.6B | 11.66% | 11.06% | 9.14% | 2.13% | 4.45% | 3.03% | 7.07% | 6.93% |
| Qwen3-ASR-1.7B | 10.56% | 10.25% | 8.74% | 1.63% | 3.40% | 2.84% | 6.35% | 6.25% |

### Chinese CER

| Model | AISHELL-1 | Wenet-meeting | Wenet-net | Avg |
| --- | ---: | ---: | ---: | ---: |
| Ark-ASR | 2.02% | 5.92% | 4.96% | 4.30% |
| Qwen3-ASR-0.6B | 2.07% | 5.57% | 5.45% | 4.36% |
| Qwen3-ASR-1.7B | 1.50% | 4.69% | 4.55% | 3.58% |

`Ark-ASR` is the 0.6B-scale ASR checkpoint trained with teacher-data adaptation and on-policy distillation from `open-audio-opd`.

## Inference

Run ASR inference with Hugging Face Transformers:

```python
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer

model_path = "AutoArk-AI/ARK-ASR-0.6B"
audio_path = "assets/libai.wav"

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

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
  --model_path AutoArk-AI/ARK-ASR-0.6B \
  --processor_path AutoArk-AI/ARK-ASR-0.6B \
  --batch_size 40 \
  --dtype float16 \
  --attn_impl sdpa
```

The output JSONL preserves input metadata and adds:

- `pred_text`: cleaned prediction text for downstream evaluation
- `pred_text_raw`: raw decoded generation before cleanup

## Evaluation

The repository also includes a J/WER evaluation entrypoint:

```bash
python scripts/eval/eval_jwer_ark_asr_transformers.py \
  --input /path/to/test.jsonl \
  --output runs/eval/result.jsonl \
  --model_path AutoArk-AI/ARK-ASR-0.6B \
  --processor_path AutoArk-AI/ARK-ASR-0.6B \
  --batch_size 40 \
  --dtype float16 \
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
