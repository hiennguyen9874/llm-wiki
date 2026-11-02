---
license: other
license_name: openmdw-1.1
license_link: >-
  https://github.com/OpenMDW/OpenMDW/blob/main/1.1/LICENSE.OpenMDW-1.1
library_name: nemo
datasets:
  - nvidia/Granary
  - YTC
  - Yodas2
  - LibriLight
  - librispeech_asr
  - fisher_corpus
  - Switchboard-1
  - WSJ-0
  - WSJ-1
  - National-Singapore-Corpus-Part-1
  - National-Singapore-Corpus-Part-6
  - vctk
  - voxpopuli
  - europarl
  - multilingual_librispeech
  - fleurs
  - mozilla-foundation/common_voice_8_0
  - MLCommons/peoples_speech
  - google/speech_commands
thumbnail: null
tags:
  - speech-recognition
  - unified-asr
  - offline-asr
  - streaming-asr
  - automatic-speech-recognition
  - speech
  - audio
  - FastConformer
  - RNNT
  - Parakeet
  - ASR
  - pytorch
  - NeMo
widget:
  - example_title: Librispeech sample 1
    src: https://cdn-media.huggingface.co/speech_samples/sample1.flac
  - example_title: Librispeech sample 2
    src: https://cdn-media.huggingface.co/speech_samples/sample2.flac
model-index:
  - name: nemotron-labs-unified-asr-0.6b
    results:
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: AMI (cleaned)
          type: ami
          config: ihm
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 7.91
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Earnings22 (cleaned, AA-chunked)
          type: earnings22
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 6.96
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: GigaSpeech (cleaned)
          type: gigaspeech
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 8.23
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: LibriSpeech test-clean
          type: librispeech_asr
          config: clean
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 1.38
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: LibriSpeech test-other
          type: librispeech_asr
          config: other
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 2.81
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: SPGI Speech
          type: spgispeech
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 2.04
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: VoxPopuli (cleaned)
          type: voxpopuli
          config: en
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 3.41
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: AMI (cleaned)
          type: ami
          config: ihm
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 8.47
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Earnings22 (cleaned, AA-chunked)
          type: earnings22
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 9.65
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: GigaSpeech (cleaned)
          type: gigaspeech
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 8.70
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: LibriSpeech test-clean
          type: librispeech_asr
          config: clean
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 1.49
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: LibriSpeech test-other
          type: librispeech_asr
          config: other
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 3.59
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: SPGI Speech
          type: spgispeech
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 2.28
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: VoxPopuli (cleaned)
          type: voxpopuli
          config: en
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 3.67
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (German)
          type: google/fleurs
          config: de
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 3.87
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (French)
          type: google/fleurs
          config: fr
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 5.28
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (Italian)
          type: google/fleurs
          config: it
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 2.30
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (Spanish)
          type: google/fleurs
          config: es
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 3.00
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (Portuguese)
          type: google/fleurs
          config: pt
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 4.42
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (German)
          type: common_voice
          config: de
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 4.77
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (French)
          type: common_voice
          config: fr
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 6.92
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (Italian)
          type: common_voice
          config: it
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 3.62
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (Spanish)
          type: common_voice
          config: es
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 3.97
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (Portuguese)
          type: common_voice
          config: pt
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 4.06
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (French)
          type: facebook/multilingual_librispeech
          config: fr
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 4.40
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (Italian)
          type: facebook/multilingual_librispeech
          config: it
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 7.07
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (Spanish)
          type: facebook/multilingual_librispeech
          config: es
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 3.87
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (Portuguese)
          type: facebook/multilingual_librispeech
          config: pt
          split: test
        metrics:
          - name: WER (offline)
            type: wer
            value: 7.05
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (German)
          type: google/fleurs
          config: de
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 5.24
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (French)
          type: google/fleurs
          config: fr
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 6.90
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (Italian)
          type: google/fleurs
          config: it
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 2.98
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (Spanish)
          type: google/fleurs
          config: es
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 4.63
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: FLEURS (Portuguese)
          type: google/fleurs
          config: pt
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 4.98
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (German)
          type: common_voice
          config: de
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 5.65
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (French)
          type: common_voice
          config: fr
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 7.61
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (Italian)
          type: common_voice
          config: it
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 4.33
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (Spanish)
          type: common_voice
          config: es
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 4.53
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Mozilla Common Voice (Portuguese)
          type: common_voice
          config: pt
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 5.15
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (French)
          type: facebook/multilingual_librispeech
          config: fr
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 6.36
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (Italian)
          type: facebook/multilingual_librispeech
          config: it
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 8.38
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (Spanish)
          type: facebook/multilingual_librispeech
          config: es
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 4.42
      - task:
          name: Automatic Speech Recognition
          type: automatic-speech-recognition
        dataset:
          name: Multilingual LibriSpeech (Portuguese)
          type: facebook/multilingual_librispeech
          config: pt
          split: test
        metrics:
          - name: WER (1.12s latency)
            type: wer
            value: 8.45
metrics:
  - wer
pipeline_tag: automatic-speech-recognition
---

# Nemotron-Labs-Unified-ASR-0.6b: Unified ASR model for offline and streaming multilingual inference

<figure align="center">
  <img src="figures/unified_scheme.png" width="1250" />
</figure>

Nemotron-Labs-Unified-ASR-0.6b is the multilingual version of [Parakeet-unified-en-0.6b](https://huggingface.co/nvidia/parakeet-unified-en-0.6b) — a unified automatic speech recognition (ASR) model that combines offline and streaming inference (with a minimum algorithmic latency of 160ms) in a single model [1]. It extends the English-only unified model to **25 European languages**, and is trained primarily on the [Granary](https://huggingface.co/datasets/nvidia/Granary) dataset [5], [6] using the same training data composition as [parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3). The model transcribes speech with punctuation and capitalization support, and uses **language-ID prompt conditioning** on the encoder to select the target language at inference time. <br>

In our evaluation setup, the new unified model outperforms [parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) in offline mode and [nemotron-3.5-asr-streaming-0.6b](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b) in most streaming scenarios with algorithmic latency down to 160ms (see [Comparison with already released models](#comparison-with-already-released-models)).

<figure align="center">
  <img src="figures/unified_asr_comparison.png" width="1250" />
</figure>

The new unified model also serves as a strong ASR front end for cascaded streaming speech translation (see [Streaming Speech Translation](#streaming-speech-translation-asr--llm-cascade)). <br>

<figure align="center">
  <img src="figures/unified_cascaded_ast.png" width="1250" />
</figure>

Key capabilities:
* **One multilingual checkpoint for both tasks:** a single unified model covers both offline and streaming inference with a minimum latency of 160ms across 25 European languages.
* **Language-ID prompting:** the target language is passed to the encoder as a prompt, which stabilizes language selection in low-latency streaming. An automatic language mode (`target_lang=auto`) is also supported.
* **Streaming chunk size flexibility:** the streaming latency (chunk + right context) is configurable from 2080ms down to 160ms in steps of 80ms, without re-training.
* **Punctuation & Capitalization:** built-in support for punctuation and capitalization in the output text.
* **Speech translation front end:** the right context lets the current chunk use upcoming audio before the transcript is committed, which gives the LLM of a cascaded speech translation system a more accurate source transcript.

**Supported Languages:** <br>
Bulgarian (**bg**), Croatian (**hr**), Czech (**cs**), Danish (**da**), Dutch (**nl**), English (**en**), Estonian (**et**), Finnish (**fi**), French (**fr**), German (**de**), Greek (**el**), Hungarian (**hu**), Italian (**it**), Latvian (**lv**), Lithuanian (**lt**), Maltese (**mt**), Polish (**pl**), Portuguese (**pt**), Romanian (**ro**), Slovak (**sk**), Slovenian (**sl**), Spanish (**es**), Swedish (**sv**), Russian (**ru**), Ukrainian (**uk**) <br>

### License/Terms of Use:
GOVERNING TERMS: Use of this model is governed by the [OpenMDW License Agreement, Version 1.1](https://github.com/OpenMDW/OpenMDW/blob/main/1.1/LICENSE.OpenMDW-1.1).

This model is ready for commercial/non-commercial use.

### Deployment Geography:
Global <br>

### Use Case: <br>
This model can be used to transcribe multilingual speech (25 European languages) into text using offline or streaming inference with latency as low as 160ms. It supports a variety of applications, such as voice assistants, live captioning, conversational bots, subtitle generation, and, combined with an LLM translator, streaming speech translation. <br>

### Release Date:  <br>
Hugging Face [10/27/26](https://huggingface.co/nvidia/nemotron-labs-unified-asr-0.6b) <br>

## Model Architecture:
**Architecture Type:** Unified-FastConformer-RNNT with language-ID prompt [1], [2] — an optimized version of the Conformer model [4] with 8x depthwise-separable convolutional downsampling and RNNT loss.<br>

**Network Architecture:** <br>
* Encoder: Unified FastConformer with 24 layers
* Decoder: RNNT (Recurrent Neural Network Transducer)
* Language conditioning: language-ID prompt fused into the encoder output
* Parameters: 600M

### Model Initialization
The encoder was initialized from the [parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) model to give the unified model strong multilingual acoustic representations from the beginning of training. <br>

### Unified offline/streaming training
The model was trained jointly in offline and streaming modes. In the offline mode we use standard offline training with full-context self-attention and non-causal convolutions. In the streaming mode we apply chunked self-attention masks (left, middle/chunk and right context) together with Dynamic Chunked Convolutions inside each FastConformer layer [3] to adapt the model to both decoding scenarios. We also use a mode-consistency regularization (MCR) loss [1] to further reduce the gap between offline and streaming performance. All model parameters are shared between offline and streaming modes (encoder, predictor, and joint networks), including the initial x8 subsampling with non-causal convolutions. <br>

### Language-ID prompting
The model uses **language-ID prompt conditioning on the encoder**, following the approach used in [nemotron-3.5-asr-streaming-0.6b](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b). The language prompt is fused with the acoustic representation as follows: <br>

* The **FastConformer encoder** processes audio into an acoustic embedding of shape `(D, T)`.
* The **language encoding** expands a one-hot language vector across the time axis → `(K, T)`, broadcasting the language identity to every frame.
* **Concatenation** along the feature axis produces a fused tensor `(D + K, T)`.
* A **projection layer** maps the fused features to the RNNT decoder.

**Why the prompt is needed.** The model uses a single shared SentencePiece tokenizer built from the combined transcripts of all 25 languages, so the tokenizer itself carries no language information and the output token space is shared across languages. In low-latency streaming configurations (latency ≈ chunk + right context ≤ 560ms), the first chunks do not contain enough speech for the model to reliably infer the spoken language, so it can begin emitting tokens belonging to a different language. The model typically self-corrects once enough audio has been accumulated, but the initial tokens are already emitted and cannot be revised. Passing the language ID as a prompt removes this ambiguity from the first chunk onward and makes the transcription language deterministic. In offline mode and at higher streaming latencies the effect is much smaller, since the model has sufficient acoustic context to identify the language on its own. <br>

**Automatic language mode.** When the spoken language is not known in advance, pass `target_lang=auto` (the language-agnostic prompt) for a language-agnostic inference. For low-latency streaming we recommend passing the language explicitly, for the reason above. All results in this card are obtained with the explicit language prompt. <br>

### Setting up Streaming Configuration
Algorithmic latency is defined as the sum of the chunk size (middle part) and the right context. For the left context we use 5.6s by default (5.6s was used during model training), but other values can be explored for a better accuracy/speed trade-off. Recommended context parameters for different latencies: <br>

| Left, s | Chunk, s | Right, s | Latency (C+R), s |
| ------- | -------- | -------- | ---------------- |
| 5.6     | 1.04     | 1.04     | 2.08             |
| 5.6     | 0.56     | 0.56     | 1.12             |
| 5.6     | 0.16     | 0.40     | 0.56             |
| 5.6     | 0.08     | 0.24     | 0.32             |
| 5.6     | 0.08     | 0.16     | 0.24             |
| 5.6     | 0.08     | 0.08     | 0.16             |

The model is quite flexible in terms of context sizes: the values above are recommendations, and other combinations of left context, chunk and right context can be chosen depending on the application. We recommend not decreasing the left context below 2s, as accuracy starts to degrade noticeably beyond that point. <br>

### Streaming Inference Limitation
The current streaming inference pipeline is **buffered**, not cache-aware: the left context is recomputed at every chunk step. Standard NVIDIA streaming ASR models use a cache-aware architecture with causal convolutions and no right context, which allows encoder states to be cached and reused across chunks. The unified model instead relies on non-causal convolutions and a right context to reach its offline accuracy, so the left context has to be recomputed at each step in order to keep training and inference conditions matched. Cache-aware decoding is technically possible with this model, but it breaks that match and leads to accuracy degradation. Fine-tuning the model with zero right context would enable cache-aware decoding, at the cost of the state-of-the-art offline performance that is the main advantage of the unified model. As a result, buffered streaming is computationally more expensive than cache-aware streaming at the same latency. To accelerate the streaming inference, one can reduce the left context to about 3-2s with possible accuracy degradation. <br>

# NVIDIA NeMo Framework

## How to Use this Model

For now, we provide only inference support for the unified model.

### Loading the Model

```python
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/nemotron-labs-unified-asr-0.6b")
```

### Offline Inference

Pass the language of the audio with `target_lang` (e.g. `"de"` for German, `"bg"` for Bulgarian), or `target_lang="auto"` to let the model identify it:

```python
output = asr_model.transcribe([wav_file_path], target_lang="de")
print(output[0].text)
```

### Streaming Inference

For streaming inference you can use the stateful chunked RNN-T decoding script from NeMo - [NeMo/examples/asr/asr_chunked_inference/rnnt/speech_to_text_streaming_infer_rnnt.py](https://github.com/NVIDIA-NeMo/Speech/blob/main/examples/asr/asr_chunked_inference/rnnt/speech_to_text_streaming_infer_rnnt.py). The left context, chunk and right context are given in seconds (5.6s / 0.56s / 0.56s for 1.12s latency); `att_context_size_as_chunk=true` enables the chunked self-attention masks; `target_lang` is the language ID (e.g. `en`, `bg`, or `auto`):

```bash
cd NeMo
python examples/asr/asr_chunked_inference/rnnt/speech_to_text_streaming_infer_rnnt.py \
    model_path=<model_path> \
    dataset_manifest=<dataset_manifest> \
    output_filename=<output_json_file> \
    left_context_secs=5.6 \
    chunk_secs=0.56 \
    right_context_secs=0.56 \
    att_context_size_as_chunk=true \
    target_lang=<language_id> \
    batch_size=<batch_size>
```

You can also run streaming inference through the pipeline method, which uses [NeMo/examples/asr/conf/asr_streaming_inference/buffered_rnnt.yaml](https://github.com/NVIDIA-NeMo/Speech/blob/main/examples/asr/conf/asr_streaming_inference/buffered_rnnt.yaml) configuration file to build end‑to‑end workflows with punctuation and capitalization (PnC), inverse text normalization (ITN), and translation support.

```python
from nemo.collections.asr.inference.factory.pipeline_builder import PipelineBuilder
from omegaconf import OmegaConf
# Path to the buffered rnnt config file downloaded from above link
cfg_path = 'buffered_rnnt.yaml'
cfg = OmegaConf.load(cfg_path)
cfg.asr.model_name = "nvidia/nemotron-labs-unified-asr-0.6b"
cfg.lang = "de"  # language ID of the audio
# Pass the paths of all the audio files for inferencing
audios = ['/path/to/your/audio.wav']
# Create the pipeline object and run inference
pipeline = PipelineBuilder.build_pipeline(cfg)
output = pipeline.run(audios)
# Print the output
for entry in output.values():
  print(entry['text'])
```

---

## Input: <br>
**Input Type(s):** Audio, Language ID <br>
**Input Format:** Audio waveform (wav), string (language ID) <br>
**Input Parameters:** One-Dimensional (1D) for audio, One-Dimensional (1D) for language ID <br>
**Other Properties Related to Input:** Single-channel audio at 16kHz sampling rate, at least 80ms duration is required. The language ID selects the target transcription language from the 25 supported languages. <br>


## Output: <br>
**Output Type(s):** Text String in the prompted language <br>
**Output Format:** String <br>
**Output Parameters:** One-Dimensional (1D) <br>
**Other Properties Related to Output:** The output text includes punctuation and capitalization. The output text might be empty if the input audio doesn't contain any speech. <br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions. <br>

## Software Integration:
**Runtime Engine(s):**
* NeMo Speech 3.1.0 <br>

**Supported Hardware Microarchitecture Compatibility:** <br>
* NVIDIA Ampere <br>
* NVIDIA Blackwell <br>
* NVIDIA Hopper  <br>
* NVIDIA Volta  <br>

**Preferred/Supported Operating System(s):**
* Linux <br>

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. <br>


## Model Version(s):
* Nemotron-Labs-Unified-ASR-0.6b-v1 <br>


## Training, Testing, and Evaluation Datasets:
## Training Dataset:

The model was trained on the combination of the [Granary dataset's ASR subset](https://huggingface.co/datasets/nvidia/Granary) [5], [6] and the in-house NeMo ASR Set 3.0, covering 25 European languages:

- 10,000 hours from human-transcribed NeMo ASR Set 3.0, including:
  - LibriSpeech (960 hours)
  - Fisher Corpus
  - National Speech Corpus Part 1
  - VCTK
  - Mozilla Common Voice (v7.0)
  - AMI

- 660,000 hours of pseudo-labeled data from Granary [5], [6], including:
  - YTC (YouTube-Commons)
  - MOSEL
  - YODAS

All transcriptions preserve punctuation and capitalization. Dataset corpora and languages were balanced using temperature sampling. A unified SentencePiece tokenizer, constructed from the training transcripts of all 25 supported languages, is shared across languages.

- Data Modality:
  - Audio and text

- Audio Training Data Size:
  - [10,000 to 1 Million Hours]

- Text Training Data Size:
  - Less than a Billion Tokens

- Data Collection Method:
  - [Hybrid: Automated, Manually-Collected]

- Labeling Method:
  - [Hybrid: Manually-Labeled, Synthetic] - Some transcripts are generated by ASR models, while some are manually labeled

**Properties:**

Number of data items: about 670k hours of audio data <br>
Modality: Audio <br>
Nature of the content: Personal data and machine generated data <br>
Language: 25 European languages (bg, cs, da, de, el, en, es, et, fi, fr, hr, hu, it, lt, lv, mt, nl, pl, pt, ro, ru, sk, sl, sv, uk) <br>


### Testing Dataset:

- FLEURS (25 languages)
- Mozilla Common Voice (MCV, 13 languages)
- Multilingual LibriSpeech (MLS, 6 languages)
- HuggingFace Open ASR Leaderboard (English), cleaned versions of the test sets:
    - AMI (cleaned)
    - Earnings22 (cleaned, AA-chunked, scored per call)
    - GigaSpeech (cleaned)
    - LibriSpeech test-clean
    - LibriSpeech test-other
    - SPGISpeech
    - VoxPopuli (cleaned)


- Data Collection Method <br>
  - [Manually-Collected] - All audios are human recorded<br>


- Labeling Method <br>
  - [Hybrid: Manually-Labeled, Synthetic]  - Some transcripts are generated by ASR models, while some are manually labeled <br>

**Properties:**

Modality: Audio <br>
Nature of the content: Personal data and machine generated data <br>
Language: 25 European languages <br>


### Evaluation Dataset:

- FLEURS (25 languages)
- Mozilla Common Voice (MCV, 13 languages)
- Multilingual LibriSpeech (MLS, 6 languages)
- HuggingFace Open ASR Leaderboard (English), cleaned versions of the test sets:
    - AMI (cleaned)
    - Earnings22 (cleaned, AA-chunked, scored per call)
    - GigaSpeech (cleaned)
    - LibriSpeech test-clean
    - LibriSpeech test-other
    - SPGISpeech
    - VoxPopuli (cleaned)


- Data Collection Method:
  - [Manually-Collected] - All audios are human recorded


- Labeling Method:
  - [Manually-Labeled]


## ASR Performance

ASR performance is measured using word error rate (WER, %, lower is better). Both reference and predicted text
are processed with a text normalizer before scoring. The unified model uses a 5.6s left context in streaming
mode, and all results use an explicit language-ID prompt. Latency is the sum of chunk and right-context sizes.
The cache-aware Nemotron 3.5 baseline uses its equivalent algorithmic latency. The figure at the
[top of this card](#nemotron-labs-unified-asr-06b-unified-asr-model-for-offline-and-streaming-multilingual-inference) plots these results as WER versus latency.

### Comparison with already released models

The multilingual HF subset comprises German, French, Italian, Spanish and Portuguese. The 25-language result
uses all available FLEURS, MCV and MLS evaluations (44 dataset-language runs).

<table>
  <thead>
    <tr><th rowspan="2" align="left">Evaluation suite</th><th rowspan="2" align="left">Model</th><th colspan="1" align="center" style="background-color:#6b7280;color:#ffffff;">Offline</th><th colspan="4" align="center" style="background-color:#76b900;color:#ffffff;border-left:2px solid #cbd5e1;">Streaming, latency = chunk + right context</th></tr>
    <tr><th align="center" style="background-color:rgba(107,114,128,0.12);">full context</th><th align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">1.12s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.56s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.32s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.16s</th></tr>
  </thead>
  <tbody>
    <tr><td rowspan="3" align="left"><strong>English, 7 cleaned sets</strong></td><td align="left">parakeet-tdt-0.6b-v3</td><td align="center" style="background-color:rgba(107,114,128,0.12);">4.93</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">32.31</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td></tr>
    <tr><td align="left">nemotron-3.5-asr-streaming-0.6b</td><td align="center" style="background-color:rgba(107,114,128,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">7.26</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.58</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.97</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.90</td></tr>
    <tr><td align="left"><strong>nemotron-labs-unified-asr-0.6b</strong></td><td align="center" style="background-color:rgba(107,114,128,0.12);"><strong>4.68</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;"><strong>5.41</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>5.68</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>6.27</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>7.87</strong></td></tr>
    <tr><td rowspan="3" align="left"><strong>Multilingual HF, 14 runs</strong></td><td align="left">parakeet-tdt-0.6b-v3</td><td align="center" style="background-color:rgba(107,114,128,0.12);">4.68</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">27.14</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td></tr>
    <tr><td align="left">nemotron-3.5-asr-streaming-0.6b</td><td align="center" style="background-color:rgba(107,114,128,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">7.22</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.60</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.01</td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>8.53</strong></td></tr>
    <tr><td align="left"><strong>nemotron-labs-unified-asr-0.6b</strong></td><td align="center" style="background-color:rgba(107,114,128,0.12);"><strong>4.61</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;"><strong>5.69</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>6.36</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>7.27</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);">9.95</td></tr>
    <tr><td rowspan="3" align="left"><strong>All 25 languages, 44 runs</strong></td><td align="left">parakeet-tdt-0.6b-v3</td><td align="center" style="background-color:rgba(107,114,128,0.12);">10.55</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">30.93</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);">-</td></tr>
    <tr><td align="left">nemotron-3.5-asr-streaming-0.6b</td><td align="center" style="background-color:rgba(107,114,128,0.12);">-</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">20.00</td><td align="center" style="background-color:rgba(118,185,0,0.12);">20.91</td><td align="center" style="background-color:rgba(118,185,0,0.12);">21.81</td><td align="center" style="background-color:rgba(118,185,0,0.12);">22.77</td></tr>
    <tr><td align="left"><strong>nemotron-labs-unified-asr-0.6b</strong></td><td align="center" style="background-color:rgba(107,114,128,0.12);"><strong>9.49</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;"><strong>11.85</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>13.25</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>15.24</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>19.19</strong></td></tr>
  </tbody>
</table>

### Multilingual Speech Recognition

Per-language WER is averaged over the available FLEURS, MCV and MLS datasets for that language. The average row
is the mean over all 44 dataset-language runs, the same as in the figure and the comparison table above; because
dataset availability differs by language, it is not the plain mean of the per-language rows.

_Languages are ordered by accuracy (lowest offline WER first)._

<table>
  <thead>
    <tr><th rowspan="2" align="left">Language</th><th colspan="1" align="center" style="background-color:#6b7280;color:#ffffff;">Offline</th><th colspan="4" align="center" style="background-color:#76b900;color:#ffffff;border-left:2px solid #cbd5e1;">Streaming, latency = chunk + right context</th></tr>
    <tr><th align="center" style="background-color:rgba(107,114,128,0.12);">full context</th><th align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">1.12s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.56s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.32s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.16s</th></tr>
  </thead>
  <tbody>
    <tr><td align="left">Spanish (es)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">3.61</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">4.53</td><td align="center" style="background-color:rgba(118,185,0,0.12);">4.94</td><td align="center" style="background-color:rgba(118,185,0,0.12);">5.38</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.15</td></tr>
    <tr><td align="left">German (de)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">4.32</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">5.45</td><td align="center" style="background-color:rgba(118,185,0,0.12);">6.30</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.47</td><td align="center" style="background-color:rgba(118,185,0,0.12);">10.01</td></tr>
    <tr><td align="left">Italian (it)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">4.33</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">5.23</td><td align="center" style="background-color:rgba(118,185,0,0.12);">5.86</td><td align="center" style="background-color:rgba(118,185,0,0.12);">6.82</td><td align="center" style="background-color:rgba(118,185,0,0.12);">9.47</td></tr>
    <tr><td align="left">Russian (ru)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">4.42</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">5.69</td><td align="center" style="background-color:rgba(118,185,0,0.12);">6.70</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.25</td><td align="center" style="background-color:rgba(118,185,0,0.12);">11.71</td></tr>
    <tr><td align="left">Portuguese (pt)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">5.18</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">6.19</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.10</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.45</td><td align="center" style="background-color:rgba(118,185,0,0.12);">12.26</td></tr>
    <tr><td align="left">French (fr)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">5.53</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">6.96</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.58</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.30</td><td align="center" style="background-color:rgba(118,185,0,0.12);">10.90</td></tr>
    <tr><td align="left">English (en)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">5.89</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">7.12</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.11</td><td align="center" style="background-color:rgba(118,185,0,0.12);">9.52</td><td align="center" style="background-color:rgba(118,185,0,0.12);">12.49</td></tr>
    <tr><td align="left">Polish (pl)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">6.01</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">7.09</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.84</td><td align="center" style="background-color:rgba(118,185,0,0.12);">9.27</td><td align="center" style="background-color:rgba(118,185,0,0.12);">11.89</td></tr>
    <tr><td align="left">Ukrainian (uk)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">7.67</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">9.27</td><td align="center" style="background-color:rgba(118,185,0,0.12);">10.41</td><td align="center" style="background-color:rgba(118,185,0,0.12);">12.19</td><td align="center" style="background-color:rgba(118,185,0,0.12);">15.76</td></tr>
    <tr><td align="left">Dutch (nl)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">7.79</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">9.07</td><td align="center" style="background-color:rgba(118,185,0,0.12);">10.09</td><td align="center" style="background-color:rgba(118,185,0,0.12);">11.61</td><td align="center" style="background-color:rgba(118,185,0,0.12);">15.20</td></tr>
    <tr><td align="left">Slovak (sk)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">8.90</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">11.76</td><td align="center" style="background-color:rgba(118,185,0,0.12);">13.39</td><td align="center" style="background-color:rgba(118,185,0,0.12);">15.21</td><td align="center" style="background-color:rgba(118,185,0,0.12);">17.93</td></tr>
    <tr><td align="left">Croatian (hr)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">9.39</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">12.05</td><td align="center" style="background-color:rgba(118,185,0,0.12);">13.93</td><td align="center" style="background-color:rgba(118,185,0,0.12);">17.11</td><td align="center" style="background-color:rgba(118,185,0,0.12);">21.20</td></tr>
    <tr><td align="left">Romanian (ro)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">9.44</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">12.18</td><td align="center" style="background-color:rgba(118,185,0,0.12);">13.41</td><td align="center" style="background-color:rgba(118,185,0,0.12);">15.17</td><td align="center" style="background-color:rgba(118,185,0,0.12);">19.65</td></tr>
    <tr><td align="left">Finnish (fi)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">10.55</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">11.70</td><td align="center" style="background-color:rgba(118,185,0,0.12);">12.77</td><td align="center" style="background-color:rgba(118,185,0,0.12);">14.36</td><td align="center" style="background-color:rgba(118,185,0,0.12);">18.35</td></tr>
    <tr><td align="left">Czech (cs)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">10.60</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">13.83</td><td align="center" style="background-color:rgba(118,185,0,0.12);">15.99</td><td align="center" style="background-color:rgba(118,185,0,0.12);">18.73</td><td align="center" style="background-color:rgba(118,185,0,0.12);">23.53</td></tr>
    <tr><td align="left">Bulgarian (bg)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">10.67</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">12.14</td><td align="center" style="background-color:rgba(118,185,0,0.12);">13.02</td><td align="center" style="background-color:rgba(118,185,0,0.12);">14.35</td><td align="center" style="background-color:rgba(118,185,0,0.12);">17.24</td></tr>
    <tr><td align="left">Greek (el)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">13.36</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">15.45</td><td align="center" style="background-color:rgba(118,185,0,0.12);">16.66</td><td align="center" style="background-color:rgba(118,185,0,0.12);">19.35</td><td align="center" style="background-color:rgba(118,185,0,0.12);">22.67</td></tr>
    <tr><td align="left">Estonian (et)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">13.45</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">15.45</td><td align="center" style="background-color:rgba(118,185,0,0.12);">16.82</td><td align="center" style="background-color:rgba(118,185,0,0.12);">18.88</td><td align="center" style="background-color:rgba(118,185,0,0.12);">24.66</td></tr>
    <tr><td align="left">Hungarian (hu)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">14.26</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">19.69</td><td align="center" style="background-color:rgba(118,185,0,0.12);">21.65</td><td align="center" style="background-color:rgba(118,185,0,0.12);">23.84</td><td align="center" style="background-color:rgba(118,185,0,0.12);">28.66</td></tr>
    <tr><td align="left">Swedish (sv)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">15.13</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">18.48</td><td align="center" style="background-color:rgba(118,185,0,0.12);">20.48</td><td align="center" style="background-color:rgba(118,185,0,0.12);">23.70</td><td align="center" style="background-color:rgba(118,185,0,0.12);">30.76</td></tr>
    <tr><td align="left">Danish (da)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">16.24</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">22.02</td><td align="center" style="background-color:rgba(118,185,0,0.12);">24.30</td><td align="center" style="background-color:rgba(118,185,0,0.12);">27.02</td><td align="center" style="background-color:rgba(118,185,0,0.12);">32.38</td></tr>
    <tr><td align="left">Maltese (mt)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">16.52</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">19.36</td><td align="center" style="background-color:rgba(118,185,0,0.12);">21.38</td><td align="center" style="background-color:rgba(118,185,0,0.12);">24.57</td><td align="center" style="background-color:rgba(118,185,0,0.12);">32.24</td></tr>
    <tr><td align="left">Lithuanian (lt)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">18.66</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">21.44</td><td align="center" style="background-color:rgba(118,185,0,0.12);">23.71</td><td align="center" style="background-color:rgba(118,185,0,0.12);">26.86</td><td align="center" style="background-color:rgba(118,185,0,0.12);">32.52</td></tr>
    <tr><td align="left">Slovenian (sl)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">20.95</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">26.63</td><td align="center" style="background-color:rgba(118,185,0,0.12);">30.02</td><td align="center" style="background-color:rgba(118,185,0,0.12);">36.02</td><td align="center" style="background-color:rgba(118,185,0,0.12);">41.88</td></tr>
    <tr><td align="left">Latvian (lv)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">21.93</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">31.87</td><td align="center" style="background-color:rgba(118,185,0,0.12);">36.42</td><td align="center" style="background-color:rgba(118,185,0,0.12);">40.92</td><td align="center" style="background-color:rgba(118,185,0,0.12);">47.48</td></tr>
    <tr><td align="left"><strong>Average (44 runs)</strong></td><td align="center" style="background-color:rgba(107,114,128,0.12);"><strong>9.49</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;"><strong>11.85</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>13.25</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>15.24</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>19.19</strong></td></tr>
  </tbody>
</table>

### English Speech Recognition (Hugging Face Open ASR Leaderboard)

These are the cleaned evaluation sets used for this release: cleaned AMI, GigaSpeech and VoxPopuli; AA-chunked
Earnings-22 scored per call; and the standard LibriSpeech and SPGISpeech sets. Therefore, this average is not
directly comparable with results computed on the older uncleaned suite. The 0.08s configuration uses a 0.08s
chunk and no right context. Without right context the model is less stable, so this configuration was evaluated
only for English and is not among the recommended settings.

<table>
  <thead>
    <tr><th rowspan="2" align="left">Dataset</th><th colspan="1" align="center" style="background-color:#6b7280;color:#ffffff;">Offline</th><th colspan="5" align="center" style="background-color:#76b900;color:#ffffff;border-left:2px solid #cbd5e1;">Streaming, latency = chunk + right context</th></tr>
    <tr><th align="center" style="background-color:rgba(107,114,128,0.12);">full context</th><th align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">1.12s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.56s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.32s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.16s</th><th align="center" style="background-color:rgba(118,185,0,0.12);">0.08s</th></tr>
  </thead>
  <tbody>
    <tr><td align="left">AMI (cleaned)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">7.91</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">8.47</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.95</td><td align="center" style="background-color:rgba(118,185,0,0.12);">9.50</td><td align="center" style="background-color:rgba(118,185,0,0.12);">11.31</td><td align="center" style="background-color:rgba(118,185,0,0.12);">13.60</td></tr>
    <tr><td align="left">Earnings22 (AA-chunked)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">6.96</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">9.65</td><td align="center" style="background-color:rgba(118,185,0,0.12);">10.48</td><td align="center" style="background-color:rgba(118,185,0,0.12);">12.12</td><td align="center" style="background-color:rgba(118,185,0,0.12);">15.48</td><td align="center" style="background-color:rgba(118,185,0,0.12);">17.73</td></tr>
    <tr><td align="left">GigaSpeech (cleaned)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">8.23</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">8.70</td><td align="center" style="background-color:rgba(118,185,0,0.12);">8.95</td><td align="center" style="background-color:rgba(118,185,0,0.12);">9.28</td><td align="center" style="background-color:rgba(118,185,0,0.12);">10.52</td><td align="center" style="background-color:rgba(118,185,0,0.12);">11.64</td></tr>
    <tr><td align="left">LibriSpeech test-clean</td><td align="center" style="background-color:rgba(107,114,128,0.12);">1.38</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">1.49</td><td align="center" style="background-color:rgba(118,185,0,0.12);">1.57</td><td align="center" style="background-color:rgba(118,185,0,0.12);">1.75</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.42</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.73</td></tr>
    <tr><td align="left">LibriSpeech test-other</td><td align="center" style="background-color:rgba(107,114,128,0.12);">2.81</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">3.59</td><td align="center" style="background-color:rgba(118,185,0,0.12);">3.95</td><td align="center" style="background-color:rgba(118,185,0,0.12);">4.55</td><td align="center" style="background-color:rgba(118,185,0,0.12);">6.41</td><td align="center" style="background-color:rgba(118,185,0,0.12);">7.06</td></tr>
    <tr><td align="left">SPGISpeech</td><td align="center" style="background-color:rgba(107,114,128,0.12);">2.04</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">2.28</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.52</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.91</td><td align="center" style="background-color:rgba(118,185,0,0.12);">4.02</td><td align="center" style="background-color:rgba(118,185,0,0.12);">4.73</td></tr>
    <tr><td align="left">VoxPopuli (cleaned)</td><td align="center" style="background-color:rgba(107,114,128,0.12);">3.41</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">3.67</td><td align="center" style="background-color:rgba(118,185,0,0.12);">3.35</td><td align="center" style="background-color:rgba(118,185,0,0.12);">3.79</td><td align="center" style="background-color:rgba(118,185,0,0.12);">4.93</td><td align="center" style="background-color:rgba(118,185,0,0.12);">5.65</td></tr>
    <tr><td align="left"><strong>Average</strong></td><td align="center" style="background-color:rgba(107,114,128,0.12);"><strong>4.68</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;"><strong>5.41</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>5.68</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>6.27</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>7.87</strong></td><td align="center" style="background-color:rgba(118,185,0,0.12);"><strong>9.02</strong></td></tr>
  </tbody>
</table>

## Streaming Speech Translation (ASR + LLM Cascade)

The unified model can be used as the ASR front end of a cascaded simultaneous speech translation system.
The English-only predecessor [Parakeet-unified-en-0.6b](https://huggingface.co/nvidia/parakeet-unified-en-0.6b) of this model was the ASR front end for the English-to-X tracks of NVIDIA's IWSLT 2026
system [8], which ranked first by COMET for English-to-German, English-to-Chinese and English-to-Italian translation
in both latency regimes. This multilingual checkpoint extends the same approach
to speech in any of its 25 ASR languages, provided that the downstream translation LLM supports the requested language pair.

The following results use [Riva-Translate-4B-Instruct-v2](https://huggingface.co/nvidia/Riva-Translate-4B-Instruct-v2) with the longest-common-prefix translation policy (waitk=-1) and 800ms end-of-utterance detection on FLEURS. COMET (scored with [Unbabel/XCOMET-XL](https://huggingface.co/Unbabel/XCOMET-XL); higher is better) and length-adaptive average lagging (LAAL, seconds; lower is better) are averaged over 23 language pairs in each direction. Maltese is excluded because the translation LLM does not support it.

<table>
  <thead>
    <tr><th rowspan="2" align="left">ASR model and setting</th><th colspan="2" align="center" style="background-color:#76b900;color:#ffffff;">English → X</th><th colspan="2" align="center" style="background-color:#76b900;color:#ffffff;border-left:2px solid #cbd5e1;">X → English</th></tr>
    <tr><th align="center" style="background-color:rgba(118,185,0,0.12);">COMET ↑</th><th align="center" style="background-color:rgba(118,185,0,0.12);">LAAL ↓</th><th align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">COMET ↑</th><th align="center" style="background-color:rgba(118,185,0,0.12);">LAAL ↓</th></tr>
  </thead>
  <tbody>
    <tr><td align="left">Unified, 0.56s chunk + 0.56s right context</td><td align="center" style="background-color:rgba(118,185,0,0.12);">81.4</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.40s</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">81.7</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.58s</td></tr>
    <tr><td align="left">Unified, 0.80s chunk + 0.80s right context</td><td align="center" style="background-color:rgba(118,185,0,0.12);">81.2</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.74s</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">82.8</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.97s</td></tr>
    <tr><td align="left">Unified, 1.04s chunk + 0.56s right context</td><td align="center" style="background-color:rgba(118,185,0,0.12);">82.1</td><td align="center" style="background-color:rgba(118,185,0,0.12);">3.14s</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">83.7</td><td align="center" style="background-color:rgba(118,185,0,0.12);">3.36s</td></tr>
    <tr><td align="left">Nemotron 3.5 cache-aware, 1.12s latency</td><td align="center" style="background-color:rgba(118,185,0,0.12);">79.3</td><td align="center" style="background-color:rgba(118,185,0,0.12);">2.96s</td><td align="center" style="background-color:rgba(118,185,0,0.12);border-left:2px solid #cbd5e1;">78.5</td><td align="center" style="background-color:rgba(118,185,0,0.12);">3.27s</td></tr>
  </tbody>
</table>

### Running the Cascade

The cascade runs in one process with [NeMo/examples/asr/asr_streaming_inference/asr_streaming_infer.py](https://github.com/NVIDIA-NeMo/Speech/blob/main/examples/asr/asr_streaming_inference/asr_streaming_infer.py):
the unified model transcribes the audio in buffered streaming mode, and every finalized ASR segment is translated
by an LLM served with vLLM. vLLM conflicts with the `all` / `cu12` / `cu13` extras, so install it into a separate
environment of the NeMo Speech checkout:

```bash
cd Speech
UV_PROJECT_ENVIRONMENT=.venv-vllm uv sync --locked --python 3.13 --extra asr --extra vllm
```

The following command translates German speech into English with the setting of the first table row (0.56s chunk
and right context, 5.6s left context):

```bash
.venv-vllm/bin/python examples/asr/asr_streaming_inference/asr_streaming_infer.py \
    --config-path=../conf/asr_streaming_inference \
    --config-name=buffered_rnnt.yaml \
    audio_file=<audio_file, directory or manifest> \
    output_filename=<output_json_file> \
    asr.model_name=nvidia/nemotron-labs-unified-asr-0.6b \
    lang=de \
    streaming.left_padding_size=5.6 \
    streaming.chunk_size=0.56 \
    streaming.right_padding_size=0.56 \
    asr_output_granularity=segment \
    enable_itn=False \
    endpointing.stop_history_eou=800 \
    enable_nmt=True \
    nmt.model_name=nvidia/Riva-Translate-4B-Instruct-v2 \
    nmt.source_language=German \
    nmt.target_language=English \
    nmt.waitk=-1 \
    nmt.device_id=1
```

- `lang` is the language ID of the speech, i.e. the source language of the translation pair; it selects the ASR
  language prompt.
- `nmt.source_language` and `nmt.target_language` are language names, not IDs. For Riva-Translate-4B-Instruct-v2,
  use `Latin American Spanish` and `Brazilian Portuguese` for the FLEURS Spanish and Portuguese data.
- `nmt.waitk=-1` commits the longest common prefix of the current and previous translations; a positive value
  instead limits how many words the translation may lag behind the transcript. `endpointing.stop_history_eou` is
  the end-of-utterance window in milliseconds.
- The translation LLM runs on GPU `nmt.device_id`. To run both models on a single GPU, set `nmt.device_id=0` and
  lower `nmt.llm_params.gpu_memory_utilization` (e.g. `0.6`).

For English-to-X translation, set `lang=en`, `nmt.source_language=English` and the target language name.


## References(s):
[1] [Reducing the Offline-Streaming Gap for Unified ASR Transducer with Consistency Regularization](https://arxiv.org/abs/2604.19079) <br>
[2] [Fast Conformer with Linearly Scalable Attention for Efficient Speech Recognition](https://arxiv.org/abs/2305.05084) <br>
[3] [Dynamic Chunk Convolution for Unified Streaming and Non-Streaming Conformer ASR](https://arxiv.org/abs/2304.09325) <br>
[4] [Conformer: Convolution-augmented Transformer for Speech Recognition](https://arxiv.org/abs/2005.08100) <br>
[5] [Granary: Speech Recognition and Translation Dataset in 25 European Languages](https://arxiv.org/abs/2505.13404) <br>
[6] [NVIDIA Granary Dataset Card](https://huggingface.co/datasets/nvidia/Granary) <br>
[7] [NVIDIA NeMo Framework](https://github.com/NVIDIA-NeMo/Speech) <br>
[8] [NeMo@IWSLT 2026: Cascaded System for Simultaneous Speech Translation](https://aclanthology.org/2026.iwslt-1.23.pdf) <br>


## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br>

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).
