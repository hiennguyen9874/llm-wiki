---
library_name: vllm
language:
  # Arabic — MSA
  - ar        # Modern Standard Arabic
  # Arabic — Maghreb
  - ary       # Moroccan Arabic
  - ayl       # Libyan Arabic
  - aeb       # Tunisian Arabic
  - arq       # Algerian Arabic
  - mey       # Hassaniya Arabic (Mauritania)
  # Arabic — Gulf
  - afb       # Gulf Arabic (Bahrain, Kuwait, Qatar, UAE)
  - ars       # Najdi Arabic (Saudi Arabia)
  - acx       # Omani Arabic
  - ayn       # Sanaani Arabic (Yemen)
  # Arabic — Nile Valley
  - arz       # Egyptian Arabic
  - apd       # Sudanese Arabic
  # Arabic — Levantine
  - acm       # Mesopotamian Arabic (Iraq)
  - ajp       # South Levantine Arabic (Jordan, Palestine)
  - apc       # North Levantine Arabic (Lebanon, Syria)
  # Arabic — Other
  - shu       # Chadian Arabic
pipeline_tag: automatic-speech-recognition
inference: false
tags:
- mistral-common
- audio
- speech-to-text
- realtime
base_model:
- mistralai/Voxtral-Mini-4B-Realtime-2602
metrics:
- cer
- wer
---

# Voxtral Mini 4B Realtime Arabic

> [!Note]
> See a space live demo directly in your browser [here](https://huggingface.co/spaces/mistralai/Voxtral-Mini-4B-Realtime-Arabic-WebGPU) powered by this [ONNX checkpoint](https://huggingface.co/onnx-community/Voxtral-Mini-4B-Realtime-Arabic-ONNX). Many thanks to the ONNX community.

Voxtral Mini 4B Realtime Arabic is a streaming speech-to-text model for **Arabic dialects and Modern Standard Arabic**.
It is designed to handle challenging real-world audio and **code-switching**, where speakers alternate between languages within the same conversation.

This model is **fine-tuned from [Voxtral-Mini-4B-Realtime-2602](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)** and has approximately 4.4 billion parameters, with weights in BF16 precision. It processes 16 kHz audio through a causal audio encoder and language decoder, producing text as audio arrives. Its configurable transcription delay supports applications such as live captions and voice interfaces.

At a configured transcription delay of **480 ms**, the model achieves an average Character Error Rate (CER) of **8.82%** across seven Arabic benchmarks. It outperforms several open-source and proprietary offline models and comes within **0.91 percentage points** of Voxtral Transcribe Arabic’s **7.91% CER**.

The model is co-developed with the Ministère de la Transition Numérique et de la Réforme Administrative (MTNRA) under the umbrella of the strategic partnership signed between Mistral and Morocco in January 2026 as a sovereign AI asset.

## Usage

### vLLM

Use [vLLM](https://github.com/vllm-project/vllm) with Voxtral Realtime support and `mistral-common` audio dependencies.

```bash
pip install --upgrade vllm "mistral-common[audio]"

vllm serve mistralai/Voxtral-Mini-4B-Realtime-Arabic
```

Stream audio over WebSocket to `/v1/realtime` by adapting this [example](https://docs.vllm.ai/en/stable/examples/speech_to_text/realtime/?h=realtime).

### Transformers

Starting with `transformers >= 5.2.0`, Voxtral Realtime runs natively in Transformers.
See the [Transformers documentation](https://huggingface.co/docs/transformers/main/en/model_doc/voxtral_realtime) for details.

```bash
pip install --upgrade "transformers>=5.2.0" accelerate
pip install --upgrade "mistral-common[audio]"
```

<details>
<summary><b>Example</b></summary>

  ```python
import torch
from transformers import VoxtralRealtimeForConditionalGeneration, AutoProcessor
from mistral_common.tokens.tokenizers.audio import Audio
from huggingface_hub import hf_hub_download

repo_id = "mistralai/Voxtral-Mini-4B-Realtime-Arabic"

processor = AutoProcessor.from_pretrained(repo_id)
model = VoxtralRealtimeForConditionalGeneration.from_pretrained(
    repo_id, dtype=torch.bfloat16, device_map="auto"
)

audio_file = hf_hub_download(
    repo_id=repo_id,
    filename="assets/bank-take-2.wav",
    repo_type="model",
)
audio = Audio.from_file(audio_file, strict=False)
audio.resample(processor.feature_extractor.sampling_rate)

inputs = processor(audio.audio_array, return_tensors="pt")
inputs = inputs.to(model.device, dtype=model.dtype)

outputs = model.generate(**inputs, do_sample=False)
print(processor.batch_decode(outputs, skip_special_tokens=True)[0])
```
</details>

## Benchmarks

We report Character Error Rate (CER) on established Arabic benchmarks and two new benchmarks, ISMA and Darija in the Wild, co-developed with Morocco’s *Ministère de la Transition Numérique et de la Réforme Administrative* (MTNRA). Lower CER is better.

![Average performances by delay](assets/avg_evals_by_delay.png)

![Benchmark performances](assets/benchmark_scores.png)

![ISMA and Darija in the Wild Benchmark composition](assets/benchmark_composition.png)


All evaluations use temperature `0.0`; the realtime model uses a configured transcription delay of `480 ms`. CER is computed with normalization co-developed with MTNRA, covering Arabic dialect-specific spelling, clitics, loanwords, and spoken numbers. The code is available in normalization.py. Scores may differ under other normalization methods.

Example of usage:
```python
from normalization import normalize_arabic_asr

reference = normalize_arabic_asr(reference)
hypothesis = normalize_arabic_asr(hypothesis)
```

*Note: Gemini’s safety filters block transcription of some FLEURS audio samples.*

#### Emerging capabilities

Training focused on Arabic code-switching. We also observe improvements in code-switching involving languages outside the training focus.

## Limitations

The model targets Arabic transcription. For other languages, use the original [Voxtral Mini 4B Realtime](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602).

## License

This model is licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0.txt).

*You must not use this model in a manner that infringes, misappropriates, or otherwise violates any third party’s rights, including intellectual property rights.*