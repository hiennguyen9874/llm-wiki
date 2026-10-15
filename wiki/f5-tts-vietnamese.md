---
type: Concept
title: F5-TTS-Vietnamese-1000h
description: Vietnamese F5-TTS_Base finetune trained on a reported 1,000 hours, with reference-conditioned CLI synthesis, non-commercial licensing and an incomplete usage example.
tags: [tts, vietnamese, f5-tts, voice-cloning]
status: draft
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T10:39:24Z }
stale_after: 2027-04-15
sources:
  - id: f5-vi-card
    resource: ../raw/F5-TTS-Vietnamese-ViVoice.md
    kind: documentation
    title: F5-TTS-Vietnamese-1000h model card
---

F5-TTS-Vietnamese-1000h is a Vietnamese F5-TTS_Base finetune trained on a reported 1,000 hours of speech, with a PyTorch CLI example using reference audio, transcript and Vocos. The card declares CC-BY-NC-SA-4.0 and non-commercial research use; it supplies no quality or realtime benchmarks. Treat it as a research candidate, not an established realtime backend (**Reported** capabilities/terms; selection **Synthesis**).[^f5-vi-card]

## Data and training

- Frontmatter names `F5-TTS-Vietnamese-1000h`, language `vi`, library `pytorch`, and datasets ViVoice, VLSP2021, VLSP2022 and VLSP2023. The body calls the first dataset Vi-Voice and links `nguyenthienhy/F5-TTS-Vietnamese` for experiments. Explicit creator/publisher, canonical model-host URL, release date and revision are absent (**Observed** metadata/omissions).[^f5-vi-card]
- Processing removes background music with Facebook Demucs, excludes clips shorter than 1 second or longer than 30 seconds, filters bad transcripts with Zalo-AI's “Chunk-Large-Former Speech2Text,” preserves punctuation and lowercases text. ASR checkpoint identity, filtering thresholds, collection consent and dataset-rights evidence are unspecified (**Reported** processing; **Observed** omissions).[^f5-vi-card]
- Training uses F5-TTS_Base, RTX 3090, batch size 3,200 frames and 1.5 months according to the card. Parameter count, dataset split, per-corpus hours, optimizer, learning rate, epochs and checkpoint selection are unavailable. “Compact” is not a measured size (**Reported** training; **Observed** limits).[^f5-vi-card]

## Inference and example defects

The example clones `https://github.com/nguyenthienhy/F5-TTS-Vietnamese`, enters the checkout and runs `python -m pip install -e.`. It invokes `f5-tts_infer-cli` with `--model "F5TTS_Base"`, `--ref_audio ref.wav`, Vietnamese `--ref_text` and `--gen_text`, `--speed 1.0`, `--vocoder_name vocos`, `--vocab_file F5-TTS-Vietnamese-ViVoice/vocab.txt` and `--ckpt_file F5-TTS-Vietnamese-ViVoice/model_last.pt` (**Observed** example, not tested compatibility).[^f5-vi-card]

Do not run the example unchanged (**Synthesis**):[^f5-vi-card]

- `mv F5-TTS-Vietnamese-ViVoice/config.json F5-TTS-Vietnamese-ViVoice/vocab.txt` moves/renames a JSON config to a vocabulary path and may overwrite an existing vocabulary; no conversion is explained (**Observed** command, risk **Synthesis**).
- The capture ends inside an unclosed Bash fence, with a trailing CLI continuation and separator; checkpoint download and explicit output path are not supplied (**Observed**).
- Reference constraints, runtime/Python versions, sampling rate, inference VRAM, TTFA, RTF, streaming, concurrency, cancellation and CPU/ONNX/GGUF support are not established. A training GPU is not an inference requirement or latency measurement (**Observed** omissions; boundary **Synthesis**).[^f5-vi-card]

## License and responsible use

Frontmatter and the license link declare CC-BY-NC-SA-4.0; prose says non-commercial research use only. The Important Note specifies research, experimentation and technology development, prohibits unlawful impersonation, cloning without lawful consent, misleading content and fraud, assigns responsibility to users and recommends AI-generated disclosure. Authors disclaim endorsement and liability. These are source-reported terms, not an independent legal or data-rights review (**Reported**).[^f5-vi-card]

## Relationships

- Compared in [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md): primary card available, but missing benchmark/streaming evidence does not justify changing deployment ordering (**Synthesis**).[^f5-vi-card]
- Cataloged in [TTS Model Survey](tts-model-survey.md); evidence concerns this Vietnamese finetune, not all upstream F5-TTS checkpoints (**Synthesis**).[^f5-vi-card]

## Coverage and limits

Fully inspected the single Markdown capture. No code installed or executed, weights downloaded, audio synthesized/listened to or benchmark reproduced. Status is draft because usage and required assets remain unresolved. Quality metrics, protocols, baselines, ablations and uncertainty are not supplied (**Observed** coverage/omissions; **Synthesis** status).[^f5-vi-card]

Ledger: the linked experiment GitHub repository (implementation, manifests, configs and tests), Demucs repository, datasets, F5-TTS_Base weights, Vocos implementation, referenced `config.json`, `vocab.txt`, `model_last.pt` and `ref.wav` are not included in the supplied single-file source or inspected. The external SPDX license page was not fetched. Relative `qr.jpg` was not found beside the capture and is excluded as decorative/payment material; donation prose is excluded as nontechnical. No sensitive values were compiled. No immutable upstream revision or capture date is supplied.[^f5-vi-card]

[^f5-vi-card]: [F5-TTS-Vietnamese-1000h card](../raw/F5-TTS-Vietnamese-ViVoice.md) — frontmatter; Important Note; F5-TTS-Vietnamese-1000h introduction/license; Model Details (processing and training); Usage (clone/install, mv and CLI flags, truncated fence). Revision and capture date unavailable.
