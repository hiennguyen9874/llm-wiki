---
license: other
license_name: nvidia-open-model-license
license_link: >-
  https://developer.download.nvidia.com/licenses/nvidia-open-model-license-agreement-june-2024.pdf
extra_gated_prompt: >-
  https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/
extra_gated_fields:
  Company: text
  Specific date: date_picker
  I want to use this model for:
    type: select
    options:
    - Commercial
    - Research
    - Education
    - label: Other
      value: other
  I agree to use this model with NVIDIA Open Model License: checkbox
extra_gated_description: Our team may take 2-3 days to process your request
extra_gated_button_content: Acknowledge license
language:
- vi
metrics:
- wer
pipeline_tag: automatic-speech-recognition
library_name: nemo
tags:
- Nemo
- ASR
- Pytorch
- FastConformer
- Parakeet
- CTC
- automatic-speech-recognition
- audio
- speech
---

# <span style="color:#76b900;">Parakeet-CTC-0.6B Unified Vietnamese–English CS

![Word Error Rate (WER) across multiple Vietnamese datasets](https://cdn-uploads.huggingface.co/production/uploads/6800b56c14b34410846bbf2d/PdJmwU_J0r0teGFQ3A800.png)
*Figure 1: ASR WER comparison across different model and CSPs. This does not include Punctuation and Capitalisation errors. Details about each testset are mentioned below.*

### <span style="color:#466f00;">Description:
This model [1] is trained on public automatic speech recognition (ASR) datasets totaling more than 2,000 hours of Vietnamese (vi) speech. The model uses Qwen3 to generate punctuation and capitalization (PnC) for the training transcripts. The language model is trained on Vietnamese Wikipedia and further enhanced with a Vietnamese dictionary and lists of proper names and place names. <br>

This model is ready for commercial/non-commercial use. <br>

### <span style="color:#466f00;">Deployment Geography:
Global <br>

### <span style="color:#466f00;">Use Case: <br>
This model serves developers, researchers, academics, and industries building applications that require speech-to-text capabilities, including but not limited to: conversational AI, voice assistants, transcription services, subtitle generation, and voice analytics platforms. <br>

## <span style="color:#466f00;">Model Architecture:
**Architecture Type:** Parakeet-CTC (also known as FastConformer-CTC) [1], [2] which is an optimized version of Conformer model [3] with 8x depthwise-separable convolutional downsampling with CTC loss. <br>

**Network Architecture:**  Parakeet-CTC-0.6B <br>

This model was developed based on FastConformer encoder architecture. <br>

Number of model parameters: 600 million model parameters. <br>

## <span style="color:#466f00;">Input(s): <br>
**Input Type(s):** Audio <br>

**Input Format(s):** .wav, .mp3, .flac, .ogg, .m4a <br>

**Input Parameters:** One-Dimensional (1D) <br>

**Other Properties Related to Input:** The maximum length (in seconds) specific to GPU memory, no pre-processing needed, a mono channel is required. <br>

## <span style="color:#466f00;">Output(s)

**Output Type(s):** Text <br>

**Output Format(s):** String <br>

**Output Parameters:** One-Dimensional (1D) <br>

**Other Properties Related to Output:** There is no maximum character length, and does not handle special characters. <br>

## <span style="color:#466f00;">How to use this model:
To train, fine-tune or play with the model you will need to install [NVIDIA NeMo](https://github.com/NVIDIA/NeMo). We recommend you install it after you've installed latest PyTorch version.
```bash
pip install -U nemo_toolkit['asr']
``` 
The model is available for use in the NeMo toolkit [3], and can be used as a pre-trained checkpoint for inference or for fine-tuning on another dataset.

#### Automatically instantiate the model

```python
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-ctc-0.6b-vi")
```

#### Transcribing using Python
Simply do:
```python
output = asr_model.transcribe(['path_to_audios'])
print(output[0].text)
```

#### Transcribing with timestamps

To transcribe with timestamps:
```python
output = asr_model.transcribe(['path_to_audios'], timestamps=True)
# by default, timestamps are enabled for char, word and segment level
word_timestamps = output[0].timestamp['word'] # word level timestamps for first sample
segment_timestamps = output[0].timestamp['segment'] # segment level timestamps
char_timestamps = output[0].timestamp['char'] # char level timestamps

for stamp in segment_timestamps:
    print(f"{stamp['start']}s - {stamp['end']}s : {stamp['segment']}")
```

#### Inference with n-gram language model
The [4-gram](https://huggingface.co/nvidia/parakeet-ctc-0.6b-Vietnamese/blob/main/lm_4gram_wiki_traintext_4x_vi_en_dict_newStyleTone_PnC_vi_en_2.0.bin) model and [lexicon](https://huggingface.co/nvidia/parakeet-ctc-0.6b-Vietnamese/blob/main/lm_4gram_wiki_traintext_4x_vi_en_dict_newStyleTone_PnC_vi_en_2.0_filtered.lexicon) provided in the repository can be used, or simply training and fine-tuning n-gram language model with KenLM and NeMo with this [tutorial](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/tutorials/asr-python-advanced-nemo-ngram-training-and-finetuning.html). 

To enhance the accuracy using n-gram language model:
```python
decoding_cfg = CTCDecodingConfig()

decoding_cfg.strategy = "flashlight"
decoding_cfg.beam.search_type = "flashlight"
decoding_cfg.beam.kenlm_path = f'path_to_model'
decoding_cfg.beam.flashlight_cfg.lexicon_path=f'path_to_lexicon'
decoding_cfg.beam.beam_size = 64
decoding_cfg.beam.beam_alpha = 0.3
decoding_cfg.beam.beam_beta = 0.5
decoding_cfg.beam.flashlight_cfg.beam_size_token = 32
decoding_cfg.beam.flashlight_cfg.beam_threshold = 20.0
    
asr_model.change_decoding_strategy(decoding_cfg)

output = asr_model.transcribe(['path_to_audios'])
print(output[0].text)
```

## <span style="color:#466f00;">Software Integration:
**Runtime Engine(s):** 
* Nemo - 2.6

**Supported Hardware Microarchitecture Compatibility:** <br>
* NVIDIA Ampere
* NVIDIA Blackwell  
* NVIDIA Hopper
* NVIDIA Volta

**Preferred/Supported Operating System(s):**
Linux <br>

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment. <br>

## <span style="color:#466f00;">Model Version(s):
 Parakeet-CTC-0.6B-unified ASR Vietnamese_1.1

## <span style="color:#466f00;">Training and Evaluation Datasets:

The total size: ~2000 hours <br>
Total number of datasets: 10 <br>

Training was conducted using this [example script](https://github.com/NVIDIA-NeMo/NeMo/blob/main/examples/asr/asr_ctc/speech_to_text_ctc_bpe.py) and [CTC configuration](https://github.com/NVIDIA-NeMo/NeMo/blob/main/examples/asr/conf/fastconformer/fast-conformer_ctc_bpe.yaml).

The tokenizer was constructed from the training set transcripts using this [script](https://github.com/NVIDIA/NeMo/blob/main/scripts/tokenizers/process_asr_text_tokenizer.py).


## Training Dataset:

- 2000 hours for training, including:
  - Common Voice Corpus 20.0
  - VietMed-L (16h)
  - LSVSC 
  - FLEURS
  - InfoRe 2
  - FOSD (FPT)
  - VAIS
  - VLSP 2020 
  - VSV-1100
  - MS-SNSD

Fleurs transcriptions is preserve punctuation and capitalization. The remaining transcriptions is generated punctuation and capitalization by [Qwen3](https://build.nvidia.com/qwen/qwen3-next-80b-a3b-instruct/modelcard) model. 

Data Modality <br>
* Other: Speech <br>

Audio Training Data Size (If Applicable) <br>
* Less than 10,000 Hours <br>

Data Collection Method by dataset <br>
* Hybrid:  Automated, Human

Labeling Method by dataset <br>
* Hybrid: Synthetic, Human  <br>

### Evaluation Dataset:

- Gigaspeech 2
- VLSP 2021 Task 2
- ViMD 
- VIVOS
- Common Voice Corpus 20.0
- FOSD
- LSVSC 
- FLEURS
- VLSP 2021 Task 1
- VietMed

Data Collection Method by dataset:  <br>

* Human <br>

Labeling Method by dataset:  <br>
* Human <br>

## <span style="color:#466f00;">Performance:
The performance of Automatic Speech Recognition (ASR) models is measured using Word Error Rate (WER). Given that this model is trained on a large and diverse dataset spanning multiple domains, it is generally more robust and accurate across various types of audio.

### Blind testset
| AVG WER | Gigaspeech2 | VLSP 2021 Task 2 | ViMD | VIVOS |
| ------  | ------ | ------ | ------ | ------ | 
| 9.30  |   11.23|   8.99     |   11.02     |   5.96     |

### In domain testset
| AVG WER | MCV-Vi-20 | FOSD | LSVSC | FLEURS |VLSP 2021 Task 1 |VietMed |
| ------ | ------ | ------ |------ |------ |------ |------ |
| 9.73 |    8.58    |   9.67     |   5.15     |   6.86     |  13.60     |   14.52     |

The VietMed benchmark testset has been fixed for transcript-audio misalignment.

# <span style="color:#466f00;">Inference:
**Acceleration Engine:** NVIDIA Nemo <br>

**Test Hardware:** <br>  

* NVIDIA A10 <br>
* NVIDIA A100 <br>
* NVIDIA A30 <br>
* NVIDIA H100 <br>
* NVIDIA Jetson Orin <br>
* NVIDIA L4 <br>
* NVIDIA L40 <br>
* NVIDIA Turing T4 <br>
* NVIDIA Volta V100 <br>
* NVIDIA Blackwell GPU <br>

## <span style="color:#466f00;">Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse. <br> 

Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).  <br>


### <span style="color:#466f00;">License/Terms of Use:
GOVERNING TERMS: Use of this model is governed by the NVIDIA Open Model License Agreement (found at [https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/)).

### <span style="color:#466f00;">Discover more from NVIDIA:</span> 
For documentation, deployment guides, enterprise-ready APIs, and the latest open models—including Nemotron and other cutting-edge speech, translation, and generative AI—visit the NVIDIA Developer Portal at developer.nvidia.com.
Join the community to access tools, support, and resources to accelerate your development with NVIDIA’s NeMo, Riva, NIM, and foundation models.<br>

#### <span style="color:#466f00;">Explore more from NVIDIA:</span>  <br>
What is [Nemotron](https://www.nvidia.com/en-us/ai-data-science/foundation-models/nemotron/)?<br>
NVIDIA Developer [Nemotron](https://developer.nvidia.com/nemotron)<br>
[NVIDIA Riva Speech](https://developer.nvidia.com/riva?sortBy=developer_learning_library%2Fsort%2Ffeatured_in.riva%3Adesc%2Ctitle%3Aasc#demos)<br>
[NeMo Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)<br>

## References(s):
[1] https://arxiv.org/abs/2305.05084 <br>
[2] https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html <br>
[3] https://arxiv.org/abs/2005.08100 <br>