---
library_name: transformers
license: mit
pipeline_tag: automatic-speech-recognition
language:
  - zh
  - en
tags:
  - audio
  - speech-recognition
  - contextual-asr
---

<div align="center">
  <img src="./figures/bailing-logo.png" width="60" alt="Bailing logo" />
  <h1>Ming-3.0-asr-tiny</h1>
  <p><i>Context-aware speech recognition for Chinese, English, and dialects.</i></p>
</div>

English · [简体中文](https://huggingface.co/inclusionAI/Ming-3.0-asr-tiny/blob/main/README.zh.md)

[GitHub code and cookbook](https://github.com/inclusionAI/Ming-3.0-asr) · [Quick Start](#quick-start) · [Evaluation](#evaluation)

**Ming-3.0-asr-tiny** combines the Ling-tiny-v3 language backbone with an audio encoder. It transcribes single-turn Chinese and English speech, covers regional dialects, and can use hotwords or preceding dialogue to improve recognition of domain-specific terms. This repository includes the model weights, tokenizer, custom Transformers implementation, and runnable inference example.

## Capabilities

- **Chinese and English ASR:** speech-to-text transcription through one model interface.
- **Dialect recognition:** evaluated on 15 regional dialect test sets, including Cantonese, Minnan, and Shanghainese.
- **Context ASR:** accepts relevant hotwords or dialogue context as part of the transcription prompt.
- **Challenging speech:** evaluated on noisy speech and five application domains.

## Architecture

<p align="center"><img src="./figures/model.jpg" width="850" alt="Ming-3.0-asr-tiny architecture" /></p>

## Quick Start

### Download and install

Use Python 3.12 on a Linux machine with a compatible CUDA GPU. Download the complete checkpoint and install its dependencies, including PyTorch and torchaudio:

```bash
python -m pip install "huggingface_hub[cli]"
hf download inclusionAI/Ming-3.0-asr-tiny --local-dir Ming-3.0-asr-tiny
cd Ming-3.0-asr-tiny
python -m pip install -r requirements.txt
```

### Run the PyTorch / Transformers example

```bash
python examples/transcribe.py \
  --model . \
  --audio /path/to/speech.wav
```

Add `--language-hint zh` or `--language-hint en` when the language is known. The example uses CUDA, BF16, SDPA, greedy decoding, and up to 256 new tokens; it loads the bundled model code with `trust_remote_code=True`. The dependency versions are listed in `requirements.txt`, including Transformers 5.12.1, fla-core 0.5.2, and PyTorch 2.11.0. For another CUDA version, first install matching PyTorch and torchaudio 2.11.0 wheels using the [official PyTorch instructions](https://pytorch.org/get-started/previous-versions/), then run `pip install -r requirements.txt`.

### PyTorch / Transformers Python API

Run this directly from the downloaded model directory with your own `speech.wav`. It is the same inference path as the bundled [executable example](./examples/transcribe.py):

```python
import soundfile as sf
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from asr_request import decode_transcript, prepare_asr_request

processor = AutoProcessor.from_pretrained(".", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    ".", trust_remote_code=True, dtype=torch.bfloat16,
    device_map="cuda:0", attn_implementation="sdpa",
).eval()
waveform, rate = sf.read("speech.wav", dtype="float32", always_2d=True)
inputs = prepare_asr_request(
    processor, (waveform.T, rate), return_tensors="pt",
).to(model.device)
eos = model.config.text_config.eos_token_id
with torch.inference_mode():
    output = model.generate(
        **inputs, max_new_tokens=256, do_sample=False,
        eos_token_id=eos, pad_token_id=eos, no_repeat_ngram_size=10,
    )
print(decode_transcript(
    processor.tokenizer, output[0, inputs.input_ids.shape[1]:].tolist(),
))
```

### Context ASR

Ordinary transcription and Context ASR use the same input format. Append the topic and hotwords directly to the base instruction, without a newline. For known-language clips up to 60 seconds, `--context-chunks` selects 3000 mel frames up to 30 seconds and 6000 beyond 30 seconds:

```bash
python examples/transcribe.py --model . --audio /path/to/speech.wav \
  --language-hint zh --context-chunks \
  --prompt $'Please recognize the language of this speech and transcribe it, placing a `\t` between the identified language and the transcribe.This is an audio about 电影蜥蜴.This audio may contains the following words or phrases:蜥蜴,姜知垠,曹承佑,姜惠贞,八音盒.'
```

For English, use `--language-hint en`. The topic and hotwords above are illustrative. Dialogue context can also be included in the prompt text. For Python calls, pass the full prompt through `prepare_asr_request(..., prompt=...)`.

### SGLang-Omni serving

[SGLang-Omni](https://sgl-project.github.io/sglang-omni/) serves this checkpoint on one GPU:

```bash
sgl-omni serve --model-path inclusionAI/Ming-3.0-asr-tiny
```

Once the server is running, transcribe a WAV file through the OpenAI-compatible audio endpoint:

```bash
curl -X POST http://127.0.0.1:8000/v1/audio/transcriptions \
  -F model=inclusionAI/Ming-3.0-asr-tiny \
  -F file=@/path/to/speech.wav \
  -F response_format=json
```

The response contains a `text` field. `language` accepts `en` or `zh`, `prompt` appends one line of topic or hotword context, and `stream=true` returns the transcript as server-sent events. See the [SGLang-Omni cookbook](https://sgl-project.github.io/sglang-omni/cookbook/ming3_asr.html) for response formats, streaming, and long-audio handling.

## Evaluation

### ASR Overview

<p align="center"><img src="./figures/asr.png" width="1000" alt="ASR performance overview" /></p>

[Watch the Ming-3.0-asr-tiny release film](https://github.com/NiniAndy/Ming-3.0-asr-tiny-blog/releases/download/media-2026-10-19/ming-3.0-asr-final.mp4)

### Chinese and English ASR

<p align="center"><img src="./figures/开源asr.png" width="1000" alt="Chinese and English ASR evaluation" /></p>

### Dialects and Domains

<p align="center"><img src="./figures/自建asr.png" width="1000" alt="Dialect and domain ASR evaluation" /></p>

### Context ASR

<p align="center"><img src="./figures/contextasr.png" width="1000" alt="Context ASR evaluation" /></p>

## Usage Notes

- Output is transcription text, without word-level timestamps or speaker diarization.
- The included example does not support streaming input; image and video inputs are unsupported.
- Long audio can be encoded in chunks with `--audio-chunk-frames`, subject to the model context limit.
- Hotwords are hints, not a guarantee that a term will appear in the transcript.

For local Transformers inference, run the bundled [PyTorch example](./examples/transcribe.py).

## License

The model weights and original project code are released under the [MIT License](./LICENSE), following the [Ming project](https://github.com/inclusionAI/Ming). Bundled Apache-2.0 source files retain their own headers and [license text](./LICENSE-APACHE-2.0). `modeling_whisper_encoder.py` retains the MIT notice for code adapted from OpenAI Whisper.

## Citation

If you use Ming-3.0-asr-tiny, cite the [GitHub repository](https://github.com/inclusionAI/Ming-3.0-asr). Citation metadata is also available in [CITATION.cff](./CITATION.cff).

```bibtex
@misc{ming_3_0_asr_tiny_2026,
  author = {{inclusionAI}},
  title = {Ming-3.0-asr-tiny: Context-Aware Speech Recognition},
  year = {2026},
  url = {https://github.com/inclusionAI/Ming-3.0-asr}
}
```
