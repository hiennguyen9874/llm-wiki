---
type: Concept
title: Indic Parler-TTS
description: Prompt-controlled multilingual Indic TTS extension of Parler-TTS Mini covering 21 languages with 69 named speakers, caption-driven style control, and per-language NSS evaluation.
tags: [tts, multilingual, indic, prompt-control, speaker-consistency]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: indic-parler-card
    resource: ../raw/indic-parler-tts.md
    kind: documentation
    title: Indic Parler-TTS model card
---

Indic Parler-TTS (`ai4bharat/indic-parler-tts`) is a multilingual Indic fine-tune of [Parler-TTS Mini v1.1](https://huggingface.co/parler-tts/parler-tts-mini-v1.1) built by the Hugging Face audio team with AI4Bharat, accepting a transcript plus a natural-language caption to control voice, emotion, pitch, rate, and recording conditions across a claimed 21 languages with 69 named speakers, trained on a ~1.8k-hour Indic plus English corpus and evaluated with a MOS-like Native Speaker Score per language (**Reported**).[^indic-parler-card]

## Model identity and provenance

- Checkpoint `ai4bharat/indic-parler-tts`; fine-tuned from [Indic Parler-TTS Pretrained](https://huggingface.co/ai4bharat/indic-parler-tts-pretrained), which extends Parler-TTS Mini v1.1; collaboration between the Hugging Face audio team and [AI4Bharat](https://ai4bharat.iitm.ac.in/) (**Reported**).[^indic-parler-card]
- Frontmatter declares `pipeline_tag: text-to-speech`, `inference: false`, Apache-2.0 license, 17 `language` codes, and `datasets: ai4b-hf/GLOBE-annotated` (**Reported**).[^indic-parler-card]
- Motivation is a reproduction of Lyth and King, *Natural language guidance of high-fidelity text-to-speech with synthetic annotations* (Stability AI / Edinburgh), alongside the Parler-TTS, Data-Speech, and Parler-TTS-organization releases (**Reported**).[^indic-parler-card]
- Distinguishing tokenizer change: a better prompt tokenizer with larger vocabulary and byte fallback, intended to simplify multilingual training and extension to other languages; unlike earlier Parler-TTS versions this checkpoint uses two tokenizers, one for the prompt and one for the description (**Reported**).[^indic-parler-card]
- Successor note: the card recommends [Indic-Speak](https://huggingface.co/bodhan-ai/indic-speak) instead, stating it supports 22 Indian languages with better TTS capabilities; no Indic-Speak concept exists in this wiki yet, so no supersession edge is recorded (**Reported**).[^indic-parler-card]

## Language coverage

- Officially 20 Indic languages plus English (21 total): Assamese, Bengali, Bodo, Dogri, English, Gujarati, Hindi, Kannada, Konkani, Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Sanskrit, Santali, Sindhi, Tamil, Telugu, and Urdu (**Reported**).[^indic-parler-card]
- Unofficial support claimed for Chhattisgarhi, Kashmiri, and Punjabi without extensive testing guarantees (**Reported**).[^indic-parler-card]
- Language selection is automatic: the model adapts to the language detected in the prompt with no explicit language flag; the documented example switches to Hindi by passing `अरे, तुम आज कैसे हो?` as the transcript (**Reported**).[^indic-parler-card]
- Accent handling: Indian English accents are officially supported through the English voices; other accents (e.g. "a male British speaker") are customized through the caption via style transfer (**Reported**).[^indic-parler-card]

## Speakers and emotions

- 69 unique voices across the supported languages, each language with a set of recommended voices optimized for naturalness and intelligibility; speaker consistency is obtained by naming the speaker in the caption (e.g. `Divya's voice is ...`) (**Reported**).[^indic-parler-card]
- Per-language roster as tabled in the card (recommended voices in bold in the source logic; reproduced here as listed) (**Reported**):[^indic-parler-card]

| Language | Available speakers | Recommended |
| --- | --- | --- |
| Assamese | Amit, Sita, Poonam, Rakesh | Amit, Sita |
| Bengali | Arjun, Aditi, Tapan, Rashmi, Arnav, Riya | Arjun, Aditi |
| Bodo | Bikram, Maya, Kalpana | Bikram, Maya |
| Chhattisgarhi | Bhanu, Champa | Bhanu, Champa |
| Dogri | Karan | Karan |
| English | Thoma, Mary, Swapna, Dinesh, Meera, Jatin, Aakash, Sneha, Kabir, Tisha, Chingkhei, Thoiba, Priya, Tarun, Gauri, Nisha, Raghav, Kavya, Ravi, Vikas, Riya | Thoma, Mary |
| Gujarati | Yash, Neha | Yash, Neha |
| Hindi | Rohit, Divya, Aman, Rani | Rohit, Divya |
| Kannada | Suresh, Anu, Chetan, Vidya | Suresh, Anu |
| Malayalam | Anjali, Anju, Harish | Anjali, Harish |
| Manipuri | Laishram, Ranjit | Laishram, Ranjit |
| Marathi | Sanjay, Sunita, Nikhil, Radha, Varun, Isha | Sanjay, Sunita |
| Nepali | Amrita | Amrita |
| Odia | Manas, Debjani | Manas, Debjani |
| Punjabi | Divjot, Gurpreet | Divjot, Gurpreet |
| Sanskrit | Aryan | Aryan |
| Tamil | Kavitha, Jaya | Jaya |
| Telugu | Prakash, Lalitha, Kiran | Prakash, Lalitha |

- Emotion rendering: 10 languages officially support emotion-specific prompts (Assamese, Bengali, Bodo, Dogri, Kannada, Malayalam, Marathi, Sanskrit, Nepali, Tamil); other languages have untested emotion support; available emotions are Command, Anger, Narration, Conversation, Disgust, Fear, Happy, Neutral, Proper Noun, News, Sad, and Surprise (**Reported**).[^indic-parler-card]

## Controllable synthesis

- Two inputs: **Transcript** (text to speak) and **Caption** (description of how it should sound, e.g. "Leela speaks in a high-pitched, fast-paced, and cheerful tone ...") (**Reported**).[^indic-parler-card]
- Caption axes (**Reported**):[^indic-parler-card]

| Control | Effect |
| --- | --- |
| Background noise | clear to slightly noisy environments |
| Reverberation | close-sounding to distant-sounding voice |
| Expressivity | monotone to highly expressive |
| Pitch | high, low, or balanced tone |
| Speaking rate | slow to fast delivery |
| Speech/voice quality | basic to refined clarity and naturalness |

- Practical tips from the card: include "very clear audio" for highest quality and "very noisy audio" for noisy output; use punctuation (e.g. commas) to shape prosody; gender, rate, pitch, and reverberation can be driven directly through the prompt; an inference guide covers SDPA, `torch.compile`, batching, and streaming (**Reported**).[^indic-parler-card]

## Inference usage

- Install once with `pip install git+https://github.com/huggingface/parler-tts.git` (**Reported**).[^indic-parler-card]
- Transformers pattern with dual tokenizers: `ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts")`, `AutoTokenizer` for the transcript prompt, and a separate description tokenizer from `model.config.text_encoder._name_or_path`; both are tokenized with `return_tensors="pt"`, passed as `input_ids`/`attention_mask` plus `prompt_input_ids`/`prompt_attention_mask` to `model.generate`, then written with `soundfile` at `model.config.sampling_rate` (**Reported**).[^indic-parler-card]
- The same pattern serves three modes: random voice (free-form caption such as "A female speaker with a British accent ..."), language switching (Hindi prompt with English caption), and named-speaker consistency (`Divya's voice is monotone yet slightly fast ...`) (**Reported**).[^indic-parler-card]
- No latency, RTF, VRAM, sampling-rate number, parameter count, or streaming protocol is stated in the source (**Reported** absence).[^indic-parler-card]

## Evaluation

- MOS-like framework with native and non-native raters; NSS is Native Speaker Score in percent with confidence intervals, reported for pretrained versus finetuned checkpoints (**Reported**).[^indic-parler-card]

| Language | NSS pretrained (%) | NSS finetuned (%) |
| --- | --- | --- |
| Assamese | 82.56 ± 1.80 | 87.36 ± 1.81 |
| Bengali | 77.41 ± 2.14 | 86.16 ± 1.85 |
| Bodo | 90.83 ± 4.54 | 94.47 ± 4.12 |
| Dogri | 82.61 ± 4.98 | 88.80 ± 3.57 |
| Gujarati | 75.28 ± 1.94 | 75.36 ± 1.78 |
| Hindi | 83.43 ± 1.53 | 84.79 ± 2.09 |
| Kannada | 77.97 ± 3.43 | 88.17 ± 2.81 |
| Konkani | 87.20 ± 3.58 | 76.60 ± 4.14 |
| Maithili | 89.07 ± 4.47 | 95.36 ± 2.52 |
| Malayalam | 82.02 ± 2.06 | 86.54 ± 1.67 |
| Manipuri | 89.58 ± 1.33 | 85.63 ± 2.60 |
| Marathi | 73.81 ± 1.93 | 76.96 ± 1.45 |
| Nepali | 64.05 ± 8.33 | 80.02 ± 5.75 |
| Odia | 90.28 ± 2.52 | 88.94 ± 3.26 |
| Sanskrit | 99.71 ± 0.58 | 99.79 ± 0.34 |
| Sindhi | 76.44 ± 2.26 | 76.46 ± 1.29 |
| Tamil | 69.68 ± 2.73 | 75.48 ± 2.18 |
| Telugu | 89.77 ± 2.20 | 88.54 ± 1.86 |
| Urdu | 77.15 ± 3.47 | 77.75 ± 3.82 |

- Card highlights: top finetuned scores for Sanskrit (99.79), Maithili (95.36), and Bodo (94.47); competitive figures for underrepresented languages such as Sindhi (76.46); a Kashmiri figure of 55.30 is mentioned in prose but has no row in the table (**Reported**).[^indic-parler-card]
- Regressions after fine-tuning are visible in the table for Konkani (87.20 → 76.60), Manipuri, Odia, and Telugu; the card does not explain them (**Synthesis** of tabled numbers).[^indic-parler-card]

## Training data

- Fine-tuned on a subset of the Indic-Parler Dataset, described as a 1,806-hour multilingual Indic plus English corpus; the four constituent aggregates tabled are GLOBE 535.0 h / 581,725 utterances (CC V1), IndicTTS 382.0 h / 220,606 (CC BY 4.0), LIMMITS 568.0 h / 246,008 (CC BY 4.0), and Rasa 288.0 h / 155,734 (CC BY 4.0), which sum to 1,773 h — 33 h below the headline figure (**Reported**, arithmetic is **Synthesis**).[^indic-parler-card]
- Dataset language statement: 16 official Indian languages plus English and Chhattisgarhi; the per-language breakdown table lists Assamese 69.78 h, Bengali 140.04 h, Bodo 49.14 h, Chhattisgarhi 80.11 h, Dogri 16.14 h, English 802.81 h, Gujarati 21.24 h, Hindi 107.00 h, Kannada 125.01 h, Malayalam 25.21 h, Manipuri 20.77 h, Marathi 122.47 h, Nepali 28.65 h, Odia 19.18 h, Punjabi 11.07 h, Sanskrit 19.91 h, Tamil 52.25 h, and Telugu 95.91 h; English dominates at ~45% of the breakdown (**Reported**).[^indic-parler-card]
- No architecture diagram, parameter count, hyperparameter list, training compute, or data-split description is present in the source (**Reported** absence).[^indic-parler-card]

## Citation and license

- Citation asks for the Sankar et al. Interspeech 2025 Rasmalai paper, the Lacombe et al. 2024 Parler-TTS GitHub reference, and the Lyth and King 2024 arXiv paper (**Reported**).[^indic-parler-card]
- Weights are permissively licensed under Apache-2.0 (**Reported**).[^indic-parler-card]

## Relationships

- Surveyed alongside every other TTS line in [TTS Model Survey](tts-model-survey.md) (**Synthesis**).[^indic-parler-card]
- Distinct from the Indic ASR line: [IndicConformer-600M-Multilingual](indic-conformer-600m-multilingual.md) covers 22 official Indian languages for recognition, while this page covers synthesis with caption-driven style control; no shared checkpoint is claimed (**Synthesis**).[^indic-parler-card]

## Coverage and limits

- Source inspected statically only; no model was downloaded, run, or listened to, and no NSS, latency, or quality figure was reproduced (**Synthesis**).[^indic-parler-card]
- The pretrained checkpoint, training corpus files, inference-guide page, demo Space, and sample audio are linked but were not fetched and are absent from `raw/` (**Synthesis**).[^indic-parler-card]
- Consequential gaps persisted to this page: no parameter count, sampling rate, latency/RTF/VRAM, or streaming claim; the speaker roster omits several claimed official languages (Konkani, Maithili, Santali, Sindhi, Urdu, Kashmiri) and adds unofficial ones; the 1,806 h headline and the 1,773 h component sum differ; and the 55.30 Kashmiri figure has no evaluation row (**Synthesis**).[^indic-parler-card]
- All capability, language, speaker, emotion, dataset, evaluation, and licensing claims above are source assertions without independent verification in this wiki (**Synthesis**).[^indic-parler-card]

[^indic-parler-card]: [Indic Parler-TTS model card](../raw/indic-parler-tts.md) — locators: frontmatter (`license: apache-2.0`, 17-code `language`, `pipeline_tag: text-to-speech`, `inference: false`, `datasets: ai4b-hf/GLOBE-annotated`); header (Parler-TTS Mini v1.1 lineage, 1,806-hour fine-tune, Indic-Speak successor note, 21-language list, byte-fallback tokenizer, HF audio × AI4Bharat banner); `Key capabilities` (21-language roster, Chhattisgarhi/Kashmiri/Punjabi unofficial note, 69 voices, 10-language emotion list with 12 emotions, Indian-English accent plus style-transfer accents, six caption axes); `Random voice` / `Switching languages` / `Using a specific speaker` fences (`pip install git+https://github.com/huggingface/parler-tts.git`, `ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts")`, dual `AutoTokenizer` plus `model.config.text_encoder._name_or_path`, `model.generate(input_ids/prompt_input_ids)`, `soundfile` at `model.config.sampling_rate`, Hindi prompt example, `Divya's voice ...` pattern); speaker table (18 rows with available and recommended voices); `Tips` (inference-guide link, "very clear/noisy audio", punctuation prosody); description-example list (10 captions); `Evaluation` NSS table (19 rows pretrained vs finetuned with ± intervals, top-Maithili/Sanskrit/Bodo prose, Kashmiri 55.30 prose mention); `Motivation` (Lyth-King paper plus three release links); `Training dataset` (Indic-Parler subset, 4-row GLOBE/IndicTTS/LIMMITS/Rasa table with hours/utterances/licenses, 18-row language hours/utterances table); `Citation` (three bib entries); `License` (Apache 2.0).
