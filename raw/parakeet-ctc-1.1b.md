---
language:
- en
library_name: nemo
datasets:
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
- mozilla-foundation/common_voice_8_0
- MLCommons/peoples_speech
thumbnail: null
tags:
- transformers
- automatic-speech-recognition
- speech
- audio
- FastConformer
- Conformer
- pytorch
- NeMo
- hf-asr-leaderboard
- ctc
license: cc-by-4.0
widget:
- example_title: Librispeech sample 1
  src: https://cdn-media.huggingface.co/speech_samples/sample1.flac
- example_title: Librispeech sample 2
  src: https://cdn-media.huggingface.co/speech_samples/sample2.flac
model-index:
- name: parakeet-ctc-1.1b
  results:
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: AMI (Meetings test)
      type: edinburghcstr/ami
      config: ihm
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 15.62
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: Earnings-22
      type: revdotcom/earnings22
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 13.69
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: GigaSpeech
      type: speechcolab/gigaspeech
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 10.27
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: LibriSpeech (clean)
      type: librispeech_asr
      config: other
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 1.83
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: LibriSpeech (other)
      type: librispeech_asr
      config: other
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 3.54
  - task:
      type: Automatic Speech Recognition
      name: automatic-speech-recognition
    dataset:
      name: SPGI Speech
      type: kensho/spgispeech
      config: test
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 4.2
  - task:
      type: Automatic Speech Recognition
      name: automatic-speech-recognition
    dataset:
      name: tedlium-v3
      type: LIUM/tedlium
      config: release1
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 3.54
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: Vox Populi
      type: facebook/voxpopuli
      config: en
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 6.53
  - task:
      type: Automatic Speech Recognition
      name: automatic-speech-recognition
    dataset:
      name: Mozilla Common Voice 9.0
      type: mozilla-foundation/common_voice_9_0
      config: en
      split: test
      args:
        language: en
    metrics:
    - name: Test WER
      type: wer
      value: 9.02
metrics:
- wer
pipeline_tag: automatic-speech-recognition
---

# Parakeet CTC 1.1B (en)

<style>
img {
 display: inline;
}
</style>

[![Model architecture](https://img.shields.io/badge/Model_Arch-FastConformer--CTC-lightgrey#model-badge)](#model-architecture)
| [![Model size](https://img.shields.io/badge/Params-1.1B-lightgrey#model-badge)](#model-architecture)
| [![Language](https://img.shields.io/badge/Language-en-lightgrey#model-badge)](#datasets)


`parakeet-ctc-1.1b` is an ASR model that transcribes speech in lower case English alphabet. This model is jointly developed by [NVIDIA NeMo](https://github.com/NVIDIA/NeMo) and [Suno.ai](https://www.suno.ai/) teams.
It is an XXL version of FastConformer CTC [1] (around 1.1B parameters) model.
See the [model architecture](#model-architecture) section and [NeMo documentation](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/asr/models.html#fast-conformer) for complete architecture details.

## NVIDIA NeMo: Training

To train, fine-tune or play with the model you will need to install [NVIDIA NeMo](https://github.com/NVIDIA/NeMo). We recommend you install it after you've installed latest PyTorch version.
```
pip install nemo_toolkit['all']
``` 

## How to Use this Model

There are several ways to use this model. Choose the one that fits your needs.

### Run locally with NeMo-Speech.cpp

[NeMo-Speech.cpp](https://github.com/NVIDIA/NeMo-Speech.cpp) provides a
lightweight native C++ runtime for local inference with
this model. After [installing the runtime](https://github.com/NVIDIA/NeMo-Speech.cpp#installation):

```bash
hf download nvidia/parakeet-ctc-1.1b \
  parakeet-ctc-1.1b.q8_0.gguf \
  --local-dir models

nemo-speech transcribe audio.wav \
  --model models/parakeet-ctc-1.1b.q8_0.gguf
```

See the [NeMo-Speech.cpp documentation](https://github.com/NVIDIA/NeMo-Speech.cpp)
for more details.

### NVIDIA NeMo

The model is available for use in the NeMo toolkit [3], and can be used as a pre-trained checkpoint for inference or for fine-tuning on another dataset. Moreover, you can now run Parakeet CTC natively with [Transformers](https://github.com/huggingface/transformers) 🤗.

#### Automatically instantiate the model

```python
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="nvidia/parakeet-ctc-1.1b")
```

#### Transcribing using NeMo
First, let's get a sample
```
wget https://dldata-public.s3.us-east-2.amazonaws.com/2086-149220-0033.wav
```
Then simply do:
```
asr_model.transcribe(['2086-149220-0033.wav'])
```

### Transcribing using [Transformers](https://github.com/huggingface/transformers) 🤗 

Make sure to install `transformers` from source.

```bash
pip install git+https://github.com/huggingface/transformers
```

<details>
  <summary>➡️ Pipeline usage</summary>

```python
from transformers import pipeline

pipe = pipeline("automatic-speech-recognition", model="nvidia/parakeet-ctc-1.1b")
out = pipe("https://huggingface.co/datasets/hf-internal-testing/dummy-audio-samples/resolve/main/bcn_weather.mp3")
print(out)
```
</details>

<details>
  <summary>➡️ AutoModel</summary>

```python
from transformers import AutoModelForCTC, AutoProcessor
from datasets import load_dataset, Audio
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained("nvidia/parakeet-ctc-1.1b")
model = AutoModelForCTC.from_pretrained("nvidia/parakeet-ctc-1.1b", dtype="auto", device_map=device)

ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
ds = ds.cast_column("audio", Audio(sampling_rate=processor.feature_extractor.sampling_rate))
speech_samples = [el['array'] for el in ds["audio"][:5]]

inputs = processor(speech_samples, sampling_rate=processor.feature_extractor.sampling_rate)
inputs.to(model.device, dtype=model.dtype)
outputs = model.generate(**inputs)
print(processor.batch_decode(outputs))
```
</details>

<details>
  <summary>➡️ Training</summary>

```python
from transformers import AutoModelForCTC, AutoProcessor
from datasets import load_dataset, Audio
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained("nvidia/parakeet-ctc-1.1b")
model = AutoModelForCTC.from_pretrained("nvidia/parakeet-ctc-1.1b", dtype="auto", device_map=device)

ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
ds = ds.cast_column("audio", Audio(sampling_rate=processor.feature_extractor.sampling_rate))
speech_samples = [el['array'] for el in ds["audio"][:5]]
text_samples = [el for el in ds["text"][:5]]

# passing `text` to the processor will prepare inputs' `labels` key
inputs = processor(audio=speech_samples, text=text_samples, sampling_rate=processor.feature_extractor.sampling_rate)
inputs.to(device, dtype=model.dtype)

outputs = model(**inputs)
outputs.loss.backward()
```
</details>

For more details about usage, the refer to [Transformers' documentation](https://huggingface.co/docs/transformers/en/index).

### Transcribing many audio files

```shell
python [NEMO_GIT_FOLDER]/examples/asr/transcribe_speech.py 
 pretrained_name="nvidia/parakeet-ctc-1.1b" 
 audio_dir="<DIRECTORY CONTAINING AUDIO FILES>"
```

### Input

This model accepts 16000 Hz mono-channel audio (wav files) as input.

### Output

This model provides transcribed speech as a string for a given audio sample.

## Model Architecture

FastConformer [1] is an optimized version of the Conformer model with 8x depthwise-separable convolutional downsampling. The model is trained using CTC loss. You may find more information on the details of FastConformer here: [Fast-Conformer Model](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/asr/models.html#fast-conformer).

## Training

The NeMo toolkit [3] was used for training the models for over several hundred epochs. These model are trained with this [example script](https://github.com/NVIDIA/NeMo/blob/main/examples/asr/asr_ctc/speech_to_text_ctc_bpe.py) and this [base config](https://github.com/NVIDIA/NeMo/blob/main/examples/asr/conf/fastconformer/fast-conformer_ctc_bpe.yaml).

The tokenizers for these models were built using the text transcripts of the train set with this [script](https://github.com/NVIDIA/NeMo/blob/main/scripts/tokenizers/process_asr_text_tokenizer.py).

### Datasets

The model was trained on 64K hours of English speech collected and prepared by NVIDIA NeMo and Suno teams.

The training dataset consists of private subset with 40K hours of English speech plus 24K hours from the following public datasets:

- Librispeech 960 hours of English speech
- Fisher Corpus
- Switchboard-1 Dataset
- WSJ-0 and WSJ-1
- National Speech Corpus (Part 1, Part 6)
- VCTK
- VoxPopuli (EN)
- Europarl-ASR (EN)
- Multilingual Librispeech (MLS EN) - 2,000 hour subset
- Mozilla Common Voice (v7.0)
- People's Speech  - 12,000 hour subset

## Performance

The performance of Automatic Speech Recognition models is measuring using Word Error Rate. Since this dataset is trained on multiple domains and a much larger corpus, it will generally perform better at transcribing audio in general.

The following tables summarizes the performance of the available models in this collection with the CTC decoder. Performances of the ASR models are reported in terms of Word Error Rate (WER%) with greedy decoding. 

|**Version**|**Tokenizer**|**Vocabulary Size**|**AMI**|**Earnings-22**|**Giga Speech**|**LS test-clean**|**SPGI Speech**|**TEDLIUM-v3**|**Vox Populi**|**Common Voice**|
|---------|-----------------------|-----------------|---------------|---------------|------------|-----------|-----|-------|------|------|
| 1.22.0  | SentencePiece Unigram | 1024 | 15.62 | 13.69 | 10.27 | 1.83 | 3.54 | 4.20 | 3.54 | 6.53 | 9.02 |

These are greedy WER numbers without external LM. More details on evaluation can be found at [HuggingFace ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

## NVIDIA Riva: Deployment

[NVIDIA Riva](https://developer.nvidia.com/riva), is an accelerated speech AI SDK deployable on-prem, in all clouds, multi-cloud, hybrid, on edge, and embedded. 
Additionally, Riva provides: 

* World-class out-of-the-box accuracy for the most common languages with model checkpoints trained on proprietary data with hundreds of thousands of GPU-compute hours 
* Best in class accuracy with run-time word boosting (e.g., brand and product names) and customization of acoustic model, language model, and inverse text normalization 
* Streaming speech recognition, Kubernetes compatible scaling, and enterprise-grade support 

Although this model isn’t supported yet by Riva, the [list of supported models is here](https://huggingface.co/models?other=Riva).  
Check out [Riva live demo](https://developer.nvidia.com/riva#demos). 

## References
[1] [Fast Conformer with Linearly Scalable Attention for Efficient Speech Recognition](https://arxiv.org/abs/2305.05084)

[2] [Google Sentencepiece Tokenizer](https://github.com/google/sentencepiece)

[3] [NVIDIA NeMo Toolkit](https://github.com/NVIDIA/NeMo)

[4] [Suno.ai](https://suno.ai/)

[5] [HuggingFace ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)


## Licence

License to use this model is covered by the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). By downloading the public and release version of the model, you accept the terms and conditions of the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) license.