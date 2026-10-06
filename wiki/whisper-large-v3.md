---
type: Concept
title: Whisper Large v3
description: OpenAI 1550M-parameter multilingual ASR and speech-translation checkpoint with 128-bin mel input and a Cantonese token, trained on 1M weakly labeled plus 4M large-v2 pseudo-labeled hours, with Transformers pipeline usage, chunked long-form, and torch.compile plus Flash-Attention speed paths.
tags: [stt, asr, whisper, multilingual, transformers]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: whisper-v3-card
    resource: ../raw/whisper-large-v3.md
    kind: documentation
    title: Whisper large-v3 model card (Hugging Face)
---

OpenAI's `whisper-large-v3` is the 1550M-parameter multilingual Transformer encoder-decoder for ASR and speech translation that keeps the large/large-v2 architecture except for 128 (vs 80) mel bins and a new Cantonese language token; trained for 2.0 epochs over 1M hours of weakly labeled plus 4M hours of large-v2 pseudo-labeled audio with a reported 10–20% error reduction over large-v2, it is served in this card through Transformers `pipeline` and model-plus-processor usage with transcription versus English translation modes, sentence- and word-level timestamps, sequential versus chunked 30-second-window long-form, and `torch.compile`, Flash-Attention 2, and SDPA speed paths, alongside hallucination, language-unevenness, and repetition limitations (**Reported**).[^whisper-v3-card]

## Identity and lineage

- Family: state-of-the-art ASR and speech-translation model from *Robust Speech Recognition via Large-Scale Weak Supervision* (Radford et al., OpenAI), trained on over 5M hours of labeled data with strong zero-shot generalization across datasets and domains (**Reported**).[^whisper-v3-card]
- v3 deltas: same architecture as large and large-v2 except the spectrogram input uses 128 mel frequency bins instead of 80, plus a new language token for Cantonese (**Reported**).[^whisper-v3-card]
- Training mix: 1M hours weakly labeled plus 4M hours pseudo-labeled with Whisper large-v2, trained for 2.0 epochs over the mixture; reported 10–20% error reduction over large-v2 across many languages, with checkpoint choice deferred to the card's `Model details` table (**Reported**).[^whisper-v3-card]
- Card provenance and license: content partly written by the Hugging Face team and partly copied from the original model card; frontmatter declares `license: apache-2.0`, `pipeline_tag: automatic-speech-recognition`, and a ~99-code `language` list (**Reported**).[^whisper-v3-card]

## Architecture and model family

- Architecture: Transformer encoder-decoder (sequence-to-sequence); English-only checkpoints cover English recognition while multilingual checkpoints cover multilingual recognition plus speech translation; transcription predicts the source language while translation predicts a different (English) target language (**Reported**).[^whisper-v3-card]
- Size table as printed (parameters; English-only vs multilingual availability): tiny 39M, base 74M, small 244M, medium 769M, large 1550M, large-v2 1550M, large-v3 1550M; only the large line is multilingual-only, and the card links each checkpoint to the Hub (**Reported**).[^whisper-v3-card]

## Transformers usage

- Setup: `pip install transformers datasets[audio] accelerate`; canonical pattern is `AutoModelForSpeechSeq2Seq` plus `AutoProcessor` wrapped in `pipeline("automatic-speech-recognition")`, with `torch.float16` on CUDA and `float32` on CPU, `low_cpu_mem_usage`, and `use_safetensors` (**Reported**, transcribed not executed).[^whisper-v3-card]
- Basic transcription: `pipe(audio)` on a loaded sample (card uses `distil-whisper/librispeech_long` and `hf-internal-testing/librispeech_asr_dummy` clips), a local path such as `pipe("audio.mp3")`, or a list of files with `batch_size` for parallel transcription (**Reported**).[^whisper-v3-card]
- Decoding controls: temperature fallback and condition-on-previous-tokens are supported; the card fence sets `max_new_tokens: 448`, `num_beams: 1`, `condition_on_prev_tokens: False`, `compression_ratio_threshold: 1.35`, `temperature: (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)`, `logprob_threshold: -1.0`, `no_speech_threshold: 0.6`, and `return_timestamps: True` (**Reported**).[^whisper-v3-card]
- Language and task: source language is auto-detected but can be forced with `generate_kwargs={"language": "english"}`; default task is same-language transcription, while `generate_kwargs={"task": "translate"}` performs translation with English as target (**Reported**).[^whisper-v3-card]
- Timestamps: `return_timestamps=True` yields sentence-level `chunks`, `return_timestamps="word"` yields word-level `chunks`; language, task, and timestamp arguments compose (e.g. French audio with sentence timestamps) (**Reported**).[^whisper-v3-card]
- Direct model-plus-processor path: processor call with `truncation=False`, `padding="longest"`, `return_attention_mask=True`, then `model.generate(**inputs, **gen_kwargs)` and `processor.batch_decode(..., skip_special_tokens=True, decode_with_timestamps=False)` (**Reported**).[^whisper-v3-card]

## Long-form transcription

- Constraint: 30-second receptive field, so longer audio needs a long-form algorithm; sequential uses a sliding-window buffered pass over 30-second slices, while chunked splits audio into overlapped shorts, transcribes independently, and stitches at boundaries (**Reported**).[^whisper-v3-card]
- Selection rule as stated: sequential when accuracy matters most or when transcribing batches of long files (comparable latency to chunked at up to 0.5% better WER); chunked when speed matters most or when transcribing a single long file (**Reported**).[^whisper-v3-card]
- Transformers defaults and fences: sequential is the default; chunked is enabled with `chunk_length_s=30` plus `batch_size` (card fence uses 16, set per device) (**Reported**).[^whisper-v3-card]

## Speed and memory options

- `torch.compile`: card claims 4.5x forward-pass speed-ups via `torch.compile(model.forward, mode="reduce-overhead", fullgraph=True)` with static cache (`cache_implementation="static"`, `max_new_tokens=256`) after two warm-up steps under `sdpa_kernel(SDPBackend.MATH)`; explicitly incompatible with the chunked long-form algorithm and Flash-Attention 2 (**Reported**, transcribed not executed).[^whisper-v3-card]
- Flash-Attention 2: recommended when the GPU supports it and `torch.compile` is unused; install `flash-attn` with `--no-build-isolation` and pass `attn_implementation="flash_attention_2"` to `from_pretrained` (**Reported**).[^whisper-v3-card]
- SDPA: PyTorch scaled dot-product attention is on by default for PyTorch 2.1.1+, checkable via `is_torch_sdpa_available()`; settable explicitly with `attn_implementation="sdpa"` (**Reported**).[^whisper-v3-card]

## Fine-tuning and intended use

- Fine-tuning: pre-trained generalization can be improved per language and task; the card points to the *Fine-Tune Whisper with Transformers* blog for a recipe with as little as 5 hours of labeled data (**Reported**).[^whisper-v3-card]
- Intended users: primarily AI researchers studying robustness, generalization, capabilities, biases, and constraints, with English ASR as a notable developer use; deployment requires robust in-context evaluation, and the card cautions against non-consensual transcription, subjective classification (including inferred human attributes), and high-risk decision-making use (**Reported**).[^whisper-v3-card]

## Performance, limitations, and implications

- Robustness claim: improved robustness to accents, background noise, and technical language plus zero-shot multilingual-to-English translation, with near-state-of-the-art recognition and translation accuracy; transcription performance in a language correlates with its training-data share (**Reported**, no numeric table in this card).[^whisper-v3-card]
- Hallucination: weakly supervised noisy-data training can emit text not present in the audio; the card hypothesizes competing next-word prediction versus transcription objectives (**Reported**).[^whisper-v3-card]
- Unevenness: lower accuracy on low-resource or low-discoverability languages and disparate performance across accents, dialects, genders, races, and ages, with full results deferred to the paper (**Reported**).[^whisper-v3-card]
- Repetition: sequence-to-sequence decoding can loop repetitively, mitigated but not eliminated by beam search and temperature scheduling (**Reported**).[^whisper-v3-card]
- Implications: accessibility gains and near-real-time applications built on top are anticipated, alongside dual-use surveillance scale-up and out-of-the-box speaker-recognition safety concerns; transcription cost is not expected to be the binding constraint on surveillance (**Reported**).[^whisper-v3-card]
- Citation: Radford et al. 2022, `arXiv:2212.04356`, BibTeX as printed (**Reported**).[^whisper-v3-card]

## Relationships

- Pruned derivative: [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) cuts this checkpoint's decoder from 32 to 4 layers (809M) for faster inference at minor quality cost; consult that page for the turbo card's usage and limits (**Synthesis**).[^whisper-v3-card]
- Distilled relative: [Distil-Large-v3.5](distil-large-v3.5.md) distills `large-v3` and benchmarks English short/long-form WER plus RTFx; consult that page before comparing distilled-versus-full accuracy and speed (**Synthesis**).[^whisper-v3-card]
- Runtime: [Faster-Whisper](faster-whisper.md) serves Whisper-family weights via CTranslate2 with batching, quantization, and VAD filtering; consult that page for its 13-minute-audio benchmark and conversion path (**Synthesis**).[^whisper-v3-card]
- Streaming wrapper: [WhisperLiveKit](whisperlivekit.md) wraps faster-whisper-class backends with SimulStreaming and LocalAgreement policies because this architecture is not natively streaming (**Synthesis**).[^whisper-v3-card]
- Decoding hygiene: [Whisper Hallucination Mitigation for Vietnamese](whisper-hallucination-mitigation.md) compiles faster-whisper decoding parameters, confidence filters, and a Vietnamese blacklist for this model family (**Synthesis**).[^whisper-v3-card]
- Surveyed in the [ASR/STT Model Survey](asr-stt-model-survey.md) catalog and capability rows (**Synthesis**).[^whisper-v3-card]

## Coverage and limits

- Source inspected statically only; no `pip install`, weight download, transcription, long-form run, `torch.compile`, Flash-Attention, SDPA check, or fine-tune was executed, and no speed or accuracy figure was reproduced (**Synthesis**).[^whisper-v3-card]
- Referenced but unfetched and absent from `raw/`: the Whisper paper, the fine-tune blog, the Hub checkpoints and datasets (`openai/whisper-large-v3`, `distil-whisper/librispeech_long`, `hf-internal-testing/librispeech_asr_dummy`), Transformers/SDPA/Flash-Attention/torch docs, and the `flash-attn` package; all fences above are transcribed, not executed (**Synthesis**).[^whisper-v3-card]
- This card prints no numeric WER or RTFx table for the large-v3 checkpoint itself (only the 10–20% reduction claim over large-v2); do not rank it against wiki Open ASR means without an external benchmark, and its `apache-2.0` frontmatter license plus release status carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^whisper-v3-card]

[^whisper-v3-card]: [Whisper large-v3 model card](../raw/whisper-large-v3.md) — locators: frontmatter (`license: apache-2.0`, `pipeline_tag: automatic-speech-recognition`, ~99-code `language` list); header (SOTA ASR/translation positioning, >5M-hour training, large-v3 deltas: 128 mel bins, Cantonese token; 1M weakly + 4M large-v2 pseudo-labeled hours, 2.0 epochs, 10–20% error reduction over large-v2; HF-team disclaimer); `Usage` (install fence; `pipeline` + `AutoModelForSpeechSeq2Seq`/`AutoProcessor` fence; local-file and `batch_size` fences; `generate_kwargs` decoding fence; language/task fences; sentence- and word-timestamp fences; model-plus-processor `<details>` fence); `Additional Speed & Memory Improvements` > `Chunked Long-Form` (30 s receptive field; sequential-vs-chunked rules; `chunk_length_s=30` + `batch_size=16` fence); `Torch compile` (4.5x claim, incompatibility note, static-cache + warm-up fence); `Flash Attention 2` (`flash-attn --no-build-isolation` + `attn_implementation` fence); `Torch Scale-Product-Attention` (`is_torch_sdpa_available()` + version rule); `Model details` (encoder-decoder, English-only vs multilingual, transcription-vs-translation, 7-row size/parameter/availability table); `Fine-Tuning` (5-hour blog pointer); `Evaluated Use` (researcher/developer scope, non-consensual/subjective/high-risk cautions); `Training Data` (1M + 4M mix, language-share correlation); `Performance and Limitations` (robustness, hallucination hypothesis, unevenness, repetition); `Broader Implications` (accessibility, surveillance/dual-use, speaker recognition); `BibTeX` (radford2022whisper).
