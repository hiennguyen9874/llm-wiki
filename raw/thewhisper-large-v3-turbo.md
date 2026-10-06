---
base_model:
- openai/whisper-large-v3-turbo
base_model_relation: quantized
license: cc-by-4.0
pipeline_tag: automatic-speech-recognition
library_name: coreml
tags:
- automatic-speech-recognition
- audio
- speech
- whisper
- multilingual
- streaming
- coreml
- cuda
- nvidia
- apple-silicon
- on-device
- ios
- macos
language:
- en
- ar
- bg
- bn
- cs
- da
- de
- el
- es
- et
- fi
- fr
- hi
- hu
- id
- it
- lt
- lv
- nl
- pl
- pt
- ro
- ru
- sk
- sl
- sv
- uk
- vi
---

# Elastic model: thewhisper-large-v3-turbo

The project GitHub: [TheWhisper](https://github.com/TheStageAI/TheWhisper/tree/main) · [TheStage Apple SDK](https://github.com/TheStageAI/AppleSDK)

**Original model:** [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) (OpenAI)

**TheWhisper-Large-V3-Turbo** is a fine-tuned, high-performance variant of OpenAI’s Whisper Large V3 model — optimized by **TheStage AI** for **real-time**, **low-latency**, and **low-power** speech-to-text (ASR) inference across multiple platforms, including **NVIDIA GPUs** and **Apple Silicon (CoreML / Neural Engine)**.

<img width="1547" height="531" alt="vanilla whisper (1)" src="https://github.com/user-attachments/assets/f0c86e58-d834-4ac7-a06b-df3a7ae3e9e9" />
<img width="1547" height="458" alt="TheStage AI Whisper (1)" src="https://github.com/user-attachments/assets/17fb45a3-b33d-4c83-b843-69b0f0aa3f65" />


## Overview

---

ElasticModels are the models produced by TheStage AI ANNA: Automated Neural Networks Accelerator. ANNA allows you to control model size, latency and quality with a simple slider movement, routing different compression algorithms to different layers. For each model, we have produced a series of optimized models:

- **XL**: Mathematically equivalent neural network, optimized with our DNN compiler.
- **L**: Near lossless model, with less than 1% degradation obtained on corresponding benchmarks.
- **M**: Faster model, with accuracy degradation less than 1.5%.
- **S**: The fastest model, with accuracy degradation less than 2%.

**How to run this model:**

| Platform | Path |
| --- | --- |
| **Apple Silicon (iOS / macOS)** | [TheStage Apple SDK](#thestage-apple-sdk) — Swift / Flutter, on-device CoreML |
| **NVIDIA GPUs (Python)** | [ElasticModels](#elasticmodels) or [TheWhisper SpeechKit](#thewhisper-speechkit) |
| **NVIDIA serving** | [Docker / OpenAI-compatible API](#serving-with-docker-image) |

Models can be accessed via TheStage AI Python SDK (ElasticModels), the TheStage Apple SDK (Swift / Flutter), or deployed as Docker containers with REST API endpoints (see Deploy section).


## System Requirements

---

### NVIDIA

| **Property**| **Value** |
 | ---  | ---  |
| **GPU** | L40s, RTX 4090, RTX 5090, H100 |
| **Python Version** | 3.10-3.12 |
| **CPU** | Intel/AMD x86_64 |
| **CUDA Version** | 12.8+ |

### Apple Silicon (TheStage Apple SDK)

| **Property**| **Value** |
 | ---  | ---  |
| **Hardware** | Apple Silicon Mac, or physical iPhone / iPad |
| **macOS** | 15.0+ |
| **iOS** | 18.0+ |
| **Xcode** | 16.0+ |
| **Swift** | 6.0+ |
| **Flutter** (optional) | 3.24+ |

> Simulator is **not** supported — run on real Apple Silicon hardware.


## TheStage AI Access Token Setup

---

Install TheStage AI CLI and setup API token:

```bash
pip install thestage
thestage config set --access-token <YOUR_ACCESS_TOKEN>
```

For the Apple SDK, create a token at [app.thestage.ai](https://app.thestage.ai) and pass it to `TheStageAI.shared.initialize(apiToken:)` (Swift) or `TheStageFlutterSDK.initialize(api_token:)` (Flutter). Token is checked online in `initialize` (once per app process when reachable). Inference runs fully on-device. Offline initialize fails — reconnect and call `initialize` again.


## TheStage Apple SDK

![On-Device Apple SDK](assets/on-device-apple-sdk-banner.png)

---

On-device transcription for **iOS and macOS**. The SDK downloads CoreML engines from this Hugging Face repo, auto-selects Neural Engine / GPU / CPU, and exposes batch `infer` plus push-based live streaming. No server in the hot path.

Docs: [TheStage Apple SDK · Whisper](https://docs.thestage.ai) · Repo: [TheStage Apple SDK](https://github.com/TheStageAI/AppleSDK)

### Installation (SwiftPM)

In Xcode: **File → Add Package Dependencies…**, paste `https://github.com/TheStageAI/AppleSDK.git`, and add the `TheStageSDK` product. Or in `Package.swift`:

```swift
.package(
    url: "https://github.com/TheStageAI/AppleSDK.git",
    exact: Version(1, 1, 0)
)
```

### Swift — batch transcription

```swift
import TheStageSDK

let ai = TheStageAI.shared
try await ai.initialize(apiToken: "th_…")

let stt = try await WhisperPipeline(
    engines_path: "TheStageAI/thewhisper-large-v3-turbo"
)

// audio: 16 kHz mono Float, samples in [-1.0, 1.0]
let result = stt.infer(audio: audio_samples, language: "en")
print(result.text)
```

Long audio is split into the bundle's window size (**10 s** for the shipping turbo engines). Optional constructor knobs: `device` (`"npu"` / `"gpu"` / `"cpu"`), `overlap_seconds`, `use_internal_vad`.

### Swift — live streaming

```swift
let streamer = stt.open_streamer(language: "en")

let captions = Task {
    for await text in streamer.partials {
        print("partial: \(text)")   // committed-so-far, grows monotonically
    }
}

for await frame in microphone_frames {   // [Float] @ 16 kHz mono
    streamer.send(frame)
    if vad_detected_pause { streamer.flush() }
}

let final_text = await streamer.finish()
await captions.value
print("final: \(final_text)")
```

`partials` is for live UI; `finish()` is the authoritative end-of-turn transcript. Call `flush()` at VAD pauses to keep latency flat on long turns; `cancel()` for barge-in.

### Flutter (iOS)

```yaml
# pubspec.yaml
dependencies:
  thestage_apple_sdk:
    git:
      url: https://github.com/TheStageAI/AppleSDK.git
      path: plugin/thestage_apple_sdk
      ref: 1.1.0
```

```dart
import 'package:thestage_apple_sdk/thestage_apple_sdk.dart';
import 'dart:typed_data';

await TheStageFlutterSDK.initialize(api_token: 'th_…');

await TheStageFlutterSDK.start_model(
  model_name: 'stt',
  engines_path: 'TheStageAI/thewhisper-large-v3-turbo',
);

// audio_samples: Float32List, 16 kHz mono, samples in [-1.0, 1.0]
final result = await TheStageFlutterSDK.infer(
  model_name: 'stt',
  input_json: {
    'audio': audio_samples,
    'language': 'en',
  },
);
print(result[0]['transcription']);
```

JSON response keys: `transcription` (`String`), `token_count` (`Int`), `decode_seconds` (`Double`), optional `tokens` (`[Int]`).

### Audio contract (Apple)

| | |
| --- | --- |
| Sample rate | **16 kHz** mono |
| Sample type | `Float` / `Float32List` in `[-1.0, 1.0]` |
| Chunk window | **10 s** (read from the bundle; older 15 / 30 s exports also work) |
| Resampling | **Not** automatic — convert mic capture before `infer` / `send` |

### Prefetch / progress

```swift
let engines_dir = try await ai.prefetch_engines(
    repo_id: "TheStageAI/thewhisper-large-v3-turbo"
)
let stt = try await WhisperPipeline(engines_path: engines_dir)

// Optional load progress:
let stt = try await WhisperPipeline(
    engines_path: "TheStageAI/thewhisper-large-v3-turbo",
    on_load_progress: { p in
        print("[\(p.model)] \(p.phase) \(Int(p.fraction * 100))%")
    }
)
```

### Apple on-device latency

Release build on **Apple M2 Max (NPU / ANE), macOS 26.2** (guidance, not an SLA):

| Metric | Value |
| --- | --- |
| RTFx (`audio_seconds / wall_seconds`) | **16.7** |
| Decode tok/s | **233** |
| Process mem | **~96 MB** |

Measured on a short ~2.6 s utterance; shipping windows are 10 s. Always bench release builds on device.


## ElasticModels

---

Elastic Models provides the same interface as HuggingFace Transformers. Here is an example of how to use the thewhisper-large-v3-turbo model.

### Installation

```bash
pip install 'thestage-elastic-models[nvidia]' \
    --extra-index-url https://thestage.jfrog.io/artifactory/api/pypi/pypi-thestage-ai-production/simple
pip install datasets==3.6.0 librosa soundfile  # only needed to load audio for the example below
```

### Usage

```python
import torch
from elastic_models.transformers import AutoModelForSpeechSeq2Seq
from transformers import AutoProcessor

model_name = "TheStageAI/thewhisper-large-v3-turbo"
hf_token = ''
device = torch.device("cuda")

processor = AutoProcessor.from_pretrained(
    model_name, token=hf_token
)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_name,
    token=hf_token,
    torch_dtype=torch.float16,
    mode='S'
).to(device)

# Load audio file
from datasets import load_dataset
dataset = load_dataset(
    "hf-internal-testing/librispeech_asr_dummy",
    "clean", split="validation"
)
audio_sample = dataset[0]["audio"]

# Process audio
input_features = processor(
    audio_sample["array"],
    sampling_rate=audio_sample["sampling_rate"],
    return_tensors="pt"
).input_features.to(device, dtype=torch.float16)

# Generate transcription
with torch.inference_mode():
    predicted_ids = model.generate(input_features)

transcription = processor.batch_decode(
    predicted_ids, skip_special_tokens=True
)[0]

print(f"Transcription: {transcription}")
```


## TheWhisper SpeechKit

---

TheWhisper can also be used via `thestage_speechkit` for NVIDIA and Apple Silicon inference from Python, including real-time streaming.

### Installation

```bash
# Install ffmpeg (required for audio processing)
# Ubuntu/Debian: apt install ffmpeg
# macOS: brew install ffmpeg
git clone https://github.com/TheStageAI/TheWhisper.git
cd TheWhisper
pip install .[nvidia]   # or pip install .[apple] for Apple Silicon
```

For TheStage AI optimized engines (NVIDIA only):

```bash
pip install thestage-elastic-models[nvidia] --extra-index-url https://thestage.jfrog.io/artifactory/api/pypi/pypi-thestage-ai-production/simple
```

### NVIDIA Usage

```python
from thestage_speechkit.nvidia import ASRPipeline

model = ASRPipeline(
    model='TheStageAI/thewhisper-large-v3-turbo',
    model_size='S',
    chunk_length_s=15,
    batch_size=32,
    device='cuda'
)

result = model(
    "path_to_your_audio.wav",
    chunk_length_s=15,
    generate_kwargs={'do_sample': False, 'num_beams': 1, 'use_cache': True}
)

print(result["text"])
```

### Apple Silicon Usage (Python)

> For shipping iOS / macOS apps, prefer the [TheStage Apple SDK](#thestage-apple-sdk) above. SpeechKit remains available for Python notebooks and macOS scripting.

```python
from thestage_speechkit.apple import ASRPipeline

model = ASRPipeline(
    model='TheStageAI/thewhisper-large-v3-turbo',
    model_size='S',
    chunk_length_s=10
)

result = model(
    "path_to_your_audio.wav",
    chunk_length_s=10,
    generate_kwargs={'do_sample': False, 'num_beams': 1, 'use_cache': True}
)

print(result["text"])
```

### Streaming

```python
from thestage_speechkit.streaming import StreamingPipeline, MicStream, StdoutStream

streaming_pipe = StreamingPipeline(
    model='TheStageAI/thewhisper-large-v3-turbo',
    model_size='S',
    chunk_length_s=15,
    platform='apple',
    language='en'
)

mic_stream = MicStream(step_size_s=0.5)
output_stream = StdoutStream()

while True:
    chunk = mic_stream.next_chunk()
    if chunk is not None:
        approved_text, assumption = streaming_pipe(chunk)
        output_stream.write(approved_text, assumption)
    else:
        break
```


## Quality Benchmarks

---

We have evaluated the models using the Hugging Face Open ASR Leaderboard methodology. For each model size (S, M, L, XL), we report Word Error Rate (WER) on standard English and multilingual speech recognition benchmarks.

![Quality Benchmarking](https://cdn.thestage.ai/production/cms_file_upload/1773836234-75d3e865-d537-475a-b991-fe8cda463108/TheWhisper_Large_Turbo_WER.png)

### Open ASR Leaderboard (English, WER %)

| **Dataset**| **S**| **M**| **L**| **XL**| **Original** |
 | ---  | ---  | ---  | ---  | ---  | ---  |
| **LibriSpeech Clean** | 1.83 | 1.8 | 1.74 | 1.73 | 1.71 |
| **LibriSpeech Other** | 3.77 | 3.76 | 3.75 | 3.72 | 3.63 |
| **SPGISpeech** | 1.92 | 1.93 | 1.92 | 1.88 | 1.88 |
| **TED-LIUM** | 3.37 | 3.3 | 3.29 | 3.25 | 3.33 |
| **VoxPopuli** | 7.37 | 6.36 | 6.34 | 6.71 | 6.28 |
| **GigaSpeech** | 9.56 | 9.54 | 9.53 | 9.48 | 9.51 |
| **Earnings-22** | 11.57 | 11.15 | 11.09 | 11.21 | 10.89 |
| **AMI** | 9.6 | 9.35 | 9.38 | 9.14 | 9.2 |
| **Mean WER** | 6.12 | 5.9 | 5.88 | 5.89 | 5.8 |


### Multilingual (WER %)

| **Dataset**| **S**| **M**| **L**| **XL**| **Original** |
 | ---  | ---  | ---  | ---  | ---  | ---  |
| **CoVoST2 DE** | 4.47 | 4.44 | 4.38 | 4.32 | 4.34 |
| **CoVoST2 ES** | 3.41 | 3.4 | 3.35 | 3.33 | 3.3 |
| **CoVoST2 FR** | 6.09 | 6.09 | 6.01 | 5.95 | 6.01 |
| **CoVoST2 IT** | 3.81 | 3.66 | 3.64 | 3.74 | 3.71 |
| **CoVoST2 PT** | 2.08 | 2.02 | 2.0 | 1.97 | 2.02 |
| **FLEURS DE** | 4.62 | 4.66 | 4.66 | 4.5 | 4.36 |
| **FLEURS ES** | 3.25 | 3.16 | 3.15 | 3.04 | 2.98 |
| **FLEURS FR** | 5.18 | 5.15 | 5.27 | 5.25 | 4.99 |
| **FLEURS IT** | 3.21 | 3.26 | 3.43 | 3.45 | 2.82 |
| **FLEURS PT** | 4.81 | 4.78 | 4.7 | 4.7 | 4.55 |
| **MLS French** | 4.67 | 4.54 | 4.48 | 4.31 | 3.77 |
| **MLS German** | 4.28 | 4.16 | 4.19 | 4.12 | 3.77 |
| **MLS Italian** | 6.89 | 7.01 | 7.11 | 7.36 | 6.12 |
| **MLS Portuguese** | 5.69 | 5.53 | 5.34 | 6.3 | 4.56 |
| **MLS Spanish** | 2.93 | 2.84 | 2.71 | 2.85 | 2.51 |
| **Mean WER** | 4.36 | 4.31 | 4.29 | 4.35 | 3.99 |


## Datasets

---

### English (Open ASR Leaderboard)

- **LibriSpeech Clean**: Read English speech from audiobooks, recorded in clean conditions. Tests baseline transcription accuracy on clear, well-articulated speech.
- **LibriSpeech Other**: Read English speech from audiobooks with more challenging acoustic conditions, including noisier recordings and less common speakers.
- **SPGISpeech**: Financial earnings calls and presentations, featuring domain-specific terminology, spontaneous speech, and diverse speaker accents.
- **TEDLium**: TED conference talks covering a wide range of topics, with diverse speakers, presentation styles, and varying audio quality.
- **VoxPopuli**: European Parliament event recordings in multiple languages, featuring political discourse, formal speech, and multilingual speakers.
- **GigaSpeech**: Large-scale multi-domain English speech corpus from audiobooks, podcasts, and YouTube, representing diverse acoustic conditions and speaking styles.
- **Earnings22**: Corporate earnings calls with financial terminology, multiple speakers, and telephone-quality audio.
- **AMI**: Meeting recordings with overlapping speech, distant microphones, and natural conversational dynamics.

### Multilingual

- **CoVoST2**: Common Voice Speech-To-Text 2. Built on Mozilla's Common Voice recordings, providing speech-to-text evaluation across 21 languages with diverse speakers, accents, and recording conditions.
- **FLEURS**: Few-shot Learning Evaluation of Universal Representations of Speech. Covers 102 languages with read speech from Wikipedia passages.
- **MLS**: Multilingual LibriSpeech. Derived from read audiobooks in 8 languages, providing large-scale multilingual ASR evaluation data.

## Metrics

---

- **WER (Word Error Rate)**: Measures the proportion of word-level errors (substitutions, insertions, deletions) in the transcription compared to the reference text. Lower values indicate better accuracy.


## Latency Benchmarks

---

We measured RTFx (Real-Time Factor) for each model size on various GPUs. RTFx indicates how many times faster than real-time the model transcribes audio. Higher RTFx is better.

![Latency Benchmarking](https://cdn.thestage.ai/production/cms_file_upload/1779128584-7ceaab51-c442-42d1-a3dc-a329ebb3cceb/TheWhisper_Large_Turbo_RTF_h100.png)

### RTFx, batch size 1

| **GPU/Model Size**| **S**| **M**| **L**| **XL**| **Original** |
 | ---  | ---  | ---  | ---  | ---  | ---  |
| **H100** | 304.4 | 304.1 | 295.7 | 285.2 | 109.2 |
| **L40s** | 247.5 | 239.6 | 239.6 | 221.2 | 81.8 |
| **GeForce RTX 5090** | 280 | 280 | 280 | 262 | 114 |
| **GeForce RTX 4090** | 250.3 | 250.3 | 250.3 | 250.3 | 157.6 |


### RTFx, batched

| **GPU/Model Size**| **S**| **M**| **L**| **XL**| **Original** |
 | ---  | ---  | ---  | ---  | ---  | ---  |
| **RTX 4090 (bs=24)** | 895 | 880 | 871 | 790 | 702 |
| **L40s (bs=32)** | 989 | 989 | 955 | 926 | 539 |
| **RTX 5090 (bs=32)** | 1319 | 1302 | 1205 | 1205 | 484 |
| **H100 (bs=64)** | 2033 | 2022 | 2019 | 2019 | 967 |


## Benchmarking Methodology

---

The benchmarking was performed on a single GPU using a 10-minute audio file resampled to 16kHz mono. RTFx (Real-Time Factor) is calculated as `audio_duration / transcription_time` — higher values mean faster-than-real-time transcription.

> **Algorithm summary:**
> 1. Load the thewhisper-large-v3-turbo model with the specified size (S, M, L, XL, original).
> 2. Load a 10-minute audio file and resample to 16kHz mono.
> 3. Run a warm-up pass to initialize GPU caches.
> 4. Synchronize the GPU, record the start time.
> 5. Run the transcription pipeline with the specified batch size and chunk length.
> 6. Synchronize the GPU, record the end time.
> 7. Calculate RTFx as `audio_duration / time_taken`.


## Serving with Docker Image

---

For serving with Nvidia GPUs, we provide ready-to-go Docker containers with OpenAI-compatible API endpoints.
Using our containers you can set up an inference endpoint on any desired cloud/serverless providers as well as on-premise servers.
You can also use this container to run inference through TheStage AI platform.

### Prebuilt image from ECR

Pull docker image and start inference container:

```bash
docker pull public.ecr.aws/i3f7g5s7/thestage/elastic-models:0.2.1.post0-stt-streaming-24.09a
```


```bash
docker run --rm -it \
  --name triton-stt \
  --gpus all \
  -p 127.0.0.1:80:80 \
  -v "$HOME/.cache:/opt/project/.cache/" \
  -e MODEL_REPO=TheStageAI/thewhisper-large-v3-turbo \
  -e MODEL_SIZE=<MODEL_SIZE> \
  -e MODEL_BATCH=<MODEL_BATCH> \
  -e PIPELINE_MAX_BATCH_SIZE=<PIPELINE_MAX_BATCH_SIZE> \
  -e CHUNK_LENGTH=<CHUNK_LENGTH> \
  -e PREPROCESSOR_WORKERS=<PREPROCESSOR_WORKERS> \
  -e MODEL_INSTANCES=<MODEL_INSTANCES> \
  -e PREPROCESSOR_QUEUE_DELAY=<PREPROCESSOR_QUEUE_DELAY> \
  -e MODEL_QUEUE_DELAY=<MODEL_QUEUE_DELAY> \
  -e ENSEMBLE_QUEUE_DELAY=<ENSEMBLE_QUEUE_DELAY> \
  -e HUGGINGFACE_ACCESS_TOKEN=<HUGGINGFACE_ACCESS_TOKEN> \
  -e THESTAGE_AUTH_TOKEN=<THESTAGE_ACCESS_TOKEN> \
  public.ecr.aws/i3f7g5s7/thestage/elastic-models:0.2.1.post0-stt-streaming-24.09a
```

| **Parameter**              | **Description**                                                                                      |
|----------------------------|------------------------------------------------------------------------------------------------------|
| `<MODEL_SIZE>`             | Available: S, M, L, XL.                                                                              |
| `<MODEL_BATCH>`            | Maximum batch size for the model.                                                                    |
| `<PIPELINE_MAX_BATCH_SIZE>` | Maximum batch size for the ASR pipeline processing.                                                 |
| `<CHUNK_LENGTH>`           | Audio chunk length in seconds (e.g., 10, 15, 20, 30).                                                |
| `<PREPROCESSOR_WORKERS>`   | Number of preprocessor worker processes (e.g., 8).                                                   |
| `<MODEL_INSTANCES>`        | Number of Triton model instances (e.g., 1).                                                          |
| `<PREPROCESSOR_QUEUE_DELAY>` | Preprocessor dynamic-batching queue delay in microseconds (e.g., 10000).                           |
| `<MODEL_QUEUE_DELAY>`      | Model dynamic-batching queue delay in microseconds (e.g., 10000).                                    |
| `<ENSEMBLE_QUEUE_DELAY>`   | Ensemble dynamic-batching queue delay in microseconds (e.g., 10000).                                 |
| `<HUGGINGFACE_ACCESS_TOKEN>` | Hugging Face access token.                                                                         |
| `<THESTAGE_ACCESS_TOKEN>`  | TheStage token generated on the platform (Profile -> Access tokens).                                 |

## Invocation

---

### CLI

```bash
elastic-models-client client stt --sample sample.wav --lang-id en
```

### cURL

```bash
curl -X POST http://127.0.0.1:80/v1/audio/transcriptions \
    -H "Authorization: Bearer 123" \
    -H "X-Lang-Id: en" \
    -H "X-Model-Name: thewhisper-large-v3-turbo-<MODEL_SIZE_LOWER>-cl<CHUNK_LENGTH>-bs<MODEL_BATCH>" \
    -F "file=@sample.wav"
```

## Endpoint Parameters

---

### Method

> **POST** `/v1/audio/transcriptions`

### Header Parameters

> `Authorization`: `string`
>
> Bearer token for authentication.

> `X-Lang-Id`: `string`
>
> Language of the audio (e.g., "en", "es", "fr").

> `X-Model-Name`: `string`
>
> Specifies the model to use for transcription. Format: `thewhisper-large-v3-turbo-<size>-cl<chunk_length>-bs<batch_size>`, where `<size>` is the lowercase letter (`s`, `m`, `l`, `xl`), `<chunk_length>` is `CHUNK_LENGTH`, and `<batch_size>` is `MODEL_BATCH`. Example: `thewhisper-large-v3-turbo-s-cl15-bs1`.

### Input Body

> `file` : `binary`
>
> The audio file to transcribe (multipart/form-data).


## Acknowledgments

---

This work builds on **Whisper Large V3 Turbo** by OpenAI: [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo).

TheWhisper builds on OpenAI Whisper Large V3 Turbo. Optimized and packaged by TheStage AI for ElasticModels / NVIDIA and TheStage Apple SDK.

## Links

---


* __Original model__: [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo)
* __Platform__: [app.thestage.ai](https://app.thestage.ai)
* __TheStage Apple SDK__: [github.com/TheStageAI/AppleSDK](https://github.com/TheStageAI/AppleSDK)
* __TheWhisper__: [github.com/TheStageAI/TheWhisper](https://github.com/TheStageAI/TheWhisper)
* __Subscribe for updates__: [TheStageAI X](https://x.com/TheStageAI)
* __Contact email__: contact@thestage.ai
