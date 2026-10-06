---
type: Concept
title: Pocket TTS
description: Lightweight 100M-parameter CPU-first multilingual TTS system with ~200 ms first-chunk streaming, ~6x real-time on MacBook Air M4, and Python, CLI, and local-server synthesis with voice cloning.
tags: [tts, cpu, streaming, multilingual, voice-cloning]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T16:35:00Z }
stale_after: 2027-10-06
sources:
  - id: pocket-tts-doc
    resource: ../raw/pocket-tts-without-voice-cloning.md
    kind: documentation
    title: Pocket TTS README and Hugging Face model card
  - id: pocket-tts-repo
    resource: ../raw/pocket-tts-repo.md
    kind: documentation
    title: Pocket TTS GitHub repository README
---

Pocket TTS is Kyutai's lightweight 100M-parameter text-to-speech system designed for CPU inference, reporting about 200 ms to the first audio chunk, about 6x real-time synthesis on a MacBook Air M4 using 2 CPU cores, streaming output, effectively unbounded input length, seven supported languages with Dutch added in the repo snapshot, and Python, CLI, and local-server interfaces with voice cloning (**Reported**).[^pocket-tts-doc][^pocket-tts-repo]

## Model identity and release

- Title is `Pocket TTS`; creator is Kyutai; links listed are demo `https://kyutai.org/pocket-tts`, GitHub `https://github.com/kyutai-labs/pocket-tts`, Hugging Face `kyutai/pocket-tts`, tech report `https://kyutai.org/blog/2026-01-13-pocket-tts`, paper `https://arxiv.org/abs/2509.06926`, and documentation `https://kyutai-labs.github.io/pocket-tts/` (**Reported**).[^pocket-tts-doc]
- Frontmatter declares `license: cc-by-4.0`, languages `en, fr, de, pt, it, es`, `library_name: pocket-tts`, plus gated fields `Company or university if applicable` and `I want to use this model for` with options `Work`, `Studies`, `Fun` (**Observed** by static inspection).[^pocket-tts-doc]
- Authors are Manu Orsini, Simon Rouard, Gabriel De Marmiesse, Václav Volhejn, Neil Zeghidour, and Alexandre Défossez, with equal contribution noted for the first three (**Reported**).[^pocket-tts-doc]
- Training code was released in August 2026 under `training/`, with community models accepted by pull request into the models list (**Reported**).[^pocket-tts-doc]

## Capabilities and performance

- Runs on CPU without requiring the GPU build of PyTorch; supports Python 3.10 through 3.14 and requires PyTorch 2.5+ (**Reported**).[^pocket-tts-doc]
- Small model size of 100M parameters; audio streaming; low latency of about 200 ms to the first audio chunk; faster than real-time at about 6x on a MacBook Air M4 CPU using only 2 CPU cores (**Reported**).[^pocket-tts-doc]
- Multi-language support for English, French, German, Portuguese, Italian, and Spanish in the earlier card snapshot, plus Dutch in the repo snapshot for seven languages; additional languages may be added in the future (**Reported**).[^pocket-tts-doc][^pocket-tts-repo]
- Handles infinitely long text inputs and can run client-side in the browser through community WebAssembly/JavaScript ports (**Reported**).[^pocket-tts-doc]
- Unsupported at the time of writing: inserting silence in the text input to generate pauses, tracked as upstream issue `#6` (**Reported**).[^pocket-tts-doc]

## Requirements and installation

- Install with `pip install pocket-tts` or `uv add pocket-tts`; try without installing with `uvx pocket-tts generate` (**Reported**).[^pocket-tts-doc]
- On Linux, the default PyPI torch is the CUDA build and pulls multi-gigabyte `nvidia-*` runtime wheels despite CPU-only inference (about 3 GB instead of 200 MB with torch 2.13); use `pip install pocket-tts --extra-index-url https://download.pytorch.org/whl/cpu`, `uvx --index https://download.pytorch.org/whl/cpu pocket-tts generate`, or a `uv` project index named `pytorch-cpu` with `torch` sourced from it; not needed on macOS or Windows where default wheels are already CPU-only (**Reported**).[^pocket-tts-doc]

## Inference usage

- `generate` CLI writes `./tts_output.wav` with default text and voice plus speed statistics; `--voice` selects a catalog voice and `--text` sets the input; `--language` selects the pretrained language model (default `english`), with larger slower 24-layer variants for non-English languages selected as e.g. `--language italian_24l`; `--config` accepts a local YAML path, `https://` URL, or `hf://<repo_id>/<path>[@revision]` for custom weights (**Reported**).[^pocket-tts-doc] `--language english_drifting_26-09` in the repo snapshot selects an English model whose sampler head was trained with drifting instead of LSD, with the recipe in `training/README.md` (**Reported**).[^pocket-tts-repo]
- `serve` CLI runs a local server with a web interface at `http://localhost:8000`, keeping the model in memory between requests and therefore faster than repeated CLI calls for multiple voices and prompts (**Reported**).[^pocket-tts-doc]
- `export-voice` CLI converts a slow-to-process audio file into a fast-loading safetensors voice embedding; loading the safetensors file only reads the KV cache from disk without further computation (**Reported**).[^pocket-tts-doc]
- Python library loads with `TTSModel.load_model()`, builds a voice state with `get_state_for_audio_prompt()` from a catalog name, local wav, or `hf://` voice path, synthesizes with `generate_audio(voice_state, text)` returning a 1D torch tensor of PCM at `tts_model.sample_rate`, and writes with `scipy.io.wavfile.write`; `load_model()` and `get_state_for_audio_prompt()` are relatively slow so model and voice states should be kept in memory, with multiple voice states allowed; voice states can be exported with `export_model_state()` and reloaded from safetensors (**Reported**).[^pocket-tts-doc]
- Voice cloning passes any wav file to `--voice` or `get_state_for_audio_prompt()`; the source recommends cleaning the sample first because sample audio quality is reproduced; per-voice licenses are listed at `https://huggingface.co/kyutai/tts-voices` (**Reported**).[^pocket-tts-doc]
- Pre-made voice catalog in this snapshot includes `alba` (en), `giovanni` (it), `lola` (es), `juergen` (de), `rafael` (pt), `estelle` (fr), plus 20 English voices (`anna`, `azelma`, `bill_boerst`, `caro_davy`, `charles`, `cosette`, `eponine`, `eve`, `fantine`, `george`, `jane`, `jean`, `javert`, `marius`, `mary`, `michael`, `paul`, `peter_yearsley`, `stuart_bell`, `vera`); full sample URLs are in the source and omitted here as non-durable attachment detail (**Reported**, with omission **Synthesis**).[^pocket-tts-doc]

## GPU behavior

- Designed for CPU; on hardware with strong single-thread CPU performance such as Apple Silicon no GPU speedup was observed, attributed to batch size 1 and a very small model (**Reported**).[^pocket-tts-doc]
- Hardware-dependent exception measured on a cloud x86 VM with 4 vCPUs and a Tesla T4: moving the model to GPU gave a consistent about 2.6x speedup over CPU, with real-time factor about 2.3–2.5x on CPU versus about 6.28x on GPU for short and long inputs (**Reported**).[^pocket-tts-doc]
- GPU use is unofficial with no `device` argument on `TTSModel.load_model()`; move the `nn.Module` with `tts_model.to("cuda")` and move output back with `audio.detach().cpu().numpy()` before writing; only the `generate` CLI exposes `--device` (default `cpu`) while `serve` and Docker always run on CPU; a torch build newer than the driver CUDA makes `torch.cuda.is_available()` silently return `False` with only a `UserWarning`, fixed by installing a matching torch build such as the `cu121` index; `quantize=True` int8 dynamic quantization is CPU-only and raises `NotImplementedError` for the CUDA backend, and the optional `torchao` backend via `pip install pocket-tts[quantize]` requires `torch>=2.11` so pinning an older torch can break `quantize=True` even on CPU (**Reported**).[^pocket-tts-doc]

## Community models, ports, and projects

- Custom weights run with `--config`, e.g. `uvx pocket-tts generate --config https://raw.githubusercontent.com/.../english_2026-04.yaml` or `hf://user/repo/config_file.yaml@commit_hash`; pin a commit hash in the URL to avoid breaking changes; pre-made voice embeddings are computed with the released weights and unavailable for community models, so `--voice` defaults to the `alba` audio file and callers pass their own audio for other voices (**Reported**).[^pocket-tts-doc]
- Community-trained models: Czech by @vvolhejn, Hindi by Saryps Labs, Korean 300M by @seastar105, Persian/Farsi by @mallahyari, Indonesian 6-layer by @anak10thn, Estonian by @cbentes, Welsh/Cymraeg 24-layer by EryriLabs, and Polish 6-layer by @shefowl in the earlier snapshot, each with a pinned `--config` plus `--voice`/`--text` example in the source (**Reported**),[^pocket-tts-doc] plus Greek (Ελληνικά) 6-layer by Myned AI in the repo snapshot with a pinned `hf://myned-ai/pocket-tts-greek/greek.yaml` config and `eleni.wav` reference voice (**Reported**).[^pocket-tts-repo]
- In-browser implementations (no official support): `wasm-pocket-tts` Rust/XN port, `pocket-tts-onnx-export` ONNX Runtime Web, `pocket-tts` Candle Rust with WebAssembly and PyO3 bindings, and `jax-js` web ML library, each with a linked demo (**Reported**);[^pocket-tts-doc][^pocket-tts-repo] the repo snapshot moves the XN port links from `LaurentMazare/xn` paths to `gradium-ai/xn-ptts` (WASM demo under `ptts-wasm`) (**Reported**).[^pocket-tts-repo]
- Alternative runtimes: MLX backend for Apple Silicon, XN and Candle Rust ports, single-file C++ `PocketTTS.cpp` on ONNX Runtime with CLI/HTTP/FFI, `sherpa-onnx` for Windows/macOS/Linux and embedded boards with 12-language bindings plus WebAssembly, C# port on TorchSharp, timestamped fork with word-level timestamps, and LiteRT `.tflite` graphs running about 1x real-time on a Pixel 8a phone GPU with Python/Kotlin snippets (**Reported**).[^pocket-tts-doc][^pocket-tts-repo]
- Projects using Pocket TTS in the earlier snapshot include a browser screen reader, Wyoming-protocol Home Assistant container, Hogwarts Legacy character voices, native and Electron macOS apps, OpenAI-compatible streaming servers, Unity 6 integration, ComfyUI node, voice-cloning chat server, Discord bot, coding-agent commentary, Deno WASM/ONNX server, clipboard/hotkey front-end, OpenClaw OpenAI-TTS containers, audiobook generator, game accessibility tool with voice manager, and a local Mac conversational voice harness (**Reported**, with omission **Synthesis**);[^pocket-tts-doc] the repo snapshot adds Libratory (PDF read-along audiobooks with voice cloning from the picker) and ToBe SAID OS system-voice integration (Android/iOS/Mac/Windows) by @lookbe (**Reported**).[^pocket-tts-repo] Full repository links are in the sources and omitted here as non-durable directory detail (**Synthesis**).

## License and responsible use

- Hugging Face frontmatter license is `cc-by-4.0` with gated-use fields; per-voice licenses are cataloged separately at `https://huggingface.co/kyutai/tts-voices` (**Reported**).[^pocket-tts-doc]
- Prohibited uses stated in the source include voice impersonation or cloning without explicit and lawful consent, misinformation/disinformation/deception including fake news, fraudulent calls, or presenting generated content as genuine recordings, and unlawful, harmful, libelous, abusive, harassing, discriminatory, hateful, or privacy-invasive content; use must comply with applicable laws and the authors disclaim liability for non-compliant use (**Reported**).[^pocket-tts-doc]

## Relationships

- CPU TTS comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B multilingual zero-shot TTS model with DualAR architecture and an ONNX INT4 CPU path, while this concept covers a 100M-parameter CPU-first TTS system with ~200 ms first-chunk streaming and Python/CLI/serve plus edge-port coverage; no shared codebase is asserted (**Synthesis**).[^pocket-tts-doc]
- Streaming TTS comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B LLM-based streaming TTS model with saved-speaker reuse and vLLM/TRT-LLM serving, while this concept covers a smaller CPU streaming TTS model with 2-core M4 figures and unofficial T4 GPU behavior; no shared vendor or codebase is asserted (**Synthesis**).[^pocket-tts-doc]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice design/direction and H100 TTFA/RTF figures, while this concept covers a six-language CPU TTS model with first-chunk latency and browser/embedded ports; no shared vendor or codebase is asserted (**Synthesis**).[^pocket-tts-doc]

## Coverage and limits

- Source inspected statically only; no package installed, no model or voice file downloaded, no audio synthesized, and no latency, real-time-factor, memory, language-quality, or GPU-speedup claims reproduced (**Synthesis**).[^pocket-tts-doc]
- Logo image, demo site, GitHub repository, Hugging Face model and voices repositories, tech report, paper, documentation pages, training code, community model configs and reference voices, browser demos, alternative-implementation repositories, project repositories, and license/terms pages were linked but not fetched and are not in `raw/`; checkpoint, tokenizer, voice-embedding, and safetensors contents were not inspected (**Synthesis**).[^pocket-tts-doc]
- All capability, compatibility, performance, serving, and ecosystem claims are source assertions without independent verification in this wiki; latency, throughput, and release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^pocket-tts-doc]
- This update ingests `raw/pocket-tts-repo.md` by diff against `raw/pocket-tts-without-voice-cloning.md`: Hugging Face frontmatter (license, gated fields) appears only in the earlier file, while Dutch, the `english_drifting_26-09` sampler-head option, the Greek community model, the Libratory and ToBe SAID projects, and the `gradium-ai/xn-ptts` implementation links appear only in the repo file; all other overlapping claims reconciled as already covered (**Synthesis**).[^pocket-tts-doc][^pocket-tts-repo]

[^pocket-tts-doc]: [Pocket TTS README and Hugging Face model card](../raw/pocket-tts-without-voice-cloning.md) — locators: frontmatter (`license`, `language`, `extra_gated_prompt`, `extra_gated_fields`, `library_name`); header links (demo, GitHub, Hugging Face, tech report, paper, documentation); training-code note (August 2026); `Main takeaways` section (CPU, 100M, streaming, ~200 ms first chunk, ~6x M4, 2 cores, Python/CLI, voice cloning, 6-language list, unbounded input, browser); `Trying it from the website` section; `Trying it with the CLI` section (`generate`/`serve`/`export-voice` fences, `--voice`/`--text`/`--language`/`--config` paragraph, `italian_24l` example, voice-catalog bullets, cloning-wav paragraph, license page); `Using it as a Python library` section (install fences, `TTSModel`/`get_state_for_audio_prompt`/`generate_audio`/`export_model_state` fences, keep-in-memory note, API docs link); `CPU-only installation` section (CUDA-wheel size paragraph, pip/uvx/uv-toml fences); `Running on GPU` section (Apple Silicon no-speedup paragraph, T4 2.6x/RTF paragraph, `to("cuda")` fence, `--device`/serve/Docker, CUDA-driver, `quantize`/`torchao` bullets); `Unsupported features` section (silence issue `#6`); `In-browser implementations` and `Alterative implementations` sections (4 + 8 entries with demos); `Models trained by the community` section (`--config` fences, commit-hash advice, alba-default paragraph, 8 `<details>` models); `Projects using Pocket TTS` section (17 entries); `Prohibited use` section (full paragraph); `Authors` section (6 names).

[^pocket-tts-repo]: [Pocket TTS GitHub repository README](../raw/pocket-tts-repo.md) — locators: `Main takeaways` section (7-language list with Dutch); `Trying it with the CLI` section (`english_drifting_26-09` drifting-vs-LSD paragraph with `training/README.md` link); `Running on GPU` section (`docs/CLI Commands/generate.md` local CLI-reference link); `In-browser implementations` section (`gradium-ai/xn-ptts/tree/main/ptts-wasm` WASM link); `Alterative implementations` section (`gradium-ai/xn-ptts` XN link); `Models trained by the community` section (Greek/Myned AI `<details>` with pinned `greek.yaml` config, `eleni.wav` voice, and sample text); `Projects using Pocket TTS` section (Libratory and ToBe SAID entries).
