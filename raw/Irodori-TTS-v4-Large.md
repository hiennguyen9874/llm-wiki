---
license: gemma
language:
- ja
pipeline_tag: text-to-speech
tags:
- speech
- voice
- tts
---

# Irodori-TTS-v4-Large

[![Code](https://img.shields.io/badge/Code-GitHub-black)](https://github.com/Aratako/Irodori-TTS) [![Demo Space](https://img.shields.io/badge/Demo-HuggingFace%20Space-blue)](https://huggingface.co/spaces/Aratako/Irodori-TTS-v4-Large-Demo)

**Irodori-TTS-v4-Large** is a Japanese Text-to-Speech model based on a Rectified Flow Diffusion Transformer (RF-DiT) architecture. It combines **Text (Input) + Reference Speech + Caption Text** in a unified model, enabling zero-shot voice cloning, text-based voice design, and style-controlled voice cloning.

The model also supports emoji-based style and sound effect control. By inserting specific emojis into the input text, you can control speaking styles, emotions, and non-verbal vocal expressions in the generated audio.

## 🌟 Key Features

  * **Multi-modal Voice Design:** Use reference audio for speaker identity and descriptive captions for voice characteristics, emotion, speaking style, and delivery.
  * **Long-reference Voice Cloning:** Condition generation on one or more reference clips, with up to 120 seconds of combined reference audio.
  * **Flow Matching TTS:** Rectified Flow Diffusion Transformer over continuous DACVAE latents for high-quality Japanese speech synthesis.
  * **Emoji-based Style Control:** Embed emojis directly in the input text for granular control over the delivery and sound effects (e.g., laughter, coughing, sighs). See [`EMOJI_ANNOTATIONS.md`](https://github.com/Aratako/Irodori-TTS/blob/main/EMOJI_ANNOTATIONS.md) for details.
  * **Integrated Watermarking:** Integrates [SilentCipher](https://github.com/sony/silentcipher) to apply robust, invisible audio watermarks directly to generated outputs, promoting responsible AI usage.

## ✨ What's New in v4-Large

  * **Larger Model:** Scales the v4 architecture from approximately 766M to 3.29B parameters, including a 24-layer, 2,048-dimensional Diffusion Transformer and a larger reference latent encoder.
  * **T5Gemma 2 Text/Caption Encoder:** Replaces ModernBERT-ja with the fine-tuned text encoder from [google/t5gemma-2-1b-1b](https://huggingface.co/google/t5gemma-2-1b-1b), shared between input text and Voice Design captions.
  * **Separately Trained Duration Predictor:** Uses a duration predictor trained after the main model, with the other model parameters frozen, following the approach used in v4.1-Small.
  * **Improved Voice Design Scores:** Achieves higher caption-adherence scores than v4-Small in the internal Coco-Nut evaluation below.

---

## 🏗️ Architecture

The model (approximately 3.29B parameters) consists of five main components:

1.  **Shared Text/Caption Encoder:** A fine-tuned T5Gemma 2 text encoder shared between the input-text and Voice Design caption paths.
2.  **Condition Projectors:** Separate learned projectors map text and caption encoder representations into their respective TTS conditioning spaces.
3.  **Reference Latent Encoder:** Encodes patched reference audio latents for speaker identity conditioning, supporting up to 120 seconds of combined reference audio.
4.  **Diffusion Transformer:** Joint-attention DiT blocks combining text, reference, and caption conditioning with Low-Rank AdaLN, half-RoPE, and SwiGLU MLPs.
5.  **Duration Predictor:** Predicts audio duration from encoded text and conditioning vectors using stacked SwiGLU MLP blocks.

Audio is represented as continuous latent sequences via the [Aratako/Semantic-DACVAE-Japanese-32dim](https://huggingface.co/Aratako/Semantic-DACVAE-Japanese-32dim) codec (32-dim), enabling high-quality 48kHz waveform reconstruction.

---

## 🚀 Usage

For inference code, installation instructions, and training scripts, please refer to the GitHub repository:

👉 **[GitHub: Aratako/Irodori-TTS](https://github.com/Aratako/Irodori-TTS)**

For lower-memory inference, torchao INT8, INT4, and FP8 variants are planned at **[Aratako/Irodori-TTS-v4-Large-Quantized](https://huggingface.co/Aratako/Irodori-TTS-v4-Large-Quantized)**.

### Long-reference Voice Cloning

For long-reference voice cloning, using multiple shorter clips from the same speaker is recommended. v4-Large was trained by randomly concatenating multiple short utterances from each speaker, and the reference-length benchmark below follows the same construction. Inference also accepts a single uninterrupted long recording, but the benefit of that input format has not been evaluated and may differ from the reported results.

## 📊 Benchmarks

The five-seed evaluations use the consecutive base sampling seeds 0 through 4. Unless otherwise noted, values are the mean and population standard deviation across these five seeds.

The Joyo Kanji Yomi Benchmark, JSUT, Coco-Nut, and JVS datasets were not included in the training data.

### Japanese Reading

Japanese reading was evaluated with no reference audio or Voice Design caption, FP32 inference, 40 RF steps, and text CFG 3.0.

#### Joyo Kanji Yomi Benchmark: Parakeet Edition

This evaluation uses [Joyo Kanji Yomi Benchmark: Parakeet Edition](https://github.com/Parakeet-Inc/Joyo-Kanji-Yomi-Benchmark-Parakeet-Edition), covering 13,536 sentences and 4,512 kanji-reading pairs. These values should not be directly compared with the original-edition Joyo results in the v4-Small and v4.1-Small model cards.

| Model | Reading accuracy ↑ | Target Kana-CER ↓ | Target Kana-CER clipped ↓ | Sentence Kana-CER ↓ | Text CER ↓ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Irodori-TTS-v4.1-Small | **93.42 ± 0.04%** | **6.88 ± 0.08%** | **5.19 ± 0.05%** | **1.25 ± 0.01%** | **4.68 ± 0.06%** |
| **Irodori-TTS-v4-Large** | 92.80 ± 0.08% | 7.96 ± 0.36% | 5.78 ± 0.06% | 1.51 ± 0.06% | 4.87 ± 0.08% |

The clipped variant caps each example's CER at 100% before averaging.

#### JSUT BASIC5000

| Model | Sentence Kana-CER ↓ | Standard CER ↓ |
| :--- | ---: | ---: |
| Irodori-TTS-v4.1-Small | **3.43 ± 0.01%** | **7.22 ± 0.12%** |
| **Irodori-TTS-v4-Large** | 3.67 ± 0.03% | 7.30 ± 0.01% |

v4-Large has slightly higher reading error rates than v4.1-Small on both benchmarks.

### Voice Design

Voice Design prompt adherence was evaluated using all 2,890 public voice descriptions from the [Coco-Nut](https://github.com/sarulab-speech/Coco-Nut) test set. Each description was paired with the same short, medium, and long reading texts, producing 8,670 clips per model without reference audio and using one deterministic seed per description/text pair. Gemini 3.6 Flash independently scored each clip from 1 to 5 for agreement between the requested voice description and the generated speech. Generation used FP32 inference, 40 RF steps, and text/caption CFG 3.0.

| Model | Mean score ↑ | Scores 1–2 ↓ | Scores 4–5 ↑ |
| :--- | ---: | ---: | ---: |
| Irodori-TTS-600M-v3-VoiceDesign | 4.2096 | 17.09% | 73.30% |
| Irodori-TTS-v4-Small | 4.2339 | 16.78% | 74.12% |
| **Irodori-TTS-v4-Large** | **4.2991** | **14.63%** | **76.24%** |

The mean score improvement over v4-Small was **+0.0652**, with a paired cluster-bootstrap 95% confidence interval of **[+0.0353, +0.0955]** across 578 Coco-Nut segment IDs. The largest improvement was on the long reading text: 3.9851 → 4.1343.

Unlike the other benchmarks, this evaluation uses a single generation run with base seed 0. The table therefore reports aggregates over the evaluated clips rather than a mean and standard deviation across five synthesis seeds.

This is a lightweight, cost-conscious internal comparison using a single automatic judge without human validation. It is not intended as a research-grade benchmark or as standalone evidence for academic claims.

See [VOICE_DESIGN_BENCHMARK.md](https://huggingface.co/Aratako/Irodori-TTS-v4-Small/blob/main/VOICE_DESIGN_BENCHMARK.md) for the evaluation protocol, scoring rubric, and limitations.

### Voice Cloning and Reference Length

Voice cloning was evaluated on JVS using all 100 speakers, five target texts, and five synthesis seeds. Independently encoded reference utterances from each speaker were concatenated into nested one-clip, approximately 30-second, approximately 60-second, and 120-second conditions. Similarity was measured against a fixed centroid of ten held-out natural utterances per speaker, so longer conditioning references did not change the scoring target. Generation used FP32 inference, 40 RF steps, text CFG 3.0, and speaker CFG 5.0.

| Model / Reference | JVS CAM++ cosine ↑ | JVS CAM++ top-1 ↑ |
| :--- | ---: | ---: |
| v4-Small, one clip | 0.6610 ± 0.0013 | 84.60 ± 0.55% |
| v4-Large, one clip | 0.6711 ± 0.0019 | 87.00 ± 0.59% |
| v4-Small, ~30 seconds | 0.7521 ± 0.0008 | 98.56 ± 0.20% |
| v4-Large, ~30 seconds | 0.7593 ± 0.0011 | 99.48 ± 0.27% |
| v4-Small, ~60 seconds | 0.7646 ± 0.0003 | 99.56 ± 0.23% |
| v4-Large, ~60 seconds | 0.7700 ± 0.0011 | 99.60 ± 0.18% |
| v4-Small, 120 seconds | 0.7753 ± 0.0009 | **99.76 ± 0.23%** |
| v4-Large, 120 seconds | **0.7788 ± 0.0005** | 99.64 ± 0.15% |

v4-Large achieves higher mean CAM++ cosine similarity at all four reference lengths, although 120-second top-1 accuracy is slightly lower. Most of the gain from extending v4-Large's references is already present at approximately 30 seconds.

See [VOICE_CLONING_BENCHMARK.md](https://huggingface.co/Aratako/Irodori-TTS-v4-Small/blob/main/VOICE_CLONING_BENCHMARK.md) for the dataset, reference construction, evaluation protocol, and limitations.

## 📊 Training Data & Annotation

The model was trained on an expanded, high-quality Japanese speech dataset. To enable the multi-modal Voice Design functionality, the training data was enriched with comprehensive text captions describing the audio characteristics.

The emoji annotations and initial text captions were generated and labeled using a fine-tuned model based on [Qwen/Qwen3-Omni-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Instruct). Subsequently, the text captions were rephrased and refined using [Qwen/Qwen3.5-35B-A3B](https://huggingface.co/Qwen/Qwen3.5-35B-A3B).

## ⚠️ Limitations

  - **Japanese Only:** This model currently supports Japanese text input only.
  - **Short-reference Voice Cloning:** Speaker similarity is substantially lower with a single short reference clip than with longer references. Approximately 30 seconds or more of reasonably clean reference speech is recommended when available.
  - **Long-reference Composition:** Training and long-reference evaluation used multiple short utterances from the same speaker concatenated together. A single uninterrupted long recording is supported as input, but its effect has not been evaluated.
  - **Conditioning Conflicts:** When using both reference audio and a text caption, contradictory instructions may result in unstable audio quality, unnatural artifacts, or one condition overriding the other. For optimal results, use the caption to guide emotion, style, or environment while keeping the base voice characteristics aligned with the reference audio.
  - **Prompt Adherence:** While the model generally follows caption instructions, highly complex or contradictory descriptions may produce inconsistent results.
  - **Emoji Control:** The effect of emoji-based control may vary depending on context and is not always perfectly consistent.
  - **Kanji Reading:** Reading accuracy is slightly lower than v4.1-Small on the evaluated Joyo and JSUT tasks. Uncommon names, specialized terminology, and context-dependent readings may be pronounced incorrectly.
  - **Evaluation Scope:** No large-scale human MOS, naturalness, prompt-adherence, or speaker-similarity evaluation was conducted. Automatic benchmark scores do not fully represent human perception.

## 📜 License & Ethical Restrictions

### License

This model is subject to the **[Gemma Terms of Use](https://ai.google.dev/gemma/terms)** because its shared text/caption encoder is derived from **[google/t5gemma-2-1b-1b](https://huggingface.co/google/t5gemma-2-1b-1b)**. Use and redistribution must comply with those terms, including the **[Gemma Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy)**, as well as the additional ethical restrictions below.

### Ethical Restrictions

In addition to the license terms, the following ethical restrictions apply:

1.  **No Impersonation:** Do not use this model to clone or impersonate the voice of any individual (e.g., voice actors, celebrities, public figures) without their explicit consent.
2.  **No Misinformation:** Do not use this model to generate deepfakes or synthetic speech intended to mislead others or spread misinformation.
3.  **Voice Generation Disclaimer:** When generating speech purely from text or captions without using reference audio, it is possible that the generated voice may coincidentally resemble that of a real person. This is strictly a probabilistic artifact within the latent space. The model was not trained with the intent of reproducing specific individuals.
4.  **Liability Disclaimer:** The developers assume no liability for any misuse of this model. Users are solely responsible for ensuring their use of the generated content complies with applicable laws and regulations in their jurisdiction.

## 🙏 Acknowledgments

This project builds upon the following works:

  - [Echo-TTS](https://jordandarefsky.com/blog/2025/echo/) — Architecture and training design reference
  - [DACVAE](https://github.com/facebookresearch/dacvae) — Audio VAE
  - [google/t5gemma-2-1b-1b](https://huggingface.co/google/t5gemma-2-1b-1b) — Pretrained text and caption encoder
  - [SilentCipher](https://github.com/sony/silentcipher) — Audio watermarking integration

We would also like to extend our special thanks to **[Respair](https://huggingface.co/Respair)** for the inspiration behind the emoji annotation feature, and to [gabrielclark3330](https://huggingface.co/gabrielclark3330) and [kikouousya](https://huggingface.co/kikouousya) for supporting this project.

## 🖊️ Citation

If you use Irodori-TTS in your research or project, please cite it as follows:

```bibtex
@misc{irodori-tts-v4-large,
  author = {Chihiro Arata},
  title = {Irodori-TTS: A Flow Matching-based Text-to-Speech Model with Emoji-driven Style Control},
  year = {2026},
  publisher = {Hugging Face},
  journal = {Hugging Face repository},
  howpublished = {\url{https://huggingface.co/Aratako/Irodori-TTS-v4-Large}}
}
```
