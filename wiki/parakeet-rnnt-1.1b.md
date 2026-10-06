---
type: Concept
title: Parakeet RNNT 1.1B
description: NVIDIA NeMo and Suno 1.1B-parameter English offline FastConformer-Transducer (RNNT) ASR model with SentencePiece-1024 greedy decoding, 64K-hour training, Transformers RNNT support with timestamps, and published multi-domain WER tables.
tags: [stt, asr, english, fastconformer, rnnt, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-rnnt-11-card
    resource: ../raw/parakeet-rnnt-1.1b.md
    kind: documentation
    title: Parakeet RNNT 1.1B (en)
---

Parakeet RNNT 1.1B (`nvidia/parakeet-rnnt-1.1b`) is NVIDIA NeMo and Suno.ai's ~1.1B-parameter English offline ASR model that transcribes 16 kHz mono speech into lowercase English text with a FastConformer encoder trained with a Transducer (RNNT) decoder and a SentencePiece Unigram tokenizer, served as a NeMo checkpoint and natively in Transformers from v5.13.0 with timestamp prediction (**Reported**).[^parakeet-rnnt-11-card]

## Identity and lineage

- Hugging Face ID `nvidia/parakeet-rnnt-1.1b`; XXL version of FastConformer Transducer (~1.1B parameters); jointly developed by NVIDIA NeMo and Suno.ai teams (**Reported**).[^parakeet-rnnt-11-card]
- Frontmatter declares `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, language `en`, and tags `Transducer`, `FastConformer`, `Conformer`, `pytorch`, `NeMo`, `hf-asr-leaderboard`, `transformers` (**Observed** by static inspection).[^parakeet-rnnt-11-card]
- License is CC-BY-4.0; downloading the release version accepts those terms (**Reported**).[^parakeet-rnnt-11-card]
- Training stack is the NeMo toolkit over several hundred epochs with the `speech_to_text_rnnt_bpe.py` example script and the `fast-conformer_transducer_bpe.yaml` base config; tokenizers were built from train-set transcripts with `process_asr_text_tokenizer.py` (**Reported**).[^parakeet-rnnt-11-card]

## Architecture

- FastConformer encoder: optimized Conformer with 8x depthwise-separable convolutional downsampling, trained in a multitask setup with a Transducer decoder (RNNT) loss; full details deferred to the NeMo Fast-Conformer documentation (**Reported**).[^parakeet-rnnt-11-card]
- Tokenizer: SentencePiece Unigram, version 1.22.0 row, vocabulary size 1024 (**Reported**).[^parakeet-rnnt-11-card]
- Output constraint: lowercase English alphabet string per audio sample (**Reported**).[^parakeet-rnnt-11-card]

## Training data

- Total: 64K hours of English speech collected and prepared by NVIDIA NeMo and Suno teams — 40K-hour private subset plus 24K hours from public datasets (**Reported**).[^parakeet-rnnt-11-card]
- Named public sources: LibriSpeech 960 hours; Fisher Corpus; Switchboard-1; WSJ-0 and WSJ-1; National Speech Corpus Parts 1 and 6; VCTK; VoxPopuli (EN); Europarl-ASR (EN); Multilingual LibriSpeech MLS EN 2,000-hour subset; Mozilla Common Voice v7.0; People's Speech 12,000-hour subset (**Reported**).[^parakeet-rnnt-11-card]

## Benchmarks (greedy WER without external LM)

All numbers below are source assertions for greedy Transducer decoding without an external language model; scored as WER percent; nothing was executed or reproduced for this wiki (**Synthesis**).[^parakeet-rnnt-11-card]

- Reported WER table, reconciling the body row with the frontmatter `model-index` (which supplies the missing LibriSpeech-other label; see Contradictions) (**Reported**):[^parakeet-rnnt-11-card]

| AMI | Earnings-22 | GigaSpeech | LS test-clean | LS test-other | SPGI Speech | TEDLIUM-v3 | VoxPopuli | Common Voice |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17.10 | 14.11 | 9.96 | 1.46 | 2.47 | 3.11 | 3.92 | 5.39 | 5.79 |

- Frontmatter `model-index` gives per-dataset test splits and configs: AMI Meetings test (`ihm`), Earnings-22 test, GigaSpeech test, LibriSpeech clean and other (`other` config label as printed), SPGI test, TEDLIUM release1, VoxPopuli en, Common Voice 9.0 en, each `args.language: en` (**Observed** by static inspection).[^parakeet-rnnt-11-card]
- Evaluation context: Open ASR Leaderboard sets; card points to the Hugging Face Open ASR Leaderboard for method detail (**Reported**).[^parakeet-rnnt-11-card]

## Inference and usage

- NeMo one-liner: `nemo.collections.asr.models.EncDecRNNTBPEModel.from_pretrained(model_name="nvidia/parakeet-rnnt-1.1b")`, then `asr_model.transcribe(['2086-149220-0033.wav'])` after fetching the sample wav; install is latest PyTorch then `pip install nemo_toolkit['all']` (**Reported**).[^parakeet-rnnt-11-card]
- Transformers paths (requires `transformers>=5.13.0`): `pipeline("automatic-speech-recognition", model="nvidia/parakeet-rnnt-1.1b")` one-shot; `AutoModelForRNNT` plus `AutoProcessor` with `model.generate(..., return_dict_in_generate=True)` for inference; token-level timestamps via `processor.decode(output.sequences, durations=output.durations, skip_special_tokens=True)`; passing `text` to the processor prepares the `labels` key for a training forward/backward pass via `outputs.loss.backward()` (**Reported**).[^parakeet-rnnt-11-card]
- Batch transcription: `python [NEMO_GIT_FOLDER]/examples/asr/transcribe_speech.py pretrained_name="nvidia/parakeet-rnnt-1.1b" audio_dir="<DIRECTORY CONTAINING AUDIO FILES>"` (**Reported**).[^parakeet-rnnt-11-card]

## Input, output, and deployment note

- Input: 16000 Hz mono-channel audio (wav files) (**Reported**).[^parakeet-rnnt-11-card]
- Output: transcribed speech as a string for a given audio sample (**Reported**).[^parakeet-rnnt-11-card]
- NVIDIA Riva: card states this model is not yet supported by Riva, and points to the Riva-supported model list and live demo; Riva is described as an accelerated speech-AI SDK with out-of-the-box checkpoints, runtime word boosting, acoustic/LM/ITN customization, streaming recognition, and Kubernetes scaling (**Reported**).[^parakeet-rnnt-11-card]

## Contradictions

- Benchmark table header lists 8 dataset labels (AMI, Earnings-22, Giga Speech, LS test-clean, SPGI Speech, TEDLIUM-v3, Vox Populi, Common Voice) but prints 9 WER values; the frontmatter `model-index` lists 9 datasets including both LibriSpeech clean (1.46) and other (2.47); this concept follows the frontmatter ordering, treating the body header as missing the LS test-other label — neither the card nor this wiki was independently verified (**Observed** by static inspection).[^parakeet-rnnt-11-card]

## Relationships

- Larger sibling of [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md): same NeMo+Suno FastConformer-Transducer family, 64K-hour data recipe, SentencePiece-1024 greedy setup, and CC-BY-4.0 terms, scaled from ~0.6B to ~1.1B parameters; compare the two WER tables when choosing between the smaller and larger offline RNNT checkpoints (**Synthesis**).[^parakeet-rnnt-11-card]
- Transducer counterpart of [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md): same ~1.1B scale, 64K-hour data recipe, and CC-BY-4.0 terms, differing in decoder (RNNT Transducer here versus CTC there) and in Transformers serving (`AutoModelForRNNT` with duration-based timestamps here versus `AutoModelForCTC` there); the 1.1B CTC card additionally documents a NeMo-Speech.cpp GGUF runtime path absent here; compare the two WER tables when choosing a 1.1B offline checkpoint (**Synthesis**).[^parakeet-rnnt-11-card]
- Shares the offline Parakeet/FastConformer lineage with [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md): that page is the smaller ~0.6B CTC checkpoint, while this page is the larger 1.1B RNNT checkpoint with native Transformers timestamping; read both when choosing between model scale and decoder type (**Synthesis**).[^parakeet-rnnt-11-card]
- Shares the RNNT/FastConformer lineage with [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): that concept covers the streaming overlapped-multitalker model with speaker-kernel injection fronted by streaming diarization, while this page is the offline single-speaker RNNT baseline; read both when choosing between batch transcription and streaming multitalker (**Synthesis**).[^parakeet-rnnt-11-card]
- Contrast streaming operating points and punctuation with [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md): that page's differentiator is cache-aware chunked streaming (80 ms–1.12 s) with native punctuation, versus this page's offline greedy-Transducer lowercase output (**Synthesis**).[^parakeet-rnnt-11-card]
- Compare offline English accuracy with [Canary-1b-v2](canary-1b-v2.md), [Qwen3-ASR family](qwen3-asr-family.md), and [Audio8-ASR-0.1B](audio8-asr-0.1b.md): this page's differentiator in the wiki is the 1.1B RNNT greedy WER table on nine Open ASR Leaderboard sets (**Synthesis**).[^parakeet-rnnt-11-card]

## Coverage and limits

- Source inspected statically only; no NeMo or Transformers install, no checkpoint download, no audio transcribed, and no WER figure reproduced (**Synthesis**).[^parakeet-rnnt-11-card]
- Referenced but unfetched and absent from `raw/`: NeMo documentation and GitHub example/config/tokenizer paths, Transformers and Parakeet RNNT documentation, FastConformer paper [1], SentencePiece [2], NeMo toolkit [3], Suno.ai [4], Open ASR Leaderboard [5], sample wav/MP3 URLs, and widget audio samples; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-rnnt-11-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-rnnt-11-card]

[^parakeet-rnnt-11-card]: [Parakeet RNNT 1.1B (en)](../raw/parakeet-rnnt-1.1b.md) — locators: frontmatter (`library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, `language: en`, `tags`, `license: cc-by-4.0`, `datasets` list, 9-entry `model-index` with AMI 17.10 / Earnings22 14.11 / GigaSpeech 9.96 / LS-clean 1.46 / LS-other 2.47 / SPGI 3.11 / TEDLIUM 3.92 / VoxPopuli 5.39 / CommonVoice 5.79); header badges (FastConformer-Transducer, 1.1B params, en) and intro (NeMo + Suno.ai joint work, XXL FastConformer Transducer ~1.1B, lowercase English); `NVIDIA NeMo: Training` (`pip install nemo_toolkit['all']`); `How to Use` (NeMo `EncDecRNNTBPEModel.from_pretrained` + `transcribe` fences, sample-wav `wget`, Transformers `pip install "transformers>=5.13.0"`, pipeline / `AutoModelForRNNT`+`AutoProcessor` inference, timestamping `decode(..., durations=...)`, and training fences, `transcribe_speech.py` batch fence); `Input` (16000 Hz mono wav) / `Output` (string per sample); `Model Architecture` (8x depthwise-separable downsampling, multitask Transducer/RNNT loss, NeMo docs link); `Training` (several hundred epochs, `speech_to_text_rnnt_bpe.py` + `fast-conformer_transducer_bpe.yaml`, `process_asr_text_tokenizer.py`); `Datasets` (64K-hour total = 40K private + 24K public, 11-item public list with MLS-EN 2k and People Speech 12k subsets); `Performance` (greedy WER without LM, 9-value v1.22.0 / SentencePiece-Unigram-1024 row, leaderboard link); `NVIDIA Riva: Deployment` (not yet supported + supported-list/demo links, Riva capability list); `References [1]–[5]`; `Licence` (CC-BY-4.0).
