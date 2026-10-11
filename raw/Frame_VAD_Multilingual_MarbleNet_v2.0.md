---
license: other
language:
- en
- es
- fr
- de
- ru
- zh
metrics:
- roc_auc
pipeline_tag: voice-activity-detection
library_name: nemo
tags:
- Multilingual
- MarbleNet
- pytorch
- speech
- audio
- VAD
- onnx
- onnxruntime
---
# Frame-VAD Multilingual MarbleNet v2.0 

## Description:

Frame-VAD Multilingual MarbleNet v2.0 is a convolutional neural network for voice activity detection (VAD) that serves as the first step for Speech Recognition and Speaker Diarization. It is a frame-based model that outputs a speech probability for each 20 millisecond frame of the input audio. The model has 91.5K parameters, making it lightweight and efficient for real-time applications. <br>
To reduce false positive errors — cases where the model incorrectly detects speech when none is present — the model was trained with white noise and real-word noise perturbations. During training, the volume of audios was also varied. Additionally, the training data includes non-speech audio samples to help the model distinguish between speech and non-speech sounds (such as coughing, laughter, and breathing, etc.) <br>

**Key Features**
- Lightweight model with only 91.5K parameters
- Robust against false positive errors
- Outputs speech probability for each 20 ms audio frame
- Multilingual support: Chinese, English, French, German, Russian, and Spanish

This model is ready for commercial use. <br>

### License/Terms of Use:
GOVERNING TERMS: Your use of this model is governed by the [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license).


### Deployment Geography:

Global <br>

### Use Case:

Developers, speech processing engineers, and AI researchers will use it as the first step for other speech processing models. <br>

## References:
[1] [Jia, Fei, Somshubra Majumdar, and Boris Ginsburg. "MarbleNet: Deep 1D Time-Channel Separable Convolutional Neural Network for Voice Activity Detection." ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP). IEEE, 2021.](https://arxiv.org/abs/2010.13886)  <br>
[2] [NVIDIA NeMo Toolkit](https://github.com/NVIDIA/NeMo)
<br> 

## Model Architecture:

**Architecture Type:**  Convolutional Neural Network (CNN) <br>
**Network Architecture:** MarbleNet <br>

**This model has 91.5K parameters** <br>

## Input: <br>
**Input Type(s):** Audio <br>
**Input Format:** .wav files <br>
**Input Parameters:** 1D <br>
**Other Properties Related to Input:** 16000 Hz Mono-channel Audio, Pre-Processing Not Needed <br>

## Output: <br>
**Output Type(s):** Sequence of speech probabilities for each 20 millisecond frame <br>
**Output Format:** Float Array <br>
**Output Parameters:** 1D <br>
**Other Properties Related to Output:** May need post-processing, such as smoothing, which reduces sudden fluctuations in detected speech probability for more natural transitions, and thresholding, which sets a cutoff value to determine whether a frame contains speech based on probability (e.g., classifying frames above 0.5 as speech and others as silence or noise). <br>

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA’s hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.



## How to Use the Model:
To train, fine-tune or play with the model you will need to install [NVIDIA NeMo](https://github.com/NVIDIA/NeMo).

```bash
pip install -U nemo_toolkit['asr']
``` 
The model is available for use in the NeMo toolkit [2], and can be used as a pre-trained checkpoint for inference.

### Automatically load the model

```python
import torch
import nemo.collections.asr as nemo_asr
vad_model = nemo_asr.models.EncDecFrameClassificationModel.from_pretrained(model_name="nvidia/frame_vad_multilingual_marblenet_v2.0")

# Move the model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vad_model = vad_model.to(device)
vad_model.eval()
```

### Inference with PyTorch
First, let's get a sample
```bash
wget https://dldata-public.s3.us-east-2.amazonaws.com/2086-149220-0033.wav
```
Then run the following:

```python
import librosa

# Load the audio
input_signal = librosa.load("2086-149220-0033.wav", sr=16000, mono=True)[0]
input_signal = torch.tensor(input_signal).unsqueeze(0).float()
input_signal_length = torch.tensor([input_signal.shape[1]]).long()

# Perform inference
with torch.no_grad():
   torch_outputs = vad_model(
        input_signal=input_signal.to(device),
        input_signal_length=input_signal_length.to(device)
    ).cpu()
```

### Export to ONNX

```python
import onnx 
from nemo.core import typecheck
typecheck.set_typecheck_enabled(False)

vad_model = vad_model.cpu()
ONNX_EXPORT_PATH = "frame_vad_multilingual_marblenet_v2.0.onnx"

# Preprocess input signal
processed_signal, processed_signal_length = vad_model.preprocessor(
    input_signal=input_signal,
    length=input_signal_length
)

# Define input example for ONNX export
inputs = {
    "processed_signal": processed_signal,
    "processed_signal_length": processed_signal_length
}

# Export
torch.onnx.export(
    model=vad_model,
    args=inputs,
    f=ONNX_EXPORT_PATH,
    input_names=list(inputs.keys()),
    output_names=["output"],
    dynamic_axes={
        "processed_signal": {0: "batch_size", 2: "sequence_length"},
        "processed_signal_length": {0: "batch_size"},
        "output": {0: "batch_size", 1: "sequence_length"}
    }
)
```

### Inference with ONNX Runtime
```python
import onnxruntime

# Load the ONNX model
session = onnxruntime.InferenceSession(
    ONNX_EXPORT_PATH, 
    providers=["CPUExecutionProvider"]
)

# Prepare input for ONNX Runtime
ort_inputs = {
    input.name: inputs[input.name].numpy()
    for input in session.get_inputs()
}

# Run inference
onnx_outputs = session.run(None, ort_inputs)[0]
```

### RTTM Output from Frame-Level Speech Predictions

To generate RTTM (Rich Transcription Time Marked) files from audio using the pretrained model:
```bash
python <NEMO_ROOT>/examples/asr/speech_classification/frame_vad_infer.py \
  --config-path="../conf/vad" \
  --config-name="frame_vad_infer_postprocess.yaml" \
  vad.model_path="nvidia/frame_vad_multilingual_marblenet_v2.0" \
  vad.parameters.shift_length_in_sec=0.02 \
  prepare_manifest.auto_split=True \
  prepare_manifest.split_duration=7200 \
  input_manifest=<Path of manifest file of evaluation data, where audio files should have unique names> \
  out_manifest_filepath=<Path of output manifest file>
```

## Software Integration:
**Runtime Engine(s):** 
* NeMo-2.3.0 <br> 

**Supported Hardware Microarchitecture Compatibility:** <br>
* [NVIDIA Ampere] <br>
* [NVIDIA Blackwell] <br>
* [NVIDIA Jetson]  <br>
* [NVIDIA Hopper] <br>
* [NVIDIA Lovelace] <br>
* [NVIDIA Pascal] <br>
* [NVIDIA Turing] <br>
* [NVIDIA Volta] <br>

## Preferred/Supported Operating System(s):
* [Linux] <br>

## Model Version(s):
Frame-VAD Multilingual MarbleNet v2.0  <br>

## Training, Testing, and Evaluation Datasets:

### Training Dataset:
**Link:**  
1. [ICSI (en)](https://groups.inf.ed.ac.uk/ami/icsi/download/)
2. [AMI (en)](https://groups.inf.ed.ac.uk/ami/corpus/)
3. [MLS (fr, es)](https://www.openslr.org/94/)
4. [MCV7 (de, ru)](https://commonvoice.mozilla.org/en/datasets)
5. [RULS (ru)](https://www.openslr.org/96/)
6. [SOVA (ru)](https://github.com/sovaai/sova-dataset)
7. [Aishell2 (zh)](https://www.aishelltech.com/)
8. [Librispeech (en)](https://www.openslr.org/12)
9. [Fisher (en)](https://www.ldc.upenn.edu/)
10. [MUSAN (noise)](https://www.openslr.org/17/)
11. [Freesound (noise)](https://freesound.org/)
12. [Vocalsound (noise)](https://github.com/YuanGongND/vocalsound)
13. [Ichbi (noise)](https://bhichallenge.med.auth.gr/ICBHI_2017_Challenge)
14. [Coswara (noise)](https://github.com/iiscleap/Coswara-Data) <br>

Data Collection Method by dataset:  <br>
* Hybrid: Human, Annotated, Synthetic <br>


Labeling Method by dataset:  <br>
* Hybrid: Human, Annotated, Synthetic <br>

**Properties:**
2600 hours of real-world data, 1000 hours of synthetic data, and 330 hours of noise data
<br>


### Testing Dataset:

**Link:** 
1. [Freesound (noise)](https://freesound.org/)
2. [MUSAN (noise)](https://www.openslr.org/17/)
3. [Librispeech (en)](https://www.openslr.org/12)
4. [Fisher (en)](https://www.ldc.upenn.edu/)
5. [MLS (fr, es)](https://www.openslr.org/94/)
6. [MCV7 (de, ru)](https://commonvoice.mozilla.org/en/datasets)
7. [AMI (en)](https://groups.inf.ed.ac.uk/ami/corpus/)
8. [Aishell2 (zh)](https://www.aishelltech.com/)
9. [CH109 (en)](https://catalog.ldc.upenn.edu/LDC97S42)  <br>

Data Collection Method by dataset:  <br>
* Hybrid: Human, Annotated <br>

Labeling Method by dataset:  <br>
* Hybrid: Human, Annotated <br>


**Properties:**
Around 100 hours of multilingual (Chinese, English, French, German, Russian, Spanish) audio data  <br>


### Evaluation Dataset:

**Link:** 
1. [VoxConverse-test](https://github.com/joonson/voxconverse/tree/master)
2. [VoxConverse-dev](https://github.com/joonson/voxconverse/tree/master)
3. [AMI-test](https://github.com/BUTSpeechFIT/AMI-diarization-setup/tree/main/only_words/rttms)
4. [Earnings21](https://github.com/revdotcom/speech-datasets/tree/main/earnings21)
5. [AISHELL4-test](https://www.openslr.org/111/)
6. [CH109](https://catalog.ldc.upenn.edu/LDC97S42)
7. [AVA-SPEECH](https://github.com/rafaelgreca/ava-speech-downloader) <br>

Data Collection Method by dataset:  <br>
* Hybrid: Human, Annotated <br>

Labeling Method by dataset:  <br>
* Hybrid: Human, Annotated <br>

**Properties:** 
Around 182 hours of multilingual (Chinese, English) audio data <br>


# Inference:
**Engine:** NVIDIA NeMo <br>
**Test Hardware:** <br>  
* RTX 5000 <br>
* A100 <br>
* V100  <br>

# Performance:
The ROC-AUC performance is listed in the following table. A higher ROC-AUC indicates better performance.

| Eval Dataset     |  ROC-AUC |
|------------------|----------|
| VoxConverse-test |   96.65  |
| VoxConverse-dev  |   97.59  |
| AMI-test         |   96.25  |
| Earnings21       |   97.11  |
| AISHELL4-test    |   92.27  |
| CH109            |   94.44  |
| AVA-SPEECH       |   95.26  |


## Ethical Considerations
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

For more detailed information on ethical considerations for this model, please see the Model Card++ Explainability, Bias, Safety & Security, and Privacy Subcards [here](https://developer.nvidia.com/blog/enhancing-ai-transparency-and-ethical-considerations-with-model-card/).

Please report security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

## Bias

Field                                                                                               |  Response
:---------------------------------------------------------------------------------------------------|:---------------
Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing:  |  None
Measures taken to mitigate against unwanted bias:                                                   |  To reduce false positive errors — cases where the model incorrectly detects speech when none is present — the model was trained with white noise and real-word noise perturbations. During training, the volume of audios was also varied. Additionally, the training data includes non-speech audio samples to help the model distinguish between speech and non-speech sounds (such as coughing, laughter, and breathing, etc.) 
Bias Metric (If Measured):                                                   |  False Positive Rate


## Explainability

Field                                                                                                  |  Response
:------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------
Intended Domain:                                                                   |  Voice Activity Detection (VAD)
Model Type:                                                                                            |  Convolutional Neural Network (CNN)
Intended Users:                                                                                        |  Developers, Speech Processing Engineers, AI Researchers
Output:                                                                                                |  Sequence of speech probabilities for each 20 millisecond audio frame
Describe how the model works:                                                                          |  The model processes input audio by extracting spectrogram features, which are then passed through MarbleNet—a lightweight CNN-based model designed for VAD. The CNN learns to detect patterns associated with speech activity and outputs a probability score indicating the presence of speech in each 20 millisecond frame
Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of:  |  Not Applicable
Technical Limitations:                                                                                 |  The model operates on 20 millisecond frames. While it supports longer frames by breaking them into smaller segments, it does not support outputs with a finer granularity than 20 milliseconds.
Verified to have met prescribed NVIDIA quality standards:  |  Yes
Performance Metrics:                                                                                   |  Accuracy (False Positive Rate, ROC-AUC score), Latency, Throughput
Potential Known Risks:                                                                                 |  While the model was trained on a limited number of languages, including Chinese, English, French, Spanish, German, and Russian, the model may experience a degradation in quality for languages and accents that are not included in the training dataset
Licensing:                                                                                             |  [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license)


## Privacy

Field                                                                                                                              |  Response
:----------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------
Generatable or reverse engineerable personal data?                                                     |  None
Personal data used to create this model?                                                                                       |  None
How often is dataset reviewed?                                                                                                     |  Before Release
Is there provenance for all datasets used in training?                                                                                |  Yes
Does data labeling (annotation, metadata) comply with privacy laws?                                                                |  Yes
Is data compliant with data subject requests for data correction or removal, if such a request was made?                           |  Yes


## Safety

Field                                               |  Response
:---------------------------------------------------|:----------------------------------
Model Application(s):                               |  Automatic Speech Recognition, Speaker Diarization, Speech Processing, Voice Activity Detection
List types of specific high-risk AI systems, if any, in which the model can be integrated: Select from the following: [Biometrics] OR [Critical infrastructure] OR [Machinery and Robotics] OR [Medical Devices] OR [Vehicles] OR [Aviation] OR [Education and vocational training] OR [Employment and Workers Management] <br>
Describe the life critical impact (if present).   |  Not Applicable
Use Case Restrictions:                              |  Abide by [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license)
Model and dataset restrictions:            |  The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to.