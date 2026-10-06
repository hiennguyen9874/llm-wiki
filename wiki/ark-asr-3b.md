---
type: Concept
title: ARK-ASR-3B
description: 3B-scale multilingual ASR model with Whisper-style encoder and Qwen decoder, SOTA on Open ASR Leaderboard English short-form at 5.04% average WER.
tags: [ml, asr, multilingual, speech-recognition]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
sources:
  - id: ark-asr-3b-card
    resource: ../raw/ARK-ASR-3B.md
    kind: documentation
    title: ARK-ASR-3B model card
---

ARK-ASR-3B is a 3B-scale multilingual automatic speech recognition model combining a Whisper-style audio encoder with RoPE, an MLP adapter, and a Qwen decoder with custom `arkasr` remote code; it reports state-of-the-art results on the Hugging Face Open ASR Leaderboard English short-form benchmark at 5.04% average WER and supports 19 languages for ASR.[^ark-asr-3b-card]

## Architecture

- Audio-capable autoregressive Transformers model for ASR: Whisper-style encoder → MLP adapter → Qwen decoder, where merged audio features are injected by replacing audio placeholder token embeddings before transcript generation (**Reported**).[^ark-asr-3b-card]
- 3B-scale decoder LLM with dedicated audio encoder and adapter; checkpoint format `safetensors`; 16 kHz sampling rate; must be loaded with `trust_remote_code=True` (**Reported**).[^ark-asr-3b-card]
- Official inference entry point is `scripts/infer/ark_asr_transformers.py` and vLLM adapter directory `scripts/vllm/ark_asr_vllm` in `AutoArk/open-audio-opd` (**Reported**).[^ark-asr-3b-card]

## Supported languages

Chinese, English, German, Japanese, French, Korean, Spanish, Polish, Italian, Romanian, Hungarian, Czech, Dutch, Finnish, Croatian, Slovak, Slovene, Estonian, and Lithuanian — 19 languages total (**Reported**).[^ark-asr-3b-card]

## Performance

English short-form WER from the Hugging Face Open ASR Leaderboard; lower is better (**Reported**).[^ark-asr-3b-card]

| Model | AMI | Earnings22 | GigaSpeech | LS Clean | LS Other | SPGISpeech | VoxPopuli | Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ARK-ASR-3B | 8.79% | 8.23% | 6.98% | 1.03% | 2.35% | 2.46% | 5.47% | 5.04% |
| ARK-ASR-0.6B | 10.02% | 9.77% | 8.00% | 1.53% | 3.51% | 2.63% | 6.31% | 5.97% |

Chinese CER (**Reported**):[^ark-asr-3b-card]

| Model | AISHELL-1 | WenetSpeech test meeting | WenetSpeech test-net |
| --- | ---: | ---: | ---: |
| ARK-ASR-3B | 1.80% | 4.97% | 4.58% |
| ARK-ASR-0.6B | 2.02% | 5.92% | 4.96% |

The card also reports RTFx of 490.98 alongside the 5.04% average WER claim (**Reported**, measurement protocol not detailed in the card).[^ark-asr-3b-card]

## Inference and serving

- Transformers inference loads `AutoArk-AI/ARK-ASR-3B` via `AutoModelForCausalLM`, `AutoProcessor`, and `AutoTokenizer` with `trust_remote_code=True`, `sdpa` attention, `bfloat16` on CUDA, 30 s / 16 kHz audio window, greedy decoding (`do_sample=False`, `max_new_tokens=256`), and `bad_words_ids` filtering of non-ASR special/added `<...>` tokens while keeping EOS (**Reported**).[^ark-asr-3b-card]
- Batch JSONL inference uses `python scripts/infer/ark_asr_transformers.py` with `--input/--output/--model_path/--processor_path/--batch_size/--dtype/--attn_impl` flags; input lines carry `audio`, `text`, `task`, `begin_time`, `end_time`; output adds `pred_text` (cleaned) and `pred_text_raw` (raw decode) (**Reported**).[^ark-asr-3b-card]
- vLLM online serving installs with `pip install -e ".[vllm]"`, starts via `scripts/vllm/deploy_ark_asr_vllm_service.sh start` (`MODEL`/`GPU`/`PORT` env vars), exposes `/health`, `/token-mask`, compact `/asr`, and OpenAI-style `/v1/audio/transcriptions` endpoints; the adapter registers the custom `arkasr` model, applies generation-time token masking, keeps `<|im_end|>` as stop token, and writes logs/PIDs under `runs/vllm/` (**Reported**).[^ark-asr-3b-card]

## Evaluation and training lineage

- Leaderboard numbers use the Hugging Face `open_asr_leaderboard` evaluation code; local J/WER evaluation uses `scripts/eval/eval_jwer_ark_asr_transformers.py` with the same model/processor/batch/dtype flags (**Reported**).[^ark-asr-3b-card]
- Training code is based on `THUNLP/OPD` and `verl`; the OPD recipe uses a stronger ASR teacher to score online student rollouts (**Reported**).[^ark-asr-3b-card]
- Canonical citation is Lin et al., *Data-Efficient On-Policy Distillation for Automatic Speech Recognition*, arXiv:2605.28139 (2026); code repository is `https://github.com/AutoArk/open-audio-opd`; model-card license field is `apache-2.0` (**Reported**).[^ark-asr-3b-card]

## Coverage and limits

- Source inspected statically only; no code executed and no audio, datasets, or metrics reproduced (**Synthesis**).[^ark-asr-3b-card]
- Architecture diagram (`figures/ark_asr_architecture.png`) and sample audio (`assets/libai.wav`) referenced in the card were not present in `raw/` and were not inspected; performance, RTFx, and SOTA claims are source assertions without independent verification in this wiki (**Synthesis**).[^ark-asr-3b-card]
- No evaluation audio or dataset files are bundled with the model repository per the card (**Reported**).[^ark-asr-3b-card]

[^ark-asr-3b-card]: [ARK-ASR-3B model card](../raw/ARK-ASR-3B.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `repository`); sections `Abstract`, `Supported Languages`, `Model Overview` (incl. Figure 1 caption), `Performance > English WER` table, `Performance > Chinese CER` table, `Inference` (Transformers code fence, JSONL schema, `ark_asr_transformers.py` command), `vLLM Online Serving` (deploy/curl commands), `Evaluation`, `Acknowledgements`, `Citation` (arXiv:2605.28139).
