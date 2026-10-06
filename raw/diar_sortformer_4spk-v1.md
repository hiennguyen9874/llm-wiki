---
license: cc-by-nc-4.0
library_name: nemo
datasets:
- fisher_english
- NIST_SRE_2004-2010
- librispeech
- ami_meeting_corpus
- voxconverse_v0.3
- icsi
- aishell4
- dihard_challenge-3
- NIST_SRE_2000-Disc8_split1
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
- name: diar_sortformer_4spk-v1
  results:
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: DIHARD3-eval
      type: dihard3-eval-1to4spks
      config: with_overlap_collar_0.0s
      split: eval
    metrics:
    - name: Test DER
      type: der
      value: 14.76
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8)
      type: CALLHOME-part2-2spk
      config: with_overlap_collar_0.25s
      split: part2-2spk
    metrics:
    - name: Test DER
      type: der
      value: 5.85
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8)
      type: CALLHOME-part2-3spk
      config: with_overlap_collar_0.25s
      split: part2-3spk
    metrics:
    - name: Test DER
      type: der
      value: 8.46
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: CALLHOME (NIST-SRE-2000 Disc8)
      type: CALLHOME-part2-4spk
      config: with_overlap_collar_0.25s
      split: part2-4spk
    metrics:
    - name: Test DER
      type: der
      value: 12.59
  - task:
      name: Speaker Diarization
      type: speaker-diarization-with-post-processing
    dataset:
      name: call_home_american_english_speech
      type: CHAES_2spk_109sessions
      config: with_overlap_collar_0.25s
      split: ch109
    metrics:
    - name: Test DER
      type: der
      value: 6.86
metrics:
- der
pipeline_tag: automatic-speech-recognition
---
# 🚨 Announcement: New Model Version Available

A new version of Sortformer diarization model [Nemotron-3-Diarization](https://huggingface.co/nvidia/nemotron-3-diarization) has been released, supporting 8 speakers and greatly improved accuracy.

# Sortformer Diarizer 4spk v1

<style>
img {
 display: inline;
}
</style>

[![Model architecture](https://img.shields.io/badge/Model_Arch-FastConformer--Transformer-lightgrey#model-badge)](#model-architecture)
| [![Model size](https://img.shields.io/badge/Params-123M-lightgrey#model-badge)](#model-architecture)
<!-- | [![Language](https://img.shields.io/badge/Language-multilingual-lightgrey#model-badge)](#datasets) -->


[Sortformer](https://arxiv.org/abs/2409.06656)[1] is a novel end-to-end neural model for speaker diarization, trained with unconventional objectives compared to existing end-to-end diarization models.

<div align="center">
    <img src="sortformer_intro.png" width="750" />
</div>

Sortformer resolves permutation problem in diarization following the arrival-time order of the speech segments from each speaker. 

## Discover more from NVIDIA:
For documentation, deployment guides, enterprise-ready APIs, and the latest open models—including Nemotron and other cutting-edge speech, translation, and generative AI—visit the NVIDIA Developer Portal at [developer.nvidia.com](https://developer.nvidia.com/).
Join the community to access tools, support, and resources to accelerate your development with NVIDIA’s NeMo, Riva, NIM, and foundation models.<br>

### Explore more from NVIDIA:  <br>
What is [Nemotron](https://www.nvidia.com/en-us/ai-data-science/foundation-models/nemotron/)?<br>
NVIDIA Developer [Nemotron](https://developer.nvidia.com/nemotron)<br>
[NVIDIA Riva Speech](https://developer.nvidia.com/riva?sortBy=developer_learning_library%2Fsort%2Ffeatured_in.riva%3Adesc%2Ctitle%3Aasc#demos)<br>
[NeMo Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)<br>

## Model Architecture

Sortformer consists of an L-size (18 layers) [NeMo Encoder for
Speech Tasks (NEST)](https://arxiv.org/abs/2408.13106)[2] which is based on [Fast-Conformer](https://arxiv.org/abs/2305.05084)[3] encoder. Following that, an 18-layer Transformer[4] encoder with hidden size of 192, 
and two feedforward layers with 4 sigmoid outputs for each frame input at the top layer. More information can be found in the [Sortformer paper](https://arxiv.org/abs/2409.06656)[1].

<div align="center">
    <img src="sortformer-v1-model.png" width="450" />
</div>

## NVIDIA NeMo

To train, fine-tune or perform diarization with Sortformer, you will need to install [NVIDIA NeMo](https://github.com/NVIDIA/NeMo)[5]. We recommend you install it after you've installed Cython and latest PyTorch version.

```
apt-get update && apt-get install -y libsndfile1 ffmpeg
pip install Cython packaging
pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]
```

## How to Use this Model

The model is available for use in the NeMo Framework[5], and can be used as a pre-trained checkpoint for inference or for fine-tuning on another dataset.

### Loading the Model

```python
from nemo.collections.asr.models import SortformerEncLabelModel

# load model from Hugging Face model card directly (You need a Hugging Face token)
diar_model = SortformerEncLabelModel.from_pretrained("nvidia/diar_sortformer_4spk-v1")

# If you have a downloaded model in "/path/to/diar_sortformer_4spk-v1.nemo", load model from a downloaded file
diar_model = SortformerEncLabelModel.restore_from(restore_path="/path/to/diar_sortformer_4spk-v1.nemo", map_location='cuda', strict=False)


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

### Getting Diarization Results
To perform speaker diarization and get a list of speaker-marked speech segments in the format 'begin_seconds, end_seconds, speaker_index', simply use:
```python3
predicted_segments = diar_model.diarize(audio=audio_input, batch_size=1)
```
To obtain tensors of speaker activity probabilities, use:
```python3
predicted_segments, predicted_probs = diar_model.diarize(audio=audio_input, batch_size=1, include_tensor_outputs=True)
```

### Input

This model accepts single-channel (mono) audio sampled at 16,000 Hz.
- The actual input tensor is a Ns x 1 matrix for each audio clip, where Ns is the number of samples in the time-series signal. 
- For instance, a 10-second audio clip sampled at 16,000 Hz (mono-channel WAV file) will form a 160,000 x 1 matrix.

### Output

The output of the model is a T x S matrix, where:  
- S is the maximum number of speakers (in this model, S = 4).  
- T is the total number of frames, including zero-padding. Each frame corresponds to a segment of 0.08 seconds of audio.  
- Each element of the T x S matrix represents the speaker activity probability in the [0, 1] range.  For example, a matrix element a(150, 2) = 0.95 indicates a 95% probability of activity for the second speaker during the time range [12.00, 12.08] seconds.


## Train and evaluate Sortformer diarizer using NeMo
### Training

Sortformer diarizer models are trained on 8 nodes of 8×NVIDIA Tesla V100 GPUs. We use 90 second long training samples and batch size of 4.
The model can be trained using this [example script](https://github.com/NVIDIA/NeMo/blob/main/examples/speaker_tasks/diarization/neural_diarizer/sortformer_diar_train.py) and [base config](https://github.com/NVIDIA/NeMo/blob/main/examples/speaker_tasks/diarization/conf/neural_diarizer/sortformer_diarizer_hybrid_loss_4spk-v1.yaml).

### Evaluation

To evaluate Sortformer diarizer and save diarization results in RTTM format, use the inference [example script](https://github.com/NVIDIA/NeMo/blob/main/examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py):
```bash
python ${NEMO_GIT_FOLDER}/examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py 
 model_path="/path/to/diar_sortformer_4spk-v1.nemo" \
 manifest_filepath="/path/to/multispeaker_manifest_with_reference_rttms.json" \
 collar=COLLAR \
 out_rttm_dir="/path/to/output_rttms"
```

You can provide the post-processing YAML configs from [`post_processing` folder](https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization/conf/post_processing) to reproduce the optimized post-processing algorithm for each development dataset:
```bash
python ${NEMO_GIT_FOLDER}/examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py \
 model_path="/path/to/diar_sortformer_4spk-v1.nemo" \
 manifest_filepath="/path/to/multispeaker_manifest_with_reference_rttms.json" \
 collar=COLLAR \
 bypass_postprocessing=False \
 postprocessing_yaml="/path/to/postprocessing_config.yaml" \
 out_rttm_dir="/path/to/output_rttms"
```

### Technical Limitations

- The model operates in a non-streaming mode (offline mode).
- It can detect a maximum of 4 speakers; performance degrades on recordings with 5 and more speakers.
- The maximum duration of a test recording depends on available GPU memory. For an RTX A6000 48GB model, the limit is around 12 minutes.
- The model was trained on publicly available speech datasets, primarily in English. As a result:
    * Performance may degrade on non-English speech.
    * Performance may also degrade on out-of-domain data, such as recordings in noisy conditions.


## Datasets

Sortformer was trained on a combination of 2030 hours of real conversations and 5150 hours or simulated audio mixtures generated by [NeMo speech data simulator](https://arxiv.org/abs/2310.12371)[6].
All the datasets listed above are based on the same labeling method via [RTTM](https://web.archive.org/web/20100606092041if_/http://www.itl.nist.gov/iad/mig/tests/rt/2009/docs/rt09-meeting-eval-plan-v2.pdf) format. A subset of RTTM files used for model training are processed for the speaker diarization model training purposes.
Data collection methods vary across individual datasets. For example, the above datasets include phone calls, interviews, web videos, and audiobook recordings. Please refer to the [Linguistic Data Consortium (LDC) website](https://www.ldc.upenn.edu/) or dataset webpage for detailed data collection methods.


### Training Datasets (Real conversations)
- Fisher English (LDC)
- 2004-2010 NIST Speaker Recognition Evaluation (LDC)
- Librispeech 
- AMI Meeting Corpus
- VoxConverse-v0.3
- ICSI
- AISHELL-4
- Third DIHARD Challenge Development (LDC)
- 2000 NIST Speaker Recognition Evaluation, split1 (LDC)

### Training Datasets (Used to simulate audio mixtures)
- 2004-2010 NIST Speaker Recognition Evaluation (LDC)
- Librispeech

## Performance


### Evaluation dataset specifications

| **Dataset**                   | **DIHARD3-Eval**   | **CALLHOME-part2**  | **CALLHOME-part2**  | **CALLHOME-part2**  | **CH109**          |
|:------------------------------|:------------------:|:-------------------:|:-------------------:|:-------------------:|:------------------:|
| **Number of Speakers**        | ≤ 4 speakers       | 2 speakers          | 3 speakers          | 4 speakers          | 2 speakers         |
| **Collar (sec)**              | 0.0s               | 0.25s               | 0.25s               | 0.25s               | 0.25s              |
| **Mean Audio Duration (sec)** | 453.0s             | 73.0s               | 135.7s              | 329.8s              | 552.9s             |

### Diarization Error Rate (DER)

* All evaluations include overlapping speech.  
* Bolded and italicized numbers represent the best-performing Sortformer evaluations.
* Post-Processing (PP) is optimized on two different held-out dataset splits. 
    - [YAML file for DH3-dev Optimized Post-Processing](https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization/conf/post_processing/sortformer_diar_4spk-v1_dihard3-dev.yaml)    
    - [YAML file for CallHome-part1 Optimized Post-Processing](https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization/conf/post_processing/sortformer_diar_4spk-v1_callhome-part1.yaml)    


| **Dataset**                                               | **DIHARD3-Eval**   | **CALLHOME-part2**  | **CALLHOME-part2**  | **CALLHOME-part2**  | **CH109**          |
|:----------------------------------------------------------|:------------------:|:-------------------:|:-------------------:|:-------------------:|:------------------:|
| DER **diar_sortformer_4spk-v1**                           | 16.28              | 6.49                | 10.01               | 14.14               | **_6.27_**         |
| DER **diar_sortformer_4spk-v1 + DH3-dev Opt. PP**         | **_14.76_**        | -                   | -                   | -                   | -                  |
| DER **diar_sortformer_4spk-v1 + CallHome-part1 Opt. PP**  | -                  | **_5.85_**          | **_8.46_**          | **_12.59_**         | 6.86               |

### Real Time Factor (RTFx)

All tests were measured on RTX A6000 48GB with batch size of 1. Post-processing is not included in RTFx calculations.

| **Datasets**                      |  **DIHARD3-Eval**   | **CALLHOME-part2**  | **CALLHOME-part2**  | **CALLHOME-part2**  | **CH109**          |
|:----------------------------------|:-------------------:|:-------------------:|:-------------------:|:-------------------:|:------------------:|
| RTFx **diar_sortformer_4spk-v1**  |  437                | 1053                | 915                 | 545                 | 415                |


## NVIDIA Riva: Deployment

[NVIDIA Riva](https://developer.nvidia.com/riva), is an accelerated speech AI SDK deployable on-prem, in all clouds, multi-cloud, hybrid, on edge, and embedded. 
Additionally, Riva provides: 

* World-class out-of-the-box accuracy for the most common languages with model checkpoints trained on proprietary data with hundreds of thousands of GPU-compute hours 
* Best in class accuracy with run-time word boosting (e.g., brand and product names) and customization of acoustic model, language model, and inverse text normalization 
* Streaming speech recognition, Kubernetes compatible scaling, and enterprise-grade support 

Although this model isn’t supported yet by Riva, the [list of supported models](https://huggingface.co/models?other=Riva) is here.  
Check out [Riva live demo](https://developer.nvidia.com/riva#demos). 


## References
[1] [Sortformer: Seamless Integration of Speaker Diarization and ASR by Bridging Timestamps and Tokens](https://arxiv.org/abs/2409.06656)

[2] [NEST: Self-supervised Fast Conformer as All-purpose Seasoning to Speech Processing Tasks](https://arxiv.org/abs/2408.13106)

[3] [Fast Conformer with Linearly Scalable Attention for Efficient Speech Recognition](https://arxiv.org/abs/2305.05084)

[4] [Attention is all you need](https://arxiv.org/abs/1706.03762)

[5] [NVIDIA NeMo Framework](https://github.com/NVIDIA/NeMo)

[6] [NeMo speech data simulator](https://arxiv.org/abs/2310.12371)

## Licence

License to use this model is covered by the [CC-BY-NC-4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode). By downloading the public and release version of the model, you accept the terms and conditions of the CC-BY-NC-4.0 license.