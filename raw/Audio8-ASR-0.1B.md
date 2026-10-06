---
library_name: transformers
tags:
- automatic-speech-recognition
- speech
- audio
- multilingual
- transformers
- pytorch
- safetensors
- hotword
- audio8
pipeline_tag: automatic-speech-recognition
language:
- en
- zh
- fr
- ja
- yue
- de
- ko
license: cc-by-nc-4.0
repository: https://github.com/AutoArk/open-audio-opd
---

<div align="center">

# Audio8-ASR-0.1B

[![GitHub](https://img.shields.io/badge/GitHub-AutoArk%2Fopen--audio--opd-blue?logo=github)](https://github.com/AutoArk/open-audio-opd)
[![arXiv](https://img.shields.io/badge/arXiv-2605.28139-b31b1b?logo=arxiv)](https://arxiv.org/abs/2605.28139)
[![License](https://img.shields.io/badge/License-CC--BY--NC--4.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)

</div>

`Audio8-ASR-0.1B` is a compact autoregressive ASR model whose language-model
component has only 0.1B parameters. It supports multilingual speech recognition
for languages including Chinese, English, French, German, Japanese, Korean, and
Cantonese. We position it as one of the smallest usable performance ASR models
in the LLM era.

This base repository provides the Hugging Face Transformers checkpoint. We also
provide deployment-focused releases:

- [Audio8-ASR-0.1B-onnx-runtime](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-onnx-runtime)
- [Audio8-ASR-0.1B-iOS-ANE](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-iOS-ANE)

The ONNX Runtime release is designed for edge-device deployment and can run
with roughly 1.1 GB peak memory footprint, depending on device, runtime
configuration, and workload.

The iOS release is designed for local iPhone transcription with roughly 200 MB
peak runtime memory footprint, depending on device, iOS version, and workload.

## Demo Video

<p align="center">
  <video src="https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B/resolve/main/assets/audio8-teaser-aurora-redesign-final.mp4" controls preload="metadata" width="720">
    Your browser does not support the video tag.
  </video>
</p>

<p align="center">
  <a href="https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B/resolve/main/assets/audio8-teaser-aurora-redesign-final.mp4">Open the demo video</a>
</p>

## Evaluation Results

| Evaluation suite | Dataset / split | Language | Metric | Score (%) | H200 RTFx |
| --- | --- | :---: | :---: | ---: | ---: |
| Open ASR Leaderboard | AMI Cleaned | EN | WER | 10.99 | 396.91 |
| Open ASR Leaderboard | Earnings22 | EN | WER | 12.31 | 654.17 |
| Open ASR Leaderboard | GigaSpeech Cleaned | EN | WER | 8.48 | 641.19 |
| Open ASR Leaderboard | LibriSpeech test.clean | EN | WER | 2.70 | 687.84 |
| Open ASR Leaderboard | LibriSpeech test.other | EN | WER | 6.59 | 610.52 |
| Open ASR Leaderboard | SPGISpeech | EN | WER | 3.73 | 870.32 |
| Open ASR Leaderboard | VoxPopuli Cleaned AA | EN | WER | 4.39 | 686.14 |
| **Open ASR Leaderboard** | **Seven-split mean / composite** | **EN** | **WER / RTFx** | **7.03** | **741.15** |
| Internal canonical ASR eval | WenetSpeech meeting | ZH | CER | 8.842 | - |
| Internal canonical ASR eval | WenetSpeech net | ZH | CER | 7.976 | - |

The Open ASR results use the seven current public splits from
[`hf-audio/open-asr-leaderboard`](https://huggingface.co/datasets/hf-audio/open-asr-leaderboard)
at dataset revision `b6bdcd0beb34f8975dc659796176d88f43aff502`. They were
measured with the standalone Transformers package on standardized H200 Hugging
Face Jobs using BF16, eager attention, greedy decoding, `max_new_tokens=256`,
and the documented 30-second audio cap. Per-split batch sizes were 1152, 1024,
1408, 1024, 1024, 2048, and 628. Raw manifests are stored in
`hf://buckets/AutoArk-AI/audio8-asr-open-asr-results`, and the corresponding
machine-readable results are provided in
`.eval_results/open_asr_leaderboard.yaml`.

The internal canonical WenetSpeech results come from the reproducibility-checked
`teacher0p6B-step3000` export with batch size 128. Its effective model tensors
are byte-identical to this standalone release; the release only removes a
redundant tied LM-head tensor and packages the same weights for standalone use.
Chinese results are reported as character error rate. AISHELL is intentionally
excluded from this table.

## Model Overview

- **Task:** automatic speech recognition
- **Checkpoint format:** `safetensors`
- **Sampling rate:** 16 kHz
- **Decoder:** 8-layer Qwen-style causal LM
- **Audio front end:** Qwen3-ASR audio encoder plus MLP adapter/projector
- **Language-model parameters:** 103,502,336 (about 0.104B)
- **End-to-end unique parameters:** 323,990,528 (about 0.324B)
- **Runtime:** Hugging Face Transformers
- **Hotwords:** optional decode-time logit boosting, no fine-tuning required

The model should be loaded with `trust_remote_code=True`.

## Files

- `config.json`, tokenizer files, processor files, and `model.safetensors`
- `configuration_arkasr.py`, `modeling_arkasr.py`, `processing_arkasr.py`
- `qwen3_asr_audio_config.py`, `qwen3_asr_audio_model.py`
- `hotword/`: backend-agnostic hotword trie
- `examples/`: Transformers inference examples

The root `config.json` is intentionally kept in this repository so Hugging Face
can recognize the model package and count downloads through normal model-file
queries.

## Transformers Inference

```python
import torch
from transformers import AutoModelForCausalLM, AutoProcessor


model_path = "AutoArk-AI/Audio8-ASR-0.1B"
audio_path = "path/to/audio.wav"

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.bfloat16 if device == "cuda" else torch.float32

processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    torch_dtype=torch_dtype,
    attn_implementation="eager",
).to(device)
model.eval()

conversation = [
    {
        "role": "user",
        "content": [
            {"type": "audio", "path": audio_path},
            {"type": "text", "text": "Please transcribe this audio."},
        ],
    }
]

batch = processor.apply_chat_template(
    conversation,
    return_tensors="pt",
    sampling_rate=16000,
    audio_padding="longest",
    add_generation_prompt=True,
    audio_max_length=30 * 16000,
    text_kwargs={"padding": "longest", "truncation": True, "max_length": 1000},
)
batch = {key: value.to(device) if hasattr(value, "to") else value for key, value in dict(batch).items()}

with torch.inference_mode():
    output_ids = model.generate(**batch, max_new_tokens=128, do_sample=False)

prompt_len = int(batch["input_ids"].shape[1])
text = processor.decode(output_ids[0, prompt_len:], skip_special_tokens=True).strip()
print(text)
```

Equivalent script:

```bash
python examples/transcribe.py path/to/audio.wav --model AutoArk-AI/Audio8-ASR-0.1B
```

For local staging before upload:

```bash
python examples/transcribe.py path/to/audio.wav --model .
```

## Hotword Boosting

Hotwords are applied at decode time by nudging logits for tokenizer paths that
match the requested words. This does not modify model weights and does not
inject the hotwords into the prompt.

```bash
python examples/transcribe_hotword.py path/to/audio.wav \
  --model AutoArk-AI/Audio8-ASR-0.1B \
  --hotwords "Audio8,AutoArk"
```

Main knobs:

- `--hotword_topk`: only boost tokens already inside the current top-k logits.
- `--hotword_start_boost`: boost for the first token of each hotword.
- `--hotword_continuation_boost`: boost for continuation tokens after a matched prefix.

## Related Releases

- [ONNX Runtime package](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-onnx-runtime)
- [iOS ANE package](https://huggingface.co/AutoArk-AI/Audio8-ASR-0.1B-iOS-ANE)

## Limitations

- The default examples target short-form ASR and truncate audio at 30 seconds.
- Hotword boosting can help with near-miss terms but can also over-bias decoding
  when boost values are too high.
- Some Transformers/tokenizers versions emit a Qwen tokenizer regex warning. The
  staged tokenizer config is kept in the loadable form used by this package; pass
  explicit tokenizer regex flags only after testing your local Transformers version.

## Acknowledgements

The audio encoder backbone is based on
[Qwen3-ASR-0.6B](https://huggingface.co/Qwen/Qwen3-ASR-0.6B), with the audio
adapter and projector trained as part of Audio8-ASR. The language-model backbone
is based on
[Ref-Pretrain-Qwen-104M](https://huggingface.co/MiniLLM/Ref-Pretrain-Qwen-104M).
