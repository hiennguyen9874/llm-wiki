---
type: Concept
title: Audio8-ASR-0.1B
description: Compact 0.1B-LM autoregressive multilingual ASR model with Qwen3-ASR encoder, 7.03% mean English WER on the Open ASR Leaderboard, decode-time hotword boosting, and ONNX plus iOS edge releases.
tags: [ml, asr, multilingual, speech-recognition]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
sources:
  - id: audio8-asr-01b-card
    resource: ../raw/Audio8-ASR-0.1B.md
    kind: documentation
    title: Audio8-ASR-0.1B model card
---

Audio8-ASR-0.1B is a compact autoregressive automatic speech recognition model whose language-model component has about 0.1B parameters, pairing a Qwen3-ASR audio encoder and MLP adapter with an 8-layer Qwen-style causal LM for multilingual short-form transcription in seven languages, with reported seven-split mean WER of 7.03% on the Open ASR Leaderboard English suite and optional decode-time hotword boosting plus ONNX Runtime and iOS ANE edge releases (**Reported**).[^audio8-asr-01b-card]

## Model identity and architecture

- Card title is `Audio8-ASR-0.1B` from `AutoArk-AI`; repository is `https://github.com/AutoArk/open-audio-opd`; frontmatter declares `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `license: cc-by-nc-4.0`, languages `en, zh, fr, ja, yue, de, ko`, and tags including `automatic-speech-recognition`, `speech`, `audio`, `multilingual`, `transformers`, `pytorch`, `safetensors`, `hotword`, and `audio8` (**Reported**).[^audio8-asr-01b-card]
- Task is automatic speech recognition; checkpoint format is `safetensors`; sampling rate is 16 kHz; runtime is Hugging Face Transformers; model must be loaded with `trust_remote_code=True` (**Reported**).[^audio8-asr-01b-card]
- Decoder is an 8-layer Qwen-style causal LM; audio front end is Qwen3-ASR audio encoder plus MLP adapter/projector (**Reported**).[^audio8-asr-01b-card]
- Language-model parameters are 103,502,336 (about 0.104B); end-to-end unique parameters are 323,990,528 (about 0.324B) (**Reported**).[^audio8-asr-01b-card]
- Lineage: audio encoder backbone is based on `Qwen/Qwen3-ASR-0.6B`, with the audio adapter and projector trained as part of Audio8-ASR; language-model backbone is based on `MiniLLM/Ref-Pretrain-Qwen-104M` (**Reported**).[^audio8-asr-01b-card]

## Supported languages

Chinese, English, French, German, Japanese, Korean, and Cantonese — seven languages total (`yue` is Cantonese) (**Reported**).[^audio8-asr-01b-card]

## Performance

Open ASR Leaderboard English short-form results; WER lower is better (**Reported**):[^audio8-asr-01b-card]

| Evaluation suite | Dataset / split | Language | Metric | Score (%) | H200 RTFx |
| --- | --- | :---: | :---: | ---: | ---: |
| Open ASR Leaderboard | AMI Cleaned | EN | WER | 10.99 | 396.91 |
| Open ASR Leaderboard | Earnings22 | EN | WER | 12.31 | 654.17 |
| Open ASR Leaderboard | GigaSpeech Cleaned | EN | WER | 8.48 | 641.19 |
| Open ASR Leaderboard | LibriSpeech test.clean | EN | WER | 2.70 | 687.84 |
| Open ASR Leaderboard | LibriSpeech test.other | EN | WER | 6.59 | 610.52 |
| Open ASR Leaderboard | SPGISpeech | EN | WER | 3.73 | 870.32 |
| Open ASR Leaderboard | VoxPopuli Cleaned AA | EN | WER | 4.39 | 686.14 |
| Open ASR Leaderboard | Seven-split mean / composite | EN | WER / RTFx | 7.03 | 741.15 |

Internal canonical Chinese ASR results; CER lower is better (**Reported**):[^audio8-asr-01b-card]

| Evaluation suite | Dataset / split | Language | Metric | Score (%) |
| --- | --- | :---: | :---: | ---: |
| Internal canonical ASR eval | WenetSpeech meeting | ZH | CER | 8.842 |
| Internal canonical ASR eval | WenetSpeech net | ZH | CER | 7.976 |

- Open ASR protocol uses the seven current public splits from `hf-audio/open-asr-leaderboard` at dataset revision `b6bdcd0beb34f8975dc659796176d88f43aff502`, measured with the standalone Transformers package on standardized H200 Hugging Face Jobs using BF16, eager attention, greedy decoding, `max_new_tokens=256`, and a 30-second audio cap; per-split batch sizes were 1152, 1024, 1408, 1024, 1024, 2048, and 628 (**Reported**).[^audio8-asr-01b-card]
- Raw Open ASR manifests are stored in `hf://buckets/AutoArk-AI/audio8-asr-open-asr-results`; machine-readable results are provided in `.eval_results/open_asr_leaderboard.yaml` (**Reported**).[^audio8-asr-01b-card]
- WenetSpeech results come from the reproducibility-checked `teacher0p6B-step3000` export with batch size 128; its effective model tensors are byte-identical to the standalone release, which only removes a redundant tied LM-head tensor and repackages the same weights; AISHELL is intentionally excluded from the table (**Reported**).[^audio8-asr-01b-card]

## Files and related releases

- Checkpoint files: `config.json`, tokenizer files, processor files, and `model.safetensors`; remote-code modules `configuration_arkasr.py`, `modeling_arkasr.py`, `processing_arkasr.py` plus `qwen3_asr_audio_config.py` and `qwen3_asr_audio_model.py`; `hotword/` backend-agnostic hotword trie; `examples/` Transformers inference examples (**Reported**).[^audio8-asr-01b-card]
- Root `config.json` is intentionally kept so Hugging Face recognizes the model package and counts downloads through normal model-file queries (**Reported**).[^audio8-asr-01b-card]
- Deployment releases: `Audio8-ASR-0.1B-onnx-runtime` for edge-device deployment at roughly 1.1 GB peak memory footprint, and `Audio8-ASR-0.1B-iOS-ANE` for local iPhone transcription at roughly 200 MB peak runtime memory footprint, each varying by device, runtime/configuration or iOS version, and workload (**Reported**).[^audio8-asr-01b-card]

## Transformers inference

- Loads `AutoArk-AI/Audio8-ASR-0.1B` via `AutoProcessor` and `AutoModelForCausalLM` with `trust_remote_code=True`, `torch_dtype` bfloat16 on CUDA else float32, `attn_implementation="eager"`, `model.eval()`, and a user conversation carrying `{"type": "audio", "path": audio_path}` plus `"Please transcribe this audio."` (**Reported**).[^audio8-asr-01b-card]
- Chat-template settings are `sampling_rate=16000`, `audio_padding="longest"`, `add_generation_prompt=True`, `audio_max_length=30 * 16000`, and `text_kwargs` with `padding="longest"`, `truncation=True`, `max_length=1000`; generation uses `max_new_tokens=128` with `do_sample=False`, then decodes past the prompt length with `skip_special_tokens=True` (**Reported**).[^audio8-asr-01b-card]
- Equivalent CLI forms are `python examples/transcribe.py path/to/audio.wav --model AutoArk-AI/Audio8-ASR-0.1B` and, for local staging before upload, `python examples/transcribe.py path/to/audio.wav --model .` (**Reported**).[^audio8-asr-01b-card]

## Hotword boosting

- Hotwords apply at decode time by nudging logits for tokenizer paths matching the requested words; this does not modify model weights and does not inject the hotwords into the prompt (**Reported**).[^audio8-asr-01b-card]
- Example: `python examples/transcribe_hotword.py path/to/audio.wav --model AutoArk-AI/Audio8-ASR-0.1B --hotwords "Audio8,AutoArk"` (**Reported**).[^audio8-asr-01b-card]
- Knobs are `--hotword_topk` (only boost tokens already inside the current top-k logits), `--hotword_start_boost` (first token of each hotword), and `--hotword_continuation_boost` (continuation tokens after a matched prefix) (**Reported**).[^audio8-asr-01b-card]

## Limitations

- Default examples target short-form ASR and truncate audio at 30 seconds (**Reported**).[^audio8-asr-01b-card]
- Hotword boosting can help near-miss terms but can over-bias decoding when boost values are too high (**Reported**).[^audio8-asr-01b-card]
- Some Transformers/tokenizers versions emit a Qwen tokenizer regex warning; the staged tokenizer config is kept in the loadable form used by the package, and explicit tokenizer regex flags should be passed only after testing the local Transformers version (**Reported**).[^audio8-asr-01b-card]

## Relationships

- Sibling ASR model: [ARK-ASR-3B](ark-asr-3b.md) is the larger 3B-scale multilingual ASR model from the same `AutoArk/open-audio-opd` codebase and arXiv line (2605.28139), reporting 5.04% average English WER versus 7.03% here, while this concept covers the compact 0.1B-LM model with hotword boosting and ONNX/iOS edge packaging (**Synthesis**).[^audio8-asr-01b-card]
- Encoder lineage: this model's audio front end is based on `Qwen/Qwen3-ASR-0.6B`; see [Qwen3-ASR family](qwen3-asr-family.md) for that encoder line's language coverage, streaming/offline behavior, and serving toolkit (**Synthesis**).[^audio8-asr-01b-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio transcribed, and no WER/CER, RTFx, or memory-footprint figures reproduced (**Synthesis**).[^audio8-asr-01b-card]
- Demo video asset, ONNX Runtime and iOS ANE releases, GitHub repository, arXiv page, raw manifests in `hf://buckets/AutoArk-AI/audio8-asr-open-asr-results`, and `.eval_results/open_asr_leaderboard.yaml` were linked but not fetched and were not present in `raw/`; checkpoint, tokenizer, processor, remote-code, `hotword/`, and `examples/` files were listed but not present in `raw/` and were not inspected (**Synthesis**).[^audio8-asr-01b-card]
- All accuracy, speed, memory-footprint, lineage, and usage claims are source assertions without independent verification in this wiki (**Synthesis**).[^audio8-asr-01b-card]

[^audio8-asr-01b-card]: [Audio8-ASR-0.1B model card](../raw/Audio8-ASR-0.1B.md) — locators: frontmatter (`library_name`, `pipeline_tag`, `language`, `license`, `tags`, `repository`); header badges (GitHub `AutoArk/open-audio-opd`, arXiv 2605.28139, license); intro paragraph (0.1B LM, 7 languages, smallest-usable positioning); deployment paragraph plus `Related Releases` (ONNX ~1.1 GB, iOS ~200 MB footprints); section `Evaluation Results` (10-row WER/CER + RTFx table, Open ASR protocol paragraph with revision `b6bdcd0…`, H200/BF16/eager/greedy/`max_new_tokens=256`/30-s cap/batch sizes, manifests bucket and `.eval_results/open_asr_leaderboard.yaml`, WenetSpeech `teacher0p6B-step3000`/batch-128/byte-identical/AISHELL-excluded paragraph); section `Model Overview` (8 bullets: task, safetensors, 16 kHz, 8-layer Qwen LM, Qwen3-ASR encoder + MLP, 103502336 / 323990528 params, Transformers, hotwords, `trust_remote_code`); section `Files` (9 file/module/dir bullets, root `config.json` note); section `Transformers Inference` (Python code fence and two `examples/transcribe.py` commands); section `Hotword Boosting` (logit-boost paragraph, `transcribe_hotword.py` command, three `--hotword_*` knobs); section `Limitations` (30-s truncation, over-bias, tokenizer-regex-warning paragraphs); section `Acknowledgements` (Qwen3-ASR-0.6B and Ref-Pretrain-Qwen-104M lineage).
