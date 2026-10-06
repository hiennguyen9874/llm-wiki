---
type: Concept
title: IndicConformer-600M-Multilingual
description: AI4Bharat 600M-parameter multilingual Conformer hybrid CTC plus RNNT ASR model covering 22 official Indian languages with dual CTC/RNNT decoding and Transformers inference.
tags: [stt, asr, multilingual, conformer, indic]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: indic-conformer-card
    resource: ../raw/indic-conformer-600m-multilingual.md
    kind: documentation
    title: IndicConformer-600M-Multilingual model card
---

IndicConformer-600M-Multi (`ai4bharat/indic-conformer-600m-multilingual`) is AI4Bharat's 600M-parameter multilingual Conformer-based hybrid CTC plus RNNT ASR model covering 22 official Indian languages (IN-22), released under the MIT license with dual CTC and RNNT decoding through a Transformers `AutoModel` entry point (**Reported**).[^indic-conformer-card]

## Identity and release

- Model name `IndicConformer-600M-Multi`; repository `ai4bharat/indic-conformer-600m-multilingual`; architecture described as multilingual Conformer-based hybrid CTC plus RNNT; parameter size 600M; languages supported IN-22 (**Reported**).[^indic-conformer-card]
- Source frontmatter declares `license: mit` and `pipeline_tag: automatic-speech-recognition` (**Observed** by static inspection).[^indic-conformer-card]
- Positioned in the card as AI4Bharat's suite for accurate speech-to-text across all 22 official Indian languages and as the country's first open-source ASR system covering that language set, framed as a tool for inclusive and accessible technology (**Reported**).[^indic-conformer-card]
- No release date, training-data mix, training procedure, benchmark table, or streaming/latency claim is stated in the card (**Observed** by static inspection).[^indic-conformer-card]

## Architecture and decoding

- Conformer-based hybrid model supporting two decoding strategies: CTC (Connectionist Temporal Classification) and RNNT (Recurrent Neural Network Transducer) (**Reported**).[^indic-conformer-card]
- The card gives no encoder/decoder layer counts, tokenizer sizes, vocabulary, feature front-end, or decoding hyperparameters beyond the CTC/RNNT choice (**Observed** by static inspection).[^indic-conformer-card]

## Supported languages

- 22 officially recognized languages of India with card-given codes: Assamese (`as`), Bengali (`bn`), Bodo (`brx`), Dogri (`doi`), Gujarati (`gu`), Hindi (`hi`), Kannada (`kn`), Konkani (`kok`), Kashmiri (`ks`), Maithili (`mai`), Malayalam (`ml`), Manipuri (`mni`), Marathi (`mr`), Nepali (`ne`), Odia (`or`), Punjabi (`pa`), Sanskrit (`sa`), Santali (`sat`), Sindhi (`sd`), Tamil (`ta`), Telugu (`te`), Urdu (`ur`) (**Reported**).[^indic-conformer-card]
- Per-language tokenizers are pointed to externally at `AI4Bharat/IndicVoices` under `artifacts/tokenizers`; that repository was not fetched in this ingest (**Reported**, with unfetched-pointer limit).[^indic-conformer-card]

## Inference and usage

- Installation fence: `pip install transformers torchaudio "onnxruntime==1.20.1" "onnx==1.20.1" "onnxruntime-gpu==1.20.1"` (**Reported**).[^indic-conformer-card]
- Transformers fence: `AutoModel.from_pretrained("ai4bharat/indic-conformer-600m-multilingual", trust_remote_code=True)`; audio loaded with `torchaudio.load`, mixed to mono via `torch.mean`, resampled to 16 kHz when needed, then transcribed with `model(wav, "hi", "ctc")` or `model(wav, "hi", "rnnt")` (**Reported**).[^indic-conformer-card]
- The example pins 16 kHz as the expected sample rate and uses Hindi (`hi`) as the language argument; supported sample-rate range, chunking, batching, punctuation, timestamps, and hardware requirements are not stated (**Reported** for the example; missing scope is **Observed**).[^indic-conformer-card]
- No usage command was executed and no transcription output reproduced in this ingest (**Synthesis**).[^indic-conformer-card]

## Relationships

- Indic-coverage peer [Qwen3-ASR family](qwen3-asr-family.md): broader 30-language plus 22-Chinese-dialect audio-LLM line with published WER tables and unified offline/streaming, versus IndicConformer's 22-Indic-language Conformer hybrid with dual CTC/RNNT decoding and no numeric table in the card; prefer IndicConformer when the task is scoped to the IN-22 set under MIT terms and Qwen3-ASR when Asian breadth or benchmarked accuracy matters (**Synthesis**).[^indic-conformer-card]
- Multilingual-Conformer peer [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md): 2B-parameter Conformer encoder plus Transformer decoder over 14 languages with published Open ASR figures, versus this 600M hybrid over 22 Indic languages with no figures; compare them when an Indic-heavy workload meets a Conformer-architecture constraint (**Synthesis**).[^indic-conformer-card]
- Massive-multilingual reference [Omnilingual ASR](omnilingual-asr.md): 1600-plus-language W2V/CTC/LLM family with per-language CER tables, versus this focused IN-22 checkpoint; use Omnilingual when low-resource breadth beyond India matters and IndicConformer when a compact single Indic checkpoint suffices (**Synthesis**).[^indic-conformer-card]

## Coverage and limits

- Source inspected statically only; no `transformers`/`torchaudio`/`onnxruntime` install, no weight download, no audio transcribed, and no accuracy, latency, or throughput figure reproduced (**Synthesis**).[^indic-conformer-card]
- Referenced but unfetched and absent from `raw/`: the Hugging Face repository page, the `AI4Bharat/IndicVoices` tokenizer tree, and any training, evaluation, or benchmark attachments behind those links (**Synthesis**).[^indic-conformer-card]
- Author contact names and addresses in the card's `Contact` section are excluded from this concept as non-durable operational detail (**Synthesis**).[^indic-conformer-card]
- All capability, coverage, compatibility, and positioning claims are source assertions without independent verification in this wiki; model-release figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^indic-conformer-card]

[^indic-conformer-card]: [IndicConformer-600M-Multilingual model card](../raw/indic-conformer-600m-multilingual.md) — locators: frontmatter (`license: mit`, `pipeline_tag: automatic-speech-recognition`); header intro (IndicConformer suite, 22 official Indian languages, first open-source claim, MIT release line); `Model Details` (model name `IndicConformer-600M-Multi`, repository link, hybrid CTC plus RNNT architecture, 600M params, IN-22); `Model Usage` (CTC/RNNT decoding bullets; `Installation` pip fence with `transformers`, `torchaudio`, pinned `onnxruntime`/`onnx`/`onnxruntime-gpu` 1.20.1; `Inference Example` fence with `AutoModel.from_pretrained` plus `trust_remote_code`, `torchaudio.load`, mono mean, 16 kHz resample, `model(wav, "hi", "ctc")` and `model(wav, "hi", "rnnt")` calls); `Supported Languages` (22-language list with `as`/`bn`/`brx`/`doi`/`gu`/`hi`/`kn`/`kok`/`ks`/`mai`/`ml`/`mni`/`mr`/`ne`/`or`/`pa`/`sa`/`sat`/`sd`/`ta`/`te`/`ur` codes; external `IndicVoices/artifacts/tokenizers` link); `Contact` section (excluded).
