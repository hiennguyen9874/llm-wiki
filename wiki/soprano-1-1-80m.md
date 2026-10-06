---
type: Concept
title: Soprano-1.1-80M
description: Ultra-lightweight 80M-parameter English-only on-device TTS model with up to 2000x real-time GPU synthesis, sub-15 ms streaming latency, and WebUI, CLI, OpenAI-compatible, and Python inference.
tags: [tts, streaming, on-device, english-only]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:20:23Z }
stale_after: 2027-10-06
sources:
  - id: soprano-card
    resource: ../raw/Soprano-1.1-80M.md
    kind: documentation
    title: Soprano README and Hugging Face model card
  - id: soprano-80m-card
    resource: ../raw/Soprano-80M.md
    kind: documentation
    title: Soprano-80M README and Hugging Face model card with outdated notice
---

Soprano-1.1-80M is an ultra-lightweight 80M-parameter English-only text-to-speech model for on-device expressive synthesis at 32 kHz, reporting up to 2000x real-time generation on GPU and 20x on CPU with lossless streaming under 15 ms on GPU and under 250 ms on CPU, under 1 GB memory use, unbounded generation via automatic text splitting, and WebUI, CLI, OpenAI-compatible endpoint, and Python interfaces without voice cloning (**Reported**).[^soprano-card]

## Model identity and release

- Title is `Soprano`; this snapshot covers checkpoint `Soprano-1.1-80M` (`ekwek/Soprano-1.1-80M`); creator is `ekwek` / `ekwek1`; code is `https://github.com/ekwek1/soprano`, demo is `https://huggingface.co/spaces/ekwek/Soprano-TTS`, and training/fine-tuning companion is `Soprano-Factory` at `https://github.com/ekwek1/soprano-factory` (**Reported**).[^soprano-card]
- Frontmatter declares `library_name: transformers`, `pipeline_tag: text-to-speech`, and `license: apache-2.0` (**Observed** by static inspection).[^soprano-card]
- News entries record `Soprano-80M` release on 2025.12.22, `Soprano-Factory` release on 2026.01.13, and `Soprano-1.1-80M` release on 2026.01.14 with a claimed 95% fewer hallucinations and a 63% preference rate over `Soprano-80M`, stated without evaluation protocol, rater count, or prompt set (**Reported**).[^soprano-card]
- Project license is Apache-2.0 (**Reported**).[^soprano-card]

## Capabilities and performance

- Compact 80M-parameter architecture with under 1 GB memory usage, expressive crystal-clear 32 kHz output, and infinite generation length via automatic text splitting (**Reported**).[^soprano-card]
- Speed claims are up to 2000x real-time on GPU and 20x real-time on CPU, with the 2000x figure qualified in the Python section as requiring sufficiently long input or large batch size (**Reported**).[^soprano-card]
- Lossless streaming claims are under 15 ms latency on GPU and under 250 ms on CPU (**Reported**).[^soprano-card]
- Device and OS support is stated as CUDA, CPU, and MPS on Windows, Linux, and Mac (**Reported**).[^soprano-card]

## Requirements and installation

- Wheel install (`pip install soprano-tts`) is CUDA-only for now (**Reported**).[^soprano-card]
- From-source CUDA install clones `https://github.com/ekwek1/soprano` and runs `pip install -e .[lmdeploy]`; CPU/MPS from-source install runs `pip install -e .` without the extra (**Reported**).[^soprano-card]
- On Windows with CUDA, `pip` installs a CPU-only PyTorch build, so the source instructs reinstalling PyTorch explicitly afterward with `pip uninstall -y torch` then `pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128` (**Reported**).[^soprano-card]

## Inference usage

- WebUI starts with `soprano-webui` (default `http://127.0.0.1:7860`); `--cache-size 1000 --decoder-batch-size 4` is suggested as an example speedup at higher memory cost (**Reported**).[^soprano-card]
- CLI form is `soprano "text"` with options `--output/-o` (default `output.wav`, non-streaming only), `--model-path/-m`, `--device/-d` (`auto`, `cuda`, `cpu`, `mps`; default `auto`), `--backend/-b` (`auto`, `transformers`, `lmdeploy`; default `auto`), `--cache-size/-c` in MB for the lmdeploy backend (default 100), `--decoder-batch-size/-bs` (default 1), and `--streaming/-s` for speaker playback; the CLI reloads the model on every call and is therefore slower than persistent methods (**Reported**).[^soprano-card]
- OpenAI-compatible server starts with `uvicorn soprano.server:app --host 0.0.0.0 --port 8000`; the documented `POST /v1/audio/speech` example takes `{"input": "..."}` and writes `speech.wav`; the endpoint currently supports non-streaming output only (**Reported**).[^soprano-card]
- Python constructs `SopranoTTS(backend='auto', device='auto', cache_size_mb=100, decoder_batch_size=1)`; larger `cache_size_mb` and `decoder_batch_size` trade memory for speed; `infer(text)` does basic synthesis, `infer(text, "out.wav")` saves to file, `infer_batch([...])` synthesizes lists with an optional output directory, and `infer_stream(text, chunk_size=1)` with `play_stream(stream)` plays with under 15 ms latency; custom sampling example passes `temperature=0.3`, `top_p=0.95`, `repetition_penalty=1.2` (**Reported**).[^soprano-card]

## Usage tips

- Best results when each sentence is 2–15 seconds long (**Reported**).[^soprano-card]
- Numbers and some special characters are recognized but occasionally mispronounced; the source recommends rewriting them phonetically (e.g. `1+1` to `one plus one`) (**Reported**).[^soprano-card]
- Unsatisfactory outputs can be regenerated for a new sample, optionally with changed sampling settings for more variation (**Reported**).[^soprano-card]
- Avoid improper grammar such as missing contractions or multiple spaces (**Reported**).[^soprano-card]

## Limitations

- English-only with no voice cloning; trained on only 1,000 hours of audio (stated as about 100x less than other TTS models), so mispronunciation of uncommon words may occur and is expected to diminish with more training data (**Reported**).[^soprano-card]

## Supersession

- Supersedes [Soprano-80M](soprano-80m.md) effective 2026.01.14: the `Soprano-80M` card header marks that checkpoint outdated and directs users to `Soprano-1.1-80M`, consistent with this card's 2026.01.14 news entry claiming 95% fewer hallucinations and 63% preference over `Soprano-80M` (**Reported**).[^soprano-card][^soprano-80m-card]

## Relationships

- Supersedes [Soprano-80M](soprano-80m.md): this 1.1 checkpoint is the stated replacement with claimed hallucination and preference gains; capability and interface claims are otherwise shared (**Synthesis**).[^soprano-card][^soprano-80m-card]

- Lightweight CPU TTS comparison: [Pocket TTS](pocket-tts.md) covers a 100M-parameter CPU-first multilingual TTS system with ~200 ms first-chunk streaming and voice cloning, while this concept covers an 80M-parameter English-only on-device TTS model with vendor-reported 2000x GPU / 20x CPU real-time factors and no voice cloning; no shared codebase is asserted (**Synthesis**).[^soprano-card]
- Sub-1B TTS comparison: [MOSS-TTS-Nano](moss-tts-nano.md) covers a 0.1B-parameter multilingual zero-shot voice-cloning TTS model with 48 kHz stereo output and ONNX CPU streaming, while this concept covers a same-scale English-only single-voice TTS model with lmdeploy/transformers backends and an OpenAI-compatible endpoint; no shared vendor or codebase is asserted (**Synthesis**).[^soprano-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice clone/design/direction and H100 TTFA/RTF figures, while this concept covers an English-only ultra-lightweight TTS model with sub-15 ms GPU streaming and <1 GB memory claims; no shared vendor or codebase is asserted (**Synthesis**).[^soprano-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no real-time-factor, latency, memory, hallucination-reduction, preference-rate, or quality claims reproduced (**Synthesis**).[^soprano-card]
- Banner image, GitHub repository, Hugging Face checkpoint and demo Space, and Soprano-Factory repository were linked but not fetched and are not in `raw/`; checkpoint, tokenizer, and audio contents were not inspected (**Synthesis**).[^soprano-card]
- All capability, performance, compatibility, and usage claims are source assertions without independent verification in this wiki; latency, throughput, memory, and release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^soprano-card]
- This ingest covers only `raw/Soprano-1.1-80M.md` for capabilities; supersession was reconciled against `raw/Soprano-80M.md`, whose body is identical apart from its outdated-banner header and one bold-formatting difference in the 2026.01.14 news line, so no `Soprano-80M`-only capability deltas remain; `Soprano-Factory` training/fine-tuning material remains pending (**Synthesis**).[^soprano-card][^soprano-80m-card]

[^soprano-card]: [Soprano README and Hugging Face model card](../raw/Soprano-1.1-80M.md) — locators: frontmatter (`library_name`, `license`, `pipeline_tag`); header badges/links (GitHub repo, Hugging Face demo Space); `News` section (2026.01.14 Soprano-1.1-80M 95%/63% line, 2026.01.13 Soprano-Factory line, 2025.12.22 Soprano-80M line); `Overview` section (2000x GPU / 20x CPU, <15 ms GPU / <250 ms CPU streaming, <1 GB, 80M, infinite length + auto splitting, 32 kHz, CUDA/CPU/MPS + Windows/Linux/Mac, WebUI/CLI/OpenAI endpoint); `Installation` section (wheel fence, source `[lmdeploy]` vs plain fences, Windows CUDA torch-reinstall callout with `torch==2.8.0` + `cu128`); `Usage / WebUI` section (`soprano-webui`, `127.0.0.1:7860`, `--cache-size 1000 --decoder-batch-size 4` tip); `Usage / CLI` section (fence with `--output/--model-path/--device/--backend/--cache-size/--decoder-batch-size/--streaming`, reload-model note); `Usage / OpenAI-compatible endpoint` section (`uvicorn soprano.server:app` fence, curl `/v1/audio/speech` fence, non-streaming note); `Usage / Python script` section (`SopranoTTS(...)` fence, `infer`/`infer_batch`/`infer_stream` + `play_stream` fences, `temperature/top_p/repetition_penalty` fence, 2000x qualification comments); `Usage tips` section (2–15 s sentence, phonetic-numbers, regenerate/resample, grammar bullets); `Limitations` section (English-only, no cloning, 1,000-hour / ~100x-less paragraph); `License` section (Apache-2.0).

[^soprano-80m-card]: [Soprano-80M README and Hugging Face model card with outdated notice](../raw/Soprano-80M.md) — locators: header outdated-notice banner ("this model is now outdated. Use Soprano-1.1-80M instead"); `News` section 2026.01.14 line (95% fewer hallucinations, 63% preference over Soprano-80M); body otherwise identical to `Soprano-1.1-80M.md` apart from banner and bold-formatting difference (verified by diff).
