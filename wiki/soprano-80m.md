---
type: Concept
title: Soprano-80M
description: Original 80M-parameter English-only on-device TTS release superseded by Soprano-1.1-80M, with up to 2000x real-time GPU synthesis and sub-15 ms streaming latency.
tags: [tts, streaming, on-device, english-only]
status: deprecated
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:20:23Z }
stale_after: 2027-10-06
sources:
  - id: soprano-80m-card
    resource: ../raw/Soprano-80M.md
    kind: documentation
    title: Soprano-80M README and Hugging Face model card with outdated notice
---

Soprano-80M is the original ultra-lightweight 80M-parameter English-only text-to-speech release for on-device expressive synthesis at 32 kHz, reporting up to 2000x real-time generation on GPU and 20x on CPU with lossless streaming under 15 ms on GPU and under 250 ms on CPU, under 1 GB memory use, and WebUI, CLI, OpenAI-compatible endpoint, and Python interfaces without voice cloning; the card itself marks this checkpoint outdated and directs users to Soprano-1.1-80M (**Reported**).[^soprano-80m-card]

## Model identity and release

- Title is `Soprano`; this snapshot covers checkpoint `Soprano-80M` released 2025.12.22 with code at `https://github.com/ekwek1/soprano` and demo at `https://huggingface.co/spaces/ekwek/Soprano-TTS`; card carries `<!-- Version 0.1.0 -->` (**Reported**).[^soprano-80m-card]
- Frontmatter declares `library_name: transformers`, `pipeline_tag: text-to-speech`, and `license: apache-2.0` (**Observed** by static inspection).[^soprano-80m-card]
- News entries record `Soprano-80M` release on 2025.12.22, `Soprano-Factory` release on 2026.01.13, and `Soprano-1.1-80M` release on 2026.01.14 with a claimed 95% fewer hallucinations and a 63% preference rate over `Soprano-80M`, stated without evaluation protocol, rater count, or prompt set (**Reported**).[^soprano-80m-card]
- Creator is `ekwek` / `ekwek1`; training/fine-tuning companion is `Soprano-Factory` at `https://github.com/ekwek1/soprano-factory` (**Reported**).[^soprano-80m-card]
- Project license is Apache-2.0 (**Reported**).[^soprano-80m-card]

## Capabilities and performance

- Compact 80M-parameter architecture with under 1 GB memory usage, expressive crystal-clear 32 kHz output, and infinite generation length via automatic text splitting (**Reported**).[^soprano-80m-card]
- Speed claims are up to 2000x real-time on GPU and 20x real-time on CPU, with the 2000x figure qualified in the Python section as requiring sufficiently long input or large batch size (**Reported**).[^soprano-80m-card]
- Lossless streaming claims are under 15 ms latency on GPU and under 250 ms on CPU (**Reported**).[^soprano-80m-card]
- Device and OS support is stated as CUDA, CPU, and MPS on Windows, Linux, and Mac (**Reported**).[^soprano-80m-card]

## Requirements and installation

- Wheel install (`pip install soprano-tts`) is CUDA-only for now (**Reported**).[^soprano-80m-card]
- From-source CUDA install clones `https://github.com/ekwek1/soprano` and runs `pip install -e .[lmdeploy]`; CPU/MPS from-source install runs `pip install -e .` without the extra (**Reported**).[^soprano-80m-card]
- On Windows with CUDA, `pip` installs a CPU-only PyTorch build, so the source instructs reinstalling PyTorch explicitly afterward with `pip uninstall -y torch` then `pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128` (**Reported**).[^soprano-80m-card]

## Inference usage

- WebUI starts with `soprano-webui` (default `http://127.0.0.1:7860`); `--cache-size 1000 --decoder-batch-size 4` is suggested as an example speedup at higher memory cost (**Reported**).[^soprano-80m-card]
- CLI form is `soprano "text"` with options `--output/-o` (default `output.wav`, non-streaming only), `--model-path/-m`, `--device/-d` (`auto`, `cuda`, `cpu`, `mps`; default `auto`), `--backend/-b` (`auto`, `transformers`, `lmdeploy`; default `auto`), `--cache-size/-c` in MB for the lmdeploy backend (default 100), `--decoder-batch-size/-bs` (default 1), and `--streaming/-s` for speaker playback; the CLI reloads the model on every call and is therefore slower than persistent methods (**Reported**).[^soprano-80m-card]
- OpenAI-compatible server starts with `uvicorn soprano.server:app --host 0.0.0.0 --port 8000`; the documented `POST /v1/audio/speech` example takes `{"input": "..."}` and writes `speech.wav`; the endpoint currently supports non-streaming output only (**Reported**).[^soprano-80m-card]
- Python constructs `SopranoTTS(backend='auto', device='auto', cache_size_mb=100, decoder_batch_size=1)`; larger `cache_size_mb` and `decoder_batch_size` trade memory for speed; `infer(text)` does basic synthesis, `infer(text, "out.wav")` saves to file, `infer_batch([...])` synthesizes lists with an optional output directory, and `infer_stream(text, chunk_size=1)` with `play_stream(stream)` plays with under 15 ms latency; custom sampling example passes `temperature=0.3`, `top_p=0.95`, `repetition_penalty=1.2` (**Reported**).[^soprano-80m-card]

## Usage tips

- Best results when each sentence is 2–15 seconds long (**Reported**).[^soprano-80m-card]
- Numbers and some special characters are recognized but occasionally mispronounced; the source recommends rewriting them phonetically (e.g. `1+1` to `one plus one`) (**Reported**).[^soprano-80m-card]
- Unsatisfactory outputs can be regenerated for a new sample, optionally with changed sampling settings for more variation (**Reported**).[^soprano-80m-card]
- Avoid improper grammar such as missing contractions or multiple spaces (**Reported**).[^soprano-80m-card]

## Limitations

- English-only with no voice cloning; trained on only 1,000 hours of audio (stated as about 100x less than other TTS models), so mispronunciation of uncommon words may occur and is expected to diminish with more training data (**Reported**).[^soprano-80m-card]

## Supersession

- Status is `deprecated`: header banner states "this model is now outdated. Use Soprano-1.1-80M instead", effective with the 2026.01.14 `Soprano-1.1-80M` news entry claiming 95% fewer hallucinations and 63% preference over `Soprano-80M`; replacement is [Soprano-1.1-80M](soprano-1-1-80m.md) (**Reported**).[^soprano-80m-card]
- Body content is otherwise identical to the `Soprano-1.1-80M` card apart from the outdated banner and one bold-formatting difference in the 2026.01.14 news line, so no `Soprano-80M`-only capability deltas remain (**Synthesis**).[^soprano-80m-card]

## Relationships

- Superseded by [Soprano-1.1-80M](soprano-1-1-80m.md): the outdated banner and 2026.01.14 news entry direct new use to the 1.1 checkpoint with stated hallucination and preference gains; capability and interface claims are otherwise shared (**Synthesis**).[^soprano-80m-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no real-time-factor, latency, memory, hallucination-reduction, preference-rate, or quality claims reproduced (**Synthesis**).[^soprano-80m-card]
- Banner image, GitHub repository, Hugging Face checkpoint and demo Space, and Soprano-Factory repository were linked but not fetched and are not in `raw/`; checkpoint, tokenizer, and audio contents were not inspected (**Synthesis**).[^soprano-80m-card]
- All capability, performance, compatibility, and usage claims are source assertions without independent verification in this wiki; latency, throughput, memory, and release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^soprano-80m-card]

[^soprano-80m-card]: [Soprano-80M README and Hugging Face model card with outdated notice](../raw/Soprano-80M.md) — locators: frontmatter (`library_name`, `license`, `pipeline_tag`); `<!-- Version 0.1.0 -->` comment; header outdated-notice banner ("this model is now outdated. Use Soprano-1.1-80M instead"); header badges/links (GitHub repo, Hugging Face demo Space); `News` section (2026.01.14 Soprano-1.1-80M 95%/63% line, 2026.01.13 Soprano-Factory line, 2025.12.22 Soprano-80M line); `Overview` section (2000x GPU / 20x CPU, <15 ms GPU / <250 ms CPU streaming, <1 GB, 80M, infinite length + auto splitting, 32 kHz, CUDA/CPU/MPS + Windows/Linux/Mac, WebUI/CLI/OpenAI endpoint); `Installation` section (wheel fence, source `[lmdeploy]` vs plain fences, Windows CUDA torch-reinstall callout with `torch==2.8.0` + `cu128`); `Usage / WebUI` section (`soprano-webui`, `127.0.0.1:7860`, `--cache-size 1000 --decoder-batch-size 4` tip); `Usage / CLI` section (fence with `--output/--model-path/--device/--backend/--cache-size/--decoder-batch-size/--streaming`, reload-model note); `Usage / OpenAI-compatible endpoint` section (`uvicorn soprano.server:app` fence, curl `/v1/audio/speech` fence, non-streaming note); `Usage / Python script` section (`SopranoTTS(...)` fence, `infer`/`infer_batch`/`infer_stream` + `play_stream` fences, `temperature/top_p/repetition_penalty` fence, 2000x qualification comments); `Usage tips` section (2–15 s sentence, phonetic-numbers, regenerate/resample, grammar bullets); `Limitations` section (English-only, no cloning, 1,000-hour / ~100x-less paragraph); `License` section (Apache-2.0).
