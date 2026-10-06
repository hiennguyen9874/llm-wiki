---
type: Concept
title: Nemotron Speech Streaming EN 0.6B
description: NVIDIA 600M-parameter cache-aware FastConformer-RNNT English streaming ASR model with native punctuation, inference-time 80 ms–1.12 s chunk selection, and published Open ASR Leaderboard WER tables.
tags: [stt, asr, streaming, english, fastconformer, rnnt, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: nemotron-en-stream-card
    resource: ../raw/nemotron-speech-streaming-en-0.6b.md
    kind: documentation
    title: Nemotron ASR Streaming model card
---

Nemotron Speech Streaming EN 0.6B (`nvidia/nemotron-speech-streaming-en-0.6b`) is NVIDIA's 600M-parameter English streaming ASR model built on a cache-aware FastConformer encoder with an RNNT decoder, transcribing speech with native punctuation and capitalization across low-latency streaming and high-throughput batch workloads via inference-time chunk-size selection (**Reported**).[^nemotron-en-stream-card]

## Identity and lineage

- Card title is `Nemotron ASR Streaming`; Hugging Face ID `nvidia/nemotron-speech-streaming-en-0.6b`; 600M parameters; English-only transcription into the English alphabet, spaces, and apostrophes with punctuation and capitalization; ready for commercial and non-commercial use (**Reported**).[^nemotron-en-stream-card]
- Architecture badges and frontmatter declare `FastConformer-CacheAware-RNNT`, `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, and tags including `streaming-asr`, `cache-aware ASR`, `FastConformer`, `RNNT`, `Parakeet`, `NeMo`, and `hf-asr-leaderboard` (**Observed** by static inspection).[^nemotron-en-stream-card]
- License is the NVIDIA Open Model License Agreement; deployment geography is Global; use case is transcription of English audio (**Reported**).[^nemotron-en-stream-card]
- Release history: current checkpoint released 03/13/2026 on Build.NVIDIA, Hugging Face, and NGC; older January-2026 checkpoint (01/05/2026) kept on the `nemotron-speech-streaming-jan2026` branch; March-2026 checkpoint was trained on larger corpora (**Reported**).[^nemotron-en-stream-card]
- Successor note dated 06/04/2026: NVIDIA Nemotron 3.5 ASR Streaming 0.6B extends this English model to 40 language-locales with language-ID conditioning; this English-only checkpoint remains the recommended choice for English-only transcription in that successor card (**Reported**).[^nemotron-en-stream-card]

## Architecture and streaming mechanism

- Network: cache-aware streaming Parakeet (FastConformer) encoder with 24 layers plus an RNN-T decoder; 600M parameters total (**Reported**).[^nemotron-en-stream-card]
- Cache-aware design maintains caches for all encoder self-attention and convolution layers so each streaming step processes only new non-overlapping audio while reusing cached activations and context from previous frames, eliminating the redundant overlapping computation of traditional buffered streaming and improving throughput (more parallel streams per GPU) and end-to-end delay without sacrificing accuracy (**Reported**).[^nemotron-en-stream-card]
- Claimed selection reasons: native streaming architecture for low-latency voice-agent interaction; superior throughput versus buffered streaming (lower operational cost); dynamic runtime latency–accuracy tradeoff with no retraining; built-in punctuation and capitalization (**Reported**).[^nemotron-en-stream-card]
- Intended realtime loop: voice assistants, live captioning, and conversational AI where low latency is critical (**Reported**).[^nemotron-en-stream-card]

## Streaming operating points

- Four runtime chunk sizes, switchable at inference without retraining to move along the latency–accuracy Pareto curve: 80, 160, 560, and 1120 ms (**Reported**).[^nemotron-en-stream-card]
- NeMo `att_context_size` mapping in 80 ms frames with left context 70 (**Reported**):[^nemotron-en-stream-card]

| `att_context_size` | Chunk size | Latency |
| --- | --- | --- |
| [70, 0] | 1 frame | 0.08 s |
| [70, 1] | 2 frames | 0.16 s |
| [70, 6] | 7 frames | 0.56 s |
| [70, 13] | 14 frames | 1.12 s |

- Chunk size equals current frame plus right context; each chunk is processed in strictly non-overlapping fashion (**Reported**).[^nemotron-en-stream-card]
- Card figure (unfetched) claims the cache-aware mechanism scales better than buffered streaming and outperforms `parakeet-ctc-1_1b-asr` across chunk sizes (**Reported**, figure not inspected).[^nemotron-en-stream-card]

## Benchmarks (Open ASR Leaderboard, WER without PnC)

All numbers below are source assertions scored with `whisper-normalizer` 0.1.12 on Hugging Face Open ASR Leaderboard sets; WER in percent; nothing was executed or reproduced for this wiki (**Synthesis**).[^nemotron-en-stream-card]

- Word error rate at 1.12 s chunk (**Reported**):[^nemotron-en-stream-card]

| Avg | AMI | Earnings22 | Gigaspeech | LS-test-clean | LS-test-other | SPGI | TEDLIUM | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6.93 | 11.73 | 12.52 | 9.66 | 2.32 | 4.84 | 2.97 | 3.50 | 7.91 |

- Word error rate at 0.56 s chunk (**Reported**):[^nemotron-en-stream-card]

| Avg | AMI | Earnings22 | Gigaspeech | LS-test-clean | LS-test-other | SPGI | TEDLIUM | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7.07 | 11.88 | 12.82 | 9.78 | 2.46 | 5.07 | 3.03 | 3.54 | 8.00 |

- Word error rate at 0.16 s chunk (**Reported**):[^nemotron-en-stream-card]

| Avg | AMI | Earnings22 | Gigaspeech | LS-test-clean | LS-test-other | SPGI | TEDLIUM | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7.67 | 14.71 | 13.01 | 10.34 | 2.56 | 5.57 | 3.25 | 3.77 | 8.18 |

- Word error rate at 0.08 s chunk (**Reported**):[^nemotron-en-stream-card]

| Avg | AMI | Earnings22 | Gigaspeech | LS-test-clean | LS-test-other | SPGI | TEDLIUM | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8.43 | 18.29 | 13.16 | 11.17 | 2.80 | 6.01 | 3.43 | 4.10 | 8.46 |

- Latency–accuracy reading: average WER degrades from 6.93 at 1.12 s to 8.43 at 80 ms; the steepest low-latency penalty is AMI (11.73 to 18.29), while LibriSpeech test-clean stays under 3.0 across all four points (**Synthesis**).[^nemotron-en-stream-card]
- Frontmatter `model-index` spot values match the 1.12 s row except VoxPopuli (frontmatter 7.97 vs body-table 7.91); see Contradictions (**Observed** by static inspection).[^nemotron-en-stream-card]

## Training and evaluation data

- Base training framing: ASRSet of approximately 250,000 hours of US English (en-US) speech, engineered for diverse acoustic conditions; total audio training size stated as 530k hours; modality audio plus text (**Reported**).[^nemotron-en-stream-card]
- Majority sources: NVIDIA Riva ASR training set (250k hours) plus the English portion of the Granary dataset — YouTube-Commons 109.5k hours, YODAS2 102k hours, Mosel 14k hours, LibriLight 49.5k hours (**Reported**).[^nemotron-en-stream-card]
- Additional datasets: Librispeech 960 hours, Fisher Corpus, Switchboard-1, WSJ-0 and WSJ-1, National Speech Corpus Parts 1 and 6, VCTK, VoxPopuli (EN), Europarl-ASR (EN), Multilingual LibriSpeech (MLS EN), Mozilla Common Voice (v11.0, v7.0, v4.0), People Speech, and AMI (**Reported**).[^nemotron-en-stream-card]
- Collection is Human (all audio human-recorded); labeling is Hybrid Human plus Synthetic (some transcripts manual, some ASR-generated) (**Reported**).[^nemotron-en-stream-card]
- Evaluation sets: AMI, Earnings22, Gigaspeech, LibriSpeech test-clean, LibriSpeech test-other, SPGI Speech, TEDLIUM, and VoxPopuli (**Reported**).[^nemotron-en-stream-card]

## Inference and usage

- NeMo-Speech.cpp local path: download `nemotron-speech-streaming-en-0.6b.q8_0.gguf` into `models/` and run `nemo-speech transcribe audio.wav --model <gguf>`; install and usage details live in the NeMo-Speech.cpp repository (**Reported**).[^nemotron-en-stream-card]
- NeMo path (Cython plus latest PyTorch; `libsndfile1 ffmpeg`; `nemo_toolkit[asr]` from GitHub main): `ASRModel.from_pretrained(model_name="nvidia/nemotron-speech-streaming-en-0.6b")`, then the cache-aware streaming script `examples/asr/asr_cache_aware_streaming/speech_to_text_cache_aware_streaming_infer.py` with `att_context_size` (right-context values 0/1/6/13), batch size, manifest, and output path; an alternate pipeline path builds end-to-end workflows with punctuation/capitalization, inverse text normalization, and translation via `cache_aware_rnnt.yaml` and `PipelineBuilder.build_pipeline(cfg).run(audios)` (**Reported**).[^nemotron-en-stream-card]
- Transformers path (requires `transformers>=5.13.0`, class `AutoModelForRNNT`): `pipeline("automatic-speech-recognition", model=...)` for one-shot use; offline transcription via `AutoProcessor` plus `model.generate`; chunked streaming via `set_num_lookahead_tokens`, per-chunk `is_streaming` / `is_first_audio_chunk` processor calls, `TextIteratorStreamer`, and a generator-threaded `model.generate` loop; full usage is in the Transformers `nemotron_asr_streaming` docs (**Reported**).[^nemotron-en-stream-card]
- Hosted NIM API path (no local GPU or download): get a key on the Build.NVIDIA model page, `pip install nvidia-riva-client`, then `ASRService.offline_recognize` with `language_code="en-US"`, automatic punctuation, and word-time offsets, or the `transcribe_file_offline.py` CLI; streaming and low-latency options are in the model page API reference, which typically accepts 16-bit mono WAV/OGG/OPUS (**Reported**).[^nemotron-en-stream-card]
- Deployment pointers named but not ingested: Modal ASR endpoint recipe, Daily/Pipecat local voice-agent example, Hugging Face demo Space, dev blog on scaling voice agents, and arXiv papers on cache-based streaming inference and FastConformer (**Reported**).[^nemotron-en-stream-card]

## Input, output, and software envelope

- Input: mono audio (`wav`, 1D); maximum length is GPU-memory bound; no preprocessing needed; NVIDIA GPU plus CUDA is faster than CPU-only (**Reported**).[^nemotron-en-stream-card]
- Output: 1D English text string with punctuation and capitalization; no maximum character length (**Reported**).[^nemotron-en-stream-card]
- Runtime: NeMo 25.11, Riva 2.25.0 or higher; microarchitectures Ampere, Blackwell, Hopper, Volta; test hardware V100, A100, A6000, DGX Spark; Linux (**Reported**).[^nemotron-en-stream-card]

## Contradictions

- VoxPopuli 1.12 s WER: frontmatter `model-index` states 7.97 while the body 1.12 s table states 7.91; neither value was chosen — both are recorded as printed, with the frontmatter value visible in the card header metadata and the table value in the performance section (**Observed**).[^nemotron-en-stream-card]

## Relationships

- Extended by [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md): that concept covers the 40-locale multilingual successor that adds language-ID prompt conditioning to this English-only 0.6B base; prefer this page for English-only transcription and the 3.5 page for multilingual coverage (**Synthesis**).[^nemotron-en-stream-card]
- Fine-tuned into [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): that concept covers the overlapped-multitalker model fine-tuned from this English 0.6B streaming base with speaker-kernel injection fronted by streaming diarization; read both when tracing the 0.6B cache-aware lineage from single-speaker to multitalker (**Synthesis**).[^nemotron-en-stream-card]
- Compare streaming English accuracy and operating points with [Canary-1b-v2](canary-1b-v2.md), [Qwen3-ASR family](qwen3-asr-family.md), [Fun-ASR-Nano-2512](fun-asr-nano-2512.md), and [Audio8 ASR Infinite](audio8-asr-infinite.md): this page's differentiator in the wiki is cache-aware chunked streaming with inference-time 80 ms–1.12 s selection and Open ASR Leaderboard WER curves (**Synthesis**).[^nemotron-en-stream-card]

## Coverage and limits

- Source inspected statically only; no NeMo / NeMo-Speech.cpp / Transformers install, no model or GGUF download, no audio transcribed, and no WER, throughput, or latency figure reproduced (**Synthesis**).[^nemotron-en-stream-card]
- Referenced but unfetched and absent from `raw/`: `figures/results_wer_and_scaling.png`, `figures/inference_pipeline.png`, `figures/caching_schema.png`; Hugging Face model page and demo Space, NeMo and NeMo-Speech.cpp repositories, streaming inference script and pipeline YAML, Transformers docs, NVIDIA NIM / NGC / Riva pages, Modal and Daily recipes, dev blog, Granary and all training/evaluation datasets, Parakeet comparator page, and references [1]–[4]; all install and inference fences are transcribed, not executed (**Synthesis**).[^nemotron-en-stream-card]
- The hosted-API credential in the source is a placeholder (`nvapi-YOUR_API_KEY`); no live secret was compiled into this concept (**Synthesis**).[^nemotron-en-stream-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^nemotron-en-stream-card]

[^nemotron-en-stream-card]: [Nemotron ASR Streaming model card](../raw/nemotron-speech-streaming-en-0.6b.md) — locators: frontmatter (`license_name: nvidia-open-model-license`, `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, `datasets` list, `tags`, `model-index` 1.12 s WERs incl. VoxPopuli 7.97); header badges (FastConformer-CacheAware-RNNT, 600M params, English); successor/prior-checkpoint notes (06/04/2026 multilingual pointer, 03/2026 vs 01/2026 checkpoint branches); intro + `Why Choose` (streaming + batch, PnC, 80/160/560/1120 ms chunks, 250k-hour ASRSet, cache-aware reuse and throughput claims, commercial-use line); `Model Architecture` (24 encoder layers, RNNT decoder, self-attention/convolution cache schema, non-overlapping claim); `How to Use` (NeMo-Speech.cpp `hf download` + `nemo-speech transcribe` fence; NeMo install + `from_pretrained` + `speech_to_text_cache_aware_streaming_infer.py` fence with `att_context_size` values; `PipelineBuilder` + `cache_aware_rnnt.yaml` fence; Transformers `>=5.13.0` pipeline/offline/streaming fences with `AutoModelForRNNT`, `set_num_lookahead_tokens`, `TextIteratorStreamer`); `Setting up Streaming Configuration` (4-row `[70, x]` 80 ms-frame table); `Try via API` (`riva.client` `offline_recognize` fence with `en-US`/punctuation/word-offsets, `transcribe_file_offline.py` CLI, WAV/OGG/OPUS note, `nvapi-YOUR_API_KEY` placeholder); `Input(s)`/`Output` (mono wav 1D, GPU-memory max length, punctuated string, CUDA note); `Datasets` (Riva 250k + Granary YTC/YODAS2/Mosel/LibriLight hour counts, 15-item additional list, 530k-hour total, Human/Hybrid labeling); `Performance` (four WER tables 1.12/0.56/0.16/0.08 s incl. VoxPopuli 7.91, `whisper-normalizer` 0.1.12, OpenASR leaderboard link); `Software Integration` (NeMo 25.11, Riva 2.25.0+, 4 microarchitectures, V100/A100/A6000/DGX Spark, Linux); `Release Date`, `License/Terms`, `Deployment Geography`, `Use Case`; `References [1]–[4]`; `Ethical Considerations` (Trustworthy AI + vulnerability link).
