---
type: Concept
title: Kokoro Vietnamese
description: Fine-tuned Vietnamese Kokoro TTS artifact set with PyTorch and ONNX runtimes, vig2p grapheme-to-phoneme, and default plus additional voicepacks.
tags: [tts, vietnamese, kokoro, onnx]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:25:17Z }
stale_after: 2027-10-07
sources:
  - id: kokoro-vi-readme
    resource: ../raw/Kokoro-Vietnamese.md
    kind: documentation
    title: Kokoro Vietnamese README capture
---

Kokoro Vietnamese is a fine-tuned Vietnamese Kokoro text-to-speech artifact set shipping a PyTorch `KModel` checkpoint alongside an ONNX Runtime acoustic-model export, a default Vietnamese voicepack plus additional voicepacks, and `vig2p` Vietnamese grapheme-to-phoneme handling, with `kokoro-vietnamese` (PyTorch), `kokoro-vietnamese-onnx` (ONNX Runtime), and `kokoro-vietnamese-export-onnx` command-line entry points (**Reported**).[^kokoro-vi-readme]

## Artifact layout

- `kokoro_vi.pth`: PyTorch Kokoro `KModel` checkpoint for inference (**Reported**).[^kokoro-vi-readme]
- `kokoro_vi.onnx`: ONNX Runtime export of the acoustic model (**Reported**).[^kokoro-vi-readme]
- `kokoro_vi_voicepack.pt`: default Vietnamese voicepack (**Reported**).[^kokoro-vi-readme]
- `config.json`: Kokoro config/vocab used by both PyTorch and ONNX inference (**Reported**).[^kokoro-vi-readme]
- `voicepacks/*.pt`: additional Vietnamese voicepacks (**Reported**).[^kokoro-vi-readme]
- Capture frontmatter declares `language: vi`, `pipeline_tag: text-to-speech`, tags `kokoro` / `vietnamese` / `text-to-speech` / `onnx`, and `license: apache-2.0` (**Reported**).[^kokoro-vi-readme]

## Install and runtimes

- Source install: `git clone https://github.com/iamdinhthuan/Kokoro-Vietnamese.git`, `cd Kokoro-Vietnamese`, `pip install -e .` (**Reported**).[^kokoro-vi-readme]
- ONNX Runtime extra: `pip install -e ".[onnx]"` (**Reported**).[^kokoro-vi-readme]
- No revision, dependency pins, Python version, model size, sample rate, or training-data details are stated in the capture (**Observed** absence).[^kokoro-vi-readme]

## Inference commands

- PyTorch CLI: `kokoro-vietnamese --text "Xin chào, hôm nay tôi đang kiểm tra giọng đọc tiếng Việt." --output outputs/sample.wav --voice diem_trinh --device cuda`; the only named voice in the capture is `diem_trinh` (**Reported**).[^kokoro-vi-readme]
- ONNX Runtime CLI: `kokoro-vietnamese-onnx --text "Tường nhà khách đã được sơn lại." --output outputs/onnx.wav --device cpu --print-phonemes` (**Reported**).[^kokoro-vi-readme]
- The ONNX CLI downloads `kokoro_vi.onnx`, `kokoro_vi_voicepack.pt`, and `config.json` from the repository when local paths are not provided; install `onnxruntime-gpu` and pass `--device cuda` for `CUDAExecutionProvider` when available (**Reported**).[^kokoro-vi-readme]
- Self-export: `kokoro-vietnamese-export-onnx --output outputs/kokoro_vi.onnx` (**Reported**).[^kokoro-vi-readme]
- Vietnamese G2P is handled by `vig2p`, stated to match the GitHub inference and training code (**Reported**).[^kokoro-vi-readme]
- No latency, RTF, TTFA, quality (MOS/WER/SIM), streaming/chunking, or concurrency figures are stated in the capture (**Observed** absence).[^kokoro-vi-readme]

## Relationships

- Catalogued by [TTS Model Survey](tts-model-survey.md) as a fine-tuned single-language artifact set alongside the multilingual catalog, not as a ranked streaming or fidelity contender (**Synthesis**).[^kokoro-vi-readme]
- Vietnamese-deployment comparison: [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) covers a Vietnamese-first on-device family with preset voices, OpenAI-compatible streaming, and RTX 3060 plus CPU benchmark tables, while this concept covers a Vietnamese Kokoro fine-tune with PyTorch/ONNX CLIs, voicepacks, and `vig2p` G2P but no published benchmarks or streaming figures; no shared codebase beyond the Kokoro lineage implied by the `KModel`/`config.json` naming is asserted (**Synthesis**).[^kokoro-vi-readme]
- Retrieval pointer, not a verified checkpoint match: [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) shortlists Vietnamese realtime options with evidence gates this capture does not meet (no quality, latency, or streaming evidence), so this concept is a pending unevaluated option relative to that shortlist (**Synthesis**).[^kokoro-vi-readme]
- Kokoro-name retrieval pointers only, with no shared-checkpoint claim: [Speaches](speaches.md) serves Piper and Kokoro (`hexgrad/Kokoro-82M`) behind an OpenAI-compatible API, [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) lists Kokoro-82M among its TTS backends, and [RealtimeVoiceChat](realtime-voice-chat.md) offers Kokoro via RealtimeTTS; the upstream Kokoro-82M weights have no primary-source concept in this wiki (**Synthesis**).[^kokoro-vi-readme]

## Coverage and limits

- Source inspected statically only as the single `raw/Kokoro-Vietnamese.md` README capture; no repository cloned, no package installed, no checkpoint or voicepack downloaded, no audio synthesized, and no install, inference, phoneme-print, or export command executed (**Observed**).[^kokoro-vi-readme]
- Material linked artifacts were not in `raw/` and were not inspected: `kokoro_vi.pth`, `kokoro_vi.onnx`, `kokoro_vi_voicepack.pt`, `config.json`, `voicepacks/*.pt`, the `vig2p` package and its phoneme inventory, the upstream `https://github.com/iamdinhthuan/Kokoro-Vietnamese` repository, training code and data, and any demo audio (**Synthesis**).[^kokoro-vi-readme]
- All capability, compatibility, voice-quality, performance, and licensing claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^kokoro-vi-readme]

[^kokoro-vi-readme]: [Kokoro Vietnamese README capture](../raw/Kokoro-Vietnamese.md) — locators: frontmatter (`language: vi`, `pipeline_tag: text-to-speech`, `tags: kokoro/vietnamese/text-to-speech/onnx`, `license: apache-2.0`); `## Files` (`kokoro_vi.pth` KModel checkpoint, `kokoro_vi.onnx` acoustic-model export, `kokoro_vi_voicepack.pt` default voicepack, `config.json` config/vocab, `voicepacks/*.pt` additional voicepacks); `## Install` (`git clone https://github.com/iamdinhthuan/Kokoro-Vietnamese.git`, `pip install -e .`, `pip install -e ".[onnx]"`); `## PyTorch Inference` (`kokoro-vietnamese --text/--output/--voice diem_trinh/--device cuda` fence); `## ONNX Runtime Inference` (`kokoro-vietnamese-onnx --text/--output/--device cpu/--print-phonemes` fence, auto-download of onnx/voicepack/config, `onnxruntime-gpu` plus `--device cuda` for CUDAExecutionProvider); `## Export ONNX Yourself` (`kokoro-vietnamese-export-onnx --output` fence); closing line (Vietnamese G2P by `vig2p`, matching GitHub inference and training code).
