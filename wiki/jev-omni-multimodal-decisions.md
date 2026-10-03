---
type: Concept
title: Jev-Omni Multimodal Decision Classifier
description: Independent open-weight multimodal classifier over text, image, audio and video on Gemma 4 12B with calibrated 2–256 option decisions, reported benchmarks and loader mechanics.
tags: [jev, decision-models, multimodal, classification, calibration]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:59:00Z }
sources:
  - id: jev-omni-2026
    resource: ../raw/Jev-Omni/README.md
    scope: ../raw/Jev-Omni/
    kind: model-card
    title: akhilaaa3/Jev-Omni
---

# Jev-Omni Multimodal Decision Classifier

Synthesis: Jev-Omni is an independent Apache-2.0 open-weight decision classifier on Gemma 4 12B IT that returns calibrated probabilities over 2–256 options for text, image, audio and video inputs — not generated explanations — with **reported** DecisionBench Medium 87.57%, JevBench 86.15%, MMAU 63.10% and MVBench 53.10%, and **observed** single-pass head-plus-prompt loader mechanics[^jev-omni-2026].

## Identity and provenance

- Package `../raw/Jev-Omni/` with canonical entry `README.md`; Hugging Face ID `akhilaaa3/Jev-Omni` from loader `MODEL_ID` and requirements URL; base `google/gemma-4-12B-it` from frontmatter and `decision_config.json`[^jev-omni-2026].
- License **observed** as Apache-2.0 following Gemma 4; dataset rights remain separate[^jev-omni-2026].
- Independence claim **reported**: implements the typed-decision interface — noul (yes/no), choice and score questions answered with calibrated probabilities — but is not affiliated with, endorsed by, sponsored by, or derived from TypeSafe AI or its Jev model, and nothing in it was trained on Jev output[^jev-omni-2026].
- Contract: supply `state` plus `question` and `options`; receive a probability for each option[^jev-omni-2026].

## Architecture — observed

- Unified backbone `Gemma4UnifiedForConditionalGeneration` (`config.json`): text tower hidden 3840, 48 layers, vocab 262144, native 262144 positions, sliding window 1024, plus audio and vision configs with dedicated token IDs (image 258880, audio 258881, video 258884)[^jev-omni-2026].
- Decision head `_Head256` in `jev_omni.py`: normalise last-token hidden state by `mu`/`sd` buffers, `Linear(hidden, 256)` in fp32, mask inactive slots with `-1e30`, softmax over active count; `decision_config.json` gives `hidden_size` 3840 and `output_classes` 256[^jev-omni-2026].
- Readout: forward hook captures decoder last-token `last_hidden_state` (`_find_backbone` tries `model.language_model` then fallbacks), model run under `torch.autocast("cuda", BF16)` with `use_cache=False`, then `head(hidden, count)` sliced to `len(options)`[^jev-omni-2026].
- Prompt **observed** in `_prompt`: `{state}\n\n---\n\nQUESTION: {question}\n\nOPTIONS:\n1. ...\n\nReply with only the number of the correct option (1-N).\nOutput a single number and nothing else.`[^jev-omni-2026].

## Multimodal input handling — observed

- `JevOmni.predict(*, state, question, options, media, modality, video_frames)` returns `{prediction, prediction_index, confidence, probabilities}` with `probabilities` mapping each option string to its mass[^jev-omni-2026].
- Constraints enforced in code: 2–256 options; `modality` in `text/image/audio/video`; non-text requires `media=...` path[^jev-omni-2026].
- Image: `PIL.Image.open(media).convert("RGB")` as one `{type:image}` content part[^jev-omni-2026].
- Video: `_video_frames` samples `video_frames` (default 16) uniformly via `cv2.VideoCapture` (`int(round((total-1)*(k+.5)/count))`), each frame as an image part; `processor_config.json` video processor allows up to 32 frames with `max_soft_tokens` 70, so the loader default is narrower than the processor maximum[^jev-omni-2026].
- Audio: `ffmpeg -t 30 -ac 1 -ar 16000` to temp `.wav`, single `{type:audio}` part, temp file unlinked after `apply_chat_template`; 30-second cap is enforced here and documented in Quick start[^jev-omni-2026].
- Chat templating via `processor.apply_chat_template([{role:user, content}], add_generation_prompt=True, enable_thinking=False)`; loader notes it downloads the original Gemma 4 multimodal components automatically[^jev-omni-2026].

## Training recipe — observed with one unresolved count

- `decision_config.json` recipe **observed**: `size` 24000, rank 512 / alpha 512, lr 1e-05, head_lr 1e-05, microbatch 8, grad_acc 1, effective_batch 32, 1 epoch, warmup_ratio 0.1 / warmup_steps 75, total steps 750, seed 3407, init `FP32 merged trained v1 + trained head + fresh LoRA`, schedule linear warmup then linear decay to 10%, trainable 2099183872 (~2.1B), world_size 4 NCCL, `source_tag: lora-v1merged-n24000-r512-lr1e-05-eb32-w10-ddp4`, merged adapters `[trained v1 rank128, lora-...]`, fingerprints recorded[^jev-omni-2026].
- README says a 30,000-question fine-tuning run on Gemma 4 12B IT; see [Contradictions](#contradictions)[^jev-omni-2026].
- Results table is labeled merged-model results[^jev-omni-2026].

## Reported benchmarks

- DecisionBench Medium (80 scenarios / 293 questions): **reported** 87.57% accuracy (equal-weight scenario average) and 86.01% micro accuracy[^jev-omni-2026].
- JevBench (matched 195 groups / 231 decisions): **reported** 86.15% accuracy and 87.45% micro accuracy[^jev-omni-2026].
- MMAU (1,000 questions): **reported** micro 63.10%; MVBench (14 evaluated tasks / 2,786 questions): **reported** 53.10% accuracy and 53.09% micro[^jev-omni-2026].
- Open-weight comparison **reported**: Jev-Omni 12B (63.10% MMAU, 53.10% MVBench, text/image/audio/video) vs Inkling 975B total / 41B active (77.20% MMAU, text/image/audio) vs Qwen3.5-397B-A17B 397B total / 17B active (77.60% MVBench, text/image/video); reference scores are officially reported by their developers and may use different protocols[^jev-omni-2026].
- Cost plot **observed** in `assets/medium-accuracy.svg`: DecisionBench Medium state-macro accuracy vs API cost per state (log USD) with Jev-Omni 87.57%, Jev 1.13 90.48%, GPT-5.6 Luna 98.76%, Gemini 3.8 Flash 99.12%, Claude Sonnet 5 99.12%; costing uses recorded input tokens at OpenRouter Gemma 3 12B input rate ($0.05/M) with no output tokens, classifiers priced one call per question (state re-sent each) vs chat models one call per state (all questions together, their cheapest shape); splitting a state per-question multiplies input tokens 2.82× on this set without changing order[^jev-omni-2026].
- Calibration **reported**: Medium ECE 0.0400 (10 bins, lower better); graph uses five bins for readability; `assets/medium-calibration.svg` plots Jev-Omni vs Jev 1.13, GPT-5.6 Luna, Gemini 3.8 Flash and Claude Sonnet 5 with larger dots for more answers[^jev-omni-2026].

## Speed, requirements and limits

- Warm H200 inference **reported** as medians over 20 optimized-backend requests: ~83 ms (~2k-token text), ~26 ms (image), ~31 ms (13-second audio), ~504 ms (16-frame video); preprocessing and network extra[^jev-omni-2026].
- Requirements **observed**: CUDA GPU required (`load_jev_omni` raises unless `device=="cuda"` and `torch.cuda.is_available()`); FP32 weights ~50 GB before runtime overhead with BF16 autocast; single ~24 GB download with no base-model download or merging at load time per loader docstring; `requirements.txt` pins `transformers==5.17.0` plus `torch>=2.10`, `accelerate`, `huggingface_hub`, `safetensors`, `numpy`, `Pillow`, `opencv-python-headless`, `soundfile`, `librosa`, and system `ffmpeg` for audio[^jev-omni-2026].
- Operating limits **reported**: best supported at ≤20 options; head accepts 256 but quality above 20 is not established; audio capped at 30 s; video uses 16 frames[^jev-omni-2026].
- Regression artifact **observed**: `verification.json` holds 4 fixed cases (meeting-time, refund-resolved, fair die, urn draw) with reference probability maps and `worst_abs_diff` 0.0193658; use it as a loader smoke check, not a benchmark[^jev-omni-2026].

## Relationships

- Contrasts with [Jev-27B-VL Vision-Capable System 1 Decisions and Serving](jev-27b-vl-multimodal-decisions.md), which adds zero-shot image decisions to a text-trained head, whereas Jev-Omni natively handles image plus audio and video with a multimodal backbone.
- Implements the typed-decision contract described in [Jev API Patterns](jev-api-patterns.md), but with its own `predict(state, question, options, media, modality)` shape rather than the hosted Choice/Noul/Score endpoints.
- Uses [Classifier Calibration](classifier-calibration.md) ECE framing for its 0.0400 Medium figure.
- Informs [Classifier Selection](classifier-selection.md) when a single open-weight model must cover audio/video as well as text and image.
- Extends [Jev Decision Model](jev-decision-model.md) as an independent (non-student) open alternative.

## Contradictions

- Training size: README says 30,000-question fine-tuning run while `decision_config.json` recipe says `size` 24000 with `source_tag ...-n24000-...` and 750 steps × effective batch 32 = 24,000 rows for one epoch — **unresolved**; cite both without choosing[^jev-omni-2026].

## Coverage limits

- Static inspection only; no GPU execution, API calls, or benchmark reproduction, so benchmarks, speed and cost are **reported** while interfaces, configs and dependency pins are **observed**.
- Inspected `README.md`, `jev_omni.py`, `example.py`, `decision_config.json`, `config.json`, `processor_config.json`, `generation_config.json`, `tokenizer_config.json`, `requirements.txt`, `verification.json`, `sha256.json`, `.gitattributes`, and both `.svg` figures; `chat_template.jinja` Google Gemma 4 canonical template was read for setup/thinking/tool branches but only the decision-relevant `enable_thinking=False` path is characterised above.
- Unavailable locally: `tokenizer.json`, `head.pt`, `assets/medium-accuracy.png`, `assets/medium-calibration.png`, and `assets/the-wall-23s.mp4` are Git-LFS pointers; weight shards (`model.safetensors` in loader `allow_patterns`) are absent; hashes for all of these are recorded in `sha256.json`.
- PNG/MP4 bytes were not visually inspected; SVG text was read instead of pixels and the MP4 has no transcript here.
- Single-point vendor-style numbers with proxy pricing (Gemma 3 12B rate for a Gemma 4 model) and protocol-mismatched open-weight references; verify before buy-vs-build use.

[^jev-omni-2026]: akhilaaa3, “Jev-Omni,” model card, canonical local entry `../raw/Jev-Omni/README.md`, package scope `../raw/Jev-Omni/`, upstream `https://huggingface.co/akhilaaa3/Jev-Omni` via loader `MODEL_ID` and requirements URL. Locators: “Results” and “Open-weight comparison” tables; cost paragraphs and `assets/medium-accuracy.svg` title/axes/legend/values; “Quick start” CUDA/FP32/BF16/media-caps text plus `example.py`; “Speed” H200 medians; “Limits” ≤20/256 line; “License” Apache-2.0 line; “Calibration” ECE line and `assets/medium-calibration.svg`; independence note; `jev_omni.py::MODEL_ID/_prompt/_video_frames/JevOmni.predict/_Head256/load_jev_omni`; `decision_config.json` hidden/output/recipe keys; `config.json` architectures/text/hidden/vocab/audio-image-video ids; `processor_config.json` image/audio/video keys; `requirements.txt`; `verification.json` cases/reference/worst_abs_diff; `sha256.json`; `.gitattributes` LFS list.
