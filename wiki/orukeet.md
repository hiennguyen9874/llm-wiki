---
type: Concept
title: Orukeet
description: 25-language Parakeet TDT 0.6B V3 finetune with 12,288 frozen Gabor kernels, reporting 9.85% pooled FLEURS WER with NeMo, ONNX, GGUF, and Core ML runtimes.
tags: [stt, asr, multilingual, fastconformer, tdt, parakeet-derivative, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T23:30:00Z }
stale_after: 2027-10-06
sources:
  - id: orukeet-card
    resource: ../raw/orukeet.md
    kind: documentation
    title: Orukeet model card
  - id: parakeet-redux-card
    resource: ../raw/parakeet-redux.md
    kind: documentation
    title: Moondream Parakeet Redux model card
---

Orukeet (`oruk/orukeet`) is Oruk AI's 25-language finetune of NVIDIA's `parakeet-tdt-0.6b-v3` that freezes half of the encoder's temporal depthwise filters as fitted Gabor kernels and retrains the rest, reporting lower WER than its teacher on 61 of 74 tested splits with NeMo, Transformers, sherpa-onnx INT8, native Q8/F16, transcribe.cpp, and Core ML runtimes derived from one r3 checkpoint (**Reported**).[^orukeet-card]

## Identity and lineage

- Model name Orukeet v0.1.0 (native package v0.1.1, weight filenames retain v0.1.0 names); team Nathan Roll, Irene Yi, Büşra Marşan, Vianney Grenez, Gabriel Stein, Momcilo Mrkaic, Pavle Padjin, Vladimir Zeljkovic, Calbert Graham across Oruk AI, Stanford, Cambridge, OpenWhispr, and Hoid; citation `roll2026orukeet`, arXiv `2609.10054` (**Reported**).[^orukeet-card]
- Frontmatter declares `base_model: nvidia/parakeet-tdt-0.6b-v3` with `base_model_relation: finetune`, `pipeline_tag: automatic-speech-recognition`, `library_name: nemo`, the same 25 European language codes as the teacher (bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu, it, lv, lt, mt, pl, pt, ro, ru, sk, sl, es, sv, uk), and `transcribe_cpp` flags (`streaming: false`, `translate: false`, `lang_detect: true`, `timestamps: token`) (**Observed** by static inspection).[^orukeet-card]
- License: code MIT; weights and fitted kernels CC BY-SA 4.0 retaining NVIDIA foundation attribution; transcript-free metric records CC BY 4.0; dataset audio under original provider terms (**Reported**).[^orukeet-card]
- Intended use: recordings, media, batch transcription, server workers, and interactive applications (**Reported**).[^orukeet-card]

## Architecture

- Retains the teacher's 627,008,134 parameters, 24-layer FastConformer encoder, token-and-duration transducer, and tokenizer; each encoder block holds 1,024 nine-tap temporal depthwise filters (**Reported**).[^orukeet-card]
- Each selected filter stores its own fitted Gabor function `g(t)=A·exp(−(t−μ)²/2σ²)·cos(2πf(t−μ)+φ)` for `t=−4…4`; all 24,576 filters were fitted and the 12,288 lowest normalized squared errors kept globally, selecting 175–748 kernels per layer at 6.32% median relative RMS error and a 13.30% cutoff (**Reported**).[^orukeet-card]
- The 110,592 selected taps stay fixed; 626,897,542 scalar parameters remain trainable; native exports materialize the fitted taps as ordinary F16 convolution weights so no Gabor-specific runtime is needed (**Reported**).[^orukeet-card]

## Construction

- Gabor recovery uses transducer loss, encoder matching, and token/duration distillation; a further 4,035 low-learning-rate updates produce the parent checkpoint (**Reported**).[^orukeet-card]
- Final r3 pass applies 168 AdamW updates with 3% warmup and cosine decay from `5e-6` to `5e-7` over three passes through 2,939 LibriSpeech test-other recordings; targets preserve native casing and punctuation while correcting reference words; the same split supplies checkpoint selection (**Reported**).[^orukeet-card]
- An export audit verifies all 12,288 fitted kernels remain exact while all 651 other parameter tensors change (**Reported**).[^orukeet-card]
- Training-lineage note: the accent/domain sample holds 256 recordings per split plus all 230 Lesbos recordings; the preceding FT-4035 continuation trained on 223,452 recordings across 24 complete partitions (371.47 hours); 6,118 previously reported examples were a sampled follow-up fit diagnostic (**Reported**).[^orukeet-card]

## Benchmarks (NeMo greedy-batch TDT, FP32 weights, BF16 CUDA autocast)

Pinned scoring code defines text normalization and compound alignment; pooled WER sums errors and normalized reference words; lower is better; nothing was executed or reproduced for this wiki (**Reported**; non-reproduction is **Synthesis**).[^orukeet-card]

| Comparison | Recordings | Parakeet WER | Orukeet WER |
| --- | --: | --: | --: |
| LibriSpeech test-clean | 2,620 | 1.53% | **1.46%** |
| LibriSpeech test-other | 2,939 | 3.14% | **2.86%** |
| FLEURS English | 647 | 4.28% | **3.82%** |
| FLEURS pooled, 25 languages | 20,146 | 11.01% | **9.85%** |
| Accents/domains pooled, 47 splits | 12,006 | 16.72% | **15.25%** |
| Accents/domains English, 20 splits | 5,120 | 9.51% | **8.84%** |

- Headline rollups: wins on 61 of 74 tested splits; 25 of 27 complete LibriSpeech/FLEURS splits; 36 of 47 accent/domain splits including all 20 English accent/domain splits; FLEURS pooled 25-language 9.85% versus 11.01% is a 10.6% relative reduction (**Reported**).[^orukeet-card]
- Comparability limit: final adaptation and checkpoint selection both use LibriSpeech test-other, so the test-other gain is selection-adjacent; read-speech and accent/domain pools are reported separately (**Synthesis**).[^orukeet-card]

## Inference and runtimes

- NeMo (benchmark source): CUDA PyTorch with `nemo_toolkit[asr]==3.0.0` and `huggingface-hub`; `hf_hub_download("oruk/orukeet", "orukeet-v0.1.0.nemo", revision="555136b50265a132d4cea0d35560c26fc4f657ab")` then `ASRModel.restore_from(checkpoint)` and `transcribe([...], return_hypotheses=True)`; `orukeet fetch source` retrieves the same hash-checked checkpoint (**Reported**).[^orukeet-card]
- Transformers: standard FP32 export at the repository root using `ParakeetForTDT` without custom remote code; works with Buzz's existing Hugging Face model option; NeMo evaluation remains the source-model benchmark with separate compatibility measurements for this export (**Reported**).[^orukeet-card]
- Native (Python 3.12+, v0.1.1 wheel): `orukeet install --device auto --cache ./orukeet-cache --output installation.json` selects optimized Metal on Apple silicon, CUDA on detected NVIDIA, or CPU; `Orukeet(config["model"], config["runtime"], device=config["device"])` with `transcribe("recording.wav")["text"]`; keep the worker alive across recordings; response carries transcription plus window-level segment times, not emotion, speaking-style, or diarization scores (**Reported**).[^orukeet-card]
- sherpa-onnx INT8: archive with `encoder.int8.onnx`, `decoder.int8.onnx`, `joiner.int8.onnx`, `tokens.txt` plus BPE vocabulary, weight license, and attribution; uses the existing offline transducer loader; all 640 application-check transcripts match the previous export; same 160-clip timing sample reports median 390 ms versus 432 ms before optimization and 428 ms for stock Parakeet on M5 Max; OpenWhispr 1.10.0 ships it as the recommended local model via Local → Oruk → Orukeet (**Reported**).[^orukeet-card]
- transcribe.cpp / Handy-compatible GGUF (`orukeet-transcribe-cpp-Q8_0.gguf`): Q8 export of the same r3 checkpoint using the existing `parakeet` architecture with no Gabor-specific runtime; CPU and Apple Metal checks use the exact `transcribe-cpp` 0.2.0 dependency pinned by Handy; tensor layout differs from the native NeMo-Speech.cpp GGUFs so the export must match the runtime (**Reported**).[^orukeet-card]
- Core ML preview (Apple Silicon): greedy and baseline portable bundles for FluidAudio 0.15.5 and TapTalk with checksums and a Swift loader, compiled on the destination Mac; greedy profile cut paired batch latency 9.5% on one M5 Max and matched baseline transcripts on 128 FLEURS recordings across eight languages; does not convert the EOU 120M live-typing model (**Reported**).[^orukeet-card]

## Model files (all derive from r3)

| Format | File | Bytes |
| --- | --- | --: |
| NeMo source | `orukeet-v0.1.0.nemo` | 2,509,342,720 |
| Native Q8 | `orukeet-v0.1.0-q8.gguf` | 714,456,704 |
| transcribe.cpp Q8 | `orukeet-transcribe-cpp-Q8_0.gguf` | 739,508,608 |
| Native F16 | `orukeet-v0.1.0-f16.gguf` | 1,296,681,088 |
| ONNX INT8 archive | `onnx/sherpa-onnx-orukeet-v0.1.0-int8.tar.bz2` | 486,807,585 |
| Core ML greedy preview | `coreml/orukeet-r3-coreml-greedy.zip` | 466,579,943 |
| Core ML baseline preview | `coreml/orukeet-r3-coreml-baseline.zip` | 466,579,851 |

- Pins: NeMo and native files at revision `555136b50265a132d4cea0d35560c26fc4f657ab`; ONNX archive at `55a984d46f68323301837194ce647c702f55facc`; ONNX package occupies 671,619,800 bytes after extraction (**Reported**).[^orukeet-card]
- SHA-256: NeMo `031c8dda…473b56`; Q8 `93ce19c6…070a45bd`; F16 `de53fb8e…49194`; ONNX archive `f9191f30…3fe8d0a` (**Reported**).[^orukeet-card]
- Checks: Q8 and F16 pass real transcription and protocol checks on Apple silicon with Metal and CPU; conversion audits verify all 12,288 fitted kernels after F16 rounding (**Reported**).[^orukeet-card]

## Relationships

- Finetune of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): same 627M FastConformer-TDT recipe, tokenizer, and 25 European languages, replacing half the temporal depthwise filters with frozen Gabor kernels and retraining the rest; prefer that page for the teacher baseline (FLEURS 11.97 / MLS 7.83 / CoVoST 11.98, English Open ASR 6.34) and this page for the accuracy-improved multilingual drop-in (**Synthesis**).[^orukeet-card]
- Contrasts with quantized derivative [Phonon-2](phonon-2.md): that page keeps the teacher's conventions at ~2.1-bit encoder precision for a 164 MB English-only throughput play (5.21% seven-set mean), while this page keeps full parameter count with Gabor-fixed taps for multilingual accuracy across NeMo/ONNX/GGUF/Core ML runtimes (**Synthesis**).[^orukeet-card]
- Contrasts with ternary derivative [Parakeet Redux](parakeet-redux.md): that page compresses the same teacher's encoder to 1.58-bit ternary weights (178 MB) for 113× CPU realtime with FLEURS pooled 10.56 and TED-LIUM 2.51, while this page keeps full precision with frozen Gabor taps for accuracy (FLEURS pooled 9.85); prefer that page for the CPU/edge operating point and this page for the accuracy-improved drop-in (**Synthesis**).[^parakeet-redux-card]
- Deployed through [Parakeet ASR Server](parakeet-asr-server.md)-style ONNX serving and the OpenWhispr 1.10.0 Parakeet worker path (existing offline transducer loader, Local → Oruk → Orukeet); prefer this page for the Orukeet weights and that page for server operations (**Synthesis**).[^orukeet-card]
- Served by [transcribe.cpp](transcribe-cpp.md) via the Handy-compatible `orukeet-transcribe-cpp-Q8_0.gguf` export (same r3 checkpoint, `parakeet` architecture, `transcribe-cpp` 0.2.0 pin); prefer that page for the runtime build and quantize path (**Synthesis**).[^orukeet-card]
- Surveyed alongside sibling multilingual checkpoints in [ASR/STT Model Survey](asr-stt-model-survey.md): compare its FLEURS-pooled and LibriSpeech rows against the teacher and Canary/Qwen3-ASR rows when choosing a European-multilingual checkpoint (**Synthesis**).[^orukeet-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, no checkpoint, GGUF, ONNX, or Core ML download, no audio transcribed, and no WER or latency figure reproduced (**Synthesis**).[^orukeet-card]
- Referenced but unfetched and absent from `raw/`: technical report PDF, `CITATION.bib`, `NOTICE.md`, `ARTIFACTS.json`, `kernel-fits.png` and affiliation images, `transformers/README.md`, `transcribe-cpp/README.md`, `coreml/README.md`, `docs/current-checkpoint-benchmarks.md` (all 74 paired scores), `docs/technical-report.md`, `docs/usage.md`, `docs/data-and-licenses.md`, training and export READMEs, evidence and conversion receipts, runtime catalogue, OpenWhispr PR and release, and oruk.ai guides and walkthroughs; all install and inference fences are transcribed, not executed (**Synthesis**).[^orukeet-card]
- All accuracy, training, size, checksum, and speed claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^orukeet-card]

[^orukeet-card]: [Orukeet model card](../raw/orukeet.md) — locators: frontmatter (`base_model: nvidia/parakeet-tdt-0.6b-v3`, `base_model_relation: finetune`, `pipeline_tag`, `library_name: nemo`, 25-code `language` list, `license: cc-by-sa-4.0`, `tags`, `transcribe_cpp` streaming/translate/lang_detect/timestamps); intro (25-language recognizer, 12,288 fitted frozen Gabor kernels, 61/74 wins, LS clean 1.46 vs 1.53 / other 2.86 vs 3.14 / FLEURS en 3.82 vs 4.28 / pooled 9.85 vs 11.01 with 10.6% relative, r3 checkpoint `031c8dda…`); `Run Orukeet with Transformers` (`ParakeetForTDT`, no remote code, Buzz option, `transformers/README.md`); `Run Orukeet with NeMo` (`nemo_toolkit[asr]==3.0.0`, `hf_hub_download` fence with revision `555136b5…`, `orukeet fetch source`); `Architecture` (627,008,134 params, 24-layer FastConformer, 1,024 nine-tap filters/block, Gabor equation, 24,576 fitted → 12,288 kept, 175–748/layer, 6.32% median / 13.30% cutoff, 110,592 fixed taps, 626,897,542 trainable); `Construction` (transducer + matching + distillation, 4,035 updates, r3 168 AdamW 3% warmup cosine `5e-6→5e-7` over 3×2,939 test-other, casing/punct targets, export audit 12,288 exact + 651 changed); `Evaluation` (NeMo greedy-batch TDT FP32/BF16, 6-row table with recording counts, 25/27 + 36/47 incl. 20/20 English wins, 256/split + 230 Lesbos, FT-4035 223,452 recordings / 24 partitions / 371.47 h, 6,118 diagnostic note); `sherpa-onnx inference` (INT8 file layout, 640 transcripts match, 390 vs 432 vs 428 ms M5 Max, OpenWhispr 1.10.0 Local→Oruk→Orukeet, archive SHA `f9191f30…`); `Native inference` (Python 3.12+, v0.1.1 wheel, `install --device auto` fence, Metal/CUDA/CPU selection, window-level segments without emotion/style/diarization); `transcribe.cpp and Handy-compatible GGUF` (`orukeet-transcribe-cpp-Q8_0.gguf`, `parakeet` arch, `transcribe-cpp` 0.2.0, layout warning); `Core ML preview` (greedy/baseline bundles, FluidAudio 0.15.5 + TapTalk, 9.5% latency cut, 128 FLEURS / 8 langs match, not EOU 120M); `Model files` (7-row byte table, revision pins, 671,619,800-byte extracted ONNX, NeMo/Q8/F16 SHAs, Metal/CPU checks, F16 kernel audit); `License and attribution` (MIT code, CC BY-SA 4.0 weights/kernels, CC BY 4.0 metric records); `Citation` (arXiv `2609.10054`).
[^parakeet-redux-card]: [Moondream Parakeet Redux model card](../raw/parakeet-redux.md) — locators: intro (1.58-bit ternary `parakeet-tdt-0.6b-v3` derivative, 178 MB, 113× CPU realtime); `Benchmarks` (FLEURS pooled 10.56 vs 11.62, TED-LIUM 2.51 vs 2.71).
