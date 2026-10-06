---
type: Concept
title: Canary-Qwen-2.5B
description: NVIDIA NeMo 2.5B-parameter English-only SALM ASR model combining a FastConformer audio encoder with a Qwen3-1.7B decoder, reporting 5.63% mean WER on the Open ASR Leaderboard at 418 RTFx with dual ASR and LLM post-processing modes.
tags: [stt, asr, english]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T14:02:00Z }
stale_after: 2027-10-06
sources:
  - id: canary-qwen-2p5b-card
    resource: ../raw/canary-qwen-2.5b.md
    kind: documentation
    title: Canary-Qwen-2.5B model card
---

Canary-Qwen-2.5B (`nvidia/canary-qwen-2.5b`) is NVIDIA NeMo team's 2.5B-parameter English-only speech-recognition model that pairs a FastConformer audio encoder with a `Qwen/Qwen3-1.7B` decoder through a linear projection plus LoRA, transcribes with punctuation and capitalization at a reported 418 RTFx, and runs in two modes — ASR transcription mode and text-only LLM post-processing mode (summarize, Q&A over the transcript) — released under CC-BY-4.0 for commercial use (**Reported**).[^canary-qwen-2p5b-card]

## Model identity and lineage

- Card title is `canary-qwen-2.5b`; Hugging Face release date is 07/17/2025 via `https://huggingface.co/nvidia/canary-qwen-2.5b`; license is CC-BY-4.0; deployment geography is Global; intended use is English speech-to-text plus transcript post-processing (transcription, summarization, answering questions about the transcript) (**Reported**).[^canary-qwen-2p5b-card]
- Speech-Augmented Language Model (SALM) [9] with FastConformer [2] encoder and Transformer decoder [3]; built from two base models — `nvidia/canary-1b-flash` [1,5] and `Qwen/Qwen3-1.7B` [4] — plus a linear projection from audio representations into LLM embedding space and low-rank adaptation (LoRA) on the LLM; prompted with `Transcribe the following: <audio>` using Qwen's chat template (**Reported**).[^canary-qwen-2p5b-card]
- Frontmatter declares `library_name: nemo`, `language: [en]`, tags including `automatic-speech-recognition`, `speech`, `audio`, `Transformer`, `FastConformer`, `Conformer`, `pytorch`, `NeMo`, `Qwen`, and `hf-asr-leaderboard`, and training-data frontmatter naming Granary, YTC, Yodas2, LibriLight, librispeech_asr, fisher_corpus, Switchboard-1, WSJ-0/1, National-Singapore-Corpus Part-1/6, vctk, voxpopuli, europarl, multilingual_librispeech, fleurs, Common Voice 8.0, and peoples_speech (**Observed** by static inspection).[^canary-qwen-2p5b-card]
- Dual-mode semantics: in ASR mode the model only transcribes speech and retains no LLM reasoning skills; in LLM mode it retains the original LLM capabilities for transcript post-processing but no longer "understands" raw audio, only its transcript (**Reported**).[^canary-qwen-2p5b-card]

## Architecture and I/O

- Audio encoder output frame rate is 80 ms (12.5 tokens per second), concatenated with text-token embeddings after linear projection; tokenizer inherited from `Qwen/Qwen3-1.7B` (**Reported**).[^canary-qwen-2p5b-card]
- Input is a batch of prompts containing audio: 16 kHz mono `.wav`/`.flac` (2D `batch, audio-samples`) plus a text prompt string (`Transcribe the following: <|audioplaceholder|>`); no preprocessing needed; input audio to the SALM `generate` call uses `model.audio_locator_tag` (**Reported**).[^canary-qwen-2p5b-card]
- Output is a 1D text transcript as token IDs or string with punctuation and capitalization; may need inverse text normalization; model optimized for NVIDIA GPU-accelerated systems via CUDA versus CPU-only (**Reported**).[^canary-qwen-2p5b-card]
- Software/hardware envelope: runtime is NeMo 2.5.0 or higher (latest trunk plus PyTorch 2.6+ for FSDP2 at card time); supported microarchitectures are Ampere, Blackwell, Jetson, Hopper, Lovelace, Pascal, Turing, and Volta; operating systems are Linux, Linux 4 Tegra, and Windows; test hardware lists A6000, A100, and RTX 5090 (**Reported**).[^canary-qwen-2p5b-card]

## Training data and procedure

- Trained with the NeMo toolkit for 90k steps on 32 NVIDIA A100 80GB GPUs; LLM parameters frozen; speech encoder, projection, and LoRA parameters trainable; ~1.3B tokens seen in total (speech-encoder output frames plus text response, prompt, and chat-template tokens) (**Reported**).[^canary-qwen-2p5b-card]
- Training script is `examples/speechlm2/salm_train.py` with base config `examples/speechlm2/conf/salm.yaml`; trainable-module and efficiency background point to references [5] and [6] (**Reported**).[^canary-qwen-2p5b-card]
- Scale is ~234K hours of public English speech (~40M speech-text pairs) across 26 datasets (18 train, 8 test) partitioned 99.6% train / 0.04% test / 0% validation; collection window 1990–2025 for training and 2005–2022 for testing; collection method Human, labeling Hybrid (Human, Automated); transcripts carry punctuation and capitalization (**Reported**).[^canary-qwen-2p5b-card]
- Majority comes from the English Granary [7] portion — YouTube-Commons (109.5k hrs), YODAS2 (77k hrs), LibriLight (13.6k hrs) — plus Librispeech (960 hrs), Fisher, Switchboard-1, WSJ-0/1, National Speech Corpus Parts 1 and 6, VCTK, VoxPopuli (EN), Europarl-ASR (EN), Multilingual Librispeech (EN), Common Voice v4.0/v7.0/v11.0, AMI, and FLEURS; AMI was oversampled to ~15% of observed data, skewing the model toward verbatim transcripts with conversational disfluencies such as repetitions (**Reported**).[^canary-qwen-2p5b-card]

## Inference and usage

- Install: `python -m pip install "nemo_toolkit[asr,tts] @ git+https://github.com/NVIDIA/NeMo.git"`; load: `SALM.from_pretrained('nvidia/canary-qwen-2.5b')` from `nemo.collections.speechlm2.models` (**Reported**).[^canary-qwen-2p5b-card]
- ASR mode: `model.generate(prompts=[[{"role": "user", "content": f"Transcribe the following: {model.audio_locator_tag}", "audio": ["speech.wav"]}]], max_new_tokens=128)` then `model.tokenizer.ids_to_text(...)` (**Reported**).[^canary-qwen-2p5b-card]
- LLM (text-only) mode: wrap generation in `with model.llm.disable_adapter():` and call `model.generate(prompts=[[{"role": "user", "content": f"{prompt}\n\n{transcript}"}]], max_new_tokens=2048)` (**Reported**).[^canary-qwen-2p5b-card]
- Dataset transcription: write a `.jsonl` manifest with `audio_filepath` and `duration` per line, then run `python examples/speechlm2/salm_generate.py pretrained_name=nvidia/canary-qwen-2.5b inputs=input_manifest.json output_manifest=generations.jsonl batch_size=128 user_prompt="Transcribe the following:"` (audio locator appended automatically when absent) (**Reported**).[^canary-qwen-2p5b-card]

## Benchmarks

All numbers below are source assertions from the card; nothing was executed or reproduced for this wiki (**Synthesis**).[^canary-qwen-2p5b-card]

- ASR predictions use greedy decoding; WER scoring processes reference and hypothesis with `whisper-normalizer` 0.1.12 and strips punctuation/capitalization (`w/o PnC`) (**Reported**).[^canary-qwen-2p5b-card]
- Hugging Face Open ASR Leaderboard row (Version 2.5.0, RTFx 418): mean 5.63; AMI 10.18, GigaSpeech 9.41, LibriSpeech Clean 1.60, LibriSpeech Other 3.10, Earnings22 10.42, SPGISpeech 1.90, Tedlium 2.72, VoxPopuli 5.66 (**Reported**; frontmatter `model-index` differs by +0.01 on AMI 10.19, GigaSpeech 9.43, LibriSpeech Clean 1.61, and Earnings22 10.45 — rounding-level deltas, neither value chosen over the other).[^canary-qwen-2p5b-card]
- Hallucination robustness on the 48-hour MUSAN [17] eval set (`max_new_tokens=50`, same protocol as `nvidia/canary-1b-flash`): 138.1 characters per minute (**Reported**).[^canary-qwen-2p5b-card]
- Noise robustness on LibriSpeech Test Clean with additive white noise (WER down): 2.41% at SNR 10, 4.08% at SNR 5, 9.83% at SNR 0, 30.60% at SNR −5 (**Reported**).[^canary-qwen-2p5b-card]
- Fairness on CasualConversations-v1 [8] with inference on non-overlapping 40 s chunks (WER down, reference and hypothesis normalized as in the Open ASR Leaderboard recipe): gender Male 16.71% (18,471 utts), Female 13.85% (23,378), N/A 17.71% (880), Other 29.46% (18); age 18–30 15.73% (15,058), 31–45 15.30% (13,984), 46–85 14.14% (12,810), 1–100 aggregate 15.11% (41,852) (**Reported**).[^canary-qwen-2p5b-card]

## Trust, ethics, and limits

- Stated limits: maximum 40 s audio and 1,024 tokens (prompt plus audio plus response) seen in training — longer inputs may technically run with degraded accuracy; exclusively ASR-oriented with no expectation that underlying LLM capabilities transfer into the speech modality; English-only training (German/French/Spanish encoder pretraining may produce spurious non-English output, not reliable multilingual use) (**Reported**).[^canary-qwen-2p5b-card]
- Ethical framing is NVIDIA Trustworthy AI shared responsibility with Model Card++ explainability/bias/safety/privacy subcards and a security-vulnerability reporting link (**Reported**).[^canary-qwen-2p5b-card]
- Evaluation datasets are Human-collected and Human-labeled: Open ASR Leaderboard sets, MUSAN 48 hrs (hallucination), LibriSpeech (noise), and Casual Conversations (fairness) (**Reported**).[^canary-qwen-2p5b-card]

## Relationships

- Extends the Canary family covered by [Canary-1b-v2](canary-1b-v2.md): that concept is a 978M-parameter multitask FastConformer encoder-decoder over 25 European languages with translation, while Canary-Qwen-2.5B is a 2.5B English-only SALM that reuses the `canary-1b-flash` encoder line with a Qwen3-1.7B decoder; cross-read both when choosing between multilingual coverage and English accuracy (**Synthesis**).[^canary-qwen-2p5b-card]
- Shares its decoder lineage with the [Qwen3-ASR family](qwen3-asr-family.md): both build on Qwen3, but Qwen3-ASR is a 30-language audio-LLM recognizer while Canary-Qwen-2.5B is English-only with a dual ASR/LLM-post-processing split; compare them for English accuracy versus language breadth (**Synthesis**).[^canary-qwen-2p5b-card]
- Ranked in this wiki's comparison in the [ASR/STT Model Survey](asr-stt-model-survey.md): cross-read that survey for Open ASR Leaderboard ordering, noise/hallucination robustness, and licensing against Parakeet, Nemotron, ARK, and Audio8 rows (**Synthesis**).[^canary-qwen-2p5b-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, no model download, no audio transcribed, and no WER, RTFx, SNR, hallucination-rate, or fairness figure reproduced (**Synthesis**).[^canary-qwen-2p5b-card]
- Referenced but unfetched and absent from `raw/`: Hugging Face model page and demo; NeMo repository, `salm_train.py`/`salm.yaml`/`salm_generate.py` scripts, and NeMo/Riva/NIM portals; Qwen3-1.7B card; papers [1]–[9]; Granary/YTC/YODAS2/LibriLight/LibriSpeech/Fisher/Switchboard/WSJ/NSC/VCTK/VoxPopuli/Europarl/MLS/Common Voice/AMI/FLEURS, Open ASR Leaderboard, MUSAN, and Casual Conversations datasets; all install and inference fences are transcribed, not executed (**Synthesis**).[^canary-qwen-2p5b-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^canary-qwen-2p5b-card]

[^canary-qwen-2p5b-card]: [Canary-Qwen-2.5B model card](../raw/canary-qwen-2.5b.md) — locators: frontmatter (`license` cc-by-4.0, `language: [en]`, `library_name: nemo`, `tags`, `datasets` list, `metrics: [wer]`, `base_model: [nvidia/canary-1b-flash, Qwen/Qwen3-1.7B]`, full `model-index` 8-set WER matrix); header badges (SALM arch, 2.5B params, en, 418 RTFx); `Model Overview > Description` (SOTA claim, PnC, dual ASR/LLM modes, commercial use); `License/Terms`, `Release Date` (Hugging Face 07/17/2025), `Deployment Geography` (Global), `Use Case`; `Model Architecture` (SALM [9], FastConformer [2], Transformer decoder [3], projection plus LoRA, `Transcribe the following: <audio>` plus Qwen chat template); `Limitations` (40 s / 1024 tokens, ASR-only, English-only); `Training` (90k steps, 32×A100 80GB, frozen LLM, trainable encoder/projection/LoRA, 80 ms / 12.5 tok/s, 1.3B tokens, `salm_train.py` plus `salm.yaml`, Qwen3-1.7B tokenizer); `Training Dataset` (234K hrs, ~40M pairs, 26/18/8 split, 99.6%/0.04%/0%, 1990–2025 / 2005–2022 windows, Human/Hybrid methods, Granary YTC 109.5k / YODAS2 77k / LibriLight 13.6k plus corpus list, AMI 15% oversample with disfluency note, PnC transcripts); `Evaluation Dataset` (Leaderboard, MUSAN 48 hrs, LibriSpeech, Casual Conversations; Human/Human); `Performance` (greedy decoding, whisper-normalizer 0.1.12 w/o PnC; Leaderboard table v2.5.0 mean 5.63 at RTFx 418; MUSAN 138.1 chars/min with `max_new_tokens=50`; SNR table 2.41/4.08/9.83/30.60%); `Model Fairness Evaluation` (CasualConversations-v1 40 s chunks, gender and age WER tables); `Inference` (NeMo engine; A6000/A100/RTX 5090); `How to Use`/`Loading`/`Input`/`Output`/`Software Integration` (NeMo 2.5.0+, SALM fences, ASR `max_new_tokens=128` vs LLM `disable_adapter` 2048 fences, jsonl manifest plus `salm_generate.py` fence, 16 kHz mono, `.wav`/`.flac`, INVERSE-text-norm note, GPU/CUDA note, Ampere–Volta list, Linux/L4T/Windows); `References [1]–[9]`.
