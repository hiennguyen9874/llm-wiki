---
type: Concept
title: Parakeet CTC 0.6B
description: NVIDIA NeMo and Suno 600M-parameter English offline FastConformer-CTC ASR model with SentencePiece-1024 greedy decoding, 64K-hour training, and published multi-domain WER tables.
tags: [stt, asr, english, fastconformer, ctc, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-ctc-card
    resource: ../raw/parakeet-ctc-0.6b.md
    kind: documentation
    title: Parakeet CTC 0.6B (en)
---

Parakeet CTC 0.6B (`nvidia/parakeet-ctc-0.6b`) is NVIDIA NeMo and Suno.ai's ~600M-parameter English offline ASR model that transcribes 16 kHz mono speech into lowercase English text with a FastConformer encoder trained under CTC loss and a SentencePiece Unigram tokenizer, served as a NeMo checkpoint and natively in Transformers (**Reported**).[^parakeet-ctc-card]

## Identity and lineage

- Hugging Face ID `nvidia/parakeet-ctc-0.6b`; XL version of FastConformer CTC (~600M parameters); jointly developed by NVIDIA NeMo and Suno.ai teams (**Reported**).[^parakeet-ctc-card]
- Frontmatter declares `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, language `en`, and tags `transformers`, `automatic-speech-recognition`, `speech`, `audio`, `FastConformer`, `Conformer`, `pytorch`, `NeMo`, `hf-asr-leaderboard`, `ctc` (**Observed** by static inspection).[^parakeet-ctc-card]
- License is CC-BY-4.0; downloading the release version accepts those terms (**Reported**).[^parakeet-ctc-card]
- Training stack is the NeMo toolkit over several hundred epochs with the `speech_to_text_ctc_bpe.py` example script and the `fast-conformer_ctc_bpe.yaml` base config; tokenizers were built from train-set transcripts with `process_asr_text_tokenizer.py` (**Reported**).[^parakeet-ctc-card]

## Architecture

- FastConformer encoder: optimized Conformer with 8x depthwise-separable convolutional downsampling, trained with CTC loss; full details deferred to the NeMo Fast-Conformer documentation (**Reported**).[^parakeet-ctc-card]
- Tokenizer: SentencePiece Unigram, version 1.22.0 row, vocabulary size 1024 (**Reported**).[^parakeet-ctc-card]
- Output constraint: lowercase English alphabet string per audio sample (**Reported**).[^parakeet-ctc-card]

## Training data

- Total: 64K hours of English speech collected and prepared by NVIDIA NeMo and Suno teams — 40K-hour private subset plus 24K hours from public datasets (**Reported**).[^parakeet-ctc-card]
- Named public sources: LibriSpeech 960 hours; Fisher Corpus; Switchboard-1; WSJ-0 and WSJ-1; National Speech Corpus Parts 1 and 6; VCTK; VoxPopuli (EN); Europarl-ASR (EN); Multilingual LibriSpeech MLS EN 2,000-hour subset; Mozilla Common Voice v7.0; People's Speech 12,000-hour subset (**Reported**).[^parakeet-ctc-card]

## Benchmarks (greedy WER without external LM)

All numbers below are source assertions for greedy CTC decoding without an external language model; scored as WER percent; nothing was executed or reproduced for this wiki (**Synthesis**).[^parakeet-ctc-card]

- Reported WER table, reconciling the body row with the frontmatter `model-index` (which supplies the missing LibriSpeech-other label; see Contradictions) (**Reported**):[^parakeet-ctc-card]

| AMI | Earnings-22 | GigaSpeech | LS test-clean | LS test-other | SPGI Speech | TEDLIUM-v3 | VoxPopuli | Common Voice |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16.30 | 14.14 | 10.35 | 1.87 | 3.76 | 4.11 | 3.78 | 7.00 | 10.57 |

- Frontmatter `model-index` gives per-dataset test splits and configs: AMI Meetings test (`ihm`), Earnings-22 test, GigaSpeech test, LibriSpeech test (`other` config label as printed), SPGI test, TEDLIUM release1, VoxPopuli en, Common Voice 9.0 en, each `args.language: en` (**Observed** by static inspection).[^parakeet-ctc-card]
- Evaluation context: Open ASR Leaderboard sets; card points to the Hugging Face Open ASR Leaderboard for method detail (**Reported**).[^parakeet-ctc-card]

## Inference and usage

- NeMo one-liner: `nemo.collections.asr.EncDecCTCModelBPE.from_pretrained(model_name="nvidia/parakeet-ctc-0.6b")`, then `asr_model.transcribe(['2086-149220-0033.wav'])` after fetching the sample wav; install is latest PyTorch then `pip install nemo_toolkit['all']` (**Reported**).[^parakeet-ctc-card]
- Transformers paths (install `transformers` from source): `pipeline("automatic-speech-recognition", model="nvidia/parakeet-ctc-0.6b")` one-shot; `AutoModelForCTC` plus `AutoProcessor` with `model.generate` for inference; passing `text` to the processor prepares the `labels` key for a training forward/backward pass via `outputs.loss.backward()` (**Reported**).[^parakeet-ctc-card]
- Batch transcription: `python [NEMO_GIT_FOLDER]/examples/asr/transcribe_speech.py pretrained_name="nvidia/parakeet-ctc-0.6b" audio_dir="<DIRECTORY CONTAINING AUDIO FILES>"` (**Reported**).[^parakeet-ctc-card]

## Input, output, and deployment note

- Input: 16000 Hz mono-channel audio (wav files) (**Reported**).[^parakeet-ctc-card]
- Output: transcribed speech as a string for a given audio sample (**Reported**).[^parakeet-ctc-card]
- NVIDIA Riva: card states this model is not yet supported by Riva, and points to the Riva-supported model list and live demo; Riva is described as an accelerated speech-AI SDK with out-of-the-box checkpoints, runtime word boosting, acoustic/LM/ITN customization, streaming recognition, and Kubernetes scaling (**Reported**).[^parakeet-ctc-card]

## Contradictions

- Benchmark table header lists 8 dataset labels (AMI, Earnings-22, Giga Speech, LS test-clean, SPGI Speech, TEDLIUM-v3, Vox Populi, Common Voice) but prints 9 WER values; the frontmatter `model-index` lists 9 datasets including both LibriSpeech clean (1.87) and other (3.76); this concept follows the frontmatter ordering, treating the body header as missing the LS test-other label — neither the card nor this wiki was independently verified (**Observed** by static inspection).[^parakeet-ctc-card]

## Relationships

- Transducer sibling [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md): same NeMo+Suno ~0.6B FastConformer family, 64K-hour data recipe, SentencePiece-1024 greedy setup, and CC-BY-4.0 terms, differing in decoder (CTC here versus RNNT Transducer there); that page adds `AutoModelForRNNT` serving with duration-based timestamps; compare the two WER tables when choosing a 0.6B offline checkpoint (**Synthesis**).[^parakeet-ctc-card]
- Smaller sibling of [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md): same NeMo+Suno FastConformer-CTC family, 64K-hour data recipe, SentencePiece-1024 greedy setup, and CC-BY-4.0 terms, scaled from ~0.6B to ~1.1B parameters; compare the two WER tables when choosing between the smaller and larger offline checkpoints (**Synthesis**).[^parakeet-ctc-card]
- Shares the offline Parakeet/FastConformer lineage with [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): that concept covers the streaming overlapped-multitalker model with speaker-kernel injection fronted by streaming diarization, while this page is the offline single-speaker CTC baseline; read both when choosing between batch transcription and streaming multitalker (**Synthesis**).[^parakeet-ctc-card]
- Contrast streaming operating points and punctuation with [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md): that page's differentiator is cache-aware chunked streaming (80 ms–1.12 s) with native punctuation, versus this page's offline greedy-CTC lowercase output (**Synthesis**).[^parakeet-ctc-card]
- Compare offline English accuracy with [Canary-1b-v2](canary-1b-v2.md), [Qwen3-ASR family](qwen3-asr-family.md), and [Audio8-ASR-0.1B](audio8-asr-0.1b.md): this page's differentiator in the wiki is the 0.6B CTC greedy WER table on nine Open ASR Leaderboard sets (**Synthesis**).[^parakeet-ctc-card]

## Coverage and limits

- Source inspected statically only; no NeMo or Transformers install, no checkpoint download, no audio transcribed, and no WER figure reproduced (**Synthesis**).[^parakeet-ctc-card]
- Referenced but unfetched and absent from `raw/`: NeMo documentation and GitHub example/config/tokenizer paths, Transformers documentation, FastConformer paper [1], SentencePiece [2], NeMo toolkit [3], Suno.ai [4], Open ASR Leaderboard [5], sample wav/MP3 URLs, and widget audio samples; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-ctc-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-ctc-card]

[^parakeet-ctc-card]: [Parakeet CTC 0.6B (en)](../raw/parakeet-ctc-0.6b.md) — locators: frontmatter (`library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, `language: en`, `tags`, `license: cc-by-4.0`, `datasets` list, 9-entry `model-index` with AMI 16.3 / Earnings22 14.14 / GigaSpeech 10.35 / LS-clean 1.87 / LS-other 3.76 / SPGI 4.11 / TEDLIUM 3.78 / VoxPopuli 7 / CommonVoice 10.57); header badges (FastConformer-CTC, 0.6B params, en) and intro (NeMo + Suno.ai joint work, XL FastConformer CTC ~600M, lowercase English); `NVIDIA NeMo: Training` (`pip install nemo_toolkit['all']`); `How to Use` (NeMo `EncDecCTCModelBPE.from_pretrained` + `transcribe` fences, sample-wav `wget`, Transformers `pip install git+...`, pipeline / `AutoModelForCTC`+`AutoProcessor` inference and training fences, `transcribe_speech.py` batch fence); `Input` (16000 Hz mono wav) / `Output` (string per sample); `Model Architecture` (8x depthwise-separable downsampling, CTC loss, NeMo docs link); `Training` (several hundred epochs, `speech_to_text_ctc_bpe.py` + `fast-conformer_ctc_bpe.yaml`, `process_asr_text_tokenizer.py`); `Datasets` (64K-hour total = 40K private + 24K public, 11-item public list with MLS-EN 2k and People Speech 12k subsets); `Performance` (greedy WER without LM, 9-value v1.22.0 / SentencePiece-Unigram-1024 row, leaderboard link); `NVIDIA Riva: Deployment` (not yet supported + supported-list/demo links, Riva capability list); `References [1]–[5]`; `Licence` (CC-BY-4.0).
