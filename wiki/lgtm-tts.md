---
type: Concept
title: LGTM-TTS
description: Multilingual 44.1 kHz text-to-speech model with 10 built-in voices, cross-lingual zero-shot voice cloning, and PyTorch plus ONNX runtimes.
tags: [tts, multilingual, voice-cloning, onnx]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T16:30:00Z }
stale_after: 2027-10-06
sources:
  - id: lgtm-card
    resource: ../raw/LGTM.md
    kind: documentation
    title: LGTM-TTS model card (polyskill/LGTM)
---

LGTM-TTS (Looks Good To Me) is a multilingual text-to-speech model synthesizing 44.1 kHz audio with 10 built-in voices and cross-lingual zero-shot voice cloning from 5–15 seconds of reference speech, served through PyTorch and ONNX Runtime backends with a CLI, denoising-step, rate, and silence controls, and a documented four-graph ONNX layout with explicit tensor I/O and sampling loop (**Reported**).[^lgtm-card]

## Model identity and provenance

- Title is `LGTM-TTS`; short name expands to Looks Good To Me; repository is `polyskill/LGTM`; frontmatter declares `pipeline_tag: text-to-speech`, 11 languages, and tags including `text-to-speech`, `tts`, `voice-cloning`, `onnx`, and `multilingual` (**Reported**).[^lgtm-card]
- The card states the model was built by Claude Opus 5.5, which wrote the modeling code, collected and processed the training data, designed and ran the experiments, and trained and evaluated the model (**Reported**).[^lgtm-card]
- Available in PyTorch and ONNX; the ONNX backend runs on ONNX Runtime and needs no PyTorch (**Reported**).[^lgtm-card]
- No parameter count, architecture family name, training-data description beyond the provenance claim, benchmark table, license, or release date is stated in the source (**Reported** absence).[^lgtm-card]

## Supported languages and built-in voices

- Eleven languages with codes: English `en`, Spanish `es`, Portuguese `pt`, French `fr`, German `de`, Italian `it`, Swedish `sv`, Vietnamese `vi`, Japanese `ja`, Korean `ko`, Indonesian `id` (**Reported**).[^lgtm-card]
- Ten built-in voices: `F1`–`F5` female and `M1`–`M5` male (**Reported**).[^lgtm-card]
- The card ships 22 audio samples (two voices per language) hosted under `https://huggingface.co/polyskill/LGTM/resolve/main/samples/`; per-sample example sentences are illustrative and are not reproduced here (**Reported**).[^lgtm-card]

## Inference usage

- Setup clones `https://huggingface.co/polyskill/LGTM` and installs `requirements.txt` for the PyTorch backend or `requirements-onnx.txt` for the ONNX backend (**Reported**).[^lgtm-card]
- PyTorch: `LGTMTTS.from_pretrained(".")` (or `"polyskill/LGTM"` to download), `synthesize(text, lang, voice)`, and `save_wav(wav, path)` producing 44.1 kHz mono output (**Reported**).[^lgtm-card]
- ONNX Runtime: `LGTMOnnx.from_pretrained(".", use_gpu=False)`, with `use_gpu=True` alongside onnxruntime-gpu; the same `synthesize` / `save_wav` calls apply (**Reported**).[^lgtm-card]
- Voice cloning accepts 5–15 seconds of clean speech; the cloned voice can then speak any supported language; `clone_voice("reference.wav")` works with both backends; `save_voice_style("my_voice.json", voice)` persists a voice for reuse as `voice="my_voice.json"` (ONNX import path is `lgtm.onnx_inference`) (**Reported**).[^lgtm-card]
- Command line: `python -m lgtm.cli --text ... --lang ... --voice ... --out out.wav`, with `--ref reference.wav --save_voice my_voice.json` for cloning and `--backend onnx` to select the ONNX backend (**Reported**).[^lgtm-card]

## Synthesis options

| Argument | Default | Meaning (**Reported**) |
| --- | --- | --- |
| `lang` | `"en"` | language code from the list above[^lgtm-card] |
| `voice` | `"F1"` | preset name, path to a voice `.json`, or `clone_voice()` output[^lgtm-card] |
| `steps` | `8` | denoising steps; fewer is faster (e.g. 5)[^lgtm-card] |
| `speed` | `1.05` | speaking rate; higher is faster[^lgtm-card] |
| `silence` | `0.3` | seconds of silence between sentences; long text is split automatically[^lgtm-card] |

## File and graph layout

| Path | Contents (**Reported**) |
| --- | --- |
| `pytorch/model.safetensors` | all weights (synthesis + voice cloning)[^lgtm-card] |
| `onnx/text_encoder.onnx`, `duration_predictor.onnx`, `vector_estimator.onnx`, `vocoder.onnx` | synthesis graphs[^lgtm-card] |
| `onnx/voice_encoder.onnx` | reference audio to voice style (cloning)[^lgtm-card] |
| `voice_styles/*.json` | built-in voices[^lgtm-card] |
| `config.json`, `unicode_indexer.json` | model config, text vocabulary[^lgtm-card] |
| `lgtm/` | inference code: `inference.py` (PyTorch), `onnx_inference.py` (ONNX), `cli.py`[^lgtm-card] |

## ONNX graph I/O and sampling loop

| Graph | Inputs | Outputs (**Reported**) |
| --- | --- | --- |
| `text_encoder` | `text_ids` int64 [B,T], `style_ttl` [B,50,256], `text_mask` [B,1,T] | `text_emb` [B,256,T][^lgtm-card] |
| `duration_predictor` | `text_ids`, `style_dp` [B,8,16], `text_mask` | `duration` [B] (seconds)[^lgtm-card] |
| `vector_estimator` | `noisy_latent` [B,144,L], `text_emb`, `style_ttl`, `latent_mask` [B,1,L], `text_mask`, `current_step` [B], `total_step` [B] | `denoised_latent` [B,144,L][^lgtm-card] |
| `vocoder` | `latent` [B,144,L] | `wav` [B, 3072·L][^lgtm-card] |
| `voice_encoder` | `wav` [1,N] (44.1 kHz) | `style_ttl` [1,50,256], `style_dp` [1,8,16][^lgtm-card] |

- Sampling loop: `L = ceil(duration·44100 / 3072)`; start from Gaussian noise masked by `latent_mask`; call `vector_estimator` for `current_step = 0 … total_step-1`; then run the vocoder; the reference implementation is `lgtm/onnx_inference.py` (**Reported**).[^lgtm-card]

## Limitations and responsible use

- Reference audio should be 5–15 seconds of clean speech; no noise-robustness, long-form, latency, VRAM, or quality figures are stated (**Reported**).[^lgtm-card]
- No consent, disclosure, or misuse guidance is stated in the source; cloning any voice therefore inherits the wiki's standing caution to obtain consent and disclose synthetic audio, as recorded for comparable cloning models (**Synthesis**).[^lgtm-card]

## Relationships

- Closest compiled comparator is [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md): both are multilingual 44.1 kHz zero-shot cloning models with an ONNX CPU path, but Audio8 publishes a DualAR architecture with parameter counts and Seed-TTS benchmark tables while LGTM publishes an ONNX graph I/O contract and sampling loop with no numeric evaluation (**Synthesis**).[^lgtm-card]
- Surveyed alongside every other TTS line in [TTS Model Survey](tts-model-survey.md) (**Synthesis**).[^lgtm-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio synthesized, and no latency, quality, or memory figure reproduced (**Synthesis**).[^lgtm-card]
- The Hugging Face repository, weight and graph files, inference code, voice-style JSON files, sample audio, and requirements files were linked but not fetched and were not present in `raw/` (**Synthesis**).[^lgtm-card]
- All identity, provenance, language, voice, usage, option-default, file-layout, and graph-I/O claims are source assertions without independent verification in this wiki; license, size, training data, and evaluation evidence are absent from the source (**Synthesis**).[^lgtm-card]

[^lgtm-card]: [LGTM-TTS model card](../raw/LGTM.md) — locators: frontmatter (`language`, `pipeline_tag`, `tags`); intro paragraphs (Looks Good To Me expansion, Claude Opus 5.5 role list, 44.1 kHz, 10 built-in voices, zero-shot cloning, PyTorch/ONNX backends); `Languages` paragraph (11 codes); `Built-in voices` paragraph (F1–F5, M1–M5); `Samples` table (22 rows, per-language example text, `samples/<lang>_<voice>.wav` audio URLs); `Setup` fence (`git clone`, `requirements.txt`, `requirements-onnx.txt`); `PyTorch` fence (`LGTMTTS.from_pretrained`, `synthesize`, `save_wav`, 44.1 kHz mono); `ONNX Runtime` fence (`LGTMOnnx.from_pretrained`, `use_gpu`); `Voice cloning` section (5–15 s clean speech, any-language reuse, `clone_voice`, `save_voice_style`, `my_voice.json`); `Command line` fence (`lgtm.cli`, `--text/--lang/--voice/--out/--ref/--save_voice/--backend`); `Options` table (`lang/voice/steps/speed/silence` defaults); `Files` table (safetensors, four synthesis graphs, voice encoder, voice styles, configs, `lgtm/` modules); `ONNX graph I/O` table (five graphs with tensor shapes) plus sampling-loop paragraph (`L` formula, masked Gaussian start, step range, vocoder, `lgtm/onnx_inference.py` pointer).
