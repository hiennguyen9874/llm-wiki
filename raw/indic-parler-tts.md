---
library_name: transformers
tags:
- text-to-speech
- annotation
license: apache-2.0
language:
- en
- as
- bn
- gu
- hi
- kn
- ks
- or
- ml
- mr
- ne
- pa
- sa
- sd
- ta
- te
- ur
- om
pipeline_tag: text-to-speech
inference: false
datasets:
- ai4b-hf/GLOBE-annotated
---

<img src="https://huggingface.co/datasets/parler-tts/images/resolve/main/Indic%20Parler-TTS.png" alt="Indic Parler Logo" width="800" style="margin-left:'auto' margin-right:'auto' display:'block'"/>

# Indic Parler-TTS

<a target="_blank" href="https://huggingface.co/spaces/ai4bharat/indic-parler-tts">
  <img src="https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-sm.svg" alt="Open in HuggingFace"/>
</a>

**Indic Parler-TTS** is a multilingual Indic extension of [Parler-TTS Mini](https://huggingface.co/parler-tts/parler-tts-mini-v1.1).

It is a fine-tuned version of [Indic Parler-TTS Pretrained](https://huggingface.co/ai4bharat/indic-parler-tts-pretrained), trained on a **1,806 hours** multilingual Indic and English dataset.

🚩 NOTE 🚩[Indic-Speak](https://huggingface.co/bodhan-ai/indic-speak) is now available. It supports 22 Indian languages and has better text-to-speech capabilities compared to Indic Parler-TTS. We recommend using Indic-Speak.

**Indic Parler-TTS Mini** can officially speak in 20 Indic languages, making it comprehensive for regional language technologies, and in English. The **21 languages** supported are: Assamese, Bengali, Bodo, Dogri, English, Gujarati, Hindi, Kannada, Konkani, Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Sanskrit, Santali, Sindhi, Tamil, Telugu, and Urdu.

Thanks to its **better prompt tokenizer**, it can easily be extended to other languages. This tokenizer has a larger vocabulary and handles byte fallback, which simplifies multilingual training.

🚨 This work is the result of a collaboration between the **HuggingFace audio team** and the **[AI4Bharat](https://ai4bharat.iitm.ac.in/) team**. 🚨


## 📖 Quick Index
* [👨‍💻 Installation](#👨‍💻-installation)
* [🛠️ Key capabilities](#🛠️-key-capabilities)
* [🎲 Using a random voice](#🎲-random-voice)
* [🌍 Switching languages](#[🌍-switching-languages)
* [🎯 Using a specific speaker](#🎯-using-a-specific-speaker)
* [Some Description Examples](#some-description-examples)
* [📐Evaluation](#📐-evaluation)
* [Motivation](#motivation)
* [Optimizing inference](https://github.com/huggingface/parler-tts/blob/main/INFERENCE.md)

### 👨‍💻 Installation

Using Parler-TTS is as simple as "bonjour". Simply install the library once:

```sh
pip install git+https://github.com/huggingface/parler-tts.git
```

## 🛠️ Key capabilities

The model accepts two primary inputs:  
1. **Transcript** - The text to be converted to speech.  
2. **Caption** - A detailed description of how the speech should sound, e.g., "Leela speaks in a high-pitched, fast-paced, and cheerful tone, full of energy and happiness. The recording is very high quality with no background noise."  

### Key Features  

1. **Language Support**  
   - **Officially supported languages**: Assamese, Bengali, Bodo, Dogri, Kannada, Malayalam, Marathi, Sanskrit, Nepali, English, Telugu, Hindi, Gujarati, Konkani, Maithili, Manipuri, Odia, Santali, Sindhi, Tamil, and Urdu.  
   - **Unofficial support**: Chhattisgarhi, Kashmiri, Punjabi.  

2. **Speaker Diversity**  
   - **69 unique voices** across the supported languages.  
   - Supported languages have a set of **recommended voices** optimized for naturalness and intelligibility.  
   
3. **Emotion Rendering**  
   - **10 languages** officially support emotion-specific prompts: Assamese, Bengali, Bodo, Dogri, Kannada, Malayalam, Marathi, Sanskrit, Nepali, and Tamil.  
   - Emotion support for other languages exists but has not been extensively tested.  
   - **Available emotions** include: Command, Anger, Narration, Conversation, Disgust, Fear, Happy, Neutral, Proper Noun, News, Sad, and Surprise.  

4. **Accent Flexibility**  
   - The model **officially supports Indian English accents** through its English voices, providing clear and natural speech.  
   - For other accents, the model allows customization by specifying accent details, such as "A male British speaker" or "A female American speaker," using style transfer for more dynamic and personalized outputs.  

5. **Customizable Output**  
   Indic Parler-TTS offers precise control over various speech characteristics using the **caption** input:  

   - **Background Noise**: Adjust the noise level in the audio, from clear to slightly noisy environments.  
   - **Reverberation**: Control the perceived distance of the voice, from close-sounding to distant-sounding speech.  
   - **Expressivity**: Specify how dynamic or monotone the speech should be, ranging from expressive to slightly expressive or monotone.  
   - **Pitch**: Modify the pitch of the speech, including high, low, or balanced tones.  
   - **Speaking Rate**: Change the speaking rate, from slow to fast.  
   - **Voice Quality**: Control the overall clarity and naturalness of the speech, adjusting from basic to refined voice quality.


## 🎲 Random voice

🚨 Unlike previous versions of Parler-TTS, here we use two tokenizers - one for the prompt and one for the description. 🚨

**Indic Parler-TTS** has been trained to generate speech with features that can be controlled with a simple text prompt, for example:

```py
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

prompt = "Hey, how are you doing today?"
description = "A female speaker with a British accent delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

description_input_ids = description_tokenizer(description, return_tensors="pt").to(device)
prompt_input_ids = tokenizer(prompt, return_tensors="pt").to(device)

generation = model.generate(input_ids=description_input_ids.input_ids, attention_mask=description_input_ids.attention_mask, prompt_input_ids=prompt_input_ids.input_ids, prompt_attention_mask=prompt_input_ids.attention_mask)
audio_arr = generation.cpu().numpy().squeeze()
sf.write("indic_tts_out.wav", audio_arr, model.config.sampling_rate)
```

Indic Parler-TTS provides highly effective control over key aspects of speech synthesis using descriptive captions. Below is a summary of what each control parameter can achieve:

| **Control Type**        | **Capabilities**                                                                 |
|--------------------------|----------------------------------------------------------------------------------|
| **Background Noise**     | Adjusts the level of background noise, supporting clear and slightly noisy environments. |
| **Reverberation**        | Controls the perceived distance of the speaker’s voice, allowing close or distant sounds. |
| **Expressivity**         | Modulates the emotional intensity of speech, from monotone to highly expressive. |
| **Pitch**                | Varies the pitch to achieve high, low, or moderate tonal output.                |
| **Speaking Rate**        | Changes the speed of speech delivery, ranging from slow to fast-paced.          |
| **Speech Quality**       | Improves or degrades the overall audio clarity, supporting basic to refined outputs. |


## 🌍 Switching languages

The model automatically adapts to the language it detects in the prompt. You don't need to specify the language you want to use. For example, to switch to Hindi, simply use an Hindi prompt:

```py
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

prompt = "अरे, तुम आज कैसे हो?"
description = "A female speaker delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

description_input_ids = description_tokenizer(description, return_tensors="pt").to(device)
prompt_input_ids = tokenizer(prompt, return_tensors="pt").to(device)

generation = model.generate(input_ids=description_input_ids.input_ids, attention_mask=description_input_ids.attention_mask, prompt_input_ids=prompt_input_ids.input_ids, prompt_attention_mask=prompt_input_ids.attention_mask)
audio_arr = generation.cpu().numpy().squeeze()
sf.write("indic_tts_out.wav", audio_arr, model.config.sampling_rate)
```

## 🎯 Using a specific speaker

To ensure speaker consistency across generations, this checkpoint was also trained on pre-determined speakers, characterized by name (e.g. Rohit, Karan, Leela, Maya, Sita, ...).
To take advantage of this, simply adapt your text description to specify which speaker to use: `Divya's voice is monotone yet slightly fast in delivery, with a very close recording that almost has no background noise.`

```py
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

prompt = "अरे, तुम आज कैसे हो?"
description = "Divya's voice is monotone yet slightly fast in delivery, with a very close recording that almost has no background noise."

description_input_ids = description_tokenizer(description, return_tensors="pt").to(device)
prompt_input_ids = tokenizer(prompt, return_tensors="pt").to(device)

generation = model.generate(input_ids=description_input_ids.input_ids, attention_mask=description_input_ids.attention_mask, prompt_input_ids=prompt_input_ids.input_ids, prompt_attention_mask=prompt_input_ids.attention_mask)
audio_arr = generation.cpu().numpy().squeeze()
sf.write("indic_tts_out.wav", audio_arr, model.config.sampling_rate)
```

The model includes **69 speakers** across 18 officially supported languages, with each language having a set of recommended voices for optimal performance. Below is a table summarizing the available speakers for each language, along with the recommended ones.

Here is the table based on the provided data:

| **Language**      | **Available Speakers**                                       | **Recommended Speakers**       |
|--------------------|-------------------------------------------------------------|---------------------------------|
| Assamese          | Amit, Sita, Poonam, Rakesh                                  | Amit, Sita                     |
| Bengali           | Arjun, Aditi, Tapan, Rashmi, Arnav, Riya                    | Arjun, Aditi                   |
| Bodo              | Bikram, Maya, Kalpana                                      | Bikram, Maya                   |
| Chhattisgarhi     | Bhanu, Champa                                              | Bhanu, Champa                  |
| Dogri             | Karan                                                      | Karan                          |
| English           | Thoma, Mary, Swapna, Dinesh, Meera, Jatin, Aakash, Sneha, Kabir, Tisha, Chingkhei, Thoiba, Priya, Tarun, Gauri, Nisha, Raghav, Kavya, Ravi, Vikas, Riya | Thoma, Mary                     |
| Gujarati          | Yash, Neha                                                 | Yash, Neha                     |
| Hindi             | Rohit, Divya, Aman, Rani                                   | Rohit, Divya                   |
| Kannada           | Suresh, Anu, Chetan, Vidya                                 | Suresh, Anu                    |
| Malayalam         | Anjali, Anju, Harish                                       | Anjali, Harish                   |
| Manipuri          | Laishram, Ranjit                                           | Laishram, Ranjit               |
| Marathi           | Sanjay, Sunita, Nikhil, Radha, Varun, Isha                  | Sanjay, Sunita                 |
| Nepali            | Amrita                                                     | Amrita                         |
| Odia              | Manas, Debjani                                             | Manas, Debjani                 |
| Punjabi           | Divjot, Gurpreet                                           | Divjot, Gurpreet               |
| Sanskrit          | Aryan                                                      | Aryan                          |
| Tamil             | Kavitha, Jaya                                        | Jaya                 |
| Telugu            | Prakash, Lalitha, Kiran                                    | Prakash, Lalitha               |


**Tips**:
* We've set up an [inference guide](https://github.com/huggingface/parler-tts/blob/main/INFERENCE.md) to make generation faster. Think SDPA, torch.compile, batching and streaming!
* Include the term "very clear audio" to generate the highest quality audio, and "very noisy audio" for high levels of background noise
* Punctuation can be used to control the prosody of the generations, e.g. use commas to add small breaks in speech
* The remaining speech features (gender, speaking rate, pitch and reverberation) can be controlled directly through the prompt


## Some Description Examples

1. **Aditi - Slightly High-Pitched, Expressive Tone**:  
   *"Aditi speaks with a slightly higher pitch in a close-sounding environment. Her voice is clear, with subtle emotional depth and a normal pace, all captured in high-quality recording."*  

2. **Sita - Rapid, Slightly Monotone**:  
   *"Sita speaks at a fast pace with a slightly low-pitched voice, captured clearly in a close-sounding environment with excellent recording quality."*  

3. **Tapan - Male, Moderate Pace, Slightly Monotone**:  
   *"Tapan speaks at a moderate pace with a slightly monotone tone. The recording is clear, with a close sound and only minimal ambient noise."*  

4. **Sunita - High-Pitched, Happy Tone**:  
   *"Sunita speaks with a high pitch in a close environment. Her voice is clear, with slight dynamic changes, and the recording is of excellent quality."*  

5. **Karan - High-Pitched, Positive Tone**:  
   *"Karan’s high-pitched, engaging voice is captured in a clear, close-sounding recording. His slightly slower delivery conveys a positive tone."*  

6. **Amrita - High-Pitched, Flat Tone**:  
   *"Amrita speaks with a high pitch at a slow pace. Her voice is clear, with excellent recording quality and only moderate background noise."*  

7. **Aditi - Slow, Slightly Expressive**:  
   *"Aditi speaks slowly with a high pitch and expressive tone. The recording is clear, showcasing her energetic and emotive voice."*  

8. **Young Male Speaker, American Accent**:  
   *"A young male speaker with a high-pitched American accent delivers speech at a slightly fast pace in a clear, close-sounding recording."*  

9. **Bikram - High-Pitched, Urgent Tone**:  
   *"Bikram speaks with a higher pitch and fast pace, conveying urgency. The recording is clear and intimate, with great emotional depth."*  

10. **Anjali - High-Pitched, Neutral Tone**:  
   *"Anjali speaks with a high pitch at a normal pace in a clear, close-sounding environment. Her neutral tone is captured with excellent audio quality."*  


## 📐 Evaluation

Indic Parler-TTS has been evaluated using a MOS-like framework by native and non-native speakers. The results highlight its exceptional performance in generating natural and intelligible speech, especially for native speakers of Indian languages.  

**NSS** stands for **Native Speaker Score**:

| **Language**   | **NSS Pretrained (%)** | **NSS Finetuned (%)** | **Highlights**                                                                                     |
|----------------|-------------------------|------------------------|--------------------------------------------------------------------------------------------------|
| Assamese       | 82.56 ± 1.80           | 87.36 ± 1.81          | Clear, natural synthesis with excellent expressiveness.                                          |
| Bengali        | 77.41 ± 2.14           | 86.16 ± 1.85          | High-quality outputs with smooth intonation.                                                    |
| Bodo           | 90.83 ± 4.54           | 94.47 ± 4.12          | Near-perfect accuracy for a lesser-resourced language.                                          |
| Dogri          | 82.61 ± 4.98           | 88.80 ± 3.57          | Robust and consistent synthesis for Dogri.                                                     |
| Gujarati       | 75.28 ± 1.94           | 75.36 ± 1.78          | Strong clarity and naturalness even for smaller languages.                                      |
| Hindi          | 83.43 ± 1.53           | 84.79 ± 2.09          | Reliable and expressive outputs for India's most widely spoken language.                       |
| Kannada        | 77.97 ± 3.43           | 88.17 ± 2.81          | Highly natural and accurate voices for Kannada.                                                |
| Konkani        | 87.20 ± 3.58           | 76.60 ± 4.14          | Produces clear and natural outputs for diverse speakers.                                       |
| Maithili       | 89.07 ± 4.47           | 95.36 ± 2.52          | Exceptionally accurate, showcasing fine-tuning success.                                         |
| Malayalam      | 82.02 ± 2.06           | 86.54 ± 1.67          | Smooth, high-quality synthesis with expressive outputs.                                        |
| Manipuri       | 89.58 ± 1.33           | 85.63 ± 2.60          | Natural intonation with minimal errors.                                                        |
| Marathi        | 73.81 ± 1.93           | 76.96 ± 1.45          | Maintains clarity and naturalness across speakers.                                             |
| Nepali         | 64.05 ± 8.33           | 80.02 ± 5.75          | Strong synthesis for native and proximal Nepali speakers.                                      |
| Odia           | 90.28 ± 2.52           | 88.94 ± 3.26          | High expressiveness and quality for Odia speakers.                                             |
| Sanskrit       | 99.71 ± 0.58           | 99.79 ± 0.34          | Near-perfect synthesis, ideal for classical use cases.                                         |
| Sindhi         | 76.44 ± 2.26           | 76.46 ± 1.29          | Clear and natural voices for underrepresented languages.                                       |
| Tamil          | 69.68 ± 2.73           | 75.48 ± 2.18          | Delivers intelligible and expressive speech.                                                   |
| Telugu         | 89.77 ± 2.20           | 88.54 ± 1.86          | Smooth and natural tonal quality for Telugu.                                                   |
| Urdu           | 77.15 ± 3.47           | 77.75 ± 3.82          | Produces high-quality speech despite resource constraints.                                     |

**Key Strengths**:  
- Exceptional performance for native speakers, with top scores for **Maithili (95.36)**, **Sanskrit (99.79)**, and **Bodo (94.47)**.  
- Competitive results for lesser-resourced and unofficially supported languages like **Kashmiri (55.30)** and **Sindhi (76.46)**.  
- Adaptability to non-native and anonymous speaker scenarios with consistently high clarity.  


## Motivation

Parler-TTS is a reproduction of work from the paper [Natural language guidance of high-fidelity text-to-speech with synthetic annotations](https://www.text-description-to-speech.com) by Dan Lyth and Simon King, from Stability AI and Edinburgh University respectively. 

Parler-TTS was released alongside:
* [The Parler-TTS repository](https://github.com/huggingface/parler-tts) - you can train and fine-tuned your own version of the model.
* [The Data-Speech repository](https://github.com/huggingface/dataspeech) - a suite of utility scripts designed to annotate speech datasets.
* [The Parler-TTS organization](https://huggingface.co/parler-tts) - where you can find the annotated datasets as well as the future checkpoints.


## Training dataset

- **Description**:  
  The model was fine-tuned on a subset of the dataset used to train the pre-trained version: **Indic-Parler Dataset**, a large-scale multilingual speech corpus designed to train the **Indic Parler-TTS** model.

- **Key Statistics**:

| Dataset         | Duration (hrs) | Languages Covered | No. of Utterances | License      |
|:---------------:|:--------------:|:-----------------:|:-----------------:|:------------:|
| GLOBE           | 535.0          | 1                 | 581,725           | CC V1        |
| IndicTTS        | 382.0          | 12                | 220,606           | CC BY 4.0    |
| LIMMITS         | 568.0          | 7                 | 246,008           | CC BY 4.0    |
| Rasa            | 288.0          | 9                 | 155,734           | CC BY 4.0    |

- **Languages Covered**:  
  The dataset supports **16 official languages** of India, along with English and Chhattisgarhi, making it comprehensive for regional language technologies. These languages include Assamese, Bengali, Bodo, Chhattisgarhi, Dogri, English, Gujarati, Hindi, Kannada, Malayalam, Manipuri, Marathi, Nepali, Odia, Punjabi, Sanskrit, Tamil and Telugu.


- **Language-Wise Data Breakdown**:

Here’s the table combining the duration (hours) and the number of utterances from the provided stats:

| Language        | Duration (hrs) | No. of Utterances |
|:---------------:|:--------------:|:-----------------:|
| Assamese        | 69.78          | 41,210            |
| Bengali         | 140.04         | 70,305            |
| Bodo            | 49.14          | 27,012            |
| Chhattisgarhi   | 80.11          | 38,148            |
| Dogri           | 16.14          | 7,823             |
| English         | 802.81         | 735,482           |
| Gujarati        | 21.24          | 5,679             |
| Hindi           | 107.00         | 46,135            |
| Kannada         | 125.01         | 54,575            |
| Malayalam       | 25.21          | 14,988            |
| Manipuri        | 20.77          | 19,232            |
| Marathi         | 122.47         | 54,894            |
| Nepali          | 28.65          | 16,016            |
| Odia            | 19.18          | 11,558            |
| Punjabi         | 11.07          | 6,892             |
| Sanskrit        | 19.91          | 8,720             |
| Tamil           | 52.25          | 29,204            |
| Telugu          | 95.91          | 37,405            |


## Citation

If you found this repository useful, please consider citing this work and also the original Stability AI paper:

```
@inproceedings{sankar25_interspeech,
  title     = {{Rasmalai : Resources for Adaptive Speech Modeling in IndiAn Languages with Accents and Intonations}},
  author    = {Ashwin Sankar and Yoach Lacombe and Sherry Thomas and Praveen {Srinivasa Varadhan} and Sanchit Gandhi and Mitesh M. Khapra},
  year      = {2025},
  booktitle = {{Interspeech 2025}},
  pages     = {4128--4132},
  doi       = {10.21437/Interspeech.2025-2758},
  issn      = {2958-1796},
}
```

```
@misc{lacombe-etal-2024-parler-tts,
  author = {Yoach Lacombe and Vaibhav Srivastav and Sanchit Gandhi},
  title = {Parler-TTS},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/huggingface/parler-tts}}
}
```

```
@misc{lyth2024natural,
      title={Natural language guidance of high-fidelity text-to-speech with synthetic annotations},
      author={Dan Lyth and Simon King},
      year={2024},
      eprint={2402.01912},
      archivePrefix={arXiv},
      primaryClass={cs.SD}
}
```

## License

This model is permissively licensed under the Apache 2.0 license.