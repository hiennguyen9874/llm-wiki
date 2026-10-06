---
type: Concept
title: Higgs Audio v3 STT
description: 2.68B-parameter Whisper-Large-v3-encoder plus Qwen3-1.7B-decoder ASR model with thinking mode, June 2026 retrain, and deterministic repetition-loop post-processing.
tags: [stt, asr, speech-recognition, whisper, qwen, open-asr-leaderboard]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: higgs-v3-stt-card
    resource: ../raw/higgs-audio-v3-stt.md
    kind: documentation
    title: Higgs Audio v3 STT model card
---

Higgs Audio v3 STT is a 2.68B-parameter speech-to-text model from Boson AI combining a Whisper-Large-v3 encoder with a Qwen3-1.7B decoder and thinking-mode transcription, served through a custom Transformers architecture with deterministic phrase- and word-level repetition-loop post-processing, whose June 2026 checkpoint refresh supersedes earlier card figures and defers to the independent Open ASR Leaderboard for evaluation (**Reported**).[^higgs-v3-stt-card]

## Model identity and release

- Weights are `bosonai/higgs-audio-v3-stt` on Hugging Face; card frontmatter declares `license: apache-2.0`, `language: [en]`, `pipeline_tag: automatic-speech-recognition`, and tags `automatic-speech-recognition`, `hf-asr-leaderboard`, `whisper`, and `qwen` (**Reported**, with frontmatter fields **Observed** by static inspection).[^higgs-v3-stt-card]
- This is the STT sibling of the Boson Higgs Audio v3 family; the TTS side is compiled separately in [Higgs TTS 3](higgs-tts-3-4b.md), which covers the ~4B TTS weights, benchmarks, and serving paths rather than this checkpoint (**Synthesis**).[^higgs-v3-stt-card]

## Architecture

- Encoder is Whisper-Large-v3 with attention layers fine-tuned in v2; decoder is Qwen3-1.7B; total parameters are 2.68B (**Reported**).[^higgs-v3-stt-card]
- Audio input is 16 kHz mono WAV; the model supports thinking mode for improved accuracy (**Reported**).[^higgs-v3-stt-card]
- Custom architecture: loading requires `trust_remote_code=True` (**Reported**).[^higgs-v3-stt-card]

## June 2026 checkpoint update

- Fine-tuning data was refreshed to public train splits of AMI (IHM), VoxPopuli (en), SPGISpeech, LibriSpeech, TED-LIUM, and GigaSpeech, plus the public Earnings22 train split (`sanchit-gandhi/earnings22_split`) with all rows from source recordings appearing in the ESB/Open-ASR test sets excluded (**Reported**).[^higgs-v3-stt-card]
- `transcribe.py` adds a phrase-level repetition-loop collapse alongside the existing word-repetition cap; both are deterministic and applied uniformly to every dataset, with `ngram_loop_fix.py` carrying the standalone reference and tests (**Reported**).[^higgs-v3-stt-card]
- Evaluation: the card points to the independently produced [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard), notes that figures listed there predate the update until the entry is re-evaluated, and states that figures previously listed on the card came from an earlier checkpoint and evaluation setup and are superseded; previous weights remain available via git revision history (**Reported**).[^higgs-v3-stt-card]
- No numeric WER is recorded in this wiki for the current checkpoint because the card prints none — rank comparisons against Open ASR averages in [ASR/STT Model Survey](asr-stt-model-survey.md) should not include this model until the leaderboard re-evaluates it (**Synthesis**).[^higgs-v3-stt-card]

## Inference

- Requirements are `torch`, `transformers>=4.51.0`, and `boson_multimodal` for audio preprocessing (**Reported**).[^higgs-v3-stt-card]
- Loading uses `AutoConfig`/`AutoModel`/`AutoTokenizer` from `bosonai/higgs-audio-v3-stt` with `trust_remote_code=True`, `torch_dtype=torch.bfloat16`, `attn_implementation="eager"`, and `device_map="cuda:0"`, then `.eval()`; the card sets `audio_out_bos_token_id` and `audio_eos_token_id` from `<|audio_out_bos|>` and `<|audio_eos|>` (**Reported**).[^higgs-v3-stt-card]
- Audio collation uses `WhisperProcessor.from_pretrained("openai/whisper-large-v3")` plus `HiggsAudioSampleCollator` from `boson_multimodal`, configured from the model config (`audio_in_token_idx`, `audio_out_token_idx`, stream BOS/EOS ids, `encode_whisper_embed`, `pad_token_id`, delay-pattern flags, codebook count, 30 s chunk size, `max_length` encoder padding); input audio is resampled to 16 kHz mono when needed (**Reported**).[^higgs-v3-stt-card]
- The worked prompt is `"Transcribe the speech. Output only the spoken words in lowercase with no punctuation."` with `prepare_chatml_sample_qwen(enable_thinking=True)`; generation uses `max_new_tokens=1024`, `use_cache=True`, `do_sample=False`, and `stop_strings=["<|im_end|>", "<|endoftext|>"]`, after which the card strips the `<think>…</think>` block and `<|…|>` special tokens (**Reported**).[^higgs-v3-stt-card]
- For the exact evaluation pipeline including deterministic repetition/loop post-processing, the card directs users to the repo-bundled `transcribe()` / `transcribe_batch()` in `transcribe.py` rather than the inline sketch (**Reported**).[^higgs-v3-stt-card]
- No streaming/chunk-latency knob, timestamp, punctuation toggle beyond the lowercase prompt, hotword, diarization, or vLLM/SGLang/server claim appears in this card (**Synthesis**).[^higgs-v3-stt-card]

## Relationships

- STT sibling in the same upstream family: [Higgs TTS 3](higgs-tts-3-4b.md) covers the 4B expressive TTS weights with inline emotion/prosody/SFX control and SGLang/vLLM-Omni serving, while this concept covers the 2.68B STT weights and transcription pipeline; no shared checkpoint is asserted (**Synthesis**).[^higgs-v3-stt-card]
- Shares the Whisper-encoder plus Qwen-decoder pattern with [ARK-ASR-3B](ark-asr-3b.md) (Whisper-style encoder, MLP adapter, Qwen decoder, 5.04% 7-split Open ASR average) and the SALM pattern of [Canary-Qwen-2.5B](canary-qwen-2.5b.md) (FastConformer encoder plus Qwen3-1.7B decoder, 5.63% 8-split mean), but Higgs Audio v3 STT's distinguishing card claims are thinking-mode decoding and deterministic repetition-loop post-processing, with no shared numeric benchmark in this card (**Synthesis**).[^higgs-v3-stt-card]
- Encoder/tokenizer lineage with the [Qwen3-ASR family](qwen3-asr-family.md) and [Faster-Whisper](faster-whisper.md) in the broad sense (Qwen decoder idiom; Whisper-Large-v3 encoder/processor reuse), but no shared checkpoint, training set, or evaluation protocol is asserted (**Synthesis**).[^higgs-v3-stt-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no audio transcribed, and no accuracy, thinking-mode gain, or repetition-fix claim reproduced (**Synthesis**).[^higgs-v3-stt-card]
- `transcribe.py`, `ngram_loop_fix.py`, the `boson_multimodal` package, the Hugging Face checkpoint and git history, and the Open ASR Leaderboard were linked but not fetched and were not present in `raw/`; checkpoint, tokenizer, and training-split contents were not inspected (**Synthesis**).[^higgs-v3-stt-card]
- All architecture, training-data, post-processing-effect, and usage claims are source assertions without independent verification in this wiki; release and benchmark pointers carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^higgs-v3-stt-card]

[^higgs-v3-stt-card]: [Higgs Audio v3 STT model card](../raw/higgs-audio-v3-stt.md) — locators: frontmatter (`license: apache-2.0`, `language: [en]`, `pipeline_tag: automatic-speech-recognition`, `tags`); header (Whisper-Large-v3 encoder + Qwen3 decoder, 2.68B total); `Update (June 2026)` section (AMI-IHM / VoxPopuli-en / SPGISpeech / LibriSpeech / TED-LIUM / GigaSpeech refresh, Earnings22 `sanchit-gandhi/earnings22_split` exclusion, phrase-level collapse + word-repetition cap in `transcribe.py`, `ngram_loop_fix.py` reference/tests, Open ASR Leaderboard pointer with predate/re-evaluation note, superseded-figures statement, git-history note); `Usage` section (`trust_remote_code=True` warning, model/tokenizer load fence, full transcription fence with `boson_multimodal` collator/`WhisperProcessor`/`ChatMLSample`/`prepare_chatml_sample_qwen(enable_thinking=True)`, 16 kHz resample, lowercase prompt, `generate(max_new_tokens=1024, do_sample=False)` with `stop_strings`, `<think>`/`<|…|>` strip, `transcribe()`/`transcribe_batch()` pointer); `Requirements` fence (`torch`, `transformers>=4.51.0`, `boson_multimodal`); `Architecture` list (Whisper-Large-v3 encoder with v2 attention fine-tune, Qwen3-1.7B decoder, 2.68B, 16 kHz mono, thinking mode).
