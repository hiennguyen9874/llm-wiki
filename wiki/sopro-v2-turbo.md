---
type: Concept
title: Sopro V2 Turbo
description: 120M-parameter multilingual zero-shot voice-cloning TTS with ~300 ms streaming time-to-first-audio on laptop CPU, M3/H100 RTF figures, and PyTorch plus ONNX browser runtimes.
tags: [tts, streaming, voice-cloning, on-device, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: sopro-v2-card
    resource: ../raw/sopro-v2-turbo.md
    kind: documentation
    title: Sopro TTS README and Hugging Face model card (sopro-v2-turbo)
---

Sopro V2 Turbo (`sopro-v2-turbo`) is Samuel Vitorino's lightweight 120M-parameter open voice-cloning text-to-speech model family member covering English, European Portuguese, French, and German, reporting about 300 ms time-to-first-audio when streaming on a laptop CPU, 0.24 real-time factor offline and 0.21 streaming on an M3 CPU and 0.07 on an H100, zero-shot cloning from 5–20 seconds of reference audio, and PyTorch plus in-browser ONNX runtimes (**Reported**).[^sopro-v2-card]

## Model identity and release

- Name is Sopro, from the Portuguese word for "breath/blow"; this snapshot covers `sopro-v2-turbo`; links listed are the blog post `https://research.haloneuro.ai/posts/sopro-v2`, GitHub `https://github.com/samuel-vitorino/sopro`, and in-browser demo `https://samuel-vitorino.github.io/sopro/` (**Reported**).[^sopro-v2-card]
- Frontmatter declares `license: apache-2.0`, `language: en, pt, fr, de`, `pipeline_tag: text-to-speech`, `tags: tts, voice-cloning, streaming, on-device`, and `library_name: sopro` (**Observed** by static inspection).[^sopro-v2-card]
- Compatibility note states current model artifacts require `sopro>=2.2.0` or `@soprotts/onnx-web>=0.3.0`, upgraded with `pip install -U sopro` or `npm install @soprotts/onnx-web@latest` (**Reported**).[^sopro-v2-card]
- Pretrained checkpoint ID used in the Python examples is `samuel-vitorino/sopro-v2-turbo` (**Reported**).[^sopro-v2-card]

## Capabilities and performance

- 120M parameters; four supported languages (English, European Portuguese, French, German); streaming synthesis; zero-shot voice cloning from 5–20 seconds of reference audio (**Reported**).[^sopro-v2-card]
- Latency claim is about 300 ms time-to-first-audio on a laptop CPU; throughput claims are 0.24 RTF offline and 0.21 RTF streaming on an M3 CPU and 0.07 RTF on an H100 (**Reported**).[^sopro-v2-card]
- Runs on a laptop CPU and in the browser via an ONNX runtime; the source claims SOTA-level intelligibility against much larger systems with the full evaluations and audio samples deferred to the linked blog post, which is not in `raw/` (**Reported**, with deferral **Synthesis**).[^sopro-v2-card]

## Requirements and installation

- From PyPI with `pip install -U sopro`; from the repo with `git clone https://github.com/samuel-vitorino/sopro`, `cd sopro`, `pip install -e .` (**Reported**).[^sopro-v2-card]
- Local demo starts with `uvx --from sopro soprotts serve`, or `soprotts serve` when already installed, then opens `http://localhost:7860`; the model downloads on first use into the Hugging Face cache; device selection is automatic CUDA-or-CPU with CPU default on macOS and explicit `--device mps` for MPS; `soprotts serve --help` covers model, device, port, and CPU int8 options (**Reported**).[^sopro-v2-card]
- Browser demo at `https://samuel-vitorino.github.io/sopro/` runs fully in-browser with no server; on mobile the model is quantized so results can sit slightly below the local demo, and low-memory devices may crash; the dependency-isolated ONNX runtime and exporter are documented in `web/README.md`, and both demos use the frontend in `demos/web` (**Reported**).[^sopro-v2-card]

## Inference usage

- CLI form is `soprotts "<text>" --ref ref.wav --out out.wav`; add `--stream` for the streaming path; sampling controls are `--temperature`, `--top-p`, and `--top-k` (**Reported**).[^sopro-v2-card]
- Additional CLI options are `--lang` (`en`, `pt`, `fr`, `de`; optional, helps pronunciation on ambiguous text), `--int8` (int8 autoregressive weights on CPU), `--steps` (acoustic solver steps; default 2), and `--max-seconds` (cap per generated segment; long text is split into segments so total length is unbounded) (**Reported**).[^sopro-v2-card]
- Non-streaming Python loads with `SoproTTS.from_pretrained("samuel-vitorino/sopro-v2-turbo", device="cpu")`, synthesizes with `tts.synthesize("<text>", ref_audio_path="ref.wav")`, and writes with `tts.save_wav("out.wav", wav)` (**Reported**).[^sopro-v2-card]
- Streaming Python iterates `tts.stream("<text>", ref_audio_path="ref.mp3")`, collects CPU chunks, concatenates with `torch.cat`, and writes with `tts.save_wav`; reference audio can be precalculated with `tts.prepare_reference(ref_audio_path="ref.mp3", stream=True)` and passed as `ref=ref` to reduce time-to-first-audio (**Reported**).[^sopro-v2-card]

## Limitations and responsible use

- No watermarking is added; the source states watermarking an open-source inference pipeline would be trivially removable and would only provide a false sense of safety, and asks users not to impersonate people (**Reported**).[^sopro-v2-card]
- Minimal text frontend: some abbreviations, numbers, and symbols may be mispronounced, so the source recommends writing words out (`1 + 2` as `one plus two`); common abbreviations like "CPU" or "TTS" are stated to read fine, and a language-specific normalizer can be placed in front (**Reported**).[^sopro-v2-card]
- Mixed-language text is a weak spot: words from one language inside a sentence of another (for example an English product name in a Portuguese sentence) can be mispronounced (**Reported**).[^sopro-v2-card]
- The streaming path (chunked attention plus causal vocoder) is not bit-exact with the offline path; for best quality the source recommends the offline path (**Reported**).[^sopro-v2-card]
- Training code release is not planned in the near future due to its complexity (**Reported**).[^sopro-v2-card]

## Training data and lineage

- Training data listed is Emilia YODAS, LibriTTS-R, and FalAR, each with a Hugging Face dataset link in the source (**Reported**).[^sopro-v2-card]
- Acknowledgements list CSM, F5-TTS, CosyVoice, Vocos, and Whisper with repository links (**Reported**).[^sopro-v2-card]

## Relationships

- CPU streaming TTS comparison: [Pocket TTS](pocket-tts.md) covers a 100M-parameter CPU-first multilingual TTS system with ~200 ms first-chunk streaming and Python/CLI/serve interfaces, while this concept covers a 120M-parameter four-language zero-shot cloning TTS model with ~300 ms TTFA and PyTorch plus browser ONNX runtimes; no shared codebase is asserted (**Synthesis**).[^sopro-v2-card]
- On-device TTS comparison: [Supertonic 2](supertonic-2.md) covers a 66M-parameter on-device multilingual TTS model with an ONNX runtime and five-language coverage, while this concept covers a larger 120M-parameter cloning-capable TTS model with M3/H100 RTF figures and a quantized mobile browser path; no shared vendor or codebase is asserted (**Synthesis**).[^sopro-v2-card]
- Small cloning-model comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B multilingual zero-shot TTS model with a 44.1 kHz neural codec and an ONNX INT4 CPU path, while this concept covers a smaller 120M-parameter four-language cloning TTS model with laptop-CPU streaming and int8 AR CPU weights; no shared vendor or codebase is asserted (**Synthesis**).[^sopro-v2-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no time-to-first-audio, real-time-factor, intelligibility, language-quality, cloning-quality, or memory claims reproduced (**Synthesis**).[^sopro-v2-card]
- Banner image, blog post, GitHub repository, Hugging Face checkpoint, local and browser demos, `web/README.md`, `demos/web` frontend, training datasets, and acknowledged repositories were linked but not fetched and are not in `raw/`; checkpoint, tokenizer, acoustic-solver, vocoder, and audio contents were not inspected (**Synthesis**).[^sopro-v2-card]
- All capability, performance, compatibility, serving, and training-data claims are source assertions without independent verification in this wiki; latency, throughput, and release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^sopro-v2-card]
- No Seed-TTS-eval or other numeric intelligibility, similarity, or benchmark table is present in this source; only the headline latency/RTF figures above are recorded (**Synthesis**).[^sopro-v2-card]

[^sopro-v2-card]: [Sopro TTS README and Hugging Face model card (sopro-v2-turbo)](../raw/sopro-v2-turbo.md) — locators: frontmatter (`license: apache-2.0`, `language: en, pt, fr, de`, `pipeline_tag: text-to-speech`, `tags`, `library_name: sopro`); compatibility callout (`sopro>=2.2.0`, `@soprotts/onnx-web>=0.3.0`); `Main features` bullets (120M, 4 languages, ~300 ms TTFA laptop CPU, 5–20 s cloning, 0.24/0.21 M3 and 0.07 H100 RTF, browser ONNX, SOTA-intelligibility claim with blog pointer); `Local demo` section (`uvx --from sopro soprotts serve`, `soprotts serve`, `localhost:7860`, HF cache, CUDA/CPU auto with macOS CPU default and `--device mps`, `--help`); `Browser demo` section (in-browser URL, mobile-quantization and low-memory caveats, `web/README.md`, `demos/web`); `Installation` section (PyPI and repo fences); `Examples / CLI` section (`soprotts ... --ref/--out` fence, `--stream`, `--temperature/--top-p/--top-k`, `--lang/--int8/--steps/--max-seconds` bullets); `Examples / Python` section (non-streaming `synthesize`, streaming `stream`, `prepare_reference` fences with `samuel-vitorino/sopro-v2-turbo`); `Disclaimers` section (no-watermarking, minimal-frontend with `1 + 2` example, mixed-language, non-bit-exact streaming, no-training-code bullets); `Training data` section (Emilia YODAS, LibriTTS-R, FalAR links); `Acknowledgements` section (CSM, F5-TTS, CosyVoice, Vocos, Whisper links).
