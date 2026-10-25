---
language:
  - en
  - zh
license: mit
library_name: transformers
tags:
  - audio
  - speech
  - automatic-speech-recognition
  - audio-understanding
  - audio-reasoning
  - speech-to-text
  - text-to-speech
  - conversational
  - mixture-of-experts
  - custom_code
model_name: Ming-3.0-audio-tiny
---

<div align="center">
  <img src="assets/ming-3.0-audio-logo.png" width="110" alt="Ming logo">
  <h1>Ming-3.0-audio-tiny</h1>
  <p><strong>Hear clearly. Understand deeply. Act intelligently.</strong></p>
</div>

Ming-3.0-audio-tiny is a compact native audio-language model from inclusionAI. It accepts audio together with text instructions and supports speech recognition, spoken question answering, audio understanding, audio reasoning, and optional synthesized-speech responses.

<div align="center">
<table align="center" border="0" cellpadding="0" cellspacing="0" style="border:none; display:inline-table; width:auto; margin:0 auto;">
  <tr>
    <td valign="middle" style="border:none; padding:0;"><a href="https://github.com/inclusionAI/Ming-3.0-audio-flash" style="display:inline-block; white-space:nowrap; line-height:17px; background-image:linear-gradient(currentColor,currentColor); background-repeat:no-repeat; background-position:0 calc(100% - 0.5px); background-size:100% 1px; text-decoration:none;"><img src="assets/github-invertocat-black-17.svg" width="17" height="17" alt="" style="display:inline-block; vertical-align:middle; position:relative; top:-1.5px; margin:0 3px 0 0;">GitHub</a></td>
    <td valign="middle" style="border:none; padding:0 8px;">·</td>
    <td valign="middle" style="border:none; padding:0;"><a href="https://modelscope.cn/models/inclusionAI/Ming-3.0-audio-tiny">🤖 ModelScope</a></td>
    <td valign="middle" style="border:none; padding:0 8px;">·</td>
    <td valign="middle" style="border:none; padding:0;"><a href="https://huggingface.co/inclusionAI/Ming-3.0-audio-flash">🤗 Flash</a></td>
    <td valign="middle" style="border:none; padding:0 8px;">·</td>
    <td valign="middle" style="border:none; padding:0;"><a href="https://huggingface.co/inclusionAI/Ming-3.0-audio-tiny">🤗 Tiny</a></td>
    <td valign="middle" style="border:none; padding:0 8px;">·</td>
    <td valign="middle" style="border:none; padding:0;"><a href="https://github.com/inclusionAI/Ming-3.0-audio-flash/tree/main/examples">💻 Examples</a></td>
  </tr>
</table>
</div>

## Model Summary

| Property | Description |
| --- | --- |
| Developer | inclusionAI |
| Model type | Compact native audio-language Mixture-of-Experts model |
| Parameters | 9.3B total parameters, 2.7B activated per inference step |
| Inputs | Audio and text instructions |
| Outputs | Text, or text with optional synthesized speech |
| Primary languages | Chinese and English, including varied accents and dialects |
| License | MIT |

## Highlights

- **Efficient audio intelligence:** Provides speech and audio understanding in a compact Mixture-of-Experts model.
- **Complex speech recognition:** Handles Chinese and English speech, dialects, accents, noisy environments, and multi-speaker recordings.
- **Long-audio understanding:** Comprehends and analyzes long-form recordings.
- **Multidimensional perception:** Understands speech, non-speech sounds, acoustic scenes, and music.
- **Audio reasoning:** Answers questions and performs reasoning over audio content.
- **Audio interaction:** Produces text responses and can optionally synthesize speech with built-in voices or a reference voice.

## Architecture

Ming-3.0-audio-tiny combines an audio encoder and projector with a compact Mixture-of-Experts language backbone. An optional Talker generates speech responses from the model's output.

## Quick Start with Transformers

The model uses custom Transformers code. Review the repository code before enabling `trust_remote_code=True`.

```bash
git clone https://github.com/inclusionAI/Ming-3.0-audio-flash.git
cd Ming-3.0-audio-flash

python -m venv .venv-transformers
source .venv-transformers/bin/activate
pip install -r requirements-transformers.txt
```

### Audio Understanding

```bash
python examples/transformers_audio.py examples/audio/introduce_ant_group.wav \
  --model inclusionAI/Ming-3.0-audio-tiny \
  --prompt "Please answer the question in the audio."
```

### Speech Recognition

```bash
python examples/transformers_audio.py examples/audio/introduce_ant_group.wav \
  --model inclusionAI/Ming-3.0-audio-tiny \
  --task asr \
  --max-new-tokens 256 \
  --no-repeat-ngram-size 10
```

The validated ASR prompt asks the model to identify the spoken language and place a tab between the language label and transcription.

### Direct Python Usage

```python
import torch
from transformers import AutoModelForCausalLM, AutoProcessor

model_id = "inclusionAI/Ming-3.0-audio-tiny"
audio_path = "examples/audio/introduce_ant_group.wav"

processor = AutoProcessor.from_pretrained(
    model_id,
    trust_remote_code=True,
    use_fast=False,
)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
).eval()

messages = [
    {
        "role": "user",
        "content": [
            {"type": "audio", "audio": audio_path},
            {"type": "text", "text": "Please answer the question in the audio."},
        ],
    }
]

inputs = processor(messages).to(model.device)
inputs["audio_feats"] = inputs["audio_feats"].to(model.dtype)

with torch.inference_mode():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=False,
    )

generated_ids = output_ids[0, inputs["input_ids"].shape[1] :]
response = processor.decode(generated_ids, skip_special_tokens=True).strip()
print(response)
```

## Speech Output

The Talker example supports built-in voices and reference-audio voice prompting:

```bash
python examples/transformers_thinker_talker.py \
  --model inclusionAI/Ming-3.0-audio-tiny \
  --audio examples/audio/introduce_ant_group.wav \
  --voice US_Stella \
  --output output.wav
```

See the [voice guide](https://github.com/inclusionAI/Ming-3.0-audio-flash/blob/main/docs/voices.md) for available voice names, invocation rules, and reference-audio usage.

## Serving

### vLLM-Omni

Text output or ASR uses the Tiny Thinker on one GPU:

```bash
export MODEL_PATH=inclusionAI/Ming-3.0-audio-tiny
MING_MODEL_VARIANT=tiny MING_OUTPUT_MODE=text \
  ./scripts/serve_vllm_omni.sh "$MODEL_PATH"
```

For synthesized-speech output, select the full-audio profile:

```bash
export MODEL_PATH=inclusionAI/Ming-3.0-audio-tiny
MING_MODEL_VARIANT=tiny MING_OUTPUT_MODE=audio \
  ./scripts/serve_vllm_omni.sh "$MODEL_PATH"
```

The reference full-audio profile places the Thinker on GPU 0 and the Talker on GPU 1. Select the deployment YAML that matches text-only, ASR, or Talker output. See the [deployment guide](https://github.com/inclusionAI/Ming-3.0-audio-flash/blob/main/README.md#vllm-omni) for details.

Select an IP or registered voice with the vLLM-Omni client's `--voice` option:

```bash
python examples/vllm_omni_audio_chat.py examples/audio/introduce_ant_group.wav \
  --audio-response \
  --voice US_Stella \
  --output-audio outputs/answer.wav
```

The client sends this selection as Chat Completions `audio.voice: {"id": "..."}`. vLLM-Omni uses the built-in IP voice `灵小柔` when no voice is specified. The model directory also provides `灵楷` and `US_James` as preset reference voices under `voice_presets/voice_audio/`, with their matching transcripts in `voice_presets/voice_prompts.json`. Both names are also available as built-in IP voices.

### SGLang

```bash
export MODEL_PATH=inclusionAI/Ming-3.0-audio-tiny
MING_MODEL_VARIANT=tiny CUDA_VISIBLE_DEVICES=0 \
  ./scripts/serve_sglang.sh "$MODEL_PATH"
```

The validated Tiny SGLang profile uses one GPU and provides text output. See the [SGLang example](https://github.com/inclusionAI/Ming-3.0-audio-flash/blob/main/examples/sglang_audio_chat.py) for client usage.

### SGLang-Omni

[SGLang-Omni](https://sgl-project.github.io/sglang-omni/) serves transcription, audio chat, and speech synthesis from one server. The Tiny checkpoint fits on a single GPU; `--talker.gpu 0` colocates speech synthesis with the other stages:

```bash
sgl-omni serve --model-path inclusionAI/Ming-3.0-audio-tiny --talker.gpu 0
```

The server exposes OpenAI-compatible `/v1/audio/transcriptions`, `/v1/audio/speech`, and `/v1/chat/completions` endpoints. The [SGLang-Omni cookbook](https://sgl-project.github.io/sglang-omni/cookbook/ming3_audio.html) shows client examples; the same requests work with the Tiny model name.

## Evaluation

The shared benchmark figures below include results for both Ming-3.0-audio-tiny and Ming-3.0-audio-flash.

### Speech Recognition

<p align="center">
  <img src="assets/benchmark-asr.png" width="100%" alt="Speech recognition benchmarks">
</p>

### Audio Intelligence

<p align="center">
  <img src="assets/benchmark-audio-intelligence.png" width="100%" alt="Audio intelligence benchmarks">
</p>

### Text Benchmarks

<p align="center">
  <img src="assets/benchmark-text.png" width="760" alt="Text benchmarks">
</p>

All benchmark values are percentages. Higher is better unless the metric is marked with a downward arrow. Results marked with an asterisk are self-evaluated. Refer to the [GitHub README](https://github.com/inclusionAI/Ming-3.0-audio-flash#benchmarks) for the latest notes and evaluation details.

## License

This model is released under the [MIT License](https://github.com/inclusionAI/Ming-3.0-audio-flash/blob/main/LICENSE). See [LEGAL.md](https://github.com/inclusionAI/Ming-3.0-audio-flash/blob/main/LEGAL.md) for the legal disclaimer.
