---
type: Concept
title: MOSS-TTS-Nano
description: 0.1B-parameter multilingual zero-shot voice-cloning TTS model with autoregressive Audio Tokenizer plus LLM architecture, 48 kHz stereo output, 20-language coverage, and PyTorch plus ONNX CPU streaming paths.
tags: [tts, multilingual, voice-cloning, streaming, cpu, onnx]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: moss-tts-nano-readme
    resource: ../raw/MOSS-TTS-Nano.md
    kind: documentation
    title: MOSS-TTS-Nano README
---

MOSS-TTS-Nano is OpenMOSS/MOSI.AI's open-source 0.1B-parameter multilingual speech-generation model for realtime use, using a pure autoregressive Audio Tokenizer plus LLM pipeline with 48 kHz 2-channel output, zero-shot voice cloning, streaming inference, long-text chunked cloning, and PyTorch plus ONNX CPU deployment paths including a CLI, local web demo, Android example, and browser-reader build (**Reported**).[^moss-tts-nano-readme]

## Model identity and release

- Title is `MOSS-TTS-Nano`; creators are MOSI.AI and the OpenMOSS team; upstream repository is `https://github.com/OpenMOSS/MOSS-TTS-Nano`; weights are `OpenMOSS-Team/MOSS-TTS-Nano` (Hugging Face) and `openmoss/MOSS-TTS-Nano` (ModelScope); demos are the GitHub Pages demo and the `OpenMOSS-Team/MOSS-TTS-Nano` Hugging Face Space (**Reported**).[^moss-tts-nano-readme]
- Release timeline in the source News section: 2026.4.10 initial release with demo Space; 2026.4.14 `MOSS-TTS-Nano-Reader` browser reading app; 2026.4.16 finetuning code; 2026.4.17 standalone ONNX CPU version plus Reader-as-browser-extension; 2026.4.27 updated `MOSS-Audio-Tokenizer-Nano` evaluation; 2026.4.29 MOSS-TTS 2.0 announcement with feedback form; 2026.5.6 `mlx-audio` support (**Reported**).[^moss-tts-nano-readme]
- Architecture is described as pure autoregressive Audio Tokenizer plus LLM; output is native 48 kHz 2-channel audio; the model card emphasizes small footprint, low latency, fast first audio, and simple local setup (**Reported**).[^moss-tts-nano-readme]
- Default checkpoints loaded by the code are `OpenMOSS-Team/MOSS-TTS-Nano` and `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano` (**Reported**).[^moss-tts-nano-readme]

## Capabilities and constraints

- Tiny size of 0.1B parameters; streaming inference with low realtime latency and fast first audio; CPU-friendly streaming generation on a 4-core CPU; long-text input via automatic chunked voice cloning (**Reported**).[^moss-tts-nano-readme]
- Main recommended workflow is voice-clone mode from a reference audio prompt; built-in voices and realtime streaming decode are listed as supported in the ONNX path (**Reported**).[^moss-tts-nano-readme]
- Install path is a clean Python 3.12 environment (Conda example), `pip install -r requirements.txt`, and `pip install -e .` to expose the `moss-tts-nano` command; known setup friction is documented for `WeTextProcessing`/`pynini`, with a Conda-forge `pynini=2.1.6.post1` plus `git+https://github.com/WhizZest/WeTextProcessing.git` workaround and a pointer to community-tested Issue #6 for non-Conda wheels (**Reported**).[^moss-tts-nano-readme]
- Server GPU path is explicitly out of this source's scope and delegated to the vLLM-Omni MOSS-TTS-Nano README (paged KV cache, streaming, OpenAI-compatible `/v1/audio/speech` endpoint), which was linked but not ingested here (**Reported**, with pointer limit **Synthesis**).[^moss-tts-nano-readme]

## Supported languages

20 languages by code: Chinese (zh), English (en), German (de), Spanish (es), French (fr), Japanese (ja), Italian (it), Hungarian (hu), Korean (ko), Russian (ru), Persian/Farsi (fa), Arabic (ar), Polish (pl), Portuguese (pt), Czech (cs), Danish (da), Swedish (sv), Greek (el), and Turkish (tr) (**Reported**).[^moss-tts-nano-readme]

## PyTorch inference and serving

- Voice clone: `python infer.py --prompt-audio-path assets/audio/zh_1.wav --text "..."`; default output is `generated_audio/infer_output.wav` (**Reported**).[^moss-tts-nano-readme]
- Local web demo: `python app.py`, then open `http://127.0.0.1:18083` (**Reported**).[^moss-tts-nano-readme]
- Packaged CLI after `pip install -e .`: `moss-tts-nano generate --prompt-speech assets/audio/zh_1.wav --text "..."` writes `generated_audio/moss_tts_nano_output.wav` by default; `--prompt-speech` is the friendly alias for the reference-audio path and `--text-file` is supported for long-form synthesis; `moss-tts-nano serve` forwards to the web app, keeps the model in memory, and serves the browser demo plus HTTP generation endpoints (**Reported**).[^moss-tts-nano-readme]
- Finetuning is delegated to `./finetuning/README.md`, which was linked but not present in `raw/` and not ingested here (**Reported**, with coverage limit **Synthesis**).[^moss-tts-nano-readme]

## ONNX CPU deployment

- The source strongly recommends the ONNX CPU version first for lightweight local deployment: no PyTorch dependency at inference (ONNX Runtime CPU), fully standalone CPU deployment, feature-complete cloning workflow (reference audio, built-in voices, realtime streaming decode), nearly 2x processing efficiency versus the original in the authors' tests, and smooth inference on 1 CPU core of a MacBook Air M4 (**Reported**).[^moss-tts-nano-readme]
- ONNX entrypoints are `infer_onnx.py`, `app_onnx.py`, and the packaged CLI with `--backend onnx`; default execution provider is CPU (`--execution-provider cpu`); NVIDIA CUDA is opt-in via `--execution-provider cuda` with `onnxruntime-gpu>=1.20.0` (installed by replacing the CPU `onnxruntime` wheel); without that flag ONNX inference stays CPU-only (**Reported**).[^moss-tts-nano-readme]
- ONNX weights default to `./models` and auto-download on first run from `OpenMOSS-Team/MOSS-TTS-Nano-100M-ONNX` and `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX` into `models/MOSS-TTS-Nano-100M-ONNX` and `models/MOSS-Audio-Tokenizer-Nano-ONNX`; an alternate directory is passed with `--model-dir`; first startup may spend extra time downloading (**Reported**).[^moss-tts-nano-readme]
- Example: `python infer_onnx.py --prompt-audio-path assets/audio/zh_1.wav --text "..."`; CUDA variant adds `--execution-provider cuda`; ONNX web demo is `python app_onnx.py` (same port `http://127.0.0.1:18083`) with an optional `--execution-provider cuda` flag (**Reported**).[^moss-tts-nano-readme]
- CLI equivalents: `moss-tts-nano generate --backend onnx --prompt-speech ... --text ...` and `moss-tts-nano serve --backend onnx`, each with an optional `--execution-provider cuda` (**Reported**).[^moss-tts-nano-readme]
- Retraining support: the exporter under `onnx/` (`python onnx/export_hf_to_tts_onnx.py --checkpoint-path /path/to/MOSS-TTS-Nano --output-dir /path/to/MOSS-TTS-Nano-100M-ONNX`) converts a local Hugging Face-format checkpoint into a TTS-only ONNX directory (`moss_tts_prefill.onnx`, `moss_tts_decode_step.onnx`, `moss_tts_local_decoder.onnx`, `moss_tts_local_cached_step.onnx`, `moss_tts_local_fixed_sampled_frame.onnx`, `moss_tts_global_shared.data`, `moss_tts_local_shared.data`, `tts_browser_onnx_meta.json`, `tokenizer.model`); existing prompt-audio codes from a fixed `MOSS-Audio-Tokenizer-Nano` do not need regeneration (**Reported**).[^moss-tts-nano-readme]
- Adjacent ONNX consumers named in the source but not ingested here: the `examples/android_onnx_runtime` on-device smoke example (loads the Nano ONNX graphs plus tokenizer decoder, synthesizes short pre-tokenized prompts, writes WAV; model files kept outside the APK) and the `MOSS-TTS-Nano-Reader` browser extension build on the ONNX CPU version (**Reported**, with coverage limit **Synthesis**).[^moss-tts-nano-readme]

## MOSS-Audio-Tokenizer-Nano

- Role: the unified discrete audio interface and shared backbone for the MOSS-TTS family (MOSS-TTS, MOSS-TTS-Nano, MOSS-TTSD, MOSS-VoiceGenerator, MOSS-SoundEffect, MOSS-TTS-Realtime); built on the Cat (Causal Audio Tokenizer with Transformer) architecture, described as CNN-free and composed entirely of causal Transformer blocks (**Reported**).[^moss-tts-nano-readme]
- Nano variant: about 20M parameters; 48 kHz input/output plus stereo; compresses 48 kHz stereo into a 12.5 Hz token stream using RVQ with 16 codebooks across variable bitrates 0.125–2 kbps (**Reported**).[^moss-tts-nano-readme]
- Reconstruction-quality claim: best overall among open-source tokenizers with no more than 120M parameters across speech (LibriSpeech test-clean EN plus AISHELL-2 ZH), audio (AudioSet subset), and music (MUSDB) data, illustrated by an evaluation table and LibriSpeech bitrate plots (SIM, STOI, PESQ-NB/WB; higher is better for speech metrics, lower Mel-Loss/STFT-Dist. is better for audio/music); the source notes channel (`ch=1` mono vs `ch=2` stereo) and quantizer-count (`Nvq`) conventions and that bitrate is controlled by RVQ codebook count at inference (**Reported**).[^moss-tts-nano-readme]
- Weights: `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano` on Hugging Face and `openmoss/MOSS-Audio-Tokenizer-Nano` on ModelScope, plus `-ONNX` variants for the CPU path; setup and metric detail is delegated to the separate MOSS-Audio-Tokenizer repository, not ingested here (**Reported**, with pointer limit **Synthesis**).[^moss-tts-nano-readme]

## MOSS-TTS family context

The source positions Nano inside the MOSS-TTS family (high-fidelity, high-expressiveness, complex real-world scenarios: long-form speech, multi-speaker dialogue, voice/character design, sound effects, realtime streaming TTS) with six released siblings, all with Hugging Face and ModelScope weights (**Reported**):[^moss-tts-nano-readme]

| Model | Architecture | Size |
| --- | --- | ---: |
| MOSS-TTS (flagship zero-shot cloning, long speech, Pinyin/phoneme/duration control, multilingual/code-switch) | `MossTTSDelay` | 8B |
| MOSS-TTS-Local-Transformer (`MossTTSLocal`, lighter MOSS-TTS style) | `MossTTSLocal` | 1.7B |
| MOSS-TTSD-v1.0 (expressive multi-speaker ultra-long dialogue) | `MossTTSDelay` | 8B |
| MOSS-VoiceGenerator (text-prompt voice design, no reference speech) | `MossTTSDelay` | 1.7B |
| MOSS-SoundEffect (ambience, city, animals, actions, short music-like fragments) | `MossTTSDelay` | 8B |
| MOSS-TTS-Realtime (low-latency voice agents, turn-consistent voice) | `MossTTSRealtime` | 1.7B |

## License and citation

- License section states the repository will follow the root `LICENSE` file and, if read before that file is published, must be treated as **not yet licensed for redistribution** (**Observed** by static inspection of the License section).[^moss-tts-nano-readme]
- Citation block requests three BibTeX entries: `openmoss2026mossttsnano` (MOSS-TTS-Nano GitHub repository), `gong2026mossttstechnicalreport` (MOSS-TTS Technical Report, arXiv:2603.18090), and `gong2026mossaudiotokenizerscalingaudiotokenizers` (MOSS-Audio-Tokenizer, arXiv:2602.10934); full author lists and URLs are in the source and abbreviated here as non-durable bibliographic detail (**Reported**, with omission **Synthesis**).[^moss-tts-nano-readme]

## Relationships

- GGUF packaging: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs a `MOSS-TTS-Nano-100M-GGUF` package (`moss_tts_nano` family, BF16 + Q8, Apache-2.0) for the audio.cpp runtime, while this concept covers the upstream PyTorch/ONNX source release, usage, and tokenizer/family context; the packaging row is source-reported in that catalog and was not re-verified here (**Synthesis**).[^moss-tts-nano-readme]
- CPU TTS comparison: [Pocket TTS](pocket-tts.md) covers a 100M-parameter CPU-first TTS system with ~200 ms first-chunk streaming and ~6x real-time on MacBook Air M4 (2 cores), while this concept covers a 0.1B-parameter CPU-friendly TTS model with 4-core streaming and a 1-core M4 ONNX path at ~2x efficiency; no shared codebase is asserted (**Synthesis**).[^moss-tts-nano-readme]
- Compact multilingual TTS comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B DualAR zero-shot cloning model with 44.1 kHz codec, 11 recommended languages, and ONNX INT4 CPU plus SGLang Omni paths, while this concept covers a smaller 0.1B autoregressive tokenizer-plus-LLM model with 48 kHz stereo, 20 languages, and ONNX Runtime CPU/CUDA plus vLLM-Omni pointers; no shared vendor or codebase is asserted (**Synthesis**).[^moss-tts-nano-readme]
- Streaming TTS comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B LLM-based streaming zero-shot TTS model with vLLM/streaming inference, while this concept covers a 0.1B streaming TTS model with chunked long-text cloning and an ONNX single-core CPU path; no shared vendor or codebase is asserted (**Synthesis**).[^moss-tts-nano-readme]
- Same-vendor transcription runtime: [MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)](moss-transcribe-cpp-gguf.md) covers a MOSS transcription/diarization GGUF runtime, while this concept covers the MOSS speech-synthesis side and its Nano audio tokenizer; no shared checkpoint is asserted (**Synthesis**).[^moss-tts-nano-readme]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no model or ONNX weights downloaded, no audio synthesized, and no latency, efficiency (~2x), single-core usability, or reconstruction-quality claims reproduced (**Synthesis**).[^moss-tts-nano-readme]
- `finetuning/README.md`, `onnx/` exporter code, `examples/android_onnx_runtime`, `assets/` images and audio, the demo video, the vLLM-Omni serving README, the MOSS-Audio-Tokenizer repository, Hugging Face/ModelScope weight contents, online demos and Spaces, API docs, arXiv papers, mlx-audio integration, Reader repositories, and social/community links (X, Discord, WeChat, star-history) were linked but not fetched and are not in `raw/`; checkpoint, tokenizer, ONNX graph, and safetensors contents were not inspected (**Synthesis**).[^moss-tts-nano-readme]
- All capability, compatibility, performance, benchmark-ranking, and serving claims are upstream assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^moss-tts-nano-readme]
- License-redistribution status reflects the source's own License section at capture time and may have changed upstream (**Synthesis**).[^moss-tts-nano-readme]

[^moss-tts-nano-readme]: [MOSS-TTS-Nano README](../raw/MOSS-TTS-Nano.md) — locators: header badges (Hugging Face, ModelScope, demo, arXiv:2603.18090, AIStudio try/API docs, X, Discord, WeChat); intro paragraph (0.1B, realtime, CPU, local demos/web/product); `Start here` line (demo, quickstart, ONNX, weights, finetuning); `News` section (2026.5.6 mlx-audio; 2026.4.29 2.0 feedback form; 2026.4.27 tokenizer eval; details: 2026.4.17 ONNX CPU + Reader extension, 2026.4.16 finetuning, 2026.4.14 Reader, 2026.4.10 release/Space); `Demo` section (Pages + Space URLs); `Introduction` + `Main Features` (footprint/latency/quality/setup, 0.1B, 48 kHz 2-channel, multilingual, AR tokenizer+LLM, streaming, 4-core CPU, chunked long-text, `infer.py`/`app.py`/CLI); `Supported Languages` 20-row table; `Quickstart/Environment Setup` (conda python=3.12, clone, requirements, editable install, `pynini`/`WeTextProcessing` workaround, Issue #6); `Voice Clone with infer.py` fence + `generated_audio/infer_output.wav`; `Local Web Demo with app.py` fence + `http://127.0.0.1:18083`; `ONNX CPU Inference` section (recommendation, no-PyTorch, standalone, cloning/streaming, ~2x, 1-core M4 Air; `infer_onnx.py`/`app_onnx.py`/CLI `--backend onnx`; `--execution-provider cpu/cuda` fences; `onnxruntime-gpu>=1.20.0` swap; auto-download repos + `models/` paths; `--model-dir` fence); `ONNX Local Web Demo`, `Android ONNX Runtime Example`, `Export TTS-only ONNX Weights` (`onnx/export_hf_to_tts_onnx.py` fence, 9-file output list, prompt-code note), `moss-tts-nano generate` (`--prompt-speech` alias, `--text-file`, output path, backend/provider fences), `moss-tts-nano serve` (backend/provider fences, in-memory/demo+HTTP note, vLLM-Omni pointer); `Finetuning` pointer; `MOSS-Audio-Tokenizer-Nano/Introduction` (unified interface, 6-model family list, Cat/CNN-free, ~20M, 48 kHz stereo, 12.5 Hz, RVQ-16, 0.125–2 kbps) + `Model Weights` table + `Evaluation Metrics`/`LibriSpeech` paragraphs (≤120M comparison, EN/ZH + audio/music splits, SIM/STOI/PESQ, Mel-Loss/STFT-Dist., ch/Nvq, bitrate-by-codebooks) + table/figure images; `MOSS-TTS Family/Introduction` + `Released Models` 6-row table (architectures, sizes, HF/ModelScope); `License` section (LICENSE-file/not-yet-licensed paragraph); `Citation` BibTeX block (3 entries); `Star History` chart.
