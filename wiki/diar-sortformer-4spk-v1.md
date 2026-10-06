---
type: Concept
title: Sortformer Diarizer 4spk v1
description: NVIDIA NeMo offline speaker-diarization model for up to four speakers with arrival-order channels, 123M parameters, NeMo inference, and published DER/RTFx benchmarks.
tags: [vad, diarization, speaker-tagging, sortformer, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T17:00:00Z }
stale_after: 2027-10-06
sources:
  - id: sortformer-4spk-card
    resource: ../raw/diar_sortformer_4spk-v1.md
    kind: documentation
    title: Sortformer Diarizer 4spk v1
---

Sortformer Diarizer 4spk v1 (`nvidia/diar_sortformer_4spk-v1`) is NVIDIA's offline end-to-end neural speaker-diarization model for up to four speakers, resolving permutation by ordering output channels on speaker arrival time (Sortformer) with a 123M-parameter NEST FastConformer plus Transformer stack, NeMo `diarize()` inference over 16 kHz mono audio, and published DER benchmarks with optimized post-processing plus RTX A6000 RTFx figures; the card announces [Nemotron 3 Diarization](nemotron-3-diarization.md) as a newer 8-speaker release with greatly improved accuracy (**Reported**).[^sortformer-4spk-card]

## Identity and release

- Model: Sortformer Diarizer 4spk v1, Hugging Face model card with `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, tags `speaker-diarization`, `speaker-recognition`, `speech`, `audio`, `Transformer`, `FastConformer`, `Conformer`, `NEST`, `pytorch`, `NeMo`; research lineage is the [Sortformer paper](https://arxiv.org/abs/2409.06656) with NEST [2], FastConformer [3], Transformer [4], NeMo [5], and NeMo speech data simulator [6] references (**Reported**).[^sortformer-4spk-card]
- License: CC-BY-NC-4.0; downloading the public release accepts its terms (**Reported**).[^sortformer-4spk-card]
- Successor notice: the card's announcement banner points to [Nemotron-3-Diarization](https://huggingface.co/nvidia/nemotron-3-diarization), supporting 8 speakers with greatly improved accuracy; no deprecation or migration date for this 4-speaker checkpoint is stated (**Reported**).[^sortformer-4spk-card]
- Riva status: this model is not yet supported by NVIDIA Riva; the card links the list of Riva-supported models and the Riva live demo (**Reported**).[^sortformer-4spk-card]

## Architecture and I/O

- Architecture: L-size 18-layer NeMo Encoder for Speech Tasks (NEST) based on FastConformer, followed by an 18-layer Transformer encoder with hidden size 192 and two feedforward layers with 4 sigmoid outputs per input frame; model size badge states 123M parameters (**Reported**).[^sortformer-4spk-card]
- Permutation handling: output speaker channels follow the arrival-time order of each speaker's speech segments, per the Sortformer approach (**Reported**).[^sortformer-4spk-card]
- Input: single-channel (mono) audio sampled at 16,000 Hz; each clip is an Ns × 1 matrix (e.g. 10 s at 16 kHz forms a 160,000 × 1 matrix) (**Reported**).[^sortformer-4spk-card]
- Output: T × S matrix with S = 4 maximum speakers and T frames including zero-padding at one frame per 0.08 s; each element is a speaker-activity probability in [0, 1] (e.g. a(150, 2) = 0.95 means 95% activity for the second speaker over [12.00, 12.08] s) (**Reported**).[^sortformer-4spk-card]

## Inference and usage

- Runtime: NVIDIA NeMo (`apt-get install libsndfile1 ffmpeg`; `pip install Cython packaging`; `pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]`); load via `SortformerEncLabelModel.from_pretrained("nvidia/diar_sortformer_4spk-v1")` (needs a Hugging Face token) or `restore_from()` a downloaded `.nemo` file with `map_location='cuda', strict=False`, then `.eval()` (**Reported**).[^sortformer-4spk-card]
- Accepted inputs: a single audio path, a list of audio paths, or a JSONL manifest where each line carries `audio_filepath`, `offset`, and `duration` (nullable on the NeMo main branch) (**Reported**).[^sortformer-4spk-card]
- Diarization calls: `diarize(audio=audio_input, batch_size=1)` returns speaker-marked segments as `begin_seconds, end_seconds, speaker_index`; `diarize(..., include_tensor_outputs=True)` additionally returns speaker-activity probability tensors (**Reported**).[^sortformer-4spk-card]
- Evaluation path: `examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py` with `model_path`, `manifest_filepath` (with reference RTTMs), `collar`, and `out_rttm_dir` saves RTTMs; per-development-set optimized post-processing is reproduced via YAML configs in `examples/speaker_tasks/diarization/conf/post_processing` with `bypass_postprocessing=False` and `postprocessing_yaml` (**Reported**).[^sortformer-4spk-card]

## Training

- Hardware and regime: trained on 8 nodes of 8× NVIDIA Tesla V100 GPUs with 90-second training samples and batch size 4; train script `sortformer_diar_train.py` and base config `sortformer_diarizer_hybrid_loss_4spk-v1.yaml` are linked (**Reported**).[^sortformer-4spk-card]
- Data scale: 2,030 hours of real conversations plus 5,150 hours of simulated mixtures generated by the NeMo speech data simulator; all listed sets share RTTM labeling, with a processed RTTM subset used for training (**Reported**).[^sortformer-4spk-card]
- Real-conversation training sets: Fisher English (LDC), 2004–2010 NIST Speaker Recognition Evaluation (LDC), Librispeech, AMI Meeting Corpus, VoxConverse v0.3, ICSI, AISHELL-4, Third DIHARD Challenge Development (LDC), 2000 NIST SRE split1 (LDC); collection methods vary (phone calls, interviews, web videos, audiobooks) with LDC/dataset pages as the authority (**Reported**).[^sortformer-4spk-card]
- Mixture-simulation sources: 2004–2010 NIST SRE and Librispeech, mixed with the NeMo simulator (**Reported**).[^sortformer-4spk-card]

## Technical limitations

- Offline (non-streaming) operation only (**Reported**).[^sortformer-4spk-card]
- Maximum 4 speakers; performance degrades on recordings with 5 or more speakers (**Reported**).[^sortformer-4spk-card]
- Maximum test-recording duration depends on GPU memory: around 12 minutes on an RTX A6000 48GB (**Reported**).[^sortformer-4spk-card]
- Trained primarily on public English speech: performance may degrade on non-English speech and on out-of-domain data such as noisy recordings (**Reported**).[^sortformer-4spk-card]

## Benchmarks

- Protocol: all evaluations include overlapping speech; frontmatter `model-index` DER values are the post-processed figures (DIHARD3-eval with 0.0 s collar; CALLHOME splits with 0.25 s collar); the body table separates base from development-set-optimized post-processing (DH3-dev and CallHome-part1 YAMLs) (**Reported**).[^sortformer-4spk-card]

| Dataset | Speakers | Collar | Mean duration |
| --- | --- | --- | ---: |
| DIHARD3-Eval | ≤ 4 | 0.0 s | 453.0 s |
| CALLHOME-part2 | 2 | 0.25 s | 73.0 s |
| CALLHOME-part2 | 3 | 0.25 s | 135.7 s |
| CALLHOME-part2 | 4 | 0.25 s | 329.8 s |
| CH109 (CALLHOME American English, 109 sessions) | 2 | 0.25 s | 552.9 s |

Table values are the card's evaluation-specification table (**Reported**).[^sortformer-4spk-card]

| DER condition | DIHARD3-Eval | CALLHOME 2spk | CALLHOME 3spk | CALLHOME 4spk | CH109 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base `diar_sortformer_4spk-v1` | 16.28 | 6.49 | 10.01 | 14.14 | 6.27 |
| + DH3-dev optimized PP | 14.76 | — | — | — | — |
| + CallHome-part1 optimized PP | — | 5.85 | 8.46 | 12.59 | 6.86 |

Table values are the card's DER table; bold/italic in the source marks the best Sortformer evaluation per column (**Reported**).[^sortformer-4spk-card]

- Speed (RTFx, higher is faster): measured on RTX A6000 48GB with batch size 1, excluding post-processing — DIHARD3-Eval 437, CALLHOME-part2 2spk 1053, 3spk 915, 4spk 545, CH109 415 (**Reported**).[^sortformer-4spk-card]

## Relationships

- Succeeded by [Nemotron 3 Diarization](nemotron-3-diarization.md): the newer checkpoint supports up to eight speakers with greatly improved accuracy per this card's announcement banner, while this concept covers the 123M-parameter offline 4-speaker Sortformer checkpoint with its own DER/RTFx tables; neither page deprecates the other (**Synthesis**).[^sortformer-4spk-card]
- Related to [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md): the 117M-parameter streaming Sortformer variant that follows this offline architecture aside from AOSC/FIFO speaker-cache management, with its own latency profiles and v2-vs-v2.1 DER tables (**Synthesis**).[^sortformer-4spk-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, inference, training, evaluation script, or DER/RTFx figure was executed or reproduced (**Synthesis**).[^sortformer-4spk-card]
- Embedded images (`sortformer_intro.png`, `sortformer-v1-model.png`), linked NeMo scripts/configs/post-processing YAMLs, arXiv references [1]–[6], LDC/dataset pages, Riva pages, and the successor Hugging Face page were not fetched; Librispeech sample widget audio was not played (**Synthesis**).[^sortformer-4spk-card]
- All architecture, data-composition, procedure, benchmark, speed, compatibility, and licensing characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^sortformer-4spk-card]

[^sortformer-4spk-card]: [Sortformer Diarizer 4spk v1](../raw/diar_sortformer_4spk-v1.md) — locators: frontmatter (`license`, `library_name`, `pipeline_tag`, `tags`, `datasets`, `model-index` with 5 DER results plus task/dataset/config/split/metric keys); announcement banner (Nemotron-3-Diarization 8-speaker link); sections `Model Architecture` (NEST L-size 18-layer FastConformer basis, 18-layer 192-hidden Transformer, 2 feedforward layers with 4 sigmoid outputs, 123M badge, intro permutation paragraph); `NVIDIA NeMo` (install fence); `How to Use this Model` (`from_pretrained` / `restore_from` / `eval` fence, single-file / list / manifest `audio_filepath+offset+duration` code blocks, `diarize` and `include_tensor_outputs` fences, `Input` 16 kHz mono Ns×1 paragraph with 160,000×1 example, `Output` T×S / S=4 / 0.08 s-frame / [0,1] paragraph with a(150,2) example); `Train and evaluate` (8×8 V100, 90 s samples, batch size 4, train script + `sortformer_diarizer_hybrid_loss_4spk-v1.yaml` links, `e2e_diarize_speech.py` plain and post-processing fences with `collar`/`out_rttm_dir`/`bypass_postprocessing`/`postprocessing_yaml`, DH3-dev and CallHome-part1 YAML links, `Technical Limitations` 4 bullets incl. RTX A6000 48GB ~12 min); `Datasets` (2030 h real + 5150 h simulated via NeMo simulator, RTTM labeling, 9-item real list, 2-item simulation list, phone/interview/web-video/audiobook + LDC note); `Performance` (spec table with speaker/collar/mean-duration rows, DER table with base + DH3-dev PP + CallHome-part1 PP rows and overlap-included/best-marked/PP-optimized notes, RTFx table with RTX A6000 bs=1 no-PP note); `NVIDIA Riva: Deployment` (not-yet-supported + model-list/demo links); `References` ([1]–[6]); `Licence` (CC-BY-NC-4.0). Referenced PNG figures have no locator available in `raw/` (files absent).
