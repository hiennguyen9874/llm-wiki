---
type: Concept
title: Irodori-TTS-v4-Large
description: 3.29B-parameter Japanese-only rectified-flow diffusion TTS model with text-plus-reference-plus-caption conditioning, long-reference voice cloning, emoji style control, and SilentCipher watermarking.
tags: [tts, voice-cloning, voice-design, japanese]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T16:00:00Z }
stale_after: 2027-10-06
sources:
  - id: irodori-v4-large-card
    resource: ../raw/Irodori-TTS-v4-Large.md
    kind: documentation
    title: Irodori-TTS-v4-Large model card
---

Irodori-TTS-v4-Large is a Japanese-only text-to-speech model of approximately 3.29B parameters built on a Rectified Flow Diffusion Transformer (RF-DiT) over continuous DACVAE latents, conditioning each synthesis on input text plus optional reference speech (up to 120 seconds combined) and a descriptive Voice Design caption, with emoji-driven style and sound-effect control and a SilentCipher invisible watermark on generated audio (**Reported**).[^irodori-v4-large-card]

## Model identity and release

- Full name is `Irodori-TTS-v4-Large` by Chihiro Arata; code is at `Aratako/Irodori-TTS` on GitHub and weights plus demo live under `Aratako/Irodori-TTS-v4-Large` on Hugging Face, with a demo Space at `Aratako/Irodori-TTS-v4-Large-Demo`; torchao INT8, INT4, and FP8 quantized variants are planned (not yet released) at `Aratako/Irodori-TTS-v4-Large-Quantized` (**Reported**).[^irodori-v4-large-card]
- Source frontmatter declares `license: gemma`, `language: ja`, `pipeline_tag: text-to-speech`, and speech/voice/TTS tags (**Observed** by static inspection).[^irodori-v4-large-card]
- v4-Large scales the v4 architecture from approximately 766M to 3.29B parameters, including a 24-layer 2,048-dimensional Diffusion Transformer and a larger reference latent encoder; it replaces the ModernBERT-ja encoder with a fine-tuned text encoder from `google/t5gemma-2-1b-1b` shared between input text and captions, and trains the duration predictor separately with other parameters frozen, following the v4.1-Small approach (**Reported**).[^irodori-v4-large-card]

## Architecture

- Five components: (1) shared fine-tuned T5Gemma 2 text/caption encoder; (2) separate learned projectors mapping text and caption representations into their TTS conditioning spaces; (3) reference latent encoder over patched reference-audio latents for speaker identity (up to 120 s combined); (4) joint-attention DiT blocks combining text, reference, and caption conditioning with Low-Rank AdaLN, half-RoPE, and SwiGLU MLPs; (5) duration predictor from encoded text and conditioning vectors using stacked SwiGLU MLP blocks (**Reported**).[^irodori-v4-large-card]
- Audio is a continuous latent sequence via the `Aratako/Semantic-DACVAE-Japanese-32dim` codec (32-dim), decoded to 48 kHz waveforms (**Reported**).[^irodori-v4-large-card]

## Capabilities and usage

- Three synthesis modes in one model: zero-shot voice cloning from reference audio, text-based voice design from a caption alone, and style-controlled cloning combining both; for long references the card recommends multiple shorter clips from the same speaker rather than one uninterrupted recording, since training concatenated random short utterances per speaker (**Reported**).[^irodori-v4-large-card]
- Emoji control embeds emojis directly in the input text for speaking style, emotion, and non-verbal effects such as laughter, coughing, and sighs; the card defers the tag list to `EMOJI_ANNOTATIONS.md` in the GitHub repository, which was not fetched into `raw/` (**Reported**).[^irodori-v4-large-card]
- Every generated output carries a robust invisible SilentCipher audio watermark for responsible-use attribution (**Reported**).[^irodori-v4-large-card]
- Inference, installation, and training entry points are deferred to the GitHub repository; no install command, API fence, or config default is reproduced in the card (**Reported**).[^irodori-v4-large-card]

## Benchmarks

- Protocol shared across the five-seed evaluations (base seeds 0–4; mean ± population standard deviation unless noted): Japanese-reading runs use FP32, 40 RF steps, text CFG 3.0, no reference or caption; voice-design runs use FP32, 40 RF steps, text/caption CFG 3.0; cloning runs use FP32, 40 RF steps, text CFG 3.0, speaker CFG 5.0; Joyo, JSUT, Coco-Nut, and JVS sets were excluded from training (**Reported**).[^irodori-v4-large-card]
- Japanese reading (Joyo Kanji Yomi Benchmark Parakeet Edition, 13,536 sentences / 4,512 kanji-reading pairs; not comparable to original-edition Joyo figures in the v4-Small and v4.1-Small cards): v4.1-Small leads v4-Large — accuracy 93.42 ± 0.04% vs 92.80 ± 0.08%, target kana-CER 6.88 ± 0.08% vs 7.96 ± 0.36%, clipped 5.19 ± 0.05% vs 5.78 ± 0.06%, sentence kana-CER 1.25 ± 0.01% vs 1.51 ± 0.06%, text CER 4.68 ± 0.06% vs 4.87 ± 0.08%; the clipped variant caps each example CER at 100% before averaging (**Reported**).[^irodori-v4-large-card]
- Japanese reading (JSUT BASIC5000): v4.1-Small again leads — sentence kana-CER 3.43 ± 0.01% vs 3.67 ± 0.03%, standard CER 7.22 ± 0.12% vs 7.30 ± 0.01%; the card states v4-Large has slightly higher reading error rates on both benchmarks (**Reported**).[^irodori-v4-large-card]
- Voice design (all 2,890 public Coco-Nut test descriptions × short/medium/long texts = 8,670 clips per model, no reference audio, one deterministic seed per pair, Gemini 3.6 Flash 1–5 judge): v4-Large 4.2991 mean (14.63% scores 1–2, 76.24% scores 4–5) beats v4-Small 4.2339 (16.78%, 74.12%) and 600M-v3-VoiceDesign 4.2096 (17.09%, 73.30%); gain over v4-Small is +0.0652 with paired cluster-bootstrap 95% CI [+0.0353, +0.0955] over 578 segment IDs, largest on the long text (3.9851 → 4.1343); the card warns this is a lightweight single-judge internal comparison without human validation, not a research-grade benchmark (**Reported**).[^irodori-v4-large-card]
- Voice cloning (JVS, all 100 speakers × 5 texts × 5 seeds; nested one-clip / ~30 s / ~60 s / 120 s concatenated references; CAM++ similarity vs a fixed 10-utterance centroid): v4-Large cosine beats v4-Small at every length — one clip 0.6711 ± 0.0019 vs 0.6610 ± 0.0013 (top-1 87.00 ± 0.59% vs 84.60 ± 0.55%), ~30 s 0.7593 ± 0.0011 vs 0.7521 ± 0.0008 (99.48 ± 0.27% vs 98.56 ± 0.20%), ~60 s 0.7700 ± 0.0011 vs 0.7646 ± 0.0003 (99.60 ± 0.18% vs 99.56 ± 0.23%), 120 s 0.7788 ± 0.0005 vs 0.7753 ± 0.0009, with 120 s top-1 slightly lower at 99.64 ± 0.15% vs 99.76 ± 0.23%; most of the length gain is already present at ~30 s (**Reported**).[^irodori-v4-large-card]
- No large-scale human MOS, naturalness, prompt-adherence, or speaker-similarity evaluation was conducted; automatic scores do not fully represent human perception (**Reported**).[^irodori-v4-large-card]

## Training data and annotation

- Trained on an expanded high-quality Japanese speech dataset enriched with descriptive voice captions; emoji annotations and initial captions were labeled by a fine-tuned model based on `Qwen/Qwen3-Omni-30B-A3B-Instruct`, then rephrased with `Qwen/Qwen3.5-35B-A3B` (**Reported**).[^irodori-v4-large-card]

## Limitations

- Japanese text input only; uncommon names, specialized terminology, and context-dependent readings may be mispronounced (**Reported**).[^irodori-v4-large-card]
- Single short reference clips give substantially lower speaker similarity than longer ones; approximately 30 s or more of reasonably clean reference speech is recommended; a single uninterrupted long recording is accepted but unevaluated and may differ from the concatenated-utterance benchmark (**Reported**).[^irodori-v4-large-card]
- Contradictory reference-plus-caption conditioning can produce unstable quality, artifacts, or one condition overriding the other; keep base voice traits aligned with the reference and use the caption for emotion, style, or environment; complex or contradictory captions and emoji effects may be inconsistent (**Reported**).[^irodori-v4-large-card]

## License and ethical restrictions

- Weights fall under the Gemma Terms of Use (including the Prohibited Use Policy) because the shared encoder derives from `google/t5gemma-2-1b-1b`; redistribution and use must comply (**Reported**).[^irodori-v4-large-card]
- Additional card restrictions: no cloning or impersonating any individual without explicit consent; no deepfakes or misinformation-oriented synthesis; caption-only voices may coincidentally resemble a real person as a latent-space artifact, not an intended reproduction; developers disclaim liability and users bear jurisdictional compliance (**Reported**, with business-contact-style material absent and omitted).[^irodori-v4-large-card]
- Citation is `@misc{irodori-tts-v4-large}` (Chihiro Arata, 2026, Hugging Face) (**Reported**).[^irodori-v4-large-card]

## Relationships

- Voice-design comparison: [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) covers a 10-language 1.7B CustomVoice/VoiceDesign line with instruction control, while this concept covers a Japanese-only 3.29B flow-matching line with caption-plus-reference conditioning and emoji control; no shared codebase is asserted (**Synthesis**).[^irodori-v4-large-card]
- Diffusion-TTS comparison: [VoxCPM2](voxcpm2.md) covers a 2B tokenizer-free diffusion-autoregressive 48 kHz multilingual line with voice design and cloning, while this concept covers a 3.29B rectified-flow DiT over DACVAE latents for Japanese-only synthesis; no shared vendor or codebase is asserted (**Synthesis**).[^irodori-v4-large-card]
- Family packaging: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs `Irodori-TTS-500M-v3`, `600M-v3-VoiceDesign`, and `v4-Small` GGUF builds, while this concept covers the newer 3.29B v4-Large checkpoint, which has no GGUF entry in that catalog (**Synthesis**).[^irodori-v4-large-card]
- Survey membership: [TTS Model Survey](tts-model-survey.md) carries the catalog, Japanese-only coverage, capability, and licensing rows for this model (**Synthesis**).[^irodori-v4-large-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no checkpoint downloaded, no audio synthesized, and no reading-accuracy, caption-adherence, or speaker-similarity figure reproduced (**Synthesis**).[^irodori-v4-large-card]
- GitHub repository, demo Space, planned quantized repository, `EMOJI_ANNOTATIONS.md`, `VOICE_DESIGN_BENCHMARK.md`, `VOICE_CLONING_BENCHMARK.md`, the Semantic-DACVAE codec checkpoint, the T5Gemma 2 encoder, SilentCipher, and the Qwen annotator models were linked but not fetched and are not in `raw/`; weights, reference-audio files, and install/test fences were not inspected (**Synthesis**).[^irodori-v4-large-card]
- All identity, architecture, benchmark, training-data, usage, and license claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^irodori-v4-large-card]

[^irodori-v4-large-card]: [Irodori-TTS-v4-Large model card](../raw/Irodori-TTS-v4-Large.md) — locators: frontmatter (`license: gemma`, `language: ja`, `pipeline_tag: text-to-speech`); intro paragraph (RF-DiT, Text + Reference Speech + Caption Text, zero-shot cloning / voice design / style-controlled cloning, emoji control); `Key Features` (multi-modal design, 120 s long-reference cloning, flow matching over DACVAE latents, emoji control + EMOJI_ANNOTATIONS pointer, SilentCipher watermark); `What's New in v4-Large` (766M → 3.29B, 24-layer 2,048-dim DiT, T5Gemma 2 replacing ModernBERT-ja, frozen-parameter duration predictor, higher Coco-Nut scores); `Architecture` 5-component list + Semantic-DACVAE-Japanese-32dim 48 kHz paragraph; `Usage` (GitHub pointer, planned torchao INT8/INT4/FP8 repo) + `Long-reference Voice Cloning` (multiple-short-clips recommendation, unevaluated single-long-recording caveat); `Benchmarks` (seeds 0–4 mean ± population SD; train-exclusion sentence; FP32/40-step/CFG settings per suite) + Joyo Parakeet-Edition table (v4.1-Small vs v4-Large, 13,536 sentences / 4,512 pairs, clipped-CER note, non-comparability warning) + JSUT BASIC5000 table + `Voice Design` (2,890 Coco-Nut descriptions × 3 texts = 8,670 clips, Gemini 3.6 Flash 1–5, 4.2096/4.2339/4.2991 table, +0.0652 CI [+0.0353, +0.0955], long-text 3.9851 → 4.1343, single-seed + lightweight-judge caveats, VOICE_DESIGN_BENCHMARK pointer) + `Voice Cloning and Reference Length` (JVS 100 speakers × 5 texts × 5 seeds, nested 1-clip/30 s/60 s/120 s, fixed 10-utterance centroid, 8-row CAM++ cosine/top-1 table, ~30 s saturation note, VOICE_CLONING_BENCHMARK pointer); `Training Data & Annotation` (expanded Japanese set, Qwen3-Omni-30B-A3B-Instruct labels + Qwen3.5-35B-A3B rephrase); `Limitations` 8 bullets (Japanese-only, short-reference gap + 30 s rule, concatenated-utterance composition caveat, conditioning conflicts, prompt adherence, emoji variance, kanji reading, no human MOS); `License & Ethical Restrictions` (Gemma Terms + Prohibited Use Policy via t5gemma-2-1b-1b; 4 ethical bullets); `Acknowledgments` (Echo-TTS, DACVAE, t5gemma-2-1b-1b, SilentCipher); `Citation` BibTeX (`irodori-tts-v4-large`).
