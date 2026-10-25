---
type: Concept
title: Pyannote Speaker Diarization Community-1
description: Open gated pyannote pipeline that diarizes 16 kHz mono audio, adds an exclusive speaker track for transcript reconciliation, and supports GPU, offline, and speaker-count control without any streaming mode.
tags: [vad, diarization, pyannote, speaker-turns, offline]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:16:00Z }
stale_after: 2027-10-25
sources:
  - id: pyannote-community-1-card
    resource: ../raw/pyannote-speaker-diarization-community-1.md
    kind: documentation
    title: pyannote/speaker-diarization-community-1 model card
---

`pyannote/speaker-diarization-community-1` is pyannote's open speaker-diarization pipeline: it takes mono 16 kHz audio and returns speaker turns, plus a second *exclusive* track that assigns each region to a single speaker so fine-grained diarization timestamps can be reconciled with (often imprecise) ASR word timestamps. The card positions it as the free successor to `speaker-diarization-3.1`, one step behind the commercial `precision-2` model, and documents packaging, GPU/offline operation, and speaker-count controls but no streaming path, latency, model size, or training data (**Reported**).[^pyannote-community-1-card]

## Identity and access

- Pipeline id `pyannote/speaker-diarization-community-1`, loaded with `pyannote.audio.Pipeline.from_pretrained`; frontmatter declares `license: cc-by-4.0` with a gated access prompt stating the pipeline "will always remain freely accessible" (**Reported**).[^pyannote-community-1-card]
- Access is gated: accept the model conditions, create a Hugging Face access token, then pass it as `token="{huggingface-token}"` (**Reported**).[^pyannote-community-1-card]
- The card claims four improvements over `speaker-diarization-3.1`: better speaker assignment and counting, simpler reconciliation with transcription timestamps via exclusive diarization, easy offline use, and an optional hosted deployment on pyannoteAI cloud (`pyannote/speaker-diarization-community-1-cloud`) (**Reported**).[^pyannote-community-1-card]
- Components named in the citations are powerset multi-class cross-entropy speaker segmentation (Plaquet and Bredin, INTERSPEECH 2023), WeSpeaker speaker embeddings (Wang et al., ICASSP 2023), and VBx Bayesian-HMM clustering of x-vectors (Landini et al., Computer Speech and Language 2022); tuning credits GENCI's Jean Zay supercomputer (**Reported**).[^pyannote-community-1-card]
- Card frontmatter also tags `voice-activity-detection`, `overlapped-speech-detection`, and `automatic-speech-recognition`, but the body documents only diarization; no VAD, overlap-detection, or ASR API is described (**Reported**; tag-scope reading **Synthesis**).[^pyannote-community-1-card]
- No revision, release date, capture date, parameter count, checkpoint inventory, or training-data description appears in the capture (**Synthesis**).[^pyannote-community-1-card]

## Audio contract and output

- Input is mono 16 kHz audio; stereo or multichannel files are downmixed by averaging channels, and other sample rates are resampled to 16 kHz automatically at load (**Reported**).[^pyannote-community-1-card]
- Output carries `speaker_diarization`, iterated as `(turn, speaker)` pairs with `turn.start`/`turn.end` in seconds, and `exclusive_speaker_diarization` (**Reported**).[^pyannote-community-1-card]
- Minimum or maximum input duration, internal chunking, maximum speaker count, and peak memory are all unstated (**Synthesis**).[^pyannote-community-1-card]

## Runtime options

| Option | Card's documented form (**Reported**)[^pyannote-community-1-card] |
| --- | --- |
| Device | CPU by default; `pipeline.to(torch.device("cuda"))` moves it to GPU |
| In-memory audio | `torchaudio.load(...)` then `pipeline({"waveform": waveform, "sample_rate": sample_rate})`, described as possibly faster |
| Progress | `with ProgressHook() as hook: pipeline(..., hook=hook)` |
| Speaker count | `num_speakers=2`, or bounds `min_speakers=2, max_speakers=5` |
| Offline | `git clone https://hf.co/pyannote/speaker-diarization-community-1 <dir>` with git-lfs and a write token, then `from_pretrained('/path/to/dir')` with no internet |

- The card gives no guidance on how the automatic speaker count is estimated, what happens when the true count falls outside `min_speakers`/`max_speakers`, or how `num_speakers` interacts with the exclusive track (**Synthesis**).[^pyannote-community-1-card]
- Only whole-file batch processing is documented. No streaming, incremental or partial output, real-time factor, algorithmic latency, VRAM, or throughput figure appears in the card (**Synthesis**).[^pyannote-community-1-card]

## Exclusive speaker diarization

- Community-1 returns an *exclusive* diarization alongside the regular one, exposed as `output.exclusive_speaker_diarization`; the card calls it a feature backported from the commercial `precision-2` model and describes its purpose as simplifying reconciliation between fine-grained diarization timestamps and sometimes-imprecise transcription timestamps (**Reported**).[^pyannote-community-1-card]
- What the exclusive track does with overlapped speech, hesitations, or silence, how it is computed, and how its accuracy is scored are not documented; the benchmark table scores regular diarization only (**Synthesis**).[^pyannote-community-1-card]

## Accuracy

The card's twelve-benchmark DER comparison against `speaker-diarization-3.1` and `precision-2` is compiled in [Pyannote Community-1 Diarization Benchmarks](pyannote-community-1-benchmarks.md): Community-1 improves on ten of twelve benchmarks by 4–17 % relative, ties on VoxConverse, and is worse on REPERE, while `precision-2` is better on all twelve (**Observed**, from the card's table).[^pyannote-community-1-card]

## Fit in a voice pipeline

- The pipeline is an offline batch diarizer: no streaming output, no latency figure, and a file/array API. It therefore fits asynchronous or post-call speaker attribution and offline transcript enrichment rather than per-turn barge-in or endpointing decisions (**Synthesis**).[^pyannote-community-1-card]
- Its natural join point with the rest of the loop is the exclusive track plus ASR word timestamps, which is also the input shape that LLM speaker-turn post-processors expect; see [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md) and [DiarizationLM Toolkit](diarizationlm-toolkit.md) (**Synthesis**).[^pyannote-community-1-card]
- Downstream packaging exists in this wiki for three runtimes: Core ML for Apple ([Speaker Diarization Core ML](speaker-diarization-coreml.md)), ONNX inside [Sherpa Vietnamese ASR](sherpa-vietnamese-asr.md), and a native GGUF backend in [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) (**Synthesis**).

## Relationships

- Upstream of [Speaker Diarization Core ML](speaker-diarization-coreml.md): FluidInference converts this pipeline's segmentation and embedding checkpoints to Core ML for FluidAudio; that concept covers the conversion artifacts, provenance pins, and Apple deployment targets, while this concept covers the upstream pipeline's contract and controls (**Synthesis**).[^pyannote-community-1-card]
- Packaged by [Sherpa Vietnamese ASR](sherpa-vietnamese-asr.md) as pure ONNX Runtime diarization and by [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) as a native GGUF backend with selectable embedders; neither packaging documents which Community-1 checkpoint or hyperparameters it reproduces (**Synthesis**).[^pyannote-community-1-card]
- Alternative to [Nemotron 3 Diarization](nemotron-3-diarization.md), [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md), and the [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md) family: those publish streaming latency profiles and explicit 4- or 8-speaker limits with DER/RTFx or SCA/MAE tables, while Community-1 documents an offline file API with no latency or speaker ceiling (**Synthesis**).[^pyannote-community-1-card]
- Complemented by [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md): that concept is an LLM that rewrites speaker turns in an already-tagged transcript, where this pipeline produces the tags; exclusive diarization is the pre-LLM mechanism for the same reconciliation problem (**Synthesis**).[^pyannote-community-1-card]
- Named as the community's default diarizer in [Community-Reported Open STT and Realtime Diarization Selection](community-open-stt-diarization.md), which treats pyannote (with diart or WhisperX) as the open standard and live diarization as weaker than batch; this concept is the primary-source card for that pipeline (**Synthesis**).[^pyannote-community-1-card]

## Contradictions

- "Much better than `speaker-diarization-3.1`" versus the card's own table: the table shows one regression (REPERE 8.9 versus 7.9) and one tie (VoxConverse 11.2 versus 11.2). Both statements are reported without choosing between them; see [Pyannote Community-1 Diarization Benchmarks](pyannote-community-1-benchmarks.md) (**Reported**).[^pyannote-community-1-card]

## Coverage and limits

- Single capture (227 lines) read in full and inspected statically. The gated-prompt text and its `extra_gated_fields` form are excluded as access boilerplate (**Synthesis**).[^pyannote-community-1-card]
- No pipeline was installed, downloaded, or run; no audio was diarized; no DER, speaker-count, GPU-speed, or offline-install claim was reproduced (**Synthesis**).[^pyannote-community-1-card]
- Uninspected: checkpoint weights and any `config.yaml`/hyperparameters, the linked `community-1` and `precision-2` blog posts, the pyannoteAI dashboard and cloud pipeline, the Hugging Face token page, and the three cited papers (**Synthesis**).[^pyannote-community-1-card]
- The license is known only from the frontmatter `cc-by-4.0` field; whether the gated terms add obligations beyond CC-BY-4.0 was not read (**Synthesis**).[^pyannote-community-1-card]
- All quality, runtime, licensing, and packaging statements are **Reported**; table arithmetic and derived comparisons are **Observed**. Model-release figures carry `stale_after: 2027-10-25` per the `vad` domain rule.

[^pyannote-community-1-card]: [pyannote/speaker-diarization-community-1 model card](../raw/pyannote-speaker-diarization-community-1.md) — locators: frontmatter (`license: cc-by-4.0`, `extra_gated_prompt`, `extra_gated_fields`, tag list); `# community-1 speaker diarization` intro (16 kHz mono input, channel averaging, resampling, four improvement bullets, cloud link); `## Setup`; `## Quick start` fence (`Pipeline.from_pretrained`, `token=`, `output.speaker_diarization` loop); `## Benchmark` table and preamble; `## Processing on GPU`; `## Processing from memory`; `## Monitoring progress`; `## Controlling the number of speakers` (`num_speakers`, `min_speakers`, `max_speakers`); `## Exclusive speaker diarization`; `## Offline use` (`git lfs install`, `git clone https://hf.co/pyannote/speaker-diarization-community-1`, local `from_pretrained`); `## Citations` (Plaquet23, Wang2023, Landini2022); `## Acknowledgment` (GENCI, Jean Zay). No revision, release date, or capture date in the file.
