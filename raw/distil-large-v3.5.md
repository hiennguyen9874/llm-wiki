---
language:
- en
license: mit
library_name: transformers
tags:
- audio
- automatic-speech-recognition
widget:
- example_title: LibriSpeech sample 1
  src: https://cdn-media.huggingface.co/speech_samples/sample1.flac
- example_title: LibriSpeech sample 2
  src: https://cdn-media.huggingface.co/speech_samples/sample2.flac
pipeline_tag: automatic-speech-recognition
---

# Distil-Whisper: Distil-Large-v3.5

Distil-Whisper is the knowledge-distilled version of OpenAI's [Whisper-Large-v3](https://huggingface.co/openai/whisper-large-v3), described in the paper [Robust Knowledge Distillation via Large-Scale Pseudo Labelling](https://arxiv.org/abs/2311.00430). As the newest addition to the Distil-Whisper English family, Distil-Large-v3.5 maintains the high efficiency of its predecessors while delivering better performance.

Compared to earlier models, Distil-Large-v3.5 has been trained on over 4× more diverse public data (98k hours) and uses a ["patient" teacher](https://arxiv.org/abs/2106.05237) with an extended training schedule and aggressive data augmentation ([SpecAugment](https://arxiv.org/abs/1904.08779)) during distillation. This results in enhanced robustness and accuracy compared to previous Distil-Whisper models, making it suitable as a drop-in replacement.

| Model                                                                        | Params / M | Rel. RTFx | Short-Form OOD WER | Long-Form OOD WER |
| ---------------------------------------------------------------------------- | ---------- | --------- | ------------------ | ----------------- |
| [large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo)       | 809        | 1.0       | 7.30               | 10.25             |
| [distil-large-v3](https://huggingface.co/distil-whisper/distil-large-v3)     | 756        | 1.44      | 7.53               | 11.6              |
| [distil-large-v3.5](https://huggingface.co/distil-whisper/distil-large-v3.5) | 756        | **1.46**  | **7.08**           | **11.39**         |

*Why consider Distil-Large-v3.5 when Whisper-Large-v3-Turbo already exists?*

1. It offers a different balance between accuracy and efficiency, remains **~1.5x faster** than Whisper-Large-v3-Turbo while performing slightly better on short-form transcription and falling ~1% behind on long-form transcription.
2. It works perfectly as a draft model for **speculative decoding** with Whisper-Large-v3. By keeping the encoder frozen during training, we need to load just two extra decoder layers and forward the encoder only once. This achieves ~2x faster inference compared to Whisper-Large-v3 while maintaining identical outputs.

This model is a 🤗 collaborative effort between [Bofeng Huang](https://huggingface.co/bofenghuang), [Eustache Le Bihan](https://huggingface.co/eustlb), [Steven Zheng](https://huggingface.co/Steveeeeeeen), and [Vaibhav Srivastav](https://huggingface.co/reach-vb).

## Table of Contents

- [Performance](#performance)
  - [Short-Form Evaluation](#short-form-evaluation)
  - [Long-Form Evaluation](#long-form-evaluation)
- [Transformers Usage](#transformers-usage)
  - [Short-Form Transcription](#short-form-transcription)
  - [Sequential Long-Form](#sequential-long-form)
  - [Chunked Long-Form](#chunked-long-form)
  - [Speculative Decoding](#speculative-decoding)
  - [Additional Speed \& Memory Improvements](#additional-speed--memory-improvements)
- [Library Integrations](#library-integrations)
  - [Whisper.cpp](#whispercpp)
  - [Faster-Whisper](#faster-whisper)
  - [OpenAI Whisper](#openai-whisper)
  - [Transformers.js](#transformersjs)
  - [Candle](#candle)
- [Training](#training)
  - [Training Details](#training-details)
  - [Training Data](#training-data)
- [License](#license)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)

## Performance

The model was evaluated on both short and long-form transcriptions, using in-distribution (ID) and out-of-distribution (OOD) datasets to assess accuracy, generalizability, and robustness.

Note that Word Error Rate (WER) results shown here are [post-normalization](https://github.com/openai/whisper/blob/main/whisper/normalizers/basic.py), which includes converting text to lowercase, removing symbols and punctuation, and more.

### Short-Form Evaluation

We've evaluated the model on 5 in-distribution (ID) test sets and 2 out-of-distribution (OOD) test sets for short-form transcription, as done in [🤗 Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard).

| Dataset     | Size / h | large-v3 | large-v3-turbo | distil-v3 | distil-v3.5 |
| ----------- | -------- | -------- | -------------- | --------- | ----------- |
| AMI         | 8.68     | 15.95    | 16.13          | 15.16     | 14.63       |
| Gigaspeech  | 35.36    | 10.02    | 10.14          | 10.08     | 9.84        |
| LS Clean    | 5.40     | 2.01     | 2.10           | 2.54      | 2.37        |
| LS Other    | 5.34     | 3.91     | 4.24           | 5.19      | 5.04        |
| Tedlium     | 2.61     | 3.86     | 3.57           | 3.86      | 3.64        |
| ----------- | -----    | -----    | -----          | -----     | -----       |
| Earnings22  | 5.43     | 11.29    | 11.63          | 11.79     | 11.29       |
| SPGISpeech  | 100.00   | 2.94     | 2.97           | 3.27      | 2.87        |
| ----------- | -----    | -----    | -----          | -----     | -----       |
| ID Average  |          | 7.15     | 7.24           | 7.37      | **7.10**    |
| OOD Average |          | 7.12     | 7.30           | 7.53      | **7.08**    |
| Average     |          | 7.14     | 7.25           | 7.41      | **7.10**    |

*Note: ID/OOD classification is based on distil-v3 and distil-v3.5 training data. Large-v3 and large-v3-turbo training corpus details are unknown, so this categorization might not represent their true in-domain vs. out-of-domain performance.*

### Long-Form Evaluation

We've evaluated the model on 1 in-distribution (ID) test sets and 4 out-of-distribution (OOD) test sets for long-form transcription, using the sequential decoding algorithm (condition_on_prev_tokens=False, return_timestamps=True).

| Dataset           | Size / h | large-v3-turbo | distil-v2 | distil-v3 | distil-v3.5 |
| ----------------- | -------- | -------------- | --------- | --------- | ----------- |
| tedlium-long-form | 2.47     | 3.07           | 9.66      | 3.9       | 4.63        |
| ----------------- | -----    | -----          | -----     | -----     | -----       |
| meanwhile         | 1.01     | 5.03           | 16.75     | 7.04      | 6.79        |
| earnings21        | 39.26    | 9.84           | 15.09     | 10.54     | 10.6        |
| earnings22        | 119.89   | 13.32          | 19.11     | 15.06     | 14.19       |
| rev16             | 16.16    | 12.82          | 21.15     | 13.76     | 13.98       |
| ----------------- | -----    | -----          | -----     | -----     | -----       |
| ID Average        |          | 3.07           | 9.66      | 3.9       | **4.63**    |
| OOD Average       |          | 10.25          | 18.03     | 11.6      | **11.39**   |
| Average           |          | 8.82           | 16.35     | 10.06     | **10.04**   |

*Note: ID/OOD classification is based on distil-v3 and distil-v3.5 training data. Large-v3 and large-v3-turbo training corpus details are unknown, so this categorization might not represent their true in-domain vs. out-of-domain performance.*

Below are the Real Time Factor (RTFx) measurements showing that Distil-Large-v3.5 is approximately 1.5x faster than Whisper-Large-v3-Turbo on long-form transcription.

| Dataset           | large-v3-turbo | distil-v2 | distil-v3 | distil-v3.5 |
| ----------------- | -------------- | --------- | --------- | ----------- |
| tedlium-long-form | 34.33          | 27.96     | 44.95     | 45.19       |
| meanwhile         | 26.55          | 28.01     | 40.84     | 42.48       |
| earnings21        | 35.25          | 36.66     | 54.69     | 54.3        |
| earnings22        | 39.08          | 42.09     | 57.28     | 58.8        |
| rev16             | 33.86          | 23.87     | 45.43     | 45.91       |
| ----------------- | -----          | -----     | -----     | -----       |
| Average           | 33.81          | 31.72     | 48.64     | **49.34**   |

## Transformers Usage

Distil-Large-v3.5 is supported in the Hugging Face 🤗 Transformers library from version 4.39 onwards. To run the model, first 
install the latest version of Transformers. For this example, we'll also install 🤗 Datasets to load a toy audio dataset 
from the Hugging Face Hub:

```bash
pip install --upgrade pip
pip install --upgrade transformers accelerate datasets[audio]
```

### Short-Form Transcription

The model can be used with the [`pipeline`](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.AutomaticSpeechRecognitionPipeline)
class to transcribe short-form audio files (< 30-seconds) as follows:

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "distil-whisper/distil-large-v3.5"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    torch_dtype=torch_dtype,
    device=device,
)

dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
sample = dataset[0]["audio"]

result = pipe(sample)
print(result["text"])
```

To transcribe a local audio file, simply pass the path to your audio file when you call the pipeline:

```diff
- result = pipe(sample)
+ result = pipe("audio.mp3")
```

For segment-level timestamps, pass the argument `return_timestamps=True` and return the `"chunks"` output:

```python
result = pipe(sample, return_timestamps=True)
print(result["chunks"])
```

<details>

<summary> For more control over the generation parameters, use the model + processor API directly: </summary>

Ad-hoc generation arguments can be passed to `model.generate`, including `num_beams` for beam-search, `return_timestamps` 
for segment-level timestamps, and `prompt_ids` for prompting. See the [docstrings](https://huggingface.co/docs/transformers/en/model_doc/whisper#transformers.WhisperForConditionalGeneration.generate)
for more details.

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
from datasets import Audio, load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "distil-whisper/distil-large-v3.5"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
dataset = dataset.cast_column("audio", Audio(processor.feature_extractor.sampling_rate))
sample = dataset[0]["audio"]

input_features = processor(
  sample["array"], sampling_rate=sample["sampling_rate"], return_tensors="pt"
).input_features

input_features = input_features.to(device, dtype=torch_dtype)

gen_kwargs = {
  "max_new_tokens": 128,
  "num_beams": 1,
  "return_timestamps": False,
}

pred_ids = model.generate(input_features, **gen_kwargs)
pred_text = processor.batch_decode(pred_ids, skip_special_tokens=True, decode_with_timestamps=gen_kwargs["return_timestamps"])

print(pred_text)
```

</details>

### Sequential Long-Form

Unlike previous Distil-Whisper releases, Distil-Large-v3 and Distil-Large-v3.5 is specifically designed to be compatible with OpenAI's sequential
long-form transcription algorithm. This algorithm uses a sliding window for buffered inference of long audio files (> 30-seconds),
and returns more accurate transcriptions compared to the [chunked long-form algorithm](#chunked-long-form).

The sequential long-form algorithm should be used in either of the following scenarios:
1. Transcription accuracy is the most important factor, and latency is less of a consideration
2. You are transcribing **batches** of long audio files, in which case the latency of sequential is comparable to chunked, while being up to 0.5% WER more accurate

If you are transcribing single long audio files and latency is the most important factor, you should use the chunked algorithm
described [below](#chunked-long-form). For a detailed explanation of the different algorithms, refer to Sections 5 of 
the [Distil-Whisper paper](https://arxiv.org/pdf/2311.00430.pdf).

The [`pipeline`](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.AutomaticSpeechRecognitionPipeline) 
class can be used to transcribe long audio files with the sequential algorithm as follows: 

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "distil-whisper/distil-large-v3.5"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    torch_dtype=torch_dtype,
    device=device,
)

dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
sample = dataset[0]["audio"]

result = pipe(sample)
print(result["text"])
```

<details>

<summary> For more control over the generation parameters, use the model + processor API directly: </summary>

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
from datasets import Audio, load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "distil-whisper/distil-large-v3.5"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
dataset = dataset.cast_column("audio", Audio(processor.feature_extractor.sampling_rate))
sample = dataset[0]["audio"]

inputs = processor(
    sample["array"],
    sampling_rate=sample["sampling_rate"],
    return_tensors="pt",
    truncation=False,
    padding="longest",
    return_attention_mask=True,
)
inputs = inputs.to(device, dtype=torch_dtype)

gen_kwargs = {
    "max_new_tokens": 448,
    "num_beams": 1,
    "condition_on_prev_tokens": False,
    "compression_ratio_threshold": 1.35,  # zlib compression ratio threshold (in token space)
    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
    "logprob_threshold": -1.0,
    "no_speech_threshold": 0.6,
    "return_timestamps": True,
}

pred_ids = model.generate(**i   nputs, **gen_kwargs)
pred_text = processor.batch_decode(pred_ids, skip_special_tokens=True, decode_with_timestamps=False)

print(pred_text)
```

</details>

### Chunked Long-Form

Distil-Large-v3.5 remains compatible with the Transformers chunked long-form algorithm. This algorithm should be used when 
a single large audio file is being transcribed and the fastest possible inference is required. In such circumstances, 
the chunked algorithm is up to 9x faster than OpenAI's sequential long-form implementation (see Table 7 of the 
[Distil-Whisper paper](https://arxiv.org/pdf/2311.00430.pdf)).

To enable chunking, pass the `chunk_length_s` parameter to the `pipeline`. For Distil-Large-v3.5, a chunk length of 25-seconds
is optimal. To activate batching over long audio files, pass the argument `batch_size`:

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "distil-whisper/distil-large-v3.5"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=25,
    batch_size=16,
    torch_dtype=torch_dtype,
    device=device,
)

dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
sample = dataset[0]["audio"]

result = pipe(sample)
print(result["text"])
```

### Speculative Decoding

Distil-Large-v3.5 can be used as an assistant to Whisper-Large-v3 for [speculative decoding](https://huggingface.co/blog/whisper-speculative-decoding).
Speculative decoding mathematically ensures that exactly the same outputs as Whisper are obtained, while being 2 times faster. 
This makes it the perfect drop-in replacement for existing Whisper pipelines, since the same outputs are guaranteed.

In the following code-snippet, we load the assistant Distil-Whisper model standalone to the main Whisper pipeline. We then
specify it as the "assistant model" for generation:

```python
from transformers import pipeline, AutoModelForCausalLM, AutoModelForSpeechSeq2Seq, AutoProcessor
import torch
from datasets import load_dataset

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

assistant_model_id = "distil-whisper/distil-large-v3.5"

assistant_model = AutoModelForCausalLM.from_pretrained(
    assistant_model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
assistant_model.to(device)

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    generate_kwargs={"assistant_model": assistant_model},
    torch_dtype=torch_dtype,
    device=device,
)

dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
sample = dataset[0]["audio"]

result = pipe(sample)
print(result["text"])
```

For more details on speculative decoding, refer to the blog post [Speculative Decoding for 2x Faster Whisper Inference](https://huggingface.co/blog/whisper-speculative-decoding).

### Additional Speed & Memory Improvements

You can apply additional speed and memory improvements to Distil-Whisper to further reduce the inference speed and VRAM 
requirements. These optimisations primarily target the attention kernel, swapping it from an eager implementation to a 
more efficient flash attention version.

#### Flash Attention 2

We recommend using [Flash-Attention 2](https://huggingface.co/docs/transformers/main/en/perf_infer_gpu_one#flashattention-2) 
if your GPU allows for it. To do so, you first need to install [Flash Attention](https://github.com/Dao-AILab/flash-attention):

```
pip install flash-attn --no-build-isolation
```

Then pass `attn_implementation="flash_attention_2"` to `from_pretrained`:

```diff
- model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
+ model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True, attn_implementation="flash_attention_2")
```

#### Torch Scale-Product-Attention (SDPA)

If your GPU does not support Flash Attention, we recommend making use of PyTorch [scaled dot-product attention (SDPA)](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html). 
This attention implementation is activated **by default** for PyTorch versions 2.1.1 or greater. To check 
whether you have a compatible PyTorch version, run the following Python code snippet:

```python
from transformers.utils import is_torch_sdpa_available

print(is_torch_sdpa_available())
```

If the above returns `True`, you have a valid version of PyTorch installed and SDPA is activated by default. If it 
returns `False`, you need to upgrade your PyTorch version according to the [official instructions](https://pytorch.org/get-started/locally/)

Once a valid PyTorch version is installed, SDPA is activated by default. It can also be set explicitly by specifying 
`attn_implementation="sdpa"` as follows:

```diff
- model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
+ model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True, attn_implementation="sdpa")
```

For more information about how to use the SDPA refer to the [Transformers SDPA documentation](https://huggingface.co/docs/transformers/en/perf_infer_gpu_one#pytorch-scaled-dot-product-attention).

#### Torch compile

Coming soon...

#### 4-bit and 8-bit Inference

Coming soon...

## Library Integrations

### Whisper.cpp

Distil-Large-v3.5 can be run with the [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) package with the original sequential long-form transcription algorithm.

Steps for getting started:

1. Clone and build the Whisper.cpp repository:

```
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make
```

2. Install the Hugging Face Hub Python package:

```bash
pip install --upgrade huggingface_hub
```

And download the GGML weights for Distil-Large-v3.5 using the following Python snippet:

```python
from huggingface_hub import hf_hub_download

hf_hub_download(repo_id='distil-whisper/distil-large-v3.5-ggml', filename='ggml-model.bin', local_dir='./models')
```

Note that if you do not have a Python environment set-up, you can also download the weights directly with `wget`:

```bash
wget https://huggingface.co/distil-whisper/distil-large-v3.5-ggml/resolve/main/ggml-model.bin -P ./models
```

3. Run inference using the provided sample audio:

```bash
./main -m ./models/ggml-model.bin -l en -f /path/to/audio/file --print-colors
```

### Faster-Whisper

Faster-Whisper is a reimplementation of Whisper using [CTranslate2](https://github.com/OpenNMT/CTranslate2/), a fast 
inference engine for Transformer models.

First, install the Faster-Whisper package according to the [official instructions](https://github.com/SYSTRAN/faster-whisper#installation).
For this example, we'll also install 🤗 Datasets to load a toy audio dataset from the Hugging Face Hub:

```bash
pip install --upgrade pip
pip install --upgrade git+https://github.com/SYSTRAN/faster-whisper datasets[audio]
```

The following code snippet loads the Distil-Large-v3.5 model and runs inference on an example file from the LibriSpeech ASR
dataset:

```python
import torch
from faster_whisper import WhisperModel
from datasets import load_dataset

# define our torch configuration
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if torch.cuda.is_available() else "float32"

# load model on GPU if available, else cpu
model = WhisperModel("distil-whisper/distil-large-v3.5-ct2", device=device, compute_type=compute_type)

# load toy dataset for example
dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
sample = dataset[1]["audio"]["path"]

segments, info = model.transcribe(sample, beam_size=5, language="en")

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
```

To transcribe a local audio file, simply pass the path to the audio file as the `audio` argument to transcribe:

```python
segments, info = model.transcribe("audio.mp3", beam_size=5, language="en")
```

### OpenAI Whisper

To use the model in the original Whisper format, first ensure you have the [`openai-whisper`](https://pypi.org/project/openai-whisper/) package installed.
For this example, we'll also install 🤗 Datasets to load a toy audio dataset from the Hugging Face Hub:

```bash
pip install --upgrade pip
pip install --upgrade openai-whisper datasets[audio]
```

The following code-snippet demonstrates how to transcribe a sample file from the LibriSpeech dataset loaded using 
🤗 Datasets:

```python
from datasets import load_dataset
from huggingface_hub import hf_hub_download
import whisper

model_path = hf_hub_download(repo_id="distil-whisper/distil-large-v3.5-openai", filename="model.bin")
model = whisper.load_model(model_path)

dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
sample = dataset[0]["audio"]["path"]

result = model.transcribe(sample, language="en")
print(result["text"])
```

Note that the model weights will be downloaded and saved to your cache the first time you run the example. Subsequently,
you can re-use the same example, and the weights will be loaded directly from your cache without having to download them
again.

To transcribe a local audio file, simply pass the path to the audio file as the `audio` argument to transcribe:

```python
result = model.transcribe("audio.mp3", language="en")
print(result["text"])
```

The Distil-Whisper model can also be used with the OpenAI Whisper CLI. Refer to the [following instructions](https://huggingface.co/distil-whisper/distil-large-v3.5-openai#cli-usage)
for details.

### Candle

Through an integration with Hugging Face [Candle](https://github.com/huggingface/candle/tree/main) 🕯️, Distil-Whisper is 
available in the Rust library 🦀

Benefit from:
* Optimised CPU backend with optional MKL support for Linux x86 and Accelerate for Macs
* Metal support for efficiently running on Macs
* CUDA backend for efficiently running on GPUs, multiple GPU distribution via NCCL
* WASM support: run Distil-Whisper in a browser

Steps for getting started:
1. Install [`candle-core`](https://github.com/huggingface/candle/tree/main/candle-core) as explained [here](https://huggingface.github.io/candle/guide/installation.html)
2. Clone the `candle` repository locally:
```
git clone https://github.com/huggingface/candle.git
```
3. Enter the example directory for [Whisper](https://github.com/huggingface/candle/tree/main/candle-examples/examples/whisper):
```
cd candle/candle-examples/examples/whisper
```
4. Run an example:
```
cargo run --example whisper --release --features symphonia -- --model distil-large-v3
```
5. To specify your own audio file, add the `--input` flag:
```
cargo run --example whisper --release --features symphonia -- --model distil-large-v3 --input audio.wav
```

**Tip:** for compiling using Apple Metal, specify the `metal` feature when you run the example:
```
cargo run --example whisper --release --features="symphonia,metal" -- --model distil-large-v3
```

Note that if you encounter the error:
```
error: target `whisper` in package `candle-examples` requires the features: `symphonia`
Consider enabling them by passing, e.g., `--features="symphonia"`
```
You should clean your `cargo` installation:
```
cargo clean
```
And subsequently recompile:
```
cargo run --example whisper --release --features symphonia -- --model distil-large-v3
```

## Training

### Training Details

Distil-Whisper inherits the encoder-decoder architecture from Whisper. The encoder maps a sequence of speech vector 
inputs to a sequence of hidden-state vectors. The decoder auto-regressively predicts text tokens, conditional on all 
previous tokens and the encoder hidden-states. Consequently, the encoder is only run forward once, whereas the decoder 
is run as many times as the number of tokens generated. In practice, this means the decoder accounts for over 90% of 
total inference time. Thus, to optimise for latency, the focus is on minimising the inference time of the decoder.

Distil-Large-v3.5 builds on techniques from previous Distil-Whisper models, particularly the training procedure introduced in [Distil-Large-v2](https://huggingface.co/distil-whisper/distil-large-v2) for teacher model distillation and the sample packing method from [Distil-Large-v3](https://huggingface.co/distil-whisper/distil-large-v3) that improves long-form transcription with sequential decoding. Beyond these established approaches, we've made several significant enhancements:

- **Significantly expanded training data**: We've increased our training dataset from 22,000 hours in the previous version to over 98,000 hours of high-quality public data, largely thanks to the [Yodas](https://huggingface.co/datasets/espnet/yodas) dataset which provides diverse content from YouTube.
- **Implemented a ["patient" teacher](https://arxiv.org/abs/2106.05237) with aggressive data augmentation ([SpecAugment](https://arxiv.org/abs/1904.08779))**: This allowed us to extend the training schedule substantially to 80 epochs compared to just 11 in the previous version. The model continues to show improvement, with evaluation loss still slightly decreasing even at this extended duration.
- **Reduced the probability of appending previous prompt in training data**: We initially set this at 50%, but discovered the model struggled with transcribing text that included previous context, possibly due to decoder size limitations. We subsequently reduced this to 20%, which improved the overall performance while still serving as a form of data augmentation.
- **Increased batch size and learning rate**: We implemented a much larger batch size of 4,096 packed segments, substantially bigger than the 256 used in the previous version. We also tested alternative learning rate schedulers including cosine, wsd, and [scheduler-free optimizers](https://github.com/facebookresearch/schedule_free/), but found the linear approach still performed best.

We also revised the segment packing order to create more logically structured packed segments and adopted [BPE dropout](https://arxiv.org/abs/1910.13267) as regularization, which we found slightly degraded performance on short-form transcription but improved results for long-form content.

The model was trained using 64 H100 GPUs on the [Jean Zay](http://www.idris.fr/eng/jean-zay/jean-zay-presentation-eng.html) cluster, with the entire training process taking three days.

The Tensorboard training logs can be found [here](https://huggingface.co/distil-whisper/distil-large-v3.5/tensorboard).
 
### Training Data

We initially gathered over 196,000 hours of public data from sources like [Common Voice](https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0), [LibriSpeech](https://huggingface.co/datasets/librispeech_asr) , [VoxPopuli](https://huggingface.co/datasets/facebook/voxpopuli) , [TED-LIUM](https://huggingface.co/datasets/LIUM/tedlium)  , [People's Speech](https://huggingface.co/datasets/MLCommons/peoples_speech), [GigaSpeech](https://huggingface.co/datasets/speechcolab/gigaspeech) , [AMI](https://huggingface.co/datasets/edinburghcstr/ami) , and notably, [Yodas](https://huggingface.co/datasets/espnet/yodas). This diverse dataset is essential for ensuring our distilled model remains robust across various audio distributions and noise conditions.

We packed the collected examples into roughly 30-second segments, with each segment containing only one speaker. To maintain high quality and consistent formatting across datasets, we pseudo-labelled these training segments using Whisper-Large-v3. We then normalized both the Whisper pseudo-labels and the ground truth labels provided by each dataset, and calculated the WER between them. We discarded any examples with a WER exceeding 10%, resulting in approximately 98,000 hours of high-quality training data.

The filtered data can be found in this [multilingual dataset](https://huggingface.co/datasets/bofenghuang/stt-pseudo-labeled-whisper-large-v3-multilingual) for reproduction and further filtering.

### Reproducing Distil-Whisper

Training and evaluation code to reproduce Distil-Whisper is available under the [Distil-Whisper repository](https://github.com/huggingface/distil-whisper/tree/main/training).

## License

Distil-Whisper inherits the [MIT license](https://github.com/huggingface/distil-whisper/blob/main/LICENSE) from OpenAI's Whisper model.

## Citation

If you use this model, please consider citing the [Distil-Whisper paper](https://arxiv.org/abs/2311.00430):
```
@misc{gandhi2023distilwhisper,
      title={Distil-Whisper: Robust Knowledge Distillation via Large-Scale Pseudo Labelling}, 
      author={Sanchit Gandhi and Patrick von Platen and Alexander M. Rush},
      year={2023},
      eprint={2311.00430},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## Acknowledgements

* OpenAI for the Whisper models and the [original codebase](https://github.com/openai/whisper)
* Hugging Face 🤗 [Transformers](https://github.com/huggingface/transformers) for the model integration
* [Sanchit Gandhi](https://huggingface.co/sanchit-gandhi) for establishing the Distil-Whisper training pipeline and conducting detailed research in this [paper](https://arxiv.org/abs/2311.00430)
* [GENCI](https://www.genci.fr/) for granting access to the IDRIS HPC resources under the allocation 2024-GC011015467
* [Georgi Gerganov](https://huggingface.co/ggerganov) for the Whisper.cpp integration
* [Systran team](https://github.com/SYSTRAN) for the Faster-Whisper integration
* [Joshua Lochner](https://huggingface.co/xenova) for the Transformers.js integration
* [Laurent Mazare](https://huggingface.co/lmz) for the Candle integration
* [Vaibhav Srivastav](https://huggingface.co/reach-vb) for Distil-Whisper distribution
* [Raghav Sonavane](https://huggingface.co/rsonavane/distil-whisper-large-v2-8-ls) for an early iteration of Distil-Whisper on the LibriSpeech dataset
