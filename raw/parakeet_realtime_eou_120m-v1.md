---
license: other
license_name: nvidia-open-model-license
license_link: >-
  https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/
language:
- en
metrics:
- wer
library_name: nemo
tags:
- speech-recognition
- FastConformer
- end-of-utterance
- voice agent
---

<style>
img {
 display: inline;
}
</style>

[![Model architecture](https://img.shields.io/badge/Model_Arch-FastConformer--RNNT-lightgrey#model-badge)](#model-architecture)
| [![Model size](https://img.shields.io/badge/Params-120M-lightgrey#model-badge)](#model-architecture)
<!-- | [![Language](https://img.shields.io/badge/Language-multilingual-lightgrey#model-badge)](#datasets) -->


# Model Overview


### Description:
Parakeet-Realtime-EOU-120m-v1 is a streaming speech recognition model that also performs end-of-utterance (EOU) detection. It achieves low latency (80ms~160 ms) and signals EOU by emitting an `<EOU>` token at the end of each utterance. The model supports only English and does not output punctuation or capitalization.

<div align="center">
    <img src="./figure-streaming.png" width="450" />
</div>


This model is designed for use in voice AI agent pipelines (e.g., [NeMo Voice Agent](https://github.com/NVIDIA-NeMo/NeMo/tree/main/examples/voice_agent)):
<div align="center">
    <img src="./voice-agent.png" width="750" />
</div>


This model is ready for commercial/non-commercial use. <br>

### License/Terms of Use

[NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/) <br> 

## Discover more from NVIDIA:
For documentation, deployment guides, enterprise-ready APIs, and the latest open models—including Nemotron and other cutting-edge speech, translation, and generative AI—visit the NVIDIA Developer Portal at [developer.nvidia.com](https://developer.nvidia.com/).
Join the community to access tools, support, and resources to accelerate your development with NVIDIA’s NeMo, Riva, NIM, and foundation models.<br>

### Explore more from NVIDIA:  <br>
What is [Nemotron](https://www.nvidia.com/en-us/ai-data-science/foundation-models/nemotron/)?<br>
NVIDIA Developer [Nemotron](https://developer.nvidia.com/nemotron)<br>
[NVIDIA Riva Speech](https://developer.nvidia.com/riva?sortBy=developer_learning_library%2Fsort%2Ffeatured_in.riva%3Adesc%2Ctitle%3Aasc#demos)<br>
[NeMo Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)<br>

## Model Architecture:
**Architecture Type:** FastConformer-RNNT [1] <br>

**Network Architecture:** cache-aware streaming FastConformer [2] with 17 encoder layers (attention context = [70,1]) and RNNT decoder. <br>

**Number of model parameters:** 120M <br>


### Input: <br>
**Input Type(s):** Audio <br>
**Input Format:** Audio waveform <br>
**Input Parameters:** 1-Dimensional <br>
**Other Properties Related to Input:** Single-channel audio in 16kHz sampling rate, at least 160ms duration is required. <br>

### Output: <br>
**Output Type(s):** Text with optional `<EOU>` token (e.g., "what is your name\<EOU\>") <br>
**Output Format:** String <br>
**Output Parameters:** 1-Dimensional <br>
**Other Properties Related to Output:** The output text might be empty if input audio doesn't contain any speech. <br>

## References(s):
[1] [Fast Conformer With Linearly Scalable Attention For Efficient Speech Recognition](https://arxiv.org/abs/2305.05084)  <br> 
[2] [Stateful Conformer with Cache-based Inference for Streaming Automatic Speech Recognition](https://arxiv.org/abs/2312.17279) <br>
[3] [NVIDIA NeMo Toolkit](https://github.com/NVIDIA-NeMo/NeMo)

## How to use this model

### Streaming usage with NeMo Voice Agent

This model is primarily designed for use in voice AI agents under streaming settings.
Please refer to [NeMo Voice Agent](https://github.com/NVIDIA-NeMo/NeMo/tree/main/examples/voice_agent) for examples on how to setup up a voice agent with 80ms ASR latency. 

To use this model in NeMo Voice Agent, set this in the server config [yaml](https://github.com/NVIDIA-NeMo/NeMo/blob/main/examples/voice_agent/server/server_configs/default.yaml):
```yaml
stt:
  type: nemo
  model: "nvidia/parakeet_realtime_eou_120m-v1"
```


### Offline usage

You will need to install [NVIDIA NeMo](https://github.com/NVIDIA/NeMo) [3]. We recommend you install it after you've installed latest PyTorch version.
```bash
pip install -U nemo_toolkit['asr']
``` 

The model can then be used in the offline setting showned below.


#### Automatically instantiate the model

```python
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet_realtime_eou_120m-v1")
```

#### Transcribing using Python
First, let's get a sample
```bash
wget https://dldata-public.s3.us-east-2.amazonaws.com/2086-149220-0033.wav
```
Then simply do:
```python
output = asr_model.transcribe(['2086-149220-0033.wav'])
print(output[0].text)
```


## Software Integration:
**Runtime Engine(s):** 
* NeMo 2.5.3+ <br>

**Supported Hardware Microarchitecture Compatibility:** <br>
* NVIDIA Ampere <br>
* NVIDIA Blackwell <br>
* NVIDIA Hopper  <br>
* NVIDIA Volta  <br>

**Preferred/Supported Operating System(s):**
* Linux <br>



## Model Version(s):
* parakeet_realtime_eou_120m-v1 <br>


## Training, Testing, and Evaluation Datasets: 
### Training Dataset:

- AMI
- DialogStudio (subset from task-oriented domain with commercial license) 
- Granary
- Google Speech Commands
- LibriTTS
- 10,000 hours from human-transcribed NeMo ASR Set 3.0, including:
  - LibriSpeech (960 hours)
  - Fisher Corpus
  - National Speech Corpus Part 1
  - VCTK
  - Europarl-ASR
  - Multilingual LibriSpeech
  - Mozilla Common Voice (v7.0)

** Data Collection Method <br>
* [Hybrid: Human, Synthetic] - Most audios are human recorded, but some are generated by TTS models with commercial license <br>

** Labeling Method <br>
* [Hybrid: Human, Synthetic] - Some transcripts are automatically generated by automatic speech recognition (ASR) models, while others are manually labeled. <br>



### Evaluation Dataset:

- HuggingFace ASR Leaderboard
    - AMI
    - Earnings22
    - Gigaspeech
    - LS-test-clean
    - LS-test-other
    - SPGI
    - Tedlium
    - Voxpopuli
- DialogStudio (subset from task-oriented domain with commercial license)


** Data Collection Method <br>
* [Hybrid: Human, Synthetic] - Most audios are human recorded, but some are generated by TTS models with commercial license <br>

** Labeling Method <br>
* [Hybrid: Human, Synthetic] - Some transcripts are generated by ASR models, while some are manually labeled <br>


### Benchmark Score <br>

#### Speech Recognition (Word Error Rate)

Word error rate (WER) on [HuggingFace OpenASR leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) measured in 160ms streaming setting. Text is normalized by [this normalizer](https://github.com/huggingface/open_asr_leaderboard/blob/main/normalizer/normalizer.py#L528) before caculating the metrics.

| Metric         | Average | AMI   | Earnings22 | Gigaspeech | LS-test-clean | LS-test-other | SPGI | Tedlium | Voxpopuli |
|----------------|---------|-------|------------|------------|---------------|----------------|------|---------|-----------|
| WER (%)        | 9.30    | 15.62 | 15.76      | 13.31      | 3.61          | 7.79           | 3.79 | 5.48    | 9.07      |


#### End-of-Utterance Detection (Latency)

The latency metrics are evaluated on TTS generated audios from DialogStudio, and a 3-second silence is appended to each sample. The actual performance on real-world scenarios will vary by acoustic environment, accents, etc.
| Percentile | Latency |
|---------|-----|
| 50% | 160ms |
| 90% | 280ms |
| 95% | 320ms |





## Inference:

**Acceleration Engine:** CUDA<br>

**Test Hardware:** <br>  
* NVIDIA V100 <br>
* NVIDIA A100 <br>
* NVIDIA A6000 <br>



## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br> 


Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).





