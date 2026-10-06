---
type: Concept
title: TheWhisper-Large-V3-Turbo
description: Fine-tuned Whisper-Large-V3-Turbo variant by TheStage AI with S/M/L/XL latency tiers, Apple CoreML on-device and NVIDIA GPU paths, and published Open ASR WER plus H100/RTX RTFx tables.
tags: [stt, asr, whisper, streaming, multilingual, coreml, nvidia, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T15:00:00Z }
stale_after: 2027-10-06
sources:
  - id: thewhisper-turbo-card
    resource: ../raw/thewhisper-large-v3-turbo.md
    kind: documentation
    title: 'Elastic model: thewhisper-large-v3-turbo'
---

TheWhisper-Large-V3-Turbo by TheStage AI is a fine-tuned, ANNA-compressed variant of OpenAI's `whisper-large-v3-turbo` for real-time low-latency speech-to-text on NVIDIA GPUs and Apple Silicon (CoreML / Neural Engine), shipped in four S/M/L/XL latency tiers with a Transformers-compatible NVIDIA path, a push-based on-device Apple SDK with live partials, and a Docker image exposing an OpenAI-compatible transcription endpoint; its card reports near-parity English Open ASR means (best 5.88 L vs 5.80 original) and 2–3x the original RTFx on H100/L40s/RTX cards (**Reported**).[^thewhisper-turbo-card]

## Identity and lineage

- Base and producer: fine-tune of `openai/whisper-large-v3-turbo` (OpenAI), optimized and packaged by TheStage AI via ANNA (Automated Neural Networks Accelerator); repo published as `TheStageAI/thewhisper-large-v3-turbo` (**Reported**).[^thewhisper-turbo-card]
- License and languages: card frontmatter declares `license: cc-by-4.0`, `pipeline_tag: automatic-speech-recognition`, `library_name: coreml`, and a 28-code language list (en, ar, bg, bn, cs, da, de, el, es, et, fi, fr, hi, hu, id, it, lt, lv, nl, pl, pt, ro, ru, sk, sl, sv, uk, vi); benchmark tables in the body cover English plus DE/ES/FR/IT/PT only, so the remaining frontmatter codes have no card-reported accuracy here (**Reported**, with the coverage gap as a limit).[^thewhisper-turbo-card]
- Upstream links named in the card: [TheWhisper](https://github.com/TheStageAI/TheWhisper/tree/main) repo, TheStage Apple SDK repo, `docs.thestage.ai`, `app.thestage.ai`, and the original `openai/whisper-large-v3-turbo` card — all unfetched in this ingest (**Reported**).[^thewhisper-turbo-card]

## Elastic size tiers

- ANNA routing: per-layer compression controlled by a size/latency/quality slider; four shipped sizes with card-stated degradation bounds against the corresponding benchmarks (**Reported**).[^thewhisper-turbo-card]
- XL: mathematically equivalent network, DNN-compiler optimized; L: near-lossless, under 1% degradation; M: faster, under 1.5%; S: fastest, under 2% (**Reported**).[^thewhisper-turbo-card]
- Selection surface: `mode='S'` in ElasticModels, `model_size='S'` in SpeechKit `ASRPipeline`, `<MODEL_SIZE>` (S/M/L/XL) in the Docker image, and the 10 s-window shipping CoreML bundle on Apple (**Reported**).[^thewhisper-turbo-card]

## System requirements and access

- NVIDIA path: L40s, RTX 4090, RTX 5090, or H100; Python 3.10–3.12; Intel/AMD x86_64 CPU; CUDA 12.8+ (**Reported**).[^thewhisper-turbo-card]
- Apple path (TheStage Apple SDK): Apple Silicon Mac or physical iPhone/iPad; macOS 15.0+, iOS 18.0+, Xcode 16.0+, Swift 6.0+, optional Flutter 3.24+; simulator is explicitly unsupported (**Reported**).[^thewhisper-turbo-card]
- Auth: `pip install thestage` plus `thestage config set --access-token <YOUR_ACCESS_TOKEN>` for Python; `TheStageAI.shared.initialize(apiToken:)` (Swift) or `TheStageFlutterSDK.initialize(api_token:)` (Flutter) with a token from `app.thestage.ai`, checked online once per app process; inference itself runs fully on-device, and offline `initialize` fails until reconnected (**Reported**; placeholder tokens only, no live credential in source).[^thewhisper-turbo-card]

## Apple SDK (on-device)

- Distribution: SwiftPM package `https://github.com/TheStageAI/AppleSDK.git`, pinned `exact: Version(1, 1, 0)` in the card fence; Flutter via `thestage_apple_sdk` git dependency at `ref: 1.1.0`; engines download from this Hugging Face repo with automatic Neural Engine / GPU / CPU selection and no server in the hot path (**Reported**).[^thewhisper-turbo-card]
- Batch inference: `WhisperPipeline(engines_path:)` then `stt.infer(audio:language:)`; long audio splits into the bundle window (10 s for shipping turbo engines; older 15/30 s exports also work); optional `device` (`"npu"`/`"gpu"`/`"cpu"`), `overlap_seconds`, `use_internal_vad` (**Reported**).[^thewhisper-turbo-card]
- Live streaming: `stt.open_streamer(language:)` exposes monotonically growing `partials` for UI plus authoritative `finish()` end-of-turn text; `flush()` at VAD pauses keeps latency flat on long turns and `cancel()` handles barge-in (**Reported**).[^thewhisper-turbo-card]
- Flutter inference returns `transcription` (`String`), `token_count` (`Int`), `decode_seconds` (`Double`), optional `tokens` (`[Int]`) (**Reported**).[^thewhisper-turbo-card]
- Audio contract: 16 kHz mono `Float`/`Float32List` in `[-1.0, 1.0]`; resampling is not automatic — convert mic capture before `infer`/`send` (**Reported**).[^thewhisper-turbo-card]
- Prefetch and progress: `ai.prefetch_engines(repo_id:)` returns the engines dir; `on_load_progress` reports per-model phase and fraction (**Reported**).[^thewhisper-turbo-card]
- Apple latency guidance (not an SLA): release build on Apple M2 Max NPU/ANE, macOS 26.2, short ~2.6 s utterance — RTFx (`audio_seconds / wall_seconds`) 16.7, 233 decode tok/s, ~96 MB process memory; card advises always benching release builds on device (**Reported**).[^thewhisper-turbo-card]

## NVIDIA Python paths

- ElasticModels (Transformers-compatible): `pip install 'thestage-elastic-models[nvidia]'` from the TheStage JFrog extra index; `AutoProcessor.from_pretrained` plus `AutoModelForSpeechSeq2Seq.from_pretrained(..., torch_dtype=torch.float16, mode='S').to("cuda")`; card fence decodes a LibriSpeech dummy clip via `model.generate` (**Reported**, transcribed not executed).[^thewhisper-turbo-card]
- SpeechKit install: `git clone https://github.com/TheStageAI/TheWhisper.git`, `pip install .[nvidia]` (or `.[apple]`), plus `ffmpeg` and, for optimized NVIDIA engines, `thestage-elastic-models[nvidia]` (**Reported**).[^thewhisper-turbo-card]
- SpeechKit NVIDIA: `thestage_speechkit.nvidia.ASRPipeline(model='TheStageAI/thewhisper-large-v3-turbo', model_size='S', chunk_length_s=15, batch_size=32, device='cuda')` with `generate_kwargs={'do_sample': False, 'num_beams': 1, 'use_cache': True}` (**Reported**).[^thewhisper-turbo-card]
- SpeechKit Apple (Python notebooks/macOS scripting; shipping apps should prefer the Apple SDK): `thestage_speechkit.apple.ASRPipeline(..., model_size='S', chunk_length_s=10)` (**Reported**).[^thewhisper-turbo-card]
- SpeechKit streaming: `streaming.StreamingPipeline(..., model_size='S', chunk_length_s=15, platform='apple', language='en')` fed by `MicStream(step_size_s=0.5)` chunks into `StdoutStream`, returning `(approved_text, assumption)` per chunk (**Reported**).[^thewhisper-turbo-card]

## Quality benchmarks

- Protocol: Hugging Face Open ASR Leaderboard methodology; WER is word-level substitutions/insertions/deletions vs reference, lower is better; per-size (S/M/L/XL) columns plus the original model column; all figures vendor-reported without independent verification (**Reported**).[^thewhisper-turbo-card]
- English Open ASR (WER %, lower is better):

| Dataset | S | M | L | XL | Original |
| --- | ---: | ---: | ---: | ---: | ---: |
| LibriSpeech Clean | 1.83 | 1.80 | 1.74 | 1.73 | 1.71 |
| LibriSpeech Other | 3.77 | 3.76 | 3.75 | 3.72 | 3.63 |
| SPGISpeech | 1.92 | 1.93 | 1.92 | 1.88 | 1.88 |
| TED-LIUM | 3.37 | 3.30 | 3.29 | 3.25 | 3.33 |
| VoxPopuli | 7.37 | 6.36 | 6.34 | 6.71 | 6.28 |
| GigaSpeech | 9.56 | 9.54 | 9.53 | 9.48 | 9.51 |
| Earnings-22 | 11.57 | 11.15 | 11.09 | 11.21 | 10.89 |
| AMI | 9.60 | 9.35 | 9.38 | 9.14 | 9.20 |
| Mean WER | 6.12 | 5.90 | 5.88 | 5.89 | 5.80 |

(**Reported**).[^thewhisper-turbo-card]

- Multilingual (WER %): CoVoST2 (DE/ES/FR/IT/PT), FLEURS (DE/ES/FR/IT/PT), MLS (French/German/Italian/Portuguese/Spanish); means S 4.36, M 4.31, L 4.29, XL 4.35 vs original 3.99 — the largest gaps sit in MLS French/Italian/Portuguese/Spanish, where S trails the original by roughly 0.4–0.8 points while CoVoST2 stays within ~0.15 points (**Reported**, gap reading is **Synthesis**).[^thewhisper-turbo-card]
- Full multilingual table as printed:

| Dataset | S | M | L | XL | Original |
| --- | ---: | ---: | ---: | ---: | ---: |
| CoVoST2 DE | 4.47 | 4.44 | 4.38 | 4.32 | 4.34 |
| CoVoST2 ES | 3.41 | 3.40 | 3.35 | 3.33 | 3.30 |
| CoVoST2 FR | 6.09 | 6.09 | 6.01 | 5.95 | 6.01 |
| CoVoST2 IT | 3.81 | 3.66 | 3.64 | 3.74 | 3.71 |
| CoVoST2 PT | 2.08 | 2.02 | 2.00 | 1.97 | 2.02 |
| FLEURS DE | 4.62 | 4.66 | 4.66 | 4.50 | 4.36 |
| FLEURS ES | 3.25 | 3.16 | 3.15 | 3.04 | 2.98 |
| FLEURS FR | 5.18 | 5.15 | 5.27 | 5.25 | 4.99 |
| FLEURS IT | 3.21 | 3.26 | 3.43 | 3.45 | 2.82 |
| FLEURS PT | 4.81 | 4.78 | 4.70 | 4.70 | 4.55 |
| MLS French | 4.67 | 4.54 | 4.48 | 4.31 | 3.77 |
| MLS German | 4.28 | 4.16 | 4.19 | 4.12 | 3.77 |
| MLS Italian | 6.89 | 7.01 | 7.11 | 7.36 | 6.12 |
| MLS Portuguese | 5.69 | 5.53 | 5.34 | 6.30 | 4.56 |
| MLS Spanish | 2.93 | 2.84 | 2.71 | 2.85 | 2.51 |
| Mean WER | 4.36 | 4.31 | 4.29 | 4.35 | 3.99 |

(**Reported**).[^thewhisper-turbo-card]

- Dataset notes compiled from the card: LibriSpeech Clean/Other (read audiobooks, clean vs challenging acoustics), SPGISpeech (earnings calls, financial terms), TED-LIUM (conference talks), VoxPopuli (European Parliament), GigaSpeech (audiobooks/podcasts/YouTube), Earnings-22 (telephone-quality earnings calls), AMI (meeting overlap/distant mics); CoVoST2 (Common Voice-based, 21 languages), FLEURS (102-language Wikipedia read speech), MLS (8-language audiobooks) (**Reported**).[^thewhisper-turbo-card]

## Latency benchmarks

- Definition and method: RTFx = `audio_duration / transcription_time`, higher is better; single-GPU run on a 10-minute 16 kHz mono file with warm-up pass and GPU synchronization around the timed transcription (**Reported**).[^thewhisper-turbo-card]
- RTFx batch size 1 (higher is better):

| GPU | S | M | L | XL | Original |
| --- | ---: | ---: | ---: | ---: | ---: |
| H100 | 304.4 | 304.1 | 295.7 | 285.2 | 109.2 |
| L40s | 247.5 | 239.6 | 239.6 | 221.2 | 81.8 |
| RTX 5090 | 280 | 280 | 280 | 262 | 114 |
| RTX 4090 | 250.3 | 250.3 | 250.3 | 250.3 | 157.6 |

(**Reported**).[^thewhisper-turbo-card]

- RTFx batched (higher is better):

| GPU (batch) | S | M | L | XL | Original |
| --- | ---: | ---: | ---: | ---: | ---: |
| RTX 4090 (bs=24) | 895 | 880 | 871 | 790 | 702 |
| L40s (bs=32) | 989 | 989 | 955 | 926 | 539 |
| RTX 5090 (bs=32) | 1319 | 1302 | 1205 | 1205 | 484 |
| H100 (bs=64) | 2033 | 2022 | 2019 | 2019 | 967 |

(**Reported**).[^thewhisper-turbo-card]

- Reading: at batch 1 the S tier runs roughly 1.6x (4090) to 3x (L40s) the original's RTFx, with S≈M≈L on 4090/5090 and a small S→XL falloff on H100/L40s; batched throughput reaches ~2000 RTFx on H100 at bs=64, about 2.1x the original at the same batch (**Synthesis** from the printed cells).[^thewhisper-turbo-card]

## Serving (Docker) and invocation

- Image: `public.ecr.aws/i3f7g5s7/thestage/elastic-models:0.2.1.post0-stt-streaming-24.09a`, run with `--gpus all`, port `127.0.0.1:80:80`, `$HOME/.cache` mounted at `/opt/project/.cache/`, and env vars `MODEL_REPO`, `MODEL_SIZE` (S/M/L/XL), `MODEL_BATCH`, `PIPELINE_MAX_BATCH_SIZE`, `CHUNK_LENGTH` (e.g. 10/15/20/30 s), `PREPROCESSOR_WORKERS`, `MODEL_INSTANCES`, `PREPROCESSOR_QUEUE_DELAY` / `MODEL_QUEUE_DELAY` / `ENSEMBLE_QUEUE_DELAY` (µs dynamic-batching delays), `HUGGINGFACE_ACCESS_TOKEN`, `THESTAGE_AUTH_TOKEN` (**Reported**).[^thewhisper-turbo-card]
- Endpoint: `POST /v1/audio/transcriptions` with `Authorization: Bearer <token>`, `X-Lang-Id` (e.g. `en`), `X-Model-Name` formatted as `thewhisper-large-v3-turbo-<size>-cl<chunk_length>-bs<batch_size>` (example `thewhisper-large-v3-turbo-s-cl15-bs1`), and multipart `file` audio (**Reported**).[^thewhisper-turbo-card]
- Clients: `elastic-models-client client stt --sample sample.wav --lang-id en`, and an equivalent `curl -F "file=@sample.wav"` fence (**Reported**, transcribed not executed).[^thewhisper-turbo-card]

## Relationships

- Upstream base model: [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) is the OpenAI checkpoint this concept fine-tunes and compresses; consult that page for the canonical 32→4-layer lineage, Transformers usage, long-form rules, and card-level limitations (**Synthesis**).[^thewhisper-turbo-card]
- Alternative Whisper runtime: [Faster-Whisper](faster-whisper.md) serves stock/distilled Whisper via CTranslate2 with batching, quantization, and VAD filtering, while this concept is a fine-tuned weight variant with its own NVIDIA and CoreML serving paths (**Synthesis**).[^thewhisper-turbo-card]
- Alternative Whisper optimization: [Distil-Large-v3.5](distil-large-v3.5.md) distills Whisper-Large-v3 for ~1.46x turbo speed at 7.08% OOD short-form WER, while TheWhisper compresses large-v3-turbo itself and reports 5.88 mean (L) on the 8-set Open ASR split — the two cards use different protocols and should not be ranked against each other without re-evaluation (**Synthesis**).[^thewhisper-turbo-card]
- VAD gating pattern: the Apple SDK's `use_internal_vad` plus streamer `flush()` at pauses mirrors the [Silero VAD](silero-vad.md) frontend practice used by other wiki STT runtimes; consult that page for chunk sizes and thresholds before wiring barge-in (**Synthesis**).[^thewhisper-turbo-card]
- Surveyed in the [ASR/STT Model Survey](asr-stt-model-survey.md) catalog, English ranking, streaming/latency, edge, licensing, and serving comparisons (**Synthesis**).[^thewhisper-turbo-card]

## Coverage and limits

- Source inspected statically only; no weights were downloaded, no Apple or NVIDIA inference was run, and no WER or RTFx figure was reproduced (**Synthesis**).[^thewhisper-turbo-card]
- Referenced but unfetched and absent from `raw/`: the Hugging Face repo files, both GitHub repos (TheWhisper, AppleSDK), `docs.thestage.ai`, `app.thestage.ai`, the Docker/ECR image, the CDN WER/RTFx chart images, and the two GitHub-attachment architecture diagrams at the top of the card; fences and tables above are transcribed, not executed (**Synthesis**).[^thewhisper-turbo-card]
- Card-internal limits carried forward: Elastic degradation bounds (<1/1.5/2%) cite "corresponding benchmarks" without naming them; the Apple M2 Max figures are labeled guidance, not an SLA, on a short 2.6 s utterance; benchmark hardware/CUDA/driver versions and chunk/batch settings for the WER runs are unstated; the English-vs-multilingual size ranking flips (L best on English mean, XL best on several single sets), so size choice needs in-domain validation (**Synthesis**).[^thewhisper-turbo-card]
- All accuracy, speed, and recommendation claims are source assertions without independent verification; benchmark figures and release status carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^thewhisper-turbo-card]

[^thewhisper-turbo-card]: [Elastic model: thewhisper-large-v3-turbo](../raw/thewhisper-large-v3-turbo.md) — locators: frontmatter (`base_model: openai/whisper-large-v3-turbo`, `license: cc-by-4.0`, `pipeline_tag`, `library_name: coreml`, 28-code `language` list); header (TheStage AI fine-tune positioning, NVIDIA + Apple Silicon targets, original-model link); `Overview` (ANNA slider; XL/L/M/S degradation bounds; platform→path table); `System Requirements` (NVIDIA GPU/Python/CPU/CUDA table; Apple hardware/macOS/iOS/Xcode/Swift/Flutter table; simulator note); `Access Token Setup` (`pip install thestage`, `thestage config set`, `initialize(apiToken:)`, online-check/offline-fail notes); `TheStage Apple SDK` (SDK banner; SwiftPM `exact: Version(1, 1, 0)` and Flutter `ref: 1.1.0` fences; batch `infer` fence with 10 s window + `device`/`overlap_seconds`/`use_internal_vad`; `open_streamer` fence with `partials`/`flush()`/`finish()`/`cancel()`; Flutter `start_model`/`infer` fence with JSON keys; audio-contract table; `prefetch_engines`/`on_load_progress` fences; M2 Max RTFx 16.7 / 233 tok-s / ~96 MB table); `ElasticModels` (JFrog `pip install`, `AutoModelForSpeechSeq2Seq ... mode='S'` + LibriSpeech-dummy fence); `TheWhisper SpeechKit` (`apt/brew ffmpeg`, `pip install .[nvidia]/[apple]`, NVIDIA `chunk_length_s=15 batch_size=32` + Apple `chunk_length_s=10` + `StreamingPipeline/MicStream/StdoutStream` fences); `Quality Benchmarks` (Open ASR methodology note; English 9-row × 5-col WER table with Mean row 6.12/5.90/5.88/5.89/5.80; multilingual 16-row × 5-col table with Mean row 4.36/4.31/4.29/4.35/3.99); `Datasets` (8 English + CoVoST2/FLEURS/MLS bullets); `Metrics` (WER definition); `Latency Benchmarks` (RTFx definition; H100/L40s/5090/4090 batch-1 table; RTX-4090-bs24/L40s-bs32/5090-bs32/H100-bs64 batched table); `Benchmarking Methodology` (10-minute 16 kHz mono, warm-up + GPU sync, 7-step algorithm); `Serving with Docker Image` (ECR image tag, `docker pull/run` fence, 11-row env-var table); `Invocation` (CLI + `curl` fences); `Endpoint Parameters` (`POST /v1/audio/transcriptions`, `Authorization`/`X-Lang-Id`/`X-Model-Name` format + example, `file` body); `Acknowledgments` + `Links`.
