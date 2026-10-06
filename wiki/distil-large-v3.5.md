---
type: Concept
title: Distil-Large-v3.5
description: 756M-parameter English distilled Whisper-Large-v3 checkpoint reporting 7.08% OOD short-form WER at 1.46x large-v3-turbo speed, with sequential and chunked long-form, speculative-decoding, and CTranslate2, whisper.cpp, and OpenAI-format runtimes.
tags: [stt, asr, whisper, distillation, english, transformers, speculative-decoding, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:10:00Z }
stale_after: 2027-10-06
sources:
  - id: distil-large-v3.5-card
    resource: ../raw/distil-large-v3.5.md
    kind: documentation
    title: Distil-Whisper Distil-Large-v3.5 model card
---

Distil-Large-v3.5 by the Distil-Whisper collaboration (Bofeng Huang, Eustache Le Bihan, Steven Zheng, Vaibhav Srivastav) is a 756M-parameter English-only knowledge distillation of OpenAI's Whisper-Large-v3 under an MIT license, positioned as a drop-in replacement that runs about 1.5x faster than Whisper-Large-v3-Turbo, scores slightly better on short-form transcription (7.08% versus 7.30% OOD WER), trails by about 1 point on long-form (11.39% versus 10.25% OOD WER), and doubles as a speculative-decoding draft model that reproduces Whisper-Large-v3 outputs identically at about 2x speed (**Reported**).[^distil-large-v3.5-card]

## Identity and lineage

- Teacher and family: distilled from `openai/whisper-large-v3` following the Distil-Whisper paper (Robust Knowledge Distillation via Large-Scale Pseudo Labelling); newest addition to the English Distil-Whisper family after `distil-large-v3`, keeping the same 756M size against 809M for `large-v3-turbo` (**Reported**).[^distil-large-v3.5-card]
- Training recipe changes over predecessors: trained on 4x more diverse public data (98k hours), a "patient" teacher with an extended 80-epoch schedule (versus 11 previously), aggressive SpecAugment augmentation, a larger 4,096-packed-segment batch (versus 256) with a linear scheduler retained after cosine, wsd, and scheduler-free alternatives tested worse, previous-prompt appending probability cut from 50% to 20% after the small decoder struggled with prompted context, revised segment packing order, and BPE-dropout regularization that slightly hurts short-form but helps long-form (**Reported**).[^distil-large-v3.5-card]
- Compute: 64 H100 GPUs on the Jean Zay cluster for three days; TensorBoard logs linked from the card (**Reported**).[^distil-large-v3.5-card]
- License and citation: inherits the MIT license from Whisper; the card asks users to cite the Distil-Whisper paper (Gandhi, von Platen, Rush 2023, arXiv:2311.00430) (**Reported**).[^distil-large-v3.5-card]

## Training data

- Started from over 196,000 public hours (Common Voice, LibriSpeech, VoxPopuli, TED-LIUM, People's Speech, GigaSpeech, AMI, and notably Yodas YouTube content), packed into roughly 30-second single-speaker segments (**Reported**).[^distil-large-v3.5-card]
- Pseudo-labelled with Whisper-Large-v3, normalized both pseudo and ground-truth labels, and discarded segments above 10% WER between them, leaving about 98,000 high-quality hours; the filtered multilingual set is published for reproduction (**Reported**).[^distil-large-v3.5-card]

## Benchmarks

- Protocol: post-normalization WER (lowercasing, symbol/punctuation stripping); short-form follows the Open ASR Leaderboard split convention and long-form uses sequential decoding with `condition_on_prev_tokens=False`; ID/OOD labels are relative to distil-v3/v3.5 training data and may not reflect the true in/out-of-domain status of large-v3 and large-v3-turbo, whose training corpora are unknown (**Reported**).[^distil-large-v3.5-card]
- Short-form (5 ID + Earnings22/SPGISpeech OOD sets): overall average 7.10% (ID 7.10, OOD 7.08), the best of the four compared checkpoints on every average against large-v3 (7.14), large-v3-turbo (7.25), and distil-v3 (7.41); per-set wins include AMI 14.63, Gigaspeech 9.84, Tedlium 3.64, Earnings22 11.29, and SPGISpeech 2.87 (**Reported**).[^distil-large-v3.5-card]
- Long-form (tedlium-long-form ID + meanwhile/earnings21/earnings22/rev16 OOD): OOD average 11.39% versus 10.25% for large-v3-turbo and 11.6% for distil-v3; ID tedlium-long-form regresses to 4.63% from distil-v3's 3.9% (**Reported**).[^distil-large-v3.5-card]
- Speed: average RTFx 49.34 versus 33.81 for large-v3-turbo (relative 1.46x), 48.64 for distil-v3, and 31.72 for distil-v2 across the five long-form sets (**Reported**).[^distil-large-v3.5-card]

## Transformers usage

- Requires Transformers 4.39 or newer with `transformers`, `accelerate`, and `datasets[audio]`; standard `AutoModelForSpeechSeq2Seq` plus `AutoProcessor` short-form pattern with `max_new_tokens=128` and optional `return_timestamps=True` chunks (**Reported**).[^distil-large-v3.5-card]
- Sequential long-form (sliding-window buffered inference, up to ~0.5% WER more accurate): recommended when accuracy matters most or when batching long files, where its latency is comparable to chunked (**Reported**).[^distil-large-v3.5-card]
- Chunked long-form: fastest path for single large files (up to 9x faster than sequential per the paper), enabled with `chunk_length_s=25` (optimal for this checkpoint) plus `batch_size` for batching (**Reported**).[^distil-large-v3.5-card]
- Speculative decoding: load the checkpoint as the assistant model alongside `openai/whisper-large-v3` via `generate_kwargs={"assistant_model": assistant_model}`; the encoder stays frozen so only two extra decoder layers load and the encoder runs once, giving ~2x faster inference with mathematically identical outputs (**Reported**).[^distil-large-v3.5-card]
- Attention and precision: Flash-Attention 2 via `attn_implementation="flash_attention_2"` where the GPU allows; PyTorch SDPA is default on torch 2.1.1+ and settable via `attn_implementation="sdpa"`; torch-compile and 4/8-bit inference sections are marked "Coming soon" (**Reported**).[^distil-large-v3.5-card]

## Runtimes and integrations

- whisper.cpp: GGML weights (`distil-whisper/distil-large-v3.5-ggml`, `ggml-model.bin`) run with the original sequential long-form algorithm via `./main -m ./models/ggml-model.bin -l en` (**Reported**).[^distil-large-v3.5-card]
- [Faster-Whisper](faster-whisper.md): CTranslate2 checkpoint `distil-whisper/distil-large-v3.5-ct2` transcribed with `beam_size=5, language="en"` (**Reported**).[^distil-large-v3.5-card]
- OpenAI Whisper format: `distil-whisper/distil-large-v3.5-openai` weights loaded through `whisper.load_model`, plus CLI usage deferred to that repo's card (**Reported**).[^distil-large-v3.5-card]
- Candle (Rust): integration claimed with CPU/Metal/CUDA/WASM backends, but the card's run fences name `--model distil-large-v3`, not v3.5, so v3.5 availability through Candle is unconfirmed in this source (**Reported**, with the flag mismatch as a limit).[^distil-large-v3.5-card]

## Relationships

- Distilled from [Whisper Large v3](whisper-large-v3.md): teacher for pseudo-labels and the speculative-decoding target whose outputs the draft setup reproduces exactly (**Synthesis**).[^distil-large-v3.5-card]
- Supersedes `distil-large-v3` in the card's positioning (better short-form at the same size and speed, trained on 4x data): no concept page exists for the predecessor, so no deprecated page is marked here (**Synthesis**).[^distil-large-v3.5-card]
- Compared with [Whisper Large v3 Turbo](whisper-large-v3-turbo.md): the speed-vs-accuracy alternative the card argues against, ~1.5x slower but ~1 point better on long-form OOD (**Synthesis**).[^distil-large-v3.5-card]
- Served by [Faster-Whisper](faster-whisper.md): that runtime's CTranslate2 engine is one of the card's documented inference paths; consult that page for batched inference, quantization, and VAD filtering (**Synthesis**).[^distil-large-v3.5-card]

## Coverage and limits

- Source inspected statically only; no weights were downloaded, no transcription, speculative-decoding, or benchmark run was executed, and no WER or RTFx figure was reproduced (**Synthesis**).[^distil-large-v3.5-card]
- Referenced but unfetched and absent from `raw/`: the teacher and turbo weights, the Distil-Whisper paper and training/evaluation code, the Yodas/Common Voice/LibriSpeech/VoxPopuli/TED-LIUM/People's Speech/GigaSpeech/AMI sources, the filtered pseudo-labelled dataset, TensorBoard logs, the GGML/CT2/OpenAI-format weight repos, and all runtime repositories (Transformers, whisper.cpp, faster-whisper, openai-whisper, Candle); every command fence above is transcribed, not executed (**Synthesis**).[^distil-large-v3.5-card]
- Transformers.js appears in the card's table of contents but has no corresponding section, so no Transformers.js usage is compiled here; Candle fences name the older checkpoint as noted above (**Synthesis**).[^distil-large-v3.5-card]
- All accuracy, speed, and recommendation claims are source assertions without independent verification; benchmark figures and release status carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^distil-large-v3.5-card]

[^distil-large-v3.5-card]: [Distil-Whisper Distil-Large-v3.5 model card](../raw/distil-large-v3.5.md) — locators: header (756M params, 1.46 rel. RTFx, 7.08 short-form / 11.39 long-form OOD WER comparison table; ~1.5x-faster and speculative-decoding rationale; author list; Transformers ≥4.39 note); `Performance` (post-normalization WER note; short-form 7-set table with ID/OOD averages; long-form 5-set WER and RTFx tables; ID/OOD caveat notes); `Transformers Usage` (install fence; short-form, sequential long-form, chunked long-form with `chunk_length_s=25`, and speculative-decoding fences; Flash-Attention 2 / SDPA / torch-compile / 4-8-bit notes); `Library Integrations` (whisper.cpp GGML fences; Faster-Whisper `distil-large-v3.5-ct2` fence; OpenAI-format `model.bin` fence; Candle fences naming `distil-large-v3`); `Training` (encoder-decoder latency rationale; 22k→98k hours, Yodas, patient teacher, SpecAugment, 80 epochs, 4,096 batch, linear scheduler, 50%→20% prompt probability, BPE dropout, 64×H100 / 3-day / Jean Zay, TensorBoard link; 196k-hour source list, 30 s single-speaker packing, 10% WER filter, filtered-dataset link, training-code link); `License` (MIT); `Citation` (arXiv:2311.00430); `Acknowledgements`.
