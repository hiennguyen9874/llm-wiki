---
type: Concept
title: ARK-ASR-0.6B
description: 0.6B-scale multilingual ASR model trained with teacher-data adaptation and online policy distillation, reporting 6.55% average English WER and 4.30% average Chinese CER in its open-audio-opd evaluation.
tags: [stt, asr, multilingual, speech-recognition]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:28:03Z }
stale_after: 2027-10-06
sources:
  - id: ark-asr-06b-card
    resource: ../raw/ARK-ASR-0.6B.md
    kind: documentation
    title: ARK-ASR-0.6B model card
  - id: ark-asr-3b-card
    resource: ../raw/ARK-ASR-3B.md
    kind: documentation
    title: ARK-ASR-3B model card
---

ARK-ASR-0.6B is a 0.6B-scale multilingual automatic speech recognition model combining a Whisper-style audio encoder with RoPE, an MLP adapter, and a Qwen2 decoder with custom `arkasr` remote code, trained with the teacher-data adaptation plus online policy distillation (TD + OPD) recipe where the student generates transcripts online and trains against token-level teacher scores on its own rollouts; the card identifies this checkpoint as the `Ark-Base+TD+OPD` model, supports 19 languages, and reports 6.55% average English WER (ahead of Qwen3-ASR-0.6B at 6.93%, behind Qwen3-ASR-1.7B at 6.25%) and 4.30% average Chinese CER in its `open-audio-opd` evaluation.[^ark-asr-06b-card]

## Architecture

- Audio-capable autoregressive Transformers model for ASR: Whisper-style encoder with RoPE → MLP adapter → Qwen2 decoder, where merged audio features are injected by replacing audio placeholder token embeddings before transcript generation (**Reported**).[^ark-asr-06b-card]
- 0.6B decoder-LLM parameters with a separate 0.6B-scale Whisper-style audio encoder and MLP adapter; checkpoint format `safetensors`; 16 kHz sampling rate; must be loaded with `trust_remote_code=True` (**Reported**).[^ark-asr-06b-card]
- Official inference entry point is `scripts/infer/ark_asr_transformers.py` in `AutoArk/open-audio-opd`; unlike the 3B card, this card documents no vLLM serving adapter (**Reported**).[^ark-asr-06b-card]
- Frontmatter of the ingested card declares `license: apache-2.0`, `pipeline_tag: automatic-speech-recognition`, and 19 `language` codes (**Observed** by static inspection).[^ark-asr-06b-card]

## Supported languages

Chinese, English, German, Japanese, French, Korean, Spanish, Polish, Italian, Romanian, Hungarian, Czech, Dutch, Finnish, Croatian, Slovak, Slovene, Estonian, and Lithuanian — 19 languages total (**Reported**).[^ark-asr-06b-card]

## Performance

English WER from the `open-audio-opd` evaluation in this card; lower is better (**Reported**).[^ark-asr-06b-card]

| Model | AMI | Earnings22 | GigaSpeech | LS Clean | LS Other | SPGISpeech | VoxPopuli | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ARK-ASR-0.6B | 11.54% | 10.07% | 8.95% | 1.87% | 3.89% | 2.89% | 6.63% | 6.55% |
| Qwen3-ASR-0.6B | 11.66% | 11.06% | 9.14% | 2.13% | 4.45% | 3.03% | 7.07% | 6.93% |
| Qwen3-ASR-1.7B | 10.56% | 10.25% | 8.74% | 1.63% | 3.40% | 2.84% | 6.35% | 6.25% |

Chinese CER from the same evaluation; lower is better (**Reported**).[^ark-asr-06b-card]

| Model | AISHELL-1 | Wenet-meeting | Wenet-net | Avg |
| --- | ---: | ---: | ---: | ---: |
| ARK-ASR-0.6B | 2.02% | 5.92% | 4.96% | 4.30% |
| Qwen3-ASR-0.6B | 2.07% | 5.57% | 5.45% | 4.36% |
| Qwen3-ASR-1.7B | 1.50% | 4.69% | 4.55% | 3.58% |

- The sibling [ARK-ASR-3B](ark-asr-3b.md) card instead reports Leaderboard-protocol numbers for the same 0.6B checkpoint: 5.97% English average (AMI 10.02%, Earnings22 9.77%, GigaSpeech 8.00%, LS Clean 1.53%, LS Other 3.51%, SPGISpeech 2.63%, VoxPopuli 6.31%) with identical Chinese CER components (2.02% / 5.92% / 4.96%); the English gap reflects different evaluation harnesses, not a different checkpoint, so do not mix the two tables into one ranking (**Synthesis**).[^ark-asr-3b-card]

## Inference

- Transformers inference loads `AutoArk-AI/ARK-ASR-0.6B` via `AutoModelForCausalLM`, `AutoProcessor`, and `AutoTokenizer` with `trust_remote_code=True`, `sdpa` attention, `float16` on CUDA (`float32` on CPU), 30 s / 16 kHz audio window (`audio_max_length=30 * 16000`), greedy decoding (`do_sample=False`, `max_new_tokens=256`), and `bad_words_ids` filtering of non-ASR special and added `<...>` tokens while keeping EOS (**Reported**).[^ark-asr-06b-card]
- Batch JSONL inference uses `python scripts/infer/ark_asr_transformers.py` with `--input/--output/--model_path/--processor_path/--batch_size/--dtype/--attn_impl` flags (example `--batch_size 40 --dtype float16 --attn_impl sdpa`); input lines carry `audio`, `text`, `task`, `begin_time`, `end_time`; output adds `pred_text` (cleaned) and `pred_text_raw` (raw decode) (**Reported**).[^ark-asr-06b-card]
- Local J/WER evaluation uses `python scripts/eval/eval_jwer_ark_asr_transformers.py` with the same model/processor/batch/dtype flags (**Reported**).[^ark-asr-06b-card]

## Evaluation and training lineage

- The TD + OPD recipe comes from `open-audio-opd`; training code is based on `THUNLP/OPD` and `verl`, and the OPD step uses a stronger ASR teacher to score online student rollouts (**Reported**).[^ark-asr-06b-card]
- Canonical citation is Lin et al., *Data-Efficient On-Policy Distillation for Automatic Speech Recognition*, arXiv:2605.28139 (2026); code repository is `https://github.com/AutoArk/open-audio-opd`; model-card license field is `apache-2.0` (**Reported**).[^ark-asr-06b-card]
- No evaluation audio or dataset files are bundled with the model repository per the card (**Reported**).[^ark-asr-06b-card]

## Relationships

- Sibling of [ARK-ASR-3B](ark-asr-3b.md): the 3B checkpoint shares the Whisper-style encoder plus MLP adapter plus Qwen decoder architecture, the `arkasr` remote code, the 19-language set, and the TD + OPD lineage, and carries this 0.6B checkpoint as its Leaderboard-protocol sibling row; read the two cards together and keep the two English WER protocols separate (**Synthesis**).[^ark-asr-3b-card]
- Benchmarked against [Qwen3-ASR family](qwen3-asr-family.md): this card's English and Chinese tables carry `Qwen3-ASR-0.6B` and `Qwen3-ASR-1.7B` columns as baselines, with the 0.6B ARK checkpoint ahead of the 0.6B Qwen3 checkpoint on average in both tables under this card's protocol; cross-read that concept for Qwen3-ASR language coverage, streaming/offline behavior, and serving toolkit (**Synthesis**).[^ark-asr-06b-card]
- Compared in [ASR/STT Model Survey](asr-stt-model-survey.md): the survey currently carries the 0.6B checkpoint only as a sibling row sourced from the 3B card's Leaderboard protocol, not from this card's `open-audio-opd` protocol; use the tables above for the card-native comparison (**Synthesis**).[^ark-asr-3b-card]

## Contradictions

- English WER for the same `ARK-ASR-0.6B` checkpoint: 6.55% average across 7 sets in this card's `open-audio-opd` evaluation versus 5.97% average across the same 7 set names in the sibling 3B card's Hugging Face Open ASR Leaderboard evaluation (per-set gaps of roughly 0.3–1.5 points, largest on AMI and Earnings22); neither figure is chosen here because the harnesses differ, and the Chinese CER components are identical across both cards.[^ark-asr-06b-card][^ark-asr-3b-card]

## Coverage and limits

- Source inspected statically only; no package installed, no model downloaded, no audio transcribed, and no WER/CER figure reproduced (**Synthesis**).[^ark-asr-06b-card]
- Architecture diagram (`figures/ark_asr_architecture.png`) and sample audio (`assets/libai.wav`) referenced in the card were not present in `raw/` and were not inspected; upstream repository, inference/eval scripts, Hugging Face model page `AutoArk-AI/ARK-ASR-0.6B`, and arXiv:2605.28139 were linked but not fetched; performance claims are source assertions without independent verification in this wiki (**Synthesis**).[^ark-asr-06b-card]
- All identity, accuracy, and compatibility claims are source assertions, and model-release plus benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^ark-asr-06b-card]

[^ark-asr-06b-card]: [ARK-ASR-0.6B model card](../raw/ARK-ASR-0.6B.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `repository`); sections `Abstract` (`Ark-Base+TD+OPD` identity, TD + OPD recipe, 19-language list), `Supported Languages`, `Model Overview` (incl. Figure 1 caption, model-size bullet, `arkasr`/`safetensors`/16 kHz/`trust_remote_code`/`ark_asr_transformers.py` bullets), `Performance > English WER` table, `Performance > Chinese CER` table, `Inference` (Transformers code fence, JSONL schema, `ark_asr_transformers.py` batch command), `Evaluation` (`eval_jwer_ark_asr_transformers.py` command, no-bundled-data note), `Acknowledgements` (`THUNLP/OPD`, `verl`, stronger teacher), `Citation` (arXiv:2605.28139).

[^ark-asr-3b-card]: [ARK-ASR-3B model card](../raw/ARK-ASR-3B.md) — locators: sections `Abstract` and `Model Overview` (shared architecture, 19-language set, `arkasr` code), `Performance > English WER` table (Leaderboard-protocol `ARK-ASR-0.6B` sibling row, 5.97% avg), `Performance > Chinese CER` table (identical 2.02% / 5.92% / 4.96% components).
