---
license: cc-by-4.0
library_name: nemo
datasets:
- fisher_english
- NIST_SRE_2004-2010
- librispeech
- ami_meeting_corpus
- voxconverse_v0.3
- icsi
- aishell4
- dihard_challenge-3-dev
- NIST_SRE_2000-Disc8_split1
- Alimeeting-train
- DiPCo
thumbnail: null
tags:
- speaker-diarization
- speaker-recognition
- speech
- audio
- Transformer
- FastConformer
- Conformer
- NEST
- pytorch
- NeMo
widget:
- example_title: Librispeech sample 1
  src: https://cdn-media.huggingface.co/speech_samples/sample1.flac
- example_title: Librispeech sample 2
  src: https://cdn-media.huggingface.co/speech_samples/sample2.flac
model-index:
- name: diar_streaming_sortformer_4spk-v2
  results:
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: DIHARD III Eval (1-4 spk)
      type: dihard3-eval-1to4spks
      config: with_overlap_collar_0.0s
      input_buffer_lenght: 1.04s
      split: eval-1to4spks
    metrics:
    - name: Test DER
      type: der
      value: 13.24
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: DIHARD III Eval (5-9 spk)
      type: dihard3-eval-5to9spks
      config: with_overlap_collar_0.0s
      input_buffer_lenght: 1.04s
      split: eval-5to9spks
    metrics:
    - name: Test DER
      type: der
      value: 42.56
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: DIHARD III Eval (full)
      type: dihard3-eval
      config: with_overlap_collar_0.0s
      input_buffer_lenght: 1.04s
      split: eval
    metrics:
    - name: Test DER
      type: der
      value: 18.91
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8) part2 (2 spk)
      type: CALLHOME-part2-2spk
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: part2-2spk
    metrics:
    - name: Test DER
      type: der
      value: 6.57
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8) part2 (3 spk)
      type: CALLHOME-part2-3spk
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: part2-3spk
    metrics:
    - name: Test DER
      type: der
      value: 10.05
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8) part2 (4 spk)
      type: CALLHOME-part2-4spk
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: part2-4spk
    metrics:
    - name: Test DER
      type: der
      value: 12.44
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8) part2 (5 spk)
      type: CALLHOME-part2-5spk
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: part2-5spk
    metrics:
    - name: Test DER
      type: der
      value: 21.68
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8) part2 (6 spk)
      type: CALLHOME-part2-6spk
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: part2-6spk
    metrics:
    - name: Test DER
      type: der
      value: 28.74
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8) part2 (full)
      type: CALLHOME-part2
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: part2
    metrics:
    - name: Test DER
      type: der
      value: 10.7
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: call_home_american_english_speech
      type: CHAES_2spk_109sessions
      config: with_overlap_collar_0.25s
      input_buffer_lenght: 1.04s
      split: ch109
    metrics:
    - name: Test DER
      type: der
      value: 4.88
metrics:
- der
pipeline_tag: automatic-speech-recognition
---

# 🚨 Announcement: New Model Version Available

A new version of Sortformer diarization model [Nemotron-3-Diarization](https://huggingface.co/nvidia/nemotron-3-diarization) has been released, supporting 8 speakers and greatly improved accuracy.


# Streaming Sortformer Diarizer 4spk v2

<style>
img {
 display: inline;
}
</style>

[![Model architecture](https://img.shields.io/badge/Model_Arch-FastConformer--Transformer-lightgrey#model-badge)](#model-architecture)
| [![Model size](https://img.shields.io/badge/Params-117M-lightgrey#model-badge)](#model-architecture)
<!-- | [![Language](https://img.shields.io/badge/Language-multilingual-lightgrey#model-badge)](#datasets) -->

This model is a streaming version of Sortformer diarizer. [Sortformer](https://arxiv.org/abs/2409.06656)[1] is a novel end-to-end neural model for speaker diarization, trained with unconventional objectives compared to existing end-to-end diarization models.

<div align="center">
    <img src="figures/sortformer_intro.png" width="750" />
</div>

[Streaming Sortformer](https://arxiv.org/abs/2507.18446)[2] employs an Arrival-Order Speaker Cache (AOSC) to store frame-level acoustic embeddings of previously observed speakers.
<div align="center">
    <img src="figures/aosc_3spk_example.gif" width="1400" />
</div>
<div align="center">
    <img src="figures/aosc_4spk_example.gif" width="1400" />
</div>

Sortformer resolves permutation problem in diarization following the arrival-time order of the speech segments from each speaker. 

This speaker diarization model can be used to enable the [NeMo Voice Agent](https://github.com/NVIDIA-NeMo/NeMo/tree/main/examples/voice_agent) to recognize speakers in conversations. See the [NeMo Voice Agent](https://github.com/NVIDIA-NeMo/NeMo/tree/main/examples/voice_agent) and the [YAML configuration](https://github.com/NVIDIA-NeMo/NeMo/blob/316aea20fc2aac4e41bc08123cc77118a9f0b82a/examples/voice_agent/server/server_configs/default.yaml#L25) for more details.
## Discover more from NVIDIA:
For documentation, deployment guides, enterprise-ready APIs, and the latest open models—including Nemotron and other cutting-edge speech, translation, and generative AI—visit the NVIDIA Developer Portal at [developer.nvidia.com](https://developer.nvidia.com/).
Join the community to access tools, support, and resources to accelerate your development with NVIDIA’s NeMo, Riva, NIM, and foundation models.<br>

### Explore more from NVIDIA:  <br>
What is [Nemotron](https://www.nvidia.com/en-us/ai-data-science/foundation-models/nemotron/)?<br>
NVIDIA Developer [Nemotron](https://developer.nvidia.com/nemotron)<br>
[NVIDIA Riva Speech](https://developer.nvidia.com/riva?sortBy=developer_learning_library%2Fsort%2Ffeatured_in.riva%3Adesc%2Ctitle%3Aasc#demos)<br>
[NeMo Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)<br>

## Model Architecture

Streaming sortformer employs pre-encode layer in the Fast-Conformer to generate speaker-cache. At each step, speaker cache is filtered to only retain the high-quality speaker cache vectors.

<div align="center">
    <img src="figures/streaming_steps.png" width="1400" />
</div>


Aside from speaker-cache management part, streaming Sortformer follows the architecture of the offline version of Sortformer. Sortformer consists of an L-size (17 layers) [NeMo Encoder for
Speech Tasks (NEST)](https://arxiv.org/abs/2408.13106)[3] which is based on [Fast-Conformer](https://arxiv.org/abs/2305.05084)[4] encoder. Following that, an 18-layer Transformer[5] encoder with hidden size of 192, 
and two feedforward layers with 4 sigmoid outputs for each frame input at the top layer. More information can be found in the [Streaming Sortformer paper](https://arxiv.org/abs/2507.18446)[2].

<div align="center">
    <img src="figures/sortformer-v1-model.png" width="450" />
</div>

## NVIDIA NeMo

To train, fine-tune or perform diarization with Sortformer, you will need to install [NVIDIA NeMo](https://github.com/NVIDIA/NeMo)[6]. We recommend you install it after you've installed Cython and latest PyTorch version.

```
apt-get update && apt-get install -y libsndfile1 ffmpeg
pip install Cython packaging
pip install 'git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]'
```

## Discover more from NVIDIA:
For documentation, deployment guides, enterprise-ready APIs, and the latest open models—including Nemotron and other cutting-edge speech, translation, and generative AI—visit the NVIDIA Developer Portal at [developer.nvidia.com](developer.nvidia.com).
Join the community to access tools, support, and resources to accelerate your development with NVIDIA’s NeMo, Riva, NIM, and foundation models.<br>

### Explore more from NVIDIA:  <br>
What is [Nemotron](https://www.nvidia.com/en-us/ai-data-science/foundation-models/nemotron/)?<br>
NVIDIA Developer [Nemotron](https://developer.nvidia.com/nemotron)<br>
[NVIDIA Riva Speech](https://developer.nvidia.com/riva?sortBy=developer_learning_library%2Fsort%2Ffeatured_in.riva%3Adesc%2Ctitle%3Aasc#demos)<br>
[NeMo Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)<br>


## 🚀 Quick Start: Run Diarization Now
Here is a short example script that loads the model, runs diarization on a WAV file, and prints the results:

```python
from nemo.collections.asr.models import SortformerEncLabelModel
diar_model = SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2")
diar_model.eval()

diar_model.sortformer_modules.chunk_len = 340
diar_model.sortformer_modules.chunk_right_context = 40
diar_model.sortformer_modules.fifo_len = 40
diar_model.sortformer_modules.spkcache_update_period = 300

predicted_segments = diar_model.diarize(audio=["/path/to/your/audio.wav"], batch_size=1)

for segment in predicted_segments[0]:
    print(segment)
```
## How to Use this Model

There are several ways to use this model. Choose the one that fits your needs.

### Run locally with NeMo-Speech.cpp

[NeMo-Speech.cpp](https://github.com/NVIDIA/NeMo-Speech.cpp) provides a
lightweight native C++ runtime for local speaker diarization. After
[installing the runtime](https://github.com/NVIDIA/NeMo-Speech.cpp#installation):

```bash
hf download nvidia/diar_streaming_sortformer_4spk-v2 \
  diar_streaming_sortformer_4spk-v2.q8_0.gguf \
  --local-dir models

nemo-speech diarize meeting.wav \
  --model models/diar_streaming_sortformer_4spk-v2.q8_0.gguf
```

The same model can add word-level speaker tags to a transcription:

```bash
nemo-speech transcribe meeting.wav \
  --model models/asr-model.gguf \
  --diar-model models/diar_streaming_sortformer_4spk-v2.q8_0.gguf \
  --json
```

See the [NeMo-Speech.cpp diarization guide](https://github.com/NVIDIA/NeMo-Speech.cpp/blob/main/docs/cli.md#diarize-audio)
for more usage examples.

### NVIDIA NeMo

The model is available for use in the NeMo Framework[6], and can be used as a pre-trained checkpoint for inference or for fine-tuning on another dataset.

### Loading the Model

```python
from nemo.collections.asr.models import SortformerEncLabelModel

# load model from Hugging Face model card directly (You need a Hugging Face token)
diar_model = SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2")

# If you have a downloaded model in "/path/to/diar_streaming_sortformer_4spk-v2.nemo", load model from a downloaded file
diar_model = SortformerEncLabelModel.restore_from(restore_path="/path/to/diar_streaming_sortformer_4spk-v2.nemo", map_location='cuda', strict=False)

# switch to inference mode
diar_model.eval()
```

### Input Format
Input to Sortformer can be an individual audio file:
```python
audio_input="/path/to/multispeaker_audio1.wav"
```
or a list of paths to audio files:
```python
audio_input=["/path/to/multispeaker_audio1.wav", "/path/to/multispeaker_audio2.wav"]
```
or a numpy array (single or list):
```python
import numpy as np
audio_input = np.random.randn(16000 * 10).astype(np.float32)  # 10 sec at 16kHz
# or a list of arrays
audio_input = [audio_array1, audio_array2]
diar_model.diarize(audio=audio_input, batch_size=2, sample_rate=16000)
```
Note: When using numpy arrays, you **MUST** specify a correct `sample_rate` in `diar_model.diarize()` function. 
Default `sample_rate` is `16000`.

or a jsonl manifest file:
```python
audio_input="/path/to/multispeaker_manifest.json"
```
where each line is a dictionary containing the following fields:
```yaml
# Example of a line in `multispeaker_manifest.json`
{
    "audio_filepath": "/path/to/multispeaker_audio1.wav",  # path to the input audio file 
    "offset": 0, # offset (start) time of the input audio
    "duration": 600,  # duration of the audio, can be set to `null` if using NeMo main branch
}
{
    "audio_filepath": "/path/to/multispeaker_audio2.wav",  
    "offset": 900,
    "duration": 580,  
}
```

### Setting up Streaming Configuration

Streaming configuration is defined by the following parameters, all measured in **80ms frames**:
* **CHUNK_SIZE**: The number of frames in a processing chunk.
* **RIGHT_CONTEXT**: The number of future frames attached after the chunk.
* **FIFO_SIZE**: The number of previous frames attached before the chunk, from the FIFO queue.
* **UPDATE_PERIOD**: The number of frames extracted from the FIFO queue to update the speaker cache.
* **SPEAKER_CACHE_SIZE**: The total number of frames in the speaker cache.

Here are recommended configurations for different scenarios:
| **Configuration** | **Latency** | **RTF** | **CHUNK_SIZE** | **RIGHT_CONTEXT** | **FIFO_SIZE** | **UPDATE_PERIOD** | **SPEAKER_CACHE_SIZE** |
| :---------------- | :---------- | :------ | :------------- | :---------------- | :------------ | :---------------- | :--------------------- |
| very high latency | 30.4s       | 0.002   | 340            | 40                | 40            | 300               | 188                    |
| high latency      | 10.0s       | 0.005   | 124            | 1                 | 124           | 124               | 188                    |
| low latency       | 1.04s       | 0.093   | 6              | 7                 | 188           | 144               | 188                    |
| ultra low latency | 0.32s       | 0.180   | 3              | 1                 | 188           | 144               | 188                    |

For clarity on the metrics used in the table:
* **Latency**: Refers to **Input Buffer Latency**, calculated as **CHUNK_SIZE** + **RIGHT_CONTEXT**. This value does not include computational processing time.
* **Real-Time Factor (RTF)**: Characterizes processing speed, calculated as the time taken to process an audio file divided by its duration. RTF values are measured with a batch size of 1 on an NVIDIA RTX 6000 Ada Generation GPU.

To set streaming configuration, use:
```python
diar_model.sortformer_modules.chunk_len = CHUNK_SIZE
diar_model.sortformer_modules.chunk_right_context = RIGHT_CONTEXT
diar_model.sortformer_modules.fifo_len = FIFO_SIZE
diar_model.sortformer_modules.spkcache_update_period = UPDATE_PERIOD
diar_model.sortformer_modules.spkcache_len = SPEAKER_CACHE_SIZE
diar_model.sortformer_modules._check_streaming_parameters()
```

### Getting Diarization Results
To perform speaker diarization and get a list of speaker-marked speech segments in the format 'begin_seconds, end_seconds, speaker_index', simply use:
```python
predicted_segments = diar_model.diarize(audio=audio_input, batch_size=1)
```
To obtain tensors of speaker activity probabilities, use:
```python
predicted_segments, predicted_probs = diar_model.diarize(audio=audio_input, batch_size=1, include_tensor_outputs=True)
```
Note that if you are feeding a list of numpy arrays, you **MUST** provide the `sample_rate` in integer format.

```python
predicted_segments, predicted_probs = diar_model.diarize(audio=[np_array1, np_array2], batch_size=2, sample_rate=16000)
```

## 🔬 For more detailed evaluations (DER)

If you need to perform a comprehensive evaluation and calculate the **Diarization Error Rate (DER)** across different parameter settings, use the NeMo example script [e2e_diarize_speech.py](https://github.com/NVIDIA-NeMo/NeMo/blob/main/examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py).
This script allows you to test the streaming behavior of the model by adjusting key parameters like `chunk_len`, `fifo_len`, and `spkcache_update_period`.
```bash
python ${NEMO_ROOT}/examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py \
    model_path="/path/to/diar_sortformer_4spk_v1.nemo" \
    dataset_manifest="/path/to/diarization_manifest.json" \
    batch_size=1 \
    spkcache_len=188 \
    spkcache_update_period=300 \
    fifo_len=40 \
    chunk_len=340 \
    chunk_right_context=40
```

### Input

This model accepts single-channel (mono) audio sampled at 16,000 Hz.
- The actual input tensor is a Ns x 1 matrix for each audio clip, where Ns is the number of samples in the time-series signal. 
- For instance, a 10-second audio clip sampled at 16,000 Hz (mono-channel WAV file) will form a 160,000 x 1 matrix.

### Output

The output of the model is an T x S matrix, where:  
- S is the maximum number of speakers (in this model, S = 4).  
- T is the total number of frames, including zero-padding. Each frame corresponds to a segment of 0.08 seconds of audio.  
Each element of the T x S matrix represents the speaker activity probability in the [0, 1] range.  For example, a matrix element a(150, 2) = 0.95 indicates a 95% probability of activity for the second speaker during the time range [12.00, 12.08] seconds.


## Train and evaluate Sortformer diarizer using NeMo
### Training

Sortformer diarizer models are trained on 8 nodes of 8×NVIDIA Tesla V100 GPUs. We use 90 second long training samples and batch size of 4.
The model can be trained using this [example script](https://github.com/NVIDIA/NeMo/blob/main/examples/speaker_tasks/diarization/neural_diarizer/sortformer_diar_train.py) and [base config](https://github.com/NVIDIA/NeMo/blob/main/examples/speaker_tasks/diarization/conf/neural_diarizer/sortformer_diarizer_hybrid_loss_4spk-v1.yaml).

### Inference

Sortformer diarizer models can be performed with post-processing algorithms using inference [example script](https://github.com/NVIDIA/NeMo/blob/main/examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py). If you provide the post-processing YAML configs in [`post_processing` folder](https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization/conf/post_processing) to reproduce the optimized post-processing algorithm for each development dataset.

### Technical Limitations

- The model operates in a streaming mode (online mode).
- It can detect a maximum of 4 speakers; performance degrades on recordings with 5 and more speakers.
- While the model is designed for long-form audio and can handle recordings that are several hours long, performance may degrade on very long recordings.
- The model was trained on publicly available speech datasets, primarily in English. As a result:
    * Performance may degrade on non-English speech.
    * Performance may also degrade on out-of-domain data, such as recordings in noisy conditions.

## Datasets

Sortformer was trained on a combination of 2445 hours of real conversations and 5150 hours or simulated audio mixtures generated by [NeMo speech data simulator](https://arxiv.org/abs/2310.12371)[7].
All the datasets listed above are based on the same labeling method via [RTTM](https://web.archive.org/web/20100606092041if_/http://www.itl.nist.gov/iad/mig/tests/rt/2009/docs/rt09-meeting-eval-plan-v2.pdf) format. A subset of RTTM files used for model training are processed for the speaker diarization model training purposes.
Data collection methods vary across individual datasets. For example, the above datasets include phone calls, interviews, web videos, and audiobook recordings. Please refer to the [Linguistic Data Consortium (LDC) website](https://www.ldc.upenn.edu/) or dataset webpage for detailed data collection methods.


### Training Datasets (Real conversations)
- Fisher English (LDC)
- AMI Meeting Corpus
- VoxConverse-v0.3
- ICSI
- AISHELL-4
- Third DIHARD Challenge Development (LDC)
- 2000 NIST Speaker Recognition Evaluation, split1 (LDC)
- DiPCo
- AliMeeting

### Training Datasets (Used to simulate audio mixtures)
- 2004-2010 NIST Speaker Recognition Evaluation (LDC)
- Librispeech

## Performance


### Evaluation data specifications

| **Dataset**                | **Number of speakers** | **Number of Sessions** |
|----------------------------|------------------------|------------------------|
| **DIHARD III Eval <=4spk** | 1-4                    | 219                    |
| **DIHARD III Eval >=5spk** | 5-9                    | 40                     |
| **DIHARD III Eval full**   | 1-9                    | 259                    |
| **CALLHOME-part2 2spk**    | 2                      | 148                    |
| **CALLHOME-part2 3spk**    | 3                      | 74                     |
| **CALLHOME-part2 4spk**    | 4                      | 20                     |
| **CALLHOME-part2 5spk**    | 5                      | 5                      |
| **CALLHOME-part2 6spk**    | 6                      | 3                      |
| **CALLHOME-part2 full**    | 2-6                    | 250                    |
| **CH109**                  | 2                      | 109                    |


### Diarization Error Rate (DER)
* All evaluations include overlapping speech.   
* Collar tolerance is 0s for DIHARD III Eval, and 0.25s for CALLHOME-part2 and CH109.  
* Post-Processing (PP) is optimized on two different held-out dataset splits.  
    - [DIHARD III Dev Optimized Post-Processing](https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization/conf/post_processing/diar_streaming_sortformer_4spk-v2_dihard3-dev.yaml) for DIHARD III Eval    
    - [CALLHOME-part1 Optimized Post-Processing](https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization/conf/post_processing/diar_streaming_sortformer_4spk-v2_callhome-part1.yaml) for CALLHOME-part2 and CH109  
    - 
| **Latency** | *PP* | **DIHARD III Eval <=4spk** | **DIHARD III Eval >=5spk** | **DIHARD III Eval full** | **CALLHOME-part2 2spk** | **CALLHOME-part2 3spk** | **CALLHOME-part2 4spk** | **CALLHOME-part2 5spk** | **CALLHOME-part2 6spk** | **CALLHOME-part2 full** | **CH109** |
|-------------|------|----------------------------|----------------------------|--------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-----------|
| 30.4s       | no   | 14.63                      | 40.74                      | 19.68                    | 6.27                    | 10.27                   | 12.30                   | 19.08                   | 28.09                   | 10.50                   | 5.03      |
| 30.4s       | yes  | 13.45                      | 41.40                      | 18.85                    | 5.34                    | 9.22                    | 11.29                   | 18.84                   | 27.29                   | 9.54                    | 4.61      |
| 10.0s       | no   | 14.90                      | 41.06                      | 19.96                    | 6.96                    | 11.05                   | 12.93                   | 20.47                   | 28.10                   | 11.21                   | 5.28      |
| 10.0s       | yes  | 13.75                      | 41.41                      | 19.10                    | 6.05                    | 9.88                    | 11.72                   | 19.66                   | 27.37                   | 10.15                   | 4.80      |
| 1.04s       | no   | 14.49                      | 42.22                      | 19.85                    | 7.51                    | 11.45                   | 13.75                   | 23.22                   | 29.22                   | 11.89                   | 5.37      |
| 1.04s       | yes  | 13.24                      | 42.56                      | 18.91                    | 6.57                    | 10.05                   | 12.44                   | 21.68                   | 28.74                   | 10.70                   | 4.88      |
| 0.32s       | no   | 14.64                      | 43.47                      | 20.19                    | 8.63                    | 12.91                   | 16.19                   | 29.40                   | 30.60                   | 13.57                   | 6.46      |
| 0.32s       | yes  | 13.44                      | 43.73                      | 19.28                    | 6.91                    | 10.45                   | 13.70                   | 27.04                   | 28.58                   | 11.38                   | 5.27      |

## NVIDIA Riva: Deployment

Streaming Sortformer is deployed via NVIDIA RIVA ASR - [Speech Recognition with Speaker Diarization](https://docs.nvidia.com/nim/riva/asr/latest/support-matrix.html#speech-recognition-with-speaker-diarization)
[NVIDIA Riva](https://developer.nvidia.com/riva), is an accelerated speech AI SDK deployable on-prem, in all clouds, multi-cloud, hybrid, on edge, and embedded. 
Additionally, Riva provides: 
* World-class out-of-the-box accuracy for the most common languages with model checkpoints trained on proprietary data with hundreds of thousands of GPU-compute hours 
* Best in class accuracy with run-time word boosting (e.g., brand and product names) and customization of acoustic model, language model, and inverse text normalization 
* Streaming speech recognition, Kubernetes compatible scaling, and enterprise-grade support 
For more information on NVIDIA RIVA, see the [list of supported models](https://huggingface.co/models?other=Riva) is here.  
Also check out the [Riva live demo](https://developer.nvidia.com/riva#demos). 

## References

[1] [Sortformer: Seamless Integration of Speaker Diarization and ASR by Bridging Timestamps and Tokens](https://arxiv.org/abs/2409.06656)  

[2] [Streaming Sortformer: Speaker Cache-Based Online Speaker Diarization with Arrival-Time Ordering](https://arxiv.org/abs/2507.18446)  

[3] [NEST: Self-supervised Fast Conformer as All-purpose Seasoning to Speech Processing Tasks](https://arxiv.org/abs/2408.13106)  

[4] [Fast Conformer with Linearly Scalable Attention for Efficient Speech Recognition](https://arxiv.org/abs/2305.05084)  

[5] [Attention is all you need](https://arxiv.org/abs/1706.03762)  

[6] [NVIDIA NeMo Framework](https://github.com/NVIDIA/NeMo)  

[7] [NeMo speech data simulator](https://arxiv.org/abs/2310.12371)  

## Licence

License to use this model is covered by the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). By downloading the public and release version of the model, you accept the terms and conditions of the CC-BY-4.0 license.
