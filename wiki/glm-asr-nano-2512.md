---
type: Concept
title: GLM-ASR-Nano-2512
description: 1.5B-parameter open-source ASR model with Cantonese and dialect coverage, low-volume speech robustness, and Transformers inference with vLLM and SGLang support.
tags: [ml, asr, speech-recognition, chinese-dialects]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T08:00:00Z }
stale_after: 2027-10-06
sources:
  - id: glm-asr-nano-card
    resource: ../raw/GLM-ASR-Nano-2512.md
    kind: documentation
    title: GLM-ASR-Nano-2512 model card
---

GLM-ASR-Nano-2512 is a 1.5B-parameter open-source automatic speech recognition model from zai-org, positioned as a compact Whisper V3 alternative with Cantonese and dialect optimization plus low-volume ("Whisper/Quiet Speech") robustness, reporting a 4.10 lowest-average error rate among comparable open-source models with strength on Chinese sets, and run through Hugging Face Transformers with planned vLLM and SGLang support (**Reported**).[^glm-asr-nano-card]

## Model identity

- Card title is `GLM-ASR-Nano-2512`; Hugging Face identifier used in all code fences is `zai-org/GLM-ASR-Nano-2512`; code and further examples live at `https://github.com/zai-org/GLM-ASR`; frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, `language: [en, zh]`, and `license: mit` (**Reported**, with frontmatter fields **Observed** by static inspection).[^glm-asr-nano-card]
- Positioning claim: robust open-source speech recognition with 1.5B parameters, designed for real-world complexity, outperforming OpenAI Whisper V3 on multiple benchmarks while staying compact (**Reported**).[^glm-asr-nano-card]

## Key capabilities

- Exceptional dialect support: beyond standard Mandarin and English, highly optimized for Cantonese (粤语) and other dialects, stated as bridging the gap in dialectal speech recognition (**Reported**).[^glm-asr-nano-card]
- Low-volume speech robustness: specifically trained for "Whisper/Quiet Speech" scenarios, capturing and transcribing extremely low-volume audio that traditional models often miss (**Reported**).[^glm-asr-nano-card]
- SOTA performance claim: lowest average error rate (4.10) among comparable open-source models, with significant advantages in Chinese benchmarks such as Wenet Meeting and Aishell-1 (**Reported**).[^glm-asr-nano-card]

## Benchmark

- The card states evaluation against leading open-source and closed-source models with superior performance, particularly in challenging acoustic environments; numeric evidence is carried only by the `bench.png` figure, which was not fetched into `raw/` and whose values are not transcribed in the card text (**Reported**, with figure-availability limit **Synthesis**).[^glm-asr-nano-card]
- Figure notes define Wenet Meeting as reflecting real-world meeting scenarios with noise and overlapping speech, and Aishell-1 as a standard Mandarin benchmark (**Reported**).[^glm-asr-nano-card]

## Inference and serving

- Runtime scope: easily integrated using the `transformers` library; the card states support for `transformers 5.x` as well as inference frameworks such as `vLLM` and `SGLang` — worded as "We will support", so treat vLLM/SGLang as planned rather than demonstrated in this card (**Reported**).[^glm-asr-nano-card]
- Install from source with `pip install git+https://github.com/huggingface/transformers` (**Reported**).[^glm-asr-nano-card]
- Basic usage loads `AutoProcessor.from_pretrained("zai-org/GLM-ASR-Nano-2512")` and `AutoModelForSeq2SeqLM.from_pretrained("zai-org/GLM-ASR-Nano-2512", dtype="auto", device_map="auto")`, builds input with `processor.apply_transcription_request("https://huggingface.co/datasets/hf-internal-testing/dummy-audio-samples/resolve/main/bcn_weather.mp3")`, moves inputs with `inputs.to(model.device, dtype=model.dtype)`, decodes with `model.generate(**inputs, do_sample=False, max_new_tokens=500)`, and recovers text with `processor.batch_decode(outputs[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)` (**Reported**).[^glm-asr-nano-card]
- Audio-array path uses `GlmAsrForConditionalGeneration.from_pretrained(...)` plus `AutoProcessor`, loads `hf-internal-testing/librispeech_asr_dummy` (`clean`, `validation` split), casts the audio column with `Audio(sampling_rate=processor.feature_extractor.sampling_rate)`, and passes the raw array to `processor.apply_transcription_request(audio_array)` before the same move/generate/decode steps (**Reported**).[^glm-asr-nano-card]
- Batched inference passes a list of two URLs (`bcn_weather.mp3`, `obama.mp3` under `hf-internal-testing/dummy-audio-samples`) to a single `processor.apply_transcription_request([...])` call, then the same move/generate/batch-decode steps (**Reported**).[^glm-asr-nano-card]

## Relationships

- Compared by [Fun-ASR-Nano-2512](fun-asr-nano-2512.md): that concept's open-source and industry WER tables include `GLM-ASR-nano` / `GLM-ASR-Nano` columns (1.5B, open-source) as a baseline against Fun-ASR-nano (0.8B), so cross-read them when comparing compact Chinese-oriented ASR checkpoints; the WER numbers themselves are compiled in the Fun-ASR concept, not in this card (**Synthesis**).[^glm-asr-nano-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio transcribed, and no error-rate or Whisper-comparison claims reproduced (**Synthesis**).[^glm-asr-nano-card]
- Linked but unfetched and not in `raw/`: header logo SVG, WeChat community image, benchmark figure `bench.png`, GitHub repository `zai-org/GLM-ASR`, Hugging Face model `zai-org/GLM-ASR-Nano-2512`, source-installed `transformers`, and the `hf-internal-testing` dummy-audio URLs plus `librispeech_asr_dummy` dataset; the WeChat link and logo are excluded as community/social and decorative material (**Synthesis**).[^glm-asr-nano-card]
- Material gaps in the card: no architecture (encoder/decoder), training-data, compute, release-date, or decoding-beyond-`do_sample=False` detail; no per-dataset numeric table in text; vLLM/SGLang usage has no commands; all identity, dialect, quiet-speech, and accuracy claims are source assertions without independent verification in this wiki; model-release, benchmark, and API details carry `stale_after: 2027-10-06` per the `ml` domain rule (**Synthesis**).[^glm-asr-nano-card]

[^glm-asr-nano-card]: [GLM-ASR-Nano-2512 model card](../raw/GLM-ASR-Nano-2512.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `library_name`); header (logo SVG, WeChat community link); section `Model Introduction` (1.5B parameters, Whisper V3 comparison, Cantonese/ dialect bullet, low-volume bullet, 4.10 average error rate with Wenet Meeting and Aishell-1 mention); section `Benchmark` (`bench.png` figure plus Wenet Meeting / Aishell-1 notes); section `Inference` (transformers 5.x plus vLLM/SGLang sentence, GitHub link, source-install command, `Basic Usage` fence with `AutoModelForSeq2SeqLM`/`AutoProcessor`/`apply_transcription_request`/`generate`/`batch_decode`, `Using Audio Arrays Directly` fence with `GlmAsrForConditionalGeneration`/`load_dataset`/`Audio`, `Batched Inference` fence with two-URL list).
