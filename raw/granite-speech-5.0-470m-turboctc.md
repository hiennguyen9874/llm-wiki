---
license: apache-2.0
language:
- en
pipeline_tag: automatic-speech-recognition
library_name: transformers
---
# Granite-Speech-5.0-470M-TurboCTC

**Model Summary:**
Granite Speech 5.0 TurboCTC is a compact 470 million parameter English ASR model with very high inference speed that is well suited for deployment on laptops, smartphones and other edge devices. 
The model consists of a conformer acoustic encoder with block self-attention, self-conditioning and temporal downsampling with an output layer corresponding to 16,384 BPE units. 
It was trained on approximately 60,000 hours of English audio from public corpora using Connectionist Temporal Classification (CTC) and inference is done non-autoregressively with greedy decoding.

**Evaluations:**

We evaluated granite-speech-5.0-470m-turboctc on standard short-form English ASR benchmarks from the [Open ASR leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard): 
<br>
![granite-5.0-470m-turboctc-wer](https://cdn-uploads.huggingface.co/production/uploads/666ec38102791b3b49f453e8/VBgBUgcpMuLdIcWr-XPbw.png)

Performance on the [Open ASR leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) (official results as of October 2, 2026, RTFx measured on 1 H200):
<br>
![newplot-4-readable](https://cdn-uploads.huggingface.co/production/uploads/666ec38102791b3b49f453e8/NPV5UHWFvVtRUYbU8rqza.png)
![pareto-size-readable](https://cdn-uploads.huggingface.co/production/uploads/666ec38102791b3b49f453e8/7VYpkH8Y7N3AoN4QO8bWX.png)
<br>
Performance on noisy and reverberant speech from the [FFASR leaderboard](https://huggingface.co/spaces/treble-technologies/ffasr) (official results as of August 25, 2026, RTFx measured on 1 L4 GPU)
<br>
![ffasr_wer](https://cdn-uploads.huggingface.co/production/uploads/666ec38102791b3b49f453e8/Cr-4eYJGdX8wDjbysu8_E.png)
![ffasr_rtfx](https://cdn-uploads.huggingface.co/production/uploads/666ec38102791b3b49f453e8/t5tJRlk4RgjZXaKrIVb0K.png)
<br>

**Release Date**: August 25, 2026 

**License:** [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

**Supported Languages:**
English

**Intended Use:**
The model is intended to be used in enterprise applications that involve accurate low-latency/high-throughput English speech-to-text transcription. 

## Usage:

### Usage with `transformers`
Granite Speech 5.0 TurboCTC is supported natively in `transformers>=5.16.0`:

```shell
pip install transformers>=5.16.0 datasets
```

```python
from datasets import Audio, load_dataset
from transformers import AutoModelForCTC, AutoProcessor

model_id = "ibm-granite/granite-speech-5.0-470m-turboctc"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForCTC.from_pretrained(model_id, device_map="auto")

ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
ds = ds.cast_column("audio", Audio(sampling_rate=processor.feature_extractor.sampling_rate))
speech_samples = [el["array"] for el in ds["audio"][:5]]

# `device` computes the log-mel front-end on the model's accelerator, saving a host-to-device copy
inputs = processor(
    speech_samples, sampling_rate=processor.feature_extractor.sampling_rate, device=model.device
)
inputs.to(model.device, dtype=model.dtype)
outputs = model.generate(**inputs)
print(processor.batch_decode(outputs, skip_special_tokens=True))
```

### Usage with `mlx-audio` for Apple Silicon M series chips

Install a recent version of mlx-audio (0.5.1 or later):
```shell
pip install -U mlx-audio
```
Sample use:
```shell
python -m mlx_audio.stt.generate --model ibm-granite/granite-speech-5.0-470m-turboctc --verbose --audio "audio.wav" --output-path "transcript"
```

### Usage with `transcribe.cpp` for local GGUF inference

[transcribe.cpp](https://github.com/handy-computer/transcribe.cpp) runs the model from a
quantized GGUF on Metal, Vulkan, CUDA, ROCm, or CPU, with no Python at runtime. Build it,
then fetch a pre-quantized GGUF:

```shell
git clone https://github.com/handy-computer/transcribe.cpp
cd transcribe.cpp && cmake -B build && cmake --build build
hf download handy-computer/granite-speech-5.0-470m-turboctc-gguf \
  granite-speech-5.0-470m-turboctc-Q8_0.gguf --local-dir models
```

Sample use:
```shell
build/bin/transcribe-cli -q -m models/granite-speech-5.0-470m-turboctc-Q8_0.gguf samples/love-loss.wav
```

**Model Architecture:** 

The architecture of granite-speech-5.0-470m-turboctc consists of 16 conformer blocks trained with Connectionist Temporal Classification (CTC) with a 16,384 BPE classification head (see configuration below).
We perform temporal subsampling by a factor of 8 to reduce frame rates from 100Hz to 12.5Hz: first by stacking and skipping consecutive logmel+delta frames (2x) followed by strided convolutions and pooled residuals in the first two conformer blocks (4x) as shown in the figure below.
In addition, the encoder uses block-attention with blocks of 128 frames and self-conditioned CTC from the middle layer. 

| Configuration parameter  | Value                | 
|-----------------|----------------------|
| Input dimension | 320 (80 logmels + 80 deltas) x 2 | 
| Nb. of layers   | 16                   | 
| Hidden dimension | 1024                | 
| Nb. of attention heads | 8             | 
| Attention head size    | 128           |
| Attention block size   | 128           | 
| Convolution kernel size | 7           | 
| Output dimension (BPE) | 16384  |

![conformer_blocks](https://cdn-uploads.huggingface.co/production/uploads/666ec38102791b3b49f453e8/lSCAUruBQ6bdHguqTKvFO.png)

## Training Data: 

Our training data is entirely comprised of publicly available datasets or of synthetic data generated from public corpora specifically targeting English ASR. 
A detailed description of the training datasets can be found in the table below:

| Name | Nb. hours | Source |
|-----------|----------------|--------------|
| CommonVoice-17 | 2500 |   https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0 |
| MLS            | 44600 |   https://huggingface.co/datasets/facebook/multilingual_librispeech |
| Librispeech    | 960 |  https://huggingface.co/datasets/openslr/librispeech_asr | 
| VoxPopuli      | 500 |  https://huggingface.co/datasets/facebook/voxpopuli | 
| YODAS          | 8900 |  https://huggingface.co/datasets/espnet/yodas |
| AMI            | 150 | https://huggingface.co/datasets/edinburghcstr/ami | 
| Earnings-22    | 100 | https://huggingface.co/datasets/esb/datasets | 

In addition, the model was trained on three synthetic datasets:

1. 2000 hours of multi-speaker data generated by concatenating single-speaker segments from MLS, YODAS, CommonVoice-17, VoxPopuli, and AMI;
2. 500 hours of multi-speaker data generated by concatenating single-speaker segments from Earnings-22; and
3. 240 hours of utterances containing numbers, currencies, website names, phone numbers, addresses, and items containing decimal points or dots which were generated using either `gpt-oss-120b` or `gpt-oss-20b` and synthesized using `StyleTTS2`.

**Infrastructure:**
We train Granite Speech TurboCTC using IBM's super computing cluster, Blue Vela, which is outfitted with NVIDIA H100 GPUs. This cluster provides a scalable
and efficient infrastructure for training our models over thousands of GPUs. The training of this particular model was completed in 10 days on 8
H100 GPUs.

**Resources**
- 📐 Technical report: https://arxiv.org/abs/2609.20104
- 📄 Blog post: https://huggingface.co/blog/ibm-granite/granite-speech-5-0-470m-turboctc
- 🔧 Notebooks: [finetune on custom data](https://colab.research.google.com/github/ibm-granite/granite-speech-models/blob/main/notebooks/finetune_granite_speech_5_turboctc.ipynb)
- ⭐️ Learn about the latest updates with Granite: https://www.ibm.com/granite
- 🚀 Get started with tutorials, best practices, and prompt engineering advice: https://www.ibm.com/granite/docs/
- 💡 Learn about the latest Granite learning resources: https://ibm.biz/granite-learning-resources

**Citation**

```bibtex
@misc{granite-speech-5.0-470m-turboctc,
  title={Granite Speech 5.0 TurboCTC},
  author={IBM Granite Speech Team},
  year={2026},
  url={https://huggingface.co/ibm-granite/granite-speech-5.0-470m-turboctc}
}
```